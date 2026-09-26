#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D90 · o pacote que cada documento levaria como DERIVADO `TABLE_EXTRACTION` (produtor «linhas-de-monitorizacao»),
e o estado de cada documento na estrada canonica. SEM REDE, SEM BANCO, SEM ESCREVER EM LADO NENHUM do vivo.

    py curadoria/d90_payload_series.py --series=curadoria/SINAL-PRECOCE-SERIES.json \
       --raw=<RAW-SALA-LEITURA.json (SELECT so-leitura)> [--texto-arif=<N37 tirado da Sala>] --saida=<pasta fora do Git>

Escreve em <saida>: um JSON por documento (o conteudo EXACTO que `guarda/preservar_derivado.py` guardaria — o escritor
unico do derivado; aqui NAO se chama) e MANIFESTO.json. Contrato do pacote: `CONTRATO` abaixo (v0, PROPOSTA — nao ha
contrato de TABLE_EXTRACTION na casa: medido, nenhum produtor, nenhum consumidor).

Regras do pacote (da D90 e das leis da casa):
  - VALOR como veio (`VALOR_TAL_COMO_VEIO`, texto); `VALOR_NUMERICO` so quando o texto e um numero inteiro/decimal;
  - NATUREZA por linha: OBSERVACAO / PREVISAO / RECOMENDACAO — separadas; uma frase que diz duas fica MISTA (lista) e
    nao se parte ao meio;
  - o que nao se sabe fica NAO SEI com o porque (UNKNOWN nao funde nem vira facto);
  - a METRICA que o contrato da fonte ESPERA (ex.: APOL `TRAP_CAPTURES`) nao e a medida: vai em METRICA_ESPERADA_PELO_CONTRATO,
    e METRICA_MEDIDA fica NAO SEI quando o cabecalho do documento nao se le.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import series_sinal_precoce as S   # noqa: E402

PRODUTOR = "linhas-de-monitorizacao"
CONTRATO = "TABLE_EXTRACTION/linhas-de-monitorizacao/v0 (PROPOSTA D90)"
NS = "NAO SEI"
# o que o contrato de fonte (regras/italy_contracts.mjs) declara — DECLARADO != MEDIDO
EVIDENCE_CLASS = {
    "IT-T3-002": "TECHNICAL_GUIDELINE + OBSERVED_FIELD_SIGNAL pontual (rotulo Presente/Non Presente)",
    "IT-T3-010": "OBSERVED_FIELD_SIGNAL + COOPERATIVE_GUIDANCE",
    "IT-T3-008": "OBSERVED_FIELD_SIGNAL + TECHNICAL_GUIDELINE (separar por bloco: 'Situazione Fitosanitaria' e OBSERVED, "
                 "'Programma di Difesa' e RECOMMENDED)",
    "IT-T3-005": "OBSERVED_FIELD_SIGNAL + COOPERATIVE_GUIDANCE",
    "IT-T2-002": "AGROCLIMATIC_SIGNAL (LEI do contrato: AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE)",
}
APOL_COLUNAS = [("COLUNA_1", "TRAP_CAPTURES"), ("COLUNA_2", NS), ("COLUNA_3", "ACTIVE_INFESTATION_PERCENT")]


def _num(v) -> float | int | None:
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return v
    m = re.fullmatch(r"\s*(\d+(?:[.,]\d+)?)\s*%?\s*", str(v))
    if not m:
        return None
    x = m.group(1).replace(",", ".")
    return float(x) if "." in x else int(x)


def _id(*partes) -> str:
    return hashlib.sha256("|".join(str(p) for p in partes).encode("utf-8")).hexdigest()[:24]


def _linha(parent: str, **k) -> dict:
    base = {"CULTURA": NS, "LOCAL": NS, "ARMADILHA": NS, "ORGANISMO": NS, "METRICA_MEDIDA": NS,
            "METRICA_ESPERADA_PELO_CONTRATO": None, "VALOR_TAL_COMO_VEIO": None, "VALOR_NUMERICO": None, "UNIDADE": NS,
            "LIMIAR": None, "FASE": NS, "DATA_DO_FACTO": NS, "DATA_DO_FACTO_BASE": NS, "NATUREZA": [], "TRECHO": None,
            "CONFERE": None, "ORIGEM": None}
    base.update(k)
    if base["VALOR_NUMERICO"] is None and base["VALOR_TAL_COMO_VEIO"] is not None:
        base["VALOR_NUMERICO"] = _num(base["VALOR_TAL_COMO_VEIO"])
    base["NATUREZA_UNICA"] = base["NATUREZA"][0] if len(base["NATUREZA"]) == 1 else ("MISTA" if base["NATUREZA"] else NS)
    base["LINHA_ID"] = _id(parent, base["LOCAL"], base["ORGANISMO"], base["METRICA_MEDIDA"], base.get("METRICA_ESPERADA_PELO_CONTRATO"),
                           base["TRECHO"])
    return base


