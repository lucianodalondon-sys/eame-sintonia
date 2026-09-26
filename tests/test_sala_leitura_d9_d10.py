#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SALA-LEITURA — D9 (o só-leitura pedido chega ao banco) e D10 (ler_atual traz o READY inteiro).

D9 · `_ambiente_psql()` deitava fora o `PGOPTIONS` de quem chamava: um
     `-c default_transaction_read_only=on` nunca chegava ao banco. Agora as opções
     do chamador são ACRESCENTADAS, e há um modo leitura (`SINTONIA_SALA_SO_LEITURA=1`)
     que corre cada leitura em `begin read only` e CONFERE `show transaction_read_only`.

         QUEM RECUSA A ESCRITA É O BANCO. OS TESTES NEGATIVOS PROVAM-NO.

D10 · `ler_atual()` não devolvia ESTADO, SOURCE_DECLARED_EVIDENCE_CLASS, FATO,
      CORRIDA, ADMITIDO_POR. Agora devolve o READY inteiro, pela mesma lista do
      dono (`CAMPOS_READY`), mais ORDEM, JANELA_DECLARADA, REVISOES e o histórico.

Postgres descartável (binários de ~/orca/pgtmp). Nunca a Sala real.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

#: a recusa do banco vem na lingua do servidor (medido: o Postgres desta maquina fala portugues)
RECUSA_DE_LEITURA = r"read-only|leitura-apenas|sola lettura|solo lectura"

