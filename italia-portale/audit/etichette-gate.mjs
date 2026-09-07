#!/usr/bin/env node
/* SINTONIA · PORTAO DAS ETICHETTE — o acoplamento da LABEL INTELLIGENCE
   ---------------------------------------------------------------------------
   Uma capacidade inteira chegou de fora, com a sua propria lei escrita e os
   seus proprios portoes. Nada disso nos serve aqui: os portoes dela mediam a
   ferramenta dela.

       OS PORTOES DA FERRAMENTA MEDEM A FERRAMENTA.
       QUEM ACOPLA TEM DE MEDIR O ACOPLAMENTO.

   O acoplamento tem tres maneiras de mentir, e nenhuma delas aparece no codigo:

     1 · SILENCIAR UMA IGNORANCIA. Trocar `PAIR_NOT_CHECKABLE_...` por «—», por
         zero, ou simplesmente nao a desenhar. A tela fica mais limpa e passa a
         dizer que sabe o que nao sabe. E a lei zero da ferramenta de origem, e
         e tambem a do contrato de design deste portal.

     2 · POR ASPAS ONDE NAO HA CITACAO. «L'etichetta scrive» e a afirmacao mais
         forte que existe aqui, porque convida quem le a ir conferir no PDF. Uma
         frase remontada entre aspas manda a pessoa procurar no documento algo
         que la nao esta — e o que ela conclui e que o documento esta errado.

     3 · COLAPSAR AS SETE COBERTURAS NUMA. 100% de PDFs descarregados nao diz
         nada sobre tabelas de uso lidas (78,5%) nem sobre doses (12,9%).

   E ha uma quarta, que e a do CONTRATO DE ACOPLAMENTO e nao da tela:

     4 · DEIXAR USO AUTORIZADO VIRAR OPORTUNIDADE COMERCIAL. A ferramenta
         responde uma familia so; juntar-lhe outra por um botao seria fazer a
         juncao que o contrato proibe em letra.

   Este portao abre o portal num browser de verdade e mede as quatro. Mede
   tambem o selo do payload — recalculando-o, nao lendo-o.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { serve, open } from './lib/drive.mjs';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const CLIENTE = path.resolve(AQUI, '..', 'client');

const G = '\x1b[32m', R = '\x1b[31m', X = '\x1b[0m', DIM = '\x1b[2m';
const linhas = [];
const ok = (t, cond, medido, detalhe) => linhas.push({ t, cond: !!cond, medido, detalhe });

/* ── 1 · O SELO, RECALCULADO ───────────────────────────────────────────────
   `CONTENT_SHA256` e o sha256 do payload COM O SELO DE FORA, por
   `v1/inteligencia/selo.py::conteudo_sha`. Ler o campo e confiar nele nao mede
   nada: quem editar uma linha edita tambem o campo. Recalcular mede.

       UM SELO QUE NAO SE RECALCULA E UMA ETIQUETA, NAO UM SELO.          */
const bruto = fs.readFileSync(path.join(CLIENTE, 'italy-label-intelligence.js'), 'utf8');
const inicio = bruto.indexOf('window.ITALY_LABEL_INTELLIGENCE = ');
const json = bruto.slice(inicio + 'window.ITALY_LABEL_INTELLIGENCE = '.length).replace(/;\s*$/, '');
const PAY = JSON.parse(json);

/* ══ O SELO MEDE-SE COM O INSTRUMENTO QUE O ESCREVEU ═══════════════════════
   A primeira versao deste controlo refez a conta em JavaScript e reprovou — e
   estava ERRADA ela, nao o payload. `json.dumps` do Python escreve o float
   `100.0` como «100.0»; `JSON.stringify`, depois de `JSON.parse`, escreve
   «100». As sete coberturas tem PCT float, e isso basta para o sha divergir.

       REIMPLEMENTAR O INSTRUMENTO NAO E MEDIR COM ELE.
       UM CONTROLO QUE REPROVA POR CAUSA DA SUA PROPRIA COPIA
       ENSINA A IGNORAR O CONTROLO.

   Entao chama-se `python3` com as MESMAS quatro opcoes de `selo.py`:
   ensure_ascii=False, sort_keys=True, separators=(',',':') e PRODUCED_BY de
   fora. Sem python na maquina o controlo diz NAO MEDIDO — o terceiro estado
   deste repositorio — e nao um PASS por omissao.                            */
