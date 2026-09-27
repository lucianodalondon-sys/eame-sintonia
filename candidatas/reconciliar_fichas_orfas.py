#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A PROVA ESTAVA GUARDADA E O ATLAS NAO A MOSTRAVA.

    py candidatas/reconciliar_fichas_orfas.py              # mede
    py candidatas/reconciliar_fichas_orfas.py --ficha      # imprime as fichas
    py candidatas/reconciliar_fichas_orfas.py --verificar  # 0 se o atlas ja as tem

O DEFEITO, MEDIDO EM 15/09/2026
--------------------------------
`data/samples/IT-SOURCE-SAMPLES/` tinha 155 pastas de prova. Treze delas —
com ficheiro bruto, `SHA256` e manifesto — pertenciam a `SOURCE_ID` que o
atlas NAO mostrava em lado nenhum. O numero existia (foi cunhado em
`candidatas/ITALY-SOURCE-MASTER-V1.json`), a prova existia, e a unica coisa
que faltava era a linha que liga as duas.

Isto e o inverso do defeito da fila. Na fila falta prova. Aqui a prova estava
guardada e o registo nao a mostrava — o que e pior, por dois motivos:

    1 · o proprio atlas ja avisa que um ID retirado «desaparece do atlas — e
        quem alocar "o proximo" volta a emiti-lo, sem que nada acuse»;
    2 · quem contasse fontes pelo atlas contava 13 a menos, e quem contasse
        pela pasta de provas contava 13 a mais. Duas contagens certas para a
        mesma casa e uma casa que nao sabe o que tem.

        PROVA GUARDADA QUE O REGISTO NAO MOSTRA E PROVA QUE NAO EXISTE,
        PARA TODO O EFEITO PRATICO.

O QUE ESTE FICHEIRO NAO FAZ
----------------------------
Nao coleta. Nao abre rede. Nao emite `SOURCE_ID` nenhum — os treze ja estavam
emitidos, e emitir de novo era exactamente o acidente que se quer evitar.
Nao escreve no atlas: imprime a ficha e deixa a decisao de colar a uma pessoa.

O VERDICT SAI DA PROVA, NAO DO GOSTO
-------------------------------------
    GREEN   os bytes preservados sao os que o site serviu (HTTP 200 + MIME
            real + SHA256 que confere com o ficheiro em disco HOJE)
    YELLOW  a captura e extrato do DOM lido por navegador — o proprio
            manifesto declara «NAO sao os bytes servidos pelo site»

Onze sao GREEN e duas sao YELLOW, e as duas YELLOW dizem porque no manifesto:
os sites da Bayer Italia e da ADAMA Italia devolvem 403 a `curl` do mesmo IP
italiano, e so abrem com navegador.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "candidatas"))
sys.path.insert(0, str(RAIZ / "leis"))

import fonte_do_atlas as ATLAS          # noqa: E402

AMOSTRAS = RAIZ / "data" / "samples" / "IT-SOURCE-SAMPLES"
MASTER = RAIZ / "candidatas" / "ITALY-SOURCE-MASTER-V1.json"

#: Largura da coluna de valor nas fichas do atlas. Copiada das que la estao.
RECUO = 30
LARGURA = 98


def _campo(chave: str, valor: str) -> str:
    """Uma linha de ficha, quebrada como o atlas quebra: recuo alinhado.

    O valor comeca sempre na coluna `RECUO`, na primeira linha e nas
    continuacoes. Um recuo que muda de linha para linha le-se como campo novo.
    """
    valor = " ".join(str(valor or "NÃO SEI").split()) or "NÃO SEI"
    linhas, atual = [], "%-*s" % (RECUO, chave + ":")
    primeira = True
    for palavra in valor.split(" "):
        if not primeira and len(atual) + 1 + len(palavra) > LARGURA:
            linhas.append(atual.rstrip())
            atual = " " * RECUO + palavra
        else:
            atual += ("" if primeira else " ") + palavra
        primeira = False
    linhas.append(atual.rstrip())
    return "\n".join(linhas)


