// D61/D62 — DATA E LUGAR DO BOLETIM, DECLARADOS PELA ROTA
//
//     node regras/boletim_data_local_test.mjs
//
// O contrato de um boletim diz onde está a data de EMISSÃO (PUBLISHED_AT), o PERÍODO de validade ou
// observação (FACT_TIME, intervalo) e a ÁREA que o boletim declara (FACT_LOCATION), cada um com a sua
// BASE. O motor lê, valida e devolve. Nada é obrigatório (D62): o que falta sai «NAO SEI» com o porquê,
// e o documento NUNCA cai por isso. Nenhuma prova abre a rede: os textos são os medidos nos boletins
// reais (ARPAE n.º 38/2026, Umbria olivo n.13), escritos aqui à mão.

import { strict as assert } from "node:assert";
import { identidadeDoContrato, conferirIdentidade, ContratoInvalido, NAO_SEI } from "./motor_de_rota.mjs";

let ok = 0, mau = 0;
const T = (nome, fn) => {
  try { fn(); console.log(`  PASS  ${nome}`); ok++; }
  catch (e) { console.log(`  FAIL  ${nome}\n        ${e.message}`); mau++; }
};

const ARPAE_TEXTO = "Bollettino AgroMeteorologico Settimanale n. 38/2026 del 21 settembre 2026\n" +
  "14 settembre 2026 - 20 settembre 2026\nDiario meteorologico: temperature sopra la media e temporali\n";
const opc = (PATTERN, n = 1, extra = {}) => ({ FROM: "PDF_TEXT", PATTERN, REQUIRED: false, DEFAULTS: Array(n).fill("x"), ...extra });
const ARPAE = {
  IDENTITY: {
    STRATEGY: "CONTENT_CAPTURE",
    CAPTURES: {
      b: { FROM: "URL", PATTERN: "/(\\d{2})_boll_agro_(\\d{4})(\\d{2})(\\d{2})(?:-\\d+)?\\.pdf$" },
      em: opc("n\\.\\s*\\d+/\\d{4}\\s+del\\s+(\\d{1,2})\\s+([a-z]+)\\s+(\\d{4})", 3, { FLAGS: "i" }),
      per: opc("(\\d{1,2})\\s+([a-z]+)\\s+(\\d{4})\\s*-\\s*(\\d{1,2})\\s+([a-z]+)\\s+(\\d{4})\\s*\\n\\s*Diario meteorologico", 6, { FLAGS: "i" }),
      cob: opc("(\\d{1,2})\\s+([a-z]+)\\s+(\\d{4})\\s*-\\s*(\\d{1,2})\\s+([a-z]+)\\s+(\\d{4})", 6, { FLAGS: "i" }),
      area: opc("valido per la provincia di ([A-Z][a-z]+)", 1),
    },
    DOCUMENT_ID: "IT-T2-051:BOLETIM:AGROMETEO:{b.2}-{b.1}",
    PUBLISHED_AT: "{em.3}-{em.2:MES_IT}-{em.1:DIA2}",
    PUBLISHED_AT_BASIS: "EMISSAO_DECLARADA_NO_BOLETIM · cabeçalho «n. NN/AAAA del <data>» do PDF",
    FACT_TIME: "{per.3}-{per.2:MES_IT}-{per.1:DIA2}/{per.6}-{per.5:MES_IT}-{per.4:DIA2}",
    FACT_TIME_BASIS: "PERIODO_LIGADO_AO_FATO_NO_TEXTO · «<data> - <data>» encabeça o «Diario meteorologico» (as observações da semana)",
    BULLETIN_PERIOD: "{cob.3}-{cob.2:MES_IT}-{cob.1:DIA2}/{cob.6}-{cob.5:MES_IT}-{cob.4:DIA2}",
    BULLETIN_PERIOD_BASIS: "PERIODO_DECLARADO_NO_BOLETIM · 2.ª linha «<data> - <data>» do PDF",
    FACT_LOCATION: "{area.1}",
    FACT_LOCATION_BASIS: "AREA_DECLARADA_NO_BOLETIM · «valido per la provincia di …»",
  },
};
const alvo = { url: "https://www.arpae.it/x/bollettini-2026/38_boll_agro_20260921.pdf", nome: "38_boll_agro_20260921.pdf" };
const com = (texto) => ({ leitores: { PDF_TEXT: () => texto } });

console.log("\n1 · O QUE O BOLETIM DIZ, SAI COM A BASE");