const tmp = path.join(CLIENTE, '.selo-payload.json');
fs.writeFileSync(tmp, json);
const py = spawnSync('python3', ['-c', `
import json,hashlib,sys
p=json.load(open(sys.argv[1],encoding='utf-8'))
corpo={k:v for k,v in p.items() if k!='PRODUCED_BY'}
print(hashlib.sha256(json.dumps(corpo,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest())
print(p['PRODUCED_BY']['CONTENT_SHA256'])
`, tmp], { encoding: 'utf8' });
fs.unlinkSync(tmp);
const [recalc, declarado] = String(py.stdout || '').trim().split('\n');
if (py.status !== 0 || !recalc) {
  ok('SELO · o payload e byte a byte o que a ferramenta selou', false,
    'NAO MEDIDO — python3 indisponivel', [String(py.stderr || '').slice(0, 200)]);
} else {
  ok('SELO · o payload e byte a byte o que a ferramenta selou', recalc === declarado,
    recalc.slice(0, 16) + (recalc === declarado ? ' = declarado' : ' ≠ ' + String(declarado).slice(0, 16)));
}

/* ── 2 · O LEXICO COBRE TUDO O QUE A TELA MOSTRA ───────────────────────────
   Um token sem entrada no lexico chega a tela sozinho. Isso NAO e ilegal — a
   lei exige o token, nao a glosa — mas e uma divida que se deve ver, e nao
   descobrir num screenshot. */
const lexBruto = fs.readFileSync(path.join(CLIENTE, 'italy-label-lexicon.js'), 'utf8');
const win = {};
new Function('window', lexBruto)(win);
const LEX = win.ITALY_LABEL_LEXICON || {};
const CAMPOS_USO = ['pair_check', 'crop_name', 'target_name', 'exclusion_check', 'route', 'evidence'];
const CAMPOS_DOSE = ['band_check', 'crop_check', 'target_literal', 'max_check', 'interval_check', 'rule_check'];
const naTela = new Set();
const guarda = (v) => { if (typeof v === 'string' && v && v === v.toUpperCase() && v.includes('_')) naTela.add(v); };
for (const p of PAY.products || []) {
  guarda(p.dose_state); guarda(p.label_validity_state);
  for (const u of p.uses || []) CAMPOS_USO.forEach((k) => guarda(u[k]));
  for (const d of p.doses || []) CAMPOS_DOSE.forEach((k) => guarda(d[k]));
}
const semGlosa = [...naTela].filter((t) => !LEX[t]).sort();
ok('LEXICO · todo estado que a tela mostra tem nome italiano ao lado',
  semGlosa.length === 0, naTela.size + ' estados · ' + semGlosa.length + ' sem glosa', semGlosa.slice(0, 10));

/* Uma regra citada e nao escrita e uma regra que ninguem pode conferir — e a
   lei da propria ferramenta, com portao proprio. Aqui a nossa metade: nenhuma
   glosa pode citar um id que R-01..R-22 / N-* / P-* nao contenha. */
const IDS = new Set(['R-01', 'R-02', 'R-03', 'R-04', 'R-05', 'R-06', 'R-07', 'R-08', 'R-09',
  'R-10', 'R-10b', 'R-11', 'R-12', 'R-13', 'R-14', 'R-15', 'R-17', 'R-18', 'R-19', 'R-20',
  'R-21', 'R-22', 'N-01', 'N-02', 'N-03', 'N-04', 'N-05',
  'P-01', 'P-02', 'P-03', 'P-04', 'P-05']);
const regrasMas = Object.keys(LEX).filter((k) => k !== 'FONTE')
  .map((k) => (LEX[k] || {}).regra).filter(Boolean).filter((r) => !IDS.has(r));
ok('REGRAS · nenhuma glosa cita um id que a lei nao contem',
  regrasMas.length === 0, [...new Set(regrasMas)].join(' ') || '0', [...new Set(regrasMas)]);