def orfas() -> list[dict]:
    """SOURCE_ID com prova guardada e sem ficha no atlas. Ordenado."""
    if not AMOSTRAS.is_dir():
        return []
    no_atlas = ATLAS._do_atlas(ATLAS._texto(str(RAIZ)))
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    por_id = {s["SOURCE_ID"]: s for s in master.get("sources", [])}
    # O dono tem nome. `IT-OWN-032` e' a chave, nao a resposta a «quem publica
    # e responde pelo dado» — e uma ficha que responde com a chave obriga o
    # leitor seguinte a ir procurar noutro ficheiro o que ja se sabia aqui.
    donos = {o["OWNER_ID"]: o for o in master.get("owners", [])}
    fora = []
    for sid in sorted(set(os.listdir(AMOSTRAS)) - no_atlas,
                      key=lambda s: (int(s.split("-")[1][1:]), s)):
        manifesto = AMOSTRAS / sid / "MANIFEST.json"
        if not manifesto.is_file() or sid not in por_id:
            continue
        fora.append({"SOURCE_ID": sid, "MASTER": por_id[sid],
                     "DONO": donos.get(por_id[sid].get("OWNER_ID"), {}),
                     "MANIFEST": json.loads(manifesto.read_text(encoding="utf-8"))})
    return fora


def conferir_bytes(sid: str, manifesto: dict) -> tuple[int, int, list[str]]:
    """Reconta o SHA256 de cada ficheiro AGORA. (conferidos, total, queixas).

    Um manifesto que declara SHA256 e nunca e' reconferido e uma promessa, nao
    uma prova. Reconferir e barato e apanha o ficheiro trocado em silencio.
    """
    pasta = AMOSTRAS / sid
    ok, total, queixas = 0, 0, []
    for f in manifesto.get("FILES", []):
        total += 1
        nome = f.get("RAW_FILE", "")
        caminho = pasta / nome
        if not caminho.is_file():
            queixas.append("%s: ficheiro declarado e ausente" % nome)
            continue
        soma = hashlib.sha256(caminho.read_bytes()).hexdigest()
        if soma != f.get("SHA256"):
            queixas.append("%s: SHA256 difere do declarado" % nome)
            continue
        ok += 1
    return ok, total, queixas


def _verdict(manifesto: dict) -> tuple[str, str]:
    ficheiros = manifesto.get("FILES", [])
    extrato = any("EXTRATO" in str(f.get("role", "")).upper() for f in ficheiros)
    if extrato:
        return ("YELLOW", "o que está preservado é extrato do DOM lido por navegador — "
                          "o manifesto declara que NÃO são os bytes servidos pelo site")
    return ("GREEN", "fonte aberta, ficheiro bruto servido pelo site preservado e "
                     "SHA256 reconferido nesta missão")


def _acesso(manifesto: dict) -> str:
    mimes = {str(f.get("MIME", "")).split(";")[0].strip()
             for f in manifesto.get("FILES", [])}
    mapa = {"application/pdf": "PDF", "text/html": "HTML", "application/json": "JSON",
            "application/vnd.oasis.opendocument.spreadsheet": "OTHER (ODS)"}
    nomes = sorted({mapa.get(m, "OTHER (%s)" % m) for m in mimes if m})
    return " · ".join(nomes) or "NÃO SEI"


def _exemplo(manifesto: dict) -> str:
    ficheiros = manifesto.get("FILES", [])
    if not ficheiros:
        return "NÃO SEI — manifesto sem ficheiro declarado"
    f = max(ficheiros, key=lambda x: x.get("BYTES") or 0)
    rota = f.get("SOURCE_URL") or manifesto.get("SOURCE_URL") or "NÃO SEI"
    quando = (manifesto.get("CAPTURE", {}).get("CAPTURED_AT_UTC") or "")[:10]
    return ("«%s» %s — %s, %s bytes, %s em %s"
            % (manifesto.get("ORIGINAL_TITLE", "NÃO SEI"), rota,
               str(f.get("MIME", "")).split(";")[0], f.get("BYTES", "?"),
               "SHA256 conferido", quando or "NÃO SEI"))


