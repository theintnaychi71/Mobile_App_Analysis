# ============================================
# COMPLETE API FOR APP MARKET DASHBOARD
# ============================================

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
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')

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

def get_all_data():
    """Get all data (from MongoDB or sample)"""
    if app.config['USE_SAMPLE_DATA']:
        return SAMPLE_DATA
    
    try:
        collection = mongo.db.apps
        data = list(collection.find({}, {'_id': 0}))
        return data if data else SAMPLE_DATA
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