TEM_PG = (E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")).exists() and shutil.which("bash")


def _ready(i, corrida="L1"):
    item = {"id": "derived:%d" % i, "texto": "Bollettino fitosanitario n. %d" % i,
            "source_id": "IT-T3-002", "artifact_type": "DERIVED",
            "parent_sha256": "a" * 64, "raw_asset_id": None,
            "captured_at": "2026-09-18T17:19:15Z"}
    d = adm.Decisao(item=item["id"], universo="T3", resultado=adm.SIM,
                    regra="teste", motivo="teste", corrida=corrida)
    return adm.pronto_para_inteligencia(item, d)


class _Ambiente(object):
    """Muda variáveis de ambiente e devolve-as como estavam."""

    def __init__(self, **kw):
        self.kw, self.antes = kw, {}

    def __enter__(self):
        for k, v in self.kw.items():
            self.antes[k] = os.environ.get(k)
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def __exit__(self, *_):
        for k, v in self.antes.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ── sem banco ─────────────────────────────────────────────────────────────
class D9SemBanco(unittest.TestCase):

    def test_as_opcoes_do_chamador_sao_acrescentadas(self):
        with _Ambiente(PGOPTIONS="-c default_transaction_read_only=on"):
            o = espera._ambiente_psql()["PGOPTIONS"]
        self.assertIn("-c default_transaction_read_only=on", o)
        self.assertIn("-c standard_conforming_strings=on", o)

    def test_o_escape_do_dono_vem_por_ultimo_e_ganha(self):
        with _Ambiente(PGOPTIONS="-c standard_conforming_strings=off"):
            o = espera._ambiente_psql()["PGOPTIONS"]
        self.assertTrue(o.endswith("-c standard_conforming_strings=on"), o)

    def test_sem_pgoptions_do_chamador_fica_so_o_do_dono(self):
        with _Ambiente(PGOPTIONS=None):
            self.assertEqual(espera._ambiente_psql()["PGOPTIONS"],
                             "-c standard_conforming_strings=on")

    def test_modo_leitura_sem_confirmacao_do_banco_levanta(self):
        """Se o banco não disser `on` na mesma transação, a leitura NÃO devolve nada."""
        pg = espera._Postgres("postgresql://x/y", so_leitura=True)
        falso = subprocess.CompletedProcess([], 0, stdout="off\n1\n", stderr="")
        with mock.patch.object(espera._Postgres, "_psql_exe", staticmethod(lambda: "psql")), \
                mock.patch.object(espera.subprocess, "run", return_value=falso):
            with self.assertRaises(espera.SalaIndisponivel):
                pg._consultar("select 1")

    def test_a_prova_on_vem_numa_linha_propria_e_os_dados_depois(self):
        """Forma REAL do psql (medida em Postgres, 26/09): `on`, mudanca de linha, e os registos."""
        pg = espera._Postgres("postgresql://x/y", so_leitura=True)
        real = subprocess.CompletedProcess([], 0, stdout="on\na" + pg.SEP_LINHA + "b\n", stderr="")
        sem_linhas = subprocess.CompletedProcess([], 0, stdout="on\n", stderr="")
        colado = subprocess.CompletedProcess([], 0, stdout="on" + pg.SEP_LINHA + "a\n", stderr="")
        with mock.patch.object(espera._Postgres, "_psql_exe", staticmethod(lambda: "psql")):
            with mock.patch.object(espera.subprocess, "run", return_value=real):
                self.assertEqual(pg._consultar("select 1"), ["a", "b"])
            with mock.patch.object(espera.subprocess, "run", return_value=sem_linhas):
                self.assertEqual(pg._consultar("select 1"), [])
            # a prova tem de ser a linha INTEIRA: `on` colado a dados nao e prova
            with mock.patch.object(espera.subprocess, "run", return_value=colado):
                with self.assertRaises(espera.SalaIndisponivel):
                    pg._consultar("select 1")

    def test_modo_leitura_embrulha_a_pergunta_em_begin_read_only(self):
        pg = espera._Postgres("postgresql://x/y", so_leitura=True)
        visto = {}

        def correr(argv, input=None, **kw):
            visto["sql"] = input
            return subprocess.CompletedProcess(argv, 0, stdout="on\n1\n", stderr="")
        with mock.patch.object(espera._Postgres, "_psql_exe", staticmethod(lambda: "psql")), \
                mock.patch.object(espera.subprocess, "run", side_effect=correr):
            self.assertEqual(pg._consultar("select 1"), ["1"])
        self.assertTrue(visto["sql"].startswith("begin read only;\nshow transaction_read_only;"))

    def test_fora_do_modo_leitura_a_escrita_nao_muda(self):
        pg = espera._Postgres("postgresql://x/y", so_leitura=False)
        visto = {}

        def correr(argv, input=None, **kw):
            visto["sql"] = input
            return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
        with mock.patch.object(espera._Postgres, "_psql_exe", staticmethod(lambda: "psql")), \
                mock.patch.object(espera.subprocess, "run", side_effect=correr):
            pg._executar("select 1;")
        self.assertEqual(visto["sql"], "select 1;")


class D10SemBanco(unittest.TestCase):

    def test_a_ponte_cobre_o_contrato_inteiro(self):
        self.assertEqual(set(espera._COLUNA_DO_CAMPO) | set(espera._CAMPOS_FORA_DE_COLUNA),
                         set(espera.CAMPOS_READY))


# ── com banco descartável ─────────────────────────────────────────────────
@unittest.skipUnless(TEM_PG, "sem Postgres portatil (~/orca/pgtmp) ou sem bash: a prova nao correu")
class NoBancoDescartavel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pasta = Path(tempfile.mkdtemp(prefix="sala-leitura-"))
        cls.base = E.Base(cls.pasta / "pg")
        assert ":54330/" not in cls.base.url, "isto e a Sala real"
        env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
        r = cls.base.subir(RAIZ, env)
        if r["CODIGO"] != 0:
            cls.base.descer()
            raise unittest.SkipTest("migrations falharam: %s" % r["ERRO"])
        cls._amb = dict(os.environ)
        try:
            os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": cls.base.url,
                               "SINTONIA_PSQL_EXE": cls.base.exe("psql")})
            os.environ.pop("PGOPTIONS", None)
            os.environ.pop(espera.VAR_SO_LEITURA, None)
            cls.sql("insert into collection_run (run_id, platform, started_at, rule_version) "
                    "values ('L1', 'teste', now(), 'teste'), ('L2', 'teste', now(), 'teste'), "
                    "('L3', 'teste', now(), 'teste')")
            espera.pousar("L1", [_ready(1), _ready(2)])
            espera.rever("L1", 1, [{"CAMPO": "fact_location", "VALOR": "Puglia", "BASE": "teste"}],
                         extrator="teste", versao="v1", motivo="teste")
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
    def sql(cls, comando):
        return subprocess.run([cls.base.exe("psql"), "-X", "-At", "-v", "ON_ERROR_STOP=1",
                               "-c", comando, cls.base.url],
                              capture_output=True, text=True, check=True).stdout.strip()

    def linhas(self):
        return int(self.sql("select count(*) from sala_de_espera"))

    # ── D9 · NEGATIVOS: a escrita é recusada PELO BANCO ─────────────────
    def test_N1_pgoptions_so_leitura_do_chamador_chega_ao_banco(self):
        """O defeito D9: antes, isto POUSAVA."""
        antes = self.linhas()
        with _Ambiente(PGOPTIONS="-c default_transaction_read_only=on"):
            with self.assertRaises(espera.SalaIndisponivel) as ctx:
                espera.pousar("L2", [_ready(3, "L2")])
        self.assertRegex(str(ctx.exception).lower(), RECUSA_DE_LEITURA)
        self.assertEqual(self.linhas(), antes)

    def test_N2_modo_leitura_recusa_pousar(self):
        antes = self.linhas()
        with _Ambiente(**{espera.VAR_SO_LEITURA: "1"}):
            with self.assertRaises(espera.SalaIndisponivel) as ctx:
                espera.pousar("L3", [_ready(4, "L3")])
        self.assertRegex(str(ctx.exception).lower(), RECUSA_DE_LEITURA)
        self.assertEqual(self.linhas(), antes)

    def test_N3_modo_leitura_recusa_rever(self):
        antes = self.sql("select count(*) from sala_de_espera_revisao")
        with _Ambiente(**{espera.VAR_SO_LEITURA: "1"}):
            with self.assertRaises(espera.SalaIndisponivel):
                espera.rever("L1", 0, [{"CAMPO": "fact_location", "VALOR": "Lazio",
                                        "BASE": "teste"}],
                             extrator="teste", versao="v1", motivo="teste")
        self.assertEqual(self.sql("select count(*) from sala_de_espera_revisao"), antes)

    def test_P1_modo_leitura_le_e_prova_on(self):
        with _Ambiente(**{espera.VAR_SO_LEITURA: "1"}):
            self.assertEqual(len(espera.ler("L1")["ITENS"]), 2)
            self.assertEqual(len(espera.ler_atual("L1")["ITENS"]), 2)

    def test_P2_fora_do_modo_leitura_pousar_continua_a_pousar(self):
        with _Ambiente(PGOPTIONS=None, **{espera.VAR_SO_LEITURA: None}):
            r = espera.pousar("L2", [_ready(5, "L2")])
        self.assertEqual(r["INSERIDAS"], 1)

    # ── D10 ─────────────────────────────────────────────────────────────
    def test_D10a_ler_atual_traz_o_ready_inteiro_na_ordem_do_dono(self):
        u = espera.ler_atual("L1")["ITENS"][0]
        self.assertEqual(list(u)[:len(espera.CAMPOS_READY)], list(espera.CAMPOS_READY))
        for extra in ("ORDEM", "JANELA_DECLARADA", "REVISOES", "HISTORICO_DE_REVISOES"):
            self.assertIn(extra, u)

    def test_D10b_sem_revisao_ler_atual_e_igual_a_ler(self):
        pousado = espera.ler("L1")["ITENS"][0]
        atual = espera.ler_atual("L1")["ITENS"][0]
        self.assertEqual({c: atual[c] for c in espera.CAMPOS_READY}, pousado)

    def test_D10c_com_revisao_o_valor_revisto_e_o_historico(self):
        atual = {u["ORDEM"]: u for u in espera.ler_atual("L1")["ITENS"]}[1]
        self.assertEqual(atual["FACT_LOCATION"], "Puglia")
        self.assertEqual(atual["REVISOES"], 1)
        h = atual["HISTORICO_DE_REVISOES"]
        self.assertEqual([(r["CAMPO"], r["VALOR"]) for r in h], [("fact_location", "Puglia")])
        self.assertEqual(espera.ler("L1")["ITENS"][1]["FACT_LOCATION"], "NAO SEI")

    def test_D10d_o_retry_continua_a_ser_retry(self):
        """`ler` não mudou de forma: pousar o que se leu é JA_ESTAVA, não conflito."""
        self.assertEqual(espera.pousar("L1", espera.ler("L1")["ITENS"])["ESTADO"], espera.JA_ESTAVA)


if __name__ == "__main__":
    unittest.main(verbosity=2)
