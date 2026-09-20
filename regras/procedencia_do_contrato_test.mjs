// SINTONIA EAME — AS PROVAS DA PROCEDÊNCIA DO CONTRATO
//
//     node regras/procedencia_do_contrato_test.mjs
//
// Guardam que os quatro campos respondem a quatro perguntas, e que nenhum
// pode voltar a responder pela do vizinho.

import { strict as assert } from "node:assert";
import { readFileSync } from "node:fs";
import {
  SOURCE_CONTRACT_VERSION, hashDoContrato, hashDaConfiguracao,
  contratoExecutavel, CAMPOS_DO_HASH,
} from "./procedencia_do_contrato.mjs";
import { CONTRACTS } from "./italy_contracts.mjs";
import { CONTRATO_MOTOR_VERSAO } from "./motor_de_rota.mjs";

let ok = 0, mau = 0;
const T = (nome, fn) => {
  try { fn(); console.log(`  PASS  ${nome}`); ok++; }
  catch (e) { console.log(`  FAIL  ${nome}\n        ${e.message}`); mau++; }
};

console.log("\n1 · A VERSÃO DO SCHEMA SUBIU, E TEM UM DONO SÓ");

T("SOURCE_CONTRACT_VERSION = italy-contracts-v2", () => {
  assert.equal(SOURCE_CONTRACT_VERSION, "italy-contracts-v2");
});

