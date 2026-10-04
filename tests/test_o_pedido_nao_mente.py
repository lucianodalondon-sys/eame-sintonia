#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BG-05 — O PEDIDO NÃO PODE MENTIR: filtro declarado não desaparece,
e a fonte nomeada não é trocada por outra.

    py -m unittest tests.test_o_pedido_nao_mente

O DEFEITO, MEDIDO ANTES DO CONSERTO
-----------------------------------
`IT-T4-001` é T4. O único executor que a alcançava estava registado só em
T2/T3. Um pedido `T4 + fonte=IT-T4-001` abria o `regulatorio-eu` — que
consome `celex`, não `fonte` — o filtro morria calado, e a corrida colhia
`EU-T4-001`. Outra fonte, outro país, outro ato, com cara de sucesso.

AS DUAS METADES DO CONSERTO, E OS DONOS
---------------------------------------
    EXECUTOR_SELECTION_OWNER  pedido/receitas.py::resolver
        promove quem consome TODOS os filtros declarados (1ª chave),
        depois quem serve a fase (2ª chave, a regra que já existia).
    FILTER_OWNER              a declaração do executor na receita
        (`argumentos_de_filtros` + `filtros_nomeados`), lida por
        `filtros_consumidos()`. `pais`/`tema`/`fase` são do resolvedor.
    O PORTÃO                  orquestrador/orquestrador.py::correr
        filtro que sobra → STATUS=FILTRO_NAO_CONSUMIDO, antes da rede.

Nenhum caso aqui toca a rede: seleção lê-se no plano; o portão recusa antes
de chamar executor; os casos `seco` não executam nada.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

from pedido import Pedido  # noqa: E402
from receitas import resolver, FILTROS_DO_RESOLVEDOR, filtros_consumidos  # noqa: E402
import orquestrador as orq  # noqa: E402


def escolhido(alvo, filtros):
    plano = resolver(Pedido(alvo=alvo, filtros=filtros))
    return plano.executores[0]["id"] if plano.executores else None


class ASelecaoSegueOsFiltros(unittest.TestCase):

    def test_1_T4_com_fonte_italiana_abre_o_executor_italiano(self):
        self.assertEqual(
            escolhido("T4", {"pais": "IT", "fonte": "IT-T4-001"}),
            "italia-recorrente")

    def test_2_T4_com_celex_continua_no_regulatorio_eu(self):
        self.assertEqual(
            escolhido("T4", {"pais": "IT", "celex": "32026R1696"}),
            "regulatorio-eu")

    def test_3_T4_sem_filtro_mantem_o_comportamento_declarado(self):
        """Bare T4 abre o primeiro da lista — a ordem é decisão escrita."""
        self.assertEqual(escolhido("T4", {"pais": "IT"}), "regulatorio-eu")

    def test_4_T3_com_fonte_continua_no_italiano(self):
        self.assertEqual(
            escolhido("T3", {"pais": "IT", "fonte": "IT-T3-002"}),
            "italia-recorrente")

    def test_5_T2_com_fonte_continua_no_italiano(self):
        self.assertEqual(
            escolhido("T2", {"pais": "IT", "fonte": "IT-T2-002"}),
            "italia-recorrente")

    def test_6_a_fase_continua_a_promover_no_T9(self):
        """A regra antiga não afrouxou: fase de SCRAP promove o scrap."""
        self.assertEqual(
            escolhido("T9", {"pais": "IT", "fase": "janela",
                             "fonte": "IT-T9-001", "teto": "10"}),
            "scrap-colheita")


