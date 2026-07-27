import pandas as pd
import pymongo

# ==========================================
# 1. DATABASE CONNECTION & DATA LOADING
# ==========================================

MONGO_URI = "mongodb+srv://data_uploader:A7KQDxaxgMKIbevE@cluster0.cuueyms.mongodb.net/?appName=Cluster0"
MONGO_DB = "app_market_db"
MONGO_COLLECTION = "apps"

print("Connecting to MongoDB Atlas...")
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    
    data_cursor = collection.find({}, {"_id": 0})
    df = pd.DataFrame(list(data_cursor))
    print(f"Success! Loaded {len(df)} app records into the DataFrame.\n")

except Exception as e:
    print(f"Error connecting to database: {e}")
    exit()

if df.empty:
    print("The DataFrame is empty. Please check your data source.")
    exit()

# ==========================================
# 2. DATA ANALYSIS & INSIGHT GENERATION
# ==========================================
print("Analyzing dataset based on actual schema...\n")
insights = []

# --- Insight 1: Most Popular App Categories (by total installs) ---
if 'Category' in df.columns and 'Installs' in df.columns:
    df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce').fillna(0)
    top_category = df.groupby('Category')['Installs'].sum().idxmax()
    top_category_installs = df.groupby('Category')['Installs'].sum().max()
    
    insight_1 = f"1. Market Dominance: The '{top_category}' category is the most popular on the market, racking up a total of {int(top_category_installs):,} downloads."
    insights.append(insight_1)

# --- Insight 2: Rating Distribution ---
if 'Rating' in df.columns:
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    avg_rating = df['Rating'].mean()
    median_rating = df['Rating'].median()
    
    insight_2 = f"2. Rating Distribution: The average app rating stands at {avg_rating:.2f}/5.0, with a median of {median_rating:.1f}, indicating user reviews skew heavily positive."
    insights.append(insight_2)

# --- Insight 3: Revenue Streams (In-App Purchases) ---
if 'In-App Purchases' in df.columns:
    iap_counts = df['In-App Purchases'].value_counts(normalize=True)
    iap_pct = (iap_counts.get(True, 0) + iap_counts.get('True', 0)) * 100
    
    insight_3 = f"3. Monetization Depth: Approximately {iap_pct:.1f}% of all applications utilize In-App Purchases, showing how common it is to rely on post-download monetization."
    insights.append(insight_3)

# --- Insight 4: Free vs Paid App Success Comparison ---
if 'Free' in df.columns and 'Rating' in df.columns:
    is_free = df['Free'].astype(str).str.lower() == 'true'
    free_apps = df[is_free]
    paid_apps = df[~is_free]
    
    avg_rating_free = free_apps['Rating'].mean()
    avg_rating_paid = paid_apps['Rating'].mean()
    
    if not paid_apps.empty and pd.notna(avg_rating_paid):
        insight_4 = f"4. Free vs Paid Satisfaction: Paid apps maintain a different average satisfaction rating ({avg_rating_paid:.2f}) compared to Free apps ({avg_rating_free:.2f}), suggesting distinct user expectations between monetization models."
    else:
        insight_4 = f"4. Free vs Paid Satisfaction: The market is overwhelmingly dominated by free offerings, with free applications holding a baseline average user rating of {avg_rating_free:.2f}."
    insights.append(insight_4)

# --- Insight 5: Review Patterns (Correlation) ---
if 'Reviews' in df.columns and 'Rating' in df.columns:
    df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce').fillna(0)
    correlation = df['Reviews'].corr(df['Rating'])
    
    insight_5 = f"5. Engagement Dynamics: The correlation coefficient between review counts and user ratings is {correlation:.2f}, highlighting how volume metrics align with user sentiment."
    insights.append(insight_5)


# ==========================================
# 3. PRINTING INSIGHTS FOR THE DASHBOARD
# ==========================================
print("=== TEXTUAL INSIGHTS FOR DASHBOARD (HAND OVER TO PERSON 4) ===")
print("-" * 65)
for insight in insights:
    print(insight)
print("-" * 65)