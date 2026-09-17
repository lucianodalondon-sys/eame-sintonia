#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUAL `psql` O RUNTIME USA — o dono, o contrato, e a prova contra Postgres real.

    py -m pytest tests/test_cliente_postgres.py

O QUE ACONTECEU, E POR QUE ISTO EXISTE
--------------------------------------
O replay canário 3 pelo workflow real (run GitHub 35232024024, 2026-09-17,
know-how §135) atravessou a bancada descartável, o Sala gate e o egresso IT,
adquiriu IT-T3-002 da rede — e caiu na primeira chamada do runtime ao banco:

    guarda/memoria_postgres.py   subprocess.run(["psql", …])  →  FileNotFoundError

Três donos lançavam `"psql"` pelo nome e confiavam no PATH do processo; o
Sala gate tinha dito PASS sem abrir ligação. O mecanismo exato pelo qual o
PATH do job não trazia o psql NÃO ficou provado — e a lição não depende dele:

    DESCOBERTA IMPLÍCITA POR PATH NÃO É UM CONTRATO.
    UM PORTÃO QUE MEDE CONFIGURAÇÃO NÃO MEDE CONETIVIDADE.

Estes testes guardam:
    1  o dono é UM (`guarda/cliente_postgres.py`), a variável é UMA
       (`SINTONIA_PSQL_EXE`), e a resolução falha fechada;
    2  declaração explícita inválida NÃO cai para o PATH;
    3  as três portas do runtime pedem o executável ao dono (por AST);
    4  o workflow DECLARA o psql em caminho nativo no passo 5a-IT;
    5  o Sala gate sonda o banco de verdade — `select 1` pelo mesmo psql;
    6  a prova como PROCESSO contra PostgreSQL 16 real, com o PATH sem psql:
       `provas/o_cliente_psql_e_declarado.py` (o último teste corre-a).
"""
import ast
import io
import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
from guarda import cliente_postgres as cp  # noqa: E402


def _fonte(*partes):
    return io.open(os.path.join(RAIZ, *partes), encoding="utf-8").read()


def _exe_falso(pasta, nome):
    caminho = os.path.join(pasta, nome)
    io.open(caminho, "wb").write(b"MZ")
    return caminho


class ODonoResolveEFalhaFechado(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cliente psql ")   # com espaço, de propósito
        self.psql = _exe_falso(self.tmp, "psql.exe")
        self.outro = _exe_falso(self.tmp, "pg_ctl.exe")
        self.sem_path = {"PATH": self.tmp_vazio()}

    def tmp_vazio(self):
        return tempfile.mkdtemp(prefix="sem-psql-")

    def test_1_declarado_e_valido_e_usado_exatamente(self):
        env = {"SINTONIA_PSQL_EXE": self.psql, "PATH": ""}
        self.assertEqual(cp.resolver_psql(env), self.psql)
        self.assertEqual(cp.comando_psql("-X", "-c", "select 1", "dsn", env=env)[0], self.psql)
        r = cp.como_foi_resolvido(env)
        self.assertEqual((r["ORIGEM"], r["PSQL"]), ("DECLARADO", self.psql))

    def test_2_caminho_com_espaco_serve(self):
        self.assertIn(" ", self.psql)
        self.assertEqual(cp.porque_nao_serve(self.psql), "")

    def test_3_declarado_inexistente_recusa(self):
        env = {"SINTONIA_PSQL_EXE": os.path.join(self.tmp, "nao.exe"), "PATH": ""}
        with self.assertRaises(cp.ClientePostgresAusente) as cx:
            cp.resolver_psql(env)
        self.assertIn("nao existe", str(cx.exception))

    def test_4_declarado_outro_executavel_recusa(self):
        env = {"SINTONIA_PSQL_EXE": self.outro, "PATH": ""}
        with self.assertRaises(cp.ClientePostgresAusente) as cx:
            cp.resolver_psql(env)
        self.assertIn("nao se chama psql", str(cx.exception))

    def test_5_forma_POSIX_nao_e_nativa_e_recusa(self):
        for c in ("/c/Users/London1/orca/pgtmp/pgsql/bin/psql.exe", "/d/pg/bin/psql"):
            self.assertIn("POSIX", cp.porque_nao_serve(c), c)
        # `/usr/bin/psql` (Linux) não é a forma POSIX-de-unidade; cai no isfile
        self.assertNotIn("POSIX", cp.porque_nao_serve("/usr/bin/psql"))

    def test_5b_caminho_relativo_recusa(self):
        """Relativo resolve-se contra o cwd de cada subprocesso: dois processos,
        dois psql. O contrato e caminho nativo COMPLETO."""
        self.assertIn("relativo", cp.porque_nao_serve("psql.exe"))
        self.assertIn("relativo", cp.porque_nao_serve(os.path.join("bin", "psql.exe")))

    def test_6_declaracao_invalida_NAO_cai_para_o_PATH(self):
        """O erro de configuração não pode ser mascarado por um acerto do PATH."""
        env = {"SINTONIA_PSQL_EXE": os.path.join(self.tmp, "nao.exe"), "PATH": self.tmp}
        with self.assertRaises(cp.ClientePostgresAusente) as cx:
            cp.resolver_psql(env)
        self.assertIn("Nao se cai para o PATH", str(cx.exception))

    def test_7_sem_declaracao_usa_o_PATH_e_declarado_diferente_vence(self):
        outra = tempfile.mkdtemp(prefix="outro-psql-")
        psql2 = _exe_falso(outra, "psql.exe")
        env = {"SINTONIA_PSQL_EXE": "", "PATH": self.tmp, "PATHEXT": ".EXE"}
        self.assertEqual(os.path.normcase(cp.resolver_psql(env)), os.path.normcase(self.psql))
        env["SINTONIA_PSQL_EXE"] = psql2
        self.assertEqual(cp.resolver_psql(env), psql2)

    def test_8_nada_declarado_e_PATH_sem_psql_falha_com_a_frase_certa(self):
        env = {"SINTONIA_PSQL_EXE": "", "PATH": self.tmp_vazio()}
        with self.assertRaises(cp.ClientePostgresAusente) as cx:
            cp.resolver_psql(env)
        self.assertIn("SINTONIA_PSQL_EXE", str(cx.exception))
        r = cp.como_foi_resolvido(env)
        self.assertEqual((r["ORIGEM"], r["PSQL"]), ("AUSENTE", None))

    def test_9_importar_nao_le_ambiente_nem_toca_no_disco(self):
        fonte = _fonte("guarda", "cliente_postgres.py")
        corpo = fonte.split('"""', 2)[2]
        topo = [l for l in corpo.splitlines() if l and not l.startswith((" ", "#", "def ", "class ", "import ", "from "))]
        for l in topo:
            self.assertNotIn("os.environ", l, l)
        self.assertNotIn("psycopg", fonte)
        self.assertNotIn("SUPABASE", fonte)


