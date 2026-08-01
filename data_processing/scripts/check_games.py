import pymongo

MONGO_URI = "mongodb+srv://data_uploader:A7KQDxaxgMKIbevE@cluster0.cuueyms.mongodb.net/?appName=Cluster0"
client = pymongo.MongoClient(MONGO_URI)
db = client["app_market_db"]
col = db["apps"]

# Game Genres List
game_genres = [
    'Action', 'Adventure', 'Arcade', 'Board', 'Card', 'Casino', 
    'Casual', 'Educational', 'Music', 'Puzzle', 'Racing', 
    'Role Playing', 'Simulation', 'Sports', 'Strategy', 'Trivia', 'Word'
]

print("="*50)
print("🔍 CATEGORY MATCHING CHECK")
print("="*50)

# 1. Check each genre individually
total_games = 0
for genre in game_genres:
    count = col.count_documents({"Category": genre})
    if count > 0:
        print(f"  • {genre}: {count} apps")
        total_games += count

print("-" * 50)
print(f"🎮 Total Combined Game Apps: {total_games}")
print("="*50)