# -*- coding: utf-8 -*-
"""Provas do schema canonico do Supabase.

Um schema que nao se verifica e um desenho. Estas provas garantem que as leis
duras do produto estao EM ESTRUTURA — coluna, check, tabela separada — e nao
apenas escritas num paragrafo que alguem pode contrariar sem perceber.

Nada aqui toca banco: nao ha instancia. As provas leem o JSON canonico, o SQL
gerado a partir dele e os contratos de publicacao e leitura.

Zero rede.
"""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from supabase_schema import carregar, gerar, medir, _pk  # noqa: E402

D = carregar()
SQL = gerar(D)
M = medir(D)
TAB = {t['name']: t for t in D['TABLES']}
VIEWS = {v['name']: v for v in D['VIEWS']}
RPCS = {r['name']: r for r in D['RPCS']}
VOC = D['VOCABULARIES']

SUP = os.path.join(ROOT, 'data', 'supabase')
with open(os.path.join(SUP, 'SUPABASE-PUBLISH-MAP.json'), encoding='utf-8') as f:
    PUB = json.load(f)
with open(os.path.join(SUP, 'SUPABASE-V8-READ-CONTRACT.json'), encoding='utf-8') as f:
    READ = json.load(f)

MIGRATION = os.path.join(ROOT, 'supabase', 'migrations', '0001_initial_canonical_schema.sql')

PAYLOAD_CANONICO = {
    'H1': ['TERRITORIAL_OBSERVATION'],
    'H2': ['REGISTRATION_DEADLINE'],
    'H3': ['COMPETITOR_PRODUCT_IDENTITY'],
    'H4': ['OBSERVED_PAID_ACTIVITY'],
    'H5': ['FIELD_PRESSURE_SERIES'],
    'H6': ['PERSON_CREATOR', 'FARM_BUSINESS_ENTITY', 'CREATOR_CONTENT_PROFILE'],
    'H7': ['SCIENTIFIC_PERSON'],
    'H8': ['COMPANY_LOCAL_ACCOUNT'],
    'H9': ['CONTENT_ENTITY', 'CONTENT_TRANSLATION', 'ONTOLOGY_TERM'],
}


class Base(unittest.TestCase):

    def cols(self, tabela):
        return {c['name']: c for c in TAB[tabela]['columns']}

    def check(self, tabela, nome):
        for ck in TAB[tabela].get('checks', []):
            if ck['name'] == nome:
                return ck
        self.fail('%s nao tem o check %s' % (tabela, nome))


class TestMangueiras(Base):

    def test_ALL_H1_H9_TYPES_MAPPED(self):
        """As nove mangueiras tem tabela com o payload CANONICO."""
        mapeado = {}
        for t in D['TABLES']:
            if t.get('hose_id') and t.get('canonical_payload_type'):
                mapeado.setdefault(t['hose_id'], []).append(t['canonical_payload_type'])
        self.assertEqual(set(mapeado), set(PAYLOAD_CANONICO), 'mangueira sem tabela')
        for hose, esperados in PAYLOAD_CANONICO.items():
            self.assertEqual(sorted(mapeado[hose]), sorted(esperados),
                             '%s nao carrega os payloads canonicos' % hose)

    def test_NO_UI_ALIAS_AS_CANONICAL_TYPE(self):
        """Nenhum alias do casco vira tipo persistido."""
        aliases = {a['UI_ALIAS_INDEX11'] for a in D['UI_ALIAS_MAP']['MAP']
                   if a['UI_ALIAS_INDEX11']}
        self.assertIn('TERRITORIAL_ATTENTION_OBJECT', aliases)
        self.assertIn('ISSUE_EXPERT', aliases)
        persistidos = {t.get('canonical_payload_type') for t in D['TABLES']}
        for alias in aliases:
            self.assertNotIn(alias, persistidos, 'alias %s virou tipo persistido' % alias)
        # e os aliases so aparecem na tabela declarada para isso
        self.assertIn('ui_alias', TAB)
        self.assertEqual(TAB['ui_alias']['columns'][2]['name'], 'ui_alias')

    def test_object_type_nao_colide_com_payload(self):
        """REGULATORY_DEADLINE e OBJECT_TYPE; REGISTRATION_DEADLINE e payload de H2."""
        self.assertIn('REGULATORY_DEADLINE', VOC['object_type'])
        self.assertEqual(TAB['registration_deadline']['canonical_payload_type'],
                         'REGISTRATION_DEADLINE')
        self.assertIn('COMPETITOR_IDENTITY_CHAIN', VOC['object_type'])
        self.assertEqual(TAB['competitor_product_identity']['canonical_payload_type'],
                         'COMPETITOR_PRODUCT_IDENTITY')

    def test_subreceptores_declaram_pai_do_vocabulario(self):
        """PARENT_HOSE_ID e campo proprio e pertence a H1..H9 — nao 'H7·CIENCIA'."""
        filhos = [t for t in D['TABLES'] if t.get('parent_hose_id')]
        self.assertTrue(filhos)
        for t in filhos:
            self.assertIn(t['parent_hose_id'], PAYLOAD_CANONICO,
                          '%s tem pai fora do vocabulario' % t['name'])
            self.assertNotIn('·', t['parent_hose_id'])


