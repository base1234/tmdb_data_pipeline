import requests
import csv
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
GENRE_URL = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=en-US"

def fetch_and_save_genres():
    response = requests.get(GENRE_URL)
    if response.status_code != 200:
        print(f"Failed to fetch genres. Status: {response.status_code}")
        return
    
    genres = response.json().get("genres", [])
    os.makedirs("dbt_tmdb/seeds", exist_ok=True)
    with open("dbt_tmdb/seeds/genres.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["genre_id", "genre_name"])
        for genre in genres:
            writer.writerow([genre["id"], genre["name"]])
    print("Genre seed file created at dbt_tmdb/seeds/genres.csv")

if __name__ == "__main__":
    fetch_and_save_genres()
