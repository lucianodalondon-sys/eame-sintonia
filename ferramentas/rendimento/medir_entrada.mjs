// REND · RENDIMENTO POR FONTE, MEDIDO SO PELA PAGINA DE ENTRADA.
//
// Pergunta: «se a coleta corresse agora, esta fonte teria materia NOVA para
// trazer?». Responde-se com UM pedido a pagina de entrada (mais o robots.txt),
// sem abrir nenhuma materia, e com as mesmas pecas que o coletor usa:
//
//   alvosDoContrato()      -> que enderecos o indice anuncia (motor_de_rota)
//   memoriaDosDetalhes()   -> o que o livro do coletor ja tem (incrementalidade)
//   decidirSobreDetalhe()  -> iria buscar ou saltava
//   lerRobots/robotsPermite -> a cortesia da A5 (robots, pausa 1 s, teto 5/site)
//
// NAO escreve em livro nenhum, NAO grava bytes no armazem, NAO toca na Sala.
// Os indices ficam em --pasta (fora do Git) so para quem quiser conferir.
//
// Uso:
//   node ferramentas/rendimento/medir_entrada.mjs --arvore <arvore do bot>
//        --ledger <observations.ndjson do bot> --sala C:/rend/sala.json
//        --curadores a.json,b.json --ids IT-..,IT-.. --saida X.json --pasta C:/rend/indices
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";

const run = promisify(execFile);
const arg = (n, d = null) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const ARVORE = arg("--arvore");
const importar = p => import(pathToFileURL(`${ARVORE}/${p}`).href);
const { CONTRACTS } = await importar("regras/italy_contracts.mjs");
const { alvosDoContrato } = await importar("regras/motor_de_rota.mjs");
const { memoriaDosDetalhes, decidirSobreDetalhe, recolheitaDoContrato } = await importar("regras/incrementalidade.mjs");
const { lerRobots, grupoQueVale, robotsPermite, siteDe, CORTESIA_PADRAO } = await importar("coleta/italy_pilot_collect.mjs");

const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36";
const TETO = CORTESIA_PADRAO.TETO_POR_HOST, PAUSA_MS = CORTESIA_PADRAO.PAUSA_S * 1000;
// Numa corrida do coletor: robots + indice + ate 3 materias = teto 5 por site.
const MATERIAS_POR_CORRIDA = TETO - 2;

const IDS = arg("--ids").split(",").filter(Boolean);
const PASTA = arg("--pasta", "C:/rend/indices");
mkdirSync(PASTA, { recursive: true });

// ── contratos: o do coletor primeiro; se nao houver, o do curador ─────────
const curadores = (arg("--curadores", "") || "").split(",").filter(Boolean).map(p => {
  const d = JSON.parse(readFileSync(p, "utf8"));
  return { p, fontes: new Map((d.FONTES || []).map(f => [f.SOURCE_ID, f])) };
});
function contratoDe(id) {
  if (CONTRACTS[id]?.ACQUISITION) return { c: CONTRACTS[id], ORIGEM: "COLETOR" };
  // Fonte do coletor servida por `case` (sem ACQUISITION): mede-se com a mesma
  // regra escrita como contrato (ex.: boletins IT-T3-002/010). Continua do coletor.
  for (const k of curadores) if (k.fontes.get(id)?.ACQUISITION)
    return { c: { ...(CONTRACTS[id] || {}), ...k.fontes.get(id) }, ORIGEM: CONTRACTS[id] ? `COLETOR_CASE:${k.p}` : `SO_CURADOR:${k.p}` };
  if (CONTRACTS[id]) return { c: CONTRACTS[id], ORIGEM: "COLETOR" };
  return { c: null, ORIGEM: "NENHUM" };
}

// ── memoria do coletor (livro) e do acervo (Sala) ───────────────────────────
const obs = readFileSync(arg("--ledger"), "utf8").split("\n").filter(Boolean).map(l => JSON.parse(l));
const memoria = memoriaDosDetalhes(obs);
const sala = JSON.parse(readFileSync(arg("--sala"), "utf8"));
const urlsAcervo = new Set(Object.values(sala.POR_FONTE).flatMap(f => f.URLS));
const norm = u => String(u).replace(/^https?:\/\/(www\.)?/i, "").replace(/\/+$/, "");
const urlsAcervoNorm = new Set([...urlsAcervo].map(norm));

