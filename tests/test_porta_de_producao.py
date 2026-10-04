# -*- coding: utf-8 -*-
"""A PORTA DE PRODUÇÃO ESTÁ LACRADA — e estes testes é que a mantêm assim.

O QUE ACONTECEU, E POR QUE ISTO EXISTE
--------------------------------------
O `canario-022` fez o que tinha de fazer: aplicou a `022` e correu o primeiro
caminho forward italiano. Depois disso ficou pendurado no repositório com
capacidade de **escrever produção** — DDL, corrida, `raw_asset`, `derivado`,
Storage — e disparado por **empurrão de código**.

    MISSÃO ONE-SHOT TERMINOU → PORTA ONE-SHOT É FECHADA.
    Não vira daemon. Não vira coletor. Não vira caminho permanente.

E havia um segundo buraco no mesmo sítio: o pré-voo corria com `|| true`, e o
job de aplicar não recebia o veredito dele. **Um portão fechado não impedia
nada** — era um aviso, não uma tranca.

A OUTRA LEI QUE ESTES TESTES GUARDAM
------------------------------------
    MIGRATION APLICADA É ARTEFATO IMUTÁVEL.
    VERSÃO IGUAL COM SHA DIFERENTE É DRIFT.

E o SHA da `022` é medido **como o Git a guarda**, não como o disco a mostra —
foi exatamente aí que a entrega anterior errou.
"""
import hashlib
import os
import re
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS = os.path.join(RAIZ, ".github", "workflows")

# O SHA do BLOB, com terminações LF — que é o que o CI faz checkout e o que a
# produção recebeu. Ver `test_o_sha_e_o_do_git_nao_o_do_disco`.
SHA_DA_022_APLICADA = \
    "230be77df8b6facfc3319b273a665120669c813feb9bc6ceac87f3497ac3f718"
MIGRATION_022 = "supabase/migrations/022_o_derivado_ganha_casa.sql"


def sem_comentarios(texto: str) -> str:
    """Só as linhas EXECUTÁVEIS do YAML.

    ⚠️ ISTO EXISTE PORQUE ME ENGANEI CINCO VEZES DA MESMA MANEIRA. O cabeçalho
    de um ficheiro explica o que ele NÃO faz — «não chama `cadeia_canonica.sh`»,
    «não recebe `SUPABASE_SECRET_KEY`» — e um teste que procura a palavra no
    ficheiro inteiro reprova justamente o texto que enuncia a regra.

    O que se compara é a coisa, não a prosa sobre a coisa.
    """
    return " ".join(l for l in texto.splitlines()
                    if not l.strip().startswith("#"))


# ── A ISENÇÃO DA BANCADA DESCARTÁVEL, POR LINHA FÍSICA — 2026-09-17 ─────────
# ⚠️ A PRIMEIRA VERSÃO DESTA ISENÇÃO PROMETIA «MESMA LINHA» E OPERAVA SOBRE O
# FICHEIRO INTEIRO: o texto chegava aqui depois de `sem_comentarios()`, que
# faz `" ".join(...)` — e um `splitlines()` sobre texto já colado devolve UMA
# linha. A revisão independente provou o bypass: um escritor de produção
# acrescentado ao `sintonia-scrap.yml` passava calado, porque a DSN benigna do
# passo 5a-IT «isentava» o ficheiro todo (know-how §131).
#
#     GUARDA QUE RACIOCINA POR LINHA NÃO PODE DESTRUIR LINHAS ANTES DE DECIDIR.
#
# Por isso `escreve_producao()` recebe o TEXTO ORIGINAL e tira os comentários
# linha a linha, sem join. E a isenção deixou de ser um par de substrings
# («@localhost» casava com `@localhost.evil.com`; «/descartavel» casava com
# `/descartavel_prod` e com `/descartavel?host=db.X.supabase.co` — e a libpq
# OBEDECE ao `?host=`): o argumento da cadeia tem de ser a DSN LITERAL da
# bancada, host local e banco `descartavel`, sem query string e sem variável.
# Um `$VAR` no lugar da DSN não ganha isenção — DESTINO DESCONHECIDO FECHA A
# PORTA, não abre.
# O gatilho é REGEX, não substring: `cadeia_canonica.sh␣␣migrations` com dois
# espaços (ou tab) é o MESMO comando para o bash, e um `in linha` com um
# espaço exato deixava-o passar — apanhado por red team em 2026-09-17.
RE_CADEIA = re.compile(r"cadeia_canonica\.sh\s+(?:migrations|importacoes)\b")
RE_BANCADA_DESCARTAVEL = re.compile(
    r"cadeia_canonica\.sh\s+(?:migrations|importacoes)\s+"
    r"['\"]?postgresql://[A-Za-z0-9_.%:-]*"        # credenciais literais
    r"@(?:localhost|127\.0\.0\.1)(?::\d{1,5})?"    # host local, e nada colado
    r"/descartavel['\"]?(?=\s|$)")                 # banco exato; ? _ . reprovam
