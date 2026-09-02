# Sintonia · ADAMA Italia — pilota

Apri **index.html**. Reindirizza a `accesso.html` e da lì al portale.

## Struttura

```
index.html              ingresso
accesso.html            accesso (nessuna autenticazione — è un pilota dimostrativo)
portale.html            il portale
italy-app-model.js      ADATTATORE — unica interfaccia fra intelligence e viste
italy-canonical-windows.js   finestre colturali canoniche (verità a monte)
italy-label-verdicts.js      verdetti di etichetta (forza delle affermazioni)
italy-ingested.js       dati reali ingeriti
italy-catalog.js        catalogo commerciale pubblico
italy-*.js              dizionari e livelli di supporto
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

## Architettura

Il portale è **solo lo strato di presentazione**. Non crea verità agronomica.

Tutte le viste leggono `ITALY_APP_MODEL`, con precedenza:

```
CANONICAL  >  REAL_SOURCE  >  REAL_DERIVED  >  SYNTHETIC_DEMO
```

Il prossimo pacchetto di intelligence entra dietro l'adattatore e vince per precedenza,
senza riscrivere nessuna vista.

## Sintonia è intelligence esterna

Il nucleo funziona da informazione pubblica e osservabile. Non richiede CRM, ordini,
sell-in, sell-out, scorte o pipeline privata. Ciò che il mondo esterno non può rivelare
resta **NON OSSERVABILE DA FONTI ESTERNE** — non un segnaposto da riempire.

La **Rete Commerciale** è un'*integrazione opzionale dimostrativa*, separata in
navigazione: mostra come Sintonia potrebbe **ricevere** messaggi dal campo. Non invia.

## Ambiente dimostrativo

L'indicatore **AMBIENTE DIMOSTRATIVO** in alto a destra apre lo **Stato dei dati**:
per ogni livello, quanti record sono reali e quanti dimostrativi.

Nessun dato dimostrativo afferma un'osservazione, attribuisce un record a un'istituzione
reale o presenta una persona simulata come dipendente ADAMA.

## ⚠ Dipendenza di rete — da chiudere prima del cliente

Il runtime carica React, ReactDOM e Babel da `unpkg.com`; l'accesso carica D3 e la
geometria della mappa da `jsdelivr`. **Con la rete disponibile funziona.**

Per una presentazione senza rete garantita questi pacchetti vanno serviti localmente.
È l'unico intervento tecnico rimasto e il primo consigliato.
