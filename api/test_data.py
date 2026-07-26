# test_data.py - Dummy data for testing API
import json

SAMPLE_DATA = [
    {
        "app_name": "Instagram",
        "category_clean": "SOCIAL",
        "rating": 4.5,
        "installs": 1000000000,
        "reviews": 5000000,
        "size_mb": 45.6,
        "price_usd": 0,
        "type": "Free"
    },
    {
        "app_name": "Subway Surfers",
        "category_clean": "GAME",
        "rating": 4.3,
        "installs": 500000000,
        "reviews": 2000000,
        "size_mb": 85.6,
        "price_usd": 0,
        "type": "Free"
    },
    {
        "app_name": "Minecraft",
        "category_clean": "GAME",
        "rating": 4.8,
        "installs": 200000000,
        "reviews": 3000000,
        "size_mb": 120.5,
        "price_usd": 6.99,
        "type": "Paid"
    }
]

def get_sample_data():
    return SAMPLE_DATA

# Save as JSON for testing
with open('sample_data.json', 'w') as f:
    json.dump(SAMPLE_DATA, f, indent=2)