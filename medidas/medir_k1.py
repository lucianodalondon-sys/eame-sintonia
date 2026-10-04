#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""K1 — as tres politicas da porta nos 2 gabaritos (+ validacao cega), antes e depois das receitas.

    ACTUAL   detector de hoje + quarentena do NAO SEI (Q1/D11)
    C        + a CAPA de fonte BEM configurada vai para QUARENTENA (D14 opcao C)
    V1       a V1 da LD3 (morada == INDEX_URL -> capa; resto = detector) SO nas fontes
             BEM configuradas (a regua a mandar); nas outras, o detector de hoje

Destino de cada pagina na porta: ENTRA (materia) · RETIDA (quarentena) · BARRADA (capa).

BEM configurada = a fonte passa os 4 passos (ready_split.regua_de == DETAIL/v1):
    ANTES   no livro do portao pos-B2 (copia)
    DEPOIS  pos-B2 + receitas (G1 V1..V4) + canario K1: uma fonte cujo contrato o G1 mudou
            so conta se o canario K1 provou o contrato NOVO pelos 4 passos.
Sem rede.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "medidas"))
sys.path.insert(0, str(RAIZ / "scripts" / "detector_capa"))
import ready_split as RS            # noqa: E402
import retrato_html as RH           # noqa: E402
import medir_gabarito as MG         # noqa: E402
import medir_detector_moldura as MD  # noqa: E402  (paginas + validacao cega da D1)


def _j(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def bem_configuradas(pos_b2: Path, livro_depois: Path, canario: Path) -> tuple[set, set, dict]:
    liv = _j(pos_b2 / "LIFECYCLE-LEDGER-V1.json")
    ev = {p["EVIDENCE_REF"]: p for p in _j(pos_b2 / "LIFECYCLE-EVIDENCE-V1.json")["PROVAS"]}
    ca = {c["SOURCE_ID"]: c for c in _j(pos_b2 / "italy_contracts_curator.json")["FONTES"]}
    cd = {c["SOURCE_ID"]: c for c in _j(livro_depois)["FONTES"]}
    est = {t["SOURCE_ID"] for t in liv["TRANSICOES"]}
    antes = {s for s in est if RS.regua_de(s, livro=liv, evidencias=ev, contratos=ca) == RS.REGUA_CURRENT}
    mudou = {s for s in cd if (ca.get(s) or {}).get("ACQUISITION") != cd[s].get("ACQUISITION")}
    k1 = set()
    for l in _j(canario)["LINHAS"]:
        r = l.get("CANARIO")
        if r and RS.passos_da_promocao({"OBSERVED_AT": l["AT"], "EVIDENCE_REF": "K1"}, {"DADOS": r},
                                       cd.get(l["SOURCE_ID"]))["REGUA"] == RS.REGUA_CURRENT:
            k1.add(l["SOURCE_ID"])
    depois = (antes - mudou) | k1
    return antes, depois, cd


def destino(v: str) -> str:
    return {MG.CAPA: "BARRADA", MG.NS: "RETIDA", MG.MAT: "ENTRA"}[v]


def politicas(bem: set, contratos: dict):
    def actual(ret, url, sid):
        return destino(ret["CAPA_OU_MATERIA"])

    def c(ret, url, sid):
        d = actual(ret, url, sid)
        return "RETIDA" if d == "BARRADA" and sid in bem else d

    def v1(ret, url, sid):
        if sid in bem:
            return destino(MG.v1_so_indice(ret, url, (contratos.get(sid) or {}).get("ACQUISITION")))
        return actual(ret, url, sid)
    return {"ACTUAL": actual, "C": c, "V1": v1}


def medir(bem: set, contratos: dict) -> dict:
    urls = {}
    for nome, P, _ in MD.gabaritos():
        for p in P:
            urls[(nome, p["ID"])] = (p["URL"], p["SOURCE_ID"])
    pags = MD.paginas()
    ret = {(g, i): RH.retrato_do_html(b) for g, _, i, _, b in pags}
    fatias = {"ORIGINAL": lambda g, s: g == "ORIGINAL",
              "CONTROLO_DESENVOLVIMENTO": lambda g, s: g == "CONTROLO_LD2" and s == "DESENVOLVIMENTO",
              "CONTROLO_CEGA": lambda g, s: s == "CEGA"}
    out = {}
    for nome_p, pol in politicas(bem, contratos).items():
        out[nome_p] = {}
        for nome_f, f in fatias.items():
            c = Counter()
            for g, s, i, v, _ in pags:
                if not f(g, s):
                    continue
                url, sid = urls[(g, i)]
                d = pol(ret[(g, i)], url, sid)
                c[(v, d)] += 1
                c[(v, d, "BEM" if sid in bem else "MAL")] += 1
            out[nome_p][nome_f] = {
                "CAPAS_QUE_ENTRAM": c[("CAPA", "ENTRA")], "CAPAS_RETIDAS": c[("CAPA", "RETIDA")],
                "CAPAS_BARRADAS": c[("CAPA", "BARRADA")],
                "NOTICIAS_QUE_ENTRAM": c[("MATERIA", "ENTRA")], "NOTICIAS_RETIDAS": c[("MATERIA", "RETIDA")],
                "NOTICIAS_BARRADAS": c[("MATERIA", "BARRADA")],
                "D14_BARRADAS_FONTE_BEM/MAL": "%d/%d" % (c[("MATERIA", "BARRADA", "BEM")] + c[("CAPA", "BARRADA", "BEM")],
                                                      c[("MATERIA", "BARRADA", "MAL")] + c[("CAPA", "BARRADA", "MAL")]),
                "D14_RETIDAS_FONTE_BEM/MAL": "%d/%d" % (c[("MATERIA", "RETIDA", "BEM")] + c[("CAPA", "RETIDA", "BEM")],
                                                     c[("MATERIA", "RETIDA", "MAL")] + c[("CAPA", "RETIDA", "MAL")]),
                "N_CAPAS": sum(n for k, n in c.items() if len(k) == 2 and k[0] == "CAPA"),
                "N_NOTICIAS": sum(n for k, n in c.items() if len(k) == 2 and k[0] == "MATERIA")}
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    antes, depois, cd = bem_configuradas(Path(arg["pos_b2"]), Path(arg["livro_depois"]), Path(arg["canario"]))
    gab = {s for _, P, _ in MD.gabaritos() for s in (p["SOURCE_ID"] for p in P)}
    res = {"DATASET": "K1-MEDICAO-V1",
           "FONTES_4_PASSOS_NOS_GABARITOS": {"ANTES_RECEITAS": len(antes & gab), "DEPOIS_RECEITAS": len(depois & gab),
                                             "ENTRARAM": sorted((depois - antes) & gab),
                                             "SAIRAM_POR_CONTRATO_MUDADO_SEM_CANARIO": sorted((antes - depois) & gab)},
           "ANTES_RECEITAS": medir(antes, cd), "DEPOIS_RECEITAS": medir(depois, cd)}
    print(json.dumps(res["FONTES_4_PASSOS_NOS_GABARITOS"], ensure_ascii=False))
    for k in ("ANTES_RECEITAS", "DEPOIS_RECEITAS"):
        for p, v in res[k].items():
            for f, x in v.items():
                print(k[:6], p, f, {a: x[a] for a in ("CAPAS_QUE_ENTRAM", "CAPAS_RETIDAS", "NOTICIAS_BARRADAS",
                                                     "NOTICIAS_RETIDAS", "N_CAPAS", "N_NOTICIAS")})
    if "saida" in arg:
        Path(arg["saida"]).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
