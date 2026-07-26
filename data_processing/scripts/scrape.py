from google_play_scraper import search, app
import pandas as pd
import time
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# ──────────────────────────────────────────────
# 1. CONFIGURATION
# ──────────────────────────────────────────────
N_HITS_PER_SEARCH = 300          
MAX_WORKERS = 8                  
CHECKPOINT_INTERVAL = 500        
CHECKPOINT_FILE = "checkpoint.json"
FINAL_CSV = "google_play_dataset.csv"
MAX_RETRIES = 3
RETRY_DELAY = 2

# ──────────────────────────────────────────────
# 2. HARDCODED CATEGORIES & COLLECTIONS
# ──────────────────────────────────────────────
CATEGORIES = [
    "GAME", "FAMILY", "BUSINESS", "FINANCE", "LIFESTYLE", "TOOLS",
    "MEDICAL", "SPORTS", "PERSONALIZATION", "PRODUCTIVITY", "COMMUNICATION",
    "WEATHER", "SOCIAL", "PHOTOGRAPHY", "NEWS_AND_MAGAZINES", "MAPS_AND_NAVIGATION",
    "SHOPPING", "TRAVEL_AND_LOCAL", "BOOKS_AND_REFERENCE", "EDUCATION",
    "ENTERTAINMENT", "MUSIC_AND_AUDIO", "VIDEO_PLAYERS", "FOOD_AND_DRINK",
    "HEALTH_AND_FITNESS", "AUTO_AND_VEHICLES", "LIBRARIES_AND_DEMO",
    "DATING", "COMICS", "EVENTS", "ART_AND_DESIGN", "PARENTING",
    "HOUSE_AND_HOME", "BEAUTY"
]

COLLECTIONS = [
    "topselling_free",
    "topselling_paid", 
    "topgrossing",
    "topselling_new_free",
    "topselling_new_paid"
]

