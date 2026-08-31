"""Corta a migration canonica em pedacos executaveis SEM mexer no que ela diz.

POR QUE CORTAR
--------------
O editor SQL do Supabase engasga com um arquivo de 118 mil caracteres. Cortar e
uma necessidade de FERRAMENTA, nao uma decisao de modelagem. Entao a regra que
manda aqui e negativa: nada pode mudar de sentido no caminho.

O QUE E UM CORTE SEGURO
-----------------------
Fronteira entre dois comandos de topo, e so isso. Nunca dentro de um CREATE
TABLE, de um corpo $$...$$, de uma VIEW ou de uma POLICY. Para saber onde um
comando termina, este arquivo LE o SQL de verdade: aspas simples, comentario de
linha, comentario de bloco e dollar-quoting com etiqueta ($$, $fn$, $neg$). Um
`split(';')` ingenuo cortaria no meio do primeiro corpo de funcao que tivesse um
ponto-e-virgula dentro — e sao cinco.

COMO A PROVA FUNCIONA
---------------------
Cada arquivo tem um CORPO delimitado por duas marcas. O corpo e uma FATIA LITERAL
do original — nao uma reescrita, nao uma reindentacao: `original[inicio:fim]`.
Concatenar os corpos na ordem tem de devolver o original inteiro, byte a byte,
menos as duas linhas `BEGIN;` e `COMMIT;` que envolviam tudo.

O que fica FORA do corpo e andaime: o cabecalho comentado, o `BEGIN;`/`COMMIT;`
proprio de cada pedaco e o `SET search_path`, que precisa ser repetido porque
cada arquivo roda numa sessao diferente. Andaime nao entra na prova porque
andaime nao e conteudo — e por isso ele vive fora das marcas, onde da para ver.

O QUE ESTE ARQUIVO NAO FAZ
--------------------------
Nao executa nada. Nao corrige SQL. Nao toca no JSON da autoridade. Se um bloco
estiver errado, o erro ja estava no original — e o lugar de consertar continua
sendo data/supabase/SUPABASE-CANONICAL-SCHEMA.json, com a migration regerada.

Uso:
    py scripts/supabase_execution_split.py            # imprime o manifesto
    py scripts/supabase_execution_split.py --sync     # grava os arquivos
"""
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANONICA = os.path.join(RAIZ, 'supabase', 'migrations',
                        '0001_initial_canonical_schema.sql')
DESTINO = os.path.join(RAIZ, 'supabase', 'execution')
MANIFESTO = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-EXECUTION-MANIFEST.json')

CANONICAL_0001_SHA256 = '41ffeb52941718a34a01135e2f76bc4611a2978e049175f90cf4014117e335ec'
DEV_PROJECT_REF = 'xhqebdweltytnghiavew'

# As duas marcas que separam conteudo de andaime. Tudo entre elas e fatia literal
# do original; tudo fora delas foi acrescentado por este script.
MARCA_INICIO = '-- >>> CORPO CANONICO — FATIA LITERAL DE 0001, NAO EDITAR >>>'
MARCA_FIM = '-- <<< FIM DO CORPO CANONICO <<<'


def ler_canonica():
    with open(CANONICA, encoding='utf-8', newline='') as fh:
        return fh.read()


def sha(txt):
    return hashlib.sha256(txt.encode('utf-8')).hexdigest()


