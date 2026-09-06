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

MANIFESTO = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                         'IT-T4-001-etichette-manifest.json')

ESTAGIOS = ('LABEL_DISCOVERY_COVERAGE', 'LABEL_DOWNLOAD_COVERAGE',
            'TEXT_EXTRACTION_COVERAGE', 'LABEL_READ_COVERAGE',
            'CROP_TERM_AND_ISSUE_BOTH_PRESENT_COVERAGE',
            'MODE_OF_ACTION_DECLARED_COVERAGE')


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

    def test_a_escada_nao_carrega_um_leitor_de_fora(self):
        """`USE_ROWS_STRUCTURED = 128` vinha depois de `READ = 123` e lia-se como o
        degrau seguinte. Nao e: 128 > 123, e 31 dos 40 que este artefacto nao leu
        estao dentro dos 128. Sao dois leitores, nao dois estagios."""
        self.assertNotIn('USE_ROWS_STRUCTURED_COVERAGE', self.est,
                         'o leitor canonico voltou para dentro da escada')
        fora = self.o['COBERTURA_DO_LEITOR_CANONICO']
        self.assertIn('NAO_E_DERIVADO_DESTE_ARTEFACTO', fora)
        self.assertTrue(fora['UNIVERSOS_BATEM'],
                        'os dois leitores nao descrevem o mesmo universo de rotulos')
        self.assertEqual(128, fora['ROTULOS_COM_PAR'])

    def test_a_lei_nao_mora_entre_os_estagios(self):
        """`LEI` era uma lista solta no meio de dicionarios de estagio: quem
        iterasse o mapa esperando {OBTAINED,TARGET,PCT,MEDE} tropecava nela."""
        self.assertNotIn('LEI', self.est)
        self.assertIn('PARSER_FAILURE != ABSENCE', self.o['LEI_DA_COBERTURA'])
        self.assertIn('UNCONFIRMED_SILENCE != DEBT != ABSENCE', self.o['LEI_DA_COBERTURA'])

    def test_o_nome_do_estagio_nao_rouba_um_termo_que_ja_tem_dono(self):
        """`AUTHORIZED_USE_ROW` vale 19 nesta casa — cultura, alvo e dose na MESMA
        linha. Chamar de 96 uma conjuncao de presencas inflava o termo em 5x."""
        self.assertNotIn('AUTHORIZED_USE_ROW_COVERAGE', self.est)
        e = self.est['CROP_TERM_AND_ISSUE_BOTH_PRESENT_COVERAGE']
        self.assertIn('AUTHORIZED_USE_ROW', e['NAO_E'])
        self.assertNotIn('linha de uso autorizado', e['MEDE'])

    def test_o_primeiro_degrau_pode_falhar(self):
        """`OBTAINED := TARGET` dava 100% para qualquer entrada. Um degrau que nao
        pode falhar nao mede a descoberta de nada."""
        import italia_portfolio as ip
        fingido = ip._cobertura_por_estagio(
            self.o['PRODUCTS'], {'TARGET_TOTAL': 200, 'ATTEMPTED': 150,
                                 'LABELS_OBTAINED': 150})
        self.assertLess(fingido['LABEL_DISCOVERY_COVERAGE']['PCT'], 100.0)
        self.assertLessEqual(fingido['TEXT_EXTRACTION_COVERAGE']['PCT'], 100.0)

    def test_o_estagio_de_texto_olha_mesmo_para_o_diretorio_que_nomeia(self):
        import italia_portfolio as ip
        do_disco = ip._textos_no_repo()
        self.assertEqual(len(do_disco),
                         self.est['TEXT_EXTRACTION_COVERAGE']['OBTAINED'],
                         'o estagio de extracao nao conta os ficheiros que nomeia')
        self.assertTrue(all(t >= ip.MIN_BYTES_DO_TEXTO for t in do_disco.values()))

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
        u = self.est['CROP_TERM_AND_ISSUE_BOTH_PRESENT_COVERAGE']['OBTAINED']
        self.assertLessEqual(r, d, 'ler mais rótulos do que se baixou é impossível')
        self.assertLessEqual(u, r, 'cultura E alvo não pode passar cultura OU alvo')
        self.assertLessEqual(self.est['LABEL_DOWNLOAD_COVERAGE']['OBTAINED'],
                             self.est['LABEL_DISCOVERY_COVERAGE']['TARGET'])

    def test_o_estado_medido_e_este(self):
        """Os números são o retrato de hoje. Mudar o dado sem mudar aqui é o defeito."""
        self.assertEqual(163, self.est['LABEL_DISCOVERY_COVERAGE']['OBTAINED'])
        self.assertEqual(163, self.est['LABEL_DOWNLOAD_COVERAGE']['OBTAINED'])
        self.assertEqual(163, self.est['TEXT_EXTRACTION_COVERAGE']['OBTAINED'])
        self.assertEqual(123, self.est['LABEL_READ_COVERAGE']['OBTAINED'])
        self.assertEqual(96, self.est['CROP_TERM_AND_ISSUE_BOTH_PRESENT_COVERAGE']['OBTAINED'])
        self.assertEqual(128, self.o['COBERTURA_DO_LEITOR_CANONICO']['ROTULOS_COM_PAR'])

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
        """É o que prova que o silêncio é do parser, e não do rótulo.

        `COM_TEXTO_INTEGRAL_NO_REPO` era `len(ids)` — igual a `COUNT` por construção,
        logo incapaz de discordar de si mesmo. Esvaziar os 40 ficheiros não reprovava
        nada. Agora o número vem do disco, com piso de bytes.
        """
        import italia_portfolio as ip
        pequenos = []
        for r in self.d['REGISTRATION_IDS']:
            caminho = os.path.join(TESTO, r + '.txt')
            if not os.path.exists(caminho) or os.path.getsize(caminho) < ip.MIN_BYTES_DO_TEXTO:
                pequenos.append(r)
        self.assertEqual([], pequenos, 'mudo sem texto de verdade: aí não dá para afirmar nada')
        self.assertEqual(len(self.d['REGISTRATION_IDS']),
                         self.d['COM_TEXTO_INTEGRAL_NO_REPO'])
        self.assertEqual(ip.MIN_BYTES_DO_TEXTO, self.d['MIN_BYTES_DO_TEXTO'])

    def test_a_divida_provada_e_o_silencio_nao_provado_sao_baldes_diferentes(self):
        """Perguntar só ao leitor canónico mandava 9 para `NAO SEI`, e 7 deles têm a
        resposta escrita no texto que este mesmo bloco cita como prova.

        `015630` tem uma secção literal `COLTURE AUTORIZZATE` com
        `VITE / Contro peronospora (Plasmopara viticola): impiegare 270 g/ha`. Publicá-lo
        como «não sei se o rótulo declara uso» é o espelho do defeito original: antes
        chamava-se ausência ao silêncio, depois chamava-se «não sei» a uma dívida medida.
        """
        conf = self.d['CONFIRMED_PARSER_DEBT']
        nao = self.d['UNCONFIRMED_SILENCE']
        self.assertEqual(38, conf['COUNT'])
        self.assertEqual(2, nao['COUNT'])
        self.assertEqual(31, len(conf['PROVA_POR_LEITOR_CANONICO']))
        self.assertEqual(7, len(conf['PROVA_POR_TEXTO_ARQUIVADO']))
        self.assertEqual(self.d['COUNT'], conf['COUNT'] + nao['COUNT'])
        self.assertEqual('NAO SEI', nao['CLASSE'])
        self.assertIn('REGULATORY_ABSENCE', nao['NAO_E'])
        self.assertEqual(set(), set(conf['IDS']) & set(nao['IDS']))

    @unittest.skipUnless(os.path.exists(PARES), 'leitor canônico não versionado')
    def test_a_divida_provada_vem_de_PERTENCA_POSITIVA(self):
        """`r not in sem_par` dava por lido pelo canônico um registo que ele nunca viu."""
        with open(PARES, encoding='utf-8') as f:
            v3 = json.load(f)
        com_par = {p['REGISTRATION_ID'] for p in v3['PAIRS']}
        lidos = sorted(r for r in self.d['REGISTRATION_IDS'] if r in com_par)
        self.assertEqual(sorted(self.d['CONFIRMED_PARSER_DEBT']['PROVA_POR_LEITOR_CANONICO']),
                         lidos)
        self.assertEqual(31, len(lidos),
                         'se o leitor canônico lê 31 dos 40, chamar os 40 de ausência é falso')
        # e um registo que o canonico NUNCA viu nao pode cair no balde provado
        universo = {p['REGISTRATION_ID'] for p in _art()['PRODUCTS']}
        self.assertFalse(com_par - universo, 'os dois artefatos descrevem universos diferentes')


