/* GATE · MAPPA DELLE AZIONI CANONICA — cinque aree, su tutte le opportunita,
   senza che nessuna area riceva un'azione che i dati non provano. */
import { mount } from '../lib/harness.mjs';

const M = mount({});
const AM = M.AM, ctx = M.ctx;
const CANONICHE = AM.AREE_CANONICHE || [];

const B = ctx.MEETING_SURFACE.build('it');
const ids = [];
for (const k of Object.keys(B)) if (Array.isArray(B[k])) for (const c of B[k]) if (c && c.id) ids.push(c.id);
const CASI = [...new Set(ids)];

/* ── 1 · cinque aree su tutte le opportunita, nelle due lingue ────────────── */
let completi = 0, incompleti = [];
const etichette = {};   /* codice -> { it: Set, en: Set } */
const righe = [];
for (const lang of ['it', 'en']) {
  for (const id of CASI) {
    const v = M.vals({ view: 'mcase', mCaseId: id, lang });
    const a = v.mcActions || [];
    const codici = a.map(x => x.DEPARTMENT);
    const mancanti = CANONICHE.filter(c => codici.indexOf(c) < 0);
    const estranei = codici.filter(c => CANONICHE.indexOf(c) < 0);
    if (!mancanti.length && !estranei.length) completi++;
    else incompleti.push({ lang, id, mancanti, estranei });
    for (const x of a) {
      (etichette[x.DEPARTMENT] = etichette[x.DEPARTMENT] || { it: new Set(), en: new Set() })[lang].add(x.deptLabel);
      righe.push({ lang, id, ...x });
    }
  }
}

/* ── 2 · un reparto, un nome per lingua ──────────────────────────────────── */
let doppi = 0;
console.log('REPARTO'.padEnd(24), 'IT'.padEnd(24), 'EN');
for (const c of CANONICHE) {
  const e = etichette[c] || { it: new Set(), en: new Set() };
  if (e.it.size > 1 || e.en.size > 1) doppi++;
  console.log(c.padEnd(24), [...e.it].join(' | ').padEnd(24), [...e.en].join(' | '));
}

/* ── 3 · nessuna azione inventata ────────────────────────────────────────── */
/* ── DUE NUMERI, NON UNO ───────────────────────────────────────────────────
   La prima versione di questo controllo accettava la DIPENDENZA al posto della
   PROVA e stampava «azioni inventate = 0». Misurato: delle 57 righe che
   raccomandano qualcosa, 26 non portano NESSUNA prova — sono tutte
   «Stabilire la condizione della finestra», la cui ragione dichiarata e
   proprio che la condizione e ignota.

       CHIEDERE DI ACCERTARE CIO CHE NON SI SA NON E INVENTARE:
       E LA RISPOSTA ONESTA A UN'ASSENZA.
       MA UN PORTONE CHE NON DISTINGUE I DUE CASI NON LO STA DIMOSTRANDO.

   Si contano quindi separatamente: le righe che raccomandano senza ragione
   alcuna (inventate) e quelle la cui unica base e una dipendenza dichiarata
   (da accertare). Le seconde non sono un difetto — sono un numero che chi
   legge il rapporto ha il diritto di vedere. */
const AGISCE = new Set(['ACTION_STATE_ACT', 'ACTION_STATE_PREPARE', 'ACTION_STATE_VALIDATE']);
const inventate = [];
const soloDipendenza = [];
let raccomandano = 0;
for (const r of righe) {
  if (!AGISCE.has(r.stateToken)) continue;
  raccomandano++;
  const senzaPerche = !r.why || !String(r.why).trim();
  const senzaProva = !r.evidence || (Array.isArray(r.evidence) ? !r.evidence.length : !String(r.evidence).trim());
  const senzaDipendenza = !r.dependency || !String(r.dependency).trim();
  if (senzaPerche || (senzaProva && senzaDipendenza)) {
    inventate.push({ id: r.id, dept: r.DEPARTMENT, stato: r.stateToken, azione: r.actionToken,
      perche: senzaPerche ? 'senza perche' : 'senza prova ne dipendenza' });
  } else if (senzaProva) {
    soloDipendenza.push({ azione: r.actionToken, perche: r.whyToken });
  }
}

/* ── 4 · la mappa vecchia non arriva a nessuno schermo ────────────────────
   Non si cerca la PAROLA: «Portafoglio» e il nome di una schermata e
   «approvvigionamento» sta dentro «bilancio di approvvigionamento», una misura
   di mercato. Cercare parole accuserebbe il portale di parlare italiano.

       UNA PAROLA NON E UN'AREA. SI CERCA LA STRUTTURA.

   Si cerca quindi: (a) il markup che disegnava la mappa a sette, (b) qualunque
   riga resa che porti un codice di reparto o di area, e si verifica che ogni
   codice stia nelle cinque canoniche. */
import fs from 'node:fs';
const SORGENTE = fs.readFileSync(new URL('../../client/portale.html', import.meta.url), 'utf8');
const RESIDUI_MARKUP = ['data-area=', 'data-area-name=', 'cs.actionMapRows', 'cs.hasActionMap']
  .filter((t) => SORGENTE.indexOf(t) >= 0);

