// CASCO-PAINEL (D78) · o PAINEL DE OPERACAO, so de leitura: coleta, Intelligence e o que falta.
//
//     node italia-portale/audit/casco/painel-operacao.mjs --vivo=<arvore do vivo> --ondas=<pasta das ondas>
//          --sala=<LEITURA-SALA-PAINEL.json> --supervisor=<SUPERVISOR-ESTADO.json> --fecho-onda3=<FECHO-ONDA3.md>
//          --decisoes=<pergunta-emenda-exp-d78.txt> [--copia=<ficheiro.js>]
//
// Cada numero vem de um ARTEFACTO MEDIDO e leva ao lado a fonte e a data da medicao. Nada e escrito a
// mao: o que nao tem artefacto fica NAO SEI / NAO MEDIDO. O estado dos consertos e das instalacoes vem do
// Git (o ramo existe? o commit esta no vivo?), nunca de uma frase.
// Escreve `italia-portale/client/italy-painel.local.js` (fora do Git e do deploy, como a Sala).
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..', '..');
const CLIENTE = path.resolve(HERE, '..', '..', 'client');
const OPT = Object.fromEntries(process.argv.slice(2).filter((a) => a.startsWith('--') && a.includes('='))
  .map((a) => [a.slice(2, a.indexOf('=')), a.slice(a.indexOf('=') + 1)]));
for (const k of ['vivo', 'ondas', 'sala', 'supervisor', 'fecho-onda3', 'decisoes']) {
  if (!OPT[k]) { console.error('falta --' + k); process.exit(2); }
}
const NS = 'NAO SEI';
const VIVO_REF = 'origin/servico-20260923-0923';
const ler = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));
const sha = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const mtime = (f) => fs.statSync(f).mtime.toISOString();
const prova = (f) => ({ ficheiro: f.replace(/\\/g, '/'), sha256: sha(f).slice(0, 16), modificado: mtime(f) });
const git = (...a) => { try { return execFileSync('git', a, { cwd: REPO, encoding: 'utf8' }).trim(); } catch { return null; } };
const noVivo = (c) => (c ? git('merge-base', '--is-ancestor', c, VIVO_REF) !== null : false);

// ── A · COLETA ────────────────────────────────────────────────────────────
const soma = (o) => Object.values(o || {}).reduce((a, b) => a + (Number(b) || 0), 0);
function onda(nome, f, d, dataPorRun) {
  const fontes = d.FONTES || [];
  const porStatus = {}; for (const x of fontes) porStatus[x.STATUS || x.PORQUE_NAO_CORREU || NS] = (porStatus[x.STATUS || x.PORQUE_NAO_CORREU || NS] || 0) + 1;
  const dom = {}; for (const x of fontes) for (const [k, v] of Object.entries(x.PEDIDOS_POR_DOMINIO || x.PEDIDOS_POR_SITE || {})) dom[k] = (dom[k] || 0) + (Number(v) || 0);
  const s0 = (fontes[0] || {}).SALA_ANTES || (typeof d.SALA_INICIO === 'object' ? d.SALA_INICIO : null);
  const s1 = (fontes[fontes.length - 1] || {}).SALA_DEPOIS || (typeof d.SALA_FIM === 'object' ? d.SALA_FIM : null);
  const run = (fontes.find((x) => x.RUN_ID) || {}).RUN_ID || '';
  const m = /-(\d{4}-\d{2}-\d{2})-/.exec(run);
  return {
    nome, data: dataPorRun || (m ? m[1] : NS), inicio: d.INICIO || (fontes[0] || {}).HORA || NS,
    fim: d.FIM || (fontes[fontes.length - 1] || {}).HORA || NS, arvore: d.ARVORE || NS,
    fontes: fontes.length, correram: fontes.filter((x) => x.CORREU).length, porStatus,
    pedidos: soma(dom), dominios: Object.keys(dom).length, maxPorDominio: Math.max(0, ...Object.values(dom)),
    // a 1.a onda (BC5) guarda a Sala como NUMERO; as ondas web, como objeto de contagens
    salaAntes: s0 == null ? NS : (typeof s0 === 'object' ? s0.sala_de_espera : s0),
    salaDepois: s1 == null ? NS : (typeof s1 === 'object' ? s1.sala_de_espera : s1),
    // o teto por DOMINIO na onda inteira (D38) so existe desde a 2.a onda; na 1.a o teto era por site e por corrida
    tetoPorDominioNaOnda: !!d.LIVRO_DA_ONDA,
    parou: d.PAROU == null ? 'nenhum disjuntor' : String(d.PAROU), prova: prova(f), dominioPedidos: dom,
  };
}
const ondas = [];
const bc5 = path.join(OPT.vivo, 'ferramentas', 'big_collection', 'BC5-BIG-COLLECTION-1A-ONDA.json');
if (fs.existsSync(bc5)) ondas.push(onda('1.a onda (BC5)', bc5, ler(bc5)));
for (const pasta of fs.readdirSync(OPT.ondas).sort()) {
  const f = path.join(OPT.ondas, pasta, 'ONDA-WEB-ESTADO.json');
  if (!fs.existsSync(f)) continue;
  const m = /-(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})$/.exec(pasta);
  ondas.push(onda(pasta, f, ler(f), m ? `${m[1]}-${m[2]}-${m[3]}` : null));
}
ondas.sort((a, b) => `${a.data} ${a.inicio}`.localeCompare(`${b.data} ${b.inicio}`));
const ultima = ondas[ondas.length - 1];
const TETO = 5;
const dominiosUltima = Object.entries(ultima ? ultima.dominioPedidos : {}).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  .map(([d, n]) => ({ dominio: d, pedidos: n, noTeto: n >= TETO }));

