#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A MATERIA-PRIMA QUE CADA FERRAMENTA PRECISA — derivada do contrato, nao inventada.

Este ficheiro NAO cria taxonomia nova e NAO cria uma segunda verdade. Cada
necessidade abaixo esta ancorada numa das tres coisas que o repositorio ja mede:

  1 · o contrato de bloco  `italia-portale/audit/blocks/*.spec.json`
      — em especial `realSource` (o que alimenta de verdade) e `fieldsThatDie`
        (os campos que morrem se o dado escrito a mao sair). `fieldsThatDie` E'
        a lista de buracos, escrita pelo proprio projeto.
  2 · o dado real do casco  `italia-portale/client/*.js`
      — contado campo a campo, com taxa de preenchimento.
  3 · a taxonomia T1..T12, lida de `_territorios.py`, que le o atlas.

AS FERRAMENTAS SAO AS QUE O MAPA MEDIU, NAO AS QUE UM PEDIDO SUPOE
------------------------------------------------------------------
O System Map mede 11 cartoes na zona `Z-TELAS`. Duas ficam fora desta analise
por serem consulta/cadastro (Archivio, Registro delle fonti). Sobram NOVE.

E duas diferencas em relacao ao que se costuma assumir, ambas medidas:

  · NAO EXISTE ferramenta «Label Intelligence». Existe `Portafoglio`, e o
    contrato dela chama-se PORTFOLIO / PRODUCT INTELLIGENCE.
  · `C-TELA-FIELD` nao e «Field Voices»: chama-se «Rete Commerciale di Campo»
    e o dado dela e `fieldMessages`, 18 registos, provenance SYNTHETIC_DEMO.
    As vozes do campo vivem noutra tela, `C-TELA-VOICES`.

TRES DAS NOVE NAO TEM CONTRATO PROPRIO
--------------------------------------
Medido por sha256: `future.spec.json`, `signal.spec.json`, `voci.spec.json` e
`field.spec.json` sao o MESMO ficheiro (10bc784976972a6d) — um documento de
«tecido conectivo» com quatro nomes. `portfolio.spec.json` e `product.spec.json`
tambem sao um so (1c80d9b3d2e33ce2).

    PARA ARCHIVIO SEGNALI, VOCI DAL CAMPO E RETE COMMERCIALE DI CAMPO,
    A NECESSIDADE DE MATERIA-PRIMA NAO PODE SER LIDA DE UM CONTRATO:
    NAO HA CONTRATO. O QUE SE ESCREVE AQUI PARA ELAS E' DERIVADO DO
    DADO QUE ELAS JA CONSOMEM, E ESTA MARCADO `ANCORA = DADO_MEDIDO`.

Isso nao e detalhe: uma ferramenta sem contrato nao tem como reprovar uma fonte
errada, porque nao declarou o que precisa.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
import _territorios as _T  # noqa: E402 — o dono da taxonomia

# ── as nove ferramentas, como o mapa as mediu ─────────────────────────────
FERRAMENTAS = {
    "WINDOWS": {
        "nome_it": "Finestre Colturali", "nome_pt": "Janelas de Cultura",
        "id_mapa": "C-TELA-WINDOWS", "de_onde_vem_hoje": "REAL",
        "contrato": "italia-portale/audit/blocks/windows.spec.json + calendar.spec.json",
        "pergunta": ("Que janela de cultura x problema esta aberta agora, em que "
                     "regiao, e quanto tempo falta para a proxima?"),
    },
    "MARKET": {
        "nome_it": "Polso di Mercato", "nome_pt": "Pulso de Mercado",
        "id_mapa": "C-TELA-MARKET", "de_onde_vem_hoje": "MISTURA",
        "contrato": "italia-portale/audit/blocks/market.spec.json",
        "pergunta": ("Como esta o mercado de cada cultura — preco, producao, "
                     "oferta e custo — e o que mudou?"),
    },
    "PORTFOLIO": {
        "nome_it": "Portafoglio", "nome_pt": "Portfolio",
        "id_mapa": "C-TELA-PORTFOLIO", "de_onde_vem_hoje": "MISTURA",
        "contrato": "italia-portale/audit/blocks/portfolio.spec.json (= product.spec.json)",
        "pergunta": ("Que produto esta registado para que cultura e que alvo, com "
                     "que dose e que restricao, e ate quando?"),
    },
    "SCIENCE": {
        "nome_it": "Intelligence Scientifica", "nome_pt": "Inteligencia Cientifica",
        "id_mapa": "C-TELA-SCIENCE", "de_onde_vem_hoje": "MISTURA",
        "contrato": "italia-portale/audit/blocks/science.spec.json",
        "pergunta": ("Que ciencia existe sobre esta cultura e este problema, quem "
                     "a faz, onde, e o que ela mediu?"),
    },
    "COMPETITORS": {
        "nome_it": "Concorrenza", "nome_pt": "Concorrencia",
        "id_mapa": "C-TELA-COMPETITORS", "de_onde_vem_hoje": "MISTURA",
        "contrato": "italia-portale/audit/blocks/competitor.spec.json",
        "pergunta": ("O que cada concorrente esta a comunicar e a registar, para "
                     "que cultura e que alvo, e quando?"),
    },
    "VOICES": {
        "nome_it": "Voci dal Campo", "nome_pt": "Vozes do Campo",
        "id_mapa": "C-TELA-VOICES", "de_onde_vem_hoje": "NAO SEI",
        "contrato": "SEM CONTRATO PROPRIO (voci.spec.json e copia do tecido conectivo)",
        "pergunta": ("Quem, no campo italiano, esta a dizer que problema, em que "
                     "cultura e em que regiao — e quando o viu?"),
    },
    "FUTURE": {
        "nome_it": "Archivio segnali", "nome_pt": "Arquivo de sinais",
        "id_mapa": "C-TELA-FUTURE", "de_onde_vem_hoje": "NAO SEI",
        "contrato": "SEM CONTRATO PROPRIO (future.spec.json e copia do tecido conectivo)",
        "pergunta": ("Que sinal novo apareceu que ainda nao e um facto de campo "
                     "estabelecido?"),
    },
    "FIELD_NET": {
        "nome_it": "Rete Commerciale di Campo", "nome_pt": "Rede Comercial de Campo",
        "id_mapa": "C-TELA-FIELD", "de_onde_vem_hoje": "NAO SEI",
        "contrato": "SEM CONTRATO PROPRIO (field.spec.json e copia do tecido conectivo)",
        "pergunta": ("O que a rede comercial no campo esta a relatar?"),
    },
    "RADAR": {
        "nome_it": "Radar delle Opportunita", "nome_pt": "Radar das Oportunidades",
        "id_mapa": "C-TELA-MEETING", "de_onde_vem_hoje": "MISTURA",
        "contrato": "italia-portale/audit/blocks/case.spec.json",
        "pergunta": ("Onde cultura, problema, regiao, janela, portfolio e "
                     "concorrente se cruzam?"),
        "nota": ("NAO TEM FAMILIA PROPRIA DE FONTES. E cruzamento das outras "
                 "camadas — por isso nao se procura fonte para ele, mede-se se as "
                 "entradas dele existem."),
    },
}

