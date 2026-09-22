// A TOPOLOGIA DE PUBLICACAO, POR EVIDENCIA — E OS CRITERIOS ESCRITOS ANTES
//
// ⚠️ OS CRITERIOS ESTAO AQUI EM CIMA DE PROPOSITO. Definir `HIGH/MEDIUM/LOW`
// depois de olhar para as fontes e escolher a regua que da o resultado que ja
// se queria — opiniao com ar de medicao. Estes nasceram antes da primeira
// linha da tabela, e nenhuma fonte os mudou.
//
// A ORDEM DA EVIDENCIA, DA MAIS FORTE PARA A MAIS FRACA ───────────────────
//
//   1 CONTRATO_MEDIDO      o contrato a mao declara UPDATE_BEHAVIOR e cita a
//                          medicao que o sustenta (N edicoes, espacamento)
//   2 DATAS_NO_DOCUMENTO   published/modified DENTRO dos bytes preservados,
//                          proprias de cada artigo
//   3 REVISITA_PRESERVADA  duas visitas guardadas ao mesmo endereco
//   4 FORMA_DO_ENDERECO    a morada carrega data ou numero de edicao
//   5 SEM_EVIDENCIA        nada disto
//
// ⚠️ PORQUE A REVISITA E SO A TERCEIRA, E NAO A PRIMEIRA.
// Medido nesta missao: os 83 pares de visitas guardadas estao TODOS a 8,7
// minutos de distancia uns dos outros. «83 de 83 nao mudaram» prova que o
// normalizador funciona; sobre o que a fonte faz numa semana nao prova nada.
// Tres fontes que essa regua daria como imutaveis carregam, dentro dos
// proprios bytes, a prova de que reescrevem artigos ate 72 dias depois de os
// publicarem. A evidencia mais VISIVEL era a mais fraca.
//
// CONFIANCA, deterministica ────────────────────────────────────────────────
//   HIGH    evidencia 1 ou 2, com >= 5 documentos medidos e veredicto coerente
//   MEDIUM  evidencia 2 com 2 a 4 documentos, ou 1 com uma so edicao,
//           ou 4 com data no caminho
//   LOW     so evidencia 3 ou 4
//   nenhuma -> nao se declara nada. `UNKNOWN`, e BLOCKED_FOR_BIG_COLLECTION.
//
// So se propoe `RECOLLECTION` com confianca HIGH ou MEDIUM. LOW nao declara:
// uma declaracao fraca vale menos que nenhuma, porque compra a admissao a Big
// Collection ao preco de um palpite.
//
// AS TOPOLOGIAS — sao categorias de ANALISE e nao entram no contrato.
// O contrato so aceita IMMUTABLE / MUTABLE / UNKNOWN.

import { readFileSync, existsSync } from "node:fs";
import { lerObservacoes } from "./recollection_censo.mjs";
import { CONTRACTS, CONTRACT_IDS } from "../regras/italy_contracts.mjs";
import { admissivelNaBigCollection } from "../regras/incrementalidade.mjs";

export const TOPOLOGIAS = Object.freeze({
  A: "IMMUTABLE_DETAIL_URLS",
  B: "MUTABLE_STABLE_URL",
  C: "LISTING_MUTABLE_DETAIL_IMMUTABLE",
  D: "FEED_OR_API_INCREMENTAL",
  E: "MIXED",
  F: "UNKNOWN",
});

const DIA = 86400000;

/** As datas que cada documento traz sobre si proprio. */
export function datasDoDocumento(html) {
  const p = (html.match(/property="article:published_time"[^>]*content="([^"]*)"/i)
    || html.match(/"datePublished"\s*:\s*"([^"]*)"/i) || [])[1];
  const m = (html.match(/property="article:modified_time"[^>]*content="([^"]*)"/i)
    || html.match(/"dateModified"\s*:\s*"([^"]*)"/i) || [])[1];
  return { PUBLICADO: p || null, MODIFICADO: m || null };
}

