# -*- coding: utf-8 -*-
"""BUSCA-NO-ACTIONS (27/09) — a busca do Google pela API oficial no GitHub Actions. SEM REDE, SEM SEGREDO.

O Google e substituido por respostas no formato dos erros dele (fixtures abaixo). A chave de teste e uma cadeia
inventada; a prova e que ela NAO aparece em nenhum ficheiro nem em nenhuma saida.
"""
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "coleta"))
sys.path.insert(0, str(RAIZ / "ferramentas" / "linha_busca"))
import linha_busca as LB            # noqa: E402
import api_oficial as API           # noqa: E402
import pedido_actions as PA         # noqa: E402
import comentarios_piloto_d106 as CP  # noqa: E402

CHAVE = "CHAVE-FALSA-de-teste-0123456789abcdef"
CX = "0123456789abcdef0:cxdeteste"
WORKFLOW = RAIZ / ".github" / "workflows" / "linha-busca-google.yml"


def _erro(http, status, mensagem, razoes=(), detalhes=()):
    corpo = {"error": {"code": http, "status": status, "message": mensagem,
                       "errors": [{"reason": r, "message": mensagem} for r in razoes],
                       "details": [{"@type": "type.googleapis.com/google.rpc.ErrorInfo", "reason": r} for r in detalhes]}}
    return http, json.dumps(corpo).encode(), "HTTP %d" % http


API_DESLIGADA = _erro(403, "PERMISSION_DENIED",
                      "Custom Search API has not been used in project 123456 before or it is disabled. Enable it by "
                      "visiting https://console.developers.google.com/apis/api/customsearch.googleapis.com then retry.",
                      ["accessNotConfigured"], ["SERVICE_DISABLED"])
CHAVE_SO_YOUTUBE = _erro(403, "PERMISSION_DENIED",
                         "Requests to this API customsearch method google.customsearch.v1.CustomSearchService.List are blocked.",
                         ["forbidden"], ["API_KEY_SERVICE_BLOCKED"])
SEM_CX = _erro(400, "INVALID_ARGUMENT", "Request contains an invalid argument.", ["badRequest"])
CHAVE_INVALIDA = _erro(400, "INVALID_ARGUMENT", "API key not valid. Please pass a valid API key.", ["badRequest"],
                       ["API_KEY_INVALID"])
SEM_ACESSO = _erro(403, "PERMISSION_DENIED", "This project does not have the access to Custom Search JSON API.",
                   ["forbidden"])
QUOTA = _erro(429, "RESOURCE_EXHAUSTED", "Quota exceeded for quota metric 'Queries' and limit 'Queries per day'.",
              ["rateLimitExceeded"], ["RATE_LIMIT_EXCEEDED"])
OK = (200, json.dumps({"searchInformation": {"totalResults": "1234"},
                       "items": [{"link": "https://www.agrometeo.it/bollettino-vite.html"},
                                 {"link": "https://www.regione.veneto.it/peronospora"}]}).encode(), "")


class A_ATesoura(unittest.TestCase):
    def test_a_chave_sai_pelo_valor_e_pela_forma(self):
        env = {API.ENV_CHAVE: CHAVE, API.ENV_CX: CX}
        t = API.redigir("GET https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=vite falhou %s" % (CHAVE, CX, CHAVE), env)
        self.assertNotIn(CHAVE, t)
        self.assertNotIn(CX, t)
        self.assertIn("key=***", t)
        self.assertIn("q=vite", t)
        self.assertEqual(API.redigir("key=outra123&num=1", {}), "key=***&num=1")


