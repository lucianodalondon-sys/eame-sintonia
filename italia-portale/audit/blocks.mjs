/* Split renderVals() into disjoint edit blocks and compute, for each, the names
   it defines that later blocks still need. That contract is what lets several
   agents rewrite one file at the same time without breaking it.

   THE MAP IS DERIVED, NOT TYPED. The first version carried hand-written line
   numbers (2394-3459). The file then grew to 7073 lines, the numbers silently
   pointed into the markup instead of the logic, and assertFrozen() could not
   even be called because it did not exist. A map that ages into a lie is worse
   than no map, so every edge here is now found by searching for an ANCHOR — a
   distinctive comment the block owns — and each edge is validated to fall on a
   top-level statement boundary inside renderVals(), which is the only place a
   split is legal. Move code around freely; the map follows.  */
import fs from 'node:fs';
import path from 'node:path';
import { CLIENT, readPortal, extractLogic } from './lib/harness.mjs';
import { codeMask } from './lib/scan.mjs';

/* One anchor per block, IN FILE ORDER. The anchor is matched against the whole
   line, first hit wins, and the block runs until the next block's anchor.

   AN ANCHOR IS A CONTRACT. An agent that rewrites a block must carry its anchor
   line through, or the map loses the block entirely. Measured once: three
   agents rewrote navbadges, productintel and portafoglio, each dropped the
   comment that named it, and assertFrozen() went from a clean 42-block map to
   MAP UNUSABLE in a single assemble. Check G1 catches it; re-anchoring on a
   line the new code actually contains is the fix. */
export const ANCHORS = [
  ['head', '§3 · ITALY_APP_MODEL is now the only place this block takes a fact from'],
  ['narrative', '§THE NARRATIVE RULE'],
  ['pest', "§4 · the pest/disease/weed tile is decorate()'s job"],
  ['products', '§10 · an empty ADAMA_PRODUCTS is NOT "ADAMA has no product"'],
  ['window', '§7 · The upstream declares WINDOW.APPLICATION per record'],
  ['evidence', '§2 · every one of these was fixture-authored'],
  ['legacy', '§5 · the 29 legacy presentation cases'],
  ['live', '§19 · Live switch'],
  ['lang', '§27 · The switch set <html lang>'],
  ['radarfilter', '---- radar filtering'],
  ['reach', '§9 · REACHED_IN_ITALY (414) and the 89 multi-country'],
  ['marketpanel', '§8 · the panel publishes its own denominator'],
  ['markettemp', '§8/§13 · market "temperature" was an editorial fixture'],
  ['competitor', '§9 · REACHED_IN_ITALY (414) is not the same claim'],
  ['navgroup', '§1 · Core = external intelligence'],
  ['sources', "§8 · 'sources' counts monitored public routes only"],
  ['navbadges', 'const navIntegrations = '],
  ['accents', '§4 · The green/amber accents'],
  ['detail', '§2 · The detail must open the SAME entity the card opened'],
  ['opportunity', '§11 · The upstream opportunity feed was researched in Portuguese'],
  ['crops', '§11 · Six crop vocabularies are measured'],
  ['canonwindow', '§13 · The canonical window is a DECLARED relation'],
  ['category', '§4 · Category tint'],
  ['days', '§7 · Days remaining, bar width and ordering'],
  ['adama', '§10 · Two real sources, in this order'],
  ['convergence', '§2 · The five-bar convergence chart'],
  ['absence', '§10 · Absence in a reading is not absence in the world'],
  ['brief', '§1 · The department action map'],
  ['rows', '§7 · THE ROW UNIVERSE MOVED'],
  ['windowscreen', '§9 · Every window on this screen is now AM.collections.cropWindows'],
  ['futurecard', '§18 · A real Future card opens the SAME real entity'],
  ['major7', '§3 · MAJOR 7 · This screen was written against'],
  ['marketpulse', '§M · Market Pulse was an editorial fixture end to end'],
  ['portfoliopanel', '§M · The portfolio panel used to list demo case products'],
  ['convergencelabel', '§M · Upstream calls these'],
  ['marketgaps', '§M · Production, trade, stocks'],
  ['signaljoin', '§M · The old signal join could never match'],
  ['industry', '§M · Industry tab'],
  ['productintel', '§4 · ADAMA Product Intelligence — TWO UNIVERSES OVER ONE NAME'],
  ['portafoglio', '§4 · Portafoglio — TWO UNIVERSES, ONE SCREEN, NEVER ONE NUMBER'],
  ['voci', '§12 · Voci dal Campo'],
  ['bands', '§7 · The band split'],
  ['casefix', '§7 · MEASURED FAILURE, now fixed'],
  ['fieldsales', '§10 · Field Sales is an integration DEMONSTRATION'],
  ['fieldkpi', '§10 · The KPI strip used to add FIELD_KPI'],
  ['futuretokens', '§7 · PRESENTATION TOKENS. Authored here'],
  ['futurefeed', '§7 · The real feed. Nothing is borrowed'],
  ['competitorwatch', '§1 · Competitor Watch now reads the model'],
  ['companies', '§1 · The 14 upstream company rows are 11 companies'],
  ['density', '§8 · communication density = density inside monitored public communication'],
  ['idresolve', '§18 · An id that does not resolve must SAY so'],
  ['science', '§12 · This block used to be built on four fixtures'],
  ['themejoin', '§12 · The theme -> canonical crop window join'],
  ['caption88', '§12 · The one caption this screen cannot ship without'],
  ['gire', '§12 · GIRE · confirmed Italian herbicide-resistance cases'],
  ['taxonomy', '§7 · A taxonomic name is never truncated'],
  ['denominator', '§8 · Never an absolute negative'],
];

