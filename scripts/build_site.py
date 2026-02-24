import json
from pathlib import Path
import os

BASE_PATH = os.environ.get("BASE_PATH", "").strip()
if BASE_PATH:
    BASE_PATH = "/" + BASE_PATH.strip("/")
else:
    BASE_PATH = ""
SITE = Path("site")
DATA = SITE / "data"
TEMPLATES = Path("templates")

def root(path: str) -> str:
    return f"{BASE_PATH}{path}"

def load(name):
    return (TEMPLATES / name).read_text(encoding="utf-8")

def render(title, content):
    base = load("base.html")
    html = (
        base
        .replace("{{ title }}", title)
        .replace("{{ content }}", content)
    )
    return html.replace("{{ base_path }}", BASE_PATH)

# 1. загружаем рукописи
with open(DATA / "manuscripts.json", encoding="utf-8") as f:
    manuscripts = json.load(f)
    manuscripts = [
    ms for ms in manuscripts
    if ms.get("id") and ms.get("title")
]
# словарь: id → рукопись
manuscript_by_id = {
    ms["id"]: ms
    for ms in manuscripts
}
with open(DATA / "spells.json", encoding="utf-8") as f:
    spells = json.load(f)

with open(DATA / "categories.json", encoding="utf-8") as f:
    categories = json.load(f)

with open(DATA / "spell_categories.json", encoding="utf-8") as f:
    spell_categories = json.load(f)

# --- count spells per category ---
spell_count_by_category = {}

for sc in spell_categories:
    cid = sc.get("category_id")
    if not cid:
        continue
    spell_count_by_category[cid] = spell_count_by_category.get(cid, 0) + 1
    
category_by_id = {
    c["id"]: c
    for c in categories
}

children_by_parent = {}

for c in categories:
    parent = c.get("parent_id")
    children_by_parent.setdefault(parent, []).append(c)

from functools import lru_cache

def category_ancestors(cat_id):
    chain = []
    current = category_by_id.get(cat_id)

    while current:
        chain.append(current)
        pid = current.get("parent_id")
        current = category_by_id.get(pid)

    return list(reversed(chain))

@lru_cache(None)
def total_spell_count(cat_id):
    # прямые заклинания в этой категории
    total = spell_count_by_category.get(cat_id, 0)

    # заклинания во всех подкатегориях
    for child in children_by_parent.get(cat_id, []):
        total += total_spell_count(child["id"])

    return total

# 2. делаем список <li>
items = []
for ms in manuscripts:
    ms_href = root(f"/manuscripts/{ms['id']}.html")
    items.append(
        f"<li>"
        f'<a href="{ms_href}">{ms.get("title","")}</a>'
        f' ({ms.get("date","")}, {ms.get("location","")})'
        f"</li>"
    )

content = "<ul>\n" + "\n".join(items) + "\n</ul>"

# 3. подставляем в шаблон
inner = load("index.html").replace(
    "{{ manuscripts }}",
    "\n".join(items)
)

# 4. заворачиваем в base
html = render("Manuscript Corpus", inner)

# 5. сохраняем
(SITE / "index.html").write_text(html, encoding="utf-8")

# ---------- manuscript pages ----------

MANUSCRIPT_DIR = SITE / "manuscripts"
MANUSCRIPT_DIR.mkdir(exist_ok=True)

manuscript_template = load("manuscript.html")

for ms in manuscripts:

    # --- breadcrumbs for manuscript ---
    breadcrumbs = (
        '<nav class="breadcrumbs">'
        f'<a href="{root("/index.html")}">Home</a>'
        f' &#8594; {ms.get("title","")}'
        '</nav>'
    )
    # 7.6 — заклинания этой рукописи
    related_spells = [
        sp for sp in spells
        if sp.get("manuscript_id") == ms["id"]
    ]

    if related_spells:
        spells_list = "<ul>" + "".join(
            f'<li><a href="../spells/{sp["id"]}.html">'
            f'{sp.get("title_en","")}</a> ({sp.get("page","")})</li>'
            for sp in related_spells
        ) + "</ul>"
    else:
        spells_list = "<p>No spells recorded.</p>"

    inner = (
        manuscript_template
        .replace("{{ breadcrumbs }}", breadcrumbs)
        .replace("{{ title }}", ms.get("title", ""))
        .replace("{{ siglum }}", ms.get("siglum", ""))
        .replace("{{ location }}", ms.get("location", ""))
        .replace("{{ date }}", ms.get("date", ""))
        .replace("{{ format }}", ms.get("format", ""))
        .replace("{{ n_texts }}", ms.get("N of texts", ""))
        .replace("{{ bibliography }}", ms.get("bibliography", ""))
        .replace("{{ spells }}", spells_list)
    )

    html = render(ms.get("title", "Manuscript"), inner)

    out = MANUSCRIPT_DIR / f'{ms["id"]}.html'
    out.write_text(html, encoding="utf-8")

# ---------- spells ----------

spell_template = load("spell.html")

SPELL_DIR = SITE / "spells"
SPELL_DIR.mkdir(exist_ok=True)

for sp in spells:
    ms = manuscript_by_id.get(sp.get("manuscript_id"), {})

    cat_ids = [
        sc["category_id"]
        for sc in spell_categories
        if sc["spell_id"] == sp["id"]
    ]

    # --- breadcrumbs for spell ---
    breadcrumbs = (
        '<nav class="breadcrumbs">'
        f'<a href="{root("/index.html")}">Home</a> &#8594; '
        f'<a href="{root("/categories/index.html")}">Categories</a>'
    )

