// SINTONIA EAME — FEED_DISCOVERY: o índice é o feed RSS/Atom que a própria fonte anuncia
//
//     node regras/feed_discovery_test.mjs
//
// SCRAP-EVOLUCAO-V1 (26/09, D89 + ESTUDO-SCRAPLING-UNIAO, prioridade 1). Nenhuma prova abre a rede:
// o leitor do feed é injectado. O feed de exemplo tem a forma do WordPress (14/44 fontes do acervo
// anunciam feed, quase todas WordPress): CDATA, entidades, <pubDate> RFC 822, <dc:creator>.

import { strict as assert } from "node:assert";
import {
  alvosDoContrato, conferirAquisicao, identidadeDoContrato, itensDoFeed, ContratoInvalido, ALVOS_POR_FONTE_D40,
} from "./motor_de_rota.mjs";

let ok = 0, mau = 0;
const TA = async (nome, fn) => {
  try { await fn(); console.log(`  PASS  ${nome}`); ok++; }
  catch (e) { console.log(`  FAIL  ${nome}\n        ${e.message}`); mau++; }
};
const leitor = (xml, status = 200) => async () => ({ status, buf: Buffer.from(xml, "utf8") });
const FEED = "https://www.cifo.it/feed/";
const RSS_WP = `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
<channel><title>Cifo</title><link>https://www.cifo.it</link>
<item><title><![CDATA[Catalogo Cifo 2026: soluzioni &amp; affidabilità]]></title>
  <link>https://www.cifo.it/newsroom/catalogo-cifo-2026-soluzioni/</link>
  <pubDate>Thu, 24 Sep 2026 07:30:00 +0000</pubDate><dc:creator><![CDATA[Redazione]]></dc:creator></item>
<item><title>Biostimolanti in vigneto</title><link>https://www.cifo.it/newsroom/biostimolanti-vigneto/</link>
  <dc:date>2026-09-20T10:00:00+02:00</dc:date></item>
<item><title>Senza data</title><link>https://www.cifo.it/newsroom/senza-data/</link></item>
<item><title>Altro sito</title><link>https://www.altro.it/news/x/</link><pubDate>Mon, 21 Sep 2026 08:00:00 +0000</pubDate></item>
<item><title>Commenti</title><link>https://www.cifo.it/newsroom/catalogo-cifo-2026-soluzioni/feed/</link></item>
<item><title>Pagina 2</title><link>https://www.cifo.it/newsroom/page/2/</link></item>
<item><title>Quarto</title><link>https://www.cifo.it/newsroom/quarto-articolo/</link><pubDate>Sat, 19 Sep 2026 08:00:00 +0000</pubDate></item>
</channel></rss>`;
const ATOM = `<feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>So aggiornato</title><link rel="alternate" href="/news/aggiornato/"/><updated>2026-09-22T00:00:00Z</updated></entry>
<entry><title>Pubblicato</title><link rel="replies" href="/news/pubblicato/#comments"/><link href="https://www.a.it/news/pubblicato/"/>
  <published>2026-09-21T10:00:00+02:00</published><updated>2026-09-23T00:00:00Z</updated></entry>
</feed>`;
const contrato = (aq = {}) => ({ OUTPUT_TYPE: "HTML",
  ACQUISITION: { STRATEGY: "FEED_DISCOVERY", FEED_URL: FEED, ...aq },
  IDENTITY: { STRATEGY: "CONTENT_CAPTURE", DOCUMENT_ID: "IT-T9-009:URL:{doc.1}",
              CAPTURES: { doc: { FROM: "URL", PATTERN: "cifo\\.it/(.+?)/?$" } } } });

console.log("\nFEED_DISCOVERY");

await TA("RSS do WordPress: os itens do proprio site, com titulo e data de publicacao NIVEL INDICE", async () => {
  const a = await alvosDoContrato("IT-T9-009", contrato({ MAX_TARGETS: 10 }), { buscar: leitor(RSS_WP) });
  assert.deepEqual(a.map((x) => x.url), [
    "https://www.cifo.it/newsroom/catalogo-cifo-2026-soluzioni/", "https://www.cifo.it/newsroom/biostimolanti-vigneto/",
    "https://www.cifo.it/newsroom/senza-data/", "https://www.cifo.it/newsroom/quarto-articolo/"]);
  assert.equal(a[0].textoDaLigacao, "Catalogo Cifo 2026: soluzioni & affidabilità");
  assert.equal(a[0].publicadoNoIndice.VALOR, "2026-09-24T07:30:00.000Z");
  assert.equal(a[0].publicadoNoIndice.CAMPO, "pubDate");
  assert.match(a[0].publicadoNoIndice.BASE, /nivel indice; nunca FACT_TIME/);
  assert.equal(a[1].publicadoNoIndice.VALOR, "2026-09-20T08:00:00.000Z");        // dc:date com fuso, em UTC
  assert.equal(a[2].publicadoNoIndice.VALOR, null);                                // sem data: NAO SEI, nao palpite
  assert.match(a[2].publicadoNoIndice.BASE, /^NAO SEI/);
});