# `chave: >` no fim da linha abre um FOLDED SCALAR: o YAML entrega ao shell
# as linhas seguintes DOBRADAS numa só. Ler o ficheiro cru sem dobrar deixava
# `run: >` esconder `cadeia \n migrations $PROD` — red team, 2026-09-17.
# ⚠️ E o cabeçalho do fold aceita MAIS do que `>`/`>-`: a spec permite
# indicador de indentação numérico e comentário — `>2`, `>-2`, `>+`, e
# `> # nada` dobram IGUAL. A primeira versão só casava o cabeçalho nu, e o
# segundo round do red team passou por `>2` — por isso o [0-9+-]{0,2} e o
# comentário opcional.
RE_DOBRA_YAML = re.compile(r":\s*>[0-9+-]{0,2}\s*(?:#.*)?$")


def _linhas_como_o_shell_ve(texto):
    """As linhas na granularidade que o EXECUTOR recebe, não a do ficheiro.

    Dobra os folded scalars (`: >` / `: >-` / `: >+`) como o YAML dobra —
    as linhas mais indentadas viram UMA linha lógica. Blocos `|` e o resto
    ficam físicos: neles, linha do ficheiro É linha do shell.
    """
    fisicas = texto.splitlines()
    logicas, i = [], 0
    while i < len(fisicas):
        linha = fisicas[i]
        if RE_DOBRA_YAML.search(linha) and not linha.strip().startswith("#"):
            recuo = len(linha) - len(linha.lstrip())
            partes = []
            i += 1
            while i < len(fisicas):
                seg = fisicas[i]
                if seg.strip() and (len(seg) - len(seg.lstrip())) <= recuo:
                    break
                partes.append(seg.strip())
                i += 1
            logicas.append(linha + " " + " ".join(p for p in partes if p))
            continue
        logicas.append(linha)
        i += 1
    return logicas


def escreve_producao(texto):
    """True quando alguma LINHA executável escreve onde produção mora.

    Recebe o texto ORIGINAL do workflow (com quebras de linha vivas), dobra
    o que o YAML dobraria, e decide linha a linha. Comentário não acusa e
    não isenta; e CADA invocação da cadeia na linha tem de provar, no seu
    próprio argumento, que o destino é a bancada descartável — um `search`
    solto deixava uma isca no fim da linha isentar o escritor real no
    começo dela (red team, 2026-09-17).
    """
    for linha in _linhas_como_o_shell_ve(texto):
        if linha.strip().startswith("#"):
            continue
        # `SUPABASE_SECRET` e não a chave inteira: partir o nome com `\` de
        # shell no fim da linha remontava a chave fora da vista da guarda.
        if "SUPABASE_SECRET" in linha:
            return True
        acusa = False
        for invocacao in RE_CADEIA.finditer(linha):
            if not RE_BANCADA_DESCARTAVEL.match(linha, invocacao.start()):
                acusa = True
                break
        if acusa:
            return True
        # `cadeia ... \` — o comando continua noutra linha, e ESTA linha já
        # não consegue provar o destino. Nenhum workflow legítimo da casa
        # parte a chamada assim. DESCONHECIDO FECHA A PORTA.
        if "cadeia_canonica.sh" in linha and linha.rstrip().endswith("\\"):
            return True
    # ── SEGUNDA PASSADA: A VISTA DOBRADA, QUE SÓ ACUSA ──────────────────
    # O YAML também dobra PLAIN e QUOTED scalars multilinha — sem `>`, sem
    # `\`, sem sinal nenhum na linha (3º round do red team, 2026-09-17).
    # Junta-se tudo o que é executável e CADA invocação da cadeia tem de
    # provar o argumento TAMBÉM aqui. A ironia é de propósito: o join que
    # causou o furo original volta, mas do lado de quem ACUSA — juntar
    # linhas nunca isenta ninguém (a isenção ancorada por invocação não é
    # alcançável por isca, e o passo 1 já devolveu True antes desta linha
    # para tudo o que ele apanha).
    dobrado = " ".join(l.strip() for l in texto.splitlines()
                       if l.strip() and not l.strip().startswith("#"))
    for invocacao in RE_CADEIA.finditer(dobrado):
        if not RE_BANCADA_DESCARTAVEL.match(dobrado, invocacao.start()):
            return True
    return False


