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
                  'MAX_NOT_PROVED_NOTE_BLOCK_UNKNOWN',
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

teste('SF-16 · NOT_PRESENT nao diz "nao declara" onde o rotulo declara', () => {
  // R-19 · 112 rotulos escrevem "con validita dal <data>" e a ficha dizia
  // NOT_PRESENT, que se le "o rotulo nao declara vigencia".
  const naoLidos = P.products.filter(p => p.label_validity_state === 'VALIDITY_PHRASE_PRESENT_FORM_NOT_READ');
  afirma(naoLidos.length > 0, 'nenhum rotulo com forma nao lida — o teste perdeu o alvo');
  const p0 = naoLidos[0];
  viewProduto(p0.reg);
  const h = html('#pdet');
  afirma(h.includes('VALIDITY_PHRASE_PRESENT_FORM_NOT_READ'),
    `${p0.reg} nao mostra que a forma de vigencia nao foi lida`);
  afirma(h.includes('PARSER_FAILURE'), 'a ficha nao nomeia a lei que isto viola');
  naoLidos.forEach(p => afirma(p.label_validity_literal && p.label_validity_literal.length > 10,
    `${p.reg} declara vigencia e nao traz a frase literal`));
  return `${naoLidos.length} rotulos declaram vigencia em forma nao estruturada, todos com a frase`;
});

teste('SF-16 · CAPTURED_AT e a captura, nao a data em que a regra rodou', () => {
  const byReg2 = Object.fromEntries(P.products.map(p => [p.reg, p]));
  const exp = P.objects.filter(o => o.OBJECT_TYPE === 'EXPIRY_EVENT');
  afirma(exp.length > 0, 'nenhum EXPIRY_EVENT — o teste perdeu o alvo');
  let mau = 0, semRegra = 0;
  exp.forEach(o => {
    const p = byReg2[o.REGISTRATION_ID];
    if (p && p.captured_at && o.CAPTURED_AT !== p.captured_at) mau++;
    if (!o.RULE_EVALUATED_AT || o.RULE_EVALUATED_AT === 'NOT_APPLICABLE') semRegra++;
  });
  afirma(mau === 0, `${mau} EXPIRY_EVENT com CAPTURED_AT diferente da captura real do produto`);
  afirma(semRegra === 0, `${semRegra} EXPIRY_EVENT sem RULE_EVALUATED_AT`);
  // e uma data so pode ter um formato na mesma tela
  const fmt = new Set(P.objects.map(o => String(o.DETECTED_AT))
    .filter(d => d !== 'NOT_KNOWN')
    .map(d => /^\d{8}$/.test(d) ? 'AAAAMMDD' : /^\d{4}-\d{2}-\d{2}$/.test(d) ? 'ISO' : 'outro'));
  afirma(fmt.size <= 1, `DETECTED_AT em ${fmt.size} formatos: ${[...fmt]}`);
  return `${exp.length} EXPIRY_EVENT com captura real e RULE_EVALUATED_AT proprio · DETECTED_AT num formato so`;
});

teste('SF-14 · a cobertura por celula desenhada aparece ao lado da por rotulo', () => {
  const c = P.coverage_crop_cell || {};
  afirma(c.CROP_CELLS_DETECTED > 0, 'cobertura por celula nao foi medida');
  afirma(c.CROP_CELLS_READ < c.CROP_CELLS_DETECTED,
    'a cobertura por celula seria 100%, o que nao bate com o vocabulario fechado');
  go('cov');
  const h = html('#v-cov');
  afirma(h.includes('CROP_BLOCK_NOT_COLLECTED'), 'a tela nao mostra o bloco nao coletado');
  afirma(h.includes('CELULA DE CULTURA DESENHADA'), 'a tela nao declara o segundo denominador');
  afirma(h.includes('piso'), 'a tela nao diz que a diferenca e um piso e nao o total');
  // as duas coberturas tem de conviver — numero unico foi o defeito da rodada 1
  afirma(h.includes(String(P.coverage.AUTHORIZED_USE_ROW_COVERAGE.COVERED)),
    'a cobertura por rotulo sumiu da tela');
  return `${c.CROP_CELLS_READ}/${c.CROP_CELLS_DETECTED} celulas (${c.PCT}%) contra ${P.coverage.AUTHORIZED_USE_ROW_COVERAGE.PCT}% por rotulo`;
});

