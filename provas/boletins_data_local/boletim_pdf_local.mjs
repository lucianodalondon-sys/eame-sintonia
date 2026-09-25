// D61/D62 · DATA E LUGAR DO BOLETIM PDF — PROVADOS NO COLETOR DE VERDADE, CONTRA UM SERVIDOR LOCAL.
//
//     node provas/boletins_data_local/boletim_pdf_local.mjs
//
// ZERO REDE EXTERNA (como a prova da «página é o boletim»): proxy de saída numa porta fechada, só 127.0.0.1.
// Um contrato lista -> PDF com a identidade pelo NÚMERO do boletim e os três campos D61 lidos no TEXTO do
// PDF (o leitor PDF_TEXT único, coleta/texto_de_pdf.mjs). Três rodadas, cada uma um boletim novo:
//   P1  cabeçalho «n. 38/2026 del 21 settembre 2026» + período + área -> os três campos, com a BASE
//   P2  PDF sem cabeçalho nem período                                 -> COLETADO na mesma (D62), NAO SEI com o porquê
//   P3  «del 31 febbraio 2026»                                        -> NAO SEI (nunca uma data inventada)
//   P4  período sem ligação ao facto no texto (D69)                   -> FACT_TIME NAO SEI, período em BULLETIN_PERIOD
// Em todas: CAPTURED_AT à parte, e nunca no lugar de PUBLISHED_AT / FACT_TIME.
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, existsSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "boletim-pdf-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
process.env.NO_PROXY = process.env.no_proxy = "127.0.0.1,localhost";
for (const k of ["SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST"]) delete process.env[k];

