#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANARIO-1149 · O ENSAIO NUM POSTGRES DESCARTAVEL — a revisao de derived:1149 e o motor depois dela.

    python3 provas/canario_1149/ensaio_descartavel.py [--saida provas/canario_1149] [--hoje 2026-09-28]

NADA DISTO TOCA NA SALA REAL. O que faz, por ordem:
  1. sobe um PostgreSQL DESCARTAVEL (initdb numa pasta temporaria, porta livre, base `descartavel` — a trava
     `guarda/banco_descartavel.exigir_descartavel` confere a morada) e aplica as migrations pela cadeia
     canonica (`motor/cadeia_canonica.sh migrations`);
  2. semeia a linha de derived:1149 tal como a Sala a exportou (`docs/lab-insumos/canario-1149/LINHA-DA-SALA
     .json`). ⚠️ O DUMP DA SALA NAO ESTA NO REPOSITORIO (vive na maquina do coordenador): a `collection_run` e o
     `raw_asset` 2272 entram como STUB DECLARADO (identity_state FORWARD_IDENTITY_UNPROVEN, preserved=false com
     o motivo, sha256 de zeros) — so para a chave estrangeira e o `raw_source_url` do export existirem;
  3. exporta a vista pela query do motor (`motor/r7_export_da_copia.sql`) — ANTES;
  4. corre `admissao/reprocessar_um_item.py` SECO sobre esse export;
  5. faz o backup do descartavel (pg_dump -Fc, o comando do backup_sala.cmd), escreve o recibo com PROVA_VALE
     SO se o dump se repuser numa segunda base e der o mesmo conteudo, cria um PARAR.flag temporario e APLICA
     pela porta `sala_de_espera.rever`; aplica DUAS vezes (a segunda tem de dar 0 inseridas);
  6. exporta de novo — DEPOIS — e corre `motor/motor_das_capacidades.py` e `pacote/pote_intelligence_casco.py`
     sobre os dois exports, e diz o que derived:1149 virou em cada um.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import banco_descartavel as BD  # noqa: E402

ITEM = "derived:1149"
LINHA = RAIZ / "docs" / "lab-insumos" / "canario-1149" / "LINHA-DA-SALA.json"
PG_BIN = Path(os.environ.get("PG_BIN", "/usr/lib/postgresql/16/bin"))
COLUNAS = ("run_id", "ordem", "item_id", "raw_observation_id", "universo", "texto", "source_id",
           "source_location", "source_location_basis", "fact_location", "fact_location_basis", "fact_time",
           "fact_time_basis", "published_at", "published_at_basis", "observed_at", "completude_tempo_lugar",
           "janela_declarada", "tempo_lugar_evidencia", "captured_at", "admitido_por", "estagio",
           "source_declared_evidence_class", "fato", "estado_da_fila", "pousado_em", "corrida_sha256")
URL_DA_FONTE = ("https://www.crea.gov.it/web/guest/-/xylella-fastidiosa-dalla-ricerca-crea-nuove-strategie-per-"
                "l-olivicoltura")


def _lit(v):
    if v is None:
        return "null"
    if not isinstance(v, str):
        v = json.dumps(v, ensure_ascii=False, sort_keys=True)
    return "'" + v.replace("'", "''") + "'"


def _porta():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def _como_postgres(cmd):
    """initdb/pg_ctl recusam root: corre-se como o utilizador postgres quando se e root."""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return ["runuser", "-u", "postgres", "--"] + cmd
    return cmd


def _psql(url, sql, env=None):
    r = subprocess.run([str(PG_BIN / "psql"), "-X", "-q", "-At", "-v", "ON_ERROR_STOP=1", url, "-c", sql],
                       capture_output=True, text=True, env=env)
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])
    return r.stdout


