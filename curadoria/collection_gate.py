#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PORTAO DE ADMISSAO DA COLLECTION — o unico sitio onde a regra vive.

    COLLECTION_ELIGIBLE = READY_CURRENT
                          AND NOT HUMAN_REVIEW_REQUIRED
                          AND NOT RETIRADA_POR_DECISAO (D9, marca no contrato)
                          AND NOT (POLICY_BLOCK | CAPABILITY_BLOCK | RETRY
                                   | UNKNOWN | DEGRADED | NOT_READY)

    READY_LEGACY NAO ENTRA POR OMISSAO.

PORQUE ISTO EXISTE
------------------
`interface_collection.ready_sources()` entregava a lista pela linha:

    if estado != LC.READY_FOR_COLLECTION: continue

Isso deixava entrar QUALQUER READY. Medido no livro canonico
(`LIFECYCLE-LEDGER-V1.json`, 278 fontes): 87 READY, dos quais 77 sao
`READY_LEGACY` — promovidas pela regua antiga, «a rota resolve e traz HTML».
A funcao ja sabia a regua: escrevia `READY_RULE` no proprio output. Escrevia
e nao filtrava. Uma etiqueta que ninguem le nao e um portao.

    READY E UMA CONSEQUENCIA, NUNCA UM CARIMBO — e elegivel para a
    Collection e uma consequencia da regua, nunca do estado sozinho.

UM DONO SO
----------
A regra nao se repete. Quem precisa de saber se uma fonte entra chama
`eligible_for_collection()` ou `avaliar()`. Nao ha um segundo `if
READY_CURRENT` nesta casa, e nao ha lista de IDs autorizados: uma lista fixa
seria outra vez um carimbo, e envelhecia em silencio no dia seguinte.

    PROIBIDO `ALLOWED_IDS = [...]`. As fontes elegiveis RESULTAM da regra.
    `test_collection_gate.py` le o texto deste ficheiro e reprova se aparecer
    um SOURCE_ID literal.

O QUE ESTE MODULO NAO FAZ
-------------------------
Nao promove, nao despromove, nao escreve no livro, nao vai a rede e nao
arranca coleta nenhuma. So responde a uma pergunta, lendo o livro canonico no
instante da pergunta.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import lifecycle as LC    # noqa: E402
import ready_split as RS  # noqa: E402

CONTRATO = "COLLECTION_INTAKE_GATE/v1"
SAIDA = RAIZ / "curadoria" / "COLLECTION-INTAKE-V1.json"

# Os motivos de recusa. Escritos por extenso porque «nao elegivel» sem motivo
# e a mesma coisa que nao medir.
NUNCA_PROMOVIDA = "NUNCA_PROMOVIDA"
ESTADO_NAO_READY = "ESTADO_NAO_READY"
READY_LEGACY = "READY_LEGACY"
HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
# D9 (23/09, bot Luciano por delegacao do dono): o pacote G1 marca no contrato
# do Curator `ESTADO_CATALOGO = RETIRADA_POR_DECISAO`. Uma fonte retirada do
# universo nao entra, qualquer que seja o estado ou a regua — e o motivo diz
# que foi DECISAO, nao defeito. A marca le-se do livro de contratos corrente
# (o mesmo que a regua le), nunca do git.
RETIRADA_POR_DECISAO = "RETIRADA_POR_DECISAO"
ELEGIVEL = "ELIGIBLE"


# ---------------------------------------------------------------------------
# REVISAO HUMANA — a heuristica DECLARADA, que nao muda o estado.
#
# O endereco do item aberto na evidencia da promocao tem menos de 4 palavras e
# nenhum digito (ex.: /lavora-con-noi, /articoli-e-pubblicazioni/). Isso cheira
# a SECCAO, nao a item publicado. Nao condena a fonte — tira-a da colheita
# automatica e pede olho humano.
#
# Esta funcao e o DONO desta regra. `reconciliar_livros._item_parece_seccao`
# delega aqui; nao ha duas copias da heuristica.
# ---------------------------------------------------------------------------
PALAVRAS_MINIMAS_NO_ULTIMO_SEGMENTO = 4


