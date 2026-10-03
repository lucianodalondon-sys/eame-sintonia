// QUE TRECHOS AINDA DIFEREM, DEPOIS DA NORMALIZACAO DE HOJE — e quantos.
//
// Serve para que cada regra nova de `TRECHOS_VOLATEIS` nasca de uma contagem
// e nao de um palpite. Alargar a lista ate o vermelho desaparecer e apagar o
// termometro; a lista so cresce com a familia MEDIDA e OLHADA.
//
// Uso: node medidas/recollection_familias.mjs

import { readFileSync, existsSync } from "node:fs";
import { lerObservacoes } from "./recollection_censo.mjs";
import { textoNormalizado } from "../regras/normalizacao_de_conteudo.mjs";

// Uma passagem so, a do proprio normalizador. Repetir o ciclo aqui daria uma
// medicao que envelhece calada quando a lista de trechos mudar — e foi
// exactamente uma lista desactualizada que esta missao veio apanhar.
const normalizado = (buf) => textoNormalizado(buf).TEXTO;

// Famílias candidatas: um nome e um teste sobre a LINHA que difere.
const FAMILIAS = [
  ["WPDM_CLIENT_ID", (l) => /wpdm_js\s*=|"client_id"\s*:/.test(l)],
  ["WORDFENCE_HID", (l) => /wordfence_lh=1&hid=/.test(l)],
  ["DRUPAL_THEME_TOKEN", (l) => /"theme_token"\s*:/.test(l)],
  ["DRUPAL_VIEW_DOM_ID", (l) => /view-dom-id-[0-9a-f]{8,}/.test(l)],
  ["DRUPAL_FORM_BUILD_ID", (l) => /name="form_build_id"/.test(l)],
  ["ENTIDADES_DE_EMAIL", (l) => /(&#\d{2,3};){2,}/.test(l)],
];

const obs = lerObservacoes().filter((o) => o.RAW_PATH && existsSync(o.RAW_PATH));
const porUrl = new Map();
for (const o of obs) {
  if (!porUrl.has(o.SOURCE_URL)) porUrl.set(o.SOURCE_URL, []);
  porUrl.get(o.SOURCE_URL).push(o);
}

const conta = {}, porFonteFam = {}, semFamilia = [];
let paresOlhados = 0, paresIguais = 0;

for (const [url, l] of porUrl) {
  l.sort((a, b) => String(a.CAPTURED_AT).localeCompare(String(b.CAPTURED_AT)));
  const v = [...new Map(l.map((o) => [o.RAW_PATH, o])).values()];
  if (v.length < 2) continue;
  const A = normalizado(readFileSync(v[0].RAW_PATH));
  const B = normalizado(readFileSync(v[1].RAW_PATH));
  if (A === null) continue;
  paresOlhados++;
  if (A === B) { paresIguais++; continue; }
  const sid = v[0].SOURCE_ID;
  const la = A.split(/\r?\n/), lb = B.split(/\r?\n/);
  const sa = new Set(la), sb = new Set(lb);
  const difs = [...la.filter((x) => !sb.has(x) && x.trim()), ...lb.filter((x) => !sa.has(x) && x.trim())];
  for (const linha of difs) {
    const nomes = FAMILIAS.filter(([, t]) => t(linha)).map(([n]) => n);
    if (nomes.length === 0) { if (semFamilia.length < 8) semFamilia.push([sid, url, linha.slice(0, 200)]); conta.SEM_FAMILIA = (conta.SEM_FAMILIA || 0) + 1; continue; }
    for (const n of nomes) {
      conta[n] = (conta[n] || 0) + 1;
      porFonteFam[n] = porFonteFam[n] || new Set();
      porFonteFam[n].add(sid);
    }
  }
}

console.log("PARES_HTML_OLHADOS      ", paresOlhados);
console.log("PARES_JA_IGUAIS_HOJE    ", paresIguais);
console.log("PARES_QUE_AINDA_DIFEREM ", paresOlhados - paresIguais);
console.log("");
console.log("FAMILIA                 LINHAS  FONTES");
for (const k of Object.keys(conta).sort((a, b) => conta[b] - conta[a])) {
  console.log(k.padEnd(24), String(conta[k]).padStart(6), " ", [...(porFonteFam[k] || [])].join(" "));
}
if (semFamilia.length) {
  console.log("\nLINHAS SEM FAMILIA NOMEADA (as que uma regra nova NAO explicaria):");
  for (const [sid, url, l] of semFamilia) console.log(" ", sid, url.slice(-40), "\n     ", l);
}
