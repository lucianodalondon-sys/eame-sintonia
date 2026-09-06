#!/usr/bin/env python3
"""COBERTURA DE RÓTULO — seis estágios, e nenhum deles pode falar pelos outros.

O defeito que este arquivo existe para tornar impossível de repetir: uma métrica só,
chamada `LABEL_COVERAGE`, media **download** e era lida como **leitura**. O artefato
publicava `163/163 (100%)` com `PARSE_FAILURES = 0` enquanto **40** produtos saíam sem
uma cultura e sem um alvo. Ninguém mentiu; o número media outra coisa e ninguém disse qual.

As leis:

    163/163 DOWNLOADED  não implica  163/163 READ
    163/163 READ        não implica  163/163 USE_ROWS_STRUCTURED
    PARSER_FAILURE   != ABSENCE
    ZERO_PARSED_ROWS != ZERO_AUTHORIZED_USES
    GENUS_MATCH      != SPECIES_MATCH
"""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

ARTEFATO = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                        'IT-T4-001-portfolio-rotulo.json')
TESTO = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS-V1', 'testo')
PARES = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS-V1', 'IT-ROTULOS-PARES-V3.json')

ESTAGIOS = ('LABEL_DISCOVERY_COVERAGE', 'LABEL_DOWNLOAD_COVERAGE',
            'TEXT_EXTRACTION_COVERAGE', 'LABEL_READ_COVERAGE',
            'AUTHORIZED_USE_ROW_COVERAGE', 'USE_ROWS_STRUCTURED_COVERAGE')


def _art():
    with open(ARTEFATO, encoding='utf-8') as f:
        return json.load(f)


@unittest.skipUnless(os.path.exists(ARTEFATO), 'gêmeo regulatório ainda não gerado')
class TestSeisEstagios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.o = _art()
        cls.est = cls.o['COBERTURA_POR_ESTAGIO']

    def test_a_regua_plana_morreu(self):
        """Enquanto existir um `LABEL_COVERAGE.PCT`, alguém vai citá-lo como leitura."""
        velha = self.o['LABEL_COVERAGE']
        self.assertTrue(velha.get('DEPRECATED'), 'LABEL_COVERAGE voltou a ser régua viva')
        for campo in ('PCT', 'OBTAINED', 'TARGET', 'STATE'):
            self.assertNotIn(campo, velha,
                             'LABEL_COVERAGE.%s voltou: é o número que media download e '
                             'era lido como leitura' % campo)
        self.assertEqual(sorted(ESTAGIOS), sorted(velha['SUBSTITUIDA_POR']))

    def test_os_seis_existem_e_declaram_o_que_medem(self):
        for nome in ESTAGIOS:
            with self.subTest(estagio=nome):
                e = self.est[nome]
                self.assertIn('OBTAINED', e)
                self.assertIn('TARGET', e)
                self.assertIn('PCT', e)
                self.assertTrue(e.get('MEDE'), '%s não diz o que mede' % nome)
                self.assertEqual(round(100.0 * e['OBTAINED'] / e['TARGET'], 1), e['PCT'],
                                 '%s: PCT não é derivado de OBTAINED/TARGET' % nome)

    def test_a_leitura_nunca_pode_passar_o_download(self):
        d = self.est['LABEL_DOWNLOAD_COVERAGE']['OBTAINED']
        r = self.est['LABEL_READ_COVERAGE']['OBTAINED']
        u = self.est['AUTHORIZED_USE_ROW_COVERAGE']['OBTAINED']
        self.assertLessEqual(r, d, 'ler mais rótulos do que se baixou é impossível')
        self.assertLessEqual(u, r, 'linha de uso exige cultura E alvo; não pode passar a leitura')

    def test_o_estado_medido_e_este(self):
        """Os números são o retrato de hoje. Mudar o dado sem mudar aqui é o defeito."""
        self.assertEqual(163, self.est['LABEL_DISCOVERY_COVERAGE']['OBTAINED'])
        self.assertEqual(163, self.est['LABEL_DOWNLOAD_COVERAGE']['OBTAINED'])
        self.assertEqual(163, self.est['TEXT_EXTRACTION_COVERAGE']['OBTAINED'])
        self.assertEqual(123, self.est['LABEL_READ_COVERAGE']['OBTAINED'])
        self.assertEqual(96, self.est['AUTHORIZED_USE_ROW_COVERAGE']['OBTAINED'])
        self.assertEqual(128, self.est['USE_ROWS_STRUCTURED_COVERAGE']['OBTAINED'])

    def test_parse_failures_nao_e_mais_um_inteiro_solto(self):
        """`PARSE_FAILURES = 0` contava exceções e era lido como rendimento."""
        pf = self.o['PARSE_FAILURES']
        self.assertIsInstance(pf, dict, 'PARSE_FAILURES voltou a ser um inteiro')
        self.assertEqual(0, pf['EXCECOES'])
        self.assertEqual(40, pf['ZERO_ROW_YIELD'])


