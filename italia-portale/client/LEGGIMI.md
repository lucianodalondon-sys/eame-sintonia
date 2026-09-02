# Sintonia · ADAMA Italia — pilota

Apri **index.html**. Reindirizza a `accesso.html` e da lì al portale.

## Struttura

```
index.html              ingresso
accesso.html            accesso (nessuna autenticazione — è un pilota dimostrativo)
portale.html            il portale
italy-app-model.js      IL CONTRATTO — unica interfaccia fra intelligence e viste
italy-canonical-windows.js   finestre colturali canoniche (verità a monte)
italy-label-verdicts.js      verdetti di etichetta (forza delle affermazioni)
italy-ingested.js       dati reali ingeriti
italy-catalog.js        catalogo commerciale pubblico
italy-*.js              dizionari e livelli di supporto
vendor/                 React, D3 e le altre librerie, servite in locale
assets/                 icone e logo ADAMA
_ds/adama-brandwell/    token e componenti del design system
vercel.json             configurazione di hosting statico
```

## Pubblicazione su Vercel

Nessuna build. Trascina questa cartella su Vercel, o:

```
vercel --prod
```

Framework preset **Other** · Build command: nessuno · Output directory: `.`

## Funziona senza rete

Tutte le librerie di esecuzione — React, ReactDOM, Babel, D3, TopoJSON e la geometria
della mappa — sono servite da `vendor/`. Il pacchetto **non contatta nessun CDN**.

Restano in uscita soltanto i **link alle fonti**: l'etichetta sul sito del Ministero, il
video, l'articolo. Quelli devono restare cliccabili — sono la tracciabilità su cui il
prodotto è costruito.

## Architettura

Il portale è **solo lo strato di presentazione**. Non crea verità agronomica.

Tutte le viste leggono `ITALY_APP_MODEL`, con precedenza:

```
CANONICAL  >  REAL_SOURCE  >  REAL_DERIVED  >  SYNTHETIC_DEMO  >  DEMO_SCENARIO
```

Il prossimo pacchetto di intelligence entra dietro il contratto e vince per precedenza,
senza riscrivere nessuna vista.

Una vista non sa mai quale ricerca ha prodotto un record: legge una collezione
normalizzata e nient'altro.

## Sintonia è intelligence esterna

Il nucleo funziona da informazione pubblica e osservabile. Non richiede CRM, ordini,
sell-in, sell-out, scorte o pipeline privata. Ciò che il mondo esterno non può rivelare
resta **NON OSSERVABILE DA FONTI ESTERNE** — non un segnaposto da riempire.

La **Rete Commerciale** è un'*integrazione opzionale dimostrativa*, separata in
navigazione: mostra come Sintonia potrebbe **ricevere** messaggi dal campo. Non invia.

## Quello che questo pilota mostra, e quello che non mostra

Il portale mostra **quello che le fonti dicono davvero**. Dove la fonte tace, la
schermata tace: un componente senza dato reale non viene riempito, viene tolto.

Alcune conseguenze che è giusto conoscere prima della presentazione:

- Il **Radar delle Opportunità** ha **3 convergenze**, non ventinove. Le ventinove
  precedenti erano scenari di presentazione e vivono dietro l'interruttore
  **SCENARI DIMOSTRATIVI**, spento per impostazione predefinita. Con l'interruttore
  acceso nessun conteggio reale cambia.
- Le **3 opportunità** e 2 dei **3 segnali di futuro** arrivano marcati `REAL_DERIVED`
  dalla fonte stessa: sono convergenze derivate, non osservazioni grezze. Lo Stato dei
  dati lo mostra nella colonna giusta.
- Il **Polso di Mercato** ha 77 osservazioni di prezzo reali (Commissione Europea,
  settimanali) su sei colture. **Pomodoro, barbabietola e melo non hanno nessuna
  osservazione** e la scheda lo dichiara invece di mostrare un verdetto.
- Il **Monitoraggio Concorrenza** ha 503 attività pubbliche osservate. 414 sono annunci a
  pagamento che hanno raggiunto l'Italia; 89 sono video organici multipaese e **non**
  vengono presentati come osservati in Italia. 320 non nominano una coltura e 89 non
  hanno una data: sono esclusi da ogni elenco "recente" invece di riceverne una finta.
- Le **17 voci pubbliche** hanno fra **1 e 13 anni**. La schermata mostra "≈ 6 anni fa" e
  mai una data di calendario, perché l'unico riferimento temporale disponibile è quello
  relativo della piattaforma.
- Le **relazioni di portafoglio** sono 236: 12 verificate sull'etichetta, 7 non trovate in
  questa lettura, 217 dal registro nazionale. *Non trovato in questa lettura* non
  significa che ADAMA non abbia un prodotto — significa che qui non è stato provato.

## Ambiente dimostrativo

L'indicatore **AMBIENTE DIMOSTRATIVO** in alto a destra apre lo **Stato dei dati**: per
ogni livello, quanti record sono reali, quanti derivati e quanti dimostrativi.

Nessun dato dimostrativo afferma un'osservazione, attribuisce un record a un'istituzione
reale o presenta una persona simulata come dipendente ADAMA.
