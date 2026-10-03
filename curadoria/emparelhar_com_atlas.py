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


def url_valida(u: str) -> bool:
    """FALHAR FECHADO: uma URL sem esquema http(s) ou sem dominio com ponto
    nao entra na comparacao nem recebe identidade. Medido no PASSO 5 do
    candidate feeder: sem isto, «nao e um endereco» dava dominio vazio, nao
    casava com nada e seguia para SOURCE_ID novo como se fosse fonte."""
    try:
        p = urlparse((u or "").strip())
    except Exception:
        return False
    return p.scheme in ("http", "https") and "." in p.netloc and " " not in p.netloc


CONTRATOS_DO_CURATOR = RAIZ / "curadoria" / "italy_contracts_curator.json"


def fichas_dos_contratos(caminho: Path | None = None) -> list[dict]:
    """As identidades que o Curator JA contratou, na mesma forma das fichas do
    Atlas — para que uma candidata cujo endereco ja e contrato NAO ganhe um
    segundo numero.

    ⚠️ O ATLAS DO COORDINATOR NAO AS TEM. `ler_atlas()` le a versao dele (185
    fichas) e as 84 do Curator so existem na tabela de contratos e no Atlas do
    disco. Uma descoberta nova que trouxesse `consorziobalsamico.it` outra vez
    casaria com nada no Atlas do coordinator e nasceria IT-T7-0xx pela segunda
    vez. O emparelhamento compara com TUDO o que tem numero.
    """
    p = caminho or CONTRATOS_DO_CURATOR
    if not p.exists():
        return []
    out = []
    for c in json.loads(p.read_text(encoding="utf-8")).get("FONTES", []):
        aq = c.get("ACQUISITION") or {}
        out.append({
            "SOURCE_ID": c["SOURCE_ID"],
            "URL": c.get("CANONICAL_ENTRY_URL") or aq.get("INDEX_URL") or aq.get("FEED_URL") or "",
            "NAME": c.get("NAME", ""), "OWNER": c.get("OWNER", ""),
            "NATIVE_ID": aq.get("CHANNEL_ID") or c.get("SOURCE_NATIVE_ID") or "",
            "TERRITORY": c.get("TERRITORY", ""), "VERDICT": "CONTRATADA_PELO_CURATOR",
        })
    return out


def identidades_conhecidas(do_disco: bool = False,
                           contratos: list[dict] | None = None) -> list[dict]:
    """Atlas + contratos do Curator, sem repetir SOURCE_ID (o Atlas manda)."""
    fichas = ler_atlas(do_disco=do_disco)
    vistos = {f["SOURCE_ID"] for f in fichas}
    for f in (contratos if contratos is not None else fichas_dos_contratos()):
        if f["SOURCE_ID"] not in vistos:
            fichas.append(f)
            vistos.add(f["SOURCE_ID"])
    return fichas


def chave_de_identidade(c: dict) -> str:
    """A chave pela qual duas candidatas sao A MESMA fonte dentro de uma
    corrida: native id > handle normalizado > dominio (fora de plataforma)."""
    nat = (c.get("_NATIVE_ID") or c.get("PLATFORM_NATIVE_ID") or "").strip()
    if nat:
        return "native:" + nat
    h = normalizar(handle_cru(c.get("URL", "")))
    if h:
        return "handle:" + h
    d = dominio(c.get("URL", ""))
    if d and d not in PLATAFORMAS:
        return "dominio:" + d
    return "url:" + (c.get("URL") or "").strip().lower().rstrip("/")


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

    achados, novas, rejeitadas = [], [], []
    vistas: dict[str, str] = {}
    for c in cands:
        # ⚠️ FALHAR FECHADO ANTES DE COMPARAR. URL invalida nao casa com nada
        # e nao ganha numero: sai pelo nome, como REJEITADA.
        if not url_valida(c.get("URL", "")):
            rejeitadas.append({"CANDIDATE_ID": c.get("CANDIDATE_ID"), "URL": c.get("URL"),
                               "PORQUE": "URL_INVALIDA: sem esquema http(s) ou sem dominio"})
            continue
        nat = (c.get("PLATFORM_NATIVE_ID") or "").strip() or native_id_da_prova(c)
        c["_NATIVE_ID"] = nat
        # ⚠️ A MESMA FONTE DUAS VEZES NA MESMA CORRIDA E UMA SO. A segunda
        # ocorrencia nao vira identidade nova: fica ligada a primeira.
        chave = chave_de_identidade(c)
        if chave in vistas:
            rejeitadas.append({"CANDIDATE_ID": c.get("CANDIDATE_ID"), "URL": c.get("URL"),
                               "PORQUE": "DUPLICADA_NA_CORRIDA: mesma identidade que %s (%s)"
                                         % (vistas[chave], chave)})
            continue
        vistas[chave] = c.get("CANDIDATE_ID")
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
    return achados, novas, rejeitadas


