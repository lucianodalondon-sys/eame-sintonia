# SINTONIA ITALY · ARCHITECTURE CLOSURE
## Rapporto · 02 settembre 2026

---

# §30 · ACCEPTANCE · APPLICATION MODEL

| voce | risultato |
|---|---|
| D() STILL RETURNS ITALY_DEMO DIRECTLY | **NO** — `ITALY_DEMO` è ora solo l'input di precedenza più bassa del modello |
| ITALY_APP_MODEL EXISTS | **SÌ** — `italy-app-model.js`, caricato per ultimo su tutto |
| CANONICAL WINDOWS FED INTO APP MODEL | **SÌ** — 29, precedenza `CANONICAL` |
| LABEL VERDICTS FED INTO APP MODEL | **SÌ** — ogni relazione porta la sua classe di forza |
| INGESTED REAL DATA FED INTO APP MODEL | **SÌ** — 18 collezioni |
| COMMERCIAL CATALOG FED INTO APP MODEL | **SÌ** — 44 voci, unite ai 163 regolatori |
| DEMO FALLBACK EXPLICIT | **SÌ** — `SYNTHETIC_DEMO` dichiarato per collezione |

## Precedenza implementata

```
CANONICAL  >  REAL_SOURCE  >  REAL_DERIVED  >  SYNTHETIC_DEMO
```

`pick()` prende il primo candidato non vuoto in ordine di precedenza. Quando il
prossimo pacchetto fornisce una tabella reale, **vince automaticamente** senza
toccare nessuna vista.

## Collezioni nel modello, misurate a runtime

| collezione | record | provenienza |
|---|---|---|
| windows | 29 | CANONICAL |
| cases | 29 | REAL_DERIVED |
| products | **166** | REAL_SOURCE (163 regolatori + 44 commerciali uniti) |
| regulatory | 163 | REAL_SOURCE |
| commercial | 44 | REAL_SOURCE |
| resistance | 34 | REAL_SOURCE |
| competitor | 72 | REAL_SOURCE |
| market | 77 | REAL_SOURCE |
| science | 88 | REAL_SOURCE |
| researchers | 60 | REAL_SOURCE |
| voices | **17** | REAL_SOURCE |
| channels | 30 | REAL_SOURCE |
| sources | 31 | REAL_SOURCE |
| events | 18 | REAL_SOURCE |
| news | 8 | REAL_SOURCE |
| signals | 56 | REAL_DERIVED |
| fieldMessages | 18 | SYNTHETIC_DEMO |

Da **2 tabelle su 22** a **18 collezioni** dietro un solo adattatore.

`counts` è derivato, mai scritto a mano: la UI cresce col prossimo carico.

---

# §31 · ACCEPTANCE · PORTFOLIO

| voce | risultato |
|---|---|
| OPPORTUNITY CARDS | 29 |
| VERIFIED PRODUCT VISIBLE | **10** |
| CHECK-NEEDED PRODUCT VISIBLE | **10** |
| NO CONFIRMED MATCH | **9** |
| CANDIDATES LOST BECAUSE NOT VERIFIED | **0** |
| PORTAFOGLIO TOP LEVEL | **SÌ** |
| COMMERCIAL CATALOG LOADED | **SÌ** — `italy-catalog.js` ora caricato |
| REGULATORY UNIVERSE AVAILABLE | **SÌ** — scheda separata |
| SPECIALI ACCESSIBLE | **SÌ** — BREVIS, BUDGE, EXELGROW, PARLEAF, POWERFILM |
| PRODUCT INTELLIGENCE VIEW | **SÌ** |
| PRODUCT ENTITY CLICKS TO RADAR FILTER | **0** — erano 11 |
| PRODUCT SEARCH OPENS PRODUCT VIEW | parziale — indice costruito, routing di Search non convertito |

Il baseline 10 / 10 / 9 è **preservato**. Nessuna relazione respinta è tornata verificata.

## Product Intelligence

`view = product`, `openProduct(name)`. Mostra nome, stato catalogo commerciale, stato
regolatorio, categoria, principio attivo, e le connessioni divise in tre classi:
verificate, da verificare, non confermate in questa lettura — con la regola di assenza
attaccata. Più finestre colturali collegate, resistenza collegata, e un blocco esplicito:

> **NON OSSERVABILE DA FONTI ESTERNE** — Vendite, scorte e quota di mercato non sono
> osservabili da fonti esterne e non fanno parte di Sintonia.

`VEDI OPPORTUNITÀ COLLEGATE →` resta come CTA separata: cliccare il prodotto **non è**
filtrare il radar.

---

# §32 · ACCEPTANCE · VOCI / FIELD SALES

