"""fast_casos: o programa so persiste/confere ids; o agrupamento e do Opus (sem matching lexical)."""
import ast
import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("FAST_AUTO_DIR", tempfile.mkdtemp())
from motor import fast_casos as K  # noqa: E402


def objs():
    return {"R1#C01": {"OBJ": "R1#C01", "RODADA": "R1", "CLASSE": "GAP", "TITULO": "a", "FATOS": []},
            "R2#C01": {"OBJ": "R2#C01", "RODADA": "R2", "CLASSE": "SINAL", "TITULO": "b", "FATOS": []},
            "R3#C02": {"OBJ": "R3#C02", "RODADA": "R3", "CLASSE": "SINAL", "TITULO": "c", "FATOS": []}}


class Agrupar(unittest.TestCase):
    def reg(self):
        return {"VERSAO": K.VERSAO, "PROXIMO": 1, "CASOS": {}}

    def test_cria_um_caso_para_varios_objetos(self):
        reg = self.reg()
        r = K.aplicar_agrupamento({"GRUPOS": [{"CASE_ID_EXISTENTE": None, "TITULO": "x",
                                               "OBJETOS": ["R1#C01", "R2#C01"], "CULTURAS_NA_FORMA_DAS_BULAS": ["MAIS"]},
                                              {"CASE_ID_EXISTENTE": None, "TITULO": "y", "OBJETOS": ["R3#C02"]}]},
                                  objs(), reg, voc=("MAIS",))
        self.assertEqual(r["CRIADOS"], ["CASE-001", "CASE-002"])
        self.assertEqual(reg["CASOS"]["CASE-001"]["OBJETOS"], ["R1#C01", "R2#C01"])
        self.assertEqual(reg["CASOS"]["CASE-001"]["CULTURAS_NA_FORMA_DAS_BULAS"], ["MAIS"])

    def test_reusa_case_id_existente(self):
        reg = self.reg()
        K.aplicar_agrupamento({"GRUPOS": [{"TITULO": "x", "OBJETOS": ["R1#C01"]}]}, objs(), reg)
        r = K.aplicar_agrupamento({"GRUPOS": [{"CASE_ID_EXISTENTE": "CASE-001", "OBJETOS": ["R1#C01", "R2#C01"]}]},
                                  objs(), reg)
        self.assertEqual(r["REUSADOS"], ["CASE-001"])
        self.assertEqual(r["CRIADOS"], [])
        self.assertEqual(reg["CASOS"]["CASE-001"]["OBJETOS"], ["R1#C01", "R2#C01"])

    def test_recusa_referencia_quebrada(self):
        reg = self.reg()
        r = K.aplicar_agrupamento({"GRUPOS": [{"CASE_ID_EXISTENTE": "CASE-099", "OBJETOS": ["R1#C01"]},
                                              {"TITULO": "z", "OBJETOS": ["R9#C09"]}]}, objs(), reg)
        motivos = sorted(x["MOTIVO"] for x in r["RECUSAS"])
        self.assertEqual(motivos, ["CASE_ID_INEXISTENTE", "OBJETO_INEXISTENTE"])
        self.assertEqual(reg["CASOS"], {})
        self.assertEqual(sorted(r["SEM_DECISAO"]), ["R1#C01", "R2#C01", "R3#C02"])

    def test_objeto_em_dois_grupos(self):
        reg = self.reg()
        r = K.aplicar_agrupamento({"GRUPOS": [{"TITULO": "a", "OBJETOS": ["R1#C01"]},
                                              {"TITULO": "b", "OBJETOS": ["R1#C01", "R2#C01"]}]}, objs(), reg)
        self.assertIn("OBJETO_EM_DOIS_GRUPOS", [x["MOTIVO"] for x in r["RECUSAS"]])
        K.conferir_registro(reg)

    def test_cultura_fora_do_vocabulario_recusada(self):
        reg = self.reg()
        r = K.aplicar_agrupamento({"GRUPOS": [{"TITULO": "a", "OBJETOS": ["R1#C01"],
                                               "CULTURAS_NA_FORMA_DAS_BULAS": ["GRANTURCO"]}]}, objs(), reg, voc=("MAIS",))
        self.assertEqual(reg["CASOS"]["CASE-001"]["CULTURAS_NA_FORMA_DAS_BULAS"], [])
        self.assertIn("CULTURA_FORA_DO_VOCABULARIO_DAS_BULAS", [x["MOTIVO"] for x in r["RECUSAS"]])

    def test_integridade_objeto_em_dois_casos(self):
        reg = {"CASOS": {"CASE-001": {"CASE_ID": "CASE-001", "OBJETOS": ["A"]},
                         "CASE-002": {"CASE_ID": "CASE-002", "OBJETOS": ["A"]}}}
        with self.assertRaises(AssertionError):
            K.conferir_registro(reg)

    def test_sem_matching_lexical_no_programa(self):
        """O agrupamento e do Opus: o modulo nao importa difflib/rapidfuzz nem calcula similaridade."""
        src = Path(K.__file__).read_text(encoding="utf-8")
        tree = ast.parse(src)
        nomes = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
        mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertFalse({"difflib", "rapidfuzz", "jellyfish", "sklearn"} & (nomes | mods))
        self.assertNotRegex(src, r"(?i)jaccard|levensh|similarit|cosine")


