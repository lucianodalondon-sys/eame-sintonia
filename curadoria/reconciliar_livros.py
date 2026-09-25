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

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import collection_gate as CG  # noqa: E402
import lifecycle as LC        # noqa: E402
import ready_split as RS      # noqa: E402

MISSAO = "RECONCILIACAO-V1"
REF_B = "f98f234c"      # aquisicao-detalhe-v1, arvore final
REF_B2 = "63b71421"     # candidate-bridge-v1, ledger com os 75 bloqueios

# ---------------------------------------------------------------------------
# LIVRO C — O BOT DE FONTES QUE ESTA VIVO (source-curator-service-v1).
#
# Os outros tres livros sao fotografias de missoes fechadas. C nao: o
# supervisor do Source Curator corre no SO e continua a escrever. Medido em
# 2026-09-22: C tem 437 fontes e 1008 transicoes contra as 278/754 desta
# arvore — 277 fontes que esta linha nunca viu.
#
#     UM BOT QUE ESCREVE NUM LIVRO QUE NINGUEM LE E TRABALHO PERDIDO.
#
# Le-se por `git show REF_C` — copia CONGELADA, nunca o ficheiro vivo: o
# supervisor pode gravar a meio da leitura e dar-nos meio livro.
#
# C entra pelas MESMAS leis dos outros: bloqueio dele preserva-se pela
# evidencia (e cede a prova posterior na historia), fonte que so ele conhece
# importa-se com a cadeia inteira, e uma promocao dele so vence esta arvore
# se tiver medido DEPOIS e a prova do canario existir mesmo. C NAO E DONO DO
# LIVRO — e o quarto testemunho, nao o juiz.
# ---------------------------------------------------------------------------
BRANCH_C = "source-curator-service-v1"
REF_C_MEDIDO = "216dd6db"   # o HEAD do bot quando esta ponte foi medida (2026-09-22)
LIVROS = ("A", "B", "B2", "C")


