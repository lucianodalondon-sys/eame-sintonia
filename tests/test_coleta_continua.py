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
import sys
import tempfile
import threading
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
             "ram": lambda: self.ram, "backup": self._backup, "robo": self.robo, "reconciliar": self.sala.reconciliar}
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
        """SCRAP-S1S2 (28/09): a SITES prova-se pelo COMPORTAMENTO; as outras quatro pelo TEXTO no
        ficheiro que RESERVA por elas — o dono do freio (`teto_da_onda`), ou o abridor que o chama
        (`scrap_http`), e nao o ficheiro do transporte. A medida vem SEMPRE rotulada: TEXTO nao passa
        por comportamento. Antes desta correcao, a regua procurava a string no transporte e deixava
        BUSCA e SOCIAL em ESPERA_LIGACAO com o transporte ligado ao livro."""
        m = {l["LINHA"]: C.medir_ligacao(l) for l in C.LINHAS}
        self.assertTrue(m["SITES"]["LIGADA"], m["SITES"])
        self.assertEqual(m["SITES"]["MEDIDO_EM"], "COMPORTAMENTO", m["SITES"])
        for n in ("BUSCA", "CIENCIA", "SOCIAL", "PESQUISADORES"):
            self.assertTrue(m[n]["LIGADA"], (n, m[n]))
            self.assertEqual(m[n]["MEDIDO_EM"], "TEXTO", (n, m[n]))

    def test_linha_sem_ficheiro_de_reserva_nao_se_liga(self):
        """LIGADA nao se declara: o ficheiro nomeado tem de EXISTIR e CHAMAR. Sem isso, fica a espera."""
        l = {"LINHA": "Z", "TRANSPORTE": "coleta/teto_da_onda.py",
             "RESERVA_EM": [{"FICHEIRO": "coleta/nao-existe-esta-linha.py", "CHAMADA": "teto.reservar("}]}
        m = C.medir_ligacao(l, C.RAIZ)
        self.assertFalse(m["LIGADA"], m)
        self.assertTrue(m["PORQUE"].startswith("SEM_RESERVA_24H"), m["PORQUE"])
        self.assertIsNone(m["MEDIDO_EM"], m)

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
        r = self.ciclo(self.sites(["IT-T5-080"]), pecas={"ram": lambda: 9.0}, a_seco=True)
        self.assertEqual(r["LINHAS"]["SITES"]["FONTES"], ["IT-T5-080"])
        self.assertFalse((self.base / C.CICLOS_F).exists())
        self.assertEqual(CONTAGEM, {})

    def test_trinco_um_servico_de_cada_vez(self):
        t = C.trinco(self.base)
        self.assertIsNotNone(t)
        self.assertIsNone(C.trinco(self.base))
        C.soltar(t)
        self.assertIsNotNone(C.trinco(self.base))


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
