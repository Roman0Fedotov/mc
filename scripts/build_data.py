import csv
import json
from pathlib import Path

DATA_DIR = Path("data")
OUT_DIR = Path("site/data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TABLES = ["manuscripts", "spells", "categories", "spell_categories"]

def detect_delimiter(sample: str) -> str:
    semicolons = sample.count(";")
    commas = sample.count(",")
    return ";" if semicolons >= commas else ","

def csv_to_json(name: str) -> None:
    csv_path = DATA_DIR / f"{name}.csv"
    json_path = OUT_DIR / f"{name}.json"

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)

        delimiter = detect_delimiter(sample)
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"✔ {name}.json created (delimiter='{delimiter}')")

for t in TABLES:
    csv_to_json(t)