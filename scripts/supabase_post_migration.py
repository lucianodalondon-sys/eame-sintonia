"""Medicao do banco DEV DEPOIS que a migration correr. Nada aqui e opiniao.

O QUE ESTE ARQUIVO NAO E
------------------------
Nao e o 0002. O 0002 pergunta "a lei pega?" — ele tenta inserir linha proibida e
exige a recusa. Este pergunta outra coisa: "o que existe la dentro, medido no
catalogo do Postgres, e igual ao que a autoridade prometeu?".

Contar `CREATE TABLE` no texto do .sql prova que eu escrevi 57 vezes a palavra
CREATE. So `pg_class` prova que existem 57 tabelas. As duas contagens ja bateram
uma vez e ainda assim nao era a mesma pergunta.

O QUE ELE MEDE DE NOVO
----------------------
1. estrutura pelo catalogo: tabelas, views, RPCs, RLS ligado, politicas
2. isolamento por pais EXERCITADO — trocando de papel de verdade, com
   SET ROLE portal_reader, e olhando o que sobra visivel
3. multilingue: um objeto, varias representacoes, texto original intacto,
   traducao em tabela separada
4. proveniencia elo a elo: ATTENTION_OBJECT -> EVIDENCE -> SOURCE -> SNAPSHOT
   -> PUBLISH_RUN -> GITHUB_FREEZE_COMMIT, cada elo contado sozinho

O ACHADO QUE ESTE ARQUIVO CARREGA E NAO ESCONDE
-----------------------------------------------
A migration cria os papeis e as politicas, e NAO da GRANT. Politica e permissao
de LINHA; GRANT e permissao de TABELA. Faltando o GRANT, portal_reader nao le
nada — nem o pais dele. Hoje isso e seguro (nega tudo) e e incompleto (o
isolamento por pais nao esta provado em producao, esta desligado).

Este script mede as duas coisas separadas, e nao conserta nenhuma:
  · GRANT_PRESENTE_NA_MIGRATION  — o estado de hoje, medido, esperado NO
  · COUNTRY_ISOLATION_*          — a policy funciona QUANDO o GRANT existir,
                                   provado dando o GRANT dentro da transacao
                                   que termina em ROLLBACK

Corrigir isso e mexer em data/supabase/SUPABASE-CANONICAL-SCHEMA.json e regerar
a migration. Nao e trabalho deste arquivo, e nao foi feito.

Uso:
    py scripts/supabase_post_migration.py            # imprime o plano
    py scripts/supabase_post_migration.py --sync     # grava o .sql
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTORIDADE = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-CANONICAL-SCHEMA.json')
SAIDA_SQL = os.path.join(RAIZ, 'supabase', 'validation',
                         '0003_post_migration_checks.sql')
SAIDA_JSON = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-POST-MIGRATION-PLAN.json')

DEV_PROJECT_REF = 'xhqebdweltytnghiavew'
REFS_RECUSADOS = {
    'odhdwvugikjdvkapbowe': 'parent: 732 objetos em storage, 19 tabelas com dado',
    'hvtycqsrdtmxxodwcwph': 'branch develop: 51 tabelas herdadas e public.schema_migracao',
}

# O commit congelado do H2. Nao e enfeite: e o elo final da cadeia de
# proveniencia, e o teste exige que a consulta chegue ate ele.
H2_COMMIT = 'd7b289425c5e436f3ce68e367b8706e11910f43b'
REPOSITORIO = 'lucianodalondon-sys/eame-sintonia'


def esperado_da_autoridade():
    """As contagens vem do JSON, nunca do .sql e nunca da minha memoria."""
    with open(AUTORIDADE, encoding='utf-8') as fh:
        d = json.load(fh)
    return {
        'TABLES': len(d['TABLES']),
        'VIEWS': len(d['VIEWS']),
        'RPCS': len(d['RPCS']),
        'DB_SCHEMA': d['DB_SCHEMA'],
    }


# ── fixture ──────────────────────────────────────────────────────────────────
# Tres paises porque o isolamento so se prova com mais de um: ver ES nao prova
# nada se ES for a unica linha que existe.
FIXTURE = """
DO $fx$ BEGIN

  insert into source (source_id, source_name, source_role, country, access_state)
       values ('SRC-P', 'boletim fitosanitario', 'registro oficial', 'ES', 'OPEN');

  insert into source_snapshot (snapshot_id, source_id, captured_at, content_hash,
                               artifact_ref, artifact_language)
       values ('SNAP-P', 'SRC-P', timestamptz '2026-08-30 10:00:00+00',
               'hash-do-artefato', 's3://snap/p.html', 'es');

  insert into geo_anchor (geo_id, country, region, geo_resolution)
       values ('GEO-P-ES', 'ES', 'Andalucia', 'NUTS2'),
              ('GEO-P-IT', 'IT', 'Veneto', 'NUTS2'),
              ('GEO-P-FR', 'FR', 'Occitanie', 'NUTS2');

  -- ORIGINAL_TEXT na lingua da fonte, sem edicao. Este texto e o que os testes
  -- de preservacao vao procurar byte a byte.
  insert into evidence (evidence_id, source_id, snapshot_id, source_location_country,
                        fact_location_geo_id, source_language, evidence_level,
                        original_text, source_published_at, captured_at)
       values ('EV-P', 'SRC-P', 'SNAP-P', 'ES', 'GEO-P-ES', 'es', 'MEASURED',
               'se ha detectado mildiu en vinedo en Andalucia',
               date '2026-08-29', timestamptz '2026-08-30 10:00:00+00');

  insert into source_provenance (evidence_id, source_id, snapshot_id, original_ref,
                                 as_of_date)
       values ('EV-P', 'SRC-P', 'SNAP-P', 'https://origem.example/boletim',
               date '2026-08-29');

  insert into publish_run (publish_run_id, pipeline_version, schema_version, status,
                           shadow_validation_passed)
       values ('RUN-P', 'pos-migration', '0.1.0-draft', 'PUBLISHED', true);

  insert into publish_run_freeze (publish_run_id, repository, path, commit_sha, hose_id)
       values ('RUN-P', '%(repo)s',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               '%(commit)s', 'H2');

  -- um objeto por pais: e a unica forma de o isolamento significar alguma coisa
  insert into attention_object (attention_object_id, object_type, country,
                                attention_state, publish_run_id)
       values ('AO-P-ES', 'PHENOMENON_CASE', 'ES', 'ATTENTION_READY', 'RUN-P'),
              ('AO-P-IT', 'REGULATORY_DEADLINE', 'IT', 'FORMING', 'RUN-P'),
              ('AO-P-FR', 'PHENOMENON_CASE', 'FR', 'NEEDS_EVIDENCE', 'RUN-P');

  insert into attention_object_evidence (attention_object_id, evidence_id, role)
       values ('AO-P-ES', 'EV-P', 'PRIMARY');

  insert into storage_provenance (subject_kind, subject_id, source_backend, repository,
                                  path, commit_sha, publish_run_id, source_id,
                                  snapshot_id, as_of_date)
       values ('attention_object', 'AO-P-ES', 'GITHUB', '%(repo)s',
               'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
               '%(commit)s', 'RUN-P', 'SRC-P', 'SNAP-P', date '2026-08-29');

  -- UM objeto, TRES representacoes. Nao tres objetos.
  insert into attention_object_representation (attention_object_id, language, title,
                                               summary, is_translation,
                                               translation_provenance,
                                               translation_quality)
       values ('AO-P-ES', 'es', 'Mildiu en vinedo', 'resumen en espanol',
               false, null, null),
              ('AO-P-ES', 'en', 'Downy mildew in vineyard', 'summary in english',
               true, 'traducao automatica revisada', 'MACHINE_REVIEWED'),
              ('AO-P-ES', 'pt', 'Mildio em vinha', 'resumo em portugues',
               true, 'traducao automatica', 'MACHINE_UNREVIEWED');

  -- texto canonico e traducao moram em tabelas diferentes, de proposito
  insert into content_entity (canonical_entity_id, entity_kind, source_language,
                              original_text, evidence_id)
       values ('CE-P', 'EVIDENCE_QUOTE', 'es',
               'se ha detectado mildiu en vinedo en Andalucia', 'EV-P');

  insert into content_translation (canonical_entity_id, translation_language,
                                   translated_text, translation_provenance,
                                   translation_quality, source_text_hash)
       values ('CE-P', 'pt', 'foi detectado mildio em vinha na Andaluzia',
               'traducao automatica', 'MACHINE_UNREVIEWED', 'hash-do-original');

