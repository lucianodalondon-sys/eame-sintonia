# -*- coding: utf-8 -*-
"""Provas da preparacao para a primeira carga sombra.

⚠️ UMA DISTINCAO QUE ATRAVESSA O ARQUIVO INTEIRO

Nao existe instancia de banco nesta rodada: sem URL, sem chave, sem CLI, sem psql,
sem Docker. Logo:

  - as provas `DB_CONSTRAINT_*` verificam que a restricao EXISTE no SQL gerado.
    Isso NAO e o mesmo que o banco ter recusado a linha. Verificar texto de SQL
    prova que a lei foi escrita; so a execucao prova que ela pega.

  - as provas de isolamento, multilingue e proveniencia rodam sobre FIXTURE.
    Provam a LOGICA, nao um banco.

Chamar qualquer uma dessas de "testada no banco" seria mentira, e o produto
inteiro existe para nao fazer isso.

Zero rede.
"""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from supabase_schema import carregar, gerar  # noqa: E402
from supabase_migration_review import revisar  # noqa: E402
from supabase_publisher_dryrun import medir as dryrun  # noqa: E402
from supabase_shadow_validator import (  # noqa: E402
    DIMENSOES, FIXTURE_FREEZE, FIXTURE_BANCO_PROMOVIDO, medir as shadow, validar,
)
from h2_resolve_commit import medir as h2medir  # noqa: E402

SUP = os.path.join(ROOT, 'data', 'supabase')
MIGRATION = os.path.join(ROOT, 'supabase', 'migrations',
                         '0001_initial_canonical_schema.sql')

D = carregar()
SQL = gerar(D)
with open(MIGRATION, encoding='utf-8') as f:
    SQL_DISCO = f.read()


def jl(nome):
    with open(os.path.join(SUP, nome), encoding='utf-8') as f:
        return json.load(f)


H2 = jl('H2-COMMIT-RESOLUTION.json')
MAPA = jl('SUPABASE-PUBLISH-MAP.json')
REVIEW = jl('SUPABASE-MIGRATION-REVIEW.json')
DRY = jl('SUPABASE-PUBLISHER-DRYRUN.json')
SHADOW = jl('SUPABASE-SHADOW-VALIDATION-RUN.json')


class TestH2(unittest.TestCase):

    def test_H2_FIXED_COMMIT_PROVENANCE(self):
        self.assertEqual(H2['STATUS'], 'RESOLVED')
        self.assertEqual(H2['H2_PROVENANCE_MUTABLE_REF'], 'NO')
        sha = H2['RESOLVED_COMMIT_SHA']
        self.assertEqual(len(sha), 40)
        self.assertEqual(sha, 'd7b289425c5e436f3ce68e367b8706e11910f43b')
        p = H2['PAYLOAD_DECLARADO']
        self.assertEqual(p['VERSOES_NA_BRANCH'], 1)
        self.assertTrue(p['HEAD_IDENTICO_AO_COMMIT'])
        self.assertTrue(H2['ALCANCAVEL_DA_BRANCH_DE_TRABALHO'])

    def test_o_sha_foi_resolvido_e_nao_escolhido(self):
        """Uma versao so: nao houve escolha a fazer."""
        self.assertIn('Nao houve escolha entre versoes', H2['COMO_FOI_RESOLVIDO'])
        vivo = h2medir()
        self.assertEqual(vivo['RESOLVED_COMMIT_SHA'], H2['RESOLVED_COMMIT_SHA'])

    def test_o_subinput_de_rotulos_nao_foi_escolhido_por_conveniencia(self):
        sub = H2['ARTEFATOS_SECUNDARIOS'][0]
        self.assertEqual(sub['STATUS'], 'FAIL_CLOSED')
        self.assertEqual(len(sub['COMMITS']), 3)
        h2 = next(i for i in MAPA['INPUTS'] if i['HOSE_ID'] == 'H2')
        self.assertEqual(h2['SUB_INPUT_NAO_FIXADO']['STATUS'], 'NOT_PINNED')

    def test_nenhuma_entrada_do_mapa_usa_branch(self):
        for i in MAPA['INPUTS']:
            for campo in ('SOURCE_COMMIT', 'HANDOFF_COMMIT', 'FREEZE_COMMIT'):
                v = i.get(campo)
                for sha in ([v] if isinstance(v, str) else (v or [])):
                    self.assertNotIn('origin/', sha, '%s.%s' % (i['HOSE_ID'], campo))
                    self.assertEqual(len(sha), 40, '%s.%s = %s' % (i['HOSE_ID'], campo, sha))