/**
 * O que os bytes preservados dizem sobre edicao DEPOIS da publicacao.
 *
 * ⚠️ UM `modified` IGUAL A HORA DA NOSSA VISITA NAO E EVIDENCIA DE NADA.
 * Medido em IT-T10-018: os 30 documentos trazem `article:modified_time` a
 * menos de 2 segundos do nosso `CAPTURED_AT`. O campo diz «modificado em» e
 * traz a hora a que NOS batemos a porta. Contado como edicao real, faria a
 * fonte parecer reescrita 30 vezes por dia.
 */
export function evidenciaDeEdicao(observacoes, sourceId) {
  const docs = new Map();
  for (const o of observacoes) {
    if (o.SOURCE_ID !== sourceId || !o.RAW_PATH || !existsSync(o.RAW_PATH)) continue;
    if (!docs.has(o.SOURCE_URL)) docs.set(o.SOURCE_URL, o);
  }
  let comDatas = 0, tardias = 0, rapidas = 0, pegadaNossa = 0, maiorAtraso = 0;
  for (const [, o] of docs) {
    const h = readFileSync(o.RAW_PATH).toString("latin1");
    const { PUBLICADO, MODIFICADO } = datasDoDocumento(h);
    if (!PUBLICADO || !MODIFICADO) continue;
    comDatas++;
    const dp = Date.parse(PUBLICADO), dm = Date.parse(MODIFICADO), dv = Date.parse(o.CAPTURED_AT);
    if (Number.isFinite(dm) && Number.isFinite(dv) && Math.abs(dm - dv) < 120000) { pegadaNossa++; continue; }
    const atraso = dm - dp;
    if (!Number.isFinite(atraso)) continue;
    if (atraso > maiorAtraso) maiorAtraso = atraso;
    if (atraso > DIA) tardias++; else rapidas++;
  }
  return {
    DOCUMENTOS: docs.size, COM_DATAS: comDatas,
    EDITADAS_DEPOIS_DE_24H: tardias, ESTAVEIS_DESDE_A_PUBLICACAO: rapidas,
    DATAS_QUE_SAO_A_NOSSA_VISITA: pegadaNossa,
    MAIOR_ATRASO_DIAS: Number((maiorAtraso / DIA).toFixed(1)),
    // So conta como medicao util o que sobrou depois de tirar a nossa pegada.
    UTEIS: tardias + rapidas,
  };
}

/** A forma da morada: carrega data ou numero proprio de cada item? */
export function formaDoEndereco(urls) {
  if (!urls.length) return { DISCRIMINANTE: false, QUAL: null };
  const comData = urls.filter((u) => /\/(19|20)\d{2}[\/\-_](0?[1-9]|1[0-2])[\/\-_](0?[1-9]|[12]\d|3[01])(\/|$|\.)/.test(u)).length;
  if (comData === urls.length) return { DISCRIMINANTE: true, QUAL: "data no caminho" };
  const distintas = new Set(urls).size;
  if (distintas === urls.length && urls.length >= 3) return { DISCRIMINANTE: true, QUAL: "um segmento proprio por item" };
  return { DISCRIMINANTE: false, QUAL: null };
}

// ── O QUE SE VIU A OLHO, E QUE REGRA NENHUMA APANHA ───────────────────────
// ⚠️ ISTO NAO E UMA EXCEPCAO PARA ARRUMAR RESULTADOS. Cada entrada CITA o que
// se viu, e nenhuma delas melhora a classificacao de ninguem — a unica que ha
// TORNA uma fonte mais suspeita do que a regra automatica a tinha posto.
//
// Uma regra lexical que soubesse ler «avvisi» em italiano seria fragil e
// dava-se mal na proxima lingua. Um olho que olhou, citado, envelhece melhor.
const OLHADO_A_OLHO = Object.freeze({
  "IT-T5-049": {
    PUBLICATION_TOPOLOGY: TOPOLOGIAS.E,
    NOTA: "2 das 4 moradas observadas nao sao artigos, sao quadros de avisos que "
      + "acumulam itens na MESMA morada: /notizie/avvisi-lezioni e "
      + "/notizie/avvisi-esami-e-prove-itinere. As outras 2 sao artigos com "
      + "segmento proprio. Declarar IMMUTABLE a esta fonte cegava os dois quadros.",
  },
});

