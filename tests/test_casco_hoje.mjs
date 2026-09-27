#!/usr/bin/env node
/* SINTONIA · CASCO-HOJE-MINIMO-HONESTO · o casco so mostra o que o pote aprovou (D97), hoje (D114)
   ---------------------------------------------------------------------------
   tests/test_pote_publicado.mjs prova a publicacao do pote R7. Esta prova guarda o que a missao
   CASCO-HOJE acrescentou por cima, item a item, no sandbox que os testes do portal usam:

     H1  o carimbo da referencia ADAMA na tela e o da PORTA (motor/porta_da_referencia.py), nunca uma
         data escrita a mao; porta que nao le -> NAO SEI; «autorizzato» nunca para uso declarado pelo
         produto (DECLARACAO_DE_PRODUTO = da confermare);
     H2  a Label Intelligence e PRODUTO DE FERRAMENTA com a data do snapshot selado (31/08) e o aviso de
         frescor; os numeros sao os do payload selado; selo diferente -> NAO SEI, sem etiquetas;
     H3  com o pote, a busca procura so nos objetos do pote e as vistas de detalhe do modelo antigo nao
         abrem; a bandeira LEGADO_V21_VISIVEL (desligada) devolve-as seladas;
     H4  Radar: «0 opportunita difendibili» contado no pote, com o PORQUE_VAZIO e a sonda olivo x mosca
         como exemplo de NO_DEFENSIBLE_ACTION_YET; o radar V2.1 (43, dois ACT_NOW) nao aparece;
     H5  Radar Futuro: so fato com chave de dominio provada; o resto e Agenda, marcada; os 44 ITFC nao
         aparecem sem ITFC_LEGADO_VISIVEL;
     H6  contagens por OBJETO DISTINTO (25), nunca a soma das gavetas (47);
     H7  pote esperado e ausente: NAO SEI em toda rota — nenhuma demo, nenhuma Rete Commerciale;
     H8  todo id de cruzamento desenhado leva PROVVISORIO (D119);
     H9  a auditoria D97 da 0 objetos fora do pote, 0 cruzamentos sem prova na tela, 0 rotas de legado.

       node tests/test_casco_hoje.mjs                                                      */
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
const FICHEIROS = ['sintonia-pote-publicado.js', 'sintonia-pote-casco.js', 'sintonia-pote-publicacao.js'];
const FONTE = Object.fromEntries(FICHEIROS.map((f) => [f, fs.readFileSync(path.join(CLIENT, f), 'utf8')]));

let falhas = 0, provas = 0;
const prova = (nome, ok, detalhe = '') => {
  provas++;
  if (!ok) { falhas++; console.log('FAIL: ' + nome + (detalhe ? ' — ' + detalhe : '')); } else console.log('ok   ' + nome);
};

/* opcoes: bandeiras (window.SINTONIA_BANDEIRAS), semPublicado (o ficheiro nao chegou), esperado (a pagina o
   pede), mexer (muda o publicado antes da leitura). */
function montar({ bandeiras = null, semPublicado = false, esperado = false, mexer = null, antes = null } = {}) {
  const M = mount({});
  M.ctx.location = { search: '', hash: '' };
  if (esperado) M.ctx.document.querySelector = (q) => (/sintonia-pote-publicado\.js/.test(String(q)) ? {} : null);
  if (bandeiras) M.ctx.SINTONIA_BANDEIRAS = bandeiras;
  if (antes) antes(M.ctx);
  for (const f of FICHEIROS) {
    if (f === FICHEIROS[0] && semPublicado) continue;
    vm.runInContext(FONTE[f], M.ctx, { filename: f });
    if (f === FICHEIROS[0] && mexer) mexer(M.ctx);
  }
  return M;
}
const M = montar();
const V = (view, extra = {}) => M.vals(Object.assign({ view, lang: 'it' }, extra));
const PUB = M.ctx.SINTONIA_POTE_PUBLICADO;
const ddmm = (iso) => { const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(iso)); return m ? m[3] + '/' + m[2] : null; };

