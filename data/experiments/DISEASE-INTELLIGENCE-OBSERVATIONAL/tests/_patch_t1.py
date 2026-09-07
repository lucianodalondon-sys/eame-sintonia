#!/usr/bin/env python3
"""Repairs the two conditions of t1 that an independent determinism lens showed could not
fail, and the citation that pointed at a file which does not exist."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "t1_determinism.py")
s = open(p, encoding="utf-8").read()

# CONDITION A could not fail: it permuted glob.glob, and _read_variable re-sorts on the same
# line. The permutation must survive into the loader, so the sort itself is removed for the
# duration of the run - which is the state the previous engine was permanently in.
s = s.replace('''def with_order(order, seed=None):
    if order == "asc":
        f = lambda p, **k: sorted(REAL_GLOB(p, **k))
    elif order == "desc":
        f = lambda p, **k: sorted(REAL_GLOB(p, **k), reverse=True)
    else:
        # ONE fixed permutation, decided by the seed and the file name, applied to every call
        f = lambda p, **k: sorted(
            REAL_GLOB(p, **k),
            key=lambda x: hashlib.md5(f"{seed}|{os.path.basename(x)}".encode()).hexdigest())
    di_core.glob.glob = f''',
'''REAL_SORTED = sorted


def with_order(order, seed=None):
    """CORRECTED after a determinism lens showed the first version could not fail: it
    permuted glob.glob, and _read_variable calls sorted() on the result in the same
    expression, so the permutation never reached the loader. The loader's own sort is now
    neutralised for the duration of the run, which is exactly the state the previous engine
    was permanently in, and the permutation is what the loader actually sees."""
    if order == "asc":
        f = lambda p, **k: REAL_SORTED(REAL_GLOB(p, **k))
    elif order == "desc":
        f = lambda p, **k: REAL_SORTED(REAL_GLOB(p, **k), reverse=True)
    else:
        f = lambda p, **k: REAL_SORTED(
            REAL_GLOB(p, **k),
            key=lambda x: hashlib.md5(f"{seed}|{os.path.basename(x)}".encode()).hexdigest())
    di_core.glob.glob = f
    # neutralise the loader's own sort so the order above is the order it reads in
    di_core.sorted = lambda it, **kw: list(it)''')

s = s.replace('''    for order, seed in conditions:
        with_order(order, seed)
        h, payload = run_once()
        name = order if seed is None else f"{order}:{seed}"
        results[name] = h
    di_core.glob.glob = REAL_GLOB''',
'''    for order, seed in conditions:
        with_order(order, seed)
        try:
            h, payload = run_once()
        finally:
            di_core.glob.glob = REAL_GLOB
            if hasattr(di_core, "sorted"):
                del di_core.sorted
        name = order if seed is None else f"{order}:{seed}"
        results[name] = h
    di_core.glob.glob = REAL_GLOB''')

# CONDITION D never called the loader: it grepped the source for a string and then
# re-implemented the guard in the test body. It now tampers a real copy and calls the loader.
old_d = s[s.index('    # D — an injected collision must RAISE'):s.index('    distinct = sorted(')]
new_d = '''    # D — an injected collision must RAISE.
    #
    # CORRECTED. The first version defined a wrapper it never invoked, grepped the source for
    # the string "JoinConflict", then re-implemented the guard inside the test and raised its
    # own exception. It proved that the test could raise, not that the loader does. It now
    # builds a real case on disk with a duplicated visit key carrying a different value, and
    # calls the shipped loader on it.
    import shutil, tempfile
    collision = {"RAISED": None, "message": None, "method": "the shipped loader, on a real "
                                                            "case with a duplicated key"}
    lab = os.path.join(HERE, "_collision_lab")
    if os.path.exists(lab):
        shutil.rmtree(lab)
    os.makedirs(os.path.join(lab, "RAW"))
    sheet = di_core.load_sheet()
    src_idx = json.load(open(os.path.join(CASE, "collection_index.json"), encoding="utf-8"))
    json.dump({"api": src_idx["api"], "crop": 2, "schema": 1, "requests": [],
               "codes": src_idx.get("codes"), "vars": src_idx.get("vars")},
              open(os.path.join(lab, "collection_index.json"), "w", encoding="utf-8"))
    rows = json.load(open(os.path.join(CASE, "RAW", "c2_s1_v-1001_2026.json"),
                          encoding="utf-8"))[:50]
    dup = dict(rows[0])
    dup["val"] = str((di_core._num(rows[0].get("val")) or 0) + 7)     # same key, other value
    open(os.path.join(lab, "RAW", "c2_s1_v-1001_2026.json"), "wb").write(
        json.dumps(rows, ensure_ascii=False).encode("utf-8"))
    open(os.path.join(lab, "RAW", "c2_s1_v-1001_2027.json"), "wb").write(
        json.dumps([dup], ensure_ascii=False).encode("utf-8"))
    try:
        di_core._read_variable(lab, -1001, sheet)
        collision["RAISED"] = False
    except di_core.JoinConflict as e:
        collision["RAISED"] = True
        collision["message"] = str(e)[:200]
    shutil.rmtree(lab, ignore_errors=True)

'''
s = s.replace(old_d, new_d)

s = s.replace('"B_HASH_SEED": "varied across processes by t1_determinism.sh; see its output",',
              '"B_HASH_SEED": {"script": "t1b_hashseed.py (this directory)",\n'
              '                           "NOTE": "the first version of this file cited '
              't1_determinism.sh, which does not exist in any commit. The property was true '
              'and the citation was not."},')
s = s.replace('''    out = {"AS_OF": AS_OF.isoformat(), "METRICS": METRICS,''',
'''    out = {"AS_OF": AS_OF.isoformat(), "METRICS": METRICS,
           "RECEIPT": di_core.code_fingerprint(),''')
open(p, "w", encoding="utf-8").write(s)
print("t1 repaired: condition A can fail, condition D calls the loader, receipt names the code")
