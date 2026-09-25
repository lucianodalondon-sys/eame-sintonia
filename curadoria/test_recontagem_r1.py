# -*- coding: utf-8 -*-
"""R1 · recontagem das READY (so com PASS IT) e observador do vivo (so leitura). Sem rede."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]


def _mod(nome):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / "scripts" / "reparo" / ("%s.py" % nome))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


RC = _mod("recontar_ready")
OV = _mod("observar_vivo")
REV = {"FONTES": [{"SOURCE_ID": "IT-T1-001", "CLASSE": "LIMPA"},
                  {"SOURCE_ID": "IT-T1-002", "CLASSE": "ACESSO_PARCIAL"},
                  {"SOURCE_ID": "IT-T1-003", "CLASSE": "SERVICO_OU_INSTITUCIONAL"},
                  {"SOURCE_ID": "IT-T1-004", "CLASSE": "TEMA_A_CONFIRMAR"}]}


def _juntado(*sids):
    return {"READY_NOVAS": [{"SOURCE_ID": s} for s in sids]}


class Conferencia(unittest.TestCase):
    def test_so_limpas_e_parciais_e_pass(self):
        c = RC.conferir(_juntado("IT-T1-001", "IT-T1-002"), REV)
        self.assertEqual(("PASS", 2, []), (c["VEREDITO"], c["READY_NOVAS"], c["ACEITES_QUE_NAO_CHEGARAM"]))

    def test_suspeita_ou_tema_que_sai_ready_e_fail(self):
        for s in ("IT-T1-003", "IT-T1-004"):
            c = RC.conferir(_juntado("IT-T1-001", s), REV)
            self.assertEqual("FAIL", c["VEREDITO"])
            self.assertEqual([s], c["SUSPEITAS_QUE_SAIRAM_READY"])

    def test_ready_fora_da_revisao_e_fail(self):
        c = RC.conferir(_juntado("IT-T9-999"), REV)
        self.assertEqual(("FAIL", ["IT-T9-999"]), (c["VEREDITO"], c["READY_FORA_DA_REVISAO"]))

    def test_aceite_que_nao_chega_e_dito_mas_nao_reprova(self):
        c = RC.conferir(_juntado("IT-T1-001"), REV)
        self.assertEqual(("PASS", ["IT-T1-002"]), (c["VEREDITO"], c["ACEITES_QUE_NAO_CHEGARAM"]))

    def test_a_medicao_das_20h28_confere(self):
        j = json.loads((RAIZ / "scripts" / "reparo" / "R1-INSTALACAO-ENSAIO-5c4daf5a.json").read_text(encoding="utf-8"))
        r = json.loads((RAIZ / "curadoria" / "REVISAO-READY-V1.json").read_text(encoding="utf-8"))
        c = RC.conferir(j, r)
        self.assertEqual(("PASS", 25, 25), (c["VEREDITO"], c["READY_NOVAS"], c["ESPERADAS"]))


class Portao(unittest.TestCase):
    def test_sem_pass_it_espera_vpn_e_nao_monta_nada(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "LIFECYCLE-LEDGER-V1.json").write_text("{}", encoding="utf-8")
            with mock.patch.object(RC, "portao", return_value={"EGRESS_GATE": "BLOCKED", "EGRESS_COUNTRY_CODE": "BR"}), \
                    mock.patch.object(RC, "montar") as montar:
                rc = RC.main(["--foto", d, "--sha", "abc"])
            self.assertEqual(RC.ESPERA_VPN, rc)
            montar.assert_not_called()


class Observador(unittest.TestCase):
    def test_conta_ready_novas_por_classe_e_marcas(self):
        with tempfile.TemporaryDirectory() as d:
            cur = Path(d) / "curadoria"
            cur.mkdir()
            livro = [{"SOURCE_ID": "IT-T1-001", "NEW_STATE": "READY_FOR_COLLECTION", "OBSERVED_AT": "2026-09-25T02:00",
                      "REASON": "x"},
                     {"SOURCE_ID": "IT-T1-002", "NEW_STATE": "READY_FOR_COLLECTION", "OBSERVED_AT": "2026-09-25T02:01",
                      "REASON": "x · ACESSO_PARCIAL: y"},
                     {"SOURCE_ID": "IT-T1-003", "NEW_STATE": "CONTRACTED_CANARY_FAILED",
                      "OBSERVED_AT": "2026-09-25T02:02", "REASON": "REVISAO_R1: SERVICO: z"},
                     {"SOURCE_ID": "IT-T1-000", "NEW_STATE": "READY_FOR_COLLECTION", "OBSERVED_AT": "2026-09-20T00:00",
                      "REASON": "antiga"}]
            (cur / "LIFECYCLE-LEDGER-V1.json").write_text(json.dumps({"TRANSICOES": livro}), encoding="utf-8")
            (cur / "LIFECYCLE-QUEUE-V1.json").write_text(json.dumps({"TAREFAS": [
                {"TASK_TYPE": "REPAIR_CONTRACT", "STATUS": "DONE"},
                {"TASK_TYPE": "REPAIR_CONTRACT", "STATUS": "PENDING"}]}), encoding="utf-8")
            (cur / "REVISAO-READY-V1.json").write_text(json.dumps(REV), encoding="utf-8")
            m = OV.medir(Path(d), "2026-09-25T00:00")
        self.assertEqual(3, m["READY_AGORA"])
        self.assertEqual(2, m["READY_NOVAS_DESDE"])
        self.assertEqual({"LIMPA": 1, "ACESSO_PARCIAL": 1}, m["READY_NOVAS_POR_CLASSE"])
        self.assertEqual([], m["SUSPEITAS_READY"])
        self.assertEqual({"ACESSO_PARCIAL": 1, "REVISAO_R1": 1}, m["MARCAS_NO_LIVRO_DESDE"])
        self.assertEqual({"DONE": 1, "PENDING": 1}, m["REPAIR_CONTRACT_NA_FILA"])


if __name__ == "__main__":
    unittest.main()
