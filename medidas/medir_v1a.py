#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V1A — a V1 medida pelo CODIGO REAL, nos 3 conjuntos (original, controlo, cego).

A K1 mediu a V1 por simulacao (`medir_k1.politicas`). Aqui cada pagina dos
gabaritos percorre o caminho de producao:

    bytes -> executor_texto_de_html._retrato          (o retrato, como na derivacao)
          -> orquestrador.item_documental_para_a_porta (com SOURCE_URL -> url_da_pagina)
          -> admissao._e_materia                        (a pergunta `materia`, com a V1)
             -> ready_split.regua_manda / contrato_de   (a regua dos 4 passos)
             -> retrato_html.veredito                   (a V1)
             -> a politica do NAO SEI (D11), chamada pela porta (a quarentena)

SIM -> ENTRA · NAO -> BARRADA · NAO_SEI -> RETIDA.

O ESTADO DAS FONTES e o da K1 «depois das receitas», numa COPIA (nunca o livro
vivo): o livro do portao pos-B2 + contratos depois do G1 (V1..V4) + as promocoes
do canario K1 (a prova de cada uma e a linha do canario). Uma fonte cujo
contrato o G1 mudou SEM canario K1 que o provasse leva
ROUTE_PROVENANCE.INTEGRADO_EM = hora do G1 — o campo que a regua ja le para
«contrato mudado depois da promocao». O script CONFERE que a copia da o mesmo
conjunto de fontes bem configuradas que a K1 (`medir_k1.bem_configuradas`), e
para se nao der.

As decisoes humanas da quarentena ficam de fora (ficheiro vazio): mede-se a regra.
Sem rede.

    py medidas/medir_v1a.py --snapshot=<K1-SNAPSHOT-...> [--saida=curadoria/V1A-MEDICAO-V1.json]
