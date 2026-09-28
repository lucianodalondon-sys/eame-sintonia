// D124-REBASE · O TRANSPORTE NODE CONTRA UM SERVIDOR LOCAL — o que o verificador independente (28/09) achou.
//
//     node provas/teto_adaptativo/transporte_rebase_local.mjs
//
// ZERO rede externa: proxy de saida para uma porta fechada; os nomes `*-rebase.test` (cada um o seu dominio
// registavel) resolvem para um
// servidor em 127.0.0.1 pelo `_curlrc` de um CURL_HOME temporario. Quem conta os pedidos e o SERVIDOR.
// Este modulo NAO depende de `provas/cortesia_http_local.mjs` (o verificador mediu um mutante que so esse
// modulo apanhava, e ele estava vermelho): cada caso aqui corre sozinho.
//
//   R1  robots PROIBE o caminho de uma materia        -> ZERO pedidos a ela; a livre vem (sem livro E com livro)
//   R2  Crawl-delay 6 MAIOR do que a pausa da classe  -> cada intervalo >= 6 s (a pausa SITE da politica e 5 s)
//   R3  429 + Retry-After                             -> o livro regista RETRY_AFTER com os segundos, lidos do `-D`
//   R4  200 + cf-mitigated: challenge                 -> o livro regista PAGINA_DE_DESAFIO, lido do `-D`
//   R5  R3/R4 com um curl que devolve %header{} VAZIO  -> os sinais continuam la (o curl 7.83 do System32)
//   R6  SEM livro: 8 materias anunciadas              -> o servidor recebe o SEM_LIVRO da politica (5), nunca 40
//   R7  o `-w` do transporte nao pede %header{}         -> a medida nao depende da versao do curl
//   R8  2.a corrida com livro: o robots vem do livro de 24 h (FEED-LIGADO) -> sem ReferenceError, e obedecido
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, writeFileSync, existsSync, mkdirSync, chmodSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "rebase-transporte-"));
process.env.ITALY_OPS_ROOT = join(RAIZ, "ops");
for (const k of Object.keys(process.env)) if (k.startsWith("SINTONIA_")) delete process.env[k];
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
const NOMES = ["robots-rebase.test", "crawl-rebase.test", "sinal-rebase.test", "desafio-rebase.test", "semlivro-rebase.test"];
process.env.NO_PROXY = process.env.no_proxy = ["127.0.0.1", "localhost", ...NOMES].join(",");

const POLITICA = JSON.parse(readFileSync(new URL("../../regras/POLITICA-CORTESIA-ADAPTATIVA.json", import.meta.url), "utf8"));
const PAUSA_SITE_S = POLITICA.CLASSES.SITE.PAUSA_MINIMA_S;
const SEM_LIVRO = POLITICA.CLASSES.SITE.MINIMO_24H;

// ── o servidor ──
const PEDIDOS = [];
let ROBOTS = "";                                   // texto do robots de cada host (404 se vazio)
const INDICE = ["m-uno", "m-due", "m-tre", "m-quattro", "m-cinque", "m-sei", "m-sette", "m-otto"];
const servidor = createServer((req, res) => {
  const host = String(req.headers.host || "").split(":")[0];
  PEDIDOS.push({ host, p: req.url, t: Date.now() });
  if (req.url === "/robots.txt") {
    if (host === "robots-rebase.test") { res.setHeader("Content-Type", "text/plain"); res.end("User-agent: *\nDisallow: /news/proibida-\n"); return; }
    if (host === "crawl-rebase.test") { res.setHeader("Content-Type", "text/plain"); res.end("User-agent: *\nCrawl-delay: 6\n"); return; }
    res.writeHead(404); res.end("non trovato"); return;
  }
  if (host === "sinal-rebase.test") { res.writeHead(429, { "Retry-After": "120", "Content-Type": "text/plain" }); res.end("troppe richieste"); return; }
  if (host === "desafio-rebase.test") { res.writeHead(200, { "cf-mitigated": "challenge", "Content-Type": "text/html" }); res.end("<html><body>ok</body></html>"); return; }
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  if (req.url === "/news/") {
    const lista = host === "robots-rebase.test" ? ["proibida-uno", "livre-uno"] : INDICE;
    res.end(`<!DOCTYPE html><html><body>${lista.map(s => `<a href="/news/${s}/">${s}</a>`).join("\n")}<p>${"testo ".repeat(200)}</p></body></html>`);
    return;
  }
  res.end(`<!DOCTYPE html><html><head><title>${req.url}</title></head><body><h1>${req.url}</h1><p>${"Testo dell'articolo. ".repeat(80)}</p></body></html>`);
});
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const PORTA = servidor.address().port;
const CURL_HOME = join(RAIZ, "curl");
mkdirSync(CURL_HOME, { recursive: true });
for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(CURL_HOME, n), NOMES.map(h => `resolve = "${h}:${PORTA}:127.0.0.1"`).join("\n") + "\n");
process.env.CURL_HOME = CURL_HOME;

