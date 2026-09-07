// Espia o texto de uma planilha ODS/XLSX sem instalar nada.
// Serve para CONFERIR que o arquivo preservado e o documento que se diz.
// Uso: node scripts/ods_peek.mjs <arquivo> [quantas_celulas]
import { readFileSync } from "node:fs";
import { inflateRawSync } from "node:zlib";

const file = process.argv[2];
const lim = Number(process.argv[3] || 80);
const b = readFileSync(file);

// varre o ZIP pelos cabecalhos locais (assinatura PK\x03\x04)
const alvos = ["content.xml", "xl/sharedStrings.xml"];
let achado = null, nome = null;
for (let i = 0; i + 30 < b.length; i++) {
  if (b[i] !== 0x50 || b[i + 1] !== 0x4b || b[i + 2] !== 0x03 || b[i + 3] !== 0x04) continue;
  const method = b.readUInt16LE(i + 8);
  const csize = b.readUInt32LE(i + 18);
  const nlen = b.readUInt16LE(i + 26);
  const elen = b.readUInt16LE(i + 28);
  const name = b.subarray(i + 30, i + 30 + nlen).toString("utf8");
  if (!alvos.includes(name)) continue;
  const start = i + 30 + nlen + elen;
  const raw = b.subarray(start, start + csize);
  try { achado = method === 8 ? inflateRawSync(raw) : raw; nome = name; } catch { }
  if (achado) break;
}
if (!achado) { console.log("nao consegui abrir o conteudo da planilha"); process.exit(0); }
const x = achado.toString("utf8");
const cel = [...x.matchAll(/<text:p[^>]*>([\s\S]{0,120}?)<\/text:p>/g)].map(m => m[1].replace(/<[^>]*>/g, "").trim()).filter(Boolean);
const linhas = (x.match(/<table:table-row/g) || []).length;
console.log(`parte lida: ${nome} · linhas de tabela: ${linhas} · celulas com texto: ${cel.length}\n`);
console.log(cel.slice(0, lim).join(" | "));
