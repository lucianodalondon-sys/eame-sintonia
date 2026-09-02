import fs from 'fs';
const a = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const b = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
let n = 0;
for (const k of Object.keys(a)) {
  const A = JSON.stringify(a[k]), B = JSON.stringify(b[k]);
  if (A === B) continue;
  if (Array.isArray(a[k])) {
    a[k].forEach((v, i) => {
      const w = b[k][i];
      if (JSON.stringify(v) !== JSON.stringify(w)) { n++; console.log('DIFF ' + k + '[' + i + ']\n  - ' + String(v).slice(0, 700) + '\n  + ' + String(w).slice(0, 700)); }
    });
    if (a[k].length !== b[k].length) { n++; console.log('LEN ' + k + ' ' + a[k].length + ' -> ' + b[k].length); }
  } else { n++; console.log('DIFF ' + k + '\n  - ' + A.slice(0, 700) + '\n  + ' + B.slice(0, 700)); }
}
console.log('--- ' + n + ' diffs');