@unittest.skipUnless(os.path.isdir(TESTO), 'textos de rótulo não versionados')
class TestNaoSeiSoDepoisDeOlhar(unittest.TestCase):
    """`NAO SEI` sobre um ficheiro que temos em disco é uma confissão de não ter olhado."""

    @classmethod
    def setUpClass(cls):
        cls.d = _art()['READ_STRUCTURING_DEBT']

    def test_nenhum_nao_sei_esconde_cultura_que_o_proprio_vocabulario_acha(self):
        import italia_portfolio as ip
        traidores = {}
        for r in self.d['UNCONFIRMED_SILENCE']['IDS']:
            achadas = ip._culturas_no_texto_arquivado(r)
            if achadas:
                traidores[r] = achadas
        self.assertEqual({}, traidores,
                         'rótulo classificado NAO SEI cujo texto arquivado tem cultura '
                         'do vocabulário da casa — isso é dívida do parser, provada')

    def test_cada_nao_sei_traz_a_sua_razao_medida(self):
        sabe = self.d['UNCONFIRMED_SILENCE']['O_QUE_SE_SABE_DE_CADA']
        self.assertEqual(sorted(self.d['UNCONFIRMED_SILENCE']['IDS']), sorted(sabe))
        for r, v in sabe.items():
            with self.subTest(registo=r):
                self.assertTrue(v.get('LEITURA'), 'NAO SEI sem razão escrita')
                self.assertTrue(v.get('E_COADIUVANTE')
                                or v.get('CITA_CULTURA_FORA_DO_VOCABULARIO'),
                                'NAO SEI sem nenhum facto medido a sustentá-lo')

    def test_a_divida_provada_por_texto_e_mesmo_provavel_no_texto(self):
        import italia_portfolio as ip
        for r in self.d['CONFIRMED_PARSER_DEBT']['PROVA_POR_TEXTO_ARQUIVADO']:
            with self.subTest(registo=r):
                self.assertTrue(ip._culturas_no_texto_arquivado(r),
                                'declarado provado pelo texto e o texto não tem cultura')


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
        # O manifesto vem do DONO dele, nao do artefato sob teste. Alimentar o gerador
        # com os numeros do proprio artefato fazia os dois primeiros degraus serem
        # verdadeiros por construcao.
        with open(MANIFESTO, encoding='utf-8') as f:
            manifesto = json.load(f)
        self.assertEqual(est, ip._cobertura_por_estagio(o['PRODUCTS'], manifesto),
                         'o gerador e o artefato discordam: a correção some na próxima rodada')
        self.assertEqual(manifesto['TARGET_TOTAL'],
                         est['LABEL_DISCOVERY_COVERAGE']['TARGET'])
        self.assertEqual(manifesto['LABELS_OBTAINED'],
                         est['LABEL_DOWNLOAD_COVERAGE']['OBTAINED'])

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
