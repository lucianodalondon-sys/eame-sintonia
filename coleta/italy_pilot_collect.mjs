// PILOTO DE COLETA RECORRENTE — ITALIA V1
//
// Prova se o SINTONIA consegue voltar amanha, reconhecer o que ja viu, capturar so o novo,
// preservar versoes e perceber quebra SEM transformar ausencia ou falha em dado.
//
// LEIS QUE ESTE COLETOR OBEDECE (cada uma com guarda em italy_contract_test.mjs):
//   CAPTURE            != DOCUMENT              uma execucao pode ver o mesmo doc 10x
//   DOCUMENT_ID        != BYTE_ID               identidade semantica != SHA256
//   SAME_URL           != SAME_DOCUMENT         URL fixa pode carregar versoes diferentes
//   SAME_HASH          != DEGRADED              receber o mesmo doc e o esperado
//   NO_CHANGE          != FAILURE
//   NEW_HASH           != NEW_SEMANTIC_FACT     mudou byte nao quer dizer fato novo
//   MOVING_WINDOW      != NEW_DATASET_EVERY_DAY janela que anda nao e dataset novo
//   FIRST_RUN          =  BASELINE              a primeira execucao nao pode dizer "novo desde ontem"
//   SOURCE_HEALTH      != SOURCE_VERDICT
//   PARSER_FAILURE MUST NOT DESTROY CAPTURED_RAW
//
// Uso:
//   node coleta/italy_pilot_collect.mjs --run-id=<RUN_ID> --fonte=<ID> [--fonte=<ID>...]
//                                             executa uma rodada real
//   node coleta/italy_pilot_collect.mjs --negativos         roda os controles negativos
//
// ⚠️ `--dry` ESTAVA DOCUMENTADO E NUNCA EXISTIU: `process.argv` so alimentava a
// `nota`, e a flag virava texto do recibo. A linha foi apagada em vez de ser
// implementada — prometer modo seco no cabecalho e nao o ter e pior do que nao
// o ter. Para correr sem rede, injecta-se `forcarBuf`, que e o mecanismo que
// esta casa ja usa.

import { execFileSync, execFile } from "node:child_process";
import { promisify } from "node:util";
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync, appendFileSync, rmSync } from "node:fs";
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
// ⚠️ `./italy_contracts.mjs` NAO EXISTE AQUI desde a mudanca para gavetas: os
// contratos moraram sempre em `regras/`. O Python ganhou `_gavetas.py` para
// resolver os nomes curtos; o lado Node ficou com os imports da pasta unica, e
// por isso este coletor NAO CARREGAVA — nao e sintaxe, e o caminho.
import { CONTRACTS } from "../regras/italy_contracts.mjs";
// O motor declarativo de rota. Ele responde «que enderecos buscar?» a partir
// do bloco `ACQUISITION` do contrato — e NAO le nenhum campo em prosa.
import { alvosDoContrato, identidadeDoContrato } from "../regras/motor_de_rota.mjs";
// ── AS DUAS DEFESAS DA INCREMENTALIDADE ────────────────────────────────────
// ⚠️ ESTAS DUAS LINHAS SAO A MISSAO INTEIRA, E O DEFEITO ERA A FALTA DELAS.
// Medido em 2026-09-22: `regras/incrementalidade.mjs` tinha md5 IDENTICO no
// laboratorio e na producao (fa79d5279b9c) — nao era codigo velho nem peca em
// falta. Mas quem chamava `decidirSobreDetalhe()` eram TRES ficheiros: o
// proprio, o teste dele e a prova. Este coletor — que e quem bate a porta e
// quem escreve `DOCUMENT_CHANGED_IN_PLACE` — tinha ZERO referencias a
// incrementalidade.
//
//     A PECA EXISTIA, ESTAVA CERTA, E NINGUEM A CHAMAVA.
//     ISTO E `MISSING_ROUTE`, NAO E CODIGO EM FALTA.
//
// A bancada passava porque a bancada chamava a peca pela mao (a prova em
// `medidas/incrementalidade_prova.mjs`). A producao corria por aqui, e aqui
// nao havia ligacao nenhuma. LAB PASS NAO PROVA OPS PASS.
import { memoriaDosDetalhes, decidirSobreDetalhe, decidirSobreIndice } from "../regras/incrementalidade.mjs";
import { compararConteudo } from "../regras/normalizacao_de_conteudo.mjs";

// ── O REGISTRY DE ADAPTERS ─────────────────────────────────────────────────
// Vazio, e isso e uma medicao e nao um esquecimento: das sete fontes com
// `case`, NENHUMA precisou de logica fora das tres estrategias declarativas.
// Criar adapters agora seria construir a porta de saida antes de existir
// alguem para sair por ela.
//
//     UM REGISTRY VAZIO DIZ «NINGUEM PRECISOU AINDA».
//     UM REGISTRY CHEIO DE NOMES POR USAR DIZ «ALGUEM ADIVINHOU».
//
// `CUSTOM_ADAPTER` existe no vocabulario para o dia em que uma fonte real
// nao couber — e nesse dia o contrato NOMEIA o adapter, sem que o
// despachador volte a conhecer SOURCE_ID.
const ADAPTERS = Object.freeze({});

const run = promisify(execFile);
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36";
const RAIZ = process.env.ITALY_OPS_ROOT || ".";
const LEDGER_DIR = `${RAIZ}/data/collection-ledger/italy`;
const STORE = `${RAIZ}/data/collection-store/italy`;
const COLLECTOR_VERSION = "pilot-v1";

// ── O UNICO CONCEITO QUE ESTE CORTE SABE RESOLVER ──────────────────────────
// `RESOLVED_STRUCTURED_TARGET` responde a UMA pergunta, e nao a outra parecida:
//
//     o que esta materializacao PRODUZIU   <- e esta
//     o que esta fonte PODE produzir       <- e a permissao, e vive no contrato
//
// A permissao (`ALLOWED_STRUCTURED_TARGETS`) ainda nao esta instalada em lado
// nenhum. Isso NAO autoriza este coletor a manter uma segunda lista sua: uma
// constante e o nome do que ele acabou de fazer; uma lista seria uma autoridade
// paralela, e a casa ja mediu o que custa ter duas.
const SOURCE_DOCUMENT = "SOURCE_DOCUMENT";

export const PILOT_SOURCES = ["IT-T3-005", "IT-T2-002", "IT-T2-004", "IT-T3-002", "IT-T3-010", "IT-T3-008", "IT-T4-001"];

// ── A CAPACIDADE, LIDA DO CONTRATO ─────────────────────────────────────────
// Enxertado de `aquisicao-detalhe-v1` na CANONICAL-MICRO-V1 (2026-09-21), a
// mao e so este bloco: aquele ramo NAO tem o portao de admissao, e trazer o
// ficheiro inteiro apagava 234 linhas daqui.
//
// `PILOT_SOURCES` e HISTORIA: as sete que o piloto percorreu por `case`, e
// fica escrita porque o ledger e as guardas contam com ela. A capacidade de
// HOJE nao se digita — le-se do contrato: sabe-se percorrer quem declara
// `ACQUISITION`. Foi a falta disto que fez a CLI recusar `IT-T3-011` como
// FONTE_DESCONHECIDA com contrato executavel escrito e site a responder.
//
//     CAPACIDADE DIGITADA E CAPACIDADE DE ONTEM.
//
// ⚠️ E UMA LISTA DE CAPACIDADE, NUNCA UMA LISTA DE PERMISSAO. Medido nesta
// missao: das 8 fontes que o portao admite, 7 estao aqui e IT-T5-041 nao —
// e das 186 que estao aqui, 178 o portao RECUSA. Os dois conjuntos cruzam-se
// e nenhum contem o outro.
//
//     CAPACIDADE NAO E APROVACAO. Quem decide se se vai e
//     `curadoria/collection_gate.py`, perguntado por
//     `coleta/italy_executor.py::admissao_do_curator` ANTES deste processo
//     sequer arrancar. Esta constante so responde «sei o caminho».
//
// ⚠️ A UNIAO DOS DOIS CAMINHOS, E NAO SO UM. O despachante de alvos tem
// exactamente duas portas — `if (c && c.ACQUISITION) -> motor declarativo`,
// `else -> switch (sourceId)`. A capacidade e a UNIAO das duas. Ler so a
// primeira, como o ramo de origem faz, mede uma casa onde os sete `case` ja
// tinham `ACQUISITION` escrito a mao; nesta linha nao tem, e a copia literal
// deste bloco fazia a CLI recusar as SETE fontes do piloto que funcionam —
// medido: 0 de 7 percorriveis. Uma lista de capacidade que esquece metade do
// despachante nao e mais honesta que uma lista digitada: e a mesma mentira,
// derivada.
export const FONTES_PERCORRIVEIS = Object.freeze([...new Set([
  ...Object.keys(CONTRACTS).filter((sid) => CONTRACTS[sid] && CONTRACTS[sid].ACQUISITION),
  ...PILOT_SOURCES,   // as sete do `switch`, que nao declaram ACQUISITION
])]);

const sha = b => createHash("sha256").update(b).digest("hex");
const agora = () => new Date().toISOString();

function assinatura(buf) {
  const h = buf.subarray(0, 8).toString("latin1");
  if (h.startsWith("%PDF")) return "PDF";
  if (h.startsWith("PK")) return "ZIP";
  const t = buf.subarray(0, 400).toString("latin1").trimStart();
  if (t.startsWith("<")) return "HTML";
  return "TEXTO";
}

// ---------- LEDGER append-only ----------
function ledgerPath() { mkdirSync(LEDGER_DIR, { recursive: true }); return `${LEDGER_DIR}/observations.ndjson`; }
export function lerLedger() {
  const p = `${LEDGER_DIR}/observations.ndjson`;
  if (!existsSync(p)) return [];
  return readFileSync(p, "utf8").split("\n").filter(Boolean).map(l => JSON.parse(l));
}
function gravar(obs) { appendFileSync(ledgerPath(), JSON.stringify(obs) + "\n"); }

// ---------- RAW imutavel ----------
function guardarRaw(sourceId, documentId, versionId, nome, buf) {
  const dir = `${STORE}/${sourceId}/${documentId.replace(/[:\/\\]/g, "_")}/${versionId}`;
  if (existsSync(`${dir}/${nome}`)) return { dir, criado: false };
  mkdirSync(dir, { recursive: true });
  writeFileSync(`${dir}/${nome}`, buf);
  return { dir, criado: true };
}

// ---------- baixar ----------
const TRANSITORIOS = [28, 35, 52, 56, 7];  // timeout, reset, resposta vazia, recv failure, connect

// ── O CONTADOR DE PORTAS BATIDAS ───────────────────────────────────────────
// ⚠️ CONTA-SE AQUI, NO UNICO SITIO QUE FALA COM A REDE, e nao la em cima por
// deducao. Tentar deduzir `INDEX_REQUESTS` pela estrategia do contrato daria
// um numero errado para as sete fontes do `switch`: quatro delas buscam um
// indice, tres nao, e `STATIC_ENDPOINT` nunca busca. Um pedido conta-se onde
// ele acontece; em qualquer outro sitio e um palpite com cara de medida.
//
//     `REDE.total` sao TODAS as idas a fonte.
//     `DETAIL_REQUESTS` sao as idas a um detalhe, contadas no laco.
//     INDEX_REQUESTS = total - detalhes.  Exacto, e sem adivinhar.
//
// ⚠️ DESDE A A5, `REDE.total` SO SOBE QUANDO O PEDIDO SAI. Um pedido que a
// cortesia recusa (robots, teto) nao bateu a porta — conta-lo como ida faria
// `INDEX_REQUESTS` inventar indices que ninguem pediu. As idas ao robots.txt
// tambem ficam fora: sao contadas a parte, em `CORTESIA.pedidos.ROBOTS`.
const REDE = { total: 0 };

