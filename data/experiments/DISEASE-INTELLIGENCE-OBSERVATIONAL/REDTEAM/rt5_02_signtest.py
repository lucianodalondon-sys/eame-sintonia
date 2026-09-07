#!/usr/bin/env python3
"""RT5 · accusation 2. What is the null of "lower than 14 of 14"?

Three nulls, because the tool declares none:

  A. NAIVE SIGN TEST. 14 independent coin flips: p = 2 * 0.5^14. This is the null
     the phrase "lower than 14 of 14" invites a reader to imagine. It is wrong,
     because the 14 comparisons share one "now".
  B. EXCHANGEABLE-SEASON RANK. If this season were an exchangeable draw from the
     same population as its k matched prior seasons, its rank among the k+1 is
     uniform. P(it is the lowest of k+1) = 1/(k+1). This is the honest null for
     "one new observation against k old ones".
  C. GROVE CLUSTER BOOTSTRAP. Resample the shared groves with replacement,
     recompute every matched rate, re-run the tool's own counting rule, and read
     off how often each verdict comes back. Drupes inside one grove are not
     independent, so the grove is the resampling unit, not the drupe.

Also reported: per-season two-proportion tests on the raw drupe counts, which is
the magnitude-aware comparison the counting rule throws away.
"""
import os, sys, json, math, random, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L

AS_OF = dt.date(2026, 9, 6)
idx, raw = L.get_index("ACTIVE_INFESTATION_COUNT")
P = L.PARAMS
random.seed(20260906)


