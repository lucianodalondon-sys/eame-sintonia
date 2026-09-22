// SINTONIA EAME — A SEGUNDA DEFESA: O QUE E RUIDO NAO E MUDANCA
//
// ⚠️ ISTO NAO E UM `normalizador-v2`. E O PRIMEIRO DESTA CASA.
// Medido em 2026-09-22 antes de escrever uma linha: `git grep` por
// normalizacao/volatil/csrf/nonce sobre todos os `.mjs` deste repositorio
// devolve auditorias do portal e ESTE ficheiro. `normalizarSias()` em
// `coleta/italy_pilot_collect.mjs` NAO e um normalizador de conteudo: e um
// PARSER de tabela de precipitacao, que transforma HTML em observacoes com
// chave — outra pergunta, outra saida. Nao ha segunda fonte de verdade aqui
// porque nao havia primeira.
//
// ⚠️ E PORQUE ISTO NAO VIVE DENTRO DE `regras/incrementalidade.mjs`.
// Aquele ficheiro declara a lei dele em letra grande: «esta regra NAO recebe
// bytes, NAO recebe sha e NAO os pode receber» — porque se os recebesse, a
// rede ja tinha sido gasta e a decisao chegava tarde. Este ficheiro come
// bytes por definicao. Meter os dois no mesmo sitio apagaria a unica coisa
// que a assinatura de `decidirSobreDetalhe()` garante.
//
//     SAO DUAS DEFESAS DISTINTAS, E NENHUMA SUBSTITUI A OUTRA:
//       1 · PRE-FETCH INCREMENTALITY  evita o pedido            (incrementalidade.mjs)
//       2 · CONTENT NORMALIZATION     evita chamar ruido mudanca (este ficheiro)
//
// A primeira poupa rede. A segunda impede a mentira no livro quando a rede
// TEM mesmo de ser gasta — numa revalidacao legitima, por exemplo.
//
//
// O QUE FOI MEDIDO, E ONDE ────────────────────────────────────────────────
// Bancada: as DUAS corridas do canario ja feitas na ops, sem tocar na rede.
//   RUN1 OPS_forward-only-live_20260922020109_0d088d  (32 detalhes)
//   RUN2 OPS_forward-only-live_20260922020511_8be761  (39 detalhes)
//   32 DOCUMENT_ID aparecem nas duas. Dos 32: 32 mudaram de RAW_SHA256,
//   e 23 desses mudaram de sha COM O MESMO NUMERO DE BYTES — assinatura de
//   token de largura fixa, nao de texto reescrito.
//
// Os trechos que diferiam, contados e nomeados um a um:
//
//   IT-T10-018  myfruit.it (October CMS)
//      179  <input name="_session_key" value="40 caracteres">
//       48  <meta property="article:modified_time" content="ISO">
//       13  <input name="_token" value="40 caracteres">
//        9  <div class="views">NNN</div>   ← O CONTADOR DE VISITAS
//
//   IT-T10-022  zootecnicainternational.com (WordPress + tagDiv Newspaper)
//      532  <aside class="... zoote-widget">  rotador de banners
//       25  uid: <hex> dentro do comentario «Speed booster» do tema
//
// ⚠️ DUAS DESSAS SEIS SAO A NOSSA PROPRIA PEGADA, E ISSO NAO E FIGURA DE
// ESTILO — e o que os numeros dizem:
//
//   `<div class="views">134</div>` -> `135`   ·   `604` -> `606`
//   `article:modified_time` = 02:01:41  e o nosso CAPTURED_AT = 02:01:42
//                           = 02:06:03  e o nosso CAPTURED_AT = 02:06:04
//
// A pagina regista a visita, a visita muda os bytes, os bytes mudam o sha, e
// o coletor conclui que o documento mudou — quando o unico que mudou fomos
// nos a olhar para ele. `article:modified_time` NAO e a data em que alguem
// editou o artigo: e a hora a que nos batemos a porta.
//
//     COMPARAR SHA DEPOIS DE VISITAR E MEDIR A PROPRIA PEGADA.
//
//
// A LEI DESTE FICHEIRO ─────────────────────────────────────────────────────
// 1 · VOCABULARIO FECHADO. Cada trecho volatil tem NOME, REGRA e ONDE FOI
//     MEDIDO. Um trecho que nao esteja nesta lista nao e volatil — e
//     conteudo. Quem quiser acrescentar um tem de o MEDIR primeiro e
//     escrever aqui onde mediu.
// 2 · SO HTML. Um PDF, um CSV ou um ZIP saem daqui INTACTOS, com
//     `NORMALIZACAO: "NOT_APPLICABLE"`. Nao sabemos tirar ruido de um PDF, e
//     fingir que sabemos seria pior do que nao o fazer.
// 3 · NUNCA APAGA TEXTO EDITORIAL. Cada regra substitui o valor volatil por
//     um marcador de largura conhecida e deixa a etiqueta de pe. O titulo, o
//     corpo, as datas do artigo e os numeros da materia passam sem tocar.
// 4 · DUAS REGUAS, E A SEGUNDA E SO TESTEMUNHA. `NORMALIZED_SHA` decide.
//     `VISIBLE_TEXT_SHA` e a regua grossa (so o texto que uma pessoa le) e
//     serve para CONFERIR a primeira, nunca para substitui-la — um
//     normalizador que engane a si proprio nao engana as duas ao mesmo tempo.

