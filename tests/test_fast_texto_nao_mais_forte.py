"""Ordem do dono 02/10 (3 restos de texto): o texto visivel nao pode ser mais forte do que campos/trechos.
Regra unica no cerebro (prompt), nao colecao de regex. Estes testes so garantem que a regra chega ao Opus."""
import ast
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


class TestTextoNaoMaisForte(unittest.TestCase):
    def test_prompt_comercial_tem_regra_geral(self):
        t = (RAIZ / "motor" / "fast_cruzamento_comercial.prompt.md").read_text(encoding="utf-8")
        self.assertIn("NUNCA PODE SER MAIS FORTE DO QUE OS CAMPOS", t)
        for palavra in ("introvabili", "conto economico", "JRC de 24/08", "QUANDO=NAO_SEI"):
            self.assertIn(palavra, t)

    def test_passo2_data_da_fonte_citada(self):
        src = (RAIZ / "motor" / "fast_auto" / "passo2_fatos.py").read_text(encoding="utf-8")
        prompt = None
        for n in ast.parse(src).body:
            if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PROMPT":
                prompt = n.value.value
        self.assertIsNotNone(prompt)
        self.assertIn("data atribuida a essa fonte citada", prompt)
        self.assertIn("so em DATA_PUBLICACAO", prompt)
        self.assertIn("nao e perda de renda", prompt)

    def test_versao_subiu(self):
        src = (RAIZ / "motor" / "fast_cruzamento_comercial.py").read_text(encoding="utf-8")
        self.assertIn("v2.2-texto-nao-mais-forte", src)


if __name__ == "__main__":
    unittest.main()
