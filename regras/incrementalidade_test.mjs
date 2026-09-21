// SINTONIA EAME — AS PROVAS DA REGRA DE REVISITA
//
//     node regras/incrementalidade_test.mjs
//
// O QUE ELAS GUARDAM
// -------------------
// Que um detalhe que ja se tem NAO volta a ser descarregado sem razao
// nomeada, e que a decisao e tomada ANTES de a rede ser gasta.
//
// NENHUMA PROVA AQUI ABRE A REDE — e nao por disciplina: a funcao que decide
// nao recebe bytes nem sabe o que e um pedido. Nao ha por onde.

import { strict as assert } from "node:assert";
import {
  DECISOES, RAZOES_DE_REVISITA, MUTABILIDADE,
  RESULTADOS_COM_DOCUMENTO, RESULTADOS_SEM_DOCUMENTO,
  RegraInvalida, recolheitaDoContrato, memoriaDosDetalhes,
  decidirSobreDetalhe, decidirSobreIndice, censoDasDecisoes,
} from "./incrementalidade.mjs";

let ok = 0, mau = 0;
const T = (nome, fn) => {
  try { fn(); console.log(`  PASS  ${nome}`); ok++; }
  catch (e) { console.log(`  FAIL  ${nome}\n        ${e.message}`); mau++; }
};

const URL1 = "https://www.myfruit.it/news/uma-noticia";
const obsOk = (extra = {}) => ({
  SOURCE_ID: "IT-T10-018", SOURCE_URL: URL1, OBSERVATION_RESULT: "NEW_DOCUMENT",
  CAPTURED_AT: "2026-09-21T19:26:11.909Z", ...extra,
});

console.log("\n1 · A LEI DE BASE — conhecido com sucesso NAO se revisita");

T("detalhe NUNCA visto -> FETCH", () => {
  const d = decidirSobreDetalhe(URL1, { memoria: new Map() });
  assert.equal(d.DECISAO, "FETCH");
  assert.equal(d.CONHECIDO, false);
  assert.equal(d.RAZAO, null, "inventou razao para um endereco novo");
});

T("detalhe conhecido COM documento -> SKIP_KNOWN por omissao", () => {
  const d = decidirSobreDetalhe(URL1, { memoria: memoriaDosDetalhes([obsOk()]) });
  assert.equal(d.DECISAO, "SKIP_KNOWN", "tornou a ir buscar o que ja tinha");
  assert.equal(d.RAZAO, null);
});

// ⚠️ OS NOMES ESTAO ESCRITOS A MAO, E ISSO E A CORRECCAO DE UM SOBREVIVENTE.
// A primeira versao destas duas provas fazia `for (const r of
// RESULTADOS_COM_DOCUMENTO)` — lia a LISTA QUE ESTAVA A TESTAR. O red team
// apanhou-o: tirar `SEEN_AGAIN` da lista deixou a suite em 22 PASSOU · 0
// FALHOU, porque o ciclo simplesmente deixou de o visitar.
//
//     UMA PROVA QUE LE A LISTA SOB ATAQUE NAO PROVA A LISTA:
//     PROVA QUE O CICLO SABE ANDAR.
//
// Escrito a mao, apagar uma entrada da lista faz a prova ficar vermelha — que
// e o que ela existe para fazer. O `length` fecha a porta ao contrario:
// acrescentar em silencio tambem reprova.
const COM_DOCUMENTO = ["BASELINE_DOCUMENT", "NEW_DOCUMENT", "DOCUMENT_CHANGED_IN_PLACE",
                       "SEMANTIC_ID_CHANGED_SAME_BYTES", "SEEN_AGAIN"];
const SEM_DOCUMENTO = ["DISCOVERY_FAILED", "TRANSPORT_OR_EMPTY",
                       "BYTE_VALIDATION_FAILED", "IDENTITY_FAILED"];

