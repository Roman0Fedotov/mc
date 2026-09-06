import html
import unicodedata
from pathlib import Path

from templating import lang_root
from sitegen.i18n import get_translations
from sitegen.services import render_breadcrumbs


def tr(lang: str, key: str) -> str:
    extra = {
        "ru": {"home": "Главная"},
        "en": {"home": "Home"},
    }
    if key in extra.get(lang, {}):
        return extra[lang][key]
    return get_translations(lang).get(key, key)


def _clean(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_syriac_for_display(value) -> str:
    text = _clean(value)

    result = []
    i = 0

    while i < len(text):
        ch = text[i]

        if ch != "ܪ":
            result.append(ch)
            i += 1
            continue

        j = i + 1
        marks = []

        while j < len(text) and unicodedata.category(text[j]).startswith("M"):
            marks.append(text[j])
            j += 1

        has_syame = "\u0308" in marks
        has_other_marks = len(marks) > 1

        if has_syame and has_other_marks:
            result.append("ܖ")
        else:
            result.append(ch)

        result.extend(marks)
        i = j

    return "".join(result)


def first_non_empty(*values) -> str:
    for value in values:
        value = _clean(value)
        if value:
            return value
    return ""


def alpha_letter_en(text: str) -> str:
    text = _clean(text)
    if not text:
        return "#"
    first = text[0].upper()
    return first if "A" <= first <= "Z" else "#"


def first_alpha_char(text: str) -> str:
    for ch in _clean(text).upper():
        if ("A" <= ch <= "Z") or ("А" <= ch <= "Я") or ch == "Ё":
            return ch
    return ""

def alpha_letter_spell(text: str, lang: str) -> str:
    ch = first_alpha_char(text)
    if not ch:
        return "OTHER"

    if lang == "ru":
        if ch == "Ё":
            ch = "Е"
        return ch if "А" <= ch <= "Я" else "OTHER"

    return ch if "A" <= ch <= "Z" else "OTHER"


# ---------- manuscripts ----------

def get_ms_siglum(ms: dict) -> str:
    return first_non_empty(
        ms.get("siglum"),
        ms.get("id"),
    )


def get_ms_collection(ms: dict) -> str:
    return first_non_empty(ms.get("collection"))


def get_ms_shelfmark(ms: dict) -> str:
    return first_non_empty(ms.get("shelfmark"))


def get_ms_location(ms: dict, lang: str) -> str:
    return _clean(ms.get(f"location_{lang}"))


def get_ms_format(ms: dict, lang: str) -> str:
    return first_non_empty(ms.get(f"format_{lang}"), ms.get("format"))


def get_ms_bibliography(ms: dict, lang: str) -> str:
    # bibliography у тебя пока общее поле, не разбитое по языкам
    return first_non_empty(ms.get("bibliography"))


def get_ms_texts_count(ms: dict) -> str:
    return first_non_empty(ms.get("texts_count"), ms.get("N of texts"))


# ---------- categories ----------

def get_category_name(cat: dict, lang: str) -> str:
    if lang == "ru":
        return first_non_empty(
            cat.get("name_ru"),
            cat.get("name"),
            cat.get("name_en"),
            cat.get("id"),
        )
    return first_non_empty(
        cat.get("name_en"),
        cat.get("name"),
        cat.get("name_ru"),
        cat.get("id"),
    )


# ---------- spells ----------

def get_spell_catalog_title(sp: dict, lang: str) -> str:
    if lang == "ru":
        return first_non_empty(
            sp.get("catalog_title_ru"),
            sp.get("catalog_title_en"),
            sp.get("source_title_ru"),
            sp.get("source_title_en"),
            sp.get("source_title_syr"),
            sp.get("id"),
        )
    return first_non_empty(
        sp.get("catalog_title_en"),
        sp.get("catalog_title_ru"),
        sp.get("source_title_en"),
        sp.get("source_title_ru"),
        sp.get("source_title_syr"),
        sp.get("id"),
    )


def get_spell_source_title_syr(sp: dict) -> str:
    return normalize_syriac_for_display(sp.get("source_title_syr"))


def get_spell_source_title_translation(sp: dict, lang: str) -> str:
    # это поле необязательное: если пусто, просто не показываем
    return first_non_empty(sp.get(f"source_title_{lang}"))


def get_spell_scribe(sp: dict) -> str:
    return first_non_empty(sp.get("scribe"))


def prepare_full_text(full_text: dict, lang: str):
    if not isinstance(full_text, dict):
        return None

    source_title = full_text.get("source_title") or {}
    if not isinstance(source_title, dict):
        source_title = {}

    lines_out = []

    for line in full_text.get("lines") or []:
        if not isinstance(line, dict):
            continue

        translation = line.get("translation") or {}
        if not isinstance(translation, dict):
            translation = {}

        lines_out.append({
            "n": _clean(line.get("n")),
            "syr": normalize_syriac_for_display(line.get("syr")),
            "translation_ru": _clean(translation.get("ru")),
            "translation_en": _clean(translation.get("en")),
            "translation_current": first_non_empty(
                translation.get(lang),
                translation.get("ru"),
                translation.get("en"),
            ),
            "note": _clean(line.get("note")),
        })

    bibliography_out = []
    bibliography = full_text.get("bibliography") or []

    if isinstance(bibliography, list):
        for item in bibliography:
            if isinstance(item, dict):
                text = _clean(item.get("text"))
            else:
                text = _clean(item)

            if text:
                bibliography_out.append(text)

    return {
        "spell_id": _clean(full_text.get("spell_id")),
        "source_title_syr": normalize_syriac_for_display(source_title.get("syr")),
        "source_title_ru": _clean(source_title.get("ru")),
        "source_title_en": _clean(source_title.get("en")),
        "source_title_current": first_non_empty(
            source_title.get(lang),
            source_title.get("ru"),
            source_title.get("en"),
        ),
        "lines": lines_out,
        "bibliography": bibliography_out,
    }


def prepare_manuscript(ms: dict, lang: str) -> dict:
    item = dict(ms)

    item["siglum_display"] = get_ms_siglum(ms)
    item["location_display"] = get_ms_location(ms, lang)
    item["collection_display"] = get_ms_collection(ms)
    item["shelfmark_display"] = get_ms_shelfmark(ms)
    item["format_display"] = get_ms_format(ms, lang)
    item["bibliography_display"] = get_ms_bibliography(ms, lang)
    item["texts_count_display"] = get_ms_texts_count(ms)

    # Алфавитный фильтр на странице рукописей должен
    # соответствовать первой видимой колонке — Siglum.
    item["alpha_letter"] = alpha_letter_en(item["siglum_display"])

    return item


def prepare_spell(sp: dict, lang: str) -> dict:
    item = dict(sp)
    title_display = get_spell_catalog_title(sp, lang)
    item["title_display"] = title_display
    item["catalog_title_display"] = title_display
    item["source_title_syr_display"] = get_spell_source_title_syr(sp)
    item["source_title_translation_display"] = get_spell_source_title_translation(sp, lang)
    item["scribe_display"] = get_spell_scribe(sp)
    item["alpha_letter"] = alpha_letter_spell(title_display, lang)
    return item


def build_index(site_dir: Path, tpl_index, manuscripts, lang):
    prepared = [prepare_manuscript(ms, lang) for ms in manuscripts]

    html_out = tpl_index.render(
        title=tr(lang, "manuscripts"),
        manuscripts=prepared,
        current_rel_path="/index.html",
    )
    (site_dir / "index.html").write_text(html_out, encoding="utf-8")



def build_manuscripts(site_dir: Path, tpl_ms, manuscripts, spells_by_ms_id, lang):
    out_dir = site_dir / "manuscripts"
    out_dir.mkdir(exist_ok=True)

    for ms in manuscripts:
        ms_view = prepare_manuscript(ms, lang)

        breadcrumbs = render_breadcrumbs([
            (tr(lang, "home"), "/index.html"),
            (tr(lang, "manuscripts"), "/index.html"),
            (ms_view["siglum_display"], None),
        ], lang)

        related_spells = []
        for sp in spells_by_ms_id.get(ms["id"], []):
            sp_view = prepare_spell(sp, lang)
            related_spells.append({
                "id": _clean(sp_view.get("id")),
                "page": _clean(sp_view.get("page")),
                "title_display": sp_view["title_display"],
            })

        html_out = tpl_ms.render(
            title=ms_view["siglum_display"] or tr(lang, "manuscript"),
            ms=ms_view,
            related_spells=related_spells,
            breadcrumbs=breadcrumbs,
            current_rel_path=f"/manuscripts/{ms['id']}.html",
        )
        (out_dir / f'{ms["id"]}.html').write_text(html_out, encoding="utf-8")



def build_spells(site_dir: Path, tpl_spell, spells, manuscript_by_id, cats_by_spell_id, category_by_id, category_ancestors, spell_texts, lang):
    out_dir = site_dir / "spells"
    out_dir.mkdir(exist_ok=True)

    for sp in spells:
        sp_view = prepare_spell(sp, lang)

        ms = manuscript_by_id.get(sp.get("manuscript_id"), {})
        ms_view = prepare_manuscript(ms, lang) if ms else {}

        cat_ids = cats_by_spell_id.get(sp["id"], [])

        breadcrumbs = render_breadcrumbs([
            (tr(lang, "home"), "/index.html"),
            (tr(lang, "spells"), "/spells/index.html"),
            (sp_view["title_display"], None),
        ], lang)

        categories_list = []
        for cid in cat_ids:
            c = category_by_id.get(cid)
            if c:
                categories_list.append({
                    "id": cid,
                    "name_display": get_category_name(c, lang),
                })

        full_text = prepare_full_text(spell_texts.get(_clean(sp.get("id"))), lang)

        if full_text:
            sp_view["source_title_syr_display"] = first_non_empty(
                full_text.get("source_title_syr"),
                sp_view.get("source_title_syr_display"),
            )
            sp_view["source_title_translation_display"] = first_non_empty(
                full_text.get("source_title_current"),
                sp_view.get("source_title_translation_display"),
            )

        html_out = tpl_spell.render(
            title=sp_view["title_display"] or tr(lang, "spells"),
            sp=sp_view,
            ms=ms_view,
            breadcrumbs=breadcrumbs,
            categories=categories_list,
            full_text=full_text,
            current_rel_path=f"/spells/{sp['id']}.html",
    )
        (out_dir / f"{sp['id']}.html").write_text(html_out, encoding="utf-8")



def build_spells_index(site_dir: Path, tpl_spells_index, spells, manuscript_by_id, lang):
    out_dir = site_dir / "spells"
    out_dir.mkdir(exist_ok=True)

    def display_title(sp):
        return prepare_spell(sp, lang)["title_display"]

    def norm_title(text: str) -> str:
        return " ".join(_clean(text).split()).lower()

    def sort_key(sp):
        ms = manuscript_by_id.get(sp.get("manuscript_id"), {})
        return (
            norm_title(display_title(sp)),
            _clean(ms.get("siglum")).lower(),
            _clean(sp.get("page")),
            _clean(sp.get("id")),
        )

    grouped = {}
    order = []

    for sp in sorted(spells, key=sort_key):
        title = display_title(sp)
        ms_id = _clean(sp.get("manuscript_id"))
        ms = manuscript_by_id.get(ms_id, {})

        group_key = norm_title(title)
        if not group_key:
            group_key = _clean(sp.get("id"))

        if group_key not in grouped:
            grouped[group_key] = {"title_display": title, "refs": []}
            order.append(group_key)

        grouped[group_key]["refs"].append({
            "spell_id": _clean(sp.get("id")),
            "manuscript_id": ms_id,
            "siglum": _clean(ms.get("siglum")),
            "page": _clean(sp.get("page")),
        })

    rows = []
    for group_key in order:
        title = grouped[group_key]["title_display"]

        seen = set()
        refs = []
        for r in grouped[group_key]["refs"]:
            key = (r["manuscript_id"], r["page"], r["spell_id"])
            if key in seen:
                continue
            seen.add(key)
            refs.append(r)

        refs.sort(key=lambda r: (
            _clean(r.get("siglum")).lower(),
            _clean(r.get("page")),
            _clean(r.get("spell_id")),
        ))

        rows.append({
            "title_display": title,
            "alpha_letter": alpha_letter_spell(title, lang),
            "occurrence_count": len(refs),
        })

    html_out = tpl_spells_index.render(
        title=tr(lang, "spells"),
        spells=rows,
        current_rel_path="/spells/index.html",
    )
    (out_dir / "index.html").write_text(html_out, encoding="utf-8")



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
    lang,
):
    out_dir = site_dir / "categories"
    out_dir.mkdir(exist_ok=True)

    for cat in categories:
        cat_id = cat["id"]
        cat_name = get_category_name(cat, lang)
        count = total_spell_count(cat_id)

        ancestors = category_ancestors(cat_id)
        crumbs = [
            (tr(lang, "home"), "/index.html"),
            (tr(lang, "categories"), "/categories/index.html"),
        ]
        for c in ancestors[:-1]:
            crumbs.append((get_category_name(c, lang), f'/categories/{c["id"]}.html'))
        crumbs.append((cat_name, None))
        breadcrumbs = render_breadcrumbs(crumbs, lang)

        pid = _clean(cat.get("parent_id")) or None
        parent = category_by_id.get(pid)
        if parent:
            parent_name = get_category_name(parent, lang)
            parent_html = (
                f'<p><strong>{html.escape(tr(lang, "parent_category"))}:</strong> '
                f'<a href="{lang_root(lang, "/categories/" + parent["id"] + ".html")}">{html.escape(parent_name)}</a></p>'
            )
        else:
            parent_html = ""

        children = sorted(
            children_by_parent.get(cat_id, []),
            key=lambda c: (get_category_name(c, lang).lower(), _clean(c.get("id"))),
        )

        if children:
            sub_html = "<ul>" + "".join(
                f'<li><a href="{lang_root(lang, "/categories/" + c["id"] + ".html")}">{html.escape(get_category_name(c, lang))}</a></li>'
                for c in children
            ) + "</ul>"
        else:
            sub_html = f"<p>{html.escape(tr(lang, 'no_subcategories'))}</p>"

        spell_ids = spell_ids_by_cat_id.get(cat_id, [])
        related_spells = []
        seen_ids = set()
        for sid in spell_ids:
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
            if sid in spell_by_id:
                related_spells.append(spell_by_id[sid])

        grouped = {}
        order = []
        for sp in related_spells:
            title = get_spell_catalog_title(sp, lang)
            key = " ".join(title.split()).lower() or _clean(sp.get("id"))
            if key not in grouped:
                grouped[key] = {"title": title, "items": []}
                order.append(key)
            grouped[key]["items"].append(sp)

        if grouped:
            blocks = []
            for key in order:
                title = grouped[key]["title"]
                entries = grouped[key]["items"]
                refs = []
                for sp in entries:
                    ms = manuscript_by_id.get(sp.get("manuscript_id"), {})
                    refs.append(
                        f'<a href="{lang_root(lang, "/manuscripts/" + sp["manuscript_id"] + ".html")}">{html.escape(_clean(ms.get("siglum")))}</a> '
                        f'<a href="{lang_root(lang, "/spells/" + sp["id"] + ".html")}">{html.escape(_clean(sp.get("page")))}</a>'
                    )
                blocks.append(f'<li><strong>{html.escape(title)}</strong><br>(' + "; ".join(refs) + ')</li>')

            spells_html = "<ul>" + "".join(blocks) + "</ul>"
        else:
            spells_html = f"<p>{html.escape(tr(lang, 'no_spells_in_category'))}</p>"

        html_out = tpl_cat.render(
            title=cat_name or tr(lang, "categories"),
            breadcrumbs=breadcrumbs,
            category_name=f"{cat_name} ({count})",
            parent=parent_html,
            subcategories=sub_html,
            spells=spells_html,
            current_rel_path=f"/categories/{cat_id}.html",
        )
        (out_dir / f"{cat_id}.html").write_text(html_out, encoding="utf-8")



