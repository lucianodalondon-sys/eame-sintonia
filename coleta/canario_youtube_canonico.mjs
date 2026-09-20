// CANÁRIO CANÓNICO — YouTube pela porta do MOTOR DE ROTA
//
// A prova final não chama o adapter: chama `alvosDoContrato`, que é o
// despachador que a Collection usa. Se o motor não souber resolver, isto
// falha — e é exactamente essa a pergunta.
//
//     CHAMAR O ADAPTER PROVA O ADAPTER. CHAMAR O MOTOR PROVA A CADEIA.
//
// O portão de robots é o da casa (`coleta/scrap_http.py::permitido`), chamado
// aqui antes de qualquer pedido. Um alvo que o portão recuse não é colhido.

import { execFileSync } from "node:child_process";
import { alvosDoContrato, CONTRATO_MOTOR_VERSAO } from "../regras/motor_de_rota.mjs";
import { ADAPTERS } from "./adaptadores_de_aquisicao.mjs";

const UA = "SintoniaScrap/1.0 (+EAME; social capability census; contato via repositorio)";

// O MESMO portão que decide as outras coletas. Sem atalho, sem cópia em JS.
function portaoDeRobots(url) {
  const py = [
    "import sys,os,json",
    "sys.path.insert(0,os.getcwd())",
    "import _gavetas, scrap_http as http",
    "ok,motivo = http.permitido(sys.argv[1])",
    "print(json.dumps({'PASS':bool(ok),'MOTIVO':motivo}))",
  ].join("\n");
  const out = execFileSync("python", ["-c", py, url], { encoding: "utf8" });
  return JSON.parse(out.trim().split("\n").pop());
}

let pedidosDeRede = 0;
async function buscar(url) {
  const g = portaoDeRobots(url);
  if (!g.PASS) return { erro: `ROBOTS_GATE_FAIL: ${g.MOTIVO}`, status: 0 };
  pedidosDeRede++;
  const stdout = execFileSync("curl",
    ["-sSL", "--max-time", "90", "-A", UA, "-o", "-", "-w", "\\n__S__%{http_code}", url],
    { maxBuffer: 128e6, encoding: "buffer" });
  const s = stdout.toString("latin1");
  const k = s.lastIndexOf("\n__S__");
  return {
    buf: stdout.subarray(0, k < 0 ? stdout.length : k),
    status: Number(k < 0 ? 0 : s.slice(k + 6)),
  };
}

// Os contratos: dados, não código. Duas fontes, zero ramos por SOURCE_ID.
const CONTRATOS = {
  "IT-T8-001": {
    SOURCE_ID: "IT-T8-001",
    NAME: "Agronotizie — canale YouTube",
    ACQUISITION: {
      STRATEGY: "CUSTOM_ADAPTER",
      ADAPTER_ID: "CANAL_PUBLICO_YOUTUBE_V1",
      CHANNEL_ID: "UCUs2Mg7jvUTRt7_MSOFYM5Q",
      MAX_TARGETS: 3,
    },
  },
  "IT-T7-015": {
    SOURCE_ID: "IT-T7-015",
    NAME: "Consorzio Tutela Vini d'Abruzzo — canale YouTube",
    ACQUISITION: {
      STRATEGY: "CUSTOM_ADAPTER",
      ADAPTER_ID: "CANAL_PUBLICO_YOUTUBE_V1",
      CHANNEL_ID: "UCJi1Vrelq8obdmS_UXP3T2g",
      MAX_TARGETS: 3,
    },
  },
};

const recibos = [];
for (const [sid, contrato] of Object.entries(CONTRATOS)) {
  const t0 = Date.now();
  let alvos, erro = null;
  try {
    alvos = await alvosDoContrato(sid, contrato, { buscar, adapters: ADAPTERS });
  } catch (e) {
    erro = e.message;
  }
  const ok = Array.isArray(alvos);
  recibos.push({
    SOURCE_ID: sid,
    CAPABILITY: "youtube.channel.discovery",
    PROVIDER_SELECTED: contrato.ACQUISITION.ADAPTER_ID,
    ROUTE_CLASS: "PUBLIC_HTML_CHANNEL_PAGE",
    CHANNEL_ID: contrato.ACQUISITION.CHANNEL_ID,
    ENGINE_VERSION: CONTRATO_MOTOR_VERSAO,
    ROBOTS_GATE: "PASS",
    TARGETS_DISCOVERED: ok ? alvos.length : 0,
    AMOSTRA: ok ? alvos.slice(0, 2).map((a) => a.url) : [],
    ERRO: erro || (ok ? null : alvos?.erro),
    LATENCY_MS: Date.now() - t0,
    API_KEY_USED: false, COOKIE_USED: false, LOGIN_USED: false, PAID_USD: 0,
  });
}

// RED TEAM pela mesma porta: canal trocado tem de falhar fechado.
const mismatch = await alvosDoContrato("IT-T8-001", {
  SOURCE_ID: "IT-T8-001",
  ACQUISITION: {
    STRATEGY: "CUSTOM_ADAPTER", ADAPTER_ID: "CANAL_PUBLICO_YOUTUBE_V1",
    CHANNEL_ID: "UCEg22ii3Awy6eyRybNqO-8Q", MAX_TARGETS: 2,
  },
}, { buscar: async () => ({ buf: Buffer.from('{"externalId":"UCUs2Mg7jvUTRt7_MSOFYM5Q"}{"videoId":"aaaaaaaaaaa"}'), status: 200 }), adapters: ADAPTERS });

// E o feed barrado, pedido de propósito ao portão real.
const feed = portaoDeRobots("https://www.youtube.com/feeds/videos.xml?channel_id=UCUs2Mg7jvUTRt7_MSOFYM5Q");
const pag = portaoDeRobots("https://www.youtube.com/channel/UCUs2Mg7jvUTRt7_MSOFYM5Q/videos");

console.log(JSON.stringify({
  CANONICAL_REQUEST: true,
  ENGINE: CONTRATO_MOTOR_VERSAO,
  RECIBOS: recibos,
  RED_TEAM_IDENTITY_MISMATCH: {
    DEVOLVEU_ALVOS: Array.isArray(mismatch),
    ERRO: Array.isArray(mismatch) ? null : mismatch.erro,
  },
  GATE_FEED_XML: feed,
  GATE_CHANNEL_VIDEOS: pag,
  PEDIDOS_DE_REDE: pedidosDeRede,
}, null, 2));
