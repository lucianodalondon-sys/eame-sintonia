#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""As edicoes do registro (IT-T4-001): o diff produto a produto e o EVENTO_REGULATORIO.

D116 + D117.1 (dono, 27/09). Duas edicoes CSV de fixture, pequenas, NUNCA baixadas
(`tests/fixtures/it_t4_001/`). Cada teste abaixo e o que apanha um defeito plantado
na mutacao da missao REFERENCIA-MANUTENCAO:

    sobrescrever a edicao antiga      -> AEdicaoAntigaNuncaSeApaga
    inventar cultura                  -> NenhumaCulturaInventada
    pular a revogacao                 -> ARevogacaoApareceComADataDaFonte
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import edicoes_do_registro as E  # noqa: E402

FIX = os.path.join(RAIZ, "tests", "fixtures", "it_t4_001")
A = os.path.join(FIX, "PROD_FTS_6_20260914.csv")
B = os.path.join(FIX, "PROD_FTS_6_20260921.csv")


def _diff():
    return E.comparar(A, B, observed_date="2026-09-27")


def _por(r, num, campo=None):
    return [m for m in r["MUDANCAS"] if m["NUMERO_REGISTRAZIONE"] == num
            and (campo is None or m["CAMPO"] == campo)]


class ODiffProdutoAProduto(unittest.TestCase):
    def test_o_portao_de_versao_autoriza(self):
        self.assertEqual(_diff()["ESTADO_DA_VERSAO"], "NEW_VERSION_CHANGED")

    def test_cada_mudanca_tem_os_campos_do_dono_e_da_regua(self):
        for m in _diff()["MUDANCAS"]:
            for c in ("NUMERO_REGISTRAZIONE", "CAMPO", "ANTES", "DEPOIS", "EDICAO",
                      "ENTITY", "REGISTRATION_ID", "CHANGE_TYPE", "BEFORE", "AFTER",
                      "SOURCE_VERSION_A", "SOURCE_VERSION_B", "VERDICT"):
                self.assertIn(c, m, "%s sem %s" % (m.get("NUMERO_REGISTRAZIONE"), c))
            self.assertEqual(m["EDICAO"], "2026-09-21")
            self.assertEqual(m["SOURCE_VERSION_A"]["VERSION_DATE"], "2026-09-14")
            self.assertEqual(len(m["SOURCE_VERSION_B"]["SHA256"]), 64)

    def test_os_tipos_medidos_na_fixture(self):
        t = _diff()["TOTAIS"]
        self.assertEqual(t, {"NEW_REGISTRATION": 1, "REGISTRATION_LEFT_THE_LIST": 1,
                             "STATUS_CHANGE": 1, "HOLDER_CHANGE": 1, "COMPOSITION_CHANGE": 1,
                             "DATE_CHANGE": 3, "REFERENCE_NAME_CHANGE": 0, "UNKNOWN_CHANGE": 5})
        self.assertEqual(_diff()["EVENTOS"], 8)

    def test_registro_novo_com_a_data_de_registrazione(self):
        m, = _por(_diff(), "019999")
        self.assertEqual((m["CHANGE_TYPE"], m["ANTES"], m["DEPOIS"]), ("NEW_REGISTRATION", None, "019999"))
        self.assertEqual(m["FACT_TIME"], "2026-09-16")

    def test_mudanca_de_titular(self):
        m, = _por(_diff(), "012222", "ragione_sociale")
        self.assertEqual((m["CHANGE_TYPE"], m["ANTES"], m["DEPOIS"]),
                         ("HOLDER_CHANGE", "SIPCAM S.P.A.", "ADAMA ITALIA S.R.L."))
        self.assertEqual(m["FACT_TIME"], "NAO SEI", "a linha nao data a mudanca de titular")

    def test_mudanca_de_substancia(self):
        m, = _por(_diff(), "013333", "sostanze_attive")
        self.assertEqual(m["CHANGE_TYPE"], "COMPOSITION_CHANGE")

    def test_vencimento_alterado(self):
        m, = _por(_diff(), "014444", "data_scadenza_autorizzazione")
        self.assertEqual((m["CHANGE_TYPE"], m["SUBTIPO"], m["ANTES"], m["DEPOIS"]),
                         ("DATE_CHANGE", "VENCIMENTO_ALTERADO", "30/09/2026", "30/09/2027"))

    def test_so_grafia_nao_vira_evento(self):
        for campo in ("ragione_sociale", "sostanze_attive"):
            m, = _por(_diff(), "017777", campo)
            self.assertEqual(m["CHANGE_TYPE"], "UNKNOWN_CHANGE")
            self.assertFalse(m["EMITE_EVENTO"])

    def test_edicao_sem_coluna_obrigatoria_falha_fechada(self):
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, "PROD_FTS_6_20260928.csv")
            with open(B, encoding="utf-8") as f:
                linhas = [l.replace(";sostanze_attive;", ";outra;") for l in f]
            with open(p, "w", encoding="utf-8") as f:
                f.writelines(linhas)
            with self.assertRaises(E.EdicaoInvalida):
                E.ler_edicao(p)
        finally:
            shutil.rmtree(d)

    def test_mesma_edicao_nao_e_mudanca(self):
        r = E.comparar(A, A)
        self.assertEqual(r["ESTADO_DA_VERSAO"], "NO_NEW_VERSION")
        self.assertEqual(r["MUDANCAS"], [])


