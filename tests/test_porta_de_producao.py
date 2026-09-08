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
        achados = set()
        for nome in os.listdir(WORKFLOWS):
            with open(os.path.join(WORKFLOWS, nome), encoding="utf-8") as f:
                t = sem_comentarios(f.read())
            escreve = ("SUPABASE_SECRET_KEY" in t
                       or "cadeia_canonica.sh migrations" in t
                       or "cadeia_canonica.sh importacoes" in t)
            if escreve:
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
