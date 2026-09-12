#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS GUARDAS DE `G-RAW-01` — a etapa RAW fala, e fala a verdade.

A prova de VALOR vive em `provas/o_raw_fala.py`, contra PostgreSQL real: é lá
que se lê do banco o que aterrou. Aqui ficam as guardas que não precisam de
banco, e uma que confere que aquela prova continua a ler o banco.

    UMA GUARDA DE TEXTO CONFERE O QUE ESTA ESCRITO.
    SO UMA LEITURA DO BANCO CONFERE O QUE ATERROU.
    E NENHUMA DAS DUAS SUBSTITUI A OUTRA.
"""
import ast
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
if os.path.join(RAIZ, "coleta") not in sys.path:
    sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import _gavetas                          # noqa: E402,F401
import rastro_da_coleta as rastro        # noqa: E402
import telemetria as tel                 # noqa: E402
from coleta import ingresso as ing       # noqa: E402

PORTA = os.path.join(RAIZ, "coleta", "ingresso.py")
PROVA = os.path.join(RAIZ, "provas", "o_raw_fala.py")
ROTA = os.path.join(RAIZ, "provas", "a_rota_m2_atravessa.py")
MIGRATION = os.path.join(RAIZ, "supabase", "migrations",
                         "028_a_etapa_raw_aponta_para_a_observacao.sql")


def _fonte(caminho):
    return io.open(caminho, encoding="utf-8").read()


class NaoSeInventouUmSegundoLivro(unittest.TestCase):
    """O dono do rastro já existia, e o vocabulário já tinha a etapa."""

    def test_a_etapa_RAW_ja_estava_no_vocabulario_canonico(self):
        self.assertIn("RAW", tel.ETAPAS_DA_COLETA)

    def test_a_porta_escreve_pelo_dono_do_rastro_e_nao_por_SQL_proprio(self):
        arv = ast.parse(_fonte(PORTA))
        chama_dono = any(
            isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "registrar"
            for n in ast.walk(arv))
        self.assertTrue(chama_dono, "a porta deixou de usar o dono do rastro")
        for proibido in ("insert into public.etapa_da_corrida",
                         "raw-ledger", "raw-events", "raw_telemetry"):
            self.assertNotIn(proibido, _fonte(PORTA).lower(),
                             "nasceu um segundo livro: %s" % proibido)


class AOrdEmEAPROVA(unittest.TestCase):
    """O rastro fala DEPOIS de a observação existir, e nunca antes."""

    def _corpo_do_receber(self):
        for no in ast.walk(ast.parse(_fonte(PORTA))):
            if isinstance(no, ast.FunctionDef) and no.name == "receber":
                return no
        return None

    def test_o_rastro_e_emitido_DEPOIS_de_preservar(self):
        """⚠️ EMITIR ANTES DO INSERT DARIA UM SUCESSO SEM SUJEITO."""
        corpo = self._corpo_do_receber()
        self.assertIsNotNone(corpo, "`receber` desapareceu da porta")
        linha_preservar = linha_falar = None
        for no in ast.walk(corpo):
            if not isinstance(no, ast.Call):
                continue
            nome = getattr(no.func, "id", None) or getattr(no.func, "attr", None)
            if nome == "preservar":
                linha_preservar = no.lineno
            if nome == "falar_do_raw":
                linha_falar = no.lineno
        self.assertIsNotNone(linha_preservar, "a porta deixou de preservar")
        self.assertIsNotNone(linha_falar, "a porta deixou de contar a passagem")
        self.assertLess(linha_preservar, linha_falar,
                        "o rastro passou a ser emitido ANTES da persistencia")


class AFONTENaoSeInventa(unittest.TestCase):
    """`SOURCE_ID` ausente fica ausente. Nada o deduz."""

    def test_a_confissao_e_o_vazio_nao_sao_identidade(self):
        for v in (None, "", "   ", "NAO SEI", "NAO_SE_APLICA"):
            with self.subTest(valor=v):
                self.assertIsNone(ing._fonte_provada([{"SOURCE_ID": v}]))

    def test_o_caminho_o_slug_e_o_sha_nao_viram_fonte(self):
        sha = "f" * 64
        for item in ({"STORAGE_LOCATION":
                      "data/collection-store/italy/IT-T2-002/x.pdf"},
                     {"SOURCE_SLUG": "it-t2-002"},
                     {"SHA256": sha},
                     {"NAME": "IT-T2-002.pdf"}):
            with self.subTest(item=sorted(item)):
                self.assertIsNone(ing._fonte_provada([item]))

    def test_duas_fontes_na_mesma_passagem_nao_viram_uma(self):
        self.assertIsNone(ing._fonte_provada([{"SOURCE_ID": "IT-T2-002"},
                                              {"SOURCE_ID": "IT-T2-009"}]))

    def test_e_UMA_fonte_provada_e_usada(self):
        self.assertEqual("IT-T2-002",
                         ing._fonte_provada([{"SOURCE_ID": "IT-T2-002"},
                                             {"SOURCE_ID": "IT-T2-002"}]))


class AOBSERVACAONaoSeEmpresta(unittest.TestCase):
    """A linha só nomeia a observação quando produziu exatamente uma."""

    def test_zero_e_N_maior_que_um_nao_nomeiam_nenhuma(self):
        for obs in ([], [{"RAW_OBSERVATION_ID": 1}, {"RAW_OBSERVATION_ID": 2}]):
            with self.subTest(n=len(obs)):
                self.assertIsNone(ing._a_observacao_desta_passagem(
                    {"RAW_OBSERVATIONS": obs}))

    def test_uma_so_e_nomeada_e_e_o_id_do_banco(self):
        self.assertEqual(7, ing._a_observacao_desta_passagem(
            {"RAW_OBSERVATIONS": [{"RAW_OBSERVATION_ID": 7}]}))

    def test_outra_etapa_nao_assina_a_observacao_do_RAW(self):
        """Apontar para o artefato de outra etapa é assinar o trabalho dela."""
        for etapa in ("DERIVED", "STRUCTURED", "ADMISSION"):
            with self.subTest(etapa=etapa):
                with self.assertRaises(ValueError):
                    rastro.registrar(None, run_id="R", etapa=etapa,
                                     estado="PASS", raw_asset_id=1)


class AContaFecha(unittest.TestCase):
    """⚠️ A MESMA OBSERVACAO CAIA EM DOIS BALDES, E A CONTA ABRIA UM BURACO.

    `RAW_OBSERVATIONS` traz as confirmadas DESTA corrida, e num reencontro a
    linha reaproveitada aparece nas duas listas. Somar as duas dava
    `accounted = 2` para uma entrada de 1, e o banco devolvia
    `unaccounted_input = -1`: um buraco NEGATIVO, inventado pela contagem.
    """

    def _baldes(self, confirmadas, reused, recusados=0, porta=0, entrada=1):
        return ing._baldes_do_raw(
            {"RAW_OBSERVATIONS": [{"RAW_OBSERVATION_ID": i + 1}
                                  for i in range(confirmadas)],
             "JA_EXISTIA_NO_BANCO": {"REUSED_METADATA": reused},
             "RECUSADOS_SEM_IDENTIDADE": [{}] * recusados},
            porta, entrada)

    def test_o_reencontro_nao_conta_duas_vezes(self):
        b = self._baldes(confirmadas=1, reused=1)
        self.assertEqual(0, b["passed"])
        self.assertEqual(1, b["reused"])
        self.assertEqual(1, b["passed"] + b["reused"] + b["rejected"]
                         + b["unknown"])

    def test_a_observacao_nova_conta_se_como_passed(self):
        b = self._baldes(confirmadas=1, reused=0)
        self.assertEqual(1, b["passed"])
        self.assertEqual(0, b["reused"])

    def test_a_conta_fecha_em_todos_os_arranjos(self):
        for conf, reu, rec, porta, ent in ((1, 0, 0, 0, 1), (1, 1, 0, 0, 1),
                                           (0, 0, 1, 0, 1), (0, 0, 0, 1, 1),
                                           (2, 1, 1, 0, 4), (0, 0, 0, 0, 3)):
            with self.subTest(entrada=ent):
                b = self._baldes(conf, reu, rec, porta, ent)
                total = (b["passed"] + b["reused"] + b["rejected"]
                         + b["unknown"])
                self.assertLessEqual(total, ent,
                                     "a contagem passou a entrada: buraco"
                                     " negativo")


class AMigrationDizOQueFazEComQueTrava(unittest.TestCase):
    """Uma coluna na tabela canónica — e não uma tabela nova."""

    def test_a_migration_existe_e_altera_a_tabela_do_rastro(self):
        s = _fonte(MIGRATION)
        self.assertIn("alter table public.etapa_da_corrida", s)
        self.assertIn("raw_asset_id bigint", s)
        self.assertIn("references public.raw_asset(id)", s)

    def test_e_nao_criou_tabela_nenhuma(self):
        s = _fonte(MIGRATION).lower()
        self.assertNotIn("create table", s,
                         "a 028 criou um segundo livro em vez de uma coluna")

    def test_a_trava_impede_outra_etapa_de_nomear_a_observacao(self):
        self.assertIn("so_o_raw_nomeia_a_observacao", _fonte(MIGRATION))


class AProvaDeVALORContinuaALerOBanco(unittest.TestCase):
    """⚠️ UM TESTE QUE SO OLHA PARA O CODIGO NAO VE O QUE ATERROU."""

    def test_a_prova_le_o_raw_asset_e_a_etapa_da_corrida(self):
        s = _fonte(PROVA)
        self.assertIn("public.raw_asset", s)
        self.assertIn("public.etapa_da_corrida", s)

    def test_e_ela_nao_se_salta_a_si_propria(self):
        """SKIP != PASS. Uma prova que se auto-salta nao prova nada."""
        self.assertNotIn("skipTest", _fonte(PROVA))

    def test_a_prova_da_estrada_usa_a_FRONTEIRA_e_nao_um_rastro_a_mao(self):
        """⚠️ UM FIXTURE QUE EMITE O QUE A PRODUCAO NUNCA EMITE MEDE O FIXTURE.

        A prova da estrada canónica não escreve a passagem do RAW: ela chama a
        MESMA função que `coleta/ingresso.receber()` chama, com o recibo REAL
        que `preservar()` devolveu.
        """
        arv = ast.parse(_fonte(ROTA))
        chama_fronteira = False
        for no in ast.walk(arv):
            if not isinstance(no, ast.Call):
                continue
            if getattr(no.func, "attr", None) == "falar_do_raw":
                chama_fronteira = True
            if getattr(no.func, "attr", None) == "registrar":
                for kw in no.keywords:
                    if kw.arg == "etapa" and isinstance(kw.value, ast.Constant):
                        self.assertNotEqual(
                            "RAW", kw.value.value,
                            "a prova passou a escrever o rastro do RAW a mao")
        self.assertTrue(chama_fronteira,
                        "a prova da estrada deixou de contar a passagem do RAW"
                        " pela fronteira de producao")


class OGapFechouEFicouNaLista(unittest.TestCase):
    """Um buraco que fecha sai da lista dos buracos — e a prova fica."""

    def test_o_gap_do_raw_deixou_de_ser_declarado(self):
        from coleta import derivacao_forward as df
        self.assertNotIn("RAW_FORWARD_NAO_EMITE", {g[0] for g in df.GAPS})

    def test_a_observabilidade_e_MEDIDA_e_nao_escrita_a_mao(self):
        """⚠️ UM CENSO ESCRITO A MAO MEDE QUEM O ESCREVEU."""
        import importlib.util as u
        sp = u.spec_from_file_location(
            "portoes", os.path.join(RAIZ, "provas",
                                    "os_portoes_da_collection.py"))
        m = u.module_from_spec(sp)
        sp.loader.exec_module(m)
        obs = m.observabilidade()
        self.assertIn("RAW", obs["ETAPAS_QUE_FALAM"])
        self.assertNotIn("RAW", obs["ETAPAS_MUDAS"])
        self.assertIn("AST", obs["COMO_FOI_MEDIDO"])

    def test_e_o_medidor_le_chamadas_e_nao_comentarios(self):
        """Um comentario que nomeie uma etapa nao e uma chamada (§60)."""
        import importlib.util as u
        sp = u.spec_from_file_location(
            "portoes", os.path.join(RAIZ, "provas",
                                    "os_portoes_da_collection.py"))
        m = u.module_from_spec(sp)
        sp.loader.exec_module(m)
        self.assertIn("ast", _fonte(os.path.join(
            RAIZ, "provas", "os_portoes_da_collection.py")))
        self.assertNotIn("READY", m.observabilidade()["ETAPAS_QUE_FALAM"],
                         "READY nao e emitido por ninguem, e o medidor"
                         " diz que e")


if __name__ == "__main__":
    unittest.main()