class ARevogacaoApareceComADataDaFonte(unittest.TestCase):
    def test_a_revogacao_e_detectada(self):
        m, = _por(_diff(), "011111", "stato_amministrativo")
        self.assertEqual((m["CHANGE_TYPE"], m["SUBTIPO"]), ("STATUS_CHANGE", "REVOGACAO"))
        self.assertTrue(m["EMITE_EVENTO"])

    def test_a_data_e_a_do_decreto_na_linha(self):
        m, = _por(_diff(), "011111", "stato_amministrativo")
        self.assertEqual(m["FACT_TIME"], "2026-09-15")
        self.assertEqual(m["DATA_DECORRENZA_REVOCA"], "2027-03-15")
        self.assertIn("data_decreto_revoca", m["FACT_TIME_BASIS"])

    def test_sair_do_ficheiro_nao_e_revogacao(self):
        m, = _por(_diff(), "015555")
        self.assertEqual((m["CHANGE_TYPE"], m["VERDICT"]), ("REGISTRATION_LEFT_THE_LIST", "UNRESOLVED"))
        self.assertNotIn("SUBTIPO", m)


class NenhumaCulturaInventada(unittest.TestCase):
    """A fixture tem «RAME VITE»: o nome carrega uma cultura, e ela NAO pode sair."""

    def test_toda_mudanca_diz_cultura_nao_sei(self):
        for m in _diff()["MUDANCAS"]:
            self.assertTrue(m["CULTURA_ALVO"].startswith("NAO SEI"), m["NUMERO_REGISTRAZIONE"])

    def test_nenhum_ready_sai_com_cultura(self):
        for p in E.emitir(_diff())["PRONTOS"]:
            self.assertEqual(p["JANELA_DECLARADA"]["CULTURA"]["VALOR"], "NAO SEI", p["ITEM_ID"])
            self.assertTrue(p["FATO"]["CULTURA_ALVO"].startswith("NAO SEI"))


