#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10 — A ROTA DE TRANSCRICAO NAO PODE VOLTAR A BAIXAR VIDEO.

A C8 escreveu a lei e a C9 mediu que ninguem a cumpria. A C10 implementou-a. O
que falta e a parte que sobrevive a esta missao:

    TRANSCRIPTION_ROUTE_MUST_NOT_DOWNLOAD_VIDEO

Estes testes existem para REPROVAR o retorno ao comportamento antigo. Se alguem
tirar o seletor de audio, ligar uma queda para video, ou deixar um endereco de
video entrar em silencio pela porta do `midia_url`, a suite cai aqui.

POR QUE O ARGV, E NAO O TEXTO DO FICHEIRO
------------------------------------------
Esta casa ja foi mordida por sentinelas ancoradas em texto:

    UMA SENTINELA ANCORADA NO TEXTO MEDE O TEXTO, NAO A LEI.

Um `grep` por `bestaudio` passaria com a palavra dentro de um comentario a
explicar que ela foi removida. Por isso o que se mede aqui e o COMANDO que a
cadeia monta, interceptado na fronteira com o processo — e, onde ha bytes, o
que o `ffprobe` ve dentro deles.
"""
import ast
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
sys.path.insert(0, RAIZ)

import fala_local as fl          # noqa: E402
import reel_transcricao as rt    # noqa: E402


def _ffmpeg():
    return shutil.which('ffmpeg')


def _fazer(caminho, *args):
    subprocess.run([_ffmpeg(), '-v', 'error', '-y'] + list(args) + [caminho],
                   check=True, capture_output=True, timeout=120)
    return caminho


class _Espia:
    """Um `yt-dlp` que regista o pedido e nunca sai da maquina."""

    def __init__(self, returncode=1, stderr='ERROR: Requested format is not available'):
        self.chamadas = []
        self._rc, self._err = returncode, stderr

    def __call__(self, args, timeout=300):
        self.chamadas.append(list(args))

        class _R:
            returncode, stdout, stderr = self._rc, '', self._err
        return _R


class _PoliticaPermissiva:
    """Injecta `PERMITIDA=SIM` em memoria; o ficheiro continua a dizer NAO.

    A C10.5D fechou a decisao humana — a aquisicao remota do Instagram esta
    recusada — e o portao passou a viver no ponto onde o socket abre. Estes
    testes medem O SELETOR e A ESPECIE DOS BYTES, que sao capacidade tecnica e
    nao politica.

        UM TESTE QUE DEIXA DE CORRER PORQUE A POLITICA MUDOU MEDE A POLITICA,
        QUE JA TEM DONO.

    Por isso a lei e injectada aqui, em memoria, e o disco fica como esta.
    """

    def __enter__(self):
        import social_matriz as mz
        self._mz = mz
        self._orig = mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT']
        mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT'] = [
            dict(r, PERMITIDA='SIM', ESTADO='PROVED') for r in self._orig]
        return self

    def __exit__(self, *_):
        self._mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT'] = self._orig
        return False


class OSeletorDeAudioEObrigatorio(unittest.TestCase):
    """O pedido de fala tem de pedir audio. Sem isto, a lei nao existe."""

    def setUp(self):
        self.espia = _Espia()
        self._orig = rt._ytdlp
        rt._ytdlp = self.espia
        self.tmp = tempfile.mkdtemp(prefix='c10-')

    def tearDown(self):
        rt._ytdlp = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _argv(self, kind):
        self.espia.chamadas.clear()
        # A PLATAFORMA E PARTE DA PERGUNTA DESDE A C10.5. O portao de politica
        # passou a viver no ponto onde o socket abre, e ele responde por
        # plataforma: sem a declarar, a resposta certa e NOT_DECLARED e nenhum
        # comando chega a ser montado. Estes testes medem o SELETOR, e para o
        # medir tem de dizer de que plataforma falam.
        with _PoliticaPermissiva():
            rt.midia_por_ytdlp('https://www.instagram.com/reel/XXXX',
                               os.path.join(self.tmp, 'x.m4a'), tentativas=1, kind=kind,
                               plataforma='INSTAGRAM')
        return self.espia.chamadas[0]

    def test_pedir_fala_poe_o_seletor_de_audio_no_comando(self):
        argv = self._argv(rt.MIDIA_AUDIO)
        self.assertIn('-f', argv,
                      'a cadeia de transcricao chamou o yt-dlp SEM seletor de '
                      'formato. O padrao dele e o melhor video MAIS o melhor '
                      'audio — que e exatamente a rota que a C10 fechou.')
        self.assertEqual(argv[argv.index('-f') + 1], rt.SELETOR_SO_AUDIO)

    def test_sem_pedido_de_fala_o_seletor_nao_entra(self):
        # Se o seletor entrasse SEMPRE, o teste de cima passaria mesmo com a
        # lei desligada, e nao mediria nada. Este e o contraponto que o torna
        # informativo.
        self.assertNotIn('-f', self._argv(rt.MIDIA_VIDEO))

    def test_o_seletor_pede_audio_sem_imagem(self):
        # `bestaudio`, na lingua do yt-dlp, e «o melhor formato SEM video».
        self.assertEqual(rt.SELETOR_SO_AUDIO, 'bestaudio')


class NaoHaQuedaParaVideo(unittest.TestCase):
    """Falha de rota nao e autorizacao para pedir mais."""

    def setUp(self):
        self.espia = _Espia()
        self._orig = rt._ytdlp
        rt._ytdlp = self.espia
        self.tmp = tempfile.mkdtemp(prefix='c10-')

    def tearDown(self):
        rt._ytdlp = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_sem_formato_de_audio_o_estado_diz_isso_e_nao_baixa_video(self):
        with _PoliticaPermissiva():
            p, motivo = rt.midia_por_ytdlp('https://x/reel/Y',
                                           os.path.join(self.tmp, 'y.m4a'),
                                           tentativas=1, kind=rt.MIDIA_AUDIO,
                                           plataforma='INSTAGRAM')
        self.assertIsNone(p)
        self.assertTrue(motivo.startswith('AUDIO_ONLY_UNAVAILABLE'), motivo)
        for argv in self.espia.chamadas:
            self.assertNotIn('bestvideo', ' '.join(argv))
            self.assertEqual(argv[argv.index('-f') + 1], rt.SELETOR_SO_AUDIO,
                             'houve uma tentativa com outro formato depois de o '
                             'audio falhar. Isso e a queda silenciosa para video.')

    def test_o_estado_de_falta_de_audio_esta_no_vocabulario(self):
        self.assertIn(rt.MEDIA_SEM_AUDIO_SO, rt.ESTADOS_DE_MIDIA)
        self.assertIn(rt.MEDIA_KIND_DIVERGE, rt.ESTADOS_DE_MIDIA)


class OsBytesSaoConferidos(unittest.TestCase):
    """A bandeira diz o que foi PEDIDO. So o ffprobe diz o que CHEGOU."""

    @classmethod
    def setUpClass(cls):
        if not _ffmpeg():
            raise unittest.SkipTest('sem ffmpeg nesta maquina')
        cls.tmp = tempfile.mkdtemp(prefix='c10-bytes-')
        cls.audio = _fazer(os.path.join(cls.tmp, 'so_audio.m4a'),
                           '-f', 'lavfi', '-i', 'sine=frequency=440:duration=2',
                           '-c:a', 'aac')
        cls.video = _fazer(os.path.join(cls.tmp, 'com_imagem.mp4'),
                           '-f', 'lavfi', '-i', 'testsrc=size=64x64:duration=2',
                           '-f', 'lavfi', '-i', 'sine=frequency=440:duration=2',
                           '-c:v', 'libx264', '-c:a', 'aac', '-shortest')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_ficheiro_so_com_som_passa(self):
        self.assertEqual(fl.fluxos(self.audio)[0], 0)
        self.assertGreaterEqual(fl.fluxos(self.audio)[1], 1)
        limpo, porque = fl.so_audio(self.audio)
        self.assertTrue(limpo, porque)

    def test_ficheiro_com_imagem_e_recusado_mesmo_com_som(self):
        limpo, porque = fl.so_audio(self.video)
        self.assertFalse(limpo)
        self.assertIn('imagem', porque)

    def test_extensao_de_audio_nao_convence_ninguem(self):
        # O ataque: renomear um MP4 para .m4a. A extensao passa a mentir e os
        # bytes continuam a dizer a verdade.
        disfarcado = os.path.join(self.tmp, 'disfarce.m4a')
        shutil.copy(self.video, disfarcado)
        limpo, _p = fl.so_audio(disfarcado)
        self.assertFalse(limpo, 'um MP4 renomeado para .m4a passou por audio')

    def test_ficheiro_ilegivel_nao_passa_por_audio_limpo(self):
        # NAO CONSEGUI VER != NAO TEM IMAGEM. Um `False` mudo colapsaria as duas.
        mau = os.path.join(self.tmp, 'lixo.m4a')
        with io.open(mau, 'wb') as fh:
            fh.write(b'isto nao e media nenhuma')
        v, a, porque = fl.fluxos(mau)
        self.assertEqual(v, fl.NAO_SEI)
        self.assertTrue(porque)
        self.assertFalse(fl.so_audio(mau)[0])


class OProvedorNaoDecideSozinho(unittest.TestCase):
    """Se a rota devolver video quando se pediu audio, os bytes sao RECUSADOS.

    Este e o buraco que um teste so de `argv` deixaria aberto: o comando pede
    audio, o fornecedor entrega imagem na mesma — por mudanca de versao, por
    formato mal anunciado, por um `-f` que deixou de significar o que
    significava — e a cadeia aceitaria porque a bandeira estava la.

        PEDIR AUDIO != TER RECEBIDO SO AUDIO.
    """

    def setUp(self):
        if not _ffmpeg():
            raise unittest.SkipTest('sem ffmpeg nesta maquina')
        self.tmp = tempfile.mkdtemp(prefix='c10-devolve-')
        self._orig = rt._ytdlp
        alvo_video = os.path.join(self.tmp, 'ZZZ.mp4')

        def _entrega_video(args, timeout=300):
            # O fornecedor "obedece" ao comando e escreve imagem na mesma.
            _fazer(alvo_video,
                   '-f', 'lavfi', '-i', 'testsrc=size=64x64:duration=2',
                   '-f', 'lavfi', '-i', 'sine=frequency=440:duration=2',
                   '-c:v', 'libx264', '-c:a', 'aac', '-shortest')

            class _R:
                returncode, stdout, stderr = 0, '', ''
            return _R
        rt._ytdlp = _entrega_video

    def tearDown(self):
        rt._ytdlp = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_bytes_com_imagem_sao_recusados_mesmo_com_o_seletor_certo(self):
        with _PoliticaPermissiva():
            caminho, motivo = rt.midia_por_ytdlp(
                'https://x/reel/ZZZ', os.path.join(self.tmp, 'ZZZ.m4a'),
                tentativas=1, kind=rt.MIDIA_AUDIO, plataforma='INSTAGRAM')
        self.assertIsNone(caminho,
                          'a cadeia aceitou um ficheiro com imagem numa rota '
                          'que jurou pedir so audio')
        self.assertTrue(motivo.startswith('MEDIA_KIND_MISMATCH'), motivo)


class AEscadaObedeceAoPedido(unittest.TestCase):
    """Todo degrau respeita `kind`, e nenhum baixa video em silencio."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='c10-escada-')
        self._midia = rt.MIDIA
        rt.MIDIA = self.tmp
        self._baixar = rt.baixar
        self.baixados = []
        rt.baixar = lambda u, d: (self.baixados.append(u), (0, 'PROVA'))[1]

    def tearDown(self):
        rt.MIDIA = self._midia
        rt.baixar = self._baixar
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_endereco_sem_especie_declarada_nao_e_baixado(self):
        ident = {'POST_ID': 'ABC', 'PLATFORM': 'INSTAGRAM'}
        _c, _p, _e, _m, degraus = rt.obter_midia(
            ident, midia_url='https://cdn/video.mp4', kind=rt.MIDIA_AUDIO)
        self.assertEqual(self.baixados, [],
                         'baixou um endereco sem saber se era audio ou video')
        primeiro = degraus[0]
        self.assertEqual(primeiro['RESULT'], rt.MEDIA_KIND_DIVERGE)

    def test_endereco_declarado_audio_pode_ser_tentado(self):
        ident = {'POST_ID': 'ABC', 'PLATFORM': 'INSTAGRAM'}
        rt.obter_midia(ident, midia_url='https://cdn/faixa.m4a',
                       kind=rt.MIDIA_AUDIO, midia_url_kind=rt.MIDIA_AUDIO)
        self.assertEqual(self.baixados, ['https://cdn/faixa.m4a'])

    def test_o_embed_e_saltado_quando_o_pedido_e_fala(self):
        ident = {'POST_ID': 'ABC', 'PLATFORM': 'INSTAGRAM'}
        # A ESCADA E CAPACIDADE, NAO LEI. Com a politica em NAO (que e o estado
        # decidido na C10.5D) a escada nem chega aos degraus de rede — e isso e
        # o portao a funcionar, nao a escada a mudar.
        with _PoliticaPermissiva():
            _c, _p, estado, _m, degraus = rt.obter_midia(ident, kind=rt.MIDIA_AUDIO)
        embed = [d for d in degraus if d['PROVIDER'] == rt.CAPTURA_EMBED]
        self.assertTrue(embed, 'o degrau do embed desapareceu do registo')
        self.assertEqual(embed[0]['RESULT'], rt.MEDIA_SEM_AUDIO_SO)
        self.assertEqual(estado, rt.MEDIA_SEM_AUDIO_SO)
        self.assertEqual(self.baixados, [])


