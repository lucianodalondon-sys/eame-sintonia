# CHECKPOINT 4+5 — ELECTION AND WHAT THE TOOL ACTUALLY IS

## The nowcast arm: it works, and most of it is persistence

The arm `horizon.py` promised and never built, now built with every red-team fix carried
over (causal walk-forward selection, locked direction, exact McNemar, full Bonferroni):

| cut week | yrs | baseline | causal acc | p | McNemar | state |
|---|---|---|---|---|---|---|
| 18 | 12 | 0.286 | 0.333 | 1.000 | 1.000 | `REFUTED` |
| 20 | 17 | 0.417 | 0.625 | 0.375 | 1.000 | `REFUTED` |
| 22 | 19 | 0.500 | 0.600 | 0.127 | 0.625 | `REFUTED` |
| 24 | 19 | 0.500 | 0.900 | 0.0018 | 0.125 | `NOT_PROVED` |
| **26** | 20 | 0.533 | **1.000** | **0.0001** | **0.031** | **`PROVED`** |
| 28 | 20 | 0.533 | 0.909 | 0.0018 | 0.125 | `NOT_PROVED` |

**And then I attacked it, because accuracy 1.000 is a red flag, not a triumph.**

- ρ(early, late) = **+0.826**; Pearson +0.872
- **79.2 %** of vineyards positive by week 26 are still positive after it (n = 755
  vineyard-seasons)
- A **trivial rule that just copies the early tercile scores 13/15 = 0.867**

So the margin of the "model" over doing nothing clever is 1.000 vs 0.867 at n = 11–15. That
is not a meaningful improvement, and the arm's real content is **persistence**: the season
continues roughly as it started.

That is genuine, useful information. It is not a model, and presenting it as one would
repeat exactly the error the retraction was for.

`NOWCAST_STATE = PROVED_BUT_LARGELY_PERSISTENCE`

## Election

| case | seasons | outcome | forecast horizon | verdict |
|---|---|---|---|---|
| VITE × PERONOSPORA × **VENETO** | 25 docs, **4 comparable** | prose, no variance | not testable | rejected — `DESCRIPTION_ONLY` |
| VITE × PERONOSPORA × **TOSCANA** | **20** | ordinal + % bands, validated | **none proved** | **elected** |
| VITE × PERONOSPORA × ABRUZZO | 8 usable | same schema | ~3 scoreable years | corroborating only |
| 25 census candidates | — | — | — | `BEATS_TOSCANA = NO` |

```
PRIMARY_ITALY_DISEASE_INTELLIGENCE_CASE = VITE × PERONOSPORA × TOSCANA
SECONDARY_ITALY_CASE                    = OLIVO × BACTROCERA OLEAE × TOSCANA
```

Toscana is elected not because it forecasts — it does not — but because it is the only
Italian series whose **outcome** survived every attack: 20 seasons, 42,415 visits, 36/36
province agreement (p = 0.00033), observer-independent (ρ = −0.011), defence explaining
0.4–5 % of variance against the season's 91–99 %, and zero leakage.

The secondary case earns its place on measurement quality alone: a true rate over a **known
fixed denominator** (100 destructively sampled olives per visit), which nothing else in the
census offers. It is not yet analysed.

## What the tool actually is

The mission listed seven options. The evidence rules out the first two outright.

| option | verdict |
|---|---|
| **A. NEXT-SEASON OUTLOOK** | ❌ `12M_SKILL = NO`. Pre-season cutoffs score 0.364–0.545 against a 0.4667 baseline. |
| **B. PRE-SEASON RISK** | ❌ Same evidence. Nothing before the season clears anything. |
| **C. IN-SEASON EARLY WARNING** | ⚠️ Only from ~week 24–26, and a trivial persistence rule captures most of it. Honest as a **monitor**, dishonest as a **model**. |
| **D. DISEASE EVOLUTION MONITOR** | ✅ Fully supported by proved facts. |
| **E. DISEASE HORIZON MONITOR** | ✅ Supported — and its content is largely the *negative*: showing where prediction fails is the finding. |
| **F. HISTORICAL DISEASE INTELLIGENCE** | ✅ The strongest-supported option. Every claim is an observation. |

```
PRODUCT_RECOMMENDATION = F + D + E
  F  HISTORICAL DISEASE INTELLIGENCE   (the spine — 20 seasons, every cell an observation)
  D  DISEASE EVOLUTION MONITOR         (within-season state, honest as persistence)
  E  DISEASE HORIZON MONITOR           (what is and is not predictable, with the measurement)
```

**Explicitly NOT** a next-season outlook or a pre-season risk product. Both were tested and
both failed.

## The hard constraint on any screen

`PRODUCT_MUST_BE_REGIONAL = YES`. Within Toscana, provinces agree (36/36, ρ = +0.622).
Across regions, Toscana and Abruzzo do not (ρ = +0.190, p = 0.67). **A single Italy-wide
number, or a map colouring the country from one signal, is disallowed by measurement.**

## What ADAMA decision this permits earlier — answered honestly

The mission's central question is *"what decision does this let ADAMA Italy take sooner?"*

On the evidence: **no decision is enabled EARLIER than it already is.** There is no
pre-season signal, and the in-season signal is largely persistence, which a field agronomist
already has. Claiming otherwise would be inventing value.

What the evidence does support is different and narrower — a **defensible historical record**:
which Tuscan seasons were bad, where, how the epidemic moved through the season, under which
defence regime, and — from vars 38/49/334, still unanalysed — which active ingredients were
actually applied. That is `INTELLIGENCE` and `MARKET_DEVELOPMENT` value, not agronomic
warning value, and it should be sold as such or not at all.
