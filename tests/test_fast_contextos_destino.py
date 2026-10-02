# -*- coding: utf-8 -*-
"""FDS v0.2 (ordem do dono 02/10): o cerebro FAST le os dominios existentes (sec.11) e o CRUZAMENTO-COMERCIAL.json
ganha so DESTINO_FERRAMENTA + TITULO_IT + TEXTOS_VISIVEIS_IT. Sem LLM (custo 0)."""
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from motor import fast_cruzamento_comercial as FC  # noqa: E402

HOJE = date(2026, 10, 2)
FATOS = {"F1": {"FACT_ID": "F1", "DOCUMENT_ID": "D1", "SOURCE_ID": "S1", "URL": "https://a.it/x", "quando": "2026",
                "evidencias": {"fato": "x"}}}
REF = {"USE_IDS": set(), "FRESCOR": "OK", "CARIMBO": {}}
FEN = {"IDS": {"IT-PHEN-001"}}
CTX = {"IDS": {"CTX-CLI-001": "CLI", "IT-RES-001": "RES"}}
HIST = {"IDS": {"HIST-FAST-1-C01"}}


def _obj(classe="SINAL", destino=None, ctx_ids=None):
    campos = {k: {"valor": "NAO_SEI", "FACT_IDs": ["F1"]} for k in FC.CAMPOS}
    o = {"ID": "C01", "CLASSE": classe, "CAMPOS": campos, "FACT_IDs": ["F1"]}
    if destino is not None:
        o["DESTINO_FERRAMENTA"] = destino
    if ctx_ids is not None:
        o["CONTEXTO_IDs"] = ctx_ids
    return o


def _conf(o):
    return FC.conferir({"objetos": [o]}, FATOS, [], REF, FEN, hoje=HOJE, ctx=CTX, hist=HIST)


class Destino(unittest.TestCase):
    def test_sinal_nao_vai_ao_opportunity_radar(self):
        ok, _ = _conf(_obj("SINAL", ["OPPORTUNITY_RADAR", "MARKET_PULSE"]))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["FUTURE_RADAR", "MARKET_PULSE"])
        self.assertEqual(ok[0]["DESTINO_RECUSADO"], ["OPPORTUNITY_RADAR"])
        self.assertEqual(ok[0]["DESTINO_DO_MODELO"], ["OPPORTUNITY_RADAR", "MARKET_PULSE"])

    def test_oportunidade_pode_ir_ao_opportunity_radar(self):
        ok, _ = _conf(_obj("OPORTUNIDADE", ["OPPORTUNITY_RADAR", "ACTION_BRIEF"]))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["OPPORTUNITY_RADAR", "ACTION_BRIEF"])

    def test_destino_fora_da_lista_recusado_e_classe_garante_ferramenta(self):
        o = _obj("GAP", ["DASHBOARD"])
        for k in FC.NECESSIDADE_DO_GAP:  # GAP com a necessidade fechada (senao a R1 rebaixa a SINAL)
            o["CAMPOS"][k]["valor"] = "x"
        ok, _ = _conf(o)
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["PORTAFOGLIO"])
        self.assertEqual(ok[0]["DESTINO_RECUSADO"], ["DASHBOARD"])

    def test_sem_destino_do_modelo_usa_a_classe(self):
        ok, _ = _conf(_obj("LEAD"))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["FUTURE_RADAR"])


class ContextoIds(unittest.TestCase):
    def test_contexto_inexistente_rejeita(self):
        ok, rej = _conf(_obj(ctx_ids=["CTX-CLI-999"]))
        self.assertEqual(ok, [])
        self.assertIn("CONTEXTO_ID_INEXISTENTE:CTX-CLI-999", rej[0]["PROBLEMAS"])

    def test_contexto_existente_passa_e_conta_dominio(self):
        ok, rej = _conf(_obj(ctx_ids=["CTX-CLI-001", "IT-RES-001", "HIST-FAST-1-C01"]))
        self.assertEqual(rej, [])
        self.assertEqual(ok[0]["CONTEXTOS_CITADOS"], ["CLI", "HISTORICO", "RES"])

    def test_contexto_sozinho_sem_fato_rejeita(self):
        o = _obj(ctx_ids=["CTX-CLI-001"])
        o["FACT_IDs"] = []
        for c in o["CAMPOS"].values():
            c["FACT_IDs"] = []
        _, rej = _conf(o)
        self.assertIn("SEM_FACT_ID", rej[0]["PROBLEMAS"])


class Leitores(unittest.TestCase):
    def test_dominio_ausente_e_declarado_nao_inventado(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "AGROMET-CONDITIONS.json").write_text(json.dumps(
                {"BUILT_AT": "x", "RECORDS": [{"tipo": "T", "o_que": "chuva"}]}), encoding="utf-8")
            c = FC.contexto_dominios(t)
        self.assertEqual(c["CARIMBO"]["CLI"]["ESTADO"], "LIDO")
        self.assertEqual(c["CARIMBO"]["MKT"]["ESTADO"], "NAO_DISPONIVEL")
        self.assertEqual(list(c["IDS"]), ["CTX-CLI-001"])

    def test_dominios_reais_carregam_todos(self):
        c = FC.contexto_dominios()
        lidos = [s for s, v in c["CARIMBO"].items() if v.get("ESTADO") == "LIDO"]
        self.assertEqual(len(lidos), len(FC.DOMINIOS))

    def test_historico_so_rodadas_anteriores(self):
        with tempfile.TemporaryDirectory() as t:
            for n in ("FAST-1", "FAST-2", "FAST-3"):
                (Path(t) / n).mkdir()
                (Path(t) / n / "CRUZAMENTO-COMERCIAL.json").write_text(json.dumps(
                    {"OBJETOS": [{"ID": "C01", "CLASSE": "SINAL", "TITULO": n}]}), encoding="utf-8")
            h = FC.contexto_historico(Path(t) / "FAST-2")
        self.assertEqual(h["RODADAS"], ["FAST-1"])
        self.assertEqual(h["IDS"], {"HIST-FAST-1-C01"})


if __name__ == "__main__":
    unittest.main()
