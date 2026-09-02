/* SINTONIA ITALY · LEGACY-FIXTURE SCANNER
   ---------------------------------------------------------------------------
   Counts every read of the legacy demo fixture (window.ITALY_DEMO) in the
   application code and classifies it.

   THE CLASSIFICATION CANNOT BE FAKED BY RENAMING.

   1. The scanner does not look for the letter "D". It first resolves every
      identifier bound to window.ITALY_DEMO or this.D(), then counts reads
      through ANY of those aliases. Aliasing the fixture to escape the count
      makes the count go UP, not down.
   2. A read is DATA_BEARING_CORE by default. It is only downgraded when the
      author wrote an explicit marker immediately before it — see MARKERS below.
      VISUAL_ONLY means the read supplies icon, colour, order, group or layout
      and no fact. EXPLICIT_DEMO means the read belongs to a labelled,
      default-off demo path that feeds no real count and no real evidence.
      Each marker carries its reason inline, so the claim is reviewable.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { CLIENT } from './harness.mjs';

/* Files that hold application logic. Pure data blobs are excluded: they DEFINE
   the fixture, they do not read it. */
export const CODE_FILES = ['portale.html', 'italy-app-model.js', 'italy-briefs.js', 'accesso.html'];

/* Marker tokens. Written in source as a block comment immediately before the
   read, e.g.  color: MARK_V('category tint only') D.DEPT[k].color
   is expressed here as the literal comment prefix. */
export const MARKERS = {
  VISUAL_ONLY: '@VISUAL_ONLY',
  EXPLICIT_DEMO: '@EXPLICIT_DEMO',
};

/** Identifiers bound to the legacy fixture in a given source text. */
export function fixtureAliases(src) {
  const aliases = new Set();
  const patterns = [
    /(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:window\.)?ITALY_DEMO\b/g,
    /(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*this\.D\(\)/g,
  ];
  for (const re of patterns) {
    let m;
    while ((m = re.exec(src))) aliases.add(m[1]);
  }
  return aliases;
}

/**
 * Is the read at `col` preceded by a classification marker?
 * The marker must be the last thing on the line before the read, so it cannot
 * be borrowed from an unrelated comment earlier in the line.
 */
function markerBefore(line, col) {
  const before = line.slice(0, col).replace(/\s+$/, '');
  if (!before.endsWith('*/')) return null;
  const open = before.lastIndexOf('/*');
  if (open < 0) return null;
  const body = before.slice(open + 2, before.length - 2);
  for (const [klass, token] of Object.entries(MARKERS)) {
    if (body.includes(token)) return { klass, reason: body.replace(token, '').trim() };
  }
  return null;
}

/**
 * Mark every character of a source as code, comment or string.
 *
 * Without this the count is nonsense in exactly the wrong direction: a good
 * migration leaves comments like "this used to read D.ARCHIVE (448 rows)", and
 * a regex over raw lines scores each of those as a surviving fixture read. The
 * headline number has to mean what it says, so the scanner tokenizes first.
 */
export function codeMask(src) {
  const mask = new Uint8Array(src.length); // 0 code · 1 comment · 2 string
  let i = 0;
  const n = src.length;
  let state = 0; // 0 code, 1 line comment, 2 block comment, 3 ' 4 " 5 ` 6 html comment
  while (i < n) {
    const c = src[i], d = src[i + 1];
    if (state === 0) {
      if (c === '/' && d === '/') { state = 1; mask[i] = mask[i + 1] = 1; i += 2; continue; }
      if (c === '/' && d === '*') { state = 2; mask[i] = mask[i + 1] = 1; i += 2; continue; }
      if (c === '<' && src.startsWith('<!--', i)) { state = 6; for (let k = 0; k < 4; k++) mask[i + k] = 1; i += 4; continue; }
      if (c === "'") { state = 3; mask[i] = 2; i++; continue; }
      if (c === '"') { state = 4; mask[i] = 2; i++; continue; }
      if (c === '`') { state = 5; mask[i] = 2; i++; continue; }
      i++; continue;
    }
    if (state === 1) { mask[i] = 1; if (c === '\n') state = 0; i++; continue; }
    if (state === 2) { mask[i] = 1; if (c === '*' && d === '/') { mask[i + 1] = 1; i += 2; state = 0; continue; } i++; continue; }
    if (state === 6) { mask[i] = 1; if (src.startsWith('-->', i)) { mask[i + 1] = mask[i + 2] = 1; i += 3; state = 0; continue; } i++; continue; }
    /* strings: honour the escape, and let a newline end a quoted string so an
       apostrophe in a comment cannot swallow the rest of the file */
    mask[i] = 2;
    if (c === '\\') { if (i + 1 < n) mask[i + 1] = 2; i += 2; continue; }
    if ((state === 3 && c === "'") || (state === 4 && c === '"') || (state === 5 && c === '`')) { state = 0; i++; continue; }
    if (c === '\n' && state !== 5) { state = 0; i++; continue; }
    i++;
  }
  return mask;
}

/** Every read `<alias>.SYMBOL` with its line, column, marker and snippet. */
export function scanFile(file, dir = CLIENT) {
  const p = path.join(dir, file);
  if (!fs.existsSync(p)) return { file, missing: true, reads: [], aliases: [] };
  const src = fs.readFileSync(p, 'utf8');
  const aliases = fixtureAliases(src);
  if (!aliases.size) return { file, reads: [], aliases: [] };

  const reads = [];
  const mask = codeMask(src);
  const aliasAlt = [...aliases].map((a) => a.replace(/\$/g, '\\$')).join('|');
  const re = new RegExp(`\\b(${aliasAlt})\\s*(?:\\.\\s*([A-Za-z_$][\\w$]*)|\\[)`, 'g');

  /* line start offsets, so a match's file position gives its line and column */
  const starts = [0];
  for (let i = 0; i < src.length; i++) if (src[i] === '\n') starts.push(i + 1);
  const lineOf = (pos) => { let lo = 0, hi = starts.length - 1; while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (starts[mid] <= pos) lo = mid; else hi = mid - 1; } return lo; };

  let m;
  re.lastIndex = 0;
  while ((m = re.exec(src))) {
    /* a mention inside a comment or a string is documentation, not a read */
    if (mask[m.index] !== 0) continue;
    const li = lineOf(m.index);
    const line = src.slice(starts[li], starts[li + 1] !== undefined ? starts[li + 1] - 1 : src.length);
    const col = m.index - starts[li];
    const symbol = m[2] || '[computed]';
    const mk = markerBefore(line, col);
    reads.push({
      file, line: li + 1, col, symbol, alias: m[1],
      klass: mk ? mk.klass : 'DATA_BEARING_CORE',
      reason: mk ? mk.reason : null,
      isHelper: /^(fmt|ago|inkOn|setMonths)$/.test(symbol),
      snippet: line.slice(Math.max(0, col - 70), col + 150).trim(),
    });
  }
  return { file, reads, aliases: [...aliases] };
}

