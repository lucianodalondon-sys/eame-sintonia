# -*- coding: utf-8 -*-
"""A CORTESIA ADAPTATIVA (D124): o teto por dominio sobe sem sinal, recua no sinal, pausa, alerta.

    py -m unittest tests.test_cortesia_adaptativa

Sem rede. O livro vive numa pasta temporaria; o tempo entra por `agora=` (os dias passam sem esperar).
A corrida concorrente e entre PROCESSOS reais (multiprocessing e node). O ensaio do transporte contra um
servidor local que responde 200/429/503/Retry-After/desafio e `provas/contador_24h_local.mjs`, chamado por
`tests/test_contador_24h.py`.
"""
import json
import multiprocessing as mp
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "provas"))
from coleta import cortesia_adaptativa as CA  # noqa: E402

T0 = 1_800_000_000.0
DIA = 86400.0


def _corredor(args):
    livro, i = args
    os.environ["SINTONIA_CORTESIA_LIVRO"] = livro
    sys.path.insert(0, str(RAIZ))
    from coleta import cortesia_adaptativa as C                    # noqa: E402
    return C.reservar("www.cia.it", run_id="P%d" % i, linha="L%d" % (i % 3))["ESTADO"]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ca-"))
        self.livro = self.tmp / "LIVRO-CORTESIA.ndjson"
        self._env = {k: os.environ.pop(k, None) for k in ("SINTONIA_CORTESIA_LIVRO", "SINTONIA_TETO_24H",
                                                          "SINTONIA_CORTESIA_ALERTAS", "SINTONIA_TETO_POR_HOST")}
        os.environ["SINTONIA_CORTESIA_LIVRO"] = str(self.livro)

    def tearDown(self):
        for k, v in self._env.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def pedir(self, host="cia.it", t=T0, status=200, headers=None, run="r", **kw):
        """Um pedido inteiro: reserva e resposta. Devolve a reserva."""
        r = CA.reservar(host, run_id=run, linha="SITES", agora=t)
        if r["ESTADO"] == "RESERVADO":
            CA.registrar_resposta(host, status, headers, run_id=run, linha="SITES", agora=t + 1, **kw)
        return r

    def dia_cheio(self, host, t, n, passo=10):
        for k in range(n):
            self.assertEqual(self.pedir(host, t + k * passo)["ESTADO"], "RESERVADO", k)

    def est(self, host="cia.it", t=T0):
        return CA.estado_do_dominio(host, t)


class APolitica(Base):
    def test_classes_e_numeros_iniciais_vem_da_politica(self):
        self.assertEqual((self.est("www.cia.it")["CLASSE"], self.est("cia.it")["ORCAMENTO_24H"]), ("SITE", 40))
        self.assertEqual(self.est("www.youtube.com")["CLASSE"], "PLATAFORMA_GRANDE")
        self.assertEqual(self.est("r1.googlevideo.com")["DOMINIO"], "youtube.com")          # D41
        self.assertEqual(self.est("pub.orcid.org")["CLASSE"], "API_COM_LIMITE_PUBLICADO")
        self.assertEqual(self.est("api.openalex.org")["ORCAMENTO_24H"], 100000)
        self.assertEqual(self.est("cia.it")["PAUSA_MINIMA_S"], 5)

    def test_as_apis_citam_a_pagina_e_dizem_que_nao_foi_conferida(self):
        api = CA.politica()["CLASSES"]["API_COM_LIMITE_PUBLICADO"]
        self.assertIn("NAO_CONFERIDO", api["ESTADO_DA_CITACAO"])
        for d, a in api["DOMINIOS"].items():
            self.assertTrue(a["CITA"].startswith("https://"), d)

    def test_o_5_fixo_saiu_dos_sitios_medidos(self):
        """D124: nenhum dos sitios que o coordenador mediu com o 5 fixo continua com ele."""
        fixos = {"coleta/dominio_registavel.py": r"^TETO_D38\s*=\s*5",
                 "coleta/reserva_24h.py": r"_PT\.TETO_D38",
                 "coleta/italy_pilot_collect.mjs": r"TETO_POR_HOST:\s*5",
                 "ferramentas/big_collection/onda_web.py": r"^TETO\s*=\s*5",
                 "ferramentas/big_collection/rodadas.py": r"PT\.TETO_D38",
                 "provas/prova_teto_dominio.py": r"import \(TETO_D38|=TETO_D38",
                 "ferramentas/maestro_social/maestro_social.py": r"^TETO\s*=\s*5",
                 "coleta/pesquisadores_t6.py": r"^TETO_POR_DOMINIO\s*=\s*5",
                 "coleta/teto_da_onda.py": r"^TETO_POR_OMISSAO\s*=\s*5",
                 "curadoria/plano_onda_social.py": r"^TETO_D38\s*=\s*5"}
        for f, rx in fixos.items():
            self.assertIsNone(re.search(rx, (RAIZ / f).read_text(encoding="utf-8"), re.M), f)

    def test_todos_perguntam_a_politica(self):
        for f in ("coleta/reserva_24h.py", "coleta/teto_da_onda.py", "ferramentas/big_collection/onda_web.py",
                  "ferramentas/big_collection/rodadas.py", "provas/prova_teto_dominio.py", "coleta/pesquisadores_t6.py",
                  "curadoria/plano_onda_social.py"):
            self.assertIn("cortesia_adaptativa", (RAIZ / f).read_text(encoding="utf-8"), f)
        self.assertIn("./cortesia_adaptativa.mjs", (RAIZ / "coleta/italy_pilot_collect.mjs").read_text(encoding="utf-8"))