"""
from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in ("", "curadoria", "medidas", "coleta", "orquestrador", "scripts/detector_capa"):
    sys.path.insert(0, str(RAIZ / p))
import _gavetas  # noqa: E402,F401
import admissao as ADM                 # noqa: E402
import orquestrador as ORQ             # noqa: E402
import executor_texto_de_html as EXH   # noqa: E402
import medir_detector_moldura as MD    # noqa: E402  (as paginas + a validacao cega da D1)
import medir_k1 as K1                  # noqa: E402  (so para CONFERIR o estado e comparar)

DESTINO = {ADM.SIM: "ENTRA", ADM.NAO: "BARRADA", ADM.NAO_SEI: "RETIDA"}
FATIAS = {"ORIGINAL": lambda g, s: g == "ORIGINAL",
          "CONTROLO_DESENVOLVIMENTO": lambda g, s: g == "CONTROLO_LD2" and s == "DESENVOLVIMENTO",
          "CONTROLO_CEGA": lambda g, s: s == "CEGA"}


def _j(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def montar_copia(snap: Path, destino: Path) -> set:
    """Escreve em `destino` os tres livros que a regua le. Devolve o conjunto K1 «depois»."""
    pos, ens = snap / "POS-B2", snap / "ENSAIO-V4"
    antes, depois, cd = K1.bem_configuradas(pos, ens / "livro.json", ens / "CANARIO.json")
    liv = _j(pos / "LIFECYCLE-LEDGER-V1.json")
    ev = _j(pos / "LIFECYCLE-EVIDENCE-V1.json")
    ca = {c["SOURCE_ID"]: c for c in _j(pos / "italy_contracts_curator.json")["FONTES"]}
    g1_at = {}
    for l in (ens / "ledger.jsonl").read_text(encoding="utf-8").splitlines():
        if l.strip():
            x = json.loads(l)
            g1_at[x["SOURCE_ID"]] = x["AT"].replace("Z", "+00:00")
    livro = _j(ens / "livro.json")
    for c in livro["FONTES"]:
        s = c["SOURCE_ID"]
        if (ca.get(s) or {}).get("ACQUISITION") != c.get("ACQUISITION") and s in g1_at:
            c.setdefault("ROUTE_PROVENANCE", {})["INTEGRADO_EM"] = g1_at[s]
    RS = K1.RS
    for l in _j(ens / "CANARIO.json")["LINHAS"]:
        s, r = l["SOURCE_ID"], l.get("CANARIO")
        # a mesma regra da K1: so conta o canario que provou o contrato NOVO pelos 4 passos
        if not r or RS.passos_da_promocao({"OBSERVED_AT": l["AT"], "EVIDENCE_REF": "K1"}, {"DADOS": r},
                                          cd.get(s))["REGUA"] != RS.REGUA_CURRENT:
            continue
        ref = "V1A-COPIA-K1-%s" % s
        ev["PROVAS"].append({"EVIDENCE_REF": ref, "DADOS": r})
        liv["TRANSICOES"].append({"SOURCE_ID": s, "PREVIOUS_STATE": "CANARY_PENDING",
                                  "NEW_STATE": "READY_FOR_COLLECTION", "EVIDENCE_REF": ref,
                                  "OBSERVED_AT": l["AT"], "OWNER": "V1A-COPIA"})
    (destino / "LIFECYCLE-LEDGER-V1.json").write_text(json.dumps(liv), encoding="utf-8")
    (destino / "LIFECYCLE-EVIDENCE-V1.json").write_text(json.dumps(ev), encoding="utf-8")
    (destino / "italy_contracts_curator.json").write_text(json.dumps(livro), encoding="utf-8")
    return depois


def apontar(destino: Path):
    """A regua (ready_split + lifecycle) e a quarentena humana passam a ler a copia."""
    RS = ADM._da_curadoria("ready_split")
    RS.LC.LIVRO = destino / "LIFECYCLE-LEDGER-V1.json"
    RS.EVIDENCIA = destino / "LIFECYCLE-EVIDENCE-V1.json"
    RS.CONTRATOS = destino / "italy_contracts_curator.json"
    ADM.QUARENTENA_HUMANA = destino / "SEM-DECISOES-HUMANAS.jsonl"
    return RS


def pela_porta(b: bytes, url: str, sid: str, n: int) -> tuple[str, dict]:
    est = {"SOURCE_ID": sid, "TEXTO": "pagina do gabarito", "DERIVED_ARTIFACT_ID": n,
           "RAW_ASSET_ID": n, "PARENT_SHA256": "0" * 64, "CAPTURED_AT": "2026-09-23T00:00:00Z",
           "RETRATO_DO_DETECTOR": EXH._retrato(b), "SOURCE_URL": url}
    item = ORQ.item_documental_para_a_porta(est, source_id=sid)
    res, _, ev = ADM._e_materia(item)
    return DESTINO[res], ev


def medir(pags, urls) -> tuple[dict, list]:
    out, linhas = {f: Counter() for f in FATIAS}, []
    for n, (g, s, i, v, b) in enumerate(pags, 1):
        url, sid = urls[(g, i)]
        d, ev = pela_porta(b, url, sid, n)
        linhas.append({"GABARITO": g, "CONJUNTO": s, "ID": i, "VEREDITO_HUMANO": v, "DESTINO": d,
                       "V1_DISPAROU": bool(ev.get("v1")), "REGUA_A_MANDAR": ev.get("regua_a_mandar")})
        for f, sel in FATIAS.items():
            if sel(g, s):
                out[f][(v, d)] += 1
    res = {f: {"CAPAS_QUE_ENTRAM": c[("CAPA", "ENTRA")], "CAPAS_RETIDAS": c[("CAPA", "RETIDA")],
               "CAPAS_BARRADAS": c[("CAPA", "BARRADA")],
               "NOTICIAS_QUE_ENTRAM": c[("MATERIA", "ENTRA")], "NOTICIAS_RETIDAS": c[("MATERIA", "RETIDA")],
               "NOTICIAS_BARRADAS": c[("MATERIA", "BARRADA")],
               "N_CAPAS": sum(x for k, x in c.items() if k[0] == "CAPA"),
               "N_NOTICIAS": sum(x for k, x in c.items() if k[0] == "MATERIA")}
           for f, c in out.items()}
    return res, linhas


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    snap = Path(arg["snapshot"])
    urls = {(nome, p["ID"]): (p["URL"], p["SOURCE_ID"]) for nome, P, _ in MD.gabaritos() for p in P}
    pags = MD.paginas()
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        depois_k1 = montar_copia(snap, d)
        RS = apontar(d)
        fontes = {sid for _, sid in urls.values()}
        bem = {s for s in fontes if RS.regua_manda(s)}
        if bem != (depois_k1 & fontes):
            raise SystemExit("A COPIA NAO REPRODUZ O ESTADO K1: a mais %s, a menos %s"
                             % (sorted(bem - depois_k1), sorted((depois_k1 & fontes) - bem)))
        real, linhas = medir(pags, urls)
        rh = ADM._da_curadoria("retrato_html")
        rh.V1_LIGADA = False
        desligada, _ = medir(pags, urls)
        rh.V1_LIGADA = True
    k1 = _j(RAIZ / "curadoria" / "K1-MEDICAO-V1.json")["DEPOIS_RECEITAS"]
    res = {"DATASET": "V1A-MEDICAO-V1",
           "METODO": "codigo real: executor._retrato -> item_documental_para_a_porta -> admissao._e_materia",
           "ESTADO_DAS_FONTES": "copia K1 depois das receitas (%s)" % snap.name,
           "FONTES_4_PASSOS_NOS_GABARITOS": len(bem), "FONTES_4_PASSOS": sorted(bem),
           "V1_LIGADA": real, "V1_DESLIGADA": desligada,
           "K1_SIMULACAO": {"ACTUAL": k1["ACTUAL"], "V1": k1["V1"]},
           "PAGINAS_ONDE_A_V1_DISPAROU": [l for l in linhas if l["V1_DISPAROU"]]}
    for f in FATIAS:
        a, s, v = desligada[f], k1["V1"][f], real[f]
        print("%-25s DESLIGADA capas=%d barr=%d ret=%d | LIGADA capas=%d barr=%d ret=%d | K1-V1 capas=%d barr=%d ret=%d"
              % (f, a["CAPAS_QUE_ENTRAM"], a["NOTICIAS_BARRADAS"], a["NOTICIAS_RETIDAS"],
                 v["CAPAS_QUE_ENTRAM"], v["NOTICIAS_BARRADAS"], v["NOTICIAS_RETIDAS"],
                 s["CAPAS_QUE_ENTRAM"], s["NOTICIAS_BARRADAS"], s["NOTICIAS_RETIDAS"]))
    if "saida" in arg:
        Path(arg["saida"]).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
