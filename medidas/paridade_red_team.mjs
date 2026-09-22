// RED TEAM DA PARIDADE — oito ataques ao codigo QUE ESTA MISSAO ESCREVEU.
//
//     node medidas/paridade_red_team.mjs
//
// A pergunta nao e «o codigo funciona?». E: «se alguem o desligar, alguma
// prova grita?». Um mutante que sobrevive e uma prova que nao prova nada.
//
// ⚠️ PROTOCOLO CACHE-SAFE (§165 do know-how), traduzido para Node.
// O §165 fala de `__pycache__` e `PYTHONDONTWRITEBYTECODE` porque foi escrito
// contra Python. Aqui o codigo e `.mjs`, e a armadilha equivalente e a cache
// de compilacao do Node (`NODE_COMPILE_CACHE`) e a cache de modulos DENTRO do
// processo. As duas fecham-se da mesma maneira:
//
//   1 · `NODE_DISABLE_COMPILE_CACHE=1` e `NODE_COMPILE_CACHE` apagado
//   2 · PROCESSO NOVO por ataque — nunca `import()` duas vezes no mesmo
//   3 · provar o DIFF (o ficheiro em disco mudou mesmo)
//   4 · provar que O MUTANTE CORREU (uma sonda le o modulo mutado e confirma
//       que o que carregou foi a versao estragada, e nao a boa em cache)
//
// O ponto 4 e o que separa isto de um teatro. Ja se mediu nesta casa um
// mutante do MESMO TAMANHO a passar por SURVIVOR so porque o interpretador
// serviu bytecode velho: o ataque aparecia no `git diff` e nunca chegava a
// correr.
//
// ⚠️ E O RESTAURO E FINALLY, SEMPRE. Um ataque que rebente a meio nao pode
// deixar o defeito escrito no repositorio.

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";

const COLETOR = "coleta/italy_pilot_collect.mjs";
const NORMAL = "regras/normalizacao_de_conteudo.mjs";
const REGRA = "regras/incrementalidade.mjs";

const AMBIENTE = { ...process.env, NODE_DISABLE_COMPILE_CACHE: "1" };
delete AMBIENTE.NODE_COMPILE_CACHE;

