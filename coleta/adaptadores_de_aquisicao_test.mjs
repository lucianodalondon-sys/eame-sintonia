// SINTONIA EAME — PROVAS DO ADAPTER `CANAL_PUBLICO_YOUTUBE_V1`
//
// Nenhum destes casos toca a rede: o leitor é injectado, e é isso que permite
// provar o comportamento MAU sem precisar que o mau aconteça lá fora.
//
// O caso que importa mais é o 3. Uma guarda de identidade que se escreve para
// tolerar «não sei» aprova tudo — e um teste que só experimenta o caminho bom
// nunca a apanha.

import assert from "node:assert/strict";
import { test } from "node:test";
import { canalPublicoYoutube, ADAPTERS } from "./adaptadores_de_aquisicao.mjs";

const CANAL = "UCUs2Mg7jvUTRt7_MSOFYM5Q";
const OUTRO = "UCEg22ii3Awy6eyRybNqO-8Q";

const pagina = (canal, ids) =>
  `<link rel="canonical" href="https://www.youtube.com/channel/${canal}">` +
  `{"externalId":"${canal}"}` +
  ids.map((i) => `{"videoId":"${i}"}`).join(",");

const leitor = (html, status = 200) => {
  const chamadas = [];
  const fn = async (url) => {
    chamadas.push(url);
    return { buf: Buffer.from(html, "utf8"), status, contentType: "text/html" };
  };
  fn.chamadas = chamadas;
  return fn;
};

const aq = (extra = {}) => ({
  STRATEGY: "CUSTOM_ADAPTER",
  ADAPTER_ID: "CANAL_PUBLICO_YOUTUBE_V1",
  CHANNEL_ID: CANAL,
  ...extra,
});

test("YT-01 · está no registry sob o nome que o contrato usa", () => {
  assert.equal(typeof ADAPTERS.CANAL_PUBLICO_YOUTUBE_V1, "function");
});

test("YT-02 · canal válido devolve alvos, e a rota é a permitida", async () => {
  const b = leitor(pagina(CANAL, ["aaaaaaaaaaa", "bbbbbbbbbbb"]));
  const r = await canalPublicoYoutube({ sourceId: "IT-T8-001", aq: aq(), buscar: b });
  assert.ok(Array.isArray(r), `esperava alvos, veio ${JSON.stringify(r)}`);
  assert.equal(r.length, 2);
  assert.equal(r[0].url, "https://www.youtube.com/watch?v=aaaaaaaaaaa");
  assert.equal(b.chamadas[0], `https://www.youtube.com/channel/${CANAL}/videos`);
});

test("YT-03 · o feed barrado por robots NUNCA é pedido", async () => {
  const b = leitor(pagina(CANAL, ["aaaaaaaaaaa"]));
  await canalPublicoYoutube({ sourceId: "IT-T8-001", aq: aq(), buscar: b });
  for (const u of b.chamadas) {
    assert.ok(!u.includes("/feeds/videos.xml"),
      `pediu a rota em Disallow: ${u}`);
  }
});

test("YT-04 · CHANNEL_ID divergente falha fechado — zero alvos", async () => {
  // A página é de OUTRO canal. Isto é o ataque real: dois canais homónimos.
  const b = leitor(pagina(OUTRO, ["aaaaaaaaaaa", "bbbbbbbbbbb"]));
  const r = await canalPublicoYoutube({ sourceId: "IT-T8-001", aq: aq(), buscar: b });
  assert.ok(!Array.isArray(r), "devolveu alvos de um canal que não é o pedido");
  assert.match(r.erro, /IDENTITY_MISMATCH/);
});

test("YT-05 · CHANNEL_ID ausente ou malformado é recusado antes da rede", async () => {
  const b = leitor(pagina(CANAL, ["aaaaaaaaaaa"]));
  for (const mau of [undefined, "", "agronotizie", "UC-curto"]) {
    await assert.rejects(
      () => canalPublicoYoutube({ sourceId: "X", aq: aq({ CHANNEL_ID: mau }), buscar: b }),
      /CHANNEL_ID/);
  }
  assert.equal(b.chamadas.length, 0, "tocou a rede com contrato inválido");
});

test("YT-06 · HTTP != 200 falha fechado", async () => {
  const r = await canalPublicoYoutube({
    sourceId: "X", aq: aq(), buscar: leitor("", 404),
  });
  assert.ok(!Array.isArray(r));
  assert.match(r.erro, /nao respondeu 200/);
});

test("YT-07 · 200 sem videoId nenhum é erro, não lista vazia silenciosa", async () => {
  const r = await canalPublicoYoutube({
    sourceId: "X", aq: aq(), buscar: leitor(pagina(CANAL, [])),
  });
  assert.ok(!Array.isArray(r));
  assert.match(r.erro, /nao trouxe videoId/);
});

test("YT-08 · MAX_TARGETS corta, e duplicados não contam duas vezes", async () => {
  const b = leitor(pagina(CANAL, ["aaaaaaaaaaa", "aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc"]));
  const r = await canalPublicoYoutube({ sourceId: "X", aq: aq({ MAX_TARGETS: 2 }), buscar: b });
  assert.equal(r.length, 2);
  assert.equal(new Set(r.map((x) => x.url)).size, 2);
});

test("YT-09 · o adapter não conhece SOURCE_ID nenhum", async () => {
  // Mesma página, dois SOURCE_ID diferentes: o resultado tem de ser idêntico.
  const html = pagina(CANAL, ["aaaaaaaaaaa", "bbbbbbbbbbb"]);
  const a = await canalPublicoYoutube({ sourceId: "IT-T8-001", aq: aq(), buscar: leitor(html) });
  const c = await canalPublicoYoutube({ sourceId: "IT-T99-999", aq: aq(), buscar: leitor(html) });
  assert.deepEqual(a, c);
  // E o código-fonte não pode conter um identificador de fonte.
});

test("YT-10 · segundo canal usa exatamente o mesmo mecanismo", async () => {
  const r = await canalPublicoYoutube({
    sourceId: "IT-T12-007",
    aq: aq({ CHANNEL_ID: OUTRO }),
    buscar: leitor(pagina(OUTRO, ["zzzzzzzzzzz"])),
  });
  assert.ok(Array.isArray(r));
  assert.equal(r[0].url, "https://www.youtube.com/watch?v=zzzzzzzzzzz");
});

test("YT-11 · sem leitor injectado, recusa — não inventa transporte", async () => {
  await assert.rejects(
    () => canalPublicoYoutube({ sourceId: "X", aq: aq(), buscar: undefined }),
    /precisa de um leitor/);
});
