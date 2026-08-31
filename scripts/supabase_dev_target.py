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

# ── inventario MEDIDO por acesso autorizado, fora desta maquina ──────────────
# Recebido pronto. Nao foi eu quem rodou; registrado como medicao externa.
TABELAS_COM_LINHA = {
    'catalogo_captura': 1, 'catalogo_produto': 56, 'catalogo_produto_agente': 176,
    'catalogo_produto_claim': 35, 'catalogo_produto_cultivo': 711,
    'catalogo_produto_cultivo_agente': 5, 'catalogo_produto_cultivo_dose': 26,
    'catalogo_produto_documento': 147, 'catalogo_produto_janela_aplicacao': 3,
    'catalogo_produto_modo_acao': 17, 'catalogo_produto_relacao': 1,
    'catalogo_produto_substancia': 73, 'catalogo_produto_tecnologia': 1,
    'catalogo_registro_crosswalk': 108, 'catalogo_termo_ambiguo': 210,
    'collection_run': 4, 'raw_asset': 245, 'registro_regulatorio': 96,
    'schema_migracao': 17,
}

INVENTARIO_MEDIDO = {
    'MEDIDO_POR': 'acesso autorizado, fora desta maquina',
    'EXECUTADO_POR_MIM': False,
    'AUTH_USERS': 0,
    'STORAGE_BUCKETS': 1,
    'STORAGE_OBJECTS': 732,
    'PUBLIC_VIEWS': 16,
    'PUBLIC_FUNCTIONS': 20,
    'PUBLIC_POLICIES': 0,
    'PUBLIC_TABLES_WITH_ROWS': 19,
    'SUPABASE_DEVELOPMENT_BRANCHES_EXISTING': 0,
    'EXISTING_USER_DATA': [{'schemaname': 'public', 'relname': k, 'n_live_tup': v}
                           for k, v in TABELAS_COM_LINHA.items()],
    'LINHAS_TOTAIS': sum(TABELAS_COM_LINHA.values()),
    'NAO_RECEBIDO': ['EXISTING_SCHEMAS', 'EXISTING_TABLES (lista)', 'EXISTING_VIEWS (lista)',
                     'EXISTING_FUNCTIONS (lista)', 'EXISTING_MIGRATION_HISTORY',
                     'DATABASE_VERSION'],
}


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

    # ORDEM QUE IMPORTA, e que um inventario real corrigiu:
    # evidencia que bloqueia vence a incompletude. "Nao sei tudo, mas sei que ha
    # 732 arquivos la dentro" e NAO, nao e "precisa decidir". A guarda de
    # completude so vale quando NADA bloqueia — la e que a ausencia de informacao
    # poderia virar um YES indevido.
    obrigatorias = ('EXISTING_SCHEMAS', 'EXISTING_TABLES', 'EXISTING_USER_DATA',
                    'AUTH_USERS', 'STORAGE_OBJECTS')
    ausentes = [k for k in obrigatorias if k not in inv]
    if not bloqueia and ausentes:
        return {
            'SAFE_TO_USE_AS_DEV': 'NEEDS_DECISION',
            'DEV_INSTANCE_AVAILABLE': 'NOT_MEASURED',
            'WHY': ['inventario incompleto: faltam %s' % ', '.join(ausentes)],
            'MOTIVOS_DE_BLOQUEIO': [],
            'MOTIVOS_DE_ATENCAO': ['chave ausente nao e chave vazia'],
        }
    if ausentes:
        atencao.append('inventario parcial (faltam %s), mas ha bloqueio medido: o '
                       'veredito nao depende do que falta' % ', '.join(ausentes))

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


