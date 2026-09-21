#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RECONCILIAR OS TRES LIVROS DE FONTES — por SOURCE_ID, pela prova, sem rede.

    LIVRO A   curadoria/LIFECYCLE-LEDGER-V1.json desta arvore (o canonico)
    LIVRO B   o mesmo ficheiro em aquisicao-detalhe-v1 (f98f234c)
    LIVRO B2  o mesmo ficheiro em candidate-bridge-v1 (63b71421)

Tres livros, nao dois: a integracao bridge+feeder trouxe a ponte inteira mas
deixou o ledger congelado, e os 75 bloqueios (69 POLICY_BLOCK + 6
CAPABILITY_BLOCK) ficaram so em B2. Um bloqueio comprovado nao desaparece
porque outro livro nao o conhece — AUSENCIA DE ANOTACAO NAO E REVOGACAO.

    NAO SE ESCOLHE UM LIVRO. NAO SE SOMAM ESTADOS. O MAIS RECENTE NAO VENCE.
    CADA SOURCE_ID RECEBE UM ESTADO FINAL, E A PROVA QUE O SUSTENTA.

Estados finais (e so estes):

    READY_CURRENT     os quatro passos na evidencia da promocao
                      (INDEX_URL -> DETAIL_LINKS -> ITEM ABERTO -> BODY UTIL)
                      e contrato atual. A regua vive em ready_split.passos_da_promocao.
    READY_LEGACY      PASS_PARCIAL: rota atual provada ate as ligacoes ou ate
                      um documento pela regua antiga, sem o gate de detalhe.
    RETRY             a ultima corrida real deu 429; a prova anterior era PASS.
    DEGRADED          a Collection reportou falha (ROUTE_FAILURE) na corrida real.
    POLICY_BLOCK      LinkedIn/Instagram: TOS proibem coleta automatizada.
    CAPABILITY_BLOCK  fonte boa, aquisicao impossivel com o que a casa tem.
    UNKNOWN           sem prova em nenhum sentido — NAO SEI e resultado.
    NOT_READY         prova de defeito (a rota traz capa/listagem como
                      documento; canario reprovado) ou passo pendente
                      (contrato, canario, revisao humana).

Zero rede: B e B2 leem-se por `git show` em commits fixos; A le-se do disco.
Nada aqui reexecuta pedidos. Onde a prova em disco nao chega, o estado e
UNKNOWN e a linha diz NEEDS_NETWORK_PROOF.

O livro canonico EVOLUI por acrescimo (F5/F6): `aplicar()` passa cada linha
por `lifecycle.registar`, que valida a transicao, e grava a proveniencia
(IMPORTADO_DE / RECONCILIACAO) ao lado das chaves canonicas. Nunca reescreve.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import lifecycle as LC        # noqa: E402
import ready_split as RS      # noqa: E402

MISSAO = "RECONCILIACAO-V1"
REF_B = "f98f234c"      # aquisicao-detalhe-v1, arvore final
REF_B2 = "63b71421"     # candidate-bridge-v1, ledger com os 75 bloqueios

# Ficheiros REAIS desta arvore. Redirecionaveis em testes (molde: test_ready_split.py).
EVIDENCIA_A = RAIZ / "curadoria" / "LIFECYCLE-EVIDENCE-V1.json"
CONTRATOS_A = RAIZ / "curadoria" / "italy_contracts_curator.json"
LISTAGENS_A = RAIZ / "curadoria" / "LISTAGENS-PROVADAS-V1.json"
ALLOC = RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"
MATCH = RAIZ / "curadoria" / "CANDIDATE-TO-SOURCE-MATCH-V1.json"
PORTA = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
SAIDA = RAIZ / "curadoria" / "RECONCILIACAO-V1.json"

# Estados finais da reconciliacao.
READY_CURRENT = "READY_CURRENT"
READY_LEGACY = "READY_LEGACY"
RETRY = "RETRY"
DEGRADED = "DEGRADED"
POLICY_BLOCK = "POLICY_BLOCK"
CAPABILITY_BLOCK = "CAPABILITY_BLOCK"
UNKNOWN = "UNKNOWN"
NOT_READY = "NOT_READY"
ESTADOS_FINAIS = (READY_CURRENT, READY_LEGACY, RETRY, DEGRADED, POLICY_BLOCK,
                  CAPABILITY_BLOCK, UNKNOWN, NOT_READY)

# Estados do lifecycle que se leem como NOT_READY (passo pendente ou reprovado).
FAMILIA_NOT_READY = frozenset({
    LC.DISCOVERED, LC.QUALIFYING, LC.CONTRACT_PENDING, LC.CANARY_PENDING,
    LC.REPAIRING, LC.CONTRACT_READY_ROUTE_BLOCKED, LC.CONTRACTED_CANARY_FAILED,
    LC.SEMANTIC_REVIEW, LC.RECONCILIATION_REQUIRED,
})

# A porta conhece tres familias sociais; as duas primeiras sao politica, a
# terceira e capacidade. E o mesmo vocabulario de ponte_candidatas.py.
TIPOS_POLITICA = {"LINKEDIN": "linkedin.com", "INSTAGRAM": "instagram.com"}
TIPOS_CAPACIDADE = {"FACEBOOK": "facebook.com"}

SOURCE_ID_RE = re.compile(r"^IT-T\d{1,2}-\d{3}$")
CANDIDATA_RE = re.compile(r"^CAND-\d{4}$")

