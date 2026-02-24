import csv
import json
from pathlib import Path

# откуда берём CSV
DATA_DIR = Path("data")

# куда кладём JSON для сайта
OUT_DIR = Path("site/data")

# создаём папку, если её нет
OUT_DIR.mkdir(parents=True, exist_ok=True)

def csv_to_json(name):
    """
    Преобразует data/name.csv → site/data/name.json
    """
    csv_path = DATA_DIR / f"{name}.csv"
    json_path = OUT_DIR / f"{name}.json"

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"✔ {name}.json created")

# список таблиц (строго по именам файлов)
tables = [
    "manuscripts",
    "spells",
    "categories",
    "spell_categories"
]

for table in tables:
    csv_to_json(table)