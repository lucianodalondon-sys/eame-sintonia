# -*- coding: utf-8 -*-
"""PESQ-FORA-DO-MUR · quem, da T6, e da FEM, do CREA ou do CNR — e em que instituto. Sem rede.

    py ferramentas/seguir_pesquisadores/fora_do_mur.py --t6=UNIDADES-T6.json --saida=FORA-DO-MUR.json

A instituicao le-se no que a OBRA declara (OpenAlex: `INSTITUICOES_NESTA_OBRA`), nunca no nome da
pessoa. Um nome de instituicao que nao e inequivoco fica marcado PROVAVEL (ex.: «Cereal Research
Centre» e, pelo nome, o antigo centro de cereais do CREA — mas o OpenAlex nao o diz). O CNR e dito
por INSTITUTO (IPSP, IBBR, ISPA...), porque as listas de pessoal sao por instituto.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# (instituicao, unidade, certeza, padrao no nome da instituicao do OpenAlex)
CASAS = [
    ("FEM", "FEM", "CERTA", r"fondazione edmund mach"),
    ("CNR", "IPSP", "CERTA", r"institute for sustainable plant protection|protezione sostenibile delle piante"),
    ("CNR", "IBBR", "CERTA", r"institute of biosciences and bioresources|bioscienze e biorisorse"),
    ("CNR", "ISPA", "CERTA", r"institute of sciences of food production|scienze delle produzioni alimentari"),
    ("CNR", "ISAFOM", "CERTA", r"agricultural and forest(ry)? systems in the mediterranean|isafom"),
    ("CNR", "IBE", "CERTA", r"institute of bioeconomy|bioeconomia"),
    ("CNR", "IRET", "CERTA", r"research on terrestrial ecosystems|ecosistemi terrestri"),
    ("CNR", "IMAMOTER", "CERTA", r"agricultural and earthmoving machines"),
    ("CNR", "ISA", "CERTA", r"^institute of food science$"),
    ("CNR", "CNR (sem instituto)", "CERTA", r"^national research council$|consiglio nazionale delle ricerche"),
    ("CREA", "CREA (sem centro)", "CERTA", r"consiglio per la ricerca in agricoltura|council for agricultural research"),
    ("CREA", "CREA-CI", "CERTA", r"research centre for cereal and industrial crops"),
    ("CREA", "CREA-OF", "CERTA", r"centro di ricerca per l.orticoltura|vegetable and ornamental crops"),
    ("CREA", "CREA-VE", "CERTA", r"viticulture and (o)?enology|viticoltura"),
    ("CREA", "CREA-OFA", "CERTA", r"olive, fruit and citrus|olivicoltura, frutticoltura"),
    ("CREA", "CREA-DC", "CERTA", r"plant protection and certification|difesa e certificazione"),
    ("CREA", "CREA-AA", "CERTA", r"agriculture and environment|agricoltura e ambiente"),
    ("CREA", "CREA-FL", "PROVAVEL", r"^forestry research centre$"),
    ("CREA", "CREA-CI (nome antigo)", "PROVAVEL", r"^cereal research centre$"),
    ("CREA", "CREA-OFA (nome antigo)", "PROVAVEL", r"istituto sperimentale per la frutticoltura"),
    ("LAIMBURG", "Laimburg", "CERTA", r"laimburg"),
]
PEDIDAS = ["grassi", "tonina", "ioriatti", "anfora"]      # FEM, pela missao


def casa_de(nome_inst: str):
    for inst, unid, certeza, rx in CASAS:
        if re.search(rx, nome_inst or "", re.I):
            return inst, unid, certeza
    return None


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    t6 = json.loads(Path(arg["t6"]).read_text(encoding="utf-8"))
    P = defaultdict(lambda: {"NOMES": set(), "ORCID": set(), "CASAS": set(), "OBRAS": 0, "RECENTES": 0,
                             "PAR_TEXTO_RECENTE": 0, "PARES": Counter()})
    for u in t6["UNIDADES"]:
        rec = (u.get("PUBLICADO_EM") or "") >= "2024"
        par = u.get("NA_CONSULTA_E_NO_TEXTO") or []
        for a in u["AUTORES"]:
            casas = {casa_de(i.get("NOME") if isinstance(i, dict) else i)          # ha obras com o nome em texto
                     for i in a.get("INSTITUICOES_NESTA_OBRA") or []} - {None}
            if not casas:
                continue
            p = P[a["OPENALEX_ID"]]
            p["NOMES"].add(a["NOME"])
            p["CASAS"] |= casas
            if a.get("ORCID_NO_INDICE") not in (None, "", "NAO SEI"):
                p["ORCID"].add(a["ORCID_NO_INDICE"])
            p["OBRAS"] += 1
            p["RECENTES"] += rec
            if par and rec:
                p["PAR_TEXTO_RECENTE"] += 1
            for x in par:
                p["PARES"][x] += 1
    pessoas = []
    for oid, p in P.items():
        nomes = sorted(p["NOMES"], key=len, reverse=True)
        pessoas.append({"OPENALEX_ID": oid, "NOME": nomes[0], "OUTROS_NOMES": nomes[1:],
                        "CASAS": sorted({"%s/%s" % (c[0], c[1]) for c in p["CASAS"]}),
                        "CERTEZA_DA_CASA": "CERTA" if any(c[2] == "CERTA" for c in p["CASAS"]) else "PROVAVEL",
                        "ORCID": sorted(p["ORCID"]), "OBRAS_T6": p["OBRAS"], "RECENTES": p["RECENTES"],
                        "PAR_DO_CASCO_RECENTE": p["PAR_TEXTO_RECENTE"], "PARES": dict(p["PARES"].most_common(4)),
                        # sobrenome INTEIRO: «Canfora» nao e «Anfora» (medido na 1.a corrida)
                        "PEDIDA_PELO_NOME": any(s in {w for n in p["NOMES"] for w in re.split(r"[\s.\-]+", n.lower())}
                                                for s in PEDIDAS)})
    # consulta2: as pessoas pedidas pelo nome cujas obras vieram da consulta2 (nao dos 589)
    if arg.get("consulta2"):
        c2 = json.loads(Path(arg["consulta2"]).read_text(encoding="utf-8")).get("PESSOAS") or {}
        ja = {x["OPENALEX_ID"] for x in pessoas}
        for nome, c in c2.items():
            if nome.split()[-1].lower() not in PEDIDAS or c.get("ESTADO") != "RESOLVIDO":
                continue
            cand = (c.get("CANDIDATOS") or [{}])[0]
            if cand.get("OPENALEX_ID") in ja:
                continue
            casas = sorted({"%s/%s" % x[:2] for i in cand.get("INSTITUICOES") or [] for x in [casa_de(i)] if x})
            pessoas.append({"OPENALEX_ID": cand.get("OPENALEX_ID"), "NOME": nome, "OUTROS_NOMES": [cand.get("NOME")],
                            "CASAS": casas, "CERTEZA_DA_CASA": "CERTA" if casas else "NAO SEI",
                            "ORCID": [cand["ORCID"]] if cand.get("ORCID") not in (None, "NAO SEI") else [],
                            "OBRAS_T6": 0, "OBRAS_CONSULTA2": c.get("OBRAS"), "RECENTES": None,
                            "PAR_DO_CASCO_RECENTE": 0, "ORGANISMOS_NO_TITULO": c.get("ORGANISMOS_EXTRA_NO_TITULO"),
                            "PARES": {}, "PEDIDA_PELO_NOME": True, "ORIGEM": "CONSULTA2 (obras fora dos 589)"})
    pessoas.sort(key=lambda x: (x["PEDIDA_PELO_NOME"], x["PAR_DO_CASCO_RECENTE"], x["OBRAS_T6"]), reverse=True)
    por_unid = Counter(c for x in pessoas for c in x["CASAS"])
    por_unid_casco = Counter(c for x in pessoas if x["PAR_DO_CASCO_RECENTE"] for c in x["CASAS"])
    resumo = {"PESSOAS": len(pessoas), "POR_UNIDADE": dict(por_unid.most_common()),
              "POR_UNIDADE_COM_CASCO_RECENTE": dict(por_unid_casco.most_common()),
              "COM_ORCID": sum(1 for x in pessoas if x["ORCID"]),
              "PEDIDAS_ACHADAS": [x["NOME"] for x in pessoas if x["PEDIDA_PELO_NOME"]]}
    Path(arg["saida"]).write_text(json.dumps({"DATASET": "PESQ-FORA-DO-MUR", "RESUMO": resumo, "PESSOAS": pessoas},
                                             ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
