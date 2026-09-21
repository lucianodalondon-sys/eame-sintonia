// PILOTO DE COLETA RECORRENTE — ITALIA V1
//
// Prova se o SINTONIA consegue voltar amanha, reconhecer o que ja viu, capturar so o novo,
// preservar versoes e perceber quebra SEM transformar ausencia ou falha em dado.
//
// LEIS QUE ESTE COLETOR OBEDECE (cada uma com guarda em italy_contract_test.mjs):
//   CAPTURE            != DOCUMENT              uma execucao pode ver o mesmo doc 10x
//   DOCUMENT_ID        != BYTE_ID               identidade semantica != SHA256
//   SAME_URL           != SAME_DOCUMENT         URL fixa pode carregar versoes diferentes
//   SAME_HASH          != DEGRADED              receber o mesmo doc e o esperado
//   NO_CHANGE          != FAILURE
//   NEW_HASH           != NEW_SEMANTIC_FACT     mudou byte nao quer dizer fato novo
//   MOVING_WINDOW      != NEW_DATASET_EVERY_DAY janela que anda nao e dataset novo
//   FIRST_RUN          =  BASELINE              a primeira execucao nao pode dizer "novo desde ontem"
//   SOURCE_HEALTH      != SOURCE_VERDICT
//   PARSER_FAILURE MUST NOT DESTROY CAPTURED_RAW
//
// Uso:
//   node coleta/italy_pilot_collect.mjs --run-id=<RUN_ID> --fonte=<ID> [--fonte=<ID>...]
//                                             executa uma rodada real
//   node coleta/italy_pilot_collect.mjs --negativos         roda os controles negativos
//
// ⚠️ `--dry` ESTAVA DOCUMENTADO E NUNCA EXISTIU: `process.argv` so alimentava a
// `nota`, e a flag virava texto do recibo. A linha foi apagada em vez de ser
// implementada — prometer modo seco no cabecalho e nao o ter e pior do que nao
// o ter. Para correr sem rede, injecta-se `forcarBuf`, que e o mecanismo que
// esta casa ja usa.

import { execFileSync, execFile } from "node:child_process";
import { promisify } from "node:util";
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync, appendFileSync, rmSync } from "node:fs";
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
// ⚠️ `./italy_contracts.mjs` NAO EXISTE AQUI desde a mudanca para gavetas: os
// contratos moraram sempre em `regras/`. O Python ganhou `_gavetas.py` para
// resolver os nomes curtos; o lado Node ficou com os imports da pasta unica, e
// por isso este coletor NAO CARREGAVA — nao e sintaxe, e o caminho.
import { CONTRACTS } from "../regras/italy_contracts.mjs";
// O motor declarativo de rota. Ele responde «que enderecos buscar?» a partir
// do bloco `ACQUISITION` do contrato — e NAO le nenhum campo em prosa.
import { alvosDoContrato, identidadeDoContrato, CONTRATO_MOTOR_VERSAO } from "../regras/motor_de_rota.mjs";
// A procedencia do contrato tem dono, e NAO e este ficheiro. Ate agora o
// coletor DIGITAVA a sua propria versao de contrato — medido: 41 corridas
// carimbadas "v1" sobre 12 GIT_HEAD, enquanto o contrato mudava em 6 commits.
//
//     QUEM ESCREVE A PROPRIA VERSAO NAO A DECLARA — AFIRMA-A.
import {
  SOURCE_CONTRACT_VERSION, hashDoContrato, hashDaConfiguracao,
} from "../regras/procedencia_do_contrato.mjs";

// ── O REGISTRY DE ADAPTERS ─────────────────────────────────────────────────
// Nasceu vazio, e ficou vazio ate ao cutover dos sete `case`. Ao migrar
// `IT-T3-008` mediu-se UM comportamento que o vocabulario finito nao
// descreve sem inventar providers de relogio: a sondagem da rota previsivel
// para tras a partir de hoje. Esse adapter vive em
// `coleta/adaptadores_de_aquisicao.mjs`, le os parametros do BLOCO do
// contrato, e o contrato NOMEIA-O — o despachador continua sem conhecer
// SOURCE_ID nenhum.
//
//     UM REGISTRY COM UM NOME EM USO DIZ «UMA FONTE PRECISOU, E ESTA ESCRITO».
//     UM REGISTRY CHEIO DE NOMES POR USAR DIZ «ALGUEM ADIVINHOU».
import { ADAPTERS } from "./adaptadores_de_aquisicao.mjs";
// O retrato do HTML (AQUISICAO-DETALHE-V1): identidade de TEXTO ao lado da de
// bytes, e o gate CAPA != MATERIA para contratos que declaram itens de detalhe.
import { retratoDoHtml, gateCapaNaoEMateria } from "./retrato_html.mjs";

const run = promisify(execFile);
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36";
const RAIZ = process.env.ITALY_OPS_ROOT || ".";
const LEDGER_DIR = `${RAIZ}/data/collection-ledger/italy`;
const STORE = `${RAIZ}/data/collection-store/italy`;
const COLLECTOR_VERSION = "pilot-v1";

// ── O UNICO CONCEITO QUE ESTE CORTE SABE RESOLVER ──────────────────────────
// `RESOLVED_STRUCTURED_TARGET` responde a UMA pergunta, e nao a outra parecida:
//
//     o que esta materializacao PRODUZIU   <- e esta
//     o que esta fonte PODE produzir       <- e a permissao, e vive no contrato
//
// A permissao (`ALLOWED_STRUCTURED_TARGETS`) ainda nao esta instalada em lado
// nenhum. Isso NAO autoriza este coletor a manter uma segunda lista sua: uma
// constante e o nome do que ele acabou de fazer; uma lista seria uma autoridade
// paralela, e a casa ja mediu o que custa ter duas.
const SOURCE_DOCUMENT = "SOURCE_DOCUMENT";

export const PILOT_SOURCES = ["IT-T3-005", "IT-T2-002", "IT-T2-004", "IT-T3-002", "IT-T3-010", "IT-T3-008", "IT-T4-001"];

