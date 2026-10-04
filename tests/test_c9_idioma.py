# -*- coding: utf-8 -*-
"""C9-IDIOMA · o detector le italiano curto, e o relatorio da onda le o egresso e o portao que o onda_web grava.

    py -m unittest tests.test_c9_idioma

Sem rede e sem Sala: as consultas sao falsas. As duas amostras sao os textos extraidos REAIS dos RAW 1436 e
1437 do MICRO-V3 (IT-T2-051, ARPAE), copiados do armazem com o mesmo sha256.
"""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("micro_coleta_c9", RAIZ / "scripts" / "micro_coleta" / "micro_coleta.py")
MC = importlib.util.module_from_spec(_spec)
sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
_spec.loader.exec_module(MC)

DADOS = RAIZ / "tests" / "dados" / "c9-idioma"
RAW_1436 = DADOS / "raw-1436-arpae-mare-balneabile.txt"
RAW_1437 = DADOS / "raw-1437-arpae-portale-prelievi.txt"
SHA = {RAW_1436: "33a0015cff921ef6a074", RAW_1437: "8a1525fe83addeb7d7ce"}


def _texto(it=0, pt=0, en=0, resto=40):
    return " ".join(["della"] * it + ["uma"] * pt + ["the"] * en + ["parola"] * resto)


class TestDetector(unittest.TestCase):
    def test_as_amostras_sao_as_do_armazem(self):
        for p, h in SHA.items():
            self.assertTrue(hashlib.sha256(p.read_bytes()).hexdigest().startswith(h), p.name)

    def test_as_duas_noticias_da_arpae_sao_italiano(self):
        self.assertEqual("it", MC.idioma(RAW_1436.read_text(encoding="utf-8")), "17 palavras it contra 1")
        self.assertEqual("it", MC.idioma(RAW_1437.read_text(encoding="utf-8")), "9 palavras it contra 0")

    def test_acima_de_20_fica_como_era(self):
        self.assertEqual("it", MC.idioma(_texto(it=25, pt=20)))
        self.assertEqual("en", MC.idioma(_texto(en=20)))

    def test_banda_curta_so_conta_com_dominio_claro(self):
        self.assertEqual("it", MC.idioma(_texto(it=9)))
        self.assertEqual("it", MC.idioma(_texto(it=12, pt=4)))
        self.assertEqual("en", MC.idioma(_texto(en=9)), "o conserto nao e so para italiano")
        self.assertEqual(MC.AUSENCIA, MC.idioma(_texto(it=11, pt=6)), "dominio fraco: NAO SEI")
        self.assertEqual(MC.AUSENCIA, MC.idioma(_texto(it=8, pt=3)), "8 < 3 x 3")
        self.assertEqual(MC.AUSENCIA, MC.idioma(_texto(it=4)), "restos de menu: NAO SEI")
        self.assertEqual(MC.AUSENCIA, MC.idioma(_texto(it=7)), "abaixo do minimo curto")
        self.assertEqual(MC.AUSENCIA, MC.idioma(""))