class OrcamentoSobe(Base):
    def test_janela_limpa_e_usada_dobra(self):
        self.dia_cheio("cia.it", T0, 20)                            # metade de 40, sem sinal
        self.assertEqual(self.est(t=T0 + DIA + 5)["ORCAMENTO_24H"], 80)
        self.assertEqual(CA.orcamento_do_dominio("cia.it", T0 + DIA + 300), 80)

    def test_janela_pouco_usada_nao_dobra(self):
        self.dia_cheio("cia.it", T0, 19)                            # menos de metade: nao provou nada
        self.assertEqual(self.est(t=T0 + DIA + 5)["ORCAMENTO_24H"], 40)

    def test_dias_parados_nao_dobram(self):
        self.dia_cheio("cia.it", T0, 1)
        self.assertEqual(self.est(t=T0 + 30 * DIA)["ORCAMENTO_24H"], 40)

    def test_para_no_teto_de_seguranca(self):
        t, nivel = T0, 40
        for _ in range(6):
            self.dia_cheio("cia.it", t, nivel, passo=6)
            t += DIA
            nivel = self.est(t=t)["ORCAMENTO_24H"]
        self.assertEqual(nivel, 640)
        self.assertEqual(self.est(t=t)["SITUACAO"], "NO_TETO_DE_SEGURANCA")

    def test_api_nao_dobra(self):
        self.dia_cheio("api.openalex.org", T0, 3, passo=2)
        self.assertEqual(self.est("api.openalex.org", T0 + 2 * DIA)["ORCAMENTO_24H"], 100000)


class RecuaNoSinal(Base):
    def test_429_corta_para_metade_e_cumpre_retry_after(self):
        self.pedir(t=T0)
        r = CA.reservar("cia.it", run_id="x", linha="SITES", agora=T0 + 10)
        x = CA.registrar_resposta("cia.it", 429, {"Retry-After": "120"}, run_id="x", linha="SITES", agora=T0 + 11)
        self.assertEqual(r["ESTADO"], "RESERVADO")
        self.assertEqual(x["SINAIS"], ["HTTP_429", "RETRY_AFTER"])
        self.assertEqual(x["DEPOIS"]["ORCAMENTO_24H"], 20)
        a = CA.reservar("cia.it", run_id="y", linha="SITES", agora=T0 + 100)
        self.assertEqual((a["ESTADO"], a["MOTIVO"], a["ATE"]), ("ADIADO_ATE", "RETRY_AFTER", T0 + 131))
        self.assertEqual(CA.reservar("cia.it", run_id="y", linha="SITES", agora=T0 + 132)["ESTADO"], "RESERVADO")

    def test_retry_after_em_data_http(self):
        from email.utils import formatdate
        x = CA.registrar_resposta("cia.it", 503, {"retry-after": formatdate(T0 + 600, usegmt=True)},
                                  run_id="x", linha="S", agora=T0)
        self.assertEqual(x["RETRY_AFTER_S"], 600)
        self.assertIn("HTTP_503", x["SINAIS"])

    def test_dois_sinais_em_24h_pausam_24h(self):
        self.pedir(t=T0, status=503)
        self.pedir(t=T0 + 100, status=429)
        e = self.est(t=T0 + 200)
        self.assertEqual((e["SITUACAO"], e["PAUSADO_ATE"], e["CABEM"]), ("PAUSADO", T0 + 101 + DIA, 0))
        a = CA.reservar("cia.it", run_id="z", linha="S", agora=T0 + DIA)
        self.assertEqual((a["ESTADO"], a["MOTIVO"]), ("ADIADO_ATE", "PAUSA_24H"))
        self.assertEqual(CA.reservar("cia.it", run_id="z", linha="S", agora=T0 + 102 + DIA)["ESTADO"], "RESERVADO")

    def test_recuo_nunca_abaixo_do_minimo(self):
        for k in range(8):
            self.pedir(t=T0 + k * 2 * DIA, status=503)
        self.assertEqual(self.est(t=T0 + 16 * DIA)["ORCAMENTO_24H"], 5)

    def test_depois_do_sinal_so_dobra_com_nova_janela_limpa(self):
        self.pedir(t=T0, status=429)                                 # 40 -> 20
        self.dia_cheio("cia.it", T0 + 100, 10)                       # metade de 20, depois do sinal
        self.assertEqual(self.est(t=T0 + 2 + DIA + 100)["ORCAMENTO_24H"], 40)


