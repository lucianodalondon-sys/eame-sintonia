// AS PROVAS DA PARIDADE — as duas defesas, e os dois lados de cada uma.
//
//     node regras/paridade_test.mjs
//
// ⚠️ TODA A PROVA E OFFLINE. Nenhuma linha daqui bate a rede: os bytes sao os
// que as duas corridas do canario ja deixaram em disco, ou bytes escritos a
// mao neste ficheiro. Um teste que precise de internet nao e um teste — e uma
// visita.
//
// O QUE TEM DE SER PROVADO NOS DOIS SENTIDOS, e a razao de cada um:
//
//   volatil     -> NAO e change      | senao o livro mente todos os dias
//   material    -> CONTINUA a ser    | senao o normalizador cega a deteccao
//   conhecido   -> NAO faz fetch     | senao nao ha incrementalidade nenhuma
//   novo        -> faz fetch         | senao deixamos de ver o que ha de novo
//   revalidar   -> pode fetch, COM RAZAO NOMEADA
//
// Provar so um lado de cada par e o defeito classico: um normalizador que
// apague tudo passa metade das provas com 100%.

import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";

import {
  normalizarConteudo, compararConteudo, textoVisivel, pareceHtml, TRECHOS_VOLATEIS,
} from "./normalizacao_de_conteudo.mjs";
import {
  memoriaDosDetalhes, decidirSobreDetalhe, decidirSobreIndice, censoDasDecisoes,
} from "./incrementalidade.mjs";

let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};

// ── UMA PAGINA DE VERDADE, EM MINIATURA ───────────────────────────────────
// Traz os seis trechos volateis medidos e um paragrafo de materia. O
// paragrafo existe para que cada prova possa perguntar «e o texto?» — sem
// ele, um normalizador que apagasse o ficheiro inteiro passaria.
const pagina = (v = {}) => Buffer.from(`<!DOCTYPE html><html><head>
<meta property="article:modified_time" content="${v.hora ?? "2026-09-22T02:01:41+00:00"}" />
</head><body>
<h1 class="single-post-title">${v.titulo ?? "Arachidi statunitensi, prezzi in forte rialzo"}</h1>
<div class="views">${v.visitas ?? 134}</div>
<p>${v.corpo ?? "I prezzi delle arachidi statunitensi sono in forte rialzo."}</p>
<aside class="td_block_template_1 widget zoote-widget"><div id="zoote-${v.anuncio ?? 111}"><a href="${v.anunciante ?? "https://sperotto-spa.com"}">x</a></div></aside>
<script id="zoote-tracking">var advads_tracking_ads = {"1":[${v.ordem ?? "15851,15321"}]};</script>
<form><input name="_session_key" type="hidden" value="${v.sessao ?? "cOYBx0pX0bhhWOy2meyATWQ7PjHUnWZkGH52MaIr"}"><input name="_token" type="hidden" value="${v.token ?? "uThxOO2rQoPyY4Fzqt0M0YLHyjLWyxDWUdV86FWg"}"></form>
<!-- Theme: Newspaper uid: ${v.uid ?? "6ab1e1ae8537b"} -->
</body></html><!-- Parsed with iubenda default class in ${v.crono ?? "0.00315"} sec. -->`, "latin1");

console.log("\n══ DEFESA 2 · O VOLATIL NAO E MUDANCA ══════════════════════════");

t("contador de visitas muda -> NAO e change", () => {
  const c = compararConteudo(pagina({ visitas: 134 }), pagina({ visitas: 135 }));
  assert.equal(c.RAW_CHANGED, true, "os bytes tinham mesmo de diferir");
  assert.equal(c.VEREDICTO, "VOLATILE_ONLY");
  assert.equal(c.NORMALIZED_CHANGED, false);
  assert.equal(c.VOLATILE_DIFFERENCE, true);
});

t("token do formulario muda -> NAO e change", () => {
  const c = compararConteudo(pagina({ token: "A".repeat(40) }), pagina({ token: "B".repeat(40) }));
  assert.equal(c.RAW_CHANGED, true);
  assert.equal(c.VEREDICTO, "VOLATILE_ONLY");
});

t("chave de sessao muda -> NAO e change", () => {
  const c = compararConteudo(pagina({ sessao: "C".repeat(40) }), pagina({ sessao: "D".repeat(40) }));
  assert.equal(c.VEREDICTO, "VOLATILE_ONLY");
});

t("article:modified_time (que e a nossa visita) muda -> NAO e change", () => {
  const c = compararConteudo(pagina({ hora: "2026-09-22T02:01:41+00:00" }), pagina({ hora: "2026-09-22T02:06:03+00:00" }));
  assert.equal(c.VEREDICTO, "VOLATILE_ONLY");
});

