// A CORTESIA DENTRO DO TRANSPORTE — PROVADA PELO CURL, CONTRA UM SERVIDOR LOCAL.
//
//     node provas/cortesia_http_local.mjs
//
// A5 (23/09): o robots.txt, a pausa entre pedidos ao mesmo host e o teto de
// pedidos por site vivem agora em `baixar()` (coleta/italy_pilot_collect.mjs),
// e nao no condutor da micro. Esta prova liga o transporte de verdade — o curl
// — contra um servidor HTTP em 127.0.0.1. Quem conta os pedidos e o SERVIDOR:
// um pedido que a cortesia recusa nao chega aqui, e e isso que se mede.
//
// ZERO REDE EXTERNA, como nas provas da recollection: proxy de saida para uma
// porta fechada, so 127.0.0.1/localhost fora dele; `EGRESS_IP = NAO SEI`.
//
//   C1  robots proibe o caminho de UMA materia  -> 0 pedidos a ela; a outra vem; robots lido 1 vez
//   C2  robots proibe o indice                  -> 0 pedidos ao indice; fonte UNKNOWN; nada no livro
//   C3  pausa por omissao (1,0 s)               -> intervalo medido no servidor >= 1 s
//   C4  pausa configurada (2 s) e Crawl-delay 3 -> >= 2 s; e o Crawl-delay manda quando e maior
//   C5  teto por omissao (5, D7)                -> 6 materias anunciadas, 5 pedidos no servidor
//   C6  teto configurado (3)                    -> 3 pedidos
//   C7  robots ilegivel (HTML, 500)             -> so o robots e pedido
//   C8  robots indisponivel (ligacao cortada)   -> so o robots; e NAO fica em cache
//   C9  robots 404                              -> sem ficheiro = sem proibicao
//   C9b robots 403 (D34, RFC 9309)              -> qualquer 4xx = indisponivel = sem proibicao
//   C10 redireccionamento                       -> o salto pede licenca: destino proibido nunca e pedido
//   C11 o leitor do robots (sem rede)           -> mais longo vence, Allow no empate, `$`, grupo proprio
//   C12 configuracao invalida                   -> falha alto
//   C13 www.site -> site (o caso Villoresi)     -> teto e pausa contam o SITE; robots do destino lido 1 vez
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, existsSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "cortesia-http-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
process.env.NO_PROXY = process.env.no_proxy = "127.0.0.1,localhost,cortesia.test,www.cortesia.test";
for (const k of ["SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST"]) delete process.env[k];