DEV_TARGET = {
    'DEV_TARGET_STRATEGY': 'NEEDS_DECISION',
    'DEV_TARGET_CREATED': 'NO',
    'POR_QUE_NAO_ESCOLHI': ('o briefing proibe escolher em silencio, e as duas opcoes '
                            'tem custo e consequencia diferentes. A recomendacao esta '
                            'abaixo com o motivo; a decisao e do Luciano.'),
    'OPCOES': [
        {
            'ID': 'A', 'NOME': 'Supabase Development Branch a partir do projeto existente',
            'EXIGE': ['plano que ofereca branching', 'projeto ligado a um repositorio Git',
                      'custo por branch aceito'],
            'CONTRA_MEDIDO': (
                'a branch nasce do projeto pai, e o pai tem 17 linhas em schema_migracao '
                'e 19 tabelas com dado. A migration canonica cairia em cima de um schema '
                'que NAO esta limpo — que e exatamente o que o proprio classificador marca '
                'como "nao pode assumir banco limpo". E o requisito "nao carregar '
                'production data automaticamente" fica dependendo de configuracao, em vez '
                'de ser garantido pela origem.'),
            'A_FAVOR': 'nasce ligada ao projeto real, e some quando a branch some',
        },
        {
            'ID': 'B', 'NOME': 'novo projeto Supabase DEV separado',
            'EXIGE': ['criar projeto', 'PROJECT_REF proprio', 'nome que se leia como DEV'],
            'A_FAVOR_MEDIDO': (
                'nasce vazio por construcao: nenhum dado de producao pode vir junto porque '
                'nao ha de onde vir. Nenhuma historia de migration para colidir. E o '
                'isolamento nao depende de configuracao — depende de ser outro projeto.'),
            'CONTRA': 'mais um projeto para manter, e outro conjunto de chaves para guardar',
        },
    ],
    'RECOMENDACAO': {
        'ESCOLHA': 'B',
        'POR_QUE': ('nao e preferencia: e o inventario. O projeto existente tem 17 '
                    'migrations aplicadas e 19 tabelas com linha. Uma branch herdaria as '
                    'duas coisas, e a migration canonica pousaria sobre schema ocupado. '
                    'Um projeto novo comeca vazio porque nao ha de onde herdar.'),
        'NAO_E_DECISAO': 'e recomendacao. Nada foi criado.',
    },
    'REQUISITOS_DO_AMBIENTE_DEV': [
        'nao carregar dado de producao automaticamente — nem por copia, nem por seed',
        'receber SOMENTE migrations',
        'ser explicitamente descartavel: apagar e recriar nao pode doer',
        'ter PROJECT_REF proprio, diferente de odhdwvugikjdvkapbowe',
        'nome que se leia como DEV sem precisar consultar ninguem',
        'service role NUNCA no frontend: a chave vai para um servidor',
        'ser identificavel como DEV pelo proprio REF, nao so pelo nome',
    ],
    'O_QUE_NAO_FAZER_COM_O_PROJETO_EXISTENTE': [
        'nao aplicar a migration canonica nele',
        'nao limpar', 'nao apagar', 'nao reutilizar como sandbox descartavel',
    ],
}

ACHADOS_DO_INVENTARIO = [
    {
        'ACHADO': 'PUBLIC_POLICIES = 0 com 19 tabelas contendo dado',
        'POR_QUE_IMPORTA': ('sem politica, o acesso depende de RLS estar desligada ou de '
                            'GRANT. Num projeto Supabase, tabela sem RLS fica legivel pela '
                            'chave anonima. Nao e o meu projeto e nao vou mexer — mas e um '
                            'fato medido que alguem precisa olhar.'),
        'ACAO': 'reportar; nenhuma alteracao feita',
    },
    {
        'ACHADO': ('os nomes das tabelas sao do dominio SINTONIA: catalogo_produto, '
                   'registro_regulatorio, raw_asset, collection_run'),
        'POR_QUE_IMPORTA': ('isto nao parece um projeto alheio: parece uma implementacao '
                            'anterior ou paralela do proprio SINTONIA. Se for, o dado la '
                            'dentro pode ter valor, e a relacao dele com o modelo canonico '
                            'desta rodada e uma pergunta em aberto — nao uma coincidencia '
                            'de nome.'),
        'ACAO': 'pergunta aberta; nao resolvida por palpite',
    },
    {
        'ACHADO': 'schema_migracao = 17',
        'POR_QUE_IMPORTA': ('o projeto tem historia de migration propria. Qualquer branch '
                            'dele herda essa historia, e a migration canonica nao pousaria '
                            'em banco limpo.'),
        'ACAO': 'e o argumento tecnico que sustenta a recomendacao B',
    },
]


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
        'ACHADOS_DO_INVENTARIO': ACHADOS_DO_INVENTARIO,
        'DEV_TARGET': DEV_TARGET,
        'EXISTING_PROJECT_AVAILABLE': 'YES',
        'EXISTING_PROJECT_SAFE_AS_DEV': cls['SAFE_TO_USE_AS_DEV'],
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
    m = medir(INVENTARIO_MEDIDO)
    m['PORTAO_DE_APLICACAO'] = preparar_aplicacao(INVENTARIO_MEDIDO)
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
