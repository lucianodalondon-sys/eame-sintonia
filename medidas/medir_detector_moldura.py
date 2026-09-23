#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D1 — o detector chama CAPA a noticias verdadeiras: medir a correcao ANTES de a aplicar.

Compara, nos dois gabaritos (original + controlo LD2), o detector ACTUAL com a
proposta «os links da moldura do site (nav/header/footer) nao contam na razao
caracteres-por-ligacao». Separa o controlo em DESENVOLVIMENTO e VALIDACAO CEGA
(medidas/D1-VALIDACAO-CEGA-V1.json, sorteada e commitada antes da analise).

    FALSE_ARTICLE_AS_LISTING  materia (humano) julgada CAPA_PROVAVEL — tem de descer
    FALSE_LISTING_AS_ARTICLE  capa (humano) julgada MATERIA_PROVAVEL — nao pode subir nem +1

Le os bytes guardados (sha256 conferido contra o manifesto). Sem rede.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import retrato_html as RH   # noqa: E402

HOME = Path.home()
CEGA = json.loads((RAIZ / "medidas" / "D1-VALIDACAO-CEGA-V1.json").read_text(encoding="utf-8"))


def gabaritos():
    orig = json.loads((RAIZ / "scripts" / "detector_capa" / "GABARITO-CAPA-V1.json").read_text(encoding="utf-8"))
    r = subprocess.run(["git", "show", "origin/listing-detail-v3:scripts/detector_capa/GABARITO-CONTROLO-LD2.json"],
                       cwd=RAIZ, capture_output=True)
    cont = json.loads(r.stdout.decode("utf-8"))
    return [("ORIGINAL", orig["PAGINAS"], HOME / "detector-capa-gabarito"),
            ("CONTROLO_LD2", cont["PAGINAS"], HOME / "ld2-controlo")]


def paginas():
    """[(gabarito, conjunto, id, veredito humano, bytes)] — so CAPA/MATERIA, sha conferido."""
    out = []
    cegas = set(CEGA["IDS"])
    for nome, P, pasta in gabaritos():
        man = {p["FICHEIRO"]: p["SHA256"] for p in
               json.loads((pasta / "MANIFESTO.json").read_text(encoding="utf-8"))["PAGINAS"]}
        for p in P:
            if p.get("VEREDITO") not in ("CAPA", "MATERIA"):
                continue
            b = (pasta / p["FICHEIRO"]).read_bytes()
            if man.get(p["FICHEIRO"]) and hashlib.sha256(b).hexdigest() != man[p["FICHEIRO"]]:
                raise SystemExit("sha256 nao confere: %s" % p["FICHEIRO"])
            conj = ("CEGA" if nome == "CONTROLO_LD2" and p["ID"] in cegas else "DESENVOLVIMENTO")
            out.append((nome, conj, p["ID"], p["VEREDITO"], b))
    return out


def contar(pags, retratar) -> dict:
    c = Counter()
    for _, _, _, v, b in pags:
        c[(v, retratar(b)["CAPA_OU_MATERIA"])] += 1
    return {"FALSE_ARTICLE_AS_LISTING": c[("MATERIA", "CAPA_PROVAVEL")],
            "FALSE_LISTING_AS_ARTICLE": c[("CAPA", "MATERIA_PROVAVEL")],
            "MATERIA_OK": c[("MATERIA", "MATERIA_PROVAVEL")],
            "MATERIA_NAO_SEI": c[("MATERIA", "NAO_SEI")],
            "CAPA_OK": c[("CAPA", "CAPA_PROVAVEL")],
            "CAPA_NAO_SEI": c[("CAPA", "NAO_SEI")],
            "N_MATERIAS": sum(n for (v, _), n in c.items() if v == "MATERIA"),
            "N_CAPAS": sum(n for (v, _), n in c.items() if v == "CAPA")}


def medir(proposta) -> dict:
    """{fatia: {ANTES, DEPOIS}}; `proposta` e uma funcao bytes -> retrato."""
    pags = paginas()
    fatias = {
        "ORIGINAL": [p for p in pags if p[0] == "ORIGINAL"],
        "CONTROLO_DESENVOLVIMENTO": [p for p in pags if p[0] == "CONTROLO_LD2" and p[1] == "DESENVOLVIMENTO"],
        "CONTROLO_CEGA": [p for p in pags if p[1] == "CEGA"],
        "CONTROLO_TODO": [p for p in pags if p[0] == "CONTROLO_LD2"],
    }
    return {k: {"ANTES": contar(v, RH.retrato_do_html), "DEPOIS": contar(v, proposta)}
            for k, v in fatias.items()}


# ── AS DUAS PROPOSTAS MEDIDAS (vivem AQUI, nao no detector: NAO foram aplicadas) ──
# Medido nas 10 noticias chamadas CAPA: em 8 a maioria dos links vive na moldura
# do sitio (<nav>/<header>/<footer>). As duas variantes so mexem na fronteira
# CAPA <-> NAO_SEI; a regra de MATERIA fica intacta, por isso nenhuma capa pode
# passar a MATERIA por elas.
_MOLDURA = re.compile(r"<(nav|header|footer)\b[^>]*>.*?</\1\s*>", re.I | re.S)


def _v(b: bytes, tambem_o_texto: bool) -> dict:
    r = RH.retrato_do_html(b)
    fonte = RH._INVISIVEL.sub(" ", RH._decodificar(b))
    fora = _MOLDURA.sub(" ", fonte)
    lig = len(RH._LIGACAO.findall(fora))
    sb = r["NON_WHITESPACE_CHARACTERS"]
    if tambem_o_texto:
        linhas = [RH._BRANCOS.sub(" ", l).strip() for l in RH._desentidar(RH._TAG.sub("\n", fora)).split("\n")]
        sb = len(RH._BRANCOS.sub("", "\n".join(l for l in linhas if l)))
    if r["HTML_KIND"] in ("CONTENT", "EMPTY"):
        k = r["HTML_KIND"]
    elif lig and sb / max(lig, 1) < RH.CARACTERES_POR_LIGACAO:
        k = "NAVIGATION"
    else:
        k = "MIXED"
    return dict(r, HTML_KIND=k, CAPA_OU_MATERIA=("MATERIA_PROVAVEL" if k == "CONTENT" else
                                                 "CAPA_PROVAVEL" if k == "NAVIGATION" else "NAO_SEI"))


PROPOSTAS = {
    "V2_LINKS_DA_MOLDURA_FORA": lambda b: _v(b, False),
    "V3_LINKS_E_TEXTO_DA_MOLDURA_FORA": lambda b: _v(b, True),
}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    res = {}
    for nome, f in PROPOSTAS.items():
        res[nome] = medir(f)
        print("==", nome)
        for k, v in res[nome].items():
            print(" ", k, {x: (v["ANTES"][x], v["DEPOIS"][x]) for x in v["ANTES"]})
    out = res
    if argv:
        Path(argv[0]).write_text(json.dumps({"DATASET": "D1-MEDICAO-DETECTOR-MOLDURA-V1",
                                             "VALIDACAO_CEGA": "medidas/D1-VALIDACAO-CEGA-V1.json",
                                             "APLICADA": False,
                                             "PROPOSTAS": out}, ensure_ascii=False, indent=1) + "\n",
                                 encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
