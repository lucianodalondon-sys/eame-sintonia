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
     Q8  o SHA do pote contra o manifesto esta dito na tela, com o MODO da conferencia; e um pote cujo
         sha nao confere continua a aparecer em ambar como NON CORRISPONDE;
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
/* AJUSTE DECLARADO (missao CASCO-HOJE-MINIMO-HONESTO, item 2): #etichette e a Label Intelligence como PRODUTO
   DE FERRAMENTA (registada pelo publicador, com a data do snapshot), nao o compartimento portfolio do pote. As
   provas que exigem o pote numa rota passam a correr nas outras onze; #etichette tem prova propria abaixo. */
const ROTAS_POTE = ROTAS.filter((r) => r !== 'etichette');

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
  /* AJUSTE DECLARADO (missao CASCO-HOJE-MINIMO-HONESTO): a missao manda trazer por merge a linha de servico
     (claude/single-reference-gateway-hhhj7t), e o gerador do pote vive nela — `pacote/pote_intelligence_casco.py`
     passou a estar no ramo por ordem do dono, e a missao autoriza mexer nele. A lei que esta prova guarda e
     «so ESTE pote vai AO AR»: continua medida, agora no sitio certo — o gerador nao e servido (vive fora de
     italia-portale/client, que e o unico diretorio publicado) e o pote local e as PARA-O-CASCO continuam fora
     do ramo. */
  const VJ = JSON.parse(ler('vercel.json'));
  prova('Q2 o gerador do pote nao e servido; as pastas PARA-O-CASCO e o pote local nao entram no ramo',
    !rastreados.some((f) => f.startsWith('italia-portale/client/') && /pote_intelligence_casco/.test(f)) &&
    String(VJ.outputDirectory || '').replace(/\/$/, '') === 'italia-portale/client' &&
    !rastreados.some((f) => /PARA-O-CASCO/.test(f)) && !rastreados.includes('italia-portale/client/sintonia-pote.js'),
    'outputDirectory=' + VJ.outputDirectory);
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
  const x = ROTAS_POTE.map((r) => [r, V(r, lang)]);
  prova(`Q3 [${lang}] as 11 rotas de ferramenta (fora #etichette) leem o pote e a publicacao`,
    x.every(([, v]) => v.poteVista === true && v.potePubVista === true), x.filter(([, v]) => !v.potePubVista).map(([r]) => r).join(','));
  prova(`Q3 [${lang}] faixa D114 + EXPERIMENTAL em toda vista`,
    x.every(([, v]) => /D114/.test(v.potePub.faixa) && /EXPERIMENTAL/.test(v.potePub.faixa) && /EXPERIMENTAL/.test(v.pote.faixa)));
}
{
  const e = V('etichette');
  prova('Q3 #etichette desenha a Label Intelligence como PRODUTO DE FERRAMENTA, nao o pote',
    e.temLabelFerramenta === true && e.poteVista === false && e.isEtichette === true && /PRODOTTO DI STRUMENTO/.test(e.labelFerramenta.titulo));
}
for (const r of ['sala', 'painel', 'search']) prova(`Q3 #${r} nao e ferramenta: a publicacao nao a toma`, V(r).potePubVista === false);

