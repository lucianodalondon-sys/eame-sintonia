// SINTONIA — LABEL INTELLIGENCE V1 · casco
// O casco NAO interpreta documento. Ele mostra intelligence objects e produtos
// que a inteligencia ja resolveu, e leva qualquer afirmacao de volta a prova.
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

// O payload tem de existir antes de qualquer constante derivada dele. Estava
// declarado 130 linhas abaixo das constantes de relogio que o leem: no
// navegador isso e "Cannot access 'P' before initialization" e a ferramenta
// inteira abria em branco. O teste de render nao pegou porque injetava P por
// fora; agora ele carrega window.__PAYLOAD__ como o navegador carrega.
const P = window.__PAYLOAD__;

// Tokens que significam AUSENCIA DE CONHECIMENTO. Nunca vira "-", "0" ou "N/A".
const UNK = ['NOT_KNOWN','NOT_PROVED','NOT_PRESERVED','NOT_PRESENT','UNKNOWN',
             'NOT_APPLICABLE','NOT_ATTEMPTED','NOT_EMITTED_BY_THIS_TOOL','NOT_CHECKED',
             'NOT_COLLECTED','NOT_VALIDATED','NOT_LOCATED','NOT_PARSED','NOT_IN_SNAPSHOT',
             'NOT_COMPUTED_WITHOUT_CLOCK','NOT_RECONSTRUCTABLE','NOT_PROVED_BY_RULE',
             'NOT_IMPLEMENTED'];
// A lista era uma enumeracao, e por isso ficou para tras: quando a coleta
// passou a emitir NOT_COLLECTED, val() caiu no ramo de valor comum e a ficha
// publicou o token dentro do atributo de um link — um link vivo para uma
// ausencia. Agora QUALQUER string NOT_* conta como ignorancia, e um portao
// varre o payload atras de NOT_* que a lista nao nomeia, para que a lista
// continue sendo documentacao e nao definicao.
//
// UMA excecao, e ela importa: NOT_RELEVANT nao e ignorancia. E uma DECISAO —
// a regra C-05 olhou o objeto e resolveu que ele nao passa para aquela area.
// Tratar decisao como ausencia apagaria a diferenca entre "o portao barrou" e
// "nao sabemos", que e justamente a distincao que esta ferramenta existe para
// manter. O proprio portao IGNORANCE_TOKENS_DECLARED achou este caso.
const DECISOES = ['NOT_RELEVANT'];
const isUnk = v => { const t = String(v);
  return !DECISOES.includes(t) && (UNK.includes(t) || /^NOT_[A-Z_]+$/.test(t)); };
// Link so nasce de um endereco de verdade. Antes a guarda era "nao esta na
// lista UNK", que confiava numa lista incompleta.
const ehURL = v => /^https?:\/\//.test(String(v || ''));
const link = (u, rotulo) => ehURL(u)
  ? `<a href="${esc(u)}" target="_blank">${esc(rotulo)}</a>`
  : val(u);
// Renderiza valor preservando o token de ignorancia, com o nome dele visivel.
const val = v => isUnk(v) ? `<span class="unknown" title="a fonte nao sustenta este campo">${esc(v)}</span>`
                          : esc(v);

// ---------------------------------------------------------------- RELOGIO
// Este arquivo e distribuido sozinho. Todo numero de dias vinha congelado do
// momento do build: aberto no ano que vem a pagina continuaria afirmando
// "vence em 6 dias" e "hoje 2026-09-06" no presente. Numero de dia agora e
// recalculado contra o relogio de quem abre, e a pagina diz as TRES datas que
// nao sao a mesma: a do dado, a do build, e a de hoje.
// SF-09 · A DATA CIVIL DE QUEM ABRE, NAO O INSTANTE UTC.
// `toISOString()` devolve a data em UTC. Reproduzido com o navegador em
// Europe/Rome e o relogio em 2026-09-01T00:30 local: a pagina imprimia
// "hoje: 2026-08-31", o CALENDARIO caia de 15 para 8 no bloco de validade
// vencida, e sete registros que venceram em 31/08 apareciam como "vencem em
// ate 30 dias". Meia-noite em Roma nao e meia-noite em Londres, e a ferramenta
// que existe para nao confundir CAPTURED_AT com EFFECTIVE_AT nao pode confundir
// o proprio dia. `dias()` tinha o mesmo defeito pelo outro lado: Date.parse de
// "YYYY-MM-DD" e tratado como UTC, entao comparar duas datas civis por instante
// erra em qualquer fuso a leste ou a oeste de Greenwich.
const iso = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
// hojeISO() E UMA PERGUNTA, NAO UMA CONSTANTE.
// Era `const hojeISO() = ...`, avaliado UMA VEZ quando a pagina carrega. Uma pagina
// aberta e deixada aberta atravessa a meia-noite com a data de ontem, e todo
// numero que se diz "de hoje" envelhece junto sem avisar. Agora cada leitura
// pergunta ao relogio de novo — que e o que a palavra "hoje" promete.
function hojeISO() { try { return iso(new Date()); } catch (e) { return null; } }
const DIA = 86400000;
// data civil ISO -> instante UTC do meio-dia. Meio-dia, e nao meia-noite, para
// que nenhum horario de verao de 1 h possa empurrar a diferenca para o dia
// vizinho.
const civil = s => Date.parse(String(s) + 'T12:00:00Z');
function dias(ate) {                     // dias de hojeISO() ate a data ISO 'ate'
  if (!hojeISO() || !/^\d{4}-\d{2}-\d{2}$/.test(String(ate))) return null;
  return Math.round((civil(ate) - civil(hojeISO())) / DIA);
}
const dISO = s => /^\d{8}$/.test(String(s)) ? `${String(s).slice(0,4)}-${String(s).slice(4,6)}-${String(s).slice(6,8)}` : String(s);
// dte do produto, recalculado. Cai para o valor do build so se nao houver relogio.
function dte(p) {
  const d = dias(p.expiry);
  return d === null ? (typeof p.dte === 'number' ? p.dte : null) : d;
}
const DATA_DATE = dISO(P.DATA_DATE);
const ULTIMA_MUDANCA = dISO(P.NEWEST_CHANGE_AT);
// idade do dado, tambem viva: ela e uma contagem ATE hoje e envelhece com a
// pagina aberta, exatamente como hojeISO().
function idadeDoDado() { return dias(DATA_DATE); }   // negativo = o dado tem essa idade

// S1 · REGRAS.md secao 5 obriga uma glosa em cima de ACT_NOW, dizendo que ele
// significa "olhe hoje" e nunca uma ordem comercial. Ela nao aparecia em
// nenhuma das nove telas: a unica frase imperativa em ingles do produto
// viajava sem o seu proprio contrato. O texto literal esta em GLOSA_JANELA
// logo abaixo, e o portao EXPIRY_AS_WITHDRAWAL recorta exatamente esse texto
// e mais nada.
const GLOSA_JANELA = `<div class="lei"><b><code>ACT_NOW</code> aqui significa
  &ldquo;olhe hoje&rdquo;, nunca &ldquo;pare de vender&rdquo;.</b> A janela e sobre
  <b>quando olhar</b>, nunca sobre o que fazer com o produto no mercado. Nenhuma janela desta
  ferramenta autoriza decisao comercial: <code>EXPIRY != WITHDRAWAL</code>, e
  <code>ACTION</code> nao e emitida por esta ferramenta em nenhuma hipotese.</div>`;
// A JANELA TAMBEM E UM NUMERO DE DIAS, e tambem estava congelada no build.
// dte() ja era recalculado no navegador; TIME_WINDOW nao, e a incoerencia
// aparecia junta na mesma tela: aberta em 2027, a ferramenta mostrava
// PLAN NEXT CYCLE ao lado de uma validade que ela propria marcava como vencida.
// Reimplementa T-01..T-08 do REGRAS.md contra o relogio de quem abre.
function janelaAgora(o) {
  if (o.OBJECT_TYPE === 'NEEDS_HUMAN_REVIEW' || o.OBJECT_TYPE === 'DATA_QUALITY_EVENT')
    return ['UNKNOWN', 'T-07'];
  if (o.OBJECT_TYPE === 'REVOCATION_ACT_CHANGE') return ['ACT_NOW', 'T-08'];
  if (o.OBJECT_TYPE === 'STATUS_CHANGE' &&
      FORA_DE_VIGOR.includes(String(o.AFTER_VALUE || '').trim().toLowerCase()))
    return ['ACT_NOW', 'T-09'];
  const p = byReg[o.REGISTRATION_ID];
  const d = p ? dte(p) : null;
  if (d === null || typeof d !== 'number') return [o.TIME_WINDOW, o.TIME_WINDOW_RULE];
  if (o.OBJECT_TYPE === 'EXPIRY_EVENT') return ['ACT_NOW', 'T-01'];
  if (d < 0) return ['ACT_NOW', 'T-01'];
  if (d <= 90) return ['PREPARE', 'T-02'];
  if (d <= 180) return ['MONITOR', 'T-03'];
  return ['PLAN_NEXT_CYCLE', 'T-04'];
}
// Marca quando a janela de hoje difere da que foi gravada no build.
function janelaSelo(o) {
  const [j, r] = hojeISO() ? janelaAgora(o) : [o.TIME_WINDOW, o.TIME_WINDOW_RULE];
  const mudou = j !== o.TIME_WINDOW;
  const [, cls, lbl] = WIN[j] || ['', 'p-dim', j];
  return `<span class="pill ${cls}" title="${esc(r)}${mudou?` — recalculada hoje; no build era ${esc(o.TIME_WINDOW)} (${esc(o.TIME_WINDOW_RULE)})`:''}">${esc(lbl||j)}</span>${
    mudou ? `<div class="meta">recalculada contra hoje. No build era <code>${esc(o.TIME_WINDOW)}</code></div>` : ''}`;
}

const WIN = {ACT_NOW:['act','p-act','ACT NOW'], PREPARE:['prep','p-warn','PREPARE'],
             MONITOR:['mon','p-ok','MONITOR'], PLAN_NEXT_CYCLE:['mon','p-dim','PLAN NEXT CYCLE'],
             NO_ACTION_YET:['','p-dim','NO ACTION YET'], UNKNOWN:['unk','p-unk','UNKNOWN']};
const PROOF = {PROVED:'p-ok', NOT_PROVED:'p-unk', NEEDS_REVIEW:'p-rev'};
// Aviso de idade, repetido em toda tela que imprime contagem de dias.
function avisoRelogio() {
  if (!hojeISO()) return `<div class="lei"><b>Sem relogio.</b> Este navegador nao devolveu a data de
    hoje: as contagens de dias abaixo sao as do momento do build
    (<code>${esc(P.BUILT_AT)}</code>) e <b>nao</b> foram atualizadas.</div>`;
  const idade = idadeDoDado() === null ? null : -idadeDoDado();
  return `<div class="lei"><b>Tres datas, e elas nao sao a mesma.</b>
    Dado: instantaneo oficial <code>${esc(P.DATA_SNAPSHOT_ID)}</code> de <b>${esc(DATA_DATE)}</b>
    &middot; mudanca provada mais recente dentro dele: <b>${esc(ULTIMA_MUDANCA)}</b>
    &middot; ferramenta montada em <code>${esc(P.BUILT_AT)}</code>
    &middot; hoje, neste navegador: <b>${esc(hojeISO())}</b>.
    ${idade !== null && idade > 0 ? `O dado tem <b>${idade} dia(s)</b>. ` : ''}
    As contagens de dias desta tela sao recalculadas contra hoje; <b>o conteudo nao</b> —
    nada foi coletado depois de ${esc(DATA_DATE)}. <span class="unknown">O que mudou desde
    ${esc(DATA_DATE)} nao e NOT_KNOWN por opiniao: nao foi coletado.</span></div>`;
}
const CAPS = {REGULATORY:'Regulatory', DEVELOPMENT_MARKET:'Desenv. de Mercado',
              COMMERCIAL_RTV:'Comercial / RTV', MARKETING_PRODUCT:'Marketing / Produto',
              SUPPLY:'Supply', INTELLIGENCE:'Inteligencia',
              COUNTRY_PRODUCT_TEAM:'Country / Product Team'};

// Os dois lados escrevem o nome da cultura de jeitos diferentes: o leitor de
// cultura x alvo normaliza ("VITE"), o leitor de dose guarda como esta impresso
// ("Vite*", "Cetriolo, Zucchino (Uso in serra)"). Casar por igualdade exata fazia
// a tela dizer NOT_KNOWN para dose que existe e esta provada.
const nrm = s => String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'')
  .toUpperCase().replace(/[^A-Z0-9 ]+/g,' ').replace(/\s+/g,' ').trim();
// Casamento por TOKEN INTEIRO. A primeira versao casava por conteudo de
// substring e produziu um erro grave: nrm('Melo, pero') contem o token MELO, e
// 'MELONE'.includes('MELO') e verdadeiro — entao a dose de macieira e pereira
// aparecia como dose autorizada de MELAO. Substring nao e identidade botanica.
function tokens(s) {
  return new Set(nrm(s).split(/[ ,;/()]+/).filter(t => t.length > 2));
}
// Direcional: todo token do par de uso tem de estar na celula de dose. A celula
// de dose e uma lista impressa no rotulo ("Melo, pero"); o par de uso e um nome
// so ("MELO"). Interseccao simples casava nos dois sentidos e casava demais.
function contido(peq, grande) {
  const a = tokens(peq), b = tokens(grande);
  if (!a.size || !b.size) return false;
  for (const t of a) if (!b.has(t)) return false;
  return true;
}
// A CELULA DE CULTURA E UMA LISTA, E LISTA SE LE ITEM A ITEM.
//
// contido() casa por TOKEN, e por token {BARBABIETOLA} esta contido em
// "Foraggere (prati-pascoli, loglio, mais, barbabietola da foraggio, erba
// medica)". Medido na tela: BARBABIETOLA x APION saia 420-1200 g/ha com selo
// LISTADA em 5 registros, enquanto no MESMO produto e sob o MESMO nome os pares
// ALTICA/AFIDI/CLEONO vinham de "Barbabietola da zucchero" — e o maximo
// autorizado para a beterraba DE ACUCAR naquela tabela e 800 g/ha.
//
// A lei certa ja estava escrita nesta casa, em v1/inteligencia/teto_dose.py:
// "Casamento por FRASE INTEIRA: 'mais dolce' nao e 'mais', e 'mais da foraggio'
// tampouco". Ela valia para o TETO (R-12) e nao valia para a JUNCAO, que e onde
// o numero e publicado. Agora vale nos dois.
const itensDaCelula = s => String(s || '').split(/[,;]|\se\s/i)
  .map(x => nrm(x)).filter(Boolean);
// item INTEIRO: "BARBABIETOLA" nao e "BARBABIETOLA DA FORAGGIO"
const culturaNaCelula = (nome, celula) => {
  const n = nrm(nome);
  return itensDaCelula(celula).some(it => it === n);
};
// E onde o vocabulario a montante NAO distingue, a ferramenta nao escolhe.
// Se a mesma etichetta escreve mais de uma forma qualificada do mesmo nome
// curto — "Mais", "Mais dolce", "Mais da foraggio"; "Barbabietola da zucchero"
// e "barbabietola da foraggio"; "cavolo broccolo" e "Cavolo cappuccio" — entao
// o nome curto nao identifica uma cultura neste documento, e nenhuma dose pode
// ser atribuida a ele por juncao de lista.
function formasDaCultura(p, nome) {
  const n = nrm(nome), formas = new Set();
  (p.doses || []).forEach(d => itensDaCelula(d.crop).forEach(it => {
    if (it === n || it.startsWith(n + ' ')) formas.add(it);
  }));
  return [...formas];
}
// A JUNCAO DA DOSE, com estado declarado.
//
// Medido sobre os 2.926 pares publicados: igualdade exata de cultura E alvo
// casa 5 pares. Os vocabularios sao estruturalmente diferentes — o leitor de
// uso normaliza para um nome ("MELO"), o de dose guarda a celula impressa
// ("Melo, pero"). Entao a juncao por lista existe, mas E INFERENCIA e tem de
// dizer que e.
//
// E, sobretudo: em 106 pares ha DUAS OU MAIS linhas de dose que servem, com
// valores diferentes (LAMDEX EXTRA em BARBABIETOLA x AFIDI da 280-600 g/ha
// e 420-1200 g/ha). A versao anterior mostrava a primeira, calada, com selo
// verde. Numero unico onde a fonte tem dois nao e resposta: e chute exibido
// como leitura.
// Uma linha de dose so pode ser candidata se ela for uma linha DESTA cultura e
// se o valor dela tiver sido conferido contra o documento. Duas exclusoes, as
// duas medidas contra a fonte primaria:
//
//   R-11 · a cultura da linha tem de sobreviver aos fios desenhados. Sem isso
//   a ferramenta publicava "TABACCO x CIMICI = 600 g/ha" com o selo mais forte
//   que ela tem: na etichetta 008259 a linha "Cimici 600" esta dentro da celula
//   de PORRO, e ha um fio desenhado entre ela e Tabacco.
//
//   NOT_LOCATED · o validador nao conseguiu localizar o valor no documento para
//   conferir. Isso e "nao verifiquei", nao "verifiquei e esta certo", e nao pode
//   sair como numero.
// SF-05 · PLAUSIBILITY_REJECTED faltava nesta lista, e a consequencia era
// visivel: em 012878 FOLPAN GOLD e 015317 SESTO GOLD a linha sai com
// CULTURA = FRAGMENTO_DE_LEITURA, ALVO = FRAGMENTO_DE_LEITURA e
// FIOS = PLAUSIBILITY_REJECTED — e a coluna DOSE/HA imprimia "2 kg/ha" assim
// mesmo. O filtro de plausibilidade existe para dizer que aquela tabela nao
// era uma tabela; publicar o numero dela e desdizer o proprio filtro.
function linhaUsavel(d) {
  return d.crop_check !== 'CROP_ASSIGNMENT_CONTRADICTED_BY_RULE'
      && d.rule_check !== 'NOT_LOCATED'
      && d.rule_check !== 'CONTRADICTED_BY_RULE'
      && d.rule_check !== 'PLAUSIBILITY_REJECTED';
}
// A rebaixa foi tentada como fato do PAR (registro, cultura, alvo) e MEDIDA:
// isso apagava fato verdadeiro. Em 008259 existem duas linhas rotuladas
// "Tabacco x Nottue defogliatrici": a de y=197,2, que na verdade e de PORRO e
// cai por R-11, e a de y=229,4, que e mesmo de Tabacco e vale 400-500 g/ha.
// Suprimir o par inteiro perderia a segunda. A rebaixa continua sendo da LINHA;
// o que MF-03 pedia — que a fila de revisao nao anuncie uma recusa enquanto a
// ficha publica o mesmo valor — ja e garantido por linhaUsavel(), que barra
// NOT_LOCATED e CONTRADICTED_BY_RULE na origem. Quantas linhas cairam aparece
// em cada celula.
const linhaPublicavel = (p, d) => linhaUsavel(d);
function juntaDose(p, u) {
  const todas = p.doses;
  const boas = todas.filter(d => linhaPublicavel(p, d));
  const descartadas = todas.length - boas.length;
  const ex = boas.filter(x => nrm(x.crop) === nrm(u.crop) && nrm(x.target) === nrm(u.target));
  const base = {descartadas, teto: teto(p, u)};
  if (ex.length === 1) {
    // EXACT_MATCH e o selo mais forte, entao paga o pedagio mais alto: a
    // citacao gravada pelo extrator tem de conter o nome da cultura. Os 5
    // unicos EXACT_MATCH da versao anterior reprovavam neste teste — a citacao
    // deles era "Cimici 600 1 Nottue defogliatrici (allo scoperto)", sem a
    // palavra Tabacco em lugar nenhum.
    const cita = nrm(ex[0].quote || '');
    const nomeNaCitacao = [...tokens(u.crop)].some(t => cita.includes(t));
    return {...base, estado: nomeNaCitacao ? 'EXACT_MATCH' : 'EXACT_MATCH_QUOTE_LACKS_CROP',
            d: nomeNaCitacao ? ex[0] : null, cand: ex};
  }
  let cand = ex;
  if (!cand.length) {
    const formas = formasDaCultura(p, u.crop);
    if (formas.length > 1)
      return {...base, estado: 'CROP_IDENTITY_NOT_PROVED', d: null, cand: [], formas};
    cand = boas.filter(x => culturaNaCelula(u.crop, x.crop) && contido(u.target, x.target));
  }
  if (!cand.length) {
    // NAO HA LINHA e HAVIA LINHA E ELA CAIU sao duas respostas diferentes.
    // A versao anterior dizia "leitura que nao ligou" tambem quando a
    // ferramenta tinha PROVADO que a linha era de outra cultura.
    const caidas = todas.filter(x => !linhaPublicavel(p, x)
      && (nrm(x.crop) === nrm(u.crop) || culturaNaCelula(u.crop, x.crop))
      && contido(u.target, x.target));
    if (caidas.length) {
      // O TOKEN TEM DE DIZER QUAL REGRA DERRUBOU A LINHA, e nao supor uma.
      //
      // O nome anterior era DOSE_ROW_CONTRADICTED_BY_R11_FOR_THIS_PAIR e valia
      // para QUALQUER linha caida — inclusive as que cairam por NOT_LOCATED,
      // que e falha do localizador e nunca chegou a comparar cultura nenhuma,
      // e agora tambem para as que caem por R-22. Afirmar "R-11 contradisse"
      // sobre uma linha que R-11 aprovou e a mesma classe de mentira que a
      // ferramenta existe para nao cometer.
      const causa = caidas.some(x => x.crop_check === 'CROP_ASSIGNMENT_CONTRADICTED_BY_RULE')
          ? 'DOSE_ROW_CONTRADICTED_BY_R11_FOR_THIS_PAIR'
        : caidas.some(x => x.band_check === 'DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE')
          ? 'DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE_FOR_THIS_PAIR'
        : caidas.some(x => x.rule_check === 'PLAUSIBILITY_REJECTED')
          ? 'DOSE_ROW_REJECTED_BY_PLAUSIBILITY_FOR_THIS_PAIR'
        : 'DOSE_ROW_NOT_LOCATED_FOR_THIS_PAIR';
      return {...base, estado: causa, d: null, cand: [], caidas};
    }
    return {...base, estado: 'NO_DOSE_ROW_FOR_THIS_PAIR', d: null, cand: []};
  }
  // Uma candidata SEM valor lido nao discorda de nada: ela nao diz nada. A
  // versao anterior contava NOT_PRESENT como um valor e declarava "as duas nao
  // dizem o mesmo valor" sobre um par em que a etichetta e inequivoca — 16 dos
  // 106 ambiguos eram este caso, e a segunda candidata era uma duplicata do
  // proprio parser.
  const comValor = cand.filter(x => !isUnk(x.dose_ha) && String(x.dose_ha || '').trim());
  const mudos = cand.length - comValor.length;
  if (!comValor.length)
    return {...base, estado: 'DOSE_ROW_WITHOUT_READ_VALUE', d: null, cand, mudos};
  const vals = new Set(comValor.map(x => `${x.dose_ha}|${x.unit_ha}`));
  if (vals.size > 1)
    return {...base, estado: 'AMBIGUOUS_DOSE_FOR_THIS_PAIR', d: null, cand: comValor, mudos};
  // R-13 · se NENHUMA candidata tem o texto do alvo confirmado literalmente no
  // documento, a tela nao responde com o numero. Existe fusao de linha provada
  // (008259) e nao ha detector: um numero cuja linha de origem nao pode ser
  // confirmada nao e uma resposta. O numero continua a um clique, com a sua
  // proveniencia — nao e apagado, e deixa de ser a resposta.
  if (comValor.every(x => x.target_literal === 'TARGET_TEXT_NOT_FOUND_LITERALLY'))
    return {...base, estado: 'DOSE_NOT_PROVED_TARGET_NOT_LITERAL',
            d: null, cand: comValor, mudos, escondida: comValor[0]};
  return {...base,
          estado: mudos ? 'LISTED_IN_DOSE_ROW_WITH_UNREAD_DUPLICATE'
                        : (comValor.length > 1 ? 'LISTED_IN_DOSE_ROW_AGREEING' : 'LISTED_IN_DOSE_ROW'),
          d: comValor[0], cand: comValor, mudos};
}

