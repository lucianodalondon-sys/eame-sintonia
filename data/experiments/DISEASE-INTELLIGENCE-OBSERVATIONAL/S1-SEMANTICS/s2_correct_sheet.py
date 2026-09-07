#!/usr/bin/env python3
"""S2 — rewrite the semantic sheet after an independent lens showed version 1.0 had the unit
exactly backwards. Run once; it is kept so the correction is auditable rather than silent."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "SOURCE-SEMANTIC-SHEET.json")
s = json.load(open(P, encoding="utf-8"))
s["SHEET_VERSION"] = "2.0"
s["CORRECTION_LOG"] = [{
 "VERSION": "1.0 -> 2.0",
 "WHAT_WAS_WRONG": (
     "Sheet 1.0 said attiva, dannosa and totale are COUNTS OF DRUPES out of tot, and built a "
     "whole UNIT_TRAP section on it: 'this engine NEVER reads the raw value as a percentage; "
     "it computes value / tot'. That is exactly backwards for the modern era. The source "
     "computes those three columns as PERCENTAGES already, and the engine was dividing by tot "
     "a second time."),
 "HOW_IT_WAS_FOUND": (
     "an independent semantics lens fetched the API's own filter metadata, which publishes the "
     "SQL. Verified here by fetching it again."),
 "THE_SOURCE_SQL_VERBATIM": {
   "attiva": "trunc(((u + l1v + l2v) / tot) * 100, 1)",
   "dannosa": "trunc(((l3v + l3m + pm + pv + fu) / tot) * 100, 1)",
   "totale": "trunc(((u+l1v+l1m+l2v+l2m+l3v+l3m+pm+pv+fu) / tot) * 100, 1)",
   "guard": "every one carries a where clause requiring tot <> '' AND tot <> '0'"},
 "THE_ERA_BREAK": {
   "WHAT": "the served values are COUNTS up to 2019 and PERCENTAGES from 2020",
   "MY_EVIDENCE": [
     "non-integer values appear in 0 of 4,458 rows in 2006 and in 0 rows in every season "
     "through 2019, then in 150 of 4,431 (3.39%) in 2020 and 0.72%-1.14% every season since. "
     "A count of drupes is always an integer; trunc(x,1) is not.",
     "on the 615 visits between 2006 and 2019 where tot is not 100 and the value is non-zero, "
     "611 (99.3%) are consistent with a COUNT and 204 (33.2%) with a PERCENTAGE.",
     "on the 571 such visits from 2020, only 222 (38.9%) are consistent with a COUNT: 61.1% "
     "are values a count cannot take."],
   "CONSEQUENCE": (
     "a baseline that spans 2019/2020 compares two conventions. The engine now applies the era "
     "rule and emits it in every cell. The definitive fix is to stop reading the "
     "server-computed columns at all and compute the rate from the stage columns, which the "
     "same independent lens fetched and verified: the three identities hold in 75,657 of "
     "75,657 visits under the era rule.")},
 "IMPACT_MEASURED_BY_THE_LENS": (
     "band changes in 32 of 2,302 gate-passing 2020+ windows (1.39%). On the 2026-09-06 "
     "publication, 0 band changes: all ten provinces are green under either reading.")}]

for v in s["VARIABLES"]:
    i = v["SOURCE_VARIABLE"]
    if i == 1:
        continue
    v["UNIT"] = "percent of sampled drupes from 2020 onward; count of drupes up to 2019"
    v["ERA_RULE"] = "infested_drupes = val * tot / 100 if year >= 2020 else val"
    v["CANNOT_USE_FOR"] = [x for x in v["CANNOT_USE_FOR"] if "percentage directly" not in x]
    v["CANNOT_USE_FOR"].append(
        "being divided by tot in the 2020+ era: the source already did that")
    if i == -1001:
        v["MEANING"] = ("the share of sampled drupes carrying EGGS or LIVE FIRST- OR "
                        "SECOND-INSTAR larvae - the stages still open to control")
        v["EVIDENCE"] = "the source's own SQL: (u + l1v + l2v) / tot * 100"
        v["CANNOT_USE_FOR"].append(
            "all live infestation: it EXCLUDES live third-instar larvae (l3v) and live pupae "
            "(pv), which an independent lens measured at 20.92% of all live individuals "
            "recorded, and it reads 0 on 2,737 of 18,798 visits where live L3 or pupae are "
            "present")
    if i == -1002:
        v["MEANING"] = ("the share of sampled drupes at or past the third instar - "
                        "third-instar larvae alive or dead, pupae alive or dead, and exit holes")
        v["EVIDENCE"] = "the source's own SQL: (l3v + l3m + pm + pv + fu) / tot * 100"
        v["CANNOT_USE_FOR"].append(
            "'damage already done' as a synonym for 'dead insects': an independent lens "
            "measured that 38.53% of what it counts is LIVE insects (l3v, pv). It is the "
            "stages past the point of control, whether alive or not.")
    if i == -1003:
        v["MEANING"] = "the share of sampled drupes carrying any of the ten counted stages"
        v["EVIDENCE"] = ("the source's own SQL: "
                         "(u+l1v+l1m+l2v+l2m+l3v+l3m+pm+pv+fu) / tot * 100")
        v["WHAT_WOULD_SETTLE_IT"] = (
            "SETTLED. An independent lens fetched the stage columns in 231 requests and found "
            "the missing component is l1m + l2m - dead first- and second-instar larvae - in "
            "34,540 of 34,555 visits (99.96%) where the gap is non-zero. It is 38.43% of "
            "everything totale counts across the archive and 66.32% in 2026. Sheet 1.0 guessed "
            "eggs (7.87%), exit holes (4.44%) or both (8.41%) and all three guesses were wrong.")
        v["ALSO"] = ("ps (punture sterili) is OUTSIDE totale in 17,992 of 17,992 visits, "
                     "hiding 100,214 sterile stings")

s["UNIT_TRAP"] = {
 "CORRECTED": "Sheet 1.0 had this exactly backwards and the engine followed it.",
 "WHAT_IS_TRUE": (
     "the source's colour legend labels are percentages BECAUSE the values are percentages "
     "from 2020 onward, computed by the SQL above. Up to 2019 the served values are counts, "
     "and there the legend only works because tot is 100 in 94.2% of visits."),
 "RULE_ADOPTED": (
     "infested_drupes = val * tot / 100 when the observation year is 2020 or later, and val "
     "before that. tot <= 0 is refused in both eras, exactly as the source's own where clause "
     "does.")}

json.dump(s, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("sheet 2.0 written")
