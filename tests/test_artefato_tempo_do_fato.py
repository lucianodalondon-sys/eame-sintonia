# -*- coding: utf-8 -*-
"""D70 · a lei do tempo do fato em `leis/artefato.py::conferir`.

    py -m unittest tests.test_artefato_tempo_do_fato

(1) FACT_TIME_BASIS == RELATIVA_A_PUBLICACAO: exige publicacao provada (e nao em conflito, DA-9),
    a expressao, o trecho, o calculo e a precisao CALCULADA — e REFAZ a conta; reprova se nao der
    exatamente o FACT_TIME.
(2) Nos outros casos: a protecao antiga, mas pelo SIGNIFICADO da data (dia / intervalo / instante),
    nao pelas letras.
"""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "leis"))
from leis import artefato as A      # noqa: E402
import fato_do_texto as FT          # noqa: E402

BASE = "meta article:published_time"
OGGI = "I tecnici hanno osservato oggi, lunedì, sintomi di peronospora nei vigneti di Verona.\n"
IERI = "I tecnici hanno osservato ieri sintomi di peronospora nei vigneti della provincia di Verona.\n"


def artefato(fact_time, published_at, notas=None, **mais):
    return A.Artefato(ARTIFACT_ID="t", ARTIFACT_TYPE="DERIVED", STORAGE_LOCATION="t", SHA256="0" * 64,
                      FACT_TIME=fact_time, PUBLISHED_AT=published_at, NOTES=dict(notas or {}), **mais)


def relativa(texto=OGGI, pub="2026-09-21"):
    r = FT.campos_do_fato(texto, pub, BASE)
    return r["fact_time"], FT.notas_para_o_artefato(r, BASE)


class TestRelativaSoComAContaRefeita(unittest.TestCase):
    def test_oggi_marcado_e_ieri_passam(self):
        for texto, esperado in ((OGGI, "2026-09-21"), (IERI, "2026-09-20")):
            ft, notas = relativa(texto)
            self.assertEqual(esperado, ft)
            self.assertEqual([], A.conferir(artefato(ft, "2026-09-21", notas)), texto)
            self.assertEqual([], A.conferir(artefato(ft, "2026-09-21T08:30:00+02:00", notas)), texto)

    def test_semana_passa(self):
        ft, notas = relativa("Le catture rilevate la settimana scorsa nei frutteti della provincia sono in forte aumento.\n",
                             "2026-09-23")
        self.assertEqual("2026-09-14/2026-09-20", ft)
        self.assertEqual([], A.conferir(artefato(ft, "2026-09-23", notas)))

    def test_cada_nota_ausente_reprova(self):
        ft, notas = relativa()
        for k in A.NOTAS_DA_RELATIVA:
            for vazio in (None, "", "NAO SEI", "NAO_SE_APLICA"):
                n = dict(notas)
                if vazio is None:
                    n.pop(k)
                else:
                    n[k] = vazio
                q = A.conferir(artefato(ft, "2026-09-21", n))
                self.assertTrue(q, (k, vazio))

    def test_calculo_errado_reprova(self):
        ft, notas = relativa(IERI)
        q = A.conferir(artefato("2026-09-19", "2026-09-21", notas))
        self.assertTrue(any("conta refeita" in x for x in q), q)

    def test_intervalo_adulterado_reprova(self):
        ft, notas = relativa()
        for mau in ("2026-09-21/2026-09-21", "2026-09-20/2026-09-21", "2026-09-21T00:00:00"):
            self.assertTrue(A.conferir(artefato(mau, "2026-09-21", notas)), mau)

    def test_expressao_ou_trecho_adulterados_reprovam(self):
        ft, notas = relativa(IERI)
        self.assertTrue(A.conferir(artefato(ft, "2026-09-21", dict(notas, FACT_TIME_EXPRESSAO="l'altro ieri"))))
        self.assertTrue(A.conferir(artefato(ft, "2026-09-21", dict(notas, FACT_TIME_EVIDENCIA="nada a ver"))))
        ft, notas = relativa()
        # o mesmo «oggi», mas no sentido de «hoje em dia» (D64): a lei tambem o recusa
        self.assertTrue(A.conferir(artefato(ft, "2026-09-21", dict(
            notas, FACT_TIME_EVIDENCIA="ad oggi sono stati osservati pochi sintomi nei vigneti"))))
        self.assertTrue(A.conferir(artefato(ft, "2026-09-21", dict(
            notas, FACT_TIME_EVIDENCIA="rispetto a oggi, lunedì, le catture calano"))))

    def test_base_trocada_reprova(self):
        ft, notas = relativa()
        # base com texto a mais
        self.assertTrue(A.conferir(artefato(ft, "2026-09-21", dict(notas, FACT_TIME_BASIS="RELATIVA_A_PUBLICACAO · x"))))
        # a mesma data, mas a base ja nao diz relativa: e a publicacao copiada -> a protecao antiga reprova
        self.assertTrue(A.conferir(artefato(ft, "2026-09-21", dict(notas, FACT_TIME_BASIS="CAMPO · texto"))))
        # calculo declarado de outra especie
        self.assertTrue(A.conferir(artefato(ft, "2026-09-21", dict(notas, FACT_TIME_CALCULO="OUTRA_CONTA"))))

    def test_precisao_sem_calculada_ou_errada_reprova(self):
        ft, notas = relativa()
        self.assertTrue(A.conferir(artefato(ft, "2026-09-21", dict(notas, FACT_TIME_PRECISION="DATE_EXACT"))))
        self.assertTrue(A.conferir(artefato(ft, "2026-09-21", dict(notas, FACT_TIME_PRECISION="WEEK+CALCULADA"))))

    def test_publicacao_nao_provada_ou_em_conflito_reprova(self):
        ft, notas = relativa()
        for b in ("NAO SEI · sem data na pagina", "UNKNOWN", "CONFLITO: contrato 2026-09-20, pagina 2026-09-22"):
            q = A.conferir(artefato(ft, "2026-09-21", dict(notas, PUBLISHED_AT_BASIS=b)))
            self.assertTrue(q, b)
        self.assertTrue(A.conferir(artefato(ft, "NAO SEI", notas)))
        self.assertTrue(A.conferir(artefato(ft, "21/09/2026", notas)))


