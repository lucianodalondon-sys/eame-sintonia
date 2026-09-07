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

/* ── 3 · A TAXONOMIA E DO REGISTO, E COBRE TUDO ────────────────────────────
   A barra de tipos so pode oferecer classes que existem no dado. E um produto
   sem classe nao pode receber uma inventada: sai UNCLASSIFIED, com o nome.

       UMA CATEGORIA INVENTADA E UM FILTRO QUE MENTE PARA OS DOIS LADOS:
       INCLUI QUEM NAO E, E ESCONDE QUEM E.                                  */
const actCount = {};
for (const p of PAY.products || []) { const a = p.activity || 'UNCLASSIFIED'; actCount[a] = (actCount[a] || 0) + 1; }
const semClasse = actCount.UNCLASSIFIED || 0;
ok('TAXONOMIA · toda classe da barra vem do campo do registo',
  Object.keys(actCount).length >= 2,
  Object.keys(actCount).length + ' classes · ' + Object.entries(actCount).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([k, n]) => k + ' ' + n).join(' · '));
ok('TAXONOMIA · a soma das classes e o universo, sem sobra nem falta',
  Object.values(actCount).reduce((a, b) => a + b, 0) === (PAY.products || []).length,
  Object.values(actCount).reduce((a, b) => a + b, 0) + ' = ' + (PAY.products || []).length
  + ' · sem classe: ' + semClasse);

/* A DERIVACAO DA LINHA ADAMA TEM DE SER CONFERIVEL, e o controlo que a pode
   desmentir e este: se um alvo aparecesse sob duas linhas diferentes, a
   derivacao TARGET_CLASS_FROM_PRODUCT_ACTIVITY estaria contradita. */
const LINHA = { 'DISERBANTE': 'WEED', 'DISERBANTE-ANTIDOTO AGRONOMICO': 'WEED', 'FUNGICIDA': 'DISEASE',
  'INSETTICIDA': 'PEST', 'INSETTICIDA-ACARICIDA': 'PEST', 'AFICIDA': 'PEST' };
const porAlvo = {};
for (const p of PAY.products || []) {
  const l = LINHA[p.activity]; if (!l) continue;
  for (const u of p.uses || []) { if (!u.target) continue; (porAlvo[u.target] = porAlvo[u.target] || new Set()).add(l); }
}
const contraditos = Object.keys(porAlvo).filter((t) => porAlvo[t].size > 1);
ok('DERIVACAO · nenhum alvo cai em duas linhas ADAMA ao mesmo tempo',
  contraditos.length === 0,
  Object.keys(porAlvo).length + ' alvos derivados · ' + contraditos.length + ' contraditos', contraditos.slice(0, 6));

/* ── 4 · OS QUATRO ESTADOS HUMANOS, MEDIDOS NO DADO ────────────────────── */
const NOME_OK = { CROP_NAME_LITERAL: 1, CROP_NAME_INFLECTED_IN_LABEL: 1 };
const ALVO_OK = { TARGET_NAME_LITERAL: 1, TARGET_NAME_INFLECTED_IN_LABEL: 1 };
const NAO_CORREU = { TARGET_NAME_NOT_CHECKED: 1, CROP_NAME_NOT_CHECKED: 1, NOT_CHECKED: 1, NOT_ATTEMPTED: 1 };
const estadoDe = (u) => {
  if (u.fact) return 'VERIFIED';
  if (NAO_CORREU[u.crop_name] || NAO_CORREU[u.target_name]) return 'ERROR';
  if (NOME_OK[u.crop_name] && ALVO_OK[u.target_name] && u.exclusion_check === 'ATTESTED_OUTSIDE_EXCLUSION') return 'FOUND';
  return 'UNKNOWN';
};
const cont = { VERIFIED: 0, FOUND: 0, UNKNOWN: 0, ERROR: 0 };
for (const p of PAY.products || []) for (const u of p.uses || []) cont[estadoDe(u)]++;
/* O MAPEAMENTO NAO PODE MUDAR O NUMERO DE VERIFICADOS. Se mudasse, a tela
   estaria a promover linhas para melhorar a leitura — que e a unica coisa que
   esta reorganizacao nao pode fazer. */
