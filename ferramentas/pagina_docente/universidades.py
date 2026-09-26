# -*- coding: utf-8 -*-
"""PAGINA-DO-DOCENTE · o leitor de CADA universidade (as 19 dos 63 prioritarios do SEGUIR-PESQUISADORES).

Cada leitor diz, para a sua universidade:
  ENTRADAS      por onde se chega a lista de docentes. SO enderecos que ja estao nos nossos livros ou bytes
                (PROVA_ENTRADA diz onde). Nenhum endereco inventado: quando o livro so tem a casa do site, a
                ENTRADA e a casa e a lista e DESCOBERTA pelos links dela (1 pedido a mais).
  PADRAO_PESSOA a forma do endereco da pagina de UM docente — so quando medida em bytes reais (P5) ou num
                link real do livro; senao None (NAO SEI: aceita-se qualquer link do mesmo dominio com o nome).
  BLOCO         (inicio, fim) do pedaco da pagina que e DA PESSOA. Fora dele ficam o cabecalho e o rodape,
                onde estao as contas sociais DA UNIVERSIDADE (Milano, Palermo, Verona e Udine: 407 de 407
                paginas reais traziam links de redes sociais fora do bloco; Padova 0 de 71): sem o corte,
                quase todo o docente «teria» redes.
                None = forma NAO medida: o leitor usa o gabarito (links repetidos entre paginas da mesma
                universidade) e o filtro de contas institucionais.
  FORMA         MEDIDA_EM_BYTES (paginas reais guardadas pela P5, 24/09) · SO_ENTRADA (so o endereco de
                entrada e conhecido) · CASA_DO_SITE (so a casa do site esta nos livros).
"""
import re

