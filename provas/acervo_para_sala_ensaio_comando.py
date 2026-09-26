#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACERVO-PARA-SALA-3 — o ENSAIO DO COMANDO EXACTO que o coordenador vai correr no vivo. Nunca o vivo, nunca a Sala.

O ensaio antigo (`acervo_para_sala_ensaio.py`) junta os livros de TODAS as pastas e corre a porta por dentro:
mede o que o acervo daria. Este mede outra coisa — o que os DOIS COMANDOS do roteiro dao, tal como estao
escritos, partindo do estado do vivo de hoje:

    1  COPIA: uma arvore de ensaio (`--arvore`, worktree do ramo a instalar) recebe o LIVRO DO VIVO tal como
       esta (so observations/runs) e, do deposito do vivo, os bytes das corridas da lista que o vivo JA tem;
       um armazem temporario com os RAW e derivados que a copia da Sala referencia (sha256 conferido);
       Postgres DESCARTAVEL restaurado de um `pg_dump` so-leitura da Sala real; `PARAR.flag` na arvore.
    2  os comandos, com a DSN/armazem apontados para a copia:
         trazer_livro.py (so conta) · trazer_livro.py --aplicar · outra vez --aplicar (tem de dar 0)
         reprocessar_lote.py (so confere) · reprocessar_lote.py --aplicar · outra vez --aplicar (Sala +0)
    3  mede: linhas novas na Sala (publicacao, data e lugar do facto, texto para medir a cultura depois);
       decisoes acrescentadas ao livro da porta
    4  desliga o Postgres e apaga o temporario

    py provas/acervo_para_sala_ensaio_comando.py --arvore <worktree de ensaio> --vivo <arvore do vivo, so leitura>
        --dump <sala.dump> --lista <LOTE.json> --livros "<glob;glob>" --raizes "<r;r>" --dados <pasta com raw.json>
        --saida <out.json>