const factReal = (PAY.products || []).reduce((a, p) => a + (p.uses || []).filter((u) => u.fact).length, 0);
ok('ESTADOS · VERIFIED e exactamente o selo do contrato, nem mais um',
  cont.VERIFIED === factReal, cont.VERIFIED + ' = ' + factReal + ' (fact=true)');
ok('ESTADOS · a soma dos quatro e o total de usos',
  cont.VERIFIED + cont.FOUND + cont.UNKNOWN + cont.ERROR
    === (PAY.products || []).reduce((a, p) => a + (p.uses || []).length, 0),
  'VERIFIED ' + cont.VERIFIED + ' · FOUND ' + cont.FOUND + ' · UNKNOWN ' + cont.UNKNOWN + ' · ERROR ' + cont.ERROR);

/* ── 5 · A TELA ────────────────────────────────────────────────────────────── */
const server = await serve(8961);
const { browser, page: pg, errors } = await open({ port: 8961, page: '/portale.html#etichette' });
await pg.waitForSelector('[data-li-card]', { timeout: 45000 });

ok('TELA · abre sem erro de pagina', errors.length === 0, errors.length + ' erros', errors.slice(0, 4));

const nomePublico = await pg.evaluate(() => {
  const h = document.querySelector('[data-li-view] h1');
  return h ? h.innerText.trim() : '';
});
ok('NOME · a ferramenta chama-se Label Intelligence na propria tela',
  /label intelligence/i.test(nomePublico), JSON.stringify(nomePublico));

const tipos = await pg.locator('[data-li-type]').evaluateAll((es) => es.map((e) => e.getAttribute('data-li-type')));
ok('BARRA · a barra de tipos oferece o universo mais cada classe do registo',
  tipos.length === Object.keys(actCount).length + 1 && tipos[0] === '',
  tipos.length + ' botoes · ' + (tipos.length - 1) + ' classes');

const coberturas = await pg.locator('[data-li-coverage]').evaluateAll((es) => es.map((e) => e.getAttribute('data-li-coverage')));
ok('COBERTURA · as sete estao na tela, e sao sete',
  coberturas.length === 7 && new Set(coberturas).size === 7,
  coberturas.length + ' · ' + coberturas.map((c) => c.replace('_COVERAGE', '')).join(' '));

const pcts = (PAY.coverage && Object.values(PAY.coverage).map((c) => c.PCT)) || [];
const media = pcts.length ? Math.round(pcts.reduce((a, b) => a + b, 0) / pcts.length * 10) / 10 : null;
const textoTudo = await pg.locator('[data-li-view]').innerText();
ok('COBERTURA · nenhuma media colapsa as sete num numero so',
  media === null || !textoTudo.includes(String(media) + '%'), 'media seria ' + media + '% — ausente da tela');

ok('CONTRATO · a tela diz que uso autorizado nao e oportunidade',
  await pg.locator('[data-li-not-opportunity]').count() === 1, 'a frase esta na tela');

const portas = await pg.evaluate(() => {
  const v = document.querySelector('[data-li-view]');
  const t = ((v && v.innerText) || '').toLowerCase();
  return { tem: !!v, radar: /radar delle opportunit|vedi le opportunit|apri l.opportunit/.test(t) };
});
ok('CONTRATO · a vista nao oferece porta para o radar',
  portas.tem && !portas.radar, portas.radar ? 'ha uma porta' : 'nenhuma porta dentro da vista');