export function classificar(sourceId, observacoes) {
  const c = CONTRACTS[sourceId];
  const urls = [...new Set(observacoes.filter((o) => o.SOURCE_ID === sourceId && o.SOURCE_URL).map((o) => o.SOURCE_URL))];
  const linha = {
    SOURCE_ID: sourceId,
    SOURCE_NAME: c ? (c.OWNER || "NAO SEI") : "SEM CONTRATO",
    UNIVERSE: c ? (c.TERRITORY || "NAO SEI") : "NAO SEI",
    RECOLLECTION_CURRENT: c && c.RECOLLECTION ? c.RECOLLECTION.DETAIL_CONTENT : "AUSENTE",
    ENDERECOS_OBSERVADOS: urls.length,
  };

  if (!c) {
    return { ...linha, PUBLICATION_TOPOLOGY: TOPOLOGIAS.F, RECOLLECTION_PROPOSED: "UNKNOWN",
      EVIDENCE_TYPE: "SEM_EVIDENCIA", EVIDENCE: "nao ha contrato nenhum para esta fonte",
      CONFIDENCE: "NONE", REASON: "sem contrato nao ha onde declarar", NEEDS_HUMAN_REVIEW: "YES" };
  }

  // ── 1 · CONTRATO MEDIDO A MAO ───────────────────────────────────────────
  const ub = String(c.UPDATE_BEHAVIOR || "");
  const temMedicao = /provado|edicoes|edicões/i.test(String(c.OBSERVED_FREQUENCY || ""));

  // ⚠️ «ADITIVO» SOZINHO NAO CHEGA, E ESTE FOI O ERRO QUE ESTA MISSAO QUASE
  // COMETEU. `UPDATE_BEHAVIOR: "ADITIVO"` diz como aparecem itens NOVOS — nao
  // diz se os VELHOS sao reescritos. Sao duas perguntas, e o campo so responde
  // a primeira.
  //
  // A diferenca esta no que se descarrega:
  //
  //   um FICHEIRO publicado (PDF, CSV, ODS) E a edicao. O nome carrega a data
  //   ou o numero, a edicao seguinte ganha ficheiro proprio, e aquele ficheiro
  //   naquela morada nao volta a ser tocado.
  //
  //   uma PAGINA (HTML, extracto de navegador, metadados de video) e uma
  //   vitrina: o item novo ganha morada propria E a morada antiga continua a
  //   ser servida por um sistema que a pode reescrever a qualquer momento.
  //
  // Medido nesta missao: aplicar «ADITIVO -> IMMUTABLE» sem esta distincao
  // declarava cego o catalogo de produtos da ADAMA (IT-T9-008) — onde uma
  // alteracao de rotulo e precisamente o facto regulatorio que se quer ver.
  const FICHEIRO = ["PDF", "CSV", "ODS", "XLSX", "ZIP", "JSON", "XML"];
  const ehFicheiro = FICHEIRO.includes(String(c.OUTPUT_TYPE || "").toUpperCase());

  if (/^ADITIVO/i.test(ub) && ehFicheiro) {
    return { ...linha, PUBLICATION_TOPOLOGY: TOPOLOGIAS.A, RECOLLECTION_PROPOSED: "IMMUTABLE",
      EVIDENCE_TYPE: "CONTRATO_MEDIDO",
      EVIDENCE: `UPDATE_BEHAVIOR="${ub}" · ${c.OBSERVED_FREQUENCY} · entrega ${c.OUTPUT_TYPE}: o ficheiro publicado E a edicao`,
      CONFIDENCE: temMedicao ? "HIGH" : "MEDIUM",
      REASON: "cada edicao ganha ficheiro proprio numa morada propria; o ficheiro antigo nao e reescrito",
      NEEDS_HUMAN_REVIEW: "NO" };
  }
  if (/^ADITIVO/i.test(ub) && !ehFicheiro) {
    return { ...linha, PUBLICATION_TOPOLOGY: TOPOLOGIAS.C, RECOLLECTION_PROPOSED: "UNKNOWN",
      EVIDENCE_TYPE: "FORMA_DO_ENDERECO",
      EVIDENCE: `UPDATE_BEHAVIOR="${ub}" diz que item novo ganha morada nova, mas a entrega e `
        + `${c.OUTPUT_TYPE} — uma pagina, nao um ficheiro fechado. Ninguem mediu se a pagina antiga e reescrita.`,
      CONFIDENCE: "LOW",
      REASON: "sabe-se descobrir o item novo; nao se sabe se o item velho muda",
      NEEDS_HUMAN_REVIEW: "YES" };
  }
  if (/^SOBRESCRITA/i.test(ub)) {
    return { ...linha, PUBLICATION_TOPOLOGY: TOPOLOGIAS.B, RECOLLECTION_PROPOSED: "MUTABLE",
      EVIDENCE_TYPE: "CONTRATO_MEDIDO", EVIDENCE: `UPDATE_BEHAVIOR="${ub}"`,
      CONFIDENCE: "HIGH", REASON: "a mesma morada recebe a edicao seguinte por cima",
      NEEDS_HUMAN_REVIEW: "NO" };
  }

  // ── 2 · AS DATAS DENTRO DOS BYTES ───────────────────────────────────────
  const ed = evidenciaDeEdicao(observacoes, sourceId);
  if (ed.UTEIS >= 2) {
    const mutavel = ed.EDITADAS_DEPOIS_DE_24H > 0;
    const conf = ed.UTEIS >= 5 ? "HIGH" : "MEDIUM";
    // ⚠️ MUTAVEL NAO IMPLICA «UMA SO MORADA», e chamar-lhe B seria impreciso.
    // Estas fontes fazem as DUAS coisas ao mesmo tempo: cada artigo novo ganha
    // morada propria (aditivo), E os artigos antigos sao reescritos meses
    // depois, na mesma morada. Isso e `E MIXED` — «parte nova, parte
    // sobrescreve» — e nao `B MUTABLE_STABLE_URL`, que e a fonte de morada
    // unica onde a edicao seguinte apaga a anterior.
    //
    // A topologia e so analise e nao entra no contrato; mas uma etiqueta
    // errada no censo le-se depois como facto, e o dono decide por ela.
    const moradaPropriaPorItem = formaDoEndereco(urls).DISCRIMINANTE;
    return { ...linha,
      PUBLICATION_TOPOLOGY: !mutavel ? TOPOLOGIAS.A
        : moradaPropriaPorItem ? TOPOLOGIAS.E : TOPOLOGIAS.B,
      RECOLLECTION_PROPOSED: mutavel ? "MUTABLE" : "IMMUTABLE",
      EVIDENCE_TYPE: "DATAS_NO_DOCUMENTO",
      EVIDENCE: `${ed.UTEIS} documentos com published+modified proprios; `
        + `${ed.EDITADAS_DEPOIS_DE_24H} editados mais de 24h depois de publicados; `
        + `maior atraso ${ed.MAIOR_ATRASO_DIAS} dias`,
      CONFIDENCE: conf,
      REASON: mutavel
        ? (moradaPropriaPorItem
          ? "cada artigo novo ganha morada propria E os antigos sao reescritos nela meses depois"
          : "a fonte reescreve o que publicou, e a morada nao muda com isso")
        : "todos os documentos assentam na publicacao e nao voltam a ser tocados",
      NEEDS_HUMAN_REVIEW: "NO" };
  }

  // ── 3 e 4 · REVISITA E FORMA DO ENDERECO — nunca chegam para declarar ───
  const forma = formaDoEndereco(urls);
  const porque = ed.DATAS_QUE_SAO_A_NOSSA_VISITA > 0
    ? `as ${ed.DATAS_QUE_SAO_A_NOSSA_VISITA} datas de modificacao sao a hora da NOSSA visita — nao dizem nada sobre a fonte`
    : urls.length === 0 ? "nenhuma observacao guardada" : "os documentos nao declaram data de publicacao nem de modificacao";
  return { ...linha,
    PUBLICATION_TOPOLOGY: forma.DISCRIMINANTE ? TOPOLOGIAS.C : TOPOLOGIAS.F,
    RECOLLECTION_PROPOSED: "UNKNOWN",
    EVIDENCE_TYPE: forma.DISCRIMINANTE ? "FORMA_DO_ENDERECO" : "SEM_EVIDENCIA",
    EVIDENCE: forma.DISCRIMINANTE ? `${forma.QUAL} (${urls.length} enderecos); ${porque}` : porque,
    CONFIDENCE: forma.DISCRIMINANTE ? "LOW" : "NONE",
    REASON: "a forma da morada sugere item proprio, mas ninguem mediu se o item e reescrito depois",
    NEEDS_HUMAN_REVIEW: "YES" };
}

