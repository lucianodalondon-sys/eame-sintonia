#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RUNBOOK-MICRO-SOCIAL — o condutor recusa antes da rede, para depois de cada rodada pela
prova-teto, e mostra data/lugar da Sala com base e precisao. Sem rede e sem banco."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "micro_social"))
sys.path.insert(0, RAIZ)
import micro_social as MS  # noqa: E402
sys.path.insert(0, os.path.join(RAIZ, "scripts", "micro_coleta"))
import micro_coleta as MC  # noqa: E402

LI = {"SOURCE_ID": "IT-T7-171", "FASE": "video-linkedin",
      "PAGINA": "https://www.linkedin.com/company/consorzio-tutela-grana-padano/", "TETO": 1}
YT = {"SOURCE_ID": "IT-T8-006", "FASE": "audio-youtube", "VIDEO": "abcdefghijk", "DURACAO_S": 480}
LOTE = {"RODADAS": [{"N": 1, "ITENS": [LI]}, {"N": 2, "ITENS": [YT]}]}
ELEGIVEL = lambda sid: {"COLLECTION_ELIGIBLE": True, "MOTIVO": "ELIGIBLE", "PORQUE": "ok"}  # noqa: E731
PASS = lambda: {"PAIS": "IT", "GATE": "PASS"}  # noqa: E731


def _run(n):
    return "IT-T7-2026-09-26-0400%02d-%016x" % (n, n)


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="micro-social-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.estado = os.path.join(self.tmp, "ESTADO.json")
        self.lancados = []

    def lancar(self, cmd):
        self.lancados.append(cmd)
        return {"CODIGO": 0, "SAIDA": "CORRIDA SUCCESS · %s\n" % _run(len(self.lancados))}

    def correr(self, n=1, **kw):
        base = dict(autorizado=True, gate=ELEGIVEL, parado=lambda: (True, "ok"), egresso=PASS,
                    instalado=lambda: [], yt_dlp=lambda: (True, "2026.8.19"),
                    sala=lambda: [], lancar=self.lancar,
                    teto=lambda ids, pasta: {"ESTADO": "PASS", "PEDIDOS_NA_ONDA": len(ids)})
        base.update(kw)
        return MS.rodada(LOTE, n, self.estado, **base)


class ARodadaRecusaAntesDaRede(_Base):

    def assertNaoLancou(self, r, texto):
        self.assertFalse(r["CORREU"])
        self.assertIn(texto, json.dumps(r, ensure_ascii=False))
        self.assertEqual(self.lancados, [])

    def test_lote_1_por_instalar(self):
        self.assertNaoLancou(self.correr(instalado=lambda: ["sem a D41"]), "LOTE_1_NAO_INSTALADO")

    def test_sem_autorizacao(self):
        self.assertNaoLancou(self.correr(autorizado=False), "autorizado-pelo-dono")

    def test_robo_a_correr(self):
        self.assertNaoLancou(self.correr(parado=lambda: (False, "supervisor vivo")), "ROBO_NAO_PARADO")

    def test_sala_sem_variaveis(self):
        self.assertNaoLancou(self.correr(sala=lambda: ["SINTONIA_SALA_DSN"]), "SINTONIA_SALA_DSN")

    def test_egresso_nao_it(self):
        self.assertNaoLancou(self.correr(egresso=lambda: {"PAIS": "UNKNOWN", "GATE": "BLOCKED"}),
                             "EGRESSO_NAO_IT")

    def test_yt_dlp_que_nao_abre_trava_a_rodada_do_youtube(self):
        self.assertNaoLancou(self.correr(n=2, yt_dlp=lambda: (False, "No module named yt_dlp")),
                             "YT_DLP_NAO_ABRE")

    def test_rodada_sem_youtube_nao_pergunta_pelo_yt_dlp(self):
        r = self.correr(n=1, yt_dlp=lambda: (False, "nao devia ser chamado"))
        self.assertTrue(r["CORREU"])

    def test_rodada_fora_do_lote(self):
        self.assertNaoLancou(self.correr(n=9), "nao esta no lote")

    def test_parada_automatica_anterior_trava_a_seguinte(self):
        with open(os.path.join(self.tmp, MS.FLAG_DE_PARADA), "w", encoding="utf-8") as f:
            f.write("PROVA-TETO=FAIL")
        self.assertNaoLancou(self.correr(), "PARADA AUTOMATICA")


