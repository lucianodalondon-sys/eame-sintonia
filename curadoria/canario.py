#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canario por familia: executar o contrato contra a rede real.

    UM CONTRATO VALIDO NAO E UM CONTRATO QUE FUNCIONA.
    A validacao prova que esta bem escrito. O canario prova que resolve.

Nao se faz um canario por fonte: quando o lote e estruturalmente igual, um
canario que passa em N fontes representa as restantes — e um que falha em
todas acusa o LOTE, nao a fonte. Por isso corre-se uma amostra por familia e
aumenta-se se houver desacordo entre elas.

⚠️ E QUANDO FALHA, A PRIMEIRA PERGUNTA NAO E SOBRE A FONTE.
Esta casa ja gastou uma corrida inteira a concluir «o Facebook bloqueia-nos»
quando o defeito era um `Safari/537.36` no User-Agent. Por isso toda falha
passa por um CONTROLO: se um endereco que TEM de funcionar tambem falha, o
veredito e CLIENT_FAILURE e a fonte fica ilibada.

    ANTES DE DECLARAR SOURCE_FAILURE, PROVAR QUE O LEITOR FUNCIONA.

Vocabulario de falha (nunca so «falhou»):

    SOURCE_FAILURE     a fonte respondeu e o que veio nao serve
    CLIENT_FAILURE     o nosso leitor esta avariado (controlo tambem falhou)
    ROUTE_FAILURE      o contrato resolve para o sitio errado
    CAPABILITY_GAP     faltaria capacidade que nao temos
    ENVIRONMENT_GAP    rede/egresso/DNS
    UNKNOWN            nao se conseguiu decidir
