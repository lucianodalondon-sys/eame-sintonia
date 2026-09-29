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


def _basis_do_ano(b):
    """R2 item 4 · `ANO_BASIS` chegava como TEXTO quando ORIGEM=RELATIVO_D63 e o
    `dict(...)` rebentava. Agora aceita as duas formas e devolve sempre um dict."""
    if isinstance(b, dict):
        return dict(b)
    return {"TRECHO": str(b), "OFFSET": None, "EXPRESSAO": str(b)}


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
        b = _basis_do_ano(reg["ANO_BASIS"])
        if isinstance(b.get("OFFSET"), int):
            b["OFFSET"] = b["OFFSET"] + deslocamento
        d["ANO_BASIS"] = b
    for extra in ("PROCEDENCIA_DO_ANO", "COMPOSICAO", "ORIGEM_DETALHE", "ANO_ORIGEM"):
        if reg.get(extra):
            d[extra] = reg[extra]
    return d


# ── R2 item 7 · o contrato da fonte tem de CHEGAR a logica ───────────────────
_ALIAS_CONTRATO = ("CONTRATO_DA_FONTE", "CONTRATO", "TIPO_DE_DATA_DA_FONTE",
                   "CONTRATO_DE_DATA", "DATA_DA_FONTE", "TIPO_DE_DATA", "contrato_da_fonte")
_VALOR_CONTRATO = {
    "VALIDADE": "VALIDADE", "VALIDITA": "VALIDADE", "VALIDITY": "VALIDADE", "VALIDITÀ": "VALIDADE",
    "EDICAO": "EDICAO", "EDIÇÃO": "EDICAO", "EDIZIONE": "EDICAO", "EDITION": "EDICAO",
    "PUBLICACAO": "PUBLICACAO", "PUBLICAÇÃO": "PUBLICACAO", "PUBLICATION": "PUBLICACAO",
}


def contrato_da_entrada(entrada: dict):
    """O que a fonte declara sobre a data do topo, venha com o nome que vier.
    VALIDADE → o periodo do topo e VALIDITY. EDICAO → PERIODO_DA_EDICAO, nunca validade."""
    for k in _ALIAS_CONTRATO:
        v = (entrada or {}).get(k)
        if v:
            return _VALOR_CONTRATO.get(str(v).strip().upper(), str(v).strip().upper())
    return None


# ── R2 item 1 · o ato tem de estar LIGADO a afirmacao ────────────────────────
_RE_REFERENCIA_A_ATO = re.compile(
    r"(?:decret|determin|delibera|ordinanz|circolar|d\.?lgs|legge|reg(?:olamento)?\.?\s*(?:ue|ce)|"
    r"n[.°]\s*\d+|sopra\s+richiamat|citat[oa]|predett[oa]|suddett[oa])", re.I)


def _ato_referido_na_afirmacao(regs, afirmacao):
    """Um ato fora da afirmacao só lhe pertence quando a afirmacao o REFERE
    explicitamente («la sopra richiamata Determinazione», «il decreto n. 9818»). Sem
    referencia, atribuir-lho seria inventar a data — foi o DATA_INVENTADA medido."""
    if not _RE_REFERENCIA_A_ATO.search(afirmacao or ""):
        return []
    numeros = set(re.findall(r"n[.°]\s*(\d+)", afirmacao or "", re.I))
    if numeros:
        ligados = [x for x in regs
                   if numeros & set(re.findall(r"n[.°]\s*(\d+)", x["BASIS"]["TRECHO"], re.I))]
        return ligados[:1]
    # referencia sem numero: so vale se houver UM unico ato no documento
    return regs[:1] if len(regs) == 1 else []


# ── R2 item 5 · NAO_EXISTE nao e NAO_SEI ─────────────────────────────────────
# A pista de que a AFIRMACAO invoca aquele tipo de tempo. Sem pista, o tipo nao existe
# nela; com pista e sem conseguir determinar, e NAO_SEI.
_PISTA_DO_TIPO = {
    "ACT_TIME": _RE_REFERENCIA_A_ATO,
    "VALIDITY_TIME": re.compile(r"valid|scadenz|prorog|deroga|entro\s|fino\s+a|autorizzazion", re.I),
    "MARKET_PERIOD": re.compile(r"prezz|quotazion|mercat|euro|listino|rilevazion|campagna|annata|"
                                r"stagione|raccolt|borsa|ingrosso", re.I),
    "PERIODO_DA_EDICAO": re.compile(r"bollettino|settimana|edizione|periodo|riferimento", re.I),
}
_NOME_DO_TIPO = {"ACT_TIME": "ato", "VALIDITY_TIME": "validade",
                 "MARKET_PERIOD": "periodo de mercado", "PERIODO_DA_EDICAO": "periodo de edicao"}
