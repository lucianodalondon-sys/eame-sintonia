// A PROVA DE PONTA A PONTA — O COLETOR INTEIRO, DUAS RODADAS, ZERO REDE.
//
//     node provas/paridade_duas_rodadas.mjs
//
// ⚠️ PORQUE ESTA PROVA EXISTE, E PORQUE NAO CHEGAVA PROVAR A REGRA SOZINHA.
// Em 2026-09-22 mediu-se isto: `regras/incrementalidade.mjs` tinha md5
// identico no laboratorio e na producao, o teste dela passava, a prova dela
// passava — e a producao redescarregava 39 de 39 detalhes. A peca estava
// certa; ninguem a chamava de dentro do coletor.
//
//     UMA PROVA QUE EXERCITA A REGRA ISOLADA VOLTA A DAR VERDE
//     COM A ROTA DESLIGADA. ESTA CHAMA O COLETOR.
//
// Corre-se numa raiz descartavel em `$TEMP`: livro proprio, armazem proprio.
// Nao toca no livro da ops nem no do repositorio.
//
// Os bytes vem de `forcarBuf`, que e o mecanismo que esta casa ja usa para
// correr sem rede. Cada chamada e CONTADA — e a contagem e a prova: uma
// rodada que nao bate a porta nao incrementa o contador.

import { mkdtempSync, rmSync, readFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "paridade-"));
process.env.ITALY_OPS_ROOT = RAIZ;

// O import tem de vir DEPOIS do env: `RAIZ` do coletor le-se no carregamento
// do modulo. Trocar a ordem faria a prova escrever no repositorio.
const { executarRodada } = await import("../coleta/italy_pilot_collect.mjs");

// ── A FONTE DE PROVA: uma pagina HTML com volateis e com materia ──────────
const FONTE = "IT-T3-005";   // contrato existente, EXPECTED_SIGNATURE "<"

// ⚠️ A PROVA DECLARA O SEU CENARIO, E NAO O PEDE EMPRESTADO AO CONTRATO.
// Apanhado em 2026-09-22, minutos depois de os contratos ganharem
// `RECOLLECTION`: esta prova passava a vermelho porque IT-T3-005 tinha
// acabado de ser declarada `MUTABLE` — e uma fonte MUTABLE revalida SEMPRE,
// que e o comportamento certo dela e o oposto do que estas rodadas medem.
//
//     UMA PROVA QUE DEPENDE DE CONFIGURACAO ALHEIA
//     MEDE A CONFIGURACAO, E NAO O QUE DIZ MEDIR.
//
// As rodadas 1 a 3 sao sobre a fonte que NAO declara nada — que e o caso de
// 179 dos 186 contratos hoje. Fixa-se aqui, em voz alta, e restaura-se no
// fim. A rodada 4 muda para `MUTABLE` de proposito, para medir o outro ramo.
const { CONTRACTS } = await import("../regras/italy_contracts.mjs");
const RECOLLECTION_ORIGINAL = CONTRACTS[FONTE].RECOLLECTION;
CONTRACTS[FONTE].RECOLLECTION = undefined;   // «UNKNOWN» — nada declarado
let VISITAS = 0;
const pagina = (v = {}) => Buffer.from(`<!DOCTYPE html><html><head>
<meta property="article:modified_time" content="${v.hora ?? "2026-09-22T02:01:41+00:00"}" />
</head><body>
<div class="views">${v.visitas ?? 134}</div>
<p>Bollettino del periodo dal 01-09-2026 al 07-09-2026</p>
<p id="materia">${v.corpo ?? "Infestazione attiva: bassa"}</p>
<form><input name="_token" type="hidden" value="${v.token ?? "A".repeat(40)}"></form>
</body></html>`, "latin1");

let estado = {};
const transporte = () => { VISITAS++; return pagina(estado); };

const contadores = [];
async function rodada(nome) {
  const antes = VISITAS;
  const { resumo, detalhes } = await executarRodada({
    runId: `PROVA_${nome}_${Date.now()}`, apenas: [FONTE],
    forcarBuf: transporte, pularParse: true, nota: `prova offline ${nome}`,
  });
  const c = resumo.contadores;
  contadores.push({ nome, PEDIDOS_AO_TRANSPORTE: VISITAS - antes, ...c });
  return { resumo, detalhes, c, pedidos: VISITAS - antes };
}

let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};

