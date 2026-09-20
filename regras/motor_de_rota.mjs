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
// Ele resolve UMA pergunta: «que endereços devo buscar?». Não interpreta
// conteúdo, não normaliza, não decide identidade semântica. Cada espécie
// continua a ter o seu adapter onde a diferença é real.
//
// E NUNCA LÊ PROSA
// ----------------
// O contrato tem campos escritos para gente — `DISCOVERY_METHOD`,
// `RETRIEVAL_METHOD`, `classificacao_honesta`. Eles continuam lá e continuam
// úteis: são o que uma pessoa lê para perceber a fonte. Este motor **não os
// abre**. O que ele lê é `ACQUISITION`, um bloco de dados com vocabulário
// fechado.
//
//     `"DD": "dia com 2 digitos"` DESCREVE. NÃO EXECUTA.
//
// O vocabulário abaixo não foi inventado: foi DERIVADO dos sete `case` que já
// existiam, medindo o que cada um realmente faz.
//
//     3 ESTRATÉGIAS COBREM OS 7 CASOS MEDIDOS.
//     UM QUARTO NOME SERIA ARQUITETURA PARA UM CASO QUE NÃO EXISTE.

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

export class ContratoInvalido extends Error {}

const ehTexto = (v) => typeof v === "string" && v.trim() !== "";

// ── O QUE FAZ UM BLOCO SER EXECUTÁVEL ──────────────────────────────────────
// ⚠️ ESTA FUNÇÃO É A DIFERENÇA ENTRE CONTRATO E DESCRIÇÃO.
// Ela recusa fechado: um bloco que não declara tudo o que a sua estratégia
// exige não é «quase executável» — é documentação. E documentação não corre.
//
//     DECLARAR PELA METADE É NÃO DECLARAR.
export function conferirAquisicao(sourceId, aq) {
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
  }
  if (e === "CUSTOM_ADAPTER") {
    if (!ehTexto(aq.ADAPTER_ID)) throw new ContratoInvalido(`${sourceId}: CUSTOM_ADAPTER sem ADAPTER_ID`);
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

function combinar(template, vars) {
  const nomes = [...String(template).matchAll(/\{([A-Za-z_]+)\}/g)].map((m) => m[1]);
  let saida = [template];
  for (const n of [...new Set(nomes)]) {
    const vals = valoresDe(vars[n]);
    const nova = [];
    for (const base of saida) for (const v of vals) nova.push(base.split(`{${n}}`).join(v));
    saida = nova;
  }
  return saida;
}

// ── A ÚNICA PERGUNTA QUE ESTE MOTOR RESPONDE ───────────────────────────────
// «Que endereços devo buscar para esta fonte?» — e mais nada.
//
// `buscar` é injectado: o motor não conhece HTTP, não conhece o armazém e não
// escreve nada. Isso mantém-no testável sem rede e impede que ele cresça para
// dentro do plano de dados.
//
//     CONTROL PLANE != DATA PLANE.
export async function alvosDoContrato(sourceId, contrato, { buscar, adapters = {} } = {}) {
  const aq = contrato && contrato.ACQUISITION;
  conferirAquisicao(sourceId, aq);

  if (aq.STRATEGY === "STATIC_ENDPOINT") {
    return [{ url: aq.URL, nome: aq.NAME || aq.URL.split("/").pop() }];
  }

  if (aq.STRATEGY === "TEMPLATE_ENUMERATION") {
    return combinar(aq.TEMPLATE, aq.VARS || {})
      .map((url) => ({ url, nome: url.split("/").pop() }));
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
    const re = new RegExp(aq.LINK_PATTERN, "gi");
    const achados = [...texto.matchAll(re)].map((m) => (m[1] !== undefined ? m[1] : m[0]));
    if (achados.length === 0) {
      // EMPTY_LIST não é erro de rede nem de contrato: é o índice a não
      // anunciar nada. Diz-se com esse nome, e não com um zero calado.
      return { erro: "EMPTY_LIST — o indice nao anuncia nenhum alvo que case com LINK_PATTERN" };
    }
    const base = aq.BASE_URL || aq.INDEX_URL;
    const urls = [...new Set(achados.map((h) => new URL(h, base).href))];
    const limite = Number.isInteger(aq.MAX_TARGETS) ? aq.MAX_TARGETS : urls.length;
    return urls.slice(0, limite).map((url) => ({ url, nome: url.split("/").pop() }));
  }

  // CUSTOM_ADAPTER — o contrato NOMEIA; o registry resolve. O despachador
  // central continua sem conhecer SOURCE_ID nenhum.
  const fn = adapters[aq.ADAPTER_ID];
  if (typeof fn !== "function") {
    throw new ContratoInvalido(
      `${sourceId}: ADAPTER_ID ${JSON.stringify(aq.ADAPTER_ID)} não está no registry`);
  }
  return fn({ sourceId, contrato, buscar });
}

// ── IDENTIDADE DECLARATIVA ─────────────────────────────────────────────────
// Medido: `identidade()` tinha NOVE ramos por SOURCE_ID — mais do que o
// discovery. Generalizar só o discovery seria o falso fechamento
// «DISCOVERY_GENERIC = YES, IDENTITY_STILL_REQUIRES_SOURCE_CASE = YES».
//
// O que se generaliza é o caso provado: a identidade que nasce do NOME do
// ficheiro por captura. `DOCUMENT_ID_RULE` continua a existir em prosa, para
// gente, e NÃO é lido aqui.
//
//     DOCUMENT_ID_RULE_TEXT != IDENTITY_EXECUTABLE_SPEC.
export function identidadeDoContrato(sourceId, contrato, alvo) {
  const spec = contrato && contrato.IDENTITY;
  if (!spec || spec.STRATEGY !== "FILENAME_CAPTURE") return null;
  if (!ehTexto(spec.PATTERN) || !ehTexto(spec.DOCUMENT_ID)) {
    throw new ContratoInvalido(`${sourceId}: FILENAME_CAPTURE precisa de PATTERN e DOCUMENT_ID`);
  }
  const m = String(alvo.nome || "").match(new RegExp(spec.PATTERN));
  if (!m) return { DOCUMENT_ID: null, SOURCE_DATE: null, SOURCE_DATE_ISO: null,
                   FACT_TIME: spec.FACT_TIME || "UNKNOWN" };
  const põe = (molde) => String(molde).replace(/\$(\d+)/g, (_, i) => m[Number(i)] ?? "");
  return {
    DOCUMENT_ID: põe(spec.DOCUMENT_ID),
    SOURCE_DATE: spec.SOURCE_DATE ? põe(spec.SOURCE_DATE) : null,
    SOURCE_DATE_ISO: spec.SOURCE_DATE_ISO ? põe(spec.SOURCE_DATE_ISO) : null,
    // ⚠️ `FACT_TIME` NÃO TEM FALLBACK, E ISSO É DELIBERADO.
    // Ele não herda `SOURCE_DATE`, não herda `PUBLISHED_AT`, e não se calcula
    // a partir do nome do ficheiro. A data do documento é quando a fonte o
    // publicou; o tempo do facto é quando a coisa aconteceu no campo — e um
    // boletim que não o diz não passa a dizê-lo por conveniência nossa.
    //
    //     FACT_TIME != PUBLISHED_AT. UNKNOWN CONTINUA UNKNOWN.
    FACT_TIME: spec.FACT_TIME || "UNKNOWN",
  };
}

export const CONTRATO_MOTOR_VERSAO = "route-engine-v1";