// ── O SERVIDOR ──────────────────────────────────────────────────────────────
const enchimento = "<p>" + "Testo dell'articolo. ".repeat(80) + "</p>";
let ROBOTS = { modo: "404", texto: "" };      // 404 · texto · html · 500 · cortar
let INDICE = [];                              // slugs anunciados no indice
const SALTOS = {};                            // "/news/x/" -> destino do 301
const PEDIDOS = [];                           // { p, t } pela ordem de chegada
const servidor = createServer((req, res) => {
  const p = req.url;
  const host = String(req.headers.host || "").split(":")[0];
  PEDIDOS.push({ p, t: Date.now(), host });
  // C13: `www.cortesia.test` manda TUDO (robots incluido) para `cortesia.test`.
  if (host === "www.cortesia.test") {
    res.writeHead(301, { Location: `http://cortesia.test:${servidor.address().port}${p}` }); res.end(); return;
  }
  if (p === "/robots.txt") {
    if (ROBOTS.modo === "cortar") { req.socket.destroy(); return; }
    if (ROBOTS.modo === "404") { res.writeHead(404); res.end("non trovato"); return; }
    if (ROBOTS.modo === "403") { res.writeHead(403); res.end("vietato"); return; }
    if (ROBOTS.modo === "500") { res.writeHead(500); res.end("errore"); return; }
    if (ROBOTS.modo === "html") { res.setHeader("Content-Type", "text/html"); res.end("<!DOCTYPE html><html><body>Benvenuti</body></html>"); return; }
    res.setHeader("Content-Type", "text/plain"); res.end(ROBOTS.texto); return;
  }
  if (SALTOS[p]) { res.writeHead(301, { Location: SALTOS[p] }); res.end(); return; }
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  if (p === "/news/") {
    res.end(`<!DOCTYPE html><html><body>${INDICE.map(s => `<a href="/news/${s}/">${s}</a>`).join("\n")}${enchimento}</body></html>`);
    return;
  }
  if (/^\/(news|altrove)\/[a-z0-9-]+\/?$/.test(p)) {
    res.end(`<!DOCTYPE html><html><head><title>${p}</title></head><body><h1>${p}</h1>${enchimento}</body></html>`);
    return;
  }
  res.writeHead(404); res.end("non trovato");
});
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${servidor.address().port}`;
// Os dois nomes do C13 resolvem para este servidor pelo `_curlrc` (o mecanismo do
// ensaio offline), num CURL_HOME so desta prova. As aspas sao obrigatorias.
const CURL_HOME = mkdtempSync(join(tmpdir(), "cortesia-curl-"));
const rc = ["www.cortesia.test", "cortesia.test"].map(h => `resolve = "${h}:${servidor.address().port}:127.0.0.1"`).join("\n") + "\n";
for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(CURL_HOME, n), rc);
process.env.CURL_HOME = CURL_HOME;

const M = await import("../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../regras/italy_contracts.mjs");
const FONTE = "IT-T10-018";
assert.equal(CONTRACTS[FONTE].ACQUISITION.STRATEGY, "HTML_LINK_DISCOVERY");
const ORIGINAL = { ACQUISITION: CONTRACTS[FONTE].ACQUISITION, RECOLLECTION: CONTRACTS[FONTE].RECOLLECTION,
                   CANONICAL_ENTRY_URL: CONTRACTS[FONTE].CANONICAL_ENTRY_URL };
CONTRACTS[FONTE].ACQUISITION = { ...ORIGINAL.ACQUISITION, INDEX_URL: `${BASE}/news/`, MAX_TARGETS: 30,
  LINK_PATTERN: String.raw`^http://127\.0\.0\.1:\d+/news/[a-z0-9]+(?:-[a-z0-9]+)+/?$` };
CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `${BASE}/news/`;
CONTRACTS[FONTE].RECOLLECTION = undefined;

const livro = () => {
  const f = join(RAIZ, "data/collection-ledger/italy/observations.ndjson");
  return existsSync(f) ? readFileSync(f, "utf8").split("\n").filter(Boolean).map(JSON.parse) : [];
};
async function rodada(nome) {
  const antes = PEDIDOS.length, linhas = livro().length;
  const { resumo, detalhes } = await M.executarRodada({ runId: `PROVA_CORTESIA_${nome}_${Date.now()}`,
    apenas: [FONTE], pularParse: true, nota: `prova cortesia ${nome}` });
  const feitos = PEDIDOS.slice(antes);
  return { c: resumo.contadores, resumo, detalhes, feitos, caminhos: feitos.map(x => x.p),
           robots: feitos.filter(x => x.p === "/robots.txt").length, novasNoLivro: livro().slice(linhas) };
}
const intervalos = (feitos) => feitos.slice(1).map((x, i) => x.t - feitos[i].t);

let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};
const censo = [];
const anota = (nome, r) => censo.push(`  ${nome.padEnd(4)} pedidos=${r.feitos.length} robots=${r.robots}` +
  ` caminhos=${JSON.stringify(r.caminhos)} recusas=${JSON.stringify(r.c.COURTESY_REFUSALS)}` +
  ` intervalos_ms=${JSON.stringify(intervalos(r.feitos))}`);

