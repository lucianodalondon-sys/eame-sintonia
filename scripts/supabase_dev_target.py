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
            'DATA_EMPTY': 'NOT_MEASURED',
            'SCHEMA_CLEAN': 'NOT_MEASURED',
            'SAFE_FOR_CANONICAL_MIGRATION': 'NO',   # nao medido nunca autoriza
            'WHY': ['inventario nao executado: sem acesso, sem leitura, sem veredito'],
            'MOTIVOS_DE_BLOQUEIO': [], 'MOTIVOS_DE_SCHEMA': [], 'MOTIVOS_DE_ATENCAO': [],
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

    # SEGUNDA DIMENSAO, e uma branch real me ensinou que ela existe.
    #
    # Ate aqui eu media DADO: usuario, arquivo, linha. Uma development branch criada
    # com WITH_DATA=false chegou com 0 linha, 0 arquivo, 0 usuario — e 51 tabelas,
    # 16 views, 20 funcoes e public.schema_migracao herdadas do pai. O meu
    # classificador respondeu YES. Estava errado pelo mesmo motivo de sempre, so que
    # do outro lado: ausencia de dado NAO e ausencia de schema.
    #
    # Banco vazio de dado e banco limpo de schema sao DUAS perguntas. A migration
    # canonica precisa das duas respondidas com sim.
    schema = []
    tabelas = [t for t in inv.get('EXISTING_TABLES', [])
               if t.get('table_schema') not in SCHEMAS_DE_SISTEMA]
    if any(t.get('table_schema') == 'sintonia' for t in tabelas):
        schema.append('ja existe schema sintonia com tabela: a migration nao pode '
                      'assumir banco limpo')

    # 'public' esta em SCHEMAS_DE_SISTEMA porque todo Postgres tem. Mas tabela DENTRO
    # de public nao vem com o Postgres: alguem criou.
    em_public = [t for t in inv.get('EXISTING_TABLES', [])
                 if t.get('table_schema') == 'public']
    n_public = inv.get('PUBLIC_TABLES', len(em_public))
    if n_public:
        schema.append('%d tabela(s) em public que nao sao minhas: o banco esta vazio '
                      'de dado e nao esta limpo de schema' % n_public)
    if inv.get('PUBLIC_VIEWS', 0) or inv.get('PUBLIC_FUNCTIONS', 0):
        schema.append('%d view(s) e %d funcao(oes) em public, herdadas'
                      % (inv.get('PUBLIC_VIEWS', 0), inv.get('PUBLIC_FUNCTIONS', 0)))

    historico = inv.get('EXISTING_MIGRATION_HISTORY')
    if historico:
        schema.append('%d migration(s) ja aplicada(s) neste projeto' % len(historico))
    if inv.get('SCHEMA_MIGRACAO_EXISTS'):
        schema.append('public.schema_migracao existe: o banco tem historia de '
                      'migration propria, e ela nao e a minha')

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
            'DATA_EMPTY': 'NOT_MEASURED',
            'SCHEMA_CLEAN': 'NOT_MEASURED',
            'SAFE_FOR_CANONICAL_MIGRATION': 'NO',
            'WHY': ['inventario incompleto: faltam %s' % ', '.join(ausentes)],
            'MOTIVOS_DE_BLOQUEIO': [], 'MOTIVOS_DE_SCHEMA': schema,
            'MOTIVOS_DE_ATENCAO': ['chave ausente nao e chave vazia'],
        }
    if ausentes:
        atencao.append('inventario parcial (faltam %s), mas ha bloqueio medido: o '
                       'veredito nao depende do que falta' % ', '.join(ausentes))

    if bloqueia:
        veredito, disp = 'NO', 'NO'
    elif atencao or schema:
        veredito, disp = 'NEEDS_DECISION', 'NOT_MEASURED'
    else:
        veredito, disp = 'YES', 'YES'

    # As duas perguntas, respondidas separado. Nenhuma responde pela outra.
    dado_vazio = 'NO' if bloqueia else 'YES'
    schema_limpo = 'NO' if schema else 'YES'
    pode_migrar = 'YES' if (dado_vazio == 'YES' and schema_limpo == 'YES') else 'NO'

    return {
        'SAFE_TO_USE_AS_DEV': veredito,
        'DEV_INSTANCE_AVAILABLE': disp,
        'DATA_EMPTY': dado_vazio,
        'SCHEMA_CLEAN': schema_limpo,
        'SAFE_FOR_CANONICAL_MIGRATION': pode_migrar,
        'WHY': (bloqueia or schema or atencao or
                ['sem linha, sem usuario, sem arquivo em storage, sem schema alheio, '
                 'e nenhuma tabela herdada em public']),
        'MOTIVOS_DE_BLOQUEIO': bloqueia,
        'MOTIVOS_DE_SCHEMA': schema,
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


# A branch foi criada, medida — e reprovada. Pelo motivo que estava escrito na
# opcao A antes de ela existir.
BRANCH = {
    'DEV_BRANCH': 'develop',
    'DEV_BRANCH_REF': 'hvtycqsrdtmxxodwcwph',
    'PARENT_PROJECT_REF': 'odhdwvugikjdvkapbowe',
    'WITH_DATA': False,
    'STATUS': 'ACTIVE_HEALTHY',
    'VERIFICADO_POR_MIM': False,
    'MEDIDO': {
        'PUBLIC_TABLES': 51, 'PUBLIC_VIEWS': 16, 'PUBLIC_FUNCTIONS': 20,
        'PUBLIC_POLICIES': 0, 'PUBLIC_TABLES_WITH_ROWS': 0,
        'STORAGE_OBJECTS': 0, 'AUTH_USERS': 0, 'SCHEMA_MIGRACAO_EXISTS': True,
    },
    'DEV_BRANCH_DATA_EMPTY': 'YES',
    'DEV_BRANCH_SCHEMA_CLEAN': 'NO',
    'DEV_BRANCH_SAFE_FOR_CANONICAL_MIGRATION': 'NO',
    'O_QUE_ISSO_ENSINOU': (
        'WITH_DATA=false barrou o DADO e nao barrou o SCHEMA. A branch chegou com 0 '
        'linha, 0 arquivo, 0 usuario — e 51 tabelas, 16 views, 20 funcoes e '
        'public.schema_migracao herdados do pai. Vazio de dado nao e limpo de schema.'),
    'BUG_QUE_ISSO_ACHOU': (
        'o classificador media so dado, e por isso devolveu YES para esta branch. '
        'Corrigido: DATA_EMPTY e SCHEMA_CLEAN sao duas perguntas, e '
        'SAFE_FOR_CANONICAL_MIGRATION exige as duas com sim.'),
    'O_QUE_NAO_FAZER': ['nao aplicar a migration canonica aqui',
                        'nao limpar a branch', 'nao dar DROP para abrir espaco',
                        'nao adaptar a migration ao schema legado',
                        'nao tocar no parent'],
}

DEV_TARGET = {
    'DEV_TARGET_STRATEGY': 'NEW_PROJECT',
    'DEV_TARGET_CREATED': 'YES',
    'DEV_PROJECT_REF': 'xhqebdweltytnghiavew',
    'DEV_PROJECT_NAME': 'eame-sintonia-dev',
    'DEV_REGION': 'eu-west-1',
    'DEV_STATUS': 'ACTIVE_HEALTHY',
    'DEV_VERIFICADO_POR_MIM': False,
    'DEV_POR_QUE_NAO_VERIFICADO': ('a existencia foi informada pelo Luciano e medida na '
                                   'conta. Nao ha credencial nesta maquina. Existir nao e '
                                   'estar limpo: o inventario 0000 e que decide.'),
    'DEV_INVENTARIO_EXECUTADO': 'NO',
    'DEV_DATA_EMPTY': 'NOT_MEASURED',
    'DEV_SCHEMA_CLEAN': 'NOT_MEASURED',
    'POR_QUE_AGORA_TEM_ESTRATEGIA': (
        'a decisao deixou de ser preferencia: a opcao A foi tentada e medida. A branch '
        'herdou schema e historia de migration do pai, exatamente como o contra da '
        'opcao A dizia. Sobra B, e o projeto B foi criado: xhqebdweltytnghiavew.'),
    'O_QUE_TER_O_REF_NAO_PROVA': (
        'ter REF proprio satisfaz UM dos sete requisitos. Nao prova DATA_EMPTY nem '
        'SCHEMA_CLEAN. A branch reprovada tambem tinha REF proprio.'),
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
        'NAO_E_DECISAO': ('era recomendacao quando foi escrita, e nada tinha sido criado. '
                          'O projeto B existe desde 31/08/2026: xhqebdweltytnghiavew. '
                          'Existir nao e estar limpo — quem responde isso e o 0000.'),
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
        '-- Projeto: %s (%s · %s)' % (DEV_TARGET['DEV_PROJECT_NAME'],
                                     DEV_TARGET['DEV_PROJECT_REF'],
                                     DEV_TARGET['DEV_REGION']),
        '--',
        '-- Este bloco entrega a EVIDENCIA bruta. O veredito separado (DATA_EMPTY e',
        '-- SCHEMA_CLEAN) sai do segundo bloco, no fim do arquivo.',
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
    L.append(gerar_veredito_sql())
    return '\n'.join(L)


def gerar_veredito_sql():
    """O bloco que responde as DUAS perguntas separadas, sem confundir uma com a outra.

    O BUG QUE ESTE BLOCO EXISTE PARA NAO REPETIR
    --------------------------------------------
    Um banco Supabase recem-criado JA VEM com schemas e tabelas: auth, storage,
    extensions, realtime, vault, supabase_migrations. Contar isso como sujeira
    reprovaria todo projeto novo — inclusive um limpo. E ignorar tudo aprovaria a
    branch reprovada, que tinha 51 tabelas herdadas em public.

    A regra, entao: so conta estrutura de APLICACAO.
      · qualquer schema fora da lista de sistema
      · qualquer tabela, view ou funcao DENTRO de public — public vem com o
        Postgres, o que esta dentro dele nao vem
      · o schema sintonia, que e o meu e nao deveria existir ainda
      · migration ja registrada em supabase_migrations.schema_migrations

    E o que pertence a uma EXTENSAO nao conta: `create extension` poe objeto em
    public sem que ninguem tenha modelado nada. pg_depend deptype='e' separa os dois.

    LINHA CONTADA DE VERDADE
    ------------------------
    pg_stat_user_tables.n_live_tup e ESTIMATIVA do coletor de estatisticas. Numa
    tabela recem-carregada, antes do autovacuum passar, ela pode dizer 0 tendo
    linha dentro. Um 'vazio' falso aqui autorizaria a migration em cima de dado de
    alguem. Por isso a contagem que decide e count(*) real, via query_to_xml, e a
    estimativa fica ao lado so para comparacao.
    """
    return '''
-- ── VEREDITO: DATA_EMPTY e SCHEMA_CLEAN, respondidos SEPARADO ──────────
--
-- Tambem somente leitura. Rode depois do bloco de cima, no mesmo projeto.
--
-- Um Supabase novo ja nasce com auth, storage, extensions, realtime, vault e
-- supabase_migrations. Isso e o banco, nao e sujeira. So conta estrutura de
-- APLICACAO: schema fora dessa lista, ou objeto criado dentro de public.
--
-- A contagem de linhas e count(*) real, nao n_live_tup: a estimativa pode dizer
-- zero numa tabela cheia enquanto o autovacuum nao passa, e um zero falso aqui
-- autorizaria a migration em cima do dado de alguem.

with sistema(nspname) as (values (%(sistema_values)s)),
app_ns as (
  select n.oid, n.nspname
    from pg_namespace n
   where n.nspname not like 'pg\\_%%'
     and n.nspname <> 'information_schema'
     and n.nspname not in (select nspname from sistema)
),
app_rel as (
  select n.nspname as schema_name, c.relname, c.relkind
    from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
   where c.relkind in ('r','p','v','m')
     and (n.nspname = 'public' or n.oid in (select oid from app_ns))
     and not exists (select 1 from pg_depend d
                      where d.objid = c.oid and d.deptype = 'e')
),
app_proc as (
  select n.nspname as schema_name, p.proname
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
   where (n.nspname = 'public' or n.oid in (select oid from app_ns))
     and not exists (select 1 from pg_depend d
                      where d.objid = p.oid and d.deptype = 'e')
),
app_linhas as (
  select r.schema_name, r.relname,
         (xpath('/row/c/text()',
                query_to_xml(format('select count(*) as c from %%I.%%I',
                                    r.schema_name, r.relname),
                             false, true, '')))[1]::text::bigint as linhas_reais
    from app_rel r
   where r.relkind in ('r','p')
),
migracoes as (
  select case when to_regclass('supabase_migrations.schema_migrations') is null
              then 0
              else (select count(*) from supabase_migrations.schema_migrations)
         end as n
),
usuarios as (
  select case when to_regclass('auth.users') is null then 0
              else (select count(*) from auth.users) end as n
),
arquivos as (
  select case when to_regclass('storage.objects') is null then 0
              else (select count(*) from storage.objects) end as n
),
medido as (
  select
    (select n from usuarios)                                        as auth_users,
    (select n from arquivos)                                        as storage_objects,
    (select coalesce(sum(linhas_reais), 0) from app_linhas)          as linhas_app,
    (select coalesce(jsonb_agg(to_jsonb(t) order by t.linhas_reais desc), '[]'::jsonb)
       from (select * from app_linhas where linhas_reais > 0) t)     as tabelas_com_linha,
    (select coalesce(jsonb_agg(nspname order by nspname), '[]'::jsonb)
       from app_ns)                                                  as schemas_de_aplicacao,
    (select coalesce(jsonb_agg(to_jsonb(t) order by t.schema_name, t.relname), '[]'::jsonb)
       from app_rel t)                                               as objetos_de_aplicacao,
    (select coalesce(jsonb_agg(to_jsonb(t) order by t.schema_name, t.proname), '[]'::jsonb)
       from app_proc t)                                              as funcoes_de_aplicacao,
    (select n from migracoes)                                        as migrations_registradas,
    (select count(*) from app_ns where nspname = 'sintonia')          as schema_sintonia
),
julgado as (
  select m.*,
    (m.auth_users = 0 and m.storage_objects = 0 and m.linhas_app = 0)      as dado_vazio,
    (jsonb_array_length(m.schemas_de_aplicacao) = 0
     and jsonb_array_length(m.objetos_de_aplicacao) = 0
     and jsonb_array_length(m.funcoes_de_aplicacao) = 0
     and m.migrations_registradas = 0)                                     as schema_limpo
    from medido m
)
select jsonb_pretty(jsonb_build_object(
  'DEV_PROJECT_REF_ESPERADO', '%(ref)s',
  'CONFERIR_O_REF_ANTES_DE_ACREDITAR', 'este SQL nao sabe em que projeto esta rodando: quem cola confere',
  'EVIDENCIA_DE_DADO', jsonb_build_object(
    'AUTH_USERS', j.auth_users,
    'STORAGE_OBJECTS', j.storage_objects,
    'LINHAS_EM_TABELAS_DE_APLICACAO', j.linhas_app,
    'TABELAS_COM_LINHA', j.tabelas_com_linha,
    'COMO_FOI_CONTADO', 'count(*) real por tabela, nao n_live_tup estimado'),
  'EVIDENCIA_DE_SCHEMA', jsonb_build_object(
    'SCHEMAS_DE_APLICACAO', j.schemas_de_aplicacao,
    'OBJETOS_DE_APLICACAO', j.objetos_de_aplicacao,
    'FUNCOES_DE_APLICACAO', j.funcoes_de_aplicacao,
    'MIGRATIONS_REGISTRADAS', j.migrations_registradas,
    'SCHEMA_SINTONIA_JA_EXISTE', j.schema_sintonia > 0,
    'O_QUE_NAO_FOI_CONTADO', 'auth, storage, extensions, realtime, vault, supabase_migrations e objetos de extensao: isso e o Supabase, nao e sujeira'),
  'DATA_EMPTY', case when j.dado_vazio then 'YES' else 'NO' end,
  'SCHEMA_CLEAN', case when j.schema_limpo then 'YES' else 'NO' end,
  'SAFE_FOR_CANONICAL_MIGRATION',
     case when j.dado_vazio and j.schema_limpo then 'YES' else 'NO' end,
  'REGRA', 'as duas perguntas sao independentes, e a migration exige as duas com YES. Vazio de dado nao e limpo de schema — foi assim que a branch hvtycqsrdtmxxodwcwph passou errado uma vez'
)) as veredito
  from julgado j;
''' % {'sistema_values': '), ('.join("'%s'" % s for s in SCHEMAS_DE_SISTEMA),
       'ref': DEV_TARGET['DEV_PROJECT_REF']}


# Dois REFs medidos e reprovados. A lista nao e conselho: e recusa.
REFS_RECUSADOS = {
    'odhdwvugikjdvkapbowe': 'parent: 732 objetos em storage e 19 tabelas com dado',
    'hvtycqsrdtmxxodwcwph': 'branch develop: vazia de dado, suja de schema — 51 tabelas '
                            'herdadas e public.schema_migracao',
}


def preparar_aplicacao(inventario=None, ref=None):
    """Portao antes de aplicar a migration. Recusa por padrao.

    Cinco condicoes, todas obrigatorias. Nenhuma delas e 'o nome do projeto bate'.
    """
    cls = classificar(inventario)
    recusas = []
    if ref in REFS_RECUSADOS:
        recusas.append('alvo %s esta na lista de recusados: %s'
                       % (ref, REFS_RECUSADOS[ref]))
    if ref is None:
        recusas.append('nenhum DEV_PROJECT_REF limpo foi informado')
    if cls['SAFE_TO_USE_AS_DEV'] != 'YES':
        recusas.append('SAFE_TO_USE_AS_DEV = %s' % cls['SAFE_TO_USE_AS_DEV'])
    if cls['SAFE_FOR_CANONICAL_MIGRATION'] != 'YES':
        recusas.append('SAFE_FOR_CANONICAL_MIGRATION = %s (DATA_EMPTY = %s, '
                       'SCHEMA_CLEAN = %s)' % (cls['SAFE_FOR_CANONICAL_MIGRATION'],
                                               cls['DATA_EMPTY'], cls['SCHEMA_CLEAN']))
    if inventario is None:
        recusas.append('inventario nao executado')
    if acesso_local()['CLAUDE_LOCAL_SUPABASE_ACCESS'] != 'YES':
        recusas.append('sem acesso local: quem aplica e quem tem credencial')
    return {
        'PODE_APLICAR': not recusas,
        'RECUSAS': recusas,
        'ALVO': ref,
        'REFS_RECUSADOS': REFS_RECUSADOS,
        'CONFIRMAR_ANTES': ('o alvo NAO e producao — hoje nao existe projeto de producao '
                            'declarado, e por isso mesmo a checagem tem de ser explicita '
                            'quando existir'),
        'ORDEM_DE_APLICACAO': ['supabase/migrations/0001_initial_canonical_schema.sql'],
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir(INVENTARIO_MEDIDO)
    m['BRANCH_MEDIDA'] = BRANCH
    m['BRANCH_CLASSIFICADA'] = classificar({
        'EXISTING_SCHEMAS': ['public'], 'EXISTING_TABLES': [], 'EXISTING_USER_DATA': [],
        'AUTH_USERS': 0, 'STORAGE_OBJECTS': 0, **BRANCH['MEDIDO']})
    m['PORTAO_DE_APLICACAO'] = preparar_aplicacao(INVENTARIO_MEDIDO,
                                                  BRANCH['DEV_BRANCH_REF'])
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
