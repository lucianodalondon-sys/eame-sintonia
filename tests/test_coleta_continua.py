# -*- coding: utf-8 -*-
"""COLETA-CONTINUA (D86, 27/09/2026): o agendador por FONTE, contra um SERVIDOR LOCAL que conta.

Zero rede externa: o servidor e 127.0.0.1; a onda falsa pede com o cabecalho Host de cada fonte e sem
proxy. A onda falsa faz o que o transporte faz com o contador multicanal (D90): RESERVA cada pedido no
livro de 24 h (`coleta/reserva_24h.py`, o mesmo codigo) e so pede com RESERVADO; escreve o livro da onda
(TETO-ONDA.json), a linha em runs.ndjson (CORTESIA.PEDIDOS_POR_HOST) e o ONDA-WEB-ESTADO.json com a Sala
antes/depois. O modo DESOBEDECE ignora o livro: e o transporte avariado que a PROVA-TETO tem de apanhar.
O robo e um falso com vida propria (vivo/parado) e a flag num ficheiro temporario.

    py tests/test_coleta_continua.py

D124 (dono, 27/09) — AJUSTE DECLARADO (D124-REBASE, 28/09): o 5 fixo e a janela D79 deixaram de ser a regra
(o teto de cada dominio e o ORCAMENTO VIGENTE da cortesia adaptativa; a janela so com --janela-24h), e o
contador de 24 h passou a ser 1 pedido de cada vez (a reserva so fecha com a RESPOSTA registada). Estes testes
provam a MECANICA do agendador (esperar, repartir, somar as linhas, provar, parar) e continuam a faze-lo:
  · com o teto MANUAL declarado SINTONIA_TETO_POR_HOST=5, que o servico continua a respeitar;
  · com a janela LIGADA de proposito (`janela_h=24` no helper `ciclo`), como `--janela-24h` a liga;
  · com a onda falsa a REGISTAR a resposta de cada pedido (`cortesia_adaptativa.registrar_resposta`),
    como o transporte real faz desde a D124, e com a pausa minima da classe a 0 numa copia da politica
    (a pausa e medida em tests/test_cortesia_adaptativa.py e provas/cortesia_http_local.mjs, nao aqui).
Nenhuma asserção foi afrouxada. O comportamento SEM estes ajustes (orcamento vigente, janela desligada,
livro D90 migrado, sonda da linha SITES) esta em tests/test_teto_adaptativo_rebase.py.
"""
import http.server
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
import coleta_continua as C  # noqa: E402
import rodadas as R  # noqa: E402

R24 = C.R24
CA = C.CA
CONTAGEM: dict = {}
_AMBIENTE_ANTES: dict = {}


def setUpModule():
    """D124 — AJUSTE DECLARADO (ver o cabecalho): teto manual 5 e a pausa minima da classe a 0."""
    for k in ("SINTONIA_TETO_POR_HOST", "SINTONIA_CORTESIA_POLITICA", "SINTONIA_CORTESIA_LIVRO"):
        _AMBIENTE_ANTES[k] = os.environ.get(k)
    os.environ["SINTONIA_TETO_POR_HOST"] = "5"
    os.environ.pop("SINTONIA_CORTESIA_LIVRO", None)
    pol = json.loads(CA.POLITICA_F.read_text(encoding="utf-8"))
    for c in ("SITE", "PLATAFORMA_GRANDE"):
        pol["CLASSES"][c]["PAUSA_MINIMA_S"] = 0
    f = Path(tempfile.mkdtemp(prefix="coleta-continua-pol-")) / "POLITICA.json"
    f.write_text(json.dumps(pol), encoding="utf-8")
    os.environ["SINTONIA_CORTESIA_POLITICA"] = str(f)


def tearDownModule():
    pf = os.environ.get("SINTONIA_CORTESIA_POLITICA")
    for k, v in _AMBIENTE_ANTES.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    if pf:
        shutil.rmtree(Path(pf).parent, ignore_errors=True)
    CA.politica(recarregar=True)


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
SHA = "c0" * 32

# fonte -> (host, pedidos que a fonte quer fazer). Espelha a 4.a onda: edagricole com 3 fontes, cia 2,
# crea com 2 (T5), enea 1, e x.test para as duas linhas.
FONTES = {
    "IT-T8-021": ("www.edagricole.test", 5), "IT-T8-022": ("edagricole.test", 5), "IT-T8-024": ("edagricole.test", 5),
    "IT-T7-112": ("www.cia.test", 5), "IT-T7-118": ("cia.test", 5),
    "IT-T5-080": ("www.crea.test", 5), "IT-T5-111": ("crea.test", 5),
    "IT-T5-187": ("www.enea.test", 5),
    "IT-T6-001": ("api.x.test", 3), "IT-T6-002": ("x.test", 3), "IT-T6-003": ("y.test", 1),
    "IT-T9-001": ("um.test", 5), "IT-T9-002": ("dois.test", 1),
}


def _dom(s):
    return R.PT.dominio_registavel(FONTES[s][0])


def _plano(rodadas):
    """Um RODADAS-PLANO como o do disparador: [[SOURCE_ID, ...], ...] -> rodadas com PREVISTOS e DOMINIOS."""
    return {"COORTE_SHA256": SHA, "RODADAS": [
        {"RODADA": i, "FONTES": [{"SOURCE_ID": s, "DOMINIO": _dom(s), "PREVISTOS": FONTES[s][1], "DOMINIOS": [_dom(s)]}
                                 for s in fs]} for i, fs in enumerate(rodadas, 1)]}


def _por_dominio(cont):
    out = {}
    for h, n in cont.items():
        d = R.PT.dominio_registavel(h)
        out[d] = out.get(d, 0) + n
    return out


class Sala:
    """A Sala falsa: cada corrida que pede deixa 1 collection_run, 1 raw_asset e 1 sala_de_espera."""

    def __init__(self):
        self.linhas = {"collection_run": [], "raw_asset": [], "sala_de_espera": []}
        self.mente = False

    def foto(self):
        return {t: {"LINHAS": len(v)} for t, v in self.linhas.items()}

    def grava(self, rid):
        for t in self.linhas:
            self.linhas[t].append(rid)
        if self.mente:
            self.linhas["sala_de_espera"].append("FANTASMA")

    def reconciliar(self, run_ids, antes, depois):
        n = {t: sum(1 for r in v if r in set(run_ids)) for t, v in self.linhas.items()}
        return C.comparar_sala(n, antes, depois)


class OndaFalsa:
    """O papel de `onda_web.py --correr` numa linha de um ciclo: pedidos HTTP de verdade ao servidor local."""

    def __init__(self, ledger, sala, desobedece=False, codigo=0):
        self.ledger, self.sala, self.desobedece, self.codigo = ledger, sala, desobedece, codigo
        self.chamadas = []

    def __call__(self, sha, fontes, pasta, historico, retomar):
        self.chamadas.append({"FONTES": list(fontes), "PASTA": str(pasta)})
        pasta.mkdir(parents=True, exist_ok=True)
        livro_f = pasta / "TETO-ONDA.json"
        livro = {}
        estado = {"FONTES": [], "PAROU": None, "SALA_INICIO": self.sala.foto()}
        for s in fontes:
            host, quer = FONTES[s]
            rid = "%s-%s-%s" % (s.rsplit("-", 1)[0], datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S"),
                                secrets.token_hex(8))
            feitos = 0
            for _ in range(quer):
                if not self.desobedece and R24.reservar(host, 1, run_id=rid, linha="TESTE")["ESTADO"] != "RESERVADO":
                    break                                  # o transporte: sem reserva, o pedido nao sai
                rq = urllib.request.Request("http://127.0.0.1:%d/" % PORTA, headers={"Host": host})
                SEM_PROXY.open(rq, timeout=10).read()
                if not self.desobedece:                    # D124: o transporte regista a resposta (fecha a reserva)
                    CA.registrar_resposta(host, 200, {}, run_id=rid, linha="TESTE")
                feitos += 1
            d = R.PT.dominio_registavel(host)
            livro[d] = livro.get(d, 0) + feitos
            livro_f.write_text(json.dumps({"PEDIDOS_POR_DOMINIO": livro}), encoding="utf-8")
            with open(self.ledger, "a", encoding="utf-8") as f:
                f.write(json.dumps({"RUN_ID": rid, "CORTESIA": {"PEDIDOS_POR_HOST": {host: feitos}}}) + "\n")
            if feitos:
                self.sala.grava(rid)
            estado["FONTES"].append({"SOURCE_ID": s, "CORREU": feitos > 0, "RUN_ID": rid,
                                     "PEDIDOS_POR_DOMINIO": {d: feitos}})
        estado["SALA_FIM"] = self.sala.foto()
        (pasta / "ONDA-WEB-ESTADO.json").write_text(json.dumps(estado), encoding="utf-8")
        return self.codigo


class Portao:
    def __init__(self, falha_na_chamada=None):
        self.n, self.falha = 0, falha_na_chamada

    def __call__(self):
        self.n += 1
        return {"PASSA": self.n != self.falha, "PAIS": "IT" if self.n != self.falha else "BR"}


