import argparse
import shutil
from pathlib import Path

from templating import make_env

from sitegen.data_loader import load_all
from sitegen.texts_loader import load_spell_texts
from sitegen.indexes import build_indexes
from sitegen.services import build_category_graph, make_total_spell_count
from sitegen.pages import (
    build_index,
    build_manuscripts,
    build_spells,
    build_spells_index,
    build_categories,
    build_categories_index,
)
from sitegen.validate import validate_data

SITE = Path("site")
ASSETS = Path("assets")
LANGS = ("ru", "en")


def clean_site(site_dir: Path) -> None:
    for sub in ("ru", "en", "manuscripts", "spells", "categories"):
        shutil.rmtree(site_dir / sub, ignore_errors=True)

    for filename in ("index.html",):
        try:
            (site_dir / filename).unlink()
        except FileNotFoundError:
            pass


def copy_assets(site_dir: Path) -> None:
    site_dir.mkdir(parents=True, exist_ok=True)

    css = ASSETS / "style.css"
    if not css.exists():
        raise SystemExit(f"Missing stylesheet: {css}. Put your CSS there.")

    for p in ASSETS.rglob("*"):
        if not p.is_file():
            continue

        rel = p.relative_to(ASSETS)
        target = site_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)


def write_root_redirect(site_dir: Path) -> None:
    html = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Redirect</title>
  <script>
    (function () {
      var lang = localStorage.getItem("preferred_lang") || "ru";
      if (lang !== "ru" && lang !== "en") lang = "ru";
      window.location.replace("./" + lang + "/index.html");
    })();
  </script>
</head>
<body></body>
</html>
"""
    (site_dir / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static site from JSON data.")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove generated HTML before build (recommended to avoid stale pages).",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate data and print issues (does not fail build).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail build if validation errors are found (implies --validate).",
    )
    args = parser.parse_args()

    if args.clean:
        clean_site(SITE)

    copy_assets(SITE)

    manuscripts, spells, categories, spell_categories = load_all()
    spell_texts = load_spell_texts()

    if args.validate or args.strict:
        errors, warnings = validate_data(manuscripts, spells, categories, spell_categories)

        for w in warnings:
            print("WARNING:", w)
        for e in errors:
            print("ERROR:", e)

        if args.strict and errors:
            raise SystemExit(1)

    idx = build_indexes(manuscripts, spells, spell_categories)

    category_by_id, children_by_parent, category_ancestors = build_category_graph(categories)
    total_spell_count = make_total_spell_count(children_by_parent, idx["spell_count_by_category"])

    for lang in LANGS:
        env = make_env(lang)
        lang_dir = SITE / lang
        lang_dir.mkdir(parents=True, exist_ok=True)

        tpl_index = env.get_template("index.html")
        tpl_spells_index = env.get_template("spells_index.html")
        tpl_ms = env.get_template("manuscript.html")
        tpl_spell = env.get_template("spell.html")
        tpl_cat = env.get_template("category.html")
        tpl_cats_index = env.get_template("categories_index.html")

        build_index(lang_dir, tpl_index, manuscripts, lang)
        build_manuscripts(lang_dir, tpl_ms, manuscripts, idx["spells_by_ms_id"], lang)
        build_spells(
            lang_dir,
            tpl_spell,
            spells,
            idx["manuscript_by_id"],
            idx["cats_by_spell_id"],
            category_by_id,
            category_ancestors,
            spell_texts,
            lang,
        )
        build_spells_index(lang_dir, tpl_spells_index, spells, idx["manuscript_by_id"], lang)
        build_categories(
            lang_dir,
            tpl_cat,
            categories,
            idx["manuscript_by_id"],
            children_by_parent,
            category_by_id,
            category_ancestors,
            total_spell_count,
            idx["spell_ids_by_cat_id"],
            idx["spell_by_id"],
            lang,
        )
        build_categories_index(lang_dir, tpl_cats_index, children_by_parent, total_spell_count, lang)

    write_root_redirect(SITE)


if __name__ == "__main__":
    main()