class OsDonosDoRuntimePedemAoDono(unittest.TestCase):
    DONOS = ("guarda/memoria_postgres.py", "coleta/coleta_checkpoint.py",
             "admissao/sala_de_espera.py")

    def test_1_nenhum_dos_tres_lanca_psql_pelo_nome_nu(self):
        for rel in self.DONOS:
            arvore = ast.parse(_fonte(*rel.split("/")))
            nus = [no.lineno for no in ast.walk(arvore)
                   if isinstance(no, ast.List) and no.elts
                   and isinstance(no.elts[0], ast.Constant) and no.elts[0].value == "psql"]
            self.assertEqual(nus, [], "%s: psql pelo nome nu nas linhas %s" % (rel, nus))

    def test_2_os_tres_importam_o_mesmo_dono(self):
        for rel in self.DONOS:
            self.assertIn("guarda.cliente_postgres import", _fonte(*rel.split("/")), rel)

    def test_3_ha_um_so_dono_da_variavel(self):
        donos = []
        for pasta in ("guarda", "coleta", "admissao", "orquestrador", "motor", "superficie"):
            base = os.path.join(RAIZ, pasta)
            for raiz, dirs, ficheiros in os.walk(base):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                for f in ficheiros:
                    if f.endswith(".py") and 'VARIAVEL = "SINTONIA_PSQL_EXE"' in _fonte(raiz, f):
                        donos.append(os.path.relpath(os.path.join(raiz, f), RAIZ))
        self.assertEqual(donos, [os.path.join("guarda", "cliente_postgres.py")])

    def test_4_o_dono_nao_importa_provas_nem_decide_dsn(self):
        corpo = _fonte("guarda", "cliente_postgres.py").split('"""', 2)[2]
        self.assertNotIn("import provas", corpo)
        self.assertNotIn("from provas", corpo)
        self.assertNotIn("banco_descartavel", corpo)
        self.assertNotIn("postgresql://", corpo)


