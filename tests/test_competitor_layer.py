"""A camada COMPETITOR e estrutural, e continua sem dado inventado.

Estes testes guardam duas coisas ao mesmo tempo, e elas puxam para lados
opostos: que a arquitetura RECONHECE a concorrencia como camada da
convergencia, e que nenhuma linha de dado competitivo foi fabricada para
fazer a capacidade parecer pronta.

Nenhum teste aqui exige coleta. Se um dia a coleta acontecer, o que muda e
DATA_COVERAGE — nao o contrato.
"""
import json
import os
import re
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AMOSTRAS = os.path.join(RAIZ, 'data', 'samples')
CONTRATO = os.path.join(AMOSTRAS, 'EAME-COMPETITOR-CONTRACT-V1.json')
LINGUAS = ('DISPLAY_TEXT_PT', 'DISPLAY_TEXT_EN', 'DISPLAY_TEXT_ES')

ESTADOS = ['COMPETITOR_REGISTERED_RESPONSE', 'COMPETITOR_PAID_META_ACTIVITY',
           'COMPETITOR_PUBLIC_COMMUNICATION', 'COMPETITOR_TECHNICAL_ACTIVITY',
           'NOT_KNOWN']


def carrega(nome=CONTRATO):
    with open(nome, encoding='utf-8') as f:
        return json.load(f)


def doc(*partes):
    with open(os.path.join(RAIZ, 'docs', *partes), encoding='utf-8') as f:
        return f.read()


class TestOContratoExiste(unittest.TestCase):

    def setUp(self):
        self.d = carrega()

    def test_as_sete_camadas_da_convergencia(self):
        c = self.d['AS_SETE_CAMADAS_DA_CONVERGENCIA']
        self.assertEqual(7, len(c))
        for esperada in ('CAMPO', 'CIENCIA', 'CLIMA', 'REGULATORIO',
                         'PORTFOLIO ADAMA LOCAL', 'CONCORRENCIA', 'TEMPO'):
            self.assertIn(esperada, c)

    def test_as_duas_perguntas_sao_duas(self):
        p = self.d['AS_DUAS_PERGUNTAS_QUE_A_CAMADA_RESPONDE']
        self.assertIn('1_QUEM_TEM_RESPOSTA', p)
        self.assertIn('2_QUEM_ESTA_SE_MOVIMENTANDO_AGORA', p)
        self.assertTrue(p['POR_QUE_SAO_DUAS'])

    def test_os_cinco_estados_existem_e_nao_se_fundem(self):
        nomes = [e['ESTADO'] for e in self.d['ESTADOS']]
        self.assertEqual(ESTADOS, nomes)
        self.assertTrue(self.d['OS_QUATRO_ESTADOS_NUNCA_SE_FUNDEM'])

    def test_todo_estado_diz_o_que_nao_prova(self):
        for e in self.d['ESTADOS']:
            self.assertTrue(e['NAO_PROVA'], e['ESTADO'])
            self.assertIn('CAPABILITY', e)

    def test_so_o_registro_e_demonstrable(self):
        """Capacidade declarada tem de bater com o que foi medido no repo."""
        cap = {e['ESTADO']: e['CAPABILITY'] for e in self.d['ESTADOS']}
        self.assertEqual('DEMONSTRABLE', cap['COMPETITOR_REGISTERED_RESPONSE'])
        for e in ('COMPETITOR_PAID_META_ACTIVITY', 'COMPETITOR_PUBLIC_COMMUNICATION',
                  'COMPETITOR_TECHNICAL_ACTIVITY'):
            self.assertEqual('PLANNED', cap[e], e)