class TestUmObjetoVariosIdiomas(Base):

    def test_ONE_OBJECT_MULTIPLE_LANGUAGES(self):
        """attention_object nao tem coluna de idioma. Nenhuma."""
        cols = self.cols('attention_object')
        for proibida in ('language', 'lang', 'idioma', 'display_language', 'locale'):
            self.assertNotIn(proibida, cols)
        rep = TAB['attention_object_representation']
        self.assertEqual(_pk(rep), ['attention_object_id', 'language'])
        self.assertIn('language', self.cols('attention_object_representation'))

    def test_a_chave_nao_deriva_do_titulo(self):
        chaves = PUB['IDEMPOTENCIA']['CHAVES_NATURAIS']
        self.assertIn('nunca do titulo', chaves['attention_object'])
        self.assertIn('titulo traduzido', PUB['IDEMPOTENCIA']['PROIBIDO'])

    def test_estruturado_separado_de_representacao(self):
        """Datas, estados e ids ficam no objeto; texto fica na representacao."""
        obj = self.cols('attention_object')
        rep = self.cols('attention_object_representation')
        for estruturado in ('object_type', 'country', 'attention_state', 'as_of_date'):
            self.assertIn(estruturado, obj)
            self.assertNotIn(estruturado, rep)
        for texto in ('title', 'summary', 'what_we_dont_know'):
            self.assertIn(texto, rep)
            self.assertNotIn(texto, obj)

    def test_fallback_declarado_nunca_fingido(self):
        p = D['LANGUAGE_FALLBACK_POLICY']
        self.assertEqual(p['CHAIN'][1:], ['en', 'pt'])
        for campo in ('REQUESTED_LANGUAGE', 'DISPLAY_LANGUAGE', 'FALLBACK_USED'):
            self.assertIn(campo, p['SEMPRE_DECLARAR'])
        self.assertIn('Nunca fabricar traducao', p['REGRA'])
        r = READ['IDIOMA_NA_LEITURA']
        self.assertEqual(r['SEM_NENHUMA']['FALLBACK_USED'], 'NO_REPRESENTATION_AVAILABLE')
        self.assertIsNone(r['SEM_NENHUMA']['text'])
        self.assertIn('resolve_representation', RPCS)

    def test_vocabulario_de_idioma_e_fechado(self):
        self.assertEqual(VOC['language_code'],
                         ['pt', 'en', 'es', 'fr', 'it', 'MULTILINGUAL', 'UNKNOWN'])
        self.assertIn("CREATE TYPE language_code AS ENUM", SQL)

    def test_unknown_e_o_default_nao_o_traco(self):
        """'—' nunca vira valor persistido: nao esta no enum."""
        self.assertNotIn('—', VOC['language_code'])
        self.assertEqual(self.cols('evidence')['source_language']['default'], "'UNKNOWN'")
        self.assertEqual(self.cols('content_entity')['source_language']['default'],
                         "'UNKNOWN'")


