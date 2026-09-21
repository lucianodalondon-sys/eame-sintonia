// AQUISICAO-DETALHE-V1 · PASSO 2 — PROVAR A LISTAGEM ANTES DE TOCAR NO CONTRATO
//
//     ROTA SUPOSTA != ROTA PROVADA.
//
// Le curadoria/CLASSIFICACAO-INDICE-104-V1.json, pega nas fontes LISTAGEM_DE_NOTICIAS
// e abre UMA vez a listagem proposta de cada uma (52 GET, um por listagem, pela
// mesma porta do canario do motor: portao de robots da casa + curl). Para cada
// uma mede:
//   · HTTP e bytes;
//   · N_PADRAO_ACTUAL  — quantos href a listagem anuncia que casam com o
//                        LINK_PATTERN que o contrato tem HOJE (ligacoesDoIndice);
//   · N_SOB_A_LISTAGEM — quantos href estao DEBAIXO do caminho da listagem
//                        (a familia 'under_example_path' que a casa ja usa);
//   · amostras dos dois.
// Nao colhe nenhum alvo, nao escreve observacao, nao toca em contrato. O que
// sai e um ficheiro de prova: curadoria/PROVA-DE-LISTAGENS-V1.json.
//
// Controlo positivo primeiro (a mesma URL do canario do lote): se o leitor
// falhar, nenhuma fonte e condenada.
//
//     node curadoria/provar_listagens.mjs            # todas as LISTAGEM
//     node curadoria/provar_listagens.mjs IT-T1-021  # so uma
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { CONTRACTS } from "../regras/italy_contracts.mjs";
import { ligacoesDoIndice } from "../regras/motor_de_rota.mjs";

const RAIZ = dirname(dirname(fileURLToPath(import.meta.url)));
// A MESMA identidade com que a Collection bate a porta (coleta/italy_pilot_collect.mjs:65).
// Medido: agronotizie devolve 403 ao UA «SintoniaScrap» e 200 a este — a prova
// tem de ser feita pela porta que a coleta vai usar, senao prova outra coisa.
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36";
const ENTRADA = join(RAIZ, "curadoria", "CLASSIFICACAO-INDICE-104-V1.json");
const SAIDA = join(RAIZ, "curadoria", "PROVA-DE-LISTAGENS-V1.json");
const CONTROLO_POSITIVO = "https://www.provincia.tn.it/";
const MAX_POR_DOMINIO = 2;