class TestNadaFoiInventado(unittest.TestCase):
    """O risco desta rodada nao e errar um numero. E parecer ter dado."""

    def setUp(self):
        self.d = carrega()

    def test_data_coverage_continua_incompleta(self):
        self.assertEqual('NOT_YET_COMPLETE',
                         self.d['ESTADO_DA_CAPACIDADE']['DATA_COVERAGE'])

    def test_os_tres_exemplos_sao_conceituais(self):
        ex = self.d['EXEMPLOS_CONCEITUAIS']
        self.assertEqual(3, len(ex))
        for e in ex:
            self.assertEqual('NOT_YET_COLLECTED', e['DATA'], e['NOME'])
            self.assertTrue(e['O_QUE_FALTA'], e['NOME'])

    def test_nenhum_concorrente_nomeado_com_dado_atribuido(self):
        """Citar o exemplo medido do X-005 e legitimo. Inventar nao e.

        A varredura ignora os campos cujo NOME os marca como regra, motivo ou
        exemplo de erro. Sem isso o teste acusa a frase que ENSINA a lei — foi
        assim que ele nasceu, disparando em "'a Syngenta nao anuncia' e uma
        afirmacao; 'nunca abri a Ads Library' e outra", dentro de
        O_ERRO_MAIS_CARO_AQUI. Quinta vez que este projeto pisa nisso.
        """
        regra = re.compile(r'(PORQUE|NAO_|NUNCA|LEIS|ERRO|O_QUE_|COMO_|RESSALVA|'
                           r'DENOMINADOR|A_REGRA|LIMITE|PROIBID)')

        def anda(o, caminho=''):
            achados = []
            if isinstance(o, dict):
                for k, v in o.items():
                    if regra.search(str(k).upper()):
                        continue
                    achados += anda(v, caminho + '.' + str(k))
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    achados += anda(v, caminho + '[%d]' % i)
            elif isinstance(o, str):
                for empresa in ('Syngenta', 'BASF', 'Bayer', 'Corteva', 'UPL', 'Nufarm'):
                    if empresa in o:
                        achados.append((caminho, empresa, o[:120]))
            return achados

        for caminho, empresa, trecho in anda(self.d):
            with self.subTest(campo=caminho, empresa=empresa):
                self.assertTrue(
                    'X-005' in trecho or 'usos autorizados' in trecho
                    or '403' in trecho or 'sitemap' in trecho,
                    '%s citada num campo de dado sem ser exemplo medido: %s'
                    % (empresa, trecho))

    def test_meta_ads_library_continua_nao_testada(self):
        m = self.d['META_ADS_LIBRARY']
        self.assertEqual('NAO_TESTADO', m['ESTADO_NESTA_RODADA'])
        self.assertIn('GRAPH API', m['PORQUE_NAO_TESTADO'].upper())

    def test_o_proximo_passo_nao_foi_executado(self):
        p = self.d['PROXIMO_PASSO_FUTURO_NAO_EXECUTADO']
        self.assertTrue(p['NAO_EXECUTADO_NESTA_RODADA'])
        for proibido in ('coleta em massa', 'cron', 'painel', 'score'):
            self.assertIn(proibido, ' '.join(p['O_QUE_ELE_NAO_FARIA']))

    def test_o_que_a_rodada_nao_fez_esta_escrito(self):
        n = ' '.join(self.d['O_QUE_ESTA_RODADA_NAO_FEZ']).lower()
        for termo in ('nao coletou', 'nao criou cron', 'nao criou score',
                      'nao construiu portal', 'nao inventou'):
            self.assertIn(termo, n)


class TestAsLeisDaCamada(unittest.TestCase):

    def setUp(self):
        self.d = carrega()

    def test_as_leis_de_registro_estao_todas(self):
        leis = self.d['LEIS']
        for lei in ('REGISTRATION != SALES', 'REGISTRATION != STOCK',
                    'REGISTRATION != COMMERCIAL AVAILABILITY',
                    'PORTFOLIO GLOBAL != PORTFOLIO LOCAL'):
            self.assertIn(lei, leis)

    def test_as_leis_da_meta_estao_todas(self):
        proibido = self.d['META_ADS_LIBRARY']['O_QUE_ELA_NAO_PROVA']
        for lei in ('META AD != SALES', 'META AD != MARKET SHARE',
                    'META AD != CAMPAIGN SUCCESS', 'META AD != STOCK',
                    'META AD != PRODUCT AVAILABILITY'):
            self.assertIn(lei, proibido)

    def test_meta_prova_ativacao_e_so_isso(self):
        self.assertIn('ATIVACAO PUBLICITARIA OBSERVADA',
                      self.d['META_ADS_LIBRARY']['O_QUE_ELA_PROVA'])

    def test_a_contagem_de_pecas_exige_denominador(self):
        self.assertTrue(self.d['META_ADS_LIBRARY']['DENOMINADOR_OBRIGATORIO'])

    def test_as_cinco_ignorancias_continuam_distintas(self):
        c = self.d['CINCO_IGNORANCIAS_APLICADAS_A_ESTA_CAMADA']
        chaves = ('NAO_SEI', 'NOT_COLLECTED', 'NOT_KNOWN', 'AUSENTE_MEDIDO', 'NAO_TESTADO')
        for k in chaves:
            self.assertIn(k, c)
        self.assertEqual(5, len({c[k] for k in chaves}))

    def test_o_erro_mais_caro_da_camada_esta_nomeado(self):
        c = self.d['CINCO_IGNORANCIAS_APLICADAS_A_ESTA_CAMADA']
        self.assertIn('NAO_TESTADO', c['O_ERRO_MAIS_CARO_AQUI'])
        self.assertIn('AUSENTE_MEDIDO', c['O_ERRO_MAIS_CARO_AQUI'])


