#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS LEITORES, COM DUAS OBSERVAÇÕES NO MESMO OBJETO.

O QUE ISTO PROVA
----------------
Que nenhum leitor desta casa responde «a primeira linha» quando há duas.

Enquanto `unique (raw_asset.storage_path)` esteve de pé, **uma** observação por
endereço era a lei, e todo leitor que perguntasse pelo endereço recebia uma
linha. As três portas de memória faziam a mesma coisa:

    return linhas[0] if linhas else None

Isso não é um defeito que se veja a olho: com uma linha, `linhas[0]` está
certo. Só quando existem duas é que ele passa a ser uma escolha — e uma escolha
feita pela ordem que o planeador do banco calhou devolver.

    ESCOLHER A PRIMEIRA E ESCOLHER AO ACASO COM CARA DE DETERMINISMO.

A BANCADA É O CASO QUE A FASE 10 CRIA
-------------------------------------
Um `storage_object`, duas `raw_asset` — duas corridas que observaram o mesmo
documento, no mesmo endereço. O SQLite desta bancada não tem o `unique` do
endereço, exactamente como o Postgres não terá depois da fase 10.

Cada pergunta tem de dizer QUAL das duas quer, e prová-lo.
"""
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from guarda.memoria_descartavel import MemoriaDescartavel  # noqa: E402
from guarda.preservar_coleta import Memoria  # noqa: E402

CAMINHO = "IT/fonte/DOCUMENT/aaaaaaaaaaaaaaaa-731-a.pdf"
SHA = "a" * 64


class DuasObservacoesUmObjeto(unittest.TestCase):
    """A bancada que só existe depois da fase 10 — e por isso é aqui que ela
    tem de existir antes."""

    def setUp(self):
        self.banco = MemoriaDescartavel()
        # O `unique` do endereço cai, como a fase 10 o vai fazer no Postgres.
        self._recriar_sem_unique()
        self.banco.con.executescript("""
          insert into collection_run (run_id, platform, started_at, rule_version)
            values ('R-A','x','2026-09-01T00:00:00Z','1'),
                   ('R-B','x','2026-09-02T00:00:00Z','1');
          insert into storage_object (storage_path, media_type, bytes, sha256)
            values ('%s','application/pdf',10,'%s');
        """ % (CAMINHO, SHA))
        oid = self.banco.con.execute(
            "select id from storage_object").fetchone()[0]
        for run in ("R-A", "R-B"):
            self.banco.con.execute(
                "insert into raw_asset (run_id, storage_path, media_type, "
                "bytes, sha256, captured_at, storage_object_id, source_id, "
                "document_key, document_key_basis, identity_state, attempts) "
                "values (?,?,?,?,?,?,?,?,?,?,?,?)",
                (run, CAMINHO, "application/pdf", 10, SHA,
                 "2026-09-01T00:00:00Z", oid, "ARPAV", "DOC-1",
                 "SOURCE_DOCUMENT_ID", "FORWARD_IDENTIFIED", 1))
        self.banco.con.commit()

    def _recriar_sem_unique(self):
        """O equivalente honesto do `drop constraint`, em SQLite.

        Um `unique` escrito NA COLUNA faz um índice implícito, e o SQLite não
        o deixa largar — `sqlite_master` guarda-lhe `sql = NULL`, por isso nem
        procurá-lo pelo texto funciona. Recriar a tabela sem a palavra é o
        único caminho, e é exactamente a mudança que a fase 10 fará do outro
        lado: o endereço deixa de ser identidade da observação.
        """
        ddl = self.banco.con.execute(
            "select sql from sqlite_master where name='raw_asset'").fetchone()[0]
        sem = re.sub(r"(storage_path\s+text not null)\s+unique", r"\1", ddl)
        assert sem != ddl, "o `unique` do endereco mudou de forma no esquema"
        self.banco.con.executescript(
            "pragma foreign_keys=off;\n"
            "alter table raw_asset rename to raw_asset_velha;\n"
            + sem + ";\n"
            "insert into raw_asset select * from raw_asset_velha;\n"
            "drop table raw_asset_velha;\n"
            "pragma foreign_keys=on;")

    # ── a bancada é mesmo a bancada ─────────────────────────────────────
    def test_a_bancada_tem_duas_observacoes_e_um_objeto(self):
        self.assertEqual(
            self.banco.con.execute(
                "select count(*) from raw_asset").fetchone()[0], 2)
        self.assertEqual(
            self.banco.con.execute(
                "select count(*) from storage_object").fetchone()[0], 1)

    # ── e cada pergunta diz qual quer ───────────────────────────────────
    def test_a_copia_e_uma_so_e_vem_de_storage_object(self):
        copia = self.banco.copia_em(CAMINHO)
        self.assertIsNotNone(copia)
        self.assertEqual(copia["sha256"], SHA)
        # E É MESMO DE `storage_object`: uma linha de `raw_asset` traria
        # `run_id`, e a cópia não tem corrida nenhuma — ela é de todas.
        self.assertNotIn("run_id", copia)

    def test_todas_as_observacoes_daquele_endereco_sao_duas(self):
        linhas = self.banco.observacoes_em(CAMINHO)
        self.assertEqual(len(linhas), 2)
        self.assertEqual(sorted(l["run_id"] for l in linhas), ["R-A", "R-B"])

    def test_a_observacao_de_uma_corrida_e_so_dela(self):
        a = self.banco.observacao_identificada("R-A", "ARPAV", "DOC-1", SHA)
        b = self.banco.observacao_identificada("R-B", "ARPAV", "DOC-1", SHA)
        self.assertIsNotNone(a)
        self.assertIsNotNone(b)
        self.assertEqual(a["run_id"], "R-A")
        self.assertEqual(b["run_id"], "R-B")
        self.assertNotEqual(a["id"], b["id"])

    def test_a_chave_forward_nao_devolve_a_observacao_de_outra_corrida(self):
        """A trava que interessa: `run_id` está na chave, logo a pergunta de
        uma corrida nunca cai na linha da outra."""
        self.assertIsNone(
            self.banco.observacao_identificada("R-C", "ARPAV", "DOC-1", SHA))

    def test_a_corrida_ve_as_suas_e_nao_as_da_outra(self):
        for run in ("R-A", "R-B"):
            linhas = self.banco.objetos_da_corrida(run)
            self.assertEqual(len(linhas), 1, run)
            self.assertEqual(linhas[0]["run_id"], run)

    # ── e a porta não tem por onde escolher a primeira ───────────────────
    def test_a_porta_nao_expoe_nenhuma_leitura_de_uma_linha_por_endereco(self):
        """`objeto_em` não pode voltar por outra porta.

        Um método que receba um endereço e devolva UMA observação é o defeito
        com outro nome. `copia_em` recebe um endereço e devolve uma CÓPIA —
        espécie diferente, e o endereço é identidade dela. `observacoes_em`
        recebe um endereço e devolve uma LISTA.
        """
        self.assertFalse(hasattr(Memoria, "objeto_em"))
        self.assertFalse(hasattr(self.banco, "objeto_em"))
        self.assertIsInstance(self.banco.observacoes_em(CAMINHO), list)


class ASemProvaTambemTemChave(unittest.TestCase):
    """E a tentativa sem prova encontra-se pela chave dela, não pelo endereço."""

    def setUp(self):
        self.banco = MemoriaDescartavel()
        self.banco.con.executescript("""
          insert into collection_run (run_id, platform, started_at, rule_version)
            values ('R-A','x','2026-09-01T00:00:00Z','1');
          insert into storage_object (storage_path, media_type, bytes, sha256)
            values ('%s','application/pdf',10,'%s');
        """ % (CAMINHO, SHA))
        self.oid = self.banco.con.execute(
            "select id from storage_object").fetchone()[0]
        self.banco.con.execute(
            "insert into raw_asset (run_id, storage_path, media_type, bytes, "
            "sha256, captured_at, storage_object_id, source_id, "
            "identity_state, attempts) values (?,?,?,?,?,?,?,?,?,?)",
            ("R-A", CAMINHO, "application/pdf", 10, SHA,
             "2026-09-01T00:00:00Z", self.oid, "ARPAV",
             "FORWARD_IDENTITY_UNPROVEN", 1))
        self.banco.con.commit()

    def test_a_tentativa_encontra_se_pela_chave(self):
        achada = self.banco.tentativa_sem_prova("R-A", "ARPAV", self.oid, SHA)
        self.assertIsNotNone(achada)
        self.assertEqual(achada["identity_state"], "FORWARD_IDENTITY_UNPROVEN")

    def test_outra_corrida_nao_e_a_mesma_tentativa(self):
        self.assertIsNone(
            self.banco.tentativa_sem_prova("R-B", "ARPAV", self.oid, SHA))

    def test_sem_copia_a_chave_continua_a_encontrar(self):
        """O caso que reprovou uma candidata inteira.

        Uma observação NÃO preservada não tem cópia, e `storage_object_id` fica
        nulo. Em SQL, `null = null` não é verdade — uma chave escrita com `=`
        deixaria de encontrar a linha, o retry entraria outra vez, e a
        duplicata teria nascido de um operador de comparação.
        """
        self.banco.con.execute(
            "insert into raw_asset (run_id, storage_path, media_type, bytes, "
            "sha256, captured_at, storage_object_id, source_id, "
            "identity_state, preserved, not_preserved_reason, attempts) "
            "values (?,?,?,?,?,?,?,?,?,?,?,?)",
            ("R-A", CAMINHO + ".sem", "application/pdf", 10, SHA,
             "2026-09-01T00:00:00Z", None, "ARPAV",
             "FORWARD_IDENTITY_UNPROVEN", 0, "BYTE_NAO_VOLTOU", 1))
        self.banco.con.commit()
        achada = self.banco.tentativa_sem_prova("R-A", "ARPAV", None, SHA)
        self.assertIsNotNone(achada)
        self.assertIsNone(achada["storage_object_id"])


if __name__ == "__main__":
    unittest.main()