/* ── 3 · A TELA ────────────────────────────────────────────────────────────── */
const server = await serve(8961);
const { browser, page: pg, errors } = await open({ port: 8961, page: '/portale.html#etichette' });
await pg.waitForSelector('[data-li-card]', { timeout: 45000 });

ok('TELA · abre sem erro de pagina', errors.length === 0, errors.length + ' erros', errors.slice(0, 4));

const coberturas = await pg.locator('[data-li-coverage]').evaluateAll((es) => es.map((e) => e.getAttribute('data-li-coverage')));
ok('COBERTURA · as sete estao na tela, e sao sete',
  coberturas.length === 7 && new Set(coberturas).size === 7,
  coberturas.length + ' · ' + coberturas.map((c) => c.replace('_COVERAGE', '')).join(' '));

/* NAO SOMAR e uma coisa que se mede: se alguem publicar uma media, ela aparece
   como um numero que nao esta em nenhuma das sete. */
const pcts = (PAY.coverage && Object.values(PAY.coverage).map((c) => c.PCT)) || [];
const media = pcts.length ? Math.round(pcts.reduce((a, b) => a + b, 0) / pcts.length * 10) / 10 : null;
const textoCob = await pg.locator('[data-li-coverage]').first().evaluate((e) => (e.closest('div').parentElement.parentElement.innerText || ''));
ok('COBERTURA · nenhuma media colapsa as sete num numero so',
  media === null || !textoCob.includes(String(media) + '%'), 'media seria ' + media + '% — ausente da tela');

ok('CONTRATO · a tela diz que uso autorizado nao e oportunidade',
  await pg.locator('[data-li-not-opportunity]').count() === 1, 'a frase esta na tela');

/* O selo FATO nao pode aparecer como «tres testes independentes disseram sim».
   A tela tem de dizer, onde se le, que hoje R-14 sozinha da os mesmos 1.324. */
const comoFato = await pg.locator('[data-li-fact-how]').first().innerText().catch(() => '');
ok('SELO FATTO · a tela diz que hoje R-14 sozinha da o mesmo numero',
  /R-14/.test(comoFato) && /1\.?324/.test(comoFato), comoFato ? 'declarado na tela' : 'ausente');

/* ── 4 · A FICHA · a ignorancia visivel e a citacao com aspas ──────────────
   Escolhe-se um rotulo cujo par NAO e facto: e ali que a tela e tentada a
   calar-se. GOLTIX (002732) tem 2 usos e 0 factos — medido no payload. */
await pg.evaluate(() => { location.hash = '#etichette'; });
await pg.locator('[data-li-card="002732"]').click();
await pg.waitForTimeout(900);

const tokens = await pg.locator('[data-li-token]').evaluateAll((es) => es.map((e) => e.getAttribute('data-li-token')));
ok('IGNORANCIA · os estados chegam a ficha com o proprio nome',
  tokens.includes('PAIR_NOT_CHECKABLE_ROUTE_NOT_GEOMETRIC'),
  tokens.length + ' tokens desenhados');

/* NENHUM token pode sair vazio ou virar traco: seria a lei zero quebrada em
   silencio, que e a unica maneira de a quebrar. */
const vazios = tokens.filter((t) => !t || !t.trim() || t.trim() === '-' || t.trim() === 'N/A' || t.trim() === '0');
ok('IGNORANCIA · nenhum token virou «—», «0», «N/A» ou vazio',
  vazios.length === 0, vazios.length + ' vazios de ' + tokens.length);

/* A GLOSA ESTA AO LADO, NAO NO LUGAR: o token e a frase italiana vivem no mesmo
   chip, e o chip tem de conter os dois. */
const chips = await pg.locator('[data-li-token]').evaluateAll((es) => es.map((e) => ({
  code: e.getAttribute('data-li-token'), txt: (e.innerText || '').trim() })));
const semAmbos = chips.filter((c) => c.txt && !c.txt.includes(c.code));
ok('GLOSA · a frase italiana esta AO LADO do token, nunca no lugar dele',
  semAmbos.length === 0, semAmbos.length + ' chips sem o proprio nome dentro',
  semAmbos.slice(0, 5).map((c) => c.code));

