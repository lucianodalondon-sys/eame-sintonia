# -*- coding: utf-8 -*-
"""B3 — a porta de contratos do bot (bloco 3 do G1, D10) e a revalidacao das elegiveis.

Sem rede, sem escrita fora de pastas temporarias.
"""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
import fila as F                  # noqa: E402
import gatilho_discovery as GD    # noqa: E402
import reconciliar_livros as R    # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "aplicar_desbloqueio", RAIZ / "scripts" / "desbloqueio" / "aplicar_desbloqueio.py")
G1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G1)

FOTO = Path.home() / "sintonia-gabarito" / "B3-SNAPSHOT-20260923T061509Z"
AGORA = datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)


def _c(sid, index, padrao="^x$", **extra):
    return dict({"SOURCE_ID": sid, "TERRITORY": "T7",
                 "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL",
                                 "INDEX_URL": index, "LINK_PATTERN": padrao, "MAX_TARGETS": 5}}, **extra)


def _prova(sid, index, padrao="^x$", doc=None):
    return ("M3", {"SOURCE_ID": sid, "CANARIO": {"URL": doc or index + "materia-um-dois"}},
            (index, padrao), "2026-09-22T23:00:00+00:00")


SID = "IT-T7-033"   # uma das 7 da D10


class PortaDeContratos(unittest.TestCase):
    def correr(self, portao, bot, provas, d10="A"):
        dono = {}
        for _, l, _, _ in provas:
            dono.setdefault(l["CANARIO"]["URL"], l["SOURCE_ID"])
        return G1.contrato_unico({c["SOURCE_ID"]: c for c in portao}, {"FONTES": bot}, provas, dono, d10)

    def test_com_prova_o_contrato_do_portao_entra_no_bot_com_origem(self):
        p = _c(SID, "https://a.it/news/", ROUTE_PROVENANCE={"MISSAO": "AQUISICAO-DETALHE-V1",
                                                           "PROVADO_EM": "2026-09-21T03:04:17"})
        bot, ac = self.correr([p], [_c(SID, "https://a.it/")], [_prova(SID, "https://a.it/news/")])
        b = bot["FONTES"][0]
        self.assertEqual(p["ACQUISITION"], b["ACQUISITION"])
        cu = b["CONTRATO_UNICO"]
        self.assertEqual(("D10", "A", True), (cu["DECISAO"], cu["OPCAO"], cu["PRECISA_DE_REMEDIR"]))
        self.assertEqual("2026-09-21T03:04:17", cu["ORIGEM"]["PROVADO_EM"])
        self.assertEqual("https://a.it/", cu["ACQUISITION_ANTERIOR"]["INDEX_URL"])
        self.assertEqual(["APLICA"], [a["ACAO"] for a in ac])

    def test_segunda_passagem_e_ja_aplicada(self):
        p = _c(SID, "https://a.it/news/")
        bot, _ = self.correr([p], [_c(SID, "https://a.it/")], [_prova(SID, "https://a.it/news/")])
        bot2, ac2 = self.correr([p], bot["FONTES"], [_prova(SID, "https://a.it/news/")])
        self.assertEqual(["JA_APLICADA"], [a["ACAO"] for a in ac2])
        self.assertEqual(bot, bot2)

    def test_sem_prova_da_aquisicao_que_fica_salta_e_vale_c(self):
        bot, ac = self.correr([_c(SID, "https://a.it/news/")], [_c(SID, "https://a.it/")],
                              [_prova(SID, "https://a.it/")])          # prova da OUTRA aquisicao
        self.assertEqual("SALTA", ac[0]["ACAO"])
        self.assertIn("vale C", ac[0]["PORQUE"])
        self.assertEqual("https://a.it/", bot["FONTES"][0]["ACQUISITION"]["INDEX_URL"])

    def test_fora_das_7_da_d10_nao_se_toca(self):
        s = "IT-T7-041"
        bot, ac = self.correr([_c(s, "https://b.it/news/")], [_c(s, "https://b.it/")],
                              [_prova(s, "https://b.it/news/")])
        self.assertEqual("SALTA", ac[0]["ACAO"])
        self.assertIn("fora das 7", ac[0]["PORQUE"])
        self.assertNotIn("CONTRATO_UNICO", bot["FONTES"][0])

    def test_sem_d10_nao_escolhe(self):
        _, ac = self.correr([_c(SID, "https://a.it/news/")], [_c(SID, "https://a.it/")],
                            [_prova(SID, "https://a.it/news/")], d10=None)
        self.assertEqual("SALTA", ac[0]["ACAO"])

    def test_opcao_b_nao_escreve_pela_porta_do_bot(self):
        bot, ac = self.correr([_c(SID, "https://a.it/news/")], [_c(SID, "https://a.it/")],
                              [_prova(SID, "https://a.it/")], d10="B")
        self.assertEqual("SALTA", ac[0]["ACAO"])
        self.assertEqual("https://a.it/", bot["FONTES"][0]["ACQUISITION"]["INDEX_URL"])

    def test_fonte_que_o_bot_nao_tem_nao_entra(self):
        bot, ac = self.correr([_c("IT-T5-041", "https://crpv.it/news/")], [_c(SID, "https://a.it/")],
                              [_prova("IT-T5-041", "https://crpv.it/news/")])
        self.assertEqual([SID], [c["SOURCE_ID"] for c in bot["FONTES"]])
        self.assertEqual([], ac)

    def test_documento_de_outra_fonte_e_duplicada(self):
        doc = "https://a.it/news/materia-um-dois"
        provas = [_prova("IT-T7-042", "https://z.it/", doc=doc), _prova(SID, "https://a.it/news/", doc=doc)]
        _, ac = self.correr([_c(SID, "https://a.it/news/")], [_c(SID, "https://a.it/")], provas)
        self.assertIn("DUPLICADA", ac[0]["PORQUE"])

    def test_invariante_outro_campo_do_bot_nao_muda(self):
        a = {"FONTES": [_c(SID, "https://a.it/")]}
        d = copy.deepcopy(a)
        d["FONTES"][0]["TERRITORY"] = "T9"
        with self.assertRaises(G1.InvarianteQuebrado):
            G1.invariantes_do_bot(a, d, {SID})
        d2 = copy.deepcopy(a)
        d2["FONTES"][0]["ACQUISITION"]["INDEX_URL"] = "https://a.it/news/"
        with self.assertRaises(G1.InvarianteQuebrado):
            G1.invariantes_do_bot(a, d2, set())            # sem autorizacao D10