// R-12 · o teto por cultura que a etichetta escreve FORA da tabela. Casamento
// por FRASE INTEIRA: "mais dolce" nao e "mais".
function teto(p, u) {
  const c = nrm(u.crop);
  for (const t of (p.ceilings || []))
    if ((t.CULTURAS || []).some(x => nrm(x) === c)) return t;
  return null;
}
const topoDaDose = v => {
  const ns = String(v || '').match(/\d+[.,]?\d*/g);
  return ns ? Math.max(...ns.map(n => parseFloat(n.replace(',', '.')))) : null;
};
function excedeTeto(d, t) {
  if (!d || !t) return false;
  const hi = topoDaDose(d.dose_ha);
  if (hi === null) return false;
  const u = String(d.unit_ha || '').toLowerCase();
  const g = (u.startsWith('kg') || u.startsWith('l')) ? hi * 1000 : hi;
  return g > t.G_HA + 0.01;
}

// A validade tem de aparecer igual em TODA tela. Antes, CULTURA x ALVO mostrava
// "2026-08-15" seco enquanto CALENDARIO e PRODUTO 360 marcavam o mesmo produto
// como vencido-e-ainda-ativo. Mesma data, tres leituras diferentes.
function validade(p) {
  if (isUnk(p.expiry)) return val(p.expiry);
  const D = dte(p);
  if (typeof D === 'number' && D < 0)
    return foraDeVigor(p)
      ? `<span style="color:var(--dim)">${esc(p.expiry)}</span>
         <span class="pill p-dim" title="a validade passou E o estado declarado no instantaneo ja e '${esc(p.status)}'. Os dois campos concordam: nao ha conflito a reportar.">VENCIDA &middot; ${esc(p.status)}</span>`
      : `<span style="color:var(--bad)">${esc(p.expiry)}</span>
         <span class="pill p-bad" title="a validade passou e o registro ainda lista o produto como '${esc(p.status)}'. Vencer nao e ser revogado.">VENCIDA</span>`;
  if (typeof D === 'number' && D <= 90)
    return `${esc(p.expiry)} <span class="pill p-warn">${D}d</span>`;
  return esc(p.expiry);
}
const byReg = Object.fromEntries(P.products.map(p => [p.reg, p]));

// ---------------------------------------------------------------- evidencia
function drawer(html) { $('#dr').innerHTML =
  `<button class="close" onclick="document.getElementById('dr').classList.remove('open')">&times;</button>${html}`;
  $('#dr').classList.add('open'); }

function evObj(id) {
  const o = P.objects.find(x => x.INTELLIGENCE_OBJECT_ID === id);
  if (!o) return;
  const rt = o.CAPABILITY_ROUTING.map(r =>
    `<div style="margin:3px 0"><b>${CAPS[r.CAPABILITY_ID]||r.CAPABILITY_ID}</b>
     <span class="pill ${r.ROUTING_STATE==='RELEVANT'?'p-ok':r.ROUTING_STATE==='POTENTIALLY_RELEVANT'?'p-warn':r.ROUTING_STATE==='UNKNOWN'?'p-unk':'p-dim'}">${r.ROUTING_STATE}</span>
     <code>${esc(r.RULE_ID)}</code><div class="meta">${esc(r.JUSTIFICATION)}</div></div>`).join('');
  drawer(`<h3>Evidencia</h3>
  <div class="meta">objeto <code>${esc(o.INTELLIGENCE_OBJECT_ID)}</code></div>
  <dl>
    <dt>Fato (o que a fonte diz)</dt><dd>${esc(o.FACT)}</dd>
    <dt>Significado regulatorio derivado</dt><dd>${val(o.DERIVED_REGULATORY_MEANING)}
      ${o.DERIVED_BY_RULE!=='NOT_PROVED'?`<code>${esc(o.DERIVED_BY_RULE)}</code>`:''}</dd>
    <dt>Implicacao de negocio</dt><dd>${val(o.POTENTIAL_BUSINESS_IMPLICATION)}
      <div class="meta">${esc(o.BUSINESS_IMPLICATION_NOTE)}</div></dd>
    <dt>Revisao recomendada</dt><dd>${val(o.RECOMMENDED_REVIEW)}</dd>
    <dt>Acao</dt><dd>${val(o.ACTION)}<div class="meta">esta ferramenta nao emite acao</div></dd>
    <dt>Antes &rarr; Depois</dt><dd>${val(o.BEFORE_VALUE)} &rarr; ${val(o.AFTER_VALUE)}</dd>
    <dt>Estado da prova</dt><dd><span class="pill ${PROOF[o.PROOF_STATE]||'p-dim'}">${esc(o.PROOF_STATE)}</span>
      &nbsp;<code>${esc(o.CONFIDENCE_STATE)}</code></dd>
    <dt>Documento antes</dt><dd class="mono">${val(o.SOURCE_DOCUMENT_BEFORE)}</dd>
    <dt>Documento depois</dt><dd class="mono">${val(o.SOURCE_DOCUMENT_AFTER)}</dd>
    <dt>Local da evidencia</dt><dd>${val(o.EVIDENCE_LOCATION)}</dd>
    <dt>Fonte oficial</dt><dd>${ehURL(o.SOURCE_URL)?link(o.SOURCE_URL,o.SOURCE_URL):val(o.SOURCE_URL||'NOT_KNOWN')}</dd>
    <dt>Autoridade</dt><dd>${val(o.SOURCE_AUTHORITY)}</dd>
    <dt>Capturado em</dt><dd>${val(o.CAPTURED_AT)}</dd>
    <dt>Detectado em</dt><dd>${val(o.DETECTED_AT)}</dd>
    <dt>Janela de observacao</dt><dd>${val(o.OBSERVATION_WINDOW||'NOT_APPLICABLE')}</dd>
    <dt>Parser</dt><dd class="mono">${val(o.PARSER_VERSION)}</dd>
    <dt>Regras</dt><dd class="mono">${esc(o.RULESET_VERSION)}</dd>
    <dt>Janela temporal</dt><dd>${janelaSelo(o)}
      <div class="meta">regra no build: <code>${esc(o.TIME_WINDOW_RULE)}</code>${hojeISO()
        ? ` &middot; recalculada contra ${esc(hojeISO())} pela regra <code>${esc(janelaAgora(o)[1])}</code>`
        : ` &middot; <span class="unknown">NOT_COMPUTED_WITHOUT_CLOCK</span>`}</div></dd>
  </dl>
  <h3 style="margin-top:16px">Quem pode precisar olhar</h3>${rt}`);
}
window.evObj = evObj;

function evProd(reg) {
  const p = byReg[reg]; if (!p) return;
  drawer(`<h3>${esc(p.name)}</h3>
  <div class="meta">registro <code>${esc(p.reg)}</code></div>
  <dl>
    <dt>Titular</dt><dd>${val(p.holder)}</dd>
    <dt>Estado administrativo</dt><dd>${val(p.status)}</dd>
    <dt>Validade declarada</dt><dd>${val(p.expiry)}</dd>
    <dt>Substancias ativas</dt><dd>${val(p.actives)}</dd>
    <dt>Instantaneo do registro</dt><dd class="mono">${esc(p.snapshot)}<br>sha256 ${esc(p.snapshot_sha)}</dd>
    <dt>Fonte do registro</dt><dd>${link(p.source_url,'CSV oficial')}</dd>
    <dt>PDF da etichetta</dt><dd>${link(p.pdf_url,'abrir no Ministero')}</dd>
    <dt>sha256 do PDF</dt><dd class="mono">${val(p.pdf_sha)}</dd>
    <dt>Bytes</dt><dd>${val(p.pdf_bytes)}</dd>
    <dt>Etichetta em vigor desde</dt><dd>${val(p.label_effective)}
      <div class="meta">data declarada pela fonte, nao inferida</div></dd>
    <dt>Capturado em</dt><dd>${val(p.captured_at)}</dd>
    <dt>Run de coleta</dt><dd class="mono">${val(p.run)}</dd>
    <dt>Estados de leitura</dt><dd>${Object.entries(p.states).map(([k,v])=>
      `<span class="pill ${v?'p-ok':'p-dim'}">${k}</span>`).join(' ')}</dd>
  </dl>`);
}
window.evProd = evProd;

function evUso(reg, i) {
  const p = byReg[reg], u = p.uses[i];
  drawer(`<h3>Uso autorizado</h3>
  <div class="meta">${esc(p.name)} &middot; <code>${esc(p.reg)}</code></div>
  <dl>
    <dt>Cultura</dt><dd>${val(u.crop)}</dd>
    <dt>Alvo</dt><dd>${val(u.target)}</dd>
    <dt>Token de origem lido pelo extrator</dt><dd>${val(u.crop_raw)} &middot; ${val(u.target_raw)}
      <div class="meta"><b>Isto NAO e citacao do rotulo.</b> E o texto que o extrator guardou como
      origem do par, e as vezes e rotulo interno do proprio leitor (por exemplo
      &ldquo;linha de dose por cultura&rdquo;, que e portugues e nao pode estar numa etichetta
      italiana). A citacao literal esta no campo abaixo.</div></dd>
    <dt>Classe de evidencia</dt><dd><span class="pill ${u.evidence==='TABLE_GEOMETRY'?'p-ok':'p-dim'}">${esc(u.evidence)}</span>
      <div class="meta">${u.evidence==='TABLE_GEOMETRY'
        ? 'linha lida da geometria da tabela; o indice de pagina do leitor de uso nao foi validado e nao e publicado'
        :'par montado a partir de prosa ou lista do rotulo, nao de uma linha de tabela'}</div></dd>
    <dt>Rota do extrator</dt><dd class="mono">${val(u.route)}</dd>
    <dt>Pagina</dt><dd>${isUnk(u.page)?val(u.page):
      `<span class="unknown">NOT_VALIDATED</span>
       <span class="meta">o leitor de uso grava um indice de pagina que nao foi validado contra
       o documento (e 0-indexado na origem). Nao publicamos numero de pagina para par de uso
       ate valida-lo.</span>`}</dd>
    <dt>Citacao literal</dt><dd>${val(u.quote)}
      <div class="meta">os pares reusados nao gravam coordenada x e a etichetta tem varias
      colunas por pagina; o trecho literal nao e recuperavel. Tentado e medido no piloto.</div></dd>
    <dt>Fonte</dt><dd>${link(p.pdf_url,'PDF oficial')}
      <div class="mono">sha256 ${esc(p.pdf_sha)}</div></dd>
    <dt>Leitor</dt><dd class="mono">it_rotulo_parser/3.4.0 (reuso de sintonia/canonical @ bdb57cf)</dd>
  </dl>
  <div class="lei">A frase correta e &ldquo;par extraido pelo nosso leitor a partir do rotulo&rdquo;,
  nunca &ldquo;o rotulo diz&rdquo;.</div>`);
}
window.evUso = evUso;

// R-18 · A FERRAMENTA USA ASPAS COM UM VERBO: "o rotulo escreve", "a linha de
// dose fala de". Aspas com esse verbo sao uma afirmacao sobre o documento — e
// convidam quem le a ir conferir. Citacao remontada e pior do que numero
// errado: manda a pessoa procurar no PDF uma frase que nao esta la, e o que ela
// conclui e que o PDF esta errado.
// Medido: 40 celulas de cultura e 28 de alvo citadas nao existem contiguas em
// nenhuma das quatro leituras do documento — sao montadas com pedaco de mais de
// uma celula. Em 008259 a celula "Orticole" termina em "zucchino" e "sedano" e
// celula PROPRIA, com linha e dose proprias: a string "zucchino sedano" nao
// existe no papel, e 318 doses a citavam.
// AUSENCIA DE ESTADO NAO E APROVACAO, e `!estado` era exatamente isso: um campo
// que nunca foi conferido saia entre aspas com o verbo "o rotulo escreve". O
// unico estado que autoriza aspas e o que diz que a frase esta la.
function citavel(estado) { return estado === 'QUOTE_VERBATIM'; }
// ...com uma excecao declarada: a linha de tabela remontada de celulas. Ela nao
// e contigua POR CONSTRUCAO — foi lida da esquerda para a direita atravessando
// colunas — e por isso ela nunca vai entre aspas, mas tambem nao e um defeito a
// denunciar: e o que o extrator faz. A tela ja a chama de "Linha remontada pelo
// extrator" em vez de "Citacao do documento".
function remontada(estado) { return estado === 'ROW_RECONSTRUCTED_FROM_CELLS'; }
function celulaCitada(txt, estado, oque) {
  if (citavel(estado)) return `<i>&ldquo;${esc(txt)}&rdquo;</i>`;
  const porque = estado === 'QUOTE_NOT_CONTIGUOUS_IN_DOCUMENT'
    ? `<b>nao existe contiguo em nenhuma leitura do documento</b>: ele junta pedaco de mais de
       uma celula`
    : estado === 'QUOTE_TOO_SHORT_TO_CHECK'
    ? `e <b>curto demais para ser conferido</b> (menos de 8 caracteres): achar essas letras no
       PDF nao prova que a celula e essa`
    : estado === 'QUOTE_CUT_MID_WORD'
    ? `existe no documento mas <b>termina no meio de uma palavra</b>: e um corte do extrator, e
       nao a frase que o rotulo escreve`
    : estado === 'QUOTE_IS_PREFIX_OF_LONGER_QUOTE'
    ? `e <b>prefixo estrito de outra frase do mesmo rotulo</b>, e prefixo inverte escopo`
    : `<b>nao foi conferido</b> contra o documento`;
  return `<span class="unknown">${esc(estado)}</span>
    <div class="meta">o texto que o extrator montou para ${esc(oque)} ${porque}. O que ele leu foi
    <code>${esc(String(txt).slice(0, 90))}</code> — mostrado como <b>leitura do extrator</b>, nao
    entre aspas como frase do rotulo</div>`;
}
function evDose(reg, i) {
  const p = byReg[reg], d = p.doses[i];
  drawer(`<h3>Dose</h3>
  <div class="meta">${esc(p.name)} &middot; <code>${esc(p.reg)}</code></div>
  <dl>
    <dt>Cultura</dt><dd>${citavel(d.crop_cell_state)?val(d.crop):val('CELL_TEXT_NOT_RECOVERABLE')}
      ${d.crop_inherited?'<span class="pill p-dim">CELULA MESCLADA</span>':''}
      ${citavel(d.crop_cell_state)?'':celulaCitada(d.crop,d.crop_cell_state,'a celula de cultura')}</dd>
    <dt>Alvo</dt><dd>${citavel(d.target_cell_state)?val(d.target):val('CELL_TEXT_NOT_RECOVERABLE')}
      ${citavel(d.target_cell_state)?'':celulaCitada(d.target,d.target_cell_state,'a celula de alvo')}</dd>
    <dt>Dose por hectare</dt><dd>${isUnk(d.dose_ha)?val(d.dose_ha):esc(d.dose_ha+' '+d.unit_ha)}
      ${d.dose_ha_inherited?'<span class="pill p-dim">HERDADA DE CELULA MESCLADA</span>':''}</dd>
    <dt>Dose por concentracao</dt><dd>${isUnk(d.dose_conc)?val(d.dose_conc):esc(d.dose_conc+' '+d.unit_conc)}</dd>
    <dt>Max. aplicacoes</dt><dd>${colunaMax(d)}
      ${d.max_app_inherited?`<span class="pill p-dim">HERDADA DE CELULA MESCLADA</span>
        <span class="pill ${d.max_check==='MAX_CONFIRMED_BY_RULE'?'p-ok':'p-unk'}">${esc(d.max_check)}</span>`:''}</dd>
    <dt>Intervalo</dt><dd>${colunaIntervalo(d)}
      ${d.interval_check&&d.interval_check!=='INTERVAL_NOT_INHERITED'
        ?`<span class="pill ${d.interval_check==='INTERVAL_CONFIRMED_BY_RULE'?'p-ok':'p-unk'}">${esc(d.interval_check)}</span>`:''}</dd>
    <dt>O texto do alvo existe literalmente no rotulo? (<code>R-13</code>)</dt>
      <dd><span class="pill ${d.target_literal==='TARGET_TEXT_FOUND_LITERALLY'?'p-ok':'p-unk'}">${val(d.target_literal)}</span>
      ${avisoAlvoLiteral(d)}</dd>
    <dt>Conferencia pelos fios da tabela</dt><dd>
      <span class="pill ${d.rule_check==='CONFIRMED_BY_RULE'?'p-ok':d.rule_check==='CONTRADICTED_BY_RULE'?'p-bad':'p-dim'}">${esc(d.rule_check)}</span>
      ${d.rejected?`<div class="meta">valor rebaixado: ${esc(d.rejected)} — um fio desenhado separa
        a linha do valor que ela recebeu. Rebaixado, nao corrigido no palpite.</div>`:''}</dd>
    <dt>Pagina</dt><dd>${val(d.page)}</dd>
    <dt>${citavel(d.quote_state)?'Citacao do documento'
          :remontada(d.quote_state)?'Linha remontada pelo extrator'
          :'Linha que o extrator montou, e que o documento nao confirma'}</dt>
      <dd><div class="quote">${esc(d.quote||'NOT_PRESERVED')}</div>
      ${citavel(d.quote_state)?'':`<div class="meta"><span class="unknown">${esc(d.quote_state)}</span>
        uma LINHA de tabela lida da esquerda para a direita atravessa colunas e <b>nunca e uma
        frase contigua</b> no documento — nao procure esta string no PDF. E, alem disso, esta
        traz palavra que nao esta na pagina que ela cita (inclusive anotacoes do proprio
        extrator, como <code>[celula mesclada: ...]</code>).</div>`}</dd>
    <dt>Fonte</dt><dd>${link(p.pdf_url,'PDF oficial')}
      <div class="mono">sha256 ${esc(p.pdf_sha)}</div></dd>
    <dt>Leitor</dt><dd class="mono">v1 dose_extrair + dose_validar (fios da tabela)</dd>
  </dl>`);
}
window.evDose = evDose;

// ---------------------------------------------------------------- 1 · TODAY
function cardObj(o) {
  const [jAgora, jRegra] = hojeISO() ? janelaAgora(o) : [o.TIME_WINDOW, o.TIME_WINDOW_RULE];
  const [cls, pill, lbl] = WIN[jAgora] || ['', 'p-dim', jAgora];
  const cons = o.CAPABILITY_ROUTING
    .filter(r => r.ROUTING_STATE === 'RELEVANT' || r.ROUTING_STATE === 'POTENTIALLY_RELEVANT')
    .map(r => `<span class="pill ${r.ROUTING_STATE==='RELEVANT'?'p-ok':'p-warn'}"
      title="regra ${esc(r.RULE_ID)}: ${esc(r.JUSTIFICATION)}">${CAPS[r.CAPABILITY_ID]||r.CAPABILITY_ID}</span>`);
  const semRota = cons.length === 0;
  return `<div class="card ${cls}">
    <h4>${esc(o.PRODUCT_NAME||'NOT_KNOWN')} <span class="meta mono">${esc(o.REGISTRATION_ID)}</span></h4>
    <div class="meta">${esc(o.FACT)}</div>
    <div class="ba"><span class="b">${val(o.BEFORE_VALUE)}</span>
      <span class="arr">&rarr;</span><span class="a">${val(o.AFTER_VALUE)}</span></div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:6px">
      <span class="pill p-dim">${esc(o.CHANGE_TYPE)}</span>
      <span class="pill ${pill}" title="${esc(jRegra)}${jAgora!==o.TIME_WINDOW?` — recalculada contra hoje; no build era ${esc(o.TIME_WINDOW)}`:''}">${lbl}</span>${
        jAgora!==o.TIME_WINDOW ? `<span class="meta" title="a janela e um numero de dias e foi recalculada contra o relogio de quem abre">&nbsp;recalculada (build: ${esc(o.TIME_WINDOW)})</span>` : ''}
      <span class="pill ${PROOF[o.PROOF_STATE]||'p-dim'}">${esc(o.PROOF_STATE)}</span>
      <span class="meta">detectado ${val(o.DETECTED_AT)}</span>
      <button class="ev" onclick="evObj('${o.INTELLIGENCE_OBJECT_ID}')">ver evidencia</button>
    </div>
    <div class="rt">${semRota
      ? '<span class="pill p-unk">SEM ROTEAMENTO PROVADO</span>'
      : '<span class="meta">pode interessar a:</span> ' + cons.join(' ')}</div>
  </div>`;
}

