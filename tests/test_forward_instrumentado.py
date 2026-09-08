#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FRONTEIRA FORWARD, E A LEI QUE IMPEDE A CADEIA DE PARECER FECHADA.

    LEGACY_REPLAY_INSTRUMENTED  !=  CANONICAL_FORWARD_INSTRUMENTED.
    DERIVED STORED              !=  READY.

Estes testes correm SEM banco: eles medem o desenho — quem emite o que, e o
que a lei recusa. A prova contra PostgreSQL 16 real vive noutro sitio, e nao se
finge banco aqui: `provas/o_forward_conta_se.py`.

⚠️ O QUE ESTE FICHEIRO NAO REPETE.
Duas sessoes fizeram O9 e O10R em paralelo nesta branch. O REPLAY LEGADO — que
`correr()` emite, que ele deixou de inventar `READY`, e que a identidade ficou
NULA — ja tem prova propria em `tests/test_o10r_a_verdade_dos_nomes.py` e
`tests/test_o9_caminho_instrumentado.py`. Repetir aqui seria uma segunda verdade
sobre a mesma pergunta. O que fica e o que so existe deste lado: a FRONTEIRA
FORWARD, e a lei de READY como funcao reutilizavel.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import _gavetas  # noqa: E402,F401
import banco_no_seco as bs              # noqa: E402
import derivacao_forward as fwd         # noqa: E402
import diagnostico as dg                # noqa: E402
import falhas                           # noqa: E402
import rastro_da_coleta as rastro       # noqa: E402
import telemetria as tel                # noqa: E402
from guarda.preservar_coleta import ArmazemDeMentira    # noqa: E402
from guarda import preservar_derivado as pd             # noqa: E402


def _v(linha, chave):
    b = linha.get(chave)
    return None if b is None else b.split("::")[0].strip().strip("'")


def _n(linha, chave):
    try:
        return int(_v(linha, chave))
    except (TypeError, ValueError):
        return 0


class ALeiDoReady(unittest.TestCase):
    """READY e um VEREDITO, e nao uma persistencia."""

    FORWARD = [{"ETAPA": "RAW", "ESTADO": "PASS"},
               {"ETAPA": "DERIVED", "ESTADO": "PASS"}]

    def test_ready_pass_sem_admission_e_apanhado(self):
        v = tel.ready_sem_quem_assine(
            self.FORWARD + [{"ETAPA": "READY", "ESTADO": "PASS"}])
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0]["FALTA"], "ADMISSION")
        self.assertEqual(v[0]["DIAGNOSTIC_CODE"], dg.ADMISSION_NOT_CONNECTED)

    def test_admission_que_nao_correu_nao_assina_nada(self):
        """⚠️ STAGE EXISTS IN VOCABULARY != STAGE RAN.

        Uma linha `ADMISSION NOT_RUN` na corrida NAO e a admissao ter
        acontecido. Se bastasse a etapa aparecer, a lei seria contornavel com
        uma linha vazia — que e a maneira mais barata de fingir uma cadeia."""
        for estado_morto in ("NOT_RUN", "SKIPPED", "NOT_APPLICABLE", "FAIL"):
            v = tel.ready_sem_quem_assine(
                self.FORWARD + [{"ETAPA": "ADMISSION", "ESTADO": estado_morto},
                                {"ETAPA": "READY", "ESTADO": "PASS"}])
            self.assertEqual(len(v), 1, estado_morto)

    def test_a_cadeia_honesta_passa(self):
        """Uma lei que reprovasse sempre seria ruido, e ruido ensina a ignorar."""
        self.assertEqual(tel.ready_sem_quem_assine(
            self.FORWARD + [{"ETAPA": "ADMISSION", "ESTADO": "PASS"},
                            {"ETAPA": "READY", "ESTADO": "PASS"}]), [])

    def test_terminar_em_derived_nao_e_violacao(self):
        self.assertEqual(tel.ready_sem_quem_assine(self.FORWARD), [])

    def test_o_dono_das_etapas_e_o_contrato_e_o_writer_importa_o(self):
        self.assertIs(rastro.ETAPAS, tel.ETAPAS_DA_COLETA)


