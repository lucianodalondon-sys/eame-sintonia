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


def _regua_manda(source_id) -> bool:
    """V1A: le o dono (ready_split.regua_manda). Import tardio: ready_split le o
    livro do lifecycle, e o canario nao precisa dele para mais nada."""
    import ready_split as RS  # noqa: PLC0415
    return RS.regua_manda(source_id)


def hrefs_da_entrada(b: bytes, index_url: str) -> set[str]:
    """Os enderecos que o canario ve numa pagina de entrada. UM so dono: o
    reparo de contratos (reparar_contrato.py) infere o padrao sobre ESTE
    conjunto, para propor exactamente o que o canario vai casar depois."""
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
        if h.startswith(("http://", "https://")):
            hrefs.add(h.split("#")[0])
    return hrefs


PDF_GATE_VERSAO = "PDF_TEXT_LAYER/v1"
PDF_MINIMO_DE_TEXTO = 800        # a mesma exigencia de corpo do HTML (BODY_UTIL: >= 800 caracteres)


def _canario_pdf(c: dict, alvo: str, alvos: list, st2: int, b2: bytes) -> dict:
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
    return dict(base_r, PASS=True, CLASSE="OK", DETAIL_GATE_PASSED=True,
                DOCUMENT_ID=c["IDENTITY"]["DOCUMENT_ID"].replace(
                    "{doc.1}", re.sub(r"^https?://[^/]+/?", "", alvo).rstrip("/")))


def canario_html(c: dict) -> dict:
    """Abre a entrada, aplica o LINK_PATTERN e prova que sai um ITEM (nao o indice)."""
    aq = c["ACQUISITION"]
    st, b, err = buscar(aq["INDEX_URL"])
    if st != 200 or not b:
        return {"PASS": False, "CLASSE": "UNKNOWN", "PORQUE": err or "HTTP %s" % st,
                "HTTP": st}
    hrefs = hrefs_da_entrada(b, aq["INDEX_URL"])
    rx = re.compile(aq["LINK_PATTERN"])
    alvos = [h for h in sorted(hrefs) if rx.match(h)]
    if not alvos:
        return {"PASS": False, "CLASSE": "SOURCE_FAILURE", "HTTP": st,
                "PORQUE": ("nenhum dos %d enderecos da entrada casa com o padrao "
                           "— EMPTY_LIST, como o contrato preve" % len(hrefs)),
                "HREFS": len(hrefs)}
    # ⚠️ O ALVO NAO PODE SER A PROPRIA ENTRADA.
    alvo = alvos[0]
    if alvo.rstrip("/") == aq["INDEX_URL"].rstrip("/"):
        return {"PASS": False, "CLASSE": "ROUTE_FAILURE", "HTTP": st,
                "PORQUE": "o padrao devolveu a propria pagina de entrada"}
    st2, b2, err2 = buscar(alvo)
    if st2 != 200 or not b2:
        return {"PASS": False, "CLASSE": "UNKNOWN", "HTTP": st2,
                "PORQUE": "documento inacessivel: %s" % (err2 or st2), "ALVO": alvo}
    # ⚠️ UM BOM UTF-8 A FRENTE DO «<» NAO E «NAO E HTML». Medido no provador de
    # listagens (CAND-0060): b'\xef\xbb\xbf<!DOC' reprovava como bytes errados.
    # D32 (4): contrato que declara PDF e julgado pela esteira de PDF, nao pelo retrato de HTML.
    if c.get("OUTPUT_TYPE") == "PDF":
        return _canario_pdf(c, alvo, alvos, st2, b2)
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
