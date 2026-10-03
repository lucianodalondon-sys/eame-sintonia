# -*- coding: utf-8 -*-
"""NUNCA PROPOR SEM PROVA — e a prova tem de existir em disco com o sha256 declarado.

Medido em 2026-09-23 pela coordenacao: das 88 linhas com ACCAO, 4 apontavam
para provas que nao estavam onde as outras estavam (3 no acervo do Git, 1 so
com o sha do TEXTO do canario). Este teste reprova qualquer linha com ACCAO !=
UNKNOWN que tenha uma prova sem ficheiro, ou com ficheiro cujo sha256 difere.

Os bytes vivem fora do Git (~/sintonia-gabarito). Numa maquina sem essa pasta
o teste SALTA com a razao escrita — nao passa calado.
"""
import hashlib
import json
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PROPOSTA = RAIZ / "curadoria" / "PROPOSTA-CATALOGO-V1.json"
PROVAS_EM = Path.home() / "sintonia-gabarito"


def _sha(f: Path) -> str:
    return hashlib.sha256(f.read_bytes()).hexdigest()


class ProvaEmDisco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.linhas = json.loads(PROPOSTA.read_text(encoding="utf-8"))["LINHAS"]

    def test_toda_accao_tem_prova(self):
        sem = [l["SOURCE_ID"] for l in self.linhas if l["ACCAO"] != "UNKNOWN" and not l["PROVA"]]
        self.assertEqual([], sem)

    def test_toda_prova_de_uma_accao_existe_com_o_sha256_declarado(self):
        if not PROVAS_EM.is_dir():
            self.skipTest("bytes das provas fora do Git e ausentes nesta maquina: %s" % PROVAS_EM)
        falhas = []
        for l in self.linhas:
            if l["ACCAO"] == "UNKNOWN":
                continue
            for p in l["PROVA"]:
                f = Path(p.get("FICHEIRO") or "")
                if not p.get("FICHEIRO") or not f.is_file():
                    falhas.append((l["SOURCE_ID"], p["ORIGEM"], "sem ficheiro"))
                elif _sha(f) != p["SHA256"]:
                    falhas.append((l["SOURCE_ID"], p["ORIGEM"], "sha256 difere"))
        self.assertEqual([], falhas)

    def test_a_agrofarma_ficou_unknown_porque_so_tinha_o_sha_do_texto(self):
        l = next(l for l in self.linhas if l["SOURCE_ID"] == "IT-T7-043")
        self.assertEqual("UNKNOWN", l["ACCAO"])
        self.assertIn("MUDAR_PARA_T9", l["PORQUE"])


if __name__ == "__main__":
    unittest.main()
