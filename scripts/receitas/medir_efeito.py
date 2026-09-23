"""O efeito da PROPOSTA-RECEITAS-V1 — medido em memoria, sem a aplicar.

    py scripts/receitas/medir_efeito.py --contratos=<copia do livro vivo> --coorte=<coorte.json>

ANTES = contratos da copia do livro vivo. DEPOIS = os mesmos, com as propostas
por cima (so em memoria; nada e escrito nos contratos).
  1. gabarito: materias casadas pelo LINK_PATTERN da sua fonte, antes/depois;
     capas casadas por engano, antes/depois (tem de ser ~0);
  2. os juizes do detector (scripts/detector_capa/medir_gabarito.py) com as
     receitas antes e depois — ACTUAL nao muda (nao le receita), V1 e a
     proposta «morada antes do formato» mudam;
  3. as 14 da micro: quantas tem receita provada (casa materia confirmada e
     nenhuma capa), antes/depois — e quantas o plano daria PRONTAS.
"""
import copy
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts" / "detector_capa"))
sys.path.insert(0, str(RAIZ / "scripts" / "receitas"))
import medir_gabarito as MG      # noqa: E402
import censo_e_proposta as CP    # noqa: E402


def aplicar_em_memoria(contratos: dict, proposta: dict) -> dict:
    depois = copy.deepcopy(contratos)
    for l in proposta["FONTES"]:
        for p in l["PROPOSTAS"]:
            aq = depois[l["SOURCE_ID"]].setdefault("ACQUISITION", {})
            aq[p["CAMPO"].split(".", 1)[1]] = p["DEPOIS"]
    return depois


def casa(aq: dict | None, url: str) -> bool:
    lp = (aq or {}).get("LINK_PATTERN")
    return bool(lp and re.match(lp, url))


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    antes = {f["SOURCE_ID"]: f for f in json.loads(Path(arg["contratos"]).read_text(encoding="utf-8"))["FONTES"]}
    coorte = json.loads(Path(arg["coorte"]).read_text(encoding="utf-8"))
    proposta = json.loads(CP.SAIDA.read_text(encoding="utf-8"))
    depois = aplicar_em_memoria(antes, proposta)
    g = json.loads(MG.GABARITO.read_text(encoding="utf-8"))
    pags = [p for p in g["PAGINAS"] if p["VEREDITO"] in ("CAPA", "MATERIA")]
    out = {}
    for nome, cont in (("ANTES", antes), ("DEPOIS", depois)):
        aq = {s: c.get("ACQUISITION") for s, c in cont.items()}
        mats = [p for p in pags if p["VEREDITO"] == "MATERIA"]
        capas = [p for p in pags if p["VEREDITO"] == "CAPA"]
        juizes = MG.medir(pags, Path.home() / "detector-capa-gabarito", aq)
        out[nome] = {
            "MATERIAS_CASADAS": f"{sum(casa(aq.get(p['SOURCE_ID']), p['URL']) for p in mats)}/{len(mats)}",
            "CAPAS_CASADAS_POR_ENGANO": f"{sum(casa(aq.get(p['SOURCE_ID']), p['URL']) for p in capas)}/{len(capas)}",
            "CAPAS_CASADAS_LISTA": [p["ID"] for p in capas if casa(aq.get(p["SOURCE_ID"]), p["URL"])],
            "DETECTOR": {j: {k: v for k, v in r.items() if k not in ("ERROS", "MATRIZ")}
                         for j, r in juizes.items() if j in ("ACTUAL", "V1_SO_INDICE", "PROPOSTA")}}

    # as 14 da micro: receita provada = casa >= 1 materia confirmada e 0 capas conhecidas
    todas = CP.paginas()
    micro = {}
    for sid in coorte["MICRO"]:
        m = [p["URL"] for p in todas if p["SOURCE_ID"] == sid and p["VEREDITO"] == "MATERIA"]
        c = [p["URL"] for p in todas if p["SOURCE_ID"] == sid and p["VEREDITO"] == "CAPA"]
        linha = {}
        for nome, cont in (("ANTES", antes), ("DEPOIS", depois)):
            a = (cont.get(sid) or {}).get("ACQUISITION")
            linha[nome] = bool(m) and all(casa(a, u) for u in m) and not any(casa(a, u) for u in c)
        micro[sid] = linha
    out["MICRO_RECEITA_PROVADA"] = {
        "ANTES": f"{sum(v['ANTES'] for v in micro.values())}/{len(micro)}",
        "DEPOIS": f"{sum(v['DEPOIS'] for v in micro.values())}/{len(micro)}",
        "POR_FONTE": micro}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
