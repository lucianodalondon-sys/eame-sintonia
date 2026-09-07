#!/usr/bin/env python3
"""Applies the corrections the six red-team lenses forced. Kept so each one is auditable."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))

# ── 1. di_observe: the era rule, the year-boundary window, consecutive-window checking ──
p = os.path.join(HERE, "di_observe.py")
s = open(p, encoding="utf-8").read()

s = s.replace(
    '    "MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE": 8,   # groves shared with a baseline season\n}',
    '    "MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE": 8,   # groves shared with a baseline season\n'
    '    "STALE_AFTER_DAYS": 14,          # p90 of grove revisit intervals is 9 days, p99 is 21\n}\n\n'
    '# The season from which the source serves percentages instead of counts. Declared,\n'
    '# evidenced in the semantic sheet CORRECTION_LOG, and emitted in every cell.\n'
    'ERA_PERCENT_FROM = 2020')

s = s.replace('''        c = v["measurements"][metric]["value"]
        t = v["measurements"]["SAMPLE_SIZE / DENOMINATOR"]["value"]
        if c is None or t is None:
            excluded += 1
            continue
        num += c
        den += t''',
'''        c = v["measurements"][metric]["value"]
        t = v["measurements"]["SAMPLE_SIZE / DENOMINATOR"]["value"]
        if c is None or t is None:
            excluded += 1
            continue
        # THE ERA RULE. From 2020 the source's own SQL already divides by tot and multiplies
        # by 100, so the served value IS the percentage. Before 2020 it is a count of drupes.
        # Dividing twice was this engine's central error; see the sheet's CORRECTION_LOG.
        # Both eras are converted to infested drupes so the two can be pooled at all.
        if d.year >= ERA_PERCENT_FROM:
            c = c * t / 100.0
        num += c
        den += t''')

# the year-boundary window: shift the WHOLE window, not each endpoint independently
s = s.replace('''def _shift(d, y):
    try:
        return d.replace(year=y)
    except ValueError:                       # 29 Feb -> 28 Feb, declared
        return d.replace(year=y, day=28)''',
'''def _shift(d, y):
    try:
        return d.replace(year=y)
    except ValueError:                       # 29 Feb -> 28 Feb, declared
        return d.replace(year=y, day=28)


def _shift_window(lo, hi, y):
    """Move a whole window into season y, keeping its LENGTH.

    Shifting the two endpoints independently is wrong whenever the window crosses 31 December:
    it produces an interval of NEGATIVE length that no row can fall inside, so the baseline
    silently empties and the printed reason blames grove rotation. An independent time lens
    measured it firing on 27 of 365 as_of dates and demonstrated it on a synthetic year-round
    case: 0 of 8 baseline seasons on 15 January against 8 of 8 on 28 January, identical data.
    Unreachable on the olive archive - December and January together hold 7 of 79,251 rows -
    and fatal for any crop that is scouted through the winter."""
    nhi = _shift(hi, y)
    return nhi - (hi - lo), nhi''')

s = s.replace('        b = pooled(visits, _shift(lo, y), _shift(hi, y), province, metric)',
              '        blo, bhi = _shift_window(lo, hi, y)\n'
              '        b = pooled(visits, blo, bhi, province, metric)')
s = s.replace('''            b_all = pooled(visits, _shift(lo, y), _shift(hi, y), province, metric)''',
              '''            blo, bhi = _shift_window(lo, hi, y)
            b_all = pooled(visits, blo, bhi, province, metric)''')
s = s.replace('''            then = pooled(visits, _shift(lo, y), _shift(hi, y), province, metric,
                          only_sites=shared)''',
              '''            then = pooled(visits, blo, bhi, province, metric, only_sites=shared)''')

# the trend must PROVE its windows are consecutive, not assert it in prose
s = s.replace('''    pts.reverse()
    if len(pts) < P["TREND_MIN_WINDOWS"]:''',
'''    pts.reverse()
    # "N consecutive windows" was asserted in the sentence and never checked. An independent
    # time lens built a case where the printed sentence claimed three consecutive windows while
    # the ends were 56 and 28 days apart and the deleted middle window held the highest value
    # of the four. The check is now made, and a gap refuses the direction.
    ends = [dt.date.fromisoformat(x["window_end"]) for x in pts]
    consecutive = all((b - a).days == P["WINDOW_DAYS"] for a, b in zip(ends, ends[1:]))
    if not consecutive:
        ana["observed_trend"] = "UNKNOWN"
        ana["observed_trend_reason"] = (
            f"the usable windows are not consecutive: their ends are "
            f"{[e.isoformat() for e in ends]}, which are not "
            f"{P['WINDOW_DAYS']} days apart. No direction is named from a series with a hole "
            f"in it.")
        ana["observed_trend_points"] = pts
        pts = []
    if len(pts) < P["TREND_MIN_WINDOWS"]:''')

# publish the age of the data
s = s.replace('''    obs["source_band"] = di_core.band_for(sheet, obs.get("value_pct"))''',
'''    obs["source_band"] = di_core.band_for(sheet, obs.get("value_pct"))
    # How old is this? The window is 28 days, so a silent archive publishes nothing after 28
    # days - but at 21 days stale it still publishes with the age never shown. Median grove
    # revisit is 7 days, p90 9, p99 21, so 14 is the declared alarm.
    if obs.get("last_observation"):
        age = (as_of - dt.date.fromisoformat(obs["last_observation"])).days
        obs["data_age_days"] = age
        obs["data_is_stale"] = age > P["STALE_AFTER_DAYS"]
        obs["stale_after_days"] = P["STALE_AFTER_DAYS"]
    else:
        obs["data_age_days"] = None
        obs["data_is_stale"] = None''')
open(p, "w", encoding="utf-8").write(s)
print("di_observe: era rule, whole-window shift, consecutive check, data age")

# ── 2. di_refresh: a payload must be COMPLETE, not merely well formed ──────────────────
p2 = os.path.join(HERE, "di_refresh.py")
r = open(p2, encoding="utf-8").read()
r = r.replace('NO_UPDATE, NEW_OBSERVATIONS = "NO_UPDATE", "NEW_OBSERVATIONS"',
              'NO_UPDATE, NEW_OBSERVATIONS = "NO_UPDATE", "NEW_OBSERVATIONS"\n'
              'SOURCE_INCOMPLETE = "SOURCE_INCOMPLETE"')
r = r.replace('''    status, detail, rows, filt = validate(r["body"])
    rec["detail"] = detail''',
'''    status, detail, rows, filt = validate(r["body"])
    rec["detail"] = detail

    # A payload can be 200 OK, ok:true, well formed AND INCOMPLETE. An independent time lens
    # fed back 2,245 of 2,928 real rows - a truncated but perfectly valid response - and it was
    # promoted: Siena went from 0.6909% on 18,383 drupes to 0.0% on 13,200, band green to
    # "Nessuna Infestazione", and it stayed publishable. Nothing refused it, because validate()
    # only ever looked at the payload and never at what canonical already held.
    if status == "OK" and os.path.exists(canon_path):
        try:
            prev_rows = json.loads(open(canon_path, "rb").read().decode("utf-8"))
        except Exception:
            prev_rows = []
        prev_n = len(prev_rows)
        prev_dates = [x.get("date") for x in prev_rows if isinstance(x, dict) and x.get("date")]
        prev_max = max(prev_dates) if prev_dates else None
        new_max = detail.get("latest_observation")
        lost = prev_n - detail["n_rows"]
        if lost > 0 or (prev_max and new_max and new_max < prev_max):
            status = SOURCE_INCOMPLETE
            detail = {"reason": "the response holds fewer rows, or an older newest "
                                "observation, than the copy already on disk",
                      "rows_now": detail["n_rows"], "rows_in_canonical": prev_n,
                      "rows_lost": lost,
                      "newest_now": new_max, "newest_in_canonical": prev_max}
            rec["detail"] = detail''')
open(p2, "w", encoding="utf-8").write(r)
print("di_refresh: completeness check against canonical")
