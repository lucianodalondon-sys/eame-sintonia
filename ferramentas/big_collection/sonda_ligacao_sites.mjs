// A SONDA DA LIGACAO DA LINHA SITES — medida pelo COMPORTAMENTO, nunca pelo texto (D124-REBASE, 28/09/2026).
//
//     node ferramentas/big_collection/sonda_ligacao_sites.mjs [--transporte=<coleta/italy_pilot_collect.mjs>]
//
// Porque existe: a coleta continua (`coleta_continua.py`) so corre uma linha de rede LIGADA ao contador de
// 24 h. Isso media-se procurando a string `reservar24h(host, 1)` no transporte. A D124 mudou a chamada para
// `reservar24h(host, 1, {...})` — o transporte continuava ligado e a linha ficava ESPERA_LIGACAO (o
// verificador independente mediu-o). E o inverso tambem era possivel: o texto la, e a chamada morta.
//
// O que se mede aqui (ZERO rede externa: proxy de saida para uma porta fechada, os dois nomes resolvem para
// um servidor em 127.0.0.1 pelo `_curlrc` de um CURL_HOME temporario; livro da cortesia TEMPORARIO):
//   A  um pedido pelo `baixar()` do transporte a um dominio livre: CADA pedido que chegou ao SERVIDOR tem
//      uma RESERVA no livro escrita ANTES de ele chegar, e uma RESPOSTA registada depois;
//   B  um pedido a um dominio que o livro diz PAUSADO (2 sinais em 24 h): ZERO pedidos no servidor.
// LIGADA = A e B. Sai uma linha JSON (a ultima): {"LIGADA": bool, "PORQUE": ..., "MEDIDO": {...}}.
//
// A politica da sonda e uma copia da real com a pausa minima a 0 (so para a sonda nao demorar): mede-se o
// FIO (reserva antes do pedido, obediencia ao livro), nao os numeros.
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const arg = Object.fromEntries(process.argv.slice(2).filter(a => a.startsWith("--") && a.includes("="))
  .map(a => [a.slice(2, a.indexOf("=")), a.slice(a.indexOf("=") + 1)]));
const TRANSPORTE = resolve(arg.transporte || join(AQUI, "..", "..", "coleta", "italy_pilot_collect.mjs"));
const LIVRE = "sonda-ligacao.test", FECHADO = "sonda-fechada.test";

const dizer = (ligada, porque, medido = {}) => {
  console.log(JSON.stringify({ LIGADA: ligada, PORQUE: porque, TRANSPORTE, MEDIDO: medido }));
};

