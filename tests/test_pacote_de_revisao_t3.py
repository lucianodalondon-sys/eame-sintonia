# -*- coding: utf-8 -*-
"""O PACOTE DE T3 TEM DE CHEGAR VAZIO, NEUTRO, E SOBRE A POPULACAO CERTA.

Um pacote de revisao humana falha de tres maneiras, e as tres sao silenciosas:

    1. alguem preenche um rotulo por maquina e ele passa por decisao humana;
    2. a resposta da maquina aparece ao lado da pergunta, e a pessoa concorda
       com ela sem saber que concordou;
    3. a lista inteira nasce da pergunta errada, e ai nem o rotulador humano
       nem a apresentacao neutra salvam nada.

    LEAKAGE NO ROTULADOR  !=  LEAKAGE NO AMOSTRADOR  !=  LEAKAGE NA POPULACAO

Estes testes prendem as tres.
"""
import importlib.util
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "pacote_t3", os.path.join(RAIZ, "provas", "pacote_de_revisao_t3.py"))
pac = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pac)

PACOTE = os.path.join(RAIZ, pac.PACOTE)
PENDENTE = os.path.join(RAIZ, pac.PENDENTE)


class APopulacaoEOFrameNeutro(unittest.TestCase):
    """A correcao desta missao, presa onde nao se desfaz sem cair."""

    @classmethod
    def setUpClass(cls):
        cls.fichas, cls.auditoria = pac.construir()

    def test_a_populacao_nao_vem_do_gabarito_de_t2(self):
        import inspect
        codigo = inspect.getsource(pac.construir) + inspect.getsource(pac._frame)
        self.assertNotIn("_gabarito_t2", codigo,
                         "a populacao voltou a nascer do corpus curado para "
                         "T2. T2-CURATED CORPUS != GENERAL T3 EVALUATION FRAME.")
        self.assertIn("sampling_frame", codigo)

    def test_a_populacao_e_exatamente_o_frame_revisavel(self):
        frame = {d["DOC_SHA256"] for d in pac.amostra.sampling_frame()
                 if d["REVIEWABLE"]}
        self.assertEqual({f["DOC_SHA256"] for f in self.fichas}, frame)

    def test_sao_53_fichas(self):
        self.assertEqual(len(self.fichas), 53,
                         "o tamanho da populacao mudou. Pode ser legitimo — "
                         "mas obriga a refazer o frame, nao a ajustar o numero.")

    def test_um_documento_uma_ficha(self):
        shas = [f["DOC_SHA256"] for f in self.fichas]
        self.assertEqual(len(shas), len(set(shas)),
                         "o mesmo documento aparece duas vezes")
        caminhos = [p for f in self.fichas for p in f["ALL_PATHS"]]
        self.assertGreater(len(caminhos), len(shas),
                           "nenhum documento vive em dois caminhos — se isto "
                           "for verdade, a deduplicacao deixou de ser testada")

    def test_as_46_foram_reaproveitadas_e_7_acrescentadas(self):
        velhas = [a for a in self.auditoria if a["JA_ESTAVA_NO_PACOTE_DE_46"]]
        novas = [a for a in self.auditoria if not a["JA_ESTAVA_NO_PACOTE_DE_46"]]
        self.assertEqual(len(velhas), 46)
        self.assertEqual(len(novas), 7)

    def test_a_contagem_de_reaproveitadas_nao_se_le_a_si_mesma(self):
        """Ler o ficheiro que a regeneracao reescreve daria 53 e 0."""
        import inspect
        self.assertNotIn("PENDENTE", inspect.getsource(pac._pacote_de_46))

    def test_os_publicadores_ausentes_entraram(self):
        """Conferido DEPOIS, nunca usado como criterio de inclusao."""
        publ = {f["PUBLISHER"] for f in self.fichas}
        for esperado in ("ISTAT", "AGEA", "ISMEA"):
            with self.subTest(publisher=esperado):
                self.assertIn(esperado, publ)
        self.assertEqual(len(publ), 17)


class AOrdemNaoCarregaSinal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fichas, _ = pac.construir()

    def test_a_ordem_e_estavel(self):
        outras, _ = pac.construir()
        self.assertEqual([f["DOC_SHA256"] for f in self.fichas],
                         [f["DOC_SHA256"] for f in outras])

    def test_a_ordem_nao_agrupa_publicador(self):
        publ = [f["PUBLISHER"] for f in self.fichas]
        blocos = sum(1 for a, b in zip(publ, publ[1:]) if a != b)
        self.assertGreater(blocos, len(set(publ)),
                           "a ordem agrupa por publicador — isso e um sinal")

    def test_a_ordem_nao_vem_do_caminho(self):
        import inspect
        self.assertIn("DOC_SHA256", inspect.getsource(pac.construir))


