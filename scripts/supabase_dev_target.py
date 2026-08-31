"""Resolucao do alvo DEV: separar a existencia do projeto do meu acesso a ele.

CORRECAO DE SEMANTICA
---------------------
A rodada anterior declarou DEV_INSTANCE_AVAILABLE = NO porque esta maquina nao
tinha URL, chave, CLI, psql nem Docker. Isso foi uma conclusao errada a partir de
uma medicao certa: o que eu media era o MEU ACESSO, e o que eu declarava era a
EXISTENCIA DO BANCO. Sao duas coisas.

  SUPABASE_PROJECT_EXISTS      existe projeto na conta?          (medido pelo Luciano)
  CLAUDE_LOCAL_SUPABASE_ACCESS eu consigo abrir conexao daqui?   (medido por mim)
  DEV_INSTANCE_AVAILABLE       existe banco DEV UTILIZAVEL?      (depende do inventario)

O terceiro nao e nenhum dos dois: um projeto pode existir, estar saudavel, e ainda
assim NAO ser utilizavel como DEV — porque tem dado que alguem precisa.

E O QUE ESTE SCRIPT NAO FAZ
---------------------------
Nao inventaria o projeto. Nao ha credencial nesta maquina, e credencial nao e coisa
que eu deva manusear. O que ele entrega e o CONTRATO do inventario — as consultas
exatas, so de leitura — e o CLASSIFICADOR que transforma um inventario em veredito.
Quem tiver acesso roda as consultas, cola o resultado, e o classificador decide.

Uso:
    py scripts/supabase_dev_target.py            # imprime
    py scripts/supabase_dev_target.py --sync     # grava o artefato
"""
import json
import os
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-DEV-TARGET.json')

# Identidade informada pelo Luciano, medida por ele na conta. Nao verificavel daqui.
PROJETO = {
    'NAME': 'eame-sintonia',
    'PROJECT_REF': 'odhdwvugikjdvkapbowe',
    'REGION': 'eu-west-1',
    'STATUS': 'ACTIVE_HEALTHY',
    'MEDIDO_POR': 'Luciano, na conta Supabase',
    'VERIFICADO_POR_MIM': False,
    'POR_QUE_NAO': 'nao ha credencial nesta maquina, e credencial nao e coisa que eu manuseie',
}

# ── o contrato do inventario ────────────────────────────────────────────────
# Somente leitura. Nenhuma consulta escreve, cria, altera ou apaga.
INVENTARIO = [
    {'CHAVE': 'DATABASE_VERSION',
     'SQL': 'select version();',
     'PARA_QUE': 'saber contra que Postgres a migration vai rodar'},
    {'CHAVE': 'EXISTING_SCHEMAS',
     'SQL': ("select nspname from pg_namespace "
             "where nspname not like 'pg_%' and nspname <> 'information_schema' "
             "order by 1;"),
     'PARA_QUE': 'descobrir se ja existe um schema sintonia, ou outro em uso'},
    {'CHAVE': 'EXISTING_TABLES',
     'SQL': ("select table_schema, table_name from information_schema.tables "
             "where table_type = 'BASE TABLE' "
             "and table_schema not in ('pg_catalog','information_schema') order by 1,2;"),
     'PARA_QUE': 'toda tabela fora dos schemas de sistema'},
    {'CHAVE': 'EXISTING_VIEWS',
     'SQL': ("select table_schema, table_name from information_schema.views "
             "where table_schema not in ('pg_catalog','information_schema') order by 1,2;"),
     'PARA_QUE': 'views ja existentes'},
    {'CHAVE': 'EXISTING_FUNCTIONS',
     'SQL': ("select n.nspname, p.proname from pg_proc p "
             "join pg_namespace n on n.oid = p.pronamespace "
             "where n.nspname not in ('pg_catalog','information_schema') order by 1,2;"),
     'PARA_QUE': 'funcoes e RPCs ja existentes'},
    {'CHAVE': 'EXISTING_RLS_POLICIES',
     'SQL': 'select schemaname, tablename, policyname from pg_policies order by 1,2,3;',
     'PARA_QUE': 'politicas ja aplicadas — e se ha tabela sem nenhuma'},
    {'CHAVE': 'EXISTING_USER_DATA',
     'SQL': ("select schemaname, relname, n_live_tup from pg_stat_user_tables "
             "where n_live_tup > 0 order by n_live_tup desc;"),
     'PARA_QUE': ('a pergunta que decide tudo: ha LINHA em alguma tabela? '
                  'Tabela vazia e descartavel; tabela com linha e de alguem')},
    {'CHAVE': 'EXISTING_MIGRATION_HISTORY',
     'SQL': ("select version, name from supabase_migrations.schema_migrations "
             "order by version;  -- pode nao existir: ausencia tambem e resposta"),
     'PARA_QUE': 'saber se alguma migration ja correu neste projeto'},
    {'CHAVE': 'AUTH_USERS',
     'SQL': 'select count(*) from auth.users;',
     'PARA_QUE': ('usuario cadastrado e dado de gente. Um projeto com usuario NAO e '
                  'descartavel, mesmo com as tabelas vazias')},
    {'CHAVE': 'STORAGE_OBJECTS',
     'SQL': 'select count(*) from storage.objects;',
     'PARA_QUE': 'arquivo guardado tambem e dado de alguem'},
]