def build_categories_index(
    site_dir: Path,
    tpl_cats_index,
    children_by_parent,
    total_spell_count,
    lang,
):
    categories_dir = site_dir / "categories"
    categories_dir.mkdir(exist_ok=True)

    toggle_text = (
        "Свернуть или развернуть подкатегории"
        if lang == "ru"
        else "Collapse or expand subcategories"
    )

    def render_items(parent_id=None, path=()):
        categories = sorted(
            children_by_parent.get(parent_id, []),
            key=lambda c: (
                get_category_name(c, lang).lower(),
                _clean(c.get("id")),
            ),
        )

        items = []

        for cat in categories:
            cat_id = _clean(cat.get("id"))

            # Дополнительная защита от пустых id и циклов.
            if not cat_id or cat_id in path:
                continue

            cat_name = get_category_name(cat, lang)
            count = total_spell_count(cat_id)
            has_children = bool(children_by_parent.get(cat_id))

            if has_children:
                aria_label = html.escape(
                    f"{toggle_text}: {cat_name}",
                    quote=True,
                )

                toggle_html = (
                    '<button '
                    'type="button" '
                    'class="category-index-tree__toggle" '
                    'aria-expanded="true" '
                    f'aria-label="{aria_label}">'
                    '<span '
                    'class="category-index-tree__chevron" '
                    'aria-hidden="true">›</span>'
                    '</button>'
                )
            else:
                toggle_html = (
                    '<span '
                    'class="category-index-tree__toggle-placeholder" '
                    'aria-hidden="true"></span>'
                )

            count_classes = "count-badge category-index-tree__count"

            if count == 0:
                count_classes += " category-index-tree__count--zero"

            children_html = ""

            if has_children:
                children_html = (
                    '<ul class="category-index-tree__children">'
                    + render_items(
                        cat_id,
                        path + (cat_id,),
                    )
                    + "</ul>"
                )

            items.append(
                '<li class="category-index-tree__item">'
                '<div class="category-index-tree__row">'
                f"{toggle_html}"
                '<a '
                'class="category-index-tree__link" '
                f'href="{lang_root(lang, "/categories/" + cat_id + ".html")}">'
                f"{html.escape(cat_name)}"
                "</a>"
                f'<span class="{count_classes}">{count}</span>'
                "</div>"
                f"{children_html}"
                "</li>"
            )

        return "".join(items)

    tree_html = (
        '<ul '
        'class="category-index-tree" '
        'data-category-index-tree>'
        + render_items()
        + "</ul>"
    )

    html_out = tpl_cats_index.render(
        title=tr(lang, "categories"),
        tree=tree_html,
        current_rel_path="/categories/index.html",
    )

    (categories_dir / "index.html").write_text(
        html_out,
        encoding="utf-8",
    )



def build_bibliography(
    site_dir: Path,
    tpl_bibliography,
    bibliography,
    lang,
):
    bibliography_dir = site_dir / "bibliography"
    bibliography_dir.mkdir(exist_ok=True)

    html_out = tpl_bibliography.render(
        title=tr(lang, "bibliography"),
        bibliography=bibliography,
        current_rel_path="/bibliography/index.html",
    )

    (bibliography_dir / "index.html").write_text(
        html_out,
        encoding="utf-8",
    )