class TestMigration(unittest.TestCase):

    def test_SCHEMA_JSON_GENERATES_SQL(self):
        self.assertEqual(SQL_DISCO, SQL, 'a migration divergiu do JSON canonico')
        self.assertIn('NAO EDITAR A MAO', SQL_DISCO)

    def test_MIGRATION_REVIEW_PASS(self):
        self.assertEqual(REVIEW['MIGRATION_REVIEW'], 'PASS')
        self.assertEqual(REVIEW['ACHADOS'], [])
        vivo = revisar()
        self.assertEqual(vivo['MIGRATION_REVIEW'], 'PASS', vivo['ACHADOS'])

    def test_contagens_batem_com_o_json(self):
        for chave, v in REVIEW['CONTAGENS'].items():
            self.assertEqual(v['SQL'], v['JSON'], chave)
        self.assertEqual(REVIEW['CONTAGENS']['TABLES']['SQL'], 57)
        self.assertEqual(REVIEW['CONTAGENS']['VIEWS']['SQL'], 13)
        self.assertEqual(REVIEW['CONTAGENS']['ENUMS']['SQL'], 27)

    def test_chave_estrangeira_tem_indice_e_on_delete(self):
        fks = [(t['name'], c) for t in D['TABLES'] for c in t['columns'] if c.get('fk')]
        self.assertTrue(fks)
        for tab, c in fks:
            self.assertIn(c.get('on_delete'), ('CASCADE', 'RESTRICT', 'SET NULL'),
                          '%s.%s sem ON DELETE' % (tab, c['name']))
        self.assertGreater(len(D['INDEXES']['LISTA']), 80)
        for i in D['INDEXES']['LISTA']:
            self.assertIn('CREATE INDEX %s ON %s (%s);' % (i['name'], i['table'], i['column']),
                          SQL)

    def test_evidencia_e_fonte_nao_caem_por_cascade(self):
        """Historia nao se apaga por baixo de quem a cita."""
        for t in D['TABLES']:
            for c in t['columns']:
                if c.get('fk', '').split('.')[0] in ('evidence', 'source', 'source_snapshot',
                                                     'publish_run', 'observation',
                                                     'ontology_term', 'content_entity'):
                    self.assertEqual(c['on_delete'], 'RESTRICT',
                                     '%s.%s' % (t['name'], c['name']))


class TestAmbiente(unittest.TestCase):

    def test_DEV_TARGET_NOT_PRODUCTION(self):
        """Nao ha instancia nenhuma — logo nao ha como apontar para producao."""
        for var in ('SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_ROLE_KEY',
                    'SUPABASE_DB_URL', 'DATABASE_URL'):
            self.assertIsNone(os.environ.get(var), '%s definida' % var)
        for p in ('supabase/config.toml', '.env', '.env.local'):
            self.assertFalse(os.path.exists(os.path.join(ROOT, p)), p)
        self.assertEqual(D['MODE']['MIGRATION_APPLIED'], 'NO')
        self.assertEqual(D['MODE']['REAL_DATA_PUBLISHED'], 'NO')
        self.assertEqual(D['MODE']['V8_WIRED'], 'NO')

    def test_NO_FRONTEND_SERVICE_ROLE(self):
        seg = D['PROVENANCE_ENVELOPE']['SECURITY']
        self.assertIn('SERVICE_ROLE_KEY', seg['NEVER_IN_FRONTEND'])
        self.assertIn('SERVICE_ROLE_KEY nunca vai para o frontend', SQL)
        # nenhum VALOR de credencial no SQL — a palavra aparece so na proibicao
        self.assertEqual(re.findall(r'eyJ[A-Za-z0-9_-]{20,}', SQL), [])
        self.assertEqual(
            re.findall(r'(?:SERVICE_ROLE_KEY|apikey)\s*[:=]\s*[\'"][^\'"]{8,}', SQL), [])
        self.assertIn('SECURITY INVOKER', SQL)
        self.assertNotIn('SECURITY DEFINER', SQL)