class Dossie(unittest.TestCase):
    def base(self):
        docs = {"RAW-1": {"DOCUMENT_ID": "RAW-1", "SOURCE_ID": "S1", "URL": "https://a.it/x", "DOMINIO": "a.it",
                          "RAW_ASSET_ID": 1, "RAW_SHA256": "h", "CAPTURED_AT": "2026-09-30T10:00", "DATA_PUBLICACAO": "NAO_SEI",
                          "NATUREZA": "EDITORIAL", "RODADA": "R1", "ORIGEM": K.ORIGEM_ACASO, "EVIDENCE_REQUEST_ID": None},
                "RAW-2": {"DOCUMENT_ID": "RAW-2", "SOURCE_ID": "S2", "URL": "https://b.it/y", "DOMINIO": "b.it",
                          "RAW_ASSET_ID": 2, "RAW_SHA256": "h2", "CAPTURED_AT": "2026-09-28T10:00", "DATA_PUBLICACAO": "2026-09-01",
                          "NATUREZA": "EDITORIAL", "RODADA": "R2", "ORIGEM": K.ORIGEM_ACASO, "EVIDENCE_REQUEST_ID": None}}
        fatos = {"F1": {"FACT_ID": "F1", "DOCUMENT_ID": "RAW-1"}, "F2": {"FACT_ID": "F2", "DOCUMENT_ID": "RAW-2"}}
        label = {"MAIS": {"ESTADO": "A_CONFIRMAR", "USOS": ["U1|P|MAIS|PIRALIDE|AUT"], "N_BULAS_ATIVAS_NAO_LIDAS": 61}}
        fen, ctx = {"IDS": {"IT-WIN-1", "IT-PHEN-1"}}, {"IDS": {"CTX-CLI-001": "CLI"}}
        caso = {"CASE_ID": "CASE-001", "OBJETOS": [], "INCORPORADOS": []}
        return caso, docs, fatos, label, fen, ctx

    def saida(self, **kw):
        s = {"TIMELINE": [{"DOCUMENT_ID": "RAW-1", "FACT_IDs": ["F1"], "TIPO_FONTE": "ASSOCIACAO"},
                          {"DOCUMENT_ID": "RAW-2", "FACT_IDs": ["F2"], "TIPO_FONTE": "IMPRENSA_AGRICOLA"}],
             "ELOS": {"PROBLEMA": {"ESTADO": "ENCONTRADO", "VALOR": "aflatossine", "FACT_IDs": ["F1"]},
                      "JANELA": {"ESTADO": "ENCONTRADO", "VALOR": "raccolta finita"},
                      "PRODUTO_ADAMA": {"ESTADO": "NAO_SEI", "VALOR": "nessuno"}},
             "EVIDENCE_REQUESTS": [{"ELO_DO_PEDIDO": t, "PERGUNTA_IT": "?", "ELOS_QUE_DESTRAVA": ["JANELA"]}
                                   for t in K.ER_MINIMOS],
             "CLASSIFICACAO": "GAP"}
        s.update(kw)
        return s

    def test_timeline_ordenada_e_datas_por_script(self):
        caso, docs, fatos, label, fen, ctx = self.base()
        out, _ = K.conferir_dossie(self.saida(), caso, docs, fatos, label, fen, ctx, {})
        self.assertEqual([e["document_id"] for e in out["timeline"]], ["RAW-2", "RAW-1"])
        self.assertEqual(out["timeline"][1]["tipo_data"], "CAPTURA")
        self.assertEqual(out["timeline"][0]["url"], "https://b.it/y")

    def test_janela_sem_crop_window_fica_nao_sei(self):
        caso, docs, fatos, label, fen, ctx = self.base()
        out, _ = K.conferir_dossie(self.saida(), caso, docs, fatos, label, fen, ctx, {})
        jan = [e for e in out["elos_faltantes"] if e["elo"] == "JANELA"][0]
        self.assertEqual(jan["estado"], "NAO_SEI")
        self.assertIn("SEM_CROP_WINDOW", jan["recusa_do_programa"])

    def test_produto_com_bulas_nao_lidas_e_a_confirmar_e_gap_nao_passa(self):
        caso, docs, fatos, label, fen, ctx = self.base()
        out, _ = K.conferir_dossie(self.saida(), caso, docs, fatos, label, fen, ctx, {})
        prod = [e for e in out["elos_faltantes"] if e["elo"] == "PRODUTO_ADAMA"][0]
        self.assertEqual(prod["estado"], "A_CONFIRMAR")
        self.assertNotEqual(out["classificacao"], "GAP")
        self.assertEqual(out["classificacao_do_modelo"], "GAP")

    def test_contraprova_gap_passa_sem_bulas_nao_lidas(self):
        caso, docs, fatos, label, fen, ctx = self.base()
        label["MAIS"]["N_BULAS_ATIVAS_NAO_LIDAS"] = 0
        out, _ = K.conferir_dossie(self.saida(), caso, docs, fatos, label, fen, ctx, {})
        self.assertEqual(out["classificacao"], "GAP")

    def test_pedido_que_nomeia_site_e_recusado(self):
        caso, docs, fatos, label, fen, ctx = self.base()
        s = self.saida()
        s["EVIDENCE_REQUESTS"][0]["PERGUNTA_IT"] = "cercare su www.ismea.it"
        out, rec = K.conferir_dossie(s, caso, docs, fatos, label, fen, ctx, {})
        self.assertIn("PEDIDO_NOMEIA_SITE_URL_OU_COLETOR", [r["MOTIVO"] for r in rec])
        self.assertEqual(out["conferencia"]["ER_MINIMOS_EM_FALTA"], ["FONTE_OFICIAL"])

    def test_timeline_recusa_documento_fora_do_caso(self):
        caso, docs, fatos, label, fen, ctx = self.base()
        s = self.saida()
        s["TIMELINE"].append({"DOCUMENT_ID": "RAW-9", "FACT_IDs": ["F9"]})
        out, rec = K.conferir_dossie(s, caso, docs, fatos, label, fen, ctx, {})
        self.assertIn("DOCUMENT_ID_FORA_DO_CASO", [r["MOTIVO"] for r in rec])
        self.assertEqual(len(out["timeline"]), 2)

    def test_oportunidade_com_elo_faltante_rebaixa(self):
        caso, docs, fatos, label, fen, ctx = self.base()
        out, _ = K.conferir_dossie(self.saida(CLASSIFICACAO="OPORTUNIDADE"), caso, docs, fatos, label, fen, ctx, {})
        self.assertNotEqual(out["classificacao"], "OPORTUNIDADE")