t("anuncio rotativo, uid do tema e cronometro mudam -> NAO e change", () => {
  const c = compararConteudo(
    pagina({ anuncio: 111, anunciante: "https://sperotto-spa.com", uid: "6ab1e1ae8537b", crono: "0.00315", ordem: "15851,15321" }),
    pagina({ anuncio: 999, anunciante: "https://www.codaf.net", uid: "6ab1e2b74bd00", crono: "0.00291", ordem: "15321,15851" }));
  assert.equal(c.VEREDICTO, "VOLATILE_ONLY");
});

t("os SEIS volateis ao mesmo tempo -> continua a NAO ser change", () => {
  const c = compararConteudo(pagina(), pagina({
    visitas: 999, hora: "2026-09-23T00:00:00+00:00", sessao: "Z".repeat(40),
    token: "Y".repeat(40), uid: "6ab1ffffffff0", crono: "9.99999",
    anuncio: 42, anunciante: "https://outro.it", ordem: "5840,680" }));
  assert.equal(c.VEREDICTO, "VOLATILE_ONLY");
  assert.equal(c.VISIBLE_TEXT_CHANGED, false, "o texto visivel nao podia ter mexido");
});

console.log("\n══ O OUTRO LADO · O MATERIAL CONTINUA A SER DETECTADO ══════════");

t("uma palavra do corpo muda -> E CHANGE", () => {
  const c = compararConteudo(
    pagina({ corpo: "I prezzi delle arachidi sono in forte rialzo." }),
    pagina({ corpo: "I prezzi delle arachidi sono in forte CALO." }));
  assert.equal(c.VEREDICTO, "MATERIAL_CHANGE");
  assert.equal(c.NORMALIZED_CHANGED, true);
  assert.equal(c.MATERIAL_DIFF ?? c.NORMALIZED_CHANGED, true);
  assert.equal(c.VOLATILE_DIFFERENCE, false);
  assert.notEqual(c.OLD_NORMALIZED_HASH, c.NEW_NORMALIZED_HASH);
});

t("o titulo muda -> E CHANGE", () => {
  const c = compararConteudo(pagina({ titulo: "Prezzi in rialzo" }), pagina({ titulo: "Prezzi in calo" }));
  assert.equal(c.VEREDICTO, "MATERIAL_CHANGE");
});

t("UM SO CARACTERE do corpo muda -> E CHANGE", () => {
  const c = compararConteudo(pagina({ corpo: "rialzo del 12%" }), pagina({ corpo: "rialzo del 13%" }));
  assert.equal(c.VEREDICTO, "MATERIAL_CHANGE");
});

t("materia muda E os volateis mudam -> E CHANGE (o ruido nao esconde o sinal)", () => {
  const c = compararConteudo(
    pagina({ corpo: "rialzo", visitas: 134, sessao: "A".repeat(40) }),
    pagina({ corpo: "CALO", visitas: 9999, sessao: "B".repeat(40) }));
  assert.equal(c.VEREDICTO, "MATERIAL_CHANGE");
});

t("bytes identicos -> IDENTICAL_BYTES, e nao MATERIAL", () => {
  const c = compararConteudo(pagina(), pagina());
  assert.equal(c.VEREDICTO, "IDENTICAL_BYTES");
  assert.equal(c.RAW_CHANGED, false);
});

console.log("\n══ O NORMALIZADOR NAO PODE APAGAR CONTEUDO ═════════════════════");

t("normalizar NAO encolhe o texto visivel", () => {
  const p = pagina();
  const antes = textoVisivel(p);
  const n = normalizarConteudo(p);
  assert.equal(n.NORMALIZACAO, "APPLIED");
  // As palavras da materia tem de sobreviver, uma a uma.
  for (const w of ["Arachidi", "statunitensi", "prezzi", "rialzo"]) {
    assert.ok(antes.includes(w), `a pagina de prova devia conter ${w}`);
  }
  assert.ok(n.VOLATEIS_TOTAL >= 6, `esperava os seis volateis, achei ${n.VOLATEIS_TOTAL}`);
});

t("o texto visivel e testemunha independente do veredicto", () => {
  const c = compararConteudo(pagina({ corpo: "alfa" }), pagina({ corpo: "beta" }));
  assert.equal(c.VISIBLE_TEXT_CHANGED, true);
  assert.equal(c.NORMALIZED_CHANGED, true);
  assert.equal(c.AVISO, null, "as duas reguas concordaram — nao devia haver aviso");
});