def linhas(doc: dict) -> list[dict]:
    p, f, out = doc["SHA256"], doc["FORMA"], []
    for l in doc["LINHAS"]:
        if f == "SALERNO":
            out.append(_linha(p, CULTURA=l["CULTURA"], LOCAL=l["LOCAL"], ORGANISMO=l["ORGANISMO"],
                              ARMADILHA="rete di monitoraggio (armadilha nao nomeada no boletim)",
                              METRICA_MEDIDA="catture (n.)" if l["METRICA"] == "catture" else "estado (texto)",
                              VALOR_TAL_COMO_VEIO=str(l["VALOR"]), UNIDADE="capturas" if l["METRICA"] == "catture" else NS,
                              FASE=l["FASE"], DATA_DO_FACTO=l["DATA"],
                              DATA_DO_FACTO_BASE="data do boletim N° %s (a tabela nao imprime data de campionamento)" % l["BOLETIM_N"],
                              NATUREZA=l["NATUREZA"], TRECHO=l["TRECHO"], CONFERE=l["CONFERE"], ORIGEM=l["ORIGEM"]))
        elif f == "APOL":
            for col, esperada in APOL_COLUNAS:
                out.append(_linha(p, CULTURA="olivo", LOCAL=l["LOCAL"], ORGANISMO=l["ORGANISMO"],
                                  METRICA_MEDIDA="NAO SEI (cabecalho da tabela e imagem) — %s" % col,
                                  METRICA_ESPERADA_PELO_CONTRATO=esperada, VALOR_TAL_COMO_VEIO=str(l[col]),
                                  FASE=l["FASE"], DATA_DO_FACTO=l["DATA"],
                                  DATA_DO_FACTO_BASE="VALID_FROM do periodo impresso %s (contrato: VALIDADE, nao publicacao)" % (l.get("PERIODO"),),
                                  NATUREZA=l["NATUREZA"], TRECHO=l["TRECHO"], ORIGEM="extractor apol (layout)"))
            out.append(_linha(p, CULTURA="olivo", LOCAL=l["LOCAL"], ORGANISMO=l["ORGANISMO"], METRICA_MEDIDA="TENDENCIA / RISCO (rotulo)",
                              METRICA_ESPERADA_PELO_CONTRATO="TREND_LABEL", VALOR_TAL_COMO_VEIO="%s / %s" % (l["TENDENCIA"], l["RISCO"]),
                              FASE=l["FASE"], DATA_DO_FACTO=l["DATA"], DATA_DO_FACTO_BASE="VALID_FROM do periodo impresso",
                              NATUREZA=l["NATUREZA"], TRECHO=l["TRECHO"], ORIGEM="extractor apol (layout)"))
        elif f == "TERRETRURIA":
            out.append(_linha(p, CULTURA="olivo", LOCAL="%s (lat %s, lon %s)" % (l["LOCAL"], l["LAT"], l["LON"]),
                              ORGANISMO=l["ORGANISMO"], ARMADILHA="catture adulti: fechado por login (fora)",
                              METRICA_MEDIDA="Infestazione attiva", METRICA_ESPERADA_PELO_CONTRATO="INFESTATION_PERCENT",
                              VALOR_TAL_COMO_VEIO=l["VALOR"], UNIDADE="%", LIMIAR=l.get("ESTADO"),
                              DATA_DO_FACTO=l["DATA"] or NS,
                              DATA_DO_FACTO_BASE="Data di campionamento impressa no ponto" if l["DATA"] else "o ponto diz «-»",
                              NATUREZA=l["NATUREZA"], TRECHO=l["TRECHO"], ORIGEM="extractor terretruria (HTML)"))
        elif f == "ARIF":
            comum = dict(CULTURA="NAO SEI (titulo em imagem)", LOCAL="NAO SEI (titulo em imagem) · bloco %02d" % l["BLOCO"],
                         FASE=l["FASE"], DATA_DO_FACTO=l["DATA"], ORIGEM=l["ORIGEM"],
                         DATA_DO_FACTO_BASE="inicio da semana do Notiziario N.%s" % l["BOLETIM_N"])
            out.append(_linha(p, METRICA_MEDIDA="Situazione Fitosanitaria (texto)", VALOR_TAL_COMO_VEIO=l["OBSERVACAO"],
                              NATUREZA=["OBSERVACAO"], TRECHO=l["OBSERVACAO"][:300], **comum))
            if l["RECOMENDACAO"] and not re.match(r"Nessun consiglio", l["RECOMENDACAO"]):
                out.append(_linha(p, METRICA_MEDIDA="Programma di Difesa (texto)", VALOR_TAL_COMO_VEIO=l["RECOMENDACAO"],
                                  NATUREZA=["RECOMENDACAO"], TRECHO=l["RECOMENDACAO"][:300], **comum))
            for lim in l["LIMIARES"]:
                out.append(_linha(p, METRICA_MEDIDA="limiar escrito", VALOR_TAL_COMO_VEIO=lim, LIMIAR=lim,
                                  NATUREZA=["RECOMENDACAO"], TRECHO=lim[:300], **comum))
        elif f == "ARPAV":
            out.append(_linha(p, CULTURA="olivo (secção 'settore olivicolo')", LOCAL="Veneto (texto regional igual nas 4 zonas)",
                              ORGANISMO=l["ORGANISMO"], METRICA_MEDIDA="frase (sem numero)", VALOR_TAL_COMO_VEIO=l["FRASE"],
                              DATA_DO_FACTO=NS, DATA_DO_FACTO_BASE="o boletim nao data a observacao; so o numero da edicao",
                              NATUREZA=l["NATUREZA"], TRECHO=l["FRASE"][:300], ORIGEM="frases (seccao Dai Servizi Fitosanitari)"))
    return out


