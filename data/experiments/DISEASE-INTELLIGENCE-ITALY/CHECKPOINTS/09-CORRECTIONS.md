# CHECKPOINT 9 — CORRECTIONS (red team, 8 lenses; reproduce phase still running)

Four **FATAL** findings landed against my own reconciliation. I verified the most consequential
one myself before accepting it. The corrections below stand regardless of the reproduce phase;
anything that phase overturns will be corrected again.

---

## FATAL 1 — Pocket 3 IS a vineyard peronospora observation. My classification was wrong.

I wrote that pockets 1–4 are *"Veneto nursery reports… nursery not vineyard"*. For pocket 3
(`Relazione annuale 2008`) that is **false**. Verbatim, line 17, which I pulled and read myself:

> *"La situazione fitosanitaria 2008 per i vigneti coltivati negli areali veneti è stata tra le
> più critiche di questi ultimi decenni… lunghi periodi di **bagnatura fogliare**… A fine giugno
> sui **vigneti test privi di trattamenti** l'infezione di peronospora interessava **il 100 %
> della superficie** e la totalità dei grappoli."*

That is a **Veneto untreated-test-vineyard peronospora incidence** — the unconfounded
observation type that Toscana structurally lacks. The same paragraph explicitly ties the
epidemic to leaf wetness, the very predictor now in hand.

**What it still is not.** One saturated value (100 %, a ceiling) for one season (2008), outside
the 2014–2025 predictor window, with no panel and no series. It does not create a backtest. But
"there is no vineyard disease number in the Veneto package" was **my error, not the source's**.

## FATAL 2 — The "nearest miss" was a geography conflation. Retracted.

I named **CREA Spresiano (TV)** as the nearest compatible outcome, "same province as the
stations". The ~10 verified numeric scorings belong to the census candidate
`VITE x PERONOSPORA x UMBRIA`, region `Umbria (plot-level: Bettona/Torgiano, PG)`. Spresiano is
*mentioned* as a recurring reference site; the numbers I leaned on are **Umbrian**.

I built a Treviso-adjacency argument on an Umbrian plot. `NEAREST_MISS = RETRACTED`.

## FATAL 3 — The scanner behind "0 disease numbers in 43 documents" has ~4 % recall.

The number-detection regex fails on the ordinary Italian forms: `incidenza media del 7,7%`,
`il 12% delle piante colpite`, `gravità 35,4 % su grappoli` — all `NOMATCH`. Measured recall
bound **≤ 3/71 = 4.2 %**.

At that recall, a document with 5 numeric outcome lines has a **~19 %** chance of being flagged
at all. **"0 candidates in 43 documents" is close to uninformative**, and I presented it as
*"the collection proved a negative properly"*. It did not, and neither did I.

```
VENETO NUMERIC_OUTCOME:  NOT_FOUND   ->   NOT_ESTABLISHED
```

The negative is **not proved**. Absence of evidence from a 4 %-recall scanner is not evidence
of absence — which is the exact law this project runs on.

## FATAL 4 — The six unfinished scouts vanished from my checkpoint, and that is where the outcomes were.

`RECON_AGENTS_STARTED = 12`, `RETURNED = 6`, `NOT_COMPLETED = 6`. The handoff flags this
prominently. My checkpoint dropped it — while **all six outcome pockets came from exactly those
scouts' folders** (`F5/`, `F6-other-pests/`).

So the fronts that were cut off mid-flight are precisely the fronts that produced every numeric
outcome found. Declaring the Veneto outcome absent while six such fronts never reported is an
over-claim of the plainest kind.

## SERIOUS corrections also accepted

| # | what I wrote | what is true |
|---|---|---|
| 5 | *"two missions independently reached 25 Annate seasons"* | The **committed manifest says `ANNATE_DISTINCT_SEASONS = 26`**; only the handoff *prose* says 25. And the two counts are not independent — I read their handoff before recounting. **Retracted on both grounds.** |
| 6 | `JOINT4` presented as model-readiness | `JOINT4` is a **row-presence** count. **0 of 57,901 JOINT4 station-days carry a usable daily-mean relative humidity** — the source publishes only `MINIMO` and `MASSIMO`. Any model needing mean RH has *zero* usable days, not 99.98 %. |
| 7 | weekly vine bulletins *"2024–2026 PRESENT"* | **36 of them are `DISCOVERED_NOT_COLLECTED`** behind `robots.txt`; only a handful of samples are preserved. `PRESENT` overstates it. |
| 8 | *"43 preserved documents scanned"* framed as the whole corpus | The 43 are 26 Annate + 17 FAS sales reports, all from **one folder** (`F8-`). The pockets live in `F5/` and `F6-`, which that scan never opened. |
| 9 | `OBSERVED_WEATHER = STRONG, 366,978 rows, 100% valued` | *"100 % valued"* is a property of the extractor, not of the data. **26.9 % of those rows fall outside the analysis window**, and 22.1 % are the min/max humidity rows with no mean. Solar radiation (10.9 % of rows, 8 stations only) is absent from my checkpoint entirely. |

## What SURVIVED the attack, reproduced by the lenses themselves

- **`JOINT4` arithmetic is exact.** An independent recompute returned 10/14 at ≥99.4 % and
  12/14 at ≥99.0 %, window = 4,263 days, with `joint4 ≤ min(per_variable)` holding at 14/14 and
  **zero partial-year inflation** — no 2026 file contributes a single day inside the window.
- **The Oderzo trap is real, and worse than I said**: T/RH are not paused but *decommissioned* —
  nothing at all for 2025 or 2026.
- **Breda di Piave's 951-day hole is genuine source absence**, confirmed against the catalogue.
- **No humidity-definition contamination**: the Toscana work uses MERRA-2 `RH2M` and never
  touches `UMID2M`; grep returns 0 hits.
- **Claim 3 stands**: all 14 stations are in provincia di Treviso, and the Toscana join remains
  `NOT_APPLICABLE`.
- **Claim 8 stands**: nothing here disturbs `FIRST_PROVED_CUTOFF = NONE` or `12M_SKILL = NO`.

## Corrected states

```
VENETO_NUMERIC_OUTCOME          = NOT_ESTABLISHED   (was NOT_FOUND — the negative is unproved)
VENETO_VINEYARD_OBSERVATION     = EXISTS, 1 saturated value (2008, 100%, untreated test vineyards)
NEAREST_MISS_SPRESIANO_TV       = RETRACTED (the scorings are Umbrian)
LEAF_WETNESS_INCREMENTAL_VALUE  = NOT_TESTABLE      (unchanged — but now for the right reason:
                                  no aligned numeric series, NOT because none can exist)
ANNATE_DISTINCT_SEASONS         = 26 per the committed manifest; 25 per the handoff prose;
                                  DISCREPANCY_UNRESOLVED, and my "independent" claim retracted
JOINT4_USABLE_FOR_MEAN_RH_MODEL = 0 of 57,901 station-days
RECON_SCOUTS_NOT_COMPLETED      = 6 of 12, and they are the source of all 6 outcome pockets
```

**Unchanged and unchallenged:** `FIRST_PROVED_CUTOFF = NONE`, `12M_SKILL = NO`,
`PREDICTIVE_HORIZON_PROVED = NO`, `PRODUCT_MUST_BE_REGIONAL = YES`,
`ADAMA_PRODUCT_RELATION = PLAUSIBLE_NOT_PROVED`, `PORTAL_INTEGRATION = NO`.
