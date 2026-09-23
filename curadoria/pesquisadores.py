#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DESCOBERTA DE PESQUISADORES — fontes CIENCIA para o Source Curator.

Missao P1 · 23/09/2026 — ordem do dono: "o maior numero de fontes,
principalmente de pesquisadores".

Reutiliza a infraestrutura de curadoria/descobrir.py (Orcamento, dedup,
robots.txt, registar via porta canonica). Adiciona um catalogo dedicado
de fontes de pesquisa agricola/agroalimentar italiana.

O QUE ESTE FICHEIRO NAO FAZ
----------------------------
- NAO qualifica. Quem decide e o Curator.
- NAO escreve no atlas nem no livro do lifecycle.
- NAO faz login, bypass de CAPTCHA ou paywall.
- NAO escreve o JSON de candidatas diretamente.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "candidatas"))
sys.path.insert(0, str(RAIZ / "curadoria"))

from fonte_nova import registar, normalizar, carregar  # noqa: E402
import descobrir as D                                   # noqa: E402

PROOF_JSON = RAIZ / "curadoria" / "PESQUISADORES-PROOF-V1.json"
LISTA_JSON = RAIZ / "curadoria" / "PESQUISADORES-LISTA-V1.json"

# ---------------------------------------------------------------------------
# Catalogo de pesquisadores
# Cada entrada: tipo deve ser CIENCIA (missao especifica).
# discovered_from = de onde a informacao de que existe veio.
# method = "directorio_curado" — lista mantida aqui.
# ---------------------------------------------------------------------------

