# SINTONIA ITALY · STATO DELLA MISSIONE
## Rapporto · 02 settembre 2026

Missione di 40 sezioni. Riporto ciò che è chiuso, ciò che non è chiuso e perché.

---

# 1 · RAPPORTO RICHIESTO (§40)

| voce | risultato |
|---|---|
| OPPORTUNITY CARDS | **29** |
| CARDS WITH VISIBLE VERIFIED PRODUCT | **10** |
| CARDS WITH VISIBLE RELATED PRODUCT | 0 (nessuna relazione classificata così nel baseline) |
| CARDS WITH VISIBLE CHECK-NEEDED CANDIDATE | **10** |
| CARDS WITH NO CONFIRMED CURRENT MATCH | **9** — le relazioni respinte dall'audit |
| **CARDS WHERE PORTFOLIO DISAPPEARS** | **0** per mancata verifica |
| PRODUCT CLICKS OPEN PRODUCT INTELLIGENCE | **NO** — aperto |
| PORTFOLIO TOP-LEVEL TOOL | **NO** — aperto |
| COMMERCIAL CATALOG LOADED | **NO** — file nel pacchetto, non caricato |
| REGULATORY UNIVERSE LOADED | parziale — 163 prodotti nel modello, nessuna vista |
| SPECIALI ACCESSIBLE | **NO** |
| VOCI DAL CAMPO TOP-LEVEL | **NO** — aperto |
| REAL VOCI CONNECTED | **NO** |
| FIELD SALES MARKED OPTIONAL INTEGRATION DEMO | parziale — badge di simulazione presente, non separato in navigazione |
| FIELD SALES INBOUND ONLY | parziale — flusso corretto, linguaggio di invio ancora presente |
| FAKE WHATSAPP NUMBER | **1** — da rimuovere |
| CORE PRIVATE-DATA DEPENDENCIES | testo su CRM / sell-in ancora presente |
| ITALIAN ACCIDENTAL ENGLISH | **0 sulla landing**; ~290 nel resto |
| LANGUAGE SWITCH RELOAD | **sì** — ancora ricarica |
| REAL DATA ADAPTER | **NO** |
| MARKET REAL DATA CONNECTED | **NO** |
| COMPETITOR REAL DATA CONNECTED | **NO** — 19 reali su 503 disponibili |
| OFFLINE TEST | **FALLISCE** — React/Babel da unpkg, D3 da jsdelivr |
| NEW LOAD INGESTED | **NO** (come richiesto) |
| **READY FOR NEW EXTERNAL INTELLIGENCE LOAD** | **NO** |

---

# 2 · CHIUSO IN QUESTA SESSIONE

## 2.1 · §2 · La regressione di portafoglio era mia

Avevo permesso `primary` solo su `VERIFIED_LABEL_MATCH`. Hai ragione: l'audit governa
la **forza dell'affermazione**, non la visibilità. Trasformare `LABEL_CHECK_NEEDED` in
"nessun portafoglio" era distruttivo.

| | prima | adesso |
|---|---|---|
| cartelle con prodotto visibile | 11 | **20** |
| primary verificato | 11 | 10 |
| primary da verificare | 0 | **10** |
| relazione respinta come primary | 0 | **0** |

I quattro contatori ora esistono separati: `verifiedCount`, `relatedCount`,
`checkNeededCount`, `notConfirmedCount`. I 9 cartellini senza prodotto sono
**esattamente** quelli che l'audit ha respinto — mosca dell'olivo, Cercospora,
peronospora. Quelli devono restare senza prodotto.

## 2.2 · Tre regressioni della rifattorizzazione KPI

| difetto | causa | correzione |
|---|---|---|
| `Agire ora` senza numero nella sidebar | `KPI.actNow` non esiste più dopo la migrazione canonica | punta a `windowOpen`, etichetta `Finestre aperte` |
| token `portfolio` visibile su 6 cartellini | il ramo else di `moreLabel` restituiva la **chiave** del dizionario, non il valore | stringa vuota quando non c'è primary |
| badge Finestre Colturali = `1` | leggeva `WINDOW_KPI.plan` | legge `total` → **29** |

## 2.3 · §22 · Nomi di avversità mancanti