class B_ODiagnostico(unittest.TestCase):
    def test_api_desligada_no_projeto(self):
        d = API.ler_diagnostico(*API_DESLIGADA, com_cx=False)
        self.assertEqual((d["API_ATIVA"], d["BUSCA_POSSIVEL"]), ("NAO", "NAO"))
        self.assertTrue(any("ativar a 'Custom Search API'" in p for p in API.o_que_o_dono_faz(d)))

    def test_chave_restrita_so_ao_youtube(self):
        d = API.ler_diagnostico(*CHAVE_SO_YOUTUBE, com_cx=False)
        self.assertEqual(d["CHAVE_PODE_USAR_A_API"], "NAO")
        self.assertIn("restricao de API", d["PORQUE"])
        self.assertTrue(any("acrescentar a 'Custom Search API'" in p for p in API.o_que_o_dono_faz(d)))

    def test_sem_cx_mede_que_o_cx_e_obrigatorio_e_que_a_api_esta_ligada(self):
        d = API.ler_diagnostico(*SEM_CX, com_cx=False)
        self.assertEqual((d["API_ATIVA"], d["CHAVE_PODE_USAR_A_API"], d["CX"]), ("SIM", "SIM", "OBRIGATORIO_E_AUSENTE"))
        self.assertIn("OBRIGATORIO (medido)", d["PORQUE"])
        self.assertTrue(any("GOOGLE_CSE_CX" in p for p in API.o_que_o_dono_faz(d)))

    def test_cx_dado_e_recusado(self):
        self.assertEqual(API.ler_diagnostico(*SEM_CX, com_cx=True)["CX"], "INVALIDO")

    def test_chave_invalida_nao_se_confunde_com_falta_de_cx(self):
        d = API.ler_diagnostico(*CHAVE_INVALIDA, com_cx=False)
        self.assertEqual(d["CHAVE_PODE_USAR_A_API"], "NAO")
        self.assertEqual(d["CX"], "AUSENTE")

    def test_projeto_sem_acesso_a_api(self):
        d = API.ler_diagnostico(*SEM_ACESSO, com_cx=True)
        self.assertEqual(d["CHAVE_PODE_USAR_A_API"], "NAO")
        self.assertTrue(any("Brave" in p for p in API.o_que_o_dono_faz(d)))

    def test_quota_esgotada_prova_que_a_api_esta_ligada(self):
        d = API.ler_diagnostico(*QUOTA, com_cx=True)
        self.assertEqual((d["API_ATIVA"], d["BUSCA_POSSIVEL"]), ("SIM", "NAO"))

    def test_200_e_a_busca_possivel_com_os_dominios(self):
        d = API.ler_diagnostico(*OK, com_cx=True)
        self.assertEqual((d["BUSCA_POSSIVEL"], d["CX"], d["RESULTADOS"]), ("SIM", "VALIDO", 2))
        self.assertEqual(d["DOMINIOS_DOS_RESULTADOS"], ["www.agrometeo.it", "www.regione.veneto.it"])
        self.assertEqual(API.o_que_o_dono_faz(d), ["Nada: a busca pode correr."])
        self.assertTrue(d["ESCOPO_INDICIO"].startswith("POUCOS_SITES: 2 dominio(s)"))
        muitos = json.dumps({"items": [{"link": "https://s%d.it/x" % i} for i in range(7)]}).encode()
        self.assertTrue(API.ler_diagnostico(200, muitos, "", com_cx=True)["ESCOPO_INDICIO"].startswith("MUITOS_SITES: 7"))

    def test_sem_rede_nada_se_prova(self):
        d = API.ler_diagnostico(0, b"", "URLError: timed out", com_cx=True)
        self.assertEqual((d["API_ATIVA"], d["BUSCA_POSSIVEL"]), ("NAO_SEI", "NAO"))


