import argparse
import shutil
from pathlib import Path

from templating import make_env

from sitegen.data_loader import load_all
from sitegen.indexes import build_indexes
from sitegen.services import build_category_graph, make_total_spell_count
from sitegen.pages import (
    build_index,
    build_manuscripts,
    build_spells,
    build_categories,
    build_categories_index,
)
from sitegen.validate import validate_data

SITE = Path("site")


def clean_site(site_dir: Path) -> None:
    for sub in ("manuscripts", "spells", "categories"):
        shutil.rmtree(site_dir / sub, ignore_errors=True)

    try:
        (site_dir / "index.html").unlink()
    except FileNotFoundError:
        pass


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

    manuscripts, spells, categories, spell_categories = load_all()

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

    env = make_env()
    tpl_index = env.get_template("index.html")
    tpl_ms = env.get_template("manuscript.html")
    tpl_spell = env.get_template("spell.html")
    tpl_cat = env.get_template("category.html")
    tpl_cats_index = env.get_template("categories_index.html")

    build_index(SITE, tpl_index, manuscripts)
    build_manuscripts(SITE, tpl_ms, manuscripts, idx["spells_by_ms_id"])
    build_spells(
        SITE,
        tpl_spell,
        spells,
        idx["manuscript_by_id"],
        idx["cats_by_spell_id"],
        category_by_id,
        category_ancestors,
    )
    build_categories(
        SITE,
        tpl_cat,
        categories,
        idx["manuscript_by_id"],
        children_by_parent,
        category_by_id,
        category_ancestors,
        total_spell_count,
        idx["spell_ids_by_cat_id"],
        idx["spell_by_id"],
    )
    build_categories_index(SITE, tpl_cats_index, children_by_parent, total_spell_count)


if __name__ == "__main__":
    main()