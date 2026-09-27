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


def registar(plataforma, capacidade, *, adaptador, executa=None, rota=None,
             pronto=None, nota=None, unidade=None):
    """Poe um adaptador no mapa. Sem `executa` nem `rota` e uma declaracao honesta.

    Um adaptador que declara a capacidade e nao tem rota devolve o estado
    medido — nunca um sucesso vazio.

    DOIS PAPEIS, UMA ENTRADA SO
    ----------------------------
        rota      a funcao CRUA, que `social_rotas` despacha depois de medir
                  o portao, a sessao e o gasto. Devolve a lista de objetos.
        executa   a funcao de NIVEL DE ADAPTADOR, que devolve (objetos, trace).
                  So para capacidade que a matriz de rotas nao conhece.

    Sao papeis diferentes da mesma capacidade, nao dois donos dela. Quem tem
    `rota` e coletado pelo caminho canonico — executor, roteador, portoes —
    e o trace nasce do registo que o roteador ja sela. Quem tem `executa`
    monta o proprio trace, porque nao ha porta para atravessar.

        A CADEIA DE REEL TEM `executa`. AS QUATRO DO YOUTUBE TEM `rota`.
        Nenhuma tem as duas: isso seria dois caminhos para o mesmo pedido,
        e o segundo caminho e sempre o que ninguem mede.

    A UNIDADE DE TRABALHO, E POR QUE ELA E OPCIONAL
    ------------------------------------------------
        unidade   `unidade(**kwargs) -> (target, entrada, campos)` ou None.
                  So o dono da plataforma sabe dizer o que e uma unidade
                  retomavel dela. Quem nao declara nao ganha checkpoint — e
                  isso e uma resposta, nao um esquecimento.

    Nem toda capacidade tem metade feita. «Resolver um canal pelo nome» ou
    resolveu ou nao resolveu, e um checkpoint `CONCLUIDO` numa operacao que se
    deve poder repetir trancava-a para sempre com
    `JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES`.

        FABRICAR RETOMADA ONDE NAO HA NADA A RETOMAR
        NAO AUMENTA COBERTURA. TRANCA A PORTA.
    """
    if executa is not None and rota is not None:
        raise RegistoDuplicado(
            '%s/%s: `executa` e `rota` ao mesmo tempo sao dois caminhos para o '
            'mesmo pedido.' % (plataforma, capacidade))
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
        'ROTA': rota,
        # A SONDA GRATUITA. Responde «consigo chegar la agora?» sem gastar
        # nada: le configuracao, nunca chama rota. E do adaptador porque so
        # ele sabe o que a sua plataforma precisa ter em maos.
        'PRONTO': pronto,
        # A unidade de trabalho desta capacidade, quando ela tem uma. `None` e
        # a declaracao honesta de que esta operacao nao e retomavel por metades.
        'UNIDADE': unidade,
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
    """→ a funcao de nivel de adaptador, ou None."""
    r = adaptador_de(plataforma, capacidade)
    return r['EXECUTA'] if r else None


def sonda_de(plataforma, capacidade):
    """→ a sonda gratuita de prontidao do adaptador, ou None."""
    r = adaptador_de(plataforma, capacidade)
    return r.get('PRONTO') if r else None


def rota_de(plataforma, capacidade):
    """→ a funcao crua que `social_rotas` despacha, ou None."""
    r = adaptador_de(plataforma, capacidade)
    return r.get('ROTA') if r else None


def tem_caminho(plataforma, capacidade):
    """Ha por onde coletar isto? Qualquer um dos dois papeis serve."""
    r = adaptador_de(plataforma, capacidade)
    return bool(r and (r['EXECUTA'] or r.get('ROTA')))


def registados():
    return dict(_MAPA)


def adaptadores():
    """Os nomes dos modulos adaptadores, sem repetir."""
    return tuple(sorted({r['ADAPTADOR'] for r in _MAPA.values()}))


def do_adaptador(nome):
    return {k: v for k, v in sorted(_MAPA.items()) if v['ADAPTADOR'] == nome}


def executaveis():
    """So as capacidades que tem caminho E prometem resultado."""
    return {k: v for k, v in sorted(_MAPA.items())
            if (v['EXECUTA'] is not None or v.get('ROTA') is not None)
            and cap.promete_resultado(v['CAPABILITY'])}


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
