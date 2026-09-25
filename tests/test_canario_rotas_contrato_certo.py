# -*- coding: utf-8 -*-
"""PONTE-ONBOARD · o canario de rotas prova o contrato que o robo VAI USAR.

Sem rede: `provar` e trocado por um dublo que so devolve ROUTE_PROVEN. O que se
prova aqui e QUAL contrato o canario le e que impressao digital escreve.

A fixture `ponte_onboard_17_contratos.json` e o caso medido no vivo a 25/09/2026:
os 17 contratos a onboardar, no HEAD do Git (574 fontes) e no disco (762). 14 dos
17 estavam trocados (9 ausentes do HEAD, 5 com outra aquisicao).
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "medidas"))
import canario_rotas_elegiveis as CR  # noqa: E402
import sha_do_contrato as SHA         # noqa: E402

FIX = json.loads((RAIZ / "tests" / "fixtures" / "ponte_onboard_17_contratos.json").read_text(encoding="utf-8"))
IDS = sorted(FIX["DISCO"])


def _livro(contratos: dict) -> dict:
    return {"DATASET": "SOURCE-CURATOR-CONTRACTS-V1", "FONTES": list(contratos.values())}


def _provado(sid, c):
    return {"SOURCE_ID": sid, "VEREDITO": "ROUTE_PROVEN", "CAUSA": "dublo",
            "INDEX_URL": (c.get("ACQUISITION") or {}).get("INDEX_URL")}


class ArvoreComGitAtrasado:
    """Uma arvore onde o HEAD tem o curador VELHO e o disco o NOVO — como o vivo."""

    def __enter__(self):
        self.d = tempfile.TemporaryDirectory()
        raiz = Path(self.d.name)
        (raiz / "curadoria").mkdir()
        f = raiz / "curadoria" / "italy_contracts_curator.json"
        git = lambda *a: subprocess.run(["git", *a], cwd=raiz, capture_output=True, check=True)
        git("init", "-q")
        f.write_text(json.dumps(_livro(FIX["HEAD"])), encoding="utf-8")
        git("add", "curadoria/italy_contracts_curator.json")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "head")
        f.write_text(json.dumps(_livro(FIX["DISCO"])), encoding="utf-8")   # o bot escreve e nao commita
        self.patches = [mock.patch.object(CR, "RAIZ", raiz),
                        mock.patch.object(CR, "CONTRATOS_EM_DISCO", f),
                        mock.patch.object(CR, "SAIDA", raiz / "curadoria" / "ROTAS-ELEGIVEIS-V1.json"),
                        mock.patch.object(CR, "provar", side_effect=_provado),
                        mock.patch.object(CR, "PAUSA_S", 0)]
        for p in self.patches:
            p.start()
        return raiz

    def __exit__(self, *a):
        for p in self.patches:
            p.stop()
        self.d.cleanup()


class CanarioLeOContratoCerto(unittest.TestCase):
    def test_a_fixture_e_o_caso_medido_14_de_17_trocados(self):
        trocados = [s for s in IDS if s not in FIX["HEAD"]
                    or SHA.do_contrato(FIX["HEAD"][s]) != SHA.do_contrato(FIX["DISCO"][s])]
        self.assertEqual((17, 14), (len(IDS), len(trocados)))

    def test_por_omissao_prova_o_contrato_em_disco_e_escreve_a_impressao(self):
        with ArvoreComGitAtrasado() as raiz:
            CR.main(["--fontes=" + ",".join(IDS), "--escrever"])
            linhas = {l["SOURCE_ID"]: l for l in json.loads(
                (raiz / "curadoria" / "ROTAS-ELEGIVEIS-V1.json").read_text(encoding="utf-8"))["LINHAS"]}
        errados = [s for s in IDS if linhas[s].get("CONTRATO_SHA256") != SHA.do_contrato(FIX["DISCO"][s])]
        self.assertEqual([], errados)
        self.assertEqual({"disco:curadoria/italy_contracts_curator.json"},
                         {l["CONTRATO_LIDO_DE"] for l in linhas.values()})
        self.assertTrue(all(l.get("PROVADO_EM") for l in linhas.values()))

    def test_o_ref_de_git_so_quando_pedido_por_extenso_e_diz_de_onde_veio(self):
        with ArvoreComGitAtrasado() as raiz:
            CR.main(["--fontes=" + ",".join(s + "@HEAD" for s in IDS), "--escrever"])
            linhas = json.loads((raiz / "curadoria" / "ROTAS-ELEGIVEIS-V1.json").read_text(encoding="utf-8"))["LINHAS"]
        # o velho comportamento, reproduzido: 9 sem contrato no HEAD, 5 com outra impressao
        sem = [l for l in linhas if l["VEREDITO"] == "UNKNOWN"]
        outra = [l for l in linhas if l.get("CONTRATO_SHA256")
                 and l["CONTRATO_SHA256"] != SHA.do_contrato(FIX["DISCO"][l["SOURCE_ID"]])]
        self.assertEqual((9, 5), (len(sem), len(outra)))
        self.assertTrue(all(l.get("CONTRATO_LIDO_DE", "HEAD:").startswith("HEAD:")
                            or "HEAD:" in l.get("CAUSA", "") for l in linhas))

    def test_juntar_rondas_nao_apaga_a_ronda_anterior(self):
        with ArvoreComGitAtrasado() as raiz:
            CR.main(["--fontes=" + ",".join(IDS[:10]), "--escrever"])
            CR.main(["--fontes=" + ",".join(IDS[10:]), "--juntar"])
            linhas = json.loads((raiz / "curadoria" / "ROTAS-ELEGIVEIS-V1.json").read_text(encoding="utf-8"))["LINHAS"]
        self.assertEqual(IDS, sorted(l["SOURCE_ID"] for l in linhas))

    def test_juntar_a_prova_nova_substitui_a_da_mesma_fonte(self):
        velha = [{"SOURCE_ID": "A", "VEREDITO": "UNKNOWN"}, {"SOURCE_ID": "B", "VEREDITO": "UNKNOWN"}]
        nova = [{"SOURCE_ID": "A", "VEREDITO": "ROUTE_PROVEN"}]
        self.assertEqual({"A": "ROUTE_PROVEN", "B": "UNKNOWN"},
                         {l["SOURCE_ID"]: l["VEREDITO"] for l in CR.juntar(velha, nova)})

    def test_a_impressao_ignora_campos_que_o_coletor_nao_le(self):
        c = dict(FIX["DISCO"][IDS[0]])
        self.assertEqual(SHA.do_contrato(c), SHA.do_contrato(dict(c, NOTAS="x", EVIDENCE_REF="y")))
        aq = dict(c["ACQUISITION"], MAX_TARGETS=99)
        self.assertNotEqual(SHA.do_contrato(c), SHA.do_contrato(dict(c, ACQUISITION=aq)))


if __name__ == "__main__":
    unittest.main()