# ──────────────────────────────────────────────
# 3. SHARED STATE & CHECKPOINT LOADING
# ──────────────────────────────────────────────
seen_apps = set()
data = []
lock = Lock()
errors = []

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
# 5. PHASE 1: KEYWORD SEARCH
# ──────────────────────────────────────────────
keywords = [
    "puzzle game", "racing game", "strategy game", "rpg game", "shooter game",
    "learn english", "learn math", "science quiz", "flashcards", "language learning",
    "stock tracker", "crypto wallet", "budget planner", "tax calculator", "invoice maker",
    "calorie counter", "step counter", "yoga for beginners", "meditation guide", "sleep tracker",
    "to do list", "note taking", "calendar planner", "pdf reader", "document scanner",
    "grocery list", "coupon finder", "price comparison", "food delivery", "restaurant finder",
    "messaging app", "video calling", "dating app", "photo sharing", "live streaming",
    "flight tracker", "hotel booking", "map offline", "gps navigation", "public transit",
    "vpn app", "antivirus", "battery saver", "wifi analyzer", "remote desktop",
    "music player", "podcast app", "radio streaming", "audiobook", "video editor",
    "horoscope", "tarot reading", "dream journal", "gratitude journal", "mood tracker",
    "metal detector", "spirit level", "decibel meter", "lux meter", "magnifying glass",
    "barcode scanner", "qr code reader", "file manager", "cloud storage", "password manager",
    "workout planner", "running tracker", "cycling app", "weight loss", "fasting timer",
    "recipe app", "meal planner", "nutrition tracker", "diet planner", "cooking guide",
    "news reader", "sports news", "weather forecast", "traffic updates", "local news",
    "online shopping", "fashion app", "electronics store", "grocery delivery", "deal finder",
    "banking app", "payment app", "money transfer", "bill payment", "investment app",
    "taxi app", "ride sharing", "car rental", "bike rental", "parking app",
    "movie streaming", "tv shows", "anime streaming", "documentary app", "kids videos",
    "ebook reader", "comic reader", "manga reader", "pdf editor", "word processor",
    "language translator", "dictionary app", "thesaurus", "grammar checker", "spell checker",
    "voice recorder", "audio editor", "sound effects", "ringtone maker", "music maker",
    "photo collage", "image editor", "selfie camera", "beauty camera", "photo filters",
    "video maker", "video cutter", "gif maker", "meme generator", "sticker maker",
    "fitness tracker", "gym workout", "home workout", "stretching app", "pilates app",
    "baby tracker", "pregnancy app", "period tracker", "fertility tracker", "health monitor",
    "mental health", "therapy app", "counseling app", "stress relief", "anxiety help",
    "sleep sounds", "white noise", "nature sounds", "relaxation app", "breathing exercise",
    "habit tracker", "goal tracker", "motivation app", "self improvement", "productivity timer",
    "expense tracker", "budget app", "savings goal", "debt tracker", "financial planner",
    "stock market", "crypto tracker", "forex trading", "commodity prices", "market news",
    "business news", "tech news", "science news", "world news", "breaking news",
    "social media", "photo sharing", "video sharing", "blogging app", "microblogging",
    "chat app", "group chat", "video chat", "voice call", "conference call",
    "email app", "calendar app", "reminder app", "alarm clock", "world clock",
    "unit converter", "currency converter", "calculator", "scientific calculator", "graphing calculator",
    "flashlight app", "compass app", "level tool", "ruler app", "protractor app",
    "qr scanner", "barcode scanner", "document scanner", "business card scanner", "receipt scanner",
    "backup app", "file transfer", "phone cleaner", "cache cleaner", "junk cleaner",
    "app locker", "photo vault", "video vault", "private browser", "incognito browser",
    "dns changer", "ip scanner", "network tools", "ping tool", "speed test",
    "bluetooth finder", "wifi password", "hotspot app", "tethering app", "internet booster",
    "screen recorder", "screenshot app", "screen capture", "video screenshot", "game recorder",
    "launcher app", "icon pack", "widget app", "wallpaper app", "live wallpaper",
    "font changer", "keyboard app", "emoji keyboard", "gifs keyboard", "theme app",
    "voice changer", "sound booster", "bass booster", "equalizer app", "volume booster",
    "battery saver", "battery optimizer", "charging alarm", "battery widget", "power saving",
    "ram booster", "cpu monitor", "storage analyzer", "disk usage", "memory cleaner",
    "antivirus app", "security app", "malware scanner", "virus remover", "privacy guard",
    "vpn free", "proxy app", "tor browser", "dark web", "anonymous browser",
    "ad blocker", "popup blocker", "tracker blocker", "privacy browser", "secure browser",
    "parental control", "kids mode", "screen time", "app timer", "digital wellbeing",
    "focus mode", "do not disturb", "night mode", "blue light filter", "eye care",
    "reading mode", "text to speech", "speech to text", "voice typing", "dictation app",
    "note taking", "sticky notes", "checklist app", "shopping list", "todo list",
    "project management", "team collaboration", "task assignment", "kanban board", "scrum app",
    "time tracking", "timesheet app", "work hours", "overtime tracker", "freelance tracker",
    "invoice generator", "billing app", "receipt maker", "quote generator", "estimate app",
    "accounting software", "bookkeeping app", "tax preparation", "gst calculator", "vat calculator",
    "payroll app", "salary calculator", "employee management", "attendance tracker", "leave management",
    "crm app", "sales tracker", "lead generator", "customer support", "helpdesk app",
    "inventory management", "stock control", "warehouse app", "supply chain", "logistics app",
    "delivery tracker", "order tracking", "package tracker", "shipment app", "courier tracker",
    "restaurant app", "food ordering", "table booking", "menu app", "recipe finder",
    "nutrition info", "calorie tracker", "macro tracker", "water tracker", "hydration reminder",
    "vitamin tracker", "supplement tracker", "allergy tracker", "symptom tracker", "pain tracker",
    "blood pressure", "heart rate", "blood sugar", "glucose tracker", "diabetes app",
    "cholesterol tracker", "weight tracker", "bmi calculator", "body fat", "muscle mass",
    "step counter", "pedometer app", "distance tracker", "calorie burn", "activity tracker",
    "sleep analysis", "sleep quality", "sleep cycle", "smart alarm", "wake up light",
    "dream journal", "lucid dreaming", "meditation timer", "mindfulness app", "zen app",
    "yoga poses", "yoga timer", "stretching routine", "flexibility app", "mobility app",
    "strength training", "weight lifting", "cardio workout", "hiit workout", "interval timer",
    "running app", "jogging app", "marathon training", "5k training", "10k training",
    "cycling tracker", "bike computer", "route planner", "elevation tracker", "speed tracker",
    "swimming app", "lap counter", "stroke counter", "pool timer", "open water swim",
    "hiking app", "trail map", "camping app", "fishing app", "hunting app",
    "golf app", "golf tracker", "swing analyzer", "putt tracker", "handicap tracker",
    "tennis app", "badminton app", "cricket app", "football app", "basketball app",
    "soccer app", "baseball app", "volleyball app", "rugby app", "hockey app",
    "boxing app", "mma app", "wrestling app", "martial arts", "self defense",
    "dance app", "choreography app", "music lessons", "guitar lessons", "piano lessons",
    "singing lessons", "voice lessons", "drum lessons", "violin lessons", "flute lessons",
    "art lessons", "drawing lessons", "painting app", "sketching app", "digital art",
    "photography lessons", "camera settings", "exposure calculator", "depth of field", "focal length",
    "video lessons", "filmmaking app", "editing tutorials", "color grading", "sound design",
    "writing app", "story writer", "novel writer", "poetry app", "journal app",
    "blog writer", "content writer", "copywriting app", "seo tools", "keyword research",
    "grammar check", "plagiarism check", "citation generator", "reference manager", "bibliography app",
    "study app", "exam prep", "test prep", "practice test", "quiz app",
    "flashcard app", "memory game", "brain training", "puzzle app", "logic game",
    "math game", "science game", "history game", "geography game", "trivia game",
    "word game", "spelling game", "vocabulary game", "language game", "typing game",
    "coding game", "programming app", "algorithm visualizer", "data structures", "computer science",
    "web development", "app development", "game development", "software testing", "debugging app",
    "version control", "git client", "code editor", "ide app", "compiler app",
    "database app", "sql client", "api tester", "rest client", "graphql client",
    "server monitor", "uptime tracker", "performance monitor", "log viewer", "error tracker",
    "analytics app", "metrics tracker", "dashboard app", "reporting tool", "data visualization",
    "chart maker", "graph maker", "diagram app", "flowchart app", "mind mapping",
    "brainstorming app", "idea organizer", "concept map", "outline app", "structure app",
    "presentation app", "slide maker", "pitch deck", "portfolio app", "resume builder",
    "cv maker", "cover letter", "job search", "career app", "interview prep",
    "salary negotiation", "networking app", "linkedin alternative", "professional network", "business card",
    "meeting scheduler", "appointment app", "booking system", "reservation app", "queue management",
    "ticket booking", "event booking", "concert tickets", "movie tickets", "sports tickets",
    "theater tickets", "museum tickets", "attraction tickets", "tour booking", "guide booking",
    "language tutor", "math tutor", "science tutor", "english tutor", "homework help",
    "online class", "video lecture", "course platform", "learning management", "student portal",
    "teacher app", "classroom app", "grade book", "attendance app", "lesson planner",
    "curriculum app", "educational games", "kids learning", "preschool app", "kindergarten app",
    "elementary app", "middle school", "high school", "college app", "university app",
    "graduate school", "phd app", "research app", "academic writing", "thesis writer",
    "dissertation app", "literature review", "research paper", "journal article", "conference paper",
    "grant writing", "funding app", "scholarship app", "student loan", "financial aid",
    "tuition planner", "education savings", "529 plan", "student budget", "college budget",
    "roommate finder", "housing app", "apartment search", "rental app", "lease tracker",
    "utility bill", "internet bill", "phone bill", "cable bill", "subscription tracker",
    "membership app", "loyalty program", "rewards app", "cashback app", "coupon app",
    "deal alert", "price drop", "sale alert", "black friday", "cyber monday",
    "gift card", "digital wallet", "mobile payment", "contactless payment", "nfc payment",
    "cryptocurrency", "bitcoin wallet", "ethereum wallet", "defi app", "nft marketplace",
    "blockchain app", "smart contract", "crypto exchange", "trading bot", "portfolio tracker",
    "investment tracker", "retirement planner", "401k tracker", "ira tracker", "pension app",
    "social security", "medicare app", "insurance app", "health insurance", "life insurance",
    "car insurance", "home insurance", "travel insurance", "pet insurance", "claim tracker",
    "legal app", "lawyer finder", "legal advice", "contract review", "document signing",
    "notary app", "witness app", "court dates", "case tracker", "legal research",
    "government app", "tax filing", "voter registration", "census app", "benefits app",
    "disability app", "unemployment app", "welfare app", "food stamps", "housing assistance",
    "childcare app", "babysitter finder", "nanny finder", "daycare app", "preschool finder",
    "elder care", "senior care", "assisted living", "nursing home", "hospice care",
    "veterinary app", "pet health", "pet insurance", "pet sitter", "dog walker",
    "pet training", "pet grooming", "pet adoption", "animal shelter", "wildlife app",
    "bird watching", "plant identifier", "garden planner", "lawn care", "pest control",
    "home repair", "plumbing app", "electrical app", "hvac app", "roofing app",
    "painting app", "flooring app", "tiling app", "carpentry app", "landscaping app",
    "interior design", "exterior design", "architecture app", "3d modeling", "cad app",
    "measurement app", "blueprint app", "renovation app", "remodeling app", "construction app",
    "project estimator", "material calculator", "cost estimator", "bid calculator", "contractor app",
    "supplier finder", "vendor app", "wholesale app", "retail app", "ecommerce app",
    "dropshipping app", "fulfillment app", "shipping app", "packaging app", "label maker",
    "barcode generator", "qr generator", "inventory scanner", "pos system", "cash register",
    "receipt printer", "invoice printer", "label printer", "barcode printer", "ticket printer",
    "badge maker", "id card maker", "certificate maker", "award maker", "trophy app",
    "medal tracker", "achievement app", "goal setting", "vision board", "dream board",
    "manifestation app", "affirmation app", "gratitude app", "journaling app", "diary app",
    "memoir app", "autobiography", "biography app", "genealogy app", "family tree",
    "ancestor search", "dna test", "heritage app", "culture app", "tradition app",
    "religion app", "spirituality app", "philosophy app", "ethics app", "morality app",
    "psychology app", "sociology app", "anthropology app", "archaeology app", "history app",
    "geography app", "geology app", "meteorology app", "astronomy app", "astrophysics app",
    "chemistry app", "physics app", "biology app", "botany app", "zoology app",
    "ecology app", "environmental app", "climate app", "weather app", "forecast app",
    "radar app", "satellite app", "map app", "navigation app", "gps app",
    "compass app", "altimeter app", "barometer app", "thermometer app", "hygrometer app",
    "anemometer app", "seismometer app", "volcano app", "earthquake app", "tsunami app",
    "disaster app", "emergency app", "first aid", "cpr app", "aed locator",
    "hospital finder", "clinic finder", "pharmacy finder", "doctor finder", "dentist finder",
    "specialist finder", "surgeon finder", "therapist finder", "counselor finder", "psychiatrist finder",
    "nutritionist finder", "dietitian finder", "trainer finder", "coach finder", "instructor finder",
    "tutor finder", "teacher finder", "professor finder", "lecturer finder", "speaker finder",
    "entertainer finder", "musician finder", "artist finder", "actor finder", "director finder",
    "producer finder", "writer finder", "editor finder", "publisher finder", "agent finder",
    "manager finder", "consultant finder", "advisor finder", "mentor finder", "coach finder",
    "life coach", "business coach", "executive coach", "career coach", "health coach",
    "fitness coach", "nutrition coach", "wellness coach", "mindset coach", "performance coach",
    "sales coach", "marketing coach", "leadership coach", "team coach", "communication coach",
    "relationship coach", "dating coach", "marriage coach", "parenting coach", "family coach",
    "financial coach", "money coach", "debt coach", "budget coach", "investment coach",
    "retirement coach", "estate coach", "tax coach", "insurance coach", "legal coach",
    "immigration coach", "visa coach", "passport coach", "travel coach", "relocation coach",
    "expat coach", "cultural coach", "language coach", "accent coach", "pronunciation coach",
    "public speaking", "presentation coach", "speech coach", "voice coach", "acting coach",
    "singing coach", "instrument coach", "dance coach", "sports coach", "golf coach",
    "tennis coach", "swim coach", "run coach", "cycle coach", "triathlon coach",
    "marathon coach", "ultra coach", "mountaineering", "climbing coach", "skiing coach",
    "snowboard coach", "surfing coach", "diving coach", "fishing coach", "hunting coach",
    "shooting coach", "archery coach", "boxing coach", "mma coach", "wrestling coach",
    "martial arts coach", "self defense coach", "fitness trainer", "personal trainer", "group trainer",
    "online trainer", "virtual trainer", "ai trainer", "smart trainer", "adaptive trainer",
    "customized trainer", "specialized trainer", "expert trainer", "certified trainer", "professional trainer"
]

def collect_keyword_ids():
    new_ids = []
    print(f"🔍 Searching {len(keywords)} keywords...")
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
        time.sleep(0.5)
    return new_ids

# ──────────────────────────────────────────────
# 6. PHASE 2: CATEGORY SCRAPING (Simplified)
# ──────────────────────────────────────────────
def collect_category_ids():
    """
    Skip category scraping for now - just use keywords.
    The keyword search with 500+ terms will give us 15,000+ apps.
    """
    print("⏭️  Skipping category charts (keywords will provide enough data)")
    return []

# ──────────────────────────────────────────────
# 7. MAIN PIPELINE
# ─────────────────────────────────────────────
def main():
    start_time = time.time()

    print("\n" + "=" * 60)
    print("PHASE 1 — Keyword Search")
    print("=" * 60)
    kw_ids = collect_keyword_ids()
    
    all_new_ids = list(set(kw_ids))
    with lock:
        for aid in all_new_ids:
            seen_apps.add(aid)

    print(f"\n {len(all_new_ids)} total new apps to fetch details for")
    
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
                if completed % 100 == 0:
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