BCR_INSTITUCIONAL = "BCR_ALVO_INSTITUCIONAL"
BCR_LISTAGEM = "BCR_ALVO_LISTAGEM"
BCR_MATERIA = "BCR_ALVO_MATERIA"
BCR_PAPELADA = "BCR_ALVO_PAPELADA_PDF"


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# LEITURA — disco para A, git show (commit fixo) para B e B2. Zero rede.
# ---------------------------------------------------------------------------
def do_git(ref: str, caminho: str) -> dict | list | None:
    try:
        r = subprocess.run(["git", "show", "%s:%s" % (ref, caminho)], cwd=str(RAIZ),
                           capture_output=True, text=True, encoding="utf-8", timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0 or not r.stdout:
        return None
    return json.loads(r.stdout)


def _json(p: Path, vazio):
    if not p.exists():
        return vazio
    return json.loads(p.read_text(encoding="utf-8"))


def ultimos(livro: dict | None) -> dict:
    """{SOURCE_ID: ultima transicao} — o estado e a ultima linha, nunca um campo."""
    est: dict = {}
    for t in (livro or {}).get("TRANSICOES", []):
        est[t["SOURCE_ID"]] = t
    return est


def historias(livro: dict | None) -> dict:
    h: dict = defaultdict(list)
    for t in (livro or {}).get("TRANSICOES", []):
        h[t["SOURCE_ID"]].append(t)
    return h


def carregar_contexto(*, ref_b: str = REF_B, ref_b2: str = REF_B2) -> dict:
    """Tudo o que a decisao precisa, lido UMA vez. Em testes, constroi-se a mao."""
    porta = _json(PORTA, {"CANDIDATAS": []})
    cands = porta.get("CANDIDATAS") or []
    if isinstance(cands, dict):
        cands = list(cands.values())
    alloc = _json(ALLOC, {"NOVAS": []})
    match = _json(MATCH, {"MATCHES": []})
    alias = {}
    for n in alloc.get("NOVAS", []):
        if n.get("CANDIDATE_ID") and n.get("SOURCE_ID"):
            alias[n["CANDIDATE_ID"]] = n["SOURCE_ID"]
    for m in match.get("MATCHES", []):
        if m.get("CANDIDATE_ID") and m.get("MATCHED_SOURCE_ID"):
            alias.setdefault(m["CANDIDATE_ID"], m["MATCHED_SOURCE_ID"])

    estado_b = do_git(ref_b, "curadoria/ESTADO-ACTUAL-DAS-FONTES-V1.json") or {}
    classif_b = do_git(ref_b, "curadoria/CLASSIFICACAO-INDICE-104-V1.json") or {}
    prova_b = do_git(ref_b, "curadoria/PROVA-DE-LISTAGENS-V1.json") or {}
    passo2_b = do_git(ref_b, "curadoria/CONTRATOS-PASSO-2-V1.json") or {}
    contratos_b = do_git(ref_b, "curadoria/italy_contracts_curator.json") or {}

    return {
        "COMMITS": {"A": _head_curto(), "B": ref_b, "B2": ref_b2},
        "A": LC._ler_bruto(),
        "B": do_git(ref_b, "curadoria/LIFECYCLE-LEDGER-V1.json"),
        "B2": do_git(ref_b2, "curadoria/LIFECYCLE-LEDGER-V1.json"),
        "EVIDENCIA_A": {p["EVIDENCE_REF"]: p for p in _json(EVIDENCIA_A, {"PROVAS": []})["PROVAS"]},
        "CONTRATOS_A": {c["SOURCE_ID"]: c for c in _json(CONTRATOS_A, {"FONTES": []})["FONTES"]},
        "CONTRATOS_B": {c["SOURCE_ID"]: c for c in contratos_b.get("FONTES", [])},
        "LISTAGENS_A": {r["SOURCE_ID"]: r for r in _json(LISTAGENS_A, {"RESULTADOS": []})["RESULTADOS"]
                        if r.get("SOURCE_ID")},
        "ESTADO_B": {f["SOURCE_ID"]: f for f in estado_b.get("FONTES", [])},
        "CLASSIF_B": {f["SOURCE_ID"]: f for f in classif_b.get("FONTES", [])},
        "PROVA_B": {r["SOURCE_ID"]: r for r in prova_b.get("RESULTADOS", [])},
        "PASSO2_TOCADAS": {t["SOURCE_ID"]: t for t in passo2_b.get("TOCADAS", [])},
        "PASSO2_INTOCADAS": {t["SOURCE_ID"]: t for t in passo2_b.get("INTOCADAS", [])},
        "PORTA": {(c.get("CANDIDATA_ID") or c.get("CANDIDATE_ID")): c for c in cands},
        "ALIAS": alias,
    }


def _head_curto() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(RAIZ),
                              capture_output=True, text=True, timeout=30).stdout.strip() or "NAO SEI"
    except (OSError, subprocess.SubprocessError):
        return "NAO SEI"


# ---------------------------------------------------------------------------
# IDENTIDADE — lei 10: mesma SOURCE_ID, uma identidade final.
# ---------------------------------------------------------------------------
def identidade(sid: str, ctx: dict) -> tuple[str, str]:
    """(id canonico, tipo). CAND-* que ja tem SOURCE_ID no Atlas/alocacao e
    ALIAS: o bloqueio dela pertence a SOURCE_ID, nao a uma segunda linha."""
    if SOURCE_ID_RE.match(sid):
        return sid, "SOURCE_ID"
    if CANDIDATA_RE.match(sid):
        alvo = ctx["ALIAS"].get(sid)
        if alvo:
            return alvo, "ALIAS_DE_CANDIDATA"
        return sid, "CANDIDATE_KEY"
    return sid, "INVALIDO"


# ---------------------------------------------------------------------------
# BLOQUEIOS — leis 2 e 3. Preservar pela evidencia; ceder so a prova posterior
# contida na PROPRIA historia da fonte.
# ---------------------------------------------------------------------------
def _evidencia_do_bloqueio(chave: str, linha: dict, ctx: dict) -> tuple[bool, str]:
    """A prova do bloqueio confere com esta arvore?"""
    estado = linha["NEW_STATE"]
    ref = linha.get("EVIDENCE_REF") or ""
    c = ctx["PORTA"].get(chave)
    if c is not None:
        tipo = (c.get("TIPO") or "").upper()
        host = re.sub(r"^https?://(www\.)?", "", (c.get("URL") or "").lower()).split("/")[0]
        if estado == LC.POLICY_BLOCK:
            dom = TIPOS_POLITICA.get(tipo)
            if dom and host.endswith(dom):
                return True, "porta desta arvore: TIPO=%s, host=%s (TOS proibem coleta automatizada)" % (tipo, host)
            return False, "porta desta arvore contradiz: TIPO=%s host=%s nao e politica" % (tipo, host)
        if estado == LC.CAPABILITY_BLOCK:
            dom = TIPOS_CAPACIDADE.get(tipo)
            if dom and host.endswith(dom):
                return True, "porta desta arvore: TIPO=%s, host=%s (sem adaptador nesta instalacao)" % (tipo, host)
            return False, "porta desta arvore contradiz: TIPO=%s host=%s nao e capacidade em falta" % (tipo, host)
    if CANDIDATA_RE.match(chave):
        return False, "candidata ausente da porta desta arvore — bloqueio sem prova local"
    if ref:
        return True, "EVIDENCE_REF=%s" % ref
    return False, "bloqueio sem EVIDENCE_REF"


