"""O instrumento da micro-coleta, provado SEM REDE.

Toda chamada a programa externo (curl, node, psql, orquestrador) passa por
`subprocess.run` do modulo — e aqui ele e trocado por um que rebenta. Um
teste que tentasse ir a rede ou ao banco falhava em vez de ir.

Nao se fixam contagens do livro (e um servico vivo): afirmam-se leis.
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "micro_coleta", RAIZ / "scripts" / "micro_coleta" / "micro_coleta.py")
MC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MC)

AMBIENTE_OK = {"SINTONIA_COLLECTION_DSN": "x", "SINTONIA_SALA_DSN": "x",
               "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_PSQL_EXE": "x"}


def _proibido(*a, **k):
    raise AssertionError(f"programa externo chamado num teste sem rede: {a[:1]}")


class _Lancador:
    def __init__(self):
        self.comandos = []

    def __call__(self, cmd):
        self.comandos.append(cmd)
        sid = next(a.split("=", 1)[1] for a in cmd if a.startswith("fonte="))
        return {"CODIGO": 0, "SAIDA": f"CORRIDA SUCCESS · RUN-FIXTURE-{sid}"}


@mock.patch.object(MC.subprocess, "run", _proibido)
class TestCorrerNaoVaiARedeSemTudoCerto(unittest.TestCase):

    def test_sem_autorizacao_nao_lanca(self):
        l = _Lancador()
        r = MC.correr(lancar=l, egresso=lambda: {"PAIS": "IT"}, ambiente=AMBIENTE_OK)
        self.assertFalse(r["CORREU"])
        self.assertEqual(l.comandos, [])

    def test_sem_as_variaveis_da_sala_nao_lanca(self):
        l = _Lancador()
        r = MC.correr(autorizado=True, lancar=l, egresso=lambda: {"PAIS": "IT"}, ambiente={})
        self.assertFalse(r["CORREU"])
        self.assertEqual(len(r["FALTA"]), 4)
        self.assertEqual(l.comandos, [])

    def test_sala_em_ficheiro_ou_banco_descartavel_recusa(self):
        for extra in ({"SINTONIA_SALA_BACKEND": "FICHEIRO"}, {"BANCO_DESCARTAVEL_URL": "x"}):
            l = _Lancador()
            r = MC.correr(autorizado=True, lancar=l, egresso=lambda: {"PAIS": "IT"},
                          ambiente={**AMBIENTE_OK, **extra})
            self.assertFalse(r["CORREU"], extra)
            self.assertEqual(l.comandos, [])

    def test_egresso_brasil_nao_lanca_nenhuma(self):
        l = _Lancador()
        r = MC.correr(autorizado=True, lancar=l, egresso=lambda: {"PAIS": "BR"},
                      ambiente=AMBIENTE_OK, consulta=_proibido)
        self.assertEqual(l.comandos, [])
        for c in r["CORRIDAS"]:
            self.assertFalse(c["CORREU"])

    def test_egresso_it_lanca_so_as_prontas_e_pela_porta_canonica(self):
        l = _Lancador()
        p = MC.plano()
        prontas = {x["SOURCE_ID"] for x in p["LINHAS"] if x["ESTADO"] == "PRONTA"}
        r = MC.correr(autorizado=True, lancar=l, egresso=lambda: {"PAIS": "IT"},
                      ambiente=AMBIENTE_OK, consulta=lambda q: [])
        lancadas = {next(a.split("=", 1)[1] for a in c if a.startswith("fonte="))
                    for c in l.comandos}
        self.assertEqual(lancadas, prontas)
        for c in l.comandos:
            self.assertEqual(c[1], "orquestrador/orquestrador.py")
            self.assertIn("--filtro", c)
            self.assertTrue(any(a.startswith("universo=") for a in c))
        for c in r["CORRIDAS"]:
            if c["CORREU"]:
                self.assertEqual(c["GATE_NO_INSTANTE"], "ELIGIBLE")
                self.assertEqual(c["EGRESSO_ANTES"]["PAIS"], "IT")
                self.assertEqual(c["EGRESSO_DEPOIS"]["PAIS"], "IT")


@mock.patch.object(MC.subprocess, "run", _proibido)
class TestPlano(unittest.TestCase):

    def test_excluidas_nunca_sao_propostas(self):
        c = MC.ler_coorte()
        prop = {f["SOURCE_ID"] for f in c["PROPOSTAS"]}
        excl = {f["SOURCE_ID"] for f in c["EXCLUIDAS"]}
        self.assertEqual(prop & excl, set())
        self.assertEqual(excl, {"IT-T7-017", "IT-T7-033", "IT-T7-042"})

    def test_pronta_tem_gate_contrato_receita_e_frase(self):
        for l in MC.plano()["LINHAS"]:
            if l["ESTADO"] == "PRONTA":
                self.assertEqual(l["GATE"], "ELIGIBLE", l["SOURCE_ID"])
                self.assertTrue(l["CONTRATO"] and l["RECEITA_WEB"] and l["FRASE_RESOLVE"])
            else:
                self.assertTrue(l["FALTA"], l["SOURCE_ID"])


    def test_filtros_das_missoes_3_e_3b_so_bloqueiam(self):
        t = Path(tempfile.mkdtemp())
        ro, re_ = t / "rotas.json", t / "rel.json"
        base = {x["SOURCE_ID"]: x["ESTADO"] for x in MC.plano()["LINHAS"]}
        prontas = [s for s, e in base.items() if e == "PRONTA"]
        ro.write_text(json.dumps({"LINHAS": [{"SOURCE_ID": prontas[0], "VEREDITO": "CAPABILITY_BLOCK"}]}))
        re_.write_text(json.dumps({"LINHAS": [{"SOURCE_ID": prontas[1], "RELEVANCIA": "NAO"}]
                                   + [{"SOURCE_ID": s, "RELEVANCIA": "SIM"} for s in base if s != prontas[1]]}))
        with mock.patch.object(MC, "ROTAS", ro), mock.patch.object(MC, "RELEVANCIA", re_):
            depois = {x["SOURCE_ID"]: x for x in MC.plano()["LINHAS"]}
        self.assertEqual(depois[prontas[0]]["ESTADO"], "BLOQUEADA")
        self.assertEqual(depois[prontas[1]]["ESTADO"], "BLOQUEADA")
        for s, e in base.items():          # nunca promove
            if e == "BLOQUEADA":
                self.assertEqual(depois[s]["ESTADO"], "BLOQUEADA")


@mock.patch.object(MC.subprocess, "run", _proibido)
class TestBancoSoLeitura(unittest.TestCase):

    def test_escrita_recusada_antes_do_psql(self):
        for q in ("delete from sala_de_espera", "update raw_asset set id=1",
                  "insert into x values (1)", "select 1; drop table raw_asset",
                  "with x as (select 1) delete from raw_asset; select 1"):
            with self.assertRaises(MC.EscritaRecusada, msg=q):
                MC.sql(q)


class TestRelatorioComFixture(unittest.TestCase):

    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        (self.t / "XX").mkdir()
        (self.t / "XX" / "materia.html").write_bytes(
            b"<html><body><p>" + b"Il prezzo delle pere e salito. " * 60 + b"</p></body></html>")
        (self.t / "XX" / "capa.html").write_bytes(
            b"<html><body>" + b"".join(b'<a href="/n%d">n</a>' % i for i in range(200))
            + b"</body></html>")
        self.livro = self.t / "livro.json"
        self.livro.write_text(json.dumps({"DECISOES": [
            {"item": "derived:10", "resultado": "SIM", "corrida": "R1"},
            {"item": "derived:11", "resultado": "NAO", "corrida": "R1"}]}), encoding="utf-8")

    def _consulta(self, sala_item="derived:10", cadeia="1"):
        def q(s):
            if "from raw_asset r left join" in s:
                return [["1", "IT-X-1", "text/html", "XX/materia.html", "7", "10", "t", "R1"],
                        ["2", "IT-X-1", "text/html", "XX/capa.html", "8", "11", "t", "R1"]]
            if "from sala_de_espera" in s:
                return [[sala_item, "1", "IT-X-1", "NAO SEI", "NAO SEI", "t", "R1", cadeia]]
            raise AssertionError(s)
        return q

    def test_mede_os_criterios(self):
        corr = [{"SOURCE_ID": "IT-X-1", "CORREU": True, "GATE_NO_INSTANTE": "ELIGIBLE",
                 "EGRESSO_ANTES": {"PAIS": "IT"}, "EGRESSO_DEPOIS": {"PAIS": "IT"}}]
        r = MC.relatorio(["R1"], corridas=corr, consulta=self._consulta(),
                         livro=self.livro, armazem=self.t, saida=self.t / "out")
        C = r["CRITERIOS"]
        self.assertTrue(C["C1_EGRESSO_IT_POR_CORRIDA"]["PASSA"])
        self.assertEqual(C["C2_MATERIA_NAO_CAPA"]["ESTADO"], "PENDENTE_HUMANO")
        self.assertEqual(C["C2_MATERIA_NAO_CAPA"]["CAPAS_DO_JUIZ"], ["2"])
        self.assertTrue(C["C3_PONTE_EM_RUNTIME"]["PASSA"])
        self.assertTrue(C["C4_PROVENIENCIA_COMPLETA"]["PASSA"])
        self.assertEqual(C["C5_FACT_TIME_LOCATION"]["FACT_TIME_UNKNOWN"], 1)
        self.assertTrue(C["C6_ZERO_BYPASS"]["PASSA"])
        self.assertEqual(C["C7_PROPORCAO_POR_FONTE_E_CLASSE"]["POR_FONTE"],
                         {"IT-X-1": {"SIM": 1, "NAO": 1}})
        self.assertIn("2\tIT-X-1", (self.t / "out" / "CAPAS-A-CONFIRMAR.tsv").read_text(encoding="utf-8"))

    def test_bypass_e_cadeia_partida_reprovam(self):
        r = MC.relatorio(["R1"], consulta=self._consulta(sala_item="derived:11", cadeia="0"),
                         livro=self.livro, armazem=self.t)
        C = r["CRITERIOS"]
        self.assertFalse(C["C6_ZERO_BYPASS"]["PASSA"])      # NAO na Sala
        self.assertFalse(C["C4_PROVENIENCIA_COMPLETA"]["PASSA"])
        self.assertFalse(C["C1_EGRESSO_IT_POR_CORRIDA"]["PASSA"])  # sem medicao = FAIL
        self.assertFalse(C["C3_PONTE_EM_RUNTIME"]["PASSA"])

    def test_bytes_em_falta_reprovam(self):
        (self.t / "XX" / "capa.html").unlink()
        r = MC.relatorio(["R1"], consulta=self._consulta(), livro=self.livro, armazem=self.t)
        self.assertEqual(r["CRITERIOS"]["C2_MATERIA_NAO_CAPA"]["ESTADO"], "FAIL")

    def test_controlo_negativo_do_juiz(self):
        self.assertTrue(MC.controlo_negativo_de_capa()["PASSA"])

    def test_run_id_com_aspas_recusado(self):
        with self.assertRaises(ValueError):
            MC.relatorio(["R1' or '1'='1"], consulta=_proibido, livro=self.livro)


if __name__ == "__main__":
    unittest.main()
