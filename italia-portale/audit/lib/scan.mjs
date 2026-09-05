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

/** Every read `<alias>.SYMBOL` with its line, column, marker and snippet. */
export function scanFile(file, dir = CLIENT) {
  const p = path.join(dir, file);
  if (!fs.existsSync(p)) return { file, missing: true, reads: [], aliases: [] };
  const src = fs.readFileSync(p, 'utf8');
  const aliases = fixtureAliases(src);
  if (!aliases.size) return { file, reads: [], aliases: [] };

  const reads = [];
  const aliasAlt = [...aliases].map((a) => a.replace(/\$/g, '\\$')).join('|');
  const re = new RegExp(`\\b(${aliasAlt})\\s*(?:\\.\\s*([A-Za-z_$][\\w$]*)|\\[)`, 'g');

  src.split('\n').forEach((line, i) => {
    let m;
    re.lastIndex = 0;
    while ((m = re.exec(line))) {
      const symbol = m[2] || '[computed]';
      const mk = markerBefore(line, m.index);
      reads.push({
        file, line: i + 1, col: m.index, symbol, alias: m[1],
        klass: mk ? mk.klass : 'DATA_BEARING_CORE',
        reason: mk ? mk.reason : null,
        isHelper: /^(fmt|ago|inkOn|setMonths)$/.test(symbol),
        snippet: line.slice(Math.max(0, m.index - 70), m.index + 150).trim(),
      });
    }
  });
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

export function grepPackage(pattern, { dir = CLIENT, exts, files } = {}) {
  const hits = [];
  for (const p of files || walkPackage(dir, exts)) {
    const src = fs.readFileSync(p, 'utf8');
    src.split('\n').forEach((line, i) => {
      const re = new RegExp(pattern.source, pattern.flags.replace('g', '') + 'g');
      let m;
      while ((m = re.exec(line))) {
        hits.push({ file: path.relative(dir, p), line: i + 1, match: m[0], text: line.trim().slice(0, 220) });
        if (!re.global) break;
      }
    });
  }
  return hits;
}
