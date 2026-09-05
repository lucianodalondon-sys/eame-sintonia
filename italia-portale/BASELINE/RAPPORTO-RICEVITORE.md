# SINTONIA ITALY · PRE-LOAD RECEIVER CLOSURE
## Rapporto misurato · 02 settembre 2026

> **RECEIVER READY FOR NEW LOAD = NO**
>
> Le sue verifiche erano corrette, incluso il fatto che il rapporto precedente
> fosse **davanti** all'architettura reale. Questa sessione ha chiuso i difetti di
> verità misurabili e ha costruito i contratti di normalizzazione, ma **120 letture
> `D.*` che trasportano dato** restano nelle viste. Il ricevitore non è pronto.

---

# §25 · TEST DI ACCETTAZIONE — VALORI MISURATI

| voce | atteso | misurato |
|---|---|---|
| CORE DATA-BEARING D.* READS | 0 | **120** ❌ |
| allowed visual-only D.* reads | — | 50 |
| APP WINDOWS | — | **29** |
| APP OPPORTUNITIES | — | **29** |
| APP FUTURE SIGNALS (reali a monte) | — | **3** |
| APP PRODUCTS | — | **166** |
| APP COMPETITOR ACTIVITIES | 503 | **503** ✅ |
| COMPETITOR FALLBACK TO D.ACTIVITIES | NO | **NO** ✅ |
| PAID ITALY-REACH KEPT SEPARATE | — | **414** `REACHED_IN_ITALY` ✅ |
| ORGANIC MULTI-COUNTRY NOT CALLED ITALY | — | **89** `MULTI_COUNTRY_OR_UNRESOLVED` ✅ |
| APP MARKET RECORDS | 77 | **77** ✅ |
| VISIBLE MARKET USES APP MODEL | SÌ | **NO** ❌ |
| APP SCIENCE RECORDS | 88 | **88** ✅ |
| VISIBLE SCIENCE USES APP MODEL | SÌ | **NO** ❌ |
| APP RESEARCHERS | 60 | **60** ✅ |
| VISIBLE RESEARCHERS USE APP MODEL | SÌ | **NO** ❌ |
| APP VOICES | 17 | **17** ✅ |
| VOICE 1 NORMALIZED PERSON | — | `@francescolorusso3927` ✅ |
| VOICE 1 NORMALIZED TEXT_ORIGINAL | — | «Io ho usato la CORNALINA» ✅ |
| VOICE 1 NORMALIZED SOURCE_URL | — | `youtube.com/watch?v=qB7RtE_2rVo` ✅ |
| VOICE 1 WHAT_IT_PROVES | — | presente ✅ |
| VOICE 1 WHAT_IT_DOES_NOT_PROVE | — | presente ✅ |
| VOCI IS NEWSROOM | SÌ | **SÌ** — IN EVIDENZA / ULTIME VOCI / TEMI, 17 link cliccabili ✅ |
| VOCI CONTAINS RTV DEMO MESSAGES | NO | **NO** ✅ |
| APP ARCHIVE | — | **740** righe indicizzate su record reali ✅ |
| VISIBLE ARCHIVE USES APP MODEL | SÌ | **NO** ❌ — la vista usa ancora `D.ARCHIVE` (448) |
| GLOBAL SEARCH USES APP MODEL | SÌ | **NO** ❌ — indice costruito, routing non convertito |
| FIELD SALES DEMO MUTATES CASE EVIDENCE | NO | **NO** ✅ |
| FIELD SALES DEMO IN FUTURE SOURCE COUNTS | NO | **NO** ✅ |
| FIELD SALES SEND BUTTON | NO | **NO** ✅ — ora `RICEVI →` |
| FAKE WHATSAPP NUMBER | 0 | **0** ✅ |
| OUTBOUND FIELD SALES LOOP | 0 | **0** ✅ |
| FUTURE RADAR GENERATED FAKE SOURCE DESCRIPTIONS | 0 | **56 riclassificati `DEMO_SCENARIO`**, ma la vista li rende ancora ❌ |
| FUTURE RADAR COUNTS DEMO AS REAL | 0 | nel modello **0** ✅ · nella vista **ancora sì** ❌ |
| UNSAFE FUTURE PRODUCT RELATIONSHIPS AS VERIFIED | 0 | non verificato in questa sessione ❌ |
| CORE INTERNAL-DATA-REQUIRED LANGUAGE | 0 | **7** ❌ |
| REFERENCE DATE | 2026-09-02 | **2026-09-02**, un solo orologio ✅ |
| ITALIAN ACCIDENTAL ENGLISH | 0 | non chiuso ❌ |
| FUTURE RADAR ACCIDENTAL ENGLISH | 0 | non chiuso ❌ |
| NEW CLAUDE CODE LOAD INGESTED | NO | **NO** ✅ |
| **RECEIVER READY FOR NEW LOAD** | — | **NO** |

