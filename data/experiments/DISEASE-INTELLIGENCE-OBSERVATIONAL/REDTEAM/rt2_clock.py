#!/usr/bin/env python3
"""
RT2 / A1 — IS THERE A WALL CLOCK ANYWHERE ON THE PATH TO A PUBLISHED NUMBER?

Method: replace the `datetime` and `time` modules with shims whose "what time is it now"
entry points RAISE. date.fromisoformat, date(), timedelta and every other pure-arithmetic
entry point keep working. Then run the whole analysis pipeline. If any published number
needs the wall clock, the run dies.

Then run the refresh path under the same armed clock, to locate exactly where the clock IS
used and what it writes.
"""
import os, sys, json, types, datetime as _real_dt, time as _real_time

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))


class ClockArmed(Exception):
    pass


def _boom(*a, **k):
    raise ClockArmed("the wall clock was read on a path that claims not to read it")


class _Date(_real_dt.date):
    today = staticmethod(_boom)


class _DateTime(_real_dt.datetime):
    now = staticmethod(_boom)
    utcnow = staticmethod(_boom)
    today = staticmethod(_boom)
    fromtimestamp = staticmethod(_boom)
    utcfromtimestamp = staticmethod(_boom)


def armed_datetime():
    m = types.ModuleType("datetime")
    for n in dir(_real_dt):
        if not n.startswith("__"):
            setattr(m, n, getattr(_real_dt, n))
    m.date = _Date
    m.datetime = _DateTime
    return m


def armed_time():
    m = types.ModuleType("time")
    for n in dir(_real_time):
        if not n.startswith("__"):
            setattr(m, n, getattr(_real_time, n))
    m.time = _boom
    m.time_ns = _boom
    m.localtime = _boom
    m.gmtime = _boom
    return m


def main():
    out = {}
    sys.modules["datetime"] = armed_datetime()
    sys.modules["time"] = armed_time()
    sys.path.insert(0, ENGINE)
    import datetime as dt          # the armed one
    import di_core, di_observe, di_adama, di_render

    # sanity: the arming really works
    try:
        dt.date.today()
        out["ARMING_WORKS"] = False
    except ClockArmed:
        out["ARMING_WORKS"] = True

    CASE = os.path.abspath(os.path.join(ENGINE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                        "CASES", "OLIVO-BACTROCERA-TOSCANA"))
    as_of = _real_dt.date(2026, 9, 6)
    as_of = dt.date.fromisoformat("2026-09-06")

    try:
        sheet = di_core.load_sheet()
        loaded = di_core.load_visits(CASE, sheet, as_of)
        provs = sorted({v["province"] for v in loaded["visits"] if v["province"]})
        adama = di_adama.relevance("Olive", "Olive Fruit Fly")
        cells = []
        for p in provs:
            c = di_observe.cell(loaded["visits"], sheet, p, "ACTIVE_INFESTATION_COUNT", as_of)
            c["adama"] = adama
            c["attention"] = di_adama.attention_class(c, adama)
            cells.append(c)
        txt = di_render.render_region(cells, adama) + "".join(
            di_render.render_province(c, adama, c["attention"]) for c in cells)
        out["ANALYSIS_PATH_WITH_THE_CLOCK_ARMED"] = "COMPLETED"
        out["n_provinces"] = len(cells)
        out["n_visits_loaded"] = loaded["n_visits"]
        out["rendered_chars"] = len(txt)
        out["published_values_pct"] = {c["province"]: c["observation"]["value_pct"]
                                       for c in cells}
    except ClockArmed as e:
        out["ANALYSIS_PATH_WITH_THE_CLOCK_ARMED"] = f"DIED: {e}"
    except Exception as e:
        out["ANALYSIS_PATH_WITH_THE_CLOCK_ARMED"] = f"OTHER_ERROR: {type(e).__name__}: {e}"

    # now the refresh path, same armed clock
    import di_refresh
    try:
        rec = di_refresh.refresh_one(
            os.path.join(HERE, "_nonexistent_canon"), os.path.join(HERE, "_rt2_stage"),
            2, 1, -1002, 2026,
            _transport=lambda url: json.dumps(
                {"data": {"ok": True, "data": [{"date": "2026-09-04", "val": "1",
                                                "id_field": 1}]}}).encode("utf-8"))
        out["REFRESH_PATH_WITH_THE_CLOCK_ARMED"] = "COMPLETED (no clock read?)"
        out["refresh_record"] = rec
    except ClockArmed as e:
        out["REFRESH_PATH_WITH_THE_CLOCK_ARMED"] = f"DIED: {e}"
    except Exception as e:
        out["REFRESH_PATH_WITH_THE_CLOCK_ARMED"] = f"OTHER: {type(e).__name__}: {e}"

    json.dump(out, open(os.path.join(HERE, "rt2_clock.json"), "w", encoding="utf-8"),
              indent=1, default=str)
    print(json.dumps(out, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
