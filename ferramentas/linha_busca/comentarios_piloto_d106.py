# -*- coding: utf-8 -*-
"""PILOTO DE COMENTARIOS DA D106 — a resposta CRUA de `commentThreads.list` para os 10 pais do §12. So no Actions.

    YOUTUBE_DATA_API_KEY=... python3 ferramentas/linha_busca/comentarios_piloto_d106.py --saida=<pasta>

D106 (dono, 27/09 ~12:05): «rodar o piloto no YouTube (API oficial, custo zero)»; a credencial so existe no runner
do GitHub Actions. Os 10 videos pais sao os de `COMMENT-INTELLIGENCE-FASE1.md` §12 (PILOT_PARENT_ITEMS): 7 com
comentarios, 2 de contraste (0 comentarios, para provar ZERO_RESULTS) e 1 de controle fora do atlas.

POR VIDEO, DUAS CHAMADAS: `order=relevance` e `order=time` (diversidade), `maxResults=100`, UMA pagina (o
`nextPageToken`, se vier, fica anotado e NAO se segue). 20 chamadas = 20 unidades das 10 000 do dia.

O QUE SAI (artifact): cada resposta CRUA, byte a byte, em `comentarios/<video>__<ordem>.json`, e o manifesto
`COMENTARIOS-PILOTO-D106.json` com o sha256 de cada uma, o pedido SEM a chave, HTTP, itens e o erro (redigido).
Nada se interpreta aqui: a entrada na Sala faz-se na maquina do coordenador, pela porta canonica — e e LA que
se aplica a minimizacao da D106 (sem perfil/avatar do comentarista; comentario = PUBLIC_ASSERTION, nunca FACT).

⚠️ A resposta crua TRAZ o nome e o canal de quem comentou (e assim que a API a devolve). Por isso o artifact
vive pouco (retention-days no workflow) e nao vai para o repositorio.

A chave nunca e impressa: vai no endereco (`key=`) e todo o texto de erro passa pela tesoura (`api_oficial.redigir`).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api_oficial as API  # noqa: E402

ENV_CHAVE = "YOUTUBE_DATA_API_KEY"
ENDERECO = "https://www.googleapis.com/youtube/v3/commentThreads"
#: COMMENT-INTELLIGENCE-FASE1.md §12, PILOT_PARENT_ITEMS, pela ordem de la.
VIDEOS = ("soP-t7nvvq8", "F5uLnId6fJk", "w87w51fSWAw", "QGE7h4gztQ8", "R5FJWJkCbKI", "5MNenAiGtlQ",
          "QmeVN7SNnMU", "2cF0yHZXiMs", "ioLYGSazexk", "ezRyN8vLVvc")
ORDENS = ("relevance", "time")
TETO_CHAMADAS = len(VIDEOS) * len(ORDENS)          # 20 — e nada mais
#: Erros que valem para a CHAVE/PROJETO, nao para o video: repetir nos outros 19 so gastaria quota a toa.
PARAM_TUDO = {"QUOTAEXCEEDED", "DAILYLIMITEXCEEDED", "RATELIMITEXCEEDED", "KEYINVALID", "ACCESSNOTCONFIGURED",
              "SERVICE_DISABLED", "API_KEY_INVALID", "API_KEY_SERVICE_BLOCKED", "API_KEY_IP_ADDRESS_BLOCKED",
              "API_KEY_HTTP_REFERRER_BLOCKED"}


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parametros(video: str, ordem: str) -> dict:
    """O pedido, SEM a chave (e assim que vai para o manifesto)."""
    return {"part": "snippet,replies", "videoId": video, "maxResults": 100, "order": ordem, "textFormat": "plainText"}


def colher(saida: Path, chave: str | None, pedir=None) -> dict:
    saida = Path(saida)
    (saida / "comentarios").mkdir(parents=True, exist_ok=True)
    doc = {"DATASET": "COMENTARIOS-PILOTO-D106", "DECISAO": "D106", "ROTA": "youtube-data-api-v3:commentThreads.list",
           "PAIS": "COMMENT-INTELLIGENCE-FASE1.md §12", "TETO_CHAMADAS": TETO_CHAMADAS, "INICIO": agora(),
           "CHAMADAS": 0, "RESPOSTAS": []}
    if not chave:
        doc.update(PAROU="o secret %s nao chegou ao ambiente — nenhuma chamada saiu" % ENV_CHAVE, FIM=agora())
        return doc
    env = {ENV_CHAVE: chave}
    parar = None
    for v in VIDEOS:
        for o in ORDENS:
            p = parametros(v, o)
            linha = {"VIDEO_ID": v, "ORDER": o, "PEDIDO_SEM_CHAVE": "%s?%s" % (ENDERECO, urllib.parse.urlencode(p))}
            if parar:
                linha["NAO_PEDIDO"] = parar
                doc["RESPOSTAS"].append(linha)
                continue
            if doc["CHAMADAS"] >= TETO_CHAMADAS:
                raise AssertionError("teto de %d chamadas ultrapassado" % TETO_CHAMADAS)
            instante = agora()
            http, corpo, erro = (pedir or API.pedir)("%s?%s" % (ENDERECO, urllib.parse.urlencode(dict(p, key=chave))))
            doc["CHAMADAS"] += 1
            nome = "comentarios/%s__%s.json" % (v, o)
            (saida / nome).write_bytes(corpo)
            linha.update(INSTANTE=instante, HTTP=http, FICHEIRO=nome, SHA256=hashlib.sha256(corpo).hexdigest(),
                         BYTES=len(corpo))
            if http == 200:
                j = json.loads(corpo or b"{}")
                linha.update(ITENS=len(j.get("items") or []),
                             RESPOSTAS_NOS_ITENS=sum(len((i.get("replies") or {}).get("comments") or [])
                                                     for i in j.get("items") or []),
                             TOTAL_DECLARADO=(j.get("pageInfo") or {}).get("totalResults"),
                             HA_MAIS_PAGINAS=bool(j.get("nextPageToken")))
            else:
                g = API._erro_do_google(corpo)
                linha.update(ERRO=API.redigir(erro, env), ERRO_RAZOES=g["RAZOES"],
                             ERRO_MENSAGEM=API.redigir(g["MENSAGEM"], env)[:300])
                if {r.upper() for r in g["RAZOES"]} & PARAM_TUDO:
                    parar = "parado depois de %s em %s/%s: o erro e da chave/projeto, nao do video" % (
                        ",".join(g["RAZOES"]), v, o)
            doc["RESPOSTAS"].append(linha)
    doc.update(FIM=agora(), PAROU=parar,
               COM_200=sum(1 for r in doc["RESPOSTAS"] if r.get("HTTP") == 200),
               ITENS_TOTAL=sum(r.get("ITENS") or 0 for r in doc["RESPOSTAS"]),
               VIDEOS_COM_COMENTARIO=sorted({r["VIDEO_ID"] for r in doc["RESPOSTAS"] if (r.get("ITENS") or 0) > 0}))
    return doc


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    saida = Path(a.get("saida") or "saida")
    chave = os.environ.get(ENV_CHAVE)
    doc = colher(saida, chave)
    texto = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    (saida / "COMENTARIOS-PILOTO-D106.json").write_text(API.redigir(texto, {ENV_CHAVE: chave or ""}), encoding="utf-8")
    print("chamadas %d/%d · HTTP 200: %d · comentarios (threads): %d · videos com comentario: %d · parou: %s" % (
        doc["CHAMADAS"], TETO_CHAMADAS, doc.get("COM_200", 0), doc.get("ITENS_TOTAL", 0),
        len(doc.get("VIDEOS_COM_COMENTARIO") or []), API.redigir(doc.get("PAROU"), {ENV_CHAVE: chave or ""}) or "nao"))
    return 0 if doc.get("COM_200") else 4


if __name__ == "__main__":
    raise SystemExit(main())