t("PDF/CSV nao sao normalizados, e diz-se porque", () => {
  const pdf = Buffer.from("%PDF-1.4\nconteudo\n");
  const n = normalizarConteudo(pdf);
  assert.equal(n.NORMALIZACAO, "NOT_APPLICABLE");
  assert.equal(n.NORMALIZED_SHA, n.RAW_SHA256, "sem normalizar, normalizado == raw");
  assert.equal(pareceHtml(pdf), false);
  // E sem saber separar ruido, TUDO e sinal — que e o certo.
  const c = compararConteudo(pdf, Buffer.from("%PDF-1.4\noutro\n"));
  assert.equal(c.VEREDICTO, "MATERIAL_CHANGE");
  assert.equal(c.NORMALIZACAO, "NOT_APPLICABLE");
});

t("cada trecho volatil tem NOME e ONDE FOI MEDIDO", () => {
  assert.ok(TRECHOS_VOLATEIS.length >= 6);
  for (const x of TRECHOS_VOLATEIS) {
    assert.ok(x.NOME && x.ONDE && x.PORQUE, `trecho sem proveniencia: ${x.NOME}`);
    assert.ok(x.REGRA instanceof RegExp, `${x.NOME} sem regra`);
  }
});

t("normalizar duas vezes da o mesmo (a regra nao guarda lastIndex)", () => {
  const p = pagina();
  assert.equal(normalizarConteudo(p).NORMALIZED_SHA, normalizarConteudo(p).NORMALIZED_SHA);
});

console.log("\n══ DEFESA 1 · A DECISAO DE IR, ANTES DE BATER A PORTA ══════════");

const U = "https://www.myfruit.it/news/arachidi";
const obs = (x = {}) => ({ SOURCE_URL: U, SOURCE_ID: "IT-T10-018", OBSERVATION_RESULT: "NEW_DOCUMENT", CAPTURED_AT: "2026-09-22T02:01:42Z", ...x });

t("documento NOVO -> FETCH (e nao se cega a deteccao)", () => {
  const d = decidirSobreDetalhe("https://www.myfruit.it/news/nunca-visto", { memoria: memoriaDosDetalhes([obs()]) });
  assert.equal(d.DECISAO, "FETCH");
  assert.equal(d.CONHECIDO, false);
});

t("conhecido e elegivel -> NAO FAZ FETCH", () => {
  const d = decidirSobreDetalhe(U, { memoria: memoriaDosDetalhes([obs()]), sourceId: "IT-T10-018", contrato: null });
  assert.equal(d.DECISAO, "SKIP_KNOWN");
  assert.equal(d.RAZAO, null);
});

t("conhecido mas a ultima visita falhou -> FETCH, com razao nomeada", () => {
  const d = decidirSobreDetalhe(U, { memoria: memoriaDosDetalhes([obs({ OBSERVATION_RESULT: "TRANSPORT_OR_EMPTY" })]) });
  assert.equal(d.DECISAO, "FETCH");
  assert.equal(d.RAZAO, "PREVIOUS_ATTEMPT_FAILED");
});

t("contrato declara MUTABLE -> REVALIDATE, e DIZ porque", () => {
  const d = decidirSobreDetalhe(U, { memoria: memoriaDosDetalhes([obs()]),
    contrato: { RECOLLECTION: { DETAIL_CONTENT: "MUTABLE" } } });
  assert.equal(d.DECISAO, "REVALIDATE");
  assert.equal(d.RAZAO, "CONTRACT_DECLARES_MUTABLE");
  assert.ok(d.PORQUE.includes("CONTRACT_DECLARES_MUTABLE"));
});

t("TTL expirado -> REVALIDATE; TTL fresco -> SKIP", () => {
  const mem = memoriaDosDetalhes([obs()]);
  const contrato = { RECOLLECTION: { DETAIL_CONTENT: "UNKNOWN", TTL_SECONDS: 3600 } };
  assert.equal(decidirSobreDetalhe(U, { memoria: mem, contrato, agora: "2026-09-22T09:00:00Z" }).DECISAO, "REVALIDATE");
  assert.equal(decidirSobreDetalhe(U, { memoria: mem, contrato, agora: "2026-09-22T02:10:00Z" }).DECISAO, "SKIP_KNOWN");
});

t("o INDICE revisita-se sempre — saltar o indice era deixar de saber do novo", () => {
  assert.equal(decidirSobreIndice().DECISAO, "FETCH");
});

t("SKIP nao gasta pedido; e o censo da UNNECESSARY_REFETCHES = 0", () => {
  const mem = memoriaDosDetalhes([obs()]);
  const censo = censoDasDecisoes([decidirSobreDetalhe(U, { memoria: mem })], { indiceRequests: 1 });
  assert.equal(censo.DETAIL_SKIPPED_KNOWN, 1);
  assert.equal(censo.DETAIL_REQUESTS, 0);
  assert.equal(censo.UNNECESSARY_REFETCHES, 0);
});

