// SINTONIA EAME — CENSO DE RECOLLECTION · A EVIDENCIA, ANTES DA OPINIAO
//
// Esta medicao NAO toca na rede. Le tres coisas que ja estao no disco:
//
//   1 · os 186 contratos            (regras/italy_contracts.mjs)
//   2 · o livro de observacoes      (data/collection-ledger/italy/observations.ndjson)
//   3 · os brutos preservados       (data/collection-store/italy/...)
//
// E responde a UMA pergunta por fonte: quando se voltou ao MESMO endereco,
// o que la estava tinha mudado de verdade, ou so se tinha mexido?
//
// ⚠️ PORQUE NAO BASTA COMPARAR `RAW_SHA256`. O livro tem 83 linhas
// `DOCUMENT_CHANGED_IN_PLACE`, e a CANONICAL-MICRO-V1 ja mediu que a maioria
// dessas diferencas e a NOSSA PROPRIA PEGADA: contador de visitas, nonce de
// sessao, `article:modified_time` que marca a hora em que batemos a porta.
// Contar shas diferentes classificaria como MUTAVEL uma fonte que nao mudou
// uma virgula — que e o defeito M2 do red team desta missao.
//
// Por isso a comparacao passa por `compararConteudo()`, que separa
// MATERIAL_CHANGE de VOLATILE_ONLY. A evidencia e o veredicto dele, nunca o sha.
//
//     MESMO ENDERECO + TEXTO MATERIALMENTE DIFERENTE  = prova de MUTABLE
//     MESMO ENDERECO + so ruido volatil               = NAO e prova de nada
//
// A segunda assimetria, e ela e deliberada: ver mudanca PROVA que muda; NAO
// ver mudanca em duas visitas com minutos de intervalo NAO prova que nunca
// muda. Por isso esta medicao so emite `PROVA_MUTAVEL`; a ausencia dela sai
// como `SEM_PROVA`, e nunca como `PROVA_IMUTAVEL`.

import { readFileSync, existsSync } from "node:fs";
import { compararConteudo } from "../regras/normalizacao_de_conteudo.mjs";
import { CONTRACTS, CONTRACT_IDS } from "../regras/italy_contracts.mjs";

const LEDGER = "data/collection-ledger/italy/observations.ndjson";

