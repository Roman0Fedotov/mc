from pathlib import Path
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_PATH = os.environ.get("BASE_PATH", "").strip()
if BASE_PATH:
    BASE_PATH = "/" + BASE_PATH.strip("/")
else:
    BASE_PATH = ""

def root(path: str) -> str:
    return f"{BASE_PATH}{path}"

def make_env():
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.globals["base_path"] = BASE_PATH
    env.globals["root"] = root
    return env