def _blob(caminho_relativo):
    """Os bytes como o Git os guarda — não como o disco os mostra."""
    return subprocess.run(["git", "show", "HEAD:%s" % caminho_relativo],
                          cwd=RAIZ, capture_output=True).stdout


class A022NaoSeEdita(unittest.TestCase):
    """A migration aplicada é um artefato, não um documento vivo."""

    def test_o_sha_da_022_e_o_que_a_producao_recebeu(self):
        self.assertEqual(hashlib.sha256(_blob(MIGRATION_022)).hexdigest(),
                         SHA_DA_022_APLICADA)

    def test_o_sha_e_o_do_git_nao_o_do_disco(self):
        """O ERRO DA ENTREGA ANTERIOR, virado em teste.

        Publiquei `7f46ea93…`, que é o `sha256` do ficheiro **neste disco
        Windows**, com CRLF. O que a produção recebeu foi o blob do Git, com
        LF: `230be77d…`. Medi do lado errado da conversão de fim de linha.

        Em máquinas onde o disco tem LF os dois valores coincidem, e o teste
        continua verde — o que ele garante é que a referência é o **blob**.
        """
        do_disco = hashlib.sha256(
            open(os.path.join(RAIZ, MIGRATION_022), "rb").read()).hexdigest()
        do_git = hashlib.sha256(_blob(MIGRATION_022)).hexdigest()
        self.assertEqual(do_git, SHA_DA_022_APLICADA)
        if do_disco != do_git:
            self.assertNotEqual(
                do_disco, SHA_DA_022_APLICADA,
                "o valor do disco nunca pode ser publicado como o aplicado")

    def test_a_022_nao_foi_reescrita_para_dizer_que_correu(self):
        """Trocar «NAO EXECUTADA» por «executada» no ficheiro mudaria o SHA e
        faria o livro-razão apontar para algo que nunca correu. O estado live
        mora nos docs, no mapa e no ledger — não numa edição retroativa."""
        texto = _blob(MIGRATION_022).decode("utf-8")
        self.assertIn("NAO EXECUTADA EM PRODUCAO", texto)


class OMigradorNaoPulaCego(unittest.TestCase):
    """Versão no livro não basta: o ficheiro tem de ser o mesmo."""

    def setUp(self):
        with open(os.path.join(RAIZ, "motor", "cadeia_canonica.sh"),
                  encoding="utf-8") as f:
            self.fonte = f.read()

    def test_o_skip_exige_o_hash(self):
        self.assertIn("HASH=MATCH", self.fonte)
        self.assertIn("select sha256 from public.schema_migracao", self.fonte)

    def test_hash_diferente_falha_fechado(self):
        self.assertIn("MIGRATION_APLICADA_MUDOU", self.fonte)
        # O `exit 1` tem de vir DEPOIS do aviso e ANTES de qualquer aplicacao.
        # Compara-se ate ao proprio `exit 1` — uma janela de N caracteres
        # atravessava o `fi` e apanhava o `psql -f` do caminho normal, que e
        # justamente o que NAO corre quando ha drift.
        i = self.fonte.index("MIGRATION_APLICADA_MUDOU")
        ate_ao_exit = self.fonte[i:self.fonte.index("exit 1", i)]
        self.assertNotIn("-f \"$f\"", ate_ao_exit)
        self.assertIn("LEDGER_SHA", ate_ao_exit)
        self.assertIn("REPO_SHA", ate_ao_exit)

    def test_o_skip_antigo_desapareceu(self):
        """A linha que pulava só por a versão existir não pode voltar."""
        self.assertNotIn('echo "MIGRATION_$num=SKIP (ja no livro-razao)"\n',
                         self.fonte.replace("HASH=MATCH", "X"))

    def test_a_migration_entra_inteira_ou_nao_entra(self):
        """Sem `--single-transaction`, cada instrução do ficheiro confirma-se
        sozinha. Reproduzido num Postgres descartável com um ficheiro
        A / B / ERRO / C: depois do erro, A e B FICARAM na tabela.

            META MIGRATION APLICADA É PIOR DO QUE NENHUMA:
            o livro-razão não a tem, e o banco já mudou.
        """
        self.assertIn("--single-transaction", self.fonte)

    def test_o_livro_razao_viaja_com_o_ddl(self):
        """O registo entra na MESMA transação do ficheiro.

        Enquanto ele era uma segunda chamada ao `psql`, havia uma janela entre
        o banco já ter mudado e o livro ainda não saber — e um processo morto
        ali deixava a migration aplicada e invisível.
        """
        # `rindex`, e não `index`: a primeira ocorrência de
        # `--single-transaction` está no COMENTÁRIO que explica porque ele
        # passou a existir. Procurar a primeira cortaria o ficheiro antes do
        # código e reprovaria a coisa certa pelo motivo errado.
        i = self.fonte.rindex("--single-transaction")
        # o `insert` do registo tem de estar no fluxo que ENTRA no psql, e não
        # numa chamada a seguir: procura-se ANTES do `--single-transaction`,
        # que é onde o `cat "$f"` e o `printf` do registo vivem.
        antes = self.fonte[:i]
        self.assertIn('cat "$f"', antes)
        self.assertIn("insert into public.schema_migracao", antes)

    def test_a_etapa_de_importacoes_nao_carrega_mais_uma_trava(self):
        """A trava saiu, e saiu junto com o que ela guardava.

        Ela existia por UM ficheiro — o catálogo ADAMA, com 138 `insert` em
        `raw_asset` sem identidade — e esse ficheiro saiu da cadeia. Medido:
        dos que restam, NENHUM toca `raw_asset`.

        Deixá-la aqui seria pior do que inútil. Ela pergunta «este banco já
        conhece a 026?» e recusa se sim — o que, sem nada antigo por trás,
        recusaria TODA importação futura contra o único banco que existe.

            UMA TRAVA QUE SO TRAVA O QUE E LEGITIMO NAO E UMA TRAVA.
        """
        self.assertNotIn("trava_do_escritor_antigo", self.fonte)
        self.assertNotIn("ADAMA-ES-CATALOGO", self.fonte)


