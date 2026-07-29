import pandas as pd
import pymongo
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==========================================
# 1. DATABASE CONNECTION & DATA LOADING
# ==========================================
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://data_uploader:A7KQDxaxgMKIbevE@cluster0.cuueyms.mongodb.net/?appName=Cluster0")
MONGO_DB = os.getenv("MONGO_DB", "app_market_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "apps")

print("🔌 Connecting to MongoDB Atlas...")
try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    
    data_cursor = collection.find({}, {"_id": 0})
    df = pd.DataFrame(list(data_cursor))
    
    print(f"✅ Success! Loaded {len(df)} app records into the DataFrame.\n")

except pymongo.errors.ServerSelectionTimeoutError:
    print("❌ Error: Could not connect to MongoDB. Please check your MONGO_URI and network connection.")
    exit()
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    exit()

if df.empty:
    print("⚠️ The DataFrame is empty. Please check if data has been uploaded to the database.")
    exit()

# ==========================================
# 1.5. DATA SANITIZATION (NEW & CRITICAL)
# ==========================================
print("🧹 Sanitizing messy data (fixing decimals, booleans, and extra columns)...")

# 1. Define the exact 16 columns we expect
expected_cols = [
    'App ID', 'App Name', 'Category', 'Rating', 'Reviews', 'Installs', 
    'Free', 'Price', 'Released', 'Last Updated', 'Developer', 
    'In-App Purchases', 'Last_Updated_Was_Missing', 'App_Age_Days', 
    'Price_Tier', 'Popularity_Tier'
]

# 2. Keep only expected columns (drops garbage columns from trailing commas)
df = df[[col for col in expected_cols if col in df.columns]]

# 3. Fill missing expected columns with safe defaults
for col in expected_cols:
    if col not in df.columns:
        df[col] = None

# 4. Robust Numeric Cleaning (handles "1,000,000" and "500000000.0")
numeric_cols = ["Rating", "Reviews", "Installs", "Price", "App_Age_Days"]
for col in numeric_cols:
    # Remove commas, then convert to numeric (coerce turns errors into NaN)
    df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.replace('.0', '', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# 5. Robust Boolean Cleaning (handles "TRUE", "False", "true", "FALSE")
bool_cols = ["Free", "In-App Purchases", "Last_Updated_Was_Missing"]
for col in bool_cols:
    df[col] = df[col].astype(str).str.strip().str.upper()
    df[col] = df[col].map({"TRUE": True, "FALSE": False, "NONE": False, "NAN": False}).fillna(False)

print("✅ Data sanitization complete!\n")

# ==========================================
# 2. DATA ANALYSIS & INSIGHT GENERATION
# ==========================================
print("📊 Analyzing dataset based on actual schema...\n")
insights = []

# --- Insight 1: Most Popular App Categories (by total installs) ---
if 'Category' in df.columns and 'Installs' in df.columns:
    category_installs = df.groupby('Category')['Installs'].sum()
    top_category = category_installs.idxmax()
    top_category_installs = category_installs.max()
    
    insight_1 = f"1. Market Dominance: The '{top_category}' category is the most popular on the market, racking up a total of {int(top_category_installs):,} downloads."
    insights.append(insight_1)
else:
    insights.append("1. Market Dominance: Could not calculate (Missing 'Category' or 'Installs' columns).")

# --- Insight 2: Rating Distribution ---
if 'Rating' in df.columns:
    valid_ratings = df['Rating'].dropna()
    valid_ratings = valid_ratings[valid_ratings > 0] # Exclude 0 ratings
    
    if not valid_ratings.empty:
        avg_rating = valid_ratings.mean()
        median_rating = valid_ratings.median()
        insight_2 = f"2. Rating Distribution: The average app rating stands at {avg_rating:.2f}/5.0, with a median of {median_rating:.1f}, indicating user reviews skew heavily positive."
        insights.append(insight_2)
    else:
        insights.append("2. Rating Distribution: No valid rating data found.")
else:
    insights.append("2. Rating Distribution: Could not calculate (Missing 'Rating' column).")

# --- Insight 3: Revenue Streams (In-App Purchases) ---
if 'In-App Purchases' in df.columns:
    iap_pct = df['In-App Purchases'].mean() * 100
    insight_3 = f"3. Monetization Depth: Approximately {iap_pct:.1f}% of all applications utilize In-App Purchases, showing how common it is to rely on post-download monetization."
    insights.append(insight_3)
else:
    insights.append("3. Monetization Depth: Could not calculate (Missing 'In-App Purchases' column).")

# --- Insight 4: Free vs Paid App Success Comparison ---
if 'Free' in df.columns and 'Rating' in df.columns:
    free_apps = df[df['Free'] == True]
    paid_apps = df[df['Free'] == False]
    
    avg_rating_free = free_apps['Rating'].mean() if not free_apps.empty else 0
    avg_rating_paid = paid_apps['Rating'].mean() if not paid_apps.empty else 0
    
    if not paid_apps.empty and pd.notna(avg_rating_paid) and avg_rating_paid > 0:
        insight_4 = f"4. Free vs Paid Satisfaction: Paid apps maintain an average satisfaction rating of {avg_rating_paid:.2f} compared to Free apps at {avg_rating_free:.2f}, suggesting distinct user expectations between monetization models."
    else:
        insight_4 = f"4. Free vs Paid Satisfaction: The market is overwhelmingly dominated by free offerings, with free applications holding a baseline average user rating of {avg_rating_free:.2f}."
    insights.append(insight_4)
else:
    insights.append("4. Free vs Paid Satisfaction: Could not calculate (Missing 'Free' or 'Rating' columns).")

# --- Insight 5: Review Patterns (Correlation) ---
if 'Reviews' in df.columns and 'Rating' in df.columns:
    valid_corr_df = df[['Reviews', 'Rating']].dropna()
    valid_corr_df = valid_corr_df[valid_corr_df['Reviews'] > 0] # Exclude 0 reviews
    
    if len(valid_corr_df) > 1:
        correlation = valid_corr_df['Reviews'].corr(valid_corr_df['Rating'])
        insight_5 = f"5. Engagement Dynamics: The correlation coefficient between review counts and user ratings is {correlation:.2f}, highlighting how volume metrics align with user sentiment."
        insights.append(insight_5)
    else:
        insights.append("5. Engagement Dynamics: Insufficient valid data to calculate correlation between reviews and ratings.")
else:
    insights.append("5. Engagement Dynamics: Could not calculate (Missing 'Reviews' or 'Rating' columns).")


# ==========================================
# 3. PRINTING INSIGHTS FOR THE DASHBOARD
# ==========================================
print("=" * 75)
print("=== 📝 TEXTUAL INSIGHTS FOR DASHBOARD (HAND OVER TO PERSON 4) ===")
print("=" * 75)
for insight in insights:
    print(insight)
print("=" * 75)
print("\n💡 Tip: Person 4 can copy these insights directly into the Streamlit dashboard markdown components.")