def _superado_na_historia(chave: str, linha: dict, ctx: dict) -> dict | None:
    """Outro livro tem a MESMA linha de bloqueio e continua com transicoes com
    prova? Entao o bloqueio foi superado por capacidade nova, nao por omissao."""
    for nome in ("A", "B", "B2"):
        hist = ctx["_HIST"][nome].get(chave) or []
        for i, t in enumerate(hist):
            if (t["NEW_STATE"] == linha["NEW_STATE"] and t.get("OBSERVED_AT") == linha.get("OBSERVED_AT")):
                depois = [u for u in hist[i + 1:] if u.get("EVIDENCE_REF")]
                if depois:
                    ult = hist[-1]
                    return {"LIVRO": nome, "ESTADO_POSTERIOR": ult["NEW_STATE"],
                            "EVIDENCE_REF": ult.get("EVIDENCE_REF"),
                            "OBSERVED_AT": ult.get("OBSERVED_AT")}
    return None


def bloqueio_de(chave: str, chaves_originais: list, ctx: dict) -> dict:
    """Devolve {FINAL, LIVRO, EVIDENCIA, PORQUE} se ha bloqueio a preservar;
    e regista os rejeitados/superados em ctx['_BLOQUEIOS']."""
    for nome in ("B2", "A", "B"):
        for k in chaves_originais:
            t = ctx["_ULT"][nome].get(k)
            if not t or t["NEW_STATE"] not in (LC.POLICY_BLOCK, LC.CAPABILITY_BLOCK):
                continue
            ok, porque = _evidencia_do_bloqueio(k, t, ctx)
            if not ok:
                ctx["_BLOQUEIOS"]["REJEITADOS"].append(
                    {"SOURCE_ID": chave, "CHAVE_NO_LIVRO": k, "LIVRO": nome,
                     "ESTADO": t["NEW_STATE"], "PORQUE": porque})
                continue
            sup = _superado_na_historia(k, t, ctx)
            if sup:
                ctx["_BLOQUEIOS"]["SUPERADOS"].append(
                    {"SOURCE_ID": chave, "LIVRO_DO_BLOQUEIO": nome, "ESTADO": t["NEW_STATE"],
                     "SUPERADO_POR": sup})
                continue
            return {"FINAL": t["NEW_STATE"], "LIVRO": nome, "CHAVE": k,
                    "EVIDENCIA": porque, "OBSERVED_AT": t.get("OBSERVED_AT"),
                    "REASON": t.get("REASON")}
    return {}


# ---------------------------------------------------------------------------
# PROVAS DE READY — o que cada livro consegue provar sobre a rota de hoje.
# ---------------------------------------------------------------------------
def _alvo_da_bcr(classif: dict | None) -> str | None:
    for b in (classif or {}).get("BANDEIRAS", []):
        if b in (BCR_INSTITUCIONAL, BCR_LISTAGEM, BCR_MATERIA, BCR_PAPELADA):
            return b
    return None


def prova_b(sid: str, ctx: dict) -> dict:
    est = ctx["ESTADO_B"].get(sid) or {}
    bc = est.get("BIG_COLLECTION") if isinstance(est.get("BIG_COLLECTION"), dict) else {}
    cl = ctx["CLASSIF_B"].get(sid)
    pl = ctx["PROVA_B"].get(sid)
    toc = ctx["PASSO2_TOCADAS"].get(sid)
    into = ctx["PASSO2_INTOCADAS"].get(sid)
    return {
        "STRATEGY": est.get("STRATEGY"), "ORIGEM": est.get("ORIGEM_DO_CONTRATO"),
        "ROUTE": est.get("ROUTE"), "ADAPTER_ID": est.get("ADAPTER_ID"),
        "BCR_CLASSE": bc.get("CLASSE"), "BCR_OBS": bc.get("OBSERVACOES"),
        "BCR_RUN_ID": bc.get("RUN_ID"),
        "CLASSIFICACAO": (cl or {}).get("CLASSIFICACAO"),
        "CRITERIO": (cl or {}).get("CRITERIO"),
        "ALVO_DA_BCR": _alvo_da_bcr(cl),
        "LISTAGEM_PROVADA": (pl or {}).get("LISTAGEM_PROVADA"),
        "LISTAGEM_URL": (pl or {}).get("URL_EFECTIVA") or (pl or {}).get("LISTAGEM_PROPOSTA"),
        "ROTA_MUDOU_DEPOIS_DA_BCR": bool(toc),
        "ROTA_DEPOIS": ((toc or {}).get("DEPOIS") or {}).get("INDEX_URL"),
        "PASSO2_INTOCADA_MOTIVO": (into or {}).get("MOTIVO"),
    }


