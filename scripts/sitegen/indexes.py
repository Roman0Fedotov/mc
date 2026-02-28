from collections import defaultdict

def build_indexes(manuscripts, spells, spell_categories):
    manuscript_by_id = {ms["id"]: ms for ms in manuscripts}

    spell_by_id = {sp["id"]: sp for sp in spells if sp.get("id")}

    spells_by_ms_id = defaultdict(list)
    for sp in spells:
        mid = sp.get("manuscript_id")
        if mid:
            spells_by_ms_id[mid].append(sp)

    cats_by_spell_id = defaultdict(list)
    spell_ids_by_cat_id = defaultdict(list)
    for sc in spell_categories:
        sid = sc.get("spell_id")
        cid = sc.get("category_id")
        if sid and cid:
            cats_by_spell_id[sid].append(cid)
            spell_ids_by_cat_id[cid].append(sid)

    # count spells per category (dedupe защитит от случайных дублей связей)
    spell_count_by_category = {cid: len(set(sids)) for cid, sids in spell_ids_by_cat_id.items()}

    return {
        "manuscript_by_id": manuscript_by_id,
        "spell_by_id": spell_by_id,
        "spells_by_ms_id": spells_by_ms_id,
        "cats_by_spell_id": cats_by_spell_id,
        "spell_ids_by_cat_id": spell_ids_by_cat_id,
        "spell_count_by_category": spell_count_by_category,
    }