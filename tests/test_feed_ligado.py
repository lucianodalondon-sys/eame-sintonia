"""FEED-LIGADO (27/09) — o feed substitui o indice, o corpo do feed entra rotulado, o robots vale 24 h, e o
pedido condicional conta no teto.

Corre `provas/scrap_evolucao/feed_ligado_local.mjs` (o coletor real contra servidores em 127.0.0.1; quem conta
os pedidos e o SERVIDOR) e prova, sem rede:
  · o instalador `regras/ligar_feeds.py` so troca a aquisicao de linhas que existem, e volta atras byte a byte;
  · o pacote nasce da mesma regra da medida (`medir_feeds_com_rede.feeds`);
  · a linha ligada expande-se pelo dono do contrato (`regras/italy_contracts.mjs`) e passa a conferencia;
  · o executor nao le o corpo do feed como se fosse a pagina.
"""
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho


def _modulo(nome, rel):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(RAIZ, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


LF = _modulo("ligar_feeds", "regras/ligar_feeds.py")


def _node(args, cwd=RAIZ):
    env = {k: v for k, v in os.environ.items()
           if k not in ("SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA", "SINTONIA_TETO_24H")}
    env["NODE_DISABLE_COMPILE_CACHE"] = "1"
    return subprocess.run(["node", *args], cwd=cwd, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=600)


def _linha(sid, aq, **extra):
    return {"SOURCE_ID": sid, "OUTPUT_TYPE": "HTML", "TERRITORY": "T9", "ACQUISITION": aq, **extra}


HTML_AQ = {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL", "INDEX_URL": "https://www.a.it/news/",
           "LINK_PATTERN": "^https?://(www\\.)?a\\.it/news/.+$", "MAX_TARGETS": 15}


class TestProvaLocal(unittest.TestCase):
    def test_o_coletor_real_no_teto_com_livro_de_24h(self):
        r = _node(["provas/scrap_evolucao/feed_ligado_local.mjs"])
        m = re.search(r"FEED_LIGADO_LOCAL · passou=(\d+) FALHAS=(\d+)", r.stdout)
        self.assertIsNotNone(m, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertEqual(m.group(2), "0", r.stdout[-4000:])
        self.assertGreaterEqual(int(m.group(1)), 12)
        self.assertEqual(r.returncode, 0)


class TestInstalador(unittest.TestCase):
    def pacote(self):
        return {"FEEDS": {
            "IT-T1-001": {"FEED_URL": "https://www.a.it/feed/", "LIGAR": True},
            "IT-T1-002": {"FEED_URL": "https://www.b.it/feed/", "LIGAR": True},
            "IT-T1-003": {"FEED_URL": "https://www.c.it/eventi/x/feed", "LIGAR": False, "PORQUE": "feed de um evento"},
            "IT-T1-004": {"FEED_URL": "https://www.d.it/feed/", "LIGAR": True},
            "IT-T1-005": {"FEED_URL": "https://www.e.it/feed/", "LIGAR": True},
            "IT-T1-006": {"FEED_URL": "https://www.f.it/feed/", "LIGAR": True},
        }}

    def tabela(self):
        return {"FONTES": [
            _linha("IT-T1-001", dict(HTML_AQ)),
            _linha("IT-T1-003", dict(HTML_AQ)),
            _linha("IT-T1-004", dict(HTML_AQ), ESTADO_CATALOGO="RETIRADA_POR_DECISAO"),
            _linha("IT-T1-005", {"STRATEGY": "FEED_DISCOVERY", "FEED_URL": "https://www.e.it/feed/"}),
            _linha("IT-T1-006", {"STRATEGY": "CUSTOM_ADAPTER", "ADAPTER_ID": "X"}),
            _linha("IT-T1-099", dict(HTML_AQ)),
        ]}

    def test_so_troca_linhas_que_existem_e_diz_porque_das_outras(self):
        d = {x["SOURCE_ID"]: x["DECISAO"] for x in LF.plano(self.tabela(), self.pacote())}
        self.assertEqual(d, {"IT-T1-001": "LIGAR", "IT-T1-002": "SEM_LINHA_NA_TABELA", "IT-T1-003": "NAO_LIGAR",
                             "IT-T1-004": "RETIRADA", "IT-T1-005": "JA_LIGADA", "IT-T1-006": "ESTRATEGIA_INESPERADA"})

    def test_aplicar_nao_cria_linha_guarda_o_caminho_de_volta_e_desfazer_repoe(self):
        t = self.tabela()
        antes = copy.deepcopy(t)
        n = LF.aplicar(t, LF.plano(t, self.pacote()), "P.json", "2026-09-27T00:00:00+00:00")
        self.assertEqual(n, 1)
        self.assertEqual(len(t["FONTES"]), len(antes["FONTES"]), "o instalador nunca cria linha")
        self.assertNotIn("IT-T1-002", {l["SOURCE_ID"] for l in t["FONTES"]})
        l = t["FONTES"][0]
        # o feed substitui o indice: o INDEX_URL fica (regra V1 da capa, plano da onda), o LINK_PATTERN nao
        self.assertEqual(l["ACQUISITION"], {"STRATEGY": "FEED_DISCOVERY", "FEED_URL": "https://www.a.it/feed/",
                                            "INDEX_URL": "https://www.a.it/news/"})
        self.assertEqual(l["FEED_LIGADO"]["ACQUISITION_ANTERIOR"], HTML_AQ)
        self.assertEqual(LF.desfazer(t), ["IT-T1-001"])
        self.assertEqual(t, antes)

    def test_a_previsao_sai_das_datas_do_feed_e_sem_corpo_e_nao_sei(self):
        tmp = tempfile.mkdtemp(prefix="feed-ligado-prev-")
        try:
            # referencia 2026-09-27 12:00 UTC; 14 com corpo e 21 sem corpo nos ultimos 7 dias, 2 velhos, 1 de outro site
            item = lambda n, dia, corpo: (
                f"<item><title>{n}</title><link>https://www.a.it/{n}/</link><pubDate>{dia} Sep 2026 08:00:00 +0000</pubDate>"
                + (f"<content:encoded><![CDATA[<p>{n}</p>]]></content:encoded>" if corpo else "") + "</item>")
            xs = [item(f"c{i}", f"Sun, {21 + i % 6}", True) for i in range(14)]
            xs += [item(f"s{i}", f"Sun, {21 + i % 6}", False) for i in range(21)]
            xs += [item("velho1", "Mon, 01", True), item("velho2", "Mon, 01", False)]
            xs += ["<item><link>https://outro.it/x/</link><pubDate>Sun, 27 Sep 2026 08:00:00 +0000</pubDate></item>"]
            os.makedirs(os.path.join(tmp, "IT-T1-001"))
            f = os.path.join(tmp, "IT-T1-001", "CORPO.bin")
            with open(f, "w", encoding="utf-8") as fh:
                fh.write('<rss xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel>' + "".join(xs) + "</channel></rss>")
            ref = 1790510400          # 2026-09-27T12:00:00Z
            os.utime(f, (ref, ref))
            pac = self.pacote()
            pac["FEEDS"]["IT-T1-001"]["FEED_URL"] = "https://www.a.it/feed/"
            decs = LF.plano(self.tabela(), pac)
            LF.conferir(decs, tmp)
            c = next(d for d in decs if d["SOURCE_ID"] == "IT-T1-001")["CONFERIDO"]
            self.assertEqual(c["ITENS_QUE_PASSAM"], 37, c)
            self.assertEqual((c["COM_CORPO"], c["SEM_CORPO"]), (15, 22))
            self.assertEqual(c["PUBLICADOS_7D"], {"COM_CORPO": 14, "SEM_CORPO": 21})
            # antes: 35 publicados/semana = 5/dia, mas so 3 pedidos cabem; depois: 2/dia sem pedido + 3 pedidos
            self.assertEqual(c["PREVISAO"], {"DOC_DIA_ANTES": 3, "DOC_DIA_DEPOIS": 5,
                                             "DOC_1A_VOLTA_ANTES": 3, "DOC_1A_VOLTA_DEPOIS": 18})
            self.assertEqual(c["PRIMEIRA_VOLTA"], {"SEM_PEDIDO_BODY_FROM_FEED": 15, "A_PEDIR": 3})
            p = LF.previsao(decs)
            self.assertEqual(p["FONTES_CONFERIDAS"], 1)
            # IT-T1-005 ja esta ligada e entra na soma — sem corpo na pasta, e NAO SEI, nao zero
            self.assertEqual(p["NAO_SEI"], ["IT-T1-005"])
            self.assertEqual(p["DOC_1A_VOLTA_DEPOIS"], 18)
            outro = [d for d in LF.plano({"FONTES": [_linha("IT-T1-002", dict(HTML_AQ))]}, pac) if d["DECISAO"] == "LIGAR"]
            LF.conferir(outro, tmp)
            self.assertEqual(outro[0]["CONFERIDO"]["ESTADO"], "NAO SEI")
            self.assertEqual(LF.previsao(outro)["NAO_SEI"], ["IT-T1-002"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_o_pacote_nasce_da_regra_da_medida(self):
        med = _modulo("medir_feeds_com_rede", "provas/scrap_evolucao/medir_feeds_com_rede.py")
        feeds = med.feeds()
        with open(os.path.join(RAIZ, "regras", "FEED-LIGADO-PACOTE.json"), encoding="utf-8") as f:
            pac = json.load(f)
        for sid, p in pac["FEEDS"].items():
            self.assertEqual(p["FEED_URL"], feeds[sid], sid)
        self.assertEqual(sum(1 for p in pac["FEEDS"].values() if p["LIGAR"]), 12)
        self.assertFalse(pac["FEEDS"]["IT-T5-186"]["LIGAR"], "o feed de UM evento nao e o indice da fonte")
        self.assertNotIn("IT-T12-130", pac["FEEDS"], "fechada 24 h na medida: sem medida, nao entra")

    def test_a_linha_ligada_expande_pelo_dono_do_contrato_e_passa_a_conferencia(self):
        tmp = tempfile.mkdtemp(prefix="feed-ligado-regras-")
        try:
            shutil.copytree(os.path.join(RAIZ, "regras"), os.path.join(tmp, "regras"))
            tab = os.path.join(tmp, "regras", "italy_contracts_onboarded.json")
            sha_antes = hashlib.sha256(open(tab, "rb").read()).hexdigest()
            self.assertEqual(LF.main(["--aplicar", "--tabela=" + tab]), 0)
            t = json.load(open(tab, encoding="utf-8"))
            ligadas = [l["SOURCE_ID"] for l in t["FONTES"] if (l.get("ACQUISITION") or {}).get("STRATEGY") == "FEED_DISCOVERY"]
            self.assertTrue(ligadas, "nenhuma linha do pacote na tabela desta arvore")
            js = ("import(process.argv[1]).then(async m=>{const r=await import(process.argv[2]);const ids=JSON.parse(process.argv[3]);"
                  "const out={};for(const s of ids){const c=m.CONTRACTS[s];r.conferirAquisicao(s,c.ACQUISITION);"
                  "out[s]={E:c.CANONICAL_ENTRY_URL,F:c.ACQUISITION.FEED_URL,R:c.ROUTE_TYPE,D:c.DISCOVERY_METHOD}};console.log(JSON.stringify(out))})")
            r = _node(["-e", js, "file://" + os.path.join(tmp, "regras", "italy_contracts.mjs"),
                       "file://" + os.path.join(tmp, "regras", "motor_de_rota.mjs"), json.dumps(ligadas)])
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            out = json.loads(r.stdout.strip().splitlines()[-1])
            for s, c in out.items():
                self.assertEqual(c["E"], c["F"], s)
                self.assertEqual(c["R"], "DISCOVERED_ROUTE")
                self.assertTrue(c["D"].startswith("FEED:"), c["D"])
            self.assertEqual(LF.main(["--desfazer", "--tabela=" + tab]), 0)
            self.assertEqual(hashlib.sha256(open(tab, "rb").read()).hexdigest(), sha_antes, "desfazer nao repos os bytes")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestSitemapNoAcervo(unittest.TestCase):
    def test_a_medida_le_sitemap_como_o_coletor_e_nao_conta_mensagens_da_casa(self):
        MS = _modulo("medir_sitemap_no_acervo", "provas/scrap_evolucao/medir_sitemap_no_acervo.py")
        amostras = ["User-agent: *\nDisallow:\nSitemap: https://a.it/s.xml # comentario\nsitemap:https://a.it/n.xml\n",
                    "User-agent: *\r\nDisallow: /x/\r\n", "# Sitemap: https://a.it/comentada.xml\nUser-agent: *\n"]
        js = ("import('./coleta/italy_pilot_collect.mjs').then(m=>console.log(JSON.stringify("
              "JSON.parse(process.argv[1]).map(t=>m.sitemapsDoRobots(t)))))")
        r = _node(["-e", js, json.dumps(amostras)])
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        self.assertEqual(json.loads(r.stdout.strip().splitlines()[-1]), [MS.sitemaps(t) for t in amostras])
        self.assertEqual(MS.sitemaps(amostras[0]), ["https://a.it/s.xml", "https://a.it/n.xml"])
        for msg in ("robots inacessivel apos 2 tentativas (URLError) — UNKNOWN, tratado como barrado por prudencia",
                    "HTTP 404 — o host nao publica robots.txt", "<!DOCTYPE html><html>"):
            self.assertFalse(MS.e_robots(msg), msg)
        m = MS.medir()
        self.assertEqual(m["K"] + (m["N"] - m["K"]) + m["NAO_SEI_TEXTO_CORTADO"], m["FONTES_COM_ROBOTS_LEGIVEL"])


class TestExecutor(unittest.TestCase):
    def test_o_corpo_do_feed_nao_e_lido_como_pagina(self):
        import italy_executor as E
        tmp = tempfile.mkdtemp(prefix="feed-ligado-exec-")
        try:
            p = os.path.join(tmp, "x.body-from-feed.html")
            b = b"<p>Pubblicato il 24/09/2026</p>"
            open(p, "wb").write(b)
            obs = {"RAW_PATH": p, "RAW_SHA256": hashlib.sha256(b).hexdigest()}
            self.assertEqual(E.bytes_da_pagina(obs), b, "a pagina com o sha certo le-se")
            self.assertIsNone(E.bytes_da_pagina(dict(obs, RAW_EVIDENCE_STATE="BODY_FROM_FEED")))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
