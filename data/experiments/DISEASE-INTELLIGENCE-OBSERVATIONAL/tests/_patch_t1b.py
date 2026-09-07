#!/usr/bin/env python3
"""t1 condition A, restructured.

The determinism lens was right that the first version could not fail. My first repair
over-corrected: it replaced the shipped engine with a mutant, so the test measured the mutant
and reported NOT_DETERMINISTIC about a thing that is not shipped.

The right shape is the one already used for the gates - the claim AND its executioner:

  A_SHIPPED  the engine exactly as it runs, with its own sort, over 8 file orders
             -> must give ONE result, or the claim is false
  A_CONTROL  the same 8 orders with the loader's sort removed
             -> must give MORE THAN ONE, or condition A is vacuous and proves nothing

and, because the two can differ for an uninteresting reason, the ANSWER (the published rates
and states) is compared separately from the RECEIPT (the whole payload including the order in
which provenance lists its files).
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "t1_determinism.py")
s = open(p, encoding="utf-8").read()

s = s.replace('''def with_order(order, seed=None):
    """CORRECTED after a determinism lens showed the first version could not fail: it
    permuted glob.glob, and _read_variable calls sorted() on the result in the same
    expression, so the permutation never reached the loader. The loader's own sort is now
    neutralised for the duration of the run, which is exactly the state the previous engine
    was permanently in, and the permutation is what the loader actually sees."""
    if order == "asc":''',
'''def with_order(order, seed=None, remove_the_loaders_sort=False):
    """Permute the file order. With remove_the_loaders_sort=True the loader's own sort is
    neutralised, which is the state the previous engine was permanently in - that variant is
    the CONTROL that proves this condition is not vacuous."""
    if order == "asc":''')
s = s.replace('''    di_core.glob.glob = f
    # neutralise the loader's own sort so the order above is the order it reads in
    di_core.sorted = lambda it, **kw: list(it)''',
'''    di_core.glob.glob = f
    if remove_the_loaders_sort:
        di_core.sorted = lambda it, **kw: list(it)''')

s = s.replace('''def run_once():''',
'''def answer_only(payload):
    """The published numbers, with nothing about how the files were listed."""
    keep = ("province", "as_of")
    out = []
    for c in payload["cells"]:
        o, a = c["observation"], c["analysis"]
        out.append({k: c.get(k) for k in keep} | {
            "metric": o.get("metric"), "value_pct": o.get("value_pct"),
            "n_visits": o.get("n_visits"), "n_sites": o.get("n_sites"),
            "drupes": o.get("drupes_sampled"), "infested": o.get("infested_drupes"),
            "hist": a.get("historical_state"), "matched": a.get("matched_panel_seasons"),
            "trend": a.get("observed_trend")})
    return hashlib.sha256(json.dumps(out, sort_keys=True, default=str).encode()).hexdigest()


def run_once():''')

s = s.replace('''    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest(), payload''',
'''    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest(), payload''')

s = s.replace('''    results = {}
    conditions = [("asc", None), ("desc", None)] + [("shuffle", s) for s in range(1, 7)]
    for order, seed in conditions:
        with_order(order, seed)
        try:
            h, payload = run_once()
        finally:
            di_core.glob.glob = REAL_GLOB
            if hasattr(di_core, "sorted"):
                del di_core.sorted
        name = order if seed is None else f"{order}:{seed}"
        results[name] = h
    di_core.glob.glob = REAL_GLOB''',
'''    conditions = [("asc", None), ("desc", None)] + [("shuffle", s) for s in range(1, 7)]
    results, answers, ctl_results, ctl_answers = {}, {}, {}, {}
    for strip, res, ans in ((False, results, answers), (True, ctl_results, ctl_answers)):
        for order, seed in conditions:
            with_order(order, seed, remove_the_loaders_sort=strip)
            try:
                h, payload = run_once()
                a = answer_only(payload)
            finally:
                di_core.glob.glob = REAL_GLOB
                if hasattr(di_core, "sorted"):
                    del di_core.sorted
            name = order if seed is None else f"{order}:{seed}"
            res[name] = h
            ans[name] = a
    di_core.glob.glob = REAL_GLOB''')

s = s.replace('''    distinct = sorted(set(results.values()))''',
'''    distinct = sorted(set(results.values()))
    d_ans = sorted(set(answers.values()))
    d_ctl = sorted(set(ctl_results.values()))
    d_ctl_ans = sorted(set(ctl_answers.values()))''')

s = s.replace('''           "A_FILE_ORDER": {"per_condition": results,
                            "distinct_results": len(distinct),
                            "DETERMINISTIC": len(distinct) == 1},''',
'''           "A_FILE_ORDER_SHIPPED": {
               "per_condition": results,
               "distinct_full_payloads": len(distinct),
               "distinct_published_answers": len(d_ans),
               "DETERMINISTIC": len(distinct) == 1},
           "A_CONTROL_WITH_THE_LOADERS_SORT_REMOVED": {
               "per_condition": ctl_results,
               "distinct_full_payloads": len(d_ctl),
               "distinct_published_answers": len(d_ctl_ans),
               "CONDITION_A_IS_NOT_VACUOUS": len(d_ctl) > 1,
               "READ": ("if this row shows 1 as well, condition A proves nothing, because the "
                        "loader's own sort would be hiding the permutation. It shows "
                        f"{len(d_ctl)} distinct payloads and {len(d_ctl_ans)} distinct "
                        "published answers - so the receipt moves with the file order and the "
                        "ANSWER does not, because the visit key is unique and a collision "
                        "raises. The sort makes the receipt reproducible; the key makes the "
                        "answer reproducible. Both are needed and they are different claims.")},''')

s = s.replace('''    out["VERDICT"] = ("DETERMINISTIC" if (out["A_FILE_ORDER"]["DETERMINISTIC"]
                                          and out["C_SAME_PROCESS_TWICE"]["IDENTICAL"]
                                          and collision["RAISED"]) else "NOT_DETERMINISTIC")''',
'''    out["VERDICT"] = ("DETERMINISTIC" if (out["A_FILE_ORDER_SHIPPED"]["DETERMINISTIC"]
                                          and out["A_CONTROL_WITH_THE_LOADERS_SORT_REMOVED"][
                                              "CONDITION_A_IS_NOT_VACUOUS"]
                                          and out["C_SAME_PROCESS_TWICE"]["IDENTICAL"]
                                          and collision["RAISED"]) else "NOT_DETERMINISTIC")''')

s = s.replace('''    for k, v in results.items():
        print(f"  {k:12s} {v}")
    print(f"\\n  distinct results over {len(results)} file orders: {len(distinct)}")''',
'''    for k, v in results.items():
        print(f"  {k:12s} {v}")
    print(f"\\n  SHIPPED : distinct payloads over {len(results)} file orders = {len(distinct)}"
          f" | distinct published answers = {len(d_ans)}")
    print(f"  CONTROL (loader's sort removed): distinct payloads = {len(d_ctl)}"
          f" | distinct published answers = {len(d_ctl_ans)}")''')
open(p, "w", encoding="utf-8").write(s)
print("t1 condition A restructured: claim plus control")
