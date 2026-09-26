# -*- coding: utf-8 -*-
"""DISPARADOR-RODADAS (26/09/2026): as rodadas, uma a uma, contra um SERVIDOR LOCAL que conta.

Zero rede externa: o servidor e 127.0.0.1; a onda falsa pede com o cabecalho Host de cada fonte
(a.test, b.test, ...) e sem proxy. Quem conta os pedidos e o SERVIDOR; a PROVA-TETO que fecha a
rodada e a de `provas/prova_teto_dominio.py`, importada pelo disparador.

A onda falsa faz o que o transporte faz (`coleta/italy_pilot_collect.mjs`): le o livro do teto da
onda (`<pasta>/TETO-ONDA.json`), nao pede acima de 5 por dominio, soma no livro, e escreve a linha
da corrida em runs.ndjson com CORTESIA.PEDIDOS_POR_HOST. O modo DESOBEDECE ignora o livro: e o
transporte avariado que a prova tem de apanhar.

    py tests/test_rodadas.py
"""
import http.server
import json
import os
import secrets
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
import rodadas as R  # noqa: E402

CONTAGEM: dict = {}


class _Servidor(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        h = (self.headers.get("Host") or "").split(":")[0]
        CONTAGEM[h] = CONTAGEM.get(h, 0) + 1
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *a):
        pass


SRV = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Servidor)
threading.Thread(target=SRV.serve_forever, daemon=True).start()
PORTA = SRV.server_address[1]
SEM_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))

# fonte -> (host, pedidos que a fonte quer fazer)
FONTES = {
    "IT-T8-001": ("www.a.test", 5), "IT-T8-002": ("a.test", 5), "IT-T8-003": ("sub.a.test", 5),
    "IT-T7-001": ("b.test", 2),
    "IT-T2-001": ("c.test", 2), "IT-T2-002": ("www.c.test", 2),
}
LINHAS = [{"SOURCE_ID": s, "DOMINIO": R.PT.dominio_registavel(h), "PEDIDOS_PREVISTOS": 5}
          for s, (h, _) in FONTES.items()]
MEDIDOS = {s: n for s, (_, n) in FONTES.items()}
SHA = "c0" * 32


def _por_dominio(cont):
    out = {}
    for h, n in cont.items():
        d = R.PT.dominio_registavel(h)
        out[d] = out.get(d, 0) + n
    return out


class OndaFalsa:
    """O papel de `onda_web.py --correr` numa rodada, com pedidos HTTP de verdade ao servidor local."""

    def __init__(self, ledger, desobedece_na_rodada=None, sem_linha_na_rodada=None, codigo=0):
        self.ledger, self.desobedece, self.sem_linha, self.codigo = ledger, desobedece_na_rodada, sem_linha_na_rodada, codigo
        self.chamadas = []
        self.quando = None                                  # instante UTC do RUN_ID (None = agora)

    def __call__(self, sha, fontes, pasta, historico, retomar):
        self.chamadas.append({"FONTES": list(fontes), "PASTA": str(pasta), "RETOMAR": retomar})
        n_rodada = int(Path(pasta).name.split("-")[1])
        pasta.mkdir(parents=True, exist_ok=True)
        livro_f = pasta / "TETO-ONDA.json"
        livro = json.loads(livro_f.read_text(encoding="utf-8"))["PEDIDOS_POR_DOMINIO"] if livro_f.exists() else {}
        estado = {"INICIO": datetime.now().strftime("%H:%M:%S"), "FONTES": [], "PAROU": None}
        for s in fontes:
            host, quer = FONTES[s]
            d = R.PT.dominio_registavel(host)
            cabe = quer + 3 if self.desobedece == n_rodada else max(0, min(quer, R.TETO - livro.get(d, 0)))
            for _ in range(cabe):
                rq = urllib.request.Request("http://127.0.0.1:%d/" % PORTA, headers={"Host": host})
                SEM_PROXY.open(rq, timeout=10).read()
            livro[d] = livro.get(d, 0) + cabe
            livro_f.write_text(json.dumps({"PEDIDOS_POR_DOMINIO": livro}), encoding="utf-8")
            rid = "%s-%s-%s" % (s.rsplit("-", 1)[0], (self.quando or datetime.now(timezone.utc)).strftime("%Y-%m-%d-%H%M%S"), secrets.token_hex(8))
            if self.sem_linha != n_rodada:
                with open(self.ledger, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"RUN_ID": rid, "CORTESIA": {"PEDIDOS_POR_HOST": {host: cabe}}}) + "\n")
            estado["FONTES"].append({"SOURCE_ID": s, "CORREU": cabe > 0, "RUN_ID": rid,
                                     "PEDIDOS_POR_DOMINIO": {d: cabe}})
        (pasta / "ONDA-WEB-ESTADO.json").write_text(json.dumps(estado), encoding="utf-8")
        return self.codigo


