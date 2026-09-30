#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F2 (REAUDIT-275, 30/09) — o CONHECIMENTO/ESTUDO sem FACT_TIME chega ao pote, sem alerta e sem tempo inventado.

    MEDIDO antes (copia RO da Sala, 309 linhas): os 100 artigos EU-T5-001 entravam com FATO = NAO_SE_APLICA,
    G0 = BLOQUEADO_EM_G0 so por FACT_TIME, e a LEITURA_ATEMPORAL_DE_CAPACIDADE disponivel. Morriam em dois sitios:
      1. `e_estudo` so lia o FATO -> triados para a CAP-WIN (0 estudos julgados);
      2. `_admite` so aceitava G0 = PASSOU -> mesmo julgados, nenhum ia ao pote.

    A REGRA (dono: Intelligence owner; P7 do contrato pote v2, INT-LAW-252 usos sem tempo):
      * estudo = o FATO o declara OU a admissao declarou NATUREZA ESTUDO_CIENTIFICO (estudo-chaves), com o extrator;
      * o estudo cujo G0 bloqueou SO por nao haver FACT_TIME (G0_FALTA == ["FACT_TIME"]) e com a leitura atemporal
        disponivel vai a `science` como SINAL de CONHECIMENTO: RESULTADO NO_DEFENSIBLE_ACTION_YET, USO_EXIGE_TEMPO
        false, ADMITIDA_POR USO_SEM_TEMPO, FACT_TIME e STUDY_PERIOD = NAO SEI;
      * data sem ano, futura ou sem base NAO e «sem tempo»: e tempo que nao ancorou, e continua fora;
      * nunca em windows/archive/future (nunca alerta, janela ou incidencia).