class TestRelatorio(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        (self.t / "XX").mkdir()
        (self.t / "XX" / "a.html").write_bytes(b"<html><body><p>" + b"Il mare e balneabile. " * 60 + b"</p></body></html>")
        (self.t / "XX" / "b.html").write_bytes(b"<html><body><p>" + b"Aggiornamento dati. " * 60 + b"</p></body></html>")
        (self.t / "XX" / "1436.txt").write_bytes(RAW_1436.read_bytes())
        (self.t / "XX" / "1437.txt").write_bytes(RAW_1437.read_bytes())
        (self.t / "XX" / "en.txt").write_text(_texto(en=9), encoding="utf-8")
        self.livro = self.t / "livro.json"
        # o NAO_SEI do MICRO-V3 foi a quarentena D11 (materia/entrada), sem «palavras» na evidencia
        d11 = {"estagio": "DOCUMENTO", "portoes": {"materia": {"resultado": "NAO_SEI"}}}
        self.livro.write_text(json.dumps({"DECISOES": [
            {"item": "derived:937", "resultado": "NAO_SEI", "regra": "materia", "evidencia": d11, "corrida": "R1"},
            {"item": "derived:938", "resultado": "NAO_SEI", "regra": "materia", "evidencia": d11, "corrida": "R1"},
            {"item": "derived:939", "resultado": "NAO_SEI", "regra": "materia", "evidencia": d11, "corrida": "R1"},
        ]}), encoding="utf-8")

    def _consulta(self, com_ingles=False):
        def q(s):
            if "from raw_asset r left join" in s:
                linhas = [["1436", "IT-T2-051", "text/html", "XX/a.html", "7", "937", "t", "R1", "https://www.arpae.it/a", "XX/1436.txt"],
                          ["1437", "IT-T2-051", "text/html", "XX/b.html", "8", "938", "t", "R1", "https://www.arpae.it/b", "XX/1437.txt"]]
                if com_ingles:
                    linhas.append(["1438", "IT-T2-051", "text/html", "XX/b.html", "9", "939", "t", "R1", "https://www.arpae.it/c", "XX/en.txt"])
                return linhas
            if "count(distinct s.run_id)" in s or "from sala_de_espera" in s:
                return []
            raise AssertionError(s)
        return q

    def test_c9_ja_nao_conta_as_duas_noticias_italianas(self):
        r = MC.relatorio(["R1"], consulta=self._consulta(), livro=self.livro, armazem=self.t)
        c9 = r["CRITERIOS"]["C9_IDIOMA_NAO_DA_NAO_SEI"]
        self.assertEqual({"it": 2}, c9["IDIOMAS"])
        self.assertEqual([], c9["NAO_SEI_ESTRANGEIRO_SEM_SINAL"])
        self.assertTrue(c9["PASSA"])

    def test_a_regra_c9_nao_mudou_estrangeiro_sem_sinal_continua_a_contar(self):
        r = MC.relatorio(["R1"], consulta=self._consulta(com_ingles=True), livro=self.livro, armazem=self.t)
        c9 = r["CRITERIOS"]["C9_IDIOMA_NAO_DA_NAO_SEI"]
        self.assertEqual([{"RAW": "1438", "SOURCE_ID": "IT-T2-051", "IDIOMA": "en"}], c9["NAO_SEI_ESTRANGEIRO_SEM_SINAL"])
        self.assertFalse(c9["PASSA"])

    def _estado(self, egresso=("IT", "IT"), gate="ELIGIBLE"):
        return {"FONTES": [{"N": 1, "SOURCE_ID": "IT-T2-051", "CORREU": True, "STATUS": "SUCCESS", "RUN_ID": "R1",
                            "GATE": gate, "EGRESSO": list(egresso)},
                           {"N": 2, "SOURCE_ID": "IT-T2-034", "CORREU": False, "RUN_ID": None, "GATE": "BLOCKED"}]}

    def test_c1_e_c3_leem_o_que_o_onda_web_grava(self):
        corr = MC.corridas_do_estado(self._estado())
        self.assertEqual(["R1"], [c["RUN_ID"] for c in corr], "fonte que nao correu (sem RUN_ID) nao entra")
        r = MC.relatorio(["R1"], corridas=corr, consulta=self._consulta(), livro=self.livro, armazem=self.t)
        C = r["CRITERIOS"]
        self.assertEqual([("IT-T2-051", "IT", "IT")], [tuple(x) for x in C["C1_EGRESSO_IT_POR_CORRIDA"]["MEDIDO"]])
        self.assertTrue(C["C1_EGRESSO_IT_POR_CORRIDA"]["PASSA"])
        self.assertTrue(C["C3_PONTE_EM_RUNTIME"]["PASSA"])

    def test_o_criterio_nao_afrouxou(self):
        for estado, crit in ((self._estado(egresso=("IT", "US")), "C1_EGRESSO_IT_POR_CORRIDA"),
                             (self._estado(egresso=("IT",)), "C1_EGRESSO_IT_POR_CORRIDA"),
                             (self._estado(gate="BLOCKED"), "C3_PONTE_EM_RUNTIME")):
            r = MC.relatorio(["R1"], corridas=MC.corridas_do_estado(estado), consulta=self._consulta(),
                             livro=self.livro, armazem=self.t)
            self.assertFalse(r["CRITERIOS"][crit]["PASSA"], (estado, crit))

    def test_a_linha_de_comando_passa_as_corridas_do_estado(self):
        p = self.t / "ONDA-WEB-ESTADO.json"
        p.write_text(json.dumps(self._estado()), encoding="utf-8")
        visto = {}

        def falso(ids, *, corridas=None, saida=None, **k):
            visto.update(ids=ids, corridas=corridas)
            return {}
        with mock.patch.object(MC, "relatorio", falso):
            self.assertEqual(0, MC.main(["relatorio", "--estado=%s" % p, "--saida=%s" % (self.t / "out")]))
        self.assertEqual(["R1"], visto["ids"])
        self.assertEqual("ELIGIBLE", visto["corridas"][0]["GATE_NO_INSTANTE"])
        self.assertEqual({"PAIS": "IT"}, visto["corridas"][0]["EGRESSO_DEPOIS"])


if __name__ == "__main__":
    unittest.main()
