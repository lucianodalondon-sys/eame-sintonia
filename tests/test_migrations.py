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

    def test_a_fase_10_retira_a_identidade_do_endereco(self):
        """A `027` faz as três coisas, e NÃO faz a quarta.

        A quarta é retirar a COLUNA `storage_path`, que é a fase 11. Uma
        migration que fizesse as duas fases de uma vez seria impossível de
        reverter por metades — e a metade que interessa reverter é sempre a
        última.
        """
        f = [x for x in self.arqs if x.startswith('027_')]
        self.assertEqual(len(f), 1, 'a fase 10 tem de ser UMA migration')
        s = open(os.path.join(MIG, f[0]), encoding='utf-8').read().lower()
        self.assertIn('drop constraint if exists raw_asset_storage_path_key', s)
        self.assertIn('raw_tentativa_sem_prova_idx', s)
        self.assertIn('nulls not distinct', s)
        self.assertIn('storage_object_id', s)
        self.assertIn('a_identidade_da_observacao_nao_se_reescreve', s)
        # A FASE 11 NAO ENTRA. `drop column storage_path` em qualquer forma.
        self.assertNotIn('drop column storage_path', s)
        self.assertNotIn('drop column if exists storage_path', s)
        # E a chave da tentativa NAO se constroi sobre o endereco: se o fizesse
        # passaria hoje e teria de ser desfeita na fase 11.
        i = s.index('raw_tentativa_sem_prova_idx')
        corpo = s[i:s.index(';', i)]
        self.assertNotIn('storage_path', corpo,
                         'a chave da tentativa nao pode depender do endereco')

    def test_nenhuma_migration_foi_executada(self):
        """Esta missao PROPOE. Se aparecer codigo de conexao aqui, alguem executou."""
        # ⚠️ AS DUAS GRAFIAS VALEM, e nao por preguica.
        # 23 das 24 migrations escrevem «NÃO EXECUTADA»; a `022` escreve
        # «NAO EXECUTADA», sem til, como todo o resto do ficheiro dela. A
        # marca esta la nas 24 — o que variava era o acento.
        #
        # O caminho obvio seria corrigir a `022`. Nao se corrige, e a razao
        # e operacional: `motor/cadeia_canonica.sh:99` guarda o `sha256sum`
        # do FICHEIRO INTEIRO em `schema_migracao`, e a trava de drift para
        # a cadeia quando o sha muda. Editar um comentario mudaria o sha e
        # partiria a cadeia em qualquer banco onde a 022 ja tenha sido
        # aplicada. O cabecalho dela diz que producao nao foi tocada; se ha
        # um ambiente de dev com ela aplicada, ninguem aqui consegue medir.
        #
        #     NAO SE MEXE NUM FICHEIRO CUJO HASH E CONTRATO
        #     PARA ARRUMAR UM ACENTO.
        #
        # E a invariante que este caso guarda e «a migration DECLARA que nao
        # foi executada» — nao «declara com til». As duas grafias declaram.
        for f in self.arqs:
            s = open(os.path.join(MIG, f), encoding='utf-8').read()
            with self.subTest(arquivo=f):
                self.assertTrue(
                    'NÃO EXECUTADA' in s or 'NAO EXECUTADA' in s,
                    f'{f} sem a marca de proposta')
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

    # AS ÚNICAS ISENÇÕES, CADA UMA COM A SUA RAZÃO ESCRITA.
    #
    # Uma isenção existe quando o índice NÃO PODE ver um NULL naquela coluna —
    # e aí `nulls not distinct` não protegeria nada, protegeria o vazio.
    #
    #     1. o predicado exclui o NULL         `where col is not null`
    #        derivável do próprio índice, e tratada em código.
    #
    #     2. um CHECK noutra migration garante o NOT NULL sob o predicado
    #        NÃO derivável de uma varredura de texto, e por isso nomeada aqui —
    #        com a trava que a justifica, que este mesmo caso confere que
    #        existe. Uma isenção cuja justificação some deixa de valer.
    ISENTOS = {
        "raw_identidade_forward_idx": (
            ("forward_identificado_exige_identidade",
             "fonte_real_em_qualquer_estado_forward"),
            "sob `identity_state = FORWARD_IDENTIFIED` as duas travas da 026 "
            "exigem `document_key` e `source_id` reais — nao so nao nulos: "
            "nao vazios e nao sentinela. O indice nunca ve um NULL ali."),
    }

    def test_indice_unico_com_coluna_nulavel_usa_nulls_not_distinct(self):
        """A MESMA lei do caso acima, para os índices que nascem FORA do
        `create table`.

        ⚠️ O caso anterior varre blocos `create table` — e a fase 10 não trouxe
        uma coluna, trouxe um `create unique index`. A lei era a mesma e a
        varredura não chegava lá: uma chave parcial sobre `storage_object_id`,
        que é anulável, teria passado sem `nulls not distinct` e destrancado
        sozinha para cada observação NÃO preservada.

            UMA LEI QUE SO SE COBRA NUM DOS SITIOS ONDE ELA VALE
            E UMA LEI COM UM BURACO DO TAMANHO DO OUTRO SITIO.

        As colunas anuláveis são lidas das próprias migrations, e não de uma
        lista escrita à mão: uma lista envelheceria em silêncio.
        """
        nulaveis = self._colunas_nulaveis()
        achou, isentados = 0, 0
        for nome, tabela, cols, trecho in self._indices_unicos():
            alvo = cols & nulaveis.get(tabela, set())
            # ISENÇÃO 1 · o predicado exclui o NULL, e isso lê-se do índice.
            alvo = {c for c in alvo
                    if not re.search(r'\b%s\s+is\s+not\s+null\b' % re.escape(c),
                                     trecho, re.I)}
            if not alvo:
                continue
            if nome in self.ISENTOS:
                isentados += 1
                continue
            achou += 1
            with self.subTest(indice=nome, chave=", ".join(sorted(cols))):
                self.assertIn("nulls not distinct", trecho.lower(),
                              f"{nome}: coluna nulavel {sorted(alvo)} e "
                              f"destranca com NULL")
        # E o caso tem de ter mesmo olhado para alguma coisa. Um `for` que não
        # itera passa sempre, e passaria calado se a varredura se partisse.
        self.assertGreater(achou + isentados, 0,
                           "nenhum indice unico com coluna nulavel foi "
                           "examinado — a varredura partiu-se")

    def test_toda_isencao_do_nulls_not_distinct_tem_a_trava_que_a_justifica(self):
        """Uma isenção é uma dívida, e esta paga-se sozinha.

        A isenção do índice forward apoia-se em duas travas da `026`. Se
        alguém as retirar, a isenção deixa de ter fundamento — e é ESTE caso
        que reprova, e não o índice a destrancar em produção meses depois.

            UMA LISTA DE EXCECOES QUE NINGUEM CONFERE
            E UMA PORTA DAS TRASEIRAS COM UM COMENTARIO BONITO POR CIMA.
        """
        nomes = {n for n, _, _, _ in self._indices_unicos()}
        for indice, (travas, porque) in self.ISENTOS.items():
            with self.subTest(indice=indice):
                self.assertIn(indice, nomes,
                              "isencao para um indice que ja nao existe")
                self.assertTrue(porque.strip(), "isencao sem razao escrita")
                for trava in travas:
                    self.assertIn(trava, self.todo,
                                  f"a trava {trava} sumiu e a isencao de "
                                  f"{indice} ficou sem fundamento")

    def _colunas_nulaveis(self):
        """`{tabela: {colunas sem NOT NULL}}`, lido das migrations."""
        fora = {}
        padrao = r'create table (?:if not exists )?public\.(\w+)\s*\((.*?)\n\);'
        for tabela, corpo in re.findall(padrao, self.todo, re.S):
            for linha in corpo.splitlines():
                m = re.match(r'\s*(\w+)\s+[\w()\[\], ]+', linha)
                if m and 'not null' not in linha.lower() and \
                   not linha.strip().lower().startswith(
                       ('unique', 'constraint', 'primary key', 'check', '--')):
                    fora.setdefault(tabela, set()).add(m.group(1))
        # `add column` tambem cria coluna, e as seis da 026 entraram por ai.
        for bloco in re.findall(
                r'alter table public\.(\w+)(.*?);', self.todo, re.S):
            tabela, corpo = bloco
            for col in re.findall(
                    r'add column(?: if not exists)?\s+(\w+)([^,\n]*)', corpo):
                nome, resto = col
                if 'not null' not in resto.lower():
                    fora.setdefault(tabela, set()).add(nome)
        return fora

    def _indices_unicos(self):
        """`(nome, tabela, {colunas}, trecho)` de cada `create unique index`."""
        padrao = (r'create unique index (?:if not exists )?(\w+)\s*'
                  r'on public\.(\w+)\s*\(([^)]*)\)([^;]*);')
        for nome, tabela, cols, resto in re.findall(padrao, self.todo,
                                                    re.S | re.I):
            limpas = {c.strip() for c in cols.split(',') if c.strip()}
            yield nome, tabela, limpas, cols + resto

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


# ⚠️ SEM ISTO, `python3 tests/test_migrations.py` NAO CORRIA NADA.
# O ficheiro define 3 classes e 20 casos, e sem um arranque saia com 0 e
# sem uma linha de saida — indistinguivel de uma bateria verde. Um censo
# feito por `for f in tests/test_*.py; do python3 $f; done` contava-o como
# aprovado; ele nunca tinha corrido.
#
#     NAO CORREU != PASSOU.
if __name__ == '__main__':
    import sys
    sys.exit(0 if unittest.main(exit=False).result.wasSuccessful() else 1)
