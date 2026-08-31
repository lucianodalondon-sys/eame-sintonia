"""Gera a migration SQL a partir do schema canonico e deriva as contagens.

O JSON e a fonte de verdade; o SQL e artefato. Escrever os dois a mao criaria
duas verdades que divergem no primeiro dia.

Uso:
    py scripts/supabase_schema.py             # imprime a medicao
    py scripts/supabase_schema.py --sync      # regrava a migration
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-CANONICAL-SCHEMA.json')
MIGRATION = os.path.join(RAIZ, 'supabase', 'migrations',
                         '0001_initial_canonical_schema.sql')

CABECALHO = """-- SINTONIA EAME · SCHEMA CANONICO · RASCUNHO
--
-- GERADO por scripts/supabase_schema.py a partir de
-- data/supabase/SUPABASE-CANONICAL-SCHEMA.json.
-- NAO EDITAR A MAO: a proxima geracao apaga a edicao.
--
-- MIGRATION_APPLIED = NO. Este arquivo NAO foi aplicado em producao e exige
-- revisao humana antes de qualquer `supabase db push`.
--
-- Regra que atravessa tudo: os tipos persistidos sao os CANONICOS do
-- FINAL-HOSE-MAP. Os aliases do casco index (11) vivem em sintonia.ui_alias e
-- nunca substituem o tipo.

BEGIN;

