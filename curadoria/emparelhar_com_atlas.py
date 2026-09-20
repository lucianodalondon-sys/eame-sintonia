#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EMPARELHAR candidata com SOURCE_ID do Atlas — antes de criar identidade nova.

    SOURCE_ID VEM DO ATLAS. NUNCA DAQUI.
    (lei escrita em regras/italy_contracts_onboarded.json)

Criar um SOURCE_ID para uma fonte que ja tem um e o pior erro possivel nesta
casa: parte a identidade em duas, e tudo o que se coletar sob o numero novo
fica orfao do historico que vive sob o numero velho.

⚠️ POR QUE ISTO NAO E UM `==` ENTRE URLs.
Medido, com controlo positivo: o Atlas tem `IT-T8-001` em
`youtube.com/@agronotizietv` e a fila tem `CAND-0187` em
`youtube.com/@AgroNotizie`. E A MESMA FONTE. Um emparelhador literal
devolveu «0 de 98 ja existem» — um zero limpo, redondo e falso, que teria
criado 98 identidades novas, uma delas duplicando IT-T8-001.

    UM ZERO SUSPEITO MERECE UM CONTROLO POSITIVO ANTES DE VIRAR NUMERO.

Regras de comparacao, da mais forte para a mais fraca:

  1. PLATFORM_NATIVE_ID   channel_id do YouTube — identidade nativa, nao texto
  2. HANDLE NORMALIZADO   minusculas, sem pontuacao, sem sufixos de plataforma
                          (tv, official, ufficiale, channel, it)
  3. DOMINIO              so para fontes NAO-plataforma: em youtube.com o
                          dominio e da plataforma, nao da fonte (COL-LAW-034)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
COORD = "claude/contract-provenance-cutover-v1"

# ⚠️ EM PLATAFORMA, O DOMINIO NAO IDENTIFICA A FONTE (COL-LAW-034).
# Sem esta lista, as 60 do YouTube colapsariam numa fonte so — o defeito
# exacto que ja foi corrigido na missao 02.
PLATAFORMAS = {"youtube.com", "youtu.be", "facebook.com", "fb.com",
               "linkedin.com", "instagram.com", "twitter.com", "x.com"}

# sufixos que o mesmo dono poe (ou nao) no handle sem mudar de identidade
_SUFIXOS = re.compile(r"(tv|official|ufficiale|oficial|channel|canale|it|italia|"
                      r"agricoltura|agro|web|online|page|pagina)$")


def _git(path: str) -> str:
    return subprocess.run(["git", "show", "%s:%s" % (COORD, path)],
                          capture_output=True, text=True,
                          encoding="utf-8", cwd=str(RAIZ)).stdout


def dominio(u: str) -> str:
    try:
        return urlparse(u).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def handle_cru(u: str) -> str:
    m = re.search(r"(?:@|/c/|/user/|/channel/|/company/|facebook\.com/)([^/?#]+)",
                  u or "")
    return m.group(1) if m else ""


def normalizar(h: str) -> str:
    """`@agronotizietv` e `@AgroNotizie` tem de dar a mesma chave."""
    h = re.sub(r"[^a-z0-9]+", "", (h or "").lower())
    anterior = None
    while h != anterior:            # 'agronotizietv' -> 'agronotizie'
        anterior = h
        h = _SUFIXOS.sub("", h)
    return h


def ler_atlas(do_disco: bool = False) -> list[dict]:
    """Uma ficha do Atlas = um bloco ``` com CHAVE: valor.

    ⚠️ POR OMISSAO LE A VERSAO DO COORDINATOR, NAO O DISCO. E deliberado: o
    emparelhamento tem de comparar com o Atlas DELE, que e o estado que vai
    valer na integracao. Ler o disco compararia com o meu proprio trabalho.

    Mas isso tem um preco medido: depois de escrever 84 fichas no disco, um
    `ler_atlas()` sem argumento continuou a devolver 185 e imprimiu
    «Atlas antes 185 / Atlas depois 185» — parecia que a escrita falhara. Nao
    falhara: o disco tinha 269, e o scanner canonico confirmou 297 fontes.

        UM LEITOR QUE OLHA PARA O SITIO ERRADO NAO DIZ «NAO SEI»:
        DIZ UM NUMERO, COM CONFIANCA.

    `do_disco=True` para conferir o que esta escrito aqui.
    """
    if do_disco:
        p = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
        txt = p.read_text(encoding="utf-8") if p.exists() else ""
    else:
        txt = _git("docs/fontes/ATLAS-DE-FONTES-EAME.md")
    fichas = []
    for sid, corpo in re.findall(r"SOURCE_ID:\s*(\S+)(.*?)(?=SOURCE_ID:|\Z)", txt, re.S):
        def campo(nome):
            m = re.search(r"^%s:\s*(.+)$" % nome, corpo, re.M)
            return m.group(1).strip() if m else ""
        fichas.append({
            "SOURCE_ID": sid, "URL": campo("URL"),
            "NAME": campo("SOURCE_NAME"), "OWNER": campo("SOURCE_OWNER"),
            "NATIVE_ID": campo("PLATFORM_NATIVE_ID"),
            "TERRITORY": campo("TERRITORY"), "VERDICT": campo("VERDICT")[:60],
        })
    return fichas


