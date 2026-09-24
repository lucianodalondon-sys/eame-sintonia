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
    for prova in sorted(PROOF_P1B.parent.glob("PESQUISADORES-P1[BCDE]-*PROOF-V1.json")):
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
_RELER_MOTIVOS = ("ROBOTS_BLOCKED", "HTTP_0", "ROBOTS_ILEGIVEL_URLError")
# So a pagina de listagem: o caminho TERMINA na palavra (nao artigo, PDF ou aviso).
_SUB_RE = re.compile(r"/(notizie|news|comunicati|comunicati-stampa|pubblicazioni|"
                     r"eventi|ufficio-stampa|stampa|bollettini|bollettino|"
                     r"bollettini-fitosanitari|avvisi-fitosanitari|agrometeo)/?$", re.I)


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

    if fora_do_foco({**cand, "familia": fam}):
        return anota("FORA_DO_FOCO", motivo="decisao do dono 23/09: veterinaria/IZS")
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
    if cand.get("corpo_re"):
        if not re.search(cand["corpo_re"], html or "", re.I):
            D._marcar_rejeitado(norm, "IDENTIDADE_NAO_CONFIRMADA", visitados)
            return anota("SEM_IDENTIDADE", corpo=cand["corpo_re"], relido=bool(antes))
        prova += " | TEXTO_DA_PAGINA_CONTEM=%s" % cand["corpo_re"]

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


