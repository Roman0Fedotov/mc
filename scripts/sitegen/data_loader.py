import json
from pathlib import Path

SITE = Path("site")
DATA = SITE / "data"

def _load_json(name: str):
    with open(DATA / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)

def load_all():
    manuscripts = _load_json("manuscripts")
    spells = _load_json("spells")
    categories = _load_json("categories")
    spell_categories = _load_json("spell_categories")

    # --- safety: filter bad rows (prevents KeyError) ---
    manuscripts = [m for m in manuscripts if isinstance(m, dict) and m.get("id") and m.get("title")]
    spells = [s for s in spells if isinstance(s, dict) and s.get("id") and s.get("manuscript_id")]
    categories = [c for c in categories if isinstance(c, dict) and c.get("id") and c.get("name")]
    spell_categories = [
        sc for sc in spell_categories
        if isinstance(sc, dict) and sc.get("spell_id") and sc.get("category_id")
    ]

    # --- UX: sort manuscripts (stable navigation) ---
    manuscripts.sort(key=lambda m: (
        (m.get("title") or "").lower(),
        m.get("id") or "",
    ))

    # --- safety: warn on duplicate manuscript ids ---
    seen = set()
    for ms in manuscripts:
        mid = ms["id"]
        if mid in seen:
            print(f"WARNING: duplicate manuscript id: {mid}")
        seen.add(mid)

    return manuscripts, spells, categories, spell_categories