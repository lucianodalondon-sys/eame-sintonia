#!/usr/bin/env node
/* SINTONIA · PORTAO DAS BARRAS DE BUSCA
   ---------------------------------------------------------------------------
   Uma barra de busca é a única peça deste portal que só existe se ALGUÉM
   DIGITAR NELA. O código pode estar certo, o modelo pode filtrar bem, e a
   barra ainda assim não servir para nada: basta que o runtime volte a montar
   o campo a cada tecla e o cursor salte fora — quem escreve «pomodoro» acaba
   com um «p» na tela e desiste.

       LER O MODELO NAO E DIGITAR NA BARRA.

   Por isso este portão abre o portal num browser de verdade e DIGITA, tecla a
   tecla, como um cliente digita. Mede quatro coisas em cada barra:

     · o texto inteiro chega ao campo (o foco não se perde entre teclas);
     · a grelha ENCOLHE — e encolhe para menos do que era antes;
     · o que sobra CONTÉM o termo procurado;
     · apagar a busca devolve exactamente a contagem inicial.

   O quarto é o controlo negativo do terceiro: um filtro que encolhe e não
   volta atrás não está a filtrar, está a partir.                            */
import { serve, open } from './lib/drive.mjs';

const G = '\x1b[32m', R = '\x1b[31m', X = '\x1b[0m';
const linhas = [];
const ok = (t, cond, medido) => { linhas.push({ t, cond: !!cond, medido }); };

/* O PORTAL NAO ABRE EM file://. O runtime do template vai buscar o proprio
   HTML por fetch, e o browser recusa-o com origem `null` — a pagina fica no
   esqueleto e QUALQUER medicao feita ali mede o esqueleto, nao o portal.
   `lib/drive.mjs` serve a pasta como a Vercel a serve; e a mesma porta que os
   outros portoes usam. */
const server = await serve(8921);
const { browser, page: pg } = await open({ port: 8921, width: 1500, height: 1000 });
await pg.waitForSelector('[data-meeting-case]', { timeout: 45000 });

/* ── 1 · O RADAR ─────────────────────────────────────────────────────────── */
const antesRadar = await pg.locator('[data-meeting-case]').count();
const barraRadar = pg.locator('[data-radar-search]');
ok('RADAR · a barra existe na tela', await barraRadar.count() === 1, await barraRadar.count());

const TERMO = 'pomodoro';
await barraRadar.click();
await pg.keyboard.type(TERMO, { delay: 30 });
await pg.waitForTimeout(400);
const escrito = await barraRadar.inputValue();
ok('RADAR · o texto inteiro chega ao campo', escrito === TERMO, JSON.stringify(escrito));

const depoisRadar = await pg.locator('[data-meeting-case]').count();
ok('RADAR · a grelha encolhe', depoisRadar > 0 && depoisRadar < antesRadar,
  antesRadar + ' → ' + depoisRadar);

/* O que sobrou tem de CONTER o termo: um filtro que encolhe ao acaso passaria
   no controlo anterior. Lê-se o texto visível da própria ficha. */
const textos = await pg.locator('[data-meeting-case]').allInnerTexts();
const casam = textos.filter((t) => t.toLowerCase().includes(TERMO)).length;
ok('RADAR · toda ficha que sobra nomeia o termo', casam === depoisRadar,
  casam + '/' + depoisRadar);

await barraRadar.fill('');
await pg.waitForTimeout(400);
const voltaRadar = await pg.locator('[data-meeting-case]').count();
ok('RADAR · apagar devolve a contagem inicial', voltaRadar === antesRadar,
  voltaRadar + ' = ' + antesRadar);

/* ── 1b · AS DUAS TENDINAS ────────────────────────────────────────────────
   A barra e as tendinas respondem a mesma pergunta por caminhos diferentes, e
   uma pode funcionar enquanto a outra nao: sao medidas em separado. Escolhe-se
   sempre a SEGUNDA opcao — a primeira e o «todas», que nao filtra nada e
   passaria neste controlo sem nunca ter filtrado. */
const escolher = async (i) => {
  const sel = pg.locator('select').nth(i);
  const vals = await sel.locator('option').evaluateAll((os) => os.map((o) => o.value));
  const alvo = vals.filter(Boolean)[0];
  await sel.selectOption(alvo);
  await pg.waitForTimeout(500);
  return alvo;
};
const cultura = await escolher(0);
const porCultura = await pg.locator('[data-meeting-case]').count();
ok('RADAR · a tendina delle colture filtra', porCultura > 0 && porCultura < antesRadar,
  cultura + ' → ' + porCultura + '/' + antesRadar);
await pg.locator('select').nth(0).selectOption('');
await pg.waitForTimeout(500);