class TestRestricoesNoSQL(unittest.TestCase):
    """Verificam que a lei ESTA ESCRITA no SQL. Nao provam execucao."""

    def test_DB_CONSTRAINT_EXPIRY_NE_BUSINESS_DECISION(self):
        self.assertIn("CONSTRAINT registration_deadline_expiry_nao_e_withdrawal "
                      "CHECK (expiry_is_withdrawal = false)", SQL)
        self.assertIn("CONSTRAINT regulatory_deadline_object_prazo_nao_autoriza_"
                      "decisao_de_negocio CHECK (max_authorized_action <> "
                      "'BUSINESS_DECISION')", SQL)

    def test_DB_CONSTRAINT_MEAN_REQUIRES_N(self):
        self.assertIn('CONSTRAINT field_pressure_reading_n_positivo CHECK (n > 0)', SQL)
        col = next(c for t in D['TABLES'] if t['name'] == 'field_pressure_reading'
                   for c in t['columns'] if c['name'] == 'n')
        self.assertIs(col['null'], False)

    def test_DB_CONSTRAINT_LOCALITY_TEXT_NE_POINT(self):
        self.assertIn("CONSTRAINT geo_anchor_locality_text_nao_e_point CHECK "
                      "((geo_resolution <> 'LOCALITY_TEXT') OR (geometry IS NULL))", SQL)
        self.assertIn("CONSTRAINT geo_anchor_point_exige_geometria", SQL)

    def test_DB_CONSTRAINT_DEPENDENT_NE_INDEPENDENT(self):
        self.assertIn('CONSTRAINT convergence_leg_dependente_declara_o_tipo_e_o_alvo', SQL)
        self.assertIn('CONSTRAINT convergence_leg_independente_nao_tem_alvo', SQL)

    def test_DB_SOURCE_LANGUAGE_CLOSED_VOCABULARY(self):
        self.assertIn("CREATE TYPE language_code AS ENUM ('pt', 'en', 'es', 'fr', 'it', "
                      "'MULTILINGUAL', 'UNKNOWN');", SQL)
        for tab, col in (('evidence', 'source_language'),
                         ('content_entity', 'source_language'),
                         ('scientific_publication', 'source_language')):
            c = next(c for t in D['TABLES'] if t['name'] == tab
                     for c in t['columns'] if c['name'] == col)
            self.assertEqual(c['type'], 'language_code')
        # O travessao existe no SQL — em comentario e no rotulo de transicao da
        # timeline, onde e apresentacao. A regra e que ele nunca seja VALOR DE
        # LINGUA: proibi-lo no arquivo inteiro confundiria os dois usos.
        self.assertNotIn('—', D['VOCABULARIES']['language_code'])
        for c in D['VOCABULARIES']['language_code']:
            self.assertRegex(c, r'^[a-zA-Z_]+$')

    def test_a_verificacao_e_de_texto_e_isso_esta_declarado(self):
        self.assertIn('NAO existe instancia', __doc__.replace('nao', 'NAO').upper()
                      .replace('NÃO', 'NAO')) if False else None
        self.assertIn('Nao existe instancia', __doc__)


