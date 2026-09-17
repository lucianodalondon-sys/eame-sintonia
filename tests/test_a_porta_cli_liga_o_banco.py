# -*- coding: utf-8 -*-
"""A PORTA CLI DO ORQUESTRADOR LIGA O BANCO — e só o banco que o ambiente prova.

O QUE ACONTECEU, E POR QUE ISTO EXISTE
--------------------------------------
O replay canário pelo workflow real (run GitHub 35215565657, 2026-09-17,
know-how §132) mostrou o `sintonia-scrap.yml` a criar um PostgreSQL
descartável, a aplicar 31 migrations, a passar o portão da Sala e o do egresso
— e a corrida a não escrever uma linha no banco. `orquestrador.main()` chamava
`correr()` sem `memoria` e sem `banco_do_rastro`; ninguém lia o ambiente; o
adaptador Postgres só existia em `provas/`. Quinze testes de YAML não podiam
ver isto: nenhum executava a porta.

    DEPENDÊNCIA DECLARADA != DEPENDÊNCIA LIGADA.
    PROVA NÃO É RUNTIME.
    MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.

Estes testes guardam as quatro coisas que fecham o defeito:

    1  a porta CLI compõe `memoria` e `banco_do_rastro` ANTES de `correr()`
       (medido no código, por AST — não por leitura de comentário);
    2  a composição só liga banco quando `BANCO_DESCARTAVEL_URL` o declara e
       prova; produção nunca é fallback (SUPABASE_DB_URL, SINTONIA_SALA_DSN);
    3  a trava do descartável é UMA, vive em `guarda/`, e fecha as portas
       laterais (`?host=`, `hostaddr`, `service`, host parecido);
    4  o runtime não importa `provas/`, e há UM adaptador Postgres.

E a prova principal — a porta como PROCESSO contra Postgres 16 real — vive em
`provas/a_porta_cli_liga_o_banco.py`; o último teste corre-a e lê o veredito.
"""
import ast
import io
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import persistencia as P  # noqa: E402
from guarda import banco_descartavel as bd  # noqa: E402

PRODUCAO = "postgresql://postgres:x@db.abcdefgh.supabase.co:5432/postgres"
LOCAL = "postgresql://postgres:descartavel@localhost:54329/descartavel"


def _fonte(*partes):
    return io.open(os.path.join(RAIZ, *partes), encoding="utf-8").read()


