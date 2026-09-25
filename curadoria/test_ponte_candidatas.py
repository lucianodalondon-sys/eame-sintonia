#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TESTES DA PONTE DE CANDIDATAS (FASE 5) — trazidos de candidate-bridge-v1.

Cada teste ATACA uma lei. Um teste que só confirma o caminho feliz não prova
lei nenhuma — prova que o código corre.

    UM TESTE QUE NUNCA DIZ «NÃO» NÃO MEDE NADA.

RED TEAM INCLUÍDO:
    T1 tem dois modos: normal (guarda activa) e mutado (guarda desligada).
    No modo mutado a contraprova REPROVA — se não reprovar, o teste é decorativo.

ISOLAMENTO (BRIDGE-FEEDER, G4) — a versão do bridge fazia `importlib.reload`
dos módulos em cada setUp e nunca restaurava os caminhos: o teste seguinte de
outro ficheiro herdava `LC.LIVRO` a apontar para uma pasta descartável já
apagada. Aqui o molde é o de test_ready_split.py:44-48 — caminhos guardados
em `_antes`, restaurados em tearDown, e a impressão (sha256) dos ficheiros
REAIS tirada antes e comparada depois de cada teste.

A ponte escreve em QUATRO sítios: o ledger PRÓPRIO (BRIDGE-LEDGER-V1.json),
a fila (F.FILA), o livro (LC.LIVRO) e a porta (FN.FILA). Os quatro vão para a
pasta descartável. Nenhum teste aqui lê ou escreve na árvore real.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F              # noqa: E402
import lifecycle as LC        # noqa: E402
import fonte_nova as FN       # noqa: E402
import ponte_candidatas as P  # noqa: E402

# Os caminhos REAIS, escritos por extenso e nao lidos dos modulos.
CAMINHOS_REAIS = {
    "F.FILA":   RAIZ / "curadoria" / "LIFECYCLE-QUEUE-V1.json",
    "LC.LIVRO": RAIZ / "curadoria" / "LIFECYCLE-LEDGER-V1.json",
    "FN.FILA":  RAIZ / "candidatas" / "FONTES-CANDIDATAS.json",
    "P.LEDGER": RAIZ / "curadoria" / "BRIDGE-LEDGER-V1.json",
}


def _impressao(p: Path) -> str:
    if not p.exists():
        return "AUSENTE"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _impressoes() -> dict:
    return {k: _impressao(p) for k, p in CAMINHOS_REAIS.items()}