try {
  console.log(`\n(servidor ${BASE} · raiz ${RAIZ})`);

  console.log("\n══ C1 · o robots proibe o caminho de uma materia ═══════════════");
  ROBOTS = { modo: "texto", texto: "User-agent: *\nDisallow: /news/proibida-\n" };
  INDICE = ["proibida-uno", "livre-uno"];
  const c1 = await rodada("C1"); anota("C1", c1);
  t("C1: ZERO pedidos ao caminho proibido; a materia livre vem", () => {
    assert.ok(!c1.caminhos.some(p => p.startsWith("/news/proibida-")), JSON.stringify(c1.caminhos));
    assert.ok(c1.caminhos.includes("/news/livre-uno/"), JSON.stringify(c1.caminhos));
  });
  t("C1: robots lido UMA vez na corrida (cache por corrida), antes de tudo", () => {
    assert.equal(c1.robots, 1); assert.equal(c1.caminhos[0], "/robots.txt");
  });
  t("C1: a recusa e contada com o motivo, e NAO e observacao nem falha", () => {
    assert.equal(c1.c.COURTESY_REFUSALS.ROBOTS_PROIBE, 1);
    assert.equal(c1.c.DETAIL_DEFERRED_BY_COURTESY, 1);
    assert.equal(c1.c.DETAIL_REQUESTS, 1, "so a materia livre foi pedida");
    assert.equal(c1.c.DETAIL_NEW, 1);
    assert.equal(c1.c.INDEX_REQUESTS, 1);
    assert.equal(c1.c.ROBOTS_REQUESTS, 1);
    assert.equal(c1.c.HEALTHY, 1, JSON.stringify(c1.c));
    assert.ok(!c1.novasNoLivro.some(l => String(l.SOURCE_URL || "").includes("proibida")),
      "a materia recusada nao pode ir ao livro");
    const d = c1.detalhes.find(x => String(x.SOURCE_URL || "").includes("proibida"));
    assert.equal(d?.DECISAO, "DEFERRED_BY_COURTESY");
    assert.equal(d?.MOTIVO, "ROBOTS_PROIBE");
  });
  t("C1: o resumo mostra a cortesia (robots, pedidos por host, recusas)", () => {
    const k = c1.resumo.CORTESIA;
    assert.equal(k.ROBOTS[BASE].ESTADO, "LIDO");
    assert.equal(k.PEDIDOS_POR_HOST["127.0.0.1"], c1.feitos.length);
    assert.equal(k.RECUSAS.length, 1);
    assert.deepEqual(k.EXCECOES, []);
  });
  t("zero rede externa: EGRESS_IP = NAO SEI", () => assert.equal(c1.resumo.EGRESS_IP, "NAO SEI"));

  console.log("\n══ C2 · o robots proibe o indice ════════════════════════════════");
  ROBOTS = { modo: "texto", texto: "User-agent: *\nDisallow: /news/\n" };
  INDICE = ["uma-due"];
  const c2 = await rodada("C2"); anota("C2", c2);
  t("C2: ZERO pedidos ao indice (so o robots foi pedido)", () => {
    assert.deepEqual(c2.caminhos, ["/robots.txt"]);
  });
  t("C2: a fonte fica UNKNOWN (nao se olhou), nao FAILED, e nada vai ao livro", () => {
    assert.equal(c2.c.UNKNOWN, 1); assert.equal(c2.c.FAILED, 0);
    assert.equal(c2.c.DISCOVERY_NOT_REQUESTED_BY_COURTESY, 1);
    assert.equal(c2.c.COURTESY_REFUSALS.ROBOTS_PROIBE, 1);
    assert.equal(c2.c.INDEX_REQUESTS, 0);
    assert.equal(c2.novasNoLivro.length, 0, JSON.stringify(c2.novasNoLivro));
  });

  console.log("\n══ C3 · a pausa por omissao ═════════════════════════════════════");
  ROBOTS = { modo: "404" };
  INDICE = ["tre-a", "tre-b"];
  const c3 = await rodada("C3"); anota("C3", c3);
  t("C3: robots + indice + 2 materias, cada pedido >= 1,0 s depois do anterior", () => {
    assert.equal(c3.feitos.length, 4, JSON.stringify(c3.caminhos));
    const iv = intervalos(c3.feitos);
    assert.ok(iv.every(ms => ms >= 990), `intervalos ${JSON.stringify(iv)} ms`);
    assert.equal(c3.resumo.CORTESIA.PAUSA_MINIMA_S, 1);
  });

  console.log("\n══ C4 · a pausa configurada, e o Crawl-delay ════════════════════");
  process.env.SINTONIA_PAUSA_POR_HOST_S = "2";
  INDICE = ["quattro-a"];
  const c4 = await rodada("C4"); anota("C4", c4);
  t("C4: com SINTONIA_PAUSA_POR_HOST_S=2, cada intervalo >= 2 s", () => {
    const iv = intervalos(c4.feitos);
    assert.equal(c4.feitos.length, 3, JSON.stringify(c4.caminhos));
    assert.ok(iv.every(ms => ms >= 1990), `intervalos ${JSON.stringify(iv)} ms`);
    assert.equal(c4.resumo.CORTESIA.PAUSA_MINIMA_S, 2);
  });
  delete process.env.SINTONIA_PAUSA_POR_HOST_S;
  ROBOTS = { modo: "texto", texto: "User-agent: *\nCrawl-delay: 3\nDisallow: /privato/\n" };
  INDICE = ["cinque-a"];
  const c4b = await rodada("C4b"); anota("C4b", c4b);
  t("C4b: Crawl-delay 3 no robots manda sobre a pausa de 1 s (depois de o ler)", () => {
    const iv = intervalos(c4b.feitos);
    assert.equal(c4b.feitos.length, 3, JSON.stringify(c4b.caminhos));
    assert.ok(iv.every(ms => ms >= 2990), `intervalos ${JSON.stringify(iv)} ms`);
    assert.equal(c4b.resumo.CORTESIA.ROBOTS[BASE].CRAWL_DELAY, 3);
  });

  console.log("\n══ C5 · o teto por omissao (5 pedidos por site, D7) ═════════════");
  ROBOTS = { modo: "404" };
  INDICE = ["sei-a", "sei-b", "sei-c", "sei-d", "sei-e", "sei-f"];
  const c5 = await rodada("C5"); anota("C5", c5);
  t("C5: 6 materias anunciadas, o servidor recebe EXACTAMENTE 5 pedidos", () => {
    assert.equal(c5.feitos.length, 5, JSON.stringify(c5.caminhos));
    assert.equal(c5.resumo.CORTESIA.TETO_POR_HOST, 5);
    assert.equal(c5.resumo.CORTESIA.PEDIDOS_POR_HOST["127.0.0.1"], 5);
  });
  t("C5: as 3 que ficaram de fora sao adiadas pelo teto, fora do livro", () => {
    assert.equal(c5.c.COURTESY_REFUSALS.TETO_POR_HOST, 3);
    assert.equal(c5.c.DETAIL_DEFERRED_BY_COURTESY, 3);
    assert.equal(c5.c.DETAIL_REQUESTS, 3); assert.equal(c5.c.NEW_DOCUMENTS, 3);
    const adiadas = c5.detalhes.filter(d => d.DECISAO === "DEFERRED_BY_COURTESY").map(d => d.SOURCE_URL);
    assert.ok(!c5.novasNoLivro.some(l => adiadas.includes(l.SOURCE_URL)), "adiada nao e observacao");
  });
  const c5b = await rodada("C5b"); anota("C5b", c5b);
  t("C5b: na corrida seguinte as adiadas voltam a ser pedidas (ADIADO != NUNCA)", () => {
    const pedidas = c5b.caminhos.filter(p => /^\/news\/sei-/.test(p));
    assert.equal(pedidas.length, 3, JSON.stringify(c5b.caminhos));
    assert.equal(c5b.c.SKIPPED_KNOWN, 3);
  });

  console.log("\n══ C6 · o teto configurado ══════════════════════════════════════");
  process.env.SINTONIA_TETO_POR_HOST = "3";
  INDICE = ["sette-a", "sette-b", "sette-c"];
  const c6 = await rodada("C6"); anota("C6", c6);
  t("C6: com SINTONIA_TETO_POR_HOST=3, o servidor recebe 3 pedidos", () => {
    assert.equal(c6.feitos.length, 3, JSON.stringify(c6.caminhos));
    assert.equal(c6.c.COURTESY_REFUSALS.TETO_POR_HOST, 2);
  });
  delete process.env.SINTONIA_TETO_POR_HOST;

  console.log("\n══ C7 · robots ilegivel (HTML e HTTP 500) ═══════════════════════");
  for (const modo of ["html", "500"]) {
    ROBOTS = { modo };
    INDICE = [`otto-${modo}`];
    const c7 = await rodada(`C7${modo}`); anota(`C7${modo}`, c7);
    t(`C7 ${modo}: so o robots e pedido — nao se afirma permissao que nao se leu`, () => {
      assert.deepEqual(c7.caminhos, ["/robots.txt"]);
      assert.equal(c7.c.COURTESY_REFUSALS.ROBOTS_ILEGIVEL, 1);
      assert.equal(c7.c.UNKNOWN, 1); assert.equal(c7.novasNoLivro.length, 0);
    });
  }

  console.log("\n══ C8 · robots indisponivel (a ligacao cai) ═════════════════════");
  ROBOTS = { modo: "cortar" };
  INDICE = ["nove-a"];
  const c8 = await rodada("C8"); anota("C8", c8);
  t("C8: nada alem do robots e pedido, e a recusa diz INDISPONIVEL (nao «o host recusou»)", () => {
    assert.ok(c8.caminhos.every(p => p === "/robots.txt"), JSON.stringify(c8.caminhos));
    assert.equal(c8.c.COURTESY_REFUSALS.ROBOTS_INDISPONIVEL, 1);
    assert.equal(c8.c.UNKNOWN, 1); assert.equal(c8.c.FAILED, 0);
    assert.equal(c8.novasNoLivro.length, 0);
    assert.ok(!(BASE in c8.resumo.CORTESIA.ROBOTS), "INDISPONIVEL nao fica em cache");
  });

  console.log("\n══ C9 · robots 404 = sem proibicao ══════════════════════════════");
  ROBOTS = { modo: "404" };
  INDICE = ["dieci-a"];
  const c9 = await rodada("C9"); anota("C9", c9);
  t("C9: robots 404 deixa passar (indice e materia pedidos)", () => {
    assert.deepEqual(c9.caminhos, ["/robots.txt", "/news/", "/news/dieci-a/"]);
    assert.equal(c9.resumo.CORTESIA.ROBOTS[BASE].ESTADO, "AUSENTE");
  });

  console.log("\n══ C9b · robots 403 = indisponivel = sem proibicao (RFC 9309, D34) ══");
  ROBOTS = { modo: "403" };
  INDICE = ["dieci-b"];
  const c9b = await rodada("C9b"); anota("C9b", c9b);
  t("C9b: robots 403 deixa passar (RFC 9309 §2.3.1.3: qualquer 4xx = indisponivel)", () => {
    assert.deepEqual(c9b.caminhos, ["/robots.txt", "/news/", "/news/dieci-b/"]);
    assert.equal(c9b.resumo.CORTESIA.ROBOTS[BASE].ESTADO, "AUSENTE");
  });

  console.log("\n══ C10 · o redireccionamento pede licenca outra vez ═════════════");
  ROBOTS = { modo: "texto", texto: "User-agent: *\nDisallow: /privato/\n" };
  INDICE = ["salta-privato", "salta-libero"];
  SALTOS["/news/salta-privato/"] = "/privato/segreto";
  SALTOS["/news/salta-libero/"] = "/altrove/arrivo-libero";
  const c10 = await rodada("C10"); anota("C10", c10);
  t("C10: o destino proibido pelo robots NUNCA e pedido", () => {
    assert.ok(!c10.caminhos.some(p => p.startsWith("/privato/")), JSON.stringify(c10.caminhos));
    assert.ok(c10.resumo.CORTESIA.RECUSAS.some(r => r.MOTIVO === "ROBOTS_PROIBE" && r.SALTO === 1));
  });
  t("C10: o salto permitido e seguido e o documento chega", () => {
    assert.ok(c10.caminhos.includes("/altrove/arrivo-libero"), JSON.stringify(c10.caminhos));
    assert.ok(c10.novasNoLivro.some(l => String(l.SOURCE_URL).endsWith("/news/salta-libero/") &&
      ["NEW_DOCUMENT", "BASELINE_DOCUMENT"].includes(l.OBSERVATION_RESULT)),
      JSON.stringify(c10.novasNoLivro.map(l => [l.SOURCE_URL, l.OBSERVATION_RESULT])));
  });
  t("C10: o salto recusado a meio JA bateu a porta — fica como falha de transporte, com o porque", () => {
    const l = c10.novasNoLivro.find(x => String(x.SOURCE_URL).endsWith("/news/salta-privato/"));
    assert.equal(l?.OBSERVATION_RESULT, "TRANSPORT_OR_EMPTY");
    assert.match(String(l?.motivo), /CORTESIA ROBOTS_PROIBE/);
  });

  console.log("\n══ C13 · www.site -> site: o mesmo site, o mesmo teto ═══════════");
  const PORTA = servidor.address().port;
  CONTRACTS[FONTE].ACQUISITION = { ...CONTRACTS[FONTE].ACQUISITION, INDEX_URL: `http://www.cortesia.test:${PORTA}/news/`,
    LINK_PATTERN: String.raw`^http://(www\.)?cortesia\.test:\d+/news/[a-z0-9]+(?:-[a-z0-9]+)+/?$` };
  ROBOTS = { modo: "texto", texto: "User-agent: *\nDisallow: /privato/\n" };
  INDICE = ["tredici-a", "tredici-b", "tredici-c", "tredici-d", "tredici-e", "tredici-f"];
  const c13 = await rodada("C13"); anota("C13", c13);
  const vistos = c13.feitos.map(x => `${x.host}${x.p}`);
  t("C13: www e sem-www sao UM site — o servidor recebe 5 pedidos, nao 5 + 5", () => {
    assert.equal(c13.feitos.length, 5, JSON.stringify(vistos));
    assert.deepEqual(c13.resumo.CORTESIA.PEDIDOS_POR_HOST, { "cortesia.test": 5 });
  });
  t("C13: o robots do destino e lido UMA vez (o salto do robots serve a origem de destino)", () => {
    assert.equal(vistos.filter(v => v === "cortesia.test/robots.txt").length, 1, JSON.stringify(vistos));
  });
  t("C13: a pausa vale entre os dois nomes do mesmo site", () => {
    const iv = intervalos(c13.feitos);
    assert.ok(iv.every(ms => ms >= 990), `intervalos ${JSON.stringify(iv)} ms`);
  });

  console.log("\n══ C11 · o leitor do robots, sem rede ═══════════════════════════");
  t("C11: o caminho mais longo vence; no empate vence Allow; `$` ancora; `*` no meio", () => {
    const g = M.lerRobots("User-agent: *\nDisallow: /a/\nAllow: /a/b\nDisallow: /x\nAllow: /x\nDisallow: /*.pdf$\nDisallow: /q*?s=\n");
    assert.equal(M.robotsPermite(g, "/a/c"), false);
    assert.equal(M.robotsPermite(g, "/a/b/c"), true);
    assert.equal(M.robotsPermite(g, "/x"), true);
    assert.equal(M.robotsPermite(g, "/doc.pdf"), false);
    assert.equal(M.robotsPermite(g, "/doc.pdf?v=1"), true);
    assert.equal(M.robotsPermite(g, "/qualcosa?s=1"), false);
    assert.equal(M.robotsPermite(g, "/robots.txt"), true);
  });
  t("C11: o grupo do nosso agente manda sobre o `*`; sem grupo, tudo permitido; Disallow vazio nao proibe", () => {
    const g = M.lerRobots("User-agent: *\nDisallow: /\n\nUser-agent: Mozilla\nDisallow: /solo/\n");
    assert.equal(M.robotsPermite(g, "/altro"), true);
    assert.equal(M.robotsPermite(g, "/solo/x"), false);
    assert.equal(M.robotsPermite(M.lerRobots("User-agent: Googlebot\nDisallow: /\n"), "/x"), true);
    assert.equal(M.robotsPermite(M.lerRobots("User-agent: *\nDisallow:\n"), "/x"), true);
  });

  console.log("\n══ C12 · configuracao invalida falha alto ═══════════════════════");
  for (const [k, v] of [["SINTONIA_TETO_POR_HOST", "0"], ["SINTONIA_TETO_POR_HOST", "2.5"], ["SINTONIA_PAUSA_POR_HOST_S", "-1"], ["SINTONIA_PAUSA_POR_HOST_S", "x"]]) {
    process.env[k] = v;
    let erro = null;
    try { await M.executarRodada({ runId: `PROVA_CORTESIA_C12_${Date.now()}`, apenas: [FONTE], pularParse: true }); }
    catch (e) { erro = e; }
    delete process.env[k];
    t(`C12: ${k}=${v} recusa arrancar`, () => assert.match(String(erro?.message), /CORTESIA_INVALIDA/));
  }
} finally {
  Object.assign(CONTRACTS[FONTE], ORIGINAL);
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
  rmSync(CURL_HOME, { recursive: true, force: true });
}

console.log("\n── censo (pedidos contados pelo servidor) ──");
for (const l of censo) console.log(l);
console.log(`\nCORTESIA_HTTP_LOCAL · passou=${passou} FALHAS=${falhou}`);
process.exit(falhou ? 1 : 0);