// ── OS OITO ATAQUES ────────────────────────────────────────────────────────
// `SONDA` corre no estado MUTADO e tem de devolver `true` — e ela que prova
// que o codigo estragado foi mesmo o que o Node carregou.
const ATAQUES = [
  {
    ID: "M1", O_QUE: "desligar o pre-fetch skip",
    // ⚠️ A sonda deste ataque so consegue ler o ficheiro — o `if` mutado vive
    // dentro do laco e nao se ve de fora. Quem prova que o mutante CORREU e
    // esta prova de COMPORTAMENTO: ela arranca o coletor num processo novo,
    // faz duas rodadas e conta as idas ao transporte. Se a contagem mudar, o
    // codigo estragado correu — e isso e prova a serio, nao um git diff.
    MORTE_ESPERADA: "RUN2 NAO BATE A PORTA",
    FICHEIRO: COLETOR,
    DE: `      if (decisao.DECISAO === "SKIP_KNOWN") {`,
    PARA: `      if (false && decisao.DECISAO === "SKIP_KNOWN") {`,
    SONDA: `const {readFileSync:R}=await import('node:fs');const f=R('${COLETOR}','utf8');
            process.stdout.write(String(f.includes('if (false && decisao.DECISAO')));`,
  },
  {
    ID: "M2", O_QUE: "forcar FETCH em todo o endereco conhecido",
    FICHEIRO: REGRA,
    DE: `  if (razoes.length === 0) {`,
    PARA: `  if (false) {`,
    SONDA: `import('./${REGRA}').then(async m=>{
            const mem=m.memoriaDosDetalhes([{SOURCE_URL:'u',OBSERVATION_RESULT:'NEW_DOCUMENT',CAPTURED_AT:'2026-01-01T00:00:00Z'}]);
            process.stdout.write(String(m.decidirSobreDetalhe('u',{memoria:mem}).DECISAO!=='SKIP_KNOWN'));});`,
  },
  {
    ID: "M3", O_QUE: "deixar o contador de visitas alterar o hash semantico",
    FICHEIRO: NORMAL,
    // A regra fica escrita, com nome e tudo — e deixa de casar. E o ataque
    // mais realista dos oito: ninguem a apaga, so lhe muda uma palavra.
    DE: `    REGRA: /(<div[^>]*class="[^"]*\\bviews\\b[^"]*"[^>]*>)\\s*\\d[\\d.,\\s]*(\\s*<)/gi,`,
    PARA: `    REGRA: /(<div[^>]*class="[^"]*\\bNUNCA_CASA_NADA\\b[^"]*"[^>]*>)\\s*\\d(\\s*<)/gi,`,
    SONDA: `import('./${NORMAL}').then(m=>{
            const p=b=>Buffer.from('<html><body><div class="views">'+b+'</div><p>x</p></body></html>');
            process.stdout.write(String(m.compararConteudo(p(1),p(2)).VEREDICTO==='MATERIAL_CHANGE'));});`,
  },
  {
    ID: "M4", O_QUE: "fazer o normalizador apagar a mudanca real",
    FICHEIRO: NORMAL,
    // O normalizador passa a comer os paragrafos — ou seja, o corpo da
    // materia. E o defeito que uma lista de volateis demasiado larga produz.
    DE: `  let texto = bytes.toString("latin1");`,
    PARA: `  let texto = bytes.toString("latin1").replace(/<p[\\s\\S]*?<\\/p>/gi, "");`,
    SONDA: `import('./${NORMAL}').then(m=>{
            const p=b=>Buffer.from('<html><body><p>'+b+'</p></body></html>');
            process.stdout.write(String(m.compararConteudo(p('alfa'),p('beta')).VEREDICTO!=='MATERIAL_CHANGE'));});`,
  },
  {
    ID: "M5", O_QUE: "transformar TODO o CHANGED_IN_PLACE em SEEN_AGAIN",
    MORTE_ESPERADA: "uma palavra da materia muda",
    FICHEIRO: COLETOR,
    DE: `        if (conteudo && conteudo.VEREDICTO === "VOLATILE_ONLY" && !conteudo.AVISO) {`,
    PARA: `        if (true) {`,
    SONDA: `const {readFileSync:R}=await import('node:fs');const f=R('${COLETOR}','utf8');
            process.stdout.write(String(f.includes('        if (true) {')));`,
  },
  {
    ID: "M6", O_QUE: "desligar a normalizacao inteira",
    FICHEIRO: NORMAL,
    DE: `  if (!pareceHtml(bytes)) {`,
    PARA: `  if (true) {`,
    SONDA: `import('./${NORMAL}').then(m=>{
            process.stdout.write(String(m.normalizarConteudo(Buffer.from('<html><p>x</p></html>')).NORMALIZACAO==='NOT_APPLICABLE'));});`,
  },
  {
    ID: "M7", O_QUE: "decidir so por RAW_SHA, ignorando o normalizado",
    FICHEIRO: NORMAL,
    DE: `  const NORMALIZED_CHANGED = a.NORMALIZED_SHA !== b.NORMALIZED_SHA;`,
    PARA: `  const NORMALIZED_CHANGED = a.RAW_SHA256 !== b.RAW_SHA256;`,
    SONDA: `import('./${NORMAL}').then(m=>{
            const p=b=>Buffer.from('<html><body><div class="views">'+b+'</div><p>x</p></body></html>');
            process.stdout.write(String(m.compararConteudo(p(1),p(2)).NORMALIZED_CHANGED===true));});`,
  },
  {
    ID: "M8", O_QUE: "dedup pos-download em vez de skip antes do pedido",
    MORTE_ESPERADA: "RUN2 NAO BATE A PORTA",
    FICHEIRO: COLETOR,
    // Move-se a decisao para DEPOIS do download: a rede ja foi gasta, e o
    // salto passa a ser dedup. O contador de rede denuncia-o.
    DE: `      const decisao = decidirSobreDetalhe(alvo.url, {`,
    // ⚠️ O ATAQUE TEM DE SER FIEL AO DEFEITO, e a primeira versao NAO era.
    // Ela punha um `baixar()` extra so no caminho com rede, e a bancada corre
    // sem rede — o mutante nao mexia em nada que a prova offline pudesse ver,
    // e lia-se como SURVIVOR. «Dedup pos-download» e OUTRA coisa: os bytes
    // chegam PRIMEIRO, e so depois alguem pergunta se ja os tinha. E assim
    // que se escreve, e assim a prova de duas rodadas conta a ida a mais.
    PARA: `      const _pre = forcarBuf ? { buf: forcarBuf(sourceId, alvo), status: 200, tentativas: 1 } : await baixar(alvo.url);
      const decisao = decidirSobreDetalhe(alvo.url, {`,
    EXTRA: { DE: `      const r = forcarBuf ? { buf: forcarBuf(sourceId, alvo), status: 200, tentativas: 1 } : await baixar(alvo.url);`,
             PARA: `      const r = _pre;` },
    SONDA: `const {readFileSync:R}=await import('node:fs');const f=R('${COLETOR}','utf8');
            process.stdout.write(String(f.indexOf('const _pre = forcarBuf ? { buf:')>0 && f.indexOf('const r = _pre;')>0));`,
  },
];

