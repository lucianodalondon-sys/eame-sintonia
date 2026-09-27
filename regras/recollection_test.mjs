// AS GUARDAS DA RECOLLECTION-V1
//
//     RECOLLECTION_UNKNOWN  ≠  NEVER_RECOLLECT
//
// Cada teste aqui existe para matar um ataque nomeado do red team desta
// missao (`provas/recollection_red_team.mjs`). Um teste que nao mate nenhum
// mutante e decoracao; o numero do ataque vai escrito ao lado.
//
// Correr:  node regras/recollection_test.mjs

import {
  decidirSobreDetalhe, memoriaDosDetalhes, censoDasDecisoes,
  recolheitaDoContrato, admissivelNaBigCollection, decidirSobreIndice,
  MUTABILIDADE, COBERTURA_DE_REVISITA, RAZOES_DE_REVISITA, RegraInvalida,
} from "./incrementalidade.mjs";
import {
  compararConteudo, canonicalizarEntidades, normalizarConteudo,
  textoNormalizado, TRECHOS_VOLATEIS,
} from "./normalizacao_de_conteudo.mjs";
import { CONTRACTS, CONTRACT_IDS } from "./italy_contracts.mjs";

let ok = 0, mau = 0;
const secao = (s) => console.log(`\n${s}`);
function t(nome, fn) {
  try { fn(); console.log("  PASS ", nome); ok++; }
  catch (e) { console.log("  FAIL ", nome, "\n         ", e.message); mau++; }
}
function igual(a, b, msg) {
  const A = JSON.stringify(a), B = JSON.stringify(b);
  if (A !== B) throw new Error(`${msg || ""} esperava ${B}, veio ${A}`);
}
function verdade(c, msg) { if (!c) throw new Error(msg || "esperava verdadeiro"); }

const URL_D = "https://exemplo.it/detalhe/1";
const CONHECIDO = memoriaDosDetalhes([{
  SOURCE_URL: URL_D, SOURCE_ID: "IT-TEST-001",
  OBSERVATION_RESULT: "NEW_DOCUMENT", CAPTURED_AT: "2026-01-01T00:00:00Z",
}]);
const AGORA = "2026-06-01T00:00:00Z";
const cont = (v) => (v === null ? null : { RECOLLECTION: { DETAIL_CONTENT: v, TTL_SECONDS: null } });
const decidir = (c) => decidirSobreDetalhe(URL_D, { memoria: CONHECIDO, sourceId: "IT-TEST-001", contrato: c, agora: AGORA });

secao("1 · UNKNOWN DEIXOU DE SER INDISTINGUIVEL DE IMMUTABLE   [M1, M6]");

t("contrato ausente e contrato IMMUTABLE nao dao a MESMA resposta", () => {
  const a = decidir(null), b = decidir(cont("IMMUTABLE"));
  igual(a.DECISAO, b.DECISAO, "a decisao de rede continua igual (e tem de continuar):");
  if (a.COBERTURA === b.COBERTURA)
    throw new Error(`ambos saem com COBERTURA=${a.COBERTURA} — o defeito de origem voltou`);
});

t("contrato ausente sai BLOCKED_FOR_BIG_COLLECTION", () => {
  igual(decidir(null).COBERTURA, "BLOCKED_FOR_BIG_COLLECTION");
});

t("UNKNOWN escrito a mao nao compra a admissao", () => {
  // Carimbar `UNKNOWN` e dizer «ainda nao sei». Nao pode valer o mesmo que medir.
  igual(decidir(cont("UNKNOWN")).COBERTURA, "BLOCKED_FOR_BIG_COLLECTION");
  igual(recolheitaDoContrato("X", cont("UNKNOWN")).DECLARADO, false);
});

t("IMMUTABLE declarado sai DECLARADA", () => {
  igual(decidir(cont("IMMUTABLE")).COBERTURA, "DECLARADA");
});

t("o salto por ignorancia traz AVISO e o salto declarado nao", () => {
  verdade(decidir(null).AVISO, "o salto cego tem de dizer o nome");
  verdade(decidir(cont("IMMUTABLE")).AVISO === null, "o salto informado nao inventa alarme");
});

secao("2 · A REDE NAO MUDOU — A INCREMENTALIDADE FICA DE PE   [M8, M10]");

t("nenhum valor de RECOLLECTION faz FETCH a um detalhe ja conhecido", () => {
  for (const v of [null, cont("UNKNOWN"), cont("IMMUTABLE")])
    igual(decidir(v).DECISAO, "SKIP_KNOWN", `contrato ${JSON.stringify(v)}:`);
});

t("UNNECESSARY_REFETCHES continua ZERO com as quatro coberturas", () => {
  const ds = [null, cont("UNKNOWN"), cont("IMMUTABLE"), cont("MUTABLE")].map(decidir);
  const c = censoDasDecisoes(ds);
  igual(c.UNNECESSARY_REFETCHES, 0);
  igual(c.DETAIL_REQUESTS, 1, "so o MUTABLE bate a porta:");
});

