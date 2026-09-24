// SINTONIA EAME — A REGRA DE REVISITA
//
// O DEFEITO QUE ISTO FECHA, MEDIDO
// ---------------------------------
// `coleta/italy_pilot_collect.mjs` decide assim (linhas 473-502):
//
//     for (const alvo of alvos) {
//       const r = await baixar(alvo.url);      // ← DESCARREGA
//       ...
//       const mesmoDoc = anterior.filter(...)  // ← e SO AQUI pergunta se ja conhecia
//
// A pergunta «ja conheco isto?» so e feita DEPOIS de os bytes ja terem
// atravessado a rede. O resultado medido na CANONICAL-MICRO-V1:
//
//     segunda visita: 85 de 85 detalhes redescarregados
//     83 de 85 classificados DOCUMENT_CHANGED_IN_PLACE
//     diferenca real: 374 linhas em 86 441 (0,43%), ZERO texto editorial
//
//     REUTILIZAR O ARMAZEM DEPOIS DO DOWNLOAD
//     NAO E INCREMENTALIDADE: A REDE JA FOI GASTA.
//
// ⚠️ E PORQUE COMPARAR BYTES NAO SALVA NADA — O ACHADO CENTRAL
// -----------------------------------------------------------
// Das 374 linhas que diferiram entre as duas visitas aos MESMOS artigos:
//
//      197  carimbo de hora / nonce / sessao
//       55  marcacao de maquina
//       52  nonce do WordPress Download Manager
//       52  farol de analytics com `hid` aleatorio
//       14  CONTADOR DE VISITAS DA PAGINA  <div class="views">365</div> -> 367
//        6  token do Drupal
//
// O contador subiu porque NOS o fizemos subir. A pagina regista a visita, a
// visita muda os bytes, os bytes mudam o sha, e o coletor conclui que o
// documento mudou — quando o unico que mudou fomos nos a olhar para ele.
//
//     A NOSSA VISITA DEIXA PEGADA NA PAGINA.
//     COMPARAR SHA DEPOIS DE VISITAR E MEDIR A PROPRIA PEGADA.
//
// Por isso esta regra NAO recebe bytes, NAO recebe sha e NAO os pode receber.
// Ela decide com o que se sabe ANTES de bater a porta: o endereco, o que o
// livro diz que aconteceu da ultima vez, o relogio, e o contrato.
//
// O QUE ELA DECIDE, E SO ISSO
// ----------------------------
//     INDEX                          pode ser revisitado, sempre
//     DETAIL nova                    -> FETCH
//     DETAIL conhecida com sucesso   -> SKIP por omissao
//
// Revisitar um detalhe conhecido exige uma RAZAO NOMEADA do vocabulario
// fechado abaixo. Sem razao, nao ha revisita — e «nao sei» nao e razao.

export const DECISOES = Object.freeze([
  "FETCH",        // nunca se viu este endereco com sucesso
  "SKIP_KNOWN",   // ja se tem; nao ha razao declarada para tornar a ir
  "REVALIDATE",   // ha razao NOMEADA; volta-se, e diz-se porque
]);

// ── AS CINCO RAZOES, E NENHUMA SEXTA ──────────────────────────────────────
// Derivadas do briefing, palavra por palavra. Uma razao que nao esteja aqui
// nao existe: quem quiser revisitar por outro motivo tem de o ESCREVER aqui
// primeiro, e aí fica medido em vez de acontecer em silencio.
export const RAZOES_DE_REVISITA = Object.freeze([
  "CONTRACT_DECLARES_MUTABLE",     // o contrato diz que o conteudo muda
  "TTL_EXPIRED",                   // o contrato deu prazo, e o prazo passou
  "PREVIOUS_ATTEMPT_FAILED",       // a ultima visita nao trouxe documento
  "CONDITIONAL_REQUEST_AVAILABLE", // ha validador guardado (ETag/Last-Modified)
  "CANONICAL_EVIDENCE_REQUIRES",   // outra evidencia canonica obriga
]);

