# -*- coding: utf-8 -*-
"""Plugin de pytest que troca o leitor de tempo VIVO pelo PROPOSTO, so durante a
corrida da bateria. Serve para saber o que quebraria se a proposta fosse instalada.

    py -3.12 -m pytest tests/test_data_do_fato.py -p provas.l5-p3.plugin_proposta

Nao altera nenhum ficheiro: substitui `leis.fato_local.tempo_do_fato` em memoria por
um adaptador que devolve a MESMA forma de dicionario (para o resto de
`leis/fato_do_texto.py` continuar a funcionar), mas com a escolha do extrator novo.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from leis import fato_local as FL
from leis_proposta import tempo_tipado as TP

# a precisao da proposta dita no vocabulario do vivo
PARA_O_VIVO = {TP.DAY: FL.DAY, TP.WEEK: FL.WEEK, TP.MONTH: FL.MONTH,
               TP.YEAR: FL.YEAR, TP.SEASON: FL.SEASON, TP.INTERVAL: FL.DAY}

_VIVO = FL.tempo_do_fato


def tempo_do_fato_proposta(texto, published_at=None):
    """A porta do vivo, respondida pela proposta. Devolve a EXPRESSAO ESCRITA (nao a
    forma ISO) no campo FACT_TIME, porque e isso que `leis/fato_do_texto.py` espera
    re-encontrar no texto para tapar e perguntar de novo."""
    # quem chama e `leis/fato_do_texto.py`, que so passa `published_at` DEPOIS de o
    # provar (`publicacao_provada`) — por isso aqui a base ja esta provada (D63).
    r = TP.tempos_do_texto(texto, published_at, usar_corpo=False,
                           published_at_basis="PROVADA_PELO_CHAMADOR" if published_at else None)
    e = r["FACT_TIME_ESCOLHIDO"]
    if e and e.get("ORIGEM") == TP.RELATIVO_D63:
        # `leis/fato_do_texto.py` tapa as relativas ANTES de chamar este leitor e conta-as
        # com a sua propria maquina (D63/D64). Devolver aqui uma relativa ja contada
        # punha um valor ISO onde o chamador espera a expressao escrita.
        e = next((x for x in r[TP.FACT_TIME] if x.get("ORIGEM") != TP.RELATIVO_D63), None)
    descartados = [{"VALUE": d["VALOR"], "WHY": d["PORQUE"]} for d in r["DESCARTADOS"]]
    if not e:
        return {"FACT_TIME": "NOT_KNOWN", "FACT_TIME_PRECISION": FL.NOT_KNOWN,
                "FACT_TIME_EVIDENCE": None, "FACT_TIME_ORIGIN": "NOT_STATED",
                "PUBLISHED_AT": published_at or "NOT_DATED_PRECISELY",
                "FACT_TIME_CANDIDATES": [d["VALOR"] for d in r["DESCARTADOS"]][:8],
                "TIME_CANDIDATES_DISCARDED": descartados,
                "WHY": "proposta L5-P3: nenhum tempo do texto ficou tipado como FACT_TIME"}
    return {"FACT_TIME": e["BASIS"]["EXPRESSAO_NUCLEO"],
            "FACT_TIME_PRECISION": PARA_O_VIVO.get(e["PRECISAO"], FL.NOT_KNOWN),
            # a frase COMO ESTA no texto: o chamador precisa de a reencontrar com
            # `t.find(ev[:60])` para tapar a data e perguntar de novo. Com os espacos
            # colapsados esse find falhava e a lei de cima deixava de correr.
            "FACT_TIME_EVIDENCE": e["BASIS"]["FRASE_BRUTA"],
            "FACT_TIME_ORIGIN": "TEXT/TIED_TO_EVENT",
            "FACT_TIME_VALOR_NORMALIZADO": e["VALOR"],
            "FACT_TIME_TIPO": TP.FACT_TIME,
            "PUBLISHED_AT": published_at or "NOT_DATED_PRECISELY",
            "TIME_CANDIDATES_DISCARDED": descartados}


# ── trocar em TODOS os sitios onde o leitor vive ─────────────────────────────
# Os testes fazem `sys.path.insert(0, RAIZ/"leis")` e depois `import fato_do_texto`:
# isso cria um SEGUNDO par de modulos (`fato_local`, `fato_do_texto`) diferente de
# `leis.fato_local`. Trocar so um deixava a bateria a correr o codigo vivo e a dar
# 0 regressoes por engano — medido: um leitor cego (sempre NAO SEI) tambem passava
# 86/86. Por isso: troca-se nos dois, e o canario abaixo prova que mordeu.
sys.path.insert(0, os.path.join(RAIZ, "leis"))
import fato_local as FL_SOLTO                                           # noqa: E402

_ALVOS = [FL, FL_SOLTO]
_ORIGINAIS = [(m, m.tempo_do_fato) for m in _ALVOS]


def _canario():
    """Prova que a troca mordeu: uma frase que o vivo le «4 settembre 2026» e a
    proposta le como intervalo tem de mudar de resposta."""
    frase = ("Il monitoraggio della mosca delle olive effettuato dal 1 al 4 settembre 2026 "
             "sul territorio regionale.")
    return [m.tempo_do_fato(frase, None).get("FACT_TIME") for m in _ALVOS]


def pytest_configure(config):
    antes = _canario()
    for m in _ALVOS:
        m.tempo_do_fato = tempo_do_fato_proposta
    depois = _canario()
    if antes == depois:
        raise RuntimeError("[L5-P3] a troca NAO mordeu (%r): a bateria mediria o codigo vivo" % (antes,))
    print("\n[L5-P3] tempo_do_fato trocado pela PROPOSTA em %d modulos; canario %r -> %r"
          % (len(_ALVOS), antes, depois))


def pytest_unconfigure(config):
    for m, f in _ORIGINAIS:
        m.tempo_do_fato = f
