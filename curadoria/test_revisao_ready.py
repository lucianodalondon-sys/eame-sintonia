# -*- coding: utf-8 -*-
"""R1 · a revisao das READY do reparo: o motivo da leitura vira estado, e so as
limpas saem READY. Sem rede; livro, fila, contratos e revisao em pastas temporarias."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import fila as F                 # noqa: E402
import lifecycle as LC           # noqa: E402
import ready_split as RS         # noqa: E402
import revisao_ready as REV      # noqa: E402
import worker as W               # noqa: E402

IDX, PAD = "https://www.exemplo.it/", r"^https?://(www\.)?exemplo\.it/news/\d+/?$"


def _contrato(sid, reparado=True, padrao=PAD):
    c = {"SOURCE_ID": sid, "OUTPUT_TYPE": "HTML",
         "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": IDX, "LINK_PATTERN": padrao}}
    if reparado:
        c["REPARO_DE_CONTRATO"] = {"DECISAO": "R1"}
    return c


def _entrada(sid, classe, motivo="m"):
    return {"SOURCE_ID": sid, "CLASSE": classe, "MOTIVO": motivo, "INDEX_URL": IDX, "LINK_PATTERN": PAD}


class _Pasta(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (REV.ARQUIVO, LC.LIVRO, F.FILA, W.EVIDENCIA)
        REV.ARQUIVO = d / "revisao.json"
        LC.LIVRO = d / "livro.json"
        F.FILA = d / "fila.json"
        W.EVIDENCIA = d / "evidencia.json"

    def tearDown(self):
        REV.ARQUIVO, LC.LIVRO, F.FILA, W.EVIDENCIA = self._antes
        self.tmp.cleanup()

    def _revisao(self, *entradas):
        REV.ARQUIVO.write_text(json.dumps({"FONTES": list(entradas)}), encoding="utf-8")


class Decisao(_Pasta):
    def test_suspeitas_retem_com_o_motivo(self):
        for classe in REV.BLOQUEIAM:
            self._revisao(_entrada("IT-T1-001", classe, "lavora con noi"))
            d = REV.decisao("IT-T1-001", _contrato("IT-T1-001"))
            self.assertEqual(("RETER", "CONTRACTED_CANARY_FAILED"), (d["ACAO"], d["ESTADO"]), classe)
            self.assertIn("REVISAO_R1: %s: lavora con noi" % classe, d["RAZAO"])

    def test_suspeita_retem_mesmo_sem_reparo_e_com_outro_contrato(self):
        self._revisao(_entrada("IT-T1-001", "LISTA_COMO_ITEM"))
        d = REV.decisao("IT-T1-001", _contrato("IT-T1-001", reparado=False, padrao="^outro$"))
        self.assertEqual("RETER", d["ACAO"])
        self.assertIn("mudou desde a leitura", d["RAZAO"])

    def test_tema_vai_para_semantic_review(self):
        self._revisao(_entrada("IT-T1-001", "TEMA_A_CONFIRMAR", "educacao"))
        d = REV.decisao("IT-T1-001", _contrato("IT-T1-001"))
        self.assertEqual(("RETER", "SEMANTIC_REVIEW"), (d["ACAO"], d["ESTADO"]))
        self.assertIn("TEMA_A_CONFIRMAR (D2", d["RAZAO"])

    def test_acesso_parcial_promove_com_nota(self):
        self._revisao(_entrada("IT-T1-001", "ACESSO_PARCIAL", "so o inicio aberto"))
        d = REV.decisao("IT-T1-001", _contrato("IT-T1-001"))
        self.assertEqual("PROMOVER_COM_NOTA", d["ACAO"])
        self.assertIn("ACESSO_PARCIAL", d["NOTA"])

    def test_limpa_com_o_mesmo_contrato_nao_diz_nada(self):
        self._revisao(_entrada("IT-T1-001", "LIMPA"))
        self.assertIsNone(REV.decisao("IT-T1-001", _contrato("IT-T1-001")))

    def test_reparada_sem_leitura_fica_pendente(self):
        self._revisao()
        d = REV.decisao("IT-T1-002", _contrato("IT-T1-002"))
        self.assertEqual(("RETER", "CONTRACTED_CANARY_FAILED"), (d["ACAO"], d["ESTADO"]))
        self.assertTrue(d["RAZAO"].startswith("REVISAO_PENDENTE"))

    def test_limpa_mas_contrato_mudou_fica_pendente(self):
        self._revisao(_entrada("IT-T1-001", "LIMPA"))
        d = REV.decisao("IT-T1-001", _contrato("IT-T1-001", padrao="^outro$"))
        self.assertEqual("RETER", d["ACAO"])
        self.assertIn("reler", d["RAZAO"])

    def test_nao_reparada_e_fora_da_revisao_nao_muda_nada(self):
        self._revisao()
        self.assertIsNone(REV.decisao("IT-T1-003", _contrato("IT-T1-003", reparado=False)))

    def test_sem_ficheiro_nao_rebenta(self):
        self.assertIsNone(REV.decisao("IT-T1-003", _contrato("IT-T1-003", reparado=False)))
        self.assertEqual("RETER", REV.decisao("IT-T1-003", _contrato("IT-T1-003"))["ACAO"])


class NoWorker(_Pasta):
    """O caminho da promocao do worker, com o canario e a regua simulados."""

    def _promover(self, sid, contrato):
        LC.registar(sid, LC.CANARY_PENDING, "preparo", evidence_ref="EV-T")
        F.enfileirar(sid, F.CANARY, priority=60)
        ok = ("OK", {"PASS": True, "DETAIL_GATE_PASSED": True})
        with mock.patch.dict(W.ETAPAS, {F.CANARY: lambda s, c: ok}), \
                mock.patch.object(RS, "passos_da_promocao",
                                  return_value={"REGUA": RS.REGUA_CURRENT, "PORQUE": "4 passos"}):
            return W.executar_uma(F.proxima(), {sid: contrato})

    def test_suspeita_nao_sai_ready_e_o_motivo_fica_no_livro(self):
        self._revisao(_entrada("IT-T1-001", "SERVICO_OU_INSTITUCIONAL", "Area Personale Tributi"))
        r = self._promover("IT-T1-001", _contrato("IT-T1-001"))
        self.assertEqual("PASS_RETIDO_PELA_REVISAO", r["RESULTADO"])
        ult = LC._ler_bruto()["TRANSICOES"][-1]
        self.assertEqual(LC.CONTRACTED_CANARY_FAILED, ult["NEW_STATE"])
        self.assertIn("Area Personale Tributi", ult["REASON"])

    def test_tema_fica_em_semantic_review(self):
        self._revisao(_entrada("IT-T1-001", "TEMA_A_CONFIRMAR"))
        self._promover("IT-T1-001", _contrato("IT-T1-001"))
        self.assertEqual(LC.SEMANTIC_REVIEW, LC.estado_de("IT-T1-001"))

    def test_limpa_sai_ready(self):
        self._revisao(_entrada("IT-T1-001", "LIMPA"))
        self._promover("IT-T1-001", _contrato("IT-T1-001"))
        self.assertEqual(LC.READY_FOR_COLLECTION, LC.estado_de("IT-T1-001"))

    def test_acesso_parcial_sai_ready_com_a_nota_visivel(self):
        self._revisao(_entrada("IT-T1-001", "ACESSO_PARCIAL", "so o inicio aberto (assinantes)"))
        self._promover("IT-T1-001", _contrato("IT-T1-001"))
        ult = LC._ler_bruto()["TRANSICOES"][-1]
        self.assertEqual(LC.READY_FOR_COLLECTION, ult["NEW_STATE"])
        self.assertIn("ACESSO_PARCIAL", ult["REASON"])

    def test_reparada_sem_leitura_nao_sai_ready(self):
        self._revisao()
        self._promover("IT-T1-009", _contrato("IT-T1-009"))
        self.assertEqual(LC.CONTRACTED_CANARY_FAILED, LC.estado_de("IT-T1-009"))

    def test_contrato_antigo_fora_da_revisao_promove_como_antes(self):
        self._revisao()
        self._promover("IT-T1-010", _contrato("IT-T1-010", reparado=False))
        self.assertEqual(LC.READY_FOR_COLLECTION, LC.estado_de("IT-T1-010"))


class Revisao15(_Pasta):
    """REVISAO-15: classes novas e o re-medir UMA vez depois de uma leitura nova."""

    def setUp(self):
        super().setUp()
        import gatilho_discovery as GD
        self.GD = GD
        self._c = GD.CONTRATOS
        GD.CONTRATOS = Path(self.tmp.name) / "contratos.json"
        GD.CONTRATOS.write_text(json.dumps({"FONTES": [_contrato("IT-T3-030")]}), encoding="utf-8")

    def tearDown(self):
        self.GD.CONTRATOS = self._c
        super().tearDown()

    def test_alvo_errado_e_nao_sei_retem_com_motivo(self):
        for classe in ("ALVO_ERRADO", "NAO_SEI"):
            self._revisao(_entrada("IT-T1-001", classe, "besouro japones"))
            d = REV.decisao("IT-T1-001", _contrato("IT-T1-001"))
            self.assertEqual(("RETER", "CONTRACTED_CANARY_FAILED"), (d["ACAO"], d["ESTADO"]), classe)
            self.assertIn("REVISAO_R1: %s: besouro japones" % classe, d["RAZAO"])

    def _cands(self, tarefas):
        from datetime import datetime, timezone
        agora = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)
        return [(c["SOURCE_ID"], c["TASK_TYPE"]) for c in self.GD.candidatas_a_reparar(
            agora, estados={"IT-T3-030": LC.CONTRACTED_CANARY_FAILED}, tarefas=tarefas)]

    def _ja_reparada(self, canario_em):
        return [{"SOURCE_ID": "IT-T3-030", "TASK_TYPE": F.REPAIR_CONTRACT, "TASK_ID": "T1", "STATUS": F.DONE,
                 "UPDATED_AT": "2026-09-25T06:00:00+00:00"},
                {"SOURCE_ID": "IT-T3-030", "TASK_TYPE": F.CANARY, "TASK_ID": "T2", "STATUS": F.DONE,
                 "UPDATED_AT": canario_em}]

    def test_leitura_nova_re_mede_uma_vez(self):
        self._revisao(dict(_entrada("IT-T3-030", "LIMPA"), REVISTO_EM="2026-09-25T12:00:00+00:00"))
        self.assertEqual([("IT-T3-030", F.VALIDATE_ROUTE)], self._cands(self._ja_reparada("2026-09-25T07:00:00+00:00")))
        # depois de re-medida (canario mais novo que a leitura), nao volta
        self.assertEqual([], self._cands(self._ja_reparada("2026-09-25T13:00:00+00:00")))

    def test_leitura_sem_data_nao_re_mede(self):
        self._revisao(_entrada("IT-T3-030", "LIMPA"))
        self.assertEqual([], self._cands(self._ja_reparada("2026-09-25T07:00:00+00:00")))

    def test_suspeita_nova_tambem_re_mede_para_escrever_o_motivo(self):
        self._revisao(dict(_entrada("IT-T3-030", "ALVO_ERRADO"), REVISTO_EM="2026-09-25T12:00:00+00:00"))
        self.assertEqual([("IT-T3-030", F.VALIDATE_ROUTE)], self._cands(self._ja_reparada("2026-09-25T07:00:00+00:00")))

    def test_retirada_por_decisao_nao_re_mede_nem_com_leitura_nova(self):
        # PACOTE-ONDA3: a D52 (retirada) vem ANTES da REVISAO-15 no gatilho
        self._revisao(dict(_entrada("IT-T3-030", "LIMPA"), REVISTO_EM="2026-09-25T12:00:00+00:00"))
        self.GD.CONTRATOS.write_text(json.dumps({"FONTES": [dict(
            _contrato("IT-T3-030"), ESTADO_CATALOGO="RETIRADA_POR_DECISAO")]}), encoding="utf-8")
        self.assertEqual([], self._cands(self._ja_reparada("2026-09-25T07:00:00+00:00")))


if __name__ == "__main__":
    unittest.main()
