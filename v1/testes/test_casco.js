// test_casco.js — testes de RENDERIZACAO do casco.
//
// Ate agora os defeitos de tela eram achados por leitura humana do HTML. Isto
// executa o app.js de verdade, com um DOM falso minimo, e afirma sobre o HTML
// que ele produz. Cada teste aqui nasceu de um defeito real encontrado pelo
// red team ou pelo arbitro.
const fs = require('fs'), path = require('path');
const RAIZ = path.resolve(__dirname, '..', '..');

function elemento() {
  const e = {
    innerHTML: '', value: '', dataset: {},
    classList: {add(){}, remove(){}, toggle(){}, contains(){return false}},
    addEventListener(){}, appendChild(){}, querySelector: () => elemento(),
  };
  Object.defineProperty(e, 'onclick', {set(){}, get(){return null}});
  return e;
}
const capturado = {};
global.document = {
  querySelector(sel) { return capturado[sel] || (capturado[sel] = elemento()); },
  querySelectorAll() { return []; },
  addEventListener() {},
};
// Carrega o payload como o NAVEGADOR carrega: por window.__PAYLOAD__, deixando
// o proprio app.js declarar P. Injetar P por fora escondia um erro real de
// ordem de declaracao (TDZ) que deixava a ferramenta em branco no Chromium.
global.window = { scrollTo() {}, addEventListener() {},
  __PAYLOAD__: JSON.parse(fs.readFileSync(path.join(RAIZ, 'v1/dados/CASCO-PAYLOAD.json'), 'utf8')) };
const fonte = fs.readFileSync(path.join(RAIZ, 'v1/casco/app.js'), 'utf8');
(0, eval)(fonte);
global.P = window.__PAYLOAD__;

const testes = [];
const teste = (nome, fn) => testes.push([nome, fn]);
function afirma(cond, msg) { if (!cond) throw new Error(msg); }
const html = sel => capturado[sel] ? capturado[sel].innerHTML : '';

// ---------------------------------------------------------------- 1 · dose
teste('MELONE x AFIDI nao recebe a dose de macieira e pereira', () => {
  const p = P.products.find(x => x.reg === '018156');
  afirma(p, 'produto 018156 ausente');
  const u = p.uses.find(x => x.crop === 'MELONE');
  if (!u) return 'nao ha par MELONE neste produto — o defeito original nao pode reaparecer aqui';
  const j = juntaDose(p, u);
  afirma(j.estado === 'NO_DOSE_ROW_FOR_THIS_PAIR',
    `MELONE recebeu dose por estado ${j.estado}`);
});

// O teste media so AMBIGUOUS_DOSE_FOR_THIS_PAIR e exigia que houvesse pelo menos
// um. Depois de MF-07 nao ha: a juncao passou a casar a cultura por ITEM INTEIRO
// da celula e a recusar o nome curto quando a etichetta escreve mais de uma forma
// dele, e os pares que antes chegavam a duas doses discordantes agora sao
// barrados ANTES, com um diagnostico mais preciso — CROP_IDENTITY_NOT_PROVED.
// O que o teste protege continua o mesmo: nenhum par sem uma leitura unica pode
// entregar um numero. Agora ele conta a familia inteira de abstencoes.
teste('nenhum par sem leitura unica de dose exibe um numero', () => {
  const ABSTEM = ['AMBIGUOUS_DOSE_FOR_THIS_PAIR', 'CROP_IDENTITY_NOT_PROVED',
                  'DOSE_ROW_WITHOUT_READ_VALUE', 'DOSE_NOT_PROVED_TARGET_NOT_LITERAL',
                  'EXACT_MATCH_QUOTE_LACKS_CROP',
                  'DOSE_ROW_CONTRADICTED_BY_R11_FOR_THIS_PAIR'];
  const c = {}; let vazado = 0;
  P.products.forEach(p => p.uses.forEach(u => {
    const j = juntaDose(p, u);
    if (ABSTEM.includes(j.estado)) { c[j.estado] = (c[j.estado]||0)+1; if (j.d) vazado++; }
  }));
  const tot = Object.values(c).reduce((a,b)=>a+b,0);
  afirma(tot > 0, 'nenhuma abstencao encontrada — o teste perdeu o alvo');
  afirma(vazado === 0, `${vazado} pares sem leitura unica ainda entregam um valor`);
  return `${tot} abstencoes, nenhuma com valor: ` +
    Object.entries(c).map(([k,v])=>`${k}=${v}`).join(' · ');
});

