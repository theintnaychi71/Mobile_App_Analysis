import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

NUM_ROWS = 50000
TARGET_DATE = datetime(2026, 7, 29)

print(f"⏳ Generating {NUM_ROWS} realistic app records matching your exact real-world constraints...")

# 1. CATEGORIES (Top apps in order)
categories = ['Games', 'Entertainment', 'Education', 'Tools', 'Social Media', 'Finance', 'Productivity']
cat_weights = [0.30, 0.15, 0.15, 0.10, 0.10, 0.10, 0.10] 

# 2. INSTALLATION DISTRIBUTION BY TIER (In your requested order)
install_tiers = ['10K-100K', '100K-1M', '1M-10M', '<10K', '10M+']
install_weights = [0.30, 0.25, 0.20, 0.15, 0.10] 
install_ranges = {
    '<10K': (100, 9999),
    '10K-100K': (10000, 99999),
    '100K-1M': (100000, 999999),
    '1M-10M': (1000000, 9999999),
    '10M+': (10000000, 100000000)
}
# Map tiers to your requested Popularity_Tier names
pop_tier_map = {
    '<10K': 'Niche (<10K)', '10K-100K': 'Growing (10K-100K)', 
    '100K-1M': 'Popular (100K-1M)', '1M-10M': 'Very Popular (1M-10M)', '10M+': 'Mega Hit (10M+)'
}

# 3. RATING DISTRIBUTION (In your requested order)
rating_tiers = ['4.4-4.6', '4.0-4.4', '4.6-5.0', '3.5-4.0', 'Below 3.5']
rating_weights = [0.35, 0.30, 0.15, 0.15, 0.05] 
rating_ranges = {
    '4.4-4.6': (4.4, 4.6), '4.0-4.4': (4.0, 4.4), '4.6-5.0': (4.6, 5.0),
    '3.5-4.0': (3.5, 4.0), 'Below 3.5': (1.0, 3.5)
}

# 4. TOP DEVELOPERS (Your exact list + fillers to make 100%)
developers = [
    'Google LLC', 'Meta Platforms', 'WhatsApp LLC, Inc.', 'Microsoft Corporation', 
    'ByteDance', 'Samsung Electronics', 'Supercell', 'King', 'Tencent Games', 
    'Netflix, Inc.', 'Independent Dev', 'Unknown Studio', 'Tech Solutions'
]
# Top 10 get ~6.5% each, fillers get the rest
dev_weights = [0.065, 0.065, 0.065, 0.065, 0.065, 0.065, 0.065, 0.065, 0.065, 0.065, 0.115, 0.115, 0.115]

# 5. RELEASE YEAR RANKING (Exact order requested)
years = [2017, 2016, 2018, 2019, 2020, 2021, 2015, 2022, 2023, 2024, 2025, 2026]
year_weights = [0.15, 0.14, 0.13, 0.12, 0.11, 0.10, 0.09, 0.08, 0.05, 0.02, 0.008, 0.002]

# ==========================================
# ✅ FIX 1: Normalize all weights to sum EXACTLY to 1.0
# ==========================================
cat_weights = [w / sum(cat_weights) for w in cat_weights]
install_weights = [w / sum(install_weights) for w in install_weights]
rating_weights = [w / sum(rating_weights) for w in rating_weights]
dev_weights = [w / sum(dev_weights) for w in dev_weights]
year_weights = [w / sum(year_weights) for w in year_weights]

# --- GENERATION ---
data = []