export function scanAll(dir = CLIENT, files = CODE_FILES) {
  const per = files.map((f) => scanFile(f, dir));
  const reads = per.flatMap((r) => r.reads);
  const counted = reads.filter((r) => !r.isHelper);
  const bySymbol = {};
  for (const r of counted) {
    const b = (bySymbol[r.symbol] = bySymbol[r.symbol] || { total: 0, core: 0, visual: 0, demo: 0 });
    b.total++;
    if (r.klass === 'DATA_BEARING_CORE') b.core++;
    else if (r.klass === 'VISUAL_ONLY') b.visual++;
    else b.demo++;
  }
  return {
    per, reads,
    counts: {
      total: counted.length,
      DATA_BEARING_CORE: counted.filter((r) => r.klass === 'DATA_BEARING_CORE').length,
      VISUAL_ONLY: counted.filter((r) => r.klass === 'VISUAL_ONLY').length,
      EXPLICIT_DEMO: counted.filter((r) => r.klass === 'EXPLICIT_DEMO').length,
      helpers: reads.filter((r) => r.isHelper).length,
    },
    bySymbol,
    dataBearing: counted.filter((r) => r.klass === 'DATA_BEARING_CORE'),
    aliases: [...new Set(per.flatMap((r) => r.aliases))],
  };
}

/* ── generic source greps used by several checks ──────────────────────────── */

export function walkPackage(dir = CLIENT, exts = ['.html', '.js', '.md', '.json', '.css']) {
  const out = [];
  const walk = (d) => {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) { if (e.name !== 'assets') walk(p); continue; }
      if (exts.includes(path.extname(e.name))) out.push(p);
    }
  };
  walk(dir);
  return out;
}

/**
 * Grep the package. With codeOnly, matches inside comments are skipped — a
 * migration that documents what it removed would otherwise be scored as still
 * containing it.
 */
export function grepPackage(pattern, { dir = CLIENT, exts, files, codeOnly = false } = {}) {
  const hits = [];
  for (const p of files || walkPackage(dir, exts)) {
    const src = fs.readFileSync(p, 'utf8');
    const mask = codeOnly ? codeMask(src) : null;
    const starts = [0];
    for (let i = 0; i < src.length; i++) if (src[i] === '\n') starts.push(i + 1);
    const re = new RegExp(pattern.source, pattern.flags.includes('g') ? pattern.flags : pattern.flags + 'g');
    let m;
    while ((m = re.exec(src))) {
      if (mask && mask[m.index] === 1) continue;
      let lo = 0, hi = starts.length - 1;
      while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (starts[mid] <= m.index) lo = mid; else hi = mid - 1; }
      const line = src.slice(starts[lo], starts[lo + 1] !== undefined ? starts[lo + 1] - 1 : src.length);
      hits.push({ file: path.relative(dir, p), line: lo + 1, match: m[0], text: line.trim().slice(0, 220) });
    }
  }
  return hits;
}
