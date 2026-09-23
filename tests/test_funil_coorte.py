"""O funil G0 com dados sinteticos cujo resultado se sabe a partida.

Sem rede, sem git, sem servico vivo: `avaliar` recebe o dicionario D ja
montado. Cada caso diz o que a regra manda, nao o que o codigo faz.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "coorte_micro"))
_s = importlib.util.spec_from_file_location("funil", RAIZ / "scripts" / "coorte_micro" / "funil.py")
FU = importlib.util.module_from_spec(_s)
_s.loader.exec_module(FU)

PAD = r"^https?://(www\.)?ex\.it/news/[a-z0-9-]+/?$"


def contrato(padrao=PAD):
    return {"ACQUISITION": {"INDEX_URL": "https://www.ex.it/news/", "LINK_PATTERN": padrao}}


def D(**kw):
    base = dict(ultimo={}, curador={}, onboarded={}, m3={}, linha={}, dec3b={}, rot={}, paginas=[])
    base.update(kw)
    return base


def mat(sid, url="https://www.ex.it/news/um-titulo-qualquer"):
    return {"SOURCE_ID": sid, "URL": url, "VEREDITO": "MATERIA", "PAPEL": "MATERIA"}


PRONTA = {"NEW_STATE": "READY_FOR_COLLECTION"}
REL = {"SINTONIA_RELEVANT": "YES", "PORQUE": "x"}


class TestDegraus(unittest.TestCase):

    def completa(self, sid="IT-T10-900", **kw):
        d = D(ultimo={sid: PRONTA}, onboarded={sid: contrato()}, paginas=[mat(sid)], rot={sid: REL})
        d.update(kw)
        return FU.avaliar(sid, d)

    def test_fonte_completa_passa(self):
        self.assertEqual(self.completa()["PARA_EM"], "PASSA")

    def test_so_ready_legacy_nao_passa_A(self):
        sid = "IT-T10-900"
        r = FU.avaliar(sid, D(linha={sid: {"READY_RULE": "LEGACY", "MOTIVO": "READY_LEGACY"}}))
        self.assertFalse(r["A"])

    def test_regua_dos_4_passos_nesta_linha_passa_A(self):
        sid = "IT-T10-900"
        r = FU.avaliar(sid, D(linha={sid: {"READY_RULE": "DETAIL/v1", "MOTIVO": "ELIGIBLE"}}))
        self.assertTrue(r["A"])

    def test_fora_da_tabela_do_coletor_e_needs_contract_e_diz_se_a_m3_provou(self):
        sid = "IT-T10-900"
        r = FU.avaliar(sid, D(ultimo={sid: PRONTA}, m3={sid: "ROUTE_PROVEN"}))
        self.assertFalse(r["B"])
        self.assertIn("NEEDS_CONTRACT", r["B_PORQUE"])
        self.assertIn("M3", r["B_PORQUE"])

    def test_universo_sem_receita_web_e_missing_route(self):
        sid = "IT-T12-900"                       # T12 nao tem receita web nesta linha
        r = FU.avaliar(sid, D(ultimo={sid: PRONTA}, onboarded={sid: contrato()}))
        self.assertFalse(r["B"])
        self.assertIn("MISSING_ROUTE", r["B_PORQUE"])

    def test_bloqueio_vivo_e_block_reason(self):
        sid = "IT-T10-900"
        r = FU.avaliar(sid, D(ultimo={sid: {"NEW_STATE": "POLICY_BLOCK"}}, onboarded={sid: contrato()}))
        self.assertEqual(r["B_PORQUE"], "POLICY_BLOCK")

    def test_sem_materia_lida_C_nunca_passa(self):
        r = self.completa(paginas=[])
        self.assertFalse(r["C"])
        self.assertIn("UNKNOWN", r["C_PORQUE"])

    def test_receita_que_nao_casa_a_materia_falha_C(self):
        sid = "IT-T10-900"
        r = self.completa(onboarded={sid: contrato(r"^https?://ex\.it/outra/.*$")})
        self.assertFalse(r["C"])

    def test_decisao_do_dono_passa_a_frente_da_3b(self):
        sid = "IT-T10-900"
        r = self.completa(dec3b={sid: "FICA_FORA"})
        self.assertTrue(r["D"])                  # rot (dono/leitura) vence a 3b

    def test_3b_fica_fora_sem_rotulo_nao_passa_D(self):
        sid = "IT-T10-900"
        r = self.completa(rot={}, dec3b={sid: "FICA_FORA"})
        self.assertFalse(r["D"])

    def test_relevancia_nao_medida_nao_passa_D(self):
        self.assertFalse(self.completa(rot={})["D"])

    def test_marca_fica_fora_em_E(self):
        sid = "IT-T7-033"
        r = FU.avaliar(sid, D(ultimo={sid: PRONTA}, onboarded={sid: contrato()},
                              paginas=[mat(sid)], rot={sid: REL}))
        self.assertFalse(r["E"])
        self.assertEqual(r["PARA_EM"], "E")


class TestDesbloqueiosNaoBaixamARegua(unittest.TestCase):

    def test_nao_ready_nunca_passa_por_desbloqueio(self):
        sid = "IT-T10-900"
        d = D(onboarded={sid: contrato()}, paginas=[mat(sid)], rot={sid: REL})
        l = FU.avaliar(sid, d)
        self.assertFalse(l["A"])
        for o in FU.desbloqueios([l], d):
            self.assertNotIn(sid, o["FONTES"])
            self.assertNotIn(sid, o["ACUMULADO_FONTES"])


if __name__ == "__main__":
    unittest.main()