def revisao_humana_do_url(url: str) -> str | None:
    """`None` = nao pede olho humano. Texto = pede, e diz porque."""
    slug = [s for s in re.sub(r"^https?://[^/]+", "", url or "").split("/") if s]
    if not slug:
        return None
    ultimo = slug[-1]
    if (len(ultimo.split("-")) < PALAVRAS_MINIMAS_NO_ULTIMO_SEGMENTO
            and not any(ch.isdigit() for ch in ultimo)):
        return ("ITEM_PARECE_SECCAO: %s — confirmar a olho que e um item e nao "
                "uma seccao" % url)
    return None


def url_do_item_aberto(source_id: str, *, livro: dict | None = None,
                       evidencias: dict | None = None) -> str:
    """O endereco que a evidencia da promocao diz ter aberto. '' = nao ha."""
    promo = RS.ultima_promocao(source_id, livro)
    ev = (evidencias if evidencias is not None
          else RS._evidencias()).get((promo or {}).get("EVIDENCE_REF") or "") or {}
    return ((ev.get("DADOS") or {}).get("ITEM_ABERTO") or {}).get("URL") or ""


def revisao_humana_de(source_id: str, *, livro: dict | None = None,
                      evidencias: dict | None = None) -> str | None:
    return revisao_humana_do_url(
        url_do_item_aberto(source_id, livro=livro, evidencias=evidencias))


# ---------------------------------------------------------------------------
# A LEI
# ---------------------------------------------------------------------------
def avaliar(source_id: str, *, livro: dict | None = None,
            evidencias: dict | None = None, contratos: dict | None = None) -> dict:
    """O veredito completo de UMA fonte, derivado do livro canonico agora.

    Devolve sempre os mesmos campos — tambem quando recusa, porque quem recusa
    sem dizer o motivo obriga o proximo a adivinhar.
    """
    if contratos is None:
        contratos = RS._contratos()
    estado = LC.estado_de(source_id, livro)
    regua = RS.regua_de(source_id, livro=livro, evidencias=evidencias,
                        contratos=contratos)
    revisao = revisao_humana_de(source_id, livro=livro, evidencias=evidencias)
    linha = {
        "SOURCE_ID": source_id,
        "STATE": estado or "AUSENTE_DO_LIVRO",
        "READY_RULE": regua,
        "HUMAN_REVIEW_REQUIRED": revisao,
        "COLLECTION_ELIGIBLE": False,
        "MOTIVO": "",
        "PORQUE": "",
    }
    contrato = contratos.get(source_id) or {}
    if contrato.get("ESTADO_CATALOGO") == RETIRADA_POR_DECISAO:
        d9 = contrato.get("CATALOGO_D9") or {}
        linha["MOTIVO"] = RETIRADA_POR_DECISAO
        linha["PORQUE"] = ("retirada do universo por decisao (D9%s); reversivel pelo "
                           "catalogo, nunca por omissao" % (
                               ": %s" % d9.get("PORQUE") if d9.get("PORQUE") else ""))
        return linha
    if estado != LC.READY_FOR_COLLECTION:
        linha["MOTIVO"] = ESTADO_NAO_READY
        linha["PORQUE"] = ("o estado no livro e %s; so entra quem esta em %s"
                           % (linha["STATE"], LC.READY_FOR_COLLECTION))
        return linha
    if regua == "NAO SEI":
        linha["MOTIVO"] = NUNCA_PROMOVIDA
        linha["PORQUE"] = "esta READY sem nenhuma linha de promocao no livro"
        return linha
    if regua != RS.REGUA_CURRENT:
        linha["MOTIVO"] = READY_LEGACY
        linha["PORQUE"] = ("promovida pela regua antiga (%s); a regua de hoje e "
                           "%s — item aberto, retratado e com corpo util"
                           % (regua, RS.REGUA_CURRENT))
        return linha
    if revisao:
        linha["MOTIVO"] = HUMAN_REVIEW_REQUIRED
        linha["PORQUE"] = revisao
        return linha
    linha["COLLECTION_ELIGIBLE"] = True
    linha["MOTIVO"] = ELEGIVEL
    linha["PORQUE"] = ("READY_CURRENT pela regua %s, sem pedido de olho humano"
                       % RS.REGUA_CURRENT)
    return linha


def eligible_for_collection(source_id: str, *, livro: dict | None = None,
                            evidencias: dict | None = None,
                            contratos: dict | None = None) -> bool:
    """A pergunta unica. Quem arranca coleta chama ISTO."""
    return avaliar(source_id, livro=livro, evidencias=evidencias,
                   contratos=contratos)["COLLECTION_ELIGIBLE"]


