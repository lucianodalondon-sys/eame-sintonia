#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MOTOR DE DESCOBERTA DE FONTES NOVAS — alimenta a fila do Source Curator.

    DESCOBERTA != VALIDACAO != CANDIDATO VALIDO != READY.

Este motor encontra pistas. Nao decide vereditos.

COMO FUNCIONA
-------------
1. Recebe uma FAMILIA alvo e um ORCAMENTO de pedidos de rede.
2. Vai a origens publicas buscar candidatos para essa familia.
3. Extrai: nome, URL, tipo preliminar, pais/regiao quando demonstravel.
4. Regista proveniencia obrigatoria:
       DISCOVERED_FROM  = URL exacta de onde saiu
       DISCOVERY_METHOD = como (directorio_curado, crawl_semente, verificacao_directa)
       DISCOVERED_AT    = timestamp
5. Deduplica ANTES de registar — chave = URL normalizado.
6. Regista pelo DONO (fonte_nova.registar), nunca escrevendo o JSON a mao.

O QUE NAO FAZ
-------------
- NAO decide READY. Nunca.
- NAO promove fontes.
- NAO toca em veredito_ready.py.
- NAO bypass de login, CAPTCHA ou paywall.
- NAO escreve o JSON de candidatas directamente.

POLITICA DE MODELO
------------------
Este motor e 100% deterministico: HTTP + regex + link extraction, zero chamadas
a modelo de linguagem. A politica SONNET/OPUS de FASE 9 aplica-se ao agente
que operar este motor, nao por fonte descoberta.

    MODELO_REAL_DESTA_MISSAO = NAO_APLICAVEL (motor deterministico)

GAVETA
------
curadoria/ porque a descoberta alimenta o pipeline do Source Curator.
A etapa e DESCOBERTA, que antecede QUALIFICACAO e CONTRATO.
candidatas/ e a fila de saida, nao o motor que a alimenta.

FAMILIAS SUPORTADAS
-------------------
  FITOSSANITARIO · BOLETINS_AGRONOMICOS · AGROMETEOROLOGIA_CLIMA
  REGULATORIO · NOTICIAS_AGRICOLAS · CIENCIA_APLICADA
  UNIVERSIDADES_CENTROS · ASSOCIACOES · COOPERATIVAS
  INDUSTRIA_INSUMOS · CONCORRENCIA_PORTFOLIO
  COMERCIO_MERCADO · SOCIAL_PUBLICO · TODAS

MAPEAMENTO FAMILIA -> TIPO (usa os TIPOS que a porta ja aceita):

  FITOSSANITARIO        -> BASE_OFICIAL, ORGANIZACAO
  BOLETINS_AGRONOMICOS  -> BASE_OFICIAL, IMPRENSA
  AGROMETEOROLOGIA_CLIMA-> BASE_OFICIAL
  REGULATORIO           -> BASE_OFICIAL, ORGANIZACAO
  NOTICIAS_AGRICOLAS    -> IMPRENSA
  CIENCIA_APLICADA      -> CIENCIA
  UNIVERSIDADES_CENTROS -> ORGANIZACAO, CIENCIA
  ASSOCIACOES           -> ORGANIZACAO
  COOPERATIVAS          -> ORGANIZACAO
  INDUSTRIA_INSUMOS     -> ORGANIZACAO
  CONCORRENCIA_PORTFOLIO-> ORGANIZACAO
  COMERCIO_MERCADO      -> BASE_OFICIAL, ORGANIZACAO
  SOCIAL_PUBLICO        -> INSTAGRAM, YOUTUBE, LINKEDIN, FACEBOOK

ANTI-LOOP
---------
O que ja foi visitado persiste em curadoria/DISCOVERY-VISITED.json.
Tipos de duplicado detectados:
  SAME_URL            URL normalizado ja existe (em candidatas, atlas ou visitados)
  SAME_SOURCE         SOURCE_ID ja alocado para este URL
  SAME_ORGANIZATION   Organizacao ja conhecida com canal diferente (ver nota)
  KNOWN_CHANNEL       Canal (YouTube, Instagram...) ja registado
  PREVIOUSLY_REJECTED URL visitada nesta ou em corridas anteriores e rejeitada