class TestSemScoreESemOportunidade(unittest.TestCase):

    def setUp(self):
        self.d = carrega()

    def test_as_palavras_proibidas_estao_declaradas(self):
        p = self.d['PALAVRAS_PROIBIDAS']
        for w in ('WHITE SPACE', 'COMPETITIVE ADVANTAGE', 'SALES OPPORTUNITY',
                  'MARKET SHARE'):
            self.assertIn(w, p)
        self.assertTrue(self.d['POR_QUE_SEM_SCORE'])

    def test_nenhuma_palavra_proibida_aparece_como_saida(self):
        """A proibicao mora em campo de regra. Se vazar para uma SAIDA, e defeito.

        A busca ignora os campos cujo NOME os marca como regra ou proibicao —
        senao o teste acusa a propria lista de PALAVRAS_PROIBIDAS, que e o erro
        que este projeto ja cometeu quatro vezes.
        """
        regra = re.compile(r'(PROIBID|NAO_|NUNCA|LEIS|POR_QUE|COMO_NAO|O_QUE_ELA_NAO|'
                           r'NAO_PROVA|NAO_E|RESSALVA|ERRO)')

        def anda(o, caminho=''):
            achados = []
            if isinstance(o, dict):
                for k, v in o.items():
                    if regra.search(str(k).upper()):
                        continue
                    achados += anda(v, caminho + '.' + str(k))
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    achados += anda(v, caminho + '[%d]' % i)
            elif isinstance(o, str):
                for w in self.d['PALAVRAS_PROIBIDAS']:
                    if w in o.upper():
                        achados.append((caminho, w))
            return achados
        self.assertEqual([], anda(self.d))

    def test_a_convergencia_nunca_conclui_oportunidade(self):
        self.assertIn('oportunidade comercial',
                      self.d['CONVERGENCIA']['O_QUE_A_CONVERGENCIA_NUNCA_CONCLUI'])
        for e in self.d['EXEMPLOS_CONCEITUAIS']:
            saida = json.dumps(e, ensure_ascii=False).upper()
            self.assertNotIn('SALES OPPORTUNITY', saida.replace('"SALES OPPORTUNITY"', '')
                             if 'COMO_NAO_SE_DIZ' in e else saida)


class TestOQuintoRelogio(unittest.TestCase):

    def setUp(self):
        self.d = carrega()['RELOGIO_COMPETITIVO']

    def test_ele_e_o_quinto_e_nao_se_funde(self):
        self.assertIn('QUINTO', self.d['E_O_QUINTO_RELOGIO'].upper())
        for r in ('CROP_STAGE', 'ISSUE_RELEVANCE_WINDOW', 'REGISTERED_PRODUCT_WINDOW',
                  'EVIDENCE_FRESHNESS'):
            self.assertIn(r, self.d['E_O_QUINTO_RELOGIO'])

    def test_os_campos_minimos_estao_todos(self):
        for c in ('FIRST_OBSERVED', 'LAST_OBSERVED', 'CHANGE_OBSERVED',
                  'SOURCE_DATE', 'AS_OF_DATE'):
            self.assertIn(c, self.d['CAMPOS_MINIMOS'])

    def test_o_frescor_continua_derivado(self):
        self.assertIn('AS_OF_DATE', self.d['FRESCOR_NAO_SE_PERSISTE'])
        self.assertIn('muda sozinho', self.d['FRESCOR_NAO_SE_PERSISTE'])

    def test_observation_start_nao_e_activity_start(self):
        self.assertIn('OBSERVATION_START != ACTIVITY_START', self.d['O_LIMITE_DURO'])


