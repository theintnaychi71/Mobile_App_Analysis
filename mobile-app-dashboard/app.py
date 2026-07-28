# ============================================================
# Mobile App Market Analysis Dashboard
# University Final Year Project
# Person 4: Dashboard Development & Data Visualization
# ============================================================

# ============================================================
# SECTION 1: Import Required Libraries
# ============================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import pymongo
import os
from dotenv import load_dotenv

def format_number(num):
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return str(num)

# ============================================================
# SECTION 2: Basic Page Configuration
# ============================================================
st.set_page_config(
    page_title="Mobile App Market Analysis Dashboard",
    page_icon="",
    layout="wide"
)

# ============================================================
# SECTION 3: Helper Function to Load Data (UPDATED FOR MONGODB)
# ============================================================
@st.cache_data(ttl=3600)  # Caches data for 1 hour to prevent slow reloading
def load_data():
    """
    Load and preprocess the dataset DIRECTLY from MongoDB Atlas.
    """
    load_dotenv()
    
    # Fetch credentials (fallback to hardcoded URI only for local dev safety)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://data_uploader:A7KQDxaxgMKIbevE@cluster0.cuueyms.mongodb.net/?appName=Cluster0")
    MONGO_DB = os.getenv("MONGO_DB", "app_market_db")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "apps")
    
    try:
        # Connect to MongoDB with a 5-second timeout
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Verify connection works
        
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        # Fetch all documents, excluding the '_id' field
        data_cursor = collection.find({}, {"_id": 0})
        df = pd.DataFrame(list(data_cursor))
        
        if df.empty:
            st.error("❌ MongoDB collection is empty. Please check your database.")
            st.stop()
            
        
        
    except pymongo.errors.ServerSelectionTimeoutError:
        st.error("❌ Could not connect to MongoDB. Please check your MONGO_URI and network connection.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error connecting to MongoDB: {e}")
        st.stop()

    # --- Preprocessing (Same as your original logic) ---
    numeric_cols = ["Rating", "Reviews", "Installs", "Price", "App_Age_Days"]
    for col in numeric_cols:
        if col in df.columns:
            # Handle comma-separated strings (e.g., "1,000,000") before converting
            if col in ["Installs", "Reviews"]:
                df[col] = df[col].astype(str).str.replace(',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Boolean conversions (TRUE/FALSE strings -> bool)
    bool_cols = ["Free", "In-App Purchases", "Last_Updated_Was_Missing"]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper().map({"TRUE": True, "FALSE": False}).fillna(False)

    # Date conversions
    if "Released" in df.columns:
        df["Released"] = pd.to_datetime(df["Released"], errors="coerce", format="mixed", dayfirst=False)
    if "Last Updated" in df.columns:
        df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce", format="mixed", dayfirst=False)
        # Derived column for trend chart: Last Updated truncated to month
        df["Last_Updated_Month"] = df["Last Updated"].dt.to_period("M").dt.to_timestamp()

    return df

# Load the data
df = load_data()

# ============================================================
# SECTION 4: Dashboard Title & Project Description
# ============================================================
st.title("📱 Mobile App Market Analysis Dashboard")
st.markdown("""
Welcome to our Mobile App Market Analysis Dashboard! 


""")
st.markdown("---")

# ============================================================
# SECTION 5: Sidebar Filters
# ============================================================
st.sidebar.header("🔍 Data Filters")
st.sidebar.info("Customize all dashboard views using these filters.")

# --- Filter 1: Category Multi-Select ---
all_categories_sorted = sorted(df["Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    " Select App Categories",
    options=all_categories_sorted,
    default=all_categories_sorted,
    help="Choose one or more categories. Leave empty to see all."
)
if not selected_categories:
    selected_categories = all_categories_sorted

# --- Filter 2: Rating Range Slider (FIXED TO INCLUDE UNRATED APPS) ---
# Set min to 0.0 to include unrated apps (Rating = 0 or NaN)
min_rating_raw = 0.0
max_rating_raw = float(df["Rating"].max()) if "Rating" in df.columns and not df["Rating"].empty else 5.0

rating_range = st.sidebar.slider(
    "⭐ Rating Range",
    min_value=min_rating_raw,
    max_value=max_rating_raw,
    value=(min_rating_raw, max_rating_raw),
    step=0.1,
    help="Filter apps within this rating band (0.0 includes unrated apps)."
)

# --- Filter 3: Free / Paid Radio Buttons ---
free_paid_choice = st.sidebar.radio(
    "💰 Pricing Model",
    options=["All Apps", "Free Only", "Paid Only"],
    help="Show all apps, only free apps, or only paid apps."
)

# --- Apply Filters ---
filtered_df = df.copy()
filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]

# Only apply rating filter if user manually adjusted it away from the default (0.0 to max)
if rating_range[1] < max_rating_raw or rating_range[0] > 0.0:
    filtered_df = filtered_df[
        (filtered_df["Rating"] >= rating_range[0]) & (filtered_df["Rating"] <= rating_range[1])
    ]

if free_paid_choice == "Free Only":
    filtered_df = filtered_df[filtered_df["Free"] == True]
elif free_paid_choice == "Paid Only":
    filtered_df = filtered_df[filtered_df["Free"] == False]

# Safety: if filters wipe the dataset, fall back to full dataset
if filtered_df.empty:
    st.sidebar.warning("⚠️ Filters produced no data. Showing all data instead.")
    filtered_df = df.copy()

# ============================================================
# SECTION 6: Key Metrics (Summary Cards)
# ============================================================
st.subheader("📊 Key Metrics")
m1, m2, m3, m4 = st.columns(4)

total_apps = len(filtered_df)
_rated = filtered_df[filtered_df["Rating"] > 0]["Rating"]
avg_rating = _rated.mean() if len(_rated) > 0 else 0
total_reviews = filtered_df["Reviews"].sum()
total_installs = filtered_df["Installs"].sum()

m1.metric(
    label="📦 Total Apps",
    value=f"{total_apps:,}",
    delta=f"{len(selected_categories)} categories"
)
m2.metric(
    label="⭐ Avg Rating",
    value=f"{avg_rating:.2f} / 5.0" if avg_rating else "N/A",
    delta=f"Min {rating_range[0]:.1f} – Max {rating_range[1]:.1f}"
)
m3.metric(
    label="💬 Total Reviews",
    value=f"{total_reviews:,.0f}"
)
m4.metric(
    label=" Total Installs",
   value=format_number(total_installs)
)
st.markdown("---")

# ============================================================
# SECTION 7: Visualization Row 1
# ============================================================
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.subheader(" App Category Distribution")

    cat_counts = (
        filtered_df["Category"]
        .value_counts()
        .reset_index()
    )

    cat_counts.columns = ["Category", "Count"]

    cat_counts = (
        cat_counts
        .sort_values("Count", ascending=True)
        .tail(20)
    )

    fig_cat = px.bar(
        cat_counts,
        x="Count",
        y="Category",
        orientation="h",
        color="Count",
        color_continuous_scale="Blues",
        title="Top 20 Categories by Number of Apps",
        text="Count",
        labels={
            "Count": "Number of Apps",
            "Category": "App Category"
        }
    )

    fig_cat.update_layout(
        height=600,
        showlegend=False,
        coloraxis_showscale=False
    )

    fig_cat.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    st.plotly_chart(
    fig_cat,
    use_container_width=True,
    key="category_distribution_chart"
)

    st.markdown("---")

    # Insight based on Person 5 analysis
    if not filtered_df.empty:
        category_install = (
            filtered_df.groupby("Category")["Installs"]
            .sum()
            .sort_values(ascending=False)
        )

        top_install_cat = category_install.index[0]
        top_install_value = category_install.iloc[0]

        st.markdown(
            f"""
💡 **Insight:** **{top_install_cat}** category dominates the market 
with **{top_install_value:,.0f} total installs**, 
showing the highest user adoption among all application categories.
"""
        )

with row1_col2:
    st.subheader("⭐ Rating Distribution")

    ratings_valid = filtered_df["Rating"].dropna()
    ratings_valid = ratings_valid[ratings_valid > 0]

    fig_rating = px.histogram(
        ratings_valid,
        x="Rating",
        nbins=20,
        title="Distribution of App Ratings",
        color_discrete_sequence=["#1f77b4"],
        labels={
            "Rating": "User Rating (0–5 Stars)",
            "count": "Number of Apps"
        },
        marginal="box"
    )

    fig_rating.update_layout(bargap=0.05)
    fig_rating.update_xaxes(range=[-0.1, 5.1])

    st.plotly_chart(
        fig_rating,
        use_container_width=True,
        key="rating_distribution_chart"
    )

    st.markdown("---")

    if len(ratings_valid) > 0:
        mean_r = ratings_valid.mean()
        median_r = ratings_valid.median()

        st.markdown(
            f"""
💡 **Insight:** The average app rating is **{mean_r:.2f}/5.0**
with a median rating of **{median_r:.1f}**.

This shows that user ratings are generally positive.
"""
        )


# ============================================================
# SECTION 8: Visualization Row 2
# ============================================================
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("🏆 Top Apps by Number of Reviews")

    top_reviews = (
        filtered_df.sort_values("Reviews", ascending=False)
        .head(10)[["App Name", "Reviews", "Category", "Rating", "Installs"]]
        .sort_values("Reviews", ascending=True)
    )

    fig_reviews = px.bar(
        top_reviews,
        x="Reviews",
        y="App Name",
        orientation="h",
        color="Category",
        title="Top 10 Most Reviewed Apps",
        hover_data=["Rating", "Installs"],
        text="Reviews",
        labels={
            "Reviews": "Number of Reviews",
            "App Name": "Application"
        }
    )

    fig_reviews.update_layout(
        height=550,
        legend_title="Category"
    )

    fig_reviews.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False
    )

    st.plotly_chart(
        fig_reviews,
        use_container_width=True,
        key="top_reviews_chart"
    )

    st.markdown("---")

    # Insight
    if not top_reviews.empty:
        top_app = top_reviews.iloc[-1]

        st.markdown(
            f"""
💡 **Insight:** The most-reviewed app is 
**{top_app['App Name']}** ({top_app['Category']}) 
with **{top_app['Reviews']:,.0f} reviews**.

This shows that highly engaged applications receive
more user feedback and market attention.
"""
        )


