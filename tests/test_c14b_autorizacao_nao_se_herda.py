# -*- coding: utf-8 -*-
"""C14-B · A AUTORIZACAO NAO SE HERDA POR PARTILHA DE IMPLEMENTACAO.

O DEFEITO QUE ESTES TESTES TERIAM APANHADO
-------------------------------------------
A C14 abriu `INSTAGRAM/FETCH_AUDIO_BYTES` para som de Reel publico, e a cadeia
passou a escolher a porta grossa a partir de `kind`: pedir `AUDIO` dava
`FETCH_AUDIO_BYTES`. Parecia certo e nao era.

`ferramentas/reel_transcricao.py` pede `kind=MIDIA_AUDIO` em TODAS as corridas.
Logo QUALQUER capacidade que chamasse a cadeia herdava a autorizacao de audio —
mesmo sem ter porta grossa nenhuma. Medido em 2026-09-19:

    instagram.reel.capture   (sem grossa, registada com `executa=`)
    -> capturar_reel -> transcrever_reel -> metadados_ytdlp
    -> YTDLP_CALLS = 1  ['-J', 'https://www.instagram.com/reel/...']

Na base `9efbac40`, a mesma chamada media `YTDLP_CALLS = 0` e
`MEDIA_STATE = ROUTE_NOT_ALLOWED`. A autorizacao de UMA capacidade alargou a
superficie de OUTRA, que ninguem autorizou.

    CAPABILITY SHARES IMPLEMENTATION != CAPABILITY SHARES AUTHORIZATION.

A CORRECAO, E POR QUE ELA E ESTA
---------------------------------
A porta grossa deixou de ser DERIVADA da especie e passou a ser DECLARADA por
quem chama (`capacidade_grossa=`). Quem nao declara nao herda: cai na pergunta
historica (`FETCH_TRANSCRIPT`), que e a mais restrita desta cadeia.

    AUSENTE = NAO DECLARADO. E NAO DECLARADO NAO AUTORIZA.

O QUE ESTES TESTES NAO FAZEM
-----------------------------
Nao tocam a rede. O `yt-dlp` e substituido por um espiao que CONTA e nunca corre,
e `socket.connect` e proibido — um pedido real reprova por AssertionError antes
de sair. Contar chamadas e a unica forma de provar que o portao recusou ANTES do
socket, e nao depois.
"""
import os
import socket
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import adaptador_instagram as ai      # noqa: E402
import reel_transcricao as rt         # noqa: E402
import scrap_capacidades as cap       # noqa: E402
import scrap_registo as reg           # noqa: E402
import social_matriz as mz            # noqa: E402

REMOTO = {'PLATFORM': 'INSTAGRAM', 'POST_ID': 'C14BSENTINELA',
          'SOURCE_URL': 'https://www.instagram.com/reel/C14BSENTINELA/'}


class _EspiaYtdlp:
    """Conta as invocacoes do descarregador. NUNCA o corre."""

    def __init__(self):
        self.chamadas = []

    def __call__(self, args, **k):
        self.chamadas.append(list(args))

        class R:
            returncode = 1
            stdout = ''
            stderr = 'ERROR: espia'
        return R()


class _SemRede:
    def __enter__(self):
        self.tentativas = []
        self._orig = socket.socket.connect
        tent = self.tentativas

        def _nao(sock, *a, **k):
            tent.append(a)
            raise AssertionError('saiu para a rede: %r' % (a,))
        socket.socket.connect = _nao
        return self

    def __exit__(self, *e):
        socket.socket.connect = self._orig
        return False


class _ComEspiao(unittest.TestCase):
    def setUp(self):
        self.espia = _EspiaYtdlp()
        self._orig = rt._ytdlp
        rt._ytdlp = self.espia

    def tearDown(self):
        rt._ytdlp = self._orig