const KILLERS = [
  ["regras/paridade_test.mjs", "as provas da paridade"],
  ["provas/paridade_duas_rodadas.mjs", "a prova de duas rodadas"],
];

function correr(ficheiro) {
  try {
    execFileSync("node", [ficheiro], { env: AMBIENTE, encoding: "utf8", stdio: "pipe", timeout: 300000 });
    return { verde: true };
  } catch (e) {
    return { verde: false, saida: String(e.stdout || "").split("\n").filter(l => l.includes("FALHA")).slice(0, 3) };
  }
}

function aplicar(a) {
  const alvos = [{ F: a.FICHEIRO, DE: a.DE, PARA: a.PARA }];
  if (a.EXTRA) alvos.push({ F: a.EXTRA.FICHEIRO || a.FICHEIRO, DE: a.EXTRA.DE, PARA: a.EXTRA.PARA });
  for (const x of alvos) {
    const t = readFileSync(x.F, "utf8");
    // ⚠️ A ANCORA TEM DE EXISTIR NAS DUAS FORMAS DE FIM DE LINHA.
    // O repositorio guarda LF e o Windows devolve CRLF ao fazer checkout —
    // ou seja, a partir do PRIMEIRO restauro os ficheiros no disco tem `\r\n`
    // e uma ancora escrita com `\n` deixa de casar. O ataque nao entra, o
    // mutante nao corre, e o relatorio le-se como SURVIVOR quando na verdade
    // nunca houve ataque nenhum. Ja se perdeu tempo nesta casa por isto.
    const lf = x.DE, crlf = x.DE.replace(/\n/g, "\r\n");
    const de = t.includes(lf) ? lf : t.includes(crlf) ? crlf : null;
    if (!de) throw new Error(`ANCORA NAO ENCONTRADA em ${x.F} (nem LF nem CRLF): ${JSON.stringify(x.DE.slice(0, 70))}`);
    const para = de === crlf ? x.PARA.replace(/\n/g, "\r\n") : x.PARA;
    writeFileSync(x.F, t.replace(de, para));
  }
  return [...new Set(alvos.map((x) => x.F))];
}

function restaurar(ficheiros) {
  // `git checkout --` devolve o ficheiro rastreado ao que o indice diz. Os
  // tres ficheiros atacados sao rastreados; se algum nao estiver, isto
  // rebenta em vez de deixar o defeito escrito — e rebentar e o certo.
  execFileSync("git", ["checkout", "--", ...ficheiros], { encoding: "utf8" });
}

// ── BASE: os killers tem de estar VERDES antes de qualquer ataque ─────────
// Sem esta medicao, um vermelho pre-existente faz TODOS os mutantes
// parecerem mortos e o relatorio sai a mentir a nosso favor.
console.log("══ BASE — os killers antes de qualquer ataque ═══════════════════");
let baseOk = true;
for (const [f, nome] of KILLERS) {
  const r = correr(f);
  console.log(`  ${r.verde ? "VERDE" : "VERMELHO"}  ${nome}  (${f})`);
  if (!r.verde) { baseOk = false; console.log("   ", (r.saida || []).join("\n    ")); }
}
if (!baseOk) {
  console.log("\n  A BASE JA ESTA VERMELHA. Um red team sobre base vermelha nao mede nada.");
  process.exit(1);
}

