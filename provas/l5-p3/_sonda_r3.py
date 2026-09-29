# -*- coding: utf-8 -*-
"""Sonda rapida da RODADA 3 (descartavel): olha o que sai, causa por causa."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import leis_proposta.tempo_tipado as M   # noqa: E402

CASOS = [
    ("R3-1 participio IT", "Le infezioni, riscontrate il 18 maggio 2026 nei frutteti, hanno colpito le cultivar tardive.", None),
    ("R3-1 sem ancora IT", "La cooperativa ha aperto il nuovo impianto di lavorazione il 12 marzo 2026 a Cesena.", None),
    ("R3-1 fundacao IT", "L'azienda, fondata nel 1998 a Verona, conta oggi duecento soci produttori.", None),
    ("R3-1 durante", "Durante il periodo dal 1 al 15 giugno 2026 sono stati posizionati i primi impianti.", None),
    ("R3-1 EN participio", "Symptoms were first recorded on 12 June 2026 in commercial orchards.", None),
    ("R3-1 EN June 12", "The outbreak was confirmed on June 12, 2026 by the regional service.", None),
    ("R3-1 EN founded", "The research centre was established in 1998 and joined the network in 2005.", None),
    ("R3-2 anos", "Il monitoraggio si e svolto dal 2019 al 2021 su tutta la regione.", None),
    ("R3-2 semanas", "Le catture sono cresciute dalla settimana 35 alla settimana 39/2026 negli oliveti.", None),
    ("R3-3 impressa", "Comunicato del 17 settembre 2026. Ieri sono state osservate infezioni nei frutteti.", None),
    ("R3-6 prazo", "Le domande di adesione devono essere presentate entro il 30 settembre 2026.", None),
    ("R3-7 nome doc", "Il Rapporto 2024 dell'osservatorio descrive la struttura del comparto ortofrutticolo.", None),
]

for nome, txt, pub in CASOS:
    r = M.tempos_do_texto(txt, pub, published_at_basis="meta" if pub else None)
    e = r["FACT_TIME_ESCOLHIDO"]
    print("%-20s FACT=%-26s" % (nome, (e["VALOR"] + " " + e["PRECISAO"]) if e else "NAO SEI"),
          "V", [x["VALOR"] for x in r["VALIDITY_TIME"]],
          "P", [x["VALOR"] for x in r["PUBLICATION_TIME"]],
          "A", [x["VALOR"] for x in r["ACT_TIME"]],
          "M", [x["VALOR"] for x in r["MARKET_PERIOD"]])
    if e and e.get("CONDICIONAL"):
        print("%22s condicional: %s" % ("", e["CONDICIONAL"][:88]))
    if not e and r["DESCARTADOS"]:
        print("%22s desc: %s" % ("", [(d["VALOR"], d["PORQUE"][:44]) for d in r["DESCARTADOS"][:3]]))
