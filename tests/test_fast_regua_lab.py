# -*- coding: utf-8 -*-
"""Correcoes do LAB a remessa-001 (AUDITORIA-LAB-CRUZAMENTO.md sec. 1), dentro da T14, sem gate novo.

O programa (nao o modelo) aplica a leitura da D162 depois da conferencia de ids:
 R1 · GAP so com O_QUE + CULTURA + ONDE + NECESSIDADE + JANELA fechados; senao a classe e SINAL e a hipotese fica
      escrita como GAP_A_CONFIRMAR com o que falta (C04 pimentao; C01 avela com JANELA NAO_SEI).
 R2 · POR_QUE_AGORA com valor so com prova: nenhuma inferencia da IA no campo e pelo menos um facto citado com o ano
      corrente escrito no seu «quando». Senao NAO_SEI, com o texto do modelo preservado (C03 Casalasco 2025; C06 limao).
 R3 · a referencia lida diz o universo certo: N linhas de uso lidas != N combinacoes mostradas, e a cultura de cada
      linha e a do campo CROP_ON_LABEL (a frase da bula pode nomear outras) — nao se afirma ausencia no texto das bulas.
"""
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from motor import fast_cruzamento_comercial as FC  # noqa: E402

HOJE = date(2026, 10, 2)
FATOS = {
    "d:1#F1": {"FACT_ID": "d:1#F1", "DOCUMENT_ID": "d:1", "SOURCE_ID": "S-A", "URL": "https://a.it/x",
               "quando": "24 de setembro de 2026", "evidencias": {"fato": "t1"}},
    "d:1#F2": {"FACT_ID": "d:1#F2", "DOCUMENT_ID": "d:1", "SOURCE_ID": "S-A", "URL": "https://a.it/x",
               "quando": "10 de dezembro (2025)", "evidencias": {"fato": "t2"}},
    "d:1#F3": {"FACT_ID": "d:1#F3", "DOCUMENT_ID": "d:1", "SOURCE_ID": "S-A", "URL": "https://a.it/x",
               "quando": "NAO_SEI", "evidencias": {"fato": "t3"}},
}
REF = {"USE_IDS": set(), "FRESCOR": "FRESCA", "CARIMBO": {}}
FEN = {"IDS": set()}
NS = "NAO_SEI — dado não encontrado no conhecimento fornecido (onde procurei: x)"


def _campos(**over):
    c = {k: {"valor": "valor sustentado", "FACT_IDs": ["d:1#F1"], "INTERPRETACAO_DA_IA": None} for k in FC.CAMPOS}
    c["POR_QUE_AGORA"] = {"valor": NS, "FACT_IDs": [], "INTERPRETACAO_DA_IA": None}
    for k, v in over.items():
        c[k] = v
    return c


def conf(o):
    o = dict({"ID": "C01", "FACT_IDs": ["d:1#F1"], "SINAIS_CRUZADOS": []}, **o)
    ok, rej = FC.conferir({"objetos": [o]}, FATOS, [], REF, FEN, hoje=HOJE)
    assert not rej, rej
    return ok[0]


class R1_GapExigeNecessidadeFechada(unittest.TestCase):
    def test_gap_com_onde_e_janela_nao_sei_vira_sinal(self):          # C04 pimentao
        o = conf({"CLASSE": "GAP", "CAMPOS": _campos(LOCAL={"valor": NS}, JANELA={"valor": NS})})
        self.assertEqual(o["CLASSE"], "SINAL")
        self.assertEqual(o["CLASSE_DO_MODELO"], "GAP")
        self.assertEqual(o["HIPOTESE_DE_GAP"]["ESTADO"], "GAP_A_CONFIRMAR")
        self.assertEqual(o["HIPOTESE_DE_GAP"]["FALTA"], ["LOCAL", "JANELA"])

    def test_gap_so_sem_janela_tambem_nao_e_gap_firme(self):          # C01 avela
        o = conf({"CLASSE": "GAP", "CAMPOS": _campos(JANELA={"valor": NS})})
        self.assertEqual(o["CLASSE"], "SINAL")
        self.assertEqual(o["HIPOTESE_DE_GAP"]["FALTA"], ["JANELA"])

    def test_contraprova_gap_com_necessidade_fechada_fica_gap(self):
        o = conf({"CLASSE": "GAP", "CAMPOS": _campos()})
        self.assertEqual(o["CLASSE"], "GAP")
        self.assertNotIn("HIPOTESE_DE_GAP", o)
        self.assertNotIn("CLASSE_DO_MODELO", o)

    def test_regra_nao_toca_noutras_classes(self):
        o = conf({"CLASSE": "LEAD", "CAMPOS": _campos(JANELA={"valor": NS})})
        self.assertEqual(o["CLASSE"], "LEAD")