T("os CINCO resultados com documento contam todos como conhecido", () => {
  for (const r of COM_DOCUMENTO) {
    const d = decidirSobreDetalhe(URL1, {
      memoria: memoriaDosDetalhes([obsOk({ OBSERVATION_RESULT: r })]) });
    assert.equal(d.DECISAO, "SKIP_KNOWN", `${r} devia contar como ja tenho`);
  }
  assert.deepEqual([...RESULTADOS_COM_DOCUMENTO].sort(), [...COM_DOCUMENTO].sort(),
    "a lista do modulo afastou-se da lista provada a mao");
});

T("os QUATRO resultados sem documento NAO contam — volta-se, e diz-se porque", () => {
  for (const r of SEM_DOCUMENTO) {
    const d = decidirSobreDetalhe(URL1, {
      memoria: memoriaDosDetalhes([obsOk({ OBSERVATION_RESULT: r })]) });
    assert.equal(d.DECISAO, "FETCH", `${r} foi tratado como documento guardado`);
    assert.equal(d.RAZAO, "PREVIOUS_ATTEMPT_FAILED");
  }
  assert.deepEqual([...RESULTADOS_SEM_DOCUMENTO].sort(), [...SEM_DOCUMENTO].sort(),
    "a lista do modulo afastou-se da lista provada a mao");
});

// ⚠️ `SEEN_AGAIN` TEM PROVA PROPRIA, e nao so um lugar num ciclo. E o caso
// que mais facilmente se perde: parece «nao trouxe nada» e significa o
// contrario — o documento esta guardado, os bytes sao os mesmos, a visita
// confirmou. Se ele cair da lista, cada `SEEN_AGAIN` volta a ser
// descarregado para sempre, e nada mais na suite da por isso.
T("SEEN_AGAIN significa QUE SE TEM o documento — nao que nao se trouxe nada", () => {
  assert.ok(RESULTADOS_COM_DOCUMENTO.includes("SEEN_AGAIN"),
    "SEEN_AGAIN saiu da lista dos que tem documento — cada revisita volta a descarregar");
  assert.ok(!RESULTADOS_SEM_DOCUMENTO.includes("SEEN_AGAIN"));
  const d = decidirSobreDetalhe(URL1, {
    memoria: memoriaDosDetalhes([obsOk({ OBSERVATION_RESULT: "SEEN_AGAIN" })]) });
  assert.equal(d.DECISAO, "SKIP_KNOWN");
});

// ⚠️ ESTA E A PROVA CENTRAL DA MISSAO, E NASCEU DE UM NUMERO.
// Medido na CANONICAL-MICRO-V1: 83 dos 85 artigos sairam
// DOCUMENT_CHANGED_IN_PLACE na segunda visita. Diferenca real: 374 linhas em
// 86 441, e ZERO texto editorial — carimbos de hora, nonces, farois de
// analytics e o CONTADOR DE VISITAS DA PAGINA, que subiu porque fomos nos
// visita-la.
//
//     A NOSSA VISITA DEIXA PEGADA. COMPARAR DEPOIS DE VISITAR
//     E MEDIR A PROPRIA PEGADA E CHAMAR-LHE NOTICIA.
console.log("\n2 · A PEGADA DA NOSSA VISITA NAO PODE ENTRAR NA DECISAO");

T("a decisao NAO muda quando os bytes mudam — nem sabe o que e um byte", () => {
  const mem = memoriaDosDetalhes([obsOk({ RAW_SHA256: "a".repeat(64) })]);
  const base = decidirSobreDetalhe(URL1, { memoria: mem });
  // As mesmas condicoes, com todos os tentadores que a pegada produz:
  for (const veneno of [
    { bytes: Buffer.from("<div class=\"views\">367</div>") },
    { sha256: "b".repeat(64) },
    { corpo: "<meta property=\"article:modified_time\" content=\"2026-09-21T19:34:54+00:00\">" },
    { resposta: { status: 200 } },
  ]) {
    const d = decidirSobreDetalhe(URL1, { memoria: mem, ...veneno });
    assert.equal(d.DECISAO, base.DECISAO,
      `a decisao mudou por causa de ${Object.keys(veneno)[0]} — a regra olhou para a pegada`);
  }
  assert.equal(base.DECISAO, "SKIP_KNOWN");
});

