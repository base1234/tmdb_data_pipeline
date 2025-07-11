import json
import glob
import os

input_files = glob.glob("data/raw/*.json")
output_dir = "data/flattened"
os.makedirs(output_dir, exist_ok=True)

for path in input_files:
    with open(path, 'r') as f:
        data = json.load(f)
        results = data.get("results", [])
    
    filename = os.path.basename(path)
    out_path = os.path.join(output_dir, f"flattened_{filename}")
    
    with open(out_path, 'w') as out:
        for record in results:
            out.write(json.dumps(record) + "\n")

print(f"Flattened {len(input_files)} file(s) to {output_dir}")