class OsSinais(Base):
    def s(self, status, headers=None, corpo=None, n=None, url=None, marcas=(), hist=()):
        return CA.detectar_sinais(status, headers, corpo, n, url, marcas, list(hist), T0)[0]

    def test_403_novo_conta_e_o_repetido_nao(self):
        self.assertEqual(self.s(403), ["HTTP_403_NOVO"])
        self.assertEqual(self.s(403, hist=[{"STATUS": 200}]), ["HTTP_403_NOVO"])
        self.assertEqual(self.s(403, hist=[{"STATUS": 403}]), [])

    def test_pagina_de_desafio(self):
        self.assertEqual(self.s(200, corpo="<html><title>Just a moment...</title>" + "x" * 50000), ["PAGINA_DE_DESAFIO"])
        self.assertEqual(self.s(200, headers={"CF-Mitigated": "challenge"}), ["PAGINA_DE_DESAFIO"])
        self.assertEqual(self.s(200, corpo="<p>Sei un robot? completa il captcha</p>"), ["PAGINA_DE_DESAFIO"])
        # a pagina grande e normal que cita reCAPTCHA no formulario NAO e desafio
        self.assertEqual(self.s(200, corpo="<form class=g-recaptcha>captcha</form>" + "texto " * 5000), [])

    def test_timeouts_em_serie(self):
        h = [{"STATUS": 0, "MARCAS": ["TIMEOUT"]}]
        self.assertEqual(self.s(0, marcas=["TIMEOUT"], hist=h), [])
        self.assertEqual(self.s(0, marcas=["TIMEOUT"], hist=h * 2), ["TIMEOUTS_EM_SERIE"])
        self.assertEqual(self.s(0, marcas=["TIMEOUT"], hist=h * 2 + [{"STATUS": 200}]), [])

    def test_queda_brusca_de_bytes_na_mesma_url(self):
        h = [{"STATUS": 200, "URL": "u", "BYTES": 50000}]
        self.assertEqual(self.s(200, n=10000, url="u", hist=h), ["QUEDA_DE_BYTES"])
        self.assertEqual(self.s(200, n=20000, url="u", hist=h), [])
        self.assertEqual(self.s(200, n=100, url="outra", hist=h), [])

    def test_200_normal_nao_e_sinal(self):
        self.assertEqual(self.s(200, corpo="<html>ok</html>", n=16), [])

    def test_sinal_fora_do_vocabulario_e_fail(self):
        self.assertEqual(CA.registrar_resposta("cia.it", 200, sinais=["INVENTADO"], run_id="r", linha="S")["ESTADO"], "FAIL")


class UmDeCadaVez(Base):
    def test_o_segundo_no_mesmo_dominio_espera_sem_pedir(self):
        a = CA.reservar("cia.it", run_id="A", linha="S", agora=T0)
        b = CA.reservar("www.cia.it", run_id="B", linha="S", agora=T0 + 1)
        self.assertEqual((a["ESTADO"], b["ESTADO"], b["MOTIVO"]), ("RESERVADO", "ADIADO_ATE", "UM_DE_CADA_VEZ"))
        self.assertEqual(sum(1 for l in self.livro.read_text().splitlines() if '"RESERVA"' in l), 1)

    def test_pausa_minima_e_crawl_delay(self):
        self.pedir(t=T0)
        self.assertEqual(CA.reservar("cia.it", run_id="B", linha="S", agora=T0 + 3)["MOTIVO"], "PAUSA_MINIMA")
        self.assertEqual(CA.reservar("cia.it", run_id="B", linha="S", agora=T0 + 6.5)["ESTADO"], "RESERVADO")
        CA.registrar_resposta("cia.it", 200, run_id="B", linha="S", agora=T0 + 7)
        r = CA.reservar("cia.it", run_id="C", linha="S", agora=T0 + 13, crawl_delay_s=30)
        self.assertEqual((r["MOTIVO"], r["ATE"]), ("PAUSA_MINIMA", T0 + 37))

    def test_lease_expira_se_o_executor_morrer(self):
        CA.reservar("cia.it", run_id="A", linha="S", agora=T0)
        self.assertEqual(CA.reservar("cia.it", run_id="B", linha="S", agora=T0 + 149)["MOTIVO"], "UM_DE_CADA_VEZ")
        self.assertEqual(CA.reservar("cia.it", run_id="B", linha="S", agora=T0 + 151)["ESTADO"], "RESERVADO")

    def test_dominios_diferentes_correm_em_paralelo_ate_ao_limite_global(self):
        n = CA.politica()["LIMITE_GLOBAL_EM_PARALELO"]
        for i in range(n):
            self.assertEqual(CA.reservar("d%d.it" % i, run_id="r", linha="S", agora=T0)["ESTADO"], "RESERVADO")
        r = CA.reservar("mais.it", run_id="r", linha="S", agora=T0 + 1)
        self.assertEqual((r["ESTADO"], r["MOTIVO"]), ("ADIADO_ATE", "LIMITE_GLOBAL"))

    def test_orcamento_esgotado_diz_quando_abre(self):
        self.dia_cheio("cia.it", T0, 40)
        r = CA.reservar("cia.it", run_id="x", linha="S", agora=T0 + 1000)
        self.assertEqual((r["MOTIVO"], r["ATE"]), ("ORCAMENTO_ESGOTADO", T0 + DIA))


