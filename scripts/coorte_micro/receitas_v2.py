"""PROPOSTA-RECEITAS-V2 — receitas novas para fontes RELEVANTES do funil G0.

    py scripts/coorte_micro/receitas_v2.py --snap=<copia do servico vivo>

Mesmo metodo da 6-PREP-d (scripts/receitas/censo_e_proposta.por_fonte): materia
lida primeiro, familia >= 2 na entrada, guarda contra padrao generico. So para
fontes com SINTONIA_RELEVANT = YES que param em C. NAO APLICA: escreve so
curadoria/PROPOSTA-RECEITAS-V2.json.
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "scripts" / "receitas"))
import censo_e_proposta as CP   # noqa: E402
import funil as FU              # noqa: E402

SAIDA = RAIZ / "curadoria" / "PROPOSTA-RECEITAS-V2.json"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    snap = Path(next(a.split("=", 1)[1] for a in argv if a.startswith("--snap=")))
    D = FU.carregar(snap)
    alvo = [l for l in (FU.avaliar(s, D) for s in D["universo"])
            if l["SINTONIA_RELEVANT"] == "YES" and not l["C"] and l["MATERIAS_LIDAS"]]
    fontes = []
    for l in alvo:
        sid = l["SOURCE_ID"]
        c = D["onboarded"].get(sid) or D["curador"].get(sid)
        host = CP.urlparse(((c or {}).get("ACQUISITION") or {}).get("INDEX_URL", "")).netloc.lower().removeprefix("www.")
        pags = [p for p in D["paginas"] if p["SOURCE_ID"] == sid]
        capas = [p["URL"] for p in D["paginas"] if p["VEREDITO"] == "CAPA" and host and host in p["URL"]]
        r = CP.por_fonte(sid, c, pags, capas)
        r["PORQUE_NESTA_LISTA"] = "SINTONIA_RELEVANT=YES e a receita nao casa a materia lida (G0)"
        fontes.append(r)
    d = {"DATASET": "PROPOSTA-RECEITAS-V2", "MISSAO": "G0",
         "ESTADO": "PROPOSTA — NAO APLICADA. Mesma aplicacao da V1: depois da unificacao (M5).",
         "METODO": "scripts/receitas/censo_e_proposta.por_fonte (6-PREP-d), sem alteracao",
         "FONTES": fontes}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in fontes:
        print(r["SOURCE_ID"], [p["DEPOIS"] for p in r["PROPOSTAS"]] or r.get("SEM_PROPOSTA"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
