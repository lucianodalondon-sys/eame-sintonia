import { serve, open, clickTitle, screenText } from '../italia-portale/audit/lib/drive.mjs';

const srv = serve(8997, process.env.DIR);
const { browser, page } = await open({ port: 8997 });

const navTitles = await page.evaluate(() =>
  [...new Set([...document.querySelectorAll('[title]')].map((e) => e.getAttribute('title')).filter(Boolean))]);
const RADAR = navTitles.find((n) => /radar/i.test(n) && !/futur/i.test(n));
await clickTitle(page, RADAR);

const m = await page.evaluate(() => {
  const AM = window.ITALY_APP_MODEL, M = AM.MEETING;
  const recs = AM.collections.opportunities.records;
  /* Does any presentation case reach the canonical population? D.CASES carry
     IT-OPP-* ids; the engine's carry OPP_*. Counting the shapes is cheaper and
     harder to fool than trusting a flag. */
  const legacyShaped = recs.filter((o) => !/^OPP_[0-9A-F]+$/.test(o.id)).map((o) => o.id);
  return {
    TOTAL: M.total,
    PUBLISHABLE: M.byPublicationState.PUBLISHABLE,
    VALIDATION_REQUIRED: M.byPublicationState.VALIDATION_REQUIRED,
    ACT_NOW: M.byStatus.ACT_NOW, VALIDATE_NOW: M.byStatus.VALIDATE_NOW,
    PREPARE: M.byStatus.FUTURE_PREPARATION, WATCH: M.byStatus.WATCH,
    TO_VALIDATE: M.byStatus.TO_VALIDATE,
    WINDOW_DEFINED: M.byWindowDefined.YES,
    WINDOW_OPEN_NOW_YES: M.byWindowOpenNow.YES,
    SOURCE_HEAD: M.sourceHead, BUILD_ID: M.buildId, CUTOFF: M.cutoff,
    modelRecords: recs.length, legacyShapedInCanonical: legacyShaped,
    demoScenariosCollection: (AM.collections.opportunityScenarios || { records: [] }).records.length,
  };
});
console.log(JSON.stringify(m, null, 1));

/* The counters as the reader sees them, not as the model holds them. */
const txt = await screenText(page);
const kpi = txt.split('\n').map((s) => s.trim()).filter(Boolean).slice(0, 40);
console.log('\nSCREEN (first lines):', kpi.slice(0, 12).join(' | '));

await browser.close(); if (srv && srv.close) srv.close(); process.exit(0);