t("o censo separa o salto informado do salto cego", () => {
  const c = censoDasDecisoes([null, cont("UNKNOWN"), cont("IMMUTABLE")].map(decidir));
  igual(c.DETAIL_SKIPPED_KNOWN, 3);
  igual(c.DETAIL_SKIPPED_UNDECLARED, 2, "ausente e UNKNOWN sao os dois cegos:");
});

t("uma decisao antiga sem o campo nao e contada como cega", () => {
  // Inventar cegueira a partir de campos em falta seria alarme, nao medida.
  igual(censoDasDecisoes([{ DECISAO: "SKIP_KNOWN", CONHECIDO: true }]).DETAIL_SKIPPED_UNDECLARED, 0);
});

t("o indice continua a revisitar-se sempre", () => {
  igual(decidirSobreIndice().DECISAO, "FETCH");
});

secao("3 · A PORTA DA BIG COLLECTION   [M6]");

t("admissivelNaBigCollection bloqueia quem nao declarou", () => {
  igual(admissivelNaBigCollection("X", null).ADMISSIVEL, false);
  igual(admissivelNaBigCollection("X", cont("UNKNOWN")).ADMISSIVEL, false);
});

t("admissivelNaBigCollection deixa passar quem declarou", () => {
  igual(admissivelNaBigCollection("X", cont("IMMUTABLE")).ADMISSIVEL, true);
  igual(admissivelNaBigCollection("X", cont("MUTABLE")).ADMISSIVEL, true);
});

t("um bloqueio e um facto contavel, nunca uma excepcao", () => {
  const r = admissivelNaBigCollection("X", null);
  verdade(COBERTURA_DE_REVISITA.includes(r.COBERTURA), "COBERTURA fora do vocabulario");
  verdade(typeof r.PORQUE === "string" && r.PORQUE.length > 10, "sem PORQUE nao se explica ao dono");
});

t("valor fora do vocabulario continua a REPROVAR", () => {
  let caiu = false;
  try { recolheitaDoContrato("X", { RECOLLECTION: { DETAIL_CONTENT: "TALVEZ" } }); }
  catch (e) { caiu = e instanceof RegraInvalida; }
  verdade(caiu, "aceitar um valor que nao se implementa e pior que recusa-lo");
});

t("o vocabulario nao cresceu as escondidas", () => {
  igual([...MUTABILIDADE], ["IMMUTABLE", "MUTABLE", "UNKNOWN"]);
  igual([...RAZOES_DE_REVISITA].length, 5, "as razoes continuam cinco:");
});

secao("4 · MUTAVEL NAO PASSA A IMUTAVEL POR RUIDO   [M2, M4]");

const HTML = (miolo, nonce) => Buffer.from(
  `<html><head><meta property="article:modified_time" content="2026-01-01T00:00:00+00:00">` +
  `</head><body><p>${miolo}</p>` +
  `<script>var wpdm_js = {"spinner":"x","client_id":"${nonce}"};</script>` +
  `<a href="//s.it/?wordfence_lh=1&hid=${nonce.toUpperCase()}">x</a>` +
  `<div class="view view-x view-dom-id-${nonce}">v</div>` +
  `<input name="form_build_id" value="form-${nonce}"></body></html>`, "latin1");

t("so o nonce a mudar => VOLATILE_ONLY", () => {
  const c = compararConteudo(HTML("o mesmo texto", "a".repeat(32)), HTML("o mesmo texto", "b".repeat(32)));
  igual(c.VEREDICTO, "VOLATILE_ONLY");
});

t("o TEXTO a mudar => MATERIAL_CHANGE, mesmo com o nonce igual", () => {
  const c = compararConteudo(HTML("texto velho", "a".repeat(32)), HTML("TEXTO NOVO", "a".repeat(32)));
  igual(c.VEREDICTO, "MATERIAL_CHANGE");
});

t("o TEXTO a mudar E o nonce a mudar continua MATERIAL_CHANGE", () => {
  // O ataque que interessa: esconder uma edicao real por tras de ruido.
  const c = compararConteudo(HTML("texto velho", "a".repeat(32)), HTML("TEXTO NOVO", "b".repeat(32)));
  igual(c.VEREDICTO, "MATERIAL_CHANGE");
});

t("cada regra nova apanha mesmo o seu trecho", () => {
  const n = textoNormalizado(HTML("x", "c".repeat(32)));
  for (const nome of ["WPDM_CLIENT_ID", "WORDFENCE_HID", "DRUPAL_VIEW_DOM_ID", "DRUPAL_FORM_BUILD_ID"])
    verdade(n.VOLATEIS[nome] >= 1, `${nome} nao apanhou nada — a regra nao morde`);
});

t("cada trecho da lista declara onde foi medido", () => {
  for (const x of TRECHOS_VOLATEIS) {
    verdade(x.NOME && x.REGRA && x.ONDE, `trecho sem NOME/REGRA/ONDE: ${x.NOME}`);
    verdade(String(x.ONDE).length > 15, `${x.NOME}: ONDE vago nao impede a lista de crescer por palpite`);
  }
});

