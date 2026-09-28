#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESTEIRA-SOZINHA — a passagem para a Sala, o gatilho da Intelligence e o vigia, sem rede e sem banco.

    python3 -m unittest tests.test_esteira_sozinha -v

Tudo corre em pastas temporarias: nenhum teste le ou escreve PARAR.flag, travas, estado do supervisor,
o livro de decisoes ou o pote do casco verdadeiros. O banco e trocado por dublos (o ensaio com
Postgres real e `provas/esteira_sozinha/ensaio_ponta_a_ponta.py`).
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "curadoria"))
import _gavetas  # noqa: E402,F401

import sala_de_espera as espera                  # noqa: E402
import gatilho_da_inteligencia as GI             # noqa: E402
import passagem_para_a_sala as PAS               # noqa: E402
import vigia_da_esteira as VIG                   # noqa: E402

AGORA = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
CORRIDA_VALIDA = RAIZ / "tests" / "fixtures" / "pote" / "CORRIDA-SINTETICA-V2-UNICO.json"
EXPORT_R7 = RAIZ / "tests" / "dados" / "int-r7" / "SINTETICO-R7-SALA-EXPORT.json"


class _Pasta(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="esteira-"))
        self.parar = self.d / "PARAR.flag"
        self.trinco = self.d / "TRINCO"
        self.destino = self.d / "client" / "sintonia-pote.js"

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)


def _consulta(n, velho=None, novo=None):
    def c(sql):
        c.sqls.append(sql)
        return [[str(n), velho or "", novo or ""]]
    c.sqls = []
    return c


# ── GATILHO: a regra ─────────────────────────────────────────────────────────
class TestRegraDoGatilho(unittest.TestCase):
    def test_sem_delta_espera(self):
        self.assertEqual(GI.decidir({"NOVOS": 0}, AGORA)["PORQUE"], "SEM_DELTA")

    def test_dez_novos_corre(self):
        d = GI.decidir({"NOVOS": 10, "MAIS_VELHO_EM": AGORA.isoformat()}, AGORA)
        self.assertEqual(d["DECISAO"], GI.CORRER)

    def test_nove_recentes_esperam(self):
        d = GI.decidir({"NOVOS": 9, "MAIS_VELHO_EM": (AGORA - timedelta(hours=3, minutes=59)).isoformat()}, AGORA)
        self.assertEqual(d["DECISAO"], GI.ESPERAR)
        self.assertIn("ABRE_EM", d)

    def test_um_novo_com_quatro_horas_corre(self):
        d = GI.decidir({"NOVOS": 1, "MAIS_VELHO_EM": (AGORA - timedelta(hours=4)).isoformat()}, AGORA)
        self.assertEqual(d["DECISAO"], GI.CORRER)

    def test_delta_nao_medido_e_nao_sei_e_nao_zero(self):
        self.assertEqual(GI.decidir({"NOVOS": None}, AGORA)["DECISAO"], GI.NAO_SEI)

    def test_recuo_depois_de_falha(self):
        d = GI.decidir({"NOVOS": 50}, AGORA, {"INT_ULTIMA_FALHA_EM": (AGORA - timedelta(minutes=5)).isoformat()})
        self.assertEqual(d["PORQUE"], "RECUO_DEPOIS_DE_FALHA")

    def test_timestamptz_do_psql_le_se(self):
        self.assertEqual(GI._quando("2026-09-28 10:00:00.5+00"),
                         datetime(2026, 9, 28, 10, 0, 0, 500000, tzinfo=timezone.utc))

    def test_delta_conta_depois_da_marca(self):
        c = _consulta(3, "2026-09-28 07:00:00+00", "2026-09-28 11:00:00+00")
        d = GI.medir_delta(c, "2026-09-28T06:00:00+00:00")
        self.assertEqual(d["NOVOS"], 3)
        self.assertIn("pousado_em > '2026-09-28T06:00:00+00:00'", c.sqls[0])