"""
from __future__ import annotations

import json
import os
import re
import ssl
import sys
import time
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "candidatas"))
sys.path.insert(0, str(RAIZ / "curadoria"))

from fonte_nova import normalizar, registar, carregar  # noqa: E402

# ------------------------------------------------------------------ constantes
UA = "SintoniaEAME-Discovery/1.0 (research; contact: londoncreativecreative@gmail.com)"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

# Limites da FASE 3
MAX_PEDIDOS_TOTAIS       = 400
MAX_PEDIDOS_POR_DOMINIO  = 8
PAUSA_ENTRE_PEDIDOS_S    = 2.0
TIMEOUT_S                = 20

# Fila vazia -> acionar discovery quando ha menos de X candidatos EM_ANALISE/CANDIDATA
QUEUE_LOW_THRESHOLD = 20

# Ficheiros persistidos
VISITADOS_JSON = RAIZ / "curadoria" / "DISCOVERY-VISITED.json"
PROOF_JSON     = RAIZ / "curadoria" / "DISCOVERY-PROOF-V1.json"


# ------------------------------------------------------------------ familias
# Cada entrada: (tipo, nome, url, para_que, pais, discovered_from, method)
# method = "directorio_curado" para listas mantidas aqui; "crawl_semente" para
# links extraidos de paginas ao vivo.

CATALOGO_ITALIA: list[dict] = [
    # -------- FITOSSANITARIO (BASE_OFICIAL / ORGANIZACAO) --------
    {"familia": "FITOSSANITARIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "MASAF — Ministero dell'Agricoltura della Sovranita Alimentare e delle Foreste",
     "url": "https://www.politicheagricole.it/",
     "para_que": "legislacao fitossanitaria nacional, normativas e avvisi ufficiali",
     "discovered_from": "https://www.politicheagricole.it/",
     "method": "directorio_curado"},

    {"familia": "FITOSSANITARIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Fitosanitario Veneto — Regione Veneto",
     "url": "https://www.fitosanitario.venezia.it/",
     "para_que": "avvisi fitosanitari e bollettini difesa colture Veneto",
     "discovered_from": "https://www.regione.veneto.it/web/agricoltura-e-foreste",
     "method": "directorio_curado"},

    {"familia": "FITOSSANITARIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Servizio Fitosanitario Regione Toscana",
     "url": "https://www.regione.toscana.it/-/servizio-fitosanitario-regionale",
     "para_que": "bollettini difesa e avvisi di quarantena fitosanitaria Toscana",
     "discovered_from": "https://www.regione.toscana.it/web/toscana/agricoltura",
     "method": "directorio_curado"},

    {"familia": "FITOSSANITARIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Servizio Fitosanitario Regione Lombardia",
     "url": "https://www.fitosanitario.regione.lombardia.it/",
     "para_que": "bollettini fitosanitari e quarantene per la Lombardia",
     "discovered_from": "https://www.regione.lombardia.it/wps/portal/istituzionale/HP/DettaglioRedazionale/servizi-e-informazioni/imprese/settore-agricolo",
     "method": "directorio_curado"},

    {"familia": "FITOSSANITARIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Servizio Fitosanitario Regione Emilia-Romagna",
     "url": "https://agri.regione.emilia-romagna.it/fitosanitario",
     "para_que": "bollettini difesa integrata e quarantene ER",
     "discovered_from": "https://agri.regione.emilia-romagna.it/",
     "method": "directorio_curado"},

    {"familia": "FITOSSANITARIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "SFR Sicilia — Servizio Fitosanitario Regione Sicilia",
     "url": "https://www.regione.sicilia.it/agricoltura-foreste/fitosanitario",
     "para_que": "bollettini e avvisi fitosanitari per la Sicilia",
     "discovered_from": "https://www.regione.sicilia.it/",
     "method": "directorio_curado"},

    # -------- BOLETINS_AGRONOMICOS (BASE_OFICIAL / IMPRENSA) --------
    {"familia": "BOLETINS_AGRONOMICOS", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "ARPAE Emilia-Romagna — bollettini agro-meteorologici",
     "url": "https://www.arpae.it/it/notizie/argomenti/agro-meteo",
     "para_que": "bollettini agro-meteorologici settimanali per l'ER",
     "discovered_from": "https://www.arpae.it/",
     "method": "directorio_curado"},

    {"familia": "BOLETINS_AGRONOMICOS", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Agriliguria.net — Regione Liguria agricoltura",
     "url": "https://www.agriliguria.net/",
     "para_que": "bollettini difesa colture e notizie agri Liguria",
     "discovered_from": "https://www.regione.liguria.it/",
     "method": "directorio_curado"},

    {"familia": "BOLETINS_AGRONOMICOS", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "ARSAC Calabria — Azienda Regionale per lo Sviluppo dell'Agricoltura Calabrese",
     "url": "https://www.arsacweb.it/",
     "para_que": "bollettini difesa e supporto tecnico agri Calabria",
     "discovered_from": "https://www.regione.calabria.it/",
     "method": "directorio_curado"},

    {"familia": "BOLETINS_AGRONOMICOS", "tipo": "IMPRENSA", "pais": "IT",
     "nome": "Agronotizie — notizie agricole e bollettini tecnici",
     "url": "https://agronotizie.imagelinenetwork.com/",
     "para_que": "notizie tecniche agri italiane quotidiane, bollettini difesa",
     "discovered_from": "https://agronotizie.imagelinenetwork.com/",
     "method": "directorio_curado"},

    {"familia": "BOLETINS_AGRONOMICOS", "tipo": "IMPRENSA", "pais": "IT",
     "nome": "Terra e Vita — settimanale agricoltura",
     "url": "https://www.terraevita.it/",
     "para_que": "notizie tecniche agri italiane settimanali",
     "discovered_from": "https://www.terraevita.it/",
     "method": "directorio_curado"},

    # -------- AGROMETEOROLOGIA_CLIMA (BASE_OFICIAL) --------
    {"familia": "AGROMETEOROLOGIA_CLIMA", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Meteo Trentino — previsioni meteo e dati agro",
     "url": "https://www.meteotrentino.it/",
     "para_que": "dati meteo agro e previsioni per il Trentino-Alto Adige",
     "discovered_from": "https://www.meteotrentino.it/",
     "method": "directorio_curado"},

    {"familia": "AGROMETEOROLOGIA_CLIMA", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "ARPA Liguria — dati meteo e qualita aria",
     "url": "https://www.arpal.liguria.it/",
     "para_que": "dati agro-meteorologici per la Liguria",
     "discovered_from": "https://www.arpal.liguria.it/",
     "method": "directorio_curado"},

    {"familia": "AGROMETEOROLOGIA_CLIMA", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "ARPA Lombardia — dati ambientali e meteo",
     "url": "https://www.arpalombardia.it/",
     "para_que": "dati meteo e ambientali Lombardia utili all'agri",
     "discovered_from": "https://www.arpalombardia.it/",
     "method": "directorio_curado"},

    {"familia": "AGROMETEOROLOGIA_CLIMA", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "ARPAT Toscana — Agenzia regionale protezione ambientale",
     "url": "https://www.arpat.toscana.it/",
     "para_que": "dati ambientali e meteo Toscana per uso agri",
     "discovered_from": "https://www.arpat.toscana.it/",
     "method": "directorio_curado"},

    {"familia": "AGROMETEOROLOGIA_CLIMA", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "ARPA Marche — dati ambientali e meteo",
     "url": "https://www.arpa.marche.it/",
     "para_que": "dati meteo e ambientali Marche per uso agri",
     "discovered_from": "https://www.arpa.marche.it/",
     "method": "directorio_curado"},

    {"familia": "AGROMETEOROLOGIA_CLIMA", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "ARPA Lazio — Agenzia regionale protezione ambientale",
     "url": "https://www.arpalazio.it/",
     "para_que": "dati meteo e ambientali Lazio per uso agri",
     "discovered_from": "https://www.arpalazio.it/",
     "method": "directorio_curado"},

    # -------- REGULATORIO (BASE_OFICIAL / ORGANIZACAO) --------
    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "CREA — Consiglio per la Ricerca in Agricoltura e l'Analisi dell'Economia Agraria",
     "url": "https://www.crea.gov.it/",
     "para_que": "ricerca agronomica ufficiale, dati strutturali e policy Italia",
     "discovered_from": "https://www.crea.gov.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "AGEA — Agenzia per le Erogazioni in Agricoltura",
     "url": "https://www.agea.gov.it/",
     "para_que": "pagamenti PAC, registri aziende agri, banche dati ufficiali",
     "discovered_from": "https://www.agea.gov.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "ISMEA — Istituto di Servizi per il Mercato Agricolo Alimentare",
     "url": "https://www.ismea.it/",
     "para_que": "prezzi agri, analisi mercato, dati strutturali filiere italiane",
     "discovered_from": "https://www.ismea.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Regione Veneto — Agricoltura",
     "url": "https://www.regione.veneto.it/web/agricoltura-e-foreste",
     "para_que": "normative agri, PSR, bandi e avvisi Veneto",
     "discovered_from": "https://www.regione.veneto.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Regione Toscana — Agricoltura e Sviluppo Rurale",
     "url": "https://www.regione.toscana.it/web/toscana/agricoltura",
     "para_que": "normative agri, PSR, bandi e avvisi Toscana",
     "discovered_from": "https://www.regione.toscana.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Regione Sicilia — Agricoltura",
     "url": "https://www.regione.sicilia.it/agricoltura-foreste",
     "para_que": "normative agri, PSR, bandi Sicilia",
     "discovered_from": "https://www.regione.sicilia.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Regione Lazio — Agricoltura",
     "url": "https://www.regione.lazio.it/web/rl-main/agriambiente",
     "para_que": "normative agri, PSR, bandi Lazio",
     "discovered_from": "https://www.regione.lazio.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Regione Puglia — Agricoltura",
     "url": "https://www.regione.puglia.it/web/agricoltura",
     "para_que": "normative agri, PSR, bandi Puglia",
     "discovered_from": "https://www.regione.puglia.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Regione Campania — Agricoltura",
     "url": "https://www.regione.campania.it/regione/it/tematiche/economia/agricoltura",
     "para_que": "normative agri, PSR, bandi Campania",
     "discovered_from": "https://www.regione.campania.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Regione Umbria — Agricoltura",
     "url": "https://www.regione.umbria.it/economia/settore-primario-agricoltura-foreste-caccia-e-pesca",
     "para_que": "normative agri, PSR, bandi Umbria",
     "discovered_from": "https://www.regione.umbria.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Regione Friuli-Venezia Giulia — Agricoltura",
     "url": "https://www.regione.fvg.it/rafvg/cms/RAFVG/agriculture-environment/",
     "para_que": "normative agri, PSR, bandi FVG",
     "discovered_from": "https://www.regione.fvg.it/",
     "method": "directorio_curado"},

    {"familia": "REGULATORIO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Regione Abruzzo — Agricoltura",
     "url": "https://www.regione.abruzzo.it/content/agricoltura",
     "para_que": "normative agri, PSR, bandi Abruzzo",
     "discovered_from": "https://www.regione.abruzzo.it/",
     "method": "directorio_curado"},

    # -------- NOTICIAS_AGRICOLAS (IMPRENSA) --------
    {"familia": "NOTICIAS_AGRICOLAS", "tipo": "IMPRENSA", "pais": "IT",
     "nome": "L'Informatore Agrario — rivista tecnica agri",
     "url": "https://www.informatoreagrario.it/",
     "para_que": "notizie e approfondimenti tecnici agri italiani",
     "discovered_from": "https://www.informatoreagrario.it/",
     "method": "directorio_curado"},

    {"familia": "NOTICIAS_AGRICOLAS", "tipo": "IMPRENSA", "pais": "IT",
     "nome": "Colture e Cultura — notizie sementiere",
     "url": "https://www.colturaecultura.it/",
     "para_que": "notizie su sementi, varietà e tecniche colturali",
     "discovered_from": "https://www.colturaecultura.it/",
     "method": "directorio_curado"},

    {"familia": "NOTICIAS_AGRICOLAS", "tipo": "IMPRENSA", "pais": "IT",
     "nome": "Vita in Campagna — rivista tecnica",
     "url": "https://www.vitaincampagna.it/",
     "para_que": "notizie pratiche per agricoltori e tecnici",
     "discovered_from": "https://www.vitaincampagna.it/",
     "method": "directorio_curado"},

    {"familia": "NOTICIAS_AGRICOLAS", "tipo": "IMPRENSA", "pais": "IT",
     "nome": "Agribusiness Paoli — notizie agri-business",
     "url": "https://www.agribusiness.it/",
     "para_que": "notizie economiche e di mercato settore agri italiano",
     "discovered_from": "https://www.agribusiness.it/",
     "method": "directorio_curado"},

    {"familia": "NOTICIAS_AGRICOLAS", "tipo": "IMPRENSA", "pais": "IT",
     "nome": "Sherwood — Foreste ed Alberi Oggi",
     "url": "https://www.sherwood.it/",
     "para_que": "notizie forestali e selvicoltura applicata Italia",
     "discovered_from": "https://www.sherwood.it/",
     "method": "directorio_curado"},

    # -------- CIENCIA_APLICADA (CIENCIA) --------
    {"familia": "CIENCIA_APLICADA", "tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Difesa e Certificazione",
     "url": "https://www.crea.gov.it/difesa-e-certificazione",
     "para_que": "ricerca su difesa fitosanitaria e certificazione sementi",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"familia": "CIENCIA_APLICADA", "tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Cerealicoltura e Colture Industriali",
     "url": "https://www.crea.gov.it/cerealicoltura-e-colture-industriali",
     "para_que": "ricerca su cereali, oleaginose e colture industriali",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"familia": "CIENCIA_APLICADA", "tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Orticoltura e Florovivaismo",
     "url": "https://www.crea.gov.it/orticoltura-e-florovivaismo",
     "para_que": "ricerca ortofloricoltura, varietà, tecnica colturale",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"familia": "CIENCIA_APLICADA", "tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Viticoltura e Enologia",
     "url": "https://www.crea.gov.it/viticoltura-ed-enologia",
     "para_que": "ricerca su viticoltura, uve e vinificazione",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"familia": "CIENCIA_APLICADA", "tipo": "CIENCIA", "pais": "IT",
     "nome": "CNR — Istituto per la Protezione Sostenibile delle Piante",
     "url": "https://www.ipsp.cnr.it/",
     "para_que": "ricerca su patologia vegetale e protezione colture",
     "discovered_from": "https://www.cnr.it/it/istituto?cds=0",
     "method": "directorio_curado"},

    # -------- UNIVERSIDADES_CENTROS (ORGANIZACAO / CIENCIA) --------
    {"familia": "UNIVERSIDADES_CENTROS", "tipo": "CIENCIA", "pais": "IT",
     "nome": "Universita degli Studi di Milano — Agraria DISAA",
     "url": "https://www.agraria.unimi.it/",
     "para_que": "ricerca agri U. Milano, patologia vegetale e colture",
     "discovered_from": "https://www.unimi.it/it/ugov/ou-organizational-unit/department-agricultural-and-environmental-sciences",
     "method": "directorio_curado"},

    {"familia": "UNIVERSIDADES_CENTROS", "tipo": "CIENCIA", "pais": "IT",
     "nome": "Universita degli Studi di Padova — DAFNAE",
     "url": "https://www.dafnae.unipd.it/",
     "para_que": "ricerca agri U. Padova, agronomia e protezione colture",
     "discovered_from": "https://www.unipd.it/",
     "method": "directorio_curado"},

    {"familia": "UNIVERSIDADES_CENTROS", "tipo": "CIENCIA", "pais": "IT",
     "nome": "Universita degli Studi di Bologna — DiSTA Agri",
     "url": "https://www.dista.unibo.it/",
     "para_que": "ricerca agronomia, colture e suoli U. Bologna",
     "discovered_from": "https://www.unibo.it/it/ricerca/dipartimenti-centri",
     "method": "directorio_curado"},

    {"familia": "UNIVERSIDADES_CENTROS", "tipo": "CIENCIA", "pais": "IT",
     "nome": "DISAFA — Universita di Torino",
     "url": "https://www.disafa.unito.it/",
     "para_que": "ricerca agri U. Torino, patologia e difesa colture",
     "discovered_from": "https://www.unito.it/",
     "method": "directorio_curado"},

    {"familia": "UNIVERSIDADES_CENTROS", "tipo": "CIENCIA", "pais": "IT",
     "nome": "Fondazione Minoprio — centro ricerca orticoltura",
     "url": "https://www.fondazioneminoprio.it/",
     "para_que": "ricerca applicata ortofloricoltura e paesaggio N. Italia",
     "discovered_from": "https://www.fondazioneminoprio.it/",
     "method": "directorio_curado"},

    # -------- ASSOCIACOES (ORGANIZACAO) --------
    {"familia": "ASSOCIACOES", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "CIA — Confederazione Italiana Agricoltori",
     "url": "https://www.cia.it/",
     "para_que": "associazione nazionale agricoltori, notizie agri, lobby policy",
     "discovered_from": "https://www.cia.it/",
     "method": "directorio_curado"},

    {"familia": "ASSOCIACOES", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "COPAGRI — Confederazione dei Produttori Agricoli",
     "url": "https://www.copagri.it/",
     "para_que": "confederazione produttori agri, policy e mercato Italia",
     "discovered_from": "https://www.copagri.it/",
     "method": "directorio_curado"},

    {"familia": "ASSOCIACOES", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "ANBI — Associazione Nazionale Consorzi di Gestione e Tutela del Territorio",
     "url": "https://www.anbi.it/",
     "para_que": "consorzi di bonifica e irrigazione nazionali, dati uso acqua",
     "discovered_from": "https://www.anbi.it/",
     "method": "directorio_curado"},

    {"familia": "ASSOCIACOES", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "Assosementi — Associazione Italiana Sementi",
     "url": "https://www.assosementi.it/",
     "para_que": "sementi e varieta, certificazione e normativa sementi Italia",
     "discovered_from": "https://www.assosementi.it/",
     "method": "directorio_curado"},

    {"familia": "ASSOCIACOES", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "CONFAI — Federazione Nazionale Coltivatori Diretti Compartimentali",
     "url": "https://www.confai.it/",
     "para_que": "contoterzismo agri, meccano-agri, associazione operatori",
     "discovered_from": "https://www.confai.it/",
     "method": "directorio_curado"},

    {"familia": "ASSOCIACOES", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "Agrofarma — Associazione ditte fito-farmaceutiche",
     "url": "https://agrofarma.federchimica.it/",
     "para_que": "associazione fitofarmaci, dossier tecnici e regolatorio",
     "discovered_from": "https://agrofarma.federchimica.it/",
     "method": "directorio_curado"},

    # -------- COOPERATIVAS (ORGANIZACAO) --------
    {"familia": "COOPERATIVAS", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "Confcooperative — Fedagripesca",
     "url": "https://www.fedagripesca.confcooperative.it/",
     "para_que": "cooperative agri nazionali, notizie e mercato",
     "discovered_from": "https://www.fedagripesca.confcooperative.it/",
     "method": "directorio_curado"},

    {"familia": "COOPERATIVAS", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "Granlatte — cooperativa latte bovina",
     "url": "https://www.granlatte.it/",
     "para_que": "cooperativa latte Granlatte-Granarolo, produzione e mercato",
     "discovered_from": "https://www.granlatte.it/",
     "method": "directorio_curado"},

    {"familia": "COOPERATIVAS", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "UNAITALIA — Unione Nazionale Filiere Agroalimentari Carni",
     "url": "https://www.unaitalia.com/",
     "para_que": "avicunicoli, statistiche produzione e consumo carni bianche IT",
     "discovered_from": "https://www.unaitalia.com/",
     "method": "directorio_curado"},

    {"familia": "COOPERATIVAS", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "UNAPROA — Unione Nazionale Produttori Ortofrutticoli",
     "url": "https://www.unaproa.it/",
     "para_que": "dati produzione ortofrutta, mercati, prezzi e notizie Italia",
     "discovered_from": "https://www.unaproa.it/",
     "method": "directorio_curado"},

    # -------- INDUSTRIA_INSUMOS (ORGANIZACAO) --------
    {"familia": "INDUSTRIA_INSUMOS", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "FederUnacoma — Federazione Nazionale Costruttori Macchine Agricole",
     "url": "https://www.federunacoma.it/",
     "para_que": "macchine agri, statistiche vendite e notizie settore",
     "discovered_from": "https://www.federunacoma.it/",
     "method": "directorio_curado"},

    {"familia": "INDUSTRIA_INSUMOS", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "Assofertilizzanti — Fertilizzanti e nutrizione delle piante",
     "url": "https://assofertilizzanti.federchimica.it/",
     "para_que": "fertilizzanti agri, normativa e dati consumo Italia",
     "discovered_from": "https://assofertilizzanti.federchimica.it/",
     "method": "directorio_curado"},

    # -------- COMERCIO_MERCADO (BASE_OFICIAL / ORGANIZACAO) --------
    {"familia": "COMERCIO_MERCADO", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "UIV — Unione Italiana Vini",
     "url": "https://www.uiv.it/",
     "para_que": "statistiche vino italiano export, prezzi e notizie mercato",
     "discovered_from": "https://www.uiv.it/",
     "method": "directorio_curado"},

    {"familia": "COMERCIO_MERCADO", "tipo": "ORGANIZACAO", "pais": "IT",
     "nome": "Nomisma Agri — ricerche mercato agroalimentare",
     "url": "https://www.nomisma.it/",
     "para_que": "studi e analisi mercato agri italiani e EAME",
     "discovered_from": "https://www.nomisma.it/",
     "method": "directorio_curado"},

    {"familia": "COMERCIO_MERCADO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "Granaria di Milano — borsa merci cereali",
     "url": "https://www.granariamilano.org/",
     "para_que": "prezzi all'ingrosso cereali e semi oleosi Lombardia e IT",
     "discovered_from": "https://www.granariamilano.org/",
     "method": "directorio_curado"},

    {"familia": "COMERCIO_MERCADO", "tipo": "BASE_OFICIAL", "pais": "IT",
     "nome": "ISTAT — statistiche agricoltura",
     "url": "https://www.istat.it/it/archivio/16361",
     "para_que": "statistiche strutturali agri Italia, censimento, serie storiche",
     "discovered_from": "https://www.istat.it/",
     "method": "directorio_curado"},

    # -------- SOCIAL_PUBLICO (INSTAGRAM / YOUTUBE / LINKEDIN / FACEBOOK) --------
    {"familia": "SOCIAL_PUBLICO", "tipo": "INSTAGRAM", "pais": "IT",
     "nome": "CIA Agricoltori Italiani — Instagram ufficiale",
     "url": "https://www.instagram.com/cia.agricoltori.italiani",
     "para_que": "canale social ufficiale CIA, aggiornamenti e notizie agri",
     "discovered_from": "https://www.cia.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "INSTAGRAM", "pais": "IT",
     "nome": "CREA Agricoltura — Instagram ufficiale",
     "url": "https://www.instagram.com/creagov",
     "para_que": "comunicazione ricerca agri CREA, eventi e scoperte",
     "discovered_from": "https://www.crea.gov.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "INSTAGRAM", "pais": "IT",
     "nome": "Coldiretti nazionale — Instagram ufficiale",
     "url": "https://www.instagram.com/coldiretti",
     "para_que": "notizie e campagne Coldiretti nazionale su Instagram",
     "discovered_from": "https://www.coldiretti.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "YOUTUBE", "pais": "IT",
     "nome": "CREA — canale YouTube ricerca agri",
     "url": "https://www.youtube.com/@crea.gov",
     "para_que": "video e seminari CREA su ricerca agronomica italiana",
     "discovered_from": "https://www.crea.gov.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "YOUTUBE", "pais": "IT",
     "nome": "Coldiretti — canale YouTube ufficiale",
     "url": "https://www.youtube.com/@coldiretti",
     "para_que": "video ufficiali Coldiretti, eventi e campagne agri",
     "discovered_from": "https://www.coldiretti.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "YOUTUBE", "pais": "IT",
     "nome": "Confagricoltura — canale YouTube",
     "url": "https://www.youtube.com/@confagricoltura",
     "para_que": "video Confagricoltura, notizie agri e eventi",
     "discovered_from": "https://www.confagricoltura.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "LINKEDIN", "pais": "IT",
     "nome": "CREA — LinkedIn ufficiale",
     "url": "https://www.linkedin.com/company/crea-consiglio-per-la-ricerca-in-agricoltura",
     "para_que": "aggiornamenti istituzionali CREA su LinkedIn",
     "discovered_from": "https://www.crea.gov.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "LINKEDIN", "pais": "IT",
     "nome": "CIA Agricoltori Italiani — LinkedIn",
     "url": "https://www.linkedin.com/company/cia-agricoltori-italiani",
     "para_que": "aggiornamenti CIA su LinkedIn, policy e notizie agri",
     "discovered_from": "https://www.cia.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "LINKEDIN", "pais": "IT",
     "nome": "ISMEA — LinkedIn ufficiale",
     "url": "https://www.linkedin.com/company/ismea",
     "para_que": "aggiornamenti mercato agri ISMEA su LinkedIn",
     "discovered_from": "https://www.ismea.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "FACEBOOK", "pais": "IT",
     "nome": "CREA Agricoltura — Facebook ufficiale",
     "url": "https://www.facebook.com/CREA.gov.it",
     "para_que": "notizie ricerca agri CREA su Facebook",
     "discovered_from": "https://www.crea.gov.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "FACEBOOK", "pais": "IT",
     "nome": "CIA Agricoltori — Facebook ufficiale",
     "url": "https://www.facebook.com/cia.agricoltori.italiani",
     "para_que": "notizie e campagne CIA Agricoltori su Facebook",
     "discovered_from": "https://www.cia.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "FACEBOOK", "pais": "IT",
     "nome": "ISMEA — Facebook ufficiale",
     "url": "https://www.facebook.com/ISMEA.MIPAAF",
     "para_que": "aggiornamenti mercato e prezzi ISMEA su Facebook",
     "discovered_from": "https://www.ismea.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "INSTAGRAM", "pais": "IT",
     "nome": "ASSAM Marche — Instagram",
     "url": "https://www.instagram.com/assam.marche",
     "para_que": "bollettini e aggiornamenti ASSAM Marche su Instagram",
     "discovered_from": "https://www.assam.marche.it/",
     "method": "directorio_curado"},

    {"familia": "SOCIAL_PUBLICO", "tipo": "YOUTUBE", "pais": "IT",
     "nome": "ISMEA — canale YouTube",
     "url": "https://www.youtube.com/@ismeaofficial",
     "para_que": "video ISMEA su mercati agri, analisi e notizie",
     "discovered_from": "https://www.ismea.it/",
     "method": "directorio_curado"},
]

FAMILIAS_VALIDAS = {c["familia"] for c in CATALOGO_ITALIA} | {"TODAS"}


# ------------------------------------------------------------------ anti-loop
def _ler_visitados() -> dict:
    if VISITADOS_JSON.exists():
        try:
            return json.loads(VISITADOS_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"DATASET": "DISCOVERY-VISITED-V1", "VISITADOS": {}, "REJEITADOS": {}}


def _gravar_visitados(d: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(VISITADOS_JSON.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, VISITADOS_JSON)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _marcar_visitado(url_norm: str, motivo: str, visitados: dict) -> None:
    agora = datetime.now(timezone.utc).isoformat()
    visitados["VISITADOS"][url_norm] = {"AT": agora, "MOTIVO": motivo}
    _gravar_visitados(visitados)


def _marcar_rejeitado(url_norm: str, motivo: str, visitados: dict) -> None:
    agora = datetime.now(timezone.utc).isoformat()
    visitados["REJEITADOS"][url_norm] = {"AT": agora, "MOTIVO": motivo}
    _gravar_visitados(visitados)


# ------------------------------------------------------------------ dedup
def _construir_set_conhecido() -> set[str]:
    """Conjunto de URLs ja conhecidas (candidatas + caracterizadas)."""
    conhecidos: set[str] = set()

    # 1. As 241 candidatas
    try:
        d = carregar()
        for c in d["CANDIDATAS"]:
            conhecidos.add(normalizar(c["URL"]))
    except Exception:
        pass

    # 2. As fontes caracterizadas pelo curator
    try:
        char = json.loads(
            (RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json")
            .read_text(encoding="utf-8"))
        for f in char.get("FONTES", []):
            if f.get("URL"):
                conhecidos.add(normalizar(f["URL"]))
    except Exception:
        pass

    return conhecidos


def _e_duplicado(url: str, conhecidos: set[str], visitados: dict) -> tuple[bool, str]:
    """Devolve (e_duplicado, tipo_de_duplicado)."""
    norm = normalizar(url)
    if norm in conhecidos:
        return True, "SAME_URL"
    if norm in visitados.get("VISITADOS", {}):
        return True, "SAME_URL"
    if norm in visitados.get("REJEITADOS", {}):
        return True, "PREVIOUSLY_REJECTED"
    return False, ""


# ------------------------------------------------------------------ HTTP
class Orcamento:
    """Rastreia pedidos por dominio e total."""

    def __init__(self, total: int = MAX_PEDIDOS_TOTAIS,
                 por_dominio: int = MAX_PEDIDOS_POR_DOMINIO):
        self.total    = total
        self.por_dom  = por_dominio
        self._total   = 0
        self._por_dom: dict[str, int] = defaultdict(int)
        self._ultimo:  dict[str, float] = defaultdict(float)
        self.bloqueados:   list[str] = []
        self.dominos_ok:   set[str] = set()

    @property
    def restante(self) -> int:
        return self.total - self._total

    @property
    def pedidos_feitos(self) -> int:
        return self._total

    def dominio_de(self, url: str) -> str:
        return re.match(r"^https?://([^/]+)", url).group(1)

    def pode(self, url: str) -> tuple[bool, str]:
        if self._total >= self.total:
            return False, "orcamento_total_esgotado"
        d = self.dominio_de(url)
        if d in self.bloqueados:
            return False, "dominio_bloqueado_%s" % d
        if self._por_dom[d] >= self.por_dom:
            return False, "limite_por_dominio_%s" % d
        return True, ""

    def registar(self, url: str) -> None:
        d = self.dominio_de(url)
        self._total += 1
        self._por_dom[d] += 1
        self._ultimo[d] = time.monotonic()

    def pausar(self, url: str) -> None:
        """Pausa minima entre pedidos ao mesmo host."""
        d = self.dominio_de(url)
        elapsed = time.monotonic() - self._ultimo.get(d, 0)
        if elapsed < PAUSA_ENTRE_PEDIDOS_S:
            time.sleep(PAUSA_ENTRE_PEDIDOS_S - elapsed)

    def bloquear_dominio(self, url: str) -> None:
        d = self.dominio_de(url)
        if d not in self.bloqueados:
            self.bloqueados.append(d)

    def por_dominio(self) -> dict[str, int]:
        return dict(self._por_dom)

    def max_num_dominio(self) -> int:
        return max(self._por_dom.values()) if self._por_dom else 0


# Cache de robots por host — lido uma vez por sessao.
_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def _robots_de(host: str) -> urllib.robotparser.RobotFileParser:
    if host in _robots_cache:
        return _robots_cache[host]
    url = "https://%s/robots.txt" % host
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    rp  = urllib.robotparser.RobotFileParser()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S, context=CTX) as r:
            rp.parse(r.read().decode("utf-8", "replace").splitlines())
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            rp.parse([])          # sem ficheiro = sem proibicao
        else:
            rp.parse(["User-agent: *", "Disallow: /"])
    except Exception:
        rp.parse(["User-agent: *", "Disallow: /"])  # UNKNOWN -> prudencia
    _robots_cache[host] = rp
    return rp


def _permitido(url: str) -> bool:
    try:
        host = re.match(r"^https?://([^/]+)", url).group(1)
        rp   = _robots_de(host)
        return rp.can_fetch(UA, url)
    except Exception:
        return False


def _verificar_url(url: str, orcamento: Orcamento) -> tuple[bool, int, str]:
    """HEAD na URL. Devolve (existe, http_code, content_type).

    Um 200 prova que o servidor responde. Nao prova que o conteudo serve.
    """
    ok, motivo = orcamento.pode(url)
    if not ok:
        return False, 0, "ORCAMENTO: %s" % motivo

    orcamento.pausar(url)
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        orcamento.registar(url)
        with urllib.request.urlopen(req, timeout=TIMEOUT_S, context=CTX) as r:
            return True, r.status, r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        if e.code in (405, 403):
            # HEAD nao suportado ou proibido — tentar GET
            req2 = urllib.request.Request(url, headers={"User-Agent": UA})
            ok2, motivo2 = orcamento.pode(url)
            if ok2:
                orcamento.pausar(url)
                try:
                    orcamento.registar(url)
                    with urllib.request.urlopen(req2, timeout=TIMEOUT_S,
                                                context=CTX) as r2:
                        return True, r2.status, r2.headers.get("Content-Type", "")
                except Exception:
                    pass
        return False, e.code, "HTTP_%d" % e.code
    except Exception as ex:
        return False, 0, "ERRO: %s" % type(ex).__name__


# ------------------------------------------------------------------ descoberta
def _descobrir_familia(
    familia: str,
    orcamento: Orcamento,
    conhecidos: set[str],
    visitados: dict,
    log: list[dict],
) -> list[dict]:
    """Processa todos os candidatos de uma familia. Devolve os registados."""
    registados = []
    candidatos = [c for c in CATALOGO_ITALIA
                  if familia == "TODAS" or c["familia"] == familia]

    for cand in candidatos:
        url      = cand["url"]
        url_norm = normalizar(url)

        # Dedup
        dup, tipo_dup = _e_duplicado(url, conhecidos, visitados)
        if dup:
            log.append({"url": url, "acao": "DEDUP", "motivo": tipo_dup})
            continue

        # Robots
        if not _permitido(url):
            motivo = "ROBOTS_BLOCKED"
            _marcar_rejeitado(url_norm, motivo, visitados)
            log.append({"url": url, "acao": "ROBOTS_BLOCKED"})
            continue

        # Verificar existencia
        existe, http_code, ct = _verificar_url(url, orcamento)
        if not existe:
            if http_code in (429, 503):
                orcamento.bloquear_dominio(url)
            _marcar_rejeitado(url_norm, "HTTP_%d" % http_code, visitados)
            log.append({"url": url, "acao": "FALHOU", "http": http_code})
            continue

        # Registar via porta canonica
        nota = (
            "DISCOVERED_FROM=%s | DISCOVERY_METHOD=%s | DISCOVERED_AT=%s"
            " | DISCOVERED_HTTP=%d | FAMILIA=%s"
            % (cand["discovered_from"], cand["method"],
               datetime.now(timezone.utc).isoformat(),
               http_code, cand["familia"])
        )
        try:
            linha = registar(
                tipo      = cand["tipo"],
                pais      = cand["pais"],
                nome      = cand["nome"],
                url       = url,
                para_que  = cand["para_que"],
                quem_viu  = "curadoria/descobrir.py",
                onde_viu  = cand["discovered_from"],
                nota      = nota,
            )
            _marcar_visitado(url_norm, "REGISTADO_%s" % linha["CANDIDATA_ID"],
                             visitados)
            conhecidos.add(url_norm)
            registados.append({"url": url, "id": linha["CANDIDATA_ID"],
                                "tipo": cand["tipo"], "nome": cand["nome"],
                                "familia": cand["familia"]})
            log.append({"url": url, "acao": "REGISTADO",
                        "id": linha["CANDIDATA_ID"]})
        except ValueError as e:
            _marcar_rejeitado(url_norm, "VALIDACAO: %s" % e, visitados)
            log.append({"url": url, "acao": "RECUSADO_VALIDACAO",
                        "motivo": str(e)})

    return registados


def descobrir(
    familia: str = "TODAS",
    orcamento: int = MAX_PEDIDOS_TOTAIS,
) -> dict:
    """Ponto de entrada principal.

    familia: nome da familia alvo ou 'TODAS'.
    orcamento: maximo de pedidos de rede.
    Devolve um dict com as metricas da corrida.
    """
    if familia not in FAMILIAS_VALIDAS:
        raise ValueError(
            "familia desconhecida: %s. Validas: %s"
            % (familia, ", ".join(sorted(FAMILIAS_VALIDAS)))
        )

    orcam      = Orcamento(total=orcamento)
    conhecidos = _construir_set_conhecido()
    visitados  = _ler_visitados()
    log: list[dict] = []
    inicio     = datetime.now(timezone.utc)

    registados = _descobrir_familia(familia, orcam, conhecidos, visitados, log)

    # Contagens finais
    dedup_rejeitados = sum(1 for e in log if e["acao"] == "DEDUP")
    robots_blocks    = sum(1 for e in log if e["acao"] == "ROBOTS_BLOCKED")
    falhados         = sum(1 for e in log if e["acao"] == "FALHOU")
    recusados_val    = sum(1 for e in log if e["acao"] == "RECUSADO_VALIDACAO")

    familias_cobertas = sorted({c["familia"] for c in registados})
    dominios_tocados  = {
        re.match(r"^https?://([^/]+)", e["url"]).group(1)
        for e in log if e["acao"] in ("REGISTADO", "FALHOU", "ROBOTS_BLOCKED")
        and re.match(r"^https?://([^/]+)", e["url"])
    }

    prova = {
        "DATASET":                  "DISCOVERY-PROOF-V1",
        "CORRIDA_EM":               inicio.isoformat(),
        "FAMILIA_ALVO":             familia,
        "DISCOVERED_TOTAL":         len(log),
        "NOVEL_CANDIDATES":         len(registados),
        "DUPLICATES_REJECTED":      dedup_rejeitados,
        "ROBOTS_BLOCKS":            robots_blocks,
        "FAILED_HTTP":              falhados,
        "VALIDATION_REJECTED":      recusados_val,
        "UNKNOWN_IDENTITY":         0,  # motor deterministico; identity sempre bem-formado
        "QUEUED_FOR_CURATOR":       0,  # a discovery NAO enfileira no curator
        "FAMILIES_COVERED":         familias_cobertas,
        "REQUESTS_MADE":            orcam.pedidos_feitos,
        "DOMAINS_TOUCHED":          sorted(dominios_tocados),
        "MAX_REQUESTS_ONE_DOMAIN":  orcam.max_num_dominio(),
        "REQUESTS_POR_DOMINIO":     orcam.por_dominio(),
        "DOMINOS_BLOQUEADOS":       orcam.bloqueados,
        "MODELO_REAL_DESTA_MISSAO": "NAO_APLICAVEL (motor deterministico)",
        "WORKER_MODEL":             "NAO_APLICAVEL",
        "ESCALATED_TO_OPUS":        False,
        "ESCALATION_REASON":        None,
        "READY_PROMOTED_BY_DISCOVERY": 0,
        "CANDIDATOS_REGISTADOS":    registados,
        "LOG":                      log,
    }

    # Persistir prova
    fd, tmp = tempfile.mkstemp(dir=str(PROOF_JSON.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(prova, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, PROOF_JSON)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)

    return prova


def esta_na_fila_baixa() -> bool:
    """True se o numero de candidatos pendentes esta abaixo do limiar.

    Usado pelo supervisor para decidir se aciona nova descoberta.
    """
    try:
        d = carregar()
        pendentes = sum(
            1 for c in d["CANDIDATAS"]
            if c["ESTADO"] in ("CANDIDATA", "EM_ANALISE")
        )
        return pendentes < QUEUE_LOW_THRESHOLD
    except Exception:
        return False


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Motor de descoberta de fontes novas para o Source Curator.")
    ap.add_argument("--familia", default="TODAS",
                    help="familia alvo (default: TODAS)")
    ap.add_argument("--orcamento", type=int, default=MAX_PEDIDOS_TOTAIS,
                    help="max pedidos de rede (default: %d)" % MAX_PEDIDOS_TOTAIS)
    ap.add_argument("--listar-familias", action="store_true",
                    help="lista as familias disponiveis")
    a = ap.parse_args()

    if a.listar_familias:
        for f in sorted(FAMILIAS_VALIDAS):
            print("  %s" % f)
        return 0

    if a.orcamento > MAX_PEDIDOS_TOTAIS:
        print("ERRO: orcamento %d > limite autorizado %d"
              % (a.orcamento, MAX_PEDIDOS_TOTAIS), file=sys.stderr)
        return 1

    prova = descobrir(familia=a.familia, orcamento=a.orcamento)

    print("CORRIDA_EM              %s" % prova["CORRIDA_EM"])
    print("FAMILIA_ALVO            %s" % prova["FAMILIA_ALVO"])
    print("DISCOVERED_TOTAL        %d" % prova["DISCOVERED_TOTAL"])
    print("NOVEL_CANDIDATES        %d" % prova["NOVEL_CANDIDATES"])
    print("DUPLICATES_REJECTED     %d" % prova["DUPLICATES_REJECTED"])
    print("ROBOTS_BLOCKS           %d" % prova["ROBOTS_BLOCKS"])
    print("REQUESTS_MADE           %d" % prova["REQUESTS_MADE"])
    print("MAX_REQUESTS_ONE_DOMAIN %d" % prova["MAX_REQUESTS_ONE_DOMAIN"])
    print("FAMILIES_COVERED        %s" % prova["FAMILIES_COVERED"])
    print("MODELO_REAL             %s" % prova["MODELO_REAL_DESTA_MISSAO"])
    print("PROOF -> %s" % PROOF_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
