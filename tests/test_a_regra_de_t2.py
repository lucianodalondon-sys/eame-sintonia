# -*- coding: utf-8 -*-
"""A MEDICAO DE T2 NAO PODE APODRECER EM SILENCIO.

Esta missao mediu se era possivel escrever a regra de «T2 — Clima e tempo» na
Admission, e a medicao respondeu QUE NAO. Uma decisao de NAO IMPLEMENTAR e a
mais facil de perder: nao deixa codigo, e daqui a tres meses alguem escreve a
lista de palavras obvia porque «ninguem tinha tentado».

    O QUE ESTE FICHEIRO GUARDA NAO E CODIGO. E UM NAO COM PROVA.

Se alguem escrever T2 em `PERGUNTAS_DO_UNIVERSO`, estes testes caem — e quem os
apagar tem de apagar tambem a razao, que esta escrita a cada um.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "prova_regra_t2", os.path.join(RAIZ, "provas", "a_regra_de_t2.py"))
prova = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prova)


class OGabaritoEReal(unittest.TestCase):
    """Um gabarito de documentos inventados mede a imaginacao de quem o fez."""

    def test_todo_documento_do_gabarito_existe_nesta_arvore(self):
        for caminho, _esperado, _why in prova.GABARITO:
            with self.subTest(caminho=caminho):
                self.assertTrue(os.path.isfile(os.path.join(RAIZ, caminho)),
                                f"o gabarito cita {caminho}, que nao existe")

    def test_todo_documento_do_gabarito_diz_porque(self):
        for caminho, esperado, why in prova.GABARITO:
            with self.subTest(caminho=caminho):
                self.assertIn(esperado, (prova.SIM, prova.NAO, prova.AMBIGUO))
                self.assertGreater(len(why), 20,
                                   f"{caminho} tem rotulo sem razao escrita")

    def test_ha_positivos_negativos_e_ambiguos(self):
        c = [e for _p, e, _w in prova.GABARITO]
        self.assertGreaterEqual(c.count(prova.SIM), 5)
        self.assertGreaterEqual(c.count(prova.NAO), 20)
        self.assertGreaterEqual(c.count(prova.AMBIGUO), 1,
                                "um gabarito sem ambiguos foi limpo para o "
                                "numero dar bem")

    def test_o_mesmo_publicador_esta_dos_dois_lados(self):
        """O contraexemplo que funda a missao: ARPAV publica T2 E T3.

        Sem ele, classificar pela fonte pareceria funcionar.
        """
        arpav_sim = [p for p, e, _w in prova.GABARITO
                     if e == prova.SIM and "Meteo Veneto" not in _w
                     and "ARPAV" in _w]
        arpav_nao = [p for p, e, w in prova.GABARITO
                     if e == prova.NAO and "ARPAV" in w]
        self.assertTrue(arpav_sim, "faltam positivos da ARPAV")
        self.assertTrue(arpav_nao, "faltam negativos da ARPAV — sem eles a "
                                   "prova de que o publicador nao decide o "
                                   "territorio desaparece")


class AMedicaoContinuaANegar(unittest.TestCase):
    """Os numeros que fecharam o portao, medidos outra vez a cada corrida."""

    @classmethod
    def setUpClass(cls):
        cls.textos = {c: prova._texto(c) for c, _e, _w in prova.GABARITO}

    def test_nenhuma_candidata_fica_sem_erro(self):
        for nome, palavras in prova.CANDIDATAS_A.items():
            m = prova._matriz(nome, palavras, self.textos)
            erros = (m["FALSE_POSITIVE"] + m["FALSE_NEGATIVE"]
                     + m["UNKNOWN"] + m["AMBIGUO_FORCADO"])
            with self.subTest(candidata=nome):
                self.assertGreater(erros, 0,
                                   f"{nome} passou a nao errar nada. Isto NAO "
                                   f"e um teste a corrigir: e a medicao a "
                                   f"mudar, e obriga a refazer o portao.")

    def test_nenhum_termo_separa_os_dois_lados_sozinho(self):
        pos = [g for g in prova.GABARITO if g[1] == prova.SIM]
        neg = [g for g in prova.GABARITO if g[1] == prova.NAO]
        self.assertEqual(len(prova._exclusivos(self.textos, pos, neg)), 0,
                         "apareceu um termo em todos os positivos e em nenhum "
                         "negativo. A medicao mudou — refazer o portao.")

    def test_a_regra_ajustada_nao_generaliza(self):
        """O ataque que decidiu tudo: treina num publicador, testa noutro."""
        pos = [g for g in prova.GABARITO if g[1] == prova.SIM]
        neg = [g for g in prova.GABARITO if g[1] == prova.NAO]
        import contextlib
        import io as _io
        with contextlib.redirect_stdout(_io.StringIO()):
            acerta, retido = prova.red_team(self.textos, pos, neg)
        self.assertEqual(retido, 10)
        self.assertEqual(acerta, 0,
                         "a regra ajustada passou a acertar num publicador que "
                         "nao viu. Se isso e verdade, o portao pode reabrir — "
                         "mas tem de ser REABERTO, nao contornado.")

    def test_a_medicao_e_a_mesma_em_duas_corridas(self):
        pos = [g for g in prova.GABARITO if g[1] == prova.SIM]
        neg = [g for g in prova.GABARITO if g[1] == prova.NAO]
        import io
        import contextlib
        saidas = []
        for _ in range(2):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                prova.red_team(self.textos, pos, neg)
            saidas.append(buf.getvalue())
        self.assertEqual(saidas[0], saidas[1],
                         "a prova responde coisas diferentes em corridas "
                         "iguais. Uma medicao instavel nao mede.")


class APortaNaoGanhouRegraDeT2(unittest.TestCase):
    """A decisao desta missao, escrita onde nao se perde."""

    def test_t2_continua_sem_regra_escrita(self):
        self.assertNotIn(
            "T2", adm.PERGUNTAS_DO_UNIVERSO,
            "alguem escreveu T2 em PERGUNTAS_DO_UNIVERSO. A medicao de "
            "`provas/a_regra_de_t2.py` diz que qualquer lista possivel separa "
            "por dia da semana e nome de departamento, e acerta 0/10 num "
            "publicador que nao viu. Se ha material novo que muda isso, "
            "refaca a medicao primeiro.")

    def test_a_porta_responde_a_verdade_sobre_t2(self):
        """NAO_SE_APLICA nao e uma falha: e a porta a dizer que nao ha regra."""
        d = adm.decidir({"id": "x", "texto": "pioggia e temperatura",
                         "source_id": "IT-T2-002", "url": "https://e.it/a",
                         "artifact_type": "RAW",
                         "captured_at": "2026-09-03T00:00:00Z"}, "T2")
        self.assertEqual(d.resultado, adm.NAO_SE_APLICA)
        self.assertIn("nao ha regra escrita", d.motivo)

    def test_os_universos_que_ja_tinham_regra_nao_foram_tocados(self):
        self.assertEqual(sorted(adm.PERGUNTAS_DO_UNIVERSO), ["T3", "T4", "T7", "T9"])
        for u, n in (("T7", 21), ("T9", 12), ("T4", 11), ("T3", 13)):
            with self.subTest(universo=u):
                self.assertEqual(len(adm.PERGUNTAS_DO_UNIVERSO[u]), n,
                                 f"a lista de {u} mudou nesta missao, e a "
                                 f"missao so autorizava mexer em T2")


class AProvaNaoSujaNada(unittest.TestCase):
    """Ja aconteceu uma vez: um teste escreveu 417 linhas no livro real."""

    def test_a_prova_nao_escreve_no_livro_de_decisoes(self):
        antes = os.path.getmtime(adm.LIVRO) if os.path.exists(adm.LIVRO) else None
        textos = {c: prova._texto(c) for c, _e, _w in prova.GABARITO}
        prova._matriz("A3-medida-forte",
                      prova.CANDIDATAS_A["A3-medida-forte"], textos)
        depois = os.path.getmtime(adm.LIVRO) if os.path.exists(adm.LIVRO) else None
        self.assertEqual(antes, depois,
                         "a prova tocou no livro real de decisoes")


if __name__ == "__main__":
    unittest.main()
