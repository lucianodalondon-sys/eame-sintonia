/* SINTONIA ITALIA · CIO CHE IL CLIENTE VEDE DAVVERO
   ---------------------------------------------------------------------------
   node audit/client-surface.mjs [--base http://host]

   Le altre guardie interrogano il modello e le proiezioni. Questa legge il DOM
   e basta, perche una parte dei difetti trovati stanotte non esisteva in
   nessuna proprieta: erano letterali scritti nel markup, e ogni controllo che
   camminava le props e passato sopra a tutti restando verde.

       UN CONTROLLO CHE GUARDA SOLO LE PROPRIETA
       DICE LA VERITA SULLE PROPRIETA.

   Nove cose, su venti schermate, nelle due lingue: undefined, null,
   [object Object], NaN, un enum grezzo lasciato come etichetta, una voce di
   navigazione che non porta da nessuna parte, un errore JavaScript fatale, una
   richiesta di rete fallita e un errore di console. Se non arriva a venti
   schermate, fallisce: non ha guardato abbastanza per assolvere.
   --------------------------------------------------------------------------- */
import fs from 'node:fs'; import http from 'node:http'; import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { navList } from './lib/nav-names.mjs';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const CLIENT=path.resolve(HERE,'..','client');
const argv=process.argv.slice(2);
const arg=(k,d)=>{const i=argv.indexOf('--'+k);return i>=0?argv[i+1]:d;};
const BASE=arg('base',null);
const PORT=Number(arg('port',8999));
const T={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.css':'text/css','.png':'image/png','.ttf':'font/ttf','.otf':'font/otf'};
let srv=null;
if(!BASE){srv=http.createServer((q,r)=>{const u=decodeURIComponent((q.url||'/').split('?')[0]);
  if(u==='/favicon.ico'){r.writeHead(204).end();return;}
  fs.readFile(path.join(CLIENT,u==='/'?'/portale.html':u),(e,b)=>{if(e){r.writeHead(404).end('404');return;}
    r.writeHead(200,{'content-type':T[path.extname(u)]||'application/octet-stream'}).end(b);});});
  await new Promise(r=>srv.listen(PORT,r));}
const ORIGIN=BASE||`http://localhost:${PORT}`;
/* I NOMI DELLE VOCI VENGONO DAL DIZIONARIO — audit/lib/nav-names.mjs.
   Erano scritti a mano qui, e quando navFuture/navSources sono cambiati
   questo file ha smesso di trovarle senza dirlo. */
const NAV={it:navList('it'),en:navList('en')};
const EXEC=['/opt/pw-browsers/chromium-1194/chrome-linux/chrome','/opt/pw-browsers/chromium/chrome-linux/chrome'].find(p=>fs.existsSync(p));
const b=await chromium.launch({executablePath:EXEC,args:['--no-sandbox']});
const hits={undef:[],nul:[],objobj:[],nan:[],enum_:[],emptyChip:[],noTitle:[],fatal:[],net:[],console_:[]};
let screens=0;
for(const lang of ['it','en']){
  const p=await b.newPage({viewport:{width:1440,height:1400}});
  p.on('pageerror',e=>hits.fatal.push(lang+': '+e.message.slice(0,80)));
  p.on('requestfailed',r=>{if(!/vercel\.live/.test(r.url()))hits.net.push(lang+': '+r.url().slice(0,70));});
  p.on('response',r=>{if(r.status()>=400&&!/favicon/.test(r.url()))hits.net.push(lang+': '+r.status()+' '+r.url().slice(0,60));});
  p.on('console',m=>{if(m.type()==='error'&&!/\{\{/.test(m.text()))hits.console_.push(lang+': '+m.text().slice(0,80));});
  await p.goto(`${ORIGIN}/portale.html`,{waitUntil:'networkidle',timeout:120000});
  await p.waitForTimeout(1200);
  if(lang==='en'){await p.evaluate(()=>{const e=[...document.querySelectorAll('span,div')].find(x=>x.textContent.trim()==='EN');let n=e;for(let i=0;i<5&&n;i++){if(getComputedStyle(n).cursor==='pointer'){n.click();return;}n=n.parentElement;}});await p.waitForTimeout(900);}
  for(const label of NAV[lang]){
    const ok=await p.evaluate((t)=>{const h=document.querySelector(`[title="${t}"]`);if(!h)return false;let n=h;for(let i=0;i<4&&n;i++){if(getComputedStyle(n).cursor==='pointer'){n.click();return true;}n=n.parentElement;}h.click();return true;},label);
    if(!ok){hits.noTitle.push(lang+' nav '+label+' non raggiungibile');continue;}
    await p.waitForTimeout(700); screens++;
    const r=await p.evaluate(()=>{
      const txt=document.body.innerText||'';
      const raw=[];
      for(const e of document.querySelectorAll('main *')){
        if(e.children.length) continue;
        const t=(e.innerText||'').trim();
        if(/^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+$/.test(t)) raw.push(t);
      }
      return {
        undef:(txt.match(/\bundefined\b/g)||[]).length,
        nul:(txt.match(/\bnull\b/g)||[]).length,
        objobj:(txt.match(/\[object Object\]/g)||[]).length,
        nan:(txt.match(/\bNaN\b/g)||[]).length,
        raw:[...new Set(raw)].slice(0,5),
      };
    });
    if(r.undef) hits.undef.push(`${lang}·${label}: ${r.undef}`);
    if(r.nul) hits.nul.push(`${lang}·${label}: ${r.nul}`);
    if(r.objobj) hits.objobj.push(`${lang}·${label}: ${r.objobj}`);
    if(r.nan) hits.nan.push(`${lang}·${label}: ${r.nan}`);
    if(r.raw.length) hits.enum_.push(`${lang}·${label}: ${r.raw.join(' ')}`);
  }
  await p.close();
}
await b.close(); if(srv) srv.close();
console.log(`\n  SWEEP · ${screens} schermate (attese 20)`);
const rows=[['undefined',hits.undef],['null',hits.nul],['[object Object]',hits.objobj],['NaN',hits.nan],
  ['raw enum',hits.enum_],['nav non raggiungibile',hits.noTitle],['fatal JS',hits.fatal],
  ['network',hits.net],['console error',hits.console_]];
let bad=0;
for(const [n,l] of rows){ if(l.length) bad+=l.length;
  console.log(`  ${l.length?'\x1b[31mFAIL\x1b[0m':'\x1b[32mOK  \x1b[0m'} ${n.padEnd(24)} ${l.length}`);
  l.slice(0,4).forEach(x=>console.log('        '+x)); }
if(screens<20) { console.log('  \x1b[31mFAIL\x1b[0m schermate insufficienti'); bad++; }
console.log(`\n  totale: ${bad}\n`);
process.exit(bad===0?0:1);