// ---------------------------------------------------------------- RODADA 4
teste('RT4 · o valor que confirma o MAX tem de ser da MESMA TABELA da linha', () => {
  // Achado BLOCKING da lente D: numa pagina com duas tabelas lado a lado, a
  // celula que CONFIRMAVA o n.max podia estar na OUTRA tabela — mesma altura na
  // folha, tabela diferente. Em 017687 ELTIRA a celula da tabela certa diz 1 e a
  // ferramenta publicava 2 com MAX_CONFIRMED_BY_RULE.
  const p = P.products.find(x => x.reg === '017687');
  afirma(p, '017687 ELTIRA ausente');
  const conf = (p.doses||[]).filter(d => d.max_check === 'MAX_CONFIRMED_BY_RULE').length;
  const contra = (p.doses||[]).filter(d => d.max_check === 'MAX_CONTRADICTED_BY_RULE').length;
  afirma(contra > 0, '017687 nao tem nenhuma linha reprovada — o teste de x nao esta valendo');
  // nenhuma linha reprovada pode imprimir o numero
  let vaza = 0;
  P.products.forEach(q => (q.doses||[]).forEach(d => {
    if (d.max_check === 'MAX_CONTRADICTED_BY_RULE' && !/NOT_PROVED/.test(colunaMax(d))) vaza++;
  }));
  afirma(vaza === 0, `${vaza} linhas reprovadas ainda imprimem o MAX`);
  return `017687: ${conf} confirmadas, ${contra} reprovadas por estarem noutra tabela`;
});

