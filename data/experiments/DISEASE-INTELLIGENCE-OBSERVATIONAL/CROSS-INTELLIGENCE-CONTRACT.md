# CROSS-INTELLIGENCE CONTRACT — Disease Intelligence × Scientific Intelligence

A contract only. **Nothing is implemented in this mission and nothing should be.**

## The two tools ask different questions

| | question | evidence |
|---|---|---|
| **Disease Intelligence** | what is happening in the field, where, in which crop and against which problem, and how does it compare with that place's own past | official field scouting: a person dissected 100 olives and counted what was inside |
| **Scientific Intelligence** | what is science finding out | papers, trials, preprints, conference proceedings |

A paper is **not** a substitute for an observation, and an observation is **not** evidence
about a mechanism. The failure mode this contract exists to prevent is a scientific finding
being read as field evidence, or a field reading being explained by a paper that describes a
different region, cultivar or year.

## The joining fields, and nothing else

```
DISEASE_INTELLIGENCE_SIGNAL_ID     stable id of one REGION x CROP x ISSUE x DATE x PROVINCE cell
SCIENTIFIC_INTELLIGENCE_SIGNAL_ID  stable id of one scientific finding
CROSS_INTELLIGENCE_STATUS          NOT_ATTEMPTED | CANDIDATE | RELATED | UNRELATED | UNKNOWN
```

`NOT_ATTEMPTED` is the value today, on every cell, and it is the honest one.

## Rules the join must obey when someone does build it

1. **Neither side may change the other's verdict.** A paper cannot move
   `historical_state`; a field reading cannot upgrade a paper's evidence class.
2. **`CANDIDATE` is a proposal, not a finding.** It means the crop and the problem match. It
   does not mean the science is about this region, this season or this cultivar.
3. **`RELATED` requires all four to match and be stated**: crop, problem, geography and the
   period the science speaks about. Three of four is `CANDIDATE`.
4. **The status is per cell and per date**, exactly like everything else here. A paper that is
   relevant to Firenze in September is not thereby relevant to Grosseto in April.
5. **`UNKNOWN` is a legitimate output** and must be commoner than `RELATED`.
6. **No commercial vocabulary crosses the join in either direction.** The prohibition on
   `ACT_NOW`, `SALES_READY`, `BUY`, `SELL`, `COMMERCIAL_OPPORTUNITY` applies to the joined
   object exactly as it applies to each side.

## What this repository can already say about the olive case

Read-only, in the existing handoff: the olive material is **content items and scientific
references**, not product-label matches — including papers by Blanca B. Landa, a Xylella
researcher, carrying DOIs. That is Scientific Intelligence material sitting in the same file
as portfolio material, which is precisely why the two need separate identifiers before anyone
tries to reason across them.

```
CROSS_INTELLIGENCE_STATUS = NOT_ATTEMPTED
```
