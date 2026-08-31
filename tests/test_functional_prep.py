# -*- coding: utf-8 -*-
"""Provas dos adaptadores funcionais NAO CONECTADOS ao casco.

Nove classes de prova, uma por linha do briefing: parsing, cardinalidade, campos
obrigatorios, pais, unidade analitica, ausencia explicita, incompatibilidade de
schema, colisoes e preservacao de proveniencia.

NOTA SOBRE O CAMINHO DESTES TESTES. O briefing sugeriu `tests/functional-prep/`.
Nao foi usado: `python -m unittest discover -s tests` NAO entra em diretorio cujo nome
nao e um identificador Python valido — o hifen faria a suite ser pulada em silencio.
Teste que nao roda e pior que teste que falta, e esse e exatamente o defeito que a
auditoria de 2026-08-29 encontrou noutra camada. Fica na convencao do repositorio.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import functional_prep as fp  # noqa: E402

FIX = os.path.join(ROOT, 'data', 'functional-sandbox', 'fixtures')
CREATOR = os.path.join(FIX, 'creator-capability-sample.json')
PUBCOMM = os.path.join(FIX, 'public-comm-batch-sample.json')
QUEBRADO = os.path.join(FIX, 'schema-incompativel.json')
EXPERT = os.path.join(ROOT, 'data', 'samples', 'SPEAKER-UNIVERSE-PILOT-V1.json')
# DELTA 2026-08-30
DEEP = os.path.join(FIX, 'creator-deep-corpus-sample.json')
FSX = os.path.join(FIX, 'foresight-crosswalk-sample.json')
FS3L = os.path.join(FIX, 'foresight-three-layer-sample.json')
SCI = os.path.join(FIX, 'science-corpus-targets-sample.json')


class TestParsing(unittest.TestCase):
    """1 · parsing — os tres artefatos reais viram objeto sem erro."""

    def test_creator_parseia(self):
        objs = fp.adaptar_creator_capability(fp.carregar(CREATOR))
        self.assertTrue(objs)

    def test_public_comm_parseia(self):
        objs = fp.adaptar_public_comm(fp.carregar(PUBCOMM))
        self.assertTrue(objs)

    def test_expert_parseia(self):
        objs = fp.adaptar_expert_directory(fp.carregar(EXPERT))
        self.assertTrue(objs)


class TestCardinalidade(unittest.TestCase):
    """2 · cardinalidade — LINHA DE INDICE NAO E ENTIDADE.

    O indice do Creator Map lista a mesma pessoa uma vez por cultura. Contar linha
    devolveria 26 ACTIVATION_READY onde ha 10 entidades: inflacao de 2,6x.
    """

    def test_linha_nao_e_entidade_no_indice_de_estado(self):
        doc = fp.carregar(CREATOR)
        linhas = doc['LOOKUP_BY_ACTIVATION_STATE']['ACTIVATION_READY']
        handles = set(x['HANDLE'] for x in linhas)
        self.assertEqual(len(linhas), 26)
        self.assertEqual(len(handles), 10)

    def test_adaptador_deduplica_por_identidade(self):
        objs = fp.adaptar_creator_capability(fp.carregar(CREATOR))
        c = fp.contar(objs)
        self.assertEqual(c['ROWS'], c['ENTITIES'],
                         'o adaptador deve entregar uma linha por entidade')

    def test_contar_devolve_sempre_os_dois_numeros(self):
        objs = fp.adaptar_creator_capability(fp.carregar(CREATOR))
        c = fp.contar(objs)
        for chave in ('ROWS', 'ENTITIES', 'BY_ANALYTICAL_UNIT'):
            self.assertIn(chave, c)

    def test_metrica_declarada_bate_com_a_medida(self):
        doc = fp.carregar(CREATOR)
        objs = fp.adaptar_creator_capability(doc)
        pessoas = [o for o in objs
                   if o['ANALYTICAL_UNIT'] == 'PERSON'
                   and o['FIELDS']['ACTIVATION_STATE'] == 'ACTIVATION_READY']
        empresas = [o for o in objs
                    if o['ANALYTICAL_UNIT'] == 'FARM_BUSINESS_ENTITY'
                    and o['FIELDS']['ACTIVATION_STATE'] == 'ACTIVATION_READY']
        m = doc['READINESS_METRICS']
        self.assertEqual(len(pessoas), m['PERSON_CREATOR_ACTIVATION_READY'])
        self.assertEqual(len(empresas), m['FARM_BUSINESS_PARTNER_READY'])

    def test_a_soma_nunca_se_chama_creators_ready(self):
        doc = fp.carregar(CREATOR)
        self.assertNotIn('CREATORS_READY', doc['READINESS_METRICS'])
        self.assertIn('Pessoa', doc['METRIC_LAW'])


class TestCamposObrigatorios(unittest.TestCase):
    """3 · campos minimos — o envelope funcional e completo em todo objeto."""

    ENVELOPE = ('ANALYTICAL_UNIT', 'IDENTITY_KEY', 'COUNTRY', 'FIELDS',
                'PROVENANCE', 'WHAT_IS_NOT_KNOWN', 'GUARDRAILS', 'WIRED_TO_CASCO')

    def test_envelope_completo_em_todos(self):
        todos = (fp.adaptar_creator_capability(fp.carregar(CREATOR))
                 + fp.adaptar_public_comm(fp.carregar(PUBCOMM))
                 + fp.adaptar_expert_directory(fp.carregar(EXPERT)))
        for o in todos:
            for c in self.ENVELOPE:
                self.assertIn(c, o, 'objeto sem %s: %r' % (c, o.get('IDENTITY_KEY')))

    def test_nada_sai_ligado_ao_casco(self):
        todos = (fp.adaptar_creator_capability(fp.carregar(CREATOR))
                 + fp.adaptar_public_comm(fp.carregar(PUBCOMM)))
        self.assertTrue(all(o['WIRED_TO_CASCO'] is False for o in todos))


class TestPais(unittest.TestCase):
    """4 · pais — nenhum objeto sai sem pais, e o pais nunca e inferido."""

    def test_todo_objeto_tem_pais(self):
        todos = (fp.adaptar_creator_capability(fp.carregar(CREATOR))
                 + fp.adaptar_public_comm(fp.carregar(PUBCOMM))
                 + fp.adaptar_expert_directory(fp.carregar(EXPERT)))
        for o in todos:
            self.assertTrue(o['COUNTRY'], o['IDENTITY_KEY'])

    def test_lote_publico_bate_com_a_contagem_declarada(self):
        doc = fp.carregar(PUBCOMM)
        objs = fp.adaptar_public_comm(doc)
        medido = {}
        for o in objs:
            medido[o['COUNTRY']] = medido.get(o['COUNTRY'], 0) + 1
        self.assertEqual(medido, doc['BY_COUNTRY'])
        self.assertEqual(len(objs), doc['ACCOUNTS_IN_BATCH'])

    def test_country_scope_e_page_role_nao_se_confundem(self):
        objs = fp.adaptar_public_comm(fp.carregar(PUBCOMM))
        for o in objs:
            self.assertEqual(o['FIELDS']['COUNTRY_SCOPE'], 'LOCAL_COUNTRY_PROVED')
            self.assertEqual(o['FIELDS']['PAGE_ROLE'], 'COMPANY')
        guard = objs[0]['GUARDRAILS']
        self.assertTrue(any('COUNTRY_SCOPE != PAGE_ROLE' in g for g in guard))


class TestUnidadeAnalitica(unittest.TestCase):
    """5 · unidade analitica — pessoa, empresa agricola e conta nao se misturam."""

    def test_unidades_declaradas_sao_conhecidas(self):
        todos = (fp.adaptar_creator_capability(fp.carregar(CREATOR))
                 + fp.adaptar_public_comm(fp.carregar(PUBCOMM))
                 + fp.adaptar_expert_directory(fp.carregar(EXPERT)))
        for o in todos:
            self.assertIn(o['ANALYTICAL_UNIT'], fp.UNIDADES)

    def test_pessoa_e_empresa_sao_unidades_diferentes(self):
        objs = fp.adaptar_creator_capability(fp.carregar(CREATOR))
        unidades = set(o['ANALYTICAL_UNIT'] for o in objs)
        self.assertIn('PERSON', unidades)
        self.assertIn('FARM_BUSINESS_ENTITY', unidades)

    def test_juntar_recusa_unidades_misturadas(self):
        misturado = fp.adaptar_creator_capability(fp.carregar(CREATOR))
        contas = fp.adaptar_public_comm(fp.carregar(PUBCOMM))
        with self.assertRaises(fp.UnidadeMisturada):
            fp.juntar(misturado, contas, por='COUNTRY')

    def test_juntar_aceita_lados_homogeneos(self):
        pessoas = [o for o in fp.adaptar_creator_capability(fp.carregar(CREATOR))
                   if o['ANALYTICAL_UNIT'] == 'PERSON']
        contas = fp.adaptar_public_comm(fp.carregar(PUBCOMM))
        pares = fp.juntar(pessoas, contas, por='COUNTRY')
        self.assertTrue(pares)
        for a, b in pares:
            self.assertEqual(a['COUNTRY'], b['COUNTRY'])

    def test_tipos_que_nao_sao_pessoa_nem_empresa_ficam_de_fora(self):
        doc = fp.carregar(CREATOR)
        objs = fp.adaptar_creator_capability(doc)
        tipos = set(o['FIELDS']['ENTITY_TYPE'] for o in objs)
        for proibido in ('MEDIA_ACCOUNT', 'ORGANIZATION', 'OTHER'):
            self.assertNotIn(proibido, tipos)


class TestAusenciaExplicita(unittest.TestCase):
    """6 · ausencia explicita — o que falta sai declarado, nunca como vazio."""

    def test_conta_sem_coleta_declara_a_ausencia_de_conteudo(self):
        doc = fp.carregar(PUBCOMM)
        self.assertEqual(doc['CONTENT_COLLECTION_STAGE'], 'NOT_STARTED')
        objs = fp.adaptar_public_comm(doc)
        for o in objs:
            self.assertEqual(o['FIELDS']['CONTENT_STATE'], 'NOT_COLLECTED')
            self.assertIsNone(o['FIELDS']['CONTENT_ITEMS'])
            self.assertTrue(any('CONTEUDO' in x for x in o['WHAT_IS_NOT_KNOWN']))

    def test_zero_nao_significa_empresa_calada(self):
        doc = fp.carregar(PUBCOMM)
        self.assertIn('NO_CONTENT_COLLECTION_EXECUTED', doc['ZERO_MEANS_NOW'])
        self.assertIn('NUNCA COMPANY_NOT_COMMUNICATING',
                      doc['ZERO_WILL_MEAN_AFTER_A_VALID_RUN'])

    def test_especialista_declara_o_que_nao_vem_do_artefato(self):
        objs = fp.adaptar_expert_directory(fp.carregar(EXPERT))
        for o in objs:
            self.assertEqual(o['FIELDS']['PUBLIC_CHANNEL_STATE'], 'NOT_IN_THIS_ARTIFACT')
            self.assertTrue(any('CONTENT_LINKED' in x for x in o['WHAT_IS_NOT_KNOWN']))

    def test_conta_publica_declara_handoff_ausente(self):
        objs = fp.adaptar_public_comm(fp.carregar(PUBCOMM))
        self.assertEqual(objs[0]['PROVENANCE']['CONTENT_COLLECTION_STAGE'], 'NOT_STARTED')

    def test_deep_corpus_declara_rota_sem_conteudo(self):
        objs = fp.adaptar_creator_deep_corpus(fp.carregar(DEEP))
        sem = [o for o in objs if o['FIELDS']['CONTENT_ROUTE'] != 'PROVED']
        self.assertTrue(sem, 'a fixture precisa conter o caso sem rota de conteudo')
        for o in sem:
            self.assertTrue(any('NO_PROVED_CONTENT_ROUTE' in x
                                for x in o['WHAT_IS_NOT_KNOWN']))

    def test_meta_declarada_nao_verificavel(self):
        objs = fp.adaptar_foresight_three_layer(fp.carregar(FS3L))
        for o in objs:
            self.assertEqual(o['PROVENANCE']['META_LEG'], 'NOT_VERIFIABLE_FROM_ORIGIN')


class TestSchemaIncompativel(unittest.TestCase):
    """7 · incompatibilidade de schema — falha fechada, com o campo que falta no texto."""

    def test_artefato_quebrado_e_recusado(self):
        doc = fp.carregar(QUEBRADO)
        for fn in (fp.adaptar_creator_capability, fp.adaptar_public_comm,
                   fp.adaptar_expert_directory):
            with self.assertRaises(fp.SchemaIncompativel):
                fn(doc)

    def test_a_mensagem_nomeia_o_que_falta(self):
        with self.assertRaises(fp.SchemaIncompativel) as ctx:
            fp.adaptar_public_comm({'SOURCE_ID': 'x'})
        self.assertIn('FROZEN_AT', str(ctx.exception))

    def test_objeto_sem_proveniencia_e_recusado(self):
        with self.assertRaises(fp.SchemaIncompativel):
            fp._objeto('PERSON', 'k', 'ES', {}, {'SOURCE_ID': 'x'}, [], ())

    def test_lista_no_lugar_de_objeto_e_recusada(self):
        with self.assertRaises(fp.SchemaIncompativel):
            fp.adaptar_creator_capability([])


class TestColisoes(unittest.TestCase):
    """8 · colisoes — chaves de identidade nao se repetem dentro de uma unidade."""

    def test_chave_unica_por_objeto_creator(self):
        objs = fp.adaptar_creator_capability(fp.carregar(CREATOR))
        chaves = [o['IDENTITY_KEY'] for o in objs]
        self.assertEqual(len(chaves), len(set(chaves)))

    def test_url_de_conta_nao_colide(self):
        objs = fp.adaptar_public_comm(fp.carregar(PUBCOMM))
        chaves = [o['IDENTITY_KEY'] for o in objs]
        self.assertEqual(len(chaves), len(set(chaves)))

    def test_person_id_de_especialista_nao_colide(self):
        objs = fp.adaptar_expert_directory(fp.carregar(EXPERT))
        chaves = [o['IDENTITY_KEY'] for o in objs]
        self.assertEqual(len(chaves), len(set(chaves)))

    def test_mesma_empresa_em_varias_contas_nao_vira_uma(self):
        objs = fp.adaptar_public_comm(fp.carregar(PUBCOMM))
        empresas = set(o['FIELDS']['COMPANY'] for o in objs)
        self.assertLess(len(empresas), len(objs),
                        'o lote deve ter mais contas do que empresas — conta != empresa')


class TestProveniencia(unittest.TestCase):
    """9 · preservacao de proveniencia — nada sai sem SOURCE_ID e AS_OF_DATE."""

    def test_todo_objeto_carrega_source_id_e_data(self):
        todos = (fp.adaptar_creator_capability(fp.carregar(CREATOR))
                 + fp.adaptar_public_comm(fp.carregar(PUBCOMM))
                 + fp.adaptar_expert_directory(fp.carregar(EXPERT)))
        for o in todos:
            self.assertTrue(o['PROVENANCE'].get('SOURCE_ID'))
            self.assertTrue(o['PROVENANCE'].get('AS_OF_DATE'))
            self.assertTrue(o['PROVENANCE'].get('CAPABILITY'))

    def test_evidencia_de_identidade_sobrevive(self):
        objs = fp.adaptar_public_comm(fp.carregar(PUBCOMM))
        for o in objs:
            self.assertTrue(o['PROVENANCE'].get('IDENTITY_EVIDENCE'))
            self.assertTrue(o['PROVENANCE'].get('COUNTRY_SCOPE_EVIDENCE'))

    def test_manifesto_de_fixture_aponta_para_commit_fixado(self):
        man = fp.carregar(os.path.join(FIX, 'FIXTURES-PROVENANCE.json'))
        for o in man['ORIGENS']:
            self.assertIn('SOURCE_COMMIT', o)
            self.assertIn('SOURCE_PATH', o)
    def test_a_ausencia_do_foresight_foi_superada_e_nao_apagada(self):
        """`NOT_FOUND_AT_SNAPSHOT != DOES_NOT_EXIST`.

        A medicao de ausencia nao e apagada: ela e marcada SUPERSEDED, com a data em que
        deixou de valer. Apagar esconderia que a afirmacao existiu e estava certa para o
        snapshot dela.
        """
        man = fp.carregar(os.path.join(FIX, 'FIXTURES-PROVENANCE.json'))
        f = man['CAPACIDADE_SEM_ARTEFATO']['COMPETITOR_FORESIGHT']
        self.assertTrue(f['ESTADO'].startswith('SUPERSEDED'))
        self.assertIn('25194e3', f['ONDE'])
        self.assertIn('NOT_FOUND_AT_SNAPSHOT', f['NOTA'])

    def test_a_meta_nao_e_alcancavel_a_partir_de_origin(self):
        man = fp.carregar(os.path.join(FIX, 'FIXTURES-PROVENANCE.json'))
        m = man['CAPACIDADE_SEM_ARTEFATO']['META_COMPETITOR']
        self.assertEqual(m['ESTADO'], 'BRANCH_NOT_PUSHED_TO_ORIGIN')
        self.assertIn('SEGUNDA MAO', m['O_QUE_EXISTE'])


class TestGuardrails(unittest.TestCase):
    """Os guardrails semanticos viajam DENTRO do objeto, nao so no documento."""

    def test_guardrails_comuns_em_todos(self):
        todos = (fp.adaptar_creator_capability(fp.carregar(CREATOR))
                 + fp.adaptar_public_comm(fp.carregar(PUBCOMM))
                 + fp.adaptar_expert_directory(fp.carregar(EXPERT)))
        for o in todos:
            self.assertIn('TEMPORAL_ORDER != CAUSALITY', o['GUARDRAILS'])
            self.assertIn('IDENTITY_PROVED != ISSUE_EXPERTISE_PROVED', o['GUARDRAILS'])

    def test_creator_nao_confirma_problema_de_campo(self):
        objs = fp.adaptar_creator_capability(fp.carregar(CREATOR))
        texto = ' '.join(objs[0]['GUARDRAILS'])
        for proibido in ('FIELD_PROBLEM', 'INCIDENCE', 'MARKET_OPPORTUNITY', 'PRODUCT_FIT'):
            self.assertIn(proibido, texto)

    def test_expert_nao_ordena(self):
        objs = fp.adaptar_expert_directory(fp.carregar(EXPERT))
        texto = ' '.join(objs[0]['GUARDRAILS'])
        self.assertIn('RECURRENCE != AUTHORITY', texto)


class TestUrboleGuard(unittest.TestCase):
    """REGRESSAO OBRIGATORIA · `URBOLE_GUARD = PASS`.

    `SAME_NAME != SAME_COMPETITOR_PRODUCT`. Um portao sem dentes e um portao com zero
    recusas dao a mesma tela — por isso a recusa e EXERCIDA aqui, com a mutacao que a
    provoca, e nao apenas observada no dado real.
    """

    def test_nome_igual_titular_diferente_e_recusado(self):
        # o caso real: marca URBOLE da SYNGENTA, registro espanhol 24157 da ADAMA
        self.assertEqual(
            fp.urbole_guard('URBOLE', 'SYNGENTA', 'ES', 'URBOLE', 'ADAMA', 'ES'),
            'REJECTED_HOLDER_MISMATCH')

    def test_nome_e_titular_iguais_mas_pais_diferente_e_recusado(self):
        self.assertEqual(
            fp.urbole_guard('COLLIS', 'BASF', 'ES', 'COLLIS', 'BASF', 'IT'),
            'REJECTED_COUNTRY_MISMATCH')

    def test_tres_concordancias_promovem(self):
        self.assertEqual(
            fp.urbole_guard('COLLIS', 'BASF', 'ES', 'COLLIS', 'BASF', 'ES'), 'PROVED')

    def test_nome_diferente_nao_e_recusa_e_sim_desconhecido(self):
        self.assertEqual(
            fp.urbole_guard('COLLIS', 'BASF', 'ES', 'REVYCARE', 'BASF', 'ES'), 'NOT_KNOWN')

    def test_guard_e_reexercido_no_adaptador(self):
        objs = fp.adaptar_foresight_crosswalk(fp.carregar(FSX))
        for o in objs:
            f = o['FIELDS']
            if f['LINK_STATE_DECLARED'] == 'PROVED':
                self.assertEqual(f['LINK_STATE_REEXERCISED'], 'PROVED',
                                 'par declarado PROVED que o guard nao sustenta: %s'
                                 % o['IDENTITY_KEY'])

    def test_o_caso_urbole_esta_na_fixture_e_nao_e_proved(self):
        objs = fp.adaptar_foresight_crosswalk(fp.carregar(FSX))
        urbole = [o for o in objs if str(o['FIELDS'].get('BRAND', '')).upper() == 'URBOLE']
        self.assertTrue(urbole, 'a fixture precisa conter o caso URBOLE')
        for o in urbole:
            self.assertNotEqual(o['FIELDS']['LINK_STATE_REEXERCISED'], 'PROVED')

    def test_artefato_declara_o_guard_como_pass(self):
        d = fp.carregar(FS3L)
        self.assertEqual(d['URBOLE_GUARD']['URBOLE_GUARD'], 'PASS')
        self.assertEqual(d['URBOLE_GUARD']['ACEITOS_COMO_PROVED'], 0)


class TestForesight(unittest.TestCase):
    """O Foresight deixou de ser ausencia. `NOT_FOUND_AT_SNAPSHOT != DOES_NOT_EXIST`."""

    def test_freeze_aceito_viaja_na_proveniencia(self):
        objs = fp.adaptar_foresight_crosswalk(fp.carregar(FSX))
        for o in objs:
            p = o['PROVENANCE']
            self.assertEqual(p['FORESIGHT_ARTIFACT_STATE'], 'EXISTS')
            self.assertEqual(p['FORESIGHT_CANONICAL_FREEZE'], 'ACCEPTED')
            self.assertEqual(p['FORESIGHT_SOURCE_COMMIT'], '25194e3')

    def test_nao_e_entrada_de_refresh_final(self):
        objs = (fp.adaptar_foresight_crosswalk(fp.carregar(FSX))
                + fp.adaptar_foresight_three_layer(fp.carregar(FS3L)))
        for o in objs:
            self.assertEqual(o['PROVENANCE']['FINAL_REFRESH_INPUT'], 'NO')

    def test_crop_e_issue_ausentes_e_declarados(self):
        objs = fp.adaptar_foresight_crosswalk(fp.carregar(FSX))
        for o in objs:
            self.assertIsNone(o['FIELDS']['CROP'])
            self.assertIsNone(o['FIELDS']['ISSUE'])
            self.assertTrue(any('CROP e ISSUE' in x for x in o['WHAT_IS_NOT_KNOWN']))

    def test_unidades_do_foresight_nao_se_misturam(self):
        cross = fp.adaptar_foresight_crosswalk(fp.carregar(FSX))
        tres = fp.adaptar_foresight_three_layer(fp.carregar(FS3L))
        with self.assertRaises(fp.UnidadeMisturada):
            fp.juntar(cross + tres, cross, por='COUNTRY')

    def test_chaves_nao_colidem(self):
        for fn, path in ((fp.adaptar_foresight_crosswalk, FSX),
                         (fp.adaptar_foresight_three_layer, FS3L)):
            chaves = [o['IDENTITY_KEY'] for o in fn(fp.carregar(path))]
            self.assertEqual(len(chaves), len(set(chaves)))

    def test_tupla_e_produto_sao_unidades_diferentes(self):
        d = fp.carregar(FS3L)
        r = d['RESULTADO']
        self.assertEqual(r['UNIDADE'], 'TUPLA (competidor, país, produto normalizado)')
        self.assertNotEqual(r['THREE_LAYER_CHAIN_PROVED_TUPLES'],
                            r['POR_UNIDADE_PRODUTO']['META_PRODUCTS_WITH_PROVED_THREE_LAYER_CHAIN'])


class TestExpertiseNoCaso(unittest.TestCase):
    """`IDENTITY_PROVED != ISSUE_EXPERTISE_PROVED`.

    A medicao anterior contou "2 especialistas em ES x OLIVE x REPILO" usando so o
    diretorio. O proprio artefato de identidade diz que a pessoa herda CROP e ISSUE da
    CONSULTA que a trouxe — herdar da consulta nao e expertise.
    """
    TERMOS_REPILO = ('repilo', 'venturia oleaginea', 'spilocaea oleagina',
                     'fusicladium oleagineum', 'peacock spot', 'olive scab')

    def _experts(self, case_id):
        return [o for o in fp.adaptar_expert_directory(fp.carregar(EXPERT))
                if o['FIELDS'].get('CASE_ID') == case_id]

    def test_es_olive_repilo_tem_identidade_mas_nao_expertise(self):
        corpus = fp.carregar(SCI)
        pessoas = self._experts('ES-OLIVE-REPILO')
        self.assertEqual(len(pessoas), 2, 'o diretorio tem duas pessoas neste recorte')
        for p in pessoas:
            r = fp.expertise_no_caso(p, corpus, 'OLIVE', 'REPILO', self.TERMOS_REPILO)
            self.assertEqual(r['COUNTRY_MATCH'], 'PROVED')
            self.assertEqual(r['CROP_EXPERTISE'], 'PROVED')
            self.assertEqual(r['ISSUE_BY_TITLE'], 0)
            self.assertEqual(r['ISSUE_EXPERTISE'], 'NOT_PROVED')
            self.assertEqual(r['CASE_LEVEL_EXPERTISE'], 'NOT_PROVED')

    def test_o_campo_issue_da_consulta_nao_promove(self):
        corpus = fp.carregar(SCI)
        pessoas = self._experts('ES-OLIVE-REPILO')
        por_consulta = sum(fp.expertise_no_caso(p, corpus, 'OLIVE', 'REPILO',
                                                self.TERMOS_REPILO)['ISSUE_BY_QUERY_FIELD']
                           for p in pessoas)
        self.assertGreater(por_consulta, 0, 'ha ISSUE=REPILO herdado da consulta')
        for p in pessoas:
            r = fp.expertise_no_caso(p, corpus, 'OLIVE', 'REPILO', self.TERMOS_REPILO)
            self.assertNotEqual(r['ISSUE_EXPERTISE'], 'PROVED')

    def test_ausencia_no_corpus_espanhol_e_not_measurable_e_nao_not_proved(self):
        corpus = fp.carregar(SCI)
        for case_id, crop, issue, termos in (
                ('IT-VINE-FLAVESCENCE', 'GRAPEVINE', 'FLAVESCENCE',
                 ('flavescence', 'scaphoideus')),):
            for p in self._experts(case_id):
                r = fp.expertise_no_caso(p, corpus, crop, issue, termos)
                self.assertEqual(r['WORKS_IN_CORPUS'], 0)
                self.assertEqual(r['ISSUE_EXPERTISE'], 'NOT_MEASURABLE')
                self.assertIn('NAO e ausencia de obra', r['WHY'])

    def test_a_regua_e_a_mesma_para_todos_os_recortes(self):
        corpus = fp.carregar(SCI)
        for p in self._experts('FR-CEREAL-SEPTORIA'):
            r = fp.expertise_no_caso(p, corpus, 'CEREALS', 'SEPTORIA',
                                     ('septoria', 'zymoseptoria'))
            self.assertNotEqual(r['ISSUE_EXPERTISE'], 'PROVED',
                                'se 1 REPILO nao promove Landa, 2 SEPTORIA nao promove aqui')


class TestDeepCorpus(unittest.TestCase):
    """`IDENTIDADE != CONTEUDO`. O Creator Map diz QUEM; o corpus diz o que o material mostra."""

    def test_unidade_propria(self):
        for o in fp.adaptar_creator_deep_corpus(fp.carregar(DEEP)):
            self.assertEqual(o['ANALYTICAL_UNIT'], 'CREATOR_CONTENT_PROFILE')

    def test_rotas_de_conteudo_medidas(self):
        objs = fp.adaptar_creator_deep_corpus(fp.carregar(DEEP))
        provadas = [o for o in objs if o['FIELDS']['CONTENT_ROUTE'] == 'PROVED']
        self.assertEqual(len(objs), 10)
        self.assertEqual(len(provadas), 9)
        self.assertEqual(len(objs) - len(provadas), 1)

    def test_issue_do_conteudo_e_classe_de_linha_nunca_problema_nomeado(self):
        objs = fp.adaptar_creator_deep_corpus(fp.carregar(DEEP))
        vistas = set()
        for o in objs:
            vistas.update((o['FIELDS']['ISSUES_OBSERVED_IN_CONTENT'] or {}).keys())
        self.assertTrue(vistas <= {'WEED', 'PEST', 'DISEASE'},
                        'o corpus nao classifica problema nomeado: %s' % vistas)
        for termo in ('REPILO', 'FLAVESCENCE', 'SEPTORIA'):
            self.assertNotIn(termo, vistas)

    def test_score_proibido_viaja_no_artefato(self):
        d = fp.carregar(DEEP)
        self.assertEqual(d['PROHIBITED_METRIC']['STATUS'], 'PROHIBITED_METRIC')
        self.assertEqual(d['PROHIBITED_METRIC']['NAME'], 'ADAMA_RELEVANCE_SCORE')

    def test_nao_observado_nao_e_ausencia(self):
        for o in fp.adaptar_creator_deep_corpus(fp.carregar(DEEP)):
            texto = ' '.join(o['GUARDRAILS'])
            self.assertIn('NOT_OBSERVED_IN_CORPUS != NO_RELATIONSHIP', texto)

    def test_identidade_e_conteudo_nao_se_juntam_por_engano(self):
        ident = [o for o in fp.adaptar_creator_capability(fp.carregar(CREATOR))
                 if o['ANALYTICAL_UNIT'] == 'PERSON']
        cont = fp.adaptar_creator_deep_corpus(fp.carregar(DEEP))
        with self.assertRaises(fp.UnidadeMisturada):
            fp.juntar(ident + cont, cont, por='COUNTRY')


if __name__ == '__main__':
    unittest.main()
