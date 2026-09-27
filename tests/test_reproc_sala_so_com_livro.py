# -*- coding: utf-8 -*-
"""REPROC-SALA-PLANO (27/09) — uma linha sem livro do coletor fica como está.

Medido na Sala real (plano do coordenador, 10:35, sem escrever): 100 linhas T6 (EU-T5-001, OpenAlex),
pousadas por `pousar_na_sala.py`, sem livro do coletor. Revistas pela porta do tempo e do lugar,
a data de publicação de todas as 100 passava a NAO SEI. Com `--so-com-livro`, não se escreve nada
para elas, e ficam contadas. Sem banco: a Sala é trocada por um dublê.

    py -m unittest tests.test_reproc_sala_so_com_livro
"""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "admissao"))
sys.path.insert(0, RAIZ)
import reprocessar_tempo_lugar as R  # noqa: E402

LINHA_T6 = {"RUN_ID": "IT-T6-2026-09-27-000000-aaaa", "ORDEM": 0, "SOURCE_ID": "EU-T5-001",
            "SHA256": "f" * 64, "ITEM_ID": "https://doi.org/10.1/x", "TEXTO": "titulo e resumo",
            "RAW_OBSERVATION_ID": "raw:1", "CAPTURED_AT": "2026-09-27T10:00:00Z", "UNIVERSO": "T5",
            "STORAGE_PATH": None, "MEDIA_TYPE": "application/json"}


class UmaLinhaSemLivroFicaComoEsta(unittest.TestCase):

    def _corre(self, *extra):
        escritas = []
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(R.espera, "exigir_canonica", return_value={}), \
                mock.patch.object(R.espera, "linhas_para_revisao", return_value=[dict(LINHA_T6)]), \
                mock.patch.object(R.espera, "rever",
                                  side_effect=lambda *a, **k: escritas.append(a) or
                                  {"INSERIDAS": 1, "JA_ERAM_ASSIM": 0}), \
                mock.patch.object(R, "ready_de", side_effect=AssertionError("nao se rele")) as rd:
            saida = os.path.join(d, "s.json")
            livro = os.path.join(d, "vazio.ndjson")
            open(livro, "w").close()
            R.main(["--livros", livro, "--aplicar", "--saida", saida, *extra])
            return json.load(open(saida, encoding="utf-8")), escritas, rd

    def test_com_a_opcao_nao_se_escreve_nada_e_fica_contada(self):
        fora, escritas, rd = self._corre("--so-com-livro")
        self.assertEqual(escritas, [])
        rd.assert_not_called()
        self.assertEqual(fora["CONTA"]["SEM_LIVRO"], 1)
        self.assertEqual(fora["CONTA"]["SALTADAS_SEM_LIVRO"], 1)
        self.assertEqual(fora["CONTA"]["REVISTAS_SEM_LIVRO"], 0)
        self.assertEqual(fora["ITENS"][0]["SALTADA"], "SEM_LIVRO")

    def test_sem_a_opcao_a_linha_e_relida_como_antes(self):
        with self.assertRaises(AssertionError):     # ready_de chamado: o comportamento de antes
            self._corre()


if __name__ == "__main__":
    unittest.main()
