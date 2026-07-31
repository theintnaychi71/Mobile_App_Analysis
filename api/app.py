# ============================================
# COMPLETE API FOR APP MARKET DASHBOARD
# ============================================

# Fix Windows console Unicode encoding for emoji output
import sys
import io
try:
    if hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        except (ValueError, OSError):
            pass
    if hasattr(sys.stderr, 'buffer'):
        try:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        except (ValueError, OSError):
            pass
except Exception:
    pass

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
import time
import math
import random

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb+srv://data_uploader:A7KQDxaxgMKIbevE@cluster0.cuueyms.mongodb.net/?appName=Cluster0')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['MONGO_DB'] = os.environ.get('MONGO_DB', 'app_market_db')
app.config['MONGO_COLLECTION'] = os.environ.get('MONGO_COLLECTION', 'apps')

# Simple in-memory cache
_cache = {}
_cache_timestamps = {}
CACHE_DURATION = 600  # 10 minutes (increased from 5)

def get_cached(key):
    """Get value from cache if not expired"""
    if key in _cache and key in _cache_timestamps:
        if time.time() - _cache_timestamps[key] < CACHE_DURATION:
            return _cache[key]
    return None

def set_cached(key, value):
    """Set value in cache"""
    _cache[key] = value
    _cache_timestamps[key] = time.time()

# Flask-PyMongo uses MONGO_DBNAME as fallback when URI has no DB path
if os.environ.get('MONGO_DB'):
    app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DB')

# Check if MongoDB is configured
if not app.config['MONGO_URI']:
    logger.warning("⚠️ MONGO_URI not found in environment variables!")
    logger.warning("Using sample data mode (no database connection)")
    app.config['USE_SAMPLE_DATA'] = True
else:
    app.config['USE_SAMPLE_DATA'] = False

# Enable CORS for Streamlit dashboard
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize MongoDB (if URI exists)
if not app.config['USE_SAMPLE_DATA']:
    mongo = PyMongo(app)

# ============================================
# SAMPLE DATA (For testing without MongoDB)
# ============================================

SAMPLE_DATA = [
    {
        "app_name": "Instagram",
        "category_clean": "SOCIAL",
        "rating": 4.5,
        "installs": 1000000000,
        "reviews": 5000000,
        "size_mb": 45.6,
        "price_usd": 0,
        "type": "Free",
        "content_rating": "Everyone"
    },
    {
        "app_name": "Subway Surfers",
        "category_clean": "GAME",
        "rating": 4.3,
        "installs": 500000000,
        "reviews": 2000000,
        "size_mb": 85.6,
        "price_usd": 0,
        "type": "Free",
        "content_rating": "Everyone"
    },
    {
        "app_name": "Minecraft",
        "category_clean": "GAME",
        "rating": 4.8,
        "installs": 200000000,
        "reviews": 3000000,
        "size_mb": 120.5,
        "price_usd": 6.99,
        "type": "Paid",
        "content_rating": "Everyone 10+"
    },
    {
        "app_name": "Duolingo",
        "category_clean": "EDUCATION",
        "rating": 4.7,
        "installs": 100000000,
        "reviews": 1000000,
        "size_mb": 35.2,
        "price_usd": 0,
        "type": "Free",
        "content_rating": "Everyone"
    },
    {
        "app_name": "TikTok",
        "category_clean": "SOCIAL",
        "rating": 4.2,
        "installs": 2000000000,
        "reviews": 10000000,
        "size_mb": 150.0,
        "price_usd": 0,
        "type": "Free",
        "content_rating": "Teen"
    }
]

# ============================================
# DATABASE HELPERS
# ============================================