CREATE SCHEMA IF NOT EXISTS {schema};
SET search_path TO {schema}, public;
"""


def carregar():
    with open(SCHEMA, encoding='utf-8') as fh:
        return json.load(fh)


def _pk(tabela):
    if tabela.get('pk'):
        return list(tabela['pk'])
    return [c['name'] for c in tabela['columns'] if c.get('pk')]


def sql_enums(d):
    linhas = ['\n-- ── VOCABULARIOS FECHADOS ─────────────────────────────────────────────']
    for nome, valores in d['VOCABULARIES'].items():
        vals = ', '.join("'%s'" % v for v in valores)
        linhas.append("CREATE TYPE %s AS ENUM (%s);" % (nome, vals))
    nao = d['NAO_PERSISTIR']
    linhas.append('')
    linhas.append('-- NAO existe enum para request_state (%s):' % ', '.join(nao['request_state']))
    linhas.append('-- %s' % nao['POR_QUE'].replace('\n', ' '))
    return '\n'.join(linhas)


def sql_tabelas(d):
    partes = ['\n-- ── TABELAS ───────────────────────────────────────────────────────────']
    alteracoes = ['\n-- ── CHAVES ESTRANGEIRAS ───────────────────────────────────────────────',
                  '-- Declaradas depois das tabelas: o grafo tem ciclos legitimos',
                  '-- (evidence -> source -> ... -> evidence) e ordenar por dependencia',
                  '-- exigiria quebrar uma relacao real.']
    for t in d['TABLES']:
        partes.append('\n-- %s' % t['purpose'])
        for linha in ('-- POR QUE: ' + t['why']).split('\n'):
            partes.append(linha)
        if t.get('hose_id'):
            partes.append('-- HOSE_ID: %s · CANONICAL_PAYLOAD_TYPE: %s'
                          % (t['hose_id'], t.get('canonical_payload_type', '—')))
        if t.get('parent_hose_id'):
            partes.append('-- PARENT_HOSE_ID: %s · CANONICAL_PAYLOAD_TYPE: %s'
                          % (t['parent_hose_id'], t.get('canonical_payload_type', '—')))
        if t.get('privacy'):
            partes.append('-- PRIVACIDADE: %s' % t['privacy'])
        if t.get('no_counter_column'):
            partes.append('-- %s' % t['no_counter_column'])

        cols = []
        for c in t['columns']:
            frag = '  %s %s' % (c['name'], c['type'])
            if c.get('identity'):
                frag += ' GENERATED ALWAYS AS IDENTITY'
            if c.get('null') is False or c.get('pk'):
                frag += ' NOT NULL'
            if c.get('default'):
                frag += ' DEFAULT %s' % c['default']
            if c.get('note'):
                frag += '  -- %s' % c['note']
            cols.append(frag)
        pk = _pk(t)
        if pk:
            cols.append('  CONSTRAINT %s_pk PRIMARY KEY (%s)' % (t['name'], ', '.join(pk)))
        for i, u in enumerate(t.get('unique', []), 1):
            cols.append('  CONSTRAINT %s_uq%d UNIQUE (%s)' % (t['name'], i, ', '.join(u)))
        for ck in t.get('checks', []):
            cols.append('  CONSTRAINT %s_%s CHECK (%s)' % (t['name'], ck['name'], ck['expr']))

        # a virgula nao entra em linhas que sao so comentario
        corpo = []
        for i, linha in enumerate(cols):
            corpo.append(linha if i == len(cols) - 1 else _com_virgula(linha))
        partes.append('CREATE TABLE %s (\n%s\n);' % (t['name'], '\n'.join(corpo)))

        for c in t['columns']:
            if c.get('fk'):
                alvo_tab, alvo_col = c['fk'].split('.')
                alteracoes.append(
                    'ALTER TABLE %s ADD CONSTRAINT %s_%s_fk\n'
                    '  FOREIGN KEY (%s) REFERENCES %s (%s);'
                    % (t['name'], t['name'], c['name'], c['name'], alvo_tab, alvo_col))
    return '\n'.join(partes), '\n'.join(alteracoes)


def _com_virgula(linha):
    """Poe a virgula ANTES do comentario, nunca depois."""
    if '  -- ' in linha:
        codigo, comentario = linha.split('  -- ', 1)
        return '%s,  -- %s' % (codigo, comentario)
    return linha + ','


def sql_views(d):
    linhas = ['\n-- ── VIEWS DE LEITURA ──────────────────────────────────────────────────',
              '-- Projecoes. A fonte de verdade continua normalizada: nenhuma view',
              '-- redefine regra, e nenhuma duplica logica que ja existe em outra.']
    for v in d['VIEWS']:
        linhas.append('\n-- %s · %s' % (v['name'], v['purpose']))
        if v.get('why'):
            linhas.append('-- POR QUE: %s' % v['why'])
        linhas.append('-- LE: %s' % ', '.join(v['reads']))
        if v.get('derives'):
            linhas.append('-- DERIVA: %s' % ', '.join(v['derives']))
    linhas.append('\n-- O corpo das views entra na proxima rodada, junto com o publisher.')
    linhas.append('-- Declarar a assinatura antes do corpo evita que cada view invente')
    linhas.append('-- sua propria versao da regra.')
    return '\n'.join(linhas)


def sql_rpcs(d):
    linhas = ['\n-- ── RPCs ──────────────────────────────────────────────────────────────']
    for r in d['RPCS']:
        linhas.append('\n-- %s(%s)' % (r['name'], ', '.join(r['args'])))
        linhas.append('--   %s' % r['purpose'])
        linhas.append('--   RETORNA: %s' % ', '.join(r['returns']))
        if r.get('why'):
            linhas.append('--   POR QUE: %s' % r['why'])
    p = d['LANGUAGE_FALLBACK_POLICY']
    linhas.append('\n-- FALLBACK DE IDIOMA: %s' % ' -> '.join(p['CHAIN']))
    linhas.append('-- %s' % p['REGRA'])
    linhas.append('-- %s' % p['EVIDENCIA'])
    return '\n'.join(linhas)


def sql_rls(d):
    return """
