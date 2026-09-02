/* Split the render logic into disjoint edit blocks and compute, for each, the
   names it defines that later blocks still need. That contract is what lets
   twelve agents rewrite one file at the same time without breaking it. */
import fs from 'node:fs';
import path from 'node:path';
import { CLIENT, readPortal, extractLogic } from './lib/harness.mjs';

export const BLOCKS = [
  { key: 'helpers', a: 2394, b: 2463, title: 'parseField + decorate + open* handlers' },
  { key: 'head', a: 2464, b: 2601, title: 'renderVals head · i18n · dataState · radar filter · KPI · regions' },
  { key: 'nav', a: 2602, b: 2613, title: 'nav counters' },
  { key: 'case', a: 2614, b: 2634, title: 'opportunity detail' },
  { key: 'calendar', a: 2635, b: 2866, title: 'crop calendar · rolling business timeline · preparation clock' },
  { key: 'windows', a: 2867, b: 2888, title: 'crop windows list + detail' },
  { key: 'signal', a: 2889, b: 2907, title: 'future signal detail' },
  { key: 'market', a: 2908, b: 2996, title: 'market pulse' },
  { key: 'product', a: 2997, b: 3024, title: 'product intelligence' },
  { key: 'portfolio', a: 3025, b: 3048, title: 'portafoglio' },
  { key: 'voci', a: 3049, b: 3081, title: 'voci dal campo' },
  { key: 'brief', a: 3082, b: 3094, title: 'action brief' },
  { key: 'field', a: 3095, b: 3131, title: 'field sales integration demo' },
  { key: 'future', a: 3132, b: 3155, title: 'future radar feed' },
  { key: 'competitor', a: 3156, b: 3187, title: 'competitor watch' },
  { key: 'science', a: 3188, b: 3316, title: 'scientific intelligence' },
  { key: 'archive', a: 3317, b: 3375, title: 'archive · sources · news · people' },
  { key: 'search', a: 3376, b: 3459, title: 'global search + the returned props object' },
];

const lines = readPortal().split('\n');
const textOf = (bl) => lines.slice(bl.a - 1, bl.b).join('\n');

/* names a block declares at any depth */
const declared = (src) => {
  const out = new Set();
  const re = /(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)/g;
  let m;
  while ((m = re.exec(src))) out.add(m[1]);
  return out;
};
/* identifiers a block mentions */
const mentioned = (src) => {
  const out = new Set();
  const re = /\b([A-Za-z_$][\w$]*)\b/g;
  let m;
  while ((m = re.exec(src))) out.add(m[1]);
  return out;
};

export function blockContracts() {
  const info = BLOCKS.map((bl) => ({ ...bl, src: textOf(bl), decl: declared(textOf(bl)) }));
  return info.map((bl, i) => {
    const later = info.slice(i + 1).map((x) => x.src).join('\n');
    const used = mentioned(later);
    const mustKeep = [...bl.decl].filter((n) => used.has(n)).sort();
    const needsFromEarlier = [...mentioned(bl.src)].filter((n) =>
      info.slice(0, i).some((x) => x.decl.has(n))).sort();
    return { key: bl.key, a: bl.a, b: bl.b, title: bl.title, lines: bl.b - bl.a + 1, mustKeep, needsFromEarlier };
  });
}

if (process.argv[1] && process.argv[1].endsWith('blocks.mjs')) {
  const c = blockContracts();
  const out = c.map((b) =>
    `## ${b.key}  (portale.html ${b.a}-${b.b}, ${b.lines} lines) — ${b.title}\n` +
    `MUST STILL DEFINE (later blocks read these): ${b.mustKeep.join(', ') || '(nothing)'}\n` +
    `MAY READ FROM EARLIER BLOCKS: ${b.needsFromEarlier.join(', ') || '(nothing)'}\n`
  ).join('\n');
  fs.writeFileSync(path.join(CLIENT, '..', 'audit', 'BLOCK-CONTRACTS.md'), out);
  console.log(out);
}
