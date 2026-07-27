# 📱 Mobile App Market Analysis and Application Trend Dashboard

> **University Final Year Project**
>
> **Course:** [Enter Your Course Name Here]
>
> **University:** [Enter Your University Name Here]
>
> **Date:** July 2026

---

## 👥 Team Members

| Role | Name | Responsibility |
|------|------|----------------|
| Person 1 | [Team Member 1 Name] | Project Manager |
| Person 2 | [Team Member 2 Name] | Data Collection |
| Person 3 | [Team Member 3 Name] | Data Cleaning & Preprocessing |
| **Person 4 (YOU)** | [Your Name] | **Dashboard Development & Data Visualization** |

---

## 📋 Project Overview

This project analyzes **Google Play Store mobile application data** (approximately 15,000 applications) and builds an **interactive dashboard** that visualizes application market trends. The dashboard helps users understand:

- Most popular app categories in the Play Store
- Average app ratings across different categories
- Which apps receive the most user reviews
- Market share of Free vs Paid applications
- Installation trends over time
- App update patterns

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| **Python 3** | Programming language for all development |
| **Pandas** | Loading and processing the cleaned CSV dataset |
| **Plotly Express** | Creating beautiful, interactive visualizations |
| **Streamlit** | Building the web-based interactive dashboard UI |
| **NumPy** | Supporting numerical calculations |

---

## 📁 Project Folder Structure

```
mobile-app-dashboard/
│
├── 📂 data/
│   └── cleaned_playstore_data.csv   ← Get this from Person 3 (Data Cleaning)
│
├── 📂 assets/                       ← (Optional) Store images/logos here
│
├── 📄 app.py                        ← Main Streamlit Dashboard (Person 4 - YOU!)
├── 📄 requirements.txt              ← List of Python libraries
└── 📄 README.md                     ← This instruction file
```

---

## 🚀 How to Run the Dashboard

Follow these steps **in order** to run the project on your computer.

### Step 1: Install Python
Make sure Python 3.8 or newer is installed on your computer.
- Download from: https://www.python.org/downloads/
- Check by opening Command Prompt / Terminal and typing:
  ```
  python --version
  ```

### Step 2: Get the Cleaned Dataset
1. Ask **Person 3** (Data Cleaning Team Member) for the cleaned CSV file
2. The file should be named: `cleaned_playstore_data.csv`
3. **Copy and paste** this file into the `data/` folder of this project

### Step 3: Install Required Libraries
Open **Command Prompt (Windows)** or **Terminal (Mac/Linux)**, navigate to the project folder, and run:

```bash
cd d:\mobile-app-dashboard
pip install -r requirements.txt
```

*Wait for all libraries to finish installing (this may take 2-5 minutes).*

### Step 4: Run the Dashboard
In the same Command Prompt / Terminal window, run:

```bash
streamlit run app.py
```

A browser window should automatically open showing the dashboard! 🎉

If the browser doesn't open automatically, look for a URL in the terminal like:
```
  Local URL: http://localhost:8501
```
Copy and paste this URL into your web browser (Chrome, Edge, or Firefox).

### Step 5: Stop the Dashboard
To stop the dashboard, go back to the Command Prompt / Terminal and press:
```
Ctrl + C
```

---

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

## 💡 How to Use the Dashboard (Presentation Tips)

1. **Start with the Key Metrics** - Point out the summary cards at the top to give quick statistics
2. **Explain the Sidebar** - Demonstrate how the filters work and show that charts update automatically
3. **Walk through each chart**:
   - What does the chart show?
   - What pattern do you see?
   - Read the insight below the chart
   - Example: "As you can see in the bar chart, Family and Games are the biggest categories..."
4. **Try interactive features**:
   - Hover your mouse over bars/points/lines to see exact values
   - Click the legend to hide/show data series
   - Use the Plotly toolbar (top-right of each chart) to zoom, pan, or download as image
5. **Show the Data Table** - Scroll to the bottom to show the raw filtered data

---

## 📝 Important Notes for Presentation Day

1. ✅ Test the dashboard on the presentation computer **the day before**
2. ✅ Make sure all filters work correctly and all charts load properly
3. ✅ Have your dataset file ready inside the `data/` folder
4. ✅ Have a backup of the whole project on a USB drive (just in case!)
5. ✅ Close other programs during presentation to keep the dashboard fast

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python is not recognized" | Install Python from python.org and restart your computer |
| "pip install fails" | Try using: `pip install --upgrade pip` first, then retry |
| Dashboard says "File not found" | Make sure `cleaned_playstore_data.csv` is inside the `data/` folder |
| Charts are blank | Check if the CSV file has the correct column names (ask Person 3) |
| Dashboard looks slow | Try reducing the data size or close other browser tabs |

---

**Good luck with your presentation!** 🎓✨