for _ in range(NUM_ROWS):
    # 1. Category
    cat = np.random.choice(categories, p=cat_weights)
    
    # 2. Installs & Popularity Tier
    pop_tier_raw = np.random.choice(install_tiers, p=install_weights)
    min_inst, max_inst = install_ranges[pop_tier_raw]
    installs = random.randint(min_inst, max_inst)
    pop_tier = pop_tier_map[pop_tier_raw]
    
    # 3. Rating (High precision like your example: 4.7608705)
    rate_tier = np.random.choice(rating_tiers, p=rating_weights)
    min_r, max_r = rating_ranges[rate_tier]
    rating = round(random.uniform(min_r, max_r), 7)
    
    # 4. Developer
    dev = np.random.choice(developers, p=dev_weights)
    
    # 5. Release Year & Dates
    year = int(np.random.choice(years, p=year_weights))
    
    # ✅ FIX 2: Cap 2026 dates so they never exceed TARGET_DATE (July 29, 2026)
    if year == 2026:
        month = random.randint(1, 7)
        day = random.randint(1, 29) if month == 7 else random.randint(1, 28)
    else:
        month = random.randint(1, 12)
        day = random.randint(1, 28)
    
    released_date = datetime(year, month, day)
    released_str = released_date.strftime('%Y-%m-%d')
    
    # Last Updated (between release and TARGET_DATE)
    days_since = (TARGET_DATE - released_date).days
    
    # ✅ FIX 3: Ensure the random range is always valid (min 1, max 730)
    max_days_ago = max(1, min(730, days_since))
    update_days_ago = random.randint(1, max_days_ago)
    
    last_updated_date = TARGET_DATE - timedelta(days=update_days_ago)
    last_updated_str = last_updated_date.strftime('%Y-%m-%d')
    
    app_age_days = (last_updated_date - released_date).days
    
    # 6. Reviews (Realistic ratio based on installs)
    reviews = max(1, int(installs * random.uniform(0.002, 0.008)))
    
    # 7. Free & Price
    is_free = random.random() < 0.90 # 90% free
    if is_free:
        price = 0.0
        price_tier = 'Free'
    else:
        price = random.choice([0.99, 1.99, 2.99, 4.99, 9.99])
        if price < 1.0: price_tier = 'Under $1'
        elif price <= 5.0: price_tier = '$1-$5'
        else: price_tier = 'Over $5'
        
    # 8. Monetization
    in_app_purchases = True if random.random() < 0.75 else False
    contains_ads = True if (is_free and random.random() < 0.70) else False
    
    # 9. App Name & ID
    prefixes = ['Super', 'Pro', 'Ultra', 'Smart', 'Daily', 'Epic', 'Quick', 'My', 'Top']
    suffixes = ['App', 'Hub', 'Go', 'Lite', 'Plus', '360', 'Master', 'World', 'Search']
    app_name = f"{random.choice(prefixes)} {cat.split()[0]} {random.choice(suffixes)}"
    
    dev_clean = dev.lower().replace(' ', '').replace(',', '').replace('.', '')
    cat_clean = cat.lower().replace(' ', '').replace('&', '')
    app_id = f"com.{dev_clean}.{cat_clean}{random.randint(100, 9999)}"
    
    data.append({
        'App ID': app_id,
        'App Name': app_name,
        'Category': cat,
        'Rating': rating,
        'Reviews': reviews,
        'Installs': installs,
        'Free': True if is_free else False,
        'Price': price,
        'Released': released_str,
        'Last Updated': last_updated_str,
        'Developer': dev,
        'In-App Purchases': in_app_purchases,
        'Contains Ads': contains_ads,
        'App_Age_Days': app_age_days,
        'Price_Tier': price_tier,
        'Popularity_Tier': pop_tier
    })

# Convert to DataFrame and Save
df = pd.DataFrame(data)
output_file = 'real_world_50k_dataset.csv'
df.to_csv(output_file, index=False)

print(f"\n✅ SUCCESS! Saved {len(df)} rows to '{output_file}'")
print("\n📊 Verification of Real-World Constraints:")
print("-" * 50)
print("Top Categories:")
print(df['Category'].value_counts())
print("\nPopularity Tier Distribution:")
print(df['Popularity_Tier'].value_counts())
print("\nRelease Year Ranking:")
df['Year'] = pd.to_datetime(df['Released']).dt.year
print(df['Year'].value_counts().sort_index(ascending=False))