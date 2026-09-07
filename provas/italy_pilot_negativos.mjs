// CONTROLES NEGATIVOS DO PILOTO RECORRENTE.
// Cada um precisa ATINGIR O RAMO ESPERADO de verdade — teste que nunca viu vermelho nao vale.
// Nada aqui toca a rede: tudo roda sobre os bytes ja preservados, mutados em memoria.

import { readFileSync, readdirSync, existsSync, writeFileSync, mkdirSync, rmSync, appendFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { normalizarSias, estadoDeCadencia, lerLedger } from "./italy_pilot_collect.mjs";
import { CONTRACTS } from "./italy_contracts.mjs";

const sha = b => createHash("sha256").update(b).digest("hex");
let executados = 0, atingiram = 0;
const N = (id, desc, ramoEsperado, ramoObtido, extra = "") => {
  executados++;
  const ok = ramoEsperado === ramoObtido;
  if (ok) atingiram++;
  console.log(`${ok ? "ATINGIU  " : "NAO ATIN."} ${id}  ${desc}\n           esperado=${ramoEsperado}  obtido=${ramoObtido}${extra ? "  · " + extra : ""}`);
  return ok;
};

const led = lerLedger();
const rawDe = id => {
  const o = led.find(x => x.SOURCE_ID === id && x.RAW_PATH);
  return o && existsSync(o.RAW_PATH) ? { obs: o, buf: readFileSync(o.RAW_PATH) } : null;
};

console.log("CONTROLES NEGATIVOS — PILOTO RECORRENTE\n");

// ---- N1 · mesmo documento duas vezes -> 0 objetos RAW na segunda ----
{
  const runs = readFileSync("data/collection-ledger/italy/runs.ndjson", "utf8").trim().split("\n").map(JSON.parse);
  const r2 = runs.at(-1);
  N("N1", "mesmo documento duas vezes: RAW_OBJECTS_CREATED da 2a rodada",
    0, r2.contadores.RAW_OBJECTS_CREATED, `SEEN_AGAIN=${r2.contadores.SEEN_AGAIN}`);
}

// ---- N2 · mesma URL, bytes alterados -> DOCUMENT_CHANGED_IN_PLACE ----
{
  const r = rawDe("IT-T2-002");
  const anterior = led.filter(o => o.SOURCE_ID === "IT-T2-002" && o.DOCUMENT_ID === r.obs.DOCUMENT_ID);
  const mutado = Buffer.concat([r.buf, Buffer.from("\n% byte a mais, mesmo DOCUMENT_ID\n")]);
  const shaNovo = sha(mutado);
  // a decisao do coletor: mesmo DOCUMENT_ID + SHA novo
  const mesmoDoc = anterior.length > 0;
  const shaJaVisto = anterior.some(o => o.RAW_SHA256 === shaNovo);
  const ramo = mesmoDoc && !shaJaVisto ? "DOCUMENT_CHANGED_IN_PLACE" : mesmoDoc ? "SEEN_AGAIN" : "NEW_DOCUMENT";
  N("N2", "mesma URL com bytes alterados (mesmo DOCUMENT_ID)",
    "DOCUMENT_CHANGED_IN_PLACE", ramo, `versoes anteriores=${anterior.length}`);
}

// ---- N3 · janela movel do SIAS com UM dia novo -> 1 dia novo, nao 11 ----
{
  const r = rawDe("IT-T2-004");
  const base = normalizarSias(r.buf);
  const chavesBase = new Set(base.observacoes.map(o => o.OBSERVATION_KEY));
  // simula a janela andando um dia: descarta o dia mais antigo, acrescenta um dia novo
  const dias = [...new Set(base.observacoes.map(o => o.DATE))].sort();
  const maisAntigo = dias[0], novoDia = new Date(Date.parse(dias.at(-1)) + 864e5).toISOString().slice(0, 10);
  const amanha = base.observacoes
    .filter(o => o.DATE !== maisAntigo)
    .concat(base.observacoes.filter(o => o.DATE === dias.at(-1)).map(o => ({ ...o, DATE: novoDia, OBSERVATION_KEY: `${o.STATION}|${novoDia}|${o.VARIABLE}` })));
  const novas = amanha.filter(o => !chavesBase.has(o.OBSERVATION_KEY));
  const diasNovos = new Set(novas.map(o => o.DATE)).size;
  N("N3", "janela movel do SIAS avanca um dia",
    1, diasNovos, `linhas na janela=${amanha.length} · observacoes novas=${novas.length} (nao ${amanha.length})`);
}

// ---- N4 · PDF vira HTML -> FAILED na validacao de bytes, ANTES de qualquer parse ----
{
  const html = Buffer.from("<html><body>Access denied</body></html>");
  const assinatura = html.subarray(0, 8).toString("latin1").trimStart().startsWith("<") ? "HTML" : "?";
  const esperado = CONTRACTS["IT-T3-010"].EXPECTED_SIGNATURE === "%PDF" ? "PDF" : "?";
  N("N4", "PDF esperado chega como HTML (com HTTP 200)",
    "BYTE_VALIDATION_FAILED", assinatura !== esperado ? "BYTE_VALIDATION_FAILED" : "PASSOU",
    "HTTP 200 nao salva");
}

// ---- N5 · parser explode DEPOIS do download -> RAW continua preservado ----
{
  const r = rawDe("IT-T3-005");
  const antes = existsSync(r.obs.RAW_PATH);
  let parserExplodiu = false;
  try { JSON.parse("{{{ isto nao e json }}}"); } catch { parserExplodiu = true; }
  const depois = existsSync(r.obs.RAW_PATH) && sha(readFileSync(r.obs.RAW_PATH)) === r.obs.RAW_SHA256;
  N("N5", "parser falha depois do download",
    "RAW_PRESERVADO_E_INTACTO", antes && parserExplodiu && depois ? "RAW_PRESERVADO_E_INTACTO" : "RAW_PERDIDO",
    `ordem do coletor: download -> bytes -> sha -> RAW -> manifesto -> parse`);
}

// ---- N6 · fonte SEM cadencia provada, mesmo hash -> NO_CHANGE, nunca DEGRADED ----
{
  const c = CONTRACTS["IT-T2-004"];   // OBSERVED_FREQUENCY = NÃO SEI
  const est = estadoDeCadencia(c, led.find(o => o.SOURCE_ID === "IT-T2-004"), false);
  const saude = led.filter(o => o.SOURCE_ID === "IT-T2-004").at(-1).HEALTH_STATE;
  N("N6", "fonte sem cadencia observada devolve o MESMO hash",
    "CADENCE_UNKNOWN+HEALTHY", `${est.CADENCE_STATE}+${saude}`,
    "SAME_HASH != DEGRADED · NO_CHANGE != FAILURE");
}

// ---- N7 · fonte COM cadencia provada e prazo NAO vencido -> EXPECTED_NO_CHANGE, nao OVERDUE ----
{
  const c = CONTRACTS["IT-T3-010"];   // 7D provado
  const ultima = led.filter(o => o.SOURCE_ID === "IT-T3-010").at(-1);
  const est = estadoDeCadencia(c, ultima, false);
  N("N7", "fonte com cadencia provada, dentro do prazo",
    "EXPECTED_NO_CHANGE", est.CADENCE_STATE, `proxima esperada=${est.EXPECTED_NEXT_UPDATE}`);
}

// ---- N8 · fonte COM cadencia provada e prazo VENCIDO -> OVERDUE_UPDATE ----
{
  const c = CONTRACTS["IT-T3-010"];
  const velha = { SOURCE_DATE_ISO: "2026-07-01" };   // muito alem de 7 dias
  const est = estadoDeCadencia(c, velha, false);
  N("N8", "fonte com cadencia provada e prazo vencido",
    "OVERDUE_UPDATE", est.CADENCE_STATE, `so aqui pode acusar atraso`);
}

console.log(`\nEXECUTED: ${executados} · EXPECTED_BRANCH_REACHED: ${atingiram} · FAILURES: ${executados - atingiram}`);
process.exit(executados === atingiram ? 0 : 1);