class OEventoPelaPortaCanonica(unittest.TestCase):
    def test_os_oito_eventos_passam_a_porta_t4(self):
        e = E.emitir(_diff())
        self.assertEqual((len(e["PRONTOS"]), e["RECUSADOS"]), (8, []))
        for p in e["PRONTOS"]:
            self.assertEqual((p["ESTAGIO"], p["UNIVERSO"], p["SOURCE_ID"]), ("FATO", "T4", "IT-T4-001"))
            self.assertEqual(p["PUBLISHED_AT"], "2026-09-21")
            self.assertEqual(p["FATO"]["ESPECIE_DO_EVENTO"], "EVENTO_REGULATORIO")

    def test_a_data_da_edicao_nunca_vira_fato(self):
        for p in E.emitir(_diff())["PRONTOS"]:
            self.assertNotEqual(p["FACT_TIME"], "2026-09-21", p["ITEM_ID"])

    def test_pousa_na_sala_e_o_retry_e_ja_estava(self):
        import sala_de_espera as espera
        d = tempfile.mkdtemp()
        antes, amb = espera.MORADA, os.environ.pop("SINTONIA_SALA_BACKEND", None)
        espera.MORADA = d
        try:
            r1 = E.emitir(_diff(), pousar=True)["SALA"]
            r2 = E.emitir(_diff(), pousar=True)["SALA"]
            self.assertEqual((r1["ESTADO"], r1["UNIDADES"]), (espera.POUSOU, 8))
            self.assertEqual(r2["ESTADO"], espera.JA_ESTAVA)
            self.assertEqual(r1["RUN_ID"], "IT-T4-DIFF-20260914-20260921")
        finally:
            espera.MORADA = antes
            if amb is not None:
                os.environ["SINTONIA_SALA_BACKEND"] = amb
            shutil.rmtree(d)


class AEdicaoAntigaNuncaSeApaga(unittest.TestCase):
    def test_o_diff_guardado_nao_e_sobrescrito(self):
        d = tempfile.mkdtemp()
        try:
            r = _diff()
            g = E.guardar_diff(r, d)
            with open(g["CAMINHO"], encoding="utf-8") as f:
                original = f.read()
            self.assertEqual(E.guardar_diff(r, d)["ESTADO"], "JA_ESTAVA")
            outro = json.loads(json.dumps(r))
            outro["MUDANCAS"] = outro["MUDANCAS"][:1]
            with self.assertRaises(E.DiffEmConflito):
                E.guardar_diff(outro, d)
            with open(g["CAMINHO"], encoding="utf-8") as f:
                self.assertEqual(f.read(), original, "a comparacao anterior foi apagada")
        finally:
            shutil.rmtree(d)

    def test_a_biblioteca_guarda_todas_as_edicoes(self):
        obs = [
            {"SOURCE_ID": "IT-T4-001", "HEALTH_STATE": "HEALTHY", "DOCUMENT_ID": "MINSALUTE:FTS6:20260914",
             "SOURCE_DATE_ISO": "2026-09-14", "CAPTURED_AT": "2026-09-18T17:20:53Z",
             "RAW_PATH": "tests/fixtures/it_t4_001/PROD_FTS_6_20260914.csv"},
            {"SOURCE_ID": "IT-T4-001", "HEALTH_STATE": "HEALTHY", "DOCUMENT_ID": "MINSALUTE:FTS6:20260921",
             "SOURCE_DATE_ISO": "2026-09-21", "CAPTURED_AT": "2026-09-22T19:00:00Z",
             "RAW_PATH": "tests/fixtures/it_t4_001/PROD_FTS_6_20260921.csv"},
            {"SOURCE_ID": "IT-T4-001", "HEALTH_STATE": "HEALTHY", "DOCUMENT_ID": "MINSALUTE:FTS6:20260921",
             "SOURCE_DATE_ISO": "2026-09-21", "CAPTURED_AT": "2026-09-23T19:00:00Z", "RAW_PATH": None},
            {"SOURCE_ID": "IT-T4-001", "HEALTH_STATE": "FAILED", "DOCUMENT_ID": "MINSALUTE:FTS6:20260928"},
        ]
        eds = E.edicoes_do_livro(obs)
        self.assertEqual([e["EDICAO"] for e in eds], ["2026-09-14", "2026-09-21"])
        self.assertTrue(all(e["BYTES_NESTA_ARVORE"] for e in eds))
        self.assertEqual(eds[1]["ULTIMA_CHECAGEM_OK"], "2026-09-23T19:00:00Z")
        self.assertEqual(eds[1]["PRIMEIRA_CAPTURA"], "2026-09-22T19:00:00Z")


if __name__ == "__main__":
    unittest.main(verbosity=2)
