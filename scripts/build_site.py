import json
from pathlib import Path
from templating import make_env, root
from collections import defaultdict

SITE = Path("site")
DATA = SITE / "data"

#  загружаем рукописи
with open(DATA / "manuscripts.json", encoding="utf-8") as f:
    manuscripts = json.load(f)

with open(DATA / "spells.json", encoding="utf-8") as f:
    spells = json.load(f)

with open(DATA / "categories.json", encoding="utf-8") as f:
    categories = json.load(f)

with open(DATA / "spell_categories.json", encoding="utf-8") as f:
    spell_categories = json.load(f)

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
    
# словарь: id → рукопись
manuscript_by_id = {
    ms["id"]: ms
    for ms in manuscripts
}
# --- indexes for performance ---
spell_by_id = {sp["id"]: sp for sp in spells if sp.get("id")}

spells_by_ms_id = defaultdict(list)
for sp in spells:
    mid = sp.get("manuscript_id")
    if mid:
        spells_by_ms_id[mid].append(sp)

cats_by_spell_id = defaultdict(list)
spell_ids_by_cat_id = defaultdict(list)
for sc in spell_categories:
    sid = sc.get("spell_id")
    cid = sc.get("category_id")
    if sid and cid:
        cats_by_spell_id[sid].append(cid)
        spell_ids_by_cat_id[cid].append(sid)

# --- count spells per category (from index) ---
spell_count_by_category = {cid: len(set(sids)) for cid, sids in spell_ids_by_cat_id.items()}

category_by_id = {
    c["id"]: c
    for c in categories
}

children_by_parent = {}

for c in categories:
    parent = (c.get("parent_id") or "").strip() or None
    children_by_parent.setdefault(parent, []).append(c)

# --- UX: sort category children by name ---
for pid, kids in children_by_parent.items():
    kids.sort(key=lambda c: (
        (c.get("name") or "").lower(),
        c.get("id") or "",
    ))

from functools import lru_cache

def category_ancestors(cat_id):
    chain = []
    current = category_by_id.get(cat_id)
    seen = set()

    while current:
        cid = current.get("id")
        if not cid or cid in seen:
            break
        seen.add(cid)

        chain.append(current)
        pid = (current.get("parent_id") or "").strip() or None
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

env = make_env()

tpl_index = env.get_template("index.html")
tpl_ms = env.get_template("manuscript.html")
tpl_spell = env.get_template("spell.html")
tpl_cat = env.get_template("category.html")
tpl_cats_index = env.get_template("categories_index.html")

html = tpl_index.render(
    title="Manuscript Corpus",
    manuscripts=manuscripts,
)

(SITE / "index.html").write_text(html, encoding="utf-8")

# ---------- manuscript pages ----------

MANUSCRIPT_DIR = SITE / "manuscripts"
MANUSCRIPT_DIR.mkdir(exist_ok=True)

for ms in manuscripts:
    breadcrumbs = (
        '<nav class="breadcrumbs">'
        f'<a href="{root("/index.html")}">Home</a>'
        f' &#8594; {ms.get("title","")}'
        '</nav>'
    )

    related_spells = spells_by_ms_id.get(ms["id"], [])

    html = tpl_ms.render(
        title=ms.get("title", "Manuscript"),
        ms=ms,
        related_spells=related_spells,
        breadcrumbs=breadcrumbs,
    )

    (MANUSCRIPT_DIR / f'{ms["id"]}.html').write_text(html, encoding="utf-8")

# ---------- spells ----------

SPELL_DIR = SITE / "spells"
SPELL_DIR.mkdir(exist_ok=True)

for sp in spells:
    ms = manuscript_by_id.get(sp.get("manuscript_id"), {})

    cat_ids = cats_by_spell_id.get(sp["id"], [])

    breadcrumbs = (
        '<nav class="breadcrumbs">'
        f'<a href="{root("/index.html")}">Home</a> &#8594; '
        f'<a href="{root("/categories/index.html")}">Categories</a>'
    )

    if cat_ids:
        main_cat = category_by_id.get(cat_ids[0])
        if main_cat:
            for c in category_ancestors(main_cat["id"]):
                breadcrumbs += (
                    f' &#8594; <a href="{root("/categories/" + c["id"] + ".html")}">{c["name"]}</a>'
                )

    breadcrumbs += f' &#8594; {sp.get("title_en","")}'
    breadcrumbs += '</nav>'

    categories_list = []
    for cid in cat_ids:
        c = category_by_id.get(cid)
        if c:
            categories_list.append({"id": cid, "name": c["name"]})

    html = tpl_spell.render(
        title=sp.get("title_en", "Spell"),
        sp=sp,
        ms=ms,
        breadcrumbs=breadcrumbs,
        categories=categories_list,
    )

    (SPELL_DIR / f"{sp['id']}.html").write_text(html, encoding="utf-8")

