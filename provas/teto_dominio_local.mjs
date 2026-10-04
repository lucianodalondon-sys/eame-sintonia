// O TETO POR DOMINIO NA ONDA INTEIRA (D38) — PROVADO PELO CURL, CONTRA UM SERVIDOR LOCAL.
//
//     node provas/teto_dominio_local.mjs
//
// ONDA2-PLANO (25/09) mediu que cia.it tem 5 fontes na coorte e levou 16 pedidos
// na 1.a onda: cada fonte e uma corrida, e o teto de 5 recomecava a cada uma.
// A D38 manda contar por DOMINIO REGISTAVEL na onda inteira. Esta prova liga o
// transporte de verdade (`baixar()` com o curl) contra um servidor HTTP em
// 127.0.0.1; quem conta os pedidos e o SERVIDOR.
//
// Zero rede externa: proxy de saida para uma porta fechada; os quatro nomes
// resolvem para 127.0.0.1 por um `_curlrc` so desta prova (o mecanismo do C13
// de `cortesia_http_local.mjs`).
//
//   D1  5 corridas do mesmo dominio, com livro da onda -> o servidor ve <= 5 pedidos a *.cia.test
//   D2  subdominios contam juntos (cia.test, www., sub.) -> o livro diz { "cia.test": 5 }
//   D3  as corridas depois do teto nao pedem nada       -> motivo TETO_DOMINIO; nenhuma fonte FAILED
//   D4  outro dominio nao e afetado                     -> outro.test tem os seus pedidos
//   D5  sem livro da onda (como antes)                  -> cada corrida tem os seus 5: o livro e a protecao
//   D6  livro ilegivel                                  -> falha alto, nao recomeca do zero
//   D7  o dominio registavel (sem rede)                 -> www/sub juntos; gov.it e regioes separados
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, existsSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "teto-dominio-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
// D41 (FREIO-SOCIAL): o host do stream do YouTube tambem resolve para o servidor local
// (o curl nunca sai da maquina): e o nome REAL que importa, porque o teto le o dominio.
const GV = "rr1---sn-x.googlevideo.com";
const NOMES = ["cia.test", "www.cia.test", "sub.cia.test", "outro.test", GV];
process.env.NO_PROXY = process.env.no_proxy = ["127.0.0.1", "localhost", ...NOMES].join(",");
for (const k of ["SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA"]) delete process.env[k];
process.env.SINTONIA_PAUSA_POR_HOST_S = "0";   // a pausa tem prova propria; aqui mede-se o teto

const enchimento = "<p>" + "Testo dell'articolo. ".repeat(80) + "</p>";
let INDICE = {};                               // host -> slugs anunciados
const PEDIDOS = [];                            // { host, p }
const servidor = createServer((req, res) => {
  const host = String(req.headers.host || "").split(":")[0];
  const p = req.url;
  PEDIDOS.push({ host, p });
  if (p === "/robots.txt") { res.writeHead(404); res.end("non trovato"); return; }
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  if (p === "/news/") {
    res.end(`<!DOCTYPE html><html><body>${(INDICE[host] || []).map(s => `<a href="/news/${s}/">${s}</a>`).join("\n")}${enchimento}</body></html>`);
    return;
  }
  if (/^\/news\/[a-z0-9-]+\/?$/.test(p)) {
    res.end(`<!DOCTYPE html><html><head><title>${p}</title></head><body><h1>${p}</h1>${enchimento}</body></html>`);
    return;
  }
  res.writeHead(404); res.end("non trovato");
});
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const PORTA = servidor.address().port;
const CURL_HOME = mkdtempSync(join(tmpdir(), "teto-dominio-curl-"));
const rc = NOMES.map(h => `resolve = "${h}:${PORTA}:127.0.0.1"`).join("\n") + "\n";
for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(CURL_HOME, n), rc);
process.env.CURL_HOME = CURL_HOME;

const M = await import("../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../regras/italy_contracts.mjs");
const FONTE = "IT-T10-018";
const ORIGINAL = { ACQUISITION: CONTRACTS[FONTE].ACQUISITION, RECOLLECTION: CONTRACTS[FONTE].RECOLLECTION,
                   CANONICAL_ENTRY_URL: CONTRACTS[FONTE].CANONICAL_ENTRY_URL };
