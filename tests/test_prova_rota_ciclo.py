# -*- coding: utf-8 -*-
"""PROVA-ROTA-CICLO · a prova de rota corre no ciclo do supervisor, com as guardas.

Sem rede: o portao de egresso, o lancamento do canario e o portao do Curator
sao dublos. O que se prova e QUEM entra na rodada, QUANDO ela sai e que NAO sai
sem portao PASS.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import prova_rota_ciclo as P   # noqa: E402
import sha_do_contrato as SHA  # noqa: E402

AGORA = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)


def _cur(sid, url):
    return {"SOURCE_ID": sid, "OUTPUT_TYPE": "HTML",
            "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL", "INDEX_URL": url,
                            "LINK_PATTERN": "^x$", "MAX_TARGETS": 1}}


def _prova(c, quando, sha=None):
    return {"SOURCE_ID": c["SOURCE_ID"], "VEREDITO": "ROUTE_PROVEN",
            "CONTRATO_SHA256": sha or SHA.do_contrato(c), "PROVADO_EM": quando.isoformat()}


class Dominio(unittest.TestCase):
    def test_o_dominio_registavel_junta_www_e_subdominios(self):
        for h in ("cia.it", "www.cia.it", "sub.cia.it", "CIA.IT."):
            self.assertEqual("cia.it", P.dominio_registavel(h))
        self.assertEqual("edagricole.it", P.dominio_registavel("terraevita.edagricole.it"))

    def test_sufixos_regionais_de_dois_niveis(self):
        self.assertEqual("regione.veneto.it", P.dominio_registavel("www.regione.veneto.it"))
        self.assertEqual("arpa.veneto.it", P.dominio_registavel("arpa.veneto.it"))
        self.assertEqual("crea.gov.it", P.dominio_registavel("www.crea.gov.it"))
        self.assertEqual("192.168.0.1", P.dominio_registavel("192.168.0.1"))

    def test_paridade_com_o_coletor_quando_ele_exporta_a_regra(self):
        mjs = RAIZ / "coleta" / "italy_pilot_collect.mjs"
        if "export function dominioRegistavel" not in mjs.read_text(encoding="utf-8"):
            self.skipTest("o coletor desta arvore ainda nao tem dominioRegistavel (ONDA2-G3 por instalar)")
        hosts = ["cia.it", "www.cia.it", "a.b.cia.it", "regione.veneto.it", "x.y.gov.it",
                 "terraevita.edagricole.it", "www.bbc.co.uk", "10.0.0.1", "localhost"]
        r = subprocess.run(["node", "-e", "import(process.argv[1]).then(m=>console.log(JSON.stringify("
                            "JSON.parse(process.argv[2]).map(m.dominioRegistavel))))",
                            mjs.as_uri(), json.dumps(hosts)], capture_output=True, text=True, timeout=60)
        self.assertEqual(json.loads(r.stdout), [P.dominio_registavel(h) for h in hosts])


class QuemPrecisa(unittest.TestCase):
    def precisa(self, elegiveis, curator, linhas, com_contrato=()):
        with mock.patch.object(P.G, "elegiveis", return_value=list(elegiveis)):
            return P.precisam_de_prova(agora=AGORA, ctx={}, curator={c["SOURCE_ID"]: c for c in curator},
                                       prova={"LINHAS": linhas}, com_contrato=set(com_contrato))

    def test_so_elegiveis(self):
        a, b = _cur("IT-T7-001", "https://a.it/"), _cur("IT-T7-002", "https://b.it/")
        self.assertEqual(["IT-T7-001"], self.precisa(["IT-T7-001"], [a, b], []))

    def test_quem_ja_tem_contrato_no_coletor_nao_precisa(self):
        a = _cur("IT-T7-001", "https://a.it/")
        self.assertEqual([], self.precisa(["IT-T7-001"], [a], [], com_contrato=["IT-T7-001"]))

    def test_prova_recente_do_contrato_de_agora_nao_precisa_mesmo_que_tenha_falhado(self):
        a = _cur("IT-T7-001", "https://a.it/")
        falhou = dict(_prova(a, AGORA - timedelta(days=1)), VEREDITO="CAPABILITY_BLOCK")
        self.assertEqual([], self.precisa(["IT-T7-001"], [a], [falhou]))

    def test_prova_de_outro_contrato_precisa(self):
        a = _cur("IT-T7-001", "https://a.it/")
        self.assertEqual(["IT-T7-001"], self.precisa(["IT-T7-001"], [a], [_prova(a, AGORA, sha="0" * 64)]))

    def test_prova_velha_precisa(self):
        a = _cur("IT-T7-001", "https://a.it/")
        velha = _prova(a, AGORA - P.ONB.PROVA_MAX_IDADE - timedelta(minutes=1))
        self.assertEqual(["IT-T7-001"], self.precisa(["IT-T7-001"], [a], [velha]))

    def test_nunca_provadas_primeiro_depois_a_mais_velha(self):
        a, b, c = (_cur("IT-T7-00%d" % i, "https://%s.it/" % n) for i, n in ((1, "a"), (2, "b"), (3, "c")))
        linhas = [_prova(a, AGORA - timedelta(days=9)), _prova(c, AGORA - timedelta(days=30))]
        self.assertEqual(["IT-T7-002", "IT-T7-003", "IT-T7-001"],
                         self.precisa(["IT-T7-001", "IT-T7-002", "IT-T7-003"], [a, b, c], linhas))


class Rodada(unittest.TestCase):
    def test_dominio_repetido_espera_pela_rodada_seguinte(self):
        cur = {s: _cur(s, u) for s, u in (("IT-T7-001", "https://www.cia.it/a"), ("IT-T7-002", "https://cia.it/b"),
                                          ("IT-T7-003", "https://toscana.cia.it/c"), ("IT-T7-004", "https://b.it/"))}
        self.assertEqual(["IT-T7-001", "IT-T7-004"], P.escolher_ronda(list(cur), cur))
        self.assertEqual(["IT-T7-002", "IT-T7-004"], P.escolher_ronda(["IT-T7-002", "IT-T7-003", "IT-T7-004"], cur))

    def test_no_maximo_ronda_max_fontes(self):
        cur = {"IT-T7-%03d" % i: _cur("IT-T7-%03d" % i, "https://d%d.it/" % i) for i in range(20)}
        self.assertEqual(P.RONDA_MAX_FONTES, len(P.escolher_ronda(sorted(cur), cur)))


class ProcFalso:
    def __init__(self, a_correr=True, rc=0):
        self.pid, self.returncode, self._a_correr, self.morto = 4242, None if a_correr else rc, a_correr, False

    def poll(self):
        if self._a_correr:
            return None
        self.returncode = 0 if self.returncode is None else self.returncode
        return self.returncode

    def kill(self):
        self.morto = True


class Ciclo(unittest.TestCase):
    def setUp(self):
        P._EM_CURSO.clear()
        self.lancadas = []

    def tearDown(self):
        P._EM_CURSO.clear()

    def volta(self, estado, agora, ronda=("IT-T7-001",), portao=(True, "EGRESS_GATE=PASS"), proc=None):
        return P.provar_se_devido(
            estado, agora=agora, planear_fn=lambda agora: list(ronda),
            portao_fn=lambda: portao,
            lancar_fn=lambda r: (self.lancadas.append(list(r)), proc or ProcFalso())[1])

    def test_rodada_sem_vpn_nao_sai_e_fica_escrito(self):
        e = {}
        r = self.volta(e, AGORA, portao=(False, "EGRESS_GATE=BLOCKED"))
        self.assertEqual("RONDA_NAO_SAIU", r["ACCAO"])
        self.assertIn("BLOCKED", r["PORQUE"])
        self.assertEqual([], self.lancadas)
        self.assertIsNone(e.get("PROVA_ROTA_PID"))

    def test_com_portao_pass_lanca_o_canario_com_a_rodada(self):
        e = {}
        r = self.volta(e, AGORA)
        self.assertEqual(("RONDA_LANCADA", [["IT-T7-001"]]), (r["ACCAO"], self.lancadas))
        self.assertEqual(4242, e["PROVA_ROTA_PID"])

    def test_sem_fontes_nao_pergunta_ao_portao_nem_lanca(self):
        perguntas = []
        r = P.provar_se_devido({}, agora=AGORA, planear_fn=lambda a: [],
                               portao_fn=lambda: (perguntas.append(1), (True, ""))[1],
                               lancar_fn=lambda r: self.fail("nao devia lancar"))
        self.assertEqual(("SEM_FONTES_A_PROVAR", []), (r["ACCAO"], perguntas))

    def test_rodada_em_curso_nao_lanca_outra(self):
        e = {}
        self.volta(e, AGORA)
        r = self.volta(e, AGORA + timedelta(minutes=5))
        self.assertEqual("RONDA_EM_CURSO", r["ACCAO"])
        self.assertEqual(1, len(self.lancadas))

    def test_rodada_presa_e_terminada_ao_fim_do_tempo_maximo(self):
        e, p = {}, ProcFalso()
        self.volta(e, AGORA, proc=p)
        r = self.volta(e, AGORA + P.RONDA_TEMPO_MAXIMO + timedelta(seconds=1))
        self.assertEqual("RONDA_TERMINADA_POR_TEMPO", r["ACCAO"])
        self.assertTrue(p.morto)

    def test_intervalo_entre_rodadas_conta_do_fim(self):
        e, p = {}, ProcFalso()
        self.volta(e, AGORA, proc=p)
        p._a_correr = False
        fim = AGORA + timedelta(minutes=3)
        self.assertEqual("RONDA_ACABOU", self.volta(e, fim)["ACCAO"])
        self.assertEqual("NADA", self.volta(e, fim + P.RONDA_INTERVALO - timedelta(seconds=1))["ACCAO"])
        self.assertEqual("RONDA_LANCADA", self.volta(e, fim + P.RONDA_INTERVALO)["ACCAO"])
        self.assertEqual(2, len(self.lancadas))

    def test_portao_blocked_tambem_espera_o_intervalo_para_voltar_a_tentar(self):
        e = {}
        self.volta(e, AGORA, portao=(False, "EGRESS_GATE=BLOCKED"))
        self.assertEqual("NADA", self.volta(e, AGORA + timedelta(minutes=1))["ACCAO"])

    def test_reinicio_do_supervisor_com_rodada_do_anterior_espera(self):
        e = {"PROVA_ROTA_PID": 999, "PROVA_ROTA_DESDE": AGORA.isoformat()}
        self.assertEqual("RONDA_DE_OUTRO_PROCESSO_A_ESPERA",
                         self.volta(e, AGORA + timedelta(minutes=10))["ACCAO"])
        self.assertEqual("RONDA_ACABOU", self.volta(e, AGORA + P.RONDA_TEMPO_MAXIMO + timedelta(seconds=1))["ACCAO"])
        self.assertEqual([], self.lancadas)

    def test_o_portao_real_sem_resposta_legivel_nao_e_pass(self):
        with mock.patch.object(P.subprocess, "run", side_effect=OSError("sem python")):
            ok, porque = P.portao_de_egresso()
        self.assertFalse(ok)
        self.assertIn("sem resposta legivel", porque)

    def test_o_portao_real_so_aceita_pass(self):
        for v, esperado in (("PASS", True), ("BLOCKED", False), ("UNKNOWN", False)):
            fake = mock.Mock(stdout='lixo antes\n{"EGRESS_GATE": "%s"}' % v)
            with mock.patch.object(P.subprocess, "run", return_value=fake):
                self.assertEqual(esperado, P.portao_de_egresso()[0])


class NoSupervisor(unittest.TestCase):
    def _loop(self, prova, onboard, **kw):
        import supervisor as S
        eventos = []
        rede = AssertionError("REDE NUM TESTE: lancar/portao reais nao se chamam aqui")
        voltas = [("WORKER_OK", {}, None), ("WORKER_OK", {}, None), KeyboardInterrupt()]
        with mock.patch.object(S, "uma_volta_sup", side_effect=voltas), \
             mock.patch.object(S.time, "sleep"), \
             mock.patch.object(S, "_anotar", side_effect=eventos.append), \
             mock.patch.object(S, "_ler_estado", return_value={}), \
             mock.patch.object(S, "_gravar_estado"), \
             mock.patch.object(S.F, "recuperar_orfas", return_value=[]), \
             mock.patch.object(P, "provar_se_devido", side_effect=prova), \
             mock.patch.object(P.ONB, "onboardar_se_mudou", side_effect=onboard), \
             mock.patch.object(P, "lancar", side_effect=rede), \
             mock.patch.object(P, "portao_de_egresso", side_effect=rede):
            with self.assertRaises(KeyboardInterrupt):
                S._loop(1.0, 0, **kw)
        return eventos

    def test_por_omissao_o_loop_nao_vai_a_rede(self):
        # o incidente de 25/09 08:01Z: testes que corriam `_loop` lancaram canarios reais
        ordem = []
        self._loop(lambda e: (ordem.append("prova"), {"ACCAO": "NADA"})[1],
                   lambda e: (ordem.append("onboard"), {"ACCAO": "NADA_MUDOU"})[1])
        self.assertEqual(["onboard", "onboard"], ordem)

    def test_main_liga_a_prova_de_rota_e_a_opcao_desliga(self):
        import supervisor as S
        for argv, esperado in ((["supervisor.py"], True), (["supervisor.py", "--sem-prova-de-rota"], False)):
            with mock.patch.object(sys, "argv", argv), \
                 mock.patch.object(S, "supervisionar", return_value=0) as sup:
                S.main()
            self.assertEqual(esperado, sup.call_args.kwargs["prova_de_rota"])

    def test_supervisionar_passa_a_escolha_ao_loop(self):
        import supervisor as S
        with mock.patch.object(S, "_adquirir_lock", return_value=1), \
             mock.patch.object(S, "_libertar_lock"), \
             mock.patch.object(S, "_loop", return_value=0) as lp:
            S.supervisionar(1.0, 0, prova_de_rota=True)
        self.assertTrue(lp.call_args.kwargs["prova_de_rota"])

    def test_o_supervisor_chama_a_prova_de_rota_antes_do_onboarding_em_cada_volta(self):
        ordem = []
        self._loop(lambda e: (ordem.append("prova"), {"ACCAO": "NADA"})[1],
                   lambda e: (ordem.append("onboard"), {"ACCAO": "NADA_MUDOU"})[1], prova_de_rota=True)
        self.assertEqual(["prova", "onboard", "prova", "onboard"], ordem)

    def test_erro_da_prova_fica_no_diario_e_o_onboarding_continua(self):
        onboard = []

        def rebenta(e):
            raise RuntimeError("canario ilegivel")
        ev = self._loop(rebenta, lambda e: (onboard.append(1), {"ACCAO": "NADA_MUDOU"})[1], prova_de_rota=True)
        self.assertEqual(2, sum(1 for x in ev if x.get("EVENTO") == "PROVA_ROTA_ERRO"))
        self.assertEqual(2, len(onboard))

    def test_rodada_que_nao_saiu_fica_no_diario(self):
        ev = self._loop(lambda e: {"ACCAO": "RONDA_NAO_SAIU", "PORQUE": "EGRESS_GATE=BLOCKED"},
                        lambda e: {"ACCAO": "NADA_MUDOU"}, prova_de_rota=True)
        self.assertEqual(2, sum(1 for x in ev if x.get("EVENTO") == "PROVA_ROTA"
                                and x.get("ACCAO") == "RONDA_NAO_SAIU"))


if __name__ == "__main__":
    unittest.main()