// S13 · a tela respondia "36 mudancas" a qualquer pergunta, porque a janela
// dela era os 14 meses inteiros. Quem pergunta "o que mudou nos ultimos 30
// dias?" merece a resposta honesta, que aqui e ZERO — a mudanca provada mais
// recente e de 20260720. Zero e uma resposta; 36 nao era.
let JANELA_DIAS = 0;                       // 0 = janela inteira observada
function setJanela(d) { if (!hojeISO()) return; JANELA_DIAS = Number(d) || 0; viewToday(); }
window.setJanela = setJanela;
function dentroDaJanela(o) {
  if (!JANELA_DIAS) return true;
  const d = dias(dISO(o.DETECTED_AT));
  // d e negativo para fato passado. Duas travas: sem relogio nao ha janela
  // (o chamador ja garante isso), e fato com data FUTURA (d > 0) nao entra numa
  // janela que conta para tras — antes entrava, porque a condicao so olhava
  // -d <= JANELA e -d de um futuro e negativo.
  return d !== null && d <= 0 && -d <= JANELA_DIAS;
}

function viewToday() {
  const todosProvados = P.objects.filter(o => o.PROOF_STATE === 'PROVED');
  const provados = hojeISO() ? todosProvados.filter(dentroDaJanela) : todosProvados;
  const rev = P.objects.filter(o => o.OBJECT_TYPE === 'NEEDS_HUMAN_REVIEW');
  const dq = P.objects.filter(o => o.OBJECT_TYPE === 'DATA_QUALITY_EVENT');
  const exp = provados.filter(o => o.OBJECT_TYPE === 'EXPIRY_EVENT');
  const ordem = {ACT_NOW:0, PREPARE:1, MONITOR:2, PLAN_NEXT_CYCLE:3, NO_ACTION_YET:4, UNKNOWN:5};
  // Um vencimento que passou NAO e uma mudanca: e uma condicao que continua valendo.
  // Misturar os dois faz 15 cards iguais soterrarem as mudancas de verdade.
  const mudancas = provados.filter(o => o.OBJECT_TYPE !== 'EXPIRY_EVENT').sort((a,b) =>
    (ordem[(hojeISO()?janelaAgora(a)[0]:a.TIME_WINDOW)]??9) - (ordem[(hojeISO()?janelaAgora(b)[0]:b.TIME_WINDOW)]??9) ||
    String(b.DETECTED_AT).localeCompare(String(a.DETECTED_AT)));
  const condicoes = exp.slice().sort((a,b) => String(a.VALID_FROM).localeCompare(String(b.VALID_FROM)));
  // SF-10 · O KPI DIZIA "hojeISO()" SOBRE UM NUMERO DE OUTRO DIA.
  // O conjunto EXPIRY_EVENT e congelado no build; o CALENDARIO recalcula o
  // MESMO criterio contra o relogio de quem abre. Medido: no relogio real os
  // dois davam 15 (coerente, e por isso passava despercebido); com o relogio em
  // 2026-12-01 o calendario dizia 41 e esta tela continuava em 15; em
  // 2040-06-20, 146 contra 15. A palavra "hoje" ficava sobre um numero do dia do
  // build. Agora o conjunto e recalculado aqui com a MESMA funcao que o
  // calendario usa, e os que o build nao viu aparecem dizendo que nao tem
  // objeto de evidencia — porque nao tem, e inventar um seria pior.
  const conflitoAgora = P.products.filter(conflitoDeValidade)
    .sort((a,b) => String(a.expiry).localeCompare(String(b.expiry)));
  const comObjeto = new Set(exp.map(o => o.REGISTRATION_ID));
  const novos = conflitoAgora.filter(p => !comObjeto.has(p.reg));
  const OPC = [[30,'30 dias'],[90,'90 dias'],[365,'12 meses'],[0,'janela inteira observada']];
  // SEM RELOGIO NAO HA JANELA. Com window.Date quebrado, dias() devolve null,
  // dentroDaJanela() rejeitava tudo e a tela respondia "0 mudancas nos ultimos
  // 365 dias — e isso e uma resposta, nao uma falha". Zero por falta de relogio
  // nao e zero: e NOT_COMPUTED_WITHOUT_CLOCK. Falha de medicao nao e ausencia.
  const semRelogio = !hojeISO();
  $('#v-today').innerHTML = `
  ${avisoRelogio()}
  ${GLOSA_JANELA}
  <div class="block" style="padding:9px 12px">
    <b>Janela:</b>
    ${semRelogio
      ? `<span class="unknown">NOT_COMPUTED_WITHOUT_CLOCK</span>
         <div class="meta">este navegador nao devolveu a data de hoje. Uma janela que conta para
         tras a partir de hoje nao pode ser calculada sem hoje, entao os botoes estao desligados e
         a tela mostra a janela inteira observada. <b>Zero por falta de relogio nao e zero.</b></div>`
      : OPC.map(([d,l]) => `<button class="ev" style="${JANELA_DIAS===d?'outline:2px solid var(--ok)':''}"
         onclick="setJanela(${d})">${l}</button>`).join(' ')}
    <div class="meta" style="margin-top:5px">${JANELA_DIAS && !semRelogio
      ? `contando para tras a partir de <b>hoje</b> (${esc(hojeISO())}), nao a partir da data
         do dado.${(() => {
           // Os dias entre a data do dado e hoje NAO foram cobertos por coleta
           // nenhuma. Para eles a resposta nao e zero: e NOT_COLLECTED. Uma
           // janela de 30 dias que termina hoje, com dado de 6 dias atras,
           // cobre 24 dias e nao 30 — e a tela tem de dizer qual e qual.
           const desc = idadeDoDado() === null ? null : -idadeDoDado();
           if (!desc || desc <= 0) return '';
           const cob = Math.max(0, JANELA_DIAS - desc);
           return ` <b>Desta janela de ${JANELA_DIAS} dias, ${cob} foram cobertos por coleta e
             ${Math.min(desc, JANELA_DIAS)} nao</b>: o instantaneo mais novo e de
             ${esc(DATA_DATE)}. Para os dias descobertos a resposta e
             <span class="unknown">NOT_COLLECTED</span>, nao zero.`;
         })()} ${mudancas.length===0
           ? `<b>Nesta janela nao ha mudanca</b> — e isso e uma resposta, nao uma falha: a mudanca
              provada mais recente do conjunto e de <b>${esc(ULTIMA_MUDANCA)}</b>, e nada foi
              coletado depois de ${esc(DATA_DATE)}. As condicoes que continuam valendo, mais
              abaixo, <b>nao</b> sao filtradas por janela: elas nao mudaram numa data, elas
              seguem de pe.` : ''}`
      : `todos os ${todosProvados.length} objetos provados das ${P.versions.length} versoes
         observadas (${esc(P.history.window)}).`}</div>
  </div>
  <div class="cards">
    <div class="kpi"><b>${mudancas.length}</b><span>mudancas provadas ${JANELA_DIAS&&!semRelogio?`nos ultimos ${JANELA_DIAS} dias`:'na janela observada'}</span></div>
    <div class="kpi"><b style="color:var(--bad)">${conflitoAgora.length}</b><span>validade vencida e ainda listado ativo${
      conflitoAgora.length!==exp.length?` <b>(no build eram ${exp.length})</b>`:''}</span></div>
    <div class="kpi"><b style="color:var(--rev)">${rev.length}</b><span>itens que a maquina recusou adivinhar</span></div>
    <div class="kpi"><b style="color:var(--unk)">${dq.length}</b><span>estados de leitura a resolver</span></div>
    <div class="kpi"><b class="mono" style="font-size:15px">${esc(P.history.window)}</b><span>janela observada (coleta)</span></div>
  </div>
  <div class="lei"><b>${P.history.raw_field_diffs}</b> diferencas brutas entre os instantaneos oficiais.
    <b>${P.history.noise}</b> (${P.history.noise_pct}%) sao a fonte reordenando a propria lista e nao viram evento.
    Restam <b>${P.history.true_changes}</b> mudancas reais na janela inteira observada.
    ${JANELA_DIAS?`Voce esta olhando um recorte de <b>${JANELA_DIAS} dias</b> dentro dela.`:''}
    O que voce ve abaixo ja passou por esse filtro.</div>
  <h2>Mudou entre dois instantaneos oficiais (${mudancas.length})</h2>
  <div class="meta" style="margin-bottom:8px">Um campo do registro tinha um valor e passou a ter
    outro. Cada card mostra o antes, o depois, e os dois documentos que provam.</div>
  ${mudancas.map(cardObj).join('') || '<div class="block meta">nenhuma mudanca provada na janela</div>'}

  <h2>Condicoes que continuam valendo hoje (${conflitoAgora.length})</h2>
  <div class="lei">Isto <b>nao mudou agora</b>: e um conflito entre dois campos oficiais que segue
    de pe. A validade declarada ja passou e o registro continua listando o produto como autorizado.
    <b>Vencer nao e ser revogado</b> &mdash; a ferramenta mostra os dois campos e nao conclui saida
    de mercado.
    ${novos.length ? `<div class="meta" style="margin-top:6px"><b>${novos.length} deste conjunto o
      build nao tinha visto:</b> a validade deles passou entre a data do build
      (${esc(P.BUILT_AT)}) e hoje (${esc(hojeISO())}). Eles entram na conta porque o criterio e
      recalculado contra o SEU relogio — mas <b>nao tem objeto de inteligencia</b>, porque nenhum
      foi emitido para eles, e inventar um seria pior do que a falta.
      ${novos.map(p=>`<code>${esc(p.reg)}</code> ${esc(p.name)}`).join(' &middot; ')}</div>` : ''}
    ${conflitoAgora.length !== exp.length ? '' : `<div class="meta" style="margin-top:6px">Hoje o
      numero recalculado bate com o do build (${exp.length}). Isso nao e sempre verdade: o
      conjunto do build envelhece e o desta tela nao.</div>`}</div>
  <div class="tw"><table>
    <thead><tr><th>Validade</th><th>Ha</th><th>Produto</th><th>Registro</th>
      <th>Estado declarado hoje</th><th></th></tr></thead>
    <tbody>${condicoes.map(o => {
      const p2 = byReg[o.REGISTRATION_ID] || {};
      return `<tr><td class="mono" style="color:var(--bad)">${esc(o.VALID_FROM)}</td>
      <td>${typeof dte(p2) === 'number' ? (-dte(p2))+'d' : val('NOT_KNOWN')}</td>
      <td>${esc(o.PRODUCT_NAME)}</td><td class="mono">${esc(o.REGISTRATION_ID)}</td>
      <td>${val(p2.status)}</td>
      <td><button class="ev" onclick="evObj('${o.INTELLIGENCE_OBJECT_ID}')">evidencia</button></td></tr>`;
    }).join('')}</tbody></table></div>`;
}

// ---------------------------------------------------------------- 2 · PRODUCT 360
// MF-04 · MAX. APLICACOES e INTERVALO herdados de celula mesclada tem de passar
// por fio, como a cultura passa em R-11. Nao passavam: a heranca publicava o
// valor da linha VIZINHA como fato, com selo HERDADA e "CONFERENCIA PELOS FIOS
// = CONFIRMED_BY_RULE", em 96 pares. Numero de tratamentos e restricao
// regulatoria — e o que a LEI ZERO nomeia.
//
// MF-05 · e quando a LINHA inteira foi reprovada por R-11, abster-se do numero
// grande e imprimir o pequeno errado ao lado nao e abstencao: as duas colunas
// vieram da MESMA leitura de geometria que a ferramenta acabou de reprovar.
function linhaReprovada(d) {
  return d.crop_check === 'CROP_ASSIGNMENT_CONTRADICTED_BY_RULE'
      || d.rule_check === 'NOT_LOCATED'
      || d.rule_check === 'PLAUSIBILITY_REJECTED'
      // R-22 · a banda que o extrator leu como UMA linha tem um risco desenhado
      // por dentro, com texto dos dois lados: sao DUAS linhas coladas, e o
      // numero pode ser da de baixo. Em 018270 o unico "1" da regiao esta do
      // outro lado do risco, e era publicado como dose do MAIS.
      || d.band_check === 'DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE';
}
function colunaHerdada(d, valor, estado, nomeCampo) {
  if (linhaReprovada(d))
    return val('NOT_PROVED_BY_RULE');
  if (estado === 'MAX_NOT_PROVED_NOTE_BLOCK_UNKNOWN')
    return `${val('NOT_PROVED_BY_LABEL_NOTE')}<div class="meta">ha nota de numero de aplicacoes
      que ENUMERA culturas e nomeia esta, e ela diz um numero diferente de <b>${esc(valor)}</b> —
      mas este leitor <b>nao conseguiu estabelecer que a nota e do bloco desta linha</b>. Uma
      etichetta com dois blocos (pieno campo e serra) tem uma nota por bloco. O numero nao e
      publicado; a nota tambem nao e afirmada
      ${d.note_says?`<div class="meta"><i>&ldquo;${esc(String(d.note_says).slice(0,180))}&rdquo;</i></div>`:''}
      (<code>R-15</code>)</div>`;
  if (estado === 'MAX_CONTRADICTED_BY_LABEL_NOTE')
    return `${val('NOT_PROVED_BY_LABEL_NOTE')}<div class="meta">a tabela dizia
      <b>${esc(valor)}</b> por posicao de linha; a nota da etichetta que ENUMERA culturas poe
      esta cultura na lista de <b>${esc(d.note_max)}</b> aplicacao(oes)
      ${d.note_says?`<i>&ldquo;${esc(String(d.note_says).slice(0,180))}&rdquo;</i>`:''}
      (<code>R-15</code>)</div>`;
  if (estado === 'MAX_CONTRADICTED_BY_RULE' || estado === 'INTERVAL_CONTRADICTED_BY_RULE')
    return `${val('NOT_PROVED_BY_RULE')}<div class="meta">o valor <b>${esc(valor)}</b> foi herdado
      de celula mesclada e <b>nenhuma celula desenhada que o contem cobre esta linha</b>: ele e da
      linha vizinha (<code>R-15</code>)</div>`;
  if (estado === 'MAX_NOT_VALIDATED' || estado === 'INTERVAL_NOT_VALIDATED')
    return `${val('NOT_VALIDATED')}<div class="meta">valor herdado de celula mesclada que este
      leitor nao conseguiu conferir contra os fios da coluna. <b>Isto e "nao conferi", nao
      "confere"</b></div>`;
  return val(valor);
}
function colunaMax(d) { return colunaHerdada(d, d.max_app, d.max_check, 'MAX'); }
function colunaIntervalo(d) { return colunaHerdada(d, d.interval, d.interval_check, 'INTERVALO'); }

// MF-06 · a ferramenta CALCULAVA o veredito R-13 e nao o lia em lugar nenhum da
// tela de produto: `target_literal` aparecia em juntaDose e em celulaDose, e em
// mais lugar nenhum. Consequencia medida: 55 linhas saiam com numero e selo
// CONFIRMADA enquanto o proprio payload as marcava TARGET_TEXT_NOT_FOUND_LITERALLY
// — entre elas a quimera "Nottue defogliatrici (allo scoperto) tentredine", que
// a REGRAS.md cita como FUSION_PROVEN_EXAMPLE. E a MESMA linha, na tela
// CULTURA x ALVO, era recusada: duas telas da mesma ferramenta davam estados de
// prova opostos sobre o mesmo fato do mesmo documento.
function avisoAlvoLiteral(d) {
  if (d.target_literal === 'TARGET_TEXT_NOT_FOUND_LITERALLY')
    return `<div class="meta"><span class="unknown">TARGET_TEXT_NOT_FOUND_LITERALLY</span>
      este texto de alvo <b>nao existe literalmente no rotulo</b>. Pode ser alvo quebrado entre
      colunas (inofensivo) ou <b>fusao de duas linhas da tabela</b>, que existe e esta provada em
      008259. <code>FUSION_DETECTOR = NOT_IMPLEMENTED</code></div>`;
  if (d.target_literal === 'TARGET_TEXT_NOT_CHECKED')
    return `<div class="meta"><span class="unknown">TARGET_TEXT_NOT_CHECKED</span>
      esta linha nao foi submetida a <code>R-13</code>. Nao conferido nao e conferido</div>`;
  return '';
}
// O selo dos fios descrevia SO o fio do VALOR. Uma linha cujo alvo nao existe
// no documento nao pode receber o selo mais forte da tela.
function seloFios(d) {
  // R-22 primeiro: se a banda de onde a linha foi lida tem um risco desenhado
  // por dentro, nao ha o que confirmar — o numero pode ser da linha de baixo.
  if (d.band_check === 'DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE')
    return `<span class="unknown" title="${esc(String(d.band_proof||'').slice(0,300))}"
      >DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE</span>
      <div class="meta">a banda de onde esta linha foi lida tem um <b>fio horizontal
      desenhado por dentro</b>, com texto acima e abaixo dele: a etichetta separou duas linhas
      e o extrator leu as duas como uma. O numero nao e publicado, porque ele pode ser da
      linha de baixo (<code>R-22</code>)</div>`;
  const ok = d.rule_check === 'CONFIRMED_BY_RULE';
  const literalRuim = d.target_literal === 'TARGET_TEXT_NOT_FOUND_LITERALLY';
  if (ok && literalRuim)
    return `<span class="pill p-unk" title="o valor confere pelos fios, mas o texto do alvo
      desta linha nao existe literalmente no rotulo">VALOR CONFERIDO &middot; ALVO NAO LITERAL</span>`;
  if (ok && d.target_literal === 'TARGET_TEXT_NOT_CHECKED')
    return `<span class="pill p-unk" title="o valor confere pelos fios; o texto do alvo nao foi
      submetido a R-13">VALOR CONFERIDO &middot; ALVO NAO CONFERIDO</span>`;
  return `<span class="pill ${ok?'p-ok':d.rule_check==='CONTRADICTED_BY_RULE'?'p-bad':'p-unk'}"
    title="${d.rule_check==='NOT_LOCATED'?'a linha ou o valor nao foi localizado no documento para conferir contra os fios':d.rule_check==='NOT_CHECKED'?'esta linha nao foi submetida a conferencia por fios':''}"
    >${ok?'CONFIRMADA':d.rule_check==='CONTRADICTED_BY_RULE'?'REVISAR':esc(d.rule_check)}</span>`;
}

