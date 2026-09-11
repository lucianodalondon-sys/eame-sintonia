#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REGISTO DE ADAPTADORES — o unico dono de `PLATAFORMA/CAPACIDADE -> ADAPTADOR`.

    import scrap_registo as reg
    reg.registar('INSTAGRAM', 'instagram.reel.capture',
                 adaptador='adaptador_instagram', executa=minha_funcao)
    reg.adaptador_de('INSTAGRAM', 'instagram.reel.capture')

POR QUE ISTO E UM FICHEIRO A PARTE, E NAO UM `dict` DENTRO DO ROTEADOR
-----------------------------------------------------------------------
Porque o roteador precisa de conhecer os adaptadores e os adaptadores precisam
de se declarar ao roteador. Se o mapa vivesse dentro do roteador, so haveria
duas saidas, e as duas sao piores:

    1. o roteador importa cada adaptador — e passa a conhecer todas as
       plataformas, que e exatamente o monolito que a lei proibe;
    2. o adaptador importa o roteador para se registar — e nasce um ciclo.

Com o registo a meio, ninguem conhece ninguem: o adaptador escreve no registo,
o roteador le do registo, e acrescentar uma plataforma nova nao toca numa unica
linha do roteador.

    O TESTE DISTO NAO E ESTETICO. E: «ACRESCENTAR O TIKTOK OBRIGA A EDITAR O
    ROTEADOR?» Se obrigar, o roteador voltou a ser o monolito.

UM CONCEITO, UM DONO
---------------------
    scrap_registo.py     PLATAFORMA/CAPACIDADE -> ADAPTADOR      (o mapa)
    social_rotas.py      escolher porta, medir portao, executar  (o despacho)
    scrap_capacidades.py o que sabemos fazer, e onde             (a declaracao)

Sao tres donos de tres coisas, nao tres donos da mesma coisa.

E O QUE O REGISTO RECUSA
-------------------------
Recusa duas coisas, e as duas ja aconteceram nesta casa:

    · dois adaptadores para a mesma (plataforma, capacidade) — que e o
      segundo dono a nascer sem ninguem reparar;
    · registar capacidade que a declaracao nao conhece — que e prometer
      resultado que ninguem mediu.

    UM ADAPTADOR PODE EXISTIR SEM EXECUTAR NADA. Nao pode e existir dizendo
    que executa.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import scrap_capacidades as cap  # noqa: E402


class RegistoDuplicado(RuntimeError):
    """Dois donos para a mesma (plataforma, capacidade). Nao ha desempate justo."""


class CapacidadeNaoDeclarada(RuntimeError):
    """Registar o que a lei nao declara e prometer o que ninguem mediu."""


#: (PLATAFORMA, capacidade pontuada) -> dicionario do registo.
_MAPA = {}


def registar(plataforma, capacidade, *, adaptador, executa=None, nota=None):
    """Poe um adaptador no mapa. `executa=None` e uma declaracao honesta.

    Um adaptador que declara a capacidade e nao tem rota devolve o estado
    medido — nunca um sucesso vazio.
    """
    plat = (plataforma or '').upper()
    if not cap.existe(capacidade):
        raise CapacidadeNaoDeclarada(
            '%s nao esta em scrap_capacidades.DECLARADAS. Declarar o estado '
            'medido primeiro; registar depois.' % capacidade)
    if cap.plataforma(capacidade) != plat:
        raise CapacidadeNaoDeclarada(
            '%s pertence a %s, nao a %s' % (capacidade, cap.plataforma(capacidade), plat))
    chave = (plat, capacidade)
    ja = _MAPA.get(chave)
    if ja and ja['ADAPTADOR'] != adaptador:
        raise RegistoDuplicado(
            '%s/%s ja pertence a %r e %r quer o mesmo lugar. '
            'Dois donos nao se resolvem por ordem de import.'
            % (plat, capacidade, ja['ADAPTADOR'], adaptador))
    alvo, porque = cap.onde(capacidade)
    _MAPA[chave] = {
        'PLATFORM': plat,
        'CAPABILITY': capacidade,
        'ADAPTADOR': adaptador,
        'EXECUTA': executa,
        'CAPABILITY_STATE': cap.estado(capacidade),
        'EXECUTION_TARGET': alvo,
        'WHY_LOCAL': porque,
        'PROVA': cap.prova(capacidade),
        'NOTA': nota,
    }
    return _MAPA[chave]


def adaptador_de(plataforma, capacidade):
    """→ o registo, ou None. None significa «nao ha dono», nao «falhou»."""
    return _MAPA.get(((plataforma or '').upper(), capacidade))


def executor_de(plataforma, capacidade):
    """→ a funcao que executa, ou None se a capacidade so esta declarada."""
    r = adaptador_de(plataforma, capacidade)
    return r['EXECUTA'] if r else None


def registados():
    return dict(_MAPA)


def adaptadores():
    """Os nomes dos modulos adaptadores, sem repetir."""
    return tuple(sorted({r['ADAPTADOR'] for r in _MAPA.values()}))


def do_adaptador(nome):
    return {k: v for k, v in sorted(_MAPA.items()) if v['ADAPTADOR'] == nome}


def executaveis():
    """So as capacidades que tem rota E prometem resultado."""
    return {k: v for k, v in sorted(_MAPA.items())
            if v['EXECUTA'] is not None and cap.promete_resultado(v['CAPABILITY'])}


def carregar_adaptadores():
    """Importa os modulos adaptadores para que eles se registem.

    A lista e explicita de proposito. Varrer a pasta a procura de
    `adaptador_*.py` parece mais esperto e e pior: um ficheiro meio escrito
    entraria em producao por existir, e a ordem de varrimento decidiria quem
    ganha um conflito. Aqui o conflito rebenta, que e o que se quer.
    """
    modulos = ('adaptador_instagram', 'adaptador_linkedin', 'adaptador_youtube',
               'adaptador_x', 'adaptador_facebook', 'adaptador_aberto')
    for m in modulos:
        __import__(m)
    return modulos
