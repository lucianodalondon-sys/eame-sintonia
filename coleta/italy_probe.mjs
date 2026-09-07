// FASE C — probe de acesso das fontes italianas, do IP italiano.
//
// REGRA DE ASSIMETRIA (importante, ler antes de interpretar a saida):
//   ACCESS_OK aqui  = sinal FORTE. Se abre para curl, abre para navegador.
//   BLOCKED aqui    = sinal FRACO / INCONCLUSIVO. Muitos sites recusam curl e
//                     aceitam navegador com janela. Precisa reteste em browser.
//   Ou seja: BLOCKED_EM_CURL_ITALIANO != BLOCKED_EM_BROWSER_ITALIANO,
//   pelo mesmo motivo que a REGRA 0 diz BLOCKED_EM_DATACENTER != BROWSER_ITALIANO.
//
// Nao preserva conteudo. So mede a porta. A preservacao e a FASE D, caso a caso.
//
// Uso: node coleta/italy_probe.mjs [saida.json]

import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";

const run = promisify(execFile);
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36";
const OUT = process.argv[2] || "data/samples/IT-PROBE/probe-fase-c.json";

const master = JSON.parse(readFileSync("data/samples/ITALY-SOURCE-MASTER-V1.json", "utf8"));

// agrupa por URL: uma organizacao pode ter varios SOURCE_ID na mesma porta
const byUrl = new Map();
for (const s of master.sources) {
  const u = (s.URL || "").trim();
  if (!u || u === "NÃO SEI" || !/^https?:/i.test(u)) continue;
  if (!byUrl.has(u)) byUrl.set(u, []);
  byUrl.get(u).push({ SOURCE_ID: s.SOURCE_ID, TERRITORY: s.TERRITORY });
}

function classify(code, body, err) {
  if (err) return { RESULTADO: "NETWORK_ERROR", nota: err };
  const c = Number(code);
  if (c === 0) return { RESULTADO: "NETWORK_ERROR", nota: "sem resposta HTTP" };
  if (c === 403) return { RESULTADO: "BLOCKED_PARA_CURL", nota: "403 — INCONCLUSIVO. Reteste obrigatorio em navegador italiano antes de qualquer RED." };
  if (c === 401) return { RESULTADO: "LOGIN_REQUIRED", nota: "401" };
  if (c === 404) return { RESULTADO: "ROTA_INEXISTENTE", nota: "404 nesta URL — a organizacao pode existir noutra rota" };
  if (c === 429) return { RESULTADO: "RATE_LIMITED", nota: "429 — INCONCLUSIVO" };
  if (c >= 500) return { RESULTADO: "SERVER_ERROR", nota: `${c} — ACCESS FAILURE, nao significa que a fonte nao existe` };
  if (c >= 300 && c < 400) return { RESULTADO: "REDIRECT_NAO_SEGUIDO", nota: String(c) };
  if (c === 200) {
    const b = (body || "").slice(0, 4000).toLowerCase();
    const waf = ["just a moment", "cf-browser-verification", "captcha", "attention required", "checking your browser", "incapsula", "akamai bot manager", "radware"];
    const hit = waf.find(w => b.includes(w));
    if (hit) return { RESULTADO: "WAF_CHALLENGE", nota: `200 mas a pagina e desafio anti-robo ("${hit}") — INCONCLUSIVO, reteste em navegador` };
    if ((body || "").length < 1500) return { RESULTADO: "ACCESS_OK_MAS_MAGRO", nota: `200 com apenas ${(body || "").length} bytes — pode ser casca; conferir a olho` };
    return { RESULTADO: "ACCESS_OK", nota: "200 com corpo real" };
  }
  return { RESULTADO: "NÃO SEI", nota: String(c) };
}

async function probe(url) {
  const args = ["-sSL", "--max-time", "45", "--max-redirs", "5", "-A", UA,
    "-H", "Accept-Language: it-IT,it;q=0.9,en;q=0.6",
    "-w", "\n__M__%{http_code}|%{content_type}|%{size_download}|%{url_effective}|%{remote_ip}|%{time_total}", url];
  try {
    const { stdout } = await run("curl", args, { maxBuffer: 64 * 1024 * 1024, encoding: "utf8" });
    const i = stdout.lastIndexOf("\n__M__");
    const body = i < 0 ? stdout : stdout.slice(0, i);
    const meta = (i < 0 ? "" : stdout.slice(i + 6)).split("|");
    return {
      HTTP_STATUS: Number(meta[0] || 0),
      MIME: meta[1] || null,
      BYTES: Number(meta[2] || 0),
      URL_EFETIVA: meta[3] || url,
      SERVER_IP: meta[4] || null,
      TEMPO_S: Number(meta[5] || 0),
      SHA256_DA_RESPOSTA: createHash("sha256").update(body).digest("hex"),
      ...classify(meta[0], body, null),
      _body: body
    };
  } catch (e) {
    return { HTTP_STATUS: 0, ...classify(0, "", (e.stderr || e.message || "").trim().slice(0, 300)) };
  }
}

function pistas(body) {
  if (!body) return [];
  const b = body.toLowerCase();
  const p = [];
  if (/<link[^>]+type="application\/rss\+xml"/.test(b)) p.push("RSS declarado no <head>");
  if (b.includes(".csv")) p.push("link .csv na pagina");
  if (b.includes(".xlsx") || b.includes(".xls\"")) p.push("link de planilha");
  if (/href="[^"]*\.pdf/.test(b)) p.push("link .pdf na pagina");
  if (b.includes("sdmx")) p.push("SDMX citado");
  if (b.includes("bollettin")) p.push("a palavra 'bollettin' aparece");
  if (b.includes("monitoragg")) p.push("a palavra 'monitoragg' aparece");
  if (b.includes("area riservata") || b.includes("accedi")) p.push("area reservada / login citado");
  if (b.includes("wp-content")) p.push("WordPress");
  return p;
}

const urls = [...byUrl.keys()];
const results = [];
for (const u of urls) {
  const r = await probe(u);
  const body = r._body; delete r._body;
  results.push({ URL: u, SOURCE_IDS: byUrl.get(u), ...r, PISTAS: pistas(body) });
  console.log(String(r.RESULTADO).padEnd(22), String(r.HTTP_STATUS).padEnd(4), String(r.BYTES).padStart(8), u);
}

const resumo = {};
results.forEach(r => { resumo[r.RESULTADO] = (resumo[r.RESULTADO] || 0) + 1; });

const doc = {
  FASE: "C — probe de acesso",
  CAPTURED_AT_UTC: new Date().toISOString(),
  METODO: "curl HTTP GET com User-Agent de navegador, seguindo redirect, do IP de saida italiano",
  EGRESS: "205.147.30.20 · Milano · IT · AS208172 Proton AG (VPN comercial, NAO ISP residencial)",
  REGRA_DE_ASSIMETRIA: {
    ACCESS_OK: "sinal FORTE — se abre para curl, abre para navegador",
    BLOCKED_OU_WAF: "sinal FRACO — INCONCLUSIVO. Exige reteste em navegador italiano antes de qualquer RED",
    lembrete: "403/503 desta execucao = ACCESS FAILURE, nao = SOURCE DOES NOT EXIST"
  },
  AVISO: "este probe NAO preserva amostra. Ele so mede a porta. Nenhum veredito GREEN pode sair daqui sozinho.",
  RESUMO: resumo,
  TOTAL_URLS: results.length,
  RESULTADOS: results
};
writeFileSync(OUT, JSON.stringify(doc, null, 1));
console.log("\n", JSON.stringify(resumo, null, 1), "\n->", OUT);