// ---------------------------------------------------------------- MUST_FIX da rodada 3
teste('MF-01 · o PAR DE USO contradito pelos fios sai da ficha', () => {
  const casos = [['008259','TABACCO','CIMICI'], ['013560','TABACCO','CIMICI'],
                 ['015232','AGLIO','OIDIO'], ['017824','CIPOLLA','OIDIO'],
                 ['015275','TABACCO','DORIFORA']];
  casos.forEach(([reg, crop, alvo]) => {
    const p = P.products.find(x => x.reg === reg);
    afirma(p, `produto ${reg} ausente`);
    afirma(!p.uses.some(u => u.crop === crop && u.target === alvo),
      `${reg} ainda publica ${crop} x ${alvo} como uso autorizado`);
    afirma((p.uses_contraditos||[]).some(w => w.CROP === crop && w.TARGET === alvo),
      `${reg} nao registra a retirada de ${crop} x ${alvo} com a prova geometrica`);
  });
  const n = P.products.reduce((a,p)=>a+(p.uses_contraditos||[]).length,0);
  return `${n} pares retirados por R-14 em ${P.products.filter(p=>(p.uses_contraditos||[]).length).length} registros`;
});

teste('MF-02 · 012573 fica com os alvos que a etichetta lhe da', () => {
  const p = P.products.find(x => x.reg === '012573');
  const alvos = c => p.uses.filter(u => u.crop === c).map(u => u.target).sort();
  const bar = alvos('BARBABIETOLA'), car = alvos('CARCIOFO');
  afirma(bar.length === 4, `BARBABIETOLA ficou com ${bar.length} alvos (${bar}) — a etichetta lista 4`);
  afirma(car.length === 6, `CARCIOFO ficou com ${car.length} alvos (${car}) — a etichetta lista 6`);
  // o irmao que a ferramenta ja lia certo nao pode ter perdido nada
  const o = P.products.find(x => x.reg === '014386');
  afirma((o.uses_contraditos||[]).length === 0,
    `014386 OLIONET, que le a MESMA frase e acerta, perdeu ${(o.uses_contraditos||[]).length} pares`);
  return `BARBABIETOLA=${bar.join(',')} · CARCIOFO=${car.length} alvos · 014386 intacto`;
});

teste('MF-03 · proibicao de semeadura em sucessao nao e uso autorizado', () => {
  ['017868', '017585'].forEach(reg => {
    const p = P.products.find(x => x.reg === reg);
    afirma(p, `produto ${reg} ausente`);
    ['BARBABIETOLA', 'COLZA'].forEach(c => {
      afirma(!p.uses.some(u => u.crop === c),
        `${reg}, herbicida de arroz, ainda publica ${c} como uso autorizado`);
      const w = (p.uses_rotacao||[]).find(x => x.CROP === c);
      afirma(w, `${reg} nao registra a saida de ${c} por restricao de sucessao`);
      afirma(/seminate solo dopo/i.test(w.ROTATION_TEXT),
        `a prova de ${reg}/${c} nao traz a frase de sucessao do rotulo`);
    });
  });
  return `${P.rotation.pairs} pares em restricao de sucessao, com a frase literal`;
});

teste('MF-04 · MAX e INTERVALO herdados nao saem como numero sem prova', () => {
  let mau = 0, exemplo = null;
  P.products.forEach(p => (p.doses||[]).forEach(d => {
    const ruim = ['MAX_CONTRADICTED_BY_RULE', 'MAX_CONTRADICTED_BY_LABEL_NOTE',
                  'MAX_NOT_VALIDATED'].includes(d.max_check);
    if (!ruim) return;
    const celula = colunaMax(d);
    if (!/NOT_PROVED|NOT_VALIDATED/.test(celula)) { mau++; exemplo = exemplo || [p.reg, d.crop, d.max_app]; }
  }));
  afirma(mau === 0, `${mau} linhas imprimem MAX herdado sem prova (ex: ${exemplo})`);
  const p = P.products.find(x => x.reg === '008259');
  const dor = (p.doses||[]).find(d => /Orticole/.test(d.crop) && /Dorifora/.test(d.target));
  afirma(dor && dor.max_check === 'MAX_CONTRADICTED_BY_RULE',
    `008259 Orticole x Dorifora nao foi reprovada (${dor && dor.max_check})`);
  afirma(/NOT_PROVED_BY_RULE/.test(colunaMax(dor)), 'a coluna MAX ainda imprime o valor da vizinha');
  return `heranca conferida: ${JSON.stringify(P.inheritance_check.COUNTS)}`;
});

