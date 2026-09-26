# -*- coding: utf-8 -*-
"""MAESTRO-SOCIAL · uma rodada social de ponta a ponta, sem rede.

O que e REAL aqui: o freio (`scrap_http` + `teto_da_onda`) contra um servidor em 127.0.0.1, a linha do
livro de corridas (`scrap_colheita.linha_da_corrida`/`escrever_linha`) e a prova-teto
(`provas/prova_teto_dominio.verificar`). O que e dublo: o egresso (o dono mede-o na rede), o
orquestrador (cada «corrida» faz N pedidos ao servidor local) e o portao.

    M1  o livro da onda e UM para as contas da onda: a 2.a conta so tem o que sobrou (o 6.o nao sai)
    M2  cada onda tem livro NOVO
    M3  VPN fora de IT ANTES da fonte: PARA e nada sai
    M4  VPN muda DEPOIS da fonte: PARA
    M5  prova-teto != PASS: PARA na onda
    M6  --retomar continua da fonte seguinte, nao relanca as feitas, e usa o MESMO livro
    M7  YouTube sem chave e sem video: nao corre, nao e FAILED; com video: audio-youtube
    M8  o estado le-se com `micro_coleta.corridas_do_estado` e o relatorio diz o que se passou
    M9  --canario deixa entrar SCRAP_FASE em CANARY_PENDING; sem ele, nao
    M10 plano que nao cabe no teto nao corre
"""
import itertools
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
for p in ("", "coleta", "curadoria", "provas", "orquestrador", "scripts/micro_coleta",
          "ferramentas/maestro_social"):
    sys.path.insert(0, str(RAIZ / p) if p else str(RAIZ))
import _gavetas  # noqa: E402,F401

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ[k] = "http://127.0.0.1:9"
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost"

import maestro_social as MS  # noqa: E402
import scrap_http as http  # noqa: E402
import teto_da_onda as teto  # noqa: E402
from coleta import scrap_colheita as sc  # noqa: E402
from tests.test_prova_teto_social import _Servidor  # noqa: E402

_N = itertools.count(1)


def run_id():
    return "IT-T5-2026-09-26-06%04d-%016x" % (next(_N), 0xabc)


def contrato(sid, fase, **filtros):
    return {"SOURCE_ID": sid, "TERRITORY": "T5",
            "ACQUISITION": {"STRATEGY": "SCRAP_FASE", "FASE": fase, "FILTROS": filtros}}


CONTRATOS = {"LI-A": contrato("LI-A", "video-linkedin", pagina="https://www.linkedin.com/company/a/", teto=2),
             "LI-B": contrato("LI-B", "video-linkedin", pagina="https://www.linkedin.com/company/b/", teto=2),
             "LI-C": contrato("LI-C", "video-linkedin", pagina="https://www.linkedin.com/company/c/", teto=2),
             "YT-A": contrato("YT-A", "canal-youtube", canal_id="UCaaaaaaaaaaaaaaaaaaaaaa")}


def plano(rodadas):
    return lambda: {"TODAS_CABEM": all(r.get("CABE_NO_TETO", True) for r in rodadas), "ONDAS": len(rodadas),
                    "RODADAS": [dict({"CABE_NO_TETO": True}, **r) for r in rodadas]}


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="maestro-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        for k, v in {"ITALY_OPS_ROOT": str(self.tmp / "ops")}.items():
            p = mock.patch.dict(os.environ, {k: v})
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(os.environ.pop, "SINTONIA_TETO_ONDA", None)
        self.srv = _Servidor()
        self.addCleanup(self.srv.fechar)
        http._ROBOTS.clear()
        p = mock.patch.object(http, "PAUSA_ENTRE_CHAMADAS", 0)
        p.start()
        self.addCleanup(p.stop)
        self.lancadas, self.livros = [], []
        self.pedidos_por_fonte = {}
        # o aviso ao coordenador vai para um ficheiro DO TESTE — nunca para o real
        # (26/09: a 1.a versao destes testes escreveu 8 avisos falsos no bc4-aviso-vivo.txt)
        self.aviso = self.tmp / "AVISO.txt"
        p = mock.patch.object(MS, "AVISO", self.aviso)
        p.start()
        self.addCleanup(p.stop)

    def lancar(self, n_por_fonte=3):
        """Cada «corrida» faz N pedidos ao servidor local pelo portao REAL (com freio) e escreve a linha REAL."""
        def f(sid, pedido, pasta):
            self.lancadas.append((sid, dict(pedido.filtros)))
            self.livros.append(os.environ.get("SINTONIA_TETO_ONDA"))
            http.zerar_contagem()
            teto.zerar()
            http._ROBOTS.clear()
            antes = len(self.srv.pedidos)
            rid = run_id()
            try:
                for i in range(self.pedidos_por_fonte.get(sid, n_por_fonte)):
                    http.buscar(self.srv.url("/%s/%d" % (sid, i)), aceitar_json=False)
            except http.TetoDoDominio:
                pass
            self.feitos = len(self.srv.pedidos) - antes
            sc.escrever_linha(sc.linha_da_corrida(run_id=rid, fase="video-linkedin", fonte=sid,
                                                  inicio=MS.agora()))
            return {"STATUS": "SUCCESS", "RUN_ID": rid, "CODIGO": 0}
        return f

    def correr(self, rodadas, *, egresso=None, retomar=False, lancar=None, prova=MS.prova_teto, videos=None):
        return MS.correr(self.tmp / "rodada", retomar=retomar, videos=videos,
                         egresso=egresso or (lambda: {"PAIS": "IT"}), lancar=lancar or self.lancar(),
                         precondicoes=lambda: [], gate=lambda s: "CANARY_PENDING",
                         prova=prova, contratos_fn=lambda: CONTRATOS, plano_fn=plano(rodadas))

    def estado(self):
        return json.loads((self.tmp / "rodada" / MS.ESTADO).read_text(encoding="utf-8"))


