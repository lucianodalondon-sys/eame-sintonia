#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O DOMINIO REGISTAVEL e o ORCAMENTO de um host — a regra D38/D41, com UM so dono no runtime.

Nasceu em `provas/prova_teto_dominio.py` (a prova independente do teto D38) e foi usada dali pelo runtime
(`coleta/rota_navegador.py`, `coleta/espera_por_dominio.py`, `coleta/reserva_24h.py`) — o runtime importava
`provas/`, o que a lei da casa proibe (`tests/test_a_porta_cli_liga_o_banco.py::test_1`). DA-21 (coordenacao
27/09, INTEGRA-NOITE lote 4): a regra MUDA-SE para aqui, tal e qual, e a prova passa a importa-la daqui. A prova
continua independente do que verifica — o CONTADOR (le o livro de corridas, nao o disjuntor); a regra do
dominio e uma so, para o transporte, as rodadas e a prova nao contarem dominios diferentes.
"""
import re

TETO_D38 = 5

# Sufixos públicos de DOIS níveis que esta prova conhece (escritos aqui, sem Public Suffix List:
# nenhuma nesta casa, e nenhuma se vai buscar à rede). Um sufixo que falte junta MAIS do que devia
# (ex.: `x.provincia.it` com `provincia.it`): a prova fica mais exigente, nunca mais branda.
SUFIXOS_DOIS_NIVEIS = frozenset("""
gov.it edu.it
abruzzo.it abr.it basilicata.it bas.it calabria.it cal.it campania.it cam.it
emilia-romagna.it emiliaromagna.it emr.it friuli-venezia-giulia.it friuli-vgiulia.it friulivenezia-giulia.it
friulivgiulia.it fvg.it lazio.it laz.it liguria.it lig.it lombardia.it lom.it marche.it mar.it molise.it mol.it
piemonte.it pmn.it puglia.it pug.it sardegna.it sar.it sicilia.it sic.it toscana.it tos.it trentino.it
trentino-alto-adige.it trentinoaltoadige.it taa.it umbria.it umb.it valledaosta.it valle-daosta.it vda.it vao.it
veneto.it ven.it
co.uk org.uk ac.uk gov.uk com.br org.br gov.br com.au org.au co.jp com.es com.pt co.nz com.ar com.mx
""".split())


# D41 (25/09): dominios DIFERENTES que sao o MESMO orcamento. O stream do YouTube vem de
# `googlevideo.com`; contar a parte deixaria cada video gastar 5 + 5. Escrito aqui, a mao,
# e so com o que a decisao nomeou: juntar de menos e o unico erro que esta prova nao pode fazer.
MESMO_ORCAMENTO = {"googlevideo.com": "youtube.com"}


def host_limpo(h):
    h = str(h or "").strip().lower()
    h = re.sub(r"^[a-z][a-z0-9+.-]*://", "", h)      # aceita tambem uma origem com esquema
    h = h.split("/")[0].split("@")[-1]
    if h.startswith("[") and "]" in h:                # IPv6 entre parenteses
        return h[: h.index("]") + 1]
    h = h.split(":")[0].rstrip(".")
    return h[4:] if h.startswith("www.") else h


def dominio_registavel(host):
    h = host_limpo(host)
    if not h or re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", h) or h.startswith("["):
        return h
    partes = [p for p in h.split(".") if p]
    if len(partes) <= 2:
        return ".".join(partes)
    dois = ".".join(partes[-2:])
    return ".".join(partes[-3:]) if dois in SUFIXOS_DOIS_NIVEIS else dois


def orcamento_de(host):
    """O dominio que PAGA o pedido: o registavel, ou aquele a que a D41 o junta."""
    d = dominio_registavel(host)
    return MESMO_ORCAMENTO.get(d, d)
