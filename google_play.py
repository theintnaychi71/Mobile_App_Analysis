import pandas as pd

input_file = r'D:\MobileAppAnalysis\data\processed\clean_dataset.csv' # Change to your current file name
output_file = r'D:\MobileAppAnalysis\data\processed\cleaned_2021_dataset.csv'

print("🔄 Loading dataset...")
df = pd.read_csv(input_file, low_memory=False, on_bad_lines='skip')

# ==========================================
# 1. FIX DATA TYPES (Crucial to prevent crashes)
# ==========================================
print("🧹 Fixing data types...")
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce').fillna(0).astype(int)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce').fillna(0).astype(int)
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(0.0)

# ==========================================
# 2. SEPARATE 2021 FROM OTHER YEARS
# ==========================================
df['Released'] = pd.to_datetime(df['Released'], format='mixed', errors='coerce')
df['Release_Year'] = df['Released'].dt.year

# Split the data
df_2021 = df[df['Release_Year'] == 2021].copy()
df_others = df[df['Release_Year'] != 2021].copy()

print(f"\n📊 Before filtering:")
print(f"  2021 Apps: {len(df_2021):,}")
print(f"  Other Years: {len(df_others):,}")

# ==========================================
# 3. DELETE UNPOPULAR 2021 APPS
# ==========================================
print("\n🗑️ Deleting unpopular 2021 apps...")
print("   (Keeping only apps with >= 1,000,000 Installs AND >= 10,000 Reviews)")

# 👇 CHANGE THESE NUMBERS TO ADJUST HOW STRICT THE FILTER IS 👇
MIN_INSTALLS = 1000000   # 1 Million installs
MIN_REVIEWS = 10000      # 10,000 reviews

# Keep ONLY the popular ones
df_2021_popular = df_2021[
    (df_2021['Installs'] >= MIN_INSTALLS) & 
    (df_2021['Reviews'] >= MIN_REVIEWS)
]

deleted_count = len(df_2021) - len(df_2021_popular)
print(f"    Deleted {deleted_count:,} unpopular apps from 2021.")
print(f"   ✅ Kept {len(df_2021_popular):,} popular apps for 2021.")

# ==========================================
# 4. COMBINE AND SAVE
# ==========================================
final_df = pd.concat([df_others, df_2021_popular], ignore_index=True)

# Drop the temporary helper column
if 'Release_Year' in final_df.columns:
    final_df = final_df.drop(columns=['Release_Year'])

# Save the new file
final_df.to_csv(output_file, index=False)

print("\n" + "="*60)
print(f"✅ SUCCESS! Saved cleaned dataset to '{output_file}'")
print(f"📦 Total apps in final dataset: {len(final_df):,}")
print("="*60)