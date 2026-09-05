#!/usr/bin/env node
/* SINTONIA · PORTAO DA LEI DE RELEVANCIA ADAMA
   ---------------------------------------------------------------------------
   Um caso vira OPORTUNIDADE quando — e so quando — se consegue ligar o facto a
   um produto ADAMA de forma defensavel. Antes desta lei, 30 dos 43 cartoes
   eram apresentados como oportunidade sem conseguir responder «por que isto e
   um caso para a ADAMA?».

       O LEITOR NAO PODE CONFUNDIR «PRECISAMOS INVESTIGAR»
       COM «TEMOS UMA OPORTUNIDADE ADAMA COMPROVADA».

   O que este portao mede, e que os testes em Python nao podem medir: o que
   chega ao BROWSER. A lei corre em Python; o veredito viaja impresso; o
   `meeting-surface.js` le-o. Entre os tres ha duas fronteiras, e uma lei que
   so vale de um lado nao vale.

   E mede uma premissa que so aqui se pode medir: o catalogo comercial esta no
   pacote embarcado, ilegivel para o gerador. Aqui pergunta-se-lhe se cada
   produto que a lei aceitou e mesmo da ADAMA.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(AQUI, '..', '..');
const CLIENTE = path.join(RAIZ, 'italia-portale', 'client');

const R = [];
const check = (id, fn) => {
  try { R.push({ id, ...fn() }); }
  catch (e) { R.push({ id, pass: false, detail: [`LANCOU: ${e.message}`] }); }
};

/* Le os artefactos como o browser os le: executando-os, na mesma ordem. */
const g = { window: {} };
vm.createContext(g);
for (const f of ['italy-handoff-v21.js', 'meeting-intelligence-snapshot.js',
                 'meeting-labels.js', 'adama-relevance.js', 'italy-casa.js',
                 'meeting-surface.js']) {
  vm.runInContext(fs.readFileSync(path.join(CLIENTE, f), 'utf8'), g);
}
const REL = g.window.ADAMA_RELEVANCE;
const CASA = g.window.ITALY_CASA;
const HAND = g.window.ITALY_HANDOFF_V21 || {};
const SURF = g.window.MEETING_SURFACE.build('it');
const SNAP = JSON.parse(fs.readFileSync(path.join(CLIENTE, 'meeting-intelligence-snapshot.json'), 'utf8'));

check('POPULACAO_43_INTACTA', () => {
  const bad = [];
  const n = SNAP.CASES.length;
  if (n !== 43) bad.push(`o snapshot traz ${n} casos`);
  const soma = REL.PER_SUPERFICIE.OPPORTUNITA + (REL.PER_SUPERFICIE.RADAR || 0)
             + (REL.PER_SUPERFICIE.SEGNALI || 0) + (REL.PER_SUPERFICIE.ERRORE || 0);
  if (soma !== n) bad.push(`as superficies somam ${soma}, nao ${n} — um caso desapareceu`);
  if (Object.keys(REL.VERDETTI).length !== n) bad.push('ha casos sem veredito');
  /* NADA SE APAGA: cada um dos 43 continua no pacote e no build da superficie. */
  if ((CASA.OPPORTUNITA_ATTUALI.CASI || []).length !== n) bad.push('o pacote perdeu casos');
  if (SURF.cases.length !== n) bad.push('a superficie perdeu casos');
  return { pass: !bad.length, detail: bad.length ? bad
    : [`43 casos · ${REL.PER_SUPERFICIE.OPPORTUNITA} opportunita + ${REL.PER_SUPERFICIE.RADAR} radar + ${REL.PER_SUPERFICIE.SEGNALI} segnali + ${REL.PER_SUPERFICIE.ERRORE} errore`] };
});