// ── OS ATAQUES ─────────────────────────────────────────────────────────────
const resultado = [];
for (const a of ATAQUES) {
  console.log(`\n══ ${a.ID} · ${a.O_QUE} ${"═".repeat(Math.max(0, 44 - a.O_QUE.length))}`);
  let ficheiros = [];
  try {
    ficheiros = aplicar(a);

    // 3 · PROVAR O DIFF
    const diff = execFileSync("git", ["diff", "--stat", "--", ...ficheiros], { encoding: "utf8" }).trim();
    if (!diff) throw new Error("o git nao ve diferenca nenhuma — o ataque nao chegou ao disco");
    console.log(`  diff:   ${diff.split("\n")[0].trim()}`);

    // 4 · PROVAR QUE O MUTANTE CORREU
    const sonda = execFileSync("node", ["--input-type=module", "-e", a.SONDA],
      { env: AMBIENTE, encoding: "utf8", cwd: process.cwd() }).trim();
    const executou = sonda === "true";
    console.log(`  sonda:  o mutante ${executou ? "CORREU" : "NAO CORREU (!!)"}  [${sonda}]`);
    if (!executou) throw new Error("a sonda nao confirmou o mutante — ver cache de compilacao");

    // O ataque
    const mortes = [];
    for (const [f, nome] of KILLERS) {
      const r = correr(f);
      console.log(`  ${r.verde ? "sobreviveu a" : "MORTO por   "} ${nome}`);
      if (!r.verde) mortes.push({ nome, PRIMEIRA_FALHA: (r.saida || [])[0] || "", TODAS: r.saida || [] });
    }
    // ⚠️ MORREU PELA RAZAO CERTA? Um mutante morto por uma prova que nada
    // tem a ver com ele conta como morto e esconde que a prova a serio ficou
    // calada. Onde o ataque declara `MORTE_ESPERADA`, ela tem de aparecer.
    const todas = mortes.map((m) => m.PRIMEIRA_FALHA + " " + (m.TODAS || []).join(" ")).join(" ");
    const razaoCerta = !a.MORTE_ESPERADA || todas.includes(a.MORTE_ESPERADA);
    if (a.MORTE_ESPERADA) {
      console.log(`  razao: ${razaoCerta ? "morreu pela prova certa" : "MORREU PELA PROVA ERRADA"} [${a.MORTE_ESPERADA}]`);
    }
    resultado.push({ ID: a.ID, O_QUE: a.O_QUE, MUTANTE_EXECUTOU: executou,
      MORTE_ESPERADA: a.MORTE_ESPERADA ?? null, MORREU_PELA_RAZAO_CERTA: razaoCerta,
      ESTADO: mortes.length && razaoCerta ? "KILLED" : "SURVIVOR", MORTO_POR: mortes });
    if (mortes.length && razaoCerta) console.log(`  ⇒ KILLED    ${mortes[0].PRIMEIRA_FALHA.trim()}`);
    else console.log("  ⇒ SURVIVOR  nenhuma prova gritou pela razao certa");
  } catch (e) {
    console.log(`  ERRO no ataque: ${e.message}`);
    resultado.push({ ID: a.ID, O_QUE: a.O_QUE, ESTADO: "ERRO", PORQUE: e.message });
  } finally {
    if (ficheiros.length) restaurar(ficheiros);
  }
}

// ── O RESTAURO CONFERE-SE, NAO SE ASSUME ──────────────────────────────────
// ⚠️ `git status --porcelain` NAO SERVE AQUI, e engana de forma silenciosa:
// ele mostra tambem o que esta no INDICE contra o HEAD — ficheiros novos
// desta missao aparecem como `A` e uma alteracao ja adicionada como `M`,
// mesmo com a arvore limpa. O que se quer saber e outra coisa: o disco ficou
// igual ao indice depois do restauro? Isso e `git diff` sem `--cached`.
const sujo = execFileSync("git", ["diff", "--name-only", "--", COLETOR, NORMAL, REGRA], { encoding: "utf8" }).trim();
console.log(`\n══ RESTAURO ════════════════════════════════════════════════════`);
console.log(sujo ? `  ⚠️ FICOU SUJO:\n${sujo}` : "  os tres ficheiros atacados voltaram ao estado do indice");

const survivors = resultado.filter((r) => r.ESTADO !== "KILLED");
console.log(`\n══ VEREDICTO ═══════════════════════════════════════════════════`);
console.log(`  ATAQUES: ${resultado.length}   KILLED: ${resultado.length - survivors.length}   SURVIVORS: ${survivors.length}`);
for (const s of survivors) console.log(`  SURVIVOR ${s.ID} — ${s.O_QUE}${s.PORQUE ? ` (${s.PORQUE})` : ""}`);

writeFileSync("medidas/PARIDADE-RED-TEAM-V1.json", JSON.stringify({
  MEDIDOR: "medidas/paridade_red_team.mjs",
  PROTOCOLO: "cache-safe §165 adaptado a Node: NODE_DISABLE_COMPILE_CACHE=1, processo novo por ataque, diff provado, sonda a provar execucao",
  NODE: process.version,
  ATAQUES: resultado.length,
  RED_TEAM_SURVIVORS: survivors.length,
  ARVORE_LIMPA_DEPOIS: sujo === "",
  RESULTADO: resultado,
}, null, 1));
console.log("\n  escrito: medidas/PARIDADE-RED-TEAM-V1.json");
if (survivors.length || sujo) process.exit(1);
