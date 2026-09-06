# ALTERNATIVE — VITE × MILDIU (Plasmopara viticola) × ANDALUCÍA

Same pathosystem as the Veneto pilot. Different region, and a completely different class of
outcome: **numbers instead of adjectives.**

Source: **RAIF** (Red de Alerta e Información Fitosanitaria), Junta de Andalucía, published
as open data on the regional CKAN portal. No credentials. No authentication circumvented.
Downloaded and parsed in full from this container.

## What the outcome actually is

Field **`1601 Mildiu: % cepas afectadas`** — the percentage of vines in a monitored parcel
showing downy mildew, recorded by a technician on a dated visit. Companion fields
`1602 % hojas con síntomas` and `1603 % racimos con síntomas` carry leaf and bunch
incidence; `1701/1702` carry Oidio on the same schema.

This is an **`OFFICIAL_OBSERVATION`**: a person looked at vines and wrote down a number.
It is not a risk index, not a model output, not a bulletin. Under the pilot's law
`RISK_FORECAST != DISEASE_PRESENCE`, this qualifies where a VitiMeteo or AlertInf bulletin
never could.

## Verified independently, not taken from the hunter

44,163 dated sampling rows parsed from the 171 MB XML export.

| | |
|---|---|
| seasons with data | **20** (2006–2025) |
| mildiu observations per season | 374 – 3,727 |
| provinces | Cádiz, Córdoba, Huelva, Málaga, Jaén, Sevilla |
| format | numeric percentage, not prose |
| variance | 2023 = 0.00 %, 2012–2014 ≈ 0.1 %, 2025 = 32.1 % mean with 91 % of records non-zero |

The published resource is **labelled 2017–2026 and actually begins in 2006** — the label
understates its own coverage by eleven years.

## The threat, and the test that answers it

**Panel collapse is real.** Monitored parcels fall from 186 (2006) to 18 (2024); annual
records fall from ~4,000 to ~400. No parcel spans all 20 seasons — the best balanced core
is 4 parcels across 8 consecutive seasons. So the network **rotates**, and a naive regional
mean could move because the parcels moved, not because the disease did.

The decisive test is whether **independently-monitored provinces agree on which seasons
were bad**. Composition changes are parcel-specific; they cannot manufacture agreement
between separate provincial networks.

| pair | shared seasons | Spearman ρ |
|---|---|---|
| Cádiz – Córdoba | 15 | **+0.757** |
| Cádiz – Huelva | 15 | +0.561 |
| Córdoba – Huelva | 20 | +0.499 |
| Córdoba – Málaga | 17 | +0.471 |
| Cádiz – Málaga | 14 | +0.402 |
| Huelva – Málaga | 17 | +0.250 |

**All six pairs positive. Mean ρ = +0.490, permutation p = 0.0004** (year labels shuffled
within each province, 5,000 draws).

There is a genuine regional season effect — which is precisely the thing a seasonal outlook
is supposed to predict. The season index is therefore built as the **median across
reporting provinces**, which is robust to which provinces reported.

## Honest comparison against the Veneto incumbent

| | Veneto (ARPAV annate agrarie) | Andalucía (RAIF) |
|---|---|---|
| outcome type | prose adjectives | **numeric %** |
| seasons | 25 documents, ~6–14 comparable | **20, all quantitative** |
| observations per season | 1 region-wide sentence | **374–3,727 dated parcel visits** |
| internal consistency check | impossible — one statement per year | **yes — 6 provinces, ρ=+0.49, p=0.0004** |
| severity scale | analyst-constructed from adjectives | printed by the observer |
| ABOVE/NORMAL/BELOW | **not constructible** | computable from the distribution |
| main threat | severity often simply not written | rotating panel / composition |
| threat testable? | no | **yes, and it passed** |

The Veneto threat is that the number was never written down; nothing can recover it.
The Andalucía threat is that the sample composition moves; that is measurable, and the
province-agreement test shows the season effect survives it.

## What is NOT claimed

1. **Andalucía is not Veneto.** Mediterranean/Atlantic, not continental prealpine. Nothing
   here transfers to a Veneto forecast. What transfers is the *pathosystem* and the
   *method*, not the numbers.
2. **The backtest has not been run.** Outcome quality is established; skill is not. The
   leakage-free feature builder, hostile backtest harness and analog engine from the Veneto
   pilot apply unchanged, and ERA5 for four Andalucían vine points is being collected.
3. **The circularity bound still has to be re-measured here.** In Veneto, antecedent weather
   explained at most ~23 % of the variance of the target season's own rainfall. That number
   is region-specific and must be recomputed for Andalucía before any skill claim.
4. **2024 rests on two provinces**, and Huelva runs systematically far above the others.
   Levels are less trustworthy than rankings.

## Verdict

`OUTCOME_QUALITY = BACKTEST_CANDIDATE_STRONG` — 20 quantitative seasons, well past the
Gate A threshold of 8, with an internal consistency check the Veneto source structurally
cannot provide.

`SKILL = NOT YET TESTED.`

This does not rescue the Veneto product. It relocates the question to a place where the
question can actually be answered.