SCHEMAS_DE_SISTEMA = ('auth', 'storage', 'extensions', 'graphql', 'graphql_public',
                      'realtime', 'supabase_functions', 'supabase_migrations',
                      'vault', 'pgsodium', 'pgsodium_masks', 'net', 'cron', 'public')


def classificar(inv):
    """Transforma um inventario em veredito. Sem inventario, NEEDS_DECISION.

    Nunca devolve YES por ausencia de informacao: 'nao sei o que tem dentro' e
    o contrario de 'esta vazio'.
    """
    if inv is None:
        return {
            'SAFE_TO_USE_AS_DEV': 'NEEDS_DECISION',
            'DEV_INSTANCE_AVAILABLE': 'NOT_MEASURED',
            'WHY': ['inventario nao executado: sem acesso, sem leitura, sem veredito'],
            'MOTIVOS_DE_BLOQUEIO': [], 'MOTIVOS_DE_ATENCAO': [],
        }

    # Inventario INCOMPLETO nao e inventario limpo. Sem esta guarda, um dicionario
    # vazio passaria por "nada encontrado" e devolveria YES — que e exatamente a
    # regra que este classificador existe para nao violar.
    obrigatorias = ('EXISTING_SCHEMAS', 'EXISTING_TABLES', 'EXISTING_USER_DATA',
                    'AUTH_USERS', 'STORAGE_OBJECTS')
    ausentes = [k for k in obrigatorias if k not in inv]
    if ausentes:
        return {
            'SAFE_TO_USE_AS_DEV': 'NEEDS_DECISION',
            'DEV_INSTANCE_AVAILABLE': 'NOT_MEASURED',
            'WHY': ['inventario incompleto: faltam %s' % ', '.join(ausentes)],
            'MOTIVOS_DE_BLOQUEIO': [],
            'MOTIVOS_DE_ATENCAO': ['chave ausente nao e chave vazia'],
        }

    bloqueia, atencao = [], []

    if inv.get('AUTH_USERS', 0) > 0:
        bloqueia.append('ha %d usuario(s) em auth.users — projeto com gente dentro nao e '
                        'descartavel' % inv['AUTH_USERS'])
    if inv.get('STORAGE_OBJECTS', 0) > 0:
        bloqueia.append('ha %d objeto(s) em storage — arquivo guardado e dado de alguem'
                        % inv['STORAGE_OBJECTS'])

    com_linha = [t for t in inv.get('EXISTING_USER_DATA', [])
                 if t.get('n_live_tup', 0) > 0]
    if com_linha:
        bloqueia.append('%d tabela(s) com linhas: %s' % (
            len(com_linha), ', '.join('%s.%s(%d)' % (t['schemaname'], t['relname'],
                                                     t['n_live_tup'])
                                      for t in com_linha[:6])))

    proprios = [s for s in inv.get('EXISTING_SCHEMAS', [])
                if s not in SCHEMAS_DE_SISTEMA]
    alheios = [s for s in proprios if s != 'sintonia']
    if alheios:
        atencao.append('schema fora do sistema e fora do sintonia: %s' % alheios)

    tabelas = [t for t in inv.get('EXISTING_TABLES', [])
               if t.get('table_schema') not in SCHEMAS_DE_SISTEMA]
    if any(t.get('table_schema') == 'sintonia' for t in tabelas):
        atencao.append('ja existe schema sintonia com tabela: a migration nao pode '
                       'assumir banco limpo')

    historico = inv.get('EXISTING_MIGRATION_HISTORY')
    if historico:
        atencao.append('%d migration(s) ja aplicada(s) neste projeto' % len(historico))

    if bloqueia:
        veredito, disp = 'NO', 'NO'
    elif atencao:
        veredito, disp = 'NEEDS_DECISION', 'NOT_MEASURED'
    else:
        veredito, disp = 'YES', 'YES'

    return {
        'SAFE_TO_USE_AS_DEV': veredito,
        'DEV_INSTANCE_AVAILABLE': disp,
        'WHY': (bloqueia or atencao or
                ['nenhuma tabela com linha, nenhum usuario, nenhum objeto em storage, '
                 'nenhum schema alheio']),
        'MOTIVOS_DE_BLOQUEIO': bloqueia,
        'MOTIVOS_DE_ATENCAO': atencao,
    }


