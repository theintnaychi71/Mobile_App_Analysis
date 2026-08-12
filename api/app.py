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


def build_mongo_match(filters):
    conditions = []
    category = filters.get('category')
    content_rating = filters.get('content_rating')
    app_type = filters.get('type')

    if category and category.upper() != 'ALL':
        conditions.append({
            '$or': [
                {'category_clean': category},
                {'Category': category},
                {'category': category}
            ]
        })

    if content_rating and content_rating.upper() != 'ALL':
        conditions.append({
            '$or': [
                {'content_rating': content_rating},
                {'Content Rating': content_rating},
                {'content_rating': content_rating.capitalize()}
            ]
        })

    if app_type and app_type.upper() != 'ALL':
        if app_type.capitalize() == 'Free':
            conditions.append({'$or': [{'type': 'Free'}, {'Free': True}, {'Price': {'$lte': 0}}]})
        else:
            conditions.append({'$or': [{'type': 'Paid'}, {'Free': False}, {'Price': {'$gt': 0}}]})

    if not conditions:
        return {}
    if len(conditions) == 1:
        return conditions[0]
    return {'$and': conditions}


def get_filtered_docs(filters, projection=None):
    if app.config['USE_SAMPLE_DATA']:
        return apply_filters(SAMPLE_DATA, filters)

    try:
        db_name = app.config.get('MONGO_DB')
        collection_name = app.config.get('MONGO_COLLECTION', 'apps')
        db = mongo.cx[db_name] if db_name else mongo.db
        collection = db[collection_name]

        if projection is None:
            projection = {
                '_id': 0,
                'App Name': 1,
                'Category': 1,
                'category_clean': 1,
                'Rating': 1,
                'Reviews': 1,
                'Installs': 1,
                'Free': 1,
                'Price': 1,
                'price_usd': 1,
                'Developer': 1,
                'Price_Tier': 1,
                'Released': 1,
                'Last Updated': 1,
                'content_rating': 1,
                'type': 1
            }

        query = build_mongo_match(filters)
        raw_data = list(collection.find(query, projection))
        return [_normalize_doc(doc) for doc in raw_data]
    except Exception as e:
        logger.error(f"Error fetching filtered docs: {e}")
        return []


if os.environ.get('MONGO_DB'):
    app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DB')

if not app.config['MONGO_URI']:
    logger.warning("⚠️ MONGO_URI not found in environment variables!")
    app.config['USE_SAMPLE_DATA'] = True
else:
    app.config['USE_SAMPLE_DATA'] = False

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
        cached = get_cached('all_data')
        if cached:
            return cached

        raw_data = list(collection.find({}, projection))
        result = [_normalize_doc(doc) for doc in raw_data] if raw_data else SAMPLE_DATA
        set_cached('all_data', result)
        return result
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
    return {'categories': categories, 'types': ['All', 'Free', 'Paid'], 'content_ratings': content_ratings}


