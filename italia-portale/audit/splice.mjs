#!/usr/bin/env node
/* SINTONIA ITALY · BLOCK SPLICER
   ---------------------------------------------------------------------------
   portale.html holds one 1000-line render function. Twelve agents cannot edit
   it at once — so each agent instead writes ONE block to audit/blocks/<key>.js
   and validates it here, against a scratch copy. Nobody touches the shared file
   until every block is in and I assemble them bottom-up.

     node audit/splice.mjs list                 the block map
     node audit/splice.mjs try <key>            splice one block, render 26 screens
     node audit/splice.mjs show <key>           print the current text of a block
     node audit/splice.mjs assemble             apply every present block for real
     node audit/splice.mjs assemble --dry       assemble into scratch only
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { CLIENT, readPortal, mount, usePortal } from './lib/harness.mjs';
import { BLOCKS } from './blocks.mjs';
import { SCREENS } from './checks.mjs';

const HERE = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'));
const BLOCKDIR = path.join(HERE, 'blocks');
const SCRATCH = path.join(HERE, '.scratch');
fs.mkdirSync(BLOCKDIR, { recursive: true });
fs.mkdirSync(SCRATCH, { recursive: true });

const blockFile = (key) => path.join(BLOCKDIR, key + '.js');
const byKey = Object.fromEntries(BLOCKS.map((b) => [b.key, b]));

/** Replace the given blocks' line ranges, highest line first so earlier ranges stay valid. */
export function spliceInto(html, patches) {
  const lines = html.split('\n');
  const sorted = patches.slice().sort((x, y) => y.a - x.a);
  for (const p of sorted) {
    const body = p.text.replace(/\s*$/, '').split('\n');
    lines.splice(p.a - 1, p.b - p.a + 1, ...body);
  }
  return lines.join('\n');
}

function presentBlocks() {
  return BLOCKS.filter((b) => fs.existsSync(blockFile(b.key)))
    .map((b) => ({ ...b, text: fs.readFileSync(blockFile(b.key), 'utf8') }));
}

function renderReport(portalPath) {
  usePortal(portalPath);
  let m;
  try { m = mount(); } catch (e) { return { fatal: e.message, ok: 0, fails: [] }; }
  const fails = [];
  for (const sc of SCREENS) {
    for (const lang of ['it', 'en']) {
      const patch = Object.assign({ view: sc.view, lang }, sc.state || {}, sc.pick ? sc.pick(m.AM) : {});
      const r = m.tryVals(patch);
      if (!r.ok) fails.push(`${lang} · ${sc.label}: ${r.error}`);
    }
  }
  usePortal(null);
  return { ok: SCREENS.length * 2 - fails.length, total: SCREENS.length * 2, fails };
}

const cmd = process.argv[2];
const key = process.argv[3];

if (cmd === 'list' || !cmd) {
  console.log('\n  block        lines            status   title');
  console.log('  ' + '-'.repeat(92));
  for (const b of BLOCKS) {
    const has = fs.existsSync(blockFile(b.key));
    console.log(`  ${b.key.padEnd(12)} ${String(b.a + '-' + b.b).padEnd(16)} ${(has ? 'WRITTEN' : '—').padEnd(8)} ${b.title}`);
  }
  console.log('');
  process.exit(0);
}

if (cmd === 'show') {
  const b = byKey[key];
  if (!b) { console.error('unknown block:', key); process.exit(2); }
  const lines = readPortal().split('\n');
  console.log(lines.slice(b.a - 1, b.b).join('\n'));
  process.exit(0);
}

if (cmd === 'try') {
  const b = byKey[key];
  if (!b) { console.error('unknown block:', key, '\nknown:', BLOCKS.map((x) => x.key).join(', ')); process.exit(2); }
  if (!fs.existsSync(blockFile(b.key))) { console.error('no candidate written yet at', blockFile(b.key)); process.exit(2); }
  /* Splice EVERY block written so far, not just yours. client/portale.html is
     never touched while the agents work, so the line map stays frozen for
     everyone — but you still see your colleagues' landed fixes, and they see
     yours. A failure in a screen you do not own belongs to whoever owns it. */
  const all = presentBlocks();
  const out = spliceInto(readPortal(), all.map((x) => ({ a: x.a, b: x.b, text: x.text })));
  const scratch = path.join(SCRATCH, `portale.${b.key}.html`);
  fs.writeFileSync(scratch, out);
  const r = renderReport(scratch);
  if (r.fatal) { console.log('SYNTAX / MOUNT ERROR (yours or a colleague\'s):\n  ' + r.fatal); process.exit(1); }
  console.log(`\n  spliced blocks: ${all.map((x) => x.key).join(', ')}`);
  console.log(`  ${r.ok}/${r.total} screen renders pass`);
  if (r.fails.length) {
    console.log('  failures:');
    [...new Set(r.fails)].slice(0, 25).forEach((f) => console.log('    ' + f));
  }
  console.log(`  scratch: ${scratch}\n`);
  process.exit(r.fails.length ? 1 : 0);
}

if (cmd === 'assemble') {
  const dry = process.argv.includes('--dry');
  const present = presentBlocks();
  if (!present.length) { console.error('no block candidates written'); process.exit(2); }
  /* disjointness is the whole safety argument — check it, do not assume it */
  const sorted = present.slice().sort((x, y) => x.a - y.a);
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i].a <= sorted[i - 1].b) {
      console.error(`OVERLAP: ${sorted[i - 1].key} (${sorted[i - 1].a}-${sorted[i - 1].b}) and ${sorted[i].key} (${sorted[i].a}-${sorted[i].b})`);
      process.exit(2);
    }
  }
  const out = spliceInto(readPortal(), present.map((b) => ({ a: b.a, b: b.b, text: b.text })));
  const scratch = path.join(SCRATCH, 'portale.assembled.html');
  fs.writeFileSync(scratch, out);
  const r = renderReport(scratch);
  console.log(`\n  assembled ${present.length}/${BLOCKS.length} blocks: ${present.map((b) => b.key).join(', ')}`);
  if (r.fatal) { console.log('  SYNTAX / MOUNT ERROR:\n    ' + r.fatal); process.exit(1); }
  console.log(`  ${r.ok}/${r.total} screen renders pass`);
  [...new Set(r.fails)].slice(0, 30).forEach((f) => console.log('    ' + f));
  if (!dry) {
    const backup = path.join(SCRATCH, 'portale.before-assemble.html');
    fs.writeFileSync(backup, readPortal());
    fs.writeFileSync(path.join(CLIENT, 'portale.html'), out);
    console.log(`\n  WRITTEN to client/portale.html (previous copy kept at ${backup})\n`);
  } else {
    console.log(`\n  dry run only; scratch at ${scratch}\n`);
  }
  process.exit(0);
}

console.error('unknown command:', cmd);
process.exit(2);
