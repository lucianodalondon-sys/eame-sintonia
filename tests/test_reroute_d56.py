# -*- coding: utf-8 -*-
"""REROUTE-D56 — o documento pronto e perguntado a TODAS as reguas; UM item, varias gavetas.

D56 (bot Luciano, 25/09 09:05): «B + (i): implementar o REROUTE na Admissão para todas as fontes; se o
item der SIM em vários universos, UM item canónico ligado a TODAS as gavetas aprovadas (sem duplicar
bytes nem proveniência), com pontuação e motivo de cada decisão.»

    A · a porta (sem banco)       SIM em 2 = 1 item com 2 gavetas · NAO em todos = 0 item · universo sem
                                  regua = NSA so para ele · menu nao conta · trecho · portao do item
    B · a estrada (FICHEIRO)      pela_porta: 1 READY, a gaveta extra ao lado, o livro com todas as decisoes;
                                  reprocessar nao duplica
    C · a Sala (Postgres descartavel, binarios de ~/orca/pgtmp): 1 linha, gavetas, a vista 038,
                                  idempotencia entre corridas, o reprocesso da Sala que ja existe

    py -m unittest tests.test_reroute_d56
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
for p in ("", "admissao", "coleta", "orquestrador"):
    if str(RAIZ / p) not in sys.path:
        sys.path.insert(0, str(RAIZ / p))
import _gavetas                          # noqa: E402,F401
import admissao as adm                   # noqa: E402
import sala_de_espera as espera          # noqa: E402
import reprocessar_reroute as rr         # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
TEM_PG = (E.PG_BIN / ("initdb.exe" if os.name == "nt" else "initdb")).exists() and shutil.which("bash")

# Um boletim fitossanitario (PDF: sem retrato do detector). As reguas de T1, T2 e T3 dizem SIM; T7 (o
# pedido) NAO. D130 (dono, 28/09): o reroute so ENTRA na Sala por T1 e T2 — T3 fica anotado no livro.
# AJUSTE DECLARADO (D130): a frase da «fioritura» e nova. Sem ela so T3 e T2 diziam SIM, e com a D130 o
# item teria UMA gaveta de reroute: a prova de «um item, varias gavetas» precisa de duas DENTRO do escopo.
BOLETIM = ("Bollettino fitosanitario. La peronospora e l'oidio sono presenti nei vigneti; le trappole "
           "mostrano catture di tignoletta, con infestazione in aumento dopo le piogge e le temperature "
           "elevate della settimana. ") * 3 + "Le viti sono in piena fioritura. "
# Comunicacao de cantina: so palavras de T9 (evento, prodotto, campagna), nenhum concorrente.
CANTINA = ("La cantina presenta il nuovo prodotto durante un evento esclusivo: la campagna di lancio del "
           "prodotto accompagnera l'evento con degustazioni e musica dal vivo per tutti gli ospiti. ") * 3
MENU = "Home | Chi siamo | Trappole | Diserbo | Infestante | Peronospora | Contatti\n"
CORPO_SEM_T3 = ("La cantina sociale ha presentato ieri sera il nuovo spumante metodo classico ai soci.\n"
                "Il presidente ha ringraziato tutti i produttori per il lavoro svolto durante l'anno.\n"
                "La serata si e conclusa con una cena preparata dagli chef del territorio locale.\n"
                "Il prossimo appuntamento con i soci sara in primavera nella sede della cantina.\n")
CORPO_COM_T3 = ("Nei vigneti della zona la peronospora e comparsa dopo le piogge di questa settimana.\n"
                "Le trappole a feromoni installate nei filari mostrano un aumento delle catture di adulti.\n"
                "I tecnici raccomandano di controllare le foglie basali e di seguire le indicazioni.\n"
                "La situazione verra aggiornata nel prossimo bollettino della settimana che viene.\n")
RETRATO = {"CAPA_OU_MATERIA": "MATERIA", "HTML_KIND": "ARTICLE"}


def doc(texto=BOLETIM, **kw):
    it = {"id": "derived:1", "texto": texto, "source_id": "IT-T3-002",
          "artifact_type": "DERIVED", "parent_sha256": "a" * 64}
    it.update(kw)
    return it


def por_universo(ds):
    return {d.universo: d for d in ds}


class APortaPerguntaATodas(unittest.TestCase):

    def test_sim_em_dois_universos_e_um_item_com_duas_gavetas(self):
        ds = adm.decidir_todas(doc(), "T7", corrida="t")
        u = por_universo(ds)
        self.assertEqual((u["T7"].resultado, u["T1"].resultado, u["T2"].resultado),
                         (adm.NAO, adm.SIM, adm.SIM))
        # D130: a regua de T3 disse SIM no corpo, mas T3 fica ANOTADO (fora do escopo do dono)
        self.assertEqual(u["T3"].resultado, adm.NAO_SEI)
        self.assertIn("REROUTE_FORA_DO_ESCOPO_D130", u["T3"].motivo)
        p = adm.principal(ds)
        self.assertEqual(p.universo, "T2")                 # a de maior pontuacao DENTRO do escopo
        g = adm.gavetas_para_a_sala(ds)
        self.assertEqual([x["UNIVERSO"] for x in g], ["T2", "T1"])
        self.assertTrue(all(x["PONTUACAO"] >= 1 and "PEDIDO=T7" in x["MOTIVO"] for x in g))
        self.assertEqual(adm.pronto_para_inteligencia(doc(), p)["UNIVERSO"], "T2")

    def test_o_pedido_continua_escrito_como_pedido_e_decidir_nao_mudou(self):
        ds = adm.decidir_todas(doc(), "T7", corrida="t")
        so = adm.decidir(doc(), "T7", corrida="t")
        self.assertEqual(ds[0].evidencia["d56"]["papel"], adm.PAPEL_PEDIDO)
        ev = dict(ds[0].evidencia)
        ev.pop("d56")
        self.assertEqual((ds[0].universo, ds[0].resultado, ds[0].regra, ds[0].motivo, ev),
                         (so.universo, so.resultado, so.regra, so.motivo, so.evidencia))
        self.assertTrue(all(d.evidencia["d56"] == dict(d.evidencia["d56"], papel=adm.PAPEL_REROUTE,
                                                        pedido="T7") for d in ds[1:]))
        # uma decisao por universo do Atlas, e o pedido so uma vez
        self.assertEqual(sorted(d.universo for d in ds), sorted(adm.universos_da_porta()))

    def test_pedido_sim_fica_a_linha_e_as_outras_sao_gavetas(self):
        ds = adm.decidir_todas(doc(), "T3", corrida="t")
        self.assertIs(adm.principal(ds), ds[0])
        # o PEDIDO T3 e a linha (a D130 nao toca no pedido); as de reroute sao so T1/T2
        self.assertEqual([x["UNIVERSO"] for x in adm.gavetas_para_a_sala(ds)], ["T3", "T1", "T2"])

    def test_nao_em_todos_e_zero_item(self):
        ds = adm.decidir_todas(doc(CANTINA), "T3", corrida="t")
        self.assertEqual([d.universo for d in ds if d.resultado == adm.SIM], [])
        self.assertIsNone(adm.principal(ds))
        self.assertEqual(adm.gavetas_para_a_sala(ds), [])
        # a cantina fala de T9 — mas sem concorrente nomeado nao e T9
        self.assertIn("T9_SEM_CONCORRENTE_NOMEADO", por_universo(ds)["T9"].motivo)

    def test_universo_sem_regua_e_nao_se_aplica_so_para_ele(self):
        ds = adm.decidir_todas(doc(), "T12", corrida="t")
        nsa = {d.universo for d in ds if d.resultado == adm.NAO_SE_APLICA}
        self.assertEqual(nsa, {"T6", "T8", "T11", "T12"})
        self.assertEqual(adm.principal(ds).universo, "T2")          # D130: T3 so anota
        self.assertEqual(ds[0].universo, "T12")

    def test_item_parado_num_portao_nao_e_perguntado_a_mais_nada(self):
        sem_origem = doc(source_id=None)
        ds = adm.decidir_todas(sem_origem, "T7", corrida="t")
        self.assertEqual((len(ds), ds[0].regra, ds[0].resultado), (1, "origem", adm.NAO_SEI))

    def test_todo_sim_do_reroute_traz_trecho_com_os_termos(self):
        for pedido in ("T7", "T12", "T10"):
            for d in adm.decidir_todas(doc(), pedido, corrida="t")[1:]:
                if d.resultado != adm.SIM:
                    continue
                tr = d.evidencia["trechos"]
                self.assertTrue(tr, d.universo)
                for t in tr:
                    for termo in t["termos"]:
                        self.assertIn(termo, adm._dobrar(t["trecho"]), (d.universo, termo))

    # AJUSTE DECLARADO (D130): o menu e o mesmo para qualquer gaveta, e as fixtures sao de T3. Para a
    # prova continuar a ser do MENU (e nao do escopo), o escopo abre T3 SO dentro deste teste.
    @mock.patch.object(adm, "REROUTE_NA_SALA_D130", frozenset({"T1", "T2", "T3"}))
    def test_o_menu_nao_conta(self):
        pagina = MENU + CORPO_SEM_T3 + "Cookie policy | Privacy | P.IVA 01234567890\n"
        com_retrato = doc(pagina, retrato_do_detector=RETRATO)
        r, motivo, ev = adm.julgar_reroute(com_retrato, "T3")
        self.assertNotEqual(r, adm.SIM, motivo)
        # controlo: o MESMO texto lido inteiro (como se fosse PDF) daria SIM — era o menu
        self.assertEqual(adm.julgar_reroute(doc(pagina), "T3")[0], adm.SIM)
        # e no corpo, a mesma regua entra — com trecho do corpo, nunca do menu
        r2, _m, ev2 = adm.julgar_reroute(doc(MENU + CORPO_COM_T3, retrato_do_detector=RETRATO), "T3")
        self.assertEqual(r2, adm.SIM)
        self.assertTrue(all("Chi siamo" not in t["trecho"] for t in ev2["trechos"]))
        self.assertTrue(ev2["texto_julgado"].startswith("CORPO"))

    def test_pagina_sem_corpo_separavel_fica_nao_sei(self):
        r, motivo, _ = adm.julgar_reroute(doc(MENU * 3, retrato_do_detector=RETRATO), "T3")
        self.assertEqual(r, adm.NAO_SEI)
        self.assertIn("CORPO_NAO_SEPARAVEL", motivo)

    def test_o_termo_tem_de_comecar_palavra_no_reroute(self):
        t = {"texto": "E prevista una sintesi del lavoro."}
        self.assertEqual(adm._do_universo(t, "T5", adm.PERGUNTAS_DO_UNIVERSO["T5"])[0], adm.SIM)
        self.assertNotEqual(adm._do_universo(t, "T5", adm.PERGUNTAS_DO_UNIVERSO["T5"],
                                             inicio_de_palavra=True)[0], adm.SIM)
        # e o reroute usa-o: a regua de T5 nem chega a dizer SIM («prevista», «sintesi»)
        r, motivo, ev = adm.julgar_reroute(doc("E prevista una sintesi del lavoro dei soci. " * 6), "T5")
        self.assertNotIn("sim_da_regua", ev, motivo)
        self.assertFalse(ev.get("palavras"), motivo)

    def test_regua_sem_medida_nao_promove_e_fica_no_livro_com_trecho(self):
        texto = ("Il decreto del Ministero modifica l'etichetta del prodotto registrato. " * 4)
        r, motivo, ev = adm.julgar_reroute(doc(texto), "T4")
        self.assertEqual(r, adm.NAO_SEI)
        self.assertIn("REROUTE_REGUA_SEM_MEDIDA", motivo)
        self.assertTrue(ev["sim_da_regua"] and ev["trechos"])
        self.assertNotIn("T4", adm.REROUTE_PROMOVE)

    def test_t9_pede_concorrente_nomeado(self):
        com = CANTINA + " Syngenta ha annunciato il lancio della campagna. "
        self.assertIn("T9_SEM_CONCORRENTE_NOMEADO", adm.julgar_reroute(doc(CANTINA), "T9")[1])
        r, motivo, ev = adm.julgar_reroute(doc(com), "T9")
        self.assertEqual(ev.get("concorrentes"), ["syngenta"])
        self.assertIn("REROUTE_REGUA_SEM_MEDIDA", motivo)     # T9 ainda sem medida: nao promove

    def test_chave_desligada_so_anota(self):
        with mock.patch.object(adm, "REROUTE_ENTRA_NA_SALA", False):
            ds = adm.decidir_todas(doc(), "T7", corrida="t")
            self.assertEqual(len(ds), len(adm.universos_da_porta()))      # o livro anota tudo
            self.assertIsNone(adm.principal(ds))                          # a Sala nao recebe
            ds3 = adm.decidir_todas(doc(), "T3", corrida="t")
            self.assertEqual([x["UNIVERSO"] for x in adm.gavetas_para_a_sala(ds3)], ["T3"])


class AGavetaTemForma(unittest.TestCase):
    def _u(self, item="derived:1", universo="T3"):
        return {"ITEM_ID": item, "UNIVERSO": universo}

    def test_recusa_o_que_nao_bate(self):
        ok = {"UNIVERSO": "T3", "PONTUACAO": 2, "MOTIVO": "m"}
        for mau in ({"derived:9": [ok]},
                    {"derived:1": [dict(ok, PONTUACAO=0)]},
                    {"derived:1": [dict(ok, PONTUACAO=True)]},
                    {"derived:1": [dict(ok, MOTIVO=" ")]},
                    {"derived:1": [dict(ok, UNIVERSO="T2")]},            # falta a da linha
                    {"derived:1": [ok, ok]}):
            with self.assertRaises(ValueError, msg=mau):
                espera._conferir_gavetas([self._u()], mau)
        self.assertEqual(espera._conferir_gavetas([self._u()], None), {})


class AEstradaNoFicheiro(unittest.TestCase):
    """pela_porta com o backend FICHEIRO (prova offline): 1 READY, a gaveta ao lado, o livro inteiro."""

    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp(prefix="reroute-d56-"))
        self._p = [mock.patch.object(espera, "MORADA", str(self.pasta / "sala")),
                   mock.patch.object(adm, "LIVRO", self.pasta / "LIVRO.json"),
                   mock.patch.dict(os.environ, {"SINTONIA_SALA_BACKEND": "FICHEIRO"})]
        for p in self._p:
            p.start()
        import orquestrador as orq
        self.orq = orq

    def tearDown(self):
        for p in self._p:
            p.stop()
        shutil.rmtree(self.pasta, ignore_errors=True)

    def test_um_ready_uma_gaveta_extra_e_o_livro_com_tudo(self):
        r = self.orq.pela_porta([doc(), doc(CANTINA, id="derived:2")], "T7", "RUN-D56")
        self.assertEqual(r["prontos"], 1)
        self.assertEqual(r["por_resultado"], {adm.NAO: 2})                # o recibo do PEDIDO, de sempre
        self.assertEqual((r["REROUTE"]["ITENS_SO_POR_REROUTE"], r["REROUTE"]["ITENS_COM_GAVETA_EXTRA"],
                          r["REROUTE"]["GAVETAS_NOVAS_NA_SALA"]), (1, 1, 1))
        lido = espera.ler("RUN-D56")["ITENS"]
        self.assertEqual([(u["ITEM_ID"], u["UNIVERSO"]) for u in lido], [("derived:1", "T2")])   # D130
        g = espera.ler_gavetas("RUN-D56")
        self.assertEqual([(x["ITEM_ID"], x["ORIGEM"], x["UNIVERSO"]) for x in g],
                         [("derived:1", "T2", "T1")])
        livro = json.loads((self.pasta / "LIVRO.json").read_text(encoding="utf-8"))["DECISOES"]
        self.assertEqual(len(livro), 2 * len(adm.universos_da_porta()))
        # reprocessar a mesma corrida nao duplica nada
        r2 = self.orq.pela_porta([doc(), doc(CANTINA, id="derived:2")], "T7", "RUN-D56")
        self.assertEqual((r2["espera"], r2["REROUTE"]["GAVETAS_NOVAS_NA_SALA"]), (espera.JA_ESTAVA, 0))
        self.assertEqual(len(espera.ler_gavetas("RUN-D56")), 1)


class OReprocessoSeco(unittest.TestCase):
    LINHAS = [{"RUN_ID": "R1", "ORDEM": 0, "ITEM_ID": "derived:1", "UNIVERSO": "T3", "SOURCE_ID": "IT-T3-002",
               "SHA256": "a" * 64, "MEDIA_TYPE": "application/pdf", "TEXTO": BOLETIM},
              {"RUN_ID": "R2", "ORDEM": 0, "ITEM_ID": "derived:9", "UNIVERSO": "T2", "SOURCE_ID": "IT-T3-002",
               "SHA256": "a" * 64, "MEDIA_TYPE": "application/pdf", "TEXTO": BOLETIM},
              {"RUN_ID": "R1", "ORDEM": 1, "ITEM_ID": "derived:2", "UNIVERSO": "T9", "SOURCE_ID": "IT-T7-017",
               "SHA256": "b" * 64, "MEDIA_TYPE": "text/html", "TEXTO": CANTINA}]

    def test_seco_e_deterministico_e_nao_repete_a_linha_de_outra_copia(self):
        a, b = rr.planear(self.LINHAS), rr.planear(list(reversed(self.LINHAS)))
        self.assertEqual(a, b)
        # o documento 'a' ja e linha em T3 e em T2 (anterior a D56): T2 NAO vira gaveta (ja e linha
        # de outra copia). A unica gaveta nova e T1 — o BOLETIM ganhou a «fioritura» (D130, declarado)
        self.assertEqual([(g["RUN_ID"], g["ORIGEM"], g["UNIVERSO"]) for g in a["GAVETAS"]],
                         [("R1", "T3", "T1")])
        self.assertEqual(len(a["DUPLICADOS_ANTES_DA_D56"]), 1)
        so_um = rr.planear(self.LINHAS[:1])
        self.assertEqual([(g["RUN_ID"], g["ORIGEM"], g["UNIVERSO"]) for g in so_um["GAVETAS"]],
                         [("R1", "T3", "T1"), ("R1", "T3", "T2")])

    def test_as_tres_travas_do_aplicar(self):
        plano = rr.planear(self.LINHAS[:1])
        flag = Path(tempfile.mkdtemp()) / "PARAR.flag"
        try:
            with self.assertRaises(rr.TravaFechada):
                rr.conferir_travas(plano, {"PROVA_VALE": True}, str(flag))       # sem PARAR.flag
            flag.write_text("parado", encoding="utf-8")
            for mau in ({"PROVA_VALE": False}, {}, {"PROVA_VALE": "true"}):      # so o backup falha
                with self.assertRaises(rr.TravaFechada):
                    rr.conferir_travas(plano, mau, str(flag))
            with self.assertRaises(rr.TravaFechada):
                rr.conferir_travas(dict(plano, VERSAO_DO_CODIGO="x"), {"PROVA_VALE": True}, str(flag))
            rr.conferir_travas(plano, {"PROVA_VALE": True}, str(flag))
        finally:
            shutil.rmtree(flag.parent, ignore_errors=True)


@unittest.skipUnless(TEM_PG, "sem Postgres portatil (~/orca/pgtmp) ou sem bash: a prova nao correu")
class ASalaDescartavel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pasta = Path(tempfile.mkdtemp(prefix="reroute-d56-pg-"))
        cls.base = E.Base(cls.pasta / "pg")
        assert ":54330/" not in cls.base.url, "isto e a Sala real"
        env = {**os.environ, "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")}
        r = cls.base.subir(RAIZ, env)
        if r["CODIGO"] != 0:
            cls.base.descer()
            raise unittest.SkipTest("migrations falharam: %s" % r["ERRO"])
        cls._amb = dict(os.environ)
        try:
            os.environ.update({"SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": cls.base.url,
                               "SINTONIA_PSQL_EXE": cls.base.exe("psql")})
            for run in ("A1", "A2", "A3", "A4", "A5"):
                cls.sql("insert into collection_run (run_id, platform, started_at, rule_version) "
                        "values ('%s', 'teste', now(), 'teste')" % run)
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        os.environ.clear()
        os.environ.update(cls._amb)
        cls.base.descer()
        shutil.rmtree(cls.pasta, ignore_errors=True)

    @classmethod
    def sql(cls, comando):
        r = subprocess.run([cls.base.exe("psql"), "-X", "-q", "-A", "-t", "-F", "|",
                            "-v", "ON_ERROR_STOP=1", "-c", comando, cls.base.url],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            raise AssertionError(r.stderr)
        return r.stdout.strip()

    def _pousar(self, run, pedido, item_id="derived:1"):
        it = doc(id=item_id)
        ds = adm.decidir_todas(it, pedido, corrida=run)
        ready = adm.pronto_para_inteligencia(it, adm.principal(ds))
        return espera.pousar(run, [ready], gavetas={ready["ITEM_ID"]: adm.gavetas_para_a_sala(ds)})

    def test_1_um_item_duas_gavetas_a_vista_e_o_atual(self):
        r = self._pousar("A1", "T7")
        self.assertEqual((r["ESTADO"], r["INSERIDAS"], r["GAVETAS_NOVAS"]), (espera.POUSOU, 1, 1))
        self.assertEqual(self.sql("select count(*) from sala_de_espera_atual"), "1")
        self.assertEqual(self.sql("select string_agg(gaveta || ':' || papel, ',' order by gaveta) "
                                  "from sala_de_espera_por_gaveta where item_id = 'derived:1'"),
                         "T1:REROUTE,T2:LINHA")                                    # D130: T3 nao entra
        self.assertEqual([(g["ORIGEM"], g["UNIVERSO"]) for g in espera.ler_gavetas("A1")], [("T2", "T1")])

    def test_2_retry_e_outra_corrida_nao_duplicam(self):
        self.assertEqual(self._pousar("A1", "T7")["GAVETAS_NOVAS"], 0)             # retry
        r = self._pousar("A2", "T3")                                                # outra corrida, pedido T3
        # D130: em A1 o T3 so foi anotado; agora T3 e o PEDIDO e SIM -> vira gaveta da linha que la esta
        # (a linha nao se repete). T1 e T2 ja la estavam: nada duplica.
        self.assertEqual((r["INSERIDAS"], r["GAVETAS_NOVAS"]), (0, 1))
        self.assertEqual(self.sql("select count(*) from sala_de_espera where item_id = 'derived:1'"), "1")
        self.assertEqual(self.sql("select count(*) from sala_de_espera_gaveta"), "2")

    def test_3_o_documento_ja_na_sala_noutro_universo_ganha_a_gaveta_do_pedido(self):
        # uma linha de antes da D56 (T3, sem gavetas); depois o mesmo item chega por um pedido T2:
        # a LINHA dele seria T2 — mas o item ja la esta, e o T2 vira gaveta da linha que la esta
        it = doc(id="derived:3")
        espera.pousar("A3", [adm.pronto_para_inteligencia(it, adm.decidir(it, "T3", corrida="A3"))])
        ds = adm.decidir_todas(it, "T2", corrida="A5")
        self.assertEqual(adm.principal(ds).universo, "T2")
        ready = adm.pronto_para_inteligencia(it, adm.principal(ds))
        r = espera.pousar("A5", [ready], gavetas={"derived:3": adm.gavetas_para_a_sala(ds)})
        self.assertEqual((r["INSERIDAS"], r["GAVETAS_NOVAS"]), (0, 2))              # T2 (pedido) + T1 (D130)
        self.assertEqual(self.sql("select count(*) from sala_de_espera where item_id = 'derived:3'"), "1")
        self.assertEqual(self.sql("select string_agg(g.run_id || ':' || g.origem || ':' || g.universo, ',' "
                                  "order by g.universo) "
                                  "from sala_de_espera_gaveta g join sala_de_espera s using (run_id, ordem) "
                                  "where s.item_id = 'derived:3'"), "A3:T3:T1,A3:T3:T2")

    def test_4_o_reprocesso_da_sala_que_ja_existe(self):
        # uma linha antiga (pousada como antes da D56: sem gavetas), e o reprocesso da-lhe as gavetas
        it = doc(id="derived:7")
        ready = adm.pronto_para_inteligencia(it, adm.decidir(it, "T3", corrida="A4"))
        espera.pousar("A4", [ready])
        linhas = [dict(l, SHA256="z" * 64) for l in espera.linhas_para_revisao() if l["RUN_ID"] == "A4"]
        plano = rr.planear(linhas)
        self.assertEqual([(g["ORIGEM"], g["UNIVERSO"]) for g in plano["GAVETAS"]],
                         [("T3", "T1"), ("T3", "T2")])                               # D130: so T1/T2
        a = espera.acrescentar_gavetas(plano["GAVETAS"])
        b = espera.acrescentar_gavetas(plano["GAVETAS"])
        self.assertEqual((a["INSERIDAS"], b["INSERIDAS"], b["JA_ESTAVAM"]), (2, 0, 2))
        # a linha nao e T5; a gaveta tem de ser NOVA (T4), senao «ja estava» esconde a origem errada
        mudou = [dict(plano["GAVETAS"][0], ORIGEM="T5", UNIVERSO="T4")]
        c = espera.acrescentar_gavetas(mudou)
        self.assertEqual((c["INSERIDAS"], c["ORIGEM_NAO_BATE"]), (0, 1))

    def test_5_a_038_so_cria_a_vista_e_desfaz_e_sobe(self):
        mig = next((RAIZ / "supabase" / "migrations").glob("038_*.sql")).read_text(encoding="utf-8")
        codigo = "\n".join(l for l in mig.lower().splitlines() if not l.strip().startswith("--"))
        self.assertNotRegex(codigo, r"\b(drop|delete|update|truncate|alter)\b")
        self.assertEqual(self.sql("select versao from schema_migracao where versao = '038'"), "038")
        antes = self.sql("select count(*) from sala_de_espera_por_gaveta")
        subprocess.run([self.base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1", "--single-transaction",
                        "-f", str(RAIZ / "supabase" / "desfazer" / "038_desfazer.sql"), self.base.url],
                       check=True, capture_output=True)
        self.assertEqual(self.sql("select to_regclass('public.sala_de_espera_por_gaveta') is null"), "t")
        self.assertEqual(self.sql("select count(*) from sala_de_espera_gaveta") != "0", True)
        subprocess.run([self.base.exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1", "--single-transaction",
                        "-f", str(next((RAIZ / "supabase" / "migrations").glob("038_*.sql"))), self.base.url],
                       check=True, capture_output=True)
        self.assertEqual(self.sql("select count(*) from sala_de_espera_por_gaveta"), antes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
