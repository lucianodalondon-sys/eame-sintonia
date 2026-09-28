# -*- coding: utf-8 -*-
"""CHAVE-PROBLEMA (27/09) — o PROBLEMA como chave da Collection, no contrato PROBLEMA/v1.

    python3 -m unittest tests.test_chave_problema -v

O dono da FORMA e `leis/afirmacao_da_fonte.py` (CONTRATO_PROBLEMA); quem a PREENCHE e um so,
`leis/boletim_do_campo.declarar_problema`, chamado pela porta (`admissao.problema_da_chave`); quem a LE
(`motor/cap_win.par_em_campo`, `motor/motor_das_capacidades._objeto_do_futuro`) nao volta ao texto para a
refazer. O reprocesso da Sala (`admissao/reprocessar_problema.py`) corre numa COPIA, a seco.

Todo texto daqui e SINTETICO (frases curtas no feitio dos boletins T3 e dos estudos T5). Sem rede, sem banco.
"""
import ast
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "admissao", RAIZ / "leis", RAIZ / "motor"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import afirmacao_da_fonte as AF  # noqa: E402
import boletim_do_campo as BC  # noqa: E402
import cap_win as W  # noqa: E402
import corrida_da_inteligencia as CI  # noqa: E402
import reprocessar_problema as RP  # noqa: E402

NS = "NAO SEI"
HOJE = date(2026, 9, 27)

# ── os textos (SINTETICOS) ───────────────────────────────────────────────────
NO_TEXTO = ("Bollettino fitosanitario n. 38 [SINTETICO]\nOLIVO\n"
            "Si registrano catture di mosca delle olive (Bactrocera oleae) in aumento nelle trappole.\n")
SO_NO_CABECALHO = ("Bollettino fitosanitario n. 38 [SINTETICO]\n• Mosca delle olive (Bactrocera oleae)\n"
                   "Le catture sono in aumento; intervenire al superamento della soglia del 10%.\n")
SO_NO_TITULO = ("Mosca delle olive: bollettino n. 38 [SINTETICO]\n"
                "Le catture sono in aumento nelle trappole della zona.\n")
CABECALHO_E_TEXTO = ("Bollettino fitosanitario n. 38 [SINTETICO]\n• Mosca delle olive\n"
                     "Nella zona costiera le catture di mosca delle olive sono in aumento.\n")
DUAS_PRAGAS = ("Bollettino fitosanitario n. 38 [SINTETICO]\nOLIVO\n"
               "Catture di mosca delle olive in aumento. Presenza di margaronia sui germogli.\n")
OUTRA_NO_MEIO = ("Bollettino fitosanitario n. 38 [SINTETICO]\n• Mosca delle olive\n"
                 "Segnalata la margaronia sui germogli; intervenire al superamento della soglia.\n")
CINCO_NOMES = ("Bollettino fitosanitario n. 38 [SINTETICO]\nOLIVO\n"
               "Mosca delle olive (Bactrocera oleae): catture in aumento.\n"
               "La mosca dell'olivo e la mosca dell'oliva sono la stessa; mosca dell’olivo in tutte le zone.\n")
SO_AUSENTE = ("Bollettino fitosanitario n. 38 [SINTETICO]\nACTINIDIA\n"
              "CIMICE ASIATICA (Halyomorpha halys); Non Presente\n")
PARECIDO = ("Bollettino fitosanitario n. 38 [SINTETICO]\nOLIVO\n"
            "Catture di Bactrocera olea e di moscerini in aumento; mosca generica nelle trappole.\n")
NOME_COMUM = ("Bollettino fitosanitario n. 38 [SINTETICO]\nOLIVO\n"
              "Catture di mosca delle olive in aumento nelle trappole.\n")
ESTUDO_DOIS_EPPO = ("[SINTETICA] Control of Plasmopara viticola and Phytophthora infestans.\n"
                    "Abstract: downy mildew was assessed in field trials.")


def _p(texto):
    return BC.problema_do_boletim(texto)