def veredito_b(sid: str, ctx: dict) -> tuple[str | None, str, dict]:
    """O que o livro B prova, por si, sobre a rota de hoje. (estado, porque, prova)."""
    t = ctx["_ULT"]["B"].get(sid)
    pb = prova_b(sid, ctx)
    if not t:
        return None, "B nao conhece a fonte", pb
    e = t["NEW_STATE"]
    if e == LC.DEGRADED:
        return DEGRADED, "B: a Collection reportou falha na corrida real (%s)" % (t.get("EVIDENCE_REF") or "")[:60], pb
    if e in (LC.POLICY_BLOCK, LC.CAPABILITY_BLOCK):
        return e, "B: bloqueio %s" % e, pb
    if e == LC.RETRY_AFTER:
        return RETRY, "B: RETRY_AFTER", pb
    if e == LC.UNKNOWN:
        return UNKNOWN, "B: UNKNOWN", pb
    if e in FAMILIA_NOT_READY:
        return NOT_READY, "B: %s (%s)" % (e, (t.get("REASON") or "")[:70]), pb
    if e != LC.READY_FOR_COLLECTION:
        return UNKNOWN, "B: estado fora do vocabulario: %s" % e, pb

    # READY em B. READY SEM PROVA NAO E READY.
    ref = t.get("EVIDENCE_REF") or ""
    if not ref:
        return UNKNOWN, "B: READY sem EVIDENCE_REF — promocao sem prova nao promove", pb
    if pb["BCR_CLASSE"] == "RATE_LIMITED_429":
        return RETRY, "B: a corrida real BCR-2026-09-20 devolveu 429; a prova anterior (%s) e PASS pela regua antiga" % ref[:50], pb
    if pb["BCR_CLASSE"] in ("ROUTE_FAILURE", "CAPABILITY_GAP"):
        return NOT_READY, "B: READY mas a corrida real deu %s" % pb["BCR_CLASSE"], pb
    if pb["BCR_CLASSE"] != "SUCCESS":
        if ref.startswith("BCR-"):
            return UNKNOWN, "B: evidencia cita BCR mas ESTADO-ACTUAL nao tem a corrida — NEEDS_NETWORK_PROOF", pb
        return UNKNOWN, "B: READY com prova que esta arvore nao consegue conferir (%s) — NEEDS_NETWORK_PROOF" % ref[:50], pb

    # Corrida real com SUCCESS. O que a Collection colheu?
    if pb["ROTA_MUDOU_DEPOIS_DA_BCR"]:
        if pb["LISTAGEM_PROVADA"]:
            return READY_LEGACY, ("B: rota mudou depois da BCR (passo 2) e a listagem nova esta provada "
                                  "ate as ligacoes — PASS_PARCIAL na rota atual"), pb
        return NOT_READY, "B: rota mudou depois da BCR (passo 2) e a listagem nova nao esta provada", pb
    alvo = pb["ALVO_DA_BCR"]
    if alvo == BCR_INSTITUCIONAL:
        return NOT_READY, "B: a BCR colheu a capa institucional como documento (%s) — homepage 200 nao e READY (lei 1)" % alvo, pb
    if alvo == BCR_LISTAGEM:
        return NOT_READY, "B: a BCR colheu a propria listagem como documento (%s) — prova da listagem nao e prova do item (lei 7)" % alvo, pb
    if alvo == BCR_MATERIA:
        return READY_LEGACY, "B: a BCR colheu materia (%s) pela regua antiga; sem gate de detalhe" % alvo, pb
    if alvo == BCR_PAPELADA:
        return UNKNOWN, ("B: a BCR colheu PDF de papelada a partir da capa (C5); forma do indice NAO_SEI; "
                         "sem prova de item de publicacao — NEEDS_NETWORK_PROOF"), pb
    # Fora do universo classificado (video, endpoint estatico, series com mais de uma observacao).
    return READY_LEGACY, ("B: corrida real com SUCCESS (%s obs, %s) fora do universo do gate de detalhe; "
                          "regua antiga" % (pb["BCR_OBS"], pb["STRATEGY"])), pb


def veredito_a(sid: str, ctx: dict) -> tuple[str | None, str, dict]:
    """O que o livro A prova, por si. (estado, porque, passos)."""
    t = ctx["_ULT"]["A"].get(sid)
    if not t:
        return None, "A nao conhece a fonte", {}
    e = t["NEW_STATE"]
    if e == LC.READY_FOR_COLLECTION:
        promo = RS.ultima_promocao(sid, ctx["A"])
        ev = ctx["EVIDENCIA_A"].get((promo or {}).get("EVIDENCE_REF") or "")
        c = ctx["CONTRATOS_A"].get(sid)
        r = RS.passos_da_promocao(promo, ev, c)
        if r["REGUA"] == RS.REGUA_CURRENT:
            return READY_CURRENT, "A: " + r["PORQUE"], r
        if ev is None:
            return READY_LEGACY, "A: promovida com prova externa (%s) pela regua antiga; %s" % (
                (promo or {}).get("EVIDENCE_REF", "")[:40], r["PORQUE"]), r
        return READY_LEGACY, "A: " + r["PORQUE"], r
    if e == LC.DEGRADED:
        return DEGRADED, "A: DEGRADED", {}
    if e == LC.RETRY_AFTER:
        return RETRY, "A: RETRY_AFTER", {}
    if e == LC.UNKNOWN:
        return UNKNOWN, "A: UNKNOWN", {}
    if e in (LC.POLICY_BLOCK, LC.CAPABILITY_BLOCK):
        return e, "A: %s" % e, {}
    if e in FAMILIA_NOT_READY:
        return NOT_READY, "A: %s (%s)" % (e, (t.get("REASON") or "")[:70]), {}
    return UNKNOWN, "A: estado fora do vocabulario: %s" % e, {}


def _quando(ref_ou_linha) -> str:
    return (ref_ou_linha or {}).get("OBSERVED_AT") or ""