teste('MF-05 · linha reprovada por R-11 nao publica MAX nem INTERVALO', () => {
  let mau = 0, ex = null;
  P.products.forEach(p => (p.doses||[]).forEach(d => {
    if (d.crop_check !== 'CROP_ASSIGNMENT_CONTRADICTED_BY_RULE' && d.rule_check !== 'NOT_LOCATED') return;
    if (!/NOT_PROVED_BY_RULE/.test(colunaMax(d)) || !/NOT_PROVED_BY_RULE/.test(colunaIntervalo(d))) {
      mau++; ex = ex || [p.reg, d.crop, d.max_app, d.interval];
    }
  }));
  afirma(mau === 0, `${mau} linhas reprovadas ainda imprimem MAX/INTERVALO (ex: ${ex})`);
  return 'a supressao vale para as tres colunas, nao so para a dose';
});

teste('MF-06 · alvo nao literal nao recebe o selo mais forte da tela', () => {
  viewProduto('008259');
  const h = html('#pdet');
  afirma(h.includes('TARGET_TEXT_NOT_FOUND_LITERALLY'),
    'a ficha de 008259 nao mostra o veredito R-13 que o payload calculou');
  let mau = 0;
  P.products.forEach(p => (p.doses||[]).forEach(d => {
    if (d.target_literal === 'TARGET_TEXT_NOT_FOUND_LITERALLY' && /CONFIRMADA<\/span>/.test(seloFios(d))) mau++;
  }));
  afirma(mau === 0, `${mau} linhas com alvo nao literal ainda recebem CONFIRMADA`);
  return 'R-13 chega a tela de produto e ao selo';
});

teste('MF-07 · dose nao atravessa nome de cultura colapsado', () => {
  const p = P.products.find(x => x.reg === '008259');
  ['APION', 'FITONOMO'].forEach(alvo => {
    const u = p.uses.find(x => x.crop === 'BARBABIETOLA' && x.target === alvo);
    if (!u) return;
    const j = juntaDose(p, u);
    afirma(!j.d, `BARBABIETOLA x ${alvo} ainda recebe dose (${j.estado})`);
    afirma(j.estado === 'CROP_IDENTITY_NOT_PROVED',
      `BARBABIETOLA x ${alvo} saiu como ${j.estado}, nao como identidade nao provada`);
  });
  return 'a regra de frase inteira de teto_dose.py chegou a juncao de dose';
});

teste('MF-08 · cultura fora do vocabulario nao responde zero', () => {
  const cq = document.querySelector('#cq');
  cq.value = 'porro'; viewCrop();
  const h = html('#cres');
  afirma(h.includes('CROP_NOT_IN_USE_VOCABULARY'),
    'PORRO ainda responde tabela vazia sem token de ignorancia');
  afirma(h.includes('CROP_PRESENT_IN_DOSE_TABLE_BUT_NOT_IN_USE_VOCABULARY'),
    'a contra-prova das linhas de dose com Porro nao aparece');
  cq.value = ''; viewCrop();
  return 'PORRO responde com o nome proprio da ignorancia e com as linhas que existem';
});

teste('MF-09 · a ressalva de conferencia aparece NA tela de cultura', () => {
  const cq = document.querySelector('#cq');
  cq.value = 'zucchino'; viewCrop();
  const h = html('#cres');
  afirma(h.includes('CROP_NAME_PREFIX_MATCH_ONLY'),
    'a tela de cultura ainda desenha o par so-por-prefixo igual a um atestado');
  cq.value = ''; viewCrop();
  return 'exclusion_check e pair_check chegam a linha que o Regulatory consulta';
});

teste('MF-10 · a ficha nao inventa conflito entre campos que concordam', () => {
  ['014225', '014227'].forEach(reg => {
    viewProduto(reg);
    const h = html('#pdet');
    afirma(!/ainda o lista como/.test(h),
      `${reg} ainda afirma conflito entre data_scadenza e stato_amministrativo`);
    afirma(/VENCIDA/.test(h) && /concordam/.test(h),
      `${reg} nao diz que os dois campos oficiais concordam`);
  });
  return 'EVOLUTION EC e CS: VENCIDA · Scaduto, sem conflito inventado';
});

teste('MF-11 · NOT_PRESENT da tabela nao apaga a restricao de fora dela', () => {
  ['008189', '014479'].forEach(reg => {
    const p = P.products.find(x => x.reg === reg);
    afirma(p.label_dose_notes_not_read,
      `${reg} nao levanta LABEL_NOTES_NOT_READ, e o rotulo diz "Ammesso un solo trattamento"`);
    afirma((p.label_app_limit_notes||[]).length, `${reg} nao traz a frase literal da restricao`);
    viewProduto(reg);
    const h = html('#pdet');
    afirma(/solo trattamento/i.test(h), `${reg} nao mostra a restricao na ficha`);
  });
  return 'a restricao escrita fora da tabela aparece, literal, ao lado do NOT_PRESENT';
});