def correr_p1b(catalogo: list, orcamento: int = 380, prova_path=None, por_dominio: int = 8) -> dict:
    ctx = {"log": [], "visitados": D._ler_visitados(), "conhecidos": D._construir_set_conhecido(),
           "p2": conhecidos_da_p2() | conhecidos_das_lanes(), "n": 0, "vigias": [vigia()]}
    orcam = D.Orcamento(total=orcamento, por_dominio=por_dominio)
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
    destino = prova_path or PROOF_P1B
    fd, tmp = tempfile.mkstemp(dir=str(destino.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(prova, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, destino)
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


# ---------------------------------------------------------------------------
# Catalogo P1c — 3.a volta: todos os IZS, Veterinaria/Agraria que faltavam,
# servicos regionais (fitossanitario + agrometeo), revistas com endereco novo.
# ---------------------------------------------------------------------------
SFR_LINKS = RAIZ / "curadoria" / "PESQUISADORES-P1C-SFR-LINKS.json"
PROOF_P1C = RAIZ / "curadoria" / "PESQUISADORES-P1C-PROOF-V1.json"
_SFN = "https://www.protezionedellepiante.it/servizi-fitosanitari-regionali/"
_T_SERV = r"fitosanit|agrometeo|meteo|agricolt|agroalim|rurale|difesa|ARPA|ERSA|ERSAF|ASSAM|SIAS|ARSAC|LAORE|ALSIA|SIARL|LaMMA"


def sfr_regionais() -> list[dict]:
    """Os 21 servicos fitossanitarios regionais que o SFN publica no mapa."""
    out = []
    for a in json.loads(SFR_LINKS.read_text(encoding="utf-8")):
        u = a["url"]
        if "?jjj=" in u:
            u = u.split("?jjj=")[0]
        out.append(_c("SERVIZI_TECNICI", "BASE_OFICIAL",
                      "Servizio Fitosanitario Regionale — %s" % a["regiao"], u,
                      "bollettini e avvisi fitosanitari, difesa integrata (%s)" % a["regiao"],
                      a["hub"], sub=True,
                      prova="listado no mapa oficial dos SFR do Servizio Fitosanitario Nazionale"))
    return out


def _serv(nome, url, para_que, titulo_re=_T_SERV):
    return _dns("SERVIZI_TECNICI", "BASE_OFICIAL", nome, url, para_que, titulo_re, sub=True)


CATALOGO_P1C: list[dict] = [
    _c("SERVIZI_TECNICI", "BASE_OFICIAL", "Servizio Fitosanitario Nazionale",
       "https://www.protezionedellepiante.it/", "emergenze, ordinanze e notizie fitosanitarie nazionali",
       "https://www.protezionedellepiante.it/", sub=True),
    _c("SERVIZI_TECNICI", "BASE_OFICIAL", "SFN — Emergenze fitosanitarie",
       "https://www.protezionedellepiante.it/emergenze-fitosanitarie/",
       "organismi nocivi da quarantena e misure d'emergenza", "https://www.protezionedellepiante.it/"),
    _c("SERVIZI_TECNICI", "BASE_OFICIAL", "Regione Abruzzo — Agrometeorologia e Agroambiente",
       "https://www.regione.abruzzo.it/content/agrometeorologia-agroambiente-0",
       "bollettini agrometeo e difesa integrata Abruzzo", "https://www.regione.abruzzo.it/agricoltura", sub=True),

    # agrometeo / assistenza tecnica regionale (DNS + titulo)
    _serv("Agrometeo Puglia", "https://www.agrometeopuglia.it/", "bollettini agrometeorologici Puglia"),
    _serv("Meteotrentino", "https://www.meteotrentino.it/", "meteo e agrometeo Trentino"),
    _serv("Meteo Provincia di Bolzano", "https://meteo.provincia.bz.it/", "meteo e agrometeo Alto Adige", r"meteo|wetter"),
    _serv("OSMER FVG — Osservatorio meteorologico", "https://www.osmer.fvg.it/", "meteo e agrometeo Friuli Venezia Giulia", r"osmer|meteo"),
    _serv("ASSAM Marche — Agenzia servizi settore agroalimentare", "https://www.assam.marche.it/", "agrometeo e assistenza tecnica Marche"),
    _serv("SIAS — Servizio Informativo Agrometeorologico Siciliano", "https://www.sias.regione.sicilia.it/", "agrometeo Sicilia"),
    _serv("LaMMA Toscana", "https://www.lamma.toscana.it/", "meteo e agrometeo Toscana", r"lamma|meteo"),
    _serv("SIARL Lazio — agrometeo", "https://www.siarl-lazio.it/", "agrometeo e assistenza tecnica Lazio"),
    _serv("ARSAC Calabria", "https://www.arsacweb.it/", "sviluppo agricolo e agrometeo Calabria"),
    _serv("ARPAS Sardegna — Meteo", "https://www.sar.sardegna.it/", "meteo e agrometeo Sardegna"),
    _serv("LAORE Sardegna — assistenza tecnica", "https://www.laore.it/", "assistenza tecnica agricola Sardegna"),
    _serv("Agriligurianet", "https://www.agriligurianet.it/", "agricoltura, assistenza tecnica e fitosanitario Liguria", r"agri|liguria"),
    _serv("ERSAF Lombardia", "https://www.ersaf.lombardia.it/", "servizi agricoli e forestali Lombardia"),
    _serv("ARSARP Molise", "https://www.arsarp.it/", "sviluppo agricolo e assistenza tecnica Molise", r"ARSARP|agricol|molise"),
    _serv("ARPAE Emilia-Romagna — SIMC", "https://simc.arpae.it/", "meteo e agrometeo Emilia-Romagna", r"arpae|meteo|simc|clima"),
    _serv("ARPAV Veneto", "https://www.arpa.veneto.it/", "agrometeo e bollettini Veneto", r"ARPAV|veneto|ambiente"),
    _serv("Regione Campania — Agricoltura", "https://agricoltura.regione.campania.it/", "agrometeo e difesa Campania", r"agricoltura|campania"),
    _serv("ALSIA Basilicata", "https://www.alsia.it/", "assistenza tecnica e agrometeo Basilicata", r"ALSIA|agricol|basilicata"),

    # IZS que faltavam (os 10)
    _dns("IZS", "CIENCIA", "IZSPB — Istituto Zooprofilattico Puglia e Basilicata", "https://www.izspb.it/",
         "sanita animale e sicurezza alimentare Puglia-Basilicata", _T_IZS),
    _dns("IZS", "CIENCIA", "IZSPLV — Istituto Zooprofilattico Piemonte, Liguria e Valle d'Aosta", "https://www.izsplv.it/",
         "sanita animale e sicurezza alimentare Piemonte-Liguria-VdA", _T_IZS),

    # Veterinaria e Agraria que faltavam (links de paginas oficiais das universidades)
    _c("VETERINARIA", "CIENCIA", "DIMEVET — Scienze Mediche Veterinarie, Univ. Bologna",
       "https://scienzemedicheveterinarie.unibo.it/it", "ricerca veterinaria Bologna",
       "https://www.unibo.it/it/ateneo/sedi-e-strutture/dipartimenti", sub=True, titulo_re=_T_VET),
    _c("VETERINARIA", "CIENCIA", "Dip. Medicina Veterinaria, Univ. Perugia", "http://www.medvet.unipg.it/",
       "ricerca veterinaria Umbria",
       "https://www.unipg.it/ateneo/organizzazione/dipartimenti?view=navigatorestrutture&struttura=517200",
       sub=True, titulo_re=_T_VET),
    _c("VETERINARIA", "CIENCIA", "Dip. Medicina Veterinaria, Univ. Sassari", "https://veterinaria.uniss.it/",
       "ricerca veterinaria Sardegna", "https://www.uniss.it/it/ateneo/strutture/dipartimenti", sub=True, titulo_re=_T_VET),
    _c("VETERINARIA", "CIENCIA", "Dip. Scienze Veterinarie, Univ. Messina", "https://vet.unime.it/",
       "ricerca veterinaria Sicilia", "https://www.unime.it/", sub=True, titulo_re=_T_VET),
    _c("VETERINARIA", "CIENCIA", "Scuola di Bioscienze e Medicina Veterinaria, Univ. Camerino", "https://sbmv.unicam.it/",
       "ricerca veterinaria e bioscienze Marche", "https://www.unicam.it/", sub=True, titulo_re=_T_VET + r"|bioscienz"),
    _c("VETERINARIA", "CIENCIA", "Dip. Medicina Veterinaria, Univ. Bari",
       "https://www.uniba.it/it/ricerca/dipartimenti/dipmedveterinaria", "ricerca veterinaria Puglia",
       "https://www.uniba.it/it/ricerca/dipartimenti"),
    _c("UNIVERSITA", "CIENCIA", "DiSSPA — Scienze del Suolo, della Pianta e degli Alimenti, Univ. Bari",
       "https://www.uniba.it/it/ricerca/dipartimenti/disspa", "ricerca agraria Puglia",
       "https://www.uniba.it/it/ricerca/dipartimenti"),
    _c("UNIVERSITA", "CIENCIA", "DISTAL — Scienze e Tecnologie Agro-Alimentari, Univ. Bologna",
       "https://distal.unibo.it/it", "ricerca agroalimentare Bologna",
       "https://www.unibo.it/it/ateneo/sedi-e-strutture/dipartimenti", sub=True, titulo_re=r"DISTAL|agro|alimentar"),
    _c("UNIVERSITA", "CIENCIA", "Dip. Agraria, Univ. Sassari", "http://agrariaweb.uniss.it/",
       "ricerca agraria Sardegna", "https://www.uniss.it/it/ateneo/strutture/dipartimenti", sub=True, titulo_re=r"agrar"),
    _c("UNIVERSITA", "CIENCIA", "Dip. Scienze Agrarie, Alimenti, Risorse Naturali e Ingegneria, Univ. Foggia",
       "https://www.agraria.unifg.it/it", "ricerca agraria Foggia", "https://www.unifg.it/",
       sub=True, titulo_re=r"agrar|alimenti|DAFNE"),
    _dns("UNIVERSITA", "CIENCIA", "D3A — Scienze Agrarie, Alimentari e Ambientali, Univ. Politecnica delle Marche",
         "https://www.d3a.univpm.it/", "ricerca agraria Marche", r"D3A|agrar|alimentar"),
    _c("UNIVERSITA", "CIENCIA", "D3A UNIVPM — Archivio News Dipartimento",
       "http://www.d3a.univpm.it/elenco-news-dipartimento", "notizie del dipartimento D3A",
       "https://www.d3a.univpm.it/"),
    _dns("UNIVERSITA", "CIENCIA", "TESAF — Territorio e Sistemi Agro-Forestali, Univ. Padova",
         "https://www.tesaf.unipd.it/", "ricerca agro-forestale Padova", r"TESAF|territorio|agro|forest"),
    _dns("UNIVERSITA", "CIENCIA", "DIBAF — Innovazione nei sistemi biologici, agroalimentari e forestali, Univ. Tuscia",
         "https://www.dibaf.unitus.it/", "ricerca agroalimentare e forestale Viterbo", r"DIBAF|biolog|agro|forest"),

    # Revistas — enderecos novos e a correcao da CAND-0488
    _c("RIVISTE_SCIENTIFICHE", "CIENCIA", "Italus Hortus — rivista SOI", "https://www.soihs.it/italushortus/default.aspx",
       "rivista scientifica di orticoltura", "https://www.soihs.it/"),
    _c("RIVISTE_SCIENTIFICHE", "CIENCIA", "Acta Italus Hortus — atti SOI", "https://www.soihs.it/acta/default.aspx",
       "atti dei convegni di orticoltura", "https://www.soihs.it/"),
    _c("RIVISTE_SCIENTIFICHE", "CIENCIA", "Italian Journal of Food Safety — PAGEPress",
       "https://www.pagepressjournals.org/ijfs", "rivista open di sicurezza alimentare e igiene veterinaria",
       "https://www.pagepressjournals.org/", titulo_re=r"Food Safety"),
    _dns("RIVISTE_SCIENTIFICHE", "CIENCIA", "Italian Journal of Food Science", "https://www.itjfs.com/",
         "rivista di scienze e tecnologie alimentari", r"Food Science", sub=False),
    _c("RIVISTE_SCIENTIFICHE", "CIENCIA", "Journal of Agricultural Engineering — PAGEPress",
       "https://www.pagepressjournals.org/jae", "rivista open di ingegneria agraria (AIIA)",
       "https://www.pagepressjournals.org/", titulo_re=r"Agricultural Engineering"),
    _c("RIVISTE_SCIENTIFICHE", "CIENCIA", "Italian Journal of Agronomy — PAGEPress",
       "https://www.pagepressjournals.org/ija", "rivista della Societa Italiana di Agronomia",
       "https://www.pagepressjournals.org/", titulo_re=r"Agronomy"),
    _c("RIVISTE_SCIENTIFICHE", "CIENCIA", "Italian Journal of Animal Science — Taylor & Francis",
       "https://www.tandfonline.com/journals/tjas20", "rivista open di zootecnia (ASPA)",
       "https://www.tandfonline.com/", titulo_re=r"Animal Science"),
]


# ---------------------------------------------------------------------------
# FORA DO FOCO — decisao do dono em 23/09 ~18:50: Veterinaria, IZS e fontes so
# de saude animal nao sao foco do Sintonia. Nada novo desse tipo entra; as ja
# registadas ficam listadas e so saem por fonte_nova.recusar, quando pedido.
# ---------------------------------------------------------------------------
FAMILIAS_FORA_DO_FOCO = {"VETERINARIA", "IZS"}
_FORA_DO_FOCO_RE = re.compile(r"veterinar|zooprofilattic|izs[a-z-]*\.it|aivi\.it", re.I)
FORA_DO_FOCO_JSON = RAIZ / "curadoria" / "PESQUISADORES-FORA-DO-FOCO-V1.json"
_FRONTEIRA = {"https://www.pagepressjournals.org/ijfs": "revista de seguranca alimentar, feita sobretudo por veterinarios",
              "https://www.crea.gov.it/web/zootecnia-e-acquacoltura": "producao animal, nao saude animal"}


def fora_do_foco(cand: dict) -> bool:
    return (cand.get("familia") in FAMILIAS_FORA_DO_FOCO
            or bool(_FORA_DO_FOCO_RE.search(cand["url"] + " " + cand.get("nome", ""))))


def listar_fora_do_foco(aplicar: bool = False) -> dict:
    """Lista as registadas fora do foco. Com aplicar=True recusa-as pela porta."""
    vivas, fronteira = [], []
    fam = {x["CANDIDATA_ID"]: x["FAMILIA"]
           for x in json.loads(LISTA_JSON.read_text(encoding="utf-8"))["CANDIDATAS"]}
    for c in carregar()["CANDIDATAS"]:
        if "MISSAO=PESQUISADORES" not in c.get("NOTA", "") or c["ESTADO"] == "RECUSADA":
            continue
        linha = {"CANDIDATA_ID": c["CANDIDATA_ID"], "URL": c["URL"], "NOME": c["NOME"]}
        if c["URL"] in _FRONTEIRA:
            fronteira.append({**linha, "PORQUE_E_FRONTEIRA": _FRONTEIRA[c["URL"]]})
        elif fora_do_foco({"url": c["URL"], "nome": c["NOME"], "familia": fam.get(c["CANDIDATA_ID"])}):
            vivas.append(linha)
    recusadas = []
    if aplicar:
        from fonte_nova import recusar
        for x in vivas:
            recusar(x["URL"], "FORA_DO_FOCO: decisao do dono 23/09 — Veterinaria/IZS/saude animal nao e foco do Sintonia")
            recusadas.append(x["CANDIDATA_ID"])
    out = {"DATASET": "PESQUISADORES-FORA-DO-FOCO-V1",
           "DECISAO": "dono 23/09 ~18:50: Veterinaria, IZS e fontes so de saude animal fora do foco",
           "GERADO_EM": datetime.now(timezone.utc).isoformat(),
           "VIVAS_FORA_DO_FOCO": len(vivas), "FRONTEIRA_A_DECIDIR": len(fronteira),
           "RECUSADAS_AGORA": recusadas, "LISTA": vivas, "FRONTEIRA": fronteira}
    fd, tmp = tempfile.mkstemp(dir=str(FORA_DO_FOCO_JSON.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, FORA_DO_FOCO_JSON)
    return out


# ---------------------------------------------------------------------------
# Catalogo P1d (24/09) — sobre a fila da producao: Sicilia (CONAF), CNR agri,
# revistas tecnicas (Edagricole e imprensa), mercado agricola, pesquisadores CREA.
# ---------------------------------------------------------------------------
PROOF_P1D = RAIZ / "curadoria" / "PESQUISADORES-P1D-PROOF-V1.json"
CREA_SOCIAL = RAIZ / "curadoria" / "PESQUISADORES-P1D-CREA-PERFIS.json"
_OUTRAS_LANES = ("origin/pesquisa-projetos-v1", "origin/pessoas-agro-v1", "origin/pessoas-agro-v2",
                 "origin/pessoas-docentes-v1", "origin/canais-pessoas-v1")
_SIC = "https://www.conaf.it/ordini-e-federazioni/lordine-piu-vicino-a-te/ordini-afferenti-federazione-sicilia/"
_EDA = "https://www.edagricole.it/"


def conhecidos_das_lanes() -> set[str]:
    """URLs registadas por outras frentes que ainda nao estao na producao."""
    out: set[str] = set()
    for ref in _OUTRAS_LANES:
        try:
            bruto = subprocess.run(["git", "show", ref + ":candidatas/FONTES-CANDIDATAS.json"],
                                   cwd=str(RAIZ), capture_output=True, check=True).stdout
            out |= {normalizar(c["URL"]) for c in json.loads(bruto)["CANDIDATAS"]}
        except Exception:
            pass
    return out


def _sic(nome, url):
    return _c("ORDINI_COLLEGI", "ORGANIZACAO", "Dottori Agronomi e Forestali — %s (sicilia)" % nome, url,
              "ordine territoriale agronomi e forestali (sicilia): notizie, eventi e formazione", _SIC,
              titulo_re=_T_ORD, pausa=3, prova="listado pela pagina oficial CONAF da regiao sicilia")


def _eda(nome, url, para_que):
    return _c("RIVISTE_TECNICHE", "IMPRENSA", nome, url, para_que, _EDA,
              prova="listada pela editora na pagina Le nostre riviste (edagricole.it)")


def _imp(familia, nome, url, para_que, titulo_re):
    return _dns(familia, "IMPRENSA", nome, url, para_que, titulo_re, sub=False)


CATALOGO_P1D: list[dict] = [
    _sic("federazione sicilia", "https://federazionesicilia.conaf.it/"),
    _sic("ordine agrigento", "https://ordineagrigento.conaf.it/"),
    _sic("ordine catania", "https://ordinecatania.conaf.it/"),
    _sic("ordine trapani", "https://ordinetrapani.conaf.it/"),
    _sic("ordine caltanissetta", "http://www.agronomicl.it/"),
    _sic("ordine enna", "http://www.agronomienna.it/"),
    _sic("ordine messina", "https://www.agronomimessina.it/"),
    _sic("ordine palermo", "http://agronomiforestalipalermo.it/"),
    _sic("ordine ragusa", "http://www.agronomiragusa.it/"),
    _sic("ordine siracusa", "http://www.agronomiforestalisiracusa.it/"),

    _dns("CNR", "CIENCIA", "CNR IBBA — Istituto di Biologia e Biotecnologia Agraria", "https://www.ibba.cnr.it/",
         "biotecnologie vegetali e agrarie", r"IBBA|biolog|agrar"),
    _dns("CNR", "CIENCIA", "CNR IRET — Istituto di Ricerca sugli Ecosistemi Terrestri", "https://www.iret.cnr.it/",
         "suolo, ecosistemi agrari e forestali", r"IRET|ecosistem"),
    _dns("CNR", "CIENCIA", "CNR DiSBA — Dipartimento Scienze Bio-Agroalimentari", "https://www.disba.cnr.it/",
         "rete CNR della ricerca agroalimentare", r"DiSBA|bio-agro|agroalimentar"),
    _dns("UNIVERSITA", "CIENCIA", "Dip. Biotecnologie, Univ. Verona", "https://www.dbt.univr.it/",
         "ricerca su vite, colture e biotecnologie vegetali Verona", r"biotecnolog"),

    _eda("Rivista di Orticoltura e Floricoltura (Edagricole)", "https://rivistaorticoltura.edagricole.it/",
         "rivista tecnica di orticoltura e floricoltura"),
    _eda("Rivista di Frutticoltura e Ortofloricoltura (Edagricole)", "https://rivistafrutticoltura.edagricole.it/",
         "rivista tecnica di frutticoltura"),
    _eda("Macchine Agricole News (Edagricole)", "https://macchineagricolenews.edagricole.it/",
         "meccanizzazione agricola e agricoltura di precisione"),
    _eda("VVQ Vigne, Vini e Qualita (Edagricole)", "https://vigneviniequalita.edagricole.it/",
         "rivista tecnica di viticoltura ed enologia"),

    _imp("MERCATO_AGRICOLO", "Italiafruit News", "https://www.italiafruit.net/",
         "mercati e prezzi dell'ortofrutta italiana", r"italiafruit|ortofrutt|frutta"),
    _imp("MERCATO_AGRICOLO", "FreshPlaza Italia", "https://www.freshplaza.it/",
         "notizie di mercato ortofrutticolo", r"freshplaza|ortofrutt"),
    _dns("MERCATO_AGRICOLO", "BASE_OFICIAL", "AGER Borsa Merci Bologna", "https://www.agerborsamerci.it/",
         "listini settimanali di cereali, foraggi e prodotti agricoli", r"borsa|merci|ager", sub=False),
    _dns("MERCATO_AGRICOLO", "BASE_OFICIAL", "BMTI — Borsa Merci Telematica Italiana", "https://www.bmti.it/",
         "prezzi all'ingrosso dei prodotti agricoli", r"borsa|BMTI|merci", sub=False),
    _imp("RIVISTE_TECNICHE", "Teatro Naturale", "https://www.teatronaturale.it/",
         "olio, olivicoltura e agroalimentare", r"teatro|olio|natural"),
    _imp("RIVISTE_TECNICHE", "Olivonews", "https://www.olivonews.it/", "olivicoltura e olio", r"olivo|olio"),
    _imp("RIVISTE_TECNICHE", "Agrisole (Il Sole 24 Ore)", "https://www.agrisole.it/",
         "economia e mercati agricoli", r"agrisole|agricolt"),
    _imp("RIVISTE_TECNICHE", "Agricultura.it", "https://www.agricultura.it/", "notizie agricole", r"agricultura|agricolt"),
    _imp("RIVISTE_TECNICHE", "Il Nuovo Agricoltore", "https://www.ilnuovoagricoltore.it/",
         "notizie tecniche per agricoltori", r"agricolt"),
    _imp("RIVISTE_TECNICHE", "AgrifoodToday", "https://www.agrifoodtoday.it/", "notizie agroalimentari", r"agrifood"),
]


def pesquisadores_crea() -> list[dict]:
    """Perfis academicos ligados pela pagina oficial do pesquisador no CREA."""
    d = json.loads(CREA_SOCIAL.read_text(encoding="utf-8"))
    out = []
    for perfil, a in d["PERFIS"].items():
        for link in a["pessoais"]:
            if "researchgate.net/profile/" not in link:
                continue
            out.append(_c("PESSOAS_PESQUISADORES", "CIENCIA", "%s (CREA %s) — ResearchGate" % (a["nome"], a["centro"]),
                          link, "pubblicazioni del ricercatore CREA %s" % a["nome"], perfil, pausa=3,
                          method="link_da_pagina_oficial_do_pesquisador",
                          prova="ligado pela pagina oficial do pesquisador no CREA (%s)" % perfil))
    return out


# ---------------------------------------------------------------------------
# Catalogo P1e (24/09, D29 «janelas de cultura»): paginas de BOLETINS dos
# servicos regionais (difesa integrata, avvisi, agrometeo, fenologia) e
# consorzi di difesa. Links tirados das paginas oficiais em p1e_e1.txt.
# ---------------------------------------------------------------------------
PROOF_P1E = RAIZ / "curadoria" / "PESQUISADORES-P1E-PROOF-V1.json"


def _bol(familia, nome, url, para_que, de):
    return _c(familia, "BASE_OFICIAL", nome, url, para_que, de,
              prova="ligada pela pagina oficial do servico regional %s" % de)


_VDA = "https://www.regione.vda.it/agricoltura/per_gli_agricoltori/fitosanitario/default_i.asp"
_ER = "https://agricoltura.regione.emilia-romagna.it/fitosanitario"
_VEN = "https://www.regione.veneto.it/web/fitosanitario"
_FVG = "https://www.ersa.fvg.it/cms/hp/"
_CAM = "http://www.agricoltura.regione.campania.it/difesa/difesa.html"
_SAR = "https://www.sar.sardegna.it/"

CATALOGO_P1E: list[dict] = [
    _bol("BOLLETTINI_DIFESA", "Valle d'Aosta — Avvisi fitosanitari per frutticoltori",
         "https://www.regione.vda.it/agricoltura/per_gli_agricoltori/fitosanitario/avvisi/frutticoltura_i.asp",
         "avvisi di difesa per melo, pero e frutta (momento del trattamento)", _VDA),
    _bol("BOLLETTINI_DIFESA", "Valle d'Aosta — Avvisi fitosanitari per viticoltori",
         "https://www.regione.vda.it/agricoltura/per_gli_agricoltori/fitosanitario/avvisi/viticoltura_i.asp",
         "avvisi di difesa della vite (peronospora, oidio, fenologia)", _VDA),
    _bol("BOLLETTINI_DIFESA", "Piemonte — Bacheca dei bollettini fitosanitari",
         "https://www.regione.piemonte.it/web/temi/agricoltura/servizi-fitosanitari-pan/bacheca-dei-bollettini",
         "bollettini di difesa integrata per coltura e zona", "https://www.regione.piemonte.it/web/temi/agricoltura/servizi-fitosanitari-pan"),
    _bol("BOLLETTINI_DIFESA", "Liguria — Sorveglianza del territorio e monitoraggio organismi nocivi",
         "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/servizio-fitosanitario-regionale/sorveglianza-del-territorio-carte-di-diffusione-e-monitoraggio-degli-organismi-nocivi.html",
         "carte di diffusione e monitoraggio di parassiti", "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/servizio-fitosanitario-regionale.html"),
    _bol("BOLLETTINI_AGROMETEO", "Liguria — Centro di agrometeorologia (CAAR)",
         "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/agrometeo-caar.html",
         "bollettini agrometeorologici Liguria", "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/servizio-fitosanitario-regionale.html"),
    _bol("BOLLETTINI_DIFESA", "Emilia-Romagna — Bollettini territoriali di produzione integrata e biologica",
         "https://agricoltura.regione.emilia-romagna.it/fitosanitario/difesa-sostenibile/bollettini",
         "bollettini settimanali di difesa integrata per provincia", _ER),
    _bol("BOLLETTINI_DIFESA", "Veneto — Bollettini fitosanitari 2026",
         "https://www.regione.veneto.it/web/fitosanitario/bollettini-fitosanitari-2026",
         "bollettini fitosanitari regionali", _VEN),
    _bol("BOLLETTINI_DIFESA", "Veneto — Difesa delle colture (bollettini e materiali tecnici)",
         "https://www.regione.veneto.it/web/fitosanitario/difesa-colture",
         "bollettini, disciplinari e materiali tecnici per la difesa", _VEN),
    _bol("BOLLETTINI_DIFESA", "ERSA FVG — Bollettini di difesa integrata e biologica",
         "http://www.ersa.fvg.it/cms/aziende/in-formazione/Bollettini/index.html",
         "bollettini di difesa per coltura in Friuli Venezia Giulia", _FVG),
    _bol("BOLLETTINI_DIFESA", "ERSA FVG — Avvisi e comunicazioni",
         "http://www.ersa.fvg.it/cms/aziende/in-formazione/Avvisi-Comunicazioni/index.html",
         "avvisi fitosanitari e schede di difesa", _FVG),
    _bol("BOLLETTINI_DIFESA", "Campania — Bollettini fitosanitari 2026",
         "http://www.agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026.html",
         "bollettini fitosanitari regionali", _CAM),
    _bol("BOLLETTINI_DIFESA", "Campania — SIMFITO, monitoraggio fitosanitario",
         "https://simfito.regione.campania.it/", "rete di monitoraggio di parassiti e malattie", _CAM),
    _bol("BOLLETTINI_AGROMETEO", "Campania — Agrometeorologia",
         "http://www.agricoltura.regione.campania.it/meteo/agrometeo.htm",
         "dati e bollettini agrometeo delle centraline regionali", _CAM),
    _bol("BOLLETTINI_DIFESA", "Umbria — Bollettini fitosanitari 2026",
         "https://www.regione.umbria.it/agricoltura/servizio-fitosanitario-regionale/in-evidenza/-/asset_publisher/PONvICXXT7f8/content/bollettini-fitosanitari-2026",
         "bollettini fitosanitari regionali", "https://www.regione.umbria.it/agricoltura/servizio-fitosanitario-regionale"),
    _bol("BOLLETTINI_DIFESA", "ARSAC Calabria — Bollettino agrometeorologico e fitosanitario (agrumi, olivo, vite)",
         "https://www.arsacweb.it/bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-e-vite/",
         "avvisi di difesa per agrumi, olivo e vite", "https://www.regione.calabria.it/website/organizzazione/dipartimento8/subsite/fitosanitario/"),
    _bol("BOLLETTINI_DIFESA", "Molise — Bollettini e comunicati fitosanitari",
         "https://www.regione.molise.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/18077",
         "bollettini fitosanitari regionali", "https://www.regione.molise.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/4130"),
    _bol("BOLLETTINI_DIFESA", "Sicilia — Difesa fitosanitaria",
         "https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-agricoltura-sviluppo-rurale-pesca-mediterranea/dipartimento-agricoltura/difesa-fitosanitaria",
         "difesa fitosanitaria regionale e avvisi", "https://www.regione.sicilia.it/"),
    _bol("BOLLETTINI_AGROMETEO", "LaMMA — Bollettino agrometeo",
         "https://www.lamma.toscana.it/agrometeo/firenze", "bollettino agrometeorologico Toscana", "https://www.lamma.toscana.it/"),
    _bol("BOLLETTINI_AGROMETEO", "ARSARP Molise — Agrometeorologia",
         "https://www.arsarp.it/category/agrometeorologia-2/", "agrometeorologia Molise", "https://www.arsarp.it/"),
    _bol("BOLLETTINI_AGROMETEO", "ARPAS Sardegna — Bollettino fenologico",
         "http://www.sar.sardegna.it/servizi/agro/bollfenologico.asp", "fasi fenologiche delle colture in Sardegna", _SAR),
    _bol("BOLLETTINI_AGROMETEO", "ARPAS Sardegna — Bollettino decadale di siccita",
         "http://www.sar.sardegna.it/servizi/agro/monit_siccita.asp", "siccita e bilancio idrico agrario", _SAR),
    _bol("BOLLETTINI_AGROMETEO", "ARPAS Sardegna — Riepilogo mensile agrometeorologico",
         "http://www.sar.sardegna.it/pubblicazioni/riepiloghimensili/mensili.asp", "riepiloghi mensili agrometeo", _SAR),

    # consorzi di difesa e servizi di avviso (DNS confirmado 24/09; identidade pelo titulo)
    _dns("CONSORZI_DIFESA", "ORGANIZACAO", "ASNACODI — Associazione Nazionale Consorzi di Difesa",
         "https://www.asnacodi.it/", "rete nazionale dei consorzi di difesa delle produzioni agricole", r"asnacodi|consorzi|difesa"),
    _dns("CONSORZI_DIFESA", "ORGANIZACAO", "CODIPRA Trento — Consorzio Difesa Produttori Agricoli",
         "https://www.codipra.it/", "avvisi, meteo e difesa delle produzioni in Trentino", r"codipra|difesa"),
    _dns("CONSORZI_DIFESA", "ORGANIZACAO", "Condifesa TVB (Treviso, Vicenza, Belluno)",
         "https://www.condifesatvb.it/", "consorzio di difesa: avvisi e servizi agrometeo", r"condifesa|difesa"),
    _dns("CONSORZI_DIFESA", "ORGANIZACAO", "Condifesa Lombardia Nord-Est",
         "https://www.condifesalombardianordest.it/", "consorzio di difesa: avvisi e servizi", r"condifesa|difesa"),
    _dns("CONSORZI_DIFESA", "ORGANIZACAO", "Condifesa Veneto", "https://www.condifesaveneto.it/",
         "consorzi di difesa del Veneto", r"condifesa|difesa"),
    _dns("CONSORZI_DIFESA", "ORGANIZACAO", "Consorzio fitosanitario di Reggio Emilia", "https://www.fitosanitario.re.it/",
         "bollettini di produzione integrata della provincia di Reggio Emilia", r"fitosanitari|consorzio"),
    _dns("CONSORZI_DIFESA", "ORGANIZACAO", "Horta — servizi di supporto alle decisioni (vite.net)", "https://www.horta-srl.it/",
         "modelli fenologici e momento del trattamento (DSS)", r"horta"),
]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Discovery focada em pesquisadores/CIENCIA para IT.")
    ap.add_argument("--orcamento", type=int, default=200)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--p1b", action="store_true",
                    help="fase P1b: releitura, IZS, Veterinaria, Ordini (rede, VPN IT)")
    ap.add_argument("--p1e", action="store_true",
                    help="D29 janelas de cultura: boletins regionais e consorzi di difesa (rede)")
    ap.add_argument("--p1d", action="store_true",
                    help="24/09: Sicilia, CNR agri, revistas tecnicas, mercado, pesquisadores CREA (rede)")
    ap.add_argument("--p1c", action="store_true",
                    help="3.a volta: IZS, Vet/Agraria, servicos regionais, revistas (rede, VPN IT)")
    ap.add_argument("--fora-do-foco", dest="fora_do_foco", action="store_true",
                    help="lista as registadas de Veterinaria/IZS (sem rede, nao mexe na fila)")
    ap.add_argument("--aplicar", action="store_true",
                    help="com --fora-do-foco: recusa-as pela porta canonica")
    ap.add_argument("--lista", action="store_true",
                    help="so escreve PESQUISADORES-LISTA-V1.json, sem rede")
    a = ap.parse_args()

    if a.p1d or a.p1e:
        cat = CATALOGO_P1E if a.p1e else (CATALOGO_P1D + pesquisadores_crea())
        r = correr_p1b(cat, orcamento=a.orcamento,
                       prova_path=PROOF_P1E if a.p1e else PROOF_P1D, por_dominio=20)
        l = escrever_lista()
        for k in ("CANDIDATAS_NOVAS", "POR_FAMILIA", "ACOES", "DUPLICADAS_EVITADAS",
                  "PEDIDOS_DE_REDE", "MAX_PEDIDOS_UM_DOMINIO", "VIGIA_PAROU", "VIGIAS"):
            print(k, r[k])
        print("LISTA_CUMULATIVA", l["CANDIDATAS_NOVAS"], l["POR_FAMILIA"])
        return 0

    if a.p1b or a.p1c:
        cat = (CATALOGO_P1C + sfr_regionais()) if a.p1c else (CATALOGO_P1B + ordini_do_conaf())
        r = correr_p1b(cat, orcamento=a.orcamento, prova_path=PROOF_P1C if a.p1c else None)
        l = escrever_lista()
        for k in ("CANDIDATAS_NOVAS", "POR_FAMILIA", "ACOES", "DUPLICADAS_EVITADAS",
                  "PEDIDOS_DE_REDE", "MAX_PEDIDOS_UM_DOMINIO", "VIGIA_PAROU", "VIGIAS"):
            print(k, r[k])
        print("LISTA_CUMULATIVA", l["CANDIDATAS_NOVAS"], l["POR_FAMILIA"])
        return 0

    if a.fora_do_foco:
        r = listar_fora_do_foco(aplicar=a.aplicar)
        print("VIVAS_FORA_DO_FOCO", r["VIVAS_FORA_DO_FOCO"], "FRONTEIRA", r["FRONTEIRA_A_DECIDIR"],
              "RECUSADAS_AGORA", len(r["RECUSADAS_AGORA"]))
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