class TestCamposMinimos(unittest.TestCase):

    def setUp(self):
        self.d = carrega()

    def campos(self, bloco):
        return {c['CAMPO']: c for c in self.d[bloco]['CAMPOS_MINIMOS']}

    def test_a_resposta_registrada_exige_pais_e_numero(self):
        c = self.campos('COMPETITOR_RESPONSE')
        for k in ('COUNTRY', 'REGISTRATION_ID', 'ACTIVE_INGREDIENT',
                  'AUTHORIZED_CROP', 'REGULATORY_STATUS', 'OFFICIAL_SOURCE',
                  'SOURCE_DATE', 'EVIDENCE'):
            self.assertIn(k, c)
            self.assertTrue(c[k]['OBRIGATORIO'], k)

    def test_o_alvo_pode_faltar_sem_o_produto_sumir(self):
        c = self.campos('COMPETITOR_RESPONSE')
        self.assertFalse(c['AUTHORIZED_TARGET']['OBRIGATORIO'])
        self.assertIn('nao some', c['AUTHORIZED_TARGET']['PORQUE'])

    def test_a_ativacao_exige_datas_e_texto_original(self):
        c = self.campos('COMPETITOR_ACTIVATION')
        for k in ('FIRST_OBSERVED', 'LAST_OBSERVED', 'CLAIM_TEXT_ORIGINAL',
                  'PIECES_OBSERVED', 'ACTIVATION_STATE'):
            self.assertTrue(c[k]['OBRIGATORIO'], k)

    def test_a_contagem_de_pecas_carrega_denominador(self):
        c = self.campos('COMPETITOR_ACTIVATION')
        self.assertIn('denominador', c['PIECES_OBSERVED']['PORQUE'])

    def test_o_grupo_economico_continua_nao_medido(self):
        c = self.campos('COMPETITOR_RESPONSE')
        self.assertFalse(c['COMPETITOR_GROUP']['OBRIGATORIO'])
        self.assertIn('DECK-015', c['COMPETITOR_GROUP']['PORQUE'])


class TestMapaDeAcoes(unittest.TestCase):

    def setUp(self):
        self.m = carrega()['MAPA_DE_ACOES']

    def test_investigar_nao_e_agir(self):
        self.assertEqual('WHO CAN INVESTIGATE NOW != WHO SHOULD ACT NOW',
                         self.m['A_DISTINCAO_QUE_MANDA'])

    def test_os_seis_publicos_estao_la(self):
        pub = {p['PUBLICO'] for p in self.m['PUBLICOS']}
        for p in ('MARKET DEVELOPMENT', 'MARKETING', 'REGULATORY / PORTFOLIO',
                  'SCIENCE / TECHNICAL', 'COMMERCIAL', 'SUPPLY'):
            self.assertIn(p, pub)

    def test_commercial_e_supply_nao_recebem_nada_por_padrao(self):
        p = {x['PUBLICO']: x for x in self.m['PUBLICOS']}
        self.assertIn('nada', p['COMMERCIAL']['RECEBE'])
        self.assertIn('nada', p['SUPPLY']['RECEBE'])

    def test_o_md_continua_o_decisor(self):
        p = {x['PUBLICO']: x for x in self.m['PUBLICOS']}
        self.assertIn('decisor central', p['MARKET DEVELOPMENT']['PAPEL'])