CATALOGO_PESQUISADORES: list[dict] = [

    # -------- CREA — centros ainda nao na fila --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Zootecnia e Acquacoltura",
     "url": "https://www.crea.gov.it/zootecnia-e-acquacoltura",
     "para_que": "ricerca zootecnica, acquacoltura e produzioni animali Italia",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Olivicoltura, Frutticoltura e Agrumicoltura",
     "url": "https://www.crea.gov.it/olivicoltura-frutticoltura-e-agrumicoltura",
     "para_que": "ricerca olive, frutta e agrumi; bollettini tecnici e varietali",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Agricoltura e Ambiente",
     "url": "https://www.crea.gov.it/agricoltura-e-ambiente",
     "para_que": "ricerca suolo, agri sostenibile, cambiamento climatico",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Alimenti e Nutrizione",
     "url": "https://www.crea.gov.it/alimenti-e-nutrizione",
     "para_que": "ricerca composizione alimenti, sicurezza e qualita nutrizionale",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Foreste e Legno",
     "url": "https://www.crea.gov.it/foreste-e-legno",
     "para_que": "ricerca selvicoltura, foreste produttive e uso del legno Italia",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Politiche e Bioeconomia",
     "url": "https://www.crea.gov.it/politiche-e-bioeconomia",
     "para_que": "analisi policy agri, bioeconomia, dati strutturali filiere",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA — Centro Ingegneria e Trasformazioni Agroalimentari",
     "url": "https://www.crea.gov.it/ingegneria-e-trasformazioni-agroalimentari",
     "para_que": "ricerca meccanizzazione, trasformazione, packaging agri",
     "discovered_from": "https://www.crea.gov.it/centri-di-ricerca",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CREA Notizie — comunicati e aggiornamenti",
     "url": "https://www.crea.gov.it/notizie",
     "para_que": "notizie ufficiali CREA su ricerca agri, scoperte e pubblicazioni",
     "discovered_from": "https://www.crea.gov.it/",
     "method": "directorio_curado"},

    # -------- CNR — istituti agri-rilevanti --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CNR ISPA — Istituto di Scienze delle Produzioni Alimentari",
     "url": "https://www.ispa.cnr.it/",
     "para_que": "ricerca produzione alimentare, sicurezza e qualita; pubblicazioni CNR",
     "discovered_from": "https://www.cnr.it/it/ricerca-e-innovazione/settori/agrifood",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CNR IBE — Istituto per la BioEconomia",
     "url": "https://www.ibe.cnr.it/",
     "para_que": "ricerca bioeconomia, biomasse, uso sostenibile risorse agri",
     "discovered_from": "https://www.cnr.it/it/ricerca-e-innovazione/settori/agrifood",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CNR ISAFoM — Istituto per i Sistemi Agricoli e Forestali del Mediterraneo",
     "url": "https://www.isafom.cnr.it/",
     "para_que": "ricerca agro-foreste-meteo Mediterraneo; bollettini tecnici",
     "discovered_from": "https://www.cnr.it/it/ricerca-e-innovazione/settori/agrifood",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CNR IBBR — Istituto di Bioscienze e Biorisorse",
     "url": "https://www.ibbr.cnr.it/",
     "para_que": "ricerca biodiversita vegetale, genetica e miglioramento colture",
     "discovered_from": "https://www.cnr.it/it/ricerca-e-innovazione/settori/agrifood",
     "method": "directorio_curado"},

    # -------- Fondazione Edmund Mach --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Fondazione Edmund Mach (FEM) — Centro di Ricerca",
     "url": "https://www.fmach.it/",
     "para_que": "ricerca vite, frutticoltura alpina, entomologia, genomica agri",
     "discovered_from": "https://www.fmach.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "FEM — Notizie e comunicati stampa",
     "url": "https://www.fmach.it/Comunicazione/Notizie",
     "para_que": "aggiornamenti FEM su ricerca applicata a frutto/vite/entomologia",
     "discovered_from": "https://www.fmach.it/",
     "method": "directorio_curado"},

    # -------- ENEA agri --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "ENEA — Dipartimento Biotecnologie e Agroindustria",
     "url": "https://www.enea.it/it/ricerca-e-innovazione/settori/biotecnologie-agroindustriali",
     "para_que": "ricerca ENEA su biotecnologie agri, nuove varieta, bioraffinerie",
     "discovered_from": "https://www.enea.it/",
     "method": "directorio_curado"},

    # -------- Accademia dei Georgofili --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Accademia dei Georgofili",
     "url": "https://www.georgofili.it/",
     "para_que": "accademia storica agri Firenze; convegni, pubblicazioni e notizie",
     "discovered_from": "https://www.georgofili.it/",
     "method": "directorio_curado"},

    # -------- IZS — Istituti Zooprofilattici --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "IZSVe — Istituto Zooprofilattico Sperimentale delle Venezie",
     "url": "https://www.izsvenezie.it/",
     "para_que": "diagnostica malattie animali e zoonosi; notizie e pubblicazioni NE Italia",
     "discovered_from": "https://www.izsvenezie.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "IZSAM — Istituto Zooprofilattico Abruzzo e Molise",
     "url": "https://www.izsam.it/",
     "para_que": "diagnostica zoonosi e sanita animale Centro-Sud Italia; pubblicazioni",
     "discovered_from": "https://www.izsam.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "IZSTO — Istituto Zooprofilattico Piemonte, Liguria e Valle d'Aosta",
     "url": "https://www.izsto.it/",
     "para_que": "diagnostica zoonosi Nord-Ovest Italia; bollettini e notizie",
     "discovered_from": "https://www.izsto.it/",
     "method": "directorio_curado"},

    # -------- Universita — dipartimenti agri non ancora in lista --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "DAGRI — Dip. Scienze e Tecnologie Agrarie Univ. Firenze",
     "url": "https://www.dagri.unifi.it/",
     "para_que": "ricerca agri Firenze; pubblicazioni, tesi, notizie del dipartimento",
     "discovered_from": "https://www.unifi.it/dipartimenti/dagri",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "DISAAA-A — Dip. Scienze Agrarie Univ. Pisa",
     "url": "https://www.agr.unipi.it/",
     "para_que": "ricerca agri Pisa; pubblicazioni, banche dati e notizie",
     "discovered_from": "https://www.unipi.it/index.php/scienze-agrarie",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "DSA3 — Dip. Scienze Agrarie Univ. Perugia",
     "url": "https://www.dsa3.unipg.it/",
     "para_que": "ricerca agri Perugia; olivicoltura, suoli, colture tipiche IT centrale",
     "discovered_from": "https://www.unipg.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "DISSPA — Dip. Scienze del Suolo Univ. Bari",
     "url": "https://www.uniba.it/ricerca/dipartimenti/disspa",
     "para_que": "ricerca agri Bari; suoli, piante, produzioni vegetali Puglia",
     "discovered_from": "https://www.uniba.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "SAF — Dip. Scienze Agrarie Univ. Palermo",
     "url": "https://www.unipa.it/strutture/dipartimenti/saf/",
     "para_que": "ricerca agri Palermo; produzioni tipiche Sicilia, olivicoltura, vite",
     "discovered_from": "https://www.unipa.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Dip. Agraria — Univ. Sassari",
     "url": "https://www.agraria.uniss.it/",
     "para_que": "ricerca agri Sassari; produzioni tipiche Sardegna",
     "discovered_from": "https://www.uniss.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "DISA — Dip. Scienze Agroalimentari Univ. Udine",
     "url": "https://www.disa.uniud.it/",
     "para_que": "ricerca agri Udine; vite, foraggio, zootecnia FVG",
     "discovered_from": "https://www.uniud.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Dip. DAFNE — Univ. della Tuscia (Viterbo)",
     "url": "https://www.unitus.it/it/dipartimento/dafne/",
     "para_que": "ricerca agri Viterbo; produzioni tipiche, foreste e ambiente",
     "discovered_from": "https://www.unitus.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Fac. Biosciences e Tecn. Agroalim. — Univ. Teramo",
     "url": "https://www.unite.it/unitn/controller?param0=dipartimentoagro",
     "para_que": "ricerca agri e alim Teramo; produzioni animali e qualita alimenti",
     "discovered_from": "https://www.unite.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "SAFE — Scuola Scienze Agrarie Univ. Basilicata",
     "url": "https://safe.unibas.it/",
     "para_que": "ricerca agri Basilicata; colture tipiche Sud Italia",
     "discovered_from": "https://www.unibas.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Fac. Scienze Agrarie e Alimentari UCSC — Piacenza",
     "url": "https://www.cattolicapiacenza.it/facolta/scienze-agrarie-alimentari-ambientali/",
     "para_que": "ricerca agri Cattolica Piacenza; zootecnia, enologia, colture intensive",
     "discovered_from": "https://www.cattolica.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Scuola Superiore Sant'Anna — Institute of Life Sciences",
     "url": "https://www.santannapisa.it/en/institute/life-sciences",
     "para_que": "ricerca bioagri Sant'Anna Pisa; biotecnologie piante e agri di precisione",
     "discovered_from": "https://www.santannapisa.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "DAFNE — Dip. Agri e Forestale Univ. Perugia",
     "url": "https://agr.unipg.it/",
     "para_que": "ricerca agro-forestale Perugia; pubblicazioni e notizie",
     "discovered_from": "https://www.unipg.it/",
     "method": "directorio_curado"},

    # -------- Riviste scientifiche italiane open-access --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Italian Journal of Agronomy — PAGEPress",
     "url": "https://www.pagepressjournals.org/index.php/ija",
     "para_que": "rivista open-access agronomia italiana; articoli e fascicoli",
     "discovered_from": "https://www.pagepressjournals.org/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Italian Journal of Animal Science — PAGEPress",
     "url": "https://www.pagepressjournals.org/index.php/ijas",
     "para_que": "rivista open-access zootecnia italiana; articoli e fascicoli",
     "discovered_from": "https://www.pagepressjournals.org/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Italian Journal of Food Science — PAGEPress",
     "url": "https://www.pagepressjournals.org/index.php/ijfs",
     "para_que": "rivista open-access scienze alimentari italiane; articoli e fascicoli",
     "discovered_from": "https://www.pagepressjournals.org/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Italus Hortus — rivista SOI di orticoltura",
     "url": "https://www.soihs.it/italus-hortus/",
     "para_que": "rivista italiana orticoltura; articoli tecnici e di ricerca",
     "discovered_from": "https://www.soihs.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Agrochimica — rivista internazionale di chimica agri",
     "url": "https://www.agrochimica.it/",
     "para_que": "rivista agrochemica italiana; ricerca su fertilizzanti e suolo",
     "discovered_from": "https://www.agrochimica.it/",
     "method": "directorio_curado"},

    # -------- Societa scientifiche agri italiane --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "SIGA — Società Italiana di Genetica Agraria",
     "url": "https://www.sigaweb.org/",
     "para_que": "genetica agri, convegni e bollettini; miglioramento genetico colture IT",
     "discovered_from": "https://www.sigaweb.org/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "SOI — Società di Orticoltura Italiana",
     "url": "https://www.soihs.it/",
     "para_que": "orticoltura italiana; convegni, rivista e notizie settore",
     "discovered_from": "https://www.soihs.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "AISSA — Associazione Italiana Società Scientifiche Agrarie",
     "url": "https://www.aissa.it/",
     "para_que": "federazione societa agri; congressi, agenda ricerca italiana",
     "discovered_from": "https://www.aissa.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "SIA — Società Italiana di Agronomia",
     "url": "https://sia.agronomia.it/",
     "para_que": "agronomia italiana; convegni, ricerche e pubblicazioni SIA",
     "discovered_from": "https://sia.agronomia.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "SIPaV — Società Italiana di Patologia Vegetale",
     "url": "https://sipav.org/",
     "para_que": "patologia vegetale; notizie, convegni e pubblicazioni SIPaV",
     "discovered_from": "https://sipav.org/",
     "method": "directorio_curado"},

    # -------- ISPRA --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "ISPRA — Istituto Superiore Protezione e Ricerca Ambientale",
     "url": "https://www.isprambiente.gov.it/it/attivita/suolo-territorio",
     "para_que": "dati suolo e territorio, erosione e biodiversita agri; rapporti ISPRA",
     "discovered_from": "https://www.isprambiente.gov.it/",
     "method": "directorio_curado"},

    # -------- Ordini e Collegi professionali (agronomos e periti) --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CONAF — Consiglio Nazionale Dottori Agronomi e Forestali",
     "url": "https://www.conaf.it/",
     "para_que": "ordine nazionale agronomi IT; notizie, eventi, pubblicazioni professionali",
     "discovered_from": "https://www.conaf.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "CONAF — Notizie e comunicati",
     "url": "https://www.conaf.it/category/notizie/",
     "para_que": "notizie CONAF: normativa agri, eventi ordine, pubblicazioni agronomi IT",
     "discovered_from": "https://www.conaf.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Collegio Nazionale dei Periti Agrari e dei Periti Agrari Laureati",
     "url": "https://www.peritiagrari.it/",
     "para_que": "collegio periti agrari IT; notizie professionali, tecnica agraria",
     "discovered_from": "https://www.peritiagrari.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Collegio Agrotecnici e Agrotecnici Laureati",
     "url": "https://www.agrotecnici.it/",
     "para_que": "agrotecnici IT; notizie professionali, tecnica colture e zootecnia",
     "discovered_from": "https://www.agrotecnici.it/",
     "method": "directorio_curado"},

    # -------- Riviste e media tecnici agronomici --------
    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Informatore Agrario — rivista tecnica agri Italia",
     "url": "https://www.informatoreagrario.it/",
     "para_que": "principale rivista tecnica agronomi IT; articoli, notizie e normativa",
     "discovered_from": "https://www.informatoreagrario.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Informatore Agrario — Notizie",
     "url": "https://www.informatoreagrario.it/redazione/notizie/",
     "para_que": "notizie Informatore Agrario: tecnica agri, ricerca, normativa IT",
     "discovered_from": "https://www.informatoreagrario.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Terra e Vita — Agri media Edagricole",
     "url": "https://www.terraevita.edagricole.it/",
     "para_que": "rivista agri tecnica; notizie filiere, ricerca e innovazione IT",
     "discovered_from": "https://www.terraevita.edagricole.it/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "AgroNotizie — notizie settore agri IT",
     "url": "https://agronotizie.imagelinenetwork.com/",
     "para_que": "aggregatore notizie agri IT; ricerca, tecnica, mercati e normativa",
     "discovered_from": "https://agronotizie.imagelinenetwork.com/",
     "method": "directorio_curado"},

    {"tipo": "CIENCIA", "pais": "IT",
     "nome": "Georgofili Info — newsletter accademica agri",
     "url": "https://www.georgofili.info/",
     "para_que": "newsletter Georgofili su ricerca agri e politiche; pubblicazioni agronomi",
     "discovered_from": "https://www.georgofili.it/",
     "method": "directorio_curado"},

    # -------- Canali social istituzionali (tipo matching: YOUTUBE/LINKEDIN) --------
    {"tipo": "YOUTUBE", "pais": "IT",
     "nome": "FEM — Fondazione Edmund Mach YouTube",
     "url": "https://www.youtube.com/@fondazioneedmundmach",
     "para_que": "video tecnici FEM su vite, frutticoltura, entomologia e genomica",
     "discovered_from": "https://www.fmach.it/",
     "method": "directorio_curado"},

    {"tipo": "YOUTUBE", "pais": "IT",
     "nome": "CREA — Centro Ricerche YouTube",
     "url": "https://www.youtube.com/@creagov",
     "para_que": "video istituzionali CREA: ricerca agri, divulgazione e risultati",
     "discovered_from": "https://www.crea.gov.it/",
     "method": "directorio_curado"},

    {"tipo": "YOUTUBE", "pais": "IT",
     "nome": "Informatore Agrario YouTube",
     "url": "https://www.youtube.com/@InformatoreAgrario",
     "para_que": "video tecnici agronomi IT: interviste ricercatori, prove in campo",
     "discovered_from": "https://www.informatoreagrario.it/",
     "method": "directorio_curado"},

    {"tipo": "YOUTUBE", "pais": "IT",
     "nome": "AgroNotizie YouTube",
     "url": "https://www.youtube.com/@agronotizie",
     "para_que": "video notizie agri IT: ricerca applicata, tecnica colturale",
     "discovered_from": "https://agronotizie.imagelinenetwork.com/",
     "method": "directorio_curado"},

    {"tipo": "LINKEDIN", "pais": "IT",
     "nome": "CONAF LinkedIn",
     "url": "https://www.linkedin.com/company/conaf-consiglio-nazionale-dottori-agronomi-e-forestali/",
     "para_que": "aggiornamenti CONAF su professione agronomo IT; notizie e policy",
     "discovered_from": "https://www.conaf.it/",
     "method": "directorio_curado"},

    {"tipo": "LINKEDIN", "pais": "IT",
     "nome": "CREA Ricerca LinkedIn",
     "url": "https://www.linkedin.com/company/crea-council-for-agricultural-research-and-economics/",
     "para_que": "aggiornamenti CREA: ricerca agri IT, pubblicazioni e opportunita",
     "discovered_from": "https://www.crea.gov.it/",
     "method": "directorio_curado"},

    {"tipo": "LINKEDIN", "pais": "IT",
     "nome": "Fondazione Edmund Mach LinkedIn",
     "url": "https://www.linkedin.com/company/fondazione-edmund-mach/",
     "para_que": "aggiornamenti FEM: vite, mela, genomica; offerte e pubblicazioni",
     "discovered_from": "https://www.fmach.it/",
     "method": "directorio_curado"},
]