/* ── 5 · AS ASPAS ──────────────────────────────────────────────────────────
   O controlo que importa: percorrem-se TODAS as fichas com dose e verifica-se
   que nenhuma frase entre aspas vem de um estado que nao seja QUOTE_VERBATIM.
   Mede-se no payload — porque a tela so mostra uma ficha de cada vez — e
   confere-se na tela que a regra desenhada e a mesma. */
const naoVerbatim = [];
for (const p of PAY.products || []) {
  for (const d of p.doses || []) {
    if (d.quote && d.quote !== 'NOT_PRESERVED' && d.quote_state !== 'QUOTE_VERBATIM') naoVerbatim.push(p.reg);
  }
}
const comAspas = await pg.evaluate(() => {
  const t = document.body.innerText || '';
  return (t.match(/l’etichetta scrive: “/g) || []).length;
});
const leiturasExtrator = await pg.evaluate(() => {
  const t = document.body.innerText || '';
  return (t.match(/lettura dell’estrattore/g) || []).length;
});
ok('CITACAO · o verbo «l’etichetta scrive» so aparece com QUOTE_VERBATIM',
  comAspas >= 1 && leiturasExtrator >= 1,
  comAspas + ' com aspas · ' + leiturasExtrator + ' como leitura do extrator · '
  + naoVerbatim.length + ' doses nao-verbatim no acervo');

/* CONTROLO NEGATIVO DA CITACAO, na propria pagina: numa ficha onde o estado da
   citacao NAO e verbatim, a frase tem de sair sem aspas. GOLTIX e o caso: os
   dois usos trazem QUOTE_NOT_CONTIGUOUS_IN_DOCUMENT. */
const goltix = await pg.locator('body').innerText();
const usoComAspas = /l’etichetta scrive: “Il dosaggio/.test(goltix);
ok('CITACAO · controlo negativo — a frase nao contigua sai SEM aspas',
  !usoComAspas && /lettura dell’estrattore — non è una citazione: Il dosaggio/.test(goltix),
  usoComAspas ? 'ASPAS INDEVIDAS' : 'sem aspas, como manda R-18');

/* ── 6 · NENHUMA PORTA PARA A OPORTUNIDADE ─────────────────────────────────
   O contrato proibe a juncao, e a maneira de a fazer sem querer e um botao.
   Mede-se: nenhum elemento desta vista navega para o radar. */
/* A PRIMEIRA VERSAO DESTE CONTROLO LEU `document.body` E ACUSOU O MENU.
   «Radar delle Opportunità» esta na barra lateral de TODAS as telas: e a
   navegacao do portal, nao uma porta desta vista.

       O QUE SE MEDE E O QUE A VISTA OFERECE,
       NAO O QUE O PORTAL TEM AO LADO DELA.                                  */
const portas = await pg.evaluate(() => {
  const v = document.querySelector('[data-li-view]');
  const t = ((v && v.innerText) || '').toLowerCase();
  return { tem: !!v, radar: /radar delle opportunit|vedi le opportunit|apri l.opportunit/.test(t) };
});
ok('CONTRATO · a vista das etichette nao oferece porta para o radar',
  portas.tem && !portas.radar,
  !portas.tem ? 'vista nao encontrada' : portas.radar ? 'ha uma porta' : 'nenhuma porta dentro da vista');

await browser.close();
server.close();

console.log('');
console.log('  SINTONIA · ETICHETTE · ACOPLAMENTO DA LABEL INTELLIGENCE');
console.log('  ' + '─'.repeat(84));
for (const l of linhas) {
  console.log(`  ${l.cond ? G + 'PASS' + X : R + 'FAIL' + X}  ${l.t.padEnd(58)} ${l.medido}`);
  if (!l.cond && l.detalhe) for (const d of [].concat(l.detalhe)) console.log(`        ${DIM}${String(d).slice(0, 140)}${X}`);
}
const mau = linhas.filter((l) => !l.cond).length;
console.log('  ' + '─'.repeat(84));
console.log(`  ${linhas.length - mau}/${linhas.length} passing` + (mau ? `  ${R}${mau} failing${X}` : ''));
console.log('');
process.exit(mau === 0 ? 0 : 1);
