#!/usr/bin/env node
/* SINTONIA ITALY · CHECK RUNNER
   node audit/run.mjs               human table
   node audit/run.mjs --json        machine readable
   node audit/run.mjs --only=D1,F3  a subset
   node audit/run.mjs --verbose     print every detail
   Exit code 0 only when every check passes. */
import { runAll } from './checks.mjs';

const argv = process.argv.slice(2);
const arg = (k) => { const a = argv.find((x) => x.startsWith(`--${k}=`)); return a ? a.split('=')[1] : null; };
const has = (k) => argv.includes(`--${k}`);

const only = arg('only') ? arg('only').split(',').map((s) => s.trim()) : null;
const results = runAll(only);

if (has('json')) {
  console.log(JSON.stringify({ results, passed: results.filter((r) => r.pass).length, total: results.length }, null, 2));
  process.exit(results.every((r) => r.pass) ? 0 : 1);
}

const G = '\x1b[32m', R = '\x1b[31m', DIM = '\x1b[2m', X = '\x1b[0m';
const pad = (s, n) => String(s).slice(0, n).padEnd(n);

console.log('');
console.log('  SINTONIA ITALY · STRUCTURAL CHECKS');
console.log('  ' + '─'.repeat(96));
for (const r of results) {
  const mark = r.pass ? `${G}PASS${X}` : `${R}FAIL${X}`;
  console.log(`  ${mark}  ${pad(r.id, 5)} ${pad(r.title, 58)} ${DIM}exp${X} ${pad(r.expected, 12)} ${DIM}got${X} ${r.measured}`);
  if ((!r.pass || has('verbose')) && r.detail !== undefined) {
    const d = Array.isArray(r.detail) ? r.detail : [r.detail];
    for (const line of d.slice(0, has('verbose') ? 40 : 12)) {
      console.log(`        ${DIM}${typeof line === 'string' ? line.slice(0, 150) : JSON.stringify(line).slice(0, 150)}${X}`);
    }
  }
}
const ok = results.filter((r) => r.pass).length;
console.log('  ' + '─'.repeat(96));
console.log(`  ${ok}/${results.length} passing${ok === results.length ? '' : `  ${R}${results.length - ok} failing${X}`}`);
console.log('');
process.exit(ok === results.length ? 0 : 1);
