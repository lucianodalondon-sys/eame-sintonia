/* Flatten one markup block to the text a reader would see: every {{ }} filled,
   every sc-for expanded, every sc-if honoured. Used to eyeball the wording and
   to run the PT/EN language predicates over text the PT1 sweep cannot reach. */
import fs from 'node:fs';
import { mount, usePortal } from './lib/harness.mjs';
import { isPortuguese } from './lang.mjs';

const IDENT = /^[A-Za-z_$][\w$]*/;
function resolvePath(vals, expr) {
  const head = expr.match(IDENT);
  if (!head) return undefined;
  let cur = vals == null ? undefined : vals[head[0]];
  let i = head[0].length;
  while (i < expr.length) {
    if (expr[i] !== '.') return undefined;
    const m = expr.slice(i + 1).match(IDENT) || expr.slice(i + 1).match(/^\d+/);
    if (!m) return undefined;
    cur = cur == null ? undefined : cur[m[0]];
    i += 1 + m[0].length;
  }
  return cur;
}
function resolve(vals, src) {
  const e = String(src).trim();
  if (!e) return undefined;
  if (e === 'true') return true;
  if (e === 'false') return false;
  if (e === 'null') return null;
  if (e[0] === '!') return !resolve(vals, e.slice(1));
  if (/^-?\d+(\.\d+)?$/.test(e)) return Number(e);
  if ((e[0] === '"' || e[0] === "'") && e[e.length - 1] === e[0]) return e.slice(1, -1);
  return resolvePath(vals, e);
}

/* tag-level parse: sc-for / sc-if / closers / holes, everything else dropped */
const BAD = [];
function flatten(src, vals) {
  BAD.length = 0;
  const TOK = /<sc-for\b[^>]*?list="\{\{([^}]*)\}\}"[^>]*?as="([^"]*)"[^>]*>|<\/sc-for>|<sc-if\b[^>]*?value="\{\{([^}]*)\}\}"[^>]*>|<\/sc-if>|\{\{([\s\S]*?)\}\}/g;
  /* two passes are overkill; instead build a token list then evaluate recursively */
  const toks = [];
  let last = 0, m;
  while ((m = TOK.exec(src))) {
    toks.push(m[1] !== undefined ? { k: 'for', list: m[1], as: m[2] }
      : m[0] === '</sc-for>' ? { k: 'endfor' }
        : m[3] !== undefined ? { k: 'if', v: m[3] }
          : m[0] === '</sc-if>' ? { k: 'endif' }
            : { k: 'hole', e: m[4] });
    last = TOK.lastIndex;
  }
  let i = 0;
  function run(scope, emit, live) {
    while (i < toks.length) {
      const t = toks[i];
      if (t.k === 'endfor' || t.k === 'endif') { i++; return t.k; }
      if (t.k === 'hole') {
        if (live) {
          const v = resolve(scope, t.e);
          if (v === undefined) BAD.push(`{{ ${t.e.trim()} }} renders EMPTY (unresolved) while visible`);
          else if (v && typeof v === 'object' && !Array.isArray(v)) BAD.push(`{{ ${t.e.trim()} }} is an OBJECT -> "[object Object]" on screen`);
          else if (v !== null && typeof v !== 'boolean' && typeof v !== 'function') emit(String(v));
        }
        i++; continue;
      }
      if (t.k === 'if') {
        const on = !!resolve(scope, t.v);
        const start = i + 1; i = start;
        run(scope, emit, live && on);
        continue;
      }
      /* for */
      const list = resolve(scope, t.list);
      const arr = Array.isArray(list) ? list : [];
      const start = i + 1;
      if (!arr.length) { i = start; run(scope, emit, false); continue; }
      for (let n = 0; n < arr.length; n++) {
        i = start;
        run(Object.assign({}, scope, { [t.as]: arr[n], $index: n }), emit, live);
      }
      continue;
    }
    return 'eof';
  }
  const out = [];
  run(vals, (x) => out.push(x), true);
  return out;
}

const file = process.argv[2], scratch = process.argv[3], view = process.argv[4];
const extra = process.argv[5] ? JSON.parse(process.argv[5]) : {};
usePortal(scratch);
const M = mount();
const src = fs.readFileSync(file, 'utf8');
for (const lang of ['it', 'en']) {
  const vals = M.vals(Object.assign({ view, lang }, extra));
  const parts = flatten(src, vals);
  const bad = [...new Set(BAD)];
  const pt = [...new Set(parts.filter(isPortuguese))];
  console.log(`\n########## ${lang.toUpperCase()} · ${parts.length} rendered strings · isPortuguese hits: ${pt.length}`);
  bad.forEach((b) => console.log('  DEFECT ' + b));
  pt.forEach((p) => console.log('  PT? ' + p.slice(0, 160)));
  if (process.argv.includes('--text')) console.log(parts.join(' | '));
}
usePortal(null);