with row2_col2:
    st.subheader("💰 Free vs Paid Applications")
    fp_df = filtered_df.copy()
    fp_df["Type"] = fp_df["Free"].map({True: "Free", False: "Paid"}).fillna("Free")
    fp_counts = fp_df["Type"].value_counts().reset_index()
    fp_counts.columns = ["Type", "App Count"]
    fp_installs = (
        fp_df.groupby("Type")["Installs"]
        .sum()
        .reset_index()
        .rename(columns={"Installs": "Total Installs"})
    )
    fp_merged = fp_counts.merge(fp_installs, on="Type")

    fig_fp = px.pie(
        fp_merged,
        names="Type",
        values="App Count",
        hole=0.5,
        title="App Count Share: Free vs Paid",
        color="Type",
        color_discrete_map={"Free": "#2ecc71", "Paid": "#e74c3c"},
       hover_data=["Total Installs"]
    )
    fig_fp.update_traces(textinfo="percent+label", pull=[0.02, 0.05])
    fig_fp.update_layout(legend_title="App Pricing Type")
    st.plotly_chart(fig_fp, use_container_width=True)
    st.markdown("---")

    # Insight
    if len(fp_merged) > 0:
        n_free = int(fp_merged.loc[fp_merged["Type"] == "Free", "App Count"].sum()) if "Free" in fp_merged["Type"].values else 0
        n_paid = int(fp_merged.loc[fp_merged["Type"] == "Paid", "App Count"].sum()) if "Paid" in fp_merged["Type"].values else 0
        pct_free = (n_free / (n_free + n_paid) * 100) if (n_free + n_paid) else 0
        pct_paid = 100 - pct_free
        inst_free = float(fp_merged.loc[fp_merged["Type"] == "Free", "Total Installs"].sum()) if "Free" in fp_merged["Type"].values else 0
        inst_paid = float(fp_merged.loc[fp_merged["Type"] == "Paid", "Total Installs"].sum()) if "Paid" in fp_merged["Type"].values else 0
        pct_inst_free = (inst_free / (inst_free + inst_paid) * 100) if (inst_free + inst_paid) else 0
        st.markdown(
            f"💡 **Insight:** **{pct_free:.1f}%** of apps are free ({n_free:,}) vs "
            f"**{pct_paid:.1f}%** paid ({n_paid:,}). Yet free apps account for "
            f"**{pct_inst_free:.1f}% of all installs**, confirming the freemium model dominates — "
            f"users overwhelmingly prefer no-upfront-cost apps."
        )

