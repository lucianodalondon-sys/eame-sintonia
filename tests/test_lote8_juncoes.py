"""LOTE8-INTEGRA — as JUNCOES que so existem com os ramos juntos.

Cada ramo do lote 8 nasceu sem ver os outros (quatro de 18461b92d, tres de c551062) e provou-se
sozinho. Estes testes provam o que so aparece na arvore integrada:

  J-ACERVO  o acervo (ACERVO-NA-INTELLIGENCE) monta objetos a mao; desde a D123 (LIGACAO-ADAMA) todo
            objeto leva a ligacao feita PELA PORTA, e o pote recusa quem nao leva. Aqui: concorrente,
            mercado, voz e arquivo saem ligados pela porta, e a voz recebe a porta aberta.
  J-BUSCA   social_por_url_achado (SOCIAL-ATE-A-SALA) le o ficheiro que linha_busca (lote 5) escreve,
            num ramo que nao tinha a linha_busca. Aqui: o registo REAL de linha_busca.colher_um entra
            com a proveniencia inteira.
  J-LINHAS  coleta_continua mede se cada linha chama a reserva de 24 h. Na arvore do ramo a BUSCA nao
            existia; nesta existe e NAO reserva: tem de ficar ESPERA_LIGACAO pelo motivo certo (nao
            pode entrar no rodizio so por o ficheiro ter aparecido). A SITES continua ligada depois
            do FEED-LIGADO mexer no transporte.

Rede fechada: nada aqui abre socket.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import acervo_na_intelligence as A          # noqa: E402  (pacote/)
import porta_da_referencia as PORTA         # noqa: E402  (motor/)
import linha_busca as LB                    # noqa: E402  (coleta/)
import social_por_url_achado as SOC         # noqa: E402  (coleta/)
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
import coleta_continua as CC                # noqa: E402

NAO_SEI = A.NAO_SEI


def _x(col, rid, tipo):
    return {"ACERVO_ID": f"italy-handoff-v21.js::{col}::{rid}", "TIPO": tipo, "SOURCE_IDS": ["SRC_A"],
            "URL": "https://exemplo/" + rid}


def _ctx(linhas, ref):
    return {"RUN_ID": "IR-LOTE8", "LINHA": linhas, "RAW": {}, "REF": ref,
            "READY": {k: {"ITEM_ID": k, "RAW_OBSERVATION_ID": "r", "SOURCE_ID": "S",
                          "PUBLISHED_AT": NAO_SEI, "CAPTURED_AT": NAO_SEI} for k in linhas}}


def _da_porta(test, lig):
    test.assertIsInstance(lig, dict, "objeto sem LIGACAO_ADAMA")
    test.assertEqual(PORTA.conferir_ligacao(lig), [], "ligacao que a porta nao reconhece")
    test.assertEqual(lig["CALCULADA_POR"], PORTA.PORTA)


class J_Acervo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = PORTA.abrir()

    def test_JA1_mercado_ligado_pela_porta_com_a_porta_aberta(self):
        x = _x("marketObservations", "M1", "preco")
        regs = {x["ACERVO_ID"]: {"MARKET": "Bologna", "PRODUCT": "grano", "STAGE": "farm gate", "UNIT": "€/t",
                                 "PRICE_NUM": 10.0}}
        linhas = {x["ACERVO_ID"]: {"ITEM_ID": x["ACERVO_ID"], "G0": "PASSOU", "FACT_TIME": "2026-06-01..2026-06-07"}}
        objs, nao = A.mercado([x], regs, _ctx(linhas, self.ref))
        self.assertEqual(nao, [])
        (o,) = objs
        _da_porta(self, o["LIGACAO_ADAMA"])
        # a cultura do objeto e NAO SEI (o registo da o produto de mercado): a porta diz o que falta,
        # e a porta que respondeu e a ABERTA (nao NAO_SEI/REFERENCIA)
        self.assertEqual(o["LIGACAO_ADAMA"]["ESTADO"], PORTA.NAO_SEI_LIGACAO)
        self.assertIn("CULTURA", o["LIGACAO_ADAMA"]["FALTA"])
        self.assertNotIn("REFERENCIA", o["LIGACAO_ADAMA"]["FALTA"])

    def test_JA2_a_voz_recebe_a_porta_aberta(self):
        x = _x("fieldVoices", "V1", "voz")
        regs = {x["ACERVO_ID"]: {"TEXT_ORIGINAL": "la peronospora sulla vite e forte quest'anno"}}
        linhas = {x["ACERVO_ID"]: {"ITEM_ID": x["ACERVO_ID"], "G0": "PASSOU", "FACT_TIME": "2026-06-01"}}
        visto = {}
        original = A.VOZ.extrair

        def espiao(doc, referencia=None):
            visto["REF"] = referencia
            return original(doc, referencia=referencia)
        A.VOZ.extrair = espiao
        try:
            objs, _nao, _m = A.vozes([x], regs, _ctx(linhas, self.ref))
        finally:
            A.VOZ.extrair = original
        self.assertIs(visto.get("REF"), self.ref, "o acervo chamou voce_dal_campo sem a porta aberta")
        for o in objs:
            _da_porta(self, o["LIGACAO_ADAMA"])

    def test_JA3_o_arquivo_leva_a_ligacao_do_objeto_de_origem(self):
        lig = PORTA.ligacao_adama(self.ref, {"VEM_DE": {}})
        o = {"OBJETO_ID": "R7-COMP-x", "ESPECIE": "SINAL", "ESTADO": "E", "PORQUE": "p", "CONTRADIZ": None,
             "INCERTEZA": None, "PROVA": [{"FACT_TIME": "2026-01-01"}], "LIGACAO_ADAMA": lig,
             "CHAVES": {"FACT_TIME": "2026-01-01"}}
        (a,) = A.arquivo({"competitors": [o]})
        self.assertEqual(a["LIGACAO_ADAMA"], lig)

    def test_JA4_o_pote_commitado_do_acervo_tem_todo_objeto_ligado_pela_porta(self):
        pote = json.loads(A.POTE_SAIDA.read_text(encoding="utf-8"))
        n = 0
        for comp, e in pote["COMPARTIMENTOS"].items():
            for o in e["OBJETOS"]:
                _da_porta(self, o.get("LIGACAO_ADAMA"))
                n += 1
        self.assertGreater(n, 1000)
        self.assertNotIn("SEM_LIGACAO_ADAMA", {r["MOTIVO"] for r in pote["RECUSADOS"]})
        self.assertNotIn("LIGACAO_ADAMA_FORA_DA_PORTA", {r["MOTIVO"] for r in pote["RECUSADOS"]})


class J_Busca(unittest.TestCase):
    def test_JB1_o_registo_real_da_linha_busca_entra_no_social(self):
        with tempfile.TemporaryDirectory() as d:
            saida = Path(d)
            r = {"URL": "https://www.instagram.com/agronomo.it/reel/Cabc12345/", "CONSULTA": "peronospora vite",
                 "CONSULTA_ID": "Q1", "MOTOR": "api-oficial", "ROTA_DO_MOTOR": "API", "POSICAO": 3,
                 "INSTANTE": "2026-09-27T10:00:00+00:00", "UNIVERSO": "IT"}
            reg = LB.colher_um(r, saida, saida, buscar=None, ledger=(), corrida="C-LOTE8")
            self.assertEqual(reg["ESTADO"], "POST_SOCIAL_PARA_O_SCRAP")
            linhas = (saida / "POSTS-PARA-O-SCRAP.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(linhas), 1)
            achado = json.loads(linhas[0])
        self.assertEqual(SOC.falta_na_proveniencia(achado["PROVENIENCIA"]), [],
                         "o formato que a linha_busca escreve ja nao e o que o social le")
        self.assertEqual(SOC.especie_do_endereco(achado["URL"])["ESPECIE"], "REEL")

    def test_JB2_as_duas_formas_do_reel_e_do_post_vao_para_o_scrap(self):
        """O que o social le como publicacao, a busca manda para POSTS-PARA-O-SCRAP (nunca para PISTAS)."""
        for u in ("https://www.instagram.com/reel/Cabc12345/", "https://www.instagram.com/oliveti_sezze/reel/DAbCdEfGhIj/",
                  "https://www.instagram.com/p/Cabc12345/", "https://www.instagram.com/conta.x/p/Cabc12345/",
                  "https://www.linkedin.com/posts/mario-rossi_vite-activity-7112345678901234567-abcd",
                  "https://www.linkedin.com/feed/update/urn:li:activity:7112345678901234567/"):
            self.assertNotEqual(SOC.especie_do_endereco(u)["ESPECIE"], "NAO_E_PUBLICACAO", u)
            self.assertEqual(LB.especie_do_resultado(u), "POST_SOCIAL", u)
        for u in ("https://www.instagram.com/oliveti_sezze/", "https://www.linkedin.com/company/adama/"):
            self.assertEqual(LB.especie_do_resultado(u), "PERFIL_SOCIAL", u)


class J_Linhas(unittest.TestCase):
    def _linha(self, nome):
        return next(l for l in CC.LINHAS if l["LINHA"] == nome)

    def test_JL1_sites_continua_ligada_depois_do_feed(self):
        m = CC.medir_ligacao(self._linha("SITES"))
        self.assertTrue(m["LIGADA"], m["PORQUE"])

    def test_JL2_busca_existe_e_nao_reserva_fica_a_espera_pelo_motivo_certo(self):
        self.assertTrue((RAIZ / "coleta" / "linha_busca.py").exists())
        m = CC.medir_ligacao(self._linha("BUSCA"))
        self.assertFalse(m["LIGADA"])
        self.assertTrue(m["PORQUE"].startswith("SEM_RESERVA_24H"), m["PORQUE"])


if __name__ == "__main__":
    unittest.main()
