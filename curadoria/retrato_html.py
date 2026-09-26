#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O RETRATO DE UM HTML — o que se mede nos bytes SEM interpretar o que dizem.

    CAPA != MATERIA.   MARKUP != TEXTO.

Nasceu na AQUISICAO-DETALHE-V1 (2026-09-21, bancada f98f234c) como
`coleta/retrato_html.mjs`, de duas medicoes no canario:

  · 9 das 104 fontes de indice tinham a PROPRIA LISTAGEM guardada como se
    fosse o documento (ex.: /News/Comunicati-stampa, /news/ufficio-stampa/).
    O contrato dizia «itens de detalhe» e o que chegou foi a capa. Nada no
    coletor distinguia uma coisa da outra.
  · 2 de 3 DOCUMENT_CHANGED_IN_PLACE no canario eram o MESMO texto visivel
    com bytes diferentes (widgets, nonces, contadores).

Este ficheiro e a porta do SOURCE CURATOR para a mesma leitura. Nao e um
merge: o worker desta arvore corre o canario em Python (`canario.py`), e por
isso o gate tem de existir aqui, no dono que promove a READY. Os limiares
sao OS MESMOS do Node (`retrato_html.mjs`) e do executor Python da outra
linha (`executor_texto_de_html.py::_kind`): 800 caracteres em paragrafos e
35% do texto; menos de 40 caracteres por ligacao e navegacao.

    UM GATE COM LIMIARES DIFERENTES DO COLETOR JULGARIA OUTRA PAGINA.

A desentidacao replica a do Node de proposito (cinco entidades nomeadas e as
numericas), e nao `html.unescape`: um leitor mais generoso aqui faria o
Curator contar caracteres que o coletor nao conta.

    TEXT_SHA256      impressao do texto visivel normalizado — identidade de
                     CONTEUDO, nao de bytes
    HTML_KIND        EMPTY · CONTENT · NAVIGATION · MIXED
    CAPA_OU_MATERIA  MATERIA_PROVAVEL · CAPA_PROVAVEL · NAO_SEI — leitura,
                     dita como leitura