# ============================================================
# SECTION 9: Visualization Row 3 (Full Width) - APP RELEASE TRENDS
# ============================================================
st.subheader("📈 App Market Growth Over Time")

# Try to use "Released" date. If it's mostly empty, fallback to "Last Updated" to ensure the chart works.
date_col = "Released" if "Released" in filtered_df.columns and filtered_df["Released"].notna().sum() > 100 else "Last Updated"
date_label = "Release Year" if date_col == "Released" else "Last Updated Year"

release_df = filtered_df.dropna(subset=[date_col]).copy()

if not release_df.empty:
    # Extract the year from the date column
    release_df["Year"] = release_df[date_col].dt.year
    
    # Filter out unrealistic years (e.g., typos like 1970 or future dates)
    release_df = release_df[(release_df["Year"] >= 2008) & (release_df["Year"] <= 2026)]
    
    # Count the number of apps per year
    release_yearly = (
        release_df.groupby("Year")
        .size()
        .reset_index(name="Number of Apps")
        .sort_values("Year")
    )

    fig_release = px.bar(
        release_yearly,
        x="Year",
        y="Number of Apps",
        title=f"Number of Apps {date_label} (Market Growth)",
        labels={"Year": "Year", "Number of Apps": "Number of Apps Published"},
        color="Number of Apps",
        color_continuous_scale="Viridis",
        text="Number of Apps"
    )
    
    fig_release.update_layout(height=550, xaxis=dict(dtick=1, showgrid=True))
    fig_release.update_traces(texttemplate="%{text:,}", textposition="outside")
    
    st.plotly_chart(fig_release, use_container_width=True)
    st.markdown("---")

    # Insight Generation
    if len(release_yearly) > 0:
        peak_year = release_yearly.loc[release_yearly["Number of Apps"].idxmax()]
        latest_year = int(release_yearly["Year"].max())
        
        # Calculate recent trend (compare last 2 available years)
        recent_data = release_yearly[release_yearly["Year"] >= latest_year - 1]
        trend_text = ""
        if len(recent_data) >= 2:
            if recent_data.iloc[-1]["Number of Apps"] > recent_data.iloc[0]["Number of Apps"]:
                trend_text = "an **upward trend** 📈"
            else:
                trend_text = "a **slight decline or stabilization** "
        
        st.markdown(
            f"💡 **Insight:** The peak year for app publishing was **{int(peak_year['Year'])}** "
            f"with **{peak_year['Number of Apps']:,} apps** released. "
            f"Recent data shows {trend_text}, indicating how the market has evolved from a 'gold rush' era "
            f"to a more mature, competitive landscape."
        )
