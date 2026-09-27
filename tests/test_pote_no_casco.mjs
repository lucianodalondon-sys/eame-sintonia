/* POTE-UNICO · o casco le o pote — atacado.

       node tests/test_pote_no_casco.mjs

   ⚠️ DADO SINTETICO DECLARADO. O pote usado aqui e tests/fixtures/pote/POTE-SINTETICO.json, gerado por
   pacote/pote_intelligence_casco.py a partir de tests/fixtures/pote/CORRIDA-SINTETICA-POTE.json: todo id
   comeca por SINT-, SINTETICA = true. Nenhum valor dele e real, e ele nunca e escrito dentro do portal —
   entra no MESMO sandbox que o banco de provas do portal usa (italia-portale/audit/lib/harness.mjs).

   Prova que:
     P1  sem pote, NADA muda (cada vista desenha o legado, como antes);
     P2  com pote, cada ferramenta desenha o SEU compartimento, e o legado apaga-se (precedencia);
     P3  vazio mostra o PORQUE; futuro tem forma propria e nunca a da oportunidade;
     P4  nenhuma regra de cruzamento: todo valor desenhado e o do pote ou NAO SEI, na ordem do pote;
     P5  pote que reprova nao desenha nada, e o legado nao volta como se fosse atual;
     P6  URL que nao e http(s) nao vira link; o pote fica fora do Git e do deploy;
     P7  toda ligacao {{ }} do bloco do pote resolve contra os valores reais. */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { mount, CLIENT } from '../italia-portale/audit/lib/harness.mjs';

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const POTE = JSON.parse(fs.readFileSync(path.join(RAIZ, 'tests/fixtures/pote/POTE-SINTETICO.json'), 'utf8'));
const LEITOR = fs.readFileSync(path.join(CLIENT, 'sintonia-pote-casco.js'), 'utf8');
const HTML = fs.readFileSync(path.join(CLIENT, 'portale.html'), 'utf8');

let falhas = 0, provas = 0;
const prova = (nome, ok, detalhe = '') => {
  provas++;
  if (!ok) { falhas++; console.log('FAIL: ' + nome + (detalhe ? ' — ' + detalhe : '')); }
  else console.log('ok   ' + nome);
};
const clone = (x) => JSON.parse(JSON.stringify(x));

/* A mesma rota -> a bandeira de legado que ela acende, e o compartimento que o pote diz que ela le. */
const ROTAS = {
  meeting: ['isMeeting', 'meeting'], radarfuturo: ['isRadarFuturo', 'future'], future: ['isFuture', 'archive'],
  archive: ['isArchive', 'archive'], windows: ['isWindows', 'windows'], market: ['isMarket', 'market'],
  voices: ['isVoices', 'voices'], competitors: ['isCompetitors', 'competitors'], science: ['isScience', 'science'],
  portfolio: ['isPortfolio', 'portfolio'], etichette: ['isEtichette', 'portfolio'], sources: ['isSources', 'sources'],
};

function montar(pote) {
  const M = mount({});
  vm.runInContext(LEITOR, M.ctx, { filename: 'sintonia-pote-casco.js' });
  if (pote !== undefined) M.ctx.SINTONIA_POTE = pote;
  return M;
}

/* ── P1 · sem pote, nada muda ─────────────────────────────────────────────── */
{
  const M = montar();
  for (const [v, [flag]] of Object.entries(ROTAS)) {
    const x = M.vals({ view: v, lang: 'it' });
    prova(`P1 sem pote, #${v} desenha o legado (${flag})`, x[flag] === true && x.poteVista === false);
  }
  const semLeitor = mount({}).vals({ view: 'meeting', lang: 'it' });
  prova('P1 sem o leitor carregado, o casco nao quebra', semLeitor.isMeeting === true && semLeitor.poteVista === false);
  prova('P1 o leitor NAO define pote nenhum sozinho', M.ctx.SINTONIA_POTE === null);
  const pedidos = (search) => {
    const escritos = [];
    const sb = vm.createContext({ document: { write: (s) => escritos.push(s) } });
    sb.window = sb; sb.window.location = { search };
    vm.runInContext(LEITOR, sb);
    return escritos;
  };
  prova('P1 sem ?pote=local o carregador nao pede ficheiro nenhum', pedidos('').length === 0 && pedidos('?sala=local').length === 0);
  prova('P1 com ?pote=local pede sintonia-pote.js, e so ele',
    JSON.stringify(pedidos('?pote=local')) === JSON.stringify(['<script src="sintonia-pote.js"><\/script>']));
}