const produto = await escolher(1);
const porProduto = await pg.locator('[data-meeting-case]').count();
ok('RADAR · a tendina dei prodotti filtra', porProduto > 0 && porProduto < antesRadar,
  produto + ' → ' + porProduto + '/' + antesRadar);
await pg.locator('select').nth(1).selectOption('');
await pg.waitForTimeout(500);
ok('RADAR · as tendinas tambem sabem voltar', await pg.locator('[data-meeting-case]').count() === antesRadar,
  await pg.locator('[data-meeting-case]').count() + ' = ' + antesRadar);

/* ── 1c · CONTROLO NEGATIVO ───────────────────────────────────────────────
   Uma grelha vazia parece um ecra partido. Quando o filtro nao deixa nada, o
   portal tem de DIZE-LO e oferecer o caminho de volta — nao ficar em branco. */
await barraRadar.click();
await pg.keyboard.type('zzzznaoexiste', { delay: 10 });
await pg.waitForTimeout(450);
ok('RADAR · zero resultados diz-se, nao se deixa em branco',
  await pg.locator('[data-meeting-case]').count() === 0 && await pg.locator('[data-radar-empty]').count() === 1,
  await pg.locator('[data-radar-empty]').count() + ' aviso');
await pg.locator('[data-radar-clear]').click();
await pg.waitForTimeout(450);
ok('RADAR · CANCELLA TUTTO devolve tudo', await pg.locator('[data-meeting-case]').count() === antesRadar,
  await pg.locator('[data-meeting-case]').count() + ' = ' + antesRadar);

/* ── 2 · O PORTAFOGLIO ───────────────────────────────────────────────────── */
await pg.evaluate(() => { location.hash = '#portfolio'; });
await pg.waitForTimeout(600);
await pg.waitForSelector('[data-expiry-slot]', { timeout: 30000 });

const antesPort = await pg.locator('[data-expiry-slot]').count();
const barraPort = pg.locator('[data-portfolio-search]');
ok('PORTAFOGLIO · a barra existe na tela', await barraPort.count() === 1, await barraPort.count());

const TERMO2 = 'folpet';
await barraPort.click();
await pg.keyboard.type(TERMO2, { delay: 30 });
await pg.waitForTimeout(400);
const escrito2 = await barraPort.inputValue();
ok('PORTAFOGLIO · o texto inteiro chega ao campo', escrito2 === TERMO2, JSON.stringify(escrito2));

const depoisPort = await pg.locator('[data-expiry-slot]').count();
ok('PORTAFOGLIO · a grelha encolhe', depoisPort > 0 && depoisPort < antesPort,
  antesPort + ' → ' + depoisPort);

await barraPort.fill('');
await pg.waitForTimeout(400);
const voltaPort = await pg.locator('[data-expiry-slot]').count();
ok('PORTAFOGLIO · apagar devolve a contagem inicial', voltaPort === antesPort,
  voltaPort + ' = ' + antesPort);

/* ── 3 · A SCADENZA, NA FICHA ────────────────────────────────────────────────
   Nao basta a pastilha existir: ela tem de dizer uma DATA onde o registo tem
   data, e dizer «non noto» onde ele cala — nunca ficar vazia, nunca as duas
   coisas ao mesmo tempo. */
const scad = await pg.locator('[data-expiry-slot]').evaluateAll((els) => els.map((e) => e.getAttribute("data-expiry")));
ok('SCADENZA · toda ficha tem a pastilha', scad.length === antesPort, scad.length + '/' + antesPort);
ok('SCADENZA · nenhuma vem vazia', scad.every((v) => v && v.trim()), scad.filter((v) => !v || !v.trim()).length + ' vazias');
const comData = scad.filter((v) => /\d{4}$/.test(v || '')).length;
const semData = scad.length - comData;
ok('SCADENZA · a data e uma data, ou e «non noto»',
  scad.every((v) => /\d{2} [A-Z]{3} \d{4}/.test(v || '') || /non noto|not known/i.test(v || '')),
  comData + ' com data · ' + semData + ' declaradas nao conhecidas');

await browser.close();
server.close();

console.log('');
console.log('  SINTONIA · BARRAS DE BUSCA E SCADENZA');
console.log('  ' + '─'.repeat(76));
for (const l of linhas) console.log(`  ${l.cond ? G + 'PASS' + X : R + 'FAIL' + X}  ${l.t.padEnd(50)} ${l.medido}`);
const mau = linhas.filter((l) => !l.cond).length;
console.log('  ' + '─'.repeat(76));
console.log(`  ${linhas.length - mau}/${linhas.length} passing` + (mau ? `  ${R}${mau} failing${X}` : ''));
console.log('');
process.exit(mau === 0 ? 0 : 1);