class TestViewsERpcs(unittest.TestCase):

    def test_VIEWS_IMPLEMENTED(self):
        self.assertEqual(len(D['VIEWS']), 13)
        for v in D['VIEWS']:
            self.assertTrue(v.get('body'), 'view %s sem corpo' % v['name'])
            self.assertIn('CREATE OR REPLACE VIEW %s AS' % v['name'], SQL)
            self.assertIn('SELECT', v['body'])

    def test_view_nao_esconde_ausencia_com_join_interno(self):
        """Onde pode faltar linha, o join e LEFT."""
        for nome in ('v_attention_feed', 'v_radar', 'v_object_detail',
                     'v_evidence_drawer', 'v_crop_map_point', 'v_action_map',
                     'v_publish_provenance', 'v_source_status'):
            v = next(x for x in D['VIEWS'] if x['name'] == nome)
            self.assertIn('LEFT JOIN', v['body'], nome)

    def test_a_contagem_de_convergencia_e_derivada_na_view(self):
        v = next(x for x in D['VIEWS'] if x['name'] == 'v_convergence_state')
        self.assertIn("count(DISTINCT l.signal_family)", v['body'])
        self.assertIn("FILTER (WHERE l.independence_state = 'INDEPENDENT')", v['body'])
        cols = [c['name'] for t in D['TABLES'] if t['name'] == 'convergence_proposition'
                for c in t['columns']]
        self.assertNotIn('independent_family_count', cols)

    def test_a_defensibilidade_da_acao_e_derivada_contando_linhas(self):
        v = next(x for x in D['VIEWS'] if x['name'] == 'v_action_map')
        self.assertIn("a.action_type <> 'BUSINESS_DECISION'", v['body'])
        self.assertIn('count(ae.evidence_id) > 0', v['body'])

    def test_o_mapa_so_desenha_ponto_com_resolucao_provada(self):
        v = next(x for x in D['VIEWS'] if x['name'] == 'v_crop_map_point')
        self.assertIn("g.geo_resolution = 'POINT' AND g.geometry IS NOT NULL", v['body'])
        self.assertIn('undrawable_reason', v['body'])

    def test_o_especialista_passa_pelo_portao_na_view(self):
        v = next(x for x in D['VIEWS'] if x['name'] == 'v_issue_expert')
        self.assertIn("ie.issue_expertise_state = 'PROVED'", v['body'])
        self.assertNotIn('ORDER BY', v['body'].upper())

    def test_RPCS_IMPLEMENTED(self):
        self.assertEqual(len(D['RPCS']), 4)
        for r in D['RPCS']:
            self.assertTrue(r.get('body'), 'rpc %s sem corpo' % r['name'])
            self.assertIn('CREATE OR REPLACE FUNCTION %s(' % r['name'], SQL)
        self.assertIn('SECURITY INVOKER', SQL)

    def test_o_fallback_de_idioma_e_declarado_e_nao_fingido(self):
        r = next(x for x in D['RPCS'] if x['name'] == 'resolve_representation')
        self.assertIn("ARRAY[p_requested_language, 'en', 'pt']", r['body'])
        self.assertIn("'NO_REPRESENTATION_AVAILABLE'", r['body'])
        self.assertIn('fallback_used', r['returns_sql'])
        self.assertIn('requested_language', r['returns_sql'])

    def test_a_fila_vazia_devolve_o_motivo(self):
        r = next(x for x in D['RPCS'] if x['name'] == 'get_attention_feed')
        self.assertIn('NO_OBJECT_PASSED_ALL_GATES', r['body'])
        self.assertIn('empty_reason', r['returns_sql'])

    def test_a_evidencia_nao_sofre_fallback(self):
        r = next(x for x in D['RPCS'] if x['name'] == 'get_evidence')
        self.assertIn('ORIGINAL_TEXT nunca sofre fallback', r['body'])
        self.assertIn('NO_TRANSLATION_ORIGINAL_ONLY', r['body'])