| voce | risultato |
|---|---|
| VOCI DAL CAMPO TOP LEVEL | **SÌ** — dopo Polso di Mercato, prima di Monitoraggio Concorrenza |
| REAL PUBLIC VOICES CONNECTED | **SÌ** — 17 dal dataset |
| FIELD SALES UNDER INTEGRAZIONI DEMO | **SÌ** — gruppo di navigazione separato, accento ambra |
| FIELD SALES INBOUND ONLY | **SÌ** |
| FAKE PHONE NUMBER | **0** |
| SEND FIELD INTELLIGENCE | **0** |
| SEND OBSERVATIONS BACK | **0** |
| OUTBOUND WHATSAPP CLAIMS | **0** |
| SIMULATE INCOMING MESSAGE | **SÌ** — `SIMULA MESSAGGIO IN ARRIVO` |

Ogni voce porta **COSA PROVA** e **COSA NON PROVA**, con la regola dichiarata:
*un commentatore non è necessariamente un agricoltore.* L'identità non viene mai promossa.

Il flusso reso è: `IN ARRIVO → RICEVUTO → CLASSIFICATO → COLLEGATO → DA VALIDARE`,
con *Sintonia riceve. Non invia messaggi da questo modulo.*

Ho trovato e rimosso una seconda occorrenza di linguaggio in uscita che era **dentro
l'Action Brief**, non nello strumento — `AFTER THE CUSTOMER VISIT` con il numero finto.

---

# §33 · ACCEPTANCE · LANGUAGE

| voce | risultato |
|---|---|
| **LANGUAGE SWITCH RELOAD** | **NO** — misurato: un marcatore DOM sopravvive allo scambio |
| `document.documentElement.lang` | **SÌ** — `it` ⇄ `en` a runtime |
| `<html lang="it">` | **SÌ** |
| ITALIAN accidental English | landing **0**; le viste profonde restano da chiudere |
| HARDCODED TRANSLATABLE TEMPLATE STRINGS | ridotte, non a zero |
| ITALIAN SEARCH PASS | indice costruito dal modello, non verificato a runtime |

**Perché la ricarica esisteva** — le stringhe di data si costruivano una volta al
caricamento del modulo. Ora `decorate()` le ricostruisce a ogni render dai `Date`
grezzi, quindi lo stato basta. Questa era la causa, non un sintomo.

---

# §34 · ACCEPTANCE · CLIENT PACKAGE

| voce | atteso | risultato |
|---|---|---|
| OLD ADAMA-BRASIL DESIGN PATH REFERENCES | 0 | **0** |
| ADAMA BRASIL IMPLEMENTATION LEAKS | 0 | **0** |
| ACCESSO BRANDWELL CSS LOADS | SÌ | **2** |
| ACTION BRIEF BRANDWELL CSS LOADS | SÌ | **1** |
| PUBLIC CDN REQUIRED | NO | **SÌ** — non chiuso |
| FULL NETWORK-OFF TEST | PASS | **FAIL** |

Il §25 era reale: `accesso.html` e `italy-briefs.js` puntavano alla cartella che avevo
cancellato. Corretti entrambi, più il readme del design system, e l'intero pacchetto
scansionato: **0 riferimenti obsoleti, 0 identità Brasil.**

---

# §35 · VERDETTO FINALE

| voce | risultato |
|---|---|
| CORE PRODUCT EXTERNAL-ONLY | **SÌ** nel modello (`coreRequiresPrivateData: false`); resta testo su CRM in Market Pulse |
| APP MODEL READY | **SÌ** |
| PORTFOLIO CONNECTED | **SÌ** |
| PRODUCT INTELLIGENCE CONNECTED | **SÌ** |
| VOCI DAL CAMPO CONNECTED | **SÌ** |
| FIELD SALES OPTIONAL/INBOUND DEMO | **SÌ** |
| ITALIAN COMPLETE | **NO** |
| OFFLINE SAFE | **NO** |
| NEW EXTERNAL LOAD INGESTED | **NO** |
| **READY FOR NEW EXTERNAL INTELLIGENCE LOAD** | **SÌ, con una riserva** |

## Perché SÌ

Il ricevitore esiste. Il prossimo pacchetto entra dietro `ITALY_APP_MODEL` e vince per
precedenza senza riscrivere una vista. Le tre entità che mancavano — prodotto,
portafoglio, voci pubbliche — ora hanno la loro forma nel modello, quindi il carico
successivo popola strutture esistenti invece di richiederne di nuove.

## La riserva, che va detta

**L'offline non è chiuso**, e non dipende dal mio template: React, ReactDOM e Babel
arrivano da `unpkg` attraverso il runtime della piattaforma; D3 e la geometria da
`jsdelivr` nell'accesso. Vanno serviti localmente prima della presentazione al cliente.
È l'unico difetto che può far fallire la demo in sala, e resta il primo intervento.

**La localizzazione delle viste profonde** resta aperta: la landing è pulita, ma la prosa
analitica del Polso di Mercato e le letture di business dell'Intelligence Scientifica sono
contenuto redazionale, non etichette.

**Search** ha l'indice costruito dal modello ma il routing dei risultati prodotto non è
stato convertito a `openProduct`.

Il carico può procedere; questi tre restano da chiudere prima del cliente.
