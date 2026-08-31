"""Revisao da migration contra o schema canonico.

O JSON e autoridade; o SQL e produto. Este revisor NAO confia em que a geracao
saiu certa: ele le o SQL gerado e confere contra o JSON, item por item.

Nenhuma correcao e feita no SQL. Se algo faltar, a mudanca vai para o JSON e a
migration e regerada.

Uso:
    py scripts/supabase_migration_review.py            # imprime
    py scripts/supabase_migration_review.py --sync     # grava o artefato
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))

from supabase_schema import carregar, gerar, _pk  # noqa: E402

MIGRATION = os.path.join(RAIZ, 'supabase', 'migrations',
                         '0001_initial_canonical_schema.sql')
SAIDA = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-MIGRATION-REVIEW.json')


def revisar():
    d = carregar()
    with open(MIGRATION, encoding='utf-8') as fh:
        sql = fh.read()

    achados = []

    def exige(cond, chave, detalhe):
        if not cond:
            achados.append({'CHECK': chave, 'DETALHE': detalhe})
        return cond

    # ── 1 · o SQL no disco e exatamente o que o JSON gera ──
    gerado = gerar(d)
    exige(sql == gerado, 'SQL_DERIVA_DO_JSON',
          'a migration no disco divergiu do JSON. Editar SQL a mao cria uma segunda '
          'verdade que a proxima geracao apaga.')

    # ── 2 · contagens ──
    contagens = {
        'TABLES': (len(re.findall(r'^CREATE TABLE ', sql, re.M)), len(d['TABLES'])),
        'VIEWS': (len(re.findall(r'^CREATE OR REPLACE VIEW ', sql, re.M)), len(d['VIEWS'])),
        'RPCS': (len(re.findall(r'^CREATE OR REPLACE FUNCTION ', sql, re.M)),
                 len(d['RPCS']) + 1),  # +1: helper allowed_countries
        'ENUMS': (len(re.findall(r'^CREATE TYPE ', sql, re.M)), len(d['VOCABULARIES'])),
        'FKS': (len(re.findall(r'ADD CONSTRAINT \w+_fk', sql)),
                sum(1 for t in d['TABLES'] for c in t['columns'] if c.get('fk'))),
        'CHECKS': (len(re.findall(r'CONSTRAINT \w+ CHECK ', sql)),
                   sum(len(t.get('checks', [])) for t in d['TABLES'])),
        'UNIQUES': (len(re.findall(r'CONSTRAINT \w+_uq\d+ UNIQUE', sql)),
                    sum(len(t.get('unique', [])) for t in d['TABLES'])),
        'RLS_ENABLE': (len(re.findall(r'ENABLE ROW LEVEL SECURITY', sql)), len(d['TABLES'])),
        'PUBLISHER_POLICIES': (len(re.findall(r'CREATE POLICY publisher_all', sql)),
                               len(d['TABLES'])),
    }
    for chave, (achado, esperado) in contagens.items():
        exige(achado == esperado, 'CONTAGEM_%s' % chave,
              'no SQL: %d · esperado pelo JSON: %d' % (achado, esperado))

    # ── 3 · indices nas chaves estrangeiras ──
    # Postgres indexa PK e UNIQUE sozinho, mas NAO a coluna que aponta para fora.
    # Sem indice, todo join do produto varre a tabela inteira.
    fks = [(t['name'], c['name']) for t in d['TABLES'] for c in t['columns'] if c.get('fk')]
    pks = {t['name']: _pk(t) for t in d['TABLES']}
    uqs = {t['name']: [u[0] for u in t.get('unique', [])] for t in d['TABLES']}
    # a coluna ja indexada por ser a PRIMEIRA da PK, ou a primeira de um UNIQUE,
    # nao precisa de indice proprio
    precisam = [(tab, col) for tab, col in fks
                if pks.get(tab, [])[:1] != [col] and col not in uqs.get(tab, [])]
    indices = set(re.findall(r'CREATE INDEX \w+ ON (\w+) \((\w+)\)', sql))
    sem_indice = [f'{t}.{c}' for t, c in precisam if (t, c) not in indices]
    exige(not sem_indice, 'INDICES_EM_CHAVE_ESTRANGEIRA',
          '%d colunas de chave estrangeira sem indice: %s'
          % (len(sem_indice), ', '.join(sem_indice[:12])
             + (' ...' if len(sem_indice) > 12 else '')))

    # ── 4 · comportamento de delete ──
    sem_on_delete = len(re.findall(r'REFERENCES \w+ \(\w+\)\s*;', sql))
    exige(sem_on_delete == 0, 'ON_DELETE_DECLARADO',
          '%d chaves estrangeiras sem ON DELETE explicito. O padrao NO ACTION nao e '
          'errado, mas nao declarado ele vira surpresa: a tabela filha de um objeto '
          'deveria cair com ele, e a evidencia NAO deveria poder ser apagada por baixo '
          'de quem a cita.' % sem_on_delete)

    # ── 5 · integridade semantica que precisa sobreviver ──
    leis = {
        'EXPIRY_NE_WITHDRAWAL': 'expiry_is_withdrawal = false',
        'PRAZO_NAO_AUTORIZA_NEGOCIO': "max_authorized_action <> 'BUSINESS_DECISION'",
        'MEDIA_EXIGE_N': 'CONSTRAINT field_pressure_reading_n_positivo CHECK (n > 0)',
        'LOCALITY_TEXT_NAO_E_POINT': "geo_resolution <> 'LOCALITY_TEXT'",
        'POINT_EXIGE_GEOMETRIA': "geo_resolution <> 'POINT'",
        'DEPENDENTE_DECLARA_ALVO': 'depends_on_leg_id IS NOT NULL',
        'BACKENDS_NAO_SE_MISTURAM': 'repository IS NOT NULL AND table_or_view IS NOT NULL',
        'PUBLICADO_EXIGE_SOMBRA': 'shadow_validation_passed = true',
        'EXPERTISE_EXIGE_EVIDENCIA': 'evidence_id IS NOT NULL',
        'GDPR_ANTES_DA_IDENTIDADE': "entity_kind <> 'PERSON_CREATOR'",
        'LATENCIA_SEM_MEDICAO_E_NULA': 'pipeline_latency_seconds IS NULL',
    }
    for nome, marca in leis.items():
        exige(marca in sql, 'LEI_%s' % nome, 'a lei sumiu do SQL: %s' % marca)

    # ── 6 · isolamento de pais ──
    com_pais = [t['name'] for t in d['TABLES']
                if any(c['name'] == 'country' for c in t['columns'])]
    faltam = [n for n in com_pais
              if 'CREATE POLICY portal_read_country ON %s ' % n not in sql]
    exige(not faltam, 'ISOLAMENTO_POR_PAIS',
          'tabelas com country sem politica de leitura: %s' % faltam)
    exige('allowed_countries()' in sql, 'HELPER_DE_PAIS', 'funcao allowed_countries ausente')

    # ── 7 · multilingue ──
    exige('CREATE TABLE content_translation' in sql and
          'CREATE TABLE content_entity' in sql,
          'ORIGINAL_E_TRADUCAO_SEPARADOS', 'original e traducao precisam de tabelas distintas')
    exige("language language_code NOT NULL" in sql,
          'REPRESENTACAO_POR_IDIOMA', 'representacao sem coluna de idioma')
    exige('resolve_representation' in sql, 'FALLBACK_NUM_LUGAR_SO',
          'a politica de fallback precisa viver numa funcao unica')

    # ── 8 · linhagem ──
    exige('CREATE TABLE source_provenance' in sql and
          'CREATE TABLE storage_provenance' in sql,
          'DUAS_PROVENIENCIAS', 'origem externa e transporte nao podem ser a mesma tabela')
    exige('CREATE TABLE publish_run_freeze' in sql, 'LINHAGEM_DE_PUBLICACAO',
          'sem publish_run_freeze nao da para responder de que commit veio a linha')
    exige('v_publish_provenance' in sql, 'VIEW_DE_LINHAGEM', 'view de linhagem ausente')

    # ── 9 · seguranca ──
    exige('SECURITY INVOKER' in sql, 'RPC_NAO_CONTORNA_RLS',
          'RPC com SECURITY DEFINER contornaria a politica de pais')
    # Procurar a PALAVRA nao serve: o SQL cita SERVICE_ROLE_KEY dentro de um comentario
    # que a PROIBE. Confundir a proibicao com a coisa proibida seria o mesmo erro de
    # substring de sempre. Aqui so conta VALOR: atribuicao ou string parecida com chave.
    valores = re.findall(r'(?:SERVICE_ROLE_KEY|apikey|api_key|password)\s*[:=]\s*[\'"][^\'"]{8,}',
                         sql, re.I)
    valores += re.findall(r'eyJ[A-Za-z0-9_-]{20,}', sql)  # JWT
    exige(not valores, 'SEM_SEGREDO_NO_SQL',
          'a migration carrega valor de credencial: %s' % valores[:3])
    exige('SERVICE_ROLE_KEY nunca vai para o frontend' in sql, 'PROIBICAO_ESCRITA',
          'a proibicao do service role sumiu do SQL')

    # ── 10 · nullability das chaves obrigatorias por tipo ──
    obrig = {
        'phenomenon_case': ['geo_id', 'crop_term_id', 'issue_term_id'],
        'regulatory_deadline_object': ['registration_id', 'deadline_date', 'deadline_kind',
                                       'status_as_declared_by_source'],
        'field_pressure_reading': ['value', 'n', 'unit'],
    }
    for tab, cols in obrig.items():
        t = next(x for x in d['TABLES'] if x['name'] == tab)
        mapa = {c['name']: c for c in t['columns']}
        for col in cols:
            exige(mapa[col].get('null') is False or mapa[col].get('pk'),
                  'NOT_NULL_%s_%s' % (tab, col), 'campo obrigatorio do tipo aceita nulo')

    return {
        'SOURCE_ID': 'SUPABASE-MIGRATION-REVIEW-EAME-2026-08-31',
        'source': 'Revisao da migration gerada contra o schema canonico.',
        'SCHEMA_VERSION': d['SCHEMA_VERSION'],
        'MIGRATION_APPLIED': 'NO',
        'CONTAGENS': {k: {'SQL': a, 'JSON': e} for k, (a, e) in contagens.items()},
        'ACHADOS': achados,
        'MIGRATION_REVIEW': 'PASS' if not achados else 'FAIL',
        'REGRA': ('Nenhuma correcao entra no .sql. A mudanca vai para o JSON e a '
                  'migration e regerada.'),
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    r = revisar()
    if '--sync' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(r, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado em', os.path.relpath(SAIDA, RAIZ))
    print(json.dumps(r, ensure_ascii=False, indent=2))
