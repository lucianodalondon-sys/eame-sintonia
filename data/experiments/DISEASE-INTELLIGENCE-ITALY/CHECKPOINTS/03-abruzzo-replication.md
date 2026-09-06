# CHECKPOINT 3 — ABRUZZO: within-Italy replication attempt, and a design constraint

The census found a **second AgroAmbiente instance** at
`agroambiente.regione.abruzzo.it`, running the same platform and the same
`survey_schema=7` as Toscana. That makes it the only within-Italy replication target for
the 31-May result, which matters more than any other candidate.

## Collected

9 seasons requested (2018–2026), 3 variables, 27 requests, 0 failures.

| season | visits | sites | provinces | bunch `SITE_INCIDENCE` |
|---|---|---|---|---|
| 2018 | 833 | 84 | 4 | 0.750 |
| 2019 | 800 | 69 | 3 | 0.261 |
| 2020 | 621 | 46 | 2 | 0.283 |
| 2021 | 602 | 60 | 2 | 0.067 |
| 2022 | 396 | 38 | 2 | 0.105 |
| **2023** | **17** | **5** | 2 | — `INSUFFICIENT_DATA` |
| 2024 | 935 | 50 | 4 | 0.040 |
| 2025 | 782 | 52 | 3 | 0.135 |
| 2026 | 774 | 72 | 4 | 0.111 |

**2023 returns 17 rows against 396–935 in every other season.** That is a collection gap,
not a mild season — 2023 was a documented peronospora disaster in central Italy. It is
recorded as `INSUFFICIENT_DATA` and excluded. Coding it as low would have inverted the worst
season in the series. *A failure of collection is not a zero.*

**USABLE_YEARS = 8** (2018–2022, 2024–2026).

## The code map is confirmed independently

Abruzzo's API returns the same mapping as Toscana's:
`49=nessuna, 50=media, 51=bassa, 52=alta`. Two independent regional instances agree, which
settles it: the previous session's `50=bassa / 51=media` was simply wrong.

Abruzzo's var 36 carries an extra code `1526 = n.d.` (not determined), which must not be
folded into `nessuna`.

## The replication does NOT hold — and that is the finding

| season | TOSCANA | ABRUZZO |
|---|---|---|
| 2018 | 0.938 | 0.750 |
| 2019 | 0.180 | 0.261 |
| 2020 | 0.062 | 0.283 |
| 2021 | 0.145 | 0.067 |
| 2022 | 0.046 | 0.105 |
| **2024** | **0.667** | **0.040** |
| 2025 | 0.294 | 0.135 |
| 2026 | 0.022 | 0.111 |

```
Spearman(TOSCANA, ABRUZZO) = +0.190     permutation p = 0.669     n = 8
```

The two regions do not track each other. 2024 is the starkest case: a bad Tuscan season and
an almost disease-free Abruzzese one.

## What this means for the product — a hard design constraint

Put beside the earlier result, the picture is coherent and specific:

- **Within Toscana**, nine provinces agree strongly — 36/36 pairs positive, mean ρ = +0.622,
  p = 0.00033.
- **Across Italian regions**, Toscana and Abruzzo are uncorrelated — ρ = +0.190, p = 0.67.

So the season effect is **regional, not national**. A single Italy-wide peronospora pressure
figure would be a fabrication averaging two independent things.

`PRODUCT_MUST_BE_REGIONAL = YES`, measured rather than assumed. Any national roll-up, any
single Italy number, and any map that colours the whole country from one signal is
disallowed by this measurement.

## What Abruzzo cannot do

It cannot carry its own horizon curve. With 8 usable seasons and a minimum training set of
5, strict temporal validation leaves ~3 scoreable years — below the threshold at which
anything can be distinguished from chance. Abruzzo is a **corroborating region**, not a
second backtest.
