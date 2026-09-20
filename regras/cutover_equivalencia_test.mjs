// SINTONIA EAME — A PROVA DE EQUIVALÊNCIA DO CUTOVER
//
//     node regras/cutover_equivalencia_test.mjs          # sem rede
//     node regras/cutover_equivalencia_test.mjs --vivo   # + os 4 índices reais
//
// O QUE ELA PROVA
// ----------------
// Que os sete `case` de `alvosDe()` e os sete de `identidade()` que viviam em
// `coleta/italy_pilot_collect.mjs` @ 380bf090 fazem HOJE, por contrato, o
// MESMO que faziam por código. A régua é a cópia congelada desse código
// (`provas/fixtures/legado_italy_pilot_380bf090.mjs`), e os pesos são os 10
// documentos brutos que o repositório guarda em `data/collection-store/italy`
// — cada um numa pasta cujo NOME é o DOCUMENT_ID que o `case` lhe deu.
//
//     LEGACY_BEHAVIOR_CAPTURED = YES   é a fixture.
//     CONTRACT_BEHAVIOR_PROVEN = YES   é este ficheiro a passar.
//
// E o que ela NÃO prova: que a fonte continua viva. Isso é o canário, com
// rede, e vive noutro sítio (`--vivo` corre-o à mão, e diz o que viu).