"""
from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import capturador as CAP  # noqa: E402  (UA ja medido: sem `Safari/`)
import retrato_html as RH  # noqa: E402  (o gate CAPA != MATERIA, mesmos limiares do coletor)

TIMEOUT = 25
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# ⚠️ CONTROLOS POSITIVOS: enderecos que TEM de funcionar. Se um destes falhar
# na mesma corrida, o problema e nosso e nenhuma fonte deve ser condenada.
CONTROLO = {
    "LOTE-YOUTUBE-FEED": ("https://www.youtube.com/feeds/videos.xml"
                          "?channel_id=UCUs2Mg7jvUTRt7_MSOFYM5Q"),   # IT-T8-001
    "LOTE-HTML-ARTIGO": "https://www.provincia.tn.it/",              # IT-T1-002
    "LOTE-YOUTUBE-CANAL": ("https://www.youtube.com/channel/"
                           "UCUs2Mg7jvUTRt7_MSOFYM5Q/videos"),         # IT-T8-001, rota do canal
}


def buscar(url: str) -> tuple[int, bytes, str]:
    req = urllib.request.Request(url, headers={
        "User-Agent": CAP.UA, "Accept": "*/*", "Accept-Language": "it-IT,it;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
            return r.status, r.read(4_000_000), ""
    except urllib.error.HTTPError as e:
        return e.code, b"", "HTTP %d" % e.code
    except Exception as e:
        return 0, b"", "%s: %s" % (type(e).__name__, str(e)[:90])


def canario_youtube(c: dict) -> dict:
    """Resolve o feed e prova que dele sai um ITEM com identidade."""
    aq = c["ACQUISITION"]
    st, b, err = buscar(aq["FEED_URL"])
    if st != 200 or not b:
        return {"PASS": False, "CLASSE": "UNKNOWN", "PORQUE": err or "HTTP %s" % st,
                "HTTP": st}
    entradas = re.findall(rb"<entry>(.*?)</entry>", b, re.S)
    if not entradas:
        return {"PASS": False, "CLASSE": "SOURCE_FAILURE", "HTTP": st,
                "PORQUE": "feed sem <entry> — EMPTY_LIST, como o contrato preve"}
    e = entradas[0]
    vid = re.search(rb"<yt:videoId>([^<]+)</yt:videoId>", e)
    pub = re.search(rb"<published>([^<]+)</published>", e)
    if not vid:
        return {"PASS": False, "CLASSE": "SOURCE_FAILURE", "HTTP": st,
                "PORQUE": "entry sem videoId — sem identidade, FAILED"}
    # ⚠️ O CANAL DECLARADO TEM DE SER O CANAL QUE RESPONDEU — MAS CUIDADO COM
    # A PRIMEIRA OCORRENCIA. Medido no feed real: a PRIMEIRA <yt:channelId> do
    # documento vem SEM o prefixo `UC` (`Ji1Vrelq8obdmS_UXP3T2g`, a par de
    # `<id>yt:channel:Ji1Vrel...</id>`), e as 16 seguintes, uma por video, vem
    # completas (`UCJi1Vrelq8obdmS_UXP3T2g`). Um `search()` ingenuo apanha a
    # anomala e conclui «o feed respondeu por outro canal» — 4 em 4 fontes
    # condenadas por um prefixo que o proprio YouTube omite no cabecalho.
    #
    #     UMA FALHA UNIFORME ACUSA O LEITOR, NAO AS FONTES.
    #     O controlo positivo tinha passado: logo, o defeito era meu.
    #
    # Compara-se com o conjunto de todos os channelId vistos, aceitando tambem
    # a forma sem prefixo.
    vistos = {x.decode() for x in re.findall(rb"<yt:channelId>([^<]+)</yt:channelId>", b)}
    esperado = aq["CHANNEL_ID"]
    if vistos and not (esperado in vistos or esperado[2:] in vistos):
        return {"PASS": False, "CLASSE": "ROUTE_FAILURE", "HTTP": st,
                "PORQUE": "o feed respondeu por outro canal: %s" % sorted(vistos)[:2]}
    return {"PASS": True, "CLASSE": "OK", "HTTP": st,
            "DOCUMENT_ID": c["IDENTITY"]["DOCUMENT_ID"].replace(
                "{video.videoId}", vid.group(1).decode()),
            "ITENS_NO_FEED": len(entradas),
            "PRIMEIRO_PUBLISHED": pub.group(1).decode()[:10] if pub else "NAO SEI"}


# ── O CANAL YOUTUBE PELA ROTA QUE O COLETOR USA (LEGACY-99 B, 25/09/2026) ──────
# ⚠️ MEDIDO: as 41 YouTube READY_LEGACY tinham no Curator a rota `feeds/videos.xml`,
# e o robots do YouTube proibe-a — VALIDATE_ROUTE: «o endereco do contrato casa com
# Disallow no robots vivo». O coletor ja colhe pela pagina publica do canal
# (CUSTOM_ADAPTER `CANAL_PUBLICO_YOUTUBE_V1`, tabela onboarded). O Curator passa a
# provar ESSA rota: a aba /videos do canal, um pedido.
YOUTUBE_CANAL = "CANAL_PUBLICO_YOUTUBE_V1"


def url_do_canal(channel_id: str) -> str:
    return "https://www.youtube.com/channel/%s/videos" % channel_id


def url_da_rota(aq: dict) -> str | None:
    """O endereco que o portao do anfitriao (robots) tem de deixar: o dono e aqui,
    para o VALIDATE_ROUTE e o canario lerem o MESMO."""
    if aq.get("STRATEGY") == "CUSTOM_ADAPTER" and aq.get("ADAPTER_ID") == YOUTUBE_CANAL:
        return url_do_canal(aq["CHANNEL_ID"]) if aq.get("CHANNEL_ID") else None
    return aq.get("FEED_URL") or aq.get("INDEX_URL")


def canario_youtube_canal(c: dict) -> dict:
    """A pagina /videos do canal responde, e do canal certo, e dela sai um video com
    identidade. Nao abre o video: a regua dos 4 passos e de HTML, e decidir se um
    video e «materia» e pergunta da regua, nao deste canario."""
    aq = c["ACQUISITION"]
    cid = aq.get("CHANNEL_ID") or ""
    st, b, err = buscar(url_do_canal(cid))
    if st != 200 or not b:
        return {"PASS": False, "CLASSE": "UNKNOWN", "PORQUE": err or "HTTP %s" % st, "HTTP": st}
    if cid.encode() not in b:
        return {"PASS": False, "CLASSE": "ROUTE_FAILURE", "HTTP": st,
                "PORQUE": "a pagina nao e do canal %s" % cid}
    vids = list(dict.fromkeys(re.findall(rb'"videoId":"([A-Za-z0-9_-]{11})"', b)))
    if not vids:
        return {"PASS": False, "CLASSE": "SOURCE_FAILURE", "HTTP": st,
                "PORQUE": "canal sem videos na aba /videos — EMPTY_LIST"}
    modelo = ((c.get("IDENTITY") or {}).get("DOCUMENT_ID")
              or "%s:YT:{video.videoId}" % c.get("SOURCE_ID", "?"))
    return {"PASS": True, "CLASSE": "OK", "HTTP": st, "ROTA": "CANAL_PUBLICO",
            "DOCUMENT_ID": modelo.replace("{video.videoId}", vids[0].decode()),
            "ITENS_NO_CANAL": len(vids), "DETAIL_ENUMERATED": len(vids)}


def _regua_manda(source_id) -> bool:
    """V1A: le o dono (ready_split.regua_manda). Import tardio: ready_split le o
    livro do lifecycle, e o canario nao precisa dele para mais nada."""
    import ready_split as RS  # noqa: PLC0415
    return RS.regua_manda(source_id)


def hrefs_da_entrada(b: bytes, index_url: str, strip_suffix: str | None = None) -> set[str]:
    """Os enderecos que o canario ve numa pagina de entrada. UM so dono: o
    reparo de contratos (reparar_contrato.py) infere o padrao sobre ESTE
    conjunto, para propor exactamente o que o canario vai casar depois.

    D47 (T2-BOLETINS): `strip_suffix` e o `ACQUISITION.STRIP_SUFFIX` do contrato, o MESMO corte que
    o coletor ja faz (`regras/motor_de_rota.mjs` · ligacoesDoIndice). Medido na ARPAE: as 60
    ligacoes dos boletins agrometeo acabam em `.pdf/view` (a pagina do Plone); sem o `/view` e o
    PDF. Sem este corte o canario abria a pagina e o coletor o PDF — dois alvos diferentes."""
    # ⚠️ IA-CUR (24/09): a ligacao RELATIVA sem barra («news_open.php?EW_ID=15142») era
    # descartada, e o `&amp;` do HTML ficava literal. Medido na Assomao: a listagem tem 44
    # noticias e o canario via 0 — e a R1 dizia SEM_FAMILIA_DE_ITENS pela mesma razao (le por
    # este leitor). Resolve-se contra o endereco da pagina, como um navegador faz.
    # `mailto:`, `javascript:`, `tel:` e afins continuam fora.
    import html as _html
    from urllib.parse import urljoin
    texto = b.decode("utf-8", "replace")
    hrefs = set()
    for h in re.findall(r'href=["\']([^"\']+)["\']', texto):
        h = _html.unescape(h).strip()
        if re.match(r"^[a-z][a-z0-9+.-]*:", h, re.I) and not h.lower().startswith(("http:", "https:")):
            continue
        # ⚠️ Medido no livro inteiro (24/09): uma ligacao malformada («http://[x»)
        # faz o urljoin rebentar com ValueError — e o canario inteiro da fonte caia
        # em excecao. O leitor antigo nunca rebentava; esta ligacao salta-se.
        try:
            h = urljoin(index_url, h)
        except ValueError:
            continue
        # ⚠️ UM LINK MALFORMADO NA PAGINA NAO PODE DERRUBAR O REPARO (LEGACY-99, 25/09):
        # IT-T12-019 (ersaf.lombardia.it) trazia um href com «[» e o `urlparse` do
        # reparo rebentava com «ValueError: Invalid IPv6 URL» (reparar_contrato.familias).
        # Este e o dono unico do conjunto: o que nao se consegue ler como endereco sai
        # aqui, e nenhum consumidor a jusante tem de se proteger sozinho.
        try:
            p = urlparse(h)
            p.hostname, p.port  # noqa: B018 — so validar: ambos levantam ValueError se malformado
        except ValueError:
            continue
        if h.startswith(("http://", "https://")):
            h = h.split("#")[0]
            if strip_suffix and h.endswith(strip_suffix):
                h = h[:-len(strip_suffix)]
            hrefs.add(h)
    return hrefs


PDF_GATE_VERSAO = "PDF_TEXT_LAYER/v1"
PDF_MINIMO_DE_TEXTO = 800        # a mesma exigencia de corpo do HTML (BODY_UTIL: >= 800 caracteres)


def textos_das_ligacoes(b: bytes, index_url: str, strip_suffix: str | None = None) -> dict:
    """DA-13: o texto de cada ligacao da entrada, pelo mesmo endereco que `hrefs_da_entrada` devolve — o
    que o motor do coletor le como LINK_TEXT (`regras/motor_de_rota.mjs` · textosDasLigacoes). Latin-1, como
    o motor le o indice; etiquetas fora; varias ligacoes para o mesmo endereco juntam-se com « | »."""
    import html as _html
    from urllib.parse import urljoin
    texto = b.decode("latin-1")
    textos: dict = {}
    for h, corpo in re.findall(r'<a\b[^>]*?href\s*=\s*["\']([^"\'#]+)["\'][^>]*>([\s\S]*?)</a>', texto, re.I):
        h = _html.unescape(h).strip()
        try:
            u = urljoin(index_url, h).split("#")[0]
        except ValueError:
            continue
        if strip_suffix and u.endswith(strip_suffix):
            u = u[:-len(strip_suffix)]
        t = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", corpo))).strip()
        if not t:
            continue
        ja = textos.get(u)
        if not ja:
            textos[u] = t
        elif t not in ja.split(" | "):
            textos[u] = ja + " | " + t
    return textos


def _canario_pdf(c: dict, alvo: str, alvos: list, st2: int, b2: bytes, texto_da_ligacao: str = "") -> dict:
    """D32 (4): o item de um contrato OUTPUT_TYPE=PDF, julgado pela ESTEIRA DE PDF que ja existe.

    O texto sai pelo mesmo executor da Collection (`coleta/executor_texto_de_pdf.extrair`,
    pdftotext) — nenhum segundo extractor. Tres saidas, como la:
      TEXT_LAYER_PRESENT com >= PDF_MINIMO_DE_TEXTO caracteres -> PASS (a regua decide READY);
      TEXT_LAYER_ABSENT (e imagem, NEEDS_OCR) ou pouco texto  -> SOURCE_FAILURE, com o porque;
      EXTRACTION_ERROR (a ferramenta falhou/nao existe)      -> UNKNOWN: problema nosso, nao da fonte.
    """
    import hashlib
    import importlib.util
    import tempfile
    base_r = {"HTTP": st2, "ALVO": alvo, "ALVOS_DESCOBERTOS": len(alvos),
              "DETAIL_ENUMERATED": len(alvos), "DETAIL_GATE": PDF_GATE_VERSAO, "BYTES": len(b2)}
    if b2.lstrip()[:5] != b"%PDF-":
        return dict(base_r, PASS=False, CLASSE="SOURCE_FAILURE", DETAIL_GATE_PASSED=False,
                    PORQUE="o contrato diz PDF e os bytes nao sao PDF — BYTE_VALIDATION_FAILED")
    spec = importlib.util.spec_from_file_location(
        "executor_texto_de_pdf", RAIZ / "coleta" / "executor_texto_de_pdf.py")
    ex = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ex)
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "item.pdf"
        p.write_bytes(b2)
        texto, estado, erro, med = ex.extrair(p)
    chars = int((med or {}).get("NON_WHITESPACE_CHARACTERS") or 0)
    item = {"URL": alvo, "HTTP": st2, "BYTES": len(b2), "DOC_KIND": "PDF", "TEXT_LAYER": estado,
            "TEXT_CHARACTERS": chars,
            "TEXT_SHA256": hashlib.sha256(texto.encode("utf-8")).hexdigest() if texto else None}
    base_r["ITEM_ABERTO"] = item
    if estado == ex.art.EXTRACTION_ERROR:
        return dict(base_r, PASS=False, CLASSE="UNKNOWN", DETAIL_GATE_PASSED=False,
                    PORQUE="a extracao do PDF falhou (problema nosso, nao da fonte): %s" % (erro or "?")[:120])
    if estado != ex.art.TEXT_LAYER_PRESENT:
        return dict(base_r, PASS=False, CLASSE="SOURCE_FAILURE", DETAIL_GATE_PASSED=False,
                    PORQUE="o PDF abriu e nao tem camada de texto (e imagem) — NEEDS_OCR")
    if chars < PDF_MINIMO_DE_TEXTO:
        return dict(base_r, PASS=False, CLASSE="SOURCE_FAILURE", DETAIL_GATE_PASSED=False,
                    PORQUE="o PDF tem so %d caracteres de texto (< %d) — sem BODY util"
                           % (chars, PDF_MINIMO_DE_TEXTO))
    # D47 (T2-BOLETINS): a identidade (e os tempos que ela declara) vem do MOTOR DO COLETOR, como na
    # «pagina e o boletim» — um motor so. Antes: um `replace("{doc.1}", caminho)` a mao, que so sabia
    # o molde por endereco e ignorava SOURCE_DATE_ISO/FACT_TIME de um contrato com capturas.
    ident = identidade_pelo_motor(c, alvo, b2, texto_da_ligacao)
    if ident.get("ERRO"):
        return dict(base_r, PASS=False, CLASSE="UNKNOWN", DETAIL_GATE_PASSED=False,
                    PORQUE="o motor do coletor nao deu identidade: %s" % str(ident["ERRO"])[:160])
    if not ident.get("DOCUMENT_ID"):
        return dict(base_r, PASS=False, CLASSE="SOURCE_FAILURE", DETAIL_GATE_PASSED=False,
                    PORQUE="IDENTITY_FAILED: as capturas do contrato nao casam com o alvo")
    return dict(base_r, PASS=True, CLASSE="OK", DETAIL_GATE_PASSED=True, DOCUMENT_ID=ident["DOCUMENT_ID"],
                TEXTO_DA_LIGACAO=texto_da_ligacao, TEMPOS=tempos_do_motor(ident))


FORMA_PAGINA_E_BOLETIM = "PAGINA_E_BOLETIM"
BOLETIM_GATE_VERSAO = "PAGINA_BOLETIM/v1"
BOLETIM_MINIMO = 300     # caracteres sem espaco no recorte do boletim (um boletim curto ainda e boletim)


# D61/D62: os seis campos de data e lugar que o motor devolve quando o contrato declara BASES — os
# nomes da fronteira (coleta/ingresso.py). A data de COLETA vai a parte e nunca preenche nenhum.
CAMPOS_DATA_E_LUGAR = ("PUBLISHED_AT", "PUBLISHED_AT_BASIS", "FACT_TIME", "FACT_TIME_BASIS",
                       "FACT_LOCATION", "FACT_LOCATION_BASIS",
                       "BULLETIN_PERIOD", "BULLETIN_PERIOD_BASIS")   # D69: o periodo do boletim, como evidencia


def declara_data_e_lugar(c: dict) -> bool:
    """O contrato entra no modo D61/D62 (declara pelo menos uma BASE de data/lugar)?"""
    ident = c.get("IDENTITY") or {}
    return any(ident.get(k) is not None for k in ("PUBLISHED_AT_BASIS", "FACT_TIME_BASIS", "FACT_LOCATION_BASIS",
                                                  "BULLETIN_PERIOD_BASIS"))


def tempos_do_motor(ident: dict) -> dict:
    """O que o canario mostra de data e lugar: os seis campos, tal como o motor os deu (D61/D62), ou —
    num contrato antigo sem BASE — o que ele tinha, com NAO SEI e o porque onde nao ha nada."""
    if ident.get("PUBLISHED_AT_BASIS"):
        t = {k: ident.get(k) for k in CAMPOS_DATA_E_LUGAR}
    else:
        pub = ident.get("SOURCE_DATE_ISO") or ident.get("SOURCE_DATE")
        t = {"PUBLISHED_AT": pub if pub and pub != "UNKNOWN" else "NAO SEI",
             "PUBLISHED_AT_BASIS": ("SOURCE_DATE_ISO do contrato (sem BASE declarada)" if pub and pub != "UNKNOWN"
                                    else "NAO SEI · o contrato nao declara onde o boletim diz a emissao"),
             "FACT_TIME": ident.get("FACT_TIME") or "NAO SEI",
             "FACT_TIME_BASIS": "NAO SEI · o contrato nao declara FACT_TIME_BASIS",
             "FACT_LOCATION": "NAO SEI",
             "FACT_LOCATION_BASIS": "NAO SEI · o contrato nao declara a area do boletim",
             "BULLETIN_PERIOD": "NAO SEI",
             "BULLETIN_PERIOD_BASIS": "NAO SEI · o contrato nao declara o periodo do boletim"}
    t["COLLECTION_TIME"] = "CAPTURED_AT do coletor (nunca no lugar dos outros)"
    return t


def identidade_pelo_motor(c: dict, url: str, b: bytes, texto_da_ligacao: str = "") -> dict:
    """A identidade do documento pelo MOTOR DO COLETOR (regras/motor_de_rota.mjs) — um motor so.
    DA-13: `texto_da_ligacao` e o texto do link do indice (LINK_TEXT), como o coletor o poe no alvo."""
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "pagina.bin"
        p.write_bytes(b)
        pedido = {"SOURCE_ID": c["SOURCE_ID"], "CONTRATO": c, "BYTES_EM": str(p),
                  "ALVO": {"url": url, "nome": (c.get("ACQUISITION") or {}).get("NAME") or url.rstrip("/").split("/")[-1],
                           "textoDaLigacao": texto_da_ligacao}}
        r = subprocess.run(["node", str(RAIZ / "regras" / "identidade_do_motor_cli.mjs")],
                           input=json.dumps(pedido), capture_output=True, text=True, encoding="utf-8", timeout=60)
    linha = (r.stdout.strip().splitlines() or ["{}"])[-1]
    try:
        return json.loads(linha)
    except ValueError:
        return {"ERRO": "o motor nao respondeu JSON: %s" % (r.stderr or linha)[-200:]}


def canario_pagina_boletim(c: dict) -> dict:
    """D42 (2): A PAGINA E O BOLETIM. A URL fixa nao identifica a edicao: quem a identifica e a data
    comprovada (+ a impressao do conteudo recortado, para deduplicar). O canario abre a pagina uma
    vez e pergunta ao MOTOR do coletor: sai identidade? o recorte do boletim tem corpo?
      PASS            identidade construida e recorte com >= BOLETIM_MINIMO caracteres
      SOURCE_FAILURE  sem o recorte / sem corpo / nao e HTML (a fonte nao tem o boletim ali)
      UNKNOWN         o motor nao respondeu (problema nosso)
    A data ausente NAO reprova: fica UNKNOWN (nunca a data de coleta) e o passo DATA_COMPROVADA diz."""
    aq = c.get("ACQUISITION") or {}
    url = aq.get("URL")
    st, b, err = buscar(url)
    base_r = {"HTTP": st, "ALVO": url, "DETAIL_GATE": BOLETIM_GATE_VERSAO, "BYTES": len(b or b""),
              "DETAIL_ENUMERATED": 1}
    if st != 200 or not b:
        return dict(base_r, PASS=False, CLASSE="UNKNOWN", PORQUE=err or "HTTP %s" % st)
    if not b.lstrip().removeprefix(b"\xef\xbb\xbf")[:1] == b"<":
        return dict(base_r, PASS=False, CLASSE="SOURCE_FAILURE", DETAIL_GATE_PASSED=False,
                    PORQUE="bytes nao sao HTML — BYTE_VALIDATION_FAILED")
    ident = identidade_pelo_motor(c, url, b)
    if ident.get("ERRO"):
        return dict(base_r, PASS=False, CLASSE="UNKNOWN", DETAIL_GATE_PASSED=False,
                    PORQUE="o motor recusou: %s" % ident["ERRO"][:160])
    item = {"URL": url, "HTTP": st, "BYTES": len(b), "FORMA": FORMA_PAGINA_E_BOLETIM,
            "DOCUMENT_ID": ident.get("DOCUMENT_ID"), "CONTENT_SHA256": ident.get("CONTENT_SHA256"),
            "SOURCE_DATE": ident.get("SOURCE_DATE"), "SOURCE_DATE_ISO": ident.get("SOURCE_DATE_ISO"),
            "FACT_TIME": ident.get("FACT_TIME"), "BOLETIM_CARACTERES": ident.get("BOLETIM_CARACTERES", 0),
            "DATA_COMPROVADA": bool(ident.get("SOURCE_DATE_ISO")) and ident.get("SOURCE_DATE_ISO") != "UNKNOWN"}
    base_r["ITEM_ABERTO"] = item
    if not item["DOCUMENT_ID"]:
        return dict(base_r, PASS=False, CLASSE="SOURCE_FAILURE", DETAIL_GATE_PASSED=False,
                    PORQUE="IDENTITY_FAILED: o recorte do boletim (CONTENT_SCOPE) nao esta na pagina")
    if item["BOLETIM_CARACTERES"] < BOLETIM_MINIMO:
        return dict(base_r, PASS=False, CLASSE="SOURCE_FAILURE", DETAIL_GATE_PASSED=False,
                    PORQUE="o boletim recortado tem so %d caracteres (< %d)" % (item["BOLETIM_CARACTERES"], BOLETIM_MINIMO))
    return dict(base_r, PASS=True, CLASSE="OK", DETAIL_GATE_PASSED=True, DOCUMENT_ID=item["DOCUMENT_ID"],
                TEMPOS=tempos_do_motor(ident))


def escolher_alvo(alvos: list[str], index_url: str = "") -> str:
    """O item que o canario TENTA primeiro. Se ele nao passar, o canario abre `alvos[0]`,
    como sempre abriu — e esse que o reparo (reparar_contrato) le, e que o canario
    continua a alcancar.

    ⚠️ MEDIDO (HR-6, 25/09/2026): o canario abria sempre `alvos[0]`, o primeiro por
    ordem alfabetica. Em 6 fontes esse primeiro tinha cara de SECCAO pela regra do
    portao (`collection_gate.revisao_humana_do_url`) e a fonte ficava READY mas fora
    da colheita (HUMAN_REVIEW_REQUIRED) — e re-medir abria o mesmo endereco, sempre.
    A CONAF tem 29 itens na entrada; o 1.o era «assemblea-agronomi-udine».

    Por isso: o primeiro, na mesma ordem, cujo endereco NAO tem cara de seccao. Se
    todos tem, o primeiro — e o portao continua a pedir olho humano. Isto so escolhe
    QUAL item se abre; quem julga se e materia continua a ser o gate de detalhe.
    """
    import collection_gate as G  # noqa: PLC0415  (import tardio: le o livro)
    entrada = (index_url or "").rstrip("/")
    for a in alvos:
        if a.rstrip("/") != entrada and not G.revisao_humana_do_url(a):
            return a
    return alvos[0]


def canario_html(c: dict) -> dict:
    """Abre a entrada, aplica o LINK_PATTERN e prova que sai um ITEM (nao o indice)."""
    aq = c["ACQUISITION"]
    st, b, err = buscar(aq["INDEX_URL"])
    if st != 200 or not b:
        return {"PASS": False, "CLASSE": "UNKNOWN", "PORQUE": err or "HTTP %s" % st,
                "HTTP": st}
    hrefs = hrefs_da_entrada(b, aq["INDEX_URL"], aq.get("STRIP_SUFFIX"))
    rx = re.compile(aq["LINK_PATTERN"])
    alvos = [h for h in sorted(hrefs) if rx.match(h)]
    if not alvos:
        return {"PASS": False, "CLASSE": "SOURCE_FAILURE", "HTTP": st,
                "PORQUE": ("nenhum dos %d enderecos da entrada casa com o padrao "
                           "— EMPTY_LIST, como o contrato preve" % len(hrefs)),
                "HREFS": len(hrefs)}
    # ⚠️ O ALVO NAO PODE SER A PROPRIA ENTRADA.
    if alvos[0].rstrip("/") == aq["INDEX_URL"].rstrip("/"):
        return {"PASS": False, "CLASSE": "ROUTE_FAILURE", "HTTP": st,
                "PORQUE": "o padrao devolveu a propria pagina de entrada"}
    # HR-6: tenta o item mais fundo; se ele nao passar, abre o primeiro, como
    # antes. NUNCA PIOR DO QUE HOJE: medido na copia, o item fundo da ARPAS e da
    # Umbria era PDF e o de Padova navegacao — sem a volta, 3 READY cairiam.
    primeiro = alvos[0]
    alvo = escolher_alvo(alvos, aq["INDEX_URL"])
    # DA-13: o texto de cada ligacao da entrada (LINK_TEXT), lido uma vez, como o coletor o poe no alvo
    textos = textos_das_ligacoes(b, aq["INDEX_URL"], aq.get("STRIP_SUFFIX"))
    r = _abrir_item(c, alvo, alvos, textos)
    if alvo != primeiro and not r.get("PASS"):
        tentado = {k: r.get(k) for k in ("ALVO", "CLASSE", "PORQUE", "ITEM_ABERTO")
                   if r.get(k) is not None}
        r = _abrir_item(c, primeiro, alvos, textos)
        r["ALVO_FUNDO_TENTADO"] = tentado
    return r


def _abrir_item(c: dict, alvo: str, alvos: list[str], textos: dict | None = None) -> dict:
    """Abre UM item e julga-o. Sem fallback aqui: quem escolhe e canario_html."""
    st2, b2, err2 = buscar(alvo)
    if st2 != 200 or not b2:
        return {"PASS": False, "CLASSE": "UNKNOWN", "HTTP": st2,
                "PORQUE": "documento inacessivel: %s" % (err2 or st2), "ALVO": alvo}
    # ⚠️ UM BOM UTF-8 A FRENTE DO «<» NAO E «NAO E HTML». Medido no provador de
    # listagens (CAND-0060): b'\xef\xbb\xbf<!DOC' reprovava como bytes errados.
    # D32 (4): contrato que declara PDF e julgado pela esteira de PDF, nao pelo retrato de HTML.
    if c.get("OUTPUT_TYPE") == "PDF":
        return _canario_pdf(c, alvo, alvos, st2, b2, (textos or {}).get(alvo, ""))
    if not b2.lstrip().removeprefix(b"\xef\xbb\xbf")[:1] == b"<":
        return {"PASS": False, "CLASSE": "SOURCE_FAILURE", "HTTP": st2,
                "PORQUE": "bytes nao sao HTML — BYTE_VALIDATION_FAILED", "ALVO": alvo}

    # ── READY EXIGE ITEM REAL (AQUISICAO-DETALHE-V1, PASSO 8 · integrado) ──
    # Ate aqui «a rota resolve» chegava: um endereco que casa com o padrao,
    # abre e traz HTML. Medido na outra linha: 32 das 104 fontes de indice
    # tinham rota resolvida e o unico item era o menu, e 9 guardavam a
    # PROPRIA LISTAGEM como documento. HTTP 200 + bytes HTML nao distingue
    # uma materia de uma capa. Por isso o item aberto e RETRATADO, e:
    #
    #     sem texto visivel         -> ITEM_SEM_TEXTO       (BODY util e obrigatorio)
    #     parece listagem/navegacao -> CAPA_NAO_E_MATERIA   (o gate, com nome)
    #
    # Nada e guardado: VALIDAR != COLETAR continua. E o gate so julga o que o
    # contrato declara como itens de detalhe (ver retrato_html.gate_capa_nao_e_materia).
    ret = RH.retrato_do_html(b2)
    item = {"URL": alvo, "HTTP": st2, "BYTES": len(b2),
            "HTML_KIND": ret["HTML_KIND"], "CAPA_OU_MATERIA": ret["CAPA_OU_MATERIA"],
            "LINKS": ret["LINKS"],
            "NON_WHITESPACE_CHARACTERS": ret["NON_WHITESPACE_CHARACTERS"],
            "PARAGRAPH_CHARACTERS": ret["PARAGRAPH_CHARACTERS"],
            "TEXT_SHA256": ret["TEXT_SHA256"]}
    base_r = {"HTTP": st2, "ALVO": alvo, "ALVOS_DESCOBERTOS": len(alvos),
              "DETAIL_ENUMERATED": len(alvos), "ITEM_ABERTO": item,
              "DETAIL_GATE": RH.GATE_VERSAO, "BYTES": len(b2)}
    if ret["HTML_KIND"] == "EMPTY":
        return dict(base_r, PASS=False, CLASSE="SOURCE_FAILURE", DETAIL_GATE_PASSED=False,
                    PORQUE="ITEM_SEM_TEXTO: o item abriu e nao tem texto visivel "
                           "— sem BODY util nao ha materia")
    # V1A: o gate recebe a morada do item e se a regua dos 4 passos manda na
    # fonte (a V1: o INDEX_URL do contrato e capa, so com a regua a mandar).
    gate = RH.gate_capa_nao_e_materia(c, ret, url=alvo, regua_a_mandar=_regua_manda(c.get("SOURCE_ID")))
    if gate:
        return dict(base_r, PASS=False, CLASSE="SOURCE_FAILURE", DETAIL_GATE_PASSED=False,
                    PORQUE=gate)
    # D61/D62: um boletim em HTML que declara data e lugar (ex.: ARSAC, uma pagina por edicao) pergunta
    # ao MOTOR, como o PDF. Os contratos sem BASE ficam exactamente como antes.
    if declara_data_e_lugar(c):
        ident = identidade_pelo_motor(c, alvo, b2)
        if ident.get("ERRO"):
            return dict(base_r, PASS=False, CLASSE="UNKNOWN", DETAIL_GATE_PASSED=False,
                        PORQUE="o motor do coletor nao deu identidade: %s" % str(ident["ERRO"])[:160])
        if not ident.get("DOCUMENT_ID"):
            return dict(base_r, PASS=False, CLASSE="SOURCE_FAILURE", DETAIL_GATE_PASSED=False,
                        PORQUE="IDENTITY_FAILED: as capturas do contrato nao casam com o alvo")
        return dict(base_r, PASS=True, CLASSE="OK", DETAIL_GATE_PASSED=True, DOCUMENT_ID=ident["DOCUMENT_ID"],
                    TEMPOS=tempos_do_motor(ident))
    return dict(base_r, PASS=True, CLASSE="OK", DETAIL_GATE_PASSED=True,
                DOCUMENT_ID=c["IDENTITY"]["DOCUMENT_ID"].replace(
                    "{doc.1}", re.sub(r"^https?://[^/]+/?", "", alvo).rstrip("/")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", required=True)
    ap.add_argument("--n", type=int, default=2, help="canarios por familia")
    ap.add_argument("--pausa", type=float, default=0.8)
    a = ap.parse_args()

    d = json.loads((RAIZ / "curadoria" / "italy_contracts_curator.json")
                   .read_text(encoding="utf-8"))
    alvo = [c for c in d["FONTES"] if c["BATCH_ID"] == a.lote]
    if not alvo:
        print("lote sem contratos: %s" % a.lote)
        return 1

    # ── CONTROLO POSITIVO ANTES DE TUDO ──────────────────────────────────
    url = CONTROLO[a.lote]
    st, b, err = buscar(url)
    controlo_ok = st == 200 and len(b) > 200
    print("controlo (%s): HTTP %s %s  ->  %s"
          % (a.lote, st, err, "OK" if controlo_ok else "FALHOU"))
    if not controlo_ok:
        print("  ⚠️ o leitor nao passou no controlo: NENHUMA fonte sera condenada.")
        print("     veredito do lote = CLIENT_FAILURE / ENVIRONMENT_GAP")
        return 2

    fn = canario_youtube if a.lote == "LOTE-YOUTUBE-FEED" else canario_html
    resultados = []
    for c in alvo[:a.n]:
        r = fn(c)
        r["SOURCE_ID"] = c["SOURCE_ID"]
        r["NAME"] = c["NAME"]
        resultados.append(r)
        print("  %-12s %-6s %-16s %s"
              % (c["SOURCE_ID"], "PASS" if r["PASS"] else "FAIL", r["CLASSE"],
                 (r.get("DOCUMENT_ID") or r.get("PORQUE", ""))[:64]))
        time.sleep(a.pausa)

    passou = sum(1 for r in resultados if r["PASS"])
    saida = {
        "LOTE": a.lote, "CANARY_ATTEMPTED": len(resultados),
        "CANARY_PASS": passou, "CANARY_FAIL": len(resultados) - passou,
        "CONTROLO_POSITIVO": {"URL": url, "HTTP": st, "OK": controlo_ok},
        "LEI": ("o controlo positivo corre ANTES: se o leitor falha, nenhuma "
                "fonte e condenada"),
        "CORRIDO_EM": datetime.now(timezone.utc).isoformat(),
        "RESULTADOS": resultados,
    }
    p = RAIZ / "curadoria" / ("CANARY-%s.json" % a.lote)
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("PASS %d/%d  ->  %s" % (passou, len(resultados), p.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
