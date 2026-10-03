#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IDEMPOTENCIA, PROVADA A ATACAR — os sete ataques do PASSO 5, pelo nome.

    1. mesma candidata duas vezes          -> uma identidade, uma tarefa activa
    2. URL que ja e contrato               -> NAO cria identidade nova
    3. URL invalida                        -> falha fechada (REJEITADA)
    4. mesma organizacao, canal diferente  -> pode ser unidade distinta (COL-LAW-034)
    5. worker morto a meio                 -> tarefa duravel, retomada (fila.recuperar_orfas)
    6. fila vazia                          -> IDLE, nao morte (supervisor.uma_volta_sup)
    7. supervisor reiniciado               -> recupera (estado persistido + orfas)

Os ataques 5-7 tem a prova principal em test_supervisor.py e test_lifecycle.py
e foram tambem corridos AO VIVO no PASSO 2 revisto (ver o relatorio). Aqui
ficam as versoes minimas, para que os sete estejam num so sitio pelo nome.

    E O CONTROLO POSITIVO DO ATLAS NAO ENFRAQUECE: @AgroNotizie tem de continuar
    a casar @agronotizietv. Um `==` entre URLs devolveu «0 de 98 ja existem» —
    um zero redondo e falso.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import emparelhar_com_atlas as EM   # noqa: E402
import fila as F                    # noqa: E402

ATLAS = [
    {"SOURCE_ID": "IT-T8-001", "URL": "https://www.youtube.com/@agronotizietv",
     "NAME": "Agronotizie (canal)", "OWNER": "", "NATIVE_ID": "UCUs2Mg7jvUTRt7_MSOFYM5Q",
     "TERRITORY": "T8", "VERDICT": ""},
    {"SOURCE_ID": "IT-T1-021", "URL": "https://agronotizie.imagelinenetwork.com/",
     "NAME": "Agronotizie (site)", "OWNER": "", "NATIVE_ID": "", "TERRITORY": "T1", "VERDICT": ""},
]


def cand(cid: str, url: str, nome: str = "x") -> dict:
    return {"CANDIDATE_ID": cid, "URL": url, "NOME": nome, "FAMILY": "HTML_SITE"}


