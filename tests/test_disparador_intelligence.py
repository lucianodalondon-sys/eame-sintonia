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
        self.destino = self.d / "client" / "sintonia-pote.js"
        self.entrega = self.d / "esteira" / "PARA-O-CASCO"

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def _subir(self):
        return lambda s, pasta, parar: GI.subir_o_pote(s, self.destino, pasta, parar, entrega=self.entrega)


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
            return json.loads(CORRIDA_VALIDA.read_text(encoding="utf-8"))

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
        self.assertTrue(self.destino.exists())
        self.assertEqual(est["INT_MARCA"], "2026-09-28T11:00:00+00:00")
        self.assertEqual(est["INT_ULTIMA_SUBIDA_EM"], AGORA.isoformat())
        self.assertFalse((self.destino.parent / ".sintonia-pote.candidato.js").exists())

    def test_pote_reprovado_nao_sobe_e_a_entrega_nao_muda(self):
        self.destino.parent.mkdir(parents=True)
        self.destino.write_text("window.SINTONIA_POTE = {\"ANTIGO\": 1};", encoding="utf-8")
        self.entrega.mkdir(parents=True)
        (self.entrega / "POTE.json").write_text("{\"ANTIGO\": 1}", encoding="utf-8")
        antes = (self.destino.read_bytes(), (self.entrega / "POTE.json").read_bytes())
        est = {}
        with mock.patch.object(GI.VP, "validar", return_value=["LEI: violacao plantada"]):
            r, _ = self._volta(est)
        self.assertEqual(r["ACCAO"], "POTE_NAO_SUBIU", r)
        self.assertEqual(r["PORQUE"], "POTE_REPROVADO")
        self.assertEqual((self.destino.read_bytes(), (self.entrega / "POTE.json").read_bytes()), antes)
        self.assertNotIn("INT_ULTIMA_SUBIDA_EM", est)
        self.assertFalse((self.destino.parent / ".sintonia-pote.candidato.js").exists())

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
                            copia=copia, motor=lambda *a: json.loads(CORRIDA_VALIDA.read_text(encoding="utf-8")),
                            subir=lambda s, pasta, parar: {"SUBIU": False}, parar=self.parar,
                            trinco=self.trinco, pasta=self.d / "esteira", podar=podar)
        self.assertEqual(vistos["podar"], [(self.d / "esteira", vistos["copia"], True)])
        self.assertEqual(est["INT_ULTIMA_PODA"], {"PODADAS": []})

    def test_o_motor_verdadeiro_sobre_o_export_r7_e_o_fiscal_decide(self):
        # O motor e o gerador de HOJE: o que o fiscal disser, o gatilho obedece.
        saida = GI.correr_o_motor(json.loads(EXPORT_R7.read_text(encoding="utf-8")), AGORA.date(), "TESTE")
        r = GI.subir_o_pote(saida, self.destino, self.d / "p", self.parar, entrega=self.entrega)
        viol = GI.VP.validar(GI.P.ler_entrada(saida))
        self.assertEqual(r["SUBIU"], not viol)
        self.assertEqual(self.destino.exists(), not viol)
        self.assertEqual(self.entrega.exists(), not viol)

    def test_entity_source_objeto_e_o_bloqueio_medido_do_pote(self):
        # BLOQUEIO declarado (nao consertado aqui): o motor escreve ENTITY_SOURCE objeto, o schema pede texto.
        # Se isto mudar, o relatorio L2 e o PARA-O-CASCO.md estao desatualizados: releia-os.
        saida = GI.correr_o_motor(json.loads(EXPORT_R7.read_text(encoding="utf-8")), AGORA.date(), "TESTE")
        viol = GI.VP.validar(json.loads(json.dumps(GI.P.ler_entrada(saida))))
        self.assertTrue(viol)
        self.assertTrue(all("ENTITY_SOURCE" in v for v in viol), viol)


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
                                    motor=lambda *a: json.loads(CORRIDA_VALIDA.read_text(encoding="utf-8")),
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
        # o pote do casco e o da entrega sao o MESMO pote
        js = self.destino.read_text(encoding="utf-8")
        self.assertEqual(json.loads(js[js.index("= ") + 2:].rstrip().rstrip(";")), pote)

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
                        "italia-portale/client/.sintonia-pote.candidato.js"):
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
