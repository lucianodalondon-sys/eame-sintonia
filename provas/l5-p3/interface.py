# -*- coding: utf-8 -*-
"""L5-P3 · a MESMA porta para os dois extratores (D147). Quem pontua e o LAB.

    from interface import extrair_atual, extrair_proposto

    entrada = {"TEXTO": "...", "PUBLISHED_AT_DA_SALA": "2026-09-24",
               "PUBLISHED_AT_BASIS_DA_SALA": "JSON-LD datePublished",
               "CAPTURED_AT": "2026-09-27T23:05:59Z"}
    alvo    = {"TRECHO": "effettuato dal 1 al 4 settembre 2026", "OFFSET": 985, "FIM": 1021}

    r = extrair_proposto(entrada, alvo)
    r["FACT_TIME"]["VALOR"]      # "2026-09-01/2026-09-04"
    r["FACT_TIME"]["PRECISAO"]   # "INTERVALO"
    r["FACT_TIME"]["ORIGEM"]     # "LITERAL"

Devolvem SEMPRE as seis chaves:
    FACT_TIME · VALIDITY_TIME · PUBLICATION_TIME · ACT_TIME · MARKET_PERIOD · PERIODO_DA_EDICAO

Cada uma e um dict com:
    VALOR       o valor, ou "NAO_SEI" / "NAO_EXISTE" / "NOT_PRODUCED"
    PRECISAO    DIA | SEMANA | MES | ANO | INTERVALO | NAO_SEI
    INICIO/FIM  so quando PRECISAO == INTERVALO
    BASIS       {TRECHO, OFFSET, FIM} — onde no texto, com offset
    ORIGEM      LITERAL | CABECALHO | RELATIVO_D63 | NAO_SE_APLICA
    ANO_BASIS   quando o ano veio do cabecalho: o segundo trecho, com o seu offset

Os tres estados de ausencia nao sao sinonimos:
    NAO_SEI       o extrator procurou e nao achou tempo deste tipo nesta afirmacao
    NAO_EXISTE    o documento nao tem este tempo (nao ha carimbo de publicacao nenhum)
    NOT_PRODUCED  este extrator NAO SABE produzir este tipo — e o caso do ATUAL, que
                  so tem um campo (`fact_time`) e nao distingue os cinco tipos.
                  NOT_PRODUCED nao e erro do extrator: e a medida do que lhe falta.

`extrair_atual` corre `leis/fato_do_texto.campos_do_fato` SEM MODIFICACAO — so traduz
a saida para esta forma. Nenhum ficheiro de `leis/` foi tocado.
"""
from __future__ import annotations

import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from leis import fato_do_texto as FT          # producao, intocada
from leis_proposta import tempo_tipado as TP  # a proposta

TIPOS = ("FACT_TIME", "VALIDITY_TIME", "PUBLICATION_TIME", "ACT_TIME",
         "MARKET_PERIOD", "PERIODO_DA_EDICAO")

NAO_SEI, NAO_EXISTE, NOT_PRODUCED = "NAO_SEI", "NAO_EXISTE", "NOT_PRODUCED"
NAO_SE_APLICA = "NAO_SE_APLICA"

# o vocabulario de precisao pedido pelo dono
PRECISAO = {TP.DAY: "DIA", TP.WEEK: "SEMANA", TP.MONTH: "MES", TP.YEAR: "ANO",
            TP.SEASON: "ANO", TP.INTERVAL: "INTERVALO"}
# a precisao do extrator ATUAL, dita no mesmo vocabulario
PRECISAO_ATUAL = {"DATE_EXACT": "DIA", "WEEK": "SEMANA", "MONTH": "MES",
                  "SEASON": "ANO", "APPROXIMATE": "ANO", "NOT_KNOWN": NAO_SEI}


def _vazio(estado, porque=None):
    d = {"VALOR": estado, "PRECISAO": NAO_SEI, "BASIS": None, "ORIGEM": NAO_SE_APLICA}
    if porque:
        d["PORQUE"] = porque
    return d


def _campo(reg, deslocamento=0):
    """Um registo da proposta traduzido para a forma da interface."""
    d = {
        "VALOR": reg["VALOR"],
        "PRECISAO": PRECISAO.get(reg["PRECISAO"], NAO_SEI),
        "BASIS": {"TRECHO": reg["BASIS"]["TRECHO"],
                  "OFFSET": reg["BASIS"]["OFFSET"] + deslocamento,
                  "FIM": reg["BASIS"]["FIM"] + deslocamento,
                  "EXPRESSAO": reg["BASIS"]["EXPRESSAO"]},
        "ORIGEM": reg.get("ORIGEM") or TP.LITERAL,
        "ANO": reg["ANO"],
        "PORQUE": reg["PORQUE"],
    }
    if reg["PRECISAO"] == TP.INTERVAL:
        d["INICIO"], d["FIM"] = reg["VALOR_INICIO"], reg["VALOR_FIM"]
    if reg.get("ANO_BASIS"):
        b = dict(reg["ANO_BASIS"])
        b["OFFSET"] = b["OFFSET"] + deslocamento
        d["ANO_BASIS"] = b
    return d


