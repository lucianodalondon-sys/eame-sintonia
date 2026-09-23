"""Ensaio X1 — congela ficheiros que a ferramenta da unificacao nao congela (extras do bot, livros da ponte).

    py ferramentas/cutover/congelar_extras.py <destino> <intervalo_s> ROTULO=CAMINHO [...]

Duas leituras a <intervalo_s>; so grava se os bytes de TODOS baterem (ate 5 tentativas).
CORTE.json com sha256. Medido: o estado do observador (PONTE-AUTOMATICA-STATE.json) muda a
cada volta — nao e livro, nao se congela por aqui.
"""
import hashlib, json, sys, time
from pathlib import Path
destino = Path(sys.argv[1]); intervalo = int(sys.argv[2]); pares = sys.argv[3:]   # rotulo=caminho
def ler():
    return {r: Path(c).read_bytes() if Path(c).exists() else None for r, c in (p.split("=", 1) for p in pares)}
for t in range(5):
    a = ler(); time.sleep(intervalo); b = ler()
    if a == b:
        break
    print("mudou entre leituras, tentativa", t + 1, [k for k in a if a[k] != b[k]])
else:
    raise SystemExit("NAO CONGELOU: os livros mudaram em todas as tentativas")
destino.mkdir(parents=True, exist_ok=True)
man = {}
for r, v in b.items():
    if v is None:
        man[r] = None; continue
    (destino / r).write_bytes(v)
    man[r] = {"SHA256": hashlib.sha256(v).hexdigest(), "BYTES": len(v)}
(destino / "CORTE.json").write_text(json.dumps({"INTERVALO_S": intervalo, "FICHEIROS": man}, indent=1), encoding="utf-8")
print(json.dumps(man, indent=1)[:1500])
