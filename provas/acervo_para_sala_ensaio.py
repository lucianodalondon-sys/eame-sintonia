#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACERVO-PARA-SALA — o REPROCESSO CANONICO do acervo fora da Sala, num ensaio. Nunca a Sala real.

    REPROCESSAR NAO E COLHER. Nenhum pedido a internet; nenhum gate relaxado.

Para as corridas que trouxeram os conteudos que estao fora da Sala e TEM texto (os que a Admissao julgou e os
que nunca foram perguntados), refaz-se a passagem pela MESMA porta da producao — como
`medidas/duas_portas_reprocessa.py` — numa copia de tudo:

    1  TEMPORARIO: um deposito do coletor (os bytes no RAW_PATH que o livro declara, sha256 conferido),
       um armazem (RAW e derivados no storage_path do banco, sha256 conferido) e um LIVRO REUNIDO:
       o livro do vivo + as linhas das mesmas corridas que so existem nos livros de outras pastas
    2  Postgres DESCARTAVEL restaurado do ultimo backup da Sala real (pg_dump -Fc do backup_sala.cmd)
    3  por corrida: `italy_executor.colher(run_id)` refaz o balcao a partir do livro, e
       `orquestrador.main(... --so-a-porta --colheita-da-corrida=RUN_ID --filtro fonte= --filtro universo=)`
       leva-o a porta. Quem escreve na Sala e `admissao/sala_de_espera.py`, SO depois de SIM.
    4  mede: linhas novas na Sala, por motivo de antes; e dessas, publicacao / data do facto / lugar do
       facto (valor, base, precisao)
    5  idempotencia: as primeiras N corridas outra vez -> Sala +0
    6  desliga o Postgres e apaga o temporario

    py provas/acervo_para_sala_ensaio.py --arvore <copia com o codigo> --dump <backup .dump>
        --dados <pasta com raw.json derivados.json> --motivos <MOTIVOS.json> --raizes "<r;r>"
        --livro-vivo <pasta do livro do vivo> --livros "<glob;glob>" --saida <out.json> [--limite N]
