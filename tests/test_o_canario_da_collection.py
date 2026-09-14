#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS QUINZE MANEIRAS DE FABRICAR UM «PASS» NESTA MISSAO.

O brief nomeou-as. Cada uma tem aqui uma guarda, e a guarda mede a
PROPRIEDADE — nunca o estado de hoje.

    UMA GUARDA PRESA AO ESTADO DE HOJE REPROVA O PROGRESSO DE AMANHA.

Isso ja custou tres testes a esta linha de missoes (§95) e quase custou um
quarto (§99.7). Por isso nenhuma guarda aqui diz «T2 nao tem regra» ou «o
canario e T4»: dizem «T2 so pode ter regra se a medicao dela abrir o portao»
e «o canario nao pode ser quem tem a peca reprovada».
"""
import importlib.util
import io
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao as adm  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "canario_t", os.path.join(RAIZ, "provas", "o_canario_da_collection.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

VEREDICTO_T2 = os.path.join(RAIZ, "data", "derivados", "A-REGRA-DE-T2.json")

_CACHE = {}


def _censo():
    if "c" not in _CACHE:
        _CACHE["c"] = C.censo()
    return _CACHE["c"]


def _t2_medido():
    if not os.path.isfile(VEREDICTO_T2):
        return None
    with io.open(VEREDICTO_T2, encoding="utf-8") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════════
# 1 · 12 · MUDAR A REGRA SO PARA PRODUZIR SIM
# ══════════════════════════════════════════════════════════════════════════
class ARegraNaoSeMudaParaOExamePassar(unittest.TestCase):

    def test_T2_so_pode_ter_regra_se_a_medicao_dela_abrir_o_portao(self):
        """⚠️ ESTA GUARDA NAO DIZ «T2 NUNCA TEM REGRA».

        Dizer isso seria congelar o estado de hoje e reprovar a missao que um
        dia medir T2 de novo com um mecanismo melhor. O que ela guarda e a
        LIGACAO: a regra so existe se o dono da resposta disser que pode.

            NAO «T2 NAO TEM REGRA», MAS «A REGRA SEGUE QUEM A MEDIU».
        """
        v = _t2_medido()
        if v is None:
            self.skipTest("`provas/a_regra_de_t2.py` ainda nao correu")
        tem_regra = "T2" in adm.PERGUNTAS_DO_UNIVERSO
        portao_aberto = v.get("T2_RULE_IMPLEMENTED") == "YES"
        if tem_regra and not portao_aberto:
            self.fail(
                "T2 ganhou regra com o portao FECHADO em %s. A medicao diz "
                "que a lista que separa o gabarito e feita de dias da semana "
                "e nomes de departamento (generalizacao %s) — escrever uma "
                "lista na mesma assim e mudar a pergunta para gostar da "
                "resposta" % (v.get("CONDICAO_QUE_FECHOU"),
                              v.get("GENERALIZACAO")))

    def test_nenhum_universo_ganha_regra_sem_estar_na_taxonomia(self):
        """ATAQUE 2 · usar classe fora do universo.

        Um universo inventado na porta e uma segunda taxonomia a nascer — e
        duas taxonomias sobre a mesma pergunta divergem.
        """
        from pedido import ALVOS
        intrusos = sorted(set(adm.PERGUNTAS_DO_UNIVERSO) - set(ALVOS))
        self.assertEqual([], intrusos,
                         "a porta julga universos que a taxonomia nao "
                         "conhece: %s" % intrusos)

    def test_a_porta_sem_regra_responde_NAO_SE_APLICA_e_nao_NAO(self):
        """ATAQUES 7 e 8 · `NAO_SE_APLICA` virar SIM, `UNKNOWN` virar NO.

        As tres respostas sao diferentes de proposito: «nao pertence», «nao
        ha regra» e «nao sei» levam a acoes diferentes.
        """
        sem_regra = next((a for a in ("T2", "T5", "T10", "T11")
                          if a not in adm.PERGUNTAS_DO_UNIVERSO), None)
        if sem_regra is None:
            self.skipTest("todos os universos de teste ganharam regra")
        item = {"id": "x", "texto": "bollettino agrometeorologico regionale",
                "source_id": "IT-T2-002", "fact_time": "2026-09-01",
                "captured_at": "2026-09-01"}
        d = adm.decidir(item, sem_regra)
        self.assertNotEqual(adm.SIM, d.resultado,
                            "a porta disse SIM sem regra escrita")
        self.assertNotEqual(adm.NAO, d.resultado,
                            "«nao ha regra» virou «nao pertence» — sao "
                            "respostas diferentes e levam a acoes diferentes")


# ══════════════════════════════════════════════════════════════════════════
# 11 · O SCRAP DECLARADO BLOCKER SEM PROVA
# ══════════════════════════════════════════════════════════════════════════
class OScrapNaoHerdaOBuracoDeNinguem(unittest.TestCase):
    """⚠️ O SCRAP E A PECA EM FALTA MAIS VISIVEL DESTA CASA, e por isso atrai
    para si qualquer buraco que ninguem nomeou. «Falta o SCRAP» e verdade e
    nao e resposta.

        «O SCRAP AINDA FALTA» != «O SCRAP E O QUE BLOQUEIA».
    """

    def test_o_teste_do_scrap_pergunta_pela_classe_e_nao_pela_ausencia(self):
        r = C.o_scrap_fecharia(_censo())
        self.assertIn("CLASSES_QUE_O_SCRAP_SERVE", r,
                      "o teste do SCRAP respondeu sem nomear a classe que ele "
                      "serve — isso e uma impressao, nao uma medicao")
        if r["SCRAP_WOULD_CLOSE_CURRENT_GAP"] == "NO":
            self.assertNotEqual("—", r["PORQUE_NAO"],
                                "disse NO sem dizer o que ainda falta depois "
                                "de o SCRAP chegar")

    def test_dar_aquisicao_a_classe_do_scrap_e_o_unico_teste_que_conta(self):
        """O SCRAP entrega AQUISICAO. Entao o teste e: dando-lhe a aquisicao
        de graca, a classe que ele serve chega a READY?"""
        r = C.o_scrap_fecharia(_censo())
        resto = r.get("DANDO_LHES_A_AQUISICAO_AINDA_FALTA") or {}
        fecharia = r["SCRAP_WOULD_CLOSE_CURRENT_GAP"] == "YES"
        self.assertEqual(fecharia, all(not v for v in resto.values()),
                         "o veredicto do SCRAP nao segue o que sobra depois "
                         "de lhe dar a aquisicao: %s" % resto)

    def test_o_blocker_do_canario_diz_se_e_o_scrap_ou_nao(self):
        v = _t2_medido()
        fechado = bool(v) and v.get("O_QUE_FALHA") == "MECANISMO"
        can = C.o_canario(_censo(), fechado)
        b = can["BLOCKER_REAL"]
        if can["CANONICAL_CANARY_CLASS_RECOMENDADA"] != "NONE":
            self.assertIn("E_O_SCRAP", b,
                          "o blocker do canario nao responde se e o SCRAP — e "
                          "um buraco sem nome vira «o SCRAP» sozinho")


# ══════════════════════════════════════════════════════════════════════════
# 6 · DUAS METADES CONTADAS COMO E2E
# ══════════════════════════════════════════════════════════════════════════
class DuasMetadesNaoSaoUmaEstrada(unittest.TestCase):

    def test_o_cruzamento_e_um_E_e_nao_um_OU(self):
        """Trocar o `and` por `or` daria uma lista de quase-canarios e um PASS
        por metades — o defeito que esta linha passou tres missoes a apanhar.
        """
        for l in _censo():
            tem_tudo = (l["CANONICAL_ACQUISITION"] == "YES"
                        and l["ADMISSION_RULE"] == "YES"
                        and l["STRUCTURED_SUPPORTED"] == "YES")
            self.assertEqual("YES" if tem_tudo else "NO", l["CAN_REACH_READY"],
                             "%s atravessa por soma de metades" % l["CLASS"])

    def test_quem_atravessa_hoje_e_quem_devia_ser_canario_sao_campos_diferentes(self):
        """⚠️ JUNTAR OS DOIS NUM CAMPO SO FARIA UMA RECOMENDACAO PARECER UMA
        OBSERVACAO. «T4 devia ser o canario» nao e «T4 atravessa»."""
        with io.open(os.path.join(RAIZ, "provas",
                                  "o_canario_da_collection.py"),
                     encoding="utf-8") as f:
            fonte = f.read()
        self.assertIn("CANONICAL_CANARY_CLASS", fonte)
        self.assertIn("CANONICAL_CANARY_CLASS_RECOMENDADA", fonte)
        cruzam = [l for l in _censo() if l["CAN_REACH_READY"] == "YES"]
        v = _t2_medido()
        can = C.o_canario(_censo(),
                          bool(v) and v.get("O_QUE_FALHA") == "MECANISMO")
        if not cruzam:
            self.assertNotEqual(
                can["CANONICAL_CANARY_CLASS_RECOMENDADA"], "",
                "ninguem atravessa e nenhuma recomendacao foi dada: a "
                "medicao para na parede em vez de a atravessar")


# ══════════════════════════════════════════════════════════════════════════
# 14 · READY SURGIR SEM SIM  ·  9 · ERROR VIRAR REJECTED
# ══════════════════════════════════════════════════════════════════════════
class ReadySoNasceDeUmSim(unittest.TestCase):

    def _decisao(self, resultado):
        return adm.Decisao(item="x", universo="T3", resultado=resultado,
                           regra="r", motivo="m", evidencia={}, corrida="c")

    def test_os_quatro_resultados_que_nao_sao_SIM_nao_produzem_READY(self):
        for r in (adm.NAO, adm.NAO_SEI, adm.NAO_SE_APLICA, adm.ERRO):
            with self.subTest(resultado=r):
                with self.assertRaises(ValueError,
                                       msg="%s produziu READY" % r):
                    adm.pronto_para_inteligencia({"texto": "t"},
                                                 self._decisao(r))

    def test_o_SIM_produz_READY_e_ele_nomeia_a_corrida(self):
        u = adm.pronto_para_inteligencia({"texto": "t"},
                                         self._decisao(adm.SIM))
        self.assertEqual("PRONTO_PARA_INTELIGENCIA", u["ESTADO"])
        self.assertEqual("c", u["CORRIDA"],
                         "a unidade pronta perdeu a corrida de onde veio")

    def test_ERRO_e_NAO_continuam_a_ser_palavras_diferentes(self):
        self.assertNotEqual(adm.ERRO, adm.NAO)
        self.assertNotEqual(adm.NAO_SEI, adm.NAO)
        self.assertNotEqual(adm.NAO_SE_APLICA, adm.NAO)


# ══════════════════════════════════════════════════════════════════════════
# 10 · FIXTURE SUBSTITUIR FONTE REAL  ·  3 · COMECAR O TESTE NA ADMISSION
# ══════════════════════════════════════════════════════════════════════════
class OCensoNaoFingeQueCorreu(unittest.TestCase):

    def test_o_censo_mede_contrato_e_diz_que_e_contrato(self):
        """⚠️ UM CENSO QUE PARECE UMA CORRIDA E PIOR DO QUE UM CENSO.
        Ele mede o que esta DECLARADO. Se alguem o ler como «isto correu»,
        passa a haver uma prova de execucao que nunca executou nada.

            MEDIR O CONTRATO NAO E MEDIR A CORRIDA.
        """
        doc = C.__doc__ or ""
        self.assertIn("nao corre executor nenhum", doc.lower().replace("ã", "a")
                      .replace("é", "e").replace("ó", "o"))

    def test_o_censo_nao_abre_banco_nem_chama_executor(self):
        import ast
        with io.open(os.path.join(RAIZ, "provas",
                                  "o_canario_da_collection.py"),
                     encoding="utf-8") as f:
            fonte = f.read()
        chamadas = set()
        for no in ast.walk(ast.parse(fonte)):
            if isinstance(no, ast.Call):
                f = no.func
                if isinstance(f, ast.Attribute):
                    chamadas.add(f.attr)
                elif isinstance(f, ast.Name):
                    chamadas.add(f.id)
        for proibida in ("correr", "atravessar", "admitir", "aplicar",
                         "preservar", "pousar", "connect"):
            self.assertNotIn(proibida, chamadas,
                             "o censo passou a EXECUTAR: %s" % proibida)


# ══════════════════════════════════════════════════════════════════════════
# O PAIS NAO ESCOLHE EXECUTOR — a medicao anterior so perguntou por IT
# ══════════════════════════════════════════════════════════════════════════
class UmPaisSoNaoEUmaResposta(unittest.TestCase):

    def test_a_lista_de_executores_nao_muda_com_o_pais(self):
        self.assertEqual([], C.executor_nao_depende_do_pais(),
                         "o executor passou a depender do pais: entao «T2 e o "
                         "unico que declara colheita» era uma frase sobre a "
                         "Italia a passar por uma frase sobre a casa")


if __name__ == "__main__":
    unittest.main()
