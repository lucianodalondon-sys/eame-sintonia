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
