# ============================================
# COMPLETE SAFE API FOR APP MARKET DASHBOARD
# ============================================

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
import re

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb+srv://data_uploader:A7KQDxaxgMKIbevE@cluster0.cuueyms.mongodb.net/?appName=Cluster0')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['MONGO_DB'] = os.environ.get('MONGO_DB', 'app_market_db')
app.config['MONGO_COLLECTION'] = os.environ.get('MONGO_COLLECTION', 'apps')

_cache = {}
_cache_timestamps = {}
CACHE_DURATION = 600

def get_cached(key):
    if key in _cache and key in _cache_timestamps:
        if time.time() - _cache_timestamps[key] < CACHE_DURATION:
            return _cache[key]
    return None

def set_cached(key, value):
    _cache[key] = value
    _cache_timestamps[key] = time.time()

if os.environ.get('MONGO_DB'):
    app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DB')

if not app.config['MONGO_URI']:
    logger.warning("️ MONGO_URI not found in environment variables!")
    app.config['USE_SAMPLE_DATA'] = True
else:
    app.config['USE_SAMPLE_DATA'] = False

# ✅ ENABLE CORS FOR ALL ROUTES & ORIGINS
CORS(app, resources={r"/*": {"origins": "*"}})

if not app.config['USE_SAMPLE_DATA']:
    mongo = PyMongo(app)

SAMPLE_DATA = [
    {"app_name": "Instagram", "category_clean": "SOCIAL", "rating": 4.5, "installs": 1000000000, "reviews": 5000000, "size_mb": 45.6, "price_usd": 0, "type": "Free", "content_rating": "Teen", "developer": "Meta Platforms, Inc.", "released": "2010-10-06", "last_updated": "2024-01-15"},
    {"app_name": "Subway Surfers", "category_clean": "GAME", "rating": 4.3, "installs": 500000000, "reviews": 2000000, "size_mb": 85.6, "price_usd": 0, "type": "Free", "content_rating": "Everyone", "developer": "SYBO Games", "released": "2012-05-24", "last_updated": "2024-02-10"},
    {"app_name": "Minecraft", "category_clean": "GAME", "rating": 4.8, "installs": 200000000, "reviews": 3000000, "size_mb": 120.5, "price_usd": 6.99, "type": "Paid", "content_rating": "Everyone 10+", "developer": "Mojang", "released": "2011-08-16", "last_updated": "2024-01-20"},
    {"app_name": "Duolingo", "category_clean": "EDUCATION", "rating": 4.7, "installs": 100000000, "reviews": 1000000, "size_mb": 35.2, "price_usd": 0, "type": "Free", "content_rating": "Everyone", "developer": "Duolingo", "released": "2012-11-13", "last_updated": "2024-02-05"},
    {"app_name": "TikTok", "category_clean": "SOCIAL", "rating": 4.2, "installs": 2000000000, "reviews": 10000000, "size_mb": 150.0, "price_usd": 0, "type": "Free", "content_rating": "Teen", "developer": "ByteDance", "released": "2016-09-01", "last_updated": "2024-02-12"},
    {"app_name": "Clash of Clans", "category_clean": "GAME", "rating": 4.6, "installs": 500000000, "reviews": 5500000, "size_mb": 145.0, "price_usd": 0, "type": "Free", "content_rating": "Everyone 10+", "developer": "Supercell", "released": "2012-08-02", "last_updated": "2024-01-25"},
    {"app_name": "Clash Royale", "category_clean": "GAME", "rating": 4.4, "installs": 300000000, "reviews": 3500000, "size_mb": 130.0, "price_usd": 0, "type": "Free", "content_rating": "Everyone 10+", "developer": "Supercell", "released": "2016-03-02", "last_updated": "2024-02-01"},
    {"app_name": "Gmail", "category_clean": "COMMUNICATION", "rating": 4.3, "installs": 5000000000, "reviews": 15000000, "size_mb": 25.0, "price_usd": 0, "type": "Free", "content_rating": "Everyone", "developer": "Google LLC", "released": "2009-10-01", "last_updated": "2024-02-08"},
    {"app_name": "YouTube", "category_clean": "VIDEO_PLAYERS", "rating": 4.1, "installs": 10000000000, "reviews": 120000000, "size_mb": 55.0, "price_usd": 0, "type": "Free", "content_rating": "Teen", "developer": "Google LLC", "released": "2007-10-15", "last_updated": "2024-02-14"},
    {"app_name": "Google Maps", "category_clean": "TRAVEL_AND_LOCAL", "rating": 4.2, "installs": 8000000000, "reviews": 30000000, "size_mb": 50.0, "price_usd": 0, "type": "Free", "content_rating": "Everyone", "developer": "Google LLC", "released": "2008-07-11", "last_updated": "2024-02-10"},
    {"app_name": "WhatsApp", "category_clean": "COMMUNICATION", "rating": 4.0, "installs": 10000000000, "reviews": 180000000, "size_mb": 40.0, "price_usd": 0, "type": "Free", "content_rating": "Teen", "developer": "Meta Platforms, Inc.", "released": "2009-05-01", "last_updated": "2024-02-13"},
    {"app_name": "Facebook", "category_clean": "SOCIAL", "rating": 3.8, "installs": 8000000000, "reviews": 150000000, "size_mb": 70.0, "price_usd": 0, "type": "Free", "content_rating": "Teen", "developer": "Meta Platforms, Inc.", "released": "2008-07-10", "last_updated": "2024-02-11"},
    {"app_name": "Chrome Browser", "category_clean": "COMMUNICATION", "rating": 4.4, "installs": 9000000000, "reviews": 35000000, "size_mb": 60.0, "price_usd": 0, "type": "Free", "content_rating": "Everyone", "developer": "Google LLC", "released": "2012-02-07", "last_updated": "2024-02-09"},
    {"app_name": "Hay Day", "category_clean": "GAME", "rating": 4.5, "installs": 150000000, "reviews": 2500000, "size_mb": 110.0, "price_usd": 0, "type": "Free", "content_rating": "Everyone", "developer": "Supercell", "released": "2012-06-21", "last_updated": "2024-01-30"},
    {"app_name": "Brawl Stars", "category_clean": "GAME", "rating": 4.3, "installs": 200000000, "reviews": 4000000, "size_mb": 175.0, "price_usd": 0, "type": "Free", "content_rating": "Everyone 10+", "developer": "Supercell", "released": "2018-12-12", "last_updated": "2024-02-06"}
]

