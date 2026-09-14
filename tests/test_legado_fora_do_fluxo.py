#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A DECISAO NAO PODE PROMOVER UMA PISTA A PROVA.

Uma classificacao que aceita o nome da pasta como fonte resolve os treze num
segundo e resolve-os errado. Estes testes existem para que nenhum deles ganhe
identidade que ninguem provou.
"""
import importlib.util
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "legado_t", os.path.join(RAIZ, "provas", "o_legado_fora_do_fluxo.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)

_CACHE = {}


def _art():
    """SEMPRE recomputado, e sem rede.

    ⚠️ LER O JSON DO DISCO JA DEIXOU SEIS MUTANTES VIVOS NUMA MISSAO
    ANTERIOR (§61). O artefato e a entrega; a suite exercita o codigo.
    """
    if "a" not in _CACHE:
        _CACHE["a"] = L.medir(sondar=False)
    return _CACHE["a"]


class APistaNuncaViraProva(unittest.TestCase):

    def test_path_hint_nunca_vira_source_id_proven(self):
        for f in _art()["ITEMS"]:
            if f["PATH_HINT"]:
                self.assertIsNone(
                    f["SOURCE_ID_PROVEN"],
                    "%s ganhou fonte a partir do nome da pasta" % f["ITEM"])

    def test_a_pista_fica_marcada_como_pista(self):
        for f in _art()["ITEMS"]:
            self.assertEqual(f["PATH_HINT_CLASSE"], L.D_PISTA)
            self.assertIn("nao e SOURCE_ID provado", f["O_QUE_A_PISTA_NAO_E"])

    def test_todos_os_treze_tem_pista_e_nenhum_tem_fonte(self):
        """O caso mais perigoso: a pista existe em todos e acerta sempre."""
        itens = _art()["ITEMS"]
        self.assertEqual(len(itens), 13)
        self.assertEqual(sum(1 for f in itens if f["PATH_HINT"]), 13)
        self.assertEqual(sum(1 for f in itens if f["SOURCE_ID_PROVEN"]), 0)


class OShaNuncaViraIdentidade(unittest.TestCase):

    def test_sha_nunca_vira_document_id(self):
        for f in _art()["ITEMS"]:
            self.assertIsNone(f["DOCUMENT_ID_PROVEN"])
            self.assertNotEqual(f["DOCUMENT_ID_PROVEN"], f["SHA256"])

    def test_sha_nunca_vira_observation_id(self):
        for f in _art()["ITEMS"]:
            self.assertNotEqual(f["CANONICAL_RAW_OBSERVATION_ID"],
                                f["SHA256"])

    def test_sha_existe_como_medida_dos_bytes(self):
        """O sha nao desaparece: ele mede os bytes, que e o que ele e."""
        for f in _art()["ITEMS"]:
            if f["BODY_EXISTS"]:
                self.assertEqual(len(f["SHA256"] or ""), 64)


class ConteudoNaoEAquisicao(unittest.TestCase):

    def test_o_documento_provar_o_publicador_nao_prova_a_aquisicao(self):
        com = [f for f in _art()["ITEMS"] if f["CONTENT_PROVES_PUBLISHER"]]
        self.assertTrue(com, "nenhum documento se identifica: o teste cegou")
        for f in com:
            self.assertFalse(
                f["ACQUISITION_PROVENANCE_PROVEN"],
                "%s: o conteudo promoveu a aquisicao" % f["ITEM"])

    def test_os_cinco_campos_de_aquisicao_sao_medidos_a_parte(self):
        campos = ("ORIGINAL_ACQUISITION_EVENT_PROVEN", "ORIGINAL_RUN_PROVEN",
                  "ORIGINAL_COLLECTED_AT_PROVEN", "ORIGINAL_ACTOR_PROVEN",
                  "ORIGINAL_METHOD_PROVEN")
        for f in _art()["ITEMS"]:
            for c in campos:
                self.assertIn(c, f)
                self.assertFalse(f[c], "%s: %s virou provado" % (f["ITEM"], c))


class EquivalenciaNaoTransfereIdentidade(unittest.TestCase):

    def test_mesmos_bytes_nao_viram_a_mesma_observacao(self):
        """CONTENT_EQUIVALENCE != SAME_OBSERVATION, e com um caso forjado."""
        f = dict(_art()["ITEMS"][0], SAME_BYTES_EXIST_IN_CANONICAL_FLOW=True,
                 RECOLLECTION_POSSIBLE="NAO SEI", BODY_EXISTS=True)
        d, porque = L.dispor(f)
        self.assertEqual(d, L.EQUIVALENTE)
        self.assertIn("NAO recebe a identidade", porque)
        self.assertIn("CONTENT_EQUIVALENCE != SAME_OBSERVATION", porque)

    def test_hoje_nenhum_dos_treze_tem_equivalente(self):
        self.assertEqual(_art()["CANONICAL_EQUIVALENTS"], 0)


class ARecoletaEUmaObservacaoNOVA(unittest.TestCase):

    def test_sem_endpoint_provado_a_recoleta_fica_nao_sei(self):
        """O site responder nao torna ESTE documento buscavel."""
        f = {"ORIGINAL_URL_PROVEN": None,
             "OFFICIAL_SOURCE_STILL_AVAILABLE": "SIM"}
        self.assertEqual(L.recoleta_possivel(f), "NAO SEI",
                         "«o site esta de pe» virou «da para recolher»")

    def test_com_endpoint_provado_e_fonte_viva_a_recoleta_e_possivel(self):
        f = {"ORIGINAL_URL_PROVEN": "https://exemplo.invalido/x.pdf",
             "OFFICIAL_SOURCE_STILL_AVAILABLE": "SIM"}
        self.assertEqual(L.recoleta_possivel(f), "SIM")
        d, porque = L.dispor(dict(f, SAME_BYTES_EXIST_IN_CANONICAL_FLOW=False,
                                  RECOLLECTION_POSSIBLE="SIM",
                                  BODY_EXISTS=True))
        self.assertEqual(d, L.RECOLLECT)
        self.assertIn("corrida nova", porque)

    def test_todos_os_treze_ficam_em_nao_sei(self):
        self.assertEqual(_art()["RECOLLECTION"], {"NAO SEI": 13})


class OUnknownPermanece(unittest.TestCase):

    def test_nenhuma_disposicao_inventa_fonte(self):
        for f in _art()["ITEMS"]:
            self.assertIsNone(f["SOURCE_ID_PROVEN"])
            self.assertIsNone(f["ORIGINAL_URL_PROVEN"])

    def test_preservar_nao_e_admitir(self):
        art = _art()
        self.assertEqual(art["DISPOSITIONS"][L.LEGACY_KEEP]["QUANTOS"], 13)
        self.assertIn("PRESERVAR != ADMITIR",
                      art["ITEMS"][0]["WHY"])
        self.assertIn("Nenhuma disposicao manda apagar",
                      art["PRESERVAR_NAO_E_ADMITIR"])

    def test_corpo_ausente_fica_unresolved_e_nao_desaparece(self):
        f = {"SAME_BYTES_EXIST_IN_CANONICAL_FLOW": False,
             "RECOLLECTION_POSSIBLE": "NAO SEI", "BODY_EXISTS": False}
        d, _ = L.dispor(f)
        self.assertEqual(d, L.UNRESOLVED)


class ACoorteVemDaMedicaoAnterior(unittest.TestCase):

    def test_a_coorte_e_conferida_contra_o_numero_declarado(self):
        import copy
        real = L._json

        def falso(c):
            d = real(c)
            if c == L.MEDICAO:
                d = copy.deepcopy(d)
                d["ROOT_CAUSES"]["OUT_OF_FLOW_EVIDENCE"]["QUANTOS"] = 99
            return d
        L._json = falso
        try:
            with self.assertRaises(L.MedicaoInvalida):
                L.coorte()
        finally:
            L._json = real

    def test_o_contrato_diz_qual_pergunta_nao_tem_dono(self):
        c = _art()["CONTRATO"]
        self.assertEqual(c["EXISTING_CONTRACT_SUFFICIENT"], "PARTIAL")
        self.assertEqual(c["BIBLE_CHANGE_REQUIRED"], "NO")
        self.assertEqual(c["CONTRACT_CHANGE_REQUIRED"], "YES")
        self.assertIn("AQUISICAO", c["A_PERGUNTA_QUE_NAO_TEM_DONO_HOJE"])


class OEstudoExternoTemFontesReais(unittest.TestCase):

    def test_tres_sistemas_e_duas_familias_no_minimo(self):
        e = _art()["EXTERNAL_STUDY"]
        self.assertGreaterEqual(len(e["SISTEMAS"]), 3)
        self.assertGreaterEqual(len({s["FAMILIA"] for s in e["SISTEMAS"]}), 2)
        for s in e["SISTEMAS"]:
            self.assertTrue(s["FONTE"].startswith("http"))

    def test_a_divergencia_ficou_registada(self):
        """Um estudo que so acha convergencia nao leu o suficiente."""
        e = _art()["EXTERNAL_STUDY"]
        self.assertTrue(e["DIVERGENCIA"])
        self.assertTrue(e["CONVERGENCIA"])


if __name__ == "__main__":
    unittest.main()
