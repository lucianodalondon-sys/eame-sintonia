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
    ArmazemDeMentira, NEW_RUN_SAME_STORAGE_PATH, SEM_IDENTIDADE_DE_FONTE,
    caminho_do_objeto, preservar, sha256)

MIGRACOES = ["001_fundacao_geografia_e_proveniencia.sql",
             "022_o_derivado_ganha_casa.sql"]
M025 = "025_o_objeto_ganha_casa.sql"
M026 = "026_a_observacao_ganha_identidade.sql"

# Os ids ANTES e DEPOIS da 026, medidos onde ela e aplicada e lidos onde a
# invariante e cobrada. Duas listas, e nao uma consulta repetida: repetir a
# consulta mediria o depois duas vezes e chamaria a isso um antes.
_ANTES_DA_026, _DEPOIS_DA_026 = [], []

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

    # ── E AQUI ENTRA A 026 ──────────────────────────────────────────────
    # O writer canonico passou a escrever a identidade da observacao, logo ele
    # NAO corre contra um esquema anterior a esta migration — e isso e correcto:
    # um writer que soubesse escrever nos dois esquemas teria de saber calar a
    # identidade, e calar identidade e o defeito que esta cirurgia fecha.
    _ANTES_DA_026.extend(banco._linhas(
        "select id, storage_path from public.raw_asset order by id",
        ("id", "storage_path")))
    _sql(banco, M026)
    _DEPOIS_DA_026.extend(banco._linhas(
        "select id, storage_path from public.raw_asset order by id",
        ("id", "storage_path")))

    # O · E O QUE FECHA A MISSAO: o writer canonico ainda escreve.
    art = {"COUNTRY": "IT", "SOURCE_SLUG": "fonte", "ARTIFACT_KIND": "DOCUMENT",
           "SOURCE_ID": "IT-T2-002", "DOCUMENT_ID": "ARPAV:Z07:2026-09-10",
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

    resultados = casos(banco) + casos_b5b(banco) + concorrencia(url)
    for nome, passou, detalhe in resultados:
        print("  %-4s %-52s %s" % ("PASS" if passou else "FAIL", nome, detalhe))
    reprovados = [n for n, p, _ in resultados if not p]
    print("\nOBJETO_E_OBSERVACAO_DB_TESTED=%s · %d caso(s)%s" % (
        "PASS" if not reprovados else "FAIL", len(resultados),
        "" if not reprovados else " · reprovou: " + ", ".join(reprovados)))
    print("NEW_RUN_SAME_CONTENT_RESOLVED=NO — medido no caso P e outra vez no B5B.")
    print("READY_FOR_PHASE_10=NO — a fase 10 nao entrou, e a trava antiga continua.")
    return 0 if not reprovados else 1




# ═════════════════════════════════════════════════════════════════════════
# B5B · FASES 7, 8 E 9 — A OBSERVAÇÃO GANHA IDENTIDADE (migration 026)
# ═════════════════════════════════════════════════════════════════════════
# A bateria final da secção **T.7** do plano, com os 27 casos. Os casos
# marcados SUPERSEDED nas secções R e S NÃO estão aqui: dois deles mandavam
# ACEITAR `CONTENT_DERIVED`, que a S.4 revogou.
#
#     DUAS ORDENS EXECUTÁVEIS NO MESMO SÍTIO SÃO ZERO ORDENS.

SENTINELAS_MEDIDAS = ("NAO SEI", "NAO_SEI", "NÃO SEI", "NAO_SE_APLICA",
                      "UNKNOWN", "NOT_KNOWN")

# Uma linha mínima que isola a identidade de tudo o resto: `preserved = false`
# com motivo dispensa a cópia, logo nenhum caso abaixo depende do objeto. Quem
# prova a ligação observação↔cópia são os casos D e E, à parte.
_LINHA = ("insert into public.raw_asset (run_id, storage_path, media_type, "
          "bytes, sha256, captured_at, preserved, not_preserved_reason%s) "
          "values ('IT-B5A','%s','application/pdf',1,'%s',"
          "'2026-09-11T00:00:00Z', false, 'linha de prova'%s);")


def _tentar(banco, caminho, sha, colunas="", valores=""):
    """Escreve uma observação e devolve a recusa do banco, ou None."""
    return banco.executar(_LINHA % (colunas, caminho, sha, valores))


def _ident(estado=None, fonte=None, chave=None, base=None, omitir_estado=False):
    """As colunas de identidade, na forma que o `insert` pede."""
    campos, valores = [], []
    if not omitir_estado:
        campos.append("identity_state")
        valores.append("null" if estado is None else "'%s'" % estado)
    for nome, v in (("source_id", fonte), ("document_key", chave),
                    ("document_key_basis", base)):
        if v is not None:
            campos.append(nome)
            valores.append("null" if v == "NULL" else "'%s'" % v)
    if not campos:
        return "", ""
    return ", " + ", ".join(campos), ", " + ", ".join(valores)


def casos_b5b(banco):
    fora = []
    n = [0]

    def caso(nome, ok, detalhe=""):
        fora.append((nome, bool(ok), detalhe))

    def endereco():
        n[0] += 1
        return "IT/b5b/DOCUMENT/caso-%02d.pdf" % n[0]

    def recusa(nome, **kw):
        cols, vals = _ident(**kw)
        erro = _tentar(banco, endereco(), "c" * 64, cols, vals)
        caso(nome, erro is not None,
             "" if erro else "ACEITE — e devia ter sido recusado")

    def aceita(nome, sha="c" * 64, **kw):
        cols, vals = _ident(**kw)
        erro = _tentar(banco, endereco(), sha, cols, vals)
        caso(nome, erro is None, (erro or "")[:90])

    # A 026 ja foi aplicada dentro de `casos()`, onde o writer precisa dela.
    antes, depois = _ANTES_DA_026, _DEPOIS_DA_026

    # ── A · OS IDS HISTORICOS SAO OS MESMOS, COMO CONJUNTO ──────────────
    caso("B5B_A_ids_historicos_preservados_exactamente",
         [x["id"] for x in antes] == [x["id"] for x in depois]
         and [x["storage_path"] for x in antes]
             == [x["storage_path"] for x in depois],
         "antes=%s depois=%s" % ([x["id"] for x in antes],
                                 [x["id"] for x in depois]))

    caso("B5B_legado_classificado_e_sem_identidade_inventada",
         banco.um("select count(*) from public.raw_asset where "
                  "identity_state = 'LEGACY_PRE_IDEMPOTENCY'") == str(len(antes))
         and banco.um(
             "select count(*) from public.raw_asset where "
             "identity_state = 'LEGACY_PRE_IDEMPOTENCY' and (source_id is not "
             "null or document_key is not null or document_key_basis is not "
             "null)") == "0",
         "legado=%s esperado=%d" % (
             banco.um("select count(*) from public.raw_asset where "
                      "identity_state = 'LEGACY_PRE_IDEMPOTENCY'"),
             len(antes)))

    # ── B · O ESTADO E OBRIGATORIO E NAO TEM DEFAULT ────────────────────
    caso("B5B_B_identity_state_NOT_NULL_e_SEM_DEFAULT",
         banco.um("select attnotnull::text from pg_attribute where "
                  "attrelid='public.raw_asset'::regclass and "
                  "attname='identity_state'") == "true"
         and banco.um(
             "select count(*) from pg_attrdef d join pg_attribute a on "
             "a.attrelid=d.adrelid and a.attnum=d.adnum where "
             "d.adrelid='public.raw_asset'::regclass and "
             "a.attname='identity_state'") == "0")

    # ── 1-3 · O CORTE DO LEGADO ─────────────────────────────────────────
    recusa("T7_01_novo_INSERT_declarando_LEGACY_e_recusado",
           estado="LEGACY_PRE_IDEMPOTENCY")
    aceita("T7_02_FORWARD_IDENTIFIED_completo_entra", sha="1" * 64,
           estado="FORWARD_IDENTIFIED", fonte="IT-T2-002",
           chave="ARPAV:Z07:2026-09-11", base="SOURCE_DOCUMENT_ID")
    aceita("T7_03_FORWARD_IDENTITY_UNPROVEN_com_fonte_real_entra", sha="2" * 64,
           estado="FORWARD_IDENTITY_UNPROVEN", fonte="IT-T2-002")

    # ── 4-5 · O ESTADO NAO PODE FALTAR ──────────────────────────────────
    recusa("T7_04_identity_state_NULL_e_recusado", estado=None)
    recusa("T7_05_writer_que_OMITE_a_coluna_e_recusado", omitir_estado=True)

    # ── 6-17 · FONTE REAL NOS DOIS ESTADOS FORWARD ──────────────────────
    for i, sent in enumerate(SENTINELAS_MEDIDAS, start=6):
        recusa("T7_%02d_IDENTIFIED_com_fonte_%s" % (i, sent.replace(" ", "_")),
               estado="FORWARD_IDENTIFIED", fonte=sent, chave="DOC:X",
               base="SOURCE_DOCUMENT_ID")
    for i, sent in enumerate(SENTINELAS_MEDIDAS, start=12):
        recusa("T7_%02d_UNPROVEN_com_fonte_%s" % (i, sent.replace(" ", "_")),
               estado="FORWARD_IDENTITY_UNPROVEN", fonte=sent)
    recusa("T7_18_UNPROVEN_com_fonte_unknown_em_minusculas",
           estado="FORWARD_IDENTITY_UNPROVEN", fonte="unknown")
    recusa("T7_19_UNPROVEN_com_fonte_em_branco",
           estado="FORWARD_IDENTITY_UNPROVEN", fonte="   ")
    recusa("T7_20_UNPROVEN_com_fonte_NULL",
           estado="FORWARD_IDENTITY_UNPROVEN", fonte="NULL")

    # ── 21-22 · CONTENT_DERIVED FOI REVOGADO ────────────────────────────
    # E a recusa NAO olha para a chave: nao e «CONTENT_DERIVED com a chave
    # errada», e o valor que nao existe.
    recusa("T7_21_CONTENT_DERIVED_com_sha256_inteiro_e_recusado",
           estado="FORWARD_IDENTIFIED", fonte="IT-T2-002",
           chave="c" * 64, base="CONTENT_DERIVED")
    recusa("T7_22_CONTENT_DERIVED_com_sha16_e_recusado",
           estado="FORWARD_IDENTIFIED", fonte="IT-T2-002",
           chave="c" * 16, base="CONTENT_DERIVED")

    # ── 23-26 · COERENCIA DOS DOIS ESTADOS FORWARD ──────────────────────
    recusa("T7_23_IDENTIFIED_sem_document_key",
           estado="FORWARD_IDENTIFIED", fonte="IT-T2-002")
    recusa("T7_24_IDENTIFIED_sem_document_key_basis",
           estado="FORWARD_IDENTIFIED", fonte="IT-T2-002", chave="DOC:X")
    recusa("T7_25_UNPROVEN_a_fingir_chave_documental",
           estado="FORWARD_IDENTITY_UNPROVEN", fonte="IT-T2-002",
           chave="DOC:X", base="SOURCE_DOCUMENT_ID")
    recusa("T7_26_estado_inventado_e_recusado",
           estado="FORWARD_QUALQUER_COISA", fonte="IT-T2-002")

    # ── 27 · NENHUMA LINHA FICOU SEM ESTADO ─────────────────────────────
    caso("T7_27_zero_linhas_sem_estado_depois_da_fase_8",
         banco.um("select count(*) from public.raw_asset "
                  "where identity_state is null") == "0")

    return fora + _casos_de_esquema(banco) + _casos_do_writer(banco)


def _casos_de_esquema(banco):
    """As provas do §28 que se leem do CATÁLOGO, não de uma escrita."""
    fora = []

    def caso(nome, ok, detalhe=""):
        fora.append((nome, bool(ok), detalhe))

    # ── C · o vocabulário da base da chave tem UM valor ─────────────────
    caso("B5B_C_basis_so_aceita_NULL_ou_SOURCE_DOCUMENT_ID",
         banco.um("select count(*) from pg_constraint where "
                  "conrelid='public.raw_asset'::regclass and "
                  "conname='base_da_chave_tem_vocabulario' and convalidated")
         == "1")

    # ── D · a observação e a cópia falam do MESMO conteúdo ──────────────
    # A `025` deixava `raw_asset.sha256 = H1` apontar para um objeto de `H2`:
    # a chave estrangeira simples passava, e a linha dizia duas coisas.
    banco.aplicar(
        "insert into public.storage_object (storage_path, media_type, bytes, "
        "sha256) values ('IT/b5b/objeto-h1.pdf','application/pdf',1,'%s') "
        "on conflict (storage_path) do nothing;" % ("7" * 64))
    erro = banco.executar(
        "insert into public.raw_asset (run_id, storage_path, media_type, "
        "bytes, sha256, captured_at, storage_object_id, identity_state, "
        "source_id, document_key, document_key_basis) select 'IT-B5A',"
        "'IT/b5b/observacao-h2.pdf','application/pdf',1,'%s',"
        "'2026-09-11T00:00:00Z', o.id,'FORWARD_IDENTIFIED','IT-T2-002',"
        "'DOC:H2','SOURCE_DOCUMENT_ID' from public.storage_object o "
        "where o.storage_path = 'IT/b5b/objeto-h1.pdf';" % ("8" * 64))
    caso("B5B_D_observacao_H1_a_apontar_para_objeto_H2_e_recusada",
         erro is not None, "" if erro else "ACEITE — e nao devia")

    # ── E · e dois objetos com os MESMOS bytes continuam legais ─────────
    # A trava de cima NÃO tornou `sha256` único no objeto. Se tornasse, o caso
    # ADAMA — o mesmo PDF publicado em `media/731` e `media/6321` — passaria a
    # ser ilegal, e ele é um facto medido.
    e1 = banco.executar(
        "insert into public.storage_object (storage_path, media_type, bytes, "
        "sha256) values ('IT/b5b/gemeo-a.pdf','application/pdf',1,'%s');"
        % ("9" * 64))
    e2 = banco.executar(
        "insert into public.storage_object (storage_path, media_type, bytes, "
        "sha256) values ('IT/b5b/gemeo-b.pdf','application/pdf',1,'%s');"
        % ("9" * 64))
    caso("B5B_E_dois_objetos_com_o_mesmo_sha_continuam_legais",
         e1 is None and e2 is None, "%s %s" % (e1 or "ok", e2 or "ok"))

    # ── F · o índice parcial existe E está válido ───────────────────────
    caso("B5B_F_indice_parcial_da_identidade_existe_e_e_valido",
         banco.um("select count(*) from pg_index i join pg_class c on "
                  "c.oid=i.indexrelid where c.relname="
                  "'raw_identidade_forward_idx' and i.indisvalid and "
                  "i.indisunique and i.indpred is not null") == "1")

    # ── §29 · E ELE FUNCIONA POR SI, SEM O `storage_path` A AJUDAR ──────
    # A prova tem de separar as duas travas. Aqui a MESMA chave de
    # idempotência é escrita num ENDEREÇO DIFERENTE: se entrasse, o índice não
    # estaria a proteger nada e quem estaria a segurar era o endereço.
    banco.aplicar(_LINHA % (
        ", identity_state, source_id, document_key, document_key_basis",
        "IT/b5b/chave-primeira.pdf", "a" * 63 + "1",
        ", 'FORWARD_IDENTIFIED','IT-T2-002','DOC:CHAVE','SOURCE_DOCUMENT_ID'"))
    erro = banco.executar(_LINHA % (
        ", identity_state, source_id, document_key, document_key_basis",
        "IT/b5b/chave-segunda-ENDERECO-DIFERENTE.pdf", "a" * 63 + "1",
        ", 'FORWARD_IDENTIFIED','IT-T2-002','DOC:CHAVE','SOURCE_DOCUMENT_ID'"))
    caso("B5B_IDEMPOTENCY_UNIQUE_INDEX_WORKS",
         erro is not None and "raw_identidade_forward_idx" in (erro or ""),
         (erro or "ACEITE — o indice nao protegeu nada")[:90])

    # E o mesmo par (fonte, documento, sha) NOUTRA corrida entra: `run_id` faz
    # parte da chave, e corrida nova é observação nova.
    banco.aplicar(
        "insert into public.collection_run (run_id, platform, started_at, "
        "rule_version) values ('IT-B5A-2','HTTP','2026-09-12T00:00:00Z','1') "
        "on conflict (run_id) do nothing;")
    erro = banco.executar((_LINHA % (
        ", identity_state, source_id, document_key, document_key_basis",
        "IT/b5b/chave-outra-corrida.pdf", "a" * 63 + "1",
        ", 'FORWARD_IDENTIFIED','IT-T2-002','DOC:CHAVE','SOURCE_DOCUMENT_ID'"
    )).replace("'IT-B5A'", "'IT-B5A-2'", 1))
    caso("B5B_a_mesma_chave_noutra_corrida_e_observacao_NOVA",
         erro is None, (erro or "")[:90])

    # ── K · a trava física antiga continua onde estava ──────────────────
    caso("B5B_K_unique_do_storage_path_continua_de_pe",
         banco.um("select count(*) from pg_indexes where "
                  "tablename='raw_asset' and indexdef ilike '%%unique%%' "
                  "and indexdef ilike '%%storage_path%%'") >= "1")

    # ── O · a precondição da sequência, lida do catálogo ────────────────
    proximo = banco.um(
        "select (case when is_called then last_value + "
        "(select seqincrement from pg_sequence where seqrelid = "
        "'public.raw_asset_id_seq'::regclass) else last_value end)::text "
        "from public.raw_asset_id_seq")
    corte = banco.um("select substring(pg_get_constraintdef(oid) from "
                     "'id <= ([0-9]+)') from pg_constraint where "
                     "conname='legado_e_anterior_ao_corte'")
    caso("B5B_O_proximo_id_natural_e_maior_que_o_corte",
         int(proximo) > int(corte),
         "proximo=%s corte=%s" % (proximo, corte))

    return fora


def _casos_do_writer(banco):
    """O writer canónico usa a identidade nova — e o retry reencontra."""
    fora = []

    def caso(nome, ok, detalhe=""):
        fora.append((nome, bool(ok), detalhe))

    corrida = {"RUN_ID": "IT-B5B-W", "PLATFORM": "HTTP", "ACTOR": "prova",
               "ACTOR_VERSION": "1", "MISSION": "B5B", "SOURCE_COUNTRY": "IT",
               "STARTED_AT": "2026-09-11T02:00:00Z", "RULE_VERSION": "1",
               "CAPTURE_METHOD": "HTTP_GET"}
    dados = b"bytes do b5b"
    art = {"COUNTRY": "IT", "SOURCE_SLUG": "it-t2-002",
           "SOURCE_ID": "IT-T2-002", "DOCUMENT_ID": "ARPAV:Z07:2026-09-11",
           "ARTIFACT_KIND": "DOCUMENT", "NAME": "b5b.pdf",
           "SOURCE_NATIVE_ID": "n9", "SHA256": sha256(dados),
           "BYTES": len(dados), "MEDIA_TYPE": "application/pdf",
           "CAPTURED_AT": "2026-09-11T02:00:00Z",
           "SOURCE_URL": "https://x.it/b5b"}
    armazem = ArmazemDeMentira()
    r = preservar(corrida, [art], armazem, lambda o: dados, memoria=banco,
                  terminou_em="2026-09-11T02:05:00Z")
    caminho = caminho_do_objeto(art)
    linha = banco.objeto_em(caminho) or {}

    caso("B5B_writer_escreve_FORWARD_IDENTIFIED",
         r["RUN_STATE"] == "COMPLETE"
         and linha.get("identity_state") == "FORWARD_IDENTIFIED"
         and linha.get("document_key_basis") == "SOURCE_DOCUMENT_ID",
         "estado=%s identidade=%s" % (r["RUN_STATE"],
                                      linha.get("identity_state")))

    # ── L · O SOURCE_ID CANONICO SOBREVIVEU, E NAO E O SLUG ─────────────
    # O endereço leva o slug — `it-t2-002` — e a coluna leva o código. Se
    # alguém, um dia, derivar um do outro, estes dois valores passam a ser
    # iguais e este caso reprova.
    caso("B5B_L_source_id_e_o_codigo_da_Collection_e_nao_o_slug",
         linha.get("source_id") == "IT-T2-002"
         and "it-t2-002" in caminho and linha.get("source_id") not in caminho,
         "source_id=%s caminho=%s" % (linha.get("source_id"), caminho))

    # ── M · A CHAVE NAO CAIU PARA O HASH ────────────────────────────────
    caso("B5B_M_document_key_e_o_DOCUMENT_ID_e_nunca_o_sha",
         linha.get("document_key") == "ARPAV:Z07:2026-09-11"
         and linha.get("document_key") != art["SHA256"],
         "document_key=%s" % linha.get("document_key"))

    # ── G · RETRY DA MESMA CORRIDA — MESMA OBSERVACAO, MESMO ID ─────────
    id_primeiro = r["RAW_OBSERVATIONS"][0]["RAW_OBSERVATION_ID"] \
        if r["RAW_OBSERVATIONS"] else None
    r2 = preservar(corrida, [art], armazem, lambda o: dados, memoria=banco,
                   terminou_em="2026-09-11T02:06:00Z")
    caso("B5B_G_retry_da_mesma_corrida_e_REUSED_com_o_mesmo_id",
         r2["JA_EXISTIA_NO_BANCO"]["REUSED_METADATA"] == 1
         and not r2["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"]
         and r2["RAW_OBSERVATIONS"]
         and r2["RAW_OBSERVATIONS"][0]["RAW_OBSERVATION_ID"] == id_primeiro,
         "reused=%s id=%s" % (r2["JA_EXISTIA_NO_BANCO"]["REUSED_METADATA"],
                              id_primeiro))

    # ── H · OUTRO CAPTURED_AT NO RETRY NAO E CONFLITO ───────────────────
    # `captured_at` é a hora em que ESTA máquina recebeu. Duas tentativas da
    # mesma corrida recebem em horas diferentes — e continuam a ser a mesma
    # observação. Antes da 026 isto dava METADATA_CONFLICT.
    r3 = preservar(corrida, [dict(art, CAPTURED_AT="2026-09-11T02:30:00Z")],
                   armazem, lambda o: dados, memoria=banco,
                   terminou_em="2026-09-11T02:35:00Z")
    caso("B5B_H_retry_com_outro_CAPTURED_AT_continua_REUSED",
         r3["JA_EXISTIA_NO_BANCO"]["REUSED_METADATA"] == 1
         and not r3["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"],
         "conflitos=%d" % len(r3["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"]))

    # ── I · E OUTRA SOURCE_URL TAMBEM NAO ───────────────────────────────
    # Um espelho, um redirecionamento, um parâmetro que a fonte acrescentou. A
    # COL-LAW-206 já dizia que a URL não é identidade; agora o writer concorda.
    r4 = preservar(corrida, [dict(art, SOURCE_URL="https://espelho.it/b5b")],
                   armazem, lambda o: dados, memoria=banco,
                   terminou_em="2026-09-11T02:40:00Z")
    caso("B5B_I_retry_com_outra_SOURCE_URL_continua_REUSED",
         r4["JA_EXISTIA_NO_BANCO"]["REUSED_METADATA"] == 1
         and not r4["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"],
         "conflitos=%d" % len(r4["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"]))

    # ── J · CORRIDA NOVA SOBRE O MESMO OBJETO — AINDA BLOQUEADA ─────────
    # E com NOME PRÓPRIO. Não é «duas verdades no mesmo endereço»: é a fase 10,
    # que não foi autorizada. Chamar-lhe outra coisa esconderia a fase.
    r5 = preservar(dict(corrida, RUN_ID="IT-B5B-W2",
                        STARTED_AT="2026-09-12T02:00:00Z"),
                   [art], armazem, lambda o: dados, memoria=banco,
                   terminou_em="2026-09-12T02:05:00Z")
    caso("B5B_J_corrida_nova_sobre_o_mesmo_objeto_continua_bloqueada",
         r5["RUN_STATE"] == "PARTIAL"
         and r5["PENDENCIA"] == NEW_RUN_SAME_STORAGE_PATH
         and not r5["RAW_OBSERVATIONS"],
         "estado=%s pendencia=%s" % (r5["RUN_STATE"], r5["PENDENCIA"]))

    # ── SEM FONTE REAL O WRITER RECUSA, E NAO INVENTA NENHUMA ───────────
    r6 = preservar(dict(corrida, RUN_ID="IT-B5B-W3",
                        STARTED_AT="2026-09-13T02:00:00Z"),
                   [dict(art, SOURCE_ID="NAO SEI", NAME="sem-fonte.pdf")],
                   armazem, lambda o: dados, memoria=banco,
                   terminou_em="2026-09-13T02:05:00Z")
    caso("B5B_sem_fonte_real_o_writer_recusa_e_nao_inventa",
         r6["PENDENCIA"] == SEM_IDENTIDADE_DE_FONTE
         and r6["RUN_STATE"] == "PARTIAL"
         and len(r6["RECUSADOS_SEM_IDENTIDADE"]) == 1,
         "pendencia=%s recusados=%d" % (r6["PENDENCIA"],
                                        len(r6["RECUSADOS_SEM_IDENTIDADE"])))

    # ── FONTE SIM, DOCUMENTO NAO — E ISSO TEM ESTADO PROPRIO ────────────
    dados_u = b"bytes sem identidade documental"
    art_u = dict(art, SHA256=sha256(dados_u), BYTES=len(dados_u),
                 NAME="sem-documento.pdf", SOURCE_NATIVE_ID="n10")
    art_u.pop("DOCUMENT_ID")
    r7 = preservar(dict(corrida, RUN_ID="IT-B5B-U",
                        STARTED_AT="2026-09-14T02:00:00Z"),
                   [art_u], armazem, lambda o: dados_u, memoria=banco,
                   terminou_em="2026-09-14T02:05:00Z")
    linha_u = banco.objeto_em(caminho_do_objeto(art_u)) or {}
    caso("B5B_sem_DOCUMENT_ID_entra_como_UNPROVEN_e_a_chave_fica_NULL",
         r7["RUN_STATE"] == "COMPLETE"
         and linha_u.get("identity_state") == "FORWARD_IDENTITY_UNPROVEN"
         and linha_u.get("document_key") is None
         and linha_u.get("document_key_basis") is None,
         "estado=%s chave=%r" % (linha_u.get("identity_state"),
                                 linha_u.get("document_key")))

    # ── N · O WRITER NAO SABE SEQUER NOMEAR O LEGADO ────────────────────
    fonte_do_writer = open(os.path.join(RAIZ, "guarda", "preservar_coleta.py"),
                           encoding="utf-8").read()
    caso("B5B_N_o_writer_nunca_emite_LEGACY_pelo_caminho_natural",
         '"LEGACY_PRE_IDEMPOTENCY"' not in fonte_do_writer
         and banco.um("select count(*) from public.raw_asset where "
                      "identity_state = 'LEGACY_PRE_IDEMPOTENCY' and "
                      "run_id like 'IT-B5B%%'") == "0")
    return fora


# ═════════════════════════════════════════════════════════════════════════
# OS DOIS CENÁRIOS DE CONCORRÊNCIA DA FASE 8 — CONTRA A MIGRATION REAL
# ═════════════════════════════════════════════════════════════════════════
# A fase 8 classifica o legado e congela um corte. Se houver UMA janela entre
# classificar e `SET NOT NULL`, uma linha nova entra sem estado e o corte passa
# a mentir. Aqui a janela é atacada dos dois lados, com a `026` tal como ela
# está no ficheiro — não com uma encenação parecida.
import subprocess  # noqa: E402
import time  # noqa: E402


def _reset(banco, url):
    """Deita fora o esquema e reconstrói o acervo ANTES da 026.

    A fase 8 corre UMA vez por banco — o corte não se recalcula, e é isso que
    a torna confiável. Logo, para dois cenários são precisos dois estados
    iniciais, e este é o único banco descartável que esta prova possui.
    """
    banco.aplicar("drop schema public cascade; create schema public;")
    for nome in MIGRACOES:
        _sql(banco, nome)
    banco.aplicar(
        "insert into public.collection_run (run_id, platform, actor, "
        "actor_version, mission, source_country, started_at, rule_version, "
        "capture_method, status) values ('IT-CONC','HTTP','ator','1','prova',"
        "'IT','2026-09-10T00:00:00Z','1','HTTP_GET','concluida');")
    for i in (1, 2, 3):
        banco.aplicar(
            "insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at) values ('IT-CONC','IT/conc/%d.pdf',"
            "'application/pdf',%d,'%s','2026-09-10T00:00:00Z');"
            % (i, i, "a" * 63 + str(i)))
    _sql(banco, M025)

    # ── O LIVRO-RAZÃO FICA COERENTE COM O QUE JÁ FOI APLICADO ───────────
    # Sem isto, o aplicador do cenário B veria 001..025 como pendentes e a
    # espera pelo lock aconteceria na PRIMEIRA migration da fila — provaria
    # que ele espera, mas não que espera NA JANELA DA 026, que é a pergunta.
    # Anotar aqui o que já foi aplicado à mão é o mesmo bootstrap que o
    # aplicador faz num banco que já tem schema e ainda não tem livro.
    import hashlib
    banco.aplicar(
        "create table if not exists public.schema_migracao ("
        " versao text primary key,"
        " aplicada_em timestamptz not null default now(),"
        " resultado text not null,"
        " sha256 text not null);")
    migracoes = os.path.join(RAIZ, "supabase", "migrations")
    for nome in sorted(os.listdir(migracoes)):
        if not nome.endswith(".sql") or nome.startswith(("008", "026")):
            continue
        with open(os.path.join(migracoes, nome), "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        banco.aplicar(
            "insert into public.schema_migracao (versao, resultado, sha256) "
            "values ('%s','JA_EXISTIA','%s') on conflict (versao) do nothing;"
            % (nome[:3], sha))


def _sessao(url, script):
    """Uma sessão `psql` que fica de pé enquanto o script dela corre."""
    return subprocess.Popen(
        ["psql", url, "-X", "-q", "-v", "ON_ERROR_STOP=1", "-f", "-"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True), script


def _correr_sessao(par):
    proc, script = par
    proc.stdin.write(script)
    proc.stdin.close()
    return proc


def _esperar(proc):
    """A saída e o código, sem `communicate()` — o `stdin` já foi fechado."""
    saida = proc.stdout.read()
    proc.wait()
    return saida


def concorrencia(url):
    fora = []

    def caso(nome, ok, detalhe=""):
        fora.append((nome, bool(ok), detalhe))

    banco = Banco(url)
    migration = open(os.path.join(RAIZ, "supabase", "migrations", M026),
                     encoding="utf-8").read()

    # ⚠️ O CENÁRIO A SEGURA A TRANSAÇÃO À MÃO, E ISSO É FIEL — NÃO UM ATALHO.
    # Desde que `motor/cadeia_canonica.sh` passou a correr cada ficheiro com
    # `--single-transaction`, a fronteira da transação é EXATAMENTE esta: o
    # ficheiro inteiro, do primeiro `alter` ao último `create index`. O `begin`
    # explícito aqui reproduz essa fronteira e acrescenta um `pg_sleep` para a
    # janela ser observável — o aplicador real fecha depressa demais para se
    # ver alguém a esperar. O cenário B corre o aplicador de verdade, onde a
    # espera é do lado dele e não precisa de encenação nenhuma.

    # ── CENÁRIO A · a transação velha que ainda não inseriu ─────────────
    # A migration segura o lock; o INSERT chega no meio. Ele NÃO pode passar à
    # frente, e quando passar não pode nascer dentro do corte.
    _reset(banco, url)
    m = _correr_sessao(_sessao(
        url, "begin;\n" + migration + "\nselect pg_sleep(3);\ncommit;\n"))
    w = _correr_sessao(_sessao(url, """
begin;
select pg_sleep(1);
insert into public.raw_asset (run_id, storage_path, media_type, bytes, sha256,
  captured_at, preserved, not_preserved_reason,
  identity_state, source_id, document_key, document_key_basis)
values ('IT-CONC','IT/conc/depois-do-lock.pdf','application/pdf',1,
  '%s','2026-09-11T00:00:00Z', false, 'prova',
  'FORWARD_IDENTIFIED','IT-T2-002','DOC:A','SOURCE_DOCUMENT_ID');
commit;
""" % ("b" * 64)))
    time.sleep(2)
    esperou = Banco(url).um(
        "select count(*) from pg_stat_activity where wait_event_type='Lock' "
        "and query ilike '%%insert into public.raw_asset%%'")
    saida_m, saida_w = _esperar(m), _esperar(w)
    nova = banco._linhas(
        "select id, identity_state from public.raw_asset where storage_path = "
        "'IT/conc/depois-do-lock.pdf'", ("id", "identity_state"))
    corte = banco.um("select substring(pg_get_constraintdef(oid) from "
                     "'id <= ([0-9]+)') from pg_constraint where "
                     "conname='legado_e_anterior_ao_corte'")
    caso("B5B_P_CENARIO_A_o_insert_espera_pela_migration",
         esperou == "1" and m.returncode == 0 and w.returncode == 0,
         "esperando=%s m=%s w=%s %s" % (esperou, m.returncode, w.returncode,
                                        (saida_m + saida_w)[-70:]))
    caso("B5B_P_CENARIO_A_o_id_novo_nasce_FORA_do_corte",
         len(nova) == 1 and int(nova[0]["id"]) > int(corte)
         and nova[0]["identity_state"] == "FORWARD_IDENTIFIED",
         "linha=%s corte=%s" % (nova, corte))

    # E o writer ANTIGO — o que não conhece a coluna — é RECUSADO. Não vira
    # legado por acidente: não entra de todo.
    erro = banco.executar(
        "insert into public.raw_asset (run_id, storage_path, media_type, "
        "bytes, sha256, captured_at, preserved, not_preserved_reason) values "
        "('IT-CONC','IT/conc/writer-antigo.pdf','application/pdf',1,'%s',"
        "'2026-09-11T00:00:00Z', false, 'prova');" % ("d" * 64))
    caso("B5B_P_CENARIO_A_o_writer_antigo_e_recusado_e_nao_vira_legado",
         erro is not None, "" if erro else "ACEITE — e nao devia")

    # ── CENÁRIO B · a transação que já inseriu e ainda não commitou ─────
    # A migration tem de ESPERAR por ela e, depois, VÊ-LA. Se não visse, a
    # linha ficava sem estado — e o `SET NOT NULL` reprovava a migration
    # inteira, que é o comportamento certo mas não é este cenário.
    _reset(banco, url)
    w2 = _correr_sessao(_sessao(url, """
begin;
insert into public.raw_asset (run_id, storage_path, media_type, bytes, sha256,
  captured_at, preserved, not_preserved_reason)
values ('IT-CONC','IT/conc/antes-do-commit.pdf',
  'application/pdf',1,'%s','2026-09-11T00:00:00Z', false, 'prova');
select pg_sleep(3);
commit;
""" % ("c" * 64))
    )
    # O APLICADOR DE VERDADE, e não uma cópia dele. Se a ordem, a transação ou
    # o livro-razão mudarem em `motor/cadeia_canonica.sh`, este caso muda com
    # eles — que é o ponto de correr o dono em vez de o imitar.
    m2 = subprocess.Popen(
        ["bash", os.path.join(RAIZ, "motor", "cadeia_canonica.sh"),
         "migrations", url],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # ⚠️ A MIGRATION ESPERA MAIS CEDO DO QUE SE ESPERAVA, e isso e medido:
    # ela nao chega ao `lock table` da fase 8 — o primeiro `alter table ... add
    # column` da fase 7 JA pede ACCESS EXCLUSIVE e ja bate na transacao aberta.
    # O `lock table` explicito continua a valer: e ele que garante que a janela
    # da fase 8 nao se abre a meio. Aqui pergunta-se o que interessa — «a
    # migration ficou a espera?» — e nao em que linha exacta ela parou.
    time.sleep(2)
    observador = Banco(url)
    migration_esperou = observador.um(
        "select count(*) from pg_stat_activity where wait_event_type='Lock' "
        "and query not ilike '%%pg_stat_activity%%'")
    onde_parou = observador.um(
        "select left(regexp_replace(query, '\\s+', ' ', 'g'), 60) from "
        "pg_stat_activity where wait_event_type='Lock' and query not ilike "
        "'%%pg_stat_activity%%' limit 1")
    saida_w2 = _esperar(w2)
    saida_m2 = m2.stdout.read()
    m2.wait()
    linha = banco._linhas(
        "select id, identity_state from public.raw_asset where storage_path = "
        "'IT/conc/antes-do-commit.pdf'", ("id", "identity_state"))
    caso("B5B_P_CENARIO_B_a_migration_espera_pela_transacao_aberta",
         migration_esperou == "1" and m2.returncode == 0 and w2.returncode == 0,
         "esperando=%s em: %s" % (migration_esperou, onde_parou))
    caso("B5B_P_CENARIO_B_a_linha_preexistente_e_vista_e_classificada",
         len(linha) == 1
         and linha[0]["identity_state"] == "LEGACY_PRE_IDEMPOTENCY"
         and banco.um("select count(*) from public.raw_asset "
                      "where identity_state is null") == "0",
         "linha=%s" % linha)
    return fora


if __name__ == "__main__":
    sys.exit(main())
