#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LIBERACAO POR CRITERIO — o formato da PROVA de um objeto liberado (LAB E5, 30/09/2026).

A prova reversa do LAB (v3.1, IR-3015b1a878172b3d2fee) reprovou o E5 nos 2 objetos liberados:
  1. o LUGAR viajava sem posicao — «Puglia» aparece 16 vezes no texto, e o nome sozinho nao prova QUAL;
  2. TRECHO_DA_DATA_LEGIVEL tinha prefixo de citacao e era interpretacao do sistema (cabecalho desdobrado).

Regras que estes testes fixam (dono: Intelligence owner):
  * todo campo TRECHO_* da prova e CITACAO LITERAL do texto da Sala, na posicao declarada em SECAO (*_EM);
  * lugar sem posicao provada pelo produtor NAO libera (C3 falha) — o juiz nao afrouxa;
  * a leitura do sistema chama-se DATA_LEGIVEL_INTERPRETADA, nunca TRECHO_*.
Texto SINTETICO; nenhum id, trecho ou data de corrida real.
"""
import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "pacote"))
sys.path.insert(0, str(RAIZ))
import liberacao_por_criterio as L  # noqa: E402

CAB = "RREEGGIIOONNEE SSIINNTTEETTIICCAA Dal 01-01-2031 al 07-01-2031"
FRASE = "Nella settimana piogge forti in Molise, sopra la media del Molise interno."
TEXTO = "Titolo Molise bollettino\n" + CAB + "\n" + FRASE + "\nFine."


def _pos(sub, depois=0):
    i = TEXTO.index(sub, depois)
    return i, i + len(sub)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raw = b"raw-sintetico-liberacao"
        (Path(self.tmp.name) / "raw.bin").write_bytes(raw)
        self.armazem = Path(self.tmp.name)
        self.linhas = {"SINT-1": {"texto": TEXTO, "raw_sha256": hashlib.sha256(raw).hexdigest(),
                                  "raw_storage_path": "raw.bin", "raw_document_key": "SINT-DOC"}}
        a, b = _pos(FRASE)
        d0, d1 = _pos(CAB)
        l0, l1 = _pos("Molise", a)                     # a ocorrencia DENTRO da afirmacao, nao a do titulo
        self.span = {"INICIO": a, "FIM": b, "TRECHO": FRASE}
        self.o = {
            "OBJETO_ID": "SINT-O-1", "ESPECIE": "SINAL", "ESPECIE_DITA_POR": "INTELLIGENCE",
            "CHAVES": {"FACT_LOCATION": "Molise"}, "LOCATION_SOURCE": "TEXT", "LIGACAO_ADAMA": {},
            "PROVA": [{"ITEM_ID": "SINT-1", "CLAIM_ID": "AF-SINT-1", "DOCUMENT_ID": "SINT-DOC", "G0": "PASSOU",
                       "RAW_SHA256": self.linhas["SINT-1"]["raw_sha256"], "RAW_STORAGE_PATH": "raw.bin"}],
            "FORA_DO_CONTRATO": {
                "LOCATION_SOURCE": "TEXT",
                "DA_FONTE": {"EVIDENCE_SPAN": self.span,
                             "FACT_TIME_BASIS": {"INICIO": d0, "FIM": d1, "TRECHO": CAB},
                             "FACT_LOCATION_TRECHO": "Molise",
                             "FACT_LOCATION_ONDE": {"INICIO": l0, "FIM": l1, "TRECHO": "Molise"}},
                "INTERPRETACAO_DO_SISTEMA": {"FACT_TIME_ORIGEM": "CABECALHO_D147"}}}
        # C4 (ligacao ADAMA) e C6 (tabela de compartimentos) nao sao o assunto aqui
        self._lig, self._leg = L.PORTA.conferir_ligacao, L._como_se_le
        L.PORTA.conferir_ligacao = lambda lig: []
        L._como_se_le = lambda s: s.replace("RREEGGIIOONNEE SSIINNTTEETTIICCAA", "REGIONE SINTETICA")

    def tearDown(self):
        L.PORTA.conferir_ligacao, L._como_se_le = self._lig, self._leg
        self.tmp.cleanup()

    def conferir(self, o):
        return L.conferir_objeto(o, "archive", self.linhas, self.armazem, set(), {})

    def liberar(self, o):
        pote = {"COMPARTIMENTOS": {"archive": {"OBJETOS": [o]}}}
        return L.liberar(pote, self.linhas, self.armazem, "IR-SINT")[0]["COMPARTIMENTOS"]["archive"]["OBJETOS"][0]


class C3_OLugarPrecisaDePosicao(Base):
    def test_lugar_com_posicao_dentro_da_afirmacao_passa(self):
        self.assertEqual(self.conferir(self.o)["C3_LUGAR_PROPRIO"], L.PASSOU)

    def test_lugar_sem_posicao_nao_libera(self):
        o = copy.deepcopy(self.o)
        del o["FORA_DO_CONTRATO"]["DA_FONTE"]["FACT_LOCATION_ONDE"]
        self.assertIn("sem posicao", self.conferir(o)["C3_LUGAR_PROPRIO"])
        self.assertEqual(self.liberar(o)["LIBERACAO"], "NAO_PARA_CLIENTE")

    def test_posicao_de_outra_ocorrencia_fora_da_afirmacao_nao_libera(self):
        o = copy.deepcopy(self.o)
        i, f = _pos("Molise")                          # a do titulo: o nome bate, o lugar do facto nao
        o["FORA_DO_CONTRATO"]["DA_FONTE"]["FACT_LOCATION_ONDE"] = {"INICIO": i, "FIM": f, "TRECHO": "Molise"}
        self.assertIn("fora do trecho da afirmacao", self.conferir(o)["C3_LUGAR_PROPRIO"])

    def test_posicao_que_nao_bate_com_o_texto_nao_libera(self):
        o = copy.deepcopy(self.o)
        o["FORA_DO_CONTRATO"]["DA_FONTE"]["FACT_LOCATION_ONDE"]["INICIO"] += 1
        self.assertIn("nao esta literal", self.conferir(o)["C3_LUGAR_PROPRIO"])


class E5_TodoTrechoEhCitacaoNaSuaPosicao(Base):
    def test_liberado_leva_lugar_em(self):
        p = self.liberar(self.o)["PROVA"][0]
        self.assertEqual(set(p["SECAO"]), {"AFIRMACAO_EM", "DATA_EM", "LUGAR_EM"})

    def test_cada_trecho_esta_literal_no_texto_na_posicao_declarada(self):
        """A mesma pergunta que o E5 do LAB faz: para cada TRECHO_*, texto[*_EM:*_EM+len] == TRECHO_*."""
        o = self.liberar(self.o)
        self.assertEqual(o["LIBERACAO"], "LIBERADO_PARA_CLIENTE")
        p = o["PROVA"][0]
        trechos = [k for k in p if k.startswith("TRECHO_")]
        self.assertEqual(sorted(trechos), sorted(L.TRECHOS_LITERAIS))
        for k in trechos:
            em = p["SECAO"][L.TRECHOS_LITERAIS[k]]
            self.assertEqual(TEXTO[em:em + len(p[k])], p[k], k)

    def test_a_leitura_do_sistema_nao_se_chama_trecho(self):
        p = self.liberar(self.o)["PROVA"][0]
        self.assertNotIn("TRECHO_DA_DATA_LEGIVEL", p)
        self.assertEqual(p["DATA_LEGIVEL_INTERPRETADA"], "REGIONE SINTETICA Dal 01-01-2031 al 07-01-2031")
        self.assertNotIn(p["DATA_LEGIVEL_INTERPRETADA"], TEXTO)   # e interpretacao: nao existe na fonte
        self.assertEqual(p["TRECHO_DA_DATA"], CAB)                 # o literal fica como esta


if __name__ == "__main__":
    unittest.main()
