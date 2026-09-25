"""MICRO-V3 pela onda web: `--fontes=`/`--lote=` correm SO as fontes escolhidas, com o livro do teto por onda (D38).

Sem rede e sem Sala: o micro_coleta e o ensaio_offline sao falsos; o transporte falso escreve no livro
da onda (SINTONIA_TETO_ONDA) como o node faria.
"""
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
import onda_web as O  # noqa: E402

COORTE = [("IT-A1", "https://www.cia.it/a"), ("IT-B1", "https://myfruit.it/"),
          ("IT-A2", "https://sub.cia.it/b"), ("IT-C1", "https://www.arpae.it/"),
          ("IT-A3", "https://cia.it/c")]
DOM = {"www.cia.it": "cia.it", "sub.cia.it": "cia.it", "cia.it": "cia.it",
       "myfruit.it": "myfruit.it", "www.arpae.it": "arpae.it"}


class AEscolha(unittest.TestCase):

    def test_1_so_as_pedidas_e_na_ordem_da_coorte(self):
        self.assertEqual(O.escolher(COORTE, ["IT-C1", "IT-A1"]),
                         [("IT-A1", "https://www.cia.it/a"), ("IT-C1", "https://www.arpae.it/")])

    def test_2_sem_escolha_e_a_coorte_toda(self):
        self.assertEqual(O.escolher(COORTE, None), COORTE)

    def test_3_fonte_fora_da_coorte_recusa_tudo(self):
        with self.assertRaises(SystemExit) as e:
            O.escolher(COORTE, ["IT-A1", "IT-ZZ"])
        self.assertIn("FONTE_FORA_DA_COORTE", str(e.exception))
        self.assertIn("IT-ZZ", str(e.exception))

    def test_4_lista_vazia_nao_vira_a_coorte_toda(self):
        with self.assertRaises(SystemExit):
            O.escolher(COORTE, [])
        with self.assertRaises(SystemExit):
            O.fontes_do_argumento({"fontes": " , "})

    def test_5_lote_e_fontes(self):
        d = Path(tempfile.mkdtemp(prefix="onda-lote-"))
        try:
            lote = d / "LOTE.json"
            lote.write_text(json.dumps({"LOTE": [{"SOURCE_ID": "IT-B1"}, {"SOURCE_ID": "IT-C1"}]}), encoding="utf-8")
            self.assertEqual(O.fontes_do_argumento({"lote": str(lote)}), ["IT-B1", "IT-C1"])
            self.assertEqual(O.fontes_do_argumento({"fontes": "IT-B1, IT-C1"}), ["IT-B1", "IT-C1"])
            self.assertIsNone(O.fontes_do_argumento({}))
            with self.assertRaises(SystemExit):
                O.fontes_do_argumento({"fontes": "IT-B1", "lote": str(lote)})
        finally:
            shutil.rmtree(d, ignore_errors=True)