# ── leitor de statements ─────────────────────────────────────────────────────
def statements(sql):
    """Devolve [(inicio, fim)] de cada comando de topo, fim logo apos o ';'.

    Le o texto uma vez, caractere a caractere, sabendo em que estado esta:
    texto normal, string entre aspas, comentario de linha, comentario de bloco,
    ou dentro de um corpo $etiqueta$. Ponto-e-virgula so encerra comando quando
    o estado e texto normal.
    """
    fora = []
    i, n = 0, len(sql)
    inicio = 0
    while i < n:
        c = sql[i]
        if c == '-' and sql[i:i + 2] == '--':
            j = sql.find('\n', i)
            i = n if j < 0 else j + 1
            continue
        if c == '/' and sql[i:i + 2] == '/*':
            j = sql.find('*/', i + 2)
            i = n if j < 0 else j + 2
            continue
        if c == "'":
            i += 1
            while i < n:
                if sql[i] == "'":
                    if sql[i:i + 2] == "''":   # aspas escapada dentro da string
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue
        if c == '"':
            j = sql.find('"', i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == '$':
            etiqueta = _etiqueta_dollar(sql, i)
            if etiqueta is not None:
                j = sql.find(etiqueta, i + len(etiqueta))
                i = n if j < 0 else j + len(etiqueta)
                continue
        if c == ';':
            fora.append((inicio, i + 1))
            i += 1
            # o resto da linha (comentario de rodape) pertence ao comando
            while i < n and sql[i] in ' \t':
                i += 1
            if sql[i:i + 2] == '--':
                j = sql.find('\n', i)
                i = n if j < 0 else j
                fora[-1] = (fora[-1][0], i)
            inicio = i
            continue
        i += 1
    resto = sql[inicio:].strip()
    if resto:
        fora.append((inicio, n))
    return fora


def _etiqueta_dollar(sql, i):
    """'$$' ou '$fn$' quando o que vem em i abre um corpo; None se nao abre."""
    j = i + 1
    while j < len(sql) and (sql[j].isalnum() or sql[j] == '_'):
        j += 1
    if j < len(sql) and sql[j] == '$':
        return sql[i:j + 1]
    return None


def _corpo_do_statement(texto):
    """Tira os comentarios que vieram grudados antes do comando.

    A fatia de cada statement comeca onde o anterior terminou, entao ela carrega
    junto os comentarios de cabecalho — que no arquivo canonico sao varias linhas
    explicando cada tabela. Para descobrir o TIPO e o ALVO, eles atrapalham; para
    a prova de reconstrucao, eles sao conteudo e ficam onde estao.
    """
    t = texto.lstrip()
    while t.startswith('--'):
        t = t.split('\n', 1)[1].lstrip() if '\n' in t else ''
    return t


def _offset_do_comando(sql, ini, fim):
    """Onde o comando de fato comeca dentro da fatia, pulando comentario e branco."""
    i = ini
    while i < fim:
        while i < fim and sql[i] in ' \t\r\n':
            i += 1
        if sql[i:i + 2] == '--':
            j = sql.find('\n', i)
            i = fim if j < 0 else j + 1
            continue
        break
    return i


def _tipo(texto):
    limpo = _corpo_do_statement(texto)
    # O rabo do arquivo e uma nota sobre fallback de idioma, sem comando nenhum.
    # Ele e conteudo e vai para o bloco e inteiro, mas nao e um statement: contar
    # como statement daria 444 onde ha 443 comandos.
    if not limpo.strip():
        return 'COMENTARIO'
    u = ' '.join(limpo.upper().split())
    for prefixo, nome in (
            ('BEGIN;', 'BEGIN'), ('COMMIT;', 'COMMIT'),
            ('SET SEARCH_PATH', 'SET'), ('CREATE SCHEMA', 'CREATE SCHEMA'),
            ('CREATE TYPE', 'CREATE TYPE'), ('CREATE TABLE', 'CREATE TABLE'),
            ('ALTER TABLE', 'ALTER TABLE'), ('CREATE UNIQUE INDEX', 'CREATE INDEX'),
            ('CREATE INDEX', 'CREATE INDEX'), ('DO ', 'DO'),
            ('CREATE POLICY', 'CREATE POLICY'),
            ('CREATE OR REPLACE FUNCTION', 'CREATE FUNCTION'),
            ('CREATE FUNCTION', 'CREATE FUNCTION'),
            ('CREATE OR REPLACE VIEW', 'CREATE VIEW'), ('CREATE VIEW', 'CREATE VIEW'),
            ('GRANT ', 'GRANT'), ('REVOKE ', 'REVOKE'), ('COMMENT ', 'COMMENT')):
        if u.startswith(prefixo):
            return nome
    return 'OUTRO'


def _alvo(texto, tipo):
    """Nome do objeto, so para o mapa ficar legivel. Nao entra na prova."""
    t = ' '.join(_corpo_do_statement(texto).split())
    for pref in ('CREATE OR REPLACE FUNCTION ', 'CREATE OR REPLACE VIEW ',
                 'CREATE TABLE ', 'CREATE TYPE ', 'CREATE POLICY ',
                 'CREATE UNIQUE INDEX ', 'CREATE INDEX ', 'ALTER TABLE ',
                 'CREATE SCHEMA '):
        if t.upper().startswith(pref):
            resto = t[len(pref):]
            return resto.split('(')[0].split(' ')[0].strip()
    return tipo


def mapear():
    sql = ler_canonica()
    fatias = []
    for ini, fim in statements(sql):
        texto = sql[ini:fim]
        tipo = _tipo(texto)
        fatias.append({'INI': ini, 'FIM': fim, 'TIPO': tipo,
                       'ALVO': _alvo(texto, tipo),
                       'LINHA': sql.count('\n', 0, ini) + 1})
    return sql, fatias


# ── divisao em blocos ────────────────────────────────────────────────────────
# Cinco pedacos, e cada corte cai numa fronteira que o proprio SQL ja tinha.
# A ordem NAO e escolha de gosto: e a ordem de dependencia do Postgres.
#   a  o que ja foi aplicado: schema, enums e as quatro primeiras tabelas
#   b  o resto das tabelas — nenhuma FK ainda, entao a ordem entre elas nao pesa
#   c  as FKs (ALTER TABLE) e os indices: precisam de todas as tabelas de pe
#   d  papeis, o helper de RLS, o RLS ligado e as politicas
#   e  as views e os RPCs, que leem tudo o que veio antes
BLOCOS = [
    {'ID': 'a', 'ARQUIVO': '0001a_already_applied.sql',
     'TITULO': 'JA APLICADO PELO CHATGPT — nao rodar de novo',
     'ATE_INCLUIR': ('CREATE TABLE', 'source'),
     'PARA_QUE': 'schema sintonia, os 27 vocabularios fechados e as quatro '
                 'primeiras tabelas. Fica separado para poder ser CONFERIDO em vez '
                 'de reexecutado.'},
    {'ID': 'b', 'ARQUIVO': '0001b_tables_remaining.sql',
     'TITULO': 'TABELAS RESTANTES',
     'ATE_ANTES_DE': ('ALTER TABLE',),
     'PARA_QUE': 'as tabelas que faltam. Nenhuma FK aqui: as chaves estrangeiras '
                 'vem no bloco c, entao a ordem entre as tabelas nao importa.'},
    {'ID': 'c', 'ARQUIVO': '0001c_foreign_keys_indexes.sql',
     'TITULO': 'CHAVES ESTRANGEIRAS E INDICES',
     'ATE_ANTES_DE': ('DO',),
     'PARA_QUE': 'as FKs com ON DELETE explicito e os indices. Exige todas as '
                 'tabelas de pe — por isso vem depois de b.'},
    {'ID': 'd', 'ARQUIVO': '0001d_roles_rls_policies.sql',
     'TITULO': 'PAPEIS, RLS E POLITICAS',
     'ATE_ANTES_DE': ('CREATE VIEW',),
     'PARA_QUE': 'os papeis, o helper allowed_countries(), o RLS ligado em toda '
                 'tabela e as politicas. O helper vem junto porque toda politica '
                 'de pais chama ele.'},
    {'ID': 'e', 'ARQUIVO': '0001e_views_rpcs.sql',
     'TITULO': 'VIEWS E RPCS',
     'ATE_O_FIM': True,
     'PARA_QUE': 'as 13 views e os 4 RPCs. Leem tudo o que veio antes, entao sao '
                 'os ultimos.'},
]


def alvo_da_reconstrucao(detalhado=False):
    """O arquivo canonico menos as DUAS linhas de transacao. Nada mais.

    Cada pedaco abre e fecha a propria transacao, entao o `BEGIN;` e o `COMMIT;`
    que envolviam o arquivo inteiro saem. Sao as unicas duas coisas que a prova
    desconsidera, e elas saem por OFFSET do leitor de statements, nao por
    substituicao de texto: `BEGIN` tambem aparece dentro dos corpos `DO $$ BEGIN`
    e de cinco funcoes, e um replace cego apagaria a palavra errada.

    O cabecalho de comentarios do original fica: ele e conteudo, e vai inteiro
    para o bloco a.
    """
    sql, fatias = mapear()
    fora = []
    for f in fatias:
        if f['TIPO'] in ('BEGIN', 'COMMIT'):
            # A fatia de um statement comeca onde o anterior terminou, entao ela
            # carrega os comentarios que vieram antes. No BEGIN isso e o cabecalho
            # inteiro do arquivo; no COMMIT, a nota final sobre fallback de idioma.
            # Remover a fatia toda apagaria 827 caracteres de texto que ninguem
            # pediu para sair. So a LINHA do comando sai.
            ini = _offset_do_comando(sql, f['INI'], f['FIM'])
            fim = f['FIM']
            # O arquivo canonico esta gravado em CRLF. Consumir so '\n' deixaria
            # um '\r' orfao no lugar da linha removida — invisivel na tela e
            # visivel no sha256.
            if sql[fim:fim + 2] == '\r\n':
                fim += 2
            elif sql[fim:fim + 1] in ('\n', '\r'):
                fim += 1
            fora.append((ini, fim))
    if len(fora) != 2:
        raise SystemExit('esperava exatamente um BEGIN e um COMMIT de topo, '
                         'achei %d' % len(fora))
    alvo, ultimo = [], 0
    for ini, fim in fora:
        alvo.append(sql[ultimo:ini])
        ultimo = fim
    alvo.append(sql[ultimo:])
    if detalhado:
        return sql, ''.join(alvo), [sql[i:j] for i, j in fora]
    return sql, ''.join(alvo)


def dividir():
    """Devolve os blocos com corpo = fatia literal do alvo da reconstrucao.

    Os cortes sao recalculados SOBRE o alvo, nao sobre o original: tirar duas
    linhas move todos os offsets seguintes, e usar os antigos cortaria no lugar
    errado por 8 caracteres.
    """
    sql_original, sql = alvo_da_reconstrucao()
    uteis = [f for f in [{'INI': i, 'FIM': j, 'TIPO': _tipo(sql[i:j]),
                          'ALVO': _alvo(sql[i:j], _tipo(sql[i:j]))}
                         for i, j in statements(sql)]
             if f['TIPO'] not in ('BEGIN', 'COMMIT', 'COMENTARIO')]
    if not uteis:
        raise SystemExit('migration sem comandos: nada a dividir')

    # agora o corpo e o arquivo inteiro: cabecalho de comentarios incluido
    corpo_ini, corpo_fim = 0, len(sql)

    cortes = []
    for b in BLOCOS[:-1]:
        if 'ATE_INCLUIR' in b:
            tipo, alvo = b['ATE_INCLUIR']
            achado = [f for f in uteis if f['TIPO'] == tipo and f['ALVO'] == alvo]
            if len(achado) != 1:
                raise SystemExit('fronteira %s %s: %d ocorrencias, esperava 1'
                                 % (tipo, alvo, len(achado)))
            cortes.append(achado[0]['FIM'])
        else:
            (tipo,) = b['ATE_ANTES_DE']
            depois = [f for f in uteis if f['TIPO'] == tipo
                      and f['INI'] >= (cortes[-1] if cortes else corpo_ini)]
            if not depois:
                raise SystemExit('fronteira antes de %s: nao encontrada' % tipo)
            cortes.append(depois[0]['INI'])

    limites = [corpo_ini] + cortes + [corpo_fim]
    saida = []
    for k, b in enumerate(BLOCOS):
        ini, fim = limites[k], limites[k + 1]
        if ini >= fim:
            raise SystemExit('bloco %s ficou vazio' % b['ID'])
        corpo = sql[ini:fim]
        dentro = [f for f in uteis if ini <= f['INI'] < fim]
        saida.append({**b, 'INI': ini, 'FIM': fim, 'CORPO': corpo,
                      'STATEMENTS': dentro})
    return sql_original, sql, corpo_ini, corpo_fim, saida


SET_PATH = 'SET search_path TO sintonia, public;'


def render(b, indice, total):
    """O arquivo inteiro: andaime fora das marcas, fatia literal dentro."""
    ja = b['ID'] == 'a'
    cab = [
        '-- SINTONIA EAME · EXECUCAO EM PARTES · BLOCO %s DE %d (%s)'
        % (b['ID'].upper(), total, b['TITULO']),
        '--',
        '-- GERADO por scripts/supabase_execution_split.py. Nao editar a mao.',
        '--',
        '-- ORIGEM: supabase/migrations/0001_initial_canonical_schema.sql',
        '-- SHA256 DA ORIGEM: %s' % CANONICAL_0001_SHA256,
        '-- ALVO: %s (eame-sintonia-dev)' % DEV_PROJECT_REF,
        '--',
        '-- PARA QUE: %s' % b['PARA_QUE'],
        '--',
        '-- ORDEM: rode a, b, c, d, e nesta ordem. Cada um abre e fecha a propria',
        '-- transacao: se um falhar, ele volta inteiro e os anteriores ficam de pe.',
        '--',
        '-- O QUE E ANDAIME AQUI: este cabecalho, o BEGIN/COMMIT abaixo e o',
        '-- SET search_path. Foram acrescentados porque cada arquivo roda numa',
        '-- sessao propria. Tudo o que esta entre as duas marcas e fatia LITERAL',
        '-- do arquivo canonico, byte a byte, e a prova de reconstrucao confere.',
    ]
    if ja:
        cab += [
            '--',
            '-- ATENCAO: este bloco JA FOI APLICADO. Ele esta aqui para ser',
            '-- CONFERIDO, nao reexecutado. Rodar de novo levanta "already exists"',
            '-- no CREATE SCHEMA e nos 27 CREATE TYPE — o Postgres recusa e a',
            '-- transacao volta inteira, entao nao estraga nada.',
            '-- Ainda assim: nao rode. A conferencia certa e o inventario 0000.',
        ]
    cab += ['', 'BEGIN;', SET_PATH, '', MARCA_INICIO, '']
    # O canonico esta em CRLF. Se o andaime saisse em LF, o arquivo ficaria com as
    # duas convencoes misturadas — funciona no Postgres e engana qualquer diff.
    nl = quebra_de_linha(b['CORPO'])
    # O corpo entra CRU, sem strip e sem reindentar. Uma quebra de linha e
    # acrescentada logo antes da marca de fim, e a leitura tira exatamente essa
    # uma — por isso rsplit. Se eu aparasse as pontas aqui, a reconstrucao
    # perderia as linhas em branco que separam os comandos no original, e a
    # prova acusaria diferenca sem que nenhum SQL tivesse mudado.
    return nl.join(cab) + b['CORPO'] + nl + MARCA_FIM + nl + nl + 'COMMIT;' + nl


def quebra_de_linha(txt):
    """A convencao do proprio texto. O canonico esta em CRLF.

    Se o andaime saisse em LF, o arquivo ficaria com as duas convencoes
    misturadas: roda no Postgres do mesmo jeito e polui qualquer diff.
    """
    return '\r\n' if '\r\n' in txt else '\n'


def corpo_do_arquivo(txt):
    """Le de volta so o que esta entre as marcas. E o que a prova compara."""
    if MARCA_INICIO not in txt or MARCA_FIM not in txt:
        raise ValueError('arquivo sem as marcas de corpo')
    nl = quebra_de_linha(txt)
    depois = txt.split(MARCA_INICIO + nl, 1)[1]
    return depois.rsplit(nl + MARCA_FIM, 1)[0]


def verificar(blocos=None, sql=None, corpo_ini=None, corpo_fim=None):
    """A prova: os corpos, na ordem, reconstroem o original sem BEGIN/COMMIT."""
    if blocos is None:
        _, sql, corpo_ini, corpo_fim, blocos = dividir()
    esperado = sql[corpo_ini:corpo_fim]
    obtido = ''.join(b['CORPO'] for b in blocos)
    return {
        'RECONSTRUCTION_MATCH': 'YES' if obtido == esperado else 'NO',
        'SEMANTIC_DIFF': 0 if obtido == esperado else len(obtido) - len(esperado),
        'DESCONSIDERADO': ['BEGIN; do original', 'COMMIT; do original',
                           'a separacao fisica entre os arquivos'],
        'CORPO_SHA256': sha(esperado),
        'CORPO_BYTES': len(esperado.encode('utf-8')),
        'O_QUE_SAIU_DO_ORIGINAL': diferenca_para_o_original(),
    }


def diferenca_para_o_original():
    """Prova que o alvo e o original menos DUAS linhas, e diz quais.

    Nao basta afirmar 'so tirei BEGIN e COMMIT'. Aqui a diferenca de tamanho e
    conferida contra o tamanho exato das duas linhas: se qualquer outro byte
    tivesse sumido no caminho, a conta nao fecharia.
    """
    original, alvo, removidas = alvo_da_reconstrucao(detalhado=True)
    limpas = [r.strip() for r in removidas]
    return {
        'LINHAS_REMOVIDAS': limpas,
        'LINHAS_REMOVIDAS_LITERAIS': [repr(r) for r in removidas],
        'CARACTERES_REMOVIDOS': len(original) - len(alvo),
        'SO_SAIU_A_TRANSACAO': limpas == ['BEGIN;', 'COMMIT;'],
        'ORIGINAL_SHA256': sha(original),
        'ALVO_SHA256': sha(alvo),
        'COMO_FOI_REMOVIDO': ('por posicao, apontada pelo leitor de statements. '
                              'Um replace de texto apagaria tambem os BEGIN que '
                              'vivem dentro dos corpos DO $$ e das funcoes.'),
    }


def verificar_no_disco():
    """A prova de novo, agora lendo os arquivos gravados em vez da memoria."""
    original, sql, corpo_ini, corpo_fim, blocos = dividir()
    pedacos = []
    faltando = []
    for b in blocos:
        caminho = os.path.join(DESTINO, b['ARQUIVO'])
        if not os.path.exists(caminho):
            faltando.append(b['ARQUIVO'])
            continue
        with open(caminho, encoding='utf-8', newline='') as fh:
            pedacos.append(corpo_do_arquivo(fh.read()))
    if faltando:
        return {'RECONSTRUCTION_MATCH': 'NO', 'FALTANDO': faltando}
    esperado = sql[corpo_ini:corpo_fim]
    obtido = ''.join(pedacos)
    igual = obtido == esperado
    return {
        'RECONSTRUCTION_MATCH': 'YES' if igual else 'NO',
        'SEMANTIC_DIFF': 0 if igual else len(obtido) - len(esperado),
        'CORPO_SHA256': sha(obtido),
        'CORPO_SHA256_ESPERADO': sha(esperado),
        'LIDO_DE': 'os cinco arquivos gravados, nao da memoria do gerador',
    }


def _resumo(statements_do_bloco):
    r = {}
    for f in statements_do_bloco:
        r[f['TIPO']] = r.get(f['TIPO'], 0) + 1
    return dict(sorted(r.items()))


def _corta(linha, do_fim=False):
    """Encurta para caber no manifesto, e marca onde cortou.

    Sem a reticencia, uma linha cortada pela metade se le como SQL quebrado:
    'ATE POLICY ...' e o fim de 'CREATE POLICY ...' sem aviso nenhum.
    """
    linha = linha.strip()
    if len(linha) <= 100:
        return linha
    return ('…' + linha[-99:]) if do_fim else (linha[:99] + '…')


def _primeira_linha(txt):
    for linha in txt.strip().splitlines():
        if linha.strip() and not linha.strip().startswith('--'):
            return _corta(linha)
    return _corta(txt.strip().splitlines()[0])


def _ultima_linha(txt):
    for linha in reversed(txt.strip().splitlines()):
        if linha.strip() and not linha.strip().startswith('--'):
            return _corta(linha, do_fim=True)
    return _corta(txt.strip().splitlines()[-1], do_fim=True)


def medir():
    original, sql, corpo_ini, corpo_fim, blocos = dividir()
    sha_origem = sha(original)
    arquivos = []
    for i, b in enumerate(blocos):
        texto = render(b, i, len(blocos))
        arquivos.append({
            'FILE': 'supabase/execution/' + b['ARQUIVO'],
            'BLOCO': b['ID'],
            'TITULO': b['TITULO'],
            'PARA_QUE': b['PARA_QUE'],
            'STARTS_WITH': _primeira_linha(b['CORPO']),
            'ENDS_WITH': _ultima_linha(b['CORPO']),
            'BYTES': len(texto.encode('utf-8')),
            'SHA256': sha(texto),
            'CORPO_BYTES': len(b['CORPO'].encode('utf-8')),
            'CORPO_SHA256': sha(b['CORPO']),
            'STATEMENTS_COUNT': len(b['STATEMENTS']),
            'STATEMENTS_POR_TIPO': _resumo(b['STATEMENTS']),
            'JA_APLICADO': b['ID'] == 'a',
            'LINHAS_NO_ORIGINAL': '%d-%d' % (sql.count('\n', 0, b['INI']) + 1,
                                             sql.count('\n', 0, b['FIM']) + 1),
        })
    prova = verificar(blocos, sql, corpo_ini, corpo_fim)
    total_st = sum(a['STATEMENTS_COUNT'] for a in arquivos)
    return {
        'SOURCE_ID': 'SUPABASE-EXECUTION-MANIFEST-EAME-2026-08-31',
        'source': 'Divisao da migration canonica em pedacos executaveis. Corte de '
                  'ferramenta, nao de modelagem: nada muda de sentido.',
        'DEV_PROJECT_REF': DEV_PROJECT_REF,
        'CANONICAL_0001_SHA256': sha_origem,
        'SHA_BATE_COM_O_DECLARADO': sha_origem == CANONICAL_0001_SHA256,
        'CANONICAL_0001_BYTES': len(original.encode('utf-8')),
        'MIGRATION_APPLIED_DEV': 'PARTIAL',
        'POR_QUE_PARCIAL': ('o bloco a foi aplicado e os quatro seguintes nao. '
                            'Enquanto e e nao correr, MIGRATION_APPLIED_DEV nao e YES.'),
        'ALREADY_APPLIED_BLOCK': arquivos[0]['FILE'],
        'REMAINING_BLOCKS': [a['FILE'] for a in arquivos[1:]],
        'ORDEM_DE_EXECUCAO': [a['FILE'] for a in arquivos[1:]],
        'ARQUIVOS': arquivos,
        'STATEMENTS_TOTAL': total_st,
        'PROVA_DE_RECONSTRUCAO': prova,
        'O_QUE_NAO_FOI_TOCADO': [
            'supabase/migrations/0001_initial_canonical_schema.sql (mesmo sha256)',
            'data/supabase/SUPABASE-CANONICAL-SCHEMA.json',
            'supabase/validation/0002_dev_validation.sql',
            'supabase/validation/0003_post_migration_checks.sql',
            'V8', 'Vercel', 'design',
        ],
        'EXECUTADO_POR_MIM': False,
        'POR_QUE_NAO': 'nao ha credencial nesta maquina, e nao e o meu papel aqui: '
                       'quem aplica e quem tem acesso.',
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    if '--sync' in sys.argv:
        os.makedirs(DESTINO, exist_ok=True)
        blocos = dividir()[4]
        for i, b in enumerate(blocos):
            caminho = os.path.join(DESTINO, b['ARQUIVO'])
            # newline='' para nao traduzir nada: o corpo tem de sair do disco
            # exatamente como entrou, senao a prova de reconstrucao vira teatro.
            with open(caminho, 'w', encoding='utf-8', newline='') as fh:
                fh.write(render(b, i, len(blocos)))
            print('gravado', os.path.relpath(caminho, RAIZ))
        m['PROVA_NO_DISCO'] = verificar_no_disco()
        with open(MANIFESTO, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado', os.path.relpath(MANIFESTO, RAIZ))
    print(json.dumps(m, ensure_ascii=False, indent=2))