// ── O QUE CONTA COMO «CONHECIDA COM SUCESSO» ──────────────────────────────
// ⚠️ VOCABULARIO FECHADO, E A DIVISAO NAO E COSMETICA. `SEEN_AGAIN` e sucesso
// (o documento esta na mao); `IDENTITY_FAILED` NAO e (descarregou-se e
// deitou-se fora). Meter os dois no mesmo saco faz uma de duas asneiras:
// ou se salta um endereco de que nunca se guardou nada, ou se torna a
// descarregar um que ja se tem.
export const RESULTADOS_COM_DOCUMENTO = Object.freeze([
  "BASELINE_DOCUMENT",
  "NEW_DOCUMENT",
  "DOCUMENT_CHANGED_IN_PLACE",
  "SEMANTIC_ID_CHANGED_SAME_BYTES",
  "SEEN_AGAIN",
]);

export const RESULTADOS_SEM_DOCUMENTO = Object.freeze([
  "DISCOVERY_FAILED",
  "TRANSPORT_OR_EMPTY",
  "BYTE_VALIDATION_FAILED",
  "IDENTITY_FAILED",
]);

// ── O QUE O CONTRATO PODE DECLARAR SOBRE REVISITA ─────────────────────────
// ⚠️ ISTO NAO LE `UPDATE_BEHAVIOR`, E E DE PROPOSITO.
// `UPDATE_BEHAVIOR` e PROSA: medido nos 186 contratos, tem 172 «NAO SEI» e
// frases como «SOBRESCRITA — janela movel de 11 dias na mesma URL». Uma frase
// descreve; nao executa. Ler prosa aqui seria o mesmo erro que o motor de rota
// ja nomeou (`"DD": "dia com 2 digitos"` DESCREVE, NAO EXECUTA), e traria de
// volta o pior de todos: um campo que o motor promete ler e le mal.
//
// O bloco executavel e `RECOLLECTION`, com vocabulario fechado. Declarar o
// bloco e um acto deliberado de quem conhece a fonte, e nao um efeito de
// redaccao.
export const MUTABILIDADE = Object.freeze(["IMMUTABLE", "MUTABLE", "UNKNOWN"]);

// ══ O DEFEITO QUE A RECOLLECTION-V1 VEIO FECHAR ═══════════════════════════
//
//     RECOLLECTION_UNKNOWN  ≠  NEVER_RECOLLECT
//
// Medido em 2026-09-22, correndo a regra com os quatro casos possiveis:
//
//     contrato SEM bloco       -> lido UNKNOWN   DECLARADO=false -> SKIP_KNOWN
//     contrato com UNKNOWN     -> lido UNKNOWN   DECLARADO=true  -> SKIP_KNOWN
//     contrato com IMMUTABLE   -> lido IMMUTABLE DECLARADO=true  -> SKIP_KNOWN
//     contrato com MUTABLE     -> lido MUTABLE   DECLARADO=true  -> REVALIDATE
//
// Reparar nas duas primeiras linhas ao lado da terceira. `UNKNOWN` e
// `IMMUTABLE` davam **exactamente a mesma decisao**, para sempre, e sem
// deixar rasto: quem nunca foi classificado era tratado como quem foi
// classificado «nunca muda». A leitura da linha 115 estava certa — devolve
// `UNKNOWN`, que e honesto. O que faltava era alguem LER esse `UNKNOWN`.
//
//     `DECLARADO` ja era calculado aqui, e NINGUEM O LIA.
//     O campo que distinguia «o dono sabe» de «ninguem sabe» existia,
//     e a decisao deitava-o fora.
//
// ⚠️ E PORQUE A CORRECCAO NAO E «UNKNOWN PASSA A REVISITAR».
// Seria trocar uma avaria por outra maior: 179 dos 186 contratos nao declaram
// nada, e todos passariam a bater a porta em todas as corridas, sem razao
// nomeada e sem nada para trazer. A paridade acabou de provar
// `UNNECESSARY_REFETCHES = 0`; isso apagava a prova e gastava a rede.
//
//     SALTAR O QUE MUDA CEGA A CASA.
//     REVISITAR TUDO O QUE NAO SE CONHECE INUNDA-A.
//
// A correccao e a terceira porta, e e a que o briefing pediu: o salto por
// ignorancia CONTINUA A SER UM SALTO — mas deixa de ser calado. Passa a
// dizer o nome, e quem nao declarou fica **fora** da Big Collection ate
// declarar. A cegueira deixa de ser um efeito silencioso e passa a ser um
// impedimento visivel.
export const COBERTURA_DE_REVISITA = Object.freeze([
  "DECLARADA",                   // o contrato diz o que acontece ao detalhe
  "BLOCKED_FOR_BIG_COLLECTION",  // ninguem declarou; salta-se, e nao entra na Big Collection
]);

