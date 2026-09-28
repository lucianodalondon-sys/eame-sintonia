# -*- coding: utf-8 -*-
"""SOCIAL-ATE-A-SALA · A — desfazer o POLICY_BLOCK (D15) das candidatas LinkedIn/Instagram pelas
decisoes do dono (D22/D23/D24/D106), SO pelas portas canonicas, e em livros de TESTE (temporarios).

    fila (fonte_nova.desbloquear_por_decisao) -> livro (lifecycle.registar) -> tarefa (fila.enfileirar QUALIFY)
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
sys.path.insert(0, str(RAIZ / "curadoria"))
import desbloquear_social as DS  # noqa: E402
import fila as F  # noqa: E402
import fonte_nova as FN  # noqa: E402
import lifecycle as LC  # noqa: E402

TERMOS_IG = {"URL": "https://help.instagram.com/581066165581870", "EM_VIGOR": "1 January 2025",
             "LIDO_EM": "2026-09-23T09:44:33Z", "TRECHO": "You can't ... in an automated way",
             "FICHEIRO": "candidatas/prova-termos/x.html", "SHA256": "e" * 64}


def ficha(cid, tipo, url, estado="POLICY_BLOCK"):
    return {"CANDIDATA_ID": cid, "TIPO": tipo, "TIPO_SIGNIFICA": "", "PAIS": "IT", "NOME": cid, "URL": url,
            "PARA_QUE_SERVE": "x", "QUEM_VIU": "x", "ONDE_VIU": "", "QUANDO": "2026-09-14", "NOTA": "",
            "ESTADO": estado, "SOURCE_ID": None, "MOTIVO_DA_RECUSA": None,
            "MOTIVO_DO_BLOQUEIO": "%s_POLICY: coleta automatizada proibida pelos TOS" % tipo,
            "EVIDENCIA_POLITICA": dict(TERMOS_IG) if estado == "POLICY_BLOCK" else None}


class _LivrosDeTeste(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        d = Path(self.t.name)
        self._antes = (FN.FILA, LC.LIVRO, F.FILA)
        FN.FILA, LC.LIVRO, F.FILA = d / "FONTES-CANDIDATAS.json", d / "LEDGER.json", d / "QUEUE.json"
        FN.FILA.write_text(json.dumps({"CANDIDATAS": [
            ficha("CAND-0087", "INSTAGRAM", "https://www.instagram.com/provinciatrento"),
            ficha("CAND-0118", "LINKEDIN", "https://www.linkedin.com/company/gruppocaviro"),
            ficha("CAND-1175", "LINKEDIN", "https://www.linkedin.com/in/alex-beneventi-0680b635", "CANDIDATA"),
            ficha("CAND-0500", "ORGANIZACAO", "https://www.crea.gov.it/")]}), encoding="utf-8")
        for cid in ("CAND-0087", "CAND-0118"):
            LC.registar(cid, LC.POLICY_BLOCK, "D15", evidence_ref="BRIDGE:x")

    def tearDown(self):
        FN.FILA, LC.LIVRO, F.FILA = self._antes
        self.t.cleanup()

    def cand(self, cid):
        return next(c for c in FN.carregar()["CANDIDATAS"] if c["CANDIDATA_ID"] == cid)


class APortaDaFila(_LivrosDeTeste):
    def test_1_desbloqueia_com_a_decisao_ao_lado_e_sem_apagar_o_bloqueio(self):
        c, feito = FN.desbloquear_por_decisao("CAND-0087", ["D22", "D106"], "DISALLOWED", {"TERMOS": TERMOS_IG}, "t")
        self.assertEqual(feito, "DESBLOQUEADA")
        c = self.cand("CAND-0087")
        self.assertEqual(c["ESTADO"], "CANDIDATA")
        self.assertEqual(c["DESBLOQUEIO"]["DECISOES"], ["D106", "D22"])
        self.assertEqual((c["DESBLOQUEIO"]["OWNER_AUTHORIZED"], c["DESBLOQUEIO"]["PLATFORM_POLICY_STATUS"]),
                         ("SIM", "DISALLOWED"))
        self.assertIn("TOS", c["MOTIVO_DO_BLOQUEIO"])
        self.assertEqual(c["EVIDENCIA_POLITICA"]["SHA256"], "e" * 64)
        self.assertEqual(c["HISTORICO_DE_ESTADO"][-1]["DE"], "POLICY_BLOCK")

    def test_2_decisao_que_nao_cobre_o_tipo_e_recusada(self):
        with self.assertRaises(ValueError):
            FN.desbloquear_por_decisao("CAND-0087", ["D23"], "DISALLOWED", {"T": 1}, "t")
        with self.assertRaises(ValueError):
            FN.desbloquear_por_decisao("CAND-0118", ["D22"], "DISALLOWED", {"T": 1}, "t")
        with self.assertRaises(ValueError):
            FN.desbloquear_por_decisao("CAND-0118", [], "DISALLOWED", {"T": 1}, "t")
        self.assertEqual(self.cand("CAND-0087")["ESTADO"], "POLICY_BLOCK")

    def test_3_sem_autorizacao_do_dono_ou_sem_politica_medida_nada_muda(self):
        with self.assertRaises(ValueError):
            FN.desbloquear_por_decisao("CAND-0087", ["D22"], "DISALLOWED", {"T": 1}, "t", owner_authorized="NAO")
        with self.assertRaises(ValueError):
            FN.desbloquear_por_decisao("CAND-0087", ["D22"], "", {"T": 1}, "t")
        with self.assertRaises(ValueError):
            FN.desbloquear_por_decisao("CAND-0087", ["D22"], "DISALLOWED", {}, "t")
        with self.assertRaises(ValueError):
            FN.desbloquear_por_decisao("CAND-0087", ["D22"], "DISALLOWED", {"T": 1}, " ")
        self.assertEqual(self.cand("CAND-0087")["ESTADO"], "POLICY_BLOCK")

    def test_4_idempotente_e_so_para_quem_esta_bloqueado(self):
        FN.desbloquear_por_decisao("CAND-0087", ["D22"], "DISALLOWED", {"T": 1}, "t")
        self.assertEqual(FN.desbloquear_por_decisao("CAND-0087", ["D22"], "DISALLOWED", {"T": 1}, "t")[1],
                         "JA_DESBLOQUEADA")
        self.assertEqual(len(self.cand("CAND-0087")["HISTORICO_DE_ESTADO"]), 1)
        self.assertTrue(FN.desbloquear_por_decisao("CAND-1175", ["D24"], "DISALLOWED", {"T": 1}, "t")[1]
                        .startswith("NAO_ESTA_EM_POLICY_BLOCK"))
        self.assertIsNone(FN.desbloquear_por_decisao("CAND-9999", ["D22"], "DISALLOWED", {"T": 1}, "t")[0])

    def test_5_uma_organizacao_comum_nao_se_desbloqueia_por_decisao_social(self):
        doc = FN.carregar()
        next(c for c in doc["CANDIDATAS"] if c["CANDIDATA_ID"] == "CAND-0500")["ESTADO"] = "POLICY_BLOCK"
        FN.gravar(doc)
        with self.assertRaises(ValueError):
            FN.desbloquear_por_decisao("CAND-0500", ["D23"], "DISALLOWED", {"T": 1}, "t")


class OCaminhoAteAoQualify(_LivrosDeTeste):
    def test_6_cada_candidata_leva_as_decisoes_que_a_cobrem(self):
        self.assertEqual(DS.decisoes_de({"TIPO": "INSTAGRAM", "URL": "x"}), ["D22", "D106"])
        self.assertEqual(DS.decisoes_de({"TIPO": "LINKEDIN", "URL": "https://www.linkedin.com/company/x"}),
                         ["D23", "D106"])
        self.assertEqual(DS.decisoes_de({"TIPO": "LINKEDIN", "URL": "https://www.linkedin.com/in/x"}),
                         ["D24", "D106"])

    def test_7_a_politica_e_a_medida_na_ficha_e_o_robots_do_linkedin(self):
        st, prova = DS.politica_medida(self.cand("CAND-0118"))
        self.assertEqual(st, "DISALLOWED")
        self.assertEqual(prova["ROBOTS"]["ROBOTS_STATUS"], "DISALLOW_ALL")
        self.assertEqual(prova["TERMOS"]["SHA256"], "e" * 64)
        self.assertEqual(DS.politica_medida({"TIPO": "INSTAGRAM"}), ("NAO SEI", {}))

    def test_8_aplicar_passa_pelas_tres_portas(self):
        feitas = DS.aplicar(DS.bloqueadas())
        self.assertEqual(sorted(f["CANDIDATA_ID"] for f in feitas), ["CAND-0087", "CAND-0118"])
        for cid in ("CAND-0087", "CAND-0118"):
            self.assertEqual(self.cand(cid)["ESTADO"], "CANDIDATA")
            self.assertEqual(LC.estado_de(cid), LC.DISCOVERED)
            t = [x for x in F._ler()["TAREFAS"] if x["SOURCE_ID"] == cid]
            self.assertEqual([x["TASK_TYPE"] for x in t], [F.QUALIFY])
        # append-only: a linha do POLICY_BLOCK continua no livro
        self.assertEqual([x["NEW_STATE"] for x in LC.historico("CAND-0087")] if hasattr(LC, "historico") else
                         [x["NEW_STATE"] for x in LC._ler_bruto()["TRANSICOES"] if x["SOURCE_ID"] == "CAND-0087"],
                         [LC.POLICY_BLOCK, LC.DISCOVERED])

    def test_9_sem_politica_medida_a_candidata_para_e_diz_porque(self):
        doc = FN.carregar()
        next(c for c in doc["CANDIDATAS"] if c["CANDIDATA_ID"] == "CAND-0087")["EVIDENCIA_POLITICA"] = None
        FN.gravar(doc)
        f = {x["CANDIDATA_ID"]: x for x in DS.aplicar(DS.bloqueadas())}
        self.assertEqual(f["CAND-0087"]["FEITO"], "PARADA")
        self.assertEqual(self.cand("CAND-0087")["ESTADO"], "POLICY_BLOCK")
        self.assertEqual(LC.estado_de("CAND-0087"), LC.POLICY_BLOCK)

    def test_10_tambem_candidatas_so_acrescenta_o_QUALIFY(self):
        self.assertEqual({c["CANDIDATA_ID"] for c in DS.bloqueadas(True)}, {"CAND-0087", "CAND-0118", "CAND-1175"})
        DS.aplicar([c for c in DS.bloqueadas(True) if c["CANDIDATA_ID"] == "CAND-1175"])
        self.assertEqual(self.cand("CAND-1175")["ESTADO"], "CANDIDATA")
        self.assertNotIn("DESBLOQUEIO", self.cand("CAND-1175"))
        self.assertEqual([x["TASK_TYPE"] for x in F._ler()["TAREFAS"] if x["SOURCE_ID"] == "CAND-1175"], [F.QUALIFY])

    def test_11_sem_copia_nem_vivo_declarado_recusa(self):
        self.assertEqual(DS.main(["--aplicar"]), 2)
        self.assertEqual(self.cand("CAND-0087")["ESTADO"], "POLICY_BLOCK")
        self.assertEqual(DS.main(["--ensaio"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