const coorteF = path.join(OPT.vivo, 'ferramentas', 'big_collection', 'COORTE-BIG-COLLECTION-V1.json');
const coorte = ler(coorteF);
const foraPorque = {}; for (const x of coorte.FORA || []) { const k = (x.FALTA || [NS]).join(' + '); foraPorque[k] = (foraPorque[k] || 0) + 1; }
const vivoHead = git('rev-parse', '--short', VIVO_REF) || NS;

const sala = ler(OPT.sala);
let acum = 0;
const salaPorDia = (sala.POR_DIA || []).map((x) => ({ dia: x.dia, novos: x.n, total: (acum += x.n) }));
const sup = ler(OPT.supervisor);
const supMedido = fs.existsSync(OPT.supervisor.replace(/\.json$/, '.medido_em'))
  ? fs.readFileSync(OPT.supervisor.replace(/\.json$/, '.medido_em'), 'utf8').trim() : mtime(OPT.supervisor);

// ── B · INTELLIGENCE ──────────────────────────────────────────────────────
const travaF = path.join(OPT.vivo, 'docs', 'operacao', 'TRAVA-DA-INTELIGENCIA.json');
const trava = ler(travaF);
function ramo(nome) {
  const ref = `origin/${nome}`;
  const head = git('rev-parse', '--short', ref);
  if (!head) return { ramo: nome, existe: false };
  return { ramo: nome, existe: true, head, data: git('log', '-1', '--format=%cI', ref), assunto: git('log', '-1', '--format=%s', ref),
    noVivo: noVivo(head) };
}
function commitDoDefeito(ramoNome, d) {
  // o commit do ramo (fora do vivo) cujo assunto nomeia o defeito como palavra inteira
  const log = git('log', '--format=%h\t%cI\t%s', `${VIVO_REF}..origin/${ramoNome}`) || '';
  for (const l of log.split('\n')) {
    const [h, quando, s] = l.split('\t');
    if (s && new RegExp(`(^|[^0-9A-Za-z])${d}([^0-9]|$)`).test(s)) return { commit: h, quando, assunto: s, noVivo: noVivo(h) };
  }
  return null;
}
const decisoesTxt = fs.readFileSync(OPT.decisoes, 'utf8');
const oQue = (d) => { const m = new RegExp(`${d} ([^;]*?)(?=; D\\d|\\. Elegiveis|$)`).exec(decisoesTxt); return m ? m[1].trim() : NS; };
const DEFEITOS = [
  ['D1', 'INTELLIGENCE', 'int-consertos-v1'], ['D2', 'INTELLIGENCE', 'int-consertos-v1'], ['D3', 'INTELLIGENCE', 'int-consertos-v1'],
  ['D4', 'INTELLIGENCE', 'int-consertos-v1'], ['D5', 'INTELLIGENCE', null], ['D6', 'INTELLIGENCE', 'int-consertos-v1'],
  ['D7', 'INTELLIGENCE', 'int-consertos-v1'], ['D8', 'INTELLIGENCE', 'int-consertos-v1'], ['D9', 'COLLECTION', 'sala-leitura-v1'],
  ['D10', 'COLLECTION', 'sala-leitura-v1'],
].map(([d, lado, r]) => {
  const c = r ? commitDoDefeito(r, d) : null;
  const estado = !r ? 'CORRETO (nao e defeito, segundo a propria lista)'
    : !c ? 'SEM CONSERTO ENCONTRADO NO RAMO'
    // o estado vem do COMMIT que nomeia o defeito (declarado pelo dono do ramo); os testes do ramo nao foram
    // corridos aqui — por isso «declarado», nunca «provado»
    : c.noVivo ? 'CONSERTO NO VIVO (commit)' : 'CONSERTO DECLARADO NO RAMO · NAO INSTALADO';
  return { defeito: d, lado, oQue: oQue(d), ramo: r, commit: c ? c.commit : null, quando: c ? c.quando : null, estado };
});
const emenda = ramo('int-sala-exp-v1');