def _normalize_doc(doc):
    """Map MongoDB field names (from clean_dataset.csv columns) to the
    SAMPLE_DATA-style names that dashboard_stats() and other endpoints expect.

    MongoDB actual fields (from uploaded clean_dataset.csv via transformer.py):
      App Name, Category, Rating, Reviews, Installs, Free, Price, Released,
      Last Updated, Developer, In-App Purchases, Price_Tier, Popularity_Tier

    Expected by API code (SAMPLE_DATA naming):
      app_name, category_clean, rating, reviews, installs, type, price_usd,
      released, last_updated, developer, content_rating
    """
    # Work on a copy so original dict isn't mutated
    d = dict(doc)

    # 1. Category: Category -> category_clean
    if 'category_clean' not in d or not d['category_clean']:
        cat = d.get('Category')
        if cat:
            d['category_clean'] = cat
        elif 'category' in d and d['category']:
            d['category_clean'] = d['category']
        else:
            d.setdefault('category_clean', 'Unknown')

    # 2. Rating: Rating (float) -> rating
    if 'rating' not in d or d.get('rating') in (None, 0):
        rating_val = d.get('Rating')
        if isinstance(rating_val, (int, float)):
            d['rating'] = float(rating_val)
        elif 'rating' not in d:
            d['rating'] = 0.0

    # 3. Installs: Installs (int) -> installs
    if 'installs' not in d or d.get('installs') in (None, 0):
        inst_val = d.get('Installs')
        if isinstance(inst_val, (int, float)):
            d['installs'] = int(inst_val)
        elif isinstance(inst_val, str):
            import re as _re
            cleaned = _re.sub(r'[^\d]', '', inst_val)
            d['installs'] = int(cleaned) if cleaned else 0
        elif 'installs' not in d:
            d['installs'] = 0

    # 4. Free/Paid Type: Free (TRUE/FALSE) or Price_Tier -> type ("Free"/"Paid")
    if 'type' not in d or not d['type']:
        is_free = False
        free_field = d.get('Free')
        if free_field is True or free_field in ('TRUE', 'True', 'true', '1', 1):
            is_free = True
        elif free_field is False or free_field in ('FALSE', 'False', 'false', '0', 0):
            is_free = False
        else:
            # Fallback: use Price or Price_Tier
            price_val = d.get('Price', d.get('price_usd', 0))
            tier = d.get('Price_Tier')
            if tier and str(tier).lower() == 'free':
                is_free = True
            elif isinstance(price_val, (int, float)) and price_val <= 0:
                is_free = True
        d['type'] = 'Free' if is_free else 'Paid'

    # Extra aliases (not strictly needed by current endpoints, but for completeness)
    if 'app_name' not in d:
        if 'App Name' in d: d['app_name'] = d['App Name']
    if 'reviews' not in d:
        r = d.get('Reviews')
        if isinstance(r, (int, float)): d['reviews'] = int(r)
    if 'price_usd' not in d:
        p = d.get('Price')
        if isinstance(p, (int, float)): d['price_usd'] = float(p)
    if 'last_updated' not in d and 'Last Updated' in d:
        d['last_updated'] = d['Last Updated']
    if 'released' not in d and 'Released' in d:
        d['released'] = d['Released']
    if 'developer' not in d and 'Developer' in d:
        d['developer'] = d['Developer']
    if 'content_rating' not in d:
        # Not present in clean_dataset.csv; set reasonable default
        d.setdefault('content_rating', 'Everyone')

    return d