class TestEvidencia(Base):

    def test_ORIGINAL_EVIDENCE_PRESERVED(self):
        cols = self.cols('evidence')
        self.assertIn('original_text', cols)
        self.assertIn('source_language', cols)
        self.assertIn('document_excerpt', cols)
        self.assertIn('source_url', cols)
        self.assertEqual(D['LANGUAGE_FALLBACK_POLICY']['EVIDENCIA'].count('sempre'), 1)
        self.assertIn('nunca entra na cadeia de fallback',
                      D['LANGUAGE_FALLBACK_POLICY']['EVIDENCIA'])

    def test_TRANSLATION_SEPARATE_FROM_ORIGINAL(self):
        """Tabelas diferentes: um UPDATE nao sobrescreve o original por acidente."""
        self.assertIn('content_entity', TAB)
        self.assertIn('content_translation', TAB)
        orig = self.cols('content_entity')
        trad = self.cols('content_translation')
        self.assertIn('original_text', orig)
        self.assertNotIn('original_text', trad)
        self.assertIn('translated_text', trad)
        self.assertNotIn('translated_text', orig)
        for campo in ('translation_provenance', 'translation_quality', 'translated_at'):
            self.assertIn(campo, trad)
        self.assertIn('source_text_hash', trad)

    def test_localidade_da_fonte_nao_e_localidade_do_fato(self):
        cols = self.cols('evidence')
        self.assertIn('source_location_country', cols)
        self.assertIn('fact_location_geo_id', cols)
        self.assertNotEqual(cols['source_location_country']['type'],
                            cols['fact_location_geo_id']['type'])

    def test_evidencia_nao_e_duplicada_por_uso(self):
        """Cinco consumidores, uma linha. Todos por chave estrangeira."""
        usos = ['attention_object_evidence', 'convergence_leg', 'action_evidence',
                'object_event', 'object_relation']
        for u in usos:
            self.assertIn(u, TAB)
        refs = [c for t in D['TABLES'] for c in t['columns']
                if c.get('fk') == 'evidence.evidence_id']
        self.assertGreaterEqual(len(refs), 8)

    def test_offsets_andam_em_par(self):
        ck = self.check('evidence', 'offsets_andam_em_par')
        self.assertIn('passage_start', ck['expr'])
        self.assertIn('passage_end', ck['expr'])


class TestSeparacoesQueNaoPodemColapsar(Base):

    def test_SCI_PERSON_NE_SCI_PUBLICATION(self):
        self.assertIn('scientific_person', TAB)
        self.assertIn('scientific_publication', TAB)
        self.assertEqual(TAB['scientific_person']['canonical_payload_type'],
                         'SCIENTIFIC_PERSON')
        self.assertEqual(TAB['scientific_publication']['canonical_payload_type'],
                         'SCIENTIFIC_PUBLICATION')
        # N:N por tabela propria — nenhum dos dois e atributo do outro
        self.assertIn('publication_author', TAB)
        self.assertEqual(_pk(TAB['publication_author']), ['publication_id', 'person_id'])
        self.assertNotIn('publication_count', self.cols('scientific_person'))

    def test_expertise_e_relacao_e_nao_atributo(self):
        """Pessoa x cultura x problema x evidencia x estado."""
        pk = _pk(TAB['issue_expertise'])
        self.assertEqual(pk, ['person_id', 'crop_term_id', 'issue_term_id'])
        cols = self.cols('issue_expertise')
        self.assertIn('issue_expertise_state', cols)
        self.assertIn('evidence_id', cols)
        self.assertNotIn('issue_expertise_proved', self.cols('person'))
        ck = self.check('issue_expertise', 'expertise_provada_exige_evidencia')
        self.assertIn('evidence_id IS NOT NULL', ck['expr'])

    def test_REG_DEADLINE_NE_LOCAL_PORTFOLIO(self):
        self.assertIn('registration_deadline', TAB)
        self.assertIn('local_adama_portfolio_context', TAB)
        d = self.cols('registration_deadline')
        p = self.cols('local_adama_portfolio_context')
        self.assertIn('registered_response_state', p)
        self.assertNotIn('registered_response_state', d)
        self.assertIn('deadline_date', d)
        self.assertNotIn('deadline_date', p)
        ck = self.check('local_adama_portfolio_context', 'portfolio_e_sempre_contexto')
        self.assertIn('is_context_not_evidence = true', ck['expr'])

    def test_registro_de_qualquer_titular_nao_e_portfolio_adama(self):
        """registration tem holder proprio; product tem is_adama separado."""
        self.assertIn('holder_organization_id', self.cols('registration'))
        self.assertIn('is_adama', self.cols('product'))
        self.assertNotIn('is_adama', self.cols('registration'))

    def test_CREATOR_ENTITY_NE_FIELD_VOICE_OBSERVATION(self):
        for t in ('person_creator', 'farm_business_entity', 'creator_content_profile',
                  'field_voice_observation'):
            self.assertIn(t, TAB)
        obs = self.cols('field_voice_observation')
        self.assertIn('observation_id', obs)
        self.assertNotIn('observation_id', self.cols('person_creator'))
        self.assertNotIn('observation_id', self.cols('farm_business_entity'))
        # os tres payloads de H6 sao tabelas distintas
        h6 = [t['name'] for t in D['TABLES']
              if t.get('hose_id') == 'H6' and t.get('canonical_payload_type')]
        self.assertEqual(len(h6), 3)

    def test_pessoa_e_negocio_nao_se_somam(self):
        h6 = next(i for i in PUB['INPUTS'] if i['HOSE_ID'] == 'H6')
        self.assertIn('somar as duas linhas', h6['PROIBIDO_NA_VALIDACAO'])
        self.assertIn('CREATORS_READY', ' '.join(h6['GUARDS']))
        ck = self.check('creator_content_profile',
                        'perfil_pertence_a_exatamente_uma_entidade')
        self.assertIn('= 1', ck['expr'])

    def test_gdpr_bloqueia_pessoa_identificada(self):
        ck = self.check('field_voice_observation',
                        'pessoa_identificada_exige_gdpr_tratado')
        self.assertIn("PERSON_CREATOR", ck['expr'])
        self.assertIn("NOT_STARTED", ck['expr'])


