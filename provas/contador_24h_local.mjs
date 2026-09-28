// O CONTADOR MULTICANAL (D90) AGORA ADAPTATIVO (D124) — PROVA ADVERSARIAL, CONTRA UM SERVIDOR LOCAL QUE CONTA.
//
//     node provas/contador_24h_local.mjs
//
// Zero rede externa: proxy para uma porta morta; os nomes *.test resolvem para 127.0.0.1 por um
// `_curlrc` so desta prova. Cada EXECUTOR e um PROCESSO node proprio (`contador_24h_executor.mjs`)
// que corre o transporte de verdade (curl). Os executores partilham SO o livro da cortesia. Quem conta
// os pedidos, e quantos estao em curso AO MESMO TEMPO em cada dominio, e o SERVIDOR.
//
// A politica desta prova e uma COPIA da oficial com numeros pequenos (SITE: 6/24 h, pausa 0,2 s), escrita
// num ficheiro temporario e dada em SINTONIA_CORTESIA_POLITICA: o codigo e o mesmo, so a escala muda.
//
//   A1  dois executores CONCORRENTES no mesmo dominio -> o servidor NUNCA ve 2 pedidos em curso ao dominio
//       (1 de cada vez), ve <= 6 no total; o livro tem exactamente o que o servidor viu; um recebeu TETO_24H
//   A2  o executor seguinte, com o orcamento esgotado -> 0 pedidos ao servidor (ADIADO sem pedir)
//   A3  um executor Python (cortesia_adaptativa.py + urllib) e um Node, concorrentes -> 1 de cada vez, <= 6
//   A4  outro dominio nao e afetado
//   B1  429 + Retry-After -> o orcamento cai para metade, bilhete RECUO, o executor seguinte faz 0 pedidos
//   B2  pagina de desafio (200 «Just a moment...») duas vezes -> PAUSADO 24 h, bilhete PAUSA_24H, 0 pedidos
//   B3  503 -> sinal HTTP_503 no livro
//   B4  SOBE: um dia limpo e usado no livro -> o orcamento dobra (6 -> 12) e o servidor ve mais de 6
//   C1  robots.txt ilegivel (HTTP 500) -> nenhum pedido alem do robots (ilegivel NAO e permissao)
import { createServer } from "node:http";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync, existsSync, appendFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = join(AQUI, "..");
// DA-21 (lote 4): o Python do AMBIENTE, nao `py` fixo — `py` so existe no Windows.
const PY = process.env.SINTONIA_PY || (process.platform === "win32" ? "py" : "python3");
const TMP = mkdtempSync(join(tmpdir(), "contador24h-"));
const POL = JSON.parse(readFileSync(join(RAIZ, "regras", "POLITICA-CORTESIA-ADAPTATIVA.json"), "utf8"));
Object.assign(POL.CLASSES.SITE, { ORCAMENTO_INICIAL_24H: 6, TETO_DE_SEGURANCA_24H: 24, MINIMO_24H: 2, PAUSA_MINIMA_S: 0.2 });
POL.LEASE_S = 20;
const POL_F = join(TMP, "POLITICA-DE-PROVA.json");
writeFileSync(POL_F, JSON.stringify(POL));

