# -*- coding: utf-8 -*-
"""BLOQUEADAS-268 — um link com acento não pode condenar a fonte (IT-T7-252, peritiagrari.it). Sem rede:
o `urlopen` é substituído e só se confere o endereço que chegaria ao pedido."""
import sys
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import canario as CAN            # noqa: E402
import reparar_contrato as RC    # noqa: E402

COM_ACENTO = "https://www.peritiagrari.it/notizie/la-novità-del-collegio-perché.html"


class _Resp:
    status = 200

    def __init__(self, url):
        self._url = url

    def read(self, n=-1):
        return b"<html>ok</html>"

    def geturl(self):
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _urlopen_que_so_aceita_ascii(req, timeout=None, context=None):
    url = req.full_url
    url.encode("ascii")          # o que o urllib real faz ao montar o pedido: rebenta com acento
    _urlopen_que_so_aceita_ascii.visto.append(url)
    return _Resp(url)


class UrlSegura(unittest.TestCase):
    def setUp(self):
        _urlopen_que_so_aceita_ascii.visto = []
        p = mock.patch.object(urllib.request, "urlopen", _urlopen_que_so_aceita_ascii)
        p.start()
        self.addCleanup(p.stop)

    def test_canario_busca_link_com_acento(self):
        st, b, err = CAN.buscar(COM_ACENTO)
        self.assertEqual((200, ""), (st, err))
        self.assertEqual(["https://www.peritiagrari.it/notizie/la-novit%C3%A0-del-collegio-perch%C3%A9.html"],
                         _urlopen_que_so_aceita_ascii.visto)

    def test_reparo_busca_link_com_acento(self):
        st, b, err, destino = RC.buscar_com_destino(COM_ACENTO)
        self.assertEqual((200, ""), (st, err))
        self.assertTrue(destino.isascii())

    def test_ja_codificado_nao_muda(self):
        for u in ("https://www.cnr.it/it/news/12345/titolo?x=1&y=a%20b#sec",
                  "https://www.peritiagrari.it/notizie/la-novit%C3%A0.html",
                  "https://it.wikipedia.org/wiki/Agricoltura_(disciplina)"):
            with self.subTest(u=u):
                self.assertEqual(u, CAN.url_segura(u))
                self.assertEqual(CAN.url_segura(u), CAN.url_segura(CAN.url_segura(u)))

    def test_espaco_vira_por_cento_20(self):
        self.assertEqual("https://x.it/a%20b", CAN.url_segura("https://x.it/a b"))


if __name__ == "__main__":
    unittest.main()
