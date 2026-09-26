#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACERVO-PARA-SALA-2 — traz para a arvore do vivo o LIVRO e os BYTES das corridas de um lote. So o coordenador aplica.

MEDIDO (26/09): das 18 corridas que dao os 12 itens novos no ensaio, 16 NAO tem linha no livro do vivo
(`data/collection-ledger/italy/observations.ndjson`) nem bytes no deposito dele — vivem nos livros de outras
pastas desta maquina. Sem elas, `italy_executor.colher(RUN_ID)` no vivo da balcao vazio e so entram 5 dos 12.

O que faz, por corrida da lista:
  1  linhas de `observations.ndjson` e `runs.ndjson` dessa corrida que existem noutros livros e NAO no do vivo
     (texto da linha igual = ja la esta; o livro e append-only: so se ACRESCENTA, nunca se reescreve)
  2  os bytes de cada `RAW_PATH` dessas linhas, achados nas raizes com o sha256 CONFERIDO contra `RAW_SHA256`;
     um ficheiro que ja existe no vivo com OUTRO conteudo PARA tudo (nao se escreve por cima)

Sem `--aplicar` so conta e mostra. Com `--aplicar` exige `PARAR.flag` ausente e escreve um recibo.

    py scripts/acervo_para_sala/trazer_livro.py --arvore <vivo> --lista LOTE-12-ITENS.json \\
        --livros "<glob;glob>" --raizes "<r;r>" [--dados <pasta com raw.json>] [--aplicar] [--recibo out.json]
"""
import argparse
import glob
import hashlib
import json
import os
import sys


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for x in ("--arvore", "--lista", "--livros", "--raizes"):
        ap.add_argument(x, required=True)
    # opcional: o raw.json da Sala (so leitura) — o mesmo conteudo pode estar guardado no armazem com OUTRO
    # caminho (`storage_path`); procura-se tambem la, pelo sha256
    ap.add_argument("--dados", default="")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--recibo", default="")
    a = ap.parse_args()
    arv = os.path.abspath(a.arvore)
    dl = os.path.join(arv, "data", "collection-ledger", "italy")
    runs = {c["RUN_ID"] for c in json.load(open(a.lista, encoding="utf-8"))["CORRIDAS"]}
    raizes = [x for x in a.raizes.split(";") if x]
    outros = {}
    if a.dados:
        for r in json.load(open(os.path.join(a.dados, "raw.json"), encoding="utf-8")):
            outros.setdefault(r["sha256"].strip(), []).append(r["storage_path"])
    plano = {"observations.ndjson": [], "runs.ndjson": []}
    for nome in plano:
        vivo = os.path.join(dl, nome)
        ja = set(open(vivo, encoding="utf-8", errors="replace").read().splitlines()) if os.path.isfile(vivo) else set()
        for padrao in a.livros.split(";"):
            if os.path.basename(padrao.replace("\\", "/")) != nome:
                continue
            for f in sorted(glob.glob(padrao)):
                if os.path.abspath(f) == os.path.abspath(vivo):
                    continue
                for l in open(f, encoding="utf-8", errors="replace"):
                    l = l.rstrip("\r\n")
                    try:
                        o = json.loads(l)
                    except ValueError:
                        continue
                    if isinstance(o, dict) and o.get("RUN_ID") in runs and l not in ja:
                        ja.add(l)
                        plano[nome].append(l)
    bytes_plano, sem, conflito = [], [], []
    for l in plano["observations.ndjson"]:
        o = json.loads(l)
        if not o.get("RAW_PATH"):
            continue
        rel = o["RAW_PATH"].lstrip("./").replace("\\", "/")
        esperado = str(o.get("RAW_SHA256") or "").strip()
        destino = os.path.join(arv, rel)
        if rel in {x for x, _ in bytes_plano}:        # o mesmo ficheiro em varias linhas: copia-se uma vez
            continue
        if os.path.isfile(destino):
            if sha(open(destino, "rb").read()) != esperado:
                conflito.append(rel)
            continue
        achado = None
        for c in [rel] + outros.get(esperado, []):
            for r in raizes:
                p = os.path.join(r, c)
                if os.path.isfile(p) and sha(open(p, "rb").read()) == esperado:
                    achado = p
                    break
            if achado:
                break
        (bytes_plano.append((rel, achado)) if achado else sem.append(rel))
    por_run = {r: sum(1 for l in plano["observations.ndjson"] if json.loads(l).get("RUN_ID") == r) for r in sorted(runs)}
    fora = {"ARVORE": arv, "APLICAR": a.aplicar,
            "LINHAS_A_ACRESCENTAR": {k: len(v) for k, v in plano.items()},
            "OBSERVACOES_POR_CORRIDA": por_run,
            "BYTES_A_COPIAR": len(bytes_plano), "BYTES_NAO_ACHADOS": sem, "CONFLITOS": conflito}
    print(json.dumps(fora, ensure_ascii=False, indent=1))
    if conflito:
        print("PARADO: ha ficheiros no vivo com outro conteudo; nada se escreve por cima.")
        return 2
    if not a.aplicar:
        print("(so contado; nada escrito — --aplicar e do coordenador)")
        return 0
    if os.path.exists(os.path.join(arv, "PARAR.flag")):
        print("PARADO: PARAR.flag presente")
        return 2
    for rel, origem in bytes_plano:
        destino = os.path.join(arv, rel)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        b = open(origem, "rb").read()
        with open(destino, "xb") as fh:                       # "x": nunca por cima
            fh.write(b)
    for nome, linhas in plano.items():
        if linhas:
            with open(os.path.join(dl, nome), "a", encoding="utf-8", newline="\n") as fh:
                fh.write("".join(l + "\n" for l in linhas))
    if a.recibo:
        with open(a.recibo, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({**fora, "LINHAS": plano, "BYTES": [r for r, _ in bytes_plano]}, fh, ensure_ascii=False, indent=1)
    print("APLICADO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
