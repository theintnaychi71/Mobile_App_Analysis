import pandas as pd
import pymongo

# ----------------------------------------------------
# CSV File Loading
# ----------------------------------------------------
CSV_FILE = 'google_play_dataset.csv'

print(f" Loading '{CSV_FILE}'...")
try:
    df = pd.read_csv(CSV_FILE)
    print(f" Loaded successfully! Total Rows: {len(df)}")
except Exception as e:
    print(f" Error loading CSV: {e}")
    exit()

# ----------------------------------------------------
# Data Transformation Functions
# ----------------------------------------------------
print("\n Transforming Installs, Price, and Size columns...")

# (A) Installs Column: '1,000,000+' -> 1000000 (Integer)
def clean_installs(val):
    if pd.isna(val):
        return 0
    val_str = str(val).replace(',', '').replace('+', '').strip()
    try:
        return int(val_str)
    except ValueError:
        return 0

# (B) Price Column: '$4.99' or 'Free' -> 4.99 or 0.0 (Float)
def clean_price(val):
    if pd.isna(val) or str(val).lower() == 'free':
        return 0.0
    val_str = str(val).replace('$', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

# (C) Size Column: '15M' -> 15.0, '500k' -> 0.49 (Float in MB)
def clean_size(val):
    if pd.isna(val):
        return None
    val_str = str(val).strip().upper()
    
    if 'M' in val_str:
        try:
            return float(val_str.replace('M', ''))
        except ValueError:
            return None
    elif 'K' in val_str:
        try:
            return round(float(val_str.replace('K', '')) / 1024, 2)
        except ValueError:
            return None
    elif 'G' in val_str:
        try:
            return float(val_str.replace('G', '')) * 1024
        except ValueError:
            return None
    else:
        return None

# Column Clean & Transform 
if 'Installs' in df.columns:
    df['Installs'] = df['Installs'].apply(clean_installs)

if 'Price' in df.columns:
    df['Price'] = df['Price'].apply(clean_price)

if 'Size' in df.columns:
    df['Size'] = df['Size'].apply(clean_size)

print(" Data Transformation Completed!")

# ----------------------------------------------------
# ၃။ Clean Data insert into MongoDB (Cloud Atlas)
# ----------------------------------------------------
print("\n Connecting to MongoDB Atlas...")


MONGO_URI = "mongodb+srv://<USERNAME>:<PASSWORD>@cluster0.cuueyms.mongodb.net/?appName=Cluster0"
DB_NAME = "app_market_db"
COLLECTION_NAME = "apps"

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

   
    collection.delete_many({})

  
    data_dict = df.to_dict('records')
    collection.insert_many(data_dict)

    print(f"\n SUCCESS! Inserted {len(data_dict)} records into MongoDB Atlas ({DB_NAME} -> {COLLECTION_NAME}).")

except Exception as e:
    print(f"\n MongoDB Error: {e}")