class OLivro(Base):
    def test_sem_livro_e_fail_e_nao_se_pede(self):
        os.environ.pop("SINTONIA_CORTESIA_LIVRO")
        self.assertEqual(CA.reservar("cia.it", run_id="r", linha="S")["ESTADO"], "FAIL")
        self.assertEqual(CA.orcamento_do_dominio("cia.it"), 40)      # sem memoria: o inicial da classe

    def test_nome_antigo_do_livro_e_sinonimo(self):
        os.environ.pop("SINTONIA_CORTESIA_LIVRO")
        os.environ["SINTONIA_TETO_24H"] = str(self.livro)
        self.assertEqual(CA.reservar("cia.it", run_id="r", linha="S", agora=T0)["ESTADO"], "RESERVADO")

    def test_livro_ilegivel_e_unknown_e_nao_escreve(self):
        # D124-REBASE — AJUSTE DECLARADO (verificador independente, 28/09): '{"RESERVAS": []}' era dado aqui
        # como ilegivel, e e o formato do livro VIVO da D90 (TETO-24H.json da coleta continua) — lido assim, toda
        # a reserva dava UNKNOWN e a coleta parava. O livro D90 BEM FORMADO le-se e migra-se
        # (tests/test_teto_adaptativo_rebase.py::OLivroAntigo); o D90 MALFORMADO continua ilegivel, e e ele que
        # fica aqui no lugar.
        for conteudo in ("{nao e json\n", '{"RESERVAS": 3}\n', '{"TIPO": "RESERVA"}\n'):
            self.livro.write_text(conteudo, encoding="utf-8")
            self.assertEqual(CA.reservar("cia.it", run_id="r", linha="S")["ESTADO"], "UNKNOWN", conteudo)
            self.assertEqual(CA.registrar_resposta("cia.it", 429, run_id="r", linha="S")["ESTADO"], "UNKNOWN")
            self.assertIsNone(CA.orcamento_do_dominio("cia.it"))
            self.assertEqual(self.livro.read_text(encoding="utf-8"), conteudo)

    def test_trinco_preso_e_unknown(self):
        os.mkdir(str(self.livro) + ".trinco")
        velho, CA.TRINCO_ESPERA_S = CA.TRINCO_ESPERA_S, 0.2
        try:
            self.assertEqual(CA.reservar("cia.it", run_id="r", linha="S")["ESTADO"], "UNKNOWN")
        finally:
            CA.TRINCO_ESPERA_S = velho
            os.rmdir(str(self.livro) + ".trinco")

    def test_so_se_acrescenta(self):
        self.pedir(t=T0)
        antes = self.livro.read_text(encoding="utf-8")
        self.pedir(t=T0 + 100, status=429)
        self.assertTrue(self.livro.read_text(encoding="utf-8").startswith(antes))

    def test_reserva_24h_e_fachada_do_mesmo_livro(self):
        from coleta import reserva_24h as R
        self.assertEqual(R.reservar("cia.it", 1, run_id="r", linha="S", agora=T0)["ESTADO"], "RESERVADO")
        self.assertEqual(R.reservar("cia.it", 2, run_id="r", linha="S")["ESTADO"], "FAIL")      # 1 de cada vez
        self.assertEqual(R.reservar("cia.it", 1, run_id="r", linha="S", teto=5)["ESTADO"], "FAIL")
        self.assertEqual(R.gasto_24h("cia.it", T0 + 1), 1)


