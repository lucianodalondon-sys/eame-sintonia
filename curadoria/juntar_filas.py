#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JUNTA-FONTES: uma so fila de candidatas, sem numeros repetidos.

Varias equipes nasceram da mesma fila da producao (906) e registaram CAND-0907..
em paralelo. Aqui cada candidata nova de cada ramo volta a entrar, pela porta
canonica (candidatas/fonte_nova.py), sobre a fila da producao — pela ordem
P1d -> P1g -> P5b -> P4b -> SOC, uma vez por URL normalizado. A nota da linha
nova junta as provas de todas as equipes que viram a mesma fonte; as outras
equipes ficam em VISTA_TAMBEM_POR. Nada e escrito na fila a mao.

Sem rede. So git show + a porta.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, OrderedDict
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "candidatas"))
from fonte_nova import registar, recusar, normalizar, carregar  # noqa: E402

SAIDA = RAIZ / "curadoria" / "FILA-UNICA-CORRESPONDENCIA-V1.json"
PRODUCAO = "origin/regua-t2-v1"
RAMOS = [("P1d", "origin/pesquisadores-v2"), ("P1g", "origin/janelas-regioes-v1"),
         ("P5b", "origin/pessoas-docentes-v1"), ("P4b", "origin/pessoas-agro-v4"),
         ("SOC", "origin/social-onda2-v1")]
FILA = "candidatas/FONTES-CANDIDATAS.json"
JANELA_P1D = {"BOLLETTINI_DIFESA", "BOLLETTINI_AGROMETEO", "CONSORZI_DIFESA"}
# Revisao P1g (24/09): o exemplo destas notas nao era boletim.
EXEMPLO_FALSO = {("P1g", "CAND-0919"): "comunicado de projeto (AgriVolt), nao boletim",
                 ("P1g", "CAND-0938"): "norma tecnica de difesa 2025, nao boletim periodico"}


def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=str(RAIZ), capture_output=True, check=True,
                          text=True, encoding="utf-8").stdout


def _fila(ref: str) -> list:
    return json.loads(_git("show", "%s:%s" % (ref, FILA)))["CANDIDATAS"]


def novas_do_ramo(ref: str) -> list:
    """Linhas do ramo que nao estao na fila de onde ele nasceu (por ID e URL)."""
    base = _git("merge-base", PRODUCAO, ref).strip()
    b = {c["CANDIDATA_ID"]: normalizar(c["URL"]) for c in _fila(base)}
    return [c for c in _fila(ref) if b.get(c["CANDIDATA_ID"]) != normalizar(c["URL"])]


def familias() -> dict:
    fam: dict = {}
    try:
        l = json.loads(_git("show", "origin/pesquisadores-v2:curadoria/PESQUISADORES-LISTA-V1.json"))
        for x in l["CANDIDATAS"]:
            fam[normalizar(x["URL"])] = x["FAMILIA"]
    except Exception:
        pass
    try:
        j = json.loads(_git("show", "origin/janelas-regioes-v1:curadoria/JANELAS-REGIOES-V1.json"))
        for x in j["CELULAS"]:
            fam.setdefault(normalizar(x["URL"]), "JANELA_" + x["COLUNA"])
    except Exception:
        pass
    return fam


def _nota_corrigida(equipe: str, c: dict) -> str:
    nota = c.get("NOTA", "")
    falso = EXEMPLO_FALSO.get((equipe, c["CANDIDATA_ID"]))
    if falso:
        nota = re.sub(r"EXEMPLO=[^|]*", "EXEMPLO=NENHUM (o exemplo do registo original foi descartado "
                      "na revisao P1g: %s) " % falso, nota)
    return nota