def build_dashboard_summary(filters):
    docs = get_filtered_docs(filters)
    if not docs:
        return {
            'stats': {'total_apps': 0, 'total_categories': 0, 'avg_rating': 0, 'total_installs': 0, 'total_reviews': 0, 'free_apps': 0, 'free_percentage': 0, 'top_categories': []},
            'category_analysis': [],
            'top_apps': [],
            'top_developers': [],
            'content_rating_distribution': [],
            'rating_distribution': [],
            'correlation_analysis': {'correlations': {'rating_reviews': 0, 'rating_installs': 0, 'reviews_installs': 0}, 'scatter_data': [], 'sample_size': 0, 'total_analyzed': 0},
            'price_distribution': {'app_count': [], 'install_distribution': []},
            'release_year_distribution': [],
            'insights': [],
            'install_distribution': []
        }

    categories = {}
    free_count = total_installs = total_reviews = 0
    for app_doc in docs:
        cat_name = app_doc.get('category_clean', 'Unknown')
        categories[cat_name] = categories.get(cat_name, 0) + 1
        if app_doc.get('type', 'Free') == 'Free':
            free_count += 1
        total_installs += app_doc.get('installs', 0)
        total_reviews += app_doc.get('reviews', 0)
    ratings = [app_doc.get('rating', 0) for app_doc in docs if app_doc.get('rating', 0) > 0]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    stats = {
        'total_apps': len(docs),
        'total_categories': len(categories),
        'avg_rating': round(avg_rating, 2),
        'total_installs': total_installs,
        'total_reviews': total_reviews,
        'free_apps': free_count,
        'free_percentage': round((free_count / len(docs)) * 100, 2) if docs else 0,
        'top_categories': sorted([{'name': k, 'count': v} for k, v in categories.items()], key=lambda x: x['count'], reverse=True)[:10]
    }

    category_stats = {}
    for app_doc in docs:
        cat = app_doc.get('category_clean', 'Unknown')
        if cat not in category_stats:
            category_stats[cat] = {'count': 0, 'total_rating': 0, 'total_installs': 0, 'total_reviews': 0, 'free_count': 0, 'paid_count': 0}
        stats_cat = category_stats[cat]
        stats_cat['count'] += 1
        stats_cat['total_rating'] += app_doc.get('rating', 0)
        stats_cat['total_installs'] += app_doc.get('installs', 0)
        stats_cat['total_reviews'] += app_doc.get('reviews', 0)
        if app_doc.get('type', 'Free') == 'Free':
            stats_cat['free_count'] += 1
        else:
            stats_cat['paid_count'] += 1
    category_analysis = []
    for cat, stats_cat in category_stats.items():
        category_analysis.append({
            'category': cat,
            'count': stats_cat['count'],
            'avg_rating': round(stats_cat['total_rating'] / stats_cat['count'], 2) if stats_cat['count'] else 0,
            'total_installs': stats_cat['total_installs'],
            'avg_installs': round(stats_cat['total_installs'] / stats_cat['count']) if stats_cat['count'] else 0,
            'total_reviews': stats_cat['total_reviews'],
            'avg_reviews': round(stats_cat['total_reviews'] / stats_cat['count']) if stats_cat['count'] else 0,
            'free_count': stats_cat['free_count'],
            'paid_count': stats_cat['paid_count'],
            'free_percentage': round((stats_cat['free_count'] / stats_cat['count']) * 100, 2) if stats_cat['count'] else 0
        })
    category_analysis.sort(key=lambda x: x['count'], reverse=True)

    top_apps = sorted(docs, key=lambda x: x.get('installs', 0), reverse=True)[:50]
    top_apps = [
        {
            'name': app_doc.get('app_name', app_doc.get('App Name', 'Unknown')),
            'category': app_doc.get('category_clean', app_doc.get('Category', 'Unknown')),
            'rating': app_doc.get('rating', 0),
            'installs': app_doc.get('installs', 0),
            'reviews': app_doc.get('reviews', 0),
            'type': app_doc.get('type', 'Free'),
            'price': app_doc.get('price_usd', app_doc.get('Price', 0)),
            'content_rating': app_doc.get('content_rating', 'Everyone'),
            'developer': app_doc.get('developer') or app_doc.get('Developer') or 'Unknown'
        }
        for app_doc in top_apps
    ]

    dev_stats = {}
    for app_doc in docs:
        dev = app_doc.get('developer') or app_doc.get('Developer') or 'Unknown'
        if dev not in dev_stats:
            dev_stats[dev] = {'developer': dev, 'total_installs': 0, 'app_count': 0, 'total_reviews': 0}
        dev_stats[dev]['total_installs'] += app_doc.get('installs', 0)
        dev_stats[dev]['app_count'] += 1
        dev_stats[dev]['total_reviews'] += app_doc.get('reviews', 0)
    top_developers = list(dev_stats.values())
    top_developers.sort(key=lambda x: x['total_installs'], reverse=True)
    for d in top_developers[:10]:
        d['avg_installs'] = round(d['total_installs'] / d['app_count']) if d['app_count'] > 0 else 0
    top_developers = top_developers[:10]

    rating_counts = {}
    rating_installs = {}
    for app_doc in docs:
        cr = str(app_doc.get('content_rating', 'Everyone')) or 'Everyone'
        rating_counts[cr] = rating_counts.get(cr, 0) + 1
        rating_installs[cr] = rating_installs.get(cr, 0) + app_doc.get('installs', 0)
    content_rating_distribution = [{'rating': k, 'count': rating_counts[k], 'total_installs': rating_installs.get(k, 0)} for k in rating_counts.keys()]
    content_rating_distribution.sort(key=lambda x: x['count'], reverse=True)

    rating_buckets = {'5.0': 0, '4.5-4.9': 0, '4.0-4.4': 0, '3.5-3.9': 0, '3.0-3.4': 0, '2.5-2.9': 0, '2.0-2.4': 0, '1.5-1.9': 0, '1.0-1.4': 0, '0-0.9': 0}
    for app_doc in docs:
        rating = app_doc.get('rating', 0)
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
    rating_distribution = [{'range': k, 'count': v} for k, v in rating_buckets.items()]

    ratings = [app_doc.get('rating', 0) for app_doc in docs if app_doc.get('rating', 0) > 0 and app_doc.get('reviews', 0) > 0]
    reviews = [app_doc.get('reviews', 0) for app_doc in docs if app_doc.get('rating', 0) > 0 and app_doc.get('reviews', 0) > 0]
    installs = [app_doc.get('installs', 0) for app_doc in docs if app_doc.get('rating', 0) > 0 and app_doc.get('reviews', 0) > 0]

    def calc_corr(x, y):
        n = len(x)
        if n < 2:
            return 0
        mean_x, mean_y = sum(x) / n, sum(y) / n
        num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        den = math.sqrt(sum((xi - mean_x)**2 for xi in x) * sum((yi - mean_y)**2 for yi in y))
        return num / den if den != 0 else 0

    correlation_analysis = {
        'correlations': {
            'rating_reviews': round(calc_corr(ratings, reviews), 3),
            'rating_installs': round(calc_corr(ratings, installs), 3),
            'reviews_installs': round(calc_corr(reviews, installs), 3)
        },
        'scatter_data': [
            {'rating': ratings[i], 'reviews': reviews[i], 'installs': installs[i]}
            for i in random.sample(range(len(ratings)), min(500, len(ratings)))
        ],
        'sample_size': min(500, len(ratings)),
        'total_analyzed': len(ratings)
    }

    price_buckets = {'Free': 0, '$0.01-$0.99': 0, '$1.00-$4.99': 0, '$5.00-$9.99': 0, '$10.00-$19.99': 0, '$20.00+': 0}
    total_installs_by_price = {k: 0 for k in price_buckets}
    for app_doc in docs:
        price = app_doc.get('price_usd', app_doc.get('Price', 0))
        installs_value = app_doc.get('installs', 0)
        if price <= 0:
            price_buckets['Free'] += 1
            total_installs_by_price['Free'] += installs_value
        elif price < 1.0:
            price_buckets['$0.01-$0.99'] += 1
            total_installs_by_price['$0.01-$0.99'] += installs_value
        elif price < 5.0:
            price_buckets['$1.00-$4.99'] += 1
            total_installs_by_price['$1.00-$4.99'] += installs_value
        elif price < 10.0:
            price_buckets['$5.00-$9.99'] += 1
            total_installs_by_price['$5.00-$9.99'] += installs_value
        elif price < 20.0:
            price_buckets['$10.00-$19.99'] += 1
            total_installs_by_price['$10.00-$19.99'] += installs_value
        else:
            price_buckets['$20.00+'] += 1
            total_installs_by_price['$20.00+'] += installs_value
    price_distribution = {
        'app_count': [{'price': k, 'count': v} for k, v in price_buckets.items()],
        'install_distribution': [{'price': k, 'installs': v} for k, v in total_installs_by_price.items()]
    }

    year_counts = {}
    for app_doc in docs:
        released = app_doc.get('released') or app_doc.get('Released', '')
        last_updated = app_doc.get('last_updated') or app_doc.get('Last Updated', '')
        year = extract_year_from_date(released) or extract_year_from_date(last_updated)
        if year:
            year_counts[year] = year_counts.get(year, 0) + 1
    release_year_distribution = [{'year': k, 'count': v} for k, v in sorted(year_counts.items(), key=lambda x: x[0])]

    insights = []
    if categories:
        top_category = max(categories.items(), key=lambda x: x[1])
        insights.append({'type': 'category_dominance', 'title': 'Market Dominance', 'message': f"The '{top_category[0]}' category dominates with {top_category[1]} apps ({round((top_category[1]/len(docs))*100, 1)}% of total)"})
    if ratings:
        insights.append({'type': 'rating_analysis', 'title': 'User Satisfaction', 'message': f"Average app rating is {sum(ratings)/len(ratings):.2f}/5.0, indicating generally positive user sentiment"})
    insights.append({'type': 'monetization', 'title': 'Monetization Model', 'message': f"{(free_count/len(docs))*100:.1f}% of apps are free, confirming the freemium model dominance"})
    total_installs_all = sum(app_doc.get('installs', 0) for app_doc in docs)
    insights.append({'type': 'install_analysis', 'title': 'Market Reach', 'message': f"Total installs across all apps: {total_installs_all:,} (Average: {total_installs_all/len(docs):,.0f} per app)"})

    install_distribution = []
    tiers = {'10M+': 0, '1M-10M': 0, '100K-1M': 0, '10K-100K': 0, '<10K': 0}
    for app_doc in docs:
        installs_value = app_doc.get('installs', 0)
        if installs_value >= 10000000:
            tiers['10M+'] += 1
        elif installs_value >= 1000000:
            tiers['1M-10M'] += 1
        elif installs_value >= 100000:
            tiers['100K-1M'] += 1
        elif installs_value >= 10000:
            tiers['10K-100K'] += 1
        else:
            tiers['<10K'] += 1
    install_distribution = [{'tier': t, 'count': tiers[t]} for t in ['10M+', '1M-10M', '100K-1M', '10K-100K', '<10K']]

    return {
        'stats': stats,
        'category_analysis': category_analysis,
        'top_apps': top_apps,
        'top_developers': top_developers,
        'content_rating_distribution': content_rating_distribution,
        'rating_distribution': rating_distribution,
        'correlation_analysis': correlation_analysis,
        'price_distribution': price_distribution,
        'release_year_distribution': release_year_distribution,
        'insights': insights,
        'install_distribution': install_distribution
    }

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

