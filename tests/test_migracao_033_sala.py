# -*- coding: utf-8 -*-
"""MIGRACAO-SALA (D68) — a 033 num Postgres DESCARTÁVEL: sobe, desce, sobe.

    O RAW NÃO MUDA. A LINHA NÃO MUDA. NUNCA HÁ UPDATE CALADO.

Um Postgres descartável (binários de ~/orca/pgtmp) numa porta livre, com as
migrations pela cadeia canónica. Nunca a Sala real. Sem os binários, SALTA e
diz porquê.

    py -m unittest tests.test_migracao_033_sala
"""
import glob
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in ("", "admissao", "coleta", "orquestrador"):
    sys.path.insert(0, str(RAIZ / p))
import _gavetas                          # noqa: E402,F401
import admissao as adm                   # noqa: E402
import sala_de_espera as espera          # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

MIG = next(iter(glob.glob(str(RAIZ / "supabase" / "migrations" / "033_*.sql"))))
DESFAZER = RAIZ / "supabase" / "desfazer" / "033_desfazer.sql"
TEM_PG = (E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")).exists() and shutil.which("bash")


def _ready(i, corrida="R1", **kw):
    item = {"id": "derived:%d" % i, "texto": "Bollettino fitosanitario n. %d" % i,
            "source_id": "IT-T3-002", "artifact_type": "DERIVED",
            "parent_sha256": "a" * 64, "raw_asset_id": None,
            "captured_at": "2026-09-18T17:19:15Z"}
    item.update(kw)
    # a estrada real passa a corrida a `decidir`; a Sala rele CORRIDA = run_id
    d = adm.Decisao(item=item["id"], universo="T3", resultado=adm.SIM,
                    regra="teste", motivo="teste", corrida=corrida)
    return adm.pronto_para_inteligencia(item, d)


class ADefaultDaCompletude(unittest.TestCase):
    """Sem banco: o default da 033 e o registo do dono, byte a byte."""

    def test_o_default_da_033_e_o_do_dono_byte_a_byte(self):
        d = json.dumps(adm.COMPLETUDE_NAO_MEDIDA, sort_keys=True, ensure_ascii=False)
        self.assertIn("default '%s'::json" % d, open(MIG, encoding="utf-8").read())

    def test_a_lista_do_que_se_reve_e_a_mesma_no_codigo_e_no_banco(self):
        sql = open(MIG, encoding="utf-8").read()
        bloco = re.search(r"revisao_so_de_campo_revisivel check \(campo in \((.*?)\)\)",
                          sql, re.S).group(1)
        no_banco = set(re.findall(r"'([a-z_]+)'", bloco))
        self.assertEqual(no_banco, set(espera.CAMPOS_REVISIVEIS))

    def test_o_ready_tem_os_campos_da_sala_pela_mesma_ordem(self):
        self.assertEqual(list(_ready(1)), list(espera.CAMPOS_READY))

    def test_os_json_do_ready_saem_com_as_chaves_ordenadas(self):
        """A Sala guarda-os com sort_keys; fora de ordem, um retry vira conflito."""
        r = _ready(1)
        for campo in ("COMPLETUDE_TEMPO_LUGAR", "TEMPO_LUGAR_EVIDENCIA"):
            self.assertEqual(list(r[campo]), sorted(r[campo]), campo)

    def test_a_migration_so_acrescenta(self):
        sql = open(MIG, encoding="utf-8").read().lower()
        codigo = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
        # o INICIO de cada instrucao; «before update or delete» do gatilho nao conta
        destrutivas = re.findall(
            r"(?m)^\s*(drop\b|delete\b|update\b|truncate\b|alter\s+table\s+\S+\s+"
            r"(?:drop|rename|alter\s+column)\b)", codigo)
        self.assertEqual(destrutivas, [])
        self.assertNotRegex(codigo, r"\brename\b|\balter\s+column\b|\btype\s+\w+\s+using\b")
        self.assertTrue("NÃO EXECUTADA" in open(MIG, encoding="utf-8").read())


@unittest.skipUnless(TEM_PG, "sem Postgres portatil (~/orca/pgtmp) ou sem bash: a prova nao correu")
class A033NoBancoDescartavel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pasta = Path(tempfile.mkdtemp(prefix="migracao-033-"))
        cls.base = E.Base(cls.pasta / "pg")
        assert ":54330/" not in cls.base.url, "isto e a Sala real"
        cls.env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
        r = cls.base.subir(RAIZ, cls.env)
        if r["CODIGO"] != 0:
            cls.base.descer()
            raise unittest.SkipTest("migrations falharam: %s" % r["ERRO"])
        cls._amb = dict(os.environ)
        try:
            os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES",
                               "SINTONIA_SALA_DSN": cls.base.url,
                               "SINTONIA_PSQL_EXE": cls.base.exe("psql")})
            cls.sql("insert into collection_run (run_id, platform, started_at, "
                    "rule_version) values ('R1', 'teste', now(), 'teste'), "
                    "('R0', 'teste', now(), 'teste')")
            espera.pousar("R1", [_ready(1, published_at="2026-09-16",
                                        published_at_basis="SOURCE_DATE_ISO (EDICAO)",
                                        source_location="Napoli",
                                        source_location_basis="contrato IT-T3-002"),
                                 _ready(2)])
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        os.environ.clear()
        os.environ.update(cls._amb)
        cls.base.descer()
        shutil.rmtree(cls.pasta, ignore_errors=True)

    @classmethod
    def sql(cls, comando, falhar=True):
        r = subprocess.run([cls.base.exe("psql"), "-X", "-q", "-A", "-t",
                            "-v", "ON_ERROR_STOP=1", "-c", comando, cls.base.url],
                           capture_output=True, text=True, encoding="utf-8")
        if falhar and r.returncode != 0:
            raise AssertionError(r.stderr)
        return r

    def rever(self, ordem, valor, base="teste"):
        return espera.rever("R1", ordem, [{"CAMPO": "fact_location", "VALOR": valor,
                                           "BASE": base}],
                            extrator="teste", versao="v1", motivo="teste")

    # ── A · as colunas novas ─────────────────────────────────────────────
    def test_1_um_escritor_antigo_continua_a_funcionar_e_le_o_default(self):
        self.sql("insert into sala_de_espera (run_id, ordem, item_id, universo, texto, "
                 "source_id, source_location, fact_location, fact_time, captured_at, "
                 "admitido_por, corrida_sha256) values ('R0', 0, 'x', 'T3', 't', 's', "
                 "'NAO SEI', 'NAO SEI', 'NAO SEI', 'NAO SEI', 'a', '%s')" % ("0" * 64))
        r = self.sql("select published_at_basis, source_location_basis, "
                     "completude_tempo_lugar from sala_de_espera where run_id='R0'").stdout
        pb, sb, comp = r.strip().split("|")
        self.assertEqual((pb, sb), ("NAO SEI", "NAO SEI"))
        self.assertEqual(json.loads(comp), adm.COMPLETUDE_NAO_MEDIDA)

    def test_2_pousar_escreve_as_bases_e_a_completude(self):
        r = self.sql("select published_at, published_at_basis, source_location_basis, "
                     "completude_tempo_lugar from sala_de_espera "
                     "where run_id='R1' and ordem=0").stdout.strip().split("|")
        self.assertEqual(r[0:3], ["2026-09-16", "SOURCE_DATE_ISO (EDICAO)", "contrato IT-T3-002"])
        self.assertEqual(json.loads(r[3])["PROVADAS"], 2)

    def test_3_repousar_o_mesmo_e_retry_e_nao_conflito(self):
        lido = espera.ler("R1")["ITENS"]
        self.assertEqual(espera.pousar("R1", lido)["ESTADO"], espera.JA_ESTAVA)

    # ── D · as revisoes ──────────────────────────────────────────────────
    def test_4_rever_nao_muda_a_linha_e_a_vista_le_a_revisao(self):
        antes = self.sql("select fact_location, corrida_sha256 from sala_de_espera "
                         "where run_id='R1' and ordem=1").stdout
        self.assertEqual(self.rever(1, "Puglia")["INSERIDAS"], 1)
        depois = self.sql("select fact_location, corrida_sha256 from sala_de_espera "
                          "where run_id='R1' and ordem=1").stdout
        self.assertEqual(antes, depois, "a linha original mudou")
        atual = {u["ORDEM"]: u for u in espera.ler_atual("R1")["ITENS"]}
        self.assertEqual(atual[1]["FACT_LOCATION"], "Puglia")
        self.assertEqual(atual[1]["REVISOES"], 1)
        self.assertEqual(atual[0]["FACT_LOCATION"], "NAO SEI")   # sem revisao: o original
        self.assertEqual(espera.ler("R1")["ITENS"][1]["FACT_LOCATION"], "NAO SEI")

    def test_5_reprocessar_duas_vezes_nao_duplica(self):
        self.rever(1, "Toscana")
        self.assertEqual(self.rever(1, "Toscana"),
                         {"INSERIDAS": 0, "JA_ERAM_ASSIM": 1})

    def test_6_a_vista_le_a_ULTIMA_revisao_e_as_anteriores_ficam(self):
        self.rever(0, "Lazio")
        self.rever(0, "Umbria")
        atual = {u["ORDEM"]: u for u in espera.ler_atual("R1")["ITENS"]}
        self.assertEqual(atual[0]["FACT_LOCATION"], "Umbria")
        n = self.sql("select count(*) from sala_de_espera_revisao where run_id='R1' "
                     "and ordem=0 and campo='fact_location'").stdout.strip()
        self.assertEqual(n, "2")

    def test_7_update_delete_truncate_nas_revisoes_sao_recusados(self):
        self.rever(1, "Marche")
        for comando in ("update sala_de_espera_revisao set valor='x'",
                        "delete from sala_de_espera_revisao",
                        "truncate sala_de_espera_revisao"):
            r = self.sql(comando, falhar=False)
            self.assertNotEqual(r.returncode, 0, comando)
            self.assertIn("SALA_REVISAO_SO_ACRESCENTA", r.stderr, comando)

    def test_8_so_se_reve_o_que_esta_na_lista(self):
        with self.assertRaises(ValueError):
            espera.rever("R1", 0, [{"CAMPO": "texto", "VALOR": "x", "BASE": "y"}],
                         extrator="t", versao="v", motivo="m")
        r = self.sql("insert into sala_de_espera_revisao (run_id, ordem, campo, revisao, "
                     "valor, base, extrator, versao_do_extrator, motivo) values "
                     "('R1', 0, 'texto', 1, 'x', 'y', 't', 'v', 'm')", falhar=False)
        self.assertNotEqual(r.returncode, 0)

    def test_9_rever_linha_que_nao_existe_e_recusado(self):
        with self.assertRaises(espera.SalaIndisponivel):
            espera.rever("R1", 99, [{"CAMPO": "fact_time", "VALOR": "x", "BASE": "y"}],
                         extrator="t", versao="v", motivo="m")

    # ── o desfazer, e subir outra vez (o ultimo: apaga as revisoes) ──────
    def test_z_desfazer_e_subir_de_novo(self):
        r = subprocess.run([self.base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1",
                            "--single-transaction", "-f", str(DESFAZER), self.base.url],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        cols = self.sql("select count(*) from information_schema.columns where "
                        "table_name='sala_de_espera' and column_name in "
                        "('published_at_basis','source_location_basis',"
                        "'completude_tempo_lugar','janela_declarada')").stdout.strip()
        self.assertEqual(cols, "0")
        for obj in ("sala_de_espera_revisao", "sala_de_espera_gaveta", "sala_de_espera_atual"):
            self.assertEqual(self.sql("select to_regclass('public.%s') is null" % obj)
                             .stdout.strip(), "t", obj)
        self.assertEqual(self.sql("select count(*) from schema_migracao where versao='033'")
                         .stdout.strip(), "0")
        self.assertEqual(self.sql("select count(*) from sala_de_espera where run_id='R1'")
                         .stdout.strip(), "2", "desfazer apagou linhas da Sala")
        r = subprocess.run([shutil.which("bash") or "bash", "motor/cadeia_canonica.sh",
                            "migrations", self.base.url], cwd=str(RAIZ), env=self.env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr[-400:])
        self.assertIn("MIGRATION_033=PASS", r.stdout)


if __name__ == "__main__":
    unittest.main()
