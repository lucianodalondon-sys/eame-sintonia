# CHECKPOINT 9 — LOCAL COLLECTION RECONCILED

## A · Handoff received and verified

```
LOCAL_COLLECTION_BRANCH = claude/disease-local-collection-italy
LOCAL_COLLECTION_HEAD   = 124f79f91b1eed0cf17161ef71aebc7e4f91df3b   ← MATCHES the declared 124f79f
HANDOFF_PATH            = pilot-disease-local-collection/LOCAL-DISEASE-COLLECTION-HANDOFF.md
HANDOFF_STATE           = PARTIAL
READY_FOR_INTELLIGENCE  = PARTIAL
FILES_UNDER_PACKAGE     = 342 (committed); raw/ deliberately outside Git
```

The handoff is unusually rigorous: it red-teamed itself with 28 agents, published eleven of
its own errors, and separates `CATALOG_AVAILABILITY` from `ACTUAL_DATA_PRESERVED`
throughout. I recounted the load-bearing numbers from the committed manifests rather than
inheriting them.

## B · Predictor datasets — measured by me from `joint-coverage.json`

Window `2014-03-01 → 2025-10-31` = **4,263 days**.

`JOINT4` = leaf wetness **and** air temperature **and** relative humidity **and** rain, all
present on the same day — which is what a downy-mildew model actually needs.

| station | BFOGL days | **JOINT4** | **%** | last T/RH |
|---|---|---|---|---|
| Ponte di Piave | 4263 | 4262 | 99.98 | 2026-07-31 |
| Volpago del Montello | 4261 | 4257 | 99.86 | 2026-07-31 |
| Gaiarine | 4261 | 4256 | 99.84 | 2026-07-31 |
| Maser | 4263 | 4256 | 99.84 | 2026-07-31 |
| Zero Branco | 4263 | 4254 | 99.79 | 2026-07-31 |
| Valdobbiadene - Bigolino | 4259 | 4250 | 99.70 | 2026-07-31 |
| Conegliano | 4255 | 4249 | 99.67 | 2026-07-31 |
| Vazzola - Tezze | 4249 | 4248 | 99.65 | 2026-07-31 |
| Villorba | 4248 | 4244 | 99.55 | 2026-07-31 |
| Roncade | 4256 | 4242 | 99.51 | 2026-07-31 |
| Farra di Soligo | 4245 | 4237 | 99.39 | 2026-07-31 |
| Castelfranco Veneto | 4236 | 4227 | 99.16 | 2026-07-31 |
| ⚠️ **Oderzo** | 4257 (99.86 %) | **3608** | **84.64** | **2024-01-28** |
| ⚠️ Breda di Piave | 3312 | 3311 | 77.67 | 2026-07-31 |

```
JOINT4_STATIONS_GE_99_4_PCT = 10 / 14      ← I reproduced this independently
JOINT4_STATIONS_GE_99_0_PCT = 12 / 14
```

**The Oderzo trap is real and I confirmed it.** Leaf wetness alone reads 99.86 %, which looks
excellent; temperature and humidity stopped on 2024-01-28, so joint coverage is 84.64 % and
the 2024–2025 seasons are unusable there for any model needing T and RH.

Format traps carried forward: `TARIA2M` and `UMID2M` arrive as **JSON objects inside a
string**, and **relative humidity has no daily mean** — only `MINIMO` and `MASSIMO`. Any
`AVG_HUMIDITY` would be fabricated.

## C · Outcome datasets — all six inventoried

`files_scanned = 12`, `files_with_measured_outcome = 6`. My classification is **stricter than
the handoff's summary table**, because I read the extracted lines:

| # | source | what it really is | verdict |
|---|---|---|---|
| 1–4 | Veneto *Relazione annuale* **2006, 2007, 2008, 2009** | Phytosanitary-service **nursery** reports. The extracted outcome lines are dominated by nursery-registry text, and pocket 4's leading line is **import trade statistics** (+26 %, +14 %) — not disease. | out of window (2006–09), nursery not vineyard |
| 5 | ERSA FVG *bilancio drupacee 2020* | Cydia molesta / Anarsia **trap-catch narrative**, stone fruit, Friuli, **1** outcome line, one season | insect, wrong crop, wrong region, N=1 |
| 6 | **Piemonte FD Progetti Pilota 2025** | **Real numeric incidence**: Alessandrino 7.7/9.9/7.7/7.2 %, Canavese 3.4/5.0/2.0/2.9 %, Barolo & Barbaresco 6.0/2.4/1.4 % | the strongest, and still not enough |

Pocket 6, classified separately as the mission requires:

