#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A CONFISSAO TEM DE CABER NA COLUNA QUE A RECEBE.

    NOT_PRESERVED != AUSENTE != NAO SEI != ZERO

Os quatro continuam diferentes. O que estes testes guardam e outra coisa: que
a fronteira escreve, em cada campo, a palavra que o DONO daquele campo
entende — e que ela nao colapsa os conceitos para conseguir isso.
"""
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
from coleta import ingresso as ing  # noqa: E402

# O vocabulario que a migration 001 declara para o enum `pais`. Lido do
# ficheiro, e nao copiado para aqui como segunda verdade.
MIGRATION = os.path.join(RAIZ, "supabase", "migrations",
                         "001_fundacao_geografia_e_proveniencia.sql")


def _vocabulario_do_enum_pais():
    import re
    with open(MIGRATION, encoding="utf-8") as f:
        m = re.search(r"create type pais as enum \(([^)]*)\)", f.read())
    return {x.strip().strip("'") for x in m.group(1).split(",")} if m else set()


class ACadaCampoASuaPalavra(unittest.TestCase):

    def test_o_pais_em_falta_usa_a_palavra_do_enum(self):
        c = ing._corrida_completa({"RUN_ID": "R"})
        self.assertIn(c["SOURCE_COUNTRY"], _vocabulario_do_enum_pais(),
                      "a fronteira escreveu no enum uma palavra que ele "
                      "recusa")

    def test_os_outros_campos_continuam_a_dizer_not_preserved(self):
        c = ing._corrida_completa({"RUN_ID": "R"})
        for campo in ("PLATFORM", "ACTOR", "ACTOR_VERSION", "RULE_VERSION"):
            self.assertEqual(c[campo], "NOT_PRESERVED",
                             "%s deixou de confessar com a palavra desta "
                             "casa" % campo)

    def test_os_dois_conceitos_nao_foram_colapsados(self):
        """`NOT_PRESERVED` e `NAO SEI` continuam a ser coisas diferentes.

        Se a correcao tivesse trocado a palavra em TODO O LADO, os dois
        conceitos ficavam um so — e a casa perdia a diferenca entre «nao
        guardei» e «nao sei».
        """
        c = ing._corrida_completa({"RUN_ID": "R"})
        self.assertNotEqual(c["PLATFORM"], c["SOURCE_COUNTRY"],
                            "os dois campos confessam com a mesma palavra: "
                            "os conceitos colaram-se")
        self.assertEqual(ing.AUSENCIA_PADRAO, "NOT_PRESERVED")

    def test_o_que_o_chamador_trouxe_nao_e_tocado(self):
        c = ing._corrida_completa({"RUN_ID": "R", "SOURCE_COUNTRY": "IT",
                                   "PLATFORM": "repo"})
        self.assertEqual(c["SOURCE_COUNTRY"], "IT")
        self.assertEqual(c["PLATFORM"], "repo")

    def test_a_tabela_nao_inventa_campos(self):
        """So campos que o dono do RAW le entram na traducao."""
        for campo in ing.AUSENCIA_POR_CAMPO:
            self.assertIn(campo, ing.CORRIDA_PARA_O_RAW,
                          "%s nao e um campo que o dono do RAW leia" % campo)


class ADiferencaEDoDonoDaColuna(unittest.TestCase):

    def test_a_palavra_escolhida_e_a_que_a_migration_declara(self):
        """Nao foi escolhida por gosto: e o default da propria coluna."""
        with open(MIGRATION, encoding="utf-8") as f:
            sql = f.read()
        self.assertIn("source_country         pais not null default 'NAO_SEI'",
                      sql, "o default da coluna mudou — remedir a escolha")
        self.assertEqual(ing.AUSENCIA_POR_CAMPO["SOURCE_COUNTRY"], "NAO_SEI")

    def test_not_preserved_nao_cabe_no_enum(self):
        """A razao do defeito, guardada para nao voltar a ser descoberta."""
        self.assertNotIn("NOT_PRESERVED", _vocabulario_do_enum_pais())


DSN = os.environ.get("BANCO_DESCARTAVEL_URL") or ""


@unittest.skipUnless(DSN, "sem PostgreSQL descartavel")
class ContraOBancoDeVerdade(unittest.TestCase):
    """⚠️ A PROVA QUE INTERESSA CORRE CONTRA O BANCO.

    Um teste que so compara strings nao teria apanhado o defeito original: a
    string `NOT_PRESERVED` e perfeitamente valida em Python. Quem a recusou
    foi o PostgreSQL.
    """

    def _aterra(self, corrida):
        import hashlib
        import importlib.util
        s = importlib.util.spec_from_file_location(
            "pgx", os.path.join(RAIZ, "provas",
                                "preservar_coleta_no_postgres.py"))
        pg = importlib.util.module_from_spec(s)
        s.loader.exec_module(pg)
        from guarda.preservar_coleta import preservar, ArmazemDeMentira
        pdf = None
        for r, _d, fs in os.walk(os.path.join(RAIZ, "data",
                                              "collection-store")):
            for f in fs:
                if f.endswith(".pdf"):
                    pdf = os.path.join(r, f)
                    break
            if pdf:
                break
        with open(pdf, "rb") as f:
            dados = f.read()
        sha = hashlib.sha256(dados).hexdigest()
        art = {"COUNTRY": "IT", "SOURCE_SLUG": "IT-T2-002",
               "ARTIFACT_KIND": "DOCUMENT", "NAME": os.path.basename(pdf),
               "SOURCE_NATIVE_ID": os.path.basename(pdf), "SHA256": sha,
               "BYTES": len(dados), "MEDIA_TYPE": "application/pdf",
               "CAPTURED_AT": "2026-09-02T15:20:48Z",
               "SOURCE_ID": "IT-T2-002",
               "SOURCE_URL": "https://exemplo.invalido/x.pdf"}
        mem = pg.MemoriaPostgres(DSN)
        rec = preservar(ing._corrida_completa(corrida), [art],
                        ArmazemDeMentira(), lambda o: dados, memoria=mem,
                        terminou_em="2026-09-12T00:05:00Z")
        n = int(mem._valor(
            "select count(*) from public.raw_asset where run_id = '%s'"
            % corrida["RUN_ID"]))
        return n, rec

    def test_corrida_sem_pais_aterra_o_bruto(self):
        import uuid
        n, rec = self._aterra({"RUN_ID": "T-SEMPAIS-" + uuid.uuid4().hex[:8],
                               "STARTED_AT": "2026-09-12T00:00:00Z",
                               "PLATFORM": "repo", "ACTOR": "teste",
                               "ACTOR_VERSION": "1", "RULE_VERSION": "1"})
        self.assertEqual(n, 1, "o bruto nao aterrou sem pais declarado")
        self.assertEqual(rec["RUN_STATE"], "COMPLETE")
        self.assertFalse((rec.get("MEMORIA") or {}).get("ERRO"),
                         "o banco recusou alguma coisa")

    def test_corrida_minima_aterra_o_bruto(self):
        import uuid
        n, rec = self._aterra({"RUN_ID": "T-MIN-" + uuid.uuid4().hex[:8],
                               "STARTED_AT": "2026-09-12T00:00:00Z"})
        self.assertEqual(n, 1)
        self.assertEqual(rec["RUN_STATE"], "COMPLETE")

    def test_o_pais_declarado_chega_intacto(self):
        import uuid
        rid = "T-COMPAIS-" + uuid.uuid4().hex[:8]
        n, _rec = self._aterra({"RUN_ID": rid,
                                "STARTED_AT": "2026-09-12T00:00:00Z",
                                "PLATFORM": "repo", "ACTOR": "teste",
                                "ACTOR_VERSION": "1", "RULE_VERSION": "1",
                                "SOURCE_COUNTRY": "IT"})
        self.assertEqual(n, 1)
        import importlib.util
        s = importlib.util.spec_from_file_location(
            "pgy", os.path.join(RAIZ, "provas",
                                "preservar_coleta_no_postgres.py"))
        pg = importlib.util.module_from_spec(s)
        s.loader.exec_module(pg)
        mem = pg.MemoriaPostgres(DSN)
        self.assertEqual(
            mem._valor("select source_country::text from "
                       "public.collection_run where run_id = '%s'" % rid),
            "IT", "o pais declarado foi trocado pela confissao")


if __name__ == "__main__":
    unittest.main()