class C_UmaChamadaSo(unittest.TestCase):
    def test_sem_chave_nenhuma_chamada_sai(self):
        pedidos = []
        d = API.diagnosticar_cse(lambda u, c=None: pedidos.append(u), env={})
        self.assertEqual((pedidos, d["CHAMADAS"]), ([], 0))
        self.assertTrue(d["O_QUE_O_DONO_FAZ"])

    def test_sem_cx_o_pedido_vai_sem_cx_e_e_um_so(self):
        pedidos = []

        def pedir(u, c=None):
            pedidos.append(u)
            return SEM_CX
        d = API.diagnosticar_cse(pedir, env={API.ENV_CHAVE: CHAVE})
        self.assertEqual(len(pedidos), 1)
        self.assertNotIn("cx=", pedidos[0])
        self.assertIn("num=10", pedidos[0])
        self.assertNotIn(CHAVE, json.dumps(d))

    def test_com_cx_e_uma_busca_de_um_resultado(self):
        pedidos = []
        API.diagnosticar_cse(lambda u, c=None: pedidos.append(u) or OK, env={API.ENV_CHAVE: CHAVE, API.ENV_CX: CX})
        self.assertEqual(len(pedidos), 1)
        self.assertIn("num=10", pedidos[0])
        self.assertIn("cx=", pedidos[0])

    def test_o_transporte_levanta_sem_a_chave_na_mensagem(self):
        with mock.patch.dict(os.environ, {API.ENV_CHAVE: CHAVE}):
            buscar = API.transporte(lambda u, c=None: CHAVE_SO_YOUTUBE)
            with self.assertRaises(API.ErroDaApi) as e:
                buscar("https://www.googleapis.com/customsearch/v1?key=%s&q=x" % CHAVE)
        self.assertNotIn(CHAVE, str(e.exception))
        self.assertIn("API_KEY_SERVICE_BLOCKED", str(e.exception))

    def test_juncao_lote5_o_erro_da_busca_sai_sem_a_chave(self):
        # LOTE5-INTEGRA (mutante J1-c): a tesoura mora em linha_busca.buscar_consultas, no ponto onde
        # busca-no-actions encontra a linha-busca. Um transporte que levanta com o endereco (e a chave) na
        # mensagem nao pode deixar a chave no RESULTADOS.json.
        def cai(u, c=None):
            raise RuntimeError("falhou GET %s" % u)
        d = Path(tempfile.mkdtemp())
        try:
            with mock.patch.dict(os.environ, {API.ENV_CHAVE: CHAVE, API.ENV_CX: CX}):
                rs = LB.buscar_consultas("GOOGLE_CSE", [{"CONSULTA_ID": "Q1", "CONSULTA": "vite peronospora"}],
                                         cai, d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertEqual(1, len(rs))
        self.assertIn("RuntimeError", rs[0]["ERRO"])
        self.assertNotIn(CHAVE, json.dumps(rs))
        self.assertNotIn(CX, json.dumps(rs))


class D_OComandoDaLinha(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="busca-actions-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.enterContext(mock.patch.dict(os.environ, {API.ENV_CHAVE: CHAVE, API.ENV_CX: CX}))
        self.enterContext(mock.patch.object(LB, "portao_it", side_effect=AssertionError("o portao IT foi chamado")))
        self.enterContext(mock.patch.object(LB, "transporte_real",
                                            side_effect=AssertionError("a API saiu pelo transporte das paginas")))
        self.pedidos = []

    def _main(self, *args, resposta=OK):
        def pedir(u, c=None):
            self.pedidos.append(u)
            return resposta
        with mock.patch.object(API, "pedir", pedir), redirect_stdout(io.StringIO()) as out:
            rc = LB.main(["linha_busca.py", *args, "--saida=%s" % self.tmp])
        return rc, out.getvalue()

    def _sem_chave_em_lado_nenhum(self, texto=""):
        self.assertNotIn(CHAVE, texto)
        for f in self.tmp.rglob("*"):
            if f.is_file():
                self.assertNotIn(CHAVE.encode(), f.read_bytes(), f)

    def test_buscar_sem_portao_pela_api_e_com_teto_n(self):
        rc, out = self._main("--buscar", "--autorizado", "--sem-portao-it", "--motor=GOOGLE_CSE",
                             "--consultas=%s" % (RAIZ / "data" / "derivados" / "LINHA-BUSCA" / "CONSULTAS.json"), "--n=3")
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(self.pedidos), 3)
        rs = json.loads((self.tmp / "RESULTADOS.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rs), 6)
        self.assertTrue(all(r["ROTA_DO_MOTOR"] == "API_OFICIAL" for r in rs))
        self._sem_chave_em_lado_nenhum(out)

    def test_erro_da_api_fica_redigido_no_resultados(self):
        rc, out = self._main("--buscar", "--autorizado", "--sem-portao-it", "--motor=GOOGLE_CSE",
                             "--consultas=%s" % (RAIZ / "data" / "derivados" / "LINHA-BUSCA" / "CONSULTAS.json"), "--n=1",
                             resposta=CHAVE_SO_YOUTUBE)
        rs = json.loads((self.tmp / "RESULTADOS.json").read_text(encoding="utf-8"))
        self.assertIn("API_KEY_SERVICE_BLOCKED", rs[0]["ERRO"])
        self._sem_chave_em_lado_nenhum(out)

    def test_n_fora_da_quota_e_recusado_sem_pedido(self):
        rc, _ = self._main("--buscar", "--autorizado", "--sem-portao-it", "--motor=GOOGLE_CSE",
                           "--consultas=%s" % (RAIZ / "data" / "derivados" / "LINHA-BUSCA" / "CONSULTAS.json"), "--n=101")
        self.assertEqual((rc, self.pedidos), (2, []))

    def test_sem_portao_nunca_serve_paginas_nem_motor_html(self):
        self.assertEqual(self._main("--colher", "--autorizado", "--sem-portao-it", "--resultados=x", "--fila=y")[0], 2)
        self.assertEqual(self._main("--buscar", "--autorizado", "--sem-portao-it", "--motor=DDG_HTML",
                                    "--consultas=x")[0], 2)
        self.assertEqual(self._main("--medir-motores", "--autorizado", "--sem-portao-it")[0], 2)
        self.assertEqual(self.pedidos, [])

    def test_diagnostico_grava_e_diz_pelo_codigo_se_da(self):
        rc, out = self._main("--diagnosticar-cse", "--autorizado", "--sem-portao-it", resposta=API_DESLIGADA)
        self.assertEqual(rc, 4)
        d = json.loads((self.tmp / "DIAGNOSTICO.json").read_text(encoding="utf-8"))
        self.assertEqual(d["API_ATIVA"], "NAO")
        self.assertIn("DONO 1:", out)
        self._sem_chave_em_lado_nenhum(out)
        rc, _ = self._main("--diagnosticar-cse", "--autorizado", "--sem-portao-it", resposta=OK)
        self.assertEqual(rc, 0)

    def test_sem_autorizado_nada(self):
        self.assertEqual(self._main("--diagnosticar-cse", "--sem-portao-it")[0], 2)
        self.assertEqual(self.pedidos, [])


class E_OPedidoDoWorkflow(unittest.TestCase):
    def _f(self, d):
        p = Path(tempfile.mkdtemp(prefix="pedido-")) / "P.json"
        self.addCleanup(shutil.rmtree, p.parent, True)
        p.write_text(json.dumps(d), encoding="utf-8")
        return p

    def test_o_ficheiro_do_repositorio_pede_diagnostico_e_comentarios_sem_cx(self):
        p = PA.ler_pedido()
        self.assertEqual((p["SO_DIAGNOSTICO"], p["COMENTARIOS"], p["CX"]), (True, True, ""))

    def test_n_so_de_1_a_100(self):
        for n in (0, 101, "muitos"):
            with self.assertRaises(PA.PedidoInvalido):
                PA.ler_pedido(self._f({"N": n}))
        self.assertEqual(PA.ler_pedido(self._f({"N": 100}))["N"], 100)

    def test_cx_so_na_forma_de_um_id(self):
        self.assertEqual(PA.ler_pedido(self._f({"CX": "0123456789abcdef0:abc_d-e"}))["CX"], "0123456789abcdef0:abc_d-e")
        for mau in ("x; rm -rf /", "a b", "${{ secrets.SUPABASE_SECRET_KEY }}", "x" * 65):
            with self.assertRaises(PA.PedidoInvalido, msg=mau):
                PA.ler_pedido(self._f({"CX": mau}))

    def test_as_saidas(self):
        s = PA.saidas(PA.ler_pedido(self._f({"N": 10, "SO_DIAGNOSTICO": False, "COMENTARIOS": "false", "CX": "abc:1"})))
        self.assertEqual(s, "n=10\nso_diagnostico=false\ncomentarios=false\ncx=abc:1\n")


class F_OWorkflow(unittest.TestCase):
    def setUp(self):
        self.y = WORKFLOW.read_text(encoding="utf-8")
        self.corpo = self.y.split("\non:")[1]                         # sem o cabecalho de comentarios

    def test_so_o_secret_do_youtube_e_escrito_fixo(self):
        self.assertEqual(sorted(set(re.findall(r"secrets\.([A-Z0-9_]+)", self.corpo))), ["YOUTUBE_DATA_API_KEY"])
        self.assertNotIn("secrets[", self.corpo)                       # pelo nome = TODOS os secrets no runner
        self.assertNotIn("SUPABASE", self.corpo)
        for linha in self.corpo.splitlines():
            if "secrets." in linha:
                self.assertRegex(linha.strip(), r"^(SINTONIA_GOOGLE_CSE_KEY|YOUTUBE_DATA_API_KEY): "
                                                r"\$\{\{ secrets\.YOUTUBE_DATA_API_KEY \}\}$")

    def test_a_chave_so_nos_passos_2_3_e_4(self):
        passos = re.split(r"\n      - ", self.corpo)
        com_segredo = [p.splitlines()[0] for p in passos if "secrets." in p]
        self.assertEqual([c.split(" · ")[0] for c in com_segredo], ["name: 2", "name: 3", "name: 4"], com_segredo)

    def test_dispara_so_por_push_no_proprio_ramo_e_nos_proprios_ficheiros(self):
        self.assertIn("  push:\n    branches: [busca-no-actions-v1]\n", self.corpo)
        self.assertIn("- '.github/workflows/linha-busca-google.yml'", self.corpo)
        self.assertIn("- 'ferramentas/linha_busca/PEDIDO-BUSCA-GOOGLE.json'", self.corpo)
        self.assertNotIn("workflow_dispatch", self.corpo)
        self.assertNotIn("pull_request", self.corpo)

    def test_sem_commit_so_leitura_so_artifact(self):
        self.assertIn("permissions:\n  contents: read", self.corpo)
        self.assertNotRegex(self.corpo, r"git (commit|push)|contents: write")
        self.assertRegex(self.corpo, r"if: always\(\)\n        uses: actions/upload-artifact@v4")
        self.assertIn("runs-on: ubuntu-latest", self.corpo)
        self.assertNotRegex(self.corpo.lower(), r"self-hosted|vpn\s*:|wireguard|openvpn")
        self.assertNotIn("--colher", self.corpo)

    def test_diagnostico_e_comentarios_na_mesma_corrida(self):
        self.assertIn("--diagnosticar-cse --autorizado --sem-portao-it", self.corpo)
        self.assertIn("ferramentas/linha_busca/comentarios_piloto_d106.py --saida=saida", self.corpo)

    def test_nenhum_input_nem_evento_entra_direto_num_run(self):
        corpo_dos_run = re.findall(r"run: (?:>-|\|)?\n?((?:\s{10,}.*\n?)+|.*)", self.corpo)
        self.assertEqual(len(corpo_dos_run), 7)          # passos 0,1,2,3,4,5,7 (o 6 e `uses`)
        self.assertFalse([r for r in corpo_dos_run if "${{" in r])

    def test_o_yaml_e_valido_quando_ha_leitor(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML ausente neste Python")
        w = yaml.safe_load(self.y)
        passos = w["jobs"]["buscar"]["steps"]
        self.assertEqual(passos[-1]["if"], "steps.coment.outcome == 'failure'")
        self.assertTrue(passos[4]["continue-on-error"] and passos[6]["continue-on-error"])
        self.assertEqual(w[True]["push"]["branches"], ["busca-no-actions-v1"])   # «on» vira True no YAML 1.1


class G_OPilotoDeComentarios(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="coment-d106-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.pedidos = []

    def _pedir(self, respostas):
        def pedir(url, cab=None):
            self.pedidos.append(url)
            v = re.search(r"videoId=([^&]+)", url).group(1)
            return respostas(v, url)
        return pedir

    def test_os_10_pais_do_12_e_as_duas_ordens(self):
        self.assertEqual(CP.VIDEOS, ("soP-t7nvvq8", "F5uLnId6fJk", "w87w51fSWAw", "QGE7h4gztQ8", "R5FJWJkCbKI",
                                     "5MNenAiGtlQ", "QmeVN7SNnMU", "2cF0yHZXiMs", "ioLYGSazexk", "ezRyN8vLVvc"))
        self.assertEqual((CP.ORDENS, CP.TETO_CHAMADAS), (("relevance", "time"), 20))

    def test_vinte_chamadas_cruas_com_sha256_e_sem_a_chave(self):
        corpo = json.dumps({"pageInfo": {"totalResults": 3}, "nextPageToken": "X",
                            "items": [{"snippet": {}, "replies": {"comments": [{}]}}] * 3}).encode()
        vazio = json.dumps({"pageInfo": {"totalResults": 0}, "items": []}).encode()
        doc = CP.colher(self.tmp, CHAVE, self._pedir(lambda v, u: (200, vazio if v in ("2cF0yHZXiMs", "ioLYGSazexk")
                                                                         else corpo, "")))
        self.assertEqual(len(self.pedidos), 20)
        self.assertTrue(all("maxResults=100" in u and "part=snippet%2Creplies" in u for u in self.pedidos))
        self.assertEqual(sum("order=relevance" in u for u in self.pedidos), 10)
        self.assertEqual((doc["COM_200"], doc["ITENS_TOTAL"], len(doc["VIDEOS_COM_COMENTARIO"])), (20, 48, 8))
        r0 = doc["RESPOSTAS"][0]
        self.assertEqual(r0["SHA256"], __import__("hashlib").sha256((self.tmp / r0["FICHEIRO"]).read_bytes()).hexdigest())
        self.assertEqual((r0["HA_MAIS_PAGINAS"], r0["RESPOSTAS_NOS_ITENS"]), (True, 3))   # nao se segue a pagina
        self.assertNotIn(CHAVE, json.dumps(doc))
        self.assertTrue(all("key=" not in r["PEDIDO_SEM_CHAVE"] for r in doc["RESPOSTAS"]))

    def test_comentarios_desligados_num_video_nao_param_os_outros(self):
        desl = json.dumps({"error": {"code": 403, "errors": [{"reason": "commentsDisabled"}],
                                     "message": "The video identified by the videoId parameter has disabled comments."}}).encode()
        doc = CP.colher(self.tmp, CHAVE, self._pedir(lambda v, u: (403, desl, "HTTP 403") if v == "soP-t7nvvq8"
                                                     else (200, b'{"items": []}', "")))
        self.assertEqual(len(self.pedidos), 20)
        self.assertEqual(doc["RESPOSTAS"][0]["ERRO_RAZOES"], ["commentsDisabled"])
        self.assertIsNone(doc["PAROU"])

    def test_erro_da_chave_para_tudo_logo_na_primeira(self):
        quota = json.dumps({"error": {"code": 403, "errors": [{"reason": "quotaExceeded"}],
                                      "message": "quota key=%s" % CHAVE}}).encode()
        doc = CP.colher(self.tmp, CHAVE, self._pedir(lambda v, u: (403, quota, "HTTP 403")))
        self.assertEqual(len(self.pedidos), 1)
        self.assertIn("quotaExceeded", doc["PAROU"])
        self.assertEqual(sum(1 for r in doc["RESPOSTAS"] if r.get("NAO_PEDIDO")), 19)
        self.assertNotIn(CHAVE, json.dumps(doc))

    def test_sem_chave_nenhuma_chamada(self):
        doc = CP.colher(self.tmp, None, self._pedir(lambda v, u: (200, b"{}", "")))
        self.assertEqual((self.pedidos, doc["CHAMADAS"]), ([], 0))
        self.assertIn("nenhuma chamada saiu", doc["PAROU"])

    def test_main_grava_o_manifesto_sem_a_chave_e_sai_4_sem_200(self):
        with mock.patch.dict(os.environ, {"YOUTUBE_DATA_API_KEY": CHAVE}), \
             mock.patch.object(CP.API, "pedir", lambda u, c=None: (400, json.dumps(
                 {"error": {"errors": [{"reason": "keyInvalid"}], "message": "bad %s" % CHAVE}}).encode(), "HTTP 400")), \
             redirect_stdout(io.StringIO()) as out:
            rc = CP.main(["--saida=%s" % self.tmp])
        self.assertEqual(rc, 4)
        m = (self.tmp / "COMENTARIOS-PILOTO-D106.json").read_text(encoding="utf-8")
        self.assertNotIn(CHAVE, m + out.getvalue())
        self.assertIn("keyInvalid", m)


if __name__ == "__main__":
    unittest.main()
