#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atribui TERRITORIO e SOURCE_ID as fontes novas, pela lei do Atlas.

    SOURCE_ID VEM DO ATLAS. NUNCA DA URL, DO HANDLE, DO SLUG OU DO HASH.

O numero e `<PAIS>-T<territorio>-<sequencia>`. Nada nele se deriva do
endereco: o endereco muda e a identidade nao. O que ele codifica e a que
TERRITORIO (T1..T12) a fonte pertence, e isso le-se no que ela publica.

⚠️ A SEQUENCIA CONTINUA DE ONDE O ATLAS PAROU, E NUNCA RECICLA.
Um numero que ja foi de alguem nao volta a ser de outra fonte — dar um numero
gasto a uma fonte diferente parte o historico em dois. Por isso o proximo
numero de cada territorio nasce do MAIOR ja existente + 1, mesmo que haja
buracos no meio.

⚠️ TERRITORIO E DECISAO DE CONTEUDO, NAO DE PLATAFORMA.
Um canal de YouTube de uma universidade e T5 (SCIENCE), nao T8. T8 e para
quem a PLATAFORMA e a natureza da fonte — creators, influencers, testatas
nativas de video. Quando a evidencia nao chega para decidir, o territorio
fica `NAO SEI` e a fonte nao recebe numero: e melhor uma fonte sem numero
do que um numero no territorio errado.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import emparelhar_com_atlas as EM  # noqa: E402

# Os 12 territorios, como o Atlas os define. A chave e o que MEDIMOS na
# caracterizacao (CONTENT_VALUE_TYPE); o valor e o territorio do Atlas.
TERRITORIO_POR_TEMA = {
    "PHYTOSANITARY": "T3",            # PEST / DISEASE / WEEDS
    "CLIMATE": "T2",                  # CLIMATE / WATER / SOIL
    "REGULATORY": "T4",               # REGULATORY
    "SCIENCE": "T5",                  # SCIENCE
    "MARKET": "T10",                  # MARKET / TRADE / INDUSTRY
    "TECHNICAL_FIELD_SIGNAL": "T7",   # TECHNICAL NETWORK
    "COMPETITOR_COMMUNICATION": "T9",  # COMPETITORS
    "PORTFOLIO": "T9",                # portfolio de concorrente
    "AGRICULTURAL_NEWS": "T8",        # FARMERS & INFLUENCERS / media
}

# Sinais no NOME da fonte que mandam mais que o tema medido: dizem O QUE A
# FONTE E, e nao apenas do que ela falou na amostra.
#
# ⚠️ POR QUE O NOME MANDA MAIS QUE O TEMA. Medido: «Conserve Italia» (uma
# conserveira) falou de clima em 2 dos 3 videos da amostra e ia para T2
# (CLIMATE / WATER / SOIL), ao lado dos servicos meteorologicos regionais.
# «WineNews» (um jornal de vinho) ia pelo mesmo caminho. O tema mede DO QUE A
# FONTE FALOU NAQUELA SEMANA; o territorio pergunta O QUE A FONTE E.
#
#     UMA EMPRESA QUE FALA DE CLIMA NAO E UM SERVICO CLIMATICO.
#     UM JORNAL QUE COBRE SECA NAO E UMA ESTACAO METEOROLOGICA.
#
# Uma fonte na gaveta errada nao da erro: da uma consulta a T2 que devolve
# uma conserveira, e ninguem percebe porque o resultado esta estranho.
_ENTIDADE = [
    (re.compile(r"\b(universit|unina|unipi|unirc|dipartiment|facolt|cnr|crea|"
                r"istitut[oi]\b|ricerc|fondazion)", re.I), "T5"),
    (re.compile(r"\b(arpa|arpae|meteo|agrometeo|idrolog)", re.I), "T2"),
    (re.compile(r"\b(fitosanitar|servizio fitosanitario|difesa)", re.I), "T3"),
    (re.compile(r"\b(consorzio|cooperativ|confcooperative|associazion|assosementi|"
                r"federazion|feder[a-z]+|confagricoltura|coldiretti|cia\b|copagri|"
                r"unacoma|ordine|conaf|collegio|georgofili)", re.I), "T7"),
    (re.compile(r"\b(borsa|mercat|camera di commercio|granaria|prezzi|myfruit)", re.I), "T10"),
    (re.compile(r"\b(fiera|salone|expo|agrilevante|eima|macfrut|vinitaly|sana)\b", re.I), "T11"),
    (re.compile(r"\b(region[ei]|provincia|assessorat|ministero|agenzia regional|"
                r"arsac|arsial|assam|ersa|psr\b)", re.I), "T12"),
    # media e editoras: a fonte E um meio de comunicacao, independentemente do
    # assunto do dia
    (re.compile(r"\b(notizie|news|giornale|rivista|informatore|terra e vita|"
                r"edagricole|agronotizie|corriere|sole 24|agrisole)", re.I), "T8"),
    # empresas e marcas: T9 (COMPETITORS) e o territorio de quem VENDE, mesmo
    # quando comunica ciencia ou clima
    (re.compile(r"\b(s\.?p\.?a\.?|s\.?r\.?l\.?|group|gruppo|italia\b)", re.I), "T9"),
]