def estado_na_estrada(sha: str, raw: list[dict]) -> dict:
    rs = [r for r in raw if r["SHA256"] == sha]
    if not rs:
        return {"RAW": "AUSENTE da Sala", "PROXIMO_PASSO": "entrar como RAW pelo escritor unico (guarda/preservar_coleta.py) — "
                "estrada do ramo acervo-para-sala-v1 (reprocessar_lote.py), NAO instalado"}
    com_derivado = [r for r in rs if r.get("DERIVADOS")]
    principal = (com_derivado or rs)[0]
    return {"RAW": "PRESENTE", "RAW_IDS": [r["ID"] for r in rs], "RAW_ID_PAI_PROPOSTO": principal["ID"],
            "DOCUMENT_KEY": principal.get("DOCUMENT_KEY"),
            "DERIVADOS_JA_EXISTENTES": principal.get("DERIVADOS") or [],
            "ITEM_NA_SALA": principal.get("NA_SALA") or [],
            "PROXIMO_PASSO": "derivado TABLE_EXTRACTION «%s» filho de raw_asset(%s, %s) pelo escritor unico "
                             "(guarda/preservar_derivado.py)" % (PRODUTOR, principal["ID"], sha[:12])}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    series = json.loads(Path(a["series"]).read_text(encoding="utf-8"))
    raw = json.loads(Path(a["raw"]).read_text(encoding="utf-8"))
    docs = list(series["DOCUMENTOS"])
    if a.get("texto-arif"):                      # o N37 so esta na Sala (texto do derivado 7): le-se de la, sem rede
        t = Path(a["texto-arif"]).read_text(encoding="utf-8")
        n37 = [r for r in raw if (r.get("DOCUMENT_KEY") or "").endswith(":N37")]
        docs.append({"SOURCE_ID": "IT-T3-008", "FORMA": "ARIF", "SHA256": n37[0]["SHA256"] if n37 else NS,
                     "FICHEIRO": "Sala documento_estruturado (derivado 7, raw %s)" % (n37[0]["ID"] if n37 else "?"),
                     "LINHAS": S.arif(t), "TEXTO_DA_SALA_SHA256": hashlib.sha256(t.encode("utf-8")).hexdigest()})
    saida = Path(a["saida"])
    saida.mkdir(parents=True, exist_ok=True)
    manifesto = []
    for d in docs:
        ls = linhas(d)
        pacote = {"CONTRATO": CONTRATO, "KIND": "TABLE_EXTRACTION", "PRODUCER": PRODUTOR,
                  "PARENT_SHA256": d["SHA256"], "SOURCE_ID": d["SOURCE_ID"], "FORMA": d["FORMA"],
                  "SOURCE_DECLARED_EVIDENCE_CLASS": EVIDENCE_CLASS.get(d["SOURCE_ID"], NS), "LINHAS": ls}
        b = (json.dumps(pacote, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")
        nome = "%s-%s.json" % (d["SOURCE_ID"], d["SHA256"][:12])
        (saida / nome).write_bytes(b)
        nat = {}
        for x in ls:
            nat[x["NATUREZA_UNICA"]] = nat.get(x["NATUREZA_UNICA"], 0) + 1
        manifesto.append({"SOURCE_ID": d["SOURCE_ID"], "FORMA": d["FORMA"], "DOCUMENTO": d.get("FICHEIRO"),
                          "PARENT_SHA256": d["SHA256"], "PACOTE": nome, "PACOTE_SHA256": hashlib.sha256(b).hexdigest(),
                          "LINHAS": len(ls), "POR_NATUREZA": nat,
                          "COM_VALOR_NUMERICO": sum(1 for x in ls if x["VALOR_NUMERICO"] is not None),
                          **estado_na_estrada(d["SHA256"], raw)})
    (saida / "MANIFESTO.json").write_text(json.dumps({"CONTRATO": CONTRATO, "DOCUMENTOS": manifesto}, ensure_ascii=False, indent=1) + "\n",
                                          encoding="utf-8")
    print(json.dumps({"DOCUMENTOS": len(manifesto), "LINHAS": sum(m["LINHAS"] for m in manifesto),
                      "RAW_PRESENTE": sum(1 for m in manifesto if m["RAW"] == "PRESENTE"),
                      "RAW_AUSENTE": sum(1 for m in manifesto if m["RAW"] != "PRESENTE")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
