#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PORTA OPERACIONAL DA COLLECTION — dez perguntas, e nenhuma e opiniao.

    py -m unittest test_persistencia_operacional

Nasceu do primeiro canario operacional real (IT-T3-010,
`XX-T3-2026-09-18-130704-dfbbd422a1b06e7c`): a aquisicao funcionou, os bytes
ficaram preservados, e o fluxo parou porque a Collection so sabia ligar-se a
uma bancada DESCARTAVEL. A Sala persistente existia; a bancada operacional da
Collection, nao.

Estes testes nao tocam rede nem banco: medem a COMPOSICAO, que e onde a
decisao vive. A prova contra PostgreSQL real e outra, e corre a seguir.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

from orquestrador import persistencia as P  # noqa: E402
from guarda import banco_operacional as OP  # noqa: E402
from guarda import banco_descartavel as DESC  # noqa: E402
from guarda import preservar_coleta as PC  # noqa: E402

# ⚠️ Desde 20/09/2026 a memoria OPERACIONAL exige a raiz dos bytes
# (`SINTONIA_ARMAZEM_RAIZ`, fora da arvore): memoria operacional com bytes em
# `<repo>/XX/` foi o defeito que apagou a Big Collection 2. As provas do modo
# operacional declaram uma raiz temporaria propria — o que a lei pede a quem
# corre a serio. O caso «sem raiz» prova-se em
# tests/test_armazem_operacional_protegido.py.
import tempfile  # noqa: E402
ARMAZEM = tempfile.mkdtemp(prefix="armazem-oper-prova-")

#: ⚠️ O VALOR TEM DE SE DECLARAR FALSO, E NÃO BASTA O NOME DA CONSTANTE DIZÊ-LO.
#: Aqui esteve `SENHA-QUE-NAO-PODE-APARECER-EM-LADO-NENHUM` — uma frase que
#: anuncia ser fixture a quem LÊ, e que para o scanner é apenas uma senha
#: literal com forma de senha. `guarda/social_guarda.py` reprovou-a, e reprovou
#: bem: ela não usa nenhuma das palavras que o contrato dele reconhece.
#:
#:     FIXTURE WITH SECRET SHAPE IS SECRET TO THE SCANNER.
#:     ENTAO A FIXTURE DECLARA-SE, OU CONSTROI-SE EM TEMPO DE EXECUCAO.
#:
#: `dummy` está na família de placeholders que a guarda aceita, e a asserção que
#: importa não mudou: estas três DSN continuam a levar uma senha, e os testes de
#: não-vazamento continuam a exigir que ela NÃO apareça em texto nem em exceção.
#: O que mudou foi a forma do valor — o propósito da prova ficou intacto.
SENHA = "dummy-password"
OPERACIONAL_OK = "postgresql://postgres:%s@127.0.0.1:54330/sala_italia" % SENHA
DESCARTAVEL_OK = "postgresql://postgres:%s@localhost:54329/descartavel" % SENHA
PRODUCAO = "postgresql://u:%s@db.abcdefgh.supabase.co:5432/postgres" % SENHA


