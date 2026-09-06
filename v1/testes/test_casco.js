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