class R2_PorQueAgoraSoComProva(unittest.TestCase):
    def test_inferencia_da_ia_vira_nao_sei(self):                     # C06 limao
        agora = {"valor": "a campanha abre agora", "FACT_IDs": ["d:1#F1"], "INTERPRETACAO_DA_IA": "inferencia minha"}
        o = conf({"CLASSE": "LEAD", "CAMPOS": _campos(POR_QUE_AGORA=agora)})
        c = o["CAMPOS"]["POR_QUE_AGORA"]
        self.assertTrue(c["valor"].startswith("NAO_SEI"))
        self.assertEqual(c["VALOR_DO_MODELO"], "a campanha abre agora")

    def test_agora_assente_em_factos_de_2025_vira_nao_sei(self):      # C03 Casalasco
        agora = {"valor": "investe agora", "FACT_IDs": ["d:1#F2", "d:1#F3"], "INTERPRETACAO_DA_IA": None}
        o = conf({"CLASSE": "LEAD", "CAMPOS": _campos(POR_QUE_AGORA=agora)})
        self.assertTrue(o["CAMPOS"]["POR_QUE_AGORA"]["valor"].startswith("NAO_SEI"))
        self.assertIn("2026", o["CAMPOS"]["POR_QUE_AGORA"]["valor"])

    def test_contraprova_facto_do_ano_corrente_sem_inferencia_fica(self):
        agora = {"valor": "carta de 24/09/2026", "FACT_IDs": ["d:1#F1"], "INTERPRETACAO_DA_IA": None}
        o = conf({"CLASSE": "SINAL", "CAMPOS": _campos(POR_QUE_AGORA=agora)})
        self.assertEqual(o["CAMPOS"]["POR_QUE_AGORA"]["valor"], "carta de 24/09/2026")
        self.assertNotIn("VALOR_DO_MODELO", o["CAMPOS"]["POR_QUE_AGORA"])

    def test_nao_sei_do_modelo_fica_como_esta(self):
        o = conf({"CLASSE": "SINAL", "CAMPOS": _campos()})
        self.assertEqual(o["CAMPOS"]["POR_QUE_AGORA"]["valor"], NS)

    def test_oportunidade_sem_prova_do_agora_fica_medida(self):
        agora = {"valor": "agora", "FACT_IDs": ["d:1#F2"], "INTERPRETACAO_DA_IA": None}
        o = conf({"CLASSE": "OPORTUNIDADE", "CAMPOS": _campos(POR_QUE_AGORA=agora)})
        self.assertTrue(o["CONFERENCIA"]["OPORTUNIDADE_COM_NAO_SEI"])


class R3_ReferenciaDizOUniversoCerto(unittest.TestCase):
    def test_prompt_separa_linhas_lidas_de_combinacoes_e_avisa_do_campo(self):
        ref = {"CARIMBO": {}, "FRESCOR": "F", "USOS": ["u1"], "USE_IDS": {"u1"}, "N_USOS_LIDOS": 2030,
               "NAO_LIDAS": [], "PORTFOLIO": [], "CULTURAS_NAS_BULAS": ["MELO"]}
        p = FC.montar_prompt({}, [], [], ref, {"AVISO": "", "LINHAS": []})
        self.assertIn("2030 linhas de uso lidas", p)
        self.assertIn("1 combinacoes distintas", p)
        self.assertIn("CROP_ON_LABEL", p)
        self.assertIn("nao afirme que uma cultura nao aparece nas bulas", p.lower())

    def test_contexto_real_conta_as_linhas_lidas(self):
        ref = FC.contexto_referencia()
        self.assertGreaterEqual(ref["N_USOS_LIDOS"], len(ref["USOS"]))


if __name__ == "__main__":
    unittest.main()