// ── C · O QUE FALTA (a regra do bot Luciano 23:17, registada no HANDOFF 23:31) ────────────
const fecho = fs.readFileSync(OPT['fecho-onda3'], 'utf8');
const veredito = (/\*\*VEREDITO_ONDA3\*\*\s*\|\s*([^|]+)\|/.exec(fecho) || [])[1];
const c9 = ramo('c9-sobre-ce28-v1');
const c2 = (() => { const r = git('branch', '-r', '--contains', 'b91e7661'); return r ? r.split('\n')[0].trim().replace('origin/', '') : null; })();
const c2r = c2 ? ramo(c2) : { ramo: NS, existe: false };
const falta = [
  { condicao: 'FECHAR-ONDA3 = PASS', estado: veredito ? veredito.replace(/\*/g, '').trim() : NS,
    ok: false, prova: prova(OPT['fecho-onda3']) },
  { condicao: 'C9 (idioma) instalado e provado no vivo', estado: c9.existe ? (c9.noVivo ? `SIM — ${c9.head} esta no vivo ${vivoHead}` : `NAO — ${c9.head} fora do vivo`) : NS,
    ok: !!(c9.existe && c9.noVivo), prova: { git: `origin/c9-sobre-ce28-v1 ⊂ ${VIVO_REF}` } },
  { condicao: 'C2 (juiz capa/materia) consertado', estado: c2r.existe ? (c2r.noVivo ? `SIM — ${c2r.head} no vivo` : `NAO INSTALADO — ramo ${c2r.ramo} @ ${c2r.head}`) : NS,
    ok: !!(c2r.existe && c2r.noVivo), prova: { git: c2r.existe ? `origin/${c2r.ramo}` : NS } },
  { condicao: 'VPN IT · teto por dominio · backup da Sala · robo parado', estado: `A MEDIR NO DISPARO. Agora: servico ${sup.SOURCE_CURATOR_SERVICE}, worker ${sup.WORKER_STATE} (robo NAO parado)`,
    ok: false, prova: prova(OPT.supervisor) },
];

// ── D · A LINHA DO TEMPO DAS INSTALACOES (CASCO-PAINEL-2) ─────────────────────
// Do reflog do ramo do VIVO: a hora em que o vivo passou a cada SHA, e a mensagem. E o registo do proprio
// Git da arvore do vivo — lido, nunca escrito.
const RAMO_VIVO = 'servico-20260923-0923';
const reflog = (() => {
  try {
    return execFileSync('git', ['-C', OPT.vivo, 'reflog', 'show', '--date=iso', '--format=%h%x09%gd%x09%gs', RAMO_VIVO],
      { encoding: 'utf8' }).trim().split('\n').map((l) => {
      const [h, gd, msg] = l.split('\t');
      const q = (/@\{([^}]+)\}/.exec(gd) || [])[1] || NS;
      return { sha: h, quando: q, mensagem: msg };
    });
  } catch { return []; }
})();
const vivoLocal = (() => { try { return execFileSync('git', ['-C', OPT.vivo, 'rev-parse', '--short', 'HEAD'], { encoding: 'utf8' }).trim(); } catch { return NS; } })();

