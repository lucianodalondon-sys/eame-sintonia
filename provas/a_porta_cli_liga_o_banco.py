#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PORTA CLI DO ORQUESTRADOR LIGA O BANCO DESCARTÁVEL — provado como PROCESSO.

    py provas/a_porta_cli_liga_o_banco.py                      (sobe um Postgres 16
                                                                portátil, se houver)
    BANCO_DESCARTAVEL_URL=postgresql://...@localhost:5432/descartavel \\
        py provas/a_porta_cli_liga_o_banco.py                  (usa o que lhe derem)

A PERGUNTA, E É UMA SÓ
----------------------
    A MESMA PORTA QUE O WORKFLOW CHAMA — `orquestrador/orquestrador.py`, como
    PROCESSO SEPARADO, com `BANCO_DESCARTAVEL_URL` no ambiente e NADA passado
    por Python — escreve a RUN, a OBSERVAÇÃO, a CÓPIA, o DERIVADO e o
    DOCUMENTO no banco, e o recibo diz o mesmo que o banco?

O QUE ISTO NÃO FAZ, E É O QUE A TORNA A PROVA CERTA
---------------------------------------------------
Não chama `orq.correr(memoria=..., banco_do_rastro=...)`. Foi exactamente
assim que a primeira coleta controlada passou (§130) — e foi exactamente por
isso que o defeito da porta CLI ficou invisível até ao replay canário pelo
workflow real (run 35215565657, §132): a prova ligava o banco por fora, e a
porta que o workflow usa não ligava nada.

    A PORTA QUE A PROVA USA TEM DE SER A PORTA QUE O WORKFLOW USA.
    FAKE EXECUTOR != CANONICAL E2E PROVEN — mas aqui o executor não é o
    assunto: a REDE fica de fora de propósito, e o material entra pela porta
    canónica de REPROCESSAMENTO (`--so-a-porta --colheita-da-corrida=<RUN>`),
    que é a mesma estrada RAW → STORAGE → DERIVED → STRUCTURED, sem aquisição.

O MATERIAL
----------
Um boletim ARPAV já versionado (`data/collection-store/italy/IT-T2-002/…/agro_01.pdf`)
e a linha do livro que o descreve, copiados para um `ITALY_OPS_ROOT`
descartável com uma corrida-fixture. O envelope de retorno é declarado pelo
próprio executor italiano (`italy_executor.colher`), e não escrito à mão.

O QUE ELA ISOLA, E O QUE NÃO CONSEGUE
-------------------------------------
Livro e armazém do coletor: no OPS_ROOT temporário. O banco: descartável, e
morre no fim. O que NÃO consegue isolar — porque é dívida nomeada e não desta
missão (`ADMISSION_LEDGER_NOT_ENV_REDIRECTABLE`): `data/samples/RUN-MANIFEST.json`
e `data/samples/LIVRO-DE-DECISOES.json` têm caminho fixo. A prova fotografa
os dois antes, restaura-os byte a byte depois, e reprova se não conseguir.

SAÍDA
-----
    0   PASS      1   FAIL      2   NOT_RUN (sem Postgres para subir)