"""
import argparse
import collections
import glob
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
APELIDO = {"T1": "cultura", "T2": "clima", "T3": "praga", "T4": "regulatorio", "T5": "ciencia",
           "T6": "pesquisador", "T7": "cooperativa", "T8": "agricultor", "T9": "concorrente",
           "T10": "mercado", "T11": "evento", "T12": "politica", "T13": "distribuicao"}

UMA_CORRIDA = r'''
import os, sys, json
sys.path.insert(0, os.getcwd())
import _gavetas
from coleta import italy_executor as ix
b = ix.colher(sys.argv[1], ops_root=os.environ["ITALY_OPS_ROOT"], raiz=os.getcwd())
print("BALCAO", json.dumps({"OBS": b["OBSERVACOES_DESTA_CORRIDA"], "COM_BYTES": b["COM_BYTES_NO_ARMAZEM"]}))
import orquestrador as orq
sys.argv = ["orquestrador/orquestrador.py", sys.argv[2], "--so-a-porta",
            "--colheita-da-corrida=%s" % sys.argv[1], "--filtro", "fonte=%s" % sys.argv[3],
            "--filtro", "universo=%s" % sys.argv[4]]
try:
    rc = orq.main()
except SystemExit as e:
    rc = int(e.code or 0)
print("RC", rc)
'''


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for a in ("--arvore", "--dump", "--dados", "--motivos", "--raizes", "--livro-vivo", "--livros", "--saida"):
        ap.add_argument(a, required=True)
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--repetir", type=int, default=5)
    a = ap.parse_args()
    arvore = Path(a.arvore)
    # a copia da Sala real le-se com default_transaction_read_only; o Postgres DESCARTAVEL nao pode herdar isso
    # (o CREATE DATABASE falha) nem a senha da Sala real
    for v in ("PGOPTIONS", "PGPASSFILE", "PGHOST", "PGPORT", "PGDATABASE", "PGUSER"):
        os.environ.pop(v, None)
    spec = importlib.util.spec_from_file_location("ensaio_offline", arvore / "scripts" / "micro_coleta" / "ensaio_offline.py")
    E = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(E)

    ler = lambda n: json.load(open(os.path.join(a.dados, n), encoding="utf-8"))
    raws, ders = ler("raw.json"), ler("derivados.json")
    mot = json.load(open(a.motivos, encoding="utf-8"))
    raizes = [x for x in a.raizes.split(";") if x]
    alvo_itens = [x for x in mot["ITENS"] if x["MOTIVO"].startswith(("NUNCA_PERGUNTADO", "ADMISSAO"))]
    grupo = lambda x: ("NUNCA_PERGUNTADO:" + ("YOUTUBE" if "YOUTUBE" in x["MARCAS"] else "OUTROS")) \
        if x["MOTIVO"].startswith("NUNCA") else ":".join(x["MOTIVO"].split(":")[:2])
    grupo_do_sha = {x["SHA256"]: grupo(x) for x in alvo_itens}
    # as corridas a reprocessar: as do banco (raw_asset.run_id) E as do LIVRO onde a impressao digital do
    # conteudo aparece — o mesmo conteudo foi muitas vezes colhido de novo por uma corrida mais recente, e e
    # essa que o livro conhece (medido: 59 corridas do banco nao tem linha em livro nenhum)
    run_por_sha = collections.defaultdict(set)
    fonte_por_run = {}
    for padrao in a.livros.split(";"):
        if "observations" not in padrao:
            continue
        for f in sorted(glob.glob(padrao)):
            for l in open(f, encoding="utf-8", errors="replace"):
                try:
                    o = json.loads(l)
                except ValueError:
                    continue
                if isinstance(o, dict) and o.get("RAW_SHA256") and o.get("RUN_ID"):
                    run_por_sha[str(o["RAW_SHA256"]).strip()].add(o["RUN_ID"])
                    fonte_por_run.setdefault(o["RUN_ID"], o.get("SOURCE_ID"))
    corridas = collections.OrderedDict()
    for x in sorted(alvo_itens, key=lambda x: x["RUN_IDS"][0]):
        for r in sorted(set(x["RUN_IDS"]) | run_por_sha.get(x["SHA256"], set())):
            corridas.setdefault(r, {"RUN_ID": r, "FONTE": fonte_por_run.get(r) or x["SOURCE_ID"],
                                    "UNIVERSO": r.split("-")[1]})
    lista = list(corridas.values())[:a.limite or None]
    runs_alvo = {c["RUN_ID"] for c in lista}

    fora = {"ARVORE": str(arvore), "ARVORE_HEAD": subprocess.run(["git", "-C", str(arvore), "log", "--format=%H %s", "-1"],
                                                                  capture_output=True, text=True).stdout.strip(),
            "DUMP": a.dump, "DUMP_SHA256": sha(open(a.dump, "rb").read()),
            "CORRIDAS": len(lista), "ITENS_ALVO": len(alvo_itens), "PASSOS": {}}
    T = Path(tempfile.mkdtemp(prefix="aps-"))
    # como no vivo: o livro e o deposito do coletor vivem DENTRO da arvore (OPS_ROOT = a arvore), e o
    # ingresso le os bytes em <arvore>/<STORAGE_LOCATION>. So a copia local de ensaio e escrita.
    ops, arm = arvore, T / "armazem"
    try:
        # ── 1 · o livro reunido, o deposito do coletor e o armazem, todos com sha conferido ──
        dl = ops / "data" / "collection-ledger" / "italy"
        dl.mkdir(parents=True, exist_ok=True)
        livro_info = {}
        for nome in ("observations.ndjson", "runs.ndjson"):
            vivo = open(os.path.join(a.livro_vivo, nome), encoding="utf-8", errors="replace").read().splitlines()
            ja = set(vivo)
            ids_vivo = set()
            for l in vivo:
                try:
                    ids_vivo.add(json.loads(l).get("RUN_ID"))
                except ValueError:
                    pass
            extra = []
            # ⚠️ SO O LIVRO DO MESMO NOME. A v2 juntava os dois: os recibos de corrida (runs.ndjson,
            # sem SOURCE_ID) entravam no livro de observacoes, cada corrida ganhava uma unidade sem
            # fonte e a porta recusava o envelope inteiro — 178 corridas «ENVELOPE_INVALIDO» que
            # eram defeito DESTE ensaio, nao do robo (medido em ACERVO-PARA-SALA-2).
            for padrao in a.livros.split(";"):
                if os.path.basename(padrao.replace("\\", "/")) != nome:
                    continue
                for f in sorted(glob.glob(padrao)):
                    for l in open(f, encoding="utf-8", errors="replace"):
                        l = l.rstrip("\n")
                        try:
                            o = json.loads(l)
                        except ValueError:
                            continue
                        if o.get("RUN_ID") in runs_alvo and o.get("RUN_ID") not in ids_vivo and l not in ja:
                            ja.add(l)
                            extra.append(l)
            with open(dl / nome, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(vivo + extra) + "\n")
            livro_info[nome] = {"DO_VIVO": len(vivo), "DE_OUTRAS_PASTAS": len(extra)}
        fora["PASSOS"]["1_LIVRO_REUNIDO"] = livro_info

        onde = {}                                     # sha -> bytes achados
        def bytes_de(s, caminhos):
            if s in onde:
                return onde[s]
            for c in caminhos:
                for r in raizes:
                    try:
                        b = open(os.path.join(r, c), "rb").read()
                    except OSError:
                        continue
                    if sha(b) == s:
                        onde[s] = b
                        return b
            return None
        caminhos_por_sha = collections.defaultdict(list)
        for r in raws:
            caminhos_por_sha[r["sha256"].strip()].append(r["storage_path"])
        for d in ders:
            caminhos_por_sha[(d["sha256"] or "").strip()].append(d["storage_path"])
        dep = collections.Counter()
        for l in open(dl / "observations.ndjson", encoding="utf-8"):
            try:
                o = json.loads(l)
            except ValueError:
                continue
            if o.get("RUN_ID") not in runs_alvo or not o.get("RAW_PATH"):
                continue
            s = str(o.get("RAW_SHA256") or "").strip()
            b = bytes_de(s, caminhos_por_sha.get(s, []))
            destino = ops / o["RAW_PATH"].lstrip("./").replace("\\", "/")
            if b is None:
                dep["SEM_BYTES"] += 1
                continue
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(b)
            dep["NO_DEPOSITO"] += 1
        raws_alvo = [r for r in raws if r["run_id"] in runs_alvo]
        ids_alvo = {r["id"] for r in raws_alvo}
        for x in raws_alvo + [d for d in ders if d["raw_asset_id"] in ids_alvo]:
            s = (x["sha256"] or "").strip()
            b = bytes_de(s, caminhos_por_sha.get(s, []))
            if b is None:
                dep["ARMAZEM_SEM_BYTES"] += 1
                continue
            p = arm / x["storage_path"]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b)
            dep["NO_ARMAZEM"] += 1
        fora["PASSOS"]["1_BYTES"] = dict(dep)

        # ── 2 · a copia da Sala num Postgres descartavel ──
        base = E.Base(T / "pg")
        assert ":54330/" not in base.url, "isto e a Sala real"
        subprocess.run([base.exe("initdb"), "-D", str(base.pasta), "-U", "postgres", "--auth=trust", "-E", "UTF8",
                        "--no-sync"], check=True, capture_output=True)
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
            sala_antes = set(psql("select item_id from sala_de_espera").split("\n")) - {""}
            fora["PASSOS"]["2_COPIA"] = {"RESTAURO": r.returncode, "ERRO": r.stderr[-300:],
                                         "SALA_ANTES": len(sala_antes), "RAW": psql("select count(*) from raw_asset"),
                                         "MIGRACAO": psql("select max(versao) from schema_migracao")}

            env = {**os.environ, "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_SALA_DSN": base.url,
                   "SINTONIA_COLLECTION_DSN": base.url, "ITALY_OPS_ROOT": str(ops), "SINTONIA_ARMAZEM_RAIZ": str(arm),
                   "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", ""), "SINTONIA_PSQL_EXE": base.exe("psql"),
                   "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1",
                   "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9", "ALL_PROXY": "http://127.0.0.1:9"}
            for v in ("SUPABASE_DB_URL", "BANCO_DESCARTAVEL_URL"):
                env.pop(v, None)

            def passar(c):
                t0 = time.time()
                x = subprocess.run([sys.executable, "-B", "-c", UMA_CORRIDA, c["RUN_ID"], APELIDO.get(c["UNIVERSO"], "mercado"),
                                    c["FONTE"], c["UNIVERSO"]], cwd=str(arvore), env=env, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=600)
                bal = next((json.loads(l[7:]) for l in x.stdout.splitlines() if l.startswith("BALCAO ")), None)
                rc = next((l[3:] for l in x.stdout.splitlines() if l.startswith("RC ")), None)
                return {"RUN_ID": c["RUN_ID"], "FONTE": c["FONTE"], "UNIVERSO": c["UNIVERSO"], "BALCAO": bal, "RC": rc,
                        "EXIT": x.returncode, "SEG": round(time.time() - t0, 1),
                        "ERRO": (x.stderr.strip().splitlines() or [""])[-1][:240],
                        "SAIDA_FIM": [l[:200] for l in x.stdout.strip().splitlines()[-12:]]}

            # ── 3 · cada corrida pela porta ──
            passagens = [passar(c) for c in lista]
            fora["PASSOS"]["3_PASSAGENS"] = {"TOTAL": len(passagens),
                                             "RC": dict(collections.Counter(str(p["RC"]) for p in passagens)),
                                             "EXIT": dict(collections.Counter(p["EXIT"] for p in passagens)),
                                             "SEGUNDOS": round(sum(p["SEG"] for p in passagens)),
                                             "ERROS_MAIS_COMUNS": dict(collections.Counter(p["ERRO"] for p in passagens
                                                                                           if p["EXIT"]).most_common(8))}
            fora["PASSAGENS"] = passagens

            # ── 4 · o que entrou ──
            cols = ("item_id, source_id, universo, published_at, published_at_basis, fact_time, fact_time_basis, "
                    "fact_location, fact_location_basis, coalesce(tempo_lugar_evidencia::text, '')")
            novas = []
            for l in psql("select %s from sala_de_espera_atual" % cols).split("\n"):
                c = l.split("\t")
                if not l or c[0] in sala_antes:
                    continue
                ev = {}
                try:
                    ev = json.loads(c[9]) if c[9] else {}
                except ValueError:
                    pass
                novas.append({"ITEM_ID": c[0], "SOURCE_ID": c[1], "UNIVERSO": c[2], "PUBLISHED_AT": c[3],
                              "PUBLISHED_AT_BASIS": c[4][:160], "FACT_TIME": c[5], "FACT_TIME_BASIS": c[6][:200],
                              "FACT_LOCATION": c[7], "FACT_LOCATION_BASIS": c[8][:200],
                              "FACT_TIME_PRECISION": ev.get("FACT_TIME_PRECISION"),
                              "FACT_LOCATION_PRECISION": ev.get("FACT_LOCATION_PRECISION"),
                              "PUBLISHED_AT_PRECISION": ev.get("PUBLISHED_AT_PRECISION")})
            der_sha = {}
            for d in ders:
                der_sha[d["id"]] = next((r["sha256"].strip() for r in raws if r["id"] == d["raw_asset_id"]), None)
            for n in novas:
                try:
                    n["GRUPO_DE_ANTES"] = grupo_do_sha.get(der_sha.get(int(n["ITEM_ID"].split(":")[1])), "NOVO_DERIVADO")
                except (ValueError, IndexError):
                    n["GRUPO_DE_ANTES"] = "?"
            ns = ("NAO SEI", "", None)
            fora["PASSOS"]["4_SALA"] = {
                "SALA_DEPOIS": len(sala_antes) + len(novas), "NOVAS": len(novas),
                "POR_GRUPO_DE_ANTES": dict(collections.Counter(n["GRUPO_DE_ANTES"] for n in novas).most_common()),
                "COM_PUBLICACAO": sum(n["PUBLISHED_AT"] not in ns for n in novas),
                "COM_DATA_DO_FATO": sum(n["FACT_TIME"] not in ns for n in novas),
                "COM_LUGAR_DO_FATO": sum(n["FACT_LOCATION"] not in ns for n in novas),
                "POR_UNIVERSO": dict(collections.Counter(n["UNIVERSO"] for n in novas).most_common())}
            fora["NOVAS"] = novas
            fora["PASSOS"]["4_ADMISSAO_NO_BANCO"] = psql(
                "select coalesce(string_agg(etapa||'='||n, ' '), '') from (select etapa, count(*) n from etapa_da_corrida "
                "where run_id in (select run_id from etapa_da_corrida group by run_id) and criada_em > now() - interval '1 day' "
                "group by etapa) x")

            # ── 5 · idempotencia ──
            antes = int(psql("select count(*) from sala_de_espera"))
            rep = [passar(c) for c in lista[:a.repetir]]
            fora["PASSOS"]["5_OUTRA_VEZ"] = {"CORRIDAS": len(rep), "SALA_ANTES": antes,
                                             "SALA_DEPOIS": int(psql("select count(*) from sala_de_espera"))}
        finally:
            base.descer()
    finally:
        shutil.rmtree(T, ignore_errors=True)
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps(fora["PASSOS"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
