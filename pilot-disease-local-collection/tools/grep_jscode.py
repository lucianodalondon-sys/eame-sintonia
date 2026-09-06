import json, sys, re

d = json.load(open(sys.argv[1], encoding='utf-8'))
needles = sys.argv[2:]
for bid, b in (d.get('blocks') or {}).items():
    js = b.get('jscode')
    if not js:
        continue
    lines = js.split('\n')
    for i, ln in enumerate(lines):
        if any(n in ln for n in needles):
            lo = max(0, i - 6)
            hi = min(len(lines), i + 10)
            print(f'----- line {i+1}')
            for j in range(lo, hi):
                mark = '>>' if j == i else '  '
                print(f'{mark} {lines[j][:220]}')