class Robo:
    """O robo falso: vivo/parado, a flag num ficheiro. `teimoso` nao para; `nao_volta` nao arranca."""

    def __init__(self, flag, vivo=True, teimoso=False, nao_volta=False, nao_sei=False):
        self.flag, self.vivo, self.teimoso, self.nao_volta, self.nao_sei = flag, vivo, teimoso, nao_volta, nao_sei
        self.eventos = []

    def estado(self):
        return {"VIVO": None if self.nao_sei else self.vivo, "FLAG": self.flag.exists()}

    def parar(self):
        self.eventos.append("PARAR")
        self.flag.write_text("x", encoding="utf-8")
        if not self.teimoso:
            self.vivo = False

    def tirar_flag(self):
        self.eventos.append("TIRAR_FLAG")
        self.flag.unlink(missing_ok=True)

    def lancar(self):
        self.eventos.append("LANCAR")
        if not self.nao_volta and not self.flag.exists():
            self.vivo = True

    def esperar(self, vivo):
        return self.vivo is vivo


def _ligada(linha):
    return {"LIGADA": True, "PORQUE": "teste"}


def _admite_tudo(ids):
    """O portao da Collection falso: admite todas. As fontes destes testes (IT-T9-001, ...) nao estao no livro
    canonico; o que o portao recusa mede-se na classe AdendoParada, com o falso que recusa e com o real."""
    return {s: {"COLLECTION_ELIGIBLE": True, "STATE": "READY_FOR_COLLECTION", "MOTIVO": "ELIGIBLE"} for s in ids}


class Base(unittest.TestCase):
    def setUp(self):
        CONTAGEM.clear()
        self.tmp = Path(tempfile.mkdtemp(prefix="coleta-continua-"))
        self.base = self.tmp / "ondas" / "COLETA-CONTINUA"
        self.base.mkdir(parents=True)
        self.ledger = self.tmp / "runs.ndjson"
        self.livro24 = self.tmp / "TETO-24H.json"
        self.env_antes = os.environ.get("SINTONIA_TETO_24H")
        os.environ["SINTONIA_TETO_24H"] = str(self.livro24)
        os.environ.pop("SINTONIA_CORTESIA_LIVRO", None)            # D124: o ciclo anterior deixou-o no ambiente
        self.sala = Sala()
        self.onda = OndaFalsa(self.ledger, self.sala)
        self.robo = Robo(self.tmp / "PARAR.flag")
        self.backups = []
        self.ram = 12.0

    def tearDown(self):
        os.environ.pop("SINTONIA_CORTESIA_LIVRO", None)
        if self.env_antes is None:
            os.environ.pop("SINTONIA_TETO_24H", None)
        else:
            os.environ["SINTONIA_TETO_24H"] = self.env_antes
        shutil.rmtree(self.tmp, ignore_errors=True)

    def pecas(self, **kw):
        p = {"portao": Portao(), "onda": self.onda, "relatorio": lambda e, s: 0, "ledger": self.ledger,
             "ram": lambda: self.ram, "backup": self._backup, "robo": self.robo, "reconciliar": self.sala.reconciliar,
             "fonte": _admite_tudo}
        p.update(kw)
        return p

    def _backup(self, pasta):
        self.backups.append(str(pasta))
        return {"PROVA_VALE": True}

    def ciclo(self, cands, pecas=None, **kw):
        kw.setdefault("livro_24h", self.livro24)
        kw.setdefault("ligacao", _ligada)
        kw.setdefault("janela_h", 24)                              # D124: a janela D79 LIGADA de proposito
        return C.ciclo(self.base, SHA, cands, pecas=pecas or self.pecas(), **kw)

    def sites(self, *rodadas):
        return {"SITES": C.candidatas_do_plano(_plano(list(rodadas)))}

    def visitar(self, dominio, horas_atras):
        """Um livro de uma onda anterior (como os de ~/sintonia-sala-italia/ondas) com uma visita ha N horas."""
        p = self.tmp / "ondas" / ("ANTIGA-%s-%d" % (dominio, horas_atras))
        p.mkdir(parents=True)
        t = datetime.now(timezone.utc) - timedelta(hours=horas_atras)
        (p / "TETO-ONDA.json").write_text(json.dumps({"PEDIDOS_POR_DOMINIO": {dominio: 5}}), encoding="utf-8")
        (p / "ONDA-WEB-ESTADO.json").write_text(json.dumps({"FONTES": [{"SOURCE_ID": "IT-T8-900", "CORREU": True,
            "RUN_ID": "IT-T8-%s-%s" % (t.strftime("%Y-%m-%d-%H%M%S"), "ab" * 8),
            "PEDIDOS_POR_DOMINIO": {dominio: 5}}]}), encoding="utf-8")