/* ── H1 · o carimbo e o da porta ─────────────────────────────────────────── */
{
  const r = spawnSync('python3', ['motor/porta_da_referencia.py', '--hoje', PUB.DECISAO.DATA], { cwd: RAIZ, encoding: 'utf8' });
  let porta = null;
  try { porta = JSON.parse(r.stdout); } catch (e) { porta = null; }
  const R = PUB.REFERENCIA_ADAMA;
  prova('H1 a porta corre e le a referencia (motor/porta_da_referencia.py)', !!porta && porta.ESTADO === 'LIDA', (r.stderr || '').slice(0, 200));
  prova('H1 o carimbo publicado e o da porta, campo a campo (edicao, data, checagem, frescor, impressao)',
    !!porta && ['EDICAO_REGISTRO', 'DATA_DA_EDICAO_REGISTRO', 'ULTIMA_CHECAGEM_OK', 'DIAS_SEM_CHECAGEM', 'ESTADO_FRESCOR',
      'EDICAO_CATALOGO', 'IMPRESSAO_DOS_LIVROS'].every((k) => porta[k] === R[k]));
  const ref = V('portfolio').potePub.ref;
  prova('H1 a tela diz «registro del DD/MM, ultima verifica DD/MM» com as datas DA PORTA',
    ref.lida === true && ref.texto.includes('registro del ' + ddmm(R.DATA_DA_EDICAO_REGISTRO)) &&
    ref.texto.includes('ultima verifica ' + ddmm(R.ULTIMA_CHECAGEM_OK)), ref.texto);
  prova('H1 o frescor vai literal e por extenso (PODE_ESTAR_DESATUALIZADO · PUÒ ESSERE NON AGGIORNATO), em ambar',
    ref.texto.includes('PODE_ESTAR_DESATUALIZADO') && /PUÒ ESSERE NON AGGIORNATO/.test(ref.texto) && ref.color === '#F5B317');
  const codigo = FONTE['sintonia-pote-publicacao.js'] + fs.readFileSync(path.join(CLIENT, 'portale.html'), 'utf8');
  /* O selo do legado «LEGADO 07/09» e o texto que o dono mandou escrever (missao, item 4) — nome do legado,
     nao carimbo da referencia; e o unico 07/09 permitido, e so nessa forma. */
  prova('H1 nenhuma data do carimbo esta escrita a mao no casco (31/08, 07/09)',
    !/\b31\/08\b|\b07\/09\b|2026-08-31|2026-09-07/.test(codigo.replace(/\/\*[\s\S]*?\*\//g, '').replace(/<!--[\s\S]*?-->/g, '')
      .replace(/(LEGADO|LEGACY) 07\/09 · /g, '')));
  const N = montar({ mexer: (ctx) => { ctx.SINTONIA_POTE_PUBLICADO.REFERENCIA_ADAMA = { ESTADO: 'NAO SEI', PORQUE: 'EDICAO_MISTURADA' }; } });
  const rn = N.vals({ view: 'portfolio', lang: 'it' }).potePub.ref;
  prova('H1 porta que nao leu -> NON SO em ambar, sem data nenhuma', rn.lida === false && /NON SO/.test(rn.texto) &&
    !/\d{2}\/\d{2}/.test(rn.texto) && rn.color === '#F5B317', rn.texto);
  prova('H1 uso declarado pelo produto (DECLARACAO_DE_PRODUTO) diz «da confermare», nunca «autorizzato»',
    /DECLARACAO_DE_PRODUTO/.test(ref.decl) && /da confermare/.test(ref.decl) && /mai «autorizzato»/.test(ref.decl));
}

/* ── H2 · a Label Intelligence como produto de ferramenta ────────────────── */
{
  const LI = PUB.LABEL_INTELLIGENCE;
  const P = M.ctx.ITALY_LABEL_INTELLIGENCE;
  const r = spawnSync('python3', ['pacote/pote_ferramenta_label.py', '--conferir'], { cwd: RAIZ, encoding: 'utf8' });
  prova('H2 o pote da ferramenta commitado e o do payload selado (pote_ferramenta_label --conferir = IGUAL)', r.status === 0 && /IGUAL/.test(r.stdout), r.stdout);
  prova('H2 o registo publicado diz PRODUTO_DE_FERRAMENTA e nao corrida da Intelligence',
    LI.ESPECIE === 'PRODUTO_DE_FERRAMENTA' && /^FERRAMENTA:/.test(LI.INTELLIGENCE_RUN_ID) && LI.INTELLIGENCE_RUN_ID !== POTE.INTELLIGENCE_RUN_ID);
  prova('H2 os numeros do registo sao os do payload selado (166 / 210 / 54) e o selo e o mesmo',
    LI.CONTAGENS.products === P.products.length && LI.CONTAGENS.objects === P.objects.length &&
    LI.CONTAGENS.versions === P.versions.length && LI.CONTENT_SHA256 === P.PRODUCED_BY.CONTENT_SHA256 && P.products.length === 166);
  const e = V('etichette');
  const nav = [].concat(e.nav, e.navEvidence, e.navIntegrationItems).find((n) => n.route === 'etichette');
  prova('H2 o menu da Label Intelligence conta os 166 do payload', nav && nav.count === P.products.length);
  const meta = e.labelFerramenta.meta.map((m) => m.k + ' ' + m.v).join(' | ');
  prova('H2 a faixa diz a data do snapshot selado (31/08, da ferramenta) e o frescor da porta',
    /istantanea del registro 31\/08 · PROD_FTS_6_20260831/.test(meta) && /PODE_ESTAR_DESATUALIZADO/.test(meta) &&
    LI.SNAPSHOT.DATA_DATE === '20260831' && LI.EDICAO_E_A_DA_PORTA === true, meta);
  prova('H2 #etichette nao desenha o pote nem os cruzamentos por cima', e.poteVista === false && e.potePubVista === false && e.isEtichette === true);
  const d = V('etichetta');
  prova('H2 o detalhe da etiqueta (#etichetta) abre: e da mesma ferramenta', d.isEtichetta === true && d.temLabelFerramenta === true);
  const X = montar({ antes: (ctx) => { /* o payload de outro selo */ }, mexer: (ctx) => { ctx.SINTONIA_POTE_PUBLICADO.LABEL_INTELLIGENCE.CONTENT_SHA256 = 'f'.repeat(64); } });
  const ex = X.vals({ view: 'etichette', lang: 'it' });
  prova('H2 selo que nao confere -> NON SO, sem etiquetas e sem legado', ex.isEtichette === false && ex.temLabelFerramenta === false &&
    ex.poteVista === true && ex.pote.recusado === true && /NON SO/.test(ex.pote.recusa));
  const xd = X.vals({ view: 'etichetta', lang: 'it' });
  prova('H2 selo que nao confere -> o detalhe da etiqueta tambem nao abre', xd.isEtichetta === false && xd.temLegadoFechado === true);
}

/* ── H3 · busca e detalhes: com o pote, so o pote ────────────────────────── */
const DETALHES = ['mcase', 'window', 'company', 'cproduct', 'event', 'theme', 'person', 'product', 'source', 'signal', 'case', 'brief'];
const FLAG = { mcase: 'isMcase', window: 'isWindow', company: 'isCompany', cproduct: 'isCProduct', event: 'isEvent', theme: 'isTheme',
  person: 'isPerson', product: 'isProduct', source: 'isSource', signal: 'isSignal', case: 'isCase', brief: 'isBrief' };
{
  const abertas = DETALHES.filter((d) => V(d)[FLAG[d]] === true);
  prova('H3 nenhuma das vistas de detalhe do modelo antigo abre com o pote', abertas.length === 0, abertas.join(','));
  const fechadas = DETALHES.filter((d) => d !== 'brief' && V(d).temLegadoFechado === true);
  prova('H3 cada detalhe fechado diz NON SO e o nome da bandeira', fechadas.length === DETALHES.length - 1 &&
    /LEGADO_V21_VISIVEL = false/.test(V('product').legadoFechado));
  const s = V('search', { committedQuery: 'vite', query: 'vite' });
  const ids = new Set();
  Object.values(POTE.COMPARTIMENTOS).forEach((c) => (c.OBJETOS || []).forEach((o) => ids.add(o.OBJETO_ID)));
  const linhas = s.searchGroups.flatMap((g) => g.items);
  prova('H3 a busca com o pote procura so nos objetos do pote', s.buscaNoPote === true && linhas.length > 0 &&
    linhas.every((l) => ids.has(l.label.split(' · ')[0])), linhas.map((l) => l.label).join(' | '));
  const n = M.ctx.SINTONIA_POTE_PUBLICACAO.busca(POTE, 'vite').length;
  prova('H3 um resultado por objeto distinto (o total e o dos objetos do pote que batem)', s.searchTotal === n && n === 2, String(s.searchTotal));
  const vazia = V('search', { committedQuery: 'zzzqqq', query: 'zzzqqq' });
  prova('H3 busca sem objeto no pote -> 0, sem cair no modelo antigo', vazia.searchTotal === 0 && vazia.searchGroups.length === 0);
  const B = montar({ bandeiras: { LEGADO_V21_VISIVEL: true } });
  const bp = B.vals({ view: 'product', lang: 'it' });
  const bs = B.vals({ view: 'search', lang: 'it', committedQuery: 'vite', query: 'vite' });
  prova('H3 com LEGADO_V21_VISIVEL ligada o detalhe volta SELADO («LEGADO 07/09»)', bp.isProduct === true && bp.temSeloLegado === true &&
    /LEGADO 07\/09/.test(bp.seloLegado) && /SENZA FINESTRA PROVATA/.test(bp.seloLegado));
  prova('H3 com LEGADO_V21_VISIVEL ligada a busca volta ao modelo antigo, selada', !bs.buscaNoPote && bs.searchTotal > n && bs.temSeloLegado === true);
  prova('H3 as bandeiras do dono estao desligadas por omissao', M.ctx.SINTONIA_POTE_PUBLICACAO.BANDEIRAS.LEGADO_V21_VISIVEL === false &&
    M.ctx.SINTONIA_POTE_PUBLICACAO.BANDEIRAS.ITFC_LEGADO_VISIVEL === false);
  const T = montar({ bandeiras: { LEGADO_V21_VISIVEL: 'true' } });
  prova('H3 so `true` liga uma bandeira (a string «true» nao)', T.vals({ view: 'product', lang: 'it' }).isProduct === false);
}

/* ── H4 · o Radar: zero contado, com o porque e o exemplo ───────────────── */
{
  const x = V('meeting');
  const R = x.potePub.radar;
  const J = ANALISE.CORTE_VERTICAL.JULGAMENTO_DA_SONDA;
  prova('H4 «0 opportunita difendibili in questa corsa», contado nas OPORTUNIDADE do pote',
    R.n === 0 && POTE.COMPARTIMENTOS.meeting.OBJETOS.filter((o) => o.ESPECIE === 'OPORTUNIDADE').length === 0 && /^0 OPPORTUNITÀ DIFENDIBILI IN QUESTA CORSA/.test(R.titulo));
  prova('H4 o PORQUE_VAZIO do pote vai ao lado', R.porque.startsWith(POTE.COMPARTIMENTOS.meeting.PORQUE_VAZIO) && R.porque.includes(POTE.COMPARTIMENTOS.meeting.PORQUE_TEXTO));
  prova('H4 o exemplo e a sonda olivo x mosca, NO_DEFENSIBLE_ACTION_YET, janela NO, agir NAO',
    R.temExemplo && R.resultado.endsWith('NO_DEFENSIBLE_ACTION_YET') && J.RESULTADO === 'NO_DEFENSIBLE_ACTION_YET' &&
    /olivo x mosca/.test(R.pergunta) && R.juizo.some((c) => c.k.endsWith('WINDOW_OPEN_NOW') && c.v === 'NO') && R.juizo.some((c) => c.k.endsWith('ACT_NOW') && c.v === 'NAO'));
  prova('H4 o radar V2.1 (e a lista de sinais por baixo dele) nao desenha', x.isMeeting === false && V('msignals').isSignalsView === false && V('radar').isMeeting === false);
  const B = montar({ bandeiras: { LEGADO_V21_VISIVEL: true } });
  const b = B.vals({ view: 'meeting', lang: 'it' });
  prova('H4 com LEGADO_V21_VISIVEL o radar V2.1 volta ao lado do pote, SELADO', b.isMeeting === true && b.poteVista === true && b.temSeloLegado === true && /LEGADO_V21_VISIVEL/.test(b.seloLegado));
}

/* ── H5 · Radar Futuro: dominio provado, Agenda a parte ─────────────────── */
{
  const Q = M.ctx.SINTONIA_POTE_PUBLICACAO;
  const F = POTE.COMPARTIMENTOS.future.OBJETOS;
  const dom = F.filter((o) => Q.chavesDeDominio(o).length > 0).map((o) => o.OBJETO_ID);
  const x = V('radarfuturo');
  prova('H5 o radar so tem os fatos com >= 1 chave de dominio provada', x.pote.objetos.map((o) => o.id).join() === dom.join() && x.pote.objetos.length === 0);
  prova('H5 os outros (so data/lugar) vao para a Agenda, marcada, e sao fatos sobre o futuro',
    x.pote.temAgenda === true && x.pote.agenda.length === F.length - dom.length && x.pote.agenda.length === 10 &&
    x.pote.agenda.every((o) => o.especie === 'FATO_PRESENTE_SOBRE_O_FUTURO') && /^AGENDA · EVENTI DATATI/.test(x.pote.futuro.agTitulo));
  prova('H5 radar vazio diz porque (zero nao prova ausencia)', x.pote.futuro.vazio === true && /zero qui non prova assenza/.test(x.pote.futuro.vazioTexto));
  prova('H5 chave de dominio: data e lugar sozinhos nao contam; cultura conta',
    Q.chavesDeDominio({ CHAVES: { FACT_TIME: '2026', FACT_LOCATION: 'Napoli', CROP_ID: 'NAO SEI' } }).length === 0 &&
    Q.chavesDeDominio({ CHAVES: { CROP_ID: 'VITE' } }).join() === 'CROP_ID');
  prova('H5 os 44 ITFC do legado nao aparecem', x.isRadarFuturo === false);
  const B = montar({ bandeiras: { ITFC_LEGADO_VISIVEL: true } });
  const b = B.vals({ view: 'radarfuturo', lang: 'it' });
  prova('H5 com ITFC_LEGADO_VISIVEL os ITFC voltam SELADOS', b.isRadarFuturo === true && b.temSeloLegado === true && /ITFC_LEGADO_VISIVEL/.test(b.seloLegado));
  const nav = [].concat(x.nav, x.navEvidence, x.navIntegrationItems).find((n) => n.route === 'radarfuturo');
  prova('H5 o menu do Radar Futuro conta o radar (0), nao a Agenda', nav && nav.count === 0);
}

/* ── H6 · objetos distintos ──────────────────────────────────────────────── */
{
  const soma = Object.values(POTE.COMPARTIMENTOS).reduce((a, c) => a + (c.OBJETOS || []).length, 0);
  const x = V('archive');
  prova('H6 a barra lateral conta 25 objetos distintos, nao a soma de 47 das gavetas', soma === 47 && x.sideRows[1].v === 25 &&
    M.ctx.SINTONIA_POTE_PUBLICACAO.distintos(POTE) === 25);
}

/* ── H7 · pote esperado e ausente: NAO SEI, nunca demo ───────────────────── */
{
  const S = montar({ semPublicado: true, esperado: true });
  const ROTAS = ['meeting', 'radarfuturo', 'future', 'windows', 'market', 'voices', 'competitors', 'science', 'portfolio',
    'etichette', 'etichetta', 'archive', 'sources', 'field', 'search'].concat(DETALHES);
  const acesas = [];
  for (const r of ROTAS) {
    const x = S.vals({ view: r, lang: 'it', committedQuery: 'vite', query: 'vite' });
    const f = Object.keys(x).filter((k) => /^is[A-Z]/.test(k) && x[k] === true && k !== 'isOrgs');
    if (f.length || !x.temLegadoFechado) acesas.push(r + ':' + f.join(','));
  }
  prova('H7 pote esperado e ausente: nenhuma rota desenha legado, demo ou Rete Commerciale; todas dizem NON SO', acesas.length === 0, acesas.join(' '));
  const x = S.vals({ view: 'meeting', lang: 'it' });
  prova('H7 o relogio e a barra lateral dizem NAO SEI, sem numeros do legado', /NAO SEI/.test(x.sideClock) && x.sideRows.length === 1 && x.sideRows[0].v === 'NAO SEI' &&
    [].concat(x.nav, x.navEvidence).filter((n) => n.route).every((n) => n.count === ''));
  prova('H7 a nota de ambiente nao fala da demo como dado', /NON SO/.test(x.envNote) && !/Dati al \d/.test(x.envNote));
  const L = montar({ semPublicado: true });
  prova('H7 sem a pagina pedir o pote (o banco de prova do casco antigo), o legado continua medivel', L.vals({ view: 'meeting', lang: 'it' }).isMeeting === true);
}

/* ── H8 · PROVVISORIO em todo id de cruzamento ───────────────────────────── */
{
  const P = V('portfolio');
  const obj = P.pote.objetos.filter((o) => o.especie === 'CROSSING');
  prova('H8 os cartoes de CROSSING do pote levam PROVVISORIO (D119)', obj.length === 2 && obj.every((o) => o.temProv && /PROVVISORIO/.test(o.prov)));
  const arq = V('archive').pote.objetos.filter((o) => o.especie === 'CROSSING');
  prova('H8 tambem no Archivio', arq.length === 2 && arq.every((o) => o.temProv));
}

/* ── H9 · a auditoria D97 ────────────────────────────────────────────────── */
{
  const r = spawnSync(process.execPath, ['italia-portale/audit/casco/d97-auditoria.mjs', '--json'], { cwd: RAIZ, encoding: 'utf8' });
  let A = null; try { A = JSON.parse(r.stdout); } catch (e) { A = null; }
  prova('H9 D97: 0 objetos fora do pote (ou sem prova)', !!A && A.OBJETOS.FORA_DA_INTELLIGENCE_OU_SEM_PROVA.length === 0 && A.OBJETOS.DISTINTOS === 25);
  prova('H9 D97: 0 cruzamentos sem prova na tela (2 na tela, 84 na aba rifiutati)', !!A && A.CRUZAMENTOS.SEM_A_PROVA_QUE_O_POTE_EXIGE.length === 0 &&
    A.CRUZAMENTOS.NA_TELA_FORA_DA_ANALISE.length === 0 && A.CRUZAMENTOS.DESENHADOS === 2 && A.CRUZAMENTOS.NA_ABA_RIFIUTATI === 84);
  prova('H9 D97: 0 rotas de legado com o pote, 0 sem o pote', !!A && A.ROTAS.ROTAS_DE_LEGADO_COM_O_POTE.length === 0 && A.SEM_POTE.ROTAS_DE_LEGADO_SEM_POTE.length === 0);
  prova('H9 D97 sai 0', r.status === 0, String(r.status));
}

console.log(`\nCASCO HOJE: ${provas - falhas}/${provas} provas`);
process.exit(falhas ? 1 : 0);