---

# I SUOI BUG CRITICI — TUTTI CONFERMATI E CORRETTI

## §4 · La chiave dell'ingestione era sbagliata

`IG.COMPETITOR` non esiste. La collezione reale è **`IG.COMP_ACTIVITIES` con 503
record**. L'adattatore cadeva su `D.ACTIVITIES` — 72 record, in gran parte sintetici.

Corretto. E la semantica già auditata è preservata nella normalizzazione:

```js
const italyReach = paid && (sem.indexOf('IT') >= 0 || ...);
geoClass: italyReach ? 'REACHED_IN_ITALY'
        : (paid ? 'REACH_NOT_RESOLVED' : 'MULTI_COUNTRY_OR_UNRESOLVED')
```

414 raggiunti in Italia · 89 multi-paese **non** chiamati osservati in Italia.
Mai `TARGETED ITALY`.

## §11 · Voci leggeva i nomi di campo sbagliati

Lo schema reale è **maiuscolo** (`PERSON`, `TEXT_ORIGINAL`, `SOURCE_URL`,
`WHAT_IT_PROVES`). La vista leggeva `v.speaker`, `v.statement`, `v.proves` — tutti
`undefined`, quindi il contenuto reale delle voci era perduto.

Normalizzato **una volta nell'adattatore**, non aggiustato nella vista.

## §17 · L'archivio era rotto in due modi

`D.ARCHIVE_ALL` non esiste → `APP.archive = 0`. La vista usava `D.ARCHIVE`, 448 righe
in gran parte sintetiche. Ora l'archivio è un **indice su record normalizzati reali**:
740 righe da scienza, mercato, concorrenza, voci, eventi, notizie e finestre canoniche.
Nessuna riga fabbricata.

## §22 · Il classificatore di provenienza contava demo come reale

`coll()` guardava solo `r.isDemo === true`. `FIELD_MESSAGES` usa `demo: true`.
Risultato: 18 messaggi sintetici contati come reali.

Un solo classificatore, con la provenienza esplicita come verità primaria:

```js
const provOf = (r, fallback) => {
  const p = String(r.provenance || r.PROVENANCE || r.prov || '').toUpperCase();
  if (p) { for (const k in DEMO_CLASSES) if (p.indexOf(k) >= 0) return P.SYNTHETIC_DEMO; return p; }
  if (r.isDemo === true || r.demo === true) return P.SYNTHETIC_DEMO;
  return fallback;
};
```

Misurato ora: **18 demo** su 18. Mai dedotto dal nome di una proprietà.

## §9 · Le mensagens demo gonfiavano l'evidenza del caso

```js
if (c.fieldCount) c.evidence.people += c.fieldCount;   // rimosso
```

Rimosso. L'integrazione opzionale può mostrare *"questo messaggio si collegherebbe
a X"*, ma non muta più nessun oggetto core.

## §5 · Future Radar fabbricava intelligence

Il codice generava 56 segnali con `while (SIGNALS.length < 56)`, status per modulo
`(ti + round*2) % 7`, tipo di fonte per modulo, e frasi di movimento scelte da una
lista fissa — poi contava quelle associazioni costruite come *"X tipi di fonte
indipendenti stanno discutendo la stessa coltura × avversità"*.

