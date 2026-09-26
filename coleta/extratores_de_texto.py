#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS EXTRATORES DE TEXTO, PARA QUEM PRECISA DE RE-EXTRAIR (D79).

`admissao/versao_do_documento.py` decide se um documento mudou DE VERDADE. Quando
a receita do extrator mudou entre a versão anterior e a nova, ele precisa de
re-extrair o RAW anterior com o extrator NOVO — e para isso recebe um registo
`{producer: extrair(bytes, media_type) -> (texto, producer_version, parameters_hash)}`.

Este ficheiro É esse registo. Não reimplementa nada: chama o `extrair()` de cada
executor e a `receita()` dele, e calcula o hash pela MESMA função que o dono da
escrita usa (`guarda.preservar_derivado.hash_dos_parametros`).

    SE A EXTRAÇÃO NÃO DEU TEXTO, O TEXTO É None — E O DECISOR DIZ NÃO SEI.
"""
import os
import tempfile
from pathlib import Path

import _gavetas  # noqa: F401
import artefato as art

from coleta import executor_texto_de_html as _html
from coleta import executor_texto_de_pdf as _pdf
from guarda.preservar_derivado import hash_dos_parametros


def _de_html(dados, media_type):
    texto, estado, _erro, _medidas = _html.extrair(dados, media_type or "text/html")
    return ((texto if estado == art.TEXT_LAYER_PRESENT else None),
            _html.EXECUTOR_VERSION, hash_dos_parametros(_html.receita()))


def _de_pdf(dados, media_type):
    # o extrator de PDF le de um caminho: o RAW vai para um ficheiro temporario,
    # que se apaga logo a seguir (nada fica, nada vai ao armazem)
    fd, caminho = tempfile.mkstemp(suffix=".pdf")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(dados)
        texto, estado, _erro, _medidas = _pdf.extrair(Path(caminho))
    finally:
        try:
            os.remove(caminho)
        except OSError:
            pass
    return ((texto if estado == art.TEXT_LAYER_PRESENT else None),
            _pdf.EXECUTOR_VERSION, hash_dos_parametros(_pdf.receita()))


def registo():
    """O registo que `sala_de_espera.pousar(..., extratores=registo())` recebe."""
    return {_html.EXECUTOR_ID: _de_html, _pdf.EXECUTOR_ID: _de_pdf}
