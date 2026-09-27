"""ONDA2-G3 — o disparador da onda web: coorte oficial conferida e teto por dominio na onda (D38).

Sem rede e sem Sala. O transporte (node) so e chamado para o dominio registavel.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
import onda_web as O  # noqa: E402


def _linhas(doms_e_prev):
    return [{"SOURCE_ID": "F%d" % i, "DOMINIO": d, "PEDIDOS_PREVISTOS": p} for i, (d, p) in enumerate(doms_e_prev)]


class ARepartição(unittest.TestCase):

    def test_1_cinco_fontes_do_mesmo_dominio_gastam_no_maximo_5(self):
        l = O.repartir(_linhas([("cia.it", 3)] * 5))
        self.assertEqual(sum(x["PEDIDOS_NA_ONDA"] for x in l), 5)
        self.assertEqual([x["PEDIDOS_NA_ONDA"] for x in l], [3, 2, 0, 0, 0])
        self.assertEqual([x["PORQUE"] for x in l], [None, "TETO_DOMINIO_PARCIAL", "TETO_DOMINIO", "TETO_DOMINIO", "TETO_DOMINIO"])

    def test_2_dominios_diferentes_nao_interferem(self):
        l = O.repartir(_linhas([("cia.it", 5), ("myfruit.it", 5), ("cia.it", 3), ("istat.it", 3)]))
        self.assertEqual([x["PEDIDOS_NA_ONDA"] for x in l], [5, 5, 0, 3])
        self.assertEqual(l[1]["PORQUE"], None)

    def test_3_o_dominio_vem_do_transporte_e_junta_subdominios(self):
        d = O.dominios(["www.cia.it", "sub.cia.it", "cia.it", "caf-cia.it", "www.arpa.marche.it"])
        self.assertEqual({d["www.cia.it"], d["sub.cia.it"], d["cia.it"]}, {"cia.it"})
        self.assertEqual(d["caf-cia.it"], "caf-cia.it")
        self.assertEqual(d["www.arpa.marche.it"], "arpa.marche.it")


class ACoorteOficial(unittest.TestCase):
    """Um repositorio git descartavel com uma coorte commitada."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="onda-web-"))
        g = lambda *a: subprocess.run(["git", "-C", str(self.tmp), *a], capture_output=True, check=True)  # noqa: E731
        g("init", "-q")
        g("config", "user.email", "t@t")
        g("config", "user.name", "t")
        g("config", "core.autocrlf", "false")
        self.rel = "ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json"
        f = self.tmp / self.rel
        f.parent.mkdir(parents=True)
        f.write_text(json.dumps({"ESTADO": "PROVISORIA", "COORTE": [{"SOURCE_ID": "IT-T7-112",
                                                                       "INDEX_URL": "https://www.cia.it/"}]}), encoding="utf-8")
        g("add", "-A")
        g("commit", "-qm", "c")
        self.g = g
        self.antes = O.RAIZ
        O.RAIZ = self.tmp

    def tearDown(self):
        O.RAIZ = self.antes
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_4_provisoria_nao_corre(self):
        with self.assertRaises(SystemExit) as e:
            O.coorte_oficial(self.rel, exigir_congelada=True, sha_declarado=None)
        self.assertIn("COORTE_NAO_CONGELADA", str(e.exception))
        # o --so-plano le a provisoria e diz que nao pode correr
        self.assertEqual(O.coorte_oficial(self.rel, exigir_congelada=False, sha_declarado=None)["COORTE"]["ESTADO"],
                         "PROVISORIA")

    def test_5_impressao_digital_errada_nao_corre(self):
        with self.assertRaises(SystemExit) as e:
            O.coorte_oficial(self.rel, exigir_congelada=False, sha_declarado="0" * 64)
        self.assertIn("COORTE_SHA256_DIFERENTE", str(e.exception))

    def test_6_congelada_e_sha_certo_corre(self):
        f = self.tmp / self.rel
        d = json.loads(f.read_text(encoding="utf-8"))
        d["ESTADO"] = "CONGELADA"
        f.write_text(json.dumps(d), encoding="utf-8")
        self.g("commit", "-qam", "congela")
        sha = O.sha256(subprocess.run(["git", "-C", str(self.tmp), "show", "HEAD:" + self.rel],
                                      capture_output=True).stdout)
        r = O.coorte_oficial(self.rel, exigir_congelada=True, sha_declarado=sha)
        self.assertEqual(r["SHA256_DO_COMMIT"], sha)

    def test_7_coorte_mexida_fora_do_commit_nao_corre(self):
        f = self.tmp / self.rel
        d = json.loads(f.read_text(encoding="utf-8"))
        d["COORTE"].append({"SOURCE_ID": "IT-T7-999", "INDEX_URL": "https://x.it/"})
        f.write_text(json.dumps(d), encoding="utf-8")
        with self.assertRaises(SystemExit) as e:
            O.coorte_oficial(self.rel, exigir_congelada=False, sha_declarado=None)
        self.assertIn("COORTE_ALTERADA_FORA_DO_COMMIT", str(e.exception))


