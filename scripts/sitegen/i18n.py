TRANSLATIONS = {
    "ru": {
        "site_title": "Корпус рукописей",

        "nav_manuscripts": "Рукописи",
        "nav_spells": "Тексты",
        "nav_categories": "Категории",

        "manuscripts": "Рукописи",
        "spells": "Тексты",
        "categories": "Категории",

        "title": "Название",
        "catalog_title": "Обобщённое название",
        "source_title": "Название в рукописи",
        "source_title_syriac": "Сирийское название",
        "source_title_translation": "Перевод названия",
        "siglum": "Сиглум",
        "location": "Местонахождение",
        "collection": "Собрание",
        "shelfmark": "Каталожный № (шифр)",
        "date": "Дата",
        "format": "Формат",
        "texts_count": "Количество текстов",
        "bibliography": "Библиография",
        "manuscript": "Рукопись",
        "page": "Лист",
        "scribe": "Писец",
        "occurrences": "Вхождения",
        "occurrence_count": "Вхождений",

        "subcategories": "Подкатегории",
        "parent_category": "Родительская категория",
        "spells_in_category": "Тексты в этой категории",

        "back_to_manuscripts": "← Назад к рукописям",
        "back_to_spells": "← Назад к текстам",
        "back_to_categories": "← Назад к категориям",
        "back_to_this_manuscript": "← Назад к этой рукописи",

        "no_spells_recorded": "Тексты не зафиксированы.",
        "no_categories_assigned": "Категории не назначены.",
        "no_subcategories": "Подкатегорий нет.",
        "no_spells_in_category": "В этой категории нет текстов.",

        "show": "Показывать",
        "all": "ВСЕ",
        "other": "ДРУГОЕ",
        "prev": "Назад",
        "next": "Вперёд",

        "spell_title_singular": "название текста",
        "spell_title_plural": "названий текстов",
        "manuscript_singular": "рукопись",
        "manuscript_plural": "рукописей",

        "breadcrumb_label": "Хлебные крошки",

        "language_switcher_label": "Переключение языка",
        "pagination_label": "Пагинация",

        "full_text": "Текст",
        "translation": "Перевод",
        "syriac_text": "Сирийский текст",
        "translation_switcher_label": "Переключение перевода",
        "translation_ru": "Русский",
        "translation_en": "English",
        "note": "Примечание",
        "text_bibliography": "Библиография текста",
    },

    "en": {
        "site_title": "Manuscript Corpus",

        "nav_manuscripts": "Manuscripts",
        "nav_spells": "Texts",
        "nav_categories": "Categories",

        "manuscripts": "Manuscripts",
        "spells": "Texts",
        "categories": "Categories",

        "title": "Title",
        "catalog_title": "Catalog title",
        "source_title": "Title in manuscript",
        "source_title_syriac": "Syriac title",
        "source_title_translation": "Title translation",
        "siglum": "Siglum",
        "location": "Location",
        "collection": "Collection",
        "shelfmark": "Catalogue no. (Shelfmark)",
        "date": "Date",
        "format": "Format",
        "texts_count": "Number of texts",
        "bibliography": "Bibliography",
        "manuscript": "Manuscript",
        "page": "Page",
        "scribe": "Scribe",
        "occurrences": "Occurrences",
        "occurrence_count": "Occurrences",

        "subcategories": "Subcategories",
        "parent_category": "Parent category",
        "spells_in_category": "Texts in this category",

        "back_to_manuscripts": "← Back to manuscripts",
        "back_to_spells": "← Back to texts",
        "back_to_categories": "← Back to categories",
        "back_to_this_manuscript": "← Back to this manuscript",

        "no_spells_recorded": "No texts recorded.",
        "no_categories_assigned": "No categories assigned.",
        "no_subcategories": "No subcategories.",
        "no_spells_in_category": "No texts in this category.",

        "show": "Show",
        "all": "ALL",
        "other": "OTHER",
        "prev": "Prev",
        "next": "Next",

        "spell_title_singular": "text title",
        "spell_title_plural": "text titles",
        "manuscript_singular": "manuscript",
        "manuscript_plural": "manuscripts",

        "breadcrumb_label": "Breadcrumbs",

        "language_switcher_label": "Language switcher",
        "pagination_label": "Pagination",

        "full_text": "Text",
        "translation": "Translation",
        "syriac_text": "Syriac text",
        "translation_switcher_label": "Translation switcher",
        "translation_ru": "Русский",
        "translation_en": "English",
        "note": "Note",
        "text_bibliography": "Text bibliography",
    },
}


def get_translations(lang: str) -> dict:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])