def _normalize_doc(doc):
    d = dict(doc)
    if 'category_clean' not in d or not d['category_clean']:
        cat = d.get('Category') or d.get('category')
        d['category_clean'] = cat if cat else 'Unknown'
    
    if 'rating' not in d or d.get('rating') in (None, 0):
        rating_val = d.get('Rating')
        d['rating'] = float(rating_val) if isinstance(rating_val, (int, float)) else 0.0
    
    if 'installs' not in d or d.get('installs') in (None, 0):
        inst_val = d.get('Installs')
        if isinstance(inst_val, (int, float)):
            d['installs'] = int(inst_val)
        elif isinstance(inst_val, str):
            cleaned = re.sub(r'[^\d]', '', inst_val)
            d['installs'] = int(cleaned) if cleaned else 0
        else:
            d['installs'] = 0
    
    if 'type' not in d or not d['type']:
        is_free = False
        free_field = d.get('Free')
        if free_field is True or free_field in ('TRUE', 'True', 'true', '1', 1):
            is_free = True
        elif free_field is False or free_field in ('FALSE', 'False', 'false', '0', 0):
            is_free = False
        else:
            price_val = d.get('Price', d.get('price_usd', 0))
            tier = d.get('Price_Tier')
            if tier and str(tier).lower() == 'free':
                is_free = True
            elif isinstance(price_val, (int, float)) and price_val <= 0:
                is_free = True
        d['type'] = 'Free' if is_free else 'Paid'
    
    if 'app_name' not in d and 'App Name' in d: d['app_name'] = d['App Name']
    if 'reviews' not in d and isinstance(d.get('Reviews'), (int, float)): d['reviews'] = int(d['Reviews'])
    if 'price_usd' not in d and isinstance(d.get('Price'), (int, float)): d['price_usd'] = float(d['Price'])
    if 'developer' not in d and 'Developer' in d: d['developer'] = d['Developer']
    if 'content_rating' not in d: d.setdefault('content_rating', 'Everyone')
    
    if 'released' not in d:
        released_val = d.get('Released')
        if released_val:
            d['released'] = str(released_val)
    
    if 'last_updated' not in d:
        last_updated_val = d.get('Last Updated')
        if last_updated_val:
            d['last_updated'] = str(last_updated_val)
    
    return d

