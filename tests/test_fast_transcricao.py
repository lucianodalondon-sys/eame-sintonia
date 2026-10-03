# -*- coding: utf-8 -*-
"""v0.3 §7A (dono 03/10, main a727bf9): o FAST le o TEXTO, nao o tipo de site.
Video/audio entra pela TRANSCRICAO que a Collection ja gravou (derived_artifact kind=TRANSCRIPTION), com o
sha256 do derivado conferido; envelope application/json sem transcricao continua fora; HTML/PDF nao mudam.
"""
import collections, hashlib, importlib.util, os, re, tempfile, unittest
from html.parser import HTMLParser

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = open(os.path.join(RAIZ, "motor", "fast_auto", "passo1_selecionar.py"), encoding="utf-8").read()
NS = {"__name__": "definicoes", "re": re, "os": os, "Counter": collections.Counter,
      "hashlib": hashlib, "HTMLParser": HTMLParser}
exec(FONTE[FONTE.index("LIMITE_ENTREGA_CHARS = int("):FONTE.index("env = dict(os.environ")] + "\n" +
     FONTE[FONTE.index("TAGS_CASCA = {"):FONTE.index("os.makedirs(AQUI")], NS)

spec = importlib.util.spec_from_file_location("rodada_fast_tr", os.path.join(RAIZ, "motor", "fast_auto", "rodada_fast.py"))
RF = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RF)


class TranscricaoEntraNoPasso1(unittest.TestCase):
    def setUp(self):
        self.arm = tempfile.mkdtemp() + "/"
        NS["ARM"] = self.arm
        self.texto = "Nell'ultimi anni la gestione degli acari e' diventata una vera sfida negli agrumi."
        os.makedirs(self.arm + "d")
        open(self.arm + "d/t.txt", "wb").write(self.texto.encode("utf-8"))
        open(self.arm + "v.mp4", "wb").write(b"\x00\x01video")
        self.tr = {"ID": 1581, "SHA256": hashlib.sha256(self.texto.encode("utf-8")).hexdigest(),
                   "STORAGE_PATH": "d/t.txt", "PRODUTOR": "transcricao-de-midia@1"}

    def test_video_com_transcricao_entrega_o_texto_falado(self):
        r = {"id": 2833, "media_type": "video/mp4", "transcricao": self.tr}
        b, t, casca = NS["bruto"](self.arm + "v.mp4", "video/mp4", NS["transcricao"](r))
        self.assertEqual(t, self.texto)
        self.assertEqual(b, b"\x00\x01video")  # RAW_SHA256 continua o do video capturado

    def test_transcricao_com_sha_diferente_para_a_rodada(self):
        r = {"id": 2833, "transcricao": dict(self.tr, SHA256="0" * 64)}
        with self.assertRaises(AssertionError) as e:
            NS["transcricao"](r)
        self.assertIn("TRANSCRICAO_SHA_NAO_CONFERE", str(e.exception))

    def test_sem_transcricao_html_continua_igual(self):
        open(self.arm + "p.html", "wb").write("<html><body><p>Peronospora in Veneto</p></body></html>".encode())
        self.assertIsNone(NS["transcricao"]({"id": 1, "transcricao": None}))
        b, t, casca = NS["bruto"](self.arm + "p.html", "text/html", None)
        self.assertIn("Peronospora in Veneto", t)


class SelecaoDoCiclo(unittest.TestCase):
    def test_sql_aceita_transcricao_e_nao_abre_json(self):
        visto = {}

        def banco(sql):
            visto["sql"] = sql
            return []
        orig, orig_f = RF.linhas_banco, RF.feitos
        RF.linhas_banco, RF.feitos = banco, (lambda: set())
        try:
            RF.candidatos(20)
        finally:
            RF.linhas_banco, RF.feitos = orig, orig_f
        sql = visto["sql"]
        self.assertIn("kind='TRANSCRIPTION'", sql)
        self.assertIn("transaction read only", sql)
        self.assertNotIn("application/json", sql)


if __name__ == "__main__":
    unittest.main()
