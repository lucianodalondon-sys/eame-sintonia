#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Escreve os contratos executaveis das fontes que o Curator onboarda.

    UM MOTOR, NAO DOIS.

Este ficheiro NAO inventa forma de contrato. Ele copia duas que ja existem e
ja foram provadas no repositorio:

  YOUTUBE_FEED   o molde de `IT-T8-001` em regras/italy_contracts.mjs —
                 ROUTE_TYPE=APPLICATION_ROUTE sobre as capacidades
                 `youtube.channel.discovery` / `youtube.video.metadata`, que
                 existem em coleta/adaptador_youtube.py e companhia.

  HTML_PUBLIC    o molde de `contratoGenerico()` — STRATEGY/MATCH/INDEX_URL/
                 LINK_PATTERN, OUTPUT_TYPE HTML, identidade pelo ENDERECO.

⚠️ POR QUE NAO SE ESTENDEU O `contratoGenerico()` PARA XML.
Medido: `ASSINATURA_POR_TIPO = { PDF, HTML }` — um OUTPUT_TYPE XML rebenta com
`OUTPUT_TYPE desconhecido`. A tentacao era acrescentar `XML: "<?xml"` e mandar
as 59 do YouTube por ali. Seria errado por duas razoes:

  1. o ficheiro e do COORDINATOR e esta a ser alterado AGORA (23 commits);
  2. um feed de YouTube nao e um documento XML que se baixa — e uma LISTAGEM
     de videos, e o item real e o video. Tratar o feed como documento poria no
     RAW o indice em vez do conteudo, que e exactamente o erro «listagem != item»
     ja corrigido na missao 02.

⚠️ E POR QUE ESTE FICHEIRO E SEPARADO.
`italy_contracts_onboarded.json` esta a ser escrito pelo COORDINATOR nesta
mesma janela. Escrever la garantia conflito mecanico. Aqui a tabela nasce
noutro ficheiro, com a mesma forma, e quem integra decide quando a importa:

    ZERO CONFLITO NAO E ZERO TRABALHO — E TRABALHO QUE NAO SE DESFAZ.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import emparelhar_com_atlas as EM  # noqa: E402

VERSAO = "SOURCE-CURATOR-CONTRACTS-V1"

# ─────────────────────────────────────────────────────────────────────────
# HTML: o padrao de link que distingue ITEM de LISTAGEM
# ─────────────────────────────────────────────────────────────────────────
# ⚠️ ESTE PADRAO E A LICAO DA MISSAO 02 ESCRITA EM REGEX. Sem ele o coletor
# guarda `/notizie` (o indice) e julga que colheu. Um item tem, no caminho,
# ou um slug com varias palavras ou um ano — coisas que um indice nao tem.
#
# ⚠️ E A SECCAO E OBRIGATORIA, NAO OPCIONAL. Primeira versao punha o grupo das
# seccoes como `(?:...)?` e o canario «passou» em 4 de 6 — com estes alvos:
#
#     IT-T7-017:URL:lavora-con-noi
#     IT-T7-029:URL:mappa-del-sito
#     IT-T12-009:URL:agenzia/amministrazione-trasparente/altri-contenuti
#
# Todos com HTTP 200, todos HTML valido, todos inuteis: paginas de recrutamento,
# mapa do site e transparencia administrativa. O contrato resolvia e o canario
# dizia PASS — o pior tipo de verde, o que confirma uma rota que traz lixo.
#
#     UM DOCUMENTO QUE CARREGA NAO E UM DOCUMENTO QUE INTERESSA.
#
# Exigir a seccao no caminho reduz o numero de fontes que passam e aumenta o
# numero de fontes que servem. Fonte que nao tem seccao reconhecivel cai em
# EMPTY_LIST e volta para amostragem — que e o sitio certo dela.
_SECOES = ("news|notizie|notizia|comunicat|articol|attualita|eventi|evento|"
           "bollettin|press|approfondiment|blog|pubblicazion|documenti|avvisi|"
           "primo-piano|in-evidenza|rassegna|agrometeo|monitoraggio|"
           "progetti|ricerca|pubblicazioni|tecnica|agricoltura")
