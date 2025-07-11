import json
import glob

files = glob.glob("data/raw/movies_popular_*.json")

if not files:
    raise FileNotFoundError("No matching files found in data/raw/. Please check the path and filename pattern.")
for file in files:
    with open("data/raw/movies_popular_20250624_171409.json", "r") as f:
        content = f.read()
        data = json.loads(content)
        print(data.keys())
