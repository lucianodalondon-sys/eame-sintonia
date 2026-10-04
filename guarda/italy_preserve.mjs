// FASE D — preserva uma amostra real com MIME / BYTES / SHA256, e MEDE de onde saiu.
//
// Uso:
//   node guarda/italy_preserve.mjs <SOURCE_ID> <url> [url2] [url3]
//
// Grava em data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/
//   - os arquivos crus, com o nome que a rota da
//   - MANIFEST.json com os campos exigidos pela REGRA 6
//
// O manifesto sai com os campos de julgamento (WHAT_IT_PROVES etc.) marcados
// PREENCHER_A_MAO de proposito: maquina nao decide o que uma evidencia prova.

import { execFile, execFileSync } from "node:child_process";
import { promisify } from "node:util";
import { mkdirSync, writeFileSync, readFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { basename } from "node:path";

const run = promisify(execFile);

// ── A PROCEDENCIA DE SAIDA E MEDIDA, NUNCA ESCRITA A MAO ────────────────────
// Ate esta missao, tres linhas deste manifesto eram LITERAIS no codigo: toda
// captura saia a declarar «Milano, Lombardia, IT — Proton AG», mesmo quando
// corria de outro pais. Medido na prova de fogo da Collection: a corrida saiu
// por US e o manifesto continuou a jurar Italia.
//
//     ORIGEM DECLARADA != ORIGEM MEDIDA. SEM MEDICAO, NAO SEI.
//
// ⚠️ E O MEDIDOR NAO NASCE AQUI. `superficie/rede.py` ja e o dono desta
// pergunta nesta casa — foi tirado de dentro de uma rota de aquisicao
// exactamente para poder ser perguntado antes dela. Escrever um segundo
// medidor em JavaScript daria dois donos ao mesmo facto, livres para divergir
// no dia em que um deles mudasse de servico.
//
//     UMA PERGUNTA, UM DONO — MESMO QUANDO ATRAVESSA DUAS LINGUAGENS.
//
// E ele devolve o PAIS e nao o IP, de proposito: a pergunta era o pais, e
// guardar mais do que a pergunta e guardar o que ninguem pediu.
function egressoMedido() {
  try {
    const out = execFileSync("python3", ["superficie/rede.py", "--egresso"],
                             { encoding: "utf8", timeout: 30000 });
    const d = JSON.parse(out);
    if (!d || typeof d.EGRESS_COUNTRY_CODE !== "string") return null;
    return d;
  } catch { return null; }
}

const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36";

const [sourceId, ...urls] = process.argv.slice(2);
if (!sourceId || urls.length === 0) {
  console.error("uso: node guarda/italy_preserve.mjs <SOURCE_ID> <url> [url2] ...");
  process.exit(2);
}
const dir = `data/samples/IT-SOURCE-SAMPLES/${sourceId}`;
mkdirSync(dir, { recursive: true });

const files = [];
for (const url of urls) {
  const nome = basename(new URL(url).pathname) || "index.html";
  const dest = `${dir}/${nome}`;
  const { stdout } = await run("curl", ["-sSL", "--max-time", "90", "-A", UA,
    "-H", "Accept-Language: it-IT,it;q=0.9",
    "-D", `${dir}/${nome}.headers.txt`,
    "-o", dest,
    "-w", "%{http_code}|%{content_type}|%{size_download}|%{url_effective}|%{remote_ip}", url],
    { maxBuffer: 16 * 1024 * 1024, encoding: "utf8" });
  const [code, mime, bytes, eff, ip] = stdout.split("|");
  const buf = readFileSync(dest);
  const sha = createHash("sha256").update(buf).digest("hex");

  // o arquivo mente? conferir a assinatura real dos primeiros bytes
  const head = buf.slice(0, 5).toString("latin1");
  let real = "DESCONHECIDO";
  if (head.startsWith("%PDF")) real = "PDF de verdade";
  else if (/^\s*[<]/.test(buf.slice(0, 200).toString("latin1"))) real = "HTML/XML";
  else if (head.startsWith("PK")) real = "ZIP/XLSX/DOCX";
  else if (/^\s*[[{]/.test(buf.slice(0, 50).toString("latin1"))) real = "JSON";

  const mentiu = /\.pdf$/i.test(nome) && real !== "PDF de verdade";
  files.push({
    RAW_FILE: nome, SOURCE_URL: url, URL_EFETIVA: eff,
    HTTP_STATUS: Number(code), MIME: mime, BYTES: Number(bytes), SHA256: sha,
    ASSINATURA_REAL_DOS_BYTES: real,
    ALERTA: mentiu ? "A EXTENSAO MENTE: termina em .pdf mas os bytes nao sao PDF. NAO tratar como documento preservado." : null,
    SERVER_IP: ip
  });
  console.log(`${code} ${String(bytes).padStart(8)} ${real.padEnd(16)} ${nome}`);
  if (mentiu) console.log("   ^^ ALERTA: extensao .pdf mas bytes nao sao PDF");
}

const EGRESSO = egressoMedido();
const manifestPath = `${dir}/MANIFEST.json`;
const doc = {
  MANIFEST_VERSION: "1",
  SOURCE_ID: sourceId,
  OWNER_ID: "PREENCHER_A_MAO",
  CAPTURE: {
    CAPTURED_AT_UTC: new Date().toISOString(),
    METODO: "curl HTTP GET com User-Agent de navegador. O pais de saida NAO se assume: vai medido em EGRESS_COUNTRY_CODE.",
    EGRESS_COUNTRY_CODE: EGRESSO ? EGRESSO.EGRESS_COUNTRY_CODE : "UNKNOWN",
    EGRESS_MEDIDO_POR: EGRESSO ? EGRESSO.CHECKER : "superficie/rede.py --egresso",
    EGRESS_PORQUE: EGRESSO ? EGRESSO.PORQUE
                           : "a medicao de saida falhou nesta captura, e ausencia de medicao nao autoriza declarar uma origem",
    EGRESS_O_QUE_NAO_PROVA: "VPN_LOCATION != SOURCE_LOCATION e VPN_LOCATION != FACT_LOCATION. Isto e o ambiente de rede da execucao, nunca a geografia do dado.",
    AUTH_USED: "NENHUMA. Nao se tentou contornar autenticacao."
  },
  FILES: files,
  SOURCE_DATE: "PREENCHER_A_MAO",
  ORIGINAL_LANGUAGE: "it",
  ORIGINAL_TITLE: "PREENCHER_A_MAO",
  SOURCE_LOCATION: "PREENCHER_A_MAO — onde fica quem publica",
  FACT_LOCATION: "PREENCHER_A_MAO — onde acontece o fato. PODE SER DIFERENTE do de cima.",
  EVIDENCE_CLASS: "PREENCHER_A_MAO",
  CROP: "PREENCHER_A_MAO", ISSUE: "PREENCHER_A_MAO", TOPICS: "PREENCHER_A_MAO",
  WHAT_IT_PROVES: "PREENCHER_A_MAO",
  WHAT_IT_DOES_NOT_PROVE: "PREENCHER_A_MAO",
  RAW_EVIDENCE_STATE: files.every(f => f.HTTP_STATUS === 200 && f.BYTES > 0 && !f.ALERTA) ? "PRESERVED" : "NOT_PRESERVED",
  UPDATE_FREQUENCY: "PREENCHER_A_MAO — nunca inferir de uma unica data",
  AUTOMATION_FEASIBILITY: "PREENCHER_A_MAO",
  VERDICT: "PREENCHER_A_MAO"
};
if (existsSync(manifestPath)) doc._aviso = "manifesto anterior foi sobrescrito nesta captura";
writeFileSync(manifestPath, JSON.stringify(doc, null, 1));
console.log("->", manifestPath);
