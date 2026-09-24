#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T2-REGUA · INVENTARIO DO ACERVO PARA O GABARITO T2 — SEM REDE.

    py scripts/regua_t2/inventariar_t2.py [--saida=DIR]

Junta os textos que JA estao no acervo (ver PROTOCOLO-GABARITO-T2.md, «De onde vem
os textos»), extrai-os com o MESMO extractor da porta, e guarda um por sha256 do
texto normalizado em `<saida>/textos/<sha16>.txt` (fora do Git). Escreve
`<saida>/INVENTARIO.json` com a origem de cada um e, quando existir, o rotulo que
ele ja tinha nos gabaritos V2/V3.

Nao julga nada e nao escreve rotulo novo: isso e o passo seguinte, a mao.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ)]
from coleta import executor_texto_de_html as HTMLX  # noqa: E402
from coleta import executor_texto_de_pdf as PDFX    # noqa: E402

CASA = Path(os.environ.get("USERPROFILE", str(Path.home())))
GAB = CASA / "sintonia-gabarito"
ARMAZEM = CASA / "sintonia-sala-italia" / "armazem" / "XX"


def _arg(nome, omissao):
    return next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--%s=" % nome)), omissao)


def normalizar(t: str) -> str:
    return re.sub(r"\s+", " ", t or "").strip()


def extrair(corpo: bytes) -> tuple[str, str]:
    if corpo[:5] == b"%PDF-":
        with tempfile.TemporaryDirectory() as d:
            f = Path(d, "x.pdf")
            f.write_bytes(corpo)
            t, estado, _e, _m = PDFX.extrair(f)
        return t or "", "PDF:" + str(estado)
    if corpo.lstrip()[:1] in (b"{", b"["):
        return "", "JSON:SEM_EXTRACTOR"
    t, estado, _e, _m = HTMLX.extrair(corpo, "text/html")
    return t or "", "HTML:" + str(estado)


def origens():
    """(origem, source_id, url, caminho, rotulo_antigo) — so ficheiros que existem."""
    for v in ("V2", "V3"):
        g = json.load(open(RAIZ / "curadoria" / ("GABARITO-T2-T12-%s.json" % v), encoding="utf-8"))
        for it in g["ITENS"]:
            f = it.get("FICHEIRO_FORA_DO_GIT")
            if not f or not Path(f).is_file():
                continue
            rot = None
            if it.get("UTILIZAVEL"):
                rot = {k: it.get(k) for k in ("UNIVERSO_DO_CONTEUDO", "UNIVERSE_MATCH",
                                               "SINTONIA_RELEVANT", "ACTION", "PORQUE")}
                rot["DE"] = "GABARITO-T2-T12-%s#%s" % (v, it.get("N"))
            yield ("GABARITO-" + v, it["SOURCE_ID"], it.get("URL"), Path(f), rot)
    cat = json.load(open(RAIZ / "curadoria" / "CATALOGO-PROVA-V1.json", encoding="utf-8"))
    for it in cat.get("PAGINAS", []):
        f = it.get("FICHEIRO_FORA_DO_GIT")
        if f and Path(f).is_file():
            yield ("CATALOGO-PROVA-V1", it["SOURCE_ID"], it.get("URL"), Path(f), None)
    for p in sorted((RAIZ / "data" / "collection-store" / "italy").rglob("*")):
        if p.is_file() and p.suffix.lower() in (".pdf", ".html", ".htm"):
            sid = p.relative_to(RAIZ / "data" / "collection-store" / "italy").parts[0]
            yield ("GIT-COLLECTION-STORE", sid, None, p, None)
    if ARMAZEM.is_dir():
        for d in sorted(ARMAZEM.iterdir()):
            if not re.match(r"it-t(2|12)-\d+$", d.name):
                continue
            for p in sorted(d.rglob("*")):
                if p.is_file():
                    yield ("ARMAZEM-OPERACIONAL", d.name.upper(), None, p, None)


def main() -> int:
    saida = Path(_arg("saida", str(GAB / "REGUA-T2-V1")))
    (saida / "textos").mkdir(parents=True, exist_ok=True)
    vistos, itens, curtos, sem_texto = {}, [], 0, 0
    for origem, sid, url, caminho, rot in origens():
        corpo = caminho.read_bytes()
        texto, extr = extrair(corpo)
        norm = normalizar(texto)
        if len(norm.replace(" ", "")) < 200:
            sem_texto += 1 if not norm else 0
            curtos += 1 if norm else 0
            continue
        h = hashlib.sha256(norm.encode("utf-8")).hexdigest()
        if h in vistos:
            vistos[h]["TAMBEM_EM"].append({"ORIGEM": origem, "SOURCE_ID": sid, "CAMINHO": str(caminho)})
            if rot and not vistos[h].get("ROTULO_ANTIGO"):
                vistos[h]["ROTULO_ANTIGO"] = rot
            continue
        f = saida / "textos" / (h[:16] + ".txt")
        f.write_bytes(norm.encode("utf-8"))
        reg = {"TEXTO_ID": h[:16], "TEXTO_SHA256": h, "ORIGEM": origem, "SOURCE_ID": sid,
               "URL": url, "CAMINHO": str(caminho),
               "BYTES_SHA256": hashlib.sha256(corpo).hexdigest(), "EXTRACAO": extr,
               "NON_WHITESPACE_CHARACTERS": len(norm.replace(" ", "")),
               "ROTULO_ANTIGO": rot, "TAMBEM_EM": []}
        vistos[h] = reg
        itens.append(reg)
    out = {"DATASET": "INVENTARIO-REGUA-T2-V1", "SEM_REDE": True,
           "TEXTOS_DISTINTOS": len(itens), "DESCARTADOS_CURTOS_<200": curtos,
           "DESCARTADOS_SEM_TEXTO": sem_texto, "ITENS": itens}
    (saida / "INVENTARIO.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "ITENS"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
