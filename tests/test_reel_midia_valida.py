#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A LEI DA MÍDIA, PRESA EM TESTE — no consumidor real, e por CONTAGEM DE CHAMADAS.

    python -m pytest tests/test_reel_midia_valida.py -q

O QUE ESTE FICHEIRO PRENDE
--------------------------
Medido em 2026-09-18, e era defeito: a cadeia escrevia

    kind_usado = MIDIA_AUDIO if e_so_audio else MIDIA_VIDEO

e TUDO o que nao fosse som virava VIDEO — e o estado final era decidido por
EXISTIR UM ARTEFATO, nao por a midia ter sido lida. Com um ficheiro de ZERO
BYTES, um HTML disfarcado de `.mp4` e um binario corrompido, os tres saiam:

    MEDIA_STATE = MEDIA_OK  ·  MEDIA_KIND_USED = VIDEO  ·  e o ASR era CHAMADO

    BYTES PRESENTES != MIDIA VALIDA.      MIDIA ILEGIVEL NAO VIRA VIDEO.

POR QUE «CALL COUNT» E NAO «ESTADO DIFERENTE DE OK»
----------------------------------------------------
«O reconhecedor recusou lixo» NAO E «o lixo nunca devia ter sido enviado».
Um teste que so olhasse `TRANSCRIPT_STATE` passaria com as duas coisas, e nao
distingue-las e apagar a unica pergunta que interessa:

    O LIXO CHEGOU A SER ENVIADO AO RECONHECEDOR?

Este ficheiro conta as chamadas. Zero e a resposta certa para lixo. Um e a
resposta certa para som.

FIXTURE
-------
WAV verdadeiro, escrito com a stdlib `wave` — sem rede, sem download, sem
binario grande no Git. Um ficheiro que comeca por `RIFF` nao e midia: e um
prefixo. A diferenca so aparece quando alguem o abre, e e isso que se testa.
"""
import os
import sys
import tempfile
import unittest
import wave

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('ferramentas', 'leis', 'coleta'):
    sys.path.insert(0, os.path.join(RAIZ, _p))

import fala_local as fl                      # noqa: E402
import reel_transcricao as rt                # noqa: E402

URL = 'https://www.instagram.com/reel/DW6X5lZkU41/'


class MidiaValidaEEspecie(unittest.TestCase):
    """O consumidor final: `transcrever_reel`, com contagem de chamadas do ASR."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='midia-valida-')
        self._transcrever = fl.transcrever
        self.chamadas = []

        def contador(*a, **k):
            self.chamadas.append(a)
            return {'TRANSCRIPT_STATE': 'OK', 'TRANSCRIPT': 'texto de teste',
                    'TRANSCRIPT_CHARS': 16}
        fl.transcrever = contador
        self.ident = rt.identidade_do_url(URL)

    def tearDown(self):
        fl.transcrever = self._transcrever
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ── fixtures ────────────────────────────────────────────────────────────
    def _ficheiro(self, nome, conteudo):
        caminho = os.path.join(self.tmp, nome)
        modo = 'wb' if isinstance(conteudo, bytes) else 'w'
        with open(caminho, modo) as f:
            f.write(conteudo)
        return caminho

    def _wav(self, nome='media.wav'):
        caminho = os.path.join(self.tmp, nome)
        with wave.open(caminho, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(b'\x00\x00' * 3200)
        return caminho

    def _correr(self, caminho, run_id):
        self.chamadas = []
        return rt.transcrever_reel(self.ident, run_id=run_id,
                                   midia_ficheiro=caminho, guardar=False)

    # ── A · zero bytes ──────────────────────────────────────────────────────
    def test_zero_bytes_nao_e_midia_ok_nem_video_e_nao_chama_asr(self):
        r = self._correr(self._ficheiro('zero.m4a', b''), 'T-ZERO')
        self.assertEqual(r.get('MEDIA_STATE'), 'MEDIA_DOWNLOAD_FAILED')
        self.assertEqual(r.get('MEDIA_KIND_USED'), 'NOT_KNOWN')
        self.assertEqual(len(self.chamadas), 0, 'o ASR foi chamado para zero bytes')

    # ── B · HTML disfarcado de midia ────────────────────────────────────────
    def test_html_com_extensao_de_video_nao_e_midia_ok_nem_video_e_nao_chama_asr(self):
        r = self._correr(self._ficheiro('pagina.mp4',
                                        '<html><body>isto nao e midia</body></html>'),
                         'T-HTML')
        self.assertEqual(r.get('MEDIA_STATE'), 'MEDIA_DOWNLOAD_FAILED')
        self.assertEqual(r.get('MEDIA_KIND_USED'), 'NOT_KNOWN')
        self.assertEqual(len(self.chamadas), 0, 'o ASR foi chamado para um HTML')

    # ── C · binario corrompido ──────────────────────────────────────────────
    def test_bytes_aleatorios_nao_sao_midia_ok_nem_video_e_nao_chamam_asr(self):
        r = self._correr(self._ficheiro('lixo.mp4', os.urandom(4096)), 'T-CORRUPT')
        self.assertEqual(r.get('MEDIA_STATE'), 'MEDIA_DOWNLOAD_FAILED')
        self.assertEqual(r.get('MEDIA_KIND_USED'), 'NOT_KNOWN')
        self.assertEqual(len(self.chamadas), 0, 'o ASR foi chamado para bytes aleatorios')

    # ── D · ficheiro inexistente ────────────────────────────────────────────
    def test_ficheiro_inexistente_nao_e_midia_ok_e_nao_chama_asr(self):
        r = self._correr(os.path.join(self.tmp, 'nao-existe.m4a'), 'T-MISSING')
        self.assertEqual(r.get('MEDIA_STATE'), 'MEDIA_DOWNLOAD_FAILED')
        self.assertEqual(r.get('MEDIA_KIND_USED'), 'NOT_KNOWN')
        self.assertEqual(len(self.chamadas), 0, 'o ASR foi chamado para um ficheiro ausente')

    # ── E · som verdadeiro continua a passar ────────────────────────────────
    def test_wav_valido_e_midia_ok_e_audio_e_chama_asr_uma_vez(self):
        r = self._correr(self._wav(), 'T-VALIDO')
        self.assertEqual(r.get('MEDIA_STATE'), 'MEDIA_OK')
        self.assertEqual(r.get('MEDIA_KIND_USED'), 'AUDIO')
        self.assertEqual(len(self.chamadas), 1, 'o ASR nao foi chamado para som valido')

    # ── F · a especie nao se colapsa em dois estados ────────────────────────
    def test_a_especie_ilegivel_nao_e_o_balde_do_video(self):
        """O defeito antigo, pregado como lei: `False` de `so_audio` NAO e VIDEO."""
        for nome, conteudo in (('z.m4a', b''),
                               ('p.mp4', '<html></html>'),
                               ('c.mp4', os.urandom(1024))):
            with self.subTest(caso=nome):
                r = self._correr(self._ficheiro(nome, conteudo), 'T-ESPECIE-' + nome)
                self.assertNotEqual(r.get('MEDIA_KIND_USED'), 'VIDEO')


if __name__ == '__main__':
    unittest.main(verbosity=2)
