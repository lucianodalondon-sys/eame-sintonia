// T10-TLS-RETRY (01/10/2026) · O TRANSPORTE DA COLETA COM UM CURL FALSO — falha de TLS que passa.
//
//     node provas/t10_tls_retry/transporte_tls_falso.mjs      (quem le e tests/test_transporte_tls_retry.py)
//
// ZERO rede: o curl e trocado por uma funcao (`trocarCurlParaTeste`) que devolve o que o ROTEIRO manda —
// o `curl: (35) schannel: SEC_E_ILLEGAL_MESSAGE` medido pelo Scrap no cluster edagricole (30/09-01/10), um
// 200, um desafio Cloudflare. Licenca, robots, reserva no livro de 24 h, pausa e retentativa correm o codigo
// de producao (`baixar()` com as 2 tentativas da coleta). Os proxies apontam para uma porta morta, por cautela.
//
// Imprime UMA linha `T10_JSON=` com o que mediu em cada caso; o juizo e do teste Python, caso a caso.
//
//   A        35 e depois 200, politica com pausa 0, sem livro   -> o intervalo entre as 2 tentativas
//   A_REAL   o mesmo com a politica REAL (SITE 5 s) e livro     -> o recuo SOMA-SE a pausa de cortesia
//   B        35 e depois 200, com livro, num subsite           -> reservas e respostas no livro
//   B2       35 nas duas, com livro                            -> reservas, a resposta STATUS 0, o orcamento
//   B3       dois subsites do MESMO dominio, cada um 35+200    -> a cota do dominio registavel
//   C/C_LIVRO desafio (cf-mitigated: challenge)                -> 1 pedido, sinal, sem recuo, recusa a seguir
//   D        curl 60 (nao transitorio)                         -> 1 pedido, sem recuo antes dele
//   E        3 tentativas, 35 em todas                         -> recuo crescente e o limite
//   F        o robots.txt com 35 e depois 404                  -> o recuo e a reserva no robots
//   G        LEASE_S curto: a 2.a tentativa nao cabe na reserva -> nao sai
//   H        orcamento 1: o robots (35, depois 404) gasta o ULTIMO lugar -> a retentativa sai na mesma reserva
//   H2       orcamento 2: robots + materia (35, depois 200) no ultimo lugar -> idem, e a reserva fecha
import { mkdtempSync, rmSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const RAIZ = mkdtempSync(join(tmpdir(), "t10-tls-"));
process.env.ITALY_OPS_ROOT = join(RAIZ, "ops");
for (const k of Object.keys(process.env)) if (k.startsWith("SINTONIA_")) delete process.env[k];
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";

const POLITICA_F = new URL("../../regras/POLITICA-CORTESIA-ADAPTATIVA.json", import.meta.url);
const politica = (mudar) => {
  const p = JSON.parse(readFileSync(POLITICA_F, "utf8"));
  mudar(p);
  const f = join(RAIZ, `politica-${Math.random().toString(36).slice(2)}.json`);
  writeFileSync(f, JSON.stringify(p));
  return f;
};
const POL_REAL = join(RAIZ, "politica-real.json");
writeFileSync(POL_REAL, readFileSync(POLITICA_F));
const POL_ZERO = politica(p => { p.CLASSES.SITE.PAUSA_MINIMA_S = 0; });
const POL_LEASE_CURTO = politica(p => { p.CLASSES.SITE.PAUSA_MINIMA_S = 0; p.LEASE_S = 95; });
const orcamento = n => politica(p => { Object.assign(p.CLASSES.SITE, { PAUSA_MINIMA_S: 0, ORCAMENTO_INICIAL_24H: n, MINIMO_24H: 1 }); });
const POL_ORC_1 = orcamento(1), POL_ORC_2 = orcamento(2);

const M = await import("../../coleta/italy_pilot_collect.mjs");
const CA = await import("../../coleta/cortesia_adaptativa.mjs");

// ── o curl falso ──
const STDERR_35 = "curl: (35) schannel: next InitializeSecurityContext failed: SEC_E_ILLEGAL_MESSAGE (0x80090326) - "
  + "This error usually occurs when a fatal SSL/TLS alert is received (e.g. handshake failed).";
let ROTEIRO = {}, CHAMADAS = [];
M.trocarCurlParaTeste((cmd, args) => {
  const url = args[args.length - 1];
  const iD = args.indexOf("-D");
  const cab = iD >= 0 ? args[iD + 1] : null;
  const c = { url, inicio: Date.now(), fim: null };
  CHAMADAS.push(c);
  const fila = ROTEIRO[url] || [];
  const o = fila.length > 1 ? fila.shift() : (fila[0] || { status: 404, corpo: "non trovato" });
  return new Promise((res, rej) => setTimeout(() => {
    c.fim = Date.now();
    if (o.codigo)
      return rej(Object.assign(new Error(`Command failed: curl ${url}`),
        { code: o.codigo, stderr: Buffer.from(o.codigo === 35 ? STDERR_35 : `curl: (${o.codigo}) falso`) }));
    if (cab) writeFileSync(cab, [`HTTP/1.1 ${o.status} X`, ...Object.entries(o.cabecalhos || {}).map(([k, v]) => `${k}: ${v}`)].join("\r\n") + "\r\n\r\n");
    res({ stdout: Buffer.concat([Buffer.from(o.corpo ?? "", "utf8"),
      Buffer.from(`\n__S__${o.status}\t${o.tipo || "text/html"}\t`, "latin1")]) });
  }, o.demoraMs || 0));
});

const PAGINA = "<!DOCTYPE html><html><body><h1>articolo</h1>" + "<p>testo dell'articolo</p>".repeat(40) + "</body></html>";
const OK = { status: 200, corpo: PAGINA };
const TLS = { codigo: 35 };
const DESAFIO = { status: 200, corpo: "<html><head><title>Just a moment...</title></head><body>cf</body></html>",
                  cabecalhos: { "cf-mitigated": "challenge" } };

function ambiente({ livro, pol }) {
  if (livro) process.env.SINTONIA_CORTESIA_LIVRO = join(RAIZ, `livro-${Math.random().toString(36).slice(2)}.ndjson`);
  else delete process.env.SINTONIA_CORTESIA_LIVRO;
  process.env.SINTONIA_CORTESIA_POLITICA = pol;
}
const chamadasA = (url) => CHAMADAS.filter(c => c.url === url);
// o intervalo entre o FIM de uma chamada e o INICIO da seguinte (em segundos)
const intervalos = (cs) => cs.slice(1).map((c, i) => (c.inicio - cs[i].fim) / 1000);
function livroDe(dom) {
  const f = process.env.SINTONIA_CORTESIA_LIVRO;
  if (!f) return null;
  const ev = CA.lerEventos(f).filter(e => e.DOMINIO === dom);
  const est = CA.estadoDoDominio(dom);
  return { RESERVAS: ev.filter(e => e.TIPO === "RESERVA").length,
           RESPOSTAS: ev.filter(e => e.TIPO === "RESPOSTA").map(e => ({ URL: e.URL, STATUS: e.STATUS, BYTES: e.BYTES, SINAIS: e.SINAIS })),
           GASTO_24H: est.GASTO_24H, ORCAMENTO_24H: est.ORCAMENTO_24H, EM_CURSO_ATE: est.EM_CURSO_ATE };
}
const resumo = (r) => r && ({ status: r.status, tentativas: r.tentativas, codigo: r.codigo ?? null, recusado: r.recusado ?? null,
                              retry_permitido: r.retry_permitido ?? null, erro: r.erro ? String(r.erro).slice(0, 160) : null });

async function caso(nome, { livro, pol, host, roteiro, tentativas = 2, extra = null }) {
  ambiente({ livro, pol });
  ROTEIRO = roteiro(host); CHAMADAS = [];
  const fonte = `https://${host}/news/articolo/`;
  const robots = `https://${host}/robots.txt`;
  const t0 = Date.now();
  const r = await M.baixarParaTeste(fonte, { runId: `T10-${nome}`, tentativas });
  const out = { RESULTADO: resumo(r), SEGUNDOS: (Date.now() - t0) / 1000,
                CHAMADAS_FONTE: chamadasA(fonte).length, INTERVALOS_FONTE_S: intervalos(chamadasA(fonte)),
                CHAMADAS_ROBOTS: chamadasA(robots).length, INTERVALOS_ROBOTS_S: intervalos(chamadasA(robots)),
                // do fim do robots ao inicio da 1.a tentativa: e ai que um recuo indevido apareceria
                ROBOTS_ATE_FONTE_S: chamadasA(robots).length && chamadasA(fonte).length
                  ? (chamadasA(fonte)[0].inicio - chamadasA(robots).at(-1).fim) / 1000 : null,
                CORTESIA: M.cortesiaParaTeste() };
  if (extra) Object.assign(out, await extra(host));
  out.LIVRO = livroDe(M.dominioRegistavel(host));
  return out;
}

const R = {};
const fonteDe = h => `https://${h}/news/articolo/`;
R.A = await caso("A", { livro: false, pol: POL_ZERO, host: "suinicoltura.caso-a.test", roteiro: h => ({ [fonteDe(h)]: [TLS, OK] }) });
R.A_REAL = await caso("A_REAL", { livro: true, pol: POL_REAL, host: "vigneviniequalita.caso-real.test", roteiro: h => ({ [fonteDe(h)]: [TLS, OK] }) });
R.B = await caso("B", { livro: true, pol: POL_ZERO, host: "terraevita.caso-b.test", roteiro: h => ({ [fonteDe(h)]: [TLS, OK] }) });
R.B2 = await caso("B2", { livro: true, pol: POL_ZERO, host: "suinicoltura.caso-b2.test", roteiro: h => ({ [fonteDe(h)]: [TLS] }) });
R.B3 = await caso("B3", { livro: true, pol: POL_ZERO, host: "suinicoltura.caso-b3.test",
  roteiro: h => ({ [fonteDe(h)]: [TLS, OK], [fonteDe("terraevita.caso-b3.test")]: [TLS, OK] }),
  extra: async () => {
    const r2 = await M.baixarParaTeste(fonteDe("terraevita.caso-b3.test"), { runId: "T10-B3", reiniciar: false });
    return { RESULTADO_SUBSITE_2: resumo(r2), CHAMADAS_SUBSITE_2: chamadasA(fonteDe("terraevita.caso-b3.test")).length };
  } });
const extraDesafio = async (h) => {
  const outra = `https://${h}/news/outra/`;
  const r2 = await M.baixarParaTeste(outra, { runId: "T10-C", reiniciar: false });
  return { RESULTADO_A_SEGUIR: resumo(r2), CHAMADAS_A_SEGUIR: chamadasA(outra).length };
};
R.C = await caso("C", { livro: false, pol: POL_ZERO, host: "www.caso-c.test", roteiro: h => ({ [fonteDe(h)]: [DESAFIO] }), extra: extraDesafio });
R.C_LIVRO = await caso("C_LIVRO", { livro: true, pol: POL_ZERO, host: "www.caso-c-livro.test", roteiro: h => ({ [fonteDe(h)]: [DESAFIO] }) });
R.D = await caso("D", { livro: false, pol: POL_ZERO, host: "www.caso-d.test", roteiro: h => ({ [fonteDe(h)]: [{ codigo: 60 }] }) });
R.E = await caso("E", { livro: false, pol: POL_ZERO, host: "www.caso-e.test", tentativas: 3, roteiro: h => ({ [fonteDe(h)]: [TLS] }) });
R.F = await caso("F", { livro: true, pol: POL_ZERO, host: "www.caso-f.test",
  roteiro: h => ({ [`https://${h}/robots.txt`]: [TLS, { status: 404, corpo: "non trovato" }], [fonteDe(h)]: [OK] }) });
R.G = await caso("G", { livro: true, pol: POL_LEASE_CURTO, host: "www.caso-g.test",
  roteiro: h => ({ [fonteDe(h)]: [{ codigo: 35, demoraMs: 2500 }, OK] }) });
R.H = await caso("H", { livro: true, pol: POL_ORC_1, host: "www.caso-h.test",
  roteiro: h => ({ [`https://${h}/robots.txt`]: [TLS, { status: 404, corpo: "non trovato" }], [fonteDe(h)]: [OK] }) });
R.H2 = await caso("H2", { livro: true, pol: POL_ORC_2, host: "www.caso-h2.test", roteiro: h => ({ [fonteDe(h)]: [TLS, OK] }) });

R._RECUO = { RECUO_TRANSITORIO: M.RECUO_TRANSITORIO ?? null,
             PAUSA_SITE_REAL_S: JSON.parse(readFileSync(POLITICA_F, "utf8")).CLASSES.SITE.PAUSA_MINIMA_S,
             LEASE_S_REAL: JSON.parse(readFileSync(POLITICA_F, "utf8")).LEASE_S };
console.log("T10_JSON=" + JSON.stringify(R));
rmSync(RAIZ, { recursive: true, force: true });
