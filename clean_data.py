import pandas as pd
import numpy as np
import re

print("🚀 Starting Final Data Cleaning Pipeline (v4 - Missing Date Fix)...")

input_file = "google_play_dataset.csv"
output_file = "clean_dataset.csv"

try:
    df = pd.read_csv(input_file)
    print(f"✅ Loaded {len(df)} rows.")
except FileNotFoundError:
    print(f"❌ Error: Could not find '{input_file}'.")
    exit()

# 1. Remove duplicates
df = df.dropna(subset=["App ID", "App Name"])
df = df.drop_duplicates(subset=["App ID"], keep="first")
print(f"📊 After deduplication: {len(df)} rows")

# 2. Clean Installs
def clean_installs(val):
    if pd.isna(val): return 0
    clean_val = re.sub(r'[^\d]', '', str(val))
    return int(clean_val) if clean_val else 0
df["Installs"] = df["Installs"].apply(clean_installs)

# 3. Clean Price
def clean_price(val):
    if pd.isna(val) or str(val).strip().lower() == "free": return 0.0
    clean_val = str(val).replace("$", "").replace("€", "").strip()
    try: return float(clean_val)
    except ValueError: return 0.0
df["Price"] = df["Price"].apply(clean_price)

# 4. Clean Reviews and Rating
df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce").fillna(0).astype(int)
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0.0)

# 5. Convert Dates
df["Released"] = pd.to_datetime(df["Released"], errors="coerce")
df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce")

# 5.5. HANDLE MISSING DATES (Critical for dashboard)
print("\n" + "="*50)
print("📅 Analyzing Missing Dates...")
print("="*50)

released_missing = df["Released"].isna().sum()
last_updated_missing = df["Last Updated"].isna().sum()
total_rows = len(df)

print(f"  Missing 'Released' dates: {released_missing} ({(released_missing/total_rows)*100:.2f}%)")
print(f"  Missing 'Last Updated' dates: {last_updated_missing} ({(last_updated_missing/total_rows)*100:.2f}%)")

# Strategy: If less than 10% missing, drop those rows. Otherwise, fill with median.
MISSING_THRESHOLD = 10  # percentage

if released_missing > 0:
    released_pct = (released_missing / total_rows) * 100
    if released_pct < MISSING_THRESHOLD:
        print(f"  🗑️  Dropping {released_missing} rows with missing 'Released' (< {MISSING_THRESHOLD}%)")
        df = df.dropna(subset=["Released"])
    else:
        print(f"  📅 Filling {released_missing} missing 'Released' dates with median")
        median_released = df["Released"].median()
        df["Released"] = df["Released"].fillna(median_released)
        df["Released_Was_Missing"] = True
        df.loc[df["Released"].notna() & ~df["Released_Was_Missing"], "Released_Was_Missing"] = False

if last_updated_missing > 0:
    last_updated_pct = (last_updated_missing / total_rows) * 100
    if last_updated_pct < MISSING_THRESHOLD:
        print(f"  🗑️  Dropping {last_updated_missing} rows with missing 'Last Updated' (< {MISSING_THRESHOLD}%)")
        df = df.dropna(subset=["Last Updated"])
    else:
        print(f"  📅 Filling {last_updated_missing} missing 'Last Updated' dates with median")
        median_updated = df["Last Updated"].median()
        df["Last Updated"] = df["Last Updated"].fillna(median_updated)
        df["Last_Updated_Was_Missing"] = True
        df.loc[df["Last Updated"].notna() & ~df["Last_Updated_Was_Missing"], "Last_Updated_Was_Missing"] = False

print(f"  ✅ Dataset after date cleanup: {len(df)} rows")

# 6. Handle Missing Values for other columns
df["Category"] = df["Category"].fillna("Unknown").str.strip()
df["Developer"] = df["Developer"].fillna("Unknown Developer").str.strip()
df["Free"] = df["Free"].fillna(False)
df["In-App Purchases"] = df["In-App Purchases"].fillna(False)

# 7. Feature Engineering
df["App_Age_Days"] = (df["Last Updated"] - df["Released"]).dt.days
df["App_Age_Days"] = df["App_Age_Days"].fillna(0).astype(int)
df.loc[df["App_Age_Days"] < 0, "App_Age_Days"] = 0

def get_price_tier(price):
    if price == 0.0: return "Free"
    elif price < 1.0: return "Under $1"
    elif price < 5.0: return "$1 - $5"
    elif price < 10.0: return "$5 - $10"
    else: return "Over $10"
df["Price_Tier"] = df["Price"].apply(get_price_tier)

def get_popularity_tier(installs):
    if installs < 1000: return "Niche (<1K)"
    elif installs < 100000: return "Growing (1K-100K)"
    elif installs < 1000000: return "Popular (100K-1M)"
    elif installs < 10000000: return "Very Popular (1M-10M)"
    else: return "Mega Hit (10M+)"
df["Popularity_Tier"] = df["Installs"].apply(get_popularity_tier)

# 8. DROP USELESS/EMPTY COLUMNS
columns_to_drop = ["Description", "Summary", "Size", "Min Android", "Content Rating", "Size_MB"]
df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

# 9. Save
df.to_csv(output_file, index=False, encoding="utf-8")

print("\n" + "="*50)
print("✅ DATA CLEANING COMPLETE!")
print(f" Final Dataset: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"💾 Saved to: {output_file}")
print("\n📋 Ready for Dashboard Columns:")
for col in df.columns:
    print(f"  - {col}")
print("="*50)