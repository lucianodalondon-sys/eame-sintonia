# CHECKPOINT 10 — FINAL RECONCILIATION (red team closed: 33 agents, 24 independent reproductions)

```
attacks raised           18 findings, 10 marked "would change the reconciliation"
reproduced independently 24 verdicts
CONFIRMED  9   OVERSTATED 14   REFUTED 1
after correction: FATAL 2 · SERIOUS 6 · MINOR 16
reproducers sustained "would change the verdict" on 2 of 10
```

## The two confirmed FATALs are **warrant failures, not conclusion failures**

Both destroy the *reason* I gave, and both leave the conclusion standing — one of them
standing more firmly than before.

**1 · The Spresiano conflation.** I reported a Treviso plot with "~10 numeric scorings over
3 years". Those three fields belong to census candidate `VITE x PERONOSPORA x UMBRIA`, region
`Umbria (Bettona/Torgiano, PG)` — **290 km away**. The census's own skeptic block records
Spresiano as *"PURELY VERBAL with no numbers whatsoever."* I relocated a numeric series 290 km
to manufacture same-province adjacency.

The correction makes `NOT_TESTABLE` **stronger**: a plot with **zero** numbers is less testable
than one with ten. And Spresiano is only **3.7 km from Villorba** — geographically ideal,
numerically empty. The unblock is therefore *not* "structure the existing series" (there is
none) but **obtain CREA Conegliano's unpublished per-visit sheets** — a data-access request,
materially larger than the "small and nameable" I claimed.

**2 · The six unfinished scouts.** The words *scout*, `NOT_COMPLETED`, `F5`, `F6` appear
nowhere in my 159-line checkpoint, while **all six outcome pockets came out of `raw/F5/` and
`raw/F6-other-pests/`** — the residue of two fronts that never reported. The package's own
manifest already records that a *previous* `OUTCOMES = NONE` verdict was wrong for exactly this
reason, and section F re-promoted that retracted denominator to a proof.

```
VENETO_NUMERIC_OUTCOME = NOT_ESTABLISHED   (NOT_FOUND is withdrawn and stays withdrawn)
```

## Confirmed SERIOUS, each sharper than I recorded

- **The scanner's recall is ZERO, not 4.2 %.** The regex is
  `\b\d+(?:[.,]\d+)?\s*(?:%|ha\b|…)\b` — the trailing `\b` after the alternation kills the `%`
  branch outright, because a word boundary after `%` needs a word character next.
  `incidenza media del 7,7%` → NOMATCH. Against the project's own 71 gold-standard lines:
  **0/71**. Even with the `\b` removed: 2/71, because the vocabulary carries no `FD`, no
  `giallumi`, no `fitoplasma` — and pocket 6, my own star exhibit, writes "FD" on every numeric
  line. My `≤ 4.2 %` was generous.
- **The caveat was misscoped.** `MONTHLY_BULLETINS_READ_FULLY = NO` exists; there is no
  equivalent flag on the 43. Same instrument, same defect, flagged on one and not the other —
  with "proved a negative properly" sitting between them.
- **I dropped the census's two disqualifying objections.** It records that visit dates are
  **endogenous to the phenomenon** ("the technician goes when disease appears"), which
  invalidates a lead-time test regardless of formatting, and that the useful series is **not
  published** — "disqualifying, not a caveat". Neither sentence reached any checkpoint. Dropping
  them is what let me write "small and nameable".
- **Pocket 6 is bigger than I said and I mis-stated it while claiming to have read it.** It
  holds **four** numeric series — Alessandrino, Canavese, Barolo & Barbaresco, and
  **Doglianese & Monregalese, which I omitted entirely** — **15 area-year values** across ≥6
  named pilot areas. Not "N=4".

## REFUTED — and it is a retraction of my own retraction

`09-CORRECTIONS.md` row 5 conceded that "two missions independently reached 25 Annate seasons"
was wrong on two grounds. **Both grounds are false. The concession was a false confession and
is itself withdrawn.** I verified the timeline myself rather than adjudicating between agents:

| fact | measured |
|---|---|
| 26 Annate PDFs git-tracked **in this repo** | `e595caf`, **2026-09-06 03:17:53** |
| my `verified_evidence.json`: `n_documents=26`, `n_distinct_vine_seasons=25`, collision `{"2005":["2004-05","2005"]}` | `d17e444`, **03:42:57** |
| local-collection handoff arrives here | `08a5786`, **14:05:33** |
| gap | **10 h 22 min** |

The second count cannot restate a document that did not yet exist. Every attacker read
`RAW_LOCATION = C:\disease-local-collection-italy\…` out of the *collection's* manifest and
generalised it to the whole repository **without grepping for the files** — the exact
`LEXICAL_SCAN != FULL_READING` error they were hunting.

