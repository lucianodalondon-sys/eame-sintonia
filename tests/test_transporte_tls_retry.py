"""T10-TLS-RETRY (01/10/2026) — a falha de TLS que passa (curl 35, schannel SEC_E_ILLEGAL_MESSAGE).

Medido pelo Scrap e pelo LAB: desde 30/09 o cluster edagricole (IT-T8-021..051, IT-T12-130/131, IT-T3-023)
cai no aperto de mao TLS; a mesma pagina, pedida a mao, da 200. A coleta tentava 2 vezes so com a pausa de
cortesia entre elas, e CADA tentativa pegava uma reserva nova no livro de 24 h — 2 reservas por pagina
falhada, numa cota que os subsites (suinicoltura., vigneviniequalita., terraevita.) dividem.

O que se exige (missao T10 + requisito do coordenador 01/10 ~19:40, PARA-T10-TLS-COTA-EDAGRICOLE.md):
  * RECUO so antes de repetir uma falha TRANSITORIA, crescente e com limite, SOMADO a pausa de cortesia;
  * a nova tentativa cabe DENTRO da mesma reserva do dominio: uma falha nao consome reserva extra; se nao
    couber no LEASE_S da reserva, nao sai;
  * o desafio (PAGINA_DE_DESAFIO) NAO e transitorio: 1 pedido, sinal no livro, recusa a seguir (controlo);
  * um erro nao transitorio (curl 60) nao leva recuo nem segunda tentativa (controlo).

Corre `provas/t10_tls_retry/transporte_tls_falso.mjs`: o `baixar()` de producao com um curl FALSO, sem rede.
"""
import json
import os
import re
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLGA = 0.05      # o relogio do Windows tem grao de ~15 ms; o setTimeout nunca dispara antes