secao("5 · A CANONICALIZACAO NAO PODE APAGAR CONTEUDO   [M4]");

t("a mesma frase em entidades diferentes fica igual", () => {
  const a = canonicalizarEntidades("i&#110;f&#111;&#64;x.it").TEXTO;
  const b = canonicalizarEntidades("&#105;nfo@x&#46;it").TEXTO;
  igual(a, "info@x.it"); igual(b, "info@x.it");
});

t("frases DIFERENTES continuam diferentes depois de traduzidas", () => {
  const a = canonicalizarEntidades("&#105;nfo@a.it").TEXTO;
  const b = canonicalizarEntidades("&#105;nfo@b.it").TEXTO;
  verdade(a !== b, "traduzir entidades nao pode colar enderecos distintos");
});

t("os cinco caracteres com significado em HTML NAO se traduzem", () => {
  const r = canonicalizarEntidades("&#38;&#60;&#62;&#34;&#39;").TEXTO;
  igual(r, "&#38;&#60;&#62;&#34;&#39;");
});

t("duplo escape nao se descodifica duas vezes", () => {
  // `&#38;#105;` e um `&#105;` literal escrito por quem escapou o `&`.
  // Traduzi-lo daria `i`, e apagava a diferenca entre o texto e a sua citacao.
  igual(canonicalizarEntidades("&#38;#105;").TEXTO, "&#38;#105;");
});

t("nao se traduz o que nao e caractere visivel", () => {
  igual(canonicalizarEntidades("&#0;&#10;").TEXTO, "&#0;&#10;");
});

t("o recibo conta as traducoes a parte dos volateis", () => {
  const n = normalizarConteudo(Buffer.from("<html><body>&#105;nfo</body></html>", "latin1"));
  igual(n.ENTIDADES_TRADUZIDAS, 1);
  igual(n.VOLATEIS_TOTAL, 0, "traduzir nao e apagar:");
});

t("um PDF continua a sair intacto", () => {
  const n = normalizarConteudo(Buffer.from("%PDF-1.4 &#105;nfo", "latin1"));
  igual(n.NORMALIZACAO, "NOT_APPLICABLE");
  igual(n.NORMALIZED_SHA, n.RAW_SHA256);
  igual(n.ENTIDADES_TRADUZIDAS, 0, "nao se mexe em bytes que nao se sabe ler:");
});

secao("6 · OS CONTRATOS DECLARADOS SAO COERENTES COM O QUE SE MEDIU");

t("todo o RECOLLECTION escrito esta no vocabulario", () => {
  for (const id of CONTRACT_IDS) {
    const r = CONTRACTS[id] && CONTRACTS[id].RECOLLECTION;
    if (!r) continue;
    verdade(MUTABILIDADE.includes(r.DETAIL_CONTENT), `${id}: ${r.DETAIL_CONTENT} fora do vocabulario`);
    recolheitaDoContrato(id, CONTRACTS[id]);   // reprova sozinho se o TTL for invalido
  }
});

t("nenhum contrato declara UNKNOWN a fingir que classificou", () => {
  const fingidos = CONTRACT_IDS.filter((id) => CONTRACTS[id].RECOLLECTION
    && CONTRACTS[id].RECOLLECTION.DETAIL_CONTENT === "UNKNOWN");
  igual(fingidos, [], "declarar UNKNOWN e nao declarar — o bloco so serve para medir:");
});

t("quem entrega FICHEIRO e diz ADITIVO nao foi declarado MUTABLE", () => {
  const FICHEIRO = ["PDF", "CSV", "ODS", "XLSX", "ZIP"];
  for (const id of CONTRACT_IDS) {
    const c = CONTRACTS[id];
    if (!c.RECOLLECTION || c.RECOLLECTION.DETAIL_CONTENT !== "MUTABLE") continue;
    if (/^ADITIVO/i.test(String(c.UPDATE_BEHAVIOR || "")) && FICHEIRO.includes(String(c.OUTPUT_TYPE).toUpperCase()))
      throw new Error(`${id}: ficheiro aditivo declarado MUTABLE — revisitaria para sempre sem necessidade`);
  }
});

t("quem entrega PAGINA nao foi declarado IMMUTABLE so por dizer ADITIVO", () => {
  // O erro que esta missao quase cometeu, e que cegaria o catalogo da ADAMA.
  const PAGINA = ["HTML", "BROWSER_RENDERED_EXTRACT"];
  for (const id of CONTRACT_IDS) {
    const c = CONTRACTS[id];
    if (!c.RECOLLECTION || c.RECOLLECTION.DETAIL_CONTENT !== "IMMUTABLE") continue;
    if (PAGINA.includes(String(c.OUTPUT_TYPE).toUpperCase()))
      throw new Error(`${id}: pagina declarada IMMUTABLE — uma reescrita silenciosa nunca seria vista`);
  }
});

console.log(`\n  PASSOU ${ok} · FALHOU ${mau}\n`);
if (mau > 0) process.exitCode = 1;
