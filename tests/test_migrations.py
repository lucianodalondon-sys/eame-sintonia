"""As migrations propostas sao COERENTES entre si, e continuam NAO EXECUTADAS.

Nao testam Postgres — nao ha banco nesta sessao e nao deve haver. Testam o que da
para provar lendo o texto: que toda tabela referenciada por uma chave estrangeira
existe, que os numeros nao colidem, e que as leis que a MISSAO 11A-BRIDGE-ES decidiu
transformar em constraint continuam la.

O risco que isto cobre e especifico: uma proposta de schema e lida uma vez, aprovada,
e executada semanas depois. Se entre a leitura e a execucao alguem renomear uma tabela
em 003 e esquecer a referencia em 005, o erro aparece no `psql`, no pior momento.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIG = os.path.join(ROOT, 'supabase', 'migrations')


def arquivos():
    return sorted(f for f in os.listdir(MIG) if f.endswith('.sql'))


def texto_de_todas():
    return '\n'.join(open(os.path.join(MIG, f), encoding='utf-8').read() for f in arquivos())


class TestMigrationsCoerentes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.arqs = arquivos()
        cls.todo = texto_de_todas()
        cls.criadas = set(re.findall(r'create table (?:if not exists )?public\.([a-z_]+)', cls.todo))
        cls.tipos = set(re.findall(r'create type ([a-z_]+)', cls.todo))

    def test_existe_pelo_menos_uma_migration(self):
        self.assertTrue(self.arqs, 'nenhuma migration em supabase/migrations/')

    def test_os_numeros_sao_unicos_e_sem_buraco(self):
        nums = [int(f[:3]) for f in self.arqs]
        self.assertEqual(len(nums), len(set(nums)), f'numero repetido em {self.arqs}')
        self.assertEqual(nums, list(range(1, len(nums) + 1)), f'sequencia com buraco: {nums}')

    def test_toda_tabela_referenciada_por_fk_e_criada(self):
        """Uma FK para tabela inexistente so falha no psql. Aqui falha antes."""
        for alvo in set(re.findall(r'references public\.([a-z_]+)', self.todo)):
            with self.subTest(tabela=alvo):
                self.assertIn(alvo, self.criadas,
                              f'FK aponta para public.{alvo}, que nenhuma migration cria')

    def test_toda_tabela_referenciada_e_criada_ANTES_de_ser_usada(self):
        """Ordem importa: o Postgres executa 001, 002, 003... em sequencia."""
        criada_em = {}
        for f in self.arqs:
            s = open(os.path.join(MIG, f), encoding='utf-8').read()
            for t in re.findall(r'create table (?:if not exists )?public\.([a-z_]+)', s):
                criada_em.setdefault(t, int(f[:3]))
        for f in self.arqs:
            n = int(f[:3])
            s = open(os.path.join(MIG, f), encoding='utf-8').read()
            for alvo in set(re.findall(r'references public\.([a-z_]+)', s)):
                with self.subTest(arquivo=f, alvo=alvo):
                    self.assertLessEqual(criada_em.get(alvo, 999), n,
                                         f'{f} referencia {alvo}, criada depois')

    def test_os_tipos_usados_foram_declarados(self):
        for t in ('pais', 'run_status', 'tipo_conteudo'):
            self.assertIn(t, self.tipos, f'tipo {t} usado mas nao declarado')

    def test_as_quatro_leis_viraram_constraint(self):
        """Cada uma destas foi uma decisao explicita da ponte Brasil -> EAME.

        Se alguem apagar uma, o que se perde nao e uma linha de SQL: e a garantia de
        que a lei nao depende de lembrar dela.
        """
        leis = {
            'bruto ausente declarado':
                r'CHECK \(preserved OR not_preserved_reason IS NOT NULL\)',
            'pessoa OU organizacao, nunca as duas':
                r'CHECK \(num_nonnulls\(pessoa_id, organizacao_id\) = 1\)',
            'zero nao vira lacuna sem diagnostico':
                r"CHECK \(estado <> 'LACUNA_CANDIDATA' OR zero_diagnosticado\)",
            'razao exige denominador':
                r'base_denominador numeric not null',
        }
        for nome, pat in leis.items():
            with self.subTest(lei=nome):
                self.assertRegex(self.todo, pat, f'a lei "{nome}" saiu do schema')

    def test_conflacao_continua_representavel(self):
        """pessoa_identificador NAO pode ter unique(sistema, valor).

        Um unique ali tornaria impossivel registrar o mesmo ID apontando para duas
        pessoas — que e exatamente o defeito que precisamos poder MEDIR. Um schema que
        nao deixa o erro existir tambem nao deixa contar quantas vezes ele aconteceu.
        """
        i = self.todo.find('create table public.pessoa_identificador')
        bloco = self.todo[i:self.todo.find(');', i)]
        self.assertNotRegex(bloco, r'UNIQUE \(sistema, valor\)\s*[,\)]',
                            'unique(sistema,valor) impediria representar conflacao')
        self.assertIn('UNIQUE (sistema, valor, pessoa_id)', bloco)

    def test_disponibilidade_comercial_nasce_em_nao_sei(self):
        """REGISTERED_RESPONSE_EXISTS != CURRENT_COMMERCIAL_AVAILABILITY."""
        self.assertRegex(
            self.todo,
            r"current_commercial_availability text not null default 'NAO_SEI'",
            'disponibilidade comercial precisa nascer NAO SEI, nunca deduzida do registro')

    def test_a_versao_da_fonte_faz_parte_da_chave_do_registro(self):
        """Status atual nao apaga a historia: duas capturas sao duas linhas."""
        i = self.todo.find('create table public.registro_regulatorio')
        bloco = self.todo[i:self.todo.find(');', i)]
        self.assertIn('UNIQUE (pais, registration_id, fonte_versao)', bloco)

    def test_todo_derivado_carrega_a_versao_da_regra(self):
        """Derivado sem rule_version nao e reproduzivel."""
        for tabela in ('conteudo', 'transcricao', 'observacao', 'derivacao',
                       'conteudo_crop_issue', 'lacuna_candidata', 'collection_run'):
            i = self.todo.find('create table public.%s ' % tabela)
            self.assertGreater(i, -1, f'tabela {tabela} nao encontrada')
            bloco = self.todo[i:self.todo.find(');', i)]
            with self.subTest(tabela=tabela):
                self.assertIn('rule_version', bloco, f'{tabela} sem rule_version')

    def test_nenhuma_migration_foi_executada(self):
        """Esta missao PROPOE. Se aparecer codigo de conexao aqui, alguem executou."""
        for f in self.arqs:
            s = open(os.path.join(MIG, f), encoding='utf-8').read()
            with self.subTest(arquivo=f):
                self.assertIn('NÃO EXECUTADA', s, f'{f} sem a marca de proposta')
        for proibido in ('SUPABASE_URL', 'SUPABASE_KEY', 'postgresql://', 'psycopg'):
            self.assertNotIn(proibido, self.todo,
                             f'credencial ou conexao ({proibido}) dentro de migration')


class TestLicoesDoBrasilNoSchema(unittest.TestCase):
    """Defeitos que o Sintonia Brasil pagou para descobrir, travados aqui.

    Cada teste abaixo existe porque o Brasil mediu o custo do defeito. Não são
    preferências de estilo: são contraexemplos com número.
    """

    @classmethod
    def setUpClass(cls):
        cls.todo = texto_de_todas()

    def test_origem_tem_chave_natural(self):
        """No Brasil, `fontes` só tem `id bigserial` — nenhuma chave natural.

        Custo medido: 102 nomes repetidos em 212 fontes. E como o dedupe de
        `documentos` é unique(fonte_id, hash_conteudo), uma fonte cadastrada duas
        vezes faz o MESMO conteúdo entrar duas vezes — e para o índice isso é
        legítimo. O dedupe do conteúdo não é melhor que a identidade da origem.
        """
        self.assertIn('create unique index origem_por_pessoa_idx', self.todo)
        self.assertIn('create unique index origem_por_organizacao_idx', self.todo)

    def test_unique_com_coluna_nulavel_usa_nulls_not_distinct(self):
        """No Postgres dois NULL são DIFERENTES: a trava destranca sozinha
        exatamente para as linhas que deixaram o campo em branco.

        Varre cada UNIQUE de tabela e exige NULLS NOT DISTINCT quando alguma
        coluna da chave é nulável. É a checagem que eu mesmo falhei na primeira
        escrita destas migrations, em quatro chaves.
        """
        padrao = r'create table public\.(\w+)\s*\((.*?)\n\);'
        for bloco in re.findall(padrao, self.todo, re.S):
            tabela, corpo = bloco
            nulaveis = set()
            for linha in corpo.splitlines():
                m = re.match(r'\s*(\w+)\s+[\w()\[\], ]+', linha)
                if m and 'not null' not in linha.lower() and \
                   not linha.strip().lower().startswith(('unique', 'constraint',
                                                         'primary key', 'check', '--')):
                    nulaveis.add(m.group(1))
            for u in re.findall(r'UNIQUE(?: NULLS NOT DISTINCT)? \(([^)]+)\)', corpo):
                cols = {c.strip() for c in u.split(',')}
                if cols & nulaveis:
                    trecho = [l for l in corpo.splitlines() if u in l][0]
                    with self.subTest(tabela=tabela, chave=u):
                        self.assertIn('NULLS NOT DISTINCT', trecho,
                                      f'{tabela}: chave ({u}) tem coluna nulável '
                                      f'{cols & nulaveis} e destranca com NULL')

    def test_duplicata_se_marca_e_nao_se_apaga(self):
        """A lei "um vídeo, uma transcrição" foi RECUSADA pelo banco no Brasil:
        o acervo já a violava, e o índice único não pôde ser criado.

        O conserto não foi apagar — foi `duplicata_de`, apontando para a cópia
        que fica. Uma lei nova não pode destruir o que veio antes dela.
        """
        self.assertIn('duplicata_de      bigint references public.conteudo(id)', self.todo)

    def test_existe_verificacao_pos_aplicacao(self):
        """Migração versionada prova que alguém ESCREVEU a tranca, não que ela
        FOI APLICADA.

        No Brasil quatro colunas de `fontes` usadas por 6 coletores foram criadas
        à mão no painel e nunca entraram em .sql; a `fontes` real tem 63 colunas
        contra 14 declaradas. Este arquivo é o que confere o outro lado.
        """
        f = [a for a in arquivos() if a.startswith('008')]
        self.assertTrue(f, 'falta a migration de verificação pós-aplicação')
        s = open(os.path.join(MIG, f[0]), encoding='utf-8').read()
        self.assertIn('information_schema.tables', s)
        self.assertIn('pg_constraint', s)
        self.assertIn('rowsecurity', s)
        self.assertIn('raise exception', s)