class Cases(unittest.TestCase):
    """CASES[] no CRUZAMENTO-COMERCIAL.json (ordem do dono 02/10): so projecao + integridade."""
    def caso(self, origem=K.ORIGEM_ACASO, er=None, prod="A_CONFIRMAR", classe="SINAL"):
        return {"case_id": "CASE-001", "titolo_it": "t", "classificacao": classe, "acao_atual_it": "a",
                "atualizado_em": "x", "CODIGO_HEAD": "h",
                "timeline": [{"data": "2026-09-01", "document_id": "RAW-1", "source_id": "S1", "url": "u",
                              "origem": origem, "evidence_request_id": er, "fact_ids": ["F1"]}],
                "elos_encontrados": [{"elo": "PROBLEMA", "valor": "v", "fact_ids": ["F1"], "document_ids": ["RAW-1"]}],
                "elos_faltantes": [{"elo": "PRODUTO_ADAMA", "estado": prod, "por_que": "p",
                                    "evidence_request_id": "ER-CASE-001-ADAMA_LABEL"},
                                   {"elo": "JANELA", "estado": "NAO_SEI", "por_que": "p", "evidence_request_id": None}],
                "evidence_requests": [{"id": "ER-CASE-001-ADAMA_LABEL", "pergunta_pt": "?", "elos_que_destrava": ["LABEL"],
                                       "tipos_de_fonte": ["ORGAO_OFICIAL"], "estado": "ABERTO"}]}

    def test_chaves_do_dono_e_destino_pela_classe(self):
        c = K.caso_para_cases(self.caso(), {"OBJETOS": ["R1#C01"]})
        for k in ("CASE_ID", "TITULO_IT", "CLASSIFICACAO", "ACAO_ATUAL_IT", "ATUALIZADO_EM", "TIMELINE",
                  "ELOS_ENCONTRADOS", "ELOS_FALTANTES", "EVIDENCE_REQUESTS"):
            self.assertIn(k, c)
        for k in ("DATA", "TITULO_CURTO_IT", "O_QUE_ACRESCENTOU_IT", "TIPO_FONTE", "URL", "SOURCE_ID", "DOCUMENT_ID",
                  "ORIGEM", "EVIDENCE_REQUEST_ID"):
            self.assertIn(k, c["TIMELINE"][0])
        for k in ("EVIDENCE_REQUEST_ID", "CASE_ID", "PERGUNTA", "ELO_ALVO", "TIPO_DE_FONTE_DESEJADA", "STATUS"):
            self.assertIn(k, c["EVIDENCE_REQUESTS"][0])
        self.assertEqual(c["DESTINO_FERRAMENTA"], "FUTURE_RADAR")
        self.assertEqual(c["OBJETOS_ABSORVIDOS"], ["R1#C01"])

    def test_produto_adama_fica_nao_sei_nunca_gap(self):
        c = K.caso_para_cases(self.caso(prod="A_CONFIRMAR"), {"OBJETOS": []})
        p = [f for f in c["ELOS_FALTANTES"] if f["ELO"] == "PRODUTO_ADAMA"][0]
        self.assertEqual((p["ESTADO"], p["ESTADO_DETALHE"]), ("NAO_SEI", "A_CONFIRMAR"))

    def test_busca_ativa_sem_pedido_recusada(self):
        with self.assertRaises(AssertionError):
            K.caso_para_cases(self.caso(origem=K.ORIGEM_BUSCA, er=None), {"OBJETOS": []})
        with self.assertRaises(AssertionError):
            K.caso_para_cases(self.caso(origem=K.ORIGEM_BUSCA, er="ER-CASE-009-X"), {"OBJETOS": []})

    def test_contraprova_busca_ativa_com_pedido_do_caso_passa(self):
        c = K.caso_para_cases(self.caso(origem=K.ORIGEM_BUSCA, er="ER-CASE-001-ADAMA_LABEL"), {"OBJETOS": []})
        self.assertEqual(c["CONTAGEM"]["BUSCA_ATIVA"], 1)

    def test_nao_sei_convertido_em_gap_recusado(self):
        c = K.caso_para_cases(self.caso(), {"OBJETOS": []})
        c["ELOS_FALTANTES"][1]["ESTADO"] = "GAP"
        with self.assertRaises(AssertionError):
            K.conferir_case(c)

    def test_destino_diferente_da_classe_recusado(self):
        c = K.caso_para_cases(self.caso(), {"OBJETOS": []})
        c["DESTINO_FERRAMENTA"] = "OPPORTUNITY_RADAR"
        with self.assertRaises(AssertionError):
            K.conferir_case(c)

    def test_busca_ativa_explicita(self):
        self.assertEqual(K.caso_para_cases(self.caso(), {"OBJETOS": []})["BUSCA_ATIVA"], "NAO")
        c = K.caso_para_cases(self.caso(origem=K.ORIGEM_BUSCA, er="ER-CASE-001-ADAMA_LABEL"), {"OBJETOS": []})
        self.assertEqual(c["BUSCA_ATIVA"], "SIM")

    def test_fonte_concorrente_sai_da_prova_do_elo_fica_na_timeline(self):
        x = self.caso()
        x["timeline"].append({"data": "2026-09-02", "document_id": "RAW-2", "tipo_fonte": "CONCORRENCIA",
                              "origem": K.ORIGEM_ACASO, "fact_ids": ["F-RAW-2-01"]})
        x["elos_encontrados"][0]["document_ids"] = ["RAW-1", "RAW-2"]
        x["elos_encontrados"][0]["fact_ids"] = ["F1", "F-RAW-2-01"]
        c = K.caso_para_cases(x, {"OBJETOS": []})
        p = c["ELOS_ENCONTRADOS"][0]
        self.assertEqual((p["DOCUMENT_IDS"], p["DOCUMENTOS_FORA_POR_REGRA"], p["FACT_IDS"]), (["RAW-1"], ["RAW-2"], ["F1"]))
        papel = {t["DOCUMENT_ID"]: t["PAPEL"] for t in c["TIMELINE"]}
        self.assertEqual(papel, {"RAW-1": "PROVA", "RAW-2": "FONTE_PROMOCIONAL"})

    def test_elo_so_com_fonte_concorrente_vira_nao_sei(self):
        x = self.caso()
        x["timeline"][0]["tipo_fonte"] = "CONCORRENCIA"
        c = K.caso_para_cases(x, {"OBJETOS": []})
        self.assertEqual(c["ELOS_ENCONTRADOS"], [])
        self.assertIn(("PROBLEMA", "NAO_SEI"), [(f["ELO"], f["ESTADO"]) for f in c["ELOS_FALTANTES"]])


if __name__ == "__main__":
    unittest.main()
