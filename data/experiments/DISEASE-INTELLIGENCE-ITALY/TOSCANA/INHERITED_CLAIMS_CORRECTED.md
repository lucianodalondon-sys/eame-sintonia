# Claims inherited from the previous session, re-checked against the API

The brief said not to inherit the previous numbers without recounting. Recounting found
three errors before a single analysis was run. All three came from the same source: my own
`ALT-VITE-PERONOSPORA-TOSCANA/ELECTION.md`.

## 1. The code→label map was wrong — two classes were swapped

Previously recorded: `49 nessuna / 50 bassa / 51 media / 52 alta`

The API's own `survey_code` filter block says:

| code | var | order_n | label |
|---|---|---|---|
| 49 | 34 | 0 | nessuna |
| **50** | 34 | 3 | **media** |
| **51** | 34 | 5 | **bassa** |
| 52 | 34 | 10 | alta |

**Codes 50 and 51 are the opposite of what was recorded.** Any analysis inheriting that map
would have swapped `bassa` and `media` in every year, in both directions, invisibly.

`order_n` is *also* not a usable ordinal here — it ranks `media` (3) below `bassa` (5). The
ordinal must come from the **labels** (`nessuna < bassa < media < alta`), not from `order_n`
and not from the code number. The collector now reads the map from the API per request and
stores it beside the data, so a relabelling by the source becomes visible instead of silent.

## 2. The series does not start in 2008

Previously recorded: *"18 seasons (2008–2026; 2011 genuinely missing)"*.

Measured: **2006 returns 2,080 rows and 2007 returns 3,411 rows.** The earlier collection
simply began its loop at 2008. The API's year filter offers **2006–2026 (21 years)**.

## 3. "36,924 georeferenced observations" — the georeferencing part is false

Measured: early years carry `lat: "0", lon: "0"`. Coordinates are **not** universal, so the
observation count and the georeferenced count are two different numbers and were conflated.

Geography is not lost, though: every row carries `admin_code` (an ISTAT municipality code)
plus `name_4` (comune), `name_3`/`nome_area` (province). So the honest statement is
**municipality-level geography for all rows, point coordinates for only some** — which is
exactly the distinction the mission's map rule demands ("não inferir região exata de
documento regional").

## What the recount also revealed that was never recorded

The Peronospora schema (7) is far richer than one presence class:

| var | name | what it is |
|---|---|---|
| 34 | `presenza_su_foglie` | ordinal PRESENCE class on leaves |
| 36 | `presenza_su_grappoli` | **incidence bands on bunches**: 1-5%, 5-10%, >15% |
| 333 | `sporulazione` | sporulating spots present, si/no |
| 37 | `piogge_ultima_settimana` | rain last week, as recorded by the observer |
| 38 | `data_ultimo_tratt.` | **date of last treatment** |
| 49 | `prodotto_principale` | **the active ingredient actually applied** |
| 334 | `prodotto_in_miscela` | the tank-mix partner |

And crop=3 (Vite) carries eight further schemas on the same vineyards: Fenologia (4),
Lobesia (5), Botrite (6), Oidio (8), Altri Insetti (9), Acari (59), Black Rot (77),
Halyomorpha (87).

Defence regime is a first-class filter with **three** real values — `bio`,
`integrato`, `integrato_volontario` — not a treated/untreated binary.

None of this is analysed yet. It is recorded here as measured structure only.