class OComandoLevaAFonteCerta(unittest.TestCase):

    def _recibo(self, alvo, filtros):
        return orq.correr(Pedido(alvo=alvo, filtros=filtros), seco=True)

    def test_7_T4_fonte_IT_T4_001_monta_o_comando_do_executor_italiano(self):
        r = self._recibo("T4", {"pais": "IT", "fonte": "IT-T4-001"})
        self.assertIn("italy_executor.py", r["COMANDO"])
        self.assertIn("IT-T4-001", r["COMANDO"])
        self.assertNotIn("eu_regulatorio", r["COMANDO"])

    def test_8_T4_fonte_IT_T4_001_nunca_vira_EU_T4_001(self):
        r = self._recibo("T4", {"pais": "IT", "fonte": "IT-T4-001"})
        self.assertNotIn("32026R1696", r["COMANDO"],
                         "o celex por omissao do regulatorio-eu entrou no "
                         "comando de um pedido que nomeou IT-T4-001")


class OFiltroQueSobraGritaAntesDaRede(unittest.TestCase):

    def _recibo(self, alvo, filtros):
        return orq.correr(Pedido(alvo=alvo, filtros=filtros), seco=True)

    def test_9_filtro_inventado_recusa_com_nome(self):
        r = self._recibo("T4", {"pais": "IT", "filtro_inventado": "x"})
        self.assertEqual(r["STATUS"], "FILTRO_NAO_CONSUMIDO")
        self.assertIn("filtro_inventado", r["FILTROS_NAO_CONSUMIDOS"])
        self.assertNotIn("COMANDO", r, "a recusa nao pode ter montado comando")

    def test_10_fonte_num_alvo_sem_quem_a_consuma_recusa(self):
        """T6 só tem o corpus-pesquisador, que não consome `fonte`."""
        r = self._recibo("T6", {"pais": "IT", "fonte": "IT-T5-002"})
        self.assertEqual(r["STATUS"], "FILTRO_NAO_CONSUMIDO")
        self.assertIn("fonte", r["FILTROS_NAO_CONSUMIDOS"])

    def test_11_os_filtros_do_resolvedor_nunca_sao_acusados(self):
        r = self._recibo("T4", {"pais": "IT", "tema": "vite",
                                "celex": "32026R1696"})
        self.assertNotEqual(r.get("STATUS"), "FILTRO_NAO_CONSUMIDO", r)

    def test_12_o_recibo_da_recusa_tem_run_id_e_motivo(self):
        r = self._recibo("T4", {"pais": "IT", "filtro_inventado": "x"})
        self.assertTrue(r["RUN_ID"])
        self.assertIn("FILTRO_NAO_CONSUMIDO", r["ERROR"])
        self.assertIn("EU-T4-001", r["ERROR"],
                      "o motivo cita o precedente que esta lei fecha")


class ADeclaracaoEDoExecutor(unittest.TestCase):

    def test_13_filtros_consumidos_le_as_duas_listas(self):
        e = {"argumentos_de_filtros": ["fase", "fonte"],
             "filtros_nomeados": ["teto"]}
        self.assertEqual(filtros_consumidos(e), {"fase", "fonte", "teto"})

    def test_14_o_resolvedor_declara_os_seus_quatro(self):
        """Os filtros que o resolvedor consome, e que por isso não descem.

        ⚠️ ERAM TRÊS, E PASSARAM A SER QUATRO. `universo` entrou quando o
        roteamento do universo deixou de ser emprestado do `alvo`: ele é a
        PERGUNTA que a Admissão fará, lida pelo control plane depois de o
        executor já ter corrido, e nenhum executor o consome — nem deve.

            O UNIVERSO É DO PEDIDO E DA PORTA. NÃO É DA AQUISIÇÃO.

        Sem ele nesta lista, declarar `universo` fazia a corrida ser recusada
        com `FILTRO_NAO_CONSUMIDO` — a guarda do BG-05 a trabalhar bem sobre
        um campo que nunca lhe pertenceu.

        Esta trava continua a ser uma trava: acrescentar um quinto nome aqui
        obriga a dizer por quê, e é exactamente para isso que ela existe.
        """
        self.assertEqual(set(FILTROS_DO_RESOLVEDOR),
                         {"pais", "tema", "fase", "universo"})


if __name__ == "__main__":
    unittest.main()
