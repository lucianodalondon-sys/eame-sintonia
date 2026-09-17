#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CLIENTE psql É DECLARADO, E O PATH DEIXA DE SER REQUISITO — provada em Windows real.

    py provas/o_cliente_psql_e_declarado.py

O DEFEITO QUE ISTO FECHA
------------------------
O replay canário 3 pelo workflow real (run GitHub 35232024024, know-how §135)
passou os três portões, adquiriu IT-T3-002 da rede e caiu na primeira chamada
do runtime ao banco: `subprocess.run(["psql", …])` → `FileNotFoundError`. O
Sala gate tinha dito PASS sem abrir ligação nenhuma.

O QUE ESTA PROVA FAZ, POR ORDEM
-------------------------------
    1  sobe um PostgreSQL 16 portátil (nasce e morre aqui), aplica as migrations
       pela cadeia canónica — com o psql no PATH SÓ para o `.sh`;
    2  tira o psql do PATH DESTE processo e de todos os filhos, e declara
       `SINTONIA_PSQL_EXE` com o caminho NATIVO;
    3  prova `shutil.which("psql") is None` e `resolver_psql()` = o declarado;
    4  os três donos do runtime falam com o banco REAL: `MemoriaPostgres`
       (select + insert), `coleta_checkpoint.Banco` (select + insert), a Sala
       `_Postgres` (leitura real) e o portão `--portao` como PROCESSO;
    5  a porta CLI do orquestrador como PROCESSO, sem rede, com a fixture do
       §133 — RUN, RAW, STORAGE, DERIVED, STRUCTURED no banco;
    6  negativos: declaração vazia + PATH sem psql; declaração inexistente;
       declaração a apontar para outro exe; forma POSIX; PATH com psql +
       declaração inválida (NÃO cai para o PATH); PATH com psql + declaração
       válida diferente (o explícito vence); caminho com espaço; caminho com
       acento;
    7  o portão da Sala FALHA com psql ausente e FALHA com o banco parado —
       antes de qualquer rede.

    CAN DO != DID DO.  Nada aqui é mock: PostgreSQL real, processos reais.

NOT_RUN não é PASS: sem Postgres portátil a prova diz-o e sai 2.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "provas"))
import _gavetas  # noqa: E402,F401
from guarda import cliente_postgres as cp  # noqa: E402
import a_porta_cli_liga_o_banco as cli  # noqa: E402  (a bancada e a fixture do §133)

CASOS = []


def caso(nome, ok, detalhe=""):
    CASOS.append((nome, bool(ok), detalhe))
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", nome, (" · " + detalhe) if detalhe else ""))


def _sem_psql(path, pgbin):
    """O PATH sem NENHUMA pasta que tenha um psql — não só a da bancada."""
    fora = []
    for p in (path or "").split(os.pathsep):
        q = p.strip().rstrip("\\/")
        if not q:
            continue
        if q.lower() == pgbin.rstrip("\\/").lower():
            continue
        if any(os.path.isfile(os.path.join(q, n)) for n in cp.NOMES_ACEITES):
            continue
        fora.append(p)
    return os.pathsep.join(fora)


def _portao(ambiente):
    r = subprocess.run([sys.executable, os.path.join("admissao", "sala_de_espera.py"),
                        "--portao"], cwd=RAIZ, env=ambiente, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=120)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _juncao(destino, origem):
    """Uma junção NTFS: a mesma pasta de binários, com outro nome. Sem cópia."""
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    if os.name == "nt":
        r = subprocess.run(["cmd", "/c", "mklink", "/J", destino, origem],
                           capture_output=True, text=True)
        return r.returncode == 0
    os.symlink(origem, destino)
    return True


