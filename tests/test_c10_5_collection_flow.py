#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.5 — O PORTAO VIVE ONDE O SOCKET ABRE, E A COLLECTION NAO TEM PORTA DE SERVICO.

A C10.4 pos o portao de politica no adaptador do Instagram. Isso cobre quem
entra pelo executor canonico. A C10.5 perguntou quem MAIS entra, e mediu:

    coleta/comunicacao_coleta.py::fase_transcrever
      -> reel_transcricao.fase_posts
        -> transcrever_reel                       ← sem adaptador, sem portao

E a fase de fala da Collection. Nao e um atalho de teste nem uma prova: e a
porta por onde a casa transcreve em producao.

    UM PORTAO QUE UMA PORTA DE PRODUCAO CONTORNA NAO DECIDE NADA.

ONDE O PORTAO PASSOU A VIVER, E PORQUE NAO E NO LOTE
------------------------------------------------------
No ponto exacto onde o socket abre: `midia_por_ytdlp`. Nao na fase, nao no lote,
nao no adaptador apenas.

Isso tem uma consequencia que E A LEI, e nao um efeito lateral: reprocessar
bytes que ja estao em casa continua a correr mesmo com a politica em NAO.

    REUSAR != ADQUIRIR. Uma recusa de AQUISICAO que tambem apagasse o
    REPROCESSAMENTO estaria a castigar o que ja esta preservado — e a obrigar
    quem mudasse uma regra a recolher tudo outra vez.

