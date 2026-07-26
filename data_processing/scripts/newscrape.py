from google_play_scraper import search, app
import pandas as pd
import time
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import itertools

# ──────────────────────────────────────────────
# 1. CONFIGURATION
# ──────────────────────────────────────────────
N_HITS_PER_SEARCH = 200          # Lowered slightly to speed up search phase
MAX_WORKERS = 10                 # Increased threads for faster fetching
CHECKPOINT_INTERVAL = 1000       # Save every 1000 apps
CHECKPOINT_FILE = "checkpoint.json"
FINAL_CSV = "google_play_dataset.csv"
MAX_RETRIES = 3
RETRY_DELAY = 2

# ──────────────────────────────────────────────
# 2. KEYWORD PERMUTATION GENERATOR
# ──────────────────────────────────────────────
# This generates 3,000+ unique search terms to find 50,000+ apps
PREFIXES = [
    "best", "top", "free", "offline", "premium", "pro", "lite", "no ads", 
    "for kids", "for adults", "for students", "for beginners", "advanced", 
    "2024", "2025", "popular", "trending", "new", "classic", "indie"
]

ROOTS = [
    "puzzle", "racing", "rpg", "strategy", "shooter", "arcade", "card", "board",
    "fitness", "yoga", "meditation", "cooking", "recipe", "budget", "finance", 
    "crypto", "stock", "news", "weather", "map", "travel", "hotel", "flight", 
    "dating", "chat", "video", "music", "photo", "editor", "scanner", "calculator", 
    "converter", "translator", "dictionary", "learning", "math", "science", "history", 
    "coding", "drawing", "painting", "writing", "reading", "audiobook", "podcast", 
    "radio", "tv", "movie", "anime", "comic", "manga", "shopping", "grocery", 
    "food", "delivery", "taxi", "parking", "car", "bike", "home", "garden", 
    "pet", "dog", "cat", "baby", "pregnancy", "health", "diet", "weight", 
    "sleep", "stress", "anxiety", "therapy", "medical", "first aid", "emergency", 
    "security", "antivirus", "vpn", "backup", "cleaner", "battery", "wifi", 
    "bluetooth", "file", "cloud", "password", "launcher", "wallpaper", "theme", 
    "keyboard", "font", "icon", "widget", "clock", "alarm", "timer", "stopwatch", 
    "calendar", "todo", "note", "reminder", "habit", "goal", "expense", "invoice", 
    "tax", "payroll", "crm", "project", "task", "team", "email", "meeting", 
    "presentation", "document", "spreadsheet", "pdf", "camera", "flashlight", 
    "compass", "level", "ruler", "mirror", "magnifier", "barcode", "qr", "nfc", 
    "remote", "smart", "iot", "robot", "drone", "3d", "ar", "vr", "emulator", "retro"
]

SUFFIXES = [
    "app", "apps", "game", "games", "tool", "tools", "software", "tracker", 
    "manager", "planner", "organizer", "helper", "guide", "tutorial", "lessons", 
    "courses", "training", "workout", "exercise", "simulator", "editor", "maker"
]

def generate_keywords():
    """Generates ~3,000 unique keywords by combining prefixes, roots, and suffixes."""
    keywords = set()
    # 1. Just roots + suffixes (e.g., "puzzle game", "fitness app")
    for root, suffix in itertools.product(ROOTS, SUFFIXES[:3]): 
        keywords.add(f"{root} {suffix}")
    
    # 2. Prefixes + roots + suffixes (e.g., "best puzzle game", "free fitness app")
    for prefix, root, suffix in itertools.product(PREFIXES[:10], ROOTS, SUFFIXES[:2]):
        keywords.add(f"{prefix} {root} {suffix}")
        
    # 3. Specific long-tail phrases
    long_tail = [
        "how to learn", "how to draw", "how to cook", "how to code", 
        "best apps for", "top games for", "free tools for", "offline apps for",
        "apps like", "games like", "alternatives to", "best free", "top paid",
        "no internet", "without wifi", "low end phone", "high graphics",
        "multiplayer online", "single player", "open world", "sandbox",
        "tower defense", "match 3", "endless runner", "battle royale",
        "word search", "crossword", "sudoku", "chess", "checkers",
        "blackjack", "poker", "slots", "bingo", "lottery",
        "coloring book", "paint by number", "pixel art", "vector art",
        "beat maker", "dj mixer", "karaoke", "lyrics finder", "chord finder",
        "step counter", "calorie counter", "water reminder", "fasting timer",
        "period tracker", "ovulation tracker", "pregnancy week by week",
        "baby names", "baby sleep", "toddler games", "preschool learning",
        "math games for kids", "reading games for kids", "science experiments",
        "language exchange", "penpal", "meet new people", "make friends",
        "local events", "things to do", "weekend activities", "hobby ideas"
    ]
    keywords.update(long_tail)
    
    return list(keywords)

# ──────────────────────────────────────────────
# 3. SHARED STATE & CHECKPOINT LOADING
# ──────────────────────────────────────────────
seen_apps = set()
data = []
lock = Lock()
errors = []

