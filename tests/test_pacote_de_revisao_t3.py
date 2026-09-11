# -*- coding: utf-8 -*-
"""O PACOTE DE T3 TEM DE CHEGAR VAZIO E NEUTRO A QUEM O LE.

Um pacote de revisao humana falha de duas maneiras, e as duas sao silenciosas:

    1. alguem preenche um rotulo por maquina e ele passa por decisao humana;
    2. a resposta da maquina aparece ao lado da pergunta, e a pessoa concorda
       com ela sem saber que concordou.

    HUMAN_LABEL NAO PODE NASCER A OLHAR PARA CURRENT_CLASSIFIER_OUTPUT.

Estes testes prendem as duas.
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


class OsCandidatosSaoReprodutiveis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fichas, cls.auditoria = pac.construir()

    def test_a_varredura_do_censo_continua_a_dar_27(self):
        n = sum(1 for a in self.auditoria if a["CASOU_A_VARREDURA_DO_CENSO"])
        self.assertEqual(n, 27, "o numero de candidatos mudou. Isso pode ser "
                                "legitimo — mas obriga a refazer o pacote, "
                                "nao a ignorar.")

    def test_os_candidatos_vem_de_pelo_menos_nove_publicadores(self):
        publ = {f["PUBLISHER"] for f, a in zip(self.fichas, self.auditoria)
                if a["CASOU_A_VARREDURA_DO_CENSO"]} - {"NAO SEI"}
        self.assertGreaterEqual(len(publ), 9, f"so {sorted(publ)}")

    def test_o_pacote_e_maior_que_a_varredura(self):
        """Se o pacote fosse so os 27, os positivos nasceriam de uma frase."""
        varridos = sum(1 for a in self.auditoria
                       if a["CASOU_A_VARREDURA_DO_CENSO"])
        self.assertGreater(
            len(self.fichas), varridos,
            "o pacote encolheu para a pre-selecao. Um gabarito cujos positivos "
            "foram escolhidos por uma frase devolve essa frase a quem o usar.")

    def test_ha_candidatos_dos_dois_lados_para_o_revisor(self):
        """>= 10 que se declaram e >= 10 que nao — sem rotular nenhum."""
        com = [f for f in self.fichas if f["EVIDENCE"]["SELF_DESCRIPTION"]]
        sem = [f for f in self.fichas if not f["EVIDENCE"]["SELF_DESCRIPTION"]]
        self.assertGreaterEqual(len(com), 10)
        self.assertGreaterEqual(len(sem), 10)

    def test_todo_item_revisavel_tem_corpo_no_disco(self):
        for f in self.fichas:
            with self.subTest(item=f["ITEM_ID"]):
                existe = os.path.isfile(os.path.join(RAIZ, f["CONTENT_PATH"]))
                self.assertEqual(f["REVIEWABLE"], "YES" if existe else "NO")
                if f["REVIEWABLE"] == "YES":
                    self.assertTrue(f["EVIDENCE"]["OPENING"].strip(),
                                    "revisavel e sem abertura nenhuma")

    def test_a_ordem_e_neutra_e_estavel(self):
        outras, _ = pac.construir()
        self.assertEqual([f["ITEM_ID"] for f in self.fichas],
                         [f["ITEM_ID"] for f in outras])
        # e nao e por publicador: publicadores iguais nao ficam todos juntos
        publ = [f["PUBLISHER"] for f in self.fichas]
        blocos = sum(1 for a, b in zip(publ, publ[1:]) if a != b)
        self.assertGreater(blocos, len(set(publ)),
                           "a ordem agrupa por publicador — isso e um sinal")


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
                self.assertEqual(f["FINAL_LABEL"], pac.NAO_CORRIDO)
                self.assertIsNone(f["REVIEWER_A"]["REASON"])
                self.assertIsNone(f["REVIEWER_B"]["REASON"])

    def test_o_ficheiro_versionado_tambem_chega_vazio(self):
        self.assertEqual(self.pendente["AUTO_LABELS_ASSIGNED"], 0)
        for i in self.pendente["ITENS"]:
            with self.subTest(item=i["ITEM_ID"]):
                self.assertEqual(i["FINAL_LABEL"], pac.NAO_CORRIDO)
                self.assertEqual(i["REVIEWER_A"]["LABEL"], pac.NAO_CORRIDO)
                self.assertEqual(i["REVIEWER_B"]["LABEL"], pac.NAO_CORRIDO)

    def test_a_segunda_revisao_nao_foi_inventada(self):
        """Copiar A para B e chamar-lhe dupla revisao e uma mentira barata."""
        for i in self.pendente["ITENS"]:
            self.assertEqual(i["AGREEMENT"], pac.NAO_CORRIDO)

    def test_a_autodescricao_nao_e_um_rotulo(self):
        """E uma citacao literal: tem de aparecer mesmo no documento."""
        for f in self.fichas:
            for trecho in f["EVIDENCE"]["SELF_DESCRIPTION"]:
                with self.subTest(item=f["ITEM_ID"]):
                    corpo = " ".join(
                        pac._linhas(pac.censo._ler(f["CONTENT_PATH"])))
                    self.assertIn(trecho[:50], corpo,
                                  "a auto-descricao nao esta no documento")
                    self.assertNotIn(trecho.upper(), ("T3_SIM", "T3_NAO"))


class OPacoteNaoInfluenciaORevisor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(PACOTE, encoding="utf-8") as f:
            cls.texto = f.read()
        cls.antes, _, cls.depois = cls.texto.partition("## AUDIT_AFTER_REVIEW")

    def test_o_bloco_de_revisao_nao_sugere_resposta(self):
        for proibida in ("PROVAVELMENTE_T3", "LIKELY_T3", "CONFIDENCE",
                         "SUGGESTED_LABEL", "PROVAVEL", "SUGERIDO"):
            with self.subTest(palavra=proibida):
                self.assertNotIn(proibida, self.antes.upper().replace("Á", "A"))

    def test_a_decisao_da_porta_so_aparece_depois(self):
        self.assertNotIn("PERGUNTAS_DO_UNIVERSO", self.antes.split(
            "## O QUE ESTE PACOTE ESCONDE")[-1].split("## ITEM 01")[-1],
            "a saida do classificador atual aparece ao lado das fichas")
        self.assertIn("decisao atual da porta", self.depois)

    def test_o_territorio_da_ficha_da_fonte_nao_aparece_nas_fichas(self):
        fichas = self.antes.split("## ITEM 01", 1)[-1]
        self.assertNotIn("TERRITORIO_DA_FICHA", fichas)
        self.assertIn("territorio da FICHA DA FONTE", self.depois)

    def test_nenhuma_ficha_diz_quais_casaram_a_varredura(self):
        fichas = self.antes.split("## ITEM 01", 1)[-1]
        self.assertNotIn("CASOU_A_VARREDURA", fichas)
        self.assertIn("casou a varredura", self.depois)

    def test_toda_ficha_deixa_os_quatro_estados_vazios(self):
        for estado in pac.ESTADOS:
            n = len(re.findall(rf"\| `{estado}` \| \[ \] \| \[ \] \|",
                               self.texto))
            with self.subTest(estado=estado):
                self.assertEqual(n, 46, f"{estado} aparece {n} vezes marcado "
                                        f"ou em falta")

    def test_o_protocolo_nao_virou_lei(self):
        import admissao as adm
        self.assertNotIn("T3_SIM", str(adm.PERGUNTAS_DO_UNIVERSO))
        self.assertEqual(sorted(adm.PERGUNTAS_DO_UNIVERSO),
                         ["T3", "T4", "T7", "T9"])


class OPacoteVersionadoBateComOGerador(unittest.TestCase):

    def test_o_json_no_disco_e_o_que_o_gerador_produz(self):
        fichas, _ = pac.construir()
        with open(PENDENTE, encoding="utf-8") as f:
            disco = json.load(f)
        self.assertEqual([i["ITEM_ID"] for i in disco["ITENS"]],
                         [f["ITEM_ID"] for f in fichas],
                         "o ficheiro versionado saiu de sincronia com o "
                         "gerador. Regenere: py provas/pacote_de_revisao_t3.py "
                         "--escrever")

    def test_construir_nao_escreve_nada(self):
        antes = (os.path.getmtime(PACOTE), os.path.getmtime(PENDENTE))
        pac.construir()
        self.assertEqual(antes, (os.path.getmtime(PACOTE),
                                 os.path.getmtime(PENDENTE)))


if __name__ == "__main__":
    unittest.main()
