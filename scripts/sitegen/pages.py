from pathlib import Path
from templating import root
from sitegen.services import render_breadcrumbs

def build_index(site_dir: Path, tpl_index, manuscripts):
    html = tpl_index.render(
        title="Manuscript Corpus",
        manuscripts=manuscripts,
    )
    (site_dir / "index.html").write_text(html, encoding="utf-8")


def build_manuscripts(site_dir: Path, tpl_ms, manuscripts, spells_by_ms_id):
    out_dir = site_dir / "manuscripts"
    out_dir.mkdir(exist_ok=True)

    for ms in manuscripts:
        breadcrumbs = render_breadcrumbs([
            ("Home", "/index.html"),
            (ms.get("title", ""), None),
        ])

        related_spells = spells_by_ms_id.get(ms["id"], [])

        html = tpl_ms.render(
            title=ms.get("title", "Manuscript"),
            ms=ms,
            related_spells=related_spells,
            breadcrumbs=breadcrumbs,
        )
        (out_dir / f'{ms["id"]}.html').write_text(html, encoding="utf-8")


def build_spells(site_dir: Path, tpl_spell, spells, manuscript_by_id, cats_by_spell_id, category_by_id, category_ancestors):
    out_dir = site_dir / "spells"
    out_dir.mkdir(exist_ok=True)

    for sp in spells:
        ms = manuscript_by_id.get(sp.get("manuscript_id"), {})
        cat_ids = cats_by_spell_id.get(sp["id"], [])

        crumbs = [
            ("Home", "/index.html"),
            ("Categories", "/categories/index.html"),
        ]

        if cat_ids:
            main_cat = category_by_id.get(cat_ids[0])
            if main_cat:
                for c in category_ancestors(main_cat["id"]):
                    crumbs.append((c["name"], f'/categories/{c["id"]}.html'))

        crumbs.append((sp.get("title_en", ""), None))
        breadcrumbs = render_breadcrumbs(crumbs)

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
        (out_dir / f"{sp['id']}.html").write_text(html, encoding="utf-8")


def build_spells_index(site_dir: Path, tpl_spells_index, spells, manuscript_by_id):
    out_dir = site_dir / "spells"
    out_dir.mkdir(exist_ok=True)

    def display_title(sp):
        return (sp.get("title_en") or "Untitled").strip() or "Untitled"

    def norm_title(t: str) -> str:
        return " ".join(t.split()).lower()


    def sort_key(sp):
        ms = manuscript_by_id.get(sp.get("manuscript_id"), {})
        return (
            norm_title(display_title(sp)),
            (ms.get("siglum") or "").lower(),
            str(sp.get("page") or ""),
            sp.get("id") or "",
        )

    grouped = {}
    order = [] 

    for sp in sorted(spells, key=sort_key):
        t = display_title(sp)
        nt = norm_title(t)

        if nt not in grouped:
            grouped[nt] = {"title": t, "refs": []}
            order.append(nt)

        ms_id = sp.get("manuscript_id") or ""
        ms = manuscript_by_id.get(ms_id, {})

        grouped[nt]["refs"].append({
            "spell_id": sp.get("id") or "",
            "manuscript_id": ms_id,
            "siglum": ms.get("siglum", ""),
            "page": sp.get("page", ""),
        })

    rows = []
    for nt in order:
        title = grouped[nt]["title"]

        seen = set()
        refs = []
        for r in grouped[nt]["refs"]:
            key = (r["manuscript_id"], str(r["page"]), r["spell_id"])
            if key in seen:
                continue
            seen.add(key)
            refs.append(r)

        refs.sort(key=lambda r: (
            (r.get("siglum") or "").lower(),
            str(r.get("page") or ""),
            r.get("spell_id") or "",
        ))

        rows.append({
            "title_en": title,
            "refs": refs,
        })

    html = tpl_spells_index.render(
        title="Spells",
        spells=rows,
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8")

def build_categories(
    site_dir: Path,
    tpl_cat,
    categories,
    manuscript_by_id,
    children_by_parent,
    category_by_id,
    category_ancestors,
    total_spell_count,
    spell_ids_by_cat_id,
    spell_by_id,
):
    out_dir = site_dir / "categories"
    out_dir.mkdir(exist_ok=True)

    for cat in categories:
        cat_id = cat["id"]
        count = total_spell_count(cat_id)

        ancestors = category_ancestors(cat_id)
        crumbs = [
            ("Home", "/index.html"),
            ("Categories", "/categories/index.html"),
        ]
        for c in ancestors[:-1]:
            crumbs.append((c["name"], f'/categories/{c["id"]}.html'))
        crumbs.append((ancestors[-1]["name"], None))
        breadcrumbs = render_breadcrumbs(crumbs)

        pid = (cat.get("parent_id") or "").strip() or None
        parent = category_by_id.get(pid)
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
                blocks.append(f'<li><strong>{title}</strong><br>(' + "; ".join(refs) + ')</li>')

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
        (out_dir / f"{cat_id}.html").write_text(html, encoding="utf-8")


def build_categories_index(site_dir: Path, tpl_cats_index, children_by_parent, total_spell_count):
    categories_dir = site_dir / "categories"
    categories_dir.mkdir(exist_ok=True)
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
    (site_dir / "categories" / "index.html").write_text(html, encoding="utf-8")