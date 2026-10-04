# -*- coding: utf-8 -*-
"""LEGACY-99 C · o robo volta a medir as READY_LEGACY sozinho, pouco de cada vez.

Sem rede e sem escrever no livro real: o portao, a promocao e o `remedir` sao dublos.
"""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import gatilho_discovery as GD  # noqa: E402
import collection_gate as CG    # noqa: E402
import ready_split as RS        # noqa: E402

AGORA = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)


def _c(sid, url, estrategia="HTML_LINK_DISCOVERY"):
    return {"SOURCE_ID": sid, "ACQUISITION": {"STRATEGY": estrategia, "INDEX_URL": url}}


class Candidatas(unittest.TestCase):
    def cands(self, contratos, motivo, promovida=None):
        ctx = {"livro": {"TRANSICOES": []}, "contratos": {c["SOURCE_ID"]: c for c in contratos}}
        with mock.patch.object(CG, "avaliar", side_effect=lambda s, **k: {"MOTIVO": motivo[s]}), \
             mock.patch.object(RS, "ultima_promocao",
                               side_effect=lambda s, l: {"OBSERVED_AT": (promovida or {}).get(s, "")}):
            return GD.candidatas_legacy(ctx=ctx)

    def test_so_ready_legacy_com_contrato_html(self):
        cs = [_c("IT-T7-001", "https://a.it/"), _c("IT-T7-002", "https://b.it/"),
              _c("IT-T8-003", "https://www.youtube.com/feeds/videos.xml?c=1", "YOUTUBE_CHANNEL_FEED")]
        m = {"IT-T7-001": "READY_LEGACY", "IT-T7-002": "ELIGIBLE", "IT-T8-003": "READY_LEGACY"}
        self.assertEqual(["IT-T7-001"], [c["SOURCE_ID"] for c in self.cands(cs, m)])

    def test_a_mais_antiga_primeiro_e_com_o_dominio_registavel(self):
        cs = [_c("IT-T7-001", "https://www.cia.it/a"), _c("IT-T7-002", "https://toscana.cia.it/b"),
              _c("IT-T2-003", "https://www.arpa.veneto.it/")]
        m = dict.fromkeys(("IT-T7-001", "IT-T7-002", "IT-T2-003"), "READY_LEGACY")
        r = self.cands(cs, m, {"IT-T7-001": "2026-09-10", "IT-T7-002": "2026-09-01", "IT-T2-003": "2026-09-05"})
        self.assertEqual(["IT-T7-002", "IT-T2-003", "IT-T7-001"], [c["SOURCE_ID"] for c in r])
        self.assertEqual(["cia.it", "arpa.veneto.it", "cia.it"], [c["DOMINIO"] for c in r])


class Lote(unittest.TestCase):
    def test_um_por_dominio(self):
        cands = [{"SOURCE_ID": "A", "DOMINIO": "cia.it"}, {"SOURCE_ID": "B", "DOMINIO": "cia.it"},
                 {"SOURCE_ID": "C", "DOMINIO": "b.it"}]
        self.assertEqual(["A", "C"], GD.lote_legacy(cands))

    def test_no_maximo_o_lote(self):
        cands = [{"SOURCE_ID": str(i), "DOMINIO": "d%d.it" % i} for i in range(30)]
        self.assertEqual(GD.LEGACY_POR_LOTE, len(GD.lote_legacy(cands)))