class AFronteiraForward(unittest.TestCase):
    """`coleta/derivacao_forward.py` — o que ela emite, e por que so isso."""

    def _correr(self, resultados, banco=None):
        """Um `derivar` de mentira: a fronteira e o que esta a ser medido."""
        fila = list(resultados)

        def derivar(raw_asset_id, pdf, armazem, memoria, relogio=None):
            return fila.pop(0)

        unidades = [{"RAW_ASSET_ID": i + 1, "PDF": "x%d.pdf" % i}
                    for i in range(len(resultados))]
        return fwd.correr(unidades, banco_do_rastro=banco, run_id="RUN-X",
                          armazem=ArmazemDeMentira(), memoria=None,
                          source_id="IT-T2-002", route_class_id="RC-1",
                          derivar=derivar)

    def test_emite_uma_so_etapa_e_ela_e_derived(self):
        banco = bs.BancoNoSeco()
        self._correr([{"ESTADO": pd.INSERTED,
                       "LINHA_ESCRITA": {"storage_path": "a.txt"}}], banco)
        self.assertEqual(set(banco.por_etapa()), {"DERIVED"})
        self.assertEqual(_v(banco.linhas[0], "edge_from"), "RAW")

    def test_nao_fala_pela_etapa_raw_que_e_de_outro_dono(self):
        """Ler a linha de outro nao e ter corrido a etapa dele."""
        banco = bs.BancoNoSeco()
        self._correr([{"ESTADO": pd.INSERTED,
                       "LINHA_ESCRITA": {"storage_path": "a.txt"}}], banco)
        self.assertNotIn("RAW", banco.por_etapa())

    def test_reused_nao_e_rejected(self):
        r = self._correr([{"ESTADO": pd.REUSED,
                           "LINHA_EXISTENTE": {"storage_path": "a.txt"}}])
        self.assertEqual(r["BALDES"]["REUSED"], 1)
        self.assertEqual(r["BALDES"]["REJECTED"], 0)

    def test_sem_camada_de_texto_e_rejected_e_nao_error(self):
        """O PDF e fotografia de papel. Propriedade DELE — a ferramenta nao
        falhou."""
        import artefato as art
        r = self._correr([{"ESTADO": "SEM_DERIVADO",
                           "MOTIVO_DO_EXECUTOR": art.TEXT_LAYER_ABSENT}])
        self.assertEqual(r["BALDES"]["REJECTED"], 1)
        self.assertEqual(r["BALDES"]["ERROR"], 0)
        self.assertEqual(r["ESTADO_DA_ETAPA"], rastro.PASS)

    def test_ferramenta_que_falha_e_error_e_nao_recusa(self):
        import artefato as art
        r = self._correr([{"ESTADO": "SEM_DERIVADO",
                           "MOTIVO_DO_EXECUTOR": art.EXTRACTION_ERROR}])
        self.assertEqual(r["BALDES"]["ERROR"], 1)
        self.assertEqual(r["ESTADO_DA_ETAPA"], rastro.FAIL)

    def test_um_estado_que_ninguem_mapeou_e_unknown_e_nao_zero(self):
        """⚠️ UNKNOWN != ZERO. Um estado novo do writer nao pode sumir na
        contagem so por ninguem ter vindo dizer por que porta ele sai."""
        r = self._correr([{"ESTADO": "UM_ESTADO_QUE_AINDA_NAO_EXISTE"}])
        self.assertEqual(r["BALDES"]["UNKNOWN"], 1)
        self.assertEqual(r["ESTADO_DA_ETAPA"], rastro.FAIL)

    def test_a_conta_fecha_com_a_mistura_toda(self):
        import artefato as art
        banco = bs.BancoNoSeco()
        self._correr([
            {"ESTADO": pd.INSERTED, "LINHA_ESCRITA": {"storage_path": "a.txt"}},
            {"ESTADO": pd.REUSED, "LINHA_EXISTENTE": {"storage_path": "b.txt"}},
            {"ESTADO": "SEM_DERIVADO",
             "MOTIVO_DO_EXECUTOR": art.TEXT_LAYER_ABSENT},
            {"ESTADO": pd.RAW_PARENT_NOT_FOUND, "PORQUE": "sem pai"},
        ], banco)
        self.assertEqual(banco.sem_explicacao(), [])
        der = banco.por_etapa()["DERIVED"]
        self.assertEqual(_n(der, "input_count"), 4)
        self.assertEqual(der["_ACCOUNTED"], 4)

    def test_o_estado_canonico_vem_de_falhas_e_nao_daqui(self):
        banco = bs.BancoNoSeco()
        self._correr([{"ESTADO": pd.ERROR, "PORQUE": "rebentou"}], banco)
        self.assertIn(_v(banco.linhas[0], "canonical_state"), falhas.ESTADOS)

    def test_o_estado_canonico_e_conferido_pelo_WRITER_e_nao_por_esta_peca(self):
        """⚠️ UM CONCEITO, UM DONO — e a trava vive no dono do rastro.

        A primeira versao desta fronteira conferia o nome ela propria. Mas a
        trava chegou entretanto a `rastro.registrar`, pela outra sessao que fez
        O9 em paralelo, depois de um emissor ter escrito `canonical_state=ERROR`
        — que e um DESTINO DE ITEM e nao um estado de falha. Duas travas sobre a
        mesma regra seriam dois donos da mesma pergunta."""
        with self.assertRaises(AssertionError):
            rastro.registrar(bs.BancoNoSeco(), run_id="R", etapa="DERIVED",
                             estado=rastro.PASS,
                             canonical_state="UM_ESTADO_QUE_FALHAS_NAO_CONHECE")

    def test_sem_banco_do_rastro_nao_emite_e_deriva_na_mesma(self):
        """OBSERVABILITY OFF nao muda o que e produzido."""
        r = self._correr([{"ESTADO": pd.INSERTED,
                           "LINHA_ESCRITA": {"storage_path": "a.txt"}}])
        self.assertEqual(r["RASTRO"], "NAO_EMITIDO")
        self.assertEqual(r["BALDES"]["PASSED"], 1)
        self.assertEqual(r["ETAPAS_EMITIDAS"], [])

    def test_declara_onde_termina_e_por_que(self):
        r = self._correr([{"ESTADO": pd.INSERTED,
                           "LINHA_ESCRITA": {"storage_path": "a.txt"}}])
        self.assertEqual(r["TERMINA_EM"], "DERIVED")
        self.assertIn("READY_NAO_TEM_DONO", r["GAPS"])