else:
    st.warning("️ No valid date data available to generate the release trend chart.")
    st.markdown("---")

# ============================================================
# SECTION 9B: Bonus Visualization Row 4 (Tabs)
# ============================================================
st.subheader("🎁 Bonus Deep-Dive Charts")
tab_pt, tab_rc, tab_pc = st.tabs([
    "💸 Price Tier Distribution",
    " Avg Rating per Category",
    "🔥 Popularity Tier by Category"
])

# --- Tab 1: Price Tier Distribution ---
with tab_pt:
    pt_order = ["Free", "Under $1", "$1 - $5", "$5 - $10", "Over $10"]
    pt_counts = filtered_df["Price_Tier"].value_counts().reset_index()
    pt_counts.columns = ["Price_Tier", "App Count"]
    pt_counts["Sort_Order"] = pt_counts["Price_Tier"].apply(
        lambda x: pt_order.index(x) if x in pt_order else 99
    )
    pt_counts = pt_counts.sort_values("Sort_Order").drop(columns="Sort_Order")

    fig_pt = px.bar(
        pt_counts,
        x="Price_Tier",
        y="App Count",
        color="Price_Tier",
        text="App Count",
        title="Distribution of Apps by Price Tier",
        labels={"Price_Tier": "Price Tier", "App Count": "Number of Apps"},
        color_discrete_map={
            "Free": "#2ecc71", "Under $1": "#3498db",
            "$1 - $5": "#9b59b6", "$5 - $10": "#e67e22", "Over $10": "#e74c3c"
        }
    )
    fig_pt.update_layout(showlegend=False, height=500)
    fig_pt.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig_pt, use_container_width=True)

    # Insight
    if not pt_counts.empty:
        paid_total = pt_counts.loc[pt_counts["Price_Tier"] != "Free", "App Count"].sum()
        mid_tier = pt_counts.loc[pt_counts["Price_Tier"].isin(["$1 - $5"]), "App Count"].sum() if "$1 - $5" in pt_counts["Price_Tier"].values else 0
        paid_pct_mid = (mid_tier / paid_total * 100) if paid_total else 0
        st.markdown(
            f" **Insight:** {pt_counts.iloc[0]['Price_Tier']} apps are the largest bucket "
            f"with **{pt_counts.iloc[0]['App Count']:,}**. Among paid apps ({paid_total:,} total), "
            f"the **$1–$5 sweet-spot tier captures {paid_pct_mid:.1f}%**, suggesting low-to-mid price points "
            f"are the most common monetization strategy. Premium tiers (Over $10) remain niche."
        )