Texto SINTETICO; nenhum item real.
"""
import copy
import hashlib
import json
import sys
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import motor_das_capacidades as M                # noqa: E402
import gatilho_da_inteligencia as GI             # noqa: E402

HOJE = date(2026, 9, 28)
EXPORT_R7 = RAIZ / "tests" / "dados" / "int-r7" / "SINTETICO-R7-SALA-EXPORT.json"
TEXTO = ("Downy mildew control in grapevine: a synthetic abstract. Field trials on grapevine showed "
         "that the treatment reduced symptoms.")


def _janela_de_estudo(texto, natureza="ESTUDO_CIENTIFICO", extrator="estudo-chaves-v1"):
    i = texto.index("grapevine")
    return {
        "CULTURA": {"VALOR": ["vite"], "ENTITY_SOURCE": "SPAN", "NATUREZA": "ESTUDO_CIENTIFICO",
                    "BASE": "«grapevine»", "VEIO_DE": "item.texto (titulo + resumo do estudo), estudo-chaves-v1",
                    "SPANS": [{"INICIO": i, "FIM": i + 9, "TRECHO": "grapevine", "VALOR": "vite"}]},
        "PROBLEMA": {"VALOR": ["peronospora"], "ENTITY_SOURCE": "SPAN", "ESTADO": "NOMEADO_NO_ESTUDO",
                     "NATUREZA": "ESTUDO_CIENTIFICO"},
        "REGIAO_DO_FATO": {"VALOR": "NAO SEI", "BASE": "NAO SEI", "ENTITY_SOURCE": "NAO SEI"},
        "FASE": {"VALOR": "NAO SEI", "BASE": "NAO SEI", "VEIO_DE": "NAO SEI"},
        "JANELA": {"VALOR": "NAO SEI", "BASE": "NAO SEI", "VEIO_DE": "NAO SEI", "PRECISAO": "NAO SEI"},
        "ORIGEM": {"CAP_SCI": {"NATUREZA": natureza, "E_INCIDENCIA_DE_CAMPO": "NAO"},
                   "EXTRATOR_DO_ESTUDO": extrator, "UNIVERSO": "T5"},
    }


class _Base(unittest.TestCase):
    def setUp(self):
        self.exp = json.loads(EXPORT_R7.read_text(encoding="utf-8"))
        for x in self.exp["LINHAS"]:
            x["raw_sha256"] = hashlib.sha256(("raw-%s" % x["raw_observation_id"]).encode()).hexdigest()
        self.l = self.exp["LINHAS"][0]
        self.l.update(texto=TEXTO, fact_time="NAO SEI", fact_time_basis="TEXTO: NAO SEI · nenhuma data",
                      fact_location="NAO SEI", fact_location_basis="NAO SEI", fato="NAO_SE_APLICA",
                      janela_declarada=_janela_de_estudo(TEXTO), universo="T5", published_at="2022-02-08")

    def correr(self):
        return M.rodar(M.entrada_do_export(self.exp), HOJE, "TESTE")

    def objetos_do_item(self, s, comp):
        return [o for o in s["ITENS_POR_FERRAMENTA"].get(comp, [])
                if any(str(p["ITEM_ID"]) == str(self.l["item_id"]) for p in o["PROVA"])]

    def linha(self, s):
        return next(e for e in s["LINEAGE"] if "CLAIM_ID" not in e and str(e["ITEM_ID"]) == str(self.l["item_id"]))


class F2_OConhecimentoChegaAoPote(_Base):
    def test_o_estudo_sem_tempo_e_triado_para_a_cap_sci(self):
        s = self.correr()
        self.assertEqual(s["TRIAGEM"][str(self.l["item_id"])]["CAPACIDADE"], "CAP-SCI")
        self.assertEqual(self.linha(s)["G0"], "BLOQUEADO_EM_G0")
        self.assertEqual(self.linha(s)["G0_FALTA"], ["FACT_TIME"])

    def test_vai_a_science_como_conhecimento_sem_alerta_e_sem_tempo(self):
        s = self.correr()
        objs = self.objetos_do_item(s, "science")
        self.assertEqual(len(objs), 1)
        o = objs[0]
        self.assertEqual(o["ESPECIE"], "SINAL")
        self.assertEqual(o["RESULTADO"], "NO_DEFENSIBLE_ACTION_YET")
        self.assertEqual(o["CHAVES"]["ESPECIE_DO_MOTOR"], M.ESPECIE_CONHECIMENTO)
        self.assertEqual(o["CHAVES"]["STUDY_PERIOD"], "NAO SEI")
        self.assertEqual(o["PROVA"][0]["FACT_TIME"], "NAO SEI")
        self.assertEqual(o["CHAVES"]["CROP_ID"], "vite")                   # o SPAN da admissao, conferido
        self.assertEqual(o["CHAVES"]["ISSUE_ID"], "NAO SEI")               # fora do PROBLEMA/v1: nao promove
        for comp in ("windows", "archive", "future"):
            self.assertEqual(self.objetos_do_item(s, comp), [], comp)

    def test_o_pote_o_admite_por_uso_sem_tempo_e_o_fiscal_passa(self):
        s = self.correr()
        pote, _ = GI.montar_o_pote(s)
        self.assertEqual(GI.VP.validar(pote), [])
        o = [o for o in pote["COMPARTIMENTOS"]["science"]["OBJETOS"]
             if any(p["ITEM_ID"] == self.l["item_id"] for p in o["PROVA"])]
        self.assertEqual(len(o), 1)
        self.assertIs(o[0]["USO_EXIGE_TEMPO"], False)
        self.assertEqual(o[0]["PROVA"][0]["ADMITIDA_POR"], "USO_SEM_TEMPO")
        self.assertEqual(o[0]["PROVA"][0]["PUBLISHED_AT"], "2022-02-08")   # publicacao ao lado, nunca FACT_TIME
        self.assertEqual(o[0]["PROVA"][0]["FACT_TIME"], "NAO SEI")


class F2_OQueContinuaFora(_Base):
    def test_sem_a_natureza_declarada_nao_e_estudo(self):
        self.l["janela_declarada"] = _janela_de_estudo(TEXTO, natureza="NAO SEI")
        s = self.correr()
        self.assertEqual(s["TRIAGEM"][str(self.l["item_id"])]["CAPACIDADE"], "CAP-WIN")
        self.assertEqual(self.objetos_do_item(s, "science"), [])

    def test_natureza_sem_extrator_nao_conta(self):
        self.l["janela_declarada"] = _janela_de_estudo(TEXTO, extrator="NAO SEI")
        self.assertEqual(self.correr()["TRIAGEM"][str(self.l["item_id"])]["CAPACIDADE"], "CAP-WIN")

    def test_data_sem_ano_nao_e_conhecimento_atemporal(self):
        self.l.update(fact_time="11 settembre", fact_time_basis="TEXTO: «11 settembre»")
        s = self.correr()
        self.assertEqual(self.linha(s)["G0_FALTA"], ["FACT_TIME:SEM_ANO"])
        self.assertEqual(self.objetos_do_item(s, "science"), [])

    def test_sem_a_leitura_atemporal_disponivel_nao_admite(self):
        l = {"G0": "BLOQUEADO_EM_G0", "G0_FALTA": ["FACT_TIME"], "FACT_TIME": "NAO SEI", "USOS_DISPONIVEIS": []}
        self.assertFalse(M._admite(l, M.SINAL, sem_tempo=True))
        l["USOS_DISPONIVEIS"] = ["LEITURA_ATEMPORAL_DE_CAPACIDADE"]
        self.assertTrue(M._admite(l, M.SINAL, sem_tempo=True))
        self.assertFalse(M._admite(l, M.SINAL))                            # sem o uso sem tempo, nada muda

    def test_bloqueio_por_proveniencia_nunca_e_admitido(self):
        l = {"G0": "BLOQUEADO_EM_G0", "G0_FALTA": ["FACT_TIME", "SOURCE_ID"], "FACT_TIME": "NAO SEI",
             "USOS_DISPONIVEIS": ["LEITURA_ATEMPORAL_DE_CAPACIDADE"]}
        self.assertFalse(M._admite(l, M.SINAL, sem_tempo=True))

    def test_span_da_cultura_que_nao_bate_com_o_texto_da_nao_sei(self):
        j = _janela_de_estudo(TEXTO)
        j["CULTURA"]["SPANS"][0]["INICIO"] += 1
        self.l["janela_declarada"] = j
        o = self.objetos_do_item(self.correr(), "science")[0]
        self.assertEqual(o["CHAVES"]["CROP_ID"], "NAO SEI")


class F2_OPortaoDaSaidaMorde(_Base):
    def _saida(self):
        return self.correr()

    def test_conhecimento_com_tempo_escrito_e_reprovado(self):
        s = copy.deepcopy(self._saida())
        o = self.objetos_do_item(s, "science")[0]
        o["CHAVES"]["STUDY_PERIOD"] = "2022-02-08"
        o["CHAVES"]["ENTITY_SOURCE"]["STUDY_PERIOD"]["VALOR"] = "2022-02-08"
        o["CHAVES"]["ENTITY_SOURCE"]["STUDY_PERIOD"]["ENTITY_SOURCE"] = "READY.PUBLISHED_AT"
        self.assertTrue(any("tempo escrito" in v for v in M.conferir_saida(s)))

    def test_conhecimento_numa_janela_e_reprovado(self):
        s = copy.deepcopy(self._saida())
        o = self.objetos_do_item(s, "science")[0]
        s["ITENS_POR_FERRAMENTA"]["windows"].append(o)
        self.assertTrue(any(v.startswith("windows/") and "conhecimento sem tempo fora de science" in v
                            for v in M.conferir_saida(s)))

    def test_sem_resultado_honesto_a_prova_sem_tempo_nao_e_admitida(self):
        s = copy.deepcopy(self._saida())
        o = self.objetos_do_item(s, "science")[0]
        o.pop("RESULTADO")
        self.assertTrue(any("nao admitida em G0" in v for v in M.conferir_saida(s)))


if __name__ == "__main__":
    unittest.main()
