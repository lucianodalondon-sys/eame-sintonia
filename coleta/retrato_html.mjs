// O RETRATO DE UM HTML — o que se mede nos bytes SEM interpretar o que dizem.
//
//     CAPA != MATERIA.   MARKUP != TEXTO.
//
// Nasceu na AQUISICAO-DETALHE-V1 (2026-09-21), de duas medicoes no canario:
//
//   · 9 das 104 fontes de indice tinham a PROPRIA LISTAGEM guardada como se
//     fosse o documento (ex.: /News/Comunicati-stampa, /news/ufficio-stampa/).
//     O contrato dizia «itens de detalhe» e o que chegou foi a capa. Nada no
//     coletor distinguia uma coisa da outra.
//   · 2 de 3 DOCUMENT_CHANGED_IN_PLACE no canario eram o MESMO texto visivel
//     com bytes diferentes (widgets, nonces, contadores): uma versao nova no
//     armazem por ruido de markup. O incremental via «mudanca real» onde nao
//     havia nenhuma.
//
// Este ficheiro responde as duas perguntas com a mesma leitura que
// `coleta/executor_texto_de_html.py::_kind` faz do lado Python — os mesmos
// limiares, para que o Node e o Python nao discordem sobre o que e navegacao.
// Nao e um parser de artigos, nao adivinha «conteudo principal», nao le prosa
// de contrato. Le bytes e devolve numeros e uma leitura dita como leitura.
//
//     TEXT_SHA256   impressao do texto visivel normalizado — identidade de
//                   CONTEUDO, nao de bytes (COL-LAW-029: o hash mira a parte
//                   relevante, nao necessariamente a pagina inteira)
//     HTML_KIND     EMPTY · CONTENT · NAVIGATION · MIXED (limiares do executor)
//     CAPA_OU_MATERIA  MATERIA_PROVAVEL · CAPA_PROVAVEL · NAO_SEI — leitura
import { createHash } from "node:crypto";

const INVISIVEL = /<(script|style|noscript|template)\b[^>]*>[\s\S]*?<\/\1\s*>|<!--[\s\S]*?-->/gi;
const PARAGRAFO = /<p\b[^>]*>([\s\S]*?)<\/p\s*>/gi;
const LIGACAO = /<a\b[^>]*\bhref\s*=/gi;
const TAG = /<[^>]+>/g;
const ENTIDADES = { amp: "&", lt: "<", gt: ">", quot: "\"", apos: "'", nbsp: " " };

function desentidar(s) {
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
    if (e[0] === "#") {
      const n = e[1] === "x" || e[1] === "X" ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      return Number.isFinite(n) ? String.fromCodePoint(n) : m;
    }
    return ENTIDADES[e.toLowerCase()] ?? m;
  });
}

function decodificar(buf) {
  let b = buf;
  if (b.length >= 3 && b[0] === 0xEF && b[1] === 0xBB && b[2] === 0xBF) b = b.subarray(3);
  // UTF-8 primeiro; se houver bytes invalidos o Node substitui por U+FFFD, e
  // isso conta como caractere — o retrato ve o que ha, nao uma pagina vazia.
  return b.toString("utf8");
}

// O texto visivel normalizado — o mesmo sobre o qual nasce TEXT_SHA256. Exportado para a
// identidade de «a pagina e o boletim» (D42 (2)): o motor le-o como PAGE_TEXT e a impressao dele
// como CONTENT_SHA256 — identidade de CONTEUDO, nao de bytes.
export function textoVisivel(buf) {
  const fonte = decodificar(buf).replace(INVISIVEL, " ");
  return desentidar(fonte.replace(TAG, "\n")).split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean).join("\n");
}

export function impressaoDoTexto(texto) {
  return createHash("sha256").update(texto.replace(/\s+/g, " "), "utf8").digest("hex");
}