def get_all_data():
    """Get all data (from MongoDB or sample) and normalize field names to
    match what the dashboard API logic expects."""
    if app.config['USE_SAMPLE_DATA']:
        return SAMPLE_DATA
    
    try:
        db_name = app.config.get('MONGO_DB')
        collection_name = app.config.get('MONGO_COLLECTION', 'apps')

        if db_name:
            db = mongo.cx[db_name]
        else:
            db = mongo.db

        collection = db[collection_name]
        
        # Only fetch necessary fields to reduce data transfer
        projection = {
            '_id': 0,
            'App Name': 1,
            'Category': 1,
            'Rating': 1,
            'Reviews': 1,
            'Installs': 1,
            'Free': 1,
            'Price': 1,
            'Released': 1,
            'Last Updated': 1,
            'Developer': 1,
            'In-App Purchases': 1,
            'Price_Tier': 1,
            'Popularity_Tier': 1
        }
        
        raw_data = list(collection.find({}, projection))

        if not raw_data:
            return SAMPLE_DATA

        # Normalize every document's field names so dashboard_stats() finds the keys it expects
        data = [_normalize_doc(doc) for doc in raw_data]
        return data

    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return SAMPLE_DATA

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/')
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running',
        'timestamp': datetime.now().isoformat(),
        'data_source': 'sample' if app.config['USE_SAMPLE_DATA'] else 'mongodb'
    })

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get main dashboard statistics"""
    # Check cache first
    cached = get_cached('dashboard_stats')
    if cached:
        return jsonify(cached)
    
    try:
        data = get_all_data()
        
        if not data:
            return jsonify({'error': 'No data available'}), 404
        
        # Calculate statistics
        total_apps = len(data)
        
        categories = {}
        free_count = 0
        total_installs = 0
        total_reviews = 0
        
        for app in data:
            cat = app.get('category_clean', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            
            if app.get('type', 'Free') == 'Free':
                free_count += 1
            
            total_installs += app.get('installs', 0)
            total_reviews += app.get('reviews', 0)
        
        # Average rating
        ratings = [app.get('rating', 0) for app in data if app.get('rating', 0) > 0]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Top categories
        top_categories = sorted(
            [{'name': k, 'count': v} for k, v in categories.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        result = {
            'total_apps': total_apps,
            'total_categories': len(categories),
            'avg_rating': round(avg_rating, 2),
            'total_installs': total_installs,
            'total_reviews': total_reviews,
            'free_apps': free_count,
            'free_percentage': round((free_count / total_apps) * 100, 2) if total_apps > 0 else 0,
            'top_categories': top_categories
        }
        
        # Cache the result
        set_cached('dashboard_stats', result)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in dashboard_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/category-analysis')
def category_analysis():
    """Get category-wise analysis"""
    category = request.args.get('category', 'All')
    cache_key = f'category_analysis_{category}'
    
    # Check cache first
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)
    
    try:
        data = get_all_data()
        
        # Filter by category if specified
        if category and category != 'All':
            data = [d for d in data if d.get('category_clean', '').upper() == category.upper()]
        
        if not data:
            return jsonify({'error': 'No data found'}), 404
        
        # Group by category
        category_stats = {}
        for app in data:
            cat = app.get('category_clean', 'Unknown')
            if cat not in category_stats:
                category_stats[cat] = {
                    'count': 0,
                    'total_rating': 0,
                    'total_installs': 0,
                    'total_reviews': 0,
                    'free_count': 0,
                    'paid_count': 0
                }
            
            stats = category_stats[cat]
            stats['count'] += 1
            stats['total_rating'] += app.get('rating', 0)
            stats['total_installs'] += app.get('installs', 0)
            stats['total_reviews'] += app.get('reviews', 0)
            
            if app.get('type', 'Free') == 'Free':
                stats['free_count'] += 1
            else:
                stats['paid_count'] += 1
        
        # Calculate averages
        result = []
        for cat, stats in category_stats.items():
            result.append({
                'category': cat,
                'count': stats['count'],
                'avg_rating': round(stats['total_rating'] / stats['count'], 2) if stats['count'] > 0 else 0,
                'total_installs': stats['total_installs'],
                'avg_installs': round(stats['total_installs'] / stats['count']) if stats['count'] > 0 else 0,
                'total_reviews': stats['total_reviews'],
                'avg_reviews': round(stats['total_reviews'] / stats['count']) if stats['count'] > 0 else 0,
                'free_count': stats['free_count'],
                'paid_count': stats['paid_count'],
                'free_percentage': round((stats['free_count'] / stats['count']) * 100, 2) if stats['count'] > 0 else 0
            })
        
        result = sorted(result, key=lambda x: x['count'], reverse=True)
        
        # Cache the result
        set_cached(cache_key, result)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in category_analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-apps')
def top_apps():
    """Get top apps by various metrics"""
    metric = request.args.get('metric', 'installs')  # installs, reviews, rating
    limit = int(request.args.get('limit', 20))
    cache_key = f'top_apps_{metric}_{limit}'
    
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)
    
    try:
        data = get_all_data()
        
        if not data:
            return jsonify({'error': 'No data found'}), 404
        
        # Sort based on metric
        if metric == 'installs':
            sorted_data = sorted(data, key=lambda x: x.get('installs', 0), reverse=True)
        elif metric == 'reviews':
            sorted_data = sorted(data, key=lambda x: x.get('reviews', 0), reverse=True)
        elif metric == 'rating':
            sorted_data = sorted(data, key=lambda x: x.get('rating', 0), reverse=True)
        else:
            sorted_data = sorted(data, key=lambda x: x.get('installs', 0), reverse=True)
        
        # Get top N
        top_apps = sorted_data[:limit]
        
        result = []
        for app in top_apps:
            result.append({
                'name': app.get('app_name', app.get('App Name', 'Unknown')),
                'category': app.get('category_clean', app.get('Category', 'Unknown')),
                'rating': app.get('rating', 0),
                'installs': app.get('installs', 0),
                'reviews': app.get('reviews', 0),
                'type': app.get('type', 'Free'),
                'price': app.get('price_usd', app.get('Price', 0))
            })
        
        set_cached(cache_key, result)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in top_apps: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rating-distribution')
def rating_distribution():
    """Get rating distribution data"""
    cache_key = 'rating_distribution'
    
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)
    
    try:
        data = get_all_data()
        
        if not data:
            return jsonify({'error': 'No data found'}), 404
        
        # Create rating buckets
        rating_buckets = {
            '5.0': 0,
            '4.5-4.9': 0,
            '4.0-4.4': 0,
            '3.5-3.9': 0,
            '3.0-3.4': 0,
            '2.5-2.9': 0,
            '2.0-2.4': 0,
            '1.5-1.9': 0,
            '1.0-1.4': 0,
            '0-0.9': 0
        }
        
        for app in data:
            rating = app.get('rating', 0)
            if rating >= 5.0:
                rating_buckets['5.0'] += 1
            elif rating >= 4.5:
                rating_buckets['4.5-4.9'] += 1
            elif rating >= 4.0:
                rating_buckets['4.0-4.4'] += 1
            elif rating >= 3.5:
                rating_buckets['3.5-3.9'] += 1
            elif rating >= 3.0:
                rating_buckets['3.0-3.4'] += 1
            elif rating >= 2.5:
                rating_buckets['2.5-2.9'] += 1
            elif rating >= 2.0:
                rating_buckets['2.0-2.4'] += 1
            elif rating >= 1.5:
                rating_buckets['1.5-1.9'] += 1
            elif rating >= 1.0:
                rating_buckets['1.0-1.4'] += 1
            else:
                rating_buckets['0-0.9'] += 1
        
        result = [{'range': k, 'count': v} for k, v in rating_buckets.items()]
        
        set_cached(cache_key, result)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in rating_distribution: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/correlation-analysis')
def correlation_analysis():
    """Get correlation analysis between different metrics"""
    cache_key = 'correlation_analysis'
    
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)
    
    try:
        data = get_all_data()
        
        if not data:
            return jsonify({'error': 'No data found'}), 404
        
        # Extract data for correlation analysis
        ratings = []
        reviews = []
        installs = []
        prices = []
        
        for app in data:
            rating = app.get('rating', 0)
            review = app.get('reviews', 0)
            install = app.get('installs', 0)
            price = app.get('price_usd', app.get('Price', 0))
            
            if rating > 0 and review > 0:
                ratings.append(rating)
                reviews.append(review)
                installs.append(install)
                prices.append(price)
        
        # Calculate correlations (simplified)
        def calculate_correlation(x, y):
            n = len(x)
            if n < 2:
                return 0
            
            mean_x = sum(x) / n
            mean_y = sum(y) / n
            
            numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
            denominator = math.sqrt(sum((xi - mean_x) ** 2 for xi in x) * sum((yi - mean_y) ** 2 for yi in y))
            
            if denominator == 0:
                return 0
            return numerator / denominator
        
        correlation_rating_reviews = calculate_correlation(ratings, reviews)
        correlation_rating_installs = calculate_correlation(ratings, installs)
        correlation_reviews_installs = calculate_correlation(reviews, installs)
        
        # Create scatter plot data (sample 500 points for performance)
        scatter_data = []
        sample_size = min(500, len(ratings))
        indices = random.sample(range(len(ratings)), sample_size)
        
        for i in indices:
            scatter_data.append({
                'rating': ratings[i],
                'reviews': reviews[i],
                'installs': installs[i]
            })
        
        result = {
            'correlations': {
                'rating_reviews': round(correlation_rating_reviews, 3),
                'rating_installs': round(correlation_rating_installs, 3),
                'reviews_installs': round(correlation_reviews_installs, 3)
            },
            'scatter_data': scatter_data,
            'sample_size': sample_size,
            'total_analyzed': len(ratings)
        }
        
        set_cached(cache_key, result)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in correlation_analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/price-distribution')
def price_distribution():
    """Get price distribution analysis"""
    cache_key = 'price_distribution'
    
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)
    
    try:
        data = get_all_data()
        
        if not data:
            return jsonify({'error': 'No data found'}), 404
        
        # Create price buckets
        price_buckets = {
            'Free': 0,
            '$0.01-$0.99': 0,
            '$1.00-$4.99': 0,
            '$5.00-$9.99': 0,
            '$10.00-$19.99': 0,
            '$20.00+': 0
        }
        
        total_installs_by_price = {
            'Free': 0,
            '$0.01-$0.99': 0,
            '$1.00-$4.99': 0,
            '$5.00-$9.99': 0,
            '$10.00-$19.99': 0,
            '$20.00+': 0
        }
        
        for app in data:
            price = app.get('price_usd', app.get('Price', 0))
            installs = app.get('installs', 0)
            
            if price <= 0:
                price_buckets['Free'] += 1
                total_installs_by_price['Free'] += installs
            elif price < 1.0:
                price_buckets['$0.01-$0.99'] += 1
                total_installs_by_price['$0.01-$0.99'] += installs
            elif price < 5.0:
                price_buckets['$1.00-$4.99'] += 1
                total_installs_by_price['$1.00-$4.99'] += installs
            elif price < 10.0:
                price_buckets['$5.00-$9.99'] += 1
                total_installs_by_price['$5.00-$9.99'] += installs
            elif price < 20.0:
                price_buckets['$10.00-$19.99'] += 1
                total_installs_by_price['$10.00-$19.99'] += installs
            else:
                price_buckets['$20.00+'] += 1
                total_installs_by_price['$20.00+'] += installs
        
        result = {
            'app_count': [{'price': k, 'count': v} for k, v in price_buckets.items()],
            'install_distribution': [{'price': k, 'installs': v} for k, v in total_installs_by_price.items()]
        }
        
        set_cached(cache_key, result)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in price_distribution: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/release-year-distribution')
def release_year_distribution():
    """Get release year distribution data"""
    cache_key = 'release_year_distribution'
    
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)
    
    try:
        data = get_all_data()
        
        if not data:
            return jsonify({'error': 'No data found'}), 404
        
        # Extract release years
        year_counts = {}
        for app in data:
            released = app.get('released', app.get('Released', ''))
            if released:
                # Try to extract year from various date formats
                import re as _re
                year_match = _re.search(r'\b(19|20)\d{2}\b', str(released))
                if year_match:
                    year = year_match.group()
                    year_counts[year] = year_counts.get(year, 0) + 1
        
        # Sort by year
        sorted_years = sorted(year_counts.items(), key=lambda x: x[0])
        
        result = [{'year': k, 'count': v} for k, v in sorted_years]
        
        set_cached(cache_key, result)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in release_year_distribution: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights')
def insights():
    """Get key insights from the data"""
    cache_key = 'insights'
    
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)
    
    try:
        data = get_all_data()
        
        if not data:
            return jsonify({'error': 'No data found'}), 404
        
        insights = []
        
        # Category dominance
        categories = {}
        for app in data:
            cat = app.get('category_clean', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        top_category = max(categories.items(), key=lambda x: x[1])
        insights.append({
            'type': 'category_dominance',
            'title': 'Market Dominance',
            'message': f"The '{top_category[0]}' category dominates with {top_category[1]} apps ({round((top_category[1]/len(data))*100, 1)}% of total)"
        })
        
        # Rating analysis
        ratings = [app.get('rating', 0) for app in data if app.get('rating', 0) > 0]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            insights.append({
                'type': 'rating_analysis',
                'title': 'User Satisfaction',
                'message': f"Average app rating is {avg_rating:.2f}/5.0, indicating generally positive user sentiment"
            })
        
        # Free vs Paid
        free_count = sum(1 for app in data if app.get('type', 'Free') == 'Free')
        free_percentage = (free_count / len(data)) * 100
        insights.append({
            'type': 'monetization',
            'title': 'Monetization Model',
            'message': f"{free_percentage:.1f}% of apps are free, confirming the freemium model dominance"
        })
        
        # Install analysis
        total_installs = sum(app.get('installs', 0) for app in data)
        avg_installs = total_installs / len(data) if len(data) > 0 else 0
        insights.append({
            'type': 'install_analysis',
            'title': 'Market Reach',
            'message': f"Total installs across all apps: {total_installs:,} (Average: {avg_installs:,.0f} per app)"
        })
        
        set_cached(cache_key, insights)
        return jsonify(insights)
    
    except Exception as e:
        logger.error(f"Error in insights: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("=" * 50)
    print("📱 App Market API")
    print("=" * 50)
    print(f"📍 Running on: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 Data source: {'SAMPLE' if app.config['USE_SAMPLE_DATA'] else 'MONGODB'}")
    print("=" * 50)
    print("\n📋 Available endpoints:")
    print("  GET /health")
    print("  GET /api/dashboard/stats")
    print("  GET /api/category-analysis")
    print("  GET /api/top-apps")
    print("  GET /api/rating-distribution")
    print("  GET /api/correlation-analysis")
    print("  GET /api/price-distribution")
    print("  GET /api/release-year-distribution")
    print("  GET /api/insights")
    print("=" * 50)
    
    app.run(debug=debug, port=port, host='0.0.0.0')