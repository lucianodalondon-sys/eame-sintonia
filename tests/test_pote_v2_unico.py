#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O POTE V2 UNICO, ATACADO — missao POTE-V2-UNICO (contrato Intelligence -> casco, D97).

    python3 -m unittest tests.test_pote_v2_unico -v

UM contrato (POTE_INTELLIGENCE_CASCO/v2): docs/intelligence/pote-v2/CONTRATO-POTE-V2.md, o schema ao lado,
e o validador (pacote/validar_pote_v2.py = schema + `conferir_pote`). Aqui prova-se:

    R  INTELLIGENCE_RUN_ID no topo; em CABECALHO so por leitura DECLARADA de compatibilidade
    U  cada PROVA com URL e PUBLISHED_AT, ou NAO SEI com a base
    E  ESPECIE e quem a disse; ENTITY_SOURCE / LOCATION_SOURCE (D112)
    T  P7 · resultado honesto e fonte do Registro nao dependem de FACT_TIME; so os usos que exigem tempo
    M  P8 · sinal solto nunca e mudanca de mercado; so SERIE medida (>= 2 pontos, mesma unidade)
    S  o schema e o codigo dizem o mesmo; o validador le .json e o .js do casco

⚠️ DADO SINTETICO DECLARADO: tests/fixtures/pote/CORRIDA-SINTETICA-V2-UNICO.json e
CORRIDA-SINTETICA-R6-EQUIVALENTE.json (gerada por provas/pote_v2/medir_recusas_r6.py). Todo id comeca
por SINT-, SINTETICA = true.
"""
import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "pacote", RAIZ / "provas" / "pote_v2", RAIZ / "tests"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pote_intelligence_casco as P                           # noqa: E402
import validar_pote_v2 as VV                                  # noqa: E402

NAO_SEI = P.NAO_SEI
FX = RAIZ / "tests" / "fixtures" / "pote"
V2U = FX / "CORRIDA-SINTETICA-V2-UNICO.json"
POTE_V2U = FX / "POTE-SINTETICO-V2-UNICO.json"
R6 = FX / "CORRIDA-SINTETICA-R6-EQUIVALENTE.json"


def corrida(f=V2U):
    return json.loads(f.read_text(encoding="utf-8"))


def obj(pote, comp, oid):
    return next(o for o in pote["COMPARTIMENTOS"][comp]["OBJETOS"] if o["OBJETO_ID"] == oid)


def ids(pote, comp):
    return [o["OBJETO_ID"] for o in pote["COMPARTIMENTOS"][comp]["OBJETOS"]]


def motivos(pote):
    return {(r["COMPARTIMENTO"], r["OBJETO_ID"], r["MOTIVO"]) for r in pote["RECUSADOS"]}


class R_UmaCorridaNoTopo(unittest.TestCase):

    def test_R1_sem_run_id_nao_ha_pote(self):
        c = corrida()
        del c["INTELLIGENCE_RUN_ID"]
        with self.assertRaises(P.LeiViolada):
            P.adaptar(c)

    def test_R2_run_id_em_cabecalho_e_lido_e_a_leitura_fica_escrita(self):
        c = corrida()
        cab = {k: c.pop(k) for k in ("INTELLIGENCE_RUN_ID", "SOURCE_HEAD", "CORTE", "RESULT_STATE")}
        c["CABECALHO"] = cab
        pote = P.adaptar(c)
        self.assertEqual(pote["INTELLIGENCE_RUN_ID"], "SINT-IR-V2U-0001")
        self.assertEqual(pote["SOURCE_HEAD"], cab["SOURCE_HEAD"])
        self.assertEqual(len(pote["LEITURA_DE_COMPATIBILIDADE"]), 4)
        self.assertTrue(all("CABECALHO" in x for x in pote["LEITURA_DE_COMPATIBILIDADE"]))
        self.assertNotIn("CABECALHO", pote)
        self.assertEqual(VV.validar(pote), [])

    def test_R3_sem_compatibilidade_a_lista_existe_e_esta_vazia(self):
        self.assertEqual(P.adaptar(corrida())["LEITURA_DE_COMPATIBILIDADE"], [])

    def test_R4_topo_e_cabecalho_que_divergem_sao_duas_corridas(self):
        c = corrida()
        c["CABECALHO"] = {"INTELLIGENCE_RUN_ID": "SINT-IR-OUTRA"}
        with self.assertRaises(P.LeiViolada):
            P.adaptar(c)

    def test_R5_pote_com_run_id_so_em_cabecalho_reprova_no_validador(self):
        pote = P.adaptar(corrida())
        pote["CABECALHO"] = {"INTELLIGENCE_RUN_ID": pote.pop("INTELLIGENCE_RUN_ID")}
        v = VV.validar(pote)
        self.assertTrue(any("INTELLIGENCE_RUN_ID" in x and "CABECALHO" in x for x in v), v)

    def test_R6_um_pote_de_outro_formato_nao_se_readapta(self):
        """O R5 do bot trazia COMPARTIMENTOS proprios: nao e o livro de uma corrida."""
        with self.assertRaises(P.LeiViolada):
            P.adaptar({"CABECALHO": {"INTELLIGENCE_RUN_ID": "SINT-IR-R5"}, "COMPARTIMENTOS": {}})


class U_ProvaComUrlEPublicacao(unittest.TestCase):

    def setUp(self):
        self.pote = P.adaptar(corrida())

    def test_U1_toda_prova_tem_url_e_published_at_ou_nao_sei_com_base(self):
        for e in self.pote["COMPARTIMENTOS"].values():
            for o in e["OBJETOS"]:
                for p in o["PROVA"]:
                    for c in ("URL", "PUBLISHED_AT"):
                        self.assertIn(c, p)
                        self.assertTrue(p[c + "_BASE"], (o["OBJETO_ID"], c))
                        if p[c] == NAO_SEI:
                            self.assertTrue(p[c + "_BASE"].startswith("NAO_VEIO"), p[c + "_BASE"])

    def test_U2_a_base_diz_de_onde_veio(self):
        p = obj(self.pote, "portfolio", "SINT-CR-NAO")["PROVA"][0]
        self.assertEqual((p["URL_BASE"], p["PUBLISHED_AT_BASE"]), ("PROVA.URL", "PROVA.PUBLISHED_AT"))
        p = obj(self.pote, "market", "SINT-MK-SOLTO")["PROVA"][0]
        self.assertEqual((p["PUBLISHED_AT"], p["PUBLISHED_AT_BASE"]), ("2026-09-18", "LINEAGE.PUBLICATION_TIME"))
        self.assertEqual(p["FACT_TIME"], NAO_SEI, "a publicacao nao vira tempo do facto")

    def test_U3_o_validador_reprova_prova_sem_url_ou_sem_base(self):
        def reprova(mexer):
            pote = copy.deepcopy(self.pote)
            mexer(obj(pote, "portfolio", "SINT-CR-NAO")["PROVA"][0])
            self.assertTrue(VV.validar(pote))
        reprova(lambda p: p.pop("URL"))
        reprova(lambda p: p.pop("PUBLISHED_AT"))
        reprova(lambda p: p.update(URL=NAO_SEI, URL_BASE=NAO_SEI))
        reprova(lambda p: p.update(PUBLISHED_AT=NAO_SEI, PUBLISHED_AT_BASE=""))
        reprova(lambda p: p.pop("ADMITIDA_POR"))

    def test_U4_publicado_em_da_entrada_e_so_leitura(self):
        pote = P.adaptar(corrida())
        for e in pote["COMPARTIMENTOS"].values():
            for o in e["OBJETOS"]:
                for p in o["PROVA"]:
                    self.assertNotIn("PUBLICADO_EM", p)


class E_EspecieEOrigem_D112(unittest.TestCase):

    def setUp(self):
        self.pote = P.adaptar(corrida())

    def test_E1_toda_especie_e_dita_e_valida(self):
        self.assertEqual(VV.validar(self.pote), [])
        pote = copy.deepcopy(self.pote)
        obj(pote, "meeting", "SINT-ND-1")["ESPECIE_DITA_POR"] = NAO_SEI
        self.assertTrue(VV.validar(pote))
        pote = copy.deepcopy(self.pote)
        del obj(pote, "meeting", "SINT-ND-1")["ESPECIE"]
        self.assertTrue(VV.validar(pote))

    def test_E2_entity_e_location_source_viajam_com_o_nome_deles(self):
        o = obj(self.pote, "windows", "SINT-W-LUGAR")
        # D-GER-1-MIG (decisao do dono do contrato, 29/09): o valor viaja com o nome dele SEM MUDAR — o objeto
        # traz EXATAMENTE o ENTITY_SOURCE da entrada, e esse valor e da COL-LAW-221.
        entrada = next(x for x in corrida()["ITENS_POR_FERRAMENTA"]["windows"] if x["OBJETO_ID"] == "SINT-W-LUGAR")
        self.assertEqual(o["ENTITY_SOURCE"], entrada["ENTITY_SOURCE"])
        self.assertEqual(o["ENTITY_SOURCE"], "UNKNOWN")
        self.assertIn(o["ENTITY_SOURCE"], P.ENTITY_SOURCES)
        self.assertEqual(o["LOCATION_SOURCE"], "TEXTO_DO_BOLETIM")
        self.assertNotIn("LOCATION_SOURCE", o["FORA_DO_CONTRATO"])
        self.assertNotIn("LOCATION_SOURCE", o["CHAVES"])

    def test_E3_lugar_do_facto_sem_origem_fica_nao_sei_a_vista(self):
        c = corrida()
        del c["ITENS_POR_FERRAMENTA"]["windows"][0]["LOCATION_SOURCE"]
        o = obj(P.adaptar(c), "windows", "SINT-W-LUGAR")
        self.assertEqual(o["LOCATION_SOURCE"], NAO_SEI)
        pote = copy.deepcopy(self.pote)
        del obj(pote, "windows", "SINT-W-LUGAR")["LOCATION_SOURCE"]
        self.assertTrue(VV.validar(pote))

    def test_E4_o_lugar_da_fonte_nao_vira_lugar_do_facto(self):
        self.assertIn(("windows", "SINT-W-SEDE", "LUGAR_DA_FONTE_NAO_E_LUGAR_DO_FACTO"), motivos(self.pote))
        pote = copy.deepcopy(self.pote)
        obj(pote, "windows", "SINT-W-LUGAR")["LOCATION_SOURCE"] = "source location"
        self.assertTrue(VV.validar(pote))


class T_OQueExigeTempo_P7(unittest.TestCase):

    def setUp(self):
        self.pote = P.adaptar(corrida())

    def test_T1_o_nao_do_cruzamento_atravessa_sem_tempo_ancorado(self):
        o = obj(self.pote, "portfolio", "SINT-CR-NAO")
        self.assertEqual((o["RESULTADO"], o["USO_EXIGE_TEMPO"]), ("NAO", False))
        self.assertEqual((o["PROVA"][0]["G0"], o["PROVA"][0]["ADMITIDA_POR"]), ("BLOQUEADO_EM_G0", "USO_SEM_TEMPO"))

    def test_T2_no_defensible_action_yet_atravessa(self):
        o = obj(self.pote, "meeting", "SINT-ND-1")
        self.assertEqual((o["RESULTADO"], o["USO_EXIGE_TEMPO"]), ("NO_DEFENSIBLE_ACTION_YET", False))

    def test_T3_a_fonte_do_registro_nao_depende_do_tempo(self):
        o = obj(self.pote, "sources", "SINT-REND-A")
        self.assertFalse(o["USO_EXIGE_TEMPO"])
        self.assertEqual([p["ADMITIDA_POR"] for p in o["PROVA"]], ["G0_PASSOU", "USO_SEM_TEMPO"])

    def test_T4_os_usos_que_exigem_tempo_continuam_a_exigir(self):
        m = motivos(self.pote)
        self.assertIn(("archive", "SINT-SG-TEMPO", "ITEM_BLOQUEADO_EM_G0"), m)     # sinal
        self.assertIn(("portfolio", "SINT-CR-SIM", "ITEM_BLOQUEADO_EM_G0"), m)     # crossing afirmativo
        self.assertIn(("meeting", "SINT-OP-NAO", "ITEM_BLOQUEADO_EM_G0"), m)       # oportunidade nunca e «nao»

    def test_T5_sem_proveniencia_continua_bloqueado_mesmo_sem_exigir_tempo(self):
        m = motivos(self.pote)
        self.assertIn(("meeting", "SINT-CR-TRATAR", "ITEM_BLOQUEADO_EM_G0"), m)
        self.assertIn(("sources", "SINT-REND-D", "ITEM_BLOQUEADO_EM_G0"), m)

    def test_T6_o_vocabulario_honesto_normaliza_acentos_e_espacos(self):
        self.assertEqual(P.normal("não tratar agora"), "NAO_TRATAR_AGORA")
        self.assertEqual(P.resultado_honesto({"CHAVES": {"CROSSING_STATE": "não"}}), "NAO")
        self.assertIsNone(P.resultado_honesto({"CHAVES": {"CROSSING_STATE": "CASA"}}))

    def test_T7_o_validador_reprova_uso_temporal_provado_sem_tempo(self):
        pote = copy.deepcopy(self.pote)
        o = obj(pote, "portfolio", "SINT-CR-NAO")
        o["RESULTADO"] = NAO_SEI
        o["USO_EXIGE_TEMPO"] = True
        self.assertTrue(any("EXIGE tempo" in x for x in VV.validar(pote)))
        pote = copy.deepcopy(self.pote)
        obj(pote, "portfolio", "SINT-CR-NAO")["USO_EXIGE_TEMPO"] = True
        self.assertTrue(VV.validar(pote))

    def test_T8_r6_equivalente_45_das_46_recusas_voltam_so_fica_o_controlo(self):
        """A base (f357712) recusa 46 nesta fixture — medido por provas/pote_v2/medir_recusas_r6.py."""
        pote = P.adaptar(corrida(R6))
        self.assertEqual([(r["COMPARTIMENTO"], r["OBJETO_ID"]) for r in pote["RECUSADOS"]],
                         [("archive", "SINT-R6-ARQ-TEMPO")])
        self.assertEqual(len(pote["COMPARTIMENTOS"]["sources"]["OBJETOS"]), 47)
        self.assertIn("SINT-R6-CR-NAO", ids(pote, "portfolio"))
        self.assertEqual(VV.validar(pote), [])


class M_OPolso_P8(unittest.TestCase):

    def setUp(self):
        self.pote = P.adaptar(corrida())

    def _leitura(self, oid):
        return obj(self.pote, "market", oid)["MERCADO"]

    def test_M1_um_preco_solto_e_sinal_solto(self):
        m = self._leitura("SINT-MK-SOLTO")
        self.assertEqual((m["LEITURA"], m["SERIE"], m["UNIDADE"]), ("SINAL_SOLTO", [], NAO_SEI))

    def test_M2_serie_medida_com_dois_pontos_na_mesma_unidade(self):
        m = self._leitura("SINT-MK-SERIE")
        self.assertEqual((m["LEITURA"], m["PONTOS"], m["UNIDADE"]), ("SERIE_MEDIDA", 2, "EUR/t"))
        self.assertNotIn("MUDANCA_DE_MERCADO", obj(self.pote, "market", "SINT-MK-SERIE"))

    def test_M3_unidades_diferentes_nao_sao_serie(self):
        m = self._leitura("SINT-MK-UNID")
        self.assertEqual(m["LEITURA"], "SINAL_SOLTO")
        self.assertIn("unidades diferentes", m["PORQUE"])

    def test_M4_afirmar_mudanca_com_um_ponto_e_recusado(self):
        self.assertIn(("market", "SINT-MK-AFIRMA", "SINAL_SOLTO_NAO_E_MUDANCA_DE_MERCADO"), motivos(self.pote))

    def test_M5_regras_da_serie(self):
        ponto = lambda per, u="EUR/t": {"PERIOD": per, "PRICE": "SINT-1", "UNIT": u}  # noqa: E731
        self.assertEqual(P.ler_serie({"SERIE": [ponto("A")]})[0], "SINAL_SOLTO")
        self.assertEqual(P.ler_serie({"SERIE": [ponto("A"), ponto("A")]})[0], "SINAL_SOLTO")
        self.assertEqual(P.ler_serie({"SERIE": [ponto("A"), dict(ponto("B"), PRICE=NAO_SEI)]})[0], "SINAL_SOLTO")
        self.assertEqual(P.ler_serie({"SERIE": [ponto("A"), ponto("B")]})[0], "SERIE_MEDIDA")

    def test_M6_o_validador_reprova_sinal_solto_como_serie(self):
        pote = copy.deepcopy(self.pote)
        obj(pote, "market", "SINT-MK-SOLTO")["MERCADO"]["LEITURA"] = "SERIE_MEDIDA"
        self.assertTrue(any("SERIE_MEDIDA" in x for x in VV.validar(pote)))
        pote = copy.deepcopy(self.pote)
        obj(pote, "market", "SINT-MK-SOLTO")["MUDANCA_DE_MERCADO"] = True
        self.assertTrue(VV.validar(pote))
        pote = copy.deepcopy(self.pote)
        del obj(pote, "market", "SINT-MK-SOLTO")["MERCADO"]
        self.assertTrue(VV.validar(pote))

    def test_M7_r6_equivalente_os_seis_precos_sao_sinais_soltos(self):
        pote = P.adaptar(corrida(R6))
        self.assertEqual({o["MERCADO"]["LEITURA"] for o in pote["COMPARTIMENTOS"]["market"]["OBJETOS"]},
                         {"SINAL_SOLTO"})


class S_SchemaEValidador(unittest.TestCase):

    def setUp(self):
        self.schema = VV.carregar_schema()
        self.pote = P.adaptar(corrida())

    def test_S1_schema_e_codigo_dizem_o_mesmo(self):
        d = self.schema["$defs"]
        self.assertEqual(self.schema["properties"]["SCHEMA"]["const"], P.CONTRATO)
        self.assertEqual(self.schema["properties"]["MARCA"]["const"], P.MARCA)
        self.assertEqual(self.schema["properties"]["COMPARTIMENTOS"]["required"], list(P.COMPARTIMENTOS))
        self.assertEqual(d["objeto"]["properties"]["ESPECIE"]["enum"], list(P.ESPECIES))
        self.assertEqual(d["objeto"]["properties"]["RESULTADO"]["enum"], list(P.RESULTADOS_HONESTOS) + [NAO_SEI])
        self.assertEqual(d["prova"]["properties"]["ADMITIDA_POR"]["enum"], list(P.ADMITIDA))
        self.assertEqual(d["objeto"]["properties"]["MERCADO"]["properties"]["LEITURA"]["enum"],
                         [P.SERIE_MEDIDA, P.SINAL_SOLTO])
        exigidos = set(P.CAMPOS_DA_PROVA) | set(P.CAMPOS_DA_PROVA_V2) | {c + "_BASE" for c in P.CAMPOS_COM_BASE} \
            | {"CORRIDA_UPSTREAM", "G0", "ADMITIDA_POR", "INTELLIGENCE_RUN_ID"}
        self.assertEqual(set(d["prova"]["required"]), exigidos)
        # tudo o que o pote escreve num objeto e numa prova esta no schema, e vice-versa
        for e in self.pote["COMPARTIMENTOS"].values():
            for o in e["OBJETOS"]:
                self.assertTrue(set(d["objeto"]["required"]) <= set(o))
                for p in o["PROVA"]:
                    self.assertEqual(set(p), exigidos)

    def test_S2_as_duas_fixtures_e_o_payload_v1_passam(self):
        for f in (FX / "POTE-SINTETICO.json", POTE_V2U):
            self.assertEqual(VV.main([str(f)]), 0, f)

    def test_S3_a_forma_reprova_sem_passar_pela_lei(self):
        pote = copy.deepcopy(self.pote)
        del pote["COMPARTIMENTOS"]["market"]["OBJETOS"][0]["PROVA"][0]["URL_BASE"]
        self.assertTrue(VV.forma(pote))
        self.assertTrue(VV.forma(dict(self.pote, INTELLIGENCE_RUN_ID=NAO_SEI)))

    def test_S4_palavra_do_schema_que_o_verificador_nao_le_reprova(self):
        self.assertTrue(VV.forma({}, {"type": "object", "patternProperties": {}}))

    def test_S5_le_o_js_que_o_casco_carrega(self):
        with tempfile.TemporaryDirectory() as d:
            js = Path(d) / "sintonia-pote.js"
            self.assertEqual(P.main([str(V2U), str(js)]), 0)
            self.assertEqual(VV.main([str(js)]), 0)
            js.write_text(js.read_text(encoding="utf-8").replace('"SINT-IR-V2U-0001"', '""', 1), encoding="utf-8")
            self.assertEqual(VV.main([str(js)]), 1)
            self.assertEqual(VV.main([str(Path(d) / "nao-existe.js")]), 2)

    def test_S6_o_documento_do_contrato_existe_e_aponta_para_o_dono(self):
        doc = (RAIZ / "docs" / "intelligence" / "pote-v2" / "CONTRATO-POTE-V2.md").read_text(encoding="utf-8")
        for termo in ("POTE_INTELLIGENCE_CASCO/v2", "pacote/pote_intelligence_casco.py", "pacote/validar_pote_v2.py",
                      "LEITURA_DE_COMPATIBILIDADE", "PUBLISHED_AT", "USO_EXIGE_TEMPO", "SERIE_MEDIDA",
                      "LOCATION_SOURCE", "D97", "D112"):
            self.assertIn(termo, doc)


class K_FixturesSinteticas(unittest.TestCase):

    def test_K1_sinteticas_e_ditas(self):
        for f in (V2U, R6):
            c = corrida(f)
            self.assertIs(c["SINTETICA"], True)
            self.assertIn("SINTETICO DECLARADO", c["_AVISO"])
            for s in re.findall(r'"(?:[A-Z_]*_ID|OBJETO_ID|CORRIDA_UPSTREAM)": "([^"]*)"', f.read_text(encoding="utf-8")):
                self.assertTrue(s.startswith("SINT-"), (f.name, s))

    def test_K2_o_pote_do_casco_e_gerado_desta_corrida(self):
        """python3 pacote/pote_intelligence_casco.py tests/fixtures/pote/CORRIDA-SINTETICA-V2-UNICO.json \\
                   tests/fixtures/pote/POTE-SINTETICO-V2-UNICO.json"""
        self.assertEqual(json.loads(POTE_V2U.read_text(encoding="utf-8")), P.adaptar(corrida()))

    def test_K3_a_r6_equivalente_e_a_que_o_script_gera(self):
        import medir_recusas_r6 as MR
        self.assertEqual(corrida(R6), json.loads(json.dumps(MR.fixture())))
        entrada = {k: len(v) for k, v in corrida(R6)["ITENS_POR_FERRAMENTA"].items()}
        self.assertEqual(entrada, {"archive": 23, "windows": 2, "science": 2, "market": 6, "future": 10,
                                   "portfolio": 3, "sources": 47})


if __name__ == "__main__":
    unittest.main()