# ---------------------------------------------------------------------------
# A DECISAO POR SOURCE_ID
# ---------------------------------------------------------------------------
def decidir(chave: str, chaves_originais: list, tipo: str, ctx: dict) -> dict:
    tA = ctx["_ULT"]["A"].get(chave)
    tB = ctx["_ULT"]["B"].get(chave)
    tB2 = None
    for k in chaves_originais:
        tB2 = ctx["_ULT"]["B2"].get(k) or tB2

    linha = {
        "SOURCE_ID": chave, "IDENTITY_KIND": tipo,
        "CHAVES_NOS_LIVROS": sorted(set(chaves_originais)),
        "STATE_A": tA["NEW_STATE"] if tA else None,
        "STATE_B": tB["NEW_STATE"] if tB else None,
        "STATE_B2": tB2["NEW_STATE"] if tB2 else None,
    }
    cA = ctx["CONTRATOS_A"].get(chave) or {}
    cB = ctx["CONTRATOS_B"].get(chave) or {}
    pb = prova_b(chave, ctx)
    linha["CONTRACT_A"] = ({"HASH": cA.get("SOURCE_CONTRACT_HASH"),
                            "ROUTE_PROVENANCE": (cA.get("ROUTE_PROVENANCE") or {}).get("INTEGRADO_EM")}
                           if cA else None)
    linha["CONTRACT_B"] = ({"HASH": cB.get("SOURCE_CONTRACT_HASH")} if cB else
                           ({"ORIGEM": pb["ORIGEM"], "STRATEGY": pb["STRATEGY"],
                             "PASSO2": "TOCADA" if pb["ROTA_MUDOU_DEPOIS_DA_BCR"] else
                             ("INTOCADA:%s" % pb["PASSO2_INTOCADA_MOTIVO"] if pb["PASSO2_INTOCADA_MOTIVO"] else None)}
                            if pb["STRATEGY"] or pb["ORIGEM"] else None))
    linha["ROUTE_A"] = ((cA.get("ACQUISITION") or {}).get("INDEX_URL") or cA.get("CANONICAL_ENTRY_URL")) if cA else None
    linha["ROUTE_B"] = pb["ROTA_DEPOIS"] or pb["ROUTE"] or ((cB.get("ACQUISITION") or {}).get("INDEX_URL") if cB else None)
    linha["CANARY_A"] = None
    if tA:
        ev = ctx["EVIDENCIA_A"].get(tA.get("EVIDENCE_REF") or "")
        linha["CANARY_A"] = ({"EVIDENCE_REF": tA.get("EVIDENCE_REF"), "PASS": (ev or {}).get("DADOS", {}).get("PASS"),
                              "OBSERVED_AT": tA.get("OBSERVED_AT")} if tA.get("EVIDENCE_REF") else None)
    linha["CANARY_B"] = ({"BCR_CLASSE": pb["BCR_CLASSE"], "BCR_OBS": pb["BCR_OBS"], "RUN_ID": pb["BCR_RUN_ID"]}
                         if pb["BCR_CLASSE"] else None)
    linha["DETAIL_PROOF_B"] = ({"CLASSIFICACAO": pb["CLASSIFICACAO"], "ALVO_DA_BCR": pb["ALVO_DA_BCR"],
                                "LISTAGEM_PROVADA": pb["LISTAGEM_PROVADA"]}
                               if (pb["CLASSIFICACAO"] or pb["LISTAGEM_PROVADA"] is not None) else None)
    linha["POLICY_EVIDENCE"] = None
    linha["CAPABILITY_EVIDENCE"] = None

    # 0. identidade invalida: nao e fonte.
    if tipo == "INVALIDO":
        linha.update(FINAL_STATE=UNKNOWN, DETAIL_PROOF_A=None, LATEST_VALID_EVIDENCE=None,
                     FINAL_REASON=("identificador fora do formato SOURCE_ID (IT-T<n>-<nnn>) e fora da porta: "
                                   "linha de prova gravada no livro real; nao e fonte; nao se apaga (append-only)"),
                     LIFECYCLE_TARGET=LC.UNKNOWN)
        return linha

    # 1. bloqueios preservados pela evidencia.
    b = bloqueio_de(chave, chaves_originais, ctx)
    if b:
        campo = "POLICY_EVIDENCE" if b["FINAL"] == LC.POLICY_BLOCK else "CAPABILITY_EVIDENCE"
        linha[campo] = {"LIVRO": b["LIVRO"], "CHAVE": b["CHAVE"], "EVIDENCIA": b["EVIDENCIA"],
                        "OBSERVED_AT": b["OBSERVED_AT"], "REASON": (b.get("REASON") or "")[:120]}
        linha.update(FINAL_STATE=b["FINAL"], DETAIL_PROOF_A=None,
                     LATEST_VALID_EVIDENCE={"FONTE": "livro %s" % b["LIVRO"], "QUANDO": b["OBSERVED_AT"],
                                            "COMMIT": ctx["COMMITS"][b["LIVRO"]]},
                     FINAL_REASON="bloqueio preservado pela evidencia (%s); ausencia noutro livro nao e revogacao" % b["EVIDENCIA"],
                     LIFECYCLE_TARGET=b["FINAL"])
        return linha

    # 2. o que cada livro prova.
    vA, pA, passosA = veredito_a(chave, ctx)
    vB, pB, _ = veredito_b(chave, ctx)
    linha["DETAIL_PROOF_A"] = passosA.get("PASSOS") if passosA else None
    if pb["ADAPTER_ID"]:
        linha["CAPABILITY_EVIDENCE"] = {"ADAPTER_ID": pb["ADAPTER_ID"],
                                        "ONDE": "%s (coleta/adaptadores_de_aquisicao.mjs); NAO nesta arvore" % ctx["COMMITS"]["B"]}

    final, porque, ev_final = _combinar(chave, tA, tB, vA, pA, vB, pB, ctx)
    linha.update(FINAL_STATE=final, FINAL_REASON=porque, LATEST_VALID_EVIDENCE=ev_final,
                 LIFECYCLE_TARGET=_alvo_lifecycle(final, tA, tB, tB2))
    if final == READY_CURRENT:
        linha["REVISAO_HUMANA"] = _item_parece_seccao(chave, ctx)
    return linha


def _item_parece_seccao(sid: str, ctx: dict) -> str | None:
    """Heuristica DECLARADA, que nao muda o estado: o endereco do item aberto
    tem menos de 4 palavras e nenhum digito (ex.: /lavora-con-noi,
    /articoli-e-pubblicazioni/). Serve para excluir da micro-colheita sugerida
    e pedir olho humano — nao para condenar."""
    promo = RS.ultima_promocao(sid, ctx["A"])
    ev = ctx["EVIDENCIA_A"].get((promo or {}).get("EVIDENCE_REF") or "") or {}
    url = ((ev.get("DADOS") or {}).get("ITEM_ABERTO") or {}).get("URL") or ""
    slug = [s for s in re.sub(r"^https?://[^/]+", "", url).split("/") if s]
    if not slug:
        return None
    ultimo = slug[-1]
    if len(ultimo.split("-")) < 4 and not any(ch.isdigit() for ch in ultimo):
        return "ITEM_PARECE_SECCAO: %s — confirmar a olho que e um item e nao uma seccao" % url
    return None


