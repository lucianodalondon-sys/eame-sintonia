# -*- coding: utf-8 -*-
"""
AQUISICAO-DETALHE-V1 · PASSO 1 — CLASSIFICAR AS 104 FONTES HTML_LINK_DISCOVERY
COM UMA SO OBSERVACAO NA BCR-2026-09-20.

O que este ficheiro e:
  · o UNIVERSO e CALCULADO (nunca digitado) de curadoria/ESTADO-ACTUAL-DAS-FONTES-V1.json:
        STRATEGY = HTML_LINK_DISCOVERY  AND  BIG_COLLECTION.CLASSE = SUCCESS
        AND BIG_COLLECTION.OBSERVACOES = 1
  · a EVIDENCIA por fonte e LIDA dos registos que ja existem (contrato, sondagem,
    manifesto da amostra, caracterizacao do curator, ledger da BCR, ficha do Atlas);
  · o JUIZO por fonte (classe + criterio) e DECLARADO abaixo, em JUIZOS, e o script
    reprova se faltar juizo a uma fonte do universo ou se sobrar juizo a uma fonte
    que nao esta nele. Ninguem tem de adivinhar porque.

Sem rede. Read-only sobre os registos. Escreve so os dois ficheiros de saida.

  py curadoria/classificar_indice_104.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
ESTADO = RAIZ / "curadoria" / "ESTADO-ACTUAL-DAS-FONTES-V1.json"
ONBOARDED = RAIZ / "regras" / "italy_contracts_onboarded.json"
CURATOR = RAIZ / "curadoria" / "italy_contracts_curator.json"
LEDGER_OBS = RAIZ / "data" / "collection-ledger" / "italy" / "observations.ndjson"
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
SAMPLES = RAIZ / "data" / "samples" / "IT-SOURCE-SAMPLES"
SAIDA_JSON = RAIZ / "curadoria" / "CLASSIFICACAO-INDICE-104-V1.json"
SAIDA_MD = RAIZ / "curadoria" / "CLASSIFICACAO-INDICE-104-V1.md"

CLASSES = ("BOLETIM_SERIADO", "LISTAGEM_DE_NOTICIAS", "NAO_SEI")

# ── OS CRITERIOS — vocabulario fechado, um por decisao ──────────────────────
CRITERIOS = {
    "C1_SERIE_PROVADA_NO_CONTRATO":
        "o LINK_PATTERN do contrato captura numero/data de edicao e o contrato traz "
        "OBSERVED_FREQUENCY provada por edicoes espacadas (contratos HAND do nucleo). "
        "O indice e o arquivo de uma serie; a edicao corrente e a unica que interessa.",
    "C2_SERIE_VISTA_NA_EVIDENCIA":
        "a evidencia guardada (INDEX_URL, sondagem, manifesto da amostra ou alvo da BCR) "
        "mostra duas ou mais edicoes numeradas/datadas da MESMA serie, ou o indice e a "
        "pagina de arquivo de uma serie.",
    "C3_LISTAGEM_VISTA_NA_EVIDENCIA":
        "a evidencia guardada mostra uma pagina de LISTAGEM de itens distintos "
        "(news/notizie/comunicati/category/newsroom/rassegna/eventi/circolari) com HTTP 200, "
        "vinda da sondagem, do manifesto, do curator ou do proprio alvo da BCR.",
    "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA":
        "viram-se itens que o PROPRIO sitio encaminha como noticia (caminho news/notizie/"
        "comunicati/eventi/blog/news-blog) — dois itens distintos, ou um item com data visivel, "
        "ou Atlas SOURCE_TYPE = IMPRENSA — mas a pagina de listagem NAO foi vista. "
        "A listagem fica A_PROVAR no PASSO 2; se nao se provar, a fonte cai para NAO_SEI.",
    "C5_INDICE_E_CAPA_E_ALVO_E_PAPELADA":
        "LOTE-PDF-INDICE: o indice e a capa do sitio (ou uma pagina avulsa) e o LINK_PATTERN "
        "e 'qualquer .pdf na pasta do exemplo'. O unico item visto e papelada administrativa "
        "(estatuto, tarifario, privacidade, brochura, regulamento). O que a fonte PUBLICA como "
        "fluxo nao foi medido: nem boletim, nem listagem de noticias.",
    "C6_SO_PAGINAS_INSTITUCIONAIS":
        "toda a evidencia guardada e de paginas institucionais ou de seccao (documentos, "
        "projetos, publicacoes, avisos de secretaria) sem item datado distinto e sem serie. "
        "Nao da para decidir a familia.",
    "C7_CONTRATO_DUPLICADO":
        "o contrato tem o MESMO INDEX_URL e o MESMO LINK_PATTERN de outro SOURCE_ID; a BCR "
        "trouxe bytes identicos para os dois. A evidencia do Atlas aponta para outro dominio "
        "que o contrato nao cobre. O que ESTE SOURCE_ID e nao se decide pelo contrato como esta.",
}

# ── AS BANDEIRAS — factos medidos, independentes da classe ──────────────────
BANDEIRAS = {
    "ROTA_CAPA": "INDEX_URL e a raiz do dominio (capa institucional).",
    "ROTA_HOME_DE_SECCAO": "INDEX_URL e a home de uma seccao ou de um sitio-filho (/home, /it, /ibbr/): nem a raiz do dominio, nem uma listagem.",
    "ROTA_ARTIGO": "INDEX_URL aponta para UM item (artigo/edicao/documento), nao para uma listagem.",
    "ROTA_LISTAGEM_OK": "INDEX_URL ja e uma pagina de listagem.",
    "PADRAO_SEM_PALAVRA": "LINK_PATTERN da familia 'slug' (3+ palavras) sem directoria de noticia: "
                          "casa com QUALQUER caminho do sitio, e o motor devolve o primeiro href do HTML "
                          "(regras/motor_de_rota.mjs::ligacoesDoIndice) — quase sempre o menu.",
    "PADRAO_PASTA_CONGELADA": "LINK_PATTERN fixa a pasta de uploads de UM mes passado: nunca vera item novo.",
    "PADRAO_OUTRO_DOMINIO": "LINK_PATTERN aponta para um dominio diferente do INDEX_URL.",
    "BCR_ALVO_INSTITUCIONAL": "o item que a BCR colheu e pagina institucional (chi siamo, contatti, sede, "
                              "consiglio, storia, PEC), nao materia.",
    "BCR_ALVO_LISTAGEM": "o item que a BCR colheu e a PROPRIA pagina de listagem, guardada como se fosse conteudo "
                         "(CAPA != MATERIA).",
    "BCR_ALVO_MATERIA": "o item que a BCR colheu e uma materia/edicao real.",
    "BCR_ALVO_PAPELADA_PDF": "o item que a BCR colheu e um PDF administrativo.",
    "INDEX_DUPLICADO": "outro SOURCE_ID tem o mesmo INDEX_URL.",
}

# ── OS JUIZOS — um por fonte do universo ─────────────────────────────────────
# (classe, criterio, bandeiras, listagem_proposta, estado_da_listagem, nota)
#   estado_da_listagem: VISTA (HTTP 200 na evidencia) · A_PROVAR (inferida do caminho) · n/a
J = {}

def j(sid, classe, criterio, bandeiras, listagem=None, estado=None, nota=""):
    assert classe in CLASSES, sid
    assert criterio in CRITERIOS, (sid, criterio)
    for b in bandeiras:
        assert b in BANDEIRAS, (sid, b)
    J[sid] = dict(CLASSIFICACAO=classe, CRITERIO=criterio, BANDEIRAS=list(bandeiras),
                  LISTAGEM_PROPOSTA=listagem, LISTAGEM_ESTADO=estado, NOTA=nota)

# HAND — nucleo regras/italy_contracts.mjs
j("IT-T3-002", "BOLETIM_SERIADO", "C1_SERIE_PROVADA_NO_CONTRATO", ["ROTA_LISTAGEM_OK", "BCR_ALVO_MATERIA"],
  nota="SA-dd-mm.pdf; OBSERVED_FREQUENCY 7D por 14 edicoes.")
j("IT-T3-010", "BOLETIM_SERIADO", "C1_SERIE_PROVADA_NO_CONTRATO", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  nota="Bollettino_Mosca n.10 de 14/09; 7D provado pelas datas dentro dos PDF. A capa e o indice certo aqui: e ela que lista as edicoes.")
j("IT-T3-008", "BOLETIM_SERIADO", "C1_SERIE_PROVADA_NO_CONTRATO", ["ROTA_LISTAGEM_OK", "BCR_ALVO_MATERIA"],
  nota="Notiziario N38 de 16-09; semanal as quartas.")
j("IT-T4-001", "BOLETIM_SERIADO", "C1_SERIE_PROVADA_NO_CONTRATO", ["ROTA_LISTAGEM_OK", "BCR_ALVO_MATERIA"],
  nota="PROD_FTS_6_YYYYMMDD.csv: versoes datadas do MESMO dataset; a corrente e a unica que interessa.")
j("IT-T2-001", "BOLETIM_SERIADO", "C1_SERIE_PROVADA_NO_CONTRATO", ["ROTA_LISTAGEM_OK", "BCR_ALVO_MATERIA"],
  nota="NN_boll_agro_YYYYMMDD.pdf; 7D por 7 edicoes seguidas.")

# TABELA_ONBOARDED · LOTE-HTML-ARTIGO
j("IT-T1-002", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_CAPA", "BCR_ALVO_LISTAGEM"],
  "https://www.provincia.tn.it/News/Comunicati-stampa", "VISTA",
  "sondagem e BCR chegaram a /News/Comunicati-stampa (listagem, guardada como conteudo); manifesto tem item /News/Eventi/ datado 2026-09-10.")
j("IT-T1-003", "NAO_SEI", "C6_SO_PAGINAS_INSTITUCIONAIS", ["PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL", "INDEX_DUPLICADO"],
  nota="so a seccao /regione/approfondimenti e a pagina da PEC foram vistas; nenhum item datado. Mesmo INDEX que IT-T3-015.")
j("IT-T1-005", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_HOME_DE_SECCAO", "BCR_ALVO_MATERIA"],
  "https://www.regione.umbria.it/notizie", "A_PROVAR",
  "dois itens distintos: /in-evidenza/ (bonus ZES) e /notizie/ (165 anniversario).")
j("IT-T1-006", "BOLETIM_SERIADO", "C2_SERIE_VISTA_NA_EVIDENCIA", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  nota="INDEX e a edicao 'valido fino al 4 agosto 2026'; manifesto tem outra edicao do MESMO 'BOLLETTINO agrometeorologico e fitosanitario' datada 2026-09-14. "
       "DIVIDA: a rota aponta a uma edicao velha, nao ao arquivo, e a BCR colheu 'chi siamo'. Nao se toca no PASSO 2 (familia boletim); fica registado.")
j("IT-T1-007", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.arsial.it/bandi-e-avvisi/avvisi-per-enti-pubblici", "VISTA",
  "arquivo de avisos (itens distintos, data visivel 2026-08-31); a BCR colheu /pubblicazioni-e-ricerche. Relevancia nao se julga aqui.")
j("IT-T1-009", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_ARTIGO", "BCR_ALVO_MATERIA"],
  "https://www.regione.lazio.it/notizie/agricoltura", "A_PROVAR",
  "dois itens distintos em /notizie/agricoltura/ (vitivinicolo 2026-2027; FEAMPA datado 2026-08-04). INDEX e a seccao /cittadini/agricoltura.")
j("IT-T1-010", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://www.regione.abruzzo.it/notizie", "A_PROVAR",
  "dois itens distintos em /notizie/ (economia; sanita datado 2026-09-14).")
j("IT-T1-011", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_ARTIGO", "BCR_ALVO_MATERIA"],
  "https://www.regione.umbria.it/agricoltura", "A_PROVAR",
  "um so item visto 3 vezes (legge-serpieri), rotulado 'Notizia' pelo sitio, data 2025-11-10 no Atlas. A seccao /agricoltura e a listagem provavel.")
j("IT-T1-013", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.sementi.it/comunicati_stampa/", "A_PROVAR",
  "dois comunicati distintos em /comunicati_stampa/ (riso; erba medica datado 2026-05-15); a BCR colheu 'le aziende associate'.")
j("IT-T1-016", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.italiaolivicola.it/category/comunicati-stampa/", "VISTA",
  "duas listagens vistas (/category/comunicati-stampa/, /category/news/); data visivel 2023-10-20 — pode estar parada; a BCR colheu 'consiglio di amministrazione'.")
j("IT-T1-018", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.rivistadiagraria.org/articoli/anno-2026/", "A_PROVAR",
  "um artigo em /articoli/anno-2026/; Atlas SOURCE_TYPE = IMPRENSA; a BCR colheu uma seccao ('animali da compagnia').")
j("IT-T1-021", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_LISTAGEM"],
  "https://agronotizie.imagelinenetwork.com/notizie-agricoltura-attualita/", "VISTA",
  "INDEX e UM artigo (agora-fertilizzanti-2026/89672); a BCR colheu a listagem /notizie-agricoltura-attualita/ como conteudo. Atlas IMPRENSA.")
j("IT-T1-022", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://olivonews.it/category/bollettino-olivicolo/", "VISTA",
  "INDEX e a categoria 'bollettino olivicolo'; manifesto tem /category/attualita/ datado 2025-04-27; a BCR colheu 'contatti'. "
       "ATENCAO: a categoria chama-se 'bollettino' — se o canario do PASSO 3 mostrar edicoes numeradas da mesma serie, reclassificar para BOLETIM_SERIADO.")
j("IT-T10-007", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.ismea.it/Press-Area/Comunicati-Stampa", "VISTA",
  "listagem de comunicati datada 2026-09-11; a BCR colheu a pagina institucional do instituto.")
j("IT-T10-009", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://www.bo.camcom.gov.it/it/blog", "A_PROVAR",
  "um item de /it/blog/ (prazo 16/10); o manifesto tem uma PAGINA institucional. Evidencia fraca: a prova da listagem decide.")
j("IT-T10-011", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.ruminantia.it/category/news-dal-mondo-della-ricerca/", "VISTA",
  "duas listagens vistas (/category/news-dal-mondo-della-ricerca/, /category/news/); Atlas IMPRENSA; a BCR colheu 'borse merci'.")
j("IT-T10-013", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.tutelaaranciarossa.it/rassegna-stampa/", "VISTA",
  "rassegna stampa datada 2026-09-14; a BCR colheu 'la storia'.")
j("IT-T11-005", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_MATERIA"],
  "https://www.simei.it/news-media/news", "VISTA",
  "listagem /news-media/news e item distillo-2026; a BCR colheu uma pagina de evento (enovitis) — materia, mas fora da listagem.")
j("IT-T12-004", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.confagricoltura.it/ita/area-stampa/notizie-brevi", "A_PROVAR",
  "INDEX e UMA notizia-breve datada 2026-06-04; a BCR colheu 'la nostra storia'.")
j("IT-T2-006", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "BCR_ALVO_MATERIA"],
  "https://www.arpacampania.it/web/guest/news", "VISTA",
  "a unica das 66 em que rota, padrao e alvo estao certos: so o MAX_TARGETS: 1 perde os outros.")
j("IT-T2-007", "BOLETIM_SERIADO", "C2_SERIE_VISTA_NA_EVIDENCIA", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_LISTAGEM"],
  nota="INDEX e a pagina do bollettino qualita dell'aria (Vulcano); a BCR colheu o ARQUIVO dos bollettini giornalieri (3,8 MB) como conteudo. Serie diaria. "
       "DIVIDA: o arquivo inteiro esta a ser guardado como documento.")
j("IT-T2-008", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://www.arpat.toscana.it/notizie", "A_PROVAR",
  "dois itens distintos (/evento/, /pubblicazione/ datado 2026-08-22); a listagem de notizie nao foi vista.")
j("IT-T2-010", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.appa.provincia.tn.it/News", "A_PROVAR",
  "INDEX e UM documento tecnico; manifesto tem item /News/Approfondimenti/ datado 2026-07-15; a BCR colheu a seccao 'Documenti e dati'.")
j("IT-T2-012", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_CAPA", "BCR_ALVO_LISTAGEM"],
  "https://www.arpa.fvg.it/news/ufficio-stampa/", "VISTA",
  "sondagem e BCR chegaram a /news/ufficio-stampa/ (listagem, guardada como conteudo); manifesto tem item datado 2026-09-09.")
j("IT-T2-013", "NAO_SEI", "C6_SO_PAGINAS_INSTITUCIONAIS", ["PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  nota="so a seccao 'Pubblicazioni RIR' e a pagina da rete micro-meteorologica; nenhum item datado.")
j("IT-T2-017", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.iret.cnr.it/news/", "VISTA",
  "listagem /news/ vista; a BCR colheu a pagina da sede.")
j("IT-T2-019", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.arpa.piemonte.it/ricerca/comunicati-stampa", "VISTA",
  "listagem de comunicati e item /notizia/ (relazione stato ambiente 2026); a BCR colheu um tema (radioattivita).")
j("IT-T2-022", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.arpa.vda.it/component/tags/tag/articoli-scientifici", "VISTA",
  "duas listagens por tag (articoli-scientifici, bollettini); itens nao vistos individualmente; a BCR colheu 'qualita e sicurezza'.")
j("IT-T3-013", "BOLETIM_SERIADO", "C2_SERIE_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  nota="INDEX e o arquivo 'bollettini interprovinciali 2026' (edicoes da mesma serie). DIVIDA: o padrao 'slug' fez a BCR colher 'piani-programmi-progetti'; "
       "e OUTPUT_TYPE HTML quando as edicoes sao provavelmente PDF. Nao se toca no PASSO 2; fica registado.")
j("IT-T3-014", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.protezionedellepiante.it/category/documenti-tecnici-ufficiali/", "VISTA",
  "duas listagens (/category/documenti-tecnici-ufficiali/, /category/articoli/ datada 2026-09-14); a BCR colheu 'area riservata'.")
j("IT-T3-015", "NAO_SEI", "C6_SO_PAGINAS_INSTITUCIONAIS", ["PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL", "INDEX_DUPLICADO"],
  nota="mesma rota e mesma evidencia de IT-T1-003 (Regione Toscana): so seccao e PEC.")
j("IT-T3-016", "NAO_SEI", "C6_SO_PAGINAS_INSTITUCIONAIS", ["PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  nota="so a pagina 'Newsletter' e a pagina PR FESR. Se a pagina for arquivo de edicoes da newsletter, e BOLETIM_SERIADO — mas nenhuma edicao foi vista.")
j("IT-T3-018", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.ispa.cnr.it/news-e-eventi", "VISTA",
  "listagem /news-e-eventi vista; a BCR colheu a pagina da sede de Bari.")
j("IT-T3-019", "NAO_SEI", "C6_SO_PAGINAS_INSTITUCIONAIS", ["BCR_ALVO_INSTITUCIONAL"],
  nota="paginas de projetos de investigacao (PAGINA no manifesto); nem noticia nem serie.")
j("IT-T5-006", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.cnr.it/it/news", "A_PROVAR",
  "INDEX e a seccao 'documenti-programmazione'; manifesto tem item /it/news/14617/ datado 2026-09-11; a BCR colheu 'cnr in numeri'.")
j("IT-T5-015", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_HOME_DE_SECCAO", "BCR_ALVO_MATERIA"],
  "https://www.ibbr.cnr.it/ibbr/news", "A_PROVAR",
  "dois itens distintos em /ibbr/news/ (iscrizioni; biotech week 2026).")
j("IT-T5-024", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_HOME_DE_SECCAO", "BCR_ALVO_MATERIA"],
  "https://disaa.unimi.it/it/eventi", "A_PROVAR",
  "dois itens distintos em /it/eventi/ (festival parco Monza; summer school LCA); manifesto tem 'pubblicazioni' datado 2026-06-18.")
j("IT-T5-025", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_ARTIGO", "BCR_ALVO_MATERIA"],
  "https://www.santannapisa.it/it/news", "A_PROVAR",
  "INDEX e UMA noticia (innoflorenerg, datada 2026-06-24), colhida 3 vezes; a BCR marcou DOCUMENT_CHANGED_IN_PLACE no mesmo artigo (HTML dinamico).")
j("IT-T5-027", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "BCR_ALVO_MATERIA"],
  "https://www.dafnae.unipd.it/news/termine/2", "VISTA",
  "listagem 'news/termine/2' (Bandi) e item node/18429.")
j("IT-T5-028", "NAO_SEI", "C6_SO_PAGINAS_INSTITUCIONAIS", ["PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  nota="so 'pubblicazioni-dipartimento' e 'delegati di dipartimento'.")
j("IT-T5-030", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "BCR_ALVO_LISTAGEM"],
  "https://www.unite.it/UniTE/Bioscienze_e_Tecnologie_Agro-Alimentari_e_Ambientali/News_ed_Eventi_-_Dipartimento_di_Bioscienze_e_tecnologie_agroalimentari_e_ambientali", "VISTA",
  "INDEX e a listagem 'News ed Eventi' (data visivel 2023-10-19 — pode estar parada); a BCR guardou a propria listagem como conteudo.")
j("IT-T5-033", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_HOME_DE_SECCAO", "BCR_ALVO_MATERIA"],
  "https://distal.unibo.it/it/notizie", "A_PROVAR",
  "item /it/notizie/ (giornata sprechi alimentari); manifesto tem a pagina 'bollettino agrofenologico' datada 2025-12-09 — um segundo endpoint possivel, fora deste passo.")
j("IT-T5-034", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL", "INDEX_DUPLICADO"],
  "https://georgofili.it/contenuti/notiziario-accademia", "A_PROVAR",
  "dois itens do 'Notiziario dell'Accademia' (1305, 620); a BCR colheu 'elenco atti'. INDEX partilhado com IT-T5-035 e IT-T5-036.")
j("IT-T5-035", "NAO_SEI", "C7_CONTRATO_DUPLICADO", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL", "INDEX_DUPLICADO"],
  nota="contrato igual ao de IT-T5-034; o Atlas aponta para georgofili.info (notiziario tecnico), dominio que o padrao nao cobre; bytes da BCR identicos aos de T5-034.")
j("IT-T5-036", "NAO_SEI", "C7_CONTRATO_DUPLICADO", ["ROTA_ARTIGO", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL", "INDEX_DUPLICADO"],
  nota="contrato igual ao de IT-T5-034; o Atlas aponta para georgofili.net (articoli), dominio que o padrao nao cobre; bytes da BCR identicos aos de T5-034.")
j("IT-T7-013", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "PADRAO_SEM_PALAVRA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.conaf.it/formazione-professionale-continua/normativa-formazione-professionale-continua/circolari-2/", "VISTA",
  "listagem 'Circolari e Delibere' (data visivel 2022-10-04); a BCR colheu 'consiglio dell'ordine'. Relevancia nao se julga aqui.")
j("IT-T9-009", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_LISTAGEM_OK", "BCR_ALVO_MATERIA"],
  "https://www.cifo.it/newsroom/", "VISTA",
  "newsroom datada 2026-09-14 e item tomato-world-2026: rota, padrao e alvo certos; so o MAX_TARGETS: 1 perde os outros.")
j("IT-T9-011", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://www.koppert.it/notizie-eventi/", "A_PROVAR",
  "item /notizia/ (acari predatori) e seccao /notizie-eventi/newsletter/ vista no manifesto.")

# TABELA_ONBOARDED · LOTE-PDF-INDICE — todas C5
for sid, nota in [
    ("IT-T1-008", "INDEX e uma pagina de rifugi (2022); item = decreto de 2024/08."),
    ("IT-T1-019", "item = estatuto da SIA (2025/01)."),
    ("IT-T10-012", "item = itinerari (2024/04)."),
    ("IT-T10-015", "item = 'pagina per sito web' (2023/07)."),
    ("IT-T12-003", "item = apresentacao institucional 2021 num bucket S3; Atlas: NAO REPRESENTATIVO."),
    ("IT-T12-005", "item = aiuti di stato (2023/01)."),
    ("IT-T12-006", "item = volume 'il futuro dell'agricoltura' (2026/02), 8,5 MB."),
    ("IT-T2-009", "item = certificado ISO 9001."),
    ("IT-T2-011", "item = 'la montagna che cambia' (ottobre 2026)."),
    ("IT-T2-015", "padrao = qualquer .pdf; item = brochure 2021."),
    ("IT-T2-016", "item = tariffario 2026."),
    ("IT-T2-020", "item = modulo reclami; Atlas: NAO REPRESENTATIVO."),
    ("IT-T2-024", "item = indagine conoscitiva 2022, 7,7 MB."),
    ("IT-T3-020", "padrao = qualquer .pdf; item = locandina de evento."),
    ("IT-T5-007", "item = carta della qualita."),
    ("IT-T5-008", "item = informativa newsletter; Atlas: NAO REPRESENTATIVO."),
    ("IT-T5-009", "item = regolamento 2025-26."),
    ("IT-T5-010", "item = capa de 'La Pianura' n.3/2010 — parece periodico, mas uma capa de 2010 nao prova arquivo vivo."),
    ("IT-T5-011", "item = processi e subprocessi dei dipartimenti."),
    ("IT-T5-012", "item = 'ad-agraria' (2026/07)."),
    ("IT-T5-013", "item = QR code do codice SDI."),
    ("IT-T5-014", "item = linee guida internazionalizzazione."),
    ("IT-T5-016", "repositorio AIR: item = guia da interface. O fluxo real (publicacoes) seria OAI-PMH, fora deste passo."),
    ("IT-T5-017", "repositorio FLORE: item = FAQ. Idem."),
    ("IT-T5-019", "repositorio Padova: item = guia rapida IRIS. Idem."),
    ("IT-T5-020", "repositorio IRIS Torino: item = desktop prodotti. Idem."),
    ("IT-T5-022", "item = call N31 (2025/10)."),
    ("IT-T5-023", "item = progetto ACTION (2025/03)."),
    ("IT-T5-026", "padrao = qualquer .pdf; item = bando tutor 2026-2027."),
    ("IT-T5-029", "item = piano operativo 2026-28."),
    ("IT-T9-010", "item = codice etico; Atlas: NAO REPRESENTATIVO."),
    ("IT-T9-012", "item = report curve diffusori (2026/08) — tecnico, mas um so, numa pasta de um mes."),
    ("IT-T9-013", "item = termos de venda; o padrao aponta para certisbelchim.co.uk; Atlas: NAO REPRESENTATIVO."),
]:
    j(sid, "NAO_SEI", "C5_INDICE_E_CAPA_E_ALVO_E_PAPELADA", ["BCR_ALVO_PAPELADA_PDF"], nota=nota)

# SOURCE CURATOR (LOTE-HTML-ARTIGO da adenda 04A)
j("IT-T5-039", "NAO_SEI", "C6_SO_PAGINAS_INSTITUCIONAIS", ["ROTA_CAPA", "BCR_ALVO_INSTITUCIONAL"],
  nota="canario e BCR so viram avisos de secretaria (esami di stato, lezioni ed esami); curator: ritmo NAO SEI, 3 amostras.")
j("IT-T7-017", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://www.riuniteciv.com/news-e-eventi/", "A_PROVAR",
  "dois itens distintos em /news-e-eventi/; curator: 3 datas 2026-05..08, 0,23 itens/semana.")
j("IT-T7-021", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://etvilloresi.it/news/", "A_PROVAR",
  "a BCR colheu um item /news/imprese/ (sversamento naviglio); o canario colhera uma pagina de projeto; curator: ritmo NAO SEI.")
j("IT-T12-009", "NAO_SEI", "C6_SO_PAGINAS_INSTITUCIONAIS", ["ROTA_CAPA", "BCR_ALVO_INSTITUCIONAL"],
  nota="canario e BCR so viram paginas de projetos (europei conclusi; misura 16.1); curator: 'avvisi e bandi', 0,02 itens/semana. A ASSAM publica boletins agrometeo, mas nada disso esta na evidencia guardada.")
j("IT-T7-031", "NAO_SEI", "C6_SO_PAGINAS_INSTITUCIONAIS", ["ROTA_CAPA", "BCR_ALVO_INSTITUCIONAL"],
  nota="canario e BCR colheram a mesma pagina de projeto (being organic); curator viu 4 itens datados ('Report e Dossier') mas nenhuma listagem de noticias foi vista.")
j("IT-T10-018", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_CAPA", "BCR_ALVO_LISTAGEM"],
  "https://www.myfruit.it/news", "A_PROVAR",
  "a BCR colheu a categoria /news/category/fruttivendoli-e-non-solo (listagem) como conteudo; canario colheu item /news/; curator: AGRICULTURAL_NEWS, 2 datas 2026-09-11..17. A listagem geral /news e a A_PROVAR; a categoria ja foi vista com 200.")
j("IT-T12-013", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_ARTIGO", "BCR_ALVO_MATERIA"],
  "https://www.regione.piemonte.it/web/temi/agricoltura", "A_PROVAR",
  "ATENCAO: o motor colhe hoje o Bollettino Ufficiale corrente (serie) porque a palavra 'bollettin' do padrao casa com /governo/bollettino/; o curator caracterizou NOTICIAS de agricoltura (tavolo verde siccita 2026-09-08, 4 datas). "
       "Se a listagem de noticias nao se provar, cai para NAO_SEI; e o padrao tem de deixar de apanhar o Bollettino Ufficiale.")
j("IT-T5-049", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://www.di3a.unict.it/it/notizie", "A_PROVAR",
  "item /it/notizie/ (avvisi esami); curator: DAILY, 0,71 itens/semana, 7 datas 2026-07..09.")
j("IT-T7-033", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://www.chianticlassico.com/news/", "A_PROVAR",
  "dois itens distintos em /news/; curator: 3 datas 2026-02..05.")
j("IT-T10-020", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_CAPA", "BCR_ALVO_LISTAGEM"],
  "https://winenews.it/it/", "A_PROVAR",
  "canario e BCR colheram a seccao /it/rassegna-stampa/dicono-di-noi/ (listagem) como conteudo; curator: 'Non solo Vino: news', 2 datas 2026-08..09. A listagem de noticias propria (nao a rassegna) e a A_PROVAR.")
j("IT-T10-021", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://plantgest.imagelinenetwork.com/it/news", "A_PROVAR",
  "item /it/eventi/ (noce da frutto/63565) e item de news no curator ('Pesco, nuove varieta' 15/09/2026, id 89677).")
j("IT-T8-008", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_CAPA", "BCR_ALVO_LISTAGEM"],
  "https://www.agroalimentarenews.com/notizie/", "A_PROVAR",
  "canario e BCR colheram /notizie/agroalimentarenews/gli-imprenditori-del-gusto/ (245 KB, seccao) como conteudo; curator: 0,0 itens/semana, datas 2014..2027 — cadencia duvidosa; o canario do PASSO 3 decide.")
j("IT-T10-022", "LISTAGEM_DE_NOTICIAS", "C3_LISTAGEM_VISTA_NA_EVIDENCIA", ["ROTA_CAPA", "BCR_ALVO_LISTAGEM"],
  "https://zootecnicainternational.com/news/", "A_PROVAR",
  "a BCR colheu a categoria /news/shows-and-fairs/ (listagem) como conteudo; canario colheu item /news/; curator: 3 datas 2026-05..09.")
j("IT-T7-040", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://www.parmigianoreggiano.it/it/news", "A_PROVAR",
  "dois itens distintos em /it/news/ (console USA; parigi bigfest, 3 MB); curator: 2 datas 2026-07..08.")
j("IT-T7-041", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://www.bonificaromagna.it/news", "A_PROVAR",
  "dois itens distintos em /news/; curator: 5 datas 2025-09..2026-09.")
j("IT-T7-042", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://www.consorziobalsamico.it/news-blog/", "A_PROVAR",
  "dois itens distintos em /news-blog/; curator: WEEKLY, 0,36 itens/semana.")
j("IT-T2-030", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_INSTITUCIONAL"],
  "https://www.nomisma.it/eventi/", "A_PROVAR",
  "canario colheu item /eventi/; a BCR colheu uma pagina de produto (osservatorio immobiliare); curator: WEEKLY, 3 datas 2026-07..09 ('analisi Nomisma').")
j("IT-T7-043", "LISTAGEM_DE_NOTICIAS", "C4_ITENS_DE_NOTICIA_SEM_LISTAGEM_VISTA", ["ROTA_CAPA", "BCR_ALVO_MATERIA"],
  "https://agrofarma.federchimica.it/news-ed-eventi", "A_PROVAR",
  "dois itens distintos em /news-ed-eventi/dettaglio-news/2026/06/07 e /2026/06/08 (a data vai no caminho).")


# ── LEITURA DOS REGISTOS (evidencia calculada, nao digitada) ─────────────────
def carregar(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def universo(estado):
    out = []
    for x in estado["FONTES"]:
        b = x.get("BIG_COLLECTION") or {}
        if x.get("STRATEGY") == "HTML_LINK_DISCOVERY" and b.get("CLASSE") == "SUCCESS" and b.get("OBSERVACOES") == 1:
            out.append(x)
    return out


def e_capa(u):
    p = urlparse(u or "")
    return p.path in ("", "/") and not p.query


def fichas_do_atlas():
    txt = ATLAS.read_text(encoding="utf-8")
    by = {}
    for b in re.split(r"\n(?=#### IT-T)", txt):
        m = re.match(r"#### (IT-T\d+-\d+)", b)
        if m and m.group(1) not in by:
            by[m.group(1)] = b
    def campo(b, nome):
        m = re.search(r"^" + nome + r":\s*(.*?)(?=\n[A-Z_]+:|\n```)", b, re.S | re.M)
        return re.sub(r"\s+", " ", m.group(1)).strip() if m else None
    return {k: {c: campo(v, c) for c in ("SOURCE_TYPE", "UPDATE_FREQUENCY", "REAL_EXAMPLE")} for k, v in by.items()}


def main():
    estado = carregar(ESTADO)
    onb = {x["SOURCE_ID"]: x for x in carregar(ONBOARDED)["FONTES"]}
    cur = {x["SOURCE_ID"]: x for x in carregar(CURATOR)["FONTES"]}
    obs = [json.loads(l) for l in LEDGER_OBS.read_text(encoding="utf-8").splitlines() if l.strip()]
    atlas = fichas_do_atlas()

    uni = universo(estado)
    ids = [x["SOURCE_ID"] for x in uni]
    faltam = sorted(set(ids) - set(J))
    sobram = sorted(set(J) - set(ids))
    if faltam or sobram:
        print("JUIZOS NAO BATEM COM O UNIVERSO — faltam:", faltam, "sobram:", sobram)
        sys.exit(2)

    idx_count = Counter(x["ROUTE"] for x in uni)
    linhas = []
    for x in uni:
        sid = x["SOURCE_ID"]
        bcr = x["BIG_COLLECTION"]
        o = next((o for o in obs if o.get("SOURCE_ID") == sid and o.get("RUN_ID") == bcr["RUN_ID"]), {})
        ob = onb.get(sid, {})
        aq = ob.get("ACQUISITION", {}) if ob else {}
        sond = ob.get("SONDAGEM") or {}
        c = (cur.get(sid) or {}).get("CARACTERIZACAO") or {}
        man = None
        p = SAMPLES / sid / "MANIFEST.json"
        if p.exists():
            try:
                man = carregar(p)
            except Exception:
                man = None
        juizo = J[sid]
        # bandeiras MEDIDAS (calculadas) — conferem-se contra as declaradas
        medidas = set()
        if e_capa(x["ROUTE"]):
            medidas.add("ROTA_CAPA")
        if idx_count[x["ROUTE"]] > 1:
            medidas.add("INDEX_DUPLICADO")
        lp = aq.get("LINK_PATTERN") or ""
        if ob and ob.get("BATCH_ID") == "LOTE-HTML-ARTIGO" and "(?:news|notizie" not in lp and re.search(r"\[a-z0-9\]\+\(\?:-\[a-z0-9\]\+\)\{2,\}", lp) and not re.search(r"/(news|notizie|newsroom|comunicat)[^|]*/\.\+", lp):
            medidas.add("PADRAO_SEM_PALAVRA")
        if ob and ob.get("BATCH_ID") == "LOTE-PDF-INDICE" and re.search(r"/20\d\d/\d\d/|/20\d\d-\d\d/", lp):
            medidas.add("PADRAO_PASTA_CONGELADA")
        try:
            if lp and re.search(r"\^https?://\(?[^/]*", lp):
                host_lp = re.search(r"\^https?://(?:\(www\\\.\)\?)?([A-Za-z0-9\\.\-]+?)/", lp)
                if host_lp:
                    h1 = host_lp.group(1).replace("\\", "").replace("www.", "")
                    h2 = urlparse(x["ROUTE"]).hostname.replace("www.", "")
                    if h1 != h2:
                        medidas.add("PADRAO_OUTRO_DOMINIO")
        except Exception:
            pass
        declaradas = set(juizo["BANDEIRAS"])
        bandeiras = sorted(declaradas | medidas)
        linhas.append({
            "SOURCE_ID": sid,
            "NAME": x["NAME"],
            "ORIGEM_DO_CONTRATO": x["ORIGEM_DO_CONTRATO"],
            "BATCH_ID": x["BATCH_ID"],
            "CLASSIFICACAO": juizo["CLASSIFICACAO"],
            "CRITERIO": juizo["CRITERIO"],
            "BANDEIRAS": bandeiras,
            "LISTAGEM_PROPOSTA": juizo["LISTAGEM_PROPOSTA"],
            "LISTAGEM_ESTADO": juizo["LISTAGEM_ESTADO"],
            "NOTA": juizo["NOTA"],
            "EVIDENCIA": {
                "INDEX_URL": x["ROUTE"],
                "ROUTE_TYPE": x["ROUTE_TYPE"],
                "IDENTITY_KIND": x["IDENTITY_KIND"],
                "OUTPUT_TYPE": ob.get("OUTPUT_TYPE") if ob else None,
                "LINK_PATTERN": lp or None,
                "MAX_TARGETS": aq.get("MAX_TARGETS") if ob else 1,
                "SONDAGEM": {"REGRA": sond.get("REGRA"), "DOCUMENTO": sond.get("DOCUMENTO")} if sond else None,
                "MANIFESTO": {
                    "WHAT_WAS_OBSERVED": (man.get("OBSERVACAO") or {}).get("WHAT_WAS_OBSERVED"),
                    "EXAMPLE_URL": (man.get("REAL_EXAMPLE") or {}).get("EXAMPLE_URL"),
                    "TIPO_ITEM": (man.get("REAL_EXAMPLE") or {}).get("TIPO_ITEM"),
                    "DATA_VISIVEL": (man.get("REAL_EXAMPLE") or {}).get("DATA_VISIVEL"),
                } if man else None,
                "CURATOR": {k: c.get(k) for k in ("ACTIVITY_STATE", "INITIAL_COLLECTION_CADENCE", "EXPECTED_ITEMS_PER_WEEK", "HISTORICAL_DEPTH_OBSERVED", "REPRESENTATIVE_SAMPLE_COUNT", "CANONICAL_EXAMPLE")} if c else None,
                "ATLAS": atlas.get(sid),
                "BCR": {
                    "RUN_ID": bcr["RUN_ID"],
                    "ALVO": o.get("SOURCE_URL"),
                    "OBSERVATION_RESULT": o.get("OBSERVATION_RESULT"),
                    "BYTES": o.get("BYTES"),
                    "MIME_ASSINATURA": o.get("MIME_ASSINATURA"),
                    "DECLARED_FREQUENCY": o.get("DECLARED_FREQUENCY"),
                    "OBSERVED_FREQUENCY": o.get("OBSERVED_FREQUENCY"),
                },
            },
        })

    por_classe = Counter(l["CLASSIFICACAO"] for l in linhas)
    por_criterio = Counter(l["CRITERIO"] for l in linhas)
    por_bandeira = Counter(b for l in linhas for b in l["BANDEIRAS"])
    por_lote = Counter((l["BATCH_ID"] or "HAND", l["CLASSIFICACAO"]) for l in linhas)
    alvo_bcr = Counter(next((b for b in l["BANDEIRAS"] if b.startswith("BCR_ALVO_")), "BCR_ALVO_NAO_CLASSIFICADO") for l in linhas)

    saida = {
        "DATASET": "CLASSIFICACAO-INDICE-104-V1",
        "MISSAO": "AQUISICAO-DETALHE-V1 · PASSO 1",
        "BASE": "907ccd70",
        "LEI": [
            "O universo e calculado de ESTADO-ACTUAL-DAS-FONTES-V1.json (STRATEGY=HTML_LINK_DISCOVERY AND BCR CLASSE=SUCCESS AND OBSERVACOES=1). Nunca digitado.",
            "Classificacao pela evidencia JA GUARDADA; sem rede. NAO_SEI e resultado valido.",
            "Classificar a FORMA do indice (serie vs itens distintos), nunca a relevancia: coletar nao e julgar (COL-LAW-005).",
            "C4 e provisorio: a listagem A_PROVAR tem de ser provada no PASSO 2; se nao se provar, a fonte cai para NAO_SEI.",
            "BOLETIM_SERIADO e NAO_SEI nao se tocam no PASSO 2. Divida registada nao e missao nova.",
        ],
        "UNIVERSO": len(linhas),
        "POR_CLASSE": dict(por_classe),
        "POR_CRITERIO": dict(por_criterio),
        "POR_LOTE_E_CLASSE": {f"{k[0]} · {k[1]}": v for k, v in sorted(por_lote.items())},
        "POR_BANDEIRA": dict(por_bandeira),
        "O_QUE_A_BCR_COLHEU": dict(alvo_bcr),
        "CRITERIOS": CRITERIOS,
        "BANDEIRAS": BANDEIRAS,
        "FONTES": linhas,
    }
    SAIDA_JSON.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")

    # ── a tabela para gente ler ──
    md = []
    md.append("# CLASSIFICACAO-INDICE-104-V1 — PASSO 1 da AQUISICAO-DETALHE-V1\n")
    md.append("> Gerado por `curadoria/classificar_indice_104.py`. Nao editar a mao: editar os JUIZOS no script e correr de novo.\n")
    md.append(f"Universo (calculado): **{len(linhas)}** fontes `HTML_LINK_DISCOVERY` com exactamente 1 observacao SUCCESS na BCR-2026-09-20.\n")
    md.append("## Contagem\n")
    md.append("| classe | fontes |\n|---|---|")
    for k in CLASSES:
        md.append(f"| {k} | {por_classe.get(k, 0)} |")
    md.append("\n| lote · classe | fontes |\n|---|---|")
    for k, v in sorted(por_lote.items()):
        md.append(f"| {k[0]} · {k[1]} | {v} |")
    md.append("\n| criterio | fontes |\n|---|---|")
    for k, v in sorted(por_criterio.items()):
        md.append(f"| {k} | {v} |")
    md.append("\n| o que a BCR colheu (1 item por fonte) | fontes |\n|---|---|")
    for k, v in sorted(alvo_bcr.items()):
        md.append(f"| {k} | {v} |")
    md.append("\n| bandeira | fontes |\n|---|---|")
    for k, v in sorted(por_bandeira.items()):
        md.append(f"| {k} | {v} |")
    md.append("\n## Criterios\n")
    for k, v in CRITERIOS.items():
        md.append(f"- **{k}** — {v}")
    md.append("\n## Bandeiras\n")
    for k, v in BANDEIRAS.items():
        md.append(f"- **{k}** — {v}")
    md.append("\n## As 104, uma a uma\n")
    md.append("| SOURCE_ID | nome | lote | classe | criterio | INDEX_URL hoje | o que a BCR colheu | listagem proposta | estado | bandeiras | nota |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|")
    def esc(s):
        return str(s if s is not None else "—").replace("|", "\\|").replace("\n", " ")
    for l in sorted(linhas, key=lambda l: (CLASSES.index(l["CLASSIFICACAO"]), l["SOURCE_ID"])):
        md.append("| " + " | ".join(esc(v) for v in (
            l["SOURCE_ID"], l["NAME"], l["BATCH_ID"] or "HAND", l["CLASSIFICACAO"], l["CRITERIO"].split("_")[0],
            l["EVIDENCIA"]["INDEX_URL"], l["EVIDENCIA"]["BCR"]["ALVO"], l["LISTAGEM_PROPOSTA"], l["LISTAGEM_ESTADO"],
            ", ".join(l["BANDEIRAS"]), l["NOTA"])) + " |")
    SAIDA_MD.write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")

    print("UNIVERSO", len(linhas))
    print("POR_CLASSE", dict(por_classe))
    print("POR_CRITERIO", dict(por_criterio))
    print("POR_LOTE_E_CLASSE", saida["POR_LOTE_E_CLASSE"])
    print("O_QUE_A_BCR_COLHEU", dict(alvo_bcr))
    print("POR_BANDEIRA", dict(por_bandeira))
    print("escrito:", SAIDA_JSON.relative_to(RAIZ), SAIDA_MD.relative_to(RAIZ))


if __name__ == "__main__":
    main()
