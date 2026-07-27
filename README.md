# 📱 Mobile App Market Analysis & Trend Dashboard

An interactive, data-driven dashboard analyzing trends across 25,000+ Google Play Store applications. This project transforms raw, scraped mobile app data into actionable business insights, highlighting market share, user engagement patterns, and category performance.

---

## 📋 Project Overview

The Google Play Store contains millions of applications, making it difficult to identify market trends manually. This project addresses that by:
1. **Scraping** live, up-to-date app data directly from the Play Store.
2. **Cleaning & Preprocessing** the data to handle missing values, standardize formats (e.g., converting "1,000,000+" to integers), and engineer new features (e.g., App Age, Price Tiers).
3. **Visualizing** the data through an interactive web dashboard to answer key questions:
   - Which app categories dominate the market in total downloads?
   - Is there a correlation between app ratings and the number of reviews?
   - What is the market share of Free vs. Paid applications?
   - How have app release and update trends evolved over time?

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core programming language |
| **Pandas & NumPy** | Data manipulation, cleaning, and feature engineering |
| **Plotly Express** | Creating responsive, interactive, and publication-ready visualizations |
| **Streamlit** | Rapid development of the web-based dashboard UI |
| **Google Play Scraper** | Extracting live application metadata |

---
## 🚀 How to Run This Project

Follow these step-by-step instructions to set up and run the dashboard on your local machine.

### Prerequisites
- **Python 3.8 or higher** installed on your system.
- **Git** installed (if cloning the repository).

### Step 1: Clone the Repository
Open your terminal or command prompt and clone the project:
```bash
git clone https://github.com/theintnaychi71/Mobile_App_Analysis.git
cd Mobile_App_Analysis
```

### Step 2: Install Required Libraries
Install all dependencies:
```bash
pip install pandas numpy plotly streamlit flask pymongo google-play-scraper
```

Installed Packages Explanation
| Package             | Purpose                           |
| ------------------- | --------------------------------- |
| pandas              | Data processing and analysis      |
| numpy               | Numerical computation             |
| plotly              | Interactive data visualization    |
| streamlit           | Dashboard user interface          |
| flask               | Backend API services              |
| pymongo             | MongoDB connection                |
| google-play-scraper | Google Play Store data collection |


### Step 3: Run the Dashboard
In the same Command Prompt / Terminal window, run:

```bash
streamlit run app.py
```
or
```bash
python -m streamlit run app.py
```
A browser window should automatically open showing the dashboard! 🎉

If the browser doesn't open automatically, look for a URL in the terminal like:
```
  Local URL: http://localhost:8501
```
Copy and paste this URL into your web browser (Chrome, Edge, or Firefox).

### Step 4: Stop the Dashboard
To stop the dashboard, go back to the Command Prompt / Terminal and press:
```
Ctrl + C
```

## 🎯 Dashboard Features

### Sidebar Filters
1. **Category Filter** - Select which app categories to display
2. **Rating Range Slider** - Filter apps by minimum and maximum rating
3. **Free/Paid Filter** - Show all apps, only free, or only paid apps

### Visualizations
1. 📊 **App Category Distribution** - Bar chart (how many apps per category)
2. 📶 **Rating Distribution** - Histogram (how ratings spread across 1-5 stars)
3. 🏆 **Top Apps by Reviews** - Horizontal bar chart (top 10 most reviewed apps)
4. 🍩 **Free vs Paid Apps** - Donut pie chart (percentage of free vs paid)
5. 📈 **Installation Trend** - Line chart (how installs change over time)

Each visualization also includes **1-2 sentences of business insights** below it.

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python is not recognized" | Install Python from python.org and restart your computer |
| "pip install fails" | Try using: `pip install --upgrade pip` first, then retry |
| ModuleNotFoundError | Ensure you ran the pip install command and that your terminal is in the correct project directory. |
| Dashboard says "File not found" | Make sure `cleaned_playstore_data.csv` is inside the `data/` folder |
| Charts are blank | Check if the CSV file has the correct column names |
| Dashboard looks slow | Try reducing the data size or close other browser tabs |

---