def _ausencia(tipo, regs_no_documento, afirmacao):
    """NAO_SEI = aconteceu e o texto nao diz quando. NAO_EXISTE = nao ha o que datar.

    Para FACT_TIME decide a afirmacao: sem palavra de acontecimento (conhecimento geral,
    biologia, definicao, conselho) nao existe facto para datar. Para os outros tipos
    decide o documento: se nao ha ato/validade/mercado nenhum, esse tempo NAO EXISTE;
    se ha mas nao esta ligado a esta afirmacao, e NAO SEI.
    """
    if tipo == "FACT_TIME":
        if not TP.acontecimento_datavel(afirmacao):
            return _vazio(NAO_EXISTE, "a afirmacao nao relata acontecimento datavel "
                                      "(conhecimento geral, biologia, definicao ou conselho)")
        return _vazio(NAO_SEI, "houve acontecimento nesta afirmacao, mas o texto nao escreve quando")
    # Nos outros tipos decide a AFIRMACAO, nao o documento: se ela nem fala de ato /
    # validade / mercado / edicao, esse tempo NAO EXISTE nela — ter um ato noutro paragrafo
    # nao torna esta afirmacao indeterminada, torna-a sem ato. Só quando a afirmacao
    # invoca a coisa e nao se consegue dizer qual e que fica NAO_SEI.
    pista = _PISTA_DO_TIPO.get(tipo)
    invoca = bool(pista and pista.search(afirmacao or ""))
    if not invoca:
        return _vazio(NAO_EXISTE, "a afirmacao nao invoca %s (ha %d no documento, de outras "
                                  "afirmacoes)" % (_NOME_DO_TIPO.get(tipo, tipo),
                                                   len(regs_no_documento)))
    if not regs_no_documento:
        return _vazio(NAO_EXISTE, "o documento nao tem tempo deste tipo")
    return _vazio(NAO_SEI, "a afirmacao invoca %s, mas ha %d no documento e nenhum se liga a "
                           "ela sem inventar" % (_NOME_DO_TIPO.get(tipo, tipo),
                                                 len(regs_no_documento)))


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
    contrato = contrato_da_entrada(entrada)
    r = TP.tempos_do_texto(texto, pub, published_at_basis=basis,
                           contrato_da_fonte=contrato, usar_corpo=False)
    a_ini, a_fim, como = _span_do_alvo(entrada, alvo)
    o_ini, o_fim = _oracao_do_alvo(texto, a_ini, a_fim)
    afirmacao = texto[o_ini:o_fim]

    def dentro(reg, i, f):
        o = reg["BASIS"]["OFFSET"]
        return i <= o < f

    fora = {}
    for t in TIPOS:
        regs = r.get(t, [])
        no_alvo = [x for x in regs if dentro(x, a_ini, a_fim)]
        na_oracao = [x for x in regs if dentro(x, o_ini, o_fim)]
        escolha = no_alvo or na_oracao
        alcance = "ALVO" if no_alvo else "ORACAO_DO_ALVO"
        # R2 item 1 · ACT_TIME NUNCA vem do documento inteiro: um ato de OUTRA afirmacao
        # atribuido a esta e data inventada. Ou esta ligado ao alvo (mesma oracao ou
        # referencia explicita na oracao), ou nao sai.
        if not escolha and t == "ACT_TIME":
            escolha = _ato_referido_na_afirmacao(regs, afirmacao)
            alcance = "REFERENCIA_EXPLICITA_NA_AFIRMACAO" if escolha else alcance
        # publicacao e periodo da edicao SAO do documento inteiro por natureza
        if not escolha and t in ("PUBLICATION_TIME", "PERIODO_DA_EDICAO"):
            escolha, alcance = regs, "DOCUMENTO"
        if not escolha:
            fora[t] = _ausencia(t, regs, afirmacao)
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
    # R2 item 6 · o metadado da ENTRADA e base admissivel para PUBLICATION_TIME (nunca
    # para FACT). Entra so quando o texto nao deu carimbo nenhum, e diz de onde vem.
    if fora["PUBLICATION_TIME"]["VALOR"] in (NAO_SEI, NAO_EXISTE) and pub:
        provada = bool(FT.publicacao_provada(pub, basis))
        fora["PUBLICATION_TIME"] = {
            "VALOR": str(pub)[:10], "PRECISAO": "DIA",
            "BASIS": {"TRECHO": "PUBLISHED_AT_DA_SALA «%s» · base «%s»" % (pub, basis or NAO_SEI),
                      "OFFSET": None, "FIM": None, "EXPRESSAO": str(pub)[:10]},
            "ORIGEM": "METADADO_DA_ENTRADA",
            "ANO": str(pub)[:4],
            "PROVADA": provada,
            "PORQUE": ("metadado de publicacao da Sala, com base declarada: admissivel para "
                       "PUBLICATION_TIME, proibido para FACT_TIME" if provada else
                       "metadado de publicacao SEM base provada: fica a vista, nao ancora relativa"),
        }
    elif fora["PUBLICATION_TIME"]["VALOR"] == NAO_SEI and not pub:
        fora["PUBLICATION_TIME"] = _vazio(NAO_EXISTE, "o documento nao traz carimbo de publicacao "
                                                      "e a entrada nao trouxe metadado")
    fora["_CONTRATO_DA_FONTE_APLICADO"] = contrato or "NENHUM"
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
