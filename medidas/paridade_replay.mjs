// O REPLAY OFFLINE DA PARIDADE — ZERO REDE.
//
// Le os bytes que as DUAS corridas do canario ja deixaram em disco e responde
// a duas perguntas separadas, com os nomes do briefing:
//
//   FASE 2 · ONDE NASCE O FALSO `DOCUMENT_CHANGED_IN_PLACE`
//            por documento: RAW_CHANGED · NORMALIZED_CHANGED ·
//            VISIBLE_TEXT_CHANGED · VOLATILE_DIFFERENCE
//
//   FASE 6 · O QUE A REGRA DE REVISITA TERIA DECIDIDO NA RUN2
//            aplicando `decidirSobreDetalhe()` sobre o livro TAL COMO ELE
//            ESTAVA ao fim da RUN1 — sem inventar estado nenhum.
//
// ⚠️ ISTO NAO ESCREVE NO LIVRO NEM NO ARMAZEM. So le.
//
// Uso:
//   node medidas/paridade_replay.mjs --raiz=<ITALY_OPS_ROOT> --run1=<ID> --run2=<ID>

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { join, dirname, isAbsolute } from "node:path";
import { pathToFileURL } from "node:url";

import { memoriaDosDetalhes, decidirSobreDetalhe, censoDasDecisoes } from "../regras/incrementalidade.mjs";
import { compararConteudo, CONTRATO_NORMALIZACAO_VERSAO } from "../regras/normalizacao_de_conteudo.mjs";

export function lerLivro(raiz) {
  const p = join(raiz, "data", "collection-ledger", "italy", "observations.ndjson");
  if (!existsSync(p)) throw new Error(`livro ausente: ${p}`);
  return readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
}

// `RAW_PATH` foi gravado relativo a `ITALY_OPS_ROOT` (o coletor corre com
// `RAIZ = process.env.ITALY_OPS_ROOT || "."`). Resolve-se contra a raiz que
// nos deram, e nunca contra o cwd de quem mede.
function caminhoDoRaw(raiz, obs) {
  if (!obs.RAW_PATH) return null;
  const p = String(obs.RAW_PATH).replace(/^\.[\/\\]/, "");
  return isAbsolute(p) ? p : join(raiz, p);
}