class Quando(unittest.TestCase):
    def volta(self, e, agora, cands=({"SOURCE_ID": "A", "DOMINIO": "a.it"},)):
        self.chamadas = getattr(self, "chamadas", [])
        return GD.revalidar_legacy_se_devido(
            e, agora, candidatas_fn=lambda: list(cands),
            remedir_fn=lambda ids: (self.chamadas.append(list(ids)), [{"FEITO": True} for _ in ids])[1])

    def test_primeiro_lote_remede_pelo_caminho_canonico(self):
        e = {}
        r = self.volta(e, AGORA)
        self.assertEqual(("LEGACY_REMEDIDAS", ["A"], 1), (r["ACCAO"], r["LOTE"], r["FEITAS"]))
        self.assertEqual([["A"]], self.chamadas)

    def test_so_um_lote_por_intervalo(self):
        e = {}
        self.volta(e, AGORA)
        self.assertEqual("NADA", self.volta(e, AGORA + timedelta(hours=GD.LEGACY_INTERVALO_H) - timedelta(seconds=1))["ACCAO"])
        self.assertEqual("LEGACY_REMEDIDAS", self.volta(e, AGORA + timedelta(hours=GD.LEGACY_INTERVALO_H))["ACCAO"])
        self.assertEqual(2, len(self.chamadas))

    def test_sem_candidatas_nao_remede(self):
        r = self.volta({}, AGORA, cands=())
        self.assertEqual("SEM_LEGACY_A_REMEDIR", r["ACCAO"])
        self.assertEqual([], self.chamadas)

    def test_o_remedir_verdadeiro_e_o_de_ready_split(self):
        with mock.patch.object(RS, "remedir", return_value=[{"FEITO": True}]) as rm:
            GD.revalidar_legacy_se_devido({}, AGORA, candidatas_fn=lambda: [{"SOURCE_ID": "A", "DOMINIO": "a.it"}])
        self.assertEqual(["A"], rm.call_args.args[0])
        self.assertIn("READY_LEGACY", rm.call_args.kwargs["motivo"])


class NoSupervisor(unittest.TestCase):
    def _loop(self, rev, **kw):
        import supervisor as S
        eventos = []
        voltas = [("WORKER_OK", {}, None), ("WORKER_OK", {}, None), KeyboardInterrupt()]
        with mock.patch.object(S, "uma_volta_sup", side_effect=voltas), \
             mock.patch.object(S.time, "sleep"), \
             mock.patch.object(S, "_anotar", side_effect=eventos.append), \
             mock.patch.object(S, "_ler_estado", return_value={}), \
             mock.patch.object(S, "_gravar_estado"), \
             mock.patch.object(S.F, "recuperar_orfas", return_value=[]), \
             mock.patch.object(GD, "revalidar_legacy_se_devido", side_effect=rev), \
             mock.patch.object(RS, "remedir", side_effect=AssertionError("LIVRO REAL NUM TESTE")), \
             mock.patch("onboardar_rotas_provadas.onboardar_se_mudou", return_value={"ACCAO": "NADA_MUDOU"}):
            with self.assertRaises(KeyboardInterrupt):
                S._loop(1.0, 0, **kw)
        return eventos

    def test_por_omissao_o_loop_nao_remede_nada(self):
        chamadas = []
        self._loop(lambda e: (chamadas.append(1), {"ACCAO": "NADA"})[1])
        self.assertEqual([], chamadas)

    def test_ligado_corre_a_cada_volta_e_anota_so_quando_faz(self):
        ev = self._loop(lambda e: {"ACCAO": "LEGACY_REMEDIDAS", "LOTE": ["A"]}, revalidar_legacy=True)
        self.assertEqual(2, sum(1 for x in ev if x.get("EVENTO") == "REVALIDAR_LEGACY"))
        ev = self._loop(lambda e: {"ACCAO": "NADA"}, revalidar_legacy=True)
        self.assertEqual(0, sum(1 for x in ev if x.get("EVENTO") == "REVALIDAR_LEGACY"))

    def test_erro_fica_no_diario_e_o_supervisor_continua(self):
        def rebenta(e):
            raise RuntimeError("livro ilegivel")
        ev = self._loop(rebenta, revalidar_legacy=True)
        self.assertEqual(2, sum(1 for x in ev if x.get("EVENTO") == "REVALIDAR_LEGACY_ERRO"))

    def test_main_liga_e_a_opcao_desliga(self):
        import supervisor as S
        for argv, esperado in ((["s.py"], True), (["s.py", "--sem-revalidar-legacy"], False)):
            with mock.patch.object(sys, "argv", argv), mock.patch.object(S, "supervisionar", return_value=0) as sup:
                S.main()
            self.assertEqual(esperado, sup.call_args.kwargs["revalidar_legacy"])


if __name__ == "__main__":
    unittest.main()
