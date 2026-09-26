# -*- coding: utf-8 -*-
"""PASSO 9 generico da MICRO-PROVA: so regista pela porta o que o canal aceita; as A_DECIDIR nunca entram. Sem rede."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "candidatas"))
import colher_prova_territorio as CPT   # noqa: E402
import fila as F                        # noqa: E402
import fonte_nova as FN                 # noqa: E402
import micro_prova_passo9 as P9         # noqa: E402

URL = "https://www.condifesaqzxv.example/"


def _prova(papel, u, c):
    return {"PAPEL": papel, "URL": u, "SHA256": c * 64, "BYTES_EM": "fora do Git (teste)"}


def _decidida(cid="L2B-01", territorio="T3", url=URL, nome="Condifesa Qzxv"):
    return {"CANDIDATA_ID": cid, "NOME": nome, "URL": url, "TERRITORIO": territorio, "PAIS": "IT",
            "DECIDIDO_POR": "OPUS (teste)", "PORQUE": "consorzio di difesa com avisos datados",
            "PROVAS": [_prova("INSTITUCIONAL", url + "statuto", "a"), _prova("CONTEUDO", url + "avviso-1", "b"),
                       _prova("CONTEUDO", url + "avviso-2", "c")]}


class Passo9(unittest.TestCase):
    def setUp(self):
        self.vivo = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="p9-")))
        (self.vivo / "curadoria").mkdir()
        (self.vivo / "candidatas").mkdir()
        for mod, attr in ((FN, "FILA"), (F, "FILA")):
            self.addCleanup(setattr, mod, attr, getattr(mod, attr))
        FN.FILA = self.vivo / "candidatas" / "FONTES-CANDIDATAS.json"
        F.FILA = self.vivo / "curadoria" / "LIFECYCLE-QUEUE-V1.json"
        doc = FN.carregar()
        doc["CANDIDATAS"].append({"CANDIDATA_ID": "CAND-0001", "TIPO": "ORGANIZACAO", "PAIS": "IT",
                                  "NOME": "Condifesa Velha", "URL": "https://www.velha.example/", "ESTADO": "EM_ANALISE"})
        FN.gravar(doc)
        (self.vivo / "curadoria" / "DECISOES-SEMANTICAS-V1.json").write_text(
            json.dumps({"DECISOES": [], "TOTAL": 0}), encoding="utf-8")
        F.enfileirar("CAND-0001", F.QUALIFY, motivo="teste")
        t = F._ler()["TAREFAS"][0]
        F.bloquear(t["TASK_ID"], "territorio indeterminado pelo nome (Condifesa Velha) — SOURCE_ID fica UNKNOWN")

    def correr(self, decididas):
        return P9.passo9(self.vivo, decididas, FN, F, CPT, quem_viu="MICRO-PROVA-TESTE", onde_viu="teste")

    def test_nova_aprovada_e_registada_e_ganha_qualify(self):
        r = self.correr([_decidida()])
        self.assertEqual(1, len(r["REGISTADAS"]))
        cid = r["REGISTADAS"][0]["CANDIDATA_ID"]
        self.assertTrue(cid.startswith("CAND-"))
        self.assertEqual([cid], r["ENTRAM"])
        self.assertEqual([(r["QUALIFY"][0][0], cid, "NOVA")], r["QUALIFY"])
        ficha = next(c for c in FN.carregar()["CANDIDATAS"] if c["CANDIDATA_ID"] == cid)
        self.assertIn("ID_PROVISORIO=L2B-01", ficha["NOTA"])

    def test_a_decidir_nunca_e_registada(self):
        r = self.correr([_decidida(territorio=CPT.A_DECIDIR)])
        self.assertEqual([], r["REGISTADAS"])
        self.assertEqual(1, len(FN.carregar()["CANDIDATAS"]))

    def test_decisao_que_o_canal_recusa_nao_deixa_ficha(self):
        d = _decidida()
        d["PROVAS"] = d["PROVAS"][:2]                 # so 1 CONTEUDO: o canal recusa
        r = self.correr([d])
        self.assertEqual([], r["REGISTADAS"])
        self.assertEqual(1, len(FN.carregar()["CANDIDATAS"]))
        self.assertIn("CONTEUDO", r["FICAM"][0]["PORQUE"])

    def test_ja_registada_reabre_so_a_sua_tarefa(self):
        d = _decidida(cid="CAND-0001", url="https://www.velha.example/", nome="Condifesa Velha")
        r = self.correr([d])
        self.assertEqual(["CAND-0001"], r["ENTRAM"])
        self.assertEqual("REABERTA", r["QUALIFY"][0][2])
        self.assertEqual([], r["REGISTADAS"])


if __name__ == "__main__":
    unittest.main()
