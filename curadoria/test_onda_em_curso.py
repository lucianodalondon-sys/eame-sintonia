#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ONDA EM CURSO (CUR-PRONTA): a coleta le uma foto, o Curator continua.

Sem rede, em pastas temporarias:
  1. com onda aberta, o portao perguntado por `--ids` responde pela FOTO e nao
     abre nenhum livro do Curator (o livro pode estar ilegivel, a meio de uma
     escrita, ou ter mudado — a resposta nao muda);
  2. foto que existe e nao se le = NAO SEI = o portao sai com rc 3 (recusa);
  3. sem onda, o portao volta ao livro vivo, como sempre;
  4. o AVANCAR nao canaria anfitrioes que estao na onda.
"""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import avancar_fontes as AV       # noqa: E402
import collection_gate as CG      # noqa: E402
import lifecycle as LC            # noqa: E402
import onda_em_curso as OND       # noqa: E402

AGORA = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)


class _Pasta(unittest.TestCase):

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.d = Path(self._td.name)
        self.addCleanup(setattr, OND, "ONDA", OND.ONDA)
        OND.ONDA = self.d / "ONDA-EM-CURSO.json"
        self.addCleanup(setattr, CG, "SAIDA", CG.SAIDA)
        CG.SAIDA = self.d / "COLLECTION-INTAKE.json"
        self.coorte = self.d / "COORTE.json"
        self.coorte.write_text(json.dumps({"COORTE": [
            {"SOURCE_ID": "IT-T9-001", "INDEX_URL": "https://www.um.it/news/"},
            {"SOURCE_ID": "IT-T9-002", "INDEX_URL": "https://dois.it/"}]}), encoding="utf-8")

    def _portao(self, *ids):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = CG.main(["--ids=%s" % ",".join(ids), "--json"])
        return rc, (json.loads(out.getvalue()) if rc == 0 else err.getvalue())


class OPortaoPelaFoto(_Pasta):

    def test_com_onda_responde_pela_foto_sem_abrir_o_livro(self):
        OND.abrir(self.coorte)
        # o livro do Curator «a meio de uma escrita»: se o portao o abrisse, rebentava
        self.addCleanup(setattr, LC, "LIVRO", LC.LIVRO)
        LC.LIVRO = self.d / "LEDGER.json"
        LC.LIVRO.write_text('{"TRANSICOES": [', encoding="utf-8")
        rc, d = self._portao("IT-T9-001", "IT-T9-777")
        self.assertEqual(rc, 0, d)
        self.assertEqual(d["COLLECTION_ELIGIBLE_IDS"], ["IT-T9-001"])
        motivos = {l["SOURCE_ID"]: l["MOTIVO"] for l in d["LINHAS"]}
        self.assertEqual(motivos, {"IT-T9-001": "ONDA_EM_CURSO",
                                   "IT-T9-777": "FORA_DA_ONDA_EM_CURSO"})
        self.assertEqual(d["ONDA_EM_CURSO"]["COORTE_SHA256"], OND.ler()["COORTE_SHA256"])

    def test_foto_ilegivel_e_nao_sei_e_recusa(self):
        OND.ONDA.write_text("{ cortado", encoding="utf-8")
        rc, err = self._portao("IT-T9-001")
        self.assertEqual(rc, 3)
        self.assertIn("NAO SEI", err)

    def test_fechar_devolve_o_portao_ao_livro_vivo(self):
        OND.abrir(self.coorte)
        self.assertTrue(OND.fechar())
        self.assertIsNone(OND.ler())
        self.assertEqual(OND.hosts_na_onda(), set())

    def test_a_foto_guarda_o_sha256_da_coorte(self):
        import hashlib
        d = OND.abrir(self.coorte)
        self.assertEqual(d["COORTE_SHA256"], hashlib.sha256(self.coorte.read_bytes()).hexdigest())
        self.assertEqual(d["HOSTS"], ["dois.it", "um.it"])


class OCuratorContinuaForaDaOnda(_Pasta):

    def test_avancar_salta_so_os_anfitrioes_da_onda(self):
        OND.abrir(self.coorte)
        html = lambda u: {"ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": u}}
        cs = AV.candidatas_a_avancar(
            AGORA, estados={"A": LC.DEGRADED, "B": LC.DEGRADED},
            contratos={"A": html("https://um.it/outra/"), "B": html("https://tres.it/")},
            tarefas=[], reguas={}, tabela={}, candidatas=[], caract=[], ponte={})
        self.assertEqual([c["SOURCE_ID"] for c in cs], ["B"])
        OND.fechar()
        cs = AV.candidatas_a_avancar(
            AGORA, estados={"A": LC.DEGRADED}, contratos={"A": html("https://um.it/outra/")},
            tarefas=[], reguas={}, tabela={}, candidatas=[], caract=[], ponte={})
        self.assertEqual([c["SOURCE_ID"] for c in cs], ["A"])


if __name__ == "__main__":
    unittest.main()
