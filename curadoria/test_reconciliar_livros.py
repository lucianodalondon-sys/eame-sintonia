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
    base = {"COMMITS": {"A": "aaaaaaaa", "B": "bbbbbbbb", "B2": "cccccccc"},
            "A": livro(), "B": livro(), "B2": livro(),
            "EVIDENCIA_A": {}, "CONTRATOS_A": {}, "CONTRATOS_B": {}, "LISTAGENS_A": {},
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


class OsLivrosReais(unittest.TestCase):
    """Le os tres livros reais (A do disco, B e B2 por git show) e NAO escreve.
    Invariantes que valem antes e depois de aplicar a reconciliacao."""

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
        if not c["B"] or not c["B2"]:
            self.skipTest("git show nao alcanca %s/%s nesta arvore" % (R.REF_B, R.REF_B2))
        d = R.censo(c)
        self.assertEqual(d["CONJUNTOS"]["IDENTIDADES_FINAIS"], 278)
        self.assertEqual(d["SOURCE_ID_DUPLICATES"], [])
        self.assertEqual(d["BLOQUEIOS"]["BLOCKS_REJECTED_AS_STALE"], [])
        self.assertEqual(d["POR_ESTADO_FINAL"][R.POLICY_BLOCK], 69)
        self.assertEqual(d["POR_ESTADO_FINAL"][R.CAPABILITY_BLOCK], 17)
        self.assertEqual(d["POR_ESTADO_FINAL"][R.READY_CURRENT], 10)
        self.assertEqual(sum(d["POR_ESTADO_FINAL"].values()), 278)


if __name__ == "__main__":
    unittest.main(verbosity=2)