# ── GATILHO: a volta ─────────────────────────────────────────────────────────
class TestVoltaDoGatilho(_Pasta):
    def _volta(self, estado, n=12, **kw):
        chamadas = {"copia": 0, "motor": 0}

        def copia(_p):
            chamadas["copia"] += 1
            return json.loads(EXPORT_R7.read_text(encoding="utf-8"))

        def motor(export, hoje, head):
            chamadas["motor"] += 1
            return json.loads(CORRIDA_VALIDA.read_text(encoding="utf-8"))

        subir = kw.pop("subir", lambda s, pasta, parar: GI.subir_o_pote(s, self.destino, pasta, parar))
        r = GI.correr_se_devido(estado, agora=AGORA, consulta=_consulta(n, "2026-09-28 01:00:00+00",
                                                                        "2026-09-28 11:00:00+00"),
                                copia=copia, motor=motor, subir=subir, parar=self.parar,
                                trinco=self.trinco, pasta=self.d / "esteira", **kw)
        return r, chamadas

    def test_sem_delta_o_motor_nao_corre(self):
        r, ch = self._volta({}, n=0)
        self.assertEqual(r["ACCAO"], "ESPERA")
        self.assertEqual(ch, {"copia": 0, "motor": 0})

    def test_pote_valido_sobe_e_a_marca_anda(self):
        est = {}
        r, ch = self._volta(est)
        self.assertEqual(r["ACCAO"], "POTE_SUBIU", r)
        self.assertTrue(self.destino.exists())
        self.assertEqual(est["INT_MARCA"], "2026-09-28T11:00:00+00:00")
        self.assertEqual(est["INT_ULTIMA_SUBIDA_EM"], AGORA.isoformat())
        self.assertFalse((self.destino.parent / ".sintonia-pote.candidato.js").exists())

    def test_pote_reprovado_nao_sobe(self):
        self.destino.parent.mkdir(parents=True)
        self.destino.write_text("window.SINTONIA_POTE = {\"ANTIGO\": 1};", encoding="utf-8")
        antes = self.destino.read_bytes()
        est = {}
        with mock.patch.object(GI.VP, "validar", return_value=["LEI: violacao plantada"]):
            r, _ = self._volta(est)
        self.assertEqual(r["ACCAO"], "POTE_NAO_SUBIU", r)
        self.assertEqual(r["PORQUE"], "POTE_REPROVADO")
        self.assertEqual(self.destino.read_bytes(), antes)
        self.assertNotIn("INT_ULTIMA_SUBIDA_EM", est)
        self.assertFalse((self.destino.parent / ".sintonia-pote.candidato.js").exists())

    def test_duas_corridas_sobrepostas_a_segunda_fica_ocupada(self):
        with espera._Trava(str(self.trinco)):
            r, ch = self._volta({})
        self.assertEqual(r["ACCAO"], "OCUPADO")
        self.assertEqual(ch, {"copia": 0, "motor": 0})

    def test_parar_flag_nao_mede_nem_corre(self):
        self.parar.write_text("parar", encoding="utf-8")
        r, ch = self._volta({})
        self.assertEqual(r["ACCAO"], "PARAR_FLAG")
        self.assertEqual(ch["motor"], 0)

    def test_copia_sem_prova_vale_nao_corre_o_motor(self):
        est = {}
        r = GI.correr_se_devido(est, agora=AGORA, consulta=_consulta(12, "2026-09-28 01:00:00+00"),
                                copia=lambda p: None, motor=lambda *a: self.fail("motor sem copia"),
                                parar=self.parar, trinco=self.trinco, pasta=self.d)
        self.assertEqual(r["ACCAO"], "COPIA_NAO_VALE")
        self.assertIn("INT_ULTIMA_FALHA_EM", est)
        self.assertNotIn("INT_MARCA", est)

    def test_a_sala_so_e_perguntada_de_5_em_5_minutos(self):
        est = {"INT_MEDIDO_EM": (AGORA - timedelta(minutes=1)).isoformat()}
        r, ch = self._volta(est)
        self.assertEqual(r["ACCAO"], "NADA")

    def _psql_falso(self, read_only):
        """Um psql de mentira que escreve o export no `-o`, com o READ_ONLY que o banco diria."""
        exe = self.d / "psql"
        exe.write_text("#!%s\nimport sys, json\na = sys.argv\nopen(a[a.index('-o') + 1], 'w').write("
                       "json.dumps({'READ_ONLY': %r, 'LINHAS': []}))\n" % (sys.executable, read_only),
                       encoding="utf-8")
        exe.chmod(0o755)
        return str(exe)

    @unittest.skipIf(os.name == "nt", "psql falso em shebang")
    def test_export_so_serve_com_read_only_on(self):
        self.assertEqual(GI.exportar("postgresql://x@127.0.0.1/y", self.d / "e.json",
                                     self._psql_falso("on"))["READ_ONLY"], "on")
        with self.assertRaises(RuntimeError):
            GI.exportar("postgresql://x@127.0.0.1/y", self.d / "e2.json", self._psql_falso("off"))

    def test_o_motor_verdadeiro_sobre_o_export_r7_e_o_fiscal_decide(self):
        # O motor e o gerador de HOJE: o que o fiscal disser, o gatilho obedece.
        saida = GI.correr_o_motor(json.loads(EXPORT_R7.read_text(encoding="utf-8")),
                                  AGORA.date(), "TESTE")
        r = GI.subir_o_pote(saida, self.destino, self.d / "p", self.parar)
        viol = GI.VP.validar(GI.P.ler_entrada(saida))
        self.assertEqual(r["SUBIU"], not viol)
        self.assertEqual(self.destino.exists(), not viol)