def get_all_data():
    if app.config['USE_SAMPLE_DATA']:
        return SAMPLE_DATA
    try:
        db_name = app.config.get('MONGO_DB')
        collection_name = app.config.get('MONGO_COLLECTION', 'apps')
        db = mongo.cx[db_name] if db_name else mongo.db
        collection = db[collection_name]
        
        projection = {
            '_id': 0, 
            'App Name': 1, 
            'Category': 1, 
            'Rating': 1, 
            'Reviews': 1, 
            'Installs': 1, 
            'Free': 1, 
            'Price': 1, 
            'Developer': 1, 
            'Price_Tier': 1,
            'Released': 1,
            'Last Updated': 1
        }
        raw_data = list(collection.find({}, projection))
        return [_normalize_doc(doc) for doc in raw_data] if raw_data else SAMPLE_DATA
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return SAMPLE_DATA

def extract_year_from_date(date_str):
    if not date_str:
        return None
    date_str = str(date_str)
    year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
    if year_match:
        return year_match.group()
    return None

def apply_filters(data, filters):
    filtered = data
    category = filters.get('category')
    app_type = filters.get('type')
    content_rating = filters.get('content_rating')

    if category and category.upper() != 'ALL':
        filtered = [d for d in filtered if d.get('category_clean', '').upper() == category.upper()]
    if app_type and app_type.upper() != 'ALL':
        filtered = [d for d in filtered if d.get('type', 'Free').capitalize() == app_type.capitalize()]
    if content_rating and content_rating.upper() != 'ALL':
        filtered = [d for d in filtered if str(d.get('content_rating', 'Everyone')).lower() == content_rating.lower()]
    return filtered

def get_unique_options():
    data = get_all_data()
    categories = sorted(list(set([d.get('category_clean', 'Unknown') for d in data if d.get('category_clean')])))
    content_ratings = sorted(list(set([str(d.get('content_rating', 'Everyone')) for d in data if d.get('content_rating')])))
    return {'categories': ['All'] + categories, 'types': ['All', 'Free', 'Paid'], 'content_ratings': ['All'] + content_ratings}

@app.route('/')
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running', 'timestamp': datetime.now().isoformat(), 'data_source': 'sample' if app.config['USE_SAMPLE_DATA'] else 'mongodb'})

@app.route('/api/filter-options')
def filter_options():
    cached = get_cached('filter_options')
    if cached: return jsonify(cached)
    options = get_unique_options()
    set_cached('filter_options', options)
    return jsonify(options)