The only real residue: `collection-manifest.json` carries a stale `ANNATE_DISTINCT_SEASONS = 26`
which is a *document* count — its own `ANNATE_SEASONS` list holds both `2004-05` and `2005`.
**Flag the field; keep the claim.**

**The lesson is mine, and it is not small: I over-confessed under adversarial pressure.** A
finding against me needs the same verification as a finding for me. Nine of twenty-four
reproductions confirmed; fourteen were overstated; I had already surrendered to one that was
simply wrong.

## What survived every attack, re-run by hostile parties and by me

- **Claim 1** — window 4,263 days; `JOINT4` ≥99.4 % at **10/14**, ≥99.0 % at **12/14**; exact
  fractions recomputed, Farra di Soligo at 99.390 % correctly excluded; 57,901 station-days.
- **Claim 2** — the Oderzo trap, and *worse* than I stated: T/RH **decommissioned**, no 2025 or
  2026 file exists at all.
- **Claim 3** — 14/14 in provincia di Treviso. Toscana 216–262 km, Piemonte 275–337, Abruzzo
  382. **No defensible sub-case rescues the join.**
- **Claim 7** — restored, see above.
- **Claim 8** — nothing disturbs `FIRST_PROVED_CUTOFF = NONE` or `12M_SKILL = NO`.
- Zero partial-year inflation: no 2026 file contributes a single day inside the window.
- No humidity-definition contamination reached the Toscana work.

## Final states

```
WHAT_IS_PROVED_FOR_ITALY
  HISTORICAL_INTELLIGENCE   PROVED   Toscana 20 seasons / 42,415 visits; 36/36 province
                                     agreement p=0.00033; observer-independent rho=-0.011
  EVOLUTION_MONITOR         PROVED   as an observational record, never as a model
  CURRENT_PRESSURE_MONITOR  PROVED   it is a measurement, not a prediction
  PREDICTOR_SET (Veneto)    PROVED   14 stations, sensor-measured leaf wetness, JOINT4 10/14
                                     >=99.4% — no reanalysis carries leaf wetness at all
  PORTFOLIO SIGNAL          PROVED   21,911 recorded applications; copper 70.6%->80.5%,
                                     rho=+0.780, confirmed by regime (bio 0.962 / integrato 0.605)

WHAT_IS_NOT_PROVED
  EARLY_WARNING 7/14/21/30D  model loses to persistence in 11-12 of 16 seasons
  PRE_SEASON_OUTLOOK / 12M   pre-season cutoffs 0.364-0.545 vs a 0.4667 baseline
  FIRST_PROVED_CUTOFF        NONE
  ADAMA_PRODUCT_RELATION     PLAUSIBLE_NOT_PROVED (substance overlap only; no label handoff)

WHAT_IS_NOT_TESTABLE
  LEAF_WETNESS_INCREMENTAL_VALUE   no aligned numeric outcome exists in the predictor's region
  VENETO BACKTEST_NUMERIC          NOT_ESTABLISHED — and the negative is NOT proved
  ABRUZZO / PIEMONTE forecasting   no predictor collected in those regions

UNIVERSAL_ENGINE_READY = PARTIAL
  contracts frozen and self-testing (they refuse my own retracted claim), capability routing
  runs on 6 cases. Not YES: no case has ever passed the predictive gate, so the predictive
  path is specified but never exercised against a success.

PRIMARY_DEMO_CASE   = TOSCANA x VITE x PERONOSPORA   (historical + evolution + current pressure)
SECONDARY_DEMO_CASE = TOSCANA x OLIVO x BACTROCERA OLEAE  (known fixed denominator; NOT analysed)

FINAL_PRODUCT_MODULES = MAP · HISTORICAL · EVOLUTION · CURRENT_PRESSURE · EVIDENCE
  EXCLUDED by evidence: EARLY_WARNING, APPLICATION_WINDOW, ADAMA_ACTION_MAP
  (ADAMA_ACTION_MAP requires a portfolio relation that is PLAUSIBLE_NOT_PROVED)

CASCO_SHADOW_RECOMMENDATION = NO, not yet.
  The gate asks for the universal engine AND two demonstrable Italian cases. The engine is
  PARTIAL and only ONE case is demonstrable — the secondary has not been analysed at all.
  What is missing is exactly two things: analyse Toscana x Olivo x Bactrocera through the
  frozen contracts, and obtain the regulatory/label handoff.

DEMO_READY          = PROVISIONAL
PORTAL_INTEGRATION  = NO
```
