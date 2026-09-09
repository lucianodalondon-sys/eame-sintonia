// Tira o texto de um HTML (arquivo local ou URL), sem script/style/nav.
// Uso: node ferramentas/html_text.mjs <arquivo|url> [quantos_caracteres] [pular_caracteres]
import { readFileSync, existsSync } from "node:fs";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
const run = promisify(execFile);
const alvo = process.argv[2];
const lim = Number(process.argv[3] || 3000);
const pula = Number(process.argv[4] || 0);
let html;
if (existsSync(alvo)) html = readFileSync(alvo, "utf8");
else {
  const { stdout } = await run("curl", ["-sSL", "--max-time", "60",
    "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "-H", "Accept-Language: it-IT,it;q=0.9", alvo], { maxBuffer: 64 * 1024 * 1024, encoding: "utf8" });
  html = stdout;
}
const txt = html
  .replace(/<script[\s\S]*?<\/script>/gi, " ")
  .replace(/<style[\s\S]*?<\/style>/gi, " ")
  .replace(/<!--[\s\S]*?-->/g, " ")
  .replace(/<(br|\/p|\/div|\/li|\/tr|\/h[1-6])\s*>/gi, "\n")
  .replace(/<[^>]*>/g, " ")
  .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&#39;/g, "'")
  .replace(/&egrave;/g, "è").replace(/&agrave;/g, "à").replace(/&ugrave;/g, "ù")
  .replace(/&ograve;/g, "ò").replace(/&igrave;/g, "ì").replace(/&rsquo;/g, "'")
  .replace(/[ \t]+/g, " ")
  .split("\n").map(l => l.trim()).filter(Boolean).join("\n");
console.log(txt.slice(pula, pula + lim));
console.log(`\n--- [${txt.length} caracteres de texto em ${alvo}] ---`);