@app.route('/api/dashboard/summary')
def dashboard_summary():
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"dashboard_summary_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)
    try:
        summary = build_dashboard_summary(filters)
        set_cached(cache_key, summary)
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error in dashboard_summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/stats')
def dashboard_stats():
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"dashboard_stats_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        
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

# ✅ NEW: Install Distribution by Tier Endpoint
@app.route('/api/install-distribution')
def install_distribution():
    filters = {'category': request.args.get('category'), 'type': request.args.get('type'), 'content_rating': request.args.get('content_rating')}
    cache_key = f"install_dist_{filters.get('category') or 'all'}_{filters.get('type') or 'all'}_{filters.get('content_rating') or 'all'}"
    cached = get_cached(cache_key)
    if cached: return jsonify(cached)
    try:
        data = apply_filters(get_all_data(), filters)
        if not data:
            result = [
                {'tier': '10M+', 'count': 0},
                {'tier': '1M-10M', 'count': 0},
                {'tier': '100K-1M', 'count': 0},
                {'tier': '10K-100K', 'count': 0},
                {'tier': '<10K', 'count': 0}
            ]
            set_cached(cache_key, result)
            return jsonify(result)
        
        tiers = {'10M+': 0, '1M-10M': 0, '100K-1M': 0, '10K-100K': 0, '<10K': 0}
        for app_doc in data:
            installs = app_doc.get('installs', 0)
            if installs >= 10000000:
                tiers['10M+'] += 1
            elif installs >= 1000000:
                tiers['1M-10M'] += 1
            elif installs >= 100000:
                tiers['100K-1M'] += 1
            elif installs >= 10000:
                tiers['10K-100K'] += 1
            else:
                tiers['<10K'] += 1
                
        tier_order = ['10M+', '1M-10M', '100K-1M', '10K-100K', '<10K']
        result = [{'tier': tier, 'count': tiers[tier]} for tier in tier_order]
        set_cached(cache_key, result)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in install_distribution: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================