class TestAArquiteturaReconheceACamada(unittest.TestCase):
    """Contrato sozinho nao muda o produto. O documento que manda tem de citar."""

    def test_a_porta_unica_declara_as_sete_camadas(self):
        t = doc('piloto', 'ARQUITETURA-DE-PRODUTO-ATUAL.md')
        self.assertIn('CONCORRÊNCIA', t)
        self.assertIn('COMPETITOR_LAYER_IN_ARCHITECTURE = YES', t)
        self.assertIn('META_EXPLICIT_SOURCE             = YES', t)
        self.assertIn('NOT_YET_COMPLETE', t)

    def test_a_porta_unica_lista_as_cinco_perguntas(self):
        t = doc('piloto', 'ARQUITETURA-DE-PRODUTO-ATUAL.md')
        for p in ('quem tem resposta?', 'quem está anunciando?',
                  'quem começou primeiro?', 'ainda existe tempo para agir?'):
            self.assertIn(p, t)

    def test_o_atlas_nomeia_a_meta_ads_library(self):
        t = doc('fontes', 'ATLAS-DE-FONTES-EAME.md')
        self.assertIn('EU-T9-002', t)
        self.assertIn('Meta Ads Library', t)
        self.assertIn('NÃO TESTADO', t)

    def test_o_atlas_separa_registro_de_ativacao_em_t9(self):
        t = doc('fontes', 'ATLAS-DE-FONTES-EAME.md')
        self.assertIn('Separação obrigatória em T9', t)

    def test_a_arquitetura_de_informacao_declara_os_estados(self):
        t = doc('ferramentas', 'ARQUITETURA-DE-INFORMACAO-EAME.md')
        for e in ESTADOS[:4]:
            self.assertIn(e, t)
        self.assertIn('COMPETITOR OBSERVATION CLOCK', t)

    def test_a_matriz_registra_o_cruzamento_da_meta(self):
        t = doc('cruzamentos', 'MATRIZ-DE-CRUZAMENTOS-EAME.md')
        self.assertIn('X-012', t)
        self.assertIn('POSSÍVEL NÃO TESTADO', t)


class TestExibicao(unittest.TestCase):
    """Estado sem texto de exibicao chega cru na tela do cliente."""

    def setUp(self):
        with open(os.path.join(AMOSTRAS, 'DISPLAY-LAYER-V1.json'), encoding='utf-8') as f:
            self.d = json.load(f)

    def regras(self, campo):
        return [r for r in self.d['REGRAS'] if r['SOURCE_FIELD'] == campo]

    def test_todo_estado_competitivo_tem_texto_nas_tres_linguas(self):
        cobertos = {r['SOURCE_VALUE'] for r in self.regras('COMPETITOR_STATE')}
        self.assertEqual(set(ESTADOS), cobertos)
        for r in self.regras('COMPETITOR_STATE'):
            for k in LINGUAS + ('SEMANTIC_RULE',):
                self.assertTrue(r.get(k), r['DISPLAY_KEY'])

    def test_silencio_nunca_e_exibido_como_ausencia(self):
        r = [x for x in self.regras('META_ACTIVITY')
             if x['SOURCE_VALUE'] == 'NOT_OBSERVED'][0]
        for k, termo in zip(LINGUAS, ('consultadas', 'searched', 'consultadas')):
            self.assertIn(termo, r[k].lower(), k)

    def test_nao_consultado_nao_vira_nenhum_anuncio(self):
        r = [x for x in self.regras('META_ACTIVITY')
             if x['SOURCE_VALUE'] == 'NOT_SEARCHED'][0]
        for k in LINGUAS:
            self.assertIsNone(re.search(r'\b(nenhum|no ad|ningun)\b', r[k].lower()), k)

    def test_not_proved_nunca_e_exibido_como_nao_tem(self):
        r = [x for x in self.regras('COMPETITOR_RESPONSE')
             if x['SOURCE_VALUE'] == 'NOT_PROVED'][0]
        for k in LINGUAS:
            self.assertIsNone(re.search(r'\b(nao tem|does not have|no tiene)\b',
                                        r[k].lower()), k)

    def test_a_janela_precoce_nao_vira_oportunidade(self):
        r = [x for x in self.regras('CONVERGENCE_CASE')
             if x['SOURCE_VALUE'] == 'POSSIBLE_EARLY_WINDOW'][0]
        for k in LINGUAS:
            for p in ('white space', 'oportunidad', 'oportunidade', 'opportunity',
                      'vantagem', 'advantage', 'ventaja'):
                self.assertNotIn(p, r[k].lower(), '%s:%s' % (r['DISPLAY_KEY'], k))

    def test_nenhum_texto_competitivo_recomenda_acao(self):
        for campo in self.d['CAMPOS_COMPETITIVOS_ADICIONADOS']:
            for r in self.regras(campo):
                for k in LINGUAS:
                    for p in ('aplique', 'apply now', 'compre', 'buy ', 'vender'):
                        self.assertNotIn(p, r[k].lower(), '%s:%s' % (r['DISPLAY_KEY'], k))


if __name__ == '__main__':
    unittest.main()
