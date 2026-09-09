/* REGRESSAO DE NAVEGADOR — os cabecalhos partem o portal?
 *
 * Abre as paginas reais num Chromium real, servidas com os cabecalhos reais do
 * vercel.json, e falha se alguma nao renderizar ou se o navegador recusar
 * alguma coisa por politica de seguranca.
 *
 *     UM CABECALHO QUE PARTE O PRODUTO E DESLIGADO NO DIA SEGUINTE.
 *     ENTAO PROVA-SE ANTES.
 *
 * SILENCIO NAO E SUCESSO: uma navegacao falhada, um corpo vazio ou um erro de
 * CSP contam todos como regressao. A primeira versao desta prova dizia
 * "SEM REGRESSAO" com as cinco paginas mortas por erro de ligacao — dizia-o
 * porque so procurava erros de CSP, e nao havia nenhum, porque nao havia
 * pagina nenhuma.
 */
import { existsSync } from 'node:fs';
import { chromium } from 'playwright';

const BASE = process.argv[2] || 'http://127.0.0.1:8799';
const PAGINAS = ['/', '/accesso', '/casa', '/portale', '/system-map/'];

/* O caminho do navegador nao pode ser o da maquina de quem escreveu a prova.
 * A primeira versao fixava /opt/pw-browsers/chromium, que existe no contentor
 * onde ela nasceu e nao existe no runner do GitHub — e a prova morria antes de
 * abrir uma pagina.
 *
 *     UMA PROVA QUE SO CORRE NA MAQUINA DE QUEM A ESCREVEU NAO E UMA PROVA.
 *
 * Usa-se o caminho pre-instalado quando ele existe; caso contrario deixa-se a
 * Playwright encontrar o que ela propria instalou. */
const PRE_INSTALADO = '/opt/pw-browsers/chromium';
const b = await chromium.launch(
  existsSync(PRE_INSTALADO) ? { executablePath: PRE_INSTALADO } : {});
let mau = 0;

for (const p of PAGINAS) {
  const ctx = await b.newContext();
  const pg = await ctx.newPage();
  const erros = [];
  const recusas = [];
  pg.on('console', m => { if (m.type() === 'error') erros.push(m.text().slice(0, 200)); });
  pg.on('pageerror', e => erros.push('PAGEERROR ' + String(e).slice(0, 200)));
  pg.on('requestfailed', r => recusas.push(`${r.failure()?.errorText} ${r.url().slice(-60)}`));

  let http = null, falha = null;
  try {
    const r = await pg.goto(BASE + p, { waitUntil: 'networkidle', timeout: 120000 });
    http = r && r.status();
  } catch (e) { falha = e.message.split('\n')[0].slice(0, 100); }
  await pg.waitForTimeout(1200);

  const texto = await pg.evaluate(() => (document.body ? document.body.innerText.length : 0)).catch(() => -1);
  const csp = [...erros, ...recusas].filter(e =>
    /Content Security Policy|Refused to (frame|load|execute|apply|connect)|blocked by CSP/i.test(e));

  const ok = !falha && http !== null && http < 400 && texto > 40 && csp.length === 0;
  if (!ok) mau++;
  console.log(`${ok ? 'OK  ' : 'MAU '} ${p.padEnd(15)} http=${http ?? falha} texto=${texto} erros=${erros.length} recusas=${recusas.length} csp=${csp.length}`);
  csp.slice(0, 3).forEach(e => console.log('     CSP:', e));
  if (!csp.length) erros.slice(0, 2).forEach(e => console.log('     erro:', e));
  await ctx.close();
}

/* ── CONTROLO POSITIVO ──────────────────────────────────────────────────────
 * As cinco paginas carregarem prova que o cabecalho nao PARTE nada. Nao prova
 * que ele FAZ alguma coisa. Um vercel.json com um erro de escrita daria
 * exactamente o mesmo verde.
 *
 *     CONTROL DECLARED != CONTROL TESTED.
 *
 * Entao tenta-se mesmo enfiar o portal dentro de um iframe. Se ele entrar, o
 * clickjacking continua possivel e este passo tem de falhar.
 */
{
  const ctx = await b.newContext();
  const pg = await ctx.newPage();

  /* Primeiro: a pagina existe mesmo?
   *
   * A versao anterior desta verificacao dizia "RECUSADO" contra um servidor que
   * nunca arrancou. Nao havia moldura porque nao havia nada — e a ausencia lia-se
   * como proteccao. Foi o controlo negativo que o mostrou, o que e o unico
   * motivo por que um controlo negativo existe.
   *
   *     UMA MOLDURA VAZIA NAO PROVA UM CABECALHO. PROVA UM SERVIDOR MORTO.
   *     INCONCLUSIVO NAO E VERDE.
   */
  let alcancavel = false;
  try {
    const r = await pg.goto(`${BASE}/accesso`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    alcancavel = !!(r && r.status() < 400);
  } catch (e) { alcancavel = false; }

  if (!alcancavel) {
    mau++;
    console.log('MAU  frame-ancestors  INCONCLUSIVO: /accesso nao responde, e sem pagina nao ha nada a enquadrar');
  } else {
    const recusado = [];
    pg.on('console', m => { if (m.type() === 'error') recusado.push(m.text()); });
    await pg.setContent(`<iframe id="alvo" src="${BASE}/accesso" width="400" height="300"></iframe>`,
                        { waitUntil: 'load' });
    await pg.waitForTimeout(2500);
    const entrou = await pg.evaluate(() => {
      const f = document.getElementById('alvo');
      try {
        return !!(f.contentDocument && f.contentDocument.body
                  && f.contentDocument.body.innerText.trim().length > 20);
      } catch (e) { return false; }   // cross-origin a serio tambem conta como recusado
    });
    const disse = recusado.some(e => /frame-ancestors|Refused to display|X-Frame-Options/i.test(e));
    if (entrou) {
      mau++;
      console.log('MAU  frame-ancestors  o portal ENTROU num iframe: o clickjacking continua possivel');
    } else if (!disse) {
      // A moldura ficou vazia e o navegador nao explicou porque. Nao chega.
      mau++;
      console.log('MAU  frame-ancestors  a moldura ficou vazia mas o navegador nao disse que a recusou: INCONCLUSIVO');
    } else {
      console.log('OK   frame-ancestors  o portal foi RECUSADO dentro de um iframe, e o navegador disse porque');
    }
  }
  await ctx.close();
}

await b.close();
console.log(mau ? `REGRESSAO DE NAVEGADOR: ${mau} de ${PAGINAS.length + 1} verificacao(oes)`
                : `SEM REGRESSAO — ${PAGINAS.length} paginas carregam e renderizam com os cabecalhos actuais`);
process.exit(mau ? 1 : 0);
