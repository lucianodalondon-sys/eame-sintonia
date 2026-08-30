"""Regressao dos tres erros de confianca ja cometidos.

Cada teste aqui existe porque o erro JA aconteceu uma vez e foi publicado.
Nao sao testes de estilo: sao cercas em volta de buracos conhecidos.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')


def carrega(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


class TestPackV1(unittest.TestCase):
    def setUp(self):
        self.pack = carrega('SPAIN-HERO-CASES-V1.json')
        self.cases = self.pack['CASES']

    def test_tres_casos(self):
        self.assertEqual(3, len(self.cases))

    def test_contrato_identico(self):
        chaves = [set(c) for c in self.cases]
        for k in chaves[1:]:
            self.assertEqual(chaves[0], k, 'os cartoes V1 nao tem os mesmos campos')

    def test_nenhum_campo_vazio(self):
        """Campo ausente vira razao declarada, nunca vazio nem zero."""
        vazios = []
        for c in self.cases:
            for k, v in c.items():
                if v in ('', [], {}, None, 0):
                    vazios.append((c['CASE_ID'], k))
        self.assertEqual([], vazios, f'campo vazio em vez de razao: {vazios}')

    def test_commercial_clock_nunca_inventado(self):
        for c in self.cases:
            self.assertIn('NAO SEI', c['COMMERCIAL_CLOCK'])

    def test_nenhum_roi(self):
        for c in self.cases:
            self.assertIn('NAO QUANTIFICADO', c['POSSIBLE_ECONOMIC_CONSEQUENCE'])


class TestRegressaoFileDateNaoEhSignalDate(unittest.TestCase):
    """Erro cometido: chamei de 'sinal de 6 dias' a data de GERACAO do arquivo.

    A observacao de repilo no oeste andaluz termina em junho e maio.
    """

    def test_caso_olivo_separa_os_relogios(self):
        c = carrega('ES-CASE-001-OLIVO-REPILO.json')
        r = c['RELOGIOS_FORMALIZADOS']
        for campo in ('OBSERVED_AT', 'SAMPLE_PERIOD', 'FILE_DATE',
                      'PUBLICATION_DATE', 'CAPTURED_AT'):
            self.assertIn(campo, r, f'{campo} nao declarado')
        self.assertNotEqual(r['FILE_DATE'], r['PUBLICATION_DATE'])
        self.assertIn('2026-06-14', r['OBSERVED_AT']['HUELVA'])

    def test_frescor_do_olivo_nao_se_chama_current(self):
        c = carrega('ES-CASE-001-OLIVO-REPILO.json')
        classe = c['RELOGIOS_FORMALIZADOS']['SIGNAL_FRESHNESS_CLASS']
        # a classe pode CITAR CURRENT_SIGNAL para dizer que nao e uma.
        # o que nao pode e SER uma.
        rotulo = classe.split('—')[0].strip()
        self.assertNotEqual('CURRENT_SIGNAL', rotulo)
        self.assertTrue(rotulo.startswith('SEASON_'), rotulo)

    def test_pack_v1_declara_observation_date_separado(self):
        pack = carrega('SPAIN-HERO-CASES-V1.json')
        for c in pack['CASES']:
            self.assertIn('EVIDENCE_DATE', c)
            self.assertIn('OBSERVATION_DATE', c)
            self.assertIn('FRESHNESS', c)


class TestRegressaoVarianteNaoEhContagemNacional(unittest.TestCase):
    """Erro cometido: publiquei '1 registro em toda a Espanha' para
    Amaranthus x milho. Era o MESMO registro contado em duas variantes
    de cultura, e a variante generica MAIZ tem zero.
    """

    def test_caso_milho_conta_variante_a_variante(self):
        c = carrega('ES-CASE-002-MAIZ-AMARANTHUS.json')
        r = c['REGULATORY_RESPONSE']
        for v in ('MAIZ_2024_x_AMARANTHUS', 'MAIZ_DE_GRANO_2027_x_AMARANTHUS',
                  'MAIZ_DULCE_2025_x_AMARANTHUS', 'MAIZ_FORRAJERO_2026_x_AMARANTHUS'):
            self.assertIn(v, r, f'variante {v} nao contada separadamente')
        self.assertEqual(0, r['MAIZ_2024_x_AMARANTHUS']['total'])
        self.assertIn('CORRECAO_DO_QUE_EU_TINHA_ESCRITO', r)

    def test_um_produto_nao_vira_dois_registros(self):
        c = carrega('ES-CASE-002-MAIZ-AMARANTHUS.json')
        quem = c['REGULATORY_RESPONSE']['QUEM_TEM']
        self.assertEqual('ES-01724', quem['REG'])
        soma = sum(c['REGULATORY_RESPONSE'][v]['total'] for v in
                   ('MAIZ_2024_x_AMARANTHUS', 'MAIZ_DE_GRANO_2027_x_AMARANTHUS',
                    'MAIZ_DULCE_2025_x_AMARANTHUS', 'MAIZ_FORRAJERO_2026_x_AMARANTHUS'))
        self.assertEqual(2, soma, 'as linhas somam 2 e o produto unico e 1 — '
                                  'a diferenca precisa continuar explicada no cartao')


class TestRegressaoSerieDeRepiloTem21Campanhas(unittest.TestCase):
    """Erro cometido: '23 safras'. A reproducao ve 21 campanhas com leitura
    de repilo em Huelva, e o dataset oficial comeca em 2006.
    """

    def test_serie_de_huelva_tem_21_campanhas(self):
        c = carrega('ES-CASE-001-OLIVO-REPILO.json')
        serie = c['SIGNAL']['SERIE_HUELVA']
        self.assertEqual(21, len(serie))
        self.assertEqual('2006', min(serie))
        self.assertEqual('2026', max(serie))

    def test_23_safras_so_pode_aparecer_como_discrepancia_declarada(self):
        """O numero errado pode ser CITADO para ser corrigido.
        O que nao pode e voltar a ser afirmado em campo comum."""
        def caminhos(o, pai=''):
            if isinstance(o, dict):
                for k, v in o.items():
                    yield from caminhos(v, f'{pai}.{k}')
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    yield from caminhos(v, f'{pai}[{i}]')
            elif isinstance(o, str):
                yield pai, o

        PERMITIDO = ('DISCREPANCIA', 'CORRECAO', 'ERRO', 'CONTRAPROVA')
        for nome in ('ES-CASE-001-OLIVO-REPILO.json', 'SPAIN-HERO-CASES-V1.json'):
            for caminho, texto in caminhos(carrega(nome)):
                if re.search(r'23\s*(?:safras|campanhas)', texto, re.I):
                    self.assertTrue(
                        any(p in caminho.upper() for p in PERMITIDO),
                        f'{nome}: "23 safras" afirmado em {caminho}, '
                        'fora de um campo de discrepancia ou correcao')


class TestRegressaoSiglaCurtaPrecisaDeLimiteDePalavra(unittest.TestCase):
    """Erro cometido: contei '34 de 96 fichas com HRAC/IRAC/FRAC'.
    'respiracion' e 'aspiracion' contem IRAC. O correto e 1 de 96.
    """

    def test_o_caso_do_cereal_registra_a_correcao(self):
        c = carrega('ES-CASE-003-CEREAL-GRAMINEAS.json')
        erro = c['ARQUITETURA_DE_MODO_DE_ACAO']['ERRO_QUE_ESSA_CONTAGEM_QUASE_PUBLICOU']
        self.assertIn('34', erro['PRIMEIRA_MEDIDA'])
        self.assertIn('1 de 96', erro['CORRIGIDO_PARA'])

    def test_a_sigla_com_limite_nao_casa_palavra_comum(self):
        rx = re.compile(r'\b(HRAC|IRAC|FRAC)\b')
        for palavra in ('respiración', 'aspiración', 'fracción', 'fraccionada', 'fracaso'):
            self.assertIsNone(rx.search(palavra), f'{palavra} ainda casa')
        self.assertIsNotNone(rx.search('grupo HRAC 1'))


class TestMunicipioNuncaPorAproximacao(unittest.TestCase):
    """Codigo catastral difere do codigo INE em 335 dos 339 municipios de Aragon."""

    def test_crosswalk_e_oficial_e_completo(self):
        d = carrega('ES-T2-003-crosswalk-municipio-aragon.json')
        self.assertEqual(81, d['CASAMENTO']['MUNICIPIOS_DE_HUESCA_COM_MILHO'])
        self.assertEqual(81, d['CASAMENTO']['CASADOS_OFICIALMENTE'])
        self.assertEqual(0, d['CASAMENTO']['SEM_CASAMENTO'])
        self.assertIn('Nenhum fuzzy-match', d['CASAMENTO']['METODO'])


if __name__ == '__main__':
    unittest.main()