// ── transporte com cortesia (a mesma lei do baixar() da A5) ────────────────
const porSite = new Map(), ultimo = new Map(), robots = new Map();
let PEDIDOS = 0;
const dormir = ms => new Promise(r => setTimeout(r, ms));
async function ida(url) {
  const site = siteDe(new URL(url).hostname);
  const u = ultimo.get(site);
  if (u !== undefined && Date.now() - u < PAUSA_MS) await dormir(PAUSA_MS - (Date.now() - u));
  porSite.set(site, (porSite.get(site) || 0) + 1);
  PEDIDOS++;
  try {
    const { stdout } = await run("curl", ["-sS", "--max-time", "60", "-A", UA,
      "-H", "Accept-Language: it-IT,it;q=0.9", "-o", "-",
      "-w", "\\n__S__%{http_code}\\t%{content_type}\\t%{redirect_url}", url],
      { maxBuffer: 64e6, encoding: "buffer" });
    const s = stdout.toString("latin1"), k = s.lastIndexOf("\n__S__");
    const r = (k < 0 ? "" : s.slice(k + 6)).split("\t");
    return { buf: stdout.subarray(0, k < 0 ? stdout.length : k), status: Number(r[0]), destino: (r[2] || "").trim() || null };
  } catch (e) {
    return { erro: (e.stderr?.toString() || e.message || "").slice(0, 160), status: 0 };
  } finally { ultimo.set(site, Date.now()); }
}
const tetoCheio = url => (porSite.get(siteDe(new URL(url).hostname)) || 0) >= TETO;
async function robotsDe(origem) {
  if (robots.has(origem)) return robots.get(origem);
  let alvo = `${origem}/robots.txt`, rb;
  for (let salto = 0; salto < 4; salto++) {
    if (tetoCheio(alvo)) return { recusado: "TETO_POR_HOST" };
    const r = await ida(alvo);
    if (r.erro) { rb = { estado: "INDISPONIVEL", porque: r.erro }; break; }
    if (r.status >= 300 && r.status < 400 && r.destino) { alvo = r.destino; continue; }
    if (r.status === 404 || r.status === 410) { rb = { estado: "AUSENTE" }; break; }
    if (r.status !== 200) { rb = { estado: "ILEGIVEL", porque: `HTTP ${r.status}` }; break; }
    const txt = r.buf.toString("utf8");
    if (/^\s*</.test(txt)) { rb = { estado: "ILEGIVEL", porque: "robots.txt em HTML" }; break; }
    const grupos = lerRobots(txt);
    rb = { estado: "LIDO", grupos, crawlDelay: grupoQueVale(grupos)?.crawlDelay ?? null }; break;
  }
  rb = rb || { estado: "ILEGIVEL", porque: "saltos demais no robots" };
  if (rb.estado !== "INDISPONIVEL") robots.set(origem, rb);
  return rb;
}
async function baixarComLicenca(url) {
  let atual = url;
  for (let salto = 0; salto <= 5; salto++) {
    const u = new URL(atual);
    if (tetoCheio(atual)) return { recusado: "TETO_POR_HOST" };
    const rb = await robotsDe(u.origin);
    if (rb.recusado) return rb;
    if (rb.estado === "INDISPONIVEL" || rb.estado === "ILEGIVEL") return { recusado: `ROBOTS_${rb.estado}`, porque: rb.porque };
    if (rb.estado === "LIDO" && !robotsPermite(rb.grupos, u.pathname + u.search)) return { recusado: "ROBOTS_PROIBE" };
    if (tetoCheio(atual)) return { recusado: "TETO_POR_HOST" };
    const r = await ida(atual);
    if (r.status >= 300 && r.status < 400 && r.destino) { atual = r.destino; continue; }
    return { ...r, URL_FINAL: atual };
  }
  return { erro: "redireccionamentos demais" };
}