teste('RT4 · nota de aplicacoes so vale para o bloco dela', () => {
  // Achado BLOCKING da lente D: 6 das 9 contradicoes por nota vinham da nota de
  // OUTRO bloco da tabela. A tela nao publicava o numero (lado seguro), mas
  // AFIRMAVA de qual nota se tratava, e a afirmacao podia estar errada.
  const desconhecido = [];
  P.products.forEach(p => (p.doses||[]).forEach(d => {
    if (d.max_check === 'MAX_NOT_PROVED_NOTE_BLOCK_UNKNOWN') desconhecido.push([p.reg, d.crop]);
  }));
  afirma(desconhecido.length > 0, 'nenhuma nota de bloco indeterminado — o teste perdeu o alvo');
  // nem o estado forte nem o fraco podem publicar o numero
  let vaza = 0;
  P.products.forEach(p => (p.doses||[]).forEach(d => {
    if (/NOTE/.test(String(d.max_check)) && !/NOT_PROVED/.test(colunaMax(d))) vaza++;
  }));
  afirma(vaza === 0, `${vaza} linhas com nota contraria ainda publicam o MAX`);
  const forte = P.products.reduce((a,p)=>a+(p.doses||[]).filter(
    d=>d.max_check==='MAX_CONTRADICTED_BY_LABEL_NOTE').length,0);
  return `${forte} contradicoes com bloco estabelecido · ${desconhecido.length} com bloco indeterminado`;
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

teste('RT4 · nome de cultura que o rotulo nao escreve nunca vira FATO', () => {
  // Achado da lente E, reproduzido e depois estendido: 23 pares publicam uma
  // cultura cuja raiz nao existe em palavra nenhuma do documento. O pior deles
  // e CILIEGIO (002983, 013405), tirado de "Pomodoro (ad esclusione di Pomodoro
  // ciliegino)" — nome de arvore extraido de dentro da EXCLUSAO de um tomate.
  // Esses dois NAO estao neste teste porque R-10 ja os retira antes da tela
  // (CROP_ONLY_INSIDE_EXCLUSION); estao conferidos no portao de python.
  const fora = [];
  P.products.forEach(p => (p.uses||[]).forEach(u => {
    if (u.crop_name === 'CROP_NAME_NOT_IN_LABEL') fora.push([p.reg, u.crop, u.target, u.fact]);
  }));
  afirma(fora.length > 0, 'nenhum par com CROP_NAME_NOT_IN_LABEL — o teste perdeu o alvo');
  const vazaram = fora.filter(x => x[3]);
  afirma(vazaram.length === 0,
    `${vazaram.length} pares com nome de cultura ausente do rotulo carregam selo FATO`);
  // e o aviso tem de estar na tela, nao so no payload
  afirma(P.products.some(x => x.reg === '018270'), '018270 ausente');
  viewProduto('018270');
  const h = html('#pdet');
  afirma(h.includes('CROP_NAME_NOT_IN_LABEL'),
    'a ficha de 018270 nao mostra que FAGIOLO nao esta escrito no rotulo');
  // flexao NAO e ausencia: "cavoli" para CAVOLO fecha a coluna
  const flex = P.products.reduce((a,p)=>a+(p.uses||[]).filter(
    u => u.crop_name === 'CROP_NAME_INFLECTED_IN_LABEL').length, 0);
  afirma(flex > 0, 'nenhum par marcado como flexao — a regra virou severa demais');
  return `${fora.length} sem nome no rotulo (nenhum e FATO) · ${flex} so plural italiano`;
});

teste('RT4 · celula fechada pelo TITULO do grupo nao e prova do par', () => {
  // Achado E-01/E-02: 13 pares tinham PAIR_CONSISTENT_WITH_RULES porque a celula
  // desenhada casou pela raiz do CROP_AS_WRITTEN ("ORTICOLE (...)", "Grano tenero
  // e duro") e nao pelo nome da cultura publicada. A geometria provou que o
  // TITULO e o alvo dividem uma celula, e nao que a cultura esta no grupo.
  const pelo = [];
  P.products.forEach(p => (p.uses||[]).forEach(u => {
    if (u.pair_check === 'PAIR_NOT_CHECKABLE_CROP_NAME_NOT_THE_ANCHOR')
      pelo.push([p.reg, u.crop, u.target, u.proof, u.fact]);
  }));
  afirma(pelo.length > 0, 'nenhum par com CROP_NAME_NOT_THE_ANCHOR — o teste perdeu o alvo');
  const provados = pelo.filter(x => x[3] !== 'USE_PAIR_NOT_VERIFIED_BY_ANY_RULE' || x[4]);
  afirma(provados.length === 0,
    `${provados.length} pares ancorados no titulo do grupo ainda carregam prova ou FATO`);
  const regs = [...new Set(pelo.map(x => x[0]))].sort();
  return `${pelo.length} pares em ${regs.length} rotulos (${regs.slice(0,4).join(', ')})`;
});

teste('RT4 · alvo que ja tem dono geometrico nao sobrevive por ocorrencia solta', () => {
  // Achado SERIOUS da lente F: 018067 MAXENTIS e 019095 KOJAMI publicavam
  // SEGALE x OIDIO. A tabela desenhada empilha ORZO (que tem OIDIO), depois
  // SEGALE (que tem so Rincosporiosi e Ruggine). O par sobrevivia porque a
  // palavra "segale" tambem aparece na LINHA DE TITULO do produto, fora de
  // celula nenhuma — e a abstencao EVIDENCIA MISTA dizia "a autorizacao pode
  // estar la". Nao podia: os dois glifos de OIDIO ja moram em celula de outra
  // cultura.
  ['018067', '019095'].forEach(reg => {
    const p = P.products.find(x => x.reg === reg);
    afirma(p, `${reg} ausente`);
    const alvos = (p.uses||[]).filter(u => u.crop === 'SEGALE').map(u => u.target).sort();
    afirma(!alvos.includes('OIDIO'),
      `${reg} ainda publica SEGALE x OIDIO como uso autorizado`);
    afirma(alvos.length === 2,
      `${reg}: SEGALE devia ficar com os 2 alvos da celula dele, tem ${alvos.length}`);
    const w = (p.uses_contraditos||[]).find(y => y.CROP === 'SEGALE' && y.TARGET === 'OIDIO');
    afirma(w, `${reg} nao lista SEGALE x OIDIO entre os contraditos`);
    afirma(w.MECHANISM === 'TARGET_BELONGS_TO_ANOTHER_CROP_CELL',
      `${reg}: o mecanismo da condenacao nao esta nomeado`);
    viewProduto(reg);
    afirma(html('#pdet').includes('ja tem dono'),
      `${reg} nao mostra a prova de que o alvo tem outro dono`);
  });
  return 'SEGALE fica com RUGGINE e RINCOSPORIOSI, que e o que a celula desenhada diz';
});

teste('RT4 · "sem celula desenhada" nao pode ser dito onde a grade existe', () => {
  // Achado SERIOUS da lente F: em 58 dos 170 PAIR_NOT_CHECKABLE_NO_DRAWN_CELL a
  // coluna da cultura E atravessada por >=3 fios — em 008259 por 15 e 17. A
  // tela afirmava "a coluna da cultura nesta pagina nao tem grade desenhada",
  // uma frase falsa sobre o documento. Token de ignorancia com nome errado
  // parece medicao e nao e.
  const inc = [], sem = [];
  P.products.forEach(p => (p.uses||[]).forEach(u => {
    if (u.pair_check === 'PAIR_NOT_CHECKABLE_TABLE_NOT_DESCRIBING_ITS_TEXT') inc.push([p.reg, u.crop]);
    if (u.pair_check === 'PAIR_NOT_CHECKABLE_NO_DRAWN_CELL') sem.push([p.reg, u.crop]);
  }));
  afirma(inc.length > 0, 'nenhum par com grade incoerente — o estado novo nao esta chegando a tela');
  afirma(sem.length > 0, 'nenhum par sem grade — os dois estados viraram um so');
  const p = P.products.find(x => x.reg === '008259');
  afirma(p, '008259 ausente');
  const pesco = (p.uses||[]).filter(u => u.crop === 'PESCO');
  afirma(pesco.length > 0, '008259 sem pares de PESCO');
  afirma(pesco.every(u => u.pair_check !== 'PAIR_NOT_CHECKABLE_NO_DRAWN_CELL'),
    '008259 PESCO voltou a dizer que a coluna nao tem grade, e ela tem 15 e 17 fios');
  // depois que a linha passou a ser agrupada por banda vertical desenhada, a
  // celula de PESCO ficou coerente e os 5 pares sao PAIR_CONSISTENT — que e uma
  // resposta melhor que a anterior, e nao a mesma com outro nome.
  const reg = inc[0][0];
  viewProduto(reg);
  afirma(html('#pdet').includes('GRADE NAO DESCREVE O TEXTO'),
    `a ficha de ${reg} nao mostra o nome certo da ignorancia`);
  return `${inc.length} com grade que nao descreve o texto · ${sem.length} realmente sem grade`;
});

teste('RT4 · sublinhado de titulo nao e regua de tabela', () => {
  // Achado BLOCKING da lente G: em 016312 TOMIGAN a coluna direita da pagina 1
  // e PROSA com titulos sublinhados. Quatro sublinhados passavam o guarda de 3
  // fios e fabricavam uma celula de 67 pt que engolia SEIS linhas de DOIS
  // blocos; o glifo de "infestanti" que provava o par era o do bloco
  // POMACEE/DRUPACEE, nao o do bloco FRUTTIFERI A GUSCIO logo abaixo. MANDORLO
  // x INFESTANTI e NOCE x INFESTANTI saiam com selo verde e fact=true. O par e
  // verdadeiro; a PROVA era falsa — com a mesma geometria o selo sairia igual
  // se a etichetta nao autorizasse.
  const p = P.products.find(x => x.reg === '016312');
  afirma(p, '016312 ausente');
  ['MANDORLO', 'NOCE'].forEach(c => {
    const u = (p.uses||[]).find(y => y.crop === c && y.target === 'INFESTANTI');
    afirma(u, `016312 sem o par ${c} x INFESTANTI`);
    afirma(!u.fact, `016312 ${c} x INFESTANTI ainda sai como FATO`);
    afirma(u.pair_check === 'PAIR_NOT_CHECKABLE_RULES_ARE_TEXT_UNDERLINES',
      `016312 ${c}: o motivo da ignorancia nao e o sublinhado (${u.pair_check})`);
  });
  // e o filtro so pode TIRAR prova, nunca criar: nenhum par de prosa pode ter
  // ganho selo verde por causa dele
  const sub = [];
  P.products.forEach(q => (q.uses||[]).forEach(u => {
    if (u.pair_check === 'PAIR_NOT_CHECKABLE_RULES_ARE_TEXT_UNDERLINES') sub.push([q.reg, u.crop]);
    afirma(!(u.pair_check === 'PAIR_NOT_CHECKABLE_RULES_ARE_TEXT_UNDERLINES' && u.fact),
      `${q.reg} ${u.crop}: sublinhado nao pode sustentar FATO`);
  }));
  afirma(sub.length > 0, 'nenhum par com riscos-sublinhado — o estado nao chega a tela');
  viewProduto('016312');
  afirma(html('#pdet').includes('OS RISCOS SAO SUBLINHADO'),
    'a ficha de 016312 nao diz que os riscos sao sublinhado');
  const regs = [...new Set(sub.map(x => x[0]))].sort();
  return `${sub.length} pares em ${regs.length} rotulos (${regs.join(', ')})`;
});

teste('RT4 · aspas com verbo de citacao so onde R-18 provou a frase', () => {
  // Achado BLOCKING da lente I, em duas partes.
  //
  // (1) O casco lia a lista de citacoes REPROVADAS com default QUOTE_VERBATIM:
  //     ausencia de registro virava afirmacao positiva. As 349 linhas
  //     ROW_RECONSTRUCTED_FROM_CELLS e as 163 QUOTE_TOO_SHORT_TO_CHECK nunca
  //     estiveram na lista e saiam como "Citacao do documento".
  // (2) As 2.873 frases que a tela imprime como "o rotulo escreve" ao lado de
  //     cada par (CROP_AS_WRITTEN, TARGET_AS_WRITTEN) nunca tinham sido
  //     conferidas. Medido: 1.408 e 939 delas nao sao literais.
  const cs = {}, ts = {}, qs = {};
  P.products.forEach(p => {
    (p.uses||[]).forEach(u => {
      cs[u.crop_raw_state] = (cs[u.crop_raw_state]||0)+1;
      ts[u.target_raw_state] = (ts[u.target_raw_state]||0)+1;
    });
    (p.doses||[]).forEach(d => { qs[d.quote_state] = (qs[d.quote_state]||0)+1; });
  });
  afirma(!cs[undefined] && !ts[undefined],
    'ha par de uso sem veredito de citacao para a celula como escrita');
  afirma((cs.QUOTE_CUT_MID_WORD||0) > 0 && (ts.QUOTE_CUT_MID_WORD||0) > 0,
    'nenhuma citacao cortada no meio de palavra — o teste perdeu o alvo');
  afirma(!qs.QUOTE_VERBATIM,
    'alguma linha de dose voltou a dizer que a citacao e literal por default');
  // e a tela: nada que nao seja QUOTE_VERBATIM pode sair com o verbo de citacao
  const norm = z => String(z||'').toLowerCase().replace(/\s+/g,' ').trim();
  const p = P.products.find(x => (x.uses||[]).some(
    u => u.target_raw_state === 'QUOTE_CUT_MID_WORD' && norm(u.target_raw) !== norm(u.target)));
  afirma(p, 'nenhum rotulo com alvo cortado no meio de palavra e texto proprio');
  const sq = document.querySelector('#sq');
  sq.value = p.reg; viewSearch();
  const h = html('#sres');
  sq.value = '';
  afirma(!/o rotulo escreve[^<]*<i>/.test(h) || h.includes('leitura do extrator'),
    'a busca ainda imprime "o rotulo escreve" sobre texto que R-18 nao aprovou');
  return `cultura ${JSON.stringify(cs)} · alvo ${JSON.stringify(ts)}`;
});

teste('RT4 · MOSCA BIANCA nao pode aparecer so como MOSCA', () => {
  // Achado SERIOUS da lente K: em 008259, 013560, 013590, 015275 e 017687 a
  // celula do alvo escreve "mosca bianca" — a mosca-branca — e a tela publicava
  // MOSCA, que em italiano e outro inseto. 85 pares, todos com selo verde. A
  // palavra "mosca" esta escrita, entao R-17 dizia LITERAL e tinha razao; o que
  // faltava dizer e que ela nunca aparece sozinha ali.
  const mb = [];
  P.products.forEach(p => (p.uses||[]).forEach(u => {
    if (u.target === 'MOSCA' && (u.target_scope||[]).includes('bianca')) mb.push(p.reg);
  }));
  afirma(mb.length === 85, `esperava 85 pares MOSCA/bianca, achei ${mb.length}`);
  const p = P.products.find(x => x.reg === '008259');
  viewProduto('008259');
  const h = html('#pdet');
  afirma(h.includes('nunca escreve este alvo sozinho'),
    'a ficha de 008259 nao mostra que a etichetta escreve "mosca bianca"');
  afirma(h.includes('bianca'), 'a palavra do documento nao aparece na tela');
  // e o campo tem de existir em TODOS os usos, nao so nos qualificados
  let semCampo = 0;
  P.products.forEach(q => (q.uses||[]).forEach(u => {
    if (!Array.isArray(u.target_scope)) semCampo++;
  }));
  afirma(semCampo === 0, `${semCampo} usos sem o campo target_scope`);
  const tot = P.products.reduce((a,q)=>a+(q.uses||[]).filter(
    u=>(u.target_scope||[]).length).length,0);
  return `${tot} pares com alvo sempre qualificado · ${mb.length} deles sao "mosca bianca"`;
});

teste('RT4 · numero do outro lado de um risco desenhado nao e dose desta linha', () => {
  // Achado BLOCKING da lente B: em 018270 GLIPHOGAN a dose da linha do MAIS e o
  // unico "1" da regiao e ele esta na linha DEBAIXO, do outro lado do fio. R-22
  // ve isso quando o documento DESENHOU o risco: 29 linhas de dose tem um fio
  // horizontal por dentro da propria banda, com texto dos dois lados.
  const cruz = [];
  P.products.forEach(p => (p.doses||[]).forEach(d => {
    if (d.band_check === 'DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE') cruz.push([p.reg, d.crop, d.dose_ha]);
  }));
  afirma(cruz.length > 0, 'nenhuma linha com risco por dentro da banda — R-22 nao chega a tela');
  // nenhuma delas pode publicar o numero nem o selo forte
  let vaza = 0;
  P.products.forEach(p => (p.doses||[]).forEach(d => {
    if (d.band_check === 'DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE'
        && /CONFIRMADA<\/span>/.test(seloFios(d))) vaza++;
    if (d.band_check === 'DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE' && !linhaReprovada(d)) vaza++;
  }));
  afirma(vaza === 0, `${vaza} linhas com risco por dentro da banda ainda publicam o numero`);
  const reg = cruz.find(x => x[0] === '018270') ? '018270' : cruz[0][0];
  viewProduto(reg);
  afirma(html('#pdet').includes('fio horizontal') || html('#pdet').includes('DOSE_ROW_BAND'),
    `a ficha de ${reg} nao explica por que o numero nao foi publicado`);
  const regs = [...new Set(cruz.map(x => x[0]))].sort();
  return `${cruz.length} linhas em ${regs.length} rotulos (${regs.slice(0,5).join(', ')})`;
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
