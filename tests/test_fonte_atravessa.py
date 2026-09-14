#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FONTE SO PODE VIR DE UM CAMPO PROVADO. NUNCA DE OUTRA COISA.

Doze ataques. Cada um tenta pôr no lugar da fonte alguma coisa que se lhe
parece: o caminho, o nome, o país, o sha, uma sentinela. Todos têm de falhar
alto.
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from dataclasses import replace

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
from coleta import ingresso as ing  # noqa: E402
from coleta import italy_executor as ixec  # noqa: E402
from leis import artefato as art  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "atravessa_t", os.path.join(RAIZ, "provas",
                                "a_fonte_atravessa_ate_a_porta.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

FONTE = "IT-T9-999"


class _ComLivro(unittest.TestCase):
    """Cada teste monta a sua coleta descartável. Nada toca em produção."""

    def setUp(self):
        self.raiz = tempfile.mkdtemp(prefix="sintonia-fonte-")

    def tearDown(self):
        shutil.rmtree(self.raiz, ignore_errors=True)

    def _poe(self, caminho, conteudo, observacoes=None, **kw):
        bruto = art.raw_do_disco(P._bytes(self.raiz, caminho, conteudo),
                                 self.raiz, **kw)
        if observacoes is None:
            observacoes = [P._observacao(RAW_SHA256=bruto.SHA256,
                                         RAW_PATH=caminho)]
        P._livro(self.raiz, observacoes)
        return bruto

    def _fonte(self, bruto):
        return ixec.fonte_do_conteudo(bruto.SHA256, raiz=self.raiz)


class OsDozeAtaques(_ComLivro):

    def test_01_sem_a_passagem_a_fonte_nao_chega(self):
        """Retirar a passagem: o bruto cru nunca tem fonte por si.

        ⚠️ ESTE TESTE FOI ALARGADO PORQUE DUAS MUTACOES SOBREVIVERAM: «nao
        passar a fonte ao bruto» e «passar o PAIS em vez da fonte». Medir o
        livro e medir o bruto CRU nao chega — ha que medir o que sai do
        carimbo.
        """
        from coleta import executor_texto_de_pdf as ex
        bruto = self._poe("a/b.pdf", b"conteudo")
        self.assertEqual(bruto.SOURCE_ID, art.NAO_SEI,
                         "raw_do_disco passou a saber a fonte sozinho")
        self.assertEqual(self._fonte(bruto)["SOURCE_ID"], FONTE,
                         "o livro deixou de responder")
        carimbado, achado = ex.fonte_para_o_bruto(bruto, self.raiz)
        self.assertEqual(carimbado.SOURCE_ID, FONTE,
                         "a fonte nao foi carimbada no bruto")
        self.assertEqual(achado["SOURCE_ID"], FONTE)

    def test_01b_o_carimbo_poe_a_fonte_e_nao_o_pais(self):
        """`COUNTRY_SCOPE` é onde entra. `SOURCE_ID` é de quem veio."""
        from coleta import executor_texto_de_pdf as ex
        bruto = self._poe("a/b.pdf", b"conteudo-pais", COUNTRY_SCOPE="IT")
        carimbado, _ = ex.fonte_para_o_bruto(bruto, self.raiz)
        self.assertEqual(carimbado.SOURCE_ID, FONTE)
        self.assertNotEqual(carimbado.SOURCE_ID, "IT",
                            "o pais entrou no lugar da fonte")
        self.assertEqual(carimbado.COUNTRY_SCOPE, "IT",
                         "o carimbo mexeu no que nao devia")

    def test_01c_sem_livro_o_carimbo_nao_inventa(self):
        from coleta import executor_texto_de_pdf as ex
        bruto = self._poe("data/x/IT-T3-008/b.pdf", b"sem-livro",
                          observacoes=[])
        carimbado, achado = ex.fonte_para_o_bruto(bruto, self.raiz)
        self.assertEqual(carimbado.SOURCE_ID, art.NAO_SEI)
        self.assertIsNone(achado["SOURCE_ID"])

    def test_02_o_caminho_nao_vota(self):
        """O caminho grita uma fonte e o livro diz outra."""
        bruto = self._poe(
            "data/collection-store/italy/IT-T3-008/x.pdf", b"c2")
        self.assertEqual(self._fonte(bruto)["SOURCE_ID"], FONTE)

    def test_03_o_pais_nao_e_a_fonte(self):
        """COUNTRY_SCOPE != SOURCE_ID. Um é onde entra, outro é de quem veio."""
        bruto = self._poe("a/b.pdf", b"c3", observacoes=[],
                          COUNTRY_SCOPE="IT")
        self.assertIsNone(self._fonte(bruto)["SOURCE_ID"])
        self.assertEqual(bruto.COUNTRY_SCOPE, "IT",
                         "o país sumiu — a correcao mexeu no que nao devia")

    def test_04_o_sha_nao_e_a_fonte(self):
        """O sha é a CHAVE para achar a linha, nunca a resposta."""
        bruto = self._poe("a/b.pdf", b"c4", observacoes=[])
        r = self._fonte(bruto)
        self.assertIsNone(r["SOURCE_ID"])
        self.assertNotIn(bruto.SHA256, json.dumps(r),
                         "o sha saiu como se fosse identidade")

    def test_05_o_nome_do_ficheiro_nao_e_a_fonte(self):
        bruto = self._poe("a/IT-T5-003.pdf", b"c5", observacoes=[])
        self.assertIsNone(self._fonte(bruto)["SOURCE_ID"])

    def test_06_livro_e_caminho_a_divergir_nao_produzem_desempate(self):
        """Não há desempate porque não há empate: o caminho não é lido."""
        bruto = self._poe(
            "data/collection-store/italy/IT-T2-001/x.pdf", b"c6")
        self.assertEqual(self._fonte(bruto)["SOURCE_ID"], FONTE)
        self.assertEqual(self._fonte(bruto)["CONFLITO"], [])

    def test_07_sentinela_nunca_e_identidade(self):
        for s in ("NAO SEI", "NÃO SEI", "NAO_SE_APLICA", "", None):
            bruto = self._poe(
                "a/b.pdf", b"c7-" + str(s).encode(),
                observacoes=[P._observacao(
                    RAW_SHA256=art.sha256_do_ficheiro(
                        P._bytes(self.raiz, "a/b.pdf",
                                 b"c7-" + str(s).encode())),
                    SOURCE_ID=s)])
            self.assertIsNone(self._fonte(bruto)["SOURCE_ID"],
                              "%r virou identidade" % (s,))

    def test_08_derived_nao_perde_o_que_o_raw_ganhou(self):
        bruto = self._poe("a/b.pdf", b"c8")
        bruto = replace(bruto, SOURCE_ID=self._fonte(bruto)["SOURCE_ID"])
        alvo = P._bytes(self.raiz, "d.txt", b"texto")
        filho = art.derivado_de(bruto, alvo, self.raiz,
                                derivacao=art.TEXT_EXTRACTION,
                                executor="t", executor_versao="1",
                                pipeline_versao="1", run_id="R",
                                estado=art.TEXT_LAYER_PRESENT)
        self.assertEqual(filho.SOURCE_ID, FONTE)

    def test_09_o_ingresso_traduz_sem_perder(self):
        cru = {"SOURCE_ID": FONTE, "ARTIFACT_TYPE": "DERIVED"}
        self.assertEqual(ing.para_a_porta(cru).get("source_id"), FONTE)

    def test_10_a_porta_le_um_nome_so(self):
        """Maiúscula e minúscula em pontos diferentes é como se perde valor."""
        item = ing.para_a_porta({"SOURCE_ID": FONTE, "ARTIFACT_TYPE": "RAW"})
        self.assertIn("source_id", item)
        self.assertNotIn("SOURCE_ID", item,
                         "os dois nomes coexistem: alguem vai ler o errado")
        d = adm.decidir(dict(item, id="x", texto="t"), "T3")
        self.assertNotEqual(d.regra, "origem")

    def test_11_retry_nao_muda_a_identidade(self):
        conteudo = b"c11"
        caminho = "a/b.pdf"
        sha = art.sha256_do_ficheiro(
            P._bytes(self.raiz, caminho, conteudo))
        obs = [P._observacao(RAW_SHA256=sha),
               P._observacao(RAW_SHA256=sha),
               P._observacao(RAW_SHA256=sha, RUN_ID="OUTRA")]
        bruto = self._poe(caminho, conteudo, observacoes=obs)
        r = self._fonte(bruto)
        self.assertEqual(r["SOURCE_ID"], FONTE)
        self.assertEqual(r["OBSERVACOES"], 3)
        self.assertEqual(r["CONFLITO"], [])

    def test_12_item_sem_livro_nao_ganha_fonte(self):
        bruto = self._poe(
            "data/samples/IT-SOURCE-SAMPLES/IT-T3-010/x.pdf", b"c12",
            observacoes=[])
        self.assertIsNone(self._fonte(bruto)["SOURCE_ID"])
        item = ing.para_a_porta({"ARTIFACT_TYPE": "RAW"})
        d = adm.decidir(dict(item, id="x", texto="t"), "T3")
        self.assertEqual(d.regra, "origem")
        self.assertEqual(d.resultado, adm.NAO_SEI)


class OConflitoEntraNoRecibo(unittest.TestCase):
    """O corpus real tem zero conflitos, e por isso este ramo precisa de teste.

        UM RAMO QUE SO OS DADOS DE AMANHA EXERCITAM
        FICA POR TESTAR ATE AMANHA — E AI E TARDE.
    """

    def _conta(self):
        return {"RAW_COM_FONTE_DO_LIVRO": 0, "RAW_SEM_FONTE_NO_LIVRO": 0,
                "RAW_FONTE_EM_CONFLITO": 0}

    def test_conflito_e_contado_e_vira_erro_no_recibo(self):
        from coleta import executor_texto_de_pdf as ex
        conta, erros = self._conta(), []
        ex.registar_achado({"SOURCE_ID": None, "CONFLITO": ["IT-A", "IT-B"]},
                           "x/y.pdf", conta, erros)
        self.assertEqual(conta["RAW_FONTE_EM_CONFLITO"], 1,
                         "o conflito nao foi contado")
        self.assertEqual(conta["RAW_SEM_FONTE_NO_LIVRO"], 0,
                         "o conflito foi engolido como «sem fonte»")
        self.assertEqual(len(erros), 1, "o conflito nao virou erro do recibo")
        self.assertIn("IT-A", erros[0]["ERRO"])

    def test_as_tres_respostas_caem_em_contas_diferentes(self):
        from coleta import executor_texto_de_pdf as ex
        conta, erros = self._conta(), []
        ex.registar_achado({"SOURCE_ID": "IT-X", "CONFLITO": []}, "a", conta, erros)
        ex.registar_achado({"SOURCE_ID": None, "CONFLITO": []}, "b", conta, erros)
        ex.registar_achado({"SOURCE_ID": None, "CONFLITO": ["p", "q"]},
                           "c", conta, erros)
        self.assertEqual(
            [conta["RAW_COM_FONTE_DO_LIVRO"], conta["RAW_SEM_FONTE_NO_LIVRO"],
             conta["RAW_FONTE_EM_CONFLITO"]], [1, 1, 1])


class DuasFontesNaoSeDesempatam(_ComLivro):

    def test_conflito_devolve_nenhuma_fonte_e_diz_quais(self):
        conteudo = b"disputado"
        sha = art.sha256_do_ficheiro(
            P._bytes(self.raiz, "a/b.pdf", conteudo))
        bruto = self._poe("a/b.pdf", conteudo, observacoes=[
            P._observacao(RAW_SHA256=sha),
            P._observacao(RAW_SHA256=sha, SOURCE_ID="IT-T9-888")])
        r = self._fonte(bruto)
        self.assertIsNone(r["SOURCE_ID"])
        self.assertEqual(r["CONFLITO"], ["IT-T9-888", FONTE])


class ATravessiaInteira(unittest.TestCase):

    def test_os_sete_cenarios_forward_passam(self):
        for c in P.cenarios():
            self.assertTrue(c["PASSA"], "cenario forward falhou: %s" % c["CASO"])

    def test_o_positivo_chega_a_pergunta_tematica(self):
        """A fonte respondida faz a cadeia avançar até ao tema.

        Se parasse antes, a correcao teria mudado um campo sem mudar nada.
        """
        positivos = [c for c in P.cenarios()
                     if c.get("ESPERADO") == P.FONTE]
        self.assertTrue(positivos)
        for c in positivos:
            self.assertEqual(c["TRILHA"]["ADMISSION_REGRA"],
                             "pertence ao universo",
                             "%s parou antes do tema" % c["CASO"])

    def test_a_prova_entrega_o_que_a_producao_entrega(self):
        """Menos campos do que a produção mede um caminho que ninguém percorre."""
        with open(os.path.join(RAIZ, "provas",
                               "a_fonte_atravessa_ate_a_porta.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        self.assertIn("ing.DO_COLETOR + ing.DA_FICHA_PARA_A_PORTA", fonte)


class OExecutorContaOQuePerguntou(unittest.TestCase):

    def test_o_recibo_mostra_quantos_ganharam_fonte(self):
        """Uma consulta que ninguém conta é indistinguível de não acontecer."""
        from coleta import executor_texto_de_pdf as ex
        c = ex.correr(seco=True)["COUNTS"]
        for k in ("RAW_COM_FONTE_DO_LIVRO", "RAW_SEM_FONTE_NO_LIVRO",
                  "RAW_FONTE_EM_CONFLITO"):
            self.assertIn(k, c)
        self.assertGreater(c["RAW_COM_FONTE_DO_LIVRO"], 0,
                           "nenhum bruto ganhou fonte: a consulta nao corre")


if __name__ == "__main__":
    unittest.main()
