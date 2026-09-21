#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A COORTE DA MICRO-COLLECTION — e so ela.

⛔ O ERRO QUE ESTE FICHEIRO EXISTE PARA NAO REPETIR
----------------------------------------------------
O censo anterior (`medidas/ultima_milha.py`) mediu o UNIVERSO:

    OBSERVATIONS_TOTAL 445 · BYTES_PRESENT 205 · COM_RAW_ASSET 9

Esses numeros sao de **58 corridas desde 14-09**. Nao sao a micro-Collection,
e `205` nao sao «205 dos 85». Citar o universo onde se pede a coorte faz o
relatorio parecer maior do que a coisa medida.

    O UNIVERSO NAO E A COORTE.
    UM NUMERO SEM POPULACAO NOMEADA NAO E UMA MEDIDA.

DE ONDE VEM A COORTE
--------------------
NAO de inferencia por hora do RUN_ID. Vem dos MANIFESTOS que as corridas
deixaram escritos — `medidas/CORRIDA-CANONICA-RUN*.json` — onde cada corrida
declara, fonte a fonte, o `RUN_ID` que cunhou. O manifesto e o dono da
resposta «que corridas sao estas»; o relogio e so um palpite.

O QUE ESTE MEDIDOR NAO FAZ
--------------------------
Nao vai a rede. Nao escreve no livro. Nao promove nada. Nao INVENTA ligacao:
um ficheiro cujo conteudo nao case com nenhum sha do livro fica `UNMATCHED`,
e UNMATCHED e uma resposta — nao um convite a adivinhar.

SAIDA: medidas/COORTE-MICRO-COLLECTION-V1.json
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter, OrderedDict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVRO = os.path.join(RAIZ, "data", "collection-ledger", "italy", "observations.ndjson")
ARMAZEM = os.path.join(RAIZ, "data", "collection-store", "italy")
SAIDA = os.path.join(RAIZ, "medidas", "COORTE-MICRO-COLLECTION-V1.json")

#: As corridas da micro-Collection, na ordem em que aconteceram. Os nomes sao
#: os dos manifestos; os RUN_ID saem de dentro deles.
MANIFESTOS = ["RUN1", "RUN1B", "RUN1C", "RUN2"]

RESULTADOS_COM_DOCUMENTO = {
    "BASELINE_DOCUMENT", "NEW_DOCUMENT", "DOCUMENT_CHANGED_IN_PLACE",
    "SEMANTIC_ID_CHANGED_SAME_BYTES", "SEEN_AGAIN",
}


def sha_do_ficheiro(caminho, bloco=1 << 20):
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for p in iter(lambda: fh.read(bloco), b""):
            h.update(p)
    return h.hexdigest()


