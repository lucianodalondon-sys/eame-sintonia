# -*- coding: utf-8 -*-
"""YT-403 (27/09, D92) — o audio do YouTube que nao vem e FAILED, com o nome certo; o yt-dlp da casa; os avisos voltam.

Medido na volta 2A do maestro (volta-2A-b-2231): 1/4 videos com audio; 3/4 «HTTP Error 403: Forbidden» no googlevideo
(1 pedido cada, depois de 2 a youtube.com) — e as quatro linhas diziam SUCCESS. Antes, na volta-2A-2226, o
`yt_dlp` nem importava («No module named yt_dlp») e tambem SUCCESS.

NENHUMA PROVA AQUI ABRE A REDE: o yt-dlp e substituido por um pacote falso numa pasta temporaria, e a rota
pelo motivo que o yt-dlp real escreveu.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for gaveta in ('pedido', 'coleta', 'leis', 'ferramentas'):
    sys.path.insert(0, os.path.join(RAIZ, gaveta))
sys.path.insert(0, RAIZ)

import adaptador_youtube as AY        # noqa: E402
import scrap_colheita as SC           # noqa: E402
import retorno_da_coleta as rc        # noqa: E402
import youtube_transcrever as ytv     # noqa: E402
import yt_dlp_com_freio as FREIO      # noqa: E402

ERRO_403 = 'ERROR: unable to download video data: HTTP Error 403: Forbidden'
AVISO_JS = ('WARNING: [youtube] No supported JavaScript runtime could be found. Only deno is enabled by default; '
            'YouTube extraction without a JS runtime has been deprecated, and some formats may be missing.')


class A_ONomeDaFalha(unittest.TestCase):
    def test_403_do_googlevideo_e_blocked(self):
        self.assertEqual(AY._classificar_falha('YT_DLP_NAO_ENTREGOU: ' + ERRO_403), 'BLOCKED')

    def test_yt_dlp_que_nao_importa_e_defeito_nosso(self):
        m = "YT_DLP_NAO_ENTREGOU: ModuleNotFoundError: No module named 'yt_dlp'"
        self.assertEqual(AY._classificar_falha(m), 'EXECUTOR_UNAVAILABLE')

    def test_o_aviso_nao_decide_so_o_erro(self):
        m = 'YT_DLP_NAO_ENTREGOU: %s | WARNING: [youtube] some formats are unavailable' % ERRO_403
        self.assertEqual(AY._classificar_falha(m), 'BLOCKED')
        self.assertEqual(AY._classificar_falha('YT_DLP_NAO_ENTREGOU: ERROR: [youtube] X: Video unavailable'),
                         'SOURCE_GONE')
        m = 'YT_DLP_NAO_ENTREGOU: ERROR: HTTP Error 500 | WARNING: [youtube] some formats are unavailable'
        self.assertEqual(AY._classificar_falha(m), 'SOURCE_UNAVAILABLE')

    def test_a_rota_levanta_blocked_com_a_frase_inteira(self):
        with mock.patch.object(ytv, '_audio', return_value=(None, 'YT_DLP_NAO_ENTREGOU: %s | %s' % (ERRO_403, AVISO_JS))), \
             mock.patch.object(AY.http, 'contar_de_fora'):
            with self.assertRaises(AY._EstadoDaApi) as c:
                AY.youtube_audio_publico(run_id='R', country_scope='IT', video_id='HfTvWjFwsvQ')
        self.assertEqual(c.exception.rel['STATE'], 'BLOCKED')
        self.assertIn('403', c.exception.rel['DETALHE'])
        self.assertIn('JavaScript runtime', c.exception.rel['DETALHE'])


class B_OsAvisosVoltam(unittest.TestCase):
    def test_sem_no_warnings_e_a_fatia_por_omissao_fica(self):
        with mock.patch.dict(os.environ, {'SINTONIA_YT_FATIA': ''}):
            a = ytv.argumentos_do_yt_dlp('X')
        self.assertNotIn('--no-warnings', a)
        self.assertEqual(a[a.index('--http-chunk-size') + 1], '50M')

    def test_a_fatia_troca_se_pelo_ambiente(self):
        with mock.patch.dict(os.environ, {'SINTONIA_YT_FATIA': '0'}):
            self.assertNotIn('--http-chunk-size', ytv.argumentos_do_yt_dlp('X'))
        with mock.patch.dict(os.environ, {'SINTONIA_YT_FATIA': '10M'}):
            a = ytv.argumentos_do_yt_dlp('X')
            self.assertEqual(a[a.index('--http-chunk-size') + 1], '10M')
        with mock.patch.dict(os.environ, {'SINTONIA_YT_FATIA': 'grande'}), self.assertRaises(ValueError):
            ytv.argumentos_do_yt_dlp('X')

    def test_o_motivo_leva_o_erro_e_os_avisos(self):
        m = ytv._motivo_do_yt_dlp('\n'.join([AVISO_JS, 'WARNING: [youtube] outro aviso', ERRO_403]), '')
        self.assertTrue(m.startswith(ERRO_403), m)
        self.assertIn('JavaScript runtime', m)
        self.assertLessEqual(len(m), 600)
        self.assertEqual(ytv._motivo_do_yt_dlp('', ''), 'sem mensagem')


def _yt_dlp_falso(pasta, marca):
    p = os.path.join(pasta, 'yt_dlp')
    os.makedirs(p)
    with open(os.path.join(p, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write('class YoutubeDL:\n    def urlopen(self, req):\n        return None\n\n'
                'def main(argv=None):\n    print(%r, argv)\n    return 0\n' % marca)


class C_OYtDlpDaCasa(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='yt403-')
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_a_pasta_nomeada_vai_a_frente_e_o_filho_usa_a(self):
        _yt_dlp_falso(self.tmp, 'YT_DLP_DA_CASA')
        env = dict(os.environ, SINTONIA_YT_DLP_DIR=self.tmp, PYTHONPATH='', SINTONIA_TETO_ONDA='')
        r = subprocess.run([sys.executable, FREIO.__file__, '--version'], capture_output=True, text=True,
                           encoding='utf-8', errors='replace', env=env, timeout=120)
        self.assertIn('YT_DLP_DA_CASA', r.stdout, r.stdout + r.stderr)
        with mock.patch.dict(os.environ, {'SINTONIA_YT_DLP_DIR': self.tmp}):
            self.assertEqual(FREIO.yt_dlp_disponivel(), (True, self.tmp))

    def test_sem_yt_dlp_em_lado_nenhum_o_check_diz_executor_unavailable_sem_rede(self):
        with mock.patch.dict(os.environ, {'SINTONIA_YT_DLP_DIR': ''}), \
             mock.patch.object(FREIO, 'PASTA_DA_CASA', os.path.join(self.tmp, 'nada')), \
             mock.patch.object(FREIO.importlib.util, 'find_spec', return_value=None):
            self.assertEqual(FREIO.yt_dlp_disponivel(), (False, None))
        with mock.patch.object(AY, '_yt_dlp_do_freio', return_value=(False, None)), \
             mock.patch('shutil.which', return_value='C:/x/ffmpeg.exe'):
            self.assertEqual(AY.pronto_para_audio_publico(), (False, 'EXECUTOR_UNAVAILABLE'))
        with mock.patch.object(AY, '_yt_dlp_do_freio', return_value=(True, self.tmp)), \
             mock.patch('shutil.which', return_value='C:/x/ffmpeg.exe'):
            self.assertEqual(AY.pronto_para_audio_publico(), (True, ''))

    def test_o_check_ja_nao_pergunta_pelo_programa_yt_dlp(self):
        vistos = []
        with mock.patch.object(AY, '_yt_dlp_do_freio', return_value=(True, self.tmp)), \
             mock.patch('shutil.which', side_effect=lambda n: vistos.append(n) or 'C:/x/' + n):
            AY.pronto_para_audio_publico()
        self.assertNotIn('yt-dlp', vistos)


class D_ZeroPorqueFalhouEFailed(unittest.TestCase):
    def _trace(self, result, erro=''):
        return {'RESULT': result, 'COST_STATE': 'ZERO', 'ROUTER_RECORD': {'ERRO': erro}}

    def test_403_sem_colheita_e_failed_e_diz_porque(self):
        t = self._trace('BLOCKED', 'BLOCKED (razao nativa: AUDIO_NAO_OBTIDO): YT_DLP_NAO_ENTREGOU: ' + ERRO_403)
        with mock.patch.object(SC.sx, 'COLLECT', return_value=([], t)):
            env = SC.colher('audio-youtube', run_id='IT-T8-X', fonte='IT-T8-004', video_id='HfTvWjFwsvQ')
        self.assertEqual(env['ESTADO'], rc.FAILED)
        self.assertIn('FALHOU', env['PORQUE_ZERO_COLHEITA'])
        self.assertIn('403', env['PORQUE_ZERO_COLHEITA'])
        self.assertNotIn('ZERO LEGÍTIMO NÃO É FALHA', env['PORQUE_ZERO_COLHEITA'])

    def test_executor_ausente_sem_colheita_e_failed(self):
        with mock.patch.object(SC.sx, 'COLLECT', return_value=([], self._trace('EXECUTOR_UNAVAILABLE'))):
            env = SC.colher('audio-youtube', run_id='IT-T8-X', fonte='IT-T8-004', video_id='HfTvWjFwsvQ')
        self.assertEqual(env['ESTADO'], rc.FAILED)

    def test_zero_de_verdade_continua_zero_legitimo(self):
        with mock.patch.object(SC.sx, 'COLLECT', return_value=([], self._trace('ZERO_RESULTS'))):
            env = SC.colher('audio-youtube', run_id='IT-T8-X', fonte='IT-T8-004', video_id='HfTvWjFwsvQ')
        self.assertNotEqual(env['ESTADO'], rc.FAILED)
        self.assertIn('ZERO LEGÍTIMO', env['PORQUE_ZERO_COLHEITA'])

    def _main(self, estado):
        env = {'RUN_ID': 'R', 'ESTADO': estado, 'COLHEITA': [], 'SUPORTE': [], 'ERROS': [],
               'ESPECIE_DA_FASE': rc.COLHEITA}
        with mock.patch.object(SC, 'colher', return_value=env), \
             mock.patch.object(SC, 'escrever', return_value=os.path.join(RAIZ, 'x.json')), \
             mock.patch.object(SC, 'escrever_linha'), \
             mock.patch.object(SC, '_livro_da_corrida_se_faltar', return_value=None), \
             mock.patch.object(SC, '_largar_livro_proprio'), \
             mock.patch.object(SC.rc, 'conferir', return_value=[]), \
             mock.patch('builtins.print'):
            return SC.main(['audio-youtube', 'IT-T8-004', '--video=HfTvWjFwsvQ', '--run-id=R'])

    def test_o_processo_sai_com_falha_e_o_orquestrador_grava_failed(self):
        self.assertEqual(self._main(rc.FAILED), 3)
        self.assertEqual(self._main(rc.PARTIAL), 0)
        self.assertEqual(self._main(rc.SUCCESS), 0)


if __name__ == '__main__':
    unittest.main()
