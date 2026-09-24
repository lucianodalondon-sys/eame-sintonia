#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SALA É IDEMPOTENTE POR DOCUMENTO — contra um Postgres REAL e descartável.

Medido na 2.ª passagem do ensaio offline (A2/A3): uma matéria revalidada e igual
(SEEN_AGAIN, derivado REUSED) ganhava uma segunda linha na Sala por outra corrida.
A trava da Sala era por corrida, não por documento.

    O MESMO DOCUMENTO NA MESMA VERSÃO = A MESMA LINHA.
    VERSÃO NOVA = LINHA NOVA. REENCAMINHADO A OUTRO UNIVERSO = OUTRA ENTRADA.

Um Postgres descartável (binários de ~/orca/pgtmp) numa porta livre, com as
migrations pela cadeia canónica. Sem esses binários, SALTA e diz porquê:
um teste que precisa de banco e não o tem não é um teste que passa.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for g in (str(RAIZ), str(RAIZ / "admissao")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas                          # noqa: E402,F401
import admissao                          # noqa: E402
import sala_de_espera as espera          # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

TEM_PG = (E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")).exists() and shutil.which("bash")


@unittest.skipUnless(TEM_PG, "sem Postgres portatil (~/orca/pgtmp) ou sem bash: a prova nao correu")
class ASalaNaoRepeteODocumento(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pasta = Path(tempfile.mkdtemp(prefix="sala-idempotente-"))
        cls.base = E.Base(cls.pasta / "pg")
        env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
        r = cls.base.subir(RAIZ, env)
        if r["CODIGO"] != 0:
            cls.base.descer()
            raise unittest.SkipTest("migrations falharam: %s" % r["ERRO"])
        cls._amb = dict(os.environ)
        # ⚠️ Um erro no setUpClass NAO chama o tearDownClass: sem isto, o
        # Postgres de teste fica ligado (aconteceu na primeira versao).
        try:
            os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": cls.base.url,
                               "SINTONIA_PSQL_EXE": cls.base.exe("psql")})
            psql = [cls.base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1", "-c"]
            for run in ("R1", "R2", "R3", "R4", "R5"):
                subprocess.run(psql + ["insert into collection_run (run_id, platform, started_at, "
                                       "rule_version) values ('%s', 'teste', now(), 'teste')" % run,
                                       cls.base.url], check=True, capture_output=True)
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        os.environ.clear()
        os.environ.update(cls._amb)
        cls.base.descer()
        shutil.rmtree(cls.pasta, ignore_errors=True)

    def unidade(self, item_id, universo="T5"):
        item = {"id": item_id, "texto": "Ensaio de campo publicado com DOI " + item_id,
                "source_id": "IT-T10-022", "fact_time": "2026-05-02"}
        # julgado pela regua T5 (o texto e de ciencia); o UNIVERSO de destino e o
        # que a Sala guarda — e o que distingue um REROUTE (D2) de uma repeticao.
        d = admissao.decidir(item, "T5", corrida="R")
        u = admissao.pronto_para_inteligencia(item, d)
        return dict(u, ITEM_ID=item_id, UNIVERSO=universo)

    def linhas(self):
        r = subprocess.run([self.base.exe("psql"), "-X", "-At", "-F", "|", "-c",
                            "select run_id, item_id, universo from sala_de_espera order by run_id, ordem",
                            self.base.url], capture_output=True, text=True, check=True)
        return [tuple(l.split("|")) for l in r.stdout.splitlines() if l.strip()]

    def test_1_documento_em_duas_corridas_fica_uma_linha(self):
        a = espera.pousar("R1", [self.unidade("derived:1"), self.unidade("derived:2")])
        self.assertEqual((a["ESTADO"], a["INSERIDAS"], a["JA_NA_SALA_POR_OUTRA_CORRIDA"]),
                         (espera.POUSOU, 2, 0))
        # R2 revalida derived:1 (igual) e traz derived:3 (versao/documento novo)
        b = espera.pousar("R2", [self.unidade("derived:1"), self.unidade("derived:3")])
        self.assertEqual((b["ESTADO"], b["INSERIDAS"], b["JA_NA_SALA_POR_OUTRA_CORRIDA"]),
                         (espera.POUSOU, 1, 1))
        ids = [l[1] for l in self.linhas()]
        self.assertEqual(ids.count("derived:1"), 1, self.linhas())
        self.assertIn("derived:3", ids)

    def test_2_corrida_so_com_repetidos_nao_escreve_nada(self):
        antes = self.linhas()
        c = espera.pousar("R3", [self.unidade("derived:1"), self.unidade("derived:2")])
        self.assertEqual(c["ESTADO"], espera.JA_ESTAVA)
        self.assertEqual(c["JA_NA_SALA_POR_OUTRA_CORRIDA"], 2)
        self.assertEqual(self.linhas(), antes)

    def test_3_repetir_a_mesma_corrida_continua_idempotente(self):
        antes = self.linhas()
        d = espera.pousar("R2", [self.unidade("derived:1"), self.unidade("derived:3")])
        self.assertEqual(d["ESTADO"], espera.JA_ESTAVA)
        self.assertEqual(self.linhas(), antes)

    def test_4_o_mesmo_documento_reencaminhado_a_outro_universo_entra(self):
        e = espera.pousar("R4", [self.unidade("derived:1", universo="T7")])
        self.assertEqual((e["ESTADO"], e["INSERIDAS"]), (espera.POUSOU, 1))
        self.assertIn(("R4", "derived:1", "T7"), self.linhas())

    def test_5_nenhum_documento_aparece_duas_vezes_no_mesmo_universo(self):
        espera.pousar("R5", [self.unidade("derived:2"), self.unidade("derived:3"),
                             self.unidade("derived:9")])
        pares = [(l[1], l[2]) for l in self.linhas()]
        self.assertEqual(len(pares), len(set(pares)), pares)


if __name__ == "__main__":
    unittest.main(verbosity=2)