A PLATAFORMA E PARTE DA PERGUNTA
----------------------------------
A politica responde por plataforma, e a plataforma vem de `ident['PLATFORM']` —
dado medido, nunca adivinhado do endereco. Sem plataforma declarada a resposta e
NOT_DECLARED, e nao declarado nao e permitido.
"""
import ast
import io
import json
import os
import shutil
import socket
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('ferramentas', 'leis', 'coleta', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import social_matriz as mz          # noqa: E402
import scrap_capacidades as cap     # noqa: E402
import scrap_http as http           # noqa: E402
import reel_transcricao as rt       # noqa: E402

GROSSA = 'FETCH_TRANSCRIPT'


def _fonte(caminho):
    return io.open(os.path.join(RAIZ, caminho), encoding='utf-8').read()


class _SemRede:
    def __enter__(self):
        self.tentativas = []
        self._orig = socket.socket.connect
        tent = self.tentativas

        def _nao(sock, *a, **k):
            tent.append(a)
            raise AssertionError('a cadeia saiu para a rede: %r' % (a,))
        socket.socket.connect = _nao
        return self

    def __exit__(self, *_):
        socket.socket.connect = self._orig
        return False


class _PoliticaNegativa:
    """Poe a decisao em NAO sem escrever politica no disco."""

    def __enter__(self):
        self._orig = mz.MATRIZ['INSTAGRAM'][GROSSA]
        mz.MATRIZ['INSTAGRAM'][GROSSA] = [
            dict(r, PERMITIDA='NAO', ESTADO='ROUTE_NOT_ALLOWED') for r in self._orig]
        return self

    def __exit__(self, *_):
        mz.MATRIZ['INSTAGRAM'][GROSSA] = self._orig
        return False


class _EspiaYtdlp:
    def __init__(self):
        self.chamadas = []

    def __call__(self, args, timeout=300):
        self.chamadas.append(list(args))

        class _R:
            returncode, stdout, stderr = 1, '', 'ERROR: espia'
        return _R


class OPortaoVivePercisamenteOndeOSocketAbre(unittest.TestCase):

    def setUp(self):
        self.espia = _EspiaYtdlp()
        self._orig = rt._ytdlp
        rt._ytdlp = self.espia
        self.tmp = tempfile.mkdtemp(prefix='c10-5-')

    def tearDown(self):
        rt._ytdlp = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_politica_negativa_impede_o_comando_de_sequer_ser_montado(self):
        with _PoliticaNegativa(), _SemRede() as rede:
            caminho, motivo = rt.midia_por_ytdlp(
                'https://www.instagram.com/reel/X', os.path.join(self.tmp, 'x.m4a'),
                tentativas=1, kind=rt.MIDIA_AUDIO, plataforma='INSTAGRAM')
        self.assertIsNone(caminho)
        self.assertTrue(motivo.startswith(mz.NAO_PERMITIDA), motivo)
        self.assertEqual(self.espia.chamadas, [], 'o yt-dlp correu apos um NAO')
        self.assertEqual(rede.tentativas, [])

    def test_plataforma_por_declarar_nao_e_permissao(self):
        with _SemRede():
            caminho, motivo = rt.midia_por_ytdlp(
                'https://x/reel/Y', os.path.join(self.tmp, 'y.m4a'),
                tentativas=1, kind=rt.MIDIA_AUDIO)
        self.assertIsNone(caminho)
        self.assertTrue(motivo.startswith(mz.NAO_DECLARADA), motivo)
        self.assertEqual(self.espia.chamadas, [])

    def test_as_tres_palavras_chegam_inteiras_ao_motivo(self):
        # NOT_DECLARED != ROUTE_NOT_ALLOWED. Colapsa-las faria «ninguem mediu»
        # e «nao pode» sairem com a mesma palavra no artefato.
        with _SemRede():
            _c, sem_plat = rt.midia_por_ytdlp(
                'https://x/reel/Y', os.path.join(self.tmp, 'a.m4a'),
                tentativas=1, plataforma='NOT_KNOWN')
        with _PoliticaNegativa(), _SemRede():
            _c, negada = rt.midia_por_ytdlp(
                'https://x/reel/Y', os.path.join(self.tmp, 'b.m4a'),
                tentativas=1, plataforma='INSTAGRAM')
        self.assertTrue(sem_plat.startswith(mz.NAO_DECLARADA), sem_plat)
        self.assertTrue(negada.startswith(mz.NAO_PERMITIDA), negada)
        self.assertNotEqual(sem_plat.split(':')[0], negada.split(':')[0])

    def test_a_politica_permitida_deixa_o_seletor_de_audio_passar(self):
        # O contraponto. Sem ele o teste de cima passaria com o portao sempre
        # fechado, e um portao que recusa tudo nao mede politica nenhuma.
        with _SemRede():
            rt.midia_por_ytdlp('https://www.instagram.com/reel/X',
                               os.path.join(self.tmp, 'z.m4a'),
                               tentativas=1, kind=rt.MIDIA_AUDIO,
                               plataforma='INSTAGRAM')
        self.assertTrue(self.espia.chamadas, 'a politica diz SIM e nada foi pedido')
        argv = self.espia.chamadas[0]
        self.assertEqual(argv[argv.index('-f') + 1], rt.SELETOR_SO_AUDIO)


class ReusarNaoEAdquirir(unittest.TestCase):
    """Uma recusa de aquisicao nao pode apagar o reprocessamento."""

    def setUp(self):
        self.espia = _EspiaYtdlp()
        self._orig = rt._ytdlp
        rt._ytdlp = self.espia
        self.tmp = tempfile.mkdtemp(prefix='c10-5-reuso-')
        self.ficheiro = os.path.join(self.tmp, 'ja-em-casa.m4a')
        io.open(self.ficheiro, 'wb').write(b'\x00' * 32)

    def tearDown(self):
        rt._ytdlp = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_bytes_entregues_atravessam_mesmo_com_a_politica_em_nao(self):
        ident = {'PLATFORM': 'INSTAGRAM', 'POST_ID': 'JAEMCASA',
                 'SOURCE_URL': 'https://www.instagram.com/reel/JAEMCASA/'}
        with _PoliticaNegativa(), _SemRede() as rede:
            caminho, capture, estado, _porque, _degraus = rt.obter_midia(
                ident, midia_ficheiro=self.ficheiro)
        self.assertIsNotNone(caminho, 'o reprocessamento foi punido pela recusa '
                                      'de uma aquisicao que ninguem pediu')
        self.assertEqual(capture, rt.CAPTURA_FORNECIDA)
        self.assertEqual(estado, rt.MEDIA_OK)
        self.assertEqual(self.espia.chamadas, [])
        self.assertEqual(rede.tentativas, [])


class ARecusaSobeComONomeDela(unittest.TestCase):
    """ERROR != REJECTED != UNKNOWN != NOT_RUN != ROUTE_NOT_ALLOWED != NOT_DECLARED."""

    def setUp(self):
        self.espia = _EspiaYtdlp()
        self._orig = rt._ytdlp
        rt._ytdlp = self.espia
        self.ident = {'PLATFORM': 'INSTAGRAM', 'POST_ID': 'C105ESTADO',
                      'SOURCE_URL': 'https://www.instagram.com/reel/C105ESTADO/'}

    def tearDown(self):
        rt._ytdlp = self._orig

    def test_a_recusa_nao_se_disfarca_de_audio_indisponivel(self):
        # «AUDIO_ONLY_UNAVAILABLE» sob uma recusa seria uma mentira precisa: o
        # som esta la — o que falta e autorizacao. Quem lesse o artefato daqui a
        # um ano concluiria que a plataforma nao serve audio.
        with _PoliticaNegativa(), _SemRede():
            _c, _prov, estado, porque, degraus = rt.obter_midia(self.ident)
        self.assertEqual(estado, mz.NAO_PERMITIDA)
        self.assertNotEqual(estado, rt.MEDIA_SEM_AUDIO_SO)
        self.assertIn('FETCH_TRANSCRIPT', porque)
        self.assertTrue(degraus and degraus[-1]['RESULT'] == mz.NAO_PERMITIDA)
        self.assertEqual(self.espia.chamadas, [])

    def test_plataforma_por_declarar_sobe_com_a_outra_palavra(self):
        with _SemRede():
            _c, _prov, estado, _porque, _d = rt.obter_midia(
                dict(self.ident, PLATFORM='NOT_KNOWN'))
        self.assertEqual(estado, mz.NAO_DECLARADA)
        self.assertNotEqual(estado, mz.NAO_PERMITIDA)
        self.assertEqual(self.espia.chamadas, [])

    def test_nem_os_metadados_saem_depois_de_um_nao(self):
        # Pedir metadados e tocar a plataforma: abre socket, gasta pedido e
        # aparece no log do host.
        with _PoliticaNegativa(), _SemRede():
            meta, porque = rt.metadados_ytdlp(self.ident['SOURCE_URL'],
                                              plataforma='INSTAGRAM')
        self.assertIsNone(meta)
        self.assertTrue(porque.startswith(mz.NAO_PERMITIDA), porque)
        self.assertEqual(self.espia.chamadas, [])


class ACollectionNaoTemPortaDeServico(unittest.TestCase):

    def _chamadas_a_aquisicao(self):
        """Quem chama a cadeia de aquisicao, fora de teste e de prova."""
        AQ = {'transcrever_reel', 'fase_posts', 'obter_midia', 'midia_por_ytdlp'}
        achados = []
        for raiz, dirs, fich in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('node_modules', '.git', '__pycache__', 'BASELINE', 'data')]
            for f in fich:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), RAIZ).replace(os.sep, '/')
                if rel.startswith(('tests/', 'provas/')):
                    continue
                if rel in ('ferramentas/reel_transcricao.py',):
                    continue
                try:
                    arv = ast.parse(io.open(os.path.join(raiz, f),
                                            encoding='utf-8').read(), rel)
                except Exception:
                    continue
                for n in ast.walk(arv):
                    if isinstance(n, ast.Call):
                        nome = getattr(n.func, 'attr', None) or getattr(n.func, 'id', None)
                        if nome in AQ:
                            achados.append((rel, n.lineno, nome))
        return achados

    def test_a_sonda_encontra_as_portas_que_a_casa_tem(self):
        # Uma sonda que encontra zero e diz «limpo» mede a sonda. O adaptador
        # chama a cadeia — se isto vier vazio, a busca partiu-se.
        achados = self._chamadas_a_aquisicao()
        self.assertTrue(any(rel == 'coleta/adaptador_instagram.py'
                            for rel, _l, _n in achados),
                        'a sonda deixou de ver o proprio adaptador')

    def test_toda_porta_de_producao_passa_pelo_portao(self):
        # Nao se exige que cada chamador pergunte: exige-se que NINGUEM chegue
        # ao socket sem a pergunta. Por isso o portao esta em `midia_por_ytdlp`,
        # e por isso este teste mede o ponto de saida e nao os chamadores.
        arv = ast.parse(_fonte('ferramentas/reel_transcricao.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'midia_por_ytdlp')
        pergunta = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Call)
                    and (getattr(n.func, 'attr', None)
                         or getattr(n.func, 'id', None)) == 'politica_da_aquisicao']
        saida = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Call)
                 and (getattr(n.func, 'attr', None)
                      or getattr(n.func, 'id', None)) == '_ytdlp']
        self.assertTrue(pergunta, 'o portao saiu de `midia_por_ytdlp`')
        self.assertTrue(saida, 'a saida para a rede mudou de sitio; o portao ficou para tras')
        self.assertLess(min(pergunta), min(saida),
                        'a pergunta corre depois da saida para a rede')

    def test_o_nome_da_capacidade_tem_um_dono_so(self):
        import adaptador_instagram as ai
        self.assertEqual(ai.CAPACIDADE_NA_MATRIZ,
                         cap.da_matriz('instagram.reel.transcribe'))
        self.assertEqual(rt.CAPACIDADE_NA_MATRIZ, GROSSA)
        self.assertEqual(ai.CAPACIDADE_NA_MATRIZ, rt.CAPACIDADE_NA_MATRIZ)


class OPortaoDeTransporteTemUmDonoSo(unittest.TestCase):
    """`scrap_http` le o robots vivo. A C10.5 mediu que a cadeia nao lhe pergunta."""

    def test_so_um_ficheiro_le_o_robots(self):
        leitores = []
        for raiz, dirs, fich in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('node_modules', '.git', '__pycache__', 'BASELINE', 'data')]
            for f in fich:
                if not f.endswith('.py'):
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), RAIZ).replace(os.sep, '/')
                if rel.startswith('tests/'):
                    continue
                if 'RobotFileParser' in io.open(os.path.join(raiz, f),
                                                encoding='utf-8').read():
                    leitores.append(rel)
        self.assertEqual(leitores, ['coleta/scrap_http.py'],
                         'nasceu um segundo leitor de robots.txt')

    def test_o_portao_de_transporte_continua_chamavel_por_quem_precisar(self):
        # Ele existe, e nao importa o roteador para existir. Quando a decisao
        # humana sobre a aquisicao do Instagram for tomada, e aqui que ela se
        # liga — uma linha, num sitio, com dono.
        self.assertTrue(callable(http.permitido))
        self.assertTrue(http.AGENTE.startswith('SintoniaScrap/'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