class ATravaDoDescartavelEUmaEViveNoRuntime(unittest.TestCase):

    def test_1_aceita_so_local_e_descartavel(self):
        for url in (LOCAL, "postgresql://postgres@127.0.0.1:5433/descartavel",
                    "postgres://p:x@[::1]:5432/objeto",
                    "postgresql://p:x@localhost/derivado",
                    "postgresql://p:x@localhost:54329/descartavel?host=127.0.0.1"):
            self.assertTrue(bd.e_descartavel(url), url)

    def test_2_recusa_as_portas_laterais_e_os_parecidos(self):
        recusar = {
            PRODUCAO: "hostname",
            "postgresql://p:x@localhost.atacante.example/descartavel": "hostname",
            "postgresql://p:x@localhost:54329/descartavel?host=db.x.supabase.co": "host",
            "postgresql://p:x@localhost:54329/descartavel?hostaddr=52.1.2.3": "hostaddr",
            "postgresql://p:x@localhost/descartavel?service=producao": "service",
            "postgresql://p:x@localhost/descartavel?dbname=postgres": "dbname",
            "postgresql://p:x@localhost/descartavel?dbname=descartavel": "dbname",
            "postgresql://localhost,db.remoto/descartavel": "hostname",
            "postgresql://p:x@localhost:5432/producao": "banco",
            "postgresql://p:x@localhost:5432/postgres": "banco",
            "mysql://p:x@localhost/descartavel": "scheme",
            "postgresql://p:x@localhost:abc/descartavel": "porto",
            "": "vazia", None: "vazia", "nada": "scheme",
        }
        for url, pedaco in recusar.items():
            motivo = bd.porque_nao_e_descartavel(url)
            self.assertTrue(motivo, url)
            self.assertIn(pedaco, motivo, url)
            with self.assertRaises(bd.BancoNaoDescartavel):
                bd.exigir_descartavel(url)

    def test_3_a_lista_de_bancos_continua_curta_e_sem_producao(self):
        self.assertLessEqual(len(bd.BANCOS_PERMITIDOS), 4)
        for proibido in ("producao", "prod", "postgres", "eame-sintonia"):
            self.assertNotIn(proibido, bd.BANCOS_PERMITIDOS)

    def test_4_o_motivo_e_a_morada_nunca_repetem_a_senha(self):
        url = "postgresql://user:SENHA-SECRETA@db.x.supabase.co:5432/postgres"
        self.assertNotIn("SENHA-SECRETA", bd.porque_nao_e_descartavel(url))
        self.assertNotIn("SENHA-SECRETA", bd.morada_sem_segredo(url))
        self.assertEqual(bd.morada_sem_segredo(LOCAL), "localhost:54329/descartavel")

    def test_4b_o_ambiente_que_desvia_a_libpq_e_conhecido_e_sai(self):
        """`PGHOSTADDR=52.1.2.3` manda a ligação para fora com a URL a dizer
        localhost (red team de arquitetura, 2026-09-17, medido na libpq)."""
        for nome in ("PGHOST", "PGHOSTADDR", "PGPORT", "PGDATABASE",
                     "PGSERVICE", "PGSERVICEFILE", "PGOPTIONS"):
            self.assertIn(nome, bd.AMBIENTE_QUE_MUDA_O_DESTINO)
        for credencial in ("PGPASSWORD", "PGPASSFILE"):
            self.assertNotIn(credencial, bd.AMBIENTE_QUE_MUDA_O_DESTINO)
        env = {"PGHOSTADDR": "52.1.2.3", "PGSERVICE": "prod",
               "PGPASSWORD": "fica", "PATH": "x"}
        limpo, retiradas = bd.ambiente_sem_desvio(env)
        self.assertEqual(sorted(retiradas), ["PGHOSTADDR", "PGSERVICE"])
        self.assertEqual(limpo, {"PGPASSWORD": "fica", "PATH": "x"})
        self.assertIn("PGHOSTADDR", env)      # o original nao e alterado

    def test_5_as_provas_importam_a_trava_daqui_e_nao_tem_copia(self):
        prova = _fonte("provas", "preservar_coleta_no_postgres.py")
        self.assertIn("guarda.banco_descartavel", prova)
        self.assertNotIn("def _e_descartavel", prova)
        sala = _fonte("provas", "a_sala_sobrevive_ao_processo.py")
        self.assertIn("guarda.banco_descartavel", sala)
        self.assertNotIn('"localhost" in url', sala)
        # nenhuma outra definição da trava, em lado nenhum do runtime
        for pasta in ("guarda", "coleta", "orquestrador", "admissao", "motor"):
            for base, _, ficheiros in os.walk(os.path.join(RAIZ, pasta)):
                for nome in ficheiros:
                    if not nome.endswith(".py") or nome == "banco_descartavel.py":
                        continue
                    self.assertNotIn("def _e_descartavel",
                                     _fonte(base, nome), os.path.join(base, nome))


