#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC4 · «o YouTube é sempre o Scrap», aplicado em `pedido/receitas.resolver`.

Quatro frases que têm de continuar verdade:
  1. os 50 canais da tabela abrem o Scrap, em qualquer território;
  2. sem a promoção, 44 não chegavam lá (a medida que justificou a mudança);
  3. pedido sem fase, ou com fase que não é do Scrap, não muda;
  4. a lista de fases é a do registo do Scrap, e o executor nunca se duplica.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
for p in ('provas', 'pedido'):
    sys.path.insert(0, os.path.join(RAIZ, p))
import pedido as PD                       # noqa: E402
import receitas as R                      # noqa: E402
import roteamento_youtube_proposta as RP  # noqa: E402


class OYoutubeESempreOScrap(unittest.TestCase):
    def test_os_50_canais_vao_ao_scrap_em_qualquer_territorio(self):
        linhas = RP.medir()
        self.assertEqual(len(linhas), 50)
        self.assertEqual({l['COM_PROMOCAO'] for l in linhas}, {('scrap-colheita', 'OK')})
        self.assertGreater(len({l['TERRITORY'] for l in linhas}), 2)

    def test_sem_a_promocao_44_nao_chegavam(self):
        fora = [l for l in RP.medir() if l['SEM_PROMOCAO'][0] != 'scrap-colheita']
        self.assertEqual(len(fora), 44)

    def test_pedido_sem_fase_nao_muda(self):
        for t in R.EXECUTORES:
            self.assertEqual(R.resolver(PD.Pedido(alvo=t, filtros={})).executores,
                             list(R.EXECUTORES.get(t, [])), t)
        execs = [{'id': 'italia-recorrente'}]
        self.assertIs(R.promover_o_scrap(execs, ''), execs)
        self.assertIs(R.promover_o_scrap(execs, 'fase-que-nao-e-do-scrap'), execs)

    def test_a_lista_de_fases_e_a_do_registo_do_scrap(self):
        scrap = {'id': 'scrap-colheita', 'serve_fases': ['canal-youtube']}
        outro = {'id': 'italia-recorrente'}
        reg = {'T9': [scrap]}
        self.assertEqual(R.promover_o_scrap([outro], 'canal-youtube', reg), [scrap, outro])
        self.assertEqual(R.promover_o_scrap([outro], 'audio-youtube', reg), [outro],
                         'fase que o registo nao declara nao promove ninguem')
        self.assertEqual(R.promover_o_scrap([scrap, outro], 'canal-youtube', reg), [scrap, outro],
                         'nunca duplica o executor')

    def test_o_resolver_chama_a_promocao(self):
        p = PD.Pedido(alvo='T12', filtros={'fase': 'canal-youtube', 'fonte': 'IT-T12-010',
                                           'canal_id': 'UCH_LCqE9qGb6TvpXwGudNbQ'})
        self.assertEqual(R.resolver(p).executores[0]['id'], 'scrap-colheita')


if __name__ == '__main__':
    unittest.main()
