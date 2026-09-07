#!/usr/bin/env python3
"""RT4-05  Field-by-field diff of the report the repository PUBLISHES (the committed
OUT/report_ACTIVE_INFESTATION_COUNT_2026-09-06.json) against the report a FRESH CLONE of the
same commit PRODUCES by running the documented command.

usage:  py rt4_05_freshclone_diff.py <committed.json> <regenerated.json>

Walks both trees and reports every leaf that differs, with its full path, both values, and -
for numbers - the absolute difference. No sampling: every leaf.
"""
import sys, json, collections


def leaves(o, path=""):
    if isinstance(o, dict):
        for k in o:
            yield from leaves(o[k], f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, o


def main(pa, pb):
    A = json.load(open(pa, encoding="utf-8"))
    B = json.load(open(pb, encoding="utf-8"))
    la, lb = dict(leaves(A)), dict(leaves(B))
    only_a = sorted(set(la) - set(lb))
    only_b = sorted(set(lb) - set(la))
    diff = []
    for k in sorted(set(la) & set(lb)):
        if la[k] != lb[k]:
            d = None
            if isinstance(la[k], (int, float)) and isinstance(lb[k], (int, float)) \
                    and not isinstance(la[k], bool):
                d = lb[k] - la[k]
            diff.append({"path": k, "committed": la[k], "regenerated": lb[k], "delta": d})
    byhead = collections.Counter(k["path"].split("[")[0] for k in diff)
    out = {"committed_file": pa, "regenerated_file": pb,
           "n_leaves_committed": len(la), "n_leaves_regenerated": len(lb),
           "n_leaves_present_only_in_committed": len(only_a),
           "n_leaves_present_only_in_regenerated": len(only_b),
           "leaves_only_in_committed_sample": only_a[:25],
           "leaves_only_in_regenerated_sample": only_b[:25],
           "n_shared_leaves_that_DIFFER": len(diff),
           "differing_leaves_by_field": dict(byhead.most_common(40)),
           "differing_leaves": diff[:400],
           "IDENTICAL": not (only_a or only_b or diff)}
    print(json.dumps({k: v for k, v in out.items() if k != "differing_leaves"},
                     indent=1, default=str)[:6000])
    json.dump(out, open(sys.argv[3], "w", encoding="utf-8"), indent=1, default=str)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
