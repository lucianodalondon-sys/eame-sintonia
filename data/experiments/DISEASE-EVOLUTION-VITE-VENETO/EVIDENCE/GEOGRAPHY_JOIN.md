# GEOGRAPHY JOIN — declared, not assumed

## What the outcome actually is

The ARPAV *Andamento dell'annata agraria* reports make **one narrative statement per
season for the whole Veneto Region**. They are not plot-level, not station-level, and
not even province-level. When a report says *"la virulenza della Peronospora è apparsa
importante in diversi areali"*, "diversi areali" is not a mapped set of areas.

**OUTCOME SPATIAL UNIT = VENETO_REGION_WIDE_NARRATIVE. One value per season.**

## What the predictor actually is

ERA5 reanalysis (~28 km native grid, served by open-meteo) at 5 points chosen to sit
inside the main Veneto viticultural districts:

| point | lat | lon | elev (m) | district |
|---|---|---|---|---|
| CONEGLIANO | 45.870 | 12.247 | 61 | Prosecco DOCG, Treviso |
| CONEGLIANO_VALDOBBIADENE | 45.870 | 12.104 | 198 | Prosecco Superiore hills |
| SOAVE_VERONA | 45.448 | 11.285 | 38 | Soave, Verona plain |
| BARDOLINO_GARDA | 45.518 | 10.738 | 88 | Bardolino / Garda east shore |
| COLLI_EUGANEI | 45.308 | 11.672 | 284 | Colli Euganei, Padova |

**PREDICTOR SPATIAL UNIT = unweighted mean of these 5 points.**

## The join, stated plainly

`REGIONAL_MEAN(5 vine points) -> VENETO_REGION_WIDE_NARRATIVE`

### Why this join is defensible
- All 5 points are inside real, named Veneto viticultural districts, so the mean is a
  vine-weighted climate rather than a Veneto-wide climate that would include the Dolomites
  and the lagoon.
- The outcome is itself region-wide, so aggregating the predictor to a regional scale
  matches the scale of the thing being predicted. Predicting a region-wide statement from
  a single station would be a scale mismatch in the other direction.

### Why this join is weak — state this in any deliverable
1. **5 points are not the Veneto.** They are an unweighted convenience sample. They are
   not weighted by planted hectares, and they omit the Piave/Lison plain and the
   Berici hills.
2. **ERA5 at ~28 km cannot resolve hill/plain contrast.** The reports repeatedly
   distinguish *pianura* from *alta e media collina* (2019 is explicit about it). The
   predictor mean averages exactly the contrast the outcome sometimes reports.
3. **Averaging destroys the extremes that drive epidemics.** Downy mildew is triggered by
   local rain events. A regional mean of 5 points under-represents the wettest district,
   which is often the one the report is describing.
4. **The outcome's own spatial scope drifts between years.** "su tutti gli ambienti
   vitati" (2019) and "in diversi areali" (2016) and "solo localmente" (2025) are three
   different spatial units wearing the same grammatical clothes. This is carried into
   the outcome coding as `scope_words_it` and must not be silently flattened into severity.

## Verdict

`GEOGRAPHY_JOIN = DECLARED_COARSE`. Usable for a regional seasonal outlook.
**Not** usable for any district-level or plot-level claim, and any deliverable that
renders a district-level map from this join is misrepresenting the evidence.