END $fx$;
""" % {'repo': REPOSITORIO, 'commit': H2_COMMIT}


def checagens(esp):
    """Cada item vira uma linha em _resultado. TIPO diz o que a linha prova.

    ESTRUTURA — contada no catalogo do Postgres
    ISOLAMENTO — medida com o papel trocado de verdade
    MULTILINGUE / PROVENIENCIA — medidas sobre a fixture
    NEGATIVA — a insercao proibida tem de ser RECUSADA; passar seria a falha
    ACHADO — nao e aprovacao nem reprovacao: e o estado de hoje, registrado
    """
    schema = esp['DB_SCHEMA']
    q_ns = "(select oid from pg_namespace where nspname = '%s')" % schema
    return [
        # ── ESTRUTURA, pelo catalogo ─────────────────────────────────────
        {'NOME': 'TABLES_ACTUAL', 'TIPO': 'ESTRUTURA', 'ESPERADO': str(esp['TABLES']),
         'SQL': "select count(*) from pg_class where relkind in ('r','p') "
                "and relnamespace = %s" % q_ns},
        {'NOME': 'VIEWS_ACTUAL', 'TIPO': 'ESTRUTURA', 'ESPERADO': str(esp['VIEWS']),
         'SQL': "select count(*) from pg_class where relkind = 'v' "
                "and relnamespace = %s" % q_ns},
        # RPC e funcao que devolve conjunto para a aplicacao chamar. O helper
        # allowed_countries() devolve char(2)[] e serve a RLS: nao e RPC, e por
        # isso o catalogo tem 5 funcoes onde a autoridade promete 4 RPCs.
        {'NOME': 'RPCS_ACTUAL', 'TIPO': 'ESTRUTURA', 'ESPERADO': str(esp['RPCS']),
         'SQL': "select count(*) from pg_proc where pronamespace = %s "
                "and proretset = true" % q_ns},
        {'NOME': 'RLS_HELPER_FUNCTIONS', 'TIPO': 'ESTRUTURA', 'ESPERADO': '1',
         'SQL': "select count(*) from pg_proc where pronamespace = %s "
                "and proretset = false" % q_ns},
        {'NOME': 'RLS_ENABLED_TABLES', 'TIPO': 'ESTRUTURA', 'ESPERADO': str(esp['TABLES']),
         'SQL': "select count(*) from pg_class where relkind in ('r','p') "
                "and relnamespace = %s and relrowsecurity = true" % q_ns},
        {'NOME': 'TABLES_WITHOUT_RLS', 'TIPO': 'ESTRUTURA', 'ESPERADO': '0',
         'SQL': "select count(*) from pg_class where relkind in ('r','p') "
                "and relnamespace = %s and relrowsecurity = false" % q_ns},
        {'NOME': 'RLS_POLICIES_ACTUAL', 'TIPO': 'ESTRUTURA', 'ESPERADO': '82',
         'SQL': "select count(*) from pg_policies where schemaname = '%s'" % schema},
        {'NOME': 'TABLES_WITHOUT_POLICY', 'TIPO': 'ESTRUTURA', 'ESPERADO': '0',
         'SQL': "select count(*) from pg_class c where c.relkind in ('r','p') "
                "and c.relnamespace = %s and not exists (select 1 from pg_policy p "
                "where p.polrelid = c.oid)" % q_ns},

        # ── ACHADO: o GRANT que a migration nao da ────────────────────────
        # Medido ANTES do grant desta transacao. Esperado NO, e NO nao e falha:
        # e o estado de hoje, escrito onde da para ver.
        {'NOME': 'GRANT_PRESENTE_NA_MIGRATION', 'TIPO': 'ACHADO', 'ESPERADO': 'NO',
         'SQL': "select case when has_table_privilege('portal_reader', "
                "'%s.attention_object', 'SELECT') then 'YES' else 'NO' end" % schema},

        # ── ISOLAMENTO POR PAIS, com o papel trocado ──────────────────────
        {'NOME': 'COUNTRY_ISOLATION_DENY_BY_DEFAULT', 'TIPO': 'ISOLAMENTO',
         'ESPERADO': '0', 'PAPEL': 'portal_reader', 'PAISES': '',
         'SQL': 'select count(*) from attention_object'},
        {'NOME': 'COUNTRY_ISOLATION_ES', 'TIPO': 'ISOLAMENTO', 'ESPERADO': 'AO-P-ES',
         'PAPEL': 'portal_reader', 'PAISES': 'ES',
         'SQL': "select coalesce(string_agg(attention_object_id, ',' order by "
                "attention_object_id), '') from attention_object"},
        {'NOME': 'COUNTRY_ISOLATION_IT', 'TIPO': 'ISOLAMENTO', 'ESPERADO': 'AO-P-IT',
         'PAPEL': 'portal_reader', 'PAISES': 'IT',
         'SQL': "select coalesce(string_agg(attention_object_id, ',' order by "
                "attention_object_id), '') from attention_object"},
        {'NOME': 'COUNTRY_ISOLATION_FR', 'TIPO': 'ISOLAMENTO', 'ESPERADO': 'AO-P-FR',
         'PAPEL': 'portal_reader', 'PAISES': 'FR',
         'SQL': "select coalesce(string_agg(attention_object_id, ',' order by "
                "attention_object_id), '') from attention_object"},
        # ver o proprio pais nao prova isolamento; NAO ver o vizinho prova.
        {'NOME': 'COUNTRY_ISOLATION_ES_NAO_VE_IT_NEM_FR', 'TIPO': 'ISOLAMENTO',
         'ESPERADO': '0', 'PAPEL': 'portal_reader', 'PAISES': 'ES',
         'SQL': "select count(*) from attention_object where country in ('IT','FR')"},
        {'NOME': 'COUNTRY_ISOLATION_GEO_ES', 'TIPO': 'ISOLAMENTO', 'ESPERADO': 'GEO-P-ES',
         'PAPEL': 'portal_reader', 'PAISES': 'ES',
         'SQL': "select coalesce(string_agg(geo_id, ',' order by geo_id), '') "
                "from geo_anchor"},
        # a filha nao tem coluna country: ela herda o pais da raiz
        {'NOME': 'COUNTRY_ISOLATION_FILHA_HERDA_O_PAIS', 'TIPO': 'ISOLAMENTO',
         'ESPERADO': '3', 'PAPEL': 'portal_reader', 'PAISES': 'ES',
         'SQL': "select count(*) from attention_object_representation"},
        {'NOME': 'COUNTRY_ISOLATION_FILHA_NEGA_PAIS_ALHEIO', 'TIPO': 'ISOLAMENTO',
         'ESPERADO': '0', 'PAPEL': 'portal_reader', 'PAISES': 'IT',
         'SQL': "select count(*) from attention_object_representation"},
        {'NOME': 'COUNTRY_ISOLATION_MULTIPAIS', 'TIPO': 'ISOLAMENTO', 'ESPERADO': '2',
         'PAPEL': 'portal_reader', 'PAISES': 'ES,FR',
         'SQL': 'select count(*) from attention_object'},

        # ── MULTILINGUE ───────────────────────────────────────────────────
        {'NOME': 'MULTILINGUAL_ONE_OBJECT_MULTI_REPRESENTATION', 'TIPO': 'MULTILINGUE',
         'ESPERADO': '1|3',
         'SQL': "select count(distinct attention_object_id) || '|' || count(*) "
                "from attention_object_representation "
                "where attention_object_id = 'AO-P-ES'"},
        {'NOME': 'ORIGINAL_TEXT_PRESERVED_EVIDENCE', 'TIPO': 'MULTILINGUE',
         'ESPERADO': 'se ha detectado mildiu en vinedo en Andalucia',
         'SQL': "select original_text from evidence where evidence_id = 'EV-P'"},
        {'NOME': 'ORIGINAL_TEXT_KEEPS_SOURCE_LANGUAGE', 'TIPO': 'MULTILINGUE',
         'ESPERADO': 'es',
         'SQL': "select source_language::text from evidence where evidence_id = 'EV-P'"},
        # a traducao existe e NAO encostou no original: sao duas tabelas
        {'NOME': 'TRANSLATION_SEPARATE_TABLE', 'TIPO': 'MULTILINGUE',
         'ESPERADO': 'se ha detectado mildiu en vinedo en Andalucia|'
                     'foi detectado mildio em vinha na Andaluzia',
         'SQL': "select ce.original_text || '|' || ct.translated_text "
                "from content_entity ce join content_translation ct "
                "on ct.canonical_entity_id = ce.canonical_entity_id "
                "where ce.canonical_entity_id = 'CE-P'"},
        {'NOME': 'TRANSLATION_DECLARES_PROVENANCE', 'TIPO': 'MULTILINGUE',
         'ESPERADO': '2',
         'SQL': "select count(*) from attention_object_representation "
                "where attention_object_id = 'AO-P-ES' and is_translation = true "
                "and translation_provenance is not null"},
        {'NOME': 'RPC_FALLBACK_USA_A_LINGUA_PEDIDA', 'TIPO': 'MULTILINGUE',
         'ESPERADO': 'es|NO',
         'SQL': "select r.language::text || '|' || r.fallback_used from "
                "resolve_representation('AO-P-ES', 'es') r"},
        {'NOME': 'RPC_FALLBACK_CAI_PARA_EN', 'TIPO': 'MULTILINGUE',
         'ESPERADO': 'en|YES',
         'SQL': "select r.language::text || '|' || r.fallback_used from "
                "resolve_representation('AO-P-ES', 'fr') r"},
        {'NOME': 'RPC_NAO_INVENTA_TRADUCAO', 'TIPO': 'MULTILINGUE',
         'ESPERADO': 'NO_REPRESENTATION_AVAILABLE',
         'SQL': "select r.fallback_used from resolve_representation('AO-P-IT', 'it') r"},

        # ── PROVENIENCIA, elo a elo ───────────────────────────────────────
        # Uma consulta so, do objeto ate o commit. Se qualquer elo do meio for
        # NULL o join morre e a contagem cai — que e exatamente o ponto.
        {'NOME': 'PROVENANCE_END_TO_END', 'TIPO': 'PROVENIENCIA',
         'ESPERADO': 'AO-P-ES|EV-P|SRC-P|SNAP-P|RUN-P|' + H2_COMMIT,
         'SQL': "select o.attention_object_id || '|' || e.evidence_id || '|' || "
                "s.source_id || '|' || sn.snapshot_id || '|' || pr.publish_run_id "
                "|| '|' || prf.commit_sha "
                "from attention_object o "
                "join attention_object_evidence aoe on aoe.attention_object_id = "
                "o.attention_object_id "
                "join evidence e on e.evidence_id = aoe.evidence_id "
                "join source s on s.source_id = e.source_id "
                "join source_snapshot sn on sn.snapshot_id = e.snapshot_id "
                "join publish_run pr on pr.publish_run_id = o.publish_run_id "
                "join publish_run_freeze prf on prf.publish_run_id = pr.publish_run_id "
                "where o.attention_object_id = 'AO-P-ES'"},
        {'NOME': 'PROVENANCE_COMMIT_TEM_40_CARACTERES', 'TIPO': 'PROVENIENCIA',
         'ESPERADO': '40',
         'SQL': "select length(commit_sha)::text from publish_run_freeze "
                "where publish_run_id = 'RUN-P'"},
        {'NOME': 'PROVENANCE_VIEW_CHEGA_NO_COMMIT', 'TIPO': 'PROVENIENCIA',
         'ESPERADO': H2_COMMIT,
         'SQL': "select commit_sha from v_publish_provenance "
                "where attention_object_id = 'AO-P-ES' limit 1"},
        {'NOME': 'PROVENANCE_SOURCE_LOCATION_NAO_E_FACT_LOCATION', 'TIPO': 'PROVENIENCIA',
         'ESPERADO': 'ES|GEO-P-ES',
         'SQL': "select source_location_country || '|' || fact_location_geo_id "
                "from evidence where evidence_id = 'EV-P'"},
        {'NOME': 'PROVENANCE_GITHUB_E_SUPABASE_SEPARADOS', 'TIPO': 'PROVENIENCIA',
         'ESPERADO': 'GITHUB|0',
         'SQL': "select source_backend::text || '|' || "
                "(case when table_or_view is null then 0 else 1 end)::text "
                "from storage_provenance where subject_id = 'AO-P-ES'"},
        {'NOME': 'PROVENANCE_OBJETO_SEM_EVIDENCIA_NAO_TEM_CADEIA', 'TIPO': 'PROVENIENCIA',
         'ESPERADO': '0',
         'SQL': "select count(*) from attention_object o "
                "join attention_object_evidence aoe on aoe.attention_object_id = "
                "o.attention_object_id where o.attention_object_id = 'AO-P-FR'"},
    ]


NEGATIVAS = [
    {'NOME': 'NEG_PUBLICADO_SEM_SOMBRA_APROVADA',
     'SQL': "insert into publish_run (publish_run_id, pipeline_version, schema_version, "
            "status, shadow_validation_passed) values ('RUN-X', 'x', 'x', 'PUBLISHED', "
            "false)",
     'POR_QUE': 'publicar sem a validacao sombra ter passado'},
    {'NOME': 'NEG_GITHUB_SEM_COMMIT',
     'SQL': "insert into storage_provenance (subject_kind, subject_id, source_backend, "
            "repository, path) values ('attention_object', 'AO-P-ES', 'GITHUB', "
            "'r', 'p')",
     'POR_QUE': 'proveniencia GitHub sem o commit que congela o arquivo'},
    {'NOME': 'NEG_BACKENDS_MISTURADOS',
     'SQL': "insert into storage_provenance (subject_kind, subject_id, source_backend, "
            "repository, path, commit_sha, table_or_view, db_schema, primary_key) "
            "values ('attention_object', 'AO-P-ES', 'GITHUB', 'r', 'p', "
            "'%s', 'attention_object', 'sintonia', 'AO-P-ES')" % H2_COMMIT,
     'POR_QUE': 'a mesma linha dizendo que veio do GitHub e do Supabase'},
    {'NOME': 'NEG_TRADUCAO_SEM_PROVENIENCIA',
     'SQL': "insert into attention_object_representation (attention_object_id, language, "
            "title, is_translation) values ('AO-P-IT', 'en', 'title', true)",
     'POR_QUE': 'representacao marcada como traducao sem dizer quem traduziu'},
    {'NOME': 'NEG_TRADUCAO_PARA_LINGUA_QUE_NAO_E_LINGUA',
     'SQL': "insert into content_translation (canonical_entity_id, translation_language, "
            "translated_text, translation_provenance) values ('CE-P', 'UNKNOWN', 't', 'p')",
     'POR_QUE': 'UNKNOWN e MULTILINGUAL nao sao alvo de traducao',
     'CODIGO': '23514'},
    {'NOME': 'NEG_DUAS_REPRESENTACOES_NA_MESMA_LINGUA',
     'SQL': "insert into attention_object_representation (attention_object_id, language, "
            "title) values ('AO-P-ES', 'es', 'outro titulo')",
     'POR_QUE': 'um objeto tem UMA representacao por lingua, nao duas'},
    {'NOME': 'NEG_LOCALITY_TEXT_COM_PONTO',
     'SQL': "insert into geo_anchor (geo_id, country, locality_text, geometry, "
            "geo_resolution, geometry_source_id) values ('GEO-X', 'ES', 'un pueblo', "
            "'{\"type\":\"Point\"}'::jsonb, 'LOCALITY_TEXT', 'SRC-P')",
     'POR_QUE': 'texto de localidade nao vira ponto no mapa'},
    {'NOME': 'NEG_GEOMETRIA_SEM_ORIGEM',
     'SQL': "insert into geo_anchor (geo_id, country, geometry, geo_resolution) "
            "values ('GEO-Y', 'ES', '{\"type\":\"Point\"}'::jsonb, 'POINT')",
     'POR_QUE': 'geometria sem dizer de onde veio'},
    {'NOME': 'NEG_OFFSETS_SOZINHOS',
     'SQL': "insert into evidence (evidence_id, source_id, source_language, "
            "evidence_level, passage_start) values ('EV-X', 'SRC-P', 'es', 'PARTIAL', 10)",
     'POR_QUE': 'inicio de trecho sem fim: meio recorte nao localiza nada'},
]


def _lit(txt):
    return "'" + txt.replace("'", "''") + "'"


def gerar_sql():
    esp = esperado_da_autoridade()
    L = ["-- MEDICAO POS-MIGRATION — SINTONIA EAME",
         '--',
         '-- GERADO por scripts/supabase_post_migration.py. Nao editar a mao.',
         '--',
         '-- ALVO: %s (eame-sintonia-dev)' % DEV_PROJECT_REF,
         '--',
         '-- REFS RECUSADOS, ambos medidos:']
    for ref, por_que in sorted(REFS_RECUSADOS.items()):
        L.append('--   %s — %s' % (ref, por_que))
    L += [
        '--',
        '-- ORDEM: 0000 (inventario) -> 0001 (migration) -> 0002 (a lei pega?)',
        '--        -> 0003 (este: o que existe la dentro, e igual ao prometido?)',
        '--',
        '-- Tudo dentro de UMA transacao que termina em ROLLBACK. O banco sai como',
        '-- entrou: nenhuma linha da fixture sobrevive, nenhum GRANT sobrevive.',
        '--',
        '-- As contagens vem do CATALOGO do Postgres, nao do texto do .sql. Contar',
        '-- a palavra CREATE num arquivo prova que alguem digitou; so pg_class prova',
        '-- que a tabela existe.',
        '--',
        '-- O GRANT: a migration cria os papeis e as politicas e NAO da GRANT.',
        '-- Politica e permissao de LINHA, GRANT e permissao de TABELA — sem o',
        '-- segundo, portal_reader nao le nem o pais dele. Este arquivo mede isso',
        '-- em GRANT_PRESENTE_NA_MIGRATION (esperado NO, e NO e o estado de hoje,',
        '-- nao uma falha deste teste) e da o GRANT aqui dentro so para conseguir',
        '-- provar que a POLICY isola. O ROLLBACK leva o GRANT junto.',
        '',
        'BEGIN;',
        'SET search_path TO %s, public;' % esp['DB_SCHEMA'],
        '',
        '-- ordem e IDENTITY, nao serial, de proposito: com serial o portal_reader',
        '-- precisaria de USAGE na sequence para inserir a propria medicao, e o nome',
        '-- do schema temporario muda a cada sessao. Coluna identity herda o',
        '-- privilegio da tabela e nao pede GRANT nenhum.',
        'CREATE TEMP TABLE _resultado (',
        '  ordem bigint GENERATED BY DEFAULT AS IDENTITY, nome text, tipo text,',
        '  esperado text, encontrado text, veredito text) ON COMMIT DROP;',
        '',
        '-- ── FIXTURE ────────────────────────────────────────────────────────',
        FIXTURE.strip(),
        '',
    ]

    checks = checagens(esp)

    # As de estrutura e as que rodam como dono: medidas antes de trocar de papel.
    L.append('-- ── ESTRUTURA, MULTILINGUE, PROVENIENCIA ───────────────────────────')
    for c in checks:
        if 'PAPEL' in c:
            continue
        L.append(_linha_resultado(c))
        L.append('')

    # As de isolamento: cada uma troca de papel, mede, e volta.
    L += [
        '-- ── ISOLAMENTO POR PAIS ────────────────────────────────────────────',
        '--',
        '-- O GRANT abaixo NAO esta na migration. Ele existe so dentro desta',
        '-- transacao, para que a policy tenha o que filtrar. Sem ele o resultado',
        '-- de todo teste de isolamento seria zero — e zero por falta de GRANT nao',
        '-- prova isolamento nenhum: prova que a porta esta trancada por fora.',
        'GRANT USAGE ON SCHEMA %s TO portal_reader;' % esp['DB_SCHEMA'],
        'GRANT SELECT ON ALL TABLES IN SCHEMA %s TO portal_reader;' % esp['DB_SCHEMA'],
        'GRANT ALL ON _resultado TO portal_reader;',
        '',
    ]
    for c in checks:
        if 'PAPEL' not in c:
            continue
        L += [
            "SET LOCAL sintonia.countries = %s;" % _lit(c['PAISES']),
            'SET LOCAL ROLE %s;' % c['PAPEL'],
            _linha_resultado(c),
            'RESET ROLE;',
            '',
        ]
    L.append("RESET ROLE;")
    L.append("SET LOCAL sintonia.countries = '';")
    L.append('')

    # As negativas: a insercao TEM de ser recusada.
    L += ['-- ── NEGATIVAS: so a recusa prova que a lei pega ────────────────────',
          '--',
          '-- Cada bloco tenta gravar uma linha proibida. PASS e quando o Postgres',
          '-- levanta excecao. Se a insercao passar, o veredito e FAIL — e o',
          '-- SAVEPOINT desfaz a linha para nao contaminar o que vem depois.',
          '']
    for n in NEGATIVAS:
        L.append(_bloco_negativa(n))
        L.append('')

    L += [
        '-- ── RESULTADO ──────────────────────────────────────────────────────',
        'SELECT jsonb_pretty(jsonb_build_object(',
        "  'DEV_PROJECT_REF_ESPERADO', %s," % _lit(DEV_PROJECT_REF),
        "  'CONFERIR_O_REF', 'este SQL nao sabe onde esta rodando: quem cola confere',",
        "  'TOTAL', (select count(*) from _resultado),",
        "  'PASS', (select count(*) from _resultado where veredito = 'PASS'),",
        "  'FAIL', (select count(*) from _resultado where veredito = 'FAIL'),",
        "  'FALHAS', (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb)",
        "             from (select nome, tipo, esperado, encontrado from _resultado",
        "                   where veredito = 'FAIL' order by ordem) t),",
        "  'ACHADOS', (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb)",
        "              from (select nome, esperado, encontrado from _resultado",
        "                    where tipo = 'ACHADO' order by ordem) t),",
        "  'TUDO', (select jsonb_agg(to_jsonb(t) order by t.ordem)",
        "           from (select * from _resultado) t)",
        ')) AS medicao_pos_migration;',
        '',
        '-- O banco sai como entrou.',
        'ROLLBACK;',
        '',
    ]
    return '\n'.join(L)


def _linha_resultado(c):
    return ('INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)\n'
            'SELECT %s, %s, %s, coalesce(v::text, %s),\n'
            "       CASE WHEN coalesce(v::text, '<NULO>') = %s THEN 'PASS' ELSE 'FAIL' END\n"
            '  FROM (%s) s(v);' % (_lit(c['NOME']), _lit(c['TIPO']), _lit(c['ESPERADO']),
                                   _lit('<NULO>'), _lit(c['ESPERADO']), c['SQL']))


def _bloco_negativa(n):
    """Uma tentativa proibida por bloco, e a limpeza sem comando de transacao.

    PL/pgSQL NAO aceita SAVEPOINT nem ROLLBACK TO escritos a mao dentro de um
    DO — levanta erro de comando de transacao invalido e derruba o arquivo
    inteiro. O que ele aceita e o sub-bloco BEGIN ... EXCEPTION, que ja abre
    uma subtransacao sozinho e a desfaz quando captura a excecao.

    Dai o RAISE proposital: quando a insercao proibida PASSA (a falha que este
    teste procura), levantar excecao de proposito e a unica forma de apagar a
    linha que entrou sem escrever ROLLBACK. A variavel `aceito` sobrevive ao
    desfazimento porque variavel de PL/pgSQL nao pertence a transacao.
    """
    return ('''DO $neg$
DECLARE aceito boolean := false; estado text := '';
BEGIN
  BEGIN
    %(sql)s;
    aceito := true;
    RAISE EXCEPTION 'DESFAZER_A_LINHA_QUE_NAO_DEVIA_TER_ENTRADO';
  EXCEPTION WHEN others THEN
    estado := SQLSTATE;
  END;
  INSERT INTO _resultado (nome, tipo, esperado, encontrado, veredito)
  VALUES (%(nome)s, 'NEGATIVA', 'RECUSADO',
          CASE WHEN aceito THEN 'ACEITO' ELSE 'RECUSADO: ' || estado END,
          CASE WHEN aceito THEN 'FAIL' ELSE 'PASS' END);
END $neg$;  -- %(por_que)s''' % {'sql': n['SQL'], 'nome': _lit(n['NOME']),
                                'por_que': n['POR_QUE']})


def medir():
    esp = esperado_da_autoridade()
    checks = checagens(esp)
    por_tipo = {}
    for c in checks:
        por_tipo[c['TIPO']] = por_tipo.get(c['TIPO'], 0) + 1
    por_tipo['NEGATIVA'] = len(NEGATIVAS)
    return {
        'SOURCE_ID': 'SUPABASE-POST-MIGRATION-PLAN-EAME-2026-08-31',
        'source': 'Medicao do DEV depois da migration. Contagem vem do catalogo, '
                  'nao do texto do .sql.',
        'DEV_PROJECT_REF': DEV_PROJECT_REF,
        'REFS_RECUSADOS': REFS_RECUSADOS,
        'EXECUTADA': False,
        'POR_QUE_NAO': 'nao ha credencial nesta maquina. Quem tem acesso roda; o SQL '
                       'se reprova sozinho.',
        'ORDEM': [
            'supabase/inventory/0000_readonly_inventory.sql (antes de tudo)',
            'supabase/migrations/0001_initial_canonical_schema.sql',
            'supabase/validation/0002_dev_validation.sql',
            'supabase/validation/0003_post_migration_checks.sql',
        ],
        'ESPERADO_DA_AUTORIDADE': esp,
        'VERIFICACOES_POR_TIPO': por_tipo,
        'TOTAL': len(checks) + len(NEGATIVAS),
        'VERIFICACOES_NEGATIVAS': len(NEGATIVAS),
        'DEPENDE_DO_FRONTEND': False,
        'TRANSACAO': 'BEGIN ... ROLLBACK — inclusive o GRANT some no fim',
        'ACHADO_REGISTRADO': {
            'O_QUE': 'a migration cria papeis e politicas e nao da GRANT',
            'POR_QUE_IMPORTA': ('politica filtra LINHA; GRANT libera TABELA. Sem GRANT, '
                                'portal_reader nao le nem o pais dele — o isolamento por '
                                'pais existe no papel e esta desligado na pratica.'),
            'HOJE_E_SEGURO': 'sim: negar tudo erra para o lado certo',
            'HOJE_ESTA_COMPLETO': 'nao',
            'ONDE_SE_CORRIGE': ('data/supabase/SUPABASE-CANONICAL-SCHEMA.json, secao RLS, '
                                'e regerar a migration. Nao no .sql a mao.'),
            'CORRIGIDO_NESTA_RODADA': 'NO',
        },
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    if '--sync' in sys.argv:
        with open(SAIDA_SQL, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(gerar_sql())
        with open(SAIDA_JSON, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado em', os.path.relpath(SAIDA_SQL, RAIZ))
        print('gravado em', os.path.relpath(SAIDA_JSON, RAIZ))
    print(json.dumps(m, ensure_ascii=False, indent=2))