// Um PDF mínimo e válido com linhas de texto (Helvetica) — o mesmo molde de curadoria/test_canario_pdf.py.
function pdfComTexto(linhas) {
  const esc = (s) => s.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
  const corpo = "BT /F1 9 Tf 20 800 Td 11 TL " + linhas.map((l) => `(${esc(l)}) '`).join(" ") + " ET";
  const objs = ["<< /Type /Catalog /Pages 2 0 R >>", "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
    `<< /Length ${Buffer.byteLength(corpo, "latin1")} >>\nstream\n${corpo}\nendstream`,
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"];
  let out = "%PDF-1.4\n"; const pos = [];
  objs.forEach((o, i) => { pos.push(Buffer.byteLength(out, "latin1")); out += `${i + 1} 0 obj\n${o}\nendobj\n`; });
  const xref = Buffer.byteLength(out, "latin1");
  out += `xref\n0 ${objs.length + 1}\n0000000000 65535 f \n` + pos.map((p) => String(p).padStart(10, "0") + " 00000 n \n").join("");
  out += `trailer\n<< /Size ${objs.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`;
  return Buffer.from(out, "latin1");
}
const texto = (cab, per, area, ligado = true) => [cab, per, per && ligado ? "Diario meteorologico: temperature sopra la media" : null, area, ...Array(40).fill("Situazione fitosanitaria delle colture della provincia e consigli di difesa integrata.")].filter(Boolean);

let LISTA = "", PDFS = {};
const servidor = createServer((req, res) => {
  if (req.url === "/robots.txt") { res.writeHead(404); res.end("non trovato"); return; }
  if (req.url === "/bollettini") { res.setHeader("Content-Type", "text/html; charset=utf-8"); res.end(LISTA); return; }
  if (PDFS[req.url]) { res.setHeader("Content-Type", "application/pdf"); res.end(PDFS[req.url]); return; }
  res.writeHead(404); res.end("non trovato");
});
await new Promise((r) => servidor.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${servidor.address().port}`;
const CURL_HOME = mkdtempSync(join(tmpdir(), "boletim-pdf-curl-"));
for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(CURL_HOME, n), "\n");
process.env.CURL_HOME = CURL_HOME;

const M = await import("../../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../../regras/italy_contracts.mjs");
const FONTE = "IT-T10-018";
const ORIGINAL = JSON.parse(JSON.stringify({ ACQUISITION: CONTRACTS[FONTE].ACQUISITION, IDENTITY: CONTRACTS[FONTE].IDENTITY,
  OUTPUT_TYPE: CONTRACTS[FONTE].OUTPUT_TYPE, RECOLLECTION: CONTRACTS[FONTE].RECOLLECTION ?? null,
  CANONICAL_ENTRY_URL: CONTRACTS[FONTE].CANONICAL_ENTRY_URL, FORMA: CONTRACTS[FONTE].FORMA ?? null,
  EXPECTED_SIGNATURE: CONTRACTS[FONTE].EXPECTED_SIGNATURE ?? null }));
const DATA_IT = "(\\d{1,2})\\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\\s+(\\d{4})";
const opc = (PATTERN, n, FLAGS) => ({ FROM: "PDF_TEXT", PATTERN, REQUIRED: false, DEFAULTS: Array(n).fill("x"), ...(FLAGS ? { FLAGS } : {}) });
Object.assign(CONTRACTS[FONTE], {
  FORMA: null, OUTPUT_TYPE: "PDF", EXPECTED_SIGNATURE: "%PDF", CANONICAL_ENTRY_URL: `${BASE}/bollettini`, RECOLLECTION: null,
  ACQUISITION: { STRATEGY: "HTML_LINK_DISCOVERY", MATCH: "URL", INDEX_URL: `${BASE}/bollettini`,
                 LINK_PATTERN: "^http://127\\.0\\.0\\.1:\\d+/pdf/(\\d{2})_boll_(\\d{4})\\.pdf$", MAX_TARGETS: 1 },
  IDENTITY: {
    STRATEGY: "CONTENT_CAPTURE",
    CAPTURES: {
      b: { FROM: "URL", PATTERN: "/(\\d{2})_boll_(\\d{4})\\.pdf$" },
      em: opc(`n\\.\\s*\\d+/\\d{4}\\s+del\\s+${DATA_IT}`, 3, "i"),
      per: opc(`${DATA_IT}\\s*-\\s*${DATA_IT}\\s*\\n\\s*Diario meteorologico`, 6, "i"),
      cob: opc(`${DATA_IT}\\s*-\\s*${DATA_IT}`, 6, "i"),
      area: opc("valido per la provincia di ([A-Z][a-z]+)", 1),
    },
    DOCUMENT_ID: `${FONTE}:BOLETIM:{b.2}-{b.1}`,
    PUBLISHED_AT: "{em.3}-{em.2:MES_IT}-{em.1:DIA2}",
    PUBLISHED_AT_BASIS: "EMISSAO_DECLARADA_NO_BOLETIM · cabeçalho «n. NN/AAAA del <data>»",
    FACT_TIME: "{per.3}-{per.2:MES_IT}-{per.1:DIA2}/{per.6}-{per.5:MES_IT}-{per.4:DIA2}",
    FACT_TIME_BASIS: "PERIODO_LIGADO_AO_FATO_NO_TEXTO · «<data> - <data>» encabeça o «Diario meteorologico»",
    BULLETIN_PERIOD: "{cob.3}-{cob.2:MES_IT}-{cob.1:DIA2}/{cob.6}-{cob.5:MES_IT}-{cob.4:DIA2}",
    BULLETIN_PERIOD_BASIS: "PERIODO_DECLARADO_NO_BOLETIM · «<data> - <data>»",
    FACT_LOCATION: "{area.1}",
    FACT_LOCATION_BASIS: "AREA_DECLARADA_NO_BOLETIM · «valido per la provincia di …»",
  },
});

const livro = () => {
  const f = join(RAIZ, "data/collection-ledger/italy/observations.ndjson");
  return existsSync(f) ? readFileSync(f, "utf8").split("\n").filter(Boolean).map(JSON.parse) : [];
};
async function rodada(nome, numero, linhas) {
  const url = `/pdf/${numero}_boll_2026.pdf`;
  PDFS = { [url]: pdfComTexto(linhas) };
  LISTA = `<!DOCTYPE html><html><body><h1>Bollettini</h1><a href="${url}">Bollettino ${numero}</a></body></html>`;
  const antes = livro().length;
  await M.executarRodada({ runId: `PROVA_BOLETIM_PDF_${nome}_${Date.now()}`, apenas: [FONTE], pularParse: true, nota: `prova ${nome}` });
  const novas = livro().slice(antes);
  assert.equal(novas.length, 1, `${nome}: esperava 1 observacao, vieram ${novas.length}`);
  return novas[0];
}
let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};

try {
  const p1 = await rodada("P1", "38", texto("Bollettino Settimanale n. 38/2026 del 21 settembre 2026",
    "14 settembre 2026 - 20 settembre 2026", "valido per la provincia di Bologna"));
  t("P1: emissão, período e área lidos no PDF, cada um com a BASE e o trecho", () => {
    assert.match(p1.OBSERVATION_RESULT, /BASELINE_DOCUMENT|NEW_DOCUMENT/);
    assert.equal(p1.DOCUMENT_ID, `${FONTE}:BOLETIM:2026-38`);
    assert.equal(p1.PUBLISHED_AT, "2026-09-21");
    assert.match(p1.PUBLISHED_AT_BASIS, /^EMISSAO_DECLARADA_NO_BOLETIM .*21 settembre 2026/);
    assert.equal(p1.FACT_TIME, "2026-09-14/2026-09-20");
    assert.match(p1.FACT_TIME_BASIS, /^PERIODO_LIGADO_AO_FATO_NO_TEXTO/);
    assert.equal(p1.BULLETIN_PERIOD, "2026-09-14/2026-09-20");
    assert.equal(p1.FACT_LOCATION, "Bologna");
    assert.match(p1.FACT_LOCATION_BASIS, /^AREA_DECLARADA_NO_BOLETIM/);
    assert.ok(p1.RAW_PATH && existsSync(p1.RAW_PATH), "RAW nao foi preservado");
    assert.ok(p1.CAPTURED_AT && !String(p1.CAPTURED_AT).startsWith("2026-09-21"), "CAPTURED_AT e a hora da coleta, a parte");
  });
  const p2 = await rodada("P2", "39", texto(null, null, null));
  t("P2: PDF sem data nem área -> COLETADO na mesma (D62), NAO SEI com o porquê", () => {
    assert.match(p2.OBSERVATION_RESULT, /NEW_DOCUMENT|BASELINE_DOCUMENT/);
    assert.equal(p2.DOCUMENT_ID, `${FONTE}:BOLETIM:2026-39`);
    assert.ok(p2.RAW_PATH && existsSync(p2.RAW_PATH), "o documento sem data tem de ser preservado");
    for (const c of ["PUBLISHED_AT", "FACT_TIME", "FACT_LOCATION"]) {
      assert.equal(p2[c], "NAO SEI", c);
      assert.match(p2[`${c}_BASIS`], /^NAO SEI · .*D62/, `${c}_BASIS`);
    }
  });
  const p3 = await rodada("P3", "40", texto("Bollettino Settimanale n. 40/2026 del 31 febbraio 2026", null, null));
  t("P3: «31 febbraio» -> NAO SEI (nunca uma data inventada)", () => {
    assert.equal(p3.PUBLISHED_AT, "NAO SEI");
    assert.match(p3.PUBLISHED_AT_BASIS, /não é data de calendário/);
  });
  const p4 = await rodada("P4", "41", texto("Bollettino Settimanale n. 41/2026 del 12 ottobre 2026",
    "5 ottobre 2026 - 11 ottobre 2026", null, false));
  t("P4 (D69): período sem ligação ao facto -> FACT_TIME NAO SEI, período guardado como evidência", () => {
    assert.equal(p4.PUBLISHED_AT, "2026-10-12");
    assert.equal(p4.FACT_TIME, "NAO SEI");
    assert.equal(p4.BULLETIN_PERIOD, "2026-10-05/2026-10-11");
    assert.match(p4.FACT_TIME_BASIS, /BULLETIN_PERIOD.*D69/);
  });
} finally {
  Object.assign(CONTRACTS[FONTE], ORIGINAL);
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
  rmSync(CURL_HOME, { recursive: true, force: true });
}
console.log(`\nBOLETIM_PDF_LOCAL · passou=${passou} FALHAS=${falhou}`);
process.exit(falhou ? 1 : 0);
