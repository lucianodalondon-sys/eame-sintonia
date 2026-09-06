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
global.window = { scrollTo() {}, addEventListener() {} };
global.P = JSON.parse(fs.readFileSync(path.join(RAIZ, 'v1/dados/CASCO-PAYLOAD.json'), 'utf8'));

const fonte = fs.readFileSync(path.join(RAIZ, 'v1/casco/app.js'), 'utf8');
(0, eval)(fonte.replace(/^const P = .*$/m, ''));

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

teste('nenhum par com >=2 doses discordantes exibe um numero', () => {
  let amb = 0, vazado = 0;
  P.products.forEach(p => p.uses.forEach(u => {
    const j = juntaDose(p, u);
    if (j.estado === 'AMBIGUOUS_DOSE_FOR_THIS_PAIR') { amb++; if (j.d) vazado++; }
  }));
  afirma(amb > 0, 'nenhum caso ambiguo encontrado — o teste perdeu o alvo');
  afirma(vazado === 0, `${vazado} pares ambiguos ainda entregam um valor unico`);
  return `${amb} pares ambiguos, nenhum com valor unico`;
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