check('SO_A_PUBLICA_COMO_OPORTUNIDADE', () => {
  /* As tres invariantes que a lei existe para garantir. */
  const bad = [];
  const r = SURF.relevance;
  if (r.B_AS_OPPORTUNITY !== 0) bad.push(`B_AS_OPPORTUNITY = ${r.B_AS_OPPORTUNITY}`);
  if (r.C_AS_OPPORTUNITY !== 0) bad.push(`C_AS_OPPORTUNITY = ${r.C_AS_OPPORTUNITY}`);
  if (r.D_AS_OPPORTUNITY !== 0) bad.push(`D_AS_OPPORTUNITY = ${r.D_AS_OPPORTUNITY}`);
  for (const c of SURF.commercial) {
    if (c.relevance !== 'A') bad.push(`${c.id} publicado como oportunidade com classe ${c.relevance}`);
  }
  /* CONTROLO NEGATIVO — um portao que nunca reprovou e decoracao. */
  const sonda = SURF.cases.filter((c) => c.relevance !== 'A');
  if (!sonda.length) bad.push('CONTROLO NEGATIVO FALHOU: nao ha caso nao-A para o portao poder apanhar');
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${SURF.commercial.length} oportunidades, todas classe A · B/C/D como oportunidade: 0/0/0`,
       `${sonda.length} casos nao-A existem e nenhum atravessou`] };
});

check('O_VALUTADOR_E_UM_SO', () => {
  /* A lei decide-se em Python. O browser transporta e nunca recalcula: se
     `meeting-surface.js` reavaliasse, haveria duas leis com o mesmo nome. */
  const bad = [];
  const js = fs.readFileSync(path.join(CLIENTE, 'meeting-surface.js'), 'utf8');
  if (REL.DONO_DA_LEI !== 'scripts/adama_relevance.py') bad.push(`dono declarado: ${REL.DONO_DA_LEI}`);
  if (!/window\.ADAMA_RELEVANCE/.test(js)) bad.push('meeting-surface nao le o veredito');
  for (const marca of ['DECLARED_ON_CATALOG_PAGE', 'ON_MINISTERIAL_LABEL', 'AUTHORIZATION_LIVE']) {
    if (new RegExp(`${marca}['"]\\s*(===|==|!==)`).test(js)) bad.push(`meeting-surface reavalia a lei (${marca})`);
  }
  /* E o veredito impresso tem de bater com o que o pacote leva por caso. */
  for (const c of CASA.OPPORTUNITA_ATTUALI.CASI) {
    const v = REL.VERDETTI[c.ID];
    if (!v) { bad.push(`${c.ID} sem veredito`); continue; }
    if (v.CLASSE !== c.RILEVANZA) bad.push(`${c.ID}: pacote ${c.RILEVANZA}, veredito ${v.CLASSE}`);
    if (v.SUPERFICIE !== c.RILEVANZA_SUPERFICIE) bad.push(`${c.ID}: superficie divergente`);
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : [`a lei vive em ${REL.DONO_DA_LEI}; o browser le e nao reavalia`,
       `${Object.keys(REL.VERDETTI).length} vereditos, todos iguais aos do pacote`] };
});

check('TODO_A_NOMEIA_UM_PRODUTO_ADAMA_REAL', () => {
  /* A premissa que so aqui se pode medir: o catalogo embarcado diz quem e da
     ADAMA. O gerador nao o consegue ler — este portao le. */
  const bad = [];
  const cat = new Map((HAND.productsCommercial || []).map((p) => [p.ID, p]));
  let provados = 0;
  for (const c of CASA.OPPORTUNITA_ATTUALI.CASI) {
    if (c.RILEVANZA !== 'A') continue;
    provados++;
    const p = c.PROVA_ADAMA;
    if (!p || !p.PRODOTTO) { bad.push(`${c.ID} e classe A sem produto que o prove`); continue; }
    const rec = cat.get(p.ID);
    if (!rec) { bad.push(`${c.ID}: ${p.ID} nao esta no catalogo comercial embarcado`); continue; }
    if (rec.HOLDER_IS_ADAMA !== true) bad.push(`${c.ID}: ${p.PRODOTTO} nao e da ADAMA (HOLDER_IS_ADAMA=${rec.HOLDER_IS_ADAMA})`);
    if (!(rec.CROP_IDS || []).includes(c.COLTURA)) bad.push(`${c.ID}: o catalogo de ${p.PRODOTTO} nao declara ${c.COLTURA}`);
    if (!p.REGISTRO) bad.push(`${c.ID}: sem numero de registo`);
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${provados} oportunidades, cada uma com um produto ADAMA nomeado, registado e com a cultura declarada no catalogo`] };
});

check('RESTRICOES_NUNCA_SE_MISTURAM', () => {
  /* 40 das 114 restricoes citam um activo que nao esta em nenhum produto ADAMA
     ligado ao caso. Mostrar a expiracao do activo do concorrente como se fosse
     a nossa e uma decisao comercial tomada ao contrario. */
  const bad = [];
  let nossas = 0; let outras = 0; let total = 0;
  const porId = new Map(SNAP.CASES.map((c) => [c.ID, c]));
  for (const c of CASA.OPPORTUNITA_ATTUALI.CASI) {
    const cru = porId.get(c.ID);
    total += (cru.PRODUCT_RESTRICTIONS || []).length;
    nossas += c.RESTRIZIONI_ADAMA.length;
    outras += c.RESTRIZIONI_ALTRO_ATTIVO.length;
    const meus = new Set((c.PRODOTTI || []).flatMap((p) => p.ATTIVI || []));
    for (const r of c.RESTRIZIONI_ADAMA) {
      if (!meus.has(r.ATTIVO)) bad.push(`${c.ID}: ${r.ATTIVO} na lista do produto ADAMA e nao esta nos seus activos`);
    }
    for (const r of c.RESTRIZIONI_ALTRO_ATTIVO) {
      if (meus.has(r.ATTIVO)) bad.push(`${c.ID}: ${r.ATTIVO} na lista dos OUTROS e e do produto ADAMA`);
    }
  }
  if (nossas + outras !== total) bad.push(`${nossas}+${outras} nao fecha em ${total} — uma restricao perdeu-se`);
  if (!outras) bad.push('CONTROLO NEGATIVO FALHOU: nenhuma restricao de outro activo foi separada');
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${total} restricoes: ${nossas} do produto ADAMA ligado, ${outras} de outra substancia citada pelas fontes`,
       'as duas listas viajam separadas e nenhuma aparece como a outra'] };
});