# ── PASSAGEM ─────────────────────────────────────────────────────────────────
def _livro_das_corridas(raiz: Path, corridas):
    p = raiz / PAS.LIVRO_DAS_CORRIDAS
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(c) + "\n" for c in corridas), encoding="utf-8")


class TestPassagem(_Pasta):
    def setUp(self):
        super().setUp()
        fim = (AGORA - timedelta(minutes=10)).isoformat()
        _livro_das_corridas(self.d, [
            {"RUN_ID": "R-T3", "FINISHED_AT": fim},
            {"RUN_ID": "R-T8", "FINISHED_AT": fim},
            {"RUN_ID": "R-VARIAS", "FINISHED_AT": fim},
            {"RUN_ID": "R-JULGADA", "FINISHED_AT": fim},
            {"RUN_ID": "R-ABERTA", "FINISHED_AT": None},
            {"RUN_ID": "R-VELHA", "FINISHED_AT": "2026-09-01T00:00:00+00:00"},
        ])
        self.livro = self.d / "LIVRO.json"
        self.livro.write_text(json.dumps({"DECISOES": [{"corrida": "R-JULGADA", "resultado": "SIM"}]}),
                              encoding="utf-8")
        self.obs = {"R-T3": ["IT-T3-010"], "R-T8": ["IT-T8-021"], "R-VARIAS": ["IT-T3-002", "IT-T7-017"],
                    "R-JULGADA": ["IT-T7-017"], "R-VELHA": ["IT-T3-010"]}
        self.estado = {"PAS_DESDE": "2026-09-20T00:00:00+00:00"}

    def _obs(self, run, _raiz):
        return [{"SOURCE_ID": s} for s in self.obs.get(run, [])]

    def _volta(self, backup, lancar, **kw):
        with mock.patch.object(PAS, "passar_uma",
                               side_effect=lambda l, lanc, livro: dict(lanc(l), COLHEITA_DA_CORRIDA=l["RUN_ID"])):
            return PAS.passar_se_devido(self.estado, agora=AGORA, raizes=[self.d], livro=self.livro,
                                        observacoes=self._obs, backup=backup, lancar=lancar,
                                        precondicoes=lambda: [], parar=self.parar, trinco=self.trinco,
                                        pasta=self.d / "p", **kw)

    def test_o_plano_diz_porque_cada_uma_fica(self):
        p = PAS.planear(self.estado, AGORA, [self.d], self.livro, self._obs)
        self.assertEqual([x["RUN_ID"] for x in p["PASSAR"]], ["R-T3"])
        fica = {x["RUN_ID"]: x["PORQUE"] for x in p["FICA"]}
        self.assertEqual(fica, {"R-T8": PAS.SEM_REGUA, "R-VARIAS": PAS.VARIAS_FONTES,
                                "R-JULGADA": PAS.JA_PASSOU, "R-ABERTA": PAS.ABERTA})

    def test_t8_e_t12_nao_tem_regua_na_admissao(self):
        # A causa A da R03, medida na regua e nao escrita a mao.
        self.assertNotIn("T8", PAS.adm.PERGUNTAS_DO_UNIVERSO)
        self.assertNotIn("T12", PAS.adm.PERGUNTAS_DO_UNIVERSO)
        self.assertEqual(PAS.adm.decidir({"id": "x", "url": "https://x.it/a", "source_id": "IT-T8-021",
                                          "texto": "vite peronospora trattamento"}, "T8").resultado,
                         PAS.adm.NAO_SE_APLICA)

    def test_sem_prova_vale_nada_se_grava(self):
        lancados = []
        r = self._volta(lambda p: {"PROVA_VALE": False}, lambda cmd: lancados.append(cmd) or {})
        self.assertEqual(r["ACCAO"], "BACKUP_NAO_VALE")
        self.assertEqual(lancados, [])
        self.assertIn("PAS_ULTIMA_FALHA_EM", self.estado)

    def test_com_prova_vale_passa_uma_vez_e_so_uma(self):
        lancados = []
        r = self._volta(lambda p: {"PROVA_VALE": True, "DUMP": "x.dump"},
                        lambda l: lancados.append(l["RUN_ID"]) or {"CODIGO": 0})
        self.assertEqual(r["ACCAO"], "PASSOU", r)
        self.assertEqual(lancados, ["R-T3"])
        r2 = self._volta(lambda p: {"PROVA_VALE": True}, lambda l: lancados.append(l["RUN_ID"]) or {},
                         forcar=True)
        self.assertEqual(r2["ACCAO"], "NADA_A_PASSAR")
        self.assertEqual(lancados, ["R-T3"])

    def test_o_backup_vem_antes_da_escrita(self):
        ordem = []
        self._volta(lambda p: ordem.append("BACKUP") or {"PROVA_VALE": True},
                    lambda l: ordem.append("PORTA") or {})
        self.assertEqual(ordem, ["BACKUP", "PORTA"])

    def test_um_so_escritor(self):
        with espera._Trava(str(self.trinco)):
            r = self._volta(lambda p: self.fail("backup com outro escritor"), lambda l: self.fail("porta"))
        self.assertEqual(r["ACCAO"], "OCUPADO")

    def test_parar_flag(self):
        self.parar.write_text("x", encoding="utf-8")
        r = self._volta(lambda p: self.fail("backup"), lambda l: self.fail("porta"))
        self.assertEqual(r["ACCAO"], "PARAR_FLAG")

    def test_primeira_volta_nao_leva_o_passado(self):
        self.estado = {}
        r = self._volta(lambda p: self.fail("backup"), lambda l: self.fail("porta"))
        self.assertEqual(r["ACCAO"], "NADA_A_PASSAR")
        self.assertEqual(self.estado["PAS_DESDE"], AGORA.isoformat())

    def test_o_pedido_a_porta_e_o_da_rodada(self):
        linha = {"RUN_ID": "R-T3", "FONTE": "IT-T3-010", "UNIVERSO": "T3", "RAIZ": str(self.d)}
        visto = {}
        with mock.patch("coleta.italy_executor.colher", return_value={"OBSERVACOES_DESTA_CORRIDA": 2}):
            r = PAS.passar_uma(linha, lambda cmd: visto.setdefault("cmd", cmd) and
                               {"CODIGO": 0, "SAIDA": "CORRIDA SUCCESS · IT-T3-NOVA"}, self.livro)
        mc = PAS._mc()
        self.assertEqual(visto["cmd"], mc.comando("IT-T3-010") + ["--so-a-porta", "--colheita-da-corrida=R-T3"])
        self.assertEqual(r["CORRIDA_DA_PORTA"], "IT-T3-NOVA")


