#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A ULTIMA MILHA — o que as 85 observacoes SAO, medido peca a peca.

PORQUE ESTE FICHEIRO EXISTE
---------------------------
A CANONICAL-MICRO-V1 fechou com «85 colhidos, 0 na Sala». Esse numero, sozinho,
nao diz nada: nao se sabe se sao 85 documentos ou 85 visitas ao mesmo, nem se
os bytes ainda estao no disco, nem onde a cadeia parou.

    RUN != OBSERVATION != CONTENT != STORAGE_OBJECT
    SHA256 identifica BYTES; NAO identifica OBSERVACAO
    storage_path e ENDERECO, nao identidade

O erro que este medidor existe para nao repetir e assumir `85 observacoes =
85 RAW`. Sao eixos diferentes e contam-se em separado, sempre.

O QUE ELE NAO FAZ
-----------------
Nao vai a rede. Nao escreve no livro. Nao promove nada. Le o livro de
observacoes e o armazem em disco, confere o SHA declarado contra os bytes que
la estao, e imprime contagens. E um medidor — se ele mudar estado, deixou de
medir e passou a ser corrida.

SAIDA: medidas/ULTIMA-MILHA-V1.json
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter, OrderedDict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVRO = os.path.join(RAIZ, "data", "collection-ledger", "italy", "observations.ndjson")
SAIDA = os.path.join(RAIZ, "medidas", "ULTIMA-MILHA-V1.json")

# Os tres resultados que significam «esta observacao trouxe bytes». Vocabulario
# fechado de proposito: um resultado novo tem de ser decidido, nao herdado.
TROUXE_BYTES = {
    "NEW_DOCUMENT",                    # documento que nao existia
    "DOCUMENT_CHANGED_IN_PLACE",       # mesmo endereco, bytes outros
    "SEMANTIC_ID_CHANGED_SAME_BYTES",  # bytes iguais, identidade outra
    "SEEN_AGAIN",                      # revisita sem novidade
}


