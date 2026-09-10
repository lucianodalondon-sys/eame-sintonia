#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SEPARAÇÃO OBJETO/OBSERVAÇÃO, PROVADA NUM POSTGRES QUE MORRE NO FIM.

O QUE ISTO PROVA
----------------
Que a `migration 025` não é um desenho bonito num ficheiro: que ela **aplica**
num Postgres 16 real, **sobre dado que já existe**, e que o que ela promete
acontece — sem mexer na identidade de nenhuma observação.

    DESIGNED   é o SQL escrito
    DB_TESTED  é o SQL aplicado sobre linhas, e as travas a morder

⚠️ **SQLite não prova esta missão.** Entram aqui `NOT VALID`, `VALIDATE
CONSTRAINT`, `pg_constraint`, chave estrangeira composta e RLS. Nenhum deles
existe no SQLite com a mesma semântica, e provar contra ele seria medir outra
coisa com o nome certo.

A ORDEM É A DA VIDA REAL, E NÃO A CONVENIENTE
---------------------------------------------
Aplica-se `001` + `022`, escreve-se o acervo, e **só então** a `025`. Uma
migration que separa espécies só vale se separar dado que já estava junto —
correr a `025` sobre uma tabela vazia provaria o SQL e nada mais.

O ESCOPO, DITO SEM ALARGAR
--------------------------
`001` + `022` + `025`. As `002`-`024` não entram: a `025` não precisa delas.

    ESCOPO = FOUNDATION_MAIS_022_MAIS_025

E o que esta prova **não** afirma: que a segunda corrida do mesmo conteúdo já
entra. Ela não entra — o caso `H` mede isso de propósito, e o resultado
esperado é o conflito. A cura é da fase 10.

NENHUMA LIGAÇÃO A PRODUÇÃO
--------------------------
Mesma tranca de `preservar_coleta_no_postgres.py`: a URL é decomposta, o
`hostname` tem de ser exatamente local e o banco tem de estar na lista curta.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import importlib.util as _u  # noqa: E402

_spec = _u.spec_from_file_location(
    "prova_pg", os.path.join(RAIZ, "provas", "preservar_coleta_no_postgres.py"))
_pg = _u.module_from_spec(_spec)
_spec.loader.exec_module(_pg)

from guarda.preservar_coleta import (  # noqa: E402
    ArmazemDeMentira, caminho_do_objeto, preservar, sha256)

MIGRACOES = ["001_fundacao_geografia_e_proveniencia.sql",
             "022_o_derivado_ganha_casa.sql"]
M025 = "025_o_objeto_ganha_casa.sql"

SHA_UM = "a" * 64
SHA_GEMEO = "b" * 64          # o mesmo conteudo, em duas publicacoes
SHA_FILHO = "d" * 64
HASH_PARAM = "e" * 64

# CASO 1 · uma observacao, um endereco.
# CASO 2 · duas observacoes, dois enderecos, MESMOS bytes -> dois objetos.
# CASO 3 · uma observacao com filho derivado.
ACERVO = [
    ("IT/f/DOCUMENT/aaaa-1-um.pdf", SHA_UM, 100),
    ("IT/f/DOCUMENT/bbbb-6321-dois.pdf", SHA_GEMEO, 138284),
    ("IT/f/DOCUMENT/bbbb-731-tres.pdf", SHA_GEMEO, 138284),
]


class Banco(_pg.MemoriaPostgres):
    def executar(self, sql):
        """Aplica e DEVOLVE o erro em vez de o levantar.

        Os casos negativos precisam de ver a recusa; levantar aqui obrigaria
        cada um deles a embrulhar-se num `try`, e o ruido esconderia a prova.
        """
        try:
            self.aplicar(sql)
            return None
        except Exception as erro:                      # noqa: BLE001
            return str(erro)

    def um(self, sql):
        return self._valor(sql)


