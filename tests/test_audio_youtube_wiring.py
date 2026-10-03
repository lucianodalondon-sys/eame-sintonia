#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DO WIRING — o áudio público alcançável PELO PEDIDO.

O C13 provou o degrau de baixo: `scrap_executor → adaptador_youtube → _audio`.
Esta suite prova o degrau de CIMA, que faltava e que parou o canário real:

    REQUEST → pedido/receitas → scrap_colheita → capability

Porque as duas coisas não são a mesma, e a diferença já custou uma missão:

    CAPABILITY PROVEN != EDGE WIRED != COLLECTION REACHABLE

`youtube.public_audio` estava PROVEN, tinha rota no `scrap_registo._MAPA`, e o
`CHECK` respondia `CAN_COLLECT_NOW`. E mesmo assim nenhum pedido conseguia
pedi-la, porque **não havia fase**. O edge verde escondeu a falta.

NENHUMA PROVA AQUI ABRE A REDE nem chama `yt-dlp`. A rota é substituída no
ponto certo e devolve o envelope que o contrato real devolve — medido em
`coleta/adaptador_youtube.py::youtube_audio_publico`, não inventado.
"""
import os
import socket
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for gaveta in ('pedido', 'coleta', 'leis', 'ferramentas'):
    sys.path.insert(0, os.path.join(RAIZ, gaveta))
sys.path.insert(0, RAIZ)

import receitas                                    # noqa: E402
from pedido import Pedido                          # noqa: E402
import scrap_colheita as SC                        # noqa: E402
import scrap_registo as SR                         # noqa: E402
import adaptador_youtube                           # noqa: E402  (regista as rotas)

FASE = 'audio-youtube'
VIDEO = '7Ps4g3juOIU'
FONTE = 'IT-T8-001'
CAPABILITY = 'youtube.public_audio'


class _SemRede:
    """Qualquer socket aberto dentro do bloco é uma falha, não um aviso."""

    def __enter__(self):
        self.chamadas = []
        self._orig = socket.socket.connect

        def espiao(_self, endereco, *a, **k):
            self.chamadas.append(endereco)
            raise AssertionError('A PROVA ABRIU A REDE: %r' % (endereco,))

        socket.socket.connect = espiao
        return self

    def __exit__(self, *e):
        socket.socket.connect = self._orig
        return False


def _envelope_falso(**kw):
    """O que a rota real devolve — campos copiados do contrato, não inventados."""
    return [{
        'OBJECT_KIND': 'PUBLIC_AUDIO',
        'VIDEO_ID': kw.get('video_id') or VIDEO,
        'SOURCE_URL': 'https://www.youtube.com/watch?v=%s' % (kw.get('video_id') or VIDEO),
        'RUN_ID': kw.get('run_id'),
        'MEDIA_KIND': 'AUDIO',
        'AUDIO_REFERENCE': os.path.join('descartavel', 'som.m4a'),
        'AUDIO_BYTES': 4096,
        'AUDIO_SHA256': 'f' * 64,
        'AUDIO_DURATION_S': 222,
        'STREAMS': {'AUDIO': 1, 'VIDEO': 0},
        'PARENT': {'KIND': 'VIDEO', 'VIDEO_ID': kw.get('video_id') or VIDEO},
    }]


class AFaseExiste(unittest.TestCase):

    def test_1_a_fase_esta_declarada(self):
        self.assertIn(FASE, SC.FASES)

    def test_2_a_fase_aponta_para_a_capability_certa(self):
        plataforma, capability, fixos, especie = SC.FASES[FASE]
        self.assertEqual('YOUTUBE', plataforma)
        self.assertEqual(CAPABILITY, capability)
        self.assertEqual({}, fixos, 'esta fase colhe UM video: nao ha teto')
        self.assertEqual('COLHEITA', especie,
                         'o som que o canal publicou e material observado, '
                         'nao uma lista de onde procurar')

    def test_3_a_especie_nao_e_catalog(self):
        self.assertNotEqual('CATALOG', SC.FASES[FASE][3])

    def test_4_o_filtro_nomeado_e_video_e_nao_fonte(self):
        self.assertEqual({'video': 'video_id'}, SC.NOMEADOS.get(FASE))
        self.assertNotIn('fonte', SC.NOMEADOS.get(FASE),
                         'VIDEO_ID != SOURCE_ID: a fase nao pode derivar o '
                         'video da source')


class OPedidoConsegueSelecionarAFase(unittest.TestCase):

    def test_5_o_executor_declara_servir_a_fase(self):
        ex = [e for e in receitas.EXECUTORES['T8'] if e['id'] == 'scrap-colheita'][0]
        self.assertIn(FASE, ex['serve_fases'])

    def test_6_o_plano_seco_escolhe_scrap_colheita(self):
        with _SemRede() as r:
            p = Pedido(alvo='T8', filtros={'fonte': FONTE, 'fase': FASE, 'video': VIDEO})
            execs = [e['id'] for e in receitas.resolver(p).executores]
        self.assertEqual('scrap-colheita', execs[0])
        self.assertEqual([], r.chamadas)

    def test_7_o_filtro_video_desce_pela_receita(self):
        ex = [e for e in receitas.EXECUTORES['T8'] if e['id'] == 'scrap-colheita'][0]
        self.assertIn('video', ex.get('filtros_nomeados') or [],
                      'sem isto o orquestrador nao passa --video e a fase '
                      'morre sem saber que video colher')

    def test_8_T8_continua_a_apontar_para_o_MESMO_executor_de_T9(self):
        t8 = [e for e in receitas.EXECUTORES['T8'] if e['id'] == 'scrap-colheita'][0]
        t9 = [e for e in receitas.EXECUTORES['T9'] if e['id'] == 'scrap-colheita'][0]
        self.assertIs(t8, t9, 'copia, nao referencia: dois donos divergem')


class AFaseChegaACapability(unittest.TestCase):
    """O que ninguém tinha provado: a fase realmente pede o áudio público."""

    def _colher_instrumentado(self, **filtros):
        """⚠️ A TRADUÇÃO NÃO ACONTECE AQUI, E ISSO FOI MEDIDO.

        `NOMEADOS` traduz o nome PÚBLICO (`--video`) para o nome que a rota
        recebe (`video_id`), e essa tradução vive no `main()` da linha de
        comando — `scrap_colheita.py:714`. `colher()` já recebe o nome
        traduzido.

        A primeira versão desta prova chamava `colher(video=...)` e via
        `video_id=None` chegar à rota. Parecia defeito do wiring; era defeito
        da prova. A tradução é testada em `test_4` e `test_22`, pela tabela;
        aqui exercita-se o caminho a jusante dela.

            ONDE A TRADUÇÃO VIVE É PARTE DO CONTRATO —
            E A PROVA TEM DE CHAMAR A FUNÇÃO PELO NOME QUE ELA ACEITA.
        """
        chamadas = []
        alvo = ('YOUTUBE', CAPABILITY)
        original = SR._MAPA[alvo]['ROTA']

        def rota_espia(**kw):
            chamadas.append(kw)
            return _envelope_falso(**kw)

        SR._MAPA[alvo]['ROTA'] = rota_espia
        try:
            with _SemRede() as r:
                saida = SC.colher(fase=FASE, run_id='PROVA-WIRING', **filtros)
            return saida, chamadas, r.chamadas
        finally:
            SR._MAPA[alvo]['ROTA'] = original

    def test_9_a_rota_e_chamada_uma_vez_so(self):
        _saida, chamadas, rede = self._colher_instrumentado(fonte=FONTE, video_id=VIDEO)
        self.assertEqual(1, len(chamadas), 'CALL_COUNT tem de ser 1')
        self.assertEqual([], rede, 'NETWORK_CALLS tem de ser 0')

    def test_10_o_video_id_do_pedido_chega_a_rota(self):
        _saida, chamadas, _ = self._colher_instrumentado(fonte=FONTE, video_id=VIDEO)
        self.assertEqual(VIDEO, chamadas[0].get('video_id'))

    def test_10b_a_tabela_traduz_video_para_video_id(self):
        """O degrau que o `main()` executa, provado pela tabela que o guia."""
        self.assertEqual('video_id', SC.NOMEADOS[FASE]['video'])

    def test_11_ha_exatamente_uma_rota_para_esta_capability(self):
        alvos = [k for k in SR._MAPA if k[1] == CAPABILITY]
        self.assertEqual(1, len(alvos), 'SECOND_PATH tem de ser 0')

    def test_12_a_rota_nao_recebe_o_source_id_como_video(self):
        _saida, chamadas, _ = self._colher_instrumentado(fonte=FONTE, video_id=VIDEO)
        kw = chamadas[0]
        self.assertNotEqual(FONTE, kw.get('video_id'),
                            'SOURCE_ID nunca pode viajar como VIDEO_ID')


class OObjetoVoltaComoColheita(unittest.TestCase):

    def _saida(self):
        alvo = ('YOUTUBE', CAPABILITY)
        original = SR._MAPA[alvo]['ROTA']
        SR._MAPA[alvo]['ROTA'] = lambda **kw: _envelope_falso(**kw)
        try:
            with _SemRede():
                return SC.colher(fase=FASE, run_id='PROVA-WIRING',
                                 fonte=FONTE, video_id=VIDEO)
        finally:
            SR._MAPA[alvo]['ROTA'] = original

    def test_13_a_especie_da_fase_e_colheita(self):
        self.assertEqual('COLHEITA', SC.FASES[FASE][3])

    def test_14_ha_uma_unidade_colhida(self):
        saida = self._saida()
        texto = str(saida)
        self.assertIn('PUBLIC_AUDIO', texto)

    def test_15_a_unidade_preserva_o_source_id_do_pedido(self):
        self.assertIn(FONTE, str(self._saida()),
                      'o SOURCE_ID desce com o pedido; nao se deriva da URL')

    def test_16_a_unidade_preserva_o_video_id_nativo(self):
        self.assertIn(VIDEO, str(self._saida()))

    def test_17_o_media_kind_e_audio_e_nao_video(self):
        texto = str(self._saida())
        self.assertIn("'MEDIA_KIND': 'AUDIO'", texto.replace('"', "'"))


class AsFalhasFecham(unittest.TestCase):
    """Uma porta que nunca diz «não» não é uma porta."""

    def test_18_sem_video_recusa_antes_da_rede(self):
        alvo = ('YOUTUBE', CAPABILITY)
        original = SR._MAPA[alvo]['ROTA']
        tocou = []
        SR._MAPA[alvo]['ROTA'] = lambda **kw: (tocou.append(kw), _envelope_falso(**kw))[1]
        try:
            with _SemRede() as r:
                try:
                    SC.colher(fase=FASE, run_id='X', fonte=FONTE)
                    faltou = not tocou
                except Exception:
                    faltou = True
            self.assertEqual([], r.chamadas, 'recusar DEPOIS da rede nao conta')
        finally:
            SR._MAPA[alvo]['ROTA'] = original

    def test_19_fase_inexistente_recusa(self):
        with _SemRede():
            with self.assertRaises(Exception):
                SC.colher(fase='audio-youtube-que-nao-existe', run_id='X',
                          fonte=FONTE, video=VIDEO)

    def test_20_sem_fase_nenhuma_recusa(self):
        with _SemRede():
            with self.assertRaises(Exception):
                SC.colher(fase='', run_id='X', fonte=FONTE, video=VIDEO)

    def test_21_uma_fonte_T8_qualquer_nao_cai_em_youtube(self):
        """T8 não é uma plataforma. Só a fase nomeada abre o YouTube."""
        with _SemRede():
            p = Pedido(alvo='T8', filtros={'fonte': 'IT-T8-002'})
            plano = receitas.resolver(p)
        self.assertNotIn('audio-youtube', str(plano.pedido.filtros),
                         'sem fase declarada ninguem pede audio')


class ONomeadoNaoAbreDemais(unittest.TestCase):

    def test_22_a_fase_nao_aceita_filtro_estranho(self):
        aceites = set(SC.NOMEADOS.get(FASE) or {})
        self.assertEqual({'video'}, aceites,
                         'a lista da fase FECHA; a da receita e que abre')

    def test_23_nenhuma_outra_fase_ganhou_public_audio(self):
        donas = [f for f, e in SC.FASES.items()
                 if isinstance(e, (tuple, list)) and e[1] == CAPABILITY]
        self.assertEqual([FASE], donas)


if __name__ == '__main__':
    unittest.main(verbosity=2)
