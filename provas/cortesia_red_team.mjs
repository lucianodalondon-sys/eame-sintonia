// RED TEAM DA CORTESIA — desligar cada guarda de `baixar()` e ver a prova morrer.
//
//     node provas/cortesia_red_team.mjs [K1 K4 ...]
//
// A pergunta e a do red team da recollection: «se alguem desligar isto, alguma
// prova grita?». Cada ataque muda UMA linha de `coleta/italy_pilot_collect.mjs`,
// corre `provas/cortesia_http_local.mjs` num processo novo e exige que ela
// FALHE. Um mutante que sobrevive e uma guarda que nenhuma prova ve.
//
// PROTOCOLO (§165, o mesmo de `provas/recollection_red_team.mjs`):
//   1 · NODE_DISABLE_COMPILE_CACHE=1 e NODE_COMPILE_CACHE apagado
//   2 · PROCESSO NOVO por ataque
//   3 · provar o DIFF: a ancora (DE) tem de existir UMA vez, e o ficheiro mutado
//       tem de diferir do original
//   4 · provar que O MUTANTE CORREU: o texto mutado escreve um ficheiro-bandeira
//       (`MUTANTE_BANDEIRA`) na hora em que a linha mutada executa. Mutante que
//       morre sem bandeira e NAO_EXECUTOU — nunca se conta como apanhado.
//   5 · restaurar em `finally`, e CONFERIR o restauro no fim (sha igual)
import { readFileSync, writeFileSync, existsSync, rmSync, mkdtempSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { tmpdir } from "node:os";
import { join } from "node:path";

const ALVO = "coleta/italy_pilot_collect.mjs";
const PROVA = "provas/cortesia_http_local.mjs";
const BANDEIRA = join(mkdtempSync(join(tmpdir(), "cortesia-rt-")), "mutante.correu");
// A bandeira: uma expressao que escreve o ficheiro e devolve `true`, para caber
// dentro de uma condicao sem mudar o resto dela.
const B = `(writeFileSync(process.env.MUTANTE_BANDEIRA, "1"), true)`;

const ATAQUES = [
  { ID: "K1", O_QUE: "o robots deixa de ser respeitado (caminho proibido e pedido)",
    DE: `  if (rb.estado === "LIDO" && !robotsPermite(rb.grupos, u.pathname + u.search))`,
    PARA: `  if (${B} && false && rb.estado === "LIDO" && !robotsPermite(rb.grupos, u.pathname + u.search))` },
  { ID: "K2", O_QUE: "robots ilegivel passa a valer como permissao",
    DE: `  if (rb.estado === "ILEGIVEL") return { recusado: "ROBOTS_ILEGIVEL", porque: rb.porque };`,
    PARA: `  if (rb.estado === "ILEGIVEL" && ${B} && false) return { recusado: "ROBOTS_ILEGIVEL", porque: rb.porque };` },
  { ID: "K3", O_QUE: "robots indisponivel passa a valer como permissao",
    DE: `  if (rb.estado === "INDISPONIVEL") return { recusado: "ROBOTS_INDISPONIVEL", porque: rb.porque };`,
    PARA: `  if (rb.estado === "INDISPONIVEL" && ${B} && false) return { recusado: "ROBOTS_INDISPONIVEL", porque: rb.porque };` },
  { ID: "K4", O_QUE: "a pausa entre pedidos ao mesmo host desaparece",
    DE: `  const minimo = Math.max(CORTESIA.cfg.PAUSA_S, crawlDelay || 0) * 1000;`,
    PARA: `  const minimo = ${B} ? 0 : 0;` },
  { ID: "K5", O_QUE: "o Crawl-delay do robots deixa de mandar",
    DE: `  const minimo = Math.max(CORTESIA.cfg.PAUSA_S, crawlDelay || 0) * 1000;`,
    PARA: `  const minimo = ${B} && CORTESIA.cfg.PAUSA_S * 1000;` },
  { ID: "K6", O_QUE: "o teto de pedidos por host desaparece",
    DE: `const tetoAtingido = host => (CORTESIA.porHost.get(host) || 0) >= CORTESIA.cfg.TETO_POR_HOST;`,
    PARA: `const tetoAtingido = host => ${B} && false;` },
  { ID: "K7", O_QUE: "o salto de redireccionamento deixa de pedir licenca",
    DE: `    const lic = await licenca(atual);`,
    PARA: `    const lic = salto > 0 && ${B} ? { host: new URL(atual).hostname, crawlDelay: null } : await licenca(atual);` },
  { ID: "K8", O_QUE: "o robots volta a ser lido a cada pedido (sem cache por corrida)",
    DE: `    if (rb.estado !== "INDISPONIVEL") CORTESIA.robots.set(u.origin, rb);`,
    PARA: `    if (rb.estado !== "INDISPONIVEL" && ${B} && false) CORTESIA.robots.set(u.origin, rb);` },
  { ID: "K9", O_QUE: "INDISPONIVEL fica em cache (um soluco vira proibicao da corrida)",
    DE: `    if (rb.estado !== "INDISPONIVEL") CORTESIA.robots.set(u.origin, rb);`,
    PARA: `    if (${B}) CORTESIA.robots.set(u.origin, rb);` },
  { ID: "K10", O_QUE: "a materia recusada volta a contar como pedido e a ir ao livro",
    DE: `      if (r.recusado && !r.foiARede) {`,
    PARA: `      if (r.recusado && !r.foiARede && ${B} && false) {` },
  { ID: "K11", O_QUE: "o indice recusado volta a ser falha da fonte, escrita no livro",
    DE: `    if (alvos?.erro && String(alvos.erro).includes("CORTESIA ")) {`,
    PARA: `    if (alvos?.erro && ${B} && false) {` },
  { ID: "K12", O_QUE: "a pausa configurada e ignorada",
    DE: `  return { PAUSA_S: ler("SINTONIA_PAUSA_POR_HOST_S", CORTESIA_PADRAO.PAUSA_S), TETO_POR_HOST,`,
    PARA: `  return { PAUSA_S: ${B} && CORTESIA_PADRAO.PAUSA_S, TETO_POR_HOST,` },
  { ID: "K13", O_QUE: "o teto configurado e ignorado",
    DE: `  const TETO_POR_HOST = ler("SINTONIA_TETO_POR_HOST", CORTESIA_PADRAO.TETO_POR_HOST);`,
    PARA: `  const TETO_POR_HOST = ${B} && CORTESIA_PADRAO.TETO_POR_HOST;` },
  { ID: "K14", O_QUE: "a configuracao invalida passa em silencio",
    DE: `    if (!Number.isFinite(n) || n < 0) throw new Error(\`CORTESIA_INVALIDA: \${nome}=\${v}\`);`,
    PARA: `    if (!Number.isFinite(n) || n < 0) { ${B}; return omissao; }` },
  { ID: "K15", O_QUE: "o pedido recusado conta como ida a rede (REDE.total inventa indices)",
    DE: `    if (!foiARede) { REDE.total++; foiARede = true; }`,
    PARA: `    if (!foiARede) { REDE.total++; foiARede = true; }`,
    ANTES_DE: `    const lic = await licenca(atual);`,
    INSERIR: `    if (${B}) REDE.total++;` },
];

const pedidos = process.argv.slice(2);
const escolhidos = pedidos.length ? ATAQUES.filter(a => pedidos.includes(a.ID)) : ATAQUES;
const ORIGINAL = readFileSync(ALVO, "utf8");
const shaOriginal = createHash("sha256").update(ORIGINAL).digest("hex");
const AMBIENTE = { ...process.env, NODE_DISABLE_COMPILE_CACHE: "1", MUTANTE_BANDEIRA: BANDEIRA };
delete AMBIENTE.NODE_COMPILE_CACHE;
for (const k of ["SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST"]) delete AMBIENTE[k];

const resultados = [];
try {
  for (const a of escolhidos) {
    const ancora = a.ANTES_DE ?? a.DE;
    const n = ORIGINAL.split(ancora).length - 1;
    if (n !== 1) { resultados.push({ ...a, VEREDICTO: `ANCORA_${n}_VEZES` }); continue; }
    const mutado = a.INSERIR ? ORIGINAL.replace(ancora, `${a.INSERIR}\n${ancora}`) : ORIGINAL.replace(a.DE, a.PARA);
    if (mutado === ORIGINAL) { resultados.push({ ...a, VEREDICTO: "SEM_DIFF" }); continue; }
    rmSync(BANDEIRA, { force: true });
    writeFileSync(ALVO, mutado);
    let x;
    try {
      x = spawnSync(process.execPath, [PROVA], { env: AMBIENTE, encoding: "utf8", timeout: 600000 });
    } finally {
      writeFileSync(ALVO, ORIGINAL);
    }
    const correu = existsSync(BANDEIRA);
    const morreu = x.status !== 0;
    const falhas = (x.stdout || "").split("\n").filter(l => l.startsWith("  FALHA")).map(l => l.trim());
    const veredicto = !correu ? "NAO_EXECUTOU" : morreu ? "MORTO" : "SOBREVIVEU";
    resultados.push({ ID: a.ID, O_QUE: a.O_QUE, VEREDICTO: veredicto, CODIGO: x.status,
                      MORTO_POR: falhas.slice(0, 3) });
    console.log(`${a.ID.padEnd(4)} ${veredicto.padEnd(12)} ${a.O_QUE}${falhas.length ? `\n       <- ${falhas[0]}` : ""}`);
  }
} finally {
  writeFileSync(ALVO, ORIGINAL);
}
const restaurado = createHash("sha256").update(readFileSync(ALVO, "utf8")).digest("hex") === shaOriginal;
const mortos = resultados.filter(r => r.VEREDICTO === "MORTO").length;
console.log(`\nCORTESIA_RED_TEAM · ataques=${resultados.length} mortos=${mortos} restaurado=${restaurado}`);
if (process.env.CORTESIA_RT_JSON) writeFileSync(process.env.CORTESIA_RT_JSON, JSON.stringify({
  DATASET: "CORTESIA-RED-TEAM-V1", ALVO, PROVA, SHA256_DO_ALVO: shaOriginal,
  ATAQUES: resultados, MORTOS: mortos, TOTAL: resultados.length, RESTAURADO: restaurado }, null, 1) + "\n");
process.exit(mortos === resultados.length && restaurado ? 0 : 1);