def ler_livro(caminho=LIVRO):
    with open(caminho, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def sha_do_ficheiro(caminho, bloco=1 << 20):
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for pedaco in iter(lambda: fh.read(bloco), b""):
            h.update(pedaco)
    return h.hexdigest()


def caminho_absoluto(raw_path):
    """O livro guarda `./data/...`; o disco quer um caminho desta maquina."""
    if not raw_path:
        return None
    return os.path.normpath(os.path.join(RAIZ, raw_path.lstrip("./").lstrip(".\\")))


def medir_observacao(o):
    """Uma linha do censo. Cada campo e uma PERGUNTA, e `None` e resposta."""
    raw_path = o.get("RAW_PATH")
    abs_ = caminho_absoluto(raw_path)
    existe = bool(abs_ and os.path.isfile(abs_))
    tamanho = os.path.getsize(abs_) if existe else None
    sha_disco = sha_do_ficheiro(abs_) if existe else None
    sha_livro = o.get("RAW_SHA256")
    return {
        # ── identidade: quatro eixos que NAO sao o mesmo eixo ──────────────
        "RUN_ID": o.get("RUN_ID"),
        "SOURCE_ID": o.get("SOURCE_ID"),
        "DOCUMENT_ID": o.get("DOCUMENT_ID"),
        "DOCUMENT_VERSION_ID": o.get("DOCUMENT_VERSION_ID"),
        "DETAIL_URL": o.get("SOURCE_URL"),
        # ── bytes ───────────────────────────────────────────────────────────
        "OBSERVATION_RESULT": o.get("OBSERVATION_RESULT"),
        "BYTES_DECLARADOS": o.get("BYTES"),
        "SHA256_LIVRO": sha_livro,
        "RAW_PATH": raw_path,
        "BYTES_PRESENT": existe,
        "BYTES_NO_DISCO": tamanho,
        "SHA256_DISCO": sha_disco,
        # ⚠️ INTEGRO nao e «o ficheiro esta la». E «o ficheiro que esta la e o
        # que o livro diz que e». Um SHA que nao bate e pior que um ficheiro em
        # falta: o ficheiro em falta sabe-se; o trocado passa por bom.
        "BYTES_INTEGROS": bool(existe and sha_livro and sha_disco == sha_livro),
        "CONTENT_TYPE": o.get("CONTENT_TYPE"),
        "MIME_ASSINATURA": o.get("MIME_ASSINATURA"),
        # ── tempo, lugar, cultura — medidos, nunca fabricados (F12) ─────────
        "FACT_TIME": o.get("FACT_TIME"),
        "SOURCE_DATE_ISO": o.get("SOURCE_DATE_ISO"),
        "CAPTURED_AT": o.get("CAPTURED_AT"),
        "RAW_PRESERVED_BEFORE_PARSE": o.get("RAW_PRESERVED_BEFORE_PARSE"),
    }


def por_corrida(obs):
    """Agrupa mantendo a ordem do livro: um ndjson e append-only, e a ordem
    dele E a cronologia. Ordenar por outra coisa apaga essa informacao."""
    grupos = OrderedDict()
    for o in obs:
        grupos.setdefault(o.get("RUN_ID"), []).append(o)
    return grupos


def censo_da_corrida(run_id, linhas):
    com_bytes = [l for l in linhas if l["BYTES_PRESENT"]]
    integros = [l for l in linhas if l["BYTES_INTEGROS"]]
    return {
        "RUN_ID": run_id,
        "OBSERVATIONS": len(linhas),
        # ⚠️ AS QUATRO CONTAGENS QUE NAO SAO A MESMA. Escrevem-se juntas
        # exactamente para que ninguem possa citar uma como se fosse a outra.
        "DISTINCT_SOURCE_ID": len({l["SOURCE_ID"] for l in linhas}),
        "DISTINCT_DOCUMENT_ID": len({l["DOCUMENT_ID"] for l in linhas if l["DOCUMENT_ID"]}),
        "DISTINCT_DETAIL_URL": len({l["DETAIL_URL"] for l in linhas if l["DETAIL_URL"]}),
        "DISTINCT_SHA256": len({l["SHA256_LIVRO"] for l in linhas if l["SHA256_LIVRO"]}),
        "DISTINCT_RAW_PATH": len({l["RAW_PATH"] for l in linhas if l["RAW_PATH"]}),
        "BYTES_PRESENT": len(com_bytes),
        "BYTES_MISSING": len(linhas) - len(com_bytes),
        "BYTES_INTEGROS": len(integros),
        "BYTES_CORROMPIDOS": len(com_bytes) - len(integros),
        "RESULTADOS": dict(Counter(l["OBSERVATION_RESULT"] for l in linhas)),
        "FACT_TIME_PROVEN": sum(1 for l in linhas
                                if l["FACT_TIME"] and "UNKNOWN" not in str(l["FACT_TIME"]).upper()),
        "FACT_TIME_UNKNOWN": sum(1 for l in linhas
                                 if not l["FACT_TIME"] or "UNKNOWN" in str(l["FACT_TIME"]).upper()),
        "SOURCE_DATE_PROVEN": sum(1 for l in linhas if l["SOURCE_DATE_ISO"]),
    }


# ── O EIXO DO BANCO ────────────────────────────────────────────────────────
# ⚠️ ESTE MEDIDOR SO LE. Nao abre transacao de escrita, nao cria tabela, nao
# promove nada. Se a ligacao nao existir, o censo sai na mesma e diz que nao
# sabe — `NAO_SEI` medido vale mais que um zero que parece resposta.
#
# A juncao faz-se pelo SHA256, e nao pelo caminho:
#     storage_path e ENDERECO; sha256 e BYTE_ID.
# Um ficheiro movido continua o mesmo conteudo; um caminho reutilizado, nao.
CONSULTA_BANCO = """
select r.sha256, r.id, r.storage_object_id, r.source_id,
       (select count(*) from derived_artifact d where d.raw_asset_id = r.id),
       (select min(d.id) from derived_artifact d where d.raw_asset_id = r.id)
  from raw_asset r
 where r.sha256 = any(%s)
"""


def eixo_do_banco(shas, dsn=None, psql=None):
    """O que o BANCO sabe destes conteudos. Devolve `None` se nao der para ler.

    Nao inventa: se a porta nao abrir, a resposta e `None` e o censo escreve
    `NAO_SEI` na coluna, em vez de escrever `ausente`. As duas palavras
    parecem-se e significam o contrario uma da outra.
    """
    dsn = dsn or os.environ.get("SALA_DSN")
    psql = psql or os.environ.get("SINTONIA_PSQL_EXE")
    if not dsn or not psql or not os.path.isfile(psql):
        return None
    import subprocess
    lista = ",".join(sorted({s for s in shas if s}))
    sql = ("select r.sha256||'|'||r.id||'|'||coalesce(r.storage_object_id::text,'')"
           "||'|'||coalesce(r.source_id,'')||'|'||"
           "(select count(*) from derived_artifact d where d.raw_asset_id=r.id) "
           "from raw_asset r where r.sha256 = any(string_to_array($SHA$" + lista + "$SHA$, ','))")
    try:
        # ⚠️ psql no Windows NAO permuta opcoes: a DSN vai no FIM, depois das
        # opcoes. Com a DSN a frente, a consulta nao corre e sai com zero — um
        # zero que se leria como «o banco nao tem nada».
        p = subprocess.run([psql, "-At", "-F", "|", "-c", sql, dsn],
                           capture_output=True, text=True, timeout=120)
    except Exception:
        return None
    if p.returncode != 0:
        return None
    fora = {}
    for linha in p.stdout.splitlines():
        # ⚠️ o psql traz `\r` no Windows; sem o tirar, o ultimo campo leva-o
        # colado e toda a comparacao falha em silencio.
        campos = linha.strip().replace("\r", "").split("|")
        if len(campos) >= 5:
            fora[campos[0]] = {"RAW_ASSET_ID": campos[1],
                               "STORAGE_OBJECT_ID": campos[2] or None,
                               "SOURCE_ID_NO_BANCO": campos[3] or None,
                               "DERIVED_COUNT": int(campos[4])}
    return fora


def medir():
    obs = ler_livro()
    linhas = [medir_observacao(o) for o in obs]

    # ── o eixo do banco, colado a cada linha (ou `NAO_SEI` se nao abriu) ────
    banco = eixo_do_banco([l["SHA256_LIVRO"] for l in linhas])
    for l in linhas:
        if banco is None:
            l["RAW_ASSET_ID"] = l["STORAGE_OBJECT_ID"] = l["DERIVED_ID"] = "NAO_SEI"
            l["ADMISSION_STATE"] = l["SALA_STATE"] = "NAO_SEI — banco nao lido"
            continue
        b = banco.get(l["SHA256_LIVRO"])
        l["RAW_ASSET_ID"] = b["RAW_ASSET_ID"] if b else None
        l["STORAGE_OBJECT_ID"] = b["STORAGE_OBJECT_ID"] if b else None
        l["DERIVED_ID"] = (b["DERIVED_COUNT"] or None) if b else None
        # ⚠️ ADMISSION NUNCA_APRESENTADO != ADMISSION_NAO. O primeiro diz que a
        # pergunta nao foi feita; o segundo que foi feita e a resposta foi nao.
        # Contar os dois juntos apagaria exactamente a informacao que interessa.
        l["ADMISSION_STATE"] = "NEVER_PRESENTED" if not b else "PRESENTED"
        l["SALA_STATE"] = "ABSENT" if not b else "SEE_SALA"

    grupos = por_corrida(linhas)

    corridas = [censo_da_corrida(r, v) for r, v in grupos.items()]
    # A ULTIMA COLHEITA: a corrida mais recente que trouxe bytes. E a unica
    # populacao que interessa para a ultima milha — as anteriores ou falharam
    # identidade (zero bytes) ou sao a mesma materia numa visita mais velha.
    com_bytes = [c for c in corridas if c["BYTES_PRESENT"] > 0]
    ultima_vaga_ts = max((c["RUN_ID"].split("-")[4] for c in com_bytes
                          if len(c["RUN_ID"].split("-")) > 4), default=None)

    todas_as_linhas = [l for v in grupos.values() for l in v]
    universo = {
        "OBSERVATIONS_TOTAL": len(todas_as_linhas),
        "RUNS_TOTAL": len(grupos),
        "OBSERVATIONS_COM_RESULTADO_DE_BYTES": sum(
            1 for l in todas_as_linhas if l["OBSERVATION_RESULT"] in TROUXE_BYTES),
        "BYTES_PRESENT_TOTAL": sum(1 for l in todas_as_linhas if l["BYTES_PRESENT"]),
        "BYTES_INTEGROS_TOTAL": sum(1 for l in todas_as_linhas if l["BYTES_INTEGROS"]),
        # O eixo do CONTEUDO, que nao e o eixo da observacao:
        "DISTINCT_SHA256_TOTAL": len({l["SHA256_LIVRO"] for l in todas_as_linhas if l["SHA256_LIVRO"]}),
        "DISTINCT_DOCUMENT_ID_TOTAL": len({l["DOCUMENT_ID"] for l in todas_as_linhas if l["DOCUMENT_ID"]}),
        "DISTINCT_RAW_PATH_TOTAL": len({l["RAW_PATH"] for l in todas_as_linhas if l["RAW_PATH"]}),
        # ── a cadeia canonica, contada por eixo ─────────────────────────────
        "COM_RAW_ASSET": sum(1 for l in todas_as_linhas if l.get("RAW_ASSET_ID") not in (None, "NAO_SEI")),
        "SEM_RAW_ASSET": sum(1 for l in todas_as_linhas if l.get("RAW_ASSET_ID") is None),
        "BANCO_LIDO": banco is not None,
    }

    return {
        "MEDIDOR": "medidas/ultima_milha.py",
        "LEI": "RUN != OBSERVATION != CONTENT != STORAGE_OBJECT",
        "UNIVERSO": universo,
        "ULTIMA_VAGA_TS": ultima_vaga_ts,
        "CORRIDAS": corridas,
        "LINHAS": todas_as_linhas,
    }


def main(argv):
    r = medir()
    with open(SAIDA, "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1, ensure_ascii=False)
    u = r["UNIVERSO"]
    print("=== UNIVERSO ===")
    for k, v in u.items():
        print(f"  {k:38} {v}")
    print("\n=== CORRIDAS QUE TROUXERAM BYTES ===")
    for c in r["CORRIDAS"]:
        if c["BYTES_PRESENT"] == 0 and not any(
                x in TROUXE_BYTES for x in c["RESULTADOS"]):
            continue
        print(f"  {c['RUN_ID'][:44]:46} obs={c['OBSERVATIONS']:3} "
              f"src={c['DISTINCT_SOURCE_ID']:2} doc={c['DISTINCT_DOCUMENT_ID']:3} "
              f"sha={c['DISTINCT_SHA256']:3} path={c['DISTINCT_RAW_PATH']:3} "
              f"presentes={c['BYTES_PRESENT']:3} integros={c['BYTES_INTEGROS']:3} "
              f"{c['RESULTADOS']}")
    print(f"\n  escrito: {os.path.relpath(SAIDA, RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