def territorio_de(c: dict) -> tuple[str, str]:
    """Devolve (territorio, porque). `NAO SEI` quando a evidencia nao chega."""
    nome = "%s %s" % (c.get("NOME", ""), c.get("URL", ""))
    for rx, t in _ENTIDADE:
        if rx.search(nome):
            return t, ("o nome da fonte diz o que ela E: «%s» -> %s"
                       % (rx.search(nome).group(0), t))

    temas = [t for t in c.get("CONTENT_VALUE_TYPE", []) if t != "UNKNOWN"]
    if temas:
        t = TERRITORIO_POR_TEMA.get(temas[0])
        if t:
            return t, "tema dominante medido na amostra: %s -> %s" % (temas[0], t)

    # ⚠️ SEM SINAL, SEM NUMERO. Um territorio inventado e pior que nenhum:
    # poe a fonte na gaveta errada e ninguem volta a olhar.
    return "NAO SEI", ("nem o nome nem a amostra disseram a que territorio "
                       "pertence — fica sem numero, de proposito")


def proximos_numeros(atlas: list[dict]) -> dict:
    """O maior numero usado por territorio, para continuar dali. Nunca reciclar."""
    maior = defaultdict(int)
    for a in atlas:
        m = re.match(r"^IT-(T\d+)-(\d+)$", a["SOURCE_ID"])
        if m:
            maior[m.group(1)] = max(maior[m.group(1)], int(m.group(2)))
    return maior


# ⚠️ CANAL E SITE DA MESMA ORGANIZACAO SAO DUAS FONTES, POR LEI.
# Medido: 15 organizacoes aparecem duas vezes na lista (canal de YouTube +
# site), e a primeira leitura foi «isto e duplicacao, tenho 30 numeros para 15
# fontes». Nao e. A lei do Atlas diz o contrario, com nome e caso:
#
#     COL-LAW-034: ORIGIN_ID != CHANNEL_ID  ·  «Canal != site»
#     IT-T8-001 e o canal AgroNotizie; IT-T1-021 e o site AgroNotizie;
#     «continua a ser outra fonte».
#
# E correcto, e a razao e de coleta: o canal e o site publicam coisas
# diferentes, em ritmos diferentes, por rotas diferentes. Fundi-los num
# SOURCE_ID daria uma fonte cuja cadencia e a media de duas realidades, e
# cujo RAW mistura XML de feed com HTML de portal.
#
#     A MESMA ORGANIZACAO PODE SER DUAS FONTES.
#     O QUE NAO PODE E A MESMA FONTE TER DOIS NUMEROS.
#
# O que se regista, para o Atlas nao perder o parentesco, e `MESMA_ORGANIZACAO`
# — um campo de relacao, nao de identidade.
def _org(nome: str) -> str:
    n = re.sub(r"—.*$", "", nome or "").strip().lower()
    return re.sub(r"[^a-z0-9]", "", n)