const enchimento = "<p>" + "Testo dell'articolo. ".repeat(80) + "</p>";
const PEDIDOS = [];
const EM_CURSO = new Map(), MAX_EM_CURSO = new Map();
const dom = h => h.replace(/^www\./, "");
let seq = 0;
const servidor = createServer((req, res) => {
  const host = String(req.headers.host || "").split(":")[0], d = dom(host);
  PEDIDOS.push({ host, p: req.url });
  EM_CURSO.set(d, (EM_CURSO.get(d) || 0) + 1);
  MAX_EM_CURSO.set(d, Math.max(MAX_EM_CURSO.get(d) || 0, EM_CURSO.get(d)));
  const fim = (codigo, corpo, cab = {}) => setTimeout(() => {
    EM_CURSO.set(d, EM_CURSO.get(d) - 1);
    res.writeHead(codigo, { "Content-Type": "text/html; charset=utf-8", ...cab }); res.end(corpo);
  }, 120);                                                     // devagar de proposito: uma rajada apareceria aqui
  // o desafio vem em TODAS as paginas do dominio, robots incluido (e o que um WAF faz)
  if (d === "desafio.test") return fim(200, "<!DOCTYPE html><html><head><title>Just a moment...</title></head><body>cf-chl</body></html>");
  if (req.url === "/robots.txt") return d === "ilegivel.test" ? fim(500, "erro") : fim(404, "non trovato");
  if (d === "lento429.test") return fim(429, "Too Many Requests", { "Retry-After": "3600" });
  if (d === "queda503.test") return fim(503, "Service Unavailable");
  if (req.url === "/news/") {
    seq++;
    return fim(200, `<!DOCTYPE html><html><body>${[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(i => `<a href="/news/materia-${seq}-${i}/">m</a>`).join("\n")}${enchimento}</body></html>`);
  }
  fim(200, `<!DOCTYPE html><html><head><title>${req.url}</title></head><body><h1>${req.url}</h1>${enchimento}</body></html>`);
});
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const PORTA = servidor.address().port;
const NOMES = ["cia.test", "www.cia.test", "outro.test", "py.test", "lento429.test", "desafio.test", "queda503.test", "sobe.test", "ilegivel.test"];
const CURL_HOME = mkdtempSync(join(tmpdir(), "contador24h-curl-"));
for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(CURL_HOME, n), NOMES.map(h => `resolve = "${h}:${PORTA}:127.0.0.1"`).join("\n") + "\n");
const MORTA = "http://127.0.0.1:9";
const ENV = { ...process.env, CURL_HOME, HTTP_PROXY: MORTA, HTTPS_PROXY: MORTA, http_proxy: MORTA, https_proxy: MORTA,
              ALL_PROXY: MORTA, NO_PROXY: ["127.0.0.1", "localhost", ...NOMES].join(","), no_proxy: ["127.0.0.1", "localhost", ...NOMES].join(","),
              PYTHONUTF8: "1", SINTONIA_CORTESIA_POLITICA: POL_F };
delete ENV.SINTONIA_TETO_24H; delete ENV.SINTONIA_CORTESIA_ALERTAS;

const correr = (cmd, args, livro) => new Promise(ok => {
  const p = spawn(cmd, args, { cwd: RAIZ, env: { ...ENV, SINTONIA_CORTESIA_LIVRO: livro } });
  let out = "", err = "";
  p.stdout.on("data", x => out += x); p.stderr.on("data", x => err += x);
  p.on("close", c => { const l = out.trim().split("\n").pop(); try { ok({ codigo: c, ...JSON.parse(l) }); } catch { ok({ codigo: c, ERRO: (out + err).slice(-600) }); } });
});
const executor = (livro, host, runId) => correr(process.execPath, [join(AQUI, "contador_24h_executor.mjs"), host, String(PORTA), runId, "10"], livro);
function executorPython(livro, host, runId, n) {
  const src = `
import sys, json, urllib.request, urllib.error
sys.path.insert(0, '.')
from coleta import cortesia_adaptativa as CA
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
feitos, adiados = 0, 0
for i in range(${n}):
    r = CA.reservar_ou_esperar('${host}', run_id='${runId}', linha='PY', espera_max_s=30)
    if r['ESTADO'] != 'RESERVADO':
        adiados += 1
        continue
    try:
        f = op.open(urllib.request.Request('http://127.0.0.1:${PORTA}/news/py-%d/' % i, headers={'Host': '${host}'}), timeout=10)
        corpo, st, cab = f.read(), f.status, dict(f.headers.items())
    except urllib.error.HTTPError as e:
        corpo, st, cab = e.read(), e.code, dict(e.headers.items())
    CA.registrar_resposta('${host}', st, cab, corpo=corpo, n_bytes=len(corpo), run_id='${runId}', linha='PY')
    feitos += 1
print(json.dumps({'RUN_ID': '${runId}', 'FEITOS': feitos, 'ADIADOS': adiados}))`;
  return correr(PY, ["-c", src], livro);
}
const conta = (d0, d) => PEDIDOS.slice(d0).filter(x => x.host === d || x.host.endsWith("." + d)).length;
const eventos = f => existsSync(f) ? readFileSync(f, "utf8").split("\n").filter(Boolean).map(l => JSON.parse(l)) : [];
const reservas = (f, d) => eventos(f).filter(e => e.TIPO === "RESERVA" && e.DOMINIO === d);
const respostas = (f, d) => eventos(f).filter(e => e.TIPO === "RESPOSTA" && e.DOMINIO === d);
const alertas = f => { const a = join(dirname(f), "ALERTAS-SCRAP-ENGINEER.ndjson"); return existsSync(a) ? readFileSync(a, "utf8").split("\n").filter(Boolean).map(l => JSON.parse(l)) : []; };
const CA = await import("../coleta/cortesia_adaptativa.mjs");
const estado = (f, d) => { process.env.SINTONIA_CORTESIA_LIVRO = f; process.env.SINTONIA_CORTESIA_POLITICA = POL_F; return CA.estadoDoDominio(d); };
let passou = 0, falhas = 0;
const ok = (cond, nome, info = "") => { if (cond) { passou++; console.log("  ok   ", nome); } else { falhas++; console.log("  FALHA", nome, info); } };