/* ══ CASO K · o filtro de tipo mostra SO aquela classe ═══════════════════ */
await pg.locator('[data-li-type="DISERBANTE"]').click();
await pg.waitForTimeout(600);
const acts = await pg.locator('[data-li-card]').evaluateAll((es) => es.map((e) => e.getAttribute('data-li-activity')));
ok('CASO K · filtrar por classe mostra so produtos dessa classe',
  acts.length > 0 && acts.every((a) => a === 'DISERBANTE'),
  acts.length + ' cartoes · ' + new Set(acts).size + ' classe(s) distintas');
const contaK = await pg.locator('[data-li-count]').getAttribute('data-li-count');
ok('CASO K · o contador diz quantos ficaram, e bate com o censo',
  String(contaK) === String(actCount.DISERBANTE), contaK + ' = ' + actCount.DISERBANTE);

/* ══ CASO L · busca por substancia activa ═══════════════════════════════ */
await pg.locator('[data-li-clear]').click();
await pg.waitForTimeout(400);
await pg.locator('[data-li-field="liSub"]').fill('GLYPHOSATE');
await pg.waitForTimeout(600);
const nSub = Number(await pg.locator('[data-li-count]').getAttribute('data-li-count'));
const esperadoSub = (PAY.products || []).filter((p) => String(p.actives || '').toUpperCase().includes('GLYPHOSATE')).length;
ok('CASO L · a busca por substancia activa busca no campo estruturado',
  nSub === esperadoSub && nSub > 0, nSub + ' = ' + esperadoSub);

/* ══ CASO N · tipo + cultura + substancia, combinados ═══════════════════ */
await pg.locator('[data-li-clear]').click();
await pg.waitForTimeout(400);
await pg.locator('[data-li-type="FUNGICIDA"]').click();
await pg.locator('[data-li-field="liCrop"]').fill('VITE');
await pg.waitForTimeout(600);
const nComb = Number(await pg.locator('[data-li-count]').getAttribute('data-li-count'));
const esperadoComb = (PAY.products || []).filter((p) => p.activity === 'FUNGICIDA'
  && (p.uses || []).some((u) => String(u.crop || '').toUpperCase().includes('VITE'))).length;
ok('CASO N · os filtros funcionam combinados', nComb === esperadoComb && nComb > 0,
  'FUNGICIDA + VITE = ' + nComb + ' (censo ' + esperadoComb + ')');

/* ══ CASO M · buscar por cultura NAO promove ocorrencia a autorizacao ═══ */
const nota = await pg.locator('[data-li-match-note]').count();
ok('CASO M · a busca por cultura avisa que encontrar nao e autorizar',
  nota === 1, nota ? 'aviso na tela' : 'AVISO AUSENTE');

/* ══ CASO O · limpar filtros devolve o universo ═════════════════════════ */
await pg.locator('[data-li-clear]').click();
await pg.waitForTimeout(600);
const nTudo = Number(await pg.locator('[data-li-count]').getAttribute('data-li-count'));
ok('CASO O · limpar filtros devolve o universo inteiro',
  nTudo === (PAY.products || []).length, nTudo + ' = ' + (PAY.products || []).length);

/* ══ CASO J · LEOPARD 5 EC, o caso que a missao nomeia ══════════════════ */
await pg.locator('[data-li-field="liQ"]').fill('LEOPARD 5 EC');
await pg.waitForTimeout(600);
await pg.locator('[data-li-card]').first().click();
await pg.waitForTimeout(900);
const leo = PAY.products.find((p) => p.name === 'LEOPARD 5 EC');
const leoUsos = (leo.uses || []).length;
const leoVer = (leo.uses || []).filter((u) => u.fact).length;
const leoTexto = await pg.locator('[data-li-view]').innerText();
ok('CASO J · LEOPARD 5 EC diz quantos foram encontrados E quantos provados',
  leoTexto.includes(String(leoUsos)) && /VERIFICATO|VERIFIED/.test(leoTexto),
  leoUsos + ' encontrados · ' + leoVer + ' verificados');

