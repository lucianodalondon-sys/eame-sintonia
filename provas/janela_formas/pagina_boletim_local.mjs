// D42 (2) · «A PÁGINA É O BOLETIM» — PROVADA NO COLETOR DE VERDADE, CONTRA UM SERVIDOR LOCAL.
//
//     node provas/janela_formas/pagina_boletim_local.mjs
//
// ZERO REDE EXTERNA (como a prova da cortesia): proxy de saída numa porta fechada, só 127.0.0.1.
// Um contrato STATIC_ENDPOINT com a forma explícita e identidade = fonte + BOLETIM + data
// comprovada; a impressão do conteúdo RECORTADO (CONTENT_SCOPE) deduplica. Seis rodadas:
//   B1  primeira captura                          -> documento novo, RAW preservado antes do parse
//   B2  o menu da página mudou (texto e contador) -> SEEN_AGAIN (mesma impressão do boletim)
//   B3  o boletim da MESMA data foi corrigido     -> DOCUMENT_CHANGED_IN_PLACE (versão nova, preservada)
//   B4  o boletim do dia seguinte                 -> documento novo (outra data)
//   B5  boletim sem data                          -> SOURCE_DATE/ISO/FACT_TIME = UNKNOWN; CAPTURED_AT à parte
//   B6  a página já não tem o boletim             -> IDENTITY_FAILED (não guarda lixo com cara de boletim)
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, existsSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "pagina-boletim-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
process.env.NO_PROXY = process.env.no_proxy = "127.0.0.1,localhost";
for (const k of ["SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST"]) delete process.env[k];

