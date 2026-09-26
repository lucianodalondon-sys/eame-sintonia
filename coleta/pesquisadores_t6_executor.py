#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T6 · PESQUISADORES — o executor que entrega os trabalhos JA GUARDADOS como COLHEITA.

    py coleta/pesquisadores_t6_executor.py --run-id=<RUN_ID> [--rodadas=<pasta>]

O QUE E, E O QUE NAO E
----------------------
NAO vai a rede. As rodadas (`coleta/pesquisadores_t6.py --rede`) ja guardaram as respostas
do OpenAlex, tal como vieram, com sha256. Este executor so as DECLARA a porta canonica,
no contrato de retorno (COL-LAW-505), para o orquestrador as levar pelo caminho de todas:

    ingresso -> RAW -> (derivacao: NOT_APPLICABLE para JSON) -> Admissao -> Sala

    O COLETOR OBSERVA. A PORTA PRESERVA. A ADMISSAO JULGA.

A FONTE E UMA SO, E JA EXISTE: `EU-T5-001` (OpenAlex, Atlas «T5 e T6»). Uma unidade
= um TRABALHO (DOI). Os pesquisadores viajam DENTRO da unidade (campo `T6`), com a prova
de cada um — nao se cunha uma fonte por pessoa para os trabalhos passarem.

O BRUTO
-------
O bruto de cada trabalho e o REGISTO dele tal como veio na pagina do OpenAlex,
serializado de forma canonica (chaves ordenadas). A pagina inteira continua guardada na
pasta da rodada; `ORIGEM_DO_REGISTO` diz qual pagina, com o sha256 dela, e a posicao.

    O REGISTO E O QUE A FONTE PUBLICOU SOBRE O TRABALHO. NAO E O ARTIGO.

O QUE NUNCA SE ESCREVE AQUI
---------------------------
FACT_TIME e FACT_LOCATION ficam NAO SEI: a data de publicacao nao e o periodo do
estudo, e a afiliacao nao e o local do ensaio. O local e o periodo ESCRITOS no resumo
viajam no campo `T6`, como candidatos com o trecho — nunca como facto.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import retorno_da_coleta as rdc  # noqa: E402
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
import pesquisadores_t6 as T6  # noqa: E402

EXECUTOR_ID = "pesquisadores-t6"
EXECUTOR_VERSION = "t6-v1"
PIPELINE_VERSION = "collection-v1"
SOURCE_ID = "EU-T5-001"
PUBLISHER = "OpenAlex"
MEDIA_TYPE = "application/json"
BALCAO = os.path.join("data", "colheita", "pesquisadores-t6")
RETORNO = os.path.join(BALCAO, "RETORNO.json")
RODADAS_POR_OMISSAO = os.path.join(BALCAO, "rodadas")
ARMAZEM = os.path.join("data", "raw", "pesquisadores-t6")


class SemCorrida(ValueError):
    """O RUN_ID vem do orquestrador. Este executor nao cunha corrida."""


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _slug(s: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in s)[:150]


def registos(rodadas: str) -> dict:
    """{chave (DOI ou id OpenAlex): (registo, pagina, sha da pagina, posicao, par)}.
    So respostas VALIDAS; a mesma obra em dois pares fica com a primeira pagina e os pares
    juntos (a mesma obra e uma unidade)."""
    out, pares = {}, {}
    for f in sorted(os.listdir(rodadas)):
        if not (f.startswith("openalex-") and f.endswith(".json")):
            continue
        cam = os.path.join(rodadas, f)
        with open(cam, "rb") as h:
            b = h.read()
        d = json.loads(b.decode("utf-8") or "null")
        if not T6.resposta_valida(d)[0]:
            continue
        par = f[len("openalex-"):-len(".json")].replace("-", " x ", 1)
        for i, w in enumerate(d["results"]):
            k = T6._doi(w.get("doi")) or w.get("id")
            pares.setdefault(k, set()).add(par)
            if k not in out:
                out[k] = (w, f, _sha(b), i)
    return {k: (v[0], v[1], v[2], v[3], sorted(pares[k])) for k, v in out.items()}


def _escrever(rel: str, b: bytes, raiz: str) -> None:
    destino = os.path.join(raiz, rel)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    if os.path.exists(destino):
        with open(destino, "rb") as h:
            if h.read() == b:
                return                         # a escrita mais segura e a que nao acontece
    fd, tmp = tempfile.mkstemp(prefix=".t6-", dir=os.path.dirname(destino))
    with os.fdopen(fd, "wb") as h:
        h.write(b)
    os.replace(tmp, destino)


