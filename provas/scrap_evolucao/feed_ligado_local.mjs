// FEED-LIGADO PELO COLETOR DE VERDADE — contra servidores locais, com o livro de 24 h (27/09).
//
//     node provas/scrap_evolucao/feed_ligado_local.mjs
//
// O transporte real (`executarRodada` → `baixar()` → curl) contra um servidor em 127.0.0.1. Quem conta os
// pedidos e o SERVIDOR. Zero rede externa: proxy para uma porta fechada; os nomes resolvem para 127.0.0.1
// por um `_curlrc` so desta prova (o mecanismo de `provas/feed_local.mjs`).
//
// Tres corridas da MESMA fonte, com o livro de 24 h (SINTONIA_TETO_24H) de uma pasta temporaria:
//   corrida 1  robots + feed + 1 materia (so a sem corpo) = 3 pedidos; 2 itens entram BODY_FROM_FEED
//   corrida 2  robots do livro de 24 h (0 pedidos) + feed condicional → 304 (1 pedido) = 4 no total
//   corrida 3  feed mudou (200, 1 pedido) = 5 → a materia nova e RECUSADA pelo teto: o 304 contou
//
//   G1  o teto: o servidor nunca ve mais de 5 pedidos do dominio em 24 h; o livro de 24 h diz o mesmo
//   G2  BODY_FROM_FEED: zero pedidos a materia; rotulo, origem, bytes exactos, nome do ficheiro, FACT_TIME
//   G3  a materia sem corpo continua a ser pedida (e a pagina nao se diz BODY_FROM_FEED)
//   G4  o robots vem do livro de 24 h na corrida 2 (o servidor nao o ve outra vez)
//   G5  o pedido condicional leva If-None-Match; 304 conta no teto e no livro de 24 h
//   G6  as linhas Sitemap: ficam no resumo e nenhum pedido sai por elas
//   G7  robots ILEGIVEL (HTML) nao da permissao, nao vai para o livro de 24 h, e volta a ser pedido
//   G8  uma entrada do livro de robots que nao se entende nao e permissao: pede-se o robots
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "feed-ligado-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
const HOST = "feedligado.test", HOST_MAU = "robotsmau.test", HOST_SUJO = "livrosujo.test";
process.env.NO_PROXY = process.env.no_proxy = ["127.0.0.1", "localhost", HOST, HOST_MAU, HOST_SUJO].join(",");
for (const k of ["SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA"]) delete process.env[k];
process.env.SINTONIA_PAUSA_POR_HOST_S = "0";
const LIVRO24 = join(RAIZ, "TETO-24H.json");
process.env.SINTONIA_TETO_24H = LIVRO24;
// ── D124 (dono, 27/09) — AJUSTE DECLARADO (D124-REBASE, 28/09) ─────────────────────────────────────────
// O livro de 24 h passou a ser o da CORTESIA ADAPTATIVA (ndjson de eventos; o orcamento do dominio e o
// vigente da politica, SITE comeca em 40, e a reserva respeita a pausa minima da classe). Esta prova mede
// que o 304 CONTA no orcamento de 24 h e que o teto fecha: fa-lo com o orcamento INICIAL de 5 declarado numa
// copia da politica (e a pausa da classe a 0, como SINTONIA_PAUSA_POR_HOST_S=0 ja fazia no transporte), e
// conta as RESERVAS lendo os eventos. Nenhuma asserção afrouxada: o 5 passou a ser declarado aqui.
{
  const pol = JSON.parse(readFileSync(new URL("../../regras/POLITICA-CORTESIA-ADAPTATIVA.json", import.meta.url), "utf8"));
  pol.CLASSES.SITE.ORCAMENTO_INICIAL_24H = 5;
  pol.CLASSES.SITE.PAUSA_MINIMA_S = 0;
  writeFileSync(join(RAIZ, "POLITICA-CORTESIA-5.json"), JSON.stringify(pol));
  process.env.SINTONIA_CORTESIA_POLITICA = join(RAIZ, "POLITICA-CORTESIA-5.json");
  delete process.env.SINTONIA_CORTESIA_LIVRO;
}

