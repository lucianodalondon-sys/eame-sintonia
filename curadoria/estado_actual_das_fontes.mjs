// O ESTADO ACTUAL DAS FONTES — materializado a partir do que a casa TEM HOJE.
//
//     FOTOGRAFIA ANTIGA CERTA NO SEU DIA  !=  VERDADE DE HOJE
//
// Este script e a resposta a pergunta «contra o que reconciliar?». Ele nao le
// o snapshot do SOURCE CURATOR (`READY-FOR-COLLECTION-V1.json`, que ainda
// classifica as 50 YouTube como ROUTE_BLOCKED pela rota velha). Ele le o que
// a linha operacional prova hoje, e so isso:
//
//   1. o registo de contratos que a Collection executa
//      (`regras/italy_contracts.mjs` = contratos a mao + tabela onboarded),
//      conferido pelo motor de rota (`conferirAquisicao` + `conferirIdentidade`);
//   2. a ficha no Atlas (`docs/fontes/ATLAS-DE-FONTES-EAME.md`);
//   3. os territorios com executor (`pedido/receitas.py`);
//   4. o canario mais recente de cada fonte (o censo YouTube da
//      BIG-COLLECTION-RELEASE para as 50; a SONDAGEM da tabela para as demais);
//   5. o resultado da Big Collection BCR-2026-09-20, lido do RUN-MANIFEST
//      (a corrida, o INGRESSO e o motivo), e conferido contra o registo do
//      relatorio.
//
// O SOURCE CURATOR semeia o ciclo de vida A PARTIR DESTE FICHEIRO, nunca a
// partir da fotografia. A fotografia fica no repositorio como historia.
//
//     ESTE FICHEIRO E DERIVADO. REGENERA-SE. NAO SE EDITA A MAO.
//
// Correr:  node curadoria/estado_actual_das_fontes.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { CONTRACTS, CONTRACT_IDS, ONBOARDED_IDS } from "../regras/italy_contracts.mjs";
import { conferirAquisicao, conferirIdentidade } from "../regras/motor_de_rota.mjs";

const RAIZ = dirname(dirname(fileURLToPath(import.meta.url)));
const SAIDA = join(RAIZ, "curadoria", "ESTADO-ACTUAL-DAS-FONTES-V1.json");
const ATLAS = join(RAIZ, "docs", "fontes", "ATLAS-DE-FONTES-EAME.md");
const CENSO_YT = join(RAIZ, "data", "derivados", "YOUTUBE-CANARIO-50-2026-09-20.json");
const MANIFESTO = join(RAIZ, "data", "samples", "RUN-MANIFEST.json");
const RELATORIO_BCR = join(RAIZ, "RELATORIO-BIG-COLLECTION-RELEASE.md");
const FOTO = join(RAIZ, "curadoria", "READY-FOR-COLLECTION-V1.json");

// A janela da BCR, como o relatorio a registou (§6).
export const BCR = Object.freeze({
  RUN_ID: "BCR-2026-09-20",
  INICIO: "2026-09-20T18:59:34Z",
  FIM: "2026-09-20T21:50:35Z",
});

function ler(p) { return readFileSync(p, "utf8"); }
function lerJson(p) { return JSON.parse(ler(p)); }

// ── 1 · o registo de contratos, conferido pelo motor ──────────────────────
function rotaDe(c) {
  const aq = c.ACQUISITION;
  if (!aq) return c.CANONICAL_ENTRY_URL || "NAO SEI";
  if (aq.STRATEGY === "CUSTOM_ADAPTER" && aq.ADAPTER_ID === "CANAL_PUBLICO_YOUTUBE_V1")
    return `https://www.youtube.com/channel/${aq.CHANNEL_ID}/videos`;
  if (aq.STRATEGY === "STATIC_ENDPOINT") return aq.URL;
  if (aq.STRATEGY === "TEMPLATE_ENUMERATION") return aq.TEMPLATE;
  return aq.INDEX_URL || c.CANONICAL_ENTRY_URL || "NAO SEI";
}

function executavel(id, c) {
  if (!c.ACQUISITION) return { EXECUTAVEL: false, PORQUE: "contrato a mao sem bloco ACQUISITION executavel" };
  try {
    conferirAquisicao(id, c.ACQUISITION);
    if (c.IDENTITY) conferirIdentidade(id, c.IDENTITY);
    return { EXECUTAVEL: true, PORQUE: "conferirAquisicao + conferirIdentidade passam" };
  } catch (e) {
    return { EXECUTAVEL: false, PORQUE: `o motor recusa o bloco: ${String(e.message).slice(0, 160)}` };
  }
}

