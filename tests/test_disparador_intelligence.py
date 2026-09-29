#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L2-DISPARADOR-INTELLIGENCE (D140) — o gatilho da Intelligence, o corte vigente, a entrega ao casco,
a volta agendada, a retencao e o vigia. Sem rede e sem banco.

    python3 -m unittest tests.test_disparador_intelligence -v

Portado da ESTEIRA-SOZINHA (f85b4138a, tests/test_esteira_sozinha.py) SO no que foi portado: a regra e a
volta do gatilho, a retencao e o vigia. A passagem armazem -> Sala e o gancho no supervisor NAO foram
portados, e os testes deles tambem nao. O que e novo aqui: o corte vigente (ITEM_ID repetido na Sala),
a prova de que o disparador nunca escreve na Sala nem marca consumido_em, a entrega com MANIFESTO e
SHA256SUMS, e a volta agendada (estado, trinco da volta, DSN so pelo nome).

Tudo corre em pastas temporarias: nenhum teste le ou escreve PARAR.flag, travas, o estado do disparador
ou o pote do casco verdadeiros. O ensaio com Postgres real e `provas/l2/ensaio_disparador.py`.
"""
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import sala_de_espera as espera                  # noqa: E402
import gatilho_da_inteligencia as GI             # noqa: E402
import vigia_da_esteira as VIG                   # noqa: E402

AGORA = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
CORRIDA_VALIDA = RAIZ / "tests" / "fixtures" / "pote" / "CORRIDA-SINTETICA-V2-UNICO.json"
EXPORT_R7 = RAIZ / "tests" / "dados" / "int-r7" / "SINTETICO-R7-SALA-EXPORT.json"


class _Pasta(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="disparador-"))
        self.parar = self.d / "PARAR.flag"
        self.trinco = self.d / "TRINCO"
        self.entrega = self.d / "esteira" / "PARA-O-CASCO"

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def _subir(self):
        return lambda s, pasta, parar: GI.subir_o_pote(s, pasta, parar, entrega=self.entrega)


def _corrida_da_lei():
    """DUBLE do motor: a corrida sintetica valida do dono do pote (tests/fixtures/pote), TAL COMO ESTA.
    D-GER-1-MIG (29/09): o ENTITY_SOURCE dela passou a UNKNOWN, valor da COL-LAW-221 — ja nao se troca
    nada aqui. Se a fixture voltar a texto livre, o gerador recusa-a e estes testes caem (mutante L61)."""
    return json.loads(CORRIDA_VALIDA.read_text(encoding="utf-8"))


def _consulta(n, velho=None, novo=None):
    def c(sql):
        c.sqls.append(sql)
        return [[str(n), velho or "", novo or ""]]
    c.sqls = []
    return c


def _export_com_repetido():
    """O export da fixture R7 + a MESMA linha pousada por outra corrida (o defeito medido na Sala real)."""
    exp = json.loads(EXPORT_R7.read_text(encoding="utf-8"))
    l0 = dict(exp["LINHAS"][0])
    outra = dict(l0, run_id="ZZ-OUTRA-CORRIDA", ordem=1)
    exp["LINHAS"].append(outra)
    pousos = [{"run_id": l["run_id"], "ordem": l["ordem"], "item_id": l["item_id"],
               "pousado_em": "2026-09-27 10:00:00+00"} for l in exp["LINHAS"]]
    pousos[-1]["pousado_em"] = "2026-09-28 09:00:00.5+00"         # a corrida nova e a vigente
    exp["POUSOS_DA_COPIA"] = pousos
    return exp, l0["item_id"]


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
    def _volta(self, estado, n=12, export=None, **kw):
        chamadas = {"copia": 0, "motor": 0, "export_do_motor": None}

        def copia(_p):
            chamadas["copia"] += 1
            return export if export is not None else json.loads(EXPORT_R7.read_text(encoding="utf-8"))

        def motor(exp, hoje, head):
            chamadas["motor"] += 1
            chamadas["export_do_motor"] = exp
            return _corrida_da_lei()

        subir = kw.pop("subir", self._subir())
        r = GI.correr_se_devido(estado, agora=AGORA, consulta=_consulta(n, "2026-09-28 01:00:00+00",
                                                                        "2026-09-28 11:00:00+00"),
                                copia=copia, motor=kw.pop("motor", motor), subir=subir, parar=self.parar,
                                trinco=self.trinco, pasta=self.d / "esteira", **kw)
        return r, chamadas

    def test_sem_delta_o_motor_nao_corre(self):
        r, ch = self._volta({}, n=0)
        self.assertEqual(r["ACCAO"], "ESPERA")
        self.assertEqual(r["PORQUE"], "SEM_DELTA")
        self.assertEqual((ch["copia"], ch["motor"]), (0, 0))

    def test_pote_valido_sobe_e_a_marca_anda(self):
        est = {}
        r, ch = self._volta(est)
        self.assertEqual(r["ACCAO"], "POTE_SUBIU", r)
        self.assertTrue((self.entrega / "POTE.json").exists())
        self.assertEqual(est["INT_MARCA"], "2026-09-28T11:00:00+00:00")
        self.assertEqual(est["INT_ULTIMA_SUBIDA_EM"], AGORA.isoformat())
        self.assertEqual(list((self.d / "esteira").rglob(".POTE.candidato.json")), [])

    def test_pote_reprovado_nao_sobe_e_a_entrega_nao_muda(self):
        self.entrega.mkdir(parents=True)
        (self.entrega / "POTE.json").write_text("{\"ANTIGO\": 1}", encoding="utf-8")
        antes = (self.entrega / "POTE.json").read_bytes()
        est = {}
        with mock.patch.object(GI.VP, "validar", return_value=["LEI: violacao plantada"]):
            r, _ = self._volta(est)
        self.assertEqual(r["ACCAO"], "POTE_NAO_SUBIU", r)
        self.assertEqual(r["PORQUE"], "POTE_REPROVADO")
        self.assertEqual((self.entrega / "POTE.json").read_bytes(), antes)
        self.assertEqual(sorted(p.name for p in self.entrega.iterdir()), ["POTE.json"])
        self.assertNotIn("INT_ULTIMA_SUBIDA_EM", est)
        self.assertEqual(list((self.d / "esteira").rglob(".POTE.candidato.json")), [])
        self.assertTrue(Path(r["GUARDADO_EM"]).exists())

    def test_duas_corridas_sobrepostas_a_segunda_fica_ocupada(self):
        with espera._Trava(str(self.trinco)):
            r, ch = self._volta({})
        self.assertEqual(r["ACCAO"], "OCUPADO")
        self.assertEqual((ch["copia"], ch["motor"]), (0, 0))

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

    def _run_falso(self, read_only, visto):
        """subprocess.run de mentira, IGUAL em Windows e Linux: escreve no `-o` o export que o banco
        diria, e guarda o comando e o ambiente para se conferir a transacao so-leitura."""
        def run(cmd, **kw):
            visto.update(cmd=cmd, env=kw.get("env") or {})
            Path(cmd[cmd.index("-o") + 1]).write_text(json.dumps({"READ_ONLY": read_only, "LINHAS": []}),
                                                      encoding="utf-8")
            return mock.Mock(returncode=0, stderr="", stdout="")
        return run

    def test_export_so_serve_com_read_only_on_em_qualquer_so(self):
        visto = {}
        with mock.patch.object(GI.subprocess, "run", self._run_falso("on", visto)):
            self.assertEqual(GI.exportar("postgresql://x@h/y", self.d / "e.json", "psql")["READ_ONLY"], "on")
        self.assertIn("begin transaction read only", visto["cmd"])
        self.assertIn("default_transaction_read_only=on", visto["env"]["PGOPTIONS"])
        self.assertEqual(visto["cmd"][-1], "postgresql://x@h/y")          # o DSN por ultimo (RUNBOOK-R7 §2)
        for mau in ("off", None, "ON"):
            with mock.patch.object(GI.subprocess, "run", self._run_falso(mau, {})), \
                 self.assertRaises(RuntimeError, msg=repr(mau)):
                GI.exportar("postgresql://x@h/y", self.d / "e2.json", "psql")

    def test_os_pousos_da_copia_leem_se_so_leitura(self):
        visto = {}

        def run(cmd, **kw):
            visto.update(cmd=cmd, env=kw.get("env") or {})
            return mock.Mock(returncode=0, stderr="",
                             stdout="R-1\t1\tderived:6\t2026-09-28 10:00:00+00\r\nR-2\t3\tderived:6\t\n")
        with mock.patch.object(GI.subprocess, "run", run):
            p = GI.ler_pousos("postgresql://x@h/y", "psql")
        self.assertEqual(p, [{"run_id": "R-1", "ordem": 1, "item_id": "derived:6",
                              "pousado_em": "2026-09-28 10:00:00+00"},
                             {"run_id": "R-2", "ordem": 3, "item_id": "derived:6", "pousado_em": None}])
        self.assertIn("default_transaction_read_only=on", visto["env"]["PGOPTIONS"])
        self.assertTrue(visto["cmd"][visto["cmd"].index("-c") + 1].lower().startswith("select "))
        self.assertEqual(visto["cmd"][-1], "postgresql://x@h/y")

    def test_a_poda_da_intelligence_corre_depois_e_poupa_a_corrida_em_curso(self):
        vistos = {}

        def copia(pasta):
            vistos["copia"] = pasta
            return json.loads(EXPORT_R7.read_text(encoding="utf-8"))

        def podar(pasta, em_curso):
            vistos.setdefault("podar", []).append((pasta, em_curso, (em_curso / "MOTOR.json").exists()))
            return {"PODADAS": []}
        est = {}
        GI.correr_se_devido(est, agora=AGORA, consulta=_consulta(12, "2026-09-28 01:00:00+00",
                                                                 "2026-09-28 11:00:00+00"),
                            copia=copia, motor=lambda *a: _corrida_da_lei(),
                            subir=lambda s, pasta, parar: {"SUBIU": False}, parar=self.parar,
                            trinco=self.trinco, pasta=self.d / "esteira", podar=podar)
        self.assertEqual(vistos["podar"], [(self.d / "esteira", vistos["copia"], True)])
        self.assertEqual(est["INT_ULTIMA_PODA"], {"PODADAS": []})

    def test_o_motor_verdadeiro_sobre_o_export_r7_e_o_fiscal_decide(self):
        # O motor e o gerador de HOJE: o que o fiscal disser, o gatilho obedece.
        saida = GI.correr_o_motor(json.loads(EXPORT_R7.read_text(encoding="utf-8")), AGORA.date(), "TESTE")
        r = GI.subir_o_pote(saida, self.d / "p", self.parar, entrega=self.entrega)
        viol = GI.VP.validar(GI.montar_o_pote(saida)[0])
        self.assertEqual(r["SUBIU"], not viol)
        self.assertEqual(self.entrega.exists(), not viol)

    def test_o_mapa_do_motor_reprova_no_gerador_e_convertido_passa_no_fiscal(self):
        # D-GER-1: o mapa do motor (D112) nao e valor da COL-LAW-221 -> o gerador do dono recusa-o ao montar.
        # D142 no ponto de montagem (mapa -> UNKNOWN) -> o fiscal aceita UNKNOWN. Pote do motor REAL valido.
        saida = GI.correr_o_motor(json.loads(EXPORT_R7.read_text(encoding="utf-8")), AGORA.date(), "TESTE")
        with self.assertRaises(GI.P.LeiViolada) as ctx:
            GI.P.ler_entrada(json.loads(json.dumps(saida)))
        self.assertIn("ENTITY_SOURCE fora da COL-LAW-221", str(ctx.exception))
        pote, n = GI.montar_o_pote(saida)
        self.assertGreater(n, 0)
        self.assertEqual(GI.VP.validar(pote), [])


# ── O CORTE VIGENTE: ITEM_ID repetido na Sala ────────────────────────────────
class TestCorteVigente(_Pasta):
    def test_sem_repetido_o_export_passa_igual(self):
        exp = json.loads(EXPORT_R7.read_text(encoding="utf-8"))
        limpo, corte = GI.cortar_vigente(exp)
        self.assertEqual(limpo["LINHAS"], exp["LINHAS"])
        self.assertFalse(corte["DEFEITO_NA_SALA"])
        self.assertEqual(corte["LINHAS_NO_EXPORT"], corte["LINHAS_NO_CORTE"])

    def test_fica_a_linha_de_pouso_mais_recente_e_as_outras_sao_declaradas(self):
        exp, iid = _export_com_repetido()
        limpo, corte = GI.cortar_vigente(exp)
        ids = [l["item_id"] for l in limpo["LINHAS"]]
        self.assertEqual(len(ids), len(set(ids)))
        vig = [l for l in limpo["LINHAS"] if l["item_id"] == iid]
        self.assertEqual(vig[0]["run_id"], "ZZ-OUTRA-CORRIDA")
        self.assertTrue(corte["DEFEITO_NA_SALA"])
        self.assertEqual(corte["ITEM_ID_REPETIDO"][iid]["FICA"]["RUN_ID"], "ZZ-OUTRA-CORRIDA")
        self.assertEqual(len(corte["ITEM_ID_REPETIDO"][iid]["FORA"]), 1)
        self.assertEqual(corte["LINHAS_NO_EXPORT"] - corte["LINHAS_NO_CORTE"], 1)
        self.assertNotIn("POUSOS_DA_COPIA", limpo)

    def test_a_ordem_do_export_nao_decide_quem_fica(self):
        exp, iid = _export_com_repetido()
        exp["LINHAS"].reverse()
        limpo, _ = GI.cortar_vigente(exp)
        self.assertEqual([l["run_id"] for l in limpo["LINHAS"] if l["item_id"] == iid], ["ZZ-OUTRA-CORRIDA"])

    def test_hora_ilegivel_num_repetido_tira_o_grupo_inteiro(self):
        exp, iid = _export_com_repetido()
        exp["POUSOS_DA_COPIA"][-1]["pousado_em"] = None
        limpo, corte = GI.cortar_vigente(exp)
        self.assertNotIn(iid, [l["item_id"] for l in limpo["LINHAS"]])
        self.assertIn(iid, corte["REPETIDO_SEM_HORA_LEGIVEL"])
        self.assertTrue(corte["DEFEITO_NA_SALA"])

    def test_sem_pousos_nada_se_escolhe(self):
        exp, iid = _export_com_repetido()
        exp.pop("POUSOS_DA_COPIA")
        limpo, corte = GI.cortar_vigente(exp)
        self.assertNotIn(iid, [l["item_id"] for l in limpo["LINHAS"]])
        self.assertIn(iid, corte["REPETIDO_SEM_HORA_LEGIVEL"])

    def test_item_id_sem_identidade_sai_e_e_declarado(self):
        exp = json.loads(EXPORT_R7.read_text(encoding="utf-8"))
        exp["LINHAS"].append(dict(exp["LINHAS"][0], item_id="?", run_id="R-X", ordem=9))
        limpo, corte = GI.cortar_vigente(exp)
        self.assertNotIn("?", [l["item_id"] for l in limpo["LINHAS"]])
        self.assertEqual(corte["ITEM_ID_SEM_IDENTIDADE"], [{"RUN_ID": "R-X", "ORDEM": 9, "ITEM_ID": "?"}])

    def test_o_motor_verdadeiro_recusa_o_repetido_e_aceita_o_corte(self):
        exp, _ = _export_com_repetido()
        with self.assertRaises(GI.M.LeiViolada):
            GI.correr_o_motor({k: v for k, v in exp.items() if k != "POUSOS_DA_COPIA"}, AGORA.date(), "T")
        limpo, _ = GI.cortar_vigente(exp)
        self.assertIn("INTELLIGENCE_RUN_ID", GI.correr_o_motor(limpo, AGORA.date(), "T"))

    def test_a_volta_leva_o_corte_ao_motor_e_declara_o_defeito(self):
        exp, iid = _export_com_repetido()
        est = {}
        r, ch = TestVoltaDoGatilho._volta(self, est, export=exp)
        ids = [l["item_id"] for l in ch["export_do_motor"]["LINHAS"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(est["INT_ULTIMO_CORTE"]["DEFEITO_NA_SALA"])
        self.assertEqual(est["INT_ULTIMO_CORTE"]["ITEM_ID_REPETIDO"], [iid])
        self.assertTrue(r["CORTE"]["DEFEITO_NA_SALA"])
        pasta = next((self.d / "esteira").glob("*/CORTE-VIGENTE.json"))
        self.assertIn(iid, json.loads(pasta.read_text(encoding="utf-8"))["ITEM_ID_REPETIDO"])


# ── SO LE A SALA, E NUNCA MARCA consumido_em (D140) ──────────────────────────
class TestSoLeASala(_Pasta):
    def test_uma_volta_inteira_nao_chama_nenhum_escritor_da_sala(self):
        vistos = []
        esp = {n: mock.Mock(side_effect=AssertionError("escritor da Sala chamado: " + n))
               for n in ("pousar", "rever", "retirar")}
        with mock.patch.multiple(espera, **esp):
            c = _consulta(12, "2026-09-28 01:00:00+00", "2026-09-28 11:00:00+00")
            r = GI.correr_se_devido({}, agora=AGORA, consulta=c,
                                    copia=lambda p: json.loads(EXPORT_R7.read_text(encoding="utf-8")),
                                    motor=lambda *a: _corrida_da_lei(),
                                    subir=self._subir(), parar=self.parar, trinco=self.trinco,
                                    pasta=self.d / "esteira")
            vistos = c.sqls
        self.assertEqual(r["ACCAO"], "POTE_SUBIU", r)
        for n, m in esp.items():
            self.assertEqual(m.call_count, 0, n)
        self.assertTrue(vistos and all(re.match(r"^\s*select\b", s, re.I) for s in vistos), vistos)

    def test_o_codigo_do_disparador_nao_escreve_na_sala(self):
        # A prova estatica: nenhum escritor da Sala, nenhum consumido_em, nenhum SQL que escreva.
        texto = (RAIZ / "admissao" / "gatilho_da_inteligencia.py").read_text(encoding="utf-8")
        codigo = texto.split('"""', 2)[2]                       # sem a docstring do topo (que explica a lei)
        for proibido in ("espera.pousar", "espera.rever", "espera.retirar", ".pousar(", ".retirar(",
                         ".rever(", "consumido_em", "consumido_por"):
            self.assertNotIn(proibido, codigo, proibido)
        for sql in re.findall(r"\b(insert\s+into|update\s+\w+\s+set|delete\s+from|truncate)\b", codigo, re.I):
            self.fail("SQL que escreve no disparador: %r" % (sql,))

    def test_a_consulta_padrao_e_o_cliente_so_leitura_da_coleta(self):
        sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
        import micro_coleta as MC
        with mock.patch.object(MC, "sql", return_value=[["0", "", ""]]) as s:
            GI.medir_delta(GI._consulta_padrao, None)
        s.assert_called_once()
        with self.assertRaises(MC.EscritaRecusada):
            MC.sql("update sala_de_espera set consumido_em = now()")


