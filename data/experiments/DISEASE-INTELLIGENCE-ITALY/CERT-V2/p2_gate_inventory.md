# CERT-V2 · Step 2 — gate inventory A–J

Gates: 10  ·  valid: 1  ·  invalid: 9  ·  incapable of passing or failing: 1

Mutations run: 33  ·  targeted kills: 14  ·  targeted survivals: 8

| gate | can it fail? | mutations killed | mutations survived | defects |
|---|---|---|---|---|
| A_OUTCOME_IS_OBSERVED | yes | M01, M02 | R05 | T6: survives a mutation that destroys its own property -> R05 [independent red team] (every value replaced by a calendar model; role and schema untouched) |
| B_NOT_SOLD_AS_FORECAST | NO | — | M03 | T6: survives a mutation that destroys its own property -> M03 [certification] (the time cutoff is removed) |
| C_REGIONAL_NOT_NATIONAL | yes | M04, M05 | R01 | T6: survives a mutation that destroys its own property -> R01 [independent red team] (published cells harmonised to one class per case; history untouched) |
| D_UNKNOWN_IS_VISIBLE | yes | M06 | M07 | T6: survives a mutation that destroys its own property -> M07 [certification] (missing read as zero (FAILURE == ZERO)) |
| E_REPRODUCIBLE | yes | M08, M09 | M27 | T6: survives a mutation that destroys its own property -> M27 [certification] (file order fixed but different (the real cross-machine defect)) |
| F_LABEL_NOT_PARAMETER_ARTEFACT | yes | M10 | R02 | SCOPE: the predicate is any(), so one stable case carries the gate while the other sits at 0.596. It certifies 'a label somewhere is stable', not 'the label is stable'.; T6: survives a mutation that destroys its own property -> R02 [independent red team] (one of the two cases' labels made a 100% par |
| G_DISCRIMINATES_BETWEEN_SEASONS | yes | — | — | — |
| H_REFRESHABLE_WITHOUT_RESEARCH | yes | M13, M14, M15, M16 | R04 | T5: requires a live third-party endpoint. Offline, the gate cannot be evaluated at all.; FROZEN CLOCK: latency is compared against a hardcoded AS_OF, so the freshness certification never expires.; T6: survives a mutation that destroys its own property -> R04 [independent red team] (every refresh ans |
| I_GENERALIZES | yes | M17, M18 | R03 | T6: survives a mutation that destroys its own property -> R03 [independent red team] (the unseen case is never run; season_outcomes is a stub) |
| J_NOT_DUPLICATE | NO | — | — | T5: reads a hardcoded absolute path under /home/user that no other machine has, while a byte-identical copy is tracked in this repository. Same defect class the arbiter used to overturn gate I, repeated in the same commit.; T4: the predicate is arithmetically incapable of returning PASS. jv is eithe |

## Cross-cutting mutations (no single gate claims these)

| id | property destroyed | detected by the suite? | which gate noticed |
|---|---|---|---|
| M20 | observed values replaced by code ids | NO | — |
| M21 | crop swapped: olive case served the vine archive | yes | H_REFRESHABLE_WITHOUT_RESEARCH |
| M22 | every observation date shifted one year forward | NO | — |
| M23 | source url and file hashes removed | NO | — |
| M24 | signal inverted | yes | F_LABEL_NOT_PARAMETER_ARTEFACT |
| M25 | universe zeroed | no verdict — the suite raised | — |
| M26 | evidence link broken on every cell | NO | — |