const TMP = mkdtempSync(join(tmpdir(), "sonda-ligacao-"));
let servidor = null;
try {
  for (const k of Object.keys(process.env)) if (k.startsWith("SINTONIA_")) delete process.env[k];
  for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
    process.env[k] = "http://127.0.0.1:9";
  process.env.NO_PROXY = process.env.no_proxy = `127.0.0.1,localhost,${LIVRE},${FECHADO}`;
  process.env.ITALY_OPS_ROOT = join(TMP, "ops");

  const PEDIDOS = [];
  servidor = createServer((req, res) => {
    PEDIDOS.push({ host: String(req.headers.host || "").split(":")[0], p: req.url, t: Date.now() / 1000 });
    if (req.url === "/robots.txt") { res.writeHead(404); res.end("non trovato"); return; }
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.end("<!DOCTYPE html><html><body><p>sonda</p></body></html>");
  });
  await new Promise(r => servidor.listen(0, "127.0.0.1", r));
  const porta = servidor.address().port;
  const curlHome = join(TMP, "curl");
  const rc = [LIVRE, FECHADO].map(h => `resolve = "${h}:${porta}:127.0.0.1"`).join("\n") + "\n";
  (await import("node:fs")).mkdirSync(curlHome, { recursive: true });
  for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(curlHome, n), rc);
  process.env.CURL_HOME = curlHome;

  // a politica real, com a pausa minima a 0 (so a sonda)
  const polF = join(dirname(TRANSPORTE), "..", "regras", "POLITICA-CORTESIA-ADAPTATIVA.json");
  const pol = JSON.parse(readFileSync(polF, "utf8"));
  for (const c of ["SITE", "PLATAFORMA_GRANDE"]) pol.CLASSES[c].PAUSA_MINIMA_S = 0;
  writeFileSync(join(TMP, "politica.json"), JSON.stringify(pol));
  process.env.SINTONIA_CORTESIA_POLITICA = join(TMP, "politica.json");

  // o livro: FECHADO ja deu 2 sinais agora (pausa de 24 h)
  const livro = join(TMP, "LIVRO-CORTESIA.ndjson");
  const agora = Date.now() / 1000;
  writeFileSync(livro, [1, 2].map(i => JSON.stringify({ DOMINIO: FECHADO, EM: agora - 10 + i, LINHA: "SONDA", MARCAS: [],
    RUN_ID: "SONDA", SINAIS: ["HTTP_429"], STATUS: 429, TIPO: "RESPOSTA" })).join("\n") + "\n");
  process.env.SINTONIA_CORTESIA_LIVRO = livro;
  process.env.SINTONIA_LINHA = "SITES";

  const M = await import(pathToFileURL(TRANSPORTE).href);
  if (typeof M.baixarParaSonda !== "function") {
    dizer(false, "o transporte nao exporta baixarParaSonda (nao se pode medir)");
    process.exitCode = 0;
  } else {
    const a = await M.baixarParaSonda(`http://${LIVRE}:${porta}/pagina`, { runId: "SONDA-A" });
    const nB0 = PEDIDOS.length;
    const b = await M.baixarParaSonda(`http://${FECHADO}:${porta}/pagina`, { runId: "SONDA-B" });
    const ev = existsSync(livro) ? readFileSync(livro, "utf8").split(/\r?\n/).filter(Boolean).map(l => JSON.parse(l)) : [];
    const pedA = PEDIDOS.filter(p => p.host === LIVRE);
    const resA = ev.filter(e => e.DOMINIO === LIVRE && e.TIPO === "RESERVA").map(e => e.EM).sort((x, y) => x - y);
    const respA = ev.filter(e => e.DOMINIO === LIVRE && e.TIPO === "RESPOSTA").map(e => e.EM).sort((x, y) => x - y);
    const pedB = PEDIDOS.slice(nB0).filter(p => p.host === FECHADO);
    // cada pedido i chegou DEPOIS da reserva i e ANTES da resposta i ser registada
    const ordem = pedA.every((p, i) => resA[i] !== undefined && resA[i] <= p.t && respA[i] !== undefined && respA[i] >= p.t);
    const medido = { PEDIDOS_A: pedA.length, RESERVAS_A: resA.length, RESPOSTAS_A: respA.length, ORDEM_A: ordem,
                     STATUS_A: a?.status ?? null, PEDIDOS_B: pedB.length, RECUSA_B: b?.recusado ?? null };
    let porque = null;
    if (pedA.length < 1) porque = "A: nenhum pedido chegou ao servidor (o transporte nao pediu)";
    else if (resA.length !== pedA.length) porque = `A: ${pedA.length} pedidos no servidor, ${resA.length} reservas no livro`;
    else if (respA.length !== pedA.length) porque = `A: ${pedA.length} pedidos no servidor, ${respA.length} respostas no livro`;
    else if (!ordem) porque = "A: um pedido chegou antes da sua reserva (ou sem resposta registada)";
    else if (pedB.length !== 0) porque = `B: o livro dizia PAUSADO e ${pedB.length} pedido(s) sairam`;
    dizer(porque === null, porque ?? `A: ${pedA.length} pedidos = ${resA.length} reservas antes + ${respA.length} respostas; B: 0 pedidos com o dominio pausado (${medido.RECUSA_B})`, medido);
  }
} catch (e) {
  dizer(false, `SONDA_FALHOU: ${e.message}`);
} finally {
  if (servidor) servidor.close();
  rmSync(TMP, { recursive: true, force: true });
}