class OAlerta(Base):
    def alertas(self):
        return CA.ler_alertas()

    def test_recuo_abre_bilhete_uma_vez_por_dia(self):
        self.pedir(t=T0, status=429, url="https://cia.it/x")
        self.pedir(t=T0 + 3 * DIA, status=503)
        self.pedir(t=T0 + 3 * DIA + 50000, status=503)               # 2.o sinal em 24 h: pausa (outro tipo)
        tipos = [(a["DOMINIO"], a["TIPO_ALERTA"]) for a in self.alertas()]
        self.assertEqual(tipos, [("cia.it", "RECUO"), ("cia.it", "RECUO"), ("cia.it", "PAUSA_24H")])
        a = self.alertas()[0]
        self.assertEqual((a["LINHA"], a["SINAL_MEDIDO"]["SINAIS"]), ("SITES", ["HTTP_429"]))
        self.assertIn("https://cia.it/x", a["RECIBOS"])
        self.assertIn("sitemap.xml", a["ESTUDAR"])

    def test_bilhete_nao_se_repete_no_mesmo_dia(self):
        self.pedir(t=T0, status=429)
        self.pedir(t=T0 + 3 * DIA, status=429)
        self.pedir(t=T0 + 3 * DIA + 10, status=403)
        self.assertEqual([a["TIPO_ALERTA"] for a in self.alertas()], ["RECUO", "RECUO", "PAUSA_24H"])

    def test_teto_de_seguranca_esgotado_abre_bilhete(self):
        t, nivel = T0, 40
        for _ in range(4):
            self.dia_cheio("cia.it", t, nivel, passo=6)
            t += DIA
            nivel = self.est(t=t)["ORCAMENTO_24H"]
        self.assertEqual(nivel, 640)
        self.dia_cheio("cia.it", t, 640, passo=6)
        self.assertEqual(CA.reservar("cia.it", run_id="z", linha="S", agora=t + 640 * 6 + 10)["MOTIVO"], "ORCAMENTO_ESGOTADO")
        self.assertEqual([a["TIPO_ALERTA"] for a in self.alertas()], ["TETO_DE_SEGURANCA"])

    def test_limite_publicado_da_api(self):
        pol = json.loads(CA.POLITICA_F.read_text(encoding="utf-8"))
        pol["CLASSES"]["API_COM_LIMITE_PUBLICADO"]["DOMINIOS"]["openalex.org"]["ORCAMENTO_24H"] = 2
        f = self.tmp / "pol.json"
        f.write_text(json.dumps(pol), encoding="utf-8")
        os.environ["SINTONIA_CORTESIA_POLITICA"] = str(f)
        try:
            self.dia_cheio("api.openalex.org", T0, 2)
            self.assertEqual(CA.reservar("api.openalex.org", run_id="z", linha="T6", agora=T0 + 100)["MOTIVO"], "ORCAMENTO_ESGOTADO")
            self.assertEqual([a["TIPO_ALERTA"] for a in self.alertas()], ["LIMITE_PUBLICADO"])
        finally:
            os.environ.pop("SINTONIA_CORTESIA_POLITICA")
            CA.politica(recarregar=True)

    def test_rendimento_baixo(self):
        self.assertIsNone(CA.registrar_rendimento("cia.it", pedidos=10, documentos_novos=0, run_id="r", linha="S", agora=T0)["ALERTA"])
        a = CA.registrar_rendimento("cia.it", pedidos=40, documentos_novos=3, run_id="r", linha="SITES", agora=T0,
                                    recibos=["RODADA-01/ONDA-WEB-ESTADO.json"])["ALERTA"]
        self.assertEqual((a["TIPO_ALERTA"], a["SINAL_MEDIDO"]["DOC_POR_PEDIDO"]), ("RENDIMENTO_BAIXO", 0.075))
        self.assertIsNone(CA.registrar_rendimento("x.it", pedidos=40, documentos_novos=30, run_id="r", linha="S", agora=T0)["ALERTA"])

    def test_pergunta_ao_scrap_engineer_e_texto_montado(self):
        self.pedir(t=T0, status=429, headers={"Retry-After": "60"})
        dia = CA._iso(T0)[:10]
        p = CA.pergunta_scrap_engineer(dia)
        txt = p.read_text(encoding="utf-8")
        self.assertEqual(p.name, "PERGUNTA-SCRAP-ENGINEER-%s.txt" % dia)
        for k in ("cia.it", "RECUO", "HTTP_429", "feed RSS/Atom", "sem LLM", "robots.txt"):
            self.assertIn(k, txt)
        self.assertIsNone(CA.pergunta_scrap_engineer("2000-01-01"))


