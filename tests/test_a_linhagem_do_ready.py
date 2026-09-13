#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS GUARDAS DA LINHAGEM DO READY — sem banco, e por isso correm sempre.

A prova de valor vive em `provas/a_linhagem_do_ready.py`, contra PostgreSQL 16
descartável, e é ela que mede a volta inteira até ao byte. Aqui ficam as
guardas que não precisam de banco — e que mordem no dia em que alguém
«simplificar» o campo.

    TER RAW ≠ O READY CONSEGUIR PROVAR QUAL RAW É O SEU.
"""
import ast
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "coleta")):
    if p not in sys.path:
        sys.path.insert(0, p)
import _gavetas                       # noqa: E402,F401
import admissao                       # noqa: E402

ROTA = os.path.join(RAIZ, "coleta", "rota_forward_documento.py")
ORQ = os.path.join(RAIZ, "orquestrador", "orquestrador.py")
BIBLIA = os.path.join(RAIZ, "BIBLIA-CANONICA-DA-COLETA.md")

CAMPOS = ("ESTADO", "ITEM_ID", "RAW_OBSERVATION_ID", "UNIVERSO", "TEXTO",
          "SOURCE_ID", "SOURCE_LOCATION", "FACT_LOCATION", "FACT_TIME",
          "CAPTURED_AT", "CORRIDA", "ADMITIDO_POR")


def _fonte(caminho):
    with io.open(caminho, encoding="utf-8") as fh:
        return fh.read()


def _bom(**troca):
    item = {"id": "i-1", "texto": "Ensaio de campo publicado com DOI",
            "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
    item.update(troca)
    return item


def _unidade(**troca):
    item = _bom(**troca)
    return admissao.pronto_para_inteligencia(
        item, admissao.decidir(item, "T7", corrida="guarda"))


class OContratoLevaAObservacao(unittest.TestCase):

    def test_o_contrato_tem_os_doze_campos_e_na_ordem_da_lei(self):
        self.assertEqual(CAMPOS, tuple(_unidade(raw_asset_id=9)))

    def test_a_observacao_viaja_com_o_valor_que_a_rota_entregou(self):
        self.assertEqual(9, _unidade(raw_asset_id=9)["RAW_OBSERVATION_ID"])

    def test_sem_observacao_diz_NAO_SEI_e_nao_inventa(self):
        """⚠️ AUSÊNCIA DIZ-SE. Um id inventado aponta para o bruto de outro."""
        self.assertEqual("NAO SEI", _unidade()["RAW_OBSERVATION_ID"])

    def test_um_id_falsy_NAO_vira_NAO_SEI(self):
        """⚠️ O `or` QUE QUASE ESCREVEU UMA FRASE FALSA (know-how §102.4).

        `raw_asset.id` é `bigserial` e não chega a 0 — mas quem escreve o
        contrato não tem de depender disso. Um `or` aqui transformaria um id
        falsy num «NÃO SEI» silencioso, e um «NÃO SEI» inventado é pior do que
        um id errado: ninguém o vai procurar.
        """
        self.assertEqual(0, _unidade(raw_asset_id=0)["RAW_OBSERVATION_ID"])

    def test_a_observacao_nao_e_a_corrida_nem_o_item(self):
        u = _unidade(raw_asset_id=9)
        self.assertNotEqual(u["RAW_OBSERVATION_ID"], u["CORRIDA"])
        self.assertNotEqual(u["RAW_OBSERVATION_ID"], u["ITEM_ID"])

    def test_o_construtor_nao_deriva_a_observacao_de_mais_nada(self):
        """Lê-se o CÓDIGO: o campo só pode sair de `raw_asset_id`.

        Uma guarda por valor passaria com `item.get('raw_asset_id') or
        sha(item)`. Esta lê a atribuição e exige que ela venha de UMA leitura.
        """
        arvore = ast.parse(_fonte(os.path.join(RAIZ, "admissao",
                                               "admissao.py")))
        lidas = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.FunctionDef) \
                    and no.name == "pronto_para_inteligencia":
                for d in ast.walk(no):
                    if isinstance(d, ast.Call) \
                            and isinstance(d.func, ast.Attribute) \
                            and d.func.attr == "get" \
                            and isinstance(d.func.value, ast.Name) \
                            and d.func.value.id == "item" \
                            and d.args \
                            and isinstance(d.args[0], ast.Constant):
                        lidas.add(d.args[0].value)
        for proibido in ("sha256", "url", "storage_path", "run_id",
                         "filename", "document_id"):
            self.assertNotIn(proibido, lidas,
                             "o contrato NAO pode ler %r para a linhagem"
                             % proibido)
        self.assertIn("raw_asset_id", lidas)


class AsRotasEntregamAObservacao(unittest.TestCase):
    """⚠️ O VALOR JÁ ESTAVA EM MÃOS. O buraco era deitá-lo fora na porta."""

    def test_a_rota_forward_entrega_raw_asset_id_a_porta(self):
        self.assertIn("'raw_asset_id': unidade.get('RAW_ASSET_ID')",
                      _fonte(ROTA))

    def test_o_orquestrador_tambem_o_entrega(self):
        self.assertIn('"raw_asset_id": estruturado.get("RAW_ASSET_ID")',
                      _fonte(ORQ))


class ALeiDizOMesmoQueOCodigo(unittest.TestCase):

    def test_a_COL_LAW_043_declara_RAW_OBSERVATION_ID(self):
        biblia = _fonte(BIBLIA)
        trecho = biblia[biblia.index("## COL-LAW-043"):
                        biblia.index("## COL-LAW-044")]
        self.assertIn("RAW_OBSERVATION_ID", trecho,
                      "a lei tem de declarar o campo que o codigo devolve")
        for campo in CAMPOS:
            self.assertIn(campo, trecho)

    def test_a_lei_recusa_derivar_a_observacao_de_sha_ou_caminho(self):
        biblia = _fonte(BIBLIA)
        trecho = biblia[biblia.index("## COL-LAW-043"):
                        biblia.index("## COL-LAW-044")]
        self.assertIn("raw_asset.id", trecho)
        self.assertIn("Nunca", trecho)

    def test_storage_object_id_NAO_entra_no_contrato(self):
        """A menor identidade que fecha a estrada é a certa.

        `raw_asset` já aponta para a cópia por chave estrangeira composta
        `(storage_object_id, sha256)`. Duplicá-la aqui daria duas declarações
        do mesmo parentesco, livres para divergir.
        """
        self.assertNotIn("STORAGE_OBJECT_ID", _unidade(raw_asset_id=9))


class OTextoNaoViajaEIssoEUmaDecisao(unittest.TestCase):
    """⚠️ NÃO VIAJAR ≠ PERDER-SE.

    `TEXT_KIND`, `TEXT_RELATION` e `LANGUAGE` ficam nos bytes do bruto —
    `coleta/ingresso.py::_bytes_do_item` serializa o item inteiro. A prova de
    que se resolvem por linhagem está em `provas/a_linhagem_do_ready.py::S4-S6`,
    contra bytes reais.
    """

    def test_a_especie_do_texto_nao_entra_no_contrato_READY(self):
        u = _unidade(raw_asset_id=9)
        for campo in ("TEXT_KIND", "TEXT_RELATION", "LANGUAGE", "TEXT_UNITS"):
            self.assertNotIn(campo, u)

    def test_o_ingresso_continua_a_serializar_o_item_inteiro(self):
        fonte = _fonte(os.path.join(RAIZ, "coleta", "ingresso.py"))
        self.assertIn("def _bytes_do_item", fonte)
        self.assertIn("TEXT_UNITS", fonte)


if __name__ == "__main__":
    unittest.main(verbosity=2)