def logcomb(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def binom_tail_at_least(k, n, p=0.5):
    return sum(math.exp(logcomb(n, i) + i * math.log(p) + (n - i) * math.log(1 - p))
               for i in range(k, n + 1))


def norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def two_prop_z(x1, n1, x2, n2):
    """Unpooled-free two-proportion z, with the caveat printed below it."""
    if n1 == 0 or n2 == 0:
        return None, None
    p1, p2 = x1 / n1, x2 / n2
    p = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return None, None
    z = (p1 - p2) / se
    return z, 2 * (1 - norm_cdf(abs(z)))


def matched_detail(prov):
    lo, hi = L.win(AS_OF, P["WINDOW_DAYS"])
    cur = idx.pooled(prov, lo, hi, as_of=AS_OF)
    rows = []
    for y in range(2006, AS_OF.year):
        b_all = idx.pooled(prov, L.shift(lo, y), L.shift(hi, y), as_of=AS_OF)
        if not b_all:
            continue
        shared = cur["sites"] & b_all["sites"]
        if len(shared) < P["MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE"]:
            continue
        now = idx.pooled(prov, lo, hi, only_sites=shared, as_of=AS_OF)
        then = idx.pooled(prov, L.shift(lo, y), L.shift(hi, y), only_sites=shared, as_of=AS_OF)
        if not now or not then or not now["drupes_sampled"] or not then["drupes_sampled"]:
            continue
        rows.append({"season": y, "shared": sorted(shared),
                     "n_shared": len(shared),
                     "now": now["rate_pct"], "then": then["rate_pct"],
                     "inf_now": now["infested_drupes"], "n_now": now["drupes_sampled"],
                     "inf_then": then["infested_drupes"], "n_then": then["drupes_sampled"]})
    return cur, rows


def bootstrap(prov, rows, cur, B=5000):
    """Resample GROVES with replacement inside each season's shared panel."""
    # build per-grove numerators/denominators once
    lo, hi = L.win(AS_OF, P["WINDOW_DAYS"])
    per_season = []
    for r in rows:
        shared = set(r["shared"])
        now = idx.pooled(prov, lo, hi, only_sites=shared, as_of=AS_OF)
        then = idx.pooled(prov, L.shift(lo, r["season"]), L.shift(hi, r["season"]),
                          only_sites=shared, as_of=AS_OF)
        groves = sorted(shared)
        per_season.append({
            "season": r["season"], "groves": groves,
            "nn": now["per_site_num"], "nd": now["per_site_den"],
            "tn": then["per_site_num"], "td": then["per_site_den"]})
    verdicts = {}
    lowers = []
    for _ in range(B):
        lower = higher = 0
        for s in per_season:
            g = s["groves"]
            pick = [g[random.randrange(len(g))] for _ in g]
            nn = sum(s["nn"].get(k, 0.0) for k in pick)
            nd = sum(s["nd"].get(k, 0.0) for k in pick)
            tn = sum(s["tn"].get(k, 0.0) for k in pick)
            td = sum(s["td"].get(k, 0.0) for k in pick)
            if not nd or not td:
                continue
            a, b = nn / nd, tn / td
            if a < b:
                lower += 1
            elif a > b:
                higher += 1
        n = len(per_season)
        lowers.append(lower)
        v = ("BELOW_HISTORICAL" if lower / n >= P["HIGH_PCTL"] else
             "ABOVE_HISTORICAL" if higher / n >= P["HIGH_PCTL"] else "TYPICAL")
        verdicts[v] = verdicts.get(v, 0) + 1
    return verdicts, lowers


out = {}
for prov in ("Firenze", "Siena", "Arezzo"):
    cur, rows = matched_detail(prov)
    k = len(rows)
    lower = sum(1 for r in rows if r["now"] < r["then"])
    higher = sum(1 for r in rows if r["now"] > r["then"])
    ties = k - lower - higher
    print(f"\n{'='*78}\n{prov}: pooled now {cur['rate_pct']}% "
          f"({cur['infested_drupes']} infested of {cur['drupes_sampled']} drupes, "
          f"{cur['n_visits']} visits, {cur['n_sites']} groves)")
    print(f"  matched seasons {k}; lower {lower}, higher {higher}, tied {ties}")
    print(f"  {'season':>6} {'shared':>6} {'now%':>8} {'then%':>8} {'now n/N':>14} "
          f"{'then n/N':>14} {'2-prop p':>10}")
    per = []
    for r in rows:
        z, p2 = two_prop_z(r["inf_now"], r["n_now"], r["inf_then"], r["n_then"])
        per.append({**{kk: r[kk] for kk in r if kk != "shared"}, "z": z, "p_two_prop": p2})
        print(f"  {r['season']:>6} {r['n_shared']:>6} {r['now']:>8} {r['then']:>8} "
              f"{f'{r[chr(39)+chr(39)] if False else r["inf_now"]}/{r["n_now"]}':>14} "
              f"{f'{r["inf_then"]}/{r["n_then"]}':>14} "
              f"{('%.2e' % p2) if p2 is not None else 'na':>10}")

    # A. naive sign test
    n_eff = lower + higher
    p_sign = 2 * binom_tail_at_least(max(lower, higher), n_eff, 0.5)
    p_sign = min(1.0, p_sign)
    # B. exchangeable rank
    # verdict fires when higher <= floor((1-HIGH_PCTL)*k); rank of "now" among k+1
    max_higher = 0
    while (k - max_higher) / k >= P["HIGH_PCTL"]:
        max_higher += 1
    max_higher -= 1
    p_rank = (max_higher + 1) / (k + 1)
    # C. bootstrap
    verd, lowers = bootstrap(prov, rows, cur)
    B = sum(verd.values())
    print(f"\n  NULL A  naive sign test, {max(lower,higher)} of {n_eff}: p = {p_sign:.3e}")
    print(f"          (assumes 14 independent pairs; they share one 'now', so this is wrong)")
    print(f"  NULL B  exchangeable-season rank: the rule fires when at most {max_higher} of "
          f"{k} prior seasons read higher,")
    print(f"          i.e. when this season ranks in the bottom {max_higher+1} of {k+1}. "
          f"Uniform rank => p = {max_higher+1}/{k+1} = {p_rank:.4f}")
    print(f"  NULL C  grove cluster bootstrap, B={B}: " +
          ", ".join(f"{kk} {vv} ({100*vv/B:.1f}%)" for kk, vv in sorted(verd.items())))
    print(f"          bootstrap 'lower' count: median {statistics.median(lowers)}, "
          f"2.5-97.5 pct [{sorted(lowers)[int(.025*B)]}, {sorted(lowers)[int(.975*B)]}] of {k}")
    out[prov] = {"rate_now_pct": cur["rate_pct"], "infested": cur["infested_drupes"],
                 "drupes": cur["drupes_sampled"], "n_visits": cur["n_visits"],
                 "n_groves": cur["n_sites"],
                 "matched_k": k, "lower": lower, "higher": higher, "ties": ties,
                 "per_season": per,
                 "p_naive_sign": p_sign, "p_exchangeable_rank": p_rank,
                 "max_higher_that_still_fires": max_higher,
                 "bootstrap": verd, "bootstrap_B": B,
                 "bootstrap_lower_median": statistics.median(lowers),
                 "bootstrap_lower_ci": [sorted(lowers)[int(.025*B)],
                                        sorted(lowers)[int(.975*B)]]}

json.dump(out, open(os.path.join(HERE, "rt5_02_signtest.json"), "w"), indent=1)
print("\nwrote rt5_02_signtest.json")
