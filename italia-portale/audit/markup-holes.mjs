/* Resolve every {{ }} hole in one markup block against the real vals, with the
   sc-for aliases bound to a real first element — the render harness only calls
   renderVals(), so an unresolved binding is otherwise invisible. */
import fs from 'node:fs';
import { mount, usePortal } from './lib/harness.mjs';

const IDENT = /^[A-Za-z_$][\w$]*/;
function resolvePath(vals, expr) {
  const head = expr.match(IDENT);
  if (!head) return undefined;
  let cur = vals == null ? undefined : vals[head[0]];
  let i = head[0].length;
  while (i < expr.length) {
    if (expr[i] === '.') {
      const m = expr.slice(i + 1).match(IDENT) || expr.slice(i + 1).match(/^\d+/);
      if (!m) return undefined;
      cur = cur == null ? undefined : cur[m[0]];
      i += 1 + m[0].length;
    } else return undefined;
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

const file = process.argv[2];
const scratch = process.argv[3];
const view = process.argv[4];
const extra = process.argv[5] ? JSON.parse(process.argv[5]) : {};
usePortal(scratch);
const M = mount();

const src = fs.readFileSync(file, 'utf8');
const TOK = /<sc-for\b[^>]*?list="\{\{([^}]*)\}\}"[^>]*?as="([^"]*)"[^>]*>|<\/sc-for>|\{\{([\s\S]*?)\}\}/g;

for (const lang of ['it', 'en']) {
  const vals = M.vals(Object.assign({ view, lang }, extra));
  const stack = [vals];
  const bad = [];
  let m;
  TOK.lastIndex = 0;
  while ((m = TOK.exec(src))) {
    const top = stack[stack.length - 1];
    if (m[1] !== undefined) {
      const list = resolve(top, m[1]);
      if (!Array.isArray(list)) bad.push(`sc-for list="${m[1].trim()}" is ${Array.isArray(list) ? 'array' : typeof list}`);
      const item = Array.isArray(list) && list.length ? list[0] : undefined;
      if (Array.isArray(list) && !list.length) bad.push(`EMPTY sc-for list="${m[1].trim()}" (renders nothing)`);
      stack.push(Object.assign({}, top, { [m[2]]: item, $index: 0 }));
    } else if (m[0] === '</sc-for>') {
      if (stack.length > 1) stack.pop();
    } else {
      const e = m[3].trim();
      if (resolve(top, e) === undefined) bad.push(`{{ ${e} }} UNRESOLVED`);
    }
  }
  const uniq = [...new Set(bad)];
  console.log(`${lang}: ${uniq.length} problem(s)`);
  uniq.forEach((b) => console.log('   ' + b));
}
usePortal(null);