const PEDIDOS = [];                 // { host, url, inm }
let PORTA = 0, VERSAO_DO_FEED = 1;
const CORPO_1 = `<p>La mosca dell'olivo: catture in aumento.</p><p style="display:none">nascosto</p><script>var t=1;</script>`;
const CORPO_2 = `<p>Peronospora, allerta nei vigneti &amp; nei frutteti.</p>`;
const u = (h, p) => `http://${h}:${PORTA}${p}`;
const feed = () => `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel>
${VERSAO_DO_FEED >= 2 ? `<item><title>Nuovo</title><link>${u(HOST, "/news/articolo-nuovo-senza-corpo/")}</link><pubDate>Sat, 26 Sep 2026 07:00:00 +0000</pubDate></item>` : ""}
<item><title>Mosca</title><link>${u(HOST, "/news/mosca-olivo-catture/")}</link><pubDate>Thu, 24 Sep 2026 07:30:00 +0000</pubDate><content:encoded><![CDATA[${CORPO_1}]]></content:encoded></item>
<item><title>Peronospora</title><link>${u(HOST, "/news/peronospora-allerta/")}</link><pubDate>Wed, 23 Sep 2026 09:00:00 +0000</pubDate><content:encoded><![CDATA[${CORPO_2}]]></content:encoded></item>
<item><title>Solo link</title><link>${u(HOST, "/news/articolo-solo-link/")}</link><pubDate>Tue, 22 Sep 2026 09:00:00 +0000</pubDate><description>riassunto</description></item>
</channel></rss>`;
const pagina = (p) => `<!DOCTYPE html><html><head><title>${p}</title></head><body><article><h1>${p}</h1>${"<p>Testo. </p>".repeat(80)}</article></body></html>`;
const servidor = createServer((req, res) => {
  const host = String(req.headers.host || "").split(":")[0];
  PEDIDOS.push({ host, url: req.url, inm: req.headers["if-none-match"] || null });
  if (host === HOST && req.url === "/robots.txt") {
    res.setHeader("Content-Type", "text/plain");
    res.end(`User-agent: *\nDisallow: /privato/\n\nSitemap: ${u(HOST, "/sitemap.xml")}\nSitemap: ${u(HOST, "/news-sitemap.xml")}\n`);
    return;
  }
  if (host === HOST && req.url === "/feed/") {
    const etag = `"feed-v${VERSAO_DO_FEED}"`;
    if (req.headers["if-none-match"] === etag) { res.writeHead(304, { ETag: etag }); res.end(); return; }
    res.writeHead(200, { "Content-Type": "application/rss+xml; charset=utf-8", ETag: etag });
    res.end(feed());
    return;
  }
  if (host === HOST && /^\/news\/[a-z0-9-]+\/$/.test(req.url)) {
    res.setHeader("Content-Type", "text/html; charset=utf-8"); res.end(pagina(req.url)); return;
  }
  // robots que vem em HTML (o CMS a responder a tudo com a pagina inicial): ILEGIVEL
  if ((host === HOST_MAU || host === HOST_SUJO) && req.url === "/robots.txt") {
    res.setHeader("Content-Type", "text/html"); res.end("<!DOCTYPE html><html><body>home</body></html>"); return;
  }
  res.writeHead(404); res.end("non trovato");
});
await new Promise((r) => servidor.listen(0, "127.0.0.1", r));
PORTA = servidor.address().port;
const CURL_HOME = mkdtempSync(join(tmpdir(), "feed-ligado-curl-"));
const resolve = [HOST, HOST_MAU, HOST_SUJO].map((h) => `resolve = "${h}:${PORTA}:127.0.0.1"`).join("\n") + "\n";
for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(CURL_HOME, n), resolve);
process.env.CURL_HOME = CURL_HOME;