class ACorridaEntreProcessos(Base):
    """D90-2: dois (ou 16) executores reservam o MESMO dominio ao mesmo tempo; so um passa, os outros
    recebem ADIADO_ATE sem pedir. So com isto PASS as linhas de rede podem correr em paralelo."""

    def test_16_processos_python_so_um_passa(self):
        with mp.get_context("spawn").Pool(8) as p:
            estados = p.map(_corredor, [(str(self.livro), i) for i in range(16)])
        self.assertEqual(estados.count("RESERVADO"), 1, estados)
        self.assertEqual(estados.count("ADIADO_ATE"), 15)
        self.assertEqual(len(CA.ler_eventos(self.livro)), 1)

    def test_python_e_node_excluem_se_pelo_mesmo_trinco(self):
        js = ("import('./coleta/cortesia_adaptativa.mjs').then(m=>{const o=[];for(let i=0;i<6;i++)"
              "o.push(m.reservar('cia.it',{runId:'N'+i,linha:'NODE'}).ESTADO);console.log(JSON.stringify(o))})")
        p = subprocess.Popen(["node", "-e", js], cwd=RAIZ, env=dict(os.environ), stdout=subprocess.PIPE, text=True)
        py = [CA.reservar("cia.it", run_id="P%d" % k, linha="PY")["ESTADO"] for k in range(6)]
        node = json.loads(p.communicate(timeout=120)[0].strip().splitlines()[-1])
        self.assertEqual((py + node).count("RESERVADO"), 1, (py, node))
        self.assertEqual(len(CA.ler_eventos(self.livro)), 1)


class OGemeoNode(Base):
    def _node(self, js):
        p = subprocess.run(["node", "--input-type=module", "-e", js], cwd=RAIZ, env=dict(os.environ),
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr[-800:])
        return json.loads(p.stdout.strip().splitlines()[-1])

    def test_a_mesma_dobra_nos_dois(self):
        """Um livro com sobe, recua, Retry-After, pausa, lease e crawl-delay: o estado de cada dominio,
        em varios instantes, e o MESMO em Python e em Node."""
        self.dia_cheio("cia.it", T0, 25)
        self.pedir("cia.it", T0 + DIA + 50, status=429, headers={"Retry-After": "300"})
        self.pedir("cia.it", T0 + DIA + 900, status=503)
        self.dia_cheio("youtube.com", T0, 3, passo=20)
        CA.reservar("x.it", run_id="r", linha="S", agora=T0 + 5, crawl_delay_s=40)
        self.pedir("api.crossref.org", T0 + 7)
        instantes = [T0 + 30, T0 + DIA + 60, T0 + DIA + 1000, T0 + 3 * DIA, T0 + 40 * DIA]
        doms = ["cia.it", "youtube.com", "x.it", "crossref.org", "nunca.it"]
        ev = CA.ler_eventos(self.livro)
        py = {"%s@%s" % (d, t): CA.dobrar_eventos(ev, d, t) for d in doms for t in instantes}
        js = ("import * as C from './coleta/cortesia_adaptativa.mjs';const ev=C.lerEventos(%s);const o={};"
              "for(const d of %s)for(const t of %s)o[d+'@'+t.toFixed(1)]=C.dobrarEventos(ev,d,t);console.log(JSON.stringify(o))"
              % (json.dumps(str(self.livro)), json.dumps(doms), json.dumps(instantes)))
        node = self._node(js)
        self.assertEqual(sorted(node), sorted(py))
        for k in py:
            self.assertEqual(json.loads(json.dumps(py[k])), node[k], k)

    def test_os_mesmos_sinais_nos_dois(self):
        casos = [(429, {}, None, None, None, [], []), (403, {}, None, None, None, [], [{"STATUS": 403}]),
                 (200, {"cf-mitigated": "challenge"}, None, None, None, [], []),
                 (200, {}, "Just a moment...", 16, None, [], []), (503, {"Retry-After": "7"}, None, None, None, [], []),
                 (0, {}, None, None, None, ["TIMEOUT"], [{"STATUS": 0, "MARCAS": ["TIMEOUT"]}] * 2),
                 (200, {}, None, 100, "u", [], [{"STATUS": 200, "URL": "u", "BYTES": 9000}])]
        py = [list(CA.detectar_sinais(s, h, c, n, u, m, hi, T0)) for s, h, c, n, u, m, hi in casos]
        js = ("import * as C from './coleta/cortesia_adaptativa.mjs';const casos=%s;"
              "console.log(JSON.stringify(casos.map(([s,h,c,n,u,m,hi])=>C.detectarSinais({status:s,headers:h,corpo:c,nBytes:n,url:u,marcas:m,historico:hi,agora:%r}))))"
              % (json.dumps(casos), T0))
        self.assertEqual(json.loads(json.dumps(py)), self._node(js))

    def test_node_com_trinco_preso_e_unknown_e_nao_escreve(self):
        os.mkdir(str(self.livro) + ".trinco")
        try:
            e = self._node("import * as C from './coleta/cortesia_adaptativa.mjs';"
                           "console.log(JSON.stringify(C.reservar('cia.it',{runId:'N',linha:'NODE'}).ESTADO))")
            self.assertEqual(e, "UNKNOWN")
            self.assertFalse(self.livro.exists())
        finally:
            os.rmdir(str(self.livro) + ".trinco")

    def test_node_livro_ilegivel_e_unknown(self):
        self.livro.write_text('{"TIPO": "RESERVA"}\n', encoding="utf-8")
        e = self._node("import * as C from './coleta/cortesia_adaptativa.mjs';"
                       "console.log(JSON.stringify([C.reservar('cia.it',{runId:'N',linha:'NODE'}).ESTADO, C.orcamentoDoDominio('cia.it')]))")
        self.assertEqual(e, ["UNKNOWN", None])
        self.assertEqual(self.livro.read_text(encoding="utf-8"), '{"TIPO": "RESERVA"}\n')

    def test_node_escreve_e_python_le_o_mesmo_recuo(self):
        js = ("import * as C from './coleta/cortesia_adaptativa.mjs';const T=%r;"
              "const a=C.reservar('cia.it',{runId:'N',linha:'NODE',agora:T});"
              "const b=C.registrarResposta('cia.it',{status:429,headers:{'Retry-After':'120'},runId:'N',linha:'NODE',agora:T+1});"
              "console.log(JSON.stringify([a.ESTADO,b.SINAIS,b.DEPOIS.ORCAMENTO_24H]))" % T0)
        self.assertEqual(self._node(js), ["RESERVADO", ["HTTP_429", "RETRY_AFTER"], 20])
        a = CA.reservar("cia.it", run_id="P", linha="PY", agora=T0 + 60)
        self.assertEqual((a["MOTIVO"], a["ATE"]), ("RETRY_AFTER", T0 + 121))
        self.assertEqual([x["TIPO_ALERTA"] for x in CA.ler_alertas()], ["RECUO"])