class TestAcao(Base):

    def test_ACTION_TYPE_CANONICAL(self):
        self.assertEqual(VOC['action_type'],
                         ['BUSINESS_DECISION', 'SYSTEM_DECISION', 'INVESTIGATION'])
        for rotulo in ('BUSINESS', 'SYSTEM'):
            self.assertNotIn(rotulo, VOC['action_type'])
        self.assertEqual(self.cols('action')['action_type']['type'], 'action_type')

    def test_BUSINESS_DECISION_REQUIRES_EVIDENCE(self):
        """A base e N:N: a regra se verifica CONTANDO linhas, nao lendo um campo."""
        self.assertIn('action_evidence', TAB)
        self.assertEqual(_pk(TAB['action_evidence']), ['action_id', 'evidence_id'])
        v = VIEWS['v_action_map']
        self.assertIn('evidence_basis_count', v['derives'])
        self.assertIn('is_defensible', v['derives'])
        self.assertIn('action_evidence', v['reads'])
        self.assertIn('is_publishable', self.cols('action'))
        self.assertIn('zero linhas', v['why'])

    def test_prazo_regulatorio_nunca_autoriza_negocio(self):
        ck = self.check('regulatory_deadline_object',
                        'prazo_nao_autoriza_decisao_de_negocio')
        self.assertIn("<> 'BUSINESS_DECISION'", ck['expr'])


class TestConvergencia(Base):

    def test_CONVERGENCE_INDEPENDENCE_REPRODUCIBLE(self):
        """Nao ha contador. A contagem sai das pernas."""
        cols = self.cols('convergence_proposition')
        for proibida in ('independent_family_count', 'leg_count', 'convergence_state'):
            self.assertNotIn(proibida, cols)
        self.assertIn('no_counter_column', TAB['convergence_proposition'])
        v = VIEWS['v_convergence_state']
        self.assertIn('independent_family_count', v['derives'])
        self.assertIn('convergence_state', v['derives'])
        self.assertIn('convergence_leg', v['reads'])

    def test_perna_carrega_os_seis_campos(self):
        cols = self.cols('convergence_leg')
        for campo in ('signal_family', 'evidence_id', 'independence_state',
                      'dependency_type', 'source_id', 'observed_at'):
            self.assertIn(campo, cols)

    def test_dependente_nao_conta_como_familia(self):
        ck = self.check('convergence_leg', 'dependente_declara_o_tipo_e_o_alvo')
        self.assertIn('depends_on_leg_id IS NOT NULL', ck['expr'])
        ck2 = self.check('convergence_leg', 'independente_nao_tem_alvo')
        self.assertIn('depends_on_leg_id IS NULL', ck2['expr'])

    def test_tres_tipos_de_convergencia_nunca_somados(self):
        self.assertEqual(set(VOC['convergence_kind']),
                         {'PHENOMENON_CONVERGENCE', 'IDENTITY_CONVERGENCE',
                          'CONTEXTUAL_ALIGNMENT'})
        self.assertIn('convergence_kind', self.cols('convergence_proposition'))

    def test_DEPENDENCY_GRAPH_REPRODUCIBLE(self):
        self.assertEqual(set(VOC['dependency_type']),
                         {'SOURCE_DEPENDENCY', 'OBSERVATION_DEPENDENCY',
                          'ENTITY_DEPENDENCY', 'DERIVATION_DEPENDENCY',
                          'SEMANTIC_DEPENDENCY', 'INDEPENDENT_SOURCE'})
        self.assertIn('dependency_edge', TAB)
        arestas = {(e['from_id'], e['to_id'], e['dependency_type'])
                   for e in PUB['DEPENDENCY_EDGES_A_PUBLICAR']}
        self.assertIn(('H3', 'H4', 'DERIVATION_DEPENDENCY'), arestas)
        self.assertIn(('H5', 'H1', 'SOURCE_DEPENDENCY'), arestas)

    def test_as_oito_familias_de_sinal(self):
        self.assertEqual(len(VOC['signal_family']), 8)
        self.assertIn('META_PAID_ADS', VOC['signal_family'])
        self.assertIn('FIELD_HISTORICAL', VOC['signal_family'])


