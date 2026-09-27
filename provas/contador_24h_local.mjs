// O CONTADOR MULTICANAL DE 24 H (D90) — PROVA ADVERSARIAL, CONTRA UM SERVIDOR LOCAL QUE CONTA.
//
//     node provas/contador_24h_local.mjs
//
// Zero rede externa: proxy para uma porta morta; os nomes *.test resolvem para 127.0.0.1 por um
// `_curlrc` so desta prova. Cada EXECUTOR e um PROCESSO node proprio (`contador_24h_executor.mjs`)
// que corre o transporte de verdade. Os executores partilham SO o livro de 24 h. Quem conta os
// pedidos e o SERVIDOR.
//
//   A1  dois executores CONCORRENTES no mesmo dominio (sem livro da onda: o teto antigo nao os via)
//       -> o servidor ve <= 5 pedidos a cia.test; o livro de 24 h diz 5; pelo menos um recebeu TETO_24H
//   A2  o 2.o executor DEPOIS de o 1.o esgotar -> 0 pedidos ao servidor (ADIADO sem pedir)
//   A3  um executor Python (reserva_24h.py + urllib) e um Node, concorrentes, no mesmo dominio -> <= 5
//   A4  outro dominio nao e afetado
import { createServer } from "node:http";
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = join(AQUI, "..");
// DA-21 (lote 4): o Python do AMBIENTE, nao `py` fixo — `py` so existe no Windows (na nuvem: spawn py ENOENT).
// A mesma regra de `provas/corrida_abortada_local.mjs`: SINTONIA_PY, senao `py` no Windows e `python3` fora.
const PY = process.env.SINTONIA_PY || (process.platform === "win32" ? "py" : "python3");
const TMP = mkdtempSync(join(tmpdir(), "contador24h-"));
const enchimento = "<p>" + "Testo dell'articolo. ".repeat(80) + "</p>";
const PEDIDOS = [];
let seq = 0;
const servidor = createServer((req, res) => {
  const host = String(req.headers.host || "").split(":")[0];
  PEDIDOS.push({ host, p: req.url });
  if (req.url === "/robots.txt") { res.writeHead(404); res.end("non trovato"); return; }
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  if (req.url === "/news/") {
    seq++;
    res.end(`<!DOCTYPE html><html><body>${[0, 1, 2, 3, 4, 5].map(i => `<a href="/news/materia-${seq}-${i}/">m</a>`).join("\n")}${enchimento}</body></html>`);
    return;
  }
  res.end(`<!DOCTYPE html><html><head><title>${req.url}</title></head><body><h1>${req.url}</h1>${enchimento}</body></html>`);
});
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const PORTA = servidor.address().port;
const NOMES = ["cia.test", "www.cia.test", "outro.test", "py.test"];
const CURL_HOME = mkdtempSync(join(tmpdir(), "contador24h-curl-"));
for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(CURL_HOME, n), NOMES.map(h => `resolve = "${h}:${PORTA}:127.0.0.1"`).join("\n") + "\n");
const MORTA = "http://127.0.0.1:9";
const ENV = { ...process.env, CURL_HOME, HTTP_PROXY: MORTA, HTTPS_PROXY: MORTA, http_proxy: MORTA, https_proxy: MORTA,
              ALL_PROXY: MORTA, NO_PROXY: ["127.0.0.1", "localhost", ...NOMES].join(","), no_proxy: ["127.0.0.1", "localhost", ...NOMES].join(","),
              PYTHONUTF8: "1" };

