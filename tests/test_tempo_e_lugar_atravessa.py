# -*- coding: utf-8 -*-
"""TEMPO-E-LUGAR — o tempo e o lugar atravessam do livro do coletor até a Sala,
cada valor com a sua BASE, e nenhum se converte no outro.

Medido na Sala real (25/09): 78 de 78 com FACT_TIME, PUBLISHED_AT,
SOURCE_LOCATION e FACT_LOCATION em `NAO SEI` — e o livro sabia a data da edição
dos boletins T3, a sede declarada no contrato e o PORQUÊ de cada UNKNOWN.

    FACT_TIME != PUBLISHED_AT != OBSERVED_AT != COLLECTED_AT
    SOURCE_LOCATION != FACT_LOCATION

Os dois mutantes que esta suíte TEM de matar (tests/mutacao_tempo_e_lugar.py):
    publicação -> fact_time        reprova
    source_location -> fact_location  reprova
"""
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("", "coleta", "orquestrador", "admissao", "regras"):
    sys.path.insert(0, os.path.join(RAIZ, p))
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import contratos_de_fonte as cf  # noqa: E402
import ingresso as ing  # noqa: E402
import italy_executor as ex  # noqa: E402
import orquestrador as ORQ  # noqa: E402

NS = adm.AUSENCIA

# Observações com a forma exacta do livro italiano (data/collection-ledger).
T3_002 = {"RUN_ID": "R1", "SOURCE_ID": "IT-T3-002", "DOCUMENT_ID": "CAMPANIA:SA:16-09-2026",
          "CAPTURED_AT": "2026-09-18T17:19:15.737Z", "SOURCE_DATE": "16/09/2026",
          "SOURCE_DATE_ISO": "2026-09-16",
          "FACT_TIME": "UNKNOWN — o boletim nao data a observacao de campo",
          "SOURCE_URL": "https://agricoltura.regione.campania.it/x/SA-16-09.pdf"}
T3_010 = {"RUN_ID": "R1", "SOURCE_ID": "IT-T3-010", "DOCUMENT_ID": "APOL:2026:N10:LE",
          "CAPTURED_AT": "2026-09-18T13:07:10Z", "SOURCE_DATE": "14/09/2026 a 20/09/2026",
          "SOURCE_DATE_ISO": "2026-09-14",
          "FACT_TIME": "UNKNOWN — o periodo e de validade, nao de observacao"}
HTML = {"RUN_ID": "R2", "SOURCE_ID": "IT-T10-018", "DOCUMENT_ID": "IT-T10-018:URL:x",
        "CAPTURED_AT": "2026-09-24T07:00:00Z",
        "FACT_TIME": "UNKNOWN — identidade pelo endereco; a fonte nao expoe data do facto por regra generica"}


def _com_contratos(caso):
    if not cf.declarados():
        caso.skipTest("node indisponivel: os contratos nao se leem nesta maquina")


