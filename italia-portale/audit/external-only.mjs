/* SINTONIA ITALIA · SOLO CIO CHE SI PUO OSSERVARE DA FUORI
   ---------------------------------------------------------------------------
   node audit/external-only.mjs [--base http://host] [--port 8971]

   SINTONIA CORE e intelligence ESTERNA. Non ha il CRM, non vede il sell-in ne
   il sell-out, non conosce gli ordini, le giacenze, il margine, la domanda del
   rivenditore, la pipeline privata, i messaggi privati.

       QUANDO UNA COSA NON E OSSERVABILE DA FONTI ESTERNE,
       IL PORTALE DEVE DIRE CHE NON LO E — NON INVENTARLA.

   Questo controllo cammina OGNI schermata nelle due lingue e cerca il
   vocabolario del dato privato. Non cerca parole sciolte («mercato» e legittimo):
   cerca le frasi che affermerebbero un accesso che il prodotto non ha. Una
   navigazione che non riesce conta come fallimento, non come schermata pulita:
   un controllo che non ha guardato non ha assolto.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
const EXEC = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  '/opt/pw-browsers/chromium/chrome-linux/chrome'].find((p) => fs.existsSync(p));
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const BASE = arg('base', null);
const PORT = Number(arg('port', 8971));
const CLIENT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'client');
let server = null;
if (!BASE) {
  const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
    '.json': 'application/json', '.css': 'text/css', '.png': 'image/png', '.ttf': 'font/ttf', '.otf': 'font/otf' };
  server = http.createServer((q, r) => {
    const u = decodeURIComponent((q.url || '/').split('?')[0]);
    if (u === '/favicon.ico') { r.writeHead(204).end(); return; }
    fs.readFile(path.join(CLIENT, u === '/' ? '/portale.html' : u), (e, buf) => {
      if (e) { r.writeHead(404).end('404'); return; }
      r.writeHead(200, { 'content-type': TYPES[path.extname(u)] || 'application/octet-stream' }).end(buf);
    });
  });
  await new Promise((r) => server.listen(PORT, r));
}
const B = BASE || `http://localhost:${PORT}`;
const NAV = {
  it: ['Radar delle Opportunità','Radar Futuro','Finestre Colturali','Polso di Mercato','Portafoglio',
       'Voci dal Campo','Concorrenza','Intelligence Scientifica','Archivio','Fonti'],
  en: ['Opportunity Radar','Future Radar','Crop Windows','Market Pulse','Portfolio',
       'Field Voices','Competitor Watch','Scientific Intelligence','Archive','Sources'],
};
/* Vocabolario proibito: dato privato spacciato per osservazione. Ogni voce e
   una frase, non una parola sciolta, per non incendiarsi su "mercato". */
const FORBIDDEN = [
  /\bCRM\b/i, /\bsell[- ]?in\b/i, /\bsell[- ]?out\b/i,
  /\bordini (ricevuti|del cliente)\b/i, /\bpurchase orders?\b/i,
  /\b(stock|giacenz\w+) (di|del|in) magazzino\b/i, /\binventory level/i,
  /\bmargine (lordo|netto|commerciale)\b/i, /\b(gross|net) margin\b/i,
  /\bdomanda del (rivenditore|distributore)\b/i, /\bdealer demand\b/i,
  /\bpipeline (privata|commerciale interna)\b/i, /\bprivate pipeline\b/i,
  /\bmessaggi privati\b/i, /\bprivate messages\b/i,
  /\bquota di mercato ADAMA\b/i, /\bADAMA market share\b/i,
];
const b = await chromium.launch({ executablePath: EXEC, args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1440, height: 1400 } });
const click = (t) => p.evaluate((t) => {
  const h = document.querySelector(`[title="${t}"]`); if (!h) return false;
  let n = h; for (let i=0;i<4&&n;i++){ if(getComputedStyle(n).cursor==='pointer'){n.click();return true;} n=n.parentElement; }
  h.click(); return true;
}, t);
const hits = [], missed = [];
let screens = 0;
for (const lang of ['it','en']) {
  await p.goto(`${B}/portale.html`, { waitUntil:'networkidle', timeout:120000 });
  await p.waitForTimeout(1200);
  if (lang==='en') {
    await p.evaluate(() => { const e=[...document.querySelectorAll('span,div')].find(x=>x.textContent.trim()==='EN');
      let n=e; for(let i=0;i<5&&n;i++){ if(getComputedStyle(n).cursor==='pointer'){n.click();return;} n=n.parentElement; } });
    await p.waitForTimeout(900);
  }
  for (const label of NAV[lang]) {
    const ok = await click(label);
    if (!ok) { missed.push(`${lang}·${label}`); continue; }
    await p.waitForTimeout(650);
    screens++;
    const t = await p.evaluate(() => document.body ? document.body.innerText : null);
    if (t === null) { missed.push(`${lang}·${label} (pagina mai caricata)`); continue; }
    for (const re of FORBIDDEN) {
      const m = t.match(re);
      if (m) {
        const i = t.indexOf(m[0]);
        hits.push(`${lang} · ${label} · ${re} -> "${t.slice(Math.max(0,i-60), i+80).replace(/\n/g,' ')}"`);
      }
    }
  }
}
await b.close();
if (server) server.close();
console.log(`\n  §7 EXTERNAL-ONLY · schermate ispezionate: ${screens} (attese 20)`);
if (missed.length) { console.log('  NAVIGAZIONI MANCATE (contano come fallimento):'); missed.forEach(m=>console.log('    - '+m)); }
if (hits.length) { console.log('  VOCABOLARIO PRIVATO TROVATO:'); hits.forEach(h=>console.log('    - '+h)); }
else console.log('  nessun dato privato dichiarato sullo schermo');
const bad = hits.length + missed.length + (screens < 20 ? 1 : 0);
console.log(`  problemi: ${bad}\n`);
process.exit(bad === 0 ? 0 : 1);
