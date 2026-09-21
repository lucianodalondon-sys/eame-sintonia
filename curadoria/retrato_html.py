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
        "HTML_KIND": kind,
        "CAPA_OU_MATERIA": ("MATERIA_PROVAVEL" if kind == "CONTENT"
                            else "CAPA_PROVAVEL" if kind == "NAVIGATION"
                            else "NAO_SEI"),
    }


def gate_capa_nao_e_materia(contrato: dict, retrato: dict) -> str | None:
    """O GATE: um contrato que declara ITENS DE DETALHE (HTML_LINK_DISCOVERY
    com saida HTML) nao pode dar por bom uma capa como conteudo final.
    Devolve None quando nao ha nada a dizer, ou a razao da reprovacao.

    Rota fixa (STATIC_ENDPOINT) e PDF NAO sao julgados: uma capa numa rota
    fixa e a rota fixa, e um PDF nao tem ligacoes para contar.
    """
    aq = (contrato or {}).get("ACQUISITION") or {}
    if aq.get("STRATEGY") != "HTML_LINK_DISCOVERY":
        return None
    if str((contrato or {}).get("OUTPUT_TYPE") or "").upper() != "HTML":
        return None
    if not retrato or retrato.get("CAPA_OU_MATERIA") != "CAPA_PROVAVEL":
        return None
    return ("CAPA_NAO_E_MATERIA: o contrato declara itens de detalhe e o alvo parece "
            "listagem/navegacao (%d ligacoes para %d caracteres, %d em paragrafos)"
            % (retrato["LINKS"], retrato["NON_WHITESPACE_CHARACTERS"],
               retrato["PARAGRAPH_CHARACTERS"]))


if __name__ == "__main__":
    import json
    import sys
    dados = sys.stdin.buffer.read()
    print(json.dumps(retrato_do_html(dados), ensure_ascii=False, indent=1))
