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


class TestRegressaoJanelaAbertaNaoEhNecessidade(unittest.TestCase):
    """Erro que quase aconteceu: manter AGIR AGORA no olivo porque a janela
    de etiqueta esta aberta. Janela aberta prova PERMISSAO, nao NECESSIDADE.
    """

    def test_o_caso_do_olivo_separa_permissao_de_necessidade(self):
        c = carrega('ES-CASE-001-OLIVO-REPILO.json')
        k = c['CORRECAO_SEMANTICA_CRITICA']
        for campo in ('FIELD_SIGNAL_STATUS', 'APPLICATION_WINDOW_STATUS',
                      'MONITORING_NEED', 'PRODUCT_ACTION_NEED', 'BUSINESS_ACTION'):
            self.assertIn(campo, k, f'{campo} nao declarado')
        self.assertIn('NOT_KNOWN', k['PRODUCT_ACTION_NEED'])
        self.assertIn('OPEN', k['APPLICATION_WINDOW_STATUS'])

    def test_o_tipo_do_caso_nomeia_o_objeto_da_acao(self):
        pack = carrega('SPAIN-HERO-CASES-V1.json')
        olivo = [c for c in pack['CASES'] if c['CASE_ID'] == 'ES-CASE-001'][0]
        self.assertEqual('VERIFY_FIELD_NOW', olivo['CASE_TYPE'])
        self.assertIn('NOT_KNOWN', olivo['CURRENT_FIELD_NEED'])
        # "aplicar" so pode aparecer negado ou condicionado
        self.assertIn('Nao aplicar', olivo['ACTION_NOW'])

    def test_nenhum_caso_usa_agir_agora_sem_objeto(self):
        pack = carrega('SPAIN-HERO-CASES-V1.json')
        for c in pack['CASES']:
            t = c['CASE_TYPE'].upper()
            if 'AGIR AGORA' in t:
                self.fail(f"{c['CASE_ID']}: AGIR AGORA sem objeto direto")


class TestRegressaoAdjacenciaNaoEhCobertura(unittest.TestCase):
    """Quatro municipios aragoneses fazem fronteira com o Segria.
    Isso e adjacencia geografica, nao cobertura de rede tecnica."""

    def test_o_caso_do_milho_declara_o_nivel_da_medida(self):
        c = carrega('ES-CASE-002-MAIZ-AMARANTHUS.json')
        i = c['TECHNICAL_NETWORK']['INTERSECAO_GEOGRAFICA']
        self.assertIn('NIVEL_DA_MEDIDA', i)
        self.assertIn('COMARCA', i['NIVEL_DA_MEDIDA'])
        self.assertIn('NAO e voz', i['CLASSIFICACAO'])


class TestGeografiaDoEstudoNaoEhAfiliacao(unittest.TestCase):
    """Afiliacao (Lleida) != local do experimento (Lleida) != origem das
    populacoes (Barcelona e Huesca). As tres coincidiriam num resumo desatento."""

    def test_o_caso_do_cereal_separa_as_tres(self):
        c = carrega('ES-CASE-003-CEREAL-GRAMINEAS.json')
        t = c['O_BLOQUEIO_MATERIAL_RESOLVIDO']['TEXTO_COMPLETO_LIDO']
        for campo in ('SAMPLE_GEOGRAPHY_VERIFICADA_OFICIALMENTE',
                      'STUDY_GEOGRAPHY', 'AUTHOR_AFFILIATION'):
            self.assertIn(campo, t)
        g = t['SAMPLE_GEOGRAPHY_VERIFICADA_OFICIALMENTE']
        self.assertEqual(8, g['Calaf']['cprovi'])
        self.assertEqual(8, g['Calonge de Segarra']['cprovi'])
        self.assertEqual(22, g['Ballobar']['cprovi'])

    def test_huesca_nao_vira_territorio_de_resistencia(self):
        c = carrega('ES-CASE-003-CEREAL-GRAMINEAS.json')
        v = c['CONVERGENCIA_REGIONAL']['VEREDITO']
        self.assertIn('NAO ha convergencia de PROVINCIA', v)


class TestMunicipioNuncaPorAproximacao(unittest.TestCase):
    """Codigo catastral difere do codigo INE em 335 dos 339 municipios de Aragon."""

    def test_crosswalk_e_oficial_e_completo(self):
        d = carrega('ES-T2-003-crosswalk-municipio-aragon.json')
        self.assertEqual(81, d['CASAMENTO']['MUNICIPIOS_DE_HUESCA_COM_MILHO'])
        self.assertEqual(81, d['CASAMENTO']['CASADOS_OFICIALMENTE'])
        self.assertEqual(0, d['CASAMENTO']['SEM_CASAMENTO'])
        self.assertIn('Nenhum fuzzy-match', d['CASAMENTO']['METODO'])


