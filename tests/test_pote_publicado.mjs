/* POTE PUBLICADO (D114) · o pote da rodada 7 vai ao ar — atacado.

       node tests/test_pote_publicado.mjs

   Este teste usa o DADO REAL publicado (italia-portale/client/sintonia-pote-publicado.js), porque e ele que
   vai ao ar: o que se prova e que a tela desenha esse dado e nada mais. Corre no MESMO sandbox que o banco
   de provas do portal usa (italia-portale/audit/lib/harness.mjs), com os tres ficheiros na ordem do
   portale.html.

   Prova que:
     Q1  o ficheiro publicado e exatamente o que o publicador produz dos insumos em docs/casco/r7/, e o pote
         e a analise la dentro sao os dos insumos, sem um campo mudado;
     Q2  so este pote atravessa: sintonia-pote.js, o gerador e PARA-O-CASCO continuam fora; com ?pote=local
         a publicacao cala-se;
     Q3  toda rota de ferramenta desenha o pote, com a faixa D114 e a marca EXPERIMENTAL;
     Q4  os 86 cruzamentos aparecem, cada um uma vez, com o estado que a Intelligence escreveu; so os 5
         «sim» levam A CONFIRMAR; fonte candidata marcada como candidata; o destino no pote de cada um;
     Q5  os recusados de cada compartimento estao visiveis, com o motivo;
     Q6  vazio diz o PORQUE; a Rete Commerciale simulada nao volta;
     Q7  o relogio diz a data da copia da Sala e o menu conta o pote — nenhum «oggi»;
     Q8  o SHA que nao confere com o manifesto esta dito na tela;
     Q9  um pote de OUTRA corrida nao herda os cruzamentos desta;
     Q10 toda ligacao {{ }} dos blocos da publicacao resolve. */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { mount, CLIENT } from '../italia-portale/audit/lib/harness.mjs';

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ler = (p) => fs.readFileSync(path.join(RAIZ, p), 'utf8');
const POTE = JSON.parse(ler('docs/casco/r7/POTE-R7.json'));
const ANALISE = JSON.parse(ler('docs/casco/r7/ANALISE-R7.json'));
const HTML = fs.readFileSync(path.join(CLIENT, 'portale.html'), 'utf8');
/* Um ficheiro por linha: cada linha e a prova de UMA leitura no mapa, nunca de duas. */
const FICHEIROS = [
  'sintonia-pote-publicado.js',
  'sintonia-pote-casco.js',
  'sintonia-pote-publicacao.js',
];
const FONTE = Object.fromEntries(FICHEIROS.map((f) => [f, fs.readFileSync(path.join(CLIENT, f), 'utf8')]));

let falhas = 0, provas = 0;
const prova = (nome, ok, detalhe = '') => {
  provas++;
  if (!ok) { falhas++; console.log('FAIL: ' + nome + (detalhe ? ' — ' + detalhe : '')); }
  else console.log('ok   ' + nome);
};
const clone = (x) => JSON.parse(JSON.stringify(x));
const igual = (a, b) => JSON.stringify(a) === JSON.stringify(b);

function montar(search = '', mexer = null) {
  const M = mount({});
  M.ctx.location = { search, hash: '' };
  for (const f of FICHEIROS) {
    vm.runInContext(FONTE[f], M.ctx, { filename: f });
    if (f === FICHEIROS[0] && mexer) mexer(M.ctx);
  }
  return M;
}

const ROTAS = ['meeting', 'radarfuturo', 'future', 'archive', 'windows', 'market', 'voices', 'competitors',
  'science', 'portfolio', 'etichette', 'sources'];