class ReusarNaoEAdquirir(unittest.TestCase):
    """Extrair audio de um MP4 antigo e o estado VELHO com nome novo."""

    def setUp(self):
        if not _ffmpeg():
            raise unittest.SkipTest('sem ffmpeg nesta maquina')
        self.tmp = tempfile.mkdtemp(prefix='c10-reuso-')
        self._midia = rt.MIDIA
        rt.MIDIA = self.tmp
        _fazer(os.path.join(self.tmp, 'ABC.mp4'),
               '-f', 'lavfi', '-i', 'testsrc=size=64x64:duration=2',
               '-f', 'lavfi', '-i', 'sine=frequency=440:duration=2',
               '-c:v', 'libx264', '-c:a', 'aac', '-shortest')

    def tearDown(self):
        rt.MIDIA = self._midia
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_o_mp4_historico_reusado_nao_e_chamado_de_audio_only(self):
        ident = {'POST_ID': 'ABC', 'PLATFORM': 'INSTAGRAM'}
        caminho, prov, _e, _m, degraus = rt.obter_midia(ident, kind=rt.MIDIA_AUDIO)
        self.assertTrue(caminho.endswith('.mp4'))
        self.assertEqual(prov, rt.CAPTURA_JA_PRESERVADA)
        self.assertEqual(degraus[0]['MEDIA_KIND'], rt.MIDIA_VIDEO,
                         'um MP4 reusado foi rotulado como audio')