/* ── IL PRODOTTO ESCE DI CASA ANCHE IN PDF ────────────────────────────────
   Questo portone rendeva schermate e dichiarava pulito. Il documento che il
   cliente SCARICA non e una schermata: si costruisce in un gestore di clic e
   passa a `italy-pdf.js` un elenco `actionAreas`. Quella riga leggeva la mappa
   ritirata a sette aree e la traduceva col dizionario V21, che tiene ancora
   NORMATIVO, PORTAFOGLIO e TECNICO E SCIENTIFICO.

       UN PORTONE CHE GUARDA SOLO LO SCHERMO DICHIARA PULITO UN PRODOTTO CHE
       ESCE DI CASA IN PDF.

   Si misura percio anche la SORGENTE dei documenti: nessun elenco di aree puo
   nascere da `actionMap` ne passare per le etichette V21 delle aree ritirate. */
const SENZA_COMMENTI = SORGENTE.slice(SORGENTE.indexOf('<script type="text/x-dc"'))
  .replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
const RESIDUI_DOCUMENTO = [];
if (/actionAreas[\s\S]{0,200}?actionMap/.test(SENZA_COMMENTI)) RESIDUI_DOCUMENTO.push('actionAreas costruito da actionMap');
if (/V21\s*&&\s*T\.V21\[a\]/.test(SENZA_COMMENTI)) RESIDUI_DOCUMENTO.push('etichette V21 di area');
for (const c of ['SCIENCE_TECHNICAL', 'PORTFOLIO', 'REGULATORY']) {
  const re = new RegExp("(areaL|deptLabel|dept)\\s*[:=][^,;\\n]{0,60}" + c);
  if (re.test(SENZA_COMMENTI)) RESIDUI_DOCUMENTO.push('codice ritirato come area: ' + c);
}

const AMMESSE = ['meeting', 'future', 'windows', 'market', 'voices', 'competitors',
  'science', 'portfolio', 'archive', 'sources'];
const C = AM.collections;
const schermi = [];
for (const lang of ['it', 'en']) {
  for (const v of AMMESSE) schermi.push({ view: v, lang });
  for (const id of CASI) schermi.push({ view: 'mcase', mCaseId: id, lang });
  for (const r of C.opportunities.records) schermi.push({ view: 'case', caseId: r.id, lang });
  for (const r of C.cropWindows.records) schermi.push({ view: 'window', windowId: r.id, lang });
  schermi.push({ view: 'brief', caseId: C.opportunities.records[0].id, briefDept: 'MARKETING', lang });
}
/* ogni oggetto reso che dichiara un reparto o un'area */
const codiciFuori = new Map();
let resi = 0;
const cerca = (v, ctx, d = 0) => {
  if (d > 7 || v == null || typeof v !== 'object') return;
  if (Array.isArray(v)) { for (const x of v) cerca(x, ctx, d + 1); return; }
  const cod = v.DEPARTMENT || v.area || v.dept;
  if (cod && typeof cod === 'string' && /^[A-Z][A-Z_]{3,}$/.test(cod) && CANONICHE.indexOf(cod) < 0)
    codiciFuori.set(cod, (codiciFuori.get(cod) || 0) + 1);
  for (const k in v) { if (k === 'raw') continue; try { cerca(v[k], ctx, d + 1); } catch (e) {} }
};
for (const st of schermi) {
  const r = M.tryVals(st);
  if (!r.ok) continue;
  resi++;
  cerca(r.vals, st.view);
}
const vecchioVisibile = RESIDUI_MARKUP.length + codiciFuori.size + RESIDUI_DOCUMENTO.length;

console.log('');
console.log('MAPA_CANONICO                    = mappa della riunione · ' + CANONICHE.length + ' aree · ' + CANONICHE.join(', '));
console.log('43_OPORTUNIDADES_TESTADAS        = ' + CASI.length + ' casi × 2 lingue · completi ' + completi + '/' + (CASI.length * 2));
if (incompleti.length) for (const i of incompleti.slice(0, 6)) console.log('    INCOMPLETO', i.lang, i.id, 'mancanti', i.mancanti.join(','), 'estranei', i.estranei.join(','));
console.log('schermate rese                   = ' + resi + '/' + schermi.length);
console.log('MAPA_ANTIGO_VISIVEL              = ' + (vecchioVisibile ? 'SIM' : 'NAO'));
if (RESIDUI_MARKUP.length) console.log('    residui nel markup:', RESIDUI_MARKUP.join(' '));
if (RESIDUI_DOCUMENTO.length) console.log('    residui nei documenti scaricati:', RESIDUI_DOCUMENTO.join(' · '));
for (const [k, n] of codiciFuori) console.log('    codice di reparto fuori dalle cinque:', k, '×', n);
console.log('NOMI_DUPLICATI_PER_REPARTO       = ' + doppi);
console.log('ACOES_INVENTADAS_ENCONTRADAS     = ' + inventate.length);
const perAzione = {};
for (const x of soloDipendenza) perAzione[x.azione + ' · ' + x.perche] = (perAzione[x.azione + ' · ' + x.perche] || 0) + 1;
console.log('righe che raccomandano           = ' + raccomandano +
  ' · con prova ' + (raccomandano - soloDipendenza.length - inventate.length) +
  ' · con la sola dipendenza dichiarata ' + soloDipendenza.length);
for (const k of Object.keys(perAzione)) console.log('    ', perAzione[k], '×', k);
for (const i of inventate.slice(0, 10)) console.log('    ', i.id, i.dept, i.stato, '·', i.perche);
console.log('righe di azione misurate         = ' + righe.length + ' (attese ' + (CASI.length * CANONICHE.length * 2) + ')');
process.exitCode = (incompleti.length || vecchioVisibile || doppi || inventate.length) ? 1 : 0;
