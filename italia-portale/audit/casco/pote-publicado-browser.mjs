#!/usr/bin/env node
/* SINTONIA · PP1 · O POTE PUBLICADO NUM BROWSER DE VERDADE (D114)
   ---------------------------------------------------------------------------
   tests/test_pote_publicado.mjs prova a leitura no sandbox. Este portao abre o
   portal como a Vercel o serve — sem bandeira nenhuma, com o pote publicado da
   rodada 7 — e le o DOM:

     · cada uma das 12 rotas de ferramenta desenha o pote, com a faixa D114 e a
       marca EXPERIMENTAL, e nenhuma deixa escapar «{{» ou «undefined»;
     · o Portafoglio desenha os 86 cruzamentos, e so 5 levam A CONFIRMAR;
     · o relogio diz a data da copia da Sala, nao «oggi»;
     · a Rete Commerciale abre no vazio do pote, marcada SIMULATO, sem a demo;
     · a 390 px, nenhuma rota rola na horizontal;
     · nenhum erro de pagina, nenhum pedido falhado (404 incluido).

       O QUE VAI AO AR MEDE-SE COMO VAI AO AR.

   AJUSTE DECLARADO (missao CASCO-HOJE-MINIMO-HONESTO, itens 1, 2 e 8; D97): a tela
   principal do Portafoglio desenha so os 2 cruzamentos que SAO objeto do pote; os
   outros 84 abrem por clique na aba «rifiutati» — as provas dos 86, dos 5 A
   CONFIRMAR e dos 47 candidatos correm la, sem uma a menos. #etichette e a Label
   Intelligence como PRODUTO DE FERRAMENTA: prova propria, sem o pote.        */
import { serve, open, CLIENT } from '../lib/drive.mjs';
import fs from 'node:fs';
import path from 'node:path';

const G = '\x1b[32m', R = '\x1b[31m', X = '\x1b[0m';
const linhas = [];
const ok = (t, cond, medido) => { linhas.push({ t, cond: !!cond, medido }); };
const ANALISE = JSON.parse(fs.readFileSync(path.resolve(CLIENT, '..', '..', 'docs/casco/r7/ANALISE-R7.json'), 'utf8'));

const PORT = 8981;
const server = await serve(PORT);
const S = await open({ port: PORT, width: 1440, height: 1000 });
const pg = S.page;
const ir = async (h) => { await pg.goto(`http://localhost:${PORT}/portale.html${h}`, { waitUntil: 'networkidle' }); await pg.waitForTimeout(600); };

const ROTAS = ['meeting', 'radarfuturo', 'future', 'windows', 'market', 'voices', 'competitors', 'science',
  'portfolio', 'etichette', 'archive', 'sources'];
