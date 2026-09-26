# -*- coding: utf-8 -*-
"""QUATRO-CHAVES-V1 — o que a régua T1 já sabe tem de poder passar adiante.

D29 pede quatro chaves para a janela de cultura: CULTURA × REGIÃO DO FATO ×
FASE × JANELA. Medido a 25/09/2026 na Sala real: 0 de 69 itens têm qualquer
uma. E a régua T1 (v9) já SABE duas — mas no SIM guardava só
`{"cultura": True}`: sabia QUE havia cultura, e deitava fora QUAL.

Estes testes exigem, na admissão (coleta/admissão, NÃO Intelligence):
  1. a porta CONTINUA sem decidir a janela — a evidência dela não ganha campos
     (é lei do dono da régua T1: `test_regua_t1.APortaNaoDecideAJanela`);
  2. `janela_declarada()`, a jusante, relê QUAL cultura pela mesma regra e
     monta as quatro chaves com a lei:
       · região do FATO nunca herdada do lugar da FONTE;
       · ausência = NAO SEI (nem vazio, nem None, nem palpite);
       · FACT_TIME != PUBLISHED_AT != CAPTURED_AT — a janela não nasce de
         data de publicação nem da nossa visita;
       · a janela em si (intervalo + safra) a régua NÃO extrai: NAO SEI.

⚠️ AJUSTE DECLARADO (D58, QUATRO-CHAVES-NA-SALA): a ausência dentro das chaves
era comparada com `A.NAO_SEI` («NAO_SEI», o RESULTADO da porta) e passou a
`A.AUSENCIA` («NAO SEI»). Não afrouxa nada: quando `janela_declarada` passou a
viajar no contrato READY, a regra de `admissao/admissao.py` (bloco «DUAS
PALAVRAS PARECIDAS») passou a valer para ela — o contrato de saída escreve
`AUSENCIA`, e `NAO_SEI` seria guardado pela Sala como valor medido.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(RAIZ, "admissao"), RAIZ]

import admissao as A  # noqa: E402

BOLETIM_T1 = (
    "Bollettino tecnico vite. Fase di fioritura in corso nei vigneti di collina. "
    "Superata la soglia di intervento per infestazione di tignoletta: si consiglia "
    "il trattamento fitosanitario entro la settimana.")


def _decidido(texto=BOLETIM_T1, **extra):
    item = {"texto": texto, "source_id": "IT-T1-900", "id": "derived:1",
            "artifact_type": "DERIVED", "parent_sha256": "a" * 64}
    item.update(extra)
    return item, A.decidir(item, "T1", corrida="RUN-TESTE")


class APortaContinuaSemDecidirAJanela(unittest.TestCase):
    """A lei do dono da regua T1 (`test_regua_t1.APortaNaoDecideAJanela`) fica
    de pe: a evidencia da porta NAO ganha campos. Quem monta as chaves e
    `janela_declarada`, a jusante."""

    def test_o_boletim_de_exemplo_passa_em_t1(self):
        _item, d = _decidido()
        self.assertEqual(d.resultado, A.SIM, d.motivo)

    def test_a_evidencia_da_porta_nao_ganhou_campos(self):
        r, _m, ev = A._do_universo({"texto": BOLETIM_T1}, "T1", A.PERGUNTAS_DO_UNIVERSO["T1"])
        self.assertEqual(r, A.SIM)
        self.assertLessEqual(set(ev), {"palavras", "cultura", "sinais", "falta"})

    def test_o_nao_sei_tambem_passa_a_cultura_adiante(self):
        item = {"texto": "Vite in collina, tutto tranquillo.", "source_id": "IT-T1-901",
                "id": "derived:3", "artifact_type": "DERIVED", "parent_sha256": "c" * 64}
        d = A.decidir(item, "T1", corrida="RUN-TESTE")
        self.assertEqual(d.resultado, A.NAO_SEI)
        j = A.janela_declarada(item, d)
        self.assertEqual(j["CULTURA"]["VALOR"], ["vite"])
        self.assertEqual(j["FASE"]["VALOR"], A.AUSENCIA)


class AJanelaDeclaradaCumpreALei(unittest.TestCase):

    def test_as_quatro_chaves_existem(self):
        item, d = _decidido()
        j = A.janela_declarada(item, d)
        # EXTRATOR-EVENTO-V2 (D84): a PRAGA/DOENCA dos boletins viaja ao lado, fora da contagem das quatro
        self.assertEqual(set(j), {"CULTURA", "REGIAO_DO_FATO", "FASE", "JANELA", "PROBLEMA", "TEMPOS", "ORIGEM"})

    def test_cultura_e_fase_vem_da_regua(self):
        item, d = _decidido()
        j = A.janela_declarada(item, d)
        self.assertIn("vite", j["CULTURA"]["VALOR"])
        self.assertGreaterEqual(len(j["FASE"]["VALOR"]), 2)
        self.assertIn("T1", j["CULTURA"]["BASE"])

    def test_regiao_nunca_herdada_da_fonte(self):
        item, d = _decidido(source_location="Veneto")
        j = A.janela_declarada(item, d)
        self.assertEqual(j["REGIAO_DO_FATO"]["VALOR"], A.AUSENCIA)

    def test_regiao_do_fato_passa_com_a_base(self):
        item, d = _decidido(fact_location="Valpolicella", fact_location_basis="declarado no boletim")
        j = A.janela_declarada(item, d)
        self.assertEqual(j["REGIAO_DO_FATO"]["VALOR"], "Valpolicella")
        self.assertEqual(j["REGIAO_DO_FATO"]["BASE"], "declarado no boletim")

    def test_publicacao_e_visita_nao_viram_tempo_do_fato_nem_janela(self):
        item, d = _decidido(published_at="2026-05-10", captured_at="2026-09-20T12:00:00Z")
        j = A.janela_declarada(item, d)
        self.assertEqual(j["TEMPOS"]["FACT_TIME"], A.AUSENCIA)
        self.assertEqual(j["TEMPOS"]["PUBLISHED_AT"], "2026-05-10")
        self.assertEqual(j["TEMPOS"]["CAPTURED_AT"], "2026-09-20T12:00:00Z")
        self.assertEqual(j["JANELA"]["VALOR"], A.AUSENCIA)

    def test_ausencia_e_nao_sei_e_nunca_vazio(self):
        item, d = _decidido()
        j = A.janela_declarada(item, d)
        for chave in ("REGIAO_DO_FATO", "JANELA"):
            self.assertEqual(j[chave]["VALOR"], A.AUSENCIA)
        for k, v in j["TEMPOS"].items():
            self.assertNotIn(v, ("", None), k)

    def test_outro_universo_nao_inventa_cultura(self):
        """PERIODO-E-CHAVES (26/09, ordem da coordenacao): fora de T1 a cultura LE-SE no titulo e
        na prova do lugar — o texto nomeia-a, nao e inventada. A regua de T1 continua a nao ser
        chamada: VEIO_DE diz o titulo, nunca a evidencia da decisao; a FASE continua NAO SEI."""
        item = {"texto": BOLETIM_T1, "source_id": "IT-T7-900", "id": "derived:2",
                "artifact_type": "DERIVED", "parent_sha256": "b" * 64}
        d = A.decidir(item, "T7", corrida="RUN-TESTE")
        j = A.janela_declarada(item, d)
        self.assertIn("vite", j["CULTURA"]["VALOR"])
        self.assertIn("titulo", j["CULTURA"]["VEIO_DE"])
        self.assertNotIn("decisao.evidencia", j["CULTURA"]["VEIO_DE"])
        self.assertEqual(j["FASE"]["VALOR"], A.AUSENCIA)
        sem = {"texto": "Riunione del consiglio direttivo e bilancio annuale.", "source_id": "IT-T7-900"}
        j = A.janela_declarada(sem, A.decidir(sem, "T7", corrida="RUN-TESTE"))
        self.assertEqual(j["CULTURA"]["VALOR"], A.AUSENCIA)

    def test_palavras_de_outra_regua_nao_viram_fase(self):
        """Uma decisão de T2 traz `palavras` de clima na evidência. Não são fase de
        cultura, e a cultura só se relê quando a régua que a pede (T1) a viu."""
        item = {"texto": BOLETIM_T1, "source_id": "IT-T2-900"}
        d = A.Decisao(item="x", universo="T2", resultado=A.SIM, regra="pertence ao universo",
                      motivo="x", evidencia={"palavras": ["pioggia", "temperatura"], "cultura": True})
        j = A.janela_declarada(item, d)
        # A regra: as palavras de CLIMA da regua T2 nao viram fase. (D84: a fase que o TEXTO do boletim escreve
        # — «fioritura» — entra, com a base do boletim; a evidencia da regua continua de fora.)
        fase = j["FASE"]["VALOR"]
        self.assertFalse({"pioggia", "temperatura"} & set(fase if isinstance(fase, list) else []))
        self.assertNotIn("decisao.evidencia", j["FASE"]["VEIO_DE"])
        # PERIODO-E-CHAVES: a cultura sai do TITULO do item, nao da evidencia da regua T2
        self.assertNotIn("decisao.evidencia", j["CULTURA"]["VEIO_DE"])
        self.assertIn("titulo", j["CULTURA"]["VEIO_DE"])


if __name__ == "__main__":
    unittest.main()
