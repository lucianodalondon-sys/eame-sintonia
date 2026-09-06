# CHECKPOINT 1E — DEFENCE STRATIFICATION (measured)

```
DEFENCE_CONFOUND_MEASURABLE  = YES
DEFENCE_STRATIFICATION_POSSIBLE = YES, but only for 7 seasons (2020-2026)
UNTREATED_SERIES_SUFFICIENT  = NO — there is NO untreated arm at all
TREATED_SERIES_SUFFICIENT    = YES for all three regimes (26-80 sites each, every season)
DEFENCE_REGIMES              = bio | integrato | integrato_volontario
```

## The regime effect exists and points the biologically expected way

Mean over 2020-2026 of `SITE_INCIDENCE` (fraction of vineyards ever positive):

| regime | leaves | bunches | mean max class (leaves) |
|---|---|---|---|
| `bio` | **0.692** | **0.330** | **0.995** |
| `integrato` | 0.617 | 0.284 | 0.840 |
| `integrato_volontario` | 0.539 | 0.289 | 0.700 |

Organic runs consistently hottest, which is what copper-based programmes predict against
modern synthetics. This is a real, quantified management effect — the thing Veneto could
only disclose and never measure.

## But the season dwarfs it, and that is the finding that matters

Do the three regimes agree on **which seasons were bad**?

| | leaves | bunches |
|---|---|---|
| `bio` vs `integrato` | +0.964 | +0.964 |
| `bio` vs `integrato_volontario` | +0.893 | **+1.000** |
| `integrato` vs `integrato_volontario` | +0.857 | +0.964 |
| **mean pairwise ρ** | **+0.905** | **+0.976** |

Variance decomposition over the same 7×3 panel:

| | leaves | bunches |
|---|---|---|
| explained by **SEASON** | **91.4 %** | **99.0 %** |
| explained by **REGIME** | 5.0 % | 0.4 % |

2023 sits at 0.97–0.99 in *every* regime; 2022 at 0.13–0.29 in every regime. The season
ordering is essentially identical whichever management regime you look through.

## What this licenses, and what it does not

**Licensed.** The season-pressure outcome can be used without stratifying, for 2006-2026,
because the management effect is second-order (0.4–5 % of variance) and does not reorder
seasons. Any published figure should still name the regime mix it came from.

**Not licensed.** Two things:

1. **There is no untreated control anywhere in this dataset.** `bio` is *treated* — with
   copper. So every number here is disease **after** control, exactly as in Veneto. What
   changed is that the *differences between control regimes* are now measurable; the
   absolute level under no control is still `NOT_KNOWN`.
2. **The stratification covers 7 of 20 seasons.** Before 2020 the regime field is not
   exposed, so 2006-2019 carries `DEFENCE_REGIME = UNKNOWN`. The 91–99 % season dominance
   is measured on 2020-2026 and is *assumed*, not proved, to hold earlier — an assumption
   the red team should attack.