class Portao:
    def __init__(self, falha_na_chamada=None):
        self.n, self.falha = 0, falha_na_chamada

    def __call__(self):
        self.n += 1
        return {"PASSA": self.n != self.falha, "PAIS": "IT" if self.n != self.falha else "BR"}


class Relatorio:
    def __init__(self):
        self.chamadas = []

    def __call__(self, estado, saida):
        self.chamadas.append(str(estado))
        return 0


class Base(unittest.TestCase):
    def setUp(self):
        CONTAGEM.clear()
        self.tmp = Path(tempfile.mkdtemp(prefix="rodadas-"))
        self.base = self.tmp / "ondas" / "ONDA4"
        self.base.mkdir(parents=True)
        self.ledger = self.tmp / "runs.ndjson"
        self.rodadas = R.planear(LINHAS, MEDIDOS)
        self.plano = {"COORTE_SHA256": SHA, "RODADAS": self.rodadas}
        self.rel = Relatorio()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def correr(self, onda, portao=None, **kw):
        return R.correr_rodadas(self.base, SHA, self.plano, onda=onda, portao=portao or Portao(),
                                relatorio=self.rel, ledger=self.ledger, **kw)


class OPlano(Base):
    def test_nenhum_dominio_passa_de_5_por_rodada(self):
        self.assertEqual(len(self.rodadas), 3)                      # a.test: 3 fontes de 5
        for r in self.rodadas:
            self.assertLessEqual(r["MAXIMO_POR_DOMINIO"], 5)
        self.assertEqual([f["SOURCE_ID"] for f in self.rodadas[0]["FONTES"]],
                         ["IT-T8-001", "IT-T7-001", "IT-T2-001", "IT-T2-002"])   # c.test: 2+2 cabem juntas

    def test_limiar_exacto_5_cabe_6_nao(self):
        r = R.planear([{"SOURCE_ID": "X1", "DOMINIO": "x.it"}, {"SOURCE_ID": "X2", "DOMINIO": "x.it"}],
                      {"X1": 3, "X2": 2})
        self.assertEqual(len(r), 1)
        r = R.planear([{"SOURCE_ID": "X1", "DOMINIO": "x.it"}, {"SOURCE_ID": "X2", "DOMINIO": "x.it"}],
                      {"X1": 3, "X2": 3})
        self.assertEqual(len(r), 2)

    def test_sem_medida_vale_o_teto_inteiro(self):
        r = R.planear([{"SOURCE_ID": "X1", "DOMINIO": "x.it"}], {})
        self.assertEqual(r[0]["FONTES"][0]["PREVISTOS"], 5)

    def test_pedidos_medidos_le_o_maximo(self):
        e = [{"FONTES": [{"SOURCE_ID": "X", "CORREU": True, "PEDIDOS_POR_DOMINIO": {"x.it": 2}}]},
             {"FONTES": [{"SOURCE_ID": "X", "CORREU": True, "PEDIDOS_POR_DOMINIO": {"x.it": 4}},
                         {"SOURCE_ID": "Y", "CORREU": False}]}]
        self.assertEqual(R.pedidos_medidos(e), {"X": 4})


class AsRodadasContraOServidor(Base):
    def test_todas_fecham_e_o_servidor_nunca_ve_mais_de_5_por_dominio_por_rodada(self):
        onda = OndaFalsa(self.ledger)
        antes = {}
        e = None
        for n in (1, 2, 3):
            e = self.correr(onda, rodada=n)
            agora = _por_dominio(CONTAGEM)
            delta = {d: agora[d] - antes.get(d, 0) for d in agora}
            self.assertLessEqual(max(delta.values()), 5, (n, delta))
            antes = agora
        self.assertEqual({k: v["ESTADO"] for k, v in e["RODADAS"].items()},
                         {"1": "FECHADA", "2": "FECHADA", "3": "FECHADA"})
        self.assertEqual(_por_dominio(CONTAGEM), {"a.test": 15, "b.test": 2, "c.test": 4})
        for n in ("1", "2", "3"):
            self.assertEqual(e["RODADAS"][n]["PROVA_TETO"]["ESTADO"], "PASS")

    def test_cada_rodada_e_uma_onda_propria(self):
        onda = OndaFalsa(self.ledger)
        self.correr(onda)
        self.assertEqual([Path(c["PASTA"]).name for c in onda.chamadas], ["RODADA-01", "RODADA-02", "RODADA-03"])
        for n in (1, 2, 3):
            self.assertTrue((self.base / ("RODADA-%02d" % n) / "TETO-ONDA.json").exists())

    def test_relatorio_pedido_com_o_estado_da_rodada(self):
        self.correr(OndaFalsa(self.ledger))
        self.assertEqual([Path(x).parent.name for x in self.rel.chamadas], ["RODADA-01", "RODADA-02", "RODADA-03"])
        self.assertTrue(all(x.endswith("ONDA-WEB-ESTADO.json") for x in self.rel.chamadas))