_EXCLUI = ("category|tag|author|wp-json|wp-content|wp-admin|page|feed|rss|"
           "search|cerca|login|privacy|cookie|lavora-con-noi|mappa-del-sito|"
           "amministrazione-trasparente|contatti|chi-siamo|dove-siamo|"
           "note-legali|accessibilita|albo|trasparenza|concorsi|bandi-di-gara")


def link_pattern(url: str) -> str:
    host = urlparse(url).netloc.lower()
    base = re.escape(host.replace("www.", ""))
    # a seccao e OBRIGATORIA e o item tem de ter slug de 3+ palavras ou um ano
    return (r"^https?://(www\.)?%s/(?!(?:%s)(?:/|$))(?:[^?#]*/)?(?:%s)[^?#]*/"
            r"(?:[a-z0-9]+(?:-[a-z0-9]+){2,}|\d{4}[^?#]*)/?(?:[?#].*)?$"
            % (base, _EXCLUI, _SECOES))


def hash_do_contrato(c: dict) -> str:
    """SOURCE_CONTRACT_HASH: muda quando o contrato muda, e so entao."""
    return hashlib.sha256(
        json.dumps(c, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:16]


def contrato_youtube(n: dict, f: dict, native: str) -> dict:
    """Replica do molde IT-T8-001. NAO constroi rota nova."""
    return {
        "SOURCE_ID": n["SOURCE_ID"],
        "OWNER": re.sub(r"—.*$", "", n["NOME"]).strip(),
        "NAME": n["NOME"],
        "TERRITORY": n["TERRITORY"],
        "BATCH_ID": "LOTE-YOUTUBE-FEED",
        "OUTPUT_TYPE": "VIDEO_METADATA",
        "CANONICAL_ENTRY_URL": n["URL"],
        "SOURCE_NATIVE_ID": native or "NAO SEI",
        "SOURCE_NATIVE_ID_KIND": "YOUTUBE_CHANNEL_ID",
        "LEI_DA_IDENTIDADE": (
            "SOURCE_ID != CHANNEL_ID. %s e a identidade do projeto; %s e a da "
            "plataforma. O contrato liga as duas AQUI. Derivar SOURCE_ID do "
            "handle, da URL ou do proprio channel_id e proibido."
            % (n["SOURCE_ID"], native or "o channel_id")),
        "ACQUISITION": {
            "STRATEGY": "YOUTUBE_CHANNEL_FEED",
            "CHANNEL_ID": native or "NAO SEI",
            "FEED_URL": ("https://www.youtube.com/feeds/videos.xml?channel_id=%s"
                         % native) if native else "NAO SEI",
            "MAX_TARGETS": 15,
        },
        "CAPABILITIES_REUTILIZADAS": ["youtube.channel.discovery",
                                      "youtube.video.metadata"],
        "ROUTE_TYPE": "APPLICATION_ROUTE",
        "ACCESS_INSTRUMENT": "SCRAP",
        "AUTH_REQUIRED": False, "BROWSER_REQUIRED": False, "JS_REQUIRED": False,
        "SESSION_FORBIDDEN": "rota publica: sem cookie, sem login, sem sessao.",
        "IDENTITY": {
            "STRATEGY": "CONTENT_CAPTURE",
            "CAPTURES": {"video": {"FROM": "FEED", "FIELD": "yt:videoId"}},
            "DOCUMENT_ID": "%s:YT:{video.videoId}" % n["SOURCE_ID"],
            "FACT_TIME": ("UNKNOWN — published_at e PUBLICATION_TIME, nao FACT_TIME"),
        },
        "IDENTITY_KEYS": ["video_id", "published_at"],
        "IDENTITY_KIND": "PLATFORM_NATIVE_ID",
        "DOCUMENT_DATE_FIELD": "published (entry do feed)",
        "TIME_RULE": "published e PUBLICATION_TIME. NAO e FACT_TIME.",
        "FACT_LOCATION_RULE": ("UNKNOWN — canal italiano NAO prova facto ocorrido "
                               "em Italia. NUNCA inferir a partir do canal."),
        "EXPECTED_FAILURES": [
            "video sem videoId = FAILED por falta de identidade",
            "feed sem nenhuma <entry> = EMPTY_LIST -> FAILED",
            "canal privado/removido = FAILED, nao DEGRADED",
        ],
        "FAIL_CLOSED_RULE": ("item sem videoId ou sem published nao tem identidade "
                             "— FAILED. Nunca registar o FEED como documento."),
        "FALLBACK": "nenhum. Nao cair para yt-dlp nem para a Data API paga.",
        "NEGATIVE_CONTROL": {"descricao": "feed sem <entry>",
                             "esperado": "EMPTY_LIST -> FAILED"},
    }


def contrato_html(n: dict, f: dict) -> dict:
    """Replica do molde contratoGenerico(): STRATEGY/MATCH/INDEX_URL/LINK_PATTERN."""
    return {
        "SOURCE_ID": n["SOURCE_ID"],
        "OWNER": re.sub(r"—.*$", "", n["NOME"]).strip(),
        "NAME": n["NOME"],
        "TERRITORY": n["TERRITORY"],
        "BATCH_ID": "LOTE-HTML-ARTIGO",
        "OUTPUT_TYPE": "HTML",
        "CANONICAL_ENTRY_URL": n["URL"],
        "ACQUISITION": {
            "STRATEGY": "HTML_LINK_DISCOVERY",
            "MATCH": "URL",
            "INDEX_URL": n["URL"],
            "LINK_PATTERN": link_pattern(n["URL"]),
            "MAX_TARGETS": 1,
        },
        "ROUTE_TYPE": "DISCOVERED_ROUTE",
        "ACCESS_INSTRUMENT": "HTTP",
        "AUTH_REQUIRED": False, "BROWSER_REQUIRED": False, "JS_REQUIRED": False,
        "IDENTITY": {
            "STRATEGY": "CONTENT_CAPTURE",
            "CAPTURES": {"doc": {"FROM": "URL", "PATTERN": "^https?://[^/]+/?(.*?)/?$"}},
            "DOCUMENT_ID": "%s:URL:{doc.1}" % n["SOURCE_ID"],
            "FACT_TIME": ("UNKNOWN — identidade pelo endereco; a fonte nao expoe "
                          "data do facto por regra generica"),
        },
        "IDENTITY_KEYS": ["url_path"],
        "IDENTITY_KIND": "URL_PATH",
        "FACT_LOCATION_RULE": ("UNKNOWN por padrao — so preencher se o proprio "
                               "documento declarar; NUNCA inferir"),
        "EXPECTED_FAILURES": [
            "entrada inacessivel (403, 404, transporte) = FAILED, nunca zero documentos",
            "entrada sem endereco que case com LINK_PATTERN = EMPTY_LIST = FAILED",
            "documento cuja assinatura de bytes nao e HTML = BYTE_VALIDATION_FAILED",
        ],
        "FAIL_CLOSED_RULE": ("sem endereco descoberto ou com bytes que nao sao HTML, "
                             "e FAILED — nunca se regista a pagina de entrada como "
                             "documento"),
        "FALLBACK": "nenhum",
        "NEGATIVE_CONTROL": {"descricao": "entrada que nao lista nenhum endereco "
                                          "que case com LINK_PATTERN",
                             "esperado": "EMPTY_LIST -> FAILED"},
    }


def main() -> int:
    alloc = json.loads((RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json")
                       .read_text(encoding="utf-8"))
    car = json.loads((RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json")
                     .read_text(encoding="utf-8"))
    porid = {c["CANDIDATE_ID"]: c for c in car["FONTES"]}

    contratos, sem_contrato = [], []
    for n in alloc["NOVAS"]:
        f = porid[n["CANDIDATE_ID"]]

        # ⚠️ SO ENTRAM AS QUE NAO PEDEM CAPACIDADE NOVA. As 11 de «ramo de
        # indice» ficam de fora deste lote, por decisao de prioridade.
        if not str(f.get("SMALL_ADAPTATION_REQUIRED", "")).startswith("NAO"):
            sem_contrato.append({"SOURCE_ID": n["SOURCE_ID"],
                                 "CANDIDATE_ID": n["CANDIDATE_ID"],
                                 "PORQUE": f["SMALL_ADAPTATION_REQUIRED"]})
            continue

        if f["FAMILY"] == "YOUTUBE":
            native = EM.native_id_da_prova(f)
            if not native:
                # sem channel_id nao ha identidade de plataforma: nao se inventa
                sem_contrato.append({"SOURCE_ID": n["SOURCE_ID"],
                                     "CANDIDATE_ID": n["CANDIDATE_ID"],
                                     "PORQUE": "channel_id nao extraido da prova"})
                continue
            c = contrato_youtube(n, f, native)
        elif f["FAMILY"] == "HTML_SITE":
            c = contrato_html(n, f)
        else:
            sem_contrato.append({"SOURCE_ID": n["SOURCE_ID"],
                                 "CANDIDATE_ID": n["CANDIDATE_ID"],
                                 "PORQUE": "familia %s sem molde provado" % f["FAMILY"]})
            continue

        # a caracterizacao viaja com o contrato: o que se aprendeu nao se perde
        c["CARACTERIZACAO"] = {
            "ACTIVITY_STATE": f["ACTIVITY"],
            "INITIAL_COLLECTION_CADENCE": f["INITIAL_COLLECTION_CADENCE"],
            "CADENCE_REASON": f["CADENCE_REASON"],
            "EXPECTED_ITEMS_PER_WEEK": f["EXPECTED_ITEMS_PER_WEEK"],
            "EXPECTED_ITEMS_PER_MONTH": f["EXPECTED_ITEMS_PER_MONTH"],
            "CONTENT_VALUE_TYPE": f["CONTENT_VALUE_TYPE"],
            "TOPICS_OBSERVED": f["TOPICS_OBSERVED"],
            "GEOGRAPHIES_OBSERVED": f["GEOGRAPHIES_OBSERVED"],
            "LANGUAGES_OBSERVED": f.get("LANGUAGES_OBSERVED"),
            "HISTORICAL_DEPTH_OBSERVED": f["HISTORICAL_DEPTH_OBSERVED"],
            "SAMPLE_PERIOD": [f["SAMPLE_PERIOD_START"], f["SAMPLE_PERIOD_END"]],
            "REPRESENTATIVE_SAMPLE_COUNT": f["REPRESENTATIVE_SAMPLE_COUNT"],
            "SOURCE_PATTERN_STABLE": f["SOURCE_PATTERN_STABLE"],
            "CANONICAL_EXAMPLE": f["CANONICAL_EXAMPLE"],
            "CARACTERIZADA_EM": car["GERADO_EM"][:10],
        }
        c["SOURCE_CONTRACT_VERSION"] = VERSAO
        c["SOURCE_CONTRACT_HASH"] = hash_do_contrato(c)
        c["ONBOARDED_BY"] = ("SOURCE-CURATOR-04 · caracterizacao de 2026-09-20, "
                             "amostra representativa com %d itens reais"
                             % f["REPRESENTATIVE_SAMPLE_COUNT"])
        c["EVIDENCE"] = f["CANONICAL_EXAMPLE"]
        contratos.append(c)

    from collections import Counter
    saida = {
        "DATASET": VERSAO,
        "O_QUE_ISTO_E": ("contratos executaveis das fontes que o SOURCE CURATOR "
                         "onboardou. Mesma forma dos contratos existentes; "
                         "ficheiro separado para nao colidir com a missao activa."),
        "COMO_SE_IMPORTA": ("do lado do dono: ler este JSON e expandir como se faz "
                            "com italy_contracts_onboarded.json. O dono do contrato "
                            "continua a ser regras/italy_contracts.mjs."),
        "MOLDES_REUTILIZADOS": {
            "LOTE-YOUTUBE-FEED": ("molde de IT-T8-001 (APPLICATION_ROUTE sobre "
                                  "youtube.channel.discovery / video.metadata)"),
            "LOTE-HTML-ARTIGO": "molde de contratoGenerico() (HTML_LINK_DISCOVERY)",
        },
        "GERADO_EM": datetime.now(timezone.utc).isoformat(),
        "TOTAL": len(contratos),
        "POR_LOTE": dict(Counter(c["BATCH_ID"] for c in contratos)),
        "SEM_CONTRATO": sem_contrato,
        "FONTES": contratos,
    }
    p = RAIZ / "curadoria" / "italy_contracts_curator.json"
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("contratos criados  %d" % len(contratos))
    print("por lote           %s" % dict(Counter(c["BATCH_ID"] for c in contratos)))
    print("sem contrato       %d" % len(sem_contrato))
    print("escrito: %s" % p.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