# ---------- categories ----------

CATEGORY_DIR = SITE / "categories"
CATEGORY_DIR.mkdir(exist_ok=True)

for cat in categories:
    cat_id = cat["id"]
    count = total_spell_count(cat_id)

    ancestors = category_ancestors(cat_id)

    breadcrumbs = (
        '<nav class="breadcrumbs">'
        f'<a href="{root("/index.html")}">Home</a> &#8594; '
        f'<a href="{root("/categories/index.html")}">Categories</a>'
    )

    for c in ancestors[:-1]:
        breadcrumbs += f' &#8594; <a href="{root("/categories/" + c["id"] + ".html")}">{c["name"]}</a>'

    breadcrumbs += f' &#8594; {ancestors[-1]["name"]}'
    breadcrumbs += '</nav>'

    parent = category_by_id.get(cat.get("parent_id"))
    if parent:
        parent_html = (
            f'<p><strong>Parent category:</strong> '
            f'<a href="{root("/categories/" + parent["id"] + ".html")}">{parent["name"]}</a></p>'
        )
    else:
        parent_html = ""

    children = children_by_parent.get(cat_id, [])
    if children:
        sub_html = "<ul>" + "".join(
            f'<li><a href="{root("/categories/" + c["id"] + ".html")}">{c["name"]}</a></li>'
            for c in children
        ) + "</ul>"
    else:
        sub_html = "<p>No subcategories.</p>"

    spell_ids = spell_ids_by_cat_id.get(cat_id, [])
    related_spells = [spell_by_id[sid] for sid in spell_ids if sid in spell_by_id]

    spells_by_title = {}
    for sp in related_spells:
        title = sp.get("title_en", "Untitled")
        spells_by_title.setdefault(title, []).append(sp)

    if spells_by_title:
        blocks = []
        for title in sorted(spells_by_title.keys(), key=lambda s: s.lower()):
            entries = spells_by_title[title]
            refs = []
            for sp in entries:
                ms = manuscript_by_id.get(sp["manuscript_id"], {})
                refs.append(
                    f'<a href="{root("/manuscripts/" + sp["manuscript_id"] + ".html")}">{ms.get("siglum","")}</a> '
                    f'<a href="{root("/spells/" + sp["id"] + ".html")}">{sp.get("page","")}</a>'
                )

            blocks.append(
                f'<li><strong>{title}</strong><br>(' + "; ".join(refs) + ')</li>'
            )

        spells_html = "<ul>" + "".join(blocks) + "</ul>"
    else:
        spells_html = "<p>No spells in this category.</p>"

    html = tpl_cat.render(
        title=cat.get("name", "Category"),
        breadcrumbs=breadcrumbs,
        category_name=f'{cat["name"]} ({count})',
        parent=parent_html,
        subcategories=sub_html,
        spells=spells_html,
    )

    (CATEGORY_DIR / f"{cat_id}.html").write_text(html, encoding="utf-8")


# ---------- categories index (tree) ----------

tree_blocks = []

root_categories = sorted(
    children_by_parent.get(None, []),
    key=lambda c: (
        (c.get("name") or "").lower(),
        c.get("id") or "",
    ),
)

for root_cat in root_categories:
    root_id = root_cat["id"]
    count = total_spell_count(root_id)

    block = (
        f'<h2><a href="{root("/categories/" + root_id + ".html")}">'
        f'{root_cat["name"]} ({count})'
        f'</a></h2>'
    )

    children = children_by_parent.get(root_id, [])
    if children:
        block += "<ul>" + "".join(
            f'<li><a href="{root("/categories/" + c["id"] + ".html")}">'
            f'{c["name"]} ({total_spell_count(c["id"])})'
            f'</a></li>'
            for c in children
        ) + "</ul>"

    tree_blocks.append(block)

tree_html = "\n".join(tree_blocks)

html = tpl_cats_index.render(
    title="Categories",
    tree=tree_html,
)

(SITE / "categories" / "index.html").write_text(html, encoding="utf-8")