// ── E · POR FONTE (CASCO-PAINEL-2): a coorte (64) e as prontas que ficaram fora (com o porque) ─────
// Juntado pelo RUN_ID: as linhas das ondas dizem SOURCE_ID + RUN_ID + pedidos; runs.ndjson (livro de
// corridas do vivo) diz o que a corrida fez; a Sala diz o que entrou; o livro de decisoes diz o que a
// Admissao decidiu. Nada e estimado: sem artefacto, o campo fica NAO SEI.
const runs = new Map();
const runsF = path.join(OPT.vivo, 'data', 'collection-ledger', 'italy', 'runs.ndjson');
if (fs.existsSync(runsF)) for (const l of fs.readFileSync(runsF, 'utf8').split('\n')) { if (!l.trim()) continue; try { const r = JSON.parse(l); runs.set(r.RUN_ID, r); } catch { /* linha partida: nao conta */ } }
const decisoesF = path.join(OPT.vivo, 'data', 'samples', 'LIVRO-DE-DECISOES.json');
const decPorFonte = {};
if (fs.existsSync(decisoesF)) for (const d of (ler(decisoesF).DECISOES || [])) {
  const s = (((d.evidencia || {}).portoes || {}).origem || {}).origem;
  if (!s) continue;
  (decPorFonte[s] = decPorFonte[s] || {})[d.resultado] = ((decPorFonte[s] || {})[d.resultado] || 0) + 1;
}
const exportSala = OPT.export && fs.existsSync(OPT.export) ? ler(OPT.export) : [];
const salaPorFonte = {};
for (const x of exportSala) (salaPorFonte[x.source_id] = salaPorFonte[x.source_id] || []).push(x);
const visitasPorFonte = {};
for (const o of ondas) {
  const d = ler(path.join(o.prova.ficheiro));
  for (const x of d.FONTES || []) {
    const r = runs.get(x.RUN_ID) || null;
    (visitasPorFonte[x.SOURCE_ID] = visitasPorFonte[x.SOURCE_ID] || []).push({
      onda: o.nome, data: o.data, hora: x.HORA || NS, correu: !!x.CORREU, status: x.STATUS || NS, porqueNaoCorreu: x.PORQUE_NAO_CORREU || null,
      runId: x.RUN_ID || null, pedidos: soma(x.PEDIDOS_POR_DOMINIO || x.PEDIDOS_POR_SITE), dominio: x.DOMINIO || Object.keys(x.PEDIDOS_POR_SITE || {})[0] || NS,
      novosDocumentos: r ? (r.contadores || {}).NEW_DOCUMENTS : NS, inicioCorrida: r ? r.STARTED_AT : NS });
  }
}
const distintos = (xs) => [...new Set(xs.filter((v) => v && v !== 'NAO SEI'))];
function fonte(sid, grupo, extra) {
  const itens = salaPorFonte[sid] || [];
  const visitas = visitasPorFonte[sid] || [];
  const ultima = visitas[visitas.length - 1] || null;
  const pubs = distintos(itens.map((i) => String(i.published_at || '').slice(0, 10))).sort();
  return Object.assign({
    sourceId: sid, grupo, visitas, nVisitas: visitas.length, nCorreu: visitas.filter((v) => v.correu).length,
    pedidosTotal: visitas.reduce((a, v) => a + (v.pedidos || 0), 0), ultimaVisita: ultima,
    salaItens: itens.length, salaDatasDoFato: distintos(itens.map((i) => i.fact_time)), salaLugaresDoFato: distintos(itens.map((i) => i.fact_location)),
    salaPublicacao: pubs.length ? `${pubs[0]}${pubs.length > 1 ? ' → ' + pubs[pubs.length - 1] : ''}` : NS,
    salaLugarDaFonte: distintos(itens.map((i) => i.source_location)),
    admissao: decPorFonte[sid] || {},
  }, extra);
}
const fontes = [
  ...(coorte.COORTE || []).map((x) => fonte(x.SOURCE_ID, 'COORTE', { universo: x.UNIVERSO, indexUrl: x.INDEX_URL,
    ultimoCanario: ((x.ULTIMO_CANARIO || {}).OBSERVED_AT) || NS, porqueFora: null })),
  ...(coorte.FORA || []).map((x) => fonte(x.SOURCE_ID, 'PRONTA_FORA_DA_COORTE', { universo: x.UNIVERSO, indexUrl: x.INDEX_URL || NS,
    ultimoCanario: NS, porqueFora: (x.FALTA || [NS]).join(' + ') })),
];
const naLista = new Set(fontes.map((f) => f.sourceId));
const naSalaForaDaLista = Object.keys(salaPorFonte).filter((s) => !naLista.has(s)).sort();
// fontes que JA deram itens a Sala mas nao estao na coorte atual nem nas prontas: mostradas a parte, para
// que a pagina por fonte nao esconda de onde veio nenhum item da Sala
for (const s of naSalaForaDaLista) {
  fontes.push(fonte(s, 'SO_NA_SALA', { universo: (salaPorFonte[s][0] || {}).universo || NS, indexUrl: NS, ultimoCanario: NS,
    porqueFora: 'nao esta na coorte congelada atual nem nas prontas que ficaram fora (deu itens em ondas/corridas anteriores)' }));
}