class NenhumRotuloFoiAtribuidoPorMaquina(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fichas, _ = pac.construir()
        with open(PENDENTE, encoding="utf-8") as f:
            cls.pendente = json.load(f)

    def test_construir_nao_preenche_rotulo_nenhum(self):
        for f in self.fichas:
            with self.subTest(item=f["ITEM_ID"]):
                self.assertEqual(f["REVIEWER_A"]["LABEL"], pac.NAO_CORRIDO)
                self.assertEqual(f["REVIEWER_B"]["LABEL"], pac.NAO_CORRIDO)
                self.assertEqual(f["AGREEMENT"], pac.NAO_CORRIDO)
                self.assertEqual(f["FINAL_LABEL"], pac.NAO_CORRIDO)

    def test_o_ficheiro_versionado_tambem_chega_vazio(self):
        self.assertEqual(self.pendente["AUTO_LABELS_ASSIGNED"], 0)
        self.assertEqual(len(self.pendente["ITENS"]), 53)
        for i in self.pendente["ITENS"]:
            with self.subTest(item=i["ITEM_ID"]):
                self.assertEqual(i["FINAL_LABEL"], pac.NAO_CORRIDO)
                self.assertEqual(i["AGREEMENT"], pac.NAO_CORRIDO)

    def test_a_regeneracao_nao_apaga_decisao_humana(self):
        """Hoje estao todas vazias. O mecanismo tem de existir na mesma."""
        import inspect
        fonte = inspect.getsource(pac.construir)
        self.assertIn("anteriores", fonte)
        self.assertIn("REVIEWER_A", inspect.getsource(pac._revisoes_anteriores))

    def test_a_autodescricao_nao_e_um_rotulo(self):
        for f in self.fichas:
            for trecho in f["EVIDENCE"]["SELF_DESCRIPTION"]:
                with self.subTest(item=f["ITEM_ID"]):
                    corpo = " ".join(pac._linhas(pac.censo._ler(f["BODY_PATH"])))
                    self.assertIn(trecho[:50], corpo)


class OPacoteNaoInfluenciaORevisor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(PACOTE, encoding="utf-8") as f:
            cls.texto = f.read()
        cls.antes, _, cls.depois = cls.texto.partition("## AUDIT_AFTER_REVIEW")
        cls.fichas_md = cls.antes.split("## ITEM 01", 1)[-1]

    def test_o_bloco_de_revisao_nao_sugere_resposta(self):
        for proibida in ("PROVAVELMENTE_T3", "LIKELY_T3", "CONFIDENCE",
                         "SUGGESTED_LABEL", "PROVAVEL", "SUGERIDO"):
            with self.subTest(palavra=proibida):
                self.assertNotIn(proibida,
                                 self.antes.upper().replace("Á", "A"))

    def test_a_decisao_da_porta_so_aparece_depois(self):
        self.assertNotIn("decisao atual da porta", self.fichas_md)
        self.assertIn("decisao atual da porta", self.depois)

    def test_o_territorio_da_ficha_da_fonte_nao_aparece_nas_fichas(self):
        self.assertNotIn("TERRITORIO_DA_FICHA", self.fichas_md)
        self.assertNotIn("territorio da FICHA DA FONTE", self.fichas_md)
        self.assertIn("territorio da FICHA DA FONTE", self.depois)

    def test_nenhuma_ficha_diz_porque_entrou(self):
        self.assertNotIn("CASOU_A_VARREDURA", self.fichas_md)
        self.assertNotIn("JA_ESTAVA_NO_PACOTE", self.fichas_md)
        self.assertIn("casou a varredura", self.depois)

    def test_toda_ficha_deixa_os_quatro_estados_vazios(self):
        for estado in pac.ESTADOS:
            n = len(re.findall(rf"\| `{estado}` \| \[ \] \| \[ \] \|",
                               self.texto))
            with self.subTest(estado=estado):
                self.assertEqual(n, 53)

    def test_ha_53_fichas_numeradas(self):
        self.assertEqual(len(re.findall(r"^## ITEM \d\d / 53$",
                                        self.texto, re.M)), 53)

    def test_o_protocolo_nao_virou_lei(self):
        import admissao as adm
        self.assertEqual(sorted(adm.PERGUNTAS_DO_UNIVERSO),
                         ["T3", "T4", "T7", "T9"])


class OPacoteVersionadoBateComOGerador(unittest.TestCase):

    def test_o_json_no_disco_e_o_que_o_gerador_produz(self):
        fichas, _ = pac.construir()
        with open(PENDENTE, encoding="utf-8") as f:
            disco = json.load(f)
        self.assertEqual([i["DOC_SHA256"] for i in disco["ITENS"]],
                         [f["DOC_SHA256"] for f in fichas],
                         "o ficheiro versionado saiu de sincronia. Regenere: "
                         "py provas/pacote_de_revisao_t3.py --escrever")

    def test_construir_nao_escreve_nada(self):
        antes = (os.path.getmtime(PACOTE), os.path.getmtime(PENDENTE))
        pac.construir()
        self.assertEqual(antes, (os.path.getmtime(PACOTE),
                                 os.path.getmtime(PENDENTE)))


class ORedTeamDosCasosDificeis(unittest.TestCase):
    """Dez ataques. Todos continuam revisaveis, e nenhum ganha rotulo."""

    @classmethod
    def setUpClass(cls):
        cls.fichas, _ = pac.construir()
        cls.por_id = {f["ITEM_ID"]: f for f in cls.fichas}

    def _tem_evidencia(self, f):
        e = f["EVIDENCE"]
        self.assertEqual(f["REVIEWABLE"], "YES")
        self.assertTrue(e["OPENING"].strip(), f"{f['ITEM_ID']} sem abertura")
        self.assertEqual(f["FINAL_LABEL"], pac.NAO_CORRIDO)

    def test_1_documento_em_dois_caminhos(self):
        multi = [f for f in self.fichas if len(f["ALL_PATHS"]) > 1]
        self.assertGreaterEqual(len(multi), 5)
        for f in multi:
            self._tem_evidencia(f)

    def test_2_e_3_varias_series_e_zonas_do_mesmo_publicador(self):
        from collections import Counter
        c = Counter(f["PUBLISHER"] for f in self.fichas)
        self.assertGreaterEqual(c.most_common(1)[0][1], 4)
        for f in [x for x in self.fichas if x["PUBLISHER"] == c.most_common(1)[0][0]]:
            self._tem_evidencia(f)

    def test_4_e_5_documento_tabular_e_administrativo(self):
        tabular = [f for f in self.fichas
                   if f["RAW_FORMAT"] in (".csv", "(sem extensao)")]
        self.assertGreaterEqual(len(tabular), 4,
                                "os documentos tabulares/administrativos "
                                "voltaram a faltar")
        for f in tabular:
            self._tem_evidencia(f)

    def test_6_filename_semanticamente_enganoso(self):
        enganosos = [f for f in self.fichas
                     if re.search(r"fitosanitar|agrometeorolog|meteorolog",
                                  f["PARENT_ARTIFACT"], re.I)
                     and not f["EVIDENCE"]["SELF_DESCRIPTION"]]
        self.assertGreaterEqual(len(enganosos), 4,
                                "os casos em que o nome engana desapareceram")
        for f in enganosos:
            self._tem_evidencia(f)

    def test_7_e_8_source_id_e_lingua_desconhecidos(self):
        sem_fonte = [f for f in self.fichas if f["SOURCE_ID"] == "NAO SEI"]
        sem_lingua = [f for f in self.fichas if f["LANGUAGE"] == "NAO SEI"]
        self.assertTrue(sem_fonte and sem_lingua)
        for f in sem_fonte[:5] + sem_lingua[:5]:
            self._tem_evidencia(f)

    def test_9_e_10_os_do_gabarito_antigo_e_os_sete_novos(self):
        _f, auditoria = pac.construir()
        for a, f in zip(auditoria, self.fichas):
            self._tem_evidencia(f)
        novas = [f for a, f in zip(auditoria, self.fichas)
                 if not a["JA_ESTAVA_NO_PACOTE_DE_46"]]
        self.assertEqual(len(novas), 7)
        self.assertTrue(any(f["RAW_FORMAT"] != ".pdf" for f in novas),
                        "os novos deviam trazer formatos fora do padrao "
                        "boletim")


if __name__ == "__main__":
    unittest.main()