# ── VIGIA ────────────────────────────────────────────────────────────────────
class TestVigia(_Pasta):
    def _marcas(self, **horas):
        out = {}
        for nome, _n, _c in VIG.ETAPAS:
            h = horas.get(nome, 0.5)
            out[nome] = (lambda h=h: ((AGORA - timedelta(hours=h)).isoformat() if h is not None else None, "teste"))
        return out

    def test_tudo_andando_sem_alerta(self):
        r = VIG.medir(AGORA, self._marcas(), {})
        self.assertFalse(r["ALERTA"], r["ALERTAS"])
        self.assertEqual(r["ETAPAS"]["portal_publico"]["ESTADO"], VIG.NAO_SEI)

    def test_etapa_alem_de_n_horas_alerta(self):
        r = VIG.medir(AGORA, self._marcas(coleta=30), {})
        self.assertTrue(r["ALERTA"])
        self.assertEqual([(a["ETAPA"], a["ESTADO"]) for a in r["ALERTAS"]], [("coleta", VIG.PARADA)])

    def test_marca_ilegivel_nao_e_silencio(self):
        r = VIG.medir(AGORA, self._marcas(sala=None), {})
        self.assertIn(("sala", VIG.NAO_SEI), [(a["ETAPA"], a["ESTADO"]) for a in r["ALERTAS"]])

    def test_marca_que_rebenta_nao_e_silencio(self):
        m = self._marcas()
        m["intelligence"] = lambda: 1 / 0
        r = VIG.medir(AGORA, m, {})
        self.assertIn("intelligence", [a["ETAPA"] for a in r["ALERTAS"]])

    def test_a_montante(self):
        r = VIG.medir(AGORA, self._marcas(sala=100, intelligence=100), {})
        self.assertEqual(r["ETAPAS"]["intelligence"]["CAUSA_PROVAVEL"], "A_MONTANTE (sala)")

    def test_de_hora_a_hora_e_escreve_o_ficheiro(self):
        est = {}
        s, h = self.d / "S.json", self.d / "H.ndjson"
        r = VIG.vigiar_se_devido(est, agora=AGORA, marcas=self._marcas(pote=50), saude=s, historico=h)
        self.assertEqual(r["ACCAO"], "ESCREVEU")
        self.assertTrue(json.loads(s.read_text(encoding="utf-8"))["ALERTA"])
        r = VIG.vigiar_se_devido(est, agora=AGORA + timedelta(minutes=59), marcas=self._marcas(),
                                 saude=s, historico=h)
        self.assertEqual(r["ACCAO"], "NADA")
        r = VIG.vigiar_se_devido(est, agora=AGORA + timedelta(hours=1), marcas=self._marcas(),
                                 saude=s, historico=h)
        self.assertEqual(r["ACCAO"], "ESCREVEU")
        self.assertEqual(len(h.read_text(encoding="utf-8").splitlines()), 2)