check('EXPIRACAO_EUROPEIA_NAO_E_RISCO', () => {
  /* APPROVAL_EXPIRY != RISCO_DE_NAO_RENOVACAO. Medido nos 47 factos: 47/47
     APPROVED e IS_RISK=false. Nenhum deles pode, sozinho, gerar oportunidade. */
  const bad = [];
  const rff = HAND.regulatoryFutureFacts || [];
  const risco = rff.filter((f) => f.IS_RISK === true || f.EU_STATE !== 'APPROVED');
  let comFacto = 0;
  const porId = new Map(SNAP.CASES.map((c) => [c.ID, c]));
  for (const c of CASA.OPPORTUNITA_ATTUALI.CASI) {
    const cru = porId.get(c.ID);
    const tem = (cru.EVIDENCE_ROLES || []).some((e) => e.ENTITY_TYPE === 'REGULATORY_FUTURE_FACT');
    if (!tem) continue;
    comFacto++;
    if (c.RILEVANZA === 'A' && !c.PROVA_ADAMA) {
      bad.push(`${c.ID} subiu com facto regulatorio e sem produto que o prove`);
    }
  }
  if (risco.length) bad.push(`${risco.length} factos declaram risco — a lei precisa de ser revista, nao ignorada`);
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${rff.length} factos regulatorios, ${rff.length - risco.length} APPROVED e nenhum declarado a risco`,
       `${comFacto} casos citam um; nenhum subiu a oportunidade por causa disso`] };
});

check('NADA_DESAPARECE_E_TUDO_SE_ALCANCA', () => {
  /* Esconder nao e apagar. Cada caso declassado continua inteiro, com o mesmo
     detalhe, sob o nome que lhe cabe. */
  const bad = [];
  const vistos = new Set([...SURF.commercial, ...SURF.radar, ...SURF.signals, ...SURF.errored].map((c) => c.id));
  for (const c of SNAP.CASES) if (!vistos.has(c.ID)) bad.push(`${c.ID} nao esta em superficie nenhuma`);
  if (vistos.size !== SNAP.CASES.length) bad.push(`${vistos.size} alcancaveis de ${SNAP.CASES.length}`);
  /* E o detalhe nao encolhe: um caso declassado mantem as suas seccoes. */
  const seccoes = (c) => [c.PERCHE, c.FINESTRA, c.CATENA, c.AZIONI, c.EVIDENZE].filter(Boolean).length;
  for (const c of CASA.OPPORTUNITA_ATTUALI.CASI) {
    if (seccoes(c) < 5) bad.push(`${c.ID} (${c.RILEVANZA}) perdeu seccoes ao ser declassado`);
  }
  return { pass: !bad.length, detail: bad.length ? bad
    : [`${vistos.size}/${SNAP.CASES.length} alcancaveis · nenhum caso perdeu detalhe ao mudar de nome`] };
});

const mau = R.filter((r) => !r.pass);
console.log('\n  SINTONIA · PORTAO DA LEI DE RELEVANCIA ADAMA');
console.log('  ' + '─'.repeat(92));
for (const r of R) {
  console.log(`  ${r.pass ? 'PASS' : 'FAIL'}  ${r.id}`);
  for (const d of r.detail || []) console.log(`        ${d}`);
}
console.log('  ' + '─'.repeat(92));
console.log(`  ${mau.length ? 'FAIL' : 'PASS'} — ${R.length - mau.length}/${R.length}\n`);
process.exit(mau.length ? 1 : 0);
