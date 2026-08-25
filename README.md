# Mobile App Market Analysis

A full-stack dashboard for exploring mobile-app market data and generating app-success predictions. The application combines a React analytics interface, a Flask REST API, MongoDB data storage, and optional Google Play data-processing scripts.

## Features

- Interactive dashboard for app counts, ratings, installs, pricing, developers, content ratings, and release trends.
- Filters for category, app type (free/paid), and content rating.
- App-success prediction report with score breakdown, benchmarks, risks, opportunities, recommendations, and a printable PDF view.
- MongoDB-backed API with a built-in sample-data fallback when data cannot be read.
- Utilities to scrape, clean, validate, and analyze Google Play Store datasets.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 18, Vite, Tailwind CSS, Recharts, Axios, Lucide |
| Backend | Flask, Flask-CORS, Flask-PyMongo, PyMongo |
| Data | MongoDB, Pandas, NumPy, Google Play Scraper |
| Optional legacy dashboard | Streamlit and Plotly |

## Project structure

```text
DAMProject/
├── api/
│   ├── app.py                 # Flask API and prediction logic
│   ├── requirements.txt       # API Python dependencies
│   └── .env.template          # API environment-variable template
├── frontend/
│   ├── src/
│   │   ├── components/        # Home, dashboard, and prediction views
│   │   └── api/api.js         # Frontend API client
│   └── package.json
├── data/processed/            # Processed CSV datasets
├── data_processing/scripts/   # Scraping and cleaning utilities
├── data_analysis/analysis.py  # Standalone MongoDB analysis script
├── mobile-app-dashboard/      # Legacy Streamlit dashboard
├── google_play.py             # Synthetic dataset generator
└── verify_data.py             # Dataset validation utility
```

## Prerequisites

- Python 3.8 or later
- Node.js 18 or later with npm
- MongoDB Atlas or a compatible MongoDB deployment (recommended for live data)

## Quick start

Run the API and frontend in separate terminals from the repository root.

### 1. Configure and run the API

```powershell
cd api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.template .env
python app.py
```

The API starts on `http://localhost:5001`.

Update `api/.env` with your MongoDB values:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
MONGO_DB=app_market_db
MONGO_COLLECTION=apps
SECRET_KEY=replace-with-a-secret
DEBUG=True
PORT=5001
```

If MongoDB cannot be queried, the API returns its bundled sample data so the interface remains usable. For production, configure a valid `MONGO_URI` and load your collection before starting the API.

### 2. Run the frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`). The frontend is configured to call the API at `http://localhost:5001`.

### 3. Create a production frontend build

```powershell
cd frontend
npm run build
npm run preview
```

## Application routes

| Route | Description |
| --- | --- |
| `/` | Landing page and headline market metrics |
| `/dashboard` | Filterable visual analytics dashboard |
| `/predict` | App-success prediction form and printable report |

## API endpoints

All analytics routes accept optional `category`, `type`, and `content_rating` query parameters where applicable.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | API health and current data source |
| `GET` | `/api/filter-options` | Available categories, types, and content ratings |
| `GET` | `/api/dashboard/stats` | Summary metrics |
| `GET` | `/api/dashboard/summary` | Combined dashboard payload |
| `GET` | `/api/category-analysis` | Category-level aggregates |
| `GET` | `/api/top-apps` | Top apps by a chosen metric |
| `GET` | `/api/top-developers` | Developer leaderboard |
| `GET` | `/api/content-rating-distribution` | Content-rating breakdown |
| `GET` | `/api/rating-distribution` | Rating buckets |
| `GET` | `/api/price-distribution` | Pricing and install distribution |
| `GET` | `/api/release-year-distribution` | Release-year trend |
| `GET` | `/api/insights` | Generated market insights |
| `GET` | `/api/install-distribution` | Install-tier counts |
| `POST` | `/api/predict` | Generate an app-success report |

Example prediction request:

```json
{
  "appName": "FocusFlow",
  "developer": "Example Studio",
  "category": "PRODUCTIVITY",
  "contentRating": "Everyone",
  "rating": 4.3,
  "reviews": 2500,
  "installs": 75000,
  "isFree": true,
  "price": 0
}
```

## Data tools

The data scripts are optional and are run from their relevant folders.

| Script | Purpose |
| --- | --- |
| `data_processing/scripts/scrape.py` | Collect Google Play metadata with `google-play-scraper` |
| `data_processing/scripts/clean_data.py` | Normalize and clean processed app data |
| `verify_data.py` | Validate category, install-tier, and release-year distributions |
| `data_analysis/analysis.py` | Run standalone analysis against the configured MongoDB collection |

Install the additional dependencies required by a particular script before using it, for example:

```powershell
pip install pandas numpy google-play-scraper pymongo python-dotenv
```

## Troubleshooting

| Issue | Resolution |
| --- | --- |
| Frontend shows API errors | Start `python app.py` from `api/` and verify it is listening on port `5001`. |
| MongoDB data is not displayed | Check `MONGO_URI`, `MONGO_DB`, `MONGO_COLLECTION`, network access, and that the collection contains documents. |
| `npm` is not recognized | Install Node.js LTS, then restart the terminal. |
| Python packages fail to install | Activate the project virtual environment and upgrade pip with `python -m pip install --upgrade pip`. |
| Scraper script fails | Google Play may rate-limit requests; wait and retry with a smaller scrape workload. |

## License

This repository is a university fourth-year project. Add an explicit license before redistributing or using it in production.
