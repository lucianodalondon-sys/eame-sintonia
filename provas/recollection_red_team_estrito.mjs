// A REGUA ESTRITA — A SUITE DONA DO FICHEIRO TEM DE MATAR O MUTANTE
//
//     node provas/recollection_red_team_estrito.mjs
//
// ⚠️ PORQUE ISTO EXISTE, E E UM ACHADO DE VERIFICACAO EXTERNA.
// `provas/recollection_red_team.mjs` da por morto um mutante que QUALQUER uma
// das tres suites apanhe. Em 2026-09-22, numa verificacao externa em clone
// isolado sobre 95d69dba, apanhou-se o que isso escondia:
//
//     DECLARADO: r.DETAIL_CONTENT !== "UNKNOWN"   ->   DECLARADO: true
//
//     regras/incrementalidade_test.mjs   PASSOU 23 · FALHOU 0   ← VERDE
//     regras/recollection_test.mjs       FALHOU                 ← so esta matou
//
// A lei estava escrita em letra grande no comentario de
// `recolheitaDoContrato()` e a suite do PROPRIO modulo nao a prendia. Quem
// mexe numa linha corre a suite do ficheiro onde mexeu — nao a de outro
// ficheiro que por acaso tambem a cobre.
//
//     UMA LEI GUARDADA SO NOUTRO FICHEIRO ESTA GUARDADA CONTRA O ACASO,
//     NAO CONTRA QUEM MEXE NA LINHA.
//
// Esta prova mede a regua estrita: para cada ataque, so conta como morto se a
// suite DONA do ficheiro mutado gritar. Protocolo cache-safe §165 na mesma —
// processo novo, diff provado, sonda a provar que o mutante correu, restauro
// em `finally` e conferido no fim.

import { readFileSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

const REGRA = "regras/incrementalidade.mjs";
const NORMAL = "regras/normalizacao_de_conteudo.mjs";

// Quem e a suite DONA de cada ficheiro. Sai do mapa: C-IT-INCREMENTALIDADE
// junta a regra ao teste dela; C-IT-NORMALIZACAO junta o normalizador a
// paridade_test.mjs.
const DONA = {
  [REGRA]: "regras/incrementalidade_test.mjs",
  [NORMAL]: "regras/paridade_test.mjs",
};

const AMBIENTE = { ...process.env, NODE_DISABLE_COMPILE_CACHE: "1" };
delete AMBIENTE.NODE_COMPILE_CACHE;

const MEM = `m.memoriaDosDetalhes([{SOURCE_URL:'u',SOURCE_ID:'X',OBSERVATION_RESULT:'NEW_DOCUMENT',CAPTURED_AT:'2026-01-01T00:00:00Z'}])`;
const sondaRegra = (c) => `import('./${REGRA}').then(m=>{const mem=${MEM};process.stdout.write(String(${c}));}).catch(()=>process.stdout.write('erro'));`;
const sondaNorm = (c) => `import('./${NORMAL}').then(m=>{process.stdout.write(String(${c}));}).catch(()=>process.stdout.write('erro'));`;
const DEC = (c) => `m.decidirSobreDetalhe('u',{memoria:mem,sourceId:'X',contrato:${c},agora:'2026-06-01T00:00:00Z'})`;
const CONT = (v) => `{RECOLLECTION:{DETAIL_CONTENT:'${v}',TTL_SECONDS:null}}`;

const ATAQUES = [
  { ID: "M1", O_QUE: "o salto cego volta a ser indistinguivel do informado", FICHEIRO: REGRA,
    DE: `    const declarado = rec.DECLARADO;`, PARA: `    const declarado = true;`,
    SONDA: sondaRegra(`${DEC("null")}.COBERTURA==='DECLARADA'`) },
  { ID: "M11", O_QUE: "carimbar UNKNOWN a mao compra a admissao", FICHEIRO: REGRA,
    DE: `    DECLARADO: r.DETAIL_CONTENT !== "UNKNOWN",`, PARA: `    DECLARADO: true,`,
    SONDA: sondaRegra(`m.recolheitaDoContrato('X',${CONT("UNKNOWN")}).DECLARADO===true`) },
  { ID: "M6", O_QUE: "a porta deixa entrar quem nao declarou", FICHEIRO: REGRA,
    DE: `  if (rec.DECLARADO) {\n    return {\n      ADMISSIVEL: true,`,
    PARA: `  if (true) {\n    return {\n      ADMISSIVEL: true,`,
    SONDA: sondaRegra(`m.admissivelNaBigCollection('X',null).ADMISSIVEL===true`) },
  { ID: "M3", O_QUE: "o indice deixa de se revisitar", FICHEIRO: REGRA,
    DE: `  return { DECISAO: "FETCH", PORQUE: "o indice anuncia o que ha de novo; revisita-se sempre" };`,
    PARA: `  return { DECISAO: "SKIP_KNOWN", PORQUE: "o indice anuncia o que ha de novo; revisita-se sempre" };`,
    SONDA: sondaRegra(`m.decidirSobreIndice().DECISAO==='SKIP_KNOWN'`) },
  { ID: "M7", O_QUE: "um endereco que falhou nunca mais e tentado", FICHEIRO: REGRA,
    DE: `  if (!conhecido || !conhecido.TEM_DOCUMENTO) {`, PARA: `  if (!conhecido) {`,
    SONDA: `import('./${REGRA}').then(m=>{const mem=m.memoriaDosDetalhes([{SOURCE_URL:'u',SOURCE_ID:'X',OBSERVATION_RESULT:'TRANSPORT_OR_EMPTY',CAPTURED_AT:'2026-01-01T00:00:00Z'}]);process.stdout.write(String(m.decidirSobreDetalhe('u',{memoria:mem,sourceId:'X',contrato:null,agora:'2026-06-01T00:00:00Z'}).DECISAO!=='FETCH'));}).catch(()=>process.stdout.write('erro'));` },
  { ID: "M5", O_QUE: "a memoria indexada pela identidade, nao pelo endereco", FICHEIRO: REGRA,
    DE: `    const url = o && o.SOURCE_URL;`, PARA: `    const url = o && o.DOCUMENT_ID;`,
    SONDA: sondaRegra(`mem.size===0`) },
  { ID: "M8", O_QUE: "tudo o que se conhece passa a ser revisitado", FICHEIRO: REGRA,
    DE: `  if (rec.DETAIL_CONTENT === "MUTABLE") razoes.push("CONTRACT_DECLARES_MUTABLE");`,
    PARA: `  if (rec.DETAIL_CONTENT !== "__nunca__") razoes.push("CONTRACT_DECLARES_MUTABLE");`,
    SONDA: sondaRegra(`${DEC("null")}.DECISAO==='REVALIDATE'`) },
  { ID: "M10", O_QUE: "o salto conhecido vira ida a rede", FICHEIRO: REGRA,
    DE: `      DECISAO: "SKIP_KNOWN",\n      RAZAO: null,\n      COBERTURA:`,
    PARA: `      DECISAO: "FETCH",\n      RAZAO: null,\n      COBERTURA:`,
    SONDA: sondaRegra(`${DEC("null")}.DECISAO==='FETCH'`) },
  { ID: "M-CENSO", O_QUE: "o censo deixa de contar o salto cego", FICHEIRO: REGRA,
    DE: `      if (d.RECOLLECTION_DECLARADA === false) c.DETAIL_SKIPPED_UNDECLARED++;`,
    PARA: `      if (d.RECOLLECTION_DECLARADA === undefined) c.DETAIL_SKIPPED_UNDECLARED++;`,
    SONDA: sondaRegra(`m.censoDasDecisoes([${DEC("null")}]).DETAIL_SKIPPED_UNDECLARED===0`) },
  { ID: "M9", O_QUE: "mudanca real em morada estavel nunca e detectada", FICHEIRO: NORMAL,
    DE: `  const NORMALIZED_CHANGED = a.NORMALIZED_SHA !== b.NORMALIZED_SHA;`,
    PARA: `  const NORMALIZED_CHANGED = false;`,
    SONDA: sondaNorm(`m.compararConteudo(Buffer.from('<html><p>a</p></html>'),Buffer.from('<html><p>b</p></html>')).VEREDICTO!=='MATERIAL_CHANGE'`) },
  { ID: "M2/M4", O_QUE: "regra volatil alarga-se ate comer o corpo da materia", FICHEIRO: NORMAL,
    DE: `    REGRA: /(view-dom-id-)[0-9a-f]{16,}/gi,`,
    PARA: `    REGRA: /(view-dom-id-)?<p>[\\s\\S]*?<\\/p>/gi,`,
    SONDA: sondaNorm(`m.textoNormalizado(Buffer.from('<html><p>materia</p></html>')).TEXTO.includes('materia')===false`) },
  { ID: "M12", O_QUE: "a canonicalizacao come os cinco caracteres de HTML", FICHEIRO: NORMAL,
    DE: `const NAO_SE_TRADUZ = new Set([34, 38, 39, 60, 62]);`,
    PARA: `const NAO_SE_TRADUZ = new Set([]);`,
    SONDA: sondaNorm(`m.canonicalizarEntidades('&#60;').TEXTO==='<'`) },
];

const TODAS = ["regras/incrementalidade_test.mjs", "regras/recollection_test.mjs", "regras/paridade_test.mjs"];

function verde(f) {
  try { execFileSync("node", [f], { env: AMBIENTE, encoding: "utf8", stdio: "pipe", timeout: 300000 }); return true; }
  catch { return false; }
}

function aplicar(a) {
  const t = readFileSync(a.FICHEIRO, "utf8");
  const lf = a.DE, crlf = a.DE.replace(/\n/g, "\r\n");
  const de = t.includes(lf) ? lf : t.includes(crlf) ? crlf : null;
  if (!de) throw new Error(`ANCORA NAO CASA em ${a.FICHEIRO}: ${JSON.stringify(a.DE.slice(0, 60))}`);
  const para = de === crlf ? a.PARA.replace(/\n/g, "\r\n") : a.PARA;
  writeFileSync(a.FICHEIRO, t.replace(de, para));
}

console.log("REGUA ESTRITA · a suite DONA do ficheiro tem de matar\n");
console.log("ATAQUE     FICHEIRO MUTADO                      SUITE DONA                         DONA MATA?  ALGUMA MATA?");
const resultado = [];
for (const a of ATAQUES) {
  try {
    aplicar(a);
    const diff = execFileSync("git", ["diff", "--stat", "--", a.FICHEIRO], { encoding: "utf8" }).trim();
    if (!diff) throw new Error("o ataque nao chegou ao disco");
    const sonda = execFileSync("node", ["--input-type=module", "-e", a.SONDA],
      { env: AMBIENTE, encoding: "utf8", cwd: process.cwd() }).trim();
    if (sonda !== "true") throw new Error(`a sonda nao confirmou o mutante [${sonda}]`);

    const dona = DONA[a.FICHEIRO];
    const donaMata = !verde(dona);
    const algumaMata = TODAS.some((f) => !verde(f));
    resultado.push({ ID: a.ID, O_QUE: a.O_QUE, FICHEIRO: a.FICHEIRO, SUITE_DONA: dona,
      MUTANTE_EXECUTOU: true, DONA_MATA: donaMata, ALGUMA_MATA: algumaMata,
      ESTADO_ESTRITO: donaMata ? "KILLED" : "SURVIVOR_ESTRITO" });
    console.log(`${a.ID.padEnd(10)} ${a.FICHEIRO.padEnd(37)} ${dona.padEnd(34)} ${(donaMata ? "SIM" : "NAO  <<<").padEnd(11)} ${algumaMata ? "sim" : "NAO"}`);
  } catch (e) {
    resultado.push({ ID: a.ID, ESTADO_ESTRITO: "ERRO", PORQUE: e.message });
    console.log(`${a.ID.padEnd(10)} ERRO: ${e.message}`);
  } finally {
    execFileSync("git", ["checkout", "--", a.FICHEIRO], { encoding: "utf8" });
  }
}

const sujo = execFileSync("git", ["diff", "--name-only", "--", REGRA, NORMAL], { encoding: "utf8" }).trim();
const sobrevivem = resultado.filter((r) => r.ESTADO_ESTRITO !== "KILLED");
console.log(`\nRESTAURO: ${sujo ? "⚠️ SUJO " + sujo : "os ficheiros atacados voltaram ao indice"}`);
console.log(`ATAQUES ${resultado.length} · KILLED_PELA_DONA ${resultado.length - sobrevivem.length} · SURVIVORS_REGUA_ESTRITA ${sobrevivem.length}`);
for (const s of sobrevivem) console.log(`  SURVIVOR_ESTRITO ${s.ID} — ${s.O_QUE || s.PORQUE}`);

writeFileSync("provas/RECOLLECTION-RED-TEAM-ESTRITO-V1.json", JSON.stringify({
  PROVA: "provas/recollection_red_team_estrito.mjs",
  REGUA: "so conta como morto se a suite DONA do ficheiro mutado reprovar",
  PORQUE: "achado em verificacao externa sobre 95d69dba: M11 morria so por recollection_test.mjs "
        + "e deixava regras/incrementalidade_test.mjs em 23/23 verde",
  PROTOCOLO: "cache-safe §165: NODE_DISABLE_COMPILE_CACHE=1, processo novo, diff provado, sonda, restauro conferido",
  NODE: process.version,
  ATAQUES: resultado.length,
  SURVIVORS_REGUA_ESTRITA: sobrevivem.length,
  ARVORE_LIMPA_DEPOIS: sujo === "",
  RESULTADO: resultado,
}, null, 1) + "\n");
console.log("\n  escrito: provas/RECOLLECTION-RED-TEAM-ESTRITO-V1.json");
if (sobrevivem.length || sujo) process.exit(1);