def native_id_da_prova(c: dict) -> str:
    """O channel_id do YouTube vive no feed guardado, nao na ficha.

    ⚠️ ESTA E A COMPARACAO MAIS FORTE QUE EXISTE PARA UM CANAL. O handle muda
    (`@AgroNotizie` hoje, `@agronotizietv` amanha) e o Atlas guarda um dos dois.
    O `channel_id` (`UC...`) e atribuido pela plataforma e nao muda nunca —
    e e exactamente o que o Atlas grava em PLATFORM_NATIVE_ID.

    Ler a prova ja capturada em vez de ir a rede: o feed esta em disco desde a
    missao 02.
    """
    p = c.get("CANONICAL_EXAMPLE") or ""
    if not p or p.startswith("http"):
        return ""
    f = RAIZ / p
    if not f.exists():
        return ""
    try:
        b = f.read_bytes()[:200000]
    except OSError:
        return ""
    m = re.search(rb"(?:channelId|channel_id)[\"'=>:\s]{1,4}(UC[\w-]{20,26})", b)
    if not m:
        m = re.search(rb"(UC[\w-]{22})", b)
    return m.group(1).decode() if m else ""


def emparelhar(cands: list[dict], atlas: list[dict]) -> tuple[list, list]:
    por_native, por_handle, por_dom = {}, {}, {}
    for a in atlas:
        if a["NATIVE_ID"] and a["NATIVE_ID"] not in ("NAO SEI", "-"):
            por_native.setdefault(a["NATIVE_ID"].strip(), a)
        h = normalizar(handle_cru(a["URL"]))
        if h:
            por_handle.setdefault(h, a)
        d = dominio(a["URL"])
        if d and d not in PLATAFORMAS:
            por_dom.setdefault(d, a)

    achados, novas = [], []
    for c in cands:
        nat = (c.get("PLATFORM_NATIVE_ID") or "").strip() or native_id_da_prova(c)
        c["_NATIVE_ID"] = nat
        a = por_native.get(nat) if nat else None
        via = "PLATFORM_NATIVE_ID"
        if not a:
            h = normalizar(handle_cru(c["URL"]))
            a = por_handle.get(h) if h else None
            via = "HANDLE_NORMALIZADO"
        if not a:
            d = dominio(c["URL"])
            if d and d not in PLATAFORMAS:
                a = por_dom.get(d)
                via = "DOMINIO"
        if a:
            achados.append({"CANDIDATE_ID": c["CANDIDATE_ID"], "URL": c["URL"],
                            "MATCHED_SOURCE_ID": a["SOURCE_ID"], "VIA": via,
                            "ATLAS_URL": a["URL"], "ATLAS_NAME": a["NAME"]})
        else:
            novas.append(c)
    return achados, novas


def main() -> int:
    car = json.loads((RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json")
                     .read_text(encoding="utf-8"))
    ready = [c for c in car["FONTES"] if c["ONBOARDING_READY"] == "YES"]
    atlas = ler_atlas()

    # ⚠️ CONTROLO POSITIVO OBRIGATORIO, ANTES DE CONFIAR NO RESULTADO.
    # Um par que TEM de casar. Se este falhar, o emparelhador esta avariado e
    # o numero de «fontes novas» e ficcao.
    alvo = next((c for c in ready if "agronotizie" in c["URL"].lower()), None)
    if alvo:
        ok, _ = emparelhar([alvo], atlas)
        if not ok:
            print("CONTROLO POSITIVO FALHOU: %s nao casou com IT-T8-001" % alvo["CANDIDATE_ID"])
            print("  -> o emparelhador esta avariado; NAO usar este resultado")
            return 1
        print("controlo positivo OK: %s -> %s (via %s)"
              % (alvo["CANDIDATE_ID"], ok[0]["MATCHED_SOURCE_ID"], ok[0]["VIA"]))

    achados, novas = emparelhar(ready, atlas)
    saida = {
        "DATASET": "CANDIDATE-TO-SOURCE-MATCH-V1",
        "LEI": "SOURCE_ID vem do Atlas — nunca do onboarding.",
        "CONTROLO_POSITIVO": "CAND-0187 (@AgroNotizie) deve casar IT-T8-001 (@agronotizietv)",
        "ATLAS_FICHAS": len(atlas),
        "CANDIDATAS_READY": len(ready),
        "JA_TEM_SOURCE_ID": len(achados),
        "SEM_SOURCE_ID": len(novas),
        "MATCHES": achados,
        "SEM_MATCH": [{"CANDIDATE_ID": c["CANDIDATE_ID"], "URL": c["URL"],
                       "NOME": c["NOME"], "FAMILY": c["FAMILY"]} for c in novas],
    }
    p = RAIZ / "curadoria" / "CANDIDATE-TO-SOURCE-MATCH-V1.json"
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("Atlas fichas       %d" % len(atlas))
    print("candidatas READY   %d" % len(ready))
    print("JA TEM SOURCE_ID   %d" % len(achados))
    print("SEM SOURCE_ID      %d" % len(novas))
    from collections import Counter
    print("por via            %s" % dict(Counter(a["VIA"] for a in achados)))
    print("escrito: %s" % p.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
