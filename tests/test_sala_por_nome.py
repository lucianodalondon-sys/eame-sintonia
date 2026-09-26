# -*- coding: utf-8 -*-
"""QUATRO-CHAVES-V2 — a Sala lê e escreve cada coluna PELO NOME.

AVISO da INSTALAÇÃO-2 (25/09): a leitura do backend Postgres era POSICIONAL
(`c[18]`, `c[19]`, `c[20]`, `c[21]`, e a nuvem acrescentava `c[22]`), e a escrita
eram duas listas paralelas — nomes num sítio, valores noutro. Juntar duas
linhas que acrescentam colunas obrigava a renumerar, e um índice errado NÃO dá
erro: lê ou grava a coluna vizinha em silêncio.

Estes testes não precisam de banco: substituem `_consultar`/`_executar` e
conferem que cada campo volta da SUA coluna e que cada valor vai para a SUA.
"""
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(RAIZ, "admissao"), RAIZ]

import sala_de_espera as S  # noqa: E402

# campo do READY -> coluna da Sala (o que `ler()` tem de respeitar)
CAMPO_DA_COLUNA = {
    "item_id": "ITEM_ID", "universo": "UNIVERSO", "texto": "TEXTO",
    "source_id": "SOURCE_ID", "source_location": "SOURCE_LOCATION",
    "fact_location": "FACT_LOCATION", "fact_time": "FACT_TIME",
    "captured_at": "CAPTURED_AT", "admitido_por": "ADMITIDO_POR",
    "estagio": "ESTAGIO", "fact_time_basis": "FACT_TIME_BASIS",
    "fact_location_basis": "FACT_LOCATION_BASIS", "published_at": "PUBLISHED_AT",
    "observed_at": "OBSERVED_AT",
    "source_declared_evidence_class": "SOURCE_DECLARED_EVIDENCE_CLASS",
    "published_at_basis": "PUBLISHED_AT_BASIS",
    "source_location_basis": "SOURCE_LOCATION_BASIS",
}
JSONS = {"fato": "FATO", "completude_tempo_lugar": "COMPLETUDE_TEMPO_LUGAR",
         "tempo_lugar_evidencia": "TEMPO_LUGAR_EVIDENCIA",
         "janela_declarada": "JANELA_DECLARADA"}


def _pg():
    b = S._Postgres.__new__(S._Postgres)      # sem ligar a banco nenhum
    return b


class ALeituraEPeloNome(unittest.TestCase):

    def _linha(self):
        vals = []
        for c in S.COLUNAS_LIDAS:
            if c == "ordem":
                vals.append("0")
            elif c == "raw_observation_id":
                vals.append("77")
            elif c in JSONS:
                vals.append(json.dumps({"MARCA": c}))
            else:
                vals.append("MARCA-" + c)
        return vals

    def test_cada_campo_volta_da_sua_coluna(self):
        b = _pg()
        pedido = {}

        def consultar(sql):
            pedido["sql"] = sql
            return [b.SEP.join(self._linha())]
        b._consultar = consultar
        item = b.ler("RUN-X")["ITENS"][0]
        for coluna, campo in CAMPO_DA_COLUNA.items():
            self.assertEqual(item[campo], "MARCA-" + coluna, campo)
        for coluna, campo in JSONS.items():
            self.assertEqual(item[campo], {"MARCA": coluna}, campo)
        self.assertEqual(item["RAW_OBSERVATION_ID"], 77)
        self.assertEqual(item["CORRIDA"], "RUN-X")
        # o select nasce da MESMA lista que a leitura usa
        self.assertIn("select " + ", ".join(S.COLUNAS_LIDAS) + " ", pedido["sql"])

    def test_numero_de_valores_errado_rebenta(self):
        b = _pg()
        b._consultar = lambda sql: [b.SEP.join(self._linha()[:-1])]
        with self.assertRaises(S.SalaIndisponivel):
            b.ler("RUN-X")

    def test_nenhuma_leitura_posicional_em_ler(self):
        import inspect
        codigo = re.sub(r"#.*", "", inspect.getsource(S._Postgres.ler))
        self.assertIsNone(re.search(r"c\[\d+\]", codigo))