class OItemEConferido(unittest.TestCase):

    def test_itens_certos_passam(self):
        self.assertEqual(MS.conferir_item(LI, ELEGIVEL), [])
        self.assertEqual(MS.conferir_item(YT, ELEGIVEL), [])

    def test_os_defeitos_do_item(self):
        casos = [(dict(YT, DURACAO_S=900), "longo demais"), (dict(YT, DURACAO_S=None), "DURACAO_S em falta"),
                 (dict(YT, VIDEO="x"), "11 caracteres"), (dict(LI, TETO=3), "TETO tem de ser 1"),
                 (dict(LI, PAGINA="https://example.com"), "PAGINA"),
                 (dict(LI, FASE="janela"), "fora da MICRO social")]
        for it, texto in casos:
            self.assertIn(texto, " ".join(MS.conferir_item(it, ELEGIVEL)), it)

    def test_portao_que_recusa_bloqueia(self):
        nao = lambda sid: {"COLLECTION_ELIGIBLE": False, "MOTIVO": "READY_LEGACY", "PORQUE": "x"}  # noqa: E731
        self.assertIn("READY_LEGACY", " ".join(MS.conferir_item(LI, nao)))

    def test_o_comando_e_python_valido_com_o_pedido(self):
        cmd = MS.comando_de(YT)
        compile(cmd[2], "<pedido>", "exec")
        self.assertIn("'fase': 'audio-youtube'", cmd[2])
        self.assertIn("'video': 'abcdefghijk'", cmd[2])
        self.assertIn("alvo='T8'", cmd[2])


class ARodadaCorreEPara(_Base):

    def test_rodada_boa_grava_estado_que_o_relatorio_le(self):
        r = self.correr()
        self.assertTrue(r["CORREU"])
        self.assertEqual(r["PARADA_AUTOMATICA"], [])
        est = json.load(open(self.estado, encoding="utf-8"))
        cs = MC.corridas_do_estado(est)
        self.assertEqual([(c["SOURCE_ID"], c["RUN_ID"], c["GATE_NO_INSTANTE"]) for c in cs],
                         [("IT-T7-171", _run(1), "ELIGIBLE")])
        self.assertEqual((cs[0]["EGRESSO_ANTES"]["PAIS"], cs[0]["EGRESSO_DEPOIS"]["PAIS"]), ("IT", "IT"))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, MS.FLAG_DE_PARADA)))

    def test_a_prova_e_sobre_a_noite_inteira(self):
        vistos = []
        teto = lambda ids, pasta: vistos.append(list(ids)) or {"ESTADO": "PASS"}  # noqa: E731
        self.correr(1, teto=teto)
        self.correr(2, teto=teto)
        self.assertEqual(vistos, [[_run(1)], [_run(1), _run(2)]])

    def test_prova_que_nao_passa_escreve_a_parada(self):
        for estado in ("FAIL", "NAO_SEI"):
            with self.subTest(estado=estado):
                for f in (self.estado, os.path.join(self.tmp, MS.FLAG_DE_PARADA)):
                    if os.path.exists(f):
                        os.remove(f)
                r = self.correr(teto=lambda ids, pasta: {"ESTADO": estado})
                self.assertTrue(r["PARADA_AUTOMATICA"])
                self.assertIn(estado, open(os.path.join(self.tmp, MS.FLAG_DE_PARADA), encoding="utf-8").read())
                r2 = self.correr(2)
                self.assertFalse(r2["CORREU"])
                self.assertIn("PARADA AUTOMATICA", r2["PORQUE"])

    def test_egresso_que_cai_depois_para(self):
        seq = iter([{"PAIS": "IT", "GATE": "PASS"}, {"PAIS": "BR", "GATE": "BLOCKED"}])
        r = self.correr(egresso=lambda: next(seq))
        self.assertIn("EGRESSO DEPOIS=BR", " ".join(r["PARADA_AUTOMATICA"]))

    def test_corrida_sem_run_id_para(self):
        r = self.correr(lancar=lambda cmd: {"CODIGO": 1, "SAIDA": "Traceback", "ERRO": "x"})
        self.assertIn("sem RUN_ID", " ".join(r["PARADA_AUTOMATICA"]))

    @unittest.skipIf(MS.lote_1_instalado(), "a PROVA-TETO-SOCIAL (lote 1) nao esta nesta arvore")
    def test_com_a_prova_teto_de_verdade_D41_para(self):
        """A prova real, sobre um livro com youtube 3 + googlevideo 3 = 6 > 5."""
        livro = os.path.join(self.tmp, "runs.ndjson")
        with open(livro, "w", encoding="utf-8") as f:
            f.write(json.dumps({"RUN_ID": _run(1), "CORTESIA": {"PEDIDOS_POR_HOST": {
                "youtube.com": 3, "rr1---sn-a.googlevideo.com": 3}}}) + "\n")
        teto = lambda ids, pasta: MS.prova_teto(ids, __import__("pathlib").Path(pasta), livro)  # noqa: E731
        r = self.correr(teto=teto)
        self.assertEqual(r["PROVA_TETO"], "FAIL")
        self.assertIn("youtube.com", open(os.path.join(self.tmp, MS.FLAG_DE_PARADA), encoding="utf-8").read())