// ══ A CORTESIA VIVE AQUI, DENTRO DO TRANSPORTE ═════════════════════════════
// ⚠️ MEDIDO NA A4 (23/09): este coletor nao lia robots.txt e disparava os
// pedidos a um mesmo site seguidos, sem pausa. Quem leu o robots e espacou os
// pedidos na micro com rede real foi o CONDUTOR, por fora
// (`scripts/micro_coleta/micro_rede_real.py`) — e uma regra que vive no
// condutor vale para aquele condutor e falta a todos os outros.
//
//     A CORTESIA E UMA PROPRIEDADE DO TRANSPORTE, E O TRANSPORTE TEM DONO.
//
// `baixar()` e o dono: e o unico sitio deste coletor por onde um pedido a uma
// fonte sai (o motor de rota recebe-o como `buscar`, os `case` chamam-no
// directamente). A unica outra saida e a medicao do egresso em ipinfo.io, que
// nao e pedido a fonte nenhuma e nao passa por aqui de proposito.
//
// As tres guardas, cada uma com a regra que ja existia na casa:
//   ROBOTS  lido por origem, uma vez por corrida, com os estados de
//           `coleta/scrap_http.py::_carregar_robots`:
//             404/410            -> AUSENTE      permitido (sem ficheiro = sem proibicao)
//             200 com regras     -> LIDO         vale o que ele diz
//             200 com HTML, ou   -> ILEGIVEL     NAO permitido — «nao afirmamos
//             qualquer outro HTTP                 permissao que nao lemos»
//             sem resposta       -> INDISPONIVEL o pedido NAO sai, e NAO e uma
//                                                 recusa do host; nao fica em
//                                                 cache (um soluco de rede nao
//                                                 vira proibicao para a corrida)
//           e vale EM CADA SALTO: o curl deixou de seguir redireccionamentos
//           sozinho (`-L` saiu), porque um 301 para outro caminho ou outro host
//           e um pedido novo e pede licenca outra vez (a mesma lei de
//           `scrap_http._PortaoEmCadaSalto`).
//   PAUSA   minima entre dois pedidos ao MESMO host, configuravel
//           (SINTONIA_PAUSA_POR_HOST_S); por omissao 1,0 s, o
//           `PAUSA_ENTRE_CHAMADAS` de `scrap_http.py`. Um `Crawl-delay` maior
//           no robots manda sobre ela.
//   TETO    pedidos HTTP por SITE (host sem `www.`) numa corrida, configuravel
//           (SINTONIA_TETO_POR_HOST); por omissao 5 — a D7 do dono: «ate 5
//           pedidos por site (robots + pagina + ate 3 materias)». Conta TODAS
//           as idas: robots, indice, materias, saltos e retentativas.
//
// O que a cortesia recusa NAO e uma observacao da fonte: nao se escreve no
// livro (como `DEFERRED_AFTER_TIMEOUT`), vai contado no resumo e em
// `detalhes`, com o motivo. Na corrida seguinte o endereco continua
// desconhecido e volta a ser pedido — ADIADO != NUNCA.
export const CORTESIA_PADRAO = Object.freeze({ PAUSA_S: 1.0, TETO_POR_HOST: 5, MAX_SALTOS: 10 });
// ── AS EXCECOES: NENHUMA, E ISSO E UMA MEDICAO ─────────────────────────────
// A regra da missao: so excecoes ja decididas pelo dono E ja escritas no
// codigo. A unica que existe (D23, videos de organizacoes no LinkedIn) vive no
// Scrap (`coleta/scrap_http.py` e as rotas dele), nao passa por este coletor, e
// por isso nao se copia para aqui. Uma lista vazia e nomeada diz «procurou-se,
// nao ha»; um interruptor generico («desligar robots») seria uma excecao que
// ninguem decidiu.
export const EXCECOES_DE_CORTESIA = Object.freeze([]);

function cortesiaDoAmbiente() {
  const ler = (nome, omissao) => {
    const v = process.env[nome];
    if (v === undefined || v === "") return omissao;
    const n = Number(v);
    if (!Number.isFinite(n) || n < 0) throw new Error(`CORTESIA_INVALIDA: ${nome}=${v}`);
    return n;
  };
  const TETO_POR_HOST = ler("SINTONIA_TETO_POR_HOST", CORTESIA_PADRAO.TETO_POR_HOST);
  // Um teto 0 ou fracionario nao e um teto: e uma forma de desligar a coleta
  // (ou de a deixar a adivinhar) sem o dizer. Falha alto.
  if (!Number.isInteger(TETO_POR_HOST) || TETO_POR_HOST < 1)
    throw new Error(`CORTESIA_INVALIDA: SINTONIA_TETO_POR_HOST=${TETO_POR_HOST} (inteiro >= 1)`);
  return { PAUSA_S: ler("SINTONIA_PAUSA_POR_HOST_S", CORTESIA_PADRAO.PAUSA_S), TETO_POR_HOST,
           MAX_SALTOS: CORTESIA_PADRAO.MAX_SALTOS };
}
// Estado de UMA corrida. `executarRodada()` recomeca-o, como faz a `REDE.total`.
const CORTESIA = { cfg: CORTESIA_PADRAO, robots: new Map(), porHost: new Map(), ultimo: new Map(),
                   pedidos: { ROBOTS: 0, FONTE: 0 }, recusas: [] };
function reiniciarCortesia() {
  CORTESIA.cfg = cortesiaDoAmbiente();
  CORTESIA.robots = new Map(); CORTESIA.porHost = new Map(); CORTESIA.ultimo = new Map();
  CORTESIA.pedidos = { ROBOTS: 0, FONTE: 0 }; CORTESIA.recusas = [];
}
const dormir = ms => new Promise(r => setTimeout(r, ms));