class AsParagens(Base):
    def test_transporte_avariado_acima_de_5_para_tudo(self):
        onda = OndaFalsa(self.ledger, desobedece_na_rodada=1)
        e = self.correr(onda)
        self.assertEqual(e["RODADAS"]["1"]["ESTADO"], "PARADA")
        self.assertEqual(e["RODADAS"]["1"]["PORQUE"], "PROVA_TETO_FAIL")
        self.assertEqual(len(onda.chamadas), 1)                     # a 2.a nao correu
        self.assertEqual(e["PAROU_NA_RODADA"], 1)
        self.assertGreater(_por_dominio(CONTAGEM)["a.test"], 5)     # o servidor viu o excesso; a prova tambem

    def test_linha_em_falta_e_nao_sei_e_para(self):
        e = self.correr(OndaFalsa(self.ledger, sem_linha_na_rodada=2))
        self.assertEqual(e["RODADAS"]["1"]["ESTADO"], "FECHADA")
        self.assertEqual(e["RODADAS"]["2"]["PORQUE"], "PROVA_TETO_NAO_SEI")
        self.assertNotIn("3", e["RODADAS"])

    def test_egresso_antes_falha_e_nada_se_pede(self):
        onda = OndaFalsa(self.ledger)
        e = self.correr(onda, portao=Portao(falha_na_chamada=1))
        self.assertEqual(e["RODADAS"]["1"]["PORQUE"], "EGRESSO_ANTES")
        self.assertEqual(onda.chamadas, [])
        self.assertEqual(CONTAGEM, {})

    def test_egresso_depois_falha_e_para(self):
        onda = OndaFalsa(self.ledger)
        e = self.correr(onda, portao=Portao(falha_na_chamada=2))
        self.assertEqual(e["RODADAS"]["1"]["PORQUE"], "EGRESSO_DEPOIS")
        self.assertEqual(len(onda.chamadas), 1)

    def test_onda_com_codigo_de_erro_nao_fecha(self):
        e = self.correr(OndaFalsa(self.ledger, codigo=1))
        self.assertEqual(e["RODADAS"]["1"]["PORQUE"], "ONDA_PAROU")

    def test_plano_de_outra_coorte_recusa(self):
        self.plano["COORTE_SHA256"] = "ff" * 32
        with self.assertRaises(SystemExit):
            self.correr(OndaFalsa(self.ledger))


class ARetoma(Base):
    def test_retoma_da_primeira_que_nao_fechou_sem_repetir(self):
        onda = OndaFalsa(self.ledger, sem_linha_na_rodada=2)
        self.correr(onda)                                           # 1 fecha, 2 para
        pedidos_1 = _por_dominio(CONTAGEM)
        onda2 = OndaFalsa(self.ledger)
        e = self.correr(onda2)
        self.assertEqual([Path(c["PASTA"]).name for c in onda2.chamadas], ["RODADA-02", "RODADA-03"])
        self.assertTrue(onda2.chamadas[0]["RETOMAR"])                # a MESMA onda, o mesmo livro
        self.assertFalse(onda2.chamadas[1]["RETOMAR"])
        self.assertEqual(e["PAROU_NA_RODADA"], None)
        # a 2.a retomada nao pede de novo o que o livro ja conta: a.test fica em 5 nessa rodada
        self.assertEqual(json.loads((self.base / "RODADA-02" / "TETO-ONDA.json").read_text())["PEDIDOS_POR_DOMINIO"]["a.test"], 5)
        self.assertEqual(_por_dominio(CONTAGEM)["a.test"] - pedidos_1["a.test"], 5)   # so a 3.a

    def test_rodada_n_so_corre_essa(self):
        onda = OndaFalsa(self.ledger)
        e = self.correr(onda, rodada=2)
        self.assertEqual([Path(c["PASTA"]).name for c in onda.chamadas], ["RODADA-02"])
        self.assertEqual(set(e["RODADAS"]), {"2"})

    def test_rodada_inexistente_recusa(self):
        with self.assertRaises(SystemExit):
            self.correr(OndaFalsa(self.ledger), rodada=9)