export class RegraInvalida extends Error {}

/**
 * Le `RECOLLECTION` de um contrato. Ausente e resposta: `UNKNOWN`, sem prazo.
 * Um valor fora do vocabulario REPROVA — aceitar um campo sem o implementar
 * e pior do que recusa-lo.
 */
export function recolheitaDoContrato(sourceId, contrato) {
  const r = (contrato && contrato.RECOLLECTION) || null;
  if (!r) return { DETAIL_CONTENT: "UNKNOWN", TTL_SECONDS: null, DECLARADO: false };
  if (!MUTABILIDADE.includes(r.DETAIL_CONTENT)) {
    throw new RegraInvalida(
      `${sourceId}: RECOLLECTION.DETAIL_CONTENT ${JSON.stringify(r.DETAIL_CONTENT)} ` +
      `fora do vocabulario (${MUTABILIDADE.join(", ")})`);
  }
  if (r.TTL_SECONDS !== undefined && r.TTL_SECONDS !== null &&
      !(Number.isInteger(r.TTL_SECONDS) && r.TTL_SECONDS > 0)) {
    throw new RegraInvalida(`${sourceId}: RECOLLECTION.TTL_SECONDS tem de ser inteiro positivo`);
  }
  return {
    DETAIL_CONTENT: r.DETAIL_CONTENT,
    TTL_SECONDS: r.TTL_SECONDS ?? null,
    // ⚠️ `UNKNOWN` ESCRITO A MAO NAO E UMA CLASSIFICACAO, e por isso nao
    // conta como declarado. Alguem que escreva `DETAIL_CONTENT: "UNKNOWN"`
    // esta a dizer «ainda nao sei» — que e exactamente o estado de quem nao
    // escreveu nada. Deixar o bloco vazio comprar a admissao a Big Collection
    // seria dar ao carimbo o valor da medicao.
    DECLARADO: r.DETAIL_CONTENT !== "UNKNOWN",
  };
}

/**
 * PODE ESTA FONTE ENTRAR NUMA BIG COLLECTION?
 *
 * A pergunta nao e «sabemos ir la buscar» — isso e a capacidade, e vive no
 * coletor. Nem «esta aprovada» — isso e o portao da curadoria. E uma
 * terceira, que ate hoje ninguem fazia: **sabemos quando voltar?**
 *
 *     UMA FONTE QUE NINGUEM CLASSIFICOU ENTRA A COLHER UMA VEZ
 *     E A NAO VOLTAR NUNCA MAIS. Isso nao e uma coleta incremental:
 *     e uma fotografia unica com nome de coleta.
 *
 * Devolve `BLOCKED_FOR_BIG_COLLECTION` em vez de atirar excepcao, de
 * proposito: um bloqueio e um facto sobre a fonte, e tem de poder ser
 * contado, listado e mostrado ao dono. Uma excepcao so pararia a corrida.
 */
export function admissivelNaBigCollection(sourceId, contrato) {
  const rec = recolheitaDoContrato(sourceId, contrato);
  if (rec.DECLARADO) {
    return {
      ADMISSIVEL: true,
      COBERTURA: "DECLARADA",
      DETAIL_CONTENT: rec.DETAIL_CONTENT,
      TTL_SECONDS: rec.TTL_SECONDS,
      PORQUE: `o contrato declara DETAIL_CONTENT=${rec.DETAIL_CONTENT}`,
    };
  }
  return {
    ADMISSIVEL: false,
    COBERTURA: "BLOCKED_FOR_BIG_COLLECTION",
    DETAIL_CONTENT: "UNKNOWN",
    TTL_SECONDS: null,
    PORQUE: "RECOLLECTION nao declarado — sem isso a fonte colhe uma vez e " +
            "nunca mais e revisitada, e ninguem daria por isso",
  };
}

