# client/vendor — runtime assets served from the package

Every file here is a **runtime dependency**: without it the portal does not boot or
does not draw. They used to be loaded from a public CDN (unpkg / jsDelivr), which
meant a client demo died the moment the room had no network. They are now part of
the package and are referenced by relative path.

Nothing in this folder is data, evidence or a source. Outbound source links
(Ministero labels, YouTube videos, DOIs, OpenAlex, company pages) are **not**
vendored and must stay clickable — that traceability is the product.

## Files

| File | Package · version | Bytes | SHA-256 | Upstream |
|---|---|---|---|---|
| `d3-7.9.0.min.js` | d3 7.9.0 | 279 706 | `f2094bbf6141b359722c4fe454eb6c4b0f0e42cc10cc7af921fc158fceb86539` | unpkg.com/d3@7.9.0/dist/d3.min.js |
| `topojson-client-3.1.0.min.js` | topojson-client 3.1.0 | 7 169 | `25cd02ae486cc5063e0215a4e4cfb15de83700c87ac48bac4d57dc6aaf3ebb89` | unpkg.com/topojson-client@3.1.0/dist/topojson-client.min.js |
| `world-atlas-2.0.2-countries-110m.json` | world-atlas 2.0.2 | 107 761 | `2516c915867c7baf18ddec727aec46c315541a07cfb3d79a6559b05d5e94eee8` | cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json |
| `react-18.3.1.production.min.js` | react 18.3.1 (UMD, production) | 10 751 | `d949f1c3687aedadcedac85261865f29b17cd273997e7f6b2bfc53b2f9d4c4dd` | unpkg.com/react@18.3.1/umd/react.production.min.js |
| `react-dom-18.3.1.production.min.js` | react-dom 18.3.1 (UMD, production) | 131 835 | `35f4f974f4b2bcd44da73963347f8952e341f83909e4498227d4e26b98f66f0d` | unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js |
| `babel-standalone-7.29.0.min.js` | @babel/standalone 7.29.0 | 3 137 752 | `2623a9e22809915ce789b4461154e277ddce520d5a4320c14d44332a5d0dcea0` | unpkg.com/@babel/standalone@7.29.0/babel.min.js |
| `jspdf-2.5.2.umd.min.js` | jspdf 2.5.2 (UMD, minified) | 365 730 | `0b1b02a0bd497200a3052a4268f23f1ff980ac7f03f7e43c128cdc858ab0b7a7` | unpkg.com/jspdf@2.5.2/dist/jspdf.umd.min.js — **una stringa modificata, vedi sotto** |

## Integrity verification (done at download time)

Five of the six were previously loaded through `<script>` tags carrying a
Subresource Integrity hash. The downloaded bytes were hashed with SHA-384 and
compared against the hash the old tag carried. **All five matched.**

| File | SRI in the old reference | Result |
|---|---|---|
| `d3-7.9.0.min.js` | `sha384-CjloA8y00+1SDAUkjs099PVfnY2KmDC2BZnws9kh8D/lX1s46w6EPhpXdqMfjK6i` | MATCH |
| `topojson-client-3.1.0.min.js` | `sha384-Ukv1p/xTma6P4/2bY5KzWBw+ydSpXmhCMtyciIQVDJ1RmOxtCYNMF1uXT9T63H67` | MATCH |
| `react-18.3.1.production.min.js` | `sha384-DGyLxAyjq0f9SPpVevD6IgztCFlnMF6oW/XQGmfe+IsZ8TqEiDrcHkMLKI6fiB/Z` | MATCH |
| `react-dom-18.3.1.production.min.js` | `sha384-gTGxhz21lVGYNMcdJOyq01Edg0jhn/c22nsx0kyqP0TxaV5WVdsSH1fSDUf5YJj1` | MATCH |
| `babel-standalone-7.29.0.min.js` | `sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y` | MATCH |
| `world-atlas-2.0.2-countries-110m.json` | none — it was fetched by `d3.json()`, which carries no SRI | n/a, SHA-384 recorded below |

`world-atlas-2.0.2-countries-110m.json` SHA-384:
`sha384-yOCJ+8ShBm8UDqtAVtAvxTDDf4gXo5edxl/YG0FmVC5OTmqVLl7utuVGBDEeZWHf`

Re-verify any file at any time:

```
node -e "const c=require('crypto'),f=require('fs');const p=process.argv[1];console.log(p, f.readFileSync(p).length, c.createHash('sha256').update(f.readFileSync(p)).digest('hex'))" <file>
```

## Who loads what

- `d3-7.9.0.min.js`, `topojson-client-3.1.0.min.js` — `<script>` tags in
  `accesso.html`, for the login-screen world map.
- `world-atlas-2.0.2-countries-110m.json` — fetched at runtime by `d3.json()` in
  `accesso.html`. If it ever fails to load the `.catch` simply paints the stage
  background; the page keeps working without the map.
- `react-…`, `react-dom-…` — loaded **unconditionally** by `support.js`
  (`loadReactUmd()`), before `init()`. The portal cannot boot without them.
- `babel-standalone-7.29.0.min.js` — loaded **lazily and conditionally** by
  `ensureBabel()` in `support.js`, and only when an `<x-import>` points at a
  `.jsx`/`.tsx` URL. All three `<x-import>` tags in `portale.html` use
  `component-from-global-scope` with no URL, so on the current portal Babel is
  never fetched. It is vendored anyway so that the loader has no path that can
  reach the network.

## L'unica riga di vendor modificata: jsPDF

`jspdf-2.5.2.umd.min.js` conteneva UN indirizzo CDN, dentro il ramo
`case "pdfobjectnewwindow":` di `output()`: quel ramo scrive nella finestra
nuova un `<script src="https://cdnjs.cloudflare.com/…/pdfobject.min.js">`.

    UN RAMO CHE OGGI NESSUNO CHIAMA E UN RAMO CHE DOMANI QUALCUNO CHIAMA.

`italy-pdf.js` usa solo `save()` e `output('arraybuffer')` — misurato, quattro
chiamate, nessuna `pdfobjectnewwindow`. L'indirizzo era quindi codice morto, ma
codice morto che il browser porta con se. E stato sostituito con
`about:blank#pdfobject-not-vendored-in-this-package`, riempito fino alla stessa
lunghezza: se quel ramo venisse mai chiamato fallirebbe A VISTA invece di
aprire in silenzio una connessione verso un CDN pubblico.

Nessuna logica toccata. Verificato dopo la modifica: `new jsPDF()`, `text()` e
`output('arraybuffer')` producono gli STESSI 3 173 byte del file originale.
SHA-256 prima `85ba2cc3ff858a20fa49fe6e457bec863ea40b55a9f3725e58a940e62f6f61a4`,
dopo `0b1b02a0bd497200a3052a4268f23f1ff980ac7f03f7e43c128cdc858ab0b7a7`.

## Why the integrity attributes were dropped

`support.js` keeps `REACT_SRI` / `REACT_DOM_SRI` / `BABEL_SRI`, now empty strings.
Setting an `integrity` attribute also forces `crossOrigin="anonymous"`, which fails
for a same-origin package file under the `file://` protocol — the way an offline
demo is opened. The bytes are inside the package and their hashes are in this file,
so integrity is pinned here instead of at load time.

## Note on `support.js`

`client/support.js` is marked *"GENERATED from dc-runtime/src/*.ts — do not edit"*.
The generator is not part of this package, so the file was edited directly. The edit
is confined to the three URL constants and the three SRI constants in the
`// src/cdn.ts` section (around line 1143). No logic was changed. If dc-runtime is
ever regenerated, this rewiring must be reapplied.
