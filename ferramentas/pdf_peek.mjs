// Espia o texto de um PDF sem instalar nada. Serve para CONFERIR que o arquivo
// preservado e mesmo o documento que se diz, nao para virar dado estruturado.
// Uso: node ferramentas/pdf_peek.mjs <arquivo.pdf> [quantos_caracteres]
import { readFileSync } from "node:fs";
import { inflateSync } from "node:zlib";

const file = process.argv[2];
const lim = Number(process.argv[3] || 3000);
const buf = readFileSync(file);
const s = buf.toString("latin1");
let texto = "";
const re = /stream\r?\n/g;
let m;
while ((m = re.exec(s))) {
  const ini = m.index + m[0].length;
  const fim = s.indexOf("endstream", ini);
  if (fim < 0) continue;
  try { texto += inflateSync(buf.subarray(ini, fim)).toString("latin1"); } catch { /* nao comprimido ou imagem */ }
  if (texto.length > 2_000_000) break;
}
const pedacos = [...texto.matchAll(/\(((?:\\.|[^()\\])*)\)/g)].map(x => x[1]);
const saida = pedacos.join(" ")
  .replace(/\\([()\\])/g, "$1")
  .replace(/\s+/g, " ")
  .trim();
console.log(saida.slice(0, lim));
console.log(`\n--- [${saida.length} caracteres de texto extraidos de ${file}] ---`);