def main() -> int:
    match = json.loads((RAIZ / "curadoria" / "CANDIDATE-TO-SOURCE-MATCH-V1.json")
                       .read_text(encoding="utf-8"))
    car = json.loads((RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json")
                     .read_text(encoding="utf-8"))
    porid = {c["CANDIDATE_ID"]: c for c in car["FONTES"]}

    atlas = EM.ler_atlas()
    maior = proximos_numeros(atlas)

    # ⚠️ TAMBEM CONTAR O QUE O COORDINATOR JA CONTRATOU. O onboarded.json tem
    # 105 SOURCE_IDs; se algum for maior que o do Atlas, comecar acima dele.
    onb = json.loads(subprocess.run(
        ["git", "show", "%s:regras/italy_contracts_onboarded.json" % EM.COORD],
        capture_output=True, text=True, encoding="utf-8", cwd=str(RAIZ)).stdout)
    for f in onb["FONTES"]:
        m = re.match(r"^IT-(T\d+)-(\d+)$", f["SOURCE_ID"])
        if m:
            maior[m.group(1)] = max(maior[m.group(1)], int(m.group(2)))

    novas, sem_territorio = [], []
    contador = dict(maior)

    # ⚠️ PRIMEIRA PASSAGEM: decidir o territorio de cada uma.
    decidido = []
    for c in match["SEM_MATCH"]:
        ficha = porid[c["CANDIDATE_ID"]]
        t, porque = territorio_de(ficha)
        decidido.append((c, ficha, t, porque))

    # ⚠️ SEGUNDA PASSAGEM: a mesma organizacao nao pode cair em territorios
    # diferentes. Medido: «WineNews» ia para T2 pelo canal (falou de clima na
    # amostra) e para T10 pelo site (falou de mercado). Sao duas fontes — isso
    # e legitimo (COL-LAW-034) — mas do MESMO territorio: o territorio
    # descreve a organizacao, nao o assunto da semana.
    #
    # Ganha a decisao tomada pelo NOME, porque essa olhou para o que a fonte E.
    por_org = defaultdict(list)
    for item in decidido:
        por_org[_org(item[1]["NOME"])].append(item)
    forcados = 0
    for org, itens in por_org.items():
        ts = {t for _, _, t, _ in itens if t != "NAO SEI"}
        if len(ts) <= 1:
            continue
        forte = next((t for _, _, t, p in itens
                      if t != "NAO SEI" and "nome da fonte" in p), None)
        alvo = forte or sorted(ts)[0]
        for i, (c, f, t, p) in enumerate(itens):
            if t != alvo:
                itens[i] = (c, f, alvo, p + " | alinhado a %s: a mesma organizacao "
                            "nao pode estar em dois territorios (COL-LAW-034 "
                            "separa canal de site, nao de territorio)" % alvo)
                forcados += 1
    decidido = [x for itens in por_org.values() for x in itens]

    for c, ficha, t, porque in decidido:
        if t == "NAO SEI":
            sem_territorio.append({"CANDIDATE_ID": c["CANDIDATE_ID"],
                                   "NOME": ficha["NOME"], "PORQUE": porque})
            continue
        contador[t] = contador.get(t, 0) + 1
        irmas = [o["CANDIDATE_ID"] for oc, o, ot, _ in decidido
                 if _org(o["NOME"]) == _org(ficha["NOME"])
                 and o["CANDIDATE_ID"] != c["CANDIDATE_ID"]]
        novas.append({
            "CANDIDATE_ID": c["CANDIDATE_ID"],
            "SOURCE_ID": "IT-%s-%03d" % (t, contador[t]),
            "TERRITORY": t,
            "TERRITORY_REASON": porque,
            "NOME": ficha["NOME"],
            "URL": ficha["URL"],
            "FAMILY": ficha["FAMILY"],
            # relacao, nao identidade: diz de quem e irma sem as fundir
            "MESMA_ORGANIZACAO": irmas or None,
        })

    saida = {
        "DATASET": "SOURCE-ID-ALLOCATION-V1",
        "LEI": ("SOURCE_ID = IT-T<territorio>-<sequencia>. Nada dele deriva da URL, "
                "do handle ou de hash. A sequencia continua do maior existente e "
                "NUNCA recicla um numero ja usado."),
        "BASE_ATLAS": len(atlas),
        "MAIOR_POR_TERRITORIO_ANTES": dict(sorted(maior.items())),
        "ATRIBUIDOS": len(novas),
        "SEM_TERRITORIO": len(sem_territorio),
        "TERRITORIO_ALINHADO_POR_ORGANIZACAO": forcados,
        "LEI_CANAL_SITE": ("COL-LAW-034 (ORIGIN_ID != CHANNEL_ID): canal e site da "
                           "mesma organizacao sao DUAS fontes com dois SOURCE_ID. "
                           "MESMA_ORGANIZACAO guarda o parentesco sem as fundir."),
        "POR_TERRITORIO": dict(Counter(n["TERRITORY"] for n in novas)),
        "NOVAS": novas,
        "SEM_TERRITORIO_DETALHE": sem_territorio,
    }
    p = RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("Atlas base            %d fichas" % len(atlas))
    print("SOURCE_ID atribuidos  %d" % len(novas))
    print("sem territorio        %d (ficam sem numero, de proposito)" % len(sem_territorio))
    print("por territorio        %s" % dict(sorted(Counter(n["TERRITORY"] for n in novas).items())))
    print("escrito: %s" % p.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
