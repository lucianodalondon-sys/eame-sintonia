# -*- coding: utf-8 -*-
"""B2 — o caminho da PROMOTION e da DEMOTION pela ponte (2026-09-23).

Tres pecas, cada uma com o seu positivo e o seu negativo:
  importar_contratos_do_bot   o contrato que so o bot tem atravessa; nunca sobrepoe
  importar_provas_do_bot      a prova que ficou para tras e recuperada
  dono_do_contrato            o portao nao tem elegivel o que o bot nao mede

Tudo em pasta temporaria: nenhum ficheiro real do repositorio e escrito.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "medidas"))
import lifecycle as LC           # noqa: E402
import ready_split as RS         # noqa: E402
import reconciliar_livros as R   # noqa: E402

FOTO = Path.home() / "sintonia-gabarito" / "B1-SNAPSHOT-20260923T051430Z"


def _c(sid, index):
    return {"SOURCE_ID": sid, "OUTPUT_TYPE": "HTML",
            "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL",
                            "INDEX_URL": index, "LINK_PATTERN": "^x$", "MAX_TARGETS": 1}}


class Isolado(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, R.EVIDENCIA_A, R.CONTRATOS_A, RS.EVIDENCIA, RS.CONTRATOS)
        self.addCleanup(self._repor)
        LC.LIVRO = d / "LEDGER.json"
        R.EVIDENCIA_A = RS.EVIDENCIA = d / "EVIDENCE.json"
        R.CONTRATOS_A = RS.CONTRATOS = d / "CONTRATOS.json"
        self.livro([])
        R.EVIDENCIA_A.write_text(json.dumps({"PROVAS": []}), encoding="utf-8")
        R.CONTRATOS_A.write_text(json.dumps({"FONTES": []}), encoding="utf-8")

    def _repor(self):
        LC.LIVRO, R.EVIDENCIA_A, R.CONTRATOS_A, RS.EVIDENCIA, RS.CONTRATOS = self._antes

    def livro(self, transicoes):
        LC.LIVRO.write_text(json.dumps({"TRANSICOES": transicoes}), encoding="utf-8")

    def contratos_a(self):
        return {c["SOURCE_ID"]: c for c in json.loads(R.CONTRATOS_A.read_text(encoding="utf-8"))["FONTES"]}


class Contratos(Isolado):
    def test_o_contrato_que_so_o_bot_tem_atravessa(self):
        self.livro([{"SOURCE_ID": "IT-T7-001", "NEW_STATE": "READY_FOR_COLLECTION"}])
        r = R.importar_contratos_do_bot({"CONTRATOS_C": {"IT-T7-001": _c("IT-T7-001", "https://a.it/news/")},
                                         "COMMITS": {"C": "disco:x"}})
        self.assertEqual(1, r["CONTRATOS_IMPORTADOS"])
        self.assertEqual("C", self.contratos_a()["IT-T7-001"]["IMPORTADO_DE"]["LIVRO"])

    def test_nunca_sobrepoe_e_a_colisao_fica_dita(self):
        self.livro([{"SOURCE_ID": "IT-T7-001", "NEW_STATE": "READY_FOR_COLLECTION"}])
        R.CONTRATOS_A.write_text(json.dumps({"FONTES": [_c("IT-T7-001", "https://a.it/news/")]}), encoding="utf-8")
        r = R.importar_contratos_do_bot({"CONTRATOS_C": {"IT-T7-001": _c("IT-T7-001", "https://a.it/")},
                                         "COMMITS": {"C": "disco:x"}})
        self.assertEqual(0, r["CONTRATOS_IMPORTADOS"])
        self.assertEqual(["IT-T7-001"], [c["SOURCE_ID"] for c in r["COLISOES_DE_DONO"]])
        self.assertEqual("https://a.it/news/", self.contratos_a()["IT-T7-001"]["ACQUISITION"]["INDEX_URL"])

    def test_contrato_igual_nao_duplica(self):
        self.livro([{"SOURCE_ID": "IT-T7-001", "NEW_STATE": "READY_FOR_COLLECTION"}])
        R.CONTRATOS_A.write_text(json.dumps({"FONTES": [_c("IT-T7-001", "https://a.it/news/")]}), encoding="utf-8")
        r = R.importar_contratos_do_bot({"CONTRATOS_C": {"IT-T7-001": _c("IT-T7-001", "https://a.it/news/")},
                                         "COMMITS": {"C": "disco:x"}})
        self.assertEqual((0, 1), (r["CONTRATOS_IMPORTADOS"], r["CONTRATOS_JA_IGUAIS"]))
        self.assertEqual(1, len(self.contratos_a()))

    def test_a_ponte_nao_semeia_fontes_que_o_livro_nao_conhece(self):
        r = R.importar_contratos_do_bot({"CONTRATOS_C": {"IT-T7-999": _c("IT-T7-999", "https://z.it/")},
                                         "COMMITS": {"C": "disco:x"}})
        self.assertEqual(0, r["CONTRATOS_IMPORTADOS"])


class ProvasParaTras(Isolado):
    def test_prova_citada_pelo_livro_e_ausente_aqui_e_recuperada_uma_vez(self):
        ref = "RECONCILIACAO-V1:livro_C_(bot)@disco:abc:EV-IT-T7-001-CANARY-1"
        self.livro([{"SOURCE_ID": "IT-T7-001", "NEW_STATE": "READY_FOR_COLLECTION", "EVIDENCE_REF": ref}])
        ctx = {"EVIDENCIA_C": {"EV-IT-T7-001-CANARY-1": {"EVIDENCE_REF": "EV-IT-T7-001-CANARY-1",
                                                        "SOURCE_ID": "IT-T7-001", "DADOS": {}}},
               "COMMITS": {"C": "disco:abc"}}
        r1 = R.importar_provas_do_bot([], ctx)       # plano vazio: a fonte ja nao muda de estado
        r2 = R.importar_provas_do_bot([], ctx)
        self.assertEqual((1, 0), (r1["PROVAS_IMPORTADAS"], r2["PROVAS_IMPORTADAS"]))
        provas = json.loads(R.EVIDENCIA_A.read_text(encoding="utf-8"))["PROVAS"]
        self.assertEqual([ref], [p["EVIDENCE_REF"] for p in provas])


class Dono(unittest.TestCase):
    CTX = {"CONTRATOS_A": {"IT-T7-001": _c("IT-T7-001", "https://a.it/news/"),
                           "IT-T7-002": _c("IT-T7-002", "https://b.it/news/"),
                           "IT-T7-003": _c("IT-T7-003", "https://c.it/news/")},
           "CONTRATOS_C": {"IT-T7-001": _c("IT-T7-001", "https://a.it/news/"),
                           "IT-T7-002": _c("IT-T7-002", "https://b.it/"),
                           "IT-T7-004": _c("IT-T7-004", "https://d.it/news/")}}

    def test_mesmo_contrato_tem_dono(self):
        self.assertIsNone(R.dono_do_contrato("IT-T7-001", self.CTX))

    def test_bot_sem_contrato_nao_mede(self):
        self.assertIn("nao tem contrato", R.dono_do_contrato("IT-T7-003", self.CTX))

    def test_bot_com_outra_rota_sao_dois_donos(self):
        self.assertIn("dois donos", R.dono_do_contrato("IT-T7-002", self.CTX))

    def test_contrato_so_no_bot_atravessa_e_nao_e_falta_de_dono(self):
        self.assertIsNone(R.dono_do_contrato("IT-T7-004", self.CTX))

    def test_livro_do_bot_ilegivel_nao_despromove_nada(self):
        self.assertIsNone(R.dono_do_contrato("IT-T7-003", dict(self.CTX, CONTRATOS_C={})))


@unittest.skipUnless(FOTO.is_dir(), "fotografia B1 fora do Git e ausente nesta maquina: %s" % FOTO)
class PontaAPontaNaFotografia(unittest.TestCase):
    """Uma volta REAL da ponte sobre copias dos livros vivos (medidas/prova_b2_ponte_em_copia.py)."""

    @classmethod
    def setUpClass(cls):
        import prova_b2_ponte_em_copia as P
        guard = (LC.LIVRO, R.EVIDENCIA_A, R.CONTRATOS_A, RS.EVIDENCIA, RS.CONTRATOS, R.SAIDA,
                 P.PA.ESTADO, P.PA.DIARIO)
        try:
            cls.out = P.correr(FOTO)
        finally:
            (LC.LIVRO, R.EVIDENCIA_A, R.CONTRATOS_A, RS.EVIDENCIA, RS.CONTRATOS, R.SAIDA,
             P.PA.ESTADO, P.PA.DIARIO) = guard

    def test_promotion_uma_fonte_do_bot_entra_no_portao(self):
        self.assertIn("IT-T8-030", self.out["ENTRARAM"])

    def test_demotion_a_fonte_que_o_bot_nao_mede_sai_do_portao(self):
        self.assertIn("IT-T5-041", self.out["SAIRAM"])

    def test_os_ficheiros_reais_ficam_intocados(self):
        self.assertTrue(self.out["FICHEIROS_REAIS_INTOCADOS"])


if __name__ == "__main__":
    unittest.main()
