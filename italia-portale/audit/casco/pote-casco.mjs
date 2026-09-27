// CASCO-POTE · o carregador do POTE da Intelligence para as ferramentas do casco.
//
//     node italia-portale/audit/casco/pote-casco.mjs <POTE-*.json | pasta intelligence-experimental> [saida-copia.js]
//
// Fluxo unico (D97): SALA -> INTELLIGENCE -> POTE -> CASCO. O casco NAO le a Sala: le o pote que a
// Intelligence escreveu (contrato POTE_INTELLIGENCE_CASCO/v1, dono = Intelligence) e desenha-o.
// Este gerador SO TRANSPORTA e ACHATA para a tela: nao cruza, nao completa NAO SEI, nao promove especie,
// nao escolhe ferramenta (SOUL §44). O item da Sala aparece so como PROVA de um objeto (§38).
//
// Escreve `italia-portale/client/italy-pote.local.js` (window.SINTONIA_POTE). ⚠️ O pote e
// EXPERIMENTAL · NAO_PARA_CLIENTE com GATE_PARA_CLIENTE = FECHADO e traz trechos de texto da Sala:
// o ficheiro esta no .gitignore e no .vercelignore do cliente e so e pedido com ?pote=local.
//
// Recusa (sai com erro, nada escrito) quando: o CONTRATO nao e POTE_INTELLIGENCE_CASCO/v1; falta a MARCA;
// a conferencia do proprio pote nao PASSA; os compartimentos nao sao as 12 vistas. Objeto cuja
// SALA_CHAVE nao navega para a CAMADA_DE_EVIDENCIA e contado como RECUSADO e nao e desenhado.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENTE = path.resolve(HERE, '..', '..', 'client');
const [ARG, COPIA] = process.argv.slice(2);
if (!ARG) { console.error('uso: pote-casco.mjs <POTE-*.json | pasta intelligence-experimental> [copia.js]'); process.exit(2); }

const CONTRATO = 'POTE_INTELLIGENCE_CASCO/v1';
const MARCA = 'EXPERIMENTAL · NAO_PARA_CLIENTE';
const VISTAS = ['meeting', 'radarfuturo', 'windows', 'etichette', 'portfolio', 'market', 'voices', 'competitors', 'science', 'future', 'archive', 'sources'];
const NS = 'NAO SEI';

// A corrida MAIS NOVA disponivel: numa pasta, o PARA-O-CASCO-R<n> de maior n que tenha um POTE-*.json.
function acharPote(arg) {
  const st = fs.statSync(arg);
  if (st.isFile()) return arg;
  const cands = fs.readdirSync(arg).map((d) => /^PARA-O-CASCO-R(\d+)$/.exec(d)).filter(Boolean)
    .map((m) => ({ n: Number(m[1]), dir: path.join(arg, m[0]) }))
    .map((c) => ({ ...c, pote: (fs.readdirSync(c.dir).find((f) => /^POTE-.*\.json$/.test(f)) || null) }))
    .filter((c) => c.pote).sort((a, b) => b.n - a.n);
  if (!cands.length) throw new Error(`nenhum PARA-O-CASCO-R*/POTE-*.json em ${arg}`);
  return path.join(cands[0].dir, cands[0].pote);
}

const FICHEIRO = acharPote(ARG);
const BYTES = fs.readFileSync(FICHEIRO);
const P = JSON.parse(BYTES.toString('utf8'));
const recusa = (m) => { console.error('RECUSADO:', m); process.exit(1); };
if (P.CONTRATO !== CONTRATO) recusa(`CONTRATO = ${P.CONTRATO}, esperado ${CONTRATO}`);
if (P.MARCA !== MARCA) recusa('pote sem a MARCA EXPERIMENTAL · NAO_PARA_CLIENTE');
if (!/^PASSA/.test(String(P.CONFERENCIA_DO_POTE || ''))) recusa(`CONFERENCIA_DO_POTE = ${P.CONFERENCIA_DO_POTE}`);
const comp = P.COMPARTIMENTOS || {};
const faltam = VISTAS.filter((v) => !comp[v]);
if (faltam.length) recusa(`compartimentos em falta: ${faltam.join(', ')}`);

const EV = (P.CAMADA_DE_EVIDENCIA && P.CAMADA_DE_EVIDENCIA.ITENS) || {};
const primeiraLinha = (t, n = 140) => { const l = String(t || '').split(/\r?\n/).map((x) => x.replace(/\f/g, '').trim()).filter(Boolean)[0] || ''; return l.length > n ? l.slice(0, n - 1) + '…' : l; };
const curto = (v, n = 260) => { if (v == null) return NS; const t = typeof v === 'string' ? v : Array.isArray(v) ? v.map((x) => (typeof x === 'object' ? JSON.stringify(x) : String(x))).join(' · ') : JSON.stringify(v); return t.length > n ? t.slice(0, n - 1) + '…' : t; };

