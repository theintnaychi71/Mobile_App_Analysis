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


# # ============================================
# ENHANCED APP SUCCESS PREDICTION ENDPOINT
# ============================================
@app.route('/api/predict', methods=['POST'])
def predict_app_success():
    """
    Strategic Market Readiness Evaluator.
    Evaluates the viability of an app's business plan against real market benchmarks.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 1. Extract strategic inputs
        category = data.get('category', 'GAME').upper()
        monetization = data.get('monetizationModel', 'Freemium')
        audience = data.get('targetAudience', 'Broad (General public)')
        marketing = data.get('marketingBudget', 'Low (<$1k/mo)')
        uvp = data.get('uniqueValue', 'Medium (Better version of existing)')
        experience = data.get('teamExperience', 'Some experience')
        retention = data.get('retentionFocus', 'Medium (Occasional use)')
        app_name = data.get('appName', 'Untitled App')
        
        # 2. Fetch real market data for benchmarking
        all_data = get_all_data()
        category_apps = [app for app in all_data if app.get('category_clean', '').upper() == category]
        
        # Also check parent category (e.g., ARCADE -> GAME)
        parent_category = category.split('_')[0] if '_' in category else category
        if not category_apps and parent_category != category:
            category_apps = [app for app in all_data if app.get('category_clean', '').upper() == parent_category]
        
        if category_apps:
            avg_category_rating = sum(app.get('rating', 0) for app in category_apps) / len(category_apps)
            avg_category_installs = sum(app.get('installs', 0) for app in category_apps) / len(category_apps)
        else:
            avg_category_rating = 4.2
            avg_category_installs = 100000
            
        all_ratings = [app.get('rating', 0) for app in all_data if app.get('rating', 0) > 0]
        avg_market_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 4.2
        all_installs = [app.get('installs', 0) for app in all_data]
        avg_market_installs = sum(all_installs) / len(all_installs) if all_installs else 500000
        
        # ==========================================
        # SCORING ALGORITHM
        # ==========================================
        
        # 1. PRODUCT VIABILITY (Max 30)
        product_score = 0
        if 'High' in uvp or 'nothing else' in uvp.lower(): product_score += 15
        elif 'Medium' in uvp or 'better' in uvp.lower(): product_score += 10
        else: product_score += 5
        
        if 'Experienced' in experience: product_score += 15
        elif 'Some' in experience: product_score += 10
        else: product_score += 5
        
        # 2. MARKET FIT (Max 25)
        market_score = 0
        high_demand_categories = ['GAME', 'SOCIAL', 'ENTERTAINMENT', 'PRODUCTIVITY', 
                                   'HEALTH', 'COMMUNICATION', 'ARCADE', 'CASUAL', 
                                   'ACTION', 'ADVENTURE', 'PUZZLE', 'RACING', 'SPORTS']
        
        is_high_demand = any(hd in category for hd in high_demand_categories)
        is_broad = 'Broad' in audience
        is_niche = 'Niche' in audience
        is_b2b = 'B2B' in audience
        
        if is_high_demand and is_broad:
            market_score = 25
        elif is_high_demand and is_niche:
            market_score = 18
        elif is_niche and not is_high_demand:
            market_score = 15
        elif is_b2b:
            market_score = 12
        else:
            market_score = 10
            
        # 3. GROWTH & MARKETING (Max 25)
        growth_score = 0
        if 'High' in marketing: growth_score += 15
        elif 'Medium' in marketing: growth_score += 10
        elif 'Low' in marketing: growth_score += 5
        else: growth_score += 2
        
        # Monetization alignment bonus
        if monetization in ['Freemium', 'Free (Ad-supported)'] and ('Medium' in marketing or 'High' in marketing):
            growth_score += 10
        elif monetization == 'Paid' and is_niche:
            growth_score += 10
        elif monetization == 'Subscription' and ('Medium' in marketing or 'High' in marketing):
            growth_score += 8
        else:
            growth_score += 3
            
        # 4. RETENTION & ENGAGEMENT (Max 20)
        retention_score = 0
        if 'High' in retention or 'daily' in retention.lower(): retention_score += 20
        elif 'Medium' in retention or 'occasional' in retention.lower(): retention_score += 12
        else: retention_score += 5
        
        # Total
        total_score = product_score + market_score + growth_score + retention_score
        success_score = min(100, max(0, total_score))
        probability = 1 / (1 + math.exp(-(success_score - 50) / 15))
        
        # ==========================================
        # MARKET POSITION
        # ==========================================
        if success_score >= 80:
            market_position = 'Highly Viable'
            position_description = 'Your strategic plan is well-balanced and positioned for strong market traction.'
        elif success_score >= 60:
            market_position = 'Moderately Viable'
            position_description = 'Your plan has solid foundations, but requires refinement in key areas to mitigate risk.'
        elif success_score >= 40:
            market_position = 'High Risk'
            position_description = 'Significant strategic gaps exist. Pivot or adjust your plan before investing heavily.'
        else:
            market_position = 'Critical Risk'
            position_description = 'Current plan is highly unlikely to succeed without major fundamental changes.'
        
        # ==========================================
        # DYNAMIC RISKS (Score-based + Logic-based)
        # ==========================================
        risks = []
        
        # Score-based risks (these WILL fire based on actual scores)
        if product_score < 15:
            risks.append({
                'severity': 'High',
                'issue': 'Weak product differentiation',
                'impact': 'Without a clear unique hook, users have no compelling reason to switch from established competitors.'
            })
        elif product_score < 20:
            risks.append({
                'severity': 'Medium',
                'issue': 'Moderate product risk',
                'impact': 'Your product is solid but not exceptional. First-time teams face a steep learning curve.'
            })
        
        if market_score < 15:
            risks.append({
                'severity': 'High',
                'issue': 'Poor category-audience fit',
                'impact': 'Your target audience and chosen category are misaligned. This makes discovery and conversion much harder.'
            })
        elif market_score < 20:
            risks.append({
                'severity': 'Medium',
                'issue': 'Crowded or mismatched market',
                'impact': 'You\'re entering a competitive space without a clear niche advantage.'
            })
        
        if growth_score < 10:
            risks.append({
                'severity': 'High',
                'issue': 'Severely underfunded growth plan',
                'impact': 'Without marketing spend or a strong organic strategy, your app will be invisible in the store.'
            })
        elif growth_score < 15:
            risks.append({
                'severity': 'Medium',
                'issue': 'Limited growth budget',
                'impact': 'You\'ll need to rely heavily on organic discovery (ASO, word-of-mouth), which is slow and unpredictable.'
            })
        
        if retention_score < 10:
            risks.append({
                'severity': 'High',
                'issue': 'One-time use pattern',
                'impact': 'Users will download, use once, and delete. You need constant new users to survive.'
            })
        elif retention_score < 15:
            risks.append({
                'severity': 'Medium',
                'issue': 'Occasional use pattern',
                'impact': 'Users will forget about your app between uses. You must invest in retention mechanics.'
            })
        
        # Logic-based risks (specific dangerous combinations)
        if 'None' in marketing and any(x in category for x in ['GAME', 'SOCIAL', 'ENTERTAINMENT', 'ARCADE']):
            risks.append({
                'severity': 'High',
                'issue': 'Zero marketing in a saturated category',
                'impact': 'Top categories have thousands of competitors. Organic discovery alone is nearly impossible.'
            })
        
        if monetization == 'Paid' and is_broad:
            risks.append({
                'severity': 'Medium',
                'issue': 'Paid pricing with broad audience',
                'impact': 'Broad audiences expect free apps. Consider freemium to lower the barrier to entry.'
            })
        
        if 'Low' in retention.lower() and monetization == 'Free (Ad-supported)':
            risks.append({
                'severity': 'High',
                'issue': 'Ad-supported model with low retention',
                'impact': 'Ads need repeated usage to generate revenue. One-time users generate almost nothing.'
            })
        
        if not risks:
            risks.append({
                'severity': 'Low',
                'issue': 'No major red flags detected',
                'impact': 'Your plan is balanced. Focus on execution and gathering real user feedback.'
            })
        
        # ==========================================
        # DYNAMIC OPPORTUNITIES
        # ==========================================
        opportunities = []
        
        if product_score >= 20:
            opportunities.append({
                'potential': 'High',
                'area': 'Strong product foundation',
                'action': 'Your differentiation is clear. Double down on this in all marketing messaging.'
            })
        
        if retention_score >= 18:
            opportunities.append({
                'potential': 'High',
                'area': 'High lifetime value potential',
                'action': 'Daily users are valuable. Build a subscription model or recurring revenue stream from day one.'
            })
        
        if market_score >= 20:
            opportunities.append({
                'potential': 'High',
                'area': 'Strong market fit',
                'action': 'Your audience and category align well. Focus on rapid user acquisition to capture market share.'
            })
        
        if growth_score >= 15:
            opportunities.append({
                'potential': 'Medium',
                'area': 'Well-funded growth',
                'action': 'You have budget to experiment. Test multiple acquisition channels (social, search, influencers) quickly.'
            })
        
        if is_niche and product_score >= 15:
            opportunities.append({
                'potential': 'High',
                'area': 'Niche domination',
                'action': 'Niche markets reward specialization. Build deep features your broad competitors ignore.'
            })
        
        if 'Low' in marketing or 'None' in marketing:
            opportunities.append({
                'potential': 'Medium',
                'area': 'Organic growth leverage',
                'action': 'Invest heavily in ASO, content marketing, and community building to compensate for low paid spend.'
            })
        
        if not opportunities:
            opportunities.append({
                'potential': 'Medium',
                'area': 'Execution advantage',
                'action': 'Focus on flawless launch and rapid iteration based on real user feedback.'
            })
        
        # ==========================================
        # DYNAMIC ROADMAP (Based on WEAKEST area)
        # ==========================================
        roadmap = []
        scores = {
            'product': product_score,
            'market': market_score,
            'growth': growth_score,
            'retention': retention_score
        }
        weakest = min(scores, key=scores.get)
        
        if weakest == 'product':
            roadmap.append({
                'priority': 'Critical',
                'milestone': 'Sharpen your unique value',
                'actions': [
                    'Survey 20+ potential users about their biggest pain points',
                    'Identify ONE feature competitors do poorly and do it 10x better',
                    'Rewrite your store description to lead with this unique benefit'
                ],
                'impact': 'Increases conversion rate by 20-40%'
            })
        
        if weakest == 'market':
            roadmap.append({
                'priority': 'Critical',
                'milestone': 'Fix your market positioning',
                'actions': [
                    'Reconsider your target audience or category choice',
                    'Research the top 10 competitors in your chosen space',
                    'Find an underserved sub-niche within your category'
                ],
                'impact': 'Reduces customer acquisition cost by 30%+'
            })
        
        if weakest == 'growth':
            roadmap.append({
                'priority': 'Critical',
                'milestone': 'Build a realistic growth engine',
                'actions': [
                    'Master App Store Optimization (keywords, icon, screenshots)',
                    'Build a pre-launch waitlist or community',
                    'Plan a launch campaign with influencers or content partners'
                ],
                'impact': 'Essential for visibility in a crowded market'
            })
        
        if weakest == 'retention':
            roadmap.append({
                'priority': 'Critical',
                'milestone': 'Design for repeated use',
                'actions': [
                    'Add push notifications with personalized value',
                    'Implement streaks, progress tracking, or gamification',
                    'Create reasons for users to return weekly (new content, updates)'
                ],
                'impact': 'Boosts lifetime value by 3-5x'
            })
        
        # Add a secondary roadmap item based on second-weakest area
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        second_weakest = sorted_scores[1][0]
        
        if second_weakest == 'product' and weakest != 'product':
            roadmap.append({
                'priority': 'High',
                'milestone': 'Strengthen product differentiation',
                'actions': ['Identify one underserved user need', 'A/B test feature variations', 'Gather early user feedback aggressively'],
                'impact': 'Improves retention and word-of-mouth'
            })
        elif second_weakest == 'growth' and weakest != 'growth':
            roadmap.append({
                'priority': 'High',
                'milestone': 'Optimize your growth strategy',
                'actions': ['Research ASO best practices for your category', 'Plan a launch timeline', 'Identify 3 free marketing channels'],
                'impact': 'Accelerates early traction'
            })
        elif second_weakest == 'retention' and weakest != 'retention':
            roadmap.append({
                'priority': 'High',
                'milestone': 'Improve user retention',
                'actions': ['Add onboarding that teaches core value', 'Implement re-engagement notifications', 'Create weekly content updates'],
                'impact': 'Increases long-term user value'
            })
        elif second_weakest == 'market' and weakest != 'market':
            roadmap.append({
                'priority': 'High',
                'milestone': 'Refine market positioning',
                'actions': ['Study top 5 competitors deeply', 'Identify gaps in their offerings', 'Position your app to fill those gaps'],
                'impact': 'Creates clearer competitive advantage'
            })
        
        if success_score >= 70:
            roadmap.append({
                'priority': 'Growth',
                'milestone': 'Scale and expand',
                'actions': ['Add premium features or subscription tier', 'Expand to adjacent markets', 'Build brand loyalty programs'],
                'impact': 'Market leadership'
            })
        
        # ==========================================
        # RECOMMENDATIONS
        # ==========================================
        recommendations = []
        
        if product_score < 15:
            recommendations.append("Your app lacks a clear unique angle. Before launch, find ONE specific problem you solve better than anyone else.")
        if growth_score < 15:
            recommendations.append("With limited marketing budget, ASO (App Store Optimization) and community building are non-negotiable. Master these first.")
        if retention_score < 15:
            recommendations.append("Design retention mechanics from day one: push notifications, streaks, progress tracking, or regular content updates.")
        if market_score < 15:
            recommendations.append("Reconsider your target audience or category. A niche audience in a less crowded category is often easier to win.")
        if monetization == 'Paid' and is_broad:
            recommendations.append("Consider switching to freemium. Broad audiences rarely pay upfront but will spend on in-app purchases.")
        
        if success_score >= 70:
            recommendations.append("Your plan is strong. Focus on flawless execution and rapid iteration based on real user feedback.")
            recommendations.append("Set up analytics from day one to track actual retention and conversion vs. these projections.")
        
        if not recommendations:
            recommendations.append("Focus on flawless execution and gathering early user feedback.")
            recommendations.append("Set up analytics from day one to track actual retention and conversion rates.")
        
        # ==========================================
        # CLEAN DISPLAY LABELS (for UI)
        # ==========================================
        def clean_label(text, mapping):
            for key, label in mapping.items():
                if key in text:
                    return label
            return text
        
        uvp_labels = {
            'nothing else': '🚀 Unique solution',
            'better': '🔧 Improved version',
            'similar': '⚠️ Similar to others',
            'High': '🚀 Unique solution',
            'Medium': '🔧 Improved version',
            'Low': '⚠️ Similar to others'
        }
        
        retention_labels = {
            'daily': '📅 Used daily',
            'occasional': '📆 Used weekly/monthly',
            'one-time': '⚡ Used once',
            'High': '📅 Used daily',
            'Medium': '📆 Used weekly/monthly',
            'Low': '⚡ Used once'
        }
        
        marketing_labels = {
            'None': '🚫 No budget',
            'Low': '💰 Small budget',
            'Medium': '💵 Medium budget',
            'High': '💎 Large budget'
        }
        
        factors = {
            'productScore': round(product_score, 1),
            'marketScore': round(market_score, 1),
            'growthScore': round(growth_score, 1),
            'retentionScore': round(retention_score, 1),
            'uvpDisplay': clean_label(uvp, uvp_labels),
            'categoryPerformance': 'Strong' if market_score >= 20 else 'Moderate' if market_score >= 15 else 'Needs Work',
            'marketingDisplay': clean_label(marketing, marketing_labels),
            'retentionDisplay': clean_label(retention, retention_labels),
            'monetizationStrategy': monetization
        }
        
                # ==========================================
        # BENCHMARKS (Show TARGETS, not N/A)
        # ==========================================
        
        # Calculate realistic targets based on their plan
        target_rating = max(4.0, round(avg_category_rating + 0.2, 2))
        
        # Install targets based on marketing budget and retention
        if 'High' in marketing:
            if 'High' in retention or 'daily' in retention.lower():
                install_target = "100K-500K (Year 1)"
            else:
                install_target = "50K-200K (Year 1)"
        elif 'Medium' in marketing:
            if 'High' in retention or 'daily' in retention.lower():
                install_target = "20K-100K (Year 1)"
            else:
                install_target = "10K-50K (Year 1)"
        elif 'Low' in marketing:
            if 'High' in retention or 'daily' in retention.lower():
                install_target = "5K-20K (Year 1)"
            else:
                install_target = "1K-10K (Year 1)"
        else:  # None
            if 'High' in retention or 'daily' in retention.lower():
                install_target = "500-5K (Year 1)"
            else:
                install_target = "100-1K (Year 1)"
        
        # Review strategy based on retention pattern
        if 'High' in retention or 'daily' in retention.lower():
            review_strategy = "Prompt after 7-day streak"
        elif 'Medium' in retention or 'occasional' in retention.lower():
            review_strategy = "Prompt after 3rd use"
        else:
            review_strategy = "Prompt right after task completion"
        
        benchmarks = {
            'rating': {
                'yours': f"{target_rating}+ ⭐",
                'category_avg': round(avg_category_rating, 2),
                'market_avg': round(avg_market_rating, 2),
                'percentile': 0,
                'note': f"Goal: Aim for {target_rating}+ to stand out in {category}"
            },
            'installs': {
                'yours': install_target,
                'category_avg': f"{int(avg_category_installs):,}",
                'market_avg': f"{int(avg_market_installs):,}",
                'percentile': 0,
                'note': "Goal: Top 25% of apps in this category have 10x the average."
            },
            'reviews': {
                'yours': review_strategy,
                'category_avg': 'Varies',
                'market_avg': 'Varies',
                'percentile': 0,
                'note': "Goal: Implement in-app review prompts after positive user actions."
            }
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
        return jsonify({'error': str(e), 'message': 'Failed to evaluate app readiness'}), 500
    
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