function viewProduto(reg) {
  const p = byReg[reg] || P.products[0];
  $('#psel').value = p.reg;
  const objs = P.objects.filter(o => o.REGISTRATION_ID === p.reg);
  const D = dte(p);
  // MF-10 · a ficha afirmava CONFLITO sobre EVOLUTION EC e CS, cujos dois
  // campos oficiais CONCORDAM (data_scadenza 04/08/2008 e stato_amministrativo
  // "Scaduto"): inventava desacordo onde a fonte nao tem nenhum. A funcao que
  // resolve isso ja existia e era chamada pela BUSCA e pelo CALENDARIO; esta
  // tela, a unica que descreve o produto isolado, nao a chamava.
  const venc = conflitoDeValidade(p);
  const vencCoerente = typeof D === 'number' && D < 0 && foraDeVigor(p);
  const porCultura = {};
  p.uses.forEach((u,i) => (porCultura[u.crop] = porCultura[u.crop]||[]).push({...u, i}));
  $('#pdet').innerHTML = `
  ${p.out_of_active_set ? `<div class="lei"><b>Este registro nao esta no conjunto ativo do
    instantaneo vigente.</b> ${esc(p.out_of_active_set_note)}
    ${p.registry_row_read ? `<div class="meta" style="margin-top:6px">
      <b>Sair do conjunto ativo nao e sair do arquivo.</b> A linha oficial deste produto foi lida
      no instantaneo <code>${esc(p.snapshot)}</code>: os campos de registro abaixo sao leitura,
      nao suposicao. O que falta e o rotulo — nenhum PDF foi baixado, por isso uso, dose e PHI
      chegam como <span class="unknown">NOT_COLLECTED</span>.</div>` : ''}</div>` : ''}
  <div class="block">
    <div style="display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap">
      <h3>${esc(p.name)}</h3>
      <button class="ev" onclick="evProd('${p.reg}')">ver proveniencia</button></div>
    <div class="meta">registro <code>${esc(p.reg)}</code> &middot; ${esc(p.holder)} &middot; ${esc(p.activity)}</div>
    <div class="tw" style="margin-top:9px"><table><tbody>
      <tr><th>Substancias ativas</th><td>${val(p.actives)}</td></tr>
      <tr><th>Formulacao</th><td>${val(p.formulation)}</td></tr>
      <tr><th>Estado administrativo</th><td>${val(p.status)}</td></tr>
      <tr><th>Registrado em</th><td>${val(p.registered_at)}</td></tr>
      <tr><th>Validade</th><td${(venc||vencCoerente)?' style="color:var(--bad)"':''}>${val(p.expiry)}
        ${venc?` &mdash; vencida ha ${-D} dias e o registro ainda o lista como &ldquo;${esc(p.status)}&rdquo;.
        <span class="meta">EXPIRY != WITHDRAWAL — a ferramenta nao conclui saida de mercado</span>`
        :vencCoerente?` &mdash; <b>VENCIDA &middot; ${esc(p.status)}</b> — os dois campos oficiais
        concordam, nao ha conflito a reportar.
        <span class="meta">EXPIRY != WITHDRAWAL — a ferramenta nao conclui saida de mercado</span>`:''}</td></tr>
      ${p.revoke_effective!==undefined ? `
      <tr><th>Perigo declarado</th><td>${val(p.hazard)}</td></tr>
      <tr><th>Revoga &middot; motivo</th><td>${val(p.revoke_reason)}</td></tr>
      <tr><th>Revoga &middot; decreto</th><td>${val(p.revoke_decree)}</td></tr>
      <tr><th>Revoga &middot; decorrencia</th><td>${val(p.revoke_effective)}</td></tr>` : ''}
      <tr><th>Etichetta em vigor desde</th><td>${val(p.label_effective)}</td></tr>
      ${p.label_validity_state === 'VALIDITY_PHRASE_PRESENT_FORM_NOT_READ' ? `
      <tr><th>Vigencia declarada NA PROPRIA etichetta</th>
        <td><span class="unknown">VALIDITY_PHRASE_PRESENT_FORM_NOT_READ</span>
          <div class="meta"><b>o rotulo declara vigencia, e este leitor nao sabe estruturar esta
          forma.</b> Ele conhece &ldquo;valida dal X al Y&rdquo;, que existe em 1 dos 163
          documentos; este escreve <code>${esc(p.label_validity_form)}</code>, que existe em 112.
          Dizer <code>NOT_PRESENT</code> aqui seria publicar
          <code>PARSER_FAILURE</code> como <code>REGULATORY_ABSENCE</code>.
          O documento escreve: <i>&ldquo;${esc(p.label_validity_literal)}&rdquo;</i>
          <div class="meta">A ferramenta <b>nao</b> converte essa data no campo de vigencia: nada
          no acervo prova que a data do &ldquo;modificata ai sensi ... con validita dal&rdquo; e o
          mesmo fato que a data do &ldquo;valida dal ... al ...&rdquo;. Quem precisa dela le a
          frase.</div></div></td></tr>` : ''}
      ${p.label_valid_to && !isUnk(p.label_valid_to) ? `
      <tr><th>Vigencia declarada NA PROPRIA etichetta</th>
        <td${(hojeISO() && p.label_valid_to < hojeISO()) ? ' style="color:var(--bad)"' : ''}>
          ${esc(p.label_valid_from)} &rarr; <b>${esc(p.label_valid_to)}</b>
          ${(hojeISO() && p.label_valid_to < hojeISO())
            ? ` &mdash; <b>a vigencia que o proprio documento declara ja terminou</b>`
            : ''}
          <div class="meta">o documento escreve: <i>&ldquo;${esc(p.label_validity_quote)}&rdquo;</i>.
          A ferramenta guardava so o &ldquo;dal&rdquo; e ficava com a metade que envelhece bem.
          Isto e o que a ETICHETTA diz sobre si mesma, e nao se confunde com a validade da
          AUTORIZACAO no registro, que esta na linha acima.</div></td></tr>` : ''}
      <tr><th>Documento</th><td class="mono">${val(p.pdf_sha)}</td></tr>
    </tbody></table></div>
  </div>

  <div class="block">
    <div style="display:flex;justify-content:space-between;align-items:baseline">
      <h3>Usos autorizados</h3>
      <span class="meta">${(p.states&&p.states.LABEL_DOWNLOADED===false)
        ? val('NOT_COLLECTED')+' — nenhum rotulo foi baixado, entao nao ha par a contar'
        : `${p.uses.filter(u=>u.fact).length} <b>FATO</b> &middot;
           ${p.uses.filter(u=>!u.fact).length} <span class="unknown">NAO_VERIFICADO</span>
           <span class="meta">(de ${p.uses.length} pares)</span>`}</span></div>
    ${p.uses.length && p.uses.every(u=>!u.fact) ? `<div class="lei" style="border-left-color:var(--bad)">
      <b>Nenhum dos ${p.uses.length} pares deste produto e fato.</b> Ou eles vem de PROSA — e a
      ferramenta nao tem instrumento nenhum para prosa, tres foram medidos e falharam — ou o
      nome do alvo nao esta escrito no rotulo. <b>Isto nao nega o uso</b>: nega que esta
      ferramenta o tenha provado. <code>PARSER_FAILURE != REGULATORY_ABSENCE</code></div>` : ''}
    ${p.uses.length ? `<div class="tw"><table>
      <thead><tr><th>Cultura</th><th>Alvos</th><th>Evidencia</th><th></th></tr></thead>
      <tbody>${Object.entries(porCultura).sort().map(([c,us]) => `<tr>
        <td><b>${esc(c)}</b>${escopoDaCultura(us[0])}${
          nomeDaCultura(us.find(u => u.crop_name === 'CROP_NAME_NOT_IN_LABEL') || us[0])}</td>
        <td class="meta">${[...new Set(us.map(u=>u.target))].join(' &middot; ')}
          ${[...new Map(us.filter(u=>(u.target_scope||[]).length)
              .map(u=>[u.target,u])).values()].map(escopoDoAlvo).join('')}</td>
        <td>${(()=>{
          // O selo TABELA descrevia so a ROTA de leitura, e por isso ficava
          // verde tambem nos pares que nunca tinham passado por fio nenhum.
          // Agora ele conta o veredito de R-14.
          const fa = us.filter(x=>x.fact).length;
          const ok = us.filter(x=>x.pair_check==='PAIR_CONSISTENT_WITH_RULES').length;
          const nl = us.filter(x=>x.target_name==='TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL').length;
          const nc = us.filter(x=>x.crop_name==='CROP_NAME_NOT_IN_LABEL').length;
          return `${fa?`<span class="pill p-ok" title="prova contra o documento E os dois nomes escritos no rotulo">FATO ${fa}</span> `:''}${
            us.length-fa?`<span class="pill p-unk" title="uma das tres colunas nao fecha">NAO_VERIFICADO ${us.length-fa}</span> `:''}
            <div class="meta">${ok} com fio conferido &middot; ${us.length-ok} sem teste de fio${
              nl?` &middot; <span class="unknown">${nl} com nome de alvo vindo de taxonomia</span>`:''}${
              nc?` &middot; <span class="unknown">${nc} com NOME DE CULTURA que o rotulo nao escreve</span>`:''}</div>
            ${(()=>{ // O NOME DA IGNORANCIA, e nao so a contagem dela. "sem teste de fio"
                     // junta cinco motivos diferentes num numero, e um deles chegou a
                     // AFIRMAR que a coluna nao tinha grade onde ela tem 17 fios.
              const est=[...new Set(us.map(x=>x.pair_check))].filter(
                x=>x && x!=='PAIR_CONSISTENT_WITH_RULES' && PAR_ROTULO[x]);
              if(!est.length) return '';
              return `<div class="meta">${est.map(x=>
                `<span class="unknown" title="${esc(PAR_ROTULO[x][2])}">${esc(PAR_ROTULO[x][1])}</span>`
              ).join(' &middot; ')}</div>`;})()}`;})()}
          ${(()=>{ // o estado da conferencia R-10 existia no payload e nunca aparecia:
                   // 12 pares publicados como CROP_NAME_NOT_FOUND_IN_LABEL_TEXT (o rotulo
                   // escreve "Grano", o leitor normaliza para FRUMENTO) eram desenhados
                   // exatamente como um par conferido.
            const e = [...new Set(us.map(x => x.exclusion_check).filter(Boolean))];
            if (!e.length || (e.length===1 && e[0]==='ATTESTED_OUTSIDE_EXCLUSION')) return '';
            return e.filter(x=>x!=='ATTESTED_OUTSIDE_EXCLUSION').map(x =>
              `<div class="meta"><span class="unknown">${esc(x)}</span>
               ${x==='CROP_NAME_NOT_FOUND_IN_LABEL_TEXT'
                 ? 'o nome desta cultura nao aparece no texto do rotulo, nem dentro nem fora de janela de exclusao. Isto e diferenca de vocabulario, nao ausencia de uso — e nao foi conferido por este teste'
                 : x==='CROP_NAME_PREFIX_MATCH_ONLY'
                 ? 'o apoio textual e so por prefixo, nao por palavra inteira: basta para nao retirar o uso, nao basta para chamar de atestado'
                 : 'estado de conferencia declarado pela coleta'}</div>`).join('');
          })()}</td>
        <td>${us.map(x=>`<button class="ev" title="${esc(x.target)}" onclick="evUso('${p.reg}',${x.i})">${esc(String(x.target).slice(0,14))}</button>`).join(' ')}</td>
      </tr>`).join('')}</tbody></table></div>`
      : (p.states && p.states.LABEL_DOWNLOADED === false
         ? `<div class="lei">Nenhum rotulo foi baixado para este produto, entao <b>nenhum leitor
            rodou</b>: isto e <span class="unknown">NOT_COLLECTED</span>, nao falha de parser e
            nao ausencia de uso autorizado. Dizer <code>PARSER_FAILURE</code> aqui seria descrever
            um mecanismo que nao aconteceu.</div>`
         : `<div class="lei">Nenhum par cultura x alvo foi lido para este produto.
            <b>Isto e estado de leitura, nao ausencia de uso autorizado.</b>
            <code>PARSER_FAILURE != REGULATORY_ABSENCE</code></div>`)}
    ${(p.uses_retirados||[]).length ? `<div class="lei" style="border-left-color:var(--bad);margin-top:10px">
      <b>Exclusao nao e permissao.</b> ${p.uses_retirados.length} par(es) que o leitor de uso tinha
      publicado como <b>autorizados</b> foram retirados desta ficha, porque a unica ocorrencia do
      nome da cultura no texto do rotulo esta <b>dentro</b> de uma janela de exclusao. Regra
      <code>${esc(P.exclusion.rule)}</code>.
      ${(() => { const nu = P.exclusion.marker_not_used || {};
        const ks = Object.keys(nu); if (!ks.length) return '';
        return `<div class="meta" style="margin-top:6px"><b>E o que esta regra NAO usa</b>, com
          nome e numero: ${ks.map(k => `<code>${esc(k)}</code> (${nu[k]})`).join(' &middot; ')}.
          <span class="unknown">EXCLUSION_MARKER_NOT_USED</span> — medido: nenhuma das janelas
          que essas formas abrem nomeia uma cultura publicada aqui como uso autorizado; no
          acervo de hoje elas restringem o MODO (&ldquo;in prossimita delle acque&rdquo;,
          &ldquo;in serra&rdquo;) e nao a cultura. Isto <b>nao</b> quer dizer que nao ha
          exclusao nesses rotulos.</div>`;})()}
      <div class="tw" style="margin-top:8px"><table>
        <thead><tr><th>Cultura retirada</th><th>Alvo</th><th>Frase do rotulo que a exclui</th></tr></thead>
        <tbody>${p.uses_retirados.map(w => `<tr>
          <td><b>${esc(w.CROP)}</b></td><td>${esc(w.TARGET)}</td>
          <td><i>&ldquo;${esc(w.EXCLUSION_TEXT)}&rdquo;</i>
            <div class="meta">${esc(w.PROOF)}</div>
            <div class="meta">documento: <code>sha256=${esc(String(w.LABEL_SHA256||'NOT_KNOWN').slice(0,16))}…</code>
              &middot; ${esc(w.LABEL_BYTES)} bytes &middot; ${link(w.LABEL_URL,'abrir no Ministero')}
              &middot; marcador <code>${esc(w.EXCLUSION_QUOTE_STATE)}</code></div></td></tr>`).join('')}
        </tbody></table></div></div>` : ''}
    ${(p.uses_contraditos||[]).length ? `<div class="lei" style="border-left-color:var(--bad);margin-top:10px">
      <b>A etichetta nao autoriza estes usos.</b> ${p.uses_contraditos.length} par(es) que o leitor
      de uso tinha publicado como <b>autorizados</b> — e com o selo <span class="pill p-ok">TABELA</span>,
      o mais forte da tela — foram retirados desta ficha porque <b>nenhuma celula desenhada que
      contem o nome da cultura contem qualquer glifo do alvo</b>. Regra <code>R-14</code>: e o mesmo
      teste de fio que <code>R-11</code> ja fazia na linha de dose e que nunca tinha sido feito no
      PAR DE USO, que e a afirmacao regulatoria mais fundamental das duas.
      <div class="tw" style="margin-top:8px"><table>
        <thead><tr><th>Cultura</th><th>Alvo retirado</th><th>Prova geometrica</th></tr></thead>
        <tbody>${p.uses_contraditos.map(w => `<tr>
          <td><b>${esc(w.CROP)}</b></td><td>${esc(w.TARGET)}</td>
          <td class="meta">${esc(w.PROOF)}
            <div class="meta">celula lida do rotulo: <i>&ldquo;${esc(String(w.CROP_AS_WRITTEN||'NOT_PRESERVED').slice(0,90))}&rdquo;</i>
              &middot; rota <code>${esc(w.ROUTE)}</code> &middot; ${link(w.LABEL_URL,'abrir no Ministero')}</div></td></tr>`).join('')}
        </tbody></table></div></div>` : ''}
    ${(p.uses_rotacao||[]).length ? `<div class="lei" style="border-left-color:var(--bad);margin-top:10px">
      <b>Proibir de semear nao e autorizar a tratar.</b> ${p.uses_rotacao.length} par(es) sairam
      desta ficha porque <b>toda</b> ocorrencia do nome da cultura no rotulo esta dentro de uma
      frase de <b>semeadura em sucessao</b> — a etichetta diz quando aquela cultura pode ser
      SEMEADA DEPOIS do tratamento, nao que este produto a trata. Regra <code>R-10b</code>.
      <div class="tw" style="margin-top:8px"><table>
        <thead><tr><th>Cultura</th><th>Alvo</th><th>Frase do rotulo</th></tr></thead>
        <tbody>${p.uses_rotacao.map(w => `<tr>
          <td><b>${esc(w.CROP)}</b></td><td>${esc(w.TARGET)}</td>
          <td><i>&ldquo;${esc(w.ROTATION_TEXT)}&rdquo;</i>
            <div class="meta">${esc(w.PROOF)} &middot; ${link(w.LABEL_URL,'abrir no Ministero')}</div></td></tr>`).join('')}
        </tbody></table></div></div>` : ''}
    ${(p.exclusion_windows||[]).length ? `<div class="meta" style="margin-top:8px">
      <b>Este rotulo tem ${p.exclusion_windows.length} janela(s) de exclusao que falam de
      CULTURA.</b> Mesmo os usos acima que sobreviveram podem ter escopo mais estreito do que o
      nome da cultura sugere. O que o rotulo escreve:
      <ul style="margin:5px 0 0 16px">${p.exclusion_windows.map(w => `<li>${
        w.QUOTABLE ? `<i>&ldquo;${esc(w.TEXT.length>140?w.TEXT.slice(0,140)+'…':w.TEXT)}&rdquo;</i>`
                   : `<span class="unknown">QUOTE_NOT_RECOVERABLE_COLUMN_LAYOUT</span>
                      <span class="meta">marcador <code>${esc(w.MARKER)}</code> encontrado, mas o
                      trecho ate o corte atravessa salto de coluna do extrator de texto: a frase
                      montada nao existe no documento, entao nao e citada</span>`}</li>`).join('')}</ul>
      A ferramenta <b>nao</b> modela escopo negativo dentro de um uso: ela avisa que ele existe.
      Janelas de compatibilidade de calda e de numero de tratamentos <b>nao</b> aparecem aqui —
      elas nao falam de cultura, e apresenta-las como escopo de cultura foi um erro da versao
      anterior.</div>` : ''}
  </div>

  <div class="block">
    <div style="display:flex;justify-content:space-between;align-items:baseline">
      <h3>Dose</h3><span class="meta">estado do leitor: <code>${esc(p.dose_state)}</code></span></div>
    ${(p.ceilings||[]).length ? `<div class="lei"><b>Esta etichetta poe teto de dose por cultura
      FORA da tabela</b>, e a nota tem o mesmo valor legal que a tabela:
      <ul style="margin:5px 0 0 16px">${p.ceilings.map(t=>`<li><i>&ldquo;${esc(t.LITERAL)}&rdquo;</i></li>`).join('')}</ul>
      A ferramenta mostra os dois numeros do documento e <b>nao calcula um terceiro</b>.</div>`
      : p.label_dose_notes_not_read ? `<div class="lei"><span class="unknown">LABEL_NOTES_NOT_READ</span>
      este rotulo tem restricao escrita <b>fora da tabela</b> que este leitor nao estrutura.
      <b>Isto nao autoriza dizer que a dose da tabela e o limite</b>, e nao autoriza ler o
      <code>NOT_PRESENT</code> da coluna MAX. APLICACOES como &ldquo;o rotulo nao poe limite&rdquo;:
      <code>NOT_PRESENT</code> descreve a CELULA da tabela, provada vazia; o que esta fora dela
      e <code>NOT_READ</code>. O que o documento escreve, literal:
      ${(p.label_app_limit_notes||[]).length ? `<ul style="margin:5px 0 0 16px">${
        p.label_app_limit_notes.map(n=>`<li><i>&ldquo;${esc(n.TEXT)}&rdquo;</i>
          <span class="meta">marcador <code>${esc(n.MARKER)}</code></span></li>`).join('')}</ul>
        <div class="meta">A citacao para no salto de coluna do extrator de texto: e o pedaco da
        frase que existe no documento, nao uma frase remontada.</div>`
        : `<div class="meta"><span class="unknown">QUOTE_NOT_RECOVERABLE</span> o marcador foi
           encontrado e o trecho nao pode ser citado sem emendar colunas</div>`}</div>` : ''}
    ${p.doses.length ? `<div class="tw"><table>
      <thead><tr><th>Cultura</th><th>Alvo</th><th>Dose/ha</th><th>Max</th><th>Intervalo</th><th>Fios</th><th></th></tr></thead>
      <tbody>${p.doses.map((d,i) => `<tr${d.crop_check==='CROP_ASSIGNMENT_CONTRADICTED_BY_RULE'?' style="opacity:.75"':''}>
        <td>${fragmento(d.crop)}${d.crop_check==='CROP_ASSIGNMENT_CONTRADICTED_BY_RULE'
          ? `<div class="meta"><span class="unknown">CROP_ASSIGNMENT_CONTRADICTED_BY_RULE</span>
             um fio desenhado da tabela separa esta linha de toda ocorrencia desta cultura na
             coluna de cultura: a linha <b>nao e desta cultura</b> (<code>R-11</code>)</div>` : ''}</td>
        <td>${fragmento(d.target)}${avisoAlvoLiteral(d)}</td>
        <td>${d.crop_check==='CROP_ASSIGNMENT_CONTRADICTED_BY_RULE'
              ? val('NOT_PROVED_BY_RULE')
              : d.rule_check==='NOT_LOCATED' ? val('NOT_VALIDATED')
              : d.rule_check==='PLAUSIBILITY_REJECTED'
              ? `${val('NOT_PROVED_BY_RULE')}<div class="meta">o filtro de plausibilidade
                 (<code>P-*</code>) recusou esta tabela: o extrator achou grade onde nao havia.
                 <b>Publicar o numero dela seria desdizer o proprio filtro.</b></div>`
              : isUnk(d.dose_ha)?val(d.dose_ha):esc(d.dose_ha+' '+d.unit_ha)}</td>
        <td>${colunaMax(d)}</td><td>${colunaIntervalo(d)}</td>
        <td>${seloFios(d)}</td>
        <td><button class="ev" onclick="evDose('${p.reg}',${i})">prova</button></td>
      </tr>`).join('')}</tbody></table></div>`
      : (p.states && p.states.LABEL_DOWNLOADED === false
         ? `<div class="lei">Nenhum rotulo foi baixado para este produto, entao o leitor de dose
            <b>nao rodou</b>: <span class="unknown">NOT_COLLECTED</span>. A explicacao sobre
            herbicidas em prosa nao se aplica aqui — ela e sobre documentos que foram abertos, e
            este nao foi.</div>`
         : `<div class="lei">Dose nao estruturada para este produto
            (<code>${esc(p.dose_state)}</code>). A maioria dos herbicidas italianos declara dose em
            <b>prosa</b>, nao em tabela, e este leitor le tabela.
            <b>Isto nao significa produto sem dose.</b></div>`)}
  </div>

  <div class="block">
    <h3>Tempo de carencia (PHI)</h3>
    <div class="lei">Nao publicado nesta versao. O extrator de carencia esta marcado
      <code>PROTOTYPE_NOT_SHIPPED</code>: 2 de 15 rotulos, com a primeira linha de cada bloco
      contaminada pela coluna vizinha. <b>As etichette trazem carencia; nos e que nao lemos.</b>
      <code>PHI_PROVED = 0</code> por decisao.</div>
  </div>

  <div class="block">
    <h3>Eventos deste produto (${objs.length})</h3>
    ${objs.length ? objs.map(cardObj).join('')
      : '<div class="meta">nenhum evento registrado na janela observada. <code>NO_CHANGE_OBSERVED_IN_WINDOW</code> nao e o mesmo que &ldquo;nunca mudou&rdquo;.</div>'}
  </div>`;
}
window.viewProduto = viewProduto;

// ---------------------------------------------------------------- 3 · TIMELINE
function viewTimeline() {
  const v = P.versions;
  const porData = {};
  P.objects.filter(o => o.PROOF_STATE === 'PROVED' && o.OBSERVATION_WINDOW)
    .forEach(o => (porData[o.OBSERVATION_WINDOW] = porData[o.OBSERVATION_WINDOW]||[]).push(o));
  $('#v-timeline').innerHTML = `
  <div class="lei">Tres coisas diferentes, que a ferramenta nunca funde:
    <b>DOCUMENT_DIFF</b> (o arquivo mudou de sha256) &middot;
    <b>SEMANTIC_DIFF</b> (um campo mudou de valor apos normalizacao) &middot;
    <b>REGULATORY_CHANGE_EVENT</b> (o campo que mudou tem significado regulatorio por regra R-*).
    Um documento novo nao e uma mudanca; um campo diferente nao e automaticamente regulatorio.</div>
  <div class="cards">
    <div class="kpi"><b>${P.history.snapshots}</b><span>instantaneos oficiais baixados</span></div>
    <div class="kpi"><b>${P.history.distinct}</b><span>documentos distintos por sha256</span></div>
    <div class="kpi"><b style="color:var(--dim)">${P.history.snapshots - P.history.distinct}</b><span>republicados sem mudar (nao contam como versao)</span></div>
    <div class="kpi"><b>${P.history.raw_field_diffs}</b><span>DOCUMENT/campo bruto</span></div>
    <div class="kpi"><b>${P.history.normalised_field_diffs}</b><span>SEMANTIC_DIFF apos normalizar</span></div>
    <div class="kpi"><b style="color:var(--ok)">${P.history.true_changes}</b><span>REGULATORY_CHANGE_EVENT</span></div>
  </div>
  <h2>Versoes arquivadas do registro oficial</h2>
  <div class="tw"><table>
    <thead><tr><th>Data</th><th>Versao (sha256)</th><th>Bytes</th><th>ADAMA ativos</th>
      <th>Republicado identico em</th><th>Eventos ate a versao seguinte</th><th></th></tr></thead>
    <tbody>${v.map((x,i) => {
      const jan = i < v.length-1 ? `${x.date}..${v[i+1].date}` : null;
      const evs = jan ? (porData[jan]||[]) : [];
      return `<tr>
        <td class="mono">${esc(x.date)}</td>
        <td class="mono">${esc(x.id)}</td>
        <td>${x.bytes.toLocaleString('pt-BR')}</td>
        <td>${x.adama_active}</td>
        <td class="meta">${x.republished.length ? x.republished.join(', ')
          : '<span class="meta">nenhum</span>'}</td>
        <td>${jan===null ? val('NOT_APPLICABLE')+'<div class="meta">ainda nao existe versao seguinte</div>'
              : evs.length ? `<b style="color:var(--ok)">${evs.length}</b>`
              : '<span class="meta">nenhum</span>'}</td>
        <td>${link(x.url,'CSV')}</td></tr>`;}).join('')}
    </tbody></table></div>`;
}