def porque_nao(source_id: str, **kw) -> str:
    v = avaliar(source_id, **kw)
    return "" if v["COLLECTION_ELIGIBLE"] else "%s: %s" % (v["MOTIVO"], v["PORQUE"])


def _contexto() -> dict:
    """Le os tres ficheiros UMA vez — 278 fontes x 3 leituras seria absurdo."""
    return {"livro": LC._ler_bruto(), "evidencias": RS._evidencias(),
            "contratos": RS._contratos()}


def inventario(*, ctx: dict | None = None) -> list[dict]:
    """TODAS as fontes READY no livro, com a regua e o veredito ao lado.

    Nao e a lista de entrega: e o que um painel honesto mostra. A lista de
    entrega e `elegiveis()`, e e mais curta — de proposito.
    """
    ctx = ctx if ctx is not None else _contexto()
    est = {}
    for t in ctx["livro"]["TRANSICOES"]:
        est[t["SOURCE_ID"]] = t["NEW_STATE"]
    return [avaliar(s, **ctx) for s in sorted(est)
            if est[s] == LC.READY_FOR_COLLECTION]


def elegiveis(*, ctx: dict | None = None) -> list[str]:
    return [l["SOURCE_ID"] for l in inventario(ctx=ctx) if l["COLLECTION_ELIGIBLE"]]


def painel(*, ctx: dict | None = None) -> dict:
    """Os quatro numeros que nao se confundem uns com os outros."""
    inv = inventario(ctx=ctx)
    return {
        "READY_TOTAL": len(inv),
        "READY_CURRENT_TOTAL": sum(1 for l in inv if l["READY_RULE"] == RS.REGUA_CURRENT),
        "READY_LEGACY_TOTAL": sum(1 for l in inv if l["READY_RULE"] == RS.REGUA_LEGACY),
        "HUMAN_REVIEW_REQUIRED": sum(1 for l in inv if l["HUMAN_REVIEW_REQUIRED"]),
        "COLLECTION_ELIGIBLE": sum(1 for l in inv if l["COLLECTION_ELIGIBLE"]),
    }


# ---------------------------------------------------------------------------
# A PORTA PARA QUEM NAO E PYTHON
#
# O coletor agendado e Node. Em vez de traduzir a lei para JavaScript — que e
# como se espalha uma regra por dez ficheiros — ele pergunta AQUI, por linha de
# comando, e le o JSON.
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    ids = []
    for a in argv:
        if a.startswith("--ids="):
            ids = [x.strip() for x in a.split("=", 1)[1].split(",") if x.strip()]
    ctx = _contexto()
    if ids:
        linhas = [avaliar(s, **ctx) for s in ids]
    else:
        linhas = inventario(ctx=ctx)
    d = {"DATASET": "COLLECTION-INTAKE-V1", "CONTRATO": CONTRATO,
         "LEI": ("COLLECTION_ELIGIBLE = READY_CURRENT AND NOT "
                 "HUMAN_REVIEW_REQUIRED AND NOT bloqueada. READY_LEGACY nao "
                 "entra por omissao."),
         "GERADO_EM": LC.agora(),
         "PAINEL": painel(ctx=ctx),
         "PERGUNTADAS": ids or None,
         "COLLECTION_ELIGIBLE_IDS": [l["SOURCE_ID"] for l in linhas
                                     if l["COLLECTION_ELIGIBLE"]],
         "RECUSADAS": [l for l in linhas if not l["COLLECTION_ELIGIBLE"]],
         "LINHAS": linhas}
    if "--json" in argv:
        print(json.dumps(d, ensure_ascii=False))
        return 0
    if "--escrever" in argv:
        SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
        print("escrito: %s" % SAIDA.relative_to(RAIZ))
    p = d["PAINEL"]
    for k in ("READY_TOTAL", "READY_CURRENT_TOTAL", "READY_LEGACY_TOTAL",
              "HUMAN_REVIEW_REQUIRED", "COLLECTION_ELIGIBLE"):
        print("%-24s %d" % (k, p[k]))
    for l in linhas:
        print("  %-12s %-22s %-9s %s" % (l["SOURCE_ID"], l["STATE"],
                                         l["READY_RULE"], l["MOTIVO"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