class AEscritaEPeloNome(unittest.TestCase):

    def _unidade(self):
        u = {c: "MARCA-" + c for c in S.CAMPOS_READY}
        u["RAW_OBSERVATION_ID"] = 5
        for campo in ("FATO", "COMPLETUDE_TEMPO_LUGAR", "TEMPO_LUGAR_EVIDENCIA",
                      "JANELA_DECLARADA"):
            u[campo] = "J-" + campo
        return u

    def _script(self):
        b = _pg()
        visto = {}

        def executar(script):
            visto["s"] = script
            return 0, "%s:1:0" % S.POUSOU, ""
        b._executar = executar
        b.pousar("RUN-Y", [self._unidade()])
        return visto["s"]

    def test_cada_valor_vai_para_a_sua_coluna(self):
        s = self._script()
        m = re.search(r"insert into _entrada\s*\(([^)]*)\)\s*values\s*\((.*?)\);", s, re.S)
        self.assertTrue(m, "nao achei o insert em _entrada")
        nomes = [n.strip() for n in m.group(1).split(",")]
        valores = [v.strip() for v in re.split(r",\s(?=(?:[^']*'[^']*')*[^']*$)", m.group(2))]
        self.assertEqual(nomes, list(S.COLUNAS_ESCRITAS))
        self.assertEqual(len(valores), len(nomes))
        par = dict(zip(nomes, valores))
        self.assertEqual(par["run_id"], "'RUN-Y'")
        self.assertEqual(par["raw_observation_id"], "5")
        self.assertEqual(par["published_at_basis"], "'MARCA-PUBLISHED_AT_BASIS'")
        self.assertEqual(par["source_location_basis"], "'MARCA-SOURCE_LOCATION_BASIS'")
        self.assertEqual(par["janela_declarada"], "'\"J-JANELA_DECLARADA\"'")
        self.assertEqual(par["tempo_lugar_evidencia"], "'\"J-TEMPO_LUGAR_EVIDENCIA\"'")
        self.assertEqual(par["fato"], "'\"J-FATO\"'")

    def test_as_tres_listas_de_colunas_sao_a_mesma(self):
        s = self._script()
        lista = ", ".join(S.COLUNAS_ESCRITAS)
        self.assertEqual(s.count(lista), 3)   # _entrada, insert na Sala, select

    def test_as_colunas_lidas_existem_nas_escritas_ou_sao_da_sala(self):
        self.assertLessEqual(set(S.COLUNAS_LIDAS) - {"ordem"}, set(S.COLUNAS_ESCRITAS))
        self.assertIn("janela_declarada", S.COLUNAS_LIDAS)
        self.assertIn("janela_declarada", S.COLUNAS_ESCRITAS)


class OsPendentesSaoPeloNome(unittest.TestCase):
    """`listar_pendentes` lia `c[0]`, `c[1]`, `c[2]` (QUATRO-CHAVES-MEDIR, 26/09)."""

    def _listar(self, linha):
        b = _pg()
        pedido = {}

        def consultar(sql):
            pedido["sql"] = sql
            return [b.SEP.join(linha)]
        b._consultar = consultar
        return b.listar_pendentes(), pedido["sql"]

    def test_cada_chave_volta_da_sua_coluna(self):
        vals = {"run_id": "RUN-P", "ordem": "7", "item_id": "derived:p-1"}
        fora, sql = self._listar([vals[c] for c, _ in S.COLUNAS_PENDENTES])
        self.assertEqual(fora, [{"RUN_ID": "RUN-P", "ORDEM": 7, "ITEM_ID": "derived:p-1"}])
        self.assertIn("select " + ", ".join(c for c, _ in S.COLUNAS_PENDENTES) + " from", sql)

    def test_numero_de_valores_errado_rebenta(self):
        b = _pg()
        b._consultar = lambda sql: [b.SEP.join(["RUN-P", "7"])]
        with self.assertRaises(S.SalaIndisponivel):
            b.listar_pendentes()

    def test_nenhuma_leitura_posicional_em_listar_pendentes(self):
        import inspect
        codigo = re.sub(r"#.*", "", inspect.getsource(S._Postgres.listar_pendentes))
        self.assertIsNone(re.search(r"\w\[\d+\]", codigo))


if __name__ == "__main__":
    unittest.main()