def ref_do_bot(branch: str = BRANCH_C) -> str:
    """O HEAD do bot AGORA — nao um commit escrito a mao.

    ⚠️ UMA PONTE PRESA A UM COMMIT FIXO ESTA MORTA NO DIA SEGUINTE. Se este
    valor fosse a constante `REF_C_MEDIDO`, o censo de hoje ficaria verde para
    sempre e o trabalho que o bot fizer amanha nunca atravessaria — que e
    exactamente o defeito que esta missao veio corrigir.

    Le-se a branch, nao a worktree do bot: o supervisor esta vivo e o ficheiro
    dele pode estar a meio de uma gravacao. `REF_C_MEDIDO` fica so como
    registo do corte desta medicao.
    """
    try:
        r = subprocess.run(["git", "rev-parse", "--short", branch], cwd=str(RAIZ),
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return REF_C_MEDIDO
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else REF_C_MEDIDO


REF_C = ref_do_bot()

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
# Um `git show` por ficheiro custa ~0.4 s, e `carregar_contexto` faz sete —
# 2.6 s por travessia. Num observador que corre de 20 em 20 segundos isso
# passa a ser a maior parte do trabalho, e e trabalho repetido: B e B2 sao
# commits FIXOS, e o conteudo de um commit nunca muda. A chave inclui o ref,
# por isso quando o ref muda (o HEAD do bot muda) a entrada e outra — o cache
# nao pode servir livro velho.
_CACHE_GIT: dict = {}


def do_git(ref: str, caminho: str) -> dict | list | None:
    chave = (ref, caminho)
    if chave in _CACHE_GIT:
        return _CACHE_GIT[chave]
    try:
        r = subprocess.run(["git", "show", "%s:%s" % (ref, caminho)], cwd=str(RAIZ),
                           capture_output=True, text=True, encoding="utf-8", timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0 or not r.stdout:
        return None
    d = json.loads(r.stdout)
    _CACHE_GIT[chave] = d
    return d


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


# ---------------------------------------------------------------------------
# LIVRO C COMO ENTRADA EXPLICITA — o corte congelado do servico vivo.
#
# `git show REF_C` so ve o que o bot COMMITOU. O servico vivo escreve os livros
# no disco e nao os commita: o que ficou por commitar nunca atravessaria. Por
# isso C aceita tambem um CORTE: um directorio com a copia dos livros e um
# CORTE.json que guarda o sha256 de cada um (feito por
# ferramentas/unificacao/congelar_livros_do_servico.py). O sha256 e verificado
# aqui — um corte que nao bate com o seu proprio manifesto nao entra.
#
# A regra de reconciliacao NAO muda: C continua a ser o quarto testemunho.
# ---------------------------------------------------------------------------
CORTE_MANIFESTO = "CORTE.json"
CORTE_LIVROS = ("LIFECYCLE-LEDGER-V1.json", "LIFECYCLE-EVIDENCE-V1.json",
                "italy_contracts_curator.json")


class CorteInvalido(Exception):
    """O corte nao tem manifesto, falta-lhe um livro, ou o sha256 nao bate."""


def ler_corte_do_servico(pasta: Path) -> dict:
    """{LIVRO, EVIDENCIAS, CONTRATOS, SHA256, MANIFESTO} — ou `CorteInvalido`."""
    pasta = Path(pasta)
    man_p = pasta / CORTE_MANIFESTO
    if not man_p.exists():
        raise CorteInvalido("sem %s em %s" % (CORTE_MANIFESTO, pasta))
    man = json.loads(man_p.read_text(encoding="utf-8"))
    shas = man.get("SHA256") or {}
    docs = {}
    for nome in CORTE_LIVROS:
        f = pasta / nome
        if not f.exists():
            if nome == "LIFECYCLE-LEDGER-V1.json":
                raise CorteInvalido("o corte nao tem o livro %s" % nome)
            docs[nome] = None
            continue
        b = f.read_bytes()
        real = hashlib.sha256(b).hexdigest()
        if shas.get(nome) != real:
            raise CorteInvalido("%s: sha256 %s != manifesto %s" % (nome, real[:12], str(shas.get(nome))[:12]))
        docs[nome] = json.loads(b.decode("utf-8"))
    evid = docs["LIFECYCLE-EVIDENCE-V1.json"] or {"PROVAS": []}
    contr = docs["italy_contracts_curator.json"] or {"FONTES": []}
    return {
        "LIVRO": docs["LIFECYCLE-LEDGER-V1.json"],
        "EVIDENCIAS": {x["EVIDENCE_REF"]: x for x in evid.get("PROVAS", [])},
        "CONTRATOS": {x["SOURCE_ID"]: x for x in contr.get("FONTES", [])},
        "SHA256": shas["LIFECYCLE-LEDGER-V1.json"],
        "MANIFESTO": man,
    }


def carregar_contexto(*, ref_b: str = REF_B, ref_b2: str = REF_B2,
                      ref_c: str = REF_C, corte_c: Path | None = None) -> dict:
    """Tudo o que a decisao precisa, lido UMA vez. Em testes, constroi-se a mao.

    `corte_c`: directorio de um corte congelado do servico. Quando dado,
    substitui o `git show REF_C` para o livro, as provas e os contratos de C."""
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

    corte = ler_corte_do_servico(corte_c) if corte_c else None
    if corte:
        livro_c = corte["LIVRO"]
        evid_c = {"PROVAS": list(corte["EVIDENCIAS"].values())}
        contratos_c = {"FONTES": list(corte["CONTRATOS"].values())}
        commit_c = "CORTE:%s" % corte["SHA256"][:12]
    else:
        livro_c = do_git(ref_c, "curadoria/LIFECYCLE-LEDGER-V1.json")
        evid_c = do_git(ref_c, "curadoria/LIFECYCLE-EVIDENCE-V1.json") or {"PROVAS": []}
        contratos_c = do_git(ref_c, "curadoria/italy_contracts_curator.json") or {}
        commit_c = ref_c

    return {
        "COMMITS": {"A": _head_curto(), "B": ref_b, "B2": ref_b2, "C": commit_c},
        "CORTE_C": ({"SHA256": corte["SHA256"], "MANIFESTO": corte["MANIFESTO"]} if corte else None),
        "A": LC._ler_bruto(),
        "B": do_git(ref_b, "curadoria/LIFECYCLE-LEDGER-V1.json"),
        "B2": do_git(ref_b2, "curadoria/LIFECYCLE-LEDGER-V1.json"),
        "C": livro_c,
        "EVIDENCIA_C": {p["EVIDENCE_REF"]: p for p in evid_c.get("PROVAS", [])},
        "CONTRATOS_C": {c["SOURCE_ID"]: c for c in contratos_c.get("FONTES", [])},
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
    for nome in LIVROS:
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
    for nome in ("B2", "A", "B", "C"):
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


# ⚠️ AUTH_BLOCK — CLASSE ANTES DO ROTULO (missao 5, UNIFICACAO-V1). O worker do
# servico escreve `AUTH_BLOCK` (muro de login) desde 22/09; os vereditos so
# conheciam POLICY/CAPABILITY e diziam «estado fora do vocabulario» -> UNKNOWN.
# Medido no corte de 23/09: 5 fontes (IT-T12-035/046/055/072/078) caiam em
# UNKNOWN so por isto. A classe e a de _CLASSE_DE (decisao ja declarada ali):
# CAPABILITY_BLOCK — «fonte boa, aquisicao impossivel com o que a casa tem».
# O rotulo AUTH_BLOCK mantem-se no livro (ver _alvo_lifecycle).
_AUTH_COMO_CAPACIDADE = "AUTH_BLOCK (muro de login) lido como CAPABILITY_BLOCK: credencial em falta e capacidade em falta"


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
    if e == LC.AUTH_BLOCK:
        return CAPABILITY_BLOCK, "B: " + _AUTH_COMO_CAPACIDADE, pb
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
        if RS.e_corrente(r["REGUA"]):
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
    if e == LC.AUTH_BLOCK:
        return CAPABILITY_BLOCK, "A: " + _AUTH_COMO_CAPACIDADE, {}
    if e in FAMILIA_NOT_READY:
        return NOT_READY, "A: %s (%s)" % (e, (t.get("REASON") or "")[:70]), {}
    return UNKNOWN, "A: estado fora do vocabulario: %s" % e, {}


def veredito_c(sid: str, ctx: dict) -> tuple[str | None, str, dict]:
    """O que o livro do BOT prova, por si — pela MESMA regua de A.

    O bot escreve o estado e a referencia da prova. A referencia tem de
    RESOLVER no manifesto de evidencias dele: uma promocao que cita uma prova
    que o proprio livro nao tem nao e uma promocao, e um carimbo. Medido nas
    8 promocoes do bot de 2026-09-20: todas citam
    `MISSAO-04:curadoria/READY-FOR-COLLECTION-V1.json@959ae46a`, que nao e
    uma linha do manifesto de canarios — zero campos, nenhum item aberto.

        PROMOCAO SEM PROVA DE CANARIO NAO PROMOVE.
    """
    t = ctx["_ULT"]["C"].get(sid)
    if not t:
        return None, "C nao conhece a fonte", {}
    e = t["NEW_STATE"]
    if e == LC.READY_FOR_COLLECTION:
        promo = RS.ultima_promocao(sid, ctx.get("C"))
        ref = (promo or {}).get("EVIDENCE_REF") or ""
        ev = ctx.get("EVIDENCIA_C", {}).get(ref)
        prova_do_bot_resolve = ev is not None
        if not prova_do_bot_resolve:
            return (UNKNOWN, "C: READY citando prova que o manifesto do bot nao tem (%s) — "
                    "promocao sem canario nao promove" % (ref[:60] or "sem EVIDENCE_REF"), {})
        r = RS.passos_da_promocao(promo, ev, ctx.get("CONTRATOS_C", {}).get(sid))
        if RS.e_corrente(r["REGUA"]):
            return READY_CURRENT, "C: " + r["PORQUE"], r
        return READY_LEGACY, "C: " + r["PORQUE"], r
    if e == LC.DEGRADED:
        return DEGRADED, "C: DEGRADED", {}
    if e == LC.RETRY_AFTER:
        return RETRY, "C: RETRY_AFTER", {}
    if e == LC.UNKNOWN:
        return UNKNOWN, "C: UNKNOWN", {}
    if e in (LC.POLICY_BLOCK, LC.CAPABILITY_BLOCK):
        return e, "C: %s" % e, {}
    if e == LC.AUTH_BLOCK:
        return CAPABILITY_BLOCK, "C: " + _AUTH_COMO_CAPACIDADE, {}
    if e in FAMILIA_NOT_READY:
        return NOT_READY, "C: %s (%s)" % (e, (t.get("REASON") or "")[:70]), {}
    return UNKNOWN, "C: estado fora do vocabulario: %s" % e, {}


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
    tC = None
    for k in chaves_originais:
        tC = ctx["_ULT"]["C"].get(k) or tC

    linha = {
        "SOURCE_ID": chave, "IDENTITY_KIND": tipo,
        "CHAVES_NOS_LIVROS": sorted(set(chaves_originais)),
        "STATE_A": tA["NEW_STATE"] if tA else None,
        "STATE_B": tB["NEW_STATE"] if tB else None,
        "STATE_B2": tB2["NEW_STATE"] if tB2 else None,
        "STATE_C": tC["NEW_STATE"] if tC else None,
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

    vC, pC, passosC = veredito_c(chave, ctx)
    linha["DETAIL_PROOF_C"] = passosC.get("PASSOS") if passosC else None
    linha["CANARY_C"] = ({"EVIDENCE_REF": tC.get("EVIDENCE_REF"),
                          "RESOLVE_NO_MANIFESTO_DO_BOT":
                              (tC.get("EVIDENCE_REF") or "") in ctx.get("EVIDENCIA_C", {}),
                          "OBSERVED_AT": tC.get("OBSERVED_AT")} if tC else None)

    final, porque, ev_final = _combinar(chave, tA, tB, vA, pA, vB, pB, ctx)
    final, porque, ev_final = _degrau_c(chave, tA, tC, vC, pC, final, porque, ev_final, ctx)
    if final == READY_CURRENT:
        falta_dono = dono_do_contrato(chave, ctx)
        if falta_dono:
            linha["DONO_DO_CONTRATO"] = falta_dono
            final, porque = NOT_READY, falta_dono + " | antes: " + porque
    linha.update(FINAL_STATE=final, FINAL_REASON=porque, LATEST_VALID_EVIDENCE=ev_final,
                 LIFECYCLE_TARGET=_alvo_lifecycle(final, tA, tB, tB2, tC))
    if final == READY_CURRENT:
        linha["REVISAO_HUMANA"] = _item_parece_seccao(chave, ctx)
    return linha


def dono_do_contrato(sid: str, ctx: dict) -> str | None:
    """`None` = o bot mede o MESMO contrato que o portao le. Texto = nao mede, e porque.

    ⚠️ UM SO DONO DO CONTRATO (B2, 2026-09-23). Prova viva T02077: a
    coordenacao pediu ao bot que re-medisse IT-T5-041 e ele respondeu «BLOCK
    VALIDATE_ROUTE sem contrato» — nenhuma transicao nova, e o portao ficou com
    ela ELIGIBLE. O READY dela nasceu nesta arvore (listagem provada a 21/09),
    com um contrato que o bot nao tem. Medido no mesmo dia: as 8 elegiveis tem
    TODAS um contrato diferente no bot (o bot mede a homepage; esta arvore, a
    listagem afinada). Uma fonte que o bot nao consegue re-medir e uma fonte
    que nunca sai do portao — nem quando o sitio muda de casa.

        O PORTAO NAO TEM ELEGIVEL O QUE O BOT NAO CONSEGUE MEDIR.

    Contrato em falta NESTA arvore e presente no bot nao e falta de dono:
    `importar_contratos_do_bot` trá-lo nesta mesma volta, igual.

    ⚠️ LIVRO DE CONTRATOS DO BOT ILEGIVEL NAO E «O BOT NAO TEM». Com
    `CONTRATOS_C` vazio (ficheiro ausente, corte sem contratos) a regra nao
    se aplica — senao uma falha de leitura despromovia o portao inteiro.
    """
    CC = ctx.get("CONTRATOS_C") or {}
    if not CC:
        return None
    cC = CC.get(sid)
    cA = (ctx.get("CONTRATOS_A") or {}).get(sid)
    if cC is None:
        return ("DONO_DO_CONTRATO: o bot nao tem contrato para esta fonte — nao a consegue "
                "re-medir; o READY desta arvore fica sem quem o confirme")
    if cA is not None and _aquisicao(cA) != _aquisicao(cC):
        rota = lambda c: (c.get("ACQUISITION") or {}).get("INDEX_URL") or c.get("CANONICAL_ENTRY_URL")
        return ("DONO_DO_CONTRATO: o bot mede outra rota (%s) que nao a que o portao le (%s) — "
                "dois donos para o mesmo contrato" % (rota(cC), rota(cA)))
    return None


def _item_parece_seccao(sid: str, ctx: dict) -> str | None:
    """Heuristica DECLARADA, que nao muda o estado: o endereco do item aberto
    tem menos de 4 palavras e nenhum digito (ex.: /lavora-con-noi,
    /articoli-e-pubblicazioni/). Serve para excluir da micro-colheita sugerida
    e pedir olho humano — nao para condenar.

    ⚠️ A REGRA NAO MORA AQUI. Mora em `collection_gate`, que e o portao de
    admissao da Collection. Este ficheiro chama-a: se houvesse duas copias, uma
    delas envelhecia sozinha e o censo passaria a discordar do portao sobre
    quem pode ser colhido."""
    return CG.revisao_humana_do_url(
        CG.url_do_item_aberto(sid, livro=ctx["A"], evidencias=ctx["EVIDENCIA_A"]))


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


def _degrau_c(chave, tA, tC, vC, pC, final, porque, ev, ctx) -> tuple[str, str, dict | None]:
    """O testemunho do BOT, por cima do que A e B ja decidiram.

    Quatro leis, por esta ordem:

    1. FONTE QUE SO O BOT CONHECE — e ele que a traz, com a cadeia dele. Sao
       as 277 que esta arvore nunca viu.
    2. LEGACY NAO SE LAVA — se a fonte ja e READY nesta casa, o bot dizer
       READY nao lhe sobe a regua. Uma fonte promovida pela regua antiga fica
       READY_LEGACY ainda que o bot a chame READY. A reconciliacao nao e
       maquina de lavar: `LEGACY_LEAK` tem de ser 0.
    3. O BOT SO VENCE QUEM MEDIU ANTES DELE, E SO COM PROVA QUE RESOLVE. Se
       esta arvore mediu depois, o bot nao desfaz a medicao; e se a prova dele
       nao esta no manifesto dele, nao vence coisa nenhuma.
    4. UM PEDIDO NAO E UM VEREDITO. `RECONCILIATION_REQUIRED` do bot quer
       dizer «remede isto», nao «isto esta errado». Quando esta arvore ja
       remediu DEPOIS, o pedido esta cumprido — nao derruba o resultado.

    O bot NUNCA escreve elegibilidade. Devolve estado e prova; quem decide se
    a fonte entra na Collection e `collection_gate`, sempre, a ler a regua.
    """
    if vC is None:
        return final, porque, ev
    evC = {"FONTE": "livro C (bot)", "QUANDO": _quando(tC),
           "COMMIT": ctx["COMMITS"].get("C", "?"), "REF": (tC or {}).get("EVIDENCE_REF")}
    prova_resolve = ((tC or {}).get("EVIDENCE_REF") or "") in ctx.get("EVIDENCIA_C", {})

    # 1. so o bot a conhece.
    if tA is None and porque.startswith("nenhum livro tem prova"):
        return vC, pC, evC

    # 2. LEGACY NAO SE LAVA.
    if final in (READY_LEGACY, READY_CURRENT) and vC in (READY_LEGACY, READY_CURRENT):
        return final, porque + " | C concorda (%s), e a regua nao sobe pelo bot" % vC, ev

    # 3 e 4. o bot mediu depois? com prova a resolver?
    if tA is not None and _quando(tC) <= _quando(tA):
        return final, porque + " | C (%s, %s) mediu ANTES desta arvore — nao derruba" % (
            vC, _quando(tC)[:19]), ev
    if vC in (READY_CURRENT, READY_LEGACY) and not prova_resolve:
        return final, porque + " | C diz READY sem prova no manifesto dele — nao promove", ev
    return vC, pC + " | C mediu depois (%s)" % _quando(tC)[:19], evC


def _alvo_lifecycle(final: str, tA: dict | None, tB: dict | None = None,
                    tB2: dict | None = None, tC: dict | None = None) -> str:
    if final in (READY_CURRENT, READY_LEGACY):
        return LC.READY_FOR_COLLECTION
    if final == CAPABILITY_BLOCK and any(x is not None and x["NEW_STATE"] == LC.AUTH_BLOCK
                                         for x in (tA, tC, tB, tB2)):
        # a classe e CAPABILITY, o rotulo continua AUTH_BLOCK: o livro nao
        # perde que a falta e uma credencial (e nao um adaptador).
        return LC.AUTH_BLOCK
    if final == RETRY:
        return LC.RETRY_AFTER
    if final in (DEGRADED, POLICY_BLOCK, CAPABILITY_BLOCK, UNKNOWN):
        return final
    # NOT_READY: manter o passo pendente que o livro que conhece a fonte ja
    # diz (A primeiro; se A nao a conhece, o livro de origem). Se o que se
    # dizia era READY, o passo pendente e remedir: CANARY_PENDING.
    for t in (tA, tB, tB2, tC):
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
    ctx["_ULT"] = {n: ultimos(ctx.get(n)) for n in LIVROS}
    ctx["_HIST"] = {n: historias(ctx.get(n)) for n in LIVROS}
    ctx["_BLOQUEIOS"] = {"REJEITADOS": [], "SUPERADOS": []}

    A, B, B2, C = (set(ctx["_ULT"][n]) for n in LIVROS)
    grupos: dict = defaultdict(list)
    tipos: dict = {}
    duplicados = []
    for k in sorted(A | B | B2 | C):
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
    # Um estado e DESCARTADO quando o livro o afirmava e a decisao final o
    # contradiz. READY de um livro que fica READY_LEGACY/READY_CURRENT nao foi
    # descartado: e a mesma prontidao, com a regua lida.
    stale = []
    for nome, campo in (("A", "STATE_A"), ("B", "STATE_B"), ("B2", "STATE_B2"), ("C", "STATE_C")):
        for l in linhas:
            e = l[campo]
            if e and not _bate(e, l["FINAL_STATE"]):
                stale.append({"SOURCE_ID": l["SOURCE_ID"], "LIVRO": nome, "ESTADO_DESCARTADO": e,
                              "FINAL": l["FINAL_STATE"], "PORQUE": l["FINAL_REASON"][:160]})

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
            "C": {"COMMIT": ctx["COMMITS"].get("C"), "FILE": "curadoria/LIFECYCLE-LEDGER-V1.json",
                  "SOURCES": len(C), "TRANSICOES": len((ctx.get("C") or {}).get("TRANSICOES", [])),
                  "POR_ESTADO": dict(Counter(t["NEW_STATE"] for t in ctx["_ULT"]["C"].values()))},
        },
        "BOT_SNAPSHOT": _corte_do_bot(ctx),
        "TELEMETRIA_DA_PONTE": _telemetria(linhas, ctx),
        "CONJUNTOS": {"UNIAO_A_B": len(A | B), "COMUNS_A_B": len(A & B), "SO_A": len(A - B), "SO_B": len(B - A),
                      "SO_B2": len(B2 - (A | B)), "UNIAO_A_B_B2": len(A | B | B2),
                      "SO_C": len(C - (A | B | B2)), "SO_C_VS_A": len(C - A), "COMUNS_A_C": len(A & C),
                      "SO_A_VS_C": len(A - C), "UNIAO_TODOS": len(A | B | B2 | C),
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


def _corte_do_bot(ctx: dict) -> dict:
    """O CORTE LOGICO. O bot nao se para para o ler — fecha-se um corte e
    reconcilia-se SO o que esta deste lado dele.

    O que o supervisor escrever DEPOIS do corte nao entra retroativamente:
    atravessa a ponte futura, na proxima volta. Sem isto, «reconciliado» seria
    uma palavra sobre um alvo em movimento.

    TRANSITION_MAX_ID e a posicao da ultima transicao do livro congelado (o
    livro e append-only, logo a posicao e um marco estavel).
    """
    livro_c = ctx.get("C") or {}
    ts = livro_c.get("TRANSICOES", [])
    return {
        "BOT_SNAPSHOT_HEAD": ctx["COMMITS"].get("C"),
        "BOT_SNAPSHOT_TIME": max((t.get("OBSERVED_AT") or "") for t in ts) if ts else None,
        "BOT_SNAPSHOT_TRANSITION_MAX_ID": len(ts),
        "BOT_SNAPSHOT_SOURCES": len(ctx["_ULT"]["C"]),
        "LEITURA": (("corte congelado com sha256 verificado: %s" % ctx["CORTE_C"]["SHA256"])
                    if ctx.get("CORTE_C") else
                    ("git show — copia congelada. O ficheiro vivo do bot NAO e lido: "
                     "o supervisor esta a correr e pode gravar a meio da leitura.")),
        "POSTERIOR_AO_CORTE": "atravessa a ponte futura; nao entra retroativo nesta reconciliacao",
    }


def _telemetria(linhas: list, ctx: dict) -> dict:
    """O funil, com as recusas DISCRIMINADAS POR MOTIVO.

        BOT_READY -> CANONICAL_RECONCILED -> (o gate decide)

    Quem esconde as recusas transforma um funil num numero bonito. Cada fonte
    que o bot diz READY e que nao chega ao fim aparece aqui com o motivo.

    ⚠️ Esta funcao NAO diz COLLECTION_ELIGIBLE. Nao e ela que decide, e nao ha
    aqui uma segunda copia da regua: quem responde a essa pergunta e
    `collection_gate.avaliar`, e so ele. O bot alimenta conhecimento; a
    elegibilidade continua a ser uma consequencia lida pelo portao.
    """
    bot_ready = [l for l in linhas if l["STATE_C"] == LC.READY_FOR_COLLECTION]
    recusas: Counter = Counter()
    detalhe = []
    for l in bot_ready:
        if l["FINAL_STATE"] in (READY_CURRENT, READY_LEGACY):
            continue
        porque = l["FINAL_REASON"]
        # A razao MAIS FORTE primeiro: uma promocao cuja prova nao existe no
        # manifesto do bot nao e uma promocao, independentemente de quando foi
        # feita. Dizer so «mediu antes» esconderia o defeito verdadeiro.
        if (l.get("CANARY_C") or {}).get("RESOLVE_NO_MANIFESTO_DO_BOT") is False:
            motivo = "PROMOCAO_SEM_PROVA_DE_CANARIO"
        elif "mediu ANTES" in porque:
            motivo = "BOT_MEDIU_ANTES_DESTA_ARVORE"
        elif l["FINAL_STATE"] in (POLICY_BLOCK, CAPABILITY_BLOCK):
            motivo = "BLOQUEIO_PRESERVADO_" + l["FINAL_STATE"]
        else:
            motivo = "REGUA_NAO_SATISFEITA_" + l["FINAL_STATE"]
        recusas[motivo] += 1
        detalhe.append({"SOURCE_ID": l["SOURCE_ID"], "MOTIVO": motivo,
                        "FINAL": l["FINAL_STATE"], "PORQUE": porque[:200]})
    reconciliadas = [l for l in linhas if l["STATE_C"] and l["FINAL_STATE"]]
    legacy_lavadas = [l["SOURCE_ID"] for l in linhas
                      if l["STATE_C"] == LC.READY_FOR_COLLECTION
                      and l["STATE_A"] == LC.READY_FOR_COLLECTION
                      and l["FINAL_STATE"] == READY_CURRENT
                      and (l.get("DETAIL_PROOF_A") or {}).get("BODY_UTIL") is not True]
    return {
        "BOT_READY": len(bot_ready),
        "CANONICAL_RECONCILED": len(reconciliadas),
        "BOT_READY_ACEITES": len(bot_ready) - sum(recusas.values()),
        "BOT_READY_RECUSADAS": sum(recusas.values()),
        "RECUSAS_POR_MOTIVO": dict(recusas),
        "RECUSAS": detalhe,
        "LEGACY_LEAK": len(legacy_lavadas),
        "LEGACY_LEAK_IDS": legacy_lavadas,
        "NOTA": ("COLLECTION_ELIGIBLE nao se calcula aqui — pergunta-se a "
                 "collection_gate.avaliar, que e o unico dono da regra."),
    }


# ---------------------------------------------------------------------------
# A CLASSE SEMANTICA — LEI PERMANENTE.
#
#     STATE_NAME_DIFF NAO IMPLICA STATE_MEANING_DIFF.
#
# Dois livros do mesmo conceito usam rotulos diferentes para o MESMO facto.
# `CANARY_PENDING` aqui e `CONTRACTED_CANARY_FAILED` no bot dizem ambos «nao
# esta pronta, falta provar a rota» — e a reconciliacao traduz um no outro de
# proposito.
#
# Medido em 2026-09-22: comparar ROTULOS dava 124 divergencias; comparar
# CLASSES dava 63. As 61 de diferenca eram acordo lido como conflito. O perigo
# nao e o numero: quem le 124 vai «consertar» 61 fontes certas, e para isso tem
# de desfazer a traducao que guarda o passo pendente de cada uma.
#
#     COMPARA-SE PRIMEIRO A CLASSE. O ROTULO SO DEPOIS, E SO PARA CONTAR.
# ---------------------------------------------------------------------------
CLASSE_READY = "READY"
CLASSE_NOT_READY = "NOT_READY_NEEDS_ROUTE_PROOF"
CLASSE_POLICY = "POLICY_BLOCK"
CLASSE_CAPABILITY = "CAPABILITY_BLOCK"
CLASSE_RETRY = "RETRY"
CLASSE_HUMAN = "HUMAN_REVIEW"
CLASSE_RECONCILIACAO = "RECONCILIATION_REQUIRED"
CLASSE_FAILED = "FAILED"
CLASSE_UNKNOWN = "UNKNOWN"

CLASSES_SEMANTICAS = (CLASSE_READY, CLASSE_NOT_READY, CLASSE_POLICY, CLASSE_CAPABILITY,
                      CLASSE_RETRY, CLASSE_HUMAN, CLASSE_RECONCILIACAO, CLASSE_FAILED,
                      CLASSE_UNKNOWN)

# O rotulo do lifecycle -> a classe. Tudo o que nao esteja aqui e UNKNOWN: um
# estado que ninguem classificou nao se adivinha pelo nome.
_CLASSE_DE = {
    LC.READY_FOR_COLLECTION: CLASSE_READY,
    LC.POLICY_BLOCK: CLASSE_POLICY,
    LC.CAPABILITY_BLOCK: CLASSE_CAPABILITY,
    LC.RETRY_AFTER: CLASSE_RETRY,
    LC.SEMANTIC_REVIEW: CLASSE_HUMAN,
    LC.RECONCILIATION_REQUIRED: CLASSE_RECONCILIACAO,
    LC.DEGRADED: CLASSE_FAILED,
    LC.UNKNOWN: CLASSE_UNKNOWN,
    # ⚠️ DECISAO DECLARADA, nao omissao. `AUTH_BLOCK` (muro de login) nao esta
    # nas nove classes fixadas. Le-se como CAPABILITY_BLOCK porque o
    # significado e o mesmo — «fonte boa, aquisicao impossivel com o que a casa
    # tem»: uma credencial que nao temos e capacidade em falta, nao uma
    # proibicao do publicador. NAO se inventa aqui uma decima classe: o
    # vocabulario e fechado, e alargá-lo e decisao de quem manda.
    LC.AUTH_BLOCK: CLASSE_CAPABILITY,
    # todos estes dizem a mesma coisa: falta provar a rota.
    LC.DISCOVERED: CLASSE_NOT_READY,
    LC.QUALIFYING: CLASSE_NOT_READY,
    LC.CONTRACT_PENDING: CLASSE_NOT_READY,
    LC.CANARY_PENDING: CLASSE_NOT_READY,
    LC.REPAIRING: CLASSE_NOT_READY,
    LC.CONTRACT_READY_ROUTE_BLOCKED: CLASSE_NOT_READY,
    LC.CONTRACTED_CANARY_FAILED: CLASSE_NOT_READY,
}


def classe_semantica(estado: str | None) -> str:
    """O FACTO que o rotulo exprime. `None` (fonte ausente) tambem e UNKNOWN."""
    return _CLASSE_DE.get(estado or "", CLASSE_UNKNOWN)


def mesmo_facto(estado_a: str | None, estado_b: str | None) -> bool:
    """Os dois livros dizem a mesma coisa, ainda que com nomes diferentes?"""
    return classe_semantica(estado_a) == classe_semantica(estado_b)


def divergencias(ult_x: dict, ult_y: dict) -> dict:
    """A comparacao honesta entre dois livros: nominais, reais, e a diferenca.

    Quem publicar «N divergencias» sem passar por aqui publica o numero
    errado — e o numero errado, neste caso, assusta para o lado de consertar
    o que esta certo.
    """
    comuns = set(ult_x) & set(ult_y)
    nominais, reais = [], []
    for k in sorted(comuns):
        a = (ult_x[k] or {}).get("NEW_STATE")
        b = (ult_y[k] or {}).get("NEW_STATE")
        if a == b:
            continue
        nominais.append(k)
        if not mesmo_facto(a, b):
            reais.append(k)
    return {
        "FONTES_EM_AMBOS": len(comuns),
        "DIVERGENCIA_NOMINAL": len(nominais),
        "DIVERGENCIA_REAL": len(reais),
        "SO_O_ROTULO_DIFERE": len(nominais) - len(reais),
        "IDS_REAIS": reais,
        "POR_CLASSE": dict(Counter(
            (classe_semantica((ult_x[k] or {}).get("NEW_STATE")),
             classe_semantica((ult_y[k] or {}).get("NEW_STATE"))) for k in reais)),
    }


def _bate(estado_lifecycle: str, final: str) -> bool:
    if estado_lifecycle == LC.READY_FOR_COLLECTION:
        return final in (READY_CURRENT, READY_LEGACY)
    return _mapa(estado_lifecycle) == final


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
    for nome in ("B", "B2", "C"):
        for k in l["CHAVES_NOS_LIVROS"]:
            if k in ctx["_HIST"][nome]:
                return nome, k
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


def importar_provas_do_bot(plano_: list, ctx: dict) -> dict:
    """Traz para o manifesto local as PROVAS do bot que sustentam o que foi
    importado. Sem isto, a ponte fica entupida no ultimo metro.

    ⚠️ O ESTADO SEM A PROVA NAO ATRAVESSA. `collection_gate` nao le o livro do
    bot: le o manifesto DESTA arvore. Uma fonte importada como READY cuja
    prova ficou no bot e lida como «READY sem nenhuma linha de promocao» —
    `NUNCA_PROMOVIDA` — e nunca sera elegivel, por muito correcto que o estado
    esteja. Copiar a prova e o que liga o cano ate ao fim.

    NAO SOBREPOE. Um `EVIDENCE_REF` que ja exista aqui com conteudo DIFERENTE
    e uma colisao de identidade entre duas arvores: nao se resolve escolhendo
    uma: fica de fora e fica dita. Medido em 2026-09-22: 35 referencias
    comuns, todas iguais byte a byte, 0 colisoes.
    """
    refs = {p["EVIDENCE_REF"] for p in plano_ if p.get("EVIDENCE_REF")}
    # ⚠️ E O QUE FICOU PARA TRAS TAMBEM (B2, 2026-09-23). O plano so traz as
    # fontes cujo estado MUDA nesta volta. Uma promocao que atravessou numa
    # volta em que a prova nao veio (medido: a ponte viva corria codigo
    # anterior a esta funcao importar alguma coisa — 23 de 35 READY do bot
    # ficaram sem prova no manifesto) nunca mais entrava no plano: o estado ja
    # estava certo, e a prova ficava no bot para sempre. Cada volta olha
    # tambem para todas as referencias que o livro canonico JA cita e que o
    # manifesto local nao tem. Idempotente: uma prova ja ca nao volta a vir.
    refs |= {t["EVIDENCE_REF"] for t in LC._ler_bruto()["TRANSICOES"]
             if t.get("EVIDENCE_REF")}
    # ⚠️ A REFERENCIA QUE O PLANO CITA NAO E A CHAVE DO MANIFESTO DO BOT.
    # `_ref_da_decisao` carimba a proveniencia no proprio texto —
    # «RECONCILIACAO-V1:livro_C_(bot)@<commit>:EV-IT-T12-019-CANARY-1282» — e o
    # manifesto de C tem a chave NUA, «EV-IT-T12-019-CANARY-1282». Comparar as
    # duas directamente dava sempre conjunto vazio: PROVAS_IMPORTADAS = 0 em
    # todas as corridas, e o entupimento no ultimo metro que esta funcao existe
    # para evitar acontecia na propria funcao.
    #
    # A prova importa-se com a chave SINTETICA, e nao com a nua: e essa que a
    # promocao cita no livro, e e por essa que `ready_split.regua_de` a procura.
    # A chave nua fica escrita ao lado, para nao se perder a origem.
    EC = ctx.get("EVIDENCIA_C", {})
    quero = {}
    for r in refs:
        if r in EC:
            quero[r] = r
        elif ":" in r and r.rsplit(":", 1)[1] in EC:
            quero[r] = r.rsplit(":", 1)[1]
    caminho = EVIDENCIA_A
    doc = _json(caminho, {"DATASET": "LIFECYCLE-EVIDENCE-V1", "PROVAS": []})
    locais = {p["EVIDENCE_REF"]: p for p in doc["PROVAS"]}
    novas, colisoes, ja_ca = [], [], 0
    for r in sorted(quero):
        prova = dict(EC[quero[r]])
        if quero[r] != r:
            prova["EVIDENCE_REF_NO_BOT"] = quero[r]
            prova["EVIDENCE_REF"] = r
        if r in locais:
            igual = (json.dumps(locais[r], sort_keys=True, ensure_ascii=False)
                     == json.dumps(prova, sort_keys=True, ensure_ascii=False))
            if igual:
                ja_ca += 1
            else:
                colisoes.append({"EVIDENCE_REF": r,
                                 "SOURCE_ID_AQUI": locais[r].get("SOURCE_ID"),
                                 "SOURCE_ID_NO_BOT": prova.get("SOURCE_ID"),
                                 "RESOLUCAO": "NAO IMPORTADA — mesma referencia, conteudo diferente"})
            continue
        prova["IMPORTADO_DE"] = {"LIVRO": "C", "COMMIT": ctx["COMMITS"].get("C"),
                                 "BRANCH": BRANCH_C, "MISSAO": MISSAO}
        novas.append(prova)
    if novas:
        doc["PROVAS"] = doc["PROVAS"] + novas
        caminho.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                           encoding="utf-8")
    return {"PROVAS_CITADAS_DE_C": len(quero), "PROVAS_IMPORTADAS": len(novas),
            "PROVAS_JA_PRESENTES_IDENTICAS": ja_ca,
            "COLISOES_NAO_IMPORTADAS": colisoes,
            "PROVAS_NO_MANIFESTO_DEPOIS": len(doc["PROVAS"])}


def _aquisicao(c: dict | None) -> str:
    return json.dumps((c or {}).get("ACQUISITION"), sort_keys=True, ensure_ascii=False)


def importar_contratos_do_bot(ctx: dict) -> dict:
    """Traz para o livro de contratos DESTA arvore os contratos que so o bot tem.

    ⚠️ O CONTRATO SEM O ESTADO NAO SERVE, E O ESTADO SEM O CONTRATO TAMBEM NAO.
    `collection_gate` le a regua sobre `italy_contracts_curator.json` DESTA
    arvore. Medido (B1/B2, 2026-09-23): das 35 fontes que o bot promoveu na
    janela do observador, 35 atravessaram SEM contrato aqui — e sem contrato
    o passo INDEX_URL da regua e falso, e a fonte nunca sai de READY_LEGACY.
    Nenhuma peca trazia o contrato: `CONTRATOS_C` so servia para decidir.

    SO O QUE FALTA. Um contrato que ja existe aqui NUNCA e sobreposto: se o do
    bot tiver outra aquisicao, e uma COLISAO de dono (dois contratos para a
    mesma fonte) — fica de fora e fica dita, com as duas entradas lado a lado.
    Quem decide o dono e o dono, nao esta funcao.

    So entram contratos de fontes que o livro canonico conhece: a ponte nao
    semeia fontes no livro de contratos.
    """
    CC = ctx.get("CONTRATOS_C", {}) or {}
    caminho = CONTRATOS_A
    doc = _json(caminho, {"DATASET": "SOURCE-CURATOR-CONTRACTS-V1", "FONTES": []})
    locais = {c["SOURCE_ID"]: c for c in doc.get("FONTES", [])}
    conhecidas = {t["SOURCE_ID"] for t in LC._ler_bruto()["TRANSICOES"]}
    novos, colisoes, iguais = [], [], 0
    for sid in sorted(conhecidas & set(CC)):
        c = CC[sid]
        if sid in locais:
            if _aquisicao(locais[sid]) == _aquisicao(c):
                iguais += 1
            else:
                colisoes.append({
                    "SOURCE_ID": sid,
                    "INDEX_AQUI": ((locais[sid].get("ACQUISITION") or {}).get("INDEX_URL")
                                   or locais[sid].get("CANONICAL_ENTRY_URL")),
                    "INDEX_NO_BOT": ((c.get("ACQUISITION") or {}).get("INDEX_URL")
                                     or c.get("CANONICAL_ENTRY_URL")),
                    "RESOLUCAO": "NAO IMPORTADO — dois contratos para a mesma fonte; decide o dono"})
            continue
        novo = dict(c)
        novo["IMPORTADO_DE"] = {"LIVRO": "C", "COMMIT": ctx["COMMITS"].get("C"),
                                "BRANCH": BRANCH_C, "MISSAO": MISSAO, "EM": agora()}
        novos.append(novo)
    if novos:
        doc["FONTES"] = doc.get("FONTES", []) + novos
        caminho.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                           encoding="utf-8")
    return {"CONTRATOS_IMPORTADOS": len(novos),
            "IMPORTADOS": [c["SOURCE_ID"] for c in novos],
            "CONTRATOS_JA_IGUAIS": iguais,
            "COLISOES_DE_DONO": colisoes}


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
    provas = importar_provas_do_bot([t for t in p if t["SOURCE_ID"] not in ilegais], ctx)
    contratos = importar_contratos_do_bot(ctx)
    return {"APLICADO_EM": agora(), "LINHAS_ANTES": antes, "LINHAS_DEPOIS": depois,
            "APENDIDAS": gravadas, "PLANEADAS": len(p),
            "CADEIAS_ILEGAIS_NAO_IMPORTADAS": sorted(ilegais), "FALTAS": faltas,
            "EVIDENCIA": provas, "CONTRATOS": contratos}


def _opcao(argv: list, nome: str) -> str | None:
    if nome in argv:
        i = argv.index(nome)
        if i + 1 < len(argv):
            return argv[i + 1]
        raise SystemExit("%s precisa de um valor" % nome)
    return None


def main(argv: list | None = None) -> int:
    """Opcoes (todas opcionais; sem elas, o comportamento e o de sempre):
      --livro-servico DIR  corte congelado do servico (CORTE.json com sha256)
      --livro-ponte FILE   livro A a usar no lugar do da arvore (ensaio); as
                           provas A leem-se/escrevem-se ao lado dele
      --saida FILE         onde escrever o censo (no lugar de RECONCILIACAO-V1.json)
    Com --livro-servico, --aplicar so e aceite se --livro-ponte tambem for dado:
    um corte de ensaio nunca escreve no livro real."""
    global SAIDA, EVIDENCIA_A
    argv = sys.argv[1:] if argv is None else argv
    corte = _opcao(argv, "--livro-servico")
    livro_a = _opcao(argv, "--livro-ponte")
    saida = _opcao(argv, "--saida")
    if corte and "--aplicar" in argv and not livro_a:
        print("--aplicar com --livro-servico exige --livro-ponte (ensaio). O livro real nao se toca.")
        return 2
    if livro_a:
        # o livro A de ensaio leva as provas ao lado: aplicar() tambem escreve
        # nelas, e as provas reais da arvore nao se tocam num ensaio.
        ev = Path(livro_a).parent / EVIDENCIA_A.name
        if not ev.exists():
            print("--livro-ponte exige %s ao lado do livro (copia das provas A)." % ev.name)
            return 2
        LC.LIVRO = Path(livro_a)
        EVIDENCIA_A = ev
    if saida:
        SAIDA = Path(saida)
    try:
        ctx = carregar_contexto(corte_c=Path(corte) if corte else None)
    except CorteInvalido as e:
        print("CORTE DO SERVICO RECUSADO: %s" % e)
        return 3
    if not ctx["B"] or not ctx["B2"]:
        print("LIVRO B ou B2 ilegivel por git show (%s / %s). NAO SE INVENTA O OUTRO LIVRO." % (REF_B, REF_B2))
        return 1
    doc = censo(ctx)
    if "--aplicar" in argv:
        doc["APLICADO"] = aplicar(doc, ctx)
        # o censo relido sobre o livro evoluido — e o que fica escrito.
        ctx2 = carregar_contexto(corte_c=Path(corte) if corte else None)
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
    try:
        print("escrito: %s" % SAIDA.relative_to(RAIZ))
    except ValueError:
        print("escrito: %s" % SAIDA)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