/** renderVals()'s own span and every legal split point inside it. */
export function renderValsSpan() {
  const { code, startLine } = extractLogic(readPortal());
  /* Count brackets in CODE ONLY. Counting them everywhere is how this map broke
     the first time: a comment on line 3238 reads  at '(' (§11)  — one unmatched
     paren inside prose — and the naive counter carried that +1 for the next
     2700 lines, so every split point below it vanished and six blocks silently
     merged into one 3830-line block. */
  const mask = codeMask(code);
  const ls = [];
  {
    let start = 0;
    for (let i = 0; i <= code.length; i++) {
      if (i === code.length || code[i] === '\n') {
        let t = '';
        for (let j = start; j < i; j++) t += mask[j] === 0 ? code[j] : ' ';
        ls.push(t);
        start = i + 1;
      }
    }
  }
  let rv = ls.findIndex((l) => /renderVals\s*\(\s*\)\s*\{/.test(l));
  if (rv < 0) throw new Error('blocks: renderVals() not found');
  let d = 0, started = false, end = -1;
  for (let i = rv; i < ls.length; i++) {
    for (const ch of ls[i]) { if (ch === '{') { d++; started = true; } else if (ch === '}') d--; }
    if (started && d === 0) { end = i; break; }
  }
  if (end < 0) throw new Error('blocks: renderVals() never closes');
  /* a split is legal only between two top-level statements of renderVals */
  d = 0;
  const edges = new Set();
  for (let i = rv + 1; i < end; i++) {
    if (d === 0 && ls[i].trim()) edges.add(startLine + i);
    for (const ch of ls[i]) {
      if (ch === '{' || ch === '(' || ch === '[') d++;
      else if (ch === '}' || ch === ')' || ch === ']') d--;
    }
  }
  return { first: startLine + rv + 1, last: startLine + end - 1, edges, startLine, lines: ls };
}

/** The current block map: [{ key, a, b, title }], a/b are 1-indexed file lines. */
export function blocks() {
  const span = renderValsSpan();
  const all = readPortal().split('\n');
  const found = ANCHORS.map(([key, anchor]) => {
    const i = all.findIndex((l, n) => n + 1 >= span.first && n + 1 <= span.last && l.includes(anchor));
    return { key, anchor, line: i < 0 ? -1 : i + 1 };
  });
  const missing = found.filter((f) => f.line < 0);
  if (missing.length) throw new Error('blocks: anchor(s) not found in renderVals: ' + missing.map((m) => m.key).join(', '));
  const sorted = [...found].sort((a, b) => a.line - b.line);
  const order = found.map((f) => f.key).join(',');
  if (sorted.map((f) => f.key).join(',') !== order) {
    throw new Error('blocks: anchors are out of order in the file — ANCHORS must list them in file order.\n  file order: ' + sorted.map((f) => f.key).join(', '));
  }
  /* An anchor names a FEATURE; it does not promise to sit at a legal cut. Most
     of these comments live inside a helper or an object literal, so the block
     opens at the nearest top-level statement at or above the anchor — the
     enclosing statement is what an editor has to own anyway. */
  const edges = [...span.edges].sort((x, y) => x - y);
  const snap = (line) => { let e = edges[0]; for (const x of edges) { if (x <= line) e = x; else break; } return e; };
  const seen = new Map();
  for (const f of sorted) {
    const at = snap(f.line);
    /* two anchors inside one statement describe one indivisible block */
    if (seen.has(at)) seen.get(at).keys.push(f.key);
    else seen.set(at, { a: at, keys: [f.key], title: f.anchor });
  }
  const starts = [...seen.values()].sort((x, y) => x.a - y.a);
  return starts.map((s, i) => ({
    key: s.keys.join('+'),
    a: s.a,
    b: i + 1 < starts.length ? starts[i + 1].a - 1 : span.last,
    title: s.title,
  }));
}

/**
 * The map is usable for parallel editing only if every edge is a legal split.
 * Throws with the offending block if not. Call this BEFORE handing ranges out.
 */
export function assertFrozen() {
  const span = renderValsSpan();
  const bs = blocks();
  const bad = [];
  for (const b of bs) {
    if (!span.edges.has(b.a)) bad.push(`${b.key} starts at ${b.a}, which is not a top-level statement of renderVals()`);
  }
  for (let i = 1; i < bs.length; i++) {
    if (bs[i].a !== bs[i - 1].b + 1) bad.push(`gap or overlap between ${bs[i - 1].key} and ${bs[i].key}`);
  }
  if (bad.length) throw new Error('blocks: map is not safe for parallel editing\n  ' + bad.join('\n  '));
  return { blocks: bs.length, from: bs[0].a, to: bs[bs.length - 1].b, lines: bs[bs.length - 1].b - bs[0].a + 1 };
}

/**
 * The MARKUP side of the same idea. The template is sectioned one screen per
 * `<sc-if value="{{ isX ...">`, so those openings are natural, disjoint edit
 * units — a second agent can rewrite the portfolio screen while a first
 * rewrites the radar, with no shared line. Ranges are 1-indexed file lines and
 * cover from one screen's opening tag to the line before the next one's.
 */
export function markupBlocks() {
  const all = readPortal().split('\n');
  const logicAt = all.findIndex((l) => l.includes('<script type="text/x-dc" data-dc-script'));
  const styleAt = all.findIndex((l) => l.includes('</style>'));
  const found = [];
  for (let i = styleAt; i < logicAt; i++) {
    const m = all[i].match(/<sc-if value="\{\{\s*(is[A-Za-z]+)/);
    if (m) found.push({ key: 'markup-' + m[1].slice(2).toLowerCase(), screen: m[1], a: i + 1 });
  }
  return found.map((f, i) => ({
    ...f,
    b: i + 1 < found.length ? found[i + 1].a - 1 : logicAt,
    title: `markup · ${f.screen}`,
  }));
}

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
  const all = readPortal().split('\n');
  const textOf = (bl) => all.slice(bl.a - 1, bl.b).join('\n');
  const info = blocks().map((bl) => ({ ...bl, src: textOf(bl), decl: declared(textOf(bl)) }));
  return info.map((bl, i) => {
    const later = info.slice(i + 1).map((x) => x.src).join('\n');
    const used = mentioned(later);
    const mustKeep = [...bl.decl].filter((n) => used.has(n)).sort();
    const needsFromEarlier = [...mentioned(bl.src)].filter((n) =>
      info.slice(0, i).some((x) => x.decl.has(n))).sort();
    return { key: bl.key, a: bl.a, b: bl.b, title: bl.title, lines: bl.b - bl.a + 1, mustKeep, needsFromEarlier };
  });
}

/* keep the old name working for callers that imported it */
export const BLOCKS = (() => { try { return blocks(); } catch { return []; } })();

if (process.argv[1] && process.argv[1].endsWith('blocks.mjs')) {
  console.log('frozen:', JSON.stringify(assertFrozen()));
  const c = blockContracts();
  const out = c.map((b) =>
    `## ${b.key}  (portale.html ${b.a}-${b.b}, ${b.lines} lines) — ${b.title}\n` +
    `MUST STILL DEFINE (later blocks read these): ${b.mustKeep.join(', ') || '(nothing)'}\n` +
    `MAY READ FROM EARLIER BLOCKS: ${b.needsFromEarlier.join(', ') || '(nothing)'}\n`
  ).join('\n');
  fs.writeFileSync(path.join(CLIENT, '..', 'audit', 'BLOCK-CONTRACTS.md'), out);
  console.log(out);
}