class OWorkflowDeclaraEmCaminhoNativo(unittest.TestCase):
    def _passo_5a(self):
        texto = _fonte(".github", "workflows", "sintonia-scrap.yml")
        inicio = texto.index("5a-IT · a bancada italiana nasce")
        fim = texto.index("- name:", inicio + 10)
        return texto[inicio:fim]

    def test_1_o_5a_IT_declara_SINTONIA_PSQL_EXE_por_cygpath(self):
        corpo = self._passo_5a()
        self.assertIn('PSQL_NATIVO="$(cygpath -w "$PGBIN/psql.exe")"', corpo)
        self.assertIn('echo "SINTONIA_PSQL_EXE=$PSQL_NATIVO" >> "$GITHUB_ENV"', corpo)

    def test_2_a_declaracao_vem_antes_dos_portoes_e_falha_se_o_cygpath_faltar(self):
        corpo = self._passo_5a()
        self.assertIn("command -v cygpath", corpo)
        self.assertLess(corpo.index("SINTONIA_PSQL_EXE="), corpo.index('echo "$PGBIN" >> "$GITHUB_PATH"'))

    def test_3_o_workflow_nao_declara_uma_segunda_variavel_de_psql(self):
        texto = _fonte(".github", "workflows", "sintonia-scrap.yml")
        import re
        nomes = set(re.findall(r'echo "([A-Z_]*PSQL[A-Z_]*)=', texto))
        self.assertEqual(nomes, {"SINTONIA_PSQL_EXE"})


class OSalaGateSondaOBanco(unittest.TestCase):
    def test_1_exigir_canonica_chama_sondar(self):
        fonte = _fonte("admissao", "sala_de_espera.py")
        corpo = fonte[fonte.index("def exigir_canonica"):]
        corpo = corpo[:corpo.index("\ndef ", 10)]
        self.assertIn(".sondar()", corpo)

    def test_2_a_sonda_e_uma_leitura_inofensiva(self):
        fonte = _fonte("admissao", "sala_de_espera.py")
        corpo = fonte[fonte.index("    def sondar(self):\n        \"\"\"UMA leitura"):]
        corpo = corpo[:corpo.index("    def _consultar")]
        self.assertIn('self._consultar("select 1")', corpo)
        for proibido in ("insert ", "create table", "update ", "delete "):
            self.assertNotIn(proibido, corpo.lower().replace("nao cria tabela, nao escreve", ""))

    def test_3_com_psql_declarado_inexistente_o_portao_bloqueia_antes_da_rede(self):
        env = dict(os.environ, SINTONIA_SALA_BACKEND="POSTGRES",
                   SINTONIA_SALA_DSN="postgresql://postgres@127.0.0.1:1/descartavel",
                   SINTONIA_PSQL_EXE=os.path.join(tempfile.gettempdir(), "psql-que-nao-existe.exe"),
                   PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, os.path.join("admissao", "sala_de_espera.py"), "--portao"],
                           cwd=RAIZ, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("SALA_DE_ESPERA=BLOCKED", r.stdout)
        self.assertIn("SINTONIA_PSQL_EXE", r.stdout)

    def test_4_o_backend_de_ficheiro_tambem_sonda_e_o_portao_continua_a_recusa_lo(self):
        import sala_de_espera as se
        self.assertEqual(se._Ficheiro().sondar()["SONDA"], "OK")


class AProvaComoProcessoContraPostgresReal(unittest.TestCase):
    """`provas/o_cliente_psql_e_declarado.py`: Windows real, PostgreSQL 16 real,
    PATH sem psql, `SINTONIA_PSQL_EXE` explícito, os três donos e a porta CLI
    como processos. NOT_RUN não é PASS: sem Postgres portátil fica skip COM
    motivo."""

    def test_o_cliente_e_declarado_e_o_PATH_deixa_de_ser_requisito(self):
        r = subprocess.run(
            [sys.executable, os.path.join("provas", "o_cliente_psql_e_declarado.py")],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=1500,
            env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        saida = (r.stdout or "") + (r.stderr or "")
        if r.returncode == 2 and "NOT_RUN" in saida:
            self.skipTest("NOT_RUN_WITH_REASON: " + saida.strip().splitlines()[-1][:200])
        self.assertIn("PSQL_RUNTIME_BINDING_PROVEN=PASS", saida, saida[-3000:])
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