# ── O SUPERVISOR: extensao, e nao segundo orquestrador ───────────────────────
class TestGanchoNoSupervisor(unittest.TestCase):
    def _loop(self, esteira, passos):
        import supervisor as S
        eventos = []
        voltas = [("IDLE", {}, None), ("PARA_FLAG", {}, None)]
        with mock.patch.object(S, "uma_volta_sup", side_effect=voltas), \
             mock.patch.object(S.time, "sleep"), \
             mock.patch.object(S, "_anotar", side_effect=eventos.append), \
             mock.patch.object(S, "_ler_estado", return_value={}), \
             mock.patch.object(S, "_gravar_estado"), \
             mock.patch.object(S.F, "recuperar_orfas", return_value=[]), \
             mock.patch.object(S, "_passos_da_esteira", return_value=passos), \
             mock.patch("onboardar_rotas_provadas.onboardar_se_mudou", return_value={"ACCAO": "NADA_MUDOU"}), \
             tempfile.TemporaryDirectory() as t:
            parar = Path(t) / "PARAR.flag"
            parar.write_text("teste", encoding="utf-8")   # o loop le o motivo quando sai
            with mock.patch.object(S, "PARAR", parar):
                S._loop(1.0, 0, esteira=esteira)
        return eventos

    def test_o_servico_chama_os_tres_passos_pela_ordem(self):
        chamados = []
        passos = tuple((n, (lambda e, n=n: chamados.append(n) or {"ACCAO": "X"}))
                       for n in ("PASSAGEM", "INTELLIGENCE", "VIGIA"))
        ev = self._loop(True, passos)
        self.assertEqual(chamados, ["PASSAGEM", "INTELLIGENCE", "VIGIA"])
        self.assertEqual([e["PASSO"] for e in ev if e.get("EVENTO") == "ESTEIRA"],
                         ["PASSAGEM", "INTELLIGENCE", "VIGIA"])

    def test_sem_esteira_nada_corre(self):
        ev = self._loop(False, (("X", lambda e: self.fail("correu sem o servico o ligar")),))
        self.assertFalse([e for e in ev if e.get("EVENTO", "").startswith("ESTEIRA")])

    def test_passo_que_rebenta_nao_derruba_o_supervisor(self):
        chamados = []
        passos = (("PASSAGEM", lambda e: 1 / 0),
                  ("VIGIA", lambda e: chamados.append(1) or {"ACCAO": "ESCREVEU"}))
        ev = self._loop(True, passos)
        self.assertEqual(chamados, [1])
        self.assertIn("ESTEIRA_ERRO", [e.get("EVENTO") for e in ev])

    def test_main_liga_a_esteira_e_ha_como_a_desligar(self):
        import supervisor as S
        with mock.patch.object(S, "supervisionar", return_value=0) as sup, \
             mock.patch.object(sys, "argv", ["supervisor.py"]):
            S.main()
        self.assertTrue(sup.call_args.kwargs["esteira"])
        with mock.patch.object(S, "supervisionar", return_value=0) as sup, \
             mock.patch.object(sys, "argv", ["supervisor.py", "--sem-esteira"]):
            S.main()
        self.assertFalse(sup.call_args.kwargs["esteira"])


if __name__ == "__main__":
    unittest.main()
