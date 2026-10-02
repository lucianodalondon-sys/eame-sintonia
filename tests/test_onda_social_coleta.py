# -*- coding: utf-8 -*-
"""SOCIAL-ONDA (02/10/2026): a linha SOCIAL ganha onda PROPRIA na coleta continua, atras do --autorizado-pelo-dono.

Medido antes deste teste (790b89e39): a linha SOCIAL saia BLOQUEADA_PERMISSAO_SOCIAL e depois BLOQUEADA_CAPACIDADE —
nao havia onda dela no ciclo (so a dos SITES, `onda_web.py --correr`, que so aceita a coorte congelada) nem a flag
na coleta continua. Os itens sociais do banco vieram de levas manuais, nunca do servico.

O que se liga (nada de extrator, rota ou ferramenta nova):
  · a onda SOCIAL consome SO as unidades ACEITES pela porta T9 (`plano_onda_social.triagem_social`) e corre pelo
    MAESTRO SOCIAL que ja existe (`maestro_social.py --correr --autorizado-pelo-dono --fontes=`);
  · POR OMISSAO FICA DESLIGADA: sem `--autorizado-pelo-dono` a linha diz BLOQUEADA_PERMISSAO_SOCIAL, com nome;
  · as MESMAS guardas da onda dos SITES (egresso IT antes/depois, livro de 24 h com reserva, backup da Sala,
    prova-teto, reconciliacao) — o ciclo e o mesmo, so a onda da linha muda;
  · Instagram: SO a URL directa do Reel (D22/D157). Um endereco de perfil e LISTAGEM_NAO_AUTORIZADA na porta.

Transporte FALSO, sem rede: o "Scrap" destes testes pede a um servidor 127.0.0.1 com o cabecalho Host da
plataforma, e passa pelo freio REAL do transporte social (`coleta/teto_da_onda.reservar` -> livro da onda +
livro da cortesia de 24 h). O maestro e o REAL (`maestro_social.correr`), com o lancamento trocado por esse
transporte. Os contratos sao SINTETICOS (os moldes de tests/test_porta_social_t9.py).

    py tests/test_onda_social_coleta.py
"""
import contextlib
import io
import json
import os
import secrets
import shutil
import sys
import unittest
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
for _p in (RAIZ / "tests", RAIZ / "coleta", RAIZ / "ferramentas" / "maestro_social"):
    sys.path.insert(0, str(_p))
import test_coleta_continua as TC  # noqa: E402 — a bancada do agendador (servidor local, robo, Sala, portao)
import test_porta_social_t9 as T9  # noqa: E402 — os moldes de contrato social da porta
import maestro_social as MS  # noqa: E402
import teto_da_onda as TDO  # noqa: E402

C = TC.C
CA = TC.CA
LI = "IT-T5-970"
PERFIL_IG = "https://www.instagram.com/bayer_italia/"
REEL_IG = "https://www.instagram.com/reel/DcNkh7LCW4u/"
_AMBIENTE: dict = {}


def setUpModule():
    TC.setUpModule()                                               # teto manual 5 e pausa minima 0 (declarado la)
    for k in ("ITALY_OPS_ROOT", "SINTONIA_TETO_ONDA"):
        _AMBIENTE[k] = os.environ.get(k)


def tearDownModule():
    for k, v in _AMBIENTE.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    TC.tearDownModule()


def reel(sid, url):
    return {"SOURCE_ID": sid, "TERRITORY": "T5",
            "ACQUISITION": {"STRATEGY": "SCRAP_FASE", "EXECUTOR": "scrap-colheita", "FASE": "captura-reel",
                            "PLATFORM": "INSTAGRAM", "FILTROS": {"url": url},
                            "AUTORIZACAO": "D22 (DECISOES-DONO): Reel publico por URL directa"}}


