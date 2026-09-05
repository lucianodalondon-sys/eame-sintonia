/* SINTONIA · DO-NOT-SHOW — um detector, e uma so vez
   ---------------------------------------------------------------------------
   As catorze regras DO_NOT_SHOW vem do handoff Human Sensors escritas em
   PORTUGUES. O ecra fala ITALIANO. Um `includes()` da frase portuguesa contra
   uma pagina italiana passa quase sempre — e nao por a regra ser respeitada,
   mas por a frase nunca poder estar la.

       UM PORTAO QUE SO SABE A LINGUA EM QUE A REGRA FOI ESCRITA
       NAO GUARDA A LINGUA EM QUE O ECRA FALA.

   Por isso o detector recebe o texto NA LINGUA DA SUPERFICIE e procura a
   forma dessa lingua, declarada em DO-NOT-SHOW-QA.json.

   E HA UM CUIDADO QUE ELE NAO PODE ATROPELAR: a casa DIZ as frases proibidas
   para as NEGAR — «si dice 72 con l'espansione dichiarata, mai copertura BUONA
   in 72 celle». Proibir isso seria exigir que a tela escondesse a propria
   regra.

       A FRASE PROIBIDA, NEGADA, E A REGRA A ENSINAR-SE.
       PROIBI-LA SERIA APAGAR A LICAO PARA SALVAR O GREP.

   A PROPRIEDADE QUE ESTE FICHEIRO EXISTE PARA PRESERVAR
   -----------------------------------------------------
   A negacao tem de estar na MESMA frase. Uma janela crua de N caracteres deixa
   a proibicao ser absolvida pelo «mai» da frase ANTERIOR — provado ao injetar
   «La copertura BUONA in 72 celle» logo a seguir ao paragrafo que ja dizia
   «mai copertura BUONA in 72 celle»: a ocorrencia nova ficou coberta pela
   negacao velha.

       UMA NEGACAO NA FRASE DE CIMA NAO NEGA A AFIRMACAO DA FRASE DE BAIXO.

   Recorta-se ate a fronteira de frase mais proxima, e nunca alem da janela.

   POR QUE UM FICHEIRO SO
   ----------------------
   `casa-gate.mjs` e `lote-completo.mjs` medem superficies diferentes com a
   MESMA lei. Duas copias do detector divergem na terceira vez que alguem mexe
   numa — e a que divergir para o lado permissivo passa a dar PASS sem nunca
   ter disparado.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';

export const QA = JSON.parse(fs.readFileSync(new URL('./DO-NOT-SHOW-QA.json', import.meta.url), 'utf8'));

/** → lista de indices onde `frase` e AFIRMADA (isto e, nao negada na sua frase). */
export function ocorrenciasNaoNegadas(texto, frase, qa = QA) {
  const t = String(texto || '').toLowerCase();
  const f = String(frase).toLowerCase();
  if (!f) return [];
  const janela = qa.JANELA_DE_NEGACAO_CHARS;
  const marcas = qa.MARCADORES_DE_NEGACAO.map((m) => m.toLowerCase());
  const achados = [];
  let i = t.indexOf(f);
  while (i >= 0) {
    const cru = t.slice(Math.max(0, i - janela), i);
    const corte = Math.max(cru.lastIndexOf('.'), cru.lastIndexOf('!'), cru.lastIndexOf('?'),
                           cru.lastIndexOf('\n'), cru.lastIndexOf(';'));
    const antes = corte >= 0 ? cru.slice(corte + 1) : cru;
    if (!marcas.some((m) => antes.includes(m))) achados.push(i);
    i = t.indexOf(f, i + 1);
  }
  return achados;
}

/** As frases de um literal na lingua pedida. 'PT' devolve a original. */
export function frasesDe(L, lingua) {
  if (lingua === 'PT') return [L.PT];
  return (lingua === 'EN' ? L.EN : L.IT) || [];
}

/** As frases proibidas na lingua pedida. */
export function frasesProibidas(lingua, qa = QA) {
  const out = [];
  for (const L of qa.LITERAIS) {
    for (const f of frasesDe(L, lingua)) out.push({ frase: f, achado: L.ACHADO, lingua });
  }
  return out;
}

/** → lista de queixas. `texto` tem de estar na lingua que se declara medir. */
export function medir(texto, lingua, qa = QA) {
  const bad = [];
  for (const L of qa.LITERAIS) {
    /* Um literal sem equivalente na lingua medida nao e um literal cumprido:
       e um literal por medir, e diz-se assim. */
    const frases = frasesDe(L, lingua);
    if (!frases.length) {
      bad.push(`${L.ACHADO}: «${L.PT}» sem equivalente declarado em ${lingua}`);
      continue;
    }
    for (const frase of frases) {
      if (ocorrenciasNaoNegadas(texto, frase, qa).length) {
        bad.push(`a superficie afferma «${frase}» (${L.ACHADO})`);
      }
    }
  }
  return bad;
}

/* ── O CONTROLO NEGATIVO DO PROPRIO DETECTOR ───────────────────────────────
   Um portao que nunca reprovou e decoracao, e um detector que nunca viu uma
   afirmacao nao mede: da PASS por nao saber olhar. As tres sondas correm
   sobre texto sintetico, sem tocar na pagina, e exigem que ele:
     1. VEJA a frase afirmada;
     2. IGNORE a frase negada na mesma frase;
     3. VEJA a frase afirmada logo a seguir a uma negacao da frase anterior. */
export function controloNegativo(qa = QA) {
  const bad = [];
  const ve = (txt, f) => ocorrenciasNaoNegadas(txt, f, qa).length > 0;
  if (!ve('la casa dice 114 pessoas senza metodo', '114 pessoas'))
    bad.push('CONTROLO NEGATIVO PT FALHOU: o detector nao ve a frase afirmada');
  if (ve('si dice 90 entita, mai 114 pessoas', '114 pessoas'))
    bad.push('CONTROLO NEGATIVO PT FALHOU: o detector acusa a frase NEGADA');
  if (!ve('la copertura BUONA in 72 celle', 'copertura BUONA'))
    bad.push('CONTROLO NEGATIVO IT FALHOU: o detector nao ve a frase italiana afirmada');
  if (ve('si dice 72 dichiarate, mai copertura BUONA in 72 celle', 'copertura BUONA'))
    bad.push('CONTROLO NEGATIVO IT FALHOU: o detector acusa a frase italiana NEGADA');
  if (!ve('mai copertura BUONA in celle. La copertura BUONA e questa.', 'copertura BUONA'))
    bad.push('CONTROLO NEGATIVO IT FALHOU: a negacao da frase ANTERIOR absolveu a afirmacao seguinte');
  /* E as mesmas tres em INGLES. A superficie fala as duas linguas; um detector
     que so conhece a negacao italiana da PASS na pagina inglesa por nao saber
     olhar — que e a falha, uma lingua adiante, que este ficheiro ja descreve. */
  if (!ve('the map shows GOOD coverage in 72 cells', 'GOOD coverage'))
    bad.push('CONTROLO NEGATIVO EN FALHOU: o detector nao ve a frase inglesa afirmada');
  if (ve('we say 72 declared, never GOOD coverage in 72 cells', 'GOOD coverage'))
    bad.push('CONTROLO NEGATIVO EN FALHOU: o detector acusa a frase inglesa NEGADA');
  if (!ve('never GOOD coverage in cells. The GOOD coverage is this.', 'GOOD coverage'))
    bad.push('CONTROLO NEGATIVO EN FALHOU: a negacao da frase ANTERIOR absolveu a afirmacao seguinte');
  return bad;
}
