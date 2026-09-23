#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC4 — os @handle do YouTube resolvidos pela capacidade do Scrap, e lidos pelo QUALIFY.

Guardas:
  · playlist e /c/ NUNCA vão à API (o resolvedor leria «playlist» como handle);
  · só RESOLVIDO com channel_id válido entra no registo como resolvido;
  · um erro de hoje não apaga a prova de ontem;
  · o QUALIFY só usa a resolução da MESMA candidata com o MESMO endereço;
  · a chave nunca aparece no registo.
Sem rede: a capacidade do Scrap é substituída por uma função que devolve o que a
API devolveria. A lane real não é tocada.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F                        # noqa: E402
import fonte_nova as FN                 # noqa: E402
import lifecycle as LC                  # noqa: E402
import resolver_handles_youtube as RH   # noqa: E402
import rota_do_scrap_youtube as RSY     # noqa: E402
import worker as W                      # noqa: E402

CANAL = "UCaaaaaaaaaaaaaaaaaaaaaa"


class _Collect:
    def __init__(self, canal=CANAL):
        self.chamadas, self.canal = [], canal

    def __call__(self, *, platform, capability, run_id, account_url):
        self.chamadas.append((platform, capability, account_url))
        if self.canal:
            return [{"CHANNEL_ID": self.canal, "RESOLVED_BY": "forHandle"}], {"RESULT": "OK"}
        return [], {"RESULT": "CHANNEL_IDENTITY_UNRESOLVED"}


class AsFormas(unittest.TestCase):
    def test_formas(self):
        self.assertEqual(RH.forma("https://www.youtube.com/@agri"), "HANDLE")
        self.assertEqual(RH.forma("https://www.youtube.com/user/agri"), "USER")
        self.assertEqual(RH.forma("https://www.youtube.com/c/Regione"), "C")
        self.assertEqual(RH.forma("https://youtube.com/playlist?list=PL1"), "PLAYLIST")
        self.assertEqual(RH.forma("http://www.youtube.com/arpatoscana"), "NOME_NU")
        self.assertEqual(RH.forma("https://www.youtube.com/watch?v=abc"), "OUTRO")

    def test_as_35_da_porta_real(self):
        p = RH.pendentes()
        self.assertEqual(len(p), 35)
        self.assertEqual(sum(c["FORMA"] in RH.RESOLVIVEIS for c in p), 31)