class Social(TC.Base):
    """A bancada da coleta continua + um catalogo social numa raiz temporaria + o maestro real."""

    def setUp(self):
        super().setUp()
        ops = self.tmp / "ops"
        os.environ["ITALY_OPS_ROOT"] = str(ops)                    # o livro de corridas do maestro = o do ciclo
        self.ledger = ops / "data" / "collection-ledger" / "italy" / "runs.ndjson"
        self.ledger.parent.mkdir(parents=True)
        self.onda = TC.OndaFalsa(self.ledger, self.sala)
        self.raiz = self.tmp / "raiz"
        (self.raiz / "curadoria").mkdir(parents=True)
        (self.raiz / "ferramentas" / "big_collection").mkdir(parents=True)
        (self.raiz / "ferramentas" / "big_collection" / "COORTE-BIG-COLLECTION-V1.json").write_text(
            json.dumps({"PLANO": {"PAINEL_DO_GATE": {"READY_SOCIAL_TOTAL": 0}}}), encoding="utf-8")
        aviso = MS.AVISO
        MS.AVISO = self.tmp / "aviso.txt"                           # o maestro nunca escreve no aviso real
        self.addCleanup(setattr, MS, "AVISO", aviso)
        self.contratos: dict = {}
        self.chamadas_maestro = []
        self.desobedece = False
        self.pedidos_por_fonte = {"www.linkedin.com": 2, "media.licdn.com": 2}
        self.egresso_no_maestro = "IT"

    # ── o catalogo e o alimentador ───────────────────────────────────────────
    def catalogo(self, *contratos, transicoes=()):
        self.contratos = {c["SOURCE_ID"]: c for c in contratos}
        (self.raiz / "curadoria" / "italy_contracts_curator.json").write_text(
            json.dumps({"FONTES": list(contratos)}), encoding="utf-8")
        (self.raiz / "curadoria" / "LIFECYCLE-LEDGER-V1.json").write_text(json.dumps({"TRANSICOES": [
            {"SOURCE_ID": s, "NEW_STATE": e} for s, e in transicoes]}), encoding="utf-8")

    def alimentar(self, autorizado):
        return C.alimentar_linhas({"RODADAS": []}, raiz=self.raiz, autorizado_social=autorizado)

    # ── o transporte falso: o papel do Scrap video-linkedin, contra o servidor local ──
    def lancar(self, sid, pedido, pasta):
        rid = "IT-T5-%s-%s" % (datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S"), secrets.token_hex(8))
        feitos: dict = {}
        try:
            for host, n in self.pedidos_por_fonte.items():
                for _ in range(n):
                    if not self.desobedece:
                        TDO.reservar(host, quem="TESTE")           # o freio REAL: sem lugar, o pedido nao sai
                    rq = urllib.request.Request("http://127.0.0.1:%d/" % TC.PORTA, headers={"Host": host})
                    TC.SEM_PROXY.open(rq, timeout=10).read()
                    if not self.desobedece:
                        TDO.registrar_resposta(host, 200)
                    feitos[host] = feitos.get(host, 0) + 1
        except TDO.TetoDaOnda:
            pass
        with open(self.ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps({"RUN_ID": rid, "CORTESIA": {"PEDIDOS_POR_HOST": feitos}}) + "\n")
        if feitos:
            self.sala.grava(rid)
        return {"STATUS": "SUCCEEDED" if feitos else "FAILED", "RUN_ID": rid, "CODIGO": 0}

    # ── o maestro REAL, no processo, com o transporte falso ──────────────────
    def maestro(self, fontes, saida):
        self.chamadas_maestro.append(list(fontes))
        linhas = [{"SOURCE_ID": s, "FASE": self.contratos[s]["ACQUISITION"].get("FASE"), "NA_ONDA": True}
                  for s in fontes]
        antes = os.environ.get("SINTONIA_TETO_ONDA")
        try:
            return MS.correr(saida, so=list(fontes), egresso=lambda: {"PAIS": self.egresso_no_maestro},
                             lancar=self.lancar, precondicoes=lambda: [], gate=lambda s: "ELIGIBLE",
                             contratos_fn=lambda: self.contratos,
                             plano_fn=lambda: MS.plano(canario=False, so=list(fontes), linhas=linhas))
        finally:
            if antes is None:
                os.environ.pop("SINTONIA_TETO_ONDA", None)
            else:
                os.environ["SINTONIA_TETO_ONDA"] = antes

    def onda_social(self, sha, fontes, pasta, historico, retomar):
        return C.onda_social_real(sha, fontes, pasta, historico, retomar, maestro=self.maestro, foto=self.sala.foto)

    def pecas(self, **kw):
        kw.setdefault("onda_social", self.onda_social)
        return super().pecas(**kw)

    def ciclo_social(self, autorizado=True, extra=None, **kw):
        a = self.alimentar(autorizado)
        cands = {"SOCIAL": a["SOCIAL"]["CANDIDATAS"]}
        cands.update(extra or {})
        return a, self.ciclo(cands, bloqueios={n: x for n, x in a.items() if n in cands and x["ESTADO"]}, **kw)


# ── 1. aceite + flag: a onda corre e regista RUN_ID ───────────────────────────
class OndaSocialCorre(Social):
    def test_aceite_com_flag_a_onda_social_corre_e_regista_run_id(self):
        self.catalogo(T9.linkedin(LI))
        a, r = self.ciclo_social()
        s = a["SOCIAL"]
        self.assertIsNone(s["ESTADO"], s)
        self.assertEqual([c["SOURCE_ID"] for c in s["CANDIDATAS"]], [LI])
        self.assertEqual(set(s["CANDIDATAS"][0]["DOMINIOS"]), {"linkedin.com", "licdn.com"})
        self.assertEqual(s["CANDIDATAS"][0]["LINHA"], "SOCIAL")
        self.assertIsNone(r["PARA"], r)
        self.assertEqual(self.chamadas_maestro, [[LI]])
        self.assertEqual(self.onda.chamadas, [])                   # nunca a onda dos SITES
        ln = r["LINHAS"]["SOCIAL"]
        self.assertEqual(ln["CORRERAM"], [LI], ln)
        self.assertEqual(len(r["RUN_IDS"]), 1, r["RUN_IDS"])
        self.assertTrue(r["RUN_IDS"][0].startswith("IT-T5-"))
        self.assertEqual(ln["RUN_IDS"], r["RUN_IDS"])
        self.assertEqual(TC._por_dominio(TC.CONTAGEM), {"linkedin.com": 2, "licdn.com": 2})
        self.assertEqual(ln["PEDIDOS"], 4)
        self.assertEqual(r["PROVA_TETO_CICLO"]["ESTADO"], "PASS", r["PROVA_TETO_CICLO"])
        self.assertEqual(r["PROVA_TETO_24H"]["ESTADO"], "PASS")
        self.assertEqual(r["RECONCILIACAO"]["ESTADO"], "PASS", r["RECONCILIACAO"])
        self.assertEqual(self.robo.eventos, ["PARAR", "TIRAR_FLAG", "LANCAR"])
        self.assertEqual(len(self.backups), 1)
        # o RUN_ID fica no livro de ciclos (e a prova de 24 h do proximo ciclo le-o la)
        ultimo = json.loads((self.base / C.CICLOS_F).read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(ultimo["RUN_IDS"], r["RUN_IDS"])
        # e cada pedido reservou no livro da cortesia de 24 h (o freio do transporte, nao so a contagem)
        reservas = [e for e in CA.ler_eventos(self.livro24) if e["TIPO"] == "RESERVA"]
        self.assertEqual(sorted({e["DOMINIO"] for e in reservas}), ["licdn.com", "linkedin.com"])
        self.assertEqual(len(reservas), 4)
        # o estado da onda social tem o formato que o ciclo, a prova e o relatorio leem
        e = json.loads((Path(ln["PASTA"]) / "ONDA-WEB-ESTADO.json").read_text(encoding="utf-8"))
        self.assertEqual([x["SOURCE_ID"] for x in e["FONTES"] if x["CORREU"]], [LI])
        self.assertEqual(e["FONTES"][0]["PEDIDOS_POR_DOMINIO"], {"linkedin.com": 2, "licdn.com": 2})
        self.assertEqual(json.loads((Path(ln["PASTA"]) / "TETO-ONDA.json").read_text(encoding="utf-8")),
                         {"PEDIDOS_POR_DOMINIO": {"linkedin.com": 2, "licdn.com": 2}})

    def test_feita_nao_volta_na_mesma_passagem(self):
        self.catalogo(T9.linkedin(LI))
        self.ciclo_social()
        _, r = self.ciclo_social()
        self.assertEqual(self.chamadas_maestro, [[LI]], r["LINHAS"]["SOCIAL"])

    def test_social_e_sites_no_mesmo_ciclo_cada_um_na_sua_onda(self):
        self.catalogo(T9.linkedin(LI))
        _, r = self.ciclo_social(extra=self.sites(["IT-T5-080"]))
        self.assertIsNone(r["PARA"], r)
        self.assertEqual([c["FONTES"] for c in self.onda.chamadas], [["IT-T5-080"]])
        self.assertEqual(self.chamadas_maestro, [[LI]])
        self.assertEqual(len(r["RUN_IDS"]), 2)
        self.assertEqual(r["RECONCILIACAO"]["ESTADO"], "PASS", r["RECONCILIACAO"])

    def test_o_maestro_real_e_chamado_com_a_flag_e_so_as_fontes_dadas(self):
        cmds = []

        def run(cmd, **kw):
            cmds.append(cmd)
            return mock.Mock(returncode=0, stdout="", stderr="")
        self.assertEqual(C.correr_maestro_real([LI, "IT-T5-971"], self.tmp / "m", run=run), 0)
        cmd = cmds[0]
        self.assertTrue(str(cmd[1]).replace("\\", "/").endswith("ferramentas/maestro_social/maestro_social.py"), cmd)
        self.assertIn("--correr", cmd)
        self.assertIn("--autorizado-pelo-dono", cmd)
        self.assertIn("--fontes=%s,IT-T5-971" % LI, cmd)
        self.assertIn("--saida=%s" % (self.tmp / "m"), cmd)
        self.assertNotIn("--canario", cmd)                         # o canario e decisao a parte

    def test_as_pecas_reais_tem_a_onda_social(self):
        self.assertIs(C.pecas_reais()["onda_social"], C.onda_social_real)
        social = next(l for l in C.LINHAS if l["LINHA"] == "SOCIAL")
        self.assertIn("maestro_social", social["ONDA"])


# ── 2. sem a flag: 0 pedidos ──────────────────────────────────────────────────
class SemFlag(Social):
    def test_sem_flag_zero_pedidos_e_bloqueio_com_nome(self):
        self.catalogo(T9.linkedin(LI))
        a, r = self.ciclo_social(autorizado=False)
        s = a["SOCIAL"]
        self.assertEqual(s["ESTADO"], "BLOQUEADA_PERMISSAO_SOCIAL", s)
        self.assertIn("--autorizado-pelo-dono", s["PORQUE"])
        self.assertEqual(s["CANDIDATAS"], [])
        self.assertEqual(s["UNIDADES_GOVERNADAS"], 1)
        self.assertNotIn("BLOQUEADA_CAPACIDADE", [m["ESTADO"] for m in s["MOTIVOS"]])   # a onda ja existe
        self.assertEqual(r["LINHAS"]["SOCIAL"]["ESTADO"], "BLOQUEADA_PERMISSAO_SOCIAL")
        self.assertEqual(self.chamadas_maestro, [])
        self.assertEqual(TC.CONTAGEM, {})
        self.assertEqual(self.robo.eventos, [])

    def test_por_omissao_o_alimentador_nao_autoriza(self):
        self.catalogo(T9.linkedin(LI))
        a = C.alimentar_linhas({"RODADAS": []}, raiz=self.raiz)
        self.assertEqual(a["SOCIAL"]["ESTADO"], "BLOQUEADA_PERMISSAO_SOCIAL")
        self.assertEqual(a["SOCIAL"]["CANDIDATAS"], [])

    def _main(self, *extra):
        plano = self.tmp / "RODADAS-PLANO.json"
        plano.write_text(json.dumps(TC._plano([])), encoding="utf-8")
        original = C.CATALOGOS["SOCIAL"]
        buf = io.StringIO()
        with mock.patch.dict(C.CATALOGOS, {"SOCIAL": lambda _r: original(self.raiz)}), \
                mock.patch.object(C, "portao_da_fonte_real", TC._admite_tudo), contextlib.redirect_stdout(buf):
            rc = C.main(["--ensaio-a-seco", "--base=%s" % self.base, "--plano=%s" % plano,
                         "--teto-24h=%s" % self.livro24, "--livros-do-dia=%s" % (self.tmp / "ondas")] + list(extra))
        self.assertEqual(rc, 0)
        return json.loads(buf.getvalue())

    def test_o_servico_sem_a_flag_fica_desligado(self):
        self.catalogo(T9.linkedin(LI))
        ln = self._main()["LINHAS"]["SOCIAL"]
        self.assertEqual((ln["ESTADO"], ln["FONTES"], ln["PEDIDOS_PREVISTOS"]), ("BLOQUEADA_PERMISSAO_SOCIAL", [], 0))

    def test_com_a_flag_o_ensaio_mostra_a_fonte_e_os_pedidos_previstos(self):
        self.catalogo(T9.linkedin(LI))
        ln = self._main("--autorizado-pelo-dono")["LINHAS"]["SOCIAL"]
        self.assertEqual((ln["ESTADO"], ln["FONTES"], ln["PEDIDOS_PREVISTOS"]), ("A_CORRER", [LI], 4), ln)
        self.assertEqual(self.chamadas_maestro, [])                 # a seco: nada corre
        self.assertEqual(TC.CONTAGEM, {})


# ── 3. recusada pela porta: 0 pedidos ─────────────────────────────────────────
class RecusadaNaPorta(Social):
    def test_unidade_recusada_pela_porta_zero_pedidos(self):
        self.catalogo(T9.linkedin("IT-T5-971", autorizacao=None))
        a, r = self.ciclo_social()
        s = a["SOCIAL"]
        self.assertEqual(s["ESTADO"], "SEM_CATALOGO", s)
        self.assertEqual(s["PORTA_SOCIAL"]["RECUSADAS"], {"SEM_RASTRO_DE_AUTORIZACAO": ["IT-T5-971"]})
        self.assertEqual(s["CANDIDATAS"], [])
        self.assertEqual(self.chamadas_maestro, [])
        self.assertEqual(TC.CONTAGEM, {})
        self.assertEqual(self.robo.eventos, [])

    def test_so_a_aceite_chega_a_onda(self):
        self.catalogo(T9.linkedin(LI), T9.linkedin("IT-T5-971", "outra", autorizacao=None),
                      T9.canal_youtube("IT-T5-972"))
        a, r = self.ciclo_social()
        self.assertEqual([c["SOURCE_ID"] for c in a["SOCIAL"]["CANDIDATAS"]], [LI])
        self.assertEqual(self.chamadas_maestro, [[LI]])
        self.assertIsNone(r["PARA"], r)

    def test_aceite_sem_rota_na_onda_social_nao_corre_e_diz_porque(self):
        # um feed READY aceite pela porta: o maestro nao tem fase para ele (T9 NAO SEI: PEDIDO_RECUSADO:KeyError).
        # Nada de rota nova: a linha diz BLOQUEADA_CAPACIDADE com o nome da fonte
        self.catalogo(T9.feed("IT-T5-973"), transicoes=[("IT-T5-973", T9.READY)])
        a, r = self.ciclo_social()
        s = a["SOCIAL"]
        self.assertEqual(s["PORTA_SOCIAL"]["ACEITES"], ["IT-T5-973"])
        self.assertEqual(s["ESTADO"], "BLOQUEADA_CAPACIDADE", s)
        self.assertIn("IT-T5-973", s["PORQUE"])
        self.assertEqual(s["CANDIDATAS"], [])
        self.assertEqual(self.chamadas_maestro, [])


# ── 4. Instagram: so a URL directa do Reel ────────────────────────────────────
class InstagramSoReel(Social):
    def test_instagram_com_url_de_perfil_recusa(self):
        self.catalogo(reel("IT-T5-980", PERFIL_IG))
        a, r = self.ciclo_social()
        s = a["SOCIAL"]
        self.assertEqual(s["PORTA_SOCIAL"]["RECUSADAS"], {"LISTAGEM_NAO_AUTORIZADA": ["IT-T5-980"]}, s)
        self.assertEqual(s["CANDIDATAS"], [])
        self.assertEqual(self.chamadas_maestro, [])
        self.assertEqual(TC.CONTAGEM, {})
        t = T9.P.triagem_social({"IT-T5-980": reel("IT-T5-980", PERFIL_IG)}, estado_de=T9.estados())
        self.assertEqual(t["RECUSADAS"][0]["MOTIVO"], "LISTAGEM_NAO_AUTORIZADA")
        self.assertIn(PERFIL_IG, t["RECUSADAS"][0]["PORQUE"])
        self.assertIn("D157", t["RECUSADAS"][0]["PORQUE"])

    def test_instagram_sem_url_tambem_nao_passa(self):
        t = T9.P.triagem_social({"IT-T5-981": reel("IT-T5-981", "")}, estado_de=T9.estados())
        self.assertEqual(t["ACEITES"], [])

    def test_reel_directo_nao_e_listagem_mas_continua_sem_conferidor(self):
        # o Reel por URL directa NAO e recusado como listagem; fica fora por outra razao, com nome: o Curator nao
        # tem conferidor para as fases de Reel (T9 NAO SEI). Esta onda nao abre isso
        t = T9.P.triagem_social({"IT-T5-982": reel("IT-T5-982", REEL_IG)}, estado_de=T9.estados())
        self.assertEqual(t["RECUSADAS"][0]["MOTIVO"], "ROTA_NAO_CONFERIDA", t["RECUSADAS"][0])
        self.assertNotIn("LISTAGEM_NAO_AUTORIZADA", [m["MOTIVO"] for m in t["RECUSADAS"][0]["MOTIVOS"]])

    def test_reel_aceite_um_dia_nao_tem_rota_na_onda(self):
        # se um dia a porta aceitar um Reel, a onda social nao o corre por uma rota inventada: o maestro so tem
        # video-linkedin (e canal/audio-youtube, fora do ambito)
        cands, sem_rota = C.candidatas_sociais(["IT-T5-983"], {"IT-T5-983": reel("IT-T5-983", REEL_IG)})
        self.assertEqual(cands, [])
        self.assertIn("IT-T5-983", sem_rota)


# ── 5. as mesmas guardas da onda dos SITES ───────────────────────────────────
class Guardas(Social):
    def setUp(self):
        super().setUp()
        self.catalogo(T9.linkedin(LI))

    def test_egresso_antes_fora_de_it_zero_pedidos(self):
        _, r = self.ciclo_social(pecas=self.pecas(portao=TC.Portao(falha_na_chamada=1)))
        self.assertEqual(r["PARA"], "EGRESSO_ANTES")
        self.assertEqual(self.chamadas_maestro, [])
        self.assertEqual(TC.CONTAGEM, {})

    def test_egresso_depois_fora_de_it_para(self):
        _, r = self.ciclo_social(pecas=self.pecas(portao=TC.Portao(falha_na_chamada=2)))
        self.assertEqual(r["PARA"], "EGRESSO_DEPOIS")

    def test_backup_sem_prova_vale_zero_pedidos(self):
        _, r = self.ciclo_social(pecas=self.pecas(backup=lambda p: {"PROVA_VALE": False}))
        self.assertEqual(r["PARA"], "BACKUP_SEM_PROVA_VALE")
        self.assertEqual(self.chamadas_maestro, [])
        self.assertEqual(self.robo.eventos, [])

    def test_ram_abaixo_de_5gb_zero_pedidos(self):
        self.ram = 2.0
        _, r = self.ciclo_social()
        self.assertEqual(r["PARA"], "RAM_ABAIXO_DE_5GB")
        self.assertEqual(self.chamadas_maestro, [])

    def test_transporte_que_nao_reserva_prova_teto_fail(self):
        self.desobedece = True
        self.pedidos_por_fonte = {"www.linkedin.com": 7}
        _, r = self.ciclo_social()
        self.assertEqual(r["PARA"], "PROVA_TETO_FAIL", r.get("PROVA_TETO_CICLO"))

    def test_o_freio_do_transporte_corta_no_livro_de_24h(self):
        # o livro de 24 h ja tem 4 reservas a linkedin.com de outra linha: o agendador nao oferece a fonte (4+4 > 5)
        for _ in range(4):
            TC.R24.reservar("www.linkedin.com", 1, run_id="OUTRA", linha="OUTRA")
            CA.registrar_resposta("www.linkedin.com", 200, {}, run_id="OUTRA", linha="OUTRA")
        _, r = self.ciclo_social()
        self.assertEqual(self.chamadas_maestro, [])
        e = [x for x in r["ESPERAM"] if x["SOURCE_ID"] == LI]
        self.assertEqual(e[0]["PORQUE"], "DOMINIO_FECHADO", e)
        self.assertIn("linkedin.com", e[0]["DOMINIOS_FECHADOS"])

    def test_reconciliacao_que_nao_bate_para(self):
        self.sala.mente = True
        _, r = self.ciclo_social()
        self.assertEqual(r["PARA"], "RECONCILIACAO_FAIL")

    def test_maestro_que_para_para_o_servico(self):
        self.egresso_no_maestro = "BR"                              # o maestro mede antes de cada fonte e PARA
        _, r = self.ciclo_social()
        self.assertTrue(str(r["PARA"]).startswith("ONDA_PAROU_SOCIAL"), r["PARA"])
        self.assertEqual(TC.CONTAGEM, {})

    def test_maestro_que_nao_escreve_estado_para(self):
        def mudo(fontes, saida):
            self.chamadas_maestro.append(list(fontes))
            return 0
        _, r = self.ciclo_social(pecas=self.pecas(onda_social=lambda *a: C.onda_social_real(
            *a, maestro=mudo, foto=self.sala.foto)))
        self.assertEqual(self.chamadas_maestro, [[LI]])
        self.assertTrue(str(r["PARA"]).startswith("ONDA_PAROU_SOCIAL"), r["PARA"])

    def test_livro_da_onda_ilegivel_nao_passa_por_nada_a_provar(self):
        def estraga(fontes, saida):
            self.chamadas_maestro.append(list(fontes))
            (saida / "ONDA-01").mkdir(parents=True)
            (saida / "ONDA-01" / "TETO-ONDA.json").write_text("{estragado", encoding="utf-8")
            (saida / MS.ESTADO).write_text(json.dumps({"FONTES": [], "ONDAS": [], "PAROU": None}), encoding="utf-8")
            return 0
        _, r = self.ciclo_social(pecas=self.pecas(onda_social=lambda *a: C.onda_social_real(
            *a, maestro=estraga, foto=self.sala.foto)))
        self.assertEqual(r["PARA"], "PROVA_TETO_NAO_SEI", r)

    def test_sem_foto_da_sala_nao_ha_pass(self):
        _, r = self.ciclo_social(pecas=self.pecas(onda_social=lambda *a: C.onda_social_real(
            *a, maestro=self.maestro, foto=lambda: None)))
        self.assertEqual(r["PARA"], "RECONCILIACAO_NAO_SEI", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