/**
 * O QUE O LIVRO SABE DE CADA ENDERECO — construido UMA vez, antes da corrida.
 *
 * A chave e o `SOURCE_URL`, porque e a unica coisa que se tem na mao ANTES de
 * bater a porta. Nem `DOCUMENT_ID` nem `sha256` servem aqui: os dois so
 * existem depois de o documento ter chegado, e a pergunta e se vale a pena
 * ir busca-lo.
 *
 *     SAME_URL != SAME_DOCUMENT continua a valer para a IDENTIDADE.
 *     Para a DECISAO DE IR, o endereco e o que ha.
 */
export function memoriaDosDetalhes(observacoes) {
  const mem = new Map();
  for (const o of observacoes || []) {
    const url = o && o.SOURCE_URL;
    if (!url) continue;
    const temDocumento = RESULTADOS_COM_DOCUMENTO.includes(o.OBSERVATION_RESULT);
    const antes = mem.get(url);
    const quando = o.CAPTURED_AT || null;
    // ⚠️ O LIVRO E APPEND-ONLY, E A ORDEM DELE E A CRONOLOGIA. A ultima linha
    // sobre este endereco e a que manda: uma falha de hoje nao e apagada por
    // um sucesso de ontem, e um sucesso de hoje cura a falha de ontem.
    if (antes && antes.QUANDO && quando && String(quando) < String(antes.QUANDO)) continue;
    mem.set(url, {
      URL: url,
      SOURCE_ID: o.SOURCE_ID || (antes && antes.SOURCE_ID) || null,
      ULTIMO_RESULTADO: o.OBSERVATION_RESULT || null,
      TEM_DOCUMENTO: temDocumento,
      QUANDO: quando,
      // ⚠️ VALIDADOR = ETag ou Last-Modified guardados. MEDIDO HOJE: o coletor
      // nunca os pediu, nunca os gravou, e o livro nao tem um unico. Fica o
      // campo porque a lei precisa dele, e fica a NULL porque e o que ha.
      // Um campo a NULL e honesto; um campo inventado desliga a prova.
      VALIDADOR: o.HTTP_ETAG || o.HTTP_LAST_MODIFIED || null,
      VEZES: (antes ? antes.VEZES : 0) + 1,
    });
  }
  return mem;
}

/**
 * A DECISAO, PARA UM ENDERECO DE DETALHE.
 *
 * ⚠️ REPARE NO QUE ESTA FUNCAO NAO RECEBE: bytes, sha256, corpo, resposta.
 * Nao os recebe porque nao os pode ter — se os tivesse, a rede ja tinha sido
 * gasta e a decisao chegava tarde. Esta assinatura E a lei.
 */