# ── o alvo: a afirmacao que o golden aponta ──────────────────────────────────
def _span_do_alvo(entrada, alvo):
    """(inicio, fim) da afirmacao-alvo dentro do TEXTO. Se o offset dado nao bate com
    o trecho, procura o trecho no texto; se nem assim, o alvo e o texto inteiro."""
    texto = str(entrada.get("TEXTO") or "")
    trecho = str((alvo or {}).get("TRECHO") or "")
    ini, fim = (alvo or {}).get("OFFSET"), (alvo or {}).get("FIM")
    if isinstance(ini, int) and trecho and texto[ini:ini + len(trecho)] == trecho:
        return ini, (fim if isinstance(fim, int) and fim > ini else ini + len(trecho)), "OFFSET_DADO"
    if trecho:
        p = texto.find(trecho)
        if p >= 0:
            return p, p + len(trecho), "TRECHO_PROCURADO"
        p = _procura_frouxa(texto, trecho)
        if p is not None:
            return p[0], p[1], "TRECHO_PROCURADO_SEM_ESPACOS"
    if isinstance(ini, int) and isinstance(fim, int) and fim > ini:
        return ini, fim, "OFFSET_DADO_SEM_CONFERIR"
    return 0, len(texto), "DOCUMENTO_INTEIRO"


def _procura_frouxa(texto, trecho):
    """O mesmo trecho com outros espacos continua a ser o mesmo trecho."""
    padrao = r"\s+".join(re.escape(p) for p in trecho.split())
    m = re.search(padrao, texto)
    return (m.start(), m.end()) if m else None


def _oracao_do_alvo(texto, ini, fim):
    a = max([texto.rfind(c, 0, ini) for c in ".!?;\n"] + [-1]) + 1
    bs = [texto.find(c, fim) for c in ".!?;\n"]
    return a, min([x for x in bs if x >= 0] + [len(texto)])


# ── o extrator PROPOSTO ──────────────────────────────────────────────────────
def extrair_proposto(entrada: dict, alvo: dict) -> dict:
    texto = str(entrada.get("TEXTO") or "")
    pub = entrada.get("PUBLISHED_AT_DA_SALA")
    basis = entrada.get("PUBLISHED_AT_BASIS_DA_SALA")
    r = TP.tempos_do_texto(texto, pub, published_at_basis=basis,
                           contrato_da_fonte=entrada.get("CONTRATO_DA_FONTE"),
                           usar_corpo=False)
    a_ini, a_fim, como = _span_do_alvo(entrada, alvo)
    o_ini, o_fim = _oracao_do_alvo(texto, a_ini, a_fim)

    def dentro(reg, i, f):
        o = reg["BASIS"]["OFFSET"]
        return i <= o < f

    fora = {}
    for t in TIPOS:
        regs = r.get(t, [])
        # a afirmacao-alvo manda: primeiro o que esta DENTRO dela, depois o que esta na
        # mesma oracao; o resto do documento so vale para PUBLICACAO e EDICAO, que sao
        # do documento inteiro por natureza.
        escolha = [x for x in regs if dentro(x, a_ini, a_fim)] or \
                  [x for x in regs if dentro(x, o_ini, o_fim)]
        alcance = "ALVO" if any(dentro(x, a_ini, a_fim) for x in regs) else "ORACAO_DO_ALVO"
        if not escolha and t in ("PUBLICATION_TIME", "PERIODO_DA_EDICAO", "ACT_TIME"):
            escolha, alcance = regs, "DOCUMENTO"
        if not escolha:
            fora[t] = _vazio(NAO_SEI, "nenhum tempo deste tipo na afirmacao-alvo")
            continue
        if t == "FACT_TIME":
            melhor = TP._escolher_facto(escolha)
            outros = melhor.get("AMBIGUO")
        else:
            melhor, outros = escolha[0], [x["VALOR"] for x in escolha[1:]] or False
        fora[t] = _campo(melhor)
        fora[t]["ALCANCE"] = alcance
        if outros:
            fora[t]["OUTROS_NO_DOCUMENTO"] = outros
    if fora["PUBLICATION_TIME"]["VALOR"] == NAO_SEI and not pub:
        fora["PUBLICATION_TIME"] = _vazio(NAO_EXISTE, "o documento nao traz carimbo de publicacao")
    fora["_ALVO"] = {"COMO": como, "OFFSET": a_ini, "FIM": a_fim,
                     "TRECHO": texto[a_ini:a_fim][:300]}
    fora["_LIMITES_INFERIDOS"] = r["LIMITES_INFERIDOS"]
    fora["_DESCARTADOS"] = [{"VALOR": d["VALOR"], "PORQUE": d["PORQUE"],
                             "OFFSET": d["BASIS"]["OFFSET"]} for d in r["DESCARTADOS"]]
    fora["_EXTRATOR"] = "PROPOSTO/leis_proposta.tempo_tipado"
    return fora