def _contrato(valor="mosca dell'olivo", veio="TEXT", base="Catture di mosca delle olive in aumento.",
              forma="mosca delle olive", **kw):
    b = {"CONTRATO": AF.CONTRATO_PROBLEMA, "VALOR": valor, "VEIO_DE": veio, "BASE": base, "FORMA": forma,
         "CODIGO": {"SISTEMA": "NOME_CANONICO", "VALOR": valor, "TABELA": "SINTETICO"}}
    b.update(kw)
    return b


# ═══════════════════════════════════════════════════════════════════════════
# A · O CONTRATO (a forma, e so a forma)
# ═══════════════════════════════════════════════════════════════════════════
class A_OContrato(unittest.TestCase):
    TXT = "Bollettino [SINTETICO]\nCatture di mosca delle olive in aumento.\n"

    def ok(self, b, texto=TXT):
        return AF.problema_conforme(b, texto)[0]

    def test_A1_o_bloco_certo_passa_e_da_o_nome(self):
        self.assertEqual(("mosca dell'olivo", "conforme PROBLEMA/v1"), AF.problema_da_chave(_contrato(), self.TXT))

    def test_A2_lista_nunca_e_valor(self):
        self.assertFalse(self.ok(_contrato(valor=["mosca dell'olivo", "margaronia"])))

    def test_A3_veio_de_fora_do_vocabulario(self):
        for v in ("SINTETICO", "ESCRITO", "SPAN", "PARAGRAPH_CONTEXT", "item.texto", NS):
            self.assertFalse(self.ok(_contrato(veio=v)), v)
        self.assertEqual(("TEXT", "SECTION_HEADER", "DOCUMENT_TITLE"), AF.VEIO_DE_DO_PROBLEMA)

    def test_A4_base_que_o_texto_nao_tem_e_praga_inferida(self):
        ok, porque = AF.problema_conforme(_contrato(base="Catture di mosca delle olive in calo."), self.TXT)
        self.assertFalse(ok)
        self.assertIn("inferida", porque)

    def test_A5_a_forma_tem_de_estar_na_base(self):
        self.assertFalse(self.ok(_contrato(forma="margaronia")))

    def test_A6_sem_contrato_nao_e_chave(self):
        velho = {"VALOR": "Bactrocera oleae", "VEIO_DE": "ESCRITO", "BASE": "SINTETICO · escrito no boletim"}
        self.assertEqual(None, AF.problema_da_chave(velho, self.TXT)[0])
        self.assertIn("fora do contrato", AF.problema_da_chave(velho, self.TXT)[1])

    def test_A7_nao_sei_so_com_porque(self):
        self.assertFalse(self.ok({"CONTRATO": AF.CONTRATO_PROBLEMA, "VALOR": NS}))
        b = {"CONTRATO": AF.CONTRATO_PROBLEMA, "VALOR": NS, "PORQUE": "duas pragas"}
        self.assertTrue(self.ok(b))
        self.assertEqual(None, AF.problema_da_chave(b, self.TXT)[0])

    def test_A8_eppo_so_com_prova_escrita_no_texto(self):
        cod = {"SISTEMA": "EPPO", "VALOR": "DACUOL", "PROVA": "Bactrocera oleae"}
        self.assertFalse(self.ok(_contrato(CODIGO=cod)))            # o texto nao escreve o binomio
        self.assertTrue(self.ok(_contrato(CODIGO=cod), self.TXT + "Bactrocera oleae.\n"))
        self.assertFalse(self.ok(_contrato(CODIGO=dict(cod, VALOR="mosca")), self.TXT + "Bactrocera oleae.\n"))

    def test_A9_nome_canonico_e_o_proprio_valor_com_tabela(self):
        self.assertFalse(self.ok(_contrato(CODIGO={"SISTEMA": "NOME_CANONICO", "VALOR": "outra",
                                                   "TABELA": "x"})))
        self.assertFalse(self.ok(_contrato(CODIGO={"SISTEMA": "NOME_CANONICO", "VALOR": "mosca dell'olivo"})))


