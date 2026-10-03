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


VIS = {"COSA_SUCCEDE": "a", "PERCHE_CONTA": "b", "AZIONE": "c", "TEMPISTICA": "settembre 2026", "COLTURA": "mais",
       "LUOGO": "Lombardia", "CLASSIFICAZIONE": "Segnale", "FONTI": "Copagri, 9 settembre 2026"}
CRIT = {k: "x" for k in FC.CRITERIO_FUTURE_RADAR}


def _pub(classe="SINAL", destino=None, crit=None, vis=None, titulo="Titolo"):
    o = _obj(classe, destino)
    o["TITULO_IT"], o["TEXTOS_VISIVEIS_IT"] = titulo, dict(VIS if vis is None else vis)
    if crit is not None:
        o["CRITERIO_FUTURE_RADAR"] = crit
    return o


class Destino(unittest.TestCase):
    """RUN-AUTO-001 (ordem do dono 03/10): o modelo decide o destino na lista fechada de 11 nomes do Casco."""

    def test_lista_fechada_do_casco(self):
        self.assertEqual(set(FC.DESTINOS), {"OPPORTUNITY_RADAR", "FUTURE_RADAR", "PORTAFOGLIO", "COMPETITION",
                                            "MARKET_PULSE", "RESEARCH", "CROP_WINDOWS", "LABEL_INTELLIGENCE", "FIELD",
                                            "ARCHIVE", "NAO_PUBLICAR"})

    def test_sinal_nao_vai_ao_opportunity_radar(self):
        ok, _ = _conf(_pub("SINAL", ["OPPORTUNITY_RADAR", "MARKET_PULSE"]))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["MARKET_PULSE"])
        self.assertEqual(ok[0]["DESTINO_RECUSADO"], ["OPPORTUNITY_RADAR"])
        self.assertEqual(ok[0]["DESTINO_DO_MODELO"], ["OPPORTUNITY_RADAR", "MARKET_PULSE"])

    def test_classe_nao_empurra_para_o_future_radar(self):
        # defeito medido 03/10 (FAST-20261003T184228): 8/8 objetos no FUTURE_RADAR pela classe SINAL
        ok, _ = _conf(_pub("SINAL", ["MARKET_PULSE"]))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["MARKET_PULSE"])

    def test_future_radar_exige_os_quatro_elementos(self):
        ok, _ = _conf(_pub("SINAL", ["FUTURE_RADAR"], crit=dict(CRIT, HORIZONTE_OU_TRIGGER="NAO_SEI")))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["NAO_PUBLICAR"])
        self.assertIn("FUTURE_RADAR:FALTA_HORIZONTE_OU_TRIGGER", ok[0]["DESTINO_RECUSADO"])
        ok, _ = _conf(_pub("SINAL", ["FUTURE_RADAR"]))  # sem criterio nenhum
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["NAO_PUBLICAR"])

    def test_future_radar_com_os_quatro_elementos_passa(self):
        ok, _ = _conf(_pub("LEAD", ["FUTURE_RADAR"], crit=CRIT))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["FUTURE_RADAR"])

    def test_oportunidade_vai_ao_opportunity_radar(self):
        ok, _ = _conf(_pub("OPORTUNIDADE", ["OPPORTUNITY_RADAR", "LABEL_INTELLIGENCE"]))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["OPPORTUNITY_RADAR", "LABEL_INTELLIGENCE"])

    def test_destino_fora_da_lista_recusado(self):
        ok, _ = _conf(_pub("SINAL", ["DASHBOARD", "ACTION_BRIEF"]))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["NAO_PUBLICAR"])
        self.assertEqual(ok[0]["DESTINO_RECUSADO"], ["DASHBOARD", "ACTION_BRIEF"])

    def test_sem_destino_do_modelo_nao_publica(self):
        ok, _ = _conf(_pub("LEAD"))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["NAO_PUBLICAR"])

    def test_nao_publicar_e_exclusivo(self):
        ok, _ = _conf(_pub("SINAL", ["MARKET_PULSE", "NAO_PUBLICAR"]))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["NAO_PUBLICAR"])
        ok, _ = _conf(_pub("SINAL", ["ARCHIVE"], vis={}))  # arquivo nao exige texto de cliente
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["ARCHIVE"])

    def test_texto_italiano_incompleto_nao_vai_ao_cliente(self):
        vis = dict(VIS); del vis["TEMPISTICA"]
        ok, _ = _conf(_pub("SINAL", ["COMPETITION"], vis=vis))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["NAO_PUBLICAR"])
        self.assertEqual(ok[0]["TEXTO_IT_INCOMPLETO"]["FALTAM"], ["TEMPISTICA"])

    def test_placeholder_nao_vai_ao_cliente(self):
        for sujo in ("testo non ancora fornito", "text not yet provided", "vedi FACT_ID F-1", "NAO_SEI"):
            ok, _ = _conf(_pub("SINAL", ["RESEARCH"], vis=dict(VIS, FONTI=sujo)))
            self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["NAO_PUBLICAR"], sujo)
        ok, _ = _conf(_pub("SINAL", ["RESEARCH"], vis=dict(VIS, LUOGO="non noto")))  # desconhecido real e valido
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["RESEARCH"])

    def test_sem_titulo_nao_vai_ao_cliente(self):
        ok, _ = _conf(_pub("SINAL", ["FIELD"], titulo=""))
        self.assertEqual(ok[0]["DESTINO_FERRAMENTA"], ["NAO_PUBLICAR"])


class ContextoIds(unittest.TestCase):
    def test_contexto_inexistente_rejeita(self):
        ok, rej = _conf(_obj(ctx_ids=["CTX-CLI-999"]))
        self.assertEqual(ok, [])
        self.assertIn("CONTEXTO_ID_INEXISTENTE:CTX-CLI-999", rej[0]["PROBLEMAS"])

    def test_contexto_existente_passa_e_conta_dominio(self):
        ok, rej = _conf(_obj(ctx_ids=["CTX-CLI-001", "IT-RES-001", "HIST-FAST-1-C01"]))
        self.assertEqual(rej, [])
        self.assertEqual(ok[0]["CONTEXTOS_CITADOS"], ["CLI", "HISTORICO", "RES"])

    def test_fenologia_citada_em_contexto_ids_existe(self):
        ok, rej = _conf(_obj(ctx_ids=["IT-PHEN-001"]))
        self.assertEqual(rej, [])
        self.assertEqual(ok[0]["CONTEXTOS_CITADOS"], ["FENOLOGIA"])

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