export function decidirSobreDetalhe(url, {
  memoria = new Map(),
  sourceId = null,
  contrato = null,
  agora = null,
  evidenciaCanonicaExige = false,
} = {}) {
  const conhecido = memoria.get(url);

  // 1 · NUNCA VISTO COM DOCUMENTO -> vai-se buscar. Inclui o endereco que ja
  //     se tentou e falhou: nao ha documento nenhum guardado dele.
  if (!conhecido || !conhecido.TEM_DOCUMENTO) {
    return {
      DECISAO: "FETCH",
      RAZAO: conhecido ? "PREVIOUS_ATTEMPT_FAILED" : null,
      PORQUE: conhecido
        ? `a ultima visita saiu ${conhecido.ULTIMO_RESULTADO} e nao guardou documento`
        : "endereco novo — o livro nunca o viu",
      CONHECIDO: Boolean(conhecido),
    };
  }

  // 2 · CONHECIDO COM DOCUMENTO. A partir daqui, ir outra vez exige RAZAO.
  const rec = recolheitaDoContrato(sourceId || conhecido.SOURCE_ID, contrato);
  const razoes = [];

  const idade = conhecido.QUANDO && agora
    ? (Date.parse(agora) - Date.parse(conhecido.QUANDO)) / 1000 : NaN;

  // ── MUTABLE COM PRAZO (T1, 2026-09-23) ────────────────────────────────────
  // ⚠️ ATE AQUI `MUTABLE` REVISITAVA TODAS AS CONHECIDAS EM TODAS AS CORRIDAS,
  // e o `TTL_SECONDS` so acrescentava uma razao a quem ja ia. Medido na T1
  // (provas/ttl_mutable_simulacao.py, datas declaradas por 52 materias das 3
  // fontes MUTABLE de noticias): ~47 revisitas por corrida, para 26 edicoes
  // espalhadas de 1 a 72 dias depois da publicacao.
  //
  // Agora: MUTABLE SEM prazo continua a revisitar sempre — e o caso dos
  // boletins reescritos na mesma morada, onde a revisita E a coleta. MUTABLE
  // COM prazo revisita quando a ultima visita passou do prazo. Nenhuma edicao
  // se perde (a materia continua a ser revisitada enquanto o indice a
  // anunciar); o preco e o atraso, e o atraso tem tecto: o prazo.
  //
  //     MUTABLE + PRAZO = «VOLTA, MAS NAO TODOS OS DIAS».
  //     MUTABLE + IDADE ILEGIVEL = VOLTA. O «NAO SEI» NAO CEGA UMA MATERIA
  //     QUE O DONO DISSE QUE MUDA.
  if (rec.DETAIL_CONTENT === "MUTABLE") {
    if (!rec.TTL_SECONDS || !Number.isFinite(idade)) razoes.push("CONTRACT_DECLARES_MUTABLE");
    else if (idade > rec.TTL_SECONDS) razoes.push("TTL_EXPIRED");
  } else if (rec.TTL_SECONDS && Number.isFinite(idade) && idade > rec.TTL_SECONDS) {
    // ⚠️ FORA DE MUTABLE, UM TTL QUE NAO DA PARA CALCULAR NAO EXPIRA. Se a
    // data nao se le, a resposta e «nao sei» — e «nao sei» nao autoriza gastar rede.
    razoes.push("TTL_EXPIRED");
  }

  // ⚠️ SO CONTA COMO RAZAO SE O VALIDADOR EXISTIR MESMO. Sem ETag nem
  // Last-Modified guardados, um pedido «condicional» e um pedido inteiro com
  // outro nome — e traz a pagina toda, com a nossa pegada dentro.
  if (conhecido.VALIDADOR) razoes.push("CONDITIONAL_REQUEST_AVAILABLE");

  if (evidenciaCanonicaExige) razoes.push("CANONICAL_EVIDENCE_REQUIRES");

  if (razoes.length === 0) {
    // ⚠️ DOIS SALTOS COM O MESMO NOME E DUAS COISAS DIFERENTES.
    // Saltar porque o dono declarou `IMMUTABLE` e uma decisao informada.
    // Saltar porque ninguem classificou a fonte e uma aposta — e ate aqui as
    // duas saiam iguais deste `return`, indistinguiveis a jusante.
    //
    // A IDA A REDE E A MESMA NOS DOIS CASOS, e isso e deliberado: mudar o
    // comportamento faria 179 fontes passarem a bater a porta sem razao. O
    // que muda e que o salto por ignorancia passa a DIZER O NOME.
    const declarado = rec.DECLARADO;
    return {
      DECISAO: "SKIP_KNOWN",
      RAZAO: null,
      COBERTURA: declarado ? "DECLARADA" : "BLOCKED_FOR_BIG_COLLECTION",
      RECOLLECTION_DECLARADA: declarado,
      DETAIL_CONTENT: rec.DETAIL_CONTENT,
      PORQUE: declarado
        ? `ja se tem este documento (${conhecido.ULTIMO_RESULTADO}` +
          (conhecido.QUANDO ? ` em ${conhecido.QUANDO}` : "") +
          `) e o contrato declara DETAIL_CONTENT=${rec.DETAIL_CONTENT}` +
          (rec.DETAIL_CONTENT === "MUTABLE"
            ? ` com prazo de ${rec.TTL_SECONDS} s; a ultima visita tem ${Math.round(idade)} s` : "")
        : `ja se tem este documento (${conhecido.ULTIMO_RESULTADO}` +
          (conhecido.QUANDO ? ` em ${conhecido.QUANDO}` : "") +
          `) e NINGUEM classificou esta fonte — salta-se por ignorancia, nao por saber`,
      AVISO: declarado ? null
        : "RECOLLECTION_UNKNOWN nao e NEVER_RECOLLECT: este salto repete-se " +
          "em todas as corridas e a fonte nunca mais e olhada. Enquanto o " +
          "contrato nao declarar, ela fica BLOCKED_FOR_BIG_COLLECTION.",
      CONHECIDO: true,
    };
  }

  return {
    DECISAO: "REVALIDATE",
    RAZAO: razoes[0],
    RAZOES: razoes,
    // O pedido condicional so e possivel se houver validador — e dizer-se
    // `true` sem ele seria prometer uma poupanca que nao acontece.
    CONDICIONAL_POSSIVEL: Boolean(conhecido.VALIDADOR),
    VALIDADOR: conhecido.VALIDADOR,
    PORQUE: `razao declarada: ${razoes.join(" + ")}`,
    CONHECIDO: true,
  };
}