// A celula de dose NUNCA imprime um numero sem dizer por que aquele numero e
// deste par. Estado ambiguo nao vira numero.
// Estados que a FONTE declara fora de vigor. Medidos no instantaneo vigente
// sobre os 17.695 produtos do registro: Revocato 13.216, Scaduto 765, Sospeso 3.
// Mesma lista da regra T-08 em REGRAS.md.
const FORA_DE_VIGOR = ['revocato', 'scaduto', 'sospeso'];
const foraDeVigor = p => FORA_DE_VIGOR.includes(String(p && p.status || '').trim().toLowerCase());
// O CONFLITO existe quando a validade passou E o registro CONTINUA declarando o
// produto em vigor. Se o estado ja e Scaduto, os dois campos concordam e nao ha
// conflito nenhum. A tela afirmava conflito sobre EVOLUTION EC e CS, cujo
// stato_amministrativo e "Scaduto": inventava desacordo entre campos que dizem
// a mesma coisa.
const conflitoDeValidade = p => {
  const d = dte(p);
  return typeof d === 'number' && d < 0 && !foraDeVigor(p);
};

// ZERO MEDIDO, NAO SEI, E NAO COLETADO SAO TRES COISAS. A BUSCA mostrava
// "USOS: NOT_KNOWN" para TOPIK 240 EC 008929, cujo rotulo FOI lido
// (LABEL_READ=true, 8.537 caracteres extraidos, sha conferido em disco) e cujo
// leitor de uso devolveu zero pares: a ferramenta MEDIU zero e disse que nao
// sabia. E a ficha de um produto sem PDF nenhum mostrava "0 pares", que afirma
// uma medicao que nunca houve. As duas conversoes estavam trocadas entre si.
function contagem(p, campo, estadoLeitura) {
  const st = p.states || {};
  if (st.LABEL_DOWNLOADED === false)
    return `<span class="unknown" title="nenhum rotulo foi baixado: nada foi medido">NOT_COLLECTED</span>`;
  const n = (p[campo] || []).length;
  if (n) return String(n);
  if (st[estadoLeitura]) return `<b>0</b><div class="meta">o leitor rodou neste documento e
    estruturou zero. Isto e medicao, nao ignorancia</div>`;
  return val('NOT_KNOWN');
}

// Nomes de estado sao impressos POR EXTENSO. Um selo de tres letras nao e um
// estado: quem le tem de poder ver, sem abrir gaveta, o que a ferramenta esta
// afirmando sobre a origem daquele numero.
const SELO = {
  EXACT_MATCH: ['p-ok', 'EXATA'],
  LISTED_IN_DOSE_ROW: ['p-warn', 'LISTADA'],
  LISTED_IN_DOSE_ROW_AGREEING: ['p-warn', 'LISTADA'],
  LISTED_IN_DOSE_ROW_WITH_UNREAD_DUPLICATE: ['p-warn', 'LISTADA'],
};
function celulaDose(l) {
  const j = l.j;
  const desc = j.descartadas
    ? `<div class="meta">${j.descartadas} linha(s) de dose deste rotulo foram descartadas antes da
       juncao: a cultura delas nao sobrevive aos fios desenhados (<code>R-11</code>) ou o valor
       nao pode ser conferido no documento.</div>` : '';
  if (j.estado === 'AMBIGUOUS_DOSE_FOR_THIS_PAIR')
    return `<span class="unknown">AMBIGUOUS_DOSE_FOR_THIS_PAIR</span>
      <span class="pill p-bad">AMBIGUA</span>
      <div class="meta">${j.cand.length} linhas de dose com valor lido servem para este par e
        <b>discordam</b>${j.mudos?` (mais ${j.mudos} sem valor lido, que nao contam como discordancia)`:''}</div>
      <button class="ev" onclick="evAmbigua('${l.p.reg}',${JSON.stringify(j.cand.map(x=>l.p.doses.indexOf(x)))})">ver as ${j.cand.length} candidatas</button>${desc}`;
  if (j.estado === 'EXACT_MATCH_QUOTE_LACKS_CROP')
    return `<span class="unknown">EXACT_MATCH_QUOTE_LACKS_CROP</span>
      <div class="meta">cultura e alvo batem letra a letra com uma linha de dose, mas a
      <b>citacao gravada pelo extrator para aquela linha nao contem o nome desta cultura</b>.
      Foi assim que a versao anterior publicou &ldquo;TABACCO x CIMICI = 600 g/ha&rdquo; com selo
      verde: a citacao era &ldquo;Cimici 600 1 Nottue defogliatrici&rdquo;, sem a palavra Tabacco.
      A ferramenta prefere nao responder.</div>${desc}`;
  if (j.estado === 'DOSE_NOT_PROVED_TARGET_NOT_LITERAL')
    return `<span class="unknown">DOSE_NOT_PROVED_TARGET_NOT_LITERAL</span>
      <div class="meta">ha linha de dose para este par, mas o <b>texto do alvo dela nao foi
      encontrado literalmente no rotulo</b>. Pode ser alvo quebrado entre colunas (inofensivo) ou
      <b>fusao de duas linhas da tabela</b>, que existe e esta provada em 008259 e faz a linha
      receber a dose da errada. Sem detector de fusao, um numero cuja linha de origem nao pode ser
      confirmada <b>nao e uma resposta</b>. O valor lido nao foi apagado:</div>
      <button class="ev" onclick="evDose('${l.p.reg}',${l.p.doses.indexOf(j.escondida)})">ver o valor lido e a sua proveniencia</button>${desc}`;
  if (j.estado === 'DOSE_ROW_WITHOUT_READ_VALUE')
    return `<span class="unknown">DOSE_ROW_WITHOUT_READ_VALUE</span>
      <div class="meta">ha linha de dose para este par, mas nenhuma delas teve o valor lido</div>${desc}`;
  if (j.estado === 'CROP_IDENTITY_NOT_PROVED')
    return `<span class="unknown">CROP_IDENTITY_NOT_PROVED</span>
      <div class="meta">esta etichetta escreve <b>${j.formas.length} formas diferentes</b> deste
      mesmo nome de cultura — ${j.formas.map(f=>`<i>&ldquo;${esc(f)}&rdquo;</i>`).join(' &middot; ')} —
      e o vocabulario do leitor de uso colapsa todas em <b>${esc(l.u.crop)}</b>. Sao culturas
      diferentes, com doses diferentes: em LAMDEX EXTRA a beterraba <i>da zucchero</i> tem teto de
      800 g/ha e a linha de <i>Foraggere</i> chega a 1200. <b>A ferramenta nao escolhe qual delas e
      esta.</b></div>${desc}`;
  if (j.estado === 'DOSE_ROW_NOT_LOCATED_FOR_THIS_PAIR')
    return `<span class="unknown">DOSE_ROW_NOT_LOCATED_FOR_THIS_PAIR</span>
      <div class="meta">ha linha de dose para este par e ela caiu — mas caiu porque o
      <b>localizador nao encontrou o valor no documento</b> (<code>NOT_LOCATED</code>), e nao
      porque alguma regra tenha provado que a linha e de outra cultura. R-11 nao disse nada
      contra este par</div>${desc}`;
  if (j.estado === 'DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE_FOR_THIS_PAIR')
    return `<span class="unknown">DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE_FOR_THIS_PAIR</span>
      <div class="meta">ha linha de dose para este par e ela caiu porque a banda de onde foi
      lida tem um <b>fio horizontal desenhado por dentro</b>: sao duas linhas coladas e o
      numero pode ser da de baixo (<code>R-22</code>)</div>${desc}`;
  if (j.estado === 'DOSE_ROW_REJECTED_BY_PLAUSIBILITY_FOR_THIS_PAIR')
    return `<span class="unknown">DOSE_ROW_REJECTED_BY_PLAUSIBILITY_FOR_THIS_PAIR</span>
      <div class="meta">ha linha de dose para este par e ela caiu no <b>teste de
      plausibilidade da tabela</b> (R-10b): o que o extrator leu como tabela nao se comporta
      como uma</div>${desc}`;
  if (j.estado === 'DOSE_ROW_CONTRADICTED_BY_R11_FOR_THIS_PAIR')
    return `<span class="unknown">DOSE_ROW_CONTRADICTED_BY_R11_FOR_THIS_PAIR</span>
      <div class="meta"><b>Havia</b> ${j.caidas.length} linha(s) de dose para este par, e ela(s)
      <b>caiu(ram) na conferencia pelos fios</b>: a cultura delas nao sobrevive ao documento
      (<code>R-11</code>). Isto nao e &ldquo;leitura que nao ligou&rdquo; — e leitura que ligou na
      linha errada e foi reprovada.</div>${desc}`;
  if (!j.d)
    return `<span class="unknown">NO_DOSE_ROW_FOR_THIS_PAIR</span>
      <div class="meta">nenhuma linha de dose utilizavel serve para este par. <b>Nao e dose zero e
      nao e dose ausente no rotulo</b>: e leitura que nao ligou</div>${desc}`;
  if (isUnk(j.d.dose_ha)) return val(j.d.dose_ha) + desc;

  let [cls, rot] = SELO[j.estado] || ['p-unk', j.estado];
  if (j.d.target_literal === 'TARGET_TEXT_NOT_FOUND_LITERALLY') { cls = 'p-unk'; rot += ' · ALVO NAO LITERAL'; }
  else if (j.d.target_literal === 'TARGET_TEXT_NOT_CHECKED') { cls = 'p-unk'; rot += ' · ALVO NAO CONFERIDO'; }
  // A celula de cultura do rotulo as vezes carrega o ESCOPO junto:
  // "Pomodoro Melanzana (uso in serra)". A juncao por token descarta o
  // parentese e a tela mostrava POMODORO sem dizer que a autorizacao e so em
  // estufa. O escopo volta, literal.
  const escopo = /\((?:uso\s+)?in\s+serra|serra\)|pieno\s+campo|sotto\s+tunnel|in\s+vivai/i
    .test(String(j.d.crop || '')) ? `<div class="meta"><b>A celula de cultura do rotulo traz
    escopo:</b> <i>&ldquo;${esc(j.d.crop)}&rdquo;</i>. A autorizacao vale nesse escopo, e o nome
    curto da cultura na coluna ao lado nao o carrega.</div>` : '';
  // R-13 · o texto do alvo desta linha existe literalmente no rotulo? NAO
  // rebaixa nada: o teste nao sabe separar alvo quebrado em coluna de alvo
  // FUNDIDO (a fusao existe e esta provada em 008259), e rebaixar 180 linhas
  // por um teste que nao distingue os dois casos apagaria uso verdadeiro.
  const literal = j.d.target_literal === 'TARGET_TEXT_NOT_CHECKED'
    ? `<div class="meta"><span class="unknown">TARGET_TEXT_NOT_CHECKED</span>
       esta linha nao foi submetida a <code>R-13</code>: o texto do alvo nao foi procurado no
       documento. Nao conferido nao e conferido — sao 43 linhas do acervo, e ate agora elas
       passavam como se fossem aprovacao.</div>`
    : j.d.target_literal === 'TARGET_TEXT_NOT_FOUND_LITERALLY'
    ? `<div class="meta"><span class="unknown">TARGET_TEXT_NOT_FOUND_LITERALLY</span>
       o texto deste alvo nao foi encontrado literalmente no rotulo. Pode ser alvo quebrado entre
       colunas (comum, inofensivo) ou <b>fusao de duas linhas da tabela</b> (existe: em 008259 o
       alvo &ldquo;Nottue defogliatrici (allo scoperto) tentredine&rdquo; junta duas linhas e
       recebe a dose da errada). <b>Esta ferramenta nao sabe separar os dois casos</b>, entao nao
       rebaixa a linha e avisa.</div>` : '';
  const nota = j.estado === 'EXACT_MATCH' ? ''
    : `<div class="meta">a linha de dose fala de ${citavel(j.d.crop_cell_state)
        ? `&ldquo;${esc(j.d.crop)}&rdquo;` : `<span class="unknown">CELL_TEXT_NOT_RECOVERABLE</span>`}
        &middot; ${citavel(j.d.target_cell_state)
        ? `&ldquo;${esc(j.d.target)}&rdquo;` : `<span class="unknown">CELL_TEXT_NOT_RECOVERABLE</span>`}${j.cand.length>1?` (${j.cand.length} linhas, mesmo valor)`:''}${j.mudos?`; mais ${j.mudos} duplicata(s) sem valor lido`:''}.
        Juncao inferida (<code>${esc(j.estado)}</code>), nao leitura deste par.</div>`;
  // R-12 · o teto por cultura escrito FORA da tabela tem o mesmo valor legal
  // que a tabela. Se a dose exibida passa dele, os dois numeros aparecem juntos
  // e a ferramenta nao escolhe nem calcula um terceiro.
  const excede = excedeTeto(j.d, j.teto);
  const avisoTeto = j.teto ? `<div class="meta" style="${excede?'color:var(--bad)':''}">
      ${excede?'<b>A propria etichetta poe um teto MENOR para esta cultura, fora da tabela:</b>'
              :'teto declarado pela etichetta para esta cultura:'}
      <i>&ldquo;${esc(j.teto.LITERAL)}&rdquo;</i>${excede?` — a tabela diz ate
      <b>${esc(j.d.dose_ha)} ${esc(j.d.unit_ha)}</b> e a nota diz no maximo
      <b>${esc(j.teto.VALOR)} ${esc(j.teto.UNIDADE)}</b>. Sao duas frases do MESMO documento
      oficial; a ferramenta mostra as duas e <b>nao calcula um terceiro numero</b>.`:''}</div>` : '';
  const notaNaoLida = (l.p.label_dose_notes_not_read && !j.teto)
    ? `<div class="meta"><span class="unknown">LABEL_NOTES_NOT_READ</span> este rotulo tem
       restricao de dose escrita fora da tabela que este leitor nao le. Nao afirmamos que a dose
       acima e o limite.</div>` : '';
  return `${esc(j.d.dose_ha + ' ' + j.d.unit_ha)}
    <span class="pill ${cls}" title="${esc(j.estado)}">${esc(rot)}</span>
    ${excede?'<span class="pill p-bad">ACIMA DO TETO DO ROTULO</span>':''}
    <button class="ev" onclick="evDose('${l.p.reg}',${l.p.doses.indexOf(j.d)})">prova da dose</button>
    ${nota}${escopo}${literal}${avisoTeto}${notaNaoLida}${desc}`;
}
function evAmbigua(reg, idx) {
  const p = byReg[reg];
  const rows = idx.map(i => p.doses[i]);
  drawer(`<h3>Dose ambigua</h3>
    <div class="meta">${esc(p.name)} &middot; <code>${esc(p.reg)}</code></div>
    <div class="lei"><b>A ferramenta nao escolhe.</b> ${rows.length} linhas de dose deste rotulo
      <b>com valor lido</b> servem para este par de cultura e alvo, e elas <b>nao dizem o mesmo
      valor</b>. Escolher uma seria inventar. O que existe e isto:
      <div class="meta" style="margin-top:5px">Linha sem valor lido nao entra nesta conta: ela nao
      discorda de nada. A versao anterior contava <code>NOT_PRESENT</code> como se fosse um valor e
      declarava ambiguidade sobre pares em que a etichetta e inequivoca.</div></div>
    <div class="tw"><table>
      <thead><tr><th>Celula de cultura lida</th><th>Celula de alvo lida</th><th>Dose/ha</th>
        <th>Pagina</th><th>Fio da tabela</th><th>Max</th><th>Intervalo</th><th></th></tr></thead>
      <tbody>${rows.map((r,k) => `<tr>
        <td>${esc(r.crop)}</td><td>${esc(r.target)}</td>
        <td><b>${isUnk(r.dose_ha)?val(r.dose_ha):esc(r.dose_ha+' '+r.unit_ha)}</b></td>
        <td>${val(r.page)}</td><td>${val(r.rule_check)}</td>
        <td>${colunaMax(r)}</td><td>${colunaIntervalo(r)}</td>
        <td><button class="ev" onclick="evDose('${esc(reg)}',${idx[k]})">prova</button></td>
      </tr>`).join('')}</tbody></table></div>
    <div class="meta" style="margin-top:8px">Quem resolve isto e uma pessoa lendo a etichetta.
      Este e o pedido de revisao, nao uma resposta.</div>`);
}
window.evAmbigua = evAmbigua;