let n = 0;
// Uma «fonte» = uma corrida num host; slugs novos a cada corrida (senao o livro salta-os).
async function corrida(host, materias = 3) {
  n++;
  const slugs = Array.from({ length: materias }, (_, i) => `materia-${n}-${i}`);
  INDICE[host] = slugs;
  CONTRACTS[FONTE].ACQUISITION = { ...ORIGINAL.ACQUISITION, INDEX_URL: `http://${host}:${PORTA}/news/`, MAX_TARGETS: 30,
    LINK_PATTERN: String.raw`^http://(?:www\.|sub\.)?(?:cia|outro)\.test:\d+/news/[a-z0-9]+(?:-[a-z0-9]+)+/?$` };
  CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `http://${host}:${PORTA}/news/`;
  CONTRACTS[FONTE].RECOLLECTION = undefined;
  const antes = PEDIDOS.length;
  const { resumo } = await M.executarRodada({ runId: `PROVA_TETO_DOMINIO_${n}_${Date.now()}`,
    apenas: [FONTE], pularParse: true, nota: `prova teto dominio ${host}` });
  return { host, c: resumo.contadores, resumo, feitos: PEDIDOS.slice(antes) };
}
const aCia = feitos => feitos.filter(x => x.host.endsWith("cia.test")).length;

let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};