class TestTimeline(Base):

    def test_TIMELINE_STATES_SEPARATE(self):
        """state_before e state_after sao colunas. A seta e apresentacao."""
        cols = self.cols('object_event')
        self.assertIn('state_before', cols)
        self.assertIn('state_after', cols)
        self.assertEqual(cols['state_before']['type'], 'attention_state')
        self.assertEqual(cols['state_after']['type'], 'attention_state')
        for proibida in ('state_transition', 'state_label', 'state'):
            self.assertNotIn(proibida, cols)
        v = VIEWS['v_object_timeline']
        self.assertIn('state_transition_label', v['derives'])
        self.assertIn('SO nesta view', v['why'])

    def test_evento_carrega_os_campos_do_contrato(self):
        cols = self.cols('object_event')
        for campo in ('event_id', 'event_type', 'event_at', 'event_at_resolution',
                      'source_id', 'observation_id', 'what_changed',
                      'signal_family_added', 'gap_reason', 'trigger_id'):
            self.assertIn(campo, cols)

    def test_sem_data_nao_se_inventa_precisao(self):
        ck = self.check('object_event', 'sem_data_sem_precisao')
        self.assertIn("event_at_resolution = 'NOT_KNOWN'", ck['expr'])
        ck2 = self.check('object_event', 'vazio_temporal_declara_o_motivo')
        self.assertIn('gap_reason IS NOT NULL', ck2['expr'])
        self.assertIn('GAP', VOC['event_type'])


class TestGeografia(Base):

    def test_LOCALITY_TEXT_NE_POINT(self):
        ck = self.check('geo_anchor', 'locality_text_nao_e_point')
        self.assertIn("LOCALITY_TEXT", ck['expr'])
        self.assertIn('geometry IS NULL', ck['expr'])
        cols = self.cols('geo_anchor')
        self.assertIn('locality_text', cols)
        self.assertIn('geometry', cols)
        self.assertIn('geo_resolution', cols)

    def test_ponto_exige_geometria_e_geometria_exige_origem(self):
        ck = self.check('geo_anchor', 'point_exige_geometria')
        self.assertIn('geometry IS NOT NULL', ck['expr'])
        ck2 = self.check('geo_anchor', 'geometria_exige_origem')
        self.assertIn('geometry_source_id IS NOT NULL', ck2['expr'])

    def test_sete_resolucoes(self):
        self.assertEqual(VOC['geo_resolution'],
                         ['COUNTRY', 'NUTS2', 'PROVINCE', 'MUNICIPALITY',
                          'LOCALITY_TEXT', 'POINT', 'NOT_KNOWN'])

    def test_view_do_mapa_deriva_o_que_pode_desenhar(self):
        v = VIEWS['v_crop_map_point']
        self.assertIn('is_drawable', v['derives'])
        self.assertIn('undrawable_reason', v['derives'])
        self.assertIn('O cliente nao decide', v['why'])