console.log("\n══ O COLETOR REAL CHAMA MESMO AS DUAS PECAS ════════════════════");
// ⚠️ ESTA E A PROVA QUE FALTAVA EM SETEMBRO DE 2026. A peca existia e estava
// certa; o que nao havia era ninguem a chama-la de dentro do coletor. Um
// teste que so exercite a regra ISOLADA volta a dar verde com a rota
// desligada — foi exactamente isso que aconteceu.
const fonte = readFileSync(new URL("../coleta/italy_pilot_collect.mjs", import.meta.url), "utf8");

t("italy_pilot_collect.mjs importa a regra de revisita", () => {
  assert.ok(/from\s+"\.\.\/regras\/incrementalidade\.mjs"/.test(fonte),
    "o coletor real nao importa regras/incrementalidade.mjs — MISSING_ROUTE outra vez");
  assert.ok(fonte.includes("decidirSobreDetalhe("), "importa e nao chama nao vale");
});

t("italy_pilot_collect.mjs importa a normalizacao de conteudo", () => {
  assert.ok(/from\s+"\.\.\/regras\/normalizacao_de_conteudo\.mjs"/.test(fonte));
  assert.ok(fonte.includes("compararConteudo("));
});

t("a DECISAO vem ANTES do download, e nao depois", () => {
  const iDecisao = fonte.indexOf("decidirSobreDetalhe(alvo.url");
  const iBaixar = fonte.indexOf("await baixar(alvo.url)");
  assert.ok(iDecisao > 0, "nao ha decisao sobre o alvo");
  assert.ok(iBaixar > 0, "nao ha download do alvo");
  assert.ok(iDecisao < iBaixar,
    "a decisao esta DEPOIS do download: isso e dedup pos-download, nao incrementalidade");
});

t("o SKIP nao escreve no livro (senao envenena a memoria da proxima corrida)", () => {
  // Entre o `SKIP_KNOWN` e o `continue` nao pode haver `gravar(`.
  const i = fonte.indexOf('decisao.DECISAO === "SKIP_KNOWN"');
  assert.ok(i > 0);
  const bloco = fonte.slice(i, fonte.indexOf("continue;", i));
  assert.ok(!bloco.includes("gravar("),
    "o salto esta a ir para o livro; `SKIPPED_KNOWN` nao esta em RESULTADOS_COM_DOCUMENTO "
    + "e a corrida seguinte voltaria a descarregar tudo");
});

console.log("\n══ REPLAY OFFLINE SOBRE OS BYTES DAS DUAS CORRIDAS ═════════════");
// Se a ops nao estiver nesta maquina, isto nao INVENTA um verde: diz que
// faltou a bancada. Prova que nao correu nao e prova que passou.
const OPS = process.env.PARIDADE_OPS_ROOT || "C:/eame-sintonia-ops";
const RUN1 = process.env.PARIDADE_RUN1 || "OPS_forward-only-live_20260922020109_0d088d";
const RUN2 = process.env.PARIDADE_RUN2 || "OPS_forward-only-live_20260922020511_8be761";

if (!existsSync(`${OPS}/data/collection-ledger/italy/observations.ndjson`)) {
  console.log(`  NAO_CORREU  bancada ausente em ${OPS} — isto NAO conta como passou`);
} else {
  const { replay } = await import("../medidas/paridade_replay.mjs");
  const r = replay(OPS, RUN1, RUN2);
  t("as 32 mudancas da RUN2 eram TODAS ruido volatil", () => {
    assert.equal(r.FASE2.PARES_COMPARADOS, 32);
    assert.equal(r.FASE2.RAW_CHANGED, 32, "os bytes mudaram nos 32 — isso e facto");
    assert.equal(r.FASE2.NORMALIZED_CHANGED, 0, "nenhum conteudo mudou");
    assert.equal(r.FASE2.VOLATILE_DIFFERENCE, 32);
  });
  t("nenhum documento foi classificado por bytes em falta", () => {
    assert.equal(r.FASE2.BYTES_AUSENTES, 0);
  });
  t("o normalizador nao contradisse o texto visivel em nenhum documento", () => {
    assert.equal(r.FASE2.NORMALIZADOR_SUSPEITO, 0);
  });
  t("com a regra ligada, a RUN2 nao teria batido a porta a nenhum detalhe", () => {
    assert.equal(r.FASE6.CENSO_SE_A_REGRA_HOUVESSE_CORRIDO.DETAIL_REQUESTS, 0);
    assert.equal(r.FASE6.PEDIDOS_EVITAVEIS, 39);
    assert.equal(r.FASE6.UNNECESSARY_REFETCHES, 0);
  });
}

console.log(`\n  ${passou} passaram, ${falhou} falharam`);
if (falhou) process.exit(1);
