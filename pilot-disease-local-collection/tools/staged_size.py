"""Report the size of what is staged, largest first. Read-only."""
import os, subprocess, sys

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = subprocess.run(['git', 'diff', '--cached', '--name-only'],
                     cwd=root, capture_output=True, timeout=120)
files = [l for l in out.stdout.decode('utf-8', 'replace').split('\n') if l.strip()]
sized = []
total = 0
for f in files:
    p = os.path.join(root, f.replace('/', os.sep))
    try:
        s = os.path.getsize(p)
    except Exception:
        s = 0
    sized.append((s, f))
    total += s
sized.sort(reverse=True)
print(f'staged files = {len(files)}')
print(f'staged bytes = {total} ({total/1_048_576:.1f} MB)')
print()
for s, f in sized[:15]:
    print(f'  {s/1024:9.1f} KB  {f}')
