#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O POTE UNICO (POTE_INTELLIGENCE_CASCO/v2), ATACADO — missao POTE-UNICO.

    python3 -m unittest tests.test_pote_intelligence_casco -v

⚠️ DADO SINTETICO DECLARADO. A corrida vem de
tests/fixtures/pote/CORRIDA-SINTETICA-POTE.json: `SINTETICA: true`, todo id
comeca por `SINT-`, e um aviso no proprio ficheiro diz que e inventada. Nenhum
valor dela e real, nem entra no portal: o pote que o casco testa
(tests/fixtures/pote/POTE-SINTETICO.json) e gerado DESTA corrida, e o teste K2
reprova se os dois divergirem.
"""
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "pacote", RAIZ / "motor", RAIZ / "provas", RAIZ / "tests"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pote_intelligence_casco as P                           # noqa: E402
import ponte_intelligence_casco as V1                         # noqa: E402

NAO_SEI = P.NAO_SEI
FIXTURE = RAIZ / "tests" / "fixtures" / "pote" / "CORRIDA-SINTETICA-POTE.json"
POTE_FIXTURE = RAIZ / "tests" / "fixtures" / "pote" / "POTE-SINTETICO.json"


def corrida():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def objs(pote, comp):
    return pote["COMPARTIMENTOS"][comp]["OBJETOS"]


def ids(pote, comp):
    return [o["OBJETO_ID"] for o in objs(pote, comp)]


def motivos(pote):
    return {(r["COMPARTIMENTO"], r["OBJETO_ID"], r["MOTIVO"]) for r in pote["RECUSADOS"]}


class A_UmPotePorCorrida(unittest.TestCase):

    def setUp(self):
        self.pote = P.adaptar(corrida())

    def test_A1_cabecalho_da_corrida(self):
        self.assertEqual(self.pote["SCHEMA"], "POTE_INTELLIGENCE_CASCO/v2")
        self.assertEqual(self.pote["INTELLIGENCE_RUN_ID"], "SINT-IR-POTE-0001")
        self.assertEqual(self.pote["SOURCE_HEAD"], "SINT-0000000000000000000000000000000000000000")
        self.assertEqual(self.pote["CORTE"], "2026-09-27T00:00:00+00:00")
        self.assertIs(self.pote["CORRIDA_SINTETICA"], True)
        self.assertEqual(self.pote["ENTRADA"], "CORRIDA")

    def test_A2_sem_source_head_ou_corte_fica_nao_sei_a_vista_e_sem_run_id_recusa(self):
        c = corrida()
        del c["SOURCE_HEAD"], c["CORTE"]
        pote = P.adaptar(c)
        self.assertEqual((pote["SOURCE_HEAD"], pote["CORTE"]), (NAO_SEI, NAO_SEI))
        c["INTELLIGENCE_RUN_ID"] = ""
        with self.assertRaises(P.LeiViolada):
            P.adaptar(c)

    def test_A3_os_doze_compartimentos_do_dono(self):
        self.assertEqual(list(self.pote["COMPARTIMENTOS"]),
                         ["meeting", "future", "windows", "market", "voices", "competitors", "science",
                          "portfolio", "archive", "sources", "field", "casa"])

    def test_A4_as_vistas_do_casco_existem_e_nenhuma_tem_dois_donos(self):
        html = (RAIZ / "italia-portale" / "client" / "portale.html").read_text(encoding="utf-8")
        ammesse = set(re.findall(r"'([a-z]+)'", re.search(r"const AMMESSE = \[([^\]]*)\]", html).group(1)))
        vistas = [v for m in P.COMPARTIMENTOS.values() for v in m["VISTAS"]]
        self.assertEqual(len(vistas), len(set(vistas)))
        self.assertTrue(set(vistas) <= ammesse, set(vistas) - ammesse)
        # toda vista-ferramenta do casco no ar tem um compartimento; so as de operacao ficam de fora
        self.assertEqual(ammesse - set(vistas), set(V1.VISTAS_QUE_NAO_SAO_FERRAMENTA))

    def test_A5_marca_em_tres_niveis(self):
        self.assertEqual(self.pote["MARCA"], P.MARCA)
        for e in self.pote["COMPARTIMENTOS"].values():
            self.assertEqual(e["MARCA"], P.MARCA)
            for o in e["OBJETOS"]:
                self.assertEqual((o["MARCA"], o["NAO_PARA_CLIENTE"], o["ESTADO"]),
                                 (P.MARCA, True, "EXPERIMENTAL_CANDIDATE"))


class B_EspecieEProvaAteAoRaw(unittest.TestCase):

    def setUp(self):
        self.pote = P.adaptar(corrida())

    def test_B1_todo_objeto_tem_especie_e_quem_a_disse(self):
        for e in self.pote["COMPARTIMENTOS"].values():
            for o in e["OBJETOS"]:
                self.assertIn(o["ESPECIE"], P.ESPECIES)
                self.assertIn(o["ESPECIE"], e["ESPECIES_ADMITIDAS"])
        w = objs(self.pote, "windows")[0]
        self.assertEqual((w["ESPECIE"], w["ESPECIE_DITA_POR"]), ("SINAL", "CONTRATO_V1"))
        op = objs(self.pote, "meeting")[0]
        self.assertEqual((op["ESPECIE"], op["ESPECIE_DITA_POR"]), ("OPORTUNIDADE", "INTELLIGENCE"))

    def test_B2_prova_ate_ao_raw_com_url_e_datas_nunca_em_branco(self):
        # AJUSTE DECLARADO (POTE-V2-UNICO, 27/09): a publicacao chama-se PUBLISHED_AT no contrato
        # v2 unico (pedido da missao); PUBLICADO_EM so se le na entrada. Mesma prova, outro nome.
        for e in self.pote["COMPARTIMENTOS"].values():
            for o in e["OBJETOS"]:
                for p in o["PROVA"]:
                    for k in ("ITEM_ID", "RAW_OBSERVATION_ID", "SOURCE_ID", "DOCUMENT_ID"):
                        self.assertTrue(str(p[k]).startswith("SINT-"), (o["OBJETO_ID"], k))
                    for k in ("URL", "PUBLISHED_AT", "COLHIDO_EM", "FACT_TIME", "CORRIDA_UPSTREAM"):
                        self.assertIn(k, p)
                        self.assertNotIn(p[k], ("", None))
                    self.assertEqual(p["INTELLIGENCE_RUN_ID"], "SINT-IR-POTE-0001")

    def test_B3_url_e_datas_vem_da_prova_ou_da_linhagem_que_a_confirmou(self):
        # AJUSTE DECLARADO (POTE-V2-UNICO, 27/09): a publicacao chama-se PUBLISHED_AT no contrato
        # v2 unico (pedido da missao); PUBLICADO_EM so se le na entrada. Mesma prova, outro nome.
        p = objs(self.pote, "meeting")[0]["PROVA"][0]        # a prova nao diz; a LINEAGE diz
        self.assertEqual((p["URL"], p["PUBLISHED_AT"], p["COLHIDO_EM"]),
                         ("https://sint.example/boletim-1", "2026-09-20", "2026-09-21"))
        p = objs(self.pote, "meeting")[1]["PROVA"][0]        # ninguem diz
        self.assertEqual((p["URL"], p["PUBLISHED_AT"], p["FACT_TIME"]), (NAO_SEI, NAO_SEI, NAO_SEI))

    def test_B4_publicacao_nao_vira_tempo_do_facto(self):
        # AJUSTE DECLARADO (POTE-V2-UNICO, 27/09): a publicacao chama-se PUBLISHED_AT no contrato
        # v2 unico (pedido da missao); PUBLICADO_EM so se le na entrada. Mesma prova, outro nome.
        p = objs(self.pote, "windows")[0]["PROVA"][0]
        self.assertEqual(p["PUBLISHED_AT"], "2026-09-10")
        self.assertEqual(p["FACT_TIME"], "2026-09-07/2026-09-13")
        c = corrida()
        del c["ITENS_POR_FERRAMENTA"]["windows"][0]["PROVA"][0]["FACT_TIME"]
        p = objs(P.adaptar(c), "windows")[0]["PROVA"][0]
        self.assertEqual((p["PUBLISHED_AT"], p["FACT_TIME"]), ("2026-09-10", NAO_SEI))


class C_VazioComOPorque(unittest.TestCase):

    def test_C1_cada_vazio_diz_porque(self):
        pote = P.adaptar(corrida())
        porque = {k: e["PORQUE_VAZIO"] for k, e in pote["COMPARTIMENTOS"].items() if not e["OBJETOS"]}
        self.assertEqual(porque, {"market": P.SEM_OBJETOS, "voices": P.SEM_OBJETOS,
                                  "competitors": P.SEM_OBJETOS, "science": P.SEM_OBJETOS,
                                  "portfolio": P.SEM_OBJETOS,
                                  "field": P.SEM_CONTRATO, "casa": P.SEM_CONTRATO})
        for k, e in pote["COMPARTIMENTOS"].items():
            if not e["OBJETOS"]:
                self.assertEqual(e["ESTADO"], "VAZIO")
                self.assertTrue(e["PORQUE_TEXTO"])
        self.assertIn("nao prova ausencia", pote["COMPARTIMENTOS"]["market"]["PORQUE_TEXTO"])

    def test_C2_compartimento_sem_contrato_recusa_objeto_em_vez_de_o_desenhar(self):
        pote = P.adaptar(corrida())
        self.assertIn(("field", "SINT-FIELD-1", P.SEM_CONTRATO), motivos(pote))
        self.assertEqual(pote["COMPARTIMENTOS"]["field"]["RECUSADOS_AQUI"], 1)

    def test_C3_corrida_que_falhou_esvazia_tudo_com_o_estado(self):
        for estado in ("ERROR", "NOT_RUN", "RUNNING", None):
            c = corrida()
            c["RESULT_STATE"] = estado
            pote = P.adaptar(c)
            for k, e in pote["COMPARTIMENTOS"].items():
                self.assertEqual(e["OBJETOS"], [], (estado, k))
                esperado = P.SEM_CONTRATO if k in ("field", "casa") else "CORRIDA_" + (estado or NAO_SEI).replace(" ", "_")
                self.assertEqual(e["PORQUE_VAZIO"], esperado)

    def test_C4_lacunas_verbatim_no_compartimento_certo(self):
        pote = P.adaptar(corrida())
        self.assertEqual([g["GAP"] for g in pote["COMPARTIMENTOS"]["market"]["LACUNAS"]],
                         ["SINT: nenhum preco com unidade nesta corrida"])
        self.assertEqual([g["REQUIREMENT_ID"] for g in pote["LACUNAS_SEM_COMPARTIMENTO"]], ["SINT-REQ-1"])


class D_RadarFuturo_P2_P5(unittest.TestCase):

    def setUp(self):
        self.pote = P.adaptar(corrida())

    def test_D1_facto_futuro_bloqueado_por_desenho_vai_ao_radar_futuro_como_especie_propria(self):
        self.assertEqual(ids(self.pote, "future"), ["SINT-FUT-1"])
        f = objs(self.pote, "future")[0]
        self.assertEqual(f["ESPECIE"], "FATO_PRESENTE_SOBRE_O_FUTURO")
        self.assertEqual(f["CHAVES"]["FACT_TIME"], "2027-03")
        self.assertEqual(f["PROVA"][0]["URL"], "https://sint.example/decreto-2027")

    def test_D2_nunca_como_oportunidade(self):
        self.assertIn(("future", "SINT-OP-NO-FUTURO", "ESPECIE_FORA_DO_COMPARTIMENTO"), motivos(self.pote))
        self.assertIn(("meeting", "SINT-FUT-NO-MEETING", "ESPECIE_FORA_DO_COMPARTIMENTO"), motivos(self.pote))
        for comp in ("meeting", "windows", "market"):
            self.assertNotIn("FATO_PRESENTE_SOBRE_O_FUTURO", P.COMPARTIMENTOS[comp]["ESPECIES"])
        self.assertEqual(P.COMPARTIMENTOS["future"]["ESPECIES"], ("FATO_PRESENTE_SOBRE_O_FUTURO",))

    def test_D3_so_o_bloqueio_por_desenho_e_nenhum_outro(self):
        self.assertIn(("future", "SINT-FUT-SEM-FONTE", "ITEM_BLOQUEADO_EM_G0"), motivos(self.pote))
        self.assertIn(("future", "SINT-FUT-CAPTURA", "ITEM_BLOQUEADO_EM_G0"), motivos(self.pote))

    def test_D4_o_bloqueio_por_desenho_nao_prova_um_sinal(self):
        c = corrida()
        c["ITENS_POR_FERRAMENTA"] = {"windows": [{
            "OBJETO_ID": "SINT-SG-5", "ESPECIE": "SINAL", "ESTADO": "EXPERIMENTAL_CANDIDATE", "CHAVES": {},
            "PROVA": [c["ITENS_POR_FERRAMENTA"]["future"][0]["PROVA"][0]]}]}
        pote = P.adaptar(c)
        self.assertEqual(ids(pote, "windows"), [])
        self.assertIn(("windows", "SINT-SG-5", "ITEM_BLOQUEADO_EM_G0"), motivos(pote))

    def test_D5_radarfuturo_e_sinonimo_de_nome_nao_de_especie(self):
        c = corrida()
        c["ITENS_POR_FERRAMENTA"] = {"radarfuturo": c["ITENS_POR_FERRAMENTA"]["future"]}
        pote = P.adaptar(c)
        self.assertEqual(ids(pote, "future"), ["SINT-FUT-1"])
        self.assertIn(("future", "SINT-OP-NO-FUTURO", "ESPECIE_FORA_DO_COMPARTIMENTO"), motivos(pote))


class E_RegistroEArchivio_P3(unittest.TestCase):

    def setUp(self):
        self.pote = P.adaptar(corrida())

    def test_E1_rendimento_de_fonte_no_registro(self):
        self.assertEqual(ids(self.pote, "sources"), ["SINT-REND-3"])
        r = objs(self.pote, "sources")[0]
        self.assertEqual(r["ESPECIE"], "RENDIMENTO_DE_FONTE")
        self.assertEqual(r["CHAVES"], {"SOURCE_ID": "SINT-SRC-3", "ITENS_LIDOS": 2,
                                       "ITENS_QUE_PASSARAM_G0": 2, "OBJETOS_PRODUZIDOS": 1})

    def test_E2_rendimento_provado_por_outra_fonte_e_recusado(self):
        self.assertIn(("sources", "SINT-REND-MISTO", "PROVA_DE_OUTRA_FONTE"), motivos(self.pote))
        c = corrida()
        del c["ITENS_POR_FERRAMENTA"]["sources"][0]["CHAVES"]["SOURCE_ID"]
        self.assertIn(("sources", "SINT-REND-3", "RENDIMENTO_SEM_FONTE"), motivos(P.adaptar(c)))

    def test_E3_o_pote_nao_calcula_rendimento(self):
        c = corrida()
        c["ITENS_POR_FERRAMENTA"]["sources"][0]["CHAVES"] = {"SOURCE_ID": "SINT-SRC-3"}
        r = objs(P.adaptar(c), "sources")[0]
        self.assertEqual(r["CHAVES"]["ITENS_LIDOS"], NAO_SEI)
        self.assertEqual(r["CHAVES"]["OBJETOS_PRODUZIDOS"], NAO_SEI)

    def test_E4_archivio_guarda_os_objetos_produzidos_sem_mudar_especie(self):
        self.assertEqual(ids(self.pote, "archive"), ["SINT-SG-2", "SINT-SG-8"])
        self.assertTrue(all(o["ESPECIE"] == "SINAL" for o in objs(self.pote, "archive")))
        self.assertNotIn("RENDIMENTO_DE_FONTE", P.COMPARTIMENTOS["archive"]["ESPECIES"])
        self.assertEqual(P.COMPARTIMENTOS["archive"]["VISTAS"], ("archive", "future"))

    def test_E6_o_mesmo_objeto_conta_uma_vez_no_compartimento(self):
        c = corrida()
        c["ITENS_POR_FERRAMENTA"]["archive"].append(copy.deepcopy(c["ITENS_POR_FERRAMENTA"]["archive"][0]))
        pote = P.adaptar(c)
        self.assertEqual(ids(pote, "archive"), ["SINT-SG-2", "SINT-SG-8"])
        self.assertIn(("archive", "SINT-SG-2", "DUPLICADO_NO_COMPARTIMENTO"), motivos(pote))

    def test_E5_especie_desconhecida_e_recusada(self):
        c = corrida()
        c["ITENS_POR_FERRAMENTA"]["archive"][0]["ESPECIE"] = "PEDIDO"
        self.assertIn(("archive", "SINT-SG-2", "ESPECIE_DESCONHECIDA"), motivos(P.adaptar(c)))


class F_ForaDoContrato_P4(unittest.TestCase):

    def test_F1_fact_location_viaja_como_fact_location(self):
        w = objs(P.adaptar(corrida()), "windows")[0]
        self.assertEqual(w["FORA_DO_CONTRATO"], {"FACT_LOCATION": "SINT-Puglia"})
        self.assertEqual(w["CHAVES"]["REGION_ID"], NAO_SEI)
        self.assertIn("REGION_ID", w["CHAVES_NAO_SEI"])

    def test_F2_valor_inventado_viaja_a_parte_e_nunca_nas_chaves(self):
        op = objs(P.adaptar(corrida()), "meeting")[0]
        self.assertEqual(op["FORA_DO_CONTRATO"], {"SCORE_INVENTADO": 99})
        self.assertNotIn("SCORE_INVENTADO", op["CHAVES"])

    def test_F3_o_pote_nao_cria_valor(self):
        c = corrida()
        pote = P.adaptar(c)
        for comp, lista in c["ITENS_POR_FERRAMENTA"].items():
            dados = {o.get("OBJETO_ID") or o.get("SIGNAL_ID"): o["CHAVES"] for o in lista}
            for o in objs(pote, P.SINONIMOS.get(comp, comp)):
                for k, v in o["CHAVES"].items():
                    self.assertTrue(v == NAO_SEI or v == dados[o["OBJETO_ID"]].get(k), (comp, k, v))


class G_Linhagem_P1(unittest.TestCase):

    def test_G1_item_em_duas_corridas_upstream_sem_dizer_qual_e_ambiguo(self):
        c = corrida()
        c["LINEAGE"].append(dict(c["LINEAGE"][1], CORRIDA_UPSTREAM="SINT-UP-B"))
        p = c["ITENS_POR_FERRAMENTA"]["meeting"][1]["PROVA"][0]
        del p["CORRIDA_UPSTREAM"]
        pote = P.adaptar(c)
        self.assertIn(("meeting", "SINT-SG-2", "PROVA_AMBIGUA"), motivos(pote))
        p["CORRIDA_UPSTREAM"] = "SINT-UP-B"
        self.assertIn("SINT-SG-2", ids(P.adaptar(c), "meeting"))

    def test_G2_a_regra_de_prova_e_a_da_ponte(self):
        """Uma regra de prova so: o pote chama a da ponte v1, nao tem uma copia."""
        src = (RAIZ / "pacote" / "pote_intelligence_casco.py").read_text(encoding="utf-8")
        self.assertIn("V1.conferir_prova(", src)
        self.assertNotIn("def conferir_prova", src)


class H_OPayloadV1(unittest.TestCase):

    def _payload_v1(self):
        import test_ponte_intelligence_casco as T1
        return V1.adaptar(T1.corrida_sintetica())

    def test_H1_payload_v1_vira_pote_com_o_que_a_v1_nao_levava_em_nao_sei(self):
        pote = P.ler_entrada(self._payload_v1())
        self.assertEqual(pote["ENTRADA"], "PAYLOAD_V1")
        self.assertEqual((pote["SOURCE_HEAD"], pote["CORTE"]), (NAO_SEI, NAO_SEI))
        self.assertEqual(ids(pote, "meeting"), ["SINT-SG-1"])
        o = objs(pote, "meeting")[0]
        self.assertEqual((o["ESPECIE"], o["ESPECIE_DITA_POR"]), ("SINAL", "CONTRATO_V1"))
        self.assertEqual(o["PROVA_CONFERIDA_POR"], V1.CONTRATO)
        self.assertEqual(o["PROVA"][0]["URL"], NAO_SEI)
        self.assertEqual(o["FORA_DO_CONTRATO"], {"SCORE_INVENTADO": 99})
        for comp in ("archive", "sources", "future"):
            self.assertEqual(pote["COMPARTIMENTOS"][comp]["PORQUE_VAZIO"], P.ENTRADA_V1_SEM_VAGA)
        self.assertEqual(pote["COMPARTIMENTOS"]["field"]["PORQUE_VAZIO"], P.SEM_CONTRATO)

    def test_H2_etichette_e_portfolio_sao_um_compartimento_e_o_sinal_conta_uma_vez(self):
        import test_ponte_intelligence_casco as T1
        c = T1.corrida_sintetica()
        s = {"SIGNAL_ID": "SINT-SG-L", "ESTADO": "EXPERIMENTAL_CANDIDATE",
             "CHAVES": {"PRODUCT_ID": "SINT-PROD-1"}, "PROVA": [T1._prova(1)]}
        c["ITENS_POR_FERRAMENTA"] = {"etichette": [s], "portfolio": [dict(s)]}
        pote = P.ler_entrada(V1.adaptar(c))
        self.assertEqual(ids(pote, "portfolio"), ["SINT-SG-L"])
        self.assertIn(("portfolio", "SINT-SG-L", "DUPLICADO_NO_COMPARTIMENTO"), motivos(pote))

    def test_H4_o_future_da_v1_era_o_archivio_segnali(self):
        """Na v1, `future` era a vista «Archivio segnali»; na v2 ela le `archive`.
        O que a v1 recusou la fica contado no Archivio, nao no Radar Futuro."""
        import test_ponte_intelligence_casco as T1
        c = T1.corrida_sintetica()
        c["ITENS_POR_FERRAMENTA"] = {"future": [{"SIGNAL_ID": "SINT-SG-F", "ESTADO": "EXPERIMENTAL_CANDIDATE",
                                                 "CHAVES": {}, "PROVA": [T1._prova(1)]}]}
        pote = P.ler_entrada(V1.adaptar(c))
        self.assertIn(("archive", "SINT-SG-F", "FERRAMENTA_SEM_CONTRATO_D84"), motivos(pote))
        self.assertEqual(pote["COMPARTIMENTOS"]["archive"]["RECUSADOS_AQUI"], 1)
        self.assertEqual(pote["COMPARTIMENTOS"]["future"]["RECUSADOS_AQUI"], 0)

    def test_H3_payload_v1_adulterado_nao_vira_pote(self):
        pl = self._payload_v1()
        del pl["FERRAMENTAS"]["meeting"]["CARTOES"][0]["MARCA"]
        with self.assertRaises(P.LeiViolada):
            P.ler_entrada(pl)


class I_AConferenciaReprova(unittest.TestCase):

    def setUp(self):
        self.pote = P.adaptar(corrida())
        self.assertEqual(P.conferir_pote(self.pote), [])

    def _reprova(self, mexer):
        pote = copy.deepcopy(self.pote)
        mexer(pote)
        self.assertTrue(P.conferir_pote(pote))

    def test_I1_marca(self):
        self._reprova(lambda p: p.pop("MARCA"))
        self._reprova(lambda p: p["COMPARTIMENTOS"]["meeting"]["OBJETOS"][0].pop("MARCA"))

    def test_I2_vazio_sem_porque(self):
        self._reprova(lambda p: p["COMPARTIMENTOS"]["market"].__setitem__("PORQUE_VAZIO", None))
        self._reprova(lambda p: p["COMPARTIMENTOS"]["market"].__setitem__("PORQUE_TEXTO", ""))

    def test_I3_oportunidade_no_radar_futuro(self):
        self._reprova(lambda p: p["COMPARTIMENTOS"]["future"]["OBJETOS"][0].__setitem__("ESPECIE", "OPORTUNIDADE"))

    def test_I4_prova_sem_raw_ou_url_escondida_ou_de_outra_corrida(self):
        # AJUSTE DECLARADO (POTE-V2-UNICO, 27/09): a publicacao chama-se PUBLISHED_AT no contrato
        # v2 unico (pedido da missao); PUBLICADO_EM so se le na entrada. Mesma prova, outro nome.
        pr = lambda p: p["COMPARTIMENTOS"]["meeting"]["OBJETOS"][1]["PROVA"][0]  # noqa: E731
        self._reprova(lambda p: pr(p).__setitem__("RAW_OBSERVATION_ID", ""))
        self._reprova(lambda p: pr(p).__setitem__("URL", ""))
        self._reprova(lambda p: pr(p).pop("PUBLISHED_AT"))
        self._reprova(lambda p: pr(p).__setitem__("INTELLIGENCE_RUN_ID", "SINT-IR-OUTRA"))

    def test_I5_cabecalho(self):
        self._reprova(lambda p: p.pop("CORTE"))
        self._reprova(lambda p: p.__setitem__("SOURCE_HEAD", ""))
        self._reprova(lambda p: p.__setitem__("SCHEMA", V1.CONTRATO))

    def test_I6_objeto_em_compartimento_sem_contrato(self):
        def m(p):
            p["COMPARTIMENTOS"]["casa"]["OBJETOS"] = [p["COMPARTIMENTOS"]["meeting"]["OBJETOS"][0]]
        self._reprova(m)


class J_ASaida(unittest.TestCase):

    def test_J1_so_um_destino_dentro_do_portal(self):
        cliente = RAIZ / "italia-portale" / "client"
        self.assertTrue(P.destino_permitido(cliente / "sintonia-pote.js"))
        for outro in (cliente / "sintonia-pote.json", cliente / "italy-demo-data.js",
                      RAIZ / "italia-portale" / "sintonia-pote.js"):
            self.assertFalse(P.destino_permitido(outro), outro)
        self.assertEqual(P.main([str(FIXTURE), str(cliente / "outro.js")]), 3)
        self.assertFalse((cliente / "outro.js").exists())

    def test_J2_o_js_e_o_global_que_o_casco_le(self):
        with tempfile.TemporaryDirectory() as d:
            saida = Path(d) / "sintonia-pote.js"
            self.assertEqual(P.main([str(FIXTURE), str(saida)]), 0)
            texto = saida.read_text(encoding="utf-8")
        self.assertTrue(texto.startswith("/* GERADO"))
        self.assertIn("window.SINTONIA_POTE = ", texto)
        self.assertIn("FORA DO GIT E DO DEPLOY", texto)

    def test_J3_o_pote_fica_fora_do_git_e_do_deploy(self):
        self.assertIn("sintonia-pote.js",
                      (RAIZ / "italia-portale" / "client" / ".gitignore").read_text(encoding="utf-8").split("\n"))
        self.assertIn("/italia-portale/client/sintonia-pote.js",
                      (RAIZ / ".vercelignore").read_text(encoding="utf-8").split("\n"))
        r = subprocess.run(["git", "-C", str(RAIZ), "check-ignore", "-q",
                            "italia-portale/client/sintonia-pote.js"])
        self.assertEqual(r.returncode, 0, "o git nao ignora sintonia-pote.js")


class K_FixtureSintetica(unittest.TestCase):

    def test_K1_a_fixture_e_sintetica_e_diz_o(self):
        c = corrida()
        self.assertIs(c["SINTETICA"], True)
        self.assertIn("SINTETICO DECLARADO", c["_AVISO"])
        for s in re.findall(r'"(?:[A-Z_]*_ID|OBJETO_ID|SIGNAL_ID|CORRIDA_UPSTREAM)": "([^"]*)"',
                            FIXTURE.read_text(encoding="utf-8")):
            self.assertTrue(s.startswith("SINT-") or s == NAO_SEI, s)

    def test_K2_o_pote_do_teste_do_casco_e_o_desta_corrida(self):
        """tests/fixtures/pote/POTE-SINTETICO.json e gerado, nao escrito a mao:
        python3 pacote/pote_intelligence_casco.py tests/fixtures/pote/CORRIDA-SINTETICA-POTE.json \\
                tests/fixtures/pote/POTE-SINTETICO.json"""
        self.assertEqual(json.loads(POTE_FIXTURE.read_text(encoding="utf-8")), P.adaptar(corrida()))


class L_OCascoLeOPote(unittest.TestCase):
    """As provas do lado do portal (tests/test_pote_no_casco.mjs), daqui."""

    def test_L1_o_casco_desenha_o_pote_com_precedencia_e_sem_regra_de_cruzamento(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "FALTA DEPENDENCIA: node (as provas do casco sao em JavaScript)")
        r = subprocess.run([node, str(RAIZ / "tests" / "test_pote_no_casco.mjs")], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
