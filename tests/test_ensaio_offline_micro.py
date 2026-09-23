"""O ensaio offline da micro-coleta — as pecas que decidem se o ensaio e honesto.

Sem rede externa, sem Postgres: o servidor de bytes sobe em 127.0.0.1 e o
`curl` e chamado com o `_curlrc` do proprio ensaio. O caminho inteiro (com base
descartavel) corre no proprio `ensaio_offline.py`, nao aqui.
"""
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)


class TestChaveEMapa(unittest.TestCase):

    def test_chave_ignora_esquema_e_porto_e_guarda_a_query(self):
        self.assertEqual(E.chave("https://WWW.x.it:443/a/b?c=1"), "www.x.it/a/b?c=1")
        self.assertEqual(E.chave("http://www.x.it"), "www.x.it/")

    def test_mapa_le_manifesto_e_livro_e_nao_serve_o_que_nao_foi_200(self):
        t = Path(tempfile.mkdtemp())
        (t / "gab" / "bytes").mkdir(parents=True)
        (t / "gab" / "bytes" / "a.html").write_text("<p>a</p>", encoding="utf-8")
        (t / "gab" / "bytes" / "b.html").write_text("<p>b</p>", encoding="utf-8")
        (t / "gab" / "MANIFESTO.json").write_text(json.dumps({"PAGINAS": [
            {"SOURCE_ID": "S1", "URL": "https://x.it/a", "HTTP": 200, "FICHEIRO": "bytes\\a.html"},
            {"SOURCE_ID": "S1", "URL": "https://x.it/b", "HTTP": 403, "FICHEIRO": "bytes\\b.html"}]}),
            encoding="utf-8")
        led = t / "lote" / "data" / "collection-ledger" / "italy"
        led.mkdir(parents=True)
        (t / "lote" / "store").mkdir()
        (t / "lote" / "store" / "m.html").write_text("<p>m</p>", encoding="utf-8")
        (led / "observations.ndjson").write_text(json.dumps(
            {"SOURCE_ID": "S2", "SOURCE_URL": "https://y.it/m", "RAW_PATH": "store/m.html",
             "CONTENT_TYPE": "text/html"}) + "\n", encoding="utf-8")
        m = E.mapa_de_fixtures([t / "gab"], [t / "lote"])
        self.assertEqual(sorted(m), ["x.it/a", "y.it/m"])


class TestServidorECurl(unittest.TestCase):
    """O servidor responde pelo host original e regista TODO pedido."""

    @classmethod
    def setUpClass(cls):
        if not shutil.which("curl") or not shutil.which("openssl"):
            raise unittest.SkipTest("curl/openssl ausentes")
        cls.t = Path(tempfile.mkdtemp())
        (cls.t / "p.html").write_text("<h1>materia</h1>", encoding="utf-8")
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-subj",
                        "/CN=fixture", "-keyout", str(cls.t / "k.pem"), "-out", str(cls.t / "c.pem"),
                        "-days", "1"], check=True, capture_output=True)
        cls.srv = E.Servidor({"www.sito-di-prova.it/news/uno": {"FICHEIRO": str(cls.t / "p.html"),
                                                                "SOURCE_ID": "S", "PAPEL": "MATERIA"}})
        cls.ph, cls.ps = E.porto_livre(), E.porto_livre()
        cls.srv.subir(cls.ph, cls.ps, cls.t / "c.pem", cls.t / "k.pem")

    @classmethod
    def tearDownClass(cls):
        cls.srv.descer()

    def _curl(self, rc, url):
        d = self.t / ("curl-%d" % len(list(self.t.glob("curl-*"))))
        d.mkdir()
        (d / "_curlrc").write_text(rc, encoding="ascii")
        (d / ".curlrc").write_text(rc, encoding="ascii")
        import os
        env = {**os.environ, "CURL_HOME": str(d)}
        return subprocess.run(["curl", "-sS", "-m", "5", "-o", "-", "-w", "\n%{http_code}", url],
                              capture_output=True, text=True, env=env)

    def _rc(self, aspas=True):
        q = '"' if aspas else ""
        return (f"connect-to = {q}:443:127.0.0.1:{self.ps}{q}\n"
                f"connect-to = {q}:80:127.0.0.1:{self.ph}{q}\ninsecure\n")

    def test_https_com_host_original_serve_os_bytes(self):
        r = self._curl(self._rc(), "https://www.sito-di-prova.it/news/uno")
        self.assertTrue(r.stdout.endswith("200"), r.stdout + r.stderr)
        self.assertIn("materia", r.stdout)

    def test_o_que_nao_foi_gravado_da_404_e_fica_registado(self):
        n = len(self.srv.registo)
        r = self._curl(self._rc(), "http://outro.example/x")
        self.assertTrue(r.stdout.endswith("404"), r.stdout + r.stderr)
        self.assertEqual(self.srv.registo[n]["ESTADO"], 404)
        self.assertEqual(self.srv.registo[n]["HOST"], "outro.example")

    def test_sem_aspas_o_curlrc_e_ignorado(self):
        """A armadilha medida: sem aspas o connect-to nao vale e o curl iria a rede.
        Usa-se um nome .invalid: sem o redirecionamento, falha a resolver — nada sai."""
        n = len(self.srv.registo)
        r = self._curl(self._rc(aspas=False), "https://nao-existe.invalid/x")
        self.assertIn("resolve", r.stderr.lower())
        self.assertEqual(len(self.srv.registo), n)