def colher(run_id: str, rodadas: str = "", raiz: str = RAIZ) -> dict:
    if not str(run_id or "").strip():
        raise SemCorrida("este executor nao cunha corrida: o RUN_ID vem do orquestrador")
    rodadas = rodadas or os.path.join(raiz, RODADAS_POR_OMISSAO)
    erros, unidades = [], []
    if not os.path.isdir(rodadas):
        erros.append({"ERRO": "SEM_RODADAS", "ONDE": rodadas.replace(os.sep, "/"),
                      "PORQUE": "nenhuma rodada guardada: nada para declarar (nao e zero colhido)"})
        regs = {}
    else:
        regs = registos(rodadas)
    us, _grupos = T6.deduplicar([(w, p) for (w, _f, _s, _i, ps) in regs.values() for p in ps])
    por_chave = {(u["DOI"] if u["DOI"] != T6.NAO_SEI else u["OPENALEX_WORK_ID"]): u for u in us}
    for k, (w, pagina, sha_pag, pos, pares) in sorted(regs.items()):
        u = por_chave[k]
        b = json.dumps(w, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        rel = os.path.join(ARMAZEM, _slug(k) + ".json").replace(os.sep, "/")
        _escrever(rel, b, raiz)
        resumo = T6.CP._resumo_do_indice(w.get("abstract_inverted_index"))
        doc = u["DOI"] if u["DOI"] != T6.NAO_SEI else (w.get("id") or rdc.NAO_SEI)
        unidades.append({
            "ESPECIE": rdc.COLHEITA,
            "SOURCE_ID": SOURCE_ID,
            "SOURCE_URL": ("https://doi.org/" + u["DOI"]) if u["DOI"] != T6.NAO_SEI else w.get("id"),
            "PUBLISHER": PUBLISHER,
            "EXECUTOR_ID": EXECUTOR_ID, "EXECUTOR_VERSION": EXECUTOR_VERSION,
            "PIPELINE_VERSION": PIPELINE_VERSION,
            "DOCUMENT_ID": doc,
            "RUN_ID": run_id,
            "CONTENT_TYPE": MEDIA_TYPE,
            "ORIGEM_DOS_BYTES": "ARQUIVO_LOCAL",
            "ORIGEM_DO_REGISTO": {"PAGINA": pagina, "PAGINA_SHA256": sha_pag, "POSICAO": pos,
                                  "PASTA": rodadas.replace(os.sep, "/")},
            "STORAGE_LOCATION": rel,
            "SHA256": _sha(b),
            "PAYLOAD": {"ONDE": rel, "ESTADO": rdc.estado_do_payload(rel, raiz)},
            # o texto que a porta le: o titulo e o resumo que a FONTE publicou
            "title": u["TITULO"],
            "texto": (u["TITULO"] + ". " + resumo).strip() if resumo else u["TITULO"],
            "PUBLISHED_AT": u["PUBLICADO_EM"],
            "PUBLISHED_AT_BASIS": "OpenAlex publication_date do registo",
            "FACT_TIME": rdc.NAO_SEI,
            "FACT_LOCATION": rdc.NAO_SEI,
            # o que e T6 viaja junto, com a prova — nunca como facto
            "T6": {c: u[c] for c in ("AUTORES", "CULTURA", "PROBLEMA", "MOLECULA",
                                     "LOCAL_DO_ESTUDO_ESCRITO", "PERIODO_DO_ESTUDO", "TRIAL_ID",
                                     "DATASET_ID", "CONSULTAS_QUE_O_TROUXERAM",
                                     "NA_CONSULTA_E_NO_TEXTO", "TIPO")},
        })
    envelope = {
        "RUN_ID": run_id, "EXECUTOR_ID": EXECUTOR_ID, "EXECUTOR_VERSION": EXECUTOR_VERSION,
        "ESTADO": rdc.FAILED if (erros and not unidades) else (rdc.PARTIAL if erros else rdc.SUCCESS),
        "COLHEITA": unidades, "SUPORTE": [], "ERROS": erros,
    }
    onde = rdc.endereco_do_envelope(RETORNO.replace(os.sep, "/"), run_id)
    destino = os.path.join(raiz, onde)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as h:
        json.dump(envelope, h, ensure_ascii=False, indent=1)
    return {"RUN_ID": run_id, "ESTADO": envelope["ESTADO"], "COLHIDAS": len(unidades),
            "DECLAROU_EM": onde, "MAL": rdc.conferir(envelope, raiz)}


def main() -> int:
    run_id, rodadas = "", ""
    for a in sys.argv[1:]:
        if a.startswith("--run-id="):
            run_id = a.split("=", 1)[1]
        elif a.startswith("--rodadas="):
            rodadas = a.split("=", 1)[1]
    if not run_id:
        print("uso: py coleta/pesquisadores_t6_executor.py --run-id=<RUN_ID> [--rodadas=<pasta>]",
              file=sys.stderr)
        return 2
    r = colher(run_id, rodadas)
    print("T6 · %s · colhidas=%d · declarou em %s · contrato: %s"
          % (r["ESTADO"], r["COLHIDAS"], r["DECLAROU_EM"], "OK" if not r["MAL"] else r["MAL"][:3]))
    return 0 if r["ESTADO"] != rdc.FAILED else 1


if __name__ == "__main__":
    raise SystemExit(main())