class ASalaMostraBaseEPrecisao(unittest.TestCase):

    def linha(self, **kw):
        base = dict(zip(MS.NOMES, ["IT-T7-171", "derived:1", "2026-09-26 04:00:00+00",
                                   "2026-09-20", "PLATAFORMA", "DIA",
                                   "IT", "CONTRATO", "PAIS",
                                   "NAO SEI", "NAO SEI", "NAO SEI",
                                   "NAO SEI", "NAO SEI", "NAO SEI"]))
        base.update(kw)
        return [base[k] for k in MS.NOMES]

    def consulta(self, *linhas):
        self.sql = []
        return lambda q: self.sql.append(q) or list(linhas)

    def estado(self):
        return {"FONTES": [{"RUN_ID": _run(1)}]}

    def test_linha_limpa_passa_e_so_le_a_vista(self):
        s = MS.sala(self.estado(), consulta=self.consulta(self.linha()))
        self.assertTrue(s["PASSA"], s["MAL"])
        self.assertIn("from sala_de_espera_atual", self.sql[0])
        self.assertTrue(self.sql[0].startswith("select"))

    def test_valor_sem_base_reprova(self):
        s = MS.sala(self.estado(), consulta=self.consulta(self.linha(PUBLISHED_AT_BASIS="NAO SEI")))
        self.assertIn("PUBLISHED_AT", " ".join(s["MAL"]))

    def test_fact_time_copiado_do_captured_at_reprova(self):
        s = MS.sala(self.estado(), consulta=self.consulta(self.linha(
            FACT_TIME="2026-09-26 04:00:00+00", FACT_TIME_BASIS="TEXTO")))
        self.assertIn("fabricado", " ".join(s["MAL"]))

    def test_sala_vazia_nao_passa(self):
        self.assertFalse(MS.sala(self.estado(), consulta=self.consulta())["PASSA"])

    def test_run_id_estranho_nao_entra_na_consulta(self):
        with self.assertRaises(ValueError):
            MS.sala({"FONTES": [{"RUN_ID": "x') or 1=1 --"}]}, consulta=self.consulta())


if __name__ == "__main__":
    unittest.main(verbosity=2)


class OLote1EConferidoNoCodigo(unittest.TestCase):

    def test_arvore_sem_o_lote_1_diz_o_que_falta(self):
        tmp = tempfile.mkdtemp(prefix="lote1-")
        self.addCleanup(shutil.rmtree, tmp, True)
        self.assertEqual(len(MS.lote_1_instalado(__import__("pathlib").Path(tmp))), 4)

    def test_arvore_com_o_lote_1_passa(self):
        import pathlib
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="lote1-"))
        self.addCleanup(shutil.rmtree, str(tmp), True)
        for rel, txt in (("coleta/scrap_http.py", "def contar_pedido"),
                         ("coleta/scrap_colheita.py", "def escrever_linha"),
                         ("provas/prova_teto_dominio.py", 'MESMO_ORCAMENTO = {"googlevideo.com": "youtube.com"}'),
                         ("ferramentas/youtube_transcrever.py", "'--print-traffic',")):
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp / rel).write_text(txt, encoding="utf-8")
        self.assertEqual(MS.lote_1_instalado(tmp), [])
