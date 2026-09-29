# -*- coding: utf-8 -*-
"""L5-P3 · mede o extrator ATUAL e o PROPOSTO no mesmo golden set.

    py -3.12 provas/l5-p3/avaliar.py <golden.json> [--sha256 <ficheiro.sha256>]
    py -3.12 provas/l5-p3/avaliar.py provas/l5-p3/casos_lab.json     (banco de dev)

O golden set e HOLD-OUT: preparado e congelado pelo LAB. Este ficheiro nao o le
para se ajustar a ele — le-o para contar acertos. O extrator proposto e congelado
num commit ANTES desta corrida.

O que conta
-----------
ACERTO                              tipo certo E valor certo
PUBLICATION_TIME_USADO_COMO_FACT_TIME   uma data de publicacao/edicao saiu como facto
VALIDITY_TIME_CONFUNDIDO_COM_FACT_TIME  uma janela de validade saiu como facto
DATA_INVENTADA                      valor que nao esta escrito no texto
PRECISAO_INVENTADA                  dia onde o texto so da mes/semana, ou ano onde
                                    o texto nao da ano
ERROS_CRITICOS                      a lista, caso a caso, com o que se esperava
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from leis import fato_do_texto as FT                      # o extrator ATUAL
from leis_proposta import tempo_tipado as TP              # o extrator PROPOSTO

NAO_SEI = ("NAO SEI", "NÃO SEI", "NOT_KNOWN", "NAO EXISTE", "NÃO EXISTE",
           "NONE", "NULL", "", "NAO_SE_APLICA", "N/A")

# ── ler o golden sem exigir um nome de campo so ──────────────────────────────
_ALIAS_TEXTO = ("TEXTO", "texto", "TRECHO", "trecho", "TEXT", "text", "CORPO", "corpo")
_ALIAS_PUB = ("PUBLICATION_TIME", "published_at", "PUBLISHED_AT", "PUB", "pub",
              "publicacao", "PUBLICACAO", "publication_time")
_ALIAS_ESPERADO = ("ESPERADO", "esperado", "GOLD", "gold", "GABARITO", "gabarito",
                   "EXPECTED", "expected")
_ALIAS_TIPO = ("TIPO", "tipo", "TIPO_ESPERADO", "KIND", "kind", "TIME_TYPE")
_ALIAS_VALOR = ("VALOR", "valor", "VALOR_ESPERADO", "VALUE", "value", "FACT_TIME")
_ALIAS_PRECISAO = ("PRECISAO", "precisao", "PRECISION", "precision", "RESOLUCAO")
_ALIAS_ID = ("ID", "id", "CASO", "caso", "N", "NOME", "nome", "CASE")
_ALIAS_TEMPOS = ("TEMPOS", "tempos", "OUTROS_TEMPOS", "outros_tempos", "TIMES",
                 "TEMPOS_DO_DOCUMENTO")
_ALIAS_CONTRATO = ("CONTRATO", "contrato", "CONTRATO_DA_FONTE", "TIPO_DE_DATA_DA_FONTE")


def _de(d, nomes, omissao=None):
    for n in nomes:
        if isinstance(d, dict) and n in d and d[n] not in (None, ""):
            return d[n]
    return omissao


def carrega(caminho):
    """Aceita lista de casos, ou {'CASOS': [...]} / {'casos': [...]} / {'cases': [...]}."""
    with open(caminho, encoding="utf-8") as f:
        bruto = json.load(f)
    if isinstance(bruto, dict):
        for k in ("CASOS", "casos", "cases", "ITENS", "itens", "GOLDEN", "golden"):
            if isinstance(bruto.get(k), list):
                return bruto[k], bruto
        return [bruto], bruto
    return bruto, {}


def le_caso(c, i):
    esp = _de(c, _ALIAS_ESPERADO, c)          # o esperado pode estar no topo do caso
    return {
        "ID": str(_de(c, _ALIAS_ID, "caso-%02d" % (i + 1))),
        "TEXTO": str(_de(c, _ALIAS_TEXTO, "")),
        "PUB": _de(c, _ALIAS_PUB),
        "CONTRATO": _de(c, _ALIAS_CONTRATO),
        "TIPO": str(_de(esp, _ALIAS_TIPO, "FACT_TIME")).upper(),
        "VALOR": _de(esp, _ALIAS_VALOR),
        "PRECISAO": _de(esp, _ALIAS_PRECISAO),
        "TEMPOS": _de(c, _ALIAS_TEMPOS, _de(esp, _ALIAS_TEMPOS, [])) or [],
    }


# ── normalizar valores para poder comparar ───────────────────────────────────
_RES_ATUAL = {"DATE_EXACT": TP.DAY, "WEEK": TP.WEEK, "MONTH": TP.MONTH,
              "SEASON": TP.SEASON, "APPROXIMATE": TP.YEAR, "NOT_KNOWN": "NOT_KNOWN"}


def nada(v):
    return v is None or str(v).strip().upper() in NAO_SEI


def iso(v):
    """Qualquer forma escrita -> a forma canonica desta prova.
    «4 settembre 2026» -> 2026-09-04 · «dal 1 al 4 settembre 2026» -> 2026-09-01/2026-09-04
    · «maggio» -> SEM_ANO-05 · «settimana 39/2026» -> 2026-W39 · ja-ISO fica igual."""
    if nada(v):
        return None
    s = re.sub(r"\s+", " ", str(v)).strip()
    s = s.replace("..", "/").replace(" a ", "/").replace("—", "/")
    if re.match(r"^(?:\d{4}|SEM_ANO)(?:-\d{2}(?:-\d{2})?|-W\d{2})?"
                r"(?:/(?:\d{4}|SEM_ANO)(?:-\d{2}(?:-\d{2})?|-W\d{2})?)?$", s, re.I):
        return s.upper().replace("SEM ANO", TP.SEM_ANO)
    low = TP._fold(s)
    for nome, rx in TP.SUPERFICIES:
        m = rx.search(low)
        if m and m.group(0).strip():
            lido = TP._leitura(nome, m)
            if lido and lido[3] != TP.NAO_SEI:
                return lido[0]
    return s.upper()


def _no_texto(valor, texto):
    """O valor esta ESCRITO no texto? (o ano, o mes e o dia aparecem?)
    Serve para apanhar data inventada — a que nao tem base nenhuma no texto."""
    low = TP._fold(texto)
    partes = [p for p in re.split(r"[/]", str(valor or "")) if p]
    for p in partes:
        ano = p[:4]
        if ano.isdigit() and ano not in low.replace(" ", "") and ano not in low:
            return False
    return True


# ── correr os dois extratores ────────────────────────────────────────────────
def atual(caso):
    r = FT.campos_do_fato(caso["TEXTO"], caso["PUB"],
                          "meta article:published_time" if caso["PUB"] else None)
    v = r.get("fact_time")
    prec = str(r.get("fact_time_precision") or "").replace("+CALCULADA", "")
    return {
        "TIPO": "FACT_TIME" if not nada(v) else None,
        "VALOR": None if nada(v) else iso(v),
        "BRUTO": v,
        "PRECISAO": _RES_ATUAL.get(prec, prec),
        "BASIS": str(r.get("fact_time_basis"))[:300],
    }


def proposto(caso):
    r = TP.tempos_do_texto(caso["TEXTO"], caso["PUB"], contrato_da_fonte=caso["CONTRATO"],
                           published_at_basis="meta article:published_time" if caso["PUB"] else None)
    e = r["FACT_TIME_ESCOLHIDO"]
    return {
        "TIPO": "FACT_TIME" if e else None,
        "VALOR": e["VALOR"] if e else None,
        "BRUTO": e["BASIS"]["EXPRESSAO"] if e else None,
        "PRECISAO": e["PRECISAO"] if e else "NOT_KNOWN",
        "BASIS": ("offset %d · %s" % (e["BASIS"]["OFFSET"], e["PORQUE"])) if e else
                 "; ".join("%s=%s" % (d["VALOR"], d["PORQUE"][:40]) for d in r["DESCARTADOS"][:4]),
        "TODOS": {t: [x["VALOR"] for x in r[t]] for t in TP.TIPOS},
        "SEM_ANO": bool(e and e["SEM_ANO"]),
        "ANO_COM_BASE": bool(e and e.get("ANO_BASIS")),
        "ANO_PROCEDENCIA": (e or {}).get("PROCEDENCIA_DO_ANO"),
    }


# ── contar ───────────────────────────────────────────────────────────────────
def _valores_do_tipo(caso, tipo):
    """Os valores que o golden diz serem daquele tipo (publicacao, validade…)."""
    fora = []
    for t in caso["TEMPOS"]:
        if str(_de(t, _ALIAS_TIPO, "")).upper() == tipo:
            v = iso(_de(t, _ALIAS_VALOR))
            if v:
                fora.append(v)
    if tipo == "PUBLICATION_TIME" and caso["PUB"]:
        fora.append(iso(caso["PUB"]))
    if caso["TIPO"] == tipo and caso["VALOR"]:
        fora.append(iso(caso["VALOR"]))
    # O valor que o golden ESPERA como facto nao conta como confusao, mesmo quando
    # coincide com a publicacao: no C7 do LAB a rilevacao de preco foi feita e
    # publicada no mesmo dia, e a data e mesmo do facto.
    if caso["TIPO"] == "FACT_TIME" and caso["VALOR"]:
        esperado = iso(caso["VALOR"])
        fora = [v for v in fora if v != esperado]
    return [v for v in fora if v]


_FINO = {TP.DAY: 0, TP.INTERVAL: 0, TP.WEEK: 1, TP.MONTH: 2, TP.SEASON: 3, TP.YEAR: 3}


def mede(casos, correr, nome):
    r = {"NOME": nome, "ACERTO": 0, "TOTAL": len(casos),
         "PUBLICATION_TIME_USADO_COMO_FACT_TIME": 0,
         "VALIDITY_TIME_CONFUNDIDO_COM_FACT_TIME": 0,
         "DATA_INVENTADA": 0, "PRECISAO_INVENTADA": 0,
         "ERROS_CRITICOS": [], "DETALHE": []}
    for caso in casos:
        s = correr(caso)
        esperado_tipo = caso["TIPO"] if caso["VALOR"] and not nada(caso["VALOR"]) else None
        esperado_val = iso(caso["VALOR"])
        acertou = ((s["TIPO"] or None) == (esperado_tipo if esperado_tipo == "FACT_TIME" else None)
                   and (s["VALOR"] or None) == (esperado_val if esperado_tipo == "FACT_TIME" else None))
        # quando o golden espera OUTRO tipo (validade/publicacao/ato/mercado), o acerto
        # do campo FACT_TIME e nao dar nada nele
        if esperado_tipo and esperado_tipo != "FACT_TIME":
            acertou = s["TIPO"] is None
            if not acertou and "TODOS" in s:
                acertou = esperado_val in s["TODOS"].get(esperado_tipo, [])
        if acertou:
            r["ACERTO"] += 1
        criticos = []
        if s["VALOR"]:
            if s["VALOR"] in _valores_do_tipo(caso, "PUBLICATION_TIME"):
                r["PUBLICATION_TIME_USADO_COMO_FACT_TIME"] += 1
                criticos.append("data de PUBLICACAO/EDICAO no FACT_TIME")
            if s["VALOR"] in _valores_do_tipo(caso, "VALIDITY_TIME"):
                r["VALIDITY_TIME_CONFUNDIDO_COM_FACT_TIME"] += 1
                criticos.append("janela de VALIDADE no FACT_TIME")
            if not _no_texto(s["VALOR"], caso["TEXTO"]):
                r["DATA_INVENTADA"] += 1
                criticos.append("valor «%s» nao esta escrito no texto" % s["VALOR"])
            if esperado_val:
                fino_s = _FINO.get(s["PRECISAO"], 9)
                fino_e = _FINO.get(caso["PRECISAO"] or "", None)
                if fino_e is None:
                    fino_e = _FINO.get(_precisao_do_valor(esperado_val), 9)
                if fino_s < fino_e:
                    r["PRECISAO_INVENTADA"] += 1
                    criticos.append("precisao %s onde o texto so da %s"
                                    % (s["PRECISAO"], caso["PRECISAO"] or _precisao_do_valor(esperado_val)))
                elif TP.SEM_ANO in esperado_val and TP.SEM_ANO not in str(s["VALOR"]):
                    # Um ano COMPOSTO do cabecalho do mesmo documento, com os dois trechos
                    # citados e a procedencia escrita, nao e ano inventado (D147 itens 1-2):
                    # o texto da o ano, noutro sitio, e a saida diz onde. Sem essa base, e
                    # invencao e conta como critico.
                    if s.get("ANO_COM_BASE"):
                        criticos.append("ano «%s» composto do cabecalho (nao invencao): %s"
                                        % (str(s["VALOR"])[:4], s.get("ANO_PROCEDENCIA")))
                    else:
                        r["PRECISAO_INVENTADA"] += 1
                        criticos.append("ano «%s» onde o texto nao da ano" % str(s["VALOR"])[:4])
        if not acertou:
            criticos.append("esperado %s=%s, saiu %s=%s" % (esperado_tipo or "NADA", esperado_val or "NAO SEI",
                                                            s["TIPO"] or "NADA", s["VALOR"] or "NAO SEI"))
        if criticos:
            r["ERROS_CRITICOS"].append({"ID": caso["ID"], "PORQUE": criticos,
                                        "EXPRESSAO": s["BRUTO"], "BASE": s["BASIS"][:160]})
        r["DETALHE"].append({"ID": caso["ID"], "ACERTO": acertou, "SAIU": s["VALOR"],
                             "ESPERADO": esperado_val, "TIPO_ESPERADO": esperado_tipo,
                             "PRECISAO": s["PRECISAO"]})
    return r


def _precisao_do_valor(v):
    v = str(v or "")
    if "/" in v:
        return TP.INTERVAL
    if "-W" in v.upper():
        return TP.WEEK
    if re.match(r"^(?:\d{4}|SEM_ANO)-\d{2}-\d{2}$", v, re.I):
        return TP.DAY
    if re.match(r"^(?:\d{4}|SEM_ANO)-\d{2}$", v, re.I):
        return TP.MONTH
    return TP.YEAR


def sha256_de(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    caminho = argv[1]
    brutos, envelope = carrega(caminho)
    casos = [le_caso(c, i) for i, c in enumerate(brutos)]
    sem_texto = [c["ID"] for c in casos if not c["TEXTO"].strip()]
    print("GOLDEN_SET      %s" % caminho)
    print("SHA256_MEDIDO   %s" % sha256_de(caminho))
    if "--sha256" in argv:
        f = argv[argv.index("--sha256") + 1]
        declarado = open(f, encoding="utf-8").read().split()[0] if os.path.exists(f) else "(ficheiro ausente)"
        print("SHA256_DECLARADO %s  -> %s" % (
            declarado, "BATE" if declarado == sha256_de(caminho) else "NAO BATE"))
    print("CASOS           %d" % len(casos))
    if sem_texto:
        print("AVISO: %d casos sem campo de texto reconhecido: %s" % (len(sem_texto), ", ".join(sem_texto[:8])))
    resultados = [mede(casos, atual, "P3_ATUAL"), mede(casos, proposto, "P3_PROPOSTO")]
    for r in resultados:
        print("\n== %s ==" % r["NOME"])
        print("ACERTO                                  %d/%d" % (r["ACERTO"], r["TOTAL"]))
        for k in ("PUBLICATION_TIME_USADO_COMO_FACT_TIME", "VALIDITY_TIME_CONFUNDIDO_COM_FACT_TIME",
                  "DATA_INVENTADA", "PRECISAO_INVENTADA"):
            print("%-40s%d" % (k, r[k]))
        print("ERROS_CRITICOS (%d):" % len(r["ERROS_CRITICOS"]))
        for e in r["ERROS_CRITICOS"]:
            print("  - %-14s %s" % (e["ID"], " | ".join(e["PORQUE"])))
    saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_resultado.json")
    with open(saida, "w", encoding="utf-8") as f:
        json.dump({"GOLDEN": caminho, "SHA256": sha256_de(caminho),
                   "ENVELOPE": {k: v for k, v in (envelope or {}).items() if not isinstance(v, list)},
                   "RESULTADOS": resultados}, f, ensure_ascii=False, indent=1)
    print("\nescrito: %s" % saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
