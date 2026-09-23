#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P2 — Pesquisa Aplicada e Projetos: descoberta e registo de fontes.

Categorias cobertas (NAO-P1: P1 cobre CREA, CNR, universidades, ISPRA, IZS, Mach, Georgofili):
  A — Rete Rurale Nazionale + Gruppi Operativi PEI-AGRI
  B — Osservatori (ISMEA, Nomisma agro)
  C — Servicos fitossanitarios regionais (boletins recorrentes)
  D — Consorzi e centros de pesquisa (NAO CRPV)
  E — IRIS repositorios de publicacoes (diferentes dos departamentos universitarios)
  F — Outros (CNR ExploRA portal, PSR informativos, AGREA)
"""
import sys
import time
import urllib.request
import urllib.robotparser
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "candidatas"))
import fonte_nova as FN  # noqa: E402

QUEM_VIU = "p2_pesquisa_projetos"
DELAY = 1.2  # segundos entre pedidos

# ---------------------------------------------------------------------------
# CATALOGOS P2 — (categoria, url, nome, tipo, para_que, nota)
# ---------------------------------------------------------------------------
FONTES = [
    # -----------------------------------------------------------------------
    # CATEGORIA A — Rete Rurale Nazionale + EIP-AGRI / Gruppi Operativos
    # -----------------------------------------------------------------------
    ("A", "https://www.reterurale.it/notizie",
     "Rete Rurale Nazionale — Notizie",
     "BASE_OFICIAL",
     "boletim de noticias e actualizacoes de politica rural italiana; publicacao recorrente",
     "CATEGORIA=RETE_RURALE"),
    ("A", "https://www.reterurale.it/pubblicazioni",
     "Rete Rurale Nazionale — Pubblicazioni",
     "BASE_OFICIAL",
     "publicacoes tecnicas e relatorios da rede rural italiana",
     "CATEGORIA=RETE_RURALE"),
    ("A", "https://www.reterurale.it/gruppioperativi",
     "Rete Rurale — Gruppi Operativi PEI-AGRI",
     "CIENCIA",
     "catalogo dos Grupos Operativos da Parceria Europeia de Inovacao em Agricultura (EIP-AGRI Italia)",
     "CATEGORIA=EIP_AGRI_GO"),
    ("A", "https://www.reterurale.it/schede",
     "Rete Rurale — Schede Progetto",
     "CIENCIA",
     "fichas de projecto dos programas de desenvolvimento rural italianos; detalhes de cada GO-PEI",
     "CATEGORIA=EIP_AGRI_GO"),
    ("A", "https://www.reterurale.it/innovazione",
     "Rete Rurale — Innovazione",
     "CIENCIA",
     "seccao de inovacao da rede rural; transferencia de conhecimento agro",
     "CATEGORIA=EIP_AGRI_INOVACAO"),

    # -----------------------------------------------------------------------
    # CATEGORIA B — Osservatori: ISMEA e Nomisma
    # -----------------------------------------------------------------------
    ("B", "https://www.ismea.it",
     "ISMEA — Istituto di Servizi per il Mercato Agricolo Alimentare",
     "BASE_OFICIAL",
     "estatisticas de mercado, precos e dados de cadeia agroalimentar italiana; publicacao recorrente",
     "CATEGORIA=OSSERVATORIO_ISMEA"),
    ("B", "https://www.ismea.it/notizie",
     "ISMEA — Notizie",
     "BASE_OFICIAL",
     "comunicados e actualizacoes de mercado agricola italiano",
     "CATEGORIA=OSSERVATORIO_ISMEA"),
    ("B", "https://www.ismea.it/dati-e-analisi",
     "ISMEA — Dati e Analisi",
     "BASE_OFICIAL",
     "dados de producao, consumo e preco de produtos agricolas italianos",
     "CATEGORIA=OSSERVATORIO_ISMEA"),
    ("B", "https://www.ismea.it/pubblicazioni",
     "ISMEA — Pubblicazioni",
     "BASE_OFICIAL",
     "relatorios e estudos de mercado agricola italiano publicados periodicamente",
     "CATEGORIA=OSSERVATORIO_ISMEA"),
    ("B", "https://www.nomisma.it/osservatorio-vino",
     "Nomisma — Osservatorio del Vino",
     "CIENCIA",
     "observatorio de mercado do vinho italiano: dados de producao, consumo e export; relatorios anuais",
     "CATEGORIA=OSSERVATORIO_NOMISMA"),
    ("B", "https://www.nomisma.it/osservatorio-cereali-mais",
     "Nomisma — Osservatorio Cereali e Mais",
     "CIENCIA",
     "observatorio de mercado de cereais e milho italiano; relatorios trimestrais",
     "CATEGORIA=OSSERVATORIO_NOMISMA"),
    ("B", "https://www.nomisma.it/osservatorio-ortofrutta",
     "Nomisma — Osservatorio Ortofrutta",
     "CIENCIA",
     "observatorio do mercado de horticolas e frutas em Italia; relatorios periodicos",
     "CATEGORIA=OSSERVATORIO_NOMISMA"),
    ("B", "https://www.nomisma.it/area-ricerca/agrifood",
     "Nomisma — Area Ricerca Agrifood",
     "CIENCIA",
     "estudos e pesquisa de mercado agroalimentar italiano: consumo, distribucao, tendencias",
     "CATEGORIA=OSSERVATORIO_NOMISMA"),

    # -----------------------------------------------------------------------
    # CATEGORIA C — Servicos fitossanitarios regionais (boletins)
    # -----------------------------------------------------------------------
    ("C", "https://www.fitosanitario.regione.veneto.it",
     "Servizio Fitosanitario Regione Veneto",
     "BASE_OFICIAL",
     "boletins fitossanitarios semanais e alertas de pragas e doencas para o Veneto",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.fitosanitario.regione.toscana.it",
     "Servizio Fitosanitario Regione Toscana",
     "BASE_OFICIAL",
     "boletins fitossanitarios e avisos de tratamento para a Toscana",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.fitosanitario.regione.piemonte.it",
     "Servizio Fitosanitario Regione Piemonte",
     "BASE_OFICIAL",
     "boletins fitossanitarios e alertas de pragas para o Piemonte",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.fitosanitario.regione.emilia-romagna.it",
     "Servizio Fitosanitario Regione Emilia-Romagna",
     "BASE_OFICIAL",
     "boletins fitossanitarios e comunicados de protecao de culturas para a Emilia-Romagna",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.regione.sicilia.it/agricoltura/servizifitosanitari",
     "Servizio Fitosanitario Regione Sicilia",
     "BASE_OFICIAL",
     "boletins fitossanitarios e alertas de pragas para a Sicilia",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),
    ("C", "https://www.regione.campania.it/regione/it/tematiche/agronomia-fitosanitario",
     "Servizio Fitosanitario Regione Campania",
     "BASE_OFICIAL",
     "boletins fitossanitarios e alertas de pragas para a Campania",
     "CATEGORIA=FITOSANITARIO_REGIONALE"),

    # -----------------------------------------------------------------------
    # CATEGORIA D — Consorzi e centros de pesquisa (NAO CRPV)
    # -----------------------------------------------------------------------
    ("D", "https://www.crpa.it",
     "CRPA — Centro Ricerche Produzioni Animali",
     "CIENCIA",
     "pesquisa em producao animal, suinocultura, bovinos e eficiencia energetica agro; boletins tecnicos",
     "CATEGORIA=CONSORZIO_RICERCA; NOTA=CRPA_nao_CRPV"),
    ("D", "https://www.crpa.it/index.php/pubblicazioni",
     "CRPA — Pubblicazioni Tecniche",
     "CIENCIA",
     "publicacoes tecnicas de pesquisa em producao animal e ambiente agricola",
     "CATEGORIA=CONSORZIO_RICERCA"),
    ("D", "https://www.sata.bs.it",
     "SATA — Servizio di Assistenza Tecnica agli Allevamenti",
     "BASE_OFICIAL",
     "assistencia tecnica a pecuaria; boletins mensais de saude animal e nutricao",
     "CATEGORIA=ASSISTENCIA_TECNICA"),
    ("D", "https://www.agrea.it",
     "AGREA — Agenzia Regionale per le Erogazioni in Agricoltura (Emilia-Romagna)",
     "BASE_OFICIAL",
     "pagamentos agricolas e noticias de politica agricola para a Emilia-Romagna",
     "CATEGORIA=AGENCIA_PAGAMENTOS_AGRO"),

    # -----------------------------------------------------------------------
    # CATEGORIA E — IRIS repositorios universitarios (publicacoes agrarias)
    # (distintos dos departamentos que a P1 cobre — P1 = departamentos/noticias,
    #  P2 = repositorios institucionais de pre-prints e artigos publicados)
    # -----------------------------------------------------------------------
    ("E", "https://iris.unibo.it",
     "IRIS — Repositorio Istituzionale Universita di Bologna",
     "CIENCIA",
     "repositorio institucional de publicacoes de pesquisa da Universidade de Bolonha; listagens de artigos agro",
     "CATEGORIA=IRIS_REPO; PAIS_PROVA=dominio_unibo.it"),
    ("E", "https://iris.unipd.it",
     "IRIS — Repositorio Istituzionale Universita di Padova",
     "CIENCIA",
     "repositorio de publicacoes de pesquisa da Universidade de Padova; artigos de agraria, veterinaria",
     "CATEGORIA=IRIS_REPO; PAIS_PROVA=dominio_unipd.it"),
    ("E", "https://iris.unimi.it",
     "IRIS — Repositorio Istituzionale Universita di Milano",
     "CIENCIA",
     "repositorio de publicacoes da Universidade de Milao; artigos de agronomia e scienze agrarie",
     "CATEGORIA=IRIS_REPO; PAIS_PROVA=dominio_unimi.it"),
    ("E", "https://iris.unitn.it",
     "IRIS — Repositorio Istituzionale Universita di Trento",
     "CIENCIA",
     "repositorio de publicacoes da Universidade de Trento; artigos de agroalimentar e montanha",
     "CATEGORIA=IRIS_REPO; PAIS_PROVA=dominio_unitn.it"),

    # -----------------------------------------------------------------------
    # CATEGORIA F — Outros portais de pesquisa e informativos
    # -----------------------------------------------------------------------
    ("F", "https://explora.cnr.it",
     "CNR ExploRA — Portale della Ricerca",
     "CIENCIA",
     "portal de pesquisa do CNR italiano: busca de projetos, publicacoes e institutos por tema agro",
     "CATEGORIA=PORTAL_PESQUISA_CNR; NOTA=ExploRA_portal_diferente_dos_institutos_CNR_de_P1"),
    ("F", "https://www.pianetapsr.it",
     "PianetaPSR — Rivista sui Programmi di Sviluppo Rurale",
     "IMPRENSA",
     "revista e noticias sobre os PSR (Programas de Desenvolvimento Rural) italianos; publicacao recorrente",
     "CATEGORIA=IMPRENSA_PSR"),
    ("F", "https://agronotizie.imagelinenetwork.com",
     "AgroNotizie — Notizie di Agricoltura",
     "IMPRENSA",
     "veiculo de imprensa especializado em noticias tecnicas agricolas italianas; publicacao diaria",
     "CATEGORIA=IMPRENSA_AGRO"),
    ("F", "https://www.terraevita.it",
     "Terra e Vita — Rivista Agricola",
     "IMPRENSA",
     "revista tecnica agricola italiana com boletins fitossanitarios e agronomicos; publicacao semanal",
     "CATEGORIA=IMPRENSA_AGRO"),
    ("F", "https://www.informatoreagrario.it",
     "L'Informatore Agrario",
     "IMPRENSA",
     "revista tecnica agricola italiana especializada em fitossanitario, agronomia e legislacao; publicacao quinzenal",
     "CATEGORIA=IMPRENSA_AGRO"),
    ("F", "https://www.georgofili.it/contenuti/notizie",
     "Accademia dei Georgofili — Notizie",
     "IMPRENSA",
     "boletim de noticias da Accademia dei Georgofili; publicacoes tecnicas e cientificas de agronomia",
     "CATEGORIA=IMPRENSA_AGRO; NOTA=pagina_noticias_distinta_da_home_P1"),
    ("F", "https://www.georgofili.it/contenuti/pubblicazioni",
     "Accademia dei Georgofili — Pubblicazioni",
     "CIENCIA",
     "publicacoes tecnicas da Accademia dei Georgofili: atti, quaderni e relatorios agronomicos",
     "CATEGORIA=PUBLICACOES_CIENCIA"),

    # -----------------------------------------------------------------------
    # CATEGORIA G — Ordini e Collegi professionali (dottori agronomi e forestali)
    # Organizacoes de classe dos engenheiros agronomos e florestais italianos
    # -----------------------------------------------------------------------
    ("G", "https://www.conaf.it",
     "CONAF — Consiglio Nazionale Dottori Agronomi e Dottori Forestali",
     "ORGANIZACAO",
     "conselho nacional dos doutores agronimos e florestais italianos; noticias, publicacoes e posicionamentos tecnicos",
     "CATEGORIA=ORDINE_AGRONOMI"),
    ("G", "https://www.conaf.it/notizie",
     "CONAF — Notizie",
     "ORGANIZACAO",
     "comunicados e noticias do conselho nacional dos agronomos e florestais italianos; publicacao recorrente",
     "CATEGORIA=ORDINE_AGRONOMI"),
    ("G", "https://www.conaf.it/pubblicazioni",
     "CONAF — Pubblicazioni",
     "CIENCIA",
     "publicacoes tecnicas do conselho nacional de agronomia e florestal italiano",
     "CATEGORIA=ORDINE_AGRONOMI"),
    ("G", "https://www.collegioperitiagrariegperitiagrari.it",
     "Collegio Periti Agrari e Periti Agrari Laureati",
     "ORGANIZACAO",
     "colegio nacional dos peritos agrarios italianos; noticias, circulares e publicacoes tecnicas",
     "CATEGORIA=COLLEGIO_PERITI_AGRARI"),
    ("G", "https://www.agrotecnici.it",
     "Collegio Nazionale degli Agrotecnici e Agrotecnici Laureati",
     "ORGANIZACAO",
     "colegio nacional dos agrotecnicos italianos; noticias, circulares e publicacoes tecnicas",
     "CATEGORIA=COLLEGIO_AGROTECNICI"),
    # Ordini provinciali dos agronomos — maiores regioes agricolas
    ("G", "https://www.odaf.mi.it",
     "Ordine Dottori Agronomi e Forestali Milano",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Milao; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odaf.bo.it",
     "Ordine Dottori Agronomi e Forestali Bologna",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Bolonha; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odafvr.it",
     "Ordine Dottori Agronomi e Forestali Verona",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Verona; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odafroma.it",
     "Ordine Dottori Agronomi e Forestali Roma",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Roma; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odaf.napoli.it",
     "Ordine Dottori Agronomi e Forestali Napoli",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Napoles; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odafbari.it",
     "Ordine Dottori Agronomi e Forestali Bari",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Bari; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odafto.it",
     "Ordine Dottori Agronomi e Forestali Torino",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Turim; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),
    ("G", "https://www.odaf.fi.it",
     "Ordine Dottori Agronomi e Forestali Firenze",
     "ORGANIZACAO",
     "ordem provincial dos agronomos e florestais de Florenca; publicacoes e eventos tecnicos",
     "CATEGORIA=ORDINE_PROVINCIALE"),

    # -----------------------------------------------------------------------
    # CATEGORIA H — Canais sociais/video ORGANIZACIONAIS de pesquisa agro IT
    # D24 (DECISOES-DONO-2026-09-23.md): perfis publicos de pesquisadores e
    # agronomos autorizados. Aqui: canais ORGANIZACIONAIS com prova conhecida.
    # Perfis PESSOAIS de pesquisadores individuais exigem prova de identidade
    # (pagina oficial universidade/ordine que ligue o nome ao perfil) — devem
    # ser registados por pesquisa web dedicada apos este lote.
    # -----------------------------------------------------------------------
    ("H", "https://www.youtube.com/@conafagronomi",
     "CONAF — YouTube (Dottori Agronomi e Forestali)",
     "YOUTUBE",
     "canal YouTube do CONAF: videoaulas, webinars e eventos tecnicos de agronomia e florestal italiana; D24",
     "CATEGORIA=CANAL_ORGANIZACIONAL; PAIS_PROVA=conaf.it_entidade_nacional_IT; D24=DECISOES-DONO-2026-09-23"),
    ("H", "https://www.youtube.com/@informatoreagrario",
     "L'Informatore Agrario — YouTube",
     "YOUTUBE",
     "canal YouTube da revista tecnica agricola italiana Informatore Agrario; videos agronômicos; D24",
     "CATEGORIA=CANAL_ORGANIZACIONAL; PAIS_PROVA=informatoreagrario.it; D24=DECISOES-DONO-2026-09-23"),
    ("H", "https://www.youtube.com/@terraevita",
     "Terra e Vita — YouTube",
     "YOUTUBE",
     "canal YouTube da revista tecnica agricola italiana Terra e Vita; fitossanitario, agronomia; D24",
     "CATEGORIA=CANAL_ORGANIZACIONAL; PAIS_PROVA=terraevita.it; D24=DECISOES-DONO-2026-09-23"),
    ("H", "https://www.youtube.com/@agronotizie",
     "AgroNotizie — YouTube",
     "YOUTUBE",
     "canal YouTube do portal de noticias agricolas italiano AgroNotizie; videos tecnicos; D24",
     "CATEGORIA=CANAL_ORGANIZACIONAL; PAIS_PROVA=agronotizie.imagelinenetwork.com; D24=DECISOES-DONO-2026-09-23"),
    ("H", "https://www.youtube.com/@reterurale",
     "Rete Rurale Nazionale — YouTube",
     "YOUTUBE",
     "canal YouTube da Rete Rurale Nazionale italiana; webinars e eventos EIP-AGRI e PSR; D24",
     "CATEGORIA=CANAL_ORGANIZACIONAL; PAIS_PROVA=reterurale.it_entidade_nacional_IT; D24=DECISOES-DONO-2026-09-23"),
    ("H", "https://www.linkedin.com/company/conaf-agronomi",
     "CONAF — LinkedIn",
     "LINKEDIN",
     "pagina LinkedIn do conselho nacional dos agronomos italianos; publicacoes e noticias da profissao; D24",
     "CATEGORIA=CANAL_ORGANIZACIONAL; PAIS_PROVA=conaf.it; D24=DECISOES-DONO-2026-09-23"),
    ("H", "https://www.linkedin.com/company/ismea",
     "ISMEA — LinkedIn",
     "LINKEDIN",
     "pagina LinkedIn do ISMEA; publicacoes de mercado agricola e dados setoriais; D24",
     "CATEGORIA=CANAL_ORGANIZACIONAL; PAIS_PROVA=ismea.it; D24=DECISOES-DONO-2026-09-23"),
]


def _url_ok(url: str, timeout: int = 12) -> tuple[bool, int]:
    """HEAD request rapido para verificar se URL responde. Devolve (ok, http_code)."""
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "Mozilla/5.0 SintoniaEAME/1.0 (+research)"})
        resp = urllib.request.urlopen(req, timeout=timeout)
        return True, resp.status
    except urllib.error.HTTPError as e:
        # 405 = HEAD nao suportado mas o URL existe; 403 pode ser firewall mas URL existe
        if e.code in (403, 405, 406):
            return True, e.code
        return False, e.code
    except Exception:
        return False, 0


def main():
    registadas = []
    falhas = []
    dedup = []
    total_reqs = 0

    d_antes = FN.carregar()
    urls_existentes = {FN.normalizar(c["URL"]) for c in d_antes["CANDIDATAS"]}

    print("P2 — PESQUISA APLICADA E PROJETOS")
    print("FONTES_ALVO:", len(FONTES))
    print("-" * 60)

    for cat, url, nome, tipo, para_que, nota in FONTES:
        chave = FN.normalizar(url)
        if chave in urls_existentes:
            dedup.append(url)
            print(f"  DEDUP [{cat}] {url[:70]}")
            continue

        total_reqs += 1
        ok, code = _url_ok(url)
        time.sleep(DELAY)

        if ok:
            linha = FN.registar(
                tipo=tipo, pais="IT", nome=nome, url=url,
                para_que=para_que,
                quem_viu=QUEM_VIU,
                onde_viu="catalogo_curado_P2_pesquisa_aplicada",
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
    for cat, url, *_ in FONTES:
        if url in registadas:
            by_cat.setdefault(cat, 0)
            by_cat[cat] += 1
    for cat in sorted(by_cat):
        print(f"  CATEGORIA_{cat}: {by_cat[cat]}")

    if falhas:
        print("\nFALHAS_DETALHE:")
        for u, c in falhas:
            print(f"  HTTP={c} {u}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
