#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O WORKFLOW E A TRAVA TÊM DE CONCORDAR SOBRE O QUE É DESCARTÁVEL (SALA-AGUENTA, 2026-09-25).

O passo 2b5 do `banco-descartavel.yml` («a sala de espera sobrevive ao processo») cria o banco
próprio `sala` desde 14/09. A trava canónica de 17/09 (`guarda/banco_descartavel.py`, 497093a7)
ficou com uma lista de PERMISSÃO que não o trazia. A prova recusava-se a correr (SystemExit 2)
e o job ficou vermelho SEM medir a Sala — um vermelho que dizia «não correu» e foi lido como
«dívida herdada».

    UM PORTÃO QUE NÃO CORRE NÃO É UM PORTÃO FECHADO: É UM PORTÃO AUSENTE.

Este teste lê o workflow como TEXTO (sem analisador de YAML) e exige que cada banco que ele
cria, e cada BANCO_DESCARTAVEL_URL que ele entrega a uma prova, passe a trava. Se alguém
acrescentar um passo com um banco novo e esquecer a lista, é aqui que reprova — e não no CI,
calado, durante dias.
"""
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
from guarda import banco_descartavel as bd  # noqa: E402

WORKFLOW = os.path.join(RAIZ, ".github", "workflows", "banco-descartavel.yml")


def _texto():
    with open(WORKFLOW, encoding="utf-8") as f:
        return f.read()


class OsBancosDoWorkflowPassamATrava(unittest.TestCase):

    def test_cada_banco_criado_pelo_workflow_e_aceite(self):
        nomes = sorted(set(re.findall(r"create database\s+([A-Za-z0-9_]+)\s*;", _texto())))
        self.assertTrue(nomes, "o workflow deixou de criar bancos? a leitura falhou")
        for nome in nomes:
            url = "postgresql://postgres:descartavel@localhost:5432/%s" % nome
            self.assertEqual(bd.porque_nao_e_descartavel(url), "",
                             "o workflow cria o banco %r e a trava recusa-o" % nome)

    def test_cada_url_entregue_a_uma_prova_e_aceite(self):
        urls = sorted(set(re.findall(r"BANCO_DESCARTAVEL_URL:\s*(postgres(?:ql)?://\S+)", _texto())))
        self.assertTrue(urls)
        for url in urls:
            self.assertEqual(bd.porque_nao_e_descartavel(url), "",
                             "o workflow entrega %r a uma prova e a trava recusa-o" % url.split("@")[-1])

    def test_o_passo_2b5_usa_o_banco_sala_e_ele_passa(self):
        t = _texto()
        self.assertIn("create database sala;", t)
        self.assertIn("provas/a_sala_sobrevive_ao_processo.py", t)
        self.assertEqual(bd.porque_nao_e_descartavel(
            "postgresql://postgres:descartavel@localhost:5432/sala"), "")

    def test_a_sala_operacional_e_os_parecidos_continuam_fora(self):
        for nome in ("sala_italia", "sala-italia", "salas", "sala_de_espera", "Sala", "sala2"):
            self.assertTrue(bd.porque_nao_e_descartavel(
                "postgresql://postgres@localhost:54330/%s" % nome), nome)

    def test_sala_remota_continua_fora(self):
        self.assertTrue(bd.porque_nao_e_descartavel(
            "postgresql://postgres:x@db.abcdefgh.supabase.co:5432/sala"))


if __name__ == "__main__":
    unittest.main(verbosity=1)
