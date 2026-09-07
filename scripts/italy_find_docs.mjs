// FASE D — auxiliar: abre uma pagina e lista os links que PARECEM documento real
// (boletim, PDF, monitoramento, preco). Nao baixa nada. So mostra o caminho.
//
// Uso: node scripts/italy_find_docs.mjs <url> [palavra-extra] [palavra-extra...]

import { execFile } from "node:child_process";
import { promisify } from "node:util";
const run = promisify(execFile);
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36";

const url = process.argv[2];
const extra = process.argv.slice(3).map(s => s.toLowerCase());
const TERMOS = ["bollettin", "monitoragg", "fitosanitar", "agrometeo", "difesa", "avversit",
  "prezzi", "mercat", "quotazion", "tecnic", "deroga", "disciplinar", "report",
  "pubblicazion", "notizi", "archivio", "download", ...extra];

const { stdout } = await run("curl", ["-sSL", "--max-time", "45", "-A", UA,
  "-H", "Accept-Language: it-IT,it;q=0.9", url], { maxBuffer: 64 * 1024 * 1024, encoding: "utf8" });

const base = new URL(url);
const seen = new Map();
const re = /<a\b[^>]*href=["']([^"'#]+)["'][^>]*>([\s\S]*?)<\/a>/gi;
let m;
while ((m = re.exec(stdout))) {
  let href = m[1].trim();
  const texto = m[2].replace(/<[^>]*>/g, " ").replace(/&nbsp;/g, " ").replace(/\s+/g, " ").trim();
  let abs;
  try { abs = new URL(href, base).href; } catch { continue; }
  if (!/^https?:/.test(abs)) continue;
  const alvo = (abs + " " + texto).toLowerCase();
  const pdf = /\.pdf(\?|$)/i.test(abs);
  const dados = /\.(csv|json|xml|xlsx?|zip)(\?|$)/i.test(abs);
  const hit = TERMOS.filter(t => alvo.includes(t));
  if (!pdf && !dados && hit.length === 0) continue;
  if (seen.has(abs)) continue;
  seen.set(abs, { url: abs, texto: texto.slice(0, 110), tipo: pdf ? "PDF" : dados ? "DADOS" : "PAGINA", termos: hit });
}

const lista = [...seen.values()].sort((a, b) =>
  (b.tipo === "PDF") - (a.tipo === "PDF") || (b.tipo === "DADOS") - (a.tipo === "DADOS") || b.termos.length - a.termos.length);

console.log(`links candidatos: ${lista.length}  (de ${url})\n`);
for (const l of lista.slice(0, 40)) {
  console.log(`[${l.tipo}] ${l.texto || "(sem texto)"}\n        ${l.url}`);
}
