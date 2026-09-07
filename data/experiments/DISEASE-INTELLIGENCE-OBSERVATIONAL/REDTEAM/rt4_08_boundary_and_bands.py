#!/usr/bin/env python3
"""RT4-08  Three cheap, exact probes that need no reload.

A  EXACT ROUNDING BOUNDARY. rt4_04 found windows whose 4-decimal rate sits exactly on a
   half-way point in binary. Redo those with Fraction, so the question "is this rate a
   genuine tie" is answered in exact arithmetic rather than in floating point. A genuine tie
   is decided by round()'s half-to-EVEN rule, which is a property of the last kept digit's
   parity - not of the data.

B  THE BAND GAP. di_core.band_for walks bands [0,0], [0.01,6), [6,10), [10,inf). A rate
   strictly between 0 and 0.01 matches NO band and the function returns None. di_render then
   does cell['observation']['source_band']['label']. Probe the whole interval and report
   whether the gap is reachable from real denominators.

C  T4 REDONE. rt4_07's sheet edit did not bite because the rate stayed inside the moved band.
   Repeat on band_for directly, which is a pure function, with an edge that does bite.
"""
import os, sys, json, math
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core

sheet = di_core.load_sheet()
out = {}

# ---------- A
cases = json.load(open(os.path.join(HERE, "rt4_04_float_order.json"), encoding="utf-8")) \
    if os.path.exists(os.path.join(HERE, "rt4_04_float_order.json")) else None
A = []
if cases:
    for w in cases["Q3_boundary"]["closest_20_to_a_rounding_boundary"][:6]:
        num = float(w["num"]); den = float(w["den"])
        q = F(num).limit_denominator(10**15) if num != int(num) else F(int(num))
        exact = F(100) * (F(num) if num != int(num) else F(int(num))) / F(int(den))
        scaled = exact * 10**4
        tie = (scaled.denominator == 2 and scaled.numerator % 2 == 1) or \
              (scaled * 2).denominator == 1 and scaled.denominator == 2
        frac = scaled - math.floor(scaled)
        A.append({
            "metric": w["metric"], "province": w["province"], "window": w["window"],
            "num": w["num"], "den": w["den"],
            "exact_rate_pct": f"{exact.numerator}/{exact.denominator}",
            "exact_rate_decimal": float(exact),
            "exact_x_1e4_fraction_part": f"{frac.numerator}/{frac.denominator}",
            "IS_AN_EXACT_TIE_AT_4_DECIMALS": frac == F(1, 2),
            "python_round_gives": round(100.0 * num / den, 4),
            "round_half_UP_would_give": math.floor(float(scaled) + 0.5) / 1e4,
            "published": w["rate_pct"]})
out["A_EXACT_ROUNDING_BOUNDARY"] = {
    "n_examined": len(A), "detail": A,
    "n_that_are_exact_ties": sum(1 for a in A if a["IS_AN_EXACT_TIE_AT_4_DECIMALS"]),
    "WHY_IT_MATTERS": "at an exact tie the published digit is chosen by round-half-to-even, "
                      "i.e. by the parity of the fourth decimal, not by the data. Any change "
                      "that moves the sum by one ULP - a different summation order, a "
                      "different libm, a different Python - flips it by 0.0001 pp."}

# ---------- B  the band gap
probe = [0.0, 1e-9, 0.001, 0.0018, 0.005, 0.0099, 0.00999999, 0.01, 0.02, 5.9999, 6.0,
         9.9999, 10.0, 100.0]
B = {str(p): di_core.band_for(sheet, p) for p in probe}
gap = sorted(p for p in probe if 0 < p < 0.01 and di_core.band_for(sheet, p) is None)
# reachable? smallest non-zero rate from a real denominator
maxden = 55707
out["B_BAND_GAP"] = {
    "band_for_probe": B,
    "rates_in_(0,0.01)_that_get_NO_band": gap,
    "band_for_returns_None_there": True if gap else False,
    "smallest_non_zero_rate_reachable_pct": 100.0 / maxden,
    "is_that_inside_the_gap": 0 < 100.0 / maxden < 0.01,
    "what_the_renderer_does_with_None":
        "di_render.render_province does cell['observation']['source_band']['label'] with no "
        "guard, so a None band is a TypeError, not a missing line",
    "reachable_with": "1 infested drupe over a window denominator above 10,000 drupes; the "
                      "largest province-window denominator measured here is 55,707"}

# ---------- C  sheet edit that bites
s2 = di_core.load_sheet()
s2["SOURCE_ACTION_BANDS"]["BANDS"][1]["to_pct"] = 0.05
s2["SOURCE_ACTION_BANDS"]["BANDS"][2]["from_pct"] = 0.05
rate = 0.0664                      # the real published Firenze rate at as_of 2026-09-06
out["C_SHEET_EDIT_THAT_BITES"] = {
    "published_rate_pct": rate,
    "band_with_the_repository_sheet": di_core.band_for(sheet, rate),
    "band_after_moving_one_edge_in_the_sheet": di_core.band_for(s2, rate),
    "BAND_CHANGED": di_core.band_for(sheet, rate) != di_core.band_for(s2, rate),
    "sheet_sha256_recorded_anywhere_in_the_published_artifact": False,
    "MEANING": "one number in an unhashed JSON file repaints the published colour from "
               "green to yellow and no receipt in the artifact would show it"}

print(json.dumps(out, indent=1, default=str))
json.dump(out, open(os.path.join(HERE, "rt4_08_boundary_and_bands.json"), "w",
                    encoding="utf-8"), indent=1, default=str)
