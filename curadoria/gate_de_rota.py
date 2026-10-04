#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GATE DE ROTA: reprova quem chega a rede por caminho em `Disallow`.

    ROTA QUE RESPONDE != ROTA PERMITIDA.

Medido nesta missao, no `robots.txt` vivo de `www.youtube.com`:

    User-agent: *
    Disallow: /feeds/videos.xml        <- linha 12, literal

Os 50 contratos YouTube da missao 04 usam exactamente esse caminho. Eles
funcionam: 50 canarios em 50 devolveram XML com videoId e data. E e isso que
torna o erro perigoso — a rota responde com HTTP 200, entrega conteudo bom, e
esta barrada na mesma.

⚠️ O REPOSITORIO JA TINHA DITO ISTO, COM ESTAS PALAVRAS:

    coleta/scrap_http.py:31
    «E o portao ja REPROVOU rota que funcionava: o `feeds/videos.xml` do
     YouTube devolveu 15 videos italianos com descricao inteira nesta
     maquina, e esta em Disallow. Ele nao entrou. E para isso que o portao
     serve — se ele so aprovasse, nao seria portao.»

    coleta/adaptador_youtube.py:756
    nota='playlistItems.list; o feeds/videos.xml foi reprovado pelo portao'

Eu citei `youtube.channel.discovery` como capacidade reutilizada nos 50
contratos — e essa capacidade usa `playlistItems.list`, a API oficial com
chave. NAO usa o feed. Escrevi o nome certo por cima da rota errada, e o
nome tranquilizou-me.

    CITAR UMA CAPACIDADE NAO E USA-LA.
    O contrato dizia `youtube.channel.discovery` e o codigo fazia urlopen()
    directo no caminho proibido, sem passar por `permitido()`.