T("o coletor NÃO digita a própria versão", () => {
  // O defeito medido: `SOURCE_CONTRACT_VERSION: "italy-contracts-v1"` escrito
  // à mão dentro do consumidor. Se voltar, isto morde.
  const src = readFileSync(new URL("../coleta/italy_pilot_collect.mjs", import.meta.url), "utf8");
  const codigo = src.split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");
  assert.ok(!/SOURCE_CONTRACT_VERSION\s*:\s*["']italy-contracts/.test(codigo),
    "o coletor voltou a afirmar a sua própria versão");
  assert.ok(codigo.includes("procedencia_do_contrato.mjs"),
    "o coletor deixou de importar o dono da versão");
});

T("SOURCE_CONTRACT_VERSION_OWNER_COUNT = 1", () => {
  // Um literal `italy-contracts-vN` fora do owner é um segundo dono.
  const ficheiros = ["../coleta/italy_pilot_collect.mjs", "./italy_contracts.mjs", "./motor_de_rota.mjs"];
  for (const f of ficheiros) {
    const src = readFileSync(new URL(f, import.meta.url), "utf8");
    const codigo = src.split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");
    assert.ok(!/["']italy-contracts-v\d["']/.test(codigo), `${f} declara a versão`);
  }
});

console.log("\n2 · OS QUATRO CAMPOS NÃO SE SUBSTITUEM");

T("versão, hash do contrato e hash da config são três valores distintos", () => {
  const c = CONTRACTS["IT-T3-011"];
  const h = hashDoContrato(c);
  const cfg = hashDaConfiguracao({
    sourceId: "IT-T3-011", contractHash: h,
    contractVersion: SOURCE_CONTRACT_VERSION, motorVersao: CONTRATO_MOTOR_VERSAO,
  });
  assert.notEqual(h, cfg);
  assert.notEqual(h, SOURCE_CONTRACT_VERSION);
  assert.notEqual(cfg, SOURCE_CONTRACT_VERSION);
});

console.log("\n3 · M1 — mudar campo EXECUTÁVEL muda o hash");

T("M1 · mexer no LINK_PATTERN muda SOURCE_CONTRACT_HASH", () => {
  const a = { ACQUISITION: { STRATEGY: "HTML_LINK_DISCOVERY", INDEX_URL: "u", LINK_PATTERN: "x" } };
  const b = { ACQUISITION: { STRATEGY: "HTML_LINK_DISCOVERY", INDEX_URL: "u", LINK_PATTERN: "y" } };
  assert.notEqual(hashDoContrato(a), hashDoContrato(b));
});

T("M1b · mexer no EXPECTED_MIME (RegExp) muda o hash", () => {
  // `JSON.stringify(/x/)` devolve `{}`. Se a serialização fosse crua, estes
  // dois contratos teriam o MESMO hash — e o hash estaria a mentir.
  const a = { EXPECTED_MIME: /^application\/pdf/ };
  const b = { EXPECTED_MIME: /^text\/csv/ };
  assert.notEqual(hashDoContrato(a), hashDoContrato(b));
});

console.log("\n4 · M2 — mudar PROSA não muda o hash");

T("M2 · corrigir DISCOVERY_METHOD não muda SOURCE_CONTRACT_HASH", () => {
  const base = { ACQUISITION: { STRATEGY: "STATIC_ENDPOINT", URL: "https://x.it/a" } };
  const a = { ...base, DISCOVERY_METHOD: "a pagina lista os PDFs" };
  const b = { ...base, DISCOVERY_METHOD: "a página lista os PDF, com acento" };
  assert.equal(hashDoContrato(a), hashDoContrato(b),
    "um comentário mudou a procedência da coleta");
});

T("M2b · DOCUMENT_ID_RULE em prosa não entra no hash", () => {
  const base = { IDENTITY: { STRATEGY: "FILENAME_CAPTURE", PATTERN: "(x)", DOCUMENT_ID: "T:$1" } };
  assert.equal(
    hashDoContrato({ ...base, DOCUMENT_ID_RULE: "AGRIOS:DIRETTIVE:{ANO}" }),
    hashDoContrato({ ...base, DOCUMENT_ID_RULE: "outra frase qualquer" }));
});

T("a lista do hash não inclui campos humanos", () => {
  for (const humano of ["DISCOVERY_METHOD", "RETRIEVAL_METHOD", "DOCUMENT_ID_RULE",
                        "aviso_de_idioma", "NOTA", "LEI", "classificacao_honesta"]) {
    assert.ok(!CAMPOS_DO_HASH.includes(humano), `${humano} entrou no hash`);
  }
});

console.log("\n5 · DETERMINISMO");

T("SOURCE_CONTRACT_HASH_DETERMINISTIC — ordem das chaves não conta", () => {
  const a = { ACQUISITION: { STRATEGY: "STATIC_ENDPOINT", URL: "u", NAME: "n" }, OUTPUT_TYPE: "PDF" };
  const b = { OUTPUT_TYPE: "PDF", ACQUISITION: { NAME: "n", URL: "u", STRATEGY: "STATIC_ENDPOINT" } };
  assert.equal(hashDoContrato(a), hashDoContrato(b));
});

T("CONFIG_HASH_DETERMINISTIC — duas corridas iguais dão o mesmo hash", () => {
  const args = { sourceId: "IT-X", contractHash: "abc",
                 contractVersion: SOURCE_CONTRACT_VERSION, motorVersao: CONTRATO_MOTOR_VERSAO };
  assert.equal(hashDaConfiguracao(args), hashDaConfiguracao(args));
});

T("o relógio NÃO entra no CONFIG_HASH", () => {
  // Se RUN_ID ou STARTED_AT entrassem, o campo mediria «quando» em vez de
  // «com quê», e nunca responderia «esta corrida é igual à anterior?».
  const src = readFileSync(new URL("./procedencia_do_contrato.mjs", import.meta.url), "utf8");
  const ini = src.indexOf("export function hashDaConfiguracao");
  const corpo = src.slice(ini, src.indexOf("\n}", ini));
  for (const proibido of ["RUN_ID", "STARTED_AT", "CAPTURED_AT", "Date.now"]) {
    assert.ok(!corpo.includes(proibido), `${proibido} entrou no CONFIG_HASH`);
  }
});

T("mudar o modo muda o CONFIG_HASH", () => {
  const base = { sourceId: "IT-X", contractHash: "abc",
                 contractVersion: SOURCE_CONTRACT_VERSION, motorVersao: CONTRATO_MOTOR_VERSAO };
  assert.notEqual(hashDaConfiguracao({ ...base, mode: "BASELINE" }),
                  hashDaConfiguracao({ ...base, mode: "INCREMENTAL" }));
});

console.log("\n6 · M3/M4 — o recibo tem de carregar os campos");

T("M3 · o recibo escreve SOURCE_CONTRACT_HASH", () => {
  const src = readFileSync(new URL("../coleta/italy_pilot_collect.mjs", import.meta.url), "utf8");
  const codigo = src.split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");
  assert.ok(codigo.includes("SOURCE_CONTRACT_HASH:"), "o recibo deixou de carregar o hash do contrato");
});

T("M4 · o recibo escreve CONFIG_HASH", () => {
  const src = readFileSync(new URL("../coleta/italy_pilot_collect.mjs", import.meta.url), "utf8");
  const codigo = src.split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");
  assert.ok(codigo.includes("CONFIG_HASH:"), "o recibo deixou de carregar o hash da configuração");
});

T("o recibo escreve CONTRATO_MOTOR_VERSAO", () => {
  const src = readFileSync(new URL("../coleta/italy_pilot_collect.mjs", import.meta.url), "utf8");
  const codigo = src.split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");
  assert.ok(codigo.includes("CONTRATO_MOTOR_VERSAO,"), "o recibo deixou de nomear o motor");
});

console.log("\n7 · M5 — contract version não volta a ser policy version");

T("M5 · o relatório do fluxo não usa contract version como policy version", () => {
  const src = readFileSync(new URL("../system-map/scripts/relatorio_do_fluxo.py", import.meta.url), "utf8");
  const codigo = src.split("\n").filter((l) => !l.trim().startsWith("#")).join("\n");
  assert.ok(!/'POLICY_VERSION':\s*c\.get\('SOURCE_CONTRACT_VERSION'\)/.test(codigo),
    "a confusão semântica voltou");
});

console.log("\n8 · O CONTRATO NÃO CARREGA CÓDIGO");

T("uma função dentro do contrato faz o hash gritar", () => {
  assert.throws(() => hashDoContrato({ ACQUISITION: { STRATEGY: "STATIC_ENDPOINT", URL: () => "x" } }),
    /funcao|função/i);
});

console.log("\n9 · OS 14 CONTRATOS REAIS TÊM HASH ESTÁVEL");

T("todos os contratos produzem hash e nenhum colide", () => {
  const hs = Object.entries(CONTRACTS).map(([k, v]) => [k, hashDoContrato(v)]);
  for (const [k, h] of hs) assert.equal(h.length, 64, `${k} sem hash`);
  // Dois contratos diferentes com o mesmo hash executável significaria que
  // o hash não distingue o que devia.
  const distintos = new Set(hs.map(([, h]) => h));
  assert.equal(distintos.size, hs.length, "dois contratos partilham hash executável");
});

console.log(`\n  PASSOU ${ok} · FALHOU ${mau}\n`);
if (mau) process.exit(1);