class OTetoDoDia(Base):
    def _livro_de_hoje(self, pedidos):
        p = self.tmp / "ondas" / "ONDA3-DE-HOJE"
        p.mkdir(parents=True)
        (p / "TETO-ONDA.json").write_text(json.dumps({"PEDIDOS_POR_DOMINIO": pedidos}), encoding="utf-8")

    def test_sem_teto_dia_nada_muda(self):
        self._livro_de_hoje({"a.test": 5, "b.test": 5, "c.test": 5})
        onda = OndaFalsa(self.ledger)
        self.correr(onda, rodada=1)
        self.assertEqual(onda.chamadas[0]["FONTES"], ["IT-T8-001", "IT-T7-001", "IT-T2-001", "IT-T2-002"])

    def test_teto_dia_adia_o_dominio_que_ja_gastou_hoje(self):
        self._livro_de_hoje({"a.test": 5})
        onda = OndaFalsa(self.ledger)
        e = self.correr(onda, rodada=1, teto_dia=8)
        self.assertEqual(onda.chamadas[0]["FONTES"], ["IT-T7-001", "IT-T2-001", "IT-T2-002"])
        self.assertEqual([a["SOURCE_ID"] for a in e["RODADAS"]["1"]["ADIADAS_TETO_DIA"]], ["IT-T8-001"])
        self.assertNotIn("a.test", _por_dominio(CONTAGEM))

    def test_teto_dia_soma_as_rodadas_de_hoje(self):
        onda = OndaFalsa(self.ledger)
        e = self.correr(onda, teto_dia=5)                            # a 2.a rodada de a.test passaria 5 hoje
        self.assertEqual(e["RODADAS"]["1"]["ESTADO"], "FECHADA")
        self.assertEqual(e["RODADAS"]["2"]["PORQUE"], "TETO_DIA")
        self.assertEqual(_por_dominio(CONTAGEM)["a.test"], 5)

    def test_livro_de_outro_dia_nao_conta(self):
        self._livro_de_hoje({"a.test": 5})
        f = self.tmp / "ondas" / "ONDA3-DE-HOJE" / "TETO-ONDA.json"
        ontem = datetime(2020, 1, 1).timestamp()
        os.utime(f, (ontem, ontem))
        self.assertEqual(R.gasto_do_dia(self.tmp / "ondas", date.today()), {})

    def test_limiar_do_dia_exacto(self):
        f = [{"SOURCE_ID": "X", "DOMINIO": "x.it", "PREVISTOS": 3}]
        self.assertEqual(len(R.filtrar_pelo_dia(f, {"x.it": 5}, 8)[0]), 1)
        self.assertEqual(len(R.filtrar_pelo_dia(f, {"x.it": 6}, 8)[0]), 0)