class AsDecisoesDoTetoNaOnda(unittest.TestCase):

    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="onda-teto-"))
        self.livro = self.d / "TETO-ONDA.json"

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_10_fonte_de_dominio_esgotado_salta_com_TETO_DOMINIO(self):
        self.assertIsNone(O.antes_da_fonte(self.livro, "cia.it"))           # sem livro: corre
        self.livro.write_text('{"PEDIDOS_POR_DOMINIO": {"cia.it": 4, "istat.it": 5}}', encoding="utf-8")
        self.assertIsNone(O.antes_da_fonte(self.livro, "cia.it"))           # 4 < 5: corre (o transporte corta)
        self.assertEqual(O.antes_da_fonte(self.livro, "istat.it"), "TETO_DOMINIO")
        self.assertIsNone(O.antes_da_fonte(self.livro, "myfruit.it"))       # outro dominio: corre

    def test_11_disjuntor_so_dispara_acima_do_teto(self):
        self.assertIsNone(O.disjuntor_de_dominio({"cia.it": 5, "istat.it": 3}))
        self.assertIn("cia.it", O.disjuntor_de_dominio({"cia.it": 6}))

    def test_12_livro_ilegivel_rebenta_em_vez_de_valer_zero(self):
        self.livro.write_text("{ nao e json", encoding="utf-8")
        with self.assertRaises(ValueError):
            O.antes_da_fonte(self.livro, "cia.it")


CIA = ["IT-T7-112", "IT-T7-118", "IT-T7-121", "IT-T7-123", "IT-T7-135"]


def _coorte():
    """A ordem da 1.a onda: myfruit, depois as 5 do cia.it, depois istat."""
    return [("IT-T10-018", "u")] + [(s, "u") for s in CIA] + [("IT-T5-090", "u")]


def _dom():
    d = {s: "cia.it" for s in CIA}
    d.update({"IT-T10-018": "myfruit.it", "IT-T5-090": "istat.it"})
    return d


def _onda(servidas, quando):
    """Um ONDA-WEB-ESTADO minimo: as fontes servidas fizeram 1 pedido; RUN_ID com o instante."""
    return {"FONTES": [{"SOURCE_ID": s, "CORREU": True, "PEDIDOS_POR_DOMINIO": {"x": 1},
                        "RUN_ID": "IT-T7-%s-000000000000" % quando} for s in servidas]}