class OsSeteAtaques(unittest.TestCase):

    def test_0_controlo_positivo_do_atlas_intacto(self):
        ok, novas, rej = EM.emparelhar([cand("C1", "https://www.youtube.com/@AgroNotizie")], ATLAS)
        self.assertEqual(1, len(ok))
        self.assertEqual("IT-T8-001", ok[0]["MATCHED_SOURCE_ID"])
        self.assertEqual("HANDLE_NORMALIZADO", ok[0]["VIA"])
        self.assertEqual(([], []), (novas, rej))

    def test_1_mesma_candidata_duas_vezes_e_uma_identidade_e_uma_tarefa(self):
        a = cand("C1", "https://www.exemplo-novo.it/")
        b = cand("C2", "https://exemplo-novo.it/")          # sem www, barra igual
        ok, novas, rej = EM.emparelhar([a, b], ATLAS)
        self.assertEqual([], ok)
        self.assertEqual(["C1"], [c["CANDIDATE_ID"] for c in novas])
        self.assertEqual(1, len(rej))
        self.assertTrue(rej[0]["PORQUE"].startswith("DUPLICADA_NA_CORRIDA"), rej[0])
        self.assertIn("C1", rej[0]["PORQUE"])
        # e na fila: enfileirar duas vezes o mesmo trabalho aberto e UMA tarefa
        with tempfile.TemporaryDirectory() as d:
            antes, F.FILA = F.FILA, Path(d) / "Q.json"
            try:
                t1 = F.enfileirar("IT-X-001", F.CANARY)
                t2 = F.enfileirar("IT-X-001", F.CANARY)
                self.assertEqual(t1["TASK_ID"], t2["TASK_ID"])
                self.assertEqual(1, F.metricas()["QUEUE_TOTAL"])
            finally:
                F.FILA = antes

    def test_2_url_que_ja_e_contrato_do_curator_nao_cria_identidade(self):
        contratos = [{"SOURCE_ID": "IT-T7-042", "URL": "https://www.consorziobalsamico.it/",
                      "NAME": "Balsamico", "OWNER": "", "NATIVE_ID": "", "TERRITORY": "T7",
                      "VERDICT": "CONTRATADA_PELO_CURATOR"}]
        fichas = ATLAS + contratos
        ok, novas, rej = EM.emparelhar(
            [cand("C9", "https://consorziobalsamico.it/news-blog/")], fichas)
        self.assertEqual(1, len(ok), "o dominio ja tem numero: nao nasce outro")
        self.assertEqual("IT-T7-042", ok[0]["MATCHED_SOURCE_ID"])
        self.assertEqual([], novas)

    def test_2b_as_fichas_dos_contratos_reais_entram_na_comparacao(self):
        """Contra a tabela real (so leitura): cada contrato do Curator vira ficha
        com URL e SOURCE_ID, e identidades_conhecidas nao repete SOURCE_ID."""
        fichas = EM.fichas_dos_contratos()
        self.assertGreaterEqual(len(fichas), 77)
        self.assertTrue(all(f["URL"].startswith("http") for f in fichas))
        todas = EM.identidades_conhecidas(contratos=fichas)
        ids = [f["SOURCE_ID"] for f in todas]
        self.assertEqual(len(ids), len(set(ids)), "SOURCE_ID repetido entre Atlas e contratos")
        # a Balsamico real, por outro endereco do mesmo dominio, casa
        ok, novas, _ = EM.emparelhar([cand("C9", "https://www.consorziobalsamico.it/x/")],
                                     todas)
        self.assertEqual("IT-T7-042", ok[0]["MATCHED_SOURCE_ID"])

    def test_3_url_invalida_falha_fechada(self):
        for url in ("nao e um endereco", "ftp://x.it/a", "https://semponto/", "", "http://a b.it/"):
            ok, novas, rej = EM.emparelhar([cand("C3", url)], ATLAS)
            self.assertEqual(([], []), (ok, novas), url)
            self.assertEqual(1, len(rej), url)
            self.assertTrue(rej[0]["PORQUE"].startswith("URL_INVALIDA"), url)

    def test_4_mesma_organizacao_canal_diferente_pode_ser_outra_unidade(self):
        """COL-LAW-034: canal != site. youtube.com/@x e x.it nao colapsam."""
        ok, novas, rej = EM.emparelhar(
            [cand("C4", "https://www.youtube.com/@cantinanova"),
             cand("C5", "https://www.cantinanova.it/")], ATLAS)
        self.assertEqual([], ok)
        self.assertEqual(["C4", "C5"], [c["CANDIDATE_ID"] for c in novas])
        self.assertEqual([], rej)
        # e o mesmo canal com sufixo de plataforma continua a ser UM
        ok, novas, rej = EM.emparelhar(
            [cand("C6", "https://www.youtube.com/@cantinanova"),
             cand("C7", "https://www.youtube.com/@CantinaNovaTV")], ATLAS)
        self.assertEqual(["C6"], [c["CANDIDATE_ID"] for c in novas])
        self.assertEqual(1, len(rej))

    def test_5_worker_morto_a_meio_a_tarefa_e_duravel_e_retomada(self):
        with tempfile.TemporaryDirectory() as d:
            antes, F.FILA = F.FILA, Path(d) / "Q.json"
            try:
                F.enfileirar("IT-X-002", F.CANARY)
                t = F.proxima()                       # IN_PROGRESS no disco
                self.assertEqual(F.IN_PROGRESS, json.loads(F.FILA.read_text())["TAREFAS"][0]["STATUS"])
                # o processo morre aqui. Quem reabrir ve IN_PROGRESS — a verdade.
                self.assertEqual([], F.recuperar_orfas())           # cedo demais: nao mexe
                agora = F.agora_utc() + timedelta(minutes=31)
                mexidas = F.recuperar_orfas(agora=agora)
                self.assertEqual([t["TASK_ID"]], [m["TASK_ID"] for m in mexidas])
                self.assertEqual(1, len(F.elegiveis(agora)))
            finally:
                F.FILA = antes

    def test_6_fila_vazia_e_IDLE_nao_morte(self):
        import supervisor as SUP
        with tempfile.TemporaryDirectory() as d:
            antes = (F.FILA, SUP.ESTADO, SUP.PARAR, SUP.DIARIO)
            F.FILA = Path(d) / "Q.json"
            SUP.ESTADO, SUP.PARAR, SUP.DIARIO = Path(d) / "S.json", Path(d) / "P.flag", Path(d) / "L.ndjson"
            self.addCleanup(setattr, SUP, "PULSO", SUP.PULSO)  # o pulso lido e batimento: nunca o real
            SUP.PULSO = Path(d) / "WORKER-HEARTBEAT.json"
            try:
                accao, estado, proc = SUP.uma_volta_sup({}, None)
                self.assertEqual("IDLE", accao)
                self.assertEqual("IDLE", estado["SUPERVISOR_STATE"])
                self.assertIsNone(proc)
            finally:
                F.FILA, SUP.ESTADO, SUP.PARAR, SUP.DIARIO = antes

    def test_7_supervisor_reiniciado_recupera_o_estado_persistido(self):
        import supervisor as SUP
        with tempfile.TemporaryDirectory() as d:
            antes = (F.FILA, SUP.ESTADO, SUP.PARAR, SUP.DIARIO)
            F.FILA = Path(d) / "Q.json"
            SUP.ESTADO, SUP.PARAR, SUP.DIARIO = Path(d) / "S.json", Path(d) / "P.flag", Path(d) / "L.ndjson"
            self.addCleanup(setattr, SUP, "PULSO", SUP.PULSO)  # o pulso lido e batimento: nunca o real
            SUP.PULSO = Path(d) / "WORKER-HEARTBEAT.json"
            try:
                SUP._gravar_estado({"SUPERVISOR_STATE": "STOPPED", "RESTARTS_TOTAL": 7,
                                    "CRASHES_SEM_PROGRESSO": []})
                estado = SUP._ler_estado()                 # o que um arranque novo le
                self.assertEqual(7, estado["RESTARTS_TOTAL"], "o contador sobrevive ao reinicio")
                accao, estado, _ = SUP.uma_volta_sup(estado, None)
                self.assertEqual("IDLE", accao)
                self.assertEqual(7, estado["RESTARTS_TOTAL"])
            finally:
                F.FILA, SUP.ESTADO, SUP.PARAR, SUP.DIARIO = antes


if __name__ == "__main__":
    unittest.main()