try {
  console.log(`\n(servidor 127.0.0.1:${PORTA} · raiz ${RAIZ})`);

  console.log("\n══ D1–D4 · uma onda com livro: 5 corridas em cia.test, 1 em outro.test ══");
  const LIVRO = join(RAIZ, "TETO-ONDA.json");
  process.env.SINTONIA_TETO_ONDA = LIVRO;
  const onda = [];
  for (const h of ["cia.test", "www.cia.test", "sub.cia.test", "cia.test", "sub.cia.test"]) onda.push(await corrida(h));
  const outro = await corrida("outro.test");
  const livro = JSON.parse(readFileSync(LIVRO, "utf8")).PEDIDOS_POR_DOMINIO;
  const totalCia = onda.reduce((s, r) => s + aCia(r.feitos), 0);
  console.log(`  pedidos a *.cia.test por corrida: ${JSON.stringify(onda.map(r => aCia(r.feitos)))} · livro ${JSON.stringify(livro)}`);
  t("D1: o servidor ve no maximo 5 pedidos a *.cia.test na onda inteira", () => {
    assert.ok(totalCia <= 5, `foram ${totalCia}`);
    assert.equal(totalCia, 5, "a onda devia gastar o teto todo (3 materias + indice + robots por corrida)");
  });
  t("D2: subdominios contam juntos — o livro tem uma chave so para cia.test, e diz 5", () => {
    assert.equal(livro["cia.test"], 5, JSON.stringify(livro));
    assert.ok(!Object.keys(livro).some(k => k !== "cia.test" && k.endsWith("cia.test")), JSON.stringify(livro));
  });
  t("D3: as corridas depois do teto nao pedem nada, com motivo TETO_DOMINIO; nenhuma FAILED", () => {
    const depois = onda.slice(1);
    assert.ok(depois.every(r => aCia(r.feitos) === 0), JSON.stringify(depois.map(r => aCia(r.feitos))));
    for (const r of onda) assert.equal(r.c.FAILED, 0, JSON.stringify(r.c));
    const recusas = depois.flatMap(r => r.resumo.CORTESIA.RECUSAS.map(x => x.MOTIVO));
    assert.ok(recusas.length > 0 && recusas.every(m => m === "TETO_DOMINIO"), JSON.stringify(recusas));
    assert.equal(onda[4].resumo.CORTESIA.TETO_CONTA_POR, "DOMINIO_REGISTAVEL_NA_ONDA");
  });
  t("D4: outro dominio nao e afetado — outro.test tem os seus pedidos, no maximo 5", () => {
    const k = outro.feitos.filter(x => x.host === "outro.test").length;
    assert.ok(k >= 1 && k <= 5, `outro.test: ${k}`);
    assert.equal(livro["outro.test"], k, JSON.stringify(livro));
    assert.equal(outro.c.FAILED, 0);
  });

  console.log("\n══ D5 · sem livro da onda: cada corrida recomeca (como antes) ══");
  delete process.env.SINTONIA_TETO_ONDA;
  const s1 = await corrida("cia.test"), s2 = await corrida("sub.cia.test");
  t("D5: sem livro, cada corrida tem o seu teto — e por isso o condutor da onda TEM de nomear o livro", () => {
    assert.equal(aCia(s1.feitos), 5); assert.equal(aCia(s2.feitos), 5);
    assert.equal(s1.resumo.CORTESIA.TETO_CONTA_POR, "DOMINIO_REGISTAVEL_NA_CORRIDA");
    assert.deepEqual(s2.resumo.CORTESIA.PEDIDOS_POR_DOMINIO, { "cia.test": 5 });
  });

  console.log("\n══ D6 · livro ilegivel ══");
  const MAU = join(RAIZ, "TETO-ONDA-MAU.json");
  writeFileSync(MAU, "{ isto nao e json");
  process.env.SINTONIA_TETO_ONDA = MAU;
  let erro = null;
  try { await corrida("outro.test"); } catch (e) { erro = e; }
  delete process.env.SINTONIA_TETO_ONDA;
  t("D6: livro ilegivel falha alto (TETO_ONDA_ILEGIVEL) em vez de recomecar do zero", () => {
    assert.ok(erro && /TETO_ONDA_ILEGIVEL/.test(String(erro.message)), String(erro && erro.message));
  });

  console.log("\n══ D8 · D41: googlevideo.com paga no orcamento do youtube.com ══");
  const LIVRO41 = join(RAIZ, "TETO-ONDA-D41.json");
  process.env.SINTONIA_TETO_ONDA = LIVRO41;
  writeFileSync(LIVRO41, JSON.stringify({ PEDIDOS_POR_DOMINIO: { "youtube.com": 5 } }));
  const gvCheio = await corrida(GV);
  writeFileSync(LIVRO41, JSON.stringify({ PEDIDOS_POR_DOMINIO: { "youtube.com": 3 } }));
  const gvDois = await corrida(GV);
  const livro41 = JSON.parse(readFileSync(LIVRO41, "utf8")).PEDIDOS_POR_DOMINIO;
  delete process.env.SINTONIA_TETO_ONDA;
  const aGV = feitos => feitos.filter(x => x.host === GV).length;
  t("D8a: youtube.com esgotado na onda -> o pedido ao googlevideo.com NAO sai (0 no servidor), motivo TETO_DOMINIO", () => {
    assert.equal(aGV(gvCheio.feitos), 0, JSON.stringify(gvCheio.feitos));
    const m = gvCheio.resumo.CORTESIA.RECUSAS.map(x => x.MOTIVO);
    assert.ok(m.length > 0 && m.every(x => x === "TETO_DOMINIO"), JSON.stringify(m));
  });
  t("D8b: com 3 gastos no youtube.com, o googlevideo.com so leva 2 - e o livro soma-os em youtube.com (sem chave googlevideo.com)", () => {
    assert.equal(aGV(gvDois.feitos), 2, JSON.stringify(gvDois.feitos));
    assert.equal(livro41["youtube.com"], 5, JSON.stringify(livro41));
    assert.ok(!("googlevideo.com" in livro41), JSON.stringify(livro41));
  });
  t("D8c: orcamentoDe junta so o que a D41 nomeou", () => {
    assert.equal(M.orcamentoDe(GV), "youtube.com"); assert.equal(M.orcamentoDe("www.youtube.com"), "youtube.com");
    assert.equal(M.orcamentoDe("media.licdn.com"), "licdn.com"); assert.equal(M.orcamentoDe("www.linkedin.com"), "linkedin.com");
  });

  console.log("\n══ D7 · o dominio registavel (sem rede) ══");
  t("D7: www/sub juntos; gov.it e regioes sao sufixo; IP e o proprio", () => {
    const d = M.dominioRegistavel;
    assert.equal(d("www.cia.it"), "cia.it"); assert.equal(d("sub.cia.it"), "cia.it"); assert.equal(d("CIA.IT"), "cia.it");
    assert.equal(d("caf-cia.it"), "caf-cia.it");
    assert.equal(d("www.salute.gov.it"), "salute.gov.it"); assert.notEqual(d("crea.gov.it"), d("salute.gov.it"));
    assert.equal(d("www.arpa.marche.it"), "arpa.marche.it"); assert.notEqual(d("arpa.marche.it"), d("regione.marche.it"));
    assert.equal(d("127.0.0.1"), "127.0.0.1");
  });
} finally {
  CONTRACTS[FONTE].ACQUISITION = ORIGINAL.ACQUISITION;
  CONTRACTS[FONTE].RECOLLECTION = ORIGINAL.RECOLLECTION;
  CONTRACTS[FONTE].CANONICAL_ENTRY_URL = ORIGINAL.CANONICAL_ENTRY_URL;
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
  rmSync(CURL_HOME, { recursive: true, force: true });
}
console.log(`\nTETO_DOMINIO_LOCAL · passou=${passou} FALHAS=${falhou}`);
process.exit(falhou ? 1 : 0);