/* ── Q1 · o publicado e o dos insumos ────────────────────────────────────── */
{
  const r = spawnSync('python3', ['pacote/publicar_pote_aprovado.py', '--conferir'], { cwd: RAIZ, encoding: 'utf8' });
  prova('Q1 o ficheiro publicado e o que o publicador produz dos insumos (--conferir = IGUAL)',
    r.status === 0 && /IGUAL/.test(r.stdout), (r.stdout || '') + (r.stderr || '') + (r.error ? String(r.error) : ''));
  const M = montar();
  const PUB = M.ctx.SINTONIA_POTE_PUBLICADO;
  prova('Q1 o pote publicado e o POTE-R7, campo a campo', !!PUB && igual(PUB.POTE, POTE));
  prova('Q1 a analise publicada e a ANALISE-R7, campo a campo', !!PUB && igual(PUB.ANALISE, ANALISE));
  prova('Q1 pote e analise sao da MESMA corrida', PUB.INTELLIGENCE_RUN_ID === POTE.INTELLIGENCE_RUN_ID &&
    ANALISE.INTELLIGENCE_RUN_ID === POTE.INTELLIGENCE_RUN_ID);
  prova('Q1 a decisao que abre a porta tem nome: D114', PUB.DECISAO && PUB.DECISAO.ID === 'D114' && /maximo de informacoes/.test(PUB.DECISAO.TEXTO));
  prova('Q1 o pote continua marcado EXPERIMENTAL e nao sintetico', POTE.MARCA === 'EXPERIMENTAL · NAO_PARA_CLIENTE' && POTE.CORRIDA_SINTETICA === false);
}

/* ── Q2 · so este pote atravessa ─────────────────────────────────────────── */
{
  const gi = fs.readFileSync(path.join(CLIENT, '.gitignore'), 'utf8').split('\n');
  const vi = ler('.vercelignore').split('\n');
  const cvi = fs.readFileSync(path.join(CLIENT, '.vercelignore'), 'utf8').split('\n');
  prova('Q2 sintonia-pote.js (pote local) continua fora do Git e do deploy',
    gi.includes('sintonia-pote.js') && vi.includes('/italia-portale/client/sintonia-pote.js') && cvi.includes('sintonia-pote.js'));
  prova('Q2 o publicado NAO esta em nenhuma tranca (e ele que vai ao ar)',
    ![gi, vi, cvi].some((l) => l.some((x) => /sintonia-pote-publica/.test(x))));
  const rastreados = spawnSync('git', ['ls-files'], { cwd: RAIZ, encoding: 'utf8' }).stdout.split('\n');
  prova('Q2 o gerador do pote e as pastas PARA-O-CASCO nao entram no ramo',
    !rastreados.includes('pacote/pote_intelligence_casco.py') && !rastreados.some((f) => /PARA-O-CASCO/.test(f)) &&
    !rastreados.includes('italia-portale/client/sintonia-pote.js'));
  const semCom = HTML.replace(/<!--[\s\S]*?-->/g, '');
  const i = (f) => semCom.indexOf(`<script src="${f}"></script>`);
  prova('Q2 portale.html carrega publicado -> leitor -> publicacao, nessa ordem',
    i(FICHEIROS[0]) > 0 && i(FICHEIROS[0]) < i(FICHEIROS[1]) && i(FICHEIROS[1]) < i(FICHEIROS[2]));
  const L = montar('?pote=local');
  prova('Q2 com ?pote=local o publicado nao se poe no lugar do pote local', L.ctx.SINTONIA_POTE === null);
  const P = montar('');
  prova('Q2 sem ?pote=local o pote do ar e o publicado', P.ctx.SINTONIA_POTE === P.ctx.SINTONIA_POTE_PUBLICADO.POTE);
}

const M = montar();
const V = (view, lang = 'it') => M.vals({ view, lang });

/* ── Q3 · toda ferramenta desenha o pote, com a faixa ───────────────────── */
for (const lang of ['it', 'en']) {
  const x = ROTAS.map((r) => [r, V(r, lang)]);
  prova(`Q3 [${lang}] as 12 rotas de ferramenta leem o pote e a publicacao`,
    x.every(([, v]) => v.poteVista === true && v.potePubVista === true), x.filter(([, v]) => !v.potePubVista).map(([r]) => r).join(','));
  prova(`Q3 [${lang}] faixa D114 + EXPERIMENTAL em toda vista`,
    x.every(([, v]) => /D114/.test(v.potePub.faixa) && /EXPERIMENTAL/.test(v.potePub.faixa) && /EXPERIMENTAL/.test(v.pote.faixa)));
}
for (const r of ['sala', 'painel', 'search']) prova(`Q3 #${r} nao e ferramenta: a publicacao nao a toma`, V(r).potePubVista === false);

