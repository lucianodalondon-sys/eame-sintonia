// A CORTESIA ADAPTATIVA — o gemeo Node de `coleta/cortesia_adaptativa.py` (D124, 27/09/2026).
//
// O MESMO livro (SINTONIA_CORTESIA_LIVRO, ou o nome antigo SINTONIA_TETO_24H), a MESMA politica
// (`regras/POLITICA-CORTESIA-ADAPTATIVA.json`), o MESMO trinco (o directorio `<livro>.trinco`) e a MESMA
// dobra dos eventos (`dobrarEventos`, linha a linha a de `dobrar_eventos`). Python e Node excluem-se pelo
// trinco e leem o mesmo estado; `tests/test_cortesia_adaptativa.py` prova a paridade.
//
// Diferenca UNICA, de proposito: aqui a entrada e o DOMINIO REGISTAVEL ja calculado por quem chama
// (`coleta/italy_pilot_collect.mjs::dominioRegistavel`), para nao haver uma quarta lista de sufixos.
// `orcamentoDe` aplica a D41 (googlevideo/ytimg pagam de youtube).
//
//     SEM LIVRO NAO HA CONTADOR (FAIL). LIVRO ILEGIVEL NAO E LIVRO VAZIO (UNKNOWN). SINAL MEDIDO, NUNCA ADIVINHADO.
import { readFileSync, appendFileSync, mkdirSync, rmdirSync, existsSync, writeFileSync, renameSync, openSync, readSync, closeSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), "..");
export const POLITICA_F = join(RAIZ, "regras", "POLITICA-CORTESIA-ADAPTATIVA.json");
export const ESPERA_CURTA = Object.freeze(["UM_DE_CADA_VEZ", "PAUSA_MINIMA", "LIMITE_GLOBAL"]);
let POL = null;

export function politica() {
  const f = process.env.SINTONIA_CORTESIA_POLITICA || POLITICA_F;
  if (!POL || POL._F !== f) { POL = JSON.parse(readFileSync(f, "utf8")); POL._F = f; }
  return POL;
}
export const orcamentoDe = dominioRegistavel => politica().MESMO_ORCAMENTO[dominioRegistavel] || dominioRegistavel;
export const livro = () => process.env.SINTONIA_CORTESIA_LIVRO || process.env.SINTONIA_TETO_24H || null;
export const alertasF = () => process.env.SINTONIA_CORTESIA_ALERTAS || (livro() ? join(dirname(livro()), "ALERTAS-SCRAP-ENGINEER.ndjson") : null);

export function classeDe(dom, pol = politica()) {
  const c = pol.CLASSES, api = c.API_COM_LIMITE_PUBLICADO;
  if (Object.prototype.hasOwnProperty.call(api.DOMINIOS, dom)) {
    const a = api.DOMINIOS[dom];
    // LINHAS-NO-CONTADOR (gemeo de `classe_de`): com limite diario publicado, ORCAMENTO_24H fixo; sem ele (NAO_SEI),
    // comeca no ORCAMENTO_INICIAL_24H (o minimo seguro) e so dobra ate ao TETO_DE_SEGURANCA_24H.
    const ini = a.ORCAMENTO_INICIAL_24H ?? a.ORCAMENTO_24H;
    return ["API_COM_LIMITE_PUBLICADO", { INICIAL: ini, TETO: a.TETO_DE_SEGURANCA_24H ?? ini, MINIMO: api.MINIMO_24H,
                                          PAUSA_S: a.PAUSA_MINIMA_S, DOBRA: !!(a.DOBRA ?? api.DOBRA) }];
  }
  const nome = c.PLATAFORMA_GRANDE.DOMINIOS.includes(dom) ? "PLATAFORMA_GRANDE" : "SITE";
  const k = c[nome];
  return [nome, { INICIAL: k.ORCAMENTO_INICIAL_24H, TETO: k.TETO_DE_SEGURANCA_24H, MINIMO: k.MINIMO_24H,
                  PAUSA_S: k.PAUSA_MINIMA_S, DOBRA: !!k.DOBRA }];
}

