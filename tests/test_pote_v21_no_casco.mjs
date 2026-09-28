/* D125 · POTES-UM-CARTAO — o casco le o pote v2.1 e so MOSTRA o que a Intelligence escreveu.

       node tests/test_pote_v21_no_casco.mjs

   ⚠️ DADO SINTETICO DECLARADO: tests/fixtures/pote/POTE-SINTETICO-V21.json, gerado por
   provas/potes_um_cartao/gerar_fixture_v21.py (corrida B com 1 documento novo que toca 3 potes; a corrida A
   e o ANTERIOR). Entra no mesmo sandbox do banco de provas do portal (italia-portale/audit/lib/harness.mjs).

   Prova que:
     Q1  o leitor aceita a v2.1 e resolve cada ID no UNICO cartao (nenhuma copia no pote);
     Q2  o mesmo cartao aparece nos 3 potes (Label, Oportunidade, Agenda) com o MESMO selo de DELTA;
     Q3  o selo e o que o pote escreveu — se o pote disser outra coisa, o casco diz essa outra coisa
         (nao compara potes, nao recalcula);
     Q4  copia no compartimento ou ID sem cartao = pote recusado, nada desenhado;
     Q5  o pote v2 de sempre continua a passar (nada quebra para quem ainda nao migrou). */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { mount, CLIENT } from '../italia-portale/audit/lib/harness.mjs';

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const V21 = JSON.parse(fs.readFileSync(path.join(RAIZ, 'tests/fixtures/pote/POTE-SINTETICO-V21.json'), 'utf8'));
const V2 = JSON.parse(fs.readFileSync(path.join(RAIZ, 'tests/fixtures/pote/POTE-SINTETICO-V2-UNICO.json'), 'utf8'));
const LEITOR = fs.readFileSync(path.join(CLIENT, 'sintonia-pote-casco.js'), 'utf8');

let falhas = 0, provas = 0;
const prova = (nome, ok, detalhe = '') => {
  provas++;
  if (!ok) { falhas++; console.log('FAIL: ' + nome + (detalhe ? ' — ' + detalhe : '')); }
  else console.log('ok   ' + nome);
};
const clone = (x) => JSON.parse(JSON.stringify(x));

function montar(pote) {
  const M = mount({});
  vm.runInContext(LEITOR, M.ctx, { filename: 'sintonia-pote-casco.js' });
  M.ctx.SINTONIA_POTE = pote;
  return M;
}
const L = (M) => M.ctx.SINTONIA_POTE_CASCO;
const C = Object.keys(V21.CARTOES).find((k) => k.startsWith('XQ-'));

/* Q1 */
{
  const M = montar(V21);
  prova('Q1 o leitor aceita a v2.1 (0 violacoes)', L(M).conferir(V21).length === 0, L(M).conferir(V21).join(' · '));
  prova('Q1 nenhum compartimento traz copia', Object.values(V21.COMPARTIMENTOS).every((e) => !('OBJETOS' in e)));
  const r = L(M).resolver(V21).pote;
  const lugares = Object.values(r.COMPARTIMENTOS).reduce((n, e) => n + e.OBJETOS.length, 0);
  prova('Q1 resolvido: 7 lugares, 4 cartoes', lugares === 7 && Object.keys(V21.CARTOES).length === 4);
}

/* Q2 */
{
  const M = montar(V21);
  const selos = ['portfolio', 'meeting', 'windows'].map((view) => {
    const x = L(M).vm(V21, view, 'it');
    const o = x.objetos.find((q) => q.id === C);
    return o ? o.delta : null;
  });
  prova('Q2 o mesmo cartao nos 3 potes', selos.every((s) => s !== null), JSON.stringify(selos));
  prova('Q2 o mesmo selo nos 3 potes', new Set(selos).size === 1 && /FORTALECEU/.test(selos[0]) && /SINT-DOC-D/.test(selos[0]), selos[0]);
  const x = L(M).vm(V21, 'meeting', 'it');
  const opp = x.objetos.find((q) => q.id === 'SINT-OPP-1');
  prova('Q2 o dependente diz PAI_MUDOU', opp && /PAI_MUDOU\(/.test(opp.delta), opp && opp.delta);
  prova('Q2 a vista diz o anterior e o DELTA da corrida', x.run.some((r) => /SINT-IR-A/.test(r.v)) && x.run.some((r) => r.k === 'DELTA'));
}

/* Q3 */
{
  const p = clone(V21);
  p.CARTOES[C].DELTA.MUDANCA = 'MUDOU_ESTADO';
  p.CARTOES[C].DELTA.CAUSA = 'SINT-CAUSA-ESCRITA-PELA-INTELLIGENCE';
  const M = montar(p);
  const o = L(M).vm(p, 'portfolio', 'it').objetos.find((q) => q.id === C);
  prova('Q3 o casco mostra o que o pote escreveu (nao recalcula)', /^MUDOU_ESTADO/.test(o.delta) && /SINT-CAUSA-ESCRITA/.test(o.delta), o.delta);
}

/* Q4 */
{
  const p = clone(V21);
  p.COMPARTIMENTOS.archive.OBJETOS = [p.CARTOES[p.COMPARTIMENTOS.archive.IDS[0]]];
  const M = montar(p);
  const x = L(M).vm(p, 'archive', 'it');
  prova('Q4 copia no compartimento: recusado', x.recusado === true && x.objetos.length === 0, x.recusa);
  const q = clone(V21);
  q.COMPARTIMENTOS.portfolio.IDS.push('SINT-SEM-CARTAO');
  const y = L(montar(q)).vm(q, 'portfolio', 'it');
  prova('Q4 ID sem cartao: recusado', y.recusado === true, y.recusa);
}

/* Q5 */
{
  const M = montar(V2);
  prova('Q5 o pote v2 continua a passar', L(M).conferir(V2).length === 0);
  const x = L(M).vm(V2, 'market', 'it');
  prova('Q5 v2 nao ganha selo de DELTA', x.objetos.every((o) => o.temDelta === false));
}

console.log('\nPOTE v2.1 NO CASCO: ' + (provas - falhas) + '/' + provas + ' provas');
process.exit(falhas ? 1 : 0);
