#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P2 PASSE 2 — URLs corrigidos apos falhas do passe 1.

Cobertura:
  - Fitossanitarios regionais com path correto (regione.X.it/agricoltura/fitosanitario)
  - IRIS repos com GET fallback (HEAD bloqueado)
  - Ordini provinciali com dominios corrigidos
  - Nomisma paths alternativos
  - CONAF notizie path correto
  - Agrotecnici / Periti Agrari corretos
  - Georgofili subpages alternativas
  - CNR ExploRA alternativo
"""
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "candidatas"))
import fonte_nova as FN  # noqa

QUEM_VIU = "p2_pesquisa_projetos_pass2"
DELAY = 1.2

FONTES2 = [
    # -----------------------------------------------------------------------
    # FITOSSANITARI regionali — paths corrigidos
    # -----------------------------------------------------------------------
    ("C", "https://www.regione.veneto.it/web/agricoltura-e-foreste/fitosanitario",
     "Servizio Fitosanitario Regione Veneto",
     "BASE_OFICIAL",
     "boletins fitossanitarios semanais e alertas de pragas e doencas para o Veneto",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.regione.toscana.it/-/fitosanitario",
     "Servizio Fitosanitario Regione Toscana",
     "BASE_OFICIAL",
     "boletins fitossanitarios e avisos de tratamento para a Toscana",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.regione.piemonte.it/web/temi/agricoltura-foreste/difesa-fitosanitaria",
     "Servizio Fitosanitario Regione Piemonte",
     "BASE_OFICIAL",
     "boletins fitossanitarios e alertas de pragas para o Piemonte",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://agricoltura.regione.emilia-romagna.it/fitosanitario",
     "Servizio Fitosanitario Regione Emilia-Romagna",
     "BASE_OFICIAL",
     "boletins fitossanitarios e comunicados de protecao de culturas para a Emilia-Romagna",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.regione.sicilia.it/agricoltura/assessorato/fitosanitario",
     "Servizio Fitosanitario Regione Sicilia",
     "BASE_OFICIAL",
     "boletins fitossanitarios e alertas de pragas para a Sicilia",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.regione.lombardia.it/wps/portal/istituzionale/HP/DettaglioServizio/servizi-e-informazioni/Enti-e-Operatori/agricoltura/fitosanitario",
     "Servizio Fitosanitario Regione Lombardia",
     "BASE_OFICIAL",
     "boletins fitossanitarios para a Lombardia; alertas de pragas e doencas",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.regione.marche.it/Regione-Utile/Agricoltura/Fitosanitario",
     "Servizio Fitosanitario Regione Marche",
     "BASE_OFICIAL",
     "boletins fitossanitarios e alertas de pragas para as Marcas",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.regione.puglia.it/web/servizi-per-il-territorio/fitosanitario",
     "Servizio Fitosanitario Regione Puglia",
     "BASE_OFICIAL",
     "boletins fitossanitarios e alertas de pragas para a Puglia",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.regione.campania.it/regione/it/tematiche/agronomia-fitosanitario/fitosanitario",
     "Servizio Fitosanitario Regione Campania",
     "BASE_OFICIAL",
     "boletins fitossanitarios e alertas de pragas para a Campania",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),

    # -----------------------------------------------------------------------
    # IRIS repositorios — GET fallback e paths alternativos
    # -----------------------------------------------------------------------
    ("E", "https://cris.unibo.it/explore",
     "IRIS/CRIS — Repositorio Universita di Bologna",
     "CIENCIA",
     "repositorio CRIS de publicacoes da Universidade de Bolonha; artigos de agraria e veterinaria",
     "CATEGORIA=IRIS_REPO; PAIS_PROVA=dominio_unibo.it"),
    ("E", "https://amsacta.unibo.it",
     "AMS Acta — Repositorio Open Access Universita di Bologna",
     "CIENCIA",
     "repositorio open access da Universidade de Bolonha; teses e publicacoes de agraria",
     "CATEGORIA=IRIS_REPO; PAIS_PROVA=dominio_unibo.it"),
    ("E", "https://air.unimi.it",
     "AIR — Repositorio Istituzionale Universita di Milano",
     "CIENCIA",
     "repositorio de publicacoes da Universidade de Milao (UNIMI); artigos de agronomia e scienze agrarie",
     "CATEGORIA=IRIS_REPO; PAIS_PROVA=dominio_unimi.it"),
    ("E", "https://paduaresearch.cab.unipd.it",
     "Padua Research Archive — Universita di Padova",
     "CIENCIA",
     "repositorio de teses e publicacoes da Universidade de Padova; agraria, veterinaria e agroalimentar",
     "CATEGORIA=IRIS_REPO; PAIS_PROVA=dominio_unipd.it"),

    # -----------------------------------------------------------------------
    # NOMISMA — paths alternativos
    # -----------------------------------------------------------------------
    ("B", "https://www.nomisma.it/ricerche",
     "Nomisma — Ricerche Agrifood",
     "CIENCIA",
     "pesquisas de mercado agroalimentar da Nomisma: horticultura, cereais, vinho, pecuaria",
     "CATEGORIA=OSSERVATORIO_NOMISMA"),
    ("B", "https://www.nomisma.it/food-agriculture",
     "Nomisma — Food & Agriculture",
     "CIENCIA",
     "seccao agrifood da Nomisma: observatorios e relatorios de mercado agricola italiano",
     "CATEGORIA=OSSERVATORIO_NOMISMA"),

    # -----------------------------------------------------------------------
    # CONAF — noticias com path correto
    # -----------------------------------------------------------------------
    ("G", "https://www.conaf.it/news",
     "CONAF — News e Comunicati",
     "ORGANIZACAO",
     "comunicados e noticias do conselho nacional dos agronomos e florestais italianos",
     "CATEGORIA=ORDINE_AGRONOMI"),
    ("G", "https://www.conaf.it/ordini-provinciali",
     "CONAF — Ordini Provinciali (directorio)",
     "ORGANIZACAO",
     "directorio dos ordini provinciali dos doutores agronomos e florestais italianos; todas as provincias",
     "CATEGORIA=ORDINE_AGRONOMI"),

    # -----------------------------------------------------------------------
    # PERITI AGRARI / AGROTECNICI — dominios corrigidos
    # -----------------------------------------------------------------------
    ("G", "https://www.peritiagrari.it",
     "Collegio Nazionale Periti Agrari e Periti Agrari Laureati",
     "ORGANIZACAO",
     "colegio nacional dos peritos agrarios italianos; noticias, circulares e publicacoes tecnicas",
     "CATEGORIA=COLLEGIO_PERITI_AGRARI"),
    ("G", "https://www.agrotecnici-agrotecnicilaurea.it",
     "Collegio Nazionale degli Agrotecnici e Agrotecnici Laureati",
     "ORGANIZACAO",
     "colegio nacional dos agrotecnicos italianos; noticias, circulares e publicacoes tecnicas",
     "CATEGORIA=COLLEGIO_AGROTECNICI"),

    # -----------------------------------------------------------------------
    # ORDINI PROVINCIALI — dominios corrigidos
    # -----------------------------------------------------------------------
    ("G", "https://www.agronomi.mi.it",
     "Ordine Dottori Agronomi e Forestali Milano",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Milao; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odafbo.it",
     "Ordine Dottori Agronomi e Forestali Bologna",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Bolonha; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odafs.it",
     "Ordine Dottori Agronomi e Forestali Siena",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Siena; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odaf-napoli.it",
     "Ordine Dottori Agronomi e Forestali Napoli",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Napoles; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odaf-bari.it",
     "Ordine Dottori Agronomi e Forestali Bari",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Bari; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odaf-torino.it",
     "Ordine Dottori Agronomi e Forestali Torino",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Turim; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odaf-firenze.it",
     "Ordine Dottori Agronomi e Forestali Firenze",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Florenca; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odaf-roma.it",
     "Ordine Dottori Agronomi e Forestali Roma",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Roma; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odaf-verona.it",
     "Ordine Dottori Agronomi e Forestali Verona",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Verona; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),

    # -----------------------------------------------------------------------
    # GEORGOFILI — paths alternativos
    # -----------------------------------------------------------------------
    ("F", "https://www.georgofili.net",
     "Georgofili.net — Informazione Scientifica Agraria",
     "IMPRENSA",
     "portal de informacao cientifica agraria da Accademia dei Georgofili; noticias e publicacoes tecnicos",
     "CATEGORIA=IMPRENSA_AGRO"),
    ("F", "https://www.georgofili.info",
     "Georgofili.info — Rivista Online di Agronomia",
     "IMPRENSA",
     "revista online de agronomia dos Georgofili; boletim cientifico periodicico com autores agronomos",
     "CATEGORIA=IMPRENSA_AGRO"),

    # -----------------------------------------------------------------------
    # CNR ExploRA alternativo
    # -----------------------------------------------------------------------
    ("F", "https://www.cnr.it/it/istituti",
     "CNR — Elenco Istituti di Ricerca",
     "CIENCIA",
     "directorio de institutos do CNR italiano; permite filtrar por area agraria e agroalimentar",
     "CATEGORIA=PORTAL_PESQUISA_CNR; NOTA=pagina_directorio_diferente_dos_institutos_individuais_P1"),

    # -----------------------------------------------------------------------
    # AGREA / SATA — dominios alternativos
    # -----------------------------------------------------------------------
    ("D", "https://agrea.regione.emilia-romagna.it",
     "AGREA — Agenzia Regionale Erogazioni Agricoltura (ER)",
     "BASE_OFICIAL",
     "pagamentos agricolas e noticias de politica agricola da Emilia-Romagna",
     "CATEGORIA=AGENCIA_PAGAMENTOS_AGRO"),
    ("D", "https://www.sata-agri.it",
     "SATA — Servizio Assistenza Tecnica Allevamenti",
     "BASE_OFICIAL",
     "assistencia tecnica a pecuaria; boletins mensais de saude animal e nutricao",
     "CATEGORIA=ASSISTENCIA_TECNICA"),
]


def _url_ok(url: str, timeout: int = 12) -> tuple[bool, int]:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method,
                                         headers={"User-Agent": "Mozilla/5.0 SintoniaEAME/1.0 (+research)"})
            resp = urllib.request.urlopen(req, timeout=timeout)
            return True, resp.status
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 406):
                return True, e.code
            if method == "HEAD":
                time.sleep(0.5)
                continue
            return False, e.code
        except Exception:
            if method == "HEAD":
                time.sleep(0.5)
                continue
            return False, 0
    return False, 0


def main():
    registadas = []
    falhas = []
    dedup = []
    total_reqs = 0

    d_antes = FN.carregar()
    urls_existentes = {FN.normalizar(c["URL"]) for c in d_antes["CANDIDATAS"]}

    print("P2 PASSE 2 — URLs CORRIGIDOS")
    print("FONTES_ALVO:", len(FONTES2))
    print("-" * 60)

    for cat, url, nome, tipo, para_que, nota in FONTES2:
        chave = FN.normalizar(url)
        if chave in urls_existentes:
            dedup.append(url)
            print(f"  DEDUP [{cat}] {url[:70]}")
            continue

        total_reqs += 1
        ok, code = _url_ok(url)
        time.sleep(DELAY)

        if ok:
            FN.registar(
                tipo=tipo, pais="IT", nome=nome, url=url,
                para_que=para_que,
                quem_viu=QUEM_VIU,
                onde_viu="catalogo_curado_P2_pass2_urls_corrigidos",
                nota=nota,
            )
            registadas.append(url)
            print(f"  OK [{cat}] {code} {url[:70]}")
        else:
            falhas.append((url, code))
            print(f"  FAIL [{cat}] {code} {url[:70]}")

    print("-" * 60)
    print(f"REGISTADAS_NOVAS: {len(registadas)}")
    print(f"DEDUP_SALTADAS:   {len(dedup)}")
    print(f"FALHAS_HTTP:      {len(falhas)}")
    print(f"PEDIDOS_REDE:     {total_reqs}")

    by_cat = {}
    for cat, url, *_ in FONTES2:
        if url in registadas:
            by_cat.setdefault(cat, 0)
            by_cat[cat] += 1
    for cat in sorted(by_cat):
        print(f"  CATEGORIA_{cat}: {by_cat[cat]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
