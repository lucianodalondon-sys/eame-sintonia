#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROVA DE DIAGNOSTICO NAO PODE INVENTAR A FONTE QUE ANDA A PROCURAR.

Uma sonda que aceita qualquer coisa como `SOURCE_ID` mede zero buracos e
parece uma boa noticia. Estes testes existem para que o numero so possa
descer por o valor existir mesmo.
"""
import importlib.util
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
from coleta import ingresso as ing  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "wiring_t", os.path.join(RAIZ, "provas", "medir_source_id_wiring_gap.py"))
W = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(W)


class NadaViraSourceId(unittest.TestCase):
    """O que NAO e fonte continua a nao ser fonte, por mais util que pareca."""

    def test_sentinela_nao_conta_como_fonte(self):
        for s in ing.NAO_E_AFIRMACAO + ("NÃO SEI",):
            self.assertFalse(W.prova_de_fonte(s),
                             "%r foi aceite como fonte provada" % (s,))

    def test_uma_string_verdadeira_nao_e_uma_fonte(self):
        """`'NAO SEI'` e truthy. Um `if valor:` daria 36 fontes onde ha 20."""
        self.assertTrue(bool("NAO SEI"))
        self.assertFalse(W.prova_de_fonte("NAO SEI"))

    def test_publisher_nao_vira_fonte(self):
        """AGEA publica, e publicar nao e ser a fonte catalogada."""
        fonte = self._fonte_da_prova()
        self.assertNotIn("PUBLISHER", fonte.split("def prova_de_fonte")[1]
                         .split("def fonte_no_caminho")[0])

    def test_url_e_sha_nao_viram_fonte(self):
        self.assertIsNone(W.fonte_no_caminho(
            "https://www.terretruria.it/monitoraggio"))
        self.assertIsNone(W.fonte_no_caminho(
            "0be2d204c98ad1b169252eaee2860e84555d1ddf1ed254ec1dc7eae37befaffc"))

    def test_o_caminho_e_sugestao_e_a_prova_sabe_disso(self):
        """`fonte_no_caminho` existe, e o artefato nunca a promove a prova.

            UMA CONVENCAO DE CAMINHO NAO E UM CAMPO.
        """
        self.assertEqual(
            W.fonte_no_caminho("data/samples/IT-SOURCE-SAMPLES/IT-T3-008/x.pdf"),
            "IT-T3-008")
        art = _artefato()
        so_caminho = [t for t in art["ITEMS"]
                      if t["PRIMEIRA_PROVA_ONDE"] is None]
        self.assertTrue(so_caminho, "o caso mais importante desapareceu")
        for t in so_caminho:
            self.assertEqual(t["ROOT_CAUSE"], W.OUT_OF_FLOW_EVIDENCE)
            self.assertIsNone(t["PRIMEIRA_PROVA_VALOR"],
                              "o caminho foi promovido a prova")

    @staticmethod
    def _fonte_da_prova():
        with open(os.path.join(RAIZ, "provas",
                               "medir_source_id_wiring_gap.py"),
                  encoding="utf-8") as f:
            return f.read()


class AAusenciaEReportadaENaoPreenchida(unittest.TestCase):

    def test_sem_prova_a_montante_fica_unknown(self):
        t = {"O_CAMINHO_SUGERE": None, "PARENT_STORAGE_LOCATION": "x/y.pdf"}
        causa, _ = W.classificar(t, None, "NUNCA_HOUVE_PROVA_NA_CADEIA")
        self.assertEqual(causa, W.NEVER_WRITTEN)

    def test_um_edge_ausente_e_reportado_e_nao_tapado(self):
        art = _artefato()
        for t in art["ITEMS"]:
            if t["FIRST_LOST_EDGE"] == "UNKNOWN":
                self.assertIn(t["ROOT_CAUSE"],
                              (W.OUT_OF_FLOW_EVIDENCE, W.NEVER_WRITTEN))
                self.assertTrue(t["ROOT_CAUSE_PORQUE"],
                                "um UNKNOWN sem explicacao e um buraco tapado")

    def test_nenhum_item_recebe_fonte_que_nao_veio_de_campo(self):
        art = _artefato()
        for t in art["ITEMS"]:
            if t["PRIMEIRA_PROVA_VALOR"] is not None:
                self.assertEqual(t["PRIMEIRA_PROVA_ONDE"], "COLLECTION_LEDGER",
                                 "%s ganhou fonte fora do recibo" % t["ITEM_ID"])


class ACoorteNaoSeReconstroi(unittest.TestCase):

    def test_a_coorte_vem_do_artefato_e_e_conferida_contra_ele(self):
        dentro, fora = W.coorte()
        self.assertEqual(len(dentro), 20)
        self.assertEqual(len(fora), 16)

    def test_quem_nao_tem_evidencia_nao_entra_nos_vinte(self):
        """Os 16 sao controlo negativo e ficam de fora, nao «por consertar»."""
        _dentro, fora = W.coorte()
        for l in fora:
            self.assertFalse(W.prova_de_fonte(l["SOURCE_ID_NO_GABARITO"]))


class OForwardNaoSeConcluiDoHistorico(unittest.TestCase):

    def test_forward_executado_fica_unknown_sem_corrida(self):
        h = W.historico_versus_forward()
        self.assertEqual(h["FORWARD_GAP_EXECUTED_AND_PROVEN"], "UNKNOWN",
                         "previsao virou medicao")

    def test_mencionar_o_recibo_num_comentario_nao_e_le_lo(self):
        """O defeito que esta prova ja teve, agora com dentes.

            UM GREP QUE NAO DISTINGUE CODIGO DE COMENTARIO
            DEIXA O TEXTO QUE EXPLICA O DEFEITO PROVAR QUE ELE NAO EXISTE.
        """
        so_comentario = ('x = 1\n'
                         '# este ficheiro nao escreve no collection-ledger\n')
        self.assertFalse(W._le_mesmo_o_recibo(so_comentario))
        le_a_serio = 'open("data/collection-ledger/italy/x.ndjson")\n'
        self.assertTrue(W._le_mesmo_o_recibo(le_a_serio))


class SchemaNaoEFluxo(unittest.TestCase):

    def test_o_banco_poder_guardar_nao_prova_que_alguem_escreve(self):
        art = _artefato()
        s = art["SCHEMA_VS_RUNTIME"]
        self.assertEqual(s["CAN_STORE"], "YES")
        self.assertEqual(s["WRITER_WRITES"], "NO")

    def test_structured_nao_observado_nao_vira_falha(self):
        """`NOT_OBSERVED` nao e `NO`. Ninguem atravessou: nao ha o que julgar.

            ERROR != UNKNOWN, e NOT_RUN nunca vira PASS nem FAIL.
        """
        art = _artefato()
        self.assertEqual(art["SCHEMA_VS_RUNTIME"]["STRUCTURED_CARRIES"],
                         "NOT_OBSERVED")


class AsGuARDAS_ESTRUTURAIS(unittest.TestCase):
    """Nascidos de mutantes que sobreviveram: cada um mata um deles."""

    def test_a_coorte_recusa_divergir_do_artefato_que_a_declara(self):
        """Mutante: apagar a conferencia contra o numero declarado.

        Dois donos do numero 20 divergem em silencio. A conferencia tem de
        rebentar, e um teste que so confirma 20/16 nao a exercita.
        """
        real = W._json
        def falso(c):
            d = real(c)
            if c == W.ALCANCE:
                import copy
                d = copy.deepcopy(d)
                d["PLANOS"]["CONTRATO"]["PORQUE"][
                    "origem · o registo confessa «NAO SEI» e a linhagem SABE"] = 99
            return d
        W._json = falso
        try:
            with self.assertRaises(W.MedicaoInvalida):
                W.coorte()
        finally:
            W._json = real

    def test_o_recibo_da_coleta_e_um_estagio_da_trilha(self):
        """Mutante: saltar o estagio do recibo."""
        art = _artefato()
        com_recibo = [t for t in art["ITEMS"]
                      if any(e["TO"] == "COLLECTION_LEDGER" and
                             e["STATUS"] == W.PRESENT for e in t["EDGES"])]
        self.assertEqual(len(com_recibo), 7,
                         "o estagio do recibo desapareceu da trilha")

    def test_o_primeiro_edge_perdido_e_o_primeiro_e_nao_o_ultimo(self):
        """Mutante: atribuir a culpa ao ultimo estagio.

            DEPOIS DO PRIMEIRO EDGE PERDIDO, OS SEGUINTES SAO CONSEQUENCIA.
        """
        art = _artefato()
        perdidos = {t["FIRST_LOST_EDGE"] for t in art["ITEMS"]
                    if t["FIRST_LOST_EDGE"] != "UNKNOWN"}
        self.assertEqual(perdidos, {"COLLECTION_LEDGER -> RAW_RECONSTRUIDO"},
                         "a culpa escorregou para outro estagio")
        for t in art["ITEMS"]:
            self.assertNotEqual(t["FIRST_LOST_EDGE"], "INGRESS -> ADMISSION",
                                "a porta foi culpada de ler o que la esta")

    def test_writer_writes_e_medido_e_nao_herdado_do_schema(self):
        """Mutante: fazer WRITER_WRITES seguir CAN_STORE."""
        s = _artefato()["SCHEMA_VS_RUNTIME"]
        self.assertEqual(s["CAN_STORE"], "YES")
        self.assertEqual(s["WRITER_WRITES"], "NO",
                         "o schema decidiu pelo writer")
        self.assertIn("ZERO RAW", s["WRITER_WRITES_PROVA"])


_CACHE = {}


def _artefato():
    """SEMPRE recomputado. NUNCA lido do disco.

    ⚠️ A PRIMEIRA VERSAO LIA `data/derivados/SOURCE-ID-WIRING-GAP-V1.json`
    quando ele existia. Resultado: seis mutacoes da logica de medicao
    SOBREVIVERAM a suite inteira — os testes liam o artefato congelado de uma
    corrida anterior e nunca chegavam a tocar no codigo mutado.

        UM TESTE QUE LE O RESULTADO GUARDADO
        TESTA O FICHEIRO, E NAO A FUNCAO QUE O ESCREVEU.

    O artefato no disco e a ENTREGA. A suite tem de exercitar o CODIGO.
    """
    if "a" not in _CACHE:
        _CACHE["a"] = W.medir()
    return _CACHE["a"]


if __name__ == "__main__":
    unittest.main()