def _combinar(chave, tA, tB, vA, pA, vB, pB, ctx) -> tuple[str, str, dict | None]:
    cB = ctx["COMMITS"]["B"]
    evA = {"FONTE": "livro A", "QUANDO": _quando(tA), "COMMIT": ctx["COMMITS"]["A"],
           "REF": (tA or {}).get("EVIDENCE_REF")} if tA else None
    evB = {"FONTE": "livro B", "QUANDO": _quando(tB), "COMMIT": cB,
           "REF": (tB or {}).get("EVIDENCE_REF")} if tB else None

    if vA is None and vB is None:
        return UNKNOWN, "nenhum livro tem prova — NAO SEI", None
    if vA is None:
        return vB, pB, evB
    if vB is None:
        return vA, pA, evA

    # A nao e READY nem bloqueio, e B e READY: quem tem a rota de hoje?
    if vA == READY_CURRENT:
        return READY_CURRENT, pA, evA
    if vA == NOT_READY and tA["NEW_STATE"] == LC.RECONCILIATION_REQUIRED:
        # A diz, por escrito, «remedir onde o adaptador existe». B e essa linha.
        return vB, ("A: RECONCILIATION_REQUIRED (medida contra rota morta) — remedida em B: " + pB), evB
    if vA == READY_LEGACY:
        # A promoveu pela regua antiga; B guarda o que a corrida real colheu com o MESMO contrato.
        if vB == NOT_READY and not prova_b(chave, ctx)["ROTA_MUDOU_DEPOIS_DA_BCR"]:
            return NOT_READY, pB + " | " + pA, evB
        if vB == RETRY:
            return RETRY, pB, evB
        return READY_LEGACY, pA + " | " + pB, evA
    if vA in (DEGRADED, RETRY, UNKNOWN):
        if vB in (READY_LEGACY, READY_CURRENT) and tB.get("EVIDENCE_REF") and _quando(tB) > _quando(tA):
            return vB, pB + " | A: %s antes" % vA, evB
        return vA, pA + " | B: " + pB, evA
    if vA == NOT_READY:
        # Quem mediu por ultimo COM PROVA decide — e so uma prova posterior de B
        # pode desfazer um passo pendente/reprovado de A (leis 5 e 6: contrato e
        # rota atuais). Sem essa prova, o READY antigo de B nao vence.
        if vB in (READY_LEGACY, READY_CURRENT) and _quando(tB) > _quando(tA) and tB.get("EVIDENCE_REF"):
            return vB, pB + " | A: " + pA + " (anterior)", evB
        return NOT_READY, ("A mediu depois (%s) sobre o contrato atual: %s | B (%s) media a rota antiga: %s"
                           % (_quando(tA)[:19], pA, (tB.get("EVIDENCE_REF") or "")[:40], pB)), evA
    return UNKNOWN, "combinacao nao prevista: A=%s B=%s" % (vA, vB), None


def _alvo_lifecycle(final: str, tA: dict | None, tB: dict | None = None,
                    tB2: dict | None = None) -> str:
    if final in (READY_CURRENT, READY_LEGACY):
        return LC.READY_FOR_COLLECTION
    if final == RETRY:
        return LC.RETRY_AFTER
    if final in (DEGRADED, POLICY_BLOCK, CAPABILITY_BLOCK, UNKNOWN):
        return final
    # NOT_READY: manter o passo pendente que o livro que conhece a fonte ja
    # diz (A primeiro; se A nao a conhece, o livro de origem). Se o que se
    # dizia era READY, o passo pendente e remedir: CANARY_PENDING.
    for t in (tA, tB, tB2):
        if t is None:
            continue
        if t["NEW_STATE"] in FAMILIA_NOT_READY:
            return t["NEW_STATE"]
        break
    return LC.CANARY_PENDING


