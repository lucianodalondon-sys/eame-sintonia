// SINTONIA EAME — O MOTOR DE ROTA DECLARATIVO
//
// O QUE ELE RESOLVE, E COMO O PROBLEMA FOI MEDIDO
// ------------------------------------------------
// `coleta/italy_pilot_collect.mjs` escolhia COMO descobrir o documento por
// `switch (sourceId)`. Medido: 20 ramos por SOURCE_ID, dos quais 7 em
// `alvosDe` e 9 em `identidade`. Uma fonte sem `case` devolvia
// «fonte sem alvo definido no piloto» — e foi exactamente isso que aconteceu
// com `IT-T3-011` na Big Collection, que eu classifiquei erradamente como
// falha da fonte quando o site respondia HTTP 200.
//
//     A FONTE NÃO É O DESPACHANTE. O CONTRATO É.
//
// O QUE ELE NÃO É, E ISSO É A LEI
// --------------------------------
//     GENERIC TRAVERSAL != UNIVERSAL PARSER.
//
// Ele resolve DUAS perguntas: «que endereços devo buscar?» e «que identidade
// tem o que chegou?». Não normaliza, não extrai linhas, não decide o que o
// documento SIGNIFICA. Cada espécie continua a ter o seu parser onde a
// diferença é real.
//
// E NUNCA LÊ PROSA
// ----------------
// O contrato tem campos escritos para gente — `DISCOVERY_METHOD`,
// `RETRIEVAL_METHOD`, `DOCUMENT_ID_RULE`, `classificacao_honesta`. Eles
// continuam lá e continuam úteis: são o que uma pessoa lê para perceber a
// fonte. Este motor **não os abre**. O que ele lê é `ACQUISITION` e
// `IDENTITY`, blocos de dados com vocabulário fechado.
//
//     `"DD": "dia com 2 digitos"` DESCREVE. NÃO EXECUTA.
//
// O vocabulário abaixo não foi inventado: foi DERIVADO dos sete `case` que
// existiam, medindo o que cada um realmente faz.
//
//     3 ESTRATÉGIAS COBREM OS 7 CASOS MEDIDOS.
//     UM QUARTO NOME SERIA ARQUITETURA PARA UM CASO QUE NÃO EXISTE.
//
// O QUE A V2 ACRESCENTOU, E PORQUÊ (cutover dos 7 `case`)
// --------------------------------------------------------
// Ao migrar os sete `case` para contrato, mediu-se o que faltava ao motor v1
// para os servir SEM inventar nada:
//
//   · 4 dos 7 montam a identidade a partir do CONTEÚDO do documento (a data
//     no corpo do HTML, o `/CreationDate` do PDF, o cabeçalho lido por
//     pdftotext). `FILENAME_CAPTURE` não chega. Nasce `CONTENT_CAPTURE`: a
//     MESMA operação (regex com grupos → molde), sobre uma fonte de texto
//     declarada. Uma capacidade partilhada, não quatro.
//   · 1 dos 7 (IT-T3-008) tem um FALLBACK de rota previsível quando o índice
//     exige navegador, e marca a descoberta como DEGRADADA. Nasce
//     `ACQUISITION.FALLBACK`: uma segunda aquisição que só corre se a primeira
//     devolver EMPTY_LIST, e cujos alvos carregam `descoberta_degradada`.
//     Perder esse sinal transformaria descoberta degradada em descoberta
//     normal — que é mentir no ledger.
//   · 1 dos 7 (IT-T2-002) tinha DUAS listas de zonas: as 4 do piloto e as 29
//     publicadas. Nasce `SUBCONJUNTOS`: o contrato declara o subconjunto com
//     nome, e quem corre escolhe-o. O despachador não conhece nem zonas nem
//     SOURCE_ID.
//
//     O MOTOR NÃO CONHECE HTTP, NÃO CONHECE pdftotext, NÃO CONHECE O RELÓGIO.
//     TUDO ISSO ENTRA INJECTADO — E POR ISSO ELE TESTA-SE SEM REDE.

