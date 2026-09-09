#!/usr/bin/env python3
"""A CADEIA DE OBSERVACAO, EXERCITADA CONTRA UM CHROME DE VERDADE.

`cdp.escutar()` e `cdp.corpo_da_resposta()` foram escritos em 2026-09-09 e
ficaram sem executar: eles so servem com um navegador vivo, e o runner local
estava offline. Codigo que nunca correu nao e codigo que funciona.

    CODIGO ESCRITO != CODIGO EXERCITADO.

Este teste sobe um servidor HTTP local, faz uma pagina buscar um JSON com a
forma REAL de um Story, e prova as tres coisas que a rota propria depende:

    1. observar o que a pagina JA pediu, sem pedir nada a mais;
    2. ler o corpo que ja chegou, SEM repetir a requisicao — repetir seria uma
       segunda chamada a plataforma para ler o que ja esta na mao, com risco de
       rate limit anexado;
    3. o objeto que sai da porta de tipo e um Story canonico.

Nao ha Instagram aqui, e isso e de proposito: este teste mede o MECANISMO. A
prova viva de Story e outra coisa, depende de sessao autenticada e da lei de
politica desta casa, e nao se confunde com esta.

Pula quando nao ha Chrome na maquina. Pular e honesto; fingir que passou nao.
"""
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
sys.path.insert(0, os.path.join(RAIZ, 'leis'))
import _gavetas  # noqa: E402,F401
import cdp                       # noqa: E402
import instagram_stories as ist  # noqa: E402

PORTA_CDP = 9344
PORTA_HTTP = 8144

STORY = {
    'id': '3210000000000000001', 'product_type': 'story', 'taken_at': 1789000000,
    'expiring_at': 1789086400, 'is_reel_media': True, 'caption_is_edited': False,
    'media_type': 1, 'user': {'username': 'conta_publica_exemplo', 'id': '999'},
    'image_versions2': {'candidates': [{'url': 'https://cdn.exemplo/i.jpg'}]},
    'original_width': 1080, 'original_height': 1920,
}
PAGINA = ("<!doctype html><meta charset=utf-8><title>t</title>"
          "<script>fetch('/tray.json').then(r=>r.json())</script>")


def _acha_chrome():
    for c in ('google-chrome', 'chromium', 'chromium-browser'):
        p = shutil.which(c)
        if p:
            return p
    for p in ('/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
              r'C:\Program Files\Google\Chrome\Application\chrome.exe'):
        if os.path.exists(p):
            return p
    return None


@unittest.skipUnless(_acha_chrome(), 'sem Chrome nesta maquina')
class ObservarNaoEPedirDeNovo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import http.server
        import tempfile
        cls.dir = tempfile.mkdtemp(prefix='cdp-prova-')
        with open(os.path.join(cls.dir, 'tray.json'), 'w', encoding='utf-8') as f:
            json.dump([STORY], f)
        with open(os.path.join(cls.dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(PAGINA)

        d = cls.dir

        class H(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **k):
                super().__init__(*a, directory=d, **k)

            def log_message(self, *a):
                pass

        cls.srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORTA_HTTP), H)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

        cls.chrome = subprocess.Popen(
            [_acha_chrome(), '--headless=new',
             '--remote-debugging-port=%d' % PORTA_CDP,
             '--user-data-dir=%s' % os.path.join(cls.dir, 'perfil'),
             '--no-sandbox', '--disable-gpu', 'about:blank'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(30):
            try:
                cdp.abas(PORTA_CDP)
                break
            except Exception:                                # noqa: BLE001
                time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.chrome.terminate()
        except Exception:                                    # noqa: BLE001
            pass
        try:
            cls.srv.shutdown()
        except Exception:                                    # noqa: BLE001
            pass
        shutil.rmtree(cls.dir, ignore_errors=True)

    def test_a_cadeia_inteira(self):
        aba, _ = cdp.abrir('about:blank', porta=PORTA_CDP, espera=0.3)
        try:
            aba.comando('Network.enable')
            aba.comando('Page.navigate',
                        url='http://127.0.0.1:%d/index.html' % PORTA_HTTP)
            evs = aba.escutar(('Network.responseReceived',), segundos=20,
                              ate=lambda m: m['params']['response']['url']
                              .endswith('tray.json'))
            alvo = [e for e in evs
                    if e['params']['response']['url'].endswith('tray.json')]
            self.assertTrue(alvo, 'escutar() nao colheu o evento da pagina')

            r = alvo[-1]['params']['response']
            self.assertEqual(r['status'], 200)

            corpo = aba.corpo_da_resposta(alvo[-1]['params']['requestId'])
            itens = json.loads(corpo)
            self.assertEqual(len(itens), 1)

            o = ist.normalizar(itens[0], username='conta_publica_exemplo',
                               run_id='CDP-PROVA', country_scope='IT',
                               route='local:cdp')
            self.assertEqual(o['CONTENT_TYPE'], 'STORY')
            self.assertEqual(o['NATIVE_ID'], STORY['id'])
            self.assertEqual(o['EXPIRES_AT_SOURCE'], 'PLATFORM')
            # E o que o SCRAP nao tem o direito de preencher continua vazio,
            # inclusive quando o dado veio do navegador da propria pessoa.
            self.assertEqual(o['FACT_TIME'], 'UNKNOWN')
            self.assertEqual(o['FACT_LOCATION'], 'UNKNOWN')
        finally:
            aba.fechar()

    def test_uma_pagina_que_nao_pede_nada_nao_inventa_evento(self):
        """`escutar()` tem de devolver vazio, e nao travar, quando nao ha o que ver."""
        aba, _ = cdp.abrir('about:blank', porta=PORTA_CDP, espera=0.3)
        try:
            aba.comando('Network.enable')
            evs = aba.escutar(('Network.responseReceived',), segundos=3)
            self.assertEqual([e for e in evs
                              if e['params']['response']['url'].endswith('tray.json')], [])
        finally:
            aba.fechar()


if __name__ == '__main__':
    unittest.main()
