#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.4C · FASE 13 — A JANELA CONTINUA DE PÉ, E PROVA-SE SEM TOCAR NO INSTAGRAM.

A C10.4C aposentou `ferramentas/instagram_transcrever.py`. A pergunta que a
missão obriga a responder antes de fechar é outra:

    INSTAGRAM_WINDOW_DISTINCT_CAPABILITY = YES | NO | UNKNOWN

`coleta/instagram_janela.py` faz DESCOBERTA e METADADOS: lê o lote congelado,
abre perfil e post pela rota pública, e normaliza o que leu. Não importa o
reconhecedor, não corre `ffmpeg`, não instancia `WhisperModel`. Descoberta não é
transcrição — e essa é diferença de CONCEITO, não de pasta.

    CORPUS DIFERENTE NÃO É CONCEITO DIFERENTE.
    Mas produzir o corpus também não é consumi-lo.

O QUE ESTE FICHEIRO PROVA, E COMO
-----------------------------------
Prova a metade PERMITIDA e OFFLINE: obediência ao lote, e o miolo de leitura —
parsing de número arredondado, resgate da legenda pela etiqueta `og:`, slug de
ficheiro. Nada aqui abre socket.

    INSTAGRAM_REQUESTS = 0 · APIFY_RUNS = 0 · COST_USD = 0

A metade que sai para a rede (`perfis`, `objetos`) não é corrida aqui — corrê-la
seria tocar a plataforma, que esta missão proíbe. Ela é medida pela ARMADILHA:
o teste substitui o navegador por um que grita se alguém o subir.

    UMA PROVA QUE PRECISA DE SAIR PARA PROVAR QUE NÃO SAI NÃO É UMA PROVA.