// os campos que o contrato do pote traz por especie, na ordem em que se leem — o valor vai tal como veio
const CAMPOS = [
  ['FACT_TIME', (o) => o.FACT_TIME != null ? `${o.FACT_TIME}${o.FACT_TIME_PRECISION ? ' · precisao ' + o.FACT_TIME_PRECISION : ''}${o.FACT_TIME_KIND ? ' · ' + o.FACT_TIME_KIND : ''}` : null],
  ['INTERVALO', (o) => o.INTERVALO ? `${o.INTERVALO.INICIO || NS} → ${o.INTERVALO.FIM || NS}` : null],
  ['FACT_LOCATION', (o) => o.FACT_LOCATION != null ? `${o.FACT_LOCATION}${o.FACT_LOCATION_ESTADO ? ' · ' + o.FACT_LOCATION_ESTADO : ''}` : null],
  ['BASE', (o) => o.BASE != null ? curto(o.BASE, 320) : null],
  ['INCERTEZA', (o) => o.INCERTEZA != null ? curto(o.INCERTEZA, 400) : null],
  ['NAO_E', (o) => o.NAO_E ? o.NAO_E.join(' · ') : null],
  ['PERGUNTA', (o) => o.PERGUNTA || null],
  ['ESTADO', (o) => o.ESTADO || o.ESTADO_ATUAL || null],
  ['TENTADOS / POSSIVEIS', (o) => o.TENTADOS != null ? `${o.TENTADOS} / ${o.POSSIVEIS}` : null],
  ['CHAVES_EM_FALTA', (o) => o.CHAVES_EM_FALTA ? Object.entries(o.CHAVES_EM_FALTA).map(([k, n]) => `${k} ${n}`).join(' · ') : null],
  ['APONTA_PARA', (o) => o.APONTA_PARA ? o.APONTA_PARA.join(' · ') : null],
  ['VISTO_EM', (o) => o.VISTO_EM ? o.VISTO_EM.map((r) => `${r.RODADA} ${r.SIGNAL_ID || ''} (${r.RULESET || ''})`).join(' → ') : null],
  ['T', (o) => o.ESPECIE === 'SOURCE_CONTRIBUTION_PROFILE' ? o.T : null],
  ['BASICO', (o) => o.BASICO ? `itens ${o.BASICO.ITENS} · documentos ${o.BASICO.DOCUMENTOS_DISTINTOS} · reobservacoes ${o.BASICO.REOBSERVACOES}` : null],
  ['COMPLETUDE', (o) => o.COMPLETUDE ? `FACT_TIME ${o.COMPLETUDE.FACT_TIME} · FACT_LOCATION ${o.COMPLETUDE.FACT_LOCATION} · CROP_ID ${o.COMPLETUDE.CROP_ID}` : null],
  ['CONVERSAO', (o) => o.CONVERSAO ? `sinais ${o.CONVERSAO.SINAIS} · factos futuros ${o.CONVERSAO.FACTOS_SOBRE_O_FUTURO} · crossings ${o.CONVERSAO.CROSSINGS_TENTADOS}/${o.CONVERSAO.CROSSINGS_POSSIVEIS} · achados ${o.CONVERSAO.ACHADOS} · oportunidades ${o.CONVERSAO.OPORTUNIDADES}` : null],
  ['CONSELHO_A_COLETA', (o) => o.SOURCE_COLLECTION_ADVICE ? `${o.SOURCE_COLLECTION_ADVICE.SUGGESTED_DIRECTION} — ${o.SOURCE_COLLECTION_ADVICE.REASON}` : null],
  ['CONTESTACAO', (o) => o.CONTESTACAO ? curto(o.CONTESTACAO) : null],
  ['DONO', (o) => o.DONO || null],
];