/* ── Q4 · os 86 cruzamentos ──────────────────────────────────────────────── */
{
  const C = V('portfolio').potePub.cruz;
  const todas = C.grupos.flatMap((g) => g.linhas);
  prova('Q4 os 86 cruzamentos estao na tela', todas.length === 86 && ANALISE.CROSSINGS.length === 86);
  prova('Q4 cada cruzamento aparece uma vez', new Set(todas.map((l) => l.id)).size === 86);
  const porId = Object.fromEntries(ANALISE.CROSSINGS.map((c) => [c.OBJETO_ID, c]));
  prova('Q4 o estado desenhado e o ESTADO_R7 da Intelligence (nenhum recalculo)',
    todas.every((l) => porId[l.id] && porId[l.id].ESTADO_R7 === l.estado));
  const cont = {}; todas.forEach((l) => { cont[l.estado] = (cont[l.estado] || 0) + 1; });
  prova('Q4 contagem por estado = resumo da analise (5 / 29 / 48 / 4)',
    igual(Object.keys(cont).sort().map((k) => [k, cont[k]]), Object.keys(ANALISE.CROSSINGS_RESUMO.POR_ESTADO).sort().map((k) => [k, ANALISE.CROSSINGS_RESUMO.POR_ESTADO[k]])) &&
    cont.POSSIBLE_ANSWER_YES_A_CONFIRMAR === 5 && cont.POSSIBLE_ANSWER_NO === 29 && cont.PARTIAL_GRAO_INCOMPATIVEL === 48 && cont.NOT_POSSIBLE === 4);
  const sim = todas.filter((l) => l.temMarca);
  prova('Q4 so os 5 «sim a confirmar» levam a marca A CONFIRMAR',
    sim.length === 5 && sim.every((l) => l.marca === 'A CONFIRMAR' && l.estado === 'POSSIBLE_ANSWER_YES_A_CONFIRMAR'));
  prova('Q4 os 5 «sim» sao os do relatorio (1209, 1221, 1223, 1228, 1229)',
    igual(sim.map((l) => l.id.split('-')[2]).sort(), ['1209', '1221', '1223', '1228', '1229']));
  prova('Q4 o «sim» nunca tem a forma da oportunidade (verde): amarelo tracejado',
    sim.every((l) => l.traco === 'dashed' && l.color === '#F5B317'));
  prova('Q4 fonte candidata marcada como candidata (VIA = EXTENSAO_DECLARADA), e so ela',
    todas.every((l) => (porId[l.id].VIA === 'EXTENSAO_DECLARADA') === /CANDIDATA/.test(l.via)) &&
    todas.filter((l) => /CANDIDATA/.test(l.via)).length === 47);
  const noPote = new Set(POTE.COMPARTIMENTOS.portfolio.OBJETOS.map((o) => o.OBJETO_ID));
  const recusa = new Set(POTE.RECUSADOS.filter((r) => r.COMPARTIMENTO === 'portfolio').map((r) => r.OBJETO_ID));
  prova('Q4 cada cruzamento diz o que o pote fez com ele (2 objetos, 80 recusados, 4 ausentes)',
    todas.filter((l) => noPote.has(l.id)).every((l) => /NEL POTE/.test(l.pote)) &&
    todas.filter((l) => recusa.has(l.id)).every((l) => /RIFIUTATO/.test(l.pote) && /DOCUMENT_ID|G0/.test(l.pote)) &&
    todas.filter((l) => !noPote.has(l.id) && !recusa.has(l.id)).length === 4 &&
    todas.filter((l) => !noPote.has(l.id) && !recusa.has(l.id)).every((l) => /ASSENTE/.test(l.pote)));
  prova('Q4 a prova de cada cruzamento: URL http(s) como link e data de publicacao (NAO SEI em destaque)',
    todas.every((l) => l.prova.temUrl && l.prova.url === porId[l.id].URL) &&
    todas.every((l) => (porId[l.id].PUBLISHED_AT === 'NAO SEI') === (l.prova.pubColor === '#F5B317')) &&
    todas.every((l) => l.prova.pub.endsWith(String(porId[l.id].PUBLISHED_AT))));
  prova('Q4 NAO SEI do lugar continua NAO SEI, em destaque',
    todas.every((l) => { const c = l.chaves.find((k) => k.k === 'luogo'); return !/NAO SEI/.test(c.v) || c.color === '#F5B317'; }));
  prova('Q4 cada cruzamento diz o que NAO e (OPPORTUNITY · RECOMENDACAO)', todas.every((l) => /OPPORTUNITY/.test(l.naoE)));
  prova('Q4 dentro de cada estado a ordem e a da analise',
    C.grupos.every((g) => igual(g.linhas.map((l) => l.id), ANALISE.CROSSINGS.filter((c) => c.ESTADO_R7 === g.k).map((c) => c.OBJETO_ID))));
  prova('Q4 a leitura da publicacao nao ordena, nao pontua (sem sort/score/rank no codigo)',
    !/\.sort\(|score|rank|relevan/i.test(FONTE['sintonia-pote-publicacao.js'].replace(/\/\*[\s\S]*?\*\//g, '')));
  prova('Q4 a Label Intelligence (etichette) le os mesmos 86', V('etichette').potePub.cruz.grupos.flatMap((g) => g.linhas).length === 86);
}

/* ── Q5 · recusados visiveis ─────────────────────────────────────────────── */
{
  let soma = 0, ok = true, det = '';
  const vistos = new Set();
  for (const r of ROTAS) {
    const x = V(r); const comp = x.pote.comp.codigo;
    const esperado = POTE.RECUSADOS.filter((q) => q.COMPARTIMENTO === comp);
    if (x.potePub.rec.linhas.length !== esperado.length) { ok = false; det = `${r}: ${x.potePub.rec.linhas.length} != ${esperado.length}`; }
    if (!vistos.has(comp)) { vistos.add(comp); soma += x.potePub.rec.linhas.length; }
  }
  prova('Q5 cada compartimento mostra os seus recusados, e so os seus', ok, det);
  prova('Q5 os 245 recusados do pote estao visiveis', soma === 245 && POTE.RECUSADOS.length === 245, String(soma));
  prova('Q5 recusado mostra o motivo', V('archive').potePub.rec.linhas.every((l) => l.motivo !== 'NAO SEI' && l.detalhe.length > 0));
}

/* ── Q6 · vazio com o porque; Rete Commerciale simulada nao volta ───────── */
{
  for (const r of ['meeting', 'voices', 'competitors']) {
    const p = V(r).pote;
    prova(`Q6 #${r} vazio mostra PORQUE_VAZIO`, p.vazio === true && /SEM_OBJETOS_NESTA_CORRIDA/.test(p.vazioTitulo) && p.objetos.length === 0);
  }
  const f = V('field');
  prova('Q6 #field: a vista simulada nao desenha (isField = false)', f.isField === false && f.potePubVista === true && f.potePub.temCampo === true);
  prova('Q6 #field diz SIMULATO e o PORQUE do pote (CASCO_SEM_CONTRATO_DE_INTELLIGENCE)',
    /SIMULATO/.test(f.potePub.campo.titulo) && /CASCO_SEM_CONTRATO_DE_INTELLIGENCE/.test(f.potePub.campo.estado) && f.potePub.campo.porque.length > 10);
  prova('Q6 a nota de ambiente diz a Rete Commerciale SIMULATO', /SIMULATO/.test(f.envNote) && /SIMULATED/.test(V('field', 'en').envNote));
}

/* ── Q7 · relogio e menu ─────────────────────────────────────────────────── */
{
  const x = V('meeting');
  prova('Q7 o relogio diz a data da copia da Sala (27 SET 2026 18:30 UTC), nao um «oggi»',
    x.sideClock === 'DATI AL · 27 SET 2026 18:30 UTC' && !/OGGI|TODAY/.test(x.sideClock));
  const conta = (route) => { const k = M.ctx.SINTONIA_POTE_CASCO.compartimentoDaVista(POTE, route); return k ? POTE.COMPARTIMENTOS[k].OBJETOS.length : ''; };
  const itens = [].concat(x.nav, x.navEvidence, x.navIntegrationItems).filter((n) => n.route);
  prova('Q7 o menu conta os objetos do compartimento de cada rota',
    itens.length >= 10 && itens.every((n) => n.count === conta(n.route)), itens.map((n) => n.route + '=' + n.count).join(' '));
  prova('Q7 o Radar delle Opportunita conta 0, como o pote', x.nav.find((n) => n.route === 'meeting').count === 0);
  prova('Q7 a barra lateral conta 47 objetos, 86 cruzamentos e 245 recusados',
    igual(x.sideRows.slice(1).map((r) => r.v), [47, 86, 245]));
}

/* ── Q8 · o SHA que nao confere ──────────────────────────────────────────── */
{
  const m = V('sources').potePub.meta.find((q) => /SHA256/.test(q.k));
  prova('Q8 o SHA do pote que nao confere com o manifesto esta dito, em destaque',
    !!m && /NON CORRISPONDE/.test(m.v) && m.color === '#F5B317');
}

/* ── Q9 · um pote de outra corrida nao herda estes cruzamentos ──────────── */
{
  const O = montar('', (ctx) => { const p = clone(ctx.SINTONIA_POTE_PUBLICADO.POTE); p.INTELLIGENCE_RUN_ID = 'IR-outra-corrida';
    Object.values(p.COMPARTIMENTOS).forEach((e) => (e.OBJETOS || []).forEach((o) => (o.PROVA || []).forEach((q) => { q.INTELLIGENCE_RUN_ID = 'IR-outra-corrida'; })));
    ctx.SINTONIA_POTE = p; });
  const x = O.vals({ view: 'portfolio', lang: 'it' });
  prova('Q9 pote de outra corrida: o leitor desenha-o, a publicacao R7 cala-se',
    x.poteVista === true && x.potePubVista === false && x.sideRows[2].v === 'NAO SEI');
}

/* ── Q10 · os blocos da publicacao ligam so ao que existe ───────────────── */
{
  const a = HTML.indexOf('<!-- ================= POTE PUBLICADO (D114) · LA FASCIA');
  const b = HTML.indexOf('<!-- ================= POTE-UNICO · IL COMPARTIMENTO', a);
  const c = HTML.indexOf('<!-- ================= POTE PUBLICADO (D114) · CIO CHE');
  const d = HTML.indexOf('<!-- ================= FIM DO POTE PUBLICADO', c);
  const bloco = HTML.slice(a, b) + HTML.slice(c, d);
  const soltas = new Set();
  for (const view of ['portfolio', 'windows', 'sources', 'field', 'archive']) {
    const x = V(view); const P = x.potePub;
    const gr = P.cruz.grupos[0] || {}; const lx = (gr.linhas || [])[0] || {};
    const si = P.sonda.itens[0] || {}; const fi = P.fontes.sinais[0] || {};
    const alias = { m: P.meta[0], e: P.cruz.resumo[0], gr, x: lx, c: (lx.chaves || [])[0] || P.sonda.juizo[0] || P.fontes.novas[0],
      tr: (lx.trechos || [])[0] || { t: '' }, i: si, sn: fi, r: P.rec.linhas[0] || { id: '', motivo: '', detalhe: '' } };
    for (const mm of bloco.matchAll(/\{\{\s*([^}]+?)\s*\}\}/g)) {
      const expr = mm[1];
      if (/^(true|false)$/.test(expr)) continue;
      const [head, ...rest] = expr.split('.');
      if (head in alias && alias[head] === undefined) continue;
      let cur = head in alias ? alias[head] : x[head];
      for (const k of rest) cur = cur == null ? undefined : cur[k];
      if (cur === undefined && !(view !== 'portfolio' && /^(gr|x|e|tr)$/.test(head)) &&
        !(view !== 'windows' && head === 'i') && !(view !== 'sources' && head === 'sn')) soltas.add(view + ':' + expr);
    }
  }
  prova('Q10 toda ligacao dos blocos da publicacao resolve', a > 0 && c > 0 && soltas.size === 0, [...soltas].join(', '));
  prova('Q10 marca visivel nos blocos (faixa, A CONFIRMAR, EXPERIMENTAL da sonda)', (bloco.match(/data-marca="1"/g) || []).length >= 3);
}

console.log(`\nPOTE PUBLICADO: ${provas - falhas}/${provas} provas`);
process.exit(falhas ? 1 : 0);