class TestFreezeEspanhaV1(unittest.TestCase):
    """O freeze so vale se ele reprovar quando um artefato muda."""

    def test_o_freeze_declara_head_e_hashes(self):
        d = carrega('SPAIN-DEMO-CONTENT-V1.json')
        f = d['FREEZE']
        self.assertRegex(f['HEAD_QUE_SUSTENTA'], r'^[0-9a-f]{40}$')
        self.assertGreaterEqual(len(f['ARTEFATOS_CANONICOS']), 10)
        for nome, meta in f['ARTEFATOS_CANONICOS'].items():
            self.assertRegex(meta['sha256'], r'^[0-9a-f]{64}$', nome)
            self.assertGreater(meta['bytes'], 0, nome)

    def test_todo_artefato_canonico_existe_e_bate(self):
        import hashlib
        d = carrega('SPAIN-DEMO-CONTENT-V1.json')
        for nome, meta in d['FREEZE']['ARTEFATOS_CANONICOS'].items():
            p = os.path.join(SAMPLES, nome)
            self.assertTrue(os.path.exists(p), f'{nome} sumiu do freeze')
            with open(p, 'rb') as f:
                atual = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(meta['sha256'], atual,
                             f'{nome} mudou depois do freeze — atualize o freeze '
                             'de proposito ou reverta a mudanca')


class TestRegressaoLeituraFalhaNaoEhZero(unittest.TestCase):
    """READ_FAILURE != ZERO. Ja aconteceu duas vezes: pdftotext ausente
    devolveu 0 caracteres em 7 fichas, e clear() no iterparse apagou
    15 campanhas de septoriose."""

    def test_o_teste_decisivo_do_milho_declara_os_chars_lidos(self):
        c = carrega('ES-CASE-002-MAIZ-AMARANTHUS.json')
        for r in c['O_TESTE_DECISIVO']['RESULTADO']:
            self.assertGreater(r['CHARS_LIDOS'], 1000,
                               f"{r['PRODUTO']}: zero de Amaranthus so vale "
                               'com texto efetivamente lido')

    def test_o_zero_do_milho_tem_controle_positivo(self):
        c = carrega('ES-CASE-002-MAIZ-AMARANTHUS.json')
        self.assertIn('CONTROLE_QUE_TORNA_O_ZERO_LEGIVEL', c['O_TESTE_DECISIVO'])

    def test_a_serie_do_cereal_nao_pode_ser_vazia(self):
        d = carrega('ES-T3-002-raif-cereales-invierno.json')
        serie = d['SERIE_SEPTORIA']
        com_leitura = [k for k, v in serie.items() if v.get('n_sup')]
        self.assertGreaterEqual(len(com_leitura), 10,
                                'serie vazia = bug de leitura, nao ausencia de dado')


class TestRegistroNaoEhDisponibilidadeComercial(unittest.TestCase):
    """REGISTRATION != COMMERCIAL_AVAILABILITY."""

    def test_commercial_clock_e_nao_sei_nos_tres(self):
        pack = carrega('SPAIN-HERO-CASES-V1.json')
        for c in pack['CASES']:
            self.assertIn('NAO SEI', c['COMMERCIAL_CLOCK'], c['CASE_ID'])

    def test_commercial_nunca_recebe_instrucao_de_venda(self):
        v2 = carrega('ES-ACTION-MAP-V2.json')
        for k, v in v2.items():
            if not k.startswith('ES-CASE'):
                continue
            self.assertEqual('WAIT_FOR_INTERNAL_DATA',
                             v['COMMERCIAL']['ACTION_TYPE'], k)

    def test_a_demo_lista_o_que_nao_pode_afirmar(self):
        d = carrega('SPAIN-DEMO-CONTENT-V1.json')
        proibido = ' '.join(d['O_QUE_A_DEMO_NAO_PODE_AFIRMAR']).lower()
        for termo in ('disponibilidade comercial', 'eficacia', 'economico'):
            self.assertIn(termo, proibido)


class TestGenericoNaoEhEspecieExplicita(unittest.TestCase):
    """GENERIC_TARGET != EXPLICIT_SPECIES_TARGET."""

    def test_o_milho_classifica_a_resposta(self):
        c = carrega('ES-CASE-002-MAIZ-AMARANTHUS.json')
        r = c['REGULATORY_RESPONSE']
        self.assertIn('EXPLICIT_SPECIES_RESPONSE = NONE',
                      json.dumps(carrega('SPAIN-HERO-CASES-V1.json'), ensure_ascii=False))
        self.assertIn('O_QUE_ISSO_NAO_E', c['O_TESTE_DECISIVO'])
        nao_e = c['O_TESTE_DECISIVO']['O_QUE_ISSO_NAO_E']
        self.assertIn('eficacia', nao_e.lower())

    def test_o_cereal_separa_explicito_de_generico(self):
        c = carrega('ES-CASE-003-CEREAL-GRAMINEAS.json')
        pack = carrega('SPAIN-HERO-CASES-V1.json')
        cereal = [x for x in pack['CASES'] if x['CASE_ID'] == 'ES-CASE-003'][0]
        self.assertIn('LOLIUM_EXPLICIT_RESPONSE', cereal['ADAMA_REGULATORY_RESPONSE'])
        self.assertIn('GENERIC_GRASS_RESPONSE', cereal['ADAMA_REGULATORY_RESPONSE'])


if __name__ == '__main__':
    unittest.main()