// ── o livro ANTIGO (D90): {"RESERVAS": [{DOMINIO, QTD, EM, RUN_ID, LINHA}]} — gemeo de `.py` ───────────
// D124-REBASE: leitura compativel (cada reserva antiga = QTD eventos RESERVA, o mesmo EM) e migracao para
// ndjson no 1.o escrito, sob o trinco (o original fica em `<livro>.D90.json`). Malformado = ILEGIVEL.
export const MIGRADO_DE = "TETO-24H/D90";
export const eLivroAntigo = texto => /^\s*\{\s*"RESERVAS"\s*:/.test(String(texto).slice(0, 256));
const ilegivel = m => Object.assign(new Error(m), { ilegivel: true });
export function eventosDoLivroAntigo(texto) {
  let d;
  try { d = JSON.parse(texto); } catch (x) { throw ilegivel(`livro D90 (RESERVAS[]) nao e JSON: ${x.message}`); }
  if (!d || typeof d !== "object" || !Array.isArray(d.RESERVAS)) throw ilegivel("livro D90 sem RESERVAS[]");
  const out = [];
  d.RESERVAS.forEach((r, i) => {
    if (!r || typeof r !== "object" || typeof r.DOMINIO !== "string" || !r.DOMINIO || typeof r.EM !== "number"
        || !Number.isInteger(r.QTD) || r.QTD < 1)
      throw ilegivel(`livro D90: reserva ${i + 1} sem DOMINIO/EM/QTD validos`);
    for (let q = 0; q < r.QTD; q++)
      out.push({ TIPO: "RESERVA", DOMINIO: orcamentoDe(r.DOMINIO), EM: r.EM, RUN_ID: r.RUN_ID ?? null, LINHA: r.LINHA ?? null,
                 HOST: r.DOMINIO, MIGRADO_DE });
  });
  return out;
}
const ordenado = e => Object.fromEntries(Object.keys(e).sort().map(k => [k, e[k]]));
export function migrarLivroAntigo(f) {           // chamar SOB o trinco; idempotente
  if (!existsSync(f)) return { ESTADO: "SEM_LIVRO", LIVRO: f };
  const texto = readFileSync(f, "utf8");
  if (!eLivroAntigo(texto)) return { ESTADO: "JA_NDJSON", LIVRO: f };
  const ev = eventosDoLivroAntigo(texto);
  const copia = `${f}.D90.json`;
  if (!existsSync(copia)) writeFileSync(copia, texto);
  writeFileSync(`${f}.tmp`, ev.map(e => JSON.stringify(ordenado(e)) + "\n").join(""));
  renameSync(`${f}.tmp`, f);
  return { ESTADO: "MIGRADO", LIVRO: f, COPIA_D90: copia, EVENTOS: ev.length };
}
function cabecaDe(f) {
  const fd = openSync(f, "r");
  try { const b = Buffer.alloc(256); const n = readSync(fd, b, 0, 256, 0); return b.subarray(0, n).toString("utf8"); }
  finally { closeSync(fd); }
}

export function lerEventos(f) {
  if (!existsSync(f)) return [];
  const texto = readFileSync(f, "utf8");
  if (eLivroAntigo(texto)) return eventosDoLivroAntigo(texto);
  const out = [];
  texto.split(/\r?\n/).forEach((l, i) => {
    if (!l.trim()) return;
    let e;
    try { e = JSON.parse(l); } catch (x) { throw Object.assign(new Error(`linha ${i + 1} nao e JSON: ${x.message}`), { ilegivel: true }); }
    if (!e || typeof e !== "object" || !["RESERVA", "RESPOSTA", "RENDIMENTO"].includes(e.TIPO)
        || typeof e.DOMINIO !== "string" || typeof e.EM !== "number")
      throw Object.assign(new Error(`linha ${i + 1} sem TIPO/DOMINIO/EM validos`), { ilegivel: true });
    out.push(e);
  });
  return out;
}
const acrescentar = (f, e) => {
  mkdirSync(dirname(f), { recursive: true });
  if (existsSync(f) && eLivroAntigo(cabecaDe(f))) migrarLivroAntigo(f);   // sob o trinco de quem escreve
  appendFileSync(f, JSON.stringify(ordenado(e)) + "\n");
};
const esperarMs = ms => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
function comTrinco(f, fn) {
  const t = `${f}.trinco`;
  mkdirSync(dirname(f), { recursive: true });
  for (let i = 0; ; i++) {
    try { mkdirSync(t); break; }
    catch (e) {
      if (e.code !== "EEXIST") throw Object.assign(new Error(`trinco: ${e.code}`), { trinco: true });
      if (i >= 400) throw Object.assign(new Error(`CORTESIA_TRINCO: ${t} ocupado ha mais de 10 s`), { trinco: true });
      esperarMs(25);
    }
  }
  try { return fn(); } finally { rmdirSync(t); }
}

// ── o estado de um dominio: DERIVADO do livro (linha a linha a de `dobrar_eventos`) ──
export function dobrarEventos(eventos, dom, agora, pol = politica()) {
  const J = Number(pol.JANELA_S), R = pol.RECUO;
  const [nome, k] = classeDe(dom, pol);
  let nivel = Math.trunc(k.INICIAL), desde = null;
  const reservas = [], sinaisEm = [];
  let pausadoAte = 0, retryAte = 0, ultRes = null, ultResp = null, crawl = 0, ultimoSinal = null;
  const evs = eventos.filter(e => e.DOMINIO === dom).sort((a, b) => Number(a.EM) - Number(b.EM));
  const promover = t => {
    if (desde === null) return;
    while (t >= desde + J) {
      const fim = desde + J;
      const usados = reservas.filter(x => desde <= x && x < fim).length;
      const teveSinal = sinaisEm.some(x => desde < x && x < fim);   // o sinal que ABRIU a janela nao conta contra ela
      if (k.DOBRA && !teveSinal && usados > 0 && usados >= Math.ceil(R.FRACAO_DE_USO_PARA_DOBRAR * nivel))
        nivel = Math.min(Math.trunc(k.TETO), nivel * 2);
      desde = fim;
      if (!reservas.some(x => x >= desde) && t >= desde + 2 * J)
        desde += Math.floor((t - desde) / J - 1) * J;
    }
  };
  for (const e of evs) {
    const t = Number(e.EM);
    if (desde === null) desde = t;
    promover(t);
    if (e.TIPO === "RESERVA") {
      reservas.push(t); ultRes = t;
      if (e.CRAWL_DELAY_S !== undefined && e.CRAWL_DELAY_S !== null) crawl = Number(e.CRAWL_DELAY_S);
    } else if (e.TIPO === "RESPOSTA") {
      ultResp = t;
      if (e.SINAIS && e.SINAIS.length) {
        nivel = Math.max(Math.trunc(k.MINIMO), Math.floor(nivel * R.FATOR));
        desde = t;
        sinaisEm.push(t);
        ultimoSinal = { EM: t, SINAIS: [...e.SINAIS], STATUS: e.STATUS ?? null };
        if (e.RETRY_AFTER_S) retryAte = Math.max(retryAte, t + Number(e.RETRY_AFTER_S));
        if (sinaisEm.filter(x => x > t - R.JANELA_DOS_SINAIS_S).length >= R.SINAIS_PARA_PAUSA)
          pausadoAte = Math.max(pausadoAte, t + Number(R.PAUSA_S));
      }
    }
  }
  promover(agora);
  const vivas = reservas.filter(x => x > agora - J).sort((a, b) => a - b);
  const gasto = vivas.length, cabem24h = Math.max(0, nivel - gasto);
  const pausa = Math.max(Number(k.PAUSA_S), crawl);
  let emCursoAte = null;
  if (ultRes !== null && (ultResp === null || ultRes > ultResp) && agora < ultRes + pol.LEASE_S) emCursoAte = ultRes + pol.LEASE_S;
  const marcos = [ultRes, ultResp].filter(x => x !== null);
  const pausaAte = marcos.length ? Math.max(...marcos) + pausa : null;
  const orcAte = cabem24h === 0 && gasto >= nivel && nivel > 0 ? vivas[gasto - nivel] + J : null;
  const bloq = Math.max(pausadoAte, retryAte);
  const situ = pausadoAte > agora ? "PAUSADO" : retryAte > agora ? "RETRY_AFTER"
    : sinaisEm.some(x => x > agora - J) ? "EM_RECUO" : nivel >= Math.trunc(k.TETO) ? "NO_TETO_DE_SEGURANCA" : "NORMAL";
  const proximos = [bloq, emCursoAte, pausaAte, orcAte].filter(x => x !== null && x > agora);
  return { DOMINIO: dom, CLASSE: nome, SITUACAO: situ, ORCAMENTO_24H: nivel, ORCAMENTO_INICIAL_24H: Math.trunc(k.INICIAL),
           TETO_DE_SEGURANCA_24H: Math.trunc(k.TETO), MINIMO_24H: Math.trunc(k.MINIMO), GASTO_24H: gasto,
           CABEM_24H: cabem24h, CABEM: bloq > agora ? 0 : cabem24h, PAUSA_MINIMA_S: pausa,
           SINAIS_24H: sinaisEm.filter(x => x > agora - J).length, ULTIMO_SINAL: ultimoSinal,
           PAUSADO_ATE: pausadoAte || null, RETRY_ATE: retryAte || null, EM_CURSO_ATE: emCursoAte,
           PAUSA_ATE: pausaAte, ORCAMENTO_ATE: orcAte, PROXIMO_PEDIDO_EM: proximos.length ? Math.max(...proximos) : agora,
           JANELA_DESDE: desde };
}

export function emCursoGlobal(eventos, agora, pol = politica(), menos = null) {
  const ult = new Map();
  for (const e of eventos) {
    if (e.TIPO !== "RESERVA" && e.TIPO !== "RESPOSTA") continue;
    const r = ult.get(e.DOMINIO) || [null, null];
    const i = e.TIPO === "RESERVA" ? 0 : 1;
    if (r[i] === null || Number(e.EM) >= r[i]) r[i] = Number(e.EM);
    ult.set(e.DOMINIO, r);
  }
  const out = [];
  for (const [d, [res, resp]] of ult)
    if (d !== menos && res !== null && (resp === null || res > resp) && agora < res + pol.LEASE_S) out.push([d, res + pol.LEASE_S]);
  return out.sort();
}

// ── os sinais (linha a linha os de `detectar_sinais`) ──
const cab = (h, nome) => {
  for (const [k, v] of Object.entries(h || {})) if (String(k).toLowerCase() === nome) return String(v).trim();
  return null;
};
export function retryAfterS(valor, agora, pol = politica()) {
  if (valor === null || valor === undefined || valor === "") return null;
  const v = String(valor).trim();
  let s;
  if (/^\d+$/.test(v)) s = Number(v);
  else {
    const ms = Date.parse(v);
    if (!Number.isFinite(ms)) return null;
    s = ms / 1000 - agora;
  }
  return Math.max(0, Math.min(s, Number(pol.RECUO.RETRY_AFTER_MAXIMO_S)));
}
export function detectarSinais({ status, headers = null, corpo = null, nBytes = null, url = null, marcas = [], historico = [], agora = 0 } = {}, pol = politica()) {
  const S = pol.SINAIS, sinais = [];
  const st = Math.trunc(Number(status || 0));
  if (st === 429) sinais.push("HTTP_429");
  if (st === 503) sinais.push("HTTP_503");
  if (st === 403 && !(historico.length && Number(historico[historico.length - 1].STATUS || 0) === 403)) sinais.push("HTTP_403_NOVO");
  const ra = retryAfterS(cab(headers, "retry-after"), agora, pol);
  if (ra !== null) sinais.push("RETRY_AFTER");
  const txt = (corpo === null ? "" : Buffer.isBuffer(corpo) ? corpo.toString("utf8") : String(corpo)).slice(0, 65536).toLowerCase();
  const tam = nBytes !== null ? nBytes : corpo !== null ? corpo.length : null;
  let desafio = (cab(headers, "cf-mitigated") || "").toLowerCase() === "challenge" || S.DESAFIO_FORTE.some(m => txt.includes(m));
  if (!desafio && (st >= 400 || (tam !== null && tam < S.DESAFIO_FRACO_SO_ABAIXO_DE_BYTES)))
    desafio = S.DESAFIO_FRACO.some(m => txt.includes(m));
  if (desafio) sinais.push("PAGINA_DE_DESAFIO");
  if ((marcas || []).includes("TIMEOUT")) {
    let serie = 1;
    for (let i = historico.length - 1; i >= 0; i--) { if ((historico[i].MARCAS || []).includes("TIMEOUT")) serie++; else break; }
    if (serie >= S.TIMEOUTS_EM_SERIE) sinais.push("TIMEOUTS_EM_SERIE");
  }
  if (url && nBytes !== null && st >= 200 && st < 300) {
    const ant = historico.filter(h => h.URL === url && Number(h.STATUS || 0) >= 200 && Number(h.STATUS || 0) < 300 && h.BYTES !== null && h.BYTES !== undefined);
    if (ant.length && ant[ant.length - 1].BYTES >= S.QUEDA_DE_BYTES_REFERENCIA_MINIMA && nBytes < S.QUEDA_DE_BYTES_FRACAO * ant[ant.length - 1].BYTES)
      sinais.push("QUEDA_DE_BYTES");
  }
  return [sinais, ra];
}

// ── a API ──
export function estadoDoDominio(dominioRegistavel, agora = Date.now() / 1000) {
  const dom = orcamentoDe(dominioRegistavel), f = livro();
  let ev = [];
  try { ev = f ? lerEventos(f) : []; } catch (e) { return { DOMINIO: dom, ESTADO: "UNKNOWN", PORQUE: `livro ilegivel: ${e.message}` }; }
  return { ...dobrarEventos(ev, dom, agora), ESTADO: f ? "LIDO" : "SEM_LIVRO" };
}
export function orcamentoDoDominio(dominioRegistavel, agora) {
  const e = estadoDoDominio(dominioRegistavel, agora);
  return e.ESTADO === "UNKNOWN" ? null : e.CABEM;
}
export function tetoVigente(dominioRegistavel, agora) {
  const e = estadoDoDominio(dominioRegistavel, agora);
  if (e.ESTADO === "UNKNOWN") throw new Error(`CORTESIA_LIVRO_ILEGIVEL: ${e.PORQUE}`);
  return e.ORCAMENTO_24H;
}

const iso = t => new Date(t * 1000).toISOString().replace(/\.\d{3}Z$/, "+00:00");
function lerAlertas(a) {
  if (!a || !existsSync(a)) return [];
  return readFileSync(a, "utf8").split(/\r?\n/).filter(l => l.trim()).map(l => JSON.parse(l));
}
function alertar(f, dom, est, linha, tipo, sinal, recibos, t) {
  const pol = politica(), a = alertasF();
  for (const x of lerAlertas(a))
    if (x.DOMINIO === dom && x.TIPO_ALERTA === tipo && Number(x.EM || 0) > t - pol.ALERTAS.UM_POR_DOMINIO_E_TIPO_POR_S) return null;
  const b = { TIPO_ALERTA: tipo, DOMINIO: dom, CLASSE: est.CLASSE ?? null, LINHA: linha, EM: t, EM_ISO: iso(t),
              SINAL_MEDIDO: sinal, RECIBOS: recibos.filter(Boolean), ORCAMENTO_24H: est.ORCAMENTO_24H ?? null,
              SITUACAO: est.SITUACAO ?? null, ESTUDAR: pol.ALERTAS.MELHORIAS_A_ESTUDAR, LIVRO: String(f) };
  acrescentar(a, b);
  return b;
}

// D124-REBASE: o teto POR CORRIDA de quem pede SEM livro (gemeo de `teto_sem_livro`): sem memoria entre
// corridas nao ha prova de que o site aguenta o inicial; vale o que a politica declara em SEM_LIVRO.
export function tetoSemLivro(dominioRegistavel, pol = politica()) {
  const regra = (pol.SEM_LIVRO || {}).TETO_POR_CORRIDA ?? "MINIMO_24H";
  if (regra !== "MINIMO_24H") throw new Error(`POLITICA: SEM_LIVRO.TETO_POR_CORRIDA=${regra} (so MINIMO_24H e conhecido)`);
  return classeDe(orcamentoDe(dominioRegistavel), pol)[1].MINIMO;
}

export function reservar(dominioRegistavel, { runId, linha, crawlDelayS = null, agora = null, host = null } = {}) {
  const f = livro();
  const base = { DOMINIO: null, RUN_ID: runId ?? null, LINHA: linha ?? null };
  if (!f) return { ...base, ESTADO: "FAIL", PORQUE: "SINTONIA_CORTESIA_LIVRO vazio: sem contador partilhado nao se pede" };
  const dom = orcamentoDe(String(dominioRegistavel || ""));
  base.DOMINIO = dom;
  if (!dom || !runId || !linha) return { ...base, ESTADO: "FAIL", PORQUE: "pedido invalido (dominio, runId, linha)" };
  try {
    return comTrinco(f, () => {
      const ev = lerEventos(f), t = agora ?? Date.now() / 1000, pol = politica();
      const e = dobrarEventos(ev, dom, t, pol);
      if (crawlDelayS !== null) {
        const marcos = ev.filter(x => x.DOMINIO === dom && (x.TIPO === "RESERVA" || x.TIPO === "RESPOSTA")).map(x => Number(x.EM));
        if (marcos.length && Math.max(...marcos) + Number(crawlDelayS) > (e.PAUSA_ATE || 0)) e.PAUSA_ATE = Math.max(...marcos) + Number(crawlDelayS);
      }
      let porque = null, ate = null;
      if ((e.PAUSADO_ATE || 0) > t) [porque, ate] = ["PAUSA_24H", e.PAUSADO_ATE];
      else if ((e.RETRY_ATE || 0) > t) [porque, ate] = ["RETRY_AFTER", e.RETRY_ATE];
      else if (e.CABEM_24H <= 0) [porque, ate] = ["ORCAMENTO_ESGOTADO", e.ORCAMENTO_ATE || t + pol.JANELA_S];
      else if (e.EM_CURSO_ATE !== null) [porque, ate] = ["UM_DE_CADA_VEZ", e.EM_CURSO_ATE];
      else if (e.PAUSA_ATE !== null && e.PAUSA_ATE > t) [porque, ate] = ["PAUSA_MINIMA", e.PAUSA_ATE];
      else {
        const outros = emCursoGlobal(ev, t, pol, dom);
        if (outros.length >= pol.LIMITE_GLOBAL_EM_PARALELO) [porque, ate] = ["LIMITE_GLOBAL", Math.min(...outros.map(o => o[1]))];
      }
      if (porque) {
        if (porque === "ORCAMENTO_ESGOTADO" && e.ORCAMENTO_24H >= e.TETO_DE_SEGURANCA_24H)
          alertar(f, dom, e, linha, e.CLASSE === "API_COM_LIMITE_PUBLICADO" ? "LIMITE_PUBLICADO" : "TETO_DE_SEGURANCA",
                  { GASTO_24H: e.GASTO_24H, ORCAMENTO_24H: e.ORCAMENTO_24H }, [runId], t);
        return { ...base, ESTADO: "ADIADO_ATE", ATE: ate, MOTIVO: porque, GASTO_24H: e.GASTO_24H, ORCAMENTO_24H: e.ORCAMENTO_24H };
      }
      const r = { TIPO: "RESERVA", DOMINIO: dom, EM: t, RUN_ID: runId, LINHA: linha, HOST: host || dom };
      if (crawlDelayS !== null) r.CRAWL_DELAY_S = Number(crawlDelayS);
      acrescentar(f, r);
      return { ...base, ESTADO: "RESERVADO", EM: t, GASTO_24H: e.GASTO_24H + 1, ORCAMENTO_24H: e.ORCAMENTO_24H, CABEM_24H: e.CABEM_24H - 1 };
    });
  } catch (x) {
    if (x.trinco || x.ilegivel) return { ...base, ESTADO: "UNKNOWN", PORQUE: x.ilegivel ? `livro ilegivel: ${x.message}` : x.message };
    throw x;
  }
}

export function registrarResposta(dominioRegistavel, { status, headers = null, sinais = [], marcas = [], url = null, nBytes = null, corpo = null, runId, linha, agora = null } = {}) {
  const f = livro();
  const base = { RUN_ID: runId ?? null, LINHA: linha ?? null };
  if (!f) return { ...base, ESTADO: "FAIL", PORQUE: "SINTONIA_CORTESIA_LIVRO vazio" };
  const pol = politica();
  const fora = sinais.filter(s => !pol.SINAIS.VOCABULARIO.includes(s)).concat(marcas.filter(m => !pol.SINAIS.MARCAS.includes(m)));
  if (fora.length) return { ...base, ESTADO: "FAIL", PORQUE: `sinal/marca fora do vocabulario: ${fora}` };
  const dom = orcamentoDe(String(dominioRegistavel || ""));
  try {
    return comTrinco(f, () => {
      const ev = lerEventos(f), t = agora ?? Date.now() / 1000;
      const hist = ev.filter(e => e.DOMINIO === dom && e.TIPO === "RESPOSTA");
      const [med, ra] = detectarSinais({ status, headers, corpo, nBytes, url, marcas, historico: hist, agora: t }, pol);
      const todos = [...new Set([...med, ...sinais])].sort((a, b) => pol.SINAIS.VOCABULARIO.indexOf(a) - pol.SINAIS.VOCABULARIO.indexOf(b));
      const e = { TIPO: "RESPOSTA", DOMINIO: dom, EM: t, STATUS: Math.trunc(Number(status || 0)), SINAIS: todos, MARCAS: [...marcas],
                  RETRY_AFTER_S: ra, BYTES: nBytes, URL: url, RUN_ID: runId, LINHA: linha };
      acrescentar(f, e);
      const depois = dobrarEventos(ev.concat([e]), dom, t, pol);
      let alerta = null;
      if (todos.length)
        alerta = alertar(f, dom, depois, linha, depois.SITUACAO === "PAUSADO" ? "PAUSA_24H" : "RECUO",
                         { STATUS: e.STATUS, SINAIS: todos, RETRY_AFTER_S: ra, URL: url }, [runId].concat(url ? [url] : []), t);
      return { ...base, ESTADO: "REGISTADO", DOMINIO: dom, SINAIS: todos, RETRY_AFTER_S: ra, DEPOIS: depois, ALERTA: alerta };
    });
  } catch (x) {
    if (x.trinco || x.ilegivel) return { ...base, ESTADO: "UNKNOWN", PORQUE: x.ilegivel ? `livro ilegivel: ${x.message}` : x.message };
    throw x;
  }
}