// ── O ROBOTS.TXT, LIDO COMO A NORMA MANDA (RFC 9309) ──────────────────────
// Grupos por `User-agent`; `Allow`/`Disallow` com `*` e `$`; vence a regra de
// caminho MAIS LONGO, e no empate vence `Allow`. `Disallow:` vazio nao proibe
// nada. O grupo que vale para nos: o do nosso token de produto (o que vem
// antes da primeira `/` do User-Agent, como faz `urllib.robotparser`, que e o
// leitor da casa); nao havendo, o `*`; nao havendo nenhum, tudo permitido.
//
// ⚠️ NAO E O `urllib.robotparser` LINHA A LINHA, e a diferenca vai declarada:
// o da casa usa a PRIMEIRA regra que casa e nao conhece `*` no meio do caminho
// (le `Disallow: /*?` como o prefixo literal «/*?», que nunca casa). Aqui vale
// a norma. Onde as duas leituras divergem, esta e a mais restritiva nos casos
// com curinga — nunca a mais permissiva por um defeito de leitura.
export function lerRobots(txt) {
  const grupos = [];
  let atual = null, aLerAgentes = false;
  for (const bruta of String(txt ?? "").split(/\r\n|\r|\n/)) {
    const linha = bruta.replace(/#.*$/, "").trim();
    const m = linha.match(/^([A-Za-z-]+)\s*:\s*(.*)$/);
    if (!m) continue;
    const campo = m[1].toLowerCase(), valor = m[2].trim();
    if (campo === "user-agent") {
      if (!atual || !aLerAgentes) { atual = { agentes: [], regras: [], crawlDelay: null }; grupos.push(atual); }
      atual.agentes.push(valor.toLowerCase());
      aLerAgentes = true;
    } else if (campo === "allow" || campo === "disallow" || campo === "crawl-delay") {
      if (!atual) continue;            // regra antes de qualquer User-agent: nao pertence a ninguem
      aLerAgentes = false;
      if (campo === "crawl-delay") {
        const n = Number(valor);
        if (Number.isFinite(n) && n >= 0) atual.crawlDelay = n;
      } else if (valor !== "") {
        atual.regras.push({ permite: campo === "allow", caminho: valor });
      }
    }
  }
  return grupos;
}
const TOKEN_DO_AGENTE = UA.split("/")[0].toLowerCase();
export function grupoQueVale(grupos, token = TOKEN_DO_AGENTE) {
  const nossos = grupos.filter(g => g.agentes.includes(token));
  const escolhidos = nossos.length ? nossos : grupos.filter(g => g.agentes.includes("*"));
  if (!escolhidos.length) return null;
  const atrasos = escolhidos.map(g => g.crawlDelay).filter(n => n !== null);
  return { regras: escolhidos.flatMap(g => g.regras), crawlDelay: atrasos.length ? Math.max(...atrasos) : null };
}
const semEscape = s => { try { return decodeURI(s); } catch { return s; } };
function casaCaminho(padrao, caminho) {
  const ancorado = padrao.endsWith("$");
  const corpo = ancorado ? padrao.slice(0, -1) : padrao;
  const re = corpo.split("*").map(p => p.replace(/[.+?^${}()|[\]\\]/g, "\\$&")).join(".*");
  return new RegExp("^" + re + (ancorado ? "$" : "")).test(caminho);
}
export function robotsPermite(grupos, caminho) {
  if (caminho === "/robots.txt") return true;
  const g = grupoQueVale(grupos);
  if (!g) return true;
  const alvo = semEscape(caminho);
  let melhor = null;
  for (const r of g.regras) {
    const padrao = semEscape(r.caminho);
    if (!casaCaminho(padrao, alvo)) continue;
    if (!melhor || padrao.length > melhor.len || (padrao.length === melhor.len && r.permite))
      melhor = { len: padrao.length, permite: r.permite };
  }
  return melhor ? melhor.permite : true;
}

// ── UMA IDA A REDE: um pedido HTTP, sem seguir saltos ──────────────────────
// Pausa ANTES, teto contado ANTES (o pedido que sai gasta o lugar, responda ou
// nao), hora do fim guardada DEPOIS — a pausa mede-se do fim de um pedido ao
// comeco do seguinte.
// ── O SITE E O HOST SEM `www.` ─────────────────────────────────────────────
// ⚠️ MEDIDO NA MICRO DA A5 (23/09): `www.etvilloresi.it` redirecciona para
// `etvilloresi.it`, e com o teto contado por HOST o mesmo site levou 6 pedidos
// (2 + 4) — a D7 diz «ate 5 pedidos por SITE». Teto e pausa contam-se pela chave
// do site; o robots continua por ORIGEM, que e o que a norma manda.
export const siteDe = host => String(host).toLowerCase().replace(/^www\./, "");
async function umaIda(url, host, tipo, crawlDelay) {
  const minimo = Math.max(CORTESIA.cfg.PAUSA_S, crawlDelay || 0) * 1000;
  host = siteDe(host);
  const ultimo = CORTESIA.ultimo.get(host);
  if (ultimo !== undefined) {
    const falta = ultimo + minimo - Date.now();
    if (falta > 0) await dormir(falta);
  }
  CORTESIA.porHost.set(host, (CORTESIA.porHost.get(host) || 0) + 1);
  CORTESIA.pedidos[tipo]++;
  try {
    // ⚠️ `%{content_type}` ENTRA PORQUE O TRANSPORTE JA O SABIA E NINGUEM O ESCREVIA.
    // A ESPECIE dos bytes vinha no cabecalho da resposta, era deitada fora aqui, e
    // a observacao chegava a porta sem dizer o que os bytes SAO. O resultado esta
    // medido nesta bancada a 2026-09-15, com `IT-T4-001` (um CSV de 4,59 MB):
    //
    //     raw_asset.media_type = 'NAO SEI'
    //     etapa DERIVED        = FAIL / DERIVATION_FAILED
    //
    // E o FAIL era mentira sobre o documento. `coleta/ingresso.py` ja tem a lei
    // escrita — «UMA FERRAMENTA QUE RECEBE O QUE NAO SABE ABRIR NAO FALHOU: FOI
    // CHAMADA PARA O TRABALHO ERRADO» — e ja tem o desfecho certo pronto
    // (`DERIVACAO_ESPECIE_NAO_SUPORTADA` -> `NOT_APPLICABLE`). Ele nunca corria,
    // porque a pergunta que o dispara e `MEDIA_TYPE`, e o campo chegava vazio.
    // Sem especie declarada, o CSV era entregue ao extractor de PDF.
    //
    //     ESPECIE POR DECLARAR NAO E ESPECIE DESCONHECIDA:
    //     E UMA PERGUNTA QUE O TRANSPORTE JA TINHA RESPONDIDO.
    //
    // ⚠️ E ISTO NAO E A EXTENSAO DO FICHEIRO OUTRA VEZ. E o que o SERVIDOR
    // declarou, e declaracao de terceiro nao e prova: quem guarda continua a ser
    // a validacao de BYTES contra `EXPECTED_SIGNATURE`, que corre antes de
    // qualquer parse e ja reprova um HTML servido como PDF. Esta linha nao a
    // substitui nem a afrouxa — acrescenta o que a fonte disse de si.
    //
    // ⚠️ `-L` SAIU DE PROPOSITO (ver o bloco da cortesia): quem segue o salto e
    // `baixar()`, que pede licenca ao robots do destino antes de ir.
    const { stdout } = await run("curl", ["-sS", "--max-time", "90", "-A", UA,
      "-H", "Accept-Language: it-IT,it;q=0.9", "-o", "-",
      "-w", "\\n__S__%{http_code}\\t%{content_type}\\t%{redirect_url}", url],
      { maxBuffer: 128e6, encoding: "buffer" });
    const s = stdout.toString("latin1");
    const k = s.lastIndexOf("\n__S__");
    const reboque = (k < 0 ? "" : s.slice(k + 6)).split("\t");
    // O reboque tem TRES campos: codigo, especie e destino do salto. Nenhum traz
    // tabulacao. AUSENTE CONTINUA AUSENTE: um servidor que nao declara tipo devolve
    // vazio aqui, e vazio vira `null` — nunca uma especie adivinhada pelo nome.
    return { buf: stdout.subarray(0, k < 0 ? stdout.length : k), status: Number(reboque[0]),
             contentType: (reboque[1] || "").trim().split(";")[0].trim() || null,
             destino: (reboque[2] || "").trim() || null };
  } finally {
    CORTESIA.ultimo.set(host, Date.now());
  }
}
const tetoAtingido = host => (CORTESIA.porHost.get(siteDe(host)) || 0) >= CORTESIA.cfg.TETO_POR_HOST;

async function robotsDaOrigem(origem) {
  let alvo = `${origem}/robots.txt`;
  for (let salto = 0; salto <= CORTESIA.cfg.MAX_SALTOS; salto++) {
    const host = new URL(alvo).hostname;
    let r = null;
    for (let i = 1; i <= 2 && !r; i++) {
      if (tetoAtingido(host)) return { recusado: "TETO_POR_HOST", porque: `teto de ${CORTESIA.cfg.TETO_POR_HOST} pedidos a ${host} esgotado antes de ler o robots.txt` };
      try { r = await umaIda(alvo, host, "ROBOTS", 0); }
      catch (e) {
        const cod = e.code ?? 0;
        if (!TRANSITORIOS.includes(cod) || i === 2)
          return { estado: "INDISPONIVEL", porque: `o transporte caiu antes da resposta (curl ${cod}) — nao e uma recusa do host` };
      }
    }
    if (r.status >= 300 && r.status < 400 && r.destino) { alvo = r.destino; continue; }
    // ⚠️ O ROBOTS LIDO NO FIM DE UM SALTO E O ROBOTS DAQUELA ORIGEM TAMBEM.
    // Medido na micro da A5: o robots de `www.etvilloresi.it` redireccionava para
    // `etvilloresi.it/robots.txt`, e a seguir o coletor pedia o MESMO ficheiro
    // outra vez para a origem de destino — um pedido gasto do teto por nada.
    // `origemLida` diz a quem o ficheiro pertence; `licenca()` guarda-o para as duas.
    const fimEm = new URL(alvo);
    const origemLida = fimEm.pathname === "/robots.txt" ? fimEm.origin : null;
    if (r.status === 404 || r.status === 410) return { estado: "AUSENTE", origemLida, porque: `HTTP ${r.status} — o host nao publica robots.txt` };
    if (r.status !== 200) return { estado: "ILEGIVEL", origemLida, porque: `HTTP ${r.status} no robots.txt — nao afirmamos permissao que nao lemos` };
    const corpo = r.buf.toString("utf8").trimStart().toLowerCase();
    if (corpo.startsWith("<!doctype") || corpo.startsWith("<html"))
      return { estado: "ILEGIVEL", origemLida, porque: "o robots.txt veio em HTML — nao afirmamos permissao que nao lemos" };
    const grupos = lerRobots(r.buf.toString("utf8"));
    return { estado: "LIDO", origemLida, grupos, crawlDelay: grupoQueVale(grupos)?.crawlDelay ?? null, porque: "robots.txt lido" };
  }
  return { estado: "ILEGIVEL", porque: `robots.txt com mais de ${CORTESIA.cfg.MAX_SALTOS} redireccionamentos` };
}

// A licenca para UM endereco: teto, robots (lido uma vez por origem), teto outra vez.
async function licenca(url) {
  let u;
  try { u = new URL(url); } catch { return { recusado: "URL_INVALIDA", porque: `endereco invalido: ${url}` }; }
  const host = u.hostname;
  if (tetoAtingido(host)) return { recusado: "TETO_POR_HOST", porque: `teto de ${CORTESIA.cfg.TETO_POR_HOST} pedidos a ${host} nesta corrida` };
  let rb = CORTESIA.robots.get(u.origin);
  if (!rb) {
    rb = await robotsDaOrigem(u.origin);
    if (rb.recusado) return rb;
    // INDISPONIVEL nao fica em cache (a regra de scrap_http.permitido).
    // Guarda-se para a origem pedida E para a origem cujo ficheiro se leu no fim
    // dos saltos (a mesma, quase sempre). Uma so instrucao, de proposito: duas
    // linhas (uma por origem) cobriam-se uma a outra, e o red team (K8) mostrou
    // que desligar a primeira nao mudava nada.
    if (rb.estado !== "INDISPONIVEL")
      for (const o of new Set([u.origin, rb.origemLida].filter(Boolean))) CORTESIA.robots.set(o, rb);
  }
  if (rb.estado === "INDISPONIVEL") return { recusado: "ROBOTS_INDISPONIVEL", porque: rb.porque };
  if (rb.estado === "ILEGIVEL") return { recusado: "ROBOTS_ILEGIVEL", porque: rb.porque };
  if (rb.estado === "LIDO" && !robotsPermite(rb.grupos, u.pathname + u.search))
    return { recusado: "ROBOTS_PROIBE", porque: `o robots.txt de ${u.origin} proibe ${u.pathname}${u.search}` };
  if (tetoAtingido(host)) return { recusado: "TETO_POR_HOST", porque: `teto de ${CORTESIA.cfg.TETO_POR_HOST} pedidos a ${host} esgotado pelo robots.txt` };
  return { host, crawlDelay: rb.crawlDelay ?? null };
}

async function baixar(url, tentativas = 2) {
  let atual = url, foiARede = false;
  for (let salto = 0; salto <= CORTESIA.cfg.MAX_SALTOS; salto++) {
    const lic = await licenca(atual);
    if (lic.recusado) {
      CORTESIA.recusas.push({ URL: atual, PEDIDO: url, MOTIVO: lic.recusado, PORQUE: lic.porque, SALTO: salto });
      // `erro` para que quem so conhece `erro` (motor de rota, `case`) pare aqui
      // e nao leia bytes que nao vieram; `recusado` para quem sabe distinguir.
      return { erro: `CORTESIA ${lic.recusado}: ${lic.porque}`, status: 0, tentativas: 0,
               recusado: lic.recusado, foiARede, retry_permitido: false };
    }
    if (!foiARede) { REDE.total++; foiARede = true; }
    let r = null;
    for (let i = 1; i <= tentativas && !r; i++) {
      if (i > 1 && tetoAtingido(lic.host))
        return { erro: `CORTESIA TETO_POR_HOST: retentativa recusada, teto de ${CORTESIA.cfg.TETO_POR_HOST} esgotado`, status: 0, tentativas: i - 1, recusado: "TETO_POR_HOST", foiARede, retry_permitido: false };
      try {
        r = await umaIda(atual, lic.host, "FONTE", lic.crawlDelay);
        r.tentativas = i;
      } catch (e) {
        const cod = e.code ?? 0;
        const transitorio = TRANSITORIOS.includes(cod);
        // retry SO para falha de transporte. Nunca para schema, MIME, login ou WAF.
        // `codigo` sai para fora porque o laco das materias precisa de distinguir
        // o site PENDURADO (28 = timeout) de uma falha rapida: ver
        // DETAIL_DEFERRED_AFTER_TIMEOUT em executarRodada().
        if (!transitorio || i === tentativas) return { erro: (e.stderr?.toString() || e.message || "").slice(0, 200), status: 0, tentativas: i, retry_permitido: transitorio, codigo: cod, foiARede };
      }
    }
    // O SALTO PEDE LICENCA OUTRA VEZ: volta ao topo do laco, a `licenca()`.
    if (r.status >= 300 && r.status < 400 && r.destino) { atual = r.destino; continue; }
    const { destino, ...resposta } = r;
    return { ...resposta, foiARede, ...(atual !== url ? { URL_FINAL: atual } : {}) };
  }
  return { erro: `mais de ${CORTESIA.cfg.MAX_SALTOS} redireccionamentos a partir de ${url}`, status: 0, tentativas: 1, foiARede, retry_permitido: false };
}

// ---------- cadencia ----------
export function estadoDeCadencia(c, ultimaObs, mudou) {
  const provada = /provado/i.test(String(c.OBSERVED_FREQUENCY));
  if (mudou) return { CADENCE_STATE: "UPDATED", EXPECTED_NEXT_UPDATE: provada ? "calculavel" : "UNKNOWN" };
  if (!provada) return { CADENCE_STATE: "CADENCE_UNKNOWN", EXPECTED_NEXT_UPDATE: "UNKNOWN", nota: "sem cadencia provada esta fonte NUNCA pode ser acusada de atraso" };
  const dias = Number((String(c.OBSERVED_FREQUENCY).match(/^(\d+)D/) || [])[1]);
  if (!dias || !ultimaObs?.SOURCE_DATE_ISO) return { CADENCE_STATE: "EXPECTED_NO_CHANGE", EXPECTED_NEXT_UPDATE: "UNKNOWN" };
  const prox = new Date(Date.parse(ultimaObs.SOURCE_DATE_ISO) + dias * 864e5);
  const atrasado = Date.now() > prox.getTime() + 864e5;   // 1 dia de folga
  return { CADENCE_STATE: atrasado ? "OVERDUE_UPDATE" : "EXPECTED_NO_CHANGE", EXPECTED_NEXT_UPDATE: prox.toISOString().slice(0, 10) };
}

// ---------- alvos por fonte ----------
// Cada alvo: { url, nome, documentIdDe(buf) -> {DOCUMENT_ID, SOURCE_DATE, FACT_TIME} }
export async function alvosDe(sourceId) {
  const c = CONTRACTS[sourceId];
  // ── O CONTRATO MANDA PRIMEIRO, E O SWITCH FICA PARA TRÁS ─────────────────
  // ⚠️ MEDIDO: este `switch` tinha SETE fontes escritas à mão, e uma fonte
  // sem `case` recebia «fonte sem alvo definido no piloto» — mesmo com
  // contrato completo e site a responder HTTP 200. Foi o que aconteceu a
  // `IT-T3-011` na Big Collection.
  //
  //     SOURCE_ID NÃO É DESPACHANTE. O CONTRATO É.
  //
  // Quem declara `ACQUISITION` é servido pelo motor declarativo e NÃO passa
  // por baixo. Quem ainda não declara continua exactamente como estava — os
  // sete `case` não se tocam, e por isso nenhuma fonte que já funcionava
  // muda de comportamento.
  //
  //     MIGRAR É ABRIR UM CAMINHO NOVO, NÃO FECHAR O ANTIGO À FORÇA.
  //
  // O dia em que o último `case` tiver `ACQUISITION`, o `switch` inteiro sai
  // — e sai por ficar vazio, não por alguém o apagar com pressa.
  // SOC2 (D17.4): uma fonte com `COLETADO_POR` nao e deste motor. Sem esta
  // guarda, `alvosDoContrato` lancava «ADAPTER_ID ... nao esta no registry» e,
  // como o ciclo da rodada nao apanha excecoes, UMA fonte destas derrubava a
  // corrida inteira. Agora e um resultado por fonte, com o nome de quem a colhe.
  if (c && c.COLETADO_POR) {
    const cp = c.COLETADO_POR;
    return { erro: `COLETADO_POR_OUTRO_EXECUTOR: ${cp.EXECUTOR}/${cp.FASE} — este motor nao colhe ${sourceId}` };
  }
  if (c && c.ACQUISITION) {
    return await alvosDoContrato(sourceId, c, { buscar: baixar, adapters: ADAPTERS });
  }
  switch (sourceId) {
    case "IT-T3-005":
      return [{ url: c.CANONICAL_ENTRY_URL, nome: "monitoraggio.html" }];
    case "IT-T2-002":
      // No piloto medimos 4. Na operacao forward-only medimos as 29 publicadas.
      // As zonas 17, 18 e 19 devolvem 404 consistente: o site nao as publica. Fato da fonte.
      const zonas = globalThis.__ARPAV_TODAS
        ? Array.from({ length: 32 }, (_, i) => i + 1).filter(n => ![17, 18, 19].includes(n))
        : [1, 9, 16, 24];
      return zonas.map(n => ({ url: `https://www.arpa.veneto.it/risorse/data-agrometeo/agrometeo/32zone/agro_${String(n).padStart(2, "0")}.pdf`, nome: `agro_${String(n).padStart(2, "0")}.pdf`, zone: n }));
    case "IT-T2-004":
      return [{ url: "http://www.sias.regione.sicilia.it/NHEOWL0530_00.html", nome: "NHEOWL0530_00.html", table: "PRECIPITAZIONE_GIORNALIERA" }];
    case "IT-T3-010": {
      const idx = await baixar("http://www.apol.it");
      if (idx.erro || idx.status !== 200) return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
      const html = idx.buf.toString("latin1");
      const links = [...html.matchAll(/href="([^"]*Bollettino_Mosca[^"]*\.pdf)"/gi)].map(m => new URL(m[1], "http://www.apol.it").href);
      if (links.length === 0) return { erro: "EMPTY_LIST — o indice nao listou nenhum boletim. Isto e FAILED, nao zero documentos." };
      const atual = links[0];
      return [{ url: atual, nome: atual.split("/").pop() }];
    }
    case "IT-T3-002": {
      const idx = await baixar("https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/SA_2026.html");
      if (idx.erro || idx.status !== 200) return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
      // os href do indice sao RELATIVOS ("pdf/SA-02-09.pdf"), nao absolutos — resolver contra a pagina
      const base = "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/";
      const links = [...idx.buf.toString("latin1").matchAll(/href="([^"]*SA-\d{2}-\d{2}\.pdf)"/gi)].map(m => new URL(m[1], base).href);
      if (links.length === 0) return { erro: "EMPTY_LIST — indice sem boletins. FAILED." };
      return [{ url: links[0], nome: links[0].split("/").pop() }];
    }
    case "IT-T3-008": {
      const idx = await baixar("https://www.agrometeopuglia.it/bollettini");
      if (idx.erro || idx.status !== 200) return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
      const links = [...idx.buf.toString("latin1").matchAll(/href="([^"]*Notiziario_Agrometeorologico_N\d+_[\d-]+\.pdf)"/gi)].map(m => new URL(m[1], "https://www.agrometeopuglia.it").href);
      if (links.length === 0) {
        // ACHADO: o indice de agrometeopuglia.it e renderizado por JavaScript — o curl nao ve os links.
        // Isto NAO e lista vazia da fonte: e limite do nosso instrumento. Por isso NAO e EMPTY_LIST/FAILED.
        // Caimos para a ROTA PREVISIVEL que o contrato ja documenta, procurando a edicao corrente
        // para tras a partir de hoje. A descoberta fica marcada como degradada, e o motivo vai no ledger.
        const hoje = new Date();
        for (let volta = 0; volta < 10; volta++) {
          const d = new Date(hoje.getTime() - volta * 864e5);
          const dd = String(d.getUTCDate()).padStart(2, "0"), mm = String(d.getUTCMonth() + 1).padStart(2, "0"), aa = d.getUTCFullYear();
          // o numero da semana nao e adivinhavel: varremos os numeros plausiveis da temporada
          for (const n of [37, 36, 35]) {
            const u = `https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/${aa}/Notiziario_Agrometeorologico_N${n}_${dd}-${mm}-${aa}.pdf`;
            const t = await baixar(u, 1);
            if (!t.erro && t.status === 200 && t.buf?.length > 100000 && t.buf.subarray(0,4).toString("latin1") === "%PDF")
              return [{ url: u, nome: u.split("/").pop(), descoberta_degradada: "INDEX_REQUIRES_BROWSER — indice e JavaScript; caiu para a rota previsivel do contrato" }];
          }
        }
        return { erro: "indice exige navegador E a rota previsivel nao achou edicao nos ultimos 10 dias" };
      }
      return [{ url: links[0], nome: links[0].split("/").pop() }];
    }
    case "IT-T4-001": {
      const idx = await baixar("https://www.dati.salute.gov.it/it/dataset/fitosanitari/");
      if (idx.erro || idx.status !== 200) return { erro: `pagina inacessivel: ${idx.erro || idx.status}` };
      const m = idx.buf.toString("latin1").match(/opendata\/(PROD_FTS_6_(\d{8})\.csv)/);
      if (!m) return { erro: "EMPTY_LIST — nenhuma versao de CSV anunciada na pagina. FAILED." };
      return [{ url: `https://www.dati.salute.gov.it/sites/default/files/opendata/${m[1]}`, nome: m[1], sourceVersion: m[2] }];
    }
  }
  return { erro: "fonte sem alvo definido no piloto" };
}

// ---------- identidade semantica ----------
function identidade(sourceId, alvo, buf) {
  // ── A IDENTIDADE DECLARATIVA VEM PRIMEIRO ────────────────────────────────
  // ⚠️ MEDIDO: esta funcao tinha NOVE ramos por SOURCE_ID — mais do que o
  // `alvosDe`. Generalizar so a descoberta produziria o falso fechamento
  // «DISCOVERY_GENERIC = YES, IDENTITY_STILL_REQUIRES_SOURCE_CASE = YES».
  //
  // Quem declara `IDENTITY` no contrato e servido pelo motor. Quem nao
  // declara cai no `switch` de sempre, sem mudanca de comportamento.
  //
  // `DOCUMENT_ID_RULE` continua em prosa, para gente, e NAO e lido aqui:
  //     DOCUMENT_ID_RULE_TEXT != IDENTITY_EXECUTABLE_SPEC.
  const _c = CONTRACTS[sourceId];
  if (_c && _c.IDENTITY) {
    const ident = identidadeDoContrato(sourceId, _c, alvo);
    if (ident) return ident;
  }
  // pdftotext 4.06 NAO aceita stdin. Grava temporario, le, apaga.
  const t = () => {
    try {
      const tmp = `${STORE}/.tmp_${sha(buf).slice(0, 10)}.pdf`;
      mkdirSync(STORE, { recursive: true });
      writeFileSync(tmp, buf);
      const out = execFileSync("pdftotext", ["-layout", "-enc", "UTF-8", tmp, "-"], { maxBuffer: 64e6, encoding: "utf8" });
      rmSync(tmp, { force: true });
      return out;
    } catch { return ""; }
  };
  switch (sourceId) {
    case "IT-T3-005": {
      const h = buf.toString("utf8");
      const p = h.match(/Bollettino del periodo dal\s*([\d-]+)\s*al\s*([\d-]+)/);
      const br = s => s ? s.split("-").reverse().join("-") : null;
      return { DOCUMENT_ID: p ? `TERRETRURIA:${p[1]}:${p[2]}` : null, SOURCE_DATE: p ? `${p[1]} a ${p[2]}` : null, SOURCE_DATE_ISO: br(p?.[2]), FACT_TIME: "por ponto — cada ponto traz sua propria data de campionamento" };
    }
    case "IT-T2-002": {
      const s = buf.toString("latin1");
      const g = (s.match(/\/CreationDate\s*\(D:(\d{14})/) || [])[1];
      const iso = g ? `${g.slice(0, 4)}-${g.slice(4, 6)}-${g.slice(6, 8)}` : null;
      return { DOCUMENT_ID: g ? `ARPAV:Z${String(alvo.zone).padStart(2, "0")}:${g}` : null, SOURCE_DATE: iso, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o PDF nao expoe a data do fato medido, so a de geracao" };
    }
    case "IT-T2-004": {
      const h = buf.toString("latin1");
      const w = h.match(/dal\s*(\d{2}\/\d{2}\/\d{4})\s*al\s*(\d{2}\/\d{2}\/\d{4})/);
      const iso = w ? w[2].split("/").reverse().join("-") : null;
      return { DOCUMENT_ID: w ? `SIAS:${alvo.table}:WINDOW_END_${iso}` : null, SOURCE_DATE: w ? `${w[1]} a ${w[2]}` : null, SOURCE_DATE_ISO: iso, FACT_TIME: "por linha — cada celula tem sua propria data" };
    }
    case "IT-T3-002": {
      const m = alvo.nome.match(/^([A-Z]{2})-(\d{2})-(\d{2})\.pdf$/);
      const iso = m ? `2026-${m[3]}-${m[2]}` : null;
      return { DOCUMENT_ID: m ? `CAMPANIA:${m[1]}:${m[2]}-${m[3]}-2026` : null, SOURCE_DATE: m ? `${m[2]}/${m[3]}/2026` : null, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o boletim nao data a observacao de campo" };
    }
    case "IT-T3-010": {
      const txt = t();
      const p = txt.match(/MOSCA DELLE OLIVE\s+(\d{2}\/\d{2}\/\d{4})\s*-\s*(\d{2}\/\d{2}\/\d{4})/);
      const n = alvo.nome.match(/_n_(\d+)_/);
      const compr = (txt.match(/COMPRENSORIO\s*-?\s*([A-Z]{2})\s*-\s*([A-Z ]+)/) || []);
      const iso = p ? p[1].split("/").reverse().join("-") : null;
      return { DOCUMENT_ID: n && p ? `APOL:${p[1].slice(-4)}:N${n[1]}:${(compr[1] || "?") + "-" + (compr[2] || "?").trim()}` : null, SOURCE_DATE: p ? `${p[1]} a ${p[2]}` : null, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o periodo e de validade, nao de observacao" };
    }
    case "IT-T3-008": {
      const n = alvo.nome.match(/_N(\d+)_([\d-]+)\.pdf/);
      const iso = n ? n[2].split("-").reverse().join("-") : null;
      return { DOCUMENT_ID: n ? `ARIF:SETTIMANALE:${iso?.slice(0, 4)}:N${n[1]}` : null, SOURCE_DATE: n ? n[2] : null, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN" };
    }
    case "IT-T4-001": {
      const v = alvo.sourceVersion;
      const iso = v ? `${v.slice(0, 4)}-${v.slice(4, 6)}-${v.slice(6, 8)}` : null;
      return { DOCUMENT_ID: v ? `MINSALUTE:FTS6:${v}` : null, SOURCE_DATE: iso, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o CSV traz datas de registro por linha, nao uma data de fato do arquivo" };
    }
  }
  return { DOCUMENT_ID: null };
}

// ---------- normalizacao (so SIAS neste piloto) ----------
export function normalizarSias(buf) {
  const h = buf.toString("latin1").replace(/&nbsp;/g, " ");
  const txt = h.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<[^>]+>/g, "\n").replace(/\r/g, "");
  const linhas = txt.split("\n").map(s => s.trim()).filter(Boolean);
  const w = h.match(/dal\s*(\d{2}\/\d{2}\/\d{4})\s*al\s*(\d{2}\/\d{2}\/\d{4})/);
  if (!w) return { erro: "sem janela declarada" };
  const ini = new Date(w[1].split("/").reverse().join("-"));
  const fim = new Date(w[2].split("/").reverse().join("-"));
  const dias = [];
  for (let d = new Date(ini); d <= fim; d.setUTCDate(d.getUTCDate() + 1)) dias.push(d.toISOString().slice(0, 10));
  const obs = [];
  for (let i = 0; i < linhas.length; i++) {
    const nome = linhas[i];
    if (!/^[A-ZÀ-Ù][A-Za-zÀ-ù'. -]{3,40}$/.test(nome)) continue;
    const seq = [];
    for (let j = i + 1; j < linhas.length && seq.length < dias.length; j++) {
      if (/^(\d+([.,]\d+)?|--)$/.test(linhas[j])) seq.push(linhas[j]); else break;
    }
    if (seq.length !== dias.length) continue;
    dias.forEach((dia, k) => obs.push({
      STATION: nome, DATE: dia, VARIABLE: "PRECIPITAZIONE_GIORNALIERA",
      VALUE: seq[k] === "--" ? null : Number(seq[k].replace(",", ".")), UNIT: "mm",
      OBSERVATION_KEY: `${nome}|${dia}|PRECIPITAZIONE_GIORNALIERA`
    }));
    i += seq.length;
  }
  return { WINDOW_START: dias[0], WINDOW_END: dias.at(-1), observacoes: obs };
}

// ---------- execucao ----------
// ⚠️ `runId` E OBRIGATORIO, E ISSO E A CORRECCAO DO B1.
// Ate aqui este ficheiro cunhava o proprio `PILOT_RUN_...`. Uma corrida cunhada
// pelo executor existe ANTES de quem coordena saber dela — e a partir dai duas
// camadas sao donas da mesma corrida. A lei ja estava escrita no comentario de
// `collection_run`: «PROVENIENCIA E PROSPECTIVA: nao se preenche elo de
// execucao passada.»
//
//     ONE RUN = ONE RUN_ID.  Quem coordena cunha; quem colhe recebe.
//
// Sem `runId` isto REBENTA. Nao ha valor por omissao, e nao se cunha outro:
// cunhar em silencio seria exactamente o defeito que o B1 veio fechar.
export async function executarRodada({ runId = null, nota = "", forcarBuf = null, pularParse = false, apenas = null, arpavZonas = null } = {}) {
  if (!runId || typeof runId !== "string" || !runId.trim()) {
    throw new Error("RUN_ID_AUSENTE: executarRodada() exige runId de quem coordena. "
                    + "Este coletor NAO cunha corrida.");
  }
  globalThis.__ARPAV_TODAS = arpavZonas === "TODAS";
  // ⚠️ ZERA-SE AQUI porque o contador e do modulo, e um teste que corra duas
  // rodadas no mesmo processo somaria a rede da primeira a segunda — e o
  // numero saia maior sem ninguem ter batido a porta.
  REDE.total = 0;
  // A cortesia tambem e de UMA corrida: robots, pedidos por host e pausas
  // recomecam aqui, e a configuracao (pausa, teto) le-se agora — invalida, falha alto.
  reiniciarCortesia();
  // ── NAO HA CONJUNTO POR OMISSAO — BG-06 ────────────────────────────────
  // `apenas ?? PILOT_SOURCES` fazia uma corrida sem fontes nomeadas colher as
  // SETE — e a setima, IT-T3-005, tem ZERO mencoes no Atlas: e candidata
  // (status NEW, verdict NAO SEI). O Atlas e o AGENTS.md ja diziam a lei
  // («o que entra pela porta e candidata, nunca fonte»); o que faltava era
  // este ficheiro obedece-la: a lista do que o coletor SABE percorrer nao e
  // a lista do que uma corrida DEVE colher.
  //
  //     O PADRAO DE UM COLETOR E UMA DECISAO QUE NINGUEM TOMOU DE NOVO.
  //     QUEM COLHE NOMEIA AS FONTES, UMA A UMA. SEM NOME, NAO HA COLHEITA.
  //
  // `PILOT_SOURCES` continua a existir e continua com as sete: e a
  // CAPACIDADE declarada (quem este coletor sabe percorrer), usada para
  // recusar FONTE_DESCONHECIDA. Capacidade nao e aprovacao — HISTORY
  // EXISTS != SOURCE APPROVED — e apagar IT-T3-005 daqui apagaria a verdade
  // de que o corredor recorrente a percorre por declaracao explicita de
  // perfil (candidatas/italy_profiles.mjs), que e outra decisao, de outra
  // missao.
  if (!Array.isArray(apenas) || apenas.length === 0) {
    throw new Error("FONTES_AUSENTES: executarRodada() exige a lista explicita "
                    + "de fontes (`apenas`). Este coletor nao tem conjunto por "
                    + "omissao — sem nome, colheria a candidata IT-T3-005.");
  }
  const FONTES = apenas;
  const anterior = lerLedger();
  const primeira = anterior.length === 0;
  const RUN_ID = runId;
  const STARTED_AT = agora();
  // ⚠️ BYTES INJECTADOS NAO TEM EGRESSO. Com `forcarBuf` nao ha ida a fonte, e
  // medir o IP desta maquina registaria um endereco por onde nada passou —
  // numero com cara de medida. NAO_SE_APLICA e a resposta certa, e e diferente
  // de NAO SEI: aqui a pergunta e que nao faz sentido.
  let egress = forcarBuf ? "NAO_SE_APLICA" : "NAO SEI";
  // ⚠️ A MEDICAO DO EGRESSO NAO PASSA POR `baixar()`, DE PROPOSITO: ipinfo.io nao e
  // fonte, nao entra no teto de nenhum site nem no robots de ninguem. E a unica
  // saida deste coletor fora do transporte, e esta nomeada aqui.
  if (!forcarBuf) {
    try { egress = JSON.parse((await run("curl", ["-s", "--max-time", "15", "https://ipinfo.io/json"], { encoding: "utf8" })).stdout); } catch { }
  }
  const GIT_HEAD = (() => { try { return execFileSync("git", ["rev-parse", "HEAD"], { encoding: "utf8" }).trim(); } catch { return "NAO SEI"; } })();

  const cont = { SOURCES_ATTEMPTED: 0, HEALTHY: 0, DEGRADED: 0, FAILED: 0, UNKNOWN: 0, NEW_DOCUMENTS: 0, CHANGED_IN_PLACE: 0, SEEN_AGAIN: 0, SEMANTIC_ID_CHANGED_SAME_BYTES: 0, RAW_OBJECTS_CREATED: 0, NORMALIZED_OBSERVATIONS_NEW: 0,
    // ── O CENSO DA INCREMENTALIDADE, NOS NOMES DO BRIEFING ─────────────────
    // `DETAIL_REQUESTS` conta portas batidas, nao documentos: e o numero que
    // diz se a segunda corrida custou rede. `SKIPPED_KNOWN` e a poupanca, e
    // `UNNECESSARY_REFETCHES` e o gate — um pedido a um detalhe ja conhecido
    // SEM razao nomeada. Com a regra ligada tem de dar zero, porque sem razao
    // a regra devolve SKIP e o pedido nao chega a acontecer.
    INDEX_REQUESTS: 0, DETAIL_REQUESTS: 0, DETAIL_NEW: 0, SKIPPED_KNOWN: 0,
    REVALIDATED: 0, UNNECESSARY_REFETCHES: 0, REVISIT_REASONS: {},
    // Materias que ficaram para a proxima corrida porque o site pendurou
    // numa materia anterior DESTA fonte (ver o laco). Nao sao observacoes.
    DETAIL_DEFERRED_AFTER_TIMEOUT: 0,
    // A CORTESIA (A5): pedidos que o transporte NAO deixou sair, por motivo
    // (ROBOTS_PROIBE · ROBOTS_ILEGIVEL · ROBOTS_INDISPONIVEL · TETO_POR_HOST).
    // Nao sao observacoes e nao mexem na saude da fonte. As idas ao robots.txt
    // contam-se a parte: nao sao indice nem materia.
    DETAIL_DEFERRED_BY_COURTESY: 0, DISCOVERY_NOT_REQUESTED_BY_COURTESY: 0,
    COURTESY_REFUSALS: {}, ROBOTS_REQUESTS: 0,
    // Quantas vezes a segunda defesa impediu o livro de mentir.
    VOLATILE_ONLY_NOT_CHANGED: 0 };
  const detalhes = [];
  // ⚠️ A MEMORIA CONSTROI-SE UMA VEZ, ANTES DA CORRIDA, e nao se actualiza a
  // meio de proposito: uma corrida decide com o que o livro sabia quando ela
  // comecou. Se se fosse actualizando, o primeiro alvo de hoje mudaria a
  // decisao sobre o segundo, e duas corridas iguais dariam contas diferentes.
  const memoria = memoriaDosDetalhes(anterior);

  for (const sourceId of FONTES) {
    cont.SOURCES_ATTEMPTED++;
    const c = CONTRACTS[sourceId];
    // O indice revisita-se SEMPRE, e e ele que anuncia o que ha de novo.
    // `alvosDe` gasta zero ou um pedido de indice conforme a estrategia; o
    // `decidirSobreIndice()` esta aqui para que a lei seja lida no codigo e
    // nao so no comentario — ela nao tem excepcao, e por isso nao tem `if`.
    decidirSobreIndice();
    const alvos = await alvosDe(sourceId);
    // ── O INDICE QUE A CORTESIA NAO DEIXOU PEDIR ─────────────────────────────
    // Robots que proibe (ou que nao se deixou ler), teto esgotado: a porta NAO
    // foi batida, por isso nao ha falha da fonte para escrever. A fonte fica
    // UNKNOWN nesta corrida — nao se olhou para ela — e o motivo vai no resumo.
    // O texto «CORTESIA » e o que `baixar()` poe no `erro`, e o motor de rota e
    // os `case` passam-no tal e qual.
    if (alvos?.erro && String(alvos.erro).includes("CORTESIA ")) {
      cont.UNKNOWN++;
      const motivo = (String(alvos.erro).match(/CORTESIA (\w+)/) || [])[1];
      cont.COURTESY_REFUSALS[motivo] = (cont.COURTESY_REFUSALS[motivo] || 0) + 1;
      cont.DISCOVERY_NOT_REQUESTED_BY_COURTESY++;
      detalhes.push({ RUN_ID, SOURCE_ID: sourceId, DOCUMENT_ID: null,
        DECISAO: "DISCOVERY_NOT_REQUESTED_BY_COURTESY", MOTIVO: motivo, PORQUE: alvos.erro,
        LIVRO: "NAO_ESCRITO — um pedido que nao saiu nao e uma observacao",
        COLLECTION_RUN_STARTED_AT: STARTED_AT });
      continue;
    }
    if (alvos?.erro) {
      cont.FAILED++;
      const obs = { RUN_ID, SOURCE_ID: sourceId, DOCUMENT_ID: null, HEALTH_STATE: "FAILED", OBSERVATION_RESULT: "DISCOVERY_FAILED", motivo: alvos.erro, CAPTURED_AT: agora(), COLLECTION_RUN_STARTED_AT: STARTED_AT };
      gravar(obs); detalhes.push(obs); continue;
    }

    let saudeFonte = "HEALTHY";
    // ══ O SITE PENDURADO PAGA UMA VEZ POR CORRIDA, NAO UMA VEZ POR MATERIA ══
    // ⚠️ MEDIDO NA R2 (2026-09-23, provas/recollection_timeout_local.mjs): cada
    // pedido ja tinha tecto (`--max-time 90`, e uma 2.a tentativa porque o
    // codigo 28 e transitorio) — 180 s por endereco. A FONTE nao tinha: um
    // indice que responde e materias que penduram custavam 180 s × cada
    // materia nova. Com o MAX_TARGETS de 30 da coorte sao 90 minutos numa so
    // fonte, numa so corrida.
    //
    // Depois do PRIMEIRO timeout de uma materia, as seguintes desta fonte que
    // iriam a rede ficam para a proxima corrida. Nao se escrevem no livro — uma
    // materia adiada nao foi observada, e escreve-la faria a memoria lembrar
    // uma tentativa que nao houve. Ficam contadas no resumo e em `detalhes`,
    // com o nome. Na corrida seguinte continuam desconhecidas, e vao-se buscar.
    //
    //     UM TIMEOUT E UMA RESPOSTA SOBRE O SITE, NAO SOBRE A MATERIA.
    //     UNKNOWN CONTINUA UNKNOWN: ADIADA != NUNCA.
    let penduradaNestaFonte = null;
    for (const alvo of alvos) {
      // ══ DEFESA 1 · A DECISAO DE IR, TOMADA ANTES DE BATER A PORTA ════════
      // ⚠️ ESTE BLOCO TEM DE FICAR ACIMA DE `baixar()`, E ISSO E A CORRECCAO.
      // Ate 2026-09-22 a pergunta «ja conheco isto?» era feita na linha 502,
      // DEPOIS de os bytes terem atravessado a rede. O resultado, medido nas
      // duas corridas do canario na ops:
      //
      //     RUN2: 39 de 39 detalhes redescarregados
      //           39 de 39 escritos como DOCUMENT_CHANGED_IN_PLACE
      //           dos 32 que tinham par na RUN1, 32 eram RUIDO VOLATIL
      //
      //     REUTILIZAR O ARMAZEM DEPOIS DO DOWNLOAD NAO E
      //     INCREMENTALIDADE: A REDE JA FOI GASTA.
      //
      // A regra nao recebe bytes nem sha — nao os pode ter, porque se os
      // tivesse ja teriamos pago o pedido. Ela decide com o endereco, o que o
      // livro diz da ultima vez, o relogio e o contrato.
      const decisao = decidirSobreDetalhe(alvo.url, {
        memoria, sourceId, contrato: c, agora: agora(),
      });
      if (decisao.DECISAO === "SKIP_KNOWN") {
        cont.SKIPPED_KNOWN++;
        // ⚠️ UM SALTO NAO VAI PARA O LIVRO, E ISSO NAO E DESLEIXO.
        // O livro e um registo de OBSERVACOES, e nao se observou nada: nao
        // ha bytes, nao ha sha, nao ha documento novo. Pior — o vocabulario
        // de `RESULTADOS_COM_DOCUMENTO` nao tem `SKIPPED_KNOWN`, por isso uma
        // linha assim faria `memoriaDosDetalhes()` concluir «nunca se obteve
        // documento deste endereco» e a corrida SEGUINTE voltava a
        // descarregar tudo. O salto envenenaria a memoria que o autorizou.
        //
        //     NAO REGISTAR UM SALTO NAO E ESCONDE-LO:
        //     ELE VAI NO RESUMO DA CORRIDA, CONTADO E COM RAZAO.
        detalhes.push({ RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url,
          DECISAO: "SKIP_KNOWN", PORQUE: decisao.PORQUE,
          LIVRO: "NAO_ESCRITO — um salto nao e uma observacao",
          COLLECTION_RUN_STARTED_AT: STARTED_AT });
        continue;
      }
      if (penduradaNestaFonte) {
        cont.DETAIL_DEFERRED_AFTER_TIMEOUT++;
        detalhes.push({ RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url,
          DECISAO: "DEFERRED_AFTER_TIMEOUT",
          PORQUE: `o site pendurou nesta corrida em ${penduradaNestaFonte} — fica para a proxima`,
          LIVRO: "NAO_ESCRITO — uma materia adiada nao e uma observacao",
          COLLECTION_RUN_STARTED_AT: STARTED_AT });
        continue;
      }
      // ⚠️ A CONTA DA IDA FAZ-SE DEPOIS DE SE SABER QUE A IDA HOUVE (A5). Ate
      // aqui contava-se antes de `baixar()`, porque `baixar()` saia sempre. Com a
      // cortesia dentro do transporte, um pedido pode ser recusado sem sair — e
      // conta-lo como DETAIL_REQUESTS/DETAIL_NEW diria que se bateu a uma porta
      // onde ninguem bateu.
      const contarIda = () => {
        if (decisao.DECISAO === "REVALIDATE") {
          cont.REVALIDATED++;
          cont.REVISIT_REASONS[decisao.RAZAO] = (cont.REVISIT_REASONS[decisao.RAZAO] || 0) + 1;
        } else if (decisao.CONHECIDO) {
          // FETCH a um endereco JA CONHECIDO. A regra so o devolve com razao
          // nomeada (`PREVIOUS_ATTEMPT_FAILED`); sem razao e desperdicio, e e
          // esse o numero que o gate desta missao olha.
          if (!decisao.RAZAO) cont.UNNECESSARY_REFETCHES++;
          else cont.REVISIT_REASONS[decisao.RAZAO] = (cont.REVISIT_REASONS[decisao.RAZAO] || 0) + 1;
        } else {
          cont.DETAIL_NEW++;
        }
        cont.DETAIL_REQUESTS++;
      };

      // ⚠️ OS BYTES INJECTADOS TAMBEM CONTAM COMO IDA AO TRANSPORTE.
      // Apanhado pelo red team desta missao (M8): o contador vivia so dentro
      // de `baixar()`, e por isso uma corrida com `forcarBuf` nao via
      // pedido nenhum. Um ataque que descarregasse ANTES de decidir — que e
      // o defeito «dedup pos-download» em pessoa — passava invisivel na
      // bancada offline, e a bancada offline e onde isto se prova.
      //
      //     UM MEDIDOR QUE SO CONTA A REDE REAL NAO MEDE
      //     UMA CORRIDA SEM REDE. CONTA-SE O TRANSPORTE, VENHA DE ONDE VIER.
      if (forcarBuf) REDE.total++;
      const r = forcarBuf ? { buf: forcarBuf(sourceId, alvo), status: 200, tentativas: 1 } : await baixar(alvo.url);
      // ── A MATERIA QUE A CORTESIA NAO DEIXOU PEDIR ──────────────────────────
      // Robots proibe o caminho, robots ilegivel/indisponivel, teto do site
      // esgotado: o pedido NAO saiu. Nao e observacao (nao vai ao livro), nao e
      // falha da fonte (a saude nao muda) — e adiamento contado, com o motivo,
      // como o DEFERRED_AFTER_TIMEOUT. Um salto recusado A MEIO (`foiARede`) ja
      // bateu a porta e segue como falha de transporte, la em baixo.
      if (r.recusado && !r.foiARede) {
        cont.DETAIL_DEFERRED_BY_COURTESY++;
        cont.COURTESY_REFUSALS[r.recusado] = (cont.COURTESY_REFUSALS[r.recusado] || 0) + 1;
        detalhes.push({ RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url,
          DECISAO: "DEFERRED_BY_COURTESY", MOTIVO: r.recusado, PORQUE: r.erro,
          LIVRO: "NAO_ESCRITO — um pedido que nao saiu nao e uma observacao",
          COLLECTION_RUN_STARTED_AT: STARTED_AT });
        continue;
      }
      contarIda();
      const CAPTURED_AT = agora();

      if (r.erro || r.status !== 200 || !r.buf?.length) {
        saudeFonte = "FAILED";
        if (r.codigo === 28) penduradaNestaFonte = alvo.url;
        const obs = { RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url, DOCUMENT_ID: null, HEALTH_STATE: "FAILED", OBSERVATION_RESULT: "TRANSPORT_OR_EMPTY", motivo: r.erro || `status ${r.status} / ${r.buf?.length ?? 0} bytes`, retries: r.tentativas, CAPTURED_AT, COLLECTION_RUN_STARTED_AT: STARTED_AT };
        gravar(obs); detalhes.push(obs); continue;
      }

      // ---- 1) validacao de bytes ANTES de qualquer parse ----
      const sig = assinatura(r.buf);
      const esperado = c.EXPECTED_SIGNATURE === "%PDF" ? "PDF" : c.EXPECTED_SIGNATURE === "<" ? "HTML" : c.EXPECTED_SIGNATURE === "PK" ? "ZIP" : null;
      const csvOk = !esperado ? String(r.buf.subarray(0, 400)).includes(String(c.EXPECTED_SIGNATURE)) : true;
      if ((esperado && sig !== esperado) || !csvOk) {
        saudeFonte = "FAILED";
        const obs = { RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url, DOCUMENT_ID: null, RAW_SHA256: sha(r.buf), HEALTH_STATE: "FAILED", OBSERVATION_RESULT: "BYTE_VALIDATION_FAILED", motivo: `esperava ${esperado || c.EXPECTED_SIGNATURE}, chegou ${sig} — HTTP 200 nao salva isto`, CAPTURED_AT, COLLECTION_RUN_STARTED_AT: STARTED_AT };
        gravar(obs); detalhes.push(obs); continue;
      }

      // `let` e nao `const`: quando a DEFESA 2 conclui que a mudanca foi so
      // ruido, este campo volta a ser o sha dos bytes PRESERVADOS, para nunca
      // desmentir o ficheiro em `RAW_PATH`. O sha do que chegou agora fica em
      // `RECEIVED_RAW_SHA256`.
      let RAW_SHA256 = sha(r.buf);
      const ident = identidade(sourceId, alvo, r.buf);
      if (!ident.DOCUMENT_ID) {
        saudeFonte = "FAILED";
        const obs = { RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url, DOCUMENT_ID: null, RAW_SHA256, HEALTH_STATE: "FAILED", OBSERVATION_RESULT: "IDENTITY_FAILED", motivo: "nao foi possivel montar DOCUMENT_ID a partir do documento", CAPTURED_AT, COLLECTION_RUN_STARTED_AT: STARTED_AT };
        gravar(obs); detalhes.push(obs); continue;
      }

      // ---- 2) os quatro casos de versionamento ----
      const mesmoDoc = anterior.filter(o => o.SOURCE_ID === sourceId && o.DOCUMENT_ID === ident.DOCUMENT_ID);
      const mesmoSha = anterior.filter(o => o.RAW_SHA256 === RAW_SHA256 && o.SOURCE_ID === sourceId);
      let OBSERVATION_RESULT, DOCUMENT_VERSION_ID;
      // Campos que so nascem quando a segunda defesa fala. Ausentes por
      // omissao: um campo a `null` numa observacao onde a pergunta nem se pos
      // seria uma resposta a pergunta nenhuma.
      let conteudo = null, RECEIVED_RAW_SHA256;

      if (mesmoDoc.some(o => o.RAW_SHA256 === RAW_SHA256)) {
        OBSERVATION_RESULT = "SEEN_AGAIN";                       // CASO A
        DOCUMENT_VERSION_ID = mesmoDoc.find(o => o.RAW_SHA256 === RAW_SHA256).DOCUMENT_VERSION_ID;
        cont.SEEN_AGAIN++;
      } else if (mesmoDoc.length) {
        // ══ DEFESA 2 · BYTES DIFERENTES NAO SAO DOCUMENTO DIFERENTE ════════
        // ⚠️ AQUI NASCIA O FALSO `DOCUMENT_CHANGED_IN_PLACE`, E A PROVA ESTA
        // MEDIDA: dos 32 documentos que apareceram nas DUAS corridas do
        // canario, 32 mudaram de sha e ZERO mudaram de conteudo. 23 deles
        // mudaram de sha com O MESMO NUMERO DE BYTES.
        //
        // Os trechos que mexiam eram seis, e dois SAO A NOSSA PROPRIA VISITA:
        //     <div class="views">134</div> -> 135
        //     article:modified_time = a hora a que NOS pedimos a pagina
        //
        // A pagina regista a visita, a visita muda os bytes, os bytes mudam o
        // sha, e o coletor conclui que o documento mudou — quando o unico que
        // mudou fomos nos a olhar para ele.
        //
        //     VOLATIL NAO E `CHANGED_IN_PLACE`.
        //
        // ⚠️ E ISTO NAO E DEDUP POS-DOWNLOAD A FAZER DE INCREMENTALIDADE. A
        // rede ja foi gasta quando se chega aqui; quem a poupa e a DEFESA 1,
        // la em cima. Esta so impede que o livro minta quando a ida FOI
        // legitima — uma revalidacao com razao nomeada, por exemplo.
        const anteriorDoDoc = mesmoDoc.at(-1);
        let bytesAntes = null;
        try {
          if (anteriorDoDoc?.RAW_PATH && existsSync(anteriorDoDoc.RAW_PATH)) bytesAntes = readFileSync(anteriorDoDoc.RAW_PATH);
        } catch { bytesAntes = null; }

        if (bytesAntes) conteudo = compararConteudo(bytesAntes, r.buf);

        if (conteudo && conteudo.VEREDICTO === "VOLATILE_ONLY" && !conteudo.AVISO) {
          // O documento e o mesmo. Fica a VERSAO que ja estava guardada, e
          // nao nasce um `v4` para arrumar ruido.
          OBSERVATION_RESULT = "SEEN_AGAIN";
          DOCUMENT_VERSION_ID = anteriorDoDoc.DOCUMENT_VERSION_ID;
          cont.SEEN_AGAIN++;
          cont.VOLATILE_ONLY_NOT_CHANGED++;
          // ⚠️ `RAW_SHA256` CONTINUA A SER O SHA DO FICHEIRO EM `RAW_PATH`, e
          // isso e obrigatorio: `medidas/coorte_da_micro_collection.py` acende
          // `SHA_MISMATCH` quando o livro aponta para bytes que nao batem —
          // «o que falta sabe-se que falta; o trocado passa por bom». Os bytes
          // que chegaram AGORA, e que nao se guardam, vao num campo com nome
          // proprio. Sao duas perguntas, e a casa ja separa as duas noutro
          // sitio: `MIME_ASSINATURA` (o que eu medi) != `CONTENT_TYPE` (o que
          // ele disse).
          RECEIVED_RAW_SHA256 = RAW_SHA256;
          RAW_SHA256 = anteriorDoDoc.RAW_SHA256;
        } else {
          OBSERVATION_RESULT = "DOCUMENT_CHANGED_IN_PLACE";      // CASO B
          DOCUMENT_VERSION_ID = `v${mesmoDoc.length + 1}_${RAW_SHA256.slice(0, 12)}`;
          cont.CHANGED_IN_PLACE++;
        }
      } else if (mesmoSha.length) {
        OBSERVATION_RESULT = "SEMANTIC_ID_CHANGED_SAME_BYTES";   // CASO D
        DOCUMENT_VERSION_ID = `v1_${RAW_SHA256.slice(0, 12)}`;
        cont.SEMANTIC_ID_CHANGED_SAME_BYTES++;
      } else {
        OBSERVATION_RESULT = primeira ? "BASELINE_DOCUMENT" : "NEW_DOCUMENT"; // CASO C
        DOCUMENT_VERSION_ID = `v1_${RAW_SHA256.slice(0, 12)}`;
        cont.NEW_DOCUMENTS++;
      }

      // ---- 3) RAW imutavel ANTES de qualquer parse ----
      // ⚠️ AQUI O `SEEN_AGAIN` SAIA SEM `RAW_PATH`, e isso confundia duas coisas:
      //
      //     NAO CRIEI O OBJECTO AGORA   !=   NAO HA BYTES EM LADO NENHUM
      //
      // Quem lia a observacao reencontrada nao tinha como chegar ao documento —
      // e a porta de entrada, sem caminho, preservaria o JSON da colheita como
      // se fosse o documento. `RAW_OBJECT_CREATED` continua a responder «criei
      // agora?»; `RAW_PATH` passa a responder «onde estao os bytes?». Sao duas
      // perguntas. `guardarRaw` ja era idempotente: se o ficheiro esta la,
      // devolve o sitio e nao escreve.
      const g = guardarRaw(sourceId, ident.DOCUMENT_ID, DOCUMENT_VERSION_ID, alvo.nome, r.buf);
      const rawCriado = g.criado, rawDir = g.dir;
      if (g.criado) cont.RAW_OBJECTS_CREATED++;

      // ---- 4) so agora o parse. Se ele explodir, o RAW ja esta salvo. ----
      let parse = null, parseErro = null;
      if (!pularParse) {
        try {
          if (sourceId === "IT-T2-004") {
            const n = normalizarSias(r.buf);
            const chavesVistas = new Set(anterior.flatMap(o => o.OBSERVATION_KEYS || []));
            const novas = (n.observacoes || []).filter(o => !chavesVistas.has(o.OBSERVATION_KEY));
            cont.NORMALIZED_OBSERVATIONS_NEW += novas.length;
            parse = { WINDOW_START: n.WINDOW_START, WINDOW_END: n.WINDOW_END, ROWS_IN_WINDOW: n.observacoes?.length ?? 0, UNIQUE_STATION_DATE_VARIABLE: new Set((n.observacoes || []).map(o => o.OBSERVATION_KEY)).size, NEW_NORMALIZED_OBSERVATIONS: novas.length };
            parse._keys = (n.observacoes || []).map(o => o.OBSERVATION_KEY);
          }
          if (sourceId === "IT-T3-005") {
            const pts = [...r.buf.toString("utf8").matchAll(/reports_points" id="(\d+)"[\s\S]*?Latitudine:\s*([-\d.]+),\s*Longitudine:\s*([-\d.]+)[\s\S]*?Infestazione attiva:\s*([^<]*?)\s*</g)]
              .map(m => ({ POINT_ID: m[1], LAT: +m[2], LON: +m[3], INFESTATION: m[4] }));
            parse = { MONITORING_POINTS: pts.length, COM_COORDENADA: pts.filter(p => Number.isFinite(p.LAT)).length, _pontos: pts };
            if (pts.length < (c.MIN_PONTOS || 0)) { saudeFonte = "FAILED"; parseErro = `${pts.length} pontos, minimo ${c.MIN_PONTOS} — EMPTY != ZERO`; }
          }
        } catch (e) { parseErro = String(e.message).slice(0, 160); }
      }

      const cad = estadoDeCadencia(c, mesmoDoc.at(-1) || anterior.filter(o => o.SOURCE_ID === sourceId).at(-1), OBSERVATION_RESULT !== "SEEN_AGAIN");

      const obs = {
        RUN_ID, SOURCE_ID: sourceId, SOURCE_URL: alvo.url,
        DOCUMENT_ID: ident.DOCUMENT_ID, DOCUMENT_VERSION_ID, RAW_SHA256,
        // ── O QUE ESTA MATERIALIZACAO PRODUZIU ─────────────────────────────
        // A razao do carimbo e uma so: acabou de nascer uma IDENTIDADE
        // DOCUMENTAL. Nao e o PDF, nem o MIME, nem a extensao, nem o nome da
        // fonte, nem o nome deste ficheiro — nenhum desses prova que houve
        // documento. `DOCUMENT_ID` e `DOCUMENT_VERSION_ID` com valor real
        // provam, porque sao o que a casa acabou de construir.
        //
        // E por isso ele e CONDICIONAL e nao constante. As quatro observacoes
        // de falha ali acima nao passam por aqui, e nenhuma delas leva o campo:
        // sem identidade, o alvo nao foi resolvido, e a resposta certa e a
        // AUSENCIA do campo. Escrever `null`, `UNKNOWN` ou `NAO SEI` poria uma
        // confissao num sitio onde so cabe um CONCEPT_ID, e quem lesse depois
        // teria de adivinhar se aquilo era um conceito ou uma desculpa.
        //
        //     ALVO AUSENTE != ALVO DESCONHECIDO != ALVO NENHUM.
        //
        // ⚠️ E ele NAO diz que esta observacao so produz isto. O mesmo boletim
        // pode vir a dar 1045 linhas (IT-T2-004) ou 139 pontos (IT-T3-005), e
        // cada uma dessas unidades tera o alvo dela. Aqui diz-se apenas que a
        // materializacao DOCUMENTAL deste corte e um SOURCE_DOCUMENT.
        ...(ident.DOCUMENT_ID && DOCUMENT_VERSION_ID
            ? { RESOLVED_STRUCTURED_TARGET: SOURCE_DOCUMENT } : {}),
        BYTES: r.buf.length, MIME_ASSINATURA: sig,
        // ── A ESPECIE, COMO A FONTE A DECLAROU ─────────────────────────────
        // ⚠️ `MIME_ASSINATURA` E OUTRA COISA, E POR ISSO AS DUAS FICAM.
        // `MIME_ASSINATURA` e o que NOS medimos nos primeiros bytes (PDF · ZIP
        // · HTML · TEXTO) — uma familia, nao um media type. `CONTENT_TYPE` e o
        // que o SERVIDOR disse. Sao duas testemunhas, e juntar as duas num
        // campo so apagaria a unica que permite compara-las.
        //
        //     O QUE EU MEDI != O QUE ELE DISSE.
        //
        // O nome e `CONTENT_TYPE` porque e assim que `coleta/ingresso.py::
        // DO_COLETOR` o transporta e `leis/artefato.py` o le. Inventar aqui um
        // nome proprio obrigaria a uma traducao a mais, e cada traducao e um
        // sitio onde o campo se pode perder — foi o que ja aconteceu ao
        // `CAPTURED_AT`.
        //
        // Com `forcarBuf` nao houve HTTP: `contentType` vem `undefined`, o
        // campo sai `null`, e a ficha volta ao que fazia antes. Ausencia
        // honesta, e nao um tipo fabricado para uma corrida sem rede.
        CONTENT_TYPE: r.contentType ?? null,
        SOURCE_DATE: ident.SOURCE_DATE, SOURCE_DATE_ISO: ident.SOURCE_DATE_ISO,
        FACT_TIME: ident.FACT_TIME ?? "UNKNOWN",
        CAPTURED_AT, COLLECTION_RUN_STARTED_AT: STARTED_AT,
        OBSERVATION_RESULT,
        HEALTH_STATE: parseErro && saudeFonte === "FAILED" ? "FAILED" : parseErro ? "DEGRADED" : "HEALTHY",
        CADENCE_STATE: cad.CADENCE_STATE, EXPECTED_NEXT_UPDATE: cad.EXPECTED_NEXT_UPDATE,
        DECLARED_FREQUENCY: c.DECLARED_FREQUENCY, OBSERVED_FREQUENCY: c.OBSERVED_FREQUENCY,
        RAW_OBJECT_CREATED: rawCriado, RAW_PATH: rawDir ? `${rawDir}/${alvo.nome}` : null,
        RAW_PRESERVED_BEFORE_PARSE: true,
        // ── O QUE A SEGUNDA DEFESA VIU, quando teve o que comparar ─────────
        // Condicional, como `RESOLVED_STRUCTURED_TARGET`: estes campos so
        // existem quando a pergunta se pos — ou seja, quando ja havia uma
        // versao deste mesmo DOCUMENT_ID para comparar. Numa observacao de
        // documento novo a pergunta nao existe, e a resposta certa e a
        // AUSENCIA do campo, nunca um `null` que se leia como «nao sei».
        ...(conteudo ? {
          NORMALIZATION: conteudo.NORMALIZACAO,
          CONTENT_VERDICT: conteudo.VEREDICTO,
          RAW_CHANGED: conteudo.RAW_CHANGED,
          NORMALIZED_CHANGED: conteudo.NORMALIZED_CHANGED,
          VISIBLE_TEXT_CHANGED: conteudo.VISIBLE_TEXT_CHANGED,
          VOLATILE_DIFFERENCE: conteudo.VOLATILE_DIFFERENCE,
          OLD_NORMALIZED_HASH: conteudo.OLD_NORMALIZED_HASH,
          NEW_NORMALIZED_HASH: conteudo.NEW_NORMALIZED_HASH,
          // ⚠️ SEM DIFF MATERIAL, UM `CHANGED_IN_PLACE` E FALSO POSITIVO. O
          // campo vai escrito para que quem ler o livro nao tenha de
          // acreditar: MATERIAL_DIFF diz se os hashes normalizados diferem.
          MATERIAL_DIFF: conteudo.NORMALIZED_CHANGED,
          VOLATILE_FRAGMENTS: conteudo.TRECHOS_VOLATEIS_ENCONTRADOS,
          ...(conteudo.AVISO ? { NORMALIZER_WARNING: conteudo.AVISO } : {}),
        } : {}),
        // O sha dos bytes que chegaram nesta visita, quando ele difere do
        // que ficou guardado. Presente SO nesse caso — se estivesse sempre,
        // duplicaria `RAW_SHA256` e um leitor distraido compararia o campo
        // errado com o disco.
        ...(RECEIVED_RAW_SHA256 ? { RECEIVED_RAW_SHA256 } : {}),
        DISCOVERY_DEGRADED: alvo.descoberta_degradada ?? null,
        PARSE_ERROR: parseErro,
        parse: parse ? Object.fromEntries(Object.entries(parse).filter(([k]) => !k.startsWith("_"))) : null,
        OBSERVATION_KEYS: parse?._keys || undefined,
        PONTOS: parse?._pontos ? parse._pontos.length : undefined
      };
      gravar(obs); detalhes.push(obs);
      if (obs.HEALTH_STATE === "FAILED") saudeFonte = "FAILED";
      else if (obs.HEALTH_STATE === "DEGRADED" && saudeFonte !== "FAILED") saudeFonte = "DEGRADED";
    }
    cont[saudeFonte]++;
  }

  const FINISHED_AT = agora();
  // INDEX_REQUESTS por subtraccao, que e a unica conta exacta: tudo o que foi
  // a rede menos o que foi a um detalhe. Com `forcarBuf` nao houve rede
  // nenhuma e o numero e zero — o que tambem e verdade.
  cont.INDEX_REQUESTS = Math.max(0, REDE.total - cont.DETAIL_REQUESTS);
  cont.ROBOTS_REQUESTS = CORTESIA.pedidos.ROBOTS;
  const resumo = {
    RUN_ID, STARTED_AT, FINISHED_AT,
    IS_BASELINE: primeira,
    nota_do_baseline: primeira ? "FIRST_RUN = BASELINE — esta execucao NAO pode dizer 'novo desde ontem'. Ela so estabelece o ponto de partida." : null,
    VPN_COUNTRY: egress?.country ?? (forcarBuf ? "NAO_SE_APLICA" : "NAO SEI"),
    EGRESS_IP: egress?.ip ?? (forcarBuf ? "NAO_SE_APLICA" : "NAO SEI"),
    COLLECTOR_VERSION, SOURCE_CONTRACT_VERSION: "italy-contracts-v1", GIT_HEAD,
    nota, contadores: cont,
    // O que a cortesia fez nesta corrida, auditavel: a configuracao em vigor, o
    // estado do robots de cada origem, os pedidos HTTP REAIS por host (robots,
    // indice, materias, saltos e retentativas) e cada recusa com o porque.
    CORTESIA: forcarBuf ? "NAO_SE_APLICA" : {
      PAUSA_MINIMA_S: CORTESIA.cfg.PAUSA_S, TETO_POR_HOST: CORTESIA.cfg.TETO_POR_HOST,
      MAX_SALTOS: CORTESIA.cfg.MAX_SALTOS, EXCECOES: [...EXCECOES_DE_CORTESIA],
      ROBOTS: Object.fromEntries([...CORTESIA.robots].map(([o, r]) => [o, { ESTADO: r.estado, CRAWL_DELAY: r.crawlDelay ?? null, PORQUE: r.porque }])),
      // Chave = o SITE (host sem `www.`), a mesma do teto e da pausa.
      PEDIDOS_POR_HOST: Object.fromEntries(CORTESIA.porHost),
      RECUSAS: CORTESIA.recusas }
  };
  mkdirSync(LEDGER_DIR, { recursive: true });
  appendFileSync(`${LEDGER_DIR}/runs.ndjson`, JSON.stringify(resumo) + "\n");
  return { resumo, detalhes };
}

// ⚠️ ESTA GUARDA NUNCA FOI VERDADE FORA DO WINDOWS, e por isso a CLI deste
// coletor NUNCA CORREU NO LINUX: em POSIX `process.argv[1]` ja comeca por `/`,
// e `file:///` + `/home/...` da `file:////home/...` — quatro barras contra as
// tres de `import.meta.url`. O ficheiro carregava, nao dizia nada, e saia com
// codigo 0: o silencio parecia sucesso.
//
//     CORRER SEM FAZER NADA E SAIR COM ZERO
//     E A FORMA MAIS CARA DE FALHAR.
//
// `pathToFileURL` e a conversao que o proprio Node exporta para isto, e vale
// nos dois sistemas.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  // A CLI tambem NAO cunha. Quem corre a mao passa a corrida a mao — e assim a
  // linha de comando conta a mesma verdade que a rota canonica.
  const args = process.argv.slice(2);
  const rid = (args.find(a => a.startsWith("--run-id=")) || "").split("=")[1];
  if (!rid) {
    console.error("uso: node coleta/italy_pilot_collect.mjs --run-id=<RUN_ID> --fonte=<ID> [--fonte=<ID>...] [nota...]");
    console.error("     este coletor NAO cunha corrida. O RUN_ID vem de quem coordena.");
    process.exit(2);
  }
  // `--fonte=` existe porque o REGISTO ja declara um filtro de fonte, e um
  // filtro declarado que nao chega ao coletor e um filtro que nao filtra.
  // Repete-se para pedir mais do que uma.
  //
  // ⚠️ E E OBRIGATORIO — BG-06. «Sem nenhum, corre o piloto inteiro» deixou
  // de ser verdade: o piloto inteiro incluia IT-T3-005, que nao esta no
  // Atlas. Sem --fonte, esta CLI recusa, como recusa RUN_ID ausente.
  const fontes = args.filter(a => a.startsWith("--fonte="))
                     .map(a => a.split("=")[1]).filter(Boolean);
  if (!fontes.length) {
    console.error("FONTES_AUSENTES: nomeie cada fonte com --fonte=<SOURCE_ID>. "
                  + "Nao ha conjunto por omissao — o padrao antigo colhia a "
                  + "candidata IT-T3-005, que nao esta no Atlas.");
    process.exit(2);
  }
  const desconhecidas = fontes.filter(f => !FONTES_PERCORRIVEIS.includes(f));
  if (desconhecidas.length) {
    console.error(`FONTE_DESCONHECIDA: ${desconhecidas.join(", ")} — este coletor `
                  + `percorre ${FONTES_PERCORRIVEIS.length} fontes com ACQUISITION `
                  + `declarado. Nao se finge que correu.`);
    process.exit(2);
  }
  const { resumo, detalhes } = await executarRodada({
    runId: rid,
    apenas: fontes,
    nota: args.filter(a => !a.startsWith("--run-id=") && !a.startsWith("--fonte=")).join(" ") });
  console.log(JSON.stringify(resumo, null, 1));
  console.log("\nSOURCE_ID     RESULTADO                        SAUDE     CADENCIA            DOCUMENT_ID");
  for (const d of detalhes) {
    console.log(`${d.SOURCE_ID.padEnd(13)} ${String(d.OBSERVATION_RESULT).padEnd(32)} ${String(d.HEALTH_STATE).padEnd(9)} ${String(d.CADENCE_STATE ?? "-").padEnd(19)} ${d.DOCUMENT_ID ?? d.motivo ?? ""}`);
  }
}
