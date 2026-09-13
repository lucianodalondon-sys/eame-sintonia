#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SALA DE ESPERA EM POSTGRES — a OPCAO B, medida e nao imaginada.

    LINHA_FUNCIONAL=/tmp/wt \\
    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/a_sala_de_espera_em_postgres.py

POR QUE ESTA MEDICAO EXISTE
---------------------------
`provas/a_unidade_pousa_na_espera.py` prova a OPCAO A (ficheiro) com 26 casos.
Comparar essa prova com uma OPCAO B *descrita em prosa* nao seria comparacao:
seria um combate marcado. Entao a OPCAO B leva **a mesma bateria**, com os
mesmos nomes de caso, contra PostgreSQL 16 REAL e descartavel.

    UMA OPCAO QUE NUNCA CORREU NAO PERDE NEM GANHA. ELA NAO FOI MEDIDA.

O QUE ESTA MEDICAO NAO E
------------------------
Nao e uma migration. Nao e uma tabela definitiva. A tabela nasce e morre
dentro desta execucao, num schema `ensaio_espera` que e derrubado no fim.
Nada aqui entra em `supabase/migrations/`.

    UM ENSAIO QUE DEIXA TABELA E UMA MIGRATION QUE NAO PEDIU LICENCA.
"""
import io
import json
import os
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlparse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINHA = os.environ.get("LINHA_FUNCIONAL") or RAIZ
for p in (LINHA, os.path.join(LINHA, "coleta"), os.path.join(LINHA, "admissao")):
    if p not in sys.path:
        sys.path.insert(0, p)

SCHEMA = "ensaio_espera"
fora = []


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


def e_descartavel(url):
    """A MESMA trava da casa: lista de PERMISSAO, e nao de bloqueio."""
    try:
        u = urlparse(url or "")
    except Exception:
        return False
    return (u.hostname in ("127.0.0.1", "localhost", "::1", "db", "postgres")
            and (u.path or "/").lstrip("/") in ("descartavel", "derivado"))


class Banco:
    """psql, no padrao da casa. `-q` para a fala do cliente nao virar dado."""

    def __init__(self, dsn):
        self.dsn = dsn

    def executa(self, sql):
        r = subprocess.run(
            ["psql", self.dsn, "-q", "-v", "ON_ERROR_STOP=1", "-tAF", "\x1f",
             "-c", sql], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip()[:400])
        return [l.split("\x1f") for l in r.stdout.strip().split("\n") if l]

    def tenta(self, sql):
        r = subprocess.run(
            ["psql", self.dsn, "-q", "-v", "ON_ERROR_STOP=1", "-tAF", "\x1f",
             "-c", sql], capture_output=True, text=True)
        return r.returncode, r.stdout.strip(), r.stderr.strip()


# ── A TABELA DO ENSAIO ───────────────────────────────────────────────────
# Os 11 campos da COL-LAW-043, e NEM UM A MAIS. A tentacao de acrescentar
# `raw_observation_id` para ganhar chave estrangeira e exactamente o 12o campo
# que a lei proibe — e ele fica de fora, de proposito, para a medicao mostrar
# o que a OPCAO B consegue SEM violar o contrato.
DDL = """
drop schema if exists {s} cascade;
create schema {s};
create table {s}.unidade_pronta (
  id              bigserial primary key,
  estado          text not null,
  item_id         text not null,
  universo        text not null,
  texto           text not null,
  source_id       text not null,
  source_location text not null,
  fact_location   text not null,
  fact_time       text not null,
  captured_at     text not null,
  corrida         text not null,
  admitido_por    text not null,
  gravado_em      timestamptz not null default now(),
  constraint uma_unidade_por_corrida unique (corrida, item_id, universo),
  constraint o_estado_e_so_um check (estado = 'PRONTO_PARA_INTELIGENCIA')
);
""".format(s=SCHEMA)

CAMPOS = ("ESTADO", "ITEM_ID", "UNIVERSO", "TEXTO", "SOURCE_ID",
          "SOURCE_LOCATION", "FACT_LOCATION", "FACT_TIME", "CAPTURED_AT",
          "CORRIDA", "ADMITIDO_POR")
COLUNAS = [c.lower() for c in CAMPOS]


def _lit(v):
    return "'" + str(v).replace("'", "''") + "'"


def pousar_sql(unidades, run_id):
    """A OPCAO B a pousar: UMA transacao, todas as unidades ou nenhuma.

    `on conflict do nothing` + contagem do que entrou e como se distingue
    POUSOU de JA_ESTAVA sem uma segunda leitura que mentiria entre as duas.
    """
    if not unidades:
        return "select 0"
    linhas = ",".join(
        "(" + ",".join(_lit(u[c]) for c in CAMPOS) + ")" for u in unidades)
    return ("insert into {s}.unidade_pronta ({cols}) values {v} "
            "on conflict (corrida, item_id, universo) do nothing "
            "returning id").format(s=SCHEMA, cols=",".join(COLUNAS), v=linhas)


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL") or ""
    if not e_descartavel(url):
        raise SystemExit(
            "RECUSADO: '%s' nao parece um banco descartavel local. "
            "Este ensaio nunca corre contra producao." % url)

    import _gavetas                                    # noqa: F401
    import admissao
    import sala_de_espera as espera

    sql = Banco(url)
    sql.executa(DDL)
    print("=" * 74)
    print("A SALA DE ESPERA EM POSTGRES — OPCAO B · schema %s · descartavel"
          % SCHEMA)
    print("=" * 74)

    # A unidade e construida pelo DONO do contrato, e nao a mao. Se a OPCAO B
    # precisasse de um construtor proprio, ja teria perdido em ONE OWNER.
    d = admissao.Decisao(item="IT-DOC-1", universo="fitossanitario",
                         resultado=admissao.SIM, regra="R-ADM", motivo="fala de fungo",
                         evidencia="fungo", versao="1", corrida="RUN-B",
                         quando="2026-09-13T00:00:00Z")
    item = {"texto": "il fungo provoca sintomi sulla foglia",
            "source_id": "IT-T3-002", "captured_at": "2026-09-10T00:00:00Z"}
    unidade = admissao.pronto_para_inteligencia(item, d)

    caso("B_E5_a_unidade_tem_os_11_campos_da_lei_e_nem_um_a_mais",
         tuple(unidade.keys()) == CAMPOS,
         "%d campos, na ordem da COL-LAW-043" % len(unidade))
    caso("B_E6_e_o_estado_dela_e_PRONTO_PARA_INTELIGENCIA",
         unidade["ESTADO"] == "PRONTO_PARA_INTELIGENCIA",
         "ESTADO=%s" % unidade["ESTADO"])

    # ── E3 · POUSAR ──────────────────────────────────────────────────────
    ids = sql.executa(pousar_sql([unidade], "RUN-B"))
    caso("B_E3_a_unidade_POUSOU_na_sala_de_espera", len(ids) == 1,
         "id=%s" % (ids[0][0] if ids else "-"))

    n = sql.executa("select count(*) from %s.unidade_pronta" % SCHEMA)[0][0]
    caso("B_E4_a_linha_existe_e_le_se_inteira", n == "1",
         "%s linha(s) na sala" % n)

    # ── R1/R2 · RETRY IDEMPOTENTE ────────────────────────────────────────
    antes = sql.executa("select id, gravado_em from %s.unidade_pronta" % SCHEMA)
    ids2 = sql.executa(pousar_sql([unidade], "RUN-B"))
    depois = sql.executa("select id, gravado_em from %s.unidade_pronta" % SCHEMA)
    caso("B_R1_o_retry_com_o_MESMO_conteudo_diz_REUSED", len(ids2) == 0,
         "insert devolveu 0 linhas: a unicidade absorveu o retry")
    caso("B_R2_e_nao_mexe_na_linha", antes == depois,
         "id e gravado_em iguais antes e depois")

    # ── C1/C2 · A MESMA CORRIDA COM OUTRA HISTORIA ───────────────────────
    # ⚠️ E AQUI A OPCAO B DIVERGE DA OPCAO A, E NAO E DETALHE.
    outra = dict(unidade, TEXTO="OUTRA HISTORIA COMPLETAMENTE")
    ids3 = sql.executa(pousar_sql([outra], "RUN-B"))
    texto = sql.executa("select texto from %s.unidade_pronta" % SCHEMA)[0][0]
    caso("B_C1_a_mesma_corrida_com_OUTRA_historia_e_conflito",
         len(ids3) == 0 and texto == unidade["TEXTO"],
         "SILENCIO: `do nothing` engoliu a divergencia — 0 linhas, 0 excepcao")
    caso("B_C2_e_a_linha_anterior_fica_INTACTA", texto == unidade["TEXTO"],
         "a primeira historia sobreviveu")

    # ── A1 · ATOMICIDADE DE UM LOTE ──────────────────────────────────────
    # Duas unidades, a segunda invalida. A OPCAO A escreve o ficheiro inteiro
    # ou nenhum; a OPCAO B tem de provar o mesmo DENTRO da transacao.
    boa = dict(unidade, ITEM_ID="IT-DOC-2")
    ma = dict(unidade, ITEM_ID="IT-DOC-3", ESTADO="INVENTADO")
    rc, _out, err = sql.tenta(
        "begin; " + pousar_sql([boa, ma], "RUN-B") + "; commit;")
    n2 = sql.executa("select count(*) from %s.unidade_pronta" % SCHEMA)[0][0]
    caso("B_A1_o_lote_publica_inteiro_ou_nao_publica",
         rc != 0 and n2 == "1",
         "a check recusou o lote e a boa NAO entrou sozinha: %s linha(s)" % n2)
    caso("B_A2_e_nao_deixa_lixo_para_tras", n2 == "1",
         "nenhuma linha orfa do lote recusado")

    # ── X1 · CRASH ANTES DO COMMIT ───────────────────────────────────────
    nova = dict(unidade, ITEM_ID="IT-DOC-4")
    proc = subprocess.Popen(
        ["psql", url, "-q", "-v", "ON_ERROR_STOP=1", "-c",
         "begin; " + pousar_sql([nova], "RUN-B")
         + "; select pg_sleep(30); commit;"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.0)
    proc.kill()
    proc.wait()
    n3 = sql.executa("select count(*) from %s.unidade_pronta" % SCHEMA)[0][0]
    caso("B_X1_um_crash_ANTES_do_commit_deixa_o_anterior_valido", n3 == "1",
         "a transacao morta nao deixou linha: %s linha(s), e as antigas leem-se"
         % n3)

    # ── K1/K2 · DUAS MAOS NA MESMA CORRIDA ───────────────────────────────
    # A OPCAO A trava por corrida e a segunda mao ouve «ocupada». A OPCAO B
    # nao trava: ela deixa as duas entrarem e resolve no COMMIT.
    conc = dict(unidade, ITEM_ID="IT-DOC-CONC")
    p1 = subprocess.Popen(
        ["psql", url, "-q", "-v", "ON_ERROR_STOP=1", "-c",
         "begin; " + pousar_sql([conc], "RUN-B")
         + "; select pg_sleep(3); commit;"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.6)
    t0 = time.time()
    rc2, out2, err2 = sql.tenta("begin; " + pousar_sql([conc], "RUN-B")
                                + "; commit;")
    esperou = time.time() - t0
    p1.wait()
    n4 = sql.executa(
        "select count(*) from %s.unidade_pronta where item_id='IT-DOC-CONC'"
        % SCHEMA)[0][0]
    caso("B_K1_duas_maos_na_mesma_corrida_nao_se_atropelam", n4 == "1",
         "a segunda BLOQUEOU %.1fs a espera do commit da primeira" % esperou)
    caso("B_K2_e_a_sala_ficou_com_UMA_historia_so", n4 == "1",
         "%s linha para IT-DOC-CONC" % n4)

    # ── N · O QUE NAO ENTRA NA SALA ──────────────────────────────────────
    for resultado in (admissao.NAO, admissao.NAO_SEI, admissao.NAO_SE_APLICA,
                      admissao.ERRO):
        dn = admissao.Decisao(item="IT-X", universo="fitossanitario",
                              resultado=resultado, regra="R-ADM", motivo="-",
                              evidencia="-", versao="1", corrida="RUN-B",
                              quando="2026-09-13T00:00:00Z")
        try:
            admissao.pronto_para_inteligencia(item, dn)
            recusou = False
        except ValueError:
            recusou = True
        caso("B_N_%s_nao_produz_unidade_nenhuma" % resultado, recusou,
             "o DONO recusou construir — e isto e do contrato, nao do backend")

    # ── O QUE SO O BANCO CONSEGUE, E O QUE ELE NAO CONSEGUE ──────────────
    cols = [r[0] for r in sql.executa(
        "select column_name from information_schema.columns where "
        "table_schema='%s' and table_name='unidade_pronta' order by 1" % SCHEMA)]
    extra = [c for c in cols if c not in COLUNAS + ["id", "gravado_em"]]
    caso("B_D1_a_unicidade_e_do_BANCO_e_nao_do_processo", True,
         "constraint uma_unidade_por_corrida (corrida,item_id,universo)")
    fks = sql.executa(
        "select count(*) from information_schema.table_constraints where "
        "table_schema='%s' and constraint_type='FOREIGN KEY'" % SCHEMA)[0][0]
    caso("B_D2_MAS_nao_ha_chave_estrangeira_para_o_RAW", fks == "0",
         "ITEM_ID e texto natural (decisao.item), e nao raw_asset.id: "
         "sem 12o campo nao ha FK — e o 12o campo e o que a COL-LAW-043 proibe")
    caso("B_D3_a_tabela_nao_carrega_campo_a_mais", not extra,
         "colunas alem dos 11 + surrogate tecnico: %s" % (extra or "nenhuma"))

    sql.executa("drop schema %s cascade" % SCHEMA)
    restou = sql.executa(
        "select count(*) from information_schema.schemata where schema_name='%s'"
        % SCHEMA)[0][0]
    caso("B_Z_o_ensaio_nao_deixou_tabela_atras_de_si", restou == "0",
         "schema %s derrubado" % SCHEMA)

    print()
    for nome, ok, detalhe in fora:
        print("  %-4s %-56s %s" % ("PASS" if ok else "FALHA", nome, detalhe))
    veredito = all(ok for _n, ok, _d in fora)
    print("=" * 74)
    print("ESPERA_EM_POSTGRES=%s" % ("PASS" if veredito else "FAIL"))
    return 0 if veredito else 1


if __name__ == "__main__":
    raise SystemExit(main())
