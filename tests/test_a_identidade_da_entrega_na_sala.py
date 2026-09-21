#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SALA SABE QUEM É CADA ENTREGA — e a entrega NÃO é o derivado.

    RUN != OBSERVATION != CONTENT != STORAGE OBJECT.
    SHA256 IDENTIFICA BYTES. STORAGE_PATH E ENDERECO. DERIVED E CONTEUDO POR RECEITA.
    A ENTREGA E «ESTA OBSERVACAO, ADMITIDA NESTA CORRIDA».

O QUE FOI MEDIDO (C-SALA-IDENTITY-V1, 2026-09-20, Sala operacional 54330)
--------------------------------------------------------------------------
A rota documental do orquestrador dava ao item o nome do DERIVADO
(`id = "derived:<DERIVED_ARTIFACT_ID>"`). O derivado tem grão CONTEÚDO POR
RECEITA (migration 022): duas observações dos mesmos bytes reencontram a
MESMA linha. Resultado na Sala: 6 pares de entregas, em corridas diferentes,
com observações diferentes (raw 164/289, 165/298, 168/302, 170/305, 175/313
e 7/26), todas com o mesmo `ITEM_ID`. A identidade da entrega estava
preservada pela chave `(run_id, ordem)` e por `raw_observation_id`; o que
estava emprestado era o NOME — e é pelo nome que `retirar()` endereça e que
um consumidor cunha `SIGNAL_ID`.

    COL-LAW-034: ITEM_ID != ARTIFACT_ID.
    UM NOME EMPRESTADO DO CONTEUDO E UMA CHAVE DUPLICADA COM AR DE CHAVE.

O QUE ESTA BATERIA PROVA SEM BANCO
----------------------------------
  1  retry da mesma admissão não duplica entrega (mesma impressão -> REUSED)
  2  nova observação sobre os mesmos bytes preserva identidade nova
  3  reutilizar o DERIVED não rouba a proveniência da nova observação
  4  SHA nunca vira observation id, nem item id, nesta rota
  5  `derived_id` já não substitui a identidade da entrega
  6  um consumidor incremental distingue JÁ PROCESSADO de ENTREGA NOVA

O QUE ELA SÓ PROVA COM A SALA OPERACIONAL AO ALCANCE (e diz quando não pode)
---------------------------------------------------------------------------
  7  as 29 entregas anteriores à BIG-COLLECTION-RELEASE continuam lá
  8  nenhuma das 17 entregas da BCR desapareceu

    UM TESTE QUE PRECISA DE BANCO E NÃO O TEM NÃO É UM TESTE QUE PASSA.
    É UM TESTE QUE NÃO CORREU — e sai como SKIP, à vista.