try {
  // A1 — dois executores concorrentes no mesmo dominio
  const L1 = join(TMP, "a", "LIVRO.ndjson"); let d0 = PEDIDOS.length;
  const [a, b] = await Promise.all([executor(L1, "cia.test", "A1-X"), executor(L1, "www.cia.test", "A1-Y")]);
  const n1 = conta(d0, "cia.test");
  const recusas = JSON.stringify([a.RECUSAS, b.RECUSAS, a.ERRO, b.ERRO]);
  console.log("A1 servidor cia.test =", n1, "| em curso ao mesmo tempo (max) =", MAX_EM_CURSO.get("cia.test"), "| reservas =", reservas(L1, "cia.test").length);
  ok(MAX_EM_CURSO.get("cia.test") === 1, "A1: 1 pedido de cada vez no dominio (nunca rajada)", `max ${MAX_EM_CURSO.get("cia.test")}`);
  ok(n1 <= 6 && n1 > 0, "A1: dois executores concorrentes -> o servidor ve <= 6 (o orcamento da politica de prova)", `viu ${n1}`);
  ok(reservas(L1, "cia.test").length === n1, "A1: o livro tem exactamente os pedidos que o servidor viu", `livro ${reservas(L1, "cia.test").length}`);
  ok(/TETO_24H/.test(recusas), "A1: pelo menos um recebeu TETO_24H (recusa, nao falha)", recusas.slice(0, 300));

  // A2 — o seguinte, com o orcamento esgotado: nao pede nada
  d0 = PEDIDOS.length;
  const c = await executor(L1, "cia.test", "A2-Z");
  ok(conta(d0, "cia.test") === 0, "A2: com o orcamento esgotado, o executor seguinte faz 0 pedidos", `fez ${conta(d0, "cia.test")}`);
  ok(c.codigo === 0 && !c.ERRO, "A2: a corrida acaba (a recusa nao rebenta a corrida)", JSON.stringify(c).slice(0, 200));

  // A3 — Python e Node concorrentes no mesmo dominio
  const L3 = join(TMP, "a3", "LIVRO.ndjson"); d0 = PEDIDOS.length;
  const [pn, pp] = await Promise.all([executor(L3, "py.test", "A3-NODE"), executorPython(L3, "py.test", "A3-PY", 5)]);
  const n3 = conta(d0, "py.test");
  console.log("A3 servidor py.test =", n3, "| python", JSON.stringify(pp), "| node", JSON.stringify(pn.PEDIDOS_POR_HOST), "| max em curso", MAX_EM_CURSO.get("py.test"));
  ok(n3 <= 6 && MAX_EM_CURSO.get("py.test") === 1, "A3: Python + Node concorrentes -> <= 6 e 1 de cada vez", `viu ${n3}, max ${MAX_EM_CURSO.get("py.test")}`);
  ok(reservas(L3, "py.test").length === n3, "A3: livro = servidor", `${reservas(L3, "py.test").length} vs ${n3}`);

  // A4 — outro dominio nao e afetado pelo livro cheio de cia.test
  d0 = PEDIDOS.length;
  await executor(L1, "outro.test", "A4-O");
  ok(conta(d0, "outro.test") > 0 && conta(d0, "outro.test") <= 6, "A4: outro.test tem os seus pedidos", `fez ${conta(d0, "outro.test")}`);

  // B1 — 429 com Retry-After
  const LB = join(TMP, "b", "LIVRO.ndjson");
  await executor(LB, "lento429.test", "B1-1");
  const e1 = estado(LB, "lento429.test");
  console.log("B1 lento429.test orcamento =", e1.ORCAMENTO_24H, "situacao =", e1.SITUACAO, "sinais =", JSON.stringify(respostas(LB, "lento429.test").map(r => r.SINAIS)));
  ok(respostas(LB, "lento429.test").some(r => r.SINAIS.includes("HTTP_429") && r.SINAIS.includes("RETRY_AFTER") && r.RETRY_AFTER_S === 3600),
     "B1: o 429 e o Retry-After ficaram medidos no livro");
  ok(e1.ORCAMENTO_24H === 3 && e1.SITUACAO === "RETRY_AFTER", "B1: o orcamento caiu para metade (6 -> 3) e o dominio espera o Retry-After", JSON.stringify(e1));
  ok(alertas(LB).some(x => x.DOMINIO === "lento429.test" && x.TIPO_ALERTA === "RECUO"), "B1: bilhete RECUO ao Scrap Engineer");
  d0 = PEDIDOS.length;
  await executor(LB, "lento429.test", "B1-2");
  ok(conta(d0, "lento429.test") === 0, "B1: durante o Retry-After, 0 pedidos", `fez ${conta(d0, "lento429.test")}`);

  // B2 — pagina de desafio, duas vezes
  await executor(LB, "desafio.test", "B2-1");
  await executor(LB, "desafio.test", "B2-2");
  const e2 = estado(LB, "desafio.test");
  console.log("B2 desafio.test situacao =", e2.SITUACAO, "sinais 24h =", e2.SINAIS_24H);
  ok(respostas(LB, "desafio.test").some(r => r.SINAIS.includes("PAGINA_DE_DESAFIO")), "B2: a pagina de desafio foi medida como sinal");
  ok(e2.SITUACAO === "PAUSADO", "B2: 2 sinais em 24 h -> dominio PAUSADO 24 h", JSON.stringify(e2));
  ok(alertas(LB).some(x => x.DOMINIO === "desafio.test" && x.TIPO_ALERTA === "PAUSA_24H"), "B2: bilhete PAUSA_24H");
  d0 = PEDIDOS.length;
  await executor(LB, "desafio.test", "B2-3");
  ok(conta(d0, "desafio.test") === 0, "B2: pausado, 0 pedidos", `fez ${conta(d0, "desafio.test")}`);

  // B3 — 503
  await executor(LB, "queda503.test", "B3");
  ok(respostas(LB, "queda503.test").some(r => r.SINAIS.includes("HTTP_503")), "B3: o 503 e sinal no livro");

  // B4 — SOBE: um dia limpo e usado (6 de 6, ha 25-30 h) -> 12
  const L4 = join(TMP, "b4", "LIVRO.ndjson");
  mkdirSync(dirname(L4), { recursive: true });
  const t0 = Date.now() / 1000 - 30 * 3600;
  for (let k = 0; k < 6; k++) {
    appendFileSync(L4, JSON.stringify({ TIPO: "RESERVA", DOMINIO: "sobe.test", EM: t0 + k * 60, RUN_ID: "ONTEM", LINHA: "SITES" }) + "\n");
    appendFileSync(L4, JSON.stringify({ TIPO: "RESPOSTA", DOMINIO: "sobe.test", EM: t0 + k * 60 + 1, STATUS: 200, SINAIS: [], MARCAS: [], RUN_ID: "ONTEM", LINHA: "SITES" }) + "\n");
  }
  ok(estado(L4, "sobe.test").ORCAMENTO_24H === 12, "B4: um dia limpo e usado -> o orcamento dobra (6 -> 12)", JSON.stringify(estado(L4, "sobe.test").ORCAMENTO_24H));
  d0 = PEDIDOS.length;
  await executor(L4, "sobe.test", "B4");
  ok(conta(d0, "sobe.test") > 6 && conta(d0, "sobe.test") <= 12, "B4: o servidor ve mais que o orcamento inicial e nunca mais que o novo", `fez ${conta(d0, "sobe.test")}`);

  // C1 — robots ilegivel nao e permissao
  d0 = PEDIDOS.length;
  await executor(LB, "ilegivel.test", "C1");
  const vistos = PEDIDOS.slice(d0).filter(x => x.host === "ilegivel.test").map(x => x.p);
  ok(vistos.length > 0 && vistos.every(p => p === "/robots.txt"), "C1: robots.txt ilegivel (HTTP 500) -> nenhum pedido alem do robots", JSON.stringify(vistos));
} finally {
  servidor.close();
  rmSync(TMP, { recursive: true, force: true });
  rmSync(CURL_HOME, { recursive: true, force: true });
}
console.log(`CONTADOR_24H_LOCAL (D124) · passou=${passou} FALHAS=${falhas}`);
process.exit(falhas ? 1 : 0);
