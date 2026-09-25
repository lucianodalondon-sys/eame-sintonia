# -*- coding: utf-8 -*-
"""ENTRADA DE JANELA — trocar SO o endereco de entrada das fontes de janela MENU / PAGINA=BOLETIM /
NAO SEI pelo endereco que a P1g (janelas-regioes-v1) mediu com boletim datado (JANELAS-68-v2, 25/09).

    py curadoria/entrada_janela.py --formas=<JANELAS-68-FORMAS-V1.json> --celulas=<JANELAS-REGIOES-V1.json>
        --contratos=<italy_contracts_curator.json> [--aplicar] [--saida=...]

Mesmo molde de `entrada_final.py` (AJUSTES-MICRO): proposta pura, SO com prova ja guardada (sem rede),
aplicada pela PORTA do reparo (`reparar_contrato.aplicar`), que guarda a ACQUISITION anterior, passa o
validador da casa e marca PRECISA_DE_REMEDIR. Nunca promove: o canario seguinte e que decide.

A prova de um endereco novo e toda da P1g:
  1. a celula (ou a pagina aprofundada) foi medida PUBLICO_COM_BOLETIM;
  2. tem EXEMPLO com DATA e REVISAO BOLETIM_REAL (um boletim datado lido por olhos, nao so um link);
  3. esta no MESMO host da entrada actual — outro host e outra fonte (D21), nao um reparo;
  4. NENHUM outro contrato do livro ja entra por esse endereco — senao a troca faz uma gemea
     (dois contratos a colher o mesmo documento) e a proposta e recusada com o dono.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

FORMAS_ALVO = ("MENU", "PAGINA_BOLETIM", "NAO_SEI")


def _host(u: str) -> str:
    return urlparse(u or "").netloc.lower().removeprefix("www.")


def _norm(u: str) -> str:
    return (u or "").strip().rstrip("/").lower().replace("://www.", "://")


def entradas_provadas(celulas: list) -> list:
    """[(endereco, exemplo)] que a P1g mediu com boletim datado e revisto."""
    out = []
    for c in celulas:
        ex = c.get("EXEMPLO") or {}
        if not (ex.get("DATA") and ex.get("REVISAO") == "BOLETIM_REAL"):
            continue
        if c.get("ESTADO_MEDIDO") == "PUBLICO_COM_BOLETIM":
            out.append((ex.get("VIA") or c["URL"], ex))
        for a in c.get("APROFUNDADO") or []:
            if isinstance(a, dict) and a.get("ESTADO_MEDIDO") == "PUBLICO_COM_BOLETIM" and a["URL"] == ex.get("VIA"):
                out.append((a["URL"], ex))
    vistos, unicos = set(), []
    for u, ex in out:
        if _norm(u) not in vistos:
            vistos.add(_norm(u))
            unicos.append((u, ex))
    return unicos


def donos_de_entrada(contratos: list) -> dict:
    d = {}
    for c in contratos:
        for u in (c.get("CANONICAL_ENTRY_URL"), (c.get("ACQUISITION") or {}).get("INDEX_URL")):
            if u:
                d.setdefault(_norm(u), set()).add(c["SOURCE_ID"])
    return d


def propor(contrato: dict, provadas: list, donos: dict) -> dict:
    """PADRAO_NOVO (so a INDEX_URL muda) ou {"DESFECHO": "SEM_PROPOSTA", "MOTIVO", "PORQUE"}. Pura."""
    aq = contrato.get("ACQUISITION") or {}
    iu, pad = aq.get("INDEX_URL"), aq.get("LINK_PATTERN")
    if not iu or not pad:
        return {"DESFECHO": "SEM_PROPOSTA", "MOTIVO": "CONTRATO_SEM_ENTRADA", "PORQUE": "sem INDEX_URL/LINK_PATTERN"}
    mesmas = [(u, ex) for u, ex in provadas if _host(u) == _host(iu) and _norm(u) != _norm(iu)]
    if not mesmas:
        return {"DESFECHO": "SEM_PROPOSTA", "MOTIVO": "SEM_PROVA_NA_P1G",
                "PORQUE": "a P1g nao mediu boletim datado noutro endereco de %s" % _host(iu)}
    livres = [(u, ex) for u, ex in mesmas if not (donos.get(_norm(u), set()) - {contrato["SOURCE_ID"]})]
    if not livres:
        u, _ = mesmas[0]
        return {"DESFECHO": "SEM_PROPOSTA", "MOTIVO": "ENTRADA_JA_TEM_DONO",
                "DONO": sorted(donos[_norm(u)] - {contrato["SOURCE_ID"]}), "ENTRADA_PROVADA": u,
                "PORQUE": "o endereco provado %s ja e a entrada de %s: trocar faria uma gemea"
                          % (u, ", ".join(sorted(donos[_norm(u)] - {contrato["SOURCE_ID"]})))}
    u, ex = max(livres, key=lambda x: x[1]["DATA"])            # o boletim mais recente decide
    return {"DESFECHO": "PADRAO_NOVO", "INDEX_URL": u, "LINK_PATTERN": pad,
            "COMO": "ENTRADA_DE_JANELA: a P1g mediu boletim datado em %s (%s); so a INDEX_URL muda" % (u, ex["DATA"]),
            "ACQUISITION_ANTERIOR": dict(aq), "ENTRADA": u, "ITEM_LIDO": ex.get("URL"),
            "ALVOS_NA_LISTAGEM": [ex.get("URL")],
            "PORQUE": "exemplo %s de %s, revisto BOLETIM_REAL" % (ex.get("URL"), ex["DATA"])}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    formas = json.loads(Path(a["formas"]).read_text(encoding="utf-8"))["FONTES"]
    provadas = entradas_provadas(json.loads(Path(a["celulas"]).read_text(encoding="utf-8"))["CELULAS"])
    cpath = Path(a["contratos"])
    livro = json.loads(cpath.read_text(encoding="utf-8"))
    por_sid = {c["SOURCE_ID"]: c for c in livro["FONTES"]}
    donos = donos_de_entrada(livro["FONTES"])
    import reparar_contrato as RC                          # noqa: E402 — a porta do reparo
    out, novos = [], {}
    for f in formas:
        if f["FORMA"] not in FORMAS_ALVO:
            continue
        c = por_sid.get(f["SOURCE_ID"])
        if not c:
            out.append({"SOURCE_ID": f["SOURCE_ID"], "FORMA": f["FORMA"], "DESFECHO": "SEM_PROPOSTA",
                        "MOTIVO": "SEM_CONTRATO_NO_LIVRO"})
            continue
        p = propor(c, provadas, donos)
        linha = {"SOURCE_ID": c["SOURCE_ID"], "FORMA": f["FORMA"],
                 "INDEX_URL_ANTES": (c.get("ACQUISITION") or {}).get("INDEX_URL"),
                 **{k: p.get(k) for k in ("DESFECHO", "MOTIVO", "INDEX_URL", "DONO", "ENTRADA_PROVADA", "PORQUE",
                                          "ITEM_LIDO")}}
        if p["DESFECHO"] == "PADRAO_NOVO":
            novos[c["SOURCE_ID"]] = RC.aplicar(c, p)                # rebenta se o validador da casa reprovar
            donos.setdefault(_norm(p["INDEX_URL"]), set()).add(c["SOURCE_ID"])   # a 2.a gemea ja nao passa
            linha["SHA256_DEPOIS"] = novos[c["SOURCE_ID"]]["SOURCE_CONTRACT_HASH"]
        out.append({k: v for k, v in linha.items() if v is not None})
    if "--aplicar" in argv and novos:
        livro["FONTES"] = [novos.get(c["SOURCE_ID"], c) for c in livro["FONTES"]]
        tmp = cpath.with_suffix(".tmp")
        tmp.write_text(json.dumps(livro, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(cpath)
    from collections import Counter
    r = {"DATASET": "ENTRADA-DE-JANELA", "APLICADO": "--aplicar" in argv and bool(novos), "CONTRATOS": str(cpath),
         "ENTRADAS_PROVADAS_NA_P1G": [{"URL": u, "EXEMPLO": ex.get("URL"), "DATA": ex["DATA"]} for u, ex in provadas],
         "N": len(out), "POR_DESFECHO": dict(Counter(l.get("MOTIVO") or l["DESFECHO"] for l in out).most_common()),
         "PROPOSTAS": [l for l in out if l["DESFECHO"] == "PADRAO_NOVO"],
         "SEM_PROPOSTA": [l for l in out if l["DESFECHO"] != "PADRAO_NOVO"]}
    s = json.dumps(r, ensure_ascii=False, indent=1) + "\n"
    if a.get("saida"):
        Path(a["saida"]).write_text(s, encoding="utf-8")
    print(json.dumps({k: r[k] for k in ("N", "POR_DESFECHO", "APLICADO")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
