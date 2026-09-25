#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D32 (7): FILA-PRECISA-DE-IA + a porta de volta da BANCADA (sem API paga, sem segundo livro).

Desenho do piloto IA-CUR (provas/ia_cur/RELATORIO-IA-CUR.md, sec. 4), agora construido:

    robo de fontes (deterministico)               bancada (agente pela assinatura)
    ─────────────────────────────                 ────────────────────────────────
    QUALIFY para em SEMANTIC_REVIEW ─┐            le a fila por lotes (1.a vez: 30)
    R1 recusa o reparo  ─────────────┼─► FILA ─►  le os BYTES que o robo guardou
    canario PASS_PARCIAL / capa ─────┘  (escritor: o robo; derivada, refeita inteira)
                                                  escreve SO nas portas:
    QUALIFY le DECISOES-SEMANTICAS-V1 ◄────────── territorio / relevancia (decisao_semantica)
    REPAIR_CONTRACT le PROPOSTAS-DE-RECEITA-V1 ◄─ receita (INDEX_URL + LINK_PATTERN + provas)
    VALIDATE_ROUTE -> CANARY -> regua             quem promove e a regua; o agente nunca

UM ESCRITOR POR FICHEIRO. A fila e do robo (o agente so le). As propostas sao do agente (o robo so
le). Nenhum livro de estado e escrito pelo agente, e a fila nao e um livro: nao guarda estado
nenhum que nao esteja ja no livro do robo e nas portas — e refeita inteira a cada volta.

QUANDO UM CASO SAI DA FILA: quando ja foi respondido DEPOIS da ultima prova do robo. Uma resposta
mais velha que a prova nao conta (a prova mudou); uma resposta mais nova conta, mesmo que seja
NAO SEI — perguntar outra vez com os mesmos bytes daria a mesma resposta. Excepcao: a linha que
diz explicitamente que espera a pergunta dupla da D2 (D2.UNIVERSE_MATCH = NAO SEI) volta a fila
como RELEVANCIA_D2.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

FILA_IA = RAIZ / "curadoria" / "FILA-PRECISA-DE-IA-V1.json"          # escritor: o robo
PROPOSTAS = RAIZ / "curadoria" / "PROPOSTAS-DE-RECEITA-V1.json"      # escritor: o agente
LOTE_CANARIO = 30          # D32 (7): a 1.a execucao da bancada e limitada a 30 casos
_SHA = re.compile(r"^[0-9a-f]{64}$")