const semPote = [], semFaixa = [], vazou = [];
for (const r of ROTAS) {
  await ir('#' + r);
  const t = await pg.evaluate(() => document.body.innerText);
  if (r === 'etichette') {
    if (!(await pg.locator('[data-label-ferramenta="PRODUTO_DE_FERRAMENTA"]').count()) || !/PRODOTTO DI STRUMENTO/.test(t)) semPote.push(r);
    if (/\{\{|undefined/.test(t)) vazou.push(r);
    continue;
  }
  if (!(await pg.locator('[data-view="pote"]').count())) semPote.push(r);
  if (!/D114/.test(t) || !/EXPERIMENTAL/.test(t)) semFaixa.push(r);
  if (/\{\{|undefined/.test(t)) vazou.push(r);
}
ok('11 rotas desenham o pote; #etichette o produto de ferramenta', semPote.length === 0, semPote.join(',') || '12/12');
ok('faixa D114 e marca EXPERIMENTAL em toda rota do pote', semFaixa.length === 0, semFaixa.join(',') || '11/11');
ok('nenhuma rota deixa escapar {{ ou undefined', vazou.length === 0, vazou.join(',') || '0');

await ir('#portfolio');
const principal = await pg.locator('[data-cruzamento]').count();
const principalNoPote = await pg.locator('[data-cruzamento][data-cruz-no-pote="true"]').count();
ok('a tela principal do Portafoglio so desenha os 2 cruzamentos que sao objeto do pote', principal === 2 && principalNoPote === 2, principal);
const prov = await pg.locator('[data-cruzamento] [data-provisorio="1"]').count();
const carimbo = (await pg.locator('[data-carimbo-referencia]').allInnerTexts()).join(' ');
ok('o carimbo da referencia diz registro, ultima verifica e o frescor', /registro del \d{2}\/\d{2}/.test(carimbo) && /ultima verifica \d{2}\/\d{2}/.test(carimbo) && /PODE_ESTAR_DESATUALIZADO/.test(carimbo), carimbo.slice(0, 90));
await pg.locator('[data-aba="recusados"]').click();
await pg.waitForTimeout(500);
const cruz = principal + await pg.locator('[data-cruzamento]').count();
const sim = await pg.locator('[data-cruzamento][data-cruz-estado="POSSIBLE_ANSWER_YES_A_CONFIRMAR"]').count();
const marcas = await pg.locator('[data-cruzamento] [data-marca="1"]').allInnerTexts();
const cand = await pg.locator('[data-cruzamento] [data-via="EXTENSAO_DECLARADA"]').count();
ok('pote (2) + aba rifiutati (84) = os 86 cruzamentos da analise, cada um com PROVVISORIO', cruz === ANALISE.CROSSINGS.length && cruz === 86 && prov === 2 && (await pg.locator('[data-cruzamento] [data-provisorio="1"]').count()) === 84, cruz);
ok('so os 5 «sim» levam A CONFIRMAR', sim === 5 && marcas.length === 5 && marcas.every((m) => m.trim() === 'A CONFIRMAR'), sim + ' / ' + marcas.length);
ok('os 47 da extensao declarada dizem FONTE CANDIDATA', cand === 47, cand);
const relogio = await pg.evaluate(() => document.querySelector('.sn-aside').innerText);
ok('o relogio diz a copia da Sala (27 SET 2026), nao «oggi»', /27 SET 2026/.test(relogio) && !/\bOGGI\b/i.test(relogio),
  (relogio.match(/DATI AL[^\n]*/) || [''])[0]);

await pg.getByText('Rete Commerciale di Ca', { exact: false }).first().click();
await pg.waitForTimeout(600);
const campo = await pg.evaluate(() => document.body.innerText);
ok('a Rete Commerciale abre no vazio do pote, marcada SIMULATO',
  (await pg.locator('[data-pote-campo]').count()) === 1 && /SIMULATO/.test(campo) && /CASCO_SEM_CONTRATO_DE_INTELLIGENCE/.test(campo), '');

await pg.setViewportSize({ width: 390, height: 844 });
const larga = [];
for (const r of ROTAS) {
  await ir('#' + r);
  const w = await pg.evaluate(() => document.documentElement.scrollWidth);
  if (w > 392) larga.push(r + '=' + w);
}
ok('a 390 px nenhuma rota rola na horizontal', larga.length === 0, larga.join(',') || '0');
ok('nenhum erro de pagina', S.errors.length === 0, S.errors.slice(0, 3).join(' | ') || '0');
ok('nenhum pedido falhado (404 incluido)', S.failed.length === 0, S.failed.slice(0, 3).join(' | ') || '0');

await S.browser.close();
server.close();
let f = 0;
for (const l of linhas) {
  if (!l.cond) f++;
  console.log(`  ${l.cond ? `${G}PASS${X}` : `${R}FAIL${X}`}  ${l.t}  · ${l.medido}`);
}
console.log(`\n  PP1 · ${linhas.length - f}/${linhas.length} passing`);
process.exit(f ? 1 : 0);
