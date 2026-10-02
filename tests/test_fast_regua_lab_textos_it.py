# -*- coding: utf-8 -*-
"""LAB 02/10 (AUDITORIA-FAST-CONTEXTOS-v2): natureza/data do documento conferidas por trecho (passo2), fonte
publicitaria marcada por script e texto italiano que nega um campo NAO_SEI medido. Sem LLM (custo 0)."""
import ast
import re
import sys
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from motor import fast_cruzamento_comercial as FC  # noqa: E402

# passo2 corre ao importar (le argv): tira-se so as definicoes puras por AST, sem executar o modulo
_src = (RAIZ / "motor" / "fast_auto" / "passo2_fatos.py").read_text(encoding="utf-8")
_mod = ast.Module(body=[n for n in ast.parse(_src).body if (isinstance(n, ast.FunctionDef) and n.name in
                        ("norm", "conferir_documento")) or (isinstance(n, ast.Assign) and
                        getattr(n.targets[0], "id", "") == "NATUREZAS")], type_ignores=[])
P2 = {"re": re}
exec(compile(_mod, "passo2_fatos.py", "exec"), P2)

TEXTO = P2["norm"]("Terra e Vita · Contenuto sponsorizzato · 29 aprile 2026 · AF-X1 contro le aflatossine")
HOJE = date(2026, 10, 2)
REF = {"USE_IDS": set(), "FRESCOR": "OK", "CARIMBO": {}}
FEN = {"IDS": set()}


class NaturezaDoDocumento(unittest.TestCase):
    def test_publicidade_com_trecho_real(self):
        r = P2["conferir_documento"]({"NATUREZA_DO_DOCUMENTO": {"VALOR": "PUBLICIDADE_PATROCINADO",
                                                                "TRECHO": "Contenuto sponsorizzato"},
                                      "DATA_PUBLICACAO": {"VALOR": "2026-04-29", "TRECHO": "29 aprile 2026"}}, TEXTO)
        self.assertEqual(r["NATUREZA_DO_DOCUMENTO"]["VALOR"], "PUBLICIDADE_PATROCINADO")
        self.assertEqual(r["DATA_PUBLICACAO"]["VALOR"], "2026-04-29")

    def test_trecho_inventado_vira_nao_sei(self):
        r = P2["conferir_documento"]({"NATUREZA_DO_DOCUMENTO": {"VALOR": "EDITORIAL", "TRECHO": "articolo redazionale"}},
                                     TEXTO)
        self.assertEqual(r["NATUREZA_DO_DOCUMENTO"]["VALOR"], "NAO_SEI")
        self.assertEqual(r["NATUREZA_DO_DOCUMENTO"]["VALOR_DO_MODELO"], "EDITORIAL")
        self.assertEqual(r["DATA_PUBLICACAO"]["VALOR"], "NAO_SEI")

    def test_natureza_fora_da_lista_vira_nao_sei(self):
        r = P2["conferir_documento"]({"NATUREZA_DO_DOCUMENTO": {"VALOR": "NOTICIA", "TRECHO": "Terra e Vita"}}, TEXTO)
        self.assertEqual(r["NATUREZA_DO_DOCUMENTO"]["VALOR"], "NAO_SEI")


def _obj(classe="SINAL", titulo_it=None, vis=None, produto="NAO_SEI"):
    campos = {k: {"valor": "x", "FACT_IDs": ["F1"]} for k in FC.CAMPOS}
    campos["PRODUTO_ADAMA"]["valor"] = produto
    campos["AUTORIZACAO_LABEL"]["valor"] = produto
    return {"ID": "C01", "CLASSE": classe, "CAMPOS": campos, "FACT_IDs": ["F1"], "TITULO_IT": titulo_it,
            "TEXTOS_VISIVEIS_IT": vis or {}}


def _conf(o, natureza="PUBLICIDADE_PATROCINADO"):
    fatos = {"F1": {"FACT_ID": "F1", "DOCUMENT_ID": "D1", "SOURCE_ID": "S1", "URL": "https://a.it/x", "quando": "2026",
                    "natureza": natureza, "publicado": "2026-04-29", "evidencias": {"fato": "x"}}}
    return FC.conferir({"objetos": [o]}, fatos, [], REF, FEN, hoje=HOJE, ctx={"IDS": {}}, hist={"IDS": set()})


class FontePublicitaria(unittest.TestCase):
    def test_marca_e_evidencia(self):
        ok, _ = _conf(_obj())
        self.assertEqual(ok[0]["FONTE_PUBLICITARIA"], ["F1"])
        self.assertEqual(ok[0]["EVIDENCIAS"][0]["NATUREZA_DO_DOCUMENTO"], "PUBLICIDADE_PATROCINADO")
        self.assertEqual(ok[0]["EVIDENCIAS"][0]["DATA_PUBLICACAO"], "2026-04-29")

    def test_editorial_nao_marca(self):
        ok, _ = _conf(_obj(), natureza="EDITORIAL")
        self.assertEqual(ok[0]["FONTE_PUBLICITARIA"], [])

    def test_linha_do_fato_leva_natureza_ao_modelo(self):
        ln = FC.linha_fato({"FACT_ID": "F1", "SOURCE_ID": "S1", "natureza": "PUBLICIDADE_PATROCINADO",
                            "publicado": "2026-04-29"})
        self.assertIn("natureza=PUBLICIDADE_PATROCINADO", ln)
        self.assertIn("publicado=2026-04-29", ln)


class TextoItalianoNaoNegaNaoSei(unittest.TestCase):
    def test_titulo_que_nega_campo_nao_sei_e_medido(self):
        ok, _ = _conf(_obj(titulo_it="Mais: noi non abbiamo un impiego autorizzato"))
        self.assertEqual(ok[0]["TEXTO_IT_AFIRMA_ALEM_DO_CAMPO"][0]["EXPRESSAO"].lower(), "non abbiamo")

    def test_formula_correta_passa(self):
        ok, _ = _conf(_obj(titulo_it="Mais: impiego non trovato nelle etichette lette"))
        self.assertNotIn("TEXTO_IT_AFIRMA_ALEM_DO_CAMPO", ok[0])

    def test_campo_com_valor_nao_e_medido(self):
        ok, _ = _conf(_obj(titulo_it="Nessun problema", produto="PROD X"))
        self.assertNotIn("TEXTO_IT_AFIRMA_ALEM_DO_CAMPO", ok[0])


if __name__ == "__main__":
    unittest.main()
