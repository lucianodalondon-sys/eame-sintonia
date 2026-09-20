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

// ── CANAL_PUBLICO_YOUTUBE_V1 ───────────────────────────────────────────────
// A rota do FEED MORREU POR LEI, NÃO POR AVARIA. `youtube.com/feeds/videos.xml`
// responde 200 com XML real — e está em `Disallow` no robots.txt do host, lido
// ao vivo pelo portão da casa. Cinquenta fontes chegaram a `READY` por ali e
// foram despromovidas, com razão.
//
//     UMA ROTA QUE RESPONDE NÃO É UMA ROTA PERMITIDA.
//
// A rota desta peça é a página pública do separador Vídeos —
// `/channel/<CHANNEL_ID>/videos` — que o MESMO portão aprova. Medido nesta
// bancada: 30 `videoId` no HTML, em três canais diferentes, HTTP 200, sem
// cookie, sem login, sem chave e sem um dólar.
//
// POR QUE ISTO É UM ADAPTER, E NÃO `HTML_LINK_DISCOVERY`
// ------------------------------------------------------
// Medido: a página traz `videoIds` = 30 e `href="/watch?v="` = **0**. Os
// endereços não existem como links no HTML servido — vivem dentro do
// `ytInitialData`, em JSON embutido. Um `LINK_PATTERN` sobre `href` encontra
// zero, e um `LINK_PATTERN` sobre o JSON seria um molde a fingir-se de link.
//
//     O VOCABULÁRIO DECLARATIVO NÃO DESCREVE «LER JSON DENTRO DE HTML».
//     É POR ISSO QUE EXISTE A PORTA `CUSTOM_ADAPTER` — e é a confissão
//     honesta desta peça, não um sítio para esconder SOURCE_ID.
//
// E NÃO É yt-dlp. A ferramenta existe nesta máquina e funciona, mas a lei
// deste ficheiro é explícita: sem `eval`, sem `Function`, **sem processo
// filho**. O `curl` que o motor já injecta em `buscar` chega aos mesmos 30
// alvos. Um provider externo aqui seria um segundo caminho invisível.
//
// A IDENTIDADE LÊ-SE DO CANAL, NUNCA DO ITEM
// -------------------------------------------
// ⚠️ Medido, e é uma armadilha real: em `yt-dlp --flat-playlist` o
// `channel_id` do ITEM vem `NA`. Uma guarda construída sobre o item compara
// `NA` com o pedido, nunca casa — ou pior, é escrita para tolerar `NA` e
// **aprova sempre**. Uma fechadura que nunca tranca.
//
// Aqui a identidade vem do documento do CANAL: `channelId`/`externalId` no
// JSON embutido, e o `<link rel="canonical">`. Se nenhum dos dois contiver o
// `CHANNEL_ID` pedido, isto devolve erro e não devolve alvo nenhum:
// `IDENTITY_MISMATCH` é falha fechada.
//
// Bloco esperado no contrato:
//   {
//     STRATEGY: "CUSTOM_ADAPTER", ADAPTER_ID: "CANAL_PUBLICO_YOUTUBE_V1",
//     CHANNEL_ID: "UC…",          // 24 caracteres, começa por UC
//     MAX_TARGETS: 10,            // opcional; sem ele, tudo o que a página deu
//   }
const RE_CHANNEL_ID = /^UC[A-Za-z0-9_-]{22}$/;
const RE_VIDEO_ID = /"videoId":"([A-Za-z0-9_-]{11})"/g;
const RE_CANAL_NO_HTML = /"(?:channelId|externalId)":"(UC[A-Za-z0-9_-]{22})"/g;
const RE_CANONICAL = /<link rel="canonical" href="([^"]+)"/;

export async function canalPublicoYoutube({ sourceId, aq, buscar }) {
  const falta = (o) => { throw new Error(`${sourceId}: CANAL_PUBLICO_YOUTUBE_V1 ${o}`); };
  if (typeof aq.CHANNEL_ID !== "string" || !RE_CHANNEL_ID.test(aq.CHANNEL_ID)) {
    falta(`sem CHANNEL_ID válido (esperado UC + 22 caracteres, veio ${JSON.stringify(aq.CHANNEL_ID)})`);
  }
  if (aq.MAX_TARGETS !== undefined && (!Number.isInteger(aq.MAX_TARGETS) || aq.MAX_TARGETS < 1)) {
    falta("MAX_TARGETS presente mas não é inteiro >= 1");
  }
  if (typeof buscar !== "function") falta("precisa de um leitor");

  // A rota é construída aqui a partir do CHANNEL_ID do contrato. O feed
  // barrado não é alcançável por este molde nem por engano.
  const url = `https://www.youtube.com/channel/${aq.CHANNEL_ID}/videos`;
  const t = await buscar(url, 2);
  if (t.erro || t.status !== 200) {
    return { erro: `a pagina publica do canal nao respondeu 200 (status ${t.status ?? 0}${t.erro ? `, ${t.erro}` : ""})` };
  }
  const html = t.buf ? t.buf.toString("utf8") : "";

  // IDENTIDADE PRIMEIRO. Só depois se olha para o conteúdo: aceitar alvos de
  // um canal e carimbá-los com o SOURCE_ID de outro é pior do que não colher.
  const canonical = RE_CANONICAL.exec(html);
  const declarados = new Set();
  for (const m of html.matchAll(RE_CANAL_NO_HTML)) declarados.add(m[1]);
  const bate = declarados.has(aq.CHANNEL_ID)
    || Boolean(canonical && canonical[1].includes(aq.CHANNEL_ID));
  if (!bate) {
    const vistos = [...declarados].slice(0, 3).join(", ") || "nenhum";
    return { erro: `IDENTITY_MISMATCH: pedi ${aq.CHANNEL_ID} e a pagina declara ${vistos}` };
  }

  const ids = [...new Set([...html.matchAll(RE_VIDEO_ID)].map((m) => m[1]))];
  if (ids.length === 0) {
    return { erro: "a pagina do canal respondeu 200 e nao trouxe videoId nenhum" };
  }
  const limite = aq.MAX_TARGETS ?? ids.length;
  return ids.slice(0, limite).map((id) => ({
    url: `https://www.youtube.com/watch?v=${id}`,
    nome: id,
  }));
}

export const ADAPTERS = Object.freeze({
  SONDA_DE_ROTA_DATADA_V1: sondaDeRotaDatada,
  CANAL_PUBLICO_YOUTUBE_V1: canalPublicoYoutube,
});