export const ESTRATEGIAS = Object.freeze([
  // O endereço está escrito no contrato e não muda. Dois casos medidos:
  // `IT-T3-005` e `IT-T2-004`.
  "STATIC_ENDPOINT",
  // O endereço nasce de um molde com variáveis, e cada variável tem PROVIDER
  // declarado. Um caso medido: `IT-T2-002` (32 zonas do ARPAV).
  "TEMPLATE_ENUMERATION",
  // Abre-se um índice e extraem-se as ligações que casam com um padrão.
  // Quatro casos medidos: `IT-T3-002`, `IT-T3-008`, `IT-T3-010`, `IT-T4-001`.
  "HTML_LINK_DISCOVERY",
  // A porta de saída honesta: quando a fonte exige lógica que o vocabulário
  // finito não descreve, o contrato NOMEIA um adapter registado. Ele não
  // carrega o código — carrega o nome.
  "CUSTOM_ADAPTER",
]);

// Como uma variável de molde recebe valor. Também derivado do que existe.
export const PROVIDERS = Object.freeze([
  "LITERAL",   // valor fixo escrito no contrato
  "ENUM",      // lista fechada de valores — o `PROV: ["AV","BN",...]` já medido
  "RANGE",     // intervalo numérico inteiro, com zeros à esquerda opcionais
]);

// As estratégias de identidade. Duas, e as duas são a mesma operação
// (regex com grupos → molde) sobre fontes de texto diferentes.
export const ESTRATEGIAS_DE_IDENTIDADE = Object.freeze([
  "FILENAME_CAPTURE",   // um padrão sobre o nome do ficheiro — o caso v1
  "CONTENT_CAPTURE",    // vários padrões, cada um sobre uma fonte de texto declarada
]);

// De onde um `CONTENT_CAPTURE` lê o texto. Vocabulário fechado, e cada
// entrada corresponde a um leitor INJECTADO pelo coletor: o motor nunca abre
// um ficheiro nem chama um programa.
export const FONTES_DE_TEXTO = Object.freeze([
  "FILENAME",     // o nome do alvo (o mesmo que FILENAME_CAPTURE usa)
  "URL",          // o endereço do alvo — a identidade honesta de quem não expõe outra
                  // (SAME_URL != SAME_DOCUMENT continua a valer: bytes novos no mesmo
                  // endereço são DOCUMENT_CHANGED_IN_PLACE, nunca um documento a menos)
  "RAW_LATIN1",   // os bytes crus lidos como latin1 (metadados de PDF, HTML antigo)
  "RAW_UTF8",     // os bytes crus lidos como utf8 (HTML moderno)
  "PDF_TEXT",     // o texto extraído do PDF (pdftotext, injectado pelo coletor)
]);

export class ContratoInvalido extends Error {}

const ehTexto = (v) => typeof v === "string" && v.trim() !== "";