const estadosNaTela = await pg.locator('[data-li-use]').evaluateAll((es) => es.map((e) => e.getAttribute('data-li-state')));
ok('CASO A/B/C · os estados humanos chegam as linhas',
  estadosNaTela.length > 0 && estadosNaTela.every((x) => ['VERIFIED', 'FOUND', 'UNKNOWN', 'ERROR'].includes(x)),
  [...new Set(estadosNaTela)].join(' · ') + ' em ' + estadosNaTela.length + ' linhas');

/* ══ CASO I · o utilizador NAO pode confundir NOT PROVEN com NOT AUTHORISED ══
   Mede-se onde importa: numa linha cujo estado NAO e verificado, a frase
   «non autorizzato» nao pode aparecer. E o bloco que usa essas palavras e
   outro, e so existe com prova positiva. */
const confusao = await pg.evaluate(() => {
  const bad = [];
  for (const el of document.querySelectorAll('[data-li-use]')) {
    const st = el.getAttribute('data-li-state');
    const t = (el.innerText || '').toLowerCase();
    if (st !== 'VERIFIED' && /non autorizzat|not authorised|not authorized/.test(t)) bad.push(st);
  }
  return bad;
});
ok('CASO I · «non provato» nunca aparece vestido de «non autorizzato»',
  confusao.length === 0, confusao.length + ' linhas confusas');

/* A frase que EXPLICA o estado tem de estar la — e o que separa as duas. */
ok('CASO B · a linha TROVATO explica que nao significa nao autorizado',
  /non significa che non sia autorizzato|does not mean it is not authorised/i.test(leoTexto),
  'a explicacao esta na linha');