# ── o extrator ATUAL (producao, sem modificacao) ─────────────────────────────
def extrair_atual(entrada: dict, alvo: dict) -> dict:
    texto = str(entrada.get("TEXTO") or "")
    pub = entrada.get("PUBLISHED_AT_DA_SALA")
    basis = entrada.get("PUBLISHED_AT_BASIS_DA_SALA")
    r = FT.campos_do_fato(texto, pub, basis)
    a_ini, a_fim, como = _span_do_alvo(entrada, alvo)

    v = r.get("fact_time")
    prec = str(r.get("fact_time_precision") or "").replace("+CALCULADA", "")
    calculada = "+CALCULADA" in str(r.get("fact_time_precision") or "")
    vazio = v is None or str(v).strip().upper() in ("NAO SEI", "NÃO SEI", "NOT_KNOWN", "")
    if vazio:
        facto = _vazio(NAO_SEI, str(r.get("fact_time_basis"))[:300])
    else:
        # o offset: onde a expressao que a producao devolveu esta no texto
        p = texto.find(str(v))
        facto = {
            "VALOR": v,
            "PRECISAO": PRECISAO_ATUAL.get(prec, NAO_SEI),
            "BASIS": {"TRECHO": str(r.get("fact_time_basis"))[:300],
                      "OFFSET": p if p >= 0 else None,
                      "FIM": (p + len(str(v))) if p >= 0 else None,
                      "EXPRESSAO": v},
            "ORIGEM": TP.RELATIVO_D63 if calculada else TP.LITERAL,
            "ANO": (re.search(r"(?:19|20)\d{2}", str(v)).group(0)
                    if re.search(r"(?:19|20)\d{2}", str(v)) else NAO_SEI),
            "PORQUE": "producao: leis/fato_do_texto.campos_do_fato",
            "DENTRO_DO_ALVO": bool(p >= 0 and a_ini <= p < a_fim),
        }
    fora = {"FACT_TIME": facto}
    # A producao NAO distingue os outros tipos: tem um campo so. Dizer NAO_SEI aqui
    # seria dizer «procurei e nao achei», e nao e verdade — nunca procurou.
    for t in TIPOS[1:]:
        fora[t] = _vazio(NOT_PRODUCED, "o extrator de producao tem um so campo (fact_time)")
    # o que a producao recebe da Sala, para o LAB nao confundir com extracao
    fora["_PUBLISHED_AT_RECEBIDO_DA_SALA"] = {
        "VALOR": pub or NAO_SEI, "BASIS": basis or NAO_SEI,
        "PROVADA": bool(FT.publicacao_provada(pub, basis)),
        "NOTA": "recebido da Sala, nao extraido do texto"}
    # a mesma producao alimentada SO com a afirmacao-alvo — a leitura mais favoravel
    # que se lhe pode dar quando o golden aponta a afirmacao
    so_alvo = FT.campos_do_fato(texto[a_ini:a_fim], pub, basis)
    fora["_FACT_TIME_SO_COM_O_ALVO"] = {
        "VALOR": so_alvo.get("fact_time"),
        "PRECISAO": PRECISAO_ATUAL.get(str(so_alvo.get("fact_time_precision") or "")
                                       .replace("+CALCULADA", ""), NAO_SEI)}
    fora["_ALVO"] = {"COMO": como, "OFFSET": a_ini, "FIM": a_fim, "TRECHO": texto[a_ini:a_fim][:300]}
    fora["_EXTRATOR"] = "ATUAL/leis.fato_do_texto.campos_do_fato (producao, sem modificacao)"
    return fora


if __name__ == "__main__":
    import json
    TEXTO = ("Il Bollettino fitosanitario relativo al monitoraggio della mosca delle olive "
             "(Bactrocera oleae) effettuato dal 1 al 4 settembre 2026 sul territorio regionale. "
             "Con Decreto Dirigenziale n. 15068 DEL 08/09/2026 e stata approvata la ridefinizione. "
             "BOLLETTINO settimana 39 dal 22/09/2026 al 29/09/2026.")
    ENTRADA = {"TEXTO": TEXTO, "PUBLISHED_AT_DA_SALA": "2026-09-24",
               "PUBLISHED_AT_BASIS_DA_SALA": "JSON-LD datePublished",
               "CAPTURED_AT": "2026-09-27T23:05:59Z"}
    ALVO = {"TRECHO": "effettuato dal 1 al 4 settembre 2026",
            "OFFSET": TEXTO.find("effettuato dal 1"),
            "FIM": TEXTO.find("effettuato dal 1") + len("effettuato dal 1 al 4 settembre 2026")}
    for f in (extrair_atual, extrair_proposto):
        print("\n=== %s ===" % f.__name__)
        print(json.dumps(f(ENTRADA, ALVO), ensure_ascii=False, indent=1))