class TestSerie(Base):

    def test_MEAN_REQUIRES_N(self):
        cols = self.cols('field_pressure_reading')
        self.assertIs(cols['n']['null'], False)
        ck = self.check('field_pressure_reading', 'n_positivo')
        self.assertEqual(ck['expr'], 'n > 0')
        self.assertIn('media nunca viaja sem o n', cols['n']['note'])

    def test_serie_separada_das_leituras(self):
        self.assertIn('field_pressure_series', TAB)
        self.assertIn('field_pressure_reading', TAB)
        s = self.cols('field_pressure_series')
        for campo in ('baseline_kind', 'baseline_state', 'cohort_state', 'backtest_state',
                      'independence_from_territorial_state'):
            self.assertIn(campo, s)
            self.assertNotIn(campo, self.cols('field_pressure_reading'))

    def test_ledger_nao_e_duplicado_em_tabela(self):
        led = D['LEDGER_DERIVATIONS']
        self.assertEqual(led['RAIF_SEASONS_AVAILABLE']['VALOR_CANONICO'], 23)
        self.assertEqual(led['RAIF_READINGS_TOTAL']['VALOR_CANONICO'], 148964)
        self.assertIn('metricas_canonicas', led['ONDE_MORA_A_VERDADE'])
        for t in D['TABLES']:
            for c in t['columns']:
                self.assertNotIn('seasons_available', c['name'])
                self.assertNotIn('readings_total', c['name'])


class TestRegulatorio(Base):

    def test_EXPIRY_NE_WITHDRAWAL(self):
        ck = self.check('registration_deadline', 'expiry_nao_e_withdrawal')
        self.assertEqual(ck['expr'], 'expiry_is_withdrawal = false')
        cols = self.cols('registration_deadline')
        self.assertEqual(cols['expiry_is_withdrawal']['default'], 'false')
        self.assertIn('status_as_declared_by_source', cols)

    def test_status_da_fonte_nunca_reinterpretado(self):
        for tabela in ('registration_deadline', 'regulatory_deadline_object'):
            self.assertIn('status_as_declared_by_source', self.cols(tabela))

    def test_tipo_regulatorio_nao_tem_cultura_nem_problema(self):
        """NOT_APPLICABLE vira ausencia de coluna, nao coluna nula."""
        cols = self.cols('regulatory_deadline_object')
        for proibida in ('crop_term_id', 'issue_term_id', 'region', 'geo_id'):
            self.assertNotIn(proibida, cols)


class TestComunicacaoPublica(Base):

    def test_NOT_STARTED_NE_NO_COMMUNICATION(self):
        cols = self.cols('company_local_account')
        self.assertEqual(cols['content_collection_stage']['default'], "'NOT_STARTED'")
        self.assertEqual(VOC['content_collection_stage'],
                         ['NOT_STARTED', 'RUNNING', 'PARTIAL', 'COMPLETE'])
        h8 = next(i for i in PUB['INPUTS'] if i['HOSE_ID'] == 'H8')
        self.assertIn('NAO e ausencia de comunicacao', h8['POR_QUE_ZERO'])
        self.assertEqual(h8['EXPECTED_ENTITY_COUNT']['company_local_account'], 22)
        self.assertEqual(h8['EXPECTED_ENTITY_COUNT']['company_public_content'], 0)

    def test_a_conta_existe_antes_do_conteudo(self):
        self.assertIn('company_local_account', TAB)
        self.assertIn('company_public_content', TAB)
        cols = self.cols('company_local_account')
        self.assertIn('identity_resolved_at', cols)
        self.assertIn('page_role', cols)
        self.assertIn('country_scope', cols)


class TestRelogios(Base):

    def test_PIPELINE_LATENCY_NE_OBSERVATION_AGE(self):
        cols = self.cols('source_clock')
        self.assertIn('observation_age_days', cols)
        self.assertIn('pipeline_latency_state', cols)
        self.assertIn('pipeline_latency_seconds', cols)
        self.assertIn('idade do FATO', cols['observation_age_days']['note'])

    def test_latencia_sem_instrumentacao_nao_vira_zero(self):
        ck = self.check('source_clock', 'latencia_sem_medicao_e_nula')
        self.assertIn('pipeline_latency_seconds IS NULL', ck['expr'])
        self.assertEqual(cols_default(TAB, 'source_clock', 'pipeline_latency_state'),
                         "'NOT_MEASURED'")

    def test_sete_relogios_do_objeto_nunca_se_fundem(self):
        self.assertEqual(len(VOC['clock_kind']), 7)
        self.assertEqual(_pk(TAB['object_clock']), ['attention_object_id', 'clock_kind'])
        self.assertIn('resolution', self.cols('object_clock'))