class OTradutorDoLivro(unittest.TestCase):
    """coleta/italy_executor.py::tempo_e_lugar — o dono do que a observação prova."""

    def setUp(self):
        _com_contratos(self)

    def test_edicao_do_boletim_vira_publicacao_com_base(self):
        t = ex.tempo_e_lugar(T3_002)
        self.assertEqual(t["PUBLISHED_AT"], "2026-09-16")
        self.assertIn("EDICAO", t["PUBLISHED_AT_BASIS"])
        self.assertIn("SOURCE_DATE_ISO", t["PUBLISHED_AT_BASIS"])

    def test_publicacao_nao_vira_tempo_do_facto(self):
        t = ex.tempo_e_lugar(T3_002)
        self.assertNotIn("FACT_TIME", t)
        self.assertIn("nao data a observacao de campo", t["FACT_TIME_BASIS"])

    def test_validade_nao_e_publicacao(self):
        t = ex.tempo_e_lugar(T3_010)
        self.assertNotIn("PUBLISHED_AT", t)
        self.assertIn("VALIDADE", t["PUBLISHED_AT_BASIS"])
        self.assertNotIn("FACT_TIME", t)

    def test_sede_vem_do_contrato_e_nao_vira_lugar_do_facto(self):
        t = ex.tempo_e_lugar(T3_002)
        self.assertEqual(t["SOURCE_LOCATION"], "Napoli")
        self.assertIn("CONTRATO", t["SOURCE_LOCATION_BASIS"])
        self.assertNotIn("FACT_LOCATION", t)
        self.assertNotIn("FACT_LOCATION_BASIS", t)

    def test_rota_generica_nao_inventa_nada_e_guarda_o_porque(self):
        t = ex.tempo_e_lugar(HTML)
        for campo in ("PUBLISHED_AT", "FACT_TIME", "SOURCE_LOCATION", "FACT_LOCATION"):
            self.assertNotIn(campo, t)
        self.assertIn("regra generica", t["FACT_TIME_BASIS"])

    def test_valor_do_coletor_sem_base_nao_atravessa(self):
        t = ex.tempo_e_lugar(dict(HTML, PUBLISHED_AT="2026-09-20",
                                  FACT_LOCATION="Puglia"))
        self.assertNotIn("PUBLISHED_AT", t)
        self.assertNotIn("FACT_LOCATION", t)

    def test_valor_do_coletor_com_base_atravessa_tal_e_qual(self):
        t = ex.tempo_e_lugar(dict(
            HTML, PUBLISHED_AT="2026-09-20T08:00:00+02:00",
            PUBLISHED_AT_BASIS="JSONLD_datePublished",
            FACT_LOCATION="Puglia", FACT_LOCATION_BASIS="ESCRITO: «... in Puglia ...»"))
        self.assertEqual(t["PUBLISHED_AT"], "2026-09-20T08:00:00+02:00")
        self.assertEqual(t["PUBLISHED_AT_BASIS"], "JSONLD_datePublished")
        self.assertEqual(t["FACT_LOCATION"], "Puglia")
        self.assertNotIn("FACT_TIME", t)

    def test_instrucao_em_prosa_nao_e_um_instante(self):
        t = ex.tempo_e_lugar(dict(HTML, FACT_TIME="por ponto — cada ponto traz a sua data"))
        self.assertNotIn("FACT_TIME", t)
        self.assertIn("por ponto", t["FACT_TIME_BASIS"])

    def test_traduzir_leva_o_recado_e_larga_a_confissao(self):
        f = ex.traduzir(dict(T3_002, RAW_PATH="data/x.pdf"))
        self.assertEqual(f["PUBLISHED_AT"], "2026-09-16")
        self.assertEqual(f["SOURCE_LOCATION"], "Napoli")
        self.assertNotIn("FACT_TIME", f)


class OContratoDizAEspecieDaData(unittest.TestCase):

    def setUp(self):
        _com_contratos(self)

    def test_so_edicao_e_publicacao(self):
        self.assertTrue(cf.data_do_documento_e_publicacao("IT-T3-002")["E_PUBLICACAO"])
        self.assertTrue(cf.data_do_documento_e_publicacao("IT-T3-008")["E_PUBLICACAO"])
        self.assertFalse(cf.data_do_documento_e_publicacao("IT-T3-010")["E_PUBLICACAO"])

    def test_sem_declaracao_nao_e_publicacao(self):
        r = cf.data_do_documento_e_publicacao("IT-T10-018")
        self.assertFalse(r["E_PUBLICACAO"])
        self.assertEqual(r["ESPECIE"], cf.NAO_SEI)


