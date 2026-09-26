# -*- coding: utf-8 -*-
"""O VIDEO DE CADA ITEM SOCIAL NA SALA — o escritor da tabela da PROPOSTA 037 (MAESTRO-SOCIAL, 26/09).

    sql_de_registo(run_id, pares) -> str | None      (pares = [(ordem, unidade), ...])
    registar(run_id, pares, *, dsn, psql="psql")     -> o que o psql devolveu

`unidade` e o que o Scrap carimbou (`leis/identidade_do_video.marcar`): `VIDEO_IDENTITY`,
`VIDEO_IDENTITY_BASIS` e, numa partilha, `MESMO_VIDEO_QUE`. `ordem` e a ordem do item NA Sala
(a mesma chave `(run_id, ordem)` de `sala_de_espera`).

⚠️ UNKNOWN NAO FUNDE: uma unidade com `VIDEO_IDENTITY` = NAO SEI (ou sem ela) nao gera linha. A tabela
recusa-a tambem (regra do formato), mas nao se manda ao banco o que se sabe que ele recusa.

⚠️ NAO ESTA LIGADO. Enquanto a 037 for proposta, ninguem chama `registar` na estrada: o sitio onde se
liga (depois do `pousar` da Admissao, com a ordem de cada item) e do dono da Sala. O ensaio
(`provas/migracao_037_ensaio_descartavel.py`) chama-o numa Sala DESCARTAVEL.
"""
from __future__ import annotations

import json
import re
import subprocess

RE_IDENTIDADE = re.compile(r"^(YOUTUBE:[A-Za-z0-9_-]{11}|LINKEDIN:urn:li:digitalmediaAsset:[A-Za-z0-9_-]+)$")


def _lit(v) -> str:
    return "'" + str(v).replace("'", "''") + "'"


def linha(run_id: str, ordem: int, u: dict) -> str | None:
    vid = str(u.get("VIDEO_IDENTITY") or "")
    if not RE_IDENTIDADE.match(vid):
        return None
    mesmo = u.get("MESMO_VIDEO_QUE")
    mesmo_sql = "null" if not mesmo else _lit(json.dumps(mesmo, ensure_ascii=False, sort_keys=True)) + "::jsonb"
    return "(%s, %d, %s, %s, %s)" % (_lit(run_id), int(ordem), _lit(vid),
                                     _lit(u.get("VIDEO_IDENTITY_BASIS") or "sem base declarada"), mesmo_sql)


def sql_de_registo(run_id: str, pares: list) -> str | None:
    valores = [x for x in (linha(run_id, o, u) for o, u in pares) if x]
    if not valores:
        return None
    return ("insert into public.sala_de_espera_video "
            "(run_id, ordem, video_identity, video_identity_basis, mesmo_video_que) values %s "
            "on conflict (run_id, ordem) do nothing;" % ", ".join(valores))


def registar(run_id: str, pares: list, *, dsn: str, psql: str = "psql") -> str:
    sql = sql_de_registo(run_id, pares)
    if sql is None:
        return "NADA_A_REGISTAR"
    r = subprocess.run([psql, "-X", "-v", "ON_ERROR_STOP=1", "-q", "-d", dsn, "-c", sql],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if r.returncode:
        raise RuntimeError("SALA_VIDEO_RECUSOU: " + (r.stderr or "")[-400:])
    return "REGISTADO"