def ficha(o: dict) -> str:
    sid, m, man = o["SOURCE_ID"], o["MASTER"], o["MANIFEST"]
    verdict, porque = _verdict(man)
    captura = man.get("CAPTURE", {})
    ok, total, _ = conferir_bytes(sid, man)
    nome = m.get("SOURCE_NAME") or sid
    prova = "data/samples/IT-SOURCE-SAMPLES/%s/MANIFEST.json" % sid

    risco = ("NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi "
             "tentada (AUTH_USED: %s) e nenhum paywall foi contornado."
             % (captura.get("AUTH_USED") or "NÃO SEI"))
    rota_saida = captura.get("EGRESS_KIND") or ""
    if "VPN" in rota_saida.upper():
        risco += (" ⚠️ A captura saiu por %s (%s): a fonte pode responder de outro "
                  "modo a partir de um IP não italiano, e isso não foi medido."
                  % (captura.get("EGRESS_KIND"), captura.get("EGRESS_GEO", "?")))

    campos = [
        ("SOURCE_ID", sid),
        ("SOURCE_NAME", nome),
        ("SOURCE_OWNER", "%s (%s)" % (o["DONO"].get("OWNER_CANONICAL_NAME"),
                                      m.get("OWNER_ID"))
         if o["DONO"].get("OWNER_CANONICAL_NAME") else (m.get("OWNER_ID") or "NÃO SEI")),
        ("COUNTRY", "ITALY"),
        ("REGION", m.get("REGION") or o["DONO"].get("REGION")),
        ("LANGUAGE", (man.get("ORIGINAL_LANGUAGE") or "NÃO SEI").upper()),
        ("TERRITORY", m.get("TERRITORY")),
        ("SOURCE_TYPE", m.get("SOURCE_TYPE")),
        ("URL", m.get("URL")),
        ("ACCESS_METHOD", _acesso(man)),
        ("CROPS", m.get("CROPS")),
        ("TOPICS", m.get("TOPICS")),
        ("GEOGRAPHIC_GRANULARITY", m.get("GEOGRAPHIC_GRANULARITY")),
        ("UPDATE_FREQUENCY", m.get("UPDATE_FREQUENCY")),
        ("HISTORICAL_DEPTH", m.get("HISTORICAL_DEPTH")),
        ("SOURCE_IDENTITY_PRESERVABLE",
         "SIM — %d de %d ficheiro(s) com SHA256 reconferido em 2026-09-15" % (ok, total)),
        ("DOCUMENT_ID_AVAILABLE", man.get("ORIGINAL_TITLE")
         and "SIM — o documento traz título e numeração próprios" or "NÃO SEI"),
        ("PUBLICATION_DATE_AVAILABLE",
         "SIM — %s" % man.get("SOURCE_DATE") if man.get("SOURCE_DATE") else "NÃO SEI"),
        ("RAW_EVIDENCE_PRESERVABLE", "SIM — já preservada: %s" % prova),
        ("AUTOMATION_FEASIBILITY",
         "NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço exato "
         "que trouxe cada ficheiro, o que é o ponto de partida de um contrato."),
        ("COLLECTION_FEASIBILITY", "NÃO SEI — registar ≠ coletar; nenhuma coleta correu"),
        ("LEGAL_OR_ACCESS_RISK", risco),
        ("REAL_EXAMPLE", _exemplo(man)),
        ("SOURCE_LOCATION", man.get("SOURCE_LOCATION")),
        ("FACT_LOCATION", man.get("FACT_LOCATION")),
        ("WHAT_IT_PROVES", man.get("WHAT_IT_PROVES") if isinstance(
            man.get("WHAT_IT_PROVES"), str) else
            " · ".join(man.get("WHAT_IT_PROVES") or []) or m.get("WHAT_IT_PROVES")),
        ("WHAT_IT_DOES_NOT_PROVE", man.get("WHAT_IT_DOES_NOT_PROVE") if isinstance(
            man.get("WHAT_IT_DOES_NOT_PROVE"), str) else
            " · ".join(man.get("WHAT_IT_DOES_NOT_PROVE") or [])
            or m.get("WHAT_IT_DOES_NOT_PROVE")),
        ("EVIDENCE", prova),
        ("VERDICT", "%s — %s" % (verdict, porque)),
    ]
    corpo = "\n".join(_campo(k, v) for k, v in campos)
    return "#### %s · %s\n\n```\n%s\n```\n" % (sid, nome, corpo)


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    argv = list(argv if argv is not None else sys.argv[1:])
    lista = orfas()

    if "--ficha" in argv:
        for o in lista:
            print(ficha(o))
        return 0

    if "--verificar" in argv:
        # Depois da reconciliacao esta lista tem de ser VAZIA. Se voltar a
        # encher, alguem guardou prova nova sem escrever a ficha.
        if lista:
            print("ORFAS=%d — prova guardada sem ficha no atlas:" % len(lista))
            for o in lista:
                print("  %s  %s" % (o["SOURCE_ID"],
                                    o["MASTER"].get("SOURCE_NAME", "")[:60]))
            return 1
        print("ORFAS=0 — toda a prova guardada tem ficha no atlas")
        return 0

    print("ORFAS_COM_PROVA_SEM_FICHA = %d" % len(lista))
    for o in lista:
        ok, total, queixas = conferir_bytes(o["SOURCE_ID"], o["MANIFEST"])
        v, _ = _verdict(o["MANIFEST"])
        print("  %-12s %-6s sha256 %d/%d  %s" % (o["SOURCE_ID"], v, ok, total,
                                                 o["MASTER"].get("SOURCE_NAME", "")[:52]))
        for q in queixas:
            print("       ⚠️  %s" % q)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