# ── 1. o agendador por fonte: dominio bloqueado espera, os outros seguem ─────
class AgendadorPorFonte(Base):
    def test_dominio_bloqueado_espera_e_as_outras_seguem(self):
        """O caso da NOITE-20260927-2023: a rodada tem edagricole (fechado) + crea (livre)."""
        self.visitar("edagricole.test", 2)
        r = self.ciclo(self.sites(["IT-T8-022", "IT-T5-080"], ["IT-T8-024", "IT-T5-111"]))
        self.assertIsNone(r["PARA"], r)
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], ["IT-T5-080"])
        self.assertEqual(_por_dominio(CONTAGEM), {"crea.test": 5})
        self.assertNotIn("edagricole.test", _por_dominio(CONTAGEM))
        esp = {e["SOURCE_ID"]: e for e in r["ESPERAM"]}
        self.assertEqual(esp["IT-T8-022"]["DOMINIOS_FECHADOS"]["edagricole.test"]["PORQUE"], "JANELA_24H")
        self.assertEqual(esp["IT-T5-111"]["DOMINIOS_FECHADOS"]["crea.test"]["PORQUE"], "TETO_NO_CICLO")

    def test_o_disparador_por_rodada_prende_a_mesma_fonte(self):
        """Contraprova: o mesmo plano pelo `rodadas.correr_rodadas` PARA JANELA_24H e nao pede nada."""
        self.visitar("edagricole.test", 2)
        plano = _plano([["IT-T8-022", "IT-T5-080"]])
        chamadas = []
        (self.base / "R").mkdir()
        e = R.correr_rodadas(self.base / "R", SHA, plano, onda=lambda *a: chamadas.append(a) or 0, portao=Portao(),
                             relatorio=lambda *a: 0, ledger=self.ledger, janela_h=24, livros_do_dia=self.tmp / "ondas")
        self.assertEqual(e["RODADAS"]["1"]["PORQUE"], "JANELA_24H")
        self.assertEqual(chamadas, [])

    def test_dominio_visitado_ha_mais_de_24h_esta_livre(self):
        self.visitar("edagricole.test", 25)
        r = self.ciclo(self.sites(["IT-T8-022"]))
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], ["IT-T8-022"])

    def test_o_ciclo_seguinte_ve_o_dominio_que_este_acabou_de_visitar(self):
        cands = self.sites(["IT-T8-022", "IT-T5-080"], ["IT-T8-024"])
        self.ciclo(cands)
        r2 = self.ciclo(cands)
        self.assertEqual(r2["LINHAS"]["SITES"]["FONTES"], [])
        self.assertTrue(r2["NADA_A_CORRER"])
        self.assertEqual(_por_dominio(CONTAGEM), {"edagricole.test": 5, "crea.test": 5})

    def test_teto_6_no_mesmo_dominio_nao_entra_no_ciclo(self):
        """5 + 1 no mesmo dominio: o segundo espera (5 e o teto; 6 nunca)."""
        cands = {"SITES": [dict(c) for c in C.candidatas_do_plano(_plano([["IT-T9-001", "IT-T9-002"]]))]}
        cands["SITES"][1].update(DOMINIO="um.test", DOMINIOS=["um.test"])
        r = self.ciclo(cands)
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], ["IT-T9-001"])
        self.assertEqual(r["ORCAMENTO_DO_CICLO"], {"um.test": 5})

    def test_limiar_exato_3_mais_2_cabe(self):
        e = C.escolher([{"SOURCE_ID": "A", "DOMINIO": "z.test", "PREVISTOS": 3, "DOMINIOS": ["z.test"]},
                        {"SOURCE_ID": "B", "DOMINIO": "z.test", "PREVISTOS": 2, "DOMINIOS": ["z.test"]},
                        {"SOURCE_ID": "C", "DOMINIO": "z.test", "PREVISTOS": 1, "DOMINIOS": ["z.test"]}],
                       feitas=[], ultima={}, reservas=[], agora_utc=datetime.now(timezone.utc), orcamento={})
        self.assertEqual([c["SOURCE_ID"] for c in e["CORREM"]], ["A", "B"])

    def test_o_livro_de_24h_de_outra_linha_fecha_o_dominio(self):
        """D90: 3 pedidos de outra linha no livro partilhado; a fonte que quer 5 espera, com a hora certa."""
        t = datetime.now(timezone.utc).timestamp() - 3600
        self.livro24.write_text(json.dumps({"RESERVAS": [{"DOMINIO": "crea.test", "QTD": 3, "EM": t,
                                                          "RUN_ID": "X", "LINHA": "CIENCIA"}]}), encoding="utf-8")
        r = self.ciclo(self.sites(["IT-T5-080"]))
        e = r["ESPERAM"][0]["DOMINIOS_FECHADOS"]["crea.test"]
        self.assertEqual(e["PORQUE"], "TETO_24H")
        self.assertEqual(e["ABRE_EM"], datetime.fromtimestamp(t + 24 * 3600, timezone.utc).isoformat(timespec="seconds"))
        self.assertEqual(CONTAGEM, {})

    def test_todos_os_dominios_da_fonte_contam(self):
        """IT-T7-172 pede georgofili.info e cai em georgofili.it: o dominio do redireccionamento fecha a fonte."""
        e = C.escolher([{"SOURCE_ID": "IT-T7-172", "DOMINIO": "georgofili.info", "PREVISTOS": 2,
                         "DOMINIOS": ["georgofili.info", "georgofili.it"]}], feitas=[],
                       ultima={"georgofili.it": datetime.now(timezone.utc) - timedelta(hours=1)}, reservas=[],
                       agora_utc=datetime.now(timezone.utc), orcamento={})
        self.assertEqual(e["CORREM"], [])
        self.assertIn("georgofili.it", e["ESPERAM"][0]["DOMINIOS_FECHADOS"])

    def test_a_ordem_do_plano_manda(self):
        e = C.escolher(C.candidatas_do_plano(_plano([["IT-T8-021", "IT-T7-112"], ["IT-T8-022", "IT-T7-118"]])),
                       feitas=[], ultima={}, reservas=[], agora_utc=datetime.now(timezone.utc), orcamento={})
        self.assertEqual([c["SOURCE_ID"] for c in e["CORREM"]], ["IT-T8-021", "IT-T7-112"])

    def test_feitas_nao_se_repetem_e_a_passagem_recomeca(self):
        cands = self.sites(["IT-T5-080"])
        self.ciclo(cands)
        est = C.ler_estado(self.base)
        self.assertEqual(est["LINHAS"]["SITES"]["FEITAS_NA_PASSAGEM"], ["IT-T5-080"])
        # depois de 24 h, a coorte da linha acabou: nova passagem, a fonte volta
        r = self.ciclo(cands, agora_utc=datetime.now(timezone.utc) + timedelta(hours=25))
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], ["IT-T5-080"])
        self.assertEqual(C.ler_estado(self.base)["LINHAS"]["SITES"]["PASSAGEM"], 2)

    def test_feita_nao_volta_na_mesma_passagem(self):
        self.ciclo(self.sites(["IT-T5-080"]))
        r = self.ciclo(self.sites(["IT-T5-080", "IT-T5-111"]), agora_utc=datetime.now(timezone.utc) + timedelta(hours=25))
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], ["IT-T5-111"])

    def test_a_onda_herda_o_livro_de_24h(self):
        """D90: o servico poe o livro no ambiente da onda (onda_web -> orquestrador -> executor -> node)."""
        os.environ.pop("SINTONIA_TETO_24H", None)
        visto = []
        onda = self.onda

        def espia(*a):
            visto.append((os.environ.get("SINTONIA_TETO_24H"), os.environ.get("SINTONIA_CORTESIA_LIVRO")))
            return onda(*a)
        r = self.ciclo(self.sites(["IT-T5-080"]), pecas=self.pecas(onda=espia))
        self.assertIsNone(r["PARA"], r)
        # D124: os DOIS nomes (o novo manda no livro da cortesia; so o antigo partia o contador em dois)
        self.assertEqual(visto, [(str(self.livro24), str(self.livro24))])
        self.assertEqual(_por_dominio(CONTAGEM), {"crea.test": 5})

    def test_feitas_do_disparador_por_rodada(self):
        er = {"RODADAS": {"1": {"ESTADO": "FECHADA", "FONTES": ["A", "B"], "FEITAS": []},
                          "2": {"ESTADO": "INCOMPLETA", "FEITAS": ["C"], "FONTES": ["C"]},
                          "4": {"ESTADO": "PARADA", "FEITAS": [], "FONTES": ["D"]}}}
        self.assertEqual(C.feitas_das_rodadas(er), ["A", "B", "C"])

    def test_proximo_a_abrir(self):
        self.visitar("edagricole.test", 2)
        self.visitar("cia.test", 5)
        r = self.ciclo(self.sites(["IT-T8-022", "IT-T7-112"]))
        self.assertEqual(r["PROXIMO_A_ABRIR"]["DOMINIO"], "cia.test")
        self.assertTrue(r["NADA_A_CORRER"])


# ── 2. as linhas (D86-b/c): cada uma o seu contador, o dominio e partilhado ──
class Linhas(Base):
    def duas(self):
        a = C.candidatas_do_plano(_plano([["IT-T6-001"]]), "A")
        b = C.candidatas_do_plano(_plano([["IT-T6-002", "IT-T6-003"]]), "B")
        return {"A": a, "B": b}

    def test_duas_linhas_nao_somam_6_no_mesmo_dominio(self):
        r = self.ciclo(self.duas())
        self.assertIsNone(r["PARA"], r)
        self.assertEqual(_por_dominio(CONTAGEM).get("x.test"), 3)
        self.assertEqual(r["ORCAMENTO_DO_CICLO"]["x.test"], 3)
        quem = [n for n in ("A", "B") if any(s in ("IT-T6-001", "IT-T6-002") for s in r["LINHAS"][n]["FONTES"])]
        self.assertEqual(len(quem), 1)
        self.assertEqual([e["SOURCE_ID"] for e in r["ESPERAM"]], ["IT-T6-002" if quem == ["A"] else "IT-T6-001"])

    def test_o_rodizio_muda_quem_abre_o_ciclo(self):
        self.assertEqual(C.ordem_das_linhas(["A", "B", "C"], 1), ["B", "C", "A"])
        self.assertEqual(C.ordem_das_linhas(["A", "B", "C"], 2), ["C", "A", "B"])
        r1 = self.ciclo(self.duas())
        self.assertEqual(r1["LINHAS"]["B"]["FONTES"], ["IT-T6-002", "IT-T6-003"])     # ciclo 1: B abre
        self.assertEqual(r1["LINHAS"]["A"]["FONTES"], [])

    def test_cada_linha_tem_o_seu_contador(self):
        self.ciclo(self.duas())
        est = C.ler_estado(self.base)["LINHAS"]
        self.assertEqual(est["B"]["FONTES_TOTAL"], 2)
        self.assertEqual(est["B"]["PEDIDOS_TOTAL"], 4)
        self.assertNotIn("A", est)                                   # A nao correu: o contador dela nao mexe

    def test_as_linhas_em_paralelo_partilham_o_orcamento(self):
        c = self.duas()
        c["C"] = C.candidatas_do_plano(_plano([["IT-T9-001"]]), "C")
        r = self.ciclo(c, paralelo=True)
        self.assertIsNone(r["PARA"], r)
        self.assertEqual(_por_dominio(CONTAGEM), {"x.test": 3, "y.test": 1, "um.test": 5})
        self.assertEqual(r["PROVA_TETO_CICLO"]["ESTADO"], "PASS")

    def test_linha_nao_ligada_ao_contador_nao_corre(self):
        c = self.duas()
        r = self.ciclo(c, ligacao=lambda l: {"LIGADA": l["LINHA"] == "A", "PORQUE": "medido"})
        self.assertEqual(r["LINHAS"]["B"]["ESTADO"], "ESPERA_LIGACAO")
        self.assertEqual(_por_dominio(CONTAGEM), {"x.test": 3})

    def test_ligacao_medida_no_codigo_desta_arvore(self):
        m = {l["LINHA"]: C.medir_ligacao(l) for l in C.LINHAS}
        self.assertTrue(m["SITES"]["LIGADA"], m["SITES"])
        # LIGACAO-4-LINHAS (30/09): as quatro linhas Python passaram a ser medidas pelo COMPORTAMENTO (a sonda
        # escreve a RESERVA no livro temporario e nao reserva com o dominio pausado). A BUSCA e a SOCIAL ja
        # reservavam por outra porta (scrap_http/teto_da_onda) e o texto dava-as como desligadas; a CIENCIA e a
        # PESQUISADORES ganharam a reserva que nao tinham. Nenhuma fica ESPERA_LIGACAO.
        for n in ("BUSCA", "CIENCIA", "SOCIAL", "PESQUISADORES"):
            self.assertTrue(m[n]["LIGADA"], (n, m[n]))
            self.assertEqual(m[n].get("MEDIDO", {}).get("RESERVAS_LIVRES"), 1, (n, m[n]))
            self.assertEqual(m[n].get("MEDIDO", {}).get("RESERVAS_NOVAS_B"), 0, (n, m[n]))

    def test_a_ligacao_e_a_chamada_nao_o_nome(self):
        d = self.tmp / "coleta"
        d.mkdir()
        (d / "t.py").write_text("# fala de reserva_24h mas nao chama\n", encoding="utf-8")
        l = {"LINHA": "Z", "TRANSPORTE": "coleta/t.py", "CHAMADA": "reserva_24h.reservar("}
        self.assertFalse(C.medir_ligacao(l, self.tmp)["LIGADA"])
        (d / "t.py").write_text("import reserva_24h\nr = reserva_24h.reservar(h, 1, run_id=x, linha='Z')\n", encoding="utf-8")
        self.assertTrue(C.medir_ligacao(l, self.tmp)["LIGADA"])