# ── as necessidades de materia-prima ──────────────────────────────────────
# campos:
#   TOOL · RAW_NEED · REQUIRED_FIELDS · FRESHNESS · GEO · TEMPORAL · TERR
#   ANCORA   de onde vem esta necessidade: CONTRATO | DADO_MEDIDO
#   PROVA    o texto ou a medicao que a sustenta
#   MEDIDO   o que o casco tem HOJE para ela (cheio/total, ou a ausencia)
NECESSIDADES = [
 # ══════════════ WINDOWS · Finestre Colturali ══════════════
 dict(TOOL="WINDOWS", RAW_NEED="Cultura e regiao da janela",
      REQUIRED_FIELDS="CROP_NAME · REGION",
      FRESHNESS="anual", GEO="REGIAO", TEMPORAL="temporada", TERR=["T1"],
      ANCORA="CONTRATO", PROVA="windows.spec: 29 rows over 10 crops x 9 regions",
      MEDIDO="CAN.windows CROP_NAME 29/29 · REGION 29/29"),
 dict(TOOL="WINDOWS", RAW_NEED="Datas de inicio e fim da janela",
      REQUIRED_FIELDS="START_DATE · END_DATE · DATE_CONFIDENCE · DATE_STATE",
      FRESHNESS="anual", GEO="REGIAO", TEMPORAL="dia", TERR=["T1", "T3"],
      ANCORA="CONTRATO", PROVA="windows.spec: 24/29 rows have real dates",
      MEDIDO="CAN.windows START_DATE 24/29 (83%) · END_DATE 24/29"),
 dict(TOOL="WINDOWS", RAW_NEED="FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
      REQUIRED_FIELDS="CROP_STAGE · CROP_STAGE_SOURCE · GENERATION_OR_STAGE · BBCH",
      FRESHNESS="semanal", GEO="REGIAO", TEMPORAL="semana", TERR=["T1", "T3"],
      ANCORA="CONTRATO+DADO_MEDIDO",
      PROVA=("windows.spec fieldsThatDie: 'crop phenology stages "
             "(D.CROP_CAL[crop].stages — Sowing, Tillering, ... Harvest)' "
             "verdict REMOVE_SUBCOMPONENT"),
      MEDIDO="CAN.windows CROP_STAGE 0/29 · CROP_STAGE_SOURCE 0/29 · GENERATION_OR_STAGE 0/29"),
 dict(TOOL="WINDOWS", RAW_NEED="FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
      REQUIRED_FIELDS="ISSUE_STAGE · ISSUE_STAGE_SOURCE",
      FRESHNESS="semanal", GEO="REGIAO", TEMPORAL="semana", TERR=["T3"],
      ANCORA="DADO_MEDIDO",
      PROVA="os campos existem no contrato canonico e estao vazios",
      MEDIDO="CAN.windows ISSUE_STAGE 0/29 · ISSUE_STAGE_SOURCE 0/29"),
 dict(TOOL="WINDOWS", RAW_NEED="OBSERVACAO DE CAMPO (fase observada, nao esperada)",
      REQUIRED_FIELDS="OBSERVED_STAGE · OBSERVATION_DATE · FIELD_REPORTED_STAGE · FACT_DATE",
      FRESHNESS="semanal", GEO="PONTO/PROVINCIA", TEMPORAL="dia", TERR=["T3", "T7"],
      ANCORA="CONTRATO",
      PROVA=("windows.spec: '0/29 have an observed stage'; e 'plus 2 Modena "
             "field-observation rows that are the only OBSERVED_STAGE values in "
             "the whole pack'"),
      MEDIDO="ING.CROP_WINDOWS OBSERVATION_DATE 2/7 · FIELD_REPORTED_STAGE 2/7 (5 = NAO SEI)"),
 dict(TOOL="WINDOWS", RAW_NEED="Janela de monitorizacao (quando ir olhar)",
      REQUIRED_FIELDS="MONITORING_WINDOW",
      FRESHNESS="anual", GEO="REGIAO", TEMPORAL="semana", TERR=["T3"],
      ANCORA="CONTRATO",
      PROVA="windows.spec fieldsThatDie: 'monitoring window' verdict DERIVABLE_FROM_REAL",
      MEDIDO="ING.CROP_WINDOWS MONITORING_WINDOW 7/7 · CAN.windows: nao tem o campo"),
 dict(TOOL="WINDOWS", RAW_NEED="Janela de controlo de infestantes",
      REQUIRED_FIELDS="weed window (inicio/fim)",
      FRESHNESS="anual", GEO="REGIAO", TEMPORAL="semana", TERR=["T3"],
      ANCORA="CONTRATO",
      PROVA="windows.spec fieldsThatDie: 'weed-control windows (D.CROP_CAL[crop].weed)'",
      MEDIDO="nenhum campo de infestante nas 29 janelas canonicas"),
 dict(TOOL="WINDOWS", RAW_NEED="ATO REGULATORIO regional que abre/fecha a janela",
      REQUIRED_FIELDS="REGULATORY_ACT · REGULATORY_WINDOW · REGULATORY_SOURCE · REGULATORY_TIMING",
      FRESHNESS="por ato", GEO="REGIAO", TEMPORAL="dia", TERR=["T4", "T12"],
      ANCORA="CONTRATO",
      PROVA=("windows.spec: '2/29 (Veneto, Piemonte Flavescenza) gain a real "
             "regulatory act'"),
      MEDIDO="CAN.windows REGULATORY_SOURCE 0/29 · ING.CROP_WINDOWS REGULATORY_ACT 5/7"),
 dict(TOOL="WINDOWS", RAW_NEED="Produto registado ligado a janela",
      REQUIRED_FIELDS="PRODUCT_MATCHES · LABEL_SOURCE · LABEL_TRIGGER",
      FRESHNESS="por alteracao de rotulo", GEO="PAIS", TEMPORAL="dia", TERR=["T4"],
      ANCORA="CONTRATO",
      PROVA=("windows.spec: 'all 29 canonical windows measure PRODUCT_MATCHES = []'; "
             "'11/29 have a verified ADAMA product' via ITALY_LABEL_VERDICTS"),
      MEDIDO="CAN.windows PRODUCT_MATCHES 0/29 · LABEL_SOURCE 0/29 · LABEL_TRIGGER 0/29"),
 dict(TOOL="WINDOWS", RAW_NEED="RASTREABILIDADE: que fonte sustenta esta janela",
      REQUIRED_FIELDS="SOURCE_IDS",
      FRESHNESS="—", GEO="—", TEMPORAL="—", TERR=["T1", "T3"],
      ANCORA="CONTRATO",
      PROVA=("windows.spec openQuestion: 'SOURCE_IDS is empty on all 29 windows. "
             "Should a window inherit the source ids of the regional regulatory "
             "act it joins?'"),
      MEDIDO="CAN.windows SOURCE_IDS 0/29"),
 dict(TOOL="WINDOWS", RAW_NEED="Area/hectares da cultura por regiao (escala)",
      REQUIRED_FIELDS="hectares por cultura x regiao",
      FRESHNESS="anual", GEO="REGIAO", TEMPORAL="ano", TERR=["T1"],
      ANCORA="CONTRATO",
      PROVA=("windows.spec fieldsThatDie: 'row hectares (rendered as ~350k ha) and "
             "the HIGH/MEDIUM/LOW crop-scale label derived from it'; e "
             "'IG.CROPS[17] has NO region and NO area fields'"),
      MEDIDO="ING.CROPS 17 registos, sem regiao e sem area"),
 dict(TOOL="WINDOWS", RAW_NEED="Desvio fenologico por regiao (a mesma cultura adianta/atrasa)",
      REQUIRED_FIELDS="offset em dias por regiao",
      FRESHNESS="anual", GEO="REGIAO", TEMPORAL="dia", TERR=["T1", "T2"],
      ANCORA="CONTRATO",
      PROVA=("windows.spec fieldsThatDie: 'per-region phenology offset "
             "(values -14 to +7 days)'"),
      MEDIDO="nao existe campo nenhum de offset no dado real"),

 # ══════════════ MARKET · Polso di Mercato ══════════════
 dict(TOOL="MARKET", RAW_NEED="Preco por cultura e por praca",
      REQUIRED_FIELDS="PRICE_NUM · UNIT · MARKET · REFERENCE_PERIOD · SOURCE_ID",
      FRESHNESS="semanal", GEO="PRACA", TEMPORAL="semana", TERR=["T10"],
      ANCORA="CONTRATO",
      PROVA=("market.spec: '77 records, all provenance REAL_SOURCE, all sourceId "
             "IT-SRC-AGRIFOOD, FREQUENCY weekly, LATEST_OBSERVATION 2026-08-23'"),
      MEDIDO="ING.MARKET PRICE_NUM 77/77 — mas UMA fonte so"),
 dict(TOOL="MARKET", RAW_NEED="Serie de preco com 3+ pontos (para tendencia)",
      REQUIRED_FIELDS="serie temporal por produto x praca",
      FRESHNESS="semanal", GEO="PRACA", TEMPORAL="semana", TERR=["T10"],
      ANCORA="CONTRATO",
      PROVA=("market.spec fieldsThatDie: 'spark — requires 3+ points in one "
             "series. Real data has exactly ...'"),
      MEDIDO="OBSERVATIONS_IN_SERIES existe; series curtas"),
 dict(TOOL="MARKET", RAW_NEED="PRODUCAO, AREA e RENDIMENTO por cultura",
      REQUIRED_FIELDS="PRODUCTION · AREA · YIELD",
      FRESHNESS="anual", GEO="REGIAO", TEMPORAL="ano", TERR=["T1", "T10"],
      ANCORA="CONTRATO",
      PROVA=("market.spec fieldsThatDie: 'production[] — Production / Area / "
             "Yield / Stocks tonnages' · nota: 'No production, area, yield ...'"),
      MEDIDO="ING.MARKET nao tem coluna de producao, area nem rendimento"),
 dict(TOOL="MARKET", RAW_NEED="STOCKS / existencias",
      REQUIRED_FIELDS="STOCK",
      FRESHNESS="mensal", GEO="PAIS", TEMPORAL="mes", TERR=["T10"],
      ANCORA="CONTRATO", PROVA="market.spec fieldsThatDie: 'STOCKS' dentro de production[]",
      MEDIDO="ausente"),
 dict(TOOL="MARKET", RAW_NEED="IMPORTACAO e EXPORTACAO",
      REQUIRED_FIELDS="IMPORT · EXPORT",
      FRESHNESS="mensal", GEO="PAIS", TEMPORAL="mes", TERR=["T10"],
      ANCORA="CONTRATO",
      PROVA=("market.spec fieldsThatDie: 'trade + flow — SUPPLY & TRADE card with "
             "PRODUCTION/IMPORTS/EXPORTS/STOCKS bars'"),
      MEDIDO="ausente"),
 dict(TOOL="MARKET", RAW_NEED="CUSTO DE INSUMO (pressao de custo)",
      REQUIRED_FIELDS="input cost index",
      FRESHNESS="mensal", GEO="PAIS", TEMPORAL="mes", TERR=["T10"],
      ANCORA="CONTRATO",
      PROVA=("market.spec fieldsThatDie: 'inputs — INPUT COST PRESSURE incl. the "
             "Baltic Dry Index 2,843 OBSERVED value'"),
      MEDIDO="ausente do dado real (esta no fixture)"),
 dict(TOOL="MARKET", RAW_NEED="CLIMA DE CONFIANCA do produtor",
      REQUIRED_FIELDS="indice de confianca",
      FRESHNESS="trimestral", GEO="PAIS", TEMPORAL="trimestre", TERR=["T10", "T8"],
      ANCORA="CONTRATO",
      PROVA=("market.spec fieldsThatDie: 'confidence — ISMEA Indice del Clima di "
             "Fiducia (-1.4, Q1 2025)' — no fixture, nao ingerido"),
      MEDIDO="ausente do dado real"),
 dict(TOOL="MARKET", RAW_NEED="Preco para TOMATE, BETERRABA e MACA",
      REQUIRED_FIELDS="PRICE por essas culturas",
      FRESHNESS="semanal", GEO="PRACA", TEMPORAL="semana", TERR=["T10"],
      ANCORA="CONTRATO",
      PROVA=("market.spec: 'Tomato 0; Sugar Beet 0; Apple 0' e "
             "fieldsThatDie 'tomato / sugarbeet / apple crop tabs ... Measured 0 "
             "market records'"),
      MEDIDO="0 registos para as tres culturas"),
 dict(TOOL="MARKET", RAW_NEED="Serie de preco de UVA/VINHO viva",
      REQUIRED_FIELDS="PRICE vinho/uva",
      FRESHNESS="semanal", GEO="PRACA", TEMPORAL="semana", TERR=["T10"],
      ANCORA="CONTRATO",
      PROVA="market.spec: 'Grapevine 1 record, series stopped in 2025'",
      MEDIDO="1 registo, serie parada em 2025"),
 dict(TOOL="MARKET", RAW_NEED="Condicao de cultura / meteo agregado para mercado",
      REQUIRED_FIELDS="crop condition",
      FRESHNESS="mensal", GEO="REGIAO", TEMPORAL="mes", TERR=["T2", "T10"],
      ANCORA="CONTRATO",
      PROVA=("market.spec fieldsThatDie: 'weather — JRC MARS is not a registered "
             "source; no crop-condition record exists'"),
      MEDIDO="ausente"),

 # ══════════════ PORTFOLIO · Portafoglio ══════════════
 dict(TOOL="PORTFOLIO", RAW_NEED="Produto, registo e titular",
      REQUIRED_FIELDS="name · reg · holder · status · expiry",
      FRESHNESS="por alteracao", GEO="PAIS", TEMPORAL="dia", TERR=["T4"],
      ANCORA="CONTRATO",
      PROVA="portfolio.spec: 'Product identity keeps coming from IG.PRODUCTS (163)'",
      MEDIDO="ING.PRODUCTS 163 · reg/holder/status/expiry cheios"),
 dict(TOOL="PORTFOLIO", RAW_NEED="Substancia ativa do produto",
      REQUIRED_FIELDS="ai",
      FRESHNESS="por alteracao", GEO="PAIS", TEMPORAL="dia", TERR=["T4"],
      ANCORA="CONTRATO", PROVA="IG.LINKS carrega 'ai'",
      MEDIDO="ING.PRODUCTS ai 163/163 · ING.LINKS ai 219/219"),
 dict(TOOL="PORTFOLIO", RAW_NEED="Cultura e ALVO autorizados por produto",
      REQUIRED_FIELDS="crop · target · cropTerm",
      FRESHNESS="por alteracao", GEO="PAIS", TEMPORAL="dia", TERR=["T4"],
      ANCORA="CONTRATO",
      PROVA=("portfolio.spec: 'IG.LINKS — 219 rows ... carrying crop enum + Latin "
             "target + product + reg + ai + moa + labelUrl, covering only 19 "
             "distinct products'"),
      MEDIDO="ING.LINKS crop/target 219/219 — mas so 19 produtos distintos de 163"),
 dict(TOOL="PORTFOLIO", RAW_NEED="DOSE autorizada",
      REQUIRED_FIELDS="doses",
      FRESHNESS="por alteracao", GEO="PAIS", TEMPORAL="dia", TERR=["T4"],
      ANCORA="CONTRATO+DADO_MEDIDO",
      PROVA="portfolio.spec fieldsThatDie: 'Product dose' verdict SHOW_UNKNOWN",
      MEDIDO="ING.LINKS doses 35/219 (16%)"),
 dict(TOOL="PORTFOLIO", RAW_NEED="INTERVALO DE SEGURANCA (PHI) e n.o maximo de aplicacoes",
      REQUIRED_FIELDS="interval · maxApp",
      FRESHNESS="por alteracao", GEO="PAIS", TEMPORAL="dia", TERR=["T4"],
      ANCORA="DADO_MEDIDO",
      PROVA="os campos existem em IG.LINKS e estao quase vazios",
      MEDIDO="ING.LINKS interval 15/219 (7%) · maxApp 0/219 (0%)"),
 dict(TOOL="PORTFOLIO", RAW_NEED="MOMENTO DE APLICACAO / fase da cultura na aplicacao",
      REQUIRED_FIELDS="timing (fase da cultura)",
      FRESHNESS="por alteracao", GEO="PAIS", TEMPORAL="fase", TERR=["T4", "T1"],
      ANCORA="CONTRATO",
      PROVA=("portfolio.spec fieldsThatDie: 'Application timing / crop stage for a "
             "product use (Post-emergence · crop 2-6 leaves)' REMOVE_SUBCOMPONENT"),
      MEDIDO="ING.LINKS tem 'timing' mas o contrato diz que o valor renderizado e fixture"),
 dict(TOOL="PORTFOLIO", RAW_NEED="MECANISMO DE ACAO (FRAC/HRAC/IRAC)",
      REQUIRED_FIELDS="frac · hrac · irac · moa",
      FRESHNESS="por alteracao", GEO="—", TEMPORAL="—", TERR=["T4", "T5"],
      ANCORA="DADO_MEDIDO", PROVA="medido nos 163 produtos",
      MEDIDO="ING.PRODUCTS frac 8/163 (5%) · irac 10/163 (6%) · hrac 52/163 (32%)"),
 dict(TOOL="PORTFOLIO", RAW_NEED="Documento oficial do rotulo (PDF) e a sua data/versao",
      REQUIRED_FIELDS="labelUrl · LABEL_DATE · LABEL_VERSION",
      FRESHNESS="por alteracao", GEO="PAIS", TEMPORAL="dia", TERR=["T4"],
      ANCORA="CONTRATO",
      PROVA=("portfolio.spec: ITALY_LABEL_VERDICTS source = 'Claude Code reading "
             "of 163 official Italian product labels', audit date 2026-09-02"),
      MEDIDO="ING.PRODUCTS labelUrl 163/163 · nao existe LABEL_DATE nem LABEL_VERSION"),
 dict(TOOL="PORTFOLIO", RAW_NEED="ALTERACAO de autorizacao (o que mudou e quando)",
      REQUIRED_FIELDS="CHANGE · data da alteracao · retirada · extensao de uso",
      FRESHNESS="por alteracao", GEO="PAIS", TEMPORAL="dia", TERR=["T4"],
      ANCORA="CONTRATO",
      PROVA=("o contrato so tem um instantaneo datado (2026-09-02); nao existe "
             "colecao de alteracoes"),
      MEDIDO="ausente — nao existe registo de delta de autorizacao"),
 dict(TOOL="PORTFOLIO", RAW_NEED="AUTORIZACAO EXCECIONAL (art. 53)",
      REQUIRED_FIELDS="autorizacao excecional · validade · cultura · alvo",
      FRESHNESS="por acto", GEO="PAIS/REGIAO", TEMPORAL="dia", TERR=["T4"],
      ANCORA="DADO_MEDIDO",
      PROVA="ES-T4-002 existe no atlas para Espanha; equivalente italiano nao esta no casco",
      MEDIDO="ausente para Italia"),
 dict(TOOL="PORTFOLIO", RAW_NEED="Ligacao produto x janela de cultura",
      REQUIRED_FIELDS="PRODUCT_MATCHES por WINDOW_ID",
      FRESHNESS="anual", GEO="REGIAO", TEMPORAL="temporada", TERR=["T4", "T1"],
      ANCORA="CONTRATO",
      PROVA=("portfolio.spec: 'ITALY_CANONICAL.windows[].PRODUCT_MATCHES — MEASURED "
             "EMPTY: all 29 windows have PRODUCT_MATCHES = [], so this tier "
             "contributes 0 rows today'"),
      MEDIDO="0/29 · so ITALY_LABEL_VERDICTS (12 VERIFIED) liga produto a problema"),

 # ══════════════ SCIENCE · Intelligence Scientifica ══════════════
 dict(TOOL="SCIENCE", RAW_NEED="Trabalho cientifico com identidade",
      REQUIRED_FIELDS="TITLE · DOI · PUBLISHED_AT · VENUE · SOURCE_URL",
      FRESHNESS="continua", GEO="—", TEMPORAL="dia", TERR=["T5"],
      ANCORA="CONTRATO", PROVA="science.spec: 'APP.collections.scienceRecords (88, from IG.SCIENCE)'",
      MEDIDO="ING.SCIENCE 88 · DOI 86/88 (98%) · restantes campos 100%"),
 dict(TOOL="SCIENCE", RAW_NEED="Autor e instituicao do trabalho",
      REQUIRED_FIELDS="AUTHOR · INSTITUTION · ORCID",
      FRESHNESS="continua", GEO="—", TEMPORAL="—", TERR=["T5", "T6"],
      ANCORA="CONTRATO",
      PROVA=("science.spec: 'IG.SCIENCE[].INSTITUTION — 6 distinct values, the "
             "FIRST AUTHOR affiliation'"),
      MEDIDO="ING.SCIENCE AUTHOR/INSTITUTION/ORCID 88/88 — mas so 6 instituicoes distintas"),
 dict(TOOL="SCIENCE", RAW_NEED="Cultura e problema do trabalho",
      REQUIRED_FIELDS="CROP · ISSUE",
      FRESHNESS="continua", GEO="—", TEMPORAL="—", TERR=["T5", "T3"],
      ANCORA="CONTRATO", PROVA="IG.SCIENCE tem CROP e ISSUE",
      MEDIDO="ING.SCIENCE CROP/ISSUE 88/88"),
 dict(TOOL="SCIENCE", RAW_NEED="LOCAL DO ESTUDO (onde o ensaio foi feito)",
      REQUIRED_FIELDS="study location",
      FRESHNESS="continua", GEO="REGIAO", TEMPORAL="—", TERR=["T5"],
      ANCORA="CONTRATO",
      PROVA=("science.spec fieldsThatDie: 'record.location / locationShort "
             "(study area)' verdict SHOW_UNKNOWN"),
      MEDIDO="ausente — IG.SCIENCE tem COUNTRY_OF_FACT, nao local do ensaio"),
 dict(TOOL="SCIENCE", RAW_NEED="METODO e RESULTADO medido (eficacia)",
      REQUIRED_FIELDS="METHOD · RESULT · EFFICACY",
      FRESHNESS="continua", GEO="—", TEMPORAL="—", TERR=["T5"],
      ANCORA="CONTRATO",
      PROVA=("science.spec fieldsThatDie: 'record.study (the STUDY vocabulary)' "
             "DERIVABLE_FROM_REAL; nao existe campo de resultado"),
      MEDIDO="ausente — ha MATERIAL_TYPE e MATERIAL_ROLE, nao resultado"),
 dict(TOOL="SCIENCE", RAW_NEED="RESISTENCIA documentada (especie, mecanismo, regiao, ano)",
      REQUIRED_FIELDS="SPECIES · MECHANISM · REGIONS · FIRST_CASE_YEAR · AUTHORITY",
      FRESHNESS="anual", GEO="REGIAO", TEMPORAL="ano", TERR=["T3", "T5"],
      ANCORA="CONTRATO", PROVA="science.spec: 'APP.collections.resistance (34, from IG.RESISTANCE)'",
      MEDIDO="ING.RESISTANCE 34 registos · TODOS os 14 campos 100% cheios"),
 dict(TOOL="SCIENCE", RAW_NEED="ENSAIO DE CAMPO / trial com resultado",
      REQUIRED_FIELDS="TRIAL · ano · local · tratamento · resultado",
      FRESHNESS="anual", GEO="REGIAO", TEMPORAL="temporada", TERR=["T5"],
      ANCORA="DADO_MEDIDO",
      PROVA="nao existe colecao de ensaio no casco; IG.SCIENCE e bibliografia",
      MEDIDO="ausente"),
 dict(TOOL="SCIENCE", RAW_NEED="PROJETO de investigacao (quem financia, quem participa)",
      REQUIRED_FIELDS="PROJECT · parceiros · periodo",
      FRESHNESS="continua", GEO="—", TEMPORAL="ano", TERR=["T5", "T12"],
      ANCORA="DADO_MEDIDO", PROVA="IG.THEMES (5) agrega temas, nao projetos",
      MEDIDO="ausente"),

 # ══════════════ COMPETITORS · Concorrenza ══════════════
 dict(TOOL="COMPETITORS", RAW_NEED="Atividade publica do concorrente, com data",
      REQUIRED_FIELDS="company · platform · start · end · url · text",
      FRESHNESS="semanal", GEO="PAIS", TEMPORAL="dia", TERR=["T9"],
      ANCORA="CONTRATO",
      PROVA=("competitor.spec: '503 records ... geoClass: 414 REACHED_IN_ITALY, "
             "89 MULTI_COUNTRY_OR_UNRESOLVED'"),
      MEDIDO="ING.COMP_ACTIVITIES 503 · start/url/text ~82% · 89 sem pais resolvido"),
 dict(TOOL="COMPETITORS", RAW_NEED="CULTURA da atividade do concorrente",
      REQUIRED_FIELDS="crops",
      FRESHNESS="semanal", GEO="PAIS", TEMPORAL="dia", TERR=["T9", "T1"],
      ANCORA="DADO_MEDIDO", PROVA="medido nos 503 registos",
      MEDIDO="ING.COMP_ACTIVITIES crops 183/503 (36%)"),
 dict(TOOL="COMPETITORS", RAW_NEED="PROBLEMA/ALVO da atividade do concorrente",
      REQUIRED_FIELDS="issues",
      FRESHNESS="semanal", GEO="PAIS", TEMPORAL="dia", TERR=["T9", "T3"],
      ANCORA="DADO_MEDIDO", PROVA="medido nos 503 registos",
      MEDIDO="ING.COMP_ACTIVITIES issues 98/503 (19%)"),
 dict(TOOL="COMPETITORS", RAW_NEED="PRODUTO do concorrente na atividade",
      REQUIRED_FIELDS="products",
      FRESHNESS="semanal", GEO="PAIS", TEMPORAL="dia", TERR=["T9", "T4"],
      ANCORA="DADO_MEDIDO", PROVA="medido nos 503 registos",
      MEDIDO="ING.COMP_ACTIVITIES products 102/503 (20%)"),
 dict(TOOL="COMPETITORS", RAW_NEED="REGIAO da atividade do concorrente",
      REQUIRED_FIELDS="region",
      FRESHNESS="semanal", GEO="REGIAO", TEMPORAL="dia", TERR=["T9"],
      ANCORA="CONTRATO",
      PROVA="competitor.spec fieldsThatDie: 'a.region' verdict REMOVE_SUBCOMPONENT",
      MEDIDO="ausente do dado real — so pais"),
 dict(TOOL="COMPETITORS", RAW_NEED="REGISTO oficial do produto do concorrente",
      REQUIRED_FIELDS="reg · ai · crop · target do produto concorrente",
      FRESHNESS="por alteracao", GEO="PAIS", TEMPORAL="dia", TERR=["T9", "T4"],
      ANCORA="CONTRATO",
      PROVA=("competitor.spec fieldsThatDie: 'Competitor product crops, issues, "
             "first/last date, paid count, people count, linked cases'"),
      MEDIDO="ING.COMP_PRODUCTS 36 registos, 6 campos — sem registo oficial"),
 dict(TOOL="COMPETITORS", RAW_NEED="CONTEUDO TECNICO do concorrente (nao publicidade)",
      REQUIRED_FIELDS="tipo de conteudo · transcricao · ensaio citado",
      FRESHNESS="semanal", GEO="PAIS", TEMPORAL="dia", TERR=["T9", "T5"],
      ANCORA="CONTRATO",
      PROVA=("competitor.spec fieldsThatDie: 'a.transcript / a.transcriptLabel / "
             "a.duration'"),
      MEDIDO="ING.COMP_ACTIVITIES nao distingue tecnico de publicitario"),
 dict(TOOL="COMPETITORS", RAW_NEED="PESSOA do concorrente (quem fala por ele)",
      REQUIRED_FIELDS="person · role · relationship",
      FRESHNESS="semanal", GEO="PAIS", TEMPORAL="dia", TERR=["T9", "T6"],
      ANCORA="CONTRATO",
      PROVA=("competitor.spec fieldsThatDie: 'a.person / a.personId / a.personRole "
             "... the entire PEOPLE activity type'"),
      MEDIDO="ING.PEOPLE 15 registos · ROLE 5/15 (10 = NAO SEI)"),

 # ══════════════ VOICES · Voci dal Campo (sem contrato) ══════════════
 dict(TOOL="VOICES", RAW_NEED="Voz de campo com autor identificado",
      REQUIRED_FIELDS="PERSON · PERSON_IDENTITY_STATE · SOURCE_URL",
      FRESHNESS="semanal", GEO="REGIAO", TEMPORAL="dia", TERR=["T8", "T7"],
      ANCORA="DADO_MEDIDO", PROVA="medido em ING.VOICES",
      MEDIDO="ING.VOICES 17 · PERSON 17/17 · PERSON_IDENTITY_STATE 17/17"),
 dict(TOOL="VOICES", RAW_NEED="REGIAO da voz de campo",
      REQUIRED_FIELDS="REGION",
      FRESHNESS="semanal", GEO="REGIAO", TEMPORAL="dia", TERR=["T8"],
      ANCORA="DADO_MEDIDO",
      PROVA="ING.VOICES REGION = literal 'NAO SEI' em 17 de 17",
      MEDIDO="0/17 — todas NAO SEI"),
 dict(TOOL="VOICES", RAW_NEED="PAPEL de quem fala (produtor? tecnico? amador?)",
      REQUIRED_FIELDS="ROLE · ORGANIZATION",
      FRESHNESS="—", GEO="—", TEMPORAL="—", TERR=["T8", "T7"],
      ANCORA="DADO_MEDIDO",
      PROVA="ING.VOICES ROLE e ORGANIZATION = 'NAO SEI' em 17 de 17",
      MEDIDO="0/17 — todas NAO SEI"),
 dict(TOOL="VOICES", RAW_NEED="DATA da observacao de campo",
      REQUIRED_FIELDS="DATE (absoluta)",
      FRESHNESS="semanal", GEO="—", TEMPORAL="dia", TERR=["T8"],
      ANCORA="DADO_MEDIDO",
      PROVA=("ING.VOICES DATE = 'NAO SEI' em 17 de 17; existem DATE_RELATIVE e "
             "DATE_NOTE, que sao aproximacao"),
      MEDIDO="0/17 absoluta · 17/17 relativa"),
 dict(TOOL="VOICES", RAW_NEED="Cultura e problema relatados",
      REQUIRED_FIELDS="CROP · ISSUE · TEXT_ORIGINAL",
      FRESHNESS="semanal", GEO="REGIAO", TEMPORAL="dia", TERR=["T8", "T3"],
      ANCORA="DADO_MEDIDO", PROVA="medido em ING.VOICES",
      MEDIDO="ING.VOICES CROP/ISSUE/TEXT_ORIGINAL 17/17"),
 dict(TOOL="VOICES", RAW_NEED="CANAL com exemplo real e data de publicacao",
      REQUIRED_FIELDS="CHANNEL_URL · EXAMPLE_URL · EXAMPLE_PUBLISHED_AT · IDENTITY_STATE",
      FRESHNESS="semanal", GEO="—", TEMPORAL="dia", TERR=["T8"],
      ANCORA="DADO_MEDIDO", PROVA="medido em ING.CHANNELS",
      MEDIDO="ING.CHANNELS 30 registos · todos os 11 campos 100% cheios"),
 dict(TOOL="VOICES", RAW_NEED="Volume de vozes suficiente para ler um territorio",
      REQUIRED_FIELDS="n.o de vozes por regiao x cultura",
      FRESHNESS="semanal", GEO="REGIAO", TEMPORAL="semana", TERR=["T8"],
      ANCORA="CONTRATO",
      PROVA=("case.spec risco: 'VOICES.REGION is NAO SEI 17/...'; e as vozes "
             "cobrem 3 CASE_ID so"),
      MEDIDO="17 vozes no total, 3 casos — nao da para ler regiao nenhuma"),

 # ══════════════ FUTURE · Archivio segnali (sem contrato) ══════════════
 dict(TOOL="FUTURE", RAW_NEED="Sinal novo com o que se observou e quem o disse",
      REQUIRED_FIELDS="OBSERVED_FACTS · WHO_IS_TALKING · WHAT_CHANGED · SOURCE_IDS",
      FRESHNESS="continua", GEO="REGIAO", TEMPORAL="dia", TERR=["T3", "T5"],
      ANCORA="DADO_MEDIDO", PROVA="medido em ING.FUTURE_SIGNALS",
      MEDIDO="ING.FUTURE_SIGNALS 3 registos · campos cheios · REGION 2/3"),
 dict(TOOL="FUTURE", RAW_NEED="PRAGA OU DOENCA EMERGENTE (primeira deteccao)",
      REQUIRED_FIELDS="especie · primeira deteccao · local · autoridade",
      FRESHNESS="continua", GEO="REGIAO", TEMPORAL="dia", TERR=["T3", "T4"],
      ANCORA="DADO_MEDIDO",
      PROVA="nao existe colecao de primeira deteccao; EPPO nao esta ingerido para Italia",
      MEDIDO="ausente"),
 dict(TOOL="FUTURE", RAW_NEED="PIPELINE REGULATORIO (substancia em avaliacao/renovacao)",
      REQUIRED_FIELDS="substancia · estado · data prevista",
      FRESHNESS="mensal", GEO="UE", TEMPORAL="dia", TERR=["T4", "T12"],
      ANCORA="DADO_MEDIDO", PROVA="o casco tem instantaneo de autorizacao, nao pipeline",
      MEDIDO="ausente"),
 dict(TOOL="FUTURE", RAW_NEED="MUDANCA DE POLITICA em consulta",
      REQUIRED_FIELDS="acto · estado de consulta · prazo",
      FRESHNESS="mensal", GEO="UE/PAIS", TEMPORAL="dia", TERR=["T12"],
      ANCORA="DADO_MEDIDO", PROVA="ausente do casco",
      MEDIDO="ausente"),
 dict(TOOL="FUTURE", RAW_NEED="DESLOCACAO CLIMATICA que muda a pressao de praga",
      REQUIRED_FIELDS="serie climatica · anomalia · regiao",
      FRESHNESS="mensal", GEO="REGIAO", TEMPORAL="mes", TERR=["T2"],
      ANCORA="DADO_MEDIDO", PROVA="nao existe colecao de clima no casco",
      MEDIDO="ausente — nenhuma colecao de T2 no ITALY_INGEST"),
 dict(TOOL="FUTURE", RAW_NEED="Volume de sinais suficiente para ser um arquivo",
      REQUIRED_FIELDS="n.o de sinais",
      FRESHNESS="continua", GEO="—", TEMPORAL="—", TERR=["T3", "T5"],
      ANCORA="DADO_MEDIDO", PROVA="3 registos",
      MEDIDO="3 sinais — a tela chama-se 'Archivio' e tem tres linhas"),

 # ══════════════ FIELD_NET · Rete Commerciale di Campo (sem contrato) ══════════════
 dict(TOOL="FIELD_NET", RAW_NEED="Relato da rede comercial, com autor e data",
      REQUIRED_FIELDS="mensagem · autor · data · regiao",
      FRESHNESS="diaria", GEO="REGIAO", TEMPORAL="dia", TERR=["T7", "T8"],
      ANCORA="CONTRATO",
      PROVA=("tecido conectivo: 'Field Sales stays on AM.collections.fieldMessages "
             "(18 records, provenance SYNTHETIC_DEMO)'"),
      MEDIDO="18 registos, TODOS SYNTHETIC_DEMO — zero dado real"),
 dict(TOOL="FIELD_NET", RAW_NEED="Identidade do tecnico de campo (TSR)",
      REQUIRED_FIELDS="pessoa · papel · territorio",
      FRESHNESS="—", GEO="REGIAO", TEMPORAL="—", TERR=["T7"],
      ANCORA="CONTRATO", PROVA="tecido conectivo: 'D.TSR' e fixture",
      MEDIDO="ausente — fixture"),

 # ══════════════ RADAR · cruzamento, sem familia propria ══════════════
 dict(TOOL="RADAR", RAW_NEED="ENTRADA: janela de cultura com data e regiao",
      REQUIRED_FIELDS="ver WINDOWS",
      FRESHNESS="semanal", GEO="REGIAO", TEMPORAL="dia", TERR=["T1", "T3"],
      ANCORA="CONTRATO", PROVA="case.spec: o radar cruza janela x portfolio x concorrente",
      MEDIDO="29 janelas canonicas, 0 com observacao"),
 dict(TOOL="RADAR", RAW_NEED="ENTRADA: ligacao produto x problema",
      REQUIRED_FIELDS="ver PORTFOLIO",
      FRESHNESS="por alteracao", GEO="PAIS", TEMPORAL="dia", TERR=["T4"],
      ANCORA="CONTRATO",
      PROVA=("case.spec: 'Opp 002 CURRENT_EVIDENCE states in prose that six ADAMA "
             "products name Piralide/Diabrotica on the maize label, while its "
             "ADAMA_PRODUCTS array is empty'"),
      MEDIDO="12 triplos VERIFIED em ITALY_LABEL_VERDICTS"),
 dict(TOOL="RADAR", RAW_NEED="ENTRADA: sinal de concorrente na mesma cultura/problema",
      REQUIRED_FIELDS="ver COMPETITORS",
      FRESHNESS="semanal", GEO="PAIS", TEMPORAL="dia", TERR=["T9"],
      ANCORA="CONTRATO", PROVA="case.spec cruza atividade de concorrente",
      MEDIDO="503 atividades, 19% com problema identificado"),
 dict(TOOL="RADAR", RAW_NEED="ENTRADA: voz de campo na mesma cultura/problema",
      REQUIRED_FIELDS="ver VOICES",
      FRESHNESS="semanal", GEO="REGIAO", TEMPORAL="dia", TERR=["T8"],
      ANCORA="CONTRATO",
      PROVA="case.spec: 'VOICES.CASE_ID measures as IT-VINE-FLAVESCENCE (8), IT-MAIZE-WEED (8), IT-DURUM_WHEAT-FUSARIUM (1)'",
      MEDIDO="17 vozes em 3 casos · nenhuma com regiao"),
 dict(TOOL="RADAR", RAW_NEED="ENTRADA: mercado da mesma cultura",
      REQUIRED_FIELDS="ver MARKET",
      FRESHNESS="semanal", GEO="PRACA", TEMPORAL="semana", TERR=["T10"],
      ANCORA="CONTRATO", PROVA="case.spec cruza mercado",
      MEDIDO="77 precos, uma fonte, 3 culturas sem nada"),
 dict(TOOL="RADAR", RAW_NEED="ENTRADA: ciencia da mesma cultura/problema",
      REQUIRED_FIELDS="ver SCIENCE",
      FRESHNESS="continua", GEO="—", TEMPORAL="—", TERR=["T5"],
      ANCORA="CONTRATO", PROVA="case.spec cruza ciencia",
      MEDIDO="88 trabalhos + 60 investigadores + 34 resistencias"),
 dict(TOOL="RADAR", RAW_NEED="VOCABULARIO UNICO de cultura entre as camadas",
      REQUIRED_FIELDS="tabela de sinonimo de cultura",
      FRESHNESS="—", GEO="—", TEMPORAL="—", TERR=["T1"],
      ANCORA="CONTRATO",
      PROVA=("case.spec risco: 'Four incompatible crop vocabularies coexist in the "
             "real data and the synonym table is load-bearing'"),
      MEDIDO="4 vocabularios de cultura em simultaneo"),
 dict(TOOL="RADAR", RAW_NEED="IDENTIDADE UNICA de caso entre as camadas",
      REQUIRED_FIELDS="case id comum",
      FRESHNESS="—", GEO="—", TEMPORAL="—", TERR=["T1", "T3"],
      ANCORA="CONTRATO",
      PROVA=("case.spec risco: 'There is a FIFTH id space for cases'; e "
             "windows.spec: 'IT-HERO-001..003 vs IT-OPP-001..029 — there is no overlap'"),
      MEDIDO="5 espacos de id de caso, sem sobreposicao"),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"FERRAMENTAS MEDIDAS = {len(FERRAMENTAS)}")
    print(f"NECESSIDADES DE MATERIA-PRIMA = {len(NECESSIDADES)}")
    print()
    from collections import Counter
    c = Counter(n["TOOL"] for n in NECESSIDADES)
    for t, f in FERRAMENTAS.items():
        print(f"  {t:12s} {f['nome_it'][:28]:28s} {f['de_onde_vem_hoje']:8s} "
              f"{c.get(t,0):2d} necessidades")
    print()
    a = Counter(n["ANCORA"] for n in NECESSIDADES)
    print("ancora da necessidade:", dict(a))
    # toda necessidade declara territorio valido
    for n in NECESSIDADES:
        for t in n["TERR"]:
            if not _T.valido(t):
                raise SystemExit(f"territorio invalido em {n['RAW_NEED']!r}: {t}")
    print("todos os territorios citados existem no atlas: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
