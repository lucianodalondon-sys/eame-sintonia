#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REROUTE D2 (D56) · antes/depois no acervo completo, sem rede e sem Sala.

    py ferramentas/reroute/medir_reroute.py --base=df0865e6 --hoje=<json dos 49 docs ligados ao livro>

1. NENHUMA REGUA MUDA: cada par (texto, universo com regua) julgado pela admissao da base e pela desta
   arvore da o MESMO veredito. O REROUTE so acrescenta evidencia.
2. Os textos com UNIVERSO DECLARADO conhecido (o gabarito das reguas, pelo TEXTO_SHA256 -> SOURCE_ID;
   e os 49 documentos das ondas de hoje, ligados ao livro de decisoes): quantos NAO/NAO_SE_APLICA da
   gaveta da fonte passam a ter SIM noutra gaveta, e em quais.
3. Contra os ROTULOS HUMANOS do gabarito V1 (UNIVERSE_MATCH, SINTONIA_RELEVANT): o REROUTE acende onde
   a pessoa disse «serve ao Sintonia» e apaga onde disse que nao?
4. A matriz inteira (texto x universo), para quem quiser ver sem universo declarado.
O corpus e o mesmo das medicoes das reguas (scripts/regua_t2/medir_via_agrometeo.PASTAS), deduplicado
pelo sha256 do texto, como em medir_t2c.py.
"""
from __future__ import annotations

import hashlib
import importlib.util as u
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
R2 = RAIZ / "scripts" / "regua_t2"
_s = u.spec_from_file_location("mr", R2 / "medir_regua_t2.py")
MR = u.module_from_spec(_s)
_s.loader.exec_module(MR)
_s = u.spec_from_file_location("mva", R2 / "medir_via_agrometeo.py")
MVA = u.module_from_spec(_s)
_s.loader.exec_module(MVA)
A = MR.A                                   # a admissao desta arvore (com o REROUTE)


def _arg(n, d=None):
    return next((x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--%s=" % n)), d)


def universo_do_source_id(s: str) -> str | None:
    m = re.match(r"^[A-Z]{2}-(T\d+)-", s or "")
    return m.group(1) if m else None


def corpus():
    """--armazem=<copia>: le a COPIA dos textos do armazem da Sala, nunca o armazem vivo."""
    pastas = list(MVA.PASTAS)
    if _arg("armazem"):
        pastas = [Path(_arg("armazem")) if "TEXT_EXTRACTION" in str(p) else p for p in pastas]
    out, vistos = [], set()
    for d in pastas:
        if d.is_dir():
            for p in sorted(d.rglob("*.txt")):
                t = p.read_text(encoding="utf-8", errors="replace")
                h = hashlib.sha256(t.encode("utf-8")).hexdigest()
                if h not in vistos:
                    vistos.add(h)
                    out.append({"NOME": d.name + ":" + p.name, "SHA": h, "TEXTO": t})
    return out


def gabarito() -> dict:
    """TEXTO_SHA256 -> {SOURCE_ID, UNIVERSO, rotulos humanos}."""
    g = {}
    for v in ("V1", "V2", "V3"):
        d = json.loads((R2 / ("GABARITO-T2-%s.json" % v)).read_text(encoding="utf-8"))
        for x in d["ITENS"]:
            e = g.setdefault(x["TEXTO_SHA256"], {"SOURCE_ID": x.get("SOURCE_ID"),
                                                 "UNIVERSO": universo_do_source_id(x.get("SOURCE_ID"))})
            for k in ("UNIVERSE_MATCH", "SINTONIA_RELEVANT", "ACTION"):
                if x.get(k) and k not in e:
                    e[k] = x[k]
    return g


def destinos(texto: str, origem: str) -> list:
    return A.reencaminhar({"texto": texto}, origem)["DESTINOS"]


def main():
    base = MR.admissao_da_revisao(_arg("base", "df0865e6"))
    reguas = sorted(A.PERGUNTAS_DO_UNIVERSO)
    C = corpus()
    G = gabarito()
    # 1 · nenhuma regua muda
    mudou = []
    for c in C:
        for uv in reguas:
            a, _ = MR.julgar(base, c["TEXTO"], uv)
            d, _ = MR.julgar(A, c["TEXTO"], uv)
            if a != d:
                mudou.append({"TEXTO": c["NOME"], "UNIVERSO": uv, "ANTES": a, "DEPOIS": d})
    # 2 · universo declarado conhecido
    declarados = []
    for c in C:
        g = G.get(c["SHA"])
        if g and g["UNIVERSO"]:
            declarados.append(dict(c, UNIVERSO=g["UNIVERSO"], SOURCE_ID=g["SOURCE_ID"], ROT=g, DE="gabarito"))
    hoje = json.loads(Path(_arg("hoje")).read_text(encoding="utf-8")) if _arg("hoje") else []
    for h in hoje:
        declarados.append({"NOME": "hoje:" + h["FICHEIRO"], "SHA": h["SHA"], "TEXTO": Path(h["CAMINHO"]).read_text(
            encoding="utf-8", errors="replace"), "UNIVERSO": h["UNIVERSO"], "SOURCE_ID": h.get("SOURCE_ID"),
            "ROT": {}, "DE": "onda de hoje (%s)" % h["ONDA"], "REGRA_NO_LIVRO": h["REGRA"]})
    rer, por_dest, por_orig = [], Counter(), Counter()
    nao = 0
    for c in declarados:
        if c.get("REGRA_NO_LIVRO") and c["REGRA_NO_LIVRO"] != "pertence ao universo":
            continue                                   # capa/materia: nao e pergunta de tema
        r, _ = MR.julgar(A, c["TEXTO"], c["UNIVERSO"])
        if r not in (A.NAO, A.NAO_SE_APLICA):
            continue
        nao += 1
        ds = destinos(c["TEXTO"], c["UNIVERSO"])
        if ds:
            rer.append({"TEXTO": c["NOME"], "DE": c["DE"], "SOURCE_ID": c["SOURCE_ID"], "ORIGEM": c["UNIVERSO"],
                        "ORIGEM_DIZ": r, "DESTINOS": [(d["UNIVERSO"], d["PONTUACAO"]) for d in ds],
                        "TITULO": c["TEXTO"][:90].replace("\n", " "),
                        "HUMANO": {k: c["ROT"].get(k) for k in ("UNIVERSE_MATCH", "SINTONIA_RELEVANT", "ACTION")}})
            por_orig[c["UNIVERSO"]] += 1
            for d in ds:
                por_dest[d["UNIVERSO"]] += 1
    # 3 · contra os rotulos humanos (so onde a pessoa rotulou SINTONIA_RELEVANT)
    conf = Counter()
    for c in declarados:
        rel = c["ROT"].get("SINTONIA_RELEVANT")
        if not rel:
            continue
        r, _ = MR.julgar(A, c["TEXTO"], c["UNIVERSO"])
        if r not in (A.NAO, A.NAO_SE_APLICA):
            continue
        conf["humano %s · reroute %s" % (rel, "SIM" if destinos(c["TEXTO"], c["UNIVERSO"]) else "NAO")] += 1
    # 4 · a matriz inteira
    matriz = Counter()
    for c in C:
        for uv in reguas:
            r, _ = MR.julgar(A, c["TEXTO"], uv)
            if r in (A.NAO, A.NAO_SE_APLICA):
                matriz["%s NAO -> %s" % (uv, "REROUTE" if destinos(c["TEXTO"], uv) else "nenhum")] += 1
    out = {"DATASET": "MEDICAO-REROUTE-V1", "BASE": _arg("base", "df0865e6"), "REGUAS": reguas,
           "TEXTOS_NO_CORPUS": len(C), "JULGAMENTOS_ANTES_DEPOIS": len(C) * len(reguas),
           "NENHUMA_REGUA_MUDA": not mudou, "MUDANCAS_DE_VEREDITO": mudou,
           "COM_UNIVERSO_DECLARADO": len(declarados),
           "DESTES_NAO_NA_GAVETA_DA_FONTE": nao, "PASSAM_A_TER_SIM_NOUTRA_GAVETA": len(rer),
           "POR_ORIGEM": dict(por_orig), "POR_DESTINO": dict(por_dest),
           "CONTRA_O_HUMANO_V1": dict(conf), "MATRIZ_TEXTO_X_UNIVERSO": dict(sorted(matriz.items())),
           "REROUTES": rer}
    saida = Path(_arg("saida", str(RAIZ / "ferramentas" / "reroute" / "MEDICAO-REROUTE-V1.json")))
    saida.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k] for k in ("TEXTOS_NO_CORPUS", "JULGAMENTOS_ANTES_DEPOIS", "NENHUMA_REGUA_MUDA",
                                          "COM_UNIVERSO_DECLARADO", "DESTES_NAO_NA_GAVETA_DA_FONTE",
                                          "PASSAM_A_TER_SIM_NOUTRA_GAVETA", "POR_ORIGEM", "POR_DESTINO",
                                          "CONTRA_O_HUMANO_V1")}, ensure_ascii=False, indent=1))
    return 0 if not mudou else 1


if __name__ == "__main__":
    raise SystemExit(main())
