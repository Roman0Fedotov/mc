import argparse
import json
from pathlib import Path


def _clean(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def validate_text_file(path: Path):
    errors = []
    warnings = []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path}: invalid JSON: {exc}"], warnings

    if not isinstance(data, dict):
        return [f"{path}: root must be an object"], warnings

    spell_id = _clean(data.get("spell_id"))

    if not spell_id:
        errors.append(f"{path}: missing spell_id")
    elif spell_id != path.stem:
        errors.append(f"{path}: spell_id={spell_id!r} does not match filename {path.stem!r}")

    source_title = data.get("source_title")
    if source_title is not None and not isinstance(source_title, dict):
        errors.append(f"{path}: source_title must be an object")

    lines = data.get("lines")
    if not isinstance(lines, list):
        errors.append(f"{path}: lines must be a list")
        lines = []

    seen_numbers = set()

    for index, line in enumerate(lines, start=1):
        prefix = f"{path}: lines[{index}]"

        if not isinstance(line, dict):
            errors.append(f"{prefix}: line must be an object")
            continue

        n = line.get("n")

        if n in (None, ""):
            errors.append(f"{prefix}: missing n")
        elif n in seen_numbers:
            errors.append(f"{prefix}: duplicate n={n!r}")
        else:
            seen_numbers.add(n)

        if not _clean(line.get("syr")):
            errors.append(f"{prefix}: missing syr")

        translation = line.get("translation")

        if not isinstance(translation, dict):
            errors.append(f"{prefix}: translation must be an object")
            continue

        has_ru = bool(_clean(translation.get("ru")))
        has_en = bool(_clean(translation.get("en")))

        if not has_ru and not has_en:
            errors.append(f"{prefix}: at least one translation is required")

    bibliography = data.get("bibliography", [])

    if bibliography not in (None, []) and not isinstance(bibliography, list):
        errors.append(f"{path}: bibliography must be a list")

    return errors, warnings


def validate_texts_dir(texts_dir: Path):
    errors = []
    warnings = []

    if not texts_dir.exists():
        warnings.append(f"texts directory not found: {texts_dir}")
        return errors, warnings

    paths = sorted(texts_dir.glob("*.json"))

    if not paths:
        warnings.append(f"no JSON files found in {texts_dir}")

    seen_ids = set()

    for path in paths:
        e, w = validate_text_file(path)
        errors.extend(e)
        warnings.extend(w)

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            sid = _clean(data.get("spell_id"))

            if sid:
                if sid in seen_ids:
                    errors.append(f"{path}: duplicate spell_id={sid}")
                seen_ids.add(sid)
        except Exception:
            pass

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate private full-text JSON files.")
    parser.add_argument("--texts-dir", default="private-data/texts")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    errors, warnings = validate_texts_dir(Path(args.texts_dir))

    for warning in warnings:
        print("WARNING:", warning)

    for error in errors:
        print("ERROR:", error)

    if args.strict and errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()