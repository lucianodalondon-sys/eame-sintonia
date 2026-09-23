#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O UNIVERSO É PERGUNTADO ANTES DA REDE — YT2, 2026-09-23.

Nasceu do canário real YT1: o pedido do áudio do YouTube sem `universo` colheu
o vídeo e transcreveu-o (5,5 min de rede e de ASR) e só então morreu em
`UniversoNaoDeclarado`, sem recibo. A lei não muda (o universo vem do PEDIDO,
sem fallback para o alvo — `tests/test_universo_vem_do_pedido.py`); muda o
QUANDO: a pergunta obrigatória faz-se antes de gastar.

E o irmão que apareceu ao lado: `FILTRO_NAO_CONSUMIDO` recusava antes da rede e
depois rebentava no manifesto. Uma recusa não é corrida; não vai ao manifesto.

⚠️ NENHUMA PROVA AQUI ABRE A REDE NEM CHAMA O EXECUTOR: `subprocess.run` do
orquestrador é trocado por um espião que regista e pára.
"""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for gaveta in ('orquestrador', 'pedido', 'coleta', 'leis', 'admissao'):
    sys.path.insert(0, os.path.join(RAIZ, gaveta))
sys.path.insert(0, RAIZ)

import orquestrador as O                    # noqa: E402
import pedido as pd                         # noqa: E402

VIDEO = '7Ps4g3juOIU'


class _Parou(Exception):
    """O espião parou a corrida no executor — chegou lá, que é o que se mede."""


def _pedido(**extra):
    p = pd.de_uma_frase('colete agricultores')
    p.filtros.update({'fase': 'audio-youtube', 'fonte': 'IT-T8-001',
                      'video': VIDEO, 'pais': 'IT', **extra})
    return p


class _Espiao:
    def __init__(self):
        self.chamadas = []

    def __call__(self, cmd, *a, **k):
        # `git log` é a versão do executor (`versao_do_executor`), e não a
        # colheita: responde-se-lhe, e só o EXECUTOR é contado e parado.
        if cmd and cmd[0] == 'git':
            import subprocess as _sp
            return _sp.CompletedProcess(cmd, 0, stdout='abc1234', stderr='')
        self.chamadas.append(cmd)
        raise _Parou()


class SemUniversoNaoSeGastaNada(unittest.TestCase):

    def test_1_sem_universo_recusa_com_nome(self):
        esp = _Espiao()
        with mock.patch.object(O.subprocess, 'run', esp):
            r = O.correr(_pedido())
        self.assertEqual('UNIVERSO_NAO_DECLARADO', r['STATUS'])
        self.assertIn('UNIVERSO_NAO_DECLARADO', r['ERROR'])

    def test_2_e_o_executor_NAO_e_chamado(self):
        """A prova que falha com o defeito: a recusa vinha depois da colheita."""
        esp = _Espiao()
        with mock.patch.object(O.subprocess, 'run', esp):
            O.correr(_pedido())
        self.assertEqual([], esp.chamadas, 'o executor correu sem universo declarado')

    def test_3_confissao_de_ausencia_tambem_recusa_antes(self):
        for v in ('', '  ', 'NAO SEI'):
            esp = _Espiao()
            with mock.patch.object(O.subprocess, 'run', esp):
                r = O.correr(_pedido(universo=v))
            self.assertEqual('UNIVERSO_NAO_DECLARADO', r['STATUS'], repr(v))
            self.assertEqual([], esp.chamadas, repr(v))

    def test_4_o_alvo_T8_da_frase_NAO_e_usado_como_universo(self):
        """ALVO != UNIVERSO: «colete agricultores» é T8 e continua a não bastar."""
        p = _pedido()
        self.assertEqual('T8', p.alvo)
        with mock.patch.object(O.subprocess, 'run', _Espiao()):
            self.assertEqual('UNIVERSO_NAO_DECLARADO', O.correr(p)['STATUS'])


class ComUniversoAPassagemContinua(unittest.TestCase):

    def test_5_com_universo_chega_ao_executor(self):
        """Controlo positivo: a verificação nova não fecha o caminho de quem declarou."""
        # O orquestrador apanha a falha do executor e escreve FAILED — o espião
        # parar não propaga. Mede-se o que importa: o executor FOI chamado.
        esp = _Espiao()
        with mock.patch.object(O.subprocess, 'run', esp):
            r = O.correr(_pedido(universo='T8'))
        self.assertEqual(1, len(esp.chamadas), 'o executor não foi chamado')
        self.assertNotEqual('UNIVERSO_NAO_DECLARADO', r['STATUS'])

    def test_6_o_seco_nao_chega_a_porta_e_nao_e_recusado(self):
        """`--seco` prova o caminho sem porta: a pergunta não se aplica a ele."""
        esp = _Espiao()
        with mock.patch.object(O.subprocess, 'run', esp):
            r = O.correr(_pedido(), seco=True)
        self.assertNotEqual('UNIVERSO_NAO_DECLARADO', r['STATUS'])
        self.assertEqual([], esp.chamadas)


class ARecusaNaoVaiAoManifesto(unittest.TestCase):
    """`main()` com uma recusa: diz porquê, sai com 1, e não escreve recibo."""

    def _main(self, *filtros):
        argv = ['orquestrador.py', 'colete agricultores',
                '--filtro', 'fase=audio-youtube', '--filtro', 'fonte=IT-T8-001',
                '--filtro', 'video=%s' % VIDEO, '--filtro', 'pais=IT']
        for f in filtros:
            argv += ['--filtro', f]
        guardado = []
        saida = io.StringIO()
        with mock.patch.object(sys, 'argv', argv), \
                mock.patch.object(O, 'guardar_recibo', lambda r: guardado.append(r)), \
                mock.patch.object(O.subprocess, 'run', _Espiao()), \
                redirect_stdout(saida):
            rc = O.main()
        return rc, guardado, saida.getvalue()

    def test_7_universo_ausente_sai_1_sem_traceback_e_sem_manifesto(self):
        rc, guardado, txt = self._main()
        self.assertEqual(1, rc)
        self.assertEqual([], guardado, 'uma recusa foi escrita no manifesto')
        self.assertIn('NAO CORREU · UNIVERSO_NAO_DECLARADO', txt)

    def test_8_filtro_nao_consumido_idem(self):
        """O irmão que rebentava com «STATUS fora do contrato»."""
        rc, guardado, txt = self._main('universo=T8', 'inventado=1')
        self.assertEqual(1, rc)
        self.assertEqual([], guardado)
        self.assertIn('NAO CORREU · FILTRO_NAO_CONSUMIDO', txt)


if __name__ == '__main__':
    unittest.main(verbosity=2)
