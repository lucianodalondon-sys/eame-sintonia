#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROVA DOS MUTANTES DO YT-METADADOS.

    python provas/_mutantes_yt_metadados.py

O que se espera de cada mutacao: que `tests/test_yt_metadados_do_audio` MORRA.
Um teste que continua verde depois de a lei mudar nao guarda nada.

Sao DUAS especies de mutacao, e a diferenca importa:

    MATRIZ   mexe na lei (o carimbo do dono, a politica da plataforma) — a lei
             tem UM dono, e o objeto tem de a seguir.
    CODIGO   mexe no leitor do que a plataforma declara (a data, os campos) —
             e o teste mede o leitor a serio, nao um duble.

Depois de cada mutacao, TUDO e restaurado, para que a seguinte seja medida
sozinha.

    RODAR COM `python` (o interpretador que tem o ambiente), como o teste.
"""
import copy
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _g in ('coleta', 'leis', 'regras', 'guarda', 'pedido', 'superficie', 'ferramentas', ''):
    sys.path.insert(0, os.path.join(RAIZ, _g) if _g else RAIZ)
import _gavetas  # noqa: F401
import social_matriz as mz          # noqa: E402
import youtube_transcrever as ytv   # noqa: E402


def corre():
    suite = unittest.TestLoader().loadTestsFromName('tests.test_yt_metadados_do_audio')
    r = unittest.TextTestRunner(verbosity=0, stream=io.StringIO()).run(suite)
    return len(r.failures) + len(r.errors)


def rota():
    return mz.MATRIZ['YOUTUBE']['FETCH_AUDIO_BYTES'][0]


MUTACOES = []


def mutacao(titulo, muda):
    MUTACOES.append((titulo, muda))


# ── MUTACOES DA LEI (a matriz) ──────────────────────────────────────────────
def _m_dono_deixa_de_autorizar():
    rota()['OWNER_AUTHORIZED'] = 'NAO'


def _m_politica_deixa_de_estar_medida():
    """Apagar o eixo da plataforma e esconder a proibicao — a casa proibe isso."""
    rota()['PLATFORM_POLICY_STATUS'] = 'NOT_MEASURED'


def _m_limite_vira_de_video_de_pessoa():
    rota()['LIMITE'] = 'PUBLIC_PERSON_VIDEO_ONLY'


# ── MUTACOES DO LEITOR (o codigo que le o que a plataforma declara) ─────────
_ORIG_DECLARADO_EM = ytv.declarado_em
_ORIG_CAMPOS = ytv.CAMPOS_PUBLICOS


def _m_data_fabricada_a_partir_do_dia():
    """A plataforma deu so o DIA, e o leitor inventa-lhe uma hora."""
    ytv.declarado_em = lambda md: ('%s-%s-%sT12:00:00Z' % (
        str(md.get('upload_date'))[:4], str(md.get('upload_date'))[4:6],
        str(md.get('upload_date'))[6:8]) if md.get('upload_date') else ('NAO SEI', 'NAO DECLARADA'),
        'SECOND')


def _m_canal_sai_dos_campos_lidos():
    ytv.CAMPOS_PUBLICOS = tuple(c for c in _ORIG_CAMPOS if c != 'channel_id')


def _m_publicacao_vira_fact_time():
    """A mutacao que a casa mais teme: colapsar dois tempos num so.

    Ela NAO muda o adaptador (isso seria escrever codigo); muda o LEITOR, de
    forma a que a data declarada passe a ser devolvida como se fosse o tempo do
    facto. Se o teste nao apanhar isto, `FACT_TIME` deixou de estar guardado.
    """
    _orig = ytv.declarado_em

    def trocado(md):
        iso, prec = _orig(md)
        return iso, 'FACT_TIME'
    ytv.declarado_em = trocado


mutacao('a MATRIZ deixa de autorizar a rota do audio', _m_dono_deixa_de_autorizar)
mutacao('a MATRIZ deixa de ter a politica da plataforma medida',
        _m_politica_deixa_de_estar_medida)
mutacao('a MATRIZ troca o limite do audio pelo de video de pessoa',
        _m_limite_vira_de_video_de_pessoa)
mutacao('o leitor fabrica a hora que a plataforma nao deu',
        _m_data_fabricada_a_partir_do_dia)
mutacao('o canal sai da lista de campos lidos', _m_canal_sai_dos_campos_lidos)
mutacao('a data declarada passa a ser devolvida como tempo do facto',
        _m_publicacao_vira_fact_time)

#: As mutacoes de lei mexem na matriz; as de leitor mexem em modulos. Cada uma
#: guarda o que lhe pertence e devolve-o no fim.
_MATRIZ = copy.deepcopy(mz.MATRIZ)

sobreviveram = 0
print('MUTANTES DO YT-METADADOS — %d mutacoes\n' % len(MUTACOES))
for titulo, muda in MUTACOES:
    antes_matriz = copy.deepcopy(mz.MATRIZ)
    antes_declarado, antes_campos = ytv.declarado_em, ytv.CAMPOS_PUBLICOS
    try:
        muda()
        mortas = corre()
    finally:
        mz.MATRIZ.clear()
        mz.MATRIZ.update(copy.deepcopy(_MATRIZ))
        ytv.declarado_em = antes_declarado
        ytv.CAMPOS_PUBLICOS = antes_campos
    marca = 'MORREU' if mortas else 'SOBREVIVEU'
    sobreviveram += 0 if mortas else 1
    print('  %-56s %-10s (%d prova(s) cairam)' % (titulo, marca, mortas))

print('\nMUTANTES = %d · SOBREVIVERAM = %d' % (len(MUTACOES), sobreviveram))
raise SystemExit(1 if sobreviveram else 0)
