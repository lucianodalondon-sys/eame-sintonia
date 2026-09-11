#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROVA DE ALCANCE TEM DE SABER DIZER «NAO CHEGOU».

Uma sonda de alcance que conta toda a gente como tendo chegado mede 36 de 36
e parece uma boa noticia. Os testes aqui existem para que o numero so possa
subir por o documento ter mesmo chegado.
"""
import importlib.util
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402


def _carrega(apelido, ficheiro):
    spec = importlib.util.spec_from_file_location(
        apelido, os.path.join(RAIZ, "provas", ficheiro))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = _carrega("alcance_t", "alcance_da_pergunta_tematica.py")


class ARegraTematicaEAQueElaDiz(unittest.TestCase):

    def test_a_regra_tematica_existe_mesmo_na_porta(self):
        """O nome nao e uma string de conveniencia: e o que a porta devolve.

        ⚠️ JA TIVEMOS DEFEITO DESTE TIPO — uma prova a comparar com um nome
        que o runtime nunca produz mede sempre zero, e zero parece uma
        medicao. Aqui o nome e confrontado com uma decisao REAL.
        """
        item = {"id": "t", "artifact_type": "RAW", "texto": "qualquer coisa",
                "source_id": "IT-T3-001"}
        d = adm.decidir(item, "T3")
        self.assertEqual(d.regra, A.REGRA_TEMATICA,
                         "um item pronto nao chegou a regra tematica; o nome "
                         "usado pela prova de alcance esta desalinhado")

    def test_parar_na_prontidao_nao_conta_como_ter_chegado(self):
        sem_origem = {"id": "t", "artifact_type": "RAW",
                      "texto": "qualquer coisa"}
        d = adm.decidir(sem_origem, "T3")
        self.assertNotEqual(d.regra, A.REGRA_TEMATICA)
        self.assertEqual(d.resultado, adm.NAO_SEI,
                         "falta de prontidao virou julgamento")


class AsClassesNascemDaMedicao(unittest.TestCase):

    def test_nenhuma_classe_de_falha_esta_escrita_a_mao(self):
        """As classes SAO as regras que pararam documentos, contadas.

            UMA TAXONOMIA ESCRITA ANTES DE MEDIR
            DESCREVE O AUTOR, NAO O ACERVO.
        """
        linhas = [
            {"CHEGOU_AO_TEMA": False, "REGRA_QUE_DECIDIU": "uma regra nova "
             "que nunca existiu", "ITEM_ID": "z", "ESTAGIO": "?",
             "SOURCE_ID_NO_REGISTO": None, "SOURCE_ID_NO_GABARITO": None},
        ]
        self.assertIn("uma regra nova que nunca existiu",
                      A.classes_de_paragem(linhas),
                      "a prova so reconhece classes que ela propria previu")

    def test_origem_em_falta_distingue_quem_sabe_de_quem_nao_sabe(self):
        """Dois buracos diferentes consertam-se em sitios diferentes.

        «o registo nao sabe e a linhagem sabe» e encanamento perdido. «ninguem
        sabe» e uma fonte por descobrir. Fundir os dois num numero so apaga
        justamente a parte accionavel.
        """
        perdido = {"CHEGOU_AO_TEMA": False, "REGRA_QUE_DECIDIU": "origem",
                   "ITEM_ID": "a", "ESTAGIO": "DOCUMENTO",
                   "SOURCE_ID_NO_REGISTO": "NAO SEI",
                   "SOURCE_ID_NO_GABARITO": "IT-T3-007"}
        orfao = dict(perdido, ITEM_ID="b", SOURCE_ID_NO_GABARITO=None)
        causas = A.porque_a_prontidao_falha([perdido, orfao])
        self.assertEqual(len(causas), 2,
                         "as duas origens em falta foram fundidas numa so")

    def test_chegar_ao_tema_e_uma_propriedade_da_regra_e_nao_da_saida(self):
        """Um NAO_SEI tematico CHEGOU. Um NAO_SEI de prontidao NAO chegou.

        As duas saidas sao a mesma palavra e nao sao a mesma coisa: uma e o
        mecanismo a confessar que nao sabe ler; a outra e o documento a nunca
        ter sido lido.
        """
        linhas = [{"CHEGOU_AO_TEMA": True, "REGRA_QUE_DECIDIU":
                   A.REGRA_TEMATICA, "ITEM_ID": "a", "ESTAGIO": "DOCUMENTO",
                   "SOURCE_ID_NO_REGISTO": "x", "SOURCE_ID_NO_GABARITO": "x"}]
        self.assertEqual(A.classes_de_paragem(linhas), {},
                         "quem chegou ao tema foi contado como paragem")


class OArtefatoNaoPodeMentir(unittest.TestCase):

    def test_a_prova_nao_fabrica_identidade(self):
        """MEASURE != FIX. Nenhuma escrita de SOURCE_ID, em sitio nenhum."""
        with open(os.path.join(RAIZ, "provas",
                               "alcance_da_pergunta_tematica.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        for proibido in ('bruto["SOURCE_ID"] =', 'item["SOURCE_ID"] =',
                         "uuid", "SOURCE_ID\"] = hash"):
            self.assertNotIn(proibido, fonte,
                             "a prova escreve identidade: %s" % proibido)

    def test_o_denominador_do_alcance_nunca_e_inventado(self):
        from fractions import Fraction
        gate = _carrega("gate_alc_t", "gate_de_aceitacao_tematica.py")
        r = gate.avaliar_reachability(15, 36)
        self.assertEqual(Fraction(r["REACHABILITY"]), Fraction(15, 36))
        self.assertFalse(r["REACHABILITY_GATE_PASS"])
        with self.assertRaises(gate.MetricaEmFalta):
            gate.avaliar_reachability(0, 0)


if __name__ == "__main__":
    unittest.main()