# ---------------------------------------------------------------------------
# Base: cada teste opera sobre ficheiros temporários isolados
# ---------------------------------------------------------------------------
class Isolada(unittest.TestCase):
    """Garante que nenhum teste lê ou escreve no repositório real."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, F.FILA, FN.FILA, P.CARACT, P.LEDGER)
        self._reais_antes = _impressoes()

        # Redirecionar todos os caminhos para o temporário
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        FN.FILA = d / "FONTES-CANDIDATAS.json"
        P.CARACT = d / "CARACT.json"
        P.LEDGER = d / "BRIDGE-LEDGER.json"

        self.d = d

    def tearDown(self):
        (LC.LIVRO, F.FILA, FN.FILA, P.CARACT, P.LEDGER) = self._antes
        self.tmp.cleanup()
        depois = _impressoes()
        self.assertEqual(
            self._reais_antes, depois,
            "um ficheiro REAL mudou durante o teste (antes=%s depois=%s)"
            % (self._reais_antes, depois))

    # -- helpers --

    def _porta(self, candidatas: list) -> None:
        """Cria um FONTES-CANDIDATAS.json mínimo com as candidatas fornecidas."""
        doc = {
            "DATASET": "SINTONIA-FONTES-CANDIDATAS-V1",
            "LEI": "test",
            "ESTADOS": {},
            "CANDIDATAS": candidatas,
            "TOTAL": len(candidatas),
        }
        FN.FILA.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _cand(self, cid: str, tipo: str, estado: str = "CANDIDATA") -> dict:
        return {
            "CANDIDATA_ID": cid,
            "TIPO": tipo,
            "TIPO_SIGNIFICA": tipo,
            "PAIS": "IT",
            "NOME": f"Fonte {cid}",
            "URL": f"https://example.com/{cid}",
            "PARA_QUE_SERVE": "teste",
            "QUEM_VIU": "test",
            "ONDE_VIU": "",
            "QUANDO": "2026-09-21",
            "NOTA": "",
            "ESTADO": estado,
            "SOURCE_ID": None,
            "MOTIVO_DA_RECUSA": None,
        }

    def _caract(self, cand_ids: list) -> None:
        """Cria um SOURCE-CHARACTERIZATION mínimo com os CANDIDATE_IDs dados."""
        P.CARACT.write_text(
            json.dumps(
                {"FONTES": [{"CANDIDATE_ID": c} for c in cand_ids]},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def _queue_total(self) -> int:
        return F.metricas()["QUEUE_TOTAL"]

    def _ledger_ids(self) -> set:
        d = P._carregar_ledger()
        return set(d["PROCESSADAS"].keys())


class T0_OsCaminhosDosTestesNaoSaoOsReais(Isolada):

    def test_os_quatro_caminhos_apontam_para_a_pasta_descartavel(self):
        for nome, p in (("F.FILA", F.FILA), ("LC.LIVRO", LC.LIVRO),
                        ("FN.FILA", FN.FILA), ("P.LEDGER", P.LEDGER)):
            self.assertEqual(p.parent, self.d, nome)
            self.assertNotEqual(p, CAMINHOS_REAIS[nome], nome)

    def test_o_ledger_da_ponte_e_o_proprio_nao_o_livro_canonico(self):
        """A guarda de idempotencia vive no BRIDGE-LEDGER, nao no livro."""
        self._porta([self._cand("CAND-Z001", "BASE_OFICIAL")])
        P.processar()
        self.assertTrue(P.LEDGER.exists())
        self.assertIn("CAND-Z001", self._ledger_ids())
        # O livro canonico nao ganhou entrada para a candidata enfileirada:
        # QUALIFY e trabalho na fila, nao transicao de estado no livro.
        self.assertIsNone(LC.estado_de("CAND-Z001"))


# ---------------------------------------------------------------------------
# T1 — Idempotência: correr 2x não cria tarefas duplicadas
# ---------------------------------------------------------------------------
class T1_Idempotencia(Isolada):

    def test_segunda_corrida_cria_zero_tarefas(self):
        """Correr a ponte duas vezes não produz trabalho duplicado."""
        self._porta([
            self._cand("CAND-A001", "BASE_OFICIAL"),
            self._cand("CAND-A002", "ORGANIZACAO"),
            self._cand("CAND-A003", "LINKEDIN"),
        ])

        m1 = P.processar()
        self.assertEqual(m1["TAREFAS_CRIADAS"], 2)
        self.assertEqual(m1["CLASSIFICADAS_BARRADAS"], 1)

        m2 = P.processar()
        # Segunda corrida: tudo ignorado
        self.assertEqual(m2["TAREFAS_CRIADAS"], 0,
                         "segunda corrida não pode criar novas tarefas")
        self.assertEqual(m2["CLASSIFICADAS_BARRADAS"], 0,
                         "segunda corrida não pode reclassificar")
        self.assertEqual(m2["JA_PROCESSADAS_IGNORADAS"], 3)

        # A fila tem exactamente as mesmas tarefas de antes
        self.assertEqual(self._queue_total(), m1["QUEUE_DEPTH_DEPOIS"])

    def test_red_team_sem_guarda_reprova(self):
        """RED TEAM: sem guarda de idempotência, a 2ª corrida reprocessa.

        Mutação: _carregar_ledger sempre devolve PROCESSADAS vazio.
        Expectativa: a 2ª corrida reporta TAREFAS_CRIADAS > 0 ou
                     CLASSIFICADAS_BARRADAS > 0 (prova que sem guarda há reprocessamento).
        Restaurar e provar que volta a passar é feito no teste seguinte.
        """
        self._porta([
            self._cand("CAND-B001", "BASE_OFICIAL"),
            self._cand("CAND-B002", "INSTAGRAM"),
        ])

        # Primeira corrida normal
        P.processar()

        # MUTAÇÃO: forçar _carregar_ledger a devolver ledger vazio sempre
        original_carregar = P._carregar_ledger

        def ledger_sempre_vazio():
            return {"DATASET": "test", "LEI": "muted", "PROCESSADAS": {}}

        P._carregar_ledger = ledger_sempre_vazio
        try:
            m_mutado = P.processar()
            total_reprocessado = (m_mutado["TAREFAS_CRIADAS"]
                                  + m_mutado["CLASSIFICADAS_BARRADAS"])
            self.assertGreater(
                total_reprocessado, 0,
                "RED TEAM FALHOU: sem guarda, a 2ª corrida devia reprocessar "
                "mas não reportou nenhum trabalho"
            )
        finally:
            P._carregar_ledger = original_carregar  # restaurar

    def test_red_team_restaurada_passa(self):
        """Depois de restaurar a guarda, a 2ª corrida volta a produzir zero."""
        self._porta([
            self._cand("CAND-C001", "IMPRENSA"),
            self._cand("CAND-C002", "FACEBOOK"),
        ])

        P.processar()
        m2 = P.processar()

        self.assertEqual(m2["TAREFAS_CRIADAS"], 0)
        self.assertEqual(m2["CLASSIFICADAS_BARRADAS"], 0)


# ---------------------------------------------------------------------------
# T2 — Candidata já no curator → ignorada, não reenfileirada
# ---------------------------------------------------------------------------
class T2_JaNosCurator(Isolada):

    def test_ja_no_curator_ignorada(self):
        """Candidata com CANDIDATA_ID em CARACT é ignorada pela ponte."""
        self._porta([
            self._cand("CAND-D001", "BASE_OFICIAL"),
            self._cand("CAND-D002", "ORGANIZACAO"),
        ])
        # D001 já está no curator
        self._caract(["CAND-D001"])

        m = P.processar()

        self.assertEqual(m["JA_PROCESSADAS_IGNORADAS"], 1)
        self.assertEqual(m["ENFILEIRADAS"], 1)
        # D001 não deve estar no ledger (nunca processado pela ponte)
        self.assertNotIn("CAND-D001", self._ledger_ids())
        self.assertIn("CAND-D002", self._ledger_ids())

    def test_ja_no_curator_nao_reenfileirada(self):
        """Candidata já no curator não ganha nova tarefa na fila."""
        self._porta([self._cand("CAND-E001", "CIENCIA")])
        self._caract(["CAND-E001"])

        m = P.processar()

        self.assertEqual(m["TAREFAS_CRIADAS"], 0)
        self.assertEqual(self._queue_total(), 0)


# ---------------------------------------------------------------------------
# T3 — Social → POLICY_BLOCK/CAPABILITY_BLOCK, NÃO na fila
# ---------------------------------------------------------------------------
class T3_SociaisBarradas(Isolada):

    def test_linkedin_vai_para_policy_block(self):
        self._porta([self._cand("CAND-F001", "LINKEDIN")])

        m = P.processar()

        self.assertEqual(m["CLASSIFICADAS_BARRADAS"], 1)
        self.assertEqual(m["SOCIAIS_ENFILEIRADAS"], 0)
        self.assertEqual(m["TAREFAS_CRIADAS"], 0)
        self.assertEqual(self._queue_total(), 0)
        self.assertEqual(LC.estado_de("CAND-F001"), LC.POLICY_BLOCK)

    def test_instagram_vai_para_policy_block(self):
        self._porta([self._cand("CAND-G001", "INSTAGRAM")])

        m = P.processar()

        self.assertEqual(m["CLASSIFICADAS_BARRADAS"], 1)
        self.assertEqual(m["SOCIAIS_ENFILEIRADAS"], 0)
        self.assertEqual(self._queue_total(), 0)
        self.assertEqual(LC.estado_de("CAND-G001"), LC.POLICY_BLOCK)

    def test_facebook_vai_para_capability_block(self):
        self._porta([self._cand("CAND-H001", "FACEBOOK")])

        m = P.processar()

        self.assertEqual(m["CLASSIFICADAS_BARRADAS"], 1)
        self.assertEqual(m["SOCIAIS_ENFILEIRADAS"], 0)
        self.assertEqual(self._queue_total(), 0)
        self.assertEqual(LC.estado_de("CAND-H001"), LC.CAPABILITY_BLOCK)

    def test_porta_marca_social_proibida_como_policy_block(self):
        """D15: a porta fica com ESTADO=POLICY_BLOCK (nao RECUSADA), o motivo no
        campo do bloqueio e a prova = o trecho dos termos, com endereco e data."""
        self._porta([self._cand("CAND-I001", "LINKEDIN")])

        P.processar()

        doc = FN.carregar()
        c = next(x for x in doc["CANDIDATAS"] if x["CANDIDATA_ID"] == "CAND-I001")
        self.assertEqual(c["ESTADO"], "POLICY_BLOCK")
        self.assertIn("POLICY_BLOCK", doc["ESTADOS"])
        self.assertFalse(c.get("MOTIVO_DA_RECUSA"))
        self.assertIn("LINKEDIN_POLICY", c["MOTIVO_DO_BLOQUEIO"])
        self.assertTrue(c["EVIDENCIA"].startswith("TERMOS https://www.linkedin.com/"))
        self.assertIn("scrape", c["EVIDENCIA_POLITICA"]["TRECHO"])

    def test_porta_marca_social_sem_capacidade_como_capability_block(self):
        """D13: sem capacidade nao e recusa. O Facebook fica CAPABILITY_BLOCK na
        porta (nao RECUSADA), com o motivo no campo do bloqueio."""
        self._porta([self._cand("CAND-I002", "FACEBOOK")])

        P.processar()

        doc = FN.carregar()
        c = next(x for x in doc["CANDIDATAS"] if x["CANDIDATA_ID"] == "CAND-I002")
        self.assertEqual(c["ESTADO"], "CAPABILITY_BLOCK")
        self.assertIn("CAPABILITY_BLOCK", c["ESTADO"])
        self.assertIn("CAPABILITY_BLOCK", doc["ESTADOS"])
        self.assertIn("FACEBOOK_CAPABILITY_BLOCK", c["MOTIVO_DO_BLOQUEIO"])
        self.assertFalse(c.get("MOTIVO_DA_RECUSA"))


# ---------------------------------------------------------------------------
# T4 — Tipo desconhecido → UNKNOWN, sem SOURCE_ID fabricado
# ---------------------------------------------------------------------------
class T4_TipoDesconhecido(Isolada):

    def test_tipo_inventado_vai_para_unknown(self):
        self._porta([self._cand("CAND-J001", "TIPO_QUE_NAO_EXISTE")])

        m = P.processar()

        self.assertEqual(m["UNKNOWN"], 1)
        self.assertEqual(m["TAREFAS_CRIADAS"], 0)
        self.assertEqual(m["CLASSIFICADAS_BARRADAS"], 0)
        # Lifecycle não tem entrada para este CANDIDATA_ID
        self.assertIsNone(LC.estado_de("CAND-J001"))

    def test_unknown_nao_fabrica_source_id(self):
        """Tipo desconhecido NÃO deve criar tarefa com SOURCE_ID inventado."""
        self._porta([self._cand("CAND-K001", "PLATAFORMA_NOVA")])

        P.processar()

        # A fila deve estar vazia
        self.assertEqual(self._queue_total(), 0)
        # O ledger regista UNKNOWN
        self.assertIn("CAND-K001", self._ledger_ids())
        ledger = P._carregar_ledger()
        self.assertEqual(ledger["PROCESSADAS"]["CAND-K001"]["DESTINO"], "UNKNOWN")


# ---------------------------------------------------------------------------
# T5 — Candidata já READY (SOURCE_ID no lifecycle) → não volta atrás
# ---------------------------------------------------------------------------
class T5_JaReady(Isolada):

    def test_candidata_com_source_id_no_curator_ignorada(self):
        """Candidata que chegou a READY passou pela caracterização — ignorada."""
        # Simular: CAND-L001 está no curator (CARACT) com SOURCE_ID pronto
        self._porta([self._cand("CAND-L001", "BASE_OFICIAL")])
        self._caract(["CAND-L001"])

        m = P.processar()

        self.assertEqual(m["JA_PROCESSADAS_IGNORADAS"], 1)
        self.assertEqual(m["TAREFAS_CRIADAS"], 0)

    def test_candidata_ready_nao_muda_estado_no_lifecycle(self):
        """Candidata com SOURCE_ID no lifecycle não tem novo registo."""
        # Registar um SOURCE_ID no lifecycle como READY (via caminho normal)
        LC.registar("IT-T5-999", LC.CANARY_PENDING, "pronto para canario")
        LC.registar("IT-T5-999", LC.READY_FOR_COLLECTION, "canario passou",
                    evidence_ref="EV-TEST")
        snap_antes = LC.snapshot().copy()

        # A ponte não deve tocar em nada
        self._porta([])
        P.processar()

        snap_depois = LC.snapshot()
        self.assertEqual(snap_antes, snap_depois,
                         "ponte não deve alterar lifecycle de fontes não candidatas")


# ---------------------------------------------------------------------------
# T6 — Interrupção a meio → estado coerente
# ---------------------------------------------------------------------------
class T6_InterrupcaoAMeio(Isolada):

    def test_falha_na_escrita_do_ledger_nao_deixa_estado_inconsistente(self):
        """Se _gravar_ledger falha, o ficheiro anterior fica intacto."""
        self._porta([
            self._cand("CAND-M001", "ORGANIZACAO"),
            self._cand("CAND-M002", "LINKEDIN"),
        ])

        # Primeira corrida normal
        P.processar()
        conteudo_antes = P.LEDGER.read_bytes()

        # Simular falha na segunda escrita
        original_gravar = P._gravar_ledger

        def gravar_com_falha(d):
            raise OSError("disco cheio — simulado")

        P._gravar_ledger = gravar_com_falha
        try:
            with self.assertRaises(OSError):
                P.processar()
        finally:
            P._gravar_ledger = original_gravar

        # O ledger não deve ter mudado
        self.assertEqual(P.LEDGER.read_bytes(), conteudo_antes,
                         "falha na escrita não deve corromper o ledger")


# ---------------------------------------------------------------------------
# T7 — Porta vazia → ponte corre sem rebentar
# ---------------------------------------------------------------------------
class T7_PortaVazia(Isolada):

    def test_porta_sem_candidatas_nao_rebenta(self):
        self._porta([])

        m = P.processar()

        self.assertEqual(m["CANDIDATAS_LIDAS"], 0)
        self.assertEqual(m["ENFILEIRADAS"], 0)
        self.assertEqual(m["CLASSIFICADAS_BARRADAS"], 0)
        self.assertEqual(m["TAREFAS_CRIADAS"], 0)
        self.assertEqual(m["SOCIAIS_ENFILEIRADAS"], 0)

    def test_porta_inexistente_nao_rebenta(self):
        """Porta sem ficheiro devolve lista vazia (comportamento de carregar())."""
        # Não criar o ficheiro — FN.carregar() devolve estrutura vazia
        m = P.processar()
        self.assertEqual(m["CANDIDATAS_LIDAS"], 0)


# ---------------------------------------------------------------------------
# T8 — Regra de negócio: SOCIAIS_ENFILEIRADAS deve ser sempre ZERO
# ---------------------------------------------------------------------------
class T8_SociaisNuncaEnfileiradas(Isolada):

    def test_mistura_de_tipos_nao_enfileira_sociais(self):
        """Com todos os tipos misturados, SOCIAIS_ENFILEIRADAS = 0."""
        self._porta([
            self._cand("CAND-N001", "LINKEDIN"),
            self._cand("CAND-N002", "INSTAGRAM"),
            self._cand("CAND-N003", "FACEBOOK"),
            self._cand("CAND-N004", "BASE_OFICIAL"),
            self._cand("CAND-N005", "ORGANIZACAO"),
            self._cand("CAND-N006", "YOUTUBE"),
        ])

        m = P.processar()

        self.assertEqual(m["SOCIAIS_ENFILEIRADAS"], 0)
        self.assertEqual(m["CLASSIFICADAS_BARRADAS"], 3)
        self.assertEqual(m["ENFILEIRADAS"], 3)

    def test_social_nao_aparece_na_fila(self):
        """LINKEDIN/INSTAGRAM/FACEBOOK não geram tarefas QUALIFY."""
        self._porta([
            self._cand("CAND-O001", "LINKEDIN"),
            self._cand("CAND-O002", "INSTAGRAM"),
            self._cand("CAND-O003", "FACEBOOK"),
        ])

        P.processar()

        self.assertEqual(self._queue_total(), 0,
                         "fontes sociais não podem estar na fila")


# ---------------------------------------------------------------------------
# T9 — QUALIFY não promove para READY (HARD STOP)
# ---------------------------------------------------------------------------
class T9_HardStopReady(Isolada):

    def test_ponte_nao_promove_para_ready(self):
        """A ponte nunca chama transição para READY_FOR_COLLECTION."""
        self._porta([
            self._cand("CAND-P001", "BASE_OFICIAL"),
            self._cand("CAND-P002", "CIENCIA"),
        ])

        P.processar()

        snap = LC.snapshot()
        for sid, estado in snap.items():
            self.assertNotEqual(
                estado, LC.READY_FOR_COLLECTION,
                f"{sid} foi promovido para READY pela ponte — proibido"
            )

    def test_ponte_nao_altera_ready_existentes(self):
        """Fontes já READY no lifecycle ficam intactas."""
        # Pôr uma fonte READY no lifecycle
        LC.registar("IT-T7-888", LC.CANARY_PENDING, "pronto")
        LC.registar("IT-T7-888", LC.READY_FOR_COLLECTION, "canario ok",
                    evidence_ref="EV-888")

        self._porta([self._cand("CAND-Q001", "ORGANIZACAO")])
        P.processar()

        self.assertEqual(LC.estado_de("IT-T7-888"), LC.READY_FOR_COLLECTION,
                         "ponte alterou estado READY de fonte existente")


if __name__ == "__main__":
    unittest.main(verbosity=2)


# ---------------------------------------------------------------------------
# D24 — perfis de PESSOAS do agro (dono real, 24/09 ~12:55, por escrito)
# Com prova oficial de identidade na NOTA: QUALIFY. Sem prova: POLICY_BLOCK com motivo.
# ---------------------------------------------------------------------------
_PROVA = "PROVA_IDENTIDADE=https://www.crea.gov.it/web/foreste-e-legno/-/pessoa-exemplo"


class TD24_PessoasComProva(Isolada):

    def _com_prova(self, cid, tipo):
        c = self._cand(cid, tipo)
        c["NOTA"] = "[P4b CAND-1] " + _PROVA
        return c

    def test_linkedin_de_pessoa_com_prova_d24_vai_a_qualify(self):
        self._porta([self._com_prova("CAND-D001", "LINKEDIN")])
        m = P.processar()
        self.assertEqual(m["PESSOAS_D24_ENFILEIRADAS"], 1)
        self.assertEqual(m["CLASSIFICADAS_BARRADAS"], 0)
        self.assertEqual(self._queue_total(), 1)
        self.assertNotEqual(LC.estado_de("CAND-D001"), LC.POLICY_BLOCK)
        c = FN.carregar()["CANDIDATAS"][0]
        self.assertEqual(c["ESTADO"], "EM_ANALISE")
        self.assertEqual(P._carregar_ledger()["PROCESSADAS"]["CAND-D001"]["MOTIVO"], P.MOTIVO_D24)

    def test_instagram_de_pessoa_com_prova_d24_vai_a_qualify(self):
        self._porta([self._com_prova("CAND-D002", "INSTAGRAM")])
        m = P.processar()
        self.assertEqual(m["PESSOAS_D24_ENFILEIRADAS"], 1)
        self.assertEqual(FN.carregar()["CANDIDATAS"][0]["ESTADO"], "EM_ANALISE")

    def test_sem_prova_continua_policy_block_e_todo_policy_block_tem_motivo(self):
        self._porta([self._cand("CAND-D003", "LINKEDIN"), self._cand("CAND-D004", "INSTAGRAM"),
                     self._com_prova("CAND-D005", "LINKEDIN")])
        P.processar()
        cs = {c["CANDIDATA_ID"]: c for c in FN.carregar()["CANDIDATAS"]}
        self.assertEqual(cs["CAND-D003"]["ESTADO"], "POLICY_BLOCK")
        self.assertEqual(cs["CAND-D004"]["ESTADO"], "POLICY_BLOCK")
        self.assertEqual(cs["CAND-D005"]["ESTADO"], "EM_ANALISE")
        for c in cs.values():
            if c["ESTADO"] == "POLICY_BLOCK":
                with self.subTest(candidata=c["CANDIDATA_ID"]):
                    self.assertTrue((c.get("MOTIVO_DO_BLOQUEIO") or "").strip(), "POLICY_BLOCK sem motivo")
                    self.assertEqual(LC.estado_de(c["CANDIDATA_ID"]), LC.POLICY_BLOCK)
        self.assertEqual(self._queue_total(), 1)

    def test_reavalia_uma_vez_os_que_a_ponte_antiga_bloqueou(self):
        self._porta([self._com_prova("CAND-D006", "LINKEDIN"), self._cand("CAND-D007", "LINKEDIN")])
        real = P.tem_prova_d24
        P.tem_prova_d24 = lambda c: False          # a ponte ANTES da D24
        try:
            P.processar()
        finally:
            P.tem_prova_d24 = real
        self.assertEqual(LC.estado_de("CAND-D006"), LC.POLICY_BLOCK)
        self.assertEqual(self._queue_total(), 0)

        m = P.processar()                           # a ponte COM a D24
        self.assertEqual(m["D24_REAVALIADAS"], 1)
        self.assertEqual(LC.estado_de("CAND-D006"), LC.QUALIFYING)
        self.assertEqual(LC.estado_de("CAND-D007"), LC.POLICY_BLOCK, "sem prova nao sai do bloqueio")
        cs = {c["CANDIDATA_ID"]: c for c in FN.carregar()["CANDIDATAS"]}
        self.assertEqual(cs["CAND-D006"]["ESTADO"], "EM_ANALISE")
        self.assertTrue(cs["CAND-D006"].get("BLOQUEIO_ANTERIOR"), "o bloqueio antigo fica guardado")
        self.assertEqual(cs["CAND-D006"].get("MOTIVO_DO_DESBLOQUEIO"), P.MOTIVO_D24)
        e = P._carregar_ledger()["PROCESSADAS"]["CAND-D006"]
        self.assertEqual((e["DESTINO"], e["DESTINO_ANTERIOR"]), ("QUALIFY", "POLICY_BLOCK"))
        self.assertEqual(self._queue_total(), 1)

        m = P.processar()                           # terceira corrida: nada de novo
        self.assertEqual(m["D24_REAVALIADAS"], 0)
        self.assertEqual(self._queue_total(), 1)

    def test_mutacao_sem_o_detector_um_perfil_sem_prova_escaparia(self):
        """RED TEAM: se o detector disser «tem prova» a tudo, o sem-prova sai do bloqueio.
        Prova que o teste do sem-prova acima MORDE: com a mutacao, a asserção dele falharia."""
        self._porta([self._cand("CAND-D008", "LINKEDIN")])
        real = P.tem_prova_d24
        P.tem_prova_d24 = lambda c: True
        try:
            P.processar()
        finally:
            P.tem_prova_d24 = real
        self.assertNotEqual(FN.carregar()["CANDIDATAS"][0]["ESTADO"], "POLICY_BLOCK")