const M = await import("../../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../../regras/italy_contracts.mjs");
const FONTE = "IT-T10-018", FONTE_MAU = "IT-T10-021", FONTE_SUJO = "IT-T1-002";
const ORIGINAIS = Object.fromEntries([FONTE, FONTE_MAU, FONTE_SUJO].map((s) => [s, { ...CONTRACTS[s] }]));
let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};
const ligar = (sid, host) => {
  CONTRACTS[sid].ACQUISITION = { STRATEGY: "FEED_DISCOVERY", FEED_URL: u(host, "/feed/") };
  CONTRACTS[sid].IDENTITY = { STRATEGY: "CONTENT_CAPTURE", DOCUMENT_ID: `${sid}:URL:{doc.1}`,
    CAPTURES: { doc: { FROM: "URL", PATTERN: `${host.replace(".", "\\.")}:\\d+/(news/[a-z0-9-]+)` } } };
  CONTRACTS[sid].CANONICAL_ENTRY_URL = u(host, "/feed/");
  CONTRACTS[sid].RECOLLECTION = undefined;
};
const obsDe = (run) => readFileSync(join(RAIZ, "data/collection-ledger/italy/observations.ndjson"), "utf8")
  .split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((o) => o.RUN_ID === run && o.SOURCE_URL);
const doHost = (h, de = 0) => PEDIDOS.slice(de).filter((p) => p.host === h);
const reservas = (dom) => readFileSync(LIVRO24, "utf8").split(/\r?\n/).filter(Boolean).map((l) => JSON.parse(l))
  .filter((e) => e.TIPO === "RESERVA" && e.DOMINIO === dom).length;           // D124: eventos, um por pedido