class NenhumEscritorAntigoSobrou(unittest.TestCase):
    """A trava foi retirada porque o que ela guardava deixou de existir.

    ⚠️ A VERSÃO ANTERIOR DESTE TESTE COBRAVA O OPOSTO: que cada caminho antigo
    CHAMASSE `trava_do_escritor_antigo.sh` antes de escrever. Era o teste certo
    para o estado errado — ele consagrava que os caminhos antigos continuavam
    lá, atrás de um guarda.

        UM CAMINHO BLOQUEADO AINDA E UM CAMINHO.
        E UM GUARDA E UMA COISA QUE ALGUEM PODE TIRAR.

    Agora a invariante é mais forte e não precisa de guarda nenhum: eles não
    existem. E a razão não é de calendário — `adama-website` é uma ORGANIZAÇÃO,
    não um código de fonte do atlas, e sem `SOURCE_ID` real não há estado
    forward possível para aquelas linhas. Nunca houve.
    """

    APOSENTADOS = (("`.github`", "workflows", "supabase-raw-roundtrip.yml"),
                   ("`.github`", "workflows", "supabase-fichas-adama.yml"),
                   ("guarda", "trava_do_escritor_antigo.sh"))

    def test_os_caminhos_antigos_nao_existem(self):
        for caminho in (os.path.join(WORKFLOWS, "supabase-raw-roundtrip.yml"),
                        os.path.join(WORKFLOWS, "supabase-fichas-adama.yml"),
                        os.path.join(RAIZ, "guarda",
                                     "trava_do_escritor_antigo.sh")):
            self.assertFalse(os.path.exists(caminho), caminho)

    def test_nenhum_workflow_chama_a_trava(self):
        for nome in os.listdir(WORKFLOWS):
            with open(os.path.join(WORKFLOWS, nome), encoding="utf-8") as f:
                self.assertNotIn("trava_do_escritor_antigo",
                                 sem_comentarios(f.read()), nome)

    def test_o_importador_nao_aplica_mais(self):
        with open(os.path.join(RAIZ, "guarda", "catalogo_importar.py"),
                  encoding="utf-8") as f:
            corpo = f.read()
        self.assertIn("APOSENTADO", corpo)
        # E o que ele deixou de fazer: chamar `psql` sobre o SQL gerado.
        self.assertNotIn("'-f', SQL_OUT", corpo)

    def test_a_cadeia_nao_importa_mais_o_catalogo_sem_identidade(self):
        """O catálogo ADAMA sai da etapa `importacoes`.

        Medido contra um Postgres com a 026: ele falha na PRIMEIRA linha, em
        `identity_state` NOT NULL. Mantê-lo na cadeia declarava uma capacidade
        que não existe.
        """
        with open(os.path.join(RAIZ, "motor", "cadeia_canonica.sh"),
                  encoding="utf-8") as f:
            corpo = "\n".join(l for l in f if not l.strip().startswith("#"))
        self.assertNotIn("ADAMA-ES-CATALOGO", corpo)

    # O INVENTÁRIO, E NÃO UM `grep` COM ESPERANÇA. Três ficheiros de código
    # operacional contêm o texto `insert into public.raw_asset`, e os três têm
    # espécie declarada. Um quarto reprova este teste — que é o ponto.
    #
    #     ESCREVE    monta a linha E aplica-a a um banco
    #     GERA       monta o texto e entrega-o a quem o leia
    #     LE         reconhece o texto que outro montou
    QUEM_FALA_DE_RAW_ASSET = {
        # O ÚNICO ESCRITOR FORWARD. Sabe falar identidade, e é chamado por
        # `coleta/ingresso.py::receber`.
        "guarda/preservar_coleta.py": "ESCREVE",
        # GERA SQL para o Git. `--aplicar` foi aposentado: não há `SOURCE_ID`
        # real para aquelas linhas, e nunca houve.
        "guarda/catalogo_importar.py": "GERA",
        # LÊ o SQL que o escritor gerou, para simular `do nothing` a engolir
        # linhas. Porta de memória em SQLite; não é caminho de produção.
        "guarda/memoria_descartavel.py": "LE",
    }

    def test_o_inventario_de_quem_fala_de_raw_asset_esta_fechado(self):
        achados = {}
        for pasta in ("guarda", "coleta", "admissao", "motor", "orquestrador"):
            raiz = os.path.join(RAIZ, pasta)
            if not os.path.isdir(raiz):
                continue
            for base, _, ficheiros in os.walk(raiz):
                if "__pycache__" in base:
                    continue
                for nome in ficheiros:
                    if not nome.endswith((".py", ".sh")):
                        continue
                    caminho = os.path.join(base, nome)
                    with open(caminho, encoding="utf-8", errors="ignore") as f:
                        corpo = sem_comentarios(f.read())
                    if re.search(r"insert\s+into\s+(public\.)?raw_asset",
                                 corpo, re.I):
                        achados[os.path.relpath(caminho, RAIZ)] = True
        self.assertEqual(sorted(achados),
                         sorted(self.QUEM_FALA_DE_RAW_ASSET), sorted(achados))

    def test_o_unico_que_ESCREVE_e_o_escritor_canonico(self):
        escritores = [f for f, e in self.QUEM_FALA_DE_RAW_ASSET.items()
                      if e == "ESCREVE"]
        self.assertEqual(escritores, ["guarda/preservar_coleta.py"])

    def test_o_gerador_nao_aplica(self):
        """`catalogo_importar.py` GERA, e a diferença tem de estar no código."""
        with open(os.path.join(RAIZ, "guarda", "catalogo_importar.py"),
                  encoding="utf-8") as f:
            corpo = sem_comentarios(f.read())
        self.assertNotIn("'-f', SQL_OUT", corpo)


