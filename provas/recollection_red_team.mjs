// RED TEAM DA RECOLLECTION — doze ataques ao codigo QUE ESTA MISSAO ESCREVEU.
//
//     node provas/recollection_red_team.mjs
//
// A pergunta nao e «o codigo funciona?». E: «se alguem o desligar, alguma
// prova grita?». Um mutante que sobrevive e uma prova que nao prova nada.
//
// Os dez minimos do briefing estao todos aqui, com o numero ao lado:
//   M1 ausente vira NEVER em silencio        M6  UNKNOWN entra na Big Collection
//   M2 mutavel classificada como imutavel    M7  fonte com feed para de descobrir
//   M3 listing e detail como a mesma coisa   M8  revisita sem necessidade
//   M4 URL igual => conteudo imutavel        M9  mudanca real nunca detectada
//   M5 URL diferente => conteudo novo        M10 recollection parte a incrementalidade
// mais dois que esta missao acrescentou, porque encontrou o defeito:
//   M11 carimbar UNKNOWN a mao compra a admissao
//   M12 a canonicalizacao come os caracteres com significado em HTML
//
// ⚠️ PROTOCOLO CACHE-SAFE (§165), traduzido para Node — o mesmo de
// `provas/paridade_red_team.mjs`, e de proposito o mesmo: duas casas de
// protocolo divergem, e a partir dai nenhuma vale.
//   1 · NODE_DISABLE_COMPILE_CACHE=1 e NODE_COMPILE_CACHE apagado
//   2 · PROCESSO NOVO por ataque
//   3 · provar o DIFF
//   4 · provar que O MUTANTE CORREU (sonda no estado mutado)
//   5 · restaurar em `finally`, e CONFERIR o restauro no fim

import { readFileSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

const REGRA = "regras/incrementalidade.mjs";
const NORMAL = "regras/normalizacao_de_conteudo.mjs";

const AMBIENTE = { ...process.env, NODE_DISABLE_COMPILE_CACHE: "1" };
delete AMBIENTE.NODE_COMPILE_CACHE;

const MEM = `m.memoriaDosDetalhes([{SOURCE_URL:'u',SOURCE_ID:'X',OBSERVATION_RESULT:'NEW_DOCUMENT',CAPTURED_AT:'2026-01-01T00:00:00Z'}])`;
const sondaRegra = (corpo) => `import('./${REGRA}').then(m=>{const mem=${MEM};process.stdout.write(String(${corpo}));}).catch(()=>process.stdout.write('erro'));`;
const sondaNorm = (corpo) => `import('./${NORMAL}').then(m=>{process.stdout.write(String(${corpo}));}).catch(()=>process.stdout.write('erro'));`;
const DEC = (c) => `m.decidirSobreDetalhe('u',{memoria:mem,sourceId:'X',contrato:${c},agora:'2026-06-01T00:00:00Z'})`;
const CONT = (v) => `{RECOLLECTION:{DETAIL_CONTENT:'${v}',TTL_SECONDS:null}}`;

const ATAQUES = [
  {
    ID: "M1", O_QUE: "o salto cego volta a ser indistinguivel do informado",
    MORTE_ESPERADA: "contrato ausente e contrato IMMUTABLE",
    FICHEIRO: REGRA,
    DE: `    const declarado = rec.DECLARADO;`,
    PARA: `    const declarado = true;`,
    SONDA: sondaRegra(`${DEC("null")}.COBERTURA==='DECLARADA'`),
  },
  {
    ID: "M11", O_QUE: "carimbar UNKNOWN a mao passa a comprar a admissao",
    MORTE_ESPERADA: "UNKNOWN escrito a mao nao compra a admissao",
    FICHEIRO: REGRA,
    DE: `    DECLARADO: r.DETAIL_CONTENT !== "UNKNOWN",`,
    PARA: `    DECLARADO: true,`,
    SONDA: sondaRegra(`m.recolheitaDoContrato('X',${CONT("UNKNOWN")}).DECLARADO===true`),
  },
  {
    ID: "M6", O_QUE: "a porta da Big Collection deixa entrar quem nao declarou",
    MORTE_ESPERADA: "admissivelNaBigCollection bloqueia quem nao declarou",
    FICHEIRO: REGRA,
    DE: `  if (rec.DECLARADO) {
    return {
      ADMISSIVEL: true,`,
    PARA: `  if (true) {
    return {
      ADMISSIVEL: true,`,
    SONDA: sondaRegra(`m.admissivelNaBigCollection('X',null).ADMISSIVEL===true`),
  },
  {
    ID: "M3", O_QUE: "o indice deixa de se revisitar",
    MORTE_ESPERADA: "o indice continua a revisitar-se sempre",
    FICHEIRO: REGRA,
    DE: `  return { DECISAO: "FETCH", PORQUE: "o indice anuncia o que ha de novo; revisita-se sempre" };`,
    PARA: `  return { DECISAO: "SKIP_KNOWN", PORQUE: "o indice anuncia o que ha de novo; revisita-se sempre" };`,
    SONDA: sondaRegra(`m.decidirSobreIndice().DECISAO==='SKIP_KNOWN'`),
  },
  {
    ID: "M7", O_QUE: "um endereco que falhou nunca mais e tentado",
    // Sem isto, um item novo cuja PRIMEIRA visita falhou fica perdido para
    // sempre: o livro tem linha dele, e a linha diz «ja se conhece».
    MORTE_ESPERADA: "resultados sem documento NAO contam",
    FICHEIRO: REGRA,
    DE: `  if (!conhecido || !conhecido.TEM_DOCUMENTO) {`,
    PARA: `  if (!conhecido) {`,
    SONDA: `import('./${REGRA}').then(m=>{const mem=m.memoriaDosDetalhes([{SOURCE_URL:'u',SOURCE_ID:'X',OBSERVATION_RESULT:'TRANSPORT_OR_EMPTY',CAPTURED_AT:'2026-01-01T00:00:00Z'}]);
      process.stdout.write(String(m.decidirSobreDetalhe('u',{memoria:mem,sourceId:'X',contrato:null,agora:'2026-06-01T00:00:00Z'}).DECISAO!=='FETCH'));}).catch(()=>process.stdout.write('erro'));`,
  },
  {
    ID: "M5", O_QUE: "a memoria passa a ser indexada pela identidade, nao pelo endereco",
    // `DOCUMENT_ID` so existe DEPOIS de descarregar. Indexar por ele faz a
    // memoria ficar vazia antes de bater a porta — e tudo vira FETCH.
    MORTE_ESPERADA: "os CINCO resultados com documento contam todos como conhecido",
    FICHEIRO: REGRA,
    DE: `    const url = o && o.SOURCE_URL;`,
    PARA: `    const url = o && o.DOCUMENT_ID;`,
    SONDA: sondaRegra(`mem.size===0`),
  },
  {
    ID: "M8", O_QUE: "tudo o que se conhece passa a ser revisitado",
    MORTE_ESPERADA: "UNNECESSARY_REFETCHES continua ZERO",
    FICHEIRO: REGRA,
    DE: `  if (rec.DETAIL_CONTENT === "MUTABLE") razoes.push("CONTRACT_DECLARES_MUTABLE");`,
    PARA: `  if (rec.DETAIL_CONTENT !== "__nunca__") razoes.push("CONTRACT_DECLARES_MUTABLE");`,
    SONDA: sondaRegra(`${DEC("null")}.DECISAO==='REVALIDATE'`),
  },
  {
    ID: "M10", O_QUE: "o salto conhecido vira ida a rede",
    MORTE_ESPERADA: "nenhum valor de RECOLLECTION faz FETCH",
    FICHEIRO: REGRA,
    DE: `      DECISAO: "SKIP_KNOWN",
      RAZAO: null,
      COBERTURA:`,
    PARA: `      DECISAO: "FETCH",
      RAZAO: null,
      COBERTURA:`,
    SONDA: sondaRegra(`${DEC("null")}.DECISAO==='FETCH'`),
  },
  {
    ID: "M-CENSO", O_QUE: "o censo deixa de contar o salto cego",
    MORTE_ESPERADA: "o censo separa o salto informado do salto cego",
    FICHEIRO: REGRA,
    DE: `      if (d.RECOLLECTION_DECLARADA === false) c.DETAIL_SKIPPED_UNDECLARED++;`,
    PARA: `      if (d.RECOLLECTION_DECLARADA === undefined) c.DETAIL_SKIPPED_UNDECLARED++;`,
    SONDA: sondaRegra(`m.censoDasDecisoes([${DEC("null")}]).DETAIL_SKIPPED_UNDECLARED===0`),
  },
  {
    ID: "M9", O_QUE: "mudanca real em morada estavel nunca e detectada",
    MORTE_ESPERADA: "o TEXTO a mudar => MATERIAL_CHANGE",
    FICHEIRO: NORMAL,
    DE: `  const NORMALIZED_CHANGED = a.NORMALIZED_SHA !== b.NORMALIZED_SHA;`,
    PARA: `  const NORMALIZED_CHANGED = false;`,
    SONDA: sondaNorm(`m.compararConteudo(Buffer.from('<html><p>a</p></html>'),Buffer.from('<html><p>b</p></html>')).VEREDICTO!=='MATERIAL_CHANGE'`),
  },
  {
    ID: "M2/M4", O_QUE: "uma regra volatil alarga-se ate comer o corpo da materia",
    // O defeito que uma lista larga demais produz: a fonte muda, o
    // normalizador apaga a mudanca, e ela passa a parecer imutavel.
    MORTE_ESPERADA: "o TEXTO a mudar => MATERIAL_CHANGE",
    FICHEIRO: NORMAL,
    DE: `    REGRA: /(view-dom-id-)[0-9a-f]{16,}/gi,`,
    PARA: `    REGRA: /(view-dom-id-)?<p>[\\s\\S]*?<\\/p>/gi,`,
    SONDA: sondaNorm(`m.textoNormalizado(Buffer.from('<html><p>materia</p></html>')).TEXTO.includes('materia')===false`),
  },
  {
    ID: "M12", O_QUE: "a canonicalizacao come os cinco caracteres de HTML",
    MORTE_ESPERADA: "os cinco caracteres com significado em HTML",
    FICHEIRO: NORMAL,
    DE: `const NAO_SE_TRADUZ = new Set([34, 38, 39, 60, 62]);`,
    PARA: `const NAO_SE_TRADUZ = new Set([]);`,
    SONDA: sondaNorm(`m.canonicalizarEntidades('&#60;').TEXTO==='<'`),
  },
];

const KILLERS = [
  ["regras/recollection_test.mjs", "as guardas da recollection"],
  ["regras/incrementalidade_test.mjs", "as provas da incrementalidade"],
  ["regras/paridade_test.mjs", "as provas da paridade"],
];

function correr(ficheiro) {
  try {
    execFileSync("node", [ficheiro], { env: AMBIENTE, encoding: "utf8", stdio: "pipe", timeout: 300000 });
    return { verde: true };
  } catch (e) {
    const saida = String(e.stdout || "") + String(e.stderr || "");
    // ⚠️ NAO TRUNCAR A LISTA DE FALHAS, e isto foi medido nesta missao.
    // Com um corte nas 4 primeiras, o ataque M8 derrubava OITO provas e a
    // que interessava era a setima: o arnes nao a via, dava
    // «MORREU PELA PROVA ERRADA» e o relatorio dizia SURVIVOR. O mutante
    // estava morto; quem estava cega era a leitura da morte.
    //
    //     TRUNCAR A EVIDENCIA E FABRICAR UM SOBREVIVENTE.
    return { verde: false, saida: saida.split("\n").filter((l) => /FAIL|FALHA/.test(l)) };
  }
}

function aplicar(a) {
  const t = readFileSync(a.FICHEIRO, "utf8");
  // ⚠️ A ANCORA TEM DE EXISTIR NAS DUAS FORMAS DE FIM DE LINHA — o repo guarda
  // LF e o checkout no Windows devolve CRLF. Uma ancora que nao casa faz o
  // ataque nunca entrar, e o relatorio le-se como SURVIVOR sem ter havido
  // ataque nenhum.
  const lf = a.DE, crlf = a.DE.replace(/\n/g, "\r\n");
  const de = t.includes(lf) ? lf : t.includes(crlf) ? crlf : null;
  if (!de) throw new Error(`ANCORA NAO ENCONTRADA em ${a.FICHEIRO}: ${JSON.stringify(a.DE.slice(0, 60))}`);
  const para = de === crlf ? a.PARA.replace(/\n/g, "\r\n") : a.PARA;
  writeFileSync(a.FICHEIRO, t.replace(de, para));
  return [a.FICHEIRO];
}

const restaurar = (fs_) => execFileSync("git", ["checkout", "--", ...fs_], { encoding: "utf8" });

console.log("══ BASE ════════════════════════════════════════════════════════");
for (const [f, nome] of KILLERS) {
  const r = correr(f);
  console.log(`  ${r.verde ? "VERDE" : "JA VERMELHO (!!)"}  ${nome}`);
  if (!r.verde) { console.log("  a base tem de estar verde antes de atacar"); process.exit(1); }
}

const resultado = [];
for (const a of ATAQUES) {
  console.log(`\n══ ${a.ID} · ${a.O_QUE} ${"═".repeat(Math.max(0, 40 - a.O_QUE.length))}`);
  let ficheiros = [];
  try {
    ficheiros = aplicar(a);

    const diff = execFileSync("git", ["diff", "--stat", "--", ...ficheiros], { encoding: "utf8" }).trim();
    if (!diff) throw new Error("o git nao ve diferenca nenhuma — o ataque nao chegou ao disco");
    console.log(`  diff:   ${diff.split("\n")[0].trim()}`);

    const sonda = execFileSync("node", ["--input-type=module", "-e", a.SONDA],
      { env: AMBIENTE, encoding: "utf8", cwd: process.cwd() }).trim();
    const executou = sonda === "true";
    console.log(`  sonda:  o mutante ${executou ? "CORREU" : "NAO CORREU (!!)"}  [${sonda}]`);
    if (!executou) throw new Error("a sonda nao confirmou o mutante — ver cache de compilacao");

    const mortes = [];
    for (const [f, nome] of KILLERS) {
      const r = correr(f);
      console.log(`  ${r.verde ? "sobreviveu a" : "MORTO por   "} ${nome}`);
      if (!r.verde) mortes.push({ nome, PRIMEIRA_FALHA: (r.saida || [])[0] || "", TODAS: r.saida || [] });
    }
    // ⚠️ MORREU PELA RAZAO CERTA? Um mutante morto por uma prova que nada tem
    // a ver com ele conta como morto e esconde que a prova a serio ficou calada.
    const todas = mortes.map((m) => m.PRIMEIRA_FALHA + " " + (m.TODAS || []).join(" ")).join(" ");
    const razaoCerta = !a.MORTE_ESPERADA || todas.includes(a.MORTE_ESPERADA);
    if (a.MORTE_ESPERADA) console.log(`  razao:  ${razaoCerta ? "morreu pela prova certa" : "MORREU PELA PROVA ERRADA"} [${a.MORTE_ESPERADA}]`);
    resultado.push({ ID: a.ID, O_QUE: a.O_QUE, MUTANTE_EXECUTOU: executou,
      MORTE_ESPERADA: a.MORTE_ESPERADA || null, MORREU_PELA_RAZAO_CERTA: razaoCerta,
      ESTADO: mortes.length && razaoCerta ? "KILLED" : "SURVIVOR", MORTO_POR: mortes });
    console.log(mortes.length && razaoCerta
      ? `  ⇒ KILLED    ${mortes[0].PRIMEIRA_FALHA.trim().slice(0, 90)}`
      : "  ⇒ SURVIVOR  nenhuma prova gritou pela razao certa");
  } catch (e) {
    console.log(`  ERRO no ataque: ${e.message}`);
    resultado.push({ ID: a.ID, O_QUE: a.O_QUE, ESTADO: "ERRO", PORQUE: e.message });
  } finally {
    if (ficheiros.length) restaurar(ficheiros);
  }
}

// ⚠️ `git diff` sem `--cached`: a pergunta e se o DISCO voltou ao indice.
const sujo = execFileSync("git", ["diff", "--name-only", "--", REGRA, NORMAL], { encoding: "utf8" }).trim();
console.log("\n══ RESTAURO ════════════════════════════════════════════════════");
console.log(sujo ? `  ⚠️ FICOU SUJO:\n${sujo}` : "  os ficheiros atacados voltaram ao estado do indice");

const survivors = resultado.filter((r) => r.ESTADO !== "KILLED");
console.log("\n══ VEREDICTO ═══════════════════════════════════════════════════");
console.log(`  ATAQUES: ${resultado.length}   KILLED: ${resultado.length - survivors.length}   RED_TEAM_SURVIVORS: ${survivors.length}`);
for (const s of survivors) console.log(`  SURVIVOR ${s.ID} — ${s.O_QUE}${s.PORQUE ? ` (${s.PORQUE})` : ""}`);

writeFileSync("provas/RECOLLECTION-RED-TEAM-V1.json", JSON.stringify({
  PROVA: "provas/recollection_red_team.mjs",
  PROTOCOLO: "cache-safe §165 adaptado a Node: NODE_DISABLE_COMPILE_CACHE=1, processo novo por ataque, diff provado, sonda a provar execucao, restauro conferido",
  NODE: process.version,
  ATAQUES: resultado.length,
  RED_TEAM_SURVIVORS: survivors.length,
  ARVORE_LIMPA_DEPOIS: sujo === "",
  RESULTADO: resultado,
}, null, 1));
console.log("\n  escrito: provas/RECOLLECTION-RED-TEAM-V1.json");
if (survivors.length || sujo) process.exit(1);