# ── 3. os portoes: PARA sozinho, e fica PARADO ───────────────────────────────
class Paragens(Base):
    def test_portao_it_antes_falha_zero_pedidos_e_robo_intacto(self):
        r = self.ciclo(self.sites(["IT-T5-080"]), pecas=self.pecas(portao=Portao(falha_na_chamada=1)))
        self.assertEqual(r["PARA"], "EGRESSO_ANTES")
        self.assertEqual(CONTAGEM, {})
        self.assertEqual(self.onda.chamadas, [])
        self.assertEqual(self.robo.eventos, [])
        self.assertEqual(self.backups, [])

    def test_portao_it_depois_falha_para(self):
        r = self.ciclo(self.sites(["IT-T5-080"]), pecas=self.pecas(portao=Portao(falha_na_chamada=2)))
        self.assertEqual(r["PARA"], "EGRESSO_DEPOIS")

    def test_parado_fica_parado_ate_rearmar(self):
        self.ciclo(self.sites(["IT-T5-080"]), pecas=self.pecas(portao=Portao(falha_na_chamada=1)))
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertTrue(r["PARA"].startswith("JA_PARADO"))
        self.assertEqual(CONTAGEM, {})
        with self.assertRaises(SystemExit):
            C.rearmar(self.base, "  ")
        C.rearmar(self.base, "coordenador leu EGRESSO_ANTES: VPN caiu, religada")
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertIsNone(r["PARA"], r)
        self.assertEqual(_por_dominio(CONTAGEM), {"crea.test": 5})

    def test_transporte_avariado_prova_teto_fail(self):
        self.onda.desobedece = True
        cands = {"SITES": [dict(c) for c in C.candidatas_do_plano(_plano([["IT-T9-001", "IT-T9-002"]]))]}
        FONTES["IT-T9-002"] = ("um.test", 1)            # o plano acha que sao dominios diferentes; o transporte pede ao mesmo
        try:
            r = self.ciclo(cands)
        finally:
            FONTES["IT-T9-002"] = ("dois.test", 1)
        self.assertEqual(r["PARA"], "PROVA_TETO_FAIL")
        self.assertEqual(r["PROVA_TETO_CICLO"]["DOMINIOS_ACIMA_DO_TETO"], {"um.test": 6})
        self.assertEqual(_por_dominio(CONTAGEM), {"um.test": 6})

    def test_linha_em_falta_no_livro_nao_sei(self):
        onda = self.onda

        def sem_ledger(*a):
            c = onda(*a)
            self.ledger.write_text("", encoding="utf-8")
            return c
        r = self.ciclo(self.sites(["IT-T5-080"]), pecas=self.pecas(onda=sem_ledger))
        self.assertEqual(r["PARA"], "PROVA_TETO_NAO_SEI")

    def test_prova_de_24h_apanha_o_que_o_ciclo_sozinho_nao_ve(self):
        """Dois ciclos no mesmo dominio dentro de 24 h (janela desligada por um livro sem hora): 5 + 5."""
        self.ciclo(self.sites(["IT-T5-080"]))
        for p in self.base.glob("CICLO-*/*/TETO-ONDA.json"):
            p.unlink()                                               # os livros das ondas sumiram
        os.environ["SINTONIA_TETO_24H"] = str(self.tmp / "OUTRO-24H.json")
        self.onda.desobedece = True
        r = self.ciclo(self.sites(["IT-T5-111"]), livro_24h=self.tmp / "OUTRO-24H.json")
        self.assertEqual(r["PROVA_TETO_CICLO"]["ESTADO"], "PASS")
        self.assertEqual(r["PARA"], "PROVA_TETO_24H_FAIL")

    def test_ram_abaixo_de_5gb_para_sem_pedir(self):
        self.ram = 4.9
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertEqual(r["PARA"], "RAM_ABAIXO_DE_5GB")
        self.assertEqual(CONTAGEM, {})
        self.assertEqual(self.robo.eventos, [])

    def test_ram_nao_sei_para(self):
        self.ram = None
        self.assertEqual(self.ciclo(self.sites(["IT-T5-080"]))["PARA"], "RAM_NAO_SEI")

    def test_ram_exatamente_5gb_corre(self):
        self.ram = 5.0
        self.assertIsNone(self.ciclo(self.sites(["IT-T5-080"]))["PARA"])

    def test_backup_sem_prova_vale_para_antes_do_robo(self):
        r = self.ciclo(self.sites(["IT-T5-080"]), pecas=self.pecas(backup=lambda p: {"PROVA_VALE": False}))
        self.assertEqual(r["PARA"], "BACKUP_SEM_PROVA_VALE")
        self.assertEqual(CONTAGEM, {})
        self.assertEqual(self.robo.eventos, [])

    def test_livro_24h_ilegivel_para(self):
        self.livro24.write_text("{partido", encoding="utf-8")
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertEqual(r["PARA"], "LIVRO_24H_NAO_SEI")
        self.assertEqual(CONTAGEM, {})

    def test_sem_livro_24h_para(self):
        r = self.ciclo(self.sites(["IT-T5-080"]), livro_24h=None)
        self.assertEqual(r["PARA"], "LIVRO_24H_NAO_SEI")

    def test_onda_com_codigo_de_erro_para(self):
        self.onda.codigo = 1
        self.assertEqual(self.ciclo(self.sites(["IT-T5-080"]))["PARA"], "ONDA_PAROU_SITES")

    def test_reconciliacao_que_nao_bate_para(self):
        self.sala.mente = True
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertEqual(r["PARA"], "RECONCILIACAO_FAIL")

    def test_reconciliacao_sem_foto_nao_sei(self):
        self.assertEqual(C.comparar_sala({"raw_asset": 1}, None, {"raw_asset": 1})["ESTADO"], "NAO_SEI")

    def test_interruptor_desliga_sem_erro(self):
        (self.base / C.DESLIGAR_F).write_text("", encoding="utf-8")
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertTrue(r["DESLIGADO"])
        self.assertIsNone(r["PARA"])
        self.assertEqual(CONTAGEM, {})


# ── 4. o robo: parado SO para gravar, e sempre deixado como estava ──────────
class RoboDeFontes(Base):
    def test_robo_vivo_e_parado_e_religado(self):
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertEqual(self.robo.eventos, ["PARAR", "TIRAR_FLAG", "LANCAR"])
        self.assertTrue(self.robo.vivo)
        self.assertFalse(self.robo.flag.exists())
        self.assertTrue(r["ROBO_RELIGADO"])

    def test_robo_religado_mesmo_quando_o_ciclo_para(self):
        self.onda.codigo = 1
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertEqual(r["PARA"], "ONDA_PAROU_SITES")
        self.assertTrue(self.robo.vivo)
        self.assertFalse(self.robo.flag.exists())

    def test_robo_religado_mesmo_quando_a_onda_rebenta(self):
        def rebenta(*a):
            raise RuntimeError("onda caiu")
        r = self.ciclo(self.sites(["IT-T5-080"]), pecas=self.pecas(onda=rebenta))
        self.assertTrue(r["PARA"].startswith("ERRO_NO_CICLO"))
        self.assertTrue(self.robo.vivo)

    def test_sem_fontes_o_robo_nao_e_tocado(self):
        self.visitar("crea.test", 1)
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertTrue(r["NADA_A_CORRER"])
        self.assertEqual(self.robo.eventos, [])
        self.assertEqual(self.backups, [])

    def test_flag_de_outro_nao_e_tirada(self):
        self.robo.flag.write_text("o coordenador parou", encoding="utf-8")
        self.robo.vivo = False
        self.ciclo(self.sites(["IT-T5-080"]))
        self.assertTrue(self.robo.flag.exists())
        self.assertEqual(self.robo.eventos, [])

    def test_robo_parado_antes_fica_parado(self):
        self.robo.vivo = False
        self.ciclo(self.sites(["IT-T5-080"]))
        self.assertEqual(self.robo.eventos, ["PARAR", "TIRAR_FLAG"])
        self.assertFalse(self.robo.vivo)

    def test_robo_que_nao_para_para_o_servico_sem_pedir(self):
        self.robo.teimoso = True
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertEqual(r["PARA"], "ROBO_NAO_PAROU")
        self.assertEqual(CONTAGEM, {})
        self.assertFalse(self.robo.flag.exists())

    def test_robo_que_nao_volta_para_o_servico(self):
        self.robo.nao_volta = True
        r = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertEqual(r["PARA"], "ROBO_NAO_VOLTOU")

    def test_robo_nao_sei_para(self):
        self.robo.nao_sei = True
        self.assertEqual(self.ciclo(self.sites(["IT-T5-080"]))["PARA"], "ROBO_NAO_SEI")