@app.route('/api/dashboard/stats')
def dashboard_stats():
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"dashboard_stats_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        
        # ✅ FIX: Empty data Handling (404 အစား 200 OK + Empty Structure ပြန်ပေးပါမည်)
        if not data: 
            empty_res = {
                'total_apps': 0, 'total_categories': 0, 'avg_rating': 0,
                'total_installs': 0, 'total_reviews': 0, 'free_apps': 0,
                'free_percentage': 0, 'top_categories': []
            }
            return jsonify(empty_res)
        
        categories = {}
        free_count = total_installs = total_reviews = 0
        for app_doc in data:
            cat_name = app_doc.get('category_clean', 'Unknown')
            categories[cat_name] = categories.get(cat_name, 0) + 1
            if app_doc.get('type', 'Free') == 'Free': free_count += 1
            total_installs += app_doc.get('installs', 0)
            total_reviews += app_doc.get('reviews', 0)
        
        ratings = [app_doc.get('rating', 0) for app_doc in data if app_doc.get('rating', 0) > 0]
        avg_rating = sum(ratings) / len(ratings) if len(ratings) > 0 else 0
        
        result = {
            'total_apps': len(data), 'total_categories': len(categories), 'avg_rating': round(avg_rating, 2),
            'total_installs': total_installs, 'total_reviews': total_reviews, 'free_apps': free_count,
            'free_percentage': round((free_count / len(data)) * 100, 2) if len(data) > 0 else 0,
            'top_categories': sorted([{'name': k, 'count': v} for k, v in categories.items()], key=lambda x: x['count'], reverse=True)[:10]
        }
        set_cached(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in dashboard_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-developers')
def top_developers():
    sort_by = request.args.get('sortBy', 'installs')
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"top_dev_{sort_by}_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        if not data: return jsonify([])
        
        dev_stats = {}
        for app_doc in data:
            dev = app_doc.get('developer') or app_doc.get('Developer') or 'Unknown'
            if dev not in dev_stats:
                dev_stats[dev] = {'developer': dev, 'total_installs': 0, 'app_count': 0, 'total_reviews': 0}
            dev_stats[dev]['total_installs'] += app_doc.get('installs', 0)
            dev_stats[dev]['app_count'] += 1
            dev_stats[dev]['total_reviews'] += app_doc.get('reviews', 0)
        
        dev_list = list(dev_stats.values())
        dev_list.sort(key=lambda x: x['total_installs' if sort_by == 'installs' else 'app_count'], reverse=True)
        
        for d in dev_list[:10]:
            d['avg_installs'] = round(d['total_installs'] / d['app_count']) if d['app_count'] > 0 else 0
            
        set_cached(cache_key, dev_list[:10])
        return jsonify(dev_list[:10])
    except Exception as e:
        logger.error(f"Error in top_developers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/content-rating-distribution')
def content_rating_distribution():
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"content_rating_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        if not data: return jsonify([])
        
        rating_counts = {}
        rating_installs = {}
        for app_doc in data:
            cr = str(app_doc.get('content_rating', 'Everyone')) or 'Everyone'
            rating_counts[cr] = rating_counts.get(cr, 0) + 1
            rating_installs[cr] = rating_installs.get(cr, 0) + app_doc.get('installs', 0)
        
        result = [{'rating': k, 'count': rating_counts[k], 'total_installs': rating_installs.get(k, 0)} for k in rating_counts.keys()]
        result.sort(key=lambda x: x['count'], reverse=True)
        set_cached(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in content_rating_distribution: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/category-analysis')
def category_analysis():
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"category_analysis_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        if not data: return jsonify([])
        
        category_stats = {}
        for app_doc in data:
            cat = app_doc.get('category_clean', 'Unknown')
            if cat not in category_stats:
                category_stats[cat] = {'count': 0, 'total_rating': 0, 'total_installs': 0, 'total_reviews': 0, 'free_count': 0, 'paid_count': 0}
            stats = category_stats[cat]
            stats['count'] += 1
            stats['total_rating'] += app_doc.get('rating', 0)
            stats['total_installs'] += app_doc.get('installs', 0)
            stats['total_reviews'] += app_doc.get('reviews', 0)
            if app_doc.get('type', 'Free') == 'Free': stats['free_count'] += 1
            else: stats['paid_count'] += 1
            
        result = []
        for cat, stats in category_stats.items():
            result.append({
                'category': cat, 'count': stats['count'],
                'avg_rating': round(stats['total_rating'] / stats['count'], 2) if stats['count'] > 0 else 0,
                'total_installs': stats['total_installs'],
                'avg_installs': round(stats['total_installs'] / stats['count']) if stats['count'] > 0 else 0,
                'total_reviews': stats['total_reviews'],
                'avg_reviews': round(stats['total_reviews'] / stats['count']) if stats['count'] > 0 else 0,
                'free_count': stats['free_count'], 'paid_count': stats['paid_count'],
                'free_percentage': round((stats['free_count'] / stats['count']) * 100, 2) if stats['count'] > 0 else 0
            })
        result.sort(key=lambda x: x['count'], reverse=True)
        set_cached(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in category_analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-apps')
def top_apps():
    metric = request.args.get('metric', 'installs')
    limit = int(request.args.get('limit', 20))
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"top_apps_{metric}_{limit}_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        if not data: return jsonify([])
        
        if metric == 'installs': sorted_data = sorted(data, key=lambda x: x.get('installs', 0), reverse=True)
        elif metric == 'reviews': sorted_data = sorted(data, key=lambda x: x.get('reviews', 0), reverse=True)
        elif metric == 'rating': sorted_data = sorted(data, key=lambda x: x.get('rating', 0), reverse=True)
        else: sorted_data = sorted(data, key=lambda x: x.get('installs', 0), reverse=True)
        
        result = []
        for app_doc in sorted_data[:limit]:
            result.append({
                'name': app_doc.get('app_name', app_doc.get('App Name', 'Unknown')),
                'category': app_doc.get('category_clean', app_doc.get('Category', 'Unknown')),
                'rating': app_doc.get('rating', 0), 'installs': app_doc.get('installs', 0), 'reviews': app_doc.get('reviews', 0),
                'type': app_doc.get('type', 'Free'), 'price': app_doc.get('price_usd', app_doc.get('Price', 0)),
                'content_rating': app_doc.get('content_rating', 'Everyone'),
                'developer': app_doc.get('developer') or app_doc.get('Developer') or 'Unknown'
            })
        set_cached(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in top_apps: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rating-distribution')
def rating_distribution():
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"rating_dist_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        
        rating_buckets = {'5.0': 0, '4.5-4.9': 0, '4.0-4.4': 0, '3.5-3.9': 0, '3.0-3.4': 0, '2.5-2.9': 0, '2.0-2.4': 0, '1.5-1.9': 0, '1.0-1.4': 0, '0-0.9': 0}
        if data:
            for app_doc in data:
                rating = app_doc.get('rating', 0)
                if rating >= 5.0: rating_buckets['5.0'] += 1
                elif rating >= 4.5: rating_buckets['4.5-4.9'] += 1
                elif rating >= 4.0: rating_buckets['4.0-4.4'] += 1
                elif rating >= 3.5: rating_buckets['3.5-3.9'] += 1
                elif rating >= 3.0: rating_buckets['3.0-3.4'] += 1
                elif rating >= 2.5: rating_buckets['2.5-2.9'] += 1
                elif rating >= 2.0: rating_buckets['2.0-2.4'] += 1
                elif rating >= 1.5: rating_buckets['1.5-1.9'] += 1
                elif rating >= 1.0: rating_buckets['1.0-1.4'] += 1
                else: rating_buckets['0-0.9'] += 1
            
        result = [{'range': k, 'count': v} for k, v in rating_buckets.items()]
        set_cached(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in rating_distribution: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/correlation-analysis')
def correlation_analysis():
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"corr_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        if not data:
            return jsonify({
                'correlations': {'rating_reviews': 0, 'rating_installs': 0, 'reviews_installs': 0},
                'scatter_data': [], 'sample_size': 0, 'total_analyzed': 0
            })
        
        ratings, reviews, installs, prices = [], [], [], []
        for app_doc in data:
            if app_doc.get('rating', 0) > 0 and app_doc.get('reviews', 0) > 0:
                ratings.append(app_doc.get('rating', 0))
                reviews.append(app_doc.get('reviews', 0))
                installs.append(app_doc.get('installs', 0))
                prices.append(app_doc.get('price_usd', app_doc.get('Price', 0)))
        
        def calc_corr(x, y):
            n = len(x)
            if n < 2: return 0
            mean_x, mean_y = sum(x)/n, sum(y)/n
            num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
            den = math.sqrt(sum((xi - mean_x)**2 for xi in x) * sum((yi - mean_y)**2 for yi in y))
            return num / den if den != 0 else 0
            
        scatter_data = []
        sample_size = min(500, len(ratings))
        if sample_size > 0:
            for i in random.sample(range(len(ratings)), sample_size):
                scatter_data.append({'rating': ratings[i], 'reviews': reviews[i], 'installs': installs[i]})
                
        result = {
            'correlations': {
                'rating_reviews': round(calc_corr(ratings, reviews), 3),
                'rating_installs': round(calc_corr(ratings, installs), 3),
                'reviews_installs': round(calc_corr(reviews, installs), 3)
            },
            'scatter_data': scatter_data, 'sample_size': sample_size, 'total_analyzed': len(ratings)
        }
        set_cached(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in correlation_analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/price-distribution')
def price_distribution():
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"price_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        
        price_buckets = {'Free': 0, '$0.01-$0.99': 0, '$1.00-$4.99': 0, '$5.00-$9.99': 0, '$10.00-$19.99': 0, '$20.00+': 0}
        total_installs_by_price = {'Free': 0, '$0.01-$0.99': 0, '$1.00-$4.99': 0, '$5.00-$9.99': 0, '$10.00-$19.99': 0, '$20.00+': 0}
        
        if data:
            for app_doc in data:
                price = app_doc.get('price_usd', app_doc.get('Price', 0))
                installs = app_doc.get('installs', 0)
                if price <= 0:
                    price_buckets['Free'] += 1; total_installs_by_price['Free'] += installs
                elif price < 1.0:
                    price_buckets['$0.01-$0.99'] += 1; total_installs_by_price['$0.01-$0.99'] += installs
                elif price < 5.0:
                    price_buckets['$1.00-$4.99'] += 1; total_installs_by_price['$1.00-$4.99'] += installs
                elif price < 10.0:
                    price_buckets['$5.00-$9.99'] += 1; total_installs_by_price['$5.00-$9.99'] += installs
                elif price < 20.0:
                    price_buckets['$10.00-$19.99'] += 1; total_installs_by_price['$10.00-$19.99'] += installs
                else:
                    price_buckets['$20.00+'] += 1; total_installs_by_price['$20.00+'] += installs
                
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
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"year_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        if not data: return jsonify([])
        
        year_counts = {}
        for app_doc in data:
            released = app_doc.get('released') or app_doc.get('Released', '')
            last_updated = app_doc.get('last_updated') or app_doc.get('Last Updated', '')
            
            year = extract_year_from_date(released)
            if not year:
                year = extract_year_from_date(last_updated)
            
            if year:
                year_counts[year] = year_counts.get(year, 0) + 1
        
        result = [{'year': k, 'count': v} for k, v in sorted(year_counts.items(), key=lambda x: x[0])]
        set_cached(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in release_year_distribution: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights')
def insights():
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"insights_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        if not data: return jsonify([])
        
        insights_list = []
        categories = {}
        for app_doc in data: categories[app_doc.get('category_clean', 'Unknown')] = categories.get(app_doc.get('category_clean', 'Unknown'), 0) + 1
        
        if categories:
            top_category = max(categories.items(), key=lambda x: x[1])
            insights_list.append({'type': 'category_dominance', 'title': 'Market Dominance', 'message': f"The '{top_category[0]}' category dominates with {top_category[1]} apps ({round((top_category[1]/len(data))*100, 1)}% of total)"})
        
        ratings = [app_doc.get('rating', 0) for app_doc in data if app_doc.get('rating', 0) > 0]
        if ratings:
            insights_list.append({'type': 'rating_analysis', 'title': 'User Satisfaction', 'message': f"Average app rating is {sum(ratings)/len(ratings):.2f}/5.0, indicating generally positive user sentiment"})
            
        free_count = sum(1 for app_doc in data if app_doc.get('type', 'Free') == 'Free')
        insights_list.append({'type': 'monetization', 'title': 'Monetization Model', 'message': f"{(free_count/len(data))*100:.1f}% of apps are free, confirming the freemium model dominance"})
        
        total_installs = sum(app_doc.get('installs', 0) for app_doc in data)
        insights_list.append({'type': 'install_analysis', 'title': 'Market Reach', 'message': f"Total installs across all apps: {total_installs:,} (Average: {total_installs/len(data):,.0f} per app)"})
        
        set_cached(cache_key, insights_list)
        return jsonify(insights_list)
    except Exception as e:
        logger.error(f"Error in insights: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================
# MAIN ENTRY POINT
# ============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    print("=" * 50)
    print("📱 App Market API (Fixed)")
    print("=" * 50)
    print(f"📍 Running on: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 Data source: {'SAMPLE' if app.config['USE_SAMPLE_DATA'] else 'MONGODB'}")
    print("=" * 50)
    
    app.run(debug=debug, port=5001, host='0.0.0.0')