T("emissão, período e identidade do boletim ARPAE n.º 38", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo, com(ARPAE_TEXTO));
  assert.equal(id.DOCUMENT_ID, "IT-T2-051:BOLETIM:AGROMETEO:2026-38");
  assert.equal(id.PUBLISHED_AT, "2026-09-21");
  assert.ok(id.PUBLISHED_AT_BASIS.startsWith("EMISSAO_DECLARADA_NO_BOLETIM"));
  assert.ok(id.PUBLISHED_AT_BASIS.includes("n. 38/2026 del 21 settembre 2026"), "a base leva o trecho lido");
  assert.equal(id.FACT_TIME, "2026-09-14/2026-09-20");
  assert.ok(id.FACT_TIME_BASIS.includes("14 settembre 2026 - 20 settembre 2026"));
});

T("a área só entra quando o boletim a declara", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo, com(ARPAE_TEXTO + "valido per la provincia di Bologna\n"));
  assert.equal(id.FACT_LOCATION, "Bologna");
  assert.ok(id.FACT_LOCATION_BASIS.startsWith("AREA_DECLARADA_NO_BOLETIM"));
});

console.log("\n2 · D62: O QUE FALTA É NAO SEI, E O DOCUMENTO NÃO CAI");

T("sem área declarada: FACT_LOCATION NAO SEI com o porquê", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo, com(ARPAE_TEXTO));
  assert.equal(id.FACT_LOCATION, NAO_SEI);
  assert.ok(id.FACT_LOCATION_BASIS.startsWith("NAO SEI"));
  assert.ok(id.FACT_LOCATION_BASIS.includes("D62"));
});

T("PDF sem cabeçalho nem período: tudo NAO SEI, mas o DOCUMENT_ID sai", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo, com("um PDF sem as linhas do cabeçalho"));
  assert.equal(id.DOCUMENT_ID, "IT-T2-051:BOLETIM:AGROMETEO:2026-38", "falta de data nunca derruba o documento");
  assert.equal(id.PUBLISHED_AT, NAO_SEI);
  assert.equal(id.FACT_TIME, NAO_SEI);
  assert.ok(id.PUBLISHED_AT_BASIS.startsWith("NAO SEI"));
});

T("a data de coleta nunca entra: sem texto, PUBLISHED_AT continua NAO SEI", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo, com(""));
  assert.equal(id.PUBLISHED_AT, NAO_SEI);
  assert.ok(!/\d{4}-\d{2}-\d{2}/.test(id.PUBLISHED_AT));
});

console.log("\n3 · NUNCA SE INVENTA UMA DATA");

T("«31 febbraio» não é data de calendário → NAO SEI", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo,
    com("n. 9/2026 del 31 febbraio 2026\n1 febbraio 2026 - 7 febbraio 2026\nDiario meteorologico: sereno\n"));
  assert.equal(id.PUBLISHED_AT, NAO_SEI);
  assert.ok(id.PUBLISHED_AT_BASIS.includes("não é data de calendário"));
  assert.equal(id.FACT_TIME, "2026-02-01/2026-02-07");
});

console.log("\n3a · D69: O PERÍODO SÓ É FACT_TIME QUANDO O TEXTO O LIGA AO FACTO");

T("período sem ligação ao facto no texto → FACT_TIME NAO SEI, o período fica em BULLETIN_PERIOD", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo,
    com("n. 38/2026 del 21 settembre 2026\n14 settembre 2026 - 20 settembre 2026\nAvvertenze generali\n"));
  assert.equal(id.FACT_TIME, NAO_SEI);
  assert.equal(id.BULLETIN_PERIOD, "2026-09-14/2026-09-20");
  assert.ok(id.FACT_TIME_BASIS.includes("BULLETIN_PERIOD"), "o FACT_TIME diz onde ficou o período");
  assert.ok(id.FACT_TIME_BASIS.includes("D69"));
  assert.equal(id.PUBLISHED_AT, "2026-09-21", "a emissão continua a ser a publicação");
});

T("com a ligação no texto (Diario meteorologico) → FACT_TIME é o período, e a evidência fica igual", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo, com(ARPAE_TEXTO));
  assert.equal(id.FACT_TIME, "2026-09-14/2026-09-20");
  assert.ok(id.FACT_TIME_BASIS.startsWith("PERIODO_LIGADO_AO_FATO_NO_TEXTO"));
  assert.equal(id.BULLETIN_PERIOD, "2026-09-14/2026-09-20");
});

T("FACT_TIME num boletim sem base «PERIODO_LIGADO_AO_FATO_NO_TEXTO» é contrato inválido", () => {
  const c = structuredClone(ARPAE.IDENTITY);
  c.FACT_TIME_BASIS = "VALIDADE_DO_BOLETIM · «valido dal … al …»";
  assert.throws(() => conferirIdentidade("X", c), ContratoInvalido);
});