// ---------------------------------------------------------------- 4 · CROP x TARGET
// MF-08 · O VOCABULARIO DE USO E UMA LISTA FECHADA, E ISSO NAO ESTAVA DITO.
//
// #cq=porro respondia "0 pares em 0 produtos." com a tabela vazia e a legenda
// zerada, sem NENHUM token de ignorancia — na tela de ROTEAMENTO, que e onde um
// Regulatory pergunta "o que a ADAMA tem registrado para PORRO na Italia?".
// Contra-prova dentro do proprio payload: ha 17 linhas de dose com cultura
// "Porro" em 5 registros, uma delas CONFIRMED_BY_RULE, e a etichetta 008259
// autoriza Porro em quatro linhas. O leitor de uso tem um vocabulario fechado de
// nomes e PORRO nao esta nele.
//
//     "Ausencia de evidencia nao e evidencia de ausencia; falha de parser/coleta
//      NAO e zero."
const VOCAB_USO = [...new Set(P.products.flatMap(p => (p.uses||[]).map(u => u.crop)))].sort();
function linhasDeDoseComCultura(termo) {
  const t = nrm(termo), out = [];
  if (t.length < 3) return out;
  P.products.forEach(p => (p.doses||[]).forEach((d,i) => {
    if (itensDaCelula(d.crop).some(it => it === t || it.startsWith(t + ' ') || it.endsWith(' ' + t)))
      out.push({p, d, i});
  }));
  return out;
}
// MF-09 · A FERRAMENTA CALCULAVA A IGNORANCIA E A ESCONDIA ONDE ELA E CONSUMIDA.
//
// `exclusion_check` era desenhado na ficha PRODUTO 360 e NAO nesta tela: medido,
// a palavra PREFIX nao ocorria uma vez no texto da tela de cultura. Os 5 pares
// ZUCCHINO x INFESTANTI cuja propria coleta ja media que a palavra nao esta no
// rotulo ("zucchin" ocorre ZERO vezes em 009005; o que existe e "Zucca") eram
// desenhados identicos a um par atestado. A ressalva existir noutra tela nao
// salva: quem consulta por cultura nunca a ve.
//
// E o mesmo vale para o veredito de R-14: um par que o teste de fio NAO
// conseguiu conferir nao pode usar o mesmo selo de um que passou.
const PAR_ROTULO = {
  PAIR_CONSISTENT_WITH_RULES: ['p-ok', 'TABELA · FIO CONFERIDO',
    'o nome da cultura e um glifo do alvo estao na MESMA celula desenhada da tabela (R-14)'],
  PAIR_NOT_CHECKABLE_ROUTE_NOT_GEOMETRIC: ['p-dim', 'TEXTO · SEM TESTE DE FIO',
    'par lido de prosa, nao de tabela: nao ha geometria a conferir. NOT_CHECKED, nao aprovado'],
  PAIR_NOT_CHECKABLE_NO_DRAWN_CELL: ['p-unk', 'TABELA · SEM CELULA DESENHADA',
    'a coluna da cultura nesta pagina nao tem grade desenhada: onde nao ha fio, mescla e inferencia'],
  // SEM GRADE e GRADE QUE NAO DESCREVE O TEXTO sao duas ignorancias diferentes,
  // e ate a rodada 4 as duas saiam com o nome da primeira. Medido: em 58 dos
  // 170 casos havia grade — em 008259 a coluna de "Pesco" e atravessada por 15
  // e 17 fios — e a tela dizia que nao havia. Token de ignorancia que descreve
  // errado o documento e pior que ausencia de token, porque parece medicao.
  // E o terceiro jeito de nao haver celula: os riscos que atravessam a coluna
  // tem as DUAS pontas da linha de texto acima deles. Isso e sublinhado de
  // titulo, nao regua de tabela. Medido em 016312 TOMIGAN, onde quatro
  // sublinhados fabricavam uma celula de 67 pt sobre SEIS linhas de DOIS blocos
  // e davam selo verde a MANDORLO x INFESTANTI e NOCE x INFESTANTI.
  PAIR_NOT_CHECKABLE_RULES_ARE_TEXT_UNDERLINES: ['p-unk', 'TABELA · OS RISCOS SAO SUBLINHADO',
    'os riscos que atravessam a coluna tem as duas pontas da linha de texto acima deles: sao sublinhado de titulo, e sublinhado nao fecha celula'],
  PAIR_NOT_CHECKABLE_TABLE_NOT_DESCRIBING_ITS_TEXT: ['p-unk', 'TABELA · GRADE NAO DESCREVE O TEXTO',
    'a grade existe e foi lida, mas alguma linha que comeca dentro dela termina fora: o que parecia celula e risco de titulo, e o teste nao se aplica'],
  PAIR_NOT_CHECKABLE_ANCHOR_NOT_FOUND: ['p-unk', 'TABELA · ALVO NAO LOCALIZADO',
    'o nome deste alvo nao ocorre na pagina, entao nao ha o que localizar na celula'],
  PAIR_NOT_CHECKABLE_CROP_ALSO_OUTSIDE_TABLE: ['p-unk', 'TABELA · EVIDENCIA MISTA',
    'parte das ocorrencias do nome da cultura esta dentro de celula desenhada e parte nao: o teste nao alcanca todas. So fica assim quando algum glifo do alvo NAO mora na celula de outra cultura — se todos moram, o alvo tem dono e o par e condenado'],
  PAIR_NOT_CHECKABLE_CROP_NAME_NOT_THE_ANCHOR: ['p-unk', 'TABELA · CELULA FECHOU PELO TITULO',
    'a celula desenhada casou pelo TITULO do grupo ("ORTICOLE (...)", "Grano tenero e duro") e nao pelo nome da cultura publicada: a geometria provou que o titulo e o alvo dividem uma celula, nao que a cultura esta no grupo'],
  PAIR_NOT_CHECKABLE_TARGET_UNDER_CROP_HEADER: ['p-unk', 'TABELA · CABECALHO DE BLOCO',
    'o alvo esta abaixo da cultura e na mesma coluna: o desenho e titulo-em-cima, e o teste de coluna nao se aplica'],
};
// PRODUCT_FOR_CROP E PRODUCT_FOR_TARGET SAO DUAS PERGUNTAS.
//
// "este produto e autorizado nesta CULTURA" e "este produto e autorizado para
// este ALVO nesta cultura" nao sao a mesma afirmacao, e a tela colapsava as
// duas num selo so. Agora cada par carrega os dois eixos e eles nunca se
// juntam:
//
//   proof        o par sobreviveu a um teste contra o documento? So a camada
//                de TABELA tem teste (R-14). A de prosa nao tem nenhum — tres
//                instrumentos foram medidos e os tres falharam (ver
//                v1/inteligencia/prosa_escopo.py);
//   target_name  o NOME do alvo esta escrito no rotulo, ou veio de uma
//                taxonomia que esta ferramenta nao tem? Medido: 256 pares
//                publicam um nome que o documento nao escreve;
//   crop_name    e o NOME DA CULTURA (R-21), que e a mesma pergunta do lado
//                mais caro. Medido: 21 pares publicados trazem uma cultura
//                cuja raiz nao existe em palavra nenhuma do documento.
//
// FATO = as TRES colunas fecham. Medido: 1.264 dos 2.875 pares publicados.
function nomeDoAlvo(u) {
  if (u.target_name !== 'TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL') return '';
  return `<div class="meta"><span class="unknown">TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL</span>
    <b>este nome nao esta escrito no rotulo.</b> O documento nomeia a praga pelo binomio
    (&ldquo;Cydia pomonella&rdquo;) e a ferramenta publica o nome comum
    (&ldquo;CARPOCAPSA&rdquo;). A equivalencia e entomologica e provavelmente certa —
    e <b>nao esta neste repositorio e nao volta ao documento</b>, entao viaja como
    inferencia e nao como leitura</div>`;
}
// R-21, o lado da CULTURA. Em 018270 e irmaos a etichetta escreve FAGIOLINO e a
// ferramenta publica FAGIOLO; em 009005 e irmaos escreve "zucca" e a ferramenta
// publica ZUCCHINO; em 015232 e irmaos escreve "Grano tenero e duro" e a
// ferramenta publica FRUMENTO. Sao 21 pares na tela.
//
// O caso extremo NAO esta entre esses 21, e vale dizer por que: em 002983 e
// 013405 a etichetta escreve "Pomodoro (ad esclusione di Pomodoro ciliegino)"
// — "ciliegino" e o TOMATE CEREJA, dentro de uma EXCLUSAO — e a lista de pares
// traz CILIEGIO, a arvore. Esses dois nao chegam aqui porque R-10 ja os retira
// como CROP_ONLY_INSIDE_EXCLUSION. Duas regras independentes acusaram o mesmo
// defeito por caminhos diferentes, e e assim que se sabe que ele e real.
function nomeDaCultura(u) {
  if (u.crop_name !== 'CROP_NAME_NOT_IN_LABEL') return '';
  return `<div class="meta"><span class="unknown">CROP_NAME_NOT_IN_LABEL</span>
    <b>o nome desta cultura nao esta escrito no rotulo</b>, e nao e flexao de nada que o
    documento escreve — o extrator leu ${citavel(u.crop_raw_state)
      ? `<i>&ldquo;${esc(String(u.crop_raw || 'NOT_PRESERVED').slice(0, 90))}&rdquo;</i>`
      : `<code>${esc(String(u.crop_raw || 'NOT_PRESERVED').slice(0, 90))}</code>
         <span class="unknown">${esc(u.crop_raw_state || 'QUOTE_NOT_CHECKED')}</span>`}.
    Passar dessa palavra para <b>${esc(u.crop)}</b> e uma <b>equivalencia de cultura</b>, e
    equivalencia de cultura precisa de prova documental ou taxonomica: semelhanca de escrita
    nao e prova</div>`;
}
// O nome normalizado joga fora o escopo que a etichetta escreve. Medido: 387
// pares publicados trazem um qualificador ("VITE da vino", "Melone (uso in
// serra)", "Barbabietola da zucchero") que o nome curto perde. Um produto
// autorizado so em uva de VINHO aparecia sob o mesmo "VITE" de um autorizado
// tambem em uva de MESA.
function escopoDaCultura(u) {
  if (!u.crop_scope || !u.crop_scope.length) return '';
  // O QUALIFICADOR E FATO; A FRASE EM VOLTA DELE PODE NAO SER. Os termos de
  // escopo sao casados por regex no texto do extrator, e isso continua valendo
  // — mas a frase inteira so vai entre aspas se R-18 disser que ela existe
  // assim no documento. Medido: 1.408 das 2.873 celulas de cultura nao sao
  // literais, a maioria cortada no meio de uma palavra pelo extrator.
  const frase = citavel(u.crop_raw_state)
    ? `<i>&ldquo;${esc(String(u.crop_raw).slice(0, 80))}&rdquo;</i>`
    : `<code>${esc(String(u.crop_raw).slice(0, 80))}</code>
       <span class="unknown">${esc(u.crop_raw_state || 'QUOTE_NOT_CHECKED')}</span>`;
  return `<div class="meta"><b>a etichetta qualifica esta cultura:</b>
    ${u.crop_scope.map(e => `<code>${esc(e)}</code>`).join(' &middot; ')} — ${frase}.
    O nome curto <b>${esc(u.crop)}</b> nao carrega esse escopo</div>`;
}
// R-17 · O MESMO PROBLEMA DO LADO DO ALVO, e a mesma resposta: mostrar.
// Medido: em 756 pares o nome publicado do alvo NUNCA aparece sozinho na celula
// como escrita. Em 85 deles a etichetta escreve "mosca bianca" — a mosca-branca
// — e a tela publicava MOSCA, que em italiano e outro inseto. Em outros 273 o
// qualificador e "sensibili", que nao muda praga nenhuma. Separar os dois casos
// exige entomologia que esta ferramenta nao tem, entao ela nao acusa e nao
// retira: poe a palavra do documento ao lado do nome curto.
function escopoDoAlvo(u) {
  if (!u.target_scope || !u.target_scope.length) return '';
  return `<div class="meta"><b>a etichetta nunca escreve este alvo sozinho:</b> sempre
    <code>${esc(u.target)} ${u.target_scope.map(e => esc(e)).join('/')}</code>.
    O nome curto <b>${esc(u.target)}</b> perde essa palavra — e ela pode ser so um adjetivo
    (&ldquo;sensibili&rdquo;), o nome da especie (&ldquo;lineatella&rdquo;) ou outro inseto
    (&ldquo;bianca&rdquo;). <span class="unknown">TARGET_NAME_ALWAYS_QUALIFIED</span></div>`;
}
function evidenciaDoPar(u) {
  const [cls, rot, tit] = PAR_ROTULO[u.pair_check]
    || [u.evidence === 'TABLE_GEOMETRY' ? 'p-ok' : 'p-dim',
        u.evidence === 'TABLE_GEOMETRY' ? 'TABELA' : 'TEXTO', ''];
  const ex = u.exclusion_check;
  const ressalva = (!ex || ex === 'ATTESTED_OUTSIDE_EXCLUSION') ? '' :
    `<div class="meta"><span class="unknown">${esc(ex)}</span>
     ${ex === 'CROP_NAME_NOT_FOUND_IN_LABEL_TEXT'
       ? 'o nome desta cultura nao aparece no texto do rotulo, nem dentro nem fora de janela de exclusao. Diferenca de vocabulario, e nao conferido por este teste'
       : ex === 'CROP_NAME_PREFIX_MATCH_ONLY'
       ? 'o apoio textual e so por prefixo, nao por palavra inteira (ZUCCHINO apoiado por "zucca" ou "zucchero"): basta para nao retirar o uso, nao basta para chamar de atestado'
       : 'estado de conferencia declarado pela coleta'}</div>`;
  const fato = u.fact
    ? `<span class="pill p-ok" title="o par sobreviveu ao teste contra o documento E os dois nomes, cultura e alvo, estao escritos no rotulo">FATO</span> `
    : `<span class="unknown" title="uma das tres colunas nao fecha: o par nao foi verificado por regra nenhuma, ou o nome do alvo nao esta no rotulo, ou o nome da cultura nao esta no rotulo">NAO_VERIFICADO</span> `;
  return `${fato}<span class="pill ${cls}" title="${esc(tit || u.pair_check || '')}">${rot}</span>${ressalva}${nomeDoAlvo(u)}${escopoDoAlvo(u)}${nomeDaCultura(u)}`;
}

// Casamento de termo de busca por TOKEN INTEIRO. Um termo com menos de 3
// letras cai para substring, porque prefixo curto e o que a pessoa digitou ate
// agora e nao uma afirmacao sobre a cultura.
function casaTermo(campo, termo) {
  const t = nrm(termo);
  if (!t) return true;
  if (t.length < 3) return String(campo).toLowerCase().includes(termo);
  return tokens(campo).has(t) || nrm(campo) === t;
}
function viewCrop() {
  const q = ($('#cq')?.value || '').trim().toLowerCase();
  const qt = ($('#ct')?.value || '').trim().toLowerCase();
  const linhas = [];
  P.products.forEach(p => {
    p.uses.forEach((u,i) => {
      // SF-06 · o filtro casava por SUBSTRING e o comentario de contido(),
      // tres funcoes acima, PROIBE exatamente isso: #cq=melo devolvia
      // "180 pares" = MELO(102) + MELONE(78), e #cq=pero, "167" = PERO(111) +
      // PEPERONE(56). O numero do cabecalho — que e a resposta que vai para o
      // slide — vinha inflado em 76%. Casamento por TOKEN INTEIRO, com o mesmo
      // nrm()/tokens() que o resto da tela ja usa.
      if (q && !casaTermo(u.crop, q)) return;
      if (qt && !casaTermo(u.target, qt)) return;
      const j = juntaDose(p, u);
      linhas.push({p, u, i, d: j.d, j});
    });
  });
  const prods = new Set(linhas.map(l => l.p.reg));
  // O termo casa algum nome do vocabulario fechado de uso?
  const noVocab = q ? VOCAB_USO.some(c => String(c).toLowerCase().includes(q)) : true;
  const forasteiras = (!linhas.length && q && !noVocab) ? linhasDeDoseComCultura(q) : [];
  $('#cres').innerHTML = `
    ${(!linhas.length && q && !noVocab) ? `<div class="lei" style="border-left-color:var(--bad)">
      <span class="unknown">CROP_NOT_IN_USE_VOCABULARY</span>
      <b>&ldquo;${esc(q)}&rdquo; nao existe no vocabulario do leitor de uso</b>, que e uma lista
      FECHADA de ${VOCAB_USO.length} nomes. <b>Isto nao e ausencia de uso autorizado</b> — e o
      leitor nao ter um nome para esta cultura. <code>PARSER_FAILURE != REGULATORY_ABSENCE</code>.
      ${forasteiras.length ? `<div style="margin-top:6px">
        <b>E ha prova do contrario a uma tela de distancia:</b>
        <span class="pill p-bad">CROP_PRESENT_IN_DOSE_TABLE_BUT_NOT_IN_USE_VOCABULARY</span>
        ${forasteiras.length} linha(s) de dose em
        ${new Set(forasteiras.map(f=>f.p.reg)).size} registro(s) trazem esta cultura na celula de
        cultura lida do rotulo:
        <div class="tw" style="margin-top:6px"><table>
          <thead><tr><th>Produto</th><th>Registro</th><th>Celula de cultura lida</th><th>Alvo</th>
            <th>Dose/ha</th><th>Fios</th><th></th></tr></thead>
          <tbody>${forasteiras.slice(0,60).map(f=>`<tr>
            <td><a onclick="go('produto');viewProduto('${f.p.reg}')" style="cursor:pointer">${esc(f.p.name)}</a></td>
            <td class="mono">${esc(f.p.reg)}</td>
            <td>${esc(f.d.crop)}</td><td>${fragmento(f.d.target)}</td>
            <td>${linhaReprovada(f.d)?val('NOT_PROVED_BY_RULE')
                 :isUnk(f.d.dose_ha)?val(f.d.dose_ha):esc(f.d.dose_ha+' '+f.d.unit_ha)}</td>
            <td>${seloFios(f.d)}</td>
            <td><button class="ev" onclick="evDose('${f.p.reg}',${f.i})">prova</button></td>
          </tr>`).join('')}</tbody></table></div>
        <div class="meta" style="margin-top:5px">Estas linhas <b>nao sao pares de uso autorizado</b>:
        sao linhas da tabela de dose, e aparecem aqui so para que a resposta desta tela nao seja
        zero quando o acervo tem material.</div></div>`
        : `<div class="meta" style="margin-top:6px">E nenhuma linha de dose do acervo traz esta
           cultura na celula lida, o que tambem <b>nao</b> prova ausencia: prova que este par de
           leitores nao a nomeia.</div>`}
      <div class="meta" style="margin-top:6px">Os ${VOCAB_USO.length} nomes que o leitor de uso
      emite: <code>${esc(VOCAB_USO.join(', '))}</code></div></div>` : ''}
    ${(() => {
      // A PERGUNTA DE PORTFOLIO, RESPONDIDA SEM COLAPSAR AS DUAS.
      // "Quais produtos ADAMA servem para esta CULTURA e este PROBLEMA?" e a
      // pergunta que o Regulatory faz nesta tela. Ela tem DUAS respostas e
      // ate agora saia uma so, com a cara da forte.
      if (!q && !qt) return '';
      const fatos = linhas.filter(l => l.u.fact);
      const naoV  = linhas.filter(l => !l.u.fact);
      const pf = new Set(fatos.map(l => l.p.reg)), pn = new Set(naoV.map(l => l.p.reg));
      const soNaoV = [...pn].filter(r => !pf.has(r));
      return `<div class="lei" style="border-left-color:${pf.size?'var(--ok)':'var(--bad)'}">
        <b>A resposta desta busca tem duas metades, e elas nao sao a mesma coisa.</b>
        <ul style="margin:6px 0 0 16px">
          <li><span class="pill p-ok">FATO</span> <b>${pf.size}</b> produto(s), em
            <b>${fatos.length}</b> par(es): o par sobreviveu ao teste de fio contra o desenho da
            tabela <b>e</b> o nome do alvo esta escrito no rotulo.
            ${pf.size ? `<span class="meta">${[...pf].map(esc).join(', ')}</span>` : ''}</li>
          <li><span class="unknown">NAO_VERIFICADO</span> <b>${soNaoV.length}</b> produto(s) a
            mais, em <b>${naoV.length}</b> par(es): o rotulo pode autorizar, e
            <b>esta ferramenta nao tem instrumento que prove</b> — a camada de prosa nao tem
            regra nenhuma, e tres foram medidas e falharam. <b>Isto nao e negacao</b>:
            <code>PARSER_FAILURE != REGULATORY_ABSENCE</code>.
            ${soNaoV.length ? `<span class="meta">${soNaoV.map(esc).join(', ')}</span>` : ''}</li>
        </ul>
        <div class="meta" style="margin-top:6px"><b>Autorizado NA CULTURA nao e autorizado PARA O
        ALVO naquela cultura.</b> Um produto pode aparecer aqui por ter a cultura na etichetta sem
        que este alvo especifico esteja provado para ela — e por isso as duas colunas viajam
        separadas em cada linha abaixo.</div></div>`;})()}
    <div class="meta" style="margin:8px 0">${linhas.length} pares em ${prods.size} produtos.</div>
    ${(() => {
      // MF-13 · a legenda dizia "Medido: 5 pares dos N" com o 5 escrito a mao no
      // codigo e o N recalculado a cada filtro. Sob #cq=vite ela anunciava
      // "5 pares dos 99" numa tabela com ZERO selos EXATA. Agora os quatro
      // estados sao contados sobre a lista que esta na tela.
      const c = {};
      linhas.forEach(x => c[x.j.estado] = (c[x.j.estado] || 0) + 1);
      const n = e => c[e] || 0;
      return `<div class="lei"><b>Como a dose e ligada a este par — e quando ela nao e.</b>
      O leitor de uso normaliza a cultura para um nome (<code>MELO</code>); o leitor de dose
      guarda a celula como esta impressa no rotulo (<code>Melo, pero</code>). Sao vocabularios
      diferentes, entao a tela declara o estado de cada juncao.
      <div class="meta" style="margin-top:5px"><b>E o mesmo vale para o ALVO, que ate agora esta
      caixa nao dizia.</b> <code>MOSCA</code> cobre tres pragas distintas no acervo — &ldquo;mosca
      bianca&rdquo; (aleirodideo), &ldquo;Mosca della frutta&rdquo; (<i>Ceratitis</i>) e
      &ldquo;Mosca, cimice verde&rdquo; — e <code>NOTTUE</code> junta &ldquo;Nottue defogliatrici
      (allo scoperto)&rdquo;, que e foliar, com &ldquo;Agriotes sp., Agrotis sp.&rdquo;, que e de
      solo. Em 008259, <code>PESCO x MOSCA</code> e <code>TABACCO x MOSCA</code> saem com o mesmo
      texto e nao sao a mesma praga. O texto como a etichetta escreve esta na coluna ALVO abaixo,
      truncado, e inteiro na gaveta de prova.</div>
      <b>Nesta tela (${linhas.length} pares):</b>
      <ul style="margin:6px 0 0 16px">
        <li><span class="pill p-ok">EXATA</span> <b>${n('EXACT_MATCH')}</b> — cultura e alvo batem
          letra a letra E a citacao gravada contem o nome da cultura.</li>
        <li><span class="pill p-warn">LISTADA</span>
          <b>${n('LISTED_IN_DOSE_ROW')+n('LISTED_IN_DOSE_ROW_AGREEING')+n('LISTED_IN_DOSE_ROW_WITH_UNREAD_DUPLICATE')}</b>
          — cultura e alvo aparecem <i>dentro</i> da celula da linha de dose. E
          <b>inferencia de juncao</b>, nao leitura direta deste par.</li>
        <li><span class="pill p-bad">AMBIGUA</span> <b>${n('AMBIGUOUS_DOSE_FOR_THIS_PAIR')}</b>
          — duas ou mais linhas com valor lido servem e <b>discordam</b>. A ferramenta nao escolhe.</li>
        <li><span class="unknown">NO_DOSE_ROW_FOR_THIS_PAIR</span>
          <b>${n('NO_DOSE_ROW_FOR_THIS_PAIR')}</b> — nenhuma linha utilizavel serve. Nao e dose
          zero e nao e dose ausente no rotulo: e leitura que nao ligou.</li>
        ${n('EXACT_MATCH_QUOTE_LACKS_CROP')?`<li><span class="unknown">EXACT_MATCH_QUOTE_LACKS_CROP</span>
          <b>${n('EXACT_MATCH_QUOTE_LACKS_CROP')}</b> — bateu letra a letra mas a citacao da linha
          nao menciona esta cultura. Foi assim que TABACCO x CIMICI virou um numero verde.</li>`:''}
        ${n('DOSE_ROW_WITHOUT_READ_VALUE')?`<li><span class="unknown">DOSE_ROW_WITHOUT_READ_VALUE</span>
          <b>${n('DOSE_ROW_WITHOUT_READ_VALUE')}</b> — ha linha, sem valor lido.</li>`:''}
        ${n('DOSE_NOT_PROVED_TARGET_NOT_LITERAL')?`<li><span class="unknown">DOSE_NOT_PROVED_TARGET_NOT_LITERAL</span>
          <b>${n('DOSE_NOT_PROVED_TARGET_NOT_LITERAL')}</b> — ha valor lido, mas o texto do alvo nao
          foi encontrado literalmente no rotulo. O numero fica a um clique e nao e a resposta.</li>`:''}
      </ul>
        ${n('CROP_IDENTITY_NOT_PROVED')?`<li><span class="unknown">CROP_IDENTITY_NOT_PROVED</span>
          <b>${n('CROP_IDENTITY_NOT_PROVED')}</b> — a etichetta escreve mais de uma forma do mesmo
          nome curto (&ldquo;Barbabietola da zucchero&rdquo; e &ldquo;barbabietola da foraggio&rdquo;),
          com doses diferentes, e o vocabulario colapsa as duas. A ferramenta nao escolhe.</li>`:''}
        ${[['DOSE_ROW_CONTRADICTED_BY_R11_FOR_THIS_PAIR',
            'reprovada por <b>R-11</b>: os fios provam que a linha e de outra cultura'],
           ['DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE_FOR_THIS_PAIR',
            'reprovada por <b>R-22</b>: a banda tem um fio desenhado por dentro, sao duas linhas'],
           ['DOSE_ROW_REJECTED_BY_PLAUSIBILITY_FOR_THIS_PAIR',
            'reprovada por <b>R-10b</b>: o que foi lido como tabela nao se comporta como uma'],
           ['DOSE_ROW_NOT_LOCATED_FOR_THIS_PAIR',
            'caiu por <code>NOT_LOCATED</code> — falha do <b>localizador</b>, e nao regra nenhuma provando nada contra o par']
          ].filter(([k]) => n(k)).map(([k, porque]) => `<li><span class="unknown">${k}</span>
          <b>${n(k)}</b> — <b>havia</b> linha para este par e ela caiu: ${porque}. Diferente de
          nao haver linha.</li>`).join('')}
      </ul>
      ${(() => {
        // SF-08 · a frase dizia "No acervo inteiro: 76 linhas descartadas por
        // R-11". Os 76 sao OCORRENCIAS de linha, contadas sobre as 839 linhas
        // que o extrator emite ANTES de deduplicar as copias da tabela dentro
        // do mesmo PDF; o acervo que esta nesta tela tem outro numero. Dizer
        // "no acervo inteiro" sobre um denominador diferente sobredeclara o
        // conserto. Agora os dois numeros aparecem, cada um com o seu.
        const pub = P.products.reduce((a,p)=>a+(p.doses||[]).length,0);
        const rep = P.products.reduce((a,p)=>a+(p.doses||[]).filter(
          d=>d.crop_check==='CROP_ASSIGNMENT_CONTRADICTED_BY_RULE').length,0);
        return `<div class="meta" style="margin-top:6px">Nas <b>${pub}</b> linhas de dose que esta
        ferramenta publica, <b>${rep}</b> carregam <code>CROP_ASSIGNMENT_CONTRADICTED_BY_RULE</code>
        e nao respondem com numero. No arquivo de <code>R-11</code>, que conta OCORRENCIAS de linha
        antes de deduplicar as copias da tabela dentro do mesmo PDF, sao
        <b>${P.crop_check ? P.crop_check.ROWS_CONTRADICTED : val('NOT_KNOWN')}</b> de
        ${P.crop_check ? (P.crop_check.ROWS_CONSISTENT + P.crop_check.ROWS_CONTRADICTED + P.crop_check.ROWS_NOT_CHECKED) : '?'}.
        <b>Sao dois denominadores</b>, e o segundo nao e "o acervo inteiro" desta tela.
        E <b>${P.ceiling ? P.ceiling.LABELS_WITH_CEILING : val('NOT_KNOWN')}</b> rotulos trazem teto
        de dose por cultura escrito fora da tabela (<code>R-12</code>).</div>
        ${(() => { const r = P.target_literal || {};
          // SF-03 · a string R-13 nao era renderizada em NENHUMA das 9 telas,
          // enquanto R-11 e R-12 apareciam com contagem de acervo. A assimetria
          // escondia justamente a regra mais fraca — e escondia um token de
          // ignorancia que a ferramenta tem e nao mostrava: NOT_IMPLEMENTED.
          if (r.ROWS_NOT_FOUND_LITERALLY === undefined) return '';
          return `<div class="meta" style="margin-top:6px"><code>R-13</code> procura o texto de
          cada alvo LITERALMENTE no rotulo, com o documento remontado por coluna:
          <b>${r.ROWS_FOUND_LITERALLY}</b> linhas achadas
          (<b>${r.ROWS_FOUND_ONLY_AFTER_COLUMN_RECONSTRUCTION||0}</b> so depois de remontar),
          <b>${r.ROWS_NOT_FOUND_LITERALLY}</b> nao achadas e
          <b>${r.ROWS_NOT_CHECKED}</b> <span class="unknown">TARGET_TEXT_NOT_CHECKED</span>.
          <b>O modulo nao rebaixa nada; quem rebaixa e esta tela</b>, no estado
          <code>DOSE_NOT_PROVED_TARGET_NOT_LITERAL</code> acima.
          <div class="meta" style="margin-top:4px"><code>FUSION_DETECTOR =
          <span class="unknown">${esc(r.FUSION_DETECTOR||'NOT_KNOWN')}</span></code> — existe fusao
          de linha PROVADA no acervo (${esc(String(r.FUSION_PROVEN_EXAMPLE||'').slice(0,150))}) e
          esta ferramenta <b>nao sabe detecta-la</b>. R-13 acusa o sintoma, nao a causa.</div>
          </div>`;})()}`;})()}
      ${(() => { const t = P.target_name || {}, pc = P.pair_check || {}, cn = P.crop_name || {};
        const prov = (pc.COUNTS||{}).PAIR_CONSISTENT_WITH_RULES || 0;
        const nlit = (t.COUNTS||{}).TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL || 0;
        const ncul = P.products.reduce((a,p)=>a+(p.uses||[]).filter(
                       u=>u.crop_name==='CROP_NAME_NOT_IN_LABEL').length,0);
        const nflex = P.products.reduce((a,p)=>a+(p.uses||[]).filter(
                       u=>u.crop_name==='CROP_NAME_INFLECTED_IN_LABEL').length,0);
        const ancora = (pc.COUNTS||{}).PAIR_NOT_CHECKABLE_CROP_NAME_NOT_THE_ANCHOR || 0;
        const fato = P.products.reduce((a,p)=>a+(p.uses||[]).filter(u=>u.fact).length,0);
        const tot  = P.products.reduce((a,p)=>a+(p.uses||[]).length,0);
        return `<div class="lei" style="margin-top:8px;border-left-color:var(--bad)">
        <b>A CAMADA DE FATO, no acervo inteiro.</b> Um par de uso so e fato quando TRES colunas
        fecham, e elas nunca se colapsam:
        <ul style="margin:6px 0 0 16px">
          <li><b>prova</b> — o par sobreviveu a um teste contra o documento. So a camada de
            TABELA tem teste (<code>R-14</code>): <b>${prov}</b> pares. A camada de PROSA
            (<b>${P.prose ? P.prose.PROSE_PAIRS_TOTAL : val('NOT_KNOWN')}</b> pares)
            <b>nao tem regra nenhuma</b> — tres instrumentos foram construidos e medidos e os
            tres falharam, e o motivo de cada um esta escrito em
            <code>v1/inteligencia/prosa_escopo.py</code>;</li>
          <li><b>nome do alvo</b> — o NOME do alvo esta escrito no rotulo? Em <b>${nlit}</b>
            pares nao esta: o documento escreve o binomio e a ferramenta publica o nome comum
            (<code>R-17</code>). Provavelmente certo, e nao verificavel aqui.</li>
          <li><b>nome da cultura</b> — a mesma pergunta do lado mais caro (<code>R-21</code>).
            Em <b>${ncul}</b> pares publicados o nome da cultura <b>nao e palavra nenhuma do
            documento</b>: a etichetta escreve &ldquo;zucca&rdquo; e a ferramenta publica
            ZUCCHINO, escreve FAGIOLINO e a ferramenta publica FAGIOLO, escreve
            &ldquo;Pomodoro (<b>ad esclusione di</b> Pomodoro ciliegino)&rdquo; e a ferramenta
            publica CILIEGIO — o nome de uma arvore tirado de dentro da exclusao de um tomate.
            Outros <b>${nflex}</b> sao so plural italiano (&ldquo;cavoli&rdquo; para CAVOLO) e
            esses <b>fecham</b> a coluna: a palavra e a mesma.</li>
        </ul>
        <div class="meta" style="margin-top:6px">Do lado da prova, o mesmo defeito tinha uma
        segunda cara: <b>${ancora}</b> pares tinham selo verde de geometria porque a celula
        desenhada fechou pelo <b>titulo do grupo</b> (&ldquo;ORTICOLE (... FAGIOLINO ...)&rdquo;,
        &ldquo;Grano tenero e duro&rdquo;) e nao pelo nome da cultura publicada. A geometria
        provou que o TITULO e o alvo dividem uma celula; nao provou que a cultura esta no
        grupo. Agora saem como
        <code>PAIR_NOT_CHECKABLE_CROP_NAME_NOT_THE_ANCHOR</code>.</div>
        <div class="meta" style="margin-top:6px"><b>FATO = ${fato} de ${tot} pares publicados.</b>
        Os outros continuam na tela porque <code>PARSER_FAILURE != REGULATORY_ABSENCE</code> — o
        rotulo pode autorizar e a ferramenta e que nao sabe provar — mas nao carregam selo de
        prova e nao devem sair daqui como relacao factual cultura x alvo x produto.</div></div>
      <div class="lei" style="margin-top:8px;border-left-color:var(--bad)">
        <b>E o PAR DE USO desta tabela`;})()} — a cultura e o alvo, nao a dose — passou pelo mesmo teste
        de fio.</b> Ate a rodada 3 nao passava: <code>R-11</code> tirava o NUMERO de
        TABACCO x CIMICI e deixava de pe a AFIRMACAO DE USO, que e a mais fundamental das duas, com
        o selo verde <span class="pill p-ok">TABELA</span>. Agora <code>R-14</code> confere cada par
        contra a celula desenhada da cultura, e o resultado no acervo inteiro e este:
        <ul style="margin:6px 0 0 16px">
          <li><b>${P.pair_check ? (P.pair_check.COUNTS.PAIR_CONTRADICTED_BY_RULE||0) : val('NOT_KNOWN')}</b>
            pares foram <b>retirados</b> das fichas: a celula que contem a cultura nao contem o alvo.
            Cada um esta listado, com a prova geometrica, na ficha do produto.</li>
          <li><b>${P.pair_check ? (P.pair_check.COUNTS.PAIR_CONSISTENT_WITH_RULES||0) : val('NOT_KNOWN')}</b>
            sobreviveram ao teste.</li>
          <li><b>${P.pair_check ? Object.entries(P.pair_check.COUNTS).filter(([k])=>k.startsWith('PAIR_NOT_CHECKABLE')).reduce((a,[,v])=>a+v,0) : val('NOT_KNOWN')}</b>
            <span class="unknown">PAIR_NOT_CHECKABLE</span> — o teste <b>nao rodou</b> neles (rota de
            prosa, sem grade desenhada, ou o nome do alvo nao ocorre na pagina). <b>Isto nao e
            aprovacao</b>, e a coluna &ldquo;Evidencia do par&rdquo; diz qual e o caso de cada
            linha.</li>
          <li><b>${P.rotation ? P.rotation.pairs : val('NOT_KNOWN')}</b> sairam por
            <code>R-10b</code>: a unica ocorrencia do nome da cultura no rotulo esta numa frase de
            semeadura em sucessao. <b>Proibir de semear nao e autorizar a tratar.</b></li>
        </ul></div></div>`;
    })()}
    <div class="tw"><table>
      <thead><tr><th>Produto</th><th>Registro</th><th>Cultura</th><th>Alvo</th>
        <th>Dose/ha</th><th>Evidencia do par</th><th>Validade</th><th></th></tr></thead>
      <tbody>${linhas.slice(0,400).map(l => `<tr>
        <td><a onclick="go('produto');viewProduto('${l.p.reg}')" style="cursor:pointer">${esc(l.p.name)}</a></td>
        <td class="mono">${esc(l.p.reg)}</td>
        <td>${esc(l.u.crop)}${escopoDaCultura(l.u)}</td>
        <td>${esc(l.u.target)}
          ${l.u.target_raw && nrm(l.u.target_raw) !== nrm(l.u.target)
            ? (citavel(l.u.target_raw_state)
              ? `<div class="meta">o rotulo escreve: <i>&ldquo;${esc(String(l.u.target_raw).slice(0,70))}${String(l.u.target_raw).length>70?'…':''}&rdquo;</i></div>`
              // R-18 · A MESMA TELA NAO PODE DIZER DUAS COISAS SOBRE O MESMO CAMPO. Na
              // gaveta de prova este texto ja saia com nome proprio de ignorancia, e aqui
              // saia com o verbo "o rotulo escreve" e sem conferencia nenhuma.
              : `<div class="meta"><span class="unknown">${esc(l.u.target_raw_state || 'QUOTE_NOT_CHECKED')}</span>
                 o extrator leu <code>${esc(String(l.u.target_raw).slice(0,70))}${String(l.u.target_raw).length>70?'…':''}</code>
                 — <b>leitura do extrator</b>, nao frase do rotulo</div>`) : ''}</td>
        <td>${celulaDose(l)}</td>
        <td>${evidenciaDoPar(l.u)}</td>
        <td>${validade(l.p)}</td>
        <td><button class="ev" onclick="evUso('${l.p.reg}',${l.i})">prova</button></td>
      </tr>`).join('')}</tbody></table></div>
    ${linhas.length>400?`<div class="meta">mostrando 400 de ${linhas.length} — refine a busca</div>`:''}`;
}
window.viewCrop = viewCrop;

