// O QUE MUDOU MESMO, LINHA A LINHA — para NAO acreditar num veredicto sem o ver.
//
// `compararConteudo()` diz MATERIAL_CHANGE quando o conteudo normalizado
// muda. Mas o normalizador tem uma lista FECHADA de trechos volateis, afinada
// em 2026-09-22 sobre DUAS fontes (myfruit, zootecnica). Um site que nao esteja
// nessa lista traz o nonce dele por classificar — e um nonce por classificar
// le-se como MATERIAL_CHANGE.
//
//     UM VEREDICTO DE MUDANCA QUE NINGUEM OLHOU
//     E UMA OPINIAO COM AR DE MEDICAO.
//
// Uso: node medidas/recollection_diff.mjs <SOURCE_ID> [quantas linhas]

import { readFileSync, existsSync } from "node:fs";
import { lerObservacoes } from "./recollection_censo.mjs";
import { normalizarConteudo, textoVisivel, textoNormalizado }
  from "../regras/normalizacao_de_conteudo.mjs";

const alvo = process.argv[2];
const LIMITE = Number(process.argv[3] || 25);

const obs = lerObservacoes().filter((o) => o.SOURCE_ID === alvo && o.RAW_PATH && existsSync(o.RAW_PATH));
const porUrl = new Map();
for (const o of obs) {
  if (!porUrl.has(o.SOURCE_URL)) porUrl.set(o.SOURCE_URL, []);
  porUrl.get(o.SOURCE_URL).push(o);
}

for (const [url, lista] of porUrl) {
  lista.sort((a, b) => String(a.CAPTURED_AT).localeCompare(String(b.CAPTURED_AT)));
  const vistos = new Set();
  const v = lista.filter((o) => { if (vistos.has(o.RAW_PATH)) return false; vistos.add(o.RAW_PATH); return true; });
  if (v.length < 2) continue;

  const A = readFileSync(v[0].RAW_PATH), B = readFileSync(v[1].RAW_PATH);
  const na = normalizarConteudo(A), nb = normalizarConteudo(B);
  if (na.NORMALIZED_SHA === nb.NORMALIZED_SHA) continue;

  console.log("=".repeat(78));
  console.log("URL   ", url);
  console.log("VISITA 1", v[0].CAPTURED_AT, v[0].BYTES, "bytes");
  console.log("VISITA 2", v[1].CAPTURED_AT, v[1].BYTES, "bytes");
  console.log("TEXTO_VISIVEL_MUDOU", textoVisivel(A) === null ? "NAO_APLICAVEL"
    : String(textoVisivel(A)) !== String(textoVisivel(B)));

  // Diferenca sobre o NORMALIZADO: e sobre ele que o veredicto se forma.
  const ta = textoNormalizado(A).TEXTO, tb = textoNormalizado(B).TEXTO;
  if (ta === null) { console.log("NAO E HTML — o normalizador nao se aplica; bytes diferentes = MATERIAL por omissao"); break; }
  const la = ta.split(/\r?\n/);
  const lb = tb.split(/\r?\n/);
  const sa = new Set(la), sb = new Set(lb);
  const so_a = la.filter((l) => !sb.has(l) && l.trim());
  const so_b = lb.filter((l) => !sa.has(l) && l.trim());
  console.log(`LINHAS so na 1: ${so_a.length}   so na 2: ${so_b.length}`);
  for (const l of so_a.slice(0, LIMITE)) console.log("  - ", l.slice(0, 220));
  for (const l of so_b.slice(0, LIMITE)) console.log("  + ", l.slice(0, 220));
  break; // um exemplo chega para olhar
}