T("DOCUMENT_CHANGED_IN_PLACE no livro NAO justifica tornar a ir", () => {
  // O livro real tem 83 destes, e sao falsos. Se «mudou da ultima vez» virasse
  // razao, a regra herdava o defeito que existe para corrigir — e cada corrida
  // justificaria a seguinte, para sempre.
  const mem = memoriaDosDetalhes([
    obsOk({ OBSERVATION_RESULT: "NEW_DOCUMENT", CAPTURED_AT: "2026-09-21T19:26:11Z" }),
    obsOk({ OBSERVATION_RESULT: "DOCUMENT_CHANGED_IN_PLACE", CAPTURED_AT: "2026-09-21T19:34:54Z" }),
  ]);
  const d = decidirSobreDetalhe(URL1, { memoria: mem });
  assert.equal(d.DECISAO, "SKIP_KNOWN",
    "«mudou da ultima vez» virou razao, e o ciclo fecha-se sobre si mesmo");
});

console.log("\n3 · REVISITAR EXIGE RAZAO NOMEADA — e as razoes sao cinco");

T("contrato que declara MUTABLE -> REVALIDATE, com o nome da razao", () => {
  const d = decidirSobreDetalhe(URL1, {
    memoria: memoriaDosDetalhes([obsOk()]),
    contrato: { RECOLLECTION: { DETAIL_CONTENT: "MUTABLE" } } });
  assert.equal(d.DECISAO, "REVALIDATE");
  assert.equal(d.RAZAO, "CONTRACT_DECLARES_MUTABLE");
});

T("TTL vencido -> REVALIDATE; TTL por vencer -> SKIP", () => {
  const mem = memoriaDosDetalhes([obsOk({ CAPTURED_AT: "2026-09-21T00:00:00Z" })]);
  const contrato = { RECOLLECTION: { DETAIL_CONTENT: "IMMUTABLE", TTL_SECONDS: 3600 } };
  const vencido = decidirSobreDetalhe(URL1, { memoria: mem, contrato, agora: "2026-09-21T12:00:00Z" });
  assert.equal(vencido.DECISAO, "REVALIDATE");
  assert.equal(vencido.RAZAO, "TTL_EXPIRED");
  const fresco = decidirSobreDetalhe(URL1, { memoria: mem, contrato, agora: "2026-09-21T00:30:00Z" });
  assert.equal(fresco.DECISAO, "SKIP_KNOWN", "foi antes do prazo acabar");
});

T("TTL que nao da para calcular NAO expira — nao sei nao autoriza rede", () => {
  const mem = memoriaDosDetalhes([obsOk({ CAPTURED_AT: "data-que-ninguem-le" })]);
  const d = decidirSobreDetalhe(URL1, {
    memoria: mem, agora: "2026-09-21T12:00:00Z",
    contrato: { RECOLLECTION: { DETAIL_CONTENT: "IMMUTABLE", TTL_SECONDS: 60 } } });
  assert.equal(d.DECISAO, "SKIP_KNOWN", "uma data ilegivel virou autorizacao para gastar rede");
});

T("evidencia canonica que exige -> REVALIDATE nomeado", () => {
  const d = decidirSobreDetalhe(URL1, {
    memoria: memoriaDosDetalhes([obsOk()]), evidenciaCanonicaExige: true });
  assert.equal(d.RAZAO, "CANONICAL_EVIDENCE_REQUIRES");
});

T("toda razao devolvida pertence ao vocabulario fechado", () => {
  const casos = [
    { contrato: { RECOLLECTION: { DETAIL_CONTENT: "MUTABLE" } } },
    { contrato: { RECOLLECTION: { DETAIL_CONTENT: "IMMUTABLE", TTL_SECONDS: 1 } }, agora: "2027-01-01T00:00:00Z" },
    { evidenciaCanonicaExige: true },
  ];
  for (const c of casos) {
    const d = decidirSobreDetalhe(URL1, { memoria: memoriaDosDetalhes([obsOk()]), ...c });
    assert.ok(RAZOES_DE_REVISITA.includes(d.RAZAO), `razao fora do vocabulario: ${d.RAZAO}`);
  }
  assert.equal(RAZOES_DE_REVISITA.length, 5);
  assert.equal(DECISOES.length, 3);
});

