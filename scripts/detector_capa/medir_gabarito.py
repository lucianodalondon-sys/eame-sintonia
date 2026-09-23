"""Mede o detector CAPA != MATERIA no GABARITO-CAPA-V1 — em memoria, sem o alterar.

    py scripts/detector_capa/medir_gabarito.py [--pasta=<gabarito>]

Quatro juizes sobre as MESMAS paginas, cada um com matriz de confusao:
  ACTUAL        curadoria/retrato_html.py tal como esta (so o FORMATO)
  SO_MORADA     so o endereco: casa o LINK_PATTERN e nao e o INDEX_URL -> MATERIA,
                senao CAPA. Serve para SEPARAR o efeito da morada do do formato.
  PROPOSTA      morada antes do formato: morada de capa -> CAPA; morada de
                detalhe -> o formato, mas NAVIGATION vira NAO_SEI (pessoa le).
  PROPOSTA_SEM_PADRAO  a mesma proposta numa fonte SEM LINK_PATTERN declarado
                (controlo pedido): cai no ACTUAL, por definicao — medido, nao dito.

O portao so reprova CAPA_PROVAVEL. Por isso «capa que atravessa» = capa julgada
MATERIA ou NAO_SEI; «materia barrada» = materia julgada CAPA.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "curadoria"))
import retrato_html as RH  # noqa: E402

GABARITO = AQUI / "GABARITO-CAPA-V1.json"
CAPA, MAT, NS = "CAPA_PROVAVEL", "MATERIA_PROVAVEL", "NAO_SEI"


def actual(retrato: dict, url: str, aq: dict | None) -> str:
    return retrato["CAPA_OU_MATERIA"]


def morada_de_capa(url: str, aq: dict) -> bool:
    indice = url.rstrip("/") == str(aq.get("INDEX_URL", "")).rstrip("/")
    return indice or not re.match(aq["LINK_PATTERN"], url)


def so_morada(retrato: dict, url: str, aq: dict | None) -> str:
    if not aq or not aq.get("LINK_PATTERN"):
        return NS
    return CAPA if morada_de_capa(url, aq) else MAT


def proposta(retrato: dict, url: str, aq: dict | None) -> str:
    if not aq or not aq.get("LINK_PATTERN"):
        return actual(retrato, url, aq)            # sem padrao: nada muda
    if morada_de_capa(url, aq):
        return CAPA
    k = retrato["CAPA_OU_MATERIA"]
    return NS if k == CAPA else k


def proposta_sem_padrao(retrato: dict, url: str, aq: dict | None) -> str:
    return proposta(retrato, url, None)


def v1_so_indice(retrato: dict, url: str, aq: dict | None) -> str:
    """Variante 1: a morada so manda quando e EXACTAMENTE o INDEX_URL."""
    if aq and url.rstrip("/") == str(aq.get("INDEX_URL", "")).rstrip("/"):
        return CAPA
    return actual(retrato, url, aq)


def v2_desempate(retrato: dict, url: str, aq: dict | None) -> str:
    """Variante 2: morada e formato em desacordo -> uma pessoa le.
    Morada de capa + formato MATERIA -> NAO_SEI; morada de capa + resto -> CAPA.
    Morada de detalhe + formato CAPA -> NAO_SEI; resto -> o formato.
    Nunca barra sozinha uma pagina que o formato aprova, nem aprova sozinha
    uma que a morada condena."""
    if not aq or not aq.get("LINK_PATTERN"):
        return actual(retrato, url, aq)
    k = retrato["CAPA_OU_MATERIA"]
    if morada_de_capa(url, aq):
        return NS if k == MAT else CAPA
    return NS if k == CAPA else k


JUIZES = {"ACTUAL": actual, "SO_MORADA": so_morada, "PROPOSTA": proposta,
          "PROPOSTA_SEM_PADRAO": proposta_sem_padrao,
          "V1_SO_INDICE": v1_so_indice, "V2_DESEMPATE": v2_desempate}


def medir(paginas: list[dict], pasta: Path, contratos: dict) -> dict:
    out = {}
    for nome, juiz in JUIZES.items():
        m = {"CAPA": Counter(), "MATERIA": Counter()}
        erros = {"CAPA_QUE_ATRAVESSA": [], "MATERIA_BARRADA": []}
        for p in paginas:
            r = RH.retrato_do_html((pasta / p["FICHEIRO"]).read_bytes())
            v = juiz(r, p["URL"], contratos.get(p["SOURCE_ID"]))
            m[p["VEREDITO"]][v] += 1
            if p["VEREDITO"] == "CAPA" and v != CAPA:
                erros["CAPA_QUE_ATRAVESSA"].append(p["ID"])
            if p["VEREDITO"] == "MATERIA" and v == CAPA:
                erros["MATERIA_BARRADA"].append(p["ID"])
        nc, nm = sum(m["CAPA"].values()), sum(m["MATERIA"].values())
        out[nome] = {
            "MATRIZ": {k: dict(v) for k, v in m.items()},
            "CAPA_CHAMADA_MATERIA": f"{m['CAPA'][MAT]}/{nc}",
            "CAPA_QUE_ATRAVESSA_O_PORTAO": f"{len(erros['CAPA_QUE_ATRAVESSA'])}/{nc}",
            "MATERIA_CHAMADA_CAPA": f"{m['MATERIA'][CAPA]}/{nm}",
            "MATERIA_PARA_PESSOA_LER": f"{m['MATERIA'][NS]}/{nm}",
            "CAPA_PARA_PESSOA_LER": f"{m['CAPA'][NS]}/{nc}",
            "CAPA_CALADA_COMO_MATERIA": f"{m['CAPA'][MAT]}/{nc}",
            "ERROS": erros}
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    pasta = Path(next((a.split("=", 1)[1] for a in argv if a.startswith("--pasta=")),
                      Path.home() / "detector-capa-gabarito"))
    g = json.loads(GABARITO.read_text(encoding="utf-8"))
    contratos = {f["SOURCE_ID"]: f.get("ACQUISITION") for f in json.loads(
        (RAIZ / "curadoria" / "italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}
    paginas = [p for p in g["PAGINAS"] if p["VEREDITO"] in ("CAPA", "MATERIA")]
    res = {"TODAS": medir(paginas, pasta, contratos)}
    for grupo in sorted({p["GRUPO"] for p in paginas}):
        res[grupo] = medir([p for p in paginas if p["GRUPO"] == grupo], pasta, contratos)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