class AProvaTeto(Base):
    """provas/prova_teto_dominio.py (D124): nunca passou do orcamento vigente; recuou no sinal."""

    def setUp(self):
        super().setUp()
        import prova_teto_dominio as PT
        self.PT = PT

    def linha(self, tipo, t, dom="cia.it", **kw):
        return dict({"TIPO": tipo, "DOMINIO": dom, "EM": t, "RUN_ID": "r", "LINHA": "S"}, **kw)

    def test_livro_honesto_passa(self):
        self.dia_cheio("cia.it", T0, 30)
        self.pedir("cia.it", T0 + 400, status=429, headers={"Retry-After": "100"})
        self.pedir("cia.it", T0 + 600)
        r = self.PT.verificar_livro(CA.ler_eventos(self.livro))
        self.assertEqual((r["ESTADO"], r["VIOLACOES"]), ("PASS", []))

    def test_cada_desobediencia_e_apanhada(self):
        casos = {
            "RESERVA_ANTES_DO_RETRY_AFTER": [self.linha("RESERVA", T0), self.linha("RESPOSTA", T0 + 1, STATUS=429, SINAIS=["HTTP_429", "RETRY_AFTER"], RETRY_AFTER_S=600),
                                             self.linha("RESERVA", T0 + 60)],
            "RESERVA_DURANTE_PAUSA_24H": [self.linha("RESPOSTA", T0, STATUS=503, SINAIS=["HTTP_503"]), self.linha("RESPOSTA", T0 + 10, STATUS=503, SINAIS=["HTTP_503"]),
                                          self.linha("RESERVA", T0 + 3600)],
            "RAJADA_NO_MESMO_DOMINIO": [self.linha("RESERVA", T0), self.linha("RESERVA", T0 + 30)],
            "PAUSA_MINIMA_VIOLADA": [self.linha("RESERVA", T0), self.linha("RESPOSTA", T0 + 1, STATUS=200, SINAIS=[]), self.linha("RESERVA", T0 + 2)],
            "PASSOU_DO_ORCAMENTO_VIGENTE": [x for k in range(41) for x in (self.linha("RESERVA", T0 + 10 * k),
                                                                             self.linha("RESPOSTA", T0 + 10 * k + 1, STATUS=200, SINAIS=[]))],
        }
        for nome, ev in casos.items():
            r = self.PT.verificar_livro(ev)
            self.assertEqual(r["ESTADO"], "FAIL", nome)
            self.assertIn(nome, {v["VIOLACAO"] for v in r["VIOLACOES"]}, nome)

    def test_a_onda_conta_contra_o_orcamento_vigente_e_nao_contra_5(self):
        corridas = {"IT-T1-2026-09-27-100000-%016x" % 1: {"CORTESIA": {"PEDIDOS_POR_HOST": {"www.cia.it": 30, "x.it": 3}}}}
        ids = list(corridas)
        self.assertEqual(self.PT.verificar(ids, corridas)["ESTADO"], "PASS")          # 30 <= 40 (era FAIL com 5)
        corridas[ids[0]]["CORTESIA"]["PEDIDOS_POR_HOST"]["cia.it"] = 11
        r = self.PT.verificar(ids, corridas)
        self.assertEqual((r["ESTADO"], r["DOMINIOS_ACIMA_DO_TETO"]), ("FAIL", {"cia.it": 41}))
        self.assertEqual(self.PT.verificar(ids, corridas, teto=50)["ESTADO"], "PASS")   # manual declarado

    def test_pedido_sem_reserva_e_apanhado(self):
        rid = "IT-T1-2026-09-27-100000-%016x" % 2
        CA.reservar("cia.it", run_id=rid, linha="S", agora=T0)
        corr = {rid: {"CORTESIA": {"PEDIDOS_POR_HOST": {"cia.it": 3}}}}
        self.assertEqual(self.PT.cruzar([rid], corr, CA.ler_eventos(self.livro)),
                         [{"RUN_ID": rid, "DOMINIO": "cia.it", "PEDIDOS": 3, "RESERVAS": 1}])