const pacote = {
  gerado: new Date().toISOString(), vivo: vivoHead, vivoLocal,
  instalacoes: reflog, fontes, naSalaForaDaLista,
  fontesProvas: { coorte: prova(coorteF), runs: fs.existsSync(runsF) ? prova(runsF) : NS, decisoes: fs.existsSync(decisoesF) ? prova(decisoesF) : NS,
    export: OPT.export && fs.existsSync(OPT.export) ? prova(OPT.export) : NS },
  coleta: {
    ondas, teto: TETO, ultimaOnda: ultima ? ultima.nome : NS, dominiosUltima,
    coorte: { estado: coorte.ESTADO, congeladaEm: (coorte.CONGELAMENTO || {}).EM || NS, dentro: (coorte.COORTE || []).length,
      fora: (coorte.FORA || []).length, foraPorque, prova: prova(coorteF) },
    sala: { medidaEm: sala.AGORA, total: Number(sala.TOTAL), porDia: salaPorDia, cobertura: sala.COBERTURA,
      soLeitura: sala.SHOW_TRANSACTION_READ_ONLY, prova: prova(OPT.sala) },
    servico: { medidoEm: supMedido, servico: sup.SOURCE_CURATOR_SERVICE, worker: sup.WORKER_STATE, filaElegivel: sup.QUEUE_ELIGIBLE_NOW,
      batimentoVelho: sup.HEARTBEAT_STALE, idadeBatimentoS: sup.HEARTBEAT_AGE_S, reinicios: sup.RESTARTS_TOTAL, prova: prova(OPT.supervisor) },
  },
  intelligence: {
    estado: trava.COLLECTION_FOUNDATION_CLOSED !== 'SIM' ? 'BLOQUEADA' : 'LIVRE',
    regra: trava.REGRA, fundacaoFechada: trava.COLLECTION_FOUNDATION_CLOSED, travaMedidaEm: trava.MEDIDO_EM,
    criteriosCumpridos: trava.QUAIS_JA_CUMPRIDOS, criteriosEmFalta: trava.QUAIS_FALTAM, prova: prova(travaF),
    emenda: Object.assign({ estado: 'PROPOSTA — espera as 2 assinaturas do dono (emenda + linha na trava)' }, emenda),
    defeitos: DEFEITOS, fonteDosDefeitos: prova(OPT.decisoes),
  },
  falta,
};
const js = '/* GERADO por italia-portale/audit/casco/painel-operacao.mjs — fora do Git e do deploy. */\n'
  + 'window.ITALY_PAINEL_OPERACAO = ' + JSON.stringify(pacote) + ';\n';
fs.writeFileSync(path.join(CLIENTE, 'italy-painel.local.js'), js);
if (OPT.copia) fs.writeFileSync(OPT.copia, js);
console.log(JSON.stringify({ vivo: vivoHead, vivoLocal, instalacoes: reflog.length, fontes: fontes.length, naSalaForaDaLista, ondas: ondas.map((o) => [o.nome, o.data, o.fontes, o.correram, o.pedidos, o.maxPorDominio, `${o.salaAntes}->${o.salaDepois}`]),
  coorte: pacote.coleta.coorte.dentro + '/' + pacote.coleta.coorte.fora, defeitos: DEFEITOS.map((d) => d.defeito + ':' + d.estado),
  emenda: emenda.head, falta: falta.map((f) => f.condicao + ' => ' + f.estado) }, null, 1));