/* ── P2 · com pote, precedencia ───────────────────────────────────────────── */
const M = montar(clone(POTE));
for (const lang of ['it', 'en']) for (const [v, [flag, comp]] of Object.entries(ROTAS)) {
  const x = M.vals({ view: v, lang });
  prova(`P2 [${lang}] #${v} le o compartimento ${comp} e apaga o legado`,
    x.poteVista === true && x[flag] === false && x.pote.comp.codigo === comp,
    `poteVista=${x.poteVista} ${flag}=${x[flag]} comp=${x.pote.comp && x.pote.comp.codigo}`);
  const e = POTE.COMPARTIMENTOS[comp];
  prova(`P2 [${lang}] #${v} desenha os ${e.OBJETOS.length} objetos do pote, na ordem do pote`,
    JSON.stringify(x.pote.objetos.map((o) => o.id)) === JSON.stringify(e.OBJETOS.map((o) => o.OBJETO_ID)));
}
for (const v of ['sala', 'painel', 'mcase', 'search']) {
  prova(`P2 #${v} nao e ferramenta: o pote nao a toma`, M.vals({ view: v, lang: 'it' }).poteVista === false);
}
for (const v of ['radar', 'msignals', 'mradar']) {
  prova(`P2 a rota #${v} e o radar: le meeting`, M.vals({ view: v, lang: 'it' }).pote.comp.codigo === 'meeting');
}
prova('P2 a faixa EXPERIMENTAL esta em toda vista do pote',
  Object.keys(ROTAS).every((v) => /EXPERIMENTAL/.test(M.vals({ view: v, lang: 'it' }).pote.faixa)));
{
  const x = M.vals({ view: 'meeting', lang: 'it' });
  const run = Object.fromEntries(x.pote.run.map((r) => [r.k, r.v]));
  prova('P2 a corrida, o SOURCE_HEAD e o corte estao no topo',
    run.corsa === POTE.INTELLIGENCE_RUN_ID && run.SOURCE_HEAD === POTE.SOURCE_HEAD && run.taglio === POTE.CORTE);
}

/* ── P3 · vazio com o porque; futuro != oportunidade ─────────────────────── */
{
  const mk = M.vals({ view: 'market', lang: 'it' }).pote;
  prova('P3 compartimento vazio diz o PORQUE (SEM_OBJETOS_NESTA_CORRIDA)',
    mk.vazio === true && /SEM_OBJETOS_NESTA_CORRIDA/.test(mk.vazioTitulo) && mk.vazioTexto.length > 10 && mk.objetos.length === 0);
  const rf = M.vals({ view: 'radarfuturo', lang: 'it' }).pote;
  const op = M.vals({ view: 'meeting', lang: 'it' }).pote;
  const fut = rf.objetos, opp = op.objetos.filter((o) => o.especie === 'OPORTUNIDADE');
  prova('P3 o Radar Futuro so desenha FATO_PRESENTE_SOBRE_O_FUTURO', fut.length > 0 && fut.every((o) => o.especie === 'FATO_PRESENTE_SOBRE_O_FUTURO' && o.eFuturo));
  prova('P3 o radar das oportunidades nao desenha futuro', op.objetos.every((o) => !o.eFuturo));
  prova('P3 futuro tem forma propria: tracejado, cor propria, aviso «NON e un\'opportunita»',
    fut.every((o) => o.traco === 'dashed' && /NON/.test(o.aviso)) && opp.length > 0 &&
    opp.every((o) => o.traco === 'solid') && fut.every((o) => opp.every((p) => p.badgeBg !== o.badgeBg && p.edge !== o.edge)));
}

