import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# ----------------- Setup -----------------
st.set_page_config(
    page_title="🎬 TMDB Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎥 TMDB Movie Insights")
st.markdown("Analyze vote trends, popularity, and ratings across genres.")

# ----------------- DB Connection -----------------

@st.cache_data
def load_data():
    conn = duckdb.connect("tmdb.duckdb", read_only=True)
    query = """
    SELECT 
        m.title,
        m.release_date,
        TRY_CAST(substr(m.release_date, 1, 4) AS INTEGER) AS release_year,
        m.vote_average,
        m.vote_count,
        m.popularity,
        g.genre_name
    FROM staging_movies m
    LEFT JOIN genre_lookup g ON m.genre_id = g.genre_id
    WHERE m.release_date IS NOT NULL
      AND length(trim(m.release_date)) >= 4
      AND substr(m.release_date, 1, 4) ~ '^[0-9]{4}$'
    """
    df = conn.execute(query).fetchdf()
    return df.dropna(subset=["title", "genre_name", "release_year"])

df = load_data()
# ----------------- Sidebar Filters -----------------
min_year = int(df["release_year"].min())
max_year = int(df["release_year"].max())
year_range = st.sidebar.slider("Select Release Year Range", min_year, max_year, (min_year, max_year))

genre_options = df["genre_name"].dropna().unique()
selected_genres = st.sidebar.multiselect("Select Genres", sorted(genre_options), default=sorted(genre_options))

filtered_df = df[
    (df["release_year"].between(*year_range)) &
    (df["genre_name"].isin(selected_genres))
]

# Deduplicated data by title and release date (used only for KPIs and yearly stats)
dedup_df = filtered_df.drop_duplicates(subset=["title", "release_date"])

# ----------------- KPIs -----------------
total_movies = dedup_df["title"].nunique()
total_votes = int(dedup_df["vote_count"].sum())
avg_rating = round(dedup_df["vote_average"].mean(), 2)

col1, col2, col3 = st.columns(3)
col1.metric("🎞️ Total Movies", total_movies)
col2.metric("🗳️ Total Votes", f"{total_votes:,}")
col3.metric("⭐ Average Rating", avg_rating)

# ----------------- Charts -----------------

# 1. Vote Count vs Popularity (Scatter)
st.subheader("📍 Vote Count vs Popularity by Genre")
fig_scatter = px.scatter(
    filtered_df,
    x="vote_count",
    y="popularity",
    color="genre_name",
    hover_name="title",
    title="Vote Count vs Popularity",
    height=500
)
st.plotly_chart(fig_scatter, use_container_width=True)

# 2. Ratings by Genre (Bar)
st.subheader("⭐ Average Rating by Genre")
rating_by_genre = (
    filtered_df.groupby("genre_name")["vote_average"]
    .mean()
    .sort_values()
    .reset_index()
)
fig_rating = px.bar(
    rating_by_genre,
    x="vote_average",
    y="genre_name",
    orientation="h",
    title="Average Rating by Genre",
    height=500
)
st.plotly_chart(fig_rating, use_container_width=True)

# 3. Yearly Ratings (Line) - deduplicated
st.subheader("📈 Yearly Average Ratings (Deduplicated)")
ratings_by_year = (
    dedup_df.groupby("release_year")["vote_average"]
    .mean()
    .reset_index()
    .sort_values("release_year")
)
fig_yearly = px.line(
    ratings_by_year,
    x="release_year",
    y="vote_average",
    title="Average Ratings by Year",
    markers=True,
    height=500
)
st.plotly_chart(fig_yearly, use_container_width=True)

# 4. Genre Movie Count (Bar)
st.subheader("🎭 Movie Count by Genre")
genre_counts = (
    filtered_df.groupby("genre_name")["title"]
    .count()
    .sort_values()
    .reset_index(name="count")
)
fig_genre_count = px.bar(
    genre_counts,
    x="count",
    y="genre_name",
    orientation="h",
    title="Number of Movies per Genre",
    height=500
)
st.plotly_chart(fig_genre_count, use_container_width=True)

# ----------------- Data Table -----------------
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered_df.sort_values("release_date", ascending=False), use_container_width=True)