O que este ficheiro faz: reclassifica, sem apagar. SOURCE_ID, ficha do Atlas,
caracterizacao e contrato ficam todos de pe — o que cai e so a afirmacao
«pronta para coleta», que era a unica que nao estava provada.
"""
from __future__ import annotations

import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import capturador as CAP  # noqa: E402

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def robots_de(host: str) -> tuple[urllib.robotparser.RobotFileParser, str]:
    """Le o robots.txt VIVO. Nao decorado, nao presumido.

    ⚠️ LER NA HORA E A REGRA DA CASA (`scrap_http.py`): «O ROBOTS E LIDO NA
    HORA, NAO DECORADO NO CODIGO.» Um Disallow copiado para uma constante
    envelhece em silencio.

    ⚠️ E 404 NO ROBOTS NAO E «PROIBIDO». Medido: um dos hosts HTML devolve
    404 em /robots.txt. Um site que nunca escreveu robots.txt nao proibiu
    nada — a norma diz que ausencia de ficheiro e permissao. Tratar 404 como
    bloqueio reprovaria fontes boas por um ficheiro que nao existe; tratar
    erro de REDE como permissao aprovaria as barradas quando a rede falha.
    As duas coisas sao diferentes e ficam separadas.

        AUSENCIA DE REGRA != REGRA DE AUSENCIA.
    """
    url = "https://%s/robots.txt" % host
    req = urllib.request.Request(url, headers={"User-Agent": CAP.UA})
    rp = urllib.robotparser.RobotFileParser()
    # ⚠️ UMA SO TENTATIVA CONDENA POR LENTIDAO. Medido: `nomisma.it` esgotou o
    # tempo a primeira vez e foi classificado «barrado»; a segunda leitura
    # devolveu HTTP 200 em 1,2 s com `Disallow:` VAZIO — ou seja, permite tudo.
    # Um timeout nao e um Disallow, e condenar por ele e o mesmo erro do
    # Facebook noutra roupa: culpar a fonte por defeito do nosso lado.
    ultimo = None
    for tentativa, espera in ((1, 25), (2, 45)):
        try:
            with urllib.request.urlopen(req, timeout=espera, context=CTX) as r:
                txt = r.read().decode("utf-8", "replace")
            rp.parse(txt.splitlines())
            return rp, txt
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                rp.parse([])                   # sem ficheiro = sem proibicao
                return rp, "HTTP %d — o host nao publica robots.txt" % e.code
            # 401/403 no proprio robots: a norma manda tratar como Disallow total
            rp.parse(["User-agent: *", "Disallow: /"])
            return rp, "HTTP %d no robots.txt — tratado como Disallow total" % e.code
        except Exception as e:
            ultimo = e
            time.sleep(2)
    # ⚠️ NAO SEI != PERMITIDO. Rede em baixo nao liberta ninguem — mas o estado
    # que se regista e UNKNOWN, nao DISALLOWED: a fonte nao foi condenada, foi
    # deixada por medir.
    rp.parse(["User-agent: *", "Disallow: /"])
    return rp, ("robots inacessivel apos 2 tentativas (%s) — UNKNOWN, tratado "
                "como barrado por prudencia" % type(ultimo).__name__)


def permitido(url: str, rp) -> bool:
    return rp.can_fetch(CAP.UA, url)


def main() -> int:
    ready = json.loads((RAIZ / "curadoria" / "READY-FOR-COLLECTION-V1.json")
                       .read_text(encoding="utf-8"))
    contr = json.loads((RAIZ / "curadoria" / "italy_contracts_curator.json")
                       .read_text(encoding="utf-8"))
    porsid = {c["SOURCE_ID"]: c for c in contr["FONTES"]}

    # um robots por host, lido uma vez
    cache, evid = {}, {}
    def rp_de(url):
        host = re.match(r"^https?://([^/]+)", url).group(1)
        if host not in cache:
            cache[host], evid[host] = robots_de(host)
        return cache[host], host

    conta, mudados = Counter(), []
    for f in ready["FONTES"]:
        c = porsid[f["SOURCE_ID"]]
        aq = c["ACQUISITION"]
        alvo = aq.get("FEED_URL") or aq.get("INDEX_URL") or aq.get("URL")
        rp, host = rp_de(alvo)
        ok = permitido(alvo, rp)
        # ⚠️ «BARRADO PORQUE LI O DISALLOW» != «BARRADO PORQUE NAO CONSEGUI LER».
        # Os dois impedem a coleta, mas so o primeiro e um facto sobre a fonte.
        # O segundo e uma medida que falta — e quem integrar tem de saber a
        # diferenca, porque uma resolve-se com politica e a outra com uma
        # segunda tentativa.
        por_medir = "UNKNOWN" in evid.get(host, "")

        f["ROUTE_URL"] = alvo
        f["ROBOTS_GATE_EXECUTED"] = "YES"
        f["ROBOTS_GATE_RESULT"] = ("ALLOWED" if ok else
                                   ("UNKNOWN_TREATED_AS_BLOCKED" if por_medir
                                    else "DISALLOWED"))
        f["ROBOTS_HOST"] = host

        if ok:
            conta["ROUTE_LEGAL"] += 1
            continue

        conta["ROUTE_UNKNOWN" if por_medir else "ROUTE_ILLEGAL"] += 1
        if f["STATE"] == "READY_FOR_COLLECTION":
            # ⚠️ NAO SE APAGA NADA. O que cai e so a prontidao.
            f["STATE"] = "CONTRACT_READY_ROUTE_BLOCKED"
            f["CANONICAL_ROUTE_READY"] = "NO"
            f["BLOCK_REASON"] = ("ROBOTS_UNREADABLE" if por_medir
                                 else "ROBOTS_DISALLOWED_ROUTE")
            f["REASON"] = (
                ("o robots.txt de %s nao respondeu em duas tentativas — nao se "
                 "provou proibicao nenhuma, mas tambem nao se provou permissao. "
                 "Barrado por prudencia, nao por veredito." % host)
                if por_medir else
                ("o canario passou e a rota esta barrada: %s casa com Disallow no "
                 "robots.txt vivo de %s. HTTP 200 nao torna uma rota permitida."
                 % (alvo.split("?")[0], host)))
            mudados.append(f["SOURCE_ID"])
        # a caracterizacao e o contrato continuam validos
        f["SOURCE_CHARACTERIZED"] = f.get("SOURCE_CHARACTERIZED", "YES")
        f["CONTRACT_VALID"] = f.get("CONTRACT_VALID", "YES")

    novo_ready = [f for f in ready["FONTES"] if f["STATE"] == "READY_FOR_COLLECTION"]
    ready["FUNIL"]["READY_FOR_COLLECTION"] = len(novo_ready)
    ready["FUNIL"]["ROUTE_BLOCKED_BY_ROBOTS"] = len(mudados)
    ready["POR_ESTADO"] = dict(Counter(f["STATE"] for f in ready["FONTES"]))
    ready["READY_POR_LOTE"] = dict(Counter(f["BATCH_ID"] for f in novo_ready))
    ready["READY_POR_TERRITORIO"] = dict(sorted(
        Counter(f["TERRITORY"] for f in novo_ready).items()))
    ready["READY_POR_CADENCIA"] = dict(Counter(
        f["INITIAL_COLLECTION_CADENCE"] for f in novo_ready))
    ready["READY_POR_ACTIVIDADE"] = dict(Counter(
        f["ACTIVITY_STATE"] for f in novo_ready))
    ready["GATE_DE_ROTA"] = {
        "CORRIDO_EM": datetime.now(timezone.utc).isoformat(),
        "LEI": "ROTA QUE RESPONDE != ROTA PERMITIDA",
        "ROBOTS_LIDO_NA_HORA": sorted(cache),
        "ROUTE_LEGAL": conta["ROUTE_LEGAL"],
        "ROUTE_ILLEGAL": conta["ROUTE_ILLEGAL"],
        "ROUTE_UNKNOWN": conta["ROUTE_UNKNOWN"],
        "RECLASSIFICADOS": mudados,
        "O_QUE_NAO_FOI_APAGADO": ("SOURCE_ID, ficha no Atlas, caracterizacao, "
                                  "contrato e canario ficam todos de pe"),
        "EVIDENCIA": {h: ([l for l in t.splitlines() if l.startswith("Disallow")][:24]
                          or [t.splitlines()[0] if t else "(sem Disallow)"])
                      for h, t in evid.items()},
    }
    (RAIZ / "curadoria" / "READY-FOR-COLLECTION-V1.json").write_text(
        json.dumps(ready, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("robots lidos ao vivo   %s" % sorted(cache))
    print("ROUTE_LEGAL            %d" % conta["ROUTE_LEGAL"])
    print("ROUTE_ILLEGAL          %d  (Disallow lido)" % conta["ROUTE_ILLEGAL"])
    print("ROUTE_UNKNOWN          %d  (robots ilegivel)" % conta["ROUTE_UNKNOWN"])
    print("reclassificados        %d" % len(mudados))
    print("-" * 46)
    print("READY antes do gate    %d" % (len(novo_ready) + len(mudados)))
    print("READY depois do gate   %d" % len(novo_ready))
    print("por estado             %s" % ready["POR_ESTADO"])
    print("READY por lote         %s" % ready["READY_POR_LOTE"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