# ═══════════════════════════════════════════════════════════════════════════
# B · O PRODUTOR UNICO (leis/boletim_do_campo.declarar_problema)
# ═══════════════════════════════════════════════════════════════════════════
class B_OProdutor(unittest.TestCase):

    def conforme(self, p, texto):
        self.assertEqual((True, "conforme PROBLEMA/v1"), AF.problema_conforme(p, texto))

    def test_B1_nome_na_frase_e_TEXT_com_o_trecho_literal_e_o_EPPO_escrito(self):
        p = _p(NO_TEXTO)
        self.assertEqual(("mosca dell'olivo", "TEXT", "SPAN"), (p["VALOR"], p["VEIO_DE"], p["ENTITY_SOURCE"]))
        self.assertIn(p["BASE"], NO_TEXTO)
        self.assertEqual(("EPPO", "DACUOL", "Bactrocera oleae"),
                         (p["CODIGO"]["SISTEMA"], p["CODIGO"]["VALOR"], p["CODIGO"]["PROVA"]))
        self.conforme(p, NO_TEXTO)

    def test_B2_praga_do_cabecalho_nao_vira_praga_do_trecho(self):
        p = _p(SO_NO_CABECALHO)
        self.assertEqual("mosca dell'olivo", p["VALOR"])
        self.assertEqual("SECTION_HEADER", p["VEIO_DE"])
        self.assertEqual("SECTION_TITLE", p["ENTITY_SOURCE"])
        self.assertEqual("• Mosca delle olive (Bactrocera oleae)", p["BASE"])
        self.conforme(p, SO_NO_CABECALHO)

    def test_B3_nome_so_no_titulo_e_DOCUMENT_TITLE(self):
        p = _p(SO_NO_TITULO)
        self.assertEqual(("mosca dell'olivo", "DOCUMENT_TITLE"), (p["VALOR"], p["VEIO_DE"]))
        self.assertEqual("Mosca delle olive: bollettino n. 38 [SINTETICO]", p["BASE"])
        self.conforme(p, SO_NO_TITULO)

    def test_B4_no_cabecalho_e_no_texto_a_base_e_a_do_texto_e_as_duas_ficam_a_vista(self):
        p = _p(CABECALHO_E_TEXTO)
        self.assertEqual("TEXT", p["VEIO_DE"])
        (c,) = p["CANDIDATOS"]
        self.assertEqual(["SECTION_HEADER", "TEXT"], sorted(o["VEIO_DE"] for o in c["OCORRENCIAS"]))

    def test_B5_duas_pragas_no_item_e_NAO_SEI_com_os_candidatos(self):
        for t in (DUAS_PRAGAS, OUTRA_NO_MEIO):
            p = _p(t)
            self.assertEqual(NS, p["VALOR"], t)
            self.assertIn("D112", p["PORQUE"])
            self.assertEqual({"mosca dell'olivo", "margaronia"}, {c["NOME"] for c in p["CANDIDATOS"]})
            self.assertIsNone(AF.problema_da_chave(p, t)[0])

    def test_B6_cinco_nomes_da_mesma_mosca_sao_uma_praga(self):
        p = _p(CINCO_NOMES)
        self.assertEqual("mosca dell'olivo", p["VALOR"])
        (c,) = p["CANDIDATOS"]
        self.assertGreaterEqual(len({o["FORMA"].lower() for o in c["OCORRENCIAS"]}), 4)
        self.assertEqual("DACUOL", p["CODIGO"]["VALOR"])
        self.conforme(p, CINCO_NOMES)

    def test_B7_praga_ausente_nunca_e_valor(self):
        p = _p(SO_AUSENTE)
        self.assertEqual(NS, p["VALOR"])
        self.assertEqual(["cimice asiatica"], p["AUSENTES"])
        self.assertEqual([], p["CANDIDATOS"])

    def test_B8_nada_por_semelhanca(self):
        p = _p(PARECIDO)                       # «Bactrocera olea», «moscerini», «mosca» sozinha
        self.assertEqual(NS, p["VALOR"])
        self.assertEqual([], p["CANDIDATOS"])
        p = _p(NOME_COMUM)                     # nome comum italiano nao cunha EPPO
        self.assertEqual("mosca dell'olivo", p["VALOR"])
        self.assertEqual(("NOME_CANONICO", "mosca dell'olivo"), (p["CODIGO"]["SISTEMA"], p["CODIGO"]["VALOR"]))
        self.assertEqual(NS, p["CODIGO"]["EPPO"])
        self.assertIn("MESMO_PROBLEMA", p["CODIGO"]["TABELA"])
        self.conforme(p, NOME_COMUM)

    def test_B9_dois_binomios_com_codigos_diferentes_nao_escolhem_codigo(self):
        p = adm.problema_da_chave({"texto": ESTUDO_DOIS_EPPO}, "T5")
        self.assertEqual("peronospora", p["VALOR"])
        self.assertEqual("NOME_CANONICO", p["CODIGO"]["SISTEMA"])
        self.assertIn("PHYTIN", p["CODIGO"]["PORQUE_SEM_EPPO"])
        self.assertIn("PLASVI", p["CODIGO"]["PORQUE_SEM_EPPO"])
        self.assertIn("pesquisadores_t6", p["CODIGO"]["TABELA"])   # o nome veio do lexico T6, e diz-se
        self.assertEqual("NOMEADO_NO_ESTUDO", p["ESTADO"])           # CAP-SCI: nomeado, nunca presente
        self.conforme(p, ESTUDO_DOIS_EPPO)


