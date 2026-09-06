# CERT-V2 · Step 11 — a disease-pressure signal is not a commercial opportunity

This is the contract the tool answers to. It is deliberately narrow, because the tool is
deliberately narrow.

## What the tool measures

One thing, and it has four dimensions, not three:

```
REGION × CROP × ISSUE × DATE
```

Concretely, for one province inside one region, on one date: the share of officially
monitored fields on which scouts recorded the issue during the trailing 28 days, placed as a
percentile inside the same calendar window of every prior season in the archive.

That is a **nowcast of what scouts recorded**. It is not a forecast, it is not a statement
about fields nobody visited, and the panel of monitored fields is not a random sample of the
region's area.

## The only states it may emit

| state | meaning |
|---|---|
| `DISEASE_PRESSURE_SIGNAL` | a class survived the publication gate on this date |
| `RADAR_SIGNAL` | worth watching; below the publication gate |
| `EXPLORATORY_SIGNAL` | the cell exists but the instrument is not certified on it |
| `INSUFFICIENT_EVIDENCE` | too few sites, or too few baseline seasons |
| `NO_SIGNAL` | measured, and nothing above the baseline |

`COMMERCIAL_OPPORTUNITY` is not on this list and this tool may never produce it.

## What a later layer must prove before any of this becomes an opportunity

1. the agronomic signal, with its date attached
2. the crop, canonicalised — **not satisfied today**: the engine's output carries no CROP field
3. the issue, canonicalised — **not satisfied today**: the output carries no ISSUE field
4. the region, canonicalised — **not satisfied today**: the output carries no REGION field
5. the date and, where the problem has one, the treatment window
6. `ADAMA_PRODUCT_RELATION` for that exact COUNTRY × CROP × ISSUE, adjudicated by the
   regulatory owner, in {`PROVED`, `NOT_FOUND`, `UNKNOWN`}
7. whatever additional commercial eligibility the V2 engine requires

Items 2, 3 and 4 are measured in `p8_crop_semantics.json`: `current_pressure` returns
`AS_OF`, `WINDOW`, `METRIC`, `VALUE_MODE`, `EVIDENCE_ROLE`, `CUTOFF_LABEL`,
`DATA_LATENCY_DAYS`, `SOURCE`, `PARAMS`, `DENOMINATOR_GUARD`, `SEASON_STATE` and
`PROVINCES` — and nothing that names the region, the crop or the issue. Three of the four
dimensions of the declared unit of analysis exist only in a directory name and in a free-text
argument the caller supplies. In `ENGINE/gates.py:26` that argument is literally the string
`"crop"`.

## The one cell that qualifies today, written the only way it may be written

```
REGION   Toscana
CROP     olive          (as a folder name; the engine cannot name it)
ISSUE    Bactrocera oleae, damaging infestation
DATE     2026-09-06     ← not optional, and not carried forward to any other date
STATE    DISEASE_PRESSURE_SIGNAL, 8 of 10 provinces published
ADAMA_PRODUCT_RELATION = NOT_FOUND for the three adjudicated products
                       = UNKNOWN for the rest of the portfolio
```

On 2026-06-15, the same cell publishes nothing at all — 0 of 10, with the newest readable
observation 241 days old. On the same three dates the vine case goes 6/10 → 1/10 → 0/10. Both
tables were re-measured in this certification and both reproduce the pilot's own C25 finding
exactly.

## What follows from that, commercially

The only cell that passes the agronomic gate on 2026-09-06 is the cell where our own reading
of 163 Italian labels did not find a product for the problem. The honest statement is that
sentence, not a softer one — and not a harder one either: `NOT_FOUND` was adjudicated for
three named products, and everything else in the portfolio is `LABEL_CHECK_NEEDED`, which is
`UNKNOWN`, not absence.
