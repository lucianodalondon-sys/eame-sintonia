# -*- coding: utf-8 -*-
"""LOTE-MICRO-V3 — aplica a REGRA-LOTE-MICRO-V3.md (commitada ANTES de ver os insumos) aos insumos fixados.

    py ferramentas/rendimento/lote_micro_v3.py --coorte=<json> --d40=<json> --bc5=<json, o blob do Git> [--saida=ferramentas/rendimento/LOTE-MICRO-V3.json]

Sem rede. Os insumos conferem-se pelo sha256 escrito na regra; se nao baterem, rebenta.
O dominio registavel pergunta-se ao transporte (onda_web.dominios), a mesma regra do teto D38.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
import onda_web as O  # noqa: E402

SHA = {"coorte": "c168e19236136761369998d4c63272ea5eab8fa4b0d580c67c83a03225d7f4bb",
       "d40": "15ba6bc332d65833ee8217a0484eca06f61437c17cc10008df5c1cf70e215d0c",
       "bc5": "972d6be105193e33b0d4cb7278cdd1ecd5bfe41a9d8d9d5d7f1753d9fdef5211"}
ISTAT = "IT-T5-090"
OBRIGATORIA = "IT-T10-018"
AGENCIA_T2 = ("arpa", "arpae", "arpal", "arpat", "arpacampania", "arpav")   # donos publicos de ambiente/meteo
TAMANHO = 6
TETO_MATERIAS = 3                                                           # robots + indice + ate 3 = 5


def _le(p: Path, nome: str) -> dict:
    b = p.read_bytes()
    h = hashlib.sha256(b).hexdigest()
    if h != SHA[nome]:
        raise SystemExit("INSUMO_DIFERENTE_DA_REGRA %s: %s != %s" % (nome, h, SHA[nome]))
    return json.loads(b)


def escolher(coorte: dict, d40: dict, bc5: dict, dominio_de) -> dict:
    fontes = [x for x in coorte["COORTE"]]
    fora = []
    if any(x["SOURCE_ID"] == ISTAT for x in fontes):
        fora.append({"SOURCE_ID": ISTAT, "PORQUE": "ISTAT fora por decisao da missao (D45)"})
        fontes = [x for x in fontes if x["SOURCE_ID"] != ISTAT]
    med = {f["SOURCE_ID"]: f for f in d40["FONTES"]}
    hist = {f["SOURCE_ID"]: f for f in bc5["FONTES"]}
    hosts = {x["SOURCE_ID"]: (x.get("INDEX_URL") or "").split("/")[2] if "//" in (x.get("INDEX_URL") or "") else ""
             for x in fontes}
    dom = dominio_de(sorted(set(hosts.values())))
    linhas = {}
    for x in fontes:
        s = x["SOURCE_ID"]
        m = med.get(s)
        h = hist.get(s) or {}
        adm = h.get("ADMISSION") or {}
        linhas[s] = {"SOURCE_ID": s, "UNIVERSO": x.get("UNIVERSO") or s.split("-")[1], "HOST": hosts[s],
                     "DOMINIO": dom.get(hosts[s], hosts[s]),
                     "ALVOS_NOVOS_D40": (m.get("ESCOLHIDOS") or 0) if m and m.get("MEDIDO") == "OK" else 0,
                     "D40_MEDIDO": (m.get("MEDIDO") if m else "NAO_MEDIDA"),
                     "BC5_SIM": adm.get("SIM", 0), "BC5_JULGADOS": sum(adm.values()) if adm else 0,
                     "BC5_CORREU": bool(h)}
    chave = lambda l: (-l["ALVOS_NOVOS_D40"], -l["BC5_SIM"], l["SOURCE_ID"])     # noqa: E731 — criterio C
    escolha, usados, passos = [], set(), []

    def toma(l, passo):
        escolha.append(dict(l, PASSO=passo))
        usados.add(l["DOMINIO"])

    def livres(pred):
        return sorted((l for l in linhas.values() if pred(l) and l["SOURCE_ID"] not in {e["SOURCE_ID"] for e in escolha}
                       and l["DOMINIO"] not in usados), key=chave)

    toma(linhas[OBRIGATORIA], "1 OBRIGATORIA (myfruit)")
    t2 = livres(lambda l: l["UNIVERSO"] == "T2" and any(l["HOST"].split(".")[-2].startswith(a) or a in l["HOST"]
                                                       for a in AGENCIA_T2))
    for l in t2[:2]:
        toma(l, "2 AGENCIA T2")
    if len(t2) < 2:
        passos.append("PASSO_2_INCOMPLETO: so %d agencia(s) T2 de dominio distinto" % len(t2))
    t1 = livres(lambda l: l["UNIVERSO"] == "T1")
    if t1:
        toma(t1[0], "3 REGUA T1")
    else:
        passos.append("SEM_ELEGIVEL_T1: a coorte nao tem fonte com UNIVERSO=T1; a vaga passa ao passo 4")
    for l in livres(lambda l: True):
        if len(escolha) >= TAMANHO:
            break
        toma(l, "4 CRITERIO C")
    for e in escolha:
        docs = min(e["ALVOS_NOVOS_D40"], TETO_MATERIAS)
        e["PREVISAO_DOCUMENTOS_NOVOS"] = docs
        if e["BC5_JULGADOS"]:
            e["PREVISAO_SIM"] = round(docs * e["BC5_SIM"] / e["BC5_JULGADOS"], 2)
            e["PREVISAO_SIM_COMO"] = "docs novos x (SIM/julgados na BC5 = %d/%d)" % (e["BC5_SIM"], e["BC5_JULGADOS"])
        else:
            e["PREVISAO_SIM"] = "NAO_SEI"
            e["PREVISAO_SIM_COMO"] = ("sem historico na BC5" if not e["BC5_CORREU"]
                                      else "correu na BC5 mas 0 documentos julgados")
        e["SE_NAO_RODAR"] = "NAO_RODOU (com o motivo) — nao conta como 0 SIM e sai do denominador"
    num = [e["PREVISAO_SIM"] for e in escolha if isinstance(e["PREVISAO_SIM"], (int, float))]
    return {"ESCOLHA": escolha, "FORA": fora, "NOTAS_DA_REGRA": passos,
            "PREVISAO_TOTAL": {"DOCUMENTOS_NOVOS": sum(e["PREVISAO_DOCUMENTOS_NOVOS"] for e in escolha),
                               "SIM_SO_DAS_FONTES_COM_HISTORICO": round(sum(num), 2),
                               "FONTES_COM_SIM_NAO_SEI": [e["SOURCE_ID"] for e in escolha if e["PREVISAO_SIM"] == "NAO_SEI"]},
            "UNIVERSO_DA_REGRA": len(linhas)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    coorte = _le(Path(a["coorte"]), "coorte")
    d40 = _le(Path(a["d40"]), "d40")
    bc5 = _le(Path(a["bc5"]), "bc5")      # o BLOB do Git (o disco do Windows pode ter CRLF e outro sha)
    r = escolher(coorte, d40, bc5, O.dominios)
    out = {"DATASET": "LOTE-MICRO-V3", "DECISAO": "D45 (bot Luciano, 25/09)",
           "REGRA": "ferramentas/rendimento/REGRA-LOTE-MICRO-V3.md (commit ae7fac6e, 05:40:32, ANTES de abrir os insumos)",
           "INSUMOS_SHA256": SHA, "REDE": "fechada — nenhum pedido",
           "CRITERIO_D35": {"NUMERADOR": "documentos com SIM na Admissao (linhas novas da sala_de_espera)",
                            "DENOMINADOR": "fontes que CORRERAM (1.a onda: 3 SIM / 18 fontes = 16,7%)",
                            "PASSA_SE": "SIM/fontes_que_correram > 16,7% E >= 2 SIM (bot Luciano, 6 fontes)",
                            "NAO_RODOU": "fica NAO_RODOU com o motivo; nao e 0 SIM; sai do denominador"},
           **r}
    s = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    if a.get("saida"):
        Path(a["saida"]).write_text(s, encoding="utf-8")
    print(s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
