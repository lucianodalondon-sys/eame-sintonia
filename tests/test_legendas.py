# -*- coding: utf-8 -*-
"""Recusa de player nao pode virar ausencia de legenda.

Em 2026-09-04 a camada gratuita de legendas mediu, no controle positivo
`jNQXAC9IVRw`, uma pagina de 1,2 MB que passava em `_bloqueado()` e trazia
`ytInitialPlayerResponse` — mas com

    playabilityStatus.status = LOGIN_REQUIRED
    reason = "Accedi per confermare di non essere un bot"

Quando o player volta negado, o YouTube nao manda o bloco `captions`. O codigo
lia `faixas == []` e gravava AUSENTE com WHISPER_CANDIDATO=True — num video que
tem duas faixas ('de', 'en'). Ausencia falsa, e conta de transcricao paga por
causa de uma reputacao de IP.

    RECUSA DE PLAYER != AUSENCIA DE LEGENDA.

Estes testes existem para impedir que esse ramo desapareca de novo. Eles nao
tocam a rede: montam as tres formas do player a mao.
"""
import json, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))


def _pagina(pr):
    """Uma pagina que passa em `_bloqueado()` e carrega este playerResponse."""
    return ('x' * 7000 + 'ytInitialData = {"a":1};'
            + 'var ytInitialPlayerResponse = ' + json.dumps(pr) + ';')


NEGADO = {'playabilityStatus': {'status': 'LOGIN_REQUIRED',
                                'reason': 'Accedi per confermare di non essere un bot'},
          'videoDetails': {}, 'microformat': {}}
OK_SEM_FAIXA = {'playabilityStatus': {'status': 'OK'},
                'videoDetails': {'title': 'video real sem legenda',
                                 'lengthSeconds': '61', 'viewCount': '10',
                                 'channelId': 'UC0'},
                'microformat': {'playerMicroformatRenderer':
                                {'publishDate': '2026-01-01'}}}
OK_COM_FAIXA = {'playabilityStatus': {'status': 'OK'},
                'videoDetails': {'title': 'video com legenda', 'lengthSeconds': '61',
                                 'viewCount': '10', 'channelId': 'UC0'},
                'microformat': {'playerMicroformatRenderer':
                                {'publishDate': '2026-01-01'}},
                'captions': {'playerCaptionsTracklistRenderer': {'captionTracks': [
                    {'languageCode': 'it', 'kind': 'asr',
                     'baseUrl': 'https://exemplo.invalid/t',
                     'name': {'simpleText': 'Italiano (gerada)'}}]}}}

CASOS = {'v-negado': NEGADO, 'v-ok-sem': OK_SEM_FAIXA, 'v-ok-com': OK_COM_FAIXA}


class TestPlayerNegado(unittest.TestCase):
    """Roda `fase_legendas` com a rede substituida por paginas montadas aqui."""

    def setUp(self):
        import youtube_janela as yj
        self.yj = yj
        self._guardados = (yj._ler, yj._abrir, yj._gravar, yj._timedtext)
        self.gravado = {}
        yj._ler = lambda nome: {'ITEMS': [
            {'VIDEO_ID': k, 'VIDEO_URL': 'https://exemplo.invalid/%s' % k,
             'ACCOUNT_HANDLE': '@t', 'TITLE': k} for k in CASOS]}
        yj._abrir = lambda url, **kw: (_pagina(CASOS[url.rsplit('/', 1)[1]]),
                                       'FALSA', 'OK')
        yj._gravar = lambda nome, corpo: (self.gravado.update(corpo), 'memoria')[1]
        yj._timedtext = lambda base_url: [{'T_MS': 0, 'DUR_MS': 900, 'TEXTO': 'ciao'}]
        yj.fase_legendas()
        self.itens = {i['VIDEO_ID']: i for i in self.gravado['ITEMS']}

    def tearDown(self):
        (self.yj._ler, self.yj._abrir, self.yj._gravar,
         self.yj._timedtext) = self._guardados

    def test_player_negado_nao_vira_ausente(self):
        i = self.itens['v-negado']
        self.assertEqual(i['CAPTION_STATE'], 'PLAYER_NEGADO')
        self.assertEqual(i['PLAYABILITY_STATUS'], 'LOGIN_REQUIRED')

    def test_player_negado_nunca_pede_transcricao_paga(self):
        self.assertIs(self.itens['v-negado']['WHISPER_CANDIDATO'], False)

    def test_o_motivo_carrega_a_frase_do_youtube(self):
        self.assertIn('LOGIN_REQUIRED', self.itens['v-negado']['POR_QUE'])
        self.assertIn('non essere un bot', self.itens['v-negado']['POR_QUE'])

    def test_ausente_continua_significando_ausente(self):
        """Player OK e faixa nenhuma: isso sim e ausencia, e ai o whisper cabe."""
        i = self.itens['v-ok-sem']
        self.assertEqual(i['CAPTION_STATE'], 'AUSENTE')
        self.assertIs(i['WHISPER_CANDIDATO'], True)

    def test_faixa_declarada_ainda_e_lida(self):
        i = self.itens['v-ok-com']
        self.assertEqual(i['CAPTION_STATE'], 'PRESENTE')

    def test_o_vocabulario_gravado_declara_os_cinco_estados(self):
        texto = self.gravado.get('CINCO_ESTADOS_DIFERENTES', '')
        for estado in ('PRESENTE', 'AUSENTE', 'DECLARADA_MAS_VAZIA',
                       'PLAYER_NEGADO', 'PORTA_NAO_ABRIU'):
            self.assertIn(estado, texto, '%s nao esta no vocabulario' % estado)


class TestPortaQueNaoAbre(unittest.TestCase):
    """`cdp.subir` tem de dizer o que o navegador disse, e nao esperar 25 s por um morto."""

    def test_a_mensagem_de_fracasso_nao_afirma_que_o_chrome_subiu(self):
        import cdp
        with open(cdp.__file__, encoding='utf-8') as f:
            fonte = f.read()
        self.assertIn('p.poll()', fonte,
                      'sem poll(), o laco espera o tempo inteiro por um processo morto')
        self.assertNotIn('o Chrome subiu mas a porta %d nao passou a escutar', fonte)
        self.assertIn('o Chrome NÃO subiu', fonte)

    def test_stderr_do_navegador_nao_vai_para_o_lixo(self):
        import cdp
        with open(cdp.__file__, encoding='utf-8') as f:
            fonte = f.read()
        i = fonte.index('def subir(')
        corpo = fonte[i:fonte.index('def _aba_de_pagina(', i)]
        self.assertNotIn('stderr=subprocess.DEVNULL', corpo,
                         'o motivo real da morte do navegador seria destruido')


if __name__ == '__main__':
    unittest.main()