# DEPARTAMENTO (texto do MUR) -> ENTRADA especifica, quando a universidade tem varias listas por departamento
UNIVERSIDADES = {
    "MILANO": {
        "DOMINIO": "unimi.it",
        "ENTRADAS": [("", "https://disaa.unimi.it/it/dipartimento/contatti/persone")],
        "PROVA_ENTRADA": "bytes P5 (disaa.unimi.it/it/dipartimento/contatti/persone, 387.976 bytes) + link na pagina V04 da ronda 1",
        "PADRAO_PESSOA": r"^https://www\.unimi\.it/(it|en)/(ugov/rubrica/person\d+|ugov/person/[a-z0-9-]+)$",
        "BLOCO": (r"ugov-rubrica--view-mode-full", r"<footer"),
        "CAMPOS": {"SITO_WEB": r'aria-label="Sito web di'},
        # a pagina tem o link ITA /it/ugov/person/<nome>-<sobrenome>: a regra bate em 154 de 165 paginas reais
        # (as 11 outras tem numero no fim ou outro nome); so vale se o nome conferir na pagina
        "CONSTRUIR": ("https://www.unimi.it/it/ugov/person/{primeiro}-{sobrenome}", "medida: 154/165 paginas P5"),
        "FORMA": "MEDIDA_EM_BYTES",
    },
    "PALERMO": {
        "DOMINIO": "unipa.it",
        "ENTRADAS": [("", "https://www.unipa.it/dipartimenti/saaf/?pagina=personale&ruolo=docenti")],
        "PROVA_ENTRADA": "bytes P5 (saaf ?pagina=personale&ruolo=docenti, 552.867 bytes)",
        "PADRAO_PESSOA": r"^https://www\.unipa\.it/persone/docenti/[a-z]/[a-z0-9.]+/?$",
        "BLOCO": (r'id="content"', r'<footer class="footer"'),
        "CAMPOS": {},
        "FORMA": "MEDIDA_EM_BYTES",
    },
    "VERONA": {
        "DOMINIO": "univr.it",
        "ENTRADAS": [("", "https://www.dbt.univr.it/?ent=persona")],
        "PROVA_ENTRADA": "bytes P5 (dbt.univr.it/?ent=persona, 179.712 bytes)",
        "PADRAO_PESSOA": r"^https://www\.dbt\.univr\.it/\?ent=persona&id=\d+$",
        "BLOCO": (r'class="row info-persona"', r'id="footer"'),
        "CAMPOS": {},
        "FORMA": "MEDIDA_EM_BYTES",
    },
    "PADOVA": {
        "DOMINIO": "unipd.it",
        "ENTRADAS": [(r"AGRONOMIA ANIMALI", "https://www.dafnae.unipd.it/category/ruoli/personale-docente"),
                     (r"TERRITORIO E SISTEMI", "https://www.tesaf.unipd.it/category/ruoli/personale-docente")],
        "PROVA_ENTRADA": "bytes P5 (dafnae 75.677 e tesaf 69.174 bytes) + link na pagina V03 da ronda 1",
        "PADRAO_PESSOA": r"^https://www\.(dafnae|tesaf|bca|maps)\.unipd\.it/category/ruoli/personale-docente\?key=[0-9A-F]{32}$",
        "BLOCO": (r'class="sideblock personale', r"<!-- footer -->"),
        "CAMPOS": {},
        "FORMA": "MEDIDA_EM_BYTES",
    },
    "UDINE": {
        "DOMINIO": "uniud.it",
        "ENTRADAS": [("", "https://di4a.uniud.it/it/cercapersone/cercapersone_dept?afferenza=107404")],
        "PROVA_ENTRADA": "bytes P5 (di4a cercapersone_dept, 164.285 bytes) + link no acervo (di4a.uniud.it)",
        "PADRAO_PESSOA": r"^https://di4a\.uniud\.it/it/cercapersone/@@cercapersone_detail\?person-id=[0-9a-f]{32}$",
        "BLOCO": (r'id="content-core"', r'id="viewlet-below-content-body"'),
        "CAMPOS": {"SITO_PERSONALE": r"Sito personale"},
        # a lista vem em paginas de 10 (b_start:int=0,10,...,180 nos bytes P5): segue-se a paginacao dentro do teto
        "PAGINACAO": r"cercapersone_dept\?afferenza=\d+&(amp;)?b_start:int=\d+",
        # o link diz so «Profilo completo»: o nome esta no cartao antes dele (medido nos bytes P5)
        "NOME_NO_CARTAO": True,
        "FORMA": "MEDIDA_EM_BYTES",
    },
    "BOLOGNA": {
        "DOMINIO": "unibo.it",
        "ENTRADAS": [("", "https://distal.unibo.it/it/dipartimento/persone")],
        "PROVA_ENTRADA": "link no acervo (distal.unibo.it, 3 paginas); a forma unibo.it/sitoweb/<nome> esta no livro (P4: 1 em 82)",
        "PADRAO_PESSOA": r"^https://www\.unibo\.it/sitoweb/[a-z0-9.]+/?$",
        # regra de UM exemplo no livro (elena.benedetti9: homonimos levam numero) — fraca; so vale se o nome conferir
        "CONSTRUIR": ("https://www.unibo.it/sitoweb/{primeiro}.{sobrenome}", "1 exemplo no livro (P4)"),
        "BLOCO": None,
        "CAMPOS": {},
        "FORMA": "SO_ENTRADA",
    },
    "Napoli Federico II": {
        "DOMINIO": "unina.it",
        "ENTRADAS": [("", "https://www.agraria.unina.it/il-dipartimento/persone/docenti-e-ricercatori")],
        "PROVA_ENTRADA": "link relativo na pagina V17 da ronda 1 (casa de agraria.unina.it)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "SO_ENTRADA",
    },
    "Politecnica delle MARCHE": {
        "DOMINIO": "univpm.it",
        "ENTRADAS": [("", "http://www.univpm.it/Entra/Engine/RAServePG.php/P/320010010411/T/Docenti-della-facolta-di-Agraria")],
        "PROVA_ENTRADA": "link na pagina P5 d3a.univpm.it/it/node/1518 («DOCENTI A CONTRATTO») e no livro",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "SO_ENTRADA",
    },
    "TERAMO": {
        "DOMINIO": "unite.it",
        "ENTRADAS": [("", "https://www.unite.it/UniTE/Contatti_1/Docenti")],
        "PROVA_ENTRADA": "link no acervo (www.unite.it, 3 paginas)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "SO_ENTRADA",
    },
    "CATANIA": {
        "DOMINIO": "unict.it",
        "ENTRADAS": [("", "https://docenti.smartedu.unict.it/docenti/")],
        "PROVA_ENTRADA": "link no acervo (di3a.unict.it, 13 paginas)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "SO_ENTRADA",
    },
    "BARI": {
        "DOMINIO": "uniba.it",
        "ENTRADAS": [("", "https://www.uniba.it/it/ricerca/dipartimenti/disspa")],
        "PROVA_ENTRADA": "livro (RELATORIO-MATERIA-PRIMA, pessoas-agro-v1)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "SO_ENTRADA",
    },
    "PISA": {
        "DOMINIO": "unipi.it",
        "ENTRADAS": [("", "https://www.agr.unipi.it/")],
        "PROVA_ENTRADA": "livro (104 mencoes; casa do DISAAA-a)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "CASA_DO_SITE",
    },
    "TORINO": {
        "DOMINIO": "unito.it",
        "ENTRADAS": [("", "https://www.disafa.unito.it/")],
        "PROVA_ENTRADA": "livro (45 mencoes; casa do DISAFA)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "CASA_DO_SITE",
    },
    "Cattolica del Sacro Cuore": {
        "DOMINIO": "unicatt.it",
        "ENTRADAS": [("", "https://piacenza.unicatt.it/")],
        "PROVA_ENTRADA": "livro (casa da sede de Piacenza)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "CASA_DO_SITE",
    },
    "TRENTO": {
        "DOMINIO": "unitn.it",
        "ENTRADAS": [("", "https://www.unitn.it/")],
        "PROVA_ENTRADA": "livro (casa do ateneu; o C3A e UniTN+FEM)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "CASA_DO_SITE",
    },
    "MOLISE": {
        "DOMINIO": "unimol.it",
        "ENTRADAS": [("", "https://www.unimol.it/")],
        "PROVA_ENTRADA": "livro (casa do ateneu)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "CASA_DO_SITE",
    },
    'ROMA "La Sapienza"': {
        "DOMINIO": "uniroma1.it",
        "ENTRADAS": [("", "https://www.uniroma1.it/it/pagina-strutturale/home")],
        "PROVA_ENTRADA": "livro (casa do ateneu)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "CASA_DO_SITE",
    },
    "SALERNO": {
        "DOMINIO": "unisa.it",
        "ENTRADAS": [("", "https://www.unisa.it/")],
        "PROVA_ENTRADA": "livro (www.unisa.it/dipartimenti/... no acervo; a casa do mesmo host)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "CASA_DO_SITE",
    },
    "MODENA e REGGIO EMILIA": {
        "DOMINIO": "unimore.it",
        "ENTRADAS": [("", "https://www.unimore.it/it")],
        "PROVA_ENTRADA": "livro (casa do ateneu)",
        "PADRAO_PESSOA": None, "BLOCO": None, "CAMPOS": {}, "FORMA": "CASA_DO_SITE",
    },
}

# palavras que marcam, num link da CASA do site, o caminho para a lista de pessoas (descoberta, 1 pedido)
PISTA_DA_LISTA = re.compile(r"(persone|docenti|personale|rubrica|people|staff|chi-e-dove|cercapersone|faculty)", re.I)
# palavras que marcam, na pagina da pessoa, um link do MESMO dominio que e dela (pagina pessoal/laboratorio)
PISTA_PAGINA_PROPRIA = re.compile(r"(sito\s*(web|personale)|pagina\s*personale|home\s*page|homepage|laborator\w*|"
                                  r"personal\s*(web|page)|research\s*group|gruppo\s*di\s*ricerca)", re.I)


def leitor_de(universidade: str):
    return UNIVERSIDADES.get(universidade)


def entrada_para(universidade: str, departamento: str) -> str:
    u = UNIVERSIDADES[universidade]
    for padrao, url in u["ENTRADAS"]:
        if not padrao or re.search(padrao, departamento or "", re.I):
            return url
    return u["ENTRADAS"][0][1]