# ── A ENTREGA AO CASCO: POTE.json + MANIFESTO.json + SHA256SUMS.txt ──────────
class TestEntrega(_Pasta):
    def test_pote_aprovado_entrega_os_tres_ficheiros_e_os_sha_batem(self):
        r, _ = TestVoltaDoGatilho._volta(self, {})
        self.assertEqual(r["ACCAO"], "POTE_SUBIU", r)
        self.assertEqual(sorted(p.name for p in self.entrega.iterdir()),
                         ["MANIFESTO.json", "POTE.json", "SHA256SUMS.txt"])
        for linha in (self.entrega / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
            sha, nome = linha.split(" *")
            self.assertEqual(sha, hashlib.sha256((self.entrega / nome).read_bytes()).hexdigest(), nome)
        man = json.loads((self.entrega / "MANIFESTO.json").read_text(encoding="utf-8"))
        pote = json.loads((self.entrega / "POTE.json").read_text(encoding="utf-8"))
        self.assertEqual(man["INTELLIGENCE_RUN_ID"], pote["INTELLIGENCE_RUN_ID"])
        self.assertEqual(man["RESULT_STATE"], pote["RESULT_STATE"])
        self.assertEqual(man["VALIDAR_POTE_V2"], "PASSA")
        self.assertEqual(man["POTE"]["SHA256_ARQUIVO"],
                         hashlib.sha256((self.entrega / "POTE.json").read_bytes()).hexdigest())
        self.assertEqual(GI.VP.validar(pote), [])

    def test_a_entrega_e_lf_e_o_sha256sums_le_se_com_a_ferramenta_padrao(self):
        TestVoltaDoGatilho._volta(self, {})
        for n in ("POTE.json", "MANIFESTO.json", "SHA256SUMS.txt"):
            self.assertNotIn(b"\r", (self.entrega / n).read_bytes(), n)
        for linha in (self.entrega / "SHA256SUMS.txt").read_bytes().split(b"\n")[:-1]:
            self.assertRegex(linha.decode("ascii"), r"^[0-9a-f]{64} \*(POTE|MANIFESTO)\.json$")

    def test_a_entrega_troca_se_inteira(self):
        self.entrega.mkdir(parents=True)
        (self.entrega / "SOBRA-DE-OUTRA.json").write_text("{}", encoding="utf-8")
        TestVoltaDoGatilho._volta(self, {})
        self.assertFalse((self.entrega / "SOBRA-DE-OUTRA.json").exists())
        self.assertFalse(self.entrega.with_name("PARA-O-CASCO.nova").exists())
        self.assertFalse(self.entrega.with_name("PARA-O-CASCO.velha").exists())

    def test_a_entrega_vive_fora_do_git(self):
        import subprocess
        for caminho in ("curadoria/esteira/intelligence/PARA-O-CASCO/POTE.json",
                        "curadoria/ESTEIRA-INTELLIGENCE-ESTADO.json", "curadoria/ESTEIRA-INTELLIGENCE-VOLTA.lock",
                        "curadoria/esteira/intelligence/20260928T120000Z/.POTE.candidato.json"):
            r = subprocess.run(["git", "check-ignore", "-q", caminho], cwd=RAIZ)
            self.assertEqual(r.returncode, 0, "o git nao ignora %s" % caminho)


# ── A VOLTA AGENDADA (--uma-volta) ───────────────────────────────────────────
class TestUmaVolta(_Pasta):
    def _kw(self):
        return dict(estado_em=self.d / "ESTADO.json", trinco_da_volta=self.d / "VOLTA",
                    ambiente={"SINTONIA_SALA_DSN": "postgresql://u:SEGREDO@h/sala"},
                    agora=AGORA, consulta=_consulta(0), parar=self.parar, trinco=self.trinco,
                    pasta=self.d / "esteira")

    def test_sem_dsn_nao_corre_e_nao_diz_a_dsn(self):
        kw = self._kw()
        kw["ambiente"] = {}
        r = GI.uma_volta(**kw)
        self.assertEqual(r["ACCAO"], "PRECONDICOES")
        self.assertIn("SINTONIA_SALA_DSN", r["FALTA"][0])
        self.assertFalse((self.d / "ESTADO.json").exists())

    def test_a_dsn_nunca_aparece_no_resultado_nem_no_estado(self):
        r = GI.uma_volta(**self._kw())
        self.assertEqual(r["ACCAO"], "ESPERA")
        self.assertNotIn("SEGREDO", json.dumps(r) + (self.d / "ESTADO.json").read_text(encoding="utf-8"))
        self.assertEqual(GI.precondicoes({"SINTONIA_SALA_DSN": "postgresql://u:SEGREDO@h/s"}), [])
        self.assertNotIn("SEGREDO", json.dumps(GI.precondicoes({})))

    def test_o_estado_grava_se_e_a_volta_seguinte_le_o(self):
        kw = self._kw()
        GI.uma_volta(**kw)
        est = json.loads((self.d / "ESTADO.json").read_text(encoding="utf-8"))
        self.assertEqual(est["INT_ULTIMA_VOLTA"]["ACCAO"], "ESPERA")
        self.assertEqual(est["INT_MEDIDO_EM"], AGORA.isoformat())
        kw["agora"] = AGORA + timedelta(minutes=1)
        self.assertEqual(GI.uma_volta(**kw)["ACCAO"], "NADA")     # leu INT_MEDIDO_EM da volta anterior

    def test_duas_voltas_ao_mesmo_tempo_a_segunda_nao_grava(self):
        kw = self._kw()
        (self.d / "ESTADO.json").write_text(json.dumps({"INT_MARCA": "M-DA-OUTRA"}), encoding="utf-8")
        with espera._Trava(str(self.d / "VOLTA")):
            r = GI.uma_volta(**kw)
        self.assertEqual(r["ACCAO"], "OCUPADO")
        self.assertEqual(json.loads((self.d / "ESTADO.json").read_text(encoding="utf-8")),
                         {"INT_MARCA": "M-DA-OUTRA"})

    def test_main_uma_volta_devolve_o_codigo_da_accao(self):
        for accao, codigo in (("PRECONDICOES", 4), ("OCUPADO", 3), ("MOTOR_ERRO", 1), ("POTE_NAO_SUBIU", 0),
                              ("ESPERA", 0)):
            with mock.patch.object(GI, "uma_volta", return_value={"ACCAO": accao}), \
                 mock.patch("builtins.print"):
                self.assertEqual(GI.main(["--uma-volta"]), codigo, accao)


# ── A FRONTEIRA: a Intelligence para na entrega; o portal e do casco ─────────
def _foto_do_portal():
    base = RAIZ / "italia-portale"
    return {str(p.relative_to(base)): (p.stat().st_size, p.stat().st_mtime_ns)
            for p in base.rglob("*") if p.is_file()}


class TestFronteira(_Pasta):
    def test_o_codigo_do_disparador_nao_aponta_para_o_portal(self):
        texto = (RAIZ / "admissao" / "gatilho_da_inteligencia.py").read_text(encoding="utf-8")
        codigo = texto.split('"""', 2)[2]
        for proibido in ("italia-portale", "sintonia-pote", "POTE_NO_CASCO", "como_js"):
            self.assertNotIn(proibido, codigo, proibido)

    def test_uma_volta_pelo_caminho_padrao_nao_escreve_sob_italia_portale(self):
        antes = _foto_do_portal()
        with mock.patch.object(GI, "ENTREGA", self.entrega):
            r = GI.correr_se_devido({}, agora=AGORA, consulta=_consulta(12, "2026-09-28 01:00:00+00",
                                                                        "2026-09-28 11:00:00+00"),
                                    copia=lambda p: json.loads(EXPORT_R7.read_text(encoding="utf-8")),
                                    motor=lambda *a: _corrida_da_lei(),
                                    parar=self.parar, trinco=self.trinco, pasta=self.d / "esteira")
        depois = _foto_do_portal()
        novos = sorted(set(depois) - set(antes))
        for n in novos:                               # um mutante que escreva ali nao deixa lixo na arvore
            (RAIZ / "italia-portale" / n).unlink(missing_ok=True)
        self.assertEqual(r["ACCAO"], "POTE_SUBIU", r)
        self.assertTrue((self.entrega / "POTE.json").exists())
        self.assertEqual(novos, [], "o disparador escreveu sob italia-portale/")
        self.assertEqual({k: v for k, v in depois.items() if k in antes}, antes,
                         "o disparador mexeu num ficheiro sob italia-portale/")


# ── ENTITY_SOURCE no ponto de montagem do pote (decisao do Intelligence owner, 28/09) ──
class TestEntitySourceNoPote(_Pasta):
    def test_valor_da_lei_fica_e_o_resto_vira_unknown(self):
        for v in ("SPAN", "PARAGRAPH_CONTEXT", "SECTION_TITLE", "DOCUMENT_TITLE", "UNKNOWN"):
            self.assertEqual(GI.entity_source_da_lei(v), v)
        for v in ({"CROP_ID": {"VALOR": "olivo", "ENTITY_SOURCE": "SPAN", "POR_ITEM": []}},
                  "TRECHO_DA_AFIRMACAO", "NAO SEI", None, ["SPAN"], "span"):
            self.assertEqual(GI.entity_source_da_lei(v), "UNKNOWN", repr(v))

    def test_o_mapa_nunca_se_achata_nem_se_escolhe_uma_entrada(self):
        # mesmo com TODAS as entradas do mapa a dizer SPAN, o pote diz UNKNOWN: escolher seria inventar
        mapa = {"CROP_ID": {"VALOR": "olivo", "ENTITY_SOURCE": "SPAN"},
                "ISSUE_ID": {"VALOR": "x", "ENTITY_SOURCE": "SPAN"}}
        self.assertEqual(GI.entity_source_da_lei(mapa), "UNKNOWN")

    def test_montar_o_pote_converte_so_o_entity_source_e_nao_mexe_na_saida_do_motor(self):
        saida = GI.correr_o_motor(json.loads(EXPORT_R7.read_text(encoding="utf-8")), AGORA.date(), "TESTE")
        copia = json.loads(json.dumps(saida))
        mapas = sum(1 for objs in saida["ITENS_POR_FERRAMENTA"].values() for o in objs
                    for dono in (o, o.get("CHAVES") or {}) if isinstance(dono.get("ENTITY_SOURCE"), dict))
        pote, n = GI.montar_o_pote(saida)
        self.assertEqual(saida, copia)                          # o mapa continua inteiro no motor
        self.assertGreater(mapas, 0)
        self.assertEqual(n, mapas)                              # so os mapas mudaram, um a um
        vistos = [o["ENTITY_SOURCE"] for e in pote["COMPARTIMENTOS"].values() for o in e["OBJETOS"]
                  if "ENTITY_SOURCE" in o]
        self.assertTrue(vistos and set(vistos) == {"UNKNOWN"}, vistos)

    def test_o_candidato_que_o_fiscal_le_ja_vem_convertido(self):
        saida = GI.correr_o_motor(json.loads(EXPORT_R7.read_text(encoding="utf-8")), AGORA.date(), "TESTE")
        r = GI.subir_o_pote(saida, self.d / "p", self.parar, entrega=self.entrega)
        self.assertTrue(r["SUBIU"], r)
        self.assertGreater(r["ENTITY_SOURCE_CONVERTIDOS"], 0)
        entregue = json.loads((self.entrega / "POTE.json").read_text(encoding="utf-8"))
        vistos = [o["ENTITY_SOURCE"] for e in entregue["COMPARTIMENTOS"].values() for o in e["OBJETOS"]
                  if "ENTITY_SOURCE" in o]
        self.assertTrue(vistos and set(vistos) <= set(GI.LEI_221), vistos)


# ── D-GER-1 · o fiscal do pote: ENTITY_SOURCE so com o vocabulario da COL-LAW-221 ────────────────
class TestFiscalEntitySource(_Pasta):
    def _pote_valido(self):
        saida = GI.correr_o_motor(json.loads(EXPORT_R7.read_text(encoding="utf-8")), AGORA.date(), "TESTE")
        pote, _ = GI.montar_o_pote(saida)
        self.assertEqual(GI.VP.validar(pote), [])
        return pote

    def _com(self, pote, valor):
        p = json.loads(json.dumps(pote))
        alvo = next(o for e in p["COMPARTIMENTOS"].values() for o in e["OBJETOS"] if "ENTITY_SOURCE" in o)
        alvo["ENTITY_SOURCE"] = valor
        return p

    def test_todo_valor_da_lei_passa_unknown_incluido(self):
        pote = self._pote_valido()
        for v in GI.LEI_221:
            self.assertEqual(GI.VP.validar(self._com(pote, v)), [], v)

    def test_o_que_nao_e_da_lei_reprova(self):
        pote = self._pote_valido()
        mapa = {"CROP_ID": {"VALOR": "x", "ENTITY_SOURCE": "SPAN", "POR_ITEM": []}}
        achatado = "POR_CHAVE — CROP_ID:SPAN; REGION_ID:NAO SEI"
        fora_da_lei = "TRECHO_DA_AFIRMACAO"            # o valor da R9 manual: entrada RECUSADA, nao regra
        for mau in (mapa, "NAO SEI", achatado, fora_da_lei, "", "?", None, ["SPAN"], "span"):
            viol = GI.VP.validar(self._com(pote, mau))
            self.assertTrue(any("ENTITY_SOURCE fora da COL-LAW-221" in v for v in viol), (mau, viol))

    def test_a_fixture_do_dono_passa_no_fiscal_tal_como_esta(self):
        # D-GER-1-MIG: a corrida sintetica do dono do pote, sem nenhuma troca, monta um pote que o fiscal aprova
        c = json.loads(CORRIDA_VALIDA.read_text(encoding="utf-8"))
        vistos = [o.get("ENTITY_SOURCE") for objs in c["ITENS_POR_FERRAMENTA"].values()
                  for o in (objs if isinstance(objs, list) else [objs]) if "ENTITY_SOURCE" in o]
        self.assertTrue(vistos and set(vistos) <= set(GI.LEI_221), vistos)
        self.assertEqual(GI.VP.validar(GI.P.ler_entrada(c)), [])

    def test_o_vocabulario_vem_do_dono_e_nao_de_uma_copia(self):
        import afirmacao_da_fonte as AF
        self.assertIs(GI.P.ENTITY_SOURCES, AF.ENTITY_SOURCES)

    def test_location_source_mantem_a_regra_de_antes(self):
        pote = self._pote_valido()
        p = json.loads(json.dumps(pote))
        o = next(o for e in p["COMPARTIMENTOS"].values() for o in e["OBJETOS"])
        o["LOCATION_SOURCE"] = "UNKNOWN"                        # para LOCATION_SOURCE, UNKNOWN esconde (como antes)
        self.assertTrue(any("LOCATION_SOURCE esconde a ignorancia" in v for v in GI.VP.validar(p)))
        o["LOCATION_SOURCE"] = "NAO SEI"
        self.assertFalse(any("LOCATION_SOURCE" in v for v in GI.VP.validar(p)))


# ── D-GER-2 · RAW_SHA256 e RAW_STORAGE_PATH na PROVA: os do raw_asset, ou NAO SEI ────────────────
class TestByteDaProva(_Pasta):
    def _export_com_byte(self):
        exp = json.loads(EXPORT_R7.read_text(encoding="utf-8"))
        for l in exp["LINHAS"]:                                  # o que o export novo leria do raw_asset
            l["raw_sha256"] = hashlib.sha256(("raw-%s" % l["raw_observation_id"]).encode()).hexdigest()
            l["raw_storage_path"] = "XX/sint/%s.bin" % l["raw_observation_id"]
        exp["LINHAS"][0]["raw_sha256"] = None                    # um raw_asset sem sha: NAO SEI
        exp["LINHAS"][0]["raw_storage_path"] = None
        return exp

    def test_o_export_le_o_byte_do_raw_asset(self):
        sql = GI.SQL_EXPORT.read_text(encoding="utf-8")
        self.assertIn("r.sha256             as raw_sha256", sql)
        self.assertIn("r.storage_path       as raw_storage_path", sql)
        self.assertIn("left join public.raw_asset r on r.id = a.raw_observation_id", sql)

    def test_cada_prova_leva_o_sha_do_banco_ou_nao_sei(self):
        exp = self._export_com_byte()
        do_banco = {str(l["raw_observation_id"]): (l["raw_sha256"], l["raw_storage_path"]) for l in exp["LINHAS"]}
        saida = GI.correr_o_motor(exp, AGORA.date(), "TESTE")
        pote, _ = GI.montar_o_pote(saida)
        self.assertEqual(GI.VP.validar(pote), [])
        provas = [p for e in pote["COMPARTIMENTOS"].values() for o in e["OBJETOS"] for p in o["PROVA"]]
        self.assertTrue(provas)
        for p in provas:
            sha, cam = do_banco[str(p["RAW_OBSERVATION_ID"])]
            self.assertEqual(p["RAW_SHA256"], sha or "NAO SEI", p["RAW_OBSERVATION_ID"])
            self.assertEqual(p["RAW_STORAGE_PATH"], cam or "NAO SEI", p["RAW_OBSERVATION_ID"])

    def test_sem_o_byte_no_export_a_prova_diz_nao_sei(self):
        saida = GI.correr_o_motor(json.loads(EXPORT_R7.read_text(encoding="utf-8")), AGORA.date(), "TESTE")
        pote, _ = GI.montar_o_pote(saida)
        for e in pote["COMPARTIMENTOS"].values():
            for o in e["OBJETOS"]:
                for p in o["PROVA"]:
                    self.assertEqual((p["RAW_SHA256"], p["RAW_STORAGE_PATH"]), ("NAO SEI", "NAO SEI"))

    def test_o_fiscal_reprova_sha_que_nao_e_do_raw_asset(self):
        saida = GI.correr_o_motor(self._export_com_byte(), AGORA.date(), "TESTE")
        pote, _ = GI.montar_o_pote(saida)
        for mau in ("sha-do-texto", "ABC", hashlib.md5(b"x").hexdigest(), "", None):
            p = json.loads(json.dumps(pote))
            next(o for e in p["COMPARTIMENTOS"].values() for o in e["OBJETOS"])["PROVA"][0]["RAW_SHA256"] = mau
            self.assertTrue(any("RAW_SHA256" in v for v in GI.VP.validar(p)), mau)


# ── RETENCAO DOS BACKUPS ─────────────────────────────────────────────────────
def _backup_falso(corrida: Path, prova_vale: bool, bytes_pg: int = 4096):
    b = corrida / "backup"
    (b / "pg" / "base").mkdir(parents=True, exist_ok=True)
    (b / "pg" / "base" / "1").write_bytes(b"x" * bytes_pg)
    (b / "SALA-ANTES-DA-MICRO.dump").write_bytes(b"d" * 100)
    (b / "PROVA-BACKUP-SALA.json").write_text(json.dumps({"PROVA_VALE": prova_vale}), encoding="utf-8")
    (corrida / "EXPORT-DA-COPIA.json").write_text("{}", encoding="utf-8")


class TestRetencao(_Pasta):
    def setUp(self):
        super().setUp()
        sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
        import provar_backup_da_sala as PB
        self.PB = PB
        self.nomes = ["20260920T000000Z", "20260921T000000Z", "20260922T000000Z", "20260923T000000Z",
                      "20260924T000000Z", "20260925T000000Z", "20260926T000000Z"]
        for n in self.nomes:
            _backup_falso(self.d / n, prova_vale=(n == "20260921T000000Z"))
        (self.d / "LIXO-QUE-NAO-E-CORRIDA").mkdir()
        (self.d / "LIXO-QUE-NAO-E-CORRIDA" / "f").write_text("fica", encoding="utf-8")

    def _inteira(self, n):
        return (self.d / n / "backup" / "pg").is_dir() and (self.d / n / "backup" / "SALA-ANTES-DA-MICRO.dump").exists()

    def test_ficam_as_n_ultimas_a_ultima_prova_vale_e_a_em_curso(self):
        r = self.PB.podar(self.d, self.d / "20260920T000000Z", guardar=3)
        ficam = {"20260920T000000Z", "20260921T000000Z", "20260924T000000Z", "20260925T000000Z",
                 "20260926T000000Z"}
        for n in self.nomes:
            self.assertEqual(self._inteira(n), n in ficam, n)
            self.assertTrue((self.d / n / "backup" / "PROVA-BACKUP-SALA.json").exists(), n)
        self.assertFalse((self.d / "20260922T000000Z" / "EXPORT-DA-COPIA.json").exists())
        self.assertEqual(sorted(r["PODADAS"]), ["20260922T000000Z", "20260923T000000Z"])
        self.assertEqual(r["ULTIMA_PROVA_VALE"], "20260921T000000Z")
        self.assertGreater(r["BYTES_LIBERTADOS"], 2 * 4096)
        self.assertEqual((self.d / "LIXO-QUE-NAO-E-CORRIDA" / "f").read_text(encoding="utf-8"), "fica")

    def test_o_disco_fica_limitado_volta_apos_volta(self):
        for n in self.nomes:
            self.PB.podar(self.d, self.d / n, guardar=3)
        inteiras = [n for n in self.nomes if self._inteira(n)]
        self.assertEqual(inteiras, ["20260921T000000Z", "20260924T000000Z", "20260925T000000Z",
                                    "20260926T000000Z"])

    def test_a_entrega_ao_casco_nao_e_podada(self):
        e = self.d / "PARA-O-CASCO"
        e.mkdir()
        (e / "POTE.json").write_text("{}", encoding="utf-8")
        self.PB.podar(self.d, self.d / "20260926T000000Z", guardar=1)
        self.assertTrue((e / "POTE.json").exists())

    def test_pasta_que_nao_existe_nao_rebenta(self):
        self.assertEqual(self.PB.podar(self.d / "nao-ha", self.d / "x")["PODADAS"], [])

    def test_a_prova_do_backup_devolve_a_dsn_ao_ambiente(self):
        # ESTEIRA-SOZINHA: a prova apagava SINTONIA_SALA_DSN e nao a repunha.
        with mock.patch.dict(os.environ, {"SINTONIA_SALA_DSN": "postgresql://antes"}), \
             mock.patch.object(self.PB.E, "fotografia", return_value={}):
            self.PB._fotografia_de(None)
            self.PB._fotografia_de("postgresql://outra")
            self.assertEqual(os.environ["SINTONIA_SALA_DSN"], "postgresql://antes")


# ── VIGIA ────────────────────────────────────────────────────────────────────
class TestVigia(_Pasta):
    def _marcas(self, **horas):
        out = {}
        for nome, _n, _c in VIG.ETAPAS:
            h = horas.get(nome, 0.5)
            out[nome] = (lambda h=h: ((AGORA - timedelta(hours=h)).isoformat() if h is not None else None, "teste"))
        return out

    def test_a_passagem_nao_portada_nao_e_etapa(self):
        self.assertNotIn("passagem", [n for n, _h, _c in VIG.ETAPAS])

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

    def test_defeito_na_sala_e_alerta_mesmo_com_tudo_a_andar(self):
        est = {"INT_ULTIMO_CORTE": {"DEFEITO_NA_SALA": True, "ITEM_ID_REPETIDO": ["derived:6"],
                                    "LINHAS_NO_EXPORT": 10, "LINHAS_NO_CORTE": 9}}
        r = VIG.medir(AGORA, self._marcas(), est)
        self.assertTrue(r["ALERTA"])
        a = [x for x in r["ALERTAS"] if x["ESTADO"] == VIG.DEFEITO_NA_SALA]
        self.assertEqual(a[0]["ITEM_ID_REPETIDO"], ["derived:6"])
        self.assertEqual(a[0]["LINHAS"], [10, 9])

    def test_as_marcas_da_intelligence_vem_do_estado_do_disparador(self):
        est = {"INT_ULTIMA_CORRIDA_EM": (AGORA - timedelta(hours=1)).isoformat()}
        m = VIG.marcas_padrao(est)
        self.assertEqual(m["intelligence"]()[0], est["INT_ULTIMA_CORRIDA_EM"])
        self.assertEqual(VIG.ESTADO_DO_DISPARADOR, GI.ESTADO)

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


if __name__ == "__main__":
    unittest.main()
