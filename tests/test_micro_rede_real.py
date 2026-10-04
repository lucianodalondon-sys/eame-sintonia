"""A4 — as pecas do condutor da micro com rede real, provadas SEM rede.

O que vai a internet (portao de egresso, robots, coletor) corre so no proprio
`micro_rede_real.py`. Aqui provam-se os limites: o caminho das materias que o
robots tem de permitir, o teto de 3 materias por site, a contagem de pedidos por
site e a quarentena contada.
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
_spec = importlib.util.spec_from_file_location(
    "micro_rede_real", RAIZ / "scripts" / "micro_coleta" / "micro_rede_real.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


class TestPrefixoDasMaterias(unittest.TestCase):

    def test_caminhos_reais_da_coorte(self):
        casos = {
            r"^https?://(www\.)?myfruit\.it/news/(?!category/)[a-z0-9]+(?:-[a-z0-9]+)+/?$": "/news/",
            r"^https?://(www\.)?riuniteciv\.com/news-e-eventi/[a-z0-9]+(?:-[a-z0-9]+)+/?$": "/news-e-eventi/",
            r"^https?://agrofarma\.federchimica\.it/news-ed-eventi/dettaglio-news/\d{4}/": "/news-ed-eventi/dettaglio-news/",
            r"^https?://(www\.)?plantgest\.imagelinenetwork\.com/(?!(?:category|tag))": "/",
        }
        for padrao, esperado in casos.items():
            with self.subTest(padrao=padrao[:40]):
                self.assertEqual(R.prefixo_das_materias(padrao), esperado)


class TestTetoDeMaterias(unittest.TestCase):

    def test_so_a_copia_baixa_para_3_e_nunca_sobe(self):
        t = Path(tempfile.mkdtemp())
        (t / "regras").mkdir()
        f = t / "regras" / "italy_contracts_onboarded.json"
        f.write_text(json.dumps({"FONTES": [
            {"SOURCE_ID": "A", "ACQUISITION": {"MAX_TARGETS": 30}},
            {"SOURCE_ID": "B", "ACQUISITION": {"MAX_TARGETS": 1}},
            {"SOURCE_ID": "C", "ACQUISITION": {}}]}), encoding="utf-8")
        mud = R.limitar_contratos(t)
        d = {c["SOURCE_ID"]: c["ACQUISITION"]["MAX_TARGETS"]
             for c in json.loads(f.read_text(encoding="utf-8"))["FONTES"]}
        self.assertEqual(d, {"A": 3, "B": 1, "C": 3})
        self.assertEqual(mud, {"A": 30, "C": None})


class TestContagemPorSite(unittest.TestCase):

    def test_robots_indice_materias_e_falhas_sem_esconder(self):
        corridas = [{"SOURCE_ID": "S", "RUN_ID": "R1"}]
        runs = [{"RUN_ID": "R1", "contadores": {"INDEX_REQUESTS": 1, "DETAIL_REQUESTS": 3}},
                {"RUN_ID": "OUTRA", "contadores": {"INDEX_REQUESTS": 9}}]
        obs = [{"RUN_ID": "R1", "HEALTH_STATE": "FAILED", "SOURCE_URL": "u",
                "OBSERVATION_RESULT": "TRANSPORT_OR_EMPTY", "motivo": "status 403"},
               {"RUN_ID": "R1", "HEALTH_STATE": "HEALTHY", "SOURCE_URL": "v"}]
        l = R.por_site(corridas, runs, obs, {"S": {}})["S"]
        self.assertEqual((l["ROBOTS"], l["INDICE"], l["MATERIAS"], l["TOTAL"]), (1, 1, 3, 5))
        self.assertEqual(l["FALHAS"], [{"URL": "u", "RESULTADO": "TRANSPORT_OR_EMPTY",
                                        "MOTIVO": "status 403"}])

    def test_a5_a_conta_do_coletor_manda_quando_existe(self):
        """A5: o coletor conta os pedidos HTTP por host; o condutor le essa conta."""
        corridas = [{"SOURCE_ID": "S", "RUN_ID": "R1"}]
        runs = [{"RUN_ID": "R1",
                 "contadores": {"INDEX_REQUESTS": 1, "DETAIL_REQUESTS": 3, "ROBOTS_REQUESTS": 1},
                 "CORTESIA": {"PEDIDOS_POR_HOST": {"www.s.it": 5, "cdn.s.it": 1},
                              "ROBOTS": {"https://www.s.it": {"ESTADO": "LIDO"}},
                              "RECUSAS": [{"URL": "u9", "MOTIVO": "TETO_POR_HOST", "PORQUE": "x"}]}}]
        l = R.por_site(corridas, runs, [], {})["S"]
        self.assertEqual((l["ROBOTS"], l["INDICE"], l["MATERIAS"]), (1, 1, 3))
        self.assertEqual((l["TOTAL"], l["MAX_POR_HOST"]), (6, 5))
        self.assertEqual(l["RECUSAS"], [{"URL": "u9", "MOTIVO": "TETO_POR_HOST"}])
        self.assertEqual(l["ROBOTS_ESTADO"], {"https://www.s.it": "LIDO"})

    def test_teto_da_d7_e_5_por_passagem(self):
        self.assertEqual(1 + 1 + R.MAX_MATERIAS, 5)


class TestPortaoDeEgressoRepeteSoUnknown(unittest.TestCase):
    """A5: UNKNOWN (checker calado) mede-se outra vez; UNKNOWN nunca passa;
    outro pais para logo, sem repetir."""

    def _com(self, respostas):
        fila = list(respostas)
        chamadas = []
        orig = R._uma_medicao_de_egresso

        def falsa():
            pais = fila.pop(0)
            chamadas.append(pais)
            return {"GATE": "PASS" if pais == "IT" else "BLOCKED", "PAIS": pais, "IP": None, "QUANDO": "t"}
        R._uma_medicao_de_egresso = falsa
        try:
            return R.portao_de_egresso(tentativas=3, espera=0), chamadas
        finally:
            R._uma_medicao_de_egresso = orig

    def test_unknown_depois_it_passa_e_guarda_as_duas(self):
        m, ch = self._com(["UNKNOWN", "IT"])
        self.assertEqual((m["GATE"], ch), ("PASS", ["UNKNOWN", "IT"]))
        self.assertEqual([x["PAIS"] for x in m["MEDICOES"]], ["UNKNOWN", "IT"])

    def test_tres_unknown_bloqueiam(self):
        m, ch = self._com(["UNKNOWN", "UNKNOWN", "UNKNOWN", "IT"])
        self.assertEqual((m["GATE"], len(ch)), ("BLOCKED", 3))

    def test_outro_pais_para_sem_repetir(self):
        m, ch = self._com(["US", "IT"])
        self.assertEqual((m["GATE"], ch), ("BLOCKED", ["US"]))


class TestQuarentena(unittest.TestCase):

    def test_so_as_decisoes_da_corrida_em_quarentena(self):
        t = Path(tempfile.mkdtemp()) / "livro.json"
        t.write_text(json.dumps({"DECISOES": [
            {"corrida": "R1", "evidencia": {"estado": "QUARENTENA"}},
            {"corrida": "R1", "evidencia": {}},
            {"corrida": "R9", "evidencia": {"estado": "QUARENTENA"}}]}), encoding="utf-8")
        self.assertEqual(R.quarentena(t, ["R1"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
