"""Ensaio X1 — resolvedor de conflitos por SIGNIFICADO para juntar pontas numa COPIA (nunca numa lane).

    py ferramentas/cutover/resolver_conflitos_ensaio.py <repo de ensaio> <nome da ponta> <registo.json>

Gerados (system-map/data/*.generated.json, state.generated.json, docs/operacao/CENSO-*,
docs/fontes/INDICE-DE-FONTES.md): lado base — regerados no fim pela cadeia. Know-how: os dois
lados, base primeiro (secoes acrescentadas). Resto: NAO resolve — lista para ler a mao.
Cada escolha fica no registo. Usado no ensaio X1 (6 pontas, 7 blocos a mao).
"""
import json, re, subprocess, sys
from pathlib import Path
R = Path(sys.argv[1]); ponta = sys.argv[2]; reg = Path(sys.argv[3])
fic = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], cwd=R, capture_output=True, text=True).stdout.split()
GER = re.compile(r"(\.generated\.json$|^docs/operacao/CENSO-|^docs/fontes/INDICE-DE-FONTES\.md$)")
log = json.loads(reg.read_text(encoding="utf-8")) if reg.exists() else []
falta = []
for f in fic:
    p = R / f
    if GER.search(f):
        subprocess.run(["git", "checkout", "--ours", "--", f], cwd=R, check=True)
        subprocess.run(["git", "add", f], cwd=R, check=True)
        log.append({"PONTA": ponta, "FICHEIRO": f, "ESCOLHA": "BASE (gerado; regerado no fim pela cadeia)"})
    elif f.endswith("KNOW-HOW.md"):
        s = open(p, encoding="utf-8", newline="").read()
        n = len(re.findall(r"^<<<<<<< ", s, re.M))
        s = re.sub(r"^<<<<<<< [^\n]*\n(.*?)^=======\r?\n(.*?)^>>>>>>> [^\n]*\n",
                   lambda m: m.group(1) + m.group(2), s, flags=re.S | re.M)
        assert "<<<<<<<" not in s
        open(p, "w", encoding="utf-8", newline="").write(s)
        subprocess.run(["git", "add", f], cwd=R, check=True)
        log.append({"PONTA": ponta, "FICHEIRO": f, "ESCOLHA": "OS DOIS LADOS (%d blocos, base primeiro)" % n})
    else:
        falta.append(f)
reg.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
print("RESOLVIDOS", len(fic) - len(falta), "| A MAO:", falta)