// ── O QUE FAZ UM BLOCO SER EXECUTÁVEL ──────────────────────────────────────
// ⚠️ ESTA FUNÇÃO É A DIFERENÇA ENTRE CONTRATO E DESCRIÇÃO.
// Ela recusa fechado: um bloco que não declara tudo o que a sua estratégia
// exige não é «quase executável» — é documentação. E documentação não corre.
//
//     DECLARAR PELA METADE É NÃO DECLARAR.
export function conferirAquisicao(sourceId, aq, { ehFallback = false } = {}) {
  if (!aq || typeof aq !== "object") {
    throw new ContratoInvalido(`${sourceId}: sem bloco ACQUISITION`);
  }
  const e = aq.STRATEGY;
  if (!ESTRATEGIAS.includes(e)) {
    throw new ContratoInvalido(
      `${sourceId}: STRATEGY ${JSON.stringify(e)} fora do vocabulário fechado ` +
      `(${ESTRATEGIAS.join(", ")})`);
  }
  if (e === "STATIC_ENDPOINT") {
    if (!ehTexto(aq.URL)) throw new ContratoInvalido(`${sourceId}: STATIC_ENDPOINT sem URL`);
  }
  if (e === "TEMPLATE_ENUMERATION") {
    if (!ehTexto(aq.TEMPLATE)) throw new ContratoInvalido(`${sourceId}: TEMPLATE_ENUMERATION sem TEMPLATE`);
    const vars = [...String(aq.TEMPLATE).matchAll(/\{([A-Za-z_]+)\}/g)].map((m) => m[1]);
    const dec = aq.VARS || {};
    for (const v of vars) {
      const spec = dec[v];
      if (!spec) {
        // ⚠️ O DEFEITO CENTRAL DA V1, NOMEADO: um molde com `{NN}` e nenhuma
        // instrução sobre o que é `NN`. `IT-T2-001` tinha exactamente isto.
        throw new ContratoInvalido(
          `${sourceId}: a variável {${v}} do TEMPLATE não tem provider em VARS. ` +
          `Um molde sem provider é uma frase, não uma rota.`);
      }
      if (!PROVIDERS.includes(spec.PROVIDER)) {
        // E isto apanha a prosa: `"dia com 2 digitos"` não é um PROVIDER.
        throw new ContratoInvalido(
          `${sourceId}: {${v}} declara PROVIDER ${JSON.stringify(spec.PROVIDER)}, ` +
          `que não é do vocabulário (${PROVIDERS.join(", ")}). ` +
          `Prosa descreve; não executa.`);
      }
      if (spec.PROVIDER === "LITERAL" && spec.VALUE === undefined) {
        throw new ContratoInvalido(`${sourceId}: {${v}} LITERAL sem VALUE`);
      }
      if (spec.PROVIDER === "ENUM" && !Array.isArray(spec.VALUES)) {
        throw new ContratoInvalido(`${sourceId}: {${v}} ENUM sem VALUES`);
      }
      if (spec.PROVIDER === "RANGE" &&
          !(Number.isInteger(spec.FROM) && Number.isInteger(spec.TO))) {
        throw new ContratoInvalido(`${sourceId}: {${v}} RANGE sem FROM/TO inteiros`);
      }
    }
    // ── SUBCONJUNTOS ─────────────────────────────────────────────────────
    // Um subconjunto restringe uma variável a valores que JÁ ESTÃO no
    // provider. Um subconjunto que inventa um valor novo não é subconjunto:
    // é uma segunda lista, e a casa já mediu o que custa ter duas.
    for (const [nome, sub] of Object.entries(aq.SUBCONJUNTOS || {})) {
      if (!sub || typeof sub !== "object") {
        throw new ContratoInvalido(`${sourceId}: SUBCONJUNTOS.${nome} não é um objecto`);
      }
      for (const [v, vals] of Object.entries(sub)) {
        if (!dec[v]) throw new ContratoInvalido(`${sourceId}: SUBCONJUNTOS.${nome} restringe {${v}}, que o TEMPLATE não tem`);
        if (!Array.isArray(vals) || vals.length === 0) throw new ContratoInvalido(`${sourceId}: SUBCONJUNTOS.${nome}.${v} tem de ser uma lista não vazia`);
        const todos = new Set(valoresDe(dec[v]));
        for (const x of vals) {
          if (!todos.has(String(x))) {
            throw new ContratoInvalido(
              `${sourceId}: SUBCONJUNTOS.${nome}.${v} contém ${JSON.stringify(x)}, ` +
              `que não está no provider de {${v}}. Subconjunto não inventa valor.`);
          }
        }
      }
    }
  }
  if (e === "HTML_LINK_DISCOVERY") {
    if (!ehTexto(aq.INDEX_URL)) throw new ContratoInvalido(`${sourceId}: HTML_LINK_DISCOVERY sem INDEX_URL`);
    if (!ehTexto(aq.LINK_PATTERN)) throw new ContratoInvalido(`${sourceId}: HTML_LINK_DISCOVERY sem LINK_PATTERN`);
    // ⚠️ O PADRÃO É DADO, E NÃO CÓDIGO. É compilado com `new RegExp` sobre uma
    // string do contrato — não há `eval`, não há função serializada, não há
    // expressão livre. Um padrão que não compila é contrato inválido, e
    // descobre-se AQUI, na conferência, e não a meio de uma corrida.
    try { new RegExp(aq.LINK_PATTERN, "i"); }
    catch (err) { throw new ContratoInvalido(`${sourceId}: LINK_PATTERN não compila: ${err.message}`); }
    // ── MATCH: onde o padrão se aplica ─────────────────────────────────────
    // "HTML" (omissão): o padrão corre sobre o texto do índice, e o grupo 1
    //   é o endereço — o modo dos 4 `case` migrados.
    // "URL": extraem-se TODOS os href, resolvem-se contra o índice, e o
    //   padrão corre sobre cada endereço ABSOLUTO. É o modo que a tabela de
    //   fontes onboarded (SOURCE-COLLECTION-READINESS-V1) já provara em
    //   2026-09-18 sobre 107 fontes; aqui entra como variante do mesmo
    //   HTML_LINK_DISCOVERY, e não como quarta estratégia.
    if (aq.MATCH !== undefined && !["HTML", "URL"].includes(aq.MATCH)) {
      throw new ContratoInvalido(`${sourceId}: MATCH ${JSON.stringify(aq.MATCH)} fora do vocabulário (HTML, URL)`);
    }
    if (aq.STRIP_SUFFIX !== undefined && !ehTexto(aq.STRIP_SUFFIX)) {
      throw new ContratoInvalido(`${sourceId}: STRIP_SUFFIX tem de ser texto não vazio`);
    }
    if (aq.SAME_HOST !== undefined && typeof aq.SAME_HOST !== "boolean") {
      throw new ContratoInvalido(`${sourceId}: SAME_HOST tem de ser true/false`);
    }
  }
  if (e === "CUSTOM_ADAPTER") {
    if (!ehTexto(aq.ADAPTER_ID)) throw new ContratoInvalido(`${sourceId}: CUSTOM_ADAPTER sem ADAPTER_ID`);
  }
  // ── FALLBACK ───────────────────────────────────────────────────────────
  // Um fallback é OUTRA aquisição, conferida pelas mesmas regras, mais um
  // motivo de degradação obrigatório. Sem motivo, o alvo do fallback sairia
  // igual a um alvo normal — e o ledger deixaria de saber que o índice não
  // respondeu. Um fallback não tem fallback: dois degraus já são um sinal de
  // que a rota principal está morta, e isso resolve-se no contrato, não com
  // uma escada.
  if (aq.FALLBACK !== undefined) {
    if (ehFallback) throw new ContratoInvalido(`${sourceId}: FALLBACK dentro de FALLBACK`);
    if (!ehTexto(aq.FALLBACK?.DEGRADED_REASON)) {
      throw new ContratoInvalido(
        `${sourceId}: FALLBACK sem DEGRADED_REASON. Um fallback calado ` +
        `transforma descoberta degradada em descoberta normal.`);
    }
    conferirAquisicao(sourceId, aq.FALLBACK, { ehFallback: true });
  }
  return true;
}

