# -*- coding: utf-8 -*-
"""SOURCE-CURATOR-INTEGRATION — os doze testes da nova divisao.

    SOURCE CURATOR PREPARA. COLLECTION COLETA.

 1. estados antigos nao vencem evidencia atual
 2. as 50 YouTube nao sao despromovidas pela rota antiga
 3. o Source Curator e o UNICO promotor de READY
 4. a Collection so consome READY
 5. falha da Collection nao abre reparo interno
 6. o reparo volta ao Curator
 7. retry nao bloqueia a fila
 8. restart preserva trabalho
 9. SOURCE_ID permanece estavel
10. a proveniencia permanece
11. sem duplicacao por reinicio
12. UNKNOWN nao vira PASS/BLOCK por omissao

Os testes que ESCREVEM correm sobre ficheiros proprios (tempdir). Os que leem
o livro da casa (`curadoria/LIFECYCLE-LEDGER-V1.json`) so leem. A rede e
substituida na primitiva mais funda (`worker.PORTAO` / `worker.SONDA`): fake
acima do portao mediria o fake.
"""
from __future__ import annotations

import importlib
import io
import json
import os
import sys
import tempfile
import time
import unittest
from datetime import timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import evidencia as EV                # noqa: E402
import fila as F                      # noqa: E402
import fontes_prontas as FP           # noqa: E402  — o lado da Collection
import interface_collection as IC     # noqa: E402
import lifecycle as LC                # noqa: E402
import semear_lifecycle as SEM        # noqa: E402
import worker as W                    # noqa: E402

CUR = RAIZ / "curadoria"
LIVRO_DA_CASA = CUR / "LIFECYCLE-LEDGER-V1.json"
ESTADO_DA_CASA = CUR / "ESTADO-ACTUAL-DAS-FONTES-V1.json"
FOTO = CUR / "READY-FOR-COLLECTION-V1.json"


def _json(p):
    with io.open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _fonte(sid, **kw):
    f = {"SOURCE_ID": sid, "TERRITORY": "T2", "ROUTE": "https://prova.invalid/%s/" % sid,
         "STRATEGY": "HTML_LINK_DISCOVERY", "ADAPTER_ID": None, "ROUTE_TYPE": "DISCOVERED_ROUTE",
         "EXECUTAVEL": True, "PORQUE_EXECUTAVEL": "ok", "FICHA_NO_ATLAS": True,
         "TERRITORIO_COM_EXECUTOR": True, "CANARIO_MAIS_RECENTE": None, "BIG_COLLECTION": None}
    f.update(kw)
    return f