# ── 5. o livro de ciclos ─────────────────────────────────────────────────────
class LivroDeCiclos(Base):
    def test_o_livro_diz_o_que_aconteceu(self):
        self.visitar("edagricole.test", 2)
        self.ciclo(self.sites(["IT-T8-022", "IT-T5-080"]))
        l = [json.loads(x) for x in (self.base / C.CICLOS_F).read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(l), 1)
        c = l[0]
        for k in ("INICIO", "FIM", "LINHAS", "RUN_IDS", "SALA_ANTES", "SALA_DEPOIS", "DOCS_NOVOS", "PROXIMO_A_ABRIR",
                  "ESPERAM", "PROVA_TETO_CICLO", "PROVA_TETO_24H", "RECONCILIACAO", "EGRESSO_ANTES", "EGRESSO_DEPOIS"):
            self.assertIn(k, c)
        self.assertEqual(c["LINHAS"]["SITES"]["PEDIDOS"], 5)
        self.assertEqual(c["DOCS_NOVOS"], 1)
        self.assertEqual(c["SALA_ANTES"]["sala_de_espera"] + 1, c["SALA_DEPOIS"]["sala_de_espera"])
        self.assertEqual(c["PROXIMO_A_ABRIR"]["DOMINIO"], "edagricole.test")

    def test_a_seco_nao_escreve_nem_pede(self):
        r = self.ciclo(self.sites(["IT-T5-080"]), pecas={"ram": lambda: 9.0, "fonte": _admite_tudo}, a_seco=True)
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], ["IT-T5-080"])
        self.assertFalse((self.base / C.CICLOS_F).exists())
        self.assertEqual(CONTAGEM, {})

    def test_trinco_um_servico_de_cada_vez(self):
        t = C.trinco(self.base)
        self.assertIsNotNone(t)
        self.assertIsNone(C.trinco(self.base))
        C.soltar(t)
        self.assertIsNotNone(C.trinco(self.base))


class TrincoDeDonoMorto(unittest.TestCase):
    """O trinco tem de separar CONFLITO de SOBRA — e antes nao separava.

    Medido a 30/09: o ciclo 101 ficou com o trinco preso por um processo morto a
    meio (PID 36520, 08:15) e a coleta so voltou quando alguem o removeu a mao.
    Um dono que ja nao existe nao e «outro servico a correr»: e sobra, e o servico
    tem de a tomar sozinho. Estas provas fixam as tres respostas — dono morto
    TOMADO, dono vivo RECUSADO, dono ilegivel RECUSADO — para o conserto nao
    voltar a depender de uma sonda manual que ninguem repete.
    """

    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="coleta-trinco-"))
        self.addCleanup(shutil.rmtree, self.base, True)

    def _sobra(self, pid, dono=True):
        t = self.base / C.TRINCO_F
        t.mkdir()
        if dono:
            (t / "DONO.json").write_text(
                json.dumps({"PID": pid, "DESDE": "2026-09-30T08:15:31-03:00"}), encoding="utf-8")
        return t

    @staticmethod
    def _pid_morto():
        """Um PID que existiu mesmo e ja acabou — nao um numero inventado.

        O filho e criado e recolhido por um PROCESSO INTERMEDIARIO: se o proprio
        teste o criasse, o handle no processo do teste mantem o PID a responder ao
        OpenProcess, e a prova mediria o handle do teste em vez da morte do dono.
        Medido a 30/09: no mesmo processo o PID recem-saido responde VIVO; pedido a
        um processo que nunca o viu, responde MORTO — que e o caso real do trinco,
        cujo dono vem sempre de uma corrida anterior.
        """
        codigo = ("import subprocess,sys;"
                  "p=subprocess.Popen([sys.executable,'-c','pass']);"
                  "p.wait();print(p.pid)")
        r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, timeout=60)
        return int(r.stdout.strip())

    def test_dono_morto_e_sobra_e_o_servico_toma_o_trinco(self):
        self._sobra(self._pid_morto())
        t = C.trinco(self.base)
        self.assertIsNotNone(t, "trinco de dono morto parou o servico: a coleta ficaria presa para sempre")
        self.assertEqual(json.loads((t / "DONO.json").read_text(encoding="utf-8"))["PID"], os.getpid())

    def test_dono_vivo_continua_a_recusar(self):
        self._sobra(os.getpid())
        self.assertIsNone(C.trinco(self.base), "o trinco deixou de ser dois servicos de cada vez")

    def test_sem_dono_legivel_nao_se_toca(self):
        self._sobra(None, dono=False)
        self.assertIsNone(C.trinco(self.base), "trinco sem dono foi tomado as cegas")
        (self.base / C.TRINCO_F / "DONO.json").write_text("{isto nao e json", encoding="utf-8")
        self.assertIsNone(C.trinco(self.base), "trinco com dono ilegivel foi tomado as cegas")

    def test_dono_com_pid_impossivel_nao_se_toca(self):
        """SERVICO-TRINCO (30/09): o DONO que o servico escreve tem sempre um PID inteiro > 0. PID 0, negativo,
        booleano, texto ou em falta e DONO corrompido — nao e prova de morte, e nao se toma (o auditor mediu
        PID 0 e -1 a serem TOMADOS no c38610e0c)."""
        for dono in ({"PID": 0}, {"PID": -1}, {"PID": True}, {"PID": "abc"}, {"PID": None}, {"PID": []},
                     {"DESDE": "2026-09-30T08:15:31-03:00"}, [1234], "1234"):
            with self.subTest(dono=dono):
                t = self.base / C.TRINCO_F
                shutil.rmtree(t, ignore_errors=True)
                t.mkdir()
                (t / "DONO.json").write_text(json.dumps(dono), encoding="utf-8")
                self.assertIsNone(C.trinco(self.base), "trinco com DONO corrompido foi tomado: %r" % (dono,))
                self.assertEqual(json.loads((t / "DONO.json").read_text(encoding="utf-8")), dono)

    def test_dono_vivo_noutro_processo_continua_a_recusar(self):
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        self.addCleanup(p.wait)
        self.addCleanup(p.kill)
        self._sobra(p.pid)
        self.assertIsNone(C.trinco(self.base), "trinco de um servico VIVO foi tomado")


# ── SERVICO-TRINCO (30/09): as regras que o auditor pediu (VERIF-SERVICO-c38610e0c = CORRIGIR) ──
# O concorrente: um processo por arranque, vivo durante as rodadas todas. Em cada rodada espera a MESMA hora
# de partida (espera ativa, para chegarem ao trinco no mesmo milissegundo), tenta o trinco, SEGURA-O ate ao
# fim da rodada (ninguem solta: dois donos na mesma rodada sao dois servicos ao mesmo tempo) e diz o que teve.
_CONCORRENTE = r'''
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import coleta_continua as C
print("PRONTO", flush=True)
for linha in sys.stdin:
    base, inicio, fim = linha.rstrip("\n").split("\t")
    while time.time() < float(inicio):
        pass
    r = {"PID": os.getpid(), "TEM": False, "EXC": None, "AINDA_DONO": None}
    t = None
    try:
        t = C.trinco(Path(base))
        r["TEM"] = t is not None
    except BaseException as ex:
        r["EXC"] = repr(ex)
    while time.time() < float(fim):
        time.sleep(0.005)
    if t is not None:
        try:
            r["AINDA_DONO"] = json.loads((t / "DONO.json").read_text(encoding="utf-8")).get("PID") == os.getpid()
        except Exception as ex:
            r["AINDA_DONO"] = repr(ex)
    print(json.dumps(r), flush=True)
'''


class TrincoSobCorrida(unittest.TestCase):
    """(a) dono MORTO + N arranques ao mesmo tempo: exatamente UM dono por rodada, e trinco() nunca lanca.

    Medido pelo auditor no c38610e0c (4 processos x 20 rodadas): 2 ou 3 donos simultaneos em 12 de 20
    rodadas e 10 FileNotFoundError dentro de trinco(). Um teste que corre uma vez nao ve isto: sao N
    processos a partir no mesmo milissegundo, rodada apos rodada.
    """
    N, RODADAS = 8, 20
    maxDiff = None

    def test_dono_morto_disputado_por_8_processos_tem_um_so_dono_em_cada_rodada(self):
        pasta = Path(tempfile.mkdtemp(prefix="coleta-trinco-corrida-"))
        self.addCleanup(shutil.rmtree, pasta, True)
        procs = [subprocess.Popen([sys.executable, "-c", _CONCORRENTE, str(RAIZ / "ferramentas" / "big_collection")],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  text=True, encoding="utf-8") for _ in range(self.N)]
        def fechar():
            for p in procs:
                p.kill()
                p.wait()
                p.stdin.close()
                p.stdout.close()
        self.addCleanup(fechar)
        for p in procs:
            self.assertEqual(p.stdout.readline().strip(), "PRONTO")
        rodadas = []
        for k in range(self.RODADAS):
            base = pasta / ("R%02d" % k)
            t = base / C.TRINCO_F
            t.mkdir(parents=True)
            (t / "DONO.json").write_text(json.dumps({"PID": TrincoDeDonoMorto._pid_morto(),
                                                     "DESDE": "2026-09-30T08:15:31-03:00"}), encoding="utf-8")
            inicio = time.time() + 0.2
            for p in procs:
                p.stdin.write("%s\t%r\t%r\n" % (base, inicio, inicio + 0.3))
                p.stdin.flush()
            rodadas.append([json.loads(p.stdout.readline()) for p in procs])
        donos = [sum(1 for r in rod if r["TEM"]) for rod in rodadas]
        excecoes = [r["EXC"] for rod in rodadas for r in rod if r["EXC"]]
        perdidos = [r for rod in rodadas for r in rod if r["TEM"] and r["AINDA_DONO"] is not True]
        # tudo numa so comparacao: a reprovacao mostra as tres medidas, nao so a primeira que falha
        self.assertEqual({"DONOS_POR_RODADA": donos, "EXCECOES_DENTRO_DE_TRINCO": excecoes, "DONOS_QUE_PERDERAM": perdidos},
                         {"DONOS_POR_RODADA": [1] * self.RODADAS, "EXCECOES_DENTRO_DE_TRINCO": [], "DONOS_QUE_PERDERAM": []},
                         "dono morto disputado: tem de haver sempre UM dono, nenhuma excecao, nenhum dono enganado"
                         " | DONOS_POR_RODADA=%s | EXCECOES=%d" % (donos, len(excecoes)))


