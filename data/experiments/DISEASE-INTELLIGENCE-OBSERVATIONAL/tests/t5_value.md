# Value test — the whole population, no cherry-pick

as_of 2026-09-06 · 10 provinces × 2 metrics = 20 cells

RULE: HIGH: publishable AND (a matched historical class that is not TYPICAL, OR a named direction of change, OR a reading outside the source's green band). MEDIUM: publishable, matched history available, and TYPICAL. LOW: publishable observation only. UNKNOWN: the observation is not publishable.

| province | metric | value | why | reading | history | trend |
|---|---|---|---|---|---|---|
| Arezzo | ACTIVE | **LOW** | an observation with no comparable history and no named direction | 0.1636% of sampled drupes (9.0 of 5500.0), source band 0-6% | INSUFFICIENT_DATA (4 seasons) | UNKNOWN |
| Firenze | ACTIVE | **HIGH** | matched history says BELOW_HISTORICAL | 0.0664% of sampled drupes (16.0 of 24100.0), source band 0-6% | BELOW_HISTORICAL (14 seasons) | STABLE_OBSERVED |
| Grosseto | ACTIVE | **LOW** | an observation with no comparable history and no named direction | 0.6784% of sampled drupes (235.55 of 34720.0), source band 0-6% | INSUFFICIENT_DATA (2 seasons) | STABLE_OBSERVED |
| Livorno | ACTIVE | **LOW** | an observation with no comparable history and no named direction | 0.9216% of sampled drupes (141.0 of 15300.0), source band 0-6% | INSUFFICIENT_DATA (1 seasons) | STABLE_OBSERVED |
| Lucca | ACTIVE | **HIGH** | a named direction: INCREASING_OBSERVED | 1.1509% of sampled drupes (61.0 of 5300.0), source band 0-6% | INSUFFICIENT_DATA (3 seasons) | INCREASING_OBSERVED |
| Massa-Carrara | ACTIVE | **LOW** | an observation with no comparable history and no named direction | 0.566% of sampled drupes (30.0 of 5300.0), source band 0-6% | INSUFFICIENT_DATA (1 seasons) | STABLE_OBSERVED |
| Pisa | ACTIVE | **HIGH** | a named direction: INCREASING_OBSERVED | 1.0708% of sampled drupes (98.47 of 9196.0), source band 0-6% | INSUFFICIENT_DATA (1 seasons) | INCREASING_OBSERVED |
| Pistoia | ACTIVE | **LOW** | an observation with no comparable history and no named direction | 0.0278% of sampled drupes (1.0 of 3600.0), source band 0-6% | INSUFFICIENT_DATA (0 seasons) | STABLE_OBSERVED |
| Prato | ACTIVE | **LOW** | an observation with no comparable history and no named direction | 0.0417% of sampled drupes (1.0 of 2400.0), source band 0-6% | INSUFFICIENT_DATA (0 seasons) | UNKNOWN |
| Siena | ACTIVE | **HIGH** | a named direction: INCREASING_OBSERVED | 0.62% of sampled drupes (113.98 of 18383.0), source band 0-6% | TYPICAL (12 seasons) | INCREASING_OBSERVED |
| Arezzo | DAMAGING | **LOW** | an observation with no comparable history and no named direction | 0.0% of sampled drupes (0.0 of 5500.0), source band Nessuna Infestazione | INSUFFICIENT_DATA (4 seasons) | UNKNOWN |
| Firenze | DAMAGING | **HIGH** | matched history says BELOW_HISTORICAL; a named direction: DECREASING_OBSERVED | 0.0% of sampled drupes (0.0 of 24100.0), source band Nessuna Infestazione | BELOW_HISTORICAL (14 seasons) | DECREASING_OBSERVED |
| Grosseto | DAMAGING | **LOW** | an observation with no comparable history and no named direction | 0.0751% of sampled drupes (26.0 of 34620.0), source band 0-6% | INSUFFICIENT_DATA (2 seasons) | STABLE_OBSERVED |
| Livorno | DAMAGING | **LOW** | an observation with no comparable history and no named direction | 0.1242% of sampled drupes (19.0 of 15300.0), source band 0-6% | INSUFFICIENT_DATA (1 seasons) | STABLE_OBSERVED |
| Lucca | DAMAGING | **LOW** | an observation with no comparable history and no named direction | 0.0% of sampled drupes (0.0 of 5300.0), source band Nessuna Infestazione | INSUFFICIENT_DATA (3 seasons) | STABLE_OBSERVED |
| Massa-Carrara | DAMAGING | **LOW** | an observation with no comparable history and no named direction | 0.4151% of sampled drupes (22.0 of 5300.0), source band 0-6% | INSUFFICIENT_DATA (1 seasons) | STABLE_OBSERVED |
| Pisa | DAMAGING | **LOW** | an observation with no comparable history and no named direction | 0.1084% of sampled drupes (9.97 of 9196.0), source band 0-6% | INSUFFICIENT_DATA (1 seasons) | STABLE_OBSERVED |
| Pistoia | DAMAGING | **LOW** | an observation with no comparable history and no named direction | 0.0% of sampled drupes (0.0 of 3600.0), source band Nessuna Infestazione | INSUFFICIENT_DATA (0 seasons) | STABLE_OBSERVED |
| Prato | DAMAGING | **LOW** | an observation with no comparable history and no named direction | 0.0% of sampled drupes (0.0 of 2400.0), source band Nessuna Infestazione | INSUFFICIENT_DATA (0 seasons) | UNKNOWN |
| Siena | DAMAGING | **HIGH** | matched history says BELOW_HISTORICAL | 0.0816% of sampled drupes (15.0 of 18383.0), source band 0-6% | BELOW_HISTORICAL (12 seasons) | STABLE_OBSERVED |

**Distribution over the whole population: {'LOW': 14, 'HIGH': 6}**

## The cells a Market Development reader could act on

- **Firenze · ACTIVE** — Firenze reads below its own matched history in 14 of 14 comparable seasons
- **Lucca · ACTIVE** — observed infestation in Lucca rose across three windows that have already ended, ending at 1.1509% of 5300.0 sampled drupes; its own history is NOT comparable
- **Pisa · ACTIVE** — observed infestation in Pisa rose across three windows that have already ended, ending at 1.0708% of 9196.0 sampled drupes; its own history is NOT comparable
- **Siena · ACTIVE** — observed infestation in Siena rose across three windows that have already ended, ending at 0.62% of 18383.0 sampled drupes; its own history is comparable
- **Firenze · DAMAGING** — Firenze reads below its own matched history in 12 of 14 comparable seasons
- **Siena · DAMAGING** — Siena reads below its own matched history in 12 of 12 comparable seasons

6 of 20 cells produce a sentence a reader could act on.

## What none of them supports

- any forecast
- any statement about groves nobody visited
- any commercial action: ADAMA_RELEVANCE for Olive x Olive Fruit Fly is NO