def acesso_local():
    envs = {k: bool(os.environ.get(k)) for k in
            ('SUPABASE_ACCESS_TOKEN', 'SUPABASE_SERVICE_ROLE_KEY', 'SUPABASE_ANON_KEY',
             'SUPABASE_DB_URL', 'SUPABASE_URL')}
    bins = {b: bool(shutil.which(b)) for b in ('supabase', 'psql', 'pg_dump', 'docker')}
    return {
        'ENV': envs, 'BIN': bins,
        'CLAUDE_LOCAL_SUPABASE_ACCESS': 'NO' if not any(envs.values()) else 'PARTIAL',
        'POR_QUE': ('sem token e sem cliente, nao ha como abrir conexao. E credencial nao '
                    'e coisa que eu deva manusear: quem tem acesso roda as consultas.'),
    }


def medir(inventario=None):
    cls = classificar(inventario)
    return {
        'SOURCE_ID': 'SUPABASE-DEV-TARGET-EAME-2026-08-31',
        'source': 'Resolucao do alvo DEV. Existencia do projeto e acesso local sao coisas diferentes.',
        'CORRECAO_DE_SEMANTICA': {
            'O_QUE_EU_DISSE_ANTES': 'DEV_INSTANCE_AVAILABLE = NO',
            'O_QUE_EU_TINHA_MEDIDO': 'ausencia de credencial e de cliente NESTA MAQUINA',
            'POR_QUE_ESTAVA_ERRADO': ('conclui sobre a EXISTENCIA do banco a partir de uma '
                                      'medicao do MEU ACESSO. Um projeto pode existir e '
                                      'estar saudavel sem eu conseguir ve-lo.'),
            'NOVA_DEFINICAO': ('DEV_INSTANCE_AVAILABLE = existe banco DEV UTILIZAVEL. '
                               'Depende do inventario, nao da minha credencial.'),
            'O_QUE_CONTINUA_VALENDO': ('CLAUDE_LOCAL_SUPABASE_ACCESS = NO. A medicao estava '
                                       'certa; o rotulo e que estava errado.'),
        },
        'PROJETO': PROJETO,
        'ACESSO_LOCAL': acesso_local(),
        'INVENTARIO_CONTRATO': INVENTARIO,
        'INVENTARIO_EXECUTADO': inventario is not None,
        'INVENTARIO': inventario,
        'CLASSIFICACAO': cls,
        'REGRA_DO_CLASSIFICADOR': {
            'BLOQUEIA': ['usuario em auth.users', 'objeto em storage',
                         'qualquer tabela com linha'],
            'ATENCAO': ['schema alheio', 'schema sintonia ja com tabela',
                        'migration ja aplicada'],
            'NUNCA': ('devolver YES por ausencia de informacao. "Nao sei o que tem dentro" '
                      'e o contrario de "esta vazio".'),
            'NOME_IGUAL_NAO_E_PROVA': ('o projeto se chamar eame-sintonia nao prova que e o '
                                       'ambiente certo, nem que esta vazio. So o inventario '
                                       'prova.'),
        },
        'MIGRATION_APPLIED_DEV': 'NO',
        'READY_TO_APPLY_MIGRATION_DEV': 'NO' if cls['SAFE_TO_USE_AS_DEV'] != 'YES' else 'YES',
    }