class TestTransporteTlsRetry(unittest.TestCase):
    R = None

    @classmethod
    def setUpClass(cls):
        env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}
        env["NODE_DISABLE_COMPILE_CACHE"] = "1"
        p = subprocess.run(["node", "provas/t10_tls_retry/transporte_tls_falso.mjs"], cwd=RAIZ, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        m = re.search(r"^T10_JSON=(.*)$", p.stdout, re.M)
        if p.returncode != 0 or not m:
            raise AssertionError("a prova nao correu (rc=%s)\n%s\n%s" % (p.returncode, p.stdout[-3000:], p.stderr[-3000:]))
        cls.R = json.loads(m.group(1))
        cls.RECUO = cls.R["_RECUO"]["RECUO_TRANSITORIO"] or {"BASE_S": None, "MAXIMO_S": None}
        cls.PAUSA = cls.R["_RECUO"]["PAUSA_SITE_REAL_S"]

    def _respostas(self, caso, url_tem="/news/"):
        return [x for x in self.R[caso]["LIVRO"]["RESPOSTAS"] if url_tem in (x["URL"] or "")]

    # ── o recuo ──
    def test_A_recuo_entre_as_tentativas_depois_do_curl_35(self):
        a = self.R["A"]
        self.assertEqual(a["RESULTADO"]["status"], 200, a)
        self.assertEqual(a["CHAMADAS_FONTE"], 2, a)
        self.assertIsNotNone(self.RECUO["BASE_S"], "sem RECUO_TRANSITORIO declarado")
        self.assertGreaterEqual(self.RECUO["BASE_S"], 2)
        self.assertLessEqual(self.RECUO["MAXIMO_S"], 5)
        gap = a["INTERVALOS_FONTE_S"][0]
        self.assertGreaterEqual(gap, self.RECUO["BASE_S"] - FOLGA, "a 2.a tentativa saiu sem recuo: %s s" % gap)
        self.assertLess(gap, self.RECUO["MAXIMO_S"] + 0.5, gap)

    def test_A_REAL_o_recuo_soma_se_a_pausa_de_cortesia(self):
        a = self.R["A_REAL"]
        self.assertEqual(a["CHAMADAS_FONTE"], 2, a)
        gap = a["INTERVALOS_FONTE_S"][0]
        self.assertIsNotNone(self.RECUO["BASE_S"], "sem RECUO_TRANSITORIO declarado")
        self.assertGreaterEqual(gap, self.PAUSA + self.RECUO["BASE_S"] - FOLGA,
                                "com a politica real o intervalo foi so a pausa de cortesia: %s s" % gap)
        self.assertLess(gap, self.PAUSA + self.RECUO["MAXIMO_S"] + 1, gap)

    def test_E_recuo_crescente_e_com_limite(self):
        e = self.R["E"]
        self.assertIsNotNone(self.RECUO["BASE_S"], "sem RECUO_TRANSITORIO declarado")
        self.assertEqual(e["CHAMADAS_FONTE"], 3, e)
        g1, g2 = e["INTERVALOS_FONTE_S"]
        self.assertGreaterEqual(g1, self.RECUO["BASE_S"] - FOLGA, e)
        self.assertLess(g1, self.RECUO["BASE_S"] + 0.5, e)
        self.assertGreater(g2, g1, "o recuo nao cresce: %s" % e["INTERVALOS_FONTE_S"])
        self.assertGreaterEqual(g2, self.RECUO["MAXIMO_S"] - FOLGA, e)
        self.assertLess(g2, self.RECUO["MAXIMO_S"] + 0.5, "o recuo passou do limite: %s" % g2)
        # 3 tentativas, 1 so reserva: no teto da corrida contam robots + 1
        self.assertEqual(e["CORTESIA"]["PEDIDOS_POR_HOST"], {"caso-e.test": 2}, e["CORTESIA"])

    def test_F_recuo_e_mesma_reserva_tambem_no_robots(self):
        f = self.R["F"]
        self.assertIsNotNone(self.RECUO["BASE_S"], "sem RECUO_TRANSITORIO declarado")
        self.assertEqual(f["CHAMADAS_ROBOTS"], 2, f)
        self.assertGreaterEqual(f["INTERVALOS_ROBOTS_S"][0], self.RECUO["BASE_S"] - FOLGA, f)
        self.assertEqual(f["RESULTADO"]["status"], 200, f)
        self.assertEqual(f["LIVRO"]["RESERVAS"], 2, "robots (2 tentativas) + materia = 2 reservas: %s" % f["LIVRO"])

    # ── a cota: uma falha nao consome reserva extra ──
    def test_A_a_retentativa_nao_conta_no_teto_da_corrida(self):
        self.assertEqual(self.R["A"]["CORTESIA"]["PEDIDOS_POR_HOST"], {"suinicoltura.caso-a.test": 2},
                         self.R["A"]["CORTESIA"])

    def test_B_falha_e_sucesso_cabem_numa_so_reserva(self):
        b = self.R["B"]
        self.assertEqual(b["RESULTADO"]["status"], 200, b)
        self.assertEqual(b["CHAMADAS_FONTE"], 2, b)
        self.assertEqual(b["LIVRO"]["RESERVAS"], 2, "robots + 1 materia; a falha pegou reserva extra: %s" % b["LIVRO"])
        r = self._respostas("B")
        self.assertEqual([x["STATUS"] for x in r], [200], "a reserva fecha UMA vez, com o que a pagina deu: %s" % r)
        self.assertIsNone(b["LIVRO"]["EM_CURSO_ATE"], "a reserva ficou aberta")

    def test_B2_duas_falhas_uma_reserva_e_a_resposta_status_0(self):
        b = self.R["B2"]
        self.assertEqual(b["CHAMADAS_FONTE"], 2, b)
        self.assertEqual(b["RESULTADO"]["codigo"], 35, b)
        self.assertTrue(b["RESULTADO"]["retry_permitido"], b)
        self.assertEqual(b["LIVRO"]["RESERVAS"], 2, b["LIVRO"])
        self.assertEqual(self._respostas("B2"), [{"URL": "https://suinicoltura.caso-b2.test/news/articolo/",
                                                  "STATUS": 0, "BYTES": None, "SINAIS": []}])
        # a falha de transporte nao e SINAL (D124): nao corta o orcamento do dominio
        self.assertEqual(b["LIVRO"]["ORCAMENTO_24H"], 40, b["LIVRO"])
        self.assertIsNone(b["LIVRO"]["EM_CURSO_ATE"], "a reserva ficou aberta")

    def test_B3_subsites_do_mesmo_dominio_dividem_a_cota(self):
        b = self.R["B3"]
        self.assertEqual(b["RESULTADO"]["status"], 200, b)
        self.assertEqual(b["RESULTADO_SUBSITE_2"]["status"], 200, b)
        self.assertEqual(b["CHAMADAS_FONTE"] + b["CHAMADAS_SUBSITE_2"], 4, b)
        self.assertEqual(b["LIVRO"]["GASTO_24H"], 4, "2 robots + 2 materias, as 2 falhas sem reserva: %s" % b["LIVRO"])

    def test_G_a_retentativa_que_nao_cabe_na_reserva_nao_sai(self):
        g = self.R["G"]
        self.assertEqual(g["CHAMADAS_FONTE"], 1, g)
        self.assertEqual(g["RESULTADO"]["codigo"], 35, g)
        self.assertEqual(g["LIVRO"]["RESERVAS"], 2, g["LIVRO"])
        self.assertEqual([x["STATUS"] for x in self._respostas("G")], [0], g["LIVRO"])
        self.assertIsNone(g["LIVRO"]["EM_CURSO_ATE"], "a reserva ficou aberta")

    # ── os controlos ──
    def test_C_desafio_nao_e_transitorio_e_continua_recusa(self):
        c = self.R["C"]
        self.assertEqual(c["CHAMADAS_FONTE"], 1, c)
        self.assertEqual(c["RESULTADO"]["tentativas"], 1, c)
        self.assertLess(c["SEGUNDOS"], 2, "o desafio esperou um recuo: %s" % c)
        self.assertIsNotNone(c["RESULTADO_A_SEGUIR"]["recusado"], c)
        self.assertEqual(c["CHAMADAS_A_SEGUIR"], 0, c)

    def test_C_LIVRO_desafio_e_sinal_no_livro(self):
        c = self.R["C_LIVRO"]
        self.assertEqual(c["CHAMADAS_FONTE"], 1, c)
        self.assertEqual([x["SINAIS"] for x in self._respostas("C_LIVRO")], [["PAGINA_DE_DESAFIO"]], c["LIVRO"])
        self.assertEqual(c["LIVRO"]["ORCAMENTO_24H"], 20, c["LIVRO"])

    def test_D_erro_nao_transitorio_sem_recuo_nem_segunda_tentativa(self):
        d = self.R["D"]
        self.assertEqual(d["CHAMADAS_FONTE"], 1, d)
        self.assertEqual(d["RESULTADO"]["codigo"], 60, d)
        self.assertFalse(d["RESULTADO"]["retry_permitido"], d)
        self.assertLess(d["ROBOTS_ATE_FONTE_S"], 1, "recuo antes da 1.a tentativa: %s" % d)


if __name__ == "__main__":
    unittest.main(verbosity=2)