T("uma data de calendário nunca vira janela agronómica: nenhum campo de janela sai do motor", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo, com(ARPAE_TEXTO));
  assert.ok(!Object.keys(id).some((k) => /JANELA|WINDOW/i.test(k)), Object.keys(id).join(","));
});

T("mês que não é italiano → NAO SEI (o filtro MES_IT é fechado)", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo, com("n. 9/2026 del 3 setembro 2026\n"));
  assert.equal(id.PUBLISHED_AT, NAO_SEI);
  assert.ok(id.PUBLISHED_AT_BASIS.includes("MES_IT"));
});

T("período que começa depois de acabar → NAO SEI", () => {
  const id = identidadeDoContrato("IT-T2-051", ARPAE, alvo, com("20 settembre 2026 - 14 settembre 2026\nDiario meteorologico\n"));
  assert.equal(id.FACT_TIME, NAO_SEI);
  assert.ok(id.FACT_TIME_BASIS.includes("começa depois de acabar"));
});

T("ano de 2 dígitos no nome (Umbria «del 26_06_26») vira 2026 pelo ANO4", () => {
  const umbria = { IDENTITY: {
    STRATEGY: "CONTENT_CAPTURE",
    CAPTURES: {
      doc: { FROM: "URL", PATTERN: "^https?://[^/]+/?(.*?)/?$" },
      d: { FROM: "URL", PATTERN: "\\+del\\+{1,2}(\\d{1,2})_(\\d{1,2})_(\\d{2,4})", REQUIRED: false, DEFAULTS: ["x", "x", "x"] },
    },
    DOCUMENT_ID: "IT-T3-053:URL:{doc.1}",
    PUBLISHED_AT: "{d.3:ANO4}-{d.2:MES2}-{d.1:DIA2}",
    PUBLISHED_AT_BASIS: "EMISSAO_NO_NOME_DO_FICHEIRO · «del DD_MM_AA»",
  } };
  const u = "https://www.regione.umbria.it/documents/18/0/bollettino+olivo+n.1+del++26_06_26/c4ba5abf?version=1.0";
  const id = identidadeDoContrato("IT-T3-053", umbria, { url: u, nome: "c4ba5abf" });
  assert.equal(id.PUBLISHED_AT, "2026-06-26");
  assert.equal(id.FACT_TIME, NAO_SEI, "a data de emissão sozinha nunca preenche o FACT_TIME");
  assert.equal(id.FACT_LOCATION, NAO_SEI);
});

console.log("\n3b · VÁRIAS FORMAS POR CAMPO (ARSAC muda de forma de semana para semana)");

const ARSAC = { IDENTITY: {
  STRATEGY: "CONTENT_CAPTURE",
  CAPTURES: {
    doc: { FROM: "URL", PATTERN: "^https?://[^/]+/?(.*?)/?$" },
    pa: { FROM: "PAGE_TEXT", PATTERN: "Settimana\\s+\\d+\\s*\\((\\d{1,2})/(\\d{1,2})/(\\d{4})\\s*[–-]\\s*(\\d{1,2})/(\\d{1,2})/(\\d{4})\\)", REQUIRED: false, DEFAULTS: Array(6).fill("x") },
    pb: { FROM: "PAGE_TEXT", PATTERN: "Settimana\\s+\\d+\\s+dal\\s+(?:dal\\s+)?(\\d{1,2})/(\\d{1,2})\\s+al\\s+(\\d{1,2})/(\\d{1,2})/(\\d{4})", REQUIRED: false, DEFAULTS: Array(5).fill("x") },
  },
  DOCUMENT_ID: "IT-T2-148:URL:{doc.1}",
  BULLETIN_PERIOD: ["{pa.3}-{pa.2:MES2}-{pa.1:DIA2}/{pa.6}-{pa.5:MES2}-{pa.4:DIA2}",
                    "{pb.5}-{pb.2:MES2}-{pb.1:DIA2}/{pb.5}-{pb.4:MES2}-{pb.3:DIA2}"],
  BULLETIN_PERIOD_BASIS: "VALIDADE_DECLARADA_NA_PAGINA_DA_EDICAO · «Settimana NN (…)»",
  FACT_TIME_BASIS: "NAO_LIGADO · a página dá a validade do boletim, sem a ligar ao facto (D69)",
  PUBLISHED_AT_BASIS: "NAO_DECLARADA_NA_PAGINA · a edição só diz «Ultima modifica», que não é a emissão",
} };
const pagina = (t) => ({ leitores: { PAGE_TEXT: () => t } });
const ed = { url: "https://arsac.calabria.it/bollettino-x/", nome: "bollettino-x" };