function executor(livro, host, runId) {
  return new Promise(ok => {
    const p = spawn(process.execPath, [join(AQUI, "contador_24h_executor.mjs"), host, String(PORTA), runId, "6"],
                    { cwd: RAIZ, env: { ...ENV, SINTONIA_TETO_24H: livro } });
    let out = "", err = "";
    p.stdout.on("data", d => out += d); p.stderr.on("data", d => err += d);
    p.on("close", c => { const l = out.trim().split("\n").pop(); try { ok({ codigo: c, ...JSON.parse(l) }); } catch { ok({ codigo: c, ERRO: (out + err).slice(-400) }); } });
  });
}
function executorPython(livro, host, runId, n) {
  const src = `
import sys, json, urllib.request
sys.path.insert(0, '.')
from coleta import reserva_24h as R
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
feitos, adiados = 0, 0
for i in range(${n}):
    r = R.reservar('${host}', 1, run_id='${runId}', linha='PY')
    if r['ESTADO'] != 'RESERVADO':
        adiados += 1
        continue
    op.open(urllib.request.Request('http://127.0.0.1:${PORTA}/news/py-%d/' % i, headers={'Host': '${host}'}), timeout=10).read()
    feitos += 1
print(json.dumps({'RUN_ID': '${runId}', 'FEITOS': feitos, 'ADIADOS': adiados}))`;
  return new Promise(ok => {
    const p = spawn(PY, ["-c", src], { cwd: RAIZ, env: { ...ENV, SINTONIA_TETO_24H: livro } });
    let out = "", err = "";
    p.stdout.on("data", d => out += d); p.stderr.on("data", d => err += d);
    p.on("close", c => { const l = out.trim().split("\n").pop(); try { ok({ codigo: c, ...JSON.parse(l) }); } catch { ok({ codigo: c, ERRO: (out + err).slice(-400) }); } });
  });
}
const conta = (d0, dom) => PEDIDOS.slice(d0).filter(x => x.host === dom || x.host.endsWith("." + dom)).length;
const reservas = f => JSON.parse(readFileSync(f, "utf8")).RESERVAS;
let passou = 0, falhas = 0;
const ok = (cond, nome, info = "") => { if (cond) { passou++; console.log("  ok   ", nome); } else { falhas++; console.log("  FALHA", nome, info); } };

try {
  // A1 — dois executores concorrentes no mesmo dominio
  const L1 = join(TMP, "A1.json"); let d0 = PEDIDOS.length;
  const [a, b] = await Promise.all([executor(L1, "cia.test", "A1-X"), executor(L1, "www.cia.test", "A1-Y")]);
  const n1 = conta(d0, "cia.test");
  const r1 = reservas(L1).filter(r => r.DOMINIO === "cia.test");
  const recusas = JSON.stringify([a.RECUSAS, b.RECUSAS, a.ERRO, b.ERRO]);
  console.log("A1 servidor cia.test =", n1, "| reservas =", r1.length, "| run_ids =", [...new Set(r1.map(r => r.RUN_ID))].join(","));
  ok(n1 <= 5, "A1: dois executores concorrentes -> o servidor ve <= 5 pedidos ao dominio", `viu ${n1}`);
  ok(r1.reduce((s, r) => s + r.QTD, 0) === n1, "A1: o livro de 24 h tem exactamente os pedidos que o servidor viu", `livro ${r1.length}`);
  ok(/TETO_24H/.test(recusas), "A1: pelo menos um recebeu TETO_24H (recusa, nao falha)", recusas.slice(0, 300));

  // A2 — o 2.o depois de o 1.o esgotar: nao pede nada
  d0 = PEDIDOS.length;
  const c = await executor(L1, "cia.test", "A2-Z");
  ok(conta(d0, "cia.test") === 0, "A2: com o dominio esgotado nas 24 h, o executor seguinte faz 0 pedidos", `fez ${conta(d0, "cia.test")}`);
  ok(c.codigo === 0 && !c.ERRO, "A2: a corrida acaba (a recusa nao rebenta a corrida)", JSON.stringify(c).slice(0, 200));

  // A3 — Python e Node concorrentes no mesmo dominio
  const L3 = join(TMP, "A3.json"); d0 = PEDIDOS.length;
  const [pn, pp] = await Promise.all([executor(L3, "py.test", "A3-NODE"), executorPython(L3, "py.test", "A3-PY", 5)]);
  const n3 = conta(d0, "py.test");
  console.log("A3 servidor py.test =", n3, "| python feitos", pp.FEITOS, "adiados", pp.ADIADOS, "| node", JSON.stringify(pn.PEDIDOS_POR_HOST));
  ok(n3 <= 5, "A3: Python + Node concorrentes -> <= 5 no dominio", `viu ${n3} ${JSON.stringify(pp)}`);
  ok(reservas(L3).length === n3, "A3: livro = servidor", `${reservas(L3).length} vs ${n3}`);

  // A4 — outro dominio nao e afetado pelo livro cheio de cia.test
  d0 = PEDIDOS.length;
  await executor(L1, "outro.test", "A4-O");
  ok(conta(d0, "outro.test") > 0 && conta(d0, "outro.test") <= 5, "A4: outro.test tem os seus pedidos", `fez ${conta(d0, "outro.test")}`);
} finally {
  servidor.close();
  rmSync(TMP, { recursive: true, force: true });
  rmSync(CURL_HOME, { recursive: true, force: true });
}
console.log(`CONTADOR_24H_LOCAL · passou=${passou} FALHAS=${falhas}`);
process.exit(falhas ? 1 : 0);