class AFronteiraLevaORecado(unittest.TestCase):
    """coleta/ingresso.py — da observação confirmada até a unidade da derivação."""

    RECADO = {"PUBLISHED_AT": "2026-09-16", "PUBLISHED_AT_BASIS": "b",
              "SOURCE_LOCATION": "Napoli", "SOURCE_LOCATION_BASIS": "c",
              "FACT_TIME_BASIS": "o coletor declarou: «UNKNOWN»"}

    def recibo(self, *alcas):
        return {"RAW_OBSERVATIONS": [{"RAW_OBSERVATION_ID": 41,
                                      ing.PASSAGENS: list(alcas),
                                      "STORAGE_PATH": "XX/a.pdf",
                                      "MEDIA_TYPE": "application/pdf",
                                      "SOURCE_ID": "IT-T3-002"}]}

    def test_a_observacao_leva_o_recado_do_seu_item(self):
        item = dict(self.RECADO, texto="x", NAO_ATRAVESSA="y")
        m = ing.tempo_e_lugar_por_observacao(self.recibo("a"), {"a": item})
        self.assertEqual(m[41], self.RECADO)

    def test_passagens_que_discordam_nao_escolhem(self):
        a = dict(self.RECADO)
        b = dict(self.RECADO, PUBLISHED_AT="2026-09-17")
        m = ing.tempo_e_lugar_por_observacao(self.recibo("a", "b"), {"a": a, "b": b})
        self.assertNotIn("PUBLISHED_AT", m[41])
        self.assertEqual(m[41]["SOURCE_LOCATION"], "Napoli")

    def test_a_confissao_nao_atravessa_como_valor(self):
        item = dict(self.RECADO, FACT_TIME=NS, FACT_LOCATION="")
        m = ing.tempo_e_lugar_por_observacao(self.recibo("a"), {"a": item})
        self.assertNotIn("FACT_TIME", m[41])
        self.assertNotIn("FACT_LOCATION", m[41])

    def test_a_unidade_da_derivacao_leva_o_recado(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
            fh.write(b"%PDF-1.4")
        self.addCleanup(os.unlink, fh.name)

        class Armazem:
            def caminho_local(self, _):
                return fh.name
        rec = self.recibo("a")
        unidades, _ = ing.unidades_para_a_derivacao(
            rec, Armazem(), ing.tempo_e_lugar_por_observacao(rec, {"a": self.RECADO}))
        self.assertEqual(unidades[0]["TEMPO_E_LUGAR"], self.RECADO)

    def test_sem_recado_a_unidade_leva_vazio_e_nao_inventa(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
            fh.write(b"%PDF-1.4")
        self.addCleanup(os.unlink, fh.name)

        class Armazem:
            def caminho_local(self, _):
                return fh.name
        unidades, _ = ing.unidades_para_a_derivacao(self.recibo("a"), Armazem())
        self.assertEqual(unidades[0]["TEMPO_E_LUGAR"], {})

    def test_o_tradutor_conhece_as_bases(self):
        p = ing.para_a_porta({"PUBLISHED_AT_BASIS": "b", "SOURCE_LOCATION_BASIS": "c"})
        self.assertEqual(p["published_at_basis"], "b")
        self.assertEqual(p["source_location_basis"], "c")


def _estruturado(recado):
    return {"SOURCE_ID": "IT-T3-002", "TEXTO": "Bollettino fitosanitario. Peronospora.",
            "DERIVED_ARTIFACT_ID": 9, "RAW_ASSET_ID": 41, "PARENT_SHA256": "d" * 64,
            "CAPTURED_AT": "2026-09-18T17:19:15.737Z", "TEMPO_E_LUGAR": recado}


class ChegaAoReady(unittest.TestCase):
    """orquestrador.item_documental_para_a_porta -> admissao.pronto_para_inteligencia."""

    def setUp(self):
        _com_contratos(self)
        self.recado = ex.tempo_e_lugar(T3_002)
        self.item = ORQ.item_documental_para_a_porta(
            _estruturado(self.recado), source_id="IT-T3-002")
        d = adm.Decisao(item=self.item["id"], universo="T3", resultado=adm.SIM,
                        regra="teste", motivo="teste")
        self.ready = adm.pronto_para_inteligencia(self.item, d)

    def test_o_item_da_porta_fala_a_lingua_da_porta(self):
        self.assertEqual(self.item["published_at"], "2026-09-16")
        self.assertEqual(self.item["source_location"], "Napoli")
        self.assertNotIn("PUBLISHED_AT", self.item)

    def test_ready_leva_publicacao_e_sede(self):
        self.assertEqual(self.ready["PUBLISHED_AT"], "2026-09-16")
        self.assertEqual(self.ready["SOURCE_LOCATION"], "Napoli")
        self.assertIn("nao data a observacao", self.ready["FACT_TIME_BASIS"])

    def test_ready_nao_converte_publicacao_em_tempo_do_facto(self):
        self.assertEqual(self.ready["FACT_TIME"], NS)
        self.assertNotEqual(self.ready["FACT_TIME"], self.ready["PUBLISHED_AT"])

    def test_ready_nao_converte_sede_em_lugar_do_facto(self):
        self.assertEqual(self.ready["FACT_LOCATION"], NS)
        self.assertNotEqual(self.ready["FACT_LOCATION"], self.ready["SOURCE_LOCATION"])
        # sem lugar provado, a base diz o porque — e e o texto que o diz
        self.assertIn("TEXTO:", self.ready["FACT_LOCATION_BASIS"])

    def test_captura_continua_a_ser_captura(self):
        self.assertEqual(self.ready["CAPTURED_AT"], "2026-09-18T17:19:15.737Z")
        self.assertNotEqual(self.ready["PUBLISHED_AT"], self.ready["CAPTURED_AT"])

    def test_so_a_lista_declarada_atravessa(self):
        item = ORQ.item_documental_para_a_porta(
            _estruturado({"FACT_TIME_PALPITE": "2026-09-01", "PUBLISHED_AT": NS}),
            source_id="IT-T3-002")
        self.assertNotIn("FACT_TIME_PALPITE", item)
        self.assertNotIn("published_at", item)

    def test_o_texto_prova_o_lugar_do_facto_com_o_trecho(self):
        est = _estruturado(self.recado)
        est["TEXTO"] = ("Aggiornamento fitosanitario settimanale per le colture orticole. "
                        "Peronospora constatata a Grosseto su pomodoro in pieno campo nella "
                        "settimana appena trascorsa dai tecnici regionali.")
        item = ORQ.item_documental_para_a_porta(est, source_id="IT-T3-002")
        self.assertEqual(item["source_location"], "Napoli")
        self.assertIn("Grosseto", item.get("fact_location", ""))
        self.assertIn("Grosseto", item["fact_location_basis"])
        self.assertNotIn("Napoli", item["fact_location"])

    def test_o_que_o_coletor_provou_vence_o_texto(self):
        recado = dict(self.recado, FACT_TIME="2026-09-10", FACT_TIME_BASIS="declarado no livro")
        est = _estruturado(recado)
        est["TEXTO"] = ("Aggiornamento fitosanitario settimanale per le colture orticole. "
                        "Sintomi di peronospora osservati il 3 settembre in provincia di Grosseto "
                        "su pomodoro in pieno campo, con danni ancora limitati.")
        item = ORQ.item_documental_para_a_porta(est, source_id="IT-T3-002")
        self.assertEqual(item["fact_time"], "2026-09-10")
        self.assertEqual(item["fact_time_basis"], "declarado no livro")

    def test_sem_recado_tudo_continua_nao_sei(self):
        item = ORQ.item_documental_para_a_porta(_estruturado({}), source_id="IT-T3-002")
        d = adm.Decisao(item=item["id"], universo="T3", resultado=adm.SIM,
                        regra="teste", motivo="teste")
        r = adm.pronto_para_inteligencia(item, d)
        for campo in ("PUBLISHED_AT", "SOURCE_LOCATION", "FACT_TIME", "FACT_LOCATION"):
            self.assertEqual(r[campo], NS, campo)


if __name__ == "__main__":
    unittest.main()