class UmDonoSo(unittest.TestCase):
    """A C10 nao pode ter feito nascer um segundo motor de fala."""

    def test_asr_owners_e_um(self):
        alvos = ('WhisperModel', 'BatchedInferencePipeline')
        donos = set()
        for raiz, pastas, ficheiros in os.walk(RAIZ):
            pastas[:] = [d for d in pastas
                         if d not in ('.git', '__pycache__', 'node_modules')]
            for f in ficheiros:
                if not f.endswith('.py'):
                    continue
                caminho = os.path.join(raiz, f)
                try:
                    with io.open(caminho, encoding='utf-8', errors='replace') as fh:
                        arvore = ast.parse(fh.read())
                except Exception:                              # noqa: BLE001
                    continue
                for no in ast.walk(arvore):
                    if isinstance(no, ast.Call):
                        nome = getattr(no.func, 'id', None) or getattr(no.func, 'attr', None)
                        if nome in alvos:
                            donos.add(os.path.relpath(caminho, RAIZ))
        self.assertEqual(donos, {os.path.join('ferramentas', 'fala_local.py')}, donos)

    def test_a_cadeia_nao_ganhou_um_segundo_descarregador(self):
        # `midia_por_ytdlp` continua a ser o unico sitio que chama o yt-dlp para
        # trazer bytes. Um segundo seria um segundo sitio onde esquecer o seletor.
        with io.open(os.path.join(RAIZ, 'ferramentas', 'reel_transcricao.py'),
                     encoding='utf-8') as fh:
            fonte = fh.read()
        arvore = ast.parse(fonte)
        com_o = []
        for no in ast.walk(arvore):
            if not isinstance(no, ast.Call):
                continue
            nome = getattr(no.func, 'id', None)
            if nome != '_ytdlp':
                continue
            pai = [a for a in ast.walk(arvore)
                   if isinstance(a, ast.FunctionDef) and no in ast.walk(a)]
            for f in pai:
                if any(isinstance(x, ast.Constant) and x.value == '-o'
                       for x in ast.walk(no)):
                    com_o.append(f.name)
        self.assertEqual(sorted(set(com_o)), ['midia_por_ytdlp'], sorted(set(com_o)))


class NadaDeApify(unittest.TestCase):
    def test_a_rota_de_audio_nao_conhece_rota_paga(self):
        espia = _Espia()
        orig = rt._ytdlp
        rt._ytdlp = espia
        tmp = tempfile.mkdtemp(prefix='c10-rota-paga-')
        try:
            with _PoliticaPermissiva():
                rt.midia_por_ytdlp('https://x/reel/Y', os.path.join(tmp, 'y.m4a'),
                                   tentativas=1, kind=rt.MIDIA_AUDIO,
                                   plataforma='INSTAGRAM')
        finally:
            rt._ytdlp = orig
            shutil.rmtree(tmp, ignore_errors=True)
        junto = ' '.join(' '.join(c) for c in espia.chamadas).lower()
        self.assertNotIn('apify', junto)


if __name__ == '__main__':
    unittest.main(verbosity=2)