# берём категории этого заклинания
    if cat_ids:
        main_cat = category_by_id.get(cat_ids[0])
        if main_cat:
            ancestors = category_ancestors(main_cat["id"])
            for c in ancestors:
                breadcrumbs += f' &#8594; <a href="../categories/{c["id"]}.html">{c["name"]}</a>'

    breadcrumbs += f' &#8594; {sp.get("title_en","")}'
    breadcrumbs += '</nav>'

    if cat_ids:
        categories_html = "<ul>" + "".join(
        f'<li><a href="../categories/{cid}.html">'
        f'{category_by_id[cid]["name"]}</a></li>'
        for cid in cat_ids
    ) + "</ul>"
    else:
        categories_html = "<p>No categories assigned.</p>"

    inner = (
        spell_template
        .replace("{{ breadcrumbs }}", breadcrumbs)
        .replace("{{ title_english }}", sp.get("title_en", ""))
        .replace("{{ translation }}", sp.get("translation", ""))
        .replace("{{ title_syriac }}", sp.get("title_syr", ""))
        .replace("{{ manuscript_id }}", sp.get("manuscript_id", ""))
        .replace("{{ manuscript_siglum }}", ms.get("siglum", ""))
        .replace("{{ page }}", sp.get("page", ""))
        .replace("{{ scribe }}", sp.get("scribe", ""))
        .replace("{{ categories }}", categories_html)
    )

    html = render(sp.get("title_en", "Spell"), inner)

    (SPELL_DIR / f"{sp['id']}.html").write_text(html, encoding="utf-8")

    # ---------- categories ----------

CATEGORY_DIR = SITE / "categories"
CATEGORY_DIR.mkdir(exist_ok=True)

category_template = load("category.html")

for cat in categories:
    cat_id = cat["id"]
    
    count = total_spell_count(cat_id)

# --- breadcrumbs ---
    ancestors = category_ancestors(cat_id)

    breadcrumbs = (
        '<nav class="breadcrumbs">'
        f'<a href="{root("/index.html")}">Home</a> &#8594; '
        f'<a href="{root("/categories/index.html")}">Categories</a>'
    )

    for c in ancestors[:-1]:
        breadcrumbs += f' &#8594; <a href="{c["id"]}.html">{c["name"]}</a>'

    breadcrumbs += f' &#8594; {ancestors[-1]["name"]}'
    breadcrumbs += '</nav>'

    # --- parent category ---
    parent = category_by_id.get(cat.get("parent_id"))
    if parent:
        parent_html = (
            f'<p><strong>Parent category:</strong> '
            f'<a href="{parent["id"]}.html">{parent["name"]}</a></p>'
        )
    else:
        parent_html = ""

    # --- subcategories ---
    children = children_by_parent.get(cat_id, [])
    if children:
        sub_html = "<ul>" + "".join(
            f'<li><a href="{c["id"]}.html">{c["name"]}</a></li>'
            for c in children
        ) + "</ul>"
    else:
        sub_html = "<p>No subcategories.</p>"

# --- spells in this category (grouped by title) ---

    spell_ids = [
        sc["spell_id"]
        for sc in spell_categories
        if sc["category_id"] == cat_id
    ]

    related_spells = [
        sp for sp in spells
        if sp["id"] in spell_ids
    ]

# группируем по title_en
    spells_by_title = {}

    for sp in related_spells:
        title = sp.get("title_en", "Untitled")
        spells_by_title.setdefault(title, []).append(sp)

    if spells_by_title:
        blocks = []

        for title, entries in spells_by_title.items():
            refs = []

            for sp in entries:
                ms = manuscript_by_id.get(sp["manuscript_id"], {})
                refs.append(
                    f'<a href="../manuscripts/{sp["manuscript_id"]}.html">{ms.get("siglum","")}</a> '
                    f'<a href="../spells/{sp["id"]}.html">{sp.get("page","")}</a>'
                )

            block = (
                f'<li>'
                f'<strong>{title}</strong><br>'
                f'(' + "; ".join(refs) + ')'
                f'</li>'
            )

            blocks.append(block)

        spells_html = "<ul>" + "".join(blocks) + "</ul>"
    else:
        spells_html = "<p>No spells in this category.</p>"

    inner = (
        category_template
        .replace("{{ breadcrumbs }}", breadcrumbs)
        .replace("{{ category_name }}", f'{cat["name"]} ({count})')
        .replace("{{ parent }}", parent_html)
        .replace("{{ subcategories }}", sub_html)
        .replace("{{ spells }}", spells_html)
    )

    html = render(cat["name"], inner)

    (CATEGORY_DIR / f"{cat_id}.html").write_text(html, encoding="utf-8")

# ---------- categories index (tree) ----------

categories_index_template = load("categories_index.html")

tree_blocks = []

# верхний уровень = parent_id пустой
root_categories = [
    c for c in categories
    if not c.get("parent_id")
]

for root in root_categories:
    root_id = root["id"]

    count = total_spell_count(root_id)

    block = (
        f'<h2><a href="{root_id}.html">'
        f'{root["name"]} ({count})'
        f'</a></h2>'
    )

    children = children_by_parent.get(root_id, [])

    if children:
        block += "<ul>" + "".join(
            f'<li><a href="{c["id"]}.html">'
            f'{c["name"]} ({total_spell_count(c["id"])})'
            f'</a></li>'
            for c in children
        ) + "</ul>"

    tree_blocks.append(block)

tree_html = "\n".join(tree_blocks)

inner = categories_index_template.replace("{{ tree }}", tree_html)

html = render("Categories", inner)

(SITE / "categories" / "index.html").write_text(html, encoding="utf-8")