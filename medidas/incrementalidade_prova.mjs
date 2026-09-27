// A PROVA DA INCREMENTALIDADE — RUN A e RUN B sobre a MESMA populacao.
//
// ZERO REDE. E nao por promessa: o transporte e um FALSO que conta cada
// chamada e serve os bytes que ja estao no disco. Se a regra decidir ir
// buscar alguma coisa, o contador acusa — e o contador e a prova, nao o
// `git status`.
//
//     NAO DEPENDER DO PORTAO PARA IMPEDIR A REDE.
//     A CORRIDA DE PROVA NAO TEM COMO LA CHEGAR.
//
// A populacao e REAL: os 85 enderecos que a CANONICAL-MICRO-V1 colheu a
// 2026-09-21, lidos do livro. Nao e uma populacao inventada para dar jeito.
//
// Saida: medidas/INCREMENTALIDADE-V1.json

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  memoriaDosDetalhes, decidirSobreDetalhe, decidirSobreIndice,
  censoDasDecisoes, RESULTADOS_COM_DOCUMENTO,
} from "../regras/incrementalidade.mjs";

const RAIZ = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const LIVRO = join(RAIZ, "data", "collection-ledger", "italy", "observations.ndjson");
const SAIDA = join(RAIZ, "medidas", "INCREMENTALIDADE-V1.json");

