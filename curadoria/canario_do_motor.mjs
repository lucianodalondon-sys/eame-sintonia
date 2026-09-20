// O CANÁRIO DO SOURCE CURATOR — pela porta do MOTOR DE ROTA, para qualquer contrato.
//
//     CHAMAR O ADAPTER PROVA O ADAPTER. CHAMAR O MOTOR PROVA A CADEIA.
//
// Generaliza `coleta/canario_youtube_canonico.mjs`: em vez de dois contratos
// escritos aqui, lê o registo que a Collection executa (`regras/italy_contracts
// .mjs`) e pede ao motor (`alvosDoContrato`) que resolva UMA fonte. Se sair
// pelo menos um alvo, a rota resolve. Não colhe nada: o índice é lido, os
// alvos não são abertos.
//
//     VALIDAR != COLETAR.
//
// O portão de robots é o da casa (`coleta/scrap_http.py::permitido`), chamado
// antes de qualquer pedido — o mesmo que julga as outras coletas. Não há cópia
// em JS: um segundo leitor de robots é uma segunda lei.
//
// Saída: UMA linha JSON no stdout, sempre, mesmo em erro. O worker lê a última.
//
//     node curadoria/canario_do_motor.mjs IT-T2-025
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";
import { CONTRACTS } from "../regras/italy_contracts.mjs";
import { alvosDoContrato, CONTRATO_MOTOR_VERSAO } from "../regras/motor_de_rota.mjs";
import { ADAPTERS } from "../coleta/adaptadores_de_aquisicao.mjs";

const RAIZ = dirname(dirname(fileURLToPath(import.meta.url)));
const UA = "SintoniaScrap/1.0 (+EAME; source curator canary; contato via repositorio)";

function portaoDeRobots(url) {
  const py = [
    "import sys,os,json",
    "sys.path.insert(0,os.getcwd())",
    "import _gavetas, scrap_http as http",
    "try:",
    "    ok,motivo = http.permitido(sys.argv[1]); print(json.dumps({'PASS':bool(ok),'MOTIVO':motivo,'LIDO':True}))",
    "except Exception as e:",
    "    print(json.dumps({'PASS':False,'MOTIVO':type(e).__name__+': '+str(e)[:120],'LIDO':False}))",
  ].join("\n");
  for (const exe of [process.env.SINTONIA_PYTHON, "py", "python3", "python"].filter(Boolean)) {
    try {
      const out = execFileSync(exe, ["-c", py, url], { cwd: RAIZ, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
      const linha = out.trim().split("\n").pop();
      if (linha && linha.startsWith("{")) return JSON.parse(linha);
    } catch { /* tenta o proximo interpretador */ }
  }
  return { PASS: false, MOTIVO: "nenhum interpretador Python respondeu ao portao", LIDO: false };
}

let pedidosDeRede = 0;
let ultimoStatus = null;
async function buscar(url) {
  const g = portaoDeRobots(url);
  if (!g.PASS) {
    // NÃO SEI != PROIBIDO — os dois chegam pela mesma porta e separam-se aqui.
    return { erro: g.LIDO ? `ROBOTS_GATE_FAIL: ${g.MOTIVO}` : `ROBOTS_UNREADABLE: ${g.MOTIVO}`, status: 0, lido: g.LIDO };
  }
  pedidosDeRede++;
  const stdout = execFileSync("curl",
    ["-sSL", "--max-time", "60", "-A", UA, "-o", "-", "-w", "\\n__S__%{http_code}", url],
    { maxBuffer: 64e6, encoding: "buffer" });
  const s = stdout.toString("latin1");
  const k = s.lastIndexOf("\n__S__");
  const status = Number(k < 0 ? 0 : s.slice(k + 6));
  ultimoStatus = status;
  return { buf: stdout.subarray(0, k < 0 ? stdout.length : k), status };
}

function dizer(o) { console.log(JSON.stringify(o)); }

async function main() {
  const sid = process.argv[2];
  const base = { SOURCE_ID: sid, ENGINE: CONTRATO_MOTOR_VERSAO, PASS: false, HTTP: null,
                 ALVOS: 0, AMOSTRA: [], PEDIDOS_DE_REDE: 0, PAID_USD: 0, MEDIDO_EM: new Date().toISOString() };
  if (!sid || !CONTRACTS[sid]) {
    dizer({ ...base, CLASSE: "UNKNOWN", PORQUE: `SOURCE_ID ${sid} nao esta no registo da Collection` });
    return 2;
  }
  const c = CONTRACTS[sid];
  if (!c.ACQUISITION) {
    dizer({ ...base, CLASSE: "CONTRACT", PORQUE: "contrato sem bloco ACQUISITION executavel" });
    return 3;
  }
  try {
    const alvos = await alvosDoContrato(sid, c, { buscar, adapters: ADAPTERS });
    if (alvos && alvos.erro) {
      const e = String(alvos.erro);
      const classe = /ROBOTS_GATE_FAIL/.test(e) ? "ROBOTS"
        : /ROBOTS_UNREADABLE/.test(e) ? "UNKNOWN"
        : /\b429\b|\b503\b/.test(e) ? "RATE"
        : /\b40[13]\b/.test(e) ? "AUTH"
        : "SOURCE";
      const http = (e.match(/\b(\d{3})\b/) || [])[1];
      dizer({ ...base, HTTP: http ? Number(http) : ultimoStatus, CLASSE: classe,
              PORQUE: e.slice(0, 200), PEDIDOS_DE_REDE: pedidosDeRede });
      return 1;
    }
    const lista = Array.isArray(alvos) ? alvos : [];
    dizer({ ...base, PASS: lista.length > 0, HTTP: ultimoStatus ?? 200, ALVOS: lista.length,
            AMOSTRA: lista.slice(0, 2).map((a) => a.url), PEDIDOS_DE_REDE: pedidosDeRede,
            PORQUE: lista.length > 0 ? "" : "o motor resolveu e nao saiu nenhum alvo", CLASSE: lista.length > 0 ? "OK" : "SOURCE" });
    return lista.length > 0 ? 0 : 1;
  } catch (e) {
    dizer({ ...base, HTTP: ultimoStatus, CLASSE: "UNKNOWN", PORQUE: `${e.name}: ${String(e.message).slice(0, 180)}`,
            PEDIDOS_DE_REDE: pedidosDeRede });
    return 1;
  }
}

main().then((code) => process.exit(code));