// ── A CAPACIDADE, LIDA DO CONTRATO ─────────────────────────────────────────
// `PILOT_SOURCES` e HISTORIA: as sete que o piloto percorreu por `case`, e
// fica escrita porque o ledger e as guardas contam com ela. A capacidade de
// HOJE nao se digita — le-se do contrato: sabe-se percorrer quem declara
// `ACQUISITION`. Foi a falta disto que fez a CLI recusar `IT-T3-011` como
// FONTE_DESCONHECIDA com contrato executavel escrito e site a responder.
//
//     CAPACIDADE DIGITADA E CAPACIDADE DE ONTEM.
export const FONTES_PERCORRIVEIS = Object.freeze(
  Object.keys(CONTRACTS).filter((sid) => CONTRACTS[sid] && CONTRACTS[sid].ACQUISITION));

const sha = b => createHash("sha256").update(b).digest("hex");
const agora = () => new Date().toISOString();

function assinatura(buf) {
  // BOM UTF-8 antes do `<` e HTML na mesma: medido nas fontes onboarded.
  if (buf.length >= 3 && buf[0] === 0xEF && buf[1] === 0xBB && buf[2] === 0xBF) buf = buf.subarray(3);
  const h = buf.subarray(0, 8).toString("latin1");
  if (h.startsWith("%PDF")) return "PDF";
  if (h.startsWith("PK")) return "ZIP";
  const t = buf.subarray(0, 400).toString("latin1").trimStart();
  if (t.startsWith("<")) return "HTML";
  return "TEXTO";
}

// ---------- LEDGER append-only ----------
function ledgerPath() { mkdirSync(LEDGER_DIR, { recursive: true }); return `${LEDGER_DIR}/observations.ndjson`; }
export function lerLedger() {
  const p = `${LEDGER_DIR}/observations.ndjson`;
  if (!existsSync(p)) return [];
  return readFileSync(p, "utf8").split("\n").filter(Boolean).map(l => JSON.parse(l));
}
function gravar(obs) { appendFileSync(ledgerPath(), JSON.stringify(obs) + "\n"); }

// ---------- RAW imutavel ----------
// ── A PASTA DO DOCUMENTO TEM TAMANHO MAXIMO, E O DOCUMENT_ID NAO ──────────
// ⚠️ MEDIDO na Big Collection 2 (2026-09-20): com identidade pelo endereco
// (IDENTITY_KIND = URL_PATH) o DOCUMENT_ID pode ter 300 caracteres, e a pasta
// que nascia dele passava os 260 do MAX_PATH do Windows — 15 ficheiros que o
// Node escreveu e o git nao conseguia abrir («Filename too long»). A
// identidade continua inteira no ledger; so a PASTA fica limitada: 64
// caracteres do id mais 12 do sha256 do id inteiro, que e o que garante que
// dois ids longos diferentes nao caem na mesma pasta. Ids curtos (todos os
// do piloto) ficam exactamente como estavam.
//
//     O NOME DA PASTA E ENDERECO DE DISCO. O DOCUMENT_ID E IDENTIDADE.
export function pastaDoDocumento(documentId) {
  const pasta = String(documentId).replace(/[:\/\\]/g, "_");
  if (pasta.length <= 80) return pasta;
  return pasta.slice(0, 64) + "_" + sha(Buffer.from(String(documentId), "utf8")).slice(0, 12);
}
function guardarRaw(sourceId, documentId, versionId, nome, buf) {
  const dir = `${STORE}/${sourceId}/${pastaDoDocumento(documentId)}/${versionId}`;
  if (existsSync(`${dir}/${nome}`)) return { dir, criado: false };
  mkdirSync(dir, { recursive: true });
  writeFileSync(`${dir}/${nome}`, buf);
  return { dir, criado: true };
}

// ---------- baixar ----------
const TRANSITORIOS = [28, 35, 52, 56, 7];  // timeout, reset, resposta vazia, recv failure, connect
async function baixar(url, tentativas = 2) {
  for (let i = 1; i <= tentativas; i++) {
    try {
      // ⚠️ `%{content_type}` ENTRA PORQUE O TRANSPORTE JA O SABIA E NINGUEM O ESCREVIA.
      // A ESPECIE dos bytes vinha no cabecalho da resposta, era deitada fora aqui, e
      // a observacao chegava a porta sem dizer o que os bytes SAO. O resultado esta
      // medido nesta bancada a 2026-09-15, com `IT-T4-001` (um CSV de 4,59 MB):
      //
      //     raw_asset.media_type = 'NAO SEI'
      //     etapa DERIVED        = FAIL / DERIVATION_FAILED
      //
      // E o FAIL era mentira sobre o documento. `coleta/ingresso.py` ja tem a lei
      // escrita — «UMA FERRAMENTA QUE RECEBE O QUE NAO SABE ABRIR NAO FALHOU: FOI
      // CHAMADA PARA O TRABALHO ERRADO» — e ja tem o desfecho certo pronto
      // (`DERIVACAO_ESPECIE_NAO_SUPORTADA` -> `NOT_APPLICABLE`). Ele nunca corria,
      // porque a pergunta que o dispara e `MEDIA_TYPE`, e o campo chegava vazio.
      // Sem especie declarada, o CSV era entregue ao extractor de PDF.
      //
      //     ESPECIE POR DECLARAR NAO E ESPECIE DESCONHECIDA:
      //     E UMA PERGUNTA QUE O TRANSPORTE JA TINHA RESPONDIDO.
      //
      // ⚠️ E ISTO NAO E A EXTENSAO DO FICHEIRO OUTRA VEZ. E o que o SERVIDOR
      // declarou, e declaracao de terceiro nao e prova: quem guarda continua a ser
      // a validacao de BYTES contra `EXPECTED_SIGNATURE`, que corre antes de
      // qualquer parse e ja reprova um HTML servido como PDF. Esta linha nao a
      // substitui nem a afrouxa — acrescenta o que a fonte disse de si.
      const { stdout } = await run("curl", ["-sSL", "--max-time", "90", "-A", UA,
        "-H", "Accept-Language: it-IT,it;q=0.9", "-o", "-",
        "-w", "\\n__S__%{http_code}\\t%{content_type}", url],
        { maxBuffer: 128e6, encoding: "buffer" });
      const s = stdout.toString("latin1");
      const k = s.lastIndexOf("\n__S__");
      // O reboque tem DOIS campos agora. `split` com limite implicito chega: o
      // `content_type` nunca traz tabulacao, e o `http_code` e so digitos.
      const reboque = (k < 0 ? "" : s.slice(k + 6)).split("\t");
      const status = Number(reboque[0]);
      // AUSENTE CONTINUA AUSENTE: um servidor que nao declara tipo devolve vazio
      // aqui, e vazio vira `null` — nunca uma especie adivinhada pelo nome.
      const contentType = (reboque[1] || "").trim().split(";")[0].trim() || null;
      return { buf: stdout.subarray(0, k < 0 ? stdout.length : k), status,
               contentType, tentativas: i };
    } catch (e) {
      const cod = e.code ?? 0;
      const transitorio = TRANSITORIOS.includes(cod);
      // retry SO para falha de transporte. Nunca para schema, MIME, login ou WAF.
      if (!transitorio || i === tentativas) return { erro: (e.stderr?.toString() || e.message || "").slice(0, 200), status: 0, tentativas: i, retry_permitido: transitorio };
    }
  }
}