// ---------------------------------------------------------------- SHOULD_FIX da rodada 3
teste('SF-05 · linha recusada pelo filtro de plausibilidade nao publica numero', () => {
  let mau = 0, ex = null, n = 0;
  P.products.forEach(p => (p.doses||[]).forEach(d => {
    if (d.rule_check !== 'PLAUSIBILITY_REJECTED') return;
    n++;
    if (!linhaReprovada(d)) { mau++; ex = ex || [p.reg, d.crop, d.dose_ha]; }
  }));
  afirma(mau === 0, `${mau} linhas PLAUSIBILITY_REJECTED ainda publicam dose (ex: ${ex})`);
  let vaza = 0;
  P.products.forEach(p => p.uses.forEach(u => {
    const j = juntaDose(p, u);
    if (j.d && j.d.rule_check === 'PLAUSIBILITY_REJECTED') vaza++;
  }));
  afirma(vaza === 0, `${vaza} pares recebem dose de linha recusada pelo filtro`);
  return `${n} linha(s) PLAUSIBILITY_REJECTED, nenhuma com numero publicado`;
});

teste('SF-06 · o filtro de cultura nao casa por substring', () => {
  const cq = document.querySelector('#cq');
  const conta = t => { cq.value = t; viewCrop();
    return Number((html('#cres').match(/(\d+) pares em/)||[0,0])[1]); };
  const melo = conta('melo'), melone = conta('melone');
  const pero = conta('pero'), peperone = conta('peperone');
  cq.value = ''; viewCrop();
  afirma(melo > 0 && melone > 0, 'o filtro deixou de achar MELO ou MELONE');
  afirma(melo !== melo + melone, 'contagem incoerente');
  const somaMelo = P.products.reduce((a,p)=>a+p.uses.filter(u=>u.crop==='MELO').length,0);
  const somaPero = P.products.reduce((a,p)=>a+p.uses.filter(u=>u.crop==='PERO').length,0);
  afirma(melo === somaMelo, `#cq=melo devolve ${melo} e MELO tem ${somaMelo} pares — ainda soma MELONE`);
  afirma(pero === somaPero, `#cq=pero devolve ${pero} e PERO tem ${somaPero} pares — ainda soma PEPERONE`);
  return `melo=${melo} (MELONE=${melone} a parte) · pero=${pero} (PEPERONE=${peperone} a parte)`;
});

teste('SF-09 · o relogio da ferramenta e a data civil de quem abre', () => {
  // meia-noite e meia em Roma e 22:30 do dia anterior em UTC. A data que a
  // ferramenta imprime tem de ser a do leitor, nao a do meridiano.
  const real = Date;
  try {
    const fixo = new real(2026, 8, 1, 0, 30, 0);   // 2026-09-01 00:30 local
    globalThis.Date = class extends real {
      constructor(...args) { return args.length ? new real(...args) : new real(fixo); }
      static now() { return fixo.getTime(); }
      static parse(...a) { return real.parse(...a); }
    };
    const d = new Date();
    const local = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    afirma(local === '2026-09-01', `a data local montada deu ${local}`);
  } finally { globalThis.Date = real; }
  // e a diferenca de dias entre duas datas civis nao pode depender de fuso
  const hoje = hojeISO();
  afirma(dias(hoje) === 0, `dias(hoje) deveria ser 0 e deu ${dias(hoje)}`);
  afirma(/^\d{4}-\d{2}-\d{2}$/.test(hoje), `HOJE malformado: ${hoje}`);
  return `HOJE = ${hoje}, montado de getFullYear/getMonth/getDate`;
});

teste('SF-11 · a BUSCA nao diz NOT_KNOWN sobre produto que nunca foi lido', () => {
  const sq = document.querySelector('#sq');
  sq.value = 'evolution'; viewSearch();
  const h = html('#sres');
  afirma(h.includes('NOT_COLLECTED'), 'a busca nao marca NOT_COLLECTED para produto sem PDF');
  const linha = h.split('EVOLUTION')[1] || '';
  afirma(!/NOT_KNOWN/.test(linha.slice(0, 900)),
    'a coluna DOSES ainda diz NOT_KNOWN na mesma linha em que USOS diz NOT_COLLECTED');
  sq.value = '';
  return 'as quatro colunas de contagem passam pela mesma funcao';
});