// O portao de robots e o da casa (coleta/scrap_http.py::permitido) — copiado
// do canario do motor, que nao o exporta porque corre main() ao importar.
function portaoDeRobots(url) {
  const py = [
    "import sys,os,json",
    "sys.path.insert(0,os.getcwd())",
    "import _gavetas, scrap_http as http",
    "try:",
    "    ok,motivo = http.permitido(sys.argv[1]); print(json.dumps({'PASS':bool(ok),'MOTIVO':motivo,'LIDO':True}))",
    "except Exception as e:",
    "    print(json.dumps({'PASS':False,'MOTIVO':type(e).__name__+': '+str(e)[:120],'LIDO':False}))",
  ].join("\n");
  for (const exe of [process.env.SINTONIA_PYTHON, "py", "python3", "python"].filter(Boolean)) {
    try {
      const out = execFileSync(exe, ["-c", py, url], { cwd: RAIZ, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
      const linha = out.trim().split("\n").pop();
      if (linha && linha.startsWith("{")) return JSON.parse(linha);
    } catch { /* tenta o proximo interpretador */ }
  }
  return { PASS: false, MOTIVO: "nenhum interpretador Python respondeu ao portao", LIDO: false };
}

let pedidosDeRede = 0;
function buscar(url) {
  const g = portaoDeRobots(url);
  if (!g.PASS) return { erro: g.LIDO ? `ROBOTS_GATE_FAIL: ${g.MOTIVO}` : `ROBOTS_UNREADABLE: ${g.MOTIVO}`, status: 0 };
  pedidosDeRede++;
  try {
    const stdout = execFileSync("curl",
      ["-sSL", "--max-time", "60", "-A", UA, "-o", "-", "-w", "\\n__S__%{http_code}__U__%{url_effective}", url],
      { maxBuffer: 64e6, encoding: "buffer" });
    const s = stdout.toString("latin1");
    const k = s.lastIndexOf("\n__S__");
    const cauda = k < 0 ? "" : s.slice(k + 6);
    const [status, efectiva] = cauda.split("__U__");
    return { buf: stdout.subarray(0, k < 0 ? stdout.length : k), status: Number(status || 0), efectiva: efectiva || url };
  } catch (e) {
    return { erro: `curl: ${String(e.message).slice(0, 120)}`, status: 0 };
  }
}

function semBarraFinal(u) { return u.replace(/\/+$/, ""); }
function hostDe(u) { return new URL(u).hostname.replace(/^www\./, ""); }

// A familia 'under_example_path': href debaixo do caminho da listagem, mesmo
// host, sem paginacao, sem feed, sem a propria listagem.
function sobALista(html, listagem) {
  const base = semBarraFinal(listagem);
  const host = hostDe(listagem);
  const vistos = new Set(), fora = [];
  for (const m of String(html).matchAll(/href\s*=\s*["']([^"'#]+)["']/gi)) {
    let u;
    try { u = new URL(m[1].trim(), listagem).href; } catch { continue; }
    if (!/^https?:/i.test(u)) continue;
    if (vistos.has(u)) continue;
    vistos.add(u);
    if (hostDe(u) !== host) continue;
    if (/\.(css|js|png|jpe?g|gif|svg|ico|woff2?|xml|rss|pdf)(\?|#|$)/i.test(u)) continue;
    if (/\/page\/\d+\/?(\?|#|$)|[?&](page|pagina|pag|p)=\d+/i.test(u)) continue;
    if (/\/(feed|rss|atom)\/?(\?|#|$)/i.test(u)) continue;
    const n = semBarraFinal(u.split(/[?#]/)[0]);
    if (n === base) continue;
    if (!n.startsWith(base + "/")) continue;
    fora.push(u);
  }
  return fora;
}

function dormir(ms) { return new Promise((r) => setTimeout(r, ms)); }

async function main() {
  const so = process.argv[2] || null;
  const classif = JSON.parse(readFileSync(ENTRADA, "utf8"));
  const fontes = classif.FONTES.filter((f) => f.CLASSIFICACAO === "LISTAGEM_DE_NOTICIAS" && (!so || f.SOURCE_ID === so));
  const saida = {
    DATASET: "PROVA-DE-LISTAGENS-V1", MISSAO: "AQUISICAO-DETALHE-V1 · PASSO 2",
    LEI: [
      "Um GET por listagem proposta; maximo 2 por dominio; so as LISTAGEM_DE_NOTICIAS de CLASSIFICACAO-INDICE-104-V1.",
      "Nao colhe alvos, nao escreve observacao, nao toca em contrato. E prova de rota, nao coleta.",
      "Controlo positivo primeiro: se o leitor falha, nenhuma fonte e condenada.",
      "LISTAGEM_PROVADA = HTTP 200 e mais de um item sob a listagem OU mais de um item pelo padrao actual.",
    ],
    CORRIDO_EM: new Date().toISOString(), EGRESS: null, CONTROLO_POSITIVO: null,
    PEDIDOS_DE_REDE: 0, PAID_USD: 0, FONTES_TENTADAS: 0, LISTAGEM_PROVADA: 0, LISTAGEM_NAO_PROVADA: 0,
    RESULTADOS: [],
  };
  try {
    const ip = execFileSync("curl", ["-s", "--max-time", "15", "https://ipinfo.io/json"], { encoding: "utf8" });
    const j = JSON.parse(ip); saida.EGRESS = { IP: j.ip, COUNTRY: j.country, CITY: j.city, ORG: j.org };
  } catch { saida.EGRESS = { IP: "NAO SEI", COUNTRY: "NAO SEI" }; }

  const cp = buscar(CONTROLO_POSITIVO);
  saida.CONTROLO_POSITIVO = { URL: CONTROLO_POSITIVO, HTTP: cp.status, BYTES: cp.buf ? cp.buf.length : 0, OK: cp.status === 200 && cp.buf && cp.buf.length > 1000, ERRO: cp.erro || null };
  if (!saida.CONTROLO_POSITIVO.OK) {
    saida.VEREDITO = "LEITOR_FALHOU — nenhuma fonte e condenada; nada foi medido";
    writeFileSync(SAIDA, JSON.stringify(saida, null, 1) + "\n");
    console.log(JSON.stringify(saida.CONTROLO_POSITIVO));
    return 2;
  }

  const porDominio = new Map();
  for (const f of fontes) {
    const listagem = f.LISTAGEM_PROPOSTA;
    const c = CONTRACTS[f.SOURCE_ID];
    const aq = c && c.ACQUISITION;
    const r = { SOURCE_ID: f.SOURCE_ID, NAME: f.NAME, CRITERIO: f.CRITERIO, LISTAGEM_PROPOSTA: listagem, LISTAGEM_ESTADO_ANTES: f.LISTAGEM_ESTADO,
                INDEX_URL_ACTUAL: aq ? aq.INDEX_URL : null, HTTP: null, URL_EFECTIVA: null, BYTES: 0,
                N_PADRAO_ACTUAL: 0, AMOSTRA_PADRAO_ACTUAL: [], N_SOB_A_LISTAGEM: 0, AMOSTRA_SOB_A_LISTAGEM: [],
                LISTAGEM_PROVADA: false, PORQUE: "" };
    saida.RESULTADOS.push(r);
    if (!listagem || !aq) { r.PORQUE = "sem listagem proposta ou sem contrato executavel"; continue; }
    const host = hostDe(listagem);
    const n = porDominio.get(host) || 0;
    if (n >= MAX_POR_DOMINIO) { r.PORQUE = `limite de ${MAX_POR_DOMINIO} pedidos por dominio atingido`; continue; }
    porDominio.set(host, n + 1);
    saida.FONTES_TENTADAS++;
    const g = buscar(listagem);
    if (g.erro || g.status !== 200) {
      r.HTTP = g.status; r.PORQUE = g.erro || `HTTP ${g.status}`;
      await dormir(800);
      continue;
    }
    r.HTTP = g.status; r.URL_EFECTIVA = g.efectiva; r.BYTES = g.buf.length;
    const html = g.buf.toString("latin1");
    try {
      const actual = ligacoesDoIndice(html, { ...aq, INDEX_URL: listagem });
      r.N_PADRAO_ACTUAL = actual.length; r.AMOSTRA_PADRAO_ACTUAL = actual.slice(0, 5);
    } catch (e) { r.PORQUE += `padrao actual nao correu: ${e.message}; `; }
    const sob = sobALista(html, g.efectiva && hostDe(g.efectiva) === host ? semBarraFinal(g.efectiva.split(/[?#]/)[0]) : listagem);
    r.N_SOB_A_LISTAGEM = sob.length; r.AMOSTRA_SOB_A_LISTAGEM = sob.slice(0, 5);
    // Todos os href do mesmo host, para se poder escrever o padrao SEM voltar a
    // rede. Medido na primeira corrida: cinco amostras nao chegavam para
    // distinguir item de menu em 14 listagens, e o limite de pedidos ja estava gasto.
    const todos = new Set();
    for (const m of html.matchAll(/href\s*=\s*["']([^"'#]+)["']/gi)) {
      try { const u = new URL(m[1].trim(), listagem).href; if (/^https?:/i.test(u) && hostDe(u) === host) todos.add(u); } catch { /* href invalido */ }
    }
    r.HREFS_MESMO_HOST = [...todos];
    r.LISTAGEM_PROVADA = r.N_SOB_A_LISTAGEM > 1 || r.N_PADRAO_ACTUAL > 1;
    if (!r.LISTAGEM_PROVADA) r.PORQUE += "200 mas nenhum ou um so item visivel — listagem nao provada";
    await dormir(800);
  }
  saida.PEDIDOS_DE_REDE = pedidosDeRede; // o controlo positivo ja passou por buscar()
  saida.LISTAGEM_PROVADA = saida.RESULTADOS.filter((r) => r.LISTAGEM_PROVADA).length;
  saida.LISTAGEM_NAO_PROVADA = saida.RESULTADOS.length - saida.LISTAGEM_PROVADA;
  saida.VEREDITO = `${saida.LISTAGEM_PROVADA} provadas / ${saida.RESULTADOS.length}`;
  if (!so) writeFileSync(SAIDA, JSON.stringify(saida, null, 1) + "\n");
  for (const r of saida.RESULTADOS) {
    console.log([r.SOURCE_ID, r.HTTP, r.BYTES, "padrao=" + r.N_PADRAO_ACTUAL, "sob=" + r.N_SOB_A_LISTAGEM, r.LISTAGEM_PROVADA ? "PROVADA" : "NAO", r.PORQUE].join(" | "));
  }
  console.log(JSON.stringify({ CONTROLO_POSITIVO: saida.CONTROLO_POSITIVO.OK, EGRESS: saida.EGRESS, PEDIDOS_DE_REDE: saida.PEDIDOS_DE_REDE, VEREDITO: saida.VEREDITO }));
  return 0;
}

main().then((code) => process.exit(code));