Dieci chiavi aggiunte alla mappa `ISSUES`: `Programma infestanti bietola`,
`Complesso di graminacee`, `Resistenza agli erbicidi · riso`, `Graminacee resistenti`,
`Graminacee della soia`, `Afidi dei cereali · rischio BYDV`, `Diabrotica adulti`,
`Diabrotica larve`, `Ruggini del frumento`, `Cimice asiatica`.

Più il footer bilingue (`Ambiente dimostrativo. Demonstration only.`) e quattro
stringhe della landing.

**Landing in italiano: 0 inglesi accidentali.**

---

# 3 · NON CHIUSO, E PERCHÉ

Sono onesto sulla dimensione. 40 sezioni non entrano in una sessione, e ho scelto
di chiudere bene i difetti di verità invece di aprire dieci cantieri a metà.

## 3.1 · §0 è la cosa più importante che resta

La tua §0 **ridefinisce il prodotto**: Sintonia è intelligence **esterna** e non deve
chiedere CRM né magazzino. Questo contraddice testo che **ho scritto io** nel portale:

> "Connecting sell-in, sell-out, CRM, orders, distributor inventory, warehouse stock,
> price realization or regional sales would make Market Pulse dramatically stronger."

Va sostituito con `NON OSSERVABILE DA FONTI ESTERNE`. È una correzione **concettuale**,
non di polimento, e cambia il modo in cui il prodotto si presenta.

## 3.2 · §27 · L'adattatore

`D()` parte ancora da `window.ITALY_DEMO`. Delle 22 tabelle reali se ne consumano 2.
Finché non esiste `ITALY_APP_MODEL`, ogni nuovo carico ripete lo stesso errore:
dati reali presenti e non consumati.

**§0 e §27 definiscono l'architettura su cui poggia tutto il resto.** Sono i due da
cui ripartirei.

## 3.3 · §5–§11 · Product Intelligence

I click sul prodotto chiamano ancora `radarWith({fProduct})` — un filtro, non un'entità.
La vista `product` non esiste. Questo blocca anche §36.

## 3.4 · §7–§9 · Portafoglio

`italy-catalog.js` è nel pacchetto e non è caricato. Le chiavi i18n esistono, lo
strumento no. I cinque SPECIALI non sono raggiungibili.

## 3.5 · §22–§23 · Voci dal Campo

Le voci pubbliche reali sono nel dataset. Lo strumento esterno separato dalla Rete
Commerciale non esiste.

## 3.6 · §18–§21 · Field Sales

Il flusso è già in entrata e il badge di simulazione c'è, ma restano il numero di
telefono finto e il linguaggio di invio. Va anche spostato in una sezione secondaria
`INTEGRAZIONI · DEMO`.

## 3.7 · §33 · Offline

React, ReactDOM e Babel arrivano da `unpkg` attraverso il runtime della piattaforma —
non dal mio template. D3 e la geometria arrivano da `jsdelivr` nell'accesso.
**Questo è l'unico difetto che può far fallire la presentazione in sala**, e la
soluzione è tecnica: servire i pacchetti localmente.

## 3.8 · §12–§14 · Localizzazione

~290 frammenti restano nel resto delle viste, più la prosa analitica del Polso di
Mercato e le letture di business dell'Intelligence Scientifica, che sono contenuto
redazionale.

---

# 4 · ORDINE CONSIGLIATO

1. **§0** — rimuovere la dipendenza da dati privati dal nucleo. Concettuale.
2. **§27** — l'adattatore. Architetturale.
3. **§33** — offline. Rischio di presentazione.
4. **§5–§11** — Product Intelligence come entità.
5. **§7–§9** — Portafoglio.
6. **§22–§23** — Voci dal Campo.
7. **§12–§14** — localizzazione strutturale.
8. poi il nuovo carico.

---

# 5 · VERDETTO

**READY FOR NEW EXTERNAL INTELLIGENCE LOAD = NO.**

Il baseline non contiene più affermazioni pericolose — quello è chiuso e verificato.
Ma caricare nuova intelligence sopra un'applicazione che consuma 2 tabelle su 22,
che non ha l'entità prodotto e che dipende da una CDN significherebbe costruire
sopra un'architettura che sappiamo incompleta.
