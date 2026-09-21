# -*- coding: utf-8 -*-
"""
AQUISICAO-DETALHE-V1 · PASSO 2 — CORRIGIR SO A FAMILIA DE NOTICIAS, E SO ONDE A ROTA FOI PROVADA

O que este ficheiro faz:
  · le CLASSIFICACAO-INDICE-104-V1.json (o PASSO 1) e PROVA-DE-LISTAGENS-V1.json (a prova de rota);
  · aplica, em regras/italy_contracts_onboarded.json, as CORRECOES declaradas abaixo —
    e SO elas. Cada correcao tem de passar por cinco portoes antes de tocar na linha:
      P1 a fonte e LISTAGEM_DE_NOTICIAS no PASSO 1;
      P2 a listagem foi alcancada com HTTP 200 e mostrou mais de um item (PROVA);
      P3 o LINK_PATTERN novo compila e casa com um item REAL guardado na prova;
      P4 o LINK_PATTERN novo NAO casa com a propria listagem nem com o nao-item declarado
         (o link de menu, a categoria, o Bollettino Ufficiale);
      P5 MAX_TARGETS = min(N medido na prova, TETO) — calculado, nunca digitado;
  · reprova se qualquer linha FORA das correcoes mudar um byte (zero diff nas 8 BOLETIM_SERIADO,
    nas 44 NAO_SEI e nas 31 LISTAGEM nao provadas);
  · escreve curadoria/CONTRATOS-PASSO-2-V1.json: o antes/depois de cada contrato tocado, e o
    porque de cada um dos que ficaram intocados.

  py curadoria/aplicar_passo2.py            # aplica
  py curadoria/aplicar_passo2.py --so-ver   # nao escreve nada; so corre os portoes
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CLASSIF = RAIZ / "curadoria" / "CLASSIFICACAO-INDICE-104-V1.json"
PROVA = RAIZ / "curadoria" / "PROVA-DE-LISTAGENS-V1.json"
TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"
SAIDA = RAIZ / "curadoria" / "CONTRATOS-PASSO-2-V1.json"

# ── O TETO, E PORQUE E 30 ────────────────────────────────────────────────────
# O motor nao pagina: a primeira pagina da listagem e o limite natural do que uma
# corrida ve. Um teto por cima disso existe por tres razoes medidas:
#   1. as maiores listagens provadas anunciam 436 (IBBR), 60 (Riunite), 37 (Myfruit)
#      e 31 (Piemonte) itens — trazer isso tudo e coleta em massa, que esta missao proibe;
#   2. a cadencia mais alta que o curator mediu nestas fontes e 0,71 itens/semana
#      (IT-T5-049): 30 itens cobrem mais de 40 semanas de atraso em qualquer uma;
#   3. o incremental (SEEN_AGAIN) faz a segunda corrida custar zero para o que ja se viu.
# 30 e uma escolha; a razao esta escrita e o numero fica ao lado da medicao que o cortou.
TETO = 30

SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)+"

# ── AS CORRECOES — uma por fonte, com o item real e o nao-item real da prova ─
# INDEX_URL None = fica o que esta. LINK_PATTERN None = fica o que esta.
# CONTAGEM = que numero da prova conta os itens: 'sob' (debaixo do caminho da
# listagem) ou 'padrao' (o padrao actual — teto, porque pode contar menu).
C = {}

def c(sid, index, padrao, contagem, item, nao_item, nota=""):
    C[sid] = dict(INDEX_URL=index, LINK_PATTERN=padrao, CONTAGEM=contagem, ITEM_EXEMPLO=item, NAO_ITEM=nao_item, NOTA=nota)

c("IT-T1-007", None, r"^https?://(www\.)?arsial\.it/bandi-e-avvisi/avvisi-per-enti-pubblici/" + SLUG + r"/?$", "sob",
  "https://www.arsial.it/bandi-e-avvisi/avvisi-per-enti-pubblici/manutenzione-ordianaria-strade-rurali-contributi-2026/",
  "https://www.arsial.it/bandi-e-avvisi/avvisi-per-privati")
c("IT-T1-010", "https://www.regione.abruzzo.it/notizie", r"^https?://(www\.)?regione\.abruzzo\.it/notizie/" + SLUG + r"/?$", "sob",
  "https://www.regione.abruzzo.it/notizie/libera-al-rimborso-240-famiglie-con-malati-oncologici",
  "https://www.regione.abruzzo.it/notizie")
c("IT-T1-016", None, r"^https?://(www\.)?italiaolivicola\.it/\d{4}/\d{2}/\d{2}/[^?#/]+/?$", "padrao",
  "https://www.italiaolivicola.it/2026/05/14/lolio-extravergine-di-oliva-italiano-fa-risparmiare-sufficienti-poche-gocce-di-gusto-e-salute/",
  "https://www.italiaolivicola.it/consiglio-di-amministrazione/",
  "WordPress com permalink datado: o item carrega a data no caminho; o menu nao. O 'padrao' contou menu tambem — e teto.")
c("IT-T1-018", "https://www.rivistadiagraria.org/articoli/anno-2026/", r"^https?://(www\.)?rivistadiagraria\.org/articoli/anno-\d{4}/" + SLUG + r"/?$", "sob",
  "https://www.rivistadiagraria.org/articoli/anno-2026/sapore-della-salute/",
  "https://www.rivistadiagraria.org/sezioni/animali-da-compagnia/",
  "DIVIDA: a listagem e a do ANO 2026; em 2027 a rota tem de rolar (o padrao ja aceita qualquer ano).")
c("IT-T1-022", None, r"^https?://(www\.)?olivonews\.it/" + r"[a-z0-9]+(?:-[a-z0-9]+){4,}" + r"/?$", "padrao",
  "https://olivonews.it/con-il-calo-termico-olive-sempre-piu-recettive-alla-mosca/",
  "https://olivonews.it/contatti-lolivo-news/",
  "WordPress com post na raiz: item e menu tem a mesma forma; distingue-se por 5+ palavras no slug (heuristica declarada). "
  "Os itens da categoria 'bollettino-olivicolo' sao artigos distintos e datados sobre a mosca — se o canario mostrar edicoes numeradas de UM documento, reclassificar.")
c("IT-T10-009", "https://www.bo.camcom.gov.it/it/blog", r"^https?://(www\.)?bo\.camcom\.gov\.it/it/blog/[^?#/]+/?$", "sob",
  "https://www.bo.camcom.gov.it/it/blog/toasia-export-training-emilia-romagna-2026-iscrizioni-entro-il-1010",
  "https://www.bo.camcom.gov.it/it/blog")
c("IT-T2-006", None, None, "padrao", None,
  "https://www.arpacampania.it/web/guest/news",
  "rota e padrao ja estavam certos: so o MAX_TARGETS: 1 perdia os outros 19.")
c("IT-T5-006", "https://www.cnr.it/it/news", r"^https?://(www\.)?cnr\.it/it/news/\d+/[^?#/]+/?$", "sob",
  "https://www.cnr.it/it/news/14635/inf-act-inizia-l-avventura-post-pnrr",
  "https://www.cnr.it/it/cnr-in-numeri")
c("IT-T5-015", "https://www.ibbr.cnr.it/ibbr/news", r"^https?://(www\.)?ibbr\.cnr\.it/ibbr/news/[a-z]+/" + SLUG + r"/?$", "padrao",
  "https://www.ibbr.cnr.it/ibbr/news/announcements/european-biotech-week-2026",
  "https://www.ibbr.cnr.it/ibbr/news/announcements",
  "a listagem anuncia 436 itens de uma vez (arquivo inteiro numa pagina): o TETO corta para 30.")
c("IT-T5-030", None, None, "sob", None, None,
  "rota e padrao (under_example_path) ja estavam certos; a listagem anuncia 11 itens e o contrato trazia 1.")
c("IT-T5-033", "https://distal.unibo.it/it/notizie", r"^https?://distal\.unibo\.it/it/notizie/" + SLUG + r"/?$", "sob",
  "https://distal.unibo.it/it/notizie/il-distal-al-32-international-horticultural-congress-di-kyoto",
  "https://distal.unibo.it/it/notizie/@@multilingual-selector/9e806d4d7a8e474a99a74fc2d660a1f9/it",
  "'sob' contou 13 com dois selectores de lingua (@@) que o padrao exclui: 13 e teto.")
c("IT-T9-009", None, None, "sob",
  "https://www.cifo.it/newsroom/catalogo-cifo-2026-soluzioni-affidabili-ogni-volta/",
  "https://www.cifo.it/newsroom/",
  "rota e padrao ja estavam certos: so o MAX_TARGETS: 1 perdia os outros 14.")
c("IT-T7-017", "https://www.riuniteciv.com/news-e-eventi/", r"^https?://(www\.)?riuniteciv\.com/news-e-eventi/" + SLUG + r"/?$", "sob",
  "https://www.riuniteciv.com/news-e-eventi/cantine-riunite-civ-ottiene-lesg-recognition-da-dnv/",
  "https://www.riuniteciv.com/news-e-eventi/",
  "a listagem anuncia 60 itens: o TETO corta para 30.")
c("IT-T10-018", None, r"^https?://(www\.)?myfruit\.it/news/(?!category/)" + SLUG + r"/?$", "padrao",
  "https://www.myfruit.it/news/pam-panorama-inaugura-a-moncalieri-torino",
  "https://www.myfruit.it/news/category/trend-e-mercati",
  "/news redirecciona para a capa, e a capa lista as noticias: a rota fica a capa e o padrao passa a exigir /news/<slug> sem 'category'. 'padrao' contou categorias tambem — e teto.")
c("IT-T12-013", None, r"^https?://(www\.)?regione\.piemonte\.it/web/temi/agricoltura/[a-z0-9-]+/" + SLUG + r"/?$", "sob",
  "https://www.regione.piemonte.it/web/temi/agricoltura/avversita-calamita-naturali/eventi-calamitosi-mese-agosto-2026",
  "https://www.regione.piemonte.it/governo/bollettino/abbonati/2026/corrente/",
  "BUG DE PADRAO corrigido: a palavra 'bollettin' do padrao generico casava com /governo/bollettino/ e o motor colhia o Bollettino Ufficiale. "
  "O padrao novo so aceita itens dentro de /web/temi/agricoltura/<seccao>/<slug>. 'sob' contou 31 com paginas de seccao de primeiro nivel que o padrao novo exclui: 31 e teto.")
c("IT-T5-049", "https://www.di3a.unict.it/it/notizie", r"^https?://(www\.)?di3a\.unict\.it/it/notizie/" + SLUG + r"/?$", "sob",
  "https://www.di3a.unict.it/it/notizie/avvisi-lezioni",
  "https://www.di3a.unict.it/it/notizie")
c("IT-T7-033", "https://www.chianticlassico.com/news/", r"^https?://(www\.)?chianticlassico\.com/news/" + SLUG + r"/?$", "sob",
  "https://www.chianticlassico.com/news/il-gallo-nero-a-vinitaly-2026/",
  "https://www.chianticlassico.com/news/")
c("IT-T10-022", "https://zootecnicainternational.com/news/", r"^https?://(www\.)?zootecnicainternational\.com/news/[a-z0-9]+(?:-[a-z0-9]+){3,}/?$", "sob",
  "https://zootecnicainternational.com/news/newcastle-disease-hungary-broiler-farms/",
  "https://zootecnicainternational.com/news/shows-and-fairs/",
  "categorias (/news/shows-and-fairs/, /news/company-news/) tem 1-2 hifens; itens tem 3+. Heuristica declarada; 'sob' contou categorias — e teto.")
c("IT-T7-041", "https://www.bonificaromagna.it/news", r"^https?://(www\.)?bonificaromagna\.it/news/" + SLUG + r"/?$", "sob",
  "https://www.bonificaromagna.it/news/registrazione-operatori-economici-su-anac",
  "https://www.bonificaromagna.it/news")
c("IT-T7-042", "https://www.consorziobalsamico.it/news-blog/", r"^https?://(www\.)?consorziobalsamico\.it/news-blog/" + SLUG + r"/?$", "sob",
  "https://www.consorziobalsamico.it/news-blog/domenica-27-settembre-torna-acetaie-aperte/",
  "https://www.consorziobalsamico.it/news-blog/")
c("IT-T7-043", "https://agrofarma.federchimica.it/news-ed-eventi", r"^https?://agrofarma\.federchimica\.it/news-ed-eventi/dettaglio-news/\d{4}/\d{2}/\d{2}/[^?#/]+/?$", "sob",
  "https://agrofarma.federchimica.it/news-ed-eventi/dettaglio-news/2026/06/08/agrofarma-e-federbio-lanciano-il-manifesto-per-il-biocontrollo",
  "https://agrofarma.federchimica.it/news-ed-eventi")

# ── AS 31 LISTAGEM QUE FICAM INTOCADAS, E PORQUE ─────────────────────────────
INTOCADAS = {
    # o portao de robots da casa nao conseguiu LER o robots.txt: nao e recusa, e «nao consegui ver»
    "IT-T10-007": "NAO_ALCANCADA_TRANSPORTE", "IT-T11-005": "NAO_ALCANCADA_TRANSPORTE", "IT-T12-004": "NAO_ALCANCADA_TRANSPORTE",
    "IT-T3-018": "NAO_ALCANCADA_TRANSPORTE", "IT-T9-011": "NAO_ALCANCADA_TRANSPORTE", "IT-T7-040": "NAO_ALCANCADA_TRANSPORTE",
    "IT-T2-030": "NAO_ALCANCADA_TRANSPORTE",
    # a rota que EU inferi do caminho dos itens nao existe (404): ROUTE_NOT_FOUND != SOURCE_BLOCKED
    "IT-T1-013": "ROTA_INFERIDA_NAO_EXISTE_404", "IT-T2-008": "ROTA_INFERIDA_NAO_EXISTE_404",
    "IT-T5-024": "ROTA_INFERIDA_NAO_EXISTE_404", "IT-T10-021": "ROTA_INFERIDA_NAO_EXISTE_404",
    "IT-T5-025": "HTTP_403_NA_LISTAGEM", "IT-T5-034": "HTTP_500_NA_LISTAGEM",
    # a listagem respondeu 200 mas o HTML servido nao anuncia itens (provavel JavaScript, ou redirecciona para um artigo)
    "IT-T1-002": "LISTAGEM_200_SEM_ITENS_NO_HTML", "IT-T1-005": "LISTAGEM_200_SEM_ITENS_NO_HTML",
    "IT-T5-027": "LISTAGEM_200_SEM_ITENS_NO_HTML", "IT-T7-021": "LISTAGEM_200_SEM_ITENS_NO_HTML",
    "IT-T1-021": "LISTAGEM_200_SEM_ITENS_NO_HTML", "IT-T1-009": "LISTAGEM_200_SEM_ITENS_NO_HTML",
    "IT-T1-011": "LISTAGEM_200_SEM_ITENS_NO_HTML",
    # a pagina existe mas os filhos sao sub-seccoes ou paginas numeradas, nao itens
    "IT-T2-010": "HUB_DE_SUBSECCOES", "IT-T2-012": "HUB_DE_SUBSECCOES", "IT-T3-014": "HUB_DE_SUBSECCOES",
    "IT-T8-008": "HUB_DE_SUBSECCOES", "IT-T10-013": "HUB_DE_SUBSECCOES",
    # a sonda so guardou 5 amostras e as 5 eram menu: limitacao da sonda, ja corrigida (HREFS_MESMO_HOST); refazer quando houver orcamento de rede
    "IT-T10-011": "ITENS_NAO_DISTINGUIVEIS_NAS_AMOSTRAS", "IT-T2-017": "ITENS_NAO_DISTINGUIVEIS_NAS_AMOSTRAS",
    "IT-T2-019": "ITENS_NAO_DISTINGUIVEIS_NAS_AMOSTRAS", "IT-T2-022": "ITENS_NAO_DISTINGUIVEIS_NAS_AMOSTRAS",
    "IT-T7-013": "ITENS_NAO_DISTINGUIVEIS_NAS_AMOSTRAS", "IT-T10-020": "ITENS_NAO_DISTINGUIVEIS_NAS_AMOSTRAS",
}
# A regra do PASSO 1 dizia: C4 sem listagem provada cai para NAO_SEI. Aplica-se
# SO onde a listagem foi ALCANCADA (200) e nao mostrou itens — nao onde a rota
# inferida deu 404, nem onde o transporte caiu (isso e «nao consegui ver»).
CAI_PARA_NAO_SEI = {"IT-T1-005", "IT-T7-021", "IT-T1-009", "IT-T1-011"}

NOTAS_EXTRA = {
    "IT-T1-021": "CONTRAPROVA DA MISSAO: o HTML servido de /notizie-agricoltura-attualita/ (61 KB, HTTP 200) anuncia 5 categorias e ZERO artigos. "
                 "Ou a listagem e montada por JavaScript, ou os artigos vivem noutro caminho. O canario do PASSO 3 nao pode terminar nesta pagina; sem itens no HTML, nao se corrige o contrato as cegas.",
    "IT-T1-009": "/notizie/agricoltura redirecciona para UM artigo (avviso-pubblico-promozione-biodistretti): a seccao nao e uma listagem servida em HTML.",
    "IT-T1-011": "/agricoltura lista sub-seccoes (PAC, PNRR, bandi) e uma unica notizia: nao e a listagem de noticias.",
    "IT-T2-012": "candidata para a proxima prova: /news/ufficio-stampa/comunicati-stampa-2026/ (filho visto com 200).",
    "IT-T2-010": "candidata para a proxima prova: /News/Comunicati-stampa ou /News/Approfondimenti (filhos vistos).",
    "IT-T10-013": "os filhos sao /rassegna-stampa/2/, /3/ … (paginacao numerica sem 'page'): os itens sao provavelmente posts na raiz.",
}


def carregar(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def gravar(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def main(so_ver=False):
    classif = carregar(CLASSIF)
    prova = carregar(PROVA)
    tabela = carregar(TABELA)
    antes = copy.deepcopy(tabela)
    classe = {f["SOURCE_ID"]: f["CLASSIFICACAO"] for f in classif["FONTES"]}
    listagem = {sid for sid, k in classe.items() if k == "LISTAGEM_DE_NOTICIAS"}
    pr = {r["SOURCE_ID"]: r for r in prova["RESULTADOS"]}
    linha = {l["SOURCE_ID"]: l for l in tabela["FONTES"]}
    erros = []

    if set(C) & set(INTOCADAS):
        erros.append(f"fonte ao mesmo tempo corrigida e intocada: {sorted(set(C) & set(INTOCADAS))}")
    if (set(C) | set(INTOCADAS)) != listagem:
        erros.append(f"correcoes+intocadas != LISTAGEM: faltam {sorted(listagem - set(C) - set(INTOCADAS))}, sobram {sorted((set(C) | set(INTOCADAS)) - listagem)}")
    if not prova.get("CONTROLO_POSITIVO", {}).get("OK"):
        erros.append("a prova de listagens nao tem controlo positivo OK: nada se aplica")

    tocadas = []
    for sid, fx in C.items():
        r = pr.get(sid)
        l = linha.get(sid)
        if classe.get(sid) != "LISTAGEM_DE_NOTICIAS":
            erros.append(f"{sid}: P1 nao e LISTAGEM_DE_NOTICIAS ({classe.get(sid)})"); continue
        if not r or r.get("HTTP") != 200 or not (r.get("N_SOB_A_LISTAGEM", 0) > 1 or r.get("N_PADRAO_ACTUAL", 0) > 1):
            erros.append(f"{sid}: P2 listagem nao provada na PROVA (HTTP {r and r.get('HTTP')}, sob={r and r.get('N_SOB_A_LISTAGEM')}, padrao={r and r.get('N_PADRAO_ACTUAL')})"); continue
        if not l:
            erros.append(f"{sid}: nao esta na tabela onboarded"); continue
        aq = l["ACQUISITION"]
        novo_index = fx["INDEX_URL"] or aq["INDEX_URL"]
        novo_padrao = fx["LINK_PATTERN"] or aq["LINK_PATTERN"]
        try:
            rx = re.compile(novo_padrao, re.I)
        except re.error as e:
            erros.append(f"{sid}: P3 padrao nao compila: {e}"); continue
        amostras = set(r.get("AMOSTRA_PADRAO_ACTUAL", [])) | set(r.get("AMOSTRA_SOB_A_LISTAGEM", []))
        if fx["ITEM_EXEMPLO"] is not None:
            if fx["ITEM_EXEMPLO"] not in amostras:
                erros.append(f"{sid}: P3 o item-exemplo nao esta nas amostras da prova (exemplo inventado?)"); continue
            if not rx.search(fx["ITEM_EXEMPLO"]):
                erros.append(f"{sid}: P3 o padrao novo NAO casa com o item real {fx['ITEM_EXEMPLO']}"); continue
        elif fx["LINK_PATTERN"] is not None:
            erros.append(f"{sid}: P3 padrao novo sem item-exemplo"); continue
        if rx.search(novo_index.rstrip("/")) or rx.search(novo_index):
            erros.append(f"{sid}: P4 o padrao novo casa com a propria listagem {novo_index}"); continue
        if fx["NAO_ITEM"] is not None and rx.search(fx["NAO_ITEM"]):
            erros.append(f"{sid}: P4 o padrao novo casa com o nao-item {fx['NAO_ITEM']}"); continue
        n = r["N_SOB_A_LISTAGEM"] if fx["CONTAGEM"] == "sob" else r["N_PADRAO_ACTUAL"]
        if n < 2:
            erros.append(f"{sid}: P5 a contagem '{fx['CONTAGEM']}' e {n} — nao ha o que subir"); continue
        novo_max = min(n, TETO)
        registo = {
            "SOURCE_ID": sid, "NAME": l.get("NAME"), "BATCH_ID": l.get("BATCH_ID"),
            "ANTES": copy.deepcopy(aq),
            "DEPOIS": {"STRATEGY": aq["STRATEGY"], "MATCH": aq["MATCH"], "INDEX_URL": novo_index, "LINK_PATTERN": novo_padrao, "MAX_TARGETS": novo_max},
            "PROVA": {"LISTAGEM": r["LISTAGEM_PROPOSTA"], "URL_EFECTIVA": r["URL_EFECTIVA"], "HTTP": r["HTTP"], "BYTES": r["BYTES"],
                      "N_SOB_A_LISTAGEM": r["N_SOB_A_LISTAGEM"], "N_PADRAO_ACTUAL": r["N_PADRAO_ACTUAL"], "CORRIDO_EM": prova["CORRIDO_EM"]},
            "MAX_TARGETS_DERIVACAO": f"min(N_{fx['CONTAGEM'].upper()}={n}, TETO={TETO}) = {novo_max}" + ("  [TETO cortou]" if n > TETO else "") +
                                     ("  [a contagem 'padrao' pode incluir menu: e teto, nao contagem de itens]" if fx["CONTAGEM"] == "padrao" else ""),
            "ITEM_REAL_QUE_O_PADRAO_CASA": fx["ITEM_EXEMPLO"], "NAO_ITEM_QUE_O_PADRAO_EXCLUI": fx["NAO_ITEM"],
            "MUDOU": {"INDEX_URL": novo_index != aq["INDEX_URL"], "LINK_PATTERN": novo_padrao != aq["LINK_PATTERN"], "MAX_TARGETS": novo_max != aq["MAX_TARGETS"]},
            "NOTA": fx["NOTA"],
        }
        tocadas.append(registo)
        if not so_ver:
            aq["INDEX_URL"] = novo_index
            aq["LINK_PATTERN"] = novo_padrao
            aq["MAX_TARGETS"] = novo_max
            l["AQUISICAO_DETALHE_V1"] = {
                "PASSO": 2, "ANTES": registo["ANTES"], "PROVA": registo["PROVA"],
                "MAX_TARGETS_DERIVACAO": registo["MAX_TARGETS_DERIVACAO"], "REGISTO": "curadoria/CONTRATOS-PASSO-2-V1.json",
            }

    # zero diff fora das corrigidas — conferido linha a linha, nao declarado
    tocados_ids = {t["SOURCE_ID"] for t in tocadas}
    for a, d in zip(antes["FONTES"], tabela["FONTES"]):
        if a["SOURCE_ID"] not in tocados_ids and a != d:
            erros.append(f"{a['SOURCE_ID']}: mudou sem ser correcao declarada")
    for k in antes:
        if k != "FONTES" and antes[k] != tabela[k]:
            erros.append(f"cabecalho da tabela mudou: {k}")

    if erros:
        print("PASSO 2 REPROVADO — nada foi escrito:")
        for e in erros:
            print("  ·", e)
        return 2

    intocadas = []
    for sid, motivo in sorted(INTOCADAS.items()):
        r = pr.get(sid, {})
        intocadas.append({"SOURCE_ID": sid, "MOTIVO": motivo, "HTTP": r.get("HTTP"), "N_SOB_A_LISTAGEM": r.get("N_SOB_A_LISTAGEM"),
                          "N_PADRAO_ACTUAL": r.get("N_PADRAO_ACTUAL"), "PORQUE_DA_PROVA": r.get("PORQUE"),
                          "CLASSIFICACAO_APOS_PROVA": "NAO_SEI" if sid in CAI_PARA_NAO_SEI else "LISTAGEM_DE_NOTICIAS (nao provada — contrato intocado)",
                          "NOTA": NOTAS_EXTRA.get(sid, "")})
    from collections import Counter
    saida = {
        "DATASET": "CONTRATOS-PASSO-2-V1", "MISSAO": "AQUISICAO-DETALHE-V1 · PASSO 2",
        "LEI": [
            "So LISTAGEM_DE_NOTICIAS com listagem PROVADA (HTTP 200 e mais de um item) e tocada.",
            "BOLETIM_SERIADO e NAO_SEI: zero diff, conferido linha a linha pelo script.",
            "MAX_TARGETS = min(N medido na prova, TETO=30): calculado; o TETO e escolha com razao escrita.",
            "Mudanca de contrato, nao de codigo. Nenhum switch por SOURCE_ID.",
            "Divergencia da fotografia do curator (italy_contracts_curator.json) e DECLARADA aqui, com o ANTES igual a fotografia — nunca silenciosa.",
        ],
        "TETO": TETO, "TETO_PORQUE": "ver o cabecalho de curadoria/aplicar_passo2.py",
        "CONTRACTS_FIXED": len(tocadas),
        "CONTRACTS_DELIBERATELY_UNTOUCHED": {
            "BOLETIM_SERIADO": sum(1 for k in classe.values() if k == "BOLETIM_SERIADO"),
            "NAO_SEI": sum(1 for k in classe.values() if k == "NAO_SEI"),
            "LISTAGEM_NAO_PROVADA": len(intocadas),
        },
        "LISTAGEM_NAO_PROVADA_POR_MOTIVO": dict(Counter(INTOCADAS.values())),
        "CAI_PARA_NAO_SEI_APOS_PROVA": sorted(CAI_PARA_NAO_SEI),
        "MAX_TARGETS_DEPOIS": dict(Counter(t["DEPOIS"]["MAX_TARGETS"] for t in tocadas)),
        "TOCADAS": tocadas,
        "INTOCADAS": intocadas,
    }
    if so_ver:
        print("SO_VER: portoes passaram para", len(tocadas), "correcoes; nada escrito")
    else:
        gravar(TABELA, tabela)
        gravar(SAIDA, saida)
        print("escrito:", TABELA.relative_to(RAIZ), SAIDA.relative_to(RAIZ))
    print("CONTRACTS_FIXED", len(tocadas), "| intocadas LISTAGEM", len(intocadas), "| MAX_TARGETS_DEPOIS", saida["MAX_TARGETS_DEPOIS"])
    print("motivos das intocadas", saida["LISTAGEM_NAO_PROVADA_POR_MOTIVO"])
    return 0


if __name__ == "__main__":
    sys.exit(main(so_ver="--so-ver" in sys.argv))
