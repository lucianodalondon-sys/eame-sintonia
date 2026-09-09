#!/usr/bin/env python3
"""RED TEAM DO SECURITY RATCHET — o portao morde?

    UM PORTAO QUE NAO CORRE NAO E UM PORTAO.
    E UM PORTAO QUE NUNCA FOI ATACADO NAO SE SABE SE MORDE.

Cada prova monta um repositorio minimo num directorio temporario, congela a
divida, aplica UMA mutacao perigosa e exige que o portao a recuse nomeando-a.
Nada aqui toca a arvore real, nenhuma base de dados e nenhum segredo.

As fixtures com forma de segredo sao construidas em tempo de execucao e nunca
escritas na arvore versionada:

    FIXTURE WITH SECRET SHAPE IS SECRET TO THE SCANNER.

    python3 -m unittest tests.test_security_ratchet -v
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile, unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
RATCHET = RAIZ / "security" / "ratchet.py"


class Casinha:
    """Um repositorio minimo, mas com as pecas reais que o portao le."""

    def __enter__(self):
        self.dir = pathlib.Path(tempfile.mkdtemp(prefix="ratchet-redteam-"))
        (self.dir / "security").mkdir()
        for f in ("ratchet.py", "superficie_publica.py", "projeccao.py"):
            shutil.copy(RAIZ / "security" / f, self.dir / "security" / f)
        (self.dir / ".github" / "workflows").mkdir(parents=True)
        (self.dir / "supabase" / "migrations").mkdir(parents=True)
        cli = self.dir / "italia-portale" / "client"
        cli.mkdir(parents=True)
        (self.dir / "vercel.json").write_text(
            json.dumps({"outputDirectory": "italia-portale/client"}), encoding="utf-8")
        (self.dir / ".vercelignore").write_text("*.md\n/supabase\n", encoding="utf-8")
        self.wf("limpo.yml", "name: limpo\npermissions:\n  contents: read\non:\n  push:\n")
        self.sql("001_base.sql",
                 "create table public.a (id int);\n"
                 "alter table public.a enable row level security;\n")
        self.cliente("app.js", 'var X = {"TITLE": "ok"};\n')
        return self

    def __exit__(self, *a):
        shutil.rmtree(self.dir, ignore_errors=True)

    def wf(self, nome, txt):
        (self.dir / ".github" / "workflows" / nome).write_text(txt, encoding="utf-8")

    def sql(self, nome, txt):
        (self.dir / "supabase" / "migrations" / nome).write_text(txt, encoding="utf-8")

    def cliente(self, nome, txt):
        p = self.dir / "italia-portale" / "client" / nome
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")

    def _correr(self, *args):
        env = dict(os.environ, SINTONIA_RATCHET_RAIZ=str(self.dir))
        return subprocess.run([sys.executable, str(self.dir / "security" / "ratchet.py"), *args],
                              capture_output=True, text=True, env=env, cwd=self.dir)

    def congelar(self):
        r = self._correr("--freeze")
        assert r.returncode == 0, r.stdout + r.stderr
        return self

    def portao(self):
        return self._correr()


class RedTeamRatchet(unittest.TestCase):

    def _morde(self, mutar, classe):
        with Casinha() as c:
            c.congelar()
            base = c.portao()
            self.assertEqual(base.returncode, 0,
                             f"a casa limpa ja falhava:\n{base.stdout}")
            mutar(c)
            depois = c.portao()
            self.assertEqual(depois.returncode, 1,
                             f"a mutacao {classe} passou em silencio:\n{depois.stdout}")
            self.assertIn(classe, depois.stdout,
                          f"mordeu, mas nao disse porque:\n{depois.stdout}")
            return depois.stdout

    # ── CI / cadeia de fornecimento ───────────────────────────────────────
    def test_pull_request_target_e_recusado(self):
        self._morde(lambda c: c.wf("mau.yml",
                    "name: mau\npermissions:\n  contents: read\non:\n  pull_request_target:\n"),
                    "NEW_PULL_REQUEST_TARGET")

    def test_write_all_e_recusado(self):
        self._morde(lambda c: c.wf("mau.yml", "name: mau\npermissions: write-all\non:\n  push:\n"),
                    "NEW_WRITE_ALL_PERMISSION")

    def test_workflow_sem_permissions_e_recusado(self):
        self._morde(lambda c: c.wf("mau.yml", "name: mau\non:\n  push:\n"),
                    "WORKFLOW_SEM_PERMISSIONS")

    def test_self_hosted_em_pull_request_e_recusado(self):
        self._morde(lambda c: c.wf("mau.yml",
                    "name: mau\npermissions:\n  contents: read\n"
                    "on:\n  pull_request:\njobs:\n  j:\n    runs-on: [self-hosted, Windows]\n"),
                    "SELF_HOSTED_EM_EVENTO_NAO_CONFIAVEL")

    def test_comentar_pull_request_target_nao_e_achado(self):
        """Falso positivo tambem e defeito: um portao que acusa um comentario
        ensina a desliga-lo."""
        with Casinha() as c:
            c.congelar()
            c.wf("doc.yml", "# nunca usar pull_request_target aqui\n"
                            "name: doc\npermissions:\n  contents: read\non:\n  push:\n")
            self.assertEqual(c.portao().returncode, 0)

    # ── fronteira publicada ───────────────────────────────────────────────
    def test_novo_dado_pessoal_publico_e_recusado(self):
        saida = self._morde(lambda c: c.cliente("novo.json", '{"EMAIL": "x"}'),
                            "NEW_PERSONAL_DATA_FIELD_IN_PUBLIC_OUTPUT")
        self.assertIn("EMAIL", saida)
        self.assertIn("novo.json", saida)

    def test_dado_pessoal_fora_da_superficie_publicada_nao_e_achado(self):
        """A prova tem de conhecer a fronteira. Um ORCID num artefacto interno
        que o .vercelignore nao publica nao e exposicao publica."""
        with Casinha() as c:
            c.congelar()
            (c.dir / "research").mkdir()
            (c.dir / "research" / "interno.json").write_text('{"ORCID": "x"}', encoding="utf-8")
            self.assertEqual(c.portao().returncode, 0)

    def test_novo_telefone_publico_e_recusado(self):
        self._morde(lambda c: c.cliente("pessoas.json", '{"PHONE": "x"}'),
                    "NEW_PERSONAL_DATA_FIELD_IN_PUBLIC_OUTPUT")

    def test_nova_formula_proprietaria_publica_e_recusada(self):
        self._morde(lambda c: c.cliente("motor.json", '{"SCORE_FORMULA": "a/b"}'),
                    "NEW_PUBLIC_ENGINE_EXPOSURE")

    def test_prompt_de_modelo_publicado_e_recusado(self):
        self._morde(lambda c: c.cliente("ia.json", '{"SYSTEM_PROMPT": "..."}'),
                    "NEW_PUBLIC_ENGINE_EXPOSURE")

    def test_source_map_proprio_publicado_e_recusado(self):
        self._morde(lambda c: c.cliente("app.js.map", "{}"),
                    "NEW_OWN_SOURCE_MAP_PUBLISHED")

    def test_source_map_de_vendor_nao_e_achado(self):
        with Casinha() as c:
            c.congelar()
            c.cliente("vendor/lib.min.js", "//# sourceMappingURL=lib.js.map\n")
            self.assertEqual(c.portao().returncode, 0)

    # ── .vercelignore: a fronteira e uma regra, e a regra pode ser apagada ──
    def test_apagar_regra_do_vercelignore_expoe_e_e_recusado(self):
        """Nao se ataca a lista de ficheiros: ataca-se a REGRA que a produz.
        Apagar '/supabase' do .vercelignore publica o esquema inteiro."""
        with Casinha() as c:
            (c.dir / "supabase" / "esquema.sql").write_text("select 1;", encoding="utf-8")
            c.congelar()
            self.assertEqual(c.portao().returncode, 0)
            # o esquema passa para dentro do outputDirectory e a regra desaparece
            shutil.copy(c.dir / "supabase" / "esquema.sql",
                        c.dir / "italia-portale" / "client" / "esquema.sql")
            (c.dir / ".vercelignore").write_text("*.md\n", encoding="utf-8")
            r = c.portao()
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("NEW_SENSITIVE_PATH_PUBLISHED", r.stdout)

    # ── base de dados ─────────────────────────────────────────────────────
    def test_nova_tabela_sem_rls_e_recusada(self):
        self._morde(lambda c: c.sql("002_nova.sql", "create table public.b (id int);\n"),
                    "NEW_TABLE_WITHOUT_RLS")

    def test_tabela_nova_com_rls_declarada_passa(self):
        with Casinha() as c:
            c.congelar()
            c.sql("002_nova.sql", "create table public.b (id int);\n"
                                  "alter table public.b enable row level security;\n")
            self.assertEqual(c.portao().returncode, 0)

    # ── a divida herdada nao pode bloquear ────────────────────────────────
    def test_divida_congelada_nao_bloqueia(self):
        """KNOWN DEBT != NEW REGRESSION. Uma exposicao ja conhecida fica visivel
        no relatorio e deixa o desenvolvimento seguir."""
        with Casinha() as c:
            c.cliente("velho.json", '{"ORCID": "x"}')
            c.congelar()
            r = c.portao()
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn("divida herdada", r.stdout)
            self.assertNotIn("REGRESSAO NOVA", r.stdout)

    def test_o_erro_diz_o_que_fazer_e_nunca_o_valor(self):
        """Erro accionavel: classe, ficheiro e campo. O VALOR do campo nunca."""
        with Casinha() as c:
            c.congelar()
            c.cliente("fuga.json", '{"PERSONAL_EMAIL": "quemquerqueseja@exemplo.pt"}')
            saida = c.portao().stdout
            self.assertIn("PERSONAL_EMAIL", saida)
            self.assertIn("fuga.json", saida)
            self.assertNotIn("quemquerqueseja", saida)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class WorkflowQueNaoCorre(unittest.TestCase):
    """Um `:` dentro do nome de um passo fez o proprio SECURITY CHECK nao
    arrancar: a corrida deu failure com ZERO jobs. Nao ha log a ler, nao ha
    passo a inspeccionar — o portao simplesmente nao existiu naquele commit.

        UM PORTAO COM ERRO DE SINTAXE NAO FALHA: DESAPARECE.
    """

    def test_yaml_invalido_e_recusado(self):
        with Casinha() as c:
            c.congelar()
            c.wf("partido.yml",
                 "name: x\npermissions:\n  contents: read\non:\n  push:\njobs:\n  j:\n"
                 "    steps:\n      - name: 5 · o ratchet: nenhuma exposicao\n")
            r = c.portao()
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("WORKFLOW_YAML_INVALIDO", r.stdout)
            self.assertIn("linha", r.stdout, "tem de dizer ONDE, nao so que falhou")

    def test_todos_os_workflows_reais_analisam(self):
        """A prova que teria evitado a corrida vazia, a correr na arvore real."""
        import yaml
        for w in sorted((RAIZ / ".github" / "workflows").glob("*.yml")):
            with self.subTest(workflow=w.name):
                yaml.safe_load(w.read_text(encoding="utf-8"))


class ProjeccaoParaOCliente(unittest.TestCase):
    """DISPLAY INPUT != COMPUTATION INPUT.

    O motor nao corre no browser — medido, nao suposto. O que viaja e o corpus,
    e dentro dele os campos internos do metodo: como uma proveniencia foi
    recuperada, porque uma evidencia conta. Esses ensinam a receita.

        UM CAMPO QUE NINGUEM LE NAO E APRESENTACAO. E EXPORTACAO.
    """

    def _casa_com_pacote(self, c, corpo, codigo_ui=""):
        c.cliente("italy-v21.js", "window.ITALY = " + corpo + ";\n")
        c.cliente("portale.html", "<script>" + codigo_ui + "</script>")

    def test_campo_interno_novo_e_recusado(self):
        with Casinha() as c:
            self._casa_com_pacote(c, '{"a":[{"NOME":1},{"NOME":2}]}', 'x.NOME')
            c.congelar()
            self.assertEqual(c.portao().returncode, 0, "a casa limpa ja falhava")
            self._casa_com_pacote(
                c, '{"a":[{"NOME":1,"PROVENANCE_STRENGTH":"x"},'
                   '{"NOME":2,"PROVENANCE_STRENGTH":"y"}]}', 'x.NOME')
            r = c.portao()
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("NEW_INTERNAL_FIELD_EXPOSED_TO_CLIENT", r.stdout)
            self.assertIn("PROVENANCE_STRENGTH", r.stdout)

    def test_campo_novo_que_a_interface_LE_nao_e_achado(self):
        """Um campo novo que a tela mostra e apresentacao, e passa."""
        with Casinha() as c:
            self._casa_com_pacote(c, '{"a":[{"NOME":1},{"NOME":2}]}', 'x.NOME')
            c.congelar()
            self._casa_com_pacote(
                c, '{"a":[{"NOME":1,"TITULO":"x"},{"NOME":2,"TITULO":"y"}]}',
                'x.NOME + x.TITULO')
            self.assertEqual(c.portao().returncode, 0, c.portao().stdout)

    def test_identificador_novo_nao_e_campo(self):
        """UM CAMPO DE ESQUEMA REPETE-SE. UM IDENTIFICADOR NAO.
        Um caso novo no pacote nao pode acordar o portao — seria o caminho mais
        curto para alguem o desligar."""
        with Casinha() as c:
            self._casa_com_pacote(c, '{"a":[{"NOME":1},{"NOME":2}]}', 'x.NOME')
            c.congelar()
            self._casa_com_pacote(
                c, '{"a":[{"NOME":1},{"NOME":2}],"OPP_75C37DED9160":{"x":1}}', 'x.NOME')
            self.assertEqual(c.portao().returncode, 0, c.portao().stdout)

    def test_campo_citado_so_num_comentario_nao_conta_como_lido(self):
        """Um campo citado num comentario nao e um campo lido: o comentario nao
        chega ao ecra de ninguem."""
        with Casinha() as c:
            self._casa_com_pacote(c, '{"a":[{"NOME":1},{"NOME":2}]}', 'x.NOME')
            c.congelar()
            self._casa_com_pacote(
                c, '{"a":[{"NOME":1,"SEGREDO_DO_METODO":"x"},'
                   '{"NOME":2,"SEGREDO_DO_METODO":"y"}]}',
                '/* usamos x.SEGREDO_DO_METODO um dia */ x.NOME')
            r = c.portao()
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("SEGREDO_DO_METODO", r.stdout)
