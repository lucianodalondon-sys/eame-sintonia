# -*- coding: utf-8 -*-
"""TRAVA-CONTAR (D59) · o resumo auditavel da onda so conta CONFERIDO por RUN_ID; e nao inventa numeros.

    py -m unittest tests.test_trava_contar

Sem rede, sem Sala, sem o vivo: livros e pastas de onda escritos aqui.
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("cei_tc", RAIZ / "system-map" / "scripts" / "censo_das_estradas_it.py")
M = importlib.util.module_from_spec(_s)
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))
_s.loader.exec_module(M)
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
import resumo_da_onda as RD   # noqa: E402

RUN = "IT-T2-2026-09-25-111503-02c8a050416a4723"


def _linha(**k):
    x = {"SOURCE_ID": "IT-T2-034", "RUN_ID": RUN, "STATUS": "SUCCESS", "RAW": 3, "DERIVED": 3,
         "PROVENIENCIA": {"SALA_LINHAS": 1, "SALA_COM_CADEIA_INTEIRA": 1}}
    x.update(k)
    return x


CORRIDAS = {RUN: {"FAILED": 0, "HEALTHY": 1, "RAW_OBJECTS_CREATED": 3}}
FONTES = {RUN: {"IT-T2-034"}}


class TestConferencia(unittest.TestCase):
    def test_linha_certa_conta(self):
        self.assertEqual((True, "CONFERIDA"), M.conferir_linha(_linha(), CORRIDAS, FONTES))

    def test_resumo_forjado_run_id_que_o_livro_nao_tem(self):
        self.assertEqual((False, "RUN_ID_AUSENTE_NO_LIVRO"),
                         M.conferir_linha(_linha(RUN_ID="IT-T2-2026-09-25-000000-forjado"), CORRIDAS, FONTES))

    def test_raw_zero_nao_conta(self):
        self.assertEqual((False, "SEM_DOCUMENTO_NOVO"), M.conferir_linha(_linha(RAW=0), CORRIDAS, FONTES))
        self.assertEqual((False, "SEM_DOCUMENTO_NOVO"), M.conferir_linha(_linha(DERIVED=0), CORRIDAS, FONTES))

    def test_unknown_nao_conta(self):
        for k in ("RAW", "DERIVED"):
            self.assertEqual((False, "RAW_OU_DERIVED_UNKNOWN"), M.conferir_linha(_linha(**{k: "UNKNOWN"}), CORRIDAS, FONTES))
        self.assertEqual((False, "RAW_OU_DERIVED_UNKNOWN"), M.conferir_linha(_linha(RAW=True), CORRIDAS, FONTES))

    def test_raw_que_nao_bate_com_o_livro(self):
        self.assertEqual((False, "RAW_NAO_BATE_COM_O_LIVRO"), M.conferir_linha(_linha(RAW=5, DERIVED=5), CORRIDAS, FONTES))

    def test_fonte_que_o_livro_nao_observou(self):
        self.assertEqual((False, "FONTE_NAO_BATE_COM_O_LIVRO"),
                         M.conferir_linha(_linha(SOURCE_ID="IT-T2-051"), CORRIDAS, FONTES))

    def test_o_livro_diz_failed(self):
        c = {RUN: dict(CORRIDAS[RUN], FAILED=1)}
        self.assertEqual((False, "O_LIVRO_DIZ_FAILED"), M.conferir_linha(_linha(), c, FONTES))

    def test_proveniencia_partida_ou_desconhecida(self):
        self.assertEqual((False, "PROVENIENCIA_PARTIDA_OU_UNKNOWN"), M.conferir_linha(
            _linha(PROVENIENCIA={"SALA_LINHAS": 2, "SALA_COM_CADEIA_INTEIRA": 1}), CORRIDAS, FONTES))
        self.assertEqual((False, "PROVENIENCIA_PARTIDA_OU_UNKNOWN"), M.conferir_linha(
            _linha(PROVENIENCIA="UNKNOWN"), CORRIDAS, FONTES))

    def test_status_e_nao_correu(self):
        self.assertEqual((False, "STATUS_NAO_E_SUCCESS"), M.conferir_linha(_linha(STATUS="FAILED"), CORRIDAS, FONTES))
        self.assertEqual((False, "NAO_CORREU"), M.conferir_linha({"SOURCE_ID": "IT-T2-146", "RUN_ID": None}, CORRIDAS, FONTES))


class TestDePontaAPonta(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        self.ondas = self.t / "ondas"
        self.ondas.mkdir()
        self.livro = self.t / "livro"
        self.livro.mkdir()
        (self.livro / "runs.ndjson").write_text(json.dumps({"RUN_ID": RUN, "contadores": CORRIDAS[RUN]}) + "\n", encoding="utf-8")
        (self.livro / "observations.ndjson").write_text(
            "".join(json.dumps({"RUN_ID": RUN, "SOURCE_ID": "IT-T2-034", "RAW_SHA256": str(i)}) + "\n" for i in range(3)),
            encoding="utf-8")
        self.resumo = {"DATASET": M.DATASET_DO_RESUMO, "FONTES": [_linha(), _linha(SOURCE_ID="IT-T9-999", RUN_ID="IT-T9-forjado")]}
        (self.ondas / "X-RESUMO.json").write_text(json.dumps(self.resumo), encoding="utf-8")

    def test_so_a_linha_conferida_prova(self):
        prova, rel = M.provas_dos_resumos(str(self.ondas), str(self.livro))
        self.assertEqual(["IT-T2-034"], sorted(prova))
        self.assertIn("conferido por RUN_ID", prova["IT-T2-034"])
        self.assertEqual({"CONFERIDA": 1, "RUN_ID_AUSENTE_NO_LIVRO": 1}, rel["LINHAS_POR_MOTIVO"])
        self.assertTrue(rel["LIVRO_SHA256"]["runs.ndjson"])

    def test_sem_livro_nada_conta(self):
        prova, rel = M.provas_dos_resumos(str(self.ondas), str(self.t / "nao-existe"))
        self.assertEqual({}, prova)
        self.assertIsNone(rel["LIVRO_SHA256"]["runs.ndjson"])

    def test_um_resumo_na_pasta_de_cima_nao_conta_sem_conferencia(self):
        p = self.t / "RESUMO-NA-PASTA-DE-CIMA.json"
        p.write_text(json.dumps(self.resumo), encoding="utf-8")
        self.assertEqual({}, M.provas_do_registo(str(p)))

    def test_ficheiro_que_nao_e_resumo_e_ignorado(self):
        (self.ondas / "Y-RESUMO.json").write_text(json.dumps({"FONTES": [_linha()]}), encoding="utf-8")
        prova, rel = M.provas_dos_resumos(str(self.ondas), str(self.livro))
        self.assertEqual(1, rel["LINHAS_POR_MOTIVO"].get("NAO_E_RESUMO"))


class TestResumoNaoInventa(unittest.TestCase):
    def _onda(self, estado, relatorios=None):
        t = Path(tempfile.mkdtemp()) / "ONDA-X"
        t.mkdir()
        (t / "ONDA-WEB-ESTADO.json").write_text(json.dumps(estado), encoding="utf-8")
        for sid, rel in (relatorios or {}).items():
            (t / sid).mkdir()
            (t / sid / "RELATORIO-PASSAGEM.json").write_text(json.dumps(rel), encoding="utf-8")
        return t

    def _rel(self, run, raw=3, der=3):
        return {"RUN_IDS": [run], "CONTAGENS": {"RAW_CREATED": raw},
                "CRITERIOS": {"C4_PROVENIENCIA_COMPLETA": {"COM_DERIVADO": der, "SALA_LINHAS": 1, "SALA_COM_CADEIA_INTEIRA": 1},
                              "C7_PROPORCAO_POR_FONTE_E_CLASSE": {"POR_FONTE": {"IT-A": {"SIM": 1}}}}}

    def test_le_o_relatorio_da_mesma_corrida(self):
        t = self._onda({"FONTES": [{"SOURCE_ID": "IT-A", "RUN_ID": "R1", "STATUS": "SUCCESS", "CORREU": True,
                                     "GATE": "ELIGIBLE", "EGRESSO": ["IT", "IT"], "LIVRO_DA_ONDA": "C:/segredo",
                                     "C4": {"COM_DERIVADO": 9}}]}, {"IT-A": self._rel("R1")})
        f = RD.resumo(t)["FONTES"][0]
        self.assertEqual((3, 3, {"SIM": 1}), (f["RAW"], f["DERIVED"], f["VEREDICTOS_DA_ADMISSION"]))
        self.assertTrue(f["RELATORIO_SHA256"])
        self.assertNotIn("C:/segredo", json.dumps(RD.resumo(t)), "caminhos do estado nao passam para o resumo")

    def test_relatorio_de_outra_corrida_e_recusado_e_fica_unknown(self):
        t = self._onda({"FONTES": [{"SOURCE_ID": "IT-A", "RUN_ID": "R1", "STATUS": "SUCCESS"}]}, {"IT-A": self._rel("R0")})
        f = RD.resumo(t)["FONTES"][0]
        self.assertIn("RELATORIO_RECUSADO", f)
        self.assertEqual((RD.UNKNOWN, RD.UNKNOWN), (f["RAW"], f["DERIVED"]))

    def test_sem_relatorio_e_sem_numero_no_estado_fica_unknown(self):
        t = self._onda({"FONTES": [{"SOURCE_ID": "IT-A", "RUN_ID": "R1", "STATUS": "SUCCESS"}]})
        f = RD.resumo(t)["FONTES"][0]
        self.assertEqual((RD.UNKNOWN, RD.UNKNOWN), (f["RAW"], f["DERIVED"]))

    def test_o_estado_novo_com_raw_e_derived_serve(self):
        t = self._onda({"FONTES": [{"SOURCE_ID": "IT-A", "RUN_ID": "R1", "STATUS": "SUCCESS", "RAW": 2, "DERIVED": 2,
                                     "C4": {"COM_DERIVADO": 2, "SALA_LINHAS": 0, "SALA_COM_CADEIA_INTEIRA": 0}}]})
        f = RD.resumo(t)["FONTES"][0]
        self.assertEqual((2, 2, "linha do estado"), (f["RAW"], f["DERIVED"], f["DE_ONDE"]))

    def test_fonte_que_nao_correu(self):
        t = self._onda({"FONTES": [{"SOURCE_ID": "IT-A", "CORREU": False, "PORQUE_NAO_CORREU": "TETO_DOMINIO"}]})
        f = RD.resumo(t)["FONTES"][0]
        self.assertEqual("TETO_DOMINIO", f["PORQUE_NAO_CORREU"])
        self.assertNotIn("RAW", f)

    def test_o_executor_e_lido_no_codigo(self):
        self.assertEqual("coleta/italy_executor.py", RD.executor_da_porta())

    def test_o_condutor_grava_raw_derived_e_escreve_o_resumo(self):
        src = (RAIZ / "ferramentas" / "big_collection" / "onda_web.py").read_text(encoding="utf-8")
        self.assertIn('"RAW": ((r.get("RELATORIO") or {}).get("CONTAGENS") or {}).get("RAW_CREATED")', src)
        self.assertIn('"DERIVED": (C.get("C4_PROVENIENCIA_COMPLETA") or {}).get("COM_DERIVADO")', src)
        self.assertEqual(2, src.count("    resumir(saida)"), "no fim da onda e quando um disjuntor a para")


if __name__ == "__main__":
    unittest.main()
