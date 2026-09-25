#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D32 (7): a FILA-PRECISA-DE-IA (escrita pelo robo, derivada) e a porta de volta da bancada
(PROPOSTAS-DE-RECEITA-V1, escrita pelo agente; o robo so le no REPAIR_CONTRACT).
Tudo em pasta descartavel; nada sai a rede; RC.inferir nunca corre quando ha proposta."""
from __future__ import annotations

import json
import sys
import unittest
from datetime import timedelta
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import bancada_ia as BIA          # noqa: E402
import fila as F                  # noqa: E402
import gatilho_discovery as GD    # noqa: E402
import lifecycle as LC            # noqa: E402
import reparar_contrato as RC     # noqa: E402
import worker as W                # noqa: E402
from test_reparar_contrato import AGORA, _contrato, _Pasta   # noqa: E402

SHA = "a" * 64
T0 = "2026-09-24T10:00:00+00:00"
T1 = "2026-09-24T12:00:00+00:00"
T2 = "2026-09-24T14:00:00+00:00"


def proposta(sid="IT-T7-900", quando=T1, **kw):
    p = {"SOURCE_ID": sid, "INDEX_URL": "https://www.exemplo.it/news/",
         "LINK_PATTERN": r"^https://www\.exemplo\.it/news/\d+/[a-z-]+$",
         "PAGINAS_LIDAS": [{"URL": "https://www.exemplo.it/news/", "SHA256": SHA}],
         "PORQUE": "a listagem /news/ tem 12 materias com o mesmo esqueleto",
         "PROPOSTO_POR": "agente de teste", "PROPOSTO_EM": quando}
    p.update(kw)
    return p


def t(sid, estado, quando, razao="x", ref="EV-1"):
    return {"SOURCE_ID": sid, "NEW_STATE": estado, "OBSERVED_AT": quando, "REASON": razao, "EVIDENCE_REF": ref}


class APortaDasReceitas(unittest.TestCase):

    def test_sem_sha256_e_opiniao(self):
        with self.assertRaises(BIA.PropostaInvalida):
            BIA.validar_proposta(proposta(PAGINAS_LIDAS=[{"URL": "https://www.exemplo.it/news/"}]))

    def test_padrao_que_casa_a_entrada_e_recusado(self):
        with self.assertRaises(BIA.PropostaInvalida):
            BIA.validar_proposta(proposta(LINK_PATTERN=r"^https://www\.exemplo\.it/news/?.*$"))

    def test_prefixo_fora_da_casa_e_recusado(self):
        with self.assertRaises(BIA.PropostaInvalida):
            BIA.validar_proposta(proposta(sid="FR-T4-001"))

    def test_pendente_ate_o_contrato_a_aplicar(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            cam = Path(d) / "P.json"
            BIA.propor_receita(proposta(), cam)
            self.assertIsNotNone(BIA.proposta_pendente("IT-T7-900", {}, caminho=cam))
            ja = {"REPARO_DE_CONTRATO": {"APLICADO_EM": T2}}
            self.assertIsNone(BIA.proposta_pendente("IT-T7-900", ja, caminho=cam))
            # um reparo que correu depois dela consumiu-a (mesmo que a porta a tenha recusado)
            self.assertIsNone(BIA.proposta_pendente("IT-T7-900", {}, caminho=cam,
                                                    consumida_em=BIA._t(T2)))


class ARespostaSemReceita(unittest.TestCase):

    def test_sem_receita_tira_da_fila_e_o_reparo_ignora(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            cam = Path(d) / "P.json"
            with self.assertRaises(BIA.PropostaInvalida):
                BIA.responder_sem_receita({"SOURCE_ID": "IT-T7-001", "PORQUE": "x", "PROPOSTO_EM": T2,
                                           "PROPOSTO_POR": "a", "PAGINAS_LIDAS": []}, cam)
            r = BIA.responder_sem_receita({"SOURCE_ID": "IT-T7-001", "PORQUE": "1.o item com 590 letras",
                                           "PROPOSTO_EM": T2, "PROPOSTO_POR": "a",
                                           "PAGINAS_LIDAS": [{"URL": "https://x.it/", "SHA256": SHA}]}, cam)
            self.assertIsNone(BIA.proposta_pendente("IT-T7-001", {}, caminho=cam))
            f = BIA.construir(transicoes=[t("IT-T7-001", LC.CONTRACTED_CANARY_FAILED, T1, "CAPA_NAO_E_MATERIA: x")],
                              decisoes=[], propostas=[r], contratos={})
            self.assertEqual([], f["CASOS"])


class AFila(unittest.TestCase):

    def fila(self, transicoes, decisoes=(), propostas=()):
        return BIA.construir(transicoes=list(transicoes), decisoes=list(decisoes),
                             propostas=list(propostas), contratos={},
                             janela=lambda sid, c: sid.startswith("IT-T3-"))

    def test_quem_entra_e_com_que_pergunta(self):
        f = self.fila([t("CAND-0001", LC.SEMANTIC_REVIEW, T1),
                       t("CAND-0002", LC.SEMANTIC_REVIEW, T1),
                       t("IT-T7-001", LC.CONTRACTED_CANARY_FAILED, T1, "REPARO_RECUSADO: SEM_FAMILIA_DE_ITENS"),
                       t("IT-T3-001", LC.CONTRACTED_CANARY_FAILED, T1, "CAPA_NAO_E_MATERIA: listagem"),
                       t("IT-T7-002", LC.CONTRACTED_CANARY_FAILED, T1, "nenhum dos 12 enderecos da entrada"),
                       t("IT-T7-003", LC.CONTRACTED_CANARY_FAILED, T1,
                         "DUPLICADA_DE_IRMA: o item aberto e o mesmo que IT-T7-009"),
                       t("IT-T7-004", LC.READY_FOR_COLLECTION, T1)],
                      decisoes=[{"CANDIDATA_ID": "CAND-0002", "TERRITORIO": "NAO SEI",
                                 "CATEGORIA": "PROVA_INSUFICIENTE", "DECIDIDO_EM": T0}])
        casos = {c["CASO"]: c["PERGUNTA"] for c in f["CASOS"]}
        self.assertEqual({"CAND-0001": "TERRITORIO", "CAND-0002": "TERRITORIO",
                          "IT-T7-001": "RECEITA", "IT-T3-001": "RECEITA"}, casos)
        self.assertEqual("IT-T3-001", f["CASOS"][0]["CASO"], "a janela D29 vai a frente")

    def test_respondido_depois_da_ultima_prova_sai(self):
        f = self.fila([t("CAND-0002", LC.SEMANTIC_REVIEW, T1),
                       t("CAND-0003", LC.SEMANTIC_REVIEW, T1),
                       t("IT-T7-001", LC.CONTRACTED_CANARY_FAILED, T1, "REPARO_RECUSADO: X")],
                      decisoes=[{"CANDIDATA_ID": "CAND-0002", "TERRITORIO": "NAO SEI",
                                 "CATEGORIA": "PROVA_INSUFICIENTE", "DECIDIDO_EM": T2},
                                {"CANDIDATA_ID": "CAND-0003", "TERRITORIO": "NAO SEI",
                                 "CATEGORIA": "NAO_E_FONTE", "DECIDIDO_EM": T0}],
                      propostas=[proposta("IT-T7-001", T2)])
        self.assertEqual([], f["CASOS"])

    def test_a_hora_que_conta_e_a_da_prova_nao_a_da_linha(self):
        """Medido no vivo (CAND-0586): linha as 12:30 (importacao), prova as 04:40, NAO SEI as 05:52."""
        linha = t("CAND-0586", LC.SEMANTIC_REVIEW, "2026-09-23T12:30:25+00:00", ref="EV-CAND-0586-QUALIFY-1940")
        dec = {"CANDIDATA_ID": "CAND-0586", "TERRITORIO": "NAO SEI", "CATEGORIA": "PROVA_INSUFICIENTE",
               "DECIDIDO_EM": "2026-09-23T05:52:05+00:00"}
        f = BIA.construir(transicoes=[linha], decisoes=[dec], propostas=[], contratos={},
                          provas_em={"EV-CAND-0586-QUALIFY-1940": "2026-09-23T04:40:39+00:00"})
        self.assertEqual([], f["CASOS"])
        # prova nova depois da decisao: volta
        f = BIA.construir(transicoes=[linha], decisoes=[dec], propostas=[], contratos={},
                          provas_em={"EV-CAND-0586-QUALIFY-1940": "2026-09-23T09:00:00+00:00"})
        self.assertEqual(["CAND-0586"], [c["CASO"] for c in f["CASOS"]])

    def test_a_linha_que_espera_a_d2_volta_como_relevancia(self):
        f = self.fila([t("CAND-0057", LC.SEMANTIC_REVIEW, T0)],
                      decisoes=[{"CANDIDATA_ID": "CAND-0057", "TERRITORIO": "NAO SEI",
                                 "CATEGORIA": "PROVA_INSUFICIENTE", "DECIDIDO_EM": T2,
                                 "D2": {"UNIVERSE_MATCH": "NAO SEI", "SINTONIA_RELEVANT": "NAO SEI"}}])
        self.assertEqual([("CAND-0057", "RELEVANCIA_D2")], [(c["CASO"], c["PERGUNTA"]) for c in f["CASOS"]])

    def test_duas_decisoes_sao_conflito_e_voltam(self):
        d = {"CANDIDATA_ID": "CAND-0001", "TERRITORIO": "T3", "DECIDIDO_EM": T2}
        f = self.fila([t("CAND-0001", LC.SEMANTIC_REVIEW, T1)], decisoes=[d, dict(d, TERRITORIO="T4")])
        self.assertIn("conflito", f["CASOS"][0]["GATILHO"])


class AVoltaPeloRobo(_Pasta):

    def setUp(self):
        super().setUp()
        # a base (_Pasta) ja desvia livro, fila e provas; repetido aqui a vista da guarda de isolamento
        F.FILA = Path(self.tmp.name) / "QUEUE.json"
        self._p = BIA.PROPOSTAS
        BIA.PROPOSTAS = Path(self.tmp.name) / "PROPOSTAS.json"

    def tearDown(self):
        BIA.PROPOSTAS = self._p
        super().tearDown()

    def test_a_fila_e_escrita_ao_lado_do_livro_nunca_na_arvore_real(self):
        """Medido 25/09: a volta do ciclo, dentro de um teste, escrevia a fila em curadoria/."""
        real = BIA.FILA_IA
        existia = real.exists()
        antes = real.read_bytes() if existia else None
        LC.LIVRO = Path(self.tmp.name) / "LEDGER.json"
        LC.registar("CAND-9001", LC.SEMANTIC_REVIEW, "prova")
        BIA.construir_do_disco(escrever=True)
        self.assertTrue((Path(self.tmp.name) / real.name).exists())
        self.assertEqual(existia, real.exists())
        if existia:
            self.assertEqual(antes, real.read_bytes())

    def test_o_reparo_usa_a_proposta_e_nao_adivinha(self):
        c = _contrato()
        self._contratos(c)
        self._estado(c["SOURCE_ID"], LC.CONTRACTED_CANARY_FAILED)
        BIA.propor_receita(proposta(quando=W.agora()))
        F.enfileirar(c["SOURCE_ID"], F.REPAIR_CONTRACT, priority=50)
        with mock.patch.object(RC, "inferir", side_effect=AssertionError("nao devia adivinhar")):
            r = W.executar_uma(F.proxima(), W._contratos())
        self.assertEqual("OK", r["RESULTADO"], r)
        novo = json.loads(W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"][0]
        self.assertEqual(proposta()["LINK_PATTERN"], novo["ACQUISITION"]["LINK_PATTERN"])
        self.assertIn("PROPOSTA_DO_AGENTE", novo["REPARO_DE_CONTRATO"]["COMO"])
        # quem decide READY continua a ser o canario + regua: aqui so CANARY_PENDING
        self.assertEqual(LC.CANARY_PENDING, LC.estado_de(c["SOURCE_ID"]))
        # e aplicada, a proposta deixa de estar pendente
        self.assertIsNone(BIA.proposta_pendente(c["SOURCE_ID"], novo))

    def test_o_gatilho_devolve_ao_reparo_a_fonte_ja_reparada_com_proposta_nova(self):
        c = _contrato()
        self._contratos(c)
        self._estado(c["SOURCE_ID"], LC.CONTRACTED_CANARY_FAILED)
        velho = (AGORA - timedelta(days=3)).isoformat()
        reparo = {"SOURCE_ID": c["SOURCE_ID"], "TASK_TYPE": F.REPAIR_CONTRACT, "TASK_ID": "T1",
                  "STATUS": F.DONE, "UPDATED_AT": velho}
        cands = lambda: {(x["SOURCE_ID"], x["TASK_TYPE"]) for x in GD.candidatas_a_reparar(AGORA, tarefas=[reparo])}
        self.assertEqual(set(), cands(), "sem proposta, uma fonte ja reparada nao volta")
        BIA.propor_receita(proposta(quando=(AGORA - timedelta(days=1)).isoformat()))
        self.assertEqual({(c["SOURCE_ID"], F.REPAIR_CONTRACT)}, cands())
        # um reparo que correu depois da proposta consome-a: nao volta a cada volta
        reparo["UPDATED_AT"] = AGORA.isoformat()
        self.assertEqual(set(), cands())


if __name__ == "__main__":
    unittest.main()
