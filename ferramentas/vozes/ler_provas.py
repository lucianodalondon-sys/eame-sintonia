#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VOZES-EXECUTAR · lê as provas e diz, por voz, se o PAPEL da pessoa está provado: SIM / NAO SEI (NAO só humano).

    PYTHONUTF8=1 py ferramentas/vozes/ler_provas.py --plano=data/derivados/VOZES-AGRONOMOS/PLANO-EXECUCAO.json \\
        --vozes=data/derivados/VOZES-AGRONOMOS/VOZES.json --provas=C:/Users/London1/sintonia-sala-italia/vozes-agronomos \\
        [--sem-sala] [--saida=<json>]   ->  <provas>/LEITURA-DAS-PROVAS.json (por omissao)

Sem rede. Dois passos, por esta ordem:
  0) a DESCRIÇÃO do vídeo que JÁ está no HTML guardado (`shortDescription` do bruto no armazém; Sala só leitura) —
     0 pedidos; `--sem-sala` salta este passo;
  1) a página colhida pelo `colher_papel.py` (os bytes em `<provas>/<ID>/`, conferidos pelo sha256 do recibo).
Regra: SIM só quando o NOME da pessoa (o apelido, pelo menos, sem acentos) e uma palavra de PAPEL aparecem no MESMO
trecho (±200 letras). Tudo o resto é NAO SEI, com o porquê. NAO — «a prova diz outro papel» — nunca é automático:
fica o campo LEITURA_HUMANA para quem ler os trechos.
"""
from __future__ import annotations

import hashlib
import html
import importlib.machinery
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

PALAVRAS_DE_PAPEL = ("agronom", "docente", "professor", "prof.", "ricercat", "tecnic", "responsabile", "direttor",
                     "dott.", "dottor", "fitopatolog", "universit", "dipartimento", "consulente", "esperto", "presidente",
                     "enolog", "funzionari", "coordinator", "researcher", "lecturer")
JANELA = 200


def dobrar(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def texto_visivel(b: bytes) -> str:
    s = b.decode("utf-8", "replace")
    s = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s))


def descricao_youtube(b: bytes) -> str:
    m = re.search(rb'"shortDescription":"(.*?)(?<!\\)","', b, re.S)
    if not m:
        return ""
    try:
        return json.loads(b'"' + m.group(1) + b'"')
    except ValueError:
        return m.group(1).decode("utf-8", "replace")


def julgar(pessoa: str, texto: str) -> dict:
    """SIM (nome + papel no mesmo trecho) ou NAO SEI, com o trecho que decidiu."""
    if not pessoa or pessoa.startswith("NAO SEI"):
        return {"PAPEL_PROVADO": "NAO SEI", "PORQUE": "serie sem nome de pessoa: a pessoa le-se a mao nos trechos"}
    t = dobrar(texto)
    apelido = dobrar(pessoa.split()[-1])
    posicoes = [m.start() for m in re.finditer(r"(?<![a-z])%s(?![a-z])" % re.escape(apelido), t)]
    if not posicoes:
        return {"PAPEL_PROVADO": "NAO SEI", "PORQUE": "o nome (%s) nao aparece" % pessoa.split()[-1]}
    for pos in posicoes:
        trecho = t[max(0, pos - JANELA): pos + JANELA]
        achou = [p for p in PALAVRAS_DE_PAPEL if p in trecho]
        if achou:
            return {"PAPEL_PROVADO": "SIM", "PORQUE": "nome e papel no mesmo trecho: %s" % ", ".join(achou[:3]),
                    "TRECHO": texto[max(0, pos - JANELA): pos + JANELA]}
    return {"PAPEL_PROVADO": "NAO SEI", "PORQUE": "o nome aparece %d vez(es), sem palavra de papel perto" % len(posicoes),
            "TRECHO": texto[max(0, posicoes[0] - JANELA): posicoes[0] + JANELA]}


def ler_passo0(vozes: dict, consultar, sep, armazem: Path) -> dict:
    fora = {}
    for f in vozes["FICHAS"]:
        v = f.get("VIDEO_GUARDADO")
        if not v:
            continue
        l = consultar("select storage_path from public.raw_asset where sha256 like '%s%%' limit 1" % v["SHA256_BRUTO"])
        p = armazem / l[0] if l else None
        if not p or not p.exists():
            fora[f["ID"]] = {"PAPEL_PROVADO": "NAO SEI", "PORQUE": "bruto do video nao esta nesta maquina"}
            continue
        d = descricao_youtube(p.read_bytes())
        # SO a descricao: o titulo e o que se quer provar (julga-lo com ele seria prova circular)
        j = julgar(f["PESSOA"], d) if d else {"PAPEL_PROVADO": "NAO SEI",
                                                                     "PORQUE": "o HTML guardado nao traz a descricao"}
        j["DESCRICAO"] = d[:600]
        fora[f["ID"]] = j
    return fora


def ler_passo1(plano: dict, provas: Path) -> dict:
    fora = {}
    recibos = {}
    for r in sorted(provas.glob("RECIBO-RONDA-*.json")):
        for c in json.loads(r.read_text("utf-8"))["COLHIDAS"]:
            recibos[c["ID"]] = c
    pessoas = {f["ID"]: f.get("PESSOA") for f in plano["FICHAS"]}
    for fid, c in recibos.items():
        alvo = next((x for x in c["PROVAS"] if x["PAPEL"] == "ALVO"), None)
        if not alvo:
            fora[fid] = {"PAPEL_PROVADO": "NAO SEI", "PORQUE": c.get("PORQUE_PAROU") or "sem pagina colhida"}
            continue
        b = Path(alvo["BYTES_EM"]).read_bytes()
        if hashlib.sha256(b).hexdigest() != alvo["SHA256"]:
            fora[fid] = {"PAPEL_PROVADO": "NAO SEI", "PORQUE": "bytes nao batem com o sha256 do recibo"}
            continue
        j = julgar(pessoas.get(fid) or "", texto_visivel(b))
        j["URL"] = alvo["URL"]
        fora[fid] = j
    return fora


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    plano = json.loads(Path(a["plano"]).read_text("utf-8"))
    vozes = json.loads(Path(a["vozes"]).read_text("utf-8"))
    provas = Path(a["provas"])
    p0 = {}
    if "--sem-sala" not in argv:
        LS = importlib.machinery.SourceFileLoader("ler_sala", str(Path(a["vozes"]).parent / "ler_sala.py.txt")).load_module()
        p0 = ler_passo0(vozes, LS.consultar, LS.SEP, Path(os.path.expanduser("~/sintonia-sala-italia/armazem")))
    p1 = ler_passo1(plano, provas) if provas.exists() else {}
    linhas = []
    for f in plano["FICHAS"]:
        fid = f["ID"]
        a0, a1 = p0.get(fid), p1.get(fid)
        if f["ESTADO"] == "JA_PROVADO":
            final = "SIM"
        elif "SIM" in ((a0 or {}).get("PAPEL_PROVADO"), (a1 or {}).get("PAPEL_PROVADO")):
            final = "SIM"
        else:
            final = "NAO SEI"
        linhas.append({"ID": fid, "PESSOA": f.get("PESSOA"), "PAPEL_NO_TITULO": f.get("PAPEL_NO_TITULO"),
                       "ESTADO_NO_PLANO": f["ESTADO"], "PASSO0_DESCRICAO": a0, "PASSO1_PAGINA": a1,
                       "PAPEL_PROVADO": final, "LEITURA_HUMANA": None})
    out = {"DATASET": "VOZES-LEITURA-DAS-PROVAS", "CONTA": {k: sum(1 for x in linhas if x["PAPEL_PROVADO"] == k)
                                                            for k in ("SIM", "NAO SEI")}, "VOZES": linhas}
    destino = Path(a["saida"]) if a.get("saida") else provas / "LEITURA-DAS-PROVAS.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out["CONTA"]), "->", destino)
    for x in linhas:
        print("%-4s %-8s %-22s %s" % (x["ID"], x["PAPEL_PROVADO"], (x["PESSOA"] or "")[:22],
                                      ((x["PASSO0_DESCRICAO"] or {}).get("PORQUE") or "")[:70]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
