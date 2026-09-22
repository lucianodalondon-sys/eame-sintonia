#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A RECONCILIACAO DOS TRES LIVROS, ATACADA — cada lei tem um teste que a tenta partir.

Livros sinteticos, sem git, sem rede. O livro REAL nunca e tocado: LC.LIVRO e
R.SAIDA apontam para uma pasta descartavel (molde: test_ready_split.py).

Os seis ataques do RED TEAM da missao (G-RT) estao aqui por numero:
    RT1  apagar POLICY_BLOCK de um dos lados     -> preserva pela evidencia
    RT2  inserir READY sem canario               -> reprova
    RT3  homepage como item de detalhe           -> reprova (fica LEGACY)
    RT4  mesma SOURCE_ID em dois estados         -> resolve pela prova, nao pela ordem
    RT5  UNKNOWN a tentar virar READY            -> reprova
    RT6  neutralizar dedup por SOURCE_ID         -> reprova (uma identidade)
"""
from __future__ import annotations

import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import lifecycle as LC              # noqa: E402
import reconciliar_livros as R      # noqa: E402

T0 = "2026-09-20T20:00:00+00:00"
T1 = "2026-09-20T23:00:00+00:00"
T2 = "2026-09-21T03:00:00+00:00"
T3 = "2026-09-21T04:00:00+00:00"


def linha(sid, de, para, quando, ref=None, reason="x", owner=LC.OWNER_CURATOR):
    return {"SOURCE_ID": sid, "PREVIOUS_STATE": de, "NEW_STATE": para, "REASON": reason,
            "EVIDENCE_REF": ref, "OBSERVED_AT": quando, "OWNER": owner, "VERSION": LC.CONTRATO}


def livro(*linhas):
    return {"DATASET": "LIFECYCLE-LEDGER-V1", "CONTRATO": LC.CONTRATO, "LEI": "t", "TRANSICOES": list(linhas)}


def contrato(sid, index="https://ex.it/news/", integrado_em=None):
    c = {"SOURCE_ID": sid, "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": index,
                                           "MAX_TARGETS": 10}, "SOURCE_CONTRACT_HASH": "h" + sid[-3:]}
    if integrado_em:
        c["ROUTE_PROVENANCE"] = {"INTEGRADO_EM": integrado_em}
    return c


def prova_canario(ref, sid, item="https://ex.it/news/mosca-olivo-calo-termico-2026/", alvos=12,
                  kind="CONTENT", capa="MATERIA_PROVAVEL", par=3000, gate=True, http=200):
    return {"EVIDENCE_REF": ref, "SOURCE_ID": sid, "ETAPA": "CANARY", "OBSERVED_AT": T2,
            "DADOS": {"PASS": True, "CLASSE": "OK", "DETAIL_GATE_PASSED": gate,
                      "ALVOS_DESCOBERTOS": alvos, "DETAIL_ENUMERATED": alvos,
                      "ITEM_ABERTO": {"URL": item, "HTTP": http, "HTML_KIND": kind, "CAPA_OU_MATERIA": capa,
                                      "PARAGRAPH_CHARACTERS": par, "NON_WHITESPACE_CHARACTERS": par * 2}}}


def estado_b(sid, classe="SUCCESS", obs=1, strategy="HTML_LINK_DISCOVERY", adapter=None, origem="TABELA_ONBOARDED"):
    return {"SOURCE_ID": sid, "STRATEGY": strategy, "ADAPTER_ID": adapter, "ORIGEM_DO_CONTRATO": origem,
            "ROUTE": "https://ex.it/", "BIG_COLLECTION": ({"RUN_ID": "RUN-" + sid, "CLASSE": classe,
                                                         "OBSERVACOES": obs} if classe else None)}


def classif(sid, alvo, classe="LISTAGEM_DE_NOTICIAS", criterio="C3_LISTAGEM_VISTA_NA_EVIDENCIA"):
    return {"SOURCE_ID": sid, "CLASSIFICACAO": classe, "CRITERIO": criterio, "BANDEIRAS": [alvo, "ROTA_CAPA"]}


def candidata(cid, tipo, host):
    return {"CANDIDATA_ID": cid, "TIPO": tipo, "URL": "https://www.%s/x/y" % host, "ESTADO": "EM_ANALISE"}


def ctx(**kw):
    base = {"COMMITS": {"A": "aaaaaaaa", "B": "bbbbbbbb", "B2": "cccccccc", "C": "dddddddd"},
            "A": livro(), "B": livro(), "B2": livro(), "C": livro(),
            "EVIDENCIA_A": {}, "CONTRATOS_A": {}, "CONTRATOS_B": {}, "LISTAGENS_A": {},
            "EVIDENCIA_C": {}, "CONTRATOS_C": {},
            "ESTADO_B": {}, "CLASSIF_B": {}, "PROVA_B": {}, "PASSO2_TOCADAS": {}, "PASSO2_INTOCADAS": {},
            "PORTA": {}, "ALIAS": {}}
    base.update(kw)
    return base


def por_id(doc):
    return {l["SOURCE_ID"]: l for l in doc["LINHAS"]}


class OsBloqueiosPreservamSe(unittest.TestCase):

    def test_rt1_policy_block_so_num_livro_e_preservado_pela_porta(self):
        c = ctx(B2=livro(linha("CAND-0001", None, LC.POLICY_BLOCK, T1, "BRIDGE:candidatas/FONTES-CANDIDATAS.json")),
                PORTA={"CAND-0001": candidata("CAND-0001", "LINKEDIN", "linkedin.com")})
        d = R.censo(c)
        self.assertEqual(por_id(d)["CAND-0001"]["FINAL_STATE"], R.POLICY_BLOCK)
        self.assertEqual(d["BLOQUEIOS"]["POLICY_BLOCK_IMPORTED"], 1)
        self.assertEqual(d["BLOQUEIOS"]["BLOCKS_REJECTED_AS_STALE"], [])

    def test_rt1_apagar_o_bloqueio_do_outro_lado_nao_o_revoga(self):
        """O bloqueio esta em A; B2 (o livro que o criou) foi «limpo». Continua."""
        c = ctx(A=livro(linha("CAND-0001", None, LC.POLICY_BLOCK, T1, "BRIDGE:candidatas/FONTES-CANDIDATAS.json")),
                B2=livro(),
                PORTA={"CAND-0001": candidata("CAND-0001", "INSTAGRAM", "instagram.com")})
        self.assertEqual(por_id(R.censo(c))["CAND-0001"]["FINAL_STATE"], R.POLICY_BLOCK)

    def test_rt1_bloqueio_cuja_porta_contradiz_e_rejeitado_como_stale(self):
        c = ctx(B2=livro(linha("CAND-0002", None, LC.POLICY_BLOCK, T1, "BRIDGE:x")),
                PORTA={"CAND-0002": candidata("CAND-0002", "IMPRENSA", "giornale.it")})
        d = R.censo(c)
        self.assertNotEqual(por_id(d)["CAND-0002"]["FINAL_STATE"], R.POLICY_BLOCK)
        self.assertEqual(len(d["BLOQUEIOS"]["BLOCKS_REJECTED_AS_STALE"]), 1)

    def test_capability_block_nao_vira_ready_por_omissao_no_outro_livro(self):
        """A bloqueia com prova; B nao conhece o bloqueio e diz READY com BCR. Lei 3."""
        sid = "IT-T7-029"
        c = ctx(A=livro(linha(sid, None, LC.CONTRACT_PENDING, T0), linha(sid, LC.CONTRACT_PENDING, LC.CAPABILITY_BLOCK, T1, "CARACT:x")),
                B=livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "BCR-x")),
                ESTADO_B={sid: estado_b(sid)}, CLASSIF_B={sid: classif(sid, R.BCR_MATERIA)})
        self.assertEqual(por_id(R.censo(c))[sid]["FINAL_STATE"], R.CAPABILITY_BLOCK)

    def test_capability_block_cede_a_prova_posterior_na_propria_historia(self):
        """B2 tem o bloqueio; A tem a MESMA linha e continua com canario provado. Nao e omissao."""
        sid = "IT-T5-041"
        bloco = linha(sid, LC.CONTRACT_PENDING, LC.CAPABILITY_BLOCK, T1, "CARACT:x")
        c = ctx(B2=livro(linha(sid, None, LC.CONTRACT_PENDING, T0), bloco),
                A=livro(linha(sid, None, LC.CONTRACT_PENDING, T0), bloco,
                        linha(sid, LC.CAPABILITY_BLOCK, LC.CANARY_PENDING, T2, "LISTAGENS-PROVADAS-V1.json"),
                        linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T3, "EV-1")),
                EVIDENCIA_A={"EV-1": prova_canario("EV-1", sid)}, CONTRATOS_A={sid: contrato(sid)})
        d = R.censo(c)
        self.assertEqual(por_id(d)[sid]["FINAL_STATE"], R.READY_CURRENT)
        self.assertEqual(len(d["BLOQUEIOS"]["BLOCKS_SUPERSEDED_BY_LATER_EVIDENCE"]), 1)


class ReadyExigeProva(unittest.TestCase):

    def test_rt2_ready_sem_evidencia_nao_e_ready(self):
        sid = "IT-T1-050"
        c = ctx(B=livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, None)),
                ESTADO_B={sid: estado_b(sid)}, CLASSIF_B={sid: classif(sid, R.BCR_MATERIA)})
        l = por_id(R.censo(c))[sid]
        self.assertEqual(l["FINAL_STATE"], R.UNKNOWN, l["FINAL_REASON"])

    def test_rt2_ready_com_referencia_mas_sem_corrida_real_conferivel_e_unknown(self):
        sid = "IT-T1-051"
        c = ctx(B=livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "BCR-inventada")),
                ESTADO_B={sid: estado_b(sid, classe=None)})
        self.assertEqual(por_id(R.censo(c))[sid]["FINAL_STATE"], R.UNKNOWN)

    def test_rt2_cadeia_ilegal_nao_e_importada_para_o_livro(self):
        """B salta de nada para READY. O plano detecta e a fonte fica de fora, nomeada."""
        sid = "IT-T1-052"
        c = ctx(B=livro(linha(sid, None, LC.READY_FOR_COLLECTION, T2, "BCR-x")),
                ESTADO_B={sid: estado_b(sid)}, CLASSIF_B={sid: classif(sid, R.BCR_MATERIA)})
        d = R.censo(c)
        faltas = R.verificar_plano(R.plano(d, c), c)
        self.assertTrue(faltas and sid in faltas[0], faltas)

    def test_rt3_homepage_como_item_de_detalhe_fica_legacy(self):
        sid = "IT-T7-017"
        for item in ("https://ex.it/", "https://ex.it", "https://ex.it/news/", "https://ex.it/news"):
            c = ctx(A=livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "EV-1")),
                    EVIDENCIA_A={"EV-1": prova_canario("EV-1", sid, item=item)}, CONTRATOS_A={sid: contrato(sid)})
            l = por_id(R.censo(c))[sid]
            self.assertEqual(l["FINAL_STATE"], R.READY_LEGACY, (item, l["FINAL_REASON"]))
            self.assertFalse(l["DETAIL_PROOF_A"]["ITEM_ABERTO"])

    def test_os_quatro_passos_decidem_current(self):
        sid = "IT-T7-017"
        casos = {
            "materia": (dict(), R.READY_CURRENT),
            "corpo NAO_SEI": (dict(kind="MIXED", capa="NAO_SEI"), R.READY_LEGACY),
            "capa": (dict(kind="NAV", capa="CAPA_PROVAVEL", gate=False), R.READY_LEGACY),
            "uma so ligacao": (dict(alvos=1), R.READY_LEGACY),
            "item 404": (dict(http=404), R.READY_LEGACY),
            "corpo curto": (dict(par=200), R.READY_LEGACY),
        }
        for nome, (kw, esperado) in casos.items():
            c = ctx(A=livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "EV-1")),
                    EVIDENCIA_A={"EV-1": prova_canario("EV-1", sid, **kw)}, CONTRATOS_A={sid: contrato(sid)})
            self.assertEqual(por_id(R.censo(c))[sid]["FINAL_STATE"], esperado, nome)

    def test_contrato_alterado_depois_da_promocao_nao_e_current(self):
        sid = "IT-T7-017"
        c = ctx(A=livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "EV-1")),
                EVIDENCIA_A={"EV-1": prova_canario("EV-1", sid)}, CONTRATOS_A={sid: contrato(sid, integrado_em=T3)})
        l = por_id(R.censo(c))[sid]
        self.assertEqual(l["FINAL_STATE"], R.READY_LEGACY)
        self.assertFalse(l["DETAIL_PROOF_A"]["CONTRATO_ATUAL"])

    def test_rt5_unknown_nao_vira_ready_sem_prova(self):
        sid = "IT-T1-060"
        A = livro(linha(sid, None, LC.CANARY_PENDING, T0), linha(sid, LC.CANARY_PENDING, LC.UNKNOWN, T1, "x"))
        # B diz READY: sem referencia; com referencia mas sem corrida; e por fim com corrida real que colheu materia.
        for B, est, esperado in (
            (livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, None)), {}, R.UNKNOWN),
            (livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "REF")), {sid: estado_b(sid, classe=None)}, R.UNKNOWN),
            (livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "BCR-x")), {sid: estado_b(sid)}, R.READY_LEGACY),
        ):
            c = ctx(A=A, B=B, ESTADO_B=est, CLASSIF_B={sid: classif(sid, R.BCR_MATERIA)})
            self.assertEqual(por_id(R.censo(c))[sid]["FINAL_STATE"], esperado)

    def test_o_que_a_corrida_real_colheu_decide(self):
        sid = "IT-T1-070"
        B = livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "BCR-x"))
        casos = [
            (R.BCR_INSTITUCIONAL, {}, {}, R.NOT_READY),
            (R.BCR_LISTAGEM, {}, {}, R.NOT_READY),
            (R.BCR_MATERIA, {}, {}, R.READY_LEGACY),
            (R.BCR_PAPELADA, {}, {}, R.UNKNOWN),
            # rota mudou no passo 2: so vale se a listagem nova esta provada
            (R.BCR_INSTITUCIONAL, {sid: {"SOURCE_ID": sid, "DEPOIS": {"INDEX_URL": "https://ex.it/n/"}}},
             {sid: {"SOURCE_ID": sid, "LISTAGEM_PROVADA": True}}, R.READY_LEGACY),
            (R.BCR_INSTITUCIONAL, {sid: {"SOURCE_ID": sid, "DEPOIS": {"INDEX_URL": "https://ex.it/n/"}}},
             {sid: {"SOURCE_ID": sid, "LISTAGEM_PROVADA": False}}, R.NOT_READY),
        ]
        for alvo, toc, pl, esperado in casos:
            c = ctx(B=B, ESTADO_B={sid: estado_b(sid)}, CLASSIF_B={sid: classif(sid, alvo)},
                    PASSO2_TOCADAS=toc, PROVA_B=pl)
            self.assertEqual(por_id(R.censo(c))[sid]["FINAL_STATE"], esperado, alvo)
        # 429 na corrida real: RETRY, nao READY
        c = ctx(B=B, ESTADO_B={sid: estado_b(sid, classe="RATE_LIMITED_429")})
        self.assertEqual(por_id(R.censo(c))[sid]["FINAL_STATE"], R.RETRY)
        # DEGRADED em B fica DEGRADED
        c = ctx(B=livro(*B["TRANSICOES"], linha(sid, LC.READY_FOR_COLLECTION, LC.DEGRADED, T3, "BCR-x", owner=LC.OWNER_COLLECTION)),
                ESTADO_B={sid: estado_b(sid, classe="ROUTE_FAILURE")})
        self.assertEqual(por_id(R.censo(c))[sid]["FINAL_STATE"], R.DEGRADED)


class UmaIdentidadePelaProva(unittest.TestCase):

    def test_rt4_conflito_resolve_se_pela_prova_e_nao_pela_ordem_dos_livros(self):
        """A: READY pelos quatro passos (T3). B: CANARY_FAILED (T2). E trocado."""
        sid = "IT-T7-017"
        ready = livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T3, "EV-1"))
        falhou = livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.CONTRACTED_CANARY_FAILED, T2, "BCR-x"))
        ev = {"EV-1": prova_canario("EV-1", sid)}
        c1 = ctx(A=ready, B=falhou, EVIDENCIA_A=ev, CONTRATOS_A={sid: contrato(sid)})
        self.assertEqual(por_id(R.censo(c1))[sid]["FINAL_STATE"], R.READY_CURRENT)
        # A prova e a mesma; muda so quem a guarda. A falha posterior com prova, sobre o contrato atual, vence o READY antigo.
        falhou_depois = livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "EV-0"),
                              linha(sid, LC.READY_FOR_COLLECTION, LC.CANARY_PENDING, T2, "CONTRATO:ROUTE_PROVENANCE"),
                              linha(sid, LC.CANARY_PENDING, LC.CONTRACTED_CANARY_FAILED, T3, "EV-2"))
        ready_antes = livro(linha(sid, None, LC.CANARY_PENDING, T0), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T1, "BCR-x"))
        c2 = ctx(A=falhou_depois, B=ready_antes, ESTADO_B={sid: estado_b(sid)}, CLASSIF_B={sid: classif(sid, R.BCR_MATERIA)},
                 CONTRATOS_A={sid: contrato(sid, integrado_em=T2)})
        self.assertEqual(por_id(R.censo(c2))[sid]["FINAL_STATE"], R.NOT_READY)

    def test_rt4_a_ordem_das_transicoes_dentro_do_livro_e_o_estado(self):
        """Inverter a lista de um livro muda o que ele diz — e a decisao continua a ler a PROVA."""
        sid = "IT-T7-017"
        a = livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T3, "EV-1"))
        ev = {"EV-1": prova_canario("EV-1", sid)}
        invertido = livro(*reversed(a["TRANSICOES"]))
        c = ctx(A=invertido, EVIDENCIA_A=ev, CONTRATOS_A={sid: contrato(sid)})
        l = por_id(R.censo(c))[sid]
        # a ultima linha do livro invertido e CANARY_PENDING: o estado de A mudou, e a decisao le-o.
        self.assertEqual(l["STATE_A"], LC.CANARY_PENDING)
        self.assertEqual(l["FINAL_STATE"], R.NOT_READY)

    def test_rt6_candidata_com_source_id_e_uma_identidade_so(self):
        sid = "IT-T5-041"
        c = ctx(A=livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "EV-1")),
                B2=livro(linha("CAND-0500", None, LC.POLICY_BLOCK, T1, "BRIDGE:x")),
                EVIDENCIA_A={"EV-1": prova_canario("EV-1", sid)}, CONTRATOS_A={sid: contrato(sid)},
                PORTA={"CAND-0500": candidata("CAND-0500", "LINKEDIN", "linkedin.com")},
                ALIAS={"CAND-0500": sid})
        d = R.censo(c)
        ids = [l["SOURCE_ID"] for l in d["LINHAS"]]
        self.assertEqual(ids, [sid], ids)
        self.assertEqual(d["CONJUNTOS"]["IDENTIDADES_FINAIS"], 1)
        self.assertEqual(len(d["SOURCE_ID_DUPLICATES"]), 1)
        # e o bloqueio da candidata pertence a SOURCE_ID: uma identidade, um estado.
        self.assertEqual(d["LINHAS"][0]["FINAL_STATE"], R.POLICY_BLOCK)
        self.assertIn("CAND-0500", d["LINHAS"][0]["CHAVES_NOS_LIVROS"])

    def test_identificador_de_prova_nao_e_fonte(self):
        c = ctx(A=livro(linha("IT-PROVA-RETRY", None, LC.CANARY_PENDING, T1), linha("IT-PROVA-RETRY", LC.CANARY_PENDING, LC.RETRY_AFTER, T1, "PROVA-C")))
        l = por_id(R.censo(c))["IT-PROVA-RETRY"]
        self.assertEqual(l["IDENTITY_KIND"], "INVALIDO")
        self.assertEqual(l["FINAL_STATE"], R.UNKNOWN)

    def test_reconciliation_required_remedida_pelo_livro_com_o_adaptador(self):
        sid = "IT-T7-015"
        c = ctx(A=livro(linha(sid, None, LC.CANARY_PENDING, T0), linha(sid, LC.CANARY_PENDING, LC.CONTRACT_READY_ROUTE_BLOCKED, T0, "M04"),
                        linha(sid, LC.CONTRACT_READY_ROUTE_BLOCKED, LC.RECONCILIATION_REQUIRED, T1, "INTEGRACAO:x")),
                B=livro(linha(sid, None, LC.CANARY_PENDING, T1), linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "BCR-yt")),
                ESTADO_B={sid: estado_b(sid, obs=15, strategy="CUSTOM_ADAPTER", adapter="CANAL_PUBLICO_YOUTUBE_V1")})
        l = por_id(R.censo(c))[sid]
        self.assertEqual(l["FINAL_STATE"], R.READY_LEGACY)
        self.assertIn("NAO nesta arvore", l["CAPABILITY_EVIDENCE"]["ONDE"])
        self.assertEqual(l["LIFECYCLE_TARGET"], LC.READY_FOR_COLLECTION)


class OLivroEvoluiPorAcrescimo(unittest.TestCase):
    """aplicar() escreve SO por lifecycle.registar, numa pasta descartavel."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, R.SAIDA)
        LC.LIVRO = d / "LEDGER.json"
        R.SAIDA = d / "RECONCILIACAO.json"

    def tearDown(self):
        LC.LIVRO, R.SAIDA = self._antes
        self.tmp.cleanup()

    def _ctx_real_pequeno(self):
        yt = "IT-T7-015"
        so_b = "IT-T3-002"
        cand = "CAND-0001"
        LC.registar(yt, LC.CANARY_PENDING, "m04")
        LC.registar(yt, LC.CONTRACT_READY_ROUTE_BLOCKED, "robots", evidence_ref="M04")
        LC.registar(yt, LC.RECONCILIATION_REQUIRED, "rota nova noutra arvore", evidence_ref="INTEGRACAO:x")
        return ctx(A=LC._ler_bruto(),
                   B=livro(linha(yt, None, LC.CANARY_PENDING, T1), linha(yt, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "BCR-yt"),
                           linha(so_b, None, LC.CANARY_PENDING, T1, "regras/italy_contracts.mjs"),
                           linha(so_b, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, "BCR-sob")),
                   B2=livro(linha(cand, None, LC.POLICY_BLOCK, T1, "BRIDGE:x")),
                   ESTADO_B={yt: estado_b(yt, obs=15, strategy="CUSTOM_ADAPTER", adapter="CANAL_PUBLICO_YOUTUBE_V1"),
                             so_b: estado_b(so_b, origem="HAND")},
                   CLASSIF_B={so_b: classif(so_b, R.BCR_INSTITUCIONAL, classe="BOLETIM_SERIADO", criterio="C2")},
                   PORTA={cand: candidata(cand, "LINKEDIN", "linkedin.com")})

    def test_aplicar_e_append_only_com_trilho_e_idempotente(self):
        c = self._ctx_real_pequeno()
        antes = json.loads(LC.LIVRO.read_text(encoding="utf-8"))["TRANSICOES"]
        doc = R.censo(c)
        r = R.aplicar(doc, c)
        depois = json.loads(LC.LIVRO.read_text(encoding="utf-8"))["TRANSICOES"]
        # 1. nada do que existia mudou
        self.assertEqual(depois[:len(antes)], antes)
        self.assertEqual(r["LINHAS_DEPOIS"], r["LINHAS_ANTES"] + r["APENDIDAS"])
        self.assertEqual(r["CADEIAS_ILEGAIS_NAO_IMPORTADAS"], [])
        est = LC.snapshot()
        # 2. a fonte YouTube foi remedida: RECONCILIATION_REQUIRED -> CANARY_PENDING -> READY, com trilho
        self.assertEqual(est["IT-T7-015"], LC.READY_FOR_COLLECTION)
        ult = LC.historia("IT-T7-015")[-1]
        self.assertEqual(ult["RECONCILIACAO"]["FINAL_STATE"], R.READY_LEGACY)
        self.assertEqual(ult["RECONCILIACAO"]["EVIDENCE_COMMIT"], "bbbbbbbb")
        self.assertTrue(ult["EVIDENCE_REF"].startswith("RECONCILIACAO-V1:"))
        # 3. a fonte so de B veio com a cadeia dela importada, e depois a decisao (capa -> remedir)
        h = LC.historia("IT-T3-002")
        self.assertEqual([t["NEW_STATE"] for t in h], [LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, LC.CANARY_PENDING])
        self.assertEqual(h[0]["IMPORTADO_DE"]["COMMIT"], "bbbbbbbb")
        self.assertEqual(h[1]["IMPORTADO_DE"]["OBSERVED_AT_ORIGINAL"], T2)
        self.assertEqual(h[2]["RECONCILIACAO"]["FINAL_STATE"], R.NOT_READY)
        # 4. o bloqueio do bridge entrou, com a chave original
        self.assertEqual(est["CAND-0001"], LC.POLICY_BLOCK)
        self.assertEqual(LC.historia("CAND-0001")[0]["IMPORTADO_DE"]["LIVRO"], "B2")
        # 5. segunda passagem: zero linhas novas
        c2 = dict(c, A=LC._ler_bruto())
        doc2 = R.censo(c2)
        self.assertEqual(R.plano(doc2, c2), [])
        r2 = R.aplicar(doc2, c2)
        self.assertEqual(r2["APENDIDAS"], 0)
        self.assertEqual(json.loads(LC.LIVRO.read_text(encoding="utf-8"))["TRANSICOES"][:len(depois)], depois)

    def test_extra_nao_sobrescreve_chave_canonica(self):
        with self.assertRaises(ValueError):
            LC.registar("IT-T7-900", LC.CANARY_PENDING, "x", extra={"NEW_STATE": "READY_FOR_COLLECTION"})
        self.assertEqual(LC.snapshot(), {})