class TrincoAtrasadoComAVez(unittest.TestCase):
    """A VEZ, com o intervalo mais estreito posto a mao (SERVICO-TRINCO, 30/09).

    O mutante M31 (tomada sem a vez) sobreviveu a corrida de 8 processos: com o dono relido logo antes do
    rename, a janela e de microssegundos e a corrida nao a acerta. Aqui ela e aberta de proposito: o
    arranque B rele o dono morto e, ANTES do rename de B, o arranque A faz uma tomada inteira. Sem a vez,
    B renomeia o trinco NOVO de A e ficam os dois com o trinco (medido com o M31). Com a vez, A nem tenta.
    Tudo no mesmo processo: o trinco do sistema (LockFile/flock) e por ficheiro aberto, e A abre o seu.
    """

    def test_arranque_atrasado_nao_rouba_o_trinco_novo_de_outro(self):
        from unittest import mock
        base = Path(tempfile.mkdtemp(prefix="coleta-trinco-atrasado-"))
        self.addCleanup(shutil.rmtree, base, True)
        t = base / C.TRINCO_F
        t.mkdir()
        (t / "DONO.json").write_text(json.dumps({"PID": TrincoDeDonoMorto._pid_morto(), "DESDE": "x"}), encoding="utf-8")
        original = C._trinco_de_dono_morto
        chamadas, de_a = [], []

        def rele_e_deixa_a_passar(p):
            morto = original(p)
            chamadas.append(morto)
            if len(chamadas) == 2:                      # B com o dono relido e ainda sem o rename: entra A
                with mock.patch.object(C, "_trinco_de_dono_morto", original):
                    de_a.append(C.trinco(base))
            return morto
        with mock.patch.object(C, "_trinco_de_dono_morto", rele_e_deixa_a_passar):
            de_b = C.trinco(base)
        self.assertEqual(len(de_a), 1, "premissa: B tinha de reler o dono antes do rename")
        donos = [x for x in (de_a[0], de_b) if x is not None]
        self.assertEqual(len(donos), 1, "dois arranques ficaram com o trinco (A=%r, B=%r)" % (de_a[0], de_b))
        self.assertTrue((t / "DONO.json").exists())


@unittest.skipUnless(os.name == "nt", "OpenProcess/GetExitCodeProcess sao do Windows")
class PidVivoNoWindows(unittest.TestCase):
    """(d) no Windows um processo que SAIU continua abrivel enquanto alguem segurar o handle dele (o auditor
    mediu OpenProcess = ok, exit = 0). Morto so quando GetExitCodeProcess != 259 (STILL_ACTIVE). E ACESSO
    NEGADO (erro 5) e um processo que existe e nao nos deixa olhar: VIVO, nunca morto."""

    @staticmethod
    def _abrir(pid):
        import ctypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        h = k.OpenProcess(0x1000, False, pid)
        erro = ctypes.get_last_error()
        if h:
            k.CloseHandle(h)
        return bool(h), erro

    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="coleta-trinco-pid-"))
        self.addCleanup(shutil.rmtree, self.base, True)

    def _morto_com_handle_aberto(self):
        p = subprocess.Popen([sys.executable, "-c", "pass"])
        p.wait()
        self._segura = p                                             # o Popen segura o handle do morto
        self.assertEqual(self._abrir(p.pid)[0], True, "premissa: o morto tem de continuar abrivel")
        return p.pid

    def _acesso_negado(self):
        abre, erro = self._abrir(4)
        if abre or erro != 5:
            self.skipTest("premissa: o PID 4 (System) ja nao da acesso negado nesta maquina (%r, %r)" % (abre, erro))
        return 4

    def test_morto_com_handle_aberto_e_morto(self):
        self.assertFalse(C._pid_vivo(self._morto_com_handle_aberto()), "processo que saiu contado como vivo")

    def test_acesso_negado_e_vivo(self):
        self.assertTrue(C._pid_vivo(self._acesso_negado()), "acesso negado contado como morto")

    def test_vivo_e_vivo(self):
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        self.addCleanup(p.wait)
        self.addCleanup(p.kill)
        self.assertTrue(C._pid_vivo(p.pid))
        self.assertTrue(C._pid_vivo(os.getpid()))

    def test_pid_que_ja_nao_existe_e_morto(self):
        self.assertFalse(C._pid_vivo(TrincoDeDonoMorto._pid_morto()))

    def _sobra(self, pid):
        t = self.base / C.TRINCO_F
        t.mkdir()
        (t / "DONO.json").write_text(json.dumps({"PID": pid, "DESDE": "2026-09-30T08:15:31-03:00"}), encoding="utf-8")

    def test_trinco_de_dono_morto_com_handle_aberto_e_tomado(self):
        self._sobra(self._morto_com_handle_aberto())
        t = C.trinco(self.base)
        self.assertIsNotNone(t, "dono morto com handle aberto parou o servico (o PARA original volta)")
        self.assertEqual(json.loads((t / "DONO.json").read_text(encoding="utf-8"))["PID"], os.getpid())

    def test_trinco_de_dono_com_acesso_negado_e_recusado(self):
        self._sobra(self._acesso_negado())
        self.assertIsNone(C.trinco(self.base), "dono protegido (acesso negado) foi dado como morto e TOMADO")


