import json
import os
from pathlib import Path

DEFAULT_TEXTS_DIR = Path("private-data") / "texts"


def _clean(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def get_texts_dir() -> Path:
    return Path(os.environ.get("PRIVATE_TEXTS_DIR", str(DEFAULT_TEXTS_DIR))).resolve()


def load_spell_texts(texts_dir=None) -> dict:
    texts_dir = texts_dir or get_texts_dir()

    if not texts_dir.exists():
        print(f"INFO: private texts directory not found: {texts_dir}")
        return {}

    result = {}

    for path in sorted(texts_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        spell_id = _clean(data.get("spell_id")) or path.stem

        if not spell_id:
            print(f"WARNING: skipped text JSON without spell_id: {path}")
            continue

        if spell_id in result:
            print(f"WARNING: duplicate text JSON for spell_id={spell_id}: {path}")
            continue

        result[spell_id] = data

    print(f"INFO: loaded {len(result)} private text JSON files from {texts_dir}")
    return result