// O NOME DA PASTA NAO DERRUBA A FONTE, E A IDENTIDADE NAO MUDA — FECHAR-ONDA2-B (D60 c).
//
//     node provas/nome_da_pasta_windows.mjs
//
// Sem rede: le `provas/nome_da_pasta_contratos_em_risco.json` (as 42 linhas em risco
// do robo vivo, 37 pelo LINK_PATTERN com `\?` + 5 com endereco literal proibido),
// calcula o DOCUMENT_ID com o motor de verdade (`contratoGenerico` +
// `identidadeDoContrato`) e cria as pastas a serio numa pasta temporaria.
//
//   N1  a regra de sempre (`: / \` -> `_`) reproduz o ENOENT no Windows (so no Windows)
//   N2  cada DOCUMENT_ID em risco da um nome sem proibido, <= 255 bytes, e o mkdir PASSA
//   N3  nenhuma colisao: nomes diferentes para DOCUMENT_ID diferentes (em risco + tabela inteira
//       + pastas que ja existem + pares armadilha)
//   N4  nenhuma identidade muda: o DOCUMENT_ID continua a levar o `?`; o nome volta ao de sempre
//   N5  compatibilidade: todo o DOCUMENT_ID que ja servia da o MESMO nome; as pastas guardadas
//       em data/collection-store/italy dao o mesmo nome; pasta antiga com `?` continua a ser achada
//   N6  o caso da onda: IT-T2-050 com `?redirect=%2F`
import { mkdtempSync, rmSync, readFileSync, mkdirSync, writeFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { contratoGenerico } from "../regras/italy_contracts.mjs";
import { identidadeDoContrato } from "../regras/motor_de_rota.mjs";
import { nomeDaPasta, nomeDeSempre, nomeDeSempreServe, nomeDeSempreDe, pastaDoDocumento,
         PROIBIDOS, LIMITE_DO_NOME, LIMITE_DO_NOME_NOVO } from "../coleta/nome_da_pasta.mjs";

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), "..");
const DADOS = JSON.parse(readFileSync(join(RAIZ, "provas", "nome_da_pasta_contratos_em_risco.json"), "utf8"));
const TMP = mkdtempSync(join(tmpdir(), "nome-da-pasta-"));
const WINDOWS = process.platform === "win32";

let passou = 0, falhas = 0;
const ok = (nome, cond, porque = "") => {
  if (cond) { passou++; console.log(`  PASS ${nome}`); }
  else { falhas++; console.log(`  FAIL ${nome} ${porque}`); }
};
const bytes = (s) => Buffer.byteLength(s, "utf8");