class LimpezaDoPgDaProvaDeBackup(unittest.TestCase):
    """(e) provar_backup_da_sala limpa <saida>/pg — a sobra de uma prova morta a meio — e SO essa pasta.
    --saida vazia ou a raiz de um disco e recusada ANTES de tocar em qualquer coisa (a Sala incluida).

    Sem Postgres e sem Sala: o DSN, a fotografia e cada subprocesso sao falsos; o que se mede e o que o
    programa apaga e quando."""

    def setUp(self):
        sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
        import provar_backup_da_sala as P
        self.P = P
        self.raiz = Path(tempfile.mkdtemp(prefix="prova-backup-pg-"))
        self.addCleanup(shutil.rmtree, self.raiz, True)
        self.chamadas = []
        self.apagados = []

    def _falsos(self, dsn=None):
        from unittest import mock

        def run(cmd, *a, **k):
            nome = Path(str(cmd[0])).stem
            pasta = Path(cmd[cmd.index("-D") + 1]) if "-D" in cmd else None
            self.chamadas.append({"CMD": nome, "PASTA": pasta, "SOBRA_AINDA_LA": bool(pasta and (pasta / "SOBRA").exists())})
            return subprocess.CompletedProcess(cmd, 0, stdout="sala_de_espera", stderr="")

        rmtree_real = shutil.rmtree

        def rmtree(p, *a, **k):
            self.apagados.append(Path(p))
            return rmtree_real(p, *a, **k)

        def dsn_falso():
            if dsn is None:
                raise AssertionError("TOCOU_NA_SALA")
            return dsn
        return [mock.patch("subprocess.run", run), mock.patch.object(self.P.shutil, "rmtree", rmtree),
                mock.patch.object(self.P.MC, "_dsn", dsn_falso),
                mock.patch.object(self.P.E, "fotografia", lambda: {"sala_de_espera": [1, "md5-falso"]})]

    def _correr(self, argv, dsn=None):
        fs = self._falsos(dsn)
        for f in fs:
            f.start()
        try:
            return self.P.main(argv)
        finally:
            for f in reversed(fs):
                f.stop()

    def _sobra_de_pg(self, saida):
        pg = saida / "pg"
        (pg / "base" / "1").mkdir(parents=True)
        (pg / "SOBRA").write_text("postmaster.pid de um ciclo morto", encoding="utf-8")
        (pg / "base" / "1" / "16384").write_bytes(b"\0" * 64)
        return pg

    def test_sobra_de_pg_e_limpa_antes_do_initdb_e_so_ela(self):
        saida = self.raiz / "CICLO-0101" / "backup"
        pg = self._sobra_de_pg(saida)
        (saida / "OUTRO.txt").write_text("nao e do pg", encoding="utf-8")
        for vizinho in (self.raiz / "pg", self.raiz / "CICLO-0101" / "pg"):
            vizinho.mkdir(parents=True)
            (vizinho / "NAO-TOCAR").write_text("x", encoding="utf-8")
        rc = self._correr(["--saida=%s" % saida], dsn="postgresql://falso@127.0.0.1:1/sala_italia")
        self.assertEqual(rc, 0)
        initdb = [c for c in self.chamadas if c["CMD"] == "initdb"]
        self.assertEqual(len(initdb), 1)
        self.assertEqual(initdb[0]["PASTA"], pg)
        self.assertFalse(initdb[0]["SOBRA_AINDA_LA"], "o initdb correu por cima da sobra: a prova morria como no ciclo 101")
        paragem = [i for i, c in enumerate(self.chamadas) if c["CMD"] == "pg_ctl" and c["PASTA"] == pg]
        self.assertLess(paragem[0], self.chamadas.index(initdb[0]), "o Postgres da sobra nao foi descido antes")
        self.assertEqual(self.apagados, [pg], "a limpeza apagou outra coisa alem de <saida>/pg")
        self.assertTrue((saida / "OUTRO.txt").exists())
        self.assertTrue((self.raiz / "pg" / "NAO-TOCAR").exists())
        self.assertTrue((self.raiz / "CICLO-0101" / "pg" / "NAO-TOCAR").exists())
        self.assertTrue(json.loads((saida / "PROVA-BACKUP-SALA.json").read_text(encoding="utf-8"))["PROVA_VALE"])

    def test_saida_vazia_ou_raiz_de_disco_e_recusada_antes_de_tudo(self):
        for s in ("", "   ", Path(RAIZ.anchor).as_posix(), str(Path(RAIZ.anchor)), "/"):
            with self.subTest(saida=s):
                self.chamadas.clear()
                self.apagados.clear()
                try:
                    rc = self._correr(["--saida=" + s])
                except AssertionError as ex:
                    self.fail("--saida=%r nao foi recusada: chegou a Sala (%s)" % (s, ex))
                self.assertEqual(rc, 2, "--saida=%r nao foi recusada" % s)
                self.assertEqual(self.chamadas, [])
                self.assertEqual(self.apagados, [])

    def test_tomada_do_trinco_e_limpeza_do_pg_nao_se_tocam(self):
        """A pergunta do Scrap (ENTREGA-SCRAP-TRINCO): mexer no trinco afeta a limpeza de pg/? Medido aqui no
        caso real do ciclo 101: um ciclo morto deixa, na MESMA base, o trinco com dono morto E a sobra
        CICLO-NNNN/backup/pg. O arranque seguinte toma o trinco (a sobra de pg fica intacta, byte a byte) e o
        ciclo repetido limpa pg/ (o trinco novo fica intacto, com o DONO deste processo)."""
        base = self.raiz / "COLETA-CONTINUA"
        t = base / C.TRINCO_F
        t.mkdir(parents=True)
        (t / "DONO.json").write_text(json.dumps({"PID": TrincoDeDonoMorto._pid_morto(), "DESDE": "x"}), encoding="utf-8")
        saida = base / "CICLO-0101" / "backup"
        pg = self._sobra_de_pg(saida)

        def foto(p):
            return {str(f.relative_to(p)): f.read_bytes() for f in sorted(p.rglob("*")) if f.is_file()}
        pg_antes = foto(pg)
        dono = C.trinco(base)
        self.assertIsNotNone(dono)
        self.assertEqual(foto(pg), pg_antes, "tomar o trinco mexeu na sobra de pg/")
        trinco_antes = foto(dono)
        rc = self._correr(["--saida=%s" % saida], dsn="postgresql://falso@127.0.0.1:1/sala_italia")
        self.assertEqual(rc, 0)
        self.assertEqual(self.apagados, [pg])
        self.assertEqual(foto(dono), trinco_antes, "limpar pg/ mexeu no trinco")
        self.assertEqual(json.loads((dono / "DONO.json").read_text(encoding="utf-8"))["PID"], os.getpid())
        C.soltar(dono)


# ── 5b. ADENDO-PARADA (01/10): o ciclo 146 PAROU o servico por nada ─────────
# Medido no vivo (eac885db3, ciclo 146, CICLO-0146/SITES/ONDA-WEB-ESTADO.json): o agendador deu IT-T8-051 a onda
# dos SITES; o portao da onda recusou com GATE:ESTADO_NAO_READY; 0 corridas, 0 pedidos; a prova-teto deu NAO_SEI
# sobre RUN_IDS=[] e o servico PAROU (PARA=PROVA_TETO_NAO_SEI) ate alguem rearmar.
#   (1) o agendador pergunta ao MESMO portao que a onda usa (collection_gate.avaliar) e nao oferece a recusada:
#       ela ESPERA com PORQUE=FONTE_NAO_READY e o estado lido;
#   (2) ciclo sem corrida E sem pedido: a prova-teto diz NADA_A_PROVAR e o servico NAO para. Com corridas (ou com
#       um pedido qualquer no livro da onda, ou sem o estado da onda) a prova continua a parar.
class OndaQueRecusa:
    """O papel da onda do ciclo 146: recebe as fontes, o portao dela recusa todas, nenhum pedido sai."""

    def __init__(self, sala, livro_da_onda=None, run_id=None, escreve_estado=True):
        self.sala, self.livro_da_onda, self.run_id, self.escreve_estado = sala, livro_da_onda, run_id, escreve_estado
        self.chamadas = []

    def __call__(self, sha, fontes, pasta, historico, retomar):
        self.chamadas.append(list(fontes))
        pasta.mkdir(parents=True, exist_ok=True)
        if self.livro_da_onda is not None:
            (pasta / "TETO-ONDA.json").write_text(self.livro_da_onda, encoding="utf-8")
        if self.escreve_estado:
            foto = self.sala.foto()
            (pasta / "ONDA-WEB-ESTADO.json").write_text(json.dumps({
                "SO_AS_FONTES": list(fontes), "SALA_INICIO": foto, "PAROU": None, "SALA_FIM": foto,
                "FONTES": [{"N": i, "SOURCE_ID": s, "CORREU": False, "STATUS": None, "RUN_ID": self.run_id,
                            "PORQUE_NAO_CORREU": ["GATE:ESTADO_NAO_READY"], "LIVRO_DA_ONDA": {}}
                           for i, s in enumerate(fontes, 1)]}), encoding="utf-8")
        return 0


def _recusa(*recusadas, estado="CONTRACTED_CANARY_FAILED"):
    """O portao falso: recusa estas com ESTADO_NAO_READY (como o real recusou IT-T8-051), admite as outras."""
    def portao(ids):
        out = _admite_tudo(ids)
        for s in ids:
            if s in recusadas:
                out[s] = {"COLLECTION_ELIGIBLE": False, "STATE": estado, "MOTIVO": "ESTADO_NAO_READY",
                          "PORQUE": "o estado no livro e %s" % estado}
        return out
    return portao