console.log("\n4 · O VALIDADOR QUE NAO EXISTE NAO SE INVENTA (F5)");

T("sem ETag guardado, CONDITIONAL_REQUEST_AVAILABLE NUNCA dispara", () => {
  const d = decidirSobreDetalhe(URL1, { memoria: memoriaDosDetalhes([obsOk()]) });
  assert.equal(d.DECISAO, "SKIP_KNOWN");
  assert.ok(!d.RAZOES || !d.RAZOES.includes("CONDITIONAL_REQUEST_AVAILABLE"),
    "prometeu pedido condicional sem ter validador nenhum");
});

T("com ETag guardado, dispara — e diz que o condicional e mesmo possivel", () => {
  const mem = memoriaDosDetalhes([obsOk({ HTTP_ETAG: "W/\"abc123\"" })]);
  const d = decidirSobreDetalhe(URL1, { memoria: mem });
  assert.equal(d.DECISAO, "REVALIDATE");
  assert.equal(d.RAZAO, "CONDITIONAL_REQUEST_AVAILABLE");
  assert.equal(d.CONDICIONAL_POSSIVEL, true);
});

T("REVALIDATE sem validador confessa que o pedido NAO pode ser condicional", () => {
  // Importa porque um REVALIDATE sem validador custa a pagina inteira. Dizer
  // `true` aqui prometeria uma poupanca que nao acontece.
  const d = decidirSobreDetalhe(URL1, {
    memoria: memoriaDosDetalhes([obsOk()]),
    contrato: { RECOLLECTION: { DETAIL_CONTENT: "MUTABLE" } } });
  assert.equal(d.CONDICIONAL_POSSIVEL, false);
});

console.log("\n5 · O CONTRATO NAO E PROSA");

T("RECOLLECTION ausente = UNKNOWN, e UNKNOWN nao autoriza rede", () => {
  const r = recolheitaDoContrato("X", { UPDATE_BEHAVIOR: "SOBRESCRITA — janela movel de 11 dias" });
  assert.equal(r.DETAIL_CONTENT, "UNKNOWN");
  assert.equal(r.DECLARADO, false);
  // ⚠️ A prosa esta LA, e continua a nao mandar. 172 dos 186 contratos dizem
  // «NAO SEI» em UPDATE_BEHAVIOR; os outros dizem frases. Ler a frase seria o
  // motor a adivinhar.
  const d = decidirSobreDetalhe(URL1, {
    memoria: memoriaDosDetalhes([obsOk()]),
    contrato: { UPDATE_BEHAVIOR: "SOBRESCRITA — a anterior desaparece" } });
  assert.equal(d.DECISAO, "SKIP_KNOWN", "o motor leu prosa e decidiu com ela");
});

T("valor fora do vocabulario REPROVA — nao se aceita campo sem o implementar", () => {
  assert.throws(() => recolheitaDoContrato("X", { RECOLLECTION: { DETAIL_CONTENT: "TALVEZ" } }),
    RegraInvalida);
  assert.throws(() => recolheitaDoContrato("X",
    { RECOLLECTION: { DETAIL_CONTENT: "MUTABLE", TTL_SECONDS: "uma hora" } }), RegraInvalida);
  assert.throws(() => recolheitaDoContrato("X",
    { RECOLLECTION: { DETAIL_CONTENT: "MUTABLE", TTL_SECONDS: -5 } }), RegraInvalida);
  assert.equal(MUTABILIDADE.length, 3);
});

console.log("\n6 · O INDICE NAO E UM DETALHE");

T("o indice revisita-se sempre", () => {
  assert.equal(decidirSobreIndice().DECISAO, "FETCH");
});

console.log("\n7 · A MEMORIA LE O LIVRO, E A ORDEM DELE E A CRONOLOGIA");