export function tabela(ids = CONTRACT_IDS) {
  const obs = lerObservacoes();
  return ids.map((id) => {
    let l = classificar(id, obs);
    const olho = OLHADO_A_OLHO[id];
    if (olho) {
      // O olho corrige a TOPOLOGIA e junta a nota a evidencia. Nunca mexe em
      // `RECOLLECTION_PROPOSED`: uma fonte por olhar continua por declarar.
      l = { ...l, PUBLICATION_TOPOLOGY: olho.PUBLICATION_TOPOLOGY,
        EVIDENCE: `${l.EVIDENCE} · OLHADO A OLHO: ${olho.NOTA}`,
        NEEDS_HUMAN_REVIEW: "YES" };
    }
    const a = admissivelNaBigCollection(id, CONTRACTS[id] || null);
    return { ...l, COBERTURA_HOJE: a.COBERTURA, ADMISSIVEL_HOJE: a.ADMISSIVEL };
  });
}

if (process.argv[1] && process.argv[1].endsWith("recollection_topologia.mjs")) {
  const alvo = process.argv[2] ? process.argv[2].split(",") : null;
  const t = tabela(alvo || CONTRACT_IDS);
  const mostra = alvo ? t : t.filter((l) => l.CONFIDENCE !== "NONE" || l.ENDERECOS_OBSERVADOS > 0);
  for (const l of mostra) {
    console.log(`${l.SOURCE_ID.padEnd(11)} ${String(l.PUBLICATION_TOPOLOGY).padEnd(33)} ` +
      `agora=${String(l.RECOLLECTION_CURRENT).padEnd(9)} proposto=${String(l.RECOLLECTION_PROPOSED).padEnd(9)} ` +
      `${String(l.CONFIDENCE).padEnd(6)} ${l.EVIDENCE_TYPE}`);
    console.log(`            ${l.EVIDENCE}`);
  }
  const conta = {};
  for (const l of t) conta[l.PUBLICATION_TOPOLOGY] = (conta[l.PUBLICATION_TOPOLOGY] || 0) + 1;
  console.log("\nPARETO POR TOPOLOGIA (os 186):");
  for (const k of Object.keys(conta).sort((a, b) => conta[b] - conta[a])) console.log(" ", String(conta[k]).padStart(4), k);
  console.log("\nWITH_RECOLLECTION_BEFORE   ", t.filter((l) => l.RECOLLECTION_CURRENT !== "AUSENTE").length);
  console.log("PROPOSTAS_NOVAS            ", t.filter((l) => l.RECOLLECTION_CURRENT === "AUSENTE" && l.RECOLLECTION_PROPOSED !== "UNKNOWN").length);
  console.log("UNKNOWN_RECOLLECTION_AFTER ", t.filter((l) => l.RECOLLECTION_CURRENT === "AUSENTE" && l.RECOLLECTION_PROPOSED === "UNKNOWN").length);
}
