# -*- coding: utf-8 -*-
"""OS DOIS MEDIDORES DA TRAVA TINHAM DE VER — e não viam.

Medido em 24/09/2026 contra a produção (`egresso-consenso-v1` @ `a310487f`):

1. `censo_das_estradas_it.py` só conhecia as 54 fontes do catálogo antigo
   (`candidatas/ITALY-SOURCE-MASTER-V1.json`). O livro que o coletor lê
   (`regras/italy_contracts_onboarded.json`) tem 193, e só 2 são comuns às
   duas listas. As fontes da 1.ª onda da Big Collection nem apareciam.

2. `censo_do_congelamento.py` gravava `FROZEN_AT_HEAD = HEAD de agora` e os
   blobs de agora — comparava a árvore consigo mesma e dava 0 diferenças
   sempre. A fotografia de referência é a da trava (`FREEZE_MANIFEST`).

    UM MEDIDOR QUE SÓ VÊ O QUE JÁ CONHECE NÃO MEDE A CASA.
    UM ALARME QUE SE COMPARA CONSIGO NUNCA TOCA.

Estes testes NÃO decidem que lista vale para o critério A, nem mudam a regra
da trava: exigem só que o medidor VEJA, e que declare o que viu.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "system-map", "scripts"))

import censo_das_estradas_it as estradas      # noqa: E402
import censo_do_congelamento as congelamento  # noqa: E402

LIVRO_DO_COLETOR = os.path.join(RAIZ, "regras", "italy_contracts_onboarded.json")
CATALOGO = os.path.join(RAIZ, "candidatas", "ITALY-SOURCE-MASTER-V1.json")
TRAVA = os.path.join(RAIZ, "docs", "operacao", "TRAVA-DA-INTELIGENCIA.json")


def _json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class OMedidorDasEstradasVeOLivroDoColetor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.u = estradas.universo_do_coletor()
        cls.ids = {r["SOURCE_ID"] for r in _json(LIVRO_DO_COLETOR)["FONTES"]}
        cls.cat = {s["SOURCE_ID"] for s in _json(CATALOGO)["sources"]}

    def test_mede_todas_as_fontes_do_livro_do_coletor(self):
        self.assertEqual(self.u["TOTAL"], len(self.ids))
        self.assertEqual({f["SOURCE_ID"] for f in self.u["POR_FONTE"]}, self.ids)

    def test_a_fonte_que_rendeu_na_big_collection_esta_la(self):
        """IT-T10-018 pousou 3 SIM na Sala real (BC5) e o censo não a via."""
        self.assertIn("IT-T10-018", {f["SOURCE_ID"] for f in self.u["POR_FONTE"]})

    def test_declara_a_sobreposicao_com_o_catalogo_da_trava(self):
        self.assertEqual(self.u["TAMBEM_NO_CATALOGO_DA_TRAVA"],
                         len(self.ids & self.cat))
        self.assertEqual(self.u["SO_NO_LIVRO_DO_COLETOR"], len(self.ids - self.cat))
        self.assertEqual(self.u["SO_NO_CATALOGO_DA_TRAVA"], len(self.cat - self.ids))

    def test_nao_inventa_classe_de_estrada(self):
        """O modelo não diz a que classe pertence cada STRATEGY. Atribuir uma
        seria fabricar o critério A — fica NAO_SEI até o dono do modelo decidir."""
        self.assertEqual({f["ROUTE_CLASS_ID"] for f in self.u["POR_FONTE"]}, {"NAO_SEI"})
        self.assertEqual(self.u["CRITERIO_A_NESTE_UNIVERSO"], "SEM_REGRA_DE_CORRESPONDENCIA")

    def test_o_estado_do_curador_vem_do_livro_e_conta_todas(self):
        self.assertEqual(sum(self.u["ESTADO_NO_CURADOR"].values()), self.u["TOTAL"])

    def test_o_veredito_declara_sobre_que_universo_fala(self):
        """A regra da trava não muda aqui: o veredito continua sobre o catálogo,
        e DIZ isso, até decisão escrita do dono."""
        rel, _ = estradas.relatorio()
        self.assertIn("ITALY-SOURCE-MASTER-V1", rel["UNIVERSO_DO_VEREDITO"]["CATALOGO"])
        self.assertEqual(rel["UNIVERSO_DO_VEREDITO"]["DECISAO"], "PENDENTE_DO_DONO")
        self.assertIn("UNIVERSO_DO_COLETOR", rel)


class OVigiaDoCongelamentoComparaComAFotografia(unittest.TestCase):

    MANIFESTO = {
        "FROZEN_AT_HEAD": "f" * 40,
        "FROZEN_INTELLIGENCE_ARTIFACTS": [
            {"PATH": "a.py", "SPECIES": "IMPLEMENTATION", "GIT_BLOB_SHA": "1" * 40},
            {"PATH": "b.js", "SPECIES": "PORTAL_UI", "GIT_BLOB_SHA": "2" * 40},
            {"PATH": "c.json", "SPECIES": "CONTRACT", "GIT_BLOB_SHA": "3" * 40},
        ],
    }

    def test_apanha_mudado_sumido_e_novo(self):
        agora = {"a.py": "1" * 40, "b.js": "9" * 40}          # c.json sumiu
        congelados_hoje = [{"PATH": "a.py", "SPECIES": "IMPLEMENTATION"},
                           {"PATH": "b.js", "SPECIES": "PORTAL_UI"},
                           {"PATH": "d.mjs", "SPECIES": "PORTAL_UI"}]
        r = congelamento.contra_a_fotografia(self.MANIFESTO, congelados_hoje,
                                             agora.get)
        self.assertEqual([m["PATH"] for m in r["MUDARAM"]], ["b.js"])
        self.assertEqual(r["SUMIRAM"], ["c.json"])
        self.assertEqual([n["PATH"] for n in r["NOVOS"]], ["d.mjs"])
        self.assertFalse(r["CONGELAMENTO_RESPEITADO"])
        self.assertEqual(r["FROZEN_AT_HEAD"], "f" * 40)

    def test_nada_mexido_da_respeitado(self):
        agora = {a["PATH"]: a["GIT_BLOB_SHA"]
                 for a in self.MANIFESTO["FROZEN_INTELLIGENCE_ARTIFACTS"]}
        hoje = [{"PATH": p, "SPECIES": "X"} for p in agora]
        r = congelamento.contra_a_fotografia(self.MANIFESTO, hoje, agora.get)
        self.assertTrue(r["CONGELAMENTO_RESPEITADO"])
        self.assertEqual((r["MUDARAM"], r["SUMIRAM"], r["NOVOS"]), ([], [], []))

    def test_o_censo_real_usa_a_fotografia_da_trava_e_nao_o_head(self):
        """O defeito: FROZEN_AT_HEAD era o HEAD do momento."""
        manifesto = _json(TRAVA)["FREEZE_MANIFEST"]
        c = congelamento.censo()
        self.assertEqual(c["FROZEN_AT_HEAD"], manifesto["FROZEN_AT_HEAD"])
        self.assertEqual(c["CONTRA_A_FOTOGRAFIA"]["FROZEN_AT_HEAD"],
                         manifesto["FROZEN_AT_HEAD"])
        self.assertIn("TRAVA-DA-INTELIGENCIA.json",
                      c["CONTRA_A_FOTOGRAFIA"]["REFERENCIA"])
        self.assertEqual(
            c["CONTRA_A_FOTOGRAFIA"]["ARTEFATOS_NA_FOTOGRAFIA"],
            len(manifesto["FROZEN_INTELLIGENCE_ARTIFACTS"]))


if __name__ == "__main__":
    unittest.main()