# ═══════════════════════════════════════════════════════════════════════════
# C · A PORTA leva o contrato na janela (sem migracao: a 033 guarda-o)
# ═══════════════════════════════════════════════════════════════════════════
class C_APorta(unittest.TestCase):

    def janela(self, texto, universo):
        item = {"id": "derived:1", "texto": texto, "source_id": "IT-T3-002", "fact_location": NS, "fact_time": NS}
        return adm.janela_para_o_ready(item, adm.decidir(item, universo, corrida="RUN-TESTE"))

    def test_C1_boletim_T3_sai_no_contrato_e_a_porta_e_o_reprocesso_dao_o_mesmo(self):
        j = self.janela(NO_TEXTO, "T3")
        self.assertEqual(AF.CONTRATO_PROBLEMA, j["PROBLEMA"]["CONTRATO"])
        self.assertEqual("mosca dell'olivo", j["PROBLEMA"]["VALOR"])
        self.assertIn("SECOES", j["PROBLEMA"])           # a leitura por secao continua ao lado
        self.assertEqual(j["PROBLEMA"], adm.problema_da_chave({"texto": NO_TEXTO}, "T3"))

    def test_C2_fora_de_boletim_e_estudo_e_NAO_SEI_dito(self):
        j = self.janela(NO_TEXTO, "T10")
        self.assertEqual(NS, j["PROBLEMA"]["VALOR"])
        self.assertIn("universo T10", j["PROBLEMA"]["PORQUE"])
        self.assertTrue(AF.problema_conforme(j["PROBLEMA"], NO_TEXTO)[0])

    def test_C3_as_quatro_chaves_da_033_nao_mudaram(self):
        j = self.janela(NO_TEXTO, "T3")
        for c in adm.QUATRO_CHAVES:
            self.assertTrue({"VALOR", "VEIO_DE", "BASE"} <= set(j[c]), c)
        self.assertEqual(("CULTURA", "REGIAO_DO_FATO", "FASE", "JANELA"), adm.QUATRO_CHAVES)

    def test_C4_a_033_nao_proibe_a_quinta_chave_e_ja_reve_a_janela(self):
        """Por que nao ha migracao: a trava so exige as quatro, e a revisao aceita `janela_declarada`."""
        import glob
        import re
        import sala_de_espera as espera
        sql = Path(glob.glob(str(RAIZ / "supabase" / "migrations" / "033_*.sql"))[0]).read_text(encoding="utf-8")
        trava = re.search(r"constraint janela_declara_as_quatro_chaves\s+check \((.*?)\n      \);", sql, re.S)
        self.assertIsNotNone(trava)
        self.assertNotIn("PROBLEMA", trava.group(1))
        self.assertEqual({"CULTURA", "REGIAO_DO_FATO", "FASE", "JANELA"},
                         set(re.findall(r"\{(\w+),VALOR\}", trava.group(1))))
        self.assertIn("janela_declarada", espera.CAMPOS_REVISIVEIS)
        self.assertIn("coalesce(jd.valor::json, s.janela_declarada)", sql)