try {
  ligar(FONTE, HOST); ligar(FONTE_MAU, HOST_MAU); ligar(FONTE_SUJO, HOST_SUJO);

  // ── corrida 1 ───────────────────────────────────────────────────────────────────────────────────
  const R1 = `PROVA_FEED_LIGADO_1_${Date.now()}`;
  const { resumo: r1 } = await M.executarRodada({ runId: R1, apenas: [FONTE], pularParse: true, nota: "feed ligado 1" });
  const o1 = obsDe(R1);
  const porUrl = Object.fromEntries(o1.map((o) => [o.SOURCE_URL.replace(/^http:\/\/[^/]+/, ""), o]));
  console.log(`  corrida 1: ${JSON.stringify(doHost(HOST).map((p) => p.url))}`);
  t("G1a: corrida 1 = robots + feed + 1 materia (3 pedidos); os 2 com corpo nao pedem nada", () => {
    assert.deepEqual(doHost(HOST).map((p) => p.url), ["/robots.txt", "/feed/", "/news/articolo-solo-link/"]);
    assert.equal(r1.contadores.BODY_FROM_FEED, 2, JSON.stringify(r1.contadores));
    assert.equal(r1.contadores.DETAIL_REQUESTS, 1);
    assert.equal(reservas("feedligado.test"), 3);
  });
  t("G2: BODY_FROM_FEED — rotulo, origem, bytes exactos (nada limpo), nome que o diz, FACT_TIME UNKNOWN, PUBLISHED_AT do feed", () => {
    const o = porUrl["/news/mosca-olivo-catture/"];
    assert.ok(o, JSON.stringify(Object.keys(porUrl)));
    assert.equal(o.RAW_EVIDENCE_STATE, "BODY_FROM_FEED");
    assert.equal(o.BODY_FROM_FEED.CAMPO, "content:encoded");
    assert.equal(o.BODY_FROM_FEED.FEED_URL, u(HOST, "/feed/"));
    assert.match(o.BODY_FROM_FEED.FEED_SHA256, /^[0-9a-f]{64}$/);
    assert.equal(readFileSync(o.RAW_PATH, "utf8"), CORPO_1);
    assert.match(o.RAW_PATH, /\.body-from-feed\.html$/);
    assert.equal(o.FACT_TIME, "UNKNOWN");
    assert.equal(o.PUBLISHED_AT, "2026-09-24T07:30:00.000Z");
    assert.match(o.PUBLISHED_AT_BASIS, /^FEED pubDate em .*nivel indice; nunca FACT_TIME$/);
    assert.equal(o.DOCUMENT_ID, `${FONTE}:URL:news/mosca-olivo-catture`);
    assert.equal(readFileSync(porUrl["/news/peronospora-allerta/"].RAW_PATH, "utf8"), CORPO_2);
  });
  t("G3: a materia sem corpo foi pedida e e PAGINA — sem rotulo de feed", () => {
    const o = porUrl["/news/articolo-solo-link/"];
    assert.ok(o && !("RAW_EVIDENCE_STATE" in o) && !("BODY_FROM_FEED" in o), JSON.stringify(o));
    assert.match(o.RAW_PATH, /articolo-solo-link\.html$/);
    assert.ok(!/body-from-feed/.test(o.RAW_PATH));
  });
  t("G6: as linhas Sitemap: ficam no resumo; nenhum pedido sai por elas", () => {
    const rb = r1.CORTESIA.ROBOTS[u(HOST, "").replace(/\/$/, "")];
    assert.ok(rb, JSON.stringify(Object.keys(r1.CORTESIA.ROBOTS)));
    assert.deepEqual(rb.SITEMAPS, [u(HOST, "/sitemap.xml"), u(HOST, "/news-sitemap.xml")]);
    assert.equal(rb.ORIGEM, "PEDIDO_NESTA_CORRIDA");
    assert.ok(!PEDIDOS.some((p) => /sitemap/.test(p.url)));
  });

  // ── corrida 2: nada mudou ─────────────────────────────────────────────────────────────────────────
  const antes2 = PEDIDOS.length;
  const R2 = `PROVA_FEED_LIGADO_2_${Date.now()}`;
  const { resumo: r2 } = await M.executarRodada({ runId: R2, apenas: [FONTE], pularParse: true, nota: "feed ligado 2" });
  console.log(`  corrida 2: ${JSON.stringify(doHost(HOST, antes2).map((p) => `${p.url}${p.inm ? " INM=" + p.inm : ""}`))}`);
  t("G4: corrida 2 — o robots vem do livro de 24 h (o servidor nao o ve)", () => {
    assert.ok(!doHost(HOST, antes2).some((p) => p.url === "/robots.txt"));
    assert.equal(r2.contadores.ROBOTS_FROM_24H_BOOK, 1);
    assert.equal(r2.contadores.ROBOTS_REQUESTS, 0);
    assert.match(Object.values(r2.CORTESIA.ROBOTS)[0].ORIGEM, /^LIVRO_24H/);
  });
  t("G5a: corrida 2 — o feed vai com If-None-Match, volta 304 e CONTA (livro de 24 h = 4)", () => {
    const ps = doHost(HOST, antes2);
    assert.deepEqual(ps.map((p) => p.url), ["/feed/"]);
    assert.equal(ps[0].inm, '"feed-v1"');
    assert.equal(r2.contadores.NOT_MODIFIED_304, 1);
    assert.equal(r2.contadores.CONDITIONAL_SENT, 1);
    assert.equal(r2.CORTESIA.PEDIDOS_POR_DOMINIO["feedligado.test"], 1);
    assert.equal(reservas("feedligado.test"), 4);
    assert.equal(obsDe(R2).length, 0, "tudo ja conhecido: nenhuma observacao nova");
  });

  // ── corrida 3: o feed mudou, e o teto de 24 h fecha ──────────────────────────────────────────────
  VERSAO_DO_FEED = 2;
  const antes3 = PEDIDOS.length;
  const R3 = `PROVA_FEED_LIGADO_3_${Date.now()}`;
  const { resumo: r3 } = await M.executarRodada({ runId: R3, apenas: [FONTE], pularParse: true, nota: "feed ligado 3" });
  console.log(`  corrida 3: ${JSON.stringify(doHost(HOST, antes3).map((p) => p.url))}`);
  t("G5b: corrida 3 — feed 200 (5.o pedido); a materia nova e RECUSADA pelo teto de 24 h — o 304 contou", () => {
    assert.deepEqual(doHost(HOST, antes3).map((p) => p.url), ["/feed/"]);
    assert.equal(r3.contadores.DETAIL_DEFERRED_BY_COURTESY, 1, JSON.stringify(r3.contadores));
    assert.equal(r3.contadores.COURTESY_REFUSALS.TETO_24H, 1);
  });
  t("G1b: nunca mais de 5 pedidos do dominio em 24 h — contado no SERVIDOR e no livro", () => {
    assert.equal(doHost(HOST).length, 5, JSON.stringify(doHost(HOST).map((p) => p.url)));
    assert.equal(reservas("feedligado.test"), 5);
  });

  // ── robots ilegivel, e livro de robots sujo ─────────────────────────────────────────────────────
  const antesMau = PEDIDOS.length;
  const RM = `PROVA_FEED_LIGADO_MAU_${Date.now()}`;
  const { resumo: rm } = await M.executarRodada({ runId: RM, apenas: [FONTE_MAU], pularParse: true, nota: "robots mau" });
  const RM2 = `PROVA_FEED_LIGADO_MAU2_${Date.now()}`;
  await M.executarRodada({ runId: RM2, apenas: [FONTE_MAU], pularParse: true, nota: "robots mau 2" });
  t("G7: robots em HTML = ILEGIVEL: o feed nao e pedido, nao vai ao livro de 24 h, e a corrida seguinte pede-o outra vez", () => {
    assert.deepEqual(doHost(HOST_MAU, antesMau).map((p) => p.url), ["/robots.txt", "/robots.txt"]);
    assert.equal(rm.contadores.COURTESY_REFUSALS.ROBOTS_ILEGIVEL, 1, JSON.stringify(rm.contadores));
    const livro = JSON.parse(readFileSync(`${LIVRO24}.robots.json`, "utf8")).ROBOTS;
    assert.ok(!Object.keys(livro).some((o) => o.includes(HOST_MAU)), JSON.stringify(Object.keys(livro)));
  });
  // uma entrada que diz LIDO sem o texto, e outra que diz ILEGIVEL: nenhuma e permissao
  const origemSujo = u(HOST_SUJO, "").replace(/\/$/, "");
  const lr = JSON.parse(readFileSync(`${LIVRO24}.robots.json`, "utf8"));
  lr.ROBOTS[origemSujo] = { ESTADO: "LIDO", EM: Date.now() / 1000, PORQUE: "sem texto" };
  writeFileSync(`${LIVRO24}.robots.json`, JSON.stringify(lr));
  const antesSujo = PEDIDOS.length;
  const RS = `PROVA_FEED_LIGADO_SUJO_${Date.now()}`;
  const { resumo: rs } = await M.executarRodada({ runId: RS, apenas: [FONTE_SUJO], pularParse: true, nota: "livro sujo" });
  t("G8: entrada do livro de robots que nao se entende (LIDO sem texto) nao e permissao: pede-se o robots", () => {
    assert.deepEqual(doHost(HOST_SUJO, antesSujo).map((p) => p.url), ["/robots.txt"]);
    assert.equal(rs.contadores.ROBOTS_FROM_24H_BOOK, 0);
    assert.equal(rs.contadores.COURTESY_REFUSALS.ROBOTS_ILEGIVEL, 1, JSON.stringify(rs.contadores));
  });
  t("G9: o validador e o do SERVIDOR (ultimo bloco), nunca o do «Connection established» do proxy", () => {
    const f = join(RAIZ, "cab.txt");
    writeFileSync(f, 'HTTP/1.1 200 Connection established\r\nETag: "do-proxy"\r\n\r\nHTTP/2 200\r\netag: "do-servidor"\r\nlast-modified: Thu, 24 Sep 2026 07:30:00 GMT\r\n\r\n');
    assert.deepEqual(M.validadoresDaResposta(f), { ETAG: '"do-servidor"', LAST_MODIFIED: "Thu, 24 Sep 2026 07:30:00 GMT" });
    writeFileSync(f, "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n");
    assert.deepEqual(M.validadoresDaResposta(f), { ETAG: null, LAST_MODIFIED: null });
    assert.deepEqual(M.cabecalhosCondicionais(null), []);
  });
  t("G8b: livro de robots que nao e JSON nao e permissao", () => {
    writeFileSync(`${LIVRO24}.robots.json`, "{ nao e json");
    assert.equal(M.robotsDoLivro24h(u(HOST, "").replace(/\/$/, "")), null);
  });
} finally {
  for (const [s, o] of Object.entries(ORIGINAIS)) { for (const k of Object.keys(CONTRACTS[s])) if (!(k in o)) delete CONTRACTS[s][k]; Object.assign(CONTRACTS[s], o); }
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
  rmSync(CURL_HOME, { recursive: true, force: true });
}
console.log(`\nFEED_LIGADO_LOCAL · passou=${passou} FALHAS=${falhou}`);
process.exit(falhou ? 1 : 0);