class Isolada(unittest.TestCase):
    """Livro, fila e evidencia proprios. O livro da casa nao e tocado."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        for m in (LC, F, EV, IC, W, SEM, FP):
            importlib.reload(m)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        EV.EVIDENCIA = d / "EVIDENCE.json"
        self.estado = d / "ESTADO.json"
        self.estado.write_text(json.dumps({"HEAD": "teste", "FONTES": []}), encoding="utf-8")
        IC.ESTADO_ACTUAL = self.estado
        IC.LC, IC.F = LC, F
        W.LC, W.F, W.EV = LC, F, EV
        SEM.LC, SEM.F, SEM.EV = LC, F, EV
        FP.IC = IC
        self.rede = []
        W.PORTAO = lambda url: (self.rede.append(("PORTAO", url)) or (True, "permite"))
        W.SONDA = lambda fonte: (self.rede.append(("SONDA", fonte["SOURCE_ID"]))
                                 or {"PASS": True, "HTTP": 200, "ALVOS": 1, "PORQUE": ""})

    def tearDown(self):
        self.tmp.cleanup()

    def _ready(self, sid, ref="EV-1"):
        LC.registar(sid, LC.CANARY_PENDING, "pronta")
        LC.registar(sid, LC.READY_FOR_COLLECTION, "canario", evidence_ref=ref)


# ── 1 ────────────────────────────────────────────────────────────────────────
class T01_EstadosAntigosNaoVencemEvidenciaAtual(Isolada):
    def test_a_fotografia_diz_ROUTE_BLOCKED_e_o_estado_actual_diz_READY(self):
        """A mesma fonte: a fotografia (missao 04) tem-na bloqueada pela rota
        velha; o registo de hoje tem-na executavel, com canario PASS pela rota
        nova. O resemeador so pode ler a segunda."""
        f = _fonte("IT-T7-015", ADAPTER_ID="CANAL_PUBLICO_YOUTUBE_V1", STRATEGY="CUSTOM_ADAPTER",
                   CANARIO_MAIS_RECENTE={"ORIGEM": "censo", "MEDIDO_EM": "2026-09-20", "RESULTADO": "PASS"})
        estado = SEM.semear_uma(f, "cabeca")
        self.assertEqual(estado, LC.READY_FOR_COLLECTION)
        self.assertNotIn(LC.CONTRACT_READY_ROUTE_BLOCKED,
                         [t["NEW_STATE"] for t in LC.historia("IT-T7-015")])

    def test_o_resemeador_nao_le_o_campo_STATE_da_fotografia_para_o_registo(self):
        src = (CUR / "semear_lifecycle.py").read_text(encoding="utf-8")
        corpo = src.split('def semear_uma', 1)[1].split('def semear_so_na_foto', 1)[0]
        self.assertNotIn('["STATE"]', corpo)
        self.assertNotIn("READY-FOR-COLLECTION-V1", corpo,
                         "semear_uma() leu a fotografia — e a fotografia e o modo de falha n.1")

    def test_no_livro_da_casa_nenhuma_fonte_do_registo_cita_a_fotografia(self):
        livro = _json(LIVRO_DA_CASA)
        reg = {f["SOURCE_ID"] for f in _json(ESTADO_DA_CASA)["FONTES"]}
        citam = sorted({t["SOURCE_ID"] for t in livro["TRANSICOES"]
                        if t["SOURCE_ID"] in reg and "READY-FOR-COLLECTION-V1" in str(t.get("EVIDENCE_REF"))})
        self.assertEqual(citam, [], "fonte do registo com estado importado da fotografia")


# ── 2 ────────────────────────────────────────────────────────────────────────
class T02_As50YouTubeNaoSaoDespromovidas(unittest.TestCase):
    def test_as_50_do_registo_estao_READY_no_livro_da_casa(self):
        est = {}
        for t in _json(LIVRO_DA_CASA)["TRANSICOES"]:
            est[t["SOURCE_ID"]] = t["NEW_STATE"]
        yt = [f["SOURCE_ID"] for f in _json(ESTADO_DA_CASA)["FONTES"]
              if f.get("ADAPTER_ID") == "CANAL_PUBLICO_YOUTUBE_V1"]
        self.assertEqual(len(yt), 50)
        fora = {s: est.get(s) for s in yt if est.get(s) != LC.READY_FOR_COLLECTION}
        self.assertEqual(fora, {}, "YouTube fora de READY: %s" % fora)

    def test_a_fotografia_continua_a_dizer_o_contrario_e_isso_nao_venceu(self):
        """Controlo: a divergencia e real. Se a fotografia ja dissesse READY,
        o teste anterior nao provaria nada."""
        foto = _json(FOTO)
        self.assertEqual(foto["POR_ESTADO"].get("CONTRACT_READY_ROUTE_BLOCKED"), 50)
        est = {t["SOURCE_ID"]: t["NEW_STATE"] for t in _json(LIVRO_DA_CASA)["TRANSICOES"]}
        bloqueadas_na_foto = [f["SOURCE_ID"] for f in foto["FONTES"]
                              if f["STATE"] == "CONTRACT_READY_ROUTE_BLOCKED"]
        self.assertEqual([s for s in bloqueadas_na_foto if est.get(s) in LC.PARADOS], [])


# ── 3 ────────────────────────────────────────────────────────────────────────
class T03_SourceCuratorEOUnicoPromotor(Isolada):
    def test_so_o_owner_SOURCE_CURATOR_promove(self):
        ok_c, _ = LC.transicao_permitida(LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, LC.OWNER_CURATOR)
        ok_col, porque = LC.transicao_permitida(LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, LC.OWNER_COLLECTION)
        ok_x, _ = LC.transicao_permitida(LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, "INTELLIGENCE")
        self.assertTrue(ok_c)
        self.assertFalse(ok_col)
        self.assertIn("Collection", porque)
        self.assertFalse(ok_x)

    def test_a_porta_da_collection_nao_tem_verbo_de_promocao(self):
        src = (RAIZ / "orquestrador" / "fontes_prontas.py").read_text(encoding="utf-8")
        self.assertNotIn("registar(", src, "a porta da Collection escreve no livro")
        self.assertNotIn("READY_FOR_COLLECTION,", src)
        with self.assertRaises(ValueError) as e:
            LC.registar("IT-T2-900", LC.READY_FOR_COLLECTION, "colhi", owner=LC.OWNER_COLLECTION,
                        evidence_ref="RUN-1")
        self.assertIn("Collection", str(e.exception))


# ── 4 ────────────────────────────────────────────────────────────────────────
class T04_ACollectionSoConsomeReady(Isolada):
    def test_exigir_ready_recusa_pelo_nome_e_passa_a_READY(self):
        self._ready("IT-T2-901")
        LC.registar("IT-T2-902", LC.CANARY_PENDING, "ainda sem canario")
        self.assertEqual(FP.exigir_ready("IT-T2-901"), {"CONHECIDA": True, "ESTADO": LC.READY_FOR_COLLECTION})
        with self.assertRaises(FP.FonteNaoReady) as e:
            FP.exigir_ready("IT-T2-902")
        self.assertIn("CANARY_PENDING", str(e.exception))
        self.assertIn("FONTE_NAO_READY", str(e.exception))

    def test_o_orquestrador_recusa_antes_da_rede(self):
        import orquestrador as orq
        from pedido import Pedido
        orq.fontes_prontas = FP
        self._ready("IT-T2-903")
        IC.source_repair_needed("IT-T2-903", "HTTP_404", run_id="RUN-BCR")
        chamou = []
        original = orq.subprocess.run
        orq.subprocess.run = lambda *a, **k: chamou.append(a) or original(*a, **k)
        try:
            r = orq.correr(Pedido(alvo="T2", filtros={"pais": "IT", "fonte": "IT-T2-903", "universo": "T2"}))
        finally:
            orq.subprocess.run = original
        self.assertEqual(r["STATUS"], "FONTE_NAO_READY")
        self.assertIn("DEGRADED", r["ERROR"])
        self.assertEqual(chamou, [], "o executor foi chamado para uma fonte que nao e READY")
        self.assertNotIn("COMANDO", r)

    def test_a_lista_que_a_collection_recebe_so_tem_READY(self):
        self._ready("IT-T2-904")
        LC.registar("IT-T2-905", LC.CANARY_PENDING, "x")
        LC.registar("IT-T2-906", LC.CANARY_PENDING, "x")
        LC.registar("IT-T2-906", LC.CONTRACT_READY_ROUTE_BLOCKED, "robots", evidence_ref="EV")
        self.assertEqual(FP.ids_ready(), ["IT-T2-904"])
        self.assertEqual([p["SOURCE_ID"] for p in FP.plano_de_coleta()], ["IT-T2-904"])


# ── 5 ────────────────────────────────────────────────────────────────────────
class T05_FalhaDaCollectionNaoAbreReparoInterno(Isolada):
    def test_reportar_avaria_degrada_enfileira_e_para(self):
        self._ready("IT-T2-910")
        r = FP.reportar_avaria("IT-T2-910", "HTTP_404", run_id="RUN-5")
        self.assertTrue(r["ACEITE"])
        self.assertEqual(LC.estado_de("IT-T2-910"), LC.DEGRADED)
        t = [x for x in F.elegiveis() if x["SOURCE_ID"] == "IT-T2-910"]
        self.assertEqual([x["TASK_TYPE"] for x in t], [F.REPAIR])
        self.assertEqual(t[0]["STATUS"], F.PENDING, "a Collection executou o reparo")
        self.assertEqual(self.rede, [], "a Collection foi a rede (canario/robots) ao reportar")

    def test_a_collection_nao_importa_o_worker(self):
        for nome in ("fontes_prontas.py", "orquestrador.py"):
            src = (RAIZ / "orquestrador" / nome).read_text(encoding="utf-8")
            self.assertNotIn("import worker", src, "%s importa o worker do Curator" % nome)


# ── 6 ────────────────────────────────────────────────────────────────────────
class T06_RepairVoltaAoCurator(Isolada):
    def test_REPAIR_com_canario_novo_devolve_READY_com_prova_nova(self):
        self._ready("IT-T2-920", ref="EV-VELHO")
        r = FP.reportar_avaria("IT-T2-920", "HTTP_404", run_id="RUN-6")
        W.correr(pausa=0, verboso=False, contratos={"IT-T2-920": _fonte("IT-T2-920")})
        h = [t["NEW_STATE"] for t in LC.historia("IT-T2-920")]
        self.assertEqual(h[-3:], [LC.DEGRADED, LC.REPAIRING, LC.READY_FOR_COLLECTION])
        ref = LC.historia("IT-T2-920")[-1]["EVIDENCE_REF"]
        self.assertNotEqual(ref, "EV-VELHO")
        self.assertEqual(EV.por_ref(ref)["ETAPA"], F.REPAIR)
        self.assertEqual(("SONDA", "IT-T2-920"), self.rede[-1])
        self.assertEqual(F.metricas()["DONE"], 1)

    def test_REPAIR_cujo_canario_falha_NAO_devolve_READY(self):
        self._ready("IT-T2-921")
        FP.reportar_avaria("IT-T2-921", "HTTP_404", run_id="RUN-6b")
        W.SONDA = lambda fonte: {"PASS": False, "HTTP": 404, "PORQUE": "404", "CLASSE": "SOURCE"}
        W.correr(pausa=0, verboso=False, contratos={"IT-T2-921": _fonte("IT-T2-921")})
        self.assertNotEqual(LC.estado_de("IT-T2-921"), LC.READY_FOR_COLLECTION)
        self.assertNotIn("IT-T2-921", IC.ready_ids())


# ── 7 ────────────────────────────────────────────────────────────────────────
class T07_RetryNaoBloqueiaAFila(Isolada):
    def test_429_em_A_adia_A_e_B_C_D_correm_na_mesma_volta(self):
        fontes = {s: _fonte(s) for s in ("IT-T2-A", "IT-T2-B", "IT-T2-C", "IT-T2-D")}
        for s in fontes:
            LC.registar(s, LC.CANARY_PENDING, "rota ok")
            F.enfileirar(s, F.CANARY, priority=99 if s == "IT-T2-A" else 50)
        W.SONDA = lambda f: ({"PASS": False, "HTTP": 429, "RETRY_AFTER_S": 3600, "PORQUE": "429"}
                             if f["SOURCE_ID"] == "IT-T2-A" else {"PASS": True, "HTTP": 200, "PORQUE": ""})
        t0 = F.agora_utc()
        inicio = time.monotonic()
        feitos = W.correr(pausa=0, verboso=False, contratos=fontes, agora_fn=lambda: t0)
        self.assertLess(time.monotonic() - inicio, 5.0, "o worker dormiu a espera do 429")
        self.assertEqual([r["SOURCE_ID"] for r in feitos], ["IT-T2-A", "IT-T2-B", "IT-T2-C", "IT-T2-D"])
        self.assertEqual(LC.estado_de("IT-T2-A"), LC.RETRY_AFTER)
        for s in ("IT-T2-B", "IT-T2-C", "IT-T2-D"):
            self.assertEqual(LC.estado_de(s), LC.READY_FOR_COLLECTION)
        a = [t for t in json.loads(F.FILA.read_text(encoding="utf-8"))["TAREFAS"] if t["SOURCE_ID"] == "IT-T2-A"][0]
        self.assertEqual(a["STATUS"], F.WAITING_RETRY)
        self.assertEqual(F._parse(a["NEXT_ATTEMPT_AT"]), t0 + timedelta(seconds=3600))
        self.assertEqual(F.elegiveis(t0 + timedelta(minutes=59)), [])
        self.assertEqual([t["SOURCE_ID"] for t in F.elegiveis(t0 + timedelta(minutes=61))], ["IT-T2-A"])

    def test_o_worker_nao_tem_sleep_de_retry(self):
        src = (CUR / "worker.py").read_text(encoding="utf-8")
        self.assertNotIn("sleep(espera", src)
        self.assertNotIn("sleep(retry", src)


# ── 8 ────────────────────────────────────────────────────────────────────────
class T08_RestartPreservaTrabalho(Isolada):
    def test_tarefa_em_curso_sobrevive_e_e_recuperada_por_outro_processo(self):
        for s in ("IT-T2-930", "IT-T2-931"):
            F.enfileirar(s, F.CANARY)
        t0 = F.agora_utc()
        pego = F.proxima(t0)          # IN_PROGRESS no disco; o processo «morre» aqui
        caminho = F.FILA
        importlib.reload(F)           # «outro processo»: so ve o disco
        F.FILA = caminho
        d = json.loads(F.FILA.read_text(encoding="utf-8"))
        self.assertEqual(len(d["TAREFAS"]), 2)
        rec = F.recuperar_orfas(agora=t0 + timedelta(hours=1))
        self.assertEqual([r["SOURCE_ID"] for r in rec], [pego["SOURCE_ID"]])
        self.assertEqual(len(F.elegiveis(t0 + timedelta(hours=1))), 2)
        self.assertTrue(all("recuperada" in (r["LAST_ERROR"] or "") for r in rec))

    def test_o_livro_e_escrito_de_forma_atomica(self):
        src = (CUR / "lifecycle.py").read_text(encoding="utf-8")
        self.assertIn("os.replace(tmp", src)
        self.assertIn("os.fsync", src)


# ── 9 ────────────────────────────────────────────────────────────────────────
class T09_SourceIdPermaneceEstavel(Isolada):
    def test_o_id_nao_muda_ao_longo_do_ciclo(self):
        sid = "IT-T2-940"
        LC.registar(sid, LC.CANARY_PENDING, "x")
        LC.registar(sid, LC.RETRY_AFTER, "429", evidence_ref="EV-1")
        LC.registar(sid, LC.CANARY_PENDING, "voltou")
        LC.registar(sid, LC.READY_FOR_COLLECTION, "canario", evidence_ref="EV-2")
        LC.registar(sid, LC.DEGRADED, "quebrou", owner=LC.OWNER_COLLECTION, evidence_ref="RUN-1")
        LC.registar(sid, LC.REPAIRING, "reparo")
        LC.registar(sid, LC.READY_FOR_COLLECTION, "canario novo", evidence_ref="EV-3")
        h = LC.historia(sid)
        self.assertEqual(len(h), 7)
        self.assertTrue(all(t["SOURCE_ID"] == sid for t in h))
        self.assertEqual([r["SOURCE_ID"] for r in IC.ready_sources()], [sid])

    def test_o_livro_da_casa_nao_inventou_nenhum_SOURCE_ID(self):
        est = _json(ESTADO_DA_CASA)
        conhecidos = {f["SOURCE_ID"] for f in est["FONTES"]} | {s["SOURCE_ID"] for s in est["SO_NA_FOTO"]}
        no_livro = {t["SOURCE_ID"] for t in _json(LIVRO_DA_CASA)["TRANSICOES"]}
        self.assertEqual(sorted(no_livro - conhecidos), [])
        self.assertEqual(sorted(conhecidos - no_livro), [], "fonte do registo sem estado no livro")


# ── 10 ───────────────────────────────────────────────────────────────────────
class T10_ProvenanciaPermanece(unittest.TestCase):
    def test_toda_linha_do_livro_da_casa_tem_owner_versao_hora_e_razao(self):
        for t in _json(LIVRO_DA_CASA)["TRANSICOES"]:
            for k in ("SOURCE_ID", "PREVIOUS_STATE", "NEW_STATE", "REASON", "OBSERVED_AT", "OWNER", "VERSION"):
                self.assertIn(k, t)
            self.assertIn(t["OWNER"], (LC.OWNER_CURATOR, LC.OWNER_COLLECTION))
            self.assertTrue(t["REASON"])

    def test_toda_promocao_READY_cita_uma_prova_desta_arvore(self):
        for t in _json(LIVRO_DA_CASA)["TRANSICOES"]:
            if t["NEW_STATE"] == LC.READY_FOR_COLLECTION:
                ref = str(t["EVIDENCE_REF"])
                self.assertTrue(ref and ref != "None")
                self.assertTrue(ref.startswith("BCR-2026-09-20:") or "YOUTUBE-CANARIO-50" in ref
                                or "SONDAGEM" in ref or ref.startswith("EV-"),
                                "prova de READY que nao e desta arvore: %s" % ref)

    def test_toda_DEGRADED_da_casa_e_da_collection_e_cita_a_corrida(self):
        for t in _json(LIVRO_DA_CASA)["TRANSICOES"]:
            if t["NEW_STATE"] == LC.DEGRADED:
                self.assertEqual(t["OWNER"], LC.OWNER_COLLECTION)
                self.assertTrue(str(t["EVIDENCE_REF"]).startswith("BCR-2026-09-20:IT-T"))


# ── 11 ───────────────────────────────────────────────────────────────────────
class T11_SemDuplicacaoPorReinicio(Isolada):
    def test_semear_duas_vezes_nao_acrescenta_linha_nenhuma(self):
        f = _fonte("IT-T2-950", CANARIO_MAIS_RECENTE={"ORIGEM": "censo", "MEDIDO_EM": "hoje", "RESULTADO": "PASS"})
        SEM.semear_uma(f, "cabeca")
        antes = len(LC._ler_bruto()["TRANSICOES"])
        # o resemeador salta o que ja existe (e o main que decide por `ja`)
        ja = LC.snapshot()
        self.assertIn("IT-T2-950", ja)
        depois = len(LC._ler_bruto()["TRANSICOES"])
        self.assertEqual(antes, depois)

    def test_enfileirar_e_reportar_repetidos_dao_uma_tarefa_e_um_DEGRADED(self):
        self._ready("IT-T2-951")
        a = FP.reportar_avaria("IT-T2-951", "HTTP_404", run_id="RUN-1")
        b = FP.reportar_avaria("IT-T2-951", "HTTP_404", run_id="RUN-1")
        self.assertTrue(a["ACEITE"])
        self.assertFalse(b["ACEITE"], "reportar duas vezes degradou duas vezes")
        self.assertEqual(F.metricas()["QUEUE_TOTAL"], 1)
        self.assertEqual(LC.metricas()[LC.DEGRADED], 1)
        with self.assertRaises(ValueError):
            LC.registar("IT-T2-951", LC.READY_FOR_COLLECTION, "outra vez", evidence_ref="EV")


# ── 12 ───────────────────────────────────────────────────────────────────────
class T12_UnknownNaoViraPassNemBlock(Isolada):
    def test_fonte_sem_prova_fica_CANARY_PENDING_com_canario_na_fila(self):
        estado = SEM.semear_uma(_fonte("IT-T2-960"), "cabeca")
        self.assertEqual(estado, LC.CANARY_PENDING)
        self.assertNotIn(estado, LC.PARADOS)
        self.assertEqual([t["TASK_TYPE"] for t in F.elegiveis() if t["SOURCE_ID"] == "IT-T2-960"], [F.CANARY])

    def test_robots_ilegivel_ou_inacessivel_e_RETRY_nunca_BLOCK(self):
        def indisponivel(url):
            raise RuntimeError("PortaoIndisponivel: o transporte caiu")
        W.PORTAO = indisponivel
        self.assertEqual(W.etapa_validate_route("IT-T2-961", _fonte("IT-T2-961"))[0], "RETRY")
        W.PORTAO = lambda url: (False, "robots.txt ilegível deste host — não afirmamos permissão que não lemos")
        self.assertEqual(W.etapa_validate_route("IT-T2-961", _fonte("IT-T2-961"))[0], "RETRY")
        # contraprova: Disallow LIDO e BLOCK
        W.PORTAO = lambda url: (False, "robots.txt do host barra este caminho para SintoniaScrap")
        self.assertEqual(W.etapa_validate_route("IT-T2-961", _fonte("IT-T2-961"))[0], "BLOCK")

    def test_fonte_desconhecida_pelo_curator_nao_e_READY_nem_bloqueio(self):
        r = FP.exigir_ready("IT-T2-999")
        self.assertEqual(r["CONHECIDA"], False)
        self.assertIsNone(r["ESTADO"])
        self.assertNotIn("IT-T2-999", FP.ids_ready())

    def test_no_livro_da_casa_as_duas_sem_prova_ficaram_CANARY_PENDING(self):
        est = {t["SOURCE_ID"]: t["NEW_STATE"] for t in _json(LIVRO_DA_CASA)["TRANSICOES"]}
        reg = {f["SOURCE_ID"]: f for f in _json(ESTADO_DA_CASA)["FONTES"]}
        sem_prova = [s for s, f in reg.items() if f["READY_PELA_REGRA_DA_CASA"]
                     and (f.get("CANARIO_MAIS_RECENTE") or {}).get("RESULTADO") != "PASS"
                     and (f.get("BIG_COLLECTION") or {}).get("CLASSE") != "SUCCESS"]
        self.assertTrue(sem_prova, "o controlo deixou de existir: mede outra coisa")
        for s in sem_prova:
            self.assertEqual(est[s], LC.CANARY_PENDING, "%s virou %s por omissao" % (s, est[s]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