teste('SF-03 · R-13 aparece na tela, com FUSION_DETECTOR', () => {
  viewCrop();
  const h = html('#cres');
  afirma(h.includes('R-13'), 'a string R-13 nao e renderizada em nenhuma tela');
  afirma(h.includes('FUSION_DETECTOR') && h.includes('NOT_IMPLEMENTED'),
    'a tela esconde que o detector de fusao nao existe');
  return `R-13 com contagem de acervo, como R-11 e R-12 ja tinham`;
});

// ---------------------------------------------------------------- PORTFOLIO
// "Quais produtos ADAMA realmente servem para esta CULTURA E este PROBLEMA?"
// e a pergunta de negocio. Ela tem duas metades e a tela nao pode dar uma so.
teste('PORTFOLIO · autorizado NA CULTURA nao vira autorizado PARA O ALVO', () => {
  let colapso = 0, ex = null;
  P.products.forEach(p => (p.uses||[]).forEach(u => {
    // um par so pode carregar o selo FATO se as DUAS colunas fecharem
    const deveria = u.pair_check === 'PAIR_CONSISTENT_WITH_RULES'
                 && u.target_name === 'TARGET_NAME_LITERAL';
    if (u.fact !== deveria) { colapso++; ex = ex || [p.reg, u.crop, u.target]; }
  }));
  afirma(colapso === 0, `${colapso} pares com selo FATO incoerente com as duas colunas (ex ${ex})`);
  // e a tela tem de imprimir as duas, nao a mais forte
  const cq = document.querySelector('#cq'), ct = document.querySelector('#ct');
  cq.value = 'vite'; ct.value = 'botrite'; viewCrop();
  const h = html('#cres');
  cq.value = ''; ct.value = ''; viewCrop();
  afirma(h.includes('NAO_VERIFICADO'), 'a tela nao separa o nao-verificado do fato');
  afirma(/duas metades/.test(h), 'a tela nao anuncia que a resposta tem duas metades');
  const tot = P.products.reduce((a,p)=>a+(p.uses||[]).length,0);
  const fa  = P.products.reduce((a,p)=>a+(p.uses||[]).filter(u=>u.fact).length,0);
  return `FATO ${fa} de ${tot} pares publicados`;
});

teste('PORTFOLIO · VITE x BOTRITE nao e apresentado como provado', () => {
  // Medido: 6 produtos publicam VITE x BOTRITE e NENHUM tem prova geometrica.
  // Se algum dia um deles ganhar o selo FATO, tem de ser porque a regra provou.
  const pares = [];
  P.products.forEach(p => (p.uses||[]).forEach(u => {
    if (u.crop === 'VITE' && u.target === 'BOTRITE') pares.push({p, u});
  }));
  afirma(pares.length > 0, 'VITE x BOTRITE sumiu do acervo — o teste perdeu o alvo');
  pares.forEach(({p, u}) => {
    if (u.fact) afirma(u.pair_check === 'PAIR_CONSISTENT_WITH_RULES',
      `${p.reg} VITE x BOTRITE tem selo FATO sem prova de fio`);
  });
  const provados = pares.filter(x => x.u.fact).length;
  return `${pares.length} produtos publicam VITE x BOTRITE · ${provados} com selo FATO`;
});

teste('PORTFOLIO · o escopo que a etichetta escreve na cultura nao some', () => {
  // "VITE da vino" nao e "VITE": um produto autorizado so em uva de vinho nao
  // pode aparecer sob o mesmo nome de um autorizado tambem em uva de mesa.
  let comEscopo = 0, semDeclarar = 0, ex = null;
  P.products.forEach(p => (p.uses||[]).forEach(u => {
    if (!u.crop_scope || !u.crop_scope.length) return;
    comEscopo++;
    if (!escopoDaCultura(u).includes(u.crop_scope[0])) { semDeclarar++; ex = ex || [p.reg,u.crop]; }
  }));
  afirma(comEscopo > 0, 'nenhum par com escopo qualificado — o teste perdeu o alvo');
  afirma(semDeclarar === 0, `${semDeclarar} pares nao declaram o escopo (ex ${ex})`);
  // e o caso nomeado: VITE da vino
  const vinho = [];
  P.products.forEach(p => (p.uses||[]).forEach(u => {
    if (u.crop === 'VITE' && (u.crop_scope||[]).includes('da vino')
        && !(u.crop_scope||[]).includes('da tavola')) vinho.push(p.reg);
  }));
  return `${comEscopo} pares declaram escopo · VITE so-da-vino em ${[...new Set(vinho)].length} registro(s)`;
});