INVENTARIO_SQL = os.path.join(RAIZ, 'supabase', 'inventory',
                              '0000_readonly_inventory.sql')


def gerar_inventario_sql():
    """Um SQL so, de leitura, que devolve o inventario inteiro como JSON.

    Feito para ser colado no editor SQL do Supabase por quem tem acesso. Nao cria,
    nao altera, nao apaga: so SELECT. As duas ultimas consultas usam to_regclass
    porque a tabela pode nao existir — e a ausencia dela tambem e resposta.
    """
    L = [
        '-- INVENTARIO SOMENTE-LEITURA DO PROJETO CANDIDATO A DEV',
        '--',
        '-- GERADO por scripts/supabase_dev_target.py. Nao editar a mao.',
        '--',
        '-- Projeto: %s (%s · %s)' % (PROJETO['NAME'], PROJETO['PROJECT_REF'],
                                     PROJETO['REGION']),
        '--',
        '-- Este script NAO escreve nada. Nenhum CREATE, ALTER, INSERT, UPDATE ou DROP.',
        '-- Rode no editor SQL do projeto e devolva o JSON para',
        '-- scripts/supabase_dev_target.py classificar.',
        '',
        'select jsonb_pretty(jsonb_build_object(',
    ]
    partes = []
    for item in INVENTARIO:
        chave, sql = item['CHAVE'], item['SQL'].split('  --')[0].rstrip().rstrip(';')
        if chave in ('DATABASE_VERSION',):
            partes.append("  '%s', (%s)" % (chave, sql))
        elif chave in ('AUTH_USERS', 'STORAGE_OBJECTS'):
            tabela = 'auth.users' if chave == 'AUTH_USERS' else 'storage.objects'
            partes.append("  '%s', (select case when to_regclass('%s') is null "
                          "then null else (%s) end)" % (chave, tabela, sql))
        elif chave == 'EXISTING_MIGRATION_HISTORY':
            partes.append("  '%s', (select case when to_regclass"
                          "('supabase_migrations.schema_migrations') is null then null "
                          "else (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) "
                          "from (%s) t) end)" % (chave, sql))
        elif chave == 'EXISTING_SCHEMAS':
            partes.append("  '%s', (select coalesce(jsonb_agg(nspname), '[]'::jsonb) "
                          "from (%s) t)" % (chave, sql))
        else:
            partes.append("  '%s', (select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) "
                          "from (%s) t)" % (chave, sql))
    L.append(',\n'.join(partes))
    L.append(')) as inventario;')
    L.append('')
    return '\n'.join(L)


def preparar_aplicacao(inventario=None):
    """Portao antes de aplicar a migration. Recusa por padrao.

    Quatro condicoes, todas obrigatorias. Nenhuma delas e 'o nome do projeto bate'.
    """
    cls = classificar(inventario)
    recusas = []
    if cls['SAFE_TO_USE_AS_DEV'] != 'YES':
        recusas.append('SAFE_TO_USE_AS_DEV = %s' % cls['SAFE_TO_USE_AS_DEV'])
    if inventario is None:
        recusas.append('inventario nao executado')
    if acesso_local()['CLAUDE_LOCAL_SUPABASE_ACCESS'] != 'YES':
        recusas.append('sem acesso local: quem aplica e quem tem credencial')
    return {
        'PODE_APLICAR': not recusas,
        'RECUSAS': recusas,
        'ALVO': PROJETO['PROJECT_REF'],
        'CONFIRMAR_ANTES': ('o alvo NAO e producao — hoje nao existe projeto de producao '
                            'declarado, e por isso mesmo a checagem tem de ser explicita '
                            'quando existir'),
        'ORDEM_DE_APLICACAO': ['supabase/migrations/0001_initial_canonical_schema.sql'],
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    m['PORTAO_DE_APLICACAO'] = preparar_aplicacao()
    if '--sync' in sys.argv:
        os.makedirs(os.path.dirname(INVENTARIO_SQL), exist_ok=True)
        with open(INVENTARIO_SQL, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(gerar_inventario_sql())
        print('inventario SQL em', os.path.relpath(INVENTARIO_SQL, RAIZ))
    if '--sync' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado em', os.path.relpath(SAIDA, RAIZ))
    print(json.dumps({k: v for k, v in m.items() if k != 'INVENTARIO_CONTRATO'},
                     ensure_ascii=False, indent=2))