class TestSignificadoNaoLetras(unittest.TestCase):
    def test_o_mesmo_dia_escrito_de_outra_maneira_reprova(self):
        for ft, pub in (("2026-09-21", "2026-09-21"), ("2026-09-21/2026-09-21", "2026-09-21"),
                        ("2026-09-21", "2026-09-21T09:00:00+02:00"),
                        ("2026-09-21/2026-09-21", "2026-09-21T09:00:00+02:00"),
                        ("2026-09-21T07:00:00Z", "2026-09-21T09:00:00+02:00"),
                        ("2026-09-14/2026-09-20", "2026-09-14/2026-09-20")):
            self.assertTrue(A.conferir(artefato(ft, pub, {"FACT_TIME_BASIS": "CAMPO"})), (ft, pub))

    def test_datas_diferentes_passam(self):
        for ft, pub in (("2026-09-20", "2026-09-21"), ("2026-09-14/2026-09-20", "2026-09-21"),
                        ("2026-09-21T06:00:00+02:00", "2026-09-21"),        # instante do facto: mais fino, nao copia
                        ("12 settembre", "2026-09-21"), ("campagna 2026", "2026-09-21")):
            self.assertEqual([], A.conferir(artefato(ft, pub, {"FACT_TIME_BASIS": "CAMPO"})), (ft, pub))

    def test_texto_que_nao_e_data_compara_como_antes(self):
        self.assertTrue(A.conferir(artefato("settembre 2026", "settembre 2026", {"FACT_TIME_BASIS": "CAMPO"})))

    def test_prova_declarada_continua_a_valer(self):
        self.assertEqual([], A.conferir(artefato("2026-09-21", "2026-09-21", {"FACT_TIME_BASIS": "PUBLISHED_AT_COM_PROVA"})))

    def test_hora_do_trabalho_pelo_significado(self):
        a = artefato("2026-09-21T07:00:00Z", "NAO SEI", {"FACT_TIME_BASIS": "CAMPO"},
                     COLLECTED_AT="2026-09-21T09:00:00+02:00")
        self.assertTrue(any("COLLECTED_AT" in x for x in A.conferir(a)))
        a = artefato("2026-09-21", "NAO SEI", {"FACT_TIME_BASIS": "CAMPO"}, COLLECTED_AT="2026-09-21T09:00:00+02:00")
        self.assertEqual([], A.conferir(a), "um dia do facto nao e a hora de trabalho da maquina")


if __name__ == "__main__":
    unittest.main()