# ---------------------------------------------------------------------------
# O CENSO — uma linha por SOURCE_ID, uniao dos tres livros.
# ---------------------------------------------------------------------------
def censo(ctx: dict) -> dict:
    ctx["_ULT"] = {n: ultimos(ctx.get(n)) for n in ("A", "B", "B2")}
    ctx["_HIST"] = {n: historias(ctx.get(n)) for n in ("A", "B", "B2")}
    ctx["_BLOQUEIOS"] = {"REJEITADOS": [], "SUPERADOS": []}

    A, B, B2 = (set(ctx["_ULT"][n]) for n in ("A", "B", "B2"))
    grupos: dict = defaultdict(list)
    tipos: dict = {}
    duplicados = []
    for k in sorted(A | B | B2):
        can, tipo = identidade(k, ctx)
        grupos[can].append(k)
        if tipo == "ALIAS_DE_CANDIDATA":
            duplicados.append({"CANDIDATA": k, "SOURCE_ID": can,
                               "RESOLUCAO": "uma identidade: a candidata e alias; o estado dela conta para a SOURCE_ID"})
            tipos.setdefault(can, "SOURCE_ID")
        else:
            tipos[can] = tipo if can not in tipos or tipos[can] != "SOURCE_ID" else tipos[can]

    linhas = [decidir(can, grupos[can], tipos[can], ctx) for can in sorted(grupos)]
    conta = Counter(l["FINAL_STATE"] for l in linhas)
    ready_cur = [l for l in linhas if l["FINAL_STATE"] == READY_CURRENT]

    importados_p = [l for l in linhas if l["FINAL_STATE"] == POLICY_BLOCK and l["STATE_A"] != LC.POLICY_BLOCK]
    importados_c = [l for l in linhas if l["FINAL_STATE"] == CAPABILITY_BLOCK and l["STATE_A"] != LC.CAPABILITY_BLOCK]
    stale = [{"SOURCE_ID": l["SOURCE_ID"], "LIVRO": "B", "ESTADO_DESCARTADO": l["STATE_B"],
              "FINAL": l["FINAL_STATE"], "PORQUE": l["FINAL_REASON"][:160]}
             for l in linhas if l["STATE_B"] and _mapa(l["STATE_B"]) != l["FINAL_STATE"]
             and l["STATE_B"] in (LC.READY_FOR_COLLECTION, LC.CONTRACTED_CANARY_FAILED)]
    stale += [{"SOURCE_ID": l["SOURCE_ID"], "LIVRO": "B2", "ESTADO_DESCARTADO": l["STATE_B2"],
               "FINAL": l["FINAL_STATE"], "PORQUE": l["FINAL_REASON"][:160]}
              for l in linhas if l["STATE_B2"] and _mapa(l["STATE_B2"]) != l["FINAL_STATE"]
              and l["STATE_B2"] in (LC.READY_FOR_COLLECTION, LC.CAPABILITY_BLOCK)]
    stale += [{"SOURCE_ID": l["SOURCE_ID"], "LIVRO": "A", "ESTADO_DESCARTADO": l["STATE_A"],
               "FINAL": l["FINAL_STATE"], "PORQUE": l["FINAL_REASON"][:160]}
              for l in linhas if l["STATE_A"] and _mapa(l["STATE_A"]) != l["FINAL_STATE"]
              and l["STATE_A"] in (LC.READY_FOR_COLLECTION, LC.RECONCILIATION_REQUIRED, LC.RETRY_AFTER)]

    return {
        "DATASET": "RECONCILIACAO-V1",
        "LEI": ("uma SOURCE_ID, um estado final, sustentado pela prova em disco. Nao se escolhe livro, "
                "nao se somam estados, o mais recente nao vence. Bloqueio comprovado preserva-se; "
                "READY exige os quatro passos; NAO SEI e resultado."),
        "GERADO_EM": agora(),
        "LIVROS": {
            "A": {"COMMIT": ctx["COMMITS"]["A"], "FILE": "curadoria/LIFECYCLE-LEDGER-V1.json",
                  "SOURCES": len(A), "TRANSICOES": len(ctx["A"]["TRANSICOES"]),
                  "POR_ESTADO": dict(Counter(t["NEW_STATE"] for t in ctx["_ULT"]["A"].values()))},
            "B": {"COMMIT": ctx["COMMITS"]["B"], "FILE": "curadoria/LIFECYCLE-LEDGER-V1.json",
                  "SOURCES": len(B), "TRANSICOES": len((ctx.get("B") or {}).get("TRANSICOES", [])),
                  "POR_ESTADO": dict(Counter(t["NEW_STATE"] for t in ctx["_ULT"]["B"].values()))},
            "B2": {"COMMIT": ctx["COMMITS"]["B2"], "FILE": "curadoria/LIFECYCLE-LEDGER-V1.json",
                   "SOURCES": len(B2), "TRANSICOES": len((ctx.get("B2") or {}).get("TRANSICOES", [])),
                   "POR_ESTADO": dict(Counter(t["NEW_STATE"] for t in ctx["_ULT"]["B2"].values()))},
        },
        "CONJUNTOS": {"UNIAO_A_B": len(A | B), "COMUNS_A_B": len(A & B), "SO_A": len(A - B), "SO_B": len(B - A),
                      "SO_B2": len(B2 - (A | B)), "UNIAO_A_B_B2": len(A | B | B2),
                      "IDENTIDADES_FINAIS": len(linhas)},
        "POR_ESTADO_FINAL": {e: conta.get(e, 0) for e in ESTADOS_FINAIS},
        "BLOQUEIOS": {
            # relativo ao livro A DESTE censo: depois de aplicar, A ja os tem e o numero e 0.
            "POLICY_BLOCK_IMPORTED": len(importados_p),
            "CAPABILITY_BLOCK_IMPORTED": len(importados_c),
            # lido do proprio livro A: as linhas de bloqueio que entraram com IMPORTADO_DE.
            "POLICY_BLOCK_IMPORTED_NO_LIVRO": sum(1 for t in ctx["A"]["TRANSICOES"]
                                                  if "IMPORTADO_DE" in t and t["NEW_STATE"] == LC.POLICY_BLOCK),
            "CAPABILITY_BLOCK_IMPORTED_NO_LIVRO": sum(1 for t in ctx["A"]["TRANSICOES"]
                                                      if "IMPORTADO_DE" in t and t["NEW_STATE"] == LC.CAPABILITY_BLOCK),
            "BLOCKS_REJECTED_AS_STALE": ctx["_BLOQUEIOS"]["REJEITADOS"],
            "BLOCKS_SUPERSEDED_BY_LATER_EVIDENCE": ctx["_BLOQUEIOS"]["SUPERADOS"],
        },
        "STALE_STATES_DISCARDED": stale,
        "SOURCE_ID_DUPLICATES": duplicados,
        "READY_RECONTADO": {
            "READY_CURRENT": [l["SOURCE_ID"] for l in ready_cur],
            "READY_CURRENT_COM_REVISAO_HUMANA": [l["SOURCE_ID"] for l in ready_cur if l.get("REVISAO_HUMANA")],
            "READY_LEGACY": [l["SOURCE_ID"] for l in linhas if l["FINAL_STATE"] == READY_LEGACY],
            "CANDIDATOS_READY_RECUSADOS": [
                {"SOURCE_ID": l["SOURCE_ID"], "FINAL": l["FINAL_STATE"], "WHY": l["FINAL_REASON"][:200]}
                for l in linhas if l["FINAL_STATE"] not in (READY_CURRENT, READY_LEGACY)
                and LC.READY_FOR_COLLECTION in (l["STATE_A"], l["STATE_B"], l["STATE_B2"])],
        },
        "LINHAS": linhas,
    }


def _mapa(estado_lifecycle: str) -> str:
    if estado_lifecycle == LC.READY_FOR_COLLECTION:
        return "READY_*"
    if estado_lifecycle == LC.RETRY_AFTER:
        return RETRY
    if estado_lifecycle in FAMILIA_NOT_READY:
        return NOT_READY
    return estado_lifecycle


# ---------------------------------------------------------------------------
# APLICAR — evoluir o livro A por acrescimo, com trilho. Idempotente.
# ---------------------------------------------------------------------------
def plano(doc: dict, ctx: dict) -> list[dict]:
    """As transicoes a acrescentar ao livro A, por SOURCE_ID, SEM gravar.
    Cada item: {SOURCE_ID, NOVO, REASON, EVIDENCE_REF, OWNER, EXTRA, NEXT}."""
    ult_a = ultimos(ctx["A"])
    plano_: list = []
    for l in doc["LINHAS"]:
        sid = l["SOURCE_ID"]
        alvo = l["LIFECYCLE_TARGET"]
        atual = (ult_a.get(sid) or {}).get("NEW_STATE")
        if atual == alvo:
            continue
        estado_simulado = atual
        # 1. fonte desconhecida de A: importar a cadeia do livro que a conhece.
        if atual is None:
            origem, chave = _livro_de_origem(l, ctx)
            if origem:
                for t in ctx["_HIST"][origem].get(chave) or []:
                    plano_.append({"SOURCE_ID": sid, "NOVO": t["NEW_STATE"], "REASON": t["REASON"],
                                   "EVIDENCE_REF": t.get("EVIDENCE_REF"), "OWNER": t.get("OWNER", LC.OWNER_CURATOR),
                                   "NEXT": t.get("NEXT_ATTEMPT_AT"),
                                   "EXTRA": {"IMPORTADO_DE": {"LIVRO": origem, "COMMIT": ctx["COMMITS"][origem],
                                                              "CHAVE_ORIGINAL": chave,
                                                              "OBSERVED_AT_ORIGINAL": t.get("OBSERVED_AT"),
                                                              "MISSAO": MISSAO}}})
                    estado_simulado = t["NEW_STATE"]
        if estado_simulado == alvo:
            continue
        # 2. a decisao da reconciliacao, com o trilho da FASE 6.
        for passo in _caminho(estado_simulado, alvo):
            plano_.append({"SOURCE_ID": sid, "NOVO": passo, "REASON": ("reconciliacao: " + l["FINAL_REASON"])[:400],
                           "EVIDENCE_REF": _ref_da_decisao(l, ctx), "OWNER": LC.OWNER_CURATOR, "NEXT": None,
                           "EXTRA": {"RECONCILIACAO": {
                               "MISSAO": MISSAO, "PREVIOUS_STATE": estado_simulado, "FINAL_STATE": l["FINAL_STATE"],
                               "STATE_A": l["STATE_A"], "STATE_B": l["STATE_B"], "STATE_B2": l["STATE_B2"],
                               "EVIDENCE_SOURCE": (l.get("LATEST_VALID_EVIDENCE") or {}).get("FONTE"),
                               "EVIDENCE_TIMESTAMP": (l.get("LATEST_VALID_EVIDENCE") or {}).get("QUANDO"),
                               "EVIDENCE_COMMIT": (l.get("LATEST_VALID_EVIDENCE") or {}).get("COMMIT"),
                               "RECONCILIATION_REASON": l["FINAL_REASON"][:400]}}})
            estado_simulado = passo
    return plano_


