#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEDE-FONTES · a PROPOSTA de SOURCE_LOCATION_RULE por fonte — so relatorio, nao escreve contratos.

    py ferramentas/sede_fontes/propor_regra.py <SEDE-DAS-FONTES-V1.json> <nomes.json> <saida.json>

Para cada fonte com sede provada (medir_sede.py) ou provada no MESMO SITE (mesmo host de outra fonte
com prova), escreve o texto da regra no formato que o contrato ja le
(«<nome do gazetteer> (<morada e prova>) — fixo», como os 15 contratos escritos a mao) e CONFERE-O com
o mesmo leitor do contrato: `contratos_de_fonte._candidatos_do_texto` + o gazetteer de leis/fato_local.py.
Assim a proposta diz o que o contrato devolveria (VALOR e PRECISAO) antes de alguem a escrever.
"""
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ / "regras"), str(RAIZ)]
import contratos_de_fonte as C  # noqa: E402
from leis import fato_local as FL  # noqa: E402

GAZ = {n: p for n, p in FL.GAZETTEER}
# comune da morada -> nome do gazetteer (provincia) quando o comune nao esta no gazetteer
PROVINCIA_DA_SIGLA = {"MO": "Modena", "RE": "Reggio nell'Emilia", "RM": "Roma", "MI": "Milano", "FI": "Firenze",
                      "BO": "Bologna", "GE": "Genova", "RA": "Ravenna"}
# leitura a mao (ver RELATORIO §2): o que a regra automatica nao decide sozinha
LEITURA = {
    "IT-T10-021": "DUAS SEDES no rodape: «Sede legale via Giovanni Nicotera 29 00195 Roma · Sede operativa via Gallo "
                  "Marcucci 23-24 48018 (Faenza, RA)». Proposta com a SEDE LEGAL; qual conta e decisao do dono.",
    "IT-T7-141": "CANDIDATA de leitura: rodape «CIA AGRICOLTORI ITALIANI TOSCANA Via di Novoli 91/N – 50127 Firenze», "
                 "mas numa so pagina guardada; a regra automatica pede >= 2 paginas ou a palavra «sede».",
    "IT-T7-033": "A morada achada e o LOCAL DE UM EVENTO (The Westin Palace Milan): a regra recusou-a, e bem.",
}


def host(u):
    h = urlparse(u if "://" in (u or "") else "https://" + (u or "")).hostname or ""
    return h.lower().removeprefix("www.")


def confere(regra):
    for nome in C._candidatos_do_texto(regra):
        if nome in GAZ:
            return nome, GAZ[nome]
    return "NAO SEI", "NOT_IN_GAZETTEER"


def main():
    sede = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["FONTES"]
    nomes = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    out, provadas = [], {}
    for f in sede:
        f["HOST"] = host(f.get("INDEX_URL") or nomes.get(f["SOURCE_ID"], {}).get("URL") or "")
        if f.get("SEDE_PROVAVEL", "NAO SEI") != "NAO SEI":
            provadas.setdefault(f["HOST"], f)
    for f in sede:
        sid = f["SOURCE_ID"]
        linha = {"SOURCE_ID": sid, "NOME": nomes.get(sid, {}).get("NOME"), "HOST": f["HOST"],
                 "PAGINAS_GUARDADAS_LIDAS": f.get("PAGINAS_GUARDADAS_LIDAS", 0)}
        prova, via = (f, "PAGINA_GUARDADA_DA_PROPRIA_FONTE") if f.get("SEDE_PROVAVEL", "NAO SEI") != "NAO SEI" else (
            # sem parentesis: o leitor do contrato corta o aparte no primeiro «)» (medido: dava NOT_IN_GAZETTEER)
            (provadas.get(f["HOST"]), "MESMO_SITE de %s" % provadas[f["HOST"]]["SOURCE_ID"]) if f["HOST"] in provadas
            else (None, None))
        if prova:
            comune = prova["SEDE_PROVAVEL"].split(" (")[0].strip().title()
            sigla = prova["SEDE_PROVAVEL"].split("(")[1].rstrip(")") if "(" in prova["SEDE_PROVAVEL"] else ""
            nome_gaz = comune if comune in GAZ else PROVINCIA_DA_SIGLA.get(sigla, comune)
            aparte = "sede: %s%s, CAP %s" % (comune, " %s" % sigla if sigla else "", prova.get("CAP"))
            regra = "%s (%s; prova: %s) — fixo" % (nome_gaz, aparte, via)
            valor, precisao = confere(regra)
            linha.update(SEDE_PROVAVEL=prova["SEDE_PROVAVEL"], VIA=via, BASE=prova["BASE"],
                         TRECHO=prova.get("TRECHO"), SOURCE_LOCATION_RULE_PROPOSTA=regra,
                         O_CONTRATO_DEVOLVERIA={"VALOR": valor, "PRECISAO": precisao})
        else:
            linha.update(SEDE_PROVAVEL="NAO SEI", VIA=None, BASE=f.get("BASE"),
                         TRECHO=f.get("TRECHO"), SOURCE_LOCATION_RULE_PROPOSTA=None,
                         O_CONTRATO_DEVOLVERIA={"VALOR": "NAO SEI", "PRECISAO": "NAO SEI"})
        if sid in LEITURA:
            linha["LEITURA_A_MAO"] = LEITURA[sid]
        out.append(linha)
        print(sid, "|", linha["SEDE_PROVAVEL"], "|", linha["VIA"], "|", linha["O_CONTRATO_DEVOLVERIA"])
    Path(sys.argv[3]).write_text(json.dumps({"DATASET": "PROPOSTA-SOURCE-LOCATION-RULE-V1", "ESCRITO_EM_CONTRATOS": 0,
                                             "FONTES": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