class Postgres:
    def __init__(self):
        self.pasta = Path(tempfile.mkdtemp(prefix="canario-1149-"))
        self.porta = _porta()
        self.admin = "postgresql://postgres@127.0.0.1:%d/postgres" % self.porta

    def url(self, base="descartavel"):
        return BD.exigir_descartavel("postgresql://postgres@127.0.0.1:%d/%s" % (self.porta, base))

    def subir(self):
        if os.geteuid() == 0:
            shutil.chown(self.pasta, "postgres")
        dados = self.pasta / "pg"
        subprocess.run(_como_postgres([str(PG_BIN / "initdb"), "-D", str(dados), "-U", "postgres",
                                       "--auth=trust", "-E", "UTF8", "--no-sync"]), check=True,
                       capture_output=True)
        subprocess.run(_como_postgres([str(PG_BIN / "pg_ctl"), "-D", str(dados), "-o",
                                       "-p %d -h 127.0.0.1" % self.porta, "-l", str(self.pasta / "pg.log"),
                                       "-w", "start"]), check=True, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for b in ("descartavel", "derivado"):
            _psql(self.admin, "create database %s;" % b)
        r = subprocess.run(["bash", "motor/cadeia_canonica.sh", "migrations", self.url()], cwd=str(RAIZ),
                           capture_output=True, text=True)
        passes = [l for l in r.stdout.splitlines() if l.startswith("MIGRATION_") and l.endswith("=PASS")]
        if r.returncode:
            raise RuntimeError("migrations: " + r.stdout[-600:] + r.stderr[-400:])
        return len(passes)

    def descer(self):
        subprocess.run(_como_postgres([str(PG_BIN / "pg_ctl"), "-D", str(self.pasta / "pg"), "-m", "fast",
                                       "stop"]), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        shutil.rmtree(self.pasta, ignore_errors=True)


def semear(url, linha):
    cr = linha["run_id"]
    _psql(url, "insert into public.collection_run (run_id, platform, started_at, rule_version) values "
               "(%s, 'ENSAIO-CANARIO-1149 (stub)', %s, 'ENSAIO-CANARIO-1149')" % (_lit(cr), _lit(linha["captured_at"])))
    _psql(url, "insert into public.raw_asset (id, run_id, storage_path, media_type, bytes, sha256, captured_at, "
               "source_url, preserved, not_preserved_reason, source_id, identity_state) values "
               "(%d, %s, 'ENSAIO-CANARIO-1149/stub-2272', 'text/html', 0, %s, %s, %s, false, %s, %s, "
               "'FORWARD_IDENTITY_UNPROVEN')"
          % (linha["raw_observation_id"], _lit(cr), _lit("0" * 64), _lit(linha["captured_at"]),
             _lit(URL_DA_FONTE), _lit("ENSAIO CANARIO-1149: STUB declarado — o bruto real (sha256 f2158520f2362956…) "
                                     "vive na Sala do coordenador; o dump nao esta no repositorio"),
             _lit(linha["source_id"])))
    cols = [c for c in COLUNAS if c in linha]
    json_cols = ("completude_tempo_lugar", "janela_declarada", "tempo_lugar_evidencia", "fato")
    _psql(url, "insert into public.sala_de_espera (%s) values (%s)"
          % (", ".join(cols), ", ".join(_lit(json.dumps(linha[c], ensure_ascii=False, sort_keys=True))
                                        if c in json_cols else _lit(linha[c]) for c in cols)))


def exportar(url):
    sql = (RAIZ / "motor" / "r7_export_da_copia.sql").read_text(encoding="utf-8")
    env = dict(os.environ, PGOPTIONS="-c default_transaction_read_only=on")
    r = subprocess.run([str(PG_BIN / "psql"), "-X", "-q", "-At", "-v", "ON_ERROR_STOP=1", url],
                       input="begin transaction read only;\n" + sql + "\ncommit;\n",
                       capture_output=True, text=True, env=env)
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])
    return json.loads(next(l for l in r.stdout.splitlines() if l.startswith("{")))


def impressao(url):
    return _psql(url, "select md5(coalesce(string_agg(x::text, '|' order by x::text), '')) from "
                      "(select * from public.sala_de_espera) x; select md5(coalesce(string_agg(x::text, '|' "
                      "order by x::text), '')) from (select * from public.sala_de_espera_revisao) x;").split()


def correr(cmd, env=None):
    r = subprocess.run([sys.executable] + cmd, cwd=str(RAIZ), capture_output=True, text=True, env=env)
    return {"CMD": " ".join(cmd), "CODIGO": r.returncode, "SAIDA": r.stdout[-3000:], "ERRO": r.stderr[-1500:]}