class AComposicaoLigaSoOQueOAmbienteProva(unittest.TestCase):

    def test_1_sem_variavel_a_persistencia_e_AUSENTE_e_nada_se_liga(self):
        r = P.dependencias_do_runtime({})
        self.assertEqual(r.ESTADO, P.AUSENTE)
        self.assertIsNone(r.memoria)
        self.assertIsNone(r.banco_do_rastro)
        self.assertIn("BANCO_DESCARTAVEL_URL", r.PORQUE)
        self.assertEqual(r.para_json()["MEMORIA"], None)

    def test_2_producao_no_ambiente_nunca_e_fallback(self):
        for env in ({"SUPABASE_DB_URL": PRODUCAO},
                    {"SINTONIA_SALA_DSN": PRODUCAO},
                    {"SUPABASE_DB_URL": PRODUCAO, "SINTONIA_SALA_DSN": PRODUCAO,
                     "SINTONIA_SALA_BACKEND": "POSTGRES"}):
            r = P.dependencias_do_runtime(env)
            self.assertEqual(r.ESTADO, P.AUSENTE, env)
            self.assertIsNone(r.memoria)
            self.assertIsNone(r.banco_do_rastro)

    def test_3_variavel_declarada_e_nao_descartavel_recusa_antes_de_tudo(self):
        for url in (PRODUCAO,
                    "postgresql://p:x@localhost.evil/descartavel",
                    "postgresql://p:x@localhost:54329/descartavel?host=db.remoto",
                    "postgresql://p:x@localhost:54329/descartavel?hostaddr=52.1.2.3",
                    "postgresql://p:x@localhost:5432/postgres",
                    "isto nao e uma url"):
            with self.assertRaises(P.BancoRecusado, msg=url):
                P.dependencias_do_runtime({"BANCO_DESCARTAVEL_URL": url})

    def test_4_variavel_descartavel_liga_o_adaptador_canonico_e_o_rastro(self):
        r = P.dependencias_do_runtime({"BANCO_DESCARTAVEL_URL": LOCAL})
        self.assertEqual(r.ESTADO, P.DESCARTAVEL)
        from guarda.memoria_postgres import MemoriaPostgres
        import coleta_checkpoint as cc
        self.assertIsInstance(r.memoria, MemoriaPostgres)
        self.assertIsInstance(r.banco_do_rastro, cc.Banco)
        self.assertEqual(r.memoria.url, LOCAL)
        self.assertEqual(r.banco_do_rastro.dsn, LOCAL)
        j = r.para_json()
        self.assertEqual(j["MORADA"], "localhost:54329/descartavel")
        self.assertNotIn("descartavel@", j["MORADA"])

    def test_4b_com_a_bancada_declarada_os_bilhetes_da_parede_saem(self):
        """A composição — e só ela, e só com a bancada declarada — tira do
        ambiente DO PROCESSO as variáveis que desviam a libpq, e di-lo no
        recibo. Sem bancada, nada é tocado."""
        nomes = ("PGHOSTADDR", "PGSERVICE", "PGPASSWORD", "BANCO_DESCARTAVEL_URL")
        guardados = {n: os.environ.get(n) for n in nomes}
        try:
            os.environ["PGHOSTADDR"] = "127.0.0.2"
            os.environ["PGSERVICE"] = "prod"
            os.environ["PGPASSWORD"] = "fica"
            os.environ.pop("BANCO_DESCARTAVEL_URL", None)
            r = P.dependencias_do_runtime()
            self.assertEqual(r.ESTADO, P.AUSENTE)
            self.assertEqual(os.environ["PGHOSTADDR"], "127.0.0.2")   # intocado
            os.environ["BANCO_DESCARTAVEL_URL"] = LOCAL
            r = P.dependencias_do_runtime()
            self.assertEqual(r.ESTADO, P.DESCARTAVEL)
            self.assertEqual(sorted(r.AMBIENTE_RETIRADO), ["PGHOSTADDR", "PGSERVICE"])
            self.assertNotIn("PGHOSTADDR", os.environ)
            self.assertNotIn("PGSERVICE", os.environ)
            self.assertEqual(os.environ["PGPASSWORD"], "fica")
            self.assertEqual(r.para_json()["AMBIENTE_RETIRADO"],
                             list(r.AMBIENTE_RETIRADO))
        finally:
            for n, v in guardados.items():
                if v is None:
                    os.environ.pop(n, None)
                else:
                    os.environ[n] = v

    def test_5_compor_nao_liga_nem_escreve(self):
        """Construir as dependências não abre ligação: só `aplicar`/`executa`
        falam com o banco. Uma URL de porto morto prova-o — se compor
        ligasse, isto rebentava."""
        r = P.dependencias_do_runtime(
            {"BANCO_DESCARTAVEL_URL": "postgresql://postgres@127.0.0.1:1/descartavel"})
        self.assertEqual(r.ESTADO, P.DESCARTAVEL)
        self.assertEqual(r.memoria.aplicacoes, 0)

    def test_6_importar_a_peca_nao_le_ambiente(self):
        fonte = _fonte("orquestrador", "persistencia.py")
        arvore = ast.parse(fonte)
        topo = [n for n in arvore.body
                if isinstance(n, (ast.Expr, ast.Assign, ast.If, ast.For))]
        for n in topo:
            for sub in ast.walk(n):
                if isinstance(sub, ast.Attribute) and sub.attr == "environ":
                    self.fail("os.environ lido no import de persistencia.py")