let PAGINA = "";
const servidor = createServer((req, res) => {
  if (req.url === "/robots.txt") { res.writeHead(404); res.end("non trovato"); return; }
  if (req.url === "/agrometeo") { res.setHeader("Content-Type", "text/html; charset=utf-8"); res.end(PAGINA); return; }
  res.writeHead(404); res.end("non trovato");
});
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${servidor.address().port}`;
const CURL_HOME = mkdtempSync(join(tmpdir(), "pagina-boletim-curl-"));
for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(CURL_HOME, n), "\n");
process.env.CURL_HOME = CURL_HOME;

const pagina = (visite, boletim, menu = "Meteo") => `<!DOCTYPE html><html><head><title>Agrometeo</title></head><body>
<nav><a href="/">Home</a> <a href="/meteo">${menu}</a> <span>Visite: ${visite}</span></nav>
<main><h1>BOLLETTINO AGROMETEOROLOGICO</h1>${boletim}<p>Fine bollettino</p></main>
<footer><a href="/contatti">Contatti</a></footer></body></html>`;
const corpo = (emissao, texto) => `<p>${emissao ? `Emesso il ${emissao} · valido dal ${emissao} al 30/09/2026` : "Senza data di emissione."}</p>` +
  `<p>${texto} ${"Previsione agrometeorologica per le colture della provincia. ".repeat(20)}</p>`;

const M = await import("../../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../../regras/italy_contracts.mjs");
const FONTE = "IT-T10-018";
const ORIGINAL = JSON.parse(JSON.stringify({ ACQUISITION: CONTRACTS[FONTE].ACQUISITION, IDENTITY: CONTRACTS[FONTE].IDENTITY,
  OUTPUT_TYPE: CONTRACTS[FONTE].OUTPUT_TYPE, RECOLLECTION: CONTRACTS[FONTE].RECOLLECTION ?? null,
  CANONICAL_ENTRY_URL: CONTRACTS[FONTE].CANONICAL_ENTRY_URL, FORMA: CONTRACTS[FONTE].FORMA ?? null }));
Object.assign(CONTRACTS[FONTE], {
  FORMA: "PAGINA_E_BOLETIM", OUTPUT_TYPE: "HTML", CANONICAL_ENTRY_URL: `${BASE}/agrometeo`,
  // a pagina E o boletim: a revisita E a coleta (vocabulario que ja existe em regras/incrementalidade.mjs)
  RECOLLECTION: { DETAIL_CONTENT: "MUTABLE" },
  ACQUISITION: { STRATEGY: "STATIC_ENDPOINT", URL: `${BASE}/agrometeo`, NAME: "agrometeo.html" },
  IDENTITY: {
    STRATEGY: "CONTENT_CAPTURE",
    DOCUMENT_ID: `${FONTE}:BOLETIM:{emissao.3}-{emissao.2}-{emissao.1}`,
    SOURCE_DATE: "{emissao.1}/{emissao.2}/{emissao.3}", SOURCE_DATE_ISO: "{emissao.3}-{emissao.2}-{emissao.1}",
    FACT_TIME: "{validade.1} a {validade.2}",
    CONTENT_SCOPE: { START: "BOLLETTINO AGROMETEOROLOGICO", END: "Fine bollettino" },
    CAPTURES: {
      emissao: { FROM: "PAGE_TEXT", PATTERN: "Emesso il (\\d{2})/(\\d{2})/(\\d{4})", REQUIRED: false, DEFAULTS: ["UNKNOWN", "UNKNOWN", "UNKNOWN"] },
      validade: { FROM: "PAGE_TEXT", PATTERN: "valido dal (\\S+) al (\\S+)", REQUIRED: false, DEFAULTS: ["UNKNOWN", "UNKNOWN"] },
    },
  },
});

const livro = () => {
  const f = join(RAIZ, "data/collection-ledger/italy/observations.ndjson");
  return existsSync(f) ? readFileSync(f, "utf8").split("\n").filter(Boolean).map(JSON.parse) : [];
};
async function rodada(nome, html) {
  PAGINA = html;
  const linhas = livro().length;
  const { resumo, detalhes } = await M.executarRodada({ runId: `PROVA_BOLETIM_${nome}_${Date.now()}`, apenas: [FONTE], pularParse: true, nota: `prova ${nome}` });
  if (process.env.VER) console.log(nome, JSON.stringify(resumo.contadores), JSON.stringify(detalhes).slice(0, 600));
  const novas = livro().slice(linhas);
  assert.equal(novas.length, 1, `${nome}: esperava 1 observacao, vieram ${novas.length}`);
  return novas[0];
}
let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};

try {
  const b1 = await rodada("B1", pagina(134, corpo("24/09/2026", "Olivo: mosca in aumento.")));
  t("B1: documento novo, identidade pela data comprovada, RAW preservado antes do parse", () => {
    assert.match(b1.OBSERVATION_RESULT, /BASELINE_DOCUMENT|NEW_DOCUMENT/);
    assert.equal(b1.DOCUMENT_ID, `${FONTE}:BOLETIM:2026-09-24`);
    assert.equal(b1.SOURCE_DATE_ISO, "2026-09-24");
    assert.equal(b1.FACT_TIME, "24/09/2026 a 30/09/2026");
    assert.match(b1.CONTENT_SHA256, /^[0-9a-f]{64}$/);
    assert.ok(b1.RAW_PATH && existsSync(b1.RAW_PATH), "RAW nao foi preservado");
    assert.equal(b1.RAW_PRESERVED_BEFORE_PARSE, true);
    assert.ok(b1.CAPTURED_AT && !String(b1.CAPTURED_AT).startsWith("2026-09-24T00"), "CAPTURED_AT e a hora da coleta, a parte");
  });
  // o MENU muda de texto (nao so o contador): a defesa antiga do ruido nao chega aqui — quem decide
  // e a impressao do boletim recortado
  const b2 = await rodada("B2", pagina(135, corpo("24/09/2026", "Olivo: mosca in aumento."), "Meteo e clima · Nuovo servizio SMS"));
  t("B2: o menu mudou, o boletim nao -> SEEN_AGAIN pela impressao do boletim (bytes diferentes)", () => {
    assert.equal(b2.OBSERVATION_RESULT, "SEEN_AGAIN");
    assert.equal(b2.CONTENT_SHA256, b1.CONTENT_SHA256);
    assert.notEqual(b2.RECEIVED_RAW_SHA256, b1.RAW_SHA256, "os bytes tinham de ser diferentes");
    assert.equal(b2.DOCUMENT_VERSION_ID, b1.DOCUMENT_VERSION_ID);
  });
  const b3 = await rodada("B3", pagina(136, corpo("24/09/2026", "Olivo: mosca STABILE (rettifica).")));
  t("B3: boletim corrigido na mesma data -> versao nova do MESMO documento, preservada", () => {
    assert.equal(b3.OBSERVATION_RESULT, "DOCUMENT_CHANGED_IN_PLACE");
    assert.equal(b3.DOCUMENT_ID, b1.DOCUMENT_ID);
    assert.notEqual(b3.CONTENT_SHA256, b1.CONTENT_SHA256);
    assert.notEqual(b3.DOCUMENT_VERSION_ID, b1.DOCUMENT_VERSION_ID);
    assert.ok(existsSync(b3.RAW_PATH));
  });
  const b4 = await rodada("B4", pagina(137, corpo("25/09/2026", "Olivo: mosca in calo.")));
  t("B4: boletim do dia seguinte -> documento novo", () => {
    assert.equal(b4.OBSERVATION_RESULT, "NEW_DOCUMENT");
    assert.equal(b4.DOCUMENT_ID, `${FONTE}:BOLETIM:2026-09-25`);
  });
  const b5 = await rodada("B5", pagina(138, corpo(null, "Olivo: situazione invariata.")));
  t("B5: sem data -> tempos UNKNOWN, nunca a data de coleta; captura preservada", () => {
    assert.equal(b5.DOCUMENT_ID, `${FONTE}:BOLETIM:UNKNOWN-UNKNOWN-UNKNOWN`);
    assert.equal(b5.SOURCE_DATE_ISO, "UNKNOWN");
    assert.equal(b5.SOURCE_DATE, "UNKNOWN");
    assert.equal(b5.FACT_TIME, "UNKNOWN");
    assert.ok(b5.CAPTURED_AT, "a hora da coleta existe, noutro campo");
    assert.ok(existsSync(b5.RAW_PATH));
  });
  const b6 = await rodada("B6", `<html><body><p>Pagina in manutenzione</p></body></html>`);
  t("B6: sem o boletim na pagina -> IDENTITY_FAILED (nao guarda lixo)", () => {
    assert.equal(b6.OBSERVATION_RESULT, "IDENTITY_FAILED");
    assert.equal(b6.DOCUMENT_ID, null);
  });
} finally {
  Object.assign(CONTRACTS[FONTE], ORIGINAL);
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
  rmSync(CURL_HOME, { recursive: true, force: true });
}
console.log(`\nPAGINA_BOLETIM_LOCAL · passou=${passou} FALHAS=${falhou}`);
process.exit(falhou ? 1 : 0);