export function replay(raiz, run1, run2) {
  const livro = lerLivro(raiz);

  const a = new Map(), b = new Map();
  for (const o of livro) {
    if (!o.DOCUMENT_ID) continue;
    if (o.RUN_ID === run1) a.set(o.DOCUMENT_ID, o);
    if (o.RUN_ID === run2) b.set(o.DOCUMENT_ID, o);
  }
  if (a.size === 0) throw new Error(`RUN1 ${run1} nao tem observacoes com DOCUMENT_ID no livro`);
  if (b.size === 0) throw new Error(`RUN2 ${run2} nao tem observacoes com DOCUMENT_ID no livro`);

  // ── FASE 2 · O CONTEUDO ─────────────────────────────────────────────────
  const conteudo = [];
  for (const [docId, o1] of a) {
    const o2 = b.get(docId);
    if (!o2) continue;
    const p1 = caminhoDoRaw(raiz, o1), p2 = caminhoDoRaw(raiz, o2);
    if (!p1 || !p2 || !existsSync(p1) || !existsSync(p2)) {
      // ⚠️ BYTES EM FALTA NAO SAO BYTES IGUAIS. Diz-se, e nao se conta.
      conteudo.push({ DOCUMENT_ID: docId, SOURCE_ID: o1.SOURCE_ID, VEREDICTO: "BYTES_AUSENTES",
                      OLD_RAW_SHA: o1.RAW_SHA256, NEW_RAW_SHA: o2.RAW_SHA256 });
      continue;
    }
    const c = compararConteudo(readFileSync(p1), readFileSync(p2));
    conteudo.push({
      DOCUMENT_ID: docId, SOURCE_ID: o1.SOURCE_ID, SOURCE_URL: o1.SOURCE_URL,
      RUN1_SHA_RAW: o1.RAW_SHA256, RUN2_SHA_RAW: o2.RAW_SHA256,
      RUN1_BYTES: o1.BYTES, RUN2_BYTES: o2.BYTES,
      RUN2_OBSERVATION_RESULT_ANTES: o2.OBSERVATION_RESULT,
      ...c,
    });
  }

  // ── FASE 6 · A DECISAO DE IR, COM O LIVRO AO FIM DA RUN1 ────────────────
  // O livro e append-only e a ordem dele e a cronologia: corta-se na ultima
  // linha da RUN1 e a memoria fica sendo exactamente o que a RUN2 teria
  // visto se alguem lhe tivesse perguntado antes de bater a porta.
  let corte = -1;
  for (let i = 0; i < livro.length; i++) if (livro[i].RUN_ID === run1) corte = i;
  const ateRun1 = livro.slice(0, corte + 1);
  const memoria = memoriaDosDetalhes(ateRun1);

  // Os enderecos que a RUN2 foi mesmo buscar — nao os que ela poderia ter ido.
  const urlsDaRun2 = [];
  const vistos = new Set();
  for (const o of livro) {
    if (o.RUN_ID !== run2 || !o.SOURCE_URL || vistos.has(o.SOURCE_URL)) continue;
    vistos.add(o.SOURCE_URL);
    urlsDaRun2.push({ url: o.SOURCE_URL, sourceId: o.SOURCE_ID });
  }

  const decisoes = urlsDaRun2.map(({ url, sourceId }) => ({
    SOURCE_URL: url, SOURCE_ID: sourceId,
    ...decidirSobreDetalhe(url, { memoria, sourceId, contrato: null, agora: null }),
  }));
  // ⚠️ `indiceRequests` NAO E ADIVINHADO: 1 por fonte que a RUN2 tocou, que e
  // o que `alvosDoContrato` gasta para ler o indice. Escrito, nao suposto.
  const fontesDaRun2 = new Set(urlsDaRun2.map((x) => x.sourceId));
  const censo = censoDasDecisoes(decisoes, { indiceRequests: fontesDaRun2.size });

  const materiais = conteudo.filter((c) => c.VEREDICTO === "MATERIAL_CHANGE");
  const volateis = conteudo.filter((c) => c.VEREDICTO === "VOLATILE_ONLY");
  const iguais = conteudo.filter((c) => c.VEREDICTO === "IDENTICAL_BYTES");
  const avisos = conteudo.filter((c) => c.AVISO);

  const trechos = {};
  for (const c of conteudo) for (const t of c.TRECHOS_VOLATEIS_ENCONTRADOS || []) trechos[t] = (trechos[t] || 0) + 1;

  return {
    MEDIDOR: "medidas/paridade_replay.mjs",
    NORMALIZACAO_VERSAO: CONTRATO_NORMALIZACAO_VERSAO,
    RAIZ: raiz, RUN1: run1, RUN2: run2,
    REDE: "NAO_SE_APLICA — este medidor so le disco",
    FASE2: {
      PARES_COMPARADOS: conteudo.length,
      RAW_CHANGED: conteudo.filter((c) => c.RAW_CHANGED).length,
      NORMALIZED_CHANGED: materiais.length,
      VOLATILE_DIFFERENCE: volateis.length,
      IDENTICAL_BYTES: iguais.length,
      BYTES_AUSENTES: conteudo.filter((c) => c.VEREDICTO === "BYTES_AUSENTES").length,
      TRECHOS_VOLATEIS_POR_DOCUMENTO: trechos,
      NORMALIZADOR_SUSPEITO: avisos.length,
      // O que a RUN2 escreveu no livro antes desta missao, e o que sobra.
      FALSE_DOCUMENT_CHANGED_IN_PLACE: conteudo.filter(
        (c) => c.RUN2_OBSERVATION_RESULT_ANTES === "DOCUMENT_CHANGED_IN_PLACE" && c.VEREDICTO !== "MATERIAL_CHANGE").length,
      MATERIAL_DIFF_EXEMPLOS: materiais.slice(0, 5).map((c) => ({
        DOCUMENT_ID: c.DOCUMENT_ID, OLD_NORMALIZED_HASH: c.OLD_NORMALIZED_HASH, NEW_NORMALIZED_HASH: c.NEW_NORMALIZED_HASH })),
    },
    FASE6: {
      DETALHES_QUE_A_RUN2_PEDIU: urlsDaRun2.length,
      CENSO_SE_A_REGRA_HOUVESSE_CORRIDO: censo,
      // A poupanca so conta enderecos que a RUN2 FOI mesmo buscar e que a
      // regra teria saltado. Um endereco novo nao e poupanca nenhuma.
      PEDIDOS_EVITAVEIS: censo.DETAIL_SKIPPED_KNOWN,
      PEDIDOS_LEGITIMOS: censo.DETAIL_NEW + censo.DETAIL_REVALIDATED + censo.DETAIL_REFETCHED,
      UNNECESSARY_REFETCHES: censo.UNNECESSARY_REFETCHES,
    },
    DETALHE_CONTEUDO: conteudo,
    DETALHE_DECISOES: decisoes,
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const arg = (n) => (process.argv.find((a) => a.startsWith(`--${n}=`)) || "").split("=").slice(1).join("=");
  const raiz = arg("raiz"), run1 = arg("run1"), run2 = arg("run2");
  if (!raiz || !run1 || !run2) {
    console.error("uso: node medidas/paridade_replay.mjs --raiz=<ITALY_OPS_ROOT> --run1=<ID> --run2=<ID>");
    process.exit(2);
  }
  const r = replay(raiz, run1, run2);
  const saida = arg("saida") || join(dirname(process.argv[1]), "PARIDADE-REPLAY-V1.json");
  mkdirSync(dirname(saida), { recursive: true });
  writeFileSync(saida, JSON.stringify(r, null, 1));
  const { DETALHE_CONTEUDO, DETALHE_DECISOES, ...resumo } = r;
  console.log(JSON.stringify(resumo, null, 1));
  console.log(`\n  escrito: ${saida}`);
}
