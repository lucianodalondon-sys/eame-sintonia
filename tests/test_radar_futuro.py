"""Regressoes do Radar do Futuro.

Cada teste impede uma confusao que ja custou caro neste projeto ou que
o contrato nomeia como proibida.
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
PAISES = ('SPAIN-RADAR-DO-FUTURO-V1.json', 'ITALY-RADAR-DO-FUTURO-V1.json')
SINAIS = ('SCIENCE_SIGNAL', 'RESEARCHER_SIGNAL', 'TECHNICAL_SIGNAL', 'FIELD_SIGNAL',
          'REGULATORY_SIGNAL', 'PORTFOLIO_SIGNAL', 'PUBLIC_VOICE_SIGNAL')
ESTADOS = ['OBSERVED_TOPIC', 'SCIENTIFIC_SIGNAL', 'EMERGING_THEME',
           'WATCHLIST_PRIORITY', 'ALMOST_RADAR_CASE', 'PROMOTED_TO_RADAR']


def carrega(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


def temas():
    for n in PAISES:
        for t in carrega(n)['THEMES']:
            yield n, t


class TestContrato(unittest.TestCase):
    def test_regua_tem_seis_estados_em_ordem(self):
        c = carrega('RADAR-DO-FUTURO-CONTRACT-V1.json')
        nomes = [s['NOME'] for s in c['REGUA_DE_MATURIDADE']]
        self.assertEqual(ESTADOS, nomes)
        for i, s in enumerate(c['REGUA_DE_MATURIDADE']):
            self.assertEqual(i, s['STATE'])

    def test_toda_promocao_tem_criterio(self):
        c = carrega('RADAR-DO-FUTURO-CONTRACT-V1.json')
        r = c['REGRAS_DE_PROMOCAO']
        for k in ('0_para_1', '1_para_2', '2_para_3', '3_para_4', '4_para_5'):
            self.assertIn(k, r)
            self.assertGreater(len(r[k]), 20, k)

    def test_palavras_de_previsao_sao_proibidas(self):
        c = carrega('RADAR-DO-FUTURO-CONTRACT-V1.json')
        for p in ('PREDICTION', 'FORECAST', 'SCORE'):
            self.assertIn(p, c['PALAVRAS_PROIBIDAS'])


class TestManyPapersNaoEhEmerging(unittest.TestCase):
    """MANY_PAPERS != EMERGING. Volume nao compra estado."""

    def test_um_tema_com_uma_camada_nao_passa_do_estado_1(self):
        for arq, t in temas():
            if t['INDEPENDENT_LAYERS'] <= 1:
                self.assertIn(t['MATURITY_STATE'], ('OBSERVED_TOPIC', 'SCIENTIFIC_SIGNAL'),
                              f"{arq}:{t['THEME_ID']} tem 1 camada e estado {t['MATURITY_STATE']}")

    def test_emerging_exige_duas_camadas_independentes(self):
        for arq, t in temas():
            if t['MATURITY_STATE'] in ('EMERGING_THEME', 'WATCHLIST_PRIORITY', 'ALMOST_RADAR_CASE'):
                self.assertGreaterEqual(t['INDEPENDENT_LAYERS'], 2, f"{arq}:{t['THEME_ID']}")

    def test_o_maior_volume_cientifico_nao_e_o_estado_mais_alto(self):
        """O par de trigo x Fusarium italiano tem MAIS ciencia que o do milho
        e MENOS camadas — e por isso fica num estado mais baixo."""
        it = {t['THEME_ID']: t for t in carrega('ITALY-RADAR-DO-FUTURO-V1.json')['THEMES']}
        self.assertEqual('SCIENTIFIC_SIGNAL', it['FT-IT-002']['MATURITY_STATE'])
        self.assertEqual('EMERGING_THEME', it['FT-IT-001']['MATURITY_STATE'])
        self.assertLess(it['FT-IT-002']['INDEPENDENT_LAYERS'],
                        it['FT-IT-001']['INDEPENDENT_LAYERS'])


class TestPrimeiraCapturaNaoEhCrescimento(unittest.TestCase):
    """FIRST_CAPTURE != GROWING."""

    def test_nenhum_tema_declara_crescimento_sem_serie(self):
        for arq, t in temas():
            self.assertIn(t['MOMENTUM_STATE'], ('NOT_KNOWN', 'BASELINE_ESTABLISHED'),
                          f"{arq}:{t['THEME_ID']} declara {t['MOMENTUM_STATE']} sem serie temporal")

    def test_o_contrato_proibe_total_acumulado_como_tendencia(self):
        c = carrega('RADAR-DO-FUTURO-CONTRACT-V1.json')['REGRAS_DE_MOMENTUM']
        self.assertIn('NOT_KNOWN', c['SEM_SERIE'])
        self.assertIn('BASELINE_ESTABLISHED', c['REGRA_ZERO'])


class TestCienciaNaoEhCampo(unittest.TestCase):
    """SCIENTIFIC_SIGNAL != FIELD_SIGNAL."""

    def test_sinais_sao_campos_distintos_e_sempre_presentes(self):
        for arq, t in temas():
            for s in SINAIS:
                self.assertIn(s, t, f"{arq}:{t['THEME_ID']} sem {s}")
                self.assertIn(t[s]['ESTADO'], ('PRESENTE', 'AUSENTE_MEDIDO', 'NAO_TESTADO'))
                self.assertGreater(len(t[s]['EVIDENCIA']), 10, f"{arq}:{t['THEME_ID']}:{s}")

    def test_ausente_medido_e_nao_testado_nao_se_confundem(self):
        """A distincao entre 'procurei e nao ha' e 'nao procurei' precisa existir
        de fato nos dados, nao so no contrato."""
        estados = set()
        for _, t in temas():
            for s in SINAIS:
                estados.add(t[s]['ESTADO'])
        self.assertIn('AUSENTE_MEDIDO', estados)
        self.assertIn('NAO_TESTADO', estados)


class TestWatchlistNaoEhCaso(unittest.TestCase):
    """WATCHLIST != CASE. A unica porta e a confirmacao de campo."""

    def test_nenhum_tema_foi_promovido_sem_campo(self):
        for arq, t in temas():
            if t['MATURITY_STATE'] == 'PROMOTED_TO_RADAR':
                self.assertTrue(t['CURRENT_FIELD_CONFIRMATION'].upper().startswith('SIM'),
                                f"{arq}:{t['THEME_ID']} promovido sem campo")

    def test_todo_tema_diz_o_que_o_promoveria(self):
        for arq, t in temas():
            self.assertGreater(len(t['WHAT_WOULD_PROMOTE_TO_RADAR']), 20, f"{arq}:{t['THEME_ID']}")

    def test_nenhum_tema_promovido_nesta_versao(self):
        for n in PAISES:
            self.assertEqual(0, carrega(n)['PROMOTED_TO_RADAR'])


class TestNextCycleNaoEhAcaoCorrente(unittest.TestCase):
    def test_tema_com_janela_fechada_nao_propoe_acao_corrente(self):
        es = {t['THEME_ID']: t for t in carrega('SPAIN-RADAR-DO-FUTURO-V1.json')['THEMES']}
        palmeri = es['FT-ES-002']
        self.assertIn('2027', palmeri['HORIZON'])
        for a in palmeri['POTENTIAL_ADAMA_AREAS']:
            self.assertNotIn('AGIR AGORA', a.upper())


class TestAfiliacaoNaoEhGeografiaDoFato(unittest.TestCase):
    """RESEARCHER_AFFILIATION != FACT_GEOGRAPHY."""

    def test_o_outlook_declara_a_regra(self):
        o = carrega('RESEARCHER-OUTLOOK-V1.json')
        self.assertIn('AUTHOR_AFFILIATION', o['REGRA_DE_GEOGRAFIA'])
        self.assertIn('STUDY_GEOGRAPHY', o['REGRA_DE_GEOGRAFIA'])

    def test_o_outlook_nao_tem_ranking_nem_seguidores(self):
        """Um termo proibido PODE ser citado para ser proibido.
        O que nao pode e aparecer num campo de dado."""
        def caminhos(o, pai=''):
            if isinstance(o, dict):
                for k, v in o.items():
                    yield from caminhos(v, f'{pai}.{k}')
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    yield from caminhos(v, f'{pai}[{i}]')
            elif isinstance(o, str):
                yield pai, o

        PERMITIDO = ('NAO_E', 'PROIBI', 'REGRA')
        for caminho, texto in caminhos(carrega('RESEARCHER-OUTLOOK-V1.json')):
            for proibido in ('seguidor', 'follower', 'authority_score'):
                if proibido in texto.lower():
                    self.assertTrue(any(p in caminho.upper() for p in PERMITIDO),
                                    f'"{proibido}" em campo de dado: {caminho}')

    def test_nenhuma_pessoa_carrega_metrica_de_alcance(self):
        o = carrega('RESEARCHER-OUTLOOK-V1.json')
        for grupo in ('ES', 'IT'):
            for p in o[grupo]:
                for k in p:
                    self.assertNotIn(k.upper(), ('FOLLOWERS', 'SCORE', 'RANK', 'AUTHORITY'))

    def test_toda_pessoa_declara_o_que_nao_esta_provado(self):
        o = carrega('RESEARCHER-OUTLOOK-V1.json')
        for grupo in ('ES', 'IT'):
            for p in o[grupo]:
                self.assertGreater(len(p['WHAT_IS_NOT_PROVED']), 20, p['WHO'])


class TestSemProdutoExplicitoNaoEhSemProduto(unittest.TestCase):
    """NO_EXPLICIT_PRODUCT != NO_PRODUCT."""

    def test_a_regra_de_display_proibe_a_frase(self):
        d = carrega('DISPLAY-LAYER-V1.json')
        proibidas = ' '.join(d['PROIBICOES_DE_TRADUCAO']).lower()
        self.assertIn('nao tem solucao', proibidas)

    def test_a_regra_de_explicit_none_nomeia_o_registro(self):
        d = carrega('DISPLAY-LAYER-V1.json')
        r = [x for x in d['REGRAS'] if x['SOURCE_FIELD'] == 'EXPLICIT_SPECIES_RESPONSE'][0]
        for lingua in ('DISPLAY_TEXT_PT', 'DISPLAY_TEXT_EN', 'DISPLAY_TEXT_ES'):
            self.assertRegex(r[lingua].lower(), r'registr', lingua)


class TestDisplayLayer(unittest.TestCase):
    def test_toda_regra_tem_as_tres_linguas_e_a_semantica(self):
        d = carrega('DISPLAY-LAYER-V1.json')
        for r in d['REGRAS']:
            for k in ('DISPLAY_TEXT_PT', 'DISPLAY_TEXT_EN', 'DISPLAY_TEXT_ES', 'SEMANTIC_RULE'):
                self.assertTrue(r.get(k), f"{r['DISPLAY_KEY']} sem {k}")

    def test_nenhum_texto_de_exibicao_contem_frase_proibida(self):
        d = carrega('DISPLAY-LAYER-V1.json')
        proibidas = ('nao tem solucao', 'sem necessidade', 'aplique agora', 'sem produto')
        for r in d['REGRAS']:
            for k in ('DISPLAY_TEXT_PT', 'DISPLAY_TEXT_EN', 'DISPLAY_TEXT_ES'):
                for p in proibidas:
                    self.assertNotIn(p, r[k].lower(), f"{r['DISPLAY_KEY']}:{k}")

    def test_todo_estado_de_maturidade_tem_texto(self):
        d = carrega('DISPLAY-LAYER-V1.json')
        cobertos = {r['SOURCE_VALUE'] for r in d['REGRAS'] if r['SOURCE_FIELD'] == 'MATURITY_STATE'}
        self.assertEqual(set(ESTADOS), cobertos)


class TestDesignDataContract(unittest.TestCase):
    def test_o_radar_do_futuro_vem_antes_do_radar(self):
        d = carrega('DESIGN-DATA-CONTRACT-V1.json')
        f = {x['ID']: x['ORDEM'] for x in d['NAVIGATION_MODEL']['NIVEL_2_FERRAMENTAS']}
        self.assertLess(f['RADAR_DO_FUTURO'], f['RADAR'])

    def test_nao_ha_cor_hex_na_inteligencia(self):
        import re
        d = carrega('DESIGN-DATA-CONTRACT-V1.json')
        self.assertEqual([], re.findall(r'#[0-9A-Fa-f]{6}', json.dumps(d, ensure_ascii=False)))

    def test_os_cinco_estados_de_ignorancia_sao_distintos(self):
        d = carrega('DESIGN-DATA-CONTRACT-V1.json')['NOT_KNOWN_STATES']
        self.assertIn('CINCO', d['REGRA'])
        self.assertIn('AUSENTE_MEDIDO', d['O_PIOR_ERRO_POSSIVEL'])


if __name__ == '__main__':
    unittest.main()
