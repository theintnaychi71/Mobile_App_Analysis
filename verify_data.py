import pandas as pd

# ──────────────────────────────────────────────
# File Path (Update this if your file is named differently)
# ──────────────────────────────────────────────
input_file = '6k_data.csv'

print("🔄 Loading dataset for verification...")
try:
    df = pd.read_csv(input_file)
    print(f"✅ Successfully loaded {len(df)} rows.\n")
except FileNotFoundError:
    print(f"❌ Error: Could not find '{input_file}'. Please check the file path.")
    exit()

print("📊 Verification of Real-World Constraints:")
print("-" * 50)

# 1. Top Categories
print("Top Categories:")
print(df['Category'].value_counts())
print()

# 2. Popularity Tier Distribution
print("Popularity Tier Distribution:")
print(df['Popularity_Tier'].value_counts())
print()

# 3. Release Year Ranking
print("Release Year Ranking:")
# Extract the year from the 'Released' column
df['Year'] = pd.to_datetime(df['Released'], errors='coerce').dt.year
print(df['Year'].value_counts().sort_index(ascending=False))

print("-" * 50)
print("✅ Verification Complete!")