def _livro_de_origem(l: dict, ctx: dict) -> tuple[str | None, str | None]:
    for k in l["CHAVES_NOS_LIVROS"]:
        if k in ctx["_HIST"]["B"]:
            return "B", k
    for k in l["CHAVES_NOS_LIVROS"]:
        if k in ctx["_HIST"]["B2"]:
            return "B2", k
    return None, None


def _caminho(de: str | None, para: str) -> list[str]:
    """O lifecycle so promove a READY a partir de CANARY_PENDING/REPAIRING, e
    RETRY_AFTER le-se como «adiada a caminho do canario»: passa por CANARY_PENDING."""
    if para in (LC.READY_FOR_COLLECTION, LC.RETRY_AFTER) and de not in LC.PODEM_PROMOVER:
        return [LC.CANARY_PENDING, para]
    return [para]


def _ref_da_decisao(l: dict, ctx: dict) -> str:
    ev = l.get("LATEST_VALID_EVIDENCE") or {}
    ref = ev.get("REF") or ""
    return "%s:%s@%s%s" % (MISSAO, ev.get("FONTE", "sem prova").replace(" ", "_"),
                           ev.get("COMMIT", "?"), (":" + ref) if ref else "")


def verificar_plano(plano_: list, ctx: dict) -> list[str]:
    """Simula cada transicao pelas regras de lifecycle ANTES de gravar. Falhar
    fechado: uma cadeia ilegal (READY sem prova, promocao fora de ordem) nao
    entra — e a fonte fica dita no relatorio."""
    est = {s: t["NEW_STATE"] for s, t in ultimos(ctx["A"]).items()}
    faltas = []
    for p in plano_:
        ok, porque = LC.transicao_permitida(est.get(p["SOURCE_ID"]), p["NOVO"], p["OWNER"])
        if ok and p["NOVO"] == LC.READY_FOR_COLLECTION and not p["EVIDENCE_REF"]:
            ok, porque = False, "READY exige EVIDENCE_REF"
        if not ok:
            faltas.append("%s: %s -> %s: %s" % (p["SOURCE_ID"], est.get(p["SOURCE_ID"]), p["NOVO"], porque))
            continue
        est[p["SOURCE_ID"]] = p["NOVO"]
    return faltas


def aplicar(doc: dict, ctx: dict) -> dict:
    """Grava o plano no livro A por `lifecycle.registar`. Devolve o resumo.
    Fontes cuja cadeia e ilegal ficam de fora, nomeadas."""
    p = plano(doc, ctx)
    faltas = verificar_plano(p, ctx)
    ilegais = {f.split(":")[0] for f in faltas}
    antes = len(LC._ler_bruto()["TRANSICOES"])
    gravadas = 0
    for t in p:
        if t["SOURCE_ID"] in ilegais:
            continue
        LC.registar(t["SOURCE_ID"], t["NOVO"], t["REASON"], owner=t["OWNER"],
                    evidence_ref=t["EVIDENCE_REF"], next_attempt_at=t.get("NEXT"), extra=t["EXTRA"])
        gravadas += 1
    depois = len(LC._ler_bruto()["TRANSICOES"])
    return {"APLICADO_EM": agora(), "LINHAS_ANTES": antes, "LINHAS_DEPOIS": depois,
            "APENDIDAS": gravadas, "PLANEADAS": len(p),
            "CADEIAS_ILEGAIS_NAO_IMPORTADAS": sorted(ilegais), "FALTAS": faltas}


def main(argv: list | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    ctx = carregar_contexto()
    if not ctx["B"] or not ctx["B2"]:
        print("LIVRO B ou B2 ilegivel por git show (%s / %s). NAO SE INVENTA O OUTRO LIVRO." % (REF_B, REF_B2))
        return 1
    doc = censo(ctx)
    if "--aplicar" in argv:
        doc["APLICADO"] = aplicar(doc, ctx)
        # o censo relido sobre o livro evoluido — e o que fica escrito.
        ctx2 = carregar_contexto()
        doc2 = censo(ctx2)
        doc2["APLICADO"] = doc["APLICADO"]
        doc2["APLICADO"]["SEGUNDA_PASSAGEM_PLANEIA"] = len(plano(doc2, ctx2))
        doc = doc2
    SAIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for k, v in doc["POR_ESTADO_FINAL"].items():
        print("%-18s %d" % (k, v))
    print("IDENTIDADES_FINAIS  %d" % doc["CONJUNTOS"]["IDENTIDADES_FINAIS"])
    print("BLOQUEIOS           %s" % json.dumps({k: (v if isinstance(v, int) else len(v))
                                                for k, v in doc["BLOQUEIOS"].items()}))
    if "APLICADO" in doc:
        print("APLICADO            %s" % json.dumps({k: v for k, v in doc["APLICADO"].items() if k != "FALTAS"}))
    print("escrito: %s" % SAIDA.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