# --- Tab 2: Average Rating per Category ---
with tab_rc:
    rating_cat = (
        filtered_df.groupby("Category")["Rating"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Avg Rating", "count": "App Count"})
        .sort_values("Avg Rating", ascending=True)
        .tail(15)
    )
    fig_rc = px.bar(
        rating_cat,
        x="Avg Rating",
        y="Category",
        orientation="h",
        color="Avg Rating",
        color_continuous_scale="RdYlGn",
        range_color=[2.5, 5.0],
        text="Avg Rating",
        hover_data={"App Count": True, "Avg Rating": ":,.2f"},
        title="Top 15 Categories by Average User Rating",
        labels={"Avg Rating": "Mean Rating (0–5)", "Category": "App Category"}
    )
    fig_rc.update_layout(height=600, coloraxis_showscale=True)
    fig_rc.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_rc, use_container_width=True)

    # Insight
    if not rating_cat.empty:
        best = rating_cat.iloc[-1]
        worst = rating_cat.iloc[0]
        st.markdown(
            f"💡 **Insight:** Users rate **{best['Category']}** highest at "
            f"**{best['Avg Rating']:.2f}** stars ({best['App Count']} apps sampled). "
            f"At the lower end of the Top 15, **{worst['Category']}** still holds "
            f"a respectable **{worst['Avg Rating']:.2f}** stars. A high rating doesn't always "
            f"match a large category — small niche categories often outperform the mass-market ones."
        )