// ── a medicao, fonte a fonte ────────────────────────────────────────────────
const agora = new Date().toISOString();
const linhas = [];
for (const id of IDS) {
  const { c, ORIGEM } = contratoDe(id);
  const L = { SOURCE_ID: id, UNIVERSO: id.split("-")[1], CONTRATO: ORIGEM };
  linhas.push(L);
  const aq = c?.ACQUISITION;
  if (!aq) { L.ESTADO = "SEM_ROTA_DECLARADA"; continue; }
  L.ESTRATEGIA = aq.STRATEGY; L.INDEX_URL = aq.INDEX_URL || aq.URL || null;
  L.MAX_TARGETS = Number.isInteger(aq.MAX_TARGETS) ? aq.MAX_TARGETS : null;
  let rec; try { rec = recolheitaDoContrato(id, c); } catch { rec = { DETAIL_CONTENT: "INVALIDO" }; }
  L.RECOLLECTION = rec.DETAIL_CONTENT + (rec.TTL_SECONDS ? `/${rec.TTL_SECONDS / 3600}h` : "");
  if (aq.STRATEGY !== "HTML_LINK_DISCOVERY") { L.ESTADO = "SEM_INDICE_PARA_MEDIR"; continue; }

  // o indice, uma vez; o motor recebe-o por injeccao e nao pode pedir mais nada
  const idx = await baixarComLicenca(aq.INDEX_URL);
  L.PEDIDO_EM = new Date().toISOString();
  if (idx.recusado) { L.ESTADO = `ADIADA_POR_CORTESIA:${idx.recusado}`; continue; }
  if (idx.erro || idx.status !== 200) { L.ESTADO = `INDICE_FALHOU:${idx.erro || "HTTP " + idx.status}`; continue; }
  L.INDEX_BYTES = idx.buf.length;
  L.INDEX_SHA256 = createHash("sha256").update(idx.buf).digest("hex");
  writeFileSync(`${PASTA}/${id}.html`, idx.buf);
  let chamadas = 0;
  const semTecto = { ...c, ACQUISITION: { ...aq, MAX_TARGETS: undefined } };
  const todos = await alvosDoContrato(id, semTecto, {
    buscar: async () => (chamadas++ === 0 ? { status: 200, buf: idx.buf } : { erro: "REND: so a entrada" }) });
  if (todos.erro) { L.ESTADO = /EMPTY_LIST/.test(todos.erro) ? "INDICE_SEM_ALVO" : `MOTOR:${todos.erro.slice(0, 80)}`; L.ANUNCIADAS = 0; continue; }
  const janela = L.MAX_TARGETS ? todos.slice(0, L.MAX_TARGETS) : todos;
  const decide = u => decidirSobreDetalhe(u, { memoria, sourceId: id, contrato: c, agora });
  const novaColetor = t => decide(t.url).DECISAO === "FETCH";
  const novaAcervo = t => novaColetor(t) && !urlsAcervo.has(t.url) && !urlsAcervoNorm.has(norm(t.url));
  L.ANUNCIADAS = todos.length;
  L.NOVAS_PARA_O_COLETOR = todos.filter(novaColetor).length;
  L.NOVAS_PARA_O_ACERVO = todos.filter(novaAcervo).length;
  L.NA_JANELA_DO_CONTRATO = janela.length;
  L.NOVAS_NA_JANELA = janela.filter(novaColetor).length;
  L.REVISITAS_NA_JANELA = janela.filter(t => { const d = decide(t.url); return d.DECISAO !== "FETCH" && d.DECISAO !== "SKIP_KNOWN"; }).length;
  // o que UMA corrida traria de facto: janela do contrato, e no maximo 3 materias por site
  L.UMA_CORRIDA_TRARIA = Math.min(L.NOVAS_NA_JANELA, MATERIAS_POR_CORRIDA);
  L.EXEMPLOS_NOVAS = todos.filter(novaAcervo).slice(0, 3).map(t => t.url);
  L.ESTADO = "MEDIDA";
}

const d = { DATASET: "REND-ENTRADA-V1", MEDIDO_EM: agora, ARVORE, PEDIDOS_HTTP: PEDIDOS,
  PEDIDOS_POR_SITE: Object.fromEntries(porSite), TETO_POR_SITE: TETO, PAUSA_S: PAUSA_MS / 1000,
  MEMORIA_DO_COLETOR: { OBSERVACOES: obs.length, ENDERECOS: memoria.size },
  ACERVO_URLS: urlsAcervo.size, LINHAS: linhas };
writeFileSync(arg("--saida"), JSON.stringify(d, null, 1) + "\n");
for (const l of linhas) console.log(l.SOURCE_ID.padEnd(11), String(l.ESTADO).slice(0, 40).padEnd(40),
  `anuncia ${l.ANUNCIADAS ?? "-"} · novas ${l.NOVAS_PARA_O_COLETOR ?? "-"}/${l.NOVAS_PARA_O_ACERVO ?? "-"} · janela ${l.NOVAS_NA_JANELA ?? "-"}/${l.NA_JANELA_DO_CONTRATO ?? "-"} · corrida ${l.UMA_CORRIDA_TRARIA ?? "-"}`);
console.log("PEDIDOS", PEDIDOS, JSON.stringify(d.PEDIDOS_POR_SITE));