T("forma 1: «Settimana 39 (22/09/2026 – 29/09/2026)»", () => {
  const id = identidadeDoContrato("IT-T2-148", ARSAC, ed, pagina("Pubblicato il bollettino Settimana 39 (22/09/2026 – 29/09/2026)"));
  assert.equal(id.BULLETIN_PERIOD, "2026-09-22/2026-09-29");
  assert.ok(id.BULLETIN_PERIOD_BASIS.includes("forma 1 de 2"));
  assert.equal(id.FACT_TIME, NAO_SEI, "validade sem ligação ao facto não é FACT_TIME (D69)");
});

T("forma 2: «Settimana 31 dal dal 20/07 al 04/08/2026» (o ano só no fim)", () => {
  const id = identidadeDoContrato("IT-T2-148", ARSAC, ed, pagina("Pubblicato il bollettino Settimana 31 dal dal 20/07 al 04/08/2026"));
  assert.equal(id.BULLETIN_PERIOD, "2026-07-20/2026-08-04");
  assert.ok(id.BULLETIN_PERIOD_BASIS.includes("forma 2 de 2"));
});

T("forma 2 na virada do ano não inventa: «dal 28/12 al 04/01/2027» → NAO SEI", () => {
  const id = identidadeDoContrato("IT-T2-148", ARSAC, ed, pagina("Settimana 1 dal 28/12 al 04/01/2027"));
  assert.equal(id.BULLETIN_PERIOD, NAO_SEI);
  assert.ok(id.BULLETIN_PERIOD_BASIS.includes("começa depois de acabar"));
});

T("BASE sem molde: o contrato diz porque o boletim não traz a emissão", () => {
  const id = identidadeDoContrato("IT-T2-148", ARSAC, ed, pagina("Settimana 39 (22/09/2026 – 29/09/2026)"));
  assert.equal(id.PUBLISHED_AT, NAO_SEI);
  assert.ok(id.PUBLISHED_AT_BASIS.includes("Ultima modifica"));
  assert.equal(id.FACT_LOCATION, NAO_SEI);
});

console.log("\n4 · O CONTRATO É CONFERIDO ANTES DE CORRER");

T("lista de moldes vazia é contrato inválido", () => {
  assert.throws(() => conferirIdentidade("X", { ...structuredClone(ARSAC.IDENTITY), BULLETIN_PERIOD: [] }), ContratoInvalido);
});

const variante = (mexe) => { const c = structuredClone(ARPAE.IDENTITY); mexe(c); return c; };

T("PUBLISHED_AT sem BASE é contrato inválido", () => {
  assert.throws(() => conferirIdentidade("X", variante((c) => { delete c.PUBLISHED_AT_BASIS; })), ContratoInvalido);
});

T("filtro fora do vocabulário é contrato inválido", () => {
  assert.throws(() => conferirIdentidade("X", variante((c) => { c.PUBLISHED_AT = "{em.3}-{em.2:ADIVINHA}-{em.1}"; })), ContratoInvalido);
});

T("campo de data a ler captura OBRIGATÓRIA é contrato inválido (D62)", () => {
  assert.throws(() => conferirIdentidade("X", variante((c) => { delete c.CAPTURES.em.REQUIRED; delete c.CAPTURES.em.DEFAULTS; })), ContratoInvalido);
});

T("campo que usa captura não declarada é contrato inválido", () => {
  assert.throws(() => conferirIdentidade("X", variante((c) => { c.FACT_LOCATION = "{zona.1}"; })), ContratoInvalido);
});

T("contrato antigo, sem BASE nenhuma, sai como antes (sem FACT_LOCATION)", () => {
  const velho = { IDENTITY: { STRATEGY: "CONTENT_CAPTURE", CAPTURES: { doc: { FROM: "URL", PATTERN: "^https?://[^/]+/?(.*?)/?$" } },
                              DOCUMENT_ID: "X:URL:{doc.1}", FACT_TIME: "UNKNOWN" } };
  const id = identidadeDoContrato("X", velho, { url: "https://a.it/b", nome: "b" });
  assert.deepEqual(Object.keys(id).sort(), ["DOCUMENT_ID", "FACT_TIME", "SOURCE_DATE", "SOURCE_DATE_ISO"]);
  assert.equal(id.FACT_TIME, "UNKNOWN");
});

console.log(`\n  PASSOU ${ok} · FALHOU ${mau}`);
process.exit(mau ? 1 : 0);
