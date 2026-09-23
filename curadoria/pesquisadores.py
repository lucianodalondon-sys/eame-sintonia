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
    fam_p1b = {}
    for prova in sorted(PROOF_P1B.parent.glob("PESQUISADORES-P1B-*PROOF-V1.json")):
        for e in json.loads(prova.read_text(encoding="utf-8"))["LOG"]:
            fam_p1b[normalizar(e["url"])] = e["familia"]
    for c in sorted(cands, key=lambda c: c["CANDIDATA_ID"]):
        fam = fam_p1b.get(normalizar(c["URL"])) or familia_de(c["URL"])
        if c["ESTADO"] != "RECUSADA":
            por_familia[fam] = por_familia.get(fam, 0) + 1
        linhas.append({"CANDIDATA_ID": c["CANDIDATA_ID"], "FAMILIA": fam,
                       "TIPO": c["TIPO"], "PAIS": c["PAIS"], "NOME": c["NOME"],
                       "URL": c["URL"], "ESTADO": c["ESTADO"]})
    lista = {"DATASET": "PESQUISADORES-LISTA-V1",
             "GERADO_EM": datetime.now(timezone.utc).isoformat(),
             "CANDIDATAS_NOVAS": sum(por_familia.values()),
             "RECUSADAS_DEPOIS_DE_REGISTADAS": sum(1 for x in linhas if x["ESTADO"] == "RECUSADA"),
             "POR_FAMILIA": dict(sorted(por_familia.items())),
             "CANDIDATAS": linhas}
    fd, tmp = tempfile.mkstemp(dir=str(LISTA_JSON.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(lista, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, LISTA_JSON)
    return lista


# ---------------------------------------------------------------------------
# FASE P1b — reler recusas, achar enderecos novos, IZS, Veterinaria, Ordini
# ---------------------------------------------------------------------------
import subprocess                                        # noqa: E402
import time                                              # noqa: E402
import urllib.error                                      # noqa: E402
import urllib.parse                                      # noqa: E402
import urllib.request                                    # noqa: E402
import urllib.robotparser                                # noqa: E402
from collections import Counter                          # noqa: E402

sys.path.insert(0, str(RAIZ / "superficie"))
import rede as R                                         # noqa: E402

PROOF_P1B = RAIZ / "curadoria" / "PESQUISADORES-P1B-PROOF-V1.json"
VIGIA_A_CADA = 10
_RELER_MOTIVOS = ("ROBOTS_BLOCKED", "HTTP_0")
# So a pagina de listagem: o caminho TERMINA na palavra (nao artigo, PDF ou aviso).
_SUB_RE = re.compile(r"/(notizie|news|comunicati|comunicati-stampa|pubblicazioni|"
                     r"eventi|ufficio-stampa|stampa)/?$", re.I)


class VigiaParou(RuntimeError):
    pass


def vigia() -> str:
    """Mede a saida. UNKNOWN repete uma vez (o checker tropeca); o resto para."""
    for tentativa in (1, 2):
        e = R.portao_de_egresso("IT")
        if e["EGRESS_GATE"] == "PASS":
            return "PASS"
        if tentativa == 1:
            time.sleep(5)
    raise VigiaParou("EGRESS=%s" % e["EGRESS_COUNTRY_CODE"])


def conhecidos_da_p2() -> set[str]:
    """URLs que a missao P2 ja registou noutra branch — nao duplicar."""
    try:
        bruto = subprocess.run(
            ["git", "show", "pesquisa-projetos-v1:candidatas/FONTES-CANDIDATAS.json"],
            cwd=str(RAIZ), capture_output=True, check=True).stdout
        return {normalizar(c["URL"]) for c in json.loads(bruto)["CANDIDATAS"]}
    except Exception:
        return set()


_diag: dict[str, tuple[str, urllib.robotparser.RobotFileParser]] = {}


def diagnosticar_robots(host: str, orcam) -> tuple[str, urllib.robotparser.RobotFileParser]:
    """Le o robots.txt de novo e diz PORQUE: 200, AUSENTE ou ILEGIVEL_<codigo>.

    ILEGIVEL continua a fechar a porta (prudencia) — so deixa de se chamar
    «proibido», porque nao e isso que foi medido.
    """
    if host in _diag:
        return _diag[host]
    url = "https://%s/robots.txt" % host
    rp = urllib.robotparser.RobotFileParser()
    ok, _ = orcam.pode(url)
    if not ok:
        rp.parse(["User-agent: *", "Disallow: /"])
        _diag[host] = ("ILEGIVEL_ORCAMENTO", rp)
        return _diag[host]
    orcam.pausar(url)
    orcam.registar(url)
    req = urllib.request.Request(url, headers={"User-Agent": D.UA})
    try:
        with urllib.request.urlopen(req, timeout=D.TIMEOUT_S, context=D.CTX) as r:
            rp.parse(r.read().decode("utf-8", "replace").splitlines())
            classe = "ROBOTS_200"
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            rp.parse([])
            classe = "ROBOTS_AUSENTE"
        else:
            rp.parse(["User-agent: *", "Disallow: /"])
            classe = "ILEGIVEL_%d" % e.code
    except Exception as ex:
        rp.parse(["User-agent: *", "Disallow: /"])
        classe = "ILEGIVEL_%s" % type(ex).__name__
    _diag[host] = (classe, rp)
    return _diag[host]


def _host(url: str) -> str:
    return urllib.parse.urlsplit(url).netloc.lower()


def _porta_do_robots(url: str, orcam) -> tuple[bool, str]:
    classe, rp = diagnosticar_robots(_host(url), orcam)
    if classe.startswith("ILEGIVEL"):
        return False, "ROBOTS_" + classe
    if not rp.can_fetch(D.UA, url):
        return False, "ROBOTS_DISALLOW"
    return True, classe


def explorar(url: str, padrao: str = "", orcam=None) -> list[tuple[str, str]]:
    """Abre uma pagina oficial (hub) e devolve os links dela. Nao regista nada."""
    orcam = orcam or D.Orcamento(total=20)
    ok, porque = _porta_do_robots(url, orcam)
    if not ok:
        print("HUB FECHADO", porque, url)
        return []
    html, code, ct = D._buscar_pagina_html(url, orcam)
    if not html:
        print("HUB SEM HTML", code, ct, url)
        return []
    rx = re.compile(padrao, re.I) if padrao else None
    vistos, out = set(), []
    for u, a in D.extrair_links(html, url):
        u = u.split("#")[0]
        if u in vistos or not u.startswith("http"):
            continue
        if rx and not (rx.search(u) or rx.search(a)):
            continue
        vistos.add(u)
        out.append((u, a))
    return out


def _motivo_rejeitado(norm: str, visitados: dict):
    r = visitados.get("REJEITADOS", {}).get(norm)
    if r is None:
        return None
    return r if isinstance(r, str) else str(r.get("MOTIVO", r))


def _registar_p1b(cand: dict, http: int, prova: str) -> dict:
    nota = ("DISCOVERED_FROM=%s | DISCOVERY_METHOD=%s | DISCOVERED_AT=%s"
            " | DISCOVERED_HTTP=%d | PROVA=%s | MISSAO=PESQUISADORES-P1B"
            % (cand["discovered_from"], cand["method"],
               datetime.now(timezone.utc).isoformat(), http, prova))
    return registar(tipo=cand["tipo"], pais=cand["pais"], nome=cand["nome"],
                    url=cand["url"], para_que=cand["para_que"],
                    quem_viu="curadoria/pesquisadores.py (P1b)",
                    onde_viu=cand["discovered_from"], nota=nota)


def tentar(cand: dict, orcam, ctx: dict, sub: bool = False) -> None:
    url, norm = cand["url"], normalizar(cand["url"])
    log, visitados = ctx["log"], ctx["visitados"]
    fam = cand.get("familia") or familia_de(url)

    def anota(acao, **kw):
        log.append({"url": url, "familia": fam, "acao": acao, **kw})

    if norm in ctx["p2"]:
        return anota("DEDUP", motivo="NA_P2")
    if norm in ctx["conhecidos"]:
        return anota("DEDUP", motivo="SAME_URL")
    antes = _motivo_rejeitado(norm, visitados)
    if antes and not antes.startswith(_RELER_MOTIVOS):
        return anota("DEDUP", motivo="PREVIOUSLY_REJECTED:" + antes)

    ctx["n"] += 1
    if ctx["n"] % VIGIA_A_CADA == 0:
        ctx["vigias"].append(vigia())

    ok, porque = _porta_do_robots(url, orcam)
    if not ok:
        D._marcar_rejeitado(norm, porque, visitados)
        return anota("ROBOTS", motivo=porque, relido=bool(antes))

    html, code, ct = D._buscar_pagina_html(url, orcam)
    if not (200 <= code < 300):
        D._marcar_rejeitado(norm, "HTTP_%d" % code, visitados)
        return anota("FALHOU", http=code, relido=bool(antes))

    prova = cand.get("prova", "pagina oficial responde")
    if cand.get("titulo_re"):
        m = re.search(r"<title[^>]*>(.*?)</title>", html or "", re.S | re.I)
        titulo = " ".join((m.group(1) if m else "").split())[:120]
        if not re.search(cand["titulo_re"], titulo, re.I):
            D._marcar_rejeitado(norm, "IDENTIDADE_NAO_CONFIRMADA", visitados)
            return anota("SEM_IDENTIDADE", titulo=titulo, relido=bool(antes))
        prova += " | TITULO=%s" % titulo

    linha = _registar_p1b(cand, code, prova)
    D._marcar_visitado(norm, "REGISTADO_%s" % linha["CANDIDATA_ID"], visitados)
    ctx["conhecidos"].add(norm)
    anota("REGISTADO", id=linha["CANDIDATA_ID"], relido=bool(antes), robots=porque)

    if sub and html:
        host = _host(url)
        achados = []
        for u, a in D.extrair_links(html, url):
            u = u.split("#")[0].split("?")[0]
            p = urllib.parse.urlsplit(u)
            if p.netloc.lower() != host or not _SUB_RE.search(p.path):
                continue
            if p.path.rstrip("/").count("/") > 3:
                continue
            if normalizar(u) == norm or normalizar(u) in {normalizar(x) for x, _ in achados}:
                continue
            achados.append((u, a))
        for u, a in achados[:2]:
            tentar({**cand, "url": u, "familia": fam, "titulo_re": None,
                    "nome": "%s — %s" % (cand["nome"], (a or urllib.parse.urlsplit(u).path)[:50]),
                    "para_que": "pagina de noticias/publicacoes de: " + cand["para_que"],
                    "discovered_from": url, "method": "link_da_home_oficial",
                    "prova": "ligada pela home oficial %s (texto: %s)" % (url, (a or "")[:60])},
                   orcam, ctx, sub=False)


def correr_p1b(catalogo: list, orcamento: int = 380) -> dict:
    ctx = {"log": [], "visitados": D._ler_visitados(), "conhecidos": D._construir_set_conhecido(),
           "p2": conhecidos_da_p2(), "n": 0, "vigias": [vigia()]}
    orcam = D.Orcamento(total=orcamento)
    inicio = datetime.now(timezone.utc).isoformat()
    parou = None
    try:
        for cand in catalogo:
            tentar(cand, orcam, ctx, sub=cand.get("sub", False))
            time.sleep(cand.get("pausa", 1))
        ctx["vigias"].append(vigia())
    except VigiaParou as ex:
        parou = str(ex)
    finally:
        D._gravar_visitados(ctx["visitados"])
    log = ctx["log"]
    por_fam: dict = {}
    for e in log:
        if e["acao"] == "REGISTADO":
            por_fam[e["familia"]] = por_fam.get(e["familia"], 0) + 1
    prova = {"DATASET": "PESQUISADORES-P1B-PROOF-V1", "CORRIDA_EM": inicio,
             "VIGIA_PAROU": parou, "VIGIAS": ctx["vigias"],
             "CANDIDATAS_NOVAS": sum(por_fam.values()),
             "POR_FAMILIA": dict(sorted(por_fam.items())),
             "ACOES": dict(Counter(e["acao"] for e in log)),
             "DUPLICADAS_EVITADAS": sum(1 for e in log if e["acao"] == "DEDUP"),
             "PEDIDOS_DE_REDE": orcam.pedidos_feitos,
             "MAX_PEDIDOS_UM_DOMINIO": orcam.max_num_dominio(),
             "ROBOTS_POR_HOST": {h: c for h, (c, _) in sorted(_diag.items())},
             "LOG": log}
    fd, tmp = tempfile.mkstemp(dir=str(PROOF_P1B.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(prova, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, PROOF_P1B)
    return prova


# ---------------------------------------------------------------------------
# Catalogo P1b — so enderecos medidos em 23/09: link de pagina oficial
# explorada (discovered_from) ou nome que resolve no DNS + titulo confirmado.
# ---------------------------------------------------------------------------
CONAF_LINKS = RAIZ / "curadoria" / "PESQUISADORES-P1B-CONAF-LINKS.json"
_CREA_HUB = "https://www.crea.gov.it/centri-di-ricerca"
_T_IZS = r"zooprofilattic|IZS"
_T_VET = r"veterinar|animal"
_T_ORD = r"agronom|forestal|ordine|federazion|dottori"


def _c(familia, tipo, nome, url, para_que, de, **kw):
    return {"familia": familia, "tipo": tipo, "pais": "IT", "nome": nome, "url": url,
            "para_que": para_que, "discovered_from": de,
            "method": kw.pop("method", "link_de_pagina_oficial"), **kw}


def _crea(slug, nome):
    return _c("CREA", "CIENCIA", "CREA — Centro " + nome,
              "https://www.crea.gov.it/web/" + slug,
              "centro di ricerca CREA: notizie, progetti e pubblicazioni", _CREA_HUB,
              prova="listado na pagina oficial Centri di ricerca do CREA")


def _dns(familia, tipo, nome, url, para_que, titulo_re, sub=True):
    return _c(familia, tipo, nome, url, para_que, url, method="dns_e_titulo",
              titulo_re=titulo_re, sub=sub,
              prova="nome resolve no DNS (medido 23/09) e a propria home responde")


CATALOGO_P1B: list[dict] = [
    # CREA — os 12 centros vivem em /web/<centro>; 4 ja estao na fila sem /web/
    _crea("agricoltura-e-ambiente", "Agricoltura e Ambiente"),
    _crea("alimenti-e-nutrizione", "Alimenti e Nutrizione"),
    _crea("foreste-e-legno", "Foreste e Legno"),
    _crea("genomica-e-bioinformatica", "Genomica e Bioinformatica"),
    _crea("ingegneria-e-trasformazioni-agroalimentari", "Ingegneria e Trasformazioni Agroalimentari"),
    _crea("olivicoltura-frutticoltura-e-agrumicoltura", "Olivicoltura, Frutticoltura e Agrumicoltura"),
    _crea("politiche-e-bioeconomia", "Politiche e Bioeconomia"),
    _crea("zootecnia-e-acquacoltura", "Zootecnia e Acquacoltura"),
    _c("CREA", "CIENCIA", "CREA — Notizie", "https://www.crea.gov.it/notizie",
       "notizie ufficiali della ricerca CREA", _CREA_HUB),
    _c("CREA", "CIENCIA", "CREA — Comunicati Stampa", "https://www.crea.gov.it/comunicati-stampa",
       "comunicati stampa CREA su risultati di ricerca", _CREA_HUB),
    _c("CREA", "CIENCIA", "CREA — Eventi", "https://www.crea.gov.it/eventi-crea",
       "convegni e giornate tecniche CREA", _CREA_HUB),
    _c("CREA", "CIENCIA", "CREA — Riviste del CREA", "https://www.crea.gov.it/riviste-del-crea",
       "riviste scientifiche e tecniche edite dal CREA", _CREA_HUB),
    _c("CREA", "CIENCIA", "CREA — Open Access", "https://www.crea.gov.it/open-access",
       "pubblicazioni ad accesso aperto dei ricercatori CREA", _CREA_HUB),
    _c("CREA", "CIENCIA", "CREA — Schede tecniche", "https://www.crea.gov.it/schede-tecniche",
       "schede tecniche CREA per colture e difesa", _CREA_HUB),

    # ENEA / ISPRA — enderecos novos no lugar dos 404
    _c("FONDAZIONI_ENTI", "CIENCIA", "ENEA — Dipartimento Sostenibilita (SSPT)",
       "https://sostenibilita.enea.it/", "ricerca ENEA su agroalimentare, bioeconomia e sostenibilita",
       "https://www.enea.it/it", sub=True, titulo_re=r"sostenib|ENEA"),
    _c("FONDAZIONI_ENTI", "CIENCIA", "ISPRA — Geologia, suolo e siti contaminati",
       "https://www.isprambiente.gov.it/it/attivita/suolo-e-territorio",
       "consumo di suolo, erosione e qualita dei suoli agricoli", "https://www.isprambiente.gov.it/it"),
    _c("FONDAZIONI_ENTI", "CIENCIA", "ISPRA — Biodiversita",
       "https://www.isprambiente.gov.it/it/attivita/biodiversita",
       "biodiversita, specie aliene e impollinatori", "https://www.isprambiente.gov.it/it"),
    _c("FONDAZIONI_ENTI", "CIENCIA", "ISPRA — Pubblicazioni",
       "https://www.isprambiente.gov.it/it/pubblicazioni",
       "rapporti ISPRA (suolo, fitofarmaci nelle acque, clima)", "https://www.isprambiente.gov.it/it"),

    # IZS — os 10 institutos; IZSVe ja esta na fila
    _dns("IZS", "CIENCIA", "IZSAM — Istituto Zooprofilattico Abruzzo e Molise", "https://www.izs.it/",
         "sanita animale, zoonosi e sicurezza alimentare Abruzzo-Molise", _T_IZS),
    _dns("IZS", "CIENCIA", "IZSLER — Istituto Zooprofilattico Lombardia ed Emilia-Romagna", "https://www.izsler.it/",
         "sanita animale e sicurezza alimentare Lombardia-Emilia-Romagna", _T_IZS),
    _dns("IZS", "CIENCIA", "IZSUM — Istituto Zooprofilattico Umbria e Marche", "https://www.izsum.it/",
         "sanita animale e sicurezza alimentare Umbria-Marche", _T_IZS),
    _dns("IZS", "CIENCIA", "IZSLT — Istituto Zooprofilattico Lazio e Toscana", "https://www.izslt.it/",
         "sanita animale e sicurezza alimentare Lazio-Toscana", _T_IZS),
    _dns("IZS", "CIENCIA", "IZSM — Istituto Zooprofilattico del Mezzogiorno", "https://www.izsmportici.it/",
         "sanita animale e sicurezza alimentare Campania-Calabria", _T_IZS),
    _dns("IZS", "CIENCIA", "IZSPB — Istituto Zooprofilattico Puglia e Basilicata", "https://www.izspb.it/",
         "sanita animale e sicurezza alimentare Puglia-Basilicata", _T_IZS),
    _dns("IZS", "CIENCIA", "IZSSi — Istituto Zooprofilattico della Sicilia", "https://www.izssicilia.it/",
         "sanita animale e sicurezza alimentare Sicilia", _T_IZS),
    _dns("IZS", "CIENCIA", "IZSSa — Istituto Zooprofilattico della Sardegna", "https://www.izs-sardegna.it/",
         "sanita animale e sicurezza alimentare Sardegna", _T_IZS),
    _dns("IZS", "CIENCIA", "IZSPLV — Istituto Zooprofilattico Piemonte, Liguria e Valle d'Aosta", "https://izsto.it/",
         "sanita animale e sicurezza alimentare Piemonte-Liguria-VdA", _T_IZS),

    # Veterinaria
    _dns("VETERINARIA", "CIENCIA", "MAPS — Medicina Animale, Produzioni e Salute, Univ. Padova",
         "https://www.maps.unipd.it/", "ricerca veterinaria e produzioni animali Padova", _T_VET),
    _dns("VETERINARIA", "CIENCIA", "BCA — Biomedicina Comparata e Alimentazione, Univ. Padova",
         "https://www.bca.unipd.it/", "ricerca veterinaria e alimentazione animale Padova", _T_VET + r"|alimentaz|biomedicin"),
    _dns("VETERINARIA", "CIENCIA", "DIVAS — Medicina Veterinaria e Scienze Animali, Univ. Milano",
         "https://www.divas.unimi.it/", "ricerca veterinaria e zootecnia Milano", _T_VET),
    _dns("VETERINARIA", "CIENCIA", "VESPA — Scienze Veterinarie per la Salute e la Produzione Animale, Univ. Milano",
         "https://www.vespa.unimi.it/", "salute animale e sicurezza alimentare Milano", _T_VET),
    _dns("VETERINARIA", "CIENCIA", "Dip. Scienze Veterinarie, Univ. Torino",
         "https://www.veterinaria.unito.it/", "ricerca veterinaria Torino", _T_VET),
    _dns("VETERINARIA", "CIENCIA", "DMVPA — Medicina Veterinaria e Produzioni Animali, Univ. Napoli Federico II",
         "https://www.mvpa.unina.it/", "ricerca veterinaria e produzioni animali Napoli", _T_VET),
    _dns("VETERINARIA", "CIENCIA", "Dip. Scienze Veterinarie, Univ. Pisa",
         "https://www.vet.unipi.it/", "ricerca veterinaria Pisa", _T_VET),
    _dns("VETERINARIA", "CIENCIA", "Dip. Scienze Medico-Veterinarie, Univ. Parma",
         "https://smv.unipr.it/", "ricerca veterinaria e sicurezza alimentare Parma", _T_VET),
    _c("VETERINARIA", "CIENCIA", "Dip. Medicina Veterinaria, Univ. Teramo",
       "https://www.unite.it/UniTE/Dipartimenti_HP/Medicina_veterinaria",
       "ricerca veterinaria Teramo", "https://www.unite.it/"),

    # Universita agraria — enderecos certos no lugar dos que nao resolviam
    _c("UNIVERSITA", "CIENCIA", "DI4A — Scienze AgroAlimentari, Ambientali e Animali, Univ. Udine",
       "https://di4a.uniud.it/", "ricerca agroalimentare e zootecnica Friuli", "https://www.uniud.it/it",
       sub=True, titulo_re=r"DI4A|agro|alimentar"),
    _dns("UNIVERSITA", "CIENCIA", "DSA3 — Scienze Agrarie, Alimentari e Ambientali, Univ. Perugia",
         "https://dsa3.unipg.it/", "ricerca agraria Umbria", r"agrari|alimentar|ambient|DSA3"),
    _c("UNIVERSITA", "CIENCIA", "Dip. Bioscienze e Tecnologie Agro-alimentari e Ambientali, Univ. Teramo",
       "https://www.unite.it/UniTE/Dipartimenti_HP/Bioscienze_e_tecnologie_agro-alimentari_e_ambientali",
       "ricerca agroalimentare Teramo", "https://www.unite.it/"),
    _c("UNIVERSITA", "CIENCIA", "Dip. Scienze Agrarie, Alimentari e Agro-ambientali, Univ. Pisa",
       "https://www.agr.unipi.it/", "ricerca agraria Pisa (relida: antes HTTP_0)", "https://www.agr.unipi.it/", sub=True),
    _c("UNIVERSITA", "CIENCIA", "DiSSPA — Scienze del Suolo, della Pianta e degli Alimenti, Univ. Bari",
       "https://www.uniba.it/ricerca/dipartimenti/disspa", "ricerca agraria Puglia (relida: antes HTTP_0)",
       "https://www.uniba.it/"),

    # Societa scientifiche e riviste
    _dns("SOCIETA_SCIENTIFICHE", "CIENCIA", "SIGA — Societa Italiana di Genetica Agraria",
         "https://www.geneticagraria.it/", "genetica agraria: congressi e notizie", r"genetica|SIGA"),
    _dns("SOCIETA_SCIENTIFICHE", "CIENCIA", "SIA — Societa Italiana di Agronomia",
         "https://www.siagr.it/", "agronomia: congressi, rivista IJA e notizie", r"agronom|SIA"),
    _dns("SOCIETA_SCIENTIFICHE", "CIENCIA", "AIVI — Associazione Italiana Veterinari Igienisti",
         "https://www.aivi.it/", "igiene degli alimenti di origine animale", r"AIVI|veterinar|igien"),
    _dns("SOCIETA_SCIENTIFICHE", "CIENCIA", "Societa Entomologica Italiana",
         "https://www.societaentomologicaitaliana.it/", "entomologia agraria: bollettino e notizie", r"entomolog"),
    _dns("SOCIETA_SCIENTIFICHE", "CIENCIA", "AIAM — Associazione Italiana di AgroMeteorologia",
         "https://www.aiam.info/", "agrometeorologia: rivista e convegni", r"agrometeo|AIAM"),
    _dns("SOCIETA_SCIENTIFICHE", "CIENCIA", "SIDEA — Societa Italiana di Economia Agraria",
         "https://www.sidea.org/", "economia agraria: convegni e pubblicazioni", r"economia|SIDEA"),
    _dns("SOCIETA_SCIENTIFICHE", "CIENCIA", "AIIA — Associazione Italiana di Ingegneria Agraria",
         "https://www.aiia.it/", "meccanizzazione e ingegneria agraria", r"ingegneria|AIIA"),
    _c("SOCIETA_SCIENTIFICHE", "CIENCIA", "SOI — Societa di Orticoltura Italiana",
       "https://www.soihs.it/", "orticoltura: convegni e notizie (relida: robots ausente)",
       "https://www.soihs.it/", sub=True),
    _c("RIVISTE_SCIENTIFICHE", "CIENCIA", "Italus Hortus — rivista SOI", "https://www.soihs.it/italus-hortus/",
       "rivista di orticoltura (relida: robots ausente)", "https://www.soihs.it/"),
    _c("RIVISTE_SCIENTIFICHE", "CIENCIA", "Journal of Entomological and Acarological Research — PAGEPress",
       "https://www.pagepressjournals.org/jear", "rivista open di entomologia e acarologia",
       "https://www.pagepressjournals.org/"),
    _c("RIVISTE_SCIENTIFICHE", "CIENCIA", "AF — L'Agronomo Forestale (rivista CONAF)",
       "https://www.agronomoforestale.eu/", "rivista professionale degli agronomi e forestali",
       "https://www.conaf.it/ordini-provinciali", titulo_re=r"agronom|forestal|AF"),

    # Ordini e Collegi (paginas nacionais)
    _c("ORDINI_COLLEGI", "ORGANIZACAO", "CONAF — Comunicati stampa",
       "https://www.conaf.it/newsinhome/conaf-news/", "comunicati stampa del Consiglio nazionale agronomi",
       "https://www.conaf.it/ordini-provinciali"),
    _c("ORDINI_COLLEGI", "ORGANIZACAO", "CONAF — Rivista", "https://www.conaf.it/newsinhome/rivista/",
       "rivista e pubblicazioni CONAF", "https://www.conaf.it/ordini-provinciali"),
    _c("ORDINI_COLLEGI", "ORGANIZACAO", "CONAF — Centro Studi", "https://www.conaf.it/uffici/centro-studi/",
       "studi e ricerche del Centro Studi CONAF", "https://www.conaf.it/ordini-provinciali"),
    _c("ORDINI_COLLEGI", "ORGANIZACAO", "Periti Agrari — Notizie dal Collegio Nazionale",
       "https://www.peritiagrari.it/area-comunicazione.html", "notizie tecniche dei periti agrari",
       "https://www.peritiagrari.it/"),
    _c("ORDINI_COLLEGI", "ORGANIZACAO", "Periti Agrari — Notizie dai Territoriali",
       "https://www.peritiagrari.it/area-comunicazione/notizie-dai-territoriali.html",
       "notizie dei collegi provinciali dei periti agrari", "https://www.peritiagrari.it/"),
    _c("ORDINI_COLLEGI", "ORGANIZACAO", "Periti Agrari — Comunicati Stampa",
       "https://www.peritiagrari.it/area-comunicazione/comunicati-stampa.html",
       "comunicati stampa del Collegio nazionale periti agrari", "https://www.peritiagrari.it/territoriali.html"),
    _c("ORDINI_COLLEGI", "ORGANIZACAO", "Collegio Nazionale Agrotecnici e Agrotecnici Laureati",
       "https://www.agrotecnici.it/", "agrotecnici: notizie professionali (relida: robots ausente)",
       "https://www.agrotecnici.it/", sub=True, titulo_re=r"agrotecnic"),

    # Riviste tecniche
    _c("RIVISTE_TECNICHE", "IMPRENSA", "L'Informatore Agrario", "https://www.informatoreagrario.it/",
       "rivista tecnica degli agronomi (relida: robots permite a home)",
       "https://www.informatoreagrario.it/", sub=True),
]

# Externos listados pelo CONAF so quando a ordem nao tem subdominio conaf.it proprio.
_ORDINI_EXTERNOS = {
    "www.odafrieti.it", "agronomicatanzaro.it", "www.agronomiforestali.it", "www.agronomi-fg.it",
    "www.agronomiforestali-novara-vco.it",
}
_RER = ("ordine-di-ferrara", "ordine-di-forli-cesena-rimini", "ordine-di-modena",
        "ordine-di-parma", "ordine-di-piacenza")


def ordini_do_conaf() -> list[dict]:
    """Uma entrada por ordem/federacao, escolhida dos links que o CONAF publica."""
    achados = json.loads(CONAF_LINKS.read_text(encoding="utf-8"))
    escolhidos: dict[str, dict] = {}
    for a in achados:
        u = a["url"].rstrip("/")
        host = urllib.parse.urlsplit(u).netloc.lower()
        regiao = a["regiao"].replace("ordini-afferenti-federazione-", "").replace(
            "ordine-regionale-", "").replace("federazione-", "")
        if host.startswith("old") or host == "ordinefvg.conaf.it":
            continue
        if host.endswith(".conaf.it"):
            chave = host[:-len(".conaf.it")]
            chave = chave[3:] if chave.startswith("new") else chave
        elif host in _ORDINI_EXTERNOS:
            chave = host
        elif host == "www.agronomiforestali-rer.it" and u.rsplit("/", 1)[-1] in _RER:
            chave = u.rsplit("/", 1)[-1]
        else:
            continue
        atual = escolhidos.get(chave)
        if atual and not (u.startswith("https") and not atual["url"].startswith("https")):
            continue
        rotulo = (chave.replace("-", " ") if chave.startswith("ordine-di") else
                  chave.replace("ordine", "ordine ").replace("federazione", "federazione ").replace("fodaf", "federazione "))
        escolhidos[chave] = _c(
            "ORDINI_COLLEGI", "ORGANIZACAO",
            "Dottori Agronomi e Forestali — %s (%s)" % (rotulo.strip(), regiao),
            u + ("/" if urllib.parse.urlsplit(u).path == "" else ""),
            "ordine territoriale agronomi e forestali (%s): notizie, eventi e formazione" % regiao,
            a["hub"], titulo_re=_T_ORD, pausa=3,
            prova="listado pela pagina oficial CONAF da regiao %s" % regiao)
    return list(escolhidos.values())


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Discovery focada em pesquisadores/CIENCIA para IT.")
    ap.add_argument("--orcamento", type=int, default=200)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--p1b", action="store_true",
                    help="fase P1b: releitura, IZS, Veterinaria, Ordini (rede, VPN IT)")
    ap.add_argument("--lista", action="store_true",
                    help="so escreve PESQUISADORES-LISTA-V1.json, sem rede")
    a = ap.parse_args()

    if a.p1b:
        r = correr_p1b(CATALOGO_P1B + ordini_do_conaf(), orcamento=a.orcamento)
        l = escrever_lista()
        for k in ("CANDIDATAS_NOVAS", "POR_FAMILIA", "ACOES", "DUPLICADAS_EVITADAS",
                  "PEDIDOS_DE_REDE", "MAX_PEDIDOS_UM_DOMINIO", "VIGIA_PAROU", "VIGIAS"):
            print(k, r[k])
        print("LISTA_CUMULATIVA", l["CANDIDATAS_NOVAS"], l["POR_FAMILIA"])
        return 0

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