// ── 2 · a ficha no Atlas ──────────────────────────────────────────────────
function fichasDoAtlas() {
  const t = ler(ATLAS);
  const ids = new Set();
  for (const m of t.matchAll(/^#### (IT-T\d+-\d{3}) ·/gm)) ids.add(m[1]);
  for (const m of t.matchAll(/^SOURCE_ID:\s+(IT-T\d+-\d{3})\s*$/gm)) ids.add(m[1]);
  return ids;
}

// ── 3 · os territorios com executor — perguntado a receita, nao adivinhado ─
function territoriosComExecutor() {
  const py = [
    "import sys, os, json",
    "sys.path.insert(0, os.getcwd())",
    "import _gavetas, receitas",
    "print(json.dumps(sorted(receitas.EXECUTORES)))",
  ].join("\n");
  for (const exe of [process.env.SINTONIA_PYTHON, "py", "python3", "python"].filter(Boolean)) {
    const r = spawnSync(exe, ["-c", py], { cwd: RAIZ, encoding: "utf8" });
    if (r.status === 0 && r.stdout.trim()) {
      const linha = r.stdout.trim().split("\n").pop();
      return { TERRITORIOS: JSON.parse(linha), PYTHON: exe };
    }
  }
  return { TERRITORIOS: null, PYTHON: null };
}

// ── 4 · o canario mais recente ────────────────────────────────────────────
function canariosYoutube() {
  const d = lerJson(CENSO_YT);
  const por = {};
  for (const r of d.RECIBOS) {
    por[r.SOURCE_ID] = {
      ORIGEM: "data/derivados/YOUTUBE-CANARIO-50-2026-09-20.json",
      MEDIDO_EM: d.MEDIDO_EM,
      RESULTADO: r.ROUTE_RESOLVED === "YES" && r.ROBOTS_GATE === "PASS" && r.IDENTITY_MATCH === "YES" ? "PASS" : "FAIL",
      ROTA: r.ROUTE,
      ROBOTS_GATE: r.ROBOTS_GATE,
      ALVOS: r.TARGETS_DISCOVERED,
      ERRO: r.ERRO,
    };
  }
  return { POR_FONTE: por, GATE_WATCH: d.ROBOTS?.GATE_WATCH ?? null, GATE_FEED_XML: d.ROBOTS?.GATE_FEED_XML ?? null };
}

function canarioDaTabela(c) {
  const s = c.SONDAGEM;
  if (!s) return null;
  return {
    ORIGEM: "regras/italy_contracts_onboarded.json · SONDAGEM",
    MEDIDO_EM: s.SONDADO_EM || "NAO SEI",
    RESULTADO: s.DOCUMENTO || s.ENTRADA_STATUS === 200 ? "PASS" : "NAO SEI",
    ROTA: rotaDe(c),
    REGRA: s.REGRA || "NAO SEI",
  };
}

// ── 5 · a Big Collection, lida do manifesto e conferida contra o relatorio ─
function corridasDaBcr() {
  const d = lerJson(MANIFESTO);
  const por = {};
  for (const r of d.RUNS) {
    const sid = r?.PEDIDO?.filtros?.fonte;
    const t = r.STARTED_AT || "";
    if (!sid || t < BCR.INICIO || t > BCR.FIM) continue;
    if (!por[sid] || por[sid].STARTED_AT < t) por[sid] = r;
  }
  const out = {};
  for (const [sid, r] of Object.entries(por)) {
    const obs = (r.INGRESSO && r.INGRESSO.PARA_A_PORTA) || [];
    const colheita = r.RETORNO && typeof r.RETORNO.COLHEITA === "number" ? r.RETORNO.COLHEITA : null;
    const motivos = obs.map((o) => String(o.motivo || ""));
    let classe, motivo;
    if (obs.length === 0) {
      classe = colheita === 0 ? "CAPABILITY_GAP" : "NAO SEI";
      motivo = colheita === 0
        ? "a corrida saiu sem nenhuma observacao e com zero itens: defeito da casa, nao da fonte (RELATORIO-BIG-COLLECTION-RELEASE §9 B1)"
        : "sem observacao no INGRESSO";
    } else if (obs.some((o) => o.HEALTH_STATE === "HEALTHY")) {
      // A fonte entregou documentos. Itens que falharam a identidade (B8 do
      // relatorio: IT-T3-011) sao avaria de ITEM, nao de FONTE — contam-se ao lado.
      classe = "SUCCESS";
      motivo = obs.every((o) => o.HEALTH_STATE === "HEALTHY") ? "" :
        `${obs.length - obs.filter((o) => o.HEALTH_STATE === "HEALTHY").length} item(ns) falharam: ${motivos.find((m) => m) || ""}`;
    } else if (motivos.some((m) => /\b429\b/.test(m))) {
      classe = "RATE_LIMITED_429"; motivo = motivos.find((m) => /\b429\b/.test(m));
    } else {
      classe = "ROUTE_FAILURE"; motivo = motivos.find((m) => m) || "";
    }
    out[sid] = {
      RUN_ID: r.RUN_ID, STATUS: r.STATUS, STARTED_AT: r.STARTED_AT,
      CLASSE: classe, MOTIVO: motivo.slice(0, 200),
      OBSERVACOES: obs.length,
      HEALTHY: obs.filter((o) => o.HEALTH_STATE === "HEALTHY").length,
    };
  }
  return out;
}

// O registo do relatorio (§6.3) — a segunda leitura, para conferir a primeira.
function tabelaDoRelatorio() {
  const t = ler(RELATORIO_BCR);
  const por = {};
  for (const m of t.matchAll(/^\| (IT-T\d+-\d{3}) \| T\d+ \| [A-Z_0-9]+ \| `([^`]+)` \| ([A-Z_]+) \|/gm)) {
    por[m[1]] = { RUN_ID: m[2], CLASSE: m[3] };
  }
  return por;
}

// A classe do relatorio e a classe medida aqui falam vocabularios vizinhos.
const EQUIVALENTES = { RATE_LIMITED_429: "POLICY_BLOCK", CAPABILITY_GAP: "SOURCE_FAILURE_SEM_OBS" };

export function materializar() {
  const fichas = fichasDoAtlas();
  const territorios = territoriosComExecutor();
  const yt = canariosYoutube();
  const bcr = corridasDaBcr();
  const relatorio = tabelaDoRelatorio();
  const foto = lerJson(FOTO);
  const onboarded = new Set(ONBOARDED_IDS);

  const fontes = [];
  for (const id of CONTRACT_IDS) {
    const c = CONTRACTS[id];
    const ex = executavel(id, c);
    const ficha = fichas.has(id);
    const comExecutor = territorios.TERRITORIOS ? territorios.TERRITORIOS.includes(c.TERRITORY) : null;
    const aq = c.ACQUISITION || {};
    const canario = yt.POR_FONTE[id] || canarioDaTabela(c) || null;
    const corrida = bcr[id] || null;
    const reportado = relatorio[id] || null;
    let confere = null;
    if (corrida && reportado) {
      confere = corrida.RUN_ID === reportado.RUN_ID &&
        (corrida.CLASSE === reportado.CLASSE || EQUIVALENTES[corrida.CLASSE] === reportado.CLASSE ||
         (corrida.CLASSE === "CAPABILITY_GAP" && reportado.CLASSE === "CAPABILITY_GAP"));
    }
    fontes.push({
      SOURCE_ID: id,
      TERRITORY: c.TERRITORY,
      NAME: c.NAME || c.OWNER || "NAO SEI",
      ORIGEM_DO_CONTRATO: onboarded.has(id) ? (c.ACQUISITION && CONTRACTS[id].ONBOARDED_BY && !c.BATCH_ID ? "HAND+TABELA" : "TABELA_ONBOARDED") : "HAND",
      BATCH_ID: c.BATCH_ID || null,
      STRATEGY: aq.STRATEGY || null,
      ADAPTER_ID: aq.ADAPTER_ID || null,
      ROUTE_TYPE: c.ROUTE_TYPE || "NAO SEI",
      ROUTE: rotaDe(c),
      IDENTITY_KIND: c.IDENTITY_KIND || (c.IDENTITY ? c.IDENTITY.STRATEGY : "NAO SEI"),
      EXECUTAVEL: ex.EXECUTAVEL,
      PORQUE_EXECUTAVEL: ex.PORQUE,
      FICHA_NO_ATLAS: ficha,
      TERRITORIO_COM_EXECUTOR: comExecutor,
      // A regra da BIG-COLLECTION-RELEASE §4, aplicada ao registo de hoje.
      READY_PELA_REGRA_DA_CASA: ex.EXECUTAVEL && ficha && comExecutor === true,
      CANARIO_MAIS_RECENTE: canario,
      BIG_COLLECTION: corrida ? { ...corrida, REPORTADO: reportado, CONFERE_COM_RELATORIO: confere } : null,
    });
  }

  // As fontes que o curator contratou e canariou mas que NAO estao no registo
  // da Collection: historia, nao estado vigente. Entram nomeadas, para que o
  // resemeador as trate como o que sao — candidatas com canario medido.
  const soNaFoto = foto.FONTES
    .filter((f) => !CONTRACTS[f.SOURCE_ID])
    .map((f) => ({
      SOURCE_ID: f.SOURCE_ID, CANDIDATE_ID: f.CANDIDATE_ID, NAME: f.NAME, TERRITORY: f.TERRITORY,
      BATCH_ID: f.BATCH_ID, ESTADO_NA_FOTO: f.STATE, REASON_NA_FOTO: String(f.REASON || "").slice(0, 200),
      FICHA_NO_ATLAS: fichas.has(f.SOURCE_ID),
      ORIGEM: `curadoria/READY-FOR-COLLECTION-V1.json @ ${String(foto.SOURCE_CURATOR_HEAD).slice(0, 12)} (${foto.GERADO_EM})`,
    }));

  // As 50 YouTube da fotografia, e o que a fotografia dizia delas — so para o
  // leitor ver a diferenca entre o dia dela e hoje.
  const fotoYt = foto.FONTES.filter((f) => f.BATCH_ID === "LOTE-YOUTUBE-FEED").map((f) => f.SOURCE_ID);

  const fichasSemContrato = [...fichas].filter((id) => !CONTRACTS[id] && !soNaFoto.some((s) => s.SOURCE_ID === id)).sort();

  const resumo = {
    CONTRACT_IDS: CONTRACT_IDS.length,
    ONBOARDED: ONBOARDED_IDS.length,
    EXECUTAVEIS: fontes.filter((f) => f.EXECUTAVEL).length,
    SEM_BLOCO_EXECUTAVEL: fontes.filter((f) => !f.EXECUTAVEL).map((f) => f.SOURCE_ID),
    SEM_FICHA_NO_ATLAS: fontes.filter((f) => !f.FICHA_NO_ATLAS).map((f) => f.SOURCE_ID),
    READY_PELA_REGRA_DA_CASA: fontes.filter((f) => f.READY_PELA_REGRA_DA_CASA).length,
    BCR_POR_CLASSE: Object.fromEntries(
      ["SUCCESS", "ROUTE_FAILURE", "RATE_LIMITED_429", "CAPABILITY_GAP", "NAO SEI"].map((k) =>
        [k, fontes.filter((f) => f.BIG_COLLECTION && f.BIG_COLLECTION.CLASSE === k).length])),
    BCR_COM_CORRIDA: fontes.filter((f) => f.BIG_COLLECTION).length,
    BCR_DIVERGE_DO_RELATORIO: fontes.filter((f) => f.BIG_COLLECTION && f.BIG_COLLECTION.CONFERE_COM_RELATORIO === false).map((f) => f.SOURCE_ID),
    BCR_SEM_LINHA_NO_RELATORIO: fontes.filter((f) => f.BIG_COLLECTION && !f.BIG_COLLECTION.REPORTADO).map((f) => f.SOURCE_ID),
    YOUTUBE_NO_REGISTO: fontes.filter((f) => f.ADAPTER_ID === "CANAL_PUBLICO_YOUTUBE_V1").length,
    YOUTUBE_NA_FOTO_COMO_ROUTE_BLOCKED: fotoYt.length,
    YOUTUBE_CANARIO_PASS: fontes.filter((f) => f.ADAPTER_ID === "CANAL_PUBLICO_YOUTUBE_V1" && f.CANARIO_MAIS_RECENTE && f.CANARIO_MAIS_RECENTE.RESULTADO === "PASS").length,
    SO_NA_FOTO: soNaFoto.length,
    FICHAS_IT_NO_ATLAS: fichas.size,
    FICHAS_SEM_CONTRATO: fichasSemContrato.length,
    TERRITORIOS_COM_EXECUTOR: territorios.TERRITORIOS,
  };

  const head = spawnSync("git", ["rev-parse", "--short", "HEAD"], { cwd: RAIZ, encoding: "utf8" }).stdout.trim() || "NAO SEI";
  return {
    DATASET: "ESTADO-ACTUAL-DAS-FONTES-V1",
    CONTRATO: "SOURCE_CURATOR_CURRENT_STATE/v1",
    LEI: [
      "Derivado do registo que a Collection executa HOJE, nunca da fotografia do curator.",
      "READY_PELA_REGRA_DA_CASA = contrato executavel (motor de rota) AND ficha no Atlas AND territorio com executor.",
      "BIG_COLLECTION e o que a corrida BCR-2026-09-20 observou; nao e opiniao sobre a fonte.",
      "Fonte so na fotografia e historia, nao estado vigente.",
    ],
    GERADO_EM: new Date().toISOString(),
    HEAD: head,
    BCR,
    ROBOTS_YOUTUBE: { GATE_WATCH: yt.GATE_WATCH, GATE_FEED_XML: yt.GATE_FEED_XML },
    PYTHON_USADO_PARA_RECEITAS: territorios.PYTHON,
    RESUMO: resumo,
    FONTES: fontes,
    SO_NA_FOTO: soNaFoto,
    FICHAS_SEM_CONTRATO: fichasSemContrato,
  };
}

if (process.argv[1] && process.argv[1].split(/[\\/]/).pop() === "estado_actual_das_fontes.mjs") {
  const d = materializar();
  writeFileSync(SAIDA, JSON.stringify(d, null, 1) + "\n", "utf8");
  console.log(`ESTADO_ACTUAL = ${SAIDA}`);
  console.log(JSON.stringify(d.RESUMO, null, 1));
}