"""
import ast
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'ferramentas', 'leis', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import instagram_janela as jn   # noqa: E402

JANELA_REL = 'coleta/instagram_janela.py'


def _fonte(rel):
    return io.open(os.path.join(RAIZ, rel), encoding='utf-8').read()


class AJanelaEUmaCapacidadeDistinta(unittest.TestCase):

    def test_a_janela_nao_e_um_transcritor(self):
        arv = ast.parse(_fonte(JANELA_REL))
        imp = []
        for n in ast.walk(arv):
            if isinstance(n, ast.Import):
                imp += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                imp.append(n.module or '')
        for proibido in ('fala_local', 'instagram_transcrever', 'reel_transcricao',
                         'faster_whisper'):
            self.assertNotIn(proibido, imp)
        argv = {n.value for n in ast.walk(arv) if isinstance(n, ast.Constant)
                and isinstance(n.value, str)}
        for proibido in ('ffmpeg', '-vn', 'bestaudio', 'yt-dlp'):
            self.assertNotIn(proibido, argv,
                             'a janela passou a montar comando de media: %r' % proibido)
        # e a sonda ve o que existe: ela TEM de encontrar os imports da janela
        self.assertIn('json', imp)

    def test_o_que_a_janela_oferece_nao_e_o_que_a_rota_velha_oferecia(self):
        publicas = [n.name for n in ast.walk(ast.parse(_fonte(JANELA_REL)))
                    if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')]
        for esperada in ('contas', 'perfis', 'objetos', 'saida_de_rede'):
            self.assertIn(esperada, publicas)
        self.assertNotIn('transcrever', publicas)
        self.assertNotIn('fase_rodar', publicas)


class AMetadePermitidaCorreOffline(unittest.TestCase):
    """Os quatro pedaços que se provam sem socket nenhum."""

    def test_ela_obedece_ao_lote_congelado(self):
        contas = jn.contas()
        self.assertTrue(contas, 'o lote congelado deixou de dar contas de Instagram')
        for c in contas:
            self.assertEqual(c['PLATFORM'], 'INSTAGRAM',
                             'a janela devolveu conta de outra plataforma')
            self.assertTrue(c.get('ACCOUNT_HANDLE'),
                            'conta sem identificador: %r' % c.get('COMPANY'))
            # O lote mistura `www.instagram.com` e `instagram.com` — as duas
            # formas sao reais e a sentinela nao inventa uma normalizacao que a
            # casa nao fez.
            self.assertTrue(c.get('ACCOUNT_URL', '').startswith(
                ('https://www.instagram.com/', 'https://instagram.com/')),
                'conta sem URL de Instagram: %r' % c.get('ACCOUNT_URL'))

    def test_o_numero_arredondado_diz_que_e_arredondado(self):
        # Este é o miolo que impede "18,7 mil" de virar uma variação inventada.
        v, como = jn._numero('18,7 mil')
        self.assertEqual(v, 18700)
        self.assertIn('ARREDONDADO', como)
        v, como = jn._numero('2.751')
        self.assertEqual(v, 2751)
        v, como = jn._numero('')
        self.assertEqual(v, jn.NAO_SEI)
        v, como = jn._numero('nada disto')
        self.assertEqual(v, jn.NAO_SEI)
        self.assertIn('formato', como)

    def test_o_resgate_pela_etiqueta_declara_de_onde_veio(self):
        inteira = jn._resgatar_do_og({
            'OG_DESCRIPTION': '205 likes, 12 comments - bayer_italia on June 12, '
                              '2025: "Oggi e un giorno importante"',
            'LIKE_COUNT_EMBED': jn.NAO_SEI, 'LIKE_COUNT_OG': '205',
            'COMMENT_COUNT_EMBED': jn.NAO_SEI, 'COMMENT_COUNT_OG': '12'})
        self.assertEqual(inteira['CAPTION'], 'Oggi e un giorno importante')
        self.assertIn('og:description', inteira['CAPTION_SOURCE'])
        self.assertEqual(inteira['CAPTION_IS_COMPLETE'], 'NOT_KNOWN')
        self.assertEqual(inteira['LIKE_COUNT_RESOLVED'], 205)
        self.assertEqual(inteira['LIKE_COUNT_RESOLVED_ROUTE'], 'OG_DESCRIPTION')

        cortada = jn._resgatar_do_og({
            'OG_DESCRIPTION': '9 likes, 1 comments - x on May 1, 2025: "Comeca aqui..."'})
        self.assertEqual(cortada['CAPTION_IS_COMPLETE'], 'NO')
        self.assertIn('TRUNCADA', cortada['CAPTION_SOURCE'])

        vazia = jn._resgatar_do_og({})
        self.assertEqual(vazia['CAPTION'], jn.NAO_SEI)

    def test_o_nome_de_ficheiro_nao_deixa_passar_caminho(self):
        self.assertEqual(jn._slug('basf_agroes'), 'basf_agroes')
        self.assertNotIn('/', jn._slug('../../etc/passwd'))
        self.assertLessEqual(len(jn._slug('x' * 200)), 60)


class ENenhumaDestasProvasSaiu(unittest.TestCase):
    """A armadilha: se alguma coisa aqui subisse navegador, isto gritava."""

    def test_nada_nesta_prova_abre_navegador(self):
        import cdp
        subiu = []

        def armadilha(*a, **k):
            subiu.append((a, k))
            raise AssertionError('esta prova subiu navegador — proibido na C10.4C')

        guardados = {}
        for nome in ('abrir', 'subir'):
            if hasattr(cdp, nome):
                guardados[nome] = getattr(cdp, nome)
                setattr(cdp, nome, armadilha)
        try:
            jn.contas()
            jn._numero('18,7 mil')
            jn._resgatar_do_og({'OG_DESCRIPTION': '1 likes, 0 comments - a on May 1, '
                                                  '2025: "b"'})
            jn._slug('c')
        finally:
            for nome, fn in guardados.items():
                setattr(cdp, nome, fn)
        self.assertEqual(subiu, [])
        # e a armadilha nao e decorativa: ela dispara quando alguem a chama
        self.assertTrue(guardados, 'nao houve o que armadilhar; a prova mediria nada')


if __name__ == '__main__':
    unittest.main(verbosity=2)