try {
  console.log("\n══ RODADA 1 · o documento e novo ═══════════════════════════════");
  const r1 = await rodada("RUN1");
  t("RUN1 bate a porta uma vez e cria o documento", () => {
    assert.equal(r1.pedidos, 1, `esperava 1 ida a fonte, houve ${r1.pedidos}`);
    assert.equal(r1.c.DETAIL_REQUESTS, 1);
    assert.equal(r1.c.DETAIL_NEW, 1);
    assert.equal(r1.c.SKIPPED_KNOWN, 0);
    assert.equal(r1.c.RAW_OBJECTS_CREATED, 1);
  });

  console.log("\n══ RODADA 2 · o mesmo endereco, ja conhecido ═══════════════════");
  // O sitio faz o que os sitios reais fazem: regista a visita e cunha token.
  estado = { visitas: 135, hora: "2026-09-22T02:06:03+00:00", token: "B".repeat(40) };
  const r2 = await rodada("RUN2");
  t("RUN2 NAO BATE A PORTA ao detalhe ja conhecido", () => {
    assert.equal(r2.pedidos, 0, `a RUN2 foi a fonte ${r2.pedidos} vez(es) — devia ser 0`);
    assert.equal(r2.c.DETAIL_REQUESTS, 0);
    assert.equal(r2.c.SKIPPED_KNOWN, 1);
    assert.equal(r2.c.UNNECESSARY_REFETCHES, 0);
  });
  t("RUN2 nao escreve CHANGED_IN_PLACE nenhum", () => {
    assert.equal(r2.c.CHANGED_IN_PLACE, 0);
    assert.equal(r2.c.RAW_OBJECTS_CREATED, 0);
  });
  t("o salto NAO foi para o livro", () => {
    const livro = readFileSync(join(RAIZ, "data/collection-ledger/italy/observations.ndjson"), "utf8")
      .split("\n").filter(Boolean).map(JSON.parse);
    assert.equal(livro.length, 1, `o livro tem ${livro.length} linhas; a RUN2 devia nao ter escrito nenhuma`);
    assert.equal(livro[0].OBSERVATION_RESULT, "BASELINE_DOCUMENT");
  });

  console.log("\n══ RODADA 3 · a mesma corrida outra vez — a memoria aguenta ════");
  // ⚠️ A RATOEIRA QUE O SALTO PODIA TER ARMADO: se o `SKIP_KNOWN` da RUN2
  // tivesse ido para o livro com um resultado fora de
  // `RESULTADOS_COM_DOCUMENTO`, `memoriaDosDetalhes()` leria a ULTIMA linha
  // como «nunca se guardou documento deste endereco» e a RUN3 voltava a
  // descarregar tudo. Um salto que se auto-desfaz na corrida seguinte parece
  // incrementalidade e nao e.
  const r3 = await rodada("RUN3");
  t("RUN3 continua a saltar — o salto nao envenenou a memoria", () => {
    assert.equal(r3.pedidos, 0);
    assert.equal(r3.c.SKIPPED_KNOWN, 1);
  });

  console.log("\n══ RODADA 4 · a revalidacao legitima, e o que ela ve ═══════════");
  // Com `RECOLLECTION.DETAIL_CONTENT = "MUTABLE"` ha razao NOMEADA para ir.
  // A rede gasta-se de proposito — e e aqui que a DEFESA 2 tem de falar.
  CONTRACTS[FONTE].RECOLLECTION = { DETAIL_CONTENT: "MUTABLE" };
  estado = { visitas: 999, hora: "2026-09-23T00:00:00+00:00", token: "C".repeat(40) };
  const r4 = await rodada("RUN4");
  t("com razao declarada, a RUN4 VAI — e diz porque", () => {
    assert.equal(r4.pedidos, 1, "com RECOLLECTION MUTABLE a ida e legitima");
    assert.equal(r4.c.REVALIDATED, 1);
    assert.equal(r4.c.REVISIT_REASONS.CONTRACT_DECLARES_MUTABLE, 1);
    assert.equal(r4.c.UNNECESSARY_REFETCHES, 0, "ida com razao nao e desperdicio");
  });
  t("so mexeram volateis -> SEEN_AGAIN, e NAO CHANGED_IN_PLACE", () => {
    assert.equal(r4.c.CHANGED_IN_PLACE, 0, "isto era o falso positivo");
    assert.equal(r4.c.SEEN_AGAIN, 1);
    assert.equal(r4.c.VOLATILE_ONLY_NOT_CHANGED, 1);
    assert.equal(r4.c.RAW_OBJECTS_CREATED, 0, "nao nasce versao nova para arrumar ruido");
  });
  t("a linha do livro traz OLD/NEW_NORMALIZED_HASH e MATERIAL_DIFF = false", () => {
    const livro = readFileSync(join(RAIZ, "data/collection-ledger/italy/observations.ndjson"), "utf8")
      .split("\n").filter(Boolean).map(JSON.parse);
    const u = livro.at(-1);
    assert.equal(u.OBSERVATION_RESULT, "SEEN_AGAIN");
    assert.equal(u.MATERIAL_DIFF, false);
    assert.equal(u.VOLATILE_DIFFERENCE, true);
    assert.ok(u.OLD_NORMALIZED_HASH && u.NEW_NORMALIZED_HASH);
    assert.equal(u.OLD_NORMALIZED_HASH, u.NEW_NORMALIZED_HASH);
    assert.ok(u.VOLATILE_FRAGMENTS.includes("CONTADOR_DE_VISITAS"));
  });
  t("RAW_SHA256 continua a bater com os bytes em RAW_PATH (sem SHA_MISMATCH)", () => {
    const livro = readFileSync(join(RAIZ, "data/collection-ledger/italy/observations.ndjson"), "utf8")
      .split("\n").filter(Boolean).map(JSON.parse);
    const u = livro.at(-1);
    assert.ok(existsSync(u.RAW_PATH), `RAW_PATH nao existe: ${u.RAW_PATH}`);
    const disco = createHash("sha256").update(readFileSync(u.RAW_PATH)).digest("hex");
    assert.equal(disco, u.RAW_SHA256,
      "o livro aponta para bytes que nao batem — e isto acende SHA_MISMATCH no censo da coorte");
    assert.notEqual(u.RECEIVED_RAW_SHA256, u.RAW_SHA256,
      "os bytes que chegaram agora tem de estar noutro campo, e nao neste");
  });

  console.log("\n══ RODADA 5 · o outro lado — materia nova CONTINUA a ser vista ══");
  estado = { visitas: 1000, token: "D".repeat(40), corpo: "Infestazione attiva: ALTA" };
  const r5 = await rodada("RUN5");
  t("uma palavra da materia muda -> DOCUMENT_CHANGED_IN_PLACE", () => {
    assert.equal(r5.pedidos, 1);
    assert.equal(r5.c.CHANGED_IN_PLACE, 1, "o normalizador estava a cegar a deteccao");
    assert.equal(r5.c.SEEN_AGAIN, 0);
    assert.equal(r5.c.RAW_OBJECTS_CREATED, 1, "materia nova guarda-se");
  });
  t("a linha do CHANGED traz MATERIAL_DIFF = true e hashes que diferem", () => {
    const livro = readFileSync(join(RAIZ, "data/collection-ledger/italy/observations.ndjson"), "utf8")
      .split("\n").filter(Boolean).map(JSON.parse);
    const u = livro.at(-1);
    assert.equal(u.OBSERVATION_RESULT, "DOCUMENT_CHANGED_IN_PLACE");
    assert.equal(u.MATERIAL_DIFF, true);
    assert.notEqual(u.OLD_NORMALIZED_HASH, u.NEW_NORMALIZED_HASH);
    assert.equal(u.NORMALIZER_WARNING, undefined);
  });
  // (o restauro do contrato faz-se no `finally`, com o resto)

  console.log("\n══ CENSO DAS CINCO RODADAS ═════════════════════════════════════");
  for (const c of contadores) {
    console.log(`  ${c.nome.padEnd(5)} rede=${c.PEDIDOS_AO_TRANSPORTE}  DETAIL_REQUESTS=${c.DETAIL_REQUESTS}`
      + `  NEW=${c.DETAIL_NEW} SKIPPED_KNOWN=${c.SKIPPED_KNOWN} REVALIDATED=${c.REVALIDATED}`
      + `  CHANGED=${c.CHANGED_IN_PLACE} SEEN_AGAIN=${c.SEEN_AGAIN}`
      + `  UNNECESSARY_REFETCHES=${c.UNNECESSARY_REFETCHES}`);
  }
  t("UNNECESSARY_REFETCHES = 0 em TODAS as rodadas", () => {
    for (const c of contadores) assert.equal(c.UNNECESSARY_REFETCHES, 0, `${c.nome} desperdicou pedido`);
  });
  t("DETAIL_REQUESTS == idas reais ao transporte, rodada a rodada", () => {
    for (const c of contadores) assert.equal(c.DETAIL_REQUESTS, c.PEDIDOS_AO_TRANSPORTE,
      `${c.nome}: o contador diz ${c.DETAIL_REQUESTS} e o transporte foi chamado ${c.PEDIDOS_AO_TRANSPORTE}`);
  });
} finally {
  // ⚠️ O CONTRATO E UM OBJECTO PARTILHADO NO PROCESSO. Deixa-lo mexido faria
  // a proxima prova do mesmo processo medir a configuracao desta.
  CONTRACTS[FONTE].RECOLLECTION = RECOLLECTION_ORIGINAL;
  rmSync(RAIZ, { recursive: true, force: true });
}

console.log(`\n  ${passou} passaram, ${falhou} falharam`);
if (falhou) process.exit(1);

import { createHash } from "node:crypto";