class TestRLS(unittest.TestCase):

    def test_rls_ligado_e_publisher_unico_escritor(self):
        for t in D['TABLES']:
            self.assertIn('ALTER TABLE %s ENABLE ROW LEVEL SECURITY;' % t['name'], SQL)
            self.assertIn('CREATE POLICY publisher_all ON %s FOR ALL TO publisher_role'
                          % t['name'], SQL)

    def test_COUNTRY_ISOLATION_ES_IT_FR(self):
        com_pais = [t['name'] for t in D['TABLES']
                    if any(c['name'] == 'country' for c in t['columns'])]
        self.assertGreater(len(com_pais), 8)
        for nome in com_pais:
            self.assertIn('CREATE POLICY portal_read_country ON %s FOR SELECT TO '
                          'portal_reader USING (country = ANY (allowed_countries()));'
                          % nome, SQL)
        iso = SHADOW['ISOLAMENTO_POR_PAIS']
        self.assertTrue(iso['ISOLADO'])
        self.assertEqual(iso['VAZAMENTO'], {})
        for pais in ('ES_ONLY', 'IT_ONLY', 'FR_ONLY'):
            self.assertEqual(len(iso[pais]), 1, pais)

    def test_o_portal_so_escreve_telemetria(self):
        self.assertIn('CREATE POLICY portal_write_telemetry ON entry_path_event FOR '
                      'INSERT TO portal_reader', SQL)
        escritas = re.findall(r'CREATE POLICY \w+ ON (\w+) FOR (INSERT|UPDATE|DELETE) '
                              r'TO portal_reader', SQL)
        self.assertEqual(escritas, [('entry_path_event', 'INSERT')])

    def test_o_que_depende_de_decisao_de_autenticacao_esta_separado(self):
        rls = D['RLS']
        self.assertTrue(rls['BLOQUEADO_POR_DECISAO_DE_AUTENTICACAO'])
        self.assertIn('deny by default', rls['HELPER']['sql'].lower().replace('_', ' ')
                      if 'deny by default' in rls['HELPER']['sql'].lower() else
                      'Deny by default')
        self.assertIn('ARRAY[]::char(2)[]', rls['HELPER']['sql'])


class TestPublisherDryRun(unittest.TestCase):

    def test_PUBLISHER_DRY_RUN_IDEMPOTENT(self):
        i = DRY['IDEMPOTENCIA']
        self.assertTrue(i['DUAS_PASSAGENS_IDENTICAS'])
        self.assertEqual(i['NOVAS_ENTIDADES_NA_SEGUNDA'], 0)
        self.assertTrue(i['SEM_CHAVE_DUPLICADA'])
        self.assertEqual(i['CHAVES_PASSAGEM_1'], i['CHAVES_PASSAGEM_2'])
        self.assertGreater(i['CHAVES_PASSAGEM_1'], 0)

    def test_a_chave_natural_nao_usa_titulo(self):
        self.assertIn('Titulo traduzido nunca entra', DRY['IDEMPOTENCIA']['COMO'])
        self.assertIn('titulo traduzido', MAPA['IDEMPOTENCIA']['PROIBIDO'])

    def test_nada_foi_gravado(self):
        self.assertEqual(DRY['MODE']['COMMIT'], 'NO')
        self.assertEqual(DRY['MODE']['DB_CONNECTION'], 'NONE')
        self.assertEqual(DRY['MODE']['REAL_DATA_PUBLISHED'], 'NO')

    def test_o_dryrun_roda_de_novo_e_da_o_mesmo(self):
        vivo = dryrun()
        self.assertEqual(vivo['IDEMPOTENCIA']['CHAVES_PASSAGEM_1'],
                         DRY['IDEMPOTENCIA']['CHAVES_PASSAGEM_1'])

    def test_nenhuma_contagem_declarada_ficou_sem_lastro(self):
        self.assertEqual(DRY['DIVERGENCIAS_DECLARADO_x_MEDIDO'], [])

    def test_o_que_nao_resolveu_esta_declarado_e_nao_chutado(self):
        self.assertEqual(DRY['INPUTS_NOT_RESOLVED'], ['H3'])
        h3 = next(i for i in MAPA['INPUTS'] if i['HOSE_ID'] == 'H3')
        self.assertEqual(h3['INPUT_ARTIFACT'], 'NOT_RESOLVED')
        self.assertIn('inventar proveniencia', h3['NOTA_DO_ARTEFATO'])

    def test_os_numeros_sem_lastro_viraram_NOT_MEASURED(self):
        h8 = next(i for i in MAPA['INPUTS'] if i['HOSE_ID'] == 'H8')
        self.assertEqual(h8['EXPECTED_ENTITY_COUNT']['company_local_account'],
                         'NOT_MEASURED')
        self.assertIn('Eu tinha escrito 22 contas', h8['CORRECAO'])
        self.assertEqual(h8['MEASURED_NOS_BLOBS_FIXADOS']['CONTAS-V1.json::ACCOUNTS'], 44)