class OResolvedor(unittest.TestCase):
    def test_playlist_e_c_nunca_vao_a_api(self):
        col = _Collect()
        lista = [{"CANDIDATA_ID": "C1", "URL": "https://youtube.com/playlist?list=PL1", "FORMA": "PLAYLIST"},
                 {"CANDIDATA_ID": "C2", "URL": "https://www.youtube.com/c/X", "FORMA": "C"},
                 {"CANDIDATA_ID": "C3", "URL": "https://www.youtube.com/@agri", "FORMA": "HANDLE"}]
        out = {l["CANDIDATA_ID"]: l for l in RH.resolver(lista, "R", collect=col)}
        self.assertEqual([c[2] for c in col.chamadas], ["https://www.youtube.com/@agri"])
        self.assertEqual(out["C1"]["ESTADO"], "NAO_SUPORTADO")
        self.assertEqual(out["C2"]["ESTADO"], "NAO_SUPORTADO")
        self.assertEqual((out["C3"]["ESTADO"], out["C3"]["CHANNEL_ID"]), ("RESOLVIDO", CANAL))
        self.assertEqual(col.chamadas[0][:2], ("YOUTUBE", "youtube.channel.resolve"))

    def test_canal_invalido_nao_e_resolvido(self):
        out = RH.resolver([{"CANDIDATA_ID": "C", "URL": "https://www.youtube.com/@x", "FORMA": "HANDLE"}],
                          "R", collect=_Collect(canal="UCcurto"))
        self.assertEqual((out[0]["ESTADO"], out[0]["CHANNEL_ID"]), ("NAO_RESOLVIDO", None))

    def test_erro_de_hoje_nao_apaga_a_prova_de_ontem(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "reg.json"
            ok = RH.resolver([{"CANDIDATA_ID": "C", "URL": "u", "FORMA": "HANDLE"}], "R1", collect=_Collect())
            RH.gravar(ok, f)
            mau = RH.resolver([{"CANDIDATA_ID": "C", "URL": "u", "FORMA": "HANDLE"}], "R2", collect=_Collect(None))
            RH.gravar(mau, f)
            d = json.loads(f.read_text(encoding="utf-8"))
            self.assertEqual(d["LINHAS"][0]["RUN_ID"], "R1")
            self.assertEqual(d["LINHAS"][0]["ESTADO"], "RESOLVIDO")

    def test_o_registo_nao_guarda_titulo_nem_chave(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "reg.json"
            RH.gravar(RH.resolver([{"CANDIDATA_ID": "C", "URL": "u", "FORMA": "HANDLE"}], "R",
                                  collect=_Collect()), f)
            txt = f.read_text(encoding="utf-8")
            self.assertNotIn("TITLE", txt)
            self.assertNotIn("AIza", txt)


class OQualifyLeAResolucao(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="soc4-")))
        alvos = {(F, "FILA"): "fila.json", (LC, "LIVRO"): "livro.json",
                 (W, "ALLOCATION"): "alloc.json", (W, "EVIDENCIA"): "evid.json",
                 (W, "PULSO"): "pulso.json", (W, "CONTRATOS"): "contratos.json",
                 (FN, "FILA"): "candidatas.json", (RSY, "TABELA"): "tabela.json",
                 (RSY, "LIVRO"): "contratos.json", (RSY, "ALLOCATION"): "alloc.json",
                 (RSY, "CONTRATOS_MJS"): "contratos.mjs", (RSY, "ATLAS"): "atlas.md",
                 (RSY, "RESOLUCAO"): "resolucao.json"}
        for (mod, attr), nome in alvos.items():
            self.addCleanup(setattr, mod, attr, getattr(mod, attr))
            setattr(mod, attr, self.tmp / nome)
        W.ALLOCATION.write_text(json.dumps({"MAIOR_POR_TERRITORIO_ANTES": {"T7": 14}, "NOVAS": []}),
                                encoding="utf-8")
        for f in (RSY.TABELA, W.CONTRATOS):
            f.write_text(json.dumps({"FONTES": []}), encoding="utf-8")
        RSY.CONTRATOS_MJS.write_text("", encoding="utf-8")
        RSY.ATLAS.write_text("", encoding="utf-8")

    def _resolucao(self, cand, url, estado="RESOLVIDO", canal=CANAL):
        RSY.RESOLUCAO.write_text(json.dumps({"LINHAS": [{"CANDIDATA_ID": cand, "URL": url, "ESTADO": estado,
                                                          "CHANNEL_ID": canal}]}), encoding="utf-8")

    def _qualify(self, cand, url):
        doc = FN.carregar()
        doc["CANDIDATAS"].append({"CANDIDATA_ID": cand, "TIPO": "YOUTUBE",
                                  "NOME": "Consorzio Tutela Vini — Youtube ufficiale", "URL": url,
                                  "PAIS": "IT", "ESTADO": "EM_ANALISE", "SOURCE_ID": None})
        FN.gravar(doc)
        F.enfileirar(cand, F.QUALIFY, priority=30, motivo="teste")
        return W.correr(max_tarefas=1, pausa=0, verboso=False)[0]

    def _novas(self):
        return json.loads(W.ALLOCATION.read_text(encoding="utf-8"))["NOVAS"]

    def test_handle_resolvido_qualifica_com_o_canal(self):
        self._resolucao("CAND-H1", "https://www.youtube.com/@vini")
        r = self._qualify("CAND-H1", "https://www.youtube.com/@vini")
        self.assertEqual(r["RESULTADO"], "OK")
        self.assertEqual(self._novas()[0]["SOURCE_NATIVE_ID"], CANAL)

    def test_resolucao_de_outro_endereco_nao_conta(self):
        self._resolucao("CAND-H2", "https://www.youtube.com/@outro")
        r = self._qualify("CAND-H2", "https://www.youtube.com/@vini")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertEqual(self._novas(), [])

    def test_nao_resolvido_nao_conta(self):
        self._resolucao("CAND-H3", "https://www.youtube.com/@vini", estado="NAO_RESOLVIDO")
        r = self._qualify("CAND-H3", "https://www.youtube.com/@vini")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertIn("NAO SEI", r["PORQUE"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