// ---------- cadencia ----------
export function estadoDeCadencia(c, ultimaObs, mudou) {
  const provada = /provado/i.test(String(c.OBSERVED_FREQUENCY));
  if (mudou) return { CADENCE_STATE: "UPDATED", EXPECTED_NEXT_UPDATE: provada ? "calculavel" : "UNKNOWN" };
  if (!provada) return { CADENCE_STATE: "CADENCE_UNKNOWN", EXPECTED_NEXT_UPDATE: "UNKNOWN", nota: "sem cadencia provada esta fonte NUNCA pode ser acusada de atraso" };
  const dias = Number((String(c.OBSERVED_FREQUENCY).match(/^(\d+)D/) || [])[1]);
  if (!dias || !ultimaObs?.SOURCE_DATE_ISO) return { CADENCE_STATE: "EXPECTED_NO_CHANGE", EXPECTED_NEXT_UPDATE: "UNKNOWN" };
  const prox = new Date(Date.parse(ultimaObs.SOURCE_DATE_ISO) + dias * 864e5);
  const atrasado = Date.now() > prox.getTime() + 864e5;   // 1 dia de folga
  return { CADENCE_STATE: atrasado ? "OVERDUE_UPDATE" : "EXPECTED_NO_CHANGE", EXPECTED_NEXT_UPDATE: prox.toISOString().slice(0, 10) };
}

// ---------- alvos por fonte ----------
// Cada alvo: { url, nome, VARS?, descoberta_degradada? }
//
// ── O CONTRATO MANDA, E NÃO HÁ MAIS `switch` ─────────────────────────────
// ⚠️ MEDIDO: esta função tinha SETE `case` por SOURCE_ID, e uma fonte sem
// `case` recebia «fonte sem alvo definido no piloto» — mesmo com contrato
// completo e site a responder HTTP 200. Foi o que aconteceu a `IT-T3-011`
// na Big Collection.
//
//     SOURCE_ID NÃO É DESPACHANTE. O CONTRATO É.
//
// Os sete `case` foram migrados um a um para `ACQUISITION` no contrato, com
// prova de equivalência (`regras/cutover_equivalencia_test.mjs`) contra a
// cópia congelada do código antigo (`provas/fixtures/legado_italy_pilot_380bf090.mjs`).
// O `switch` saiu por ficar vazio, não por alguém o apagar com pressa.
// LEGACY_DISCOVERY_CASES = 0.
//
// `subconjunto` é a única escolha de quem corre: um nome que o contrato pode
// declarar em `SUBCONJUNTOS` (o ARPAV declara PILOTO = 4 zonas). Fontes que
// não o declaram ignoram-no. O despachador não sabe o que é uma zona.
async function alvosDe(sourceId, { subconjunto = null } = {}) {
  const c = CONTRACTS[sourceId];
  if (!c) return { erro: "fonte sem contrato" };
  if (!c.ACQUISITION) {
    // Contrato em prosa não corre. Diz-se com este nome para que o ledger
    // distinga «a fonte não respondeu» de «ninguém escreveu como perguntar».
    return { erro: "CONTRACT_NOT_EXECUTABLE — o contrato nao declara ACQUISITION" };
  }
  return await alvosDoContrato(sourceId, c, { buscar: baixar, adapters: ADAPTERS, subconjunto });
}

// ---------- identidade semantica ----------
// ── A IDENTIDADE É DECLARATIVA, E NÃO HÁ MAIS `switch` ───────────────────
// ⚠️ MEDIDO: esta funcao tinha SETE ramos por SOURCE_ID. Quatro deles liam
// o CONTEUDO do documento (a data no corpo do HTML, o /CreationDate do PDF,
// o cabecalho lido por pdftotext). O motor ganhou `CONTENT_CAPTURE` para os
// servir — UMA capacidade, e nao quatro — e os leitores de texto sao
// injectados daqui: o motor nao abre ficheiros nem chama programas.
//
// `DOCUMENT_ID_RULE` continua em prosa, para gente, e NAO e lido aqui:
//     DOCUMENT_ID_RULE_TEXT != IDENTITY_EXECUTABLE_SPEC.
// LEGACY_IDENTITY_CASES = 0.
//
// pdftotext 4.06 NAO aceita stdin. Grava temporario, le, apaga. E o MESMO
// extractor de sempre — nao ha um segundo PDF→texto nesta casa.
function textoDoPdf(buf) {
  try {
    const tmp = `${STORE}/.tmp_${sha(buf).slice(0, 10)}.pdf`;
    mkdirSync(STORE, { recursive: true });
    writeFileSync(tmp, buf);
    const out = execFileSync("pdftotext", ["-layout", "-enc", "UTF-8", tmp, "-"], { maxBuffer: 64e6, encoding: "utf8" });
    rmSync(tmp, { force: true });
    return out;
  } catch { return ""; }
}
function identidade(sourceId, alvo, buf) {
  const c = CONTRACTS[sourceId];
  if (!c || !c.IDENTITY) return { DOCUMENT_ID: null };
  return identidadeDoContrato(sourceId, c, alvo, { leitores: {
    RAW_LATIN1: () => buf.toString("latin1"),
    RAW_UTF8: () => buf.toString("utf8"),
    PDF_TEXT: () => textoDoPdf(buf),
  } });
}

