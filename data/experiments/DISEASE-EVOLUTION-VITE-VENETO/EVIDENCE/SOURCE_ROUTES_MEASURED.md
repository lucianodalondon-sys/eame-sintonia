# ARPAV source routes — measured, with the negative results kept

Every route below was probed with a real HTTP request. Nothing here is assumed.
No credentials were used or requested, and no authentication was circumvented.

## USABLE

### `annate-agrarie` — the outcome source
`/temi-ambientali/agrometeo/file-e-allegati/annate-agrarie` → **26 PDFs, agrarian year
2000-01 to calendar 2025**, all HTTP 200, open.
Role: `OFFICIAL_OBSERVATION`. Region-wide narrative written after each season.
This is the only outcome source in the pilot.

**How it was found:** the public folder page shows only 2014–2025. The other 14 came from
the Plone REST API at `https://www.arpa.veneto.it/api/...`, which lists the underlying
attachment folder. They were not guessed.

## MEASURED AND REJECTED

### `bollettino-mese` — monthly agrometeo bulletins
`/temi-ambientali/agrometeo/file-e-allegati/bollettino-mese` → 22 year folders, 2004–2025,
roughly 264 documents. Looked like a large density upgrade over one narrative per season.

**Sampled `giugno-2019.pdf`: 10 pages, 17,570 characters, and the tokens `peronospor`,
`oidi` and `vit` each occur ZERO times.** These bulletins are pure meteorology —
temperature, rainfall, radiation, water balance. They carry no phytosanitary observation.

`REJECTED_AS_OUTCOME_SOURCE — NO_DISEASE_CONTENT`. Rejected on a measurement, not a guess.

### `peronospora-vite` — folder name looked decisive, content is not
`/temi-ambientali/agrometeo/file-e-allegati/peronospora-vite` → 7 items: 5 illustration
images (`cervello.jpg`, `semaforo.jpg`, `veneto.jpg`…) and 2 PDFs, `vitimeteo.pdf` and
`vitimeteo2.pdf`.

These are **current VitiMeteo model bulletins**, not an archive and not observations.
Under the pilot's own law `RISK_FORECAST != DISEASE_PRESENCE`, a simulation output is
`MODELLED_RISK` and can never serve as backtest ground truth — using it would score a
model against another model.

`REJECTED_AS_OUTCOME_SOURCE — MODELLED_RISK, NOT AN OBSERVATION, AND NO HISTORY`.

The same applies to **AlertInf** (`AlertInf scheda italiano.pdf`), the downy-mildew
simulation model referenced in the same folder tree.

### `agrometeoinforma` — the phytosanitary bulletin
`/dati-ambientali/bollettini/agrometeo/agrometeoinforma` → HTTP 200 but `items_total: 0`.
No archive exposed through the API. Even if it were, these are advisory bulletins stating
risk and recommended treatment, so they would be `MODELLED_RISK` / advisory, not outcomes.

`NO_ARCHIVE_EXPOSED`.

## `PC_REQUIRED_ROUTES` — blocked, classified, not circumvented

| URL | blocker class | note |
|---|---|---|
| `/temi-ambientali/agrometeo/bollettini/copy_of_andamento-annate-agrarie` | `AUTH_REQUIRED` | HTTP 401, redirects to `/login`. A **stale restricted duplicate** of the annate-agrarie folder. The canonical path without the `copy_of_` prefix returns 200 and holds the same series, so nothing is lost and there is nothing here for the user to fetch. Recorded because an earlier pass followed this link and wrongly reported the whole collection as auth-walled. |
| `https://www.arpa.veneto.it/++api++/@search` | `BROWSER_ENV_BLOCK` | HTTP 504 from their reverse proxy (`VirtualHostBase ... :null`). The working API base is `https://www.arpa.veneto.it/api/`, which this pilot uses instead. Not a real blocker. |

**Nothing on this list requires the user's PC.** The entire outcome collection completed
from this container over open HTTP.

## Conclusion

The Veneto route is exhausted. The 26 annate agrarie are the whole of the available
observed record; there is no denser ARPAV series hiding behind them. Any improvement in
outcome quality has to come from a different region or a different pathosystem — which is
what the parallel outcome-first alternatives hunt is for — not from more ARPAV crawling.