# ═══════════════════════════════════════════════════════════════════════════
# D · QUEM LE (cap_win, motor) le a chave — nunca o texto
# ═══════════════════════════════════════════════════════════════════════════
def _item_win(iid, texto, problema, url):
    campo = lambda v: {"VALOR": v, "BASE": "SINTETICO", "VEIO_DE": "SINTETICO"}  # noqa: E731
    return {"MARCA": "SINTETICO", "ITEM_ID": iid, "RAW_OBSERVATION_ID": "RAW-" + iid, "SOURCE_ID": "SRC-" + iid,
            "URL": url, "CAPTURED_AT": "2026-09-25T10:00:00Z", "PUBLISHED_AT": "2026-09-25",
            "FACT_TIME": "2026-09-20/2026-09-24", "FACT_TIME_BASIS": "SINTETICO", "TEXTO": texto,
            "JANELA_DECLARADA": {"CULTURA": campo("olivo"), "PROBLEMA": problema,
                                 "REGIAO_DO_FATO": campo("Puglia"), "FASE": campo(NS), "JANELA": campo(NS)}}


class D_OLeitor(unittest.TestCase):

    def par(self, texto, problema):
        return W.par_em_campo(_item_win("D", texto, problema, "https://d.example/SINTETICO/1"))

    def test_D1_a_chave_do_produtor_vira_ISSUE_ID(self):
        par, falta = self.par(NO_TEXTO, _p(NO_TEXTO))
        self.assertEqual([], falta)
        self.assertEqual("mosca dell'olivo", par["ISSUE_ID"])

    def test_D2_sem_chave_nao_ha_par_mesmo_com_a_praga_no_texto(self):
        for prob in (_p(DUAS_PRAGAS), None, {"VALOR": "mosca dell'olivo", "VEIO_DE": "ESCRITO", "BASE": "x"},
                     _contrato(valor=["mosca dell'olivo"]), _contrato(base="nao esta no texto", forma="texto")):
            par, falta = self.par(NO_TEXTO, prob)
            self.assertIsNone(par, prob)
            self.assertTrue(any(f.startswith("JANELA_DECLARADA.PROBLEMA") for f in falta), falta)

    def test_D3_a_chave_de_outro_texto_nao_serve(self):
        par, falta = self.par(NOME_COMUM, _p(NO_TEXTO))    # a base e de outro boletim
        self.assertIsNone(par)
        self.assertIn("inferida", " ".join(falta))

    def test_D4_ponta_a_ponta_o_boletim_ganha_janela(self):
        texto = NO_TEXTO + "Intervenire al superamento della soglia del 10% di infestazione attiva.\n"
        itens = [_item_win("E2E", texto, _p(texto), "https://e.example/SINTETICO/1")]
        livro = CI.correr("CHAVE-PROBLEMA", itens, universo={"ITENS_NO_CORTE": 1})
        cw = W.julgar(livro, itens, HOJE, referencia={"ESTADO": NS})
        self.assertEqual([], cw["NOT_POSSIBLE"])
        (j,) = cw["CROP_WINDOWS"]
        self.assertEqual(("olivo", "mosca dell'olivo", "Puglia"), (j["CROP_ID"], j["ISSUE_ID"], j["REGION_ID"]))

    def test_D5_sem_problema_continua_NOT_POSSIBLE(self):
        texto = DUAS_PRAGAS + "Intervenire al superamento della soglia.\n"
        itens = [_item_win("E2E", texto, _p(texto), "https://e.example/SINTETICO/1")]
        livro = CI.correr("CHAVE-PROBLEMA", itens, universo={"ITENS_NO_CORTE": 1})
        cw = W.julgar(livro, itens, HOJE, referencia={"ESTADO": NS})
        self.assertEqual(W.NOT_POSSIBLE, cw["ANALYTIC_OUTPUT"])
        self.assertIn("CROP_ISSUE_EM_CAMPO", cw["REQUIREMENTS"][0]["REQUIREMENT"])

    def test_D6_o_motor_le_o_problema_do_futuro_pelo_mesmo_contrato(self):
        import motor_das_capacidades as M
        e = json.loads((RAIZ / "tests" / "dados" / "int-r7" / "SINTETICO-R7-SALA-EXPORT.json")
                       .read_text(encoding="utf-8"))
        evt = next(l for l in e["LINHAS"] if l["item_id"] == "SINT-R7-ARIF-EVT#0")

        def issue(ex):
            s = M.rodar(M.entrada_do_export(ex), HOJE, "SINT-HEAD")
            (o,) = s["ITENS_POR_FERRAMENTA"]["future"]
            return o["CHAVES"]["ENTITY_SOURCE"]["ISSUE_ID"]["VALOR"]
        self.assertEqual(NS, issue(e))
        # fora do contrato (a forma antiga da fixture) continua NAO SEI
        evt["janela_declarada"]["PROBLEMA"] = {"VALOR": "Bactrocera oleae", "VEIO_DE": "ESCRITO",
                                               "BASE": "SINTETICO · escrito no boletim"}
        self.assertEqual(NS, issue(e))
        # com o nome escrito e a chave no contrato, sai o nome
        evt["texto"] = "Mosca delle olive: giornata tecnica il 15 ottobre 2026 a Bari. [SINTETICO]"
        evt["janela_declarada"]["PROBLEMA"] = _p(evt["texto"])
        self.assertEqual("mosca dell'olivo", issue(e))