T("a ULTIMA observacao sobre o endereco e a que manda", () => {
  // falha depois de sucesso -> volta-se
  const caiu = memoriaDosDetalhes([
    obsOk({ CAPTURED_AT: "2026-09-21T10:00:00Z" }),
    obsOk({ OBSERVATION_RESULT: "TRANSPORT_OR_EMPTY", CAPTURED_AT: "2026-09-21T11:00:00Z" }),
  ]);
  assert.equal(decidirSobreDetalhe(URL1, { memoria: caiu }).DECISAO, "FETCH");
  // sucesso depois de falha -> ja se tem
  const curou = memoriaDosDetalhes([
    obsOk({ OBSERVATION_RESULT: "TRANSPORT_OR_EMPTY", CAPTURED_AT: "2026-09-21T10:00:00Z" }),
    obsOk({ CAPTURED_AT: "2026-09-21T11:00:00Z" }),
  ]);
  assert.equal(decidirSobreDetalhe(URL1, { memoria: curou }).DECISAO, "SKIP_KNOWN");
});

T("linhas fora de ordem no livro nao trocam a resposta", () => {
  const fora = memoriaDosDetalhes([
    obsOk({ OBSERVATION_RESULT: "TRANSPORT_OR_EMPTY", CAPTURED_AT: "2026-09-21T11:00:00Z" }),
    obsOk({ CAPTURED_AT: "2026-09-21T10:00:00Z" }),
  ]);
  assert.equal(decidirSobreDetalhe(URL1, { memoria: fora }).DECISAO, "FETCH",
    "uma linha mais velha sobrepos-se a mais nova");
});

T("observacao sem SOURCE_URL nao entra na memoria — nem rebenta", () => {
  const m = memoriaDosDetalhes([{ SOURCE_ID: "X", OBSERVATION_RESULT: "DISCOVERY_FAILED" }, obsOk()]);
  assert.equal(m.size, 1);
});

console.log("\n8 · O CENSO CONTA O QUE ACONTECEU, E NAO O QUE SE QUERIA");

T("UNNECESSARY_REFETCHES conta revisita sem razao nomeada", () => {
  const c = censoDasDecisoes([
    { DECISAO: "FETCH", CONHECIDO: false },
    { DECISAO: "SKIP_KNOWN", CONHECIDO: true },
    { DECISAO: "REVALIDATE", CONHECIDO: true, RAZAO: "TTL_EXPIRED" },
    { DECISAO: "REVALIDATE", CONHECIDO: true, RAZAO: null },   // ← o pecado
    { DECISAO: "FETCH", CONHECIDO: true, RAZAO: null },        // ← e este
  ], { indiceRequests: 2 });
  assert.equal(c.DETAIL_NEW, 1);
  assert.equal(c.DETAIL_SKIPPED_KNOWN, 1);
  assert.equal(c.DETAIL_REVALIDATED, 2);
  assert.equal(c.DETAIL_REFETCHED, 1);
  assert.equal(c.UNNECESSARY_REFETCHES, 2);
  assert.equal(c.INDEX_REQUESTS, 2);
  // SKIP nao bate a porta; tudo o resto bate.
  assert.equal(c.DETAIL_REQUESTS, 4);
});

T("com esta regra, UNNECESSARY_REFETCHES e estruturalmente ZERO", () => {
  // Nao e optimismo: a funcao so devolve FETCH/REVALIDATE com razao, ou
  // SKIP. Nao ha ramo que produza revisita sem nome.
  const mem = memoriaDosDetalhes([obsOk()]);
  const ds = [
    decidirSobreDetalhe(URL1, { memoria: mem }),
    decidirSobreDetalhe(URL1, { memoria: mem, contrato: { RECOLLECTION: { DETAIL_CONTENT: "MUTABLE" } } }),
    decidirSobreDetalhe("https://novo.it/x", { memoria: mem }),
    decidirSobreDetalhe(URL1, { memoria: memoriaDosDetalhes([obsOk({ OBSERVATION_RESULT: "IDENTITY_FAILED" })]) }),
  ];
  assert.equal(censoDasDecisoes(ds).UNNECESSARY_REFETCHES, 0);
});

console.log(`\n  PASSOU ${ok} · FALHOU ${mau}\n`);
if (mau) process.exit(1);
