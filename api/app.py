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
        raw_data = list(collection.find({}, {'_id': 0}))

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
    try:
        data = get_all_data()
        
        if not data:
            return jsonify({'error': 'No data available'}), 404
        
        # Calculate statistics
        total_apps = len(data)
        
        categories = {}
        free_count = 0
        total_installs = 0
        
        for app in data:
            cat = app.get('category_clean', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            
            if app.get('type', 'Free') == 'Free':
                free_count += 1
            
            total_installs += app.get('installs', 0)
        
        # Average rating
        ratings = [app.get('rating', 0) for app in data if app.get('rating', 0) > 0]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Top categories
        top_categories = sorted(
            [{'name': k, 'count': v} for k, v in categories.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        return jsonify({
            'total_apps': total_apps,
            'total_categories': len(categories),
            'avg_rating': round(avg_rating, 2),
            'total_installs': total_installs,
            'free_apps': free_count,
            'free_percentage': round((free_count / total_apps) * 100, 2) if total_apps > 0 else 0,
            'top_categories': top_categories
        })
    
    except Exception as e:
        logger.error(f"Error in dashboard_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/category-analysis')
def category_analysis():
    """Get category-wise analysis"""
    try:
        data = get_all_data()
        category = request.args.get('category')
        
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
                    'total_installs': 0
                }
            
            stats = category_stats[cat]
            stats['count'] += 1
            stats['total_rating'] += app.get('rating', 0)
            stats['total_installs'] += app.get('installs', 0)
        
        # Calculate averages
        result = []
        for cat, stats in category_stats.items():
            result.append({
                'category': cat,
                'count': stats['count'],
                'avg_rating': round(stats['total_rating'] / stats['count'], 2),
                'total_installs': stats['total_installs'],
                'avg_installs': round(stats['total_installs'] / stats['count'])
            })
        
        return jsonify(sorted(result, key=lambda x: x['count'], reverse=True))
    
    except Exception as e:
        logger.error(f"Error in category_analysis: {e}")
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
    print("=" * 50)
    
    app.run(debug=debug, port=port, host='0.0.0.0')