from pathlib import Path

# Current file path
current_file = Path(__file__).resolve()
print(f"Current file path: {current_file}")

# Parent directories
print(f"Parent directory: {current_file.parent}")
print(f"Grandparent directory: {current_file.parent.parent}")

# Example constructing paths relative to grandparent
scripts_dir = current_file.parent.parent / "scripts"
dbt_dir = current_file.parent.parent / "dbt_tmdb"

print(f"Scripts directory: {scripts_dir}")
print(f"DBT directory: {dbt_dir}")
