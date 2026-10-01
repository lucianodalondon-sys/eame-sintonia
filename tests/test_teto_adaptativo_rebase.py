# -*- coding: utf-8 -*-
"""D124-REBASE (28/09): o que o VERIFICADOR INDEPENDENTE reprovou na instalacao do teto adaptativo sobre a2aa73f.

    py -m unittest tests.test_teto_adaptativo_rebase

Sem rede (so 127.0.0.1). Cada classe e uma das quebras medidas:
  1. `coleta_continua.py` (a tarefa SINTONIA-COLETA-CONTINUA, a cada 30 min) importava `rodadas.TETO` e
     `reserva_24h._ler/gasto/ate_quando`, que a D124 removeu -> `import coleta_continua` rebentava.
     Agora: importa; o teto e o orcamento vigente; pausa/Retry-After fecham o dominio; 1 ciclo a seco pelo CLI.
  2. a linha SITES era medida pelo TEXTO `reservar24h(host, 1)`; mede-se pelo COMPORTAMENTO (a sonda).
  3. o livro vivo `TETO-24H.json` ({"RESERVAS": [...]}, D90) era ILEGIVEL para a D124 -> tudo UNKNOWN.
     Agora: leitura compativel + migracao no 1.o escrito (Python e Node), `--migrar`, malformado = UNKNOWN.
  4/5. o transporte Node: sinais pelo `-D` (curl 7.83), Crawl-delay > 5 s, robots PROIBE, sem livro = SEM_LIVRO,
     e o robots de 24 h do FEED-LIGADO sem ReferenceError — `provas/teto_adaptativo/transporte_rebase_local.mjs`.

ADENDO-PARADA (01/10) — AJUSTE DECLARADO: o ciclo passou a perguntar ao portao da Collection (`collection_gate`)
antes de oferecer uma fonte, e sem portao injectado usa o REAL. As fontes destes testes nao estao no livro canonico:
os ciclos em processo levam o portao falso que admite tudo (`pecas["fonte"]`), e o ciclo pelo CLI (que nao se
injecta) usa duas fontes que o portao real admite AGORA nesta arvore. Nenhuma assercao mudou.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
from coleta import cortesia_adaptativa as CA  # noqa: E402

AMBIENTE = ("SINTONIA_CORTESIA_LIVRO", "SINTONIA_TETO_24H", "SINTONIA_CORTESIA_ALERTAS", "SINTONIA_TETO_POR_HOST",
            "SINTONIA_CORTESIA_POLITICA", "SINTONIA_PAUSA_POR_HOST_S")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rebase-d124-"))
        self._env = {k: os.environ.pop(k, None) for k in AMBIENTE}
        CA.politica(recarregar=True)

    def tearDown(self):
        for k, v in self._env.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
        CA.politica(recarregar=True)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def node(self, js):
        p = subprocess.run(["node", "--input-type=module", "-e", js], cwd=RAIZ, env=dict(os.environ),
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr[-800:])
        return json.loads(p.stdout.strip().splitlines()[-1])


def _livro_d90(f: Path, reservas: list) -> None:
    """Exactamente como o reserva_24h da producao (a2aa73f) o escrevia: uma linha, RESERVAS primeiro."""
    f.write_text(json.dumps({"RESERVAS": reservas}, ensure_ascii=False), encoding="utf-8")


# ── 1. a coleta continua importa e corre sobre a cortesia adaptativa ──────────
class AColetaContinuaNaoPara(Base):
    def test_import_num_processo_limpo(self):
        """O que a tarefa do Windows faz: um processo novo importa o servico (antes: AttributeError TETO)."""
        env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}
        p = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, 'ferramentas/big_collection'); "
                            "import coleta_continua as C; print(C.CA.__name__, C.teto_manual())"],
                           cwd=RAIZ, env=env, capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        self.assertEqual(p.stdout.split(), ["cortesia_adaptativa", "None"])

    def test_sem_teto_manual_vale_o_orcamento_vigente_e_nao_5(self):
        import coleta_continua as C
        c = [{"SOURCE_ID": s, "DOMINIO": "z.it", "PREVISTOS": 5, "DOMINIOS": ["z.it"]} for s in "ABCDEFGHI"]
        e = C.escolher(c, feitas=[], ultima={}, reservas=[], agora_utc=datetime.now(timezone.utc), orcamento={})
        inicial = CA.politica()["CLASSES"]["SITE"]["ORCAMENTO_INICIAL_24H"]
        self.assertEqual(len(e["CORREM"]), inicial // 5)                # 40 / 5 = 8 fontes, nao 1
        self.assertEqual(e["ESPERAM"][0]["DOMINIOS_FECHADOS"]["z.it"]["PORQUE"], "TETO_NO_CICLO")
        self.assertEqual(e["ESPERAM"][0]["DOMINIOS_FECHADOS"]["z.it"]["ORCAMENTO_24H"], inicial)

    def visitar(self, dominio, horas_atras):
        """Um livro de uma onda anterior com uma visita ha N horas (o que `rodadas.ultima_visita_por_dominio` le)."""
        p = self.tmp / "ondas" / ("ANTIGA-%s" % dominio)
        p.mkdir(parents=True)
        t = datetime.now(timezone.utc) - timedelta(hours=horas_atras)
        (p / "TETO-ONDA.json").write_text(json.dumps({"PEDIDOS_POR_DOMINIO": {dominio: 5}}), encoding="utf-8")
        (p / "ONDA-WEB-ESTADO.json").write_text(json.dumps({"FONTES": [{"SOURCE_ID": "IT-T8-900", "CORREU": True,
            "RUN_ID": "IT-T8-%s-%s" % (t.strftime("%Y-%m-%d-%H%M%S"), "ab" * 8),
            "PEDIDOS_POR_DOMINIO": {dominio: 5}}]}), encoding="utf-8")

    def test_a_janela_d79_esta_desligada_por_omissao_e_liga_se_dizendo(self):
        import coleta_continua as C
        self.visitar("z.it", 2)
        c = {"SITES": [{"SOURCE_ID": "A", "DOMINIO": "z.it", "PREVISTOS": 2, "DOMINIOS": ["z.it"]}]}
        from tests import test_coleta_continua as T
        kw = dict(pecas={"ram": lambda: 9.0, "fonte": T._admite_tudo}, livro_24h=self.tmp / "L.ndjson", a_seco=True,
                  ligacao=lambda l: {"LIGADA": True, "PORQUE": "t"})
        r = C.ciclo(self.tmp / "ondas" / "CC", "s", c, **kw)
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], ["A"])
        self.assertIsNone(r["JANELA_24H"])
        r = C.ciclo(self.tmp / "ondas" / "CC", "s", c, janela_h=24, **kw)
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], [])
        self.assertEqual(r["ESPERAM"][0]["DOMINIOS_FECHADOS"]["z.it"]["PORQUE"], "JANELA_24H")

    def test_pausa_de_24h_e_retry_after_fecham_o_dominio(self):
        import coleta_continua as C
        t = time.time()
        ev = [{"TIPO": "RESPOSTA", "DOMINIO": "p.it", "EM": t - 100 + i, "STATUS": 429, "SINAIS": ["HTTP_429"]} for i in (1, 2)]
        ev += [{"TIPO": "RESPOSTA", "DOMINIO": "r.it", "EM": t - 10, "STATUS": 429, "SINAIS": ["HTTP_429", "RETRY_AFTER"],
                "RETRY_AFTER_S": 600}]
        c = [{"SOURCE_ID": d, "DOMINIO": d, "PREVISTOS": 1, "DOMINIOS": [d]} for d in ("p.it", "r.it", "livre.it")]
        e = C.escolher(c, feitas=[], ultima={}, reservas=ev, agora_utc=datetime.now(timezone.utc), orcamento={})
        self.assertEqual([x["SOURCE_ID"] for x in e["CORREM"]], ["livre.it"])
        porque = {x["SOURCE_ID"]: x["DOMINIOS_FECHADOS"][x["SOURCE_ID"]] for x in e["ESPERAM"]}
        self.assertEqual(porque["p.it"]["PORQUE"], "PAUSA_24H")
        self.assertEqual(porque["r.it"]["PORQUE"], "RETRY_AFTER")
        self.assertEqual(porque["r.it"]["ABRE_EM"], datetime.fromtimestamp(t - 10 + 600, timezone.utc).isoformat(timespec="seconds"))

    def test_o_gasto_de_24h_e_o_do_ciclo_somam_contra_o_orcamento(self):
        import coleta_continua as C
        t = time.time()
        ev = [{"TIPO": "RESERVA", "DOMINIO": "g.it", "EM": t - 3600} for _ in range(37)]
        c = [{"SOURCE_ID": "A", "DOMINIO": "g.it", "PREVISTOS": 2, "DOMINIOS": ["g.it"]},
             {"SOURCE_ID": "B", "DOMINIO": "g.it", "PREVISTOS": 2, "DOMINIOS": ["g.it"]}]
        e = C.escolher(c, feitas=[], ultima={}, reservas=ev, agora_utc=datetime.now(timezone.utc), orcamento={})
        self.assertEqual([x["SOURCE_ID"] for x in e["CORREM"]], ["A"])     # 37 + 2 = 39 <= 40; 39 + 2 > 40
        self.assertEqual(e["ESPERAM"][0]["DOMINIOS_FECHADOS"]["g.it"]["PORQUE"], "TETO_NO_CICLO")

    def test_a_onda_herda_o_livro_pelos_dois_nomes(self):
        """SINTONIA_CORTESIA_LIVRO manda sobre o nome antigo: um so pode partir o contador em dois."""
        src = (RAIZ / "ferramentas/big_collection/coleta_continua.py").read_text(encoding="utf-8")
        self.assertIn('os.environ["SINTONIA_TETO_24H"] = str(livro_24h)', src)
        self.assertIn('os.environ["SINTONIA_CORTESIA_LIVRO"] = str(livro_24h)', src)

    def test_um_ciclo_a_seco_pelo_cli_com_o_livro_d90(self):
        """--ensaio-a-seco: 0 rede, 0 Sala, com o livro vivo no formato antigo — le-o e nao o muda. A janela D79
        so fecha com --janela-24h (edagricole visitado ha 2 h)."""
        agora = datetime.now(timezone.utc)
        # o CLI pergunta ao portao REAL (nao se injecta): duas fontes que ele admite agora nesta arvore
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import collection_gate as GATE  # noqa: PLC0415
        a, b = [l["SOURCE_ID"] for l in GATE.inventario() if l["COLLECTION_ELIGIBLE"]][:2]
        plano = {"COORTE_SHA256": "c0" * 32, "RODADAS": [{"RODADA": 1, "FONTES": [
            {"SOURCE_ID": a, "DOMINIO": "edagricole.test", "PREVISTOS": 5, "DOMINIOS": ["edagricole.test"]},
            {"SOURCE_ID": b, "DOMINIO": "crea.test", "PREVISTOS": 5, "DOMINIOS": ["crea.test"]}]}]}
        (self.tmp / "plano.json").write_text(json.dumps(plano), encoding="utf-8")
        self.visitar("edagricole.test", 2)
        livro = self.tmp / "TETO-24H.json"
        _livro_d90(livro, [{"DOMINIO": "crea.test", "QTD": 38, "EM": agora.timestamp() - 60, "RUN_ID": "X", "LINHA": "SITES"}])
        antes = livro.read_bytes()
        env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}

        def cli(*extra):
            p = subprocess.run([sys.executable, "ferramentas/big_collection/coleta_continua.py", "--ensaio-a-seco",
                                "--base=%s" % (self.tmp / "ondas" / "CC"), "--plano=%s" % (self.tmp / "plano.json"),
                                "--teto-24h=%s" % livro, "--livros-do-dia=%s" % (self.tmp / "ondas")] + list(extra),
                               cwd=RAIZ, env=env, capture_output=True, text=True, timeout=300)
            self.assertEqual(p.returncode, 0, p.stderr[-1500:])
            return json.loads(p.stdout)
        r = cli()
        self.assertIsNone(r["PARA"], r)
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], [a])
        esp = {e["SOURCE_ID"]: e["DOMINIOS_FECHADOS"] for e in r["ESPERAM"]}
        self.assertEqual(esp[b]["crea.test"]["PORQUE"], "TETO_24H")
        self.assertEqual(esp[b]["crea.test"]["GASTO_24H"], 38)
        r = cli("--janela-24h")
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], [])
        esp = {e["SOURCE_ID"]: e["DOMINIOS_FECHADOS"] for e in r["ESPERAM"]}
        self.assertEqual(esp[a]["edagricole.test"]["PORQUE"], "JANELA_24H")
        self.assertEqual(livro.read_bytes(), antes, "o ensaio a seco nao escreve no livro")


class UmCicloEmLoopback(Base):
    def test_um_ciclo_inteiro_contra_o_servidor_local_com_o_livro_d90(self):
        """Um ciclo NAO seco: portao, backup, robo, onda (pedidos HTTP reais a 127.0.0.1, reservados e respondidos
        no livro), prova-teto do ciclo e das 24 h pelo ORCAMENTO VIGENTE (sem teto manual) e reconciliacao — com o
        livro vivo ainda no formato D90. No fim: o livro migrou, o original ficou em .D90.json, e o gasto antigo
        continua a contar."""
        from tests import test_coleta_continua as T
        import coleta_continua as C
        T.CONTAGEM.clear()
        livro = self.tmp / "TETO-24H.json"
        t = time.time()
        _livro_d90(livro, [{"DOMINIO": "cia.test", "QTD": 4, "EM": t - 600, "RUN_ID": "X", "LINHA": "SITES"}])
        os.environ["SINTONIA_TETO_24H"] = str(livro)
        base = self.tmp / "ondas" / "COLETA-CONTINUA"
        base.mkdir(parents=True)
        ledger = self.tmp / "runs.ndjson"
        sala, robo = T.Sala(), T.Robo(self.tmp / "PARAR.flag")
        onda = T.OndaFalsa(ledger, sala)
        pecas = {"portao": T.Portao(), "onda": onda, "relatorio": lambda e, s: 0, "ledger": ledger, "ram": lambda: 12.0,
                 "backup": lambda p: {"PROVA_VALE": True}, "robo": robo, "reconciliar": sala.reconciliar,
                 "fonte": T._admite_tudo}
        cands = {"SITES": C.candidatas_do_plano(T._plano([["IT-T9-002"]]))}
        r = C.ciclo(base, T.SHA, cands, pecas=pecas, livro_24h=livro, ligacao=lambda l: {"LIGADA": True, "PORQUE": "t"})
        self.assertIsNone(r["PARA"], r)
        self.assertEqual(r["TETO_VEM_DE"], "orcamento vigente (D124)")
        self.assertEqual(T.CONTAGEM, {"dois.test": 1})
        self.assertEqual(r["PROVA_TETO_CICLO"]["ESTADO"], "PASS")
        self.assertEqual(r["PROVA_TETO_24H"]["ESTADO"], "PASS")
        self.assertEqual(r["RECONCILIACAO"]["ESTADO"], "PASS")
        self.assertEqual(robo.eventos, ["PARAR", "TIRAR_FLAG", "LANCAR"])
        self.assertTrue((self.tmp / "TETO-24H.json.D90.json").exists())
        ev = CA.ler_eventos(livro)
        self.assertEqual(sum(1 for e in ev if e["DOMINIO"] == "dois.test" and e["TIPO"] == "RESERVA"), 1)
        self.assertEqual(sum(1 for e in ev if e["DOMINIO"] == "dois.test" and e["TIPO"] == "RESPOSTA"), 1)
        self.assertEqual(CA.estado_do_dominio("cia.test")["GASTO_24H"], 4)


# ── 2. a linha SITES e medida pelo que o transporte FAZ ───────────────────────
class ALigacaoPorComportamento(Base):
    def copia(self):
        d = self.tmp / "arvore"
        for x in ("coleta", "regras", "ferramentas/big_collection"):
            shutil.copytree(RAIZ / x, d / x, ignore=shutil.ignore_patterns("__pycache__", "*.json.gz"))
        return d

    def linha(self):
        import coleta_continua as C
        return next(l for l in C.LINHAS if l["LINHA"] == "SITES")

    def test_sites_ligada_nesta_arvore_pela_sonda(self):
        import coleta_continua as C
        m = C.medir_ligacao(self.linha())
        self.assertTrue(m["LIGADA"], m)
        self.assertTrue(m["PORQUE"].startswith("SONDA:"), m)
        self.assertEqual(m["MEDIDO"]["PEDIDOS_B"], 0)
        self.assertEqual(m["MEDIDO"]["PEDIDOS_A"], m["MEDIDO"]["RESERVAS_A"])

    def test_o_texto_da_chamada_nao_chega(self):
        """O transporte com a string `reservar24h(host, 1)` mas que pede SEM reservar: NAO ligada."""
        import coleta_continua as C
        d = self.copia()
        f = d / "coleta" / "italy_pilot_collect.mjs"
        s = f.read_text(encoding="utf-8")
        de = "      r = reservar24h(host, 1, { crawlDelayS: crawlDelay || null });"
        self.assertEqual(s.count(de), 1)
        f.write_text(s.replace(de, '      r = { ESTADO: "RESERVADO" }; // reservar24h(host, 1)'), encoding="utf-8")
        m = C.medir_ligacao(self.linha(), d)
        self.assertFalse(m["LIGADA"], m)
        self.assertIn("reservas no livro", m["PORQUE"])

    def test_o_transporte_que_ignora_o_livro_pausado_nao_esta_ligado(self):
        import coleta_continua as C
        d = self.copia()
        f = d / "coleta" / "italy_pilot_collect.mjs"
        s = f.read_text(encoding="utf-8")
        de = "  return gasto >= tetoDe(host) || CORTESIA.recuo.has(dominio24h(host)) || esgotado24h(host);"
        self.assertEqual(s.count(de), 1)
        s = s.replace(de, "  return gasto >= tetoDe(host) || CORTESIA.recuo.has(dominio24h(host));")
        de2 = "    if (r.ESTADO !== \"RESERVADO\")\n      throw"
        self.assertEqual(s.count(de2), 1)
        f.write_text(s.replace(de2, "    if (false)\n      throw"), encoding="utf-8")
        m = C.medir_ligacao(self.linha(), d)
        self.assertFalse(m["LIGADA"], m)
        self.assertIn("PAUSADO", m["PORQUE"])

    def test_sonda_que_nao_corre_nao_liga(self):
        import coleta_continua as C
        l = dict(self.linha(), SONDA="ferramentas/big_collection/nao_existe.mjs")
        self.assertFalse(C.medir_ligacao(l)["LIGADA"])


# ── 3. o livro D90 le-se e migra-se (Python e Node) ───────────────────────────
class OLivroAntigo(Base):
    def setUp(self):
        super().setUp()
        self.livro = self.tmp / "TETO-24H.json"
        os.environ["SINTONIA_TETO_24H"] = str(self.livro)          # como a coleta continua o passa
        self.t = time.time()
        _livro_d90(self.livro, [{"DOMINIO": "cia.it", "QTD": 3, "EM": self.t - 3600, "RUN_ID": "A", "LINHA": "SITES"},
                                {"DOMINIO": "youtube.com", "QTD": 2, "EM": self.t - 7200, "RUN_ID": "B", "LINHA": "SOCIAL"},
                                {"DOMINIO": "cia.it", "QTD": 1, "EM": self.t - 30 * 3600, "RUN_ID": "C", "LINHA": "SITES"}])

    def test_leitura_compativel_conta_o_gasto_como_antes(self):
        e = CA.estado_do_dominio("www.cia.it", self.t)
        self.assertEqual(e["ESTADO"], "LIDO")
        self.assertEqual(e["GASTO_24H"], 3)                        # a de ha 30 h ja saiu da janela
        self.assertEqual(CA.estado_do_dominio("googlevideo.com", self.t)["GASTO_24H"], 2)   # D41

    def test_reservar_migra_o_livro_e_guarda_o_original(self):
        original = self.livro.read_text(encoding="utf-8")
        r = CA.reservar("cia.it", run_id="N", linha="SITES", agora=self.t)
        self.assertEqual(r["ESTADO"], "RESERVADO", r)
        self.assertEqual(r["GASTO_24H"], 4)
        linhas = [json.loads(x) for x in self.livro.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(linhas), 3 + 2 + 1 + 1)
        self.assertTrue(all(x["TIPO"] == "RESERVA" for x in linhas))
        self.assertEqual(sum(1 for x in linhas if x.get("MIGRADO_DE") == CA.MIGRADO_DE), 6)
        self.assertEqual((self.tmp / "TETO-24H.json.D90.json").read_text(encoding="utf-8"), original)
        self.assertEqual(CA.estado_do_dominio("cia.it", self.t)["GASTO_24H"], 4)

    def test_a_fachada_reserva_24h_tambem_le_o_antigo(self):
        from coleta import reserva_24h as R24
        self.assertEqual(R24.gasto_24h("cia.it", self.t), 3)
        self.assertEqual(R24.reservar("cia.it", 1, run_id="F", linha="SITES", agora=self.t)["ESTADO"], "RESERVADO")

    def test_antigo_malformado_continua_unknown_e_nao_se_escreve(self):
        for mau in ('{"RESERVAS": [{"DOMINIO": "cia.it", "EM": 1}]}', '{"RESERVAS": 3}', '{"RESERVAS": [partido'):
            self.livro.write_text(mau, encoding="utf-8")
            r = CA.reservar("cia.it", run_id="N", linha="SITES", agora=self.t)
            self.assertEqual(r["ESTADO"], "UNKNOWN", (mau, r))
            self.assertEqual(self.livro.read_text(encoding="utf-8"), mau)
            self.assertFalse((self.tmp / "TETO-24H.json.D90.json").exists())

    def test_cli_migrar(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}
        p = subprocess.run([sys.executable, "coleta/cortesia_adaptativa.py", "--migrar", str(self.livro)], cwd=RAIZ,
                           env=env, capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["ESTADO"], "MIGRADO")
        self.assertEqual(json.loads(p.stdout)["EVENTOS"], 6)
        p = subprocess.run([sys.executable, "coleta/cortesia_adaptativa.py", "--migrar", str(self.livro)], cwd=RAIZ,
                           env=env, capture_output=True, text=True, timeout=120)
        self.assertEqual(json.loads(p.stdout)["ESTADO"], "JA_NDJSON")

    def test_node_le_o_antigo_igual_ao_python(self):
        doms = ["cia.it", "youtube.com", "nunca.it"]
        py = {d: CA.dobrar_eventos(CA.ler_eventos(self.livro), d, self.t) for d in doms}
        js = ("import * as C from './coleta/cortesia_adaptativa.mjs';const ev=C.lerEventos(%s);const o={};"
              "for(const d of %s)o[d]=C.dobrarEventos(ev,d,%r);console.log(JSON.stringify(o))"
              % (json.dumps(str(self.livro)), json.dumps(doms), self.t))
        self.assertEqual(json.loads(json.dumps(py)), self.node(js))

    def test_node_reserva_migra_e_python_le(self):
        js = ("import * as C from './coleta/cortesia_adaptativa.mjs';"
              "console.log(JSON.stringify(C.reservar('cia.it',{runId:'NODE',linha:'SITES',agora:%r})))" % self.t)
        r = self.node(js)
        self.assertEqual(r["ESTADO"], "RESERVADO", r)
        self.assertEqual(r["GASTO_24H"], 4)
        self.assertTrue((self.tmp / "TETO-24H.json.D90.json").exists())
        self.assertEqual(CA.estado_do_dominio("cia.it", self.t)["GASTO_24H"], 4)
        self.assertFalse(CA.e_livro_antigo(self.livro.read_text(encoding="utf-8")))

    def test_node_antigo_malformado_e_unknown(self):
        self.livro.write_text('{"RESERVAS": [{"DOMINIO": "cia.it"}]}', encoding="utf-8")
        js = ("import * as C from './coleta/cortesia_adaptativa.mjs';"
              "console.log(JSON.stringify(C.reservar('cia.it',{runId:'NODE',linha:'SITES'})))")
        self.assertEqual(self.node(js)["ESTADO"], "UNKNOWN")


# ── 4/5. o transporte Node contra um servidor local ───────────────────────────
class OTransporteNode(Base):
    def test_a_prova_local_passa_inteira(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}
        env["NODE_DISABLE_COMPILE_CACHE"] = "1"
        r = subprocess.run(["node", "provas/teto_adaptativo/transporte_rebase_local.mjs"], cwd=RAIZ, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        import re
        m = re.search(r"TRANSPORTE_REBASE_LOCAL · passou=(\d+) FALHAS=(\d+)", r.stdout)
        self.assertIsNotNone(m, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertEqual(m.group(2), "0", r.stdout[-3000:])
        self.assertGreaterEqual(int(m.group(1)), 7 if os.name == "nt" else 9, r.stdout[-3000:])
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])

    def test_sem_livro_o_teto_e_o_sem_livro_da_politica_nos_dois(self):
        self.assertEqual(CA.teto_sem_livro("www.cia.it"), CA.politica()["CLASSES"]["SITE"]["MINIMO_24H"])
        self.assertEqual(CA.teto_sem_livro("youtube.com"), CA.politica()["CLASSES"]["PLATAFORMA_GRANDE"]["MINIMO_24H"])
        js = ("import * as C from './coleta/cortesia_adaptativa.mjs';"
              "console.log(JSON.stringify([C.tetoSemLivro('cia.it'),C.tetoSemLivro('youtube.com')]))")
        self.assertEqual(self.node(js), [CA.teto_sem_livro("cia.it"), CA.teto_sem_livro("youtube.com")])
        self.assertLess(CA.teto_sem_livro("cia.it"), CA.politica()["CLASSES"]["SITE"]["ORCAMENTO_INICIAL_24H"])


# ── o orcamento esgotado recusa a reserva nos DOIS gemeos (nao so a pre-verificacao do transporte) ──
class OOrcamentoEsgotadoNosDois(Base):
    def test_a_reserva_41_e_adiada_em_python_e_em_node(self):
        """O transporte Node pergunta ANTES (esgotado24h) e o mutante «orcamento ignorado» no reservar do gemeo
        sobrevivia (mutacao do rebase, M05). Aqui pergunta-se ao reservar dos dois, direto."""
        livro = self.tmp / "L.ndjson"
        os.environ["SINTONIA_CORTESIA_LIVRO"] = str(livro)
        t0 = 1_800_000_000.0
        inicial = CA.politica()["CLASSES"]["SITE"]["ORCAMENTO_INICIAL_24H"]
        with open(livro, "w", encoding="utf-8") as h:
            for i in range(inicial):
                h.write(json.dumps({"TIPO": "RESERVA", "DOMINIO": "o.it", "EM": t0 + 10 * i, "RUN_ID": "r", "LINHA": "S"}) + "\n")
                h.write(json.dumps({"TIPO": "RESPOSTA", "DOMINIO": "o.it", "EM": t0 + 10 * i + 1, "STATUS": 200,
                                    "SINAIS": [], "RUN_ID": "r", "LINHA": "S"}) + "\n")
        t = t0 + 10 * inicial + 60
        py = CA.reservar("o.it", run_id="p", linha="S", agora=t)
        js = self.node("import * as C from './coleta/cortesia_adaptativa.mjs';"
                       "console.log(JSON.stringify(C.reservar('o.it',{runId:'n',linha:'S',agora:%r})))" % t)
        for r in (py, js):
            self.assertEqual((r["ESTADO"], r.get("MOTIVO")), ("ADIADO_ATE", "ORCAMENTO_ESGOTADO"), r)
            self.assertEqual(r["ATE"], t0 + 86400)
        self.assertEqual(sum(1 for l in livro.read_text(encoding="utf-8").splitlines()), 2 * inicial)


# ── o Crawl-delay no lado Python (o livro guarda-o e a reserva obedece) ───────
class OCrawlDelayPython(Base):
    def test_crawl_delay_maior_do_que_a_pausa_da_classe_manda(self):
        os.environ["SINTONIA_CORTESIA_LIVRO"] = str(self.tmp / "L.ndjson")
        t = 1_800_000_000.0
        pausa = CA.politica()["CLASSES"]["SITE"]["PAUSA_MINIMA_S"]
        self.assertEqual(CA.reservar("cd.it", run_id="a", linha="S", agora=t, crawl_delay_s=12)["ESTADO"], "RESERVADO")
        CA.registrar_resposta("cd.it", 200, {}, run_id="a", linha="S", agora=t + 1)
        r = CA.reservar("cd.it", run_id="a", linha="S", agora=t + 1 + pausa + 1)       # passou a pausa, nao o crawl
        self.assertEqual((r["ESTADO"], r.get("MOTIVO")), ("ADIADO_ATE", "PAUSA_MINIMA"), r)
        self.assertEqual(r["ATE"], t + 1 + 12)
        self.assertEqual(CA.reservar("cd.it", run_id="a", linha="S", agora=t + 1 + 12)["ESTADO"], "RESERVADO")


if __name__ == "__main__":
    unittest.main(verbosity=2)