await TA("o teto D40: sem MAX_TARGETS vao no maximo 3 alvos (robots + feed + 3 = 5, o teto D38)", async () => {
  const a = await alvosDoContrato("IT-T9-009", contrato(), { buscar: leitor(RSS_WP) });
  assert.equal(ALVOS_POR_FONTE_D40, 3);
  assert.equal(a.length, 3);
});

await TA("outro site, feed de comentarios e paginacao ficam fora; SAME_HOST=false deixa o outro site entrar", async () => {
  const a = await alvosDoContrato("IT-T9-009", contrato({ MAX_TARGETS: 10 }), { buscar: leitor(RSS_WP) });
  const us = a.map((x) => x.url).join(" ");
  assert.ok(!us.includes("altro.it") && !us.includes("/feed/") && !us.includes("/page/2/"), us);
  const b = await alvosDoContrato("IT-T9-009", contrato({ MAX_TARGETS: 10, SAME_HOST: false }), { buscar: leitor(RSS_WP) });
  assert.ok(b.some((x) => x.url.includes("altro.it")));
});

await TA("LINK_PATTERN do contrato filtra os itens", async () => {
  const a = await alvosDoContrato("IT-T9-009", contrato({ MAX_TARGETS: 10, LINK_PATTERN: "biostimolanti" }), { buscar: leitor(RSS_WP) });
  assert.deepEqual(a.map((x) => x.url), ["https://www.cifo.it/newsroom/biostimolanti-vigneto/"]);
});

await TA("Atom: <updated> NAO e publicacao; <published> e; o link rel=replies nao e o item", async () => {
  const it = itensDoFeed(ATOM, "https://www.a.it/feed/atom/");
  assert.equal(it[0].url, "https://www.a.it/news/aggiornato/");
  assert.equal(it[0].publicado, null);
  assert.equal(it[1].url, "https://www.a.it/news/pubblicato/");
  assert.equal(it[1].publicado, "2026-09-21T08:00:00.000Z");
  assert.equal(it[1].campoData, "published");
});

await TA("feed fora do ar e erro com nome; feed sem itens do site e EMPTY_LIST", async () => {
  const e = await alvosDoContrato("IT-T9-009", contrato(), { buscar: leitor("", 404) });
  assert.match(e.erro, /feed inacessivel: 404/);
  const v = await alvosDoContrato("IT-T9-009", contrato(), { buscar: leitor("<rss><channel></channel></rss>") });
  assert.match(v.erro, /^EMPTY_LIST/);
});

await TA("a conferencia recusa FEED_DISCOVERY sem FEED_URL, padrao que nao compila e SAME_HOST que nao e booleano", async () => {
  assert.throws(() => conferirAquisicao("X", { STRATEGY: "FEED_DISCOVERY" }), ContratoInvalido);
  assert.throws(() => conferirAquisicao("X", { STRATEGY: "FEED_DISCOVERY", FEED_URL: FEED, LINK_PATTERN: "(" }), ContratoInvalido);
  assert.throws(() => conferirAquisicao("X", { STRATEGY: "FEED_DISCOVERY", FEED_URL: FEED, SAME_HOST: "sim" }), ContratoInvalido);
  assert.ok(conferirAquisicao("X", { STRATEGY: "FEED_DISCOVERY", FEED_URL: FEED }));
});

await TA("com o classificador D40, os alvos escolhidos levam o que o feed disse deles", async () => {
  const classificar = () => ({ ESTADO: "NOVO" });
  const a = await alvosDoContrato("IT-T9-009", contrato(), { buscar: leitor(RSS_WP), classificar });
  assert.ok(a.length >= 1 && a.every((x) => x.publicadoNoIndice && "BASE" in x.publicadoNoIndice), JSON.stringify(a));
});

await TA("a data do feed NUNCA vira FACT_TIME: a identidade do alvo continua com FACT_TIME UNKNOWN", async () => {
  const [alvo] = await alvosDoContrato("IT-T9-009", contrato(), { buscar: leitor(RSS_WP) });
  const id = identidadeDoContrato("IT-T9-009", contrato(), alvo);
  assert.equal(id.FACT_TIME, "UNKNOWN");
  assert.equal(id.DOCUMENT_ID, "IT-T9-009:URL:newsroom/catalogo-cifo-2026-soluzioni");
});

console.log(`\n  PASSOU ${ok} · FALHOU ${mau}`);
process.exit(mau ? 1 : 0);