# APP SUCCESS PREDICTION ENDPOINT
# ============================================
# ============================================
# ENHANCED APP SUCCESS PREDICTION ENDPOINT
# ============================================
@app.route('/api/predict', methods=['POST'])
def predict_app_success():
    """
    Advanced app success prediction with market analysis and comparative benchmarks.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract and validate input data
        required_fields = ['category', 'rating', 'reviews', 'installs', 'isFree']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Input values
        category = data.get('category', 'GAME').upper()
        rating = float(data.get('rating', 3.5))
        reviews = int(data.get('reviews', 0))
        installs = int(data.get('installs', 0))
        is_free = bool(data.get('isFree', True))
        price = float(data.get('price', 0))
        app_name = data.get('appName', 'Unknown')
        developer = data.get('developer', 'Unknown')
        content_rating = data.get('contentRating', 'Everyone')
        
        # Get all data for market analysis
        all_data = get_all_data()
        
        # Get category-specific data
        category_apps = [app for app in all_data if app.get('category_clean', '').upper() == category.upper()]
        category_count = len(category_apps)
        
        # Calculate category baselines
        if category_apps:
            avg_category_rating = sum(app.get('rating', 0) for app in category_apps) / len(category_apps)
            avg_category_reviews = sum(app.get('reviews', 0) for app in category_apps) / len(category_apps)
            avg_category_installs = sum(app.get('installs', 0) for app in category_apps) / len(category_apps)
            
            # Percentile calculations
            sorted_installs = sorted([app.get('installs', 0) for app in category_apps])
            percentile_25 = sorted_installs[int(len(sorted_installs) * 0.25)] if sorted_installs else 0
            percentile_50 = sorted_installs[int(len(sorted_installs) * 0.50)] if sorted_installs else 0
            percentile_75 = sorted_installs[int(len(sorted_installs) * 0.75)] if sorted_installs else 0
            
            # Category performance metrics
            category_rating_dist = {
                'excellent': len([a for a in category_apps if a.get('rating', 0) >= 4.5]),
                'good': len([a for a in category_apps if 4.0 <= a.get('rating', 0) < 4.5]),
                'average': len([a for a in category_apps if 3.0 <= a.get('rating', 0) < 4.0]),
                'poor': len([a for a in category_apps if a.get('rating', 0) < 3.0])
            }
        else:
            avg_category_rating = 4.0
            avg_category_reviews = 5000
            avg_category_installs = 100000
            percentile_25 = 10000
            percentile_50 = 50000
            percentile_75 = 200000
            category_rating_dist = {'excellent': 30, 'good': 40, 'average': 25, 'poor': 5}
        
        # Calculate overall market metrics
        all_ratings = [app.get('rating', 0) for app in all_data if app.get('rating', 0) > 0]
        avg_market_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 4.0
        
        all_installs = [app.get('installs', 0) for app in all_data]
        avg_market_installs = sum(all_installs) / len(all_installs) if all_installs else 500000
        
        # ===== ADVANCED SCORING ALGORITHM =====
        
        # 1. QUALITY SCORE (25 points) - Based on rating and reviews
        quality_score = 0
        
        # Rating component (15 points)
        if rating >= 4.5:
            quality_score += 15
        elif rating >= 4.0:
            quality_score += 12
        elif rating >= 3.5:
            quality_score += 9
        elif rating >= 3.0:
            quality_score += 6
        else:
            quality_score += 3
        
        # Review quality ratio (10 points) - High review count with good rating = engaged users
        if installs > 0:
            review_ratio = reviews / installs
            if review_ratio >= 0.01:  # 1% review rate - excellent engagement
                quality_score += 10
            elif review_ratio >= 0.005:  # 0.5% review rate - good
                quality_score += 8
            elif review_ratio >= 0.002:  # 0.2% review rate - average
                quality_score += 5
            elif review_ratio >= 0.001:  # 0.1% review rate - below average
                quality_score += 3
            else:
                quality_score += 1
        else:
            quality_score += 5  # Default if no installs
        
        # 2. MARKET PERFORMANCE SCORE (30 points) - Based on installs relative to category
        market_score = 0
        
        if installs >= percentile_75:
            market_score = 30  # Top 25%
        elif installs >= percentile_50:
            market_score = 24  # Top 50%
        elif installs >= percentile_25:
            market_score = 18  # Top 75%
        else:
            market_score = 10  # Bottom 25%
        
        # Bonus for exceeding category average
        if avg_category_installs > 0 and installs > avg_category_installs:
            market_score += min(5, (installs / avg_category_installs - 1) * 10)
        
        market_score = min(30, market_score)
        
        # 3. USER ENGAGEMENT SCORE (20 points) - Based on reviews and retention indicators
        engagement_score = 0
        
        # Review velocity (10 points)
        if reviews >= 10000:
            engagement_score += 10
        elif reviews >= 5000:
            engagement_score += 8
        elif reviews >= 1000:
            engagement_score += 6
        elif reviews >= 100:
            engagement_score += 4
        else:
            engagement_score += 2
        
        # Rating consistency (10 points) - Compare to category average
        rating_diff = rating - avg_category_rating
        if rating_diff >= 0.5:
            engagement_score += 10  # Much better than average
        elif rating_diff >= 0.2:
            engagement_score += 7  # Better than average
        elif rating_diff >= 0:
            engagement_score += 4  # On par with average
        elif rating_diff >= -0.5:
            engagement_score += 2  # Slightly below average
        else:
            engagement_score += 0  # Significantly below average
        
        # 4. MONETIZATION SCORE (15 points) - Business model effectiveness
        monetization_score = 0
        
        if is_free:
            # Free apps need scale
            if installs >= 1000000:
                monetization_score = 15  # 1M+ installs - excellent for freemium
            elif installs >= 100000:
                monetization_score = 12  # 100K+ - good
            elif installs >= 50000:
                monetization_score = 9   # 50K+ - average
            elif installs >= 10000:
                monetization_score = 6   # 10K+ - below average
            else:
                monetization_score = 3   # <10K - needs work
        else:
            # Paid apps need conversion
            if price >= 0.99 and price <= 4.99:
                # Good price point
                if installs >= 10000:
                    monetization_score = 15  # Good sales
                elif installs >= 5000:
                    monetization_score = 12
                elif installs >= 1000:
                    monetization_score = 9
                else:
                    monetization_score = 6
            elif price < 0.99:
                monetization_score = 8  # Low price, needs volume
            else:
                # Premium pricing
                if installs >= 5000:
                    monetization_score = 12  # Premium success
                elif installs >= 1000:
                    monetization_score = 9
                else:
                    monetization_score = 6
        
        # 5. COMPETITIVE POSITION SCORE (10 points) - Market positioning
        competitive_score = 0
        
        # Category competition analysis
        category_demand_factors = {
            'GAME': {'competition': 'Very High', 'factor': 0.8},
            'SOCIAL': {'competition': 'High', 'factor': 0.85},
            'PRODUCTIVITY': {'competition': 'Medium', 'factor': 1.0},
            'EDUCATION': {'competition': 'Medium', 'factor': 1.0},
            'HEALTH': {'competition': 'Medium', 'factor': 1.0},
            'FINANCE': {'competition': 'Medium-High', 'factor': 0.9},
            'LIFESTYLE': {'competition': 'Medium', 'factor': 1.0},
            'ENTERTAINMENT': {'competition': 'High', 'factor': 0.9},
            'COMMUNICATION': {'competition': 'Very High', 'factor': 0.75},
            'TRAVEL': {'competition': 'Medium', 'factor': 1.0}
        }
        
        cat_info = category_demand_factors.get(category, {'competition': 'Unknown', 'factor': 1.0})
        
        # Score based on performance in competitive category
        if category_count > 0:
            position = (installs / avg_category_installs) if avg_category_installs > 0 else 0
            if position >= 2.0:
                competitive_score = 10  # Outperforming competitors
            elif position >= 1.0:
                competitive_score = 7   # On par with competitors
            elif position >= 0.5:
                competitive_score = 4   # Below average but viable
            else:
                competitive_score = 2   # Needs significant improvement
        
        # Calculate total success score
        total_score = (
            quality_score +
            market_score +
            engagement_score +
            monetization_score +
            competitive_score
        )
        
        success_score = min(100, max(0, total_score))
        
        # Calculate success probability using logistic function
        probability = 1 / (1 + math.exp(-(success_score - 50) / 15))
        
        # ===== MARKET POSITION ANALYSIS =====
        
        # Determine market position
        if success_score >= 80:
            market_position = 'Market Leader'
            position_description = 'Your app is positioned as a top performer in its category'
        elif success_score >= 60:
            market_position = 'Strong Contender'
            position_description = 'Your app shows strong potential to compete effectively'
        elif success_score >= 40:
            market_position = 'Growing App'
            position_description = 'Your app has room for improvement but solid foundation'
        else:
            market_position = 'Needs Improvement'
            position_description = 'Significant improvements needed to compete effectively'
        
        # ===== RISK & OPPORTUNITY ANALYSIS =====
        
        risks = []
        opportunities = []
        
        # Risk factors
        if rating < 3.5:
            risks.append({'severity': 'High', 'issue': 'Low rating', 'impact': 'Users may uninstall quickly'})
        if reviews < 100 and installs > 1000:
            risks.append({'severity': 'Medium', 'issue': 'Low engagement', 'impact': 'Users not leaving reviews suggests low engagement'})
        if not is_free and installs < 1000:
            risks.append({'severity': 'High', 'issue': 'Low paid app adoption', 'impact': 'Revenue potential severely limited'})
        if installs < percentile_25 and category_count > 10:
            risks.append({'severity': 'Medium', 'issue': 'Below category average', 'impact': 'Struggling to compete in saturated market'})
        
        # Opportunity factors
        if rating >= 4.0 and installs < percentile_50:
            opportunities.append({'potential': 'High', 'area': 'Quality product, needs marketing', 'action': 'Increase marketing spend to reach more users'})
        if installs > avg_category_installs:
            opportunities.append({'potential': 'Medium', 'area': 'Market leader potential', 'action': 'Consider premium features or expansion'})
        if not is_free and rating >= 4.5:
            opportunities.append({'potential': 'High', 'area': 'Premium pricing power', 'action': 'Could increase price point with strong quality'})
        if category_count < 100:
            opportunities.append({'potential': 'Medium', 'area': 'Less competitive category', 'action': 'Focus on quality to dominate niche market'})
        
        # ===== COMPARATIVE BENCHMARKS =====
        
        benchmarks = {
            'rating': {
                'yours': rating,
                'category_avg': round(avg_category_rating, 2),
                'market_avg': round(avg_market_rating, 2),
                'percentile': calculate_percentile(rating, [app.get('rating', 0) for app in all_data if app.get('rating', 0) > 0])
            },
            'installs': {
                'yours': installs,
                'category_avg': int(avg_category_installs),
                'market_avg': int(avg_market_installs),
                'percentile': calculate_percentile(installs, all_installs)
            },
            'reviews': {
                'yours': reviews,
                'category_avg': int(avg_category_reviews),
                'market_avg': int(sum(app.get('reviews', 0) for app in all_data) / len(all_data)) if all_data else 0,
                'percentile': calculate_percentile(reviews, [app.get('reviews', 0) for app in all_data])
            }
        }
        
        # ===== SUCCESS ROADMAP =====
        
        roadmap = []
        
        if rating < 4.0:
            roadmap.append({
                'priority': 'Critical',
                'milestone': 'Improve rating to 4.0+',
                'actions': ['Fix critical bugs', 'Improve user experience', 'Add requested features'],
                'impact': '+15-20 success points'
            })
        
        if installs < percentile_50:
            roadmap.append({
                'priority': 'High',
                'milestone': 'Reach category median installs',
                'actions': ['Increase marketing budget', 'Optimize ASO', 'Consider paid promotion'],
                'impact': '+10-15 success points'
            })
        
        if reviews < 1000:
            roadmap.append({
                'priority': 'Medium',
                'milestone': 'Build review base to 1,000+',
                'actions': ['Implement review prompts', 'Engage with users', 'Respond to feedback'],
                'impact': '+5-10 success points'
            })
        
        if not roadmap:
            roadmap.append({
                'priority': 'Growth',
                'milestone': 'Scale and expand',
                'actions': ['Add premium features', 'Expand to new markets', 'Build brand loyalty'],
                'impact': 'Market leadership'
            })
        
        # ===== FINAL RECOMMENDATIONS =====
        
        recommendations = []
        
        if rating < 4.0:
            recommendations.append("Prioritize user experience improvements to achieve 4.0+ rating - this is critical for long-term success")
        if reviews < 500:
            recommendations.append("Implement strategic review prompts and user engagement features to build social proof")
        if installs < percentile_50:
            recommendations.append("Invest in user acquisition through ASO optimization, social media marketing, or paid advertising")
        if not is_free and installs < 5000:
            recommendations.append("Consider freemium model or free trial to increase user base before monetization")
        if rating >= 4.0 and installs < percentile_25:
            recommendations.append("Your quality is strong - focus on marketing to reach more users")
        if rating >= 4.5 and reviews >= 5000:
            recommendations.append("Excellent foundation - consider premium features or expansion to maximize revenue")
        
        if not recommendations:
            recommendations.append("Your app is well-positioned for success!")
            recommendations.append("Focus on retention and building long-term user loyalty")
            recommendations.append("Consider expansion or premium features to maximize potential")
        
        # ===== FACTORS FOR UI DISPLAY =====
        
        factors = {
            'qualityScore': round(quality_score, 1),
            'marketScore': round(market_score, 1),
            'engagementScore': round(engagement_score, 1),
            'monetizationScore': round(monetization_score, 1),
            'competitiveScore': round(competitive_score, 1),
            'ratingImpact': f"{rating:.1f}/5.0 ({rating_diff:+.1f} vs avg)",
            'installProjection': f"{installs:,}",
            'categoryPosition': f"{position:.1f}x category avg",
            'revenuePotential': f"${price:.2f}" if not is_free else "Freemium Model",
            'competitionLevel': cat_info['competition'],
            'categoryPerformance': 'Excellent' if success_score >= 70 else 'Good' if success_score >= 50 else 'Average' if success_score >= 30 else 'Needs Work',
            'engagementPotential': 'High' if engagement_score >= 15 else 'Medium' if engagement_score >= 10 else 'Low'
        }
        
        result = {
            'successScore': round(success_score, 1),
            'probability': round(probability, 4),
            'marketPosition': market_position,
            'positionDescription': position_description,
            'factors': factors,
            'benchmarks': benchmarks,
            'risks': risks,
            'opportunities': opportunities,
            'roadmap': roadmap,
            'recommendation': {
                'score': round(success_score, 1),
                'recommendations': recommendations
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in predict_app_success: {e}")
        return jsonify({'error': str(e), 'message': 'Failed to predict app success'}), 500


def calculate_percentile(value, data_list):
    """Calculate percentile rank of a value in a dataset"""
    if not data_list:
        return 0
    sorted_data = sorted(data_list)
    count_below = sum(1 for x in sorted_data if x < value)
    return round((count_below / len(sorted_data)) * 100, 1)

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