def ler_livro():
    with open(LIVRO, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def corridas_dos_manifestos():
    """`{nome_da_corrida: {RUN_ID, ...}}`, lido do que cada corrida declarou."""
    fora = OrderedDict()
    for nome in MANIFESTOS:
        p = os.path.join(RAIZ, "medidas", "CORRIDA-CANONICA-%s.json" % nome)
        if not os.path.isfile(p):
            fora[nome] = {"RUN_IDS": [], "AUSENTE": True}
            continue
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        ids, fontes = [], []
        for f in d.get("FONTES") or []:
            if f.get("RUN_ID"):
                ids.append(f["RUN_ID"])
                fontes.append(f.get("SOURCE_ID"))
        fora[nome] = {
            "RUN_IDS": ids,
            "SOURCE_IDS": fontes,
            "COMECOU_EM": d.get("COMECOU_EM"),
            "REDE_REAL": d.get("REDE_REAL"),
            "OBSERVACOES_NOVAS_DECLARADAS": d.get("OBSERVACOES_NOVAS_TOTAL"),
            "AUSENTE": False,
        }
    return fora


def observation_id(o):
    """A IDENTIDADE DE UMA OBSERVACAO, e nao um numero inventado.

    ⚠️ O livro NAO tem campo `OBSERVATION_ID`. Em vez de cunhar um agora — o
    que criaria uma identidade que so existe neste relatorio e que ninguem
    mais reconhece — declara-se a CHAVE COMPOSTA que ja identifica a linha:

        (RUN_ID, SOURCE_URL)   uma visita, a um endereco, numa corrida

    E escreve-se com prefixo `obs:` para que se leia como o que e. `sha256`
    nao serve: identifica BYTES, e a mesma observacao pode reaparecer.
    `DOCUMENT_ID` tambem nao: e o documento, nao a visita.
    """
    return "obs:%s|%s" % (o.get("RUN_ID"), o.get("SOURCE_URL") or o.get("DOCUMENT_ID") or "")


def caminho_local(o):
    rp = o.get("RAW_PATH")
    if not rp:
        return None
    return os.path.normpath(os.path.join(RAIZ, rp.lstrip("./").lstrip(".\\")))


def medir():
    livro = ler_livro()
    corridas = corridas_dos_manifestos()
    por_run = {}
    for o in livro:
        por_run.setdefault(o.get("RUN_ID"), []).append(o)

    # ── o eixo do banco, lido UMA vez (so leitura) ──────────────────────────
    banco = eixo_do_banco([o.get("RAW_SHA256") for o in livro])

    # ── FASE A · a coorte, corrida a corrida ───────────────────────────────
    fases_a, itens = OrderedDict(), []
    for nome, info in corridas.items():
        linhas = []
        for rid in info["RUN_IDS"]:
            for o in por_run.get(rid, []):
                local = caminho_local(o)
                existe = bool(local and os.path.isfile(local))
                sha_disco = sha_do_ficheiro(local) if existe else None
                sha_livro = o.get("RAW_SHA256")
                b = (banco or {}).get(sha_livro) if sha_livro else None
                linha = {
                    "CORRIDA": nome,
                    "RUN_ID": o.get("RUN_ID"),
                    "OBSERVATION_ID": observation_id(o),
                    "SOURCE_ID": o.get("SOURCE_ID"),
                    "DOCUMENT_ID": o.get("DOCUMENT_ID"),
                    "DETAIL_URL": o.get("SOURCE_URL"),
                    "OBSERVATION_RESULT": o.get("OBSERVATION_RESULT"),
                    "LOCAL_FILE": (os.path.relpath(local, RAIZ).replace("\\", "/")
                                   if existe else None),
                    "BYTES": o.get("BYTES"),
                    "SHA256": sha_livro,
                    "SHA256_DO_DISCO": sha_disco,
                    # ⚠️ SHA_MISMATCH e coisa diferente de ficheiro em falta.
                    # O que falta sabe-se que falta; o trocado passa por bom.
                    "SHA_MISMATCH": bool(existe and sha_livro and sha_disco != sha_livro),
                    "RAW_ASSET_ID": (b or {}).get("RAW_ASSET_ID"),
                    "STORAGE_OBJECT_ID": (b or {}).get("STORAGE_OBJECT_ID"),
                    "DERIVED_COUNT": (b or {}).get("DERIVED_COUNT", 0) if b else 0,
                    "FACT_TIME": o.get("FACT_TIME"),
                    "SOURCE_DATE_ISO": o.get("SOURCE_DATE_ISO"),
                }
                linhas.append(linha)
                itens.append(linha)
        com_bytes = [l for l in linhas if l["LOCAL_FILE"]]
        fases_a[nome] = {
            "RUNS": len(info["RUN_IDS"]),
            "FONTES": len(set(info.get("SOURCE_IDS") or [])),
            "REDE_REAL": info.get("REDE_REAL"),
            "TARGET_OBSERVATIONS": len(linhas),
            "TARGET_WITH_BYTES": len(com_bytes),
            "TARGET_BYTES_INTEGRITY_OK": sum(
                1 for l in com_bytes if l["SHA256"] and not l["SHA_MISMATCH"]),
            "TARGET_SHA_MISMATCH": sum(1 for l in linhas if l["SHA_MISMATCH"]),
            "TARGET_WITH_RAW_ASSET": sum(1 for l in linhas if l["RAW_ASSET_ID"]),
            "TARGET_WITHOUT_RAW_ASSET": sum(1 for l in linhas if not l["RAW_ASSET_ID"]),
            "DISTINCT_DOCUMENT_ID": len({l["DOCUMENT_ID"] for l in linhas if l["DOCUMENT_ID"]}),
            "DISTINCT_DETAIL_URL": len({l["DETAIL_URL"] for l in linhas if l["DETAIL_URL"]}),
            "DISTINCT_SHA256": len({l["SHA256"] for l in linhas if l["SHA256"]}),
            "RESULTADOS": dict(Counter(l["OBSERVATION_RESULT"] for l in linhas)),
        }

    # ── FASE B · os ficheiros do armazem, vistos DO LADO DO DISCO ──────────
    # ⚠️ A DIRECCAO IMPORTA. Partir do livro responde «as observacoes tem
    # bytes?»; partir do disco responde «estes bytes sao de quem?». Sao duas
    # perguntas, e um ficheiro orfao so aparece na segunda.
    sha_do_livro = {}
    for o in livro:
        s = o.get("RAW_SHA256")
        if s:
            sha_do_livro.setdefault(s, []).append(o)

    ficheiros, matched, unmatched = [], 0, 0
    for base, _dirs, nomes in os.walk(ARMAZEM):
        for n in nomes:
            p = os.path.join(base, n)
            s = sha_do_ficheiro(p)
            donos = sha_do_livro.get(s, [])
            if donos:
                matched += 1
                como = "SHA256 == RAW_SHA256 de %d observacao(oes)" % len(donos)
            else:
                unmatched += 1
                # NAO SE INVENTA LIGACAO. Nem pelo nome, nem pela pasta: a
                # pasta tem o DOCUMENT_ID no caminho e seria facil «deduzir»
                # o dono — e essa deducao nao e prova de que estes BYTES sao
                # os daquela observacao.
                como = None
            ficheiros.append({
                "FICHEIRO": os.path.relpath(p, RAIZ).replace("\\", "/"),
                "BYTES": os.path.getsize(p),
                "SHA256": s,
                "ESTADO": "MATCHED" if donos else "UNMATCHED",
                "COMO_SE_PROVOU": como,
                "OBSERVACOES": [observation_id(d) for d in donos][:6],
                "CORRIDAS": sorted({d.get("RUN_ID") for d in donos}) if donos else [],
            })

    # observacoes da COORTE sem bytes locais
    sem_bytes = [l for l in itens if not l["LOCAL_FILE"]]

    fase_b = {
        "FICHEIROS_NO_ARMAZEM": len(ficheiros),
        "LOCAL_BYTES_MATCHED": matched,
        "LOCAL_BYTES_UNMATCHED": unmatched,
        "OBSERVATIONS_WITHOUT_LOCAL_BYTES": len(sem_bytes),
        "COMO_SE_PROVA": "sha256 do ficheiro em disco == RAW_SHA256 escrito no "
                         "livro. Nome e pasta NAO contam como prova: o caminho "
                         "carrega o DOCUMENT_ID e seria facil «deduzir» o dono, "
                         "mas deduzir nao e provar que ESTES bytes sao daquela "
                         "observacao.",
        "FICHEIROS_DA_COORTE": sum(
            1 for f in ficheiros if any(c in {l["RUN_ID"] for l in itens} for c in f["CORRIDAS"])),
    }

    return {
        "MEDIDOR": "medidas/coorte_da_micro_collection.py",
        "LEI": "O UNIVERSO NAO E A COORTE",
        "UNIVERSO_PARA_CONTRASTE": {
            "OBSERVACOES_NO_LIVRO_INTEIRO": len(livro),
            "CORRIDAS_NO_LIVRO_INTEIRO": len(por_run),
            "PORQUE_ESTA_AQUI": "para nao ser confundido com a coorte, e nao "
                                "para ser citado no lugar dela",
        },
        "COORTE": {
            "CORRIDAS": list(corridas.keys()),
            "RUN_IDS": {k: v["RUN_IDS"] for k, v in corridas.items()},
            "TOTAL_OBSERVACOES_DA_COORTE": len(itens),
        },
        "FASE_A": fases_a,
        "FASE_B": fase_b,
        "BANCO_LIDO": banco is not None,
        "ITENS": itens,
        "FICHEIROS": ficheiros,
        "OBSERVACOES_SEM_BYTES_LOCAIS": [
            {k: l[k] for k in ("CORRIDA", "RUN_ID", "OBSERVATION_ID", "SOURCE_ID",
                               "OBSERVATION_RESULT", "SHA256")} for l in sem_bytes],
    }


def eixo_do_banco(shas):
    """So LEITURA, pelo psql. `None` quando nao da para ler — e `None` escreve
    `NAO_SEI` na coluna, que e diferente de escrever `ausente`."""
    dsn = os.environ.get("SALA_DSN")
    psql = os.environ.get("SINTONIA_PSQL_EXE")
    if not dsn or not psql or not os.path.isfile(psql):
        return None
    import subprocess
    lista = ",".join(sorted({s for s in shas if s}))
    sql = ("select r.sha256||'|'||r.id||'|'||coalesce(r.storage_object_id::text,'')"
           "||'|'||(select count(*) from derived_artifact d where d.raw_asset_id=r.id) "
           "from raw_asset r where r.sha256 = any(string_to_array($S$" + lista + "$S$, ','))")
    try:
        # psql no Windows nao permuta opcoes: a DSN vai no FIM.
        p = subprocess.run([psql, "-At", "-F", "|", "-c", sql, dsn],
                           capture_output=True, text=True, timeout=180)
    except Exception:
        return None
    if p.returncode != 0:
        return None
    fora = {}
    for linha in p.stdout.splitlines():
        # o psql traz `\r` no Windows; sem o tirar o ultimo campo leva-o colado
        c = linha.strip().replace("\r", "").split("|")
        if len(c) >= 4:
            fora[c[0]] = {"RAW_ASSET_ID": c[1], "STORAGE_OBJECT_ID": c[2] or None,
                          "DERIVED_COUNT": int(c[3])}
    return fora


def main(argv):
    r = medir()
    with open(SAIDA, "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1, ensure_ascii=False)

    print("=== A COORTE (dos manifestos, nao do relogio) ===")
    cab = ("corrida", "runs", "obs", "c/bytes", "integr", "mism", "c/RAW", "s/RAW",
           "docs", "urls", "shas")
    print("  %-7s %4s %4s %7s %6s %4s %5s %5s %4s %4s %4s" % cab)
    for nome, f in r["FASE_A"].items():
        print("  %-7s %4d %4d %7d %6d %4d %5d %5d %4d %4d %4d" % (
            nome, f["RUNS"], f["TARGET_OBSERVATIONS"], f["TARGET_WITH_BYTES"],
            f["TARGET_BYTES_INTEGRITY_OK"], f["TARGET_SHA_MISMATCH"],
            f["TARGET_WITH_RAW_ASSET"], f["TARGET_WITHOUT_RAW_ASSET"],
            f["DISTINCT_DOCUMENT_ID"], f["DISTINCT_DETAIL_URL"], f["DISTINCT_SHA256"]))
        print("          %s" % f["RESULTADOS"])
    print("\n  TOTAL_OBSERVACOES_DA_COORTE = %d" % r["COORTE"]["TOTAL_OBSERVACOES_DA_COORTE"])
    print("  (universo inteiro do livro, para contraste: %d observacoes em %d corridas)"
          % (r["UNIVERSO_PARA_CONTRASTE"]["OBSERVACOES_NO_LIVRO_INTEIRO"],
             r["UNIVERSO_PARA_CONTRASTE"]["CORRIDAS_NO_LIVRO_INTEIRO"]))

    print("\n=== FASE B · os ficheiros, vistos do lado do DISCO ===")
    for k, v in r["FASE_B"].items():
        if k != "COMO_SE_PROVA":
            print("  %-36s %s" % (k, v))
    print("\n  escrito: medidas/COORTE-MICRO-COLLECTION-V1.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
