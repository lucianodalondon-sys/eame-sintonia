import { serve, open, screenText, caseIds } from '../italia-portale/audit/lib/drive.mjs';
const srv = serve(8991, process.env.DIR);
const { browser, page, errors, failed } = await open({ port: 8991 });
const nav = await page.evaluate(() => [...new Set([...document.querySelectorAll('[title]')].map(e=>e.getAttribute('title')).filter(Boolean))]);
console.log('NAV:', JSON.stringify(nav.slice(0,14)));
console.log('entries matching /radar/i :', JSON.stringify(nav.filter(n=>/radar/i.test(n))));
const t = await screenText(page);
console.log('DEFAULT SCREEN (first lines):', t.split('\n').filter(Boolean).slice(0,3).join(' | '));
console.log('cards on the default screen:', (await caseIds(page)).length);
const m = await page.evaluate(()=>{
  const AM=window.ITALY_APP_MODEL;
  return { meetingTotal: AM.MEETING && AM.MEETING.total, counts: AM.MEETING && {
    pub: AM.MEETING.byPublicationState, st: AM.MEETING.byStatus,
    wdef: AM.MEETING.byWindowDefined, wopen: AM.MEETING.byWindowOpenNow,
    withPrimary: AM.MEETING.withPrimary, withoutPrimary: AM.MEETING.withoutPrimary } };
});
console.log('AM.MEETING:', JSON.stringify(m));
console.log('ERRORS', errors.length, 'FAILED', (failed||[]).length);
await browser.close(); if(srv&&srv.close)srv.close(); process.exit(0);
