"""DIAGNOSTICO-SALA-V1 — leitura pura dos 76 da corrida 0a8a01dbc999da85.

SO LE. Nao chama adm.escrever(), nao abre rede, nao escreve no banco.
Entrada: a juncao derived_artifact x raw_asset (TSV tirado por SELECT) e o
LIVRO-DE-DECISOES.json. Saida: um JSON por item em stdout-ficheiro.

    py scripts/diagnostico_sala/ler_os_76.py <juncao.tsv> <raiz_derivados> <saida.json>
"""
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
from admissao import admissao as adm  # noqa: E402

CORRIDA = "0a8a01dbc999da85"


def main(tsv, raiz_derivados, saida):
    livro = json.loads((RAIZ / "data/samples/LIVRO-DE-DECISOES.json")
                       .read_text(encoding="utf-8"))
    escrito = {d["item"]: d for d in livro["DECISOES"] if CORRIDA in d.get("corrida", "")}
    out = []
    for ln in Path(tsv).read_text(encoding="utf-8").splitlines():
        did, rid, src, sha, dpath, url, rpath = ln.split("\t")
        f = Path(raiz_derivados) / dpath
        b = f.read_bytes() if f.exists() else None
        texto = b.decode("utf-8", "replace") if b else ""
        dec = escrito.get(f"derived:{did}", {})
        ev = dec.get("evidencia", {})
        uni_certo = src.split("-")[1]
        leituras = {}
        for u in ("T10", "T7", "T3", "T5"):
            r, _m, e = adm._do_universo({"texto": texto}, u, adm.PERGUNTAS_DO_UNIVERSO[u])
            leituras[u] = {"r": r, "palavras": e.get("palavras", []),
                           "noutro": e.get("achado_noutro", {})}
        out.append(dict(
            derived=int(did), raw=int(rid), source_id=src, url=url,
            sha_ok=(b is not None and hashlib.sha256(b).hexdigest() == sha),
            caracteres=len(texto),
            escrito=dec.get("resultado"), escrito_universo=dec.get("universo"),
            escrito_motivo=dec.get("motivo"),
            escrito_palavras=ev.get("palavras", []),
            escrito_noutro=ev.get("achado_noutro", {}),
            universo_da_fonte=uni_certo, leituras=leituras,
            texto_inicio=texto[:600]))
    Path(saida).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("itens", len(out), "sha_ok", sum(o["sha_ok"] for o in out),
          "com_decisao", sum(1 for o in out if o["escrito"]))


if __name__ == "__main__":
    main(*sys.argv[1:4])