def main():
    bancada = cli.Bancada()
    try:
        url = bancada.subir()
    except (OSError, subprocess.CalledProcessError) as ex:
        print("NOT_RUN: nao consegui subir um Postgres portatil (%s)" % type(ex).__name__)
        return 2
    if not url:
        print("NOT_RUN: nem Postgres portatil (SINTONIA_PG_PORTATIL / initdb no PATH).")
        return 2
    pgbin = bancada.pgbin
    psql_nativo = os.path.normpath(os.path.join(pgbin, "psql.exe" if os.name == "nt" else "psql"))
    print("banco: Postgres portatil em 127.0.0.1:%d/descartavel" % bancada.porto)
    print("psql declarado: %s" % psql_nativo)

    # 1 · migrations: o .sh precisa do psql no PATH — e SÓ ele
    amb_sh = dict(os.environ)
    amb_sh["PATH"] = pgbin + os.pathsep + amb_sh.get("PATH", "")
    codigo, n, _, erro = cli._migrations(url, amb_sh)
    caso("migrations_pela_cadeia_canonica", codigo == 0 and n >= 31,
         "exit=%d PASS=%d %s" % (codigo, n, (erro or "")[-120:] if codigo else ""))
    if codigo != 0:
        return 1

    # 2 · o PATH deste processo e dos filhos deixa de ter psql; a declaração entra
    os.environ["PATH"] = _sem_psql(os.environ.get("PATH", ""), pgbin)
    os.environ.pop("SINTONIA_PSQL_EXE", None)
    caso("PATH_sem_psql", shutil.which("psql") is None, "which=%r" % shutil.which("psql"))
    try:
        cp.resolver_psql()
        caso("sem_declaracao_e_sem_PATH_falha_fechado", False, "resolveu sem ter com que")
    except cp.ClientePostgresAusente as ex:
        caso("sem_declaracao_e_sem_PATH_falha_fechado", "SINTONIA_PSQL_EXE" in str(ex))
    os.environ["SINTONIA_PSQL_EXE"] = psql_nativo
    caso("resolver_devolve_o_declarado", cp.resolver_psql() == psql_nativo, cp.resolver_psql())
    caso("caminho_e_nativo", os.path.isabs(psql_nativo) and (":" in psql_nativo[:3] or os.name != "nt"), psql_nativo)

    # 4 · os três donos, contra o banco real, sem psql no PATH
    from guarda.memoria_postgres import MemoriaPostgres
    m = MemoriaPostgres(url)
    caso("MemoriaPostgres_select_real", m._valor("select 1") == "1")
    m.aplicar("create table if not exists public._prova_cliente_psql (x int); "
              "insert into public._prova_cliente_psql values (7);")
    caso("MemoriaPostgres_insert_real", m._valor("select count(*) from public._prova_cliente_psql") == "1")
    import coleta_checkpoint as cc
    b = cc.Banco(url)
    caso("Banco_select_real", b.executa("select 7") == [["7"]])
    b.executa("insert into public._prova_cliente_psql values (8)")
    caso("Banco_insert_real", b.executa("select count(*) from public._prova_cliente_psql") == [["2"]])
    m.aplicar("drop table public._prova_cliente_psql;")
    os.environ["SINTONIA_SALA_BACKEND"] = "POSTGRES"
    os.environ["SINTONIA_SALA_DSN"] = url
    import sala_de_espera as se
    try:
        e = se.exigir_canonica()
        caso("Sala_exigir_canonica_sonda_o_banco_real", e.get("SONDA") == "OK",
             json.dumps({k: e.get(k) for k in ("BACKEND", "SONDA", "PSQL_ORIGEM")}))
    except se.SalaIndisponivel as ex:
        caso("Sala_exigir_canonica_sonda_o_banco_real", False, str(ex)[:160])
    caso("Sala_leitura_real", se.ler("RUN-QUE-NAO-EXISTE") is None)
    amb = dict(os.environ)
    amb.update({"PYTHONIOENCODING": "utf-8"})
    for chave in ("SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL"):
        amb.pop(chave, None)
    codigo, saida = _portao(amb)
    caso("SALA_GATE_REAL_DB_PASS_como_processo", codigo == 0 and "SALA_DE_ESPERA=PASS" in saida,
         "exit=%d %s" % (codigo, saida.strip().splitlines()[0][:100] if saida.strip() else ""))

    # 5 · a porta CLI como processo, sem rede, sem psql no PATH
    ops = tempfile.mkdtemp(prefix="ops-prova-psql-")
    run_fixture = "IT-T2-FIXTURE-PSQL-%d" % int(time.time())
    fotografias = {c: io.open(os.path.join(RAIZ, c), "rb").read()
                   for c in cli.CAMINHOS_FIXOS if os.path.exists(os.path.join(RAIZ, c))}
    try:
        colheita = cli.preparar_fixture(ops, run_fixture)
        caso("fixture_declarada_pelo_executor", colheita.get("OBSERVACOES_DESTA_CORRIDA", 0) >= 1)
        amb_cli = dict(amb)
        amb_cli.update({"ITALY_OPS_ROOT": ops, "BANCO_DESCARTAVEL_URL": url})
        caso("PATH_da_CLI_nao_tem_psql", shutil.which("psql", path=amb_cli["PATH"]) is None)
        codigo, run1, saida, erro = cli.correr_a_porta(amb_cli, run_fixture)
        caso("CLI_exit_0_sem_psql_no_PATH", codigo == 0 and bool(run1),
             "exit=%d run=%s %s" % (codigo, run1, (erro or "")[-200:] if codigo else ""))
        if run1:
            runs = int(m._valor("select count(*) from public.collection_run where run_id = '%s'" % run1))
            raws = int(m._valor("select count(*) from public.raw_asset where run_id = '%s'" % run1))
            sos = int(m._valor("select count(*) from public.storage_object where sha256 = '%s'" % cli.FIXTURE_SHA))
            ders = int(m._valor("select count(*) from public.derived_artifact d join public.raw_asset r "
                                "on r.id = d.raw_asset_id where r.run_id = '%s'" % run1))
            estr = int(m._valor("select count(*) from public.documento_estruturado where run_id = '%s'" % run1))
            caso("RUN_ROWS_>=_1", runs >= 1, "run=%d" % runs)
            caso("RAW_ROWS_>=_1", raws >= 1, "raw=%d" % raws)
            caso("STORAGE_ROWS_>=_1", sos >= 1, "storage=%d" % sos)
            caso("DERIVED_ROWS_>=_1", ders >= 1, "derived=%d" % ders)
            caso("STRUCTURED_ROWS_>=_1", estr >= 1, "structured=%d" % estr)
            print("  CONTAGENS RUN=%d RAW=%d STORAGE=%d DERIVED=%d STRUCTURED=%d" % (runs, raws, sos, ders, estr))
            caso("CLI_imprime_persistencia_descartavel", "persistencia: DESCARTAVEL" in saida)
    finally:
        for c, conteudo in fotografias.items():
            io.open(os.path.join(RAIZ, c), "wb").write(conteudo)
        shutil.rmtree(ops, ignore_errors=True)
    caso("acervo_versionado_restaurado",
         all(io.open(os.path.join(RAIZ, c), "rb").read() == v for c, v in fotografias.items()))

    # 6 · negativos, no resolvedor e no portão
    def recusa(nome, env, esperado):
        try:
            cp.resolver_psql(env)
            caso(nome, False, "resolveu quando devia recusar")
        except cp.ClientePostgresAusente as ex:
            caso(nome, esperado in str(ex), str(ex)[:90])
    base_sem = dict(os.environ)
    recusa("N1_declaracao_vazia_e_PATH_sem_psql", dict(base_sem, SINTONIA_PSQL_EXE=""), "nenhum psql")
    recusa("N2_declaracao_inexistente", dict(base_sem, SINTONIA_PSQL_EXE=os.path.join(pgbin, "nao-existe.exe")), "nao existe")
    recusa("N3_declaracao_aponta_para_outro_exe", dict(base_sem, SINTONIA_PSQL_EXE=os.path.join(pgbin, "pg_ctl.exe")), "nao se chama psql")
    recusa("N4_forma_POSIX_recusada", dict(base_sem, SINTONIA_PSQL_EXE="/c/Users/x/pgsql/bin/psql.exe"), "POSIX")
    com_path = dict(base_sem, PATH=pgbin + os.pathsep + base_sem["PATH"])
    caso("N5_PATH_com_psql_e_sem_declaracao_usa_o_PATH",
         os.path.normcase(cp.resolver_psql(dict(com_path, SINTONIA_PSQL_EXE=""))) == os.path.normcase(psql_nativo))
    recusa("N6_PATH_com_psql_e_declaracao_invalida_NAO_cai_para_o_PATH",
           dict(com_path, SINTONIA_PSQL_EXE=os.path.join(pgbin, "nao-existe.exe")), "Nao se cai para o PATH")
    raiz_tmp = tempfile.mkdtemp(prefix="pg cliente ")
    with_space = os.path.join(raiz_tmp, "pasta com espaco", "bin")
    with_accent = os.path.join(raiz_tmp, "pasta com acento çãõ", "bin")
    ok_space = _juncao(with_space, pgbin)
    ok_accent = _juncao(with_accent, pgbin)
    psql_space = os.path.join(with_space, os.path.basename(psql_nativo))
    psql_accent = os.path.join(with_accent, os.path.basename(psql_nativo))
    caso("N7_PATH_com_psql_e_declaracao_valida_diferente_o_explicito_vence",
         ok_space and cp.resolver_psql(dict(com_path, SINTONIA_PSQL_EXE=psql_space)) == psql_space, psql_space)
    if ok_space:
        os.environ["SINTONIA_PSQL_EXE"] = psql_space
        caso("N8_caminho_com_espaco_funciona", MemoriaPostgres(url)._valor("select 2") == "2", psql_space)
    else:
        caso("N8_caminho_com_espaco_funciona", False, "nao consegui criar a juncao")
    if ok_accent:
        os.environ["SINTONIA_PSQL_EXE"] = psql_accent
        try:
            caso("N9_caminho_com_acento_funciona", MemoriaPostgres(url)._valor("select 3") == "3", psql_accent)
        except (OSError, IOError) as ex:
            caso("N9_caminho_com_acento_funciona", False, "%s: %s" % (type(ex).__name__, str(ex)[:80]))
    else:
        caso("N9_caminho_com_acento_funciona", False, "nao consegui criar a juncao")
    os.environ["SINTONIA_PSQL_EXE"] = psql_nativo
    for d in (with_space, with_accent):
        try:
            os.rmdir(d)            # a junção sai; a pasta real fica
        except OSError:
            pass
    shutil.rmtree(raiz_tmp, ignore_errors=True)

    # 7 · o portão da Sala falha ANTES da rede: psql ausente, e banco parado
    amb_mau = dict(amb, SINTONIA_PSQL_EXE=os.path.join(pgbin, "nao-existe.exe"))
    codigo, saida = _portao(amb_mau)
    caso("SALA_GATE_FAIL_com_psql_ausente", codigo == 1 and "SALA_DE_ESPERA=BLOCKED" in saida,
         "exit=%d" % codigo)
    amb_sem = dict(amb)
    amb_sem.pop("SINTONIA_PSQL_EXE", None)
    codigo, saida = _portao(amb_sem)
    caso("SALA_GATE_FAIL_sem_declaracao_e_sem_PATH", codigo == 1 and "SALA_DE_ESPERA=BLOCKED" in saida,
         "exit=%d" % codigo)
    fim = bancada.destruir()
    codigo, saida = _portao(amb)
    caso("SALA_GATE_FAIL_com_banco_parado", codigo == 1 and "SALA_DE_ESPERA=BLOCKED" in saida,
         "exit=%d %s" % (codigo, " ".join(saida.split())[:120]))
    caso("teardown_porto_fechado_e_cluster_removido",
         not fim.get("PORTO_VIVO") and not fim.get("CLUSTER_SOBROU"), json.dumps(fim))

    falhas = [c for c in CASOS if not c[1]]
    print()
    print("CASOS=%d PASS=%d FAIL=%d" % (len(CASOS), len(CASOS) - len(falhas), len(falhas)))
    print("PSQL_RUNTIME_BINDING_PROVEN=%s" % ("PASS" if not falhas else "FAIL"))
    return 0 if not falhas else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    raise SystemExit(main())