@unittest.skipUnless(os.path.exists(ARTEFATO), 'gêmeo regulatório ainda não gerado')
class TestDividaDeLeituraNaoEAusencia(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.o = _art()
        cls.d = cls.o['READ_STRUCTURING_DEBT']

    def test_a_divida_e_classificada_como_divida(self):
        self.assertEqual('READ/STRUCTURING_DEBT', self.d['CLASSE'])
        self.assertEqual('REGULATORY_ABSENCE', self.d['NAO_E'])
        self.assertEqual(40, self.d['COUNT'])

    def test_os_mudos_do_artefato_sao_exatamente_os_listados(self):
        mudos = sorted(p['REGISTRATION_ID'] for p in self.o['PRODUCTS']
                       if not p['CROP_TERMS_PRESENT'] and not p['ISSUES_FROM_SOURCE'])
        self.assertEqual(mudos, sorted(self.d['REGISTRATION_IDS']),
                         'a lista da dívida não é a lista real de produtos mudos')

    @unittest.skipUnless(os.path.isdir(TESTO), 'textos de rótulo não versionados')
    def test_todo_mudo_tem_texto_integral_no_repositorio(self):
        """É o que prova que o silêncio é do parser, e não do rótulo."""
        faltam = [r for r in self.d['REGISTRATION_IDS']
                  if not os.path.exists(os.path.join(TESTO, r + '.txt'))]
        self.assertEqual([], faltam, 'mudo sem texto no repo: aí não dá para afirmar nada')

    @unittest.skipUnless(os.path.exists(PARES), 'leitor canônico não versionado')
    def test_a_maioria_dos_mudos_ja_foi_lida_pelo_leitor_canonico(self):
        with open(PARES, encoding='utf-8') as f:
            v3 = json.load(f)
        sem = {x['REGISTRATION_ID'] for x in v3['LABELS_WITHOUT_SUPPORTED_PAIR_LIST']}
        lidos = sorted(r for r in self.d['REGISTRATION_IDS'] if r not in sem)
        self.assertEqual(sorted(self.d['IDS_JA_LIDOS_PELO_LEITOR_CANONICO']), lidos)
        self.assertEqual(31, len(lidos),
                         'se o leitor canônico lê 31 dos 40, chamar os 40 de ausência é falso')


@unittest.skipUnless(os.path.isdir(TESTO), 'textos de rótulo não versionados')
class TestAusenciaConferidaNoTextoIntegral(unittest.TestCase):
    """A afirmação «nenhum dos 163 nomeia Bactrocera oleae» é sobre 163, não sobre 123.

    Ela sobrevive — mas por pouco, e o "por pouco" é a lição: três rótulos citam o
    GÊNERO `Bactrocera`. Uma busca por gênero teria "refutado" uma afirmação correta.
    """

    ESPECIE = re.compile(r'bactrocera\s+ole[ae]', re.I)
    VERNACULO = re.compile(r"mosca\s+dell[’']?\s*oliv|mosca\s+delle\s+oliv", re.I)
    GENERO = re.compile(r'bactrocera', re.I)

    @classmethod
    def setUpClass(cls):
        cls.ids = sorted(p['REGISTRATION_ID'] for p in _art()['PRODUCTS'])
        cls.txt = {}
        for r in cls.ids:
            f = os.path.join(TESTO, r + '.txt')
            if os.path.exists(f):
                with open(f, encoding='utf-8', errors='replace') as fh:
                    cls.txt[r] = fh.read()

    def test_o_denominador_da_ausencia_e_o_conjunto_inteiro(self):
        self.assertEqual(163, len(self.ids))
        self.assertEqual(163, len(self.txt),
                         'afirmar ausência sobre 163 exige ter os 163 textos')

    def test_nenhum_rotulo_nomeia_a_especie_nem_o_vernaculo(self):
        esp = [r for r, t in self.txt.items() if self.ESPECIE.search(t)]
        ver = [r for r, t in self.txt.items() if self.VERNACULO.search(t)]
        self.assertEqual([], esp, 'Bactrocera oleae apareceu: a afirmação publicada cai')
        self.assertEqual([], ver, '"mosca dell\'olivo" apareceu: a afirmação publicada cai')

    def test_o_genero_aparece_e_isso_nao_refuta_nada(self):
        gen = sorted(r for r, t in self.txt.items() if self.GENERO.search(t))
        self.assertEqual(['009800', '012023', '014210'], gen,
                         'mudou quem cita o gênero — reconferir antes de mexer na afirmação')
        for r in gen:
            with self.subTest(registro=r):
                self.assertRegex(self.txt[r], r'(?i)bactrocera\s+dorsalis',
                                 'o gênero aparece sem ser dorsalis: reabrir a afirmação')


class TestOGeradorConcordaComOArtefato(unittest.TestCase):
    """Correção que vive só no arquivo gerado é apagada na próxima execução.

    Este teste alimenta o GERADOR com os PRODUCTS publicados e exige que ele devolva,
    campo a campo, o mesmo bloco de cobertura e a mesma dívida.
    """

    @unittest.skipUnless(os.path.exists(ARTEFATO), 'gêmeo regulatório ainda não gerado')
    def test_o_gerador_reproduz_a_cobertura_publicada(self):
        import italia_portfolio as ip
        o = _art()
        est = o['COBERTURA_POR_ESTAGIO']
        manifesto = {'TARGET_TOTAL': est['LABEL_DISCOVERY_COVERAGE']['TARGET'],
                     'LABELS_OBTAINED': est['LABEL_DOWNLOAD_COVERAGE']['OBTAINED']}
        self.assertEqual(est, ip._cobertura_por_estagio(o['PRODUCTS'], manifesto),
                         'o gerador e o artefato discordam: a correção some na próxima rodada')

    @unittest.skipUnless(os.path.exists(ARTEFATO), 'gêmeo regulatório ainda não gerado')
    def test_o_gerador_reproduz_a_divida_publicada(self):
        import italia_portfolio as ip
        o = _art()
        self.assertEqual(o['READ_STRUCTURING_DEBT'], ip._divida_de_leitura(o['PRODUCTS']))

    def test_o_gerador_nao_publica_mais_a_regua_plana(self):
        import italia_portfolio as ip
        velha = ip._cobertura_antiga_depreciada()
        self.assertTrue(velha['DEPRECATED'])
        for campo in ('PCT', 'OBTAINED', 'TARGET', 'STATE'):
            self.assertNotIn(campo, velha)


if __name__ == '__main__':
    unittest.main(verbosity=2)