def main() -> int:
    car = json.loads((RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json")
                     .read_text(encoding="utf-8"))
    ready = [c for c in car["FONTES"] if c["ONBOARDING_READY"] == "YES"]
    # Atlas do coordinator + o que o Curator ja contratou: TUDO o que tem numero.
    atlas = identidades_conhecidas()

    # ⚠️ CONTROLO POSITIVO OBRIGATORIO, ANTES DE CONFIAR NO RESULTADO.
    # Um par que TEM de casar. Se este falhar, o emparelhador esta avariado e
    # o numero de «fontes novas» e ficcao.
    alvo = next((c for c in ready if "agronotizie" in c["URL"].lower()), None)
    if alvo:
        ok, _, _ = emparelhar([alvo], atlas)
        if not ok:
            print("CONTROLO POSITIVO FALHOU: %s nao casou com IT-T8-001" % alvo["CANDIDATE_ID"])
            print("  -> o emparelhador esta avariado; NAO usar este resultado")
            return 1
        print("controlo positivo OK: %s -> %s (via %s)"
              % (alvo["CANDIDATE_ID"], ok[0]["MATCHED_SOURCE_ID"], ok[0]["VIA"]))

    # ⚠️ QUEM JA TEM NUMERO NESTA LINHA MANTEM-NO PELO CANDIDATE_ID, NAO PELA
    # URL. Sem isto, uma segunda corrida da cadeia veria as 84 contratadas
    # como «ja existem» (casam com o proprio contrato) e o alocador, que so
    # numera SEM_MATCH, deixava-as cair da ALLOCATION — perdendo a ligacao
    # candidata -> numero que a fila, o worker e os lotes leem.
    #
    #     UMA CORRIDA REPETIDA TEM DE DEVOLVER O MESMO RESULTADO, NAO ZERO.
    alocadas = {}
    p_alloc = RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"
    if p_alloc.exists():
        alocadas = {n["CANDIDATE_ID"]: n["SOURCE_ID"]
                    for n in json.loads(p_alloc.read_text(encoding="utf-8"))["NOVAS"]}
    ja = [{"CANDIDATE_ID": c["CANDIDATE_ID"], "URL": c["URL"],
           "MATCHED_SOURCE_ID": alocadas[c["CANDIDATE_ID"]], "VIA": "JA_ALOCADA_NESTA_LINHA",
           "ATLAS_URL": c["URL"], "ATLAS_NAME": c.get("NOME", "")}
          for c in ready if c["CANDIDATE_ID"] in alocadas]
    por_emparelhar = [c for c in ready if c["CANDIDATE_ID"] not in alocadas]

    achados, novas, rejeitadas = emparelhar(por_emparelhar, atlas)
    achados = ja + achados
    saida = {
        "DATASET": "CANDIDATE-TO-SOURCE-MATCH-V1",
        "LEI": ("SOURCE_ID vem do Atlas — nunca do onboarding. Compara-se com o Atlas "
                "E com os contratos do Curator; URL invalida e duplicada na corrida "
                "saem REJEITADAS, nunca viram identidade."),
        "CONTROLO_POSITIVO": "CAND-0187 (@AgroNotizie) deve casar IT-T8-001 (@agronotizietv)",
        "ATLAS_FICHAS": len(atlas),
        "CANDIDATAS_READY": len(ready),
        "JA_TEM_SOURCE_ID": len(achados),
        "JA_ALOCADAS_NESTA_LINHA": len(ja),
        "SEM_SOURCE_ID": len(novas),
        "REJEITADAS": len(rejeitadas),
        "REJEITADAS_DETALHE": rejeitadas,
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
