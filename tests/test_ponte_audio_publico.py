#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PONTE DO ÁUDIO PÚBLICO — os BYTES atravessam, não o envelope.

Nasceu do primeiro canário real do YouTube (`IT-T8-001`, run
`XX-T8-2026-09-19-202445-33e272ebab26f54f`), que adquiriu **bem** e preservou
**mal**:

    WAV real no disco .......... 7.112.072 bytes · 222,25 s · A=1 V=0
    RAW preservado ............. 1.232 bytes · media_type=application/json
    DERIVED .................... 0
    ADMISSION .................. NAO_SEI  (documento sem texto)

O som ficou no disco e o RAW guardou o **envelope que falava sobre ele**.

    A OBSERVAÇÃO DESCREVE O ITEM. QUANDO HÁ FICHEIRO,
    ELA NÃO É O ITEM — ELA APONTA PARA ELE.

Nenhuma prova aqui abre a rede. O canário é o WAV que já foi adquirido; se ele
não existir, as provas que precisam dele dizem-no em vez de baixar outro.

    NEW_MEDIA_ACQUISITION = NO · NETWORK_CALLS = 0
"""
import hashlib
import json
import os
import socket
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for gaveta in ('coleta', 'leis', 'ferramentas', 'guarda'):
    sys.path.insert(0, os.path.join(RAIZ, gaveta))
sys.path.insert(0, RAIZ)

import scrap_colheita as SC          # noqa: E402
import ingresso                      # noqa: E402

WAV = os.path.join(RAIZ, 'data', 'samples', 'YOUTUBE-TRANSCRICOES',
                   'audio-cache', '7Ps4g3juOIU.wav')
VIDEO = '7Ps4g3juOIU'
FONTE = 'IT-T8-001'


class _SemRede:
    def __enter__(self):
        self.chamadas = []
        self._orig = socket.socket.connect

        def espiao(_s, endereco, *a, **k):
            self.chamadas.append(endereco)
            raise AssertionError('A PROVA ABRIU A REDE: %r' % (endereco,))

        socket.socket.connect = espiao
        return self

    def __exit__(self, *e):
        socket.socket.connect = self._orig
        return False


def _wav_de_brincar(caminho, segundos=1):
    """Um WAV VÁLIDO construído pela `wave` do Python — nunca baixado."""
    import wave
    import struct
    with wave.open(caminho, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b''.join(struct.pack('<h', (i * 37) % 3000 - 1500)
                               for i in range(16000 * segundos)))
    return caminho


def _objeto(caminho, **muda):
    """O objeto tal como `youtube_audio_publico` passa a devolvê-lo."""
    corpo = open(caminho, 'rb').read()
    o = {
        'OBJECT_KIND': 'PUBLIC_AUDIO',
        'MEDIA_KIND': 'AUDIO',
        'VIDEO_ID': VIDEO,
        'SOURCE_URL': 'https://www.youtube.com/watch?v=%s' % VIDEO,
        'RUN_ID': 'PROVA-PONTE',
        'ROUTE': 'yt-dlp:public_audio',
        'EXECUTOR': 'adaptador_youtube.youtube_audio_publico',
        'CONTENT_TYPE': 'audio/wav',
        'AUDIO_REFERENCE': caminho,
        'AUDIO_BYTES': len(corpo),
        'AUDIO_SHA256': hashlib.sha256(corpo).hexdigest(),
        'STREAMS': {'AUDIO': 1, 'VIDEO': 0},
        'PARENT': {'KIND': 'VIDEO', 'VIDEO_ID': VIDEO},
    }
    o.update(muda)
    return o


def _atravessar(caminho, **muda):
    """PUBLIC_AUDIO → scrap_colheita.unidade → ingresso.ficha."""
    with _SemRede() as r:
        u = SC.unidade(_objeto(caminho, **muda), run_id='PROVA-PONTE',
                       fonte=FONTE)
        f = ingresso.ficha(u, corrida={'RUN_ID': 'PROVA-PONTE'})
    return u, f, r.chamadas


class OAdaptadorDeclaraAEspecie(unittest.TestCase):
    """Quem mediu os bytes é quem diz o que eles são."""

    def test_1_o_adaptador_declara_content_type(self):
        import inspect
        import adaptador_youtube as ay
        src = inspect.getsource(ay.youtube_audio_publico)
        self.assertIn("'CONTENT_TYPE': 'audio/wav'", src,
                      'a espécie tem de sair do dono da aquisição')

    def test_2_a_declaracao_vem_depois_da_medicao(self):
        """Declarar antes de `ffprobe` seria prometer o que não se mediu."""
        import inspect
        import adaptador_youtube as ay
        src = inspect.getsource(ay.youtube_audio_publico)
        self.assertLess(src.index('fl.fluxos'), src.index("'CONTENT_TYPE'"))

    def test_3_video_com_imagem_nao_chega_a_declarar_audio(self):
        import inspect
        import adaptador_youtube as ay
        src = inspect.getsource(ay.youtube_audio_publico)
        self.assertLess(src.index('if video_streams:'), src.index("'CONTENT_TYPE'"),
                        'o CONTRACT_DRIFT tem de levantar ANTES da declaração')


class AFronteiraTraduzSemDecidir(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp(prefix='ponte-audio-')
        self.wav = _wav_de_brincar(os.path.join(self.tmp, 'canario.wav'))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_4_audio_reference_vira_storage_location(self):
        u, _f, rede = _atravessar(self.wav)
        self.assertTrue(u.get('STORAGE_LOCATION'))
        self.assertEqual([], rede)

    def test_5_o_content_type_do_coletor_e_transportado(self):
        u, _f, _ = _atravessar(self.wav)
        self.assertEqual('audio/wav', u.get('CONTENT_TYPE'))

    def test_6_o_payload_diz_PRESENTE_e_onde(self):
        u, _f, _ = _atravessar(self.wav)
        self.assertEqual('PRESENTE', u['PAYLOAD']['ESTADO'])
        self.assertTrue(u['PAYLOAD']['ONDE'])

    def test_7_a_fronteira_nao_inventa_especie(self):
        """Sem `CONTENT_TYPE` do coletor não se adivinha pela extensão."""
        u, f, _ = _atravessar(self.wav, CONTENT_TYPE=None)
        self.assertIsNone(u.get('STORAGE_LOCATION'),
                          'sem espécie declarada, a ponte NÃO atravessa')
        self.assertEqual('application/json', f.CONTENT_TYPE)

    def test_8_ficheiro_inexistente_nao_vira_raw_de_audio(self):
        u, f, _ = _atravessar(self.wav,
                              AUDIO_REFERENCE=os.path.join(self.tmp, 'nao-existe.wav'))
        self.assertIsNone(u.get('STORAGE_LOCATION'))
        self.assertEqual('application/json', f.CONTENT_TYPE)

    def test_9_sem_referencia_continua_o_caminho_antigo(self):
        u, _f, _ = _atravessar(self.wav, AUDIO_REFERENCE=None)
        self.assertEqual('NAO_SE_APLICA', u['PAYLOAD']['ESTADO'])

    def test_10_uma_observacao_de_texto_nao_muda_de_comportamento(self):
        """Post/legenda continuam a ser o próprio item. Nada regride."""
        with _SemRede():
            u = SC.unidade({'OBJECT_KIND': 'POST', 'TEXT': 'ciao'},
                           run_id='X', fonte=FONTE)
        self.assertEqual('NAO_SE_APLICA', u['PAYLOAD']['ESTADO'])
        self.assertIsNone(u.get('STORAGE_LOCATION'))


class OsBytesSaoOsBytes(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp(prefix='ponte-bytes-')
        self.wav = _wav_de_brincar(os.path.join(self.tmp, 'canario.wav'))
        self.corpo = open(self.wav, 'rb').read()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_11_o_raw_tem_o_media_type_do_audio(self):
        _u, f, _ = _atravessar(self.wav)
        self.assertEqual('audio/wav', f.CONTENT_TYPE)

    def test_12_o_raw_tem_os_bytes_do_wav(self):
        _u, f, _ = _atravessar(self.wav)
        self.assertEqual(len(self.corpo), f.BYTES)

    def test_13_o_sha_do_raw_e_o_sha_do_wav(self):
        _u, f, _ = _atravessar(self.wav)
        self.assertEqual(hashlib.sha256(self.corpo).hexdigest(), f.SHA256)

    def test_14_o_sha_do_raw_NAO_e_o_sha_do_json(self):
        """A prova negativa: se fosse o envelope, este sha bateria."""
        u, f, _ = _atravessar(self.wav)
        sha_json = hashlib.sha256(
            json.dumps(u, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        self.assertNotEqual(sha_json, f.SHA256)

    def test_15_audio_com_bytes_json_e_IMPOSSIVEL(self):
        """`RAW_MEDIA_TYPE_AUDIO_WITH_JSON_BYTES = IMPOSSIBLE`.

        A espécie e os bytes vêm do MESMO ficheiro: `raw_do_disco` lê o
        caminho para calcular o sha. Não há caminho de código que rotule
        `audio/*` sobre bytes de envelope — e é isso que este teste fixa.
        """
        _u, f, _ = _atravessar(self.wav)
        corpo_lido = open(os.path.join(RAIZ, f.STORAGE_LOCATION), 'rb').read() \
            if os.path.isfile(os.path.join(RAIZ, f.STORAGE_LOCATION)) \
            else open(self.wav, 'rb').read()
        self.assertTrue(f.CONTENT_TYPE.startswith('audio/'))
        self.assertEqual(hashlib.sha256(corpo_lido).hexdigest(), f.SHA256)
        self.assertFalse(corpo_lido.lstrip()[:1] in (b'{', b'['),
                         'bytes de JSON sob rótulo de áudio')

    def test_16_o_storage_location_e_endereco_e_nao_identidade(self):
        _u, f, _ = _atravessar(self.wav)
        self.assertNotIn(f.SHA256, str(f.STORAGE_LOCATION),
                         'o sha identifica os bytes; o caminho é onde eles estão')


class AProcedenciaSobrevive(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp(prefix='ponte-proc-')
        self.wav = _wav_de_brincar(os.path.join(self.tmp, 'canario.wav'))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_17_o_source_id_do_pedido_continua(self):
        u, _f, _ = _atravessar(self.wav)
        self.assertEqual(FONTE, u['SOURCE_ID'])

    def test_18_o_video_id_sobrevive_na_observacao(self):
        u, _f, _ = _atravessar(self.wav)
        self.assertEqual(VIDEO, u['OBSERVACAO']['VIDEO_ID'])

    def test_19_o_parent_continua_a_dizer_VIDEO(self):
        u, _f, _ = _atravessar(self.wav)
        self.assertEqual('VIDEO', u['OBSERVACAO']['PARENT']['KIND'])

    def test_20_o_document_id_continua_NAO_SEI(self):
        u, _f, _ = _atravessar(self.wav)
        self.assertEqual('NAO SEI', u['DOCUMENT_ID'],
                         'DOCUMENT_ID_WIRING_GAP continua aberto, e declarado')

    def test_21_o_source_id_nao_virou_o_video_id(self):
        u, _f, _ = _atravessar(self.wav)
        self.assertNotEqual(u['SOURCE_ID'], u['OBSERVACAO']['VIDEO_ID'])


class ODerivadorCerto(unittest.TestCase):

    def test_22_audio_escolhe_transcricao_de_midia(self):
        caps = ingresso._capacidades_de_derivacao()
        quem = [c.get('EXECUTOR_ID') for c in caps
                if ingresso._cabe_na_capacidade(c, 'audio/wav')]
        self.assertEqual(['transcricao-de-midia'], quem)

    def test_23_o_executor_de_pdf_NAO_e_escolhido(self):
        caps = ingresso._capacidades_de_derivacao()
        quem = [c.get('EXECUTOR_ID') for c in caps
                if ingresso._cabe_na_capacidade(c, 'audio/wav')]
        self.assertNotIn('texto-de-pdf', quem)

    def test_24_json_continua_sem_derivador(self):
        """A prova de que o defeito era este: JSON não tem quem o derive."""
        caps = ingresso._capacidades_de_derivacao()
        quem = [c.get('EXECUTOR_ID') for c in caps
                if ingresso._cabe_na_capacidade(c, 'application/json')]
        self.assertEqual([], quem)


class OCanarioReal(unittest.TestCase):
    """Com o WAV que já foi adquirido. Sem baixar nada."""

    def setUp(self):
        if not os.path.isfile(WAV):
            self.skipTest('REAL_AUDIO_REPROCESS = NOT_RUN — o WAV já não está '
                          'no disco, e esta prova NÃO o vai buscar')

    def test_25_o_wav_real_atravessa_com_os_seus_bytes(self):
        corpo = open(WAV, 'rb').read()
        _u, f, rede = _atravessar(WAV)
        self.assertEqual('audio/wav', f.CONTENT_TYPE)
        self.assertEqual(len(corpo), f.BYTES)
        self.assertEqual(hashlib.sha256(corpo).hexdigest(), f.SHA256)
        self.assertEqual([], rede, 'NETWORK_CALLS tem de ser 0')

    def test_26_os_bytes_batem_com_o_que_a_corrida_real_mediu(self):
        corpo = open(WAV, 'rb').read()
        self.assertEqual(7112072, len(corpo))
        self.assertEqual(
            '7785c5059749335040a059bf55812d5bc2c7ddd929eb1672a886f557aeff2bda',
            hashlib.sha256(corpo).hexdigest())


if __name__ == '__main__':
    unittest.main(verbosity=2)