import { createHash } from "node:crypto";

const sha256 = (s) => createHash("sha256").update(s, "utf8").digest("hex");

// ── OS TRECHOS VOLATEIS, MEDIDOS UM A UM ──────────────────────────────────
// `ONDE` nao e decoracao: e o que impede a lista de crescer por palpite.
export const TRECHOS_VOLATEIS = Object.freeze([
  {
    NOME: "CONTADOR_DE_VISITAS",
    ONDE: "IT-T10-018 myfruit.it — 9 documentos, 134->135, 604->606, 6444->6448",
    PORQUE: "a pagina conta a nossa propria visita; o numero sobe porque nos fomos la",
    ONDE_DOI: "o numero muda, o sha muda, e o livro escreve DOCUMENT_CHANGED_IN_PLACE",
    // So o conteudo do contador. A etiqueta `<div class="views">` fica.
    REGRA: /(<div[^>]*class="[^"]*\bviews\b[^"]*"[^>]*>)\s*\d[\d.,\s]*(\s*<)/gi,
    TROCA: "$1<!--VOLATIL:CONTADOR-->$2",
  },
  {
    NOME: "META_MODIFIED_TIME_QUE_E_A_NOSSA_VISITA",
    ONDE: "IT-T10-018 myfruit.it — 23 documentos, 48 trechos; valor = CAPTURED_AT -1s",
    PORQUE: "o campo diz 'modificado em' e traz a hora a que NOS pedimos a pagina",
    ONDE_DOI: "metadado, nunca corpo — uma edicao a serio muda tambem o texto",
    REGRA: /(<meta[^>]*property="article:modified_time"[^>]*content=")[^"]*(")/gi,
    TROCA: "$1VOLATIL:HORA$2",
  },
  {
    NOME: "SESSION_KEY",
    ONDE: "IT-T10-018 myfruit.it — 23 documentos, 179 trechos, 40 caracteres cada",
    PORQUE: "chave de sessao do October CMS, cunhada a cada resposta",
    ONDE_DOI: "muda sempre, mesmo com a pagina literalmente igual",
    REGRA: /(<input[^>]*name="_session_key"[^>]*value=")[^"]*(")/gi,
    TROCA: "$1VOLATIL:SESSAO$2",
  },
  {
    NOME: "CSRF_TOKEN",
    ONDE: "IT-T10-018 myfruit.it — 9 documentos, 13 trechos, 40 caracteres cada",
    PORQUE: "token anti-falsificacao do formulario da newsletter, cunhado por pedido",
    ONDE_DOI: "idem — e por desenho que ele nunca se repete",
    REGRA: /(<input[^>]*name="_token"[^>]*value=")[^"]*(")/gi,
    TROCA: "$1VOLATIL:TOKEN$2",
  },
  {
    NOME: "TAGDIV_SPEED_BOOSTER_UID",
    ONDE: "IT-T10-022 zootecnicainternational.com — 9 documentos, 25 trechos",
    PORQUE: "identificador por pedido do tema Newspaper, num comentario HTML",
    ONDE_DOI: "6ab1e1ae8537b -> 6ab1e2b74bd..; e um relogio em hexadecimal",
    REGRA: /(\buid:\s*)[0-9a-f]{8,}/gi,
    TROCA: "$1VOLATIL:UID",
  },
  {
    NOME: "ROTADOR_DE_ANUNCIO_ZOOTE",
    ONDE: "IT-T10-022 — 9 documentos, 532 trechos; 11 banners por pagina, 1 bloco",
    PORQUE: "o bloco sorteia anunciantes a cada visita (sperotto -> codaf -> ...)",
    // ⚠️ ESTE E O UNICO QUE APAGA UM BLOCO INTEIRO, E POR ISSO E O MAIS
    // PERIGOSO DA LISTA. Confere-se por medicao: e um `<aside>` de barra
    // lateral, ha exactamente UM por pagina, nao tem `<aside>` dentro, e
    // nao contem uma unica palavra do artigo — so `<a>` e `<img>` de
    // publicidade. Se um dia tiver, esta regra tem de cair.
    ONDE_DOI: "o anunciante muda, os bytes mudam, e o artigo e o mesmo",
    REGRA: /<aside[^>]*\bzoote-widget\b[^>]*>[\s\S]*?<\/aside>/gi,
    TROCA: "<!--VOLATIL:ANUNCIO-->",
  },
  {
    NOME: "ZOOTE_TRACKING_ORDEM_DOS_ANUNCIOS",
    ONDE: "IT-T10-022 — os 9 documentos que sobravam depois das regras acima",
    PORQUE: "o mesmo rotador publica em JavaScript a lista de anuncios sorteados",
    // ⚠️ E POR ISSO QUE ESTE ENTROU, E NAO POR SOBRAR. Medido documento a
    // documento nos 9: e exactamente O MESMO CONJUNTO de 11 identificadores,
    // por outra ordem — nenhum anuncio entra, nenhum sai.
    //
    //   RUN1  15851,15321,13882,15995,15441,15000,15859,16233,17136,680,5840
    //   RUN2  17136,15441,15000,15995,15851,13882,15321,15859,16233,680,5840
    //   conjunto ordenado identico: 9 de 9
    //
    // Alargar uma regra ate o vermelho desaparecer e como apagar o
    // termometro. Este trecho entra porque SE MEDIU que e uma baralhada do
    // mesmo baralho, e nao porque estava a incomodar.
    ONDE_DOI: "a ordem muda a cada pedido, e o sha do artigo vai atras",
    REGRA: /(<script[^>]*\bid="zoote-tracking"[^>]*>)[\s\S]*?(<\/script>)/gi,
    TROCA: "$1/*VOLATIL:ANUNCIOS*/$2",
  },
  {
    NOME: "IUBENDA_CRONOMETRO",
    ONDE: "IT-T10-022 — 9 documentos, o ultimo trecho que sobrava depois de tudo",
    PORQUE: "comentario HTML onde o plugin de cookies diz quanto tempo ELE demorou",
    // `<!-- Parsed with iubenda default class in 0.0276 sec. -->` — 0.00315
    // numa visita, 0.00291 na outra. E um cronometro da maquina do servidor,
    // nao uma frase sobre o documento; e o unico numero de todo o ficheiro
    // que mede o servidor a trabalhar.
    ONDE_DOI: "0.00315 -> 0.00291; quatro digitos chegam para mudar o sha",
    REGRA: /(<!--\s*Parsed with iubenda[^>]*?in\s*)[\d.]+(\s*sec)/gi,
    TROCA: "$1VOLATIL:CRONOMETRO$2",
  },
]);

export class NormalizacaoInvalida extends Error {}

// ── E ISTO E HTML? ────────────────────────────────────────────────────────
// A mesma pergunta que `assinatura()` do coletor faz, e de proposito: uma
// segunda opiniao sobre a especie dos bytes seria uma segunda verdade.
export function pareceHtml(buf) {
  const cabeca = Buffer.isBuffer(buf) ? buf.subarray(0, 8).toString("latin1") : String(buf).slice(0, 8);
  if (cabeca.startsWith("%PDF") || cabeca.startsWith("PK")) return false;
  const inicio = (Buffer.isBuffer(buf) ? buf.subarray(0, 400).toString("latin1") : String(buf).slice(0, 400)).trimStart();
  return inicio.startsWith("<");
}

// ── A REGUA GROSSA: O QUE UMA PESSOA LE ───────────────────────────────────
// Script, estilo, comentario e etiqueta saem; fica o texto. Nao substitui a
// regua fina — um token dentro de um `value=` nunca foi texto visivel, por
// isso esta regua sozinha diria «nada mudou» tambem quando algo mudou no
// `alt` de uma imagem. Ela CONFERE, nao decide.
export function textoVisivel(buf) {
  const s = Buffer.isBuffer(buf) ? buf.toString("latin1") : String(buf);
  return s
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * NORMALIZA UM DOCUMENTO. Nao decide nada — so descreve.
 *
 * Devolve sempre `RAW_SHA256`, e devolve `NORMALIZED_SHA` IGUAL ao raw
 * quando nao ha normalizacao possivel. Um ficheiro nao-HTML sai daqui com
 * `NORMALIZACAO: "NOT_APPLICABLE"` — que e diferente de «normalizei e nao
 * encontrei nada»: a pergunta e que nao se aplica.
 */
export function normalizarConteudo(buf) {
  const bytes = Buffer.isBuffer(buf) ? buf : Buffer.from(String(buf), "latin1");
  const RAW_SHA256 = createHash("sha256").update(bytes).digest("hex");

  if (!pareceHtml(bytes)) {
    return {
      NORMALIZACAO: "NOT_APPLICABLE",
      PORQUE: "os bytes nao sao HTML — esta casa nao sabe tirar ruido de PDF/ZIP/CSV",
      RAW_SHA256,
      NORMALIZED_SHA: RAW_SHA256,
      VISIBLE_TEXT_SHA: null,
      VOLATEIS: {},
      VOLATEIS_TOTAL: 0,
    };
  }

  let texto = bytes.toString("latin1");
  const VOLATEIS = {};
  let total = 0;
  for (const t of TRECHOS_VOLATEIS) {
    let n = 0;
    // `RegExp` com `g` guarda `lastIndex`; recria-se por uso para que duas
    // chamadas seguidas nunca deem respostas diferentes sobre o mesmo texto.
    const re = new RegExp(t.REGRA.source, t.REGRA.flags);
    texto = texto.replace(re, (...args) => {
      n++;
      // `TROCA` usa `$1`/`$2`; deixa-se o `replace` do JS resolve-los.
      return String(t.TROCA).replace(/\$(\d)/g, (_, i) => args[Number(i)] ?? "");
    });
    if (n > 0) { VOLATEIS[t.NOME] = n; total += n; }
  }

  return {
    NORMALIZACAO: "APPLIED",
    RAW_SHA256,
    NORMALIZED_SHA: sha256(texto),
    VISIBLE_TEXT_SHA: sha256(textoVisivel(texto)),
    VOLATEIS,
    VOLATEIS_TOTAL: total,
  };
}

/**
 * COMPARA DUAS VISITAS AO MESMO ENDERECO, e diz se houve mudanca MATERIAL.
 *
 * ⚠️ O VEREDICTO SAI DE `NORMALIZED_SHA`, E SO DELE.
 * `VISIBLE_TEXT_CHANGED` vai no recibo porque e a testemunha independente:
 * se um dia o normalizador disser «nada mudou» e o texto visivel disser que
 * mudou, ha um bug AQUI — e o campo `AVISO` di-lo em voz alta em vez de
 * deixar a contradicao calada.
 *
 * Nao-HTML: `NORMALIZED_SHA == RAW_SHA256`, portanto bytes diferentes dao
 * `MATERIAL_CHANGE`. E o comportamento de sempre, e e o certo: sem saber
 * separar ruido, tudo e sinal.
 */
export function compararConteudo(bufAntes, bufDepois) {
  const a = normalizarConteudo(bufAntes);
  const b = normalizarConteudo(bufDepois);

  const RAW_CHANGED = a.RAW_SHA256 !== b.RAW_SHA256;
  const NORMALIZED_CHANGED = a.NORMALIZED_SHA !== b.NORMALIZED_SHA;
  const VISIBLE_TEXT_CHANGED =
    a.VISIBLE_TEXT_SHA === null || b.VISIBLE_TEXT_SHA === null
      ? null
      : a.VISIBLE_TEXT_SHA !== b.VISIBLE_TEXT_SHA;

  // Ruido volatil = os bytes mexeram-se e o conteudo normalizado nao.
  const VOLATILE_DIFFERENCE = RAW_CHANGED && !NORMALIZED_CHANGED;

  const VEREDICTO = !RAW_CHANGED
    ? "IDENTICAL_BYTES"
    : NORMALIZED_CHANGED
      ? "MATERIAL_CHANGE"
      : "VOLATILE_ONLY";

  const quais = new Set([...Object.keys(a.VOLATEIS), ...Object.keys(b.VOLATEIS)]);

  return {
    VEREDICTO,
    RAW_CHANGED,
    NORMALIZED_CHANGED,
    VISIBLE_TEXT_CHANGED,
    VOLATILE_DIFFERENCE,
    NORMALIZACAO: a.NORMALIZACAO === "APPLIED" && b.NORMALIZACAO === "APPLIED" ? "APPLIED" : "NOT_APPLICABLE",
    OLD_RAW_SHA: a.RAW_SHA256,
    NEW_RAW_SHA: b.RAW_SHA256,
    OLD_NORMALIZED_HASH: a.NORMALIZED_SHA,
    NEW_NORMALIZED_HASH: b.NORMALIZED_SHA,
    TRECHOS_VOLATEIS_ENCONTRADOS: [...quais],
    // ⚠️ A CONTRADICAO NAO FICA CALADA. Se o texto que uma pessoa le mudou e
    // o normalizado nao, foi o normalizador que apagou conteudo — que e
    // exactamente o defeito M4 do red team.
    AVISO: (!NORMALIZED_CHANGED && VISIBLE_TEXT_CHANGED === true)
      ? "NORMALIZADOR_SUSPEITO: o texto visivel mudou e o normalizado nao — isto e um defeito aqui, nao um documento igual"
      : null,
  };
}

export const CONTRATO_NORMALIZACAO_VERSAO = "content-normalization-v1";
