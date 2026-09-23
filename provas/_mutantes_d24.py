#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROVA DOS MUTANTES DO D24: `test_d24_video_de_pessoa` tem de MORRER quando
uma rota de PESSOA muda, ou quando uma porta proibida se abre.

    py provas/_mutantes_d24.py

Seis mutacoes, uma de cada vez, e a expectativa e sempre a mesma: um teste que
continua verde depois de a rota mudar nao guarda nada. Depois de cada mutacao, a
matriz e RESTAURADA, para que a mutacao seguinte seja medida sozinha.
"""
import copy
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in ('coleta', 'leis', 'regras', 'pedido', ''):
    sys.path.insert(0, os.path.join(RAIZ, g) if g else RAIZ)
import _gavetas  # noqa: F401
import social_matriz as mz


def corre():
    suite = unittest.TestLoader().loadTestsFromName('tests.test_d24_video_de_pessoa')
    r = unittest.TextTestRunner(verbosity=0, stream=io.StringIO()).run(suite)
    return len(r.failures) + len(r.errors)


def rota(cap, nome):
    for r in mz.MATRIZ['LINKEDIN'][cap]:
        if r.get('ROTA') == nome:
            return r
    raise KeyError(nome)


MUTACOES = []


def mutacao(titulo, muda):
    MUTACOES.append((titulo, muda))


def _m_estado():
    r = rota('FETCH_VIDEO_BYTES', 'linkedin:data-sources-mp4-de-pessoa')
    r['ESTADO'] = 'BLOCKED'


def _m_dono():
    r = rota('FETCH_VIDEO_BYTES', 'linkedin:data-sources-mp4-de-pessoa')
    r['OWNER_AUTHORIZED'] = 'NAO'


def _m_limite():
    r = rota('FETCH_VIDEO_BYTES', 'linkedin:data-sources-mp4-de-pessoa')
    r['LIMITE'] = 'PUBLIC_ORG_VIDEO_ONLY'


def _m_nota():
    r = rota('FETCH_VIDEO_BYTES', 'linkedin:data-sources-mp4-de-pessoa')
    r['NOTA'] = 'aquisicao medida, sem nome de decisao nenhum'


def _m_renomeia():
    r = rota('FETCH_VIDEO_BYTES', 'linkedin:data-sources-mp4-de-pessoa')
    r['ROTA'] = 'linkedin:contatos-de-pessoa'


def _m_abre_porta_proibida():
    """A porta que o dono NAO autorizou, aberta como se estivesse autorizada.

    ⚠️ A MUTACAO NAO ESCREVE `PERMITIDA` — ela MUDA o valor de uma rota que ja
    existe. Ha uma prova nesta casa (`tests/test_c10_4_route_gate`) que exige
    que `PERMITIDA` seja ESCRITA so pela matriz, e ela esta certa: um mutante
    que declarasse politica seria um SEGUNDO DONO DA POLITICA disfarcado de
    prova. Mutar um valor nao e declarar uma lei.

    (E foi medido: a primeira versao deste mutante criava a rota com
    `PERMITIDA=` dentro de um dicionario, e a sonda daquela prova apanhou-o —
    corretamente. O mutante mudou; a prova nao.)
    """
    r = rota('DISCOVER_ACCOUNT', 'linkedin:perfil-publico-de-pessoa')
    r['ROTA'] = 'linkedin:contatos-de-pessoa'
    r['ESTADO'] = 'PROVED'
    r['PERMITIDA'] = 'SIM'


mutacao('o ESTADO da rota de pessoa muda', _m_estado)
mutacao('o dono deixa de estar autorizado na rota de pessoa', _m_dono)
mutacao('o LIMITE da rota de pessoa vira o da organizacao', _m_limite)
mutacao('a NOTA da rota de pessoa perde o nome da decisao', _m_nota)
mutacao('a rota de pessoa ganha nome de conteudo pessoal', _m_renomeia)
mutacao('a porta de CONTATOS aparece autorizada', _m_abre_porta_proibida)

sobreviveram = 0
print('MUTANTES DO D24 — %d mutacoes\n' % len(MUTACOES))
for titulo, muda in MUTACOES:
    antes = copy.deepcopy(mz.MATRIZ)
    try:
        muda()
        mortas = corre()
    finally:
        mz.MATRIZ.clear()
        mz.MATRIZ.update(copy.deepcopy(antes))
    marca = 'MORREU' if mortas else 'SOBREVIVEU'
    sobreviveram += 0 if mortas else 1
    print('  %-52s %-9s (%d prova(s) cairam)' % (titulo, marca, mortas))

print('\nMUTANTES = %d · SOBREVIVERAM = %d' % (len(MUTACOES), sobreviveram))
raise SystemExit(1 if sobreviveram else 0)