NOT_RUN não é PASS, e o código de saída di-lo (mesmo vocabulário de
`provas/preservar_coleta_no_postgres.py`).
"""
import hashlib
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

from guarda.banco_descartavel import e_descartavel  # noqa: E402

FIXTURE_PDF = os.path.join("data", "collection-store", "italy", "IT-T2-002",
                           "ARPAV_Z01_20260903160930", "v1_f88c89d73d6a",
                           "agro_01.pdf")
FIXTURE_SHA = "f88c89d73d6a132a1c1ec6e87aadd893dd1f1028425dcf0fc4ffb37ab29170af"
FONTE = "IT-T2-002"
ASSUNTO = "colete clima"
CAMINHOS_FIXOS = (os.path.join("data", "samples", "RUN-MANIFEST.json"),
                  os.path.join("data", "samples", "LIVRO-DE-DECISOES.json"))
# O DONO da bancada portátil é `SINTONIA_PG_PORTATIL` — o mesmo que o workflow
# lê no 5a-IT. Esta é só a omissão, e é a MESMA do workflow, escrita de forma
# portátil: `$HOME/orca/pgtmp/pgsql/bin`. A primeira versão gravava aqui o
# caminho absoluto de UMA conta Windows (`C:\Users\<utilizador>\…`), e a guarda
# de credenciais (guarda/social_guarda.py · «caminho pessoal Windows») acusou-o
# na árvore versionada. Identidade de máquina não é configuração.
PG_PORTATIL_POR_OMISSAO = os.path.join(os.path.expanduser("~"),
                                       "orca", "pgtmp", "pgsql", "bin")

CASOS = []
try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass


def caso(nome, ok, detalhe=""):
    CASOS.append((nome, bool(ok), detalhe))
    print("  %-4s %-58s %s" % ("PASS" if ok else "FAIL", nome, detalhe))
    return bool(ok)


def _psql(url, sql):
    cmd = ["psql", "-X", "-q", "-A", "-t", "-F", "\x1f",
           "-v", "ON_ERROR_STOP=1", "-f", "-", url]
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:400])
    return [l.split("\x1f") for l in r.stdout.splitlines() if l.strip()]


def _um(url, sql):
    r = _psql(url, sql)
    return r[0][0] if r else ""


# ═════════════════════════════════════════════════════════════════════════
# O POSTGRES DESCARTÁVEL — o que vier no ambiente, ou um que nasce aqui
# ═════════════════════════════════════════════════════════════════════════

class Bancada:
    """Um cluster portátil que nasce e morre com a prova. `None` se não der."""

    def __init__(self):
        self.pgbin = None
        self.cluster = None
        self.porto = None
        self.url = None
        self.log = None

    @staticmethod
    def binarios():
        for candidato in (os.environ.get("SINTONIA_PG_PORTATIL"),
                          PG_PORTATIL_POR_OMISSAO):
            if candidato and os.path.isfile(os.path.join(candidato, "initdb.exe")):
                return candidato
            if candidato and os.path.isfile(os.path.join(candidato, "initdb")):
                return candidato
        p = shutil.which("initdb")
        return os.path.dirname(p) if p else None

    @staticmethod
    def porto_livre():
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        p = s.getsockname()[1]
        s.close()
        return p

    def subir(self):
        self.pgbin = self.binarios()
        if not self.pgbin:
            return None
        self.cluster = tempfile.mkdtemp(prefix="pg-prova-cli-")
        self.porto = self.porto_livre()
        self.log = os.path.join(self.cluster, "servidor.log")
        # O `psql` que a prova e a porta vão chamar é ESTE, e tem de estar no
        # PATH antes de qualquer subprocesso — o adaptador chama-o pelo nome.
        os.environ["PATH"] = self.pgbin + os.pathsep + os.environ.get("PATH", "")
        exe = lambda n: os.path.join(self.pgbin, n)  # noqa: E731
        subprocess.run([exe("initdb"), "-D", self.cluster, "-U", "postgres",
                        "--auth=trust", "-E", "UTF8", "--no-sync"],
                       check=True, capture_output=True)
        # ⚠️ SEM `capture_output` AQUI. O postmaster herda os pipes do pg_ctl
        # e mantém-nos abertos; `run()` fica à espera de um EOF que nunca vem
        # e a prova pendura para sempre com o cluster vivo. O workflow já o
        # sabia (`>/dev/null` no 5a-IT); esta prova aprendeu-o à sua custa.
        subprocess.run([exe("pg_ctl"), "-D", self.cluster,
                        "-o", "-p %d -h 127.0.0.1" % self.porto,
                        "-l", self.log, "-w", "start"],
                       check=True, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        admin = "postgresql://postgres@127.0.0.1:%d/postgres" % self.porto
        subprocess.run([exe("psql"), "-X", "-q", "-v", "ON_ERROR_STOP=1",
                        "-c", "create database descartavel;", admin],
                       check=True, capture_output=True)
        self.url = "postgresql://postgres@127.0.0.1:%d/descartavel" % self.porto
        return self.url

    def destruir(self):
        if not self.cluster:
            return {}
        exe = os.path.join(self.pgbin, "pg_ctl")
        subprocess.run([exe, "-D", self.cluster, "-w", "-m", "fast", "stop"],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        shutil.rmtree(self.cluster, ignore_errors=True)
        s = socket.socket()
        s.settimeout(0.5)
        try:
            s.connect(("127.0.0.1", self.porto))
            porto_vivo = True
        except OSError:
            porto_vivo = False
        finally:
            s.close()
        return {"PORTO_VIVO": porto_vivo,
                "CLUSTER_SOBROU": os.path.exists(self.cluster)}


def _migrations(url, ambiente):
    bash = shutil.which("bash")
    if not bash:
        raise RuntimeError("bash ausente: a cadeia canonica e um .sh")
    r = subprocess.run([bash, os.path.join("motor", "cadeia_canonica.sh"),
                        "migrations", url], cwd=RAIZ, env=ambiente,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    passes = [l for l in (r.stdout or "").splitlines()
              if l.startswith("MIGRATION_") and "=PASS" in l]
    return r.returncode, len(passes), (r.stdout or "")[-1200:], (r.stderr or "")[-600:]


# ═════════════════════════════════════════════════════════════════════════
# A FIXTURE — o livro, os bytes e o envelope, num OPS_ROOT descartável
# ═════════════════════════════════════════════════════════════════════════

def _linha_do_livro():
    livro = os.path.join(RAIZ, "data", "collection-ledger", "italy",
                         "observations.ndjson")
    for l in io.open(livro, encoding="utf-8"):
        if not l.strip():
            continue
        o = json.loads(l)
        if o.get("SOURCE_ID") == FONTE and o.get("RAW_SHA256") == FIXTURE_SHA:
            return o
    raise RuntimeError("a linha-fixture nao esta no livro versionado")


def preparar_fixture(ops, run_fixture):
    """Copia os bytes e a linha para o OPS_ROOT e faz o EXECUTOR declarar o
    envelope — o mesmo código que declara numa corrida real."""
    origem = os.path.join(RAIZ, FIXTURE_PDF)
    destino = os.path.join(ops, FIXTURE_PDF)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copyfile(origem, destino)
    o = dict(_linha_do_livro())
    o["RUN_ID"] = run_fixture
    o["RAW_PATH"] = destino          # absoluto: o executor relativiza à raiz
    livro = os.path.join(ops, "data", "collection-ledger", "italy",
                         "observations.ndjson")
    os.makedirs(os.path.dirname(livro), exist_ok=True)
    io.open(livro, "w", encoding="utf-8").write(json.dumps(o, ensure_ascii=False) + "\n")
    import italy_executor as ie
    colheita = ie.colher(run_fixture, ops_root=ops, raiz=RAIZ)
    return colheita


# ═════════════════════════════════════════════════════════════════════════
# A PORTA, COMO PROCESSO
# ═════════════════════════════════════════════════════════════════════════

def correr_a_porta(ambiente, run_fixture, extra=()):
    cmd = [sys.executable, os.path.join("orquestrador", "orquestrador.py"),
           ASSUNTO, "--filtro", "pais=IT", "--filtro", "fonte=%s" % FONTE,
           "--so-a-porta", "--colheita-da-corrida=%s" % run_fixture, *extra]
    r = subprocess.run(cmd, cwd=RAIZ, env=ambiente, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       timeout=900)
    run_id = ""
    for l in (r.stdout or "").splitlines():
        if l.startswith("CORRIDA ") and " · " in l:
            run_id = l.split(" · ", 1)[1].strip()
    return r.returncode, run_id, r.stdout or "", r.stderr or ""


def recibo_da_corrida(run_id):
    p = os.path.join(RAIZ, CAMINHOS_FIXOS[0])
    d = json.load(io.open(p, encoding="utf-8"))
    corridas = d if isinstance(d, list) else next(
        (v for v in d.values() if isinstance(v, list)
         and v and isinstance(v[0], dict) and "RUN_ID" in v[0]), [])
    for c in corridas:
        if isinstance(c, dict) and c.get("RUN_ID") == run_id:
            return c
    return {}


def _sha(caminho):
    return hashlib.sha256(io.open(caminho, "rb").read()).hexdigest()


def _git_status(caminhos):
    r = subprocess.run(["git", "status", "--porcelain", "--", *caminhos], cwd=RAIZ,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else "GIT_INDISPONIVEL"


# ═════════════════════════════════════════════════════════════════════════
# main
# ═════════════════════════════════════════════════════════════════════════

def main():
    url = (os.environ.get("BANCO_DESCARTAVEL_URL") or "").strip()
    bancada = Bancada()
    ambiente = dict(os.environ)
    if url:
        if not e_descartavel(url):
            print("RECUSADO: BANCO_DESCARTAVEL_URL nao prova ser descartavel.")
            return 2
        print("banco: o do ambiente (%s...)" % url.split("@")[-1][:40])
    else:
        try:
            url = bancada.subir()
        except (OSError, subprocess.CalledProcessError) as ex:
            print("NOT_RUN: nao consegui subir um Postgres portatil (%s)"
                  % type(ex).__name__)
            return 2
        if not url:
            print("NOT_RUN: nem BANCO_DESCARTAVEL_URL nem Postgres portatil "
                  "(SINTONIA_PG_PORTATIL / initdb no PATH).")
            return 2
        ambiente["PATH"] = os.environ["PATH"]
        print("banco: Postgres portatil em 127.0.0.1:%d/descartavel" % bancada.porto)

    fotografias = {c: io.open(os.path.join(RAIZ, c), "rb").read()
                   for c in CAMINHOS_FIXOS if os.path.exists(os.path.join(RAIZ, c))}
    # O que o GIT via antes — e nao o que a prova acabou de escrever. Comparar
    # a restauracao com a propria fotografia e tautologico (red team, item 17).
    git_antes = _git_status(CAMINHOS_FIXOS)
    ops = tempfile.mkdtemp(prefix="ops-prova-cli-")
    run_fixture = "IT-T2-FIXTURE-CLI-%d" % int(time.time())
    envelopes = []
    try:
        codigo, n, saida, erro = _migrations(url, ambiente)
        caso("migrations_pela_cadeia_canonica", codigo == 0 and n >= 31,
             "exit=%d PASS=%d %s" % (codigo, n, erro[-160:] if codigo else ""))
        if codigo != 0:
            return 1

        colheita = preparar_fixture(ops, run_fixture)
        envelopes.append(colheita.get("DECLAROU_EM") or "")
        caso("fixture_declarada_pelo_executor",
             colheita.get("OBSERVACOES_DESTA_CORRIDA", 0) >= 1
             and colheita.get("COM_BYTES_NO_ARMAZEM", 0) >= 1,
             "run_fixture=%s envelope=%s" % (run_fixture, colheita.get("DECLAROU_EM")))

        base = dict(ambiente)
        base.update({"ITALY_OPS_ROOT": ops, "PYTHONIOENCODING": "utf-8",
                     "SINTONIA_SALA_BACKEND": "POSTGRES",
                     "SINTONIA_SALA_DSN": url})
        for chave in ("SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL"):
            base.pop(chave, None)

        # ── I · a porta com o banco declarado ESCREVE ─────────────────────
        amb = dict(base)
        amb["BANCO_DESCARTAVEL_URL"] = url
        codigo, run1, saida, erro = correr_a_porta(amb, run_fixture)
        caso("cli_exit_0_e_run_id_no_stdout", codigo == 0 and bool(run1),
             "exit=%d run=%s %s" % (codigo, run1, (erro or "")[-200:] if codigo else ""))
        if not run1:
            print(saida[-2000:])
            return 1
        caso("cli_imprime_persistencia_descartavel",
             "persistencia: DESCARTAVEL" in saida)
        recibo = recibo_da_corrida(run1)
        caso("recibo_declara_persistencia_descartavel",
             (recibo.get("PERSISTENCIA") or {}).get("ESTADO") == "DESCARTAVEL",
             json.dumps(recibo.get("PERSISTENCIA"))[:120])
        ingresso = recibo.get("INGRESSO") or {}
        caso("recibo_PARA_A_DERIVACAO_nao_vazio",
             len(ingresso.get("PARA_A_DERIVACAO") or []) >= 1,
             "RUN_STATE=%s RASTRO=%s" % (ingresso.get("RUN_STATE"), ingresso.get("RASTRO")))
        caso("recibo_DERIVACAO_chamada",
             (recibo.get("DERIVACAO") or {}).get("CHAMADO") is True,
             json.dumps((recibo.get("DERIVACAO") or {}).get("BALDES"))[:120])
        caso("recibo_ESTRUTURACAO_chamada",
             (recibo.get("ESTRUTURACAO") or {}).get("CHAMADO") is True,
             "UNIDADES=%s" % (recibo.get("ESTRUTURACAO") or {}).get("UNIDADES"))

        # ── NO BANCO, e não só no recibo ─────────────────────────────────
        run_rows = int(_um(url, "select count(*) from public.collection_run "
                                "where run_id = '%s'" % run1) or 0)
        caso("RUN_ROWS_>=_1_no_banco", run_rows >= 1, "RUN_ROWS=%d" % run_rows)
        obs = _psql(url, "select id, storage_object_id, sha256 from public.raw_asset "
                         "where run_id = '%s' order by id" % run1)
        caso("RAW_OBSERVATIONS_>=_1_no_banco", len(obs) >= 1, "n=%d" % len(obs))
        raw_id = int(obs[0][0]) if obs and obs[0][0].isdigit() else 0
        caso("RAW_OBSERVATION_ID_e_inteiro_positivo", raw_id > 0, "id=%s" % raw_id)
        so_id = obs[0][1] if obs else ""
        caso("STORAGE_OBJECT_ID_existe_e_esta_ligado", bool(so_id) and so_id.isdigit(),
             "storage_object_id=%s" % so_id)
        sha_banco = obs[0][2] if obs else ""
        caso("sha256_no_banco_e_o_dos_bytes", sha_banco == FIXTURE_SHA, sha_banco[:16])
        # A identidade da observacao e um inteiro do banco; o sha e 64 hex.
        # (A primeira versao desta regua perguntava «o id aparece dentro do
        # sha?» — e o digito 1 aparece em qualquer sha. Regua errada, nao
        # defeito.)
        caso("RAW_OBSERVATION_ID_!=_SHA",
             isinstance(raw_id, int) and len(sha_banco) == 64
             and str(raw_id) != sha_banco)
        copia = _psql(url, "select id, storage_path, sha256 from public.storage_object "
                           "where id = %s" % (so_id or "0"))
        caso("copia_no_storage_object_com_o_mesmo_sha",
             bool(copia) and copia[0][2] == FIXTURE_SHA, copia[0][1][:60] if copia else "")
        der = int(_um(url, "select count(*) from public.derived_artifact "
                           "where raw_asset_id = %d" % raw_id) or 0)
        caso("DERIVED_>=_1_no_banco", der >= 1, "derived=%d" % der)
        estr = int(_um(url, "select count(*) from public.documento_estruturado "
                            "where run_id = '%s'" % run1) or 0)
        caso("STRUCTURED_>=_1_no_banco", estr >= 1, "structured=%d" % estr)
        etapas = _psql(url, "select etapa, estado from public.etapa_da_corrida "
                            "where run_id = '%s' order by id" % run1)
        caso("rastro_das_etapas_no_banco", any(e[0] == "RAW" for e in etapas),
             " ".join("%s=%s" % (e[0], e[1]) for e in etapas)[:120])
        caso("RUN_ID_do_recibo_==_RUN_ID_no_banco",
             _um(url, "select run_id from public.collection_run where run_id='%s'" % run1) == run1)
        caso("sem_rede_a_saida_e_um_reprocessamento",
             "colheita reprocessada da corrida" in json.dumps(recibo.get("COLHEITA_NAO_ENCONTRADA", "")))

        # ── J · os mesmos bytes numa corrida nova ─────────────────────────
        codigo, run2, saida2, erro2 = correr_a_porta(amb, run_fixture)
        caso("segunda_corrida_exit_0", codigo == 0 and bool(run2) and run2 != run1,
             "run2=%s" % run2)
        obs2 = _psql(url, "select id, storage_object_id, sha256 from public.raw_asset "
                          "where run_id = '%s' order by id" % run2)
        caso("nova_RUN_tem_a_sua_propria_observacao",
             len(obs2) >= 1 and (obs2[0][0] != obs[0][0]),
             "obs1=%s obs2=%s" % (obs[0][0] if obs else "?", obs2[0][0] if obs2 else "?"))
        caso("mesmos_bytes_=>_um_so_storage_object",
             bool(obs2) and obs2[0][1] == so_id,
             "so1=%s so2=%s" % (so_id, obs2[0][1] if obs2 else "?"))
        n_so = int(_um(url, "select count(*) from public.storage_object "
                            "where sha256 = '%s'" % FIXTURE_SHA) or 0)
        caso("storage_reuse_no_banco", n_so == 1, "storage_objects_para_o_sha=%d" % n_so)
        recibo2 = recibo_da_corrida(run2)
        baldes2 = (recibo2.get("DERIVACAO") or {}).get("BALDES") or {}
        caso("derivado_da_segunda_corrida_e_REUSED_ou_PASSED",
             (baldes2.get("REUSED", 0) + baldes2.get("PASSED", 0)) >= 1,
             json.dumps(baldes2)[:120])
        caso("nao_ha_REUSED_chamado_de_NEW",
             (recibo2.get("DERIVACAO") or {}).get("ESTADO_DA_ETAPA") in ("PASS", "REUSED", "PASSED", "PARTIAL")
             and not (baldes2.get("PASSED", 0) >= 1 and baldes2.get("REUSED", 0) == 0 and der >= 1 and
                      int(_um(url, "select count(*) from public.derived_artifact where raw_asset_id = %s" % (obs2[0][0] if obs2 else "0")) or 0) == 0),
             "ESTADO_DA_ETAPA=%s" % (recibo2.get("DERIVACAO") or {}).get("ESTADO_DA_ETAPA"))

        # ── B · variavel declarada mas NÃO descartável: recusa ANTES de escrever
        antes = _sha(os.path.join(RAIZ, CAMINHOS_FIXOS[0]))
        runs_antes = int(_um(url, "select count(*) from public.collection_run") or 0)
        amb_mau = dict(base)
        amb_mau["BANCO_DESCARTAVEL_URL"] = "postgresql://postgres:x@db.abcdefgh.supabase.co:5432/postgres"
        codigo, run_mau, saida_mau, _ = correr_a_porta(amb_mau, run_fixture)
        caso("B_supabase_em_BANCO_DESCARTAVEL_URL_e_recusado", codigo == 2 and "BANCO_RECUSADO" in saida_mau and not run_mau,
             "exit=%d" % codigo)
        caso("B_recusa_veio_ANTES_de_qualquer_escrita",
             _sha(os.path.join(RAIZ, CAMINHOS_FIXOS[0])) == antes
             and int(_um(url, "select count(*) from public.collection_run") or 0) == runs_antes)
        amb_mau["BANCO_DESCARTAVEL_URL"] = "postgresql://postgres@localhost:%s/descartavel?host=db.abcdefgh.supabase.co" % (bancada.porto or 5432)
        codigo, run_mau, saida_mau, _ = correr_a_porta(amb_mau, run_fixture)
        caso("D_host_override_na_query_e_recusado", codigo == 2 and "BANCO_RECUSADO" in saida_mau, "exit=%d" % codigo)

        # ── E · PGHOSTADDR na parede: a libpq desviaria; a composicao tira-o ──
        amb_e = dict(amb)
        amb_e["PGHOSTADDR"] = "127.0.0.2"       # loopback onde ninguem escuta
        amb_e["PGSERVICE"] = "producao"
        runs_antes = int(_um(url, "select count(*) from public.collection_run") or 0)
        codigo, run_e, saida_e, erro_e = correr_a_porta(amb_e, run_fixture)
        recibo_e = recibo_da_corrida(run_e) if run_e else {}
        obs_e = (_psql(url, "select count(*) from public.raw_asset where run_id = '%s'" % run_e)
                 if run_e else [])
        caso("E_PGHOSTADDR_e_PGSERVICE_no_ambiente_nao_desviam_a_ligacao",
             codigo == 0 and bool(run_e) and obs_e and int(obs_e[0][0]) >= 1
             and int(_um(url, "select count(*) from public.collection_run") or 0) == runs_antes + 1,
             "exit=%d run=%s" % (codigo, run_e))
        retirado = (recibo_e.get("PERSISTENCIA") or {}).get("AMBIENTE_RETIRADO") or []
        caso("E_o_recibo_diz_que_variaveis_sairam",
             sorted(retirado) == ["PGHOSTADDR", "PGSERVICE"], json.dumps(retirado))

        # ── H · produção no ambiente e nenhuma bancada: NÃO se liga nada ──
        amb_h = dict(base)
        amb_h["SUPABASE_DB_URL"] = "postgresql://postgres:x@db.abcdefgh.supabase.co:5432/postgres"
        amb_h["SINTONIA_SALA_DSN"] = url     # a Sala é outro dono; fica como está
        codigo, run_h, saida_h, erro_h = correr_a_porta(amb_h, run_fixture)
        recibo_h = recibo_da_corrida(run_h) if run_h else {}
        caso("H_sem_BANCO_DESCARTAVEL_URL_a_persistencia_e_AUSENTE",
             codigo == 0 and (recibo_h.get("PERSISTENCIA") or {}).get("ESTADO") == "AUSENTE"
             and "persistencia: AUSENTE" in saida_h, "exit=%d" % codigo)
        caso("H_sem_banco_nao_ha_observacao_no_banco_nenhum",
             (recibo_h.get("INGRESSO") or {}).get("RASTRO") == "NAO_EMITIDO"
             and not (recibo_h.get("INGRESSO") or {}).get("PARA_A_DERIVACAO")
             and int(_um(url, "select count(*) from public.collection_run where run_id='%s'" % run_h) or 0) == 0)
        return 0 if all(ok for _, ok, _ in CASOS) else 1
    finally:
        # ── RESTAURAR O QUE TEM CAMINHO FIXO, BYTE A BYTE ─────────────────
        for c, antes_bytes in fotografias.items():
            io.open(os.path.join(RAIZ, c), "wb").write(antes_bytes)
        restaurados = all(io.open(os.path.join(RAIZ, c), "rb").read() == b
                          for c, b in fotografias.items())
        caso("ficheiros_de_caminho_fixo_restaurados_byte_a_byte", restaurados)
        depois = _git_status(CAMINHOS_FIXOS)
        caso("git_ve_os_ficheiros_de_caminho_fixo_como_antes", depois == git_antes,
             "antes=%r depois=%r" % (git_antes[:60], depois[:60]))
        # O envelope da fixture vive numa pasta so dela (por corrida, como a
        # lei do retorno manda); a pasta sai inteira. `colheita.json` e o
        # balcao fixo do executor (ignorado pelo git) e fica como estava.
        for e in envelopes:
            pasta = os.path.dirname(os.path.join(RAIZ, e)) if e else ""
            if pasta and os.path.basename(pasta).startswith("IT-T2-FIXTURE-CLI-"):
                shutil.rmtree(pasta, ignore_errors=True)
        shutil.rmtree(ops, ignore_errors=True)
        fim = bancada.destruir()
        if fim:
            caso("bancada_destruida_porto_fechado_cluster_removido",
                 not fim["PORTO_VIVO"] and not fim["CLUSTER_SOBROU"], json.dumps(fim))
        reprovados = [n for n, ok, _ in CASOS if not ok]
        print("\nCLI_POSTGRES_BINDING_PROVEN=%s · %d caso(s)%s"
              % ("PASS" if not reprovados else "FAIL", len(CASOS),
                 "" if not reprovados else " · reprovados: " + ", ".join(reprovados)))


if __name__ == "__main__":
    sys.exit(main())
