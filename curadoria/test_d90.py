# -*- coding: utf-8 -*-
"""D90 — pacote TABLE_EXTRACTION das series e o ensaio da escrita pelo dono do derivado, num banco descartavel (SQLite
da casa). Sem rede."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI.parent), str(AQUI)]
import d90_payload_series as P      # noqa: E402
import d90_preservar_pacotes as W   # noqa: E402
from guarda.memoria_descartavel import MemoriaDescartavel   # noqa: E402
from guarda.preservar_coleta import ArmazemLocal            # noqa: E402

SHA_PAI = "ab" * 32
DOC_APOL = {"SHA256": SHA_PAI, "SOURCE_ID": "IT-T3-010", "FORMA": "APOL", "LINHAS": [
    {"LOCAL": "COMPRENSORIO BR - COLLINA LITORANEA", "ORGANISMO": "mosca", "FASE": "INGROSSAMENTO FRUTTI",
     "COLUNA_1": 7, "COLUNA_2": 1, "COLUNA_3": "5%", "TENDENCIA": "STAZIONARIO", "RISCO": "BASSO",
     "PERIODO": ["07/09/2026", "13/09/2026"], "DATA": "2026-09-07", "NATUREZA": ["OBSERVACAO"], "TRECHO": "x"}]}


class Pacote(unittest.TestCase):
    def test_valor_como_veio_e_numero_so_quando_e_numero(self):
        ls = P.linhas(DOC_APOL)
        c3 = [l for l in ls if l["METRICA_ESPERADA_PELO_CONTRATO"] == "ACTIVE_INFESTATION_PERCENT"][0]
        self.assertEqual(("5%", 5), (c3["VALOR_TAL_COMO_VEIO"], c3["VALOR_NUMERICO"]))
        rot = [l for l in ls if l["METRICA_ESPERADA_PELO_CONTRATO"] == "TREND_LABEL"][0]
        self.assertIsNone(rot["VALOR_NUMERICO"])

    def test_metrica_medida_fica_nao_sei_quando_o_cabecalho_e_imagem(self):
        for l in P.linhas(DOC_APOL):
            if l["METRICA_ESPERADA_PELO_CONTRATO"] in ("TRAP_CAPTURES", "ACTIVE_INFESTATION_PERCENT"):
                self.assertTrue(l["METRICA_MEDIDA"].startswith("NAO SEI"))

    def test_natureza_separada_e_mista_nao_se_parte(self):
        doc = {"SHA256": SHA_PAI, "SOURCE_ID": "IT-T2-002", "FORMA": "ARPAV", "LINHAS": [
            {"ORGANISMO": "Spilocaea", "NATUREZA": ["OBSERVACAO", "PREVISAO"], "FRASE": "possono favorire"},
            {"ORGANISMO": "Bactrocera", "NATUREZA": ["OBSERVACAO"], "FRASE": "pressione stabile"}]}
        ls = P.linhas(doc)
        self.assertEqual(["MISTA", "OBSERVACAO"], [l["NATUREZA_UNICA"] for l in ls])

    def test_arif_observacao_e_recomendacao_em_linhas_distintas(self):
        doc = {"SHA256": SHA_PAI, "SOURCE_ID": "IT-T3-008", "FORMA": "ARIF", "LINHAS": [
            {"BLOCO": 3, "BOLETIM_N": "37", "DATA": "2026-09-09", "FASE": "Invaiatura.", "ORIGEM": "rotulos",
             "OBSERVACAO": "Catture di tignoletta nelle trappole.", "RECOMENDACAO": "Intervenire al superamento della soglia.",
             "LIMIARES": ["Intervenire al superamento della soglia."]}]}
        nat = [l["NATUREZA_UNICA"] for l in P.linhas(doc)]
        self.assertEqual(["OBSERVACAO", "RECOMENDACAO", "RECOMENDACAO"], nat)

    def test_linha_id_estavel(self):
        self.assertEqual([l["LINHA_ID"] for l in P.linhas(DOC_APOL)], [l["LINHA_ID"] for l in P.linhas(DOC_APOL)])

    def test_estado_na_estrada(self):
        raw = [{"ID": 1, "SHA256": SHA_PAI, "DOCUMENT_KEY": "APOL:2026:N9:BR", "DERIVADOS": [{"KIND": "TEXT_EXTRACTION"}]}]
        self.assertEqual(1, P.estado_na_estrada(SHA_PAI, raw)["RAW_ID_PAI_PROPOSTO"])
        self.assertIn("AUSENTE", P.estado_na_estrada("cd" * 32, raw)["RAW"])


class EnsaioDaEscrita(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="d90-")))
        self.pac = self.tmp / "pacotes"
        self.pac.mkdir()
        b = json.dumps({"LINHAS": P.linhas(DOC_APOL)}, sort_keys=True).encode("utf-8")
        (self.pac / "p.json").write_bytes(b)
        (self.pac / "MANIFESTO.json").write_text(json.dumps({"DOCUMENTOS": [
            {"RAW": "PRESENTE", "RAW_ID_PAI_PROPOSTO": 1, "PACOTE": "p.json", "PACOTE_SHA256": hashlib.sha256(b).hexdigest(),
             "SOURCE_ID": "IT-T3-010", "FORMA": "APOL", "LINHAS": 4},
            {"RAW": "PRESENTE", "RAW_ID_PAI_PROPOSTO": 1, "PACOTE": "vazio.json", "SOURCE_ID": "IT-T2-002",
             "FORMA": "ARPAV", "LINHAS": 0},
            {"RAW": "AUSENTE da Sala", "PACOTE": "q.json", "SOURCE_ID": "IT-T3-010", "FORMA": "APOL", "LINHAS": 4}]}),
            encoding="utf-8")
        self.m = MemoriaDescartavel()
        self.m.aplicar("insert into public.collection_run (run_id, platform, actor, source_country, started_at, "
                       "status, rule_version) values ('R1', 'web', 'ensaio/d90', 'IT', '2026-09-26T00:00:00Z', 'concluida', "
                       "'ensaio-v1');")
        self.m.aplicar("insert into public.raw_asset (run_id, storage_path, media_type, bytes, sha256, captured_at, "
                       "preserved, not_preserved_reason, identity_state) values ('R1', 'IT/x/1.pdf', 'application/pdf', 1, "
                       "'%s', '2026-09-26T00:00:00Z', 0, 'ensaio', 'LEGACY_PRE_IDEMPOTENCY');" % SHA_PAI)
        self.arm = ArmazemLocal(self.tmp / "armazem")

    def test_so_raw_presente_e_escrito_e_segunda_vez_reusa(self):
        r1 = W.correr(self.pac, self.arm, self.m, aplicar=True)
        self.assertEqual(1, len(r1))
        self.assertEqual(1, self.m.contar("derived_artifact"))
        r2 = W.correr(self.pac, self.arm, self.m, aplicar=True)
        self.assertEqual(1, self.m.contar("derived_artifact"), "a mesma receita nao escreve duas vezes")
        self.assertNotEqual(r1[0]["ESTADO"], None)
        self.assertIn("REUSED", str(r2[0]["ESTADO"]))

    def test_a_seco_nao_escreve(self):
        W.correr(self.pac, self.arm, self.m, aplicar=False)
        self.assertEqual(0, self.m.contar("derived_artifact"))

    def test_recusa_a_sala_real(self):
        self.assertTrue(W.e_a_sala_real("postgresql://u:p@127.0.0.1:54330/postgres"))
        self.assertFalse(W.e_a_sala_real("postgresql://u:p@127.0.0.1:55432/descartavel"))


if __name__ == "__main__":
    unittest.main()