// ── o curl que imita o 7.83 (so fora do Windows: la o execFile nao corre um script) ──
// Recebe os argumentos do transporte, apaga cada `%header{...}` (o 7.83 devolve-o vazio), anota os argumentos
// e chama o curl verdadeiro.
const CURL_VERDADEIRO = process.platform === "win32" ? null : execFileSync("sh", ["-c", "command -v curl"], { encoding: "utf8" }).trim();
const ARGS_F = join(RAIZ, "curl-args.ndjson");
function ligarCurlAntigo() {
  if (!CURL_VERDADEIRO) return false;
  const bin = join(RAIZ, "bin");
  mkdirSync(bin, { recursive: true });
  writeFileSync(join(bin, "curl"), `#!/usr/bin/env node
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const a = process.argv.slice(2).map(x => x.replace(/%header\\{[^}]*\\}/g, ""));
fs.appendFileSync(${JSON.stringify(ARGS_F)}, JSON.stringify(process.argv.slice(2)) + "\\n");
const r = spawnSync(${JSON.stringify(CURL_VERDADEIRO)}, a, { stdio: "inherit" });
process.exit(r.status === null ? 1 : r.status);
`);
  chmodSync(join(bin, "curl"), 0o755);
  process.env.PATH = `${bin}:${process.env.PATH}`;
  return true;
}

// a politica real com a pausa minima a 0 — so para R3/R4/R5 (medem sinais, nao a pausa)
const POL_SEM_PAUSA = join(RAIZ, "politica-sem-pausa.json");
{ const p = JSON.parse(JSON.stringify(POLITICA)); for (const c of ["SITE", "PLATAFORMA_GRANDE"]) p.CLASSES[c].PAUSA_MINIMA_S = 0;
  writeFileSync(POL_SEM_PAUSA, JSON.stringify(p)); }

const M = await import("../../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../../regras/italy_contracts.mjs");
const FONTE = "IT-T10-018";
const ORIGINAL = { ACQUISITION: CONTRACTS[FONTE].ACQUISITION, RECOLLECTION: CONTRACTS[FONTE].RECOLLECTION,
                   CANONICAL_ENTRY_URL: CONTRACTS[FONTE].CANONICAL_ENTRY_URL };
function apontar(host) {
  const base = `http://${host}:${PORTA}`;
  CONTRACTS[FONTE].ACQUISITION = { ...ORIGINAL.ACQUISITION, STRATEGY: "HTML_LINK_DISCOVERY", INDEX_URL: `${base}/news/`, MAX_TARGETS: 30,
    LINK_PATTERN: String.raw`^http://[a-z]+-rebase\.test:\d+/news/[a-z0-9]+(?:-[a-z0-9]+)+/?$` };
  CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `${base}/news/`;
  CONTRACTS[FONTE].RECOLLECTION = undefined;
}
async function rodada(host, nome) {
  apontar(host);
  const antes = PEDIDOS.length;
  const { resumo } = await M.executarRodada({ runId: `PROVA_REBASE_${nome}_${Date.now()}`, apenas: [FONTE], pularParse: true, nota: nome });
  const feitos = PEDIDOS.slice(antes).filter(p => p.host === host);
  return { resumo, feitos, caminhos: feitos.map(x => x.p) };
}
const eventos = f => existsSync(f) ? readFileSync(f, "utf8").split(/\r?\n/).filter(Boolean).map(l => JSON.parse(l)) : [];
const intervalos = fs => fs.slice(1).map((x, i) => x.t - fs[i].t);