def descobrir_pesquisadores(orcamento: int = 200) -> dict:
    """Corre discovery focada em fontes CIENCIA (pesquisadores).

    Reutiliza toda a infraestrutura de descobrir.py:
    - Orcamento, robots.txt, rate limiting
    - Dedup contra candidatas + characterization
    - Registo pela porta canonica (fonte_nova.registar)
    """
    orcam      = D.Orcamento(total=orcamento)
    conhecidos = D._construir_set_conhecido()
    visitados  = D._ler_visitados()
    log: list[dict] = []
    inicio     = datetime.now(timezone.utc)

    registados: list[dict] = []

    for cand in CATALOGO_PESQUISADORES:
        url      = cand["url"]
        url_norm = normalizar(url)

        # Dedup
        dup, tipo_dup = D._e_duplicado(url, conhecidos, visitados)
        if dup:
            log.append({"url": url, "acao": "DEDUP", "motivo": tipo_dup})
            continue

        # Robots
        if not D._permitido(url):
            D._marcar_rejeitado(url_norm, "ROBOTS_BLOCKED", visitados)
            log.append({"url": url, "acao": "ROBOTS_BLOCKED"})
            continue

        # Verificar existencia (HEAD ou GET)
        existe, http_code, ct = D._verificar_url(url, orcam)
        if not existe:
            if http_code in (429, 503):
                orcam.bloquear_dominio(url)
            D._marcar_rejeitado(url_norm, "HTTP_%d" % http_code, visitados)
            log.append({"url": url, "acao": "FALHOU", "http": http_code})
            continue

        nota = (
            "DISCOVERED_FROM=%s | DISCOVERY_METHOD=%s | DISCOVERED_AT=%s"
            " | DISCOVERED_HTTP=%d | MISSAO=PESQUISADORES-P1"
            % (cand["discovered_from"], cand["method"],
               datetime.now(timezone.utc).isoformat(), http_code)
        )
        try:
            linha = registar(
                tipo     = cand["tipo"],
                pais     = cand["pais"],
                nome     = cand["nome"],
                url      = url,
                para_que = cand["para_que"],
                quem_viu = "curadoria/pesquisadores.py",
                onde_viu = cand["discovered_from"],
                nota     = nota,
            )
            D._marcar_visitado(url_norm, "REGISTADO_%s" % linha["CANDIDATA_ID"],
                               visitados)
            conhecidos.add(url_norm)
            registados.append({
                "url": url, "id": linha["CANDIDATA_ID"],
                "tipo": cand["tipo"], "nome": cand["nome"],
            })
            log.append({"url": url, "acao": "REGISTADO",
                        "id": linha["CANDIDATA_ID"]})
        except ValueError as e:
            D._marcar_rejeitado(url_norm, "VALIDACAO: %s" % e, visitados)
            log.append({"url": url, "acao": "RECUSADO_VALIDACAO", "motivo": str(e)})

    dedup   = sum(1 for e in log if e["acao"] == "DEDUP")
    robots  = sum(1 for e in log if e["acao"] == "ROBOTS_BLOCKED")
    falhou  = sum(1 for e in log if e["acao"] == "FALHOU")

    doms_tocados = {
        re.match(r"^https?://([^/]+)", e["url"]).group(1)
        for e in log
        if e["acao"] in ("REGISTADO", "FALHOU", "ROBOTS_BLOCKED")
        and re.match(r"^https?://([^/]+)", e["url"])
    }

    prova = {
        "DATASET":                  "PESQUISADORES-PROOF-V1",
        "MISSAO":                   "P1-PESQUISADORES-2026-09-23",
        "CORRIDA_EM":               inicio.isoformat(),
        "DISCOVERED_TOTAL":         len(log),
        "NOVEL_CANDIDATES":         len(registados),
        "DUPLICATES_REJECTED":      dedup,
        "ROBOTS_BLOCKS":            robots,
        "FAILED_HTTP":              falhou,
        "REQUESTS_MADE":            orcam.pedidos_feitos,
        "DOMAINS_TOUCHED":          sorted(doms_tocados),
        "MAX_REQUESTS_ONE_DOMAIN":  orcam.max_num_dominio(),
        "CANDIDATOS_REGISTADOS":    registados,
        "LOG":                      log,
    }

    fd, tmp = tempfile.mkstemp(dir=str(PROOF_JSON.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(prova, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, PROOF_JSON)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)

    return prova


_FAMILIAS = [
    ("CANAIS_SOCIAIS",        ("youtube.com", "linkedin.com", "instagram.com", "facebook.com")),
    ("CNR",                   ("cnr.it",)),
    ("CREA",                  ("crea.gov.it",)),
    ("IZS",                   ("izs",)),
    ("ORDINI_COLLEGI",        ("conaf.it", "peritiagrari", "agrotecnici")),
    ("ACCADEMIE",             ("georgofili",)),
    ("SOCIETA_SCIENTIFICHE",  ("aissa.it", "sipav", "soihs", "sigaweb", "agronomia.it")),
    ("RIVISTE_SCIENTIFICHE",  ("pagepress", "agrochimica", "fupress", "bulletinofinsectology")),
    ("RIVISTE_TECNICHE",      ("terraevita", "informatoreagrario", "agronotizie")),
    ("FONDAZIONI_ENTI",       ("fmach.it", "laimburg", "enea.it", "isprambiente")),
    ("UNIVERSITA",            ("uni", "santanna", "cattolica")),
]


def familia_de(url: str) -> str:
    u = url.lower()
    for fam, chaves in _FAMILIAS:
        if any(k in u for k in chaves):
            return fam
    return "OUTRA"


def escrever_lista() -> dict:
    """Lista cumulativa desta missao, lida da fila (nao da ultima corrida)."""
    cands = [c for c in carregar()["CANDIDATAS"]
             if "MISSAO=PESQUISADORES" in c.get("NOTA", "")]
    por_familia: dict[str, int] = {}
    linhas = []
    for c in sorted(cands, key=lambda c: c["CANDIDATA_ID"]):
        fam = familia_de(c["URL"])
        por_familia[fam] = por_familia.get(fam, 0) + 1
        linhas.append({"CANDIDATA_ID": c["CANDIDATA_ID"], "FAMILIA": fam,
                       "TIPO": c["TIPO"], "PAIS": c["PAIS"], "NOME": c["NOME"],
                       "URL": c["URL"], "ESTADO": c["ESTADO"]})
    lista = {"DATASET": "PESQUISADORES-LISTA-V1",
             "GERADO_EM": datetime.now(timezone.utc).isoformat(),
             "CANDIDATAS_NOVAS": len(linhas),
             "POR_FAMILIA": dict(sorted(por_familia.items())),
             "CANDIDATAS": linhas}
    fd, tmp = tempfile.mkstemp(dir=str(LISTA_JSON.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(lista, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, LISTA_JSON)
    return lista


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Discovery focada em pesquisadores/CIENCIA para IT.")
    ap.add_argument("--orcamento", type=int, default=200)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--lista", action="store_true",
                    help="so escreve PESQUISADORES-LISTA-V1.json, sem rede")
    a = ap.parse_args()

    if a.lista:
        l = escrever_lista()
        print("CANDIDATAS_NOVAS", l["CANDIDATAS_NOVAS"], l["POR_FAMILIA"])
        return 0

    if a.listar:
        for c in CATALOGO_PESQUISADORES:
            print("  [%s] %s" % (c["tipo"], c["url"]))
        print("Total no catalogo:", len(CATALOGO_PESQUISADORES))
        return 0

    r = descobrir_pesquisadores(orcamento=a.orcamento)

    print("CORRIDA_EM          %s" % r["CORRIDA_EM"])
    print("DISCOVERED_TOTAL    %d" % r["DISCOVERED_TOTAL"])
    print("NOVEL_CANDIDATES    %d" % r["NOVEL_CANDIDATES"])
    print("DUPLICATES_REJECTED %d" % r["DUPLICATES_REJECTED"])
    print("ROBOTS_BLOCKS       %d" % r["ROBOTS_BLOCKS"])
    print("FAILED_HTTP         %d" % r["FAILED_HTTP"])
    print("REQUESTS_MADE       %d" % r["REQUESTS_MADE"])
    print()
    print("Candidatos registados:")
    for c in r["CANDIDATOS_REGISTADOS"]:
        print("  [%s] %s  %s" % (c["tipo"], c["id"], c["nome"][:60]))
    print()
    print("PROOF ->", PROOF_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