function lerLivro() {
  return readFileSync(LIVRO, "utf8").split("\n").filter((l) => l.trim())
    .map((l) => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

// ── O TRANSPORTE FALSO ────────────────────────────────────────────────────
// Serve do DISCO, conta tudo, e nao sabe fazer rede. Um `fetch` a serio nao
// existe neste processo: nao ha import de `node:https`, nao ha `fetch(`.
function transporteFalso(livro) {
  const porUrl = new Map();
  for (const o of livro) {
    if (o.SOURCE_URL && o.RAW_PATH) porUrl.set(o.SOURCE_URL, o.RAW_PATH);
  }
  const chamadas = [];
  return {
    chamadas,
    buscar(url) {
      chamadas.push(url);
      const p = porUrl.get(url);
      const abs = p ? join(RAIZ, p.replace(/^\.[\\/]/, "")) : null;
      if (!abs || !existsSync(abs)) return { erro: "sem bytes no armazem", status: 0 };
      return { buf: readFileSync(abs), status: 200, tentativas: 1 };
    },
  };
}

function corrida(nome, { urls, memoria, livro, agora, contratos = {} }) {
  const transporte = transporteFalso(livro);
  // O INDICE revisita-se sempre — uma vez por fonte.
  const fontes = [...new Set(urls.map((u) => u.SOURCE_ID))];
  let indiceRequests = 0;
  for (const _f of fontes) { decidirSobreIndice(); indiceRequests++; }

  const decisoes = [];
  for (const { url, SOURCE_ID } of urls) {
    const d = decidirSobreDetalhe(url, {
      memoria, sourceId: SOURCE_ID, contrato: contratos[SOURCE_ID] || null, agora,
    });
    decisoes.push(d);
    // ⚠️ SO SE BATE A PORTA QUANDO A DECISAO O MANDA. Esta linha e o ponto
    // onde a regra passa de opiniao a comportamento — e o contador do
    // transporte e que diz se ela foi mesmo obedecida.
    if (d.DECISAO === "FETCH" || d.DECISAO === "REVALIDATE") transporte.buscar(url);
  }

  const censo = censoDasDecisoes(decisoes, { indiceRequests });
  return {
    RUN: nome,
    POPULACAO: urls.length,
    FONTES: fontes.length,
    ...censo,
    // A PROVA: pedidos que a regra AUTORIZOU vs portas a que se bateu mesmo.
    DETAIL_REQUESTS_CONTADOS_NO_TRANSPORTE: transporte.chamadas.length,
    COERENTE: transporte.chamadas.length === censo.DETAIL_REQUESTS,
    decisoes,
  };
}

function main() {
  const livro = lerLivro();

  // ── a populacao real: a VAGA A de 2026-09-21, os 85 que foram colhidos ──
  const carimbo = (r) => String(r || "").split("-")[5] || "";
  const vagaA = livro.filter((o) => String(o.RUN_ID).includes("2026-09-21") &&
    carimbo(o.RUN_ID) < "193400" && RESULTADOS_COM_DOCUMENTO.includes(o.OBSERVATION_RESULT));
  const urls = [...new Map(vagaA.map((o) => [o.SOURCE_URL, o])).values()]
    .map((o) => ({ url: o.SOURCE_URL, SOURCE_ID: o.SOURCE_ID }));

  // ── F5 · ETag / Last-Modified: MEDIR, NAO SUPOR ────────────────────────
  // Pergunta-se ao livro, que e o unico registo do que as fontes responderam.
  // Nao se vai a rede para descobrir: a missao proibe, e com razao.
  const comEtag = livro.filter((o) => o.HTTP_ETAG).length;
  const comLastMod = livro.filter((o) => o.HTTP_LAST_MODIFIED).length;
  const f5 = {
    OBSERVACOES_NO_LIVRO: livro.length,
    OBSERVACOES_COM_ETAG_GRAVADO: comEtag,
    OBSERVACOES_COM_LAST_MODIFIED_GRAVADO: comLastMod,
    // ⚠️ AS TRES RESPOSTAS SAO DIFERENTES, e so a terceira e verdade aqui:
    //   «as fontes NAO oferecem»  -> afirmacao sobre a FONTE
    //   «nos nao usamos»          -> afirmacao sobre NOS
    //   «NAO SEI»                 -> nunca se perguntou
    CONDITIONAL_REQUEST_IMPLEMENTED: false,
    COLECTOR_PEDE_VALIDADOR: false,
    COLECTOR_GRAVA_VALIDADOR: false,
    SOURCES_OFFER_ETAG: "NAO SEI",
    PORQUE: "o coletor nunca enviou If-None-Match nem If-Modified-Since e nunca "
          + "gravou ETag nem Last-Modified; zero ocorrencias em " + livro.length
          + " observacoes. Saber se as fontes oferecem exige um pedido a rede, "
          + "que esta missao nao autoriza. NAO SEI e a resposta honesta — "
          + "dizer «nao oferecem» seria uma afirmacao sobre a fonte assente "
          + "num silencio nosso.",
    CAPACIDADE_INVENTADA: false,
  };

  // ── RUN A: memoria vazia. Tudo e novo. ─────────────────────────────────
  const runA = corrida("RUN_A", { urls, memoria: new Map(), livro, agora: "2026-09-21T19:26:00Z" });

  // ── RUN B: a memoria e o que a RUN A deixou escrito no livro. ──────────
  // Nao se fabrica a memoria: le-se do livro real, exactamente como o coletor
  // a leria na corrida seguinte.
  const memoriaB = memoriaDosDetalhes(vagaA);
  const runB = corrida("RUN_B", { urls, memoria: memoriaB, livro, agora: "2026-09-21T19:34:00Z" });

  const resultado = {
    MEDIDOR: "medidas/incrementalidade_prova.mjs",
    REDE: "ZERO — transporte falso, bytes do disco, sem import de https/fetch",
    POPULACAO: "os 85 enderecos reais colhidos a 2026-09-21 (vaga A)",
    F5_VALIDADORES: f5,
    RUN_A: { ...runA, decisoes: undefined },
    RUN_B: { ...runB, decisoes: undefined },
    // ── os nomes que o briefing pediu, tal e qual ────────────────────────
    BRIEFING: {
      INDEX_REQUESTS_RUN_B: runB.INDEX_REQUESTS,
      DETAIL_NEW_RUN_B: runB.DETAIL_NEW,
      DETAIL_SKIPPED_KNOWN_RUN_B: runB.DETAIL_SKIPPED_KNOWN,
      DETAIL_REVALIDATED_RUN_B: runB.DETAIL_REVALIDATED,
      DETAIL_REFETCHED_RUN_B: runB.DETAIL_REFETCHED,
      UNNECESSARY_REFETCHES_RUN_B: runB.UNNECESSARY_REFETCHES,
    },
    // O que o coletor de hoje faria com a MESMA populacao, para se ver a
    // diferenca em numero e nao em adjectivo.
    COMPORTAMENTO_MEDIDO_DO_COLETOR_ACTUAL: {
      DETAIL_REQUESTS_RUN_B: 85,
      DETAIL_SKIPPED_KNOWN_RUN_B: 0,
      PORQUE: "italy_pilot_collect.mjs:474 chama baixar() antes de a linha 502 "
            + "perguntar se o documento ja era conhecido",
    },
  };

  writeFileSync(SAIDA, JSON.stringify(resultado, null, 1), "utf8");

  const p = (t, o) => {
    console.log(`\n${t}`);
    for (const [k, v] of Object.entries(o)) {
      if (v === undefined || k === "decisoes") continue;
      console.log(`  ${k.padEnd(42)} ${typeof v === "object" ? JSON.stringify(v) : v}`);
    }
  };
  p("=== F5 · VALIDADORES (ETag / Last-Modified) ===", f5);
  p("=== RUN A (memoria vazia) ===", { ...runA, decisoes: undefined });
  p("=== RUN B (memoria = o que a RUN A deixou) ===", { ...runB, decisoes: undefined });
  p("=== CAMPOS DO BRIEFING ===", resultado.BRIEFING);
  p("=== O COLETOR DE HOJE, MESMA POPULACAO ===", resultado.COMPORTAMENTO_MEDIDO_DO_COLETOR_ACTUAL);
  console.log(`\n  escrito: medidas/INCREMENTALIDADE-V1.json`);

  // Falha alto se a regra nao se comportou: um medidor que sai 0 a mentir e
  // pior do que nenhum.
  if (!runA.COERENTE || !runB.COERENTE) {
    console.log("\n  INCOERENTE: decisoes e portas batidas nao batem certo");
    process.exit(1);
  }
}

main();