class APortaOperacional(unittest.TestCase):

    def test_A_modo_descartavel_continua_a_funcionar(self):
        """A rota que ja existia nao pode mudar de semantica."""
        r = P.dependencias_do_runtime({P.VARIAVEL: DESCARTAVEL_OK})
        self.assertEqual(r.ESTADO, P.DESCARTAVEL)
        self.assertIsNotNone(r.memoria)
        self.assertIsNotNone(r.banco_do_rastro)

    def test_B_descartavel_invalido_continua_recusado(self):
        with self.assertRaises(P.BancoRecusado):
            P.dependencias_do_runtime({P.VARIAVEL: PRODUCAO})

    def test_C_modo_operacional_autorizado_liga(self):
        r = P.dependencias_do_runtime({P.VARIAVEL_OPERACIONAL: OPERACIONAL_OK, PC.VARIAVEL_DA_RAIZ: ARMAZEM})
        self.assertEqual(r.ESTADO, P.OPERACIONAL)
        self.assertIsNotNone(r.memoria)
        self.assertIsNotNone(r.banco_do_rastro)

    def test_D_nenhuma_declarada_e_explicito(self):
        """Ausencia diz-se; nao se preenche."""
        r = P.dependencias_do_runtime({})
        self.assertEqual(r.ESTADO, P.AUSENTE)
        self.assertIsNone(r.memoria)
        self.assertIsNone(r.banco_do_rastro)
        self.assertIn("RAW_OBSERVATIONS sai vazio", r.PORQUE)

    def test_E_operacional_nao_autorizada_recusa_antes_de_escrever(self):
        for url in (
            "postgresql://postgres:x@127.0.0.1:54330/outro_banco",
            "postgresql://postgres:x@10.1.2.3:54330/sala_italia",
            PRODUCAO,
        ):
            with self.assertRaises(P.BancoOperacionalRecusado):
                P.dependencias_do_runtime({P.VARIAVEL_OPERACIONAL: url})

    def test_F_producao_nunca_e_escolhida_automaticamente(self):
        r = P.dependencias_do_runtime({"SUPABASE_DB_URL": PRODUCAO})
        self.assertEqual(r.ESTADO, P.AUSENTE)
        self.assertIsNone(r.memoria)

    def test_G_config_da_sala_nao_liga_memoria_da_collection(self):
        """SINTONIA_SALA_DSN e da SALA. Outro dono, outra pergunta."""
        r = P.dependencias_do_runtime({
            "SINTONIA_SALA_DSN": OPERACIONAL_OK,
            "SINTONIA_SALA_BACKEND": "POSTGRES"})
        self.assertEqual(r.ESTADO, P.AUSENTE)
        self.assertIsNone(r.memoria)

    def test_H_duas_configuracoes_falham_fechado(self):
        with self.assertRaises(P.ModosEmConflito):
            P.dependencias_do_runtime({P.VARIAVEL: DESCARTAVEL_OK,
                                       P.VARIAVEL_OPERACIONAL: OPERACIONAL_OK, PC.VARIAVEL_DA_RAIZ: ARMAZEM})

    def test_I_segredo_nunca_aparece_no_recibo(self):
        r = P.dependencias_do_runtime({P.VARIAVEL_OPERACIONAL: OPERACIONAL_OK, PC.VARIAVEL_DA_RAIZ: ARMAZEM})
        texto = "%s %s %s" % (r.PORQUE, r.MORADA, r.para_json())
        self.assertNotIn(SENHA, texto)
        self.assertIn("127.0.0.1:54330/sala_italia", r.MORADA)
        # E o mesmo para as recusas: o motivo nao repete a URL inteira.
        try:
            P.dependencias_do_runtime({P.VARIAVEL_OPERACIONAL: PRODUCAO})
        except P.BancoOperacionalRecusado as ex:
            self.assertNotIn(SENHA, str(ex))

    def test_J_importar_nao_tem_efeito_lateral(self):
        """Importar nao liga nada e nao mexe no ambiente."""
        antes = dict(os.environ)
        import importlib
        importlib.reload(OP)
        self.assertEqual(dict(os.environ), antes)


class AsDuasListasNaoSeMisturam(unittest.TestCase):

    def test_allowlist_descartavel_intacta(self):
        """DISPOSABLE_GUARD_UNCHANGED_SEMANTICALLY."""
        self.assertEqual(DESC.BANCOS_PERMITIDOS,
                         ("descartavel", "derivado", "social", "objeto"))

    def test_sala_italia_nao_entrou_na_lista_descartavel(self):
        self.assertNotIn("sala_italia", DESC.BANCOS_PERMITIDOS)

    def test_descartavel_nao_passa_pelo_guarda_operacional(self):
        """Um banco descartavel NAO e uma bancada operacional."""
        self.assertNotEqual(OP.porque_nao_e_operacional(DESCARTAVEL_OK), "")

    def test_operacional_nao_passa_pelo_guarda_descartavel(self):
        self.assertNotEqual(DESC.porque_nao_e_descartavel(OPERACIONAL_OK), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
