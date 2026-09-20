// SINTONIA EAME — O REGISTRY DE ADAPTERS DE AQUISIÇÃO
//
// O QUE ISTO É, E O QUE NÃO É
// ----------------------------
// `regras/motor_de_rota.mjs` tem três estratégias declarativas e uma porta de
// saída, `CUSTOM_ADAPTER`: o contrato NOMEIA um adapter registado aqui, e o
// despachador central continua sem conhecer SOURCE_ID nenhum.
//
// Este registry nasceu VAZIO e assim ficou até ao cutover dos sete `case`.
// Ao migrar `IT-T3-008`, mediu-se UM comportamento que o vocabulário finito
// não descreve sem inventar providers de relógio: quando o índice não anuncia
// o boletim, o `case` sondava a rota previsível para trás a partir de hoje,
// combinando data e número de edição, e aceitava o primeiro PDF real.
//
//     UM ADAPTER É A CONFISSÃO DE QUE A LÓGICA NÃO CABE NO VOCABULÁRIO.
//     NÃO É UM SÍTIO PARA ESCONDER SOURCE_ID.
//
// Por isso cada adapter lê os seus parâmetros do BLOCO do contrato (`aq`), e
// não de constantes suas. Nada aqui sabe que existe uma Puglia.
//
// A lei do motor vale aqui: sem `eval`, sem `Function`, sem processo filho.
// A rede entra por `buscar`, injectada; o dia entra por `agora`, injectado.

const pad2 = (n) => String(n).padStart(2, "0");

// Semana ISO-8601 de uma data (UTC). Medido nos boletins da ARIF Puglia:
// N35 = 26/08/2026, N36 = 02/09, N37 = 09/09, N38 = 16/09 — quatro de quatro
// coincidem com a semana ISO da data. É esta a regra que `NUMEROS.RULE =
// "ISO_WEEK"` declara; o contrato diz que a usa, e o ledger continua a poder
// provar o contrário se um dia a fonte saltar um número.
export function semanaIso(d) {
  const t = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  const dia = t.getUTCDay() || 7;                 // segunda = 1 … domingo = 7
  t.setUTCDate(t.getUTCDate() + 4 - dia);         // quinta-feira da mesma semana
  const inicio = new Date(Date.UTC(t.getUTCFullYear(), 0, 1));
  return Math.ceil(((t - inicio) / 864e5 + 1) / 7);
}

function conferirSonda(sourceId, aq) {
  const falta = (o) => { throw new Error(`${sourceId}: SONDA_DE_ROTA_DATADA_V1 ${o}`); };
  if (typeof aq.TEMPLATE !== "string" || !aq.TEMPLATE.trim()) falta("sem TEMPLATE");
  for (const v of ["AAAA", "MM", "DD"]) {
    if (!aq.TEMPLATE.includes(`{${v}}`)) falta(`TEMPLATE sem {${v}}`);
  }
  if (!Number.isInteger(aq.DIAS_PARA_TRAS) || aq.DIAS_PARA_TRAS < 1) falta("sem DIAS_PARA_TRAS inteiro >= 1");
  const n = aq.NUMEROS;
  if (aq.TEMPLATE.includes("{N}")) {
    if (!n || typeof n !== "object") falta("TEMPLATE tem {N} e não há NUMEROS");
    if (n.RULE === "ENUM") {
      if (!Array.isArray(n.VALUES) || n.VALUES.length === 0) falta("NUMEROS.ENUM sem VALUES");
    } else if (n.RULE === "ISO_WEEK") {
      if (!Array.isArray(n.OFFSETS) || n.OFFSETS.length === 0 || !n.OFFSETS.every(Number.isInteger)) falta("NUMEROS.ISO_WEEK sem OFFSETS inteiros");
    } else {
      falta(`NUMEROS.RULE ${JSON.stringify(n.RULE)} fora do vocabulário (ENUM, ISO_WEEK)`);
    }
  }
  const ac = aq.ACEITAR;
  if (!ac || typeof ac !== "object") falta("sem ACEITAR");
  if (typeof ac.SIGNATURE !== "string" || !ac.SIGNATURE) falta("ACEITAR sem SIGNATURE");
  if (!Number.isInteger(ac.MIN_BYTES) || ac.MIN_BYTES < 0) falta("ACEITAR sem MIN_BYTES inteiro");
}

// ── SONDA_DE_ROTA_DATADA_V1 ────────────────────────────────────────────────
// Para cada dia, de hoje para trás (`DIAS_PARA_TRAS` dias), e para cada
// número candidato, monta o endereço pelo molde e PEDE-O. Aceita o primeiro
// cujos bytes comecem por `ACEITAR.SIGNATURE` e tenham pelo menos
// `ACEITAR.MIN_BYTES`. A ordem — dia fora, número dentro — é a do `case`
// medido, e é a que encontra a edição mais recente primeiro.
//
// Bloco esperado no contrato:
//   {
//     STRATEGY: "CUSTOM_ADAPTER", ADAPTER_ID: "SONDA_DE_ROTA_DATADA_V1",
//     TEMPLATE: ".../{AAAA}/Notiziario_N{N}_{DD}-{MM}-{AAAA}.pdf",
//     DIAS_PARA_TRAS: 10,
//     NUMEROS: { RULE: "ISO_WEEK", OFFSETS: [0, -1] }   // ou { RULE: "ENUM", VALUES: [37, 36, 35] }
//     ACEITAR: { SIGNATURE: "%PDF", MIN_BYTES: 100000 },
//   }
//
// Devolve `[{ url, nome }]` com UM alvo, ou `{ erro }`. Quem marca a
// descoberta como degradada é o motor, com o `DEGRADED_REASON` do contrato —
// este adapter não sabe se está a correr como fallback.
export async function sondaDeRotaDatada({ sourceId, aq, buscar, agora }) {
  conferirSonda(sourceId, aq);
  if (typeof buscar !== "function") throw new Error(`${sourceId}: SONDA_DE_ROTA_DATADA_V1 precisa de um leitor`);
  const hoje = agora();
  let pedidos = 0;
  for (let volta = 0; volta < aq.DIAS_PARA_TRAS; volta++) {
    const d = new Date(hoje.getTime() - volta * 864e5);
    const AAAA = String(d.getUTCFullYear()), MM = pad2(d.getUTCMonth() + 1), DD = pad2(d.getUTCDate());
    const numeros = !aq.TEMPLATE.includes("{N}") ? [null]
      : aq.NUMEROS.RULE === "ENUM" ? aq.NUMEROS.VALUES.map(String)
      : aq.NUMEROS.OFFSETS.map((o) => String(semanaIso(d) + o));
    for (const N of numeros) {
      const u = aq.TEMPLATE.split("{AAAA}").join(AAAA).split("{MM}").join(MM)
        .split("{DD}").join(DD).split("{N}").join(N ?? "");
      pedidos++;
      const t = await buscar(u, 1);
      const assinatura = t.buf ? t.buf.subarray(0, aq.ACEITAR.SIGNATURE.length).toString("latin1") : "";
      if (!t.erro && t.status === 200 && (t.buf?.length ?? 0) > aq.ACEITAR.MIN_BYTES && assinatura === aq.ACEITAR.SIGNATURE) {
        return [{ url: u, nome: u.split("/").pop() }];
      }
    }
  }
  return { erro: `a rota previsivel nao achou edicao nos ultimos ${aq.DIAS_PARA_TRAS} dias (${pedidos} enderecos sondados)` };
}

export const ADAPTERS = Object.freeze({
  SONDA_DE_ROTA_DATADA_V1: sondaDeRotaDatada,
});