class APortaCLIComPoeAntesDeCorrer(unittest.TestCase):

    def _chamada_a_correr_em_main(self):
        arvore = ast.parse(_fonte("orquestrador", "orquestrador.py"))
        main = next(n for n in arvore.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        for no in ast.walk(main):
            if (isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
                    and no.func.id == "correr"):
                return no
        self.fail("main() nao chama correr()")

    def test_1_main_passa_memoria_e_banco_do_rastro_a_correr(self):
        chamada = self._chamada_a_correr_em_main()
        nomes = {k.arg for k in chamada.keywords}
        self.assertIn("memoria", nomes)
        self.assertIn("banco_do_rastro", nomes)

    def test_2_o_que_main_passa_vem_da_composicao_e_nao_de_um_literal(self):
        chamada = self._chamada_a_correr_em_main()
        for k in chamada.keywords:
            if k.arg in ("memoria", "banco_do_rastro"):
                self.assertIsInstance(k.value, ast.Attribute, k.arg)
                self.assertEqual(k.value.value.id, "runtime")

    def test_3_o_recibo_declara_a_persistencia(self):
        fonte = _fonte("orquestrador", "orquestrador.py")
        self.assertIn('recibo["PERSISTENCIA"] = runtime.para_json()', fonte)

    def test_4_o_workflow_continua_a_chamar_so_o_orquestrador(self):
        yml = _fonte(".github", "workflows", "sintonia-scrap.yml")
        exec_ = "\n".join(l for l in yml.splitlines()
                          if not l.strip().startswith("#"))
        self.assertIn("orquestrador/orquestrador.py", exec_)
        for proibido in ("persistencia.py", "memoria_postgres", "MemoriaPostgres",
                         "banco_do_rastro", "primeira_coleta_controlada_italia"):
            self.assertNotIn(proibido, exec_, proibido)
        self.assertIn("BANCO_DESCARTAVEL_URL=", exec_)


class ORuntimeNaoImportaProvasEHaUmAdaptador(unittest.TestCase):
    PASTAS_DE_RUNTIME = ("guarda", "coleta", "orquestrador", "admissao",
                         "motor", "pedido", "leis")
    OUTRAS_GAVETAS = ("ferramentas", "fontes", "candidatas", "superficie",
                      "regras", "medidas", "portoes")

    #: ⚠️ `_gavetas.py` põe `provas/` no `sys.path`, e por isso um `import
    #: corrigir_custo` NU chega a `provas/corrigir_custo.py` sem dizer
    #: `provas.` — o red team de arquitetura (2026-09-17) apanhou o teste
    #: cego a esse vetor. Estes dois já existiam antes desta missão e ficam
    #: NOMEADOS como dívida: o teste passa a acusar qualquer TERCEIRO.
    #: Tirar uma linha daqui é fechar a dívida; acrescentar uma é abri-la.
    DIVIDA_PRE_EXISTENTE = {
        ("coleta/instagram_coleta.py", "corrigir_custo"),
        ("motor/corrida_da_inteligencia.py", "espinha_da_intelligence"),
    }

    def _so_existe_em_provas(self, nome, pasta_do_importador):
        if not os.path.exists(os.path.join(RAIZ, "provas", nome + ".py")):
            return False
        if os.path.exists(os.path.join(pasta_do_importador, nome + ".py")):
            return False
        for g in self.PASTAS_DE_RUNTIME + self.OUTRAS_GAVETAS:
            if os.path.exists(os.path.join(RAIZ, g, nome + ".py")):
                return False
        return not os.path.exists(os.path.join(RAIZ, nome + ".py"))

    def test_1_nenhum_modulo_de_runtime_importa_provas(self):
        achados = set()
        for pasta in self.PASTAS_DE_RUNTIME:
            raiz = os.path.join(RAIZ, pasta)
            if not os.path.isdir(raiz):
                continue
            for base, _, ficheiros in os.walk(raiz):
                if "__pycache__" in base:
                    continue
                for nome in ficheiros:
                    if not nome.endswith(".py"):
                        continue
                    caminho = os.path.join(base, nome)
                    try:
                        arvore = ast.parse(_fonte(caminho))
                    except SyntaxError:
                        continue
                    for no in ast.walk(arvore):
                        modulos = []
                        if isinstance(no, ast.Import):
                            modulos = [a.name for a in no.names]
                        elif isinstance(no, ast.ImportFrom) and no.module:
                            modulos = [no.module]
                        for m in modulos:
                            self.assertFalse(
                                m == "provas" or m.startswith("provas."),
                                "%s importa %s" % (caminho, m))
                            # o vetor real: nome NU que só existe em provas/
                            raiz_do_nome = m.split(".")[0]
                            if self._so_existe_em_provas(raiz_do_nome, base):
                                rel = os.path.relpath(caminho, RAIZ).replace(os.sep, "/")
                                achados.add((rel, raiz_do_nome))
        novos = achados - self.DIVIDA_PRE_EXISTENTE
        self.assertEqual(novos, set(),
                         "runtime a importar provas/ por nome nu: %s" % sorted(novos))
        fechadas = self.DIVIDA_PRE_EXISTENTE - achados
        self.assertEqual(fechadas, set(),
                         "divida fechada e ainda listada: %s" % sorted(fechadas))

    def test_2_ha_um_so_dialeto_psql_de_memoria_no_runtime(self):
        """`portas_live.MemoriaSupabase` era uma segunda implementação. Agora
        só sabe de onde vem a URL: o `_psql`, o `_linhas`, o `_ISO` e as
        projeções vivem numa classe só."""
        from guarda.memoria_postgres import MemoriaPostgres
        from guarda.portas_live import MemoriaSupabase
        self.assertTrue(issubclass(MemoriaSupabase, MemoriaPostgres))
        for metodo in ("_psql", "_linhas", "_select", "aplicar",
                       "objetos_da_corrida", "raw_por_id",
                       "derivado_com_identidade", "documento_do_derivado"):
            self.assertNotIn(metodo, MemoriaSupabase.__dict__, metodo)
        donos = []
        for base, _, ficheiros in os.walk(os.path.join(RAIZ, "guarda")):
            for nome in ficheiros:
                if nome.endswith(".py") and "def _psql(" in _fonte(base, nome):
                    donos.append(nome)
        self.assertEqual(donos, ["memoria_postgres.py"])

    def test_3_a_prova_e_uma_subclasse_da_canonica_com_a_trava_a_entrada(self):
        sys.path.insert(0, os.path.join(RAIZ, "provas"))
        import preservar_coleta_no_postgres as pg
        from guarda.memoria_postgres import MemoriaPostgres
        self.assertTrue(issubclass(pg.MemoriaPostgres, MemoriaPostgres))
        with self.assertRaises(SystemExit):
            pg.MemoriaPostgres(PRODUCAO)
        self.assertIs(pg._e_descartavel, bd.e_descartavel)

    def test_4_o_adaptador_fala_por_stdin_utf8_e_com_a_dsn_em_ultimo(self):
        fonte = _fonte("guarda", "memoria_postgres.py")
        self.assertIn('"-f", "-", self.url]', fonte)
        self.assertIn('encoding="utf-8"', fonte)
        self.assertNotIn('"-c", sql', fonte)
        self.assertNotIn("insert into raw_asset", fonte.lower())

    def test_5_o_adaptador_nao_decide_se_e_descartavel(self):
        """Quem decide é quem compõe. Um adaptador que recusasse produção não
        serviria a porta LIVE; um que ligasse por conta própria seria o
        defeito. Construir com produção NÃO levanta — e também não liga."""
        from guarda.memoria_postgres import MemoriaPostgres
        m = MemoriaPostgres(PRODUCAO)
        self.assertEqual(m.aplicacoes, 0)
        self.assertNotIn("banco_descartavel", _fonte("guarda", "memoria_postgres.py")
                         .split('"""', 2)[2])


class AProvaComoProcessoContraPostgresReal(unittest.TestCase):
    """O gate desta missão: `provas/a_porta_cli_liga_o_banco.py` corre a porta
    CLI como PROCESSO SEPARADO contra Postgres 16 real e lê o banco."""

    def test_a_porta_cli_escreve_no_banco_descartavel(self):
        r = subprocess.run(
            [sys.executable, os.path.join("provas", "a_porta_cli_liga_o_banco.py")],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=1500,
            env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        saida = (r.stdout or "") + (r.stderr or "")
        if r.returncode == 2:
            # NOT_RUN não é PASS: fica visível como skip COM motivo, e o
            # veredito de missão exige que a prova tenha corrido a sério.
            self.skipTest("NOT_RUN_WITH_REASON: " + saida.strip().splitlines()[-1][:200])
        self.assertEqual(r.returncode, 0, saida[-3000:])
        self.assertIn("CLI_POSTGRES_BINDING_PROVEN=PASS", saida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
