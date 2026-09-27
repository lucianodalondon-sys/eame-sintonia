# -*- coding: utf-8 -*-
"""CANAIS-41 · as duas ferramentas do roteiro: montar as corridas e separar o que se aplica.

Sem rede, sem banco: envelopes temporarios; o DSN nunca e usado aqui.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "canais41"))
import montar_corridas as MC   # noqa: E402
import para_aplicar as PA      # noqa: E402


class Separar(unittest.TestCase):
    def l(self, v, p=""):
        return {"VEREDITO": v, "PORQUE": p}

    def test_ready_aplica_zero_volta_a_medir(self):
        self.assertEqual("APLICAR", PA.classe(self.l("READY", "canario do Scrap ...")))
        self.assertEqual("REMEDIR_DEPOIS", PA.classe(self.l("ZERO", "ZERO_RESULTS")))

    def test_falha_da_fonte_aplica(self):
        for p in ("D53: o item 1 nao prova TITULO (video 'x')",
                  "D53: o item 0 nao prova CANAL (video 'x')",
                  "IDENTIDADE A CONFERIR POR HUMANO: ..."):
            with self.subTest(p=p):
                self.assertEqual("APLICAR", PA.classe(self.l("FALHA", p)))

    def test_falha_nossa_nunca_condena_a_fonte(self):
        for p in ("colheita vazia com RESULT=BUDGET_EXHAUSTED: teto desta execucao",
                  "colheita vazia com RESULT=CREDENTIAL_MISSING: sem chave",
                  "3 itens vistos e 0 linhas RAW no banco da corrida: visto nao e guardado",
                  "o envelope e de 'IT-T8-005', nao de IT-T8-004",
                  "o Atlas nao conhece IT-T7-015: a corrida nao pode ancorar nada",
                  "item 0 sem OWNER_AUTHORIZED, PLATFORM_POLICY_STATUS",
                  "item 0 sem PUBLISHED_AT, OWNER_AUTHORIZED, PLATFORM_POLICY_STATUS"):
            with self.subTest(p=p):
                self.assertEqual("DEFEITO_NOSSO", PA.classe(self.l("FALHA", p)))

    def test_o_filtro_so_passa_as_linhas_a_aplicar(self):
        with tempfile.TemporaryDirectory() as d:
            corr = {"A|1": {"SOURCE_ID": "A", "RUN_ID": "1"}, "B|2": {"SOURCE_ID": "B", "RUN_ID": "2"},
                    "C|3": {"SOURCE_ID": "C", "RUN_ID": "3"}}
            regua = {"LINHAS": [dict(SOURCE_ID="A", RUN_ID="1", VEREDITO="READY", PORQUE="ok"),
                                dict(SOURCE_ID="B", RUN_ID="2", VEREDITO="FALHA", PORQUE="0 linhas RAW no banco"),
                                dict(SOURCE_ID="C", RUN_ID="3", VEREDITO="ZERO", PORQUE="ZERO_RESULTS")]}
            Path(d, "c.json").write_text(json.dumps(corr), encoding="utf-8")
            Path(d, "r.json").write_text(json.dumps(regua), encoding="utf-8")
            PA.main(["x", "--regua=%s" % Path(d, "r.json"), "--corridas=%s" % Path(d, "c.json"),
                     "--saida=%s" % Path(d, "a.json")])
            self.assertEqual(["A|1"], list(json.loads(Path(d, "a.json").read_text(encoding="utf-8"))))
            fora = json.loads(Path(d, "a.fora.json").read_text(encoding="utf-8"))
            self.assertEqual({"DEFEITO_NOSSO", "REMEDIR_DEPOIS"}, {f["CLASSE"] for f in fora})


class Montar(unittest.TestCase):
    def test_sem_dsn_o_raw_fica_nao_sei_e_envelope_trocado_e_problema(self):
        with tempfile.TemporaryDirectory() as d:
            env = Path(d, "env")
            for rid, sid, fase in (("RUN-000001", "IT-T8-004", "canal-youtube"),
                                   ("RUN-000002", "IT-T8-004", "audio-youtube")):
                (env / rid).mkdir(parents=True)
                (env / rid / "ENVELOPE.json").write_text(json.dumps(
                    {"SOURCE_ID_DO_PEDIDO": sid, "FASE": fase}), encoding="utf-8")
            Path(d, "r.tsv").write_text("IT-T8-004\tRUN-000001\nIT-T8-004\tRUN-000002\nIT-T8-005\tRUN-000003\n",
                                        encoding="utf-8")
            rc = MC.main(["x", "--rodada=%s" % Path(d, "r.tsv"), "--envelopes=%s" % env,
                          "--saida=%s" % Path(d, "c.json")])
            c = json.loads(Path(d, "c.json").read_text(encoding="utf-8"))
            self.assertEqual(1, rc)                                  # houve problemas
            self.assertEqual(["IT-T8-004|RUN-000001"], list(c))
            self.assertTrue(str(c["IT-T8-004|RUN-000001"]["MEDIDA"]).startswith("NAO_SEI"))

    def test_run_id_com_forma_estranha_nao_chega_ao_sql(self):
        with self.assertRaises(ValueError):
            MC.raw_da_corrida("postgres://nunca-usado", "x'; drop table raw_asset; --")


if __name__ == "__main__":
    unittest.main()
