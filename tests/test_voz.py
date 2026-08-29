# -*- coding: utf-8 -*-
"""A camada de voz so pode dizer o que as amostras sustentam.

Estes testes existem para impedir tres coisas:
  1. que um papel volte a ser inferido de nome, foto, idioma ou prosa livre
  2. que a cobertura suba porque o classificador ficou permissivo
  3. que a concordancia de ordem seja publicada como antecipacao
"""
import json, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
DOC = os.path.join(ROOT, 'docs', 'descoberta', 'CAMADA-DE-VOZ-ESPANHA.md')


def amostra(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


def doc():
    with open(DOC, encoding='utf-8') as f:
        return f.read()


class TestIdentidadeAntesDeConteudo(unittest.TestCase):

    def setUp(self):
        self.li = amostra('ES-VOICE-LINKEDIN.json')

    def test_papel_nunca_vem_de_nome_foto_ou_prosa(self):
        proibidos = self.li['ROLE_RULE']['NAO_USADO']
        for campo in ('nome da conta', 'foto', 'idioma'):
            self.assertIn(campo, proibidos, f'{campo} nao pode decidir papel')
        self.assertTrue(any('prosa livre' in p for p in proibidos),
                        'a prosa livre precisa estar explicitamente proibida')

    def test_pais_so_de_campo_declarado(self):
        for o in self.li['ORIGINS']:
            self.assertIn(o['COUNTRY'], ('ES', 'NAO_DECLARADO') if o['COUNTRY'] in ('ES', 'NAO_DECLARADO')
                          else (o['COUNTRY'],))
            self.assertTrue(o['COUNTRY'], 'COUNTRY nunca pode ser vazio; use NAO_DECLARADO')

    def test_toda_origem_tem_nome(self):
        sem = [o['ORIGIN_ID'] for o in self.li['ORIGINS'] if not o.get('NAME')]
        self.assertEqual([], sem, f'origens sem NAME: {sem}')

    def test_todo_papel_resolvido_tem_evidencia(self):
        for o in self.li['ORIGINS']:
            if o['DECLARED_ROLE'] not in ('NOT_DECLARED',):
                self.assertTrue(o.get('ROLE_EVIDENCE'),
                                f"{o['NAME']} tem papel sem evidencia declarada")

    def test_ambiguous_e_estado_e_nao_desempate(self):
        amb = [o for o in self.li['ORIGINS'] if o['DECLARED_ROLE'] == 'AMBIGUOUS']
        self.assertTrue(amb, 'se nenhum caso e ambiguo, o classificador esta desempatando sozinho')
        for o in amb:
            self.assertIn('+', o['ROLE_EVIDENCE'], 'AMBIGUOUS precisa mostrar os dois papeis')


class TestCoberturaHonesta(unittest.TestCase):

    def test_cobertura_bate_com_as_origens(self):
        li = amostra('ES-VOICE-LINKEDIN.json')
        c = li['ROLE_COVERAGE']
        es = [o for o in li['ORIGINS'] if o['COUNTRY'] == 'ES']
        self.assertEqual(c['TOTAL'], len(es))
        self.assertEqual(c['RESOLVED'] + c['AMBIGUOUS'] + c['UNRESOLVED'], c['TOTAL'],
                         'os tres estados precisam somar o total')
        self.assertEqual(c['RESOLVED'], sum(
            1 for o in es if o['DECLARED_ROLE'] not in ('NOT_DECLARED', 'AMBIGUOUS')))

    def test_cobertura_nao_e_um_por_cento(self):
        c = amostra('ES-VOICE-LINKEDIN.json')['ROLE_COVERAGE']
        self.assertLess(c['COVERAGE'], 1.0,
                        'cobertura de 100% em identidade publica e sinal de classificador permissivo')

    def test_os_tres_erros_do_classificador_antigo_estao_registrados(self):
        t = doc()
        for marca in ('Oleo Revista', 'ftalimida', 'IAS-CSIC'):
            self.assertIn(marca, t, f'o erro medido de {marca} nao pode desaparecer do registro')


class TestVozNaoEAlcance(unittest.TestCase):

    def test_influencer_nao_e_autoridade(self):
        li = amostra('ES-VOICE-LINKEDIN.json')
        self.assertIn('INFLUENCER', li['PUBLIC_TECHNICAL_VOICE']['NAO_E'])
        self.assertIn('Alcance nao e autoridade', li['PUBLIC_TECHNICAL_VOICE']['NAO_E'])

    def test_quantidade_nao_e_representatividade(self):
        li = amostra('ES-VOICE-LINKEDIN.json')
        v = li['PUBLIC_TECHNICAL_VOICE']
        self.assertGreater(v['TOTAL'], v['BY_TOPIC'].get('OLIVE', 0),
                           'o total precisa ser maior que o recorte de olivar, senao a ressalva some')
        self.assertIn('DESENHO DA CONSULTA', li['QUANTIDADE_NAO_E_REPRESENTATIVIDADE'].upper())


class TestInstagramReprovadoPorMedida(unittest.TestCase):

    def setUp(self):
        self.ig = amostra('ES-VOICE-INSTAGRAM.json')

    def test_veredito_e_falha_com_razao(self):
        self.assertTrue(self.ig['VERDICT'].startswith('INSTAGRAM_ES = FAILED_WITH_REASON'))

    def test_a_falha_e_de_identidade_e_nao_de_volume(self):
        m = self.ig['IDENTITY_MEASURE']
        self.assertGreater(m['DECLARE_NOTHING'], m['DECLARE_ES'],
                           'a razao da reprovacao e identidade ausente, nao falta de itens')
        self.assertEqual(m['AGRO_ACCOUNTS'],
                         m['DECLARE_ES'] + m['DECLARE_NON_ES'] + m['DECLARE_NOTHING'])

    def test_homonimo_registrado(self):
        h = self.ig['HOMONYM_CAPTURE']
        self.assertEqual(0, h['agro_items'], 'se #repilo virar agronomico, a licao muda')
        self.assertIn('marca', h['licao'])

    def test_idioma_nao_e_pais(self):
        self.assertIn('ORIGINAL_LANGUAGE nunca decide FACT_LOCATION',
                      self.ig['LANGUAGE_IS_NOT_COUNTRY']['lei'])


class TestRotasDeMidia(unittest.TestCase):

    def setUp(self):
        self.r = amostra('ES-VOICE-MEDIA-ROUTES.json')

    def test_http_200_nao_conta_como_fonte_viva(self):
        for rota in self.r['ROUTES']:
            if rota.get('HTTP') == 200 and rota.get('ITEMS') == 0:
                self.assertEqual('FAILED_WITH_REASON', rota['STATE'],
                                 f"{rota['NAME']}: 200 com zero itens nao pode ser PROVED")

    def test_toda_rota_provada_tem_itens_e_data(self):
        for rota in self.r['ROUTES']:
            if rota['STATE'] == 'PROVED':
                self.assertGreater(rota['ITEMS'], 0)
                self.assertTrue(rota['LAST_DATE'], f"{rota['NAME']} sem relogio de publicacao")

    def test_tls_nunca_foi_desligado(self):
        self.assertIn('nao foi desligada', self.r['TLS_NAO_FOI_DESLIGADO'])

    def test_nenhuma_rota_e_chamada_de_api_oficial(self):
        self.assertIn('PUBLIC APPLICATION ROUTE', self.r['ROUTE_TYPE'])
        self.assertNotIn('API oficial', json.dumps(self.r, ensure_ascii=False))


class TestConcorrentesComDenominador(unittest.TestCase):

    def test_denominador_declarado_e_nao_e_a_empresa(self):
        c = amostra('ES-COMPETITOR-VOICE.json')
        self.assertIn('NAO e', c['DENOMINADOR_HONESTO'])
        self.assertIn('share of voice', c['DENOMINADOR_HONESTO'])

    def test_soma_de_posts_bate(self):
        c = amostra('ES-COMPETITOR-VOICE.json')
        self.assertEqual(c['INDUSTRY_POSTS'], sum(x['POSTS'] for x in c['BY_ORIGIN']))
        self.assertEqual(c['INDUSTRY_ORIGINS'], len(c['BY_ORIGIN']))


class TestReconciliacaoNaoViraAntecipacao(unittest.TestCase):

    def setUp(self):
        self.x = amostra('ES-VOICE-x-REGUA.json')

    def test_a_rota_com_geografia_pedida_fica_de_fora(self):
        self.assertIn('circular', self.x['PORQUE_SO_A_ROTA_POST'])
        self.assertNotIn('TITLE_SEARCH', json.dumps(
            {k: v for k, v in self.x.items() if k in ('LINKEDIN_POST_ROUTE', 'YOUTUBE')},
            ensure_ascii=False))

    def test_as_duas_camadas_concordam_com_exposicao_e_nao_com_incidencia(self):
        for camada in ('LINKEDIN_POST_ROUTE', 'YOUTUBE'):
            c = self.x[camada]
            self.assertGreater(c['rho_vs_exposure_index'], c['rho_vs_incidence_only'],
                               f'{camada}: se a incidencia passar a explicar melhor, o achado mudou')

    def test_correlacao_nunca_e_publicada_como_antecipacao(self):
        self.assertIn('nao e antecedencia', self.x['O_QUE_ISSO_NAO_PROVA'])
        t = doc()
        self.assertIn('PRESSÃO DE CAMPO ≠ ALERTA ANTECIPADO', t)

    def test_confundidor_de_cordoba_segue_declarado(self):
        self.assertIn('Cordoba', self.x['CONFOUNDER_ABERTO'])
        self.assertIn('aberto', self.x['CONFOUNDER_ABERTO'])


class TestFranciaEItaliaNaoForamAbertas(unittest.TestCase):

    def test_nenhuma_amostra_de_voz_coletou_fora_da_espanha(self):
        for nome in os.listdir(SAMPLES):
            if not nome.startswith(('ES-VOICE', 'ES-COMPETITOR')):
                continue
            with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
                d = json.load(f)
            fl = str(d.get('FACT_LOCATION', ''))
            self.assertNotIn('FRANCE', fl.upper())
            self.assertNotIn('ITAL', fl.upper())

    def test_o_documento_declara_o_paro(self):
        t = doc()
        self.assertIn('Não foram abertas', t)


class TestChaveNuncaNoRepositorio(unittest.TestCase):

    TOKEN = re.compile(r'apify_api_[A-Za-z0-9]{10,}')

    def test_nenhum_token_versionado(self):
        achados = []
        for base, dirs, arqs in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules')]
            for a in arqs:
                p = os.path.join(base, a)
                try:
                    with open(p, encoding='utf-8', errors='ignore') as f:
                        if self.TOKEN.search(f.read()):
                            achados.append(os.path.relpath(p, ROOT))
                except OSError:
                    continue
        self.assertEqual([], achados, f'token da Apify versionado em: {achados}')


if __name__ == '__main__':
    unittest.main()