```
HISTORICAL_VALUE = YES   real dated regional incidence, officially published
MONITORING_VALUE = YES   the pilot areas are re-surveyed annually
BACKTEST_VALUE   = NO    N=4 years, annual resolution, and POLICY-CONFOUNDED —
                         symptomatic vines are under mandatory legal removal, so the
                         decline partly measures enforcement, not epidemiology
```

## D · Geography compatibility — the join that decides everything

```
PREDICTOR_GEOGRAPHY = 14 ARPAV stations, ALL in provincia di TREVISO, Veneto (lat/lon, 14/14)
OUTCOME_GEOGRAPHY   = Toscana (my calibrated case) / Abruzzo / Piemonte
JOIN_METHOD         = NONE ATTEMPTED
JOIN_LIMITATION     = NOT_APPLICABLE — different regions
```

`PRODUCT_MUST_BE_REGIONAL = YES` was proved earlier (Toscana vs Abruzzo ρ = +0.190, p = 0.67).
**Treviso leaf wetness therefore cannot be used to improve the Toscana backtest.** Doing so
would be the exact error the regionality law exists to prevent.

## E · Leaf wetness — the role, and the nearest miss

The question is not *"does leaf wetness save the forecast?"* It is *"is there any Italian case
where region, crop, issue and years all line up?"* I tested compatibility against my own
25-candidate census rather than taking the handoff's word.

**Nearest miss, and it is genuinely near.** The CREA/AIPP *Bilancio Fitosanitario Viticolo*
untreated-control plots include **CREA Spresiano (TV)** — the *same province* as the stations,
the *right* pathosystem (Plasmopara viticola), and *unconfounded by treatment*, which is
exactly what Toscana lacks.

It still fails, on measurement:

| criterion | status |
|---|---|
| `SAME_REGION` | ✔ Treviso |
| `SAME_CROP` | ✔ vite |
| `SAME_ISSUE` | ✔ peronospora |
| `OVERLAPPING_YEARS` | ✔ within 2014–2025 |
| **`TEMPORAL_ALIGNMENT`** | ✘ **~10 numeric scorings across 3 years**, irregular event-driven visits |
| **structure** | ✘ published as **sentences in conference proceedings**, never as rows; scoring scale inconsistent between regions *and* between editions (% diffusione vs oil spots per leaf) |

```
LEAF_WETNESS_INCREMENTAL_VALUE = NOT_TESTABLE
```

**`NOT_TESTABLE` is not `NO`.** The series is preserved and is the best predictor set in the
whole project. What would unblock it is small and nameable: a structured, per-visit series
from the Spresiano untreated plot — or any Treviso vineyard panel with dated numeric
peronospora readings on a stable scale.

## F · Veneto verdict

```
HISTORICAL_CONTEXT          = STRONG    25 Annate 2001-2025 + 347 monthly bulletins 2004-2025
OBSERVED_WEATHER            = STRONG    14 stations, 366,978 rows, 100% valued
LEAF_WETNESS                = STRONG    232 files, 82,125 rows, sensor-measured (no reanalysis has it)
QUALITATIVE_DISEASE_REPORTS = PRESENT   weekly vine bulletins 2024-2026, narrative only
NUMERIC_OUTCOME             = NOT_FOUND
BACKTEST_NUMERIC            = NOT_TESTABLE
```

The collection proved a negative properly: 43 preserved official Veneto documents scanned,
**0 publish a disease number** for the window. The monthly bulletins carry **155 lexical
mentions of peronospora/oidio and 0 measurements** — mining that folder would fabricate 155
observations that do not exist.

`MONTHLY_BULLETINS_READ_FULLY = NO` (347 preserved, lexically scanned only). Absence in a
lexical scan is **not** proof that no document contains anything useful.

**The Vitimeteo spreadsheets are model output, not observation** — their own cover says
*"Indicazioni di rischio — percentuali di infezione, modello Vitimeteo — Plasmopara (versione
sperimentale)"*. They are never used as ground truth here.

## G · Toscana status — unchanged by this handoff

Nothing in the local collection touches Toscana. The retractions stand:

```
FIRST_PROVED_CUTOFF       = NONE
12M_SKILL                 = NO
PREDICTIVE_HORIZON_PROVED = NO
EARLY_WARNING_7/14/21/30D = NOT_PROVED
PRODUCT_MUST_BE_REGIONAL  = YES
```

The Annate reconciliation is a genuine independent cross-check: the collection measured **25
distinct seasons, 2001–2025**, from the documents' own first pages — and my own recount of the
same corpus reached **25 distinct seasons** as well, having caught the same duplicated 2005.
Two missions, different methods, same number.
