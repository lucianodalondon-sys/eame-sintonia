#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LER UM .XLSX SEM INSTALAR NADA.

    from xlsx_simples import folhas, tabela
    for linha in tabela("candidatas/X.xlsx", "QUALIFICACAO"):
        print(linha["NOME"])

PORQUE ISTO EXISTE
------------------
Duas folhas de calculo desta gaveta carregam a prova de 381 fontes italianas —
estado HTTP, dono, ancora de identidade, pais, portao de qualificacao. Elas sao
a razao pela qual esta missao nao precisa de abrir uma unica fonte.

E nesta maquina `import openpyxl` levanta ModuleNotFoundError.

    PROVA QUE SO SE LE COM UMA DEPENDENCIA QUE NAO ESTA INSTALADA
    E PROVA QUE, NA PRATICA, NINGUEM LE.

Um .xlsx e um zip com XML dentro. Isto abre o zip e le o XML, com a biblioteca
padrao e mais nada. Le; nao escreve, nao calcula formula, nao formata.

O QUE ELE NAO FAZ, DE PROPOSITO
--------------------------------
  · nao avalia formulas — devolve o valor em cache que o Excel gravou;
  · nao converte data de serie para data — devolve o numero como esta;
  · nao adivinha cabecalho repetido — a segunda coluna com o mesmo nome
    sobrescreve a primeira, e isso e' visivel em `folhas()`.

Nenhuma dessas limitacoes toca nas folhas desta gaveta, que sao texto.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_NS = {"m": _MAIN, "r": _REL}

_COLUNA = re.compile(r"[A-Z]+")


def _alvos(z: zipfile.ZipFile) -> list[tuple[str, str]]:
    """(nome da folha, caminho do XML dentro do zip), pela ordem do livro."""
    livro = ET.fromstring(z.read("xl/workbook.xml"))
    ligacoes = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    por_id = {r.get("Id"): r.get("Target") for r in ligacoes}
    fora = []
    for folha in livro.find("m:sheets", _NS):
        alvo = por_id[folha.get("{%s}id" % _REL)]
        alvo = alvo.lstrip("/")
        if not alvo.startswith("xl/"):
            alvo = "xl/" + alvo
        fora.append((folha.get("name"), alvo))
    return fora


def _partilhadas(z: zipfile.ZipFile) -> list[str]:
    """A tabela de strings partilhadas. O XML guarda indices, nao texto."""
    try:
        bruto = z.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    raiz = ET.fromstring(bruto)
    return ["".join(t.text or "" for t in si.iter("{%s}t" % _MAIN)) for si in raiz]


def _celulas(z: zipfile.ZipFile, alvo: str, ss: list[str]) -> list[dict]:
    """Uma lista de {coluna: valor}, incluindo a linha de cabecalho."""
    raiz = ET.fromstring(z.read(alvo))
    fora = []
    for linha in raiz.iter("{%s}row" % _MAIN):
        atual: dict[str, str] = {}
        for c in linha:
            ref = c.get("r") or ""
            col = _COLUNA.match(ref)
            if not col:
                continue
            tipo = c.get("t")
            if tipo == "inlineStr":
                valor = "".join(t.text or "" for t in c.iter("{%s}t" % _MAIN))
            else:
                v = c.find("m:v", _NS)
                if v is None or v.text is None:
                    valor = ""
                elif tipo == "s":
                    valor = ss[int(v.text)]
                else:
                    valor = v.text
            atual[col.group()] = valor
        fora.append(atual)
    return fora


def folhas(caminho) -> dict[str, int]:
    """Nome de cada folha -> numero de linhas (cabecalho incluido)."""
    with zipfile.ZipFile(Path(caminho)) as z:
        ss = _partilhadas(z)
        return {nome: len(_celulas(z, alvo, ss)) for nome, alvo in _alvos(z)}


def tabela(caminho, folha: str) -> list[dict]:
    """As linhas de uma folha como dicionarios, com a PRIMEIRA linha por chave.

    Celula vazia devolve string vazia — nunca `None`. Quem le prova nao deve
    ter de distinguir «a coluna nao existe» de «a coluna existe e esta vazia»
    em cada uso; distingue-se uma vez, aqui.
    """
    with zipfile.ZipFile(Path(caminho)) as z:
        ss = _partilhadas(z)
        alvo = dict(_alvos(z)).get(folha)
        if alvo is None:
            raise KeyError("folha inexistente: %s · existem: %s"
                           % (folha, ", ".join(dict(_alvos(z)))))
        linhas = _celulas(z, alvo, ss)
    if not linhas:
        return []
    cabecalho = linhas[0]
    colunas = sorted(cabecalho, key=lambda c: (len(c), c))
    nomes = {c: (cabecalho.get(c) or c) for c in colunas}
    return [{nomes[c]: r.get(c, "") for c in colunas} for r in linhas[1:]]