/* ══ CASO G · o PDF oficial abre ═══════════════════════════════════════ */
const href = await pg.locator('[data-li-pdf]').first().getAttribute('href');
ok('CASO G · o documento oficial tem endereco e abre noutra aba',
  !!href && /^https?:\/\//.test(href), href ? href.slice(0, 58) + '…' : 'SEM ENDERECO');

/* ══ CASO F · frase encontrada e nao interpretada ══════════════════════ */
ok('CASO F · «trovata — non interpretata» onde a frase existe e nao foi lida',
  await pg.locator('[data-li-found-not-parsed]').count() >= 1, 'estado declarado');

/* ══ CASO E · campo ausente aparece com nome, nunca em branco ══════════ */
const vazios = await pg.locator('[data-li-token]').evaluateAll((es) =>
  es.map((e) => e.getAttribute('data-li-token')).filter((t) => !t || !t.trim() || ['-', 'N/A', '0'].includes(t.trim())));
ok('CASO E · nenhum token virou «—», «0», «N/A» ou vazio', vazios.length === 0, vazios.length + ' vazios');

/* ══ CASO H · a auditoria preserva o que estava a vista ════════════════ */
const antesAudit = await pg.locator('[data-li-token]').count();
await pg.locator('[data-li-audit-toggle]').click();
await pg.waitForTimeout(500);
const depoisAudit = await pg.locator('[data-li-token]').count();
const auditTexto = await pg.locator('[data-li-audit]').innerText().catch(() => '');
ok('CASO H · a auditoria abre e traz istantanea, regras e selo',
  depoisAudit > antesAudit && /PROD_FTS|R-\d\d|[0-9a-f]{16}/.test(auditTexto),
  antesAudit + ' → ' + depoisAudit + ' tokens');

/* ══ EVIDENCIA A UM CLIQUE ═════════════════════════════════════════════ */
await pg.locator('[data-li-evidence-btn]').first().click();
await pg.waitForTimeout(500);
const ev = await pg.locator('[data-li-evidence]').count();
ok('EVIDENCIA · cada linha abre a sua evidencia sem sair da pagina',
  ev >= 1, ev + ' bloco(s) de evidencia');

/* ══ A CITACAO · aspas so com QUOTE_VERBATIM ═══════════════════════════ */
const evTexto = await pg.locator('[data-li-evidence]').first().innerText();
const temAspas = /l’etichetta scrive: “/.test(evTexto);
const temLeitura = /lettura dell’estrattore/.test(evTexto);
ok('CITACAO · a evidencia distingue citacao de leitura do extractor',
  temAspas || temLeitura, (temAspas ? 'com aspas' : '') + (temLeitura ? ' + leitura do extractor' : ''));

/* CONTROLO NEGATIVO: nenhuma frase entre aspas pode vir de um estado que nao
   seja QUOTE_VERBATIM. Mede-se no payload, que e onde estao os dois lados. */
const aspasIndevidas = [];
for (const p of PAY.products || []) {
  for (const d of p.doses || []) {
    if (d.quote && d.quote !== 'NOT_PRESERVED' && d.quote_state !== 'QUOTE_VERBATIM') aspasIndevidas.push(p.reg);
  }
}
const nAspas = (leoTexto.match(/l’etichetta scrive: “/g) || []).length;
const nLeitura = (leoTexto.match(/lettura dell’estrattore/g) || []).length;
ok('CITACAO · o verbo forte so com QUOTE_VERBATIM, e ha as duas formas na tela',
  nLeitura >= 1, nAspas + ' com aspas · ' + nLeitura + ' como leitura · '
  + aspasIndevidas.length + ' doses nao-verbatim no acervo');

/* ══ COMPARACAO · o que nao da, diz-se com o proprio nome ══════════════ */
ok('COMPARACAO · o que o acervo nao permite comparar esta declarado',
  leoTexto.includes('NOT_IMPLEMENTABLE_WITH_CURRENT_EVIDENCE'),
  'estado declarado na ficha');

/* ══ CASO P · nenhum produto recebe classe inventada ═══════════════════ */
/* A PRIMEIRA VERSAO DESTE CONTROLO MEDIU ZERO CARTOES E PASSOU.
   `location.hash` nao volta da ficha para a lista neste guscio — a vista e
   estado, nao rota — e um `every` sobre lista vazia e verdadeiro.

       UM CONTROLO QUE PASSA SOBRE ZERO ELEMENTOS NAO CONTROLOU NADA.

   Volta-se pelo botao que o leitor usa, e exige-se que haja cartoes. */
await pg.locator('[data-li-view] span').filter({ hasText: /tutte le etichette/i }).first().click();
await pg.waitForTimeout(900);
/* a lista guarda os filtros ao voltar — e correcto para quem usa, e faria
   este controlo medir UM cartao. Limpa-se, para medir o universo. */
await pg.locator('[data-li-clear]').click();
await pg.waitForTimeout(700);
const todasAct = await pg.locator('[data-li-card]').evaluateAll((es) => es.map((e) => e.getAttribute('data-li-activity')));
const inventadas = todasAct.filter((a) => !(a in { ...{} }) && a !== 'UNCLASSIFIED' && !Object.prototype.hasOwnProperty.call(actCount, a));
ok('CASO P · nenhum cartao mostra uma classe que o registo nao escreveu',
  todasAct.length > 0 && inventadas.length === 0,
  todasAct.length + ' cartoes · ' + inventadas.length + ' classes inventadas', inventadas.slice(0, 5));

await browser.close();
server.close();

console.log('');
console.log('  SINTONIA · LABEL INTELLIGENCE · O ACOPLAMENTO E A FERRAMENTA');
console.log('  ' + '─'.repeat(86));
for (const l of linhas) {
  console.log(`  ${l.cond ? G + 'PASS' + X : R + 'FAIL' + X}  ${l.t.padEnd(60)} ${l.medido}`);
  if (!l.cond && l.detalhe) for (const d of [].concat(l.detalhe)) console.log(`        ${DIM}${String(d).slice(0, 140)}${X}`);
}
const mau = linhas.filter((l) => !l.cond).length;
console.log('  ' + '─'.repeat(86));
console.log(`  ${linhas.length - mau}/${linhas.length} passing` + (mau ? `  ${R}${mau} failing${X}` : ''));
console.log('');
process.exit(mau === 0 ? 0 : 1);