function valoresDe(spec) {
  if (spec.PROVIDER === "LITERAL") return [String(spec.VALUE)];
  if (spec.PROVIDER === "ENUM") return spec.VALUES.map(String);
  const largura = Number.isInteger(spec.PAD) ? spec.PAD : 0;
  const fora = [];
  for (let i = spec.FROM; i <= spec.TO; i++) {
    const s = String(i);
    fora.push(largura > 0 ? s.padStart(largura, "0") : s);
  }
  return fora;
}

// Combina o molde com os valores. Cada resultado carrega os valores que o
// produziram (`VARS`), porque a identidade pode precisar de saber QUE zona
// este endereço é — e lê-lo do alvo é mais honesto do que reinferi-lo.
function combinar(template, vars, restricao = null) {
  const nomes = [...String(template).matchAll(/\{([A-Za-z_]+)\}/g)].map((m) => m[1]);
  let saida = [{ url: template, VARS: {} }];
  for (const n of [...new Set(nomes)]) {
    const vals = restricao && Array.isArray(restricao[n]) ? restricao[n].map(String) : valoresDe(vars[n]);
    const nova = [];
    for (const base of saida) for (const v of vals) {
      nova.push({ url: base.url.split(`{${n}}`).join(v), VARS: { ...base.VARS, [n]: v } });
    }
    saida = nova;
  }
  return saida;
}