export function lerObservacoes(caminho = LEDGER) {
  if (!existsSync(caminho)) return [];
  return readFileSync(caminho, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
}

/**
 * Para cada endereco com DOIS OU MAIS brutos preservados, compara versoes
 * consecutivas. Devolve o censo por fonte.
 */
export function censoDeRevisitas(observacoes) {
  const porUrl = new Map();
  let semFicheiro = 0;
  for (const o of observacoes) {
    if (!o.SOURCE_URL) continue;
    if (!o.RAW_PATH) continue;
    if (!existsSync(o.RAW_PATH)) { semFicheiro++; continue; }
    if (!porUrl.has(o.SOURCE_URL)) porUrl.set(o.SOURCE_URL, []);
    porUrl.get(o.SOURCE_URL).push(o);
  }

  const porFonte = new Map();
  for (const [url, obs] of porUrl) {
    obs.sort((a, b) => String(a.CAPTURED_AT).localeCompare(String(b.CAPTURED_AT)));
    const sid = obs[0].SOURCE_ID || "SEM_SOURCE_ID";
    if (!porFonte.has(sid)) porFonte.set(sid, {
      SOURCE_ID: sid, URLS_COM_BRUTO: 0, URLS_REVISITADAS: 0, PARES: 0,
      IDENTICAL_BYTES: 0, VOLATILE_ONLY: 0, MATERIAL_CHANGE: 0,
      NORMALIZADOR_SUSPEITO: 0, EXEMPLOS_MATERIAIS: [],
    });
    const f = porFonte.get(sid);
    f.URLS_COM_BRUTO++;

    // Uma versao por ficheiro distinto: o livro repete a mesma versao em
    // `SEEN_AGAIN`, e contar a repeticao como par inflacionaria o denominador.
    const vistos = new Set();
    const versoes = obs.filter((o) => {
      if (vistos.has(o.RAW_PATH)) return false;
      vistos.add(o.RAW_PATH); return true;
    });
    if (versoes.length >= 2) f.URLS_REVISITADAS++;
    for (let i = 1; i < versoes.length; i++) {
      const c = compararConteudo(readFileSync(versoes[i - 1].RAW_PATH), readFileSync(versoes[i].RAW_PATH));
      f.PARES++;
      f[c.VEREDICTO === "IDENTICAL_BYTES" ? "IDENTICAL_BYTES"
        : c.VEREDICTO === "VOLATILE_ONLY" ? "VOLATILE_ONLY" : "MATERIAL_CHANGE"]++;
      if (c.AVISO) f.NORMALIZADOR_SUSPEITO++;
      if (c.VEREDICTO === "MATERIAL_CHANGE" && f.EXEMPLOS_MATERIAIS.length < 3) {
        f.EXEMPLOS_MATERIAIS.push({ URL: url, DE: c.OLD_RAW_SHA.slice(0, 12), PARA: c.NEW_RAW_SHA.slice(0, 12) });
      }
    }
  }
  return { PORTE: porUrl.size, OBS_COM_RAW_PATH_SEM_FICHEIRO: semFicheiro, FONTES: [...porFonte.values()] };
}

/** O que o livro sabe de cada fonte, mesmo sem bruto no disco. */
export function censoDoLivro(observacoes) {
  const porFonte = new Map();
  for (const o of observacoes) {
    const sid = o.SOURCE_ID || "SEM_SOURCE_ID";
    if (!porFonte.has(sid)) porFonte.set(sid, { SOURCE_ID: sid, OBS: 0, URLS: new Set(), RESULTADOS: {}, VALIDADORES: 0 });
    const f = porFonte.get(sid);
    f.OBS++;
    if (o.SOURCE_URL) f.URLS.add(o.SOURCE_URL);
    f.RESULTADOS[o.OBSERVATION_RESULT] = (f.RESULTADOS[o.OBSERVATION_RESULT] || 0) + 1;
    if (o.HTTP_ETAG || o.HTTP_LAST_MODIFIED) f.VALIDADORES++;
  }
  return [...porFonte.values()].map((f) => ({ ...f, URLS: f.URLS.size }));
}

export function censoDosContratos() {
  const c = { TOTAL: CONTRACT_IDS.length, COM_RECOLLECTION: [], SEM_RECOLLECTION: [], POR_VALOR: {} };
  for (const id of CONTRACT_IDS) {
    const r = CONTRACTS[id] && CONTRACTS[id].RECOLLECTION;
    if (r) {
      c.COM_RECOLLECTION.push(id);
      c.POR_VALOR[r.DETAIL_CONTENT] = (c.POR_VALOR[r.DETAIL_CONTENT] || 0) + 1;
    } else c.SEM_RECOLLECTION.push(id);
  }
  return c;
}

if (process.argv[1] && process.argv[1].endsWith("recollection_censo.mjs")) {
  const obs = lerObservacoes();
  const contratos = censoDosContratos();
  console.log("CONTRACTS_TOTAL         ", contratos.TOTAL);
  console.log("WITH_RECOLLECTION       ", contratos.COM_RECOLLECTION.length, contratos.COM_RECOLLECTION.join(" "));
  console.log("  por valor             ", JSON.stringify(contratos.POR_VALOR));
  console.log("WITHOUT_RECOLLECTION    ", contratos.SEM_RECOLLECTION.length);
  console.log("");
  const r = censoDeRevisitas(obs);
  console.log("OBSERVACOES             ", obs.length);
  console.log("URLS_COM_BRUTO_NO_DISCO ", r.PORTE);
  console.log("OBS_SEM_O_FICHEIRO      ", r.OBS_COM_RAW_PATH_SEM_FICHEIRO);
  console.log("");
  console.log("FONTE         URLS  REVIS  PARES  IDENT  VOLAT  MATER  SUSPEITO");
  for (const f of r.FONTES.sort((a, b) => a.SOURCE_ID.localeCompare(b.SOURCE_ID))) {
    console.log(f.SOURCE_ID.padEnd(13),
      String(f.URLS_COM_BRUTO).padStart(4), String(f.URLS_REVISITADAS).padStart(6),
      String(f.PARES).padStart(6), String(f.IDENTICAL_BYTES).padStart(6),
      String(f.VOLATILE_ONLY).padStart(6), String(f.MATERIAL_CHANGE).padStart(6),
      String(f.NORMALIZADOR_SUSPEITO).padStart(9));
    for (const e of f.EXEMPLOS_MATERIAIS) console.log("      MATERIAL:", e.URL, e.DE, "->", e.PARA);
  }
  console.log("");
  console.log("LIVRO — resultados por fonte:");
  for (const f of censoDoLivro(obs).sort((a, b) => a.SOURCE_ID.localeCompare(b.SOURCE_ID))) {
    console.log(f.SOURCE_ID.padEnd(13), "obs=" + String(f.OBS).padStart(3), "urls=" + String(f.URLS).padStart(3),
      "validadores=" + f.VALIDADORES, JSON.stringify(f.RESULTADOS));
  }
}