def juntar(aplicar: bool = True) -> dict:
    prod = {normalizar(c["URL"]): c["CANDIDATA_ID"] for c in carregar()["CANDIDATAS"]}
    n_prod = len(prod)
    grupos: "OrderedDict[str, list]" = OrderedDict()
    por_ramo: dict = {}
    for equipe, ref in RAMOS:
        novas = novas_do_ramo(ref)
        por_ramo[equipe] = {"REF": ref, "SHA": _git("rev-parse", "--short", ref).strip(), "NOVAS_NO_RAMO": len(novas)}
        for c in novas:
            grupos.setdefault(normalizar(c["URL"]), []).append((equipe, c))
    fam = familias()
    corr, resultado = [], Counter()
    for k, ocorr in grupos.items():
        vivas = [(e, c) for e, c in ocorr if c["ESTADO"] != "RECUSADA"]
        dono_e, dono = (vivas or ocorr)[0]
        if k in prod:
            novo, res = prod[k], "JA_NA_PRODUCAO"
        else:
            notas = []
            for e, c in ocorr:
                n = _nota_corrigida(e, c)
                txt = "[%s %s] %s" % (e, c["CANDIDATA_ID"], n)
                if n and n not in [x.split("] ", 1)[-1] for x in notas]:
                    notas.append(txt)
            nota = " || ".join(notas) + " | FILA_UNICA=juntar_filas.py %s" % datetime.now(timezone.utc).date()
            res = "NOVA"
            if aplicar:
                l = registar(tipo=dono["TIPO"], pais=dono["PAIS"], nome=dono["NOME"], url=dono["URL"],
                             para_que=dono["PARA_QUE_SERVE"], quem_viu=dono["QUEM_VIU"],
                             onde_viu=dono["ONDE_VIU"], nota=nota)
                novo = l["CANDIDATA_ID"]
                if not vivas:
                    recusar(dono["URL"], "FILA_UNICA: recusada no ramo %s %s — %s"
                            % (dono_e, dono["CANDIDATA_ID"], dono.get("MOTIVO_DA_RECUSA") or "sem motivo"))
                    res = "NOVA_RECUSADA"
            else:
                novo = "SERIA_NOVA"
            prod[k] = novo
        if aplicar:
            for e, c in ocorr:
                if (e, c["CANDIDATA_ID"]) != (dono_e, dono["CANDIDATA_ID"]) and c.get("QUEM_VIU"):
                    registar(tipo=c["TIPO"], pais=c["PAIS"], nome=c["NOME"], url=c["URL"],
                             para_que=c["PARA_QUE_SERVE"], quem_viu="%s (%s %s)" % (c["QUEM_VIU"], e, c["CANDIDATA_ID"]),
                             onde_viu=c["ONDE_VIU"])
        equipes = sorted({e for e, _ in ocorr})
        for e, c in ocorr:
            corr.append({"RAMO": e, "CAND_ANTIGO": c["CANDIDATA_ID"], "URL": c["URL"], "CAND_NOVO": novo,
                         "RESULTADO": res if (e, c["CANDIDATA_ID"]) == (dono_e, dono["CANDIDATA_ID"])
                         else ("JUNTADA_A %s" % novo), "EQUIPES_COM_ESTA_FONTE": equipes,
                         "FAMILIA": fam.get(k) or ("PESSOAS" if e in ("P5b", "P4b") else c["TIPO"])})
        resultado[res] += 1
    fila = carregar()["CANDIDATAS"]
    ids = [c["CANDIDATA_ID"] for c in fila]
    urls = [normalizar(c["URL"]) for c in fila]
    novas = [x for x in corr if x["RESULTADO"].startswith("NOVA")]
    fam_novas = Counter(x["FAMILIA"] for x in novas)
    janela = [x for x in novas if x["FAMILIA"].startswith("JANELA_") or x["FAMILIA"] in JANELA_P1D]
    for e in por_ramo:
        por_ramo[e]["RESULTADOS"] = dict(Counter(x["RESULTADO"].split()[0] for x in corr if x["RAMO"] == e))
    out = {"DATASET": "FILA-UNICA-CORRESPONDENCIA-V1", "GERADO_EM": datetime.now(timezone.utc).isoformat(),
           "PRODUCAO": "%s %s" % (PRODUCAO, _git("rev-parse", "--short", PRODUCAO).strip()),
           "FILA_ANTES": n_prod, "FILA_DEPOIS": len(fila), "RAMOS": por_ramo,
           "FONTES_DISTINTAS": len(grupos), "RESULTADOS": dict(resultado),
           "CANDIDATAS_NOVAS": len(novas), "POR_FAMILIA": dict(sorted(fam_novas.items())),
           "JANELA_D29": {"ESTRITO": len(janela),
                          "COM_SERVIZI_TECNICI": len(janela) + fam_novas.get("SERVIZI_TECNICI", 0)},
           "DUPLICADOS_MEDIDOS": {"CAND_ID_REPETIDO": len(ids) - len(set(ids)),
                                  "URL_REPETIDO_NA_FILA_TODA": len(urls) - len(set(urls)),
                                  "URL_REPETIDO_ENTRE_AS_NOVAS": len(novas) - len({normalizar(x["URL"]) for x in novas})},
           "CORRESPONDENCIA": corr}
    fd, tmp = tempfile.mkstemp(dir=str(SAIDA.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, SAIDA)
    return out


if __name__ == "__main__":
    aplicar = "--aplicar" in sys.argv
    r = juntar(aplicar=aplicar)
    print("APLICADO" if aplicar else "ENSAIO (nada escrito na fila)")
    for k in ("FILA_ANTES", "FILA_DEPOIS", "FONTES_DISTINTAS", "RESULTADOS", "CANDIDATAS_NOVAS",
              "POR_FAMILIA", "JANELA_D29", "DUPLICADOS_MEDIDOS"):
        print(k, r[k])
    for e, v in r["RAMOS"].items():
        print(" ", e, v)
