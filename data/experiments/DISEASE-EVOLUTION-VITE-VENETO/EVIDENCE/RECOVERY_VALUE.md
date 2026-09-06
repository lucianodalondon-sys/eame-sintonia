# What recovering 2000–2013 actually bought — measured, not asserted

The gap was measured before it was filled, and the gain was measured after.

## Analog coverage

For each target season 2014–2025, take its 4 nearest meteorological analogs among all
prior ERA5 seasons back to 1992, and ask how many of them carry a disease outcome:

| outcome window | nearest analogs that carry an outcome |
|---|---|
| labels 2014–2025 only (before) | **11 / 48 = 23 %** |
| labels 2001–2025 (after)       | **30 / 48 = 62 %** |

Before the recovery, the nearest analog for 2017 was 2000, for 2019 it was 1993, for
2014 it was 2009 — every one of them a season we knew nothing about. The outlook would
have been standing on years it could not see.

## Labelled prior seasons available per target

| target | before | after |
|---|---|---|
| 2014 | 0 | 13 |
| 2019 | 5 | 18 |
| 2025 | 11 | 24 |

An analog outlook for 2014 was previously impossible — there was no prior labelled season
at all. Every target year gains at least 13.

## What it does NOT buy

1. **Documents are not outcomes.** 26 PDFs is not 26 comparable seasons. The mechanical
   lexicon scan finds **no severity marker at all in 14 of the 26 documents**. Gate A is
   applied to comparable outcomes, not to file counts, and this number is the reason the
   gate is not a formality.
2. **The older documents are differently shaped.** Length runs from 7,166 to 32,553 chars.
   The five oldest are agrarian years (1 Nov → 31 Oct), not calendar years.
3. **It does not touch the circularity bound.** `EVIDENCE/circularity_probe.json` was
   computed on 34 seasons of ERA5 and is independent of how many outcomes exist. Antecedent
   weather explains at most ~23 % of the variance in the target season's own rainfall. More
   labels make the estimate of skill sharper; they do not raise the ceiling on it.
