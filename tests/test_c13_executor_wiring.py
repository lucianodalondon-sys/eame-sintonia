#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DO EDGE — o audio publico ligado ao executor canonico.

Nasceu do §151. A capacidade `youtube.public_audio` ja estava DECLARADA e ja
tinha rota na matriz, mas o `CHECK` respondia `CAN=False / DECLARED_WITHOUT_ROUTE`
— porque declarar uma porta e ter uma porta sao coisas diferentes.

    CAN DO != DID DO. E DECLARAR != LIGAR.

Este ficheiro prova o que passou a existir e, sobretudo, o que NAO pode passar a
existir: um segundo descarregador, um objeto que chama VIDEO ao som, e uma falha
de aquisicao disfarcada de `ZERO_RESULTS`.

NENHUMA PROVA AQUI ABRE A REDE. O `_audio` e substituido no ponto certo, e o
ficheiro que ele devolve e um WAV de verdade — construido pela biblioteca `wave`
do Python, para que medir os bytes nao exija gerar media nenhuma.
"""
import io
import os
import socket
import struct
import sys
import tempfile
import unittest
import wave

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import adaptador_youtube as ay     # noqa: E402
import fala_local as fl            # noqa: E402
import scrap_capacidades as cap    # noqa: E402
import scrap_executor as ex        # noqa: E402
import scrap_registo as reg        # noqa: E402
import social_envelope as env      # noqa: E402
import social_matriz as mz         # noqa: E402
import youtube_transcrever as ytv  # noqa: E402

PLAT = 'YOUTUBE'
AUDIO = 'youtube.public_audio'
CANARIO = 'zaEk8LE6SOQ'


def _wav_silencioso(caminho, segundos=1.0, taxa=16000):
    """Um WAV valido, sem `ffmpeg`. Quem o MEDE e que precisa do `ffprobe`."""
    n = int(taxa * segundos)
    with wave.open(caminho, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes(struct.pack('<%dh' % n, *([0] * n)))
    return caminho


def _tem_ffprobe():
    import shutil
    return bool(shutil.which('ffprobe'))


def _corpo(nome):
    """O texto de UMA funcao do adaptador, e so ela.

    Cortar ate ao fim do ficheiro era mentira: apanhava as notas do REGISTO, e
    uma delas fala de `ffmpeg` porque e isso que a rota USA. A prova tem de
    olhar para o corpo da funcao, e nao para o que vem depois dela.

    A funcao corta no primeiro `def` de topo, na primeira barra de seccao, ou
    no primeiro `reg.` — o que vier primeiro. As tres marcas existem porque
    nem toda a funcao e seguida de outra funcao.
    """
    fonte = open(ay.__file__, encoding='utf-8').read()
    resto = fonte[fonte.index('def %s(' % nome):]
    cortes = [resto.index(c, 1) for c in ('\ndef ', '\n# ═', '\nreg.')
              if c in resto[1:]]
    return resto[:min(cortes)] if cortes else resto


class _AudioEspiao:
    """Um `_audio` que conta as chamadas e devolve um ficheiro real.

    Ele existe para que a prova seja de DESPACHO e nao de download: o caminho
    canonico tem de chegar ate aqui UMA vez, e uma so.
    """

    def __init__(self, caminho=None, motivo=None):
        self.chamadas = []
        self._caminho = caminho
        self._motivo = motivo

    def __call__(self, video_id, *a, **k):
        self.chamadas.append(video_id)
        if self._caminho:
            return self._caminho, None
        return None, self._motivo


class ASondaNaoColeta(unittest.TestCase):
    """O CHECK pergunta «consigo chegar la?». Ele NAO vai la."""

    def setUp(self):
        self._dir = tempfile.mkdtemp(prefix='c13-wiring-')

    def _com_audio_espiao(self, fn):
        original = ytv._audio
        espiao = _AudioEspiao(caminho=_wav_silencioso(
            os.path.join(self._dir, 's.wav')))
        ytv._audio = espiao
        try:
            return fn(espiao)
        finally:
            ytv._audio = original

    def test_1_CHECK_nao_dispara_a_aquisicao(self):
        """A sonda le declaracao, registo e ambiente. Nao baixa nada."""
        def corre(espiao):
            d = ex.CHECK(PLAT, AUDIO)
            self.assertEqual(espiao.chamadas, [],
                             'o CHECK disparou a aquisicao: ele responde '
                             '«consigo chegar la?», e nao «vai la agora»')
            return d
        d = self._com_audio_espiao(corre)
        self.assertTrue(d['CAN'])
        self.assertEqual(d['STATE'], 'CAN_COLLECT_NOW')
        self.assertTrue(d['PRODUCTION_READY'])

    def test_2_CHECK_nao_abre_socket(self):
        """Com a rede proibida, o CHECK responde o mesmo."""
        original = socket.socket.connect
        socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(
            AssertionError('o CHECK abriu a rede'))
        try:
            d = ex.CHECK(PLAT, AUDIO)
        finally:
            socket.socket.connect = original
        self.assertTrue(d['CAN'])
        self.assertEqual(d['STATE'], 'CAN_COLLECT_NOW')

    def test_3_CHECK_custa_zero(self):
        """A pergunta e de graca. Um CHECK que custa dinheiro nao e um CHECK."""
        d = ex.CHECK(PLAT, AUDIO)
        self.assertEqual(d['COST_TO_CHECK_USD'], 0.0)

    def test_4_a_sonda_nao_toca_a_rede_nem_o_disco(self):
        """`pronto_para_audio_publico` so olha para o que esta instalado."""
        corpo = _corpo('pronto_para_audio_publico')
        for proibido in ('http.buscar', 'urllib', 'socket', 'subprocess',
                         'ytv._audio', 'Popen'):
            self.assertNotIn(proibido, corpo,
                             'a sonda de prontidao mexe em `%s` — ela tem de ser '
                             'gratuita e offline' % proibido)


class ODespachoCanonico(unittest.TestCase):
    """Uma volta so, pelo caminho canonico, e nenhuma porta lateral."""

    @classmethod
    def setUpClass(cls):
        cls._dir = tempfile.mkdtemp(prefix='c13-despacho-')
        cls._wav = _wav_silencioso(os.path.join(cls._dir, 'canario.wav'))

    def _despachar(self):
        original = ytv._audio
        espiao = _AudioEspiao(caminho=self._wav)
        ytv._audio = espiao
        try:
            objetos, trace = ex.COLLECT(
                platform=PLAT, capability=AUDIO,
                run_id='C13-WIRING-TESTE', scope='PONTUAL',
                video_id=CANARIO)
        finally:
            ytv._audio = original
        return objetos, trace, espiao

    def test_5_o_COLLECT_chega_ao_adaptador_e_a_aquisicao_uma_vez(self):
        objetos, trace, espiao = self._despachar()
        self.assertEqual(espiao.chamadas, [CANARIO],
                         'a implementacao de aquisicao foi chamada %d vez(es)'
                         % len(espiao.chamadas))
        self.assertEqual(len(objetos), 1)
        self.assertEqual(trace['EXECUTOR_ID'], 'SINTONIA_SCRAP')
        self.assertEqual(trace['ROUTE'], ay.ROTA_AUDIO_PUBLICO)
        self.assertEqual(trace['CAPABILITY'], AUDIO)

    def test_6_ha_exatamente_uma_rota_registada(self):
        """Uma porta so. Duas seriam duas verdades sobre a mesma aquisicao."""
        achados = [c for (p, c) in reg.registados() if p == PLAT and c == AUDIO]
        self.assertEqual(len(achados), 1)
        r = reg.rota_de(PLAT, AUDIO)
        self.assertTrue(callable(r))
        self.assertEqual(r.__name__, 'youtube_audio_publico')

    def test_7_a_capacidade_entra_pela_matriz_e_nao_por_atalho(self):
        """`rota=`, e nao `executa=`: quem tem matriz nao contorna o roteador."""
        d = reg.adaptador_de(PLAT, AUDIO)
        self.assertIsNone(d['EXECUTA'],
                          'a rota usa `executa=`, e isso passa ao lado de '
                          '`social_rotas` — a matriz deixaria de mandar')
        self.assertIsNotNone(d['ROTA'])
        self.assertEqual(cap.da_matriz(AUDIO), 'FETCH_AUDIO_BYTES')
        self.assertEqual(mz.decisao(PLAT, 'FETCH_AUDIO_BYTES')['DECISAO'], 'ALLOWED')

    def test_8_nao_ha_segundo_descarregador(self):
        """A implementacao continua a ser a que ja estava provada."""
        corpo = _corpo('youtube_audio_publico')
        self.assertIn('ytv._audio(', corpo,
                      'a rota deixou de chamar a implementacao provada')
        for proibido in ('subprocess', 'Popen', 'yt_dlp.YoutubeDL',
                         'ffmpeg', 'check_output', 'os.system'):
            self.assertNotIn(proibido, corpo,
                             'a rota criou caminho proprio de download (`%s`)'
                             % proibido)

    def test_9_o_legado_nao_se_moveu(self):
        """Ligar o audio nao pode mexer no que ja estava medido."""
        self.assertEqual(cap.estado('youtube.search'), cap.PROVEN)
        self.assertEqual(cap.estado('youtube.channel.discovery'), cap.PROVEN)
        self.assertEqual(cap.estado('youtube.video.metadata'), cap.PROVEN)
        self.assertEqual(cap.estado('youtube.comments'), cap.PROVEN)
        self.assertEqual(cap.estado('youtube.native_caption'), cap.PARTIAL)
        self.assertEqual(cap.estado('youtube.media'), cap.BLOCKED)
        for velha in ('youtube.search', 'youtube.channel.discovery',
                      'youtube.video.metadata', 'youtube.comments',
                      'youtube.native_caption'):
            d = reg.adaptador_de(PLAT, velha)
            self.assertIsNotNone(d['ROTA'],
                                 'a rota de `%s` desapareceu' % velha)


@unittest.skipUnless(_tem_ffprobe(), 'sem ffprobe: o que chegou nao se mede')
class OObjetoNaoMente(unittest.TestCase):
    """AUDIO_ONLY != VIDEO, e som nao e texto."""

    @classmethod
    def setUpClass(cls):
        cls._dir = tempfile.mkdtemp(prefix='c13-objeto-')
        cls._wav = _wav_silencioso(os.path.join(cls._dir, 'canario.wav'), 2.0)

    def _objeto(self):
        original = ytv._audio
        ytv._audio = _AudioEspiao(caminho=self._wav)
        try:
            objetos, _ = ex.COLLECT(platform=PLAT, capability=AUDIO,
                                    run_id='C13-WIRING-TESTE', video_id=CANARIO)
        finally:
            ytv._audio = original
        return objetos[0]

    def test_10_a_especie_e_AUDIO(self):
        o = self._objeto()
        self.assertEqual(o['MEDIA_KIND'], 'AUDIO')
        self.assertEqual(o['ACQUISITION_STATE'], ay.AUDIO_ADQUIRIDO)
        self.assertEqual(o['STREAMS']['VIDEO'], 0)
        self.assertGreaterEqual(o['STREAMS']['AUDIO'], 1)
        self.assertGreater(o['AUDIO_BYTES'], 0)
        self.assertEqual(len(o['AUDIO_SHA256']), 64)

    def test_11_o_objeto_nao_se_chama_VIDEO(self):
        o = self._objeto()
        for campo, valor in o.items():
            if campo == 'PARENT':
                continue
            if isinstance(valor, str):
                self.assertNotEqual(valor, 'VIDEO',
                                    'o objeto declara VIDEO para bytes de som '
                                    '(`%s`)' % campo)

    def test_12_nao_e_um_transcript_disfarcado(self):
        """Som != texto. Quem reconhece fala e outra capacidade, com outro dono."""
        o = self._objeto()
        for proibido in ('TRANSCRIPT', 'CAPTION', 'TEXT', 'LANGUAGE'):
            self.assertNotIn(proibido, o,
                             'o objeto de audio carrega `%s`, e isso e de outra '
                             'capacidade' % proibido)

    def test_13_a_linhagem_vai_ate_o_video_pai(self):
        o = self._objeto()
        self.assertEqual(o['PARENT']['VIDEO_ID'], CANARIO)
        self.assertEqual(o['VIDEO_ID'], CANARIO)
        self.assertEqual(o['SOURCE_URL'],
                         'https://www.youtube.com/watch?v=' + CANARIO)
        self.assertEqual(o['ROUTE'], ay.ROTA_AUDIO_PUBLICO)
        self.assertEqual(o['LIMITE'], 'PUBLIC_AUDIO_ONLY')

    def test_14_o_envelope_canonico_nao_foi_ampliado(self):
        """Nao se alarga o vocabulario do envelope para o verde ficar facil."""
        self.assertNotIn('AUDIO', env.CONTENT_TYPES,
                         'alargaram `CONTENT_TYPES` para encaixar o audio — o '
                         'vocabulario do envelope e de outra pergunta')

    def test_15_a_rota_nao_chama_ASR(self):
        """Aquisicao de som e reconhecimento de fala sao dois donos."""
        corpo = _corpo('youtube_audio_publico')
        for proibido in ('fala_local.transcrever', 'fl.transcrever', 'whisper',
                         'transcrever('):
            self.assertNotIn(proibido, corpo,
                             'a rota de aquisicao chama ASR (`%s`)' % proibido)


class AFalhaTemNome(unittest.TestCase):
    """«Nao consegui o som» nunca pode sair como «este video esta calado»."""

    def _despachar(self, caminho=None, motivo=None, **kw):
        original = ytv._audio
        ytv._audio = _AudioEspiao(caminho=caminho, motivo=motivo)
        try:
            return ex.COLLECT(platform=PLAT, capability=AUDIO,
                              run_id='C13-WIRING-TESTE', **kw)
        finally:
            ytv._audio = original

    def test_16_falha_de_aquisicao_nao_vira_ZERO_RESULTS(self):
        objetos, trace = self._despachar(
            motivo='ERROR: [youtube] %s: Video unavailable' % CANARIO,
            video_id=CANARIO)
        self.assertNotEqual(trace['RESULT'], 'ZERO_RESULTS',
                            'a falha do descarregador foi lida como «nao havia '
                            'nada para colher» — sao coisas diferentes')
        self.assertNotEqual(trace['RESULT'], 'OK')
        self.assertNotEqual(trace['ROUTER_RECORD']['ESTADO'], 'ZERO_RESULTS')
        self.assertEqual(trace['NATIVE_REASON'], ay.AUDIO_NAO_OBTIDO)
        self.assertEqual(trace['RESULT'], 'SOURCE_GONE')
        self.assertEqual(trace['ROUTER_RECORD']['ESTADO'], 'SOURCE_GONE')
        self.assertEqual(trace['ROUTER_RECORD']['OBJETOS'], 0)
        self.assertIn('unavailable', str(trace['ROUTER_RECORD']['ERRO']).lower(),
                      'o trace perdeu a frase que dizia QUAL foi a falha')
        # A taxonomia da casa leu o estado declarado pela rota, e nao o
        # reinterpretou: a fonte degradou-se, o executor esta sao.
        self.assertEqual(trace['ROUTER_RECORD']['SOURCE_HEALTH'], 'GONE')
        self.assertEqual(trace['ROUTER_RECORD']['EXECUTOR_HEALTH'], 'HEALTHY')

    def test_17_ferramenta_partida_nao_e_video_inexistente(self):
        objetos, trace = self._despachar(
            motivo='yt-dlp estourou o tempo (300s)', video_id=CANARIO)
        self.assertEqual(trace['RESULT'], 'EXECUTOR_UNAVAILABLE')
        self.assertEqual(trace['NATIVE_REASON'], ay.AUDIO_NAO_OBTIDO)
        self.assertEqual(trace['ROUTER_RECORD']['EXECUTOR_HEALTH'], 'BROKEN')

    def test_18_sem_video_id_a_rota_recusa_em_vez_de_inventar(self):
        objetos, trace = self._despachar(caminho='/dev/null')
        self.assertEqual(objetos, [])
        self.assertEqual(trace['NATIVE_REASON'], ay.VIDEO_ID_AUSENTE)
        self.assertEqual(trace['RESULT'], 'CONTRACT_DRIFT')

    def test_19_nao_se_fabrica_id_a_partir_de_endereco_estranho(self):
        """Identidade vem da fonte, ou nao vem."""
        self.assertIsNone(ay._video_id_de(video_url='https://example.org/x'))
        self.assertIsNone(ay._video_id_de(video_id='curto'))
        self.assertIsNone(ay._video_id_de(video_id='a' * 40))
        self.assertEqual(ay._video_id_de(video_url=(
            'https://www.youtube.com/watch?v=%s&t=10' % CANARIO)), CANARIO)
        self.assertEqual(ay._video_id_de(video_id=CANARIO), CANARIO)

    def test_20_um_ficheiro_com_imagem_nao_e_rebatizado_de_audio(self):
        """AUDIO_ONLY != VIDEO — e o portao esta nos bytes, nao no pedido."""
        original = fl.fluxos
        fl.fluxos = lambda c: (1, 1, None)   # trouxe imagem
        try:
            objetos, trace = self._despachar(caminho='/qualquer', video_id=CANARIO)
        finally:
            fl.fluxos = original
        self.assertEqual(objetos, [])
        self.assertEqual(trace['NATIVE_REASON'], ay.MEDIA_KIND_DIVERGE)
        self.assertNotEqual(trace['RESULT'], 'OK')


class AFronteiraPublica(unittest.TestCase):
    """A rota e PUBLICA, e isso tem de ser visivel no codigo."""

    def test_21_a_rota_nao_aceita_sessao(self):
        corpo = _corpo('youtube_audio_publico')
        assinatura = corpo[:corpo.index('):')]
        for proibido in ('cookie', 'cookies', 'sessao', 'session', 'token',
                         'credencial', 'oauth'):
            self.assertNotIn(proibido, assinatura.lower(),
                             'a rota publica aceita `%s` — o limite '
                             'PUBLIC_AUDIO_ONLY deixaria de ser verdade' % proibido)

    def test_22_a_matriz_continua_a_dizer_a_politica(self):
        """Os tres eixos nao se colapsam num so."""
        d = mz.decisao(PLAT, 'FETCH_AUDIO_BYTES')
        self.assertEqual(d['OWNER_AUTHORIZED'], 'SIM')
        self.assertEqual(d['PLATFORM_POLICY_STATUS'], 'DISALLOWED')
        self.assertEqual(d['LIMITE'], 'PUBLIC_AUDIO_ONLY')
        self.assertEqual(d['DECISAO'], 'ALLOWED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