# --- Tab 3: Popularity Tier by Category ---
with tab_pc:
    pop_order = ["Niche (<1K)", "Growing (1K-100K)", "Popular (100K-1M)", "Very Popular (1M-10M)", "Mega Hit (10M+)"]
    # Limit to Top 15 categories (by total app count) for readability
    top_cats_pop = filtered_df["Category"].value_counts().head(15).index.tolist()
    pop_df = filtered_df[filtered_df["Category"].isin(top_cats_pop)].copy()
    pop_ct = (
        pop_df.groupby(["Category", "Popularity_Tier"])
        .size()
        .reset_index(name="App Count")
    )
    fig_pc = px.bar(
        pop_ct,
        x="Category",
        y="App Count",
        color="Popularity_Tier",
        color_discrete_sequence=["#95a5a6", "#3498db", "#2ecc71", "#f39c12", "#e74c3c"],
        category_orders={"Popularity_Tier": pop_order},
        title="Popularity Mix across Top 15 Categories (Stacked)",
        labels={"Category": "App Category", "App Count": "Apps", "Popularity_Tier": "Popularity Tier"},
        text_auto=True
    )
    fig_pc.update_layout(height=600, xaxis_tickangle=-45, barmode="stack", legend_title="Popularity Tier")
    st.plotly_chart(fig_pc, use_container_width=True)

    # Insight
    if not pop_ct.empty:
        cat_pct = (
            pop_df.groupby(["Category", "Popularity_Tier"]).size()
            / pop_df.groupby("Category").size() * 100
        ).reset_index(name="Pct")
        big_hits = cat_pct[cat_pct["Popularity_Tier"].isin(["Mega Hit (10M+)", "Very Popular (1M-10M)"])]
        if not big_hits.empty:
            best_mega = big_hits.groupby("Category")["Pct"].sum().idxmax()
            best_mega_pct = big_hits.groupby("Category")["Pct"].sum().max()
            st.markdown(
                f"💡 **Insight:** Among Top 15 categories, **{best_mega}** has the highest share "
                f"of heavy-hitters (Very Popular + Mega Hit combined) at **{best_mega_pct:.1f}%**. "
                f"Most categories skew heavily toward the 'Growing' and 'Popular' tiers, "
                f"confirming that true breakaway apps remain rare regardless of category."
            )
st.markdown("---")

# ============================================================
# SECTION 10: Filtered Data Preview Table
# ============================================================
st.markdown("---")
st.subheader("📋 Filtered Data Preview")

preview_df = filtered_df.copy()
# Format columns nicely for display
display_cols = [
    "App Name", "Category", "Rating", "Reviews", "Installs",
    "Free", "Price", "Released", "Last Updated", "Developer",
    "In-App Purchases", "App_Age_Days", "Price_Tier", "Popularity_Tier"
]
# Only include columns that exist
display_cols = [c for c in display_cols if c in preview_df.columns]

# Show row count and a toggle for showing all columns
show_all_cols = st.checkbox(
    "Show all columns (includes App ID and data-cleaning flags)",
    value=False
)
cols_to_show = list(preview_df.columns) if show_all_cols else display_cols
view_df = preview_df[cols_to_show].head(500).reset_index(drop=True)

st.caption(
    f"Showing rows 1–{min(len(view_df), 500):,} of **{len(filtered_df):,}** total "
    f"({len(cols_to_show)} columns). Click column headers to sort."
)
st.dataframe(view_df, use_container_width=True, hide_index=True)

# ============================================================
# SECTION 11: Footer
# ============================================================
st.markdown("---")
st.caption("🎓 University Fourth Year Project | Mobile App Market Analysis Dashboard | 2026")