class AJanelaDe24h(Base):
    """D79: 1 rodada por janela movel de 24 h por dominio, lida dos livros (hora do RUN_ID, UTC)."""

    T = datetime(2026, 9, 25, 22, 58, 0, tzinfo=timezone.utc)

    def _onda_antiga(self, dominios_host, segundos=40, com_estado=True):
        p = self.tmp / "ondas" / "ONDA3-ANTIGA"
        p.mkdir(parents=True)
        gastos = {R.PT.dominio_registavel(h): 5 for h in dominios_host}
        (p / "TETO-ONDA.json").write_text(json.dumps({"PEDIDOS_POR_DOMINIO": gastos}), encoding="utf-8")
        if com_estado:
            fontes = [{"SOURCE_ID": "IT-T9-9%02d" % i, "CORREU": True, "SEGUNDOS": segundos,
                       "RUN_ID": "IT-T9-%s-%s" % (self.T.strftime("%Y-%m-%d-%H%M%S"), "ab" * 8),
                       "PEDIDOS_POR_DOMINIO": {R.PT.dominio_registavel(h): 5}} for i, h in enumerate(dominios_host)]
            (p / "ONDA-WEB-ESTADO.json").write_text(json.dumps({"FONTES": fontes}), encoding="utf-8")
        return p

    def test_dominio_visitado_ha_menos_de_24h_para_a_rodada_inteira(self):
        self._onda_antiga(["a.test"])
        onda = OndaFalsa(self.ledger)
        e = self.correr(onda, rodada=1, janela_h=24, agora_utc=self.T + timedelta(hours=23))
        self.assertEqual(e["RODADAS"]["1"]["PORQUE"], "JANELA_24H")
        self.assertEqual(onda.chamadas, [])
        self.assertEqual(CONTAGEM, {})
        self.assertEqual(e["RODADAS"]["1"]["ABRE_EM"], (self.T + timedelta(hours=24, seconds=40)).isoformat())

    def test_a_janela_conta_do_fim_da_corrida(self):
        self._onda_antiga(["a.test"], segundos=40)
        onda = OndaFalsa(self.ledger)
        e = self.correr(onda, rodada=1, janela_h=24, agora_utc=self.T + timedelta(hours=24, seconds=30))
        self.assertEqual(e["RODADAS"]["1"]["PORQUE"], "JANELA_24H")      # 24 h do inicio, mas nao do fim
        e = self.correr(onda, rodada=1, janela_h=24, agora_utc=self.T + timedelta(hours=24, seconds=41))
        self.assertEqual(e["RODADAS"]["1"]["ESTADO"], "FECHADA")

    def test_sem_estado_vale_a_hora_do_livro(self):
        p = self._onda_antiga(["a.test"], com_estado=False)
        t = (self.T + timedelta(hours=2)).timestamp()
        os.utime(p / "TETO-ONDA.json", (t, t))
        e = self.correr(OndaFalsa(self.ledger), rodada=1, janela_h=24, agora_utc=self.T + timedelta(hours=25))
        self.assertEqual(e["RODADAS"]["1"]["PORQUE"], "JANELA_24H")      # o livro e de T+2h: abre as T+26h

    def test_dominio_fora_da_rodada_nao_prende(self):
        self._onda_antiga(["outro.test"])
        e = self.correr(OndaFalsa(self.ledger), rodada=1, janela_h=24, agora_utc=self.T + timedelta(hours=1))
        self.assertEqual(e["RODADAS"]["1"]["ESTADO"], "FECHADA")

    def test_rodadas_seguidas_do_mesmo_dominio_esperam_24h(self):
        onda = OndaFalsa(self.ledger)
        onda.quando = self.T
        e = self.correr(onda, janela_h=24, agora_utc=self.T)
        self.assertEqual(e["RODADAS"]["1"]["ESTADO"], "FECHADA")
        self.assertEqual(e["RODADAS"]["2"]["PORQUE"], "JANELA_24H")      # a.test acabou de ser pedido
        onda.quando = self.T + timedelta(hours=25)
        e = self.correr(onda, janela_h=24, agora_utc=self.T + timedelta(hours=25))
        self.assertEqual(e["RODADAS"]["2"]["ESTADO"], "FECHADA")
        self.assertEqual(e["RODADAS"]["3"]["PORQUE"], "JANELA_24H")

    def test_sem_janela_nada_muda(self):
        self._onda_antiga(["a.test", "b.test", "c.test"])
        e = self.correr(OndaFalsa(self.ledger), rodada=1, agora_utc=self.T)
        self.assertEqual(e["RODADAS"]["1"]["ESTADO"], "FECHADA")

    def test_run_id_e_utc(self):
        self._onda_antiga(["a.test"], segundos=0)
        self.assertEqual(R.ultima_visita_por_dominio(self.tmp / "ondas")["a.test"], self.T)


class ORodadaIncompletaNaoPerdeNinguem(Base):
    def test_adiada_pelo_teto_dia_corre_na_retoma_e_so_ela(self):
        p = self.tmp / "ondas" / "ONDA3-DE-HOJE"
        p.mkdir(parents=True)
        (p / "TETO-ONDA.json").write_text(json.dumps({"PEDIDOS_POR_DOMINIO": {"a.test": 5}}), encoding="utf-8")
        onda = OndaFalsa(self.ledger)
        e = self.correr(onda, rodada=1, teto_dia=8)
        self.assertEqual(e["RODADAS"]["1"]["ESTADO"], "INCOMPLETA")
        self.assertEqual(e["RODADAS"]["1"]["FALTAM"], ["IT-T8-001"])
        (p / "TETO-ONDA.json").unlink()                                   # «amanha»: o livro de ontem sai
        e = self.correr(onda, rodada=1, teto_dia=8)
        self.assertEqual(onda.chamadas[-1]["FONTES"], ["IT-T8-001"])
        self.assertTrue(onda.chamadas[-1]["RETOMAR"])
        self.assertEqual(e["RODADAS"]["1"]["ESTADO"], "FECHADA")
        self.assertEqual(sorted(e["RODADAS"]["1"]["FEITAS"]), ["IT-T2-001", "IT-T2-002", "IT-T7-001", "IT-T8-001"])


if __name__ == "__main__":
    unittest.main()