-- ── ROW LEVEL SECURITY ────────────────────────────────────────────────
-- Ligado em TODAS as tabelas. Uma tabela sem RLS num projeto Supabase fica
-- legivel pela chave anonima: o padrao seguro e negar e abrir depois.
--
-- Papeis:
--   publisher_role  escreve inteligencia canonica (service role, so no backend)
--   portal_reader   le o que o pais dele autoriza
--   anon            nao le nada de inteligencia
--
-- SERVICE_ROLE_KEY NUNCA vai para o frontend. O portal fala com um servidor,
-- e o servidor fala com o Supabase.
"""


def sql_rls_policies(d):
    linhas = []
    for t in d['TABLES']:
        linhas.append('ALTER TABLE %s ENABLE ROW LEVEL SECURITY;' % t['name'])
    linhas.append('')
    linhas.append('-- Isolamento por pais nas tabelas que tem country. As politicas'
                  '\n-- concretas entram com a autenticacao, na rodada de wiring.')
    for t in d['TABLES']:
        if any(c['name'] == 'country' for c in t['columns']):
            linhas.append('--   %s: filtrar por country' % t['name'])
    return '\n'.join(linhas)


def gerar(d):
    tabelas, fks = sql_tabelas(d)
    return '\n'.join([
        CABECALHO.format(schema=d['DB_SCHEMA']),
        sql_enums(d),
        tabelas,
        fks,
        sql_rls(d),
        sql_rls_policies(d),
        sql_views(d),
        sql_rpcs(d),
        '\nCOMMIT;',
        '',
    ])


DICIONARIO = os.path.join(RAIZ, 'docs', 'supabase', 'SUPABASE-DATA-DICTIONARY-EAME.md')


def gerar_dicionario(d):
    """O dicionario tambem e artefato. Escrever a mao criaria duas verdades."""
    m = medir(d)
    L = ['# DICIONÁRIO DE DADOS — SUPABASE SINTONIA EAME', '',
         '> **GERADO** por `scripts/supabase_schema.py` a partir de',
         '> `data/supabase/SUPABASE-CANONICAL-SCHEMA.json`. Não editar à mão.', '',
         '```',
         'SCHEMA_VERSION = %s        MIGRATION_APPLIED = NO' % d['SCHEMA_VERSION'],
         'TABELAS = %-3d  VIEWS = %-3d  RPCs = %-3d  ENUMS = %-3d'
         % (m['TABLES_TOTAL'], m['VIEWS_TOTAL'], m['RPCS_TOTAL'], m['ENUMS_TOTAL']),
         'COLUNAS = %-3d  CHECKS = %-3d  CHAVES ESTRANGEIRAS = %-3d'
         % (m['COLUMNS_TOTAL'], m['CHECKS_TOTAL'], m['FOREIGN_KEYS_TOTAL']),
         '```', '',
         '**Toda tabela tem um POR QUE.** Uma tabela sem justificativa é uma tabela que',
         'ninguém sabe defender quando alguém propuser fundi-la com outra.', '',
         '---', '', '## VOCABULÁRIOS FECHADOS', '']
    for nome, valores in d['VOCABULARIES'].items():
        L.append('**`%s`** — %s' % (nome, ' · '.join(valores)))
        L.append('')
    nao = d['NAO_PERSISTIR']
    L += ['### O que NÃO vira enum', '',
          '**`request_state`** — %s' % ' · '.join(nao['request_state']), '',
          '> %s' % nao['POR_QUE'], '',
          '**Onde vivem:** %s' % nao['ONDE_VIVEM'], '',
          '**O que fica no banco:** %s' % nao['O_QUE_FICA_NO_BANCO'], '',
          '---', '', '## TABELAS', '']
    for t in d['TABLES']:
        L.append('### `%s`' % t['name'])
        L.append('')
        L.append('%s' % t['purpose'])
        L.append('')
        L.append('> **Por quê:** %s' % t['why'])
        L.append('')
        if t.get('hose_id'):
            L.append('`HOSE_ID = %s` · `CANONICAL_PAYLOAD_TYPE = %s`'
                     % (t['hose_id'], t.get('canonical_payload_type', '—')))
            L.append('')
        if t.get('parent_hose_id'):
            L.append('`PARENT_HOSE_ID = %s` · `CANONICAL_PAYLOAD_TYPE = %s`'
                     % (t['parent_hose_id'], t.get('canonical_payload_type', '—')))
            L.append('')
        if t.get('privacy'):
            L.append('**Privacidade:** %s' % t['privacy'])
            L.append('')
        L.append('| coluna | tipo | nulo | nota |')
        L.append('|---|---|---|---|')
        pk = _pk(t)
        for c in t['columns']:
            nulo = 'não' if (c.get('null') is False or c.get('pk')) else 'sim'
            marca = ' 🔑' if c['name'] in pk else ''
            nota = c.get('note', '')
            if c.get('fk'):
                nota = ('→ `%s`' % c['fk']) + (' · ' + nota if nota else '')
            L.append('| `%s`%s | %s | %s | %s |' % (c['name'], marca, c['type'], nulo, nota))
        L.append('')
        for ck in t.get('checks', []):
            L.append('- **check `%s`** — `%s`' % (ck['name'], ck['expr']))
        if t.get('checks'):
            L.append('')
        if t.get('no_counter_column'):
            L.append('> ⚠️ %s' % t['no_counter_column'])
            L.append('')
    L += ['---', '', '## VIEWS', '']
    for v in d['VIEWS']:
        L.append('### `%s`' % v['name'])
        L.append('')
        L.append(v['purpose'])
        L.append('')
        if v.get('why'):
            L.append('> **Por quê:** %s' % v['why'])
            L.append('')
        L.append('**Lê:** %s' % ', '.join('`%s`' % r for r in v['reads']))
        if v.get('derives'):
            L.append('')
            L.append('**Deriva:** %s' % ', '.join('`%s`' % x for x in v['derives']))
        L.append('')
    L += ['---', '', '## RPCs', '']
    for r in d['RPCS']:
        L.append('### `%s(%s)`' % (r['name'], ', '.join(r['args'])))
        L.append('')
        L.append(r['purpose'])
        L.append('')
        L.append('**Retorna:** %s' % ', '.join('`%s`' % x for x in r['returns']))
        L.append('')
        if r.get('why'):
            L.append('> **Por quê:** %s' % r['why'])
            L.append('')
    p = d['LANGUAGE_FALLBACK_POLICY']
    L += ['---', '', '## POLÍTICA DE FALLBACK DE IDIOMA', '',
          '```', 'CADEIA: %s' % ' → '.join(p['CHAIN']), '```', '',
          p['REGRA'], '',
          '**Sempre declarado:** %s' % ' · '.join(p['SEMPRE_DECLARAR']), '',
          '**Nunca:** %s' % p['NUNCA'], '',
          '**Evidência:** %s' % p['EVIDENCIA'], '']
    led = d['LEDGER_DERIVATIONS']
    L += ['---', '', '## NÚMEROS DE LEDGER', '', led['REGRA'], '', '```']
    for k, v in led.items():
        if isinstance(v, dict):
            L.append('%-24s = %-8s  deriva de: %s' % (k, v['VALOR_CANONICO'], v['DERIVA_DE']))
    L += ['```', '', '**Onde mora a verdade:** %s' % led['ONDE_MORA_A_VERDADE'], '']
    return '\n'.join(L) + '\n'


def medir(d=None):
    d = d or carregar()
    tabelas = d['TABLES']
    por_hose = {}
    for t in tabelas:
        # so entra no mapa de mangueira quem declara payload canonico. Tabelas de
        # apoio (leituras da serie, conteudo futuro) tem hose_id e nao sao payload.
        if t.get('hose_id') and t.get('canonical_payload_type'):
            por_hose.setdefault(t['hose_id'], []).append(t['canonical_payload_type'])
    canonicos = {t.get('canonical_payload_type') for t in tabelas if t.get('canonical_payload_type')}
    aliases = {a['UI_ALIAS_INDEX11'] for a in d['UI_ALIAS_MAP']['MAP'] if a['UI_ALIAS_INDEX11']}
    return {
        'SCHEMA_VERSION': d['SCHEMA_VERSION'],
        'TABLES_TOTAL': len(tabelas),
        'VIEWS_TOTAL': len(d['VIEWS']),
        'RPCS_TOTAL': len(d['RPCS']),
        'ENUMS_TOTAL': len(d['VOCABULARIES']),
        'COLUMNS_TOTAL': sum(len(t['columns']) for t in tabelas),
        'CHECKS_TOTAL': sum(len(t.get('checks', [])) for t in tabelas),
        'FOREIGN_KEYS_TOTAL': sum(1 for t in tabelas for c in t['columns'] if c.get('fk')),
        'HOSE_PAYLOAD_TABLES': por_hose,
        'HOSES_MAPPED': sorted(por_hose),
        'SUBRECEPTOR_TABLES': [t['name'] for t in tabelas if t.get('parent_hose_id')],
        'CANONICAL_PAYLOAD_TYPES': sorted(canonicos),
        'ALIASES_NEVER_PERSISTED': sorted(aliases),
        'TABLES_WITHOUT_WHY': [t['name'] for t in tabelas if not t.get('why')],
        'TABLES_WITHOUT_PK': [t['name'] for t in tabelas if not _pk(t)],
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    d = carregar()
    if '--sync' in sys.argv:
        os.makedirs(os.path.dirname(MIGRATION), exist_ok=True)
        with open(MIGRATION, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(gerar(d))
        print('migration gravada em', os.path.relpath(MIGRATION, RAIZ))
        os.makedirs(os.path.dirname(DICIONARIO), exist_ok=True)
        with open(DICIONARIO, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(gerar_dicionario(d))
        print('dicionario gravado em', os.path.relpath(DICIONARIO, RAIZ))
    print(json.dumps(medir(d), ensure_ascii=False, indent=2))