class M1OLivroEUmPorOnda(_Base):
    def test_a_segunda_conta_so_tem_o_que_sobrou(self):
        rc = self.correr([{"ONDA": 1, "LINKEDIN": ["LI-A", "LI-B"], "YOUTUBE": []}])
        e = self.estado()
        self.assertEqual(rc, 0, e.get("PAROU"))
        self.assertEqual(len(self.srv.pedidos), 5)                 # 4 + 1: o 6.o nao saiu
        a, b = e["FONTES"]
        self.assertEqual(a["PEDIDOS_POR_HOST"], {"127.0.0.1": 4})   # robots + 3 paginas
        self.assertEqual(b["PEDIDOS_POR_HOST"], {"127.0.0.1": 1})   # so o robots coube
        self.assertEqual([r["MOTIVO"] for r in b["RECUSAS_DO_FREIO"]], ["TETO_DOMINIO"])
        self.assertEqual(e["ONDAS"][0]["LIVRO_NO_FIM"], {"127.0.0.1": 5})
        self.assertEqual(e["ONDAS"][0]["PROVA_TETO"]["ESTADO"], "PASS")
        self.assertEqual(self.lancadas[0][1]["teto"], "1")           # C2: o pedido leva teto=1

    def test_cada_onda_tem_livro_novo(self):
        self.correr([{"ONDA": 1, "LINKEDIN": ["LI-A"], "YOUTUBE": []},
                     {"ONDA": 2, "LINKEDIN": ["LI-B"], "YOUTUBE": []}])
        self.assertNotEqual(self.livros[0], self.livros[1])
        self.assertEqual(len(self.srv.pedidos), 8)                 # 4 + 4, cada onda com o seu teto


class M3VPN(_Base):
    def test_fora_de_it_antes_nada_sai(self):
        rc = self.correr([{"ONDA": 1, "LINKEDIN": ["LI-A"], "YOUTUBE": []}], egresso=lambda: {"PAIS": "US"})
        self.assertEqual(rc, 1)
        self.assertEqual(self.lancadas, [])
        self.assertIn("EGRESSO_NAO_IT", self.estado()["PAROU"]["PORQUE"])
        self.assertIn("EGRESSO_NAO_IT", self.aviso.read_text(encoding="utf-8"))   # o aviso sai, no sitio do teste

    def test_vpn_muda_depois_para(self):
        paises = iter(["IT", "NL"])
        rc = self.correr([{"ONDA": 1, "LINKEDIN": ["LI-A", "LI-B"], "YOUTUBE": []}],
                         egresso=lambda: {"PAIS": next(paises)})
        self.assertEqual(rc, 1)
        self.assertEqual([s for s, _ in self.lancadas], ["LI-A"])
        self.assertIn("EGRESSO_SAIU_DE_IT", self.estado()["PAROU"]["PORQUE"])


class M5ProvaTeto(_Base):
    def test_prova_que_nao_passa_para(self):
        rc = self.correr([{"ONDA": 1, "LINKEDIN": ["LI-A"], "YOUTUBE": []},
                          {"ONDA": 2, "LINKEDIN": ["LI-B"], "YOUTUBE": []}],
                         prova=lambda ids: {"ESTADO": "NAO_SEI"})
        self.assertEqual(rc, 1)
        self.assertEqual([s for s, _ in self.lancadas], ["LI-A"])
        self.assertIn("PROVA_TETO_NAO_SEI", self.estado()["PAROU"]["PORQUE"])


