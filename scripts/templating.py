import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sitegen.i18n import get_translations

BASE_PATH = os.environ.get("BASE_PATH", "").strip()
if BASE_PATH:
    BASE_PATH = "/" + BASE_PATH.strip("/")
else:
    BASE_PATH = ""

CACHE_BUST = os.environ.get("CACHE_BUST", "").strip()


def root(path: str) -> str:
    return f"{BASE_PATH}{path}"


def lang_root(lang: str, path: str) -> str:
    lang = (lang or "ru").strip().lower()
    if lang not in ("ru", "en"):
        lang = "ru"

    if not path.startswith("/"):
        path = "/" + path

    return root(f"/{lang}{path}")


def alpha_letters(lang: str):
    if lang == "ru":
        return list("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ")
    return list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def make_env(lang: str = "ru"):
    lang = (lang or "ru").strip().lower()
    if lang not in ("ru", "en"):
        lang = "ru"

    tr = get_translations(lang)

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    env.globals["base_path"] = BASE_PATH
    env.globals["cache_bust"] = CACHE_BUST
    env.globals["root"] = root
    env.globals["lang"] = lang
    env.globals["lang_root"] = lambda path: lang_root(lang, path)
    env.globals["lang_url"] = lang_root
    env.globals["other_lang"] = "en" if lang == "ru" else "ru"
    env.globals["t"] = lambda key: tr.get(key, key)
    env.globals["alpha_letters"] = alpha_letters(lang)

    return env