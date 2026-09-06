#!/usr/bin/env python3
"""RT3-E1. AS_OF is claimed to be an input, never the clock. Prove it hostilely.

Three layers:
  1. AST scan of every .py in ENGINE/ and CASES/ for any expression that can yield the
     current time, and for every module-level or default-argument date literal.
  2. RUNTIME trap: replace datetime.date.today, datetime.datetime.now/utcnow/today,
     time.time and time.localtime with functions that RAISE, then run the full publication
     path (load_rows -> current_pressure -> hindcast -> sensitivity). If any published number
     depends on the clock, this raises.
  3. FROZEN-CLOCK equivalence: run the publication path twice under two wildly different
     fake system clocks and compare the outputs byte for byte.
"""
import sys, os, ast, json, io, datetime as dt, time, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
CAS = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
OUT = {}

CLOCKY = {"now", "utcnow", "today", "time", "localtime", "gmtime", "monotonic",
          "perf_counter", "time_ns", "fromtimestamp", "getmtime", "getctime", "getatime",
          "stat", "date_today"}


def scan(path):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    hits, literals = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if name in CLOCKY:
                hits.append({"line": node.lineno, "call": ast.unparse(node)[:90]})
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "date" and ast.unparse(node.func).endswith("dt.date"):
            literals.append({"line": node.lineno, "expr": ast.unparse(node)[:70]})
    # default arguments that are date literals
    defaults = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for a, dflt in zip(node.args.args[-len(node.args.defaults):] if node.args.defaults else [],
                               node.args.defaults):
                s = ast.unparse(dflt)
                if "date(" in s or "now(" in s or "today(" in s:
                    defaults.append({"func": node.name, "line": node.lineno,
                                     "arg": a.arg, "default": s})
    return hits, literals, defaults


files = sorted([os.path.join(ENG, f) for f in os.listdir(ENG) if f.endswith(".py")] +
               [os.path.join(CAS, f) for f in os.listdir(CAS) if f.endswith(".py")])
ast_res = {}
for p in files:
    h, l, d = scan(p)
    ast_res[os.path.relpath(p, os.path.dirname(ENG)).replace("\\", "/")] = {
        "CLOCK_CALLS": h, "HARDCODED_DATE_LITERALS": l, "DATE_DEFAULT_ARGUMENTS": d}
OUT["AST_SCAN"] = {"N_FILES_SCANNED": len(files), "PER_FILE": ast_res,
                   "TOTAL_CLOCK_CALLS": sum(len(v["CLOCK_CALLS"]) for v in ast_res.values()),
                   "FILES_WITH_CLOCK_CALLS": [k for k, v in ast_res.items() if v["CLOCK_CALLS"]]}

# ---------------------------------------------------------------- 2. runtime trap
sys.path.insert(0, ENG)
sys.path.insert(0, CAS)
import current_pressure as cp

AS_OF = dt.date(2026, 9, 6)
CASE = os.path.join(CAS, "VITE-OIDIO-TOSCANA")
VAR = 39


class Boom(Exception):
    pass


class TrapDate(dt.date):
    @classmethod
    def today(cls):
        raise Boom("date.today() reached inside the publication path")


class TrapDateTime(dt.datetime):
    @classmethod
    def now(cls, tz=None):
        raise Boom("datetime.now() reached inside the publication path")

    @classmethod
    def utcnow(cls):
        raise Boom("datetime.utcnow() reached inside the publication path")

    @classmethod
    def today(cls):
        raise Boom("datetime.today() reached inside the publication path")


def trapped_time():
    raise Boom("time.time() reached inside the publication path")


saved = (dt.date, dt.datetime, time.time, time.localtime)
trap = {}
try:
    cp.dt.date, cp.dt.datetime = TrapDate, TrapDateTime
    time.time = trapped_time
    time.localtime = lambda *a: (_ for _ in ()).throw(Boom("time.localtime() reached"))
    steps = {}
    try:
        pre = cp.load_rows(CASE, VAR)
        steps["load_rows"] = "OK"
    except Boom as e:
        steps["load_rows"] = f"CLOCK REACHED: {e}"; pre = None
    if pre:
        for label, fn in (("current_pressure", lambda: cp.current_pressure(CASE, VAR, AS_OF, _pre=pre)),
                          ("hindcast", lambda: cp.hindcast(CASE, VAR, 9, 6, range(2015, 2027))),
                          ("sensitivity", lambda: cp.sensitivity(CASE, VAR, AS_OF))):
            try:
                fn(); steps[label] = "OK"
            except Boom as e:
                steps[label] = f"CLOCK REACHED: {e}"
            except Exception as e:
                steps[label] = f"other error: {type(e).__name__}: {str(e)[:120]}"
    trap = steps
finally:
    cp.dt.date, cp.dt.datetime = saved[0], saved[1]
    time.time, time.localtime = saved[2], saved[3]
OUT["RUNTIME_CLOCK_TRAP"] = {
    "STEPS": trap,
    "VERDICT": ("NO CLOCK REACHES A PUBLISHED NUMBER"
                if all(v == "OK" for v in trap.values()) else "CLOCK REACHED"),
}

# ---------------------------------------------------------------- 3. frozen-clock equivalence
pre = cp.load_rows(CASE, VAR)
runs = {}
for tag, fake in (("clock_2026", dt.date(2026, 9, 6)), ("clock_1999", dt.date(1999, 1, 1)),
                  ("clock_2099", dt.date(2099, 12, 31))):
    class FakeDate(dt.date):
        _f = fake

        @classmethod
        def today(cls):
            return cls._f
    cp.dt.date = FakeDate
    try:
        r = cp.current_pressure(CASE, VAR, AS_OF, _pre=pre)
        runs[tag] = json.dumps(r, sort_keys=True, default=str)
    finally:
        cp.dt.date = saved[0]
OUT["FROZEN_CLOCK_EQUIVALENCE"] = {
    "SYSTEM_CLOCKS_TESTED": list(runs),
    "ALL_OUTPUTS_BYTE_IDENTICAL": len(set(runs.values())) == 1,
    "N_DISTINCT_OUTPUTS": len(set(runs.values())),
    "OUTPUT_LENGTH_BYTES": len(next(iter(runs.values()))),
}

json.dump(OUT, open(os.path.join(HERE, "rt3_e1_clock_audit.json"), "w"), indent=1, default=str)
print("AST: files=%s clock_calls=%s in %s"
      % (OUT["AST_SCAN"]["N_FILES_SCANNED"], OUT["AST_SCAN"]["TOTAL_CLOCK_CALLS"],
         OUT["AST_SCAN"]["FILES_WITH_CLOCK_CALLS"]))
for k, v in ast_res.items():
    if v["CLOCK_CALLS"]:
        print("   ", k, v["CLOCK_CALLS"])
    if v["DATE_DEFAULT_ARGUMENTS"]:
        print("   DEFAULT-ARG DATE ", k, v["DATE_DEFAULT_ARGUMENTS"])
print("TRAP:", OUT["RUNTIME_CLOCK_TRAP"])
print("FROZEN:", OUT["FROZEN_CLOCK_EQUIVALENCE"])