def _do_item(motor: dict) -> dict:
    fora = {}
    for sec in ("CAP_WIN", "CAP_SCI"):
        bloco = motor.get(sec) or {}
        for chave, v in bloco.items():
            for x in (v if isinstance(v, list) else []):
                if isinstance(x, dict) and x.get("ITEM_ID") == ITEM:
                    fora.setdefault(sec, {})[chave] = x
    for j in (motor.get("CAP_WIN") or {}).get("JANELAS") or []:
        if ITEM in json.dumps(j, ensure_ascii=False):
            fora.setdefault("CAP_WIN", {})["JANELA"] = j
    fora["LINEAGE"] = next((l for l in motor.get("LINEAGE") or [] if l.get("ITEM_ID") == ITEM), None)
    return fora


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    saida = Path(next((a.split("=", 1)[1] for a in argv if a.startswith("--saida=")),
                      str(RAIZ / "provas" / "canario_1149")))
    hoje = next((a.split("=", 1)[1] for a in argv if a.startswith("--hoje=")), "2026-09-28")
    saida.mkdir(parents=True, exist_ok=True)
    linha = json.loads(LINHA.read_text(encoding="utf-8"))
    pg = Postgres()
    res = {"ITEM": ITEM, "HOJE": hoje, "SALA_REAL_TOCADA": False,
           "STUB_DECLARADO": "collection_run + raw_asset 2272 (o dump real nao esta no repositorio)"}
    tmp = Path(tempfile.mkdtemp(prefix="canario-1149-ensaio-"))
    try:
        res["MIGRATIONS_PASS"] = pg.subir()
        url = pg.url()
        semear(url, linha)
        antes = exportar(url)
        (tmp / "export-antes.json").write_text(json.dumps(antes, ensure_ascii=False), encoding="utf-8")
        seco = correr(["admissao/reprocessar_um_item.py", "--entrada", str(tmp / "export-antes.json"),
                       "--item", ITEM, "--saida", str(tmp / "revisoes.json")])
        res["SECO"] = {k: seco[k] for k in ("CODIGO", "ERRO")}
        revs = json.loads((tmp / "revisoes.json").read_text(encoding="utf-8"))
        res["SECO"]["RESUMO"] = revs["RESUMO"]
        res["SECO"]["REVISOES"] = [r["CAMPO"] for r in revs["REVISOES"]]
        res["SECO"]["GRAVOU_NO_BANCO"] = revs["GRAVOU_NO_BANCO"]
        res["SECO"]["IMPRESSAO_DEPOIS_DO_SECO_IGUAL"] = None
        foto_antes = impressao(url)
        res["SECO"]["IMPRESSAO_DEPOIS_DO_SECO_IGUAL"] = foto_antes == impressao(url)
        # 5 · backup provado + PARAR.flag + aplicar (duas vezes)
        dump = tmp / "DESCARTAVEL-ANTES.dump"
        subprocess.run([str(PG_BIN / "pg_dump"), "-Fc", "-Z", "6", "--no-owner", "--no-privileges", "-f",
                        str(dump), url], check=True, capture_output=True)
        url2 = pg.url("derivado")
        rr = subprocess.run([str(PG_BIN / "pg_restore"), "--no-owner", "--no-privileges", "-d", url2, str(dump)],
                            capture_output=True, text=True)
        prova = {"DUMP": str(dump), "PG_RESTORE_CODIGO": rr.returncode,
                 "IMPRESSAO_ORIGINAL": foto_antes, "IMPRESSAO_REPOSTA": impressao(url2)}
        prova["PROVA_VALE"] = rr.returncode == 0 and prova["IMPRESSAO_ORIGINAL"] == prova["IMPRESSAO_REPOSTA"]
        (tmp / "prova-backup.json").write_text(json.dumps(prova), encoding="utf-8")
        res["BACKUP"] = {k: prova[k] for k in ("PG_RESTORE_CODIGO", "PROVA_VALE")}
        env = dict(os.environ, SINTONIA_SALA_BACKEND="POSTGRES", SINTONIA_SALA_DSN=url)
        # sem PARAR.flag tem de recusar (a trava 1)
        parar = RAIZ / "curadoria" / "PARAR.flag"
        existia = parar.exists()
        sem_flag = None
        if not existia:
            sem_flag = correr(["admissao/reprocessar_um_item.py", "--aplicar", str(tmp / "revisoes.json"),
                               "--backup", str(tmp / "prova-backup.json")], env)
        res["APLICAR_SEM_PARAR_FLAG"] = ("NAO_TESTADO (a flag ja existia)" if sem_flag is None else
                                         {"CODIGO": sem_flag["CODIGO"], "ERRO": sem_flag["ERRO"][-200:]})
        parar.write_text("CANARIO-1149 ensaio descartavel\n", encoding="utf-8")
        try:
            a1 = correr(["admissao/reprocessar_um_item.py", "--aplicar", str(tmp / "revisoes.json"),
                         "--backup", str(tmp / "prova-backup.json")], env)
            a2 = correr(["admissao/reprocessar_um_item.py", "--aplicar", str(tmp / "revisoes.json"),
                         "--backup", str(tmp / "prova-backup.json")], env)
        finally:
            if not existia:
                parar.unlink()
        res["APLICAR_1"] = {"CODIGO": a1["CODIGO"], "RECIBO": a1["SAIDA"][-400:], "ERRO": a1["ERRO"][-400:]}
        res["APLICAR_2"] = {"CODIGO": a2["CODIGO"], "RECIBO": a2["SAIDA"][-400:], "ERRO": a2["ERRO"][-400:]}
        res["REVISOES_NA_TABELA"] = _psql(url, "select campo || ' | rev ' || revisao || ' | ' || versao_do_extrator from "
                                               "public.sala_de_espera_revisao order by campo").splitlines()
        res["LINHA_ORIGINAL_INTACTA"] = _psql(url, "select published_at || ' | ' || fact_location from "
                                                   "public.sala_de_espera").strip()
        depois = exportar(url)
        (tmp / "export-depois.json").write_text(json.dumps(depois, ensure_ascii=False), encoding="utf-8")
        l = depois["LINHAS"][0]
        jd = l["janela_declarada"]
        res["VISTA_DEPOIS"] = {
            "published_at": l["published_at"], "published_at_basis": l["published_at_basis"],
            "fact_time": l["fact_time"], "fact_location": l["fact_location"],
            "fact_location_basis": l["fact_location_basis"],
            "CULTURA": jd["CULTURA"]["VALOR"], "PROBLEMA": jd["PROBLEMA"]["VALOR"],
            "PROBLEMA_BASE": jd["PROBLEMA"]["BASE"], "AGENTES_DE_CONTROLE": jd["PROBLEMA"].get("AGENTES_DE_CONTROLE"),
            "REGIAO_DO_FATO": jd["REGIAO_DO_FATO"]["VALOR"], "REGIAO_BASE": jd["REGIAO_DO_FATO"]["BASE"],
            "REGIAO_PRECISAO": jd["REGIAO_DO_FATO"].get("PRECISAO"), "REGIAO_KIND": jd["REGIAO_DO_FATO"]["KIND"]}
        # 6 · o motor e o pote, antes e depois
        for nome in ("antes", "depois"):
            m = correr(["motor/motor_das_capacidades.py", str(tmp / ("export-%s.json" % nome)), "--hoje", hoje,
                        "--saida", str(tmp / ("motor-%s.json" % nome))])
            p = correr(["pacote/pote_intelligence_casco.py", str(tmp / ("motor-%s.json" % nome)),
                        str(tmp / ("pote-%s.json" % nome))])
            motor = json.loads((tmp / ("motor-%s.json" % nome)).read_text(encoding="utf-8")) \
                if (tmp / ("motor-%s.json" % nome)).exists() else {}
            pote = json.loads((tmp / ("pote-%s.json" % nome)).read_text(encoding="utf-8")) \
                if (tmp / ("pote-%s.json" % nome)).exists() else {}
            res["MOTOR_" + nome.upper()] = {"CODIGO": m["CODIGO"], "ERRO": m["ERRO"][-600:],
                                            "ITEM": _do_item(motor)}
            res["POTE_" + nome.upper()] = {"CODIGO": p["CODIGO"], "ERRO": p["ERRO"][-600:],
                                           "SAIDA": p["SAIDA"][-600:],
                                           "ITEM_NO_POTE": [k for k, v in pote.items()
                                                            if ITEM in json.dumps(v, ensure_ascii=False)]}
            for f in ("motor-%s.json" % nome, "pote-%s.json" % nome, "export-%s.json" % nome):
                if (tmp / f).exists():
                    shutil.copy(tmp / f, saida / f.upper().replace(".JSON", ".json"))
        shutil.copy(tmp / "revisoes.json", saida / "REVISOES-SECO.json")
    finally:
        pg.descer()
        shutil.rmtree(tmp, ignore_errors=True)
    (saida / "ENSAIO-1149.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: res.get(k) for k in ("MIGRATIONS_PASS", "SECO", "BACKUP", "APLICAR_SEM_PARAR_FLAG",
                                              "APLICAR_1", "APLICAR_2", "VISTA_DEPOIS")},
                     ensure_ascii=False, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