class APortaOneShotFoiAposentada(unittest.TestCase):
    """O `canario-022` não existe mais, e nada o substituiu com poder."""

    def test_o_workflow_do_canario_nao_existe(self):
        self.assertFalse(os.path.exists(
            os.path.join(WORKFLOWS, "canario-022.yml")))

    def test_o_script_do_canario_nao_existe(self):
        self.assertFalse(os.path.exists(
            os.path.join(RAIZ, "provas", "canario_forward_it.py")))

    def test_nenhum_workflow_dispara_o_canario(self):
        for nome in os.listdir(WORKFLOWS):
            with open(os.path.join(WORKFLOWS, nome), encoding="utf-8") as f:
                self.assertNotIn("canario_forward_it", sem_comentarios(f.read()),
                                 nome)


class AAuditoriaSoLe(unittest.TestCase):
    """O que sobrou tem valor e nenhum poder."""

    def setUp(self):
        with open(os.path.join(WORKFLOWS, "auditoria-live.yml"),
                  encoding="utf-8") as f:
            self.wf = sem_comentarios(f.read())

    def test_nao_aplica_migration(self):
        self.assertNotIn("cadeia_canonica", self.wf)
        self.assertNotIn("migrations \"$", self.wf)

    def test_nao_recebe_a_chave_de_escrita(self):
        """`SUPABASE_SECRET_KEY` e `SUPABASE_URL` só existiam para escrever no
        Storage. Já não há o que escrever — e uma credencial que ninguém usa é
        uma credencial que um dia alguém usa."""
        self.assertNotIn("SUPABASE_SECRET_KEY", self.wf)
        self.assertNotIn("SUPABASE_URL", self.wf)
        self.assertIn("SUPABASE_DB_URL", self.wf)

    def test_o_script_dela_nao_escreve(self):
        with open(os.path.join(RAIZ, "provas", "auditoria_live.sh"),
                  encoding="utf-8") as f:
            corpo = "\n".join(l for l in f if not l.strip().startswith("#"))
        for verbo in ("insert into", "update ", "delete from", "drop ",
                      "alter table", "create table"):
            self.assertNotIn(verbo, corpo.lower(), verbo)

    def test_um_empurrao_por_esta_porta_nao_escreve_nada(self):
        """O gatilho por caminho é seguro **porque** o job não tem poder — não
        porque alguém se lembre de não empurrar."""
        self.assertIn("push:", self.wf)
        self.assertNotIn("preservar", self.wf)
        self.assertNotIn("storage", self.wf.lower())


