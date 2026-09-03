/* SINTONIA · INVENTARIO — o que existe, medido no navegador
   ---------------------------------------------------------------------------
   node audit/inventory.mjs [--out file.json] [--shots dir]

   Antes de corrigir, contar. Este script nao julga: percorre as telas pela
   navegacao real, clica em cada elemento clicavel uma vez, e escreve o que viu.
   O relatorio que sai daqui e a tabela AÇÃO / ONDE / O QUE FAZ do fecho.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { serve, open, clickTitle, clickText, openCase, caseIds, screenText, clickables,
  fingerprint, computedSurvey, overflow, nav, shot, C } from './lib/drive.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const OUT = arg('out', null); const SHOTS = arg('shots', null);
const PORT = 8931;

const server = await serve(PORT);
const { browser, page, errors, noise, failed } = await open({ port: PORT });

const report = { screens: [], actions: [], surveys: {}, errors: [], failed: [], navLabels: [] };

report.navLabels = await nav(page);
const NAVS = report.navLabels.filter((l, i, a) => a.indexOf(l) === i);

/* Cada visita registra a impressao digital do ecra e todos os clicaveis. */
async function visit(name) {
  const fp = await fingerprint(page);
  const cl = await clickables(page);
  const txt = await screenText(page);
  report.screens.push({ name, ...fp, clickables: cl.length, dead: cl.filter((c) => !c.hasHandler && !c.href).length, textSample: txt.slice(0, 200).replace(/\s+/g, ' ') });
  for (const c of cl) report.actions.push({ screen: name, ...c });
  await shot(page, SHOTS, 'inv-' + name);
  return fp;
}

await visit('HOME');
report.surveys.HOME = await computedSurvey(page);
report.surveys.HOME_overflow = await overflow(page);

/* A navegacao chama-se pelo nome: title="{{ n.label }}" e o nome que o leitor le. */
for (const label of NAVS.slice(0, 24)) {
  const before = await fingerprint(page);
  const ok = await clickTitle(page, label);
  if (!ok) { report.screens.push({ name: 'NAV:' + label, error: 'nav item not clickable' }); continue; }
  const fp = await visit('NAV:' + label);
  if (fp.head === before.head && fp.chars === before.chars) report.screens[report.screens.length - 1].suspect = 'screen did not change';
}

/* O detalhe da oportunidade, e o que la existe. */
await clickTitle(page, NAVS[0] || 'Radar');
const ids = await caseIds(page);
report.caseIdsOnRadar = ids;
if (await openCase(page)) {
  await visit('CASE-DETAIL');
  report.surveys.CASE = await computedSurvey(page);
}

report.errors = errors; report.noise = noise;
report.failed = [...new Set(failed)];

await browser.close(); server.close();

/* ── o que se imprime ─────────────────────────────────────────────────────── */
const dead = report.actions.filter((a) => !a.hasHandler && !a.href);
console.log('\n  SINTONIA · INVENTARIO NO NAVEGADOR');
console.log('  ' + '─'.repeat(96));
console.log(`  telas visitadas ......... ${report.screens.length}`);
console.log(`  itens de navegacao ...... ${NAVS.length}`);
console.log(`  elementos clicaveis ..... ${report.actions.length}`);
console.log(`  sem handler nem href .... ${dead.length}`);
console.log(`  erros de consola ........ ${report.errors.length}`);
console.log(`  pedidos falhados ........ ${report.failed.length}`);
console.log(`  ruido de template ....... ${report.noise.length}`);
console.log('  ' + '─'.repeat(96));
for (const s of report.screens) {
  const flag = s.error ? C.r(s.error) : s.suspect ? C.y(s.suspect) : '';
  console.log(`  ${String(s.name).padEnd(28)} ${String(s.chars ?? '-').padStart(7)} chars  ${String(s.cases ?? 0).padStart(3)} cards  ${String(s.clickables ?? 0).padStart(4)} cta  ${flag}`);
}
if (report.errors.length) { console.log('\n  ERROS:'); report.errors.slice(0, 20).forEach((e) => console.log('   ' + C.r(e))); }
if (report.failed.length) { console.log('\n  PEDIDOS FALHADOS:'); report.failed.slice(0, 20).forEach((e) => console.log('   ' + C.r(e))); }
if (dead.length) { console.log('\n  CLICAVEIS SEM ACAO (amostra):'); dead.slice(0, 20).forEach((d) => console.log(`   ${d.screen} · <${d.tag}> "${d.text}"`)); }

const survey = report.surveys.HOME || {};
const top = (o, n = 12) => Object.entries(o || {}).sort((a, b) => b[1] - a[1]).slice(0, n).map(([k, v]) => `${k} ×${v}`);
console.log('\n  HOME · fundos calculados:  ' + top(survey.bg).join('  ·  '));
console.log('  HOME · cores de texto:     ' + top(survey.color).join('  ·  '));
console.log('  HOME · familias de fonte:  ' + top(survey.font).join('  ·  '));
console.log('  HOME · raios:              ' + top(survey.radius).join('  ·  '));
console.log('  HOME · titulos em CAPS:    ' + (survey.caps || []).length);
(survey.caps || []).slice(0, 10).forEach((c) => console.log(`     ${c.size}px  "${c.text}"`));
const ov = report.surveys.HOME_overflow || {};
console.log(`\n  HOME · largura doc ${ov.docWidth} · scroll ${ov.scrollWidth} · transbordos ${(ov.offenders || []).length}`);

if (OUT) { fs.mkdirSync(path.dirname(OUT), { recursive: true }); fs.writeFileSync(OUT, JSON.stringify(report, null, 1)); console.log('\n  ' + OUT); }
