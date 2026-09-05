# SINTONIA ITALY · RECEIVER MIGRATION
## Rapporto misurato · sessione 2 · 02 settembre 2026

> **RECEIVER READY FOR HANDOFF V2 = NO**
>
> 127 letture `D.*` che trasportano dato restano. Non dico pronto.

---

# §1 · LA SUA CORREZIONE PIÙ IMPORTANTE — ACCETTATA

Il mio merge additivo **era** l'assegnazione cieca che lei vieta. Lasciava che campi
**fattuali** della fixture — `crop`, `issue`, `region`, `dates`, `cov`, `topics` —
entrassero in record etichettati come reali. È peggio che non convertire: un record demo
si travestiva da osservazione esterna.

**Rimosso da tutte e tre le collezioni.** I metadati di presentazione ora vivono sotto
`record.ui`, fisicamente separati dallo spazio dei fatti. Merge di record fixture
rimasti: **0**.

---

# §5 · FUTURE RADAR — MIGRATO

| voce | atteso | misurato |
|---|---|---|
| APP FUTURE REAL SIGNALS | 3 | **3** ✅ |
| VISIBLE FUTURE USES `APP.futureSignals` | SÌ | **SÌ** ✅ |
| VISIBLE FUTURE DEMO SCENARIOS BY DEFAULT | 0 | **0** ✅ |
| nav badge | — | **3**, non 56 ✅ |
| toggle SCENARI DIMOSTRATIVI | — | presente, off per default, testato ✅ |

Il feed reale mostra **3 segnali**. Non ho protetto la densità visiva.

I 56 generati sono in una collezione separata dietro il toggle, e non contribuiscono a
conteggi, convergenza di fonti o evidenza.

**§6 · La view tollera i campi mancanti.** I segnali a monte non hanno `who`,
`whyWatch`, `trail`, `promotion` — cinque accessi ora protetti, **senza fabbricare i
valori**.

---

# §14 · PROVENIENZA DELLE OPPORTUNITÀ — CORRETTA

Lei ha ragione: una finestra canonica non prova l'intero oggetto opportunità. Un caso è
reale **solo** se esiste a monte. I 29 di presentazione non sono più marcati derivati-
reali per via di un campo con fonte.

---

# §13 · IL SECONDO OROLOGIO — CHIUSO

Lei l'ha trovato e il mio rapporto precedente diceva il contrario. Era in `portale.html`,
non nel file dati che avevo corretto: `new Date(2026, 8, 1)` — **il 1 settembre**.
Ora legge `AM.REF`. Orologi Sep-1 rimasti: **0**.

---

# §21 · IL LOOP IN USCITA — CHIUSO

Trovato dove lei ha detto, dentro il flusso dell'Action Brief:
`DETECT → … → SEND → RECEIVE FIELD FEEDBACK → LEARN`.
Ora: `RILEVA → COMPRENDI → PRIORIZZA → ASSEGNA → PREPARA`. Occorrenze: **0**.

---

# §10 · UN BUG LATENTE CHE HO SCOPERTO

`D.ARCHIVE_ALL` **non è mai esistito**, e la view lo leggeva. Non si vedeva perché il
percorso non veniva eseguito. Ora punta a `APP.archive.records` — 740 righe indicizzate
su record reali.

---

# §24 · AUDIT STATICO — OCCORRENZE RIMANENTI