class NenhumaOutraPortaGanhouPoder(unittest.TestCase):
    """Quem pode escrever produção continua a ser quem já podia."""

    # A LISTA E MEDIDA, NAO LEMBRADA. Escrevi-a de cabeca com quatro nomes e
    # o teste apanhou-me: `calendario-regressoes` e `supabase-conexao` ja
    # tinham a chave antes desta missao. Nao sao portas novas — sao portas que
    # eu nao tinha visto, e o teste servir para isso e o ponto dele.
    ESCRITORES = {"supabase-migrate.yml", "supabase-fichas-adama.yml",
                  "supabase-raw-roundtrip.yml", "supabase-storage.yml",
                  "supabase-conexao.yml", "calendario-regressoes.yml"}

    def test_o_conjunto_de_escritores_nao_cresceu(self):
        # ⚠️ A PORTA DE PRODUÇÃO É QUEM ESCREVE ONDE PRODUÇÃO MORA.
        # A fase italiana (2026-09-16) corre `cadeia_canonica.sh migrations`
        # contra um PostgreSQL DESCARTÁVEL em localhost — contá-la como porta
        # de produção diria que um banco que nasce e morre com o job é
        # produção. A isenção vive em `escreve_producao()` (módulo), decide
        # LINHA FÍSICA a linha física, e exige a DSN literal da bancada na
        # PRÓPRIA linha da cadeia — ver o aviso ali e o know-how §131: a
        # primeira versão colava o ficheiro antes de decidir, e isentava o
        # ficheiro inteiro. O texto vai CRU, com as quebras de linha vivas.
        achados = set()
        for nome in os.listdir(WORKFLOWS):
            with open(os.path.join(WORKFLOWS, nome), encoding="utf-8") as f:
                t = f.read()
            if escreve_producao(t):
                achados.add(nome)
        novos = achados - self.ESCRITORES
        self.assertEqual(novos, set(), "porta de escrita nova: %s" % novos)
        # e a auditoria NUNCA pode entrar nesta lista
        self.assertNotIn("auditoria-live.yml", achados)
        self.assertNotIn("canario-022.yml", achados)

    def test_o_que_escreve_migration_corre_so_a_mao(self):
        with open(os.path.join(WORKFLOWS, "supabase-migrate.yml"),
                  encoding="utf-8") as f:
            t = sem_comentarios(f.read())
        cabeca = t[t.index("on:"):t.index("permissions:")]
        self.assertIn("workflow_dispatch:", cabeca)
        self.assertNotIn("supabase/migrations/", cabeca,
                         "um empurrao numa migration passaria a aplica-la")