// ---------------------------------------------------------------- 5 · CALENDAR
function viewCal() {
  const fx = [[30,'30 dias'],[90,'90 dias'],[180,'180 dias'],[365,'12 meses']];
  const venc = P.products.filter(conflitoDeValidade);
  const vencCoerente = P.products.filter(p => typeof dte(p) === 'number' && dte(p) < 0 && foraDeVigor(p));
  const bloco = (lo,hi,lbl) => {
    const l = P.products.filter(p => typeof dte(p) === 'number' && dte(p) >= lo && dte(p) <= hi)
      .sort((a,b) => dte(a) - dte(b));
    return `<div class="block"><h3>${lbl} <span class="meta">(${l.length})</span></h3>
    ${l.length ? `<div class="tw"><table>
      <thead><tr><th>Validade</th><th>Faltam</th><th>Produto</th><th>Registro</th><th>Estado</th><th>Usos lidos</th><th></th></tr></thead>
      <tbody>${l.map(p=>`<tr><td class="mono">${esc(p.expiry)}</td><td>${dte(p)}d</td>
        <td>${esc(p.name)}</td><td class="mono">${esc(p.reg)}</td><td class="meta">${esc(p.status)}</td>
        <td>${contagem(p,'uses','LABEL_READ')}</td>
        <td><button class="ev" onclick="evProd('${p.reg}')">prova</button></td></tr>`).join('')}
      </tbody></table></div>` : '<div class="meta">nenhum produto nesta janela</div>'}</div>`;
  };
  $('#v-cal').innerHTML = `
  ${avisoRelogio()}
  ${GLOSA_JANELA}
  <div class="lei">Todas as datas abaixo vem do campo <code>data_scadenza_autorizzazione</code> do
    registro oficial. <b>A ferramenta nao cria prazo que nao esta na fonte</b> — nao ha deadline de
    revisao inventado aqui. E vencimento nao e revogacao.</div>
  <div class="block" style="border-left:3px solid var(--bad)">
    <h3>Validade ja vencida, e o registro ainda lista como em vigor <span class="meta">(${venc.length})</span></h3>
    <div class="meta">Estes sao um conflito entre dois campos oficiais do mesmo instantaneo, nao uma
      conclusao nossa: a data passou e o <code>stato_amministrativo</code> continua sendo um estado
      em vigor.</div>
    <div class="tw" style="margin-top:8px"><table>
      <thead><tr><th>Validade</th><th>Ha</th><th>Produto</th><th>Registro</th><th>Estado declarado</th><th></th></tr></thead>
      <tbody>${venc.sort((a,b)=>a.expiry.localeCompare(b.expiry)).map(p=>`<tr>
        <td class="mono" style="color:var(--bad)">${esc(p.expiry)}</td><td>${-dte(p)}d</td>
        <td>${esc(p.name)}</td><td class="mono">${esc(p.reg)}</td><td>${esc(p.status)}</td>
        <td><button class="ev" onclick="evProd('${p.reg}')">prova</button></td></tr>`).join('')}
      </tbody></table></div></div>
  ${vencCoerente.length ? `<div class="block">
    <h3>Validade vencida, e o registro JA declara fora de vigor <span class="meta">(${vencCoerente.length})</span></h3>
    <div class="meta">Aqui os dois campos oficiais <b>concordam</b> — nao ha conflito, e por isso
      estes nao aparecem no bloco vermelho acima. A ferramenta separa os dois casos porque afirmar
      &ldquo;o registro ainda lista como em vigor&rdquo; sobre um produto <code>Scaduto</code> seria
      inventar um desacordo que a fonte nao tem.</div>
    <div class="tw" style="margin-top:8px"><table>
      <thead><tr><th>Validade</th><th>Ha</th><th>Produto</th><th>Registro</th><th>Estado declarado</th><th></th></tr></thead>
      <tbody>${vencCoerente.sort((a,b)=>String(a.expiry).localeCompare(String(b.expiry))).map(p=>`<tr>
        <td class="mono">${esc(p.expiry)}</td><td>${-dte(p)}d</td>
        <td>${esc(p.name)}</td><td class="mono">${esc(p.reg)}</td><td>${val(p.status)}</td>
        <td><button class="ev" onclick="evProd('${p.reg}')">prova</button></td></tr>`).join('')}
      </tbody></table></div></div>` : ''}
  ${bloco(0,30,'Vencem em ate 30 dias')}
  ${bloco(31,90,'31 a 90 dias')}
  ${bloco(91,180,'91 a 180 dias')}
  ${bloco(181,365,'181 dias a 12 meses')}`;
}

// ---------------------------------------------------------------- 6 · ACTION CENTER
// S5 · o corte em 60 linhas era mudo: 150 objetos sumiam da tela cujo proposito
// e ser a caixa de entrada de uma area. Continua havendo corte (a tela tem de
// abrir), mas ele e dito, contado, e reversivel em um clique.
let LIMITE = 60;
function setLimite(n) { LIMITE = Number(n) || 60; viewAction(); }
window.setLimite = setLimite;

function viewAction() {
  const caps = Object.keys(CAPS);
  const blocos = caps.map(c => {
    const meus = P.objects.map(o => {
      const r = o.CAPABILITY_ROUTING.find(x => x.CAPABILITY_ID === c);
      return r ? {o, r} : null;
    }).filter(Boolean);
    // Agrupa por ESTADO + REGRA + JUSTIFICATIVA. Um cabecalho de grupo so pode
    // anunciar o que vale para TODAS as linhas dele. Duas correcoes somadas:
    //  - antes o cabecalho pegava a regra do primeiro objeto e a estampava sobre
    //    210 linhas com regras diferentes;
    //  - agrupar so por ESTADO+REGRA ainda nao bastava, porque C-99 escreve o
    //    tipo do evento dentro da justificativa: um grupo C-99 juntava sete
    //    tipos e o cabecalho anunciava o de cima ("nenhuma regra cobre
    //    DATE_CHANGE") sobre linhas de NEEDS_HUMAN_REVIEW e EXPIRY_EVENT.
    const porEstado = {};
    meus.forEach(x => {
      const k = JSON.stringify([x.r.ROUTING_STATE, x.r.RULE_ID, x.r.JUSTIFICATION]);
      (porEstado[k] = porEstado[k]||[]).push(x);
    });
    const rtvNota = c === 'COMMERCIAL_RTV'
      ? `<div class="lei">O campo nao recebe fato regulatorio bruto. Regra <code>C-05</code>:
         tudo fica <code>NOT_RELEVANT</code> ate o portao <code>G-01</code>, que exige prova e
         revisao humana registrada. <b>Esta versao nao abre esse portao.</b>
         A ferramenta so criaria <code>COMMERCIAL_MESSAGE_CANDIDATE</code>, nunca uma mensagem.</div>`
      : '';
    if (!meus.length) return `<div class="block"><h3>${CAPS[c]}</h3>${rtvNota}
      <div class="meta">nenhum objeto alcanca esta capacidade</div></div>`;
    const linha = (chave, lista) => { const [est, rid, just] = JSON.parse(chave);
      // Tripwire: se um dia o agrupamento deixar entrar duas justificativas no
      // mesmo grupo, a tela diz isso em vez de estampar a do primeiro objeto.
      const js = new Set(lista.map(x => x.r.JUSTIFICATION));
      const por = js.size === 1 ? esc(just)
        : `<span class="unknown">JUSTIFICATION_NOT_UNIFORM</span> (${js.size} textos diferentes sob a mesma regra)`;
      // NOT_RELEVANT e um portao fechado, nao uma lista. Listar as 210 linhas
      // debaixo de um aviso dizendo que o portao as barra e mostrar exatamente
      // o que se afirmou nao estar mostrando.
      if (est === 'NOT_RELEVANT') return `<div style="margin:9px 0">
        <span class="pill p-dim">NOT_RELEVANT</span>
        <span class="meta"><b>${lista.length} objeto(s)</b> barrados aqui pela regra
          <code>${esc(rid)}</code> — ${por}</span>
        <div class="meta">As linhas <b>nao</b> sao listadas nesta area: o estado delas para esta
          capacidade e &ldquo;nao passa&rdquo;, e imprimir a tabela seria entregar como conteudo o
          que a regra acabou de barrar. Cada um destes objetos continua visivel, com prova, na(s)
          area(s) onde alguma regra o deixa passar, e em MUDANCAS.</div></div>`;
      return `<div style="margin:9px 0">
      <span class="pill ${est==='RELEVANT'?'p-ok':est==='POTENTIALLY_RELEVANT'?'p-warn':'p-unk'}">${est}</span>
      ${est==='UNKNOWN'?'<span class="meta">— nenhuma regra cobre este tipo para esta area. <b>Isto nao diz que a area nao precisa olhar; diz que nao sabemos.</b></span>':''}
      <span class="meta">${lista.length} objeto(s) &middot; regra <code>${esc(rid)}</code> — ${por}</span>
      <div class="tw" style="margin-top:6px"><table>
        <thead><tr><th>Produto</th><th>Tipo</th><th>Antes &rarr; Depois</th><th>Janela</th><th>Prova</th><th></th></tr></thead>
        <tbody>${lista.slice(0, LIMITE).map(({o}) => `<tr>
          <td>${esc(o.PRODUCT_NAME||'NOT_KNOWN')}<div class="mono meta">${esc(o.REGISTRATION_ID)}</div></td>
          <td>${esc(o.CHANGE_TYPE)}</td>
          <td>${val(o.BEFORE_VALUE)} &rarr; ${val(o.AFTER_VALUE)}</td>
          <td>${janelaSelo(o)}</td>
          <td><span class="pill ${PROOF[o.PROOF_STATE]||'p-dim'}">${esc(o.PROOF_STATE)}</span></td>
          <td><button class="ev" onclick="evObj('${o.INTELLIGENCE_OBJECT_ID}')">evidencia</button></td>
        </tr>`).join('')}</tbody></table></div>
      ${lista.length>LIMITE?`<div class="meta"><b>mostrando ${LIMITE} de ${lista.length}</b> —
        ${lista.length-LIMITE} objeto(s) deste grupo nao estao nesta tela.
        <button class="ev" onclick="setLimite(${lista.length})">mostrar todos os ${lista.length}</button>
        ${LIMITE>60?`<button class="ev" onclick="setLimite(60)">voltar a 60</button>`:''}</div>`:''}</div>`; };
    // S6 · "(210)" queria dizer duas coisas opostas com o mesmo estilo: em
    // Regulatory, 210 itens roteados para voce; em Marketing, 210 itens que
    // NENHUMA regra soube rotear — uma fila vazia com cara de fila cheia.
    // Agora o cabecalho separa o que chegou do que ninguem soube endereçar.
    const roteados = meus.filter(x => x.r.ROUTING_STATE === 'RELEVANT' ||
                                      x.r.ROUTING_STATE === 'POTENTIALLY_RELEVANT').length;
    const semRegra = meus.filter(x => x.r.ROUTING_STATE === 'UNKNOWN').length;
    const barrados = meus.filter(x => x.r.ROUTING_STATE === 'NOT_RELEVANT').length;
    const cabecalho = `<h3>${CAPS[c]}
      <span class="meta">&mdash; ${roteados ? `<b>${roteados}</b> roteado(s) por regra` : '<b>0</b> roteados'}
      ${semRegra ? ` &middot; <span class="unknown">${semRegra} sem regra (UNKNOWN)</span>` : ''}
      ${barrados ? ` &middot; ${barrados} barrado(s) por portao` : ''}</span></h3>
      ${roteados === 0 && semRegra > 0 ? `<div class="lei" style="border-left-color:var(--unk)">
        <b>Esta fila esta vazia, e o numero grande ao lado nao e a fila.</b> Nenhuma regra
        roteia qualquer objeto desta versao para esta area: os ${semRegra} sao objetos que
        chegaram ate aqui e sairam como <code>UNKNOWN</code>.
        ${(c === 'MARKETING_PRODUCT' || c === 'DEVELOPMENT_MARKET') ? `Isto e estrutural, nao um
        mes parado: as regras <code>C-03</code>, <code>C-04</code> e <code>C-06</code> consomem
        <code>CROP_USE_ADDED/REMOVED</code>, <code>TARGET_USE_ADDED/REMOVED</code>,
        <code>DOSE_CHANGE</code> e <code>RESTRICTION_CHANGE</code>, e <b>nenhum desses tipos tem
        emissor nesta versao</b> — o motor de mudanca compara campos do registro oficial e ainda
        nao compara duas leituras de rotulo. Enquanto isso nao existir, esta area recebe zero, e
        a ferramenta prefere dizer isso a fingir uma caixa de entrada.` : ''}</div>` : ''}`;
    return `<div class="block">${cabecalho}${rtvNota}
      ${Object.keys(porEstado).sort((a,b)=>{
          const o={RELEVANT:0,POTENTIALLY_RELEVANT:1,UNKNOWN:2,NEEDS_REVIEW:3,NOT_RELEVANT:4};
          return (o[JSON.parse(a)[0]]??9)-(o[JSON.parse(b)[0]]??9);
        }).map(k => linha(k, porEstado[k])).join('')}</div>`;
  });
  $('#v-action').innerHTML = GLOSA_JANELA + `
  <div class="lei">Roteamento diz <b>quem pode precisar olhar</b>, nunca <b>o que fazer</b>.
    Cada estado abaixo aponta a regra <code>C-*</code> que o autoriza, em
    <code>v1/inteligencia/REGRAS.md</code>. Tipo de evento sem regra sai <code>UNKNOWN</code>.
    <b>Esta ferramenta nao emite ACTION.</b></div>
  ${blocos.join('')}`;
}

