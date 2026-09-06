// render_dump.js — despeja TODA a tela renderizada num arquivo, para os portoes
// de python poderem afirmar sobre o que a pessoa VE.
//
// O motivo, medido pelo teste de mutacao da rodada 4: os portoes
// UNKNOWN_HIDDEN_OR_FILLED, UNKNOWN_VISIBLE e PARSER_FAILURE_AS_ABSENCE
// varriam o `label-intelligence.html` ESTATICO — onde as tabelas ainda nao
// existem, porque o casco as monta em tempo de execucao. Com `val()` devolvendo
// "-" no lugar de todo token de ignorancia, os tres passaram. Com a lei
// `PARSER_FAILURE != REGULATORY_ABSENCE` apagada de 5 das 6 telas, o portao que
// existe para garantir que ela aparece tambem passou: ela sobrava no arquivo.
//
// Portao que varre o template nao esta olhando a tela.
const fs = require('fs'), path = require('path');
const RAIZ = path.resolve(__dirname, '..', '..');

function elemento() {
  const e = { innerHTML: '', value: '', dataset: {},
    classList: {add(){}, remove(){}, toggle(){}, contains(){return false}},
    addEventListener(){}, appendChild(){}, querySelector: () => elemento() };
  Object.defineProperty(e, 'onclick', {set(){}, get(){return null}});
  return e;
}
const cap = {};
global.document = {
  querySelector(sel) { return cap[sel] || (cap[sel] = elemento()); },
  querySelectorAll() { return []; }, addEventListener() {},
};
global.window = { scrollTo() {}, addEventListener() {},
  __PAYLOAD__: JSON.parse(fs.readFileSync(path.join(RAIZ, 'v1/dados/CASCO-PAYLOAD.json'), 'utf8')) };
(0, eval)(fs.readFileSync(path.join(RAIZ, 'v1/casco/app.js'), 'utf8'));
const P = window.__PAYLOAD__;

// grava direto no arquivo: juntar tudo numa string estoura o limite do V8, e
// so o que MUDOU desde o render anterior interessa — senao cada tela reescreve
// as anteriores e o despejo cresce ao quadrado.
const ARQ = path.join(RAIZ, 'v1/testes/RENDER-DUMP.html');
const fh = fs.openSync(ARQ, 'w');
let nblocos = 0, nchars = 0;
const ultimo = {};
const guarda = () => {
  for (const k in cap) {
    const h = cap[k].innerHTML;
    if (!h || ultimo[k] === h) continue;
    ultimo[k] = h;
    const b = `\n<!-- bloco ${k} -->\n` + h;
    fs.writeSync(fh, b); nblocos++; nchars += b.length;
  }
};
const tenta = fn => {
  try { fn(); guarda(); }
  catch (e) { const b = `\n<!-- ERRO ${e.message} -->\n`; fs.writeSync(fh, b); nchars += b.length; }
};

// as telas
['viewCoverage', 'viewChanges', 'viewCal', 'viewReview', 'viewCrop', 'viewSearch',
 'viewPortfolio', 'viewDecisoes', 'viewRegras'].forEach(n => {
  if (typeof global[n] === 'function') tenta(() => global[n]());
});
// as fichas de produto
P.products.forEach(p => tenta(() => viewProduto(p.reg)));
// as gavetas de prova: dose, uso, objeto
P.products.forEach((p, ip) => {
  (p.doses || []).forEach((_, i) => tenta(() => evDose(p.reg, i)));
  (p.uses || []).forEach((_, i) => tenta(() => evUso(p.reg, i)));
});
(P.objects || []).forEach((_, i) => tenta(() => { if (typeof evObj === 'function') evObj(i); }));

fs.closeSync(fh);
process.stderr.write(`  render: ${nblocos} blocos, ${nchars} caracteres\n`);