# Load checkpoint to KEEP your existing 15,000 apps!
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
        checkpoint = json.load(f)
        seen_apps = set(checkpoint.get("seen_apps", []))
        data = checkpoint.get("data", [])
    print(f"♻️  Loaded existing checkpoint: {len(data)} apps already collected")

def save_checkpoint():
    with lock:
        snapshot = {"seen_apps": list(seen_apps), "data": data}
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f)

def save_csv():
    with lock:
        df = pd.DataFrame(data)
    df.to_csv(FINAL_CSV, index=False, encoding="utf-8")
    print(f"💾 CSV saved — {len(df)} apps")

# ──────────────────────────────────────────────
# 4. HELPER FUNCTIONS
# ─────────────────────────────────────────────
def parse_released_date(released_str: str) -> str | None:
    if not released_str: 
        return None
    formats_to_try = ["%b %d, %Y", "%B %d, %Y", "%Y", "%b %Y", "%B %Y"]
    for fmt in formats_to_try:
        try:
            return datetime.strptime(released_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError: 
            continue
    return released_str

def fetch_app_details(app_id: str) -> dict | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            details = app(app_id, lang="en", country="us")
            updated_ts = details.get("updated")
            updated_date = datetime.fromtimestamp(updated_ts).strftime("%Y-%m-%d") if updated_ts else None
            
            released_raw = details.get("released")
            released_date = parse_released_date(released_raw)

            return {
                "App ID": app_id, 
                "App Name": details.get("title"),
                "Category": details.get("genre"), 
                "Rating": details.get("score"),
                "Reviews": details.get("reviews"), 
                "Installs": details.get("installs"),
                "Size": details.get("size"), 
                "Free": details.get("free"),
                "Price": details.get("price"), 
                "Released": released_date,
                "Last Updated": updated_date, 
                "Developer": details.get("developer"),
                "Content Rating": details.get("contentRating"),
                "Min Android": details.get("androidVersion"),
                "In-App Purchases": details.get("containsAds"),
                "Summary": details.get("summary"), 
                "Description": details.get("description"),
            }
        except Exception as e:
            wait = RETRY_DELAY * attempt
            time.sleep(wait)
    with lock: 
        errors.append(app_id)
    return None

# ──────────────────────────────────────────────
# 5. PHASE 1: MASSIVE KEYWORD SEARCH
# ──────────────────────────────────────────────
def collect_keyword_ids():
    keywords = generate_keywords()
    print(f"🔍 Generated {len(keywords)} unique keywords to search...")
    new_ids = []
    
    for i, keyword in enumerate(keywords, 1):
        try:
            results = search(keyword, lang="en", country="us", n_hits=N_HITS_PER_SEARCH)
            found = 0
            for item in results:
                aid = item.get("appId")
                if aid and aid not in seen_apps:
                    new_ids.append(aid)
                    found += 1
            if found > 0:
                print(f"[KW {i}/{len(keywords)}] '{keyword}' -> {found} new apps")
        except Exception as e:
            print(f"Search failed for '{keyword}': {e}")
        
        # Small delay to prevent IP ban
        if i % 50 == 0:
            print(f"  ⏳ Pausing briefly... ({len(new_ids)} new apps found so far)")
            time.sleep(2)
        else:
            time.sleep(0.3)
            
    return new_ids

# ──────────────────────────────────────────────
# 6. MAIN PIPELINE
# ─────────────────────────────────────────────
def main():
    start_time = time.time()

    print("\n" + "=" * 60)
    print("PHASE 1 — Massive Keyword Search (Targeting 50,000+ apps)")
    print("=" * 60)
    kw_ids = collect_keyword_ids()
    
    all_new_ids = list(set(kw_ids))
    with lock:
        for aid in all_new_ids:
            seen_apps.add(aid)

    print(f"\n🆕 {len(all_new_ids)} total new apps found to fetch details for")
    
    if not all_new_ids:
        print("Nothing new to fetch. Exiting.")
        save_csv()
        return

    print("\n" + "=" * 60)
    print(f"PHASE 2 — Fetching Details ({MAX_WORKERS} threads)")
    print("=" * 60)

    completed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_to_id = {pool.submit(fetch_app_details, aid): aid for aid in all_new_ids}
        for future in as_completed(future_to_id):
            result = future.result()
            if result:
                with lock:
                    data.append(result)
                    completed += 1
                if completed % 200 == 0:
                    print(f"  ✅ Fetched {completed}/{len(all_new_ids)} | Total dataset: {len(data)}")
                if len(data) % CHECKPOINT_INTERVAL == 0:
                    save_checkpoint()
                    print(f"  💾 Checkpoint saved at {len(data)} apps")

    elapsed = time.time() - start_time
    save_checkpoint()
    save_csv()

    print("\n" + "=" * 60)
    print("✅ DONE")
    print(f"  Total apps collected : {len(data)}")
    print(f"  Failed fetches       : {len(errors)}")
    print(f"  Time elapsed         : {elapsed/60:.1f} minutes")
    print("=" * 60)

    if errors:
        with open("failed_apps.txt", "w") as f:
            f.write("\n".join(errors))
        print(f"  Failed IDs saved to failed_apps.txt")

if __name__ == "__main__":
    main()