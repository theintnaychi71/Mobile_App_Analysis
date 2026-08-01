import pandas as pd
import pymongo
import re

# ----------------------------------------------------
# CSV File Loading (Mac Relative Path)
# ----------------------------------------------------
CSV_FILE = 'data/processed/clean_dataset.csv'

print(f"🔄 Loading '{CSV_FILE}'...")
try:
    df = pd.read_csv(CSV_FILE)
    print(f"✅ Loaded successfully! Total Rows: {len(df)}")
except Exception as e:
    print(f"❌ Error loading CSV: {e}")
    exit()

# ----------------------------------------------------
# Data Transformation & Type Conversion
# ----------------------------------------------------
print("\n🔄 Transforming Data Types for MongoDB...")

# Ensure Installs and Price are numeric
if 'Installs' in df.columns:
    df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce').fillna(0).astype(int)

if 'Price' in df.columns:
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.0)

# Convert Date strings to Datetime Objects for MongoDB Atlas
if 'Released' in df.columns:
    df['Released'] = pd.to_datetime(df['Released'], errors='coerce')

if 'Last Updated' in df.columns:
    df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')

print("✅ Data Transformation Completed!")

# ----------------------------------------------------
# Insert into MongoDB (Cloud Atlas)
# ----------------------------------------------------
print("\n🌐 Connecting to MongoDB Atlas...")

MONGO_URI = "mongodb+srv://data_uploader:A7KQDxaxgMKIbevE@cluster0.cuueyms.mongodb.net/?appName=Cluster0"
DB_NAME = "app_market_db"
COLLECTION_NAME = "apps"

try:
    # Set server selection timeout to prevent hanging if network fails
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Clear previous records before inserting live dataset
    print("🧹 Clearing old collection data...")
    collection.delete_many({})

    # Convert DataFrame to dictionary format
    data_dict = df.to_dict('records')
    
    # Bulk insert into Atlas
    print(f"🚀 Uploading {len(data_dict)} records to Atlas Cloud...")
    result = collection.insert_many(data_dict)

    print("\n" + "="*50)
    print(f"🎉 SUCCESS! Inserted {len(result.inserted_ids)} records into MongoDB Atlas!")
    print(f"📂 Database: {DB_NAME} -> Collection: {COLLECTION_NAME}")
    print("="*50)

except Exception as e:
    print(f"\n❌ MongoDB Error: {e}")