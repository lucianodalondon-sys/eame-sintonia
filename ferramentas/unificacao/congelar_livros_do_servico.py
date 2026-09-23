"""Congelar um corte dos livros do servico vivo SEM o parar (so leitura na origem).

Le os livros duas vezes, com `--intervalo` segundos de distancia. Se os bytes
de TODOS forem iguais nas duas leituras, o bot estava parado entre voltas: o
corte e coerente entre os livros (cada livro sozinho ja e gravado de forma
atomica, mas os tres sao gravados em momentos diferentes). Se algum mudou,
espera e tenta de novo, ate `--tentativas`.

Escreve SO no `--destino` (tem de ficar fora de qualquer worktree de lane):
a copia dos livros + CORTE.json com o sha256 de cada um. E esse manifesto que
`curadoria/reconciliar_livros.py --livro-servico DIR` verifica.

Uso:
  py ferramentas/unificacao/congelar_livros_do_servico.py \
     --origem <worktree do servico>/curadoria --destino %TEMP%/corte-livros-X
"""
import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

LIVROS = ("LIFECYCLE-LEDGER-V1.json", "LIFECYCLE-EVIDENCE-V1.json",
          "LIFECYCLE-QUEUE-V1.json", "italy_contracts_curator.json",
          "RED-TEAM-TELEMETRIA-V1.json")
OBRIGATORIO = "LIFECYCLE-LEDGER-V1.json"


def ler(origem: Path) -> dict:
    out = {}
    for n in LIVROS:
        f = origem / n
        out[n] = f.read_bytes() if f.exists() else None
    return out


def valido(b: bytes) -> bool:
    try:
        json.loads(b.decode("utf-8"))
        return True
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False


def congelar(origem: Path, destino: Path, intervalo: float, tentativas: int) -> dict:
    if destino.exists() and any(destino.iterdir()):
        raise SystemExit("destino nao esta vazio: %s" % destino)
    for i in range(1, tentativas + 1):
        a = ler(origem)
        time.sleep(intervalo)
        b = ler(origem)
        mudou = [n for n in LIVROS if a[n] != b[n]]
        partido = [n for n in LIVROS if b[n] is not None and not valido(b[n])]
        if not mudou and not partido and b[OBRIGATORIO] is not None:
            destino.mkdir(parents=True, exist_ok=True)
            shas = {}
            for n, bs in b.items():
                if bs is None:
                    continue
                (destino / n).write_bytes(bs)
                shas[n] = hashlib.sha256(bs).hexdigest()
            man = {
                "CORTE_EM": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "ORIGEM": str(origem),
                "INTERVALO_S": intervalo,
                "TENTATIVA": i,
                "SHA256": shas,
                "BYTES": {n: len(bs) for n, bs in b.items() if bs is not None},
                "TRANSICOES": len(json.loads(b[OBRIGATORIO])["TRANSICOES"]),
            }
            (destino / "CORTE.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
            return man
        print("tentativa %d: mudou=%s partido=%s — outra vez" % (i, mudou, partido), file=sys.stderr)
    raise SystemExit("sem corte estavel em %d tentativas" % tentativas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origem", required=True)
    ap.add_argument("--destino", required=True)
    ap.add_argument("--intervalo", type=float, default=30.0)
    ap.add_argument("--tentativas", type=int, default=10)
    a = ap.parse_args()
    man = congelar(Path(a.origem), Path(a.destino), a.intervalo, a.tentativas)
    print(json.dumps(man, indent=1))


if __name__ == "__main__":
    main()