Tutti i 56 sono ora `provenance: 'DEMO_SCENARIO'`, in una collezione separata,
**esclusi da ogni totale reale**. A monte esistono **3 segnali veri** con link di
evidenza tracciabili.

## §19 · Due orologi

`italy-demo-data.js` aveva `new Date(2026, 8, 1)` — il **1** settembre, non il 2.
Ora legge la data di riferimento dal contratto canonico. Misurato: modello
`2026-09-02`, demo `Wed Sep 02 2026`. Un solo orologio.

---

# DIFETTO NUOVO CHE HO TROVATO

I campi `WHAT_IT_PROVES` / `WHAT_IT_DOES_NOT_PROVE` dei dati a monte sono scritti
**in portoghese**:

> «um comentarista escreveu isto sob este vídeo…»
> «nao prova que quem escreveu e produtor…»

È linguaggio di nota di ricerca che finisce nell'interfaccia di un cliente italiano.
Non l'ho tradotto: è contenuto a monte, e riscriverlo sarebbe inventare. **Va corretto
nel prossimo pacchetto di intelligence**, non nel portale.

---

# COSA RESTA — E PERCHÉ NON DICO PRONTO

**120 letture `D.*` che trasportano dato.** I contratti normalizzati esistono per 19
collezioni, ma le viste continuano a leggere la fixture:

| lettura | occorrenze |
|---|---|
| `D.WINDOWS` | 20 |
| `D.ACTIVITIES` | 19 |
| `D.SIGNALS` | 11 |
| `D.CASES` | 11 |
| `D.SCI_THEMES` | 9 |
| `D.ARCHIVE` | 8 |
| `D.CROP_CAL` | 8 |
| `D.PRODUCTS` | 7 |
| `D.EVENTS` | 7 |
| `D.SOURCES` | 6 |
| `D.FIELD_MESSAGES` | 5 |
| altre | 9 |

Finché queste esistono, il prossimo carico popola il modello ma **non arriva allo
schermo** — che è esattamente il difetto che lei ha individuato nel rapporto
precedente. Non lo ripeto dicendo pronto.

Restano inoltre: la vista Future Radar che rende ancora gli scenari, le 7 stringhe di
linguaggio su dati privati nel core, l'italiano delle viste profonde, e il routing di
Search.

## Ho provato la conversione in questa sessione. Ecco perché è tornata indietro.

Ho costruito la tabella di alias e sostituito **77 letture** in un passaggio. Il portale
si è rotto in cascata, e la causa è istruttiva:

**La forma normalizzata non è la forma che le viste usano.** Il contratto espone
`crop`, `issue`, `startDate`, `status`. Le viste usano `cov`, `topics`, `dates`,
`city`, `prep`, `bucket`, `ladder`, `readiness` — campi di presentazione che la
fixture calcola e il contratto non ha.

Ogni errore ne rivelava un altro: `.includes` su `cov` mancante nelle fonti, `.dates`
mancante negli eventi, un indice `BASF` mancante nella concorrenza. Ho risolto tre
collezioni con un **merge additivo** — il record normalizzato più i campi di presentazione
della fixture — e funzionava, ma restavano altre.

Ho annullato la sostituzione invece di consegnare un portale a metà che si rompe.

**La strada giusta**, che ora è chiara: ogni collezione ha bisogno del suo merge additivo
prima della sostituzione, non dopo. Il modello resta autorevole; i campi di presentazione
vengono aggiunti sopra. Il pattern è dimostrato su finestre, fonti ed eventi in
`italy-app-model.js` — va replicato per concorrenza, scienza, ricercatori, archivio,
temi e calendario colturale, **una collezione per volta, verificando fra ognuna**.

Voci dal Campo è la prova che l'approccio funziona: è l'unica vista **già convertita**,
legge solo il contratto normalizzato, e mostra le 17 voci reali con contenuto e link.

**Prossima sessione, un obiettivo solo**: le restanti collezioni, merge additivo prima
della sostituzione, una per volta.