| simbolo | occorrenze | classe |
|---|---|---|
| `D.WINDOWS` | 20 | DATA_BEARING |
| `D.ACTIVITIES` | 19 | DATA_BEARING |
| `D.CASES` | 11 | DATA_BEARING |
| `D.SIGNALS` | 10 | DATA_BEARING |
| `D.SCI_THEMES` | 9 | DATA_BEARING |
| `D.ARCHIVE` | 8 | DATA_BEARING |
| `D.CROP_CAL` | 8 | DATA_BEARING |
| `D.PRODUCTS` | 7 | DATA_BEARING |
| `D.EVENTS` | 7 | DATA_BEARING |
| `D.SOURCES` | 6 | DATA_BEARING |
| `D.FIELD_MESSAGES` | 5 | DATA_BEARING |
| `D.RECORDS` | 3 | DATA_BEARING |
| `D.NEWS` | 3 | DATA_BEARING |
| `D.TSR` | 3 | DATA_BEARING |
| `D.REGION_STATS` | 2 | DATA_BEARING |
| `D.PEOPLE` | 1 | DATA_BEARING |
| `D.OBSERVED` | 1 | DATA_BEARING |
| `D.PRODUCT_LIST` | 1 | DATA_BEARING |
| `D.MATRIX` | 1 | DATA_BEARING |
| `D.ISSUE_ROWS` | 1 | DATA_BEARING |
| `D.INSTITUTIONS` | 1 | DATA_BEARING |

**DATA_BEARING = 127** · VISUAL_ONLY = 53

---

# PERCHÉ NON HO CONVERTITO LE ALTRE

Ho migrato **una** collezione, con test, come lei ha chiesto. Ogni collezione successiva
richiede lo stesso lavoro: la view va adattata al contratto reale, campo per campo,
tollerando ciò che manca.

Il pattern è ora dimostrato due volte — **Voci dal Campo** e **Future Radar** sono le due
viste che leggono solo il contratto normalizzato. Nessuna recupera un campo fattuale
dalla fixture.

Restano in ordine: Competitor Watch (19), Market Pulse, Scientific Intelligence (9),
Archive (8), Crop Windows (20), Opportunity Radar (11), Search.

**Non dico pronto con 127 letture aperte.**

---

# §25 · ACCETTAZIONE MISURATA

| voce | atteso | misurato |
|---|---|---|
| CORE DATA-BEARING D.* READS | 0 | **127** ❌ |
| VISUAL-ONLY D.* READS | — | 53 |
| APP FUTURE REAL SIGNALS | 3 | **3** ✅ |
| VISIBLE FUTURE USES APP MODEL | SÌ | **SÌ** ✅ |
| VISIBLE FUTURE DEMO SCENARIOS BY DEFAULT | 0 | **0** ✅ |
| APP COMPETITOR | 503 | **503** ✅ |
| VISIBLE COMPETITOR USES APP MODEL | SÌ | **NO** ❌ |
| APP MARKET | 77 | **77** ✅ |
| VISIBLE MARKET USES APP MODEL | SÌ | **NO** ❌ |
| APP SCIENCE | 88 | **88** ✅ |
| APP RESEARCHERS | 60 | **60** ✅ |
| APP ARCHIVE | ≈740 | **740** ✅ |
| VISIBLE ARCHIVE USES APP MODEL | SÌ | parziale ⚠ |
| DEMO OPPORTUNITY COUNTED AS REAL | 0 | **0** ✅ |
| PRODUCT RELATIONSHIP TRUTH SOURCE | — | ITALY_LABEL_VERDICTS |
| REFERENCE DATE | 2026-09-02 | **2026-09-02** ✅ |
| HARDCODED SEP-1 CLOCKS | 0 | **0** ✅ |
| VOCI REAL PUBLIC VOICES | 17 | **17** ✅ |
| VOCI RTV DEMO MESSAGES | 0 | **0** ✅ |
| FIELD SALES MUTATES CORE | NO | **NO** ✅ |
| FIELD SALES OUTBOUND LOOP | 0 | **0** ✅ |
| BLIND ADDITIVE MERGES | 0 | **0** ✅ |
| NEW HANDOFF V2 INGESTED | NO | **NO** ✅ |
| **RECEIVER READY** | — | **NO** |

## §20 · Le note portoghesi

I campi `WHAT_IT_PROVES` / `WHAT_IT_DOES_NOT_PROVE` restano come li fornisce il dato a
monte. Non li ho tradotti dentro il Design, come lei ha chiesto. I campi localizzati
`provesIt` / `notProvesIt` vanno forniti dal Handoff V2.