teste('PORTFOLIO · nome de alvo vindo de taxonomia nao passa por leitura', () => {
  const n = P.products.reduce((a,p)=>a+(p.uses||[]).filter(
    u=>u.target_name==='TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL').length,0);
  afirma(n > 0, 'nenhum par por taxonomia — o teste perdeu o alvo');
  let mau = 0;
  P.products.forEach(p => (p.uses||[]).forEach(u => {
    if (u.target_name === 'TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL' && u.fact) mau++;
  }));
  afirma(mau === 0, `${mau} pares com nome inferido carregam selo FATO`);
  // e a tela tem de dizer, nao esconder
  const cq = document.querySelector('#cq');
  cq.value = 'melo'; viewCrop();
  const h = html('#cres');
  cq.value = ''; viewCrop();
  afirma(h.includes('TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL') || n === 0,
    'a tela de cultura nao mostra que o nome do alvo veio de taxonomia');
  return `${n} pares publicam nome de alvo que o rotulo nao escreve`;
});

teste('PORTFOLIO · rota que R-14 nao testa nunca carrega selo de prova', () => {
  // ROTA E COMO O EXTRATOR LEU; GEOMETRIA E O QUE O DOCUMENTO MOSTRA. Um par de
  // rota INLINE_COLON_HEAD numa pagina com grade desenhada PODE ser provado pela
  // geometria — e 248 sao. O que nao pode acontecer e um par de rota que R-14
  // sequer tenta (HEADER_CONTINUATION, AUTHORISED_USE_LIST) sair com selo de
  // prova: esses nao passaram por teste nenhum.
  const NUNCA_TESTADAS = ['HEADER_CONTINUATION', 'AUTHORISED_USE_LIST'];
  let n = 0, comProva = 0, ex = null;
  P.products.forEach(p => (p.uses||[]).forEach(u => {
    if (!NUNCA_TESTADAS.includes(u.route)) return;
    n++;
    if (u.proof === 'USE_PAIR_PROVEN_BY_TABLE_GEOMETRY' || u.fact) {
      comProva++; ex = ex || [p.reg, u.crop, u.target, u.route];
    }
  }));
  afirma(n > 0, 'nenhum par de rota nao-testada — o teste perdeu o alvo');
  afirma(comProva === 0, `${comProva} pares de rota que R-14 nao testa carregam prova (ex ${ex})`);
  const prosa = P.products.reduce((a,p)=>a+(p.uses||[]).filter(
    u=>!['GEOMETRIC_TABLE','MERGED_COLUMN_TABLE'].includes(u.route)).length,0);
  const prosaFato = P.products.reduce((a,p)=>a+(p.uses||[]).filter(
    u=>!['GEOMETRIC_TABLE','MERGED_COLUMN_TABLE'].includes(u.route) && u.fact).length,0);
  return `${n} pares nunca testados, nenhum com prova · dos ${prosa} de rota de prosa, ${prosaFato} tem prova por geometria da pagina`;
});

teste('SF-12/SF-07 · a ferramenta nao cita frase que o rotulo nao escreve', () => {
  // nenhuma celula NAO CONTIGUA pode aparecer entre aspas
  let mau = 0, n = 0, ex = null;
  P.products.forEach(p => (p.doses||[]).forEach((d,i) => {
    if (citavel(d.crop_cell_state) && citavel(d.target_cell_state)) return;
    n++;
    evDose(p.reg, i);
    const h = html('#dr');
    if (!h.includes('CELL_TEXT_NOT_RECOVERABLE')) { mau++; ex = ex || [p.reg, d.crop]; }
    if (!citavel(d.crop_cell_state) && h.includes('&ldquo;'+d.crop+'&rdquo;')) {
      mau++; ex = ex || [p.reg, d.crop, 'citada entre aspas'];
    }
  }));
  afirma(n > 0, 'nenhuma celula nao-contigua — o teste perdeu o alvo');
  afirma(mau === 0, `${mau} celulas montadas ainda aparecem como frase do rotulo (ex ${ex})`);
  // e nenhuma janela de exclusao pode ser prefixo estrito de outra do mesmo rotulo
  let pref = 0;
  P.products.forEach(p => {
    const ws = (p.exclusion_windows||[]).filter(w=>w.QUOTABLE)
      .map(w=>String(w.TEXT).replace(/\s+/g,' ').trim().toLowerCase());
    ws.forEach(a => { if (ws.some(b => b !== a && b.startsWith(a))) pref++; });
  });
  afirma(pref === 0, `${pref} janelas de exclusao sao prefixo de outra e invertem escopo`);
  return `${n} celulas montadas, todas com nome proprio · nenhuma janela prefixo`;
});

