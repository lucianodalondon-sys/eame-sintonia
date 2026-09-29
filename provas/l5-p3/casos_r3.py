# -*- coding: utf-8 -*-
"""L5-P3 · RODADA 3 · casos MEUS, novos, um grupo por causa (1 a 8). Pela interface.

    py -3.12 provas/l5-p3/casos_r3.py

Escritos a partir das causas GENERICAS do coordenador. Nenhum vem da prova, que nao foi
aberta. A causa 1 (a principal) tem casos em italiano E em ingles, com tempos verbais e
construcoes diferentes, como a rodada 3 pediu.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

from interface import extrair_proposto   # noqa: E402

BASE = "JSON-LD datePublished"
_res = []


def caso(causa, nome, texto, alvo_trecho, espera, pub=None, campo="FACT_TIME",
         contrato=None, precisao=None, extra=None):
    entrada = {"TEXTO": texto, "PUBLISHED_AT_DA_SALA": pub,
               "PUBLISHED_AT_BASIS_DA_SALA": BASE if pub else None,
               "CAPTURED_AT": "2026-09-29T06:00:00Z"}
    if contrato:
        entrada["CONTRATO_DA_FONTE"] = contrato
    p = texto.find(alvo_trecho)
    assert p >= 0, "o trecho do alvo nao esta no texto: %s" % nome
    r = extrair_proposto(entrada, {"TRECHO": alvo_trecho, "OFFSET": p, "FIM": p + len(alvo_trecho)})
    saiu = r[campo]["VALOR"]
    ok = saiu == espera
    if ok and precisao:
        ok = r[campo]["PRECISAO"] == precisao
    if ok and extra:
        ok = extra(r)
    _res.append(ok)
    print("%-5s C%s %-32s %s=%-26s %s" % ("OK" if ok else "FALHA", causa, nome, campo, saiu,
                                          "" if ok else "(esperado %s%s)" % (
                                              espera, " " + precisao if precisao else "")))
    if not ok:
        print("        porque: %s" % str(r[campo].get("PORQUE"))[:130])
    return r


# ── CAUSA 1 · a data na propria oracao da afirmacao E o tempo do acontecimento ──
# italiano: participio, passato prossimo, presente, gerundio, passivo
caso(1, "participio IT", "Le infezioni, riscontrate il 18 maggio 2026 nei frutteti, hanno colpito le tardive.",
     "Le infezioni, riscontrate il 18 maggio 2026 nei frutteti", "2026-05-18", precisao="DIA")
caso(1, "passato prossimo IT", "La cooperativa ha aperto il nuovo impianto il 12 marzo 2026 a Cesena.",
     "La cooperativa ha aperto il nuovo impianto il 12 marzo 2026", "2026-03-12", precisao="DIA")
caso(1, "sem verbo de campo IT", "Il presidente ha firmato l'accordo con i soci il 3 febbraio 2026 a Verona.",
     "Il presidente ha firmato l'accordo con i soci il 3 febbraio 2026", "2026-02-03")
caso(1, "fundacao IT (alvo)", "L'azienda, fondata nel 1998 a Verona, conta duecento soci produttori.",
     "L'azienda, fondata nel 1998 a Verona", "1998", precisao="ANO")
caso(1, "entrada em instituicao", "Il ricercatore e entrato nell'Universita di Bologna nel 2010 come borsista.",
     "Il ricercatore e entrato nell'Universita di Bologna nel 2010", "2010", precisao="ANO")
caso(1, "durante o periodo", "Durante il periodo dal 1 al 15 giugno 2026 sono stati posizionati i primi impianti.",
     "Durante il periodo dal 1 al 15 giugno 2026", "2026-06-01/2026-06-15", precisao="INTERVALO")
# ingles
caso(1, "EN participio", "Symptoms were first recorded on 12 June 2026 in commercial orchards.",
     "Symptoms were first recorded on 12 June 2026", "2026-06-12", precisao="DIA")
caso(1, "EN June 12, 2026", "The outbreak was confirmed on June 12, 2026 by the regional service.",
     "The outbreak was confirmed on June 12, 2026", "2026-06-12", precisao="DIA")
caso(1, "EN founded (alvo)", "The research centre was established in 1998 in Wageningen.",
     "The research centre was established in 1998", "1998", precisao="ANO")
caso(1, "EN during period", "Trapping was carried out from 1 to 15 June 2026 across the region.",
     "Trapping was carried out from 1 to 15 June 2026", "2026-06-01/2026-06-15", precisao="INTERVALO")

# ── CAUSA 2 · intervalos INTEIROS: dias, semanas, meses, anos ─────────────────
caso(2, "intervalo de dias", "I rilievi sono stati eseguiti dal 3 al 7 agosto 2026 negli oliveti.",
     "I rilievi sono stati eseguiti dal 3 al 7 agosto 2026", "2026-08-03/2026-08-07",
     precisao="INTERVALO", extra=lambda r: r["FACT_TIME"].get("INICIO") == "2026-08-03"
     and r["FACT_TIME"].get("FIM") == "2026-08-07")
caso(2, "intervalo de meses", "Le anomalie termiche si sono concentrate tra maggio-giugno 2026 nelle Marche.",
     "Le anomalie termiche si sono concentrate tra maggio-giugno 2026", "2026-05/2026-06",
     precisao="INTERVALO")
caso(2, "intervalo de anos", "Il monitoraggio si e svolto dal 2019 al 2021 su tutta la regione.",
     "Il monitoraggio si e svolto dal 2019 al 2021", "2019/2021", precisao="INTERVALO")
caso(2, "intervalo de semanas", "Le catture sono cresciute dalla settimana 35 alla settimana 39/2026 negli oliveti.",
     "Le catture sono cresciute dalla settimana 35 alla settimana 39/2026",
     "2026-W35/2026-W39", precisao="INTERVALO")

# ── CAUSA 3 · D63 pela data IMPRESSA, com o metadado da Sala vazio ────────────
caso(3, "ieri pela data impressa",
     "Comunicato del 17 settembre 2026. Ieri sono state osservate infezioni nei frutteti.",
     "Ieri sono state osservate infezioni nei frutteti", "2026-09-16",
     extra=lambda r: r["FACT_TIME"]["ORIGEM"] == "RELATIVO_D63"
     and "IMPRESSA" in str(r["FACT_TIME"].get("PROCEDENCIA_DO_ANO", "")))
caso(3, "questa settimana pelo boletim",
     "BOLLETTINO settimana 39 dal 22/09/2026 al 29/09/2026\nQuesta settimana sono stati osservati attacchi.",
     "Questa settimana sono stati osservati attacchi", "2026-09-22/2026-09-29",
     extra=lambda r: bool(r["FACT_TIME"].get("COMPOSICAO")))

# ── CAUSA 4 · D153 · ano da linha de data do mesmo documento ──────────────────
caso(4, "ano da linha de data",
     "Bollettino fitosanitario n. 17/2026 del 04.05.2026\nVITICOLTURA\n"
     "Nei monitoraggi eseguiti giovedi 30 aprile sono state rilevate infezioni nei vigneti.",
     "Nei monitoraggi eseguiti giovedi 30 aprile", "2026-04-30", precisao="DIA",
     extra=lambda r: r["FACT_TIME"]["ORIGEM"] == "CABECALHO"
     and bool(r["FACT_TIME"].get("ANO_BASIS")) and bool(r["FACT_TIME"].get("PROCEDENCIA_DO_ANO")))
caso(4, "ano concorrente -> NAO SEI",
     "Bollettino n. 5 del 2026 · archivio storico 2025\nVITICOLTURA\n"
     "Nei monitoraggi eseguiti giovedi 30 aprile sono state rilevate infezioni nei vigneti.",
     "Nei monitoraggi eseguiti giovedi 30 aprile", "SEM_ANO-04-30")
caso(4, "sem dia/mes: publicacao nao vira facto",
     "Bollettino fitosanitario n. 17/2026 del 04.05.2026\nVITICOLTURA\n"
     "La difesa integrata richiede attenzione costante negli impianti giovani della zona.",
     "La difesa integrata richiede attenzione costante negli impianti giovani da zona"
     if False else "La difesa integrata richiede attenzione costante", "NAO_EXISTE")

# ── CAUSA 5 · periodo de validade sem ano: ano da linha de emissao ────────────
caso(5, "validade sem ano no periodo",
     "Bollettino di difesa n. 14 del 23 luglio 2026\nPREVISIONE\n"
     "Le indicazioni sono valide dal 24 al 31 luglio per tutti i vigneti della provincia.",
     "valide dal 24 al 31 luglio", "2026-07-24/2026-07-31", campo="VALIDITY_TIME")

# ── CAUSA 6 · ACT_TIME so para ATO; prazo e VALIDADE ─────────────────────────
caso(6, "ato de verdade",
     "Con Decreto Dirigenziale n. 15068 del 08/09/2026 e stata approvata la ridefinizione delle aree.",
     "Con Decreto Dirigenziale n. 15068 del 08/09/2026 e stata approvata la ridefinizione",
     "2026-09-08", campo="ACT_TIME")
caso(6, "prazo nao e ato",
     "Le domande di adesione devono essere presentate entro il 30 settembre 2026 agli uffici.",
     "Le domande di adesione devono essere presentate entro il 30 settembre 2026",
     "2026-09-30", campo="VALIDITY_TIME")
caso(6, "prazo: ACT fica sem nada",
     "Le domande di adesione devono essere presentate entro il 30 settembre 2026 agli uffici.",
     "Le domande di adesione devono essere presentate entro il 30 settembre 2026",
     "NAO_EXISTE", campo="ACT_TIME")
caso(6, "acontecimento nunca vai para ACT",
     "Le infezioni sono state riscontrate il 18 maggio 2026 nei frutteti della provincia.",
     "Le infezioni sono state riscontrate il 18 maggio 2026", "NAO_EXISTE", campo="ACT_TIME")

# ── CAUSA 7 · PUBLICATION_TIME nunca de um ano que e NOME de documento ───────
caso(7, "Rapporto 2024 nao e publicacao",
     "Il Rapporto 2024 dell'osservatorio descrive la struttura del comparto ortofrutticolo.",
     "Il Rapporto 2024 dell'osservatorio descrive la struttura", "NAO_EXISTE",
     campo="PUBLICATION_TIME")
caso(7, "Rapporto 2024 nao e facto",
     "Il Rapporto 2024 dell'osservatorio descrive la struttura del comparto ortofrutticolo.",
     "Il Rapporto 2024 dell'osservatorio descrive la struttura", "NAO_EXISTE")

# ── CAUSA 8 · conhecimento / biologia / definicao -> NAO_EXISTE ──────────────
caso(8, "biologia -> NAO_EXISTE",
     "La Bactrocera oleae e un dittero le cui larve si nutrono della polpa delle olive.",
     "La Bactrocera oleae e un dittero le cui larve si nutrono della polpa", "NAO_EXISTE")
caso(8, "definicao EN -> NAO_EXISTE",
     "Fire blight is a bacterial disease of pome fruits caused by Erwinia amylovora.",
     "Fire blight is a bacterial disease of pome fruits", "NAO_EXISTE")
caso(8, "aconteceu sem data -> NAO_SEI",
     "Nei frutteti della zona sono state riscontrate infezioni diffuse sulle cultivar tardive.",
     "Nei frutteti della zona sono state riscontrate infezioni diffuse", "NAO_SEI")

print("\nCASOS_R3 %d/%d" % (sum(1 for x in _res if x), len(_res)))
raise SystemExit(0 if all(_res) else 1)
