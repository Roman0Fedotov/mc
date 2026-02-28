def validate_data(manuscripts, spells, categories, spell_categories):
    errors = []
    warnings = []

    # helpers
    def find_dupes(ids):
        seen = set()
        dupes = set()
        for x in ids:
            if x in seen:
                dupes.add(x)
            seen.add(x)
        return sorted(d for d in dupes if d)

    ms_ids = [m.get("id") for m in manuscripts]
    sp_ids = [s.get("id") for s in spells]
    cat_ids = [c.get("id") for c in categories]

    dup_ms = find_dupes(ms_ids)
    dup_sp = find_dupes(sp_ids)
    dup_cat = find_dupes(cat_ids)

    if dup_ms:
        warnings.append(f"Duplicate manuscript ids: {dup_ms[:10]}" + (" ..." if len(dup_ms) > 10 else ""))
    if dup_sp:
        warnings.append(f"Duplicate spell ids: {dup_sp[:10]}" + (" ..." if len(dup_sp) > 10 else ""))
    if dup_cat:
        warnings.append(f"Duplicate category ids: {dup_cat[:10]}" + (" ..." if len(dup_cat) > 10 else ""))

    ms_set = set(i for i in ms_ids if i)
    sp_set = set(i for i in sp_ids if i)
    cat_set = set(i for i in cat_ids if i)

    # spells -> manuscripts
    for sp in spells:
        sid = sp.get("id")
        mid = sp.get("manuscript_id")
        if mid and mid not in ms_set:
            errors.append(f"Spell {sid} references missing manuscript_id={mid}")

    # spell_categories links
    for sc in spell_categories:
        sid = sc.get("spell_id")
        cid = sc.get("category_id")
        if sid and sid not in sp_set:
            errors.append(f"spell_categories references missing spell_id={sid}")
        if cid and cid not in cat_set:
            errors.append(f"spell_categories references missing category_id={cid}")

    # categories parent_id existence + build parent map
    parent_by_id = {}
    for c in categories:
        cid = c.get("id")
        if not cid:
            continue
        pid = (c.get("parent_id") or "").strip() or None
        parent_by_id[cid] = pid
        if pid and pid not in cat_set:
            warnings.append(f"Category {cid} has parent_id={pid} which does not exist")

    # ---- NEW: cycle detection in category parent graph ----
    done = set()
    for start in parent_by_id.keys():
        if start in done:
            continue

        path = []
        pos = {}  # cat_id -> index in path
        cur = start

        while cur:
            if cur in pos:
                cycle = path[pos[cur]:] + [cur]
                errors.append("Category cycle detected: " + " -> ".join(cycle))
                break

            if cur in done:
                break

            pos[cur] = len(path)
            path.append(cur)

            cur = parent_by_id.get(cur)

        done.update(path)

    return errors, warnings