class OLedgerEOCenso(unittest.TestCase):
    """O que o forward instrumentado obriga os artefatos a dizer.

        LEGACY_REPLAY_INSTRUMENTED != CANONICAL_FORWARD_INSTRUMENTED.

    A outra sessao mediu o buraco e escreveu-o com todas as letras:
    `FORWARD_INSTRUMENTED: false`, `PORQUE_FORWARD_NAO_ESTA: ...`. Esta missao
    fechou-o. O que estes testes impedem e o contrario: que ele apareca fechado
    sem prova que exista em disco.
    """

    def _ledger(self):
        import json
        with open(os.path.join(RAIZ, "system-map", "data",
                               "provas-de-execucao.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_o_ledger_aponta_uma_fronteira_e_uma_prova_que_existem(self):
        p = self._ledger()["PROVADOS"]["coleta/executor_texto_de_pdf.py"]
        self.assertTrue(p["FORWARD_INSTRUMENTED"])
        fw = p["FORWARD"]
        for chave in ("FRONTEIRA", "PROVA"):
            self.assertTrue(os.path.exists(os.path.join(RAIZ, fw[chave])),
                            "%s: %s" % (chave, fw[chave]))

    def test_o_forward_declara_onde_termina_e_nao_promete_a_cadeia_toda(self):
        fw = self._ledger()["PROVADOS"][
            "coleta/executor_texto_de_pdf.py"]["FORWARD"]
        self.assertEqual(["DERIVED"], fw["ETAPAS_OBSERVADAS"])
        for nunca in ("READY", "ADMISSION", "STRUCTURED", "RAW"):
            self.assertNotIn(nunca, fw["ETAPAS_OBSERVADAS"])

    def test_a_identidade_do_forward_e_provavel_e_a_do_legado_nao(self):
        """⚠️ AS DUAS RESPOSTAS SAO DIFERENTES PORQUE AS PERGUNTAS SAO.

        O replay legado varre 49 PDF de OITO fontes: nao ha UMA fonte, e NULL e
        a unica resposta honesta. A unidade forward e UMA, e o caminho onde ela
        foi preservada nomeia a fonte."""
        p = self._ledger()["PROVADOS"]["coleta/executor_texto_de_pdf.py"]
        self.assertIsNone(p["SOURCE_ID"])
        self.assertIsNone(p["ROUTE_CLASS_ID"])
        self.assertTrue(p["FORWARD"]["SOURCE_ID"])
        with open(os.path.join(RAIZ, "candidatas",
                               "ITALY-SOURCE-MASTER-V1.json"),
                  encoding="utf-8") as f:
            self.assertIn('"%s"' % p["FORWARD"]["SOURCE_ID"], f.read())

    def test_o_censo_deriva_o_campo_e_nao_o_digita(self):
        sys.path.insert(0, os.path.join(RAIZ, "system-map", "scripts"))
        import json
        with open(os.path.join(RAIZ, "system-map", "data",
                               "executores.generated.json"), encoding="utf-8") as f:
            censo = json.load(f)
        fw = censo["M2"]["CANONICAL_FORWARD_PATH"]
        self.assertEqual("YES", fw["CANONICAL_FORWARD_PATH_PROVED"])
        self.assertIn("coleta/derivacao_forward.py", fw["FRONTEIRAS"])

    def test_a_rota_da_m2_so_e_YES_com_as_duas_etapas_na_MESMA_rota(self):
        """⚠️ O INSTRUMENTO EXISTIR NAO E A ROTA SER OBSERVAVEL.

        Este teste exigia `NO`, e enquanto STRUCTURED e ADMISSION nao corriam
        `NO` era a resposta certa. A M2 fez as duas correrem — e um teste que
        congela a resposta reprovaria a missao por ela ter tido sucesso.

        A lei que ele protege NAO era «fica NO». Era: o campo so pode virar
        YES quando as duas etapas correrem NA MESMA ROTA. E essa continua
        inteira, e mais dura do que antes."""
        import json
        with open(os.path.join(RAIZ, "system-map", "data",
                               "executores.generated.json"), encoding="utf-8") as f:
            censo = json.load(f)
        rota = censo["M2"]["M2_ROUTE"]
        if rota["M2_ROUTE_OBSERVABILITY_READY"] != "YES":
            self.assertTrue(rota["ETAPAS_DA_ROTA_M2_NUNCA_OBSERVADAS"],
                            "NO sem dizer o que falta")
            return
        medida = rota.get("ROTA_MEDIDA")
        self.assertTrue(medida, "YES sem uma rota concreta por tras")
        for etapa in ("STRUCTURED", "ADMISSION"):
            self.assertIn(etapa, medida["ETAPAS_OBSERVADAS"],
                          "YES sem a MESMA rota observar %s" % etapa)
        self.assertTrue(medida.get("PROVA"), "YES sem prova apontavel")


if __name__ == "__main__":
    unittest.main()