/* ── P4 · nenhuma regra de cruzamento ────────────────────────────────────── */
{
  let ok = true, det = '';
  for (const [comp, e] of Object.entries(POTE.COMPARTIMENTOS)) {
    const v = Object.entries(ROTAS).find(([, [, c]]) => c === comp);
    if (!v) continue;
    const objs = M.vals({ view: v[0], lang: 'it' }).pote.objetos;
    e.OBJETOS.forEach((o, i) => {
      for (const c of objs[i].chaves) {
        const orig = o.CHAVES[c.k];
        const esperado = typeof orig === 'string' ? orig : JSON.stringify(orig);
        if (c.v !== esperado) { ok = false; det = `${comp}/${o.OBJETO_ID}/${c.k}: ${c.v} != ${esperado}`; }
        if (c.v === 'NAO SEI' && c.color !== '#F5B317') { ok = false; det = 'NAO SEI sem destaque'; }
      }
      if (objs[i].chaves.length !== Object.keys(o.CHAVES).length) { ok = false; det = 'chave a mais ou a menos'; }
    });
  }
  prova('P4 todo valor desenhado e o do pote (ou NAO SEI em destaque), sem chave inventada', ok, det);
  prova('P4 o leitor nao ordena, nao pontua, nao cruza (sem sort/score/rank no codigo)',
    !/\.sort\(|score|rank|relevan/i.test(LEITOR.replace(/\/\*[\s\S]*?\*\//g, '')));
  const w = M.vals({ view: 'windows', lang: 'it' }).pote.objetos[0];
  prova('P4 FACT_LOCATION viaja como FACT_LOCATION (fora do contrato) e REGION_ID fica NAO SEI',
    w.fora.some((c) => c.k === 'FACT_LOCATION' && c.v === 'SINT-Puglia') &&
    w.chaves.some((c) => c.k === 'REGION_ID' && c.v === 'NAO SEI'));
  prova('P4 publicacao nao vira tempo do facto no ecra',
    /pubblicato 2026-09-10 · raccolto NAO SEI · tempo del fatto 2026-09-07\/2026-09-13/.test(w.provas[0].datas));
}

/* ── P5 · pote que reprova ───────────────────────────────────────────────── */
for (const [nome, mexer] of [
  ['sem a marca', (p) => { delete p.MARCA; }],
  ['outro contrato', (p) => { p.SCHEMA = 'PONTE_INTELLIGENCE_CASCO/v1'; }],
  ['compartimento a menos', (p) => { delete p.COMPARTIMENTOS.sources; }],
  ['vazio sem porque', (p) => { p.COMPARTIMENTOS.market.PORQUE_VAZIO = null; }],
  ['oportunidade no Radar Futuro', (p) => { p.COMPARTIMENTOS.future.OBJETOS[0].ESPECIE = 'OPORTUNIDADE'; }],
  ['objeto sem prova', (p) => { p.COMPARTIMENTOS.meeting.OBJETOS[0].PROVA = []; }],
]) {
  const pote = clone(POTE); mexer(pote);
  const R = montar(pote);
  const x = R.vals({ view: 'meeting', lang: 'it' });
  prova(`P5 pote ${nome}: recusado, nada desenhado, legado apagado`,
    x.poteVista === true && x.pote.recusado === true && x.pote.objetos.length === 0 && x.isMeeting === false);
}

/* ── P6 · URL e fronteira do Git ─────────────────────────────────────────── */
{
  const arq = M.vals({ view: 'archive', lang: 'it' }).pote.objetos;
  const js = arq.find((o) => o.id === 'SINT-SG-8').provas[0];
  prova('P6 URL javascript: nao vira link', js.temUrl === false && js.url === '' && js.semUrl === true);
  const op = M.vals({ view: 'meeting', lang: 'it' }).pote.objetos[0].provas[0];
  prova('P6 URL https vira link, com a prova ate ao DOCUMENT_ID',
    op.temUrl === true && /^https:/.test(op.url) && /ITEM_ID .* → RAW_OBSERVATION_ID .* → SOURCE_ID .* → DOCUMENT_ID /.test(op.cadeia));
  const gi = fs.readFileSync(path.join(CLIENT, '.gitignore'), 'utf8').split('\n');
  const vi = fs.readFileSync(path.join(RAIZ, '.vercelignore'), 'utf8').split('\n');
  prova('P6 sintonia-pote.js esta no .gitignore do cliente e no .vercelignore',
    gi.includes('sintonia-pote.js') && vi.includes('/italia-portale/client/sintonia-pote.js'));
  prova('P6 o portale.html nao pede sintonia-pote.js direto (so o carregador, com ?pote=local)',
    !/src="sintonia-pote\.js"/.test(HTML.replace(/<!--[\s\S]*?-->/g, '')) && /src="sintonia-pote-casco\.js"/.test(HTML) &&
    /\?pote=local|pote=local/.test(LEITOR));
}

/* ── P7 · o bloco do pote liga so ao que existe ──────────────────────────── */
{
  const a = HTML.indexOf('<sc-if value="{{ poteVista }}"');
  const b = HTML.indexOf('<!-- ================= SALA', a);
  const bloco = HTML.slice(a, b);
  const x = M.vals({ view: 'meeting', lang: 'it' });
  const alias = { r: x.pote.run[0], o: x.pote.objetos[0], c: x.pote.objetos[0].chaves[0],
    p: x.pote.objetos[0].provas[0], g: { t: '' } };
  const soltas = [];
  for (const m of bloco.matchAll(/\{\{\s*([^}]+?)\s*\}\}/g)) {
    const expr = m[1];
    if (/^(true|false)$/.test(expr)) continue;
    const [head, ...rest] = expr.split('.');
    let cur = head in alias ? alias[head] : x[head];
    for (const k of rest) cur = cur == null ? undefined : cur[k];
    if (cur === undefined) soltas.push(expr);
  }
  prova('P7 toda ligacao do bloco do pote resolve', a > 0 && soltas.length === 0, soltas.join(', '));
  prova('P7 marca no bloco e em cada objeto', (bloco.match(/data-marca="1"/g) || []).length >= 2);
}

console.log(`\nPOTE NO CASCO: ${provas - falhas}/${provas} provas`);
process.exit(falhas ? 1 : 0);
