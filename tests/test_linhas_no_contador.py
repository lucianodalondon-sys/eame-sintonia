# -*- coding: utf-8 -*-
"""LINHAS-NO-CONTADOR (28/09/2026) — BUSCA, CIENCIA e SOCIAL no MESMO contador da linha SITES (D86/D90/D124).

    py -m unittest tests.test_linhas_no_contador

O que se prova aqui, sem rede (servidores em 127.0.0.1, livros e politicas temporarios):
  1. A PORTA (`coleta/reserva_24h.pedir`): a reserva vem ANTES do pedido; sem RESERVADO o pedido nao sai; a
     resposta (e o sinal 429/Retry-After) vai ao livro DEPOIS.
  2. D90-2 adversarial: duas linhas, em PROCESSOS diferentes, reservam o MESMO dominio ao MESMO tempo — a 2.a
     recebe ADIADO_ATE e nao pede (o servidor conta 1).
  3. D124-3: as APIs com limite publicado (ORCID, OpenAlex, Crossref, YouTube Data, Google CSE) usam o limite
     publicado, com a fonte do numero; sem numero diario publicado, NAO_SEI e o minimo seguro. A Custom Search
     e o YouTube Data vivem no mesmo dominio e sao orcamentos DIFERENTES.
  4. SOCIAL: ligar ao contador NAO abre rota nenhuma (a matriz decide o mesmo que decidia na base; o robots
     continua a barrar com o orcamento livre).
  5. O portao de egresso real (`rodadas.portao_real`) diz PASSA=False quando o rede.py reprova (o mutante
     PASSA=True fixo sobrevivia na verificacao do teto).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for p in (RAIZ, RAIZ / "coleta", RAIZ / "ferramentas" / "big_collection", RAIZ / "ferramentas" / "linha_busca"):
    sys.path.insert(0, str(p))
import _gavetas  # noqa: E402,F401
import cortesia_adaptativa as CA  # noqa: E402
import reserva_24h as R24  # noqa: E402

ENVS = ("SINTONIA_CORTESIA_LIVRO", "SINTONIA_TETO_24H", "SINTONIA_CORTESIA_POLITICA", "SINTONIA_LINHA",
        "SINTONIA_RUN_ID", "SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA", "SINTONIA_CORTESIA_ALERTAS")


class Servidor:
    """Conta cada pedido (host, caminho, instante). `atraso_s` segura a resposta (pedidos em voo)."""

    def __init__(self, atraso_s=0.0, status=200, robots=None):
        self.pedidos = []
        srv = self

        class H(BaseHTTPRequestHandler):
            def do_GET(self):                                      # noqa: N802
                srv.pedidos.append({"HOST": (self.headers.get("Host") or "").split(":")[0], "P": self.path,
                                    "T": time.time()})
                if self.path.startswith("/robots.txt"):
                    if robots is None:
                        self.send_response(404)
                        self.end_headers()
                        return
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(robots.encode())
                    return
                time.sleep(atraso_s)
                corpo = b'{"ok": true, "group": [], "results": []}'
                self.send_response(status)
                if status == 429:
                    self.send_header("Retry-After", "3600")
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(corpo)))
                self.end_headers()
                self.wfile.write(corpo)

            def log_message(self, *a):
                pass
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.porta = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def url(self, caminho="/pagina"):
        return "http://127.0.0.1:%d%s" % (self.porta, caminho)

    def fechar(self):
        self.srv.shutdown()
        self.srv.server_close()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="linhas-contador-"))
        self.antes = {k: os.environ.get(k) for k in ENVS}
        for k in ENVS:
            os.environ.pop(k, None)
        self.livro = self.tmp / "LIVRO-CORTESIA.ndjson"
        os.environ["SINTONIA_CORTESIA_LIVRO"] = str(self.livro)

    def tearDown(self):
        import shutil
        for k, v in self.antes.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        CA.politica(recarregar=True)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def politica(self, **mudar):
        """Uma copia da politica real com as mudancas dadas (caminho de chaves -> valor)."""
        pol = json.loads((RAIZ / "regras" / "POLITICA-CORTESIA-ADAPTATIVA.json").read_text(encoding="utf-8"))
        for chave, v in mudar.items():
            d = pol
            partes = chave.split("__")
            for x in partes[:-1]:
                d = d[x]
            d[partes[-1]] = v
        f = self.tmp / "politica.json"
        f.write_text(json.dumps(pol), encoding="utf-8")
        os.environ["SINTONIA_CORTESIA_POLITICA"] = str(f)
        CA.politica(recarregar=True)
        return pol

    def eventos(self, dom=None):
        ev = CA.ler_eventos(self.livro)
        return [e for e in ev if dom is None or e["DOMINIO"] == dom]


# ── 1. a porta: reserva ANTES, pedido so com RESERVADO, resposta DEPOIS ───────────────────────────────
class APorta(Base):
    def test_a_reserva_esta_no_livro_quando_o_pedido_sai(self):
        vistos = []

        def fazer():
            vistos.append([e["TIPO"] for e in self.eventos("porta.test")])
            return 200, {}, b"x" * 10
        r, res = R24.pedir("http://porta.test/a", fazer, run_id="T", linha="CIENCIA")
        self.assertEqual(r["ESTADO"], "RESERVADO")
        self.assertEqual(vistos, [["RESERVA"]])                     # a reserva ja estava escrita
        self.assertEqual([e["TIPO"] for e in self.eventos("porta.test")], ["RESERVA", "RESPOSTA"])
        self.assertEqual(res[0], 200)

    def test_sem_reserva_o_pedido_nao_sai(self):
        agora = time.time()
        with open(self.livro, "w", encoding="utf-8") as h:
            for i in (1, 2):
                h.write(json.dumps({"TIPO": "RESPOSTA", "DOMINIO": "pausado.test", "EM": agora - 10 + i,
                                    "SINAIS": ["HTTP_429"], "STATUS": 429, "RUN_ID": "x", "LINHA": "x"}) + "\n")
        chamado = []
        r, res = R24.pedir("http://pausado.test/a", lambda: chamado.append(1), run_id="T", linha="BUSCA")
        self.assertEqual((r["ESTADO"], r["MOTIVO"], res, chamado), ("ADIADO_ATE", "PAUSA_24H", None, []))

    def test_sem_livro_nao_ha_contador_e_nada_sai(self):
        os.environ.pop("SINTONIA_CORTESIA_LIVRO")
        chamado = []
        r, res = R24.pedir("http://x.test/a", lambda: chamado.append(1), run_id="T", linha="SOCIAL")
        self.assertEqual((r["ESTADO"], res, chamado), ("FAIL", None, []))

    def test_o_429_vai_ao_livro_como_sinal_e_o_recuo_vale(self):
        e = urllib.error.HTTPError("http://recuo.test/a", 429, "x", {"Retry-After": "600"}, None)

        def fazer():
            raise e
        with self.assertRaises(urllib.error.HTTPError):
            R24.pedir("http://recuo.test/a", fazer, run_id="T", linha="SOCIAL")
        resp = [x for x in self.eventos("recuo.test") if x["TIPO"] == "RESPOSTA"]
        self.assertEqual(resp[0]["SINAIS"], ["HTTP_429", "RETRY_AFTER"])
        chamado = []
        r, res = R24.pedir("http://recuo.test/b", lambda: chamado.append(1), run_id="T", linha="SOCIAL")
        self.assertEqual((r["ESTADO"], r["MOTIVO"], chamado), ("ADIADO_ATE", "RETRY_AFTER", []))

    def test_o_scrap_http_nao_reserva_duas_vezes_o_pedido_da_porta(self):
        """Um processo com o abridor do scrap_http instalado e uma linha que pede pela porta: 1 reserva."""
        import scrap_http  # noqa: F401 — instala o abridor
        s = Servidor()
        try:
            import youtube_oficial as YT
            YT._http(s.url("/youtube/v3/videos?id=x"))
        finally:
            s.fechar()
        self.assertEqual(len(s.pedidos), 1)
        self.assertEqual([e["TIPO"] for e in self.eventos()], ["RESERVA", "RESPOSTA"])

    def test_um_salto_para_outro_dominio_dentro_da_porta_reserva_a_parte(self):
        """Dentro da porta (orcamento 127.0.0.1) o abridor ve um pedido a OUTRO dominio (localhost): esse nao
        esta coberto pela reserva da porta, e reserva no livro por si."""
        import scrap_http  # noqa: F401 — instala o abridor
        import urllib.request
        s = Servidor()
        try:
            def fazer():
                with urllib.request.urlopen("http://localhost:%d/outro" % s.porta, timeout=10) as r:
                    return r.status, {}, r.read()
            R24.pedir(s.url("/a"), fazer, run_id="T", linha="SOCIAL")
        finally:
            s.fechar()
        doms = [(e["DOMINIO"], e["TIPO"]) for e in self.eventos()]
        self.assertIn(("localhost", "RESERVA"), doms)
        self.assertEqual(sum(1 for d in doms if d == ("127.0.0.1", "RESERVA")), 1)


# ── 2. D90-2: duas linhas, o mesmo dominio, o mesmo instante ──────────────────────────────────────────
_FILHO = r'''
import json, os, sys, time
sys.path[:0] = [sys.argv[1], sys.argv[1] + "/coleta", sys.argv[1] + "/ferramentas/linha_busca"]
import _gavetas
linha, url, t0 = sys.argv[2], sys.argv[3], float(sys.argv[4])
os.environ["SINTONIA_LINHA"] = linha
if linha == "CIENCIA":
    import pesquisadores_t6 as M
    f = lambda: M.pedir_para_sonda(url)
elif linha == "BUSCA":
    import linha_busca as M
    f = lambda: M.pedir_para_sonda(url, "API")
else:
    import youtube_oficial as M
    f = lambda: M._http(url)
while time.time() < t0:
    time.sleep(0.001)
try:
    r = f()
except Exception as ex:
    r = "%s: %s" % (type(ex).__name__, ex)
print(json.dumps({"LINHA": linha, "R": str(r)[:300]}))
'''


_FILHO_NODE = r'''
import { pathToFileURL } from "node:url";
const [raiz, url, t0] = process.argv.slice(2);
process.env.SINTONIA_LINHA = "SITES";
const M = await import(pathToFileURL(raiz + "/coleta/italy_pilot_collect.mjs").href);
while (Date.now() / 1000 < Number(t0)) await new Promise(r => setTimeout(r, 1));
let r;
try { r = await M.baixarParaSonda(url, { runId: "SITES-D90-2" }); } catch (e) { r = "EXCECAO: " + String(e && e.message || e); }
console.log(JSON.stringify({ LINHA: "SITES", R: JSON.stringify(r && r.buf ? { ...r, buf: "<bytes>" } : r).slice(0, 300) }));
'''


class DuasLinhasOMesmoDominio(Base):
    """D90-2 adversarial: tres linhas em tres processos, o mesmo dominio, o mesmo instante."""

    def correr(self, linhas, url):
        f = self.tmp / "filho.py"
        f.write_text(_FILHO, encoding="utf-8")
        fn = self.tmp / "filho.mjs"
        fn.write_text(_FILHO_NODE, encoding="utf-8")
        env = dict(os.environ, NO_PROXY="*", no_proxy="*", ITALY_OPS_ROOT=str(self.tmp / "ops"))
        for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
            env.pop(k, None)
        t0 = time.time() + 3.0
        ps = [subprocess.Popen(["node", str(fn), str(RAIZ), url, str(t0)] if l == "SITES" else
                               [sys.executable, str(f), str(RAIZ), l, url, str(t0)], env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for l in linhas]
        return [json.loads(p.communicate(timeout=120)[0].strip().splitlines()[-1]) for p in ps]

    def test_o_ultimo_lugar_do_orcamento_so_um_pede(self):
        """O dominio tem 1 lugar no orcamento de 24 h. Quatro linhas (SITES em Node; CIENCIA, BUSCA e SOCIAL em
        Python), quatro processos, o mesmo instante: o servidor ve 1 pedido e o livro 1 reserva nova; as linhas
        Python que perderam recebem ADIADO_ATE ORCAMENTO_ESGOTADO e NAO pedem."""
        self.politica(CLASSES__SITE__ORCAMENTO_INICIAL_24H=2, CLASSES__SITE__PAUSA_MINIMA_S=0)
        s = Servidor(atraso_s=0.8)
        try:
            dom = CA.dominio("127.0.0.1")
            t = time.time() - 3600
            with open(self.livro, "w", encoding="utf-8") as h:
                h.write(json.dumps({"TIPO": "RESERVA", "DOMINIO": dom, "EM": t, "RUN_ID": "x", "LINHA": "SITES"}) + "\n")
                h.write(json.dumps({"TIPO": "RESPOSTA", "DOMINIO": dom, "EM": t + 1, "STATUS": 200, "SINAIS": [],
                                    "RUN_ID": "x", "LINHA": "SITES"}) + "\n")
            rs = self.correr(["SITES", "CIENCIA", "BUSCA", "SOCIAL"], s.url("/youtube/v3/videos"))
        finally:
            s.fechar()
        self.assertEqual(len(s.pedidos), 1, (s.pedidos, rs))
        novas = [e for e in self.eventos(dom) if e["TIPO"] == "RESERVA" and e["EM"] > t + 10]
        self.assertEqual(len(novas), 1, (novas, rs))
        ganhou = novas[0]["LINHA"]
        py = [r for r in rs if r["LINHA"] != "SITES" and r["LINHA"] != ganhou]
        self.assertEqual(len(py), 3 if ganhou == "SITES" else 2, rs)
        for r in py:
            self.assertIn("ADIADO_ATE", r["R"], rs)
            self.assertIn("ORCAMENTO_ESGOTADO", r["R"], rs)

    def test_um_de_cada_vez_a_reserva_atomica_entre_processos(self):
        """Orcamento livre, mas 1 pedido de cada vez por dominio: com o 1.o em voo, a reserva directa da 2.a
        linha (reserva_24h.reservar, sem esperar) volta ADIADO_ATE UM_DE_CADA_VEZ e nao escreve nada."""
        self.politica(CLASSES__SITE__PAUSA_MINIMA_S=0)
        s = Servidor(atraso_s=3.0)
        try:
            f = self.tmp / "filho.py"
            f.write_text(_FILHO, encoding="utf-8")
            env = dict(os.environ, NO_PROXY="*", no_proxy="*")
            p = subprocess.Popen([sys.executable, str(f), str(RAIZ), "CIENCIA", s.url(), str(time.time())], env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            fim = time.time() + 20
            while not s.pedidos and time.time() < fim:
                time.sleep(0.02)
            r = R24.reservar("127.0.0.1", 1, run_id="T2", linha="BUSCA")
            p.communicate(timeout=60)
        finally:
            s.fechar()
        self.assertEqual((r["ESTADO"], r["MOTIVO"]), ("ADIADO_ATE", "UM_DE_CADA_VEZ"))
        self.assertEqual(len(s.pedidos), 1)
        self.assertEqual([e["LINHA"] for e in self.eventos() if e["TIPO"] == "RESERVA"], ["CIENCIA"])


# ── 3. D124-3: o limite PUBLICADO, com a fonte; NAO_SEI = o minimo seguro ─────────────────────────────
class APIsNoLimitePublicado(Base):
    def api(self):
        return CA.politica()["CLASSES"]["API_COM_LIMITE_PUBLICADO"]

    def test_cada_api_diz_o_numero_e_de_onde_ele_vem(self):
        api = self.api()
        for d, a in api["DOMINIOS"].items():
            self.assertTrue(a["CITA"].startswith("https://"), d)
            self.assertTrue(a.get("FONTE_DO_NUMERO"), d)
            lim = a["LIMITE_PUBLICADO_24H"]
            _, k = CA.classe_de(d)
            if lim == "NAO_SEI":
                self.assertEqual(k["INICIAL"], api["MINIMO_24H"], d)          # comeca no minimo seguro
                if k["DOBRA"]:
                    self.assertTrue(a.get("LIMITE_DERIVADO"), d)             # o teto diz de onde vem
            else:
                self.assertIsInstance(lim, int, d)
                self.assertLessEqual(k["INICIAL"], lim, d)
                self.assertLessEqual(k["TETO"], lim, d)
                self.assertFalse(k["DOBRA"], d)

    def test_as_cinco_apis_da_missao_pelos_enderecos_do_codigo(self):
        import pesquisadores_t6 as T6
        import youtube_oficial as YT
        import api_oficial as API
        casos = {T6.OPENALEX: ("openalex.org", 100000), T6.CROSSREF: ("crossref.org", 5),
                 T6.ORCID_WORKS % "0000-0001-0000-0001": ("orcid.org", 5),
                 API.ENDERECO_CSE + "?q=x": ("googleapis.com/customsearch", 100),
                 YT.API + "/search?q=x": ("googleapis.com/youtube/search", 100),
                 YT.API + "/videos?id=x": ("googleapis.com/youtube", 10000),
                 YT.API + "/commentThreads?videoId=x": ("googleapis.com/youtube", 10000)}
        for url, (dom, ini) in casos.items():
            host = url.split("/")[2]
            k = CA.dominio_do_pedido(host, url)
            self.assertEqual(k, dom, url)
            self.assertEqual(CA.classe_de(k)[0], "API_COM_LIMITE_PUBLICADO", url)
            self.assertEqual(CA.classe_de(k)[1]["INICIAL"], ini, url)

    def test_os_numeros_nao_passam_dos_donos_que_ja_existem_no_codigo(self):
        import api_oficial as API
        import social_matriz as mz
        d = self.api()["DOMINIOS"]
        self.assertLessEqual(d["googleapis.com/customsearch"]["ORCAMENTO_24H"], API.QUOTA_DIA["GOOGLE_CSE"])
        lim = mz.LIMITE_PADRAO_PROJETO["YOUTUBE"]
        self.assertLessEqual(d["googleapis.com/youtube/search"]["ORCAMENTO_24H"], lim["SEARCH"])
        self.assertLessEqual(d["googleapis.com/youtube"]["ORCAMENTO_24H"], lim["GENERAL"])

    def test_a_101a_consulta_do_cse_nao_sai(self):
        """100 gratis por dia; a 101.a seria PAGA (rota paga proibida): ADIADO_ATE, nada sai."""
        url = "https://www.googleapis.com/customsearch/v1?q=x"
        t = 1_800_000_000.0
        for i in range(100):
            r = CA.reservar("www.googleapis.com", run_id="T", linha="BUSCA", url=url, agora=t)
            self.assertEqual(r["ESTADO"], "RESERVADO", (i, r))
            CA.registrar_resposta("www.googleapis.com", 200, {}, url=url, run_id="T", linha="BUSCA", agora=t + 0.1)
            t += 2
        r = CA.reservar("www.googleapis.com", run_id="T", linha="BUSCA", url=url, agora=t)
        self.assertEqual((r["ESTADO"], r["MOTIVO"]), ("ADIADO_ATE", "ORCAMENTO_ESGOTADO"))
        # o YouTube Data, no MESMO dominio, continua com o orcamento dele
        r = CA.reservar("www.googleapis.com", run_id="T", linha="SOCIAL", url="https://www.googleapis.com/youtube/v3/videos",
                        agora=t)
        self.assertEqual(r["ESTADO"], "RESERVADO")

    def test_sem_url_paga_o_dominio_inteiro_no_minimo(self):
        k = CA.dominio_do_pedido("www.googleapis.com")
        self.assertEqual(k, "googleapis.com")
        self.assertEqual(CA.classe_de(k)[1]["TETO"], self.api()["MINIMO_24H"])


# ── 4. SOCIAL: o contador nao abre rota nenhuma ─────────────────────────────────────────────────────
class SocialNaoAbreRota(Base):
    def test_a_matriz_decide_o_mesmo_que_na_base_com_o_contador_ligado(self):
        import social_matriz as mz
        foto = json.loads((RAIZ / "tests" / "fixtures" / "linhas_no_contador" / "DECISOES-SOCIAIS-e2413970.json")
                          .read_text(encoding="utf-8"))["DECISOES"]
        os.environ["SINTONIA_LINHA"] = "SOCIAL"
        for chave, antes in foto.items():
            plat, cap = chave.split("/")
            agora = mz.decisao(plat, cap)
            if antes["DECISAO"] != mz.PERMITIDA_SIM:
                self.assertNotEqual(agora["DECISAO"], mz.PERMITIDA_SIM, chave)     # nada fechado abriu
            self.assertEqual(json.loads(json.dumps(agora)), antes, chave)

    def test_instagram_linkedin_continuam_fechados_onde_estavam(self):
        import social_matriz as mz
        os.environ["SINTONIA_LINHA"] = "SOCIAL"
        self.assertEqual(mz.decisao("INSTAGRAM", "INCREMENTAL")["DECISAO"], mz.NAO_PERMITIDA)
        self.assertEqual(mz.decisao("LINKEDIN", "FETCH_POST")["DECISAO"], mz.NAO_PERMITIDA)

    def test_orcamento_livre_nao_passa_por_cima_do_robots(self):
        """O livro tem lugar, a linha e SOCIAL, o robots diz Disallow: a pagina NAO sai (so o robots foi lido)."""
        import scrap_http
        s = Servidor(robots="User-agent: *\nDisallow: /\n")
        try:
            os.environ["SINTONIA_LINHA"] = "SOCIAL"
            with self.assertRaises(scrap_http.RotaNaoPermitida):
                scrap_http.buscar_bytes(s.url("/p/reel"))
        finally:
            s.fechar()
        self.assertEqual([p["P"] for p in s.pedidos], ["/robots.txt"])


# ── 4b. a sonda APANHA o transporte que falha (defeitos plantados numa copia) ────────────────────────
class ASondaApanha(unittest.TestCase):
    """A linha CIENCIA medida numa COPIA com um defeito na porta: a sonda tem de dizer NAO LIGADA, e porque."""
    PORTA = "coleta/reserva_24h.py"
    RESERVA = ("    r = _CA.reservar_ou_esperar(host, run_id=run_id, linha=linha, crawl_delay_s=crawl_delay_s,\n"
               "                                espera_max_s=espera_max_s, url=url)\n")

    def copia(self, de, para):
        import shutil
        d = Path(tempfile.mkdtemp(prefix="sonda-copia-"))
        self.addCleanup(shutil.rmtree, d, True)
        shutil.copy(RAIZ / "_gavetas.py", d / "_gavetas.py")
        shutil.copytree(RAIZ / "coleta", d / "coleta", ignore=shutil.ignore_patterns("__pycache__"))
        (d / "regras").mkdir()
        shutil.copy(RAIZ / "regras" / "POLITICA-CORTESIA-ADAPTATIVA.json", d / "regras")
        (d / "ferramentas" / "big_collection").mkdir(parents=True)
        shutil.copy(RAIZ / "ferramentas" / "big_collection" / "sonda_ligacao_linhas.py", d / "ferramentas" / "big_collection")
        f = d / self.PORTA
        t = f.read_text(encoding="utf-8")
        self.assertEqual(t.count(de), 1, de)
        f.write_text(t.replace(de, para), encoding="utf-8")
        return d

    def medir(self, d):
        import coleta_continua as C
        return C.medir_ligacao(next(l for l in C.LINHAS if l["LINHA"] == "CIENCIA"), d)

    def test_a_copia_sem_defeito_esta_ligada(self):
        self.assertTrue(self.medir(self.copia("JANELA_S = 24 * 3600", "JANELA_S = 24 * 3600"))["LIGADA"])

    def test_pede_sem_reservar(self):
        m = self.medir(self.copia(self.RESERVA, '    r = {"ESTADO": "RESERVADO", "DOMINIO": host}\n'))
        self.assertFalse(m["LIGADA"], m)
        self.assertIn("0 reservas no livro", m["PORQUE"])

    def test_reserva_depois_do_pedido(self):
        m = self.medir(self.copia(self.RESERVA, "    _cedo = tuple(fazer())\n    fazer = lambda: _cedo\n" + self.RESERVA))
        self.assertFalse(m["LIGADA"], m)
        self.assertIn("antes da sua reserva", m["PORQUE"])

    def test_ignora_o_livro_pausado(self):
        m = self.medir(self.copia('    if r["ESTADO"] != "RESERVADO":\n        return r, None\n',
                                  '    if False:\n        return r, None\n'))
        self.assertFalse(m["LIGADA"], m)
        self.assertIn("B: o livro dizia PAUSADO", m["PORQUE"])

    def test_nao_regista_o_sinal(self):
        m = self.medir(self.copia("    _CA.registrar_resposta(host, int(st or 0), dict(cab or {}),",
                                  "    _CA.registrar_resposta(host, 200, {},"))
        self.assertFalse(m["LIGADA"], m)
        self.assertIn("S: o 429 nao foi obedecido", m["PORQUE"])


# ── 4c. o gemeo Node le as APIs como o Python ───────────────────────────────────────────────────────
class OGemeoNode(unittest.TestCase):
    def test_classe_das_apis_igual_nos_dois(self):
        doms = sorted(CA.politica()["CLASSES"]["API_COM_LIMITE_PUBLICADO"]["DOMINIOS"])
        js = ("import * as CA from %s; console.log(JSON.stringify(Object.fromEntries(%s.map(d => [d, CA.classeDe(d)]))));"
              % (json.dumps((RAIZ / "coleta" / "cortesia_adaptativa.mjs").as_uri()), json.dumps(doms)))
        env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}
        r = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, env=env, timeout=60)
        node = json.loads(r.stdout)
        for d in doms:
            self.assertEqual(node[d], list(CA.classe_de(d)), d)


# ── 4d. ligada ao contador nao inventa executor ─────────────────────────────────────────────────────
class LigadaSemOnda(unittest.TestCase):
    def test_busca_ligada_com_candidatas_nao_corre_a_onda_web(self):
        import coleta_continua as C
        with tempfile.TemporaryDirectory() as d:
            livro = Path(d) / "L.ndjson"
            livro.write_text("", encoding="utf-8")
            cands = {n: [] for n in ("SITES", "BUSCA", "CIENCIA", "SOCIAL", "PESQUISADORES")}
            cands["BUSCA"] = [{"SOURCE_ID": "IT-X-1", "DOMINIO": "x.test", "PREVISTOS": 1, "DOMINIOS": ["x.test"],
                               "RODADA_DO_PLANO": 1, "CLASSE_PRIORIDADE": None, "LINHA": "BUSCA"}]
            r = C.ciclo(Path(d) / "b", "sha", cands, pecas={"ram": lambda: 99.0}, livro_24h=livro, a_seco=True,
                        ligacao=lambda l: {"LIGADA": True, "PORQUE": "SONDA: t"})
        self.assertEqual(r["LINHAS"]["BUSCA"]["ESTADO"], "LIGADA_SEM_ONDA")
        self.assertEqual(r["LINHAS"]["BUSCA"]["FONTES"], [])
        self.assertIn("SEM ONDA NO CICLO", r["LINHAS"]["BUSCA"]["PORQUE"])
        self.assertEqual(r["ORCAMENTO_DO_CICLO"], {})


# ── 5. o portao de egresso REAL ─────────────────────────────────────────────────────────────────────
class PortaoReal(unittest.TestCase):
    def correr(self, rc, saida):
        import rodadas as R
        chamadas = []

        def falso(cmd, **k):
            chamadas.append(cmd)
            return subprocess.CompletedProcess(cmd, rc, stdout=json.dumps(saida), stderr="")
        real = R.subprocess.run
        R.subprocess.run = falso
        try:
            return R.portao_real(), chamadas
        finally:
            R.subprocess.run = real

    def test_rede_py_reprova_passa_e_falso(self):
        v, cmds = self.correr(3, {"EGRESS_COUNTRY_CODE": "US", "EGRESS_GATE": "FAIL"})
        self.assertIs(v["PASSA"], False)
        self.assertEqual((v["CODIGO"], v["PAIS"]), (3, "US"))

    def test_rede_py_aprova_passa_e_verdadeiro_e_pergunta_por_it(self):
        v, cmds = self.correr(0, {"EGRESS_COUNTRY_CODE": "IT", "EGRESS_GATE": "PASS"})
        self.assertIs(v["PASSA"], True)
        self.assertEqual(v["PAIS"], "IT")
        cmd = cmds[0]
        self.assertTrue(str(cmd[1]).replace("\\", "/").endswith("superficie/rede.py"), cmd)
        self.assertEqual(cmd[2:5], ["--portao-de-egresso", "IT", "--sem-cache"])

    def test_saida_ilegivel_com_codigo_de_falha_nao_passa(self):
        import rodadas as R
        real = R.subprocess.run
        R.subprocess.run = lambda cmd, **k: subprocess.CompletedProcess(cmd, 1, stdout="Traceback ...", stderr="")
        try:
            self.assertIs(R.portao_real()["PASSA"], False)
        finally:
            R.subprocess.run = real


if __name__ == "__main__":
    unittest.main()