class TestEstadoDeCarga(Base):

    def test_request_state_nao_vira_enum(self):
        nao = D['NAO_PERSISTIR']
        self.assertEqual(set(nao['request_state']),
                         {'UNWIRED', 'LOADING', 'ERROR_FAIL_CLOSED'})
        for proibido in nao['request_state']:
            for valores in VOC.values():
                self.assertNotIn(proibido, valores,
                                 '%s virou valor persistido' % proibido)
        self.assertNotIn('request_state', VOC)
        self.assertIn('CAMADA DE APLICACAO', nao['POR_QUE'])

    def test_data_state_e_pipeline_state_existem(self):
        self.assertEqual(set(VOC['data_state']),
                         {'READY', 'EMPTY_VALID', 'NOT_STARTED', 'NOT_AVAILABLE', 'BLOCKED'})
        self.assertIn('pipeline_state', VOC)

    def test_o_contrato_de_leitura_declara_a_juncao(self):
        e = READ['ESTADOS_NA_LEITURA']
        self.assertEqual(set(e['O_QUE_O_RECEPTOR_ACRESCENTA']),
                         {'UNWIRED', 'LOADING', 'ERROR_FAIL_CLOSED'})
        self.assertIn('sem nunca degradar para EMPTY_VALID', e['COMO_O_V8_COMBINA'])


class TestPublisher(Base):

    def test_PUBLISHER_IDEMPOTENT(self):
        idem = PUB['IDEMPOTENCIA']
        self.assertIn('nao duplica objeto', idem['REGRA'])
        for familia in ('attention_object', 'evidence', 'object_event',
                        'content_translation', 'field_pressure_reading',
                        'convergence_leg'):
            self.assertIn(familia, idem['CHAVES_NATURAIS'])
        self.assertIn('titulo traduzido', idem['PROIBIDO'])

    def test_publicado_exige_sombra_aprovada(self):
        ck = self.check('publish_run', 'publicado_exige_sombra_aprovada')
        self.assertIn('shadow_validation_passed = true', ck['expr'])

    def test_PROVENANCE_REACHES_SOURCE_FREEZE(self):
        self.assertIn('publish_run', TAB)
        self.assertIn('publish_run_freeze', TAB)
        cols = self.cols('publish_run_freeze')
        for campo in ('repository', 'path', 'commit_sha'):
            self.assertIn(campo, cols)
        self.assertIn('pipeline_version', self.cols('publish_run'))
        v = VIEWS['v_publish_provenance']
        self.assertIn('publish_run_freeze', v['reads'])
        self.assertIn('storage_provenance', v['reads'])

    def test_leitura_do_github_e_por_commit_fixo(self):
        p = D['PROVENANCE_ENVELOPE']
        self.assertIn('COMMIT_SHA', p['PINNED_READ_RULE'])
        self.assertIn('COMMIT_SHA fixo', PUB['LEI_DE_LEITURA'])

    def test_a_branch_do_h2_esta_declarada_e_nao_escondida(self):
        """Uma entrada fora da lei, dita em voz alta."""
        h2 = next(i for i in PUB['INPUTS'] if i['HOSE_ID'] == 'H2')
        self.assertEqual(h2['SOURCE_COMMIT'], 'RESOLVER_ANTES_DA_CARGA')
        self.assertIn('BRANCH', h2['NOTA_DO_COMMIT'])

    def test_contagem_que_nao_pode_ser_afirmada_e_NOT_MEASURED(self):
        h1 = next(i for i in PUB['INPUTS'] if i['HOSE_ID'] == 'H1')
        self.assertEqual(h1['EXPECTED_ENTITY_COUNT']['attention_object'], 'NOT_MEASURED')
        self.assertIn('seria inventa-lo', h1['POR_QUE_NOT_MEASURED'])


