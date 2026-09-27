"""SOC-ONDA2 · PASSO 5 — o plano (SÓ PLANO) de uma onda social pelo orquestrador existente.

    py curadoria/plano_onda_social.py [--json SAIDA]

Não corre nada, não bate à rede, não escreve em livro. Para cada fonte social do
livro (contrato `SCRAP_FASE`) responde, pela ordem da casa (D28: o disparo é sempre
o orquestrador → executor; nada paralelo):

  1. o PORTÃO deixa-a entrar na coorte? (`collection_gate.avaliar`)
  2. o PEDIDO, montado EM PROCESSO (`pedido.Pedido`), resolve para `scrap-colheita`?
     — a frase da linha de comando junta os valores de `--filtro` ao texto e um
     endereço com «agricultural» virou T1 (medido no canário, IT-T5-163). A onda
     monta o pedido por dentro; o comando fica escrito só para quem o quiser ler.
  3. o executor CONSOME todos os filtros do contrato? (`receitas.filtros_consumidos`)
  4. `orquestrador.correr(pedido, so_plano=True)` devolve PLANO?

E escreve os buracos que o plano não fecha (onde a chave vive, a regra do nome do
documento na tabela do coletor), cada um com o dono.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "curadoria"))
import _gavetas  # noqa: E402,F401

import collection_gate as GATE   # noqa: E402
import lifecycle as LC           # noqa: E402
import receitas as REC           # noqa: E402
from pedido import Pedido        # noqa: E402

CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"
EXECUTOR = "scrap-colheita"

BURACOS = {
    "CHAVE_YOUTUBE_SO_NO_GITHUB": (
        "a fase canal-youtube (API oficial) precisa de YOUTUBE_DATA_API_KEY, que so existe no "
        "GitHub Actions; sintonia-scrap.yml (fases canonicas) nao a injecta — a porta local "
        "responde CREDENTIAL_MISSING", "coordenador + engenheiro do Scrap (workflow)"),
    "DOCUMENT_ID_RULE_FORA_DA_TABELA": (
        "o Scrap le a regra do nome do documento em regras/italy_contracts.mjs (tabela do "
        "coletor); os contratos sociais do Curator nao estao la — o item entra com "
        "DOCUMENT_ID = NAO SEI (a identidade da plataforma, NATIVE_ID, vem inteira)",
        "CUR-PRONTA / coordenador (ponte livro do Curator -> tabela do coletor)"),
    "FRASE_DA_CLI_POLUI_O_ALVO": (
        "orquestrador.py junta os valores de --filtro a frase; um endereco com «agricultural» "
        "resolveu T1 em vez de T5. A onda monta o Pedido em processo",
        "dono do orquestrador (so documentado; esta onda contorna montando o Pedido)"),
}


def fontes_sociais(contratos: dict) -> list[str]:
    return sorted(s for s, c in contratos.items()
                  if (c.get("ACQUISITION") or {}).get("STRATEGY") == "SCRAP_FASE")


# ── C2 (FREIO-SOCIAL, 26/09): O TETO DO PEDIDO NA ONDA NAO E O DO CONTRATO ──────
# O contrato LinkedIn escreve `teto: 2` (quantos videos por conta). Com 2 contas numa
# onda isso da 2 x (1 pagina + 2 posts) = 6 pedidos a linkedin.com — passa o teto D38.
# A onda pede `teto=1` por conta (2 x 2 = 4). O contrato nao muda: e a onda que decide
# quanto gasta, e escreve-o no pedido.
TETO_LINKEDIN_NA_ONDA = 1
CONTAS_LINKEDIN_POR_ONDA = 2
TETO_D38 = 5


def pedido_de(c: dict, *, teto_linkedin: int | None = TETO_LINKEDIN_NA_ONDA) -> Pedido:
    aq = c["ACQUISITION"]
    f = {"fase": aq["FASE"], "fonte": c["SOURCE_ID"], "pais": "IT", "universo": c["TERRITORY"]}
    f.update({k: str(v) for k, v in (aq.get("FILTROS") or {}).items()})
    if aq.get("FASE") == "video-linkedin" and teto_linkedin is not None:
        f["teto"] = str(teto_linkedin)
    return Pedido(alvo=c["TERRITORY"], filtros=f)


def previsto_linkedin(teto: int) -> dict:
    """Pedidos por conta, LIDOS no codigo (adaptador_linkedin.video_da_pagina_publica):
    1 pagina + ate `teto` posts a linkedin.com; ate `teto` MP4 + ate `teto` legendas a licdn.com."""
    return {"linkedin.com": 1 + teto, "licdn.com": 2 * teto}


#: MEDIDO offline (SOCIAL-QUALIFICAR): 3 a youtube.com + 1 a googlevideo.com por video ate ~9,7 MiB (D41: um orcamento).
PREVISTO_YOUTUBE_VIDEO_CURTO = {"youtube.com": 4}


def rodadas(linhas: list[dict], *, teto_linkedin: int = TETO_LINKEDIN_NA_ONDA,
            contas_li: int = CONTAS_LINKEDIN_POR_ONDA) -> list[dict]:
    """As ondas da passagem A: ate `contas_li` contas LinkedIn + 1 canal YouTube por onda
    (dominios diferentes). Cada onda leva o PREVISTO por dominio e diz se cabe no teto D38.
    Previsto e o maximo que o codigo pode pedir; o freio (`coleta/teto_da_onda.py`) trava o resto."""
    li = [l["SOURCE_ID"] for l in linhas if l.get("NA_ONDA") and l.get("FASE") == "video-linkedin"]
    yt = [l["SOURCE_ID"] for l in linhas if l.get("NA_ONDA") and l.get("FASE") in ("canal-youtube", "audio-youtube")]
    n = max((len(li) + contas_li - 1) // contas_li, len(yt))
    fora = []
    for i in range(n):
        contas = li[i * contas_li:(i + 1) * contas_li]
        canal = yt[i:i + 1]
        prev = {}
        for _ in contas:
            for d, k in previsto_linkedin(teto_linkedin).items():
                prev[d] = prev.get(d, 0) + k
        for _ in canal:
            for d, k in PREVISTO_YOUTUBE_VIDEO_CURTO.items():
                prev[d] = prev.get(d, 0) + k
        fora.append({"ONDA": i + 1, "LINKEDIN": contas, "YOUTUBE": canal, "PREVISTO_POR_DOMINIO": prev,
                     "CABE_NO_TETO": all(v <= TETO_D38 for v in prev.values())})
    return fora


def plano() -> dict:
    import orquestrador as ORQ
    contratos = {c["SOURCE_ID"]: c for c in json.loads(CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}
    ctx = GATE._contexto()
    linhas = []
    for s in fontes_sociais(contratos):
        c = contratos[s]
        aq = c["ACQUISITION"]
        g = GATE.avaliar(s, **ctx)
        falta, executor, sobra, status = [], None, [], None
        if not g["COLLECTION_ELIGIBLE"]:
            falta.append("PORTAO:%s" % g["MOTIVO"])
        try:
            p = pedido_de(c)
            pl = REC.resolver(p)
            e = pl.executores[0] if pl.executores else {}
            executor = e.get("id")
            sobra = sorted(set(p.filtros) - REC.filtros_consumidos(e) - {"pais", "universo"}) if e else []
            status = ORQ.correr(p, so_plano=True)["STATUS"]
            if executor != EXECUTOR:
                falta.append("EXECUTOR:%s" % executor)
            if sobra:
                falta.append("FILTRO_NAO_CONSUMIDO:%s" % ",".join(sobra))
            if p.alvo != c["TERRITORY"]:
                falta.append("ALVO:%s" % p.alvo)
        except Exception as ex:                                   # noqa: BLE001
            falta.append("PEDIDO_RECUSADO:%s:%s" % (type(ex).__name__, str(ex)[:80]))
        buracos = []
        if aq.get("FASE") == "canal-youtube":
            buracos.append("CHAVE_YOUTUBE_SO_NO_GITHUB")
        buracos.append("DOCUMENT_ID_RULE_FORA_DA_TABELA")
        linhas.append({"SOURCE_ID": s, "TERRITORY": c["TERRITORY"], "FASE": aq.get("FASE"),
                       "ESTADO": LC.estado_de(s), "PORTAO": g["MOTIVO"], "READY_RULE": g["READY_RULE"],
                       "EXECUTOR": executor, "PLANO": status, "FALTA": falta, "BURACOS": buracos,
                       "NA_ONDA": not falta,
                       "PEDIDO_EM_PROCESSO": "Pedido(alvo=%r, filtros=%r)" % (
                           c["TERRITORY"], pedido_de(c).filtros if not any(
                               f.startswith("PEDIDO_RECUSADO") for f in falta) else None)})
    na_onda = [l for l in linhas if l["NA_ONDA"]]
    return {"DATASET": "SOC-ONDA2-PLANO-ONDA-SOCIAL-V1", "SO_PLANO": True,
            "FONTES_SOCIAIS_NO_LIVRO": len(linhas),
            "NA_ONDA": len(na_onda),
            "NA_ONDA_POR_FASE": dict(Counter(l["FASE"] for l in na_onda)),
            "FORA_POR_MOTIVO": dict(Counter(f.split(":")[0] + ":" + f.split(":")[1]
                                            for l in linhas for f in l["FALTA"])),
            "BURACOS": {k: {"O_QUE": v[0], "DONO": v[1]} for k, v in BURACOS.items()},
            "TETO_LINKEDIN_NA_ONDA": TETO_LINKEDIN_NA_ONDA,
            "RODADAS": rodadas(linhas),
            "LINHAS": linhas}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    r = plano()
    print(json.dumps({k: v for k, v in r.items() if k not in ("LINHAS", "BURACOS")}, ensure_ascii=False, indent=1))
    for l in r["LINHAS"]:
        if l["NA_ONDA"]:
            print("  NA ONDA  %-11s %-4s %-15s -> %s (%s)" % (l["SOURCE_ID"], l["TERRITORY"], l["FASE"],
                                                            l["EXECUTOR"], l["PLANO"]))
    if a.json:
        Path(a.json).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