class OPainel(unittest.TestCase):
    def test_materia_prima_por_dia_so_leitura(self):
        sys.path.insert(0, str(RAIZ / "medidas"))
        import materia_prima_por_dia as MP
        tmp = Path(tempfile.mkdtemp(prefix="mp-"))
        try:
            (tmp / "runs.ndjson").write_text("\n".join(json.dumps(x) for x in [
                {"RUN_ID": "a", "FINISHED_AT": "2026-09-27T10:00:00Z", "contadores": {"NEW_DOCUMENTS": 7, "INDEX_REQUESTS": 2, "DETAIL_REQUESTS": 12}},
                {"RUN_ID": "b", "FINISHED_AT": "2026-09-27T23:00:00Z", "contadores": {"NEW_DOCUMENTS": 3, "INDEX_REQUESTS": 1, "DETAIL_REQUESTS": 5}},
                {"RUN_ID": "c", "FINISHED_AT": "2026-09-28T01:00:00Z", "contadores": {"NEW_DOCUMENTS": 1}}]) + "\n{partido\n")
            (tmp / "o1").mkdir()
            (tmp / "o1" / "ONDA-WEB-ESTADO.json").write_text(json.dumps({"FONTES": [
                {"RUN_ID": "IT-T1-2026-09-27-100000-%016x" % 1, "SALA_ANTES": {"sala.item": 10}, "SALA_DEPOIS": {"sala.item": 14}}]}))
            r = MP.painel(tmp / "runs.ndjson", tmp, None)
            d = {(x["DIA"], x["LINHA"]): x for x in r["DIAS"]}
            self.assertEqual(d[("2026-09-27", "SITES")]["DOCUMENTOS_NOVOS"], 10)
            self.assertEqual(d[("2026-09-27", "SITES")]["PEDIDOS"], 20)
            self.assertEqual(d[("2026-09-27", "SITES")]["DOC_POR_PEDIDO"], 0.5)
            self.assertEqual(d[("2026-09-27", "SITES")]["ITENS_NOVOS_NA_SALA"], 4)
            self.assertEqual(d[("2026-09-28", "SITES")]["PEDIDOS"], "NAO SEI")       # sem contagem: nao e zero
            self.assertEqual(d[("2026-09-28", "SITES")]["ITENS_NOVOS_NA_SALA"], "NAO SEI")
            self.assertEqual(r["CORRIDAS_ILEGIVEIS"], 1)
            src = (RAIZ / "medidas" / "materia_prima_por_dia.py").read_text(encoding="utf-8")
            for proibido in ("urllib", "requests", "socket", "http.client", "subprocess"):
                self.assertNotIn("import " + proibido, src)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# O ensaio do transporte contra o servidor local (200/429/503/Retry-After/desafio, provas/contador_24h_local.mjs)
# corre em tests/test_contador_24h.py::OTransporteContraOServidor — a casa dele desde a D90; nao se corre duas vezes.


if __name__ == "__main__":
    unittest.main()
