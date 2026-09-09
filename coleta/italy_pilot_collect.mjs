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
//   node coleta/italy_pilot_collect.mjs                 executa uma rodada real
//   node coleta/italy_pilot_collect.mjs --dry           usa so o que ja esta no disco
//   node coleta/italy_pilot_collect.mjs --negativos     roda os controles negativos

import { execFileSync, execFile } from "node:child_process";
import { promisify } from "node:util";
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync, appendFileSync, rmSync } from "node:fs";
import { createHash, randomUUID } from "node:crypto";
import { CONTRACTS } from "./italy_contracts.mjs";

const run = promisify(execFile);
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36";
const RAIZ = process.env.ITALY_OPS_ROOT || ".";
const LEDGER_DIR = `${RAIZ}/data/collection-ledger/italy`;
const STORE = `${RAIZ}/data/collection-store/italy`;
const COLLECTOR_VERSION = "pilot-v1";

export const PILOT_SOURCES = ["IT-T3-005", "IT-T2-002", "IT-T2-004", "IT-T3-002", "IT-T3-010", "IT-T3-008", "IT-T4-001"];

const sha = b => createHash("sha256").update(b).digest("hex");
const agora = () => new Date().toISOString();

function assinatura(buf) {
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
function guardarRaw(sourceId, documentId, versionId, nome, buf) {
  const dir = `${STORE}/${sourceId}/${documentId.replace(/[:\/\\]/g, "_")}/${versionId}`;
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
      const { stdout } = await run("curl", ["-sSL", "--max-time", "90", "-A", UA,
        "-H", "Accept-Language: it-IT,it;q=0.9", "-o", "-", "-w", "\\n__S__%{http_code}", url],
        { maxBuffer: 128e6, encoding: "buffer" });
      const s = stdout.toString("latin1");
      const k = s.lastIndexOf("\n__S__");
      const status = Number(s.slice(k + 6));
      return { buf: stdout.subarray(0, k < 0 ? stdout.length : k), status, tentativas: i };
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
// Cada alvo: { url, nome, documentIdDe(buf) -> {DOCUMENT_ID, SOURCE_DATE, FACT_TIME} }
async function alvosDe(sourceId) {
  const c = CONTRACTS[sourceId];
  switch (sourceId) {
    case "IT-T3-005":
      return [{ url: c.CANONICAL_ENTRY_URL, nome: "monitoraggio.html" }];
    case "IT-T2-002":
      // No piloto medimos 4. Na operacao forward-only medimos as 29 publicadas.
      // As zonas 17, 18 e 19 devolvem 404 consistente: o site nao as publica. Fato da fonte.
      const zonas = globalThis.__ARPAV_TODAS
        ? Array.from({ length: 32 }, (_, i) => i + 1).filter(n => ![17, 18, 19].includes(n))
        : [1, 9, 16, 24];
      return zonas.map(n => ({ url: `https://www.arpa.veneto.it/risorse/data-agrometeo/agrometeo/32zone/agro_${String(n).padStart(2, "0")}.pdf`, nome: `agro_${String(n).padStart(2, "0")}.pdf`, zone: n }));
    case "IT-T2-004":
      return [{ url: "http://www.sias.regione.sicilia.it/NHEOWL0530_00.html", nome: "NHEOWL0530_00.html", table: "PRECIPITAZIONE_GIORNALIERA" }];
    case "IT-T3-010": {
      const idx = await baixar("http://www.apol.it");
      if (idx.erro || idx.status !== 200) return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
      const html = idx.buf.toString("latin1");
      const links = [...html.matchAll(/href="([^"]*Bollettino_Mosca[^"]*\.pdf)"/gi)].map(m => new URL(m[1], "http://www.apol.it").href);
      if (links.length === 0) return { erro: "EMPTY_LIST — o indice nao listou nenhum boletim. Isto e FAILED, nao zero documentos." };
      const atual = links[0];
      return [{ url: atual, nome: atual.split("/").pop() }];
    }
    case "IT-T3-002": {
      const idx = await baixar("https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/SA_2026.html");
      if (idx.erro || idx.status !== 200) return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
      // os href do indice sao RELATIVOS ("pdf/SA-02-09.pdf"), nao absolutos — resolver contra a pagina
      const base = "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/";
      const links = [...idx.buf.toString("latin1").matchAll(/href="([^"]*SA-\d{2}-\d{2}\.pdf)"/gi)].map(m => new URL(m[1], base).href);
      if (links.length === 0) return { erro: "EMPTY_LIST — indice sem boletins. FAILED." };
      return [{ url: links[0], nome: links[0].split("/").pop() }];
    }
    case "IT-T3-008": {
      const idx = await baixar("https://www.agrometeopuglia.it/bollettini");
      if (idx.erro || idx.status !== 200) return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
      const links = [...idx.buf.toString("latin1").matchAll(/href="([^"]*Notiziario_Agrometeorologico_N\d+_[\d-]+\.pdf)"/gi)].map(m => new URL(m[1], "https://www.agrometeopuglia.it").href);
      if (links.length === 0) {
        // ACHADO: o indice de agrometeopuglia.it e renderizado por JavaScript — o curl nao ve os links.
        // Isto NAO e lista vazia da fonte: e limite do nosso instrumento. Por isso NAO e EMPTY_LIST/FAILED.
        // Caimos para a ROTA PREVISIVEL que o contrato ja documenta, procurando a edicao corrente
        // para tras a partir de hoje. A descoberta fica marcada como degradada, e o motivo vai no ledger.
        const hoje = new Date();
        for (let volta = 0; volta < 10; volta++) {
          const d = new Date(hoje.getTime() - volta * 864e5);
          const dd = String(d.getUTCDate()).padStart(2, "0"), mm = String(d.getUTCMonth() + 1).padStart(2, "0"), aa = d.getUTCFullYear();
          // o numero da semana nao e adivinhavel: varremos os numeros plausiveis da temporada
          for (const n of [37, 36, 35]) {
            const u = `https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/${aa}/Notiziario_Agrometeorologico_N${n}_${dd}-${mm}-${aa}.pdf`;
            const t = await baixar(u, 1);
            if (!t.erro && t.status === 200 && t.buf?.length > 100000 && t.buf.subarray(0,4).toString("latin1") === "%PDF")
              return [{ url: u, nome: u.split("/").pop(), descoberta_degradada: "INDEX_REQUIRES_BROWSER — indice e JavaScript; caiu para a rota previsivel do contrato" }];
          }
        }
        return { erro: "indice exige navegador E a rota previsivel nao achou edicao nos ultimos 10 dias" };
      }
      return [{ url: links[0], nome: links[0].split("/").pop() }];
    }
    case "IT-T4-001": {
      const idx = await baixar("https://www.dati.salute.gov.it/it/dataset/fitosanitari/");
      if (idx.erro || idx.status !== 200) return { erro: `pagina inacessivel: ${idx.erro || idx.status}` };
      const m = idx.buf.toString("latin1").match(/opendata\/(PROD_FTS_6_(\d{8})\.csv)/);
      if (!m) return { erro: "EMPTY_LIST — nenhuma versao de CSV anunciada na pagina. FAILED." };
      return [{ url: `https://www.dati.salute.gov.it/sites/default/files/opendata/${m[1]}`, nome: m[1], sourceVersion: m[2] }];
    }
  }
  return { erro: "fonte sem alvo definido no piloto" };
}

// ---------- identidade semantica ----------
function identidade(sourceId, alvo, buf) {
  // pdftotext 4.06 NAO aceita stdin. Grava temporario, le, apaga.
  const t = () => {
    try {
      const tmp = `${STORE}/.tmp_${sha(buf).slice(0, 10)}.pdf`;
      mkdirSync(STORE, { recursive: true });
      writeFileSync(tmp, buf);
      const out = execFileSync("pdftotext", ["-layout", "-enc", "UTF-8", tmp, "-"], { maxBuffer: 64e6, encoding: "utf8" });
      rmSync(tmp, { force: true });
      return out;
    } catch { return ""; }
  };
  switch (sourceId) {
    case "IT-T3-005": {
      const h = buf.toString("utf8");
      const p = h.match(/Bollettino del periodo dal\s*([\d-]+)\s*al\s*([\d-]+)/);
      const br = s => s ? s.split("-").reverse().join("-") : null;
      return { DOCUMENT_ID: p ? `TERRETRURIA:${p[1]}:${p[2]}` : null, SOURCE_DATE: p ? `${p[1]} a ${p[2]}` : null, SOURCE_DATE_ISO: br(p?.[2]), FACT_TIME: "por ponto — cada ponto traz sua propria data de campionamento" };
    }
    case "IT-T2-002": {
      const s = buf.toString("latin1");
      const g = (s.match(/\/CreationDate\s*\(D:(\d{14})/) || [])[1];
      const iso = g ? `${g.slice(0, 4)}-${g.slice(4, 6)}-${g.slice(6, 8)}` : null;
      return { DOCUMENT_ID: g ? `ARPAV:Z${String(alvo.zone).padStart(2, "0")}:${g}` : null, SOURCE_DATE: iso, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o PDF nao expoe a data do fato medido, so a de geracao" };
    }
    case "IT-T2-004": {
      const h = buf.toString("latin1");
      const w = h.match(/dal\s*(\d{2}\/\d{2}\/\d{4})\s*al\s*(\d{2}\/\d{2}\/\d{4})/);
      const iso = w ? w[2].split("/").reverse().join("-") : null;
      return { DOCUMENT_ID: w ? `SIAS:${alvo.table}:WINDOW_END_${iso}` : null, SOURCE_DATE: w ? `${w[1]} a ${w[2]}` : null, SOURCE_DATE_ISO: iso, FACT_TIME: "por linha — cada celula tem sua propria data" };
    }
    case "IT-T3-002": {
      const m = alvo.nome.match(/^([A-Z]{2})-(\d{2})-(\d{2})\.pdf$/);
      const iso = m ? `2026-${m[3]}-${m[2]}` : null;
      return { DOCUMENT_ID: m ? `CAMPANIA:${m[1]}:${m[2]}-${m[3]}-2026` : null, SOURCE_DATE: m ? `${m[2]}/${m[3]}/2026` : null, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o boletim nao data a observacao de campo" };
    }
    case "IT-T3-010": {
      const txt = t();
      const p = txt.match(/MOSCA DELLE OLIVE\s+(\d{2}\/\d{2}\/\d{4})\s*-\s*(\d{2}\/\d{2}\/\d{4})/);
      const n = alvo.nome.match(/_n_(\d+)_/);
      const compr = (txt.match(/COMPRENSORIO\s*-?\s*([A-Z]{2})\s*-\s*([A-Z ]+)/) || []);
      const iso = p ? p[1].split("/").reverse().join("-") : null;
      return { DOCUMENT_ID: n && p ? `APOL:${p[1].slice(-4)}:N${n[1]}:${(compr[1] || "?") + "-" + (compr[2] || "?").trim()}` : null, SOURCE_DATE: p ? `${p[1]} a ${p[2]}` : null, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o periodo e de validade, nao de observacao" };
    }
    case "IT-T3-008": {
      const n = alvo.nome.match(/_N(\d+)_([\d-]+)\.pdf/);
      const iso = n ? n[2].split("-").reverse().join("-") : null;
      return { DOCUMENT_ID: n ? `ARIF:SETTIMANALE:${iso?.slice(0, 4)}:N${n[1]}` : null, SOURCE_DATE: n ? n[2] : null, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN" };
    }
    case "IT-T4-001": {
      const v = alvo.sourceVersion;
      const iso = v ? `${v.slice(0, 4)}-${v.slice(4, 6)}-${v.slice(6, 8)}` : null;
      return { DOCUMENT_ID: v ? `MINSALUTE:FTS6:${v}` : null, SOURCE_DATE: iso, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o CSV traz datas de registro por linha, nao uma data de fato do arquivo" };
    }
  }
  return { DOCUMENT_ID: null };
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
export async function executarRodada({ nota = "", forcarBuf = null, pularParse = false, apenas = null, arpavZonas = null } = {}) {
  globalThis.__ARPAV_TODAS = arpavZonas === "TODAS";
  const FONTES = apenas ?? PILOT_SOURCES;
  const anterior = lerLedger();
  const primeira = anterior.length === 0;
  const RUN_ID = `PILOT_RUN_${new Date().toISOString().replace(/[-:T.]/g, "").slice(0, 14)}_${randomUUID().slice(0, 6)}`;
  const STARTED_AT = agora();
  let egress = "NAO SEI";
  try { egress = JSON.parse((await run("curl", ["-s", "--max-time", "15", "https://ipinfo.io/json"], { encoding: "utf8" })).stdout); } catch { }
  const GIT_HEAD = (() => { try { return execFileSync("git", ["rev-parse", "HEAD"], { encoding: "utf8" }).trim(); } catch { return "NAO SEI"; } })();

  const cont = { SOURCES_ATTEMPTED: 0, HEALTHY: 0, DEGRADED: 0, FAILED: 0, UNKNOWN: 0, NEW_DOCUMENTS: 0, CHANGED_IN_PLACE: 0, SEEN_AGAIN: 0, SEMANTIC_ID_CHANGED_SAME_BYTES: 0, RAW_OBJECTS_CREATED: 0, NORMALIZED_OBSERVATIONS_NEW: 0 };
  const detalhes = [];

  for (const sourceId of FONTES) {
    cont.SOURCES_ATTEMPTED++;
    const c = CONTRACTS[sourceId];
    const alvos = await alvosDe(sourceId);
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
      let rawCriado = false, rawDir = null;
      if (OBSERVATION_RESULT !== "SEEN_AGAIN") {
        const g = guardarRaw(sourceId, ident.DOCUMENT_ID, DOCUMENT_VERSION_ID, alvo.nome, r.buf);
        rawCriado = g.criado; rawDir = g.dir;
        if (g.criado) cont.RAW_OBJECTS_CREATED++;
      }

      // ---- 4) so agora o parse. Se ele explodir, o RAW ja esta salvo. ----
      let parse = null, parseErro = null;
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
        BYTES: r.buf.length, MIME_ASSINATURA: sig,
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
    VPN_COUNTRY: egress?.country ?? "NAO SEI", EGRESS_IP: egress?.ip ?? "NAO SEI",
    COLLECTOR_VERSION, SOURCE_CONTRACT_VERSION: "italy-contracts-v1", GIT_HEAD,
    nota, contadores: cont
  };
  mkdirSync(LEDGER_DIR, { recursive: true });
  appendFileSync(`${LEDGER_DIR}/runs.ndjson`, JSON.stringify(resumo) + "\n");
  return { resumo, detalhes };
}

if (process.argv[1] && import.meta.url === `file:///${process.argv[1].replace(/\\/g, "/")}`) {
  const { resumo, detalhes } = await executarRodada({ nota: process.argv.slice(2).join(" ") });
  console.log(JSON.stringify(resumo, null, 1));
  console.log("\nSOURCE_ID     RESULTADO                        SAUDE     CADENCIA            DOCUMENT_ID");
  for (const d of detalhes) {
    console.log(`${d.SOURCE_ID.padEnd(13)} ${String(d.OBSERVATION_RESULT).padEnd(32)} ${String(d.HEALTH_STATE).padEnd(9)} ${String(d.CADENCE_STATE ?? "-").padEnd(19)} ${d.DOCUMENT_ID ?? d.motivo ?? ""}`);
  }
}
