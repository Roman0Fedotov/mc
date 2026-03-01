from functools import lru_cache
from templating import root

def build_category_graph(categories):
    category_by_id = {c["id"]: c for c in categories}

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

    return category_by_id, children_by_parent, category_ancestors


def make_total_spell_count(children_by_parent, spell_count_by_category):
    @lru_cache(None)
    def total_spell_count(cat_id):
        total = spell_count_by_category.get(cat_id, 0)
        for child in children_by_parent.get(cat_id, []):
            total += total_spell_count(child["id"])
        return total

    return total_spell_count


def render_breadcrumbs(items):
    parts = []
    for label, href in items:
        if href:
            parts.append(f'<a href="{root(href)}">{label}</a>')
        else:
            parts.append(label)
    return '<nav class="breadcrumbs">' + " &#8594; ".join(parts) + "</nav>"