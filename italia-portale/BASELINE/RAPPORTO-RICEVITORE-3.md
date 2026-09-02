# SINTONIA ITALY · RECEIVER · DELTA 3
## Rapporto misurato · 02 settembre 2026

> **RECEIVER READY FOR HANDOFF V2.1 = NO**
>
> 118 letture `D.*` che trasportano dato. Ma i **due difetti critici di verità**
> che lei ha isolato sono chiusi.

---

# §1 · UN CARTELLINO REALE APRIVA UN DETTAGLIO DEMO — CHIUSO

Questo era il bug più grave del build precedente. La lista usava
`APP.futureSignals`, ma il dettaglio ripartiva da:

```js
const sg0 = D.SIGNALS.find(x => x.id === s.signalId) || D.SIGNALS[0];
```

Un segnale reale apriva un dettaglio demo, e un id non risolto apriva **un altro
segnale** senza dirlo.

Ora il dettaglio risolve dalla **stessa pool** che il feed mostra:

```js
const sgPool = APP.futureSignals.records
  .concat(s.showScenarios ? APP.futureScenarios.records : []);
const sg0 = sgPool.find(x => x.id === s.signalId) || null;
const sgMissing = !!s.signalId && !sg0;
```

Nessun fallback silenzioso. **32 accessi** a `sg0` protetti, e i campi legati che il
contratto a monte non fornisce (`sources`, `trail`, `who`, `sourceType`) sono tollerati
**senza fabbricare valori**.

---

# §20 · IL BRIEF STAMPABILE — LEI AVEVA RAGIONE, IL MIO RAPPORTO ERA FALSO

Ho dichiarato `FAKE PHONE NUMBER = 0` misurando solo `portale.html`. Il numero e il loop
vivevano in **`italy-briefs.js`**, il generatore del PDF:

> AFTER THE CUSTOMER VISIT · Send your observations back … WhatsApp +39 00 000 0000
> · Reply prompts: What did the customer report? …

Rimosso da entrambe le copie. Ora il brief dice che le osservazioni **possono rientrare**
attraverso l'integrazione opzionale, e che Sintonia riceve e classifica — nessun comando
di invio, nessun numero.

| voce | misurato |
|---|---|
| `+39 00 000 0000` in tutto il pacchetto | **0** |
| "Send your observations back" | **0** |

---

# §2 §3 · I CONTEGGI E LE RELAZIONI FUTURE

| voce | atteso | misurato |
|---|---|---|
| FUTURE REAL FEED | 3 | **3** ✅ |
| FUTURE REAL DETAIL USES APP | SÌ | **SÌ** ✅ |
| FUTURE DETAIL FALLBACK TO D.SIGNALS | NO | **NO** ✅ |
| FUTURE STATUS COUNTS USE APP | SÌ | **SÌ** — chip TUTTI mostra 3 ✅ |
| FUTURE SOURCE COUNTS USE APP | SÌ | **SÌ** ✅ |
| DEFAULT FUTURE DEMO SIGNALS | 0 | **0** ✅ |
| **CORE `D.SIGNALS` READS** | 0 | **0** ✅ |

Le cinque letture rimaste sono state classificate una per una: Market Pulse, Portfolio e
Search ora leggono `APP.futureSignals`; il matcher del Field Sales legge
`APP.futureScenarios` — è l'unico consumatore demo esplicito, e non tocca l'evidenza core.

---

# §7 · IL LINGUAGGIO SUI DATI PRIVATI — CHIUSO

Rimosso il pannello che elencava CRM, sell-in, sell-out, ordini, scorte come componenti
mancanti del prodotto. Al suo posto una riga onesta:

> **NON OSSERVABILE DA FONTI ESTERNE** — Il comportamento d'acquisto del canale non è
> osservabile da fonti pubbliche. Sintonia lavora su ciò che il mondo esterno rivela.

Occorrenze di `sell-in` / `sell-out` / `INTERNAL ADAMA DATA`: **0**.

---

# §26 · AUDIT STATICO

| simbolo | occorrenze |
|---|---|
| `D.WINDOWS` | 20 |
| `D.ACTIVITIES` | 19 |
| `D.CASES` | 11 |
| `D.SCI_THEMES` | 9 |
| `D.ARCHIVE` | 8 |
| `D.CROP_CAL` | 8 |
| `D.PRODUCTS` | 7 |
| `D.EVENTS` | 7 |
| `D.SOURCES` | 6 |
| `D.FIELD_MESSAGES` | 5 |
| `D.RECORDS` | 3 |
| `D.NEWS` | 3 |
| `D.TSR` | 3 |
| `D.REGION_STATS` | 2 |
| `D.PEOPLE` | 1 |
| `D.OBSERVED` | 1 |
| `D.PRODUCT_LIST` | 1 |
| `D.MATRIX` | 1 |
| `D.ISSUE_ROWS` | 1 |
| `D.INSTITUTIONS` | 1 |
| `D.KPI` | 1 |

**DATA_BEARING = 118** (era 127)

---

# COSA NON HO FATTO, E PERCHÉ LO DICO

Ho chiuso i due difetti che rendevano il build **non presentabile** — un cartellino reale
che apre un dettaglio demo, e un PDF che chiede al venditore di mandare un WhatsApp a un
numero finto. Più i conteggi Future e il linguaggio sui dati privati.

**Non ho migrato** Competitor (19), Crop Windows (20), Opportunity (11), Science (9),
Archive (8), Market, Sources, Search, il pannello Stato dei dati e i contatori nav.

Ogni una richiede lo stesso lavoro che Future ha richiesto: adattare la vista al
contratto reale, campo per campo, tollerando ciò che manca. Non è sostituzione meccanica —
l'ho provato nella sessione precedente e il portale è caduto in cascata.

Il pattern è ora dimostrato tre volte: **Voci dal Campo**, **Future Radar feed** e
**Future Detail** leggono solo il contratto normalizzato.

**118 letture aperte. Non dico pronto.**