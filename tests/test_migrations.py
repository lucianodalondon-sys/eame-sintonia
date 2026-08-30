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

    def test_os_numeros_sao_unicos_e_todo_buraco_e_declarado(self):
        """Sequencia sem buraco, com UMA excecao: um numero RESERVADO.

        O 014 e do catalogo publico da branch paralela e fica vago ate ele
        entrar. Um buraco silencioso continua sendo defeito — o que muda e
        que um buraco DECLARADO na propria migration seguinte nao e.
        """
        nums = [int(f[:3]) for f in self.arqs]
        self.assertEqual(len(nums), len(set(nums)), f'numero repetido em {self.arqs}')
        buracos = sorted(set(range(1, max(nums) + 1)) - set(nums))
        for b in buracos:
            with self.subTest(numero=b):
                self.assertRegex(
                    self.todo, rf'O N[UÚ]MERO {b:03d} EST[AÁ] RESERVADO',
                    f'buraco {b:03d} na sequencia sem reserva declarada em migration nenhuma')

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

    def test_custo_declara_como_foi_medido(self):
        """Tres metodos de custo escrevendo na mesma coluna, sem dizer qual.

        O leitor do acervo brasileiro chamou isso de "o defeito de schema mais
        importante" da proveniencia: custo lido da plataforma e custo estimado por
        diferenca de saldo nao sao o mesmo numero, e somar os dois produz um total
        que nao existe.
        """
        self.assertIn('cost_method', self.todo)
        self.assertRegex(self.todo, r'CHECK \(cost_usd IS NULL OR cost_method IS NOT NULL\)')

    def test_todo_conteudo_aponta_para_a_execucao_que_o_produziu(self):
        """No Brasil `documentos.coleta_id` e FK desde o inicio, mas o preenchimento
        e PARCIAL e nao uniforme por porta — zero em varias celulas. O custo medido:
        o freio de fonte-seca da fila enxerga so um quarto do acervo.

        Uma FK nulavel nao garante o elo. Aqui run_id e NOT NULL nas tres tabelas de
        conteudo, entao a linha nao existe sem a execucao que a produziu.
        """
        for tabela in ('conteudo', 'transcricao', 'comentario'):
            i = self.todo.find('create table public.%s ' % tabela)
            bloco = self.todo[i:self.todo.find(');', i)]
            with self.subTest(tabela=tabela):
                self.assertRegex(bloco, r'run_id\s+text\s+not null',
                                 f'{tabela}.run_id precisa ser NOT NULL')


class TestRawPesadoNaoVoltaParaOGit(unittest.TestCase):
    """O gz nao deltifica: cada versao entra no pack pelo tamanho integral, para sempre.

    Medido em 2026-08-29 sobre este repositorio: os 12 blobs .gz tem ratio 1,00 e ZERO
    delta base, contra 0,16 dos .json. Um deles sozinho e 17% do pack. O backfill do
    universo espanhol expandido somaria 4,5 MB permanentes e irrecuperaveis sem reescrever
    historico.

    Os 12 ja versionados ficam: apagar blob antigo nao encolhe o pack de quem ja clonou, e
    reescrever historico custa mais do que resolve. Esta trava so impede o CRESCIMENTO.
    """

    CONGELADO = os.path.join(os.path.dirname(MIG), '..', 'data', 'samples',
                             'RAW-PESADO-CONGELADO.txt')

    def _rastreados(self):
        import subprocess
        r = subprocess.run(['git', 'ls-files', 'data/samples/**/*.gz'],
                           cwd=ROOT, capture_output=True, text=True)
        return sorted(x for x in r.stdout.split('\n') if x.strip())

    def test_nenhum_gz_novo_entrou(self):
        caminho = os.path.join(ROOT, 'data', 'samples', 'RAW-PESADO-CONGELADO.txt')
        with open(caminho, encoding='utf-8') as f:
            congelado = sorted(x for x in f.read().split('\n') if x.strip())
        atual = self._rastreados()
        novos = sorted(set(atual) - set(congelado))
        self.assertEqual([], novos,
                         'RAW pesado novo entrou no Git: %s — deve ir para Storage, '
                         'e o Git guarda so o hash no manifesto' % novos)

    def test_o_gitignore_barra_a_reincidencia(self):
        with open(os.path.join(ROOT, '.gitignore'), encoding='utf-8') as f:
            g = f.read()
        self.assertIn('data/samples/**/*.gz', g)

    def test_a_lista_congelada_nao_esta_vazia(self):
        """Lista vazia passaria o teste sempre — e seria uma trava que nao trava."""
        caminho = os.path.join(ROOT, 'data', 'samples', 'RAW-PESADO-CONGELADO.txt')
        with open(caminho, encoding='utf-8') as f:
            n = len([x for x in f.read().split('\n') if x.strip()])
        self.assertGreaterEqual(n, 11, 'a lista congelada perdeu entradas')
