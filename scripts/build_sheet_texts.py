import csv
import json
import shutil
from pathlib import Path


SPELLS_CSV = Path("data/spells.csv")
OUT_DIR = Path("build/texts")


def clean(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def detect_delimiter(sample: str) -> str:
    first_line = sample.splitlines()[0] if sample else ""

    if ";" in first_line:
        return ";"

    if "," in first_line:
        return ","

    raise ValueError("Could not detect CSV delimiter")


def split_text_cell(value) -> list[str]:
    """
    Один перенос строки в ячейке = одна строка текста.
    Внешние пустые строки удаляем.
    Внутренние пустые строки сохраняем, чтобы не нарушить выравнивание.
    """
    if value is None:
        return []

    text = str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if not text.strip():
        return []

    lines = text.split("\n")

    while lines and not lines[0].strip():
        lines.pop(0)

    while lines and not lines[-1].strip():
        lines.pop()

    return [line.strip() for line in lines]


def make_text(row: dict, row_number: int):
    spell_id = clean(row.get("id"))

    syr_lines = split_text_cell(row.get("text_syr"))
    ru_lines = split_text_cell(row.get("text_ru"))
    en_lines = split_text_cell(row.get("text_en"))

    # У этого spell вообще нет полного текста
    if not syr_lines and not ru_lines and not en_lines:
        return None

    if not spell_id:
        raise ValueError(
            f"Row {row_number}: full text exists, but id is empty"
        )

    if not syr_lines:
        raise ValueError(
            f"{spell_id}: text_syr is empty"
        )

    line_count = len(syr_lines)

    # Если перевод существует, число строк должно совпадать
    if ru_lines and len(ru_lines) != line_count:
        raise ValueError(
            f"{spell_id}: line count mismatch: "
            f"text_syr={line_count}, text_ru={len(ru_lines)}"
        )

    if en_lines and len(en_lines) != line_count:
        raise ValueError(
            f"{spell_id}: line count mismatch: "
            f"text_syr={line_count}, text_en={len(en_lines)}"
        )

    # Полностью отсутствующий язык превращаем
    # в пустые значения нужной длины
    if not ru_lines:
        ru_lines = [""] * line_count

    if not en_lines:
        en_lines = [""] * line_count

    lines = []

    for i in range(line_count):
        syr = syr_lines[i]
        ru = ru_lines[i]
        en = en_lines[i]

        if not syr:
            raise ValueError(
                f"{spell_id}: empty Syriac line {i + 1}"
            )

        # Сохраняем нынешнее правило проекта:
        # должен существовать хотя бы один перевод
        if not ru and not en:
            raise ValueError(
                f"{spell_id}: line {i + 1} has no RU or EN translation"
            )

        lines.append({
            "n": i + 1,
            "syr": syr,
            "translation": {
                "ru": ru,
                "en": en,
            },
            "note": "",
        })

    return {
        "spell_id": spell_id,

        "source_title": {
            "syr": clean(row.get("source_title_syr")),
            "ru": clean(row.get("source_title_ru")),
            "en": clean(row.get("source_title_en")),
        },

        "lines": lines,

        "bibliography": [],
    }


def main():
    if not SPELLS_CSV.exists():
        raise FileNotFoundError(SPELLS_CSV)

    # Важно для локальных повторных сборок:
    # старые тексты не должны оставаться.
    shutil.rmtree(OUT_DIR, ignore_errors=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with SPELLS_CSV.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        sample = f.read(4096)
        f.seek(0)

        delimiter = detect_delimiter(sample)

        reader = csv.DictReader(
            f,
            delimiter=delimiter
        )

        seen_ids = set()
        count = 0

        for row_number, row in enumerate(reader, start=2):
            data = make_text(row, row_number)

            if data is None:
                continue

            spell_id = data["spell_id"]

            if spell_id in seen_ids:
                raise ValueError(
                    f"Duplicate spell id with full text: {spell_id}"
                )

            seen_ids.add(spell_id)

            out_path = OUT_DIR / f"{spell_id}.json"

            out_path.write_text(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )

            count += 1

    print(f"Created {count} spell text JSON files in {OUT_DIR}")


if __name__ == "__main__":
    main()