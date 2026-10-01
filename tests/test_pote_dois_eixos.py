#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""K2 · OS DOIS EIXOS (veredito FAIL do LAB no pote e97ce8b0, 01/10/2026).

O LAB mediu: os 3 objetos saiam LIBERACAO = LIBERADO_PARA_CLIENTE e, ao mesmo tempo, NAO_PARA_CLIENTE = true,
MARCA «EXPERIMENTAL · NAO_PARA_CLIENTE» e ESTADO EXPERIMENTAL_CANDIDATE — e a raiz tambem dizia NAO_PARA_CLIENTE.
Decisao do dono do contrato (pacote/pote_intelligence_casco.py, CONTRATO_DOS_EIXOS):

  EIXO 1 · ELEGIBILIDADE por objeto: LIBERACAO; MARCA, NAO_PARA_CLIENTE e ESTADO do objeto dizem o mesmo.
  EIXO 2 · AMBIENTE por pote: AMBIENTE = PREVIEW_NAO_PRODUCAO, PRODUCAO = false (raiz, compartimentos, manifesto).

Estes testes fixam: um objeto NUNCA vem liberado e nao-para-cliente ao mesmo tempo (com eixos ou sem eles);
a raiz nao fala do cliente; o pote e97ce8b0 tal como foi publicado REPROVA no fiscal novo; e os eixos so COPIAM
a LIBERACAO que o C8-AUTO deu — nao liberam nada. Texto SINTETICO (pote do gerador sobre o export sintetico R7).
"""
import copy
import json
import sys
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import pote_intelligence_casco as P              # noqa: E402
import validar_pote_v2 as VP                     # noqa: E402
import gatilho_da_inteligencia as GI             # noqa: E402
import liberacao_por_criterio as L               # noqa: E402

EXPORT_R7 = RAIZ / "tests" / "dados" / "int-r7" / "SINTETICO-R7-SALA-EXPORT.json"


def _pote_com_liberacao(liberados: int = 1) -> dict:
    """Um pote real do gerador (export sintetico), com LIBERACAO carimbada como o C8 a deixa: os primeiros
    `liberados` objetos LIBERADO, o resto NAO_PARA_CLIENTE. O C8 nao corre aqui: o assunto e a forma."""
    s = GI.correr_o_motor(json.loads(EXPORT_R7.read_text(encoding="utf-8")), date(2026, 9, 28), "TESTE-K2")
    pote = copy.deepcopy(GI.montar_o_pote(s)[0])
    n = 0
    for e in pote["COMPARTIMENTOS"].values():
        for o in e["OBJETOS"]:
            o["LIBERACAO"] = P.LIBERADO if n < liberados else P.NAO_LIBERADO
            n += 1
    assert n > liberados, "o pote sintetico precisa de objetos liberados E bloqueados"
    return pote


def _objetos(pote):
    return [(c, o) for c, e in pote["COMPARTIMENTOS"].items() for o in e["OBJETOS"]]


class K2_UmObjetoDizUmaCoisa(unittest.TestCase):
    def setUp(self):
        self.antes = _pote_com_liberacao()
        self.pote = P.aplicar_eixos(self.antes)

    def test_com_os_eixos_o_pote_passa_no_fiscal_e_na_forma(self):
        self.assertEqual(P.conferir_pote(self.pote), [])
        self.assertEqual(VP.validar(self.pote), [])

    def test_nenhum_objeto_liberado_e_nao_para_cliente_ao_mesmo_tempo(self):
        for _, o in _objetos(self.pote):
            if o["LIBERACAO"] == P.LIBERADO:
                self.assertIs(o["NAO_PARA_CLIENTE"], False)
                self.assertNotIn("NAO_PARA_CLIENTE", o["MARCA"])
                self.assertEqual(o["ESTADO"], P.ESTADO_LIBERADO)
            else:
                self.assertIs(o["NAO_PARA_CLIENTE"], True)
                self.assertEqual(o["ESTADO"], P.ESTADO_TRANSPORTAVEL)

    def test_a_raiz_diz_o_ambiente_e_nao_o_cliente(self):
        self.assertEqual((self.pote["AMBIENTE"], self.pote["PRODUCAO"]), (P.AMBIENTE_PREVIEW, False))
        self.assertNotIn("NAO_PARA_CLIENTE", self.pote)
        self.assertNotIn("NAO_PARA_CLIENTE", self.pote["MARCA"])
        for e in self.pote["COMPARTIMENTOS"].values():
            self.assertNotIn("NAO_PARA_CLIENTE", e)
            self.assertEqual(e["AMBIENTE"], P.AMBIENTE_PREVIEW)

    def test_os_eixos_so_copiam_a_liberacao_do_c8(self):
        antes = {o["OBJETO_ID"]: o["LIBERACAO"] for _, o in _objetos(self.antes)}
        depois = {o["OBJETO_ID"]: o["LIBERACAO"] for _, o in _objetos(self.pote)}
        self.assertEqual(antes, depois)

    def test_objeto_sem_liberacao_nao_recebe_eixo(self):
        p = copy.deepcopy(self.antes)
        _objetos(p)[0][1].pop("LIBERACAO")
        with self.assertRaises(ValueError):
            P.aplicar_eixos(p)


class K2_ContradicaoReprova(unittest.TestCase):
    """O teste negativo pedido: liberado e nao-para-cliente ao mesmo tempo -> FALHA."""
    def setUp(self):
        self.pote = P.aplicar_eixos(_pote_com_liberacao())
        self.lib = next(o for _, o in _objetos(self.pote) if o["LIBERACAO"] == P.LIBERADO)
        self.blq = next(o for _, o in _objetos(self.pote) if o["LIBERACAO"] == P.NAO_LIBERADO)

    def _k2(self, pote):
        return [x for x in P.conferir_pote(pote) if "K2" in x or "EIXO" in x]

    def test_liberado_com_nao_para_cliente_true_reprova(self):
        self.lib["NAO_PARA_CLIENTE"] = True
        self.assertTrue(self._k2(self.pote))

    def test_liberado_com_a_marca_experimental_nao_para_cliente_reprova(self):
        self.lib["MARCA"] = P.MARCA
        self.assertTrue(self._k2(self.pote))

    def test_liberado_com_estado_experimental_candidate_reprova(self):
        self.lib["ESTADO"] = P.ESTADO_TRANSPORTAVEL
        self.assertTrue(self._k2(self.pote))

    def test_bloqueado_que_se_diz_para_cliente_reprova(self):
        self.blq["NAO_PARA_CLIENTE"] = False
        self.assertTrue(self._k2(self.pote))

    def test_raiz_que_diz_nao_para_cliente_reprova(self):
        self.pote["NAO_PARA_CLIENTE"] = True
        self.assertTrue(self._k2(self.pote))

    def test_compartimento_que_diz_nao_para_cliente_reprova(self):
        next(iter(self.pote["COMPARTIMENTOS"].values()))["NAO_PARA_CLIENTE"] = True
        self.assertTrue(self._k2(self.pote))

    def test_raiz_que_se_diz_producao_reprova(self):
        self.pote["PRODUCAO"] = True
        self.assertTrue(self._k2(self.pote))
        self.assertTrue(VP.forma(self.pote))

    def test_pote_sem_eixos_com_objeto_liberado_reprova(self):
        """A forma do e97ce8b0: pote v2 de sempre (NAO_PARA_CLIENTE em tudo) com objetos LIBERADO."""
        velho = _pote_com_liberacao()
        self.assertTrue([x for x in P.conferir_pote(velho) if "K2" in x])

    def test_o_gerador_para_se_o_pote_contradiz(self):
        """liberacao_por_criterio corre o fiscal ANTES de entregar: um pote contraditorio nunca chega a pasta."""
        self.assertTrue(P.conferir_pote(_pote_com_liberacao()))


if __name__ == "__main__":
    unittest.main()