# ═══════════════════════════════════════════════════════════════════════════
# E · O REPROCESSO DA SALA (numa copia, a seco, idempotente)
# ═══════════════════════════════════════════════════════════════════════════
def _linha(ordem, texto, universo="T3", janela=None):
    j = janela if janela is not None else copy.deepcopy(adm.JANELA_NAO_MEDIDA)
    return {"run_id": "RUN-SINT", "ordem": ordem, "item_id": "SINT#%d" % ordem, "universo": universo,
            "texto": texto, "janela_declarada": json.dumps(j, ensure_ascii=False, sort_keys=True)}


COPIA = [_linha(1, NO_TEXTO), _linha(2, SO_NO_CABECALHO), _linha(3, DUAS_PRAGAS),
         _linha(4, SO_AUSENTE), _linha(5, NO_TEXTO, universo="T10"),
         _linha(6, NO_TEXTO, janela=dict(copy.deepcopy(adm.JANELA_NAO_MEDIDA),
                                         CULTURA={"VALOR": ["olivo"], "VEIO_DE": "revisao anterior",
                                                  "BASE": "SINTETICO"}))]


class E_OReprocesso(unittest.TestCase):

    def test_E1_so_a_chave_PROBLEMA_muda(self):
        fora = RP.reprocessar(COPIA)
        self.assertIs(False, fora["GRAVOU_NO_BANCO"])
        for linha, it in zip(COPIA, fora["ITENS"]):
            (r,) = it["REVISOES"]
            self.assertEqual("janela_declarada", r["CAMPO"])
            nova, velha = json.loads(r["VALOR"]), json.loads(linha["janela_declarada"])
            self.assertEqual(r["VALOR"], json.dumps(nova, ensure_ascii=False, sort_keys=True))
            self.assertEqual({k: v for k, v in velha.items() if k != "PROBLEMA"},
                             {k: v for k, v in nova.items() if k != "PROBLEMA"})
            self.assertTrue(AF.problema_conforme(nova["PROBLEMA"], linha["texto"])[0])
        self.assertEqual(["olivo"], json.loads(fora["ITENS"][5]["REVISOES"][0]["VALOR"])["CULTURA"]["VALOR"])

    def test_E2_a_conta_diz_o_que_sai_de_NAO_SEI(self):
        c = RP.reprocessar(COPIA)["CONTA"]
        self.assertEqual((6, 3, 1, 1, 1), (c["ITENS"], c["COM_PROBLEMA"], c["SO_CANDIDATOS"], c["SO_AUSENTES"],
                                           c["SEM_LEITOR_NO_UNIVERSO"]))
        self.assertEqual({"TEXT": 2, "SECTION_HEADER": 1}, c["POR_VEIO_DE"])
        self.assertEqual(3, c["COM_EPPO"])

    def test_E3_mesmo_codigo_duas_vezes_nao_repete(self):
        a = RP.reprocessar(COPIA)
        atuais = [dict(l, janela_declarada=x["REVISOES"][0]["VALOR"]) for l, x in zip(COPIA, a["ITENS"])]
        b = RP.reprocessar(atuais)
        self.assertEqual(a["VERSAO_DO_EXTRATOR"], b["VERSAO_DO_EXTRATOR"])
        self.assertEqual((0, len(COPIA)), (b["CONTA"]["REVISOES"], b["CONTA"]["JA_ERAM_ASSIM"]))

    def test_E4_sem_morada_ou_sem_janela_atual_e_erro_e_nao_revisao(self):
        sem_janela = dict(_linha(9, NO_TEXTO), janela_declarada=None)
        sem_morada = dict(_linha(10, NO_TEXTO), run_id=None)
        fora = RP.reprocessar([sem_janela, sem_morada])
        self.assertEqual((2, 0), (fora["CONTA"]["ERROS"], fora["CONTA"]["REVISOES"]))
        self.assertIn("janela_declarada ATUAL", fora["ITENS"][0]["ERRO"])

    def test_E5_o_seco_nao_abre_o_banco(self):
        arvore = ast.parse((RAIZ / "admissao" / "reprocessar_problema.py").read_text(encoding="utf-8"))
        topo = {a.name for n in arvore.body if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
        self.assertNotIn("sala_de_espera", topo)
        f = next(n for n in arvore.body if isinstance(n, ast.FunctionDef) and n.name == "reprocessar")
        chamadas = {getattr(n.func, "attr", getattr(n.func, "id", "")) for n in ast.walk(f)
                    if isinstance(n, ast.Call)}
        self.assertFalse({"rever", "pousar", "exigir_canonica", "aplicar"} & chamadas)

    def test_E6_aplicar_exige_a_canonica_a_mesma_versao_e_so_usa_rever(self):
        fora = RP.reprocessar(COPIA)

        class Falsa:
            def __init__(self):
                self.ordem, self.chamadas = [], []

            def exigir_canonica(self):
                self.ordem.append("canonica")

            def rever(self, run_id, ordem, revisoes, extrator, versao, motivo):
                self.ordem.append("rever")
                self.chamadas.append((run_id, ordem, revisoes, extrator, versao, motivo))
                return {"INSERIDAS": len(revisoes), "JA_ERAM_ASSIM": 0}
        f = Falsa()
        recibo = RP.aplicar(fora, espera=f)
        self.assertEqual("canonica", f.ordem[0])
        self.assertEqual((len(COPIA), len(COPIA)), (recibo["LINHAS"], recibo["INSERIDAS"]))
        self.assertTrue(all(c[4] == fora["VERSAO_DO_EXTRATOR"] and c[3] == RP.EXTRATOR for c in f.chamadas))
        velho = dict(fora, VERSAO_DO_EXTRATOR="chave-problema@outra")
        g = Falsa()
        with self.assertRaises(SystemExit):
            RP.aplicar(velho, espera=g)
        self.assertNotIn("rever", g.ordem)

    def test_E7_linha_de_comando_seco(self):
        with tempfile.TemporaryDirectory() as d:
            ent, sai = os.path.join(d, "copia.json"), os.path.join(d, "rev.json")
            with open(ent, "w", encoding="utf-8") as h:
                json.dump({"ITENS": COPIA}, h, ensure_ascii=False)
            r = subprocess.run([sys.executable, str(RAIZ / "admissao" / "reprocessar_problema.py"),
                                "--entrada", ent, "--seco", "--saida", sai],
                               capture_output=True, text=True, cwd=str(RAIZ))
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertIs(False, json.loads(r.stdout)["GRAVOU_NO_BANCO"])
            with open(sai, encoding="utf-8") as h:
                self.assertEqual(len(COPIA), json.load(h)["CONTA"]["REVISOES"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
