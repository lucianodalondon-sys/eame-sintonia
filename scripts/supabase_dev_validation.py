"""Gera a bateria de validacao que roda DENTRO do Postgres do DEV.

Nao ha credencial nesta maquina. Em vez de descrever o que deveria ser testado, este
script escreve o SQL que TESTA — e que se reprova sozinho. Quem tem acesso roda e
recebe um JSON com PASS/FAIL por verificacao.

Duas decisoes que importam:

1. Tudo roda dentro de UMA transacao que termina em ROLLBACK. O DEV sai como
   entrou: a validacao nao deixa lixo nem depende de limpeza manual.

2. As verificacoes NEGATIVAS sao as que valem. Contar tabela prova que o CREATE
   correu; so a linha RECUSADA prova que a lei pega. Cada uma tenta inserir algo
   proibido e registra PASS quando o banco recusa.

Uso:
    py scripts/supabase_dev_validation.py --sync
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-CANONICAL-SCHEMA.json')
SAIDA_SQL = os.path.join(RAIZ, 'supabase', 'validation', '0002_dev_validation.sql')
SAIDA_JSON = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-DEV-VALIDATION-PLAN.json')

# O alvo NAO esta escrito aqui, e isso e de proposito.
#
# Eu ja escrevi 'hvtycqsrdtmxxodwcwph' nesta linha uma vez. A branch foi medida no
# mesmo dia e reprovou: vazia de dado, suja de schema. Alvo fixo no codigo vira alvo
# errado no dia seguinte. Quem roda informa o REF, e a lista abaixo recusa os dois
# que ja foram medidos e reprovados.
DEV_REF = None
REFS_RECUSADOS = {
    'odhdwvugikjdvkapbowe': 'parent: 732 objetos em storage, 19 tabelas com dado',
    'hvtycqsrdtmxxodwcwph': 'branch develop: 51 tabelas herdadas e public.schema_migracao',
}

# ── fixture minima: o menor grafo que sustenta as verificacoes ──────────────
FIXTURE = """
  insert into source (source_id, source_name, source_role, access_state)
       values ('SRC-V', 'fonte de validacao', 'validacao', 'OPEN');
  insert into ontology_term (term_id, term_kind) values ('CROP-V', 'CROP'), ('ISSUE-V', 'ISSUE');
  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-FR', 'FR', 'Occitanie', 'NUTS2');
  insert into evidence (evidence_id, source_id, source_language, evidence_level)
       values ('EV-V', 'SRC-V', 'es', 'MEASURED');
  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-V', 'validacao', '0.1.0-draft', 'PENDING', false);
  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-V', 'lucianodalondon-sys/eame-sintonia',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'H2');
  insert into attention_object (attention_object_id, object_type, country, attention_state,
                                publish_run_id)
       values ('AO-ES-V', 'PHENOMENON_CASE', 'ES', 'FORMING', 'RUN-V'),
              ('AO-IT-V', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-V'),
              ('AO-FR-V', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-V');
  insert into attention_object_evidence (attention_object_id, evidence_id)
       values ('AO-ES-V', 'EV-V');
  insert into source_provenance (evidence_id, source_id) values ('EV-V', 'SRC-V');
  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id)
       values ('attention_object', 'AO-ES-V', 'GITHUB',
               'lucianodalondon-sys/eame-sintonia', 'data/x.json',
               'd7b289425c5e436f3ce68e367b8706e11910f43b', 'RUN-V');
  insert into field_pressure_series (series_id, country, source_id)
       values ('SER-V', 'ES', 'SRC-V');
  insert into convergence_proposition (proposition_id, attention_object_id,
                                       proposition_text, convergence_kind)
       values ('PROP-V', 'AO-ES-V', 'proposicao de validacao', 'PHENOMENON_CONVERGENCE');
  insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
                               source_id, independence_state)
       values ('LEG-V', 'PROP-V', 'TERRITORIAL', 'EV-V', 'SRC-V', 'INDEPENDENT');
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('AO-ES-V', 'OBJECT_TITLE', 'es', 'texto original em espanhol', 'EV-V');
"""

# ── verificacoes NEGATIVAS: cada uma DEVE ser recusada pelo banco ───────────
NEGATIVAS = [
    ('EXPIRY_NE_WITHDRAWAL',
     "prazo com expiry_is_withdrawal = true",
     """insert into organization (organization_id, name) values ('ORG-V', 'x');
        insert into product (product_id, normalized_name) values ('PRD-V', 'x');
        insert into registration (registration_id, country, registration_number,
                                  holder_organization_id, product_id, source_id)
             values ('REG-V', 'IT', '0001', 'ORG-V', 'PRD-V', 'SRC-V');
        insert into registration_deadline (deadline_id, registration_id, deadline_date,
             deadline_kind, status_as_declared_by_source, expiry_is_withdrawal,
             evidence_id, source_id)
             values ('DL-V', 'REG-V', '2027-03-31', 'EXPIRY', 'IN FORCE', true,
                     'EV-V', 'SRC-V');"""),

    ('PRAZO_NAO_AUTORIZA_BUSINESS_DECISION',
     "objeto de prazo com max_authorized_action = BUSINESS_DECISION",
     """insert into organization (organization_id, name) values ('ORG-W', 'x');
        insert into product (product_id, normalized_name) values ('PRD-W', 'x');
        insert into registration (registration_id, country, registration_number,
                                  holder_organization_id, product_id, source_id)
             values ('REG-W', 'IT', '0002', 'ORG-W', 'PRD-W', 'SRC-V');
        insert into regulatory_deadline_object (attention_object_id, registration_id,
             deadline_date, deadline_kind, status_as_declared_by_source,
             max_authorized_action)
             values ('AO-IT-V', 'REG-W', '2027-03-31', 'EXPIRY', 'IN FORCE',
                     'BUSINESS_DECISION');"""),

    ('MEDIA_EXIGE_N',
     "leitura de serie com n = 0",
     """insert into field_pressure_reading (reading_id, series_id, value, n, unit, source_id)
             values ('RD-V', 'SER-V', 12.5, 0, 'pct', 'SRC-V');"""),

    ('MEDIA_EXIGE_N_NAO_NULO',
     "leitura de serie com n nulo",
     """insert into field_pressure_reading (reading_id, series_id, value, n, unit, source_id)
             values ('RD-W', 'SER-V', 12.5, null, 'pct', 'SRC-V');"""),

    ('LOCALITY_TEXT_NAO_E_POINT',
     "localidade em texto carregando geometria",
     """insert into geo_anchor (geo_id, country, locality_text, geometry, geo_resolution,
                                geometry_source_id)
             values ('GEO-X', 'ES', 'cerca de Jaen', '{"type":"Point"}'::jsonb,
                     'LOCALITY_TEXT', 'SRC-V');"""),

    ('POINT_EXIGE_GEOMETRIA',
     "resolucao POINT sem geometria",
     """insert into geo_anchor (geo_id, country, geo_resolution)
             values ('GEO-Y', 'ES', 'POINT');"""),

    ('GEOMETRIA_EXIGE_ORIGEM',
     "geometria sem fonte declarada",
     """insert into geo_anchor (geo_id, country, geometry, geo_resolution)
             values ('GEO-Z', 'ES', '{"type":"Point"}'::jsonb, 'POINT');"""),

    ('DEPENDENTE_DECLARA_ALVO',
     "perna DEPENDENT sem tipo de dependencia e sem alvo",
     """insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
             source_id, independence_state)
             values ('LEG-W', 'PROP-V', 'FIELD_HISTORICAL', 'EV-V', 'SRC-V', 'DEPENDENT');"""),

    ('INDEPENDENTE_NAO_TEM_ALVO',
     "perna INDEPENDENT apontando para outra perna",
     """insert into convergence_leg (leg_id, proposition_id, signal_family, evidence_id,
             source_id, independence_state, depends_on_leg_id)
             values ('LEG-X', 'PROP-V', 'CREATOR', 'EV-V', 'SRC-V', 'INDEPENDENT', 'LEG-V');"""),

    ('SOURCE_LANGUAGE_VOCABULARIO_FECHADO',
     "lingua fora do vocabulario",
     """insert into evidence (evidence_id, source_id, source_language)
             values ('EV-X', 'SRC-V', 'de');"""),

    ('SOURCE_LANGUAGE_NAO_ACEITA_TRACO',
     "lingua igual a travessao",
     """insert into evidence (evidence_id, source_id, source_language)
             values ('EV-Y', 'SRC-V', '—');"""),

    ('EXPERTISE_PROVADA_EXIGE_EVIDENCIA',
     "expertise PROVED sem evidencia",
     """insert into person (person_id) values ('PER-V');
        insert into issue_expertise (person_id, crop_term_id, issue_term_id,
             issue_expertise_state)
             values ('PER-V', 'CROP-V', 'ISSUE-V', 'PROVED');"""),

    ('GDPR_ANTES_DA_IDENTIDADE',
     "observacao de pessoa identificada com GDPR nao iniciado",
     """insert into observation (observation_id, observation_kind, source_id, signal_family)
             values ('OBS-V', 'FIELD_VOICE_OBSERVATION', 'SRC-V', 'CREATOR');
        insert into field_voice_observation (observation_id, entity_kind, platform,
             gdpr_treatment_state)
             values ('OBS-V', 'PERSON_CREATOR', 'youtube', 'NOT_STARTED');"""),

    ('LATENCIA_SEM_MEDICAO_E_NULA',
     "latencia com valor sem estado PROVED",
     """insert into source_clock (source_id, source_status, pipeline_latency_state,
             pipeline_latency_seconds)
             values ('SRC-V', 'ABERTA', 'NOT_MEASURED', 0);"""),

    ('PUBLICADO_EXIGE_SOMBRA',
     "publish_run PUBLISHED sem sombra aprovada",
     """insert into publish_run (publish_run_id, pipeline_version, schema_version,
             status, shadow_validation_passed)
             values ('RUN-X', 'v', '0.1.0-draft', 'PUBLISHED', false);"""),

    ('BACKENDS_NAO_SE_MISTURAM',
     "proveniencia com repositorio E tabela ao mesmo tempo",
     """insert into storage_provenance (subject_kind, subject_id, source_backend,
             repository, path, commit_sha, db_schema, table_or_view, primary_key)
             values ('evidence', 'EV-V', 'GITHUB', 'r', 'p',
                     'd7b289425c5e436f3ce68e367b8706e11910f43b',
                     'sintonia', 'evidence', 'evidence_id');"""),

    ('GITHUB_EXIGE_COMMIT',
     "proveniencia GITHUB sem commit_sha",
     """insert into storage_provenance (subject_kind, subject_id, source_backend,
             repository, path)
             values ('evidence', 'EV-V', 'GITHUB', 'r', 'p');"""),

    ('PORTFOLIO_E_SEMPRE_CONTEXTO',
     "portfolio local marcado como evidencia",
     """insert into local_adama_portfolio_context (context_id, country, source_id,
             is_context_not_evidence)
             values ('CTX-V', 'ES', 'SRC-V', false);"""),

    ('OBJETO_NAO_SE_RELACIONA_CONSIGO',
     "objeto relacionado a si mesmo",
     """insert into object_relation (from_object_id, to_object_id, relation_kind)
             values ('AO-ES-V', 'AO-ES-V', 'MESMO');"""),

    ('MUDANCA_DE_ESTADO_EXIGE_ESTADO',
     "evento STATE_CHANGE sem estado depois",
     """insert into object_event (event_id, attention_object_id, event_type, what_changed)
             values ('EVT-V', 'AO-ES-V', 'STATE_CHANGE', 'mudou');"""),

    ('VAZIO_TEMPORAL_DECLARA_MOTIVO',
     "evento GAP sem motivo",
     """insert into object_event (event_id, attention_object_id, event_type, what_changed)
             values ('EVT-W', 'AO-ES-V', 'GAP', 'nada');"""),

    ('SEM_DATA_SEM_PRECISAO',
     "evento sem data com resolucao exata",
     """insert into object_event (event_id, attention_object_id, event_type,
             event_at_resolution, what_changed)
             values ('EVT-X', 'AO-ES-V', 'NEW_EVIDENCE', 'EXACT_DATE', 'x');"""),

    ('PERFIL_PERTENCE_A_UMA_ENTIDADE',
     "perfil de creator sem pessoa e sem negocio",
     """insert into creator_content_profile (profile_id, entity_kind, platform, source_id)
             values ('PRF-V', 'PERSON_CREATOR', 'youtube', 'SRC-V');"""),

    ('CONCORDANCIA_EXIGE_PORTAO',
     "cadeia com concordancia PROVED e portao NOT_RUN",
     """insert into organization (organization_id, name) values ('ORG-Z', 'x');
        insert into competitor_product_identity (identity_id, country,
             competitor_organization_id, agreement_state, urbole_guard_result)
             values ('CPI-V', 'ES', 'ORG-Z', 'PROVED', 'NOT_RUN');"""),

    ('PAR_PROVADO_EXIGE_PASSAGEM',
     "pareamento cultura x problema PROVED sem a passagem",
     """insert into phenomenon_case (attention_object_id, geo_id, crop_term_id,
             issue_term_id, crop_issue_pairing_state)
             values ('AO-ES-V', 'GEO-ES', 'CROP-V', 'ISSUE-V', 'PROVED');"""),

    ('OFFSETS_ANDAM_EM_PAR',
     "offset de passagem pela metade",
     """insert into evidence (evidence_id, source_id, passage_start)
             values ('EV-Z', 'SRC-V', 10);"""),

    ('TRADUCAO_NAO_E_NA_LINGUA_DE_ORIGEM',
     "traducao com lingua UNKNOWN",
     """insert into content_translation (canonical_entity_id, translation_language,
             translated_text, translation_provenance)
             values ('AO-ES-V', 'UNKNOWN', 'x', 'y');"""),
]

# ── verificacoes POSITIVAS: contam ou derivam ──────────────────────────────
POSITIVAS = [
    ('TABLES_ACTUAL', 57,
     "select count(*) from information_schema.tables "
     "where table_schema = 'sintonia' and table_type = 'BASE TABLE'"),
    ('VIEWS_ACTUAL', 13,
     "select count(*) from information_schema.views where table_schema = 'sintonia'"),
    ('RPCS_ACTUAL', 5,
     "select count(*) from pg_proc p join pg_namespace n on n.oid = p.pronamespace "
     "where n.nspname = 'sintonia'"),
    ('ENUMS_ACTUAL', 27,
     "select count(distinct t.typname) from pg_type t join pg_namespace n "
     "on n.oid = t.typnamespace where n.nspname = 'sintonia' and t.typtype = 'e'"),
    ('RLS_ENABLED_ALL', 57,
     "select count(*) from pg_class c join pg_namespace n on n.oid = c.relnamespace "
     "where n.nspname = 'sintonia' and c.relkind = 'r' and c.relrowsecurity"),
    ('PUBLISHER_POLICIES', 57,
     "select count(*) from pg_policies where schemaname = 'sintonia' "
     "and policyname = 'publisher_all'"),
    ('INDEXES_ON_FK', 86,
     "select count(*) from pg_indexes where schemaname = 'sintonia' "
     "and indexname like '%\\_idx'"),
    ('CONVERGENCE_SINGLE_SIGNAL', 'SINGLE_SIGNAL',
     "select convergence_state from v_convergence_state where proposition_id = 'PROP-V'"),
    ('READINESS_NOT_READY', 'false',
     "select coalesce(computed_is_ready, false)::text from v_attention_readiness "
     "where attention_object_id = 'AO-ES-V'"),
    ('COUNTRY_ISOLATION_ES', 1,
     "select count(*) from attention_object where country = 'ES'"),
    ('COUNTRY_ISOLATION_IT', 1,
     "select count(*) from attention_object where country = 'IT'"),
    ('COUNTRY_ISOLATION_FR', 1,
     "select count(*) from attention_object where country = 'FR'"),
    ('MULTILINGUAL_ONE_OBJECT', 1,
     "select count(distinct attention_object_id) from attention_object_representation "
     "where attention_object_id = 'AO-ES-V'"),
    ('MULTILINGUAL_FIVE_LANGUAGES', 5,
     "select count(*) from attention_object_representation "
     "where attention_object_id = 'AO-ES-V'"),
    ('ORIGINAL_PRESERVED', 'texto original em espanhol',
     "select original_text from content_entity where canonical_entity_id = 'AO-ES-V'"),
    ('PROVENANCE_REACHES_COMMIT', 'd7b289425c5e436f3ce68e367b8706e11910f43b',
     "select commit_sha from v_publish_provenance "
     "where attention_object_id = 'AO-ES-V' limit 1"),
    ('ALLOWED_COUNTRIES_DENIES_BY_DEFAULT', 0,
     "select coalesce(array_length(allowed_countries(), 1), 0)"),
]


def gerar_sql():
    L = [
        '-- VALIDACAO DO DEV — SINTONIA EAME',
        '--',
        '-- GERADO por scripts/supabase_dev_validation.py. Nao editar a mao.',
        '--',
        '-- ALVO: um DEV_PROJECT_REF LIMPO, que ainda nao existe.',
        '--',
        '-- REFS RECUSADOS, ambos medidos:'] + [
        '--   %s — %s' % (r, m) for r, m in sorted(REFS_RECUSADOS.items())] + [
        '--',
        '-- Rodar DEPOIS de aplicar supabase/migrations/0001_initial_canonical_schema.sql',
        '-- em um banco limpo de dado E de schema. As duas coisas.',
        '--',
        '-- Tudo acontece dentro de UMA transacao que termina em ROLLBACK: o banco sai',
        '-- como entrou. As verificacoes NEGATIVAS sao as que valem — contar tabela prova',
        '-- que o CREATE correu; so a linha RECUSADA prova que a lei pega.',
        '',
        'BEGIN;',
        'SET search_path TO sintonia, public;',
        '',
        'CREATE TEMP TABLE _resultado (ordem serial, nome text, tipo text,',
        '                             esperado text, encontrado text, veredito text) '
        'ON COMMIT DROP;',
        '',
        '-- fixture minima',
        'SAVEPOINT antes_da_fixture;',
        'DO $fx$ BEGIN', FIXTURE, 'END $fx$;',
        '',
        '-- representacoes em cinco idiomas: UM objeto, cinco linhas',
        "INSERT INTO attention_object_representation (attention_object_id, language, title)",
        "SELECT 'AO-ES-V', l, 'titulo em ' || l",
        "  FROM unnest(ARRAY['pt','en','es','fr','it']::language_code[]) AS l;",
        '',
        '-- ── NEGATIVAS: cada uma DEVE ser recusada ──────────────────────────',
    ]
    for nome, descricao, sql in NEGATIVAS:
        corpo = '\n'.join('    ' + l.strip() for l in sql.strip().split('\n'))
        L += [
            '',
            '-- %s · %s' % (nome, descricao),
            'DO $n$ BEGIN',
            '  BEGIN',
            corpo,
            "    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)",
            "    VALUES ('%s', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL');" % nome,
            '  EXCEPTION WHEN others THEN',
            "    INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)",
            "    VALUES ('%s', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS');" % nome,
            '  END;',
            '  ROLLBACK TO SAVEPOINT antes_da_fixture;',
            '  -- refazer a fixture: o rollback do teste desfez tudo',
            'END $n$;',
            'DO $rf$ BEGIN', FIXTURE, 'END $rf$;',
        ]

    L += ['', '-- ── POSITIVAS: contagem e derivacao ────────────────────────────────']
    for nome, esperado, sql in POSITIVAS:
        L += [
            "INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)",
            "SELECT '%s', 'POSITIVA', '%s', v::text," % (nome, esperado),
            "       CASE WHEN v::text = '%s' THEN 'PASS' ELSE 'FAIL' END" % esperado,
            "  FROM (%s) s(v);" % sql,
        ]

    L += [
        '',
        '-- ── RESULTADO ──────────────────────────────────────────────────────',
        'SELECT jsonb_pretty(jsonb_build_object(',
        "  'DEV_PROJECT_REF', current_setting('sintonia.dev_ref', true),",
        "  'TOTAL', (select count(*) from _resultado),",
        "  'PASS', (select count(*) from _resultado where veredito = 'PASS'),",
        "  'FAIL', (select count(*) from _resultado where veredito = 'FAIL'),",
        "  'FALHAS', (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb)",
        "             from (select nome, tipo, esperado, encontrado from _resultado",
        "                   where veredito = 'FAIL' order by ordem) t),",
        "  'TUDO', (select jsonb_agg(to_jsonb(t) order by t.ordem)",
        "           from (select * from _resultado) t)",
        ')) AS validacao;',
        '',
        '-- O banco sai como entrou.',
        'ROLLBACK;',
        '',
    ]
    return '\n'.join(L)


def medir():
    with open(SCHEMA, encoding='utf-8') as fh:
        d = json.load(fh)
    return {
        'SOURCE_ID': 'SUPABASE-DEV-VALIDATION-PLAN-EAME-2026-08-31',
        'source': 'Bateria de validacao do DEV, escrita para rodar dentro do Postgres.',
        'DEV_PROJECT_REF': DEV_REF,
        'REFS_RECUSADOS': REFS_RECUSADOS,
        'EXECUTADA': False,
        'POR_QUE_NAO': ('duas razoes, e a segunda e a que manda agora: nao ha credencial '
                        'nesta maquina, e nao ha banco limpo para rodar. O SQL roda '
                        'sozinho e se reprova sozinho quando o alvo existir.'),
        'ORDEM': ['supabase/inventory/0000_readonly_inventory.sql (no DEV novo, antes de tudo)',
                  'supabase/migrations/0001_initial_canonical_schema.sql',
                  'supabase/validation/0002_dev_validation.sql'],
        'VERIFICACOES_NEGATIVAS': len(NEGATIVAS),
        'VERIFICACOES_POSITIVAS': len(POSITIVAS),
        'TOTAL': len(NEGATIVAS) + len(POSITIVAS),
        'NEGATIVAS': [{'NOME': n, 'TENTA': d2} for n, d2, _ in NEGATIVAS],
        'POSITIVAS': [{'NOME': n, 'ESPERADO': str(e)} for n, e, _ in POSITIVAS],
        'TRANSACAO': 'BEGIN ... ROLLBACK — o DEV sai como entrou',
        'ESPERADO_DO_SCHEMA': {'TABLES': len(d['TABLES']), 'VIEWS': len(d['VIEWS']),
                               'RPCS': len(d['RPCS']) + 1, 'ENUMS': len(d['VOCABULARIES']),
                               'INDEXES': len(d['INDEXES']['LISTA'])},
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    if '--sync' in sys.argv:
        os.makedirs(os.path.dirname(SAIDA_SQL), exist_ok=True)
        with open(SAIDA_SQL, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(gerar_sql())
        with open(SAIDA_JSON, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('SQL em', os.path.relpath(SAIDA_SQL, RAIZ))
        print('plano em', os.path.relpath(SAIDA_JSON, RAIZ))
    print(json.dumps({k: v for k, v in m.items()
                      if k not in ('NEGATIVAS', 'POSITIVAS')},
                     ensure_ascii=False, indent=2))
