"""
streamlit_dashboard.py

A professional and elegant Streamlit dashboard for TMDB movie insights, showing top 10 popular movies with year and genre filters.
"""
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------- Page Configuration -----------------
st.set_page_config(
    page_title="TMDB Movie Insights",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- Theme Settings -----------------
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = px.colors.qualitative.Plotly

# ----------------- Data Loading -----------------
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    conn = duckdb.connect("tmdb.duckdb", read_only=True)
    query = """
    SELECT
        m.title,
        m.release_date,
        TRY_CAST(substr(m.release_date,1,4) AS INTEGER) AS release_year,
        m.vote_average,
        m.vote_count,
        m.popularity,
        g.genre_name
    FROM staging_movies m
    LEFT JOIN genre_lookup g USING (genre_id)
    WHERE m.release_date IS NOT NULL
      AND length(trim(m.release_date)) >= 4
      AND substr(m.release_date,1,4) ~ '^[0-9]{4}$'
    """
    df = conn.execute(query).fetchdf()
    df = df.dropna(subset=["title","genre_name","release_year"])
    df["release_year"] = df["release_year"].astype(int)
    return df

# Load data
df = load_data()

# ----------------- Sidebar Filters -----------------
st.sidebar.header("Filter Movies")
min_year, max_year = int(df["release_year"].min()), int(df["release_year"].max())
year_range = st.sidebar.slider("Release Year", min_year, max_year, (min_year, max_year))
genres = sorted(df["genre_name"].unique())
selected_genres = st.sidebar.multiselect("Genre", genres, default=genres)
use_filtered = st.sidebar.toggle("Apply Filters to Top 10 Chart", value=True)
st.sidebar.markdown("---")
st.sidebar.write("Source: TMDB via DuckDB")

# Filtered dataset
filtered = df[
    df["release_year"].between(*year_range) &
    df["genre_name"].isin(selected_genres)
]
dedup = filtered.drop_duplicates(subset=["title","release_date"])

# ----------------- Main Layout -----------------
st.title("TMDB Movie Insights")
st.markdown("Explore trends in votes, popularity, and ratings across movie genres.")

# ----------------- Key Metrics -----------------
total_movies = dedup["title"].nunique()
total_votes = int(dedup["vote_count"].sum())
avg_rating = round(dedup["vote_average"].mean(), 2)
col1, col2, col3 = st.columns(3)
col1.metric(label="Total Movies", value=f"{total_movies:,}")
col2.metric(label="Total Votes", value=f"{total_votes:,}")
col3.metric(label="Average Rating", value=avg_rating)

# ----------------- Prepare Figures -----------------
# 1. Top 10 Popular Movies (toggle filter)
base_df = filtered if use_filtered else df
top_popular = (
    base_df.drop_duplicates(subset=["title","release_date"])
    .sort_values("popularity", ascending=False)
    .head(10)
)
fig1 = px.bar(
    top_popular[::-1],
    x="popularity",
    y="title",
    orientation="h",
    labels={"popularity": "Popularity Score", "title": "Movie Title"},
    title="Top 10 Most Popular Movies" + (" (Filtered)" if use_filtered else " (All Time)"),
    height=450,
)

# 2. Average Rating by Genre
rating_by_genre = (
    filtered.groupby("genre_name")["vote_average"]
    .mean().sort_values(ascending=False).reset_index()
)
fig2 = px.bar(
    rating_by_genre,
    x="vote_average",
    y="genre_name",
    orientation="h",
    labels={"vote_average": "Avg Rating (0–10)", "genre_name": "Genre"},
    height=450
)
fig2.update_layout(yaxis={'categoryorder':'total ascending'})
fig2.update_traces(texttemplate='%{x:.2f}', textposition='outside')

# 3. Yearly Average Ratings
yearly = (
    dedup.groupby("release_year")["vote_average"]
    .mean().reset_index().sort_values("release_year")
)
yearly['rolling'] = yearly['vote_average'].rolling(3, min_periods=1).mean()
fig3 = px.line(
    yearly,
    x="release_year",
    y=["vote_average", "rolling"],
    labels={"value": "Avg Rating (0–10)", "release_year": "Year", "variable": "Series"},
    height=450
)

# 4. Movie Count by Genre
genre_counts = (
    filtered.groupby("genre_name")["title"]
    .count().sort_values().reset_index(name="count")
)
fig4 = px.bar(
    genre_counts,
    x="count",
    y="genre_name",
    orientation="h",
    color="genre_name",
    labels={"count": "Movie Count", "genre_name": "Genre"},
    height=450
)
fig4.update_layout(showlegend=False)

# 5. Top 10 Movies by Vote Count
top_votes = (
    filtered.drop_duplicates(subset=["title","release_date"])
    .sort_values("vote_count", ascending=False)
    .head(10)
)
fig5 = px.bar(
    top_votes[::-1],
    x="vote_count",
    y="title",
    orientation="h",
    labels={"vote_count": "Vote Count", "title": "Movie Title"},
    title="Top 10 Movies by Vote Count",
    height=450
)

# ----------------- Charts in Tabs -----------------
tabs = st.tabs([
    "🔥 Top Popular Movies",
    "⭐ Avg Rating by Genre",
    "📈 Yearly Avg Ratings",
    "🎭 Movie Count by Genre",
    "🗳️ Top Voted Movies",
])
with tabs[0]:
    st.subheader("Top 10 Most Popular Movies" + (" (Filtered)" if use_filtered else " (All Time)"))
    st.plotly_chart(fig1, use_container_width=True)
with tabs[1]:
    st.subheader("Average Rating by Genre")
    st.plotly_chart(fig2, use_container_width=True)
with tabs[2]:
    st.subheader("Yearly Average Ratings")
    st.plotly_chart(fig3, use_container_width=True)
with tabs[3]:
    st.subheader("Movie Count by Genre")
    st.plotly_chart(fig4, use_container_width=True)
with tabs[4]:
    st.subheader("Top 10 Movies by Vote Count")
    st.plotly_chart(fig5, use_container_width=True)

# ----------------- Raw Data -----------------
with st.expander("View Raw Data"):
    st.dataframe(filtered.sort_values("release_date", ascending=False), use_container_width=True)