class TestProveniencia(Base):

    def test_duas_proveniencias_separadas(self):
        self.assertIn('source_provenance', TAB)
        self.assertIn('storage_provenance', TAB)
        self.assertIn('apagaria a origem externa', TAB['source_provenance']['why'])
        self.assertIn('origem externa real',
                      D['PROVENANCE_ENVELOPE']['DUAS_PROVENIENCIAS']['source_provenance'])

    def test_backends_nao_se_misturam(self):
        ck = self.check('storage_provenance', 'backends_nao_se_misturam')
        self.assertIn('repository IS NOT NULL AND table_or_view IS NOT NULL', ck['expr'])
        self.check('storage_provenance', 'github_exige_commit_e_caminho')
        self.check('storage_provenance', 'supabase_exige_tabela_e_chave')

    def test_os_dois_envelopes_tem_os_campos_do_contrato(self):
        p = D['PROVENANCE_ENVELOPE']
        for campo in ('REPOSITORY', 'PATH', 'COMMIT_SHA', 'HASH', 'SOURCE_ID', 'AS_OF_DATE'):
            self.assertIn(campo, p['GITHUB'])
        for campo in ('SCHEMA', 'TABLE_OR_VIEW', 'PRIMARY_KEY', 'SNAPSHOT_ID',
                      'CAPTURED_AT', 'SOURCE_ID', 'AS_OF_DATE'):
            self.assertIn(campo, p['SUPABASE'])

    def test_NO_FRONTEND_SECRET(self):
        seg = D['PROVENANCE_ENVELOPE']['SECURITY']
        for proibido in ('SERVICE_ROLE_KEY', 'secret', 'token'):
            self.assertIn(proibido, seg['NEVER_IN_FRONTEND'])
        self.assertIn('SERVICE_ROLE_KEY NUNCA vai para o frontend', SQL)
        self.assertIn('SEM_SEGREDO_NO_FRONTEND', READ['PRINCIPIOS'])
        # e o schema nao guarda credencial em lugar nenhum.
        # 'key' sozinho nao serve como termo: casa com unknown_key e primary_key,
        # que sao estrutura. Confundir mencao com uso ja me custou tres testes.
        for t in D['TABLES']:
            for c in t['columns']:
                nome = c['name'].lower()
                for proibido in ('service_role', 'api_key', 'apikey', 'secret',
                                 'token', 'password', 'senha', 'credential'):
                    self.assertNotIn(proibido, nome,
                                     '%s.%s parece guardar credencial' % (t['name'], nome))

    def test_o_portal_so_escreve_telemetria(self):
        e = READ['ESCRITA_PELO_PORTAL']
        self.assertEqual(e['PERMITIDO'], ['entry_path_event'])
        self.assertIn('nao escreve objeto', e['PROIBIDO'])
        self.assertIn('sem user_id', TAB['entry_path_event']['privacy'])


class TestMigrationEDerivacao(Base):

    def test_a_migration_e_gerada_e_nao_editada(self):
        with open(MIGRATION, encoding='utf-8') as f:
            disco = f.read()
        self.assertEqual(disco, SQL, 'a migration no disco divergiu do JSON canonico')
        self.assertIn('NAO EDITAR A MAO', disco)
        self.assertIn('MIGRATION_APPLIED = NO', disco)

    def test_rls_ligada_em_todas_as_tabelas(self):
        for t in D['TABLES']:
            self.assertIn('ALTER TABLE %s ENABLE ROW LEVEL SECURITY;' % t['name'], SQL)

    def test_toda_tabela_tem_por_que_e_chave(self):
        self.assertEqual(M['TABLES_WITHOUT_WHY'], [])
        self.assertEqual(M['TABLES_WITHOUT_PK'], [])

    def test_os_numeros_do_desenho_sao_derivados(self):
        self.assertEqual(M['TABLES_TOTAL'], len(D['TABLES']))
        self.assertEqual(M['VIEWS_TOTAL'], len(D['VIEWS']))
        self.assertEqual(M['RPCS_TOTAL'], len(D['RPCS']))
        self.assertGreater(M['CHECKS_TOTAL'], 25)

    def test_nada_foi_aplicado_nem_publicado(self):
        for chave, valor in D['MODE'].items():
            self.assertEqual(valor, 'NO', chave)

    def test_o_script_nao_toca_a_rede(self):
        import ast
        with open(os.path.join(ROOT, 'scripts', 'supabase_schema.py'), encoding='utf-8') as f:
            arvore = ast.parse(f.read())
        proibidos = {'requests', 'urllib', 'http', 'socket', 'httpx', 'subprocess', 'psycopg2'}
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for a in no.names:
                    self.assertNotIn(a.name.split('.')[0], proibidos)
            elif isinstance(no, ast.ImportFrom) and no.module:
                self.assertNotIn(no.module.split('.')[0], proibidos)


def cols_default(tab, tabela, coluna):
    for c in tab[tabela]['columns']:
        if c['name'] == coluna:
            return c.get('default')
    return None


if __name__ == '__main__':
    unittest.main()