"""
import argparse
import collections
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIVRO_COLETOR = Path("data") / "collection-ledger" / "italy"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for x in ("--arvore", "--vivo", "--dump", "--lista", "--livros", "--raizes", "--dados", "--saida"):
        ap.add_argument(x, required=True)
    a = ap.parse_args()
    arv, vivo = Path(a.arvore).resolve(), Path(a.vivo).resolve()
    assert arv != vivo and "source-curator-service" not in str(arv), "a arvore de ensaio nao pode ser o vivo"
    for v in ("PGOPTIONS", "PGPASSFILE", "PGHOST", "PGPORT", "PGDATABASE", "PGUSER"):
        os.environ.pop(v, None)
    spec = importlib.util.spec_from_file_location("ensaio_offline", RAIZ / "scripts" / "micro_coleta" / "ensaio_offline.py")
    E = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(E)
    lista = json.load(open(a.lista, encoding="utf-8"))["CORRIDAS"]
    runs = {c["RUN_ID"] for c in lista}
    raizes = [x for x in a.raizes.split(";") if x]
    fora = {"ARVORE": str(arv), "ARVORE_HEAD": subprocess.run(["git", "-C", str(arv), "log", "--format=%H %s", "-1"],
                                                               capture_output=True, text=True).stdout.strip(),
            "VIVO_HEAD": subprocess.run(["git", "-C", str(vivo), "log", "--format=%H", "-1"],
                                        capture_output=True, text=True).stdout.strip(),
            "DUMP_SHA256": sha(open(a.dump, "rb").read()), "LISTA": a.lista, "CORRIDAS": len(lista), "PASSOS": {}}

    # ── 1 · a arvore recebe o livro do vivo tal como esta, e os bytes que o vivo ja tem ──
    for nome in ("observations.ndjson", "runs.ndjson"):
        shutil.copyfile(vivo / LIVRO_COLETOR / nome, arv / LIVRO_COLETOR / nome)
    dep = collections.Counter()
    for l in open(arv / LIVRO_COLETOR / "observations.ndjson", encoding="utf-8", errors="replace"):
        try:
            o = json.loads(l)
        except ValueError:
            continue
        if o.get("RUN_ID") not in runs or not o.get("RAW_PATH"):
            continue
        rel = o["RAW_PATH"].lstrip("./").replace("\\", "/")
        origem, destino = vivo / rel, arv / rel
        if destino.exists():
            dep["JA_NA_ARVORE"] += 1
        elif origem.is_file() and sha(origem.read_bytes()) == str(o.get("RAW_SHA256") or "").strip():
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origem, destino)
            dep["COPIADO_DO_VIVO"] += 1
        else:
            dep["NAO_ESTA_NO_VIVO"] += 1
    (arv / "PARAR.flag").write_text("ensaio ACERVO-PARA-SALA-3\n", encoding="utf-8")
    fora["PASSOS"]["1_ARVORE"] = {"LIVRO_DO_VIVO_LINHAS": sum(1 for _ in open(arv / LIVRO_COLETOR / "observations.ndjson",
                                                                              encoding="utf-8", errors="replace")),
                                  "DEPOSITO": dict(dep)}
    livro_porta = arv / "data" / "samples" / "LIVRO-DE-DECISOES.json"
    decisoes_antes = len(json.load(open(livro_porta, encoding="utf-8"))["DECISOES"])

    T = Path(tempfile.mkdtemp(prefix="aps3-"))
    arm = T / "armazem"
    base = E.Base(T / "pg")
    assert ":54330/" not in base.url, "isto e a Sala real"
    subprocess.run([base.exe("initdb"), "-D", str(base.pasta), "-U", "postgres", "--auth=trust", "-E", "UTF8", "--no-sync"],
                   check=True, capture_output=True)
    subprocess.run([base.exe("pg_ctl"), "-D", str(base.pasta), "-o", f"-p {base.porto} -h 127.0.0.1", "-l",
                    str(base.pasta / "servidor.log"), "-w", "start"], check=True, stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        subprocess.run([base.exe("psql"), "-X", "-q", "-c", "create database sala_italia;",
                        f"postgresql://postgres@127.0.0.1:{base.porto}/postgres"], check=True, capture_output=True)
        r = subprocess.run([base.exe("pg_restore"), "--no-owner", "--no-privileges", "-d", base.url, a.dump],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")

        def psql(q):
            x = subprocess.run([base.exe("psql"), "-X", "-q", "-A", "-t", "-F", "\t", "-v", "ON_ERROR_STOP=1",
                                "-c", q, base.url], capture_output=True, text=True, encoding="utf-8")
            if x.returncode:
                raise SystemExit("psql: " + x.stderr)
            return x.stdout.strip()

        # o armazem da copia: tudo o que a copia da Sala referencia, com sha256 conferido
        am = collections.Counter()
        for linha in psql("select storage_path, sha256 from raw_asset union all "
                          "select storage_path, sha256 from derived_artifact").split("\n"):
            if "\t" not in linha:
                continue
            caminho, s = linha.split("\t")
            destino = arm / caminho
            if destino.exists():
                continue
            for R in raizes:
                p = Path(R) / caminho
                if p.is_file() and sha(p.read_bytes()) == s.strip():
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(p, destino)
                    am["COPIADO"] += 1
                    break
            else:
                am["NAO_ACHADO"] += 1
        sala_antes = set(psql("select item_id from sala_de_espera").split("\n")) - {""}
        fora["PASSOS"]["2_COPIA"] = {"RESTAURO": r.returncode, "ERRO": r.stderr[-300:], "ARMAZEM": dict(am),
                                     "SALA_ANTES_ITENS": len(sala_antes),
                                     "SALA_ANTES_LINHAS": psql("select count(*) from sala_de_espera"),
                                     "MIGRACAO": psql("select max(versao) from schema_migracao")}

        env = {**os.environ, "SINTONIA_SALA_DSN": base.url, "SINTONIA_COLLECTION_DSN": base.url,
               "SINTONIA_ARMAZEM_RAIZ": str(arm), "SINTONIA_PSQL_EXE": base.exe("psql"),
               "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", ""), "PYTHONUTF8": "1",
               "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9", "ALL_PROXY": "http://127.0.0.1:9"}
        for v in ("SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL"):
            env.pop(v, None)

        # ── 2 · OS COMANDOS DO ROTEIRO, tal como estao escritos (so a --arvore e a da copia) ──
        trazer = [sys.executable, "-B", str(RAIZ / "scripts" / "acervo_para_sala" / "trazer_livro.py"),
                  "--arvore", str(arv), "--lista", a.lista, "--dados", a.dados, "--livros", a.livros,
                  "--raizes", a.raizes]
        reproc = [sys.executable, "-B", str(RAIZ / "scripts" / "acervo_para_sala" / "reprocessar_lote.py"),
                  "--arvore", str(arv), "--lista", a.lista]

        def correr(nome, cmd):
            t0 = time.time()
            x = subprocess.run(cmd, cwd=str(RAIZ), env=env, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=7200)
            fora["PASSOS"][nome] = {"CODIGO": x.returncode, "SEG": round(time.time() - t0, 1),
                                    "SAIDA_FIM": [l[:220] for l in x.stdout.strip().splitlines()[-14:]],
                                    "ERRO_FIM": x.stderr.strip()[-400:]}
            print(nome, x.returncode, flush=True)

        correr("3a_TRAZER_SO_CONTA", trazer)
        correr("3b_TRAZER_APLICAR", trazer + ["--aplicar", "--recibo", str(T / "trazer.json")])
        correr("3c_TRAZER_OUTRA_VEZ", trazer + ["--aplicar"])
        correr("4a_REPROCESSAR_SO_CONFERE", reproc)
        correr("4b_REPROCESSAR_APLICAR", reproc + ["--aplicar", "--saida", str(T / "recibo-1.json")])
        linhas_depois_1 = psql("select count(*) from sala_de_espera")
        correr("4c_REPROCESSAR_OUTRA_VEZ", reproc + ["--aplicar", "--saida", str(T / "recibo-2.json")])
        fora["PASSOS"]["5_IDEMPOTENCIA"] = {"LINHAS_DEPOIS_1": linhas_depois_1,
                                            "LINHAS_DEPOIS_2": psql("select count(*) from sala_de_espera")}
        for n_, f_ in (("RECIBO_1", "recibo-1.json"), ("RECIBO_2", "recibo-2.json")):
            if (T / f_).exists():
                rc = json.load(open(T / f_, encoding="utf-8"))
                fora[n_] = {"SALA_ANTES": rc.get("SALA_ANTES"), "SALA_DEPOIS": rc.get("SALA_DEPOIS"),
                            "EXIT": dict(collections.Counter(str(c["EXIT"]) for c in rc["CORRIDAS"])),
                            "ERROS": [c["ERRO"] for c in rc["CORRIDAS"] if c["EXIT"]][:5]}

        # ── 3 · o que entrou ──
        cols = ", ".join("translate(coalesce(%s::text, ''), chr(9) || chr(10) || chr(13), '   ')" % c for c in (
            "item_id", "source_id", "universo", "published_at", "fact_time", "fact_location", "raw_observation_id",
            "admitido_por", "texto"))
        novas = []
        for l in psql("select %s from sala_de_espera_atual" % cols).split("\n"):
            c = l.split("\t")
            if not l or c[0] in sala_antes:
                continue
            novas.append({"ITEM_ID": c[0], "SOURCE_ID": c[1], "UNIVERSO": c[2], "PUBLISHED_AT": c[3],
                          "FACT_TIME": c[4], "FACT_LOCATION": c[5], "RAW_OBSERVATION_ID": c[6],
                          "ADMITIDO_POR": c[7][:200], "TEXTO": c[8]})
        ns = ("NAO SEI", "", None)
        dec = json.load(open(livro_porta, encoding="utf-8"))["DECISOES"][decisoes_antes:]
        video = [d for d in dec if "youtube.com/watch" in json.dumps(d.get("evidencia") or {})]
        fora["PASSOS"]["6_SALA"] = {
            "NOVAS": len(novas),
            "POR_UNIVERSO": dict(collections.Counter(n["UNIVERSO"] for n in novas)),
            "POR_FONTE": dict(collections.Counter(n["SOURCE_ID"] for n in novas)),
            "COM_PUBLICACAO": sum(n["PUBLISHED_AT"] not in ns for n in novas),
            "COM_DATA_DO_FATO": sum(n["FACT_TIME"] not in ns for n in novas),
            "COM_LUGAR_DO_FATO": sum(n["FACT_LOCATION"] not in ns for n in novas),
            "DECISOES_ACRESCENTADAS": len(dec),
            "DECISOES_DE_VIDEO": dict(collections.Counter(d["resultado"] for d in video)),
            "VIDEO_POR_MOTIVO": dict(collections.Counter("%s %s: %s" % (d["universo"], d["resultado"],
                                                                        str(d.get("motivo"))[:70])
                                                         for d in video).most_common(12))}
        fora["NOVAS"] = novas
        fora["DECISOES"] = dec
    finally:
        base.descer()
        shutil.rmtree(T, ignore_errors=True)
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps(fora["PASSOS"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