class TestShadowValidator(unittest.TestCase):

    def test_SHADOW_VALIDATOR_IDS_NOT_ONLY_COUNTS(self):
        caso = SHADOW['CASO_OBJETO_PROMOVIDO']
        self.assertTrue(caso['CONTAGEM_ERA_IGUAL'])
        self.assertEqual(caso['PUBLISH'], 'FAIL_CLOSED')
        self.assertIn('attention_object', caso['FAMILIES_FAILED'])
        dims = {m['DIMENSION'] for m in caso['O_QUE_PEGOU']}
        self.assertIn('states', dims)

    def test_o_validador_compara_as_catorze_dimensoes(self):
        self.assertEqual(len(DIMENSOES), 14)
        for d in ('ids', 'states', 'dates', 'evidence_ids', 'source_ids', 'relations',
                  'dependency_types', 'actions', 'translations', 'provenance'):
            self.assertIn(d, SHADOW['DIMENSOES_COMPARADAS'])

    def test_banco_fiel_passa(self):
        self.assertEqual(SHADOW['CASO_BANCO_FIEL']['PUBLISH'], 'OK')

    def test_qualquer_mismatch_fecha(self):
        r = validar(FIXTURE_FREEZE, FIXTURE_BANCO_PROMOVIDO)
        self.assertEqual(r['PUBLISH'], 'FAIL_CLOSED')
        self.assertIn('fecha a publicacao inteira', r['REGRA'])

    def test_o_limite_esta_declarado(self):
        self.assertEqual(SHADOW['MODE']['PROVA_UM_BANCO_REAL'], 'NAO')
        self.assertIn('nao ha instancia', SHADOW['LIMITE_DESTA_RODADA'])


class TestMultilingueEProveniencia(unittest.TestCase):

    def test_ONE_OBJECT_MULTI_LANGUAGE_DB(self):
        m = SHADOW['MULTILINGUE']
        self.assertTrue(m['UM_OBJETO_VARIAS_REPRESENTACOES'])
        self.assertTrue(m['NENHUM_OBJETO_POR_IDIOMA'])
        self.assertEqual(len(m['OBJETOS_DISTINTOS']), 1)
        self.assertEqual(sorted(m['IDIOMAS']), ['en', 'es', 'fr', 'it', 'pt'])
        # e o schema torna a duplicacao impossivel: o objeto nao tem coluna de idioma
        cols = [c['name'] for t in D['TABLES'] if t['name'] == 'attention_object'
                for c in t['columns']]
        for proibida in ('language', 'lang', 'locale'):
            self.assertNotIn(proibida, cols)

    def test_ORIGINAL_NE_TRANSLATION_DB(self):
        orig = [c['name'] for t in D['TABLES'] if t['name'] == 'content_entity'
                for c in t['columns']]
        trad = [c['name'] for t in D['TABLES'] if t['name'] == 'content_translation'
                for c in t['columns']]
        self.assertIn('original_text', orig)
        self.assertNotIn('original_text', trad)
        self.assertIn('translated_text', trad)
        self.assertNotIn('translated_text', orig)
        self.assertIn('translation_provenance', trad)
        self.assertIn('source_text_hash', trad)
        self.assertIn('CREATE TABLE content_translation', SQL)

    def test_PROVENANCE_END_TO_END(self):
        p = SHADOW['PROVENIENCIA_PONTA_A_PONTA']
        self.assertTrue(p['RESPONDE_QUAL_COMMIT_PRODUZIU'])
        self.assertTrue(p['RESPONDE_QUAL_FONTE_SUSTENTA'])
        self.assertEqual(p['ELOS'], 8)
        self.assertEqual(p['VIEW_QUE_FAZ_ISSO'], 'v_publish_provenance')
        v = next(x for x in D['VIEWS'] if x['name'] == 'v_publish_provenance')
        self.assertIn('publish_run_freeze', v['reads'])
        self.assertIn('commit_sha', v['body'])
        self.assertIn('d7b289425c5e436f3ce68e367b8706e11910f43b', str(p['CADEIA']))


if __name__ == '__main__':
    unittest.main()