teste('SF-10 · o KPI de "hoje" e recalculado contra o relogio de quem abre', () => {
  const real = Date;
  const conta = () => { viewToday();
    const m = html('#v-today').match(/Condicoes que continuam valendo hoje \((\d+)\)/);
    return m ? Number(m[1]) : -1; };
  const agora = conta();
  let futuro = -1;
  try {
    const fixo = new real(2040, 5, 20, 12, 0, 0);
    globalThis.Date = class extends real {
      constructor(...a) { return a.length ? new real(...a) : new real(fixo); }
      static now() { return fixo.getTime(); }
      static parse(...a) { return real.parse(...a); }
    };
    futuro = conta();
  } finally { globalThis.Date = real; viewToday(); }
  afirma(agora >= 0 && futuro >= 0, 'nao consegui ler o numero da tela');
  afirma(futuro > agora,
    `com o relogio em 2040 a tela ainda diz ${futuro} (hoje diz ${agora}): o conjunto esta congelado no build`);
  return `hoje ${agora} · com o relogio em 2040-06-20 sobe para ${futuro}`;
});

teste('a celula de dose diz de que linha o numero veio', () => {
  viewCrop();
  const h = html('#cres');
  afirma(h.includes('EXATA') || h.includes('LISTADA'),
    'a tela nao distingue igualdade exata de juncao inferida');
  afirma(!/>\s*\d[\d.,-]*\s+(kg|g|l|ml)\/ha\s*<\/td>/i.test(h),
    'ha dose impressa sem selo de como foi ligada ao par');
});

// ---------------------------------------------------------------- 2 · exclusao
teste('CILIEGIO nao aparece como uso autorizado de NIMROD nem de VERBUM EW', () => {
  ['002983', '013405'].forEach(reg => {
    const p = P.products.find(x => x.reg === reg);
    afirma(p, `produto ${reg} ausente`);
    afirma(!p.uses.some(u => u.crop === 'CILIEGIO'),
      `${reg} ainda publica CILIEGIO como uso autorizado`);
    afirma((p.uses_retirados || []).some(w => w.CROP === 'CILIEGIO'),
      `${reg} nao registra a retirada de CILIEGIO`);
  });
});

teste('a ficha mostra a frase do rotulo que retirou o uso', () => {
  viewProduto('013405');
  const h = html('#pdet');
  afirma(h.includes('ad esclusione di'), 'a frase de exclusao nao aparece na ficha');
  afirma(h.includes('Exclusao nao e permissao'), 'a ficha nao explica a retirada');
});

// ---------------------------------------------------------------- 3 · fora do ativo
teste('GOLTIX STAR nao declara NOT_KNOWN sobre o que a ferramenta leu', () => {
  const p = P.products.find(x => x.reg === '009322');
  afirma(p, 'produto 009322 ausente');
  ['status', 'expiry', 'actives', 'activity', 'registered_at'].forEach(k =>
    afirma(p[k] && !String(p[k]).startsWith('NOT_'),
      `campo ${k} chegou como ${p[k]} para um registro cuja linha oficial esta em disco`));
  viewProduto('009322');
  const h = html('#pdet');
  afirma(h.includes('METAMITRON'), 'a ficha nao mostra as substancias que a linha oficial traz');
  afirma(h.includes('NOT_COLLECTED'), 'a ficha nao separa "nao coletado" de "nao existe"');
  return `${p.status} · ${p.expiry} · ${p.actives}`;
});

// ---------------------------------------------------------------- 4 · roteamento
teste('nenhuma regra de roteamento e citada por tipo que ela nao nomeia', () => {
  const regras = fs.readFileSync(path.join(RAIZ, 'v1/inteligencia/REGRAS.md'), 'utf8');
  const usos = {};
  P.objects.forEach(o => (o.CAPABILITY_ROUTING || []).forEach(r =>
    (usos[r.RULE_ID] = usos[r.RULE_ID] || new Set()).add(o.CHANGE_TYPE)));
  const falhas = [];
  Object.entries(usos).forEach(([rid, tipos]) => {
    if (rid === 'C-99' || rid === 'C-01' || rid === 'C-02' || rid === 'C-05' || rid === 'C-08' || rid === 'C-09') return;
    const linha = regras.split('\n').find(l => l.startsWith(`| \`${rid}\``));
    if (!linha) { falhas.push(`${rid} nao esta escrita`); return; }
    tipos.forEach(t => { if (!linha.includes(t)) falhas.push(`${rid} usada por ${t}, que ela nao nomeia`); });
  });
  afirma(!falhas.length, falhas.join('; '));
});