class M6Retomar(_Base):
    def test_continua_da_fonte_seguinte_com_o_mesmo_livro(self):
        rod = [{"ONDA": 1, "LINKEDIN": ["LI-A", "LI-B"], "YOUTUBE": []},
               {"ONDA": 2, "LINKEDIN": ["LI-C"], "YOUTUBE": []}]
        paises = iter(["IT", "IT", "US"])                          # LI-A corre; antes de LI-B, fora de IT
        self.assertEqual(self.correr(rod, egresso=lambda: {"PAIS": next(paises)}), 1)
        self.assertEqual([s for s, _ in self.lancadas], ["LI-A"])
        with self.assertRaises(SystemExit):                       # sem --retomar, nao se reescreve a rodada
            self.correr(rod)
        rc = self.correr(rod, retomar=True)
        e = self.estado()
        self.assertEqual(rc, 0, e.get("PAROU"))
        self.assertEqual([s for s, _ in self.lancadas], ["LI-A", "LI-B", "LI-C"])     # LI-A nao relancou
        self.assertEqual(self.livros[0], self.livros[1])           # a onda 1 continua no MESMO livro
        self.assertEqual(e["ONDAS"][0]["LIVRO_NO_FIM"], {"127.0.0.1": 5})
        self.assertEqual(len(e["RETOMADAS"]), 1)
        self.assertTrue(e["FIM"])


class M7YouTube(_Base):
    def test_sem_chave_e_sem_video_nao_corre_e_nao_e_failed(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(MS.ENV_CHAVE_YT, None)
            rc = self.correr([{"ONDA": 1, "LINKEDIN": [], "YOUTUBE": ["YT-A"]}])
        e = self.estado()
        self.assertEqual(rc, 0, e.get("PAROU"))
        self.assertEqual(self.lancadas, [])
        self.assertEqual(e["FONTES"][0]["PORQUE_NAO_CORREU"], "SEM_VIDEO_E_SEM_CHAVE")

    def test_com_video_vai_por_audio_youtube(self):
        os.environ.pop(MS.ENV_CHAVE_YT, None)
        self.correr([{"ONDA": 1, "LINKEDIN": [], "YOUTUBE": ["YT-A"]}], videos={"YT-A": "AbCdEfGhIjK"})
        [(sid, f)] = self.lancadas
        self.assertEqual((f["fase"], f["video"]), ("audio-youtube", "AbCdEfGhIjK"))


class M8Relatorio(_Base):
    def test_estado_legivel_pelo_relatorio_do_runbook_e_pelo_maestro(self):
        import micro_coleta as M
        self.correr([{"ONDA": 1, "LINKEDIN": ["LI-A", "LI-B"], "YOUTUBE": []}])
        e = self.estado()
        cs = M.corridas_do_estado(e)
        self.assertEqual([c["SOURCE_ID"] for c in cs], ["LI-A", "LI-B"])
        self.assertEqual(cs[0]["EGRESSO_ANTES"], {"PAIS": "IT"})
        r = MS.relatorio(e)
        self.assertEqual((r["FONTES_CORRIDAS"], r["RECUSAS_DO_FREIO"], r["EGRESSO_SEMPRE_IT"], r["TERMINOU"]),
                         (2, 1, True, True))
        self.assertEqual(r["PROVA_TETO_POR_ONDA"], {1: "PASS"})
        self.assertIn("PROVA_TETO_POR_ONDA", MS.relatorio_md(r))


class M9Canario(unittest.TestCase):
    def linhas(self):
        return [{"SOURCE_ID": "LI-A", "FASE": "video-linkedin", "NA_ONDA": False, "ESTADO": "CANARY_PENDING",
                 "FALTA": ["PORTAO:ESTADO_NAO_READY"]},
                {"SOURCE_ID": "LI-X", "FASE": "video-linkedin", "NA_ONDA": False, "ESTADO": "CANARY_PENDING",
                 "FALTA": ["PORTAO:ESTADO_NAO_READY", "EXECUTOR:outro"]},
                {"SOURCE_ID": "LI-R", "FASE": "video-linkedin", "NA_ONDA": False, "ESTADO": "RETRY_AFTER",
                 "FALTA": ["PORTAO:ESTADO_NAO_READY"]}]

    def test_canario_so_abre_canary_pending_sem_outra_falta(self):
        import plano_onda_social as P
        with mock.patch.object(P, "plano", return_value={"LINHAS": self.linhas()}):
            com = MS.linhas_do_plano(canario=True)
        with mock.patch.object(P, "plano", return_value={"LINHAS": self.linhas()}):
            sem = MS.linhas_do_plano(canario=False)
        self.assertEqual([l["SOURCE_ID"] for l in com if l["NA_ONDA"]], ["LI-A"])
        self.assertEqual([l["SOURCE_ID"] for l in sem if l["NA_ONDA"]], [])

    def test_fonte_pedida_fora_do_plano_recusa(self):
        with self.assertRaises(SystemExit):
            MS.escolher(self.linhas(), ["LI-NAO-EXISTE"])


class M10PlanoQueNaoCabe(_Base):
    def test_nao_corre(self):
        with self.assertRaises(SystemExit):
            self.correr([{"ONDA": 1, "LINKEDIN": ["LI-A"], "YOUTUBE": [], "CABE_NO_TETO": False}])
        self.assertEqual(self.lancadas, [])


if __name__ == "__main__":
    unittest.main()