def _sql(banco, nome):
    with open(os.path.join(RAIZ, "supabase", "migrations", nome),
              encoding="utf-8") as f:
        banco.aplicar(f.read())


def casos(banco):
    fora = []

    def caso(nome, ok, detalhe=""):
        fora.append((nome, bool(ok), detalhe))

    # ── O ACERVO, ESCRITO COM O ESQUEMA ANTIGO ──────────────────────────
    banco.aplicar(
        "insert into public.collection_run (run_id, platform, actor, "
        "actor_version, mission, source_country, started_at, rule_version, "
        "capture_method, status) values ('IT-B5A','HTTP','ator','1','prova',"
        "'IT','2026-09-10T00:00:00Z','1','HTTP_GET','concluida') "
        "on conflict (run_id) do nothing;")
    for caminho, sha, bytes_ in ACERVO:
        banco.aplicar(
            "insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at, source_url) values "
            "('IT-B5A','%s','application/pdf',%d,'%s',"
            "'2026-09-10T00:00:00Z','https://x.it/%s');"
            % (caminho, bytes_, sha, caminho[-8:]))
    banco.aplicar(
        "insert into public.derived_artifact (raw_asset_id, parent_sha256, "
        "kind, producer, producer_version, parameters_hash, sha256, bytes, "
        "media_type, storage_path, derived_at) select id, sha256, "
        "'TEXT_EXTRACTION','texto-de-pdf','1','%s','%s',10,'text/plain',"
        "'IT/derivados/um.txt','2026-09-10T00:00:00Z' from public.raw_asset "
        "where storage_path = '%s';" % (HASH_PARAM, SHA_FILHO, ACERVO[0][0]))

    antes = banco._linhas(
        "select id, storage_path from public.raw_asset order by id",
        ("id", "storage_path"))
    derivado_antes = banco._linhas(
        "select id, raw_asset_id from public.derived_artifact order by id",
        ("id", "raw_asset_id"))

    # ── E AGORA A CIRURGIA, SOBRE DADO QUE JA ESTAVA JUNTO ──────────────
    _sql(banco, M025)

    # A · a casa do objeto existe
    caso("A_storage_object_existe",
         banco.um("select count(*) from information_schema.tables where "
                  "table_schema='public' and table_name='storage_object'") == "1")

    # B · RLS ligado, como em toda a casa desde a 006
    caso("B_RLS_ligado_no_storage_object",
         banco.um("select relrowsecurity from pg_class where "
                  "relname='storage_object'") == "t")

    # C · o endereco e a identidade
    caso("C_storage_path_e_unico_no_objeto",
         banco.um("select count(*) from pg_constraint c join pg_class t on "
                  "t.oid=c.conrelid where t.relname='storage_object' and "
                  "c.contype='u'") >= "1",
         "constraints unique = %s" % banco.um(
             "select count(*) from pg_constraint c join pg_class t on "
             "t.oid=c.conrelid where t.relname='storage_object' and "
             "c.contype='u'"))

    # D · e o sha NAO e. Medido, nao suposto.
    caso("D_sha256_NAO_e_unico_no_objeto",
         banco.um(
             "select count(*) from pg_indexes where tablename='storage_object' "
             "and indexdef ilike '%%unique%%' and indexdef ilike '%%sha256%%'"
         ) == "0")

    # E · a coluna da ligacao
    caso("E_raw_asset_tem_storage_object_id",
         banco.um("select count(*) from information_schema.columns where "
                  "table_name='raw_asset' and column_name='storage_object_id'")
         == "1")

    # F · e ela e chave estrangeira de verdade
    caso("F_FK_observacao_para_objeto",
         banco.um(
             "select count(*) from pg_constraint c join pg_class t on "
             "t.oid=c.conrelid join pg_class r on r.oid=c.confrelid "
             "where t.relname='raw_asset' and r.relname='storage_object' "
             "and c.contype='f'") == "1")

    # G · um objeto por endereco, nem mais nem menos
    objetos = banco.um("select count(*) from public.storage_object")
    enderecos = banco.um("select count(distinct storage_path) from public.raw_asset")
    caso("G_um_objeto_por_endereco", objetos == enderecos == str(len(ACERVO)),
         "objetos=%s enderecos=%s" % (objetos, enderecos))

    # H · e toda observacao preservada ficou ligada
    soltas = banco.um("select count(*) from public.raw_asset where preserved "
                      "and storage_object_id is null")
    caso("H_nenhuma_observacao_preservada_ficou_solta", soltas == "0",
         "soltas=%s" % soltas)

    # I · A PERGUNTA QUE MANDA. Os ids nao se mexeram.
    depois = banco._linhas(
        "select id, storage_path from public.raw_asset order by id",
        ("id", "storage_path"))
    caso("I_raw_asset_id_antes_e_igual_a_depois", antes == depois,
         "antes=%s depois=%s" % ([x["id"] for x in antes],
                                 [x["id"] for x in depois]))

    # J · e o filho continua a apontar para o mesmo pai
    derivado_depois = banco._linhas(
        "select id, raw_asset_id from public.derived_artifact order by id",
        ("id", "raw_asset_id"))
    caso("J_derivado_aponta_para_o_mesmo_pai",
         derivado_antes == derivado_depois and len(derivado_depois) == 1,
         "antes=%s depois=%s" % (derivado_antes, derivado_depois))

    # K · a chave composta continua a MORDER, e nao apenas a existir
    erro = banco.executar(
        "insert into public.derived_artifact (raw_asset_id, parent_sha256, "
        "kind, producer, producer_version, parameters_hash, sha256, bytes, "
        "media_type, storage_path, derived_at) values "
        "(%s,'%s','TEXT_EXTRACTION','x','1','%s','%s',1,'text/plain',"
        "'IT/derivados/mentira.txt','2026-09-10T00:00:00Z');"
        % (antes[0]["id"], "c" * 64, HASH_PARAM, "f" * 64))
    caso("K_FK_composta_derivado_continua_a_morder", bool(erro),
         "o banco recusou pai-por-id != pai-por-sha" if erro
         else "ACEITOU parentesco incoerente")

    # L · o check foi mesmo VALIDADO, e nao so criado
    caso("L_check_condicional_validado",
         banco.um("select convalidated from pg_constraint where "
                  "conname='preservado_aponta_para_a_copia'") == "t")

    # M · e ele recusa o que existe para recusar
    erro_m = banco.executar(
        "insert into public.raw_asset (run_id, storage_path, media_type, "
        "bytes, sha256, captured_at) values ('IT-B5A','IT/f/DOCUMENT/sem.pdf',"
        "'application/pdf',1,'%s','2026-09-10T00:00:00Z');" % SHA_UM)
    caso("M_preservado_sem_copia_e_recusado", bool(erro_m),
         "recusado" if erro_m else "ACEITOU observacao preservada sem copia")

    # N · dois objetos com o MESMO sha e enderecos diferentes convivem
    gemeos = banco.um(
        "select count(*) from public.storage_object where sha256 = '%s'"
        % SHA_GEMEO)
    caso("N_mesmo_sha_em_dois_objetos_e_permitido", gemeos == "2",
         "objetos com o sha gemeo = %s" % gemeos)

    # O · E O QUE FECHA A MISSAO: o writer canonico ainda escreve.
    art = {"COUNTRY": "IT", "SOURCE_SLUG": "fonte", "ARTIFACT_KIND": "DOCUMENT",
           "NAME": "novo.pdf", "SOURCE_NATIVE_ID": "n1",
           "SHA256": sha256(b"bytes novos"), "BYTES": len(b"bytes novos"),
           "MEDIA_TYPE": "application/pdf",
           "CAPTURED_AT": "2026-09-10T01:00:00Z",
           "SOURCE_URL": "https://x.it/novo"}
    corrida = {"RUN_ID": "IT-B5A-FORWARD", "PLATFORM": "HTTP", "ACTOR": "ator",
               "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT",
               "RULE_VERSION": "1", "CAPTURE_METHOD": "HTTP_GET",
               "STARTED_AT": "2026-09-10T01:00:00Z"}
    r = preservar(corrida, [art], ArmazemDeMentira(),
                  lambda o: b"bytes novos", memoria=banco,
                  terminou_em="2026-09-10T01:05:00Z")
    caminho_novo = caminho_do_objeto(art)
    ligada = banco.um(
        "select count(*) from public.raw_asset a join public.storage_object o "
        "on o.id = a.storage_object_id where a.storage_path = '%s'"
        % caminho_novo)
    caso("O_writer_forward_escreve_depois_da_fase_6",
         r["RUN_STATE"] == "COMPLETE" and ligada == "1"
         and len(r["RAW_OBSERVATIONS"]) == 1,
         "estado=%s ligada=%s observacoes=%d" % (
             r["RUN_STATE"], ligada, len(r["RAW_OBSERVATIONS"])))

    # ── E O QUE AINDA NAO ESTA CURADO, MEDIDO DE PROPOSITO ──────────────
    # A segunda corrida do mesmo conteudo AINDA conflita, porque
    # `unique (raw_asset.storage_path)` continua de pe. Isto NAO e um defeito
    # desta migration: e a fase 10, que nao foi autorizada. Medir aqui impede
    # que alguem leia a separacao como se fosse a cura.
    corrida_b = dict(corrida, RUN_ID="IT-B5A-FORWARD-B",
                     STARTED_AT="2026-09-11T01:00:00Z")
    r2 = preservar(corrida_b, [art], ArmazemDeMentira(),
                   lambda o: b"bytes novos", memoria=banco,
                   terminou_em="2026-09-11T01:05:00Z")
    caso("P_segunda_corrida_do_mesmo_conteudo_AINDA_conflita",
         r2["RUN_STATE"] == "PARTIAL" and not r2["RAW_OBSERVATIONS"],
         "estado=%s observacoes=%d — esperado, a cura e a fase 10"
         % (r2["RUN_STATE"], len(r2["RAW_OBSERVATIONS"])))

    # E a trava antiga continua onde estava. Retira-la e a fase 10.
    caso("Q_unique_do_storage_path_em_raw_asset_continua",
         banco.um("select count(*) from pg_indexes where "
                  "tablename='raw_asset' and indexdef ilike '%%unique%%' "
                  "and indexdef ilike '%%storage_path%%'") >= "1")
    return fora


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL", "")
    if not _pg._e_descartavel(url):
        print("NOT_RUN — sem BANCO_DESCARTAVEL_URL apontado a um banco "
              "descartavel local. Esta prova nunca corre contra producao.")
        return 2
    banco = Banco(url)
    for nome in MIGRACOES:
        _sql(banco, nome)
    print("migrations 001 e 022 aplicadas. Acervo escrito com o esquema ANTIGO.")
    print("ESCOPO: FOUNDATION_MAIS_022_MAIS_025\n")

    resultados = casos(banco)
    for nome, passou, detalhe in resultados:
        print("  %-4s %-52s %s" % ("PASS" if passou else "FAIL", nome, detalhe))
    reprovados = [n for n, p, _ in resultados if not p]
    print("\nOBJETO_E_OBSERVACAO_DB_TESTED=%s · %d caso(s)%s" % (
        "PASS" if not reprovados else "FAIL", len(resultados),
        "" if not reprovados else " · reprovou: " + ", ".join(reprovados)))
    print("NEW_RUN_SAME_CONTENT_RESOLVED=NO — e isso esta medido no caso P.")
    return 0 if not reprovados else 1


if __name__ == "__main__":
    sys.exit(main())
