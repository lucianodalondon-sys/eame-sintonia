# -*- coding: utf-8 -*-
"""SINAL PRECOCE NO ACERVO — inventario por territorio, mesmo PDF conta uma vez, texto integral guardado. Sem rede."""
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import sinal_precoce_acervo as S   # noqa: E402

TEXTO = "Bollettino N 25 del 02/09/2026\n  Taccaro Gennaro   frutticini   n. 4 catture di Ceratitis capitata\n"


class Acervo(unittest.TestCase):
    def setUp(self):
        self.r = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="acervo-")))
        for rel, b in (("italy/IT-T3-002/A/v1/SA-02-09.pdf", b"%PDF-1 um"),
                       ("copia/IT-T3-002/SA-02-09.pdf", b"%PDF-1 um"),          # a mesma, noutra pasta
                       ("italy/IT-T2-002/Z/agro.pdf", b"%PDF-1 meteo"),         # outro territorio
                       ("italy/IT-T3-010/B/boll.PDF", b"%PDF-1 dois")):
            f = self.r / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(b)
        (self.r / "italy/IT-T3-099/pasta.pdf").mkdir(parents=True)             # pasta com nome .pdf: ignora

    def test_so_o_territorio_e_uma_vez_por_sha(self):
        inv = S.inventario([self.r], "IT-T3-")
        self.assertEqual(["IT-T3-002", "IT-T3-010"], [e["SOURCE_ID"] for e in inv])
        self.assertEqual(2, len(inv[0]["CAMINHOS"]))

    def test_texto_integral_e_linhas_sem_resumo(self):
        inv = S.inventario([self.r], "IT-T3-")
        res = S.ler_todos(inv[:1], self.r / "textos", extrair=lambda p: TEXTO)
        self.assertEqual(TEXTO, Path(res[0]["TEXTO_INTEGRAL_EM"]).read_text(encoding="utf-8"))
        self.assertEqual(2, res[0]["COPIAS"])
        linha = [x for x in res[0]["LINHAS_COM_SINAL"] if "CONTAGEM" in x["TIPOS"]][0]
        self.assertEqual(TEXTO.splitlines()[1], linha["LINHA"])

    def test_sem_texto_diz_porque(self):
        def rebenta(p):
            raise RuntimeError("pdftotext falhou")
        res = S.ler_todos(S.inventario([self.r], "IT-T3-")[:1], self.r / "t", extrair=rebenta)
        self.assertEqual("SEM_TEXTO", res[0]["ESTADO"])


if __name__ == "__main__":
    unittest.main()