class AdendoParada(Base):
    # (1) o agendador nao oferece a onda a fonte que o portao dela recusa
    def test_fonte_nao_ready_nao_vai_a_onda_e_espera_com_nome_proprio(self):
        r = self.ciclo(self.sites(["IT-T5-080", "IT-T9-002"]), pecas=self.pecas(fonte=_recusa("IT-T9-002")))
        self.assertIsNone(r["PARA"], r)
        self.assertEqual([c["FONTES"] for c in self.onda.chamadas], [["IT-T5-080"]])
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], ["IT-T5-080"])
        e = [x for x in r["ESPERAM"] if x["SOURCE_ID"] == "IT-T9-002"]
        self.assertEqual(len(e), 1, r["ESPERAM"])
        self.assertEqual(e[0]["PORQUE"], "FONTE_NAO_READY")
        self.assertEqual(e[0]["ESTADO_LIDO"], "CONTRACTED_CANARY_FAILED")
        self.assertEqual(e[0]["MOTIVO_DO_PORTAO"], "ESTADO_NAO_READY")
        self.assertEqual(e[0]["LINHA"], "SITES")
        self.assertNotIn("dois.test", _por_dominio(CONTAGEM))

    def test_so_fontes_nao_ready_o_ciclo_nao_toca_na_onda_nem_no_robo(self):
        r = self.ciclo(self.sites(["IT-T9-002"]), pecas=self.pecas(fonte=_recusa("IT-T9-002")))
        self.assertIsNone(r["PARA"], r)
        self.assertEqual(self.onda.chamadas, [])
        self.assertEqual(self.robo.eventos, [])
        self.assertEqual(r["LINHAS"]["SITES"]["ESTADO"], "NADA_ELEGIVEL")      # ha fontes e nenhuma cabe agora
        self.assertEqual([(x["SOURCE_ID"], x["PORQUE"]) for x in r["ESPERAM"]], [("IT-T9-002", "FONTE_NAO_READY")])
        self.assertIsNone(C.ler_estado(self.base)["PAROU"])

    def test_portao_que_nao_responde_para_o_servico(self):
        def rebenta(ids):
            raise ValueError("livro canonico ilegivel")
        r = self.ciclo(self.sites(["IT-T9-002"]), pecas=self.pecas(fonte=rebenta))
        self.assertEqual(r["PARA"], "PORTAO_DA_FONTE_NAO_SEI")
        self.assertEqual(self.onda.chamadas, [])

    def test_sem_portao_injectado_o_ciclo_usa_o_portao_real(self):
        # fail-closed: quem chama o ciclo sem dizer o portao leva o REAL, nunca um que admite tudo
        p = self.pecas()
        del p["fonte"]
        r = self.ciclo(self.sites(["IT-T9-002"]), pecas=p)
        self.assertEqual(self.onda.chamadas, [])
        e = [x for x in r["ESPERAM"] if x["SOURCE_ID"] == "IT-T9-002"]
        self.assertEqual([(x["PORQUE"], x["ESTADO_LIDO"]) for x in e], [("FONTE_NAO_READY", "AUSENTE_DO_LIVRO")])

    def test_o_agendador_pergunta_ao_mesmo_portao_que_a_onda(self):
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import collection_gate as GATE  # noqa: PLC0415
        ctx = GATE._contexto()
        ids = sorted({t["SOURCE_ID"] for t in ctx["livro"]["TRANSICOES"]}) + ["IT-T0-AUSENTE"]
        v = C.portao_da_fonte_real(ids)
        esperado = {s: GATE.avaliar(s, **ctx) for s in ids}
        self.assertEqual({s: (x["COLLECTION_ELIGIBLE"], x["STATE"], x["MOTIVO"]) for s, x in v.items()},
                         {s: (x["COLLECTION_ELIGIBLE"], x["STATE"], x["MOTIVO"]) for s, x in esperado.items()})
        # a comparacao nao passa por vazio: ha admitidas E recusadas por estado neste livro
        self.assertTrue(any(x["COLLECTION_ELIGIBLE"] for x in v.values()))
        self.assertTrue(any(x["MOTIVO"] == GATE.ESTADO_NAO_READY for x in v.values()))
        # e e este o portao da onda: onda_web.py --correr -> micro_coleta.correr -> plano -> GATE.avaliar
        mc = (RAIZ / "scripts" / "micro_coleta" / "micro_coleta.py").read_text(encoding="utf-8")
        self.assertIn("import collection_gate as GATE", mc)
        self.assertIn("g = GATE.avaliar(s, **ctx)", mc)
        self.assertIn("falta.append(f\"GATE:{g['MOTIVO']}\")", mc)

    def test_a_passagem_acaba_com_as_admitidas(self):
        # a recusada nunca corre: se a passagem esperasse por ela, a linha ficava NADA_ELEGIVEL para sempre
        cands = self.sites(["IT-T5-080", "IT-T9-002"])
        pecas = self.pecas(fonte=_recusa("IT-T9-002"))
        self.ciclo(cands, pecas=pecas)
        r = self.ciclo(cands, pecas=pecas, agora_utc=datetime.now(timezone.utc) + timedelta(hours=25))
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], ["IT-T5-080"], r)
        self.assertEqual(C.ler_estado(self.base)["LINHAS"]["SITES"]["PASSAGEM"], 2)

    # (2) ciclo sem corrida e sem pedido: nada a provar, o servico segue
    def test_ciclo_146_sem_corrida_e_sem_pedido_nao_para(self):
        onda = OndaQueRecusa(self.sala)
        r = self.ciclo(self.sites(["IT-T9-002"]), pecas=self.pecas(onda=onda))
        self.assertEqual(onda.chamadas, [["IT-T9-002"]])
        self.assertEqual(r["RUN_IDS"], [])
        self.assertEqual(r["PROVA_TETO_CICLO"]["ESTADO"], "NADA_A_PROVAR", r["PROVA_TETO_CICLO"])
        self.assertEqual(r["PROVA_TETO_CICLO"]["CORRIDAS_DA_ONDA"], 0)
        self.assertEqual(r["PROVA_TETO_CICLO"]["PEDIDOS_NOS_LIVROS_DAS_ONDAS"], 0)
        self.assertEqual(r["PROVA_TETO_24H"]["ESTADO"], "NADA_A_PROVAR")
        self.assertIsNone(r["PARA"], r)
        self.assertIsNone(C.ler_estado(self.base)["PAROU"])
        self.assertEqual(self.robo.eventos, ["PARAR", "TIRAR_FLAG", "LANCAR"])
        self.assertEqual(r["RECONCILIACAO"]["ESTADO"], "PASS")
        self.assertEqual(r["LINHAS"]["SITES"]["CORRERAM"], [])
        # e o ciclo seguinte corre: nao ficou PARADO
        r2 = self.ciclo(self.sites(["IT-T5-080"]))
        self.assertNotIn("JA_PARADO", str(r2["PARA"]))
        self.assertEqual(r2["LINHAS"]["SITES"]["CORRERAM"], ["IT-T5-080"])

    def test_sem_corrida_mas_com_pedido_no_livro_da_onda_para(self):
        onda = OndaQueRecusa(self.sala, livro_da_onda=json.dumps({"PEDIDOS_POR_DOMINIO": {"dois.test": 2}}))
        r = self.ciclo(self.sites(["IT-T9-002"]), pecas=self.pecas(onda=onda))
        self.assertEqual(r["PARA"], "PROVA_TETO_NAO_SEI", r)

    def test_sem_corrida_e_livro_da_onda_ilegivel_para(self):
        onda = OndaQueRecusa(self.sala, livro_da_onda="{nao e json")
        r = self.ciclo(self.sites(["IT-T9-002"]), pecas=self.pecas(onda=onda))
        self.assertEqual(r["PARA"], "PROVA_TETO_NAO_SEI", r)

    def test_onda_sem_estado_gravado_para(self):
        onda = OndaQueRecusa(self.sala, escreve_estado=False)
        r = self.ciclo(self.sites(["IT-T9-002"]), pecas=self.pecas(onda=onda))
        self.assertEqual(r["PARA"], "PROVA_TETO_NAO_SEI", r)

    def test_corrida_que_nao_correu_mas_tem_run_id_sem_linha_no_livro_para(self):
        rid = "IT-T9-%s-%s" % (datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S"), "cd" * 8)
        onda = OndaQueRecusa(self.sala, run_id=rid)
        r = self.ciclo(self.sites(["IT-T9-002"]), pecas=self.pecas(onda=onda))
        self.assertEqual(r["RUN_IDS"], [rid])
        self.assertEqual(r["PARA"], "PROVA_TETO_NAO_SEI", r)
        self.assertEqual(r["PROVA_TETO_CICLO"]["CORRIDAS_SEM_LINHA_NO_LIVRO"], [rid])

    def test_ciclo_vazio_nao_apaga_a_prova_das_24h(self):
        self.ciclo(self.sites(["IT-T5-080"]))                       # uma corrida de verdade ha minutos
        self.ledger.write_text("", encoding="utf-8")                # o livro de corridas perdeu-a
        r = self.ciclo(self.sites(["IT-T9-002"]), pecas=self.pecas(onda=OndaQueRecusa(self.sala)))
        self.assertEqual(r["PROVA_TETO_CICLO"]["ESTADO"], "NADA_A_PROVAR")
        self.assertEqual(r["PARA"], "PROVA_TETO_24H_NAO_SEI", r)

    def test_livro_da_cortesia_ilegivel_continua_a_parar(self):
        livro24 = self.livro24

        def estraga(*a):
            c = self.onda(*a)
            livro24.write_text("{estragado", encoding="utf-8")
            return c
        r = self.ciclo(self.sites(["IT-T5-080"]), pecas=self.pecas(onda=estraga))
        self.assertEqual(r["PARA"], "PROVA_TETO_NAO_SEI", r)

        def estraga_sem_corrida(*a):
            c = OndaQueRecusa(self.sala)(*a)
            livro24.write_text("{estragado", encoding="utf-8")
            return c
        self.livro24.unlink()
        C.rearmar(self.base, "teste")
        r = self.ciclo(self.sites(["IT-T9-002"]), pecas=self.pecas(onda=estraga_sem_corrida))
        self.assertEqual(r["PARA"], "PROVA_TETO_NAO_SEI", r)


# ── 6. o plano real da 4.a onda (ensaio a seco, 0 rede) ──────────────────────
class EnsaioOnda4(unittest.TestCase):
    def test_o_ensaio_gravado_mostra_fontes_presas_elegiveis(self):
        f = RAIZ / "ferramentas" / "big_collection" / "onda4" / "ENSAIO-COLETA-CONTINUA.json"
        d = json.loads(f.read_text(encoding="utf-8"))
        self.assertEqual(d["DISPARADOR_POR_RODADA"]["PAROU"], "JANELA_24H")
        self.assertEqual(d["DISPARADOR_POR_RODADA"]["CHAMADAS_A_ONDA"], 0)
        correm = d["AGENDADOR_POR_FONTE"]["LINHAS"]["SITES"]["FONTES"]
        self.assertTrue(correm)
        presas = {s for r in d["RODADAS_PRESAS"] for s in r["FONTES"]}
        self.assertTrue(set(correm) <= presas)
        for e in d["AGENDADOR_POR_FONTE"]["ESPERAM"]:
            self.assertTrue(e["ABRE_EM"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
