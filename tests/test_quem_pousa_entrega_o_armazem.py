#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D79 · QUEM POUSA NA SALA ENTREGA O ARMAZÉM E OS EXTRATORES (DEDUP-PARA-INSTALAR).

Sem isto, o decisor de versões nunca consegue re-extrair o RAW anterior e toda a
troca de receita de extrator vira NAO SEI. Os dois escritores da Sala:

  · `orquestrador.pela_porta`             — provado a correr, com `pousar` espiado
  · `coleta.rota_forward_documento`       — provado no código (AST): `atravessar`
    passa o armazém a `levar_a_espera`, e esta passa-o, com os extratores, a `pousar`
"""
import ast
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
for g in (str(RAIZ), str(RAIZ / "orquestrador"), str(RAIZ / "admissao")):
    if g not in sys.path:
        sys.path.insert(0, g)


def _chamadas(caminho, funcao, alvo):
    """As chamadas a `alvo` (nome final) dentro da função `funcao` do ficheiro."""
    arvore = ast.parse(Path(caminho).read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name == funcao:
            return [c for c in ast.walk(no) if isinstance(c, ast.Call)
                    and (getattr(c.func, "attr", None) == alvo or getattr(c.func, "id", None) == alvo)]
    raise AssertionError("funcao %s nao encontrada em %s" % (funcao, caminho))


def _kw(chamada):
    return {k.arg: k.value for k in chamada.keywords}


class ARotaForwardEntrega(unittest.TestCase):
    ROTA = RAIZ / "coleta" / "rota_forward_documento.py"

    def test_levar_a_espera_passa_armazem_e_extratores_ao_pousar(self):
        (c,) = _chamadas(self.ROTA, "levar_a_espera", "pousar")
        kw = _kw(c)
        self.assertIn("armazem", kw)
        self.assertEqual(getattr(kw["armazem"], "id", None), "armazem")
        self.assertIn("extratores", kw)

    def test_atravessar_passa_o_armazem_a_levar_a_espera(self):
        (c,) = _chamadas(self.ROTA, "atravessar", "levar_a_espera")
        self.assertEqual(getattr(_kw(c).get("armazem"), "id", None), "armazem")


#: O recibo que o dono devolve quando nao ha o que pousar (sala_de_espera.pousar).
VAZIO = {"ESTADO": None, "RUN_ID": "R-TESTE", "FICHEIRO": None, "MORADA": None,
         "UNIDADES": 0, "BACKEND": "FICHEIRO", "CANONICO": False,
         "PORQUE": "nenhuma unidade admitida: nao ha o que pousar"}


class OOrquestradorEntrega(unittest.TestCase):

    def test_pela_porta_entrega_o_armazem_e_o_registo_ao_pousar(self):
        import orquestrador as orq
        from coleta import extratores_de_texto as ext
        armazem = object()
        with mock.patch.object(orq.espera, "pousar", return_value=VAZIO) as p, \
                mock.patch.object(orq.adm, "escrever", return_value=None):
            orq.pela_porta([], "T5", "R-TESTE", armazem=armazem)
        _, kw = p.call_args
        self.assertIs(kw.get("armazem"), armazem)
        self.assertEqual(set(kw.get("extratores") or {}), set(ext.registo()))

    def test_correr_passa_o_seu_armazem_a_pela_porta(self):
        (c,) = _chamadas(RAIZ / "orquestrador" / "orquestrador.py", "correr", "pela_porta")
        self.assertEqual(getattr(_kw(c).get("armazem"), "id", None), "armazem")


if __name__ == "__main__":
    unittest.main(verbosity=2)