/**
 * O INDICE NAO E UM DETALHE, e por isso tem regra propria: pode ser
 * revisitado sempre. E ele que anuncia o que ha de novo — saltar o indice
 * seria deixar de saber que existe materia nova, que e o oposto do objectivo.
 *
 *     REVISITAR O INDICE E BARATO E NECESSARIO.
 *     REVISITAR O DETALHE QUE JA SE TEM E SO CARO.
 */
export function decidirSobreIndice() {
  return { DECISAO: "FETCH", PORQUE: "o indice anuncia o que ha de novo; revisita-se sempre" };
}

/**
 * O CENSO DE UMA CORRIDA, nos nomes que o briefing pediu. Conta decisoes, e
 * nao adivinha: `UNNECESSARY_REFETCHES` sao as revisitas que aconteceram sem
 * razao nomeada — e com esta regra tem de dar ZERO, porque sem razao a
 * funcao acima devolve SKIP.
 */
export function censoDasDecisoes(decisoes, { indiceRequests = 0 } = {}) {
  const c = {
    INDEX_REQUESTS: indiceRequests,
    DETAIL_NEW: 0,
    DETAIL_SKIPPED_KNOWN: 0,
    // ⚠️ O NUMERO QUE ATE HOJE NAO EXISTIA. Dos saltos acima, quantos foram
    // dados sobre uma fonte que NINGUEM classificou. Nao e um erro da corrida
    // — e a medida da cegueira que ela esta a acumular calada.
    DETAIL_SKIPPED_UNDECLARED: 0,
    DETAIL_REVALIDATED: 0,
    DETAIL_REFETCHED: 0,
    UNNECESSARY_REFETCHES: 0,
    RAZOES: {},
  };
  for (const d of decisoes) {
    if (d.DECISAO === "FETCH" && !d.CONHECIDO) c.DETAIL_NEW++;
    else if (d.DECISAO === "FETCH") { c.DETAIL_REFETCHED++; if (!d.RAZAO) c.UNNECESSARY_REFETCHES++; }
    else if (d.DECISAO === "SKIP_KNOWN") {
      c.DETAIL_SKIPPED_KNOWN++;
      // `RECOLLECTION_DECLARADA` so e `false` quando a regra o disse. Um
      // `undefined` de uma decisao antiga NAO conta como cegueira: inventar
      // um numero alto a partir de campos em falta seria alarme, nao medida.
      if (d.RECOLLECTION_DECLARADA === false) c.DETAIL_SKIPPED_UNDECLARED++;
    }
    else if (d.DECISAO === "REVALIDATE") {
      c.DETAIL_REVALIDATED++;
      if (!d.RAZAO) c.UNNECESSARY_REFETCHES++;
    }
    if (d.RAZAO) c.RAZOES[d.RAZAO] = (c.RAZOES[d.RAZAO] || 0) + 1;
  }
  // Pedidos de rede que a corrida faz a detalhes: os novos, os refetch e as
  // revalidacoes. O SKIP nao bate a porta — e essa e a unica poupanca real.
  c.DETAIL_REQUESTS = c.DETAIL_NEW + c.DETAIL_REFETCHED + c.DETAIL_REVALIDATED;
  return c;
}

export const CONTRATO_INCREMENTALIDADE_VERSAO = "revisit-rule-v1";