class AIsencaoDaBancadaEEstreitaDeVerdade(unittest.TestCase):
    """Os contraexemplos da revisão independente, agora como regressão.

    A revisão (2026-09-17, know-how §131) provou que a isenção antiga era de
    FICHEIRO quando prometia ser de LINHA: um escritor de produção passava
    calado se qualquer outra linha do ficheiro tivesse as strings benignas.
    Estes testes reproduzem exatamente esses ataques — se `escreve_producao`
    voltar a colar linhas ou a casar por substring, eles reprovam.
    """

    LEGITIMA = ('      PATH="$PGBIN:$PATH" bash motor/cadeia_canonica.sh '
                "migrations 'postgresql://postgres:descartavel"
                "@localhost:54329/descartavel'")
    ESCRITOR = ('      - run: bash motor/cadeia_canonica.sh migrations '
                '"$SUPABASE_DB_URL"')

    def test_1_a_linha_legitima_da_bancada_continua_permitida(self):
        self.assertFalse(escreve_producao(self.LEGITIMA))
        # e 127.0.0.1 é o mesmo host local
        self.assertFalse(escreve_producao(
            self.LEGITIMA.replace("@localhost", "@127.0.0.1")))

    def test_2_o_escritor_de_producao_e_detectado_sozinho(self):
        self.assertTrue(escreve_producao(self.ESCRITOR))

    def test_3_o_ataque_da_revisao_o_workflow_real_mais_um_escritor(self):
        # O BYPASS QUE REPROVOU A ENTREGA: o sintonia-scrap.yml inteiro, com a
        # linha legítima do 5a-IT dentro, mais um escritor acrescentado. A
        # guarda antiga passava isto calada; esta NÃO PODE.
        with open(os.path.join(WORKFLOWS, "sintonia-scrap.yml"),
                  encoding="utf-8") as f:
            real = f.read()
        self.assertTrue(escreve_producao(real + "\n" + self.ESCRITOR + "\n"))

    def test_4_isca_na_linha_anterior_nao_esconde(self):
        isca = '      - run: echo "postgresql://x@localhost:54329/descartavel"'
        self.assertTrue(escreve_producao(isca + "\n" + self.ESCRITOR))

    def test_5_isca_na_linha_seguinte_nao_esconde(self):
        isca = '      - run: echo "postgresql://x@localhost:54329/descartavel"'
        self.assertTrue(escreve_producao(self.ESCRITOR + "\n" + isca))

    def test_6_comentario_nao_isenta_e_nao_acusa(self):
        # comentário com as strings benignas não esconde o escritor…
        self.assertTrue(escreve_producao(
            "# bancada @localhost /descartavel\n" + self.ESCRITOR))
        # …e comentário citando o secret não acusa documentação
        self.assertFalse(escreve_producao(
            "# este workflow nao recebe SUPABASE_SECRET_KEY\n"
            "      - run: echo ola"))

    def test_7_isca_inline_na_propria_linha_nao_isenta(self):
        # a dupla de substrings na MESMA linha do escritor também não basta:
        # a isenção exige a DSN literal como ARGUMENTO da cadeia
        self.assertTrue(escreve_producao(
            self.ESCRITOR + "  # @localhost /descartavel"))
        self.assertTrue(escreve_producao(
            '      - run: bash motor/cadeia_canonica.sh migrations '
            '"$SUPABASE_DB_URL" && echo "@localhost/descartavel"'))

    def test_8_hosts_e_bancos_parecidos_reprovam(self):
        for dsn in ("postgresql://x@localhost.evil.com:5432/descartavel",
                    "postgresql://x@localhost:54329/descartavel_prod",
                    "postgresql://x@localhost:54329/descartavel.evil",
                    "postgresql://x@evillocalhost:54329/descartavel"):
            linha = ("      - run: bash motor/cadeia_canonica.sh migrations "
                     "'%s'" % dsn)
            self.assertTrue(escreve_producao(linha), dsn)

    def test_9_query_string_nao_ganha_isencao(self):
        # a libpq OBEDECE ao ?host= — uma DSN «local» com host na query
        # conecta noutro servidor. Provado no metal na revisão de 2026-09-17.
        for dsn in ("postgresql://x@localhost:54329/descartavel"
                    "?host=db.abc.supabase.co",
                    "postgresql://x@localhost:54329/descartavel"
                    "?hostaddr=203.0.113.9"):
            linha = ("      - run: bash motor/cadeia_canonica.sh migrations "
                     "'%s'" % dsn)
            self.assertTrue(escreve_producao(linha), dsn)

    def test_10_variavel_no_lugar_da_dsn_fecha_a_porta(self):
        # destino desconhecido NÃO é destino descartável
        for arg in ('"$DSN_QUE_PARECE_INOCENTE"', "$URL", "'$BANCADA'"):
            linha = ("      - run: bash motor/cadeia_canonica.sh "
                     "migrations %s" % arg)
            self.assertTrue(escreve_producao(linha), arg)

    def test_11_o_secret_continua_acusando(self):
        self.assertTrue(escreve_producao(
            "      SUPABASE_SECRET_KEY: ${{ secrets.SUPABASE_SECRET_KEY }}"))

    def test_12_continuacao_de_linha_nao_engana(self):
        # a cadeia numa linha e a DSN na seguinte: a linha da cadeia não
        # prova o destino NELA — fecha-se a porta (fail-closed; o workflow
        # real mantém a chamada numa linha só)
        self.assertTrue(escreve_producao(
            "      - run: bash motor/cadeia_canonica.sh migrations \\\n"
            "          'postgresql://postgres:x@db.abc.supabase.co/postgres'"))
        # e partir ANTES do `migrations` também não esconde: a linha com a
        # cadeia termina em `\` sem provar destino — acusa igual
        self.assertTrue(escreve_producao(
            "      - run: bash motor/cadeia_canonica.sh \\\n"
            '          migrations "$SUPABASE_DB_URL"'))

    # Os três furos que o red team abriu na PRIMEIRA versão deste conserto
    # (2026-09-17) — cada um fica aqui para nunca mais abrir.

    def test_13_espaco_dobrado_ou_tab_e_o_mesmo_comando(self):
        # o bash colapsa espaço; um gatilho por substring com UM espaço não
        for sep in ("  ", "\t", " \t "):
            linha = ('      - run: bash motor/cadeia_canonica.sh%smigrations '
                     '"$SUPABASE_DB_URL"' % sep)
            self.assertTrue(escreve_producao(linha), repr(sep))
        # e a isenção continua a valer com espaço dobrado na linha legítima
        self.assertFalse(escreve_producao(
            self.LEGITIMA.replace("migrations '", "migrations  '")))

    def test_14_folded_scalar_do_yaml_e_uma_linha_logica(self):
        # `run: >` dobra as linhas ANTES de o shell as ver — a guarda tem de
        # ler na mesma granularidade
        self.assertTrue(escreve_producao(
            "      - run: >\n"
            "          bash motor/cadeia_canonica.sh\n"
            '          migrations "$SUPABASE_DB_URL"\n'))
        self.assertTrue(escreve_producao(
            "      - run: >-\n"
            "          bash motor/cadeia_canonica.sh\n"
            '          importacoes "$SUPABASE_DB_URL"\n'))
        # dobrada, a chamada LEGÍTIMA continua legítima
        self.assertFalse(escreve_producao(
            "      - run: >\n"
            "          bash motor/cadeia_canonica.sh migrations\n"
            "          'postgresql://postgres:descartavel"
            "@localhost:54329/descartavel'\n"))
        # e os cabeçalhos de fold que a spec também permite — indicador de
        # indentação e comentário — dobram IGUAL (2º round do red team)
        for cabecalho in (">2", ">-2", ">+2", ">2-", "> # nada", ">- # x"):
            self.assertTrue(escreve_producao(
                "      - run: %s\n"
                "          bash motor/cadeia_canonica.sh\n"
                '          migrations "$SUPABASE_DB_URL"\n' % cabecalho),
                cabecalho)

    def test_15_isca_completa_na_mesma_linha_nao_isenta_o_escritor(self):
        # o ataque mais fino: escritor real + uma invocação-isca COMPLETA
        # (cadeia + DSN benigna) colada depois — cada invocação tem de
        # provar o SEU argumento
        bancada = ("cadeia_canonica.sh migrations postgresql://postgres:"
                   "descartavel@localhost:54329/descartavel")
        self.assertTrue(escreve_producao(
            '      - run: bash motor/cadeia_canonica.sh migrations '
            '"$SUPABASE_DB_URL" # %s' % bancada))
        self.assertTrue(escreve_producao(
            '      - run: bash motor/cadeia_canonica.sh migrations '
            '"$SUPABASE_DB_URL" ; echo %s' % bancada))

    def test_16_o_nome_do_secret_partido_nao_escapa(self):
        self.assertTrue(escreve_producao(
            "      - run: export SUPABASE_SECRET\\\n"
            "_KEY=abc && ./escreve.sh"))

    def test_17_plain_scalar_multilinha_dobra_sem_sinal_nenhum(self):
        # o YAML dobra `run: comando` com continuação indentada — sem `>`,
        # sem `\`. O shell recebe UMA linha; a guarda tem de acusar igual
        # (3º round do red team)
        self.assertTrue(escreve_producao(
            "      - run: bash motor/cadeia_canonica.sh\n"
            '          migrations "$SUPABASE_DB_URL"\n'))
        # e as variantes com aspas multilinha dobram do mesmo jeito
        self.assertTrue(escreve_producao(
            '      - run: "bash motor/cadeia_canonica.sh\n'
            '          migrations $SUPABASE_DB_URL"\n'))
        self.assertTrue(escreve_producao(
            "      - run: 'bash motor/cadeia_canonica.sh\n"
            "          importacoes $SUPABASE_DB_URL'\n"))
        # a chamada legítima partida em plain scalar continua legítima:
        # a vista dobrada prova o argumento dela na própria invocação
        self.assertFalse(escreve_producao(
            "      - run: bash motor/cadeia_canonica.sh\n"
            "          migrations 'postgresql://postgres:descartavel"
            "@localhost:54329/descartavel'\n"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