class OLivroDoBotAtravessa(unittest.TestCase):
    """O LIVRO C — o bot vivo. Cada lei da ponte com o ataque que a tenta partir.

    RT-C1  fonte que so o bot conhece desaparece na reconciliacao  -> entra, com cadeia
    RT-C2  o bot lava uma READY_LEGACY para READY_CURRENT          -> LEGACY_LEAK = 0
    RT-C3  o bot promove citando prova que nao existe              -> nao promove
    RT-C4  o bot, medindo antes, derruba medicao desta arvore      -> nao derruba
    RT-C5  o bot mede DEPOIS, com prova a resolver                 -> vence (a ponte e viva)
    RT-C6  fonte so da Collection desaparece por o bot nao a ter   -> fica
    RT-C7  bloqueio do bot some por omissao                        -> preserva-se
    RT-C8  bloqueio do bot sobrevive a prova posterior             -> cede
    RT-C9  o bot escreve elegibilidade                             -> so o gate decide
    """

    def _c(self, **kw):
        return ctx(**kw)

    def test_rt_c1_fonte_so_do_bot_entra_com_a_cadeia(self):
        sid = "IT-T4-077"
        c = self._c(C=livro(linha(sid, None, LC.CANARY_PENDING, T1),
                            linha(sid, LC.CANARY_PENDING, LC.CONTRACTED_CANARY_FAILED, T2, "EV-C1")))
        l = por_id(R.censo(c))[sid]
        self.assertEqual(l["STATE_C"], LC.CONTRACTED_CANARY_FAILED)
        self.assertEqual(l["FINAL_STATE"], R.NOT_READY)
        # e o plano importa a cadeia INTEIRA do bot, nao so o estado final
        origem, chave = R._livro_de_origem(l, dict(c, _HIST={n: R.historias(c.get(n)) for n in R.LIVROS}))
        self.assertEqual((origem, chave), ("C", sid))

    def test_rt_c2_o_bot_nao_lava_legacy_para_current(self):
        sid = "IT-T4-078"
        # A promoveu pela regua ANTIGA: item aberto e a propria capa.
        ref = "EV-A-LEGACY"
        c = self._c(A=livro(linha(sid, None, LC.CANARY_PENDING, T1),
                            linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T2, ref)),
                    EVIDENCIA_A={ref: prova_canario(ref, sid, item="https://ex.it/news/",
                                                    kind="MIXED", capa="NAO_SEI", par=10)},
                    CONTRATOS_A={sid: contrato(sid)},
                    # o bot diz READY com prova perfeita, e DEPOIS
                    C=livro(linha(sid, None, LC.CANARY_PENDING, T2),
                            linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T3, "EV-C2")),
                    EVIDENCIA_C={"EV-C2": prova_canario("EV-C2", sid)},
                    CONTRATOS_C={sid: contrato(sid)})
        d = R.censo(c)
        l = por_id(d)[sid]
        self.assertEqual(l["FINAL_STATE"], R.READY_LEGACY)   # NAO subiu a CURRENT
        self.assertEqual(d["TELEMETRIA_DA_PONTE"]["LEGACY_LEAK"], 0)

    def test_rt_c3_promocao_do_bot_sem_prova_no_manifesto_nao_promove(self):
        sid = "IT-T4-079"
        c = self._c(A=livro(linha(sid, None, LC.CANARY_PENDING, T2)),
                    # prova citada que o manifesto do bot NAO tem, e medida depois
                    C=livro(linha(sid, None, LC.CANARY_PENDING, T2),
                            linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T3,
                                  "MISSAO-04:curadoria/READY-FOR-COLLECTION-V1.json@959ae46a")),
                    EVIDENCIA_C={})
        d = R.censo(c)
        l = por_id(d)[sid]
        self.assertNotIn(l["FINAL_STATE"], (R.READY_CURRENT, R.READY_LEGACY))
        self.assertIs(l["CANARY_C"]["RESOLVE_NO_MANIFESTO_DO_BOT"], False)
        t = d["TELEMETRIA_DA_PONTE"]
        self.assertEqual(t["RECUSAS_POR_MOTIVO"]["PROMOCAO_SEM_PROVA_DE_CANARIO"], 1)
        self.assertEqual(t["BOT_READY_ACEITES"], 0)

    def test_rt_c3b_o_veredito_do_bot_por_si_nao_diz_ready_sem_prova(self):
        """A LEI MEDE-SE ONDE ELA VIVE.

        `_degrau_c` tambem recusa esta promocao, mas por outra razao (a regua
        nao sobe, o bot mediu antes). Se so se medisse o estado final, apagar
        a guarda DENTRO de `veredito_c` nao partiria teste nenhum — e ficaria
        uma funcao publica a afirmar «C prova READY» sobre uma promocao que
        nao tem canario nenhum. O contrato de `veredito_c` e dizer o que C
        prova POR SI; e por si, sem prova, C nao prova READY.
        """
        sid = "IT-T4-089"
        c = ctx(C=livro(linha(sid, None, LC.CANARY_PENDING, T2),
                        linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T3,
                              "MISSAO-04:ficheiro-de-missao-nao-e-canario")),
                EVIDENCIA_C={}, CONTRATOS_C={sid: contrato(sid)})
        c["_ULT"] = {n: R.ultimos(c.get(n)) for n in R.LIVROS}
        estado, porque, _ = R.veredito_c(sid, c)
        self.assertEqual(estado, R.UNKNOWN, porque)
        self.assertIn("promocao sem canario nao promove", porque)
        # e com a prova a resolver, a MESMA funcao promove: a guarda distingue.
        ref = "EV-OK-C3B"
        c2 = ctx(C=livro(linha(sid, None, LC.CANARY_PENDING, T2),
                         linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T3, ref)),
                 EVIDENCIA_C={ref: prova_canario(ref, sid)}, CONTRATOS_C={sid: contrato(sid)})
        c2["_ULT"] = {n: R.ultimos(c2.get(n)) for n in R.LIVROS}
        self.assertEqual(R.veredito_c(sid, c2)[0], R.READY_CURRENT)

    def test_rt_c4_bot_que_mediu_antes_nao_derruba_esta_arvore(self):
        sid = "IT-T4-080"
        ref = "EV-A4"
        c = self._c(A=livro(linha(sid, None, LC.CANARY_PENDING, T2),
                            linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T3, ref)),
                    EVIDENCIA_A={ref: prova_canario(ref, sid)}, CONTRATOS_A={sid: contrato(sid)},
                    C=livro(linha(sid, None, LC.RECONCILIATION_REQUIRED, T1, "INTEGRACAO:x")))
        l = por_id(R.censo(c))[sid]
        self.assertEqual(l["FINAL_STATE"], R.READY_CURRENT)
        self.assertIn("mediu ANTES", l["FINAL_REASON"])

    def test_rt_c5_bot_que_mede_depois_com_prova_vence_a_ponte_e_viva(self):
        """Se NADA do bot pudesse vencer, a ponte estaria morta — seria um
        filtro, nao um cano. Aqui A esta pendente e o bot prova DEPOIS."""
        sid = "IT-T4-081"
        c = self._c(A=livro(linha(sid, None, LC.CANARY_PENDING, T1)),
                    C=livro(linha(sid, None, LC.CANARY_PENDING, T2),
                            linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T3, "EV-C5")),
                    EVIDENCIA_C={"EV-C5": prova_canario("EV-C5", sid)},
                    CONTRATOS_C={sid: contrato(sid)})
        l = por_id(R.censo(c))[sid]
        self.assertEqual(l["FINAL_STATE"], R.READY_CURRENT)
        self.assertEqual(l["LIFECYCLE_TARGET"], LC.READY_FOR_COLLECTION)
        self.assertEqual(l["LATEST_VALID_EVIDENCE"]["FONTE"], "livro C (bot)")

    def test_rt_c6_fonte_so_da_collection_nao_desaparece(self):
        so_a, so_c = "IT-T4-082", "IT-T4-083"
        c = self._c(A=livro(linha(so_a, None, LC.CANARY_PENDING, T2)),
                    C=livro(linha(so_c, None, LC.CANARY_PENDING, T2)))
        d = R.censo(c)
        self.assertEqual(sorted(por_id(d)), [so_a, so_c])
        self.assertEqual(d["CONJUNTOS"]["IDENTIDADES_FINAIS"], 2)

    def test_rt_c7_bloqueio_do_bot_nao_some_por_omissao(self):
        sid = "IT-T4-084"
        c = self._c(A=livro(linha(sid, None, LC.CANARY_PENDING, T1)),
                    C=livro(linha(sid, None, LC.CAPABILITY_BLOCK, T2, "CARACT:x")))
        l = por_id(R.censo(c))[sid]
        self.assertEqual(l["FINAL_STATE"], R.CAPABILITY_BLOCK)
        self.assertEqual(l["CAPABILITY_EVIDENCE"]["LIVRO"], "C")

    def test_rt_c8_bloqueio_do_bot_cede_a_prova_posterior_desta_arvore(self):
        """O caso real dos 4: o bot marcou CAPABILITY_BLOCK as 22:54 de 20/09;
        esta arvore escreveu o contrato e passou o canario a 21/09. Capacidade
        nova PROVADA supera o bloqueio — isso nao e revogacao por omissao."""
        sid = "IT-T4-085"
        ref = "EV-A8"
        c = self._c(A=livro(linha(sid, None, LC.CAPABILITY_BLOCK, T1, "CARACT:x"),
                            linha(sid, LC.CAPABILITY_BLOCK, LC.CANARY_PENDING, T2, "contrato escrito"),
                            linha(sid, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, T3, ref)),
                    EVIDENCIA_A={ref: prova_canario(ref, sid)}, CONTRATOS_A={sid: contrato(sid)},
                    C=livro(linha(sid, None, LC.CAPABILITY_BLOCK, T1, "CARACT:x")))
        d = R.censo(c)
        l = por_id(d)[sid]
        self.assertEqual(l["FINAL_STATE"], R.READY_CURRENT)
        self.assertTrue(d["BLOQUEIOS"]["BLOCKS_SUPERSEDED_BY_LATER_EVIDENCE"])

    def test_rt_c9_o_bot_nao_escreve_elegibilidade(self):
        """SOURCE_CURATOR_READY != COLLECTION_ELIGIBLE. A palavra nao existe no
        vocabulario da reconciliacao, e nao ha aqui uma segunda copia da regua:
        quem decide e collection_gate."""
        import ast
        arvore = ast.parse((AQUI / "reconciliar_livros.py").read_text(encoding="utf-8"))
        escritas = []
        for no in ast.walk(arvore):
            alvos = []
            if isinstance(no, ast.Assign):
                alvos = no.targets
            elif isinstance(no, (ast.AnnAssign, ast.AugAssign)):
                alvos = [no.target]
            for a in alvos:
                if isinstance(a, ast.Name) and a.id == "COLLECTION_ELIGIBLE":
                    escritas.append(a.id)
                if (isinstance(a, ast.Subscript) and isinstance(a.slice, ast.Constant)
                        and a.slice.value == "COLLECTION_ELIGIBLE"):
                    escritas.append("dict[COLLECTION_ELIGIBLE]")
            # tambem em dicionarios literais: {"COLLECTION_ELIGIBLE": ...}
            if isinstance(no, ast.Dict):
                for ch in no.keys:
                    if isinstance(ch, ast.Constant) and ch.value == "COLLECTION_ELIGIBLE":
                        escritas.append("literal COLLECTION_ELIGIBLE")
        self.assertEqual(escritas, [],
                         "a reconciliacao escreve elegibilidade; so collection_gate pode: %s" % escritas)
        # e o veredito do bot nunca devolve um estado fora do vocabulario fechado
        for v in ("READY_CURRENT", "READY_LEGACY", "NOT_READY", "UNKNOWN"):
            self.assertIn(getattr(R, v), R.ESTADOS_FINAIS)

    def test_rt_c10_url_igual_com_source_id_diferente_nao_funde(self):
        """Duas SOURCE_ID diferentes NAO se fundem por terem a mesma morada. A
        identidade vem do registo (Atlas/alocacao), nunca de uma heuristica de
        URL — fundir por parecenca inventa uma fonte que ninguem registou."""
        a, b = "IT-T4-086", "IT-T4-087"
        c = self._c(C=livro(linha(a, None, LC.CANARY_PENDING, T2),
                            linha(b, None, LC.CANARY_PENDING, T2)),
                    PORTA={}, ALIAS={})
        d = R.censo(c)
        self.assertEqual(sorted(por_id(d)), [a, b])
        self.assertEqual(d["SOURCE_ID_DUPLICATES"], [])

    def test_rt_c16_divergencia_nominal_nao_e_divergencia_de_facto(self):
        """CONTAR NOMES DE ESTADO CONTA DUAS VEZES O MESMO ACORDO.

        Medido em 2026-09-22, depois da volta 3: comparar o estado desta
        arvore com o do bot dava **124** divergencias nominais, onde a missao
        tinha medido 63. Parecia que a reconciliacao tinha piorado o dobro.
        Nao tinha: 61 dessas 124 eram fontes em que os dois lados dizem a
        MESMA COISA com nomes diferentes — `CANARY_PENDING` aqui e
        `CONTRACTED_CANARY_FAILED` no bot sao ambos «nao pronta, falta provar
        a rota». Sao o mesmo facto, e `_alvo_lifecycle` traduz um no outro de
        proposito (NOT_READY guarda o passo pendente da familia).

            DOIS NOMES PARA O MESMO FACTO NAO SAO UM DESACORDO.

        Quem contasse nomes concluia que a ponte partiu, e ia «consertar» um
        acordo. Compara-se por CLASSE — pronta · nao pronta · bloqueada ·
        adiada — e so o que muda de classe e divergencia a serio.
        """
        pares_que_concordam = [
            (LC.CANARY_PENDING, LC.CONTRACTED_CANARY_FAILED),
            (LC.CANARY_PENDING, LC.CONTRACT_PENDING),
            (LC.SEMANTIC_REVIEW, LC.RECONCILIATION_REQUIRED),
        ]
        for aqui, no_bot in pares_que_concordam:
            self.assertIn(aqui, R.FAMILIA_NOT_READY)
            self.assertIn(no_bot, R.FAMILIA_NOT_READY)
            self.assertEqual(R._mapa(aqui), R._mapa(no_bot),
                             "%s e %s deviam ler-se como o mesmo facto" % (aqui, no_bot))
        # e os que MUDAM de classe continuam a ser desacordo a serio
        for aqui, no_bot in ((LC.READY_FOR_COLLECTION, LC.CAPABILITY_BLOCK),
                             (LC.READY_FOR_COLLECTION, LC.RECONCILIATION_REQUIRED),
                             (LC.CANARY_PENDING, LC.READY_FOR_COLLECTION)):
            self.assertNotEqual(R._mapa(aqui), R._mapa(no_bot))

    def test_rt_c13_o_head_do_bot_e_descoberto_nao_escrito_a_mao(self):
        """A PONTE FUTURA TEM DE ESTAR VIVA.

        `REF_C_MEDIDO` e so o registo do corte desta medicao. Se a ponte
        passasse a devolver essa constante, o censo de hoje continuaria verde
        para sempre e o trabalho que o bot fizer amanha nunca atravessaria —
        um censo historico verde com ponte futura morta e uma falha.

        Prova-se pedindo o HEAD de OUTRA referencia conhecida: se a funcao
        descobre mesmo, devolve o HEAD dela; se devolvesse a constante, este
        teste morria.
        """
        outra = R.ref_do_bot("HEAD")
        esperado = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                  cwd=str(AQUI.parent), capture_output=True,
                                  text=True, timeout=30).stdout.strip()
        if not esperado:
            self.skipTest("git nao responde nesta arvore")
        self.assertEqual(outra, esperado)
        # e o HEAD do bot vem da branch dele, nao de uma constante no ficheiro
        do_bot = R.ref_do_bot(R.BRANCH_C)
        da_branch = subprocess.run(["git", "rev-parse", "--short", R.BRANCH_C],
                                   cwd=str(AQUI.parent), capture_output=True,
                                   text=True, timeout=30).stdout.strip()
        if da_branch:
            self.assertEqual(do_bot, da_branch)

    def test_rt_c15_prova_do_bot_nunca_sobrepoe_a_desta_arvore(self):
        """Mesma EVIDENCE_REF, conteudo DIFERENTE, e uma colisao de identidade
        entre duas arvores. Nao se resolve escolhendo uma: a de ca fica, a do
        bot NAO entra, e a colisao fica dita. Medido: 35 referencias comuns,
        todas iguais, 0 colisoes — mas a guarda tem de existir antes de haver
        a primeira."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = Path(tmp.name)
        antes = R.EVIDENCIA_A
        R.EVIDENCIA_A = d / "EVIDENCE.json"
        self.addCleanup(lambda: setattr(R, "EVIDENCIA_A", antes))
        ref = "EV-COLISAO-0001"
        local = prova_canario(ref, "IT-T4-090", item="https://ex.it/news/a-de-ca-2026/")
        R.EVIDENCIA_A.write_text(json.dumps(
            {"DATASET": "LIFECYCLE-EVIDENCE-V1", "PROVAS": [local]}, ensure_ascii=False),
            encoding="utf-8")
        do_bot = prova_canario(ref, "IT-T4-999", item="https://outra.it/news/do-bot-2026/")
        c = ctx(EVIDENCIA_C={ref: do_bot}, COMMITS={"A": "a", "B": "b", "B2": "c", "C": "d"})
        r = R.importar_provas_do_bot([{"SOURCE_ID": "IT-T4-090", "EVIDENCE_REF": ref}], c)
        self.assertEqual(r["PROVAS_IMPORTADAS"], 0)
        self.assertEqual(len(r["COLISOES_NAO_IMPORTADAS"]), 1)
        self.assertEqual(r["COLISOES_NAO_IMPORTADAS"][0]["SOURCE_ID_NO_BOT"], "IT-T4-999")
        # e o ficheiro em disco continua com a prova DESTA arvore, intacta
        depois = json.loads(R.EVIDENCIA_A.read_text(encoding="utf-8"))["PROVAS"]
        self.assertEqual(depois, [local])

    def test_rt_c12_a_ponte_nao_escreve_em_regras_nem_em_contratos(self):
        """RECOLLECTION_UNKNOWN_LEAK = 0, por construcao e medido.

        A recollection e um SEGUNDO portao, depois deste: quem nao declara
        `DETAIL_CONTENT` fica `BLOCKED_FOR_BIG_COLLECTION` mesmo estando
        elegivel pela curadoria. Uma fonte NAO pode ganhar essa passagem por o
        bot a ter aprovado — e a unica forma de a ganhar seria esta ponte
        escrever num contrato. Entao ela nao escreve em contrato nenhum: os
        unicos caminhos que grava sao o livro e o manifesto de prova.
        """
        import ast
        texto = (AQUI / "reconciliar_livros.py").read_text(encoding="utf-8")
        arvore = ast.parse(texto)
        escritas = []
        for no in ast.walk(arvore):
            if (isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute)
                    and no.func.attr == "write_text"):
                alvo = no.func.value
                escritas.append(alvo.id if isinstance(alvo, ast.Name) else ast.dump(alvo)[:40])
        self.assertTrue(escritas, "nenhuma escrita encontrada — o teste deixou de medir")
        self.assertEqual(sorted(set(escritas)), ["SAIDA", "caminho"],
                         "a reconciliacao passou a escrever noutro sitio: %s" % set(escritas))
        # e nenhuma mencao a RECOLLECTION / contratos de coleta neste modulo
        self.assertNotIn("RECOLLECTION", texto)
        self.assertNotIn("italy_contracts.mjs", texto)

    def test_rt_c11_o_corte_logico_fica_escrito(self):
        c = self._c(C=livro(linha("IT-T4-088", None, LC.CANARY_PENDING, T1),
                            linha("IT-T4-088", LC.CANARY_PENDING, LC.RETRY_AFTER, T2)))
        s = R.censo(c)["BOT_SNAPSHOT"]
        self.assertEqual(s["BOT_SNAPSHOT_HEAD"], "dddddddd")
        self.assertEqual(s["BOT_SNAPSHOT_TRANSITION_MAX_ID"], 2)
        self.assertEqual(s["BOT_SNAPSHOT_TIME"], T2)


class OsLivrosReais(unittest.TestCase):
    """Le os QUATRO livros reais (A do disco; B, B2 e C por git show) e NAO
    escreve. Invariantes que valem antes e depois de aplicar a reconciliacao."""

    def test_zy_censo_dos_livros_reais(self):
        # O livro A e o REAL, dito por extenso: outro modulo da suite pode ter
        # deixado LC.LIVRO a apontar para uma pasta descartavel ja apagada, e
        # um ledger vazio faria os 4 bloqueios superados voltarem (17 -> 21).
        antes = LC.LIVRO
        LC.LIVRO = AQUI / "LIFECYCLE-LEDGER-V1.json"
        try:
            c = R.carregar_contexto()
        finally:
            LC.LIVRO = antes
        if not c["B"] or not c["B2"] or not c["C"]:
            self.skipTest("git show nao alcanca %s/%s/%s nesta arvore"
                          % (R.REF_B, R.REF_B2, R.REF_C))
        d = R.censo(c)
        # ⚠️ AQUI AFIRMAM-SE LEIS, NAO FOTOGRAFIAS. O livro do bot e escrito por
        # um servico que esta a correr: qualquer numero absoluto sobre ele
        # (fontes, transicoes, recusas) envelhece sozinho e produz um vermelho
        # que nao significa defeito. Os limites inferiores (`>=`) valem porque
        # os livros sao append-only e os bloqueios nao se revogam.
        con = d["CONJUNTOS"]
        self.assertEqual(con["IDENTIDADES_FINAIS"], con["UNIAO_TODOS"])
        self.assertGreaterEqual(con["UNIAO_TODOS"], 555)
        self.assertEqual(con["COMUNS_A_C"] + con["SO_C_VS_A"], d["LIVROS"]["C"]["SOURCES"])
        self.assertEqual(sum(d["POR_ESTADO_FINAL"].values()), con["IDENTIDADES_FINAIS"])
        self.assertEqual(d["SOURCE_ID_DUPLICATES"], [])
        # bloqueios provados nao desaparecem: o numero nunca desce
        self.assertGreaterEqual(d["POR_ESTADO_FINAL"][R.POLICY_BLOCK], 69)

        t = d["TELEMETRIA_DA_PONTE"]
        self.assertEqual(t["LEGACY_LEAK"], 0)
        # ⚠️ A LEI, nao a contagem: TODA a fonte que o bot diz READY e que aqui
        # nao e READY tem de ter um motivo escrito — e se o motivo e «sem prova
        # de canario», a prova citada tem mesmo de nao resolver no livro dele.
        porid = {l["SOURCE_ID"]: l for l in d["LINHAS"]}
        for rec in t["RECUSAS"]:
            self.assertTrue(rec["MOTIVO"], rec)
            if rec["MOTIVO"] == "PROMOCAO_SEM_PROVA_DE_CANARIO":
                self.assertIs(porid[rec["SOURCE_ID"]]["CANARY_C"]
                              ["RESOLVE_NO_MANIFESTO_DO_BOT"], False, rec)
        self.assertEqual(t["BOT_READY_ACEITES"] + t["BOT_READY_RECUSADAS"], t["BOT_READY"])
        # ⚠️ READY_CURRENT nao se afirma por contagem: afirma-se pela regua.
        # Nenhuma fonte pode estar READY_CURRENT sem os quatro passos na prova.
        for l in d["LINHAS"]:
            if l["FINAL_STATE"] == R.READY_CURRENT:
                passos = l.get("DETAIL_PROOF_A") or l.get("DETAIL_PROOF_C") or {}
                self.assertTrue(passos.get("BODY_UTIL"),
                                "%s e READY_CURRENT sem BODY_UTIL provado" % l["SOURCE_ID"])
        # ⚠️ O LIVRO DO BOT E UM ALVO VIVO. Este teste ja falhou uma vez por
        # afirmar `TRANSITION_MAX_ID == 1008`: o supervisor escreveu mais 119
        # transicoes a meio da missao e o numero passou a 1127. Fixar a
        # fotografia de um servico que corre e garantir um vermelho no dia
        # seguinte — e, pior, um vermelho que nao significa defeito nenhum.
        # Afirma-se o INVARIANTE: o livro e append-only, logo o corte nunca
        # encolhe, e bate sempre com o livro que foi mesmo lido.
        s = d["BOT_SNAPSHOT"]
        self.assertEqual(s["BOT_SNAPSHOT_HEAD"], R.REF_C)
        self.assertEqual(s["BOT_SNAPSHOT_TRANSITION_MAX_ID"], len(c["C"]["TRANSICOES"]))
        self.assertGreaterEqual(s["BOT_SNAPSHOT_TRANSITION_MAX_ID"], 1008)
        self.assertEqual(s["BOT_SNAPSHOT_SOURCES"], d["LIVROS"]["C"]["SOURCES"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
