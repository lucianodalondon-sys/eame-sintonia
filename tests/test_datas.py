# -*- coding: utf-8 -*-
"""Data lida errada nao levanta excecao — publica um numero errado.

Em 2026-09-04 a camada territorial media frescor com uma data truncada:

    datas_no_texto('2026-08-24')  ->  2026-08-02

A alternancia do dia estava escrita `(0?[1-9]|[12]\\d|3[01])`. Regex casa
*leftmost-first*: contra "24" o motor pega `0?[1-9]` no "2" e, como nada depois
exige retrocesso, para ali. Em `dd/mm/aaaa` o `[-/]` seguinte forcava o
retrocesso e o formato passava — por isso ninguem viu.

    257 DAS 365 DATAS ISO DE 2026 VOLTAVAM ERRADAS, E SEMPRE PARA TRAS.

O erro tinha direcao: empurrava tudo para o comeco do mes e fazia toda fonte
parecer mais velha do que era. Estes testes existem para que a ordem das
alternativas nunca mais seja trocada por acidente.
"""
import datetime
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))


class TestDataNaoTrunca(unittest.TestCase):

    def setUp(self):
        import fonte_territorial
        self.ler = fonte_territorial.datas_no_texto

    def test_o_caso_que_quebrou(self):
        self.assertEqual([datetime.date(2026, 8, 24)], self.ler('2026-08-24'))

    def test_o_ano_inteiro_em_quatro_formatos(self):
        """Se um formato truncar um dia, o ano inteiro acusa."""
        formatos = ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y')
        for fmt in formatos:
            errados = []
            dia = datetime.date(2026, 1, 1)
            while dia.year == 2026:
                lido = self.ler(dia.strftime(fmt))
                if not lido or lido[0] != dia:
                    errados.append((dia.isoformat(), lido))
                dia += datetime.timedelta(days=1)
            self.assertEqual([], errados[:5],
                             '%s truncou %d datas de 365' % (fmt, len(errados)))

    def test_dia_de_dois_digitos_nao_vira_o_digito_das_dezenas(self):
        """O sintoma exato do defeito: 24 virava 2, 31 virava 3, 15 virava 1."""
        for texto, esperado in (('2026-08-24', 24), ('2026-08-31', 31),
                                ('2026-01-15', 15), ('2026-12-25', 25)):
            self.assertEqual(esperado, self.ler(texto)[0].day, texto)

    def test_data_impossivel_e_recusada_em_vez_de_arredondada(self):
        for texto in ('2026-13-01', '2026-02-30', '2026-00-10'):
            self.assertEqual([], self.ler(texto), texto)

    def test_duas_datas_no_mesmo_texto_saem_as_duas_inteiras(self):
        lido = self.ler('publicado em 2026-08-31 e revisto em 01/09/2026')
        self.assertEqual([datetime.date(2026, 8, 31), datetime.date(2026, 9, 1)], lido)


if __name__ == '__main__':
    unittest.main()