# porque o robo parou -> que pergunta e para a IA
RECUSAS_DE_RECEITA = ("REPARO_RECUSADO", "CAPA_NAO_E_MATERIA",
                      "canario resolveu, mas a regua dos quatro passos nao promove")


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _t(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _json(p: Path, chave: str) -> list:
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8")).get(chave) or []


# ---------------------------------------------------------------------------
# A PORTA DAS RECEITAS (escritor: o agente; o robo so le)
# ---------------------------------------------------------------------------
class PropostaInvalida(ValueError):
    pass


def validar_proposta(p: dict) -> None:
    """Sem URL + sha256 de bytes lidos, a proposta e uma opiniao — e a porta recusa."""
    for k in ("SOURCE_ID", "INDEX_URL", "LINK_PATTERN", "PROPOSTO_EM", "PROPOSTO_POR", "PORQUE"):
        if not p.get(k):
            raise PropostaInvalida("falta %s" % k)
    if not re.match(r"^(IT|EU|INT)-T\d+-\d{3}$", p["SOURCE_ID"]):
        raise PropostaInvalida("SOURCE_ID fora do formato: %s" % p["SOURCE_ID"])
    try:
        rx = re.compile(p["LINK_PATTERN"])
    except re.error as e:
        raise PropostaInvalida("LINK_PATTERN nao compila: %s" % e) from e
    if rx.match(p["INDEX_URL"].rstrip("/")):
        raise PropostaInvalida("LINK_PATTERN casa com a propria INDEX_URL (listagem viraria item)")
    lidas = [x for x in p.get("PAGINAS_LIDAS") or []
             if str(x.get("URL", "")).startswith(("http://", "https://")) and _SHA.match(str(x.get("SHA256", "")))]
    if not lidas:
        raise PropostaInvalida("sem PAGINAS_LIDAS com URL + sha256")
    if _t(p["PROPOSTO_EM"]) is None:
        raise PropostaInvalida("PROPOSTO_EM ilegivel")


def propor_receita(p: dict, caminho: Path | None = None) -> dict:
    """Acrescenta (nunca reescreve) uma proposta valida. Rebenta se for invalida."""
    caminho = caminho or PROPOSTAS
    validar_proposta(p)
    d = (json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else
         {"DATASET": "PROPOSTAS-DE-RECEITA-V1",
          "LEI": "escritor: a bancada (agente). O robo so le, no REPAIR_CONTRACT; quem promove e a regua.",
          "PROPOSTAS": []})
    d["PROPOSTAS"].append(p)
    caminho.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def responder_sem_receita(r: dict, caminho: Path | None = None) -> dict:
    """A resposta «li e nao ha receita» tambem e uma resposta: com prova, fica na porta, e o caso
    sai da fila ate haver prova nova. O reparo ignora-a (nao e PADRAO_NOVO)."""
    caminho = caminho or PROPOSTAS
    for k in ("SOURCE_ID", "PORQUE", "PROPOSTO_EM", "PROPOSTO_POR"):
        if not r.get(k):
            raise PropostaInvalida("falta %s" % k)
    if not [x for x in r.get("PAGINAS_LIDAS") or [] if _SHA.match(str(x.get("SHA256", "")))]:
        raise PropostaInvalida("sem PAGINAS_LIDAS com URL + sha256")
    r = dict(r, RESPOSTA="SEM_RECEITA")
    d = (json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else
         {"DATASET": "PROPOSTAS-DE-RECEITA-V1",
          "LEI": "escritor: a bancada (agente). O robo so le, no REPAIR_CONTRACT; quem promove e a regua.",
          "PROPOSTAS": []})
    d["PROPOSTAS"].append(r)
    caminho.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return r


def proposta_pendente(source_id: str, contrato: dict | None, *, caminho: Path | None = None,
                      consumida_em: datetime | None = None) -> dict | None:
    """A proposta valida mais recente para esta fonte, ainda nao aplicada.

    Aplicada = o contrato tem REPARO_DE_CONTRATO.APLICADO_EM depois dela, ou uma tarefa de
    reparo ja correu depois dela (`consumida_em`) — assim uma proposta que a porta recusa nao
    volta a fila a cada volta."""
    validas = []
    for p in _json(caminho or PROPOSTAS, "PROPOSTAS"):
        if p.get("SOURCE_ID") != source_id or p.get("RESPOSTA") == "SEM_RECEITA":
            continue
        try:
            validar_proposta(p)
        except PropostaInvalida:
            continue
        validas.append(p)
    if not validas:
        return None
    p = max(validas, key=lambda x: _t(x["PROPOSTO_EM"]))
    quando = _t(p["PROPOSTO_EM"])
    aplicado = _t(((contrato or {}).get("REPARO_DE_CONTRATO") or {}).get("APLICADO_EM"))
    if aplicado and aplicado >= quando:
        return None
    if consumida_em and consumida_em >= quando:
        return None
    return p


def como_desfecho(p: dict) -> dict:
    """A proposta do agente no formato que `reparar_contrato.aplicar` aceita."""
    return {"DESFECHO": "PADRAO_NOVO", "INDEX_URL": p["INDEX_URL"], "LINK_PATTERN": p["LINK_PATTERN"],
            "COMO": "PROPOSTA_DO_AGENTE (%s)" % p["PROPOSTO_POR"], "PAGINAS_LIDAS": p["PAGINAS_LIDAS"],
            "PORQUE": "proposta do agente: %s" % p["PORQUE"]}


# ---------------------------------------------------------------------------
# A FILA (escritor: o robo; derivada, refeita inteira)
# ---------------------------------------------------------------------------
def _ultimas(transicoes: list[dict]) -> dict[str, dict]:
    u = {}
    for t in transicoes:
        u[t["SOURCE_ID"]] = t
    return u


def construir(*, transicoes: list[dict], decisoes: list[dict], propostas: list[dict],
              contratos: dict[str, dict], janela=None, provas_em: dict[str, str] | None = None) -> dict:
    """A fila, pura: nao le disco, nao escreve. `janela(sid, contrato) -> bool` (D29).

    `provas_em` = {EVIDENCE_REF: OBSERVED_AT da prova}. ⚠️ A HORA QUE CONTA E A DA PROVA, NAO A
    DA LINHA DO LIVRO. Medido no vivo: CAND-0586 tem a linha as 12:30 (importacao da
    reconciliacao) e a prova as 04:40; a decisao NAO SEI e das 05:52. Pela hora da linha, as 39
    NAO SEI voltavam todas a fila sem uma pagina nova — a mesma pergunta com os mesmos bytes."""
    provas_em = provas_em or {}
    import lifecycle as LC   # noqa: PLC0415
    import decisao_semantica as DS   # noqa: PLC0415
    ult = _ultimas(transicoes)
    dec = {}
    for d in decisoes:
        dec.setdefault(d.get("CANDIDATA_ID"), []).append(d)
    prop = {}
    for p in propostas:
        prop.setdefault(p.get("SOURCE_ID"), []).append(p)
    casos, fora = [], {}

    def _fora(motivo):
        fora[motivo] = fora.get(motivo, 0) + 1

    for sid, t in sorted(ult.items()):
        e = t["NEW_STATE"]
        prova_em = _t(provas_em.get(t.get("EVIDENCE_REF")) or t.get("OBSERVED_AT"))
        razao = t.get("REASON") or ""
        caso = None
        if sid.startswith("CAND-") and e == LC.SEMANTIC_REVIEW:
            linhas = dec.get(sid) or []
            if len(linhas) > 1:
                caso = ("TERRITORIO", "conflito: %d decisoes para a mesma candidata" % len(linhas))
            elif not linhas:
                caso = ("TERRITORIO", "sem decisao semantica")
            else:
                d = linhas[0]
                respondida = _t(d.get("DECIDIDO_EM"))
                if (d.get("D2") or {}).get("UNIVERSE_MATCH") == "NAO SEI":
                    caso = ("RELEVANCIA_D2", "espera a pergunta dupla da D2")
                elif d.get("TERRITORIO") != "NAO SEI" or d.get("CATEGORIA") in DS.NAO_SEMEIAM:
                    _fora("RESPONDIDA (territorio ou nao-fonte)")
                elif respondida and prova_em and respondida >= prova_em:
                    _fora("NAO SEI respondido depois da ultima prova (espera prova nova)")
                else:
                    caso = ("TERRITORIO", "NAO SEI mais velho que a ultima prova do robo")
        elif sid.startswith(("IT-", "EU-", "INT-")) and e == LC.CONTRACTED_CANARY_FAILED:
            if not razao.startswith(RECUSAS_DE_RECEITA) and "DUPLICADA_DE_IRMA" not in razao:
                if razao.startswith("nenhum dos"):
                    _fora("EMPTY_LIST (o reparo deterministico ainda nao correu)")
                else:
                    _fora("outra falha de canario")
                continue
            if "DUPLICADA_DE_IRMA" in razao:
                _fora("DUPLICADA_DE_IRMA (nao e pergunta para a IA)")
                continue
            ps = [p for p in prop.get(sid) or [] if _t(p.get("PROPOSTO_EM"))]
            if ps and prova_em and max(_t(p["PROPOSTO_EM"]) for p in ps) >= prova_em:
                ultima = max(ps, key=lambda p: _t(p["PROPOSTO_EM"]))
                _fora("respondida SEM_RECEITA depois da ultima prova (espera prova nova)"
                      if ultima.get("RESPOSTA") == "SEM_RECEITA"
                      else "receita proposta depois da ultima prova (espera o robo)")
                continue
            caso = ("RECEITA", razao[:160])
        elif e == LC.SEMANTIC_REVIEW:
            _fora("SEMANTIC_REVIEW de fonte (decisao humana, ex.: ficha do Atlas)")
        if caso:
            c = contratos.get(sid)
            casos.append({"CASO": sid, "PERGUNTA": caso[0], "GATILHO": caso[1], "ESTADO": e,
                          "PROVA_DO_ROBO": t.get("EVIDENCE_REF"), "DESDE": t.get("OBSERVED_AT"),
                          "JANELA_D29": bool(janela(sid, c)) if janela else False,
                          "ENTRADA": ((c or {}).get("ACQUISITION") or {}).get("INDEX_URL")
                          or (c or {}).get("CANONICAL_ENTRY_URL"),
                          "PORTA": ("PROPOSTAS-DE-RECEITA-V1 -> REPAIR_CONTRACT" if caso[0] == "RECEITA"
                                    else "DECISOES-SEMANTICAS-V1 -> QUALIFY")})
    # D29 primeiro; depois o caso mais velho (quem espera ha mais tempo)
    casos.sort(key=lambda x: (not x["JANELA_D29"], x["DESDE"] or "", x["CASO"]))
    por = {}
    for c in casos:
        por[c["PERGUNTA"]] = por.get(c["PERGUNTA"], 0) + 1
    return {"DATASET": "FILA-PRECISA-DE-IA-V1", "CONSTRUIDA_EM": agora(),
            "LEI": "escritor: o robo; derivada do livro e das portas, refeita inteira; nao e livro de estado",
            "TOTAL": len(casos), "POR_PERGUNTA": por, "FORA_DA_FILA": fora, "CASOS": casos}


def construir_do_disco(escrever: bool = True) -> dict:
    import decisao_semantica as DS   # noqa: PLC0415
    import janela_de_cultura as JC   # noqa: PLC0415
    import lifecycle as LC           # noqa: PLC0415
    contratos = {c["SOURCE_ID"]: c for c in
                 _json(RAIZ / "curadoria" / "italy_contracts_curator.json", "FONTES")}
    provas_em = {p["EVIDENCE_REF"]: p.get("OBSERVED_AT")
                 for p in _json(RAIZ / "curadoria" / "LIFECYCLE-EVIDENCE-V1.json", "PROVAS")}
    # a janela (D29) tambem se declara na linha da tabela do coletor, nao so no contrato do robo
    tabela = {c["SOURCE_ID"]: c for c in _json(RAIZ / "regras" / "italy_contracts_onboarded.json", "FONTES")}
    f = construir(transicoes=LC._ler_bruto()["TRANSICOES"], decisoes=DS._ler(),
                  propostas=_json(PROPOSTAS, "PROPOSTAS"), contratos=contratos,
                  janela=lambda sid, c: JC.e_janela(sid, c, tabela.get(sid)), provas_em=provas_em)
    if escrever:
        # ao lado do LIVRO de estados: na producao e curadoria/ (= FILA_IA); num teste que desvia o
        # livro para uma pasta descartavel, a fila vai com ele — nunca escreve na arvore real.
        destino = FILA_IA if LC.LIVRO.parent == FILA_IA.parent else LC.LIVRO.parent / FILA_IA.name
        destino.write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding="utf-8")
    return f


def lote(fila: dict, n: int = LOTE_CANARIO) -> list[dict]:
    """Os n primeiros casos da fila — o que a bancada le nesta execucao."""
    return list(fila["CASOS"][:n])


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lote", type=int, default=LOTE_CANARIO)
    ap.add_argument("--nao-escrever", action="store_true")
    a = ap.parse_args()
    f = construir_do_disco(escrever=not a.nao_escrever)
    print(json.dumps({k: f[k] for k in ("TOTAL", "POR_PERGUNTA", "FORA_DA_FILA")}, ensure_ascii=False, indent=1))
    for c in lote(f, a.lote):
        print("%-12s %-14s D29=%s %s" % (c["CASO"], c["PERGUNTA"], int(c["JANELA_D29"]), c["GATILHO"][:80]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