def _livro(*linhas):
    return {"TRANSICOES": [{"SOURCE_ID": s, "NEW_STATE": "READY_FOR_COLLECTION", "OBSERVED_AT": q,
                            "EVIDENCE_REF": "EV-%s" % s, "PREVIOUS_STATE": "CANARY_PENDING"}
                           for s, q in linhas]}


def _vr(sid, quando):
    return {"SOURCE_ID": sid, "TASK_TYPE": F.VALIDATE_ROUTE, "STATUS": F.DONE,
            "UPDATED_AT": quando.isoformat()}


class Revalidar(unittest.TestCase):
    VELHA = (AGORA - timedelta(days=10)).isoformat()
    NOVA = (AGORA - timedelta(days=2)).isoformat()

    def cands(self, livro, elegiveis, tarefas=(), contratos=None):
        ctx = {"livro": livro, "evidencias": {}, "contratos": contratos or {}}
        with mock.patch("collection_gate.elegiveis", return_value=list(elegiveis)):
            return GD.candidatas_a_revalidar(AGORA, ctx=ctx, tarefas=list(tarefas))

    def test_elegivel_com_prova_velha_e_re_medida(self):
        c = self.cands(_livro(("IT-T7-001", self.VELHA)), ["IT-T7-001"])
        self.assertEqual([("IT-T7-001", "PROVA_VELHA")], [(x["SOURCE_ID"], x["MOTIVO"]) for x in c])

    def test_elegivel_com_prova_recente_nao(self):
        self.assertEqual([], self.cands(_livro(("IT-T7-001", self.NOVA)), ["IT-T7-001"]))

    def test_ready_que_o_portao_nao_deixa_colher_nao_e_re_medida(self):
        self.assertEqual([], self.cands(_livro(("IT-T7-001", self.VELHA)), []))

    def test_anti_eco_validate_route_recente_nao_repete_mesmo_sem_linha_no_livro(self):
        c = self.cands(_livro(("IT-T7-001", self.VELHA)), ["IT-T7-001"],
                       tarefas=[_vr("IT-T7-001", AGORA - timedelta(days=1))])
        self.assertEqual([], c)

    def test_validate_route_antiga_nao_impede(self):
        c = self.cands(_livro(("IT-T7-001", self.VELHA)), ["IT-T7-001"],
                       tarefas=[_vr("IT-T7-001", AGORA - timedelta(days=9))])
        self.assertEqual(1, len(c))

    def test_contrato_novo_da_d10_e_re_medido_logo_uma_vez(self):
        contratos = {SID: {"CONTRATO_UNICO": {"APLICADO_EM": (AGORA - timedelta(days=1)).isoformat()}}}
        c = self.cands(_livro((SID, self.NOVA)), [], contratos=contratos)
        self.assertEqual([(SID, "CONTRATO_NOVO")], [(x["SOURCE_ID"], x["MOTIVO"]) for x in c])
        depois = self.cands(_livro((SID, self.NOVA)), [], contratos=contratos,
                            tarefas=[_vr(SID, AGORA - timedelta(hours=1))])
        self.assertEqual([], depois)

    def test_enfileira_no_maximo_por_volta_e_na_fila_isolada(self):
        with tempfile.TemporaryDirectory() as d:
            antes = F.FILA
            F.FILA = Path(d) / "FILA.json"
            try:
                sids = ["IT-T7-%03d" % i for i in range(1, 9)]
                ctx = {"livro": _livro(*[(s, self.VELHA) for s in sids]), "evidencias": {}, "contratos": {}}
                with mock.patch("collection_gate.elegiveis", return_value=sids):
                    r = GD.revalidar_elegiveis(AGORA, ctx=ctx, tarefas=[])
                self.assertEqual((8, GD.REVALIDAR_POR_VOLTA), (r["CANDIDATAS"], len(r["ENFILEIRADAS"])))
                t = json.loads(F.FILA.read_text(encoding="utf-8"))["TAREFAS"]
                self.assertEqual({F.VALIDATE_ROUTE}, {x["TASK_TYPE"] for x in t})
            finally:
                F.FILA = antes