"""
from __future__ import annotations

import hashlib
import re

GATE_VERSAO = "CAPA_NAO_E_MATERIA/v1"

# Os mesmos limiares do coletor. Mudar um aqui sem mudar la e criar um
# segundo juiz.
PARAGRAFO_MINIMO = 800
PARAGRAFO_FRACCAO = 0.35
CARACTERES_POR_LIGACAO = 40

_INVISIVEL = re.compile(
    r"<(script|style|noscript|template)\b[^>]*>.*?</\1\s*>|<!--.*?-->", re.I | re.S)
_PARAGRAFO = re.compile(r"<p\b[^>]*>(.*?)</p\s*>", re.I | re.S)
_LIGACAO = re.compile(r"<a\b[^>]*\bhref\s*=", re.I)
_TAG = re.compile(r"<[^>]+>")
_ENTIDADE = re.compile(r"&(#x[0-9a-f]+|#\d+|[a-z]+);", re.I)
_ENTIDADES = {"amp": "&", "lt": "<", "gt": ">", "quot": "\"", "apos": "'", "nbsp": " "}
_BRANCOS = re.compile(r"\s+")
# As chamadas «leia mais» de uma LISTA: cada item de uma pagina de lista traz a sua.
# Contadas no HTML visivel (sem script/style), como as ligacoes.
_LEIA_MAIS = re.compile(
    r"\b(leggi\s+tutto|leggi\s+di\s+pi[uù]|continua\s+a\s+leggere|read\s+more|scopri\s+di\s+pi[uù])\b",
    re.I)


def _desentidar(s: str) -> str:
    def _uma(m: re.Match) -> str:
        e = m.group(1)
        if e[0] == "#":
            try:
                n = int(e[2:], 16) if e[1] in "xX" else int(e[1:], 10)
                return chr(n)
            except (ValueError, OverflowError):
                return m.group(0)
        return _ENTIDADES.get(e.lower(), m.group(0))
    return _ENTIDADE.sub(_uma, s)


def _decodificar(b: bytes) -> str:
    if b[:3] == b"\xef\xbb\xbf":
        b = b[3:]
    # UTF-8 primeiro; bytes invalidos viram U+FFFD e contam como caractere —
    # o retrato ve o que ha, nao uma pagina vazia.
    return b.decode("utf-8", "replace")


def kind_de(sem_brancos: int, paragrafo: int, ligacoes: int) -> str:
    """A mesma funcao que `executor_texto_de_html.py::_kind` na outra linha."""
    if sem_brancos == 0:
        return "EMPTY"
    if paragrafo >= PARAGRAFO_MINIMO and paragrafo >= PARAGRAFO_FRACCAO * sem_brancos:
        return "CONTENT"
    if ligacoes and sem_brancos / max(ligacoes, 1) < CARACTERES_POR_LIGACAO:
        return "NAVIGATION"
    return "MIXED"


def retrato_do_html(b: bytes) -> dict:
    fonte = _INVISIVEL.sub(" ", _decodificar(b))
    ligacoes = len(_LIGACAO.findall(fonte))
    paragrafo = 0
    for m in _PARAGRAFO.finditer(fonte):
        paragrafo += len(_BRANCOS.sub("", _desentidar(_TAG.sub(" ", m.group(1)))))
    linhas = [_BRANCOS.sub(" ", l).strip() for l in _desentidar(_TAG.sub("\n", fonte)).split("\n")]
    texto = "\n".join(l for l in linhas if l)
    sem_brancos = len(_BRANCOS.sub("", texto))
    kind = kind_de(sem_brancos, paragrafo, ligacoes)
    return {
        "TEXT_SHA256": hashlib.sha256(_BRANCOS.sub(" ", texto).encode("utf-8")).hexdigest(),
        "NON_WHITESPACE_CHARACTERS": sem_brancos,
        "PARAGRAPH_CHARACTERS": paragrafo,
        "LINKS": ligacoes,
        "READ_MORE_LINKS": len(_LEIA_MAIS.findall(fonte)),
        "HTML_KIND": kind,
        "CAPA_OU_MATERIA": ("MATERIA_PROVAVEL" if kind == "CONTENT"
                            else "CAPA_PROVAVEL" if kind == "NAVIGATION"
                            else "NAO_SEI"),
    }


def _sem_barra(u: str) -> str:
    """A mesma normalizacao de `ready_split._sem_barra` (a regua dos 4 passos)."""
    return (u or "").strip().rstrip("/").lower()


# ── V1: O INDEX_URL DO CONTRATO E CAPA (LD3 → K1 → V1A, 2026-09-23) ─────────
# A morada so manda quando e EXACTAMENTE a pagina de entrada que o contrato
# declara — e so quando a REGUA MANDA: a fonte passa os 4 passos
# (`ready_split.regua_de == DETAIL/v1`). Numa fonte que nao os passa, o
# INDEX_URL nao esta provado, e usa-lo para julgar seria julgar pela morada que
# ninguem conferiu. Nessas, o detector de hoje, sem mudanca.
#
# So HTML_LINK_DISCOVERY: numa rota fixa o INDEX_URL E o documento.
#
# Criterio fixado ANTES de medir (briefing LD2): «so se dominar o ACTUAL nos dois
# erros em todos os gabaritos». Medido na K1 (receitas V4): capas que entram
# 37->30 · 6->5 · 4->3 (cego); noticias barradas e retidas iguais nos tres.
#
#     O PAR TEM DE MUDAR JUNTO: `coleta/retrato_html.mjs` tem a mesma regra.
V1_LIGADA = True
REGRA_V1 = "V1_INDEX_URL_E_CAPA"


# ── V2: A LISTA QUE PARECE MATERIA (C2-JUIZ, 2026-09-26) ─────────────────────
# Na 3.a onda o formato deu CONTENT a `sostenibilita.enea.it/eventi/meeting-
# internazionali-0` (IT-T5-186, raw 1520): uma LISTA de eventos, cada um com o seu
# «Leggi tutto su …» (10 na pagina). Entrou na Sala com a data de um evento e o
# lugar de outro. O formato mede a pagina inteira e nao ve que o texto e de VARIOS.
#
# A regra so APERTA: materia com >= 6 chamadas «leia mais» passa a CAPA_PROVAVEL.
# Medido antes de escolher (GABARITO-CAPA-V1, 146 paginas; 3.a onda, 75 HTML):
#   · no gabarito, capas que atravessam 63 -> 58; materias barradas 6 -> 7;
#   · na 3.a onda, a noticia com mais «leia mais» tem 4 (Riunite, barra lateral);
#     a lista ENEA tem 10. Limiar 6 = o meio; margem de UM exemplo, declarada.
# A regra irma (data de publicacao salvaria a noticia curta com menu grande) foi
# MEDIDA E RECUSADA: no gabarito deixava passar 11 capas para salvar 2 noticias.
#
#     O PAR TEM DE MUDAR JUNTO: `coleta/retrato_html.mjs` tem a mesma regra.
V2_LIGADA = True
REGRA_V2 = "V2_LISTA_COM_LEIA_MAIS"
LEIA_MAIS_MINIMO = 6


def e_lista_com_leia_mais(retrato: dict | None) -> bool:
    r = retrato or {}
    return (V2_LIGADA and r.get("CAPA_OU_MATERIA") == "MATERIA_PROVAVEL"
            and (r.get("READ_MORE_LINKS") or 0) >= LEIA_MAIS_MINIMO)


def e_o_indice_do_contrato(url: str, contrato: dict | None) -> bool:
    aq = (contrato or {}).get("ACQUISITION") or {}
    if aq.get("STRATEGY") != "HTML_LINK_DISCOVERY":
        return False
    indice = _sem_barra(aq.get("INDEX_URL") or "")
    return bool(indice) and _sem_barra(url) == indice


def veredito(retrato: dict | None, *, url: str | None, contrato: dict | None,
             regua_a_mandar: bool) -> str:
    """CAPA_OU_MATERIA com a V1: o retrato, salvo se a pagina e o INDEX_URL de
    uma fonte que passa os 4 passos — entao CAPA_PROVAVEL. Sem `url`, a V1 nao
    se aplica (NAO SEI se e o indice): fica o detector.

    `url`, `contrato` e `regua_a_mandar` sao OBRIGATORIOS por nome: um chamador
    esquecido rebenta, em vez de julgar calado sem a regra."""
    return regra_e_veredito(retrato, url=url, contrato=contrato, regua_a_mandar=regua_a_mandar)[1]


def regra_e_veredito(retrato: dict | None, *, url: str | None, contrato: dict | None,
                     regua_a_mandar: bool) -> tuple:
    """(regra que mudou o detector ou None, CAPA_OU_MATERIA). V1 antes de V2."""
    k = (retrato or {}).get("CAPA_OU_MATERIA")
    if V1_LIGADA and regua_a_mandar is True and url and e_o_indice_do_contrato(url, contrato):
        return (REGRA_V1 if k != "CAPA_PROVAVEL" else None), "CAPA_PROVAVEL"
    if e_lista_com_leia_mais(retrato):
        return REGRA_V2, "CAPA_PROVAVEL"
    return None, k


def gate_capa_nao_e_materia(contrato: dict, retrato: dict, *, url: str | None,
                            regua_a_mandar: bool) -> str | None:
    """O GATE: um contrato que declara ITENS DE DETALHE (HTML_LINK_DISCOVERY
    com saida HTML) nao pode dar por bom uma capa como conteudo final.
    Devolve None quando nao ha nada a dizer, ou a razao da reprovacao.

    Rota fixa (STATIC_ENDPOINT) e PDF NAO sao julgados: uma capa numa rota
    fixa e a rota fixa, e um PDF nao tem ligacoes para contar.

    V1A: recebe o endereco da pagina e se a regua dos 4 passos manda na fonte.
    """
    aq = (contrato or {}).get("ACQUISITION") or {}
    if aq.get("STRATEGY") != "HTML_LINK_DISCOVERY":
        return None
    if str((contrato or {}).get("OUTPUT_TYPE") or "").upper() != "HTML":
        return None
    if not retrato:
        return None
    regra, k = regra_e_veredito(retrato, url=url, contrato=contrato, regua_a_mandar=regua_a_mandar)
    if k != "CAPA_PROVAVEL":
        return None
    if regra == REGRA_V1:
        return ("CAPA_NAO_E_MATERIA (%s): a pagina e o proprio INDEX_URL do contrato, e a "
                "fonte passa os 4 passos" % REGRA_V1)
    if regra == REGRA_V2:
        return ("CAPA_NAO_E_MATERIA (%s): pagina de lista, %d chamadas «leia mais»"
                % (REGRA_V2, retrato.get("READ_MORE_LINKS") or 0))
    return ("CAPA_NAO_E_MATERIA: o contrato declara itens de detalhe e o alvo parece "
            "listagem/navegacao (%d ligacoes para %d caracteres, %d em paragrafos)"
            % (retrato["LINKS"], retrato["NON_WHITESPACE_CHARACTERS"],
               retrato["PARAGRAPH_CHARACTERS"]))


if __name__ == "__main__":
    import json
    import sys
    dados = sys.stdin.buffer.read()
    print(json.dumps(retrato_do_html(dados), ensure_ascii=False, indent=1))