export function retratoDoHtml(buf) {
  const fonte = decodificar(buf).replace(INVISIVEL, " ");
  const ligacoes = (fonte.match(LIGACAO) || []).length;
  let paragrafo = 0;
  for (const m of fonte.matchAll(PARAGRAFO)) {
    paragrafo += desentidar(m[1].replace(TAG, " ")).replace(/\s+/g, "").length;
  }
  const texto = textoVisivel(buf);
  const semBrancos = texto.replace(/\s+/g, "").length;
  const kind = semBrancos === 0 ? "EMPTY"
    : (paragrafo >= 800 && paragrafo >= 0.35 * semBrancos) ? "CONTENT"
    : (ligacoes && semBrancos / Math.max(ligacoes, 1) < 40) ? "NAVIGATION"
    : "MIXED";
  return {
    TEXT_SHA256: impressaoDoTexto(texto),
    NON_WHITESPACE_CHARACTERS: semBrancos,
    PARAGRAPH_CHARACTERS: paragrafo,
    LINKS: ligacoes,
    HTML_KIND: kind,
    CAPA_OU_MATERIA: kind === "CONTENT" ? "MATERIA_PROVAVEL" : kind === "NAVIGATION" ? "CAPA_PROVAVEL" : "NAO_SEI",
  };
}

function semBarra(u) {
  // A mesma normalizacao de ready_split._sem_barra e de retrato_html.py.
  return String(u || "").trim().replace(/\/+$/, "").toLowerCase();
}

// ── V1: O INDEX_URL DO CONTRATO E CAPA (LD3 -> K1 -> V1A, 2026-09-23) ──────
// O gemeo de `curadoria/retrato_html.py::veredito`. A morada so manda quando e
// EXACTAMENTE o INDEX_URL do contrato — e so quando a REGUA MANDA (a fonte passa
// os 4 passos, ready_split.regua_de == DETAIL/v1). So HTML_LINK_DISCOVERY: numa
// rota fixa o INDEX_URL e o documento. Mudar um lado sem o outro e criar um
// segundo juiz: tests/test_v1a_v1_ligada.py compara os dois pagina a pagina.
//
// Enxertado de origin/aquisicao-detalhe-v1 (f98f234c) na V1A. Os chamadores
// Node (coleta/italy_pilot_collect.mjs e curadoria/canario_do_motor.mjs) vivem
// nessa linha e NAO nesta arvore: ao juntar, passam a dar { url, reguaAMandar }
// — sem isso o gate levanta, nao julga calado.
export const V1_LIGADA = true;
export const REGRA_V1 = "V1_INDEX_URL_E_CAPA";

export function eOIndiceDoContrato(url, contrato) {
  const aq = (contrato && contrato.ACQUISITION) || {};
  if (aq.STRATEGY !== "HTML_LINK_DISCOVERY") return false;
  const indice = semBarra(aq.INDEX_URL);
  return Boolean(indice) && semBarra(url) === indice;
}

function opcoesObrigatorias(opcoes) {
  if (!opcoes || !("url" in opcoes) || typeof opcoes.reguaAMandar !== "boolean") {
    throw new TypeError("V1A: o gate pede { url, reguaAMandar } — o endereco da pagina e se a regua dos 4 passos manda na fonte");
  }
}

export function veredito(retrato, contrato, opcoes) {
  opcoesObrigatorias(opcoes);
  const k = retrato ? retrato.CAPA_OU_MATERIA : undefined;
  if (V1_LIGADA && opcoes.reguaAMandar === true && opcoes.url && eOIndiceDoContrato(opcoes.url, contrato)) {
    return "CAPA_PROVAVEL";
  }
  return k;
}

// O GATE: um contrato que declara ITENS DE DETALHE (HTML_LINK_DISCOVERY com
// saida HTML) nao pode guardar uma capa como conteudo final. Devolve null
// quando nao ha nada a dizer, ou a razao da reprovacao.
// V1A: recebe { url, reguaAMandar } — obrigatorio.
export function gateCapaNaoEMateria(contrato, retrato, opcoes) {
  opcoesObrigatorias(opcoes);
  const aq = contrato && contrato.ACQUISITION;
  if (!aq || aq.STRATEGY !== "HTML_LINK_DISCOVERY") return null;
  if (String(contrato.OUTPUT_TYPE || "").toUpperCase() !== "HTML") return null;
  if (!retrato) return null;
  if (veredito(retrato, contrato, opcoes) !== "CAPA_PROVAVEL") return null;
  if (retrato.CAPA_OU_MATERIA !== "CAPA_PROVAVEL") {
    return `CAPA_NAO_E_MATERIA (${REGRA_V1}): a pagina e o proprio INDEX_URL do contrato, e a fonte passa os 4 passos`;
  }
  return `CAPA_NAO_E_MATERIA: o contrato declara itens de detalhe e o alvo parece listagem/navegacao `
       + `(${retrato.LINKS} ligacoes para ${retrato.NON_WHITESPACE_CHARACTERS} caracteres, ${retrato.PARAGRAPH_CHARACTERS} em paragrafos)`;
}
