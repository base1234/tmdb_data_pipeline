import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/movie/popular"
OUTPUT_DIR = "data/raw"
NUM_PAGES = 100

def fetch_popular_movies():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Delete old JSON files before fetching new data
    for file in os.listdir(OUTPUT_DIR):
        if file.endswith(".json"):
            os.remove(os.path.join(OUTPUT_DIR, file))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{OUTPUT_DIR}/movies_popular_{timestamp}.json"

    all_movies = []

    for page in range(1, NUM_PAGES + 1):
        url = f"{BASE_URL}?api_key={API_KEY}&language=en-US&page={page}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            all_movies.extend(results)
            print(f"Fetched page {page}, movies: {len(results)}")
        else:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")
            break

    with open(output_file, "w") as f:
        json.dump({"results": all_movies}, f, indent=2)

    print(f"Saved {len(all_movies)} movies to {output_file}")

if __name__ == "__main__":
    fetch_popular_movies()