let recusados = 0;
function objeto(o) {
  const pv = o.PROVA && typeof o.PROVA === 'object' ? o.PROVA : null;
  const ev = pv && pv.SALA_CHAVE ? EV[pv.SALA_CHAVE] : null;
  if (pv && pv.SALA_CHAVE && !ev) { recusados++; return null; } // a prova nao navega: nao se desenha
  const agregada = o.PROVA_AGREGADA || null;
  return {
    especie: o.ESPECIE || NS,
    id: o.SIGNAL_ID || o.SOURCE_ID || (pv && pv.ITEM_ID) || NS,
    titulo: primeiraLinha(o.TITULO) || (ev ? primeiraLinha(ev.TITULO) : '') || o.SOURCE_ID || '',
    campos: CAMPOS.map(([k, f]) => [k, f(o)]).filter(([, v]) => v != null && v !== ''),
    prova: pv ? {
      cadeia: `${pv.SALA_CHAVE} → RAW ${pv.RAW_OBSERVATION_ID} → ${pv.DOCUMENT_ID} → sha256 ${String(pv.RAW_SHA256 || NS).slice(0, 16)}… → ${pv.INTELLIGENCE_RUN_ID}`,
      fonte: pv.SOURCE_ID || NS,
      url: ev && ev.SOURCE_URL && /^https?:/.test(ev.SOURCE_URL) ? ev.SOURCE_URL : null,
      publicado: ev ? (ev.PUBLICADO_EM || NS) : NS,
    } : {
      cadeia: agregada ? `prova agregada: ${(agregada.SALA_CHAVES || []).length} itens da Sala · ${agregada.INTELLIGENCE_RUN_ID || ''}${agregada.RENDIMENTO_SHA256 ? ' · RENDIMENTO sha256 ' + agregada.RENDIMENTO_SHA256.slice(0, 16) + '…' : ''}` : `PROVA: ${curto(o.PROVA)}`,
      fonte: o.SOURCE_ID || NS, url: null, publicado: NS,
    },
  };
}

const compartimentos = {};
for (const v of VISTAS) {
  const c = comp[v];
  const objs = (c.OBJETOS || []).map(objeto).filter(Boolean);
  const existe = (c.ENTRADA_QUE_EXISTE || []).map(objeto).filter(Boolean);
  const porEspecie = (a) => a.reduce((m, o) => (m[o.especie] = (m[o.especie] || 0) + 1, m), {});
  compartimentos[v] = {
    nome: c.NOME_IT, secao: c.SECAO_DO_DONO, pergunta: c.PERGUNTA, entradaEsperada: c.ENTRADA_ESPERADA,
    classificacao: c.CLASSIFICACAO_45 || null, diferenca: c.DIFERENCA || null, porqueVazio: c.PORQUE_VAZIO || null,
    responsavel: c.INTELLIGENCE_RESPONSAVEL || NS, contratoQueFalta: c.CONTRATO_QUE_FALTA || null, proveniencia: c.PROVENIENCIA || null,
    objetos: objs, objetosPorEspecie: porEspecie(objs), existe, existePorEspecie: porEspecie(existe),
  };
}

const cab = P.CABECALHO || {};
const pacote = {
  contrato: P.CONTRATO, marca: P.MARCA, gate: P.GATE_PARA_CLIENTE, chave: P.CHAVE_DO_POTE,
  ficheiro: path.basename(FICHEIRO), rodada: (/PARA-O-CASCO-(R\d+)/.exec(FICHEIRO) || [])[1] || NS,
  sha256: crypto.createHash('sha256').update(BYTES).digest('hex'),
  run: cab.INTELLIGENCE_RUN_ID, ruleset: cab.RULESET, biblia: cab.BIBLIA,
  motor: cab.SOURCE_HEAD ? `${String(cab.SOURCE_HEAD.MOTOR || '').slice(0, 8)} (${cab.SOURCE_HEAD.MOTOR_RAMO || NS})` : NS,
  ponte: cab.SOURCE_HEAD ? String(cab.SOURCE_HEAD.PONTE || '').slice(0, 8) : NS,
  corte: cab.CORTE ? cab.CORTE.COPIA_DA_SALA_EM : NS,
  soLeitura: cab.CORTE ? cab.CORTE.TRANSACTION_READ_ONLY : NS,
  salaLinhas: cab.CORTE && cab.CORTE.IMPRESSOES && cab.CORTE.IMPRESSOES.sala_de_espera ? cab.CORTE.IMPRESSOES.sala_de_espera.LINHAS : NS,
  estadoAnalitico: P.ESTADO_ANALITICO, conferencia: P.CONFERENCIA_DO_POTE,
  evidencia: Object.keys(EV).length, recusados, gerado: new Date().toISOString(), compartimentos,
};
const js = '/* GERADO por italia-portale/audit/casco/pote-casco.mjs a partir do POTE da Intelligence.\n'
  + '   EXPERIMENTAL · NAO_PARA_CLIENTE · traz trechos da Sala: fora do Git e do deploy (so com ?pote=local). */\n'
  + 'window.SINTONIA_POTE = ' + JSON.stringify(pacote) + ';\n';
fs.writeFileSync(path.join(CLIENTE, 'italy-pote.local.js'), js);
if (COPIA) fs.writeFileSync(COPIA, js);
console.log(JSON.stringify({
  ficheiro: FICHEIRO, sha256: pacote.sha256, chave: pacote.chave, rodada: pacote.rodada, recusados,
  porVista: Object.fromEntries(VISTAS.map((v) => [v, { objetos: compartimentos[v].objetos.length, existe: compartimentos[v].existe.length, classificacao: compartimentos[v].classificacao }])),
}, null, 1));