@unittest.skipUnless(FOTO.is_dir(), "fotografia B3 fora do Git e ausente nesta maquina: %s" % FOTO)
class EnsaioNaFotografia(unittest.TestCase):
    """O pacote inteiro, 2 passagens, sobre copias; depois dono_do_contrato das 7."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d = Path(cls.tmp.name)
        (d / "livro.json").write_bytes((FOTO / "portao_contratos.json").read_bytes())
        (d / "bot.json").write_bytes((FOTO / "bot_contratos.json").read_bytes())
        (d / "tabela.json").write_bytes((RAIZ / "regras" / "italy_contracts_onboarded.json").read_bytes())
        cls.saidas = []
        for _ in range(2):
            r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "desbloqueio" / "aplicar_desbloqueio.py"),
                                "--livro=%s" % (d / "livro.json"), "--tabela=%s" % (d / "tabela.json"),
                                "--livro-bot=%s" % (d / "bot.json"), "--d10=A",
                                "--ledger=%s" % (d / "ledger.jsonl"), "--escrever"],
                               cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")
            cls.saidas.append(r.stdout)
        L = {c["SOURCE_ID"]: c for c in json.loads((d / "livro.json").read_text(encoding="utf-8"))["FONTES"]}
        B = {c["SOURCE_ID"]: c for c in json.loads((d / "bot.json").read_text(encoding="utf-8"))["FONTES"]}
        cls.ctx = {"CONTRATOS_A": L, "CONTRATOS_C": B}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_segunda_passagem_escreve_zero(self):
        self.assertIn("ESCRITO: 0 alteracao", self.saidas[1])

    def test_seis_das_sete_ficam_com_um_so_dono(self):
        seis = ["IT-T10-018", "IT-T10-022", "IT-T7-017", "IT-T7-033", "IT-T7-042", "IT-T7-043"]
        self.assertEqual([None] * 6, [R.dono_do_contrato(s, self.ctx) for s in seis])

    def test_a_setima_sem_prova_continua_sem_dono_e_sai(self):
        self.assertIsNotNone(R.dono_do_contrato("IT-T5-049", self.ctx))

    def test_a_crpv_nao_entra_no_bot(self):
        self.assertIsNotNone(R.dono_do_contrato("IT-T5-041", self.ctx))


if __name__ == "__main__":
    unittest.main()