let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};

try {
  console.log(`(servidor 127.0.0.1:${PORTA} · raiz ${RAIZ})`);

  // R1 — robots PROIBE, sem livro e com livro
  process.env.SINTONIA_PAUSA_POR_HOST_S = "0";
  const r1a = await rodada("robots-rebase.test", "R1a");
  t("R1 sem livro: ZERO pedidos ao caminho proibido pelo robots; a materia livre vem", () => {
    assert.ok(!r1a.caminhos.some(p => p.startsWith("/news/proibida-")), JSON.stringify(r1a.caminhos));
    assert.ok(r1a.caminhos.includes("/news/livre-uno/"), JSON.stringify(r1a.caminhos));
    assert.equal(r1a.resumo.contadores.COURTESY_REFUSALS.ROBOTS_PROIBE, 1);
  });
  process.env.SINTONIA_CORTESIA_LIVRO = join(RAIZ, "livro-r1.ndjson");
  process.env.SINTONIA_CORTESIA_POLITICA = POL_SEM_PAUSA;
  const r1b = await rodada("robots-rebase.test", "R1b");
  t("R1 com livro: ZERO pedidos ao caminho proibido; nenhuma reserva gasta nele", () => {
    assert.ok(!r1b.caminhos.some(p => p.startsWith("/news/proibida-")), JSON.stringify(r1b.caminhos));
    assert.ok(!eventos(process.env.SINTONIA_CORTESIA_LIVRO).some(e => String(e.URL || "").includes("proibida")));
  });
  const r1c = await rodada("robots-rebase.test", "R1c");
  t("R8: a 2.a corrida le o robots do livro de 24 h (FEED-LIGADO) sem rebentar, e continua a obedecer-lhe", () => {
    assert.ok(!r1c.caminhos.includes("/robots.txt"), JSON.stringify(r1c.caminhos));
    assert.ok(!r1c.caminhos.some(p => p.startsWith("/news/proibida-")), JSON.stringify(r1c.caminhos));
    assert.match(r1c.resumo.CORTESIA.ROBOTS[`http://robots-rebase.test:${PORTA}`].ORIGEM, /^LIVRO_24H/);
  });
  delete process.env.SINTONIA_CORTESIA_LIVRO; delete process.env.SINTONIA_CORTESIA_POLITICA;
  delete process.env.SINTONIA_PAUSA_POR_HOST_S;

  // R2 — Crawl-delay 6 > pausa da classe (5 s), SEM pausa declarada
  const r2 = await rodada("crawl-rebase.test", "R2");
  t(`R2: Crawl-delay 6 manda sobre a pausa da classe SITE (${PAUSA_SITE_S} s): cada intervalo >= 6 s`, () => {
    assert.ok(6 > PAUSA_SITE_S, "so prova se o Crawl-delay for MAIOR do que a pausa da classe");
    assert.ok(r2.feitos.length >= 3, JSON.stringify(r2.caminhos));
    const iv = intervalos(r2.feitos);
    assert.ok(iv.every(ms => ms >= 5990), `intervalos ${JSON.stringify(iv)} ms`);
    assert.equal(r2.resumo.CORTESIA.ROBOTS[`http://crawl-rebase.test:${PORTA}`].CRAWL_DELAY, 6);
  });

  // R3/R4 — sinais lidos do `-D` (curl verdadeiro), depois R5 com o curl que imita o 7.83
  async function sinais(tag) {
    const livro = join(RAIZ, `livro-${tag}.ndjson`);
    process.env.SINTONIA_CORTESIA_LIVRO = livro;
    process.env.SINTONIA_CORTESIA_POLITICA = POL_SEM_PAUSA;
    const a = await M.baixarParaSonda(`http://sinal-rebase.test:${PORTA}/pagina`, { runId: `R-${tag}-429` });
    const b = await M.baixarParaSonda(`http://desafio-rebase.test:${PORTA}/pagina`, { runId: `R-${tag}-cf` });
    delete process.env.SINTONIA_CORTESIA_LIVRO; delete process.env.SINTONIA_CORTESIA_POLITICA;
    const ev = eventos(livro).filter(e => e.TIPO === "RESPOSTA" && String(e.URL || "").endsWith("/pagina"));
    return { a, b, r429: ev.find(e => e.DOMINIO === "sinal-rebase.test"), rcf: ev.find(e => e.DOMINIO === "desafio-rebase.test") };
  }
  const s1 = await sinais("R3");
  t("R3: 429 + Retry-After 120 -> RETRY_AFTER no livro, 120 s", () => {
    assert.equal(s1.a.status, 429);
    assert.ok(s1.r429 && s1.r429.SINAIS.includes("RETRY_AFTER"), JSON.stringify(s1.r429));
    assert.equal(s1.r429.RETRY_AFTER_S, 120);
  });
  t("R4: cf-mitigated: challenge -> PAGINA_DE_DESAFIO no livro", () => {
    assert.ok(s1.rcf && s1.rcf.SINAIS.includes("PAGINA_DE_DESAFIO"), JSON.stringify(s1.rcf));
  });
  const antigo = ligarCurlAntigo();
  if (antigo) {
    const s2 = await sinais("R5");
    t("R5: com um curl que devolve %header{} VAZIO (o 7.83), Retry-After e cf-mitigated continuam medidos", () => {
      assert.ok(s2.r429 && s2.r429.SINAIS.includes("RETRY_AFTER") && s2.r429.RETRY_AFTER_S === 120, JSON.stringify(s2.r429));
      assert.ok(s2.rcf && s2.rcf.SINAIS.includes("PAGINA_DE_DESAFIO"), JSON.stringify(s2.rcf));
    });
    t("R7: o `-w` do transporte nao pede %header{} e todo pedido leva `-D`", () => {
      const chamadas = readFileSync(ARGS_F, "utf8").split("\n").filter(Boolean).map(l => JSON.parse(l));
      assert.ok(chamadas.length >= 2, String(chamadas.length));
      for (const a of chamadas) {
        assert.ok(!a.some(x => x.includes("%header")), JSON.stringify(a));
        assert.ok(a.includes("-D"), JSON.stringify(a));
      }
    });
  } else {
    console.log("  --    R5/R7: NAO_SE_APLICA neste sistema (win32: o execFile nao corre o curl de imitacao)");
  }

  // R6 — sem livro: o SEM_LIVRO da politica, nunca o inicial 40
  process.env.SINTONIA_PAUSA_POR_HOST_S = "0";
  const r6 = await rodada("semlivro-rebase.test", "R6");
  delete process.env.SINTONIA_PAUSA_POR_HOST_S;
  t(`R6: sem livro, 8 materias anunciadas -> o servidor recebe ${SEM_LIVRO} pedidos (SEM_LIVRO = MINIMO da classe), nao 10`, () => {
    assert.equal(POLITICA.SEM_LIVRO.TETO_POR_CORRIDA, "MINIMO_24H");
    assert.ok(SEM_LIVRO < POLITICA.CLASSES.SITE.ORCAMENTO_INICIAL_24H);
    assert.equal(r6.feitos.length, SEM_LIVRO, JSON.stringify(r6.caminhos));
    assert.equal(r6.resumo.CORTESIA.TETO_ADAPTATIVO.LIVRO, null);
  });
} finally {
  Object.assign(CONTRACTS[FONTE], ORIGINAL);
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
}
console.log(`\nTRANSPORTE_REBASE_LOCAL · passou=${passou} FALHAS=${falhou}`);
process.exit(falhou ? 1 : 0);