/* ── Q4 · os 86 cruzamentos ──────────────────────────────────────────────
   AJUSTE DECLARADO (missao CASCO-HOJE-MINIMO-HONESTO, item 1; D97): a tela PRINCIPAL do Portafoglio desenha
   so os cruzamentos que SAO objeto do pote (2); os outros 84 vao para a aba «rifiutati», com o motivo. Nenhuma
   prova de conteudo afrouxa: as mesmas asserções correm sobre a uniao das duas abas (86, cada um uma vez), e
   ha provas novas sobre a separacao. */
{
  const C = V('portfolio').potePub.cruz;
  const principais = C.principais;
  const aba = C.grupos.flatMap((g) => g.linhas);
  const todas = principais.concat(aba);
  const noPote = new Set(POTE.COMPARTIMENTOS.portfolio.OBJETOS.map((o) => o.OBJETO_ID));
  const recusa = new Set(POTE.RECUSADOS.filter((r) => r.COMPARTIMENTO === 'portfolio').map((r) => r.OBJETO_ID));
  prova('Q4 a tela principal so tem os cruzamentos que sao objeto do pote (2)',
    principais.length === 2 && principais.every((l) => noPote.has(l.id) && l.noPote === true) && noPote.size === 2);
  prova('Q4 a aba «rifiutati» tem os outros 84, nenhum objeto do pote', aba.length === 84 && aba.every((l) => !noPote.has(l.id) && l.noPote === false));
  prova('Q4 os 86 cruzamentos estao nas duas abas', todas.length === 86 && ANALISE.CROSSINGS.length === 86);
  prova('Q4 cada cruzamento aparece uma vez', new Set(todas.map((l) => l.id)).size === 86);
  const porId = Object.fromEntries(ANALISE.CROSSINGS.map((c) => [c.OBJETO_ID, c]));
  prova('Q4 o estado desenhado e o ESTADO_R7 da Intelligence (nenhum recalculo), escrito LITERAL',
    todas.every((l) => porId[l.id] && porId[l.id].ESTADO_R7 === l.estado && l.estadoNome.endsWith(l.estado)));
  const cont = {}; todas.forEach((l) => { cont[l.estado] = (cont[l.estado] || 0) + 1; });
  prova('Q4 contagem por estado = resumo da analise (5 / 29 / 48 / 4)',
    igual(Object.keys(cont).sort().map((k) => [k, cont[k]]), Object.keys(ANALISE.CROSSINGS_RESUMO.POR_ESTADO).sort().map((k) => [k, ANALISE.CROSSINGS_RESUMO.POR_ESTADO[k]])) &&
    cont.POSSIBLE_ANSWER_YES_A_CONFIRMAR === 5 && cont.POSSIBLE_ANSWER_NO === 29 && cont.PARTIAL_GRAO_INCOMPATIVEL === 48 && cont.NOT_POSSIBLE === 4);
  const sim = todas.filter((l) => l.temMarca);
  prova('Q4 so os 5 «sim a confirmar» levam a marca A CONFIRMAR',
    sim.length === 5 && sim.every((l) => l.marca === 'A CONFIRMAR' && l.estado === 'POSSIBLE_ANSWER_YES_A_CONFIRMAR'));
  prova('Q4 os 5 «sim» sao os do relatorio (1209, 1221, 1223, 1228, 1229) — e estao na aba rifiutati',
    igual(sim.map((l) => l.id.split('-')[2]).sort(), ['1209', '1221', '1223', '1228', '1229']) && sim.every((l) => !noPote.has(l.id)));
  prova('Q4 o «sim» nunca tem a forma da oportunidade (verde): amarelo tracejado',
    sim.every((l) => l.traco === 'dashed' && l.color === '#F5B317'));
  prova('Q4 fonte candidata marcada como candidata (VIA = EXTENSAO_DECLARADA), e so ela',
    todas.every((l) => (porId[l.id].VIA === 'EXTENSAO_DECLARADA') === /CANDIDATA/.test(l.via)) &&
    todas.filter((l) => /CANDIDATA/.test(l.via)).length === 47);
  prova('Q4 cada cruzamento diz o que o pote fez com ele (2 objetos, 80 recusados, 4 ausentes)',
    todas.filter((l) => noPote.has(l.id)).every((l) => /NEL POTE/.test(l.pote)) &&
    todas.filter((l) => recusa.has(l.id)).every((l) => /RIFIUTATO/.test(l.pote) && /DOCUMENT_ID|G0/.test(l.pote)) &&
    todas.filter((l) => !noPote.has(l.id) && !recusa.has(l.id)).length === 4 &&
    todas.filter((l) => !noPote.has(l.id) && !recusa.has(l.id)).every((l) => /ASSENTE/.test(l.pote)));
  prova('Q4 a aba rifiutati conta os motivos que o pote escreveu (79 PROVA_INCOMPLETA · 1 G0 · 4 ausentes)',
    igual(Object.fromEntries(C.recMotivos.map((m) => [m.k, Number(m.v)])), { ITEM_BLOQUEADO_EM_G0: 1, PROVA_INCOMPLETA: 79, AUSENTE_DO_POTE: 4 }));
  prova('Q4 a prova de cada cruzamento: URL http(s) como link e data de publicacao (NAO SEI em destaque)',
    todas.every((l) => l.prova.temUrl && l.prova.url === porId[l.id].URL) &&
    todas.every((l) => (porId[l.id].PUBLISHED_AT === 'NAO SEI') === (l.prova.pubColor === '#F5B317')) &&
    todas.every((l) => l.prova.pub.endsWith(String(porId[l.id].PUBLISHED_AT))));
  prova('Q4 NAO SEI do lugar continua NAO SEI, em destaque',
    todas.every((l) => { const c = l.chaves.find((k) => k.k === 'luogo'); return !/NAO SEI/.test(c.v) || c.color === '#F5B317'; }));
  prova('Q4 cada cruzamento diz o que NAO e (OPPORTUNITY · RECOMENDACAO)', todas.every((l) => /OPPORTUNITY/.test(l.naoE)));
  prova('Q4 cada id de cruzamento leva a marca PROVVISORIO (D119)', todas.every((l) => /PROVVISORIO/.test(l.prov) && /D119/.test(l.prov)));
  prova('Q4 dentro de cada estado a ordem e a da analise',
    C.grupos.every((g) => igual(g.linhas.map((l) => l.id), ANALISE.CROSSINGS.filter((c) => c.ESTADO_R7 === g.k && !noPote.has(c.OBJETO_ID)).map((c) => c.OBJETO_ID))) &&
    igual(principais.map((l) => l.id), ANALISE.CROSSINGS.filter((c) => noPote.has(c.OBJETO_ID)).map((c) => c.OBJETO_ID)));
  prova('Q4 a leitura da publicacao nao ordena, nao pontua (sem sort/score/rank no codigo)',
    !/\.sort\(|score|rank|relevan/i.test(FONTE['sintonia-pote-publicacao.js'].replace(/\/\*[\s\S]*?\*\//g, '')));
  const x = V('portfolio');
  prova('Q4 por omissao a aba aberta e a do pote; «rifiutati» so por clique', x.cruzAbaPote === true && x.cruzAbaRec === false);
  prova('Q4 a Label Intelligence (etichette) nao rele os 86: e produto de ferramenta', V('etichette').potePubVista === false);
}

/* ── Q5 · recusados visiveis ─────────────────────────────────────────────── */
{
  let soma = 0, ok = true, det = '';
  const vistos = new Set();
  for (const r of ROTAS_POTE) {
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
  /* AJUSTE DECLARADO (missao CASCO-HOJE-MINIMO-HONESTO, itens 2, 5 e 6): #etichette conta os produtos da
     ferramenta registada (166, o payload selado); #radarfuturo conta so os fatos com chave de dominio provada
     (a Agenda nao e radar); a barra lateral conta OBJETOS DISTINTOS (25, nunca a soma de 47 das gavetas) e
     os cruzamentos que SAO objeto do pote (2, nunca os 86 da analise). */
  const Qp = M.ctx.SINTONIA_POTE_PUBLICACAO;
  const conta = (route) => {
    if (route === 'etichette') return M.ctx.SINTONIA_POTE_PUBLICADO.LABEL_INTELLIGENCE.CONTAGENS.products;
    const k = M.ctx.SINTONIA_POTE_CASCO.compartimentoDaVista(POTE, route);
    if (!k) return '';
    if (route === 'radarfuturo') return POTE.COMPARTIMENTOS[k].OBJETOS.filter((o) => Qp.chavesDeDominio(o).length > 0).length;
    return POTE.COMPARTIMENTOS[k].OBJETOS.length;
  };
  const itens = [].concat(x.nav, x.navEvidence, x.navIntegrationItems).filter((n) => n.route);
  prova('Q7 o menu conta os objetos do compartimento de cada rota',
    itens.length >= 10 && itens.every((n) => n.count === conta(n.route)), itens.map((n) => n.route + '=' + n.count).join(' '));
  prova('Q7 o Radar delle Opportunita conta 0, como o pote', x.nav.find((n) => n.route === 'meeting').count === 0);
  prova('Q7 a barra lateral conta 25 objetos distintos, 2 cruzamentos no pote e 245 recusados',
    igual(x.sideRows.slice(1).map((r) => r.v), [25, 2, 245]), JSON.stringify(x.sideRows.slice(1).map((r) => r.v)));
}

/* ── Q8 · o SHA do pote contra o manifesto ───────────────────────────────
   AJUSTE DECLARADO (missao ACERVO-ORGANIZADO, item 6, sobre a D114): esta prova esperava
   «NON CORRISPONDE» porque a causa nao estava medida. Foi medida: o manifesto fez o hash dos
   bytes CRLF, o Git guarda LF, e LF -> CRLF nos bytes do Git da exatamente o sha declarado.
   O publicador passou a dizer o MODO (IGUAL_BYTE_A_BYTE / IGUAL_APOS_FIM_DE_LINHA_CRLF /
   DIFERENTE). A prova nao afrouxa: (a) o modo real e o CRLF e a tela di-lo por extenso; (b) o
   caminho do ambar continua provado, com um pote que nao confere. */
{
  const m = V('sources').potePub.meta.find((q) => /SHA256/.test(q.k));
  const pub = montar().ctx.SINTONIA_POTE_PUBLICADO;
  prova('Q8 o publicado declara o modo CRLF e o sha em CRLF e o do manifesto',
    pub.SHA256_CONFERENCIA === 'IGUAL_APOS_FIM_DE_LINHA_CRLF' && pub.SHA256_CONFERE_COM_O_MANIFESTO === true &&
    pub.POTE_SHA256_EM_CRLF === pub.SHA256_DECLARADO_NO_MANIFESTO && pub.POTE_SHA256 !== pub.SHA256_DECLARADO_NO_MANIFESTO);
  prova('Q8 a tela diz que confere SO pelo fim de linha, sem ambar',
    !!m && /fine riga/.test(m.v) && /CRLF/.test(m.v) && !/NON CORRISPONDE/.test(m.v) && m.color !== '#F5B317', m && m.v);
  const N = montar('', (ctx) => { ctx.SINTONIA_POTE_PUBLICADO.SHA256_CONFERENCIA = 'DIFERENTE';
    ctx.SINTONIA_POTE_PUBLICADO.SHA256_CONFERE_COM_O_MANIFESTO = false; });
  const mn = N.vals({ view: 'sources', lang: 'it' }).potePub.meta.find((q) => /SHA256/.test(q.k));
  prova('Q8 um pote cujo sha nao confere aparece NON CORRISPONDE, em ambar',
    !!mn && /NON CORRISPONDE/.test(mn.v) && mn.color === '#F5B317', mn && mn.v);
  const B = montar('', (ctx) => { ctx.SINTONIA_POTE_PUBLICADO.SHA256_CONFERENCIA = 'OUTRO_MODO_QUALQUER'; });
  const mb = B.vals({ view: 'sources', lang: 'it' }).potePub.meta.find((q) => /SHA256/.test(q.k));
  prova('Q8 um modo que o publicador nao conhece nao passa por «corrisponde»',
    !!mb && /NON CORRISPONDE/.test(mb.v) && mb.color === '#F5B317', mb && mb.v);
}

/* ── Q9 · um pote de outra corrida nao herda estes cruzamentos ──────────── */
{
  const O = montar('', (ctx) => { const p = clone(ctx.SINTONIA_POTE_PUBLICADO.POTE); p.INTELLIGENCE_RUN_ID = 'IR-outra-corrida';
    Object.values(p.COMPARTIMENTOS).forEach((e) => (e.OBJETOS || []).forEach((o) => (o.PROVA || []).forEach((q) => { q.INTELLIGENCE_RUN_ID = 'IR-outra-corrida'; })));
    ctx.SINTONIA_POTE = p; });
  const x = O.vals({ view: 'portfolio', lang: 'it' });
  /* AJUSTE DECLARADO (missao CASCO-HOJE-MINIMO-HONESTO, item 6): a linha «incroci» deixou de ser o TOTAL da
     analise R7 (que era NAO SEI para outra corrida) e passou a contar os cruzamentos que sao objeto do pote
     CARREGADO. A lei desta prova continua: nada da analise R7 e herdado — o numero vem do pote da outra corrida. */
  const outro = O.ctx.SINTONIA_POTE;
  const cruzDoOutro = new Set(Object.values(outro.COMPARTIMENTOS).flatMap((e) => (e.OBJETOS || []).filter((o) => o.ESPECIE === 'CROSSING').map((o) => o.OBJETO_ID))).size;
  prova('Q9 pote de outra corrida: o leitor desenha-o, a publicacao R7 cala-se',
    x.poteVista === true && x.potePubVista === false && x.sideRows[2].v === cruzDoOutro &&
    x.sideRows[2].v !== ANALISE.CROSSINGS_RESUMO.TOTAL);
}

/* ── Q11 · codigo ao lado de um nome, titulo sem maiusculas (ADAMA) ─────── */
{
  const semNome = [], caps = [];
  for (const lang of ['it', 'en']) for (const r of ROTAS_POTE.concat(['field'])) {
    const x = V(r, lang);
    const t = r === 'field' ? x.potePub.campo.titulo : x.pote.titulo;
    if (!t || t === t.toUpperCase()) caps.push(lang + ':' + r + '=' + t);
    for (const o of x.pote.objetos || []) {
      if (!/ · /.test(o.especieRotulo) || !o.especieRotulo.endsWith(o.especie)) semNome.push(o.especie);
      for (const c of [].concat(o.chaves, o.fora)) if (/^[A-Z0-9_]+$/.test(c.k) && c.rotulo === c.k) semNome.push(c.k);
    }
  }
  prova('Q11 o titulo de cada vista do pote nao esta em MAIUSCULAS', caps.length === 0, caps.slice(0, 4).join(' | '));
  prova('Q11 todo codigo do contrato usado como rotulo leva o nome humano ao lado (e o codigo fica)',
    semNome.length === 0, [...new Set(semNome)].slice(0, 6).join(','));
  const x = V('portfolio');
  prova('Q11 o rotulo nao muda o dado: k, v e especie continuam os do leitor',
    x.pote.objetos.every((o, i) => o.especie === POTE.COMPARTIMENTOS.portfolio.OBJETOS[i].ESPECIE &&
      o.chaves.every((c) => c.k in POTE.COMPARTIMENTOS.portfolio.OBJETOS[i].CHAVES)));
}

/* ── Q12 · a sonda olivo x mosca, nas Finestre, com o juizo da Intelligence ── */
{
  const P = V('windows').potePub;
  const J = ANALISE.CORTE_VERTICAL.JULGAMENTO_DA_SONDA;
  const val = (code) => (P.sonda.juizo.find((c) => c.k.endsWith(code)) || {}).v || '';
  prova('Q12 as Finestre desenham a sonda com os 13 itens do corte vertical',
    P.temSonda === true && P.sonda.itens.length === ANALISE.CORTE_VERTICAL.ITENS.length && P.sonda.itens.length === 13);
  prova('Q12 o juizo e o da Intelligence (NO_DEFENSIBLE_ACTION_YET · janela NO · agir NAO)',
    val('RESULTADO').endsWith(J.RESULTADO) && val('WINDOW_OPEN_NOW') === 'NO' && val('ACT_NOW') === 'NAO' &&
    J.RESULTADO === 'NO_DEFENSIBLE_ACTION_YET');
  prova('Q12 a sonda diz que nao e janela instalada', /NON è una finestra installata/.test(P.sonda.titulo) && /nao e CAP-WIN/.test(P.sonda.execucao));
  prova('Q12 a sonda so aparece nas Finestre', ROTAS.filter((r) => r !== 'windows').every((r) => V(r).potePub.temSonda === false));
}

/* ── Q10 · os blocos da publicacao ligam so ao que existe ───────────────── */
{
  const a = HTML.indexOf('<!-- ================= POTE PUBLICADO (D114) · LA FASCIA');
  const b = HTML.indexOf('<!-- ================= POTE-UNICO · IL COMPARTIMENTO', a);
  const c = HTML.indexOf('<!-- ================= POTE PUBLICADO (D114) · CIO CHE');
  const d = HTML.indexOf('<!-- ================= FIM DO POTE PUBLICADO', c);
  const bloco = HTML.slice(a, b) + HTML.slice(c, d);
  const soltas = new Set();
  for (const view of ['portfolio', 'windows', 'sources', 'field', 'archive', 'meeting']) {
    const x = V(view); const P = x.potePub;
    const gr = P.cruz.grupos[0] || {}; const lx = (gr.linhas || [])[0] || P.cruz.principais[0] || {};
    const si = P.sonda.itens[0] || {}; const fi = P.fontes.sinais[0] || {};
    const alias = { m: P.meta[0], e: P.cruz.resumo[0], gr, x: lx, c: (lx.chaves || [])[0] || P.sonda.juizo[0] || P.fontes.novas[0] || P.radar.juizo[0],
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