// ---------- normalizacao (so SIAS neste piloto) ----------
export function normalizarSias(buf) {
  const h = buf.toString("latin1").replace(/&nbsp;/g, " ");
  const txt = h.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<[^>]+>/g, "\n").replace(/\r/g, "");
  const linhas = txt.split("\n").map(s => s.trim()).filter(Boolean);
  const w = h.match(/dal\s*(\d{2}\/\d{2}\/\d{4})\s*al\s*(\d{2}\/\d{2}\/\d{4})/);
  if (!w) return { erro: "sem janela declarada" };
  const ini = new Date(w[1].split("/").reverse().join("-"));
  const fim = new Date(w[2].split("/").reverse().join("-"));
  const dias = [];
  for (let d = new Date(ini); d <= fim; d.setUTCDate(d.getUTCDate() + 1)) dias.push(d.toISOString().slice(0, 10));
  const obs = [];
  for (let i = 0; i < linhas.length; i++) {
    const nome = linhas[i];
    if (!/^[A-ZÀ-Ù][A-Za-zÀ-ù'. -]{3,40}$/.test(nome)) continue;
    const seq = [];
    for (let j = i + 1; j < linhas.length && seq.length < dias.length; j++) {
      if (/^(\d+([.,]\d+)?|--)$/.test(linhas[j])) seq.push(linhas[j]); else break;
    }
    if (seq.length !== dias.length) continue;
    dias.forEach((dia, k) => obs.push({
      STATION: nome, DATE: dia, VARIABLE: "PRECIPITAZIONE_GIORNALIERA",
      VALUE: seq[k] === "--" ? null : Number(seq[k].replace(",", ".")), UNIT: "mm",
      OBSERVATION_KEY: `${nome}|${dia}|PRECIPITAZIONE_GIORNALIERA`
    }));
    i += seq.length;
  }
  return { WINDOW_START: dias[0], WINDOW_END: dias.at(-1), observacoes: obs };
}

// ---------- execucao ----------
// ⚠️ `runId` E OBRIGATORIO, E ISSO E A CORRECCAO DO B1.
// Ate aqui este ficheiro cunhava o proprio `PILOT_RUN_...`. Uma corrida cunhada
// pelo executor existe ANTES de quem coordena saber dela — e a partir dai duas
// camadas sao donas da mesma corrida. A lei ja estava escrita no comentario de
// `collection_run`: «PROVENIENCIA E PROSPECTIVA: nao se preenche elo de
// execucao passada.»
//
//     ONE RUN = ONE RUN_ID.  Quem coordena cunha; quem colhe recebe.
//
// Sem `runId` isto REBENTA. Nao ha valor por omissao, e nao se cunha outro:
// cunhar em silencio seria exactamente o defeito que o B1 veio fechar.
export async function executarRodada({ runId = null, nota = "", forcarBuf = null, pularParse = false, apenas = null, arpavZonas = null } = {}) {
  if (!runId || typeof runId !== "string" || !runId.trim()) {
    throw new Error("RUN_ID_AUSENTE: executarRodada() exige runId de quem coordena. "
                    + "Este coletor NAO cunha corrida.");
  }
  // `arpavZonas` fica na assinatura por compatibilidade com o corredor
  // recorrente. O que ele escolhe e um SUBCONJUNTO declarado no contrato:
  // sem "TODAS", corre-se o subconjunto `PILOTO` de quem o declarar (o ARPAV
  // declara 4 zonas); com "TODAS", corre-se o provider inteiro. Fontes sem
  // SUBCONJUNTOS ignoram a escolha. Nada aqui sabe o que e uma zona.
  const subconjunto = arpavZonas === "TODAS" ? null : "PILOTO";
  // ── NAO HA CONJUNTO POR OMISSAO — BG-06 ────────────────────────────────
  // `apenas ?? PILOT_SOURCES` fazia uma corrida sem fontes nomeadas colher as
  // SETE — e a setima, IT-T3-005, tem ZERO mencoes no Atlas: e candidata
  // (status NEW, verdict NAO SEI). O Atlas e o AGENTS.md ja diziam a lei
  // («o que entra pela porta e candidata, nunca fonte»); o que faltava era
  // este ficheiro obedece-la: a lista do que o coletor SABE percorrer nao e
  // a lista do que uma corrida DEVE colher.
  //
  //     O PADRAO DE UM COLETOR E UMA DECISAO QUE NINGUEM TOMOU DE NOVO.
  //     QUEM COLHE NOMEIA AS FONTES, UMA A UMA. SEM NOME, NAO HA COLHEITA.
  //
  // `PILOT_SOURCES` continua a existir e continua com as sete: e a
  // CAPACIDADE declarada (quem este coletor sabe percorrer), usada para
  // recusar FONTE_DESCONHECIDA. Capacidade nao e aprovacao — HISTORY
  // EXISTS != SOURCE APPROVED — e apagar IT-T3-005 daqui apagaria a verdade
  // de que o corredor recorrente a percorre por declaracao explicita de
  // perfil (candidatas/italy_profiles.mjs), que e outra decisao, de outra
  // missao.
  if (!Array.isArray(apenas) || apenas.length === 0) {
    throw new Error("FONTES_AUSENTES: executarRodada() exige a lista explicita "
                    + "de fontes (`apenas`). Este coletor nao tem conjunto por "
                    + "omissao — sem nome, colheria a candidata IT-T3-005.");
  }
  const FONTES = apenas;
  const anterior = lerLedger();
  const primeira = anterior.length === 0;
  const RUN_ID = runId;
  const STARTED_AT = agora();
  // ⚠️ BYTES INJECTADOS NAO TEM EGRESSO. Com `forcarBuf` nao ha ida a fonte, e
  // medir o IP desta maquina registaria um endereco por onde nada passou —
  // numero com cara de medida. NAO_SE_APLICA e a resposta certa, e e diferente
  // de NAO SEI: aqui a pergunta e que nao faz sentido.
  let egress = forcarBuf ? "NAO_SE_APLICA" : "NAO SEI";
  if (!forcarBuf) {
    try { egress = JSON.parse((await run("curl", ["-s", "--max-time", "15", "https://ipinfo.io/json"], { encoding: "utf8" })).stdout); } catch { }
  }
  const GIT_HEAD = (() => { try { return execFileSync("git", ["rev-parse", "HEAD"], { encoding: "utf8" }).trim(); } catch { return "NAO SEI"; } })();

  // MARKUP_ONLY_REOBSERVATIONS: bytes mudaram, texto visivel nao — versao nova
  // por ruido de markup. LISTING_AS_CONTENT: o contrato declarava itens de
  // detalhe e o alvo era uma capa. Os dois sao o WASTEFUL_REOBSERVATION e o
  // gate CAPA != MATERIA da AQUISICAO-DETALHE-V1, contados por corrida.
  const cont = { SOURCES_ATTEMPTED: 0, HEALTHY: 0, DEGRADED: 0, FAILED: 0, UNKNOWN: 0, NEW_DOCUMENTS: 0, CHANGED_IN_PLACE: 0, SEEN_AGAIN: 0, SEMANTIC_ID_CHANGED_SAME_BYTES: 0, RAW_OBJECTS_CREATED: 0, NORMALIZED_OBSERVATIONS_NEW: 0, MARKUP_ONLY_REOBSERVATIONS: 0, LISTING_AS_CONTENT: 0 };
  const detalhes = [];

  for (const sourceId of FONTES) {
    cont.SOURCES_ATTEMPTED++;
    const c = CONTRACTS[sourceId];
    const alvos = await alvosDe(sourceId, { subconjunto });
    if (alvos?.erro) {
      cont.FAILED++;
      const obs = { RUN_ID, SOURCE_ID: sourceId, DOCUMENT_ID: null, HEALTH_STATE: "FAILED", OBSERVATION_RESULT: "DISCOVERY_FAILED", motivo: alvos.erro, CAPTURED_AT: agora(), COLLECTION_RUN_STARTED_AT: STARTED_AT };
      gravar(obs); detalhes.push(obs); continue;
    }

    let saudeFonte = "HEALTHY";
    for (const alvo of alvos) {
      const r = forcarBuf ? { buf: forcarBuf(sourceId, alvo), status: 200, tentativas: 1 } : await baixar(alvo.url);
      const CAPTURED_AT = agora();

      if (r.erro || r.status !== 200 || !r.buf?.length) {
        saudeFonte = "FAILED";
        const obs = { RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url, DOCUMENT_ID: null, HEALTH_STATE: "FAILED", OBSERVATION_RESULT: "TRANSPORT_OR_EMPTY", motivo: r.erro || `status ${r.status} / ${r.buf?.length ?? 0} bytes`, retries: r.tentativas, CAPTURED_AT, COLLECTION_RUN_STARTED_AT: STARTED_AT };
        gravar(obs); detalhes.push(obs); continue;
      }

      // ---- 1) validacao de bytes ANTES de qualquer parse ----
      const sig = assinatura(r.buf);
      const esperado = c.EXPECTED_SIGNATURE === "%PDF" ? "PDF" : c.EXPECTED_SIGNATURE === "<" ? "HTML" : c.EXPECTED_SIGNATURE === "PK" ? "ZIP" : null;
      const csvOk = !esperado ? String(r.buf.subarray(0, 400)).includes(String(c.EXPECTED_SIGNATURE)) : true;
      if ((esperado && sig !== esperado) || !csvOk) {
        saudeFonte = "FAILED";
        const obs = { RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url, DOCUMENT_ID: null, RAW_SHA256: sha(r.buf), HEALTH_STATE: "FAILED", OBSERVATION_RESULT: "BYTE_VALIDATION_FAILED", motivo: `esperava ${esperado || c.EXPECTED_SIGNATURE}, chegou ${sig} — HTTP 200 nao salva isto`, CAPTURED_AT, COLLECTION_RUN_STARTED_AT: STARTED_AT };
        gravar(obs); detalhes.push(obs); continue;
      }

      const RAW_SHA256 = sha(r.buf);
      const ident = identidade(sourceId, alvo, r.buf);
      if (!ident.DOCUMENT_ID) {
        saudeFonte = "FAILED";
        const obs = { RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url, DOCUMENT_ID: null, RAW_SHA256, HEALTH_STATE: "FAILED", OBSERVATION_RESULT: "IDENTITY_FAILED", motivo: "nao foi possivel montar DOCUMENT_ID a partir do documento", CAPTURED_AT, COLLECTION_RUN_STARTED_AT: STARTED_AT };
        gravar(obs); detalhes.push(obs); continue;
      }

      // ---- 2) os quatro casos de versionamento ----
      const mesmoDoc = anterior.filter(o => o.SOURCE_ID === sourceId && o.DOCUMENT_ID === ident.DOCUMENT_ID);
      const mesmoSha = anterior.filter(o => o.RAW_SHA256 === RAW_SHA256 && o.SOURCE_ID === sourceId);
      let OBSERVATION_RESULT, DOCUMENT_VERSION_ID;

      if (mesmoDoc.some(o => o.RAW_SHA256 === RAW_SHA256)) {
        OBSERVATION_RESULT = "SEEN_AGAIN";                       // CASO A
        DOCUMENT_VERSION_ID = mesmoDoc.find(o => o.RAW_SHA256 === RAW_SHA256).DOCUMENT_VERSION_ID;
        cont.SEEN_AGAIN++;
      } else if (mesmoDoc.length) {
        OBSERVATION_RESULT = "DOCUMENT_CHANGED_IN_PLACE";        // CASO B
        DOCUMENT_VERSION_ID = `v${mesmoDoc.length + 1}_${RAW_SHA256.slice(0, 12)}`;
        cont.CHANGED_IN_PLACE++;
      } else if (mesmoSha.length) {
        OBSERVATION_RESULT = "SEMANTIC_ID_CHANGED_SAME_BYTES";   // CASO D
        DOCUMENT_VERSION_ID = `v1_${RAW_SHA256.slice(0, 12)}`;
        cont.SEMANTIC_ID_CHANGED_SAME_BYTES++;
      } else {
        OBSERVATION_RESULT = primeira ? "BASELINE_DOCUMENT" : "NEW_DOCUMENT"; // CASO C
        DOCUMENT_VERSION_ID = `v1_${RAW_SHA256.slice(0, 12)}`;
        cont.NEW_DOCUMENTS++;
      }

      // ---- 3) RAW imutavel ANTES de qualquer parse ----
      // ⚠️ AQUI O `SEEN_AGAIN` SAIA SEM `RAW_PATH`, e isso confundia duas coisas:
      //
      //     NAO CRIEI O OBJECTO AGORA   !=   NAO HA BYTES EM LADO NENHUM
      //
      // Quem lia a observacao reencontrada nao tinha como chegar ao documento —
      // e a porta de entrada, sem caminho, preservaria o JSON da colheita como
      // se fosse o documento. `RAW_OBJECT_CREATED` continua a responder «criei
      // agora?»; `RAW_PATH` passa a responder «onde estao os bytes?». Sao duas
      // perguntas. `guardarRaw` ja era idempotente: se o ficheiro esta la,
      // devolve o sitio e nao escreve.
      const g = guardarRaw(sourceId, ident.DOCUMENT_ID, DOCUMENT_VERSION_ID, alvo.nome, r.buf);
      const rawCriado = g.criado, rawDir = g.dir;
      if (g.criado) cont.RAW_OBJECTS_CREATED++;

      // ---- 4) so agora o parse. Se ele explodir, o RAW ja esta salvo. ----
      let parse = null, parseErro = null;

      // ---- 3b) o retrato do HTML: texto != bytes, capa != materia ----
      // Corre DEPOIS do RAW estar guardado e ANTES do parse: se explodir,
      // os bytes ja la estao. So para HTML; PDF/CSV/ZIP ficam como estavam.
      let retrato = null, contentChange = null;
      if (sig === "HTML") {
        try { retrato = retratoDoHtml(r.buf); } catch (e) { retrato = null; }
        if (retrato && OBSERVATION_RESULT === "DOCUMENT_CHANGED_IN_PLACE") {
          // A versao anterior pode nao ter TEXT_SHA256 (escrita antes desta
          // medida): entao NAO SEI, nunca «mudou» nem «igual» por omissao.
          const antesTxt = mesmoDoc.at(-1)?.TEXT_SHA256 ?? null;
          contentChange = !antesTxt ? "UNKNOWN" : antesTxt === retrato.TEXT_SHA256 ? "MARKUP_ONLY" : "TEXT_CHANGED";
          if (contentChange === "MARKUP_ONLY") cont.MARKUP_ONLY_REOBSERVATIONS++;
        }
        // O GATE: contrato que declara itens de detalhe nao guarda capa como
        // conteudo final. O RAW fica (e prova do que a rota devolveu); a
        // observacao sai DEGRADED com a razao pelo nome, nunca HEALTHY.
        const gate = gateCapaNaoEMateria(c, retrato);
        if (gate) { parseErro = gate; cont.LISTING_AS_CONTENT++; }
      }
      if (!pularParse) {
        try {
          if (sourceId === "IT-T2-004") {
            const n = normalizarSias(r.buf);
            const chavesVistas = new Set(anterior.flatMap(o => o.OBSERVATION_KEYS || []));
            const novas = (n.observacoes || []).filter(o => !chavesVistas.has(o.OBSERVATION_KEY));
            cont.NORMALIZED_OBSERVATIONS_NEW += novas.length;
            parse = { WINDOW_START: n.WINDOW_START, WINDOW_END: n.WINDOW_END, ROWS_IN_WINDOW: n.observacoes?.length ?? 0, UNIQUE_STATION_DATE_VARIABLE: new Set((n.observacoes || []).map(o => o.OBSERVATION_KEY)).size, NEW_NORMALIZED_OBSERVATIONS: novas.length };
            parse._keys = (n.observacoes || []).map(o => o.OBSERVATION_KEY);
          }
          if (sourceId === "IT-T3-005") {
            const pts = [...r.buf.toString("utf8").matchAll(/reports_points" id="(\d+)"[\s\S]*?Latitudine:\s*([-\d.]+),\s*Longitudine:\s*([-\d.]+)[\s\S]*?Infestazione attiva:\s*([^<]*?)\s*</g)]
              .map(m => ({ POINT_ID: m[1], LAT: +m[2], LON: +m[3], INFESTATION: m[4] }));
            parse = { MONITORING_POINTS: pts.length, COM_COORDENADA: pts.filter(p => Number.isFinite(p.LAT)).length, _pontos: pts };
            if (pts.length < (c.MIN_PONTOS || 0)) { saudeFonte = "FAILED"; parseErro = `${pts.length} pontos, minimo ${c.MIN_PONTOS} — EMPTY != ZERO`; }
          }
        } catch (e) { parseErro = String(e.message).slice(0, 160); }
      }

      const cad = estadoDeCadencia(c, mesmoDoc.at(-1) || anterior.filter(o => o.SOURCE_ID === sourceId).at(-1), OBSERVATION_RESULT !== "SEEN_AGAIN");

      const obs = {
        RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url,
        DOCUMENT_ID: ident.DOCUMENT_ID, DOCUMENT_VERSION_ID, RAW_SHA256,
        // ── O QUE ESTA MATERIALIZACAO PRODUZIU ─────────────────────────────
        // A razao do carimbo e uma so: acabou de nascer uma IDENTIDADE
        // DOCUMENTAL. Nao e o PDF, nem o MIME, nem a extensao, nem o nome da
        // fonte, nem o nome deste ficheiro — nenhum desses prova que houve
        // documento. `DOCUMENT_ID` e `DOCUMENT_VERSION_ID` com valor real
        // provam, porque sao o que a casa acabou de construir.
        //
        // E por isso ele e CONDICIONAL e nao constante. As quatro observacoes
        // de falha ali acima nao passam por aqui, e nenhuma delas leva o campo:
        // sem identidade, o alvo nao foi resolvido, e a resposta certa e a
        // AUSENCIA do campo. Escrever `null`, `UNKNOWN` ou `NAO SEI` poria uma
        // confissao num sitio onde so cabe um CONCEPT_ID, e quem lesse depois
        // teria de adivinhar se aquilo era um conceito ou uma desculpa.
        //
        //     ALVO AUSENTE != ALVO DESCONHECIDO != ALVO NENHUM.
        //
        // ⚠️ E ele NAO diz que esta observacao so produz isto. O mesmo boletim
        // pode vir a dar 1045 linhas (IT-T2-004) ou 139 pontos (IT-T3-005), e
        // cada uma dessas unidades tera o alvo dela. Aqui diz-se apenas que a
        // materializacao DOCUMENTAL deste corte e um SOURCE_DOCUMENT.
        ...(ident.DOCUMENT_ID && DOCUMENT_VERSION_ID
            ? { RESOLVED_STRUCTURED_TARGET: SOURCE_DOCUMENT } : {}),
        BYTES: r.buf.length, MIME_ASSINATURA: sig,
        // ── A ESPECIE, COMO A FONTE A DECLAROU ─────────────────────────────
        // ⚠️ `MIME_ASSINATURA` E OUTRA COISA, E POR ISSO AS DUAS FICAM.
        // `MIME_ASSINATURA` e o que NOS medimos nos primeiros bytes (PDF · ZIP
        // · HTML · TEXTO) — uma familia, nao um media type. `CONTENT_TYPE` e o
        // que o SERVIDOR disse. Sao duas testemunhas, e juntar as duas num
        // campo so apagaria a unica que permite compara-las.
        //
        //     O QUE EU MEDI != O QUE ELE DISSE.
        //
        // O nome e `CONTENT_TYPE` porque e assim que `coleta/ingresso.py::
        // DO_COLETOR` o transporta e `leis/artefato.py` o le. Inventar aqui um
        // nome proprio obrigaria a uma traducao a mais, e cada traducao e um
        // sitio onde o campo se pode perder — foi o que ja aconteceu ao
        // `CAPTURED_AT`.
        //
        // Com `forcarBuf` nao houve HTTP: `contentType` vem `undefined`, o
        // campo sai `null`, e a ficha volta ao que fazia antes. Ausencia
        // honesta, e nao um tipo fabricado para uma corrida sem rede.
        CONTENT_TYPE: r.contentType ?? null,
        SOURCE_DATE: ident.SOURCE_DATE, SOURCE_DATE_ISO: ident.SOURCE_DATE_ISO,
        FACT_TIME: ident.FACT_TIME ?? "UNKNOWN",
        CAPTURED_AT, COLLECTION_RUN_STARTED_AT: STARTED_AT,
        OBSERVATION_RESULT,
        HEALTH_STATE: parseErro && saudeFonte === "FAILED" ? "FAILED" : parseErro ? "DEGRADED" : "HEALTHY",
        CADENCE_STATE: cad.CADENCE_STATE, EXPECTED_NEXT_UPDATE: cad.EXPECTED_NEXT_UPDATE,
        DECLARED_FREQUENCY: c.DECLARED_FREQUENCY, OBSERVED_FREQUENCY: c.OBSERVED_FREQUENCY,
        RAW_OBJECT_CREATED: rawCriado, RAW_PATH: rawDir ? `${rawDir}/${alvo.nome}` : null,
        RAW_PRESERVED_BEFORE_PARSE: true,
        DISCOVERY_DEGRADED: alvo.descoberta_degradada ?? null,
        PARSE_ERROR: parseErro,
        // ── O RETRATO (AQUISICAO-DETALHE-V1) — so para HTML; ausente = null ──
        // TEXT_SHA256 e identidade de CONTEUDO (texto visivel), ao lado de
        // RAW_SHA256 (bytes). CONTENT_CHANGE so existe quando o documento mudou
        // no sitio: MARKUP_ONLY (texto igual) · TEXT_CHANGED · UNKNOWN (a versao
        // anterior nao tinha retrato). CAPA_OU_MATERIA e leitura, nao veredito.
        TEXT_SHA256: retrato ? retrato.TEXT_SHA256 : null,
        HTML_KIND: retrato ? retrato.HTML_KIND : null,
        CAPA_OU_MATERIA: retrato ? retrato.CAPA_OU_MATERIA : null,
        CONTENT_CHANGE: contentChange,
        parse: parse ? Object.fromEntries(Object.entries(parse).filter(([k]) => !k.startsWith("_"))) : null,
        OBSERVATION_KEYS: parse?._keys || undefined,
        PONTOS: parse?._pontos ? parse._pontos.length : undefined
      };
      gravar(obs); detalhes.push(obs);
      if (obs.HEALTH_STATE === "FAILED") saudeFonte = "FAILED";
      else if (obs.HEALTH_STATE === "DEGRADED" && saudeFonte !== "FAILED") saudeFonte = "DEGRADED";
    }
    cont[saudeFonte]++;
  }

  const FINISHED_AT = agora();
  const resumo = {
    RUN_ID, STARTED_AT, FINISHED_AT,
    IS_BASELINE: primeira,
    nota_do_baseline: primeira ? "FIRST_RUN = BASELINE — esta execucao NAO pode dizer 'novo desde ontem'. Ela so estabelece o ponto de partida." : null,
    VPN_COUNTRY: egress?.country ?? (forcarBuf ? "NAO_SE_APLICA" : "NAO SEI"),
    EGRESS_IP: egress?.ip ?? (forcarBuf ? "NAO_SE_APLICA" : "NAO SEI"),
    COLLECTOR_VERSION, SOURCE_CONTRACT_VERSION, GIT_HEAD,
    // ── A PROCEDENCIA DO CONTRATO, EM QUATRO CAMPOS QUE NAO SE SUBSTITUEM ──
    // `SOURCE_CONTRACT_VERSION` diz que FORMATO o runtime entende — e vem do
    // dono do contrato, nao mais digitado aqui.
    //
    // `SOURCE_CONTRACT_HASH` diz que contrato EXECUTAVEL correu. Ele muda
    // quando um campo lido pelo runtime muda, e NAO muda quando alguem
    // corrige uma virgula num comentario:
    //
    //     UM HASH QUE MUDA COM UM COMENTARIO MEDE O FICHEIRO,
    //     NAO O CONTRATO.
    //
    // `CONFIG_HASH` diz com que CONFIGURACAO a corrida correu, e deixa de
    // fora RUN_ID e relogio de proposito: duas corridas iguais tem de dar o
    // mesmo hash, ou o campo passa a medir «quando» em vez de «com que».
    //
    // `CONTRATO_MOTOR_VERSAO` diz que MOTOR interpretou o contrato.
    //
    // Sao por fonte, e por isso vao num mapa: uma corrida pode tocar varias
    // fontes, e um hash unico da corrida esconderia qual contrato produziu
    // qual observacao.
    SOURCE_CONTRACT_HASH: Object.fromEntries(
      FONTES.map((sid) => [sid, hashDoContrato(CONTRACTS[sid])])),
    CONFIG_HASH: Object.fromEntries(
      FONTES.map((sid) => [sid, hashDaConfiguracao({
        sourceId: sid,
        contractHash: hashDoContrato(CONTRACTS[sid]),
        contractVersion: SOURCE_CONTRACT_VERSION,
        motorVersao: CONTRATO_MOTOR_VERSAO,
        mode: primeira ? "BASELINE" : "INCREMENTAL",
      })])),
    CONTRATO_MOTOR_VERSAO,
    nota, contadores: cont
  };
  mkdirSync(LEDGER_DIR, { recursive: true });
  appendFileSync(`${LEDGER_DIR}/runs.ndjson`, JSON.stringify(resumo) + "\n");
  return { resumo, detalhes };
}

// ⚠️ ESTA GUARDA NUNCA FOI VERDADE FORA DO WINDOWS, e por isso a CLI deste
// coletor NUNCA CORREU NO LINUX: em POSIX `process.argv[1]` ja comeca por `/`,
// e `file:///` + `/home/...` da `file:////home/...` — quatro barras contra as
// tres de `import.meta.url`. O ficheiro carregava, nao dizia nada, e saia com
// codigo 0: o silencio parecia sucesso.
//
//     CORRER SEM FAZER NADA E SAIR COM ZERO
//     E A FORMA MAIS CARA DE FALHAR.
//
// `pathToFileURL` e a conversao que o proprio Node exporta para isto, e vale
// nos dois sistemas.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  // A CLI tambem NAO cunha. Quem corre a mao passa a corrida a mao — e assim a
  // linha de comando conta a mesma verdade que a rota canonica.
  const args = process.argv.slice(2);
  const rid = (args.find(a => a.startsWith("--run-id=")) || "").split("=")[1];
  if (!rid) {
    console.error("uso: node coleta/italy_pilot_collect.mjs --run-id=<RUN_ID> --fonte=<ID> [--fonte=<ID>...] [nota...]");
    console.error("     este coletor NAO cunha corrida. O RUN_ID vem de quem coordena.");
    process.exit(2);
  }
  // `--fonte=` existe porque o REGISTO ja declara um filtro de fonte, e um
  // filtro declarado que nao chega ao coletor e um filtro que nao filtra.
  // Repete-se para pedir mais do que uma.
  //
  // ⚠️ E E OBRIGATORIO — BG-06. «Sem nenhum, corre o piloto inteiro» deixou
  // de ser verdade: o piloto inteiro incluia IT-T3-005, que nao esta no
  // Atlas. Sem --fonte, esta CLI recusa, como recusa RUN_ID ausente.
  const fontes = args.filter(a => a.startsWith("--fonte="))
                     .map(a => a.split("=")[1]).filter(Boolean);
  if (!fontes.length) {
    console.error("FONTES_AUSENTES: nomeie cada fonte com --fonte=<SOURCE_ID>. "
                  + "Nao ha conjunto por omissao — o padrao antigo colhia a "
                  + "candidata IT-T3-005, que nao esta no Atlas.");
    process.exit(2);
  }
  // A recusa mede a CAPACIDADE DE HOJE (quem tem `ACQUISITION` no contrato),
  // e nao a lista historica do piloto. Continua a recusar antes da rede.
  const desconhecidas = fontes.filter(f => !FONTES_PERCORRIVEIS.includes(f));
  if (desconhecidas.length) {
    console.error(`FONTE_DESCONHECIDA: ${desconhecidas.join(", ")} — este coletor `
                  + `percorre ${FONTES_PERCORRIVEIS.join(", ")}. Nao se finge que correu.`);
    process.exit(2);
  }
  const { resumo, detalhes } = await executarRodada({
    runId: rid,
    apenas: fontes,
    nota: args.filter(a => !a.startsWith("--run-id=") && !a.startsWith("--fonte=")).join(" ") });
  console.log(JSON.stringify(resumo, null, 1));
  console.log("\nSOURCE_ID     RESULTADO                        SAUDE     CADENCIA            DOCUMENT_ID");
  for (const d of detalhes) {
    console.log(`${d.SOURCE_ID.padEnd(13)} ${String(d.OBSERVATION_RESULT).padEnd(32)} ${String(d.HEALTH_STATE).padEnd(9)} ${String(d.CADENCE_STATE ?? "-").padEnd(19)} ${d.DOCUMENT_ID ?? d.motivo ?? ""}`);
  }
}