// ---------------------------------------------------------------- 7 · REVIEW QUEUE
function tabRev(lista) {
  return `<div class="tw"><table>
    <thead><tr><th>Produto</th><th>Cultura lida</th><th>Alvo lido</th><th>Valor rebaixado</th>
      <th>Regra que rebaixou</th><th>O que o fio dizia antes</th><th>Onde</th><th></th></tr></thead>
    <tbody>${lista.map(o => `<tr>
      <td>${esc(o.PRODUCT_NAME)}<div class="mono meta">${esc(o.REGISTRATION_ID)}</div></td>
      <td>${fragmento(o.AFFECTED_CROP)}</td><td>${fragmento(o.AFFECTED_TARGET)}</td>
      <td style="color:var(--bad)">${val(o.BEFORE_VALUE)}</td>
      <td class="meta">${val(o.DEMOTION_RULE)}</td>
      <td class="meta">${o.RULE_CHECK_BEFORE_DEMOTION==='CONFIRMED_BY_RULE'
        ? `<b style="color:var(--warn)">CONFIRMED_BY_RULE</b>
           <div class="meta">o fio desenhado CONFIRMAVA este valor; a heuristica passou por cima</div>`
        : val(o.RULE_CHECK_BEFORE_DEMOTION)}</td>
      <td class="meta">${val(o.EVIDENCE_LOCATION)}</td>
      <td><button class="ev" onclick="evObj('${o.INTELLIGENCE_OBJECT_ID}')">evidencia</button></td>
    </tr>`).join('') || '<tr><td colspan=8 class="meta">nenhuma</td></tr>'}</tbody></table></div>`;
}

// S10 · fragmentos de parser publicados com cara de nome de cultura: FOLPAN GOLD
// mostrava CULTURA "da vino" e ALVO "della vite (Plasmopara" — as metades finais
// de "VITE da vino" e "Peronospora della vite (Plasmopara viticola)". Continuam
// visiveis, porque apagar evidencia de leitura errada e pior; mas a tela agora
// diz que aquilo e um fragmento, nao um nome.
const FUNCIONAL = /^(da |della |dello |dei |delle |degli |di |del |al |alla |in |con |per |su |e |ed |o )/i;
function fragmento(v) {
  if (isUnk(v)) return val(v);
  const t = String(v);
  if (!FUNCIONAL.test(t) && !/\($/.test(t.trim()) && !/\([^)]*$/.test(t)) return esc(t);
  return `<span class="unknown" title="o extrator cortou a celula: isto e um pedaco de texto, nao um nome de cultura ou alvo">FRAGMENTO_DE_LEITURA</span>
    <div class="meta">o extrator guardou &ldquo;${esc(t)}&rdquo;, que comeca por palavra funcional
    italiana ou tem parentese aberto sem fechar: e a metade de uma celula, nao um nome</div>`;
}

function viewReview() {
  const rev = P.objects.filter(o => o.OBJECT_TYPE === 'NEEDS_HUMAN_REVIEW');
  // S9 · a tela chamava "contradicao de fio" um conjunto produzido por DOIS
  // mecanismos com graus de evidencia diferentes: o fio desenhado e uma medida
  // do documento; o filtro de plausibilidade e uma heuristica que nos
  // escrevemos. Juntar os dois debaixo do nome do mais forte inflava a
  // evidencia do mais fraco.
  const porFio = rev.filter(o => o.DEMOTION_MECHANISM !== 'PLAUSIBILITY_FILTER');
  const porPlaus = rev.filter(o => o.DEMOTION_MECHANISM === 'PLAUSIBILITY_FILTER');
  const dq = P.objects.filter(o => o.OBJECT_TYPE === 'DATA_QUALITY_EVENT');
  const semUso = P.products.filter(p => !p.uses.length);
  const semDose = P.products.filter(p => !p.doses.length);
  $('#v-review').innerHTML = `
  <div class="lei"><b>Esta tela mostra o que a maquina recusou adivinhar.</b>
    Nenhum item aqui e uma afirmacao sobre o produto — todos sao afirmacoes sobre o
    <b>nosso estado de leitura</b>. <code>PARSER_FAILURE != REGULATORY_ABSENCE</code></div>
  <div class="cards">
    <div class="kpi"><b style="color:var(--rev)">${porFio.length}</b><span>doses rebaixadas por fio desenhado (medida)</span></div>
    <div class="kpi"><b style="color:var(--rev)">${porPlaus.length}</b><span>doses rebaixadas por plausibilidade (heuristica nossa)</span></div>
    <div class="kpi"><b style="color:var(--unk)">${dq.length}</b><span>rotulos sem tabela de uso lida</span></div>
    <div class="kpi"><b style="color:var(--unk)">${semUso.length}</b><span>produtos sem par cultura x alvo</span></div>
    <div class="kpi"><b style="color:var(--unk)">${semDose.length}</b><span>produtos sem dose estruturada</span></div>
    <div class="kpi"><b style="color:var(--unk)">${P.products.length}</b><span>fichas sem PHI (nao publicado)</span></div>
  </div>

  <h2>Dose rebaixada porque o fio desenhado da tabela contradiz o valor (${porFio.length})</h2>
  <div class="meta" style="margin-bottom:8px">O extrator leu um valor; os fios desenhados da tabela
    mostram que ele pertence a outra linha. Isto e uma <b>medida do documento</b>. O valor foi
    <b>rebaixado, nao corrigido no palpite</b> — trocar um erro por outro nao e conserto.</div>
  ${tabRev(porFio)}

  <h2>Dose rebaixada por filtro de plausibilidade (${porPlaus.length})</h2>
  <div class="lei" style="border-left-color:var(--unk)"><b>Grau de evidencia diferente do bloco de
    cima.</b> Aqui a rebaixa veio de uma <b>heuristica nossa</b> (regras <code>P-01</code> a
    <code>P-05</code>, escritas em <code>REGRAS.md</code>), que julgou que a linha nao parece uma
    linha de dose — por exemplo, uma celula que comeca por palavra funcional italiana, sinal de
    que o extrator cortou a celula no meio. A heuristica pode estar errada nos dois sentidos, e
    por isso o item vem para revisao humana em vez de ser apagado.
    <b>A coluna &ldquo;o que o fio dizia antes&rdquo; mostra o veredito da medida do documento que
    esta heuristica sobrescreveu</b> — onde ele diz <code>CONFIRMED_BY_RULE</code>, o fio
    desenhado confirmava o valor e a heuristica derrubou assim mesmo. Dizer que &ldquo;nenhum fio
    contradisse nada&rdquo; seria afirmar um negativo cuja prova este modulo tinha apagado.</div>
  ${tabRev(porPlaus)}

  <h2>Rotulos cuja tabela de uso nao foi lida (${dq.length})</h2>
  <div class="lei">A maioria dos herbicidas italianos declara dose em <b>prosa</b>
    (&ldquo;alla dose di 1-3 l/ha&rdquo;), nao em tabela. Este leitor le tabela.
    <b>Nenhum destes produtos e um produto sem uso ou sem dose.</b></div>
  <div class="tw"><table>
    <thead><tr><th>Produto</th><th>Registro</th><th>Atividade</th><th>Estado do leitor</th><th>Pares lidos</th><th></th></tr></thead>
    <tbody>${dq.slice(0,200).map(o => {
      const p = byReg[o.REGISTRATION_ID] || {};
      return `<tr><td>${esc(o.PRODUCT_NAME)}</td><td class="mono">${esc(o.REGISTRATION_ID)}</td>
      <td class="meta">${esc(p.activity||'NOT_KNOWN')}</td>
      <td><code>${esc(p.dose_state||'NOT_ATTEMPTED')}</code></td>
      <td>${contagem(p,'uses','LABEL_READ')}</td>
      <td><button class="ev" onclick="evObj('${o.INTELLIGENCE_OBJECT_ID}')">evidencia</button></td></tr>`;
    }).join('')}</tbody></table></div>`;
}

// ---------------------------------------------------------------- 9 · COVERAGE
function viewCov() {
  const c = P.coverage;
  const barra = (k, o) => `<tr><td>${k.replace(/_/g,' ')}</td>
    <td><b>${o.COVERED}</b> <span class="meta">de ${o.OF}</span></td>
    <td style="width:44%"><div style="background:#0b0e10;border-radius:4px;height:16px;position:relative">
      <div style="position:absolute;inset:0 auto 0 0;width:${o.PCT}%;background:${o.PCT>=90?'var(--ok)':o.PCT>=40?'var(--warn)':'var(--unk)'};border-radius:4px"></div>
      <b style="position:relative;font-size:10.5px;padding-left:6px;line-height:16px">${o.PCT}%</b></div></td></tr>`;
  $('#v-cov').innerHTML = `
  <div class="lei"><b>Nao existe um numero unico de cobertura nesta ferramenta.</b>
    Cada linha abaixo conta uma coisa diferente e <b>nenhuma implica a seguinte</b>:
    ter o PDF nao e ter lido, ter lido nao e ter estruturado o uso, e ter o uso nao e ter a dose.</div>
  <div class="lei" style="border-left-color:var(--unk)"><b>Dois denominadores, e eles nao sao o
    mesmo universo.</b> A cobertura abaixo denomina por <b>${P.coverage.LABEL_DISCOVERY_COVERAGE.OF}</b>:
    os produtos ADAMA <b>no conjunto ativo</b> do instantaneo vigente, que sao os que a coleta
    percorreu. O seletor de PRODUTO 360 oferece <b>${P.products.length}</b> fichas, porque
    ${P.products.filter(p=>p.out_of_active_set).length} registros aparecem em eventos do historico
    <b>sem estar no conjunto ativo</b> (${P.products.filter(p=>p.out_of_active_set).map(p=>esc(p.reg)+' '+esc(p.name)).join(', ')}).
    Eles tem ficha porque a linha oficial deles foi lida; <b>nao</b> entram na cobertura porque
    nenhum rotulo foi coletado para eles. Somar os dois numeros seria contar universos
    diferentes.</div>
  ${(() => { const c = P.coverage_crop_cell || {};
    if (c.CROP_CELLS_DETECTED === undefined) return '';
    const nr = (c.COUNTS||{})['CROP_BLOCK_NOT_COLLECTED']||0;
    const iv = (c.COUNTS||{})['CROP_BLOCK_IN_VOCABULARY_NOT_READ']||0;
    return `<div class="lei" style="border-left-color:var(--bad)">
    <b>A cobertura acima conta ROTULO. Esta conta CELULA DE CULTURA DESENHADA — e o numero e
    outro.</b> Um rotulo conta como coberto se dele saiu <i>pelo menos um</i> par; assim o bloco
    que o leitor nao leu desaparece no denominador do bloco que ele leu. Medido com os fios:
    <div class="tw" style="margin-top:8px"><table><tbody>
      <tr><td>celulas de cultura desenhadas detectadas</td><td><b>${c.CROP_CELLS_DETECTED}</b></td></tr>
      <tr><td>com alguma cultura que virou par de uso</td><td><b style="color:var(--ok)">${c.CROP_CELLS_READ}</b>
        (${c.PCT}%)</td></tr>
      <tr><td><code>CROP_BLOCK_NOT_COLLECTED</code> — o nome esta fora dos
        ${c.USE_VOCABULARY_SIZE} do vocabulario de uso</td><td><b style="color:var(--unk)">${nr}</b></td></tr>
      <tr><td><code>CROP_BLOCK_IN_VOCABULARY_NOT_READ</code> — o nome ESTA no vocabulario e o
        bloco nao produziu par</td><td><b style="color:var(--bad)">${iv}</b></td></tr>
    </tbody></table></div>
    <div class="meta" style="margin-top:6px"><b>Isto nao e "a cobertura verdadeira".</b> Uma
    celula desenhada com nome de cultura pode ser cabecalho, nota ou tabela de carencia, e uma
    etichetta que repete a tabela conta a celula duas vezes. A diferenca e um <b>piso</b> do que
    falta, nao o total. As duas coberturas ficam na tela porque contam coisas diferentes —
    cobertura como numero unico foi o defeito da rodada 1.</div>
    <div class="meta" style="margin-top:6px">O vocabulario de uso e uma lista FECHADA de
    <b>${VOCAB_USO.length}</b> nomes. Nomes que a etichetta escreve e que ele nao tem — medido:
    <code>PORRO</code>, <code>FINOCCHIO</code>, <code>LATTUGHE</code>, <code>SCAROLE</code>,
    <code>RUCOLA</code>, <code>SEDANO</code>, <code>CAVOLFIORE</code>, <code>POMACEE</code>,
    <code>FRUMENTO</code> — nao viram par de uso mesmo quando o rotulo os autoriza. A tela
    CULTURA x ALVO responde <code>CROP_NOT_IN_USE_VOCABULARY</code> nesses casos.
    <div class="meta">Os ${VOCAB_USO.length} nomes: <code>${esc(VOCAB_USO.join(', '))}</code></div></div>
    </div>`;})()}
  <div class="block"><h3>Cobertura por etapa</h3>
    <div class="tw"><table><tbody>${Object.entries(c).map(([k,o]) => barra(k,o)).join('')}</tbody></table></div>
    <div class="meta" style="margin-top:9px">${esc(P.coverage_note)}</div></div>
  <div class="block"><h3>Historico e comparabilidade</h3>
    <div class="tw"><table><tbody>
      <tr><td>Instantaneos oficiais baixados</td><td><b>${P.history.snapshots}</b></td></tr>
      <tr><td>Documentos distintos (sha256)</td><td><b>${P.history.distinct}</b></td></tr>
      <tr><td>Janela observada</td><td class="mono">${esc(P.history.window)}</td></tr>
      <tr><td>Diferencas brutas de campo</td><td>${P.history.raw_field_diffs}</td></tr>
      <tr><td>Apos normalizar (SEMANTIC_DIFF)</td><td>${P.history.normalised_field_diffs}</td></tr>
      <tr><td>Ruido de serializacao suprimido</td><td><b>${P.history.noise}</b> (${P.history.noise_pct}%)</td></tr>
      <tr><td>Eventos regulatorios</td><td><b style="color:var(--ok)">${P.history.true_changes}</b></td></tr>
    </tbody></table></div></div>
  ${(() => { const r = P.reconciliation || {};
    if (r.STATE === 'NOT_CHECKED' || r.TRUE_CHANGES_MEASURED === undefined)
      return `<div class="block"><h3>Reconciliacao com a releitura crua da fonte</h3>
        <div class="meta">${val('NOT_CHECKED')} — a recontagem independente nao rodou neste build</div></div>`;
    // Os numeros desta ferramenta e os da recontagem independente apareciam em
    // lugares diferentes sem que nada dissesse por que diferiam. Diferenca sem
    // mecanismo e a mesma doenca de publicar cobertura como numero unico.
    const lin = (k, m, pb, d, por) => `<tr><td>${k}</td><td><b>${m}</b></td><td><b>${pb}</b></td>
      <td style="color:${d?'var(--warn)':'var(--ok)'}"><b>${d}</b></td><td class="meta">${por}</td></tr>`;
    return `<div class="block"><h3>Reconciliacao com a releitura crua da fonte</h3>
      <div class="meta" style="margin-bottom:8px"><code>v1/medir_baseline.py</code> le a fonte e
        reexecuta os extratores sem a camada de inteligencia. Esta ferramenta publica o que sobra
        <b>depois</b> dela. Os dois numeros nao tem de ser iguais &mdash; tem de ser
        <b>explicados</b>.</div>
      <div class="tw"><table>
        <thead><tr><th>Grandeza</th><th>Releitura crua</th><th>Publicado</th><th>Delta</th>
          <th>Mecanismo</th></tr></thead>
        <tbody>
        ${lin('mudancas reais', r.TRUE_CHANGES_MEASURED, r.TRUE_CHANGES_PUBLISHED,
              r.TRUE_CHANGES_DELTA, esc(r.POR_QUE_O_DELTA_DE_MUDANCA||''))}
        ${lin('linhas de dose distintas', r.DOSE_ROWS_MEASURED_DISTINCT, r.DOSE_ROWS_PUBLISHED_DISTINCT,
              r.DOSE_ROWS_DELTA, esc(r.POR_QUE_O_DELTA_DE_DOSE||''))}
        ${lin('rotulos com linha de dose', r.DOSE_LABELS_MEASURED, r.DOSE_LABELS_PUBLISHED,
              r.DOSE_LABELS_DELTA, 'P-01: tabela que o extrator achou onde nao havia')}
        </tbody></table></div></div>`; })()}
  <div class="block"><h3>O que esta versao declaradamente nao faz</h3>
    <ul class="meta" style="line-height:1.8">
      <li>nao emite <code>ACTION</code> — o parser nao produz acao;</li>
      <li>nao emite <code>PHI_CHANGE</code> — portao <code>G-02</code> fechado, <code>PHI_PROVED = 0</code>;</li>
      <li>nao emite implicacao de negocio — portao <code>G-03</code>, nenhuma regra <code>B-*</code> existe;</li>
      <li>nao envia nada ao campo — portao <code>G-01</code> fechado;</li>
      <li>nao infere demanda, estoque, preco ou concorrencia a partir de rotulo;</li>
      <li>nao publica citacao literal dos pares cultura x alvo: os pares reusados nao gravam
          coordenada x e a etichetta tem varias colunas por pagina. Tentado, medido, descartado.</li>
    </ul></div>`;
}

// ---------------------------------------------------------------- 10 · SEARCH
function viewSearch() {
  const q = ($('#sq').value||'').trim().toLowerCase();
  if (!q) { $('#sres').innerHTML = '<div class="meta">digite um produto, registro, cultura, alvo, substancia ativa, estado ou tipo de mudanca</div>'; return; }
  const prods = P.products.filter(p =>
    [p.name,p.reg,p.actives,p.holder,p.status,p.activity,p.formulation].join(' ').toLowerCase().includes(q)
    || p.uses.some(u => (u.crop+' '+u.target).toLowerCase().includes(q)));
  const objs = P.objects.filter(o =>
    [o.PRODUCT_NAME,o.REGISTRATION_ID,o.CHANGE_TYPE,o.FACT,o.BEFORE_VALUE,o.AFTER_VALUE]
      .join(' ').toLowerCase().includes(q));
  $('#sres').innerHTML = `
  <div class="lei">A busca so consulta os <b>intelligence objects</b> e os produtos ja resolvidos
    pela inteligencia. <b>Ela nao le PDF e nao gera resposta livre.</b> Toda linha do resultado
    leva a prova.</div>
  <h2>Produtos (${prods.length})</h2>
  ${prods.length ? `<div class="tw"><table>
    <thead><tr><th>Produto</th><th>Registro</th><th>Titular</th><th>Ativos</th><th>Validade</th><th>Usos</th><th>Doses</th><th></th></tr></thead>
    <tbody>${prods.slice(0,80).map(p=>`<tr>
      <td><a onclick="go('produto');viewProduto('${p.reg}')" style="cursor:pointer">${esc(p.name)}</a></td>
      <td class="mono">${esc(p.reg)}</td><td class="meta">${esc(p.holder)}</td>
      <td class="meta">${val(p.actives)}</td><td>${validade(p)}</td>
      <td>${contagem(p,'uses','LABEL_READ')}</td>
      <td>${contagem(p,'doses','LABEL_READ')}</td>
      <td><button class="ev" onclick="evProd('${p.reg}')">prova</button></td></tr>`).join('')}
    </tbody></table></div>` : '<div class="meta">nenhum produto</div>'}
  <h2>Eventos (${objs.length})</h2>
  ${objs.length ? objs.slice(0,40).map(cardObj).join('') : '<div class="meta">nenhum evento</div>'}`;
}
window.viewSearch = viewSearch;

// ---------------------------------------------------------------- roteador
const VIEWS = {today:viewToday, produto:()=>viewProduto($('#psel').value),
               timeline:viewTimeline, crop:viewCrop, cal:viewCal, action:viewAction,
               review:viewReview, cov:viewCov, search:viewSearch};
function go(v) {
  $$('nav a').forEach(a => a.classList.toggle('on', a.dataset.v === v));
  $$('.view').forEach(x => x.classList.remove('on'));
  $('#v-'+v).classList.add('on');
  (VIEWS[v]||(()=>{}))();
  window.scrollTo(0,0);
}
window.go = go;
$$('nav a').forEach(a => a.onclick = () => go(a.dataset.v));
document.addEventListener('keydown', e => { if (e.key === 'Escape') $('#dr').classList.remove('open'); });

// selects e buscas
$('#psel').innerHTML = P.products.slice().sort((a,b)=>a.name.localeCompare(b.name))
  .map(p => `<option value="${p.reg}">${esc(p.name)} — ${esc(p.reg)}</option>`).join('');
$('#psel').addEventListener('change', () => viewProduto($('#psel').value));
['cq','ct'].forEach(id => $('#'+id).addEventListener('input', viewCrop));
$('#sq').addEventListener('input', viewSearch);

// A tarja de datas do cabecalho, preenchida pelo relogio de quem abre.
$('#relogio').innerHTML = hojeISO()
  ? `dado: <b>${esc(DATA_DATE)}</b> (${esc(P.DATA_SNAPSHOT_ID)}) &middot; ultima mudanca provada:
     <b>${esc(ULTIMA_MUDANCA)}</b> &middot; montado em ${esc(P.BUILT_AT)} &middot;
     hoje: <b>${esc(hojeISO())}</b>${idadeDoDado() !== null && -idadeDoDado() > 0 ? ` &middot; o dado tem ${-idadeDoDado()} dia(s)` : ''}`
  : `dado: <b>${esc(DATA_DATE)}</b> &middot; montado em ${esc(P.BUILT_AT)} &middot;
     <span class="unknown">SEM_RELOGIO</span> — este navegador nao devolveu a data de hoje`;

go('today');
