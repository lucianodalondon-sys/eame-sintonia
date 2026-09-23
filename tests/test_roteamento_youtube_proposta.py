#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC3 · a proposta «o YouTube é sempre o Scrap», guardada ANTES de ser aplicada.

O bloco proposto vive, por agora, em `provas/roteamento_youtube_proposta.py`
(`promover_o_scrap`). Quando o engenheiro do Scrap o colar em
`pedido/receitas.py::resolver`, estes testes passam a importar dali — e as
mesmas quatro frases têm de continuar verdade.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
sys.path.insert(0, os.path.join(RAIZ, 'provas'))
import roteamento_youtube_proposta as RP  # noqa: E402


class OYoutubeESempreOScrap(unittest.TestCase):
    def test_os_50_canais_vao_ao_scrap_em_qualquer_territorio(self):
        linhas = RP.medir()
        self.assertEqual(len(linhas), 50)
        self.assertEqual({l['PROPOSTA'] for l in linhas}, {('scrap-colheita', 'OK')})

    def test_hoje_44_nao_chegam_ao_scrap(self):
        # A medida que justifica a proposta. Se este número mudar, a proposta
        # (ou a árvore) mudou — relê-la antes de aplicar.
        fora = [l for l in RP.medir() if l['HOJE'][0] != 'scrap-colheita']
        self.assertEqual(len(fora), 44)

    def test_pedido_sem_fase_nao_muda(self):
        execs = [{'id': 'italia-recorrente'}]
        self.assertIs(RP.promover_o_scrap(execs, ''), execs)
        self.assertIs(RP.promover_o_scrap(execs, 'fase-que-nao-e-do-scrap'), execs)

    def test_a_lista_de_fases_e_a_do_registo_do_scrap(self):
        scrap = {'id': 'scrap-colheita', 'serve_fases': ['canal-youtube']}
        outro = {'id': 'italia-recorrente'}
        reg = {'T9': [scrap]}
        self.assertEqual(RP.promover_o_scrap([outro], 'canal-youtube', reg), [scrap, outro])
        self.assertEqual(RP.promover_o_scrap([outro], 'audio-youtube', reg), [outro],
                         'fase que o registo nao declara nao promove ninguem')
        self.assertEqual(RP.promover_o_scrap([scrap, outro], 'canal-youtube', reg), [scrap, outro],
                         'nunca duplica o executor')


if __name__ == '__main__':
    unittest.main()
