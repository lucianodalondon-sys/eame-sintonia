#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEDUP-DOC — a Sala pergunta «já está?» pelo DOCUMENTO do bruto, não só pelo derivado.

Medido na Sala real a 25/09 (só leitura): 94 linhas, 13 documentos em dobro.
Três formas, cada uma com o seu teste:

  A · mesmo documento, mesmo bruto, mesmo item_id        (já barrado desde f2d5217b)
  B · mesmo documento, bruto com bytes novos → item_id novo (NÃO era barrado)
  C · o mesmo endereço registado em FONTES diferentes      (não se funde: outra fonte)

E a lei do bot Luciano (23:17): só funde quem tem identidade PROVADA
(FORWARD_IDENTIFIED). «Não sei qual documento» — FORWARD_IDENTITY_UNPROVEN ou
LEGACY_PRE_IDEMPOTENCY — nunca funde com nada.

Postgres descartável (binários de ~/orca/pgtmp), migrations pela cadeia canónica.
Sem esses binários, SALTA e diz porquê.
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

CORRIDAS = ["D%02d" % i for i in range(1, 17)]


@unittest.skipUnless(TEM_PG, "sem Postgres portatil (~/orca/pgtmp) ou sem bash: a prova nao correu")
class ASalaNaoRepeteODocumentoPelaChave(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pasta = Path(tempfile.mkdtemp(prefix="sala-dedup-doc-"))
        cls.base = E.Base(cls.pasta / "pg")
        env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
        r = cls.base.subir(RAIZ, env)
        if r["CODIGO"] != 0:
            cls.base.descer()
            raise unittest.SkipTest("migrations falharam: %s" % r["ERRO"])
        cls._amb = dict(os.environ)
        try:
            os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": cls.base.url,
                               "SINTONIA_PSQL_EXE": cls.base.exe("psql")})
            cls.sql("insert into collection_run (run_id, platform, started_at, rule_version) values "
                    + ", ".join("('%s', 'teste', now(), 'teste')" % c for c in CORRIDAS))
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
        r = subprocess.run([cls.base.exe("psql"), "-X", "-At", "-v", "ON_ERROR_STOP=1",
                            "-c", comando, cls.base.url],
                           capture_output=True, text=True, check=True)
        return r.stdout.strip()

    _n = 0

    def bruto(self, run, source_id, chave, estado="FORWARD_IDENTIFIED", sha="a"):
        """Uma linha em raw_asset. Devolve o id. O bruto nunca é alterado depois."""
        ASalaNaoRepeteODocumentoPelaChave._n += 1
        n = ASalaNaoRepeteODocumentoPelaChave._n
        k = "null" if chave is None else "'%s'" % chave
        base = "null" if chave is None else "'SOURCE_DOCUMENT_ID'"
        return int(self.sql(
            "insert into raw_asset (run_id, storage_path, media_type, bytes, sha256, captured_at, "
            "source_id, document_key, document_key_basis, identity_state) values "
            "('%s', 'teste/%d', 'text/html', 1, '%s', now(), '%s', %s, %s, '%s') returning id"
            % (run, n, (sha * 64)[:64], source_id, k, base, estado)).splitlines()[0])

    def unidade(self, item_id, raw_id, source_id="IT-T5-025", universo="T5"):
        item = {"id": item_id, "texto": "Ensaio de campo publicado com DOI " + item_id,
                "source_id": source_id, "fact_time": "2026-05-02"}
        d = admissao.decidir(item, "T5", corrida="R")
        u = admissao.pronto_para_inteligencia(item, d)
        return dict(u, ITEM_ID=item_id, UNIVERSO=universo, RAW_OBSERVATION_ID=raw_id,
                    SOURCE_ID=source_id)

    def contar(self, item_ids):
        lista = ", ".join("'%s'" % i for i in item_ids)
        return int(self.sql("select count(*) from sala_de_espera where item_id in (%s)" % lista))

    # ── A · mesmo bruto, mesmo item_id ───────────────────────────────────
    def test_A_mesmo_documento_mesmo_bruto_fica_uma_linha(self):
        r1 = self.bruto("D01", "IT-T5-015", "IT-T5-015:URL:news/a", sha="1")
        r2 = self.bruto("D02", "IT-T5-015", "IT-T5-015:URL:news/a", sha="1")
        espera.pousar("D01", [self.unidade("derived:101", r1, "IT-T5-015")])
        b = espera.pousar("D02", [self.unidade("derived:101", r2, "IT-T5-015")])
        self.assertEqual(b["INSERIDAS"], 0)
        self.assertEqual(self.contar(["derived:101"]), 1)

    # ── B · bytes novos, derivado novo, MESMO documento ─────────────────
    def test_B_bytes_novos_do_mesmo_documento_nao_ganham_segunda_linha(self):
        r1 = self.bruto("D03", "IT-T5-030", "IT-T5-030:URL:news/b", sha="2")
        r2 = self.bruto("D04", "IT-T5-030", "IT-T5-030:URL:news/b", sha="3")
        espera.pousar("D03", [self.unidade("derived:201", r1, "IT-T5-030")])
        b = espera.pousar("D04", [self.unidade("derived:202", r2, "IT-T5-030")])
        self.assertEqual((b["INSERIDAS"], b["JA_NA_SALA_POR_OUTRA_CORRIDA"]), (0, 1))
        self.assertEqual(self.contar(["derived:201", "derived:202"]), 1)

    # ── C · o mesmo endereço em fontes diferentes ────────────────────────
    def test_C_mesmo_endereco_em_outra_fonte_entra_e_na_mesma_fonte_nao(self):
        r1 = self.bruto("D05", "IT-T5-034", "IT-T5-034:URL:elenco-atti", sha="4")
        r2 = self.bruto("D06", "IT-T5-035", "IT-T5-035:URL:elenco-atti", sha="5")
        r3 = self.bruto("D07", "IT-T5-034", "IT-T5-034:URL:elenco-atti", sha="6")
        espera.pousar("D05", [self.unidade("derived:301", r1, "IT-T5-034")])
        b = espera.pousar("D06", [self.unidade("derived:302", r2, "IT-T5-035")])
        c = espera.pousar("D07", [self.unidade("derived:303", r3, "IT-T5-034")])
        self.assertEqual(b["INSERIDAS"], 1)      # outra fonte: não se funde
        self.assertEqual(c["INSERIDAS"], 0)      # a mesma fonte outra vez: barrada
        self.assertEqual(self.contar(["derived:301", "derived:302", "derived:303"]), 2)

    # ── A mesma chave em fontes diferentes não funde (chave sem prefixo) ─
    def test_C2_chave_igual_em_fontes_diferentes_nao_funde(self):
        r1 = self.bruto("D08", "IT-T3-002", "CAMPANIA:SA:16-09-2026", sha="7")
        r2 = self.bruto("D09", "IT-T3-099", "CAMPANIA:SA:16-09-2026", sha="8")
        espera.pousar("D08", [self.unidade("derived:401", r1, "IT-T3-002")])
        b = espera.pousar("D09", [self.unidade("derived:402", r2, "IT-T3-099")])
        self.assertEqual(b["INSERIDAS"], 1)

    # ── UNKNOWN · sem identidade provada nunca funde ─────────────────────
    def test_U1_identidade_nao_provada_nao_funde(self):
        r1 = self.bruto("D10", "IT-T5-040", None, estado="FORWARD_IDENTITY_UNPROVEN", sha="9")
        r2 = self.bruto("D11", "IT-T5-040", None, estado="FORWARD_IDENTITY_UNPROVEN", sha="9")
        espera.pousar("D10", [self.unidade("derived:501", r1, "IT-T5-040")])
        b = espera.pousar("D11", [self.unidade("derived:502", r2, "IT-T5-040")])
        self.assertEqual(b["INSERIDAS"], 1)

    def test_U2_legado_com_a_mesma_chave_nao_funde(self):
        # LEGACY_PRE_IDEMPOTENCY pode trazer chave, mas ela não é prova.
        r1 = self.bruto("D12", "IT-T5-041", "IT-T5-041:URL:x", estado="LEGACY_PRE_IDEMPOTENCY", sha="b")
        r2 = self.bruto("D13", "IT-T5-041", "IT-T5-041:URL:x", estado="LEGACY_PRE_IDEMPOTENCY", sha="c")
        espera.pousar("D12", [self.unidade("derived:601", r1, "IT-T5-041")])
        b = espera.pousar("D13", [self.unidade("derived:602", r2, "IT-T5-041")])
        self.assertEqual(b["INSERIDAS"], 1)

    def test_U3_sem_bruto_nao_funde(self):
        espera.pousar("D14", [self.unidade("derived:701", "NAO SEI", "IT-T5-042")])
        self.assertEqual(self.contar(["derived:701"]), 1)

    # ── o mesmo documento duas vezes na MESMA corrida ────────────────────
    def test_L_mesma_corrida_com_o_documento_duas_vezes_fica_uma(self):
        r1 = self.bruto("D15", "IT-T7-013", "IT-T7-013:URL:c", sha="d")
        r2 = self.bruto("D15", "IT-T7-013", "IT-T7-013:URL:c", sha="e")
        a = espera.pousar("D15", [self.unidade("derived:801", r1, "IT-T7-013"),
                                  self.unidade("derived:802", r2, "IT-T7-013")])
        self.assertEqual(a["INSERIDAS"], 1)
        self.assertEqual(self.contar(["derived:801", "derived:802"]), 1)

    # ── outro universo continua a ser outra entrada (REROUTE, D2) ───────
    def test_R_mesmo_documento_em_outro_universo_entra(self):
        r1 = self.bruto("D16", "IT-T5-030", "IT-T5-030:URL:news/b", sha="f")
        b = espera.pousar("D16", [self.unidade("derived:901", r1, "IT-T5-030", universo="T7")])
        self.assertEqual(b["INSERIDAS"], 1)

    # ── nada é apagado nem alterado ──────────────────────────────────────
    def test_Z_o_bruto_e_a_sala_so_crescem(self):
        brutos = int(self.sql("select count(*) from raw_asset"))
        self.assertGreaterEqual(brutos, ASalaNaoRepeteODocumentoPelaChave._n)


if __name__ == "__main__":
    unittest.main(verbosity=2)