import { strict as assert } from "node:assert";
import { readFileSync, existsSync, writeFileSync, rmSync, mkdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { CONTRACTS } from "./italy_contracts.mjs";
import { alvosDoContrato, identidadeDoContrato, CONTRATO_MOTOR_VERSAO } from "./motor_de_rota.mjs";
import { ADAPTERS, semanaIso } from "../coleta/adaptadores_de_aquisicao.mjs";
import { alvosDeLegado, identidadeLegada, LEGADO_FONTES, LEGADO_HEAD } from "../provas/fixtures/legado_italy_pilot_380bf090.mjs";

let ok = 0, mau = 0, saltados = 0;
const T = (nome, fn) => {
  try { fn(); console.log(`  PASS  ${nome}`); ok++; }
  catch (e) { console.log(`  FAIL  ${nome}\n        ${e.message}`); mau++; }
};
const TA = async (nome, fn) => {
  try { await fn(); console.log(`  PASS  ${nome}`); ok++; }
  catch (e) { console.log(`  FAIL  ${nome}\n        ${e.message}`); mau++; }
};
const SKIP = (nome, porque) => { console.log(`  SKIP  ${nome} — ${porque}`); saltados++; };

// O MESMO pdftotext que o coletor usa. Se não existir nesta máquina, as
// provas que dependem dele ficam SKIP, e isso é resultado e não verde.
// `pdftotext -v` sai com código != 0 de propósito; só ENOENT diz «não há».
const temPdftotext = (() => { try { execFileSync("pdftotext", ["-v"], { stdio: "ignore" }); return true; } catch (e) { return e.code !== "ENOENT"; } })();
const textoDoPdf = (buf) => {
  const dir = "data/collection-store/italy";
  mkdirSync(dir, { recursive: true });
  const tmp = `${dir}/.tmp_equiv_${Math.random().toString(16).slice(2, 10)}.pdf`;
  writeFileSync(tmp, buf);
  try { return execFileSync("pdftotext", ["-layout", "-enc", "UTF-8", tmp, "-"], { maxBuffer: 64e6, encoding: "utf8" }); }
  finally { rmSync(tmp, { force: true }); }
};
const leitoresDe = (buf) => ({
  RAW_LATIN1: () => buf.toString("latin1"),
  RAW_UTF8: () => buf.toString("utf8"),
  PDF_TEXT: () => textoDoPdf(buf),
});

// Um leitor de rede falso: serve o que lhe derem, regista o que lhe pedem.
function leitorFalso(mapa) {
  const pedidos = [];
  const buscar = async (url) => {
    pedidos.push(url);
    const r = mapa[url];
    // `""` é um índice que RESPONDE vazio (HTTP 200 sem links); só a
    // ausência no mapa é 404. Confundir os dois esconderia o fallback.
    if (r === undefined) return { status: 404, buf: Buffer.from("<html>404</html>", "latin1") };
    return { status: 200, buf: Buffer.isBuffer(r) ? r : Buffer.from(r, "latin1") };
  };
  return { buscar, pedidos };
}
const pdfFalso = (bytes) => Buffer.concat([Buffer.from("%PDF-1.4\n", "latin1"), Buffer.alloc(bytes, "x")]);

// Os alvos legados carregavam campos que o `case` de identidade lia
// (`zone`, `table`, `sourceVersion`). Reconstroem-se do nome, para a régua
// legada receber exactamente o que recebia.
function alvoLegado(sourceId, nome) {
  const a = { nome, url: nome };
  if (sourceId === "IT-T2-002") a.zone = Number(nome.match(/agro_(\d{2})/)[1]);
  if (sourceId === "IT-T2-004") a.table = "PRECIPITAZIONE_GIORNALIERA";
  if (sourceId === "IT-T4-001") a.sourceVersion = nome.match(/(\d{8})/)[1];
  return a;
}

console.log(`\nLEGADO = ${LEGADO_HEAD} · MOTOR = ${CONTRATO_MOTOR_VERSAO} · pdftotext = ${temPdftotext ? "sim" : "NAO"}`);

console.log("\n1 · AS SETE FONTES LEGADAS TÊM CONTRATO EXECUTÁVEL");
for (const sid of LEGADO_FONTES) {
  T(`${sid} declara ACQUISITION e IDENTITY`, () => {
    assert.ok(CONTRACTS[sid].ACQUISITION, "sem ACQUISITION");
    assert.ok(CONTRACTS[sid].IDENTITY, "sem IDENTITY");
  });
}

console.log("\n2 · IDENTIDADE — os 10 documentos brutos guardados dão o MESMO DOCUMENT_ID, SOURCE_DATE, SOURCE_DATE_ISO e FACT_TIME");
const STORE = "data/collection-store/italy";
const GUARDADOS = [
  ["IT-T2-002", "ARPAV_Z01_20260903160930/v1_f88c89d73d6a/agro_01.pdf"],
  ["IT-T2-002", "ARPAV_Z09_20260902152638/v1_3d3c1bc0e963/agro_09.pdf"],
  ["IT-T2-002", "ARPAV_Z16_20260903160912/v1_8c13500d4350/agro_16.pdf"],
  ["IT-T2-002", "ARPAV_Z24_20260902152048/v1_0be2d204c98a/agro_24.pdf"],
  ["IT-T2-004", "SIAS_PRECIPITAZIONE_GIORNALIERA_WINDOW_END_2026-09-05/v1_6c71cc191272/NHEOWL0530_00.html"],
  ["IT-T3-002", "CAMPANIA_SA_02-09-2026/v1_0c2723e66201/SA-02-09.pdf"],
  ["IT-T3-005", "TERRETRURIA_31-08-2026_06-09-2026/v1_2e488a8232ba/monitoraggio.html"],
  ["IT-T3-008", "ARIF_SETTIMANALE_2026_N36/v1_e612807928b5/Notiziario_Agrometeorologico_N36_02-09-2026.pdf"],
  ["IT-T3-010", "APOL_2026_N9_BR-COLLINA/v1_59da05274359/Bollettino_Mosca_dellOlivo_n_9_del_07_09_2026.pdf"],
  ["IT-T4-001", "MINSALUTE_FTS6_20260907/v1_9cd4d156369f/PROD_FTS_6_20260907.csv"],
];
let identidadesIguais = 0;
for (const [sid, rel] of GUARDADOS) {
  const p = `${STORE}/${sid}/${rel}`;
  const nome = rel.split("/").pop();
  const precisaPdf = CONTRACTS[sid].IDENTITY.STRATEGY === "CONTENT_CAPTURE"
    && Object.values(CONTRACTS[sid].IDENTITY.CAPTURES).some((c) => c.FROM === "PDF_TEXT");
  if (!existsSync(p)) { SKIP(`${sid} ${nome}`, "ficheiro bruto não está nesta árvore"); continue; }
  if (precisaPdf && !temPdftotext) { SKIP(`${sid} ${nome}`, "pdftotext ausente nesta máquina"); continue; }
  T(`${sid} ${nome}`, () => {
    const buf = readFileSync(p);
    const legado = identidadeLegada(sid, alvoLegado(sid, nome), buf, { pdfTexto: () => textoDoPdf(buf) });
    const novo = identidadeDoContrato(sid, CONTRACTS[sid], { nome, url: nome }, { leitores: leitoresDe(buf) });
    assert.deepEqual(novo, legado, `contrato: ${JSON.stringify(novo)}\n        legado:   ${JSON.stringify(legado)}`);
    // E a pasta onde o documento vive é o DOCUMENT_ID que o `case` lhe deu:
    // a régua não é só a fixture — é o próprio armazém.
    const pasta = rel.split("/")[0];
    assert.equal(String(legado.DOCUMENT_ID).replace(/[:\/\\]/g, "_"), pasta, "o DOCUMENT_ID legado não é a pasta do armazém");
    assert.ok(legado.DOCUMENT_ID, "a régua legada devolveu null — a prova não mediria nada");
    identidadesIguais++;
  });
}

console.log("\n3 · FACT_TIME — nenhum UNKNOWN virou data, e nenhuma identidade ganhou FACT_LOCATION");
const FACT_TIME_LEGADO = {
  "IT-T3-005": "por ponto — cada ponto traz sua propria data de campionamento",
  "IT-T2-002": "UNKNOWN — o PDF nao expoe a data do fato medido, so a de geracao",
  "IT-T2-004": "por linha — cada celula tem sua propria data",
  "IT-T3-002": "UNKNOWN — o boletim nao data a observacao de campo",
  "IT-T3-010": "UNKNOWN — o periodo e de validade, nao de observacao",
  "IT-T3-008": "UNKNOWN",
  "IT-T4-001": "UNKNOWN — o CSV traz datas de registro por linha, nao uma data de fato do arquivo",
};
for (const [sid, esperado] of Object.entries(FACT_TIME_LEGADO)) {
  T(`${sid} FACT_TIME é palavra por palavra o do case`, () => {
    assert.equal(CONTRACTS[sid].IDENTITY.FACT_TIME, esperado);
    assert.ok(!/^\d{4}-\d{2}-\d{2}/.test(String(CONTRACTS[sid].IDENTITY.FACT_TIME)), "FACT_TIME parece uma data — fabricado");
    assert.ok(!("FACT_LOCATION" in CONTRACTS[sid].IDENTITY), "IDENTITY não pode declarar FACT_LOCATION");
  });
}

console.log("\n4 · DESCOBERTA ESTÁTICA E ENUMERADA — os mesmos endereços, na mesma ordem");
const semRede = { buscar: async () => { throw new Error("esta prova não abre a rede"); } };
const soUrlNome = (xs) => xs.map((a) => ({ url: a.url, nome: a.nome }));
await TA("IT-T3-005 · um alvo, o mesmo", async () => {
  const l = await alvosDeLegado("IT-T3-005", CONTRACTS["IT-T3-005"], { baixar: semRede.buscar });
  const n = await alvosDoContrato("IT-T3-005", CONTRACTS["IT-T3-005"], semRede);
  assert.deepEqual(soUrlNome(n), soUrlNome(l));
});
await TA("IT-T2-004 · um alvo, o mesmo", async () => {
  const l = await alvosDeLegado("IT-T2-004", CONTRACTS["IT-T2-004"], { baixar: semRede.buscar });
  const n = await alvosDoContrato("IT-T2-004", CONTRACTS["IT-T2-004"], semRede);
  assert.deepEqual(soUrlNome(n), soUrlNome(l));
});
await TA("IT-T2-002 · piloto = 4 zonas, as mesmas", async () => {
  const l = await alvosDeLegado("IT-T2-002", CONTRACTS["IT-T2-002"], { baixar: semRede.buscar, arpavTodas: false });
  const n = await alvosDoContrato("IT-T2-002", CONTRACTS["IT-T2-002"], { ...semRede, subconjunto: "PILOTO" });
  assert.equal(n.length, 4);
  assert.deepEqual(soUrlNome(n), soUrlNome(l));
  assert.deepEqual(n.map((a) => a.VARS.NN), ["01", "09", "16", "24"], "o alvo carrega a zona em VARS");
});
await TA("IT-T2-002 · TODAS = 29 zonas publicadas, as mesmas, na mesma ordem", async () => {
  const l = await alvosDeLegado("IT-T2-002", CONTRACTS["IT-T2-002"], { baixar: semRede.buscar, arpavTodas: true });
  const n = await alvosDoContrato("IT-T2-002", CONTRACTS["IT-T2-002"], { ...semRede, subconjunto: null });
  assert.equal(n.length, 29);
  assert.deepEqual(soUrlNome(n), soUrlNome(l));
  assert.ok(!n.some((a) => /agro_1[789]\.pdf$/.test(a.nome)), "as zonas 17, 18 e 19 não se publicam — facto da fonte");
});

console.log("\n5 · DESCOBERTA POR ÍNDICE — o mesmo primeiro alvo, a partir do mesmo índice");
const INDICES = {
  "IT-T3-002": ['https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/SA_2026.html',
    '<a href="pdf/SA-16-09.pdf">16/09</a> <a href="pdf/SA-09-09.pdf">09/09</a> <a href="pdf/SA-02-09.pdf">02/09</a>'],
  "IT-T3-010": ['http://www.apol.it',
    '<a href="/documenti/notizie/Bollettino_Mosca_dellOlivo_n_10_del_14_09_2026.pdf">n.10</a> <a href="/documenti/notizie/Bollettino_Mosca_dellOlivo_n_9_del_07_09_2026.pdf">n.9</a>'],
  "IT-T4-001": ['https://www.dati.salute.gov.it/it/dataset/fitosanitari/',
    '<p>Scarica: <a href="/sites/default/files/opendata/PROD_FTS_6_20260914.csv">CSV</a> e opendata/PROD_FTS_6_20260914.xml</p>'],
  "IT-T3-008": ['https://www.agrometeopuglia.it/bollettini',
    '<a href="/bollettino-elettronico/settimanale/2026/Notiziario_Agrometeorologico_N38_16-09-2026.pdf">n.38</a> <a href="/bollettino-elettronico/settimanale/2026/Notiziario_Agrometeorologico_N37_09-09-2026.pdf">n.37</a>'],
};
for (const [sid, [indexUrl, html]] of Object.entries(INDICES)) {
  await TA(`${sid} · índice sintético`, async () => {
    const A = leitorFalso({ [indexUrl]: html }), B = leitorFalso({ [indexUrl]: html });
    const l = await alvosDeLegado(sid, CONTRACTS[sid], { baixar: A.buscar });
    const n = await alvosDoContrato(sid, CONTRACTS[sid], { buscar: B.buscar, adapters: ADAPTERS });
    assert.ok(Array.isArray(l) && Array.isArray(n), `legado=${JSON.stringify(l)} novo=${JSON.stringify(n)}`);
    assert.deepEqual(soUrlNome(n), soUrlNome(l));
    assert.deepEqual(B.pedidos, A.pedidos, "pediram endereços diferentes ao índice");
  });
  await TA(`${sid} · índice vazio → o mesmo EMPTY_LIST (sem fallback) ou o mesmo fallback`, async () => {
    if (sid === "IT-T3-008") return; // o fallback prova-se na secção 6
    const A = leitorFalso({ [indexUrl]: "<p>nada</p>" }), B = leitorFalso({ [indexUrl]: "<p>nada</p>" });
    const l = await alvosDeLegado(sid, CONTRACTS[sid], { baixar: A.buscar });
    const n = await alvosDoContrato(sid, CONTRACTS[sid], { buscar: B.buscar, adapters: ADAPTERS });
    assert.ok(l.erro && /EMPTY_LIST/.test(l.erro), "o legado não deu EMPTY_LIST");
    assert.ok(n.erro && /EMPTY_LIST/.test(n.erro), "o contrato não deu EMPTY_LIST");
  });
  await TA(`${sid} · índice inacessível → erro nos dois, e nenhum alvo inventado`, async () => {
    const A = leitorFalso({}), B = leitorFalso({});
    const l = await alvosDeLegado(sid, CONTRACTS[sid], { baixar: A.buscar });
    const n = await alvosDoContrato(sid, CONTRACTS[sid], { buscar: B.buscar, adapters: ADAPTERS });
    assert.ok(l.erro && n.erro, `legado=${JSON.stringify(l)} novo=${JSON.stringify(n)}`);
    assert.equal(B.pedidos.length, 1, "o contrato não pode sondar quando o índice está caído — isso seria esconder uma fonte caída atrás de uma rota adivinhada");
  });
}

console.log("\n6 · IT-T3-008 — o FALLBACK degradado sobrevive, com o MESMO sinal e a MESMA ordem de sondagem");
const PUG = "https://www.agrometeopuglia.it/bollettini";
const pdfN = (n, dd, mm) => `https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/2026/Notiziario_Agrometeorologico_N${n}_${dd}-${mm}-2026.pdf`;
const relogio = (iso) => () => new Date(iso);
// A régua legada tinha a lista fixa [37, 36, 35]. Para provar EQUIVALÊNCIA
// compara-se com o contrato a usar a MESMA lista; a regra ISO_WEEK do
// contrato real prova-se a seguir como CORRECÇÃO DE ROTA COM PROVA.
const contratoComEnum = () => {
  const c = structuredClone(CONTRACTS["IT-T3-008"]);
  c.ACQUISITION.FALLBACK.NUMEROS = { RULE: "ENUM", VALUES: [37, 36, 35] };
  return c;
};
await TA("índice sem links + N37 de 09/09 existe (relógio 2026-09-10) → o mesmo alvo, marcado degradado nos dois", async () => {
  const mapa = { [PUG]: "<p>renderizado por javascript</p>", [pdfN(37, "09", "09")]: pdfFalso(200000) };
  const A = leitorFalso(mapa), B = leitorFalso(mapa);
  const l = await alvosDeLegado("IT-T3-008", CONTRACTS["IT-T3-008"], { baixar: A.buscar, agora: relogio("2026-09-10T12:00:00Z") });
  const n = await alvosDoContrato("IT-T3-008", contratoComEnum(), { buscar: B.buscar, adapters: ADAPTERS, agora: relogio("2026-09-10T12:00:00Z") });
  assert.deepEqual(n, l, `contrato=${JSON.stringify(n)}\n        legado=${JSON.stringify(l)}`);
  assert.equal(n[0].descoberta_degradada, "INDEX_REQUIRES_BROWSER — indice e JavaScript; caiu para a rota previsivel do contrato");
  assert.deepEqual(B.pedidos, A.pedidos, "a ordem de sondagem mudou");
});
await TA("PDF pequeno demais (< 100000 bytes) é recusado nos dois, e a sondagem continua", async () => {
  const mapa = { [PUG]: "", [pdfN(37, "10", "09")]: pdfFalso(5000), [pdfN(36, "09", "09")]: pdfFalso(200000) };
  const A = leitorFalso(mapa), B = leitorFalso(mapa);
  const l = await alvosDeLegado("IT-T3-008", CONTRACTS["IT-T3-008"], { baixar: A.buscar, agora: relogio("2026-09-10T12:00:00Z") });
  const n = await alvosDoContrato("IT-T3-008", contratoComEnum(), { buscar: B.buscar, adapters: ADAPTERS, agora: relogio("2026-09-10T12:00:00Z") });
  assert.deepEqual(n, l);
  assert.equal(n[0].nome, "Notiziario_Agrometeorologico_N36_09-09-2026.pdf");
});
await TA("HTML servido como PDF é recusado nos dois", async () => {
  const mapa = { [PUG]: "", [pdfN(37, "10", "09")]: Buffer.alloc(200000, "<") };
  const A = leitorFalso(mapa), B = leitorFalso(mapa);
  const l = await alvosDeLegado("IT-T3-008", CONTRACTS["IT-T3-008"], { baixar: A.buscar, agora: relogio("2026-09-10T12:00:00Z") });
  const n = await alvosDoContrato("IT-T3-008", contratoComEnum(), { buscar: B.buscar, adapters: ADAPTERS, agora: relogio("2026-09-10T12:00:00Z") });
  assert.ok(l.erro && n.erro, "um dos dois aceitou HTML como boletim");
  assert.equal(B.pedidos.length, A.pedidos.length, "número de sondagens diferente");
});
await TA("nada nos últimos 10 dias → erro nos dois, e o mesmo número de endereços sondados (1 + 10 × 3)", async () => {
  const A = leitorFalso({ [PUG]: "" }), B = leitorFalso({ [PUG]: "" });
  const l = await alvosDeLegado("IT-T3-008", CONTRACTS["IT-T3-008"], { baixar: A.buscar, agora: relogio("2026-09-20T12:00:00Z") });
  const n = await alvosDoContrato("IT-T3-008", contratoComEnum(), { buscar: B.buscar, adapters: ADAPTERS, agora: relogio("2026-09-20T12:00:00Z") });
  assert.ok(l.erro && n.erro);
  assert.equal(A.pedidos.length, 31);
  assert.deepEqual(B.pedidos, A.pedidos);
});

console.log("\n7 · IT-T3-008 — a CORRECÇÃO DE ROTA (ENUM → ISO_WEEK) está provada, e o contrato real usa-a");
T("N35..N38 são as semanas ISO de 26/08, 02/09, 09/09 e 16/09 de 2026 — quatro de quatro", () => {
  assert.equal(semanaIso(new Date("2026-08-26T00:00:00Z")), 35);
  assert.equal(semanaIso(new Date("2026-09-02T00:00:00Z")), 36);
  assert.equal(semanaIso(new Date("2026-09-09T00:00:00Z")), 37);
  assert.equal(semanaIso(new Date("2026-09-16T00:00:00Z")), 38);
});
T("o contrato real declara NUMEROS = ISO_WEEK com offsets [0, -1]", () => {
  assert.deepEqual(CONTRACTS["IT-T3-008"].ACQUISITION.FALLBACK.NUMEROS, { RULE: "ISO_WEEK", OFFSETS: [0, -1] });
});
await TA("em 2026-09-20 a lista fixa NÃO acha a N38 de 16/09; a semana ISO acha — e marca degradado", async () => {
  const mapa = { [PUG]: "", [pdfN(38, "16", "09")]: pdfFalso(200000), [pdfN(37, "09", "09")]: pdfFalso(200000) };
  const velho = await alvosDoContrato("IT-T3-008", contratoComEnum(), { buscar: leitorFalso(mapa).buscar, adapters: ADAPTERS, agora: relogio("2026-09-20T12:00:00Z") });
  const novo = await alvosDoContrato("IT-T3-008", CONTRACTS["IT-T3-008"], { buscar: leitorFalso(mapa).buscar, adapters: ADAPTERS, agora: relogio("2026-09-20T12:00:00Z") });
  assert.ok(velho.erro, "a lista fixa devia falhar em 2026-09-20 — foi isso que motivou a correcção");
  assert.equal(novo[0]?.nome, "Notiziario_Agrometeorologico_N38_16-09-2026.pdf");
  assert.ok(novo[0].descoberta_degradada, "o sinal de degradação perdeu-se");
});
await TA("com o índice a listar links, o fallback NÃO corre (descoberta normal, sem sinal)", async () => {
  const B = leitorFalso({ [PUG]: `<a href="/bollettino-elettronico/settimanale/2026/Notiziario_Agrometeorologico_N38_16-09-2026.pdf">x</a>` });
  const n = await alvosDoContrato("IT-T3-008", CONTRACTS["IT-T3-008"], { buscar: B.buscar, adapters: ADAPTERS, agora: relogio("2026-09-20T12:00:00Z") });
  assert.equal(n.length, 1);
  assert.equal(n[0].descoberta_degradada, undefined);
  assert.equal(B.pedidos.length, 1);
});

console.log("\n8 · O SWITCH SAIU — e saiu por ficar vazio");
T("o coletor não tem nenhum `case \"IT-` nem `globalThis.__ARPAV_TODAS`", () => {
  const src = readFileSync(new URL("../coleta/italy_pilot_collect.mjs", import.meta.url), "utf8");
  const codigo = src.split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");
  assert.equal((codigo.match(/case "IT-/g) || []).length, 0, "LEGACY_CASES != 0");
  assert.ok(!codigo.includes("switch (sourceId)"), "ainda há um switch por SOURCE_ID");
  assert.ok(!codigo.includes("__ARPAV_TODAS"), "a variável global do ARPAV voltou");
  assert.ok(codigo.includes("alvosDoContrato") && codigo.includes("identidadeDoContrato"));
});
T("o motor continua sem processo filho: pdftotext é injectado pelo coletor", () => {
  const motor = readFileSync(new URL("./motor_de_rota.mjs", import.meta.url), "utf8");
  for (const proibido of ["eval(", "new Function", "execSync", "execFileSync", "spawn(", "child_process"]) {
    assert.ok(!motor.includes(proibido), `o motor contém ${proibido}`);
  }
});

if (process.argv.includes("--vivo")) {
  console.log("\n9 · AO VIVO — os 4 índices reais dão o mesmo primeiro alvo (rede; não conta para o placar)");
  const { execFile } = await import("node:child_process");
  const { promisify } = await import("node:util");
  const run = promisify(execFile);
  const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36";
  const baixar = async (url) => {
    try {
      const { stdout } = await run("curl", ["-sSL", "--max-time", "90", "-A", UA, "-H", "Accept-Language: it-IT,it;q=0.9", "-o", "-", "-w", "\\n__S__%{http_code}", url], { maxBuffer: 128e6, encoding: "buffer" });
      const s = stdout.toString("latin1"); const k = s.lastIndexOf("\n__S__");
      return { buf: stdout.subarray(0, k < 0 ? stdout.length : k), status: Number(s.slice(k + 6)) };
    } catch (e) { return { erro: String(e.message).slice(0, 120), status: 0 }; }
  };
  for (const sid of ["IT-T3-002", "IT-T3-010", "IT-T4-001", "IT-T3-008"]) {
    const l = await alvosDeLegado(sid, CONTRACTS[sid], { baixar });
    const n = await alvosDoContrato(sid, CONTRACTS[sid], { buscar: baixar, adapters: ADAPTERS });
    const igual = JSON.stringify(soUrlNome(Array.isArray(n) ? n : [])) === JSON.stringify(soUrlNome(Array.isArray(l) ? l : []));
    console.log(`  ${sid}  legado=${JSON.stringify(l)}\n  ${" ".repeat(sid.length)}  novo  =${JSON.stringify(n)}\n  ${" ".repeat(sid.length)}  DISCOVERY_EQUIVALENT_LIVE=${igual ? "YES" : "NO"}`);
  }
}

console.log(`\n  PASSOU ${ok} · FALHOU ${mau} · SALTADOS ${saltados} · IDENTIDADES_IGUAIS ${identidadesIguais}/${GUARDADOS.length}\n`);
if (mau) process.exit(1);
