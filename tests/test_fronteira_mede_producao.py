# -*- coding: utf-8 -*-
"""PRODUZIR NÃO É CONSUMIR — e a fronteira tem de as medir em separado.

    READY = fim da Collection.
    READY CONSUMER = 0 é o ESTADO DESEJADO enquanto a Intelligence não começou.

Isto está escrito na secção 24 do `SINTONIA-EAME-KNOW-HOW.md` como alvo de
fechamento. E a medição da fronteira estava a tratá-lo como defeito:

    GAP = None if consumidores else "READY_SEM_CONSUMIDOR"

Duas consequências, as duas medidas por red team em 2026-09-11 (C-MADRUGADA-CR1):

  1. o ALVO da arquitetura (READY produzido, zero consumidores) saía com o
     MESMO diagnóstico de nada ter sido produzido;
  2. um consumidor artificial, com ZERO produção, LIMPAVA o gap — a fronteira
     era declarada sã justamente no estado que a arquitetura proíbe hoje.

    UM MEDIDOR QUE NAO CONSEGUE DISTINGUIR O ALVO DO DEFEITO
    NAO ESTA A MEDIR: ESTA A OPINAR.

E o mesmo booleano viajava para o censo, onde `ENTROU` fazia
`bool(DESTINO_EXISTE) and bool(CONSUMIDORES)` — uma prova de «a saída
atravessou» que só podia subir acima de zero no dia em que alguém violasse a
arquitetura. Uma medida incapaz de reportar sucesso quando o sistema está
correcto está partida, independentemente do sistema.

Esta trava fixa as quatro respostas. Ela não diz que a fronteira está boa: diz
que o diagnóstico distingue os quatro estados do mundo.
"""
import importlib.util
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _medidor():
    spec = importlib.util.spec_from_file_location(
        "_fronteira_medidor", os.path.join(RAIZ, "provas", "a_fronteira_da_coleta.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class OEstadoDaFronteiraDistingueOsQuatroMundos(unittest.TestCase):
    """Produção × consumo são dois eixos. Quatro estados, quatro diagnósticos."""

    def setUp(self):
        self.m = _medidor()
        self.assertTrue(
            hasattr(self.m, "o_estado_da_fronteira"),
            "o medidor não expõe `o_estado_da_fronteira(produzido, consumidores)`. "
            "Sem uma função pura, o diagnóstico só existe dentro de `main()` e "
            "não há como o testar sem escrever no disco do repositório.")

    def gap(self, produzido, consumidores):
        return self.m.o_estado_da_fronteira(produzido, consumidores)[0]

    def test_nada_produzido_e_o_defeito_e_ele_tem_nome_proprio(self):
        self.assertEqual(self.gap(False, []), "READY_NUNCA_PRODUZIDO")

    def test_o_alvo_da_arquitetura_nao_e_um_defeito(self):
        """READY produzido + zero consumidores = `WAITING FOR INTELLIGENCE`."""
        self.assertIsNone(
            self.gap(True, []),
            "READY produzido com zero consumidores é o ESTADO DESEJADO da "
            "secção 24 do know-how, e não pode sair como gap.")

    def test_consumidor_sem_producao_nao_limpa_coisa_nenhuma(self):
        """O pior estado do mundo não pode ser o melhor diagnóstico."""
        self.assertEqual(
            self.gap(False, ["inteligencia/le_o_ready.py"]),
            "READY_NUNCA_PRODUZIDO",
            "zero produção continua a ser zero produção, haja quem leia ou não.")

    def test_consumidor_com_producao_e_bypass_enquanto_a_inteligencia_nao_comecou(self):
        self.assertEqual(
            self.gap(True, ["inteligencia/le_o_ready.py"]),
            "CONSUMIDOR_ANTES_DA_INTELIGENCIA")

    def test_todo_gap_traz_o_porque_escrito(self):
        for produzido, cons in ((False, []), (True, []), (False, ["x.py"]), (True, ["x.py"])):
            gap, porque = self.m.o_estado_da_fronteira(produzido, cons)
            with self.subTest(produzido=produzido, consumidores=cons):
                if gap is None:
                    self.assertIsNone(porque)
                else:
                    self.assertGreater(len(porque or ""), 30,
                                       "um gap sem motivo escrito é um rótulo")


class OCensoNaoMedeEntradaPeloConsumidor(unittest.TestCase):
    """`ENTROU` é «a saída atravessou a fronteira» — produção, não consumo."""

    def setUp(self):
        caminho = os.path.join(RAIZ, "system-map", "scripts", "censo_cards_sensores.py")
        with open(caminho, encoding="utf-8") as f:
            self.fonte = f.read()

    def test_a_formula_de_entrou_nao_depende_de_consumidores(self):
        # Lê a LINHA DE ATRIBUIÇÃO, não o ficheiro: o comentário logo acima
        # cita a fórmula antiga de propósito, e procurar texto no ficheiro
        # inteiro faria a explicação do conserto acusar o defeito.
        atribuicoes = [l.strip() for l in self.fonte.splitlines()
                       if l.strip().startswith("atravessou =")]
        self.assertEqual(len(atribuicoes), 1,
                         "esperava uma única atribuição de `atravessou`")
        self.assertNotIn(
            "CONSUMIDORES", atribuicoes[0],
            "`ENTROU` não pode exigir consumidor: com `READY CONSUMER = 0` como "
            "alvo, essa fórmula nunca consegue reportar sucesso. Linha: "
            + atribuicoes[0])

    def test_entrou_mede_producao(self):
        self.assertIn("READY_PRODUZIDO", self.fonte,
                      "o censo deve ler a produção do READY por nome próprio")


if __name__ == "__main__":
    unittest.main()


class OQueAtravessaAFronteiraEOQueNaoAtravessa(unittest.TestCase):
    """RED TEAM da fronteira, do lado da porta.

    A correcção desta missão foi no MEDIDOR, e um medidor consertado é fácil de
    consertar demais: bastaria a porta ficar mais generosa para `ENTROU` subir
    sem nada ter melhorado. Estas travas prendem o outro lado.

        NUNCA RELAXAR A ADMISSAO PARA FAZER DADO PASSAR.
    """

    def setUp(self):
        import sys
        sys.path.insert(0, RAIZ)
        import _gavetas  # noqa: F401
        import admissao
        self.adm = admissao
        self.bom = {"id": "rt", "texto": "Ensaio de campo com DOI publicado",
                    "source_id": "IT-T7-001", "fact_time": "2026-05-02"}

    def test_so_o_SIM_produz_ready(self):
        d = self.adm.decidir(self.bom, "T7", corrida="RT")
        self.assertEqual(d.resultado, self.adm.SIM)
        self.assertEqual(self.adm.pronto_para_inteligencia(self.bom, d)["ESTADO"],
                         "PRONTO_PARA_INTELIGENCIA")

    def test_NAO_SEI_nao_produz_ready(self):
        sem = {"id": "rt", "texto": "Ensaio com DOI", "source_id": "IT-T7-002"}
        d = self.adm.decidir(sem, "T7", corrida="RT")
        self.assertEqual(d.resultado, self.adm.NAO_SEI)
        with self.assertRaises(Exception):
            self.adm.pronto_para_inteligencia(sem, d)

    def test_ERRO_nao_vira_rejeicao(self):
        d = self.adm.decidir({"id": "rt", "erro_de_leitura": "TimeoutError",
                              "source_id": "IT-T7-003", "fact_time": "2026-01-01"}, "T7")
        self.assertEqual(d.resultado, self.adm.ERRO)
        self.assertNotEqual(d.resultado, self.adm.NAO)

    def test_ficha_de_catalogo_nunca_vira_ready(self):
        """O INDICE DE UMA COLHEITA NAO E A COLHEITA — e é por aqui que hoje
        entra tudo o que as receitas alcançam (ver provas/o_corte_de_cr1.py)."""
        cat = {"PERSON_ID": "p1", "MATERIALS_FOUND": 3, "ORCID_WORKS_DECLARED": 9}
        d = self.adm.decidir(cat, "T7", corrida="RT")
        self.assertEqual(d.resultado, self.adm.NAO_SE_APLICA)
        with self.assertRaises(Exception):
            self.adm.pronto_para_inteligencia(cat, d)

    def test_duas_corridas_nao_se_confundem(self):
        a = self.adm.decidir(dict(self.bom), "T7", corrida="RUN-A")
        b = self.adm.decidir(dict(self.bom), "T7", corrida="RUN-B")
        self.assertNotEqual(a.corrida, b.corrida)

    def test_a_saida_carrega_a_corrida_que_a_produziu(self):
        """Saída antiga numa pasta não pode ser atribuída à corrida nova."""
        d = self.adm.decidir(dict(self.bom), "T7", corrida="RUN-VELHA")
        self.assertEqual(
            self.adm.pronto_para_inteligencia(dict(self.bom), d)["CORRIDA"],
            "RUN-VELHA")