class OCorrerSoComAsEscolhidas(unittest.TestCase):
    """`correr` inteiro com micro_coleta falso: quem e chamado, e o teto do livro da onda."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="onda-fontes-"))
        self.saida = self.tmp / "onda"
        self.chamadas = []
        self.livros = []
        teste = self

        def correr_falso(ids, *, autorizado, saida):
            s = ids[0]
            teste.chamadas.append(s)
            livro = Path(os.environ["SINTONIA_TETO_ONDA"])
            teste.livros.append(str(livro))
            host = dict(COORTE)[s].split("/")[2]
            gasto = json.loads(livro.read_text(encoding="utf-8"))["PEDIDOS_POR_DOMINIO"] if livro.exists() else {}
            gasto[DOM[host]] = min(O.TETO, gasto.get(DOM[host], 0) + 5)       # o transporte gasta ate ao teto
            livro.write_text(json.dumps({"PEDIDOS_POR_DOMINIO": gasto}), encoding="utf-8")
            return {"CORRIDAS": [{"CORREU": True, "STATUS": "SUCCESS", "RUN_ID": "R-" + s,
                                  "EGRESSO_ANTES": {"PAIS": "IT"}, "EGRESSO_DEPOIS": {"PAIS": "IT"}}]}

        M = types.ModuleType("micro_coleta")
        M.precondicoes = lambda: []
        M.correr = correr_falso
        E = types.ModuleType("ensaio_offline")
        E.fotografia = lambda: {"sala": {"LINHAS": 1}}
        oficial = {"COORTE": {"ESTADO": "CONGELADA", "COORTE": [{"SOURCE_ID": s, "INDEX_URL": u} for s, u in COORTE]},
                   "SHA256_DO_COMMIT": "abc", "HEAD": "h"}
        self.patches = [mock.patch.dict(sys.modules, {"micro_coleta": M, "ensaio_offline": E}),
                        mock.patch.object(O, "coorte_oficial", lambda *a, **k: oficial),
                        mock.patch.object(O, "dominios", lambda hosts: {h: DOM[h] for h in hosts}),
                        mock.patch.object(O, "historicos", lambda extra=None: []),
                        mock.patch.object(O, "LEDGER", self.tmp / "nao-existe.jsonl"),
                        mock.patch.object(O, "AVISO", self.tmp / "AVISO.txt"),
                        mock.patch.dict(os.environ, {})]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _estado(self):
        return json.loads((self.saida / "ONDA-WEB-ESTADO.json").read_text(encoding="utf-8"))

    def test_6_so_as_escolhidas_correm(self):
        rc = O.correr("coorte", "abc", self.saida, None, ["IT-B1", "IT-C1"])
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(self.chamadas), ["IT-B1", "IT-C1"])
        self.assertEqual(self._estado()["SO_AS_FONTES"], ["IT-B1", "IT-C1"])
        self.assertEqual(sorted(x["SOURCE_ID"] for x in self._estado()["FONTES"]), ["IT-B1", "IT-C1"])

    def test_7_o_livro_da_onda_e_o_da_saida(self):
        O.correr("coorte", "abc", self.saida, None, ["IT-B1"])
        self.assertEqual(self.livros, [str(self.saida / "TETO-ONDA.json")])

    def test_8_o_teto_por_dominio_vale_entre_escolhidas(self):
        """IT-A1 e IT-A3 sao do mesmo dominio (cia.it): a 1.a gasta 5, a 2.a nao corre (TETO_DOMINIO)."""
        rc = O.correr("coorte", "abc", self.saida, None, ["IT-A1", "IT-A3", "IT-B1"])
        self.assertEqual(rc, 0)
        cia = [s for s in self.chamadas if s in ("IT-A1", "IT-A3")]
        self.assertEqual(len(cia), 1)
        saltou = [x for x in self._estado()["FONTES"] if x.get("PORQUE_NAO_CORREU") == "TETO_DOMINIO"]
        self.assertEqual(len(saltou), 1)
        self.assertEqual(saltou[0]["DOMINIO"], "cia.it")
        self.assertNotIn("IT-A2", self.chamadas)
        self.assertLessEqual(max(O.ler_livro(self.saida / "TETO-ONDA.json").values()), O.TETO)

    def test_9_fora_da_coorte_recusa_antes_de_qualquer_chamada(self):
        with self.assertRaises(SystemExit):
            O.correr("coorte", "abc", self.saida, None, ["IT-B1", "IT-ZZ"])
        self.assertEqual(self.chamadas, [])

    def test_10_main_passa_o_lote_ao_correr(self):
        lote = self.tmp / "LOTE.json"
        lote.write_text(json.dumps({"LOTE": [{"SOURCE_ID": "IT-C1"}]}), encoding="utf-8")
        rc = O.main(["--correr", "--lote=%s" % lote, "--sha256=abc", "--saida=%s" % self.saida])
        self.assertEqual(rc, 0)
        self.assertEqual(self.chamadas, ["IT-C1"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
