#!/usr/bin/env python3
"""RED TEAM DO MONITOR DE DERIVA (SEC-020).

A base viva estava mais segura do que o repositorio dizia, e ninguem sabia.
Esta prova garante que a proxima deriva nao passa em silencio — e, mais
importante, que a deriva SEGURA continua a ser reportada como deriva.

    A LIVE DATABASE THAT IS SAFER THAN THE REPO IS STILL DRIFT.
    SAFE DRIFT != NO DRIFT.

Nenhuma ligacao e feita. Cada prova monta um censo sintetico — o mesmo formato
que o catalogo devolve — e verifica a classificacao.

    python3 -m unittest tests.test_security_drift_db -v
"""
import importlib.util, json, pathlib, tempfile, unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("drift_db", RAIZ / "security" / "drift_db.py")
drift = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drift)

FECHADA = "rls=true|force=false|policies=0|anon_s=false|anon_i=false|anon_u=false|anon_d=false" \
          "|auth_s=false|auth_i=false|auth_u=false|auth_d=false"


def censo(linhas):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write("CTX|db=x|user=y|pgrst_db_schemas=NAO_DEFINIDO_AO_NIVEL_DA_BD\n")
    f.write("SCHEMA|public|anon_usage=true|anon_create=false"
            "|authenticated_usage=true|authenticated_create=false\n")
    f.write("\n".join(linhas) + "\n")
    f.close()
    return f.name


class Deriva(unittest.TestCase):
    def setUp(self):
        self.esperado_real = drift.ESPERADO
        self.tmp = pathlib.Path(tempfile.mkdtemp()) / "esperado.json"
        drift.ESPERADO = self.tmp

    def tearDown(self):
        drift.ESPERADO = self.esperado_real

    def esperar(self, tabelas, vistas=None):
        self.tmp.write_text(json.dumps({"tabelas": tabelas, "vistas": vistas or {}}), encoding="utf-8")

    def classes(self, linhas):
        return {a["classe"] for a in drift.comparar(drift.ler_censo(censo(linhas)))[0]}

    # ── regressao de seguranca: tem de morder ─────────────────────────────
    def test_anon_ganha_select_e_regressao(self):
        self.esperar({"fonte_externa": {"rls": True, "policies": 0}})
        cs = self.classes([f"T|fonte_externa|{FECHADA.replace('anon_s=false', 'anon_s=true')}"])
        self.assertIn("LIVE_LESS_RESTRICTIVE", cs)
        self.assertTrue(drift.CLASSES_REGRESSAO & cs, "devia contar como regressao")

    def test_anon_ganha_escrita_e_regressao(self):
        self.esperar({"t": {"rls": True, "policies": 0}})
        self.assertIn("LIVE_LESS_RESTRICTIVE",
                      self.classes([f"T|t|{FECHADA.replace('anon_i=false', 'anon_i=true')}"]))

    def test_rls_desligada_e_regressao(self):
        self.esperar({"t": {"rls": True, "policies": 0}})
        cs = self.classes([f"T|t|{FECHADA.replace('rls=true', 'rls=false')}"])
        self.assertIn("RLS_DESLIGADA", cs)

    def test_vista_sem_invoker_legivel_por_anon_e_regressao_de_desenho(self):
        self.esperar({})
        cs = self.classes(["V|v_x|invoker=nao_definido|anon_s=true|auth_s=true"])
        self.assertIn("VISTA_SEM_SECURITY_INVOKER_LEGIVEL_POR_ANON", cs)

    # ── deriva sem exposicao: tem de aparecer, sem bloquear ───────────────
    def test_deriva_segura_continua_a_ser_deriva(self):
        """O achado desta noite. A base tinha RLS onde a migration nao pedia.
        Isso e SAFE e e DRIFT ao mesmo tempo, e o verde silencioso seria a
        pior das respostas."""
        self.esperar({"fonte_externa": {"rls": True, "policies": 0}})
        cs = self.classes([f"T|fonte_externa|{FECHADA}"])
        self.assertIn("LIVE_MORE_RESTRICTIVE", cs)
        self.assertFalse(drift.CLASSES_REGRESSAO & cs, "deriva segura nao pode bloquear")

    def test_tabela_so_na_base_viva(self):
        self.esperar({})
        self.assertIn("TABLE_ONLY_IN_LIVE", self.classes([f"T|apareceu_do_nada|{FECHADA}"]))

    def test_tabela_so_no_repositorio(self):
        self.esperar({})
        # `fonte_externa` e criada pelas migrations reais e nao aparece no censo
        self.assertIn("TABLE_ONLY_IN_REPO", self.classes([f"T|apenas_viva|{FECHADA}"]))

    def test_politica_nova_e_deriva_e_nao_regressao(self):
        # `fonte_externa` existe nas migrations reais: a comparacao de
        # politicas so tem sentido para uma tabela que os dois lados conhecem.
        self.esperar({"fonte_externa": {"rls": True, "policies": 0}})
        cs = self.classes([f"T|fonte_externa|{FECHADA.replace('policies=0', 'policies=2')}"])
        self.assertIn("POLICY_MISMATCH", cs)
        self.assertFalse(drift.CLASSES_REGRESSAO & cs)

    def test_vista_sem_invoker_inalcancavel_e_latente_e_nao_regressao(self):
        self.esperar({})
        cs = self.classes(["V|v_y|invoker=nao_definido|anon_s=false|auth_s=false"])
        self.assertIn("VISTA_SEM_SECURITY_INVOKER_LATENTE", cs)
        self.assertFalse(drift.CLASSES_REGRESSAO & cs)

    def test_invoker_on_nao_e_achado(self):
        """O Postgres grava `on`, nao `true`. Comparar com "true" transformaria
        as 16 vistas correctas em 16 achados."""
        self.esperar({})
        self.assertNotIn("VISTA_SEM_SECURITY_INVOKER_LATENTE",
                         self.classes(["V|v_z|invoker=on|anon_s=false|auth_s=false"]))


class EstadoEsperadoReal(unittest.TestCase):
    def test_o_esperado_declarado_esta_completo_e_fechado(self):
        """O ficheiro no repositorio e uma DECLARACAO revista, nao uma
        fotografia automatica. Esta prova le-o e exige que ele continue a
        declarar uma base fechada."""
        d = json.loads((RAIZ / "security" / "live-db-expected.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(d["tabelas"]), 60)
        abertas = [n for n, t in d["tabelas"].items()
                   if any(t[k] for k in ("anon_s", "anon_i", "anon_u", "anon_d"))]
        self.assertEqual(abertas, [], "o esperado declara privilegio anon nalguma tabela")
        self.assertEqual([n for n, t in d["tabelas"].items() if not t["rls"]], [],
                         "o esperado declara uma tabela sem RLS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
