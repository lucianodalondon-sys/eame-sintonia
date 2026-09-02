#!/usr/bin/env python3
"""Estado de aprovacao EU das substancias ativas, lido do ato legal.

A EU Pesticides Database continua fechada a este ambiente: toda rota de dados
devolve 307 para sorry.ec.europa.eu, com ou sem cabecalho de navegador. Em vez de
declarar o gap e parar, esta coleta vai a fonte que a base apenas publica: o
Regulamento de Execucao (UE) 540/2011, cujo ANEXO E a lista legal das substancias
ativas aprovadas, com data de aprovacao e data de expiracao por substancia.

    ./scripts/adama_it_eu.py

O que este ato prova:  APPROVED e a data de expiracao da aprovacao.
O que ele NAO prova:   RENEWAL_UNDER_REVIEW, DRAFT_NON_RENEWAL, ARTICLE_21_REVIEW.
                       Esses vivem em SCoPAFF e EFSA, e continuam UNKNOWN aqui.

Ausencia do anexo tambem nao prova nao-renovacao: a substancia pode nunca ter sido
aprovada, ou ter saido por ato que nao foi lido. Ausente => UNKNOWN, nunca NON_RENEWED.
"""
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime

OUT = "research/adama-italy-product-intelligence-deep"
RAW = "data/raw/EU-540-2011"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
HIS = "https://eur-lex.europa.eu/legal-content/EN/HIS/?uri=CELEX:32011R0540"
TXT = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:%s"

MESES = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}


def _curl(url, dest=None):
    cmd = ["curl", "-sSL", "-m", "180", "-A", UA, "--retry", "4", "--retry-delay", "2", url]
    if dest:
        subprocess.run(cmd + ["-o", dest], check=True)
        return None
    return subprocess.run(cmd, check=True, capture_output=True, text=True,
                          errors="replace").stdout


def versao_mais_recente():
    """A consolidacao muda; fixar a data no codigo daria leitura velha sem aviso."""
    his = _curl(HIS)
    vs = sorted(set(re.findall(r"0?2011R0540-(\d{8})", his)))
    if not vs:
        sys.exit("nenhuma versao consolidada encontrada no historico do EUR-Lex")
    return vs[-1]


def _data(txt):
    m = re.search(r"(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})", txt)
    if not m or m.group(2) not in MESES:
        return None
    return date(int(m.group(3)), MESES[m.group(2)], int(m.group(1))).isoformat()


def parsear(html):
    """Cada linha do anexo tem: nome comum (com CAS/CIPAC), IUPAC, pureza,
    data de aprovacao, data de expiracao, disposicoes especificas."""
    linhas = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S)
    saida = {}
    for tr in linhas:
        celulas = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", td)).strip()
                   for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(celulas) < 5:
            continue
        # a celula do nome comum e a que traz CAS ou CIPAC junto
        idx = next((i for i, c in enumerate(celulas[:3]) if re.search(r"CAS No|CIPAC No", c)), None)
        if idx is None:
            continue
        nome = re.split(r"CAS No|CIPAC No", celulas[idx])[0].strip(" ,;")
        nome = re.sub(r"\s*\(.*?\)\s*$", "", nome).strip()
        if not nome or len(nome) > 90:
            continue
        datas = [(i, _data(c)) for i, c in enumerate(celulas) if _data(c)]
        aprov = expira = None
        if len(datas) >= 2:
            aprov, expira = datas[0][1], datas[1][1]
        elif len(datas) == 1:
            aprov = datas[0][1]
        saida.setdefault(nome.upper(), {
            "COMMON_NAME": nome,
            "EU_STATE": "APPROVED",
            "DATE_OF_APPROVAL": aprov,
            "EXPIRATION_OF_APPROVAL": expira,
            "CAS": (re.search(r"CAS No:?\s*([0-9-]+)", celulas[idx]) or [None, None])[1],
            "CIPAC": (re.search(r"CIPAC No:?\s*([0-9]+)", celulas[idx]) or [None, None])[1],
        })
    return saida


def main():
    versao = versao_mais_recente()
    celex = "02011R0540-" + versao
    os.makedirs(RAW, exist_ok=True)
    destino = os.path.join(RAW, celex + ".html")
    if not os.path.exists(destino):
        _curl(TXT % celex, destino)
    with open(destino, encoding="utf-8", errors="replace") as fh:
        html = fh.read()
    subst = parsear(html)

    pacote = {
        "SOURCE": "Regulamento de Execucao (UE) n. 540/2011 — Anexo, texto consolidado",
        "SOURCE_URL": TXT % celex,
        "CELEX": celex,
        "CONSOLIDATION_DATE": "%s-%s-%s" % (versao[:4], versao[4:6], versao[6:]),
        "READ_AT": date.today().isoformat(),
        "AUTHORITY_CLASS": "OFFICIAL_EU_LEGAL_ACT",
        "WHAT_IT_PROVES": ["APPROVED", "DATE_OF_APPROVAL", "EXPIRATION_OF_APPROVAL"],
        "WHAT_IT_DOES_NOT_PROVE": [
            "RENEWAL_UNDER_REVIEW", "DRAFT_NON_RENEWAL", "ARTICLE_21_REVIEW",
            "ausencia no anexo nao prova NON_RENEWED",
            "estado EU nao prova comercializacao na Italia",
        ],
        "RULES": ["EXTENSION != RENEWAL", "DRAFT != DECISION", "REVIEW != RESTRICTION",
                  "EU STATUS != ITALIAN MARKETABILITY"],
        "COUNT": len(subst),
        "SUBSTANCES": subst,
    }
    os.makedirs(OUT, exist_ok=True)
    caminho = os.path.join(OUT, "EU-SOURCE-540-2011.json")
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump(pacote, fh, ensure_ascii=False, indent=2)
    print("EU 540/2011 (%s): %d substancias -> %s" % (pacote["CONSOLIDATION_DATE"], len(subst), caminho))
    return pacote


if __name__ == "__main__":
    main()