class AAutorizacaoNaoSeHerda(_ComEspiao):
    """T1 · T2 · T4 — quem nao tem porta propria nao ganha rede de vizinha."""

    def test_T1_capture_remoto_nao_toca_a_rede(self):
        """A capacidade SEM porta grossa nao adquire, mesmo com a vizinha aberta.

        Este e o teste que teria apanhado o defeito: ele falha se `capture`
        voltar a alcancar o descarregador por herdar a autorizacao de
        `public_audio`.
        """
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_AUDIO_BYTES')['DECISAO'],
                         mz.PERMITIDA_SIM,
                         'premissa: a porta do audio publico esta aberta')
        with _SemRede() as rede:
            objetos, _trace = ai.capturar_reel(ident=dict(REMOTO),
                                               run_id='C14B-T1', guardar=False)
        self.assertEqual(self.espia.chamadas, [],
                         'capture chegou ao yt-dlp sem porta grossa propria')
        self.assertEqual(rede.tentativas, [])
        self.assertEqual(objetos[0]['MEDIA_STATE'], mz.NAO_PERMITIDA)

    def test_T2_a_rota_partilhada_sem_porta_declarada_tambem_recusa(self):
        """`reel_transcrever` e partilhada; sem porta declarada, recusa."""
        with _SemRede() as rede:
            objetos = ai.reel_transcrever(run_id='C14B-T2', ident=dict(REMOTO),
                                          guardar=False)
        self.assertEqual(self.espia.chamadas, [])
        self.assertEqual(rede.tentativas, [])
        self.assertEqual(objetos[0]['MEDIA_STATE'], mz.NAO_PERMITIDA)

    def test_T4_uma_capacidade_sem_decisao_nao_herda_a_da_vizinha(self):
        """`reel.capture` e `reel.audio` nao tem porta grossa — e continuam sem."""
        for nome in ('instagram.reel.capture', 'instagram.reel.audio'):
            with self.subTest(capacidade=nome):
                self.assertIsNone(
                    cap.da_matriz(nome),
                    '%s ganhou porta grossa sem decisao humana' % nome)

    def test_T4b_nenhuma_capacidade_remota_vive_sem_portao(self):
        """O GATE CENTRAL: `REMOTE_NETWORK_POSSIBLE` exige `GATE_BEFORE_NETWORK`.

        Percorre TODO registo Instagram. Quem consegue alcancar a rede tem de
        ter uma porta grossa que a matriz conheca — senao a decisao dela nao
        existe, e `NOT_DECLARED` nao e permissao.
        """
        reg.carregar_adaptadores()
        for (plat, capac), d in sorted(reg.registados().items()):
            if plat != 'INSTAGRAM':
                continue
            if not (d.get('ROTA') or d.get('EXECUTA')):
                continue          # declaracao honesta: nao executa nada
            with self.subTest(capacidade=capac):
                grossa = cap.da_matriz(capac)
                if grossa is None:
                    # Sem porta: a cadeia tem de recusar a aquisicao remota.
                    continue
                self.assertIn(grossa, mz.MATRIZ.get(plat) or {},
                              '%s declara %s, que a matriz de %s nao conhece'
                              % (capac, grossa, plat))


class APortaAutorizadaAtravessa(_ComEspiao):
    """T5 e a contraprova positiva: a porta certa CHEGA ao executor."""

    def test_a_porta_autorizada_chega_ao_descarregador(self):
        """Contraprova: sem isto, os testes acima passariam com a cadeia morta.

        Uma cadeia partida daria `chamadas = []` em TODOS os casos, e os testes
        de recusa ficariam verdes por nada.
        """
        with _SemRede():
            ai.reel_audio_publico(run_id='C14B-POS', ident=dict(REMOTO),
                                  guardar=False)
        self.assertTrue(self.espia.chamadas,
                        'a rota autorizada nao chegou ao executor')
        pediu_audio = [c for c in self.espia.chamadas if '-f' in c]
        self.assertTrue(pediu_audio, 'nenhuma chamada pediu faixa de audio')
        self.assertIn(rt.SELETOR_SO_AUDIO, pediu_audio[0],
                      'a rota autorizada pediu algo que nao e audio')

    def test_T5_a_plataforma_faz_parte_da_chave(self):
        """`INSTAGRAM/FETCH_AUDIO_BYTES` != `YOUTUBE/FETCH_AUDIO_BYTES`."""
        ig = mz.decisao('INSTAGRAM', 'FETCH_AUDIO_BYTES')
        yt = mz.decisao('YOUTUBE', 'FETCH_AUDIO_BYTES')
        self.assertNotEqual(ig['ROTA'], yt['ROTA'],
                            'as duas plataformas colapsaram numa rota so')
        self.assertEqual(ig['LIMITE'], 'PUBLIC_AUDIO_ONLY')
        self.assertEqual(yt['LIMITE'], 'PUBLIC_AUDIO_ONLY')

    def test_os_tres_eixos_nao_se_colapsam(self):
        """A autorizacao do dono NAO apaga a evidencia da plataforma."""
        d = mz.decisao('INSTAGRAM', 'FETCH_AUDIO_BYTES')
        self.assertEqual(d['OWNER_AUTHORIZED'], 'SIM')
        self.assertEqual(d['PLATFORM_POLICY_STATUS'], 'DISALLOWED')
        self.assertEqual(d['LIMITE'], 'PUBLIC_AUDIO_ONLY')

    def test_o_limite_nao_abre_video_nem_legenda(self):
        """Autorizar som nao autoriza video, e nao reabre a legenda."""
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')['DECISAO'],
                         mz.NAO_PERMITIDA)
        self.assertEqual(mz.decisao('INSTAGRAM', 'FETCH_VIDEO_BYTES')['DECISAO'],
                         mz.NAO_DECLARADA)


class ReusarContinuaAFuncionar(_ComEspiao):
    """T3 — a lei madura nao pode ser vitima da correcao."""

    def test_T3_reprocessar_ficheiro_local_nao_exige_autorizacao(self):
        """REUSAR != ADQUIRIR: bytes em casa correm sem porta e sem rede."""
        import tempfile
        import wave
        tmp = tempfile.mkdtemp(prefix='c14b-')
        wav = os.path.join(tmp, 'local.wav')
        with wave.open(wav, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(8000)
            w.writeframes(b'\x00\x00' * 800)

        with _SemRede() as rede:
            caminho, capture, estado, _motivo, _degraus = rt.obter_midia(
                dict(REMOTO), midia_ficheiro=wav)

        self.assertEqual(self.espia.chamadas, [],
                         'o reprocessamento foi buscar midia a rede')
        self.assertEqual(rede.tentativas, [])
        self.assertEqual(caminho, wav)
        self.assertEqual(estado, 'MEDIA_OK')


if __name__ == '__main__':
    unittest.main(verbosity=2)