"""
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in (RAIZ, os.path.join(RAIZ, "admissao"), os.path.join(RAIZ, "orquestrador")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas                                            # noqa: E402,F401
import admissao                                            # noqa: E402
import sala_de_espera as espera                            # noqa: E402

ORQ = os.path.join(RAIZ, "orquestrador", "orquestrador.py")
SHA64 = re.compile(r"^[0-9a-f]{64}$")

# ── O QUE A DERIVAÇÃO ENTREGA À ESTRUTURAÇÃO, tal como `pela_estruturacao`
# o constrói (orquestrador.py, `feitos.append`). Os números são os REAIS da
# Sala operacional em 2026-09-20: o derivado 56 nasceu da observação 164 na
# corrida das 13:11 e foi REENCONTRADO pela observação 289 na corrida das
# 19:25 (BCR). Mesmos bytes (`PARENT_SHA256`), duas observações.
DERIVADO_56 = "9397764bcf72" + "0" * 52
ANTIGA = {"RAW_ASSET_ID": 164, "SOURCE_ID": "IT-T5-015",
          "DERIVED_ARTIFACT_ID": 56, "PARENT_SHA256": DERIVADO_56,
          "CAPTURED_AT": "2026-09-20T11:16:09.282Z",
          "ESTADO": "INSERTED",
          "TEXTO": "Iscrizioni aperte per il 6. Maria Ciaramella — ricerca universita"}
NOVA = dict(ANTIGA, RAW_ASSET_ID=289, ESTADO="REUSED",
            CAPTURED_AT="2026-09-20T19:25:15.633Z")
CORRIDA_ANTIGA = "IT-T5-2026-09-20-131125-8d14df1ddbe963fc"
CORRIDA_NOVA = "IT-T5-2026-09-20-192508-6a134eecf66c22a3"


def _fonte(caminho):
    with io.open(caminho, encoding="utf-8") as f:
        return f.read()


def _orq():
    import orquestrador as orq                               # noqa: PLC0415
    return orq


def _ready(estruturado, corrida, universo="T5"):
    """O caminho REAL até ao contrato de saída: item -> porta -> READY."""
    item = _orq().item_documental_para_a_porta(estruturado, source_id="IT-T5-015")
    d = admissao.decidir(item, universo, corrida=corrida)
    if d.resultado != admissao.SIM:
        raise AssertionError("a porta nao admitiu o item de bancada: %s / %s"
                             % (d.regra, d.motivo))
    return item, admissao.pronto_para_inteligencia(item, d)


class Bancada(unittest.TestCase):
    """Uma sala de ficheiro descartável por caso. A morada real não se toca."""

    def setUp(self):
        self.sala = tempfile.mkdtemp(prefix="sala-identidade-")
        self.addCleanup(shutil.rmtree, self.sala, ignore_errors=True)
        self._morada = espera.MORADA
        espera.MORADA = self.sala
        self.addCleanup(setattr, espera, "MORADA", self._morada)
        self._amb = dict(os.environ)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(self._amb)))
        os.environ.pop("SINTONIA_SALA_BACKEND", None)
        os.environ.pop("SINTONIA_SALA_DSN", None)


class T1_RetryDaMesmaAdmissaoNaoDuplica(Bancada):
    def test_a_mesma_corrida_com_o_mesmo_conteudo_da_REUSED_e_uma_so_entrega(self):
        _, pronta = _ready(NOVA, CORRIDA_NOVA)
        primeiro = espera.pousar(CORRIDA_NOVA, [pronta])
        segundo = espera.pousar(CORRIDA_NOVA, [pronta])
        self.assertEqual(primeiro["ESTADO"], espera.POUSOU)
        self.assertEqual(segundo["ESTADO"], espera.JA_ESTAVA)
        self.assertEqual(len(espera.ler(CORRIDA_NOVA)["ITENS"]), 1)

    def test_o_retry_tem_a_mesma_impressao_e_por_isso_nao_e_conflito(self):
        _, a = _ready(NOVA, CORRIDA_NOVA)
        _, b = _ready(NOVA, CORRIDA_NOVA)
        self.assertEqual(espera.impressao_da_corrida(CORRIDA_NOVA, [a]),
                         espera.impressao_da_corrida(CORRIDA_NOVA, [b]))

    def test_e_o_backend_canonico_decide_pela_mesma_impressao(self):
        """O Postgres não se corre aqui; o que se prova é que a decisão
        REUSED/CONFLICT dele é a MESMA chave — `corrida_sha256` — e não o
        `item_id`. Se alguém mudar a chave, isto morde."""
        fonte = _fonte(os.path.join(RAIZ, "admissao", "sala_de_espera.py"))
        self.assertIn("select corrida_sha256 into ja", fonte)
        self.assertIn("elsif ja = {sha} then", fonte)
        self.assertNotIn("where item_id = {", fonte)


class T2_NovaObservacaoPreservaIdentidadeNova(Bancada):
    def test_duas_observacoes_do_mesmo_derivado_sao_duas_entregas_com_nomes_diferentes(self):
        item_a, a = _ready(ANTIGA, CORRIDA_ANTIGA)
        item_b, b = _ready(NOVA, CORRIDA_NOVA)
        self.assertEqual(a["RAW_OBSERVATION_ID"], 164)
        self.assertEqual(b["RAW_OBSERVATION_ID"], 289)
        self.assertNotEqual(a["ITEM_ID"], b["ITEM_ID"])
        self.assertNotEqual(item_a["id"], item_b["id"])
        # e pousam como DUAS entregas, uma por corrida
        espera.pousar(CORRIDA_ANTIGA, [a])
        espera.pousar(CORRIDA_NOVA, [b])
        self.assertEqual(len(espera.ler(CORRIDA_ANTIGA)["ITENS"]), 1)
        self.assertEqual(len(espera.ler(CORRIDA_NOVA)["ITENS"]), 1)

    def test_a_nova_corrida_nao_e_confundida_com_retry_da_antiga(self):
        _, a = _ready(ANTIGA, CORRIDA_ANTIGA)
        _, b = _ready(NOVA, CORRIDA_NOVA)
        self.assertNotEqual(espera.impressao_da_corrida(CORRIDA_ANTIGA, [a]),
                            espera.impressao_da_corrida(CORRIDA_NOVA, [b]))

    def test_o_conteudo_nao_e_duplicado_para_preservar_a_identidade(self):
        """A identidade nova vive no NOME e na OBSERVAÇÃO — o texto e o pai
        dos bytes continuam os mesmos. Não se copia conteúdo para ter
        identidade."""
        _, a = _ready(ANTIGA, CORRIDA_ANTIGA)
        _, b = _ready(NOVA, CORRIDA_NOVA)
        self.assertEqual(a["TEXTO"], b["TEXTO"])
        self.assertEqual(a["SOURCE_ID"], b["SOURCE_ID"])


class T3_ReutilizarODerivedNaoRoubaAProveniencia(Bancada):
    def test_a_observacao_da_entrega_nova_e_a_nova_e_nunca_a_do_derivado(self):
        item, pronta = _ready(NOVA, CORRIDA_NOVA)
        # O derivado 56 nasceu da observação 164. A entrega nova veio da 289.
        self.assertEqual(item["raw_asset_id"], 289)
        self.assertEqual(pronta["RAW_OBSERVATION_ID"], 289)
        self.assertNotEqual(pronta["RAW_OBSERVATION_ID"], 164)

    def test_o_reencontro_do_derivado_nao_muda_o_nome_da_entrega_antiga(self):
        _, a = _ready(ANTIGA, CORRIDA_ANTIGA)
        _, b = _ready(NOVA, CORRIDA_NOVA)
        self.assertNotIn(str(b["RAW_OBSERVATION_ID"]), a["ITEM_ID"])
        self.assertNotIn(str(a["RAW_OBSERVATION_ID"]), b["ITEM_ID"])


class T4_ShaNuncaViraObservationIdNemItemId(Bancada):
    def test_com_observacao_o_id_e_o_da_observacao_e_nao_um_sha(self):
        item, pronta = _ready(NOVA, CORRIDA_NOVA)
        for valor in (item["id"], pronta["ITEM_ID"], str(pronta["RAW_OBSERVATION_ID"])):
            self.assertIsNone(SHA64.match(valor), valor)
            self.assertNotIn(DERIVADO_56, valor)

    def test_sem_observacao_nao_se_fabrica_endereco_e_a_porta_recusa(self):
        """RAW_ASSET_ID ausente: nem sha, nem derivado, nem caminho servem de
        nome. O item chega sem `id`, a porta diz NAO_SEI por `identidade` e
        nada pousa — COL-LAW-034 em letra."""
        sem = dict(NOVA)
        sem.pop("RAW_ASSET_ID")
        item = _orq().item_documental_para_a_porta(sem, source_id="IT-T5-015")
        self.assertNotIn("id", item)
        self.assertIsNone(item.get("raw_asset_id"))
        d = admissao.decidir(item, "T5", corrida=CORRIDA_NOVA)
        self.assertEqual(d.resultado, admissao.NAO_SEI)
        self.assertEqual(d.regra, "identidade")
        with self.assertRaises(ValueError):
            admissao.pronto_para_inteligencia(item, d)

    def test_raw_observation_id_nunca_e_derivado_do_sha_pela_porta(self):
        item = {"id": "x-1", "texto": "Ensaio de campo com DOI",
                "source_id": "IT-T7-001", "fact_time": "2026-05-02",
                "parent_sha256": DERIVADO_56}
        d = admissao.decidir(item, "T5", corrida="R1")
        pronta = admissao.pronto_para_inteligencia(item, d)
        self.assertEqual(pronta["RAW_OBSERVATION_ID"], "NAO SEI")


class T5_DerivedIdNaoSubstituiAIdentidadeDaEntrega(Bancada):
    def test_o_item_ja_nao_se_chama_derived(self):
        item, pronta = _ready(NOVA, CORRIDA_NOVA)
        self.assertFalse(item["id"].startswith("derived:"), item["id"])
        self.assertFalse(pronta["ITEM_ID"].startswith("derived:"), pronta["ITEM_ID"])
        self.assertEqual(pronta["ITEM_ID"], "obs:289")

    def test_e_a_fonte_do_orquestrador_deixou_de_emprestar_o_nome(self):
        fonte = _fonte(ORQ)
        self.assertNotIn('"derived:%s"', fonte)
        self.assertIn('"obs:%s" % observacao', fonte)

    def test_dois_derivados_diferentes_da_mesma_observacao_seriam_a_mesma_entrega(self):
        """O sentido inverso, para que a regra não seja lida ao contrário:
        a identidade segue a OBSERVAÇÃO. Outra receita sobre a mesma
        observação não é outra entrega."""
        outra_receita = dict(NOVA, DERIVED_ARTIFACT_ID=999)
        item_a, _ = _ready(NOVA, CORRIDA_NOVA)
        item_b, _ = _ready(outra_receita, CORRIDA_NOVA)
        self.assertEqual(item_a["id"], item_b["id"])


class T6_ConsumidorIncrementalDistingueVelhoDeNovo(Bancada):
    def _duas(self):
        _, a = _ready(ANTIGA, CORRIDA_ANTIGA)
        _, b = _ready(NOVA, CORRIDA_NOVA)
        return a, b

    def test_a_chave_canonica_da_entrega_separa_as_duas(self):
        a, b = self._duas()
        chaves = {(x["CORRIDA"], x["RAW_OBSERVATION_ID"]) for x in (a, b)}
        self.assertEqual(len(chaves), 2)

    def test_e_o_nome_tambem_as_separa_agora(self):
        a, b = self._duas()
        self.assertEqual(len({x["ITEM_ID"] for x in (a, b)}), 2)

    def test_a_referencia_da_intelligence_e_distinta_sem_correr_nada(self):
        """`referencia_do_item` é função pura — não abre corrida nenhuma."""
        import corrida_da_inteligencia as intel                 # noqa: PLC0415
        a, b = self._duas()
        ra, rb = intel.referencia_do_item(a), intel.referencia_do_item(b)
        self.assertNotEqual(ra, rb)
        self.assertNotEqual(ra["ITEM_ID"], rb["ITEM_ID"])
        self.assertNotEqual(ra["RAW_OBSERVATION_ID"], rb["RAW_OBSERVATION_ID"])
        # e um SIGNAL cunhado por (corrida|ITEM_ID) já não colide
        def cunho(r):
            return hashlib.sha256(("IR-X|" + str(r["ITEM_ID"])).encode()).hexdigest()[:16]
        self.assertNotEqual(cunho(ra), cunho(rb))

    def test_o_derivado_sozinho_NAO_chega_para_distinguir_e_por_isso_nao_e_chave(self):
        """O contraste, escrito para que ninguém volte a chavear por
        derivado: as duas entregas partilham o mesmo texto e o mesmo pai."""
        a, b = self._duas()
        self.assertEqual(len({x["TEXTO"] for x in (a, b)}), 1)


# ═════════════════════════════════════════════════════════════════════════
# 7 · 8 — SÓ COM A SALA OPERACIONAL AO ALCANCE, E SÓ A LER
# ═════════════════════════════════════════════════════════════════════════
# As 46 entregas medidas em 2026-09-20 (29 anteriores + 17 da BCR), pela
# chave `(run_id, ordem)`, com o `item_id` e a observação que tinham no dia.
# A lista é FIXA de propósito: a Sala pode crescer; estas não podem sumir.
ENTREGAS_MEDIDAS = [
    ("XX-T3-2026-09-18-134205-772b57c43c0130fe", 0, "derived:1", 1, "ANTES"),
    ("XX-T3-2026-09-18-171909-b66be5e4276b76f7", 0, "derived:6", 7, "ANTES"),
    ("XX-T3-2026-09-18-171937-6f76511ca75100a5", 0, "derived:7", 9, "ANTES"),
    ("IT-T3-2026-09-19-234958-31fa5cf0b3c1cedc", 0, "derived:6", 26, "ANTES"),
    ("IT-T3-2026-09-20-110656-6e4ffc27a86c5269", 0, "derived:11", 36, "ANTES"),
    ("IT-T5-2026-09-20-111447-ff5fc4cbd0be96eb", 0, "derived:20", 76, "ANTES"),
    ("IT-T5-2026-09-20-111501-7e74df1e07242c23", 0, "derived:21", 77, "ANTES"),
    ("IT-T5-2026-09-20-111514-dab3a43d6cbff096", 0, "derived:22", 78, "ANTES"),
    ("IT-T5-2026-09-20-111527-7010244996e4f60d", 0, "derived:23", 79, "ANTES"),
    ("IT-T5-2026-09-20-111552-c60226342543877f", 0, "derived:24", 81, "ANTES"),
    ("IT-T5-2026-09-20-111612-d62f7e530872ae53", 0, "derived:25", 83, "ANTES"),
    ("IT-T5-2026-09-20-111637-925cca0288d7a725", 0, "derived:26", 85, "ANTES"),
    ("IT-T5-2026-09-20-111645-f9961800a1c6a1b5", 0, "derived:27", 86, "ANTES"),
    ("IT-T5-2026-09-20-111655-12e3ab07857fc48c", 0, "derived:28", 87, "ANTES"),
    ("IT-T5-2026-09-20-111716-60f046454a78601b", 0, "derived:29", 89, "ANTES"),
    ("IT-T5-2026-09-20-111757-3f5e69cf99a858d4", 0, "derived:30", 93, "ANTES"),
    ("IT-T5-2026-09-20-111833-300d63e8f5ad1547", 0, "derived:31", 96, "ANTES"),
    ("IT-T5-2026-09-20-131125-8d14df1ddbe963fc", 0, "derived:56", 164, "ANTES"),
    ("IT-T5-2026-09-20-131130-895a0314eae09400", 0, "derived:57", 165, "ANTES"),
    ("IT-T5-2026-09-20-131134-416d0d69a8c8e948", 0, "derived:58", 166, "ANTES"),
    ("IT-T5-2026-09-20-131138-25dca3fc1409d65d", 0, "derived:59", 167, "ANTES"),
    ("IT-T5-2026-09-20-131143-3373b6aaa2b3f10c", 0, "derived:60", 168, "ANTES"),
    ("IT-T5-2026-09-20-131154-4545d6b1e93089db", 0, "derived:61", 169, "ANTES"),
    ("IT-T5-2026-09-20-131200-68afc47009a79970", 0, "derived:62", 170, "ANTES"),
    ("IT-T5-2026-09-20-131205-10c1ea3a8c305043", 0, "derived:63", 171, "ANTES"),
    ("IT-T5-2026-09-20-131211-efd0f7c5d86970a4", 0, "derived:64", 173, "ANTES"),
    ("IT-T7-2026-09-20-131216-bde6d847dc5c70e1", 0, "derived:65", 174, "ANTES"),
    ("IT-T9-2026-09-20-131220-6701c875ad0307e8", 0, "derived:66", 175, "ANTES"),
    ("IT-T5-2026-09-20-144624-321fa3994d5fb839", 0, "derived:87", 200, "ANTES"),
    ("IT-T5-2026-09-20-192508-6a134eecf66c22a3", 0, "derived:56", 289, "BCR"),
    ("IT-T5-2026-09-20-192532-9aac8c847b3a9086", 0, "derived:126", 291, "BCR"),
    ("IT-T5-2026-09-20-192653-3059d44865de3771", 0, "derived:57", 298, "BCR"),
    ("IT-T5-2026-09-20-192708-c824dabebd7f3b61", 0, "derived:128", 299, "BCR"),
    ("IT-T5-2026-09-20-192734-8b9ef001a8833894", 0, "derived:129", 301, "BCR"),
    ("IT-T5-2026-09-20-192753-50b3827b5360b47a", 0, "derived:60", 302, "BCR"),
    ("IT-T5-2026-09-20-192820-3218c890fbdc53ea", 0, "derived:130", 304, "BCR"),
    ("IT-T5-2026-09-20-192843-147a52f842d703b2", 0, "derived:62", 305, "BCR"),
    ("IT-T5-2026-09-20-192855-65f932fb8ca2d940", 0, "derived:131", 306, "BCR"),
    ("IT-T5-2026-09-20-192906-7ab07ae1f5ec1c43", 0, "derived:132", 307, "BCR"),
    ("IT-T5-2026-09-20-192919-8e956ede5a0f00ca", 0, "derived:133", 308, "BCR"),
    ("IT-T7-2026-09-20-192932-34df68b28dff931e", 0, "derived:134", 309, "BCR"),
    ("IT-T9-2026-09-20-193058-ff56ab6f5e532dc1", 0, "derived:66", 313, "BCR"),
    ("IT-T5-2026-09-20-193605-e847862f7bea0834", 0, "derived:142", 334, "BCR"),
    ("IT-T5-2026-09-20-193632-9cea5353f98faba7", 0, "derived:143", 335, "BCR"),
    ("IT-T7-2026-09-20-193746-81a5352c4a43f429", 0, "derived:147", 339, "BCR"),
    ("IT-T7-2026-09-20-193826-d16655f6c9c2f725", 0, "derived:149", 341, "BCR")
]


def _dsn_operacional():
    v = (os.environ.get("SINTONIA_SALA_DSN") or "").strip()
    if v:
        return v
    caminho = os.path.join(os.path.expanduser("~"), "sintonia-sala-italia", "SALA_DSN.txt")
    if os.path.isfile(caminho):
        return _fonte(caminho).strip()
    return None


def _consultar(sql):
    """Só leitura. Opções primeiro, DSN por último (tests/test_psql_argv.py)."""
    from guarda.cliente_postgres import resolver_psql, ClientePostgresAusente  # noqa: PLC0415
    dsn = _dsn_operacional()
    if not dsn:
        raise unittest.SkipTest("Sala operacional fora de alcance: sem DSN "
                                "(SINTONIA_SALA_DSN ou ~/sintonia-sala-italia/SALA_DSN.txt)")
    try:
        psql = resolver_psql()
    except ClientePostgresAusente as ex:
        raise unittest.SkipTest("Sala operacional fora de alcance: %s" % ex)
    r = subprocess.run([psql, "-X", "-w", "-q", "-A", "-t", "-F", "\x1f",
                        "-v", "ON_ERROR_STOP=1", "-f", "-", dsn],
                       input=sql, capture_output=True, text=True, encoding="utf-8",
                       timeout=60)
    if r.returncode != 0:
        raise unittest.SkipTest("Sala operacional nao respondeu (psql rc=%d)" % r.returncode)
    return [l.split("\x1f") for l in r.stdout.replace("\r", "").split("\n") if l.strip()]


class T7_T8_NenhumaEntregaLegitimaDesaparece(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.linhas = {(r, int(o)): (i, None if raw == "" else int(raw))
                      for r, o, i, raw in _consultar(
                          "select run_id, ordem, item_id, coalesce(raw_observation_id::text,'') "
                          "from public.sala_de_espera")}

    def _presentes(self, epoca):
        esperadas = [e for e in ENTREGAS_MEDIDAS if e[4] == epoca]
        faltam = [(r, o) for r, o, _, _, _ in esperadas if (r, o) not in self.linhas]
        return esperadas, faltam

    def test_7_as_29_anteriores_a_BCR_continuam_na_sala(self):
        esperadas, faltam = self._presentes("ANTES")
        self.assertEqual(len(esperadas), 29)
        self.assertEqual(faltam, [])

    def test_8_nenhuma_das_17_da_BCR_desapareceu(self):
        esperadas, faltam = self._presentes("BCR")
        self.assertEqual(len(esperadas), 17)
        self.assertEqual(faltam, [])

    def test_a_observacao_de_cada_entrega_medida_nao_foi_reescrita(self):
        """Reconciliar não é reescrever: a observação que cada linha apontava
        no dia continua a ser a mesma. A proveniência histórica preserva-se."""
        for r, o, _, raw, _ in ENTREGAS_MEDIDAS:
            self.assertEqual(self.linhas[(r, o)][1], raw, (r, o))

    def test_o_nome_historico_fica_como_evidencia_e_nao_se_apaga(self):
        """As 6 colisões de nome são evidência do defeito; não se corrigem
        apagando nem reescrevendo linha. O que muda é o que entra daqui em
        diante."""
        for r, o, item, _, _ in ENTREGAS_MEDIDAS:
            self.assertEqual(self.linhas[(r, o)][0], item, (r, o))


if __name__ == "__main__":
    unittest.main()