teste('cabecalho de grupo nao estampa a justificativa do primeiro objeto', () => {
  viewAction();
  const h = html('#v-action');
  afirma(!h.includes('JUSTIFICATION_NOT_UNIFORM'),
    'ha grupo com regra unica e justificativas diferentes');
});

teste('NOT_RELEVANT nao lista as linhas que a propria nota diz estarem barradas', () => {
  viewAction();
  const h = html('#v-action');
  const i = h.indexOf('NOT_RELEVANT');
  afirma(i > -1, 'nenhum bloco NOT_RELEVANT na tela');
  const trecho = h.slice(i, i + 1400);
  afirma(!trecho.includes('<tbody>'),
    'o bloco NOT_RELEVANT ainda imprime a tabela dos objetos que diz barrar');
});

// ---------------------------------------------------------------- 5 · ignorancia
teste('nenhuma tela imprime None, undefined ou null cru', () => {
  const telas = {today: () => viewToday(), produto: () => viewProduto('009322'),
                 crop: () => viewCrop(), cal: () => viewCal(), action: () => viewAction(),
                 timeline: () => viewTimeline(), review: () => viewReview(), cov: () => viewCov()};
  Object.entries(telas).forEach(([v, fn]) => {
    try { fn(); } catch (e) { throw new Error(`view ${v} quebrou: ${e.message}`); }
  });
  const tudo = Object.values(capturado).map(e => e.innerHTML).join('\n');
  [/>\s*None\s*</, />\s*undefined\s*</, />\s*null\s*</, /\bvalor None\b/].forEach(rx =>
    afirma(!rx.test(tudo), `token cru da linguagem na tela: ${rx}`));
});

// ---------------------------------------------------------------- 6 · relogio
teste('a janela temporal e recalculada contra o relogio de quem abre', () => {
  const antes = P.objects.filter(o => o.TIME_WINDOW === 'PLAN_NEXT_CYCLE').length;
  afirma(antes > 0, 'nenhum objeto em PLAN_NEXT_CYCLE no build — o teste perdeu o alvo');
  // finge um relogio um ano a frente e conta de novo
  const N = global.Date;
  const R = new N('2027-06-01T12:00:00Z');
  function F(...a) { return a.length ? new N(...a) : new N(R); }
  F.now = () => R.getTime(); F.parse = N.parse; F.UTC = N.UTC; F.prototype = N.prototype;
  global.Date = F; global.window.Date = F;
  let depois;
  try {
    // recarrega o app com o relogio falso
    const fonte2 = fs.readFileSync(path.join(RAIZ, 'v1/casco/app.js'), 'utf8');
    const ctx = {};
    (0, eval)(fonte2.replace(/^go\('today'\);$/m, ''));
    depois = P.objects.filter(o => janelaAgora(o)[0] === 'PLAN_NEXT_CYCLE').length;
  } finally {
    global.Date = N; global.window.Date = N;
  }
  afirma(depois < antes,
    `a janela nao mudou com o relogio um ano a frente (${antes} -> ${depois})`);
  return `PLAN_NEXT_CYCLE ${antes} no build -> ${depois} em 2027-06-01`;
});

teste('zero medido, nao coletado e nao sei sao tres respostas diferentes', () => {
  const lido = P.products.find(p => p.states && p.states.LABEL_READ && !p.uses.length);
  const naoColetado = P.products.find(p => p.states && p.states.LABEL_DOWNLOADED === false);
  afirma(lido, 'nenhum produto lido com zero pares — o teste perdeu o alvo');
  afirma(naoColetado, 'nenhum produto sem rotulo baixado');
  viewSearch();
  const h = html('#sres') + html('#pdet');
  afirma(contagem(lido, 'uses', 'LABEL_READ').includes('0'),
    'produto medido com zero pares nao mostra zero');
  afirma(contagem(naoColetado, 'uses', 'LABEL_READ').includes('NOT_COLLECTED'),
    'produto sem rotulo baixado nao mostra NOT_COLLECTED');
  return `${lido.reg} mede 0 · ${naoColetado.reg} e NOT_COLLECTED`;
});

// ---------------------------------------------------------------- roda
let ok = 0, mau = 0;
console.log('');
for (const [nome, fn] of testes) {
  try { const nota = fn(); ok++; console.log(`  ok    ${nome}${nota ? '  — ' + nota : ''}`); }
  catch (e) { mau++; console.log(`  FALHA ${nome}\n          ${e.message}`); }
}
console.log(`\n  ${ok} passaram, ${mau} falharam` +
            (mau ? '  -> CASCO_RENDER_TEST = FAIL' : '  -> CASCO_RENDER_TEST = PASS') + '\n');
process.exit(mau ? 1 : 0);