class AOrdemDentroDoDominio(unittest.TestCase):

    def test_13_quem_foi_atendido_ha_mais_tempo_vai_primeiro(self):
        h = [_onda(["IT-T7-112"], "2026-09-24-120000"), _onda(["IT-T7-118"], "2026-09-24-130000"),
             _onda(["IT-T7-121", "IT-T7-123", "IT-T7-135"], "2026-09-25-080000")]
        o = O.ordenar_por_dominio(_coorte(), _dom(), O.ultima_vez_atendida(h))
        self.assertEqual([s for s, _ in o if s in CIA], ["IT-T7-112", "IT-T7-118", "IT-T7-121", "IT-T7-123", "IT-T7-135"])
        h.append(_onda(["IT-T7-112"], "2026-09-26-080000"))            # o 112 foi atendido agora: vai para o fim
        o = O.ordenar_por_dominio(_coorte(), _dom(), O.ultima_vez_atendida(h))
        self.assertEqual([s for s, _ in o if s in CIA][0], "IT-T7-118")
        self.assertEqual([s for s, _ in o if s in CIA][-1], "IT-T7-112")

    def test_14_nunca_atendida_vai_antes_de_todas_e_o_empate_e_pelo_SOURCE_ID(self):
        h = [_onda(["IT-T7-112", "IT-T7-118"], "2026-09-24-120000")]
        o = [s for s, _ in O.ordenar_por_dominio(_coorte(), _dom(), O.ultima_vez_atendida(h)) if s in CIA]
        self.assertEqual(o, ["IT-T7-121", "IT-T7-123", "IT-T7-135", "IT-T7-112", "IT-T7-118"])

    def test_15_outros_dominios_nao_mudam_de_lugar_e_a_ordem_e_deterministica(self):
        h = [_onda(["IT-T7-112"], "2026-09-24-120000")]
        a = O.ordenar_por_dominio(_coorte(), _dom(), O.ultima_vez_atendida(h))
        b = O.ordenar_por_dominio(list(reversed(_coorte()))[::-1], _dom(), O.ultima_vez_atendida(h))
        self.assertEqual(a, b)
        self.assertEqual(a[0][0], "IT-T10-018")
        self.assertEqual(a[-1][0], "IT-T5-090")

    def test_16_em_tres_ondas_as_cinco_do_cia_it_sao_atendidas(self):
        """Com o teto de 5 e ~3 pedidos por fonte, cabem 1 inteira + 1 parcial por onda.
        A rotacao tem de chegar as 5 em 3 ondas; sem ela, 3 das 5 nunca seriam atendidas."""
        h, atendidas = [], set()
        for n, quando in enumerate(["2026-09-26-080000", "2026-09-27-080000", "2026-09-28-080000"]):
            ordem = O.ordenar_por_dominio(_coorte(), _dom(), O.ultima_vez_atendida(h))
            l = O.repartir([{"SOURCE_ID": s, "DOMINIO": _dom()[s], "PEDIDOS_PREVISTOS": 3} for s, _ in ordem])
            servidas = [x["SOURCE_ID"] for x in l if x["PEDIDOS_NA_ONDA"] > 0 and x["SOURCE_ID"] in CIA]
            self.assertEqual(len(servidas), 2, servidas)
            atendidas |= set(servidas)
            h.append(_onda(servidas, quando))
        self.assertEqual(atendidas, set(CIA))

    def test_17_o_instante_vem_do_RUN_ID_e_so_conta_quem_fez_pedido(self):
        self.assertEqual(O.quando_do_run("IT-T7-2026-09-24-120737-b9d168ef521cb4d9"), "2026-09-24T12:07:37")
        e = {"FONTES": [{"SOURCE_ID": "A", "CORREU": True, "PEDIDOS_POR_SITE": {"x": 0},
                         "RUN_ID": "IT-T7-2026-09-24-120737-ab"},
                        {"SOURCE_ID": "B", "CORREU": False, "PORQUE_NAO_CORREU": "TETO_DOMINIO"}]}
        self.assertEqual(O.ultima_vez_atendida([e]), {})


class OCorrerRecusa(unittest.TestCase):

    def test_8_correr_sem_sha_ou_sem_saida_recusa(self):
        with self.assertRaises(SystemExit):
            O.main(["--correr", "--saida=%s" % tempfile.gettempdir()])
        with self.assertRaises(SystemExit):
            O.main(["--correr", "--sha256=abc"])

    def test_9_livro_de_outra_onda_nao_se_reaproveita(self):
        d = Path(tempfile.mkdtemp(prefix="onda-livro-"))
        try:
            (d / "TETO-ONDA.json").write_text('{"PEDIDOS_POR_DOMINIO": {}}', encoding="utf-8")
            with self.assertRaises(SystemExit) as e:
                O.main(["--correr", "--sha256=abc", "--saida=%s" % d])
            self.assertIn("LIVRO_DA_ONDA_JA_EXISTE", str(e.exception))
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