function urlsDe(o, out = []) {
  if (Array.isArray(o)) o.forEach((v) => urlsDe(v, out));
  else if (o && typeof o === "object") Object.values(o).forEach((v) => urlsDe(v, out));
  else if (typeof o === "string" && /^https?:\/\//.test(o)) out.push(o);
  return out;
}

// ── os DOCUMENT_ID em risco, pelo motor de verdade ──────────────────────────
// Por linha: os enderecos literais da linha + variantes com `?` e com os outros
// proibidos, como a descoberta os traria (o LINK_PATTERN admite a query).
const EM_RISCO = [];
for (const linha of DADOS.FONTES) {
  const c = contratoGenerico(linha);
  const base = (linha.SONDAGEM && linha.SONDAGEM.DOCUMENTO) || linha.ACQUISITION.INDEX_URL;
  const semQuery = base.split(/[?#]/)[0].replace(/\/$/, "") + "/materia-di-prova";
  const urls = new Set([...urlsDe(linha),
    `${semQuery}?redirect=%2F`, `${semQuery}?page=2&lang=it`,
    `${semQuery}?q="grano"<duro>|*`, `${semQuery}/?id=1`]);
  for (const url of urls) {
    const ident = identidadeDoContrato(linha.SOURCE_ID, c, { url, nome: "x.html" });
    if (!ident || !ident.DOCUMENT_ID) continue;
    EM_RISCO.push({ SID: linha.SOURCE_ID, url, id: ident.DOCUMENT_ID });
  }
}
const COM_PROIBIDO = EM_RISCO.filter((x) => PROIBIDOS.test(nomeDeSempre(x.id)));
console.log(`linhas ${DADOS.FONTES.length} (37 pelo LINK_PATTERN: ${DADOS.IDS_37.length}) · ` +
            `DOCUMENT_ID calculados ${EM_RISCO.length} · com proibido ${COM_PROIBIDO.length}`);
ok("N0 as 37 do criterio estao todas no conjunto",
   DADOS.IDS_37.length === 37 && DADOS.IDS_37.every((s) => DADOS.FONTES.some((f) => f.SOURCE_ID === s)));
ok("N0 cada linha em risco da pelo menos um DOCUMENT_ID com proibido",
   DADOS.FONTES.every((f) => COM_PROIBIDO.some((x) => x.SID === f.SOURCE_ID)),
   DADOS.FONTES.filter((f) => !COM_PROIBIDO.some((x) => x.SID === f.SOURCE_ID)).map((f) => f.SOURCE_ID).join(","));

// ── N1 · a regra de sempre rebenta no Windows ──────────────────────────────
const T2050 = EM_RISCO.find((x) => x.SID === "IT-T2-050" && /\?redirect=%2F$/.test(x.url) && !/materia-di-prova/.test(x.url));
ok("N6 o caso da onda esta no conjunto (IT-T2-050, ?redirect=%2F)", !!T2050);
if (WINDOWS) {
  let erro = "";
  try { mkdirSync(join(TMP, "velha", "IT-T2-050", nomeDeSempre(T2050.id), "v1"), { recursive: true }); }
  catch (e) { erro = e.code || String(e); }
  ok("N1 a regra de sempre reproduz o ENOENT da onda", erro === "ENOENT", `deu ${erro || "sem erro"}`);
} else {
  console.log("  (N1 so no Windows: aqui o `?` e aceite)");
}

// ── N2 · todo o nome e valido e o mkdir passa ───────────────────────────────
const falhouMk = [], invalidos = [];
for (const x of EM_RISCO) {
  const nome = nomeDaPasta(x.id);
  if (PROIBIDOS.test(nome) || /[:\/\\]/.test(nome) || bytes(nome) > LIMITE_DO_NOME) invalidos.push(nome);
  const dir = pastaDoDocumento(join(TMP, "nova", x.SID), x.id);
  try {
    mkdirSync(join(dir, "2026-09-25"), { recursive: true });
    writeFileSync(join(dir, "2026-09-25", "documento.html"), "x");
  } catch (e) { falhouMk.push(`${x.SID} ${e.code}`); }
}
ok("N2 nenhum nome com proibido nem acima de 255 bytes", invalidos.length === 0, invalidos.slice(0, 3).join(" | "));
// O endereco comprido SEM proibido tambem nao cabia num nome de pasta (IT-T2-006 traz um de ~700).
const LONGO = "IT-T2-006:URL:news/-/asset_publisher/" + "segmento-lungo-".repeat(20) + "fine";
const dLongo = pastaDoDocumento(join(TMP, "nova", "IT-T2-006"), LONGO);
let erroLongo = "";
try { mkdirSync(join(dLongo, "2026-09-25"), { recursive: true }); } catch (e) { erroLongo = e.code || String(e); }
ok("N2 endereco comprido sem proibido: nome <= 255 bytes e mkdir passa",
   bytes(nomeDeSempre(LONGO)) > LIMITE_DO_NOME && bytes(nomeDaPasta(LONGO)) <= LIMITE_DO_NOME && !erroLongo, erroLongo);
ok(`N2 mkdir + escrita passam nos ${EM_RISCO.length} DOCUMENT_ID`, falhouMk.length === 0, falhouMk.slice(0, 3).join(", "));

// ── N3 · nenhuma colisao ────────────────────────────────────────────────────
const TABELA = DADOS.DOCUMENTOS_SONDADOS_DA_TABELA_INTEIRA.map((u) => {
  const m = /^https?:\/\/[^/]+\/?(.*?)\/?$/.exec(u);
  return m ? `IT-TX-000:URL:${m[1]}` : null;
}).filter(Boolean);
const guardadas = execFileSync("git", ["ls-files", "data/collection-store/italy"], { cwd: RAIZ, encoding: "utf8" })
  .split("\n").filter(Boolean).map((p) => p.split("/")).filter((p) => p.length >= 6)
  .map((p) => ({ SID: p[3], nome: p[4] }));
const ARMADILHAS = [
  "IT-T2-050:URL:a:b?c", "IT-T2-050:URL:a/b?c",           // so diferem em : vs / (o de sempre juntava)
  "IT-T2-050:URL:a?b", "IT-T2-050:URL:a%3Fb",             // o `?` contra o seu codigo literal
  "IT-T2-050:URL:a%b?", "IT-T2-050:URL:a%25b?",           // o `%` tambem se codifica
  "IT-T2-050:URL:x?" + "y".repeat(400), "IT-T2-050:URL:x?" + "y".repeat(399) + "z",   // cortados
];
const todos = new Map();
const colisoes = [];
const juntar = (sid, id) => {
  const k = `${sid}/${nomeDaPasta(id)}`;
  if (todos.has(k) && todos.get(k) !== id) colisoes.push(`${k} <- ${todos.get(k)} | ${id}`);
  todos.set(k, id);
};
for (const x of EM_RISCO) juntar(x.SID, x.id);
for (const id of TABELA) juntar("IT-TX-000", id);
for (const g of guardadas) juntar(g.SID, g.nome);
for (const id of ARMADILHAS) juntar("IT-T2-050", id);
// e o nome novo nunca cai num nome de sempre que ja serve (de qualquer conjunto)
const deSempreValidos = new Set([...EM_RISCO.map((x) => x.id), ...TABELA, ...guardadas.map((g) => g.nome)]
  .filter(nomeDeSempreServe).map(nomeDeSempre));
const invasoes = COM_PROIBIDO.filter((x) => deSempreValidos.has(nomeDaPasta(x.id)));
ok(`N3 nenhuma colisao em ${todos.size} nomes (em risco + tabela + ${guardadas.length} guardadas + armadilhas)`,
   colisoes.length === 0, colisoes.slice(0, 3).join(" ; "));
ok("N3 nenhum nome novo igual a um nome de sempre", invasoes.length === 0);
ok("N3 o par : vs / da dois nomes", nomeDaPasta(ARMADILHAS[0]) !== nomeDaPasta(ARMADILHAS[1]));
ok("N3 o nome e estavel (mesmo DOCUMENT_ID, mesmo nome)", EM_RISCO.every((x) => nomeDaPasta(x.id) === nomeDaPasta(String(x.id))));

// ── N4 · a identidade nao muda ──────────────────────────────────────────────
ok("N4 o DOCUMENT_ID da onda continua a levar o endereco inteiro com `?`",
   T2050 && T2050.id === "IT-T2-050:URL:" + T2050.url.replace(/^https?:\/\/[^/]+\//, ""), T2050 && T2050.id);
let reversiveis = 0;
const semVolta = COM_PROIBIDO.filter((x) => {
  const n = nomeDaPasta(x.id);
  // so os que nao foram cortados: cada proibido (e `%`) cresce 2 bytes ao codificar
  const codificado = bytes(nomeDeSempre(x.id)) + 2 * (nomeDeSempre(x.id).match(/[%*?"<>| -]/g) || []).length;
  if (codificado <= LIMITE_DO_NOME_NOVO - 13) reversiveis++;
  return codificado <= LIMITE_DO_NOME_NOVO - 13 && nomeDeSempreDe(n) !== nomeDeSempre(x.id);
});
ok(`N4 o percent-encoding volta ao nome de sempre (${reversiveis} nomes nao cortados)`, semVolta.length === 0 && reversiveis > 0,
   semVolta.slice(0, 2).map((x) => x.id).join(" | "));

// ── N5 · compatibilidade ────────────────────────────────────────────────────
const mudou = [...TABELA, ...EM_RISCO.map((x) => x.id)].filter(nomeDeSempreServe)
  .filter((id) => nomeDaPasta(id) !== nomeDeSempre(id));
ok("N5 todo o DOCUMENT_ID que ja servia da o MESMO nome de sempre", mudou.length === 0, mudou.slice(0, 2).join(" | "));
const guardadaMudou = guardadas.filter((g) => nomeDaPasta(g.nome) !== g.nome);
ok(`N5 as ${new Set(guardadas.map((g) => g.SID + "/" + g.nome)).size} pastas guardadas no Git continuam com o mesmo nome`,
   guardadas.length > 0 && guardadaMudou.length === 0, guardadaMudou.slice(0, 2).map((g) => g.nome).join(" | "));
const base = "data/collection-store/italy/IT-T2-050";
const antiga = `${base}/${nomeDeSempre(T2050.id)}`;
ok("N5 pasta antiga com `?` (criada num Linux) continua a ser achada",
   pastaDoDocumento(base, T2050.id, (p) => p === antiga) === antiga);
ok("N5 sem pasta antiga, vai para o nome novo",
   pastaDoDocumento(base, T2050.id, () => false) === `${base}/${nomeDaPasta(T2050.id)}`);
ok("N5 se perguntar pelo disco rebentar, vai para o nome novo",
   pastaDoDocumento(base, T2050.id, () => { throw new Error("x"); }) === `${base}/${nomeDaPasta(T2050.id)}`);

// ── N6 · o caso da onda, a serio ────────────────────────────────────────────
const d6 = pastaDoDocumento(join(TMP, "onda", "IT-T2-050"), T2050.id);
mkdirSync(join(d6, "2026-09-25"), { recursive: true });
ok("N6 IT-T2-050 cria a pasta nesta maquina", existsSync(join(d6, "2026-09-25")), d6);
console.log(`  IT-T2-050: ${T2050.id}\n        -> ${nomeDaPasta(T2050.id)}`);

rmSync(TMP, { recursive: true, force: true });
console.log(`NOME_DA_PASTA_WINDOWS · passou=${passou} FALHAS=${falhas}`);
process.exit(falhas ? 1 : 0);
