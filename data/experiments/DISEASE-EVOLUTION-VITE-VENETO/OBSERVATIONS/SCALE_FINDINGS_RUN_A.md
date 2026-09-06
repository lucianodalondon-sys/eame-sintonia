# What three independent scale designers concluded (run A, 2014–2025)

Three agents were asked separately to build an ordinal severity scale from the ARPAV
reports. None of them returned a usable single annual grade. Their `scale_defensible`
verdicts were **PARTIAL, PARTIAL, NO** — not one said yes.

## 1. Only 6 of 12 seasons print a severity descriptor

**2014, 2016, 2021, 2022, 2024, 2025.**

The other six carry non-assignability codes, and the codes are not interchangeable:

| season | code | why |
|---|---|---|
| 2015 | `NA-DATO` | the document contains no vine peronospora statement at all |
| 2017 | `NA-RISCHIO` | its only sentence is a **risk category**, not an outcome |
| 2020 | `NA-ESORDIO` | onset/date reported, no severity |
| 2018, 2019 | low confidence | extent and occurrence, not graded severity |
| 2023 | mixed | opposite statements in different phases |

This is the same set of 6 that the two independent extraction runs agree on. Two
different methods, one number.

## 2. The ABOVE / NORMAL / BELOW test level is not supportable — the source forbids it

This was one of the two scale levels the mission asked for, and it fails on the evidence:

> across the twelve "Annata agraria" documents 2014–2025 **not one sentence ever compares
> vine peronospora to a norm, an average or a previous year** — the reports reserve that
> language for weather

`NORMAL` is an **empty category**. `ABOVE_NORMAL` has no clean member. A scale cannot be
built by inventing a baseline the source never states, so an ABOVE/NORMAL/BELOW product
here would be the analyst's construction wearing the source's authority.

**The LOW/MEDIUM/HIGH level survives (weakly, on 6 seasons); the ABOVE/NORMAL/BELOW level
does not survive at all.** That is a finding, not a gap to be filled.

## 3. Seasons are internally split, so one value per year misrepresents them

2014 is the clearest: spring infections explicitly *"leggere"*, then July secondary
infections *"quasi ovunque ben visibili"* forcing repeated re-spraying, ending in leaf
infection that blocked sugar accumulation at harvest. Coding 2014 as "low" from the spring
words understates it; coding it "high" from the summer words overstates the spring.

The designers' shared recommendation is a **phase-segmented record** (spring / early
summer / late summer), each cell carrying the verbatim Italian that justifies it, with a
rule that a cell without its sentence is not published.

## 4. Confounds they insisted must never be merged into the grade

- **defence regime** — 2022's *"pressoché assente"* is qualified *"nei vigneti regolarmente
  difesi"*; 2024 distinguishes *difesa integrata* from *vigneti biologici*. That is severity
  under control, not natural pressure.
- **spatial extent** — *"quasi ovunque"* vs *"solo nel settore Trevigiano e Veneziano"* vs
  *"in diversi areali"* are three different spatial units, not three severities.
- **organ affected** — *"anche su grappolo"* is the economically decisive escalation and is
  not the same axis as intensity.
- **risk vs observation** — 2017's *"rischio basso"* belongs in a disjoint column and must
  never sit beside observed severity.

## Consequence for the pilot

On 2014–2025 alone this is **6 comparable seasons → `DEMO_ONLY`** under Gate A, not
`BACKTEST_CANDIDATE_STRONG`. The 2000–2013 batch may move the count; it cannot repair the
ABOVE/NORMAL/BELOW finding, which is a property of how ARPAV writes, not of how many years
we have.
