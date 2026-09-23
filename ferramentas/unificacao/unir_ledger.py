"""Une o LIFECYCLE-LEDGER de duas lanes sem escolher um lado (missao 5).

    py ferramentas/unificacao/unir_ledger.py <base> <nossa> <deles> <etiqueta> [--escrever] [--relatorio F]

O livro e append-only: o estado de uma fonte e a ULTIMA transicao. As duas
lanes partem do mesmo prefixo (o livro na merge-base) e acrescentam caudas
diferentes — muitas vezes a MESMA reconciliacao aplicada duas vezes, a partir
de copias diferentes do livro do bot. Colar as duas caudas duplicava
transicoes e partia a cadeia (PREVIOUS_STATE que ja nao e o estado anterior).

Regra (nunca escolher lado, nunca inventar transicao):
  1. fica a cauda NOSSA inteira (a base da unificacao e a ponte);
  2. cada transicao da cauda DELES, pela ordem dela, e confrontada com o
     estado corrente da fonte no livro unido:
       DUPLICADA  — a nossa cauda ja tem a mesma (fonte, de, para, prova);
       ABSORVIDA  — a fonte ja esta no estado de destino;
       APLICADA   — PREVIOUS_STATE == estado corrente e a lei do lifecycle
                    permite: acrescenta-se, com UNIFICACAO={origem} ao lado;
       CONFLITO   — o resto: nao se escreve; fica listada para a
                    reconciliar_livros.py resolver pela prova, fonte a fonte.
O relatorio lista as quatro classes por SOURCE_ID.
"""
import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CAMINHO = "curadoria/LIFECYCLE-LEDGER-V1.json"
sys.path.insert(0, str(RAIZ / "curadoria"))
import lifecycle as L  # noqa: E402


def ler(ref: str) -> dict:
    p = subprocess.run(["git", "show", "%s:%s" % (ref, CAMINHO)], cwd=str(RAIZ), capture_output=True)
    if p.returncode != 0:
        raise SystemExit("sem %s em %s" % (CAMINHO, ref))
    return json.loads(p.stdout)


def chave(t: dict) -> tuple:
    return (t["SOURCE_ID"], t.get("PREVIOUS_STATE"), t["NEW_STATE"], t.get("EVIDENCE_REF"))


def unir(base: dict, nossa: dict, deles: dict, etiqueta: str) -> tuple[dict, dict]:
    nb = len(base["TRANSICOES"])
    for nome, d in (("nossa", nossa), ("deles", deles)):
        if d["TRANSICOES"][:nb] != base["TRANSICOES"]:
            raise SystemExit("%s nao comeca pelo livro da base: append-only violado" % nome)
    cauda_nossa = nossa["TRANSICOES"][nb:]
    cauda_deles = deles["TRANSICOES"][nb:]
    nossas = {chave(t) for t in cauda_nossa}
    out = dict(nossa)
    out["TRANSICOES"] = list(nossa["TRANSICOES"])
    estado = {}
    for t in out["TRANSICOES"]:
        estado[t["SOURCE_ID"]] = t["NEW_STATE"]
    classes, por_fonte = Counter(), {}
    for t in cauda_deles:
        sid, cur = t["SOURCE_ID"], estado.get(t["SOURCE_ID"])
        if chave(t) in nossas:
            c = "DUPLICADA"
        elif cur == t["NEW_STATE"]:
            c = "ABSORVIDA"
        elif t.get("PREVIOUS_STATE") == cur and L.transicao_permitida(cur, t["NEW_STATE"], t["OWNER"])[0]:
            c = "APLICADA"
            linha = dict(t)
            linha["UNIFICACAO"] = {"MISSAO": "UNIFICACAO-V1", "ORIGEM": etiqueta}
            out["TRANSICOES"].append(linha)
            estado[sid] = t["NEW_STATE"]
        else:
            c = "CONFLITO"
        classes[c] += 1
        por_fonte.setdefault(c, []).append({"SOURCE_ID": sid, "DE": t.get("PREVIOUS_STATE"),
                                            "PARA": t["NEW_STATE"], "CORRENTE": cur,
                                            "EVIDENCE_REF": t.get("EVIDENCE_REF")})
    rel = {"ORIGEM": etiqueta, "BASE": nb, "CAUDA_NOSSA": len(cauda_nossa),
           "CAUDA_DELES": len(cauda_deles), "CLASSES": dict(classes),
           "TOTAL_UNIDO": len(out["TRANSICOES"]), "POR_CLASSE": por_fonte}
    return out, rel


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("base"), ap.add_argument("nossa"), ap.add_argument("deles"), ap.add_argument("etiqueta")
    ap.add_argument("--escrever", action="store_true")
    ap.add_argument("--relatorio")
    a = ap.parse_args()
    out, rel = unir(ler(a.base), ler(a.nossa), ler(a.deles), a.etiqueta)
    print(json.dumps({k: v for k, v in rel.items() if k != "POR_CLASSE"}, ensure_ascii=False))
    if a.relatorio:
        Path(a.relatorio).write_text(json.dumps(rel, indent=1, ensure_ascii=False), encoding="utf-8")
    if a.escrever:
        (RAIZ / CAMINHO).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                    newline="\n")