class TestRegistoDeFalha(unittest.TestCase):
    """Todo raw fica em .../OBSERVATION/; o que separa falha de documento e o conteudo."""

    def test_json_do_coletor_com_falha_e_registo_de_falha(self):
        t = Path(tempfile.mkdtemp())
        (t / "f.json").write_text(json.dumps({"HEALTH_STATE": "FAILED", "SHA256": "",
                                              "OBSERVATION_RESULT": "TRANSPORT_OR_EMPTY"}), encoding="utf-8")
        self.assertTrue(E.e_registo_de_falha(t, "f.json", "application/json"))

    def test_json_de_uma_fonte_de_api_e_documento(self):
        t = Path(tempfile.mkdtemp())
        (t / "d.json").write_text(json.dumps({"dados": [1, 2, 3]}), encoding="utf-8")
        self.assertFalse(E.e_registo_de_falha(t, "d.json", "application/json"))

    def test_html_nunca_e_registo_de_falha(self):
        t = Path(tempfile.mkdtemp())
        (t / "p.html").write_text('{"HEALTH_STATE": "FAILED"}', encoding="utf-8")
        self.assertFalse(E.e_registo_de_falha(t, "p.html", "text/html"))


class TestCampos(unittest.TestCase):
    """Os 15 campos do mandato: valor, peca e rota — sem falha de ensaio contada como proveniencia."""

    def _campos(self, cad):
        corridas = [{"SOURCE_ID": "S", "RUN_ID": "R1", "CODIGO": 0}]
        rel = {"CRITERIOS": {
            "C4_PROVENIENCIA_COMPLETA": {"OBSERVACOES": 3, "COM_DECISAO": 1, "SALA_LINHAS": 1,
                                         "SALA_COM_CADEIA_INTEIRA": 1},
            "C7_PROPORCAO_POR_FONTE_E_CLASSE": {"POR_FONTE": {"S": {"SIM": 1, "SEM_DERIVADO": 2}}},
            "C2_MATERIA_NAO_CAPA": {"CAPAS_DO_JUIZ": []}}}
        antes = {"sala_de_espera": 5, "raw_asset": 10, "derived_artifact": 4}
        depois = {"sala_de_espera": 6, "raw_asset": 13, "derived_artifact": 5}
        runs = [{"RUN_ID": "R1", "contadores": {"HEALTHY": 0, "FAILED": 1, "DETAIL_NEW": 3,
                                                "DETAIL_REQUESTS": 3, "UNNECESSARY_REFETCHES": 0}}]
        return E.campos(corridas, rel, antes, depois, runs, [], [{"HOST": "a"}] * 5,
                        {"EGRESSO": 0}, cad)

    def test_os_quinze_campos_do_mandato_estao_todos(self):
        c = self._campos({"RAW_DOCUMENTOS": 1, "RAW_REGISTOS_DE_FALHA": 2, "DOCUMENTOS_SEM_DERIVADO": []})
        mandato = {"SOURCES_ATTEMPTED", "SOURCES_SUCCESS", "DETAIL_DOCUMENTS", "LISTINGS_REJECTED",
                   "RAW_CREATED", "DERIVED_CREATED", "ADMISSION_SIM", "ADMISSION_NAO",
                   "ADMISSION_NAO_SEI", "SALA_DELTA", "UNNECESSARY_REFETCHES",
                   "FALSE_DOCUMENT_CHANGED", "PROVENANCE_FAILURES", "NETWORK_REQUESTS", "PAID_USD"}
        self.assertTrue(mandato <= set(c), mandato - set(c))
        for k, v in c.items():
            self.assertIn("ROTA", v, k)

    def test_registo_de_falha_nao_e_raw_nem_falha_de_proveniencia(self):
        c = self._campos({"RAW_DOCUMENTOS": 1, "RAW_REGISTOS_DE_FALHA": 2, "DOCUMENTOS_SEM_DERIVADO": []})
        self.assertEqual(c["RAW_CREATED"]["VALOR"], 1)
        self.assertEqual(c["RAW_CREATED"]["RAW_LINHAS_TOTAL"], 3)
        self.assertEqual(c["PROVENANCE_FAILURES"]["VALOR"], 0)

    def test_documento_sem_derivado_e_falha_de_proveniencia(self):
        c = self._campos({"RAW_DOCUMENTOS": 2, "RAW_REGISTOS_DE_FALHA": 1, "DOCUMENTOS_SEM_DERIVADO": [77]})
        self.assertEqual(c["PROVENANCE_FAILURES"]["VALOR"], 1)

    def test_sucesso_e_a_saude_do_coletor_nao_o_codigo_de_saida(self):
        c = self._campos({})
        self.assertEqual(c["SOURCES_SUCCESS"]["VALOR"], 0)
        self.assertEqual(c["SOURCES_SUCCESS"]["PROCESSO_RC0"], 1)

    def test_sala_delta_e_listagens_sem_dono(self):
        c = self._campos({})
        self.assertEqual(c["SALA_DELTA"]["VALOR"], 1)
        self.assertEqual(c["LISTINGS_REJECTED"]["ROTA"], "MISSING_ROUTE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