// ── MATCH: "URL" — as ligações de um índice, endereço a endereço ──────────
// Derivado, e não inventado, do `linksDaEntrada()` que a missão
// SOURCE-COLLECTION-READINESS-V1 provou sobre 107 fontes em 2026-09-18.
// O que fica de fora fica de fora por medição: ativos estáticos, paginação
// e feeds não são documentos; a própria entrada não é um documento seu.
const ATIVOS_ESTATICOS = /\.(css|js|png|jpe?g|gif|svg|ico|woff2?|xml|rss)(\?|#|$)/i;
const PAGINACAO = /\/page\/\d+\/?(\?|#|$)|[?&](page|pagina|pag|p)=\d+/i;
const FEED = /\/(feed|rss|atom)\/?(\?|#|$)/i;

export function ligacoesDoIndice(html, aq) {
  const padrao = new RegExp(aq.LINK_PATTERN, "i");
  const entrada = aq.INDEX_URL;
  const host = new URL(entrada).hostname.replace(/^www\./, "");
  const entradaNorm = entrada.replace(/\/+$/, "");
  const vistos = new Set(), fora = [];
  for (const m of String(html).matchAll(/href\s*=\s*["']([^"'#]+)["']/gi)) {
    let u;
    try { u = new URL(m[1].trim(), entrada).href; } catch { continue; }
    if (!/^https?:/i.test(u)) continue;
    if (aq.STRIP_SUFFIX && u.endsWith(aq.STRIP_SUFFIX)) u = u.slice(0, -aq.STRIP_SUFFIX.length);
    if (vistos.has(u)) continue;
    vistos.add(u);
    if (aq.SAME_HOST !== false && new URL(u).hostname.replace(/^www\./, "") !== host) continue;
    if (ATIVOS_ESTATICOS.test(u) || PAGINACAO.test(u) || FEED.test(u)) continue;
    if (u.replace(/\/+$/, "") === entradaNorm) continue;
    if (!padrao.test(u)) continue;
    fora.push(u);
  }
  return fora;
}

// O nome do ficheiro guardado nasce do último troço do caminho; um artigo
// HTML raramente traz extensão, e o armazém precisa de uma.
export function nomeDoAlvo(url, outputType) {
  let nome = "";
  try { nome = decodeURIComponent(new URL(url).pathname.split("/").filter(Boolean).pop() || ""); } catch { }
  // ⚠️ 60 e nao 120: medido na Big Collection 2, com a pasta do documento ja
  // limitada, 9 ficheiros continuavam acima dos 260 caracteres do MAX_PATH do
  // Windows por causa do NOME. Fica a cauda, que e onde vive a extensao.
  nome = nome.replace(/[^A-Za-z0-9._-]+/g, "_").slice(-60);
  const ext = String(outputType || "").toUpperCase() === "PDF" ? ".pdf" : ".html";
  if (!nome) return "documento" + ext;
  if (!/\.[A-Za-z0-9]{1,5}$/.test(nome)) nome += ext;
  return nome;
}

// ── A PRIMEIRA PERGUNTA QUE ESTE MOTOR RESPONDE ────────────────────────────
// «Que endereços devo buscar para esta fonte?»
//
// `buscar` é injectado: o motor não conhece HTTP, não conhece o armazém e não
// escreve nada. Isso mantém-no testável sem rede e impede que ele cresça para
// dentro do plano de dados.
//
//     CONTROL PLANE != DATA PLANE.
//
// Opções:
//   buscar(url, tentativas?)  → { status, buf } | { erro }
//   adapters                  → registry { ADAPTER_ID: fn }
//   subconjunto               → nome de um SUBCONJUNTOS declarado no contrato;
//                               fontes que não o declaram ignoram-no
//   agora                     → () => Date, para adapters que dependem do dia
export async function alvosDoContrato(sourceId, contrato, opcoes = {}) {
  const aq = contrato && contrato.ACQUISITION;
  conferirAquisicao(sourceId, aq);
  const primario = await executarAquisicao(sourceId, contrato, aq, opcoes);
  // Só EMPTY_LIST abre o fallback. Índice inacessível (rede, 403, 500) não é
  // «o índice não anunciou nada» — é «não consegui perguntar», e o fallback
  // esconderia uma fonte caída atrás de uma rota adivinhada.
  if (aq.FALLBACK && primario?.erro && /EMPTY_LIST/.test(primario.erro)) {
    const seg = await executarAquisicao(sourceId, contrato, aq.FALLBACK, opcoes);
    if (seg?.erro) return seg;
    return seg.map((a) => ({ ...a, descoberta_degradada: aq.FALLBACK.DEGRADED_REASON }));
  }
  return primario;
}

async function executarAquisicao(sourceId, contrato, aq, { buscar, adapters = {}, subconjunto = null, agora = null } = {}) {
  if (aq.STRATEGY === "STATIC_ENDPOINT") {
    return [{ url: aq.URL, nome: aq.NAME || aq.URL.split("/").pop() }];
  }

  if (aq.STRATEGY === "TEMPLATE_ENUMERATION") {
    const restricao = subconjunto && aq.SUBCONJUNTOS ? (aq.SUBCONJUNTOS[subconjunto] || null) : null;
    return combinar(aq.TEMPLATE, aq.VARS || {}, restricao)
      .map(({ url, VARS }) => ({ url, nome: url.split("/").pop(), VARS }));
  }

  if (aq.STRATEGY === "HTML_LINK_DISCOVERY") {
    if (typeof buscar !== "function") {
      throw new ContratoInvalido(`${sourceId}: HTML_LINK_DISCOVERY precisa de um leitor`);
    }
    const idx = await buscar(aq.INDEX_URL);
    if (idx.erro || idx.status !== 200) {
      return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
    }
    const texto = idx.buf.toString("latin1");
    const limite = Number.isInteger(aq.MAX_TARGETS) ? aq.MAX_TARGETS : Infinity;
    if (aq.MATCH === "URL") {
      const urls = ligacoesDoIndice(texto, aq);
      if (urls.length === 0) {
        return { erro: "EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PATTERN" };
      }
      return urls.slice(0, limite).map((url) => ({ url, nome: nomeDoAlvo(url, contrato && contrato.OUTPUT_TYPE) }));
    }
    const re = new RegExp(aq.LINK_PATTERN, "gi");
    const achados = [...texto.matchAll(re)].map((m) => (m[1] !== undefined ? m[1] : m[0]));
    if (achados.length === 0) {
      // EMPTY_LIST não é erro de rede nem de contrato: é o índice a não
      // anunciar nada. Diz-se com esse nome, e não com um zero calado.
      return { erro: "EMPTY_LIST — o indice nao anuncia nenhum alvo que case com LINK_PATTERN" };
    }
    const base = aq.BASE_URL || aq.INDEX_URL;
    const urls = [...new Set(achados.map((h) => new URL(h, base).href))];
    return urls.slice(0, limite).map((url) => ({ url, nome: url.split("/").pop() }));
  }

  // CUSTOM_ADAPTER — o contrato NOMEIA; o registry resolve. O despachador
  // central continua sem conhecer SOURCE_ID nenhum. O adapter recebe o SEU
  // bloco (`aq`), porque é lá que estão os parâmetros dele — no contrato, e
  // não no código.
  const fn = adapters[aq.ADAPTER_ID];
  if (typeof fn !== "function") {
    throw new ContratoInvalido(
      `${sourceId}: ADAPTER_ID ${JSON.stringify(aq.ADAPTER_ID)} não está no registry`);
  }
  return fn({ sourceId, contrato, aq, buscar, agora: agora || (() => new Date()) });
}

// ── IDENTIDADE DECLARATIVA ─────────────────────────────────────────────────
// Medido: `identidade()` tinha NOVE ramos por SOURCE_ID — mais do que o
// discovery. Generalizar só o discovery seria o falso fechamento
// «DISCOVERY_GENERIC = YES, IDENTITY_STILL_REQUIRES_SOURCE_CASE = YES».
//
// O que se generaliza é a OPERAÇÃO que os nove ramos faziam: um padrão com
// grupos sobre um texto, e um molde que os recompõe. `DOCUMENT_ID_RULE`
// continua a existir em prosa, para gente, e NÃO é lido aqui.
//
//     DOCUMENT_ID_RULE_TEXT != IDENTITY_EXECUTABLE_SPEC.
export function conferirIdentidade(sourceId, spec) {
  if (!spec || typeof spec !== "object") throw new ContratoInvalido(`${sourceId}: sem bloco IDENTITY`);
  if (!ESTRATEGIAS_DE_IDENTIDADE.includes(spec.STRATEGY)) {
    throw new ContratoInvalido(
      `${sourceId}: IDENTITY.STRATEGY ${JSON.stringify(spec.STRATEGY)} fora do vocabulário ` +
      `(${ESTRATEGIAS_DE_IDENTIDADE.join(", ")})`);
  }
  if (!ehTexto(spec.DOCUMENT_ID)) throw new ContratoInvalido(`${sourceId}: IDENTITY sem DOCUMENT_ID`);
  if (spec.STRATEGY === "FILENAME_CAPTURE") {
    if (!ehTexto(spec.PATTERN)) throw new ContratoInvalido(`${sourceId}: FILENAME_CAPTURE precisa de PATTERN`);
    try { new RegExp(spec.PATTERN); }
    catch (err) { throw new ContratoInvalido(`${sourceId}: PATTERN não compila: ${err.message}`); }
  }
  if (spec.STRATEGY === "CONTENT_CAPTURE") {
    const caps = spec.CAPTURES;
    if (!caps || typeof caps !== "object" || Object.keys(caps).length === 0) {
      throw new ContratoInvalido(`${sourceId}: CONTENT_CAPTURE sem CAPTURES`);
    }
    for (const [nome, c] of Object.entries(caps)) {
      if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(nome)) throw new ContratoInvalido(`${sourceId}: CAPTURES.${nome}: nome inválido`);
      if (!FONTES_DE_TEXTO.includes(c?.FROM)) {
        throw new ContratoInvalido(
          `${sourceId}: CAPTURES.${nome}.FROM ${JSON.stringify(c?.FROM)} fora do vocabulário ` +
          `(${FONTES_DE_TEXTO.join(", ")})`);
      }
      if (!ehTexto(c.PATTERN)) throw new ContratoInvalido(`${sourceId}: CAPTURES.${nome} sem PATTERN`);
      try { new RegExp(c.PATTERN, c.FLAGS || ""); }
      catch (err) { throw new ContratoInvalido(`${sourceId}: CAPTURES.${nome}.PATTERN não compila: ${err.message}`); }
      if (c.REQUIRED === false && !Array.isArray(c.DEFAULTS)) {
        // Uma captura opcional sem valores por omissão deixaria buracos no
        // molde — e um DOCUMENT_ID com buraco é uma identidade a meio.
        throw new ContratoInvalido(`${sourceId}: CAPTURES.${nome} é opcional (REQUIRED=false) e por isso exige DEFAULTS`);
      }
    }
    // Todo `{nome.N}` dos moldes tem de apontar para uma captura declarada.
    for (const campo of ["DOCUMENT_ID", "SOURCE_DATE", "SOURCE_DATE_ISO"]) {
      for (const m of String(spec[campo] || "").matchAll(/\{([A-Za-z_][A-Za-z0-9_]*)\.(\d+)\}/g)) {
        if (!caps[m[1]]) throw new ContratoInvalido(`${sourceId}: ${campo} usa {${m[1]}.${m[2]}}, e não há CAPTURES.${m[1]}`);
      }
    }
  }
  return true;
}

// `leitores` é injectado pelo coletor e é PREGUIÇOSO: só se lê o PDF se
// alguma captura pedir `PDF_TEXT`. Cada leitor devolve uma string.
//
//   leitores = { RAW_LATIN1: () => string, RAW_UTF8: () => string, PDF_TEXT: () => string }
//
// A resposta tem sempre os quatro campos. `DOCUMENT_ID: null` significa que
// uma captura obrigatória não casou — e isso é IDENTITY_FAILED, não uma
// identidade parcial.
export function identidadeDoContrato(sourceId, contrato, alvo, { leitores = {} } = {}) {
  const spec = contrato && contrato.IDENTITY;
  if (!spec) return null;
  conferirIdentidade(sourceId, spec);
  // ⚠️ `FACT_TIME` NÃO TEM FALLBACK, E ISSO É DELIBERADO.
  // Ele não herda `SOURCE_DATE`, não herda `PUBLISHED_AT`, e não se calcula
  // a partir do nome do ficheiro. A data do documento é quando a fonte o
  // publicou; o tempo do facto é quando a coisa aconteceu no campo — e um
  // boletim que não o diz não passa a dizê-lo por conveniência nossa.
  //
  //     FACT_TIME != PUBLISHED_AT. UNKNOWN CONTINUA UNKNOWN.
  const FACT_TIME = spec.FACT_TIME || "UNKNOWN";
  const vazio = { DOCUMENT_ID: null, SOURCE_DATE: null, SOURCE_DATE_ISO: null, FACT_TIME };

  if (spec.STRATEGY === "FILENAME_CAPTURE") {
    const m = String(alvo.nome || "").match(new RegExp(spec.PATTERN));
    if (!m) return vazio;
    const põe = (molde) => String(molde).replace(/\$(\d+)/g, (_, i) => m[Number(i)] ?? "");
    return {
      DOCUMENT_ID: põe(spec.DOCUMENT_ID),
      SOURCE_DATE: spec.SOURCE_DATE ? põe(spec.SOURCE_DATE) : null,
      SOURCE_DATE_ISO: spec.SOURCE_DATE_ISO ? põe(spec.SOURCE_DATE_ISO) : null,
      FACT_TIME,
    };
  }

  // CONTENT_CAPTURE — cada captura lê a sua fonte de texto uma vez.
  const textos = {};
  const textoDe = (de) => {
    if (de === "FILENAME") return String(alvo.nome || "");
    if (de === "URL") return String(alvo.url || "");
    if (!(de in textos)) {
      const ler = leitores[de];
      if (typeof ler !== "function") {
        throw new ContratoInvalido(`${sourceId}: CAPTURES pede ${de}, e o coletor não injectou esse leitor`);
      }
      textos[de] = String(ler() ?? "");
    }
    return textos[de];
  };
  const grupos = {};
  for (const [nome, c] of Object.entries(spec.CAPTURES)) {
    const m = textoDe(c.FROM).match(new RegExp(c.PATTERN, c.FLAGS || ""));
    if (m) {
      // `.trim()` em cada grupo: um padrão como `([A-Z ]+)` apanha o espaço
      // antes do fim da linha, e o `case` medido tirava-o à mão.
      grupos[nome] = m.map((g) => (g == null ? "" : String(g).trim()));
    } else if (c.REQUIRED === false) {
      grupos[nome] = ["", ...c.DEFAULTS.map(String)];
    } else {
      return vazio;
    }
  }
  const põe = (molde) => String(molde).replace(/\{([A-Za-z_][A-Za-z0-9_]*)\.(\d+)\}/g,
    (_, n, i) => grupos[n]?.[Number(i)] ?? "");
  return {
    DOCUMENT_ID: põe(spec.DOCUMENT_ID),
    SOURCE_DATE: spec.SOURCE_DATE ? põe(spec.SOURCE_DATE) : null,
    SOURCE_DATE_ISO: spec.SOURCE_DATE_ISO ? põe(spec.SOURCE_DATE_ISO) : null,
    FACT_TIME,
  };
}

// v2: CONTENT_CAPTURE · ACQUISITION.FALLBACK (com DEGRADED_REASON) ·
// SUBCONJUNTOS · VARS no alvo · adapter recebe o seu bloco e o relógio.
export const CONTRATO_MOTOR_VERSAO = "route-engine-v2";
