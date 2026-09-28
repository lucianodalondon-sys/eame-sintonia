#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IDENTIDADE DO CRUZAMENTO (IDENT-v1) — um cartao por PERGUNTA, a prova conta uma vez, e o DELTA e da Intelligence.

    MISSAO   POTES-UM-CARTAO (D125 aprovada pelo dono 27/09 ~21:40: «potes, aprovo»; desenho em
             docs/lab/IDENTIDADE-CRUZAMENTO.md §1-§7 e §11.2 INT-LAW-096/097/098/099/215/216)
    ESPECIE  MOTOR (Z-MOTOR). Codigo da Intelligence. NAO E POTE. NAO E TELA. NAO TOCA REDE NEM LIVRO VIVO.

    python3 -m unittest tests.test_identidade_cruzamento -v

AS TRES IDENTIDADES (§1.2)
--------------------------
    CROSSING_ID       XQ-sha(CROSSING_KEY)   a PERGUNTA. Persiste entre corridas. Nunca leva run, documento,
                                             posicao, boletim nem edicao da referencia (INT-LAW-096).
    EVIDENCE_LINK_ID  XL-sha(KEY|EVIDENCIA)  pergunta x documento. O mesmo documento lido N vezes = 1 link
                                             (INT-LAW-098).
    AVALIACAO_ID      XA-sha(ID|RUN)         a resposta DAQUELA corrida — e so aqui que o run entra (INT-LAW-099).

    SG2-  sinal     = sha(DOCUMENTO|RAW_OBSERVATION_ID|FACT_TIME)            (antes: run + posicao)
    FUT2- futuro    = sha(ISSUE|GEO|HORIZONTE); sem ISSUE, como o SG2          (antes: run + item)
    REND- rendimento: MANTEM o run — e medida da corrida, nao do mundo.

AS DUAS GUARDAS CONTRA O ERRO CONTRARIO (juntar o que e diferente)
-----------------------------------------------------------------
    INT-LAW-097  chave com NAO SEI nao junta com nada: o slot vira NAO_SEI@<documento>.
    INT-LAW-099  a edicao da bula NAO entra na chave: edicao nova = nova AVALIACAO da mesma pergunta.

D125 (os quatro pontos do coordenador, aprovados pelo dono)
-----------------------------------------------------------
    1. um fato/documento pode alimentar VARIOS potes (compartimentos) ao mesmo tempo;
    2. o fato atualiza UMA vez e todos os potes que o usam mudam juntos na mesma corrida
       (os dependentes sao reavaliados com CAUSA = PAI_MUDOU(<id>));
    3. 1 documento novo que toca 3 potes = 0 cartoes repetidos e os 3 com o mesmo GATILHO;
    4. nenhum pote guarda copia do cartao, so o ID; a prova conta 1 vez (fecho por EVIDENCIA / ORIGINADOR).

OS DOIS DEFEITOS DA POC DO LAB, CORRIGIDOS AQUI (IDENTIDADE-CRUZAMENTO §3)
------------------------------------------------------------------------
    1. `estado_vigente`: NO -> YES da MESMA origem em periodos diferentes e TEMPORAL_CHANGE, e o estado
       vigente e o da prova mais recente (com o anterior no HISTORICO) — nunca «CONFLITANTE».
    2. F1: o estado da pergunta e o do ROTULO (AI x CROP x edicao), calculado por quem le o rotulo
       (motor/cruzamentos_max.py:avaliar_rotulo) — nunca o «melhor link». A qualidade de cada link fica no link.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import vocabulario_unico as VOCAB   # noqa: E402  (motor/)

REGRA = "IDENT-v1"
NAO_SEI = "NAO SEI"

# ── AS FAMILIAS: os slots da chave, em ordem fixa (§1.3) ──────────────────────
F1 = "F1_ROTULO_X_SUBSTANCIA_CITADA"
F2 = "F2_PORTFOLIO_MATCH"
F3 = "F3_COMPETITIVE_SET"
F4 = "F4_JANELA_CULTURA_PRAGA"
F5 = "F5_FUTURO"
FAMILIAS = {
    F1: ("JURISDICAO", "AI", "CROP"),
    F2: ("JURISDICAO", "CROP", "TARGET"),
    F3: ("JURISDICAO", "AI", "REGISTRO"),
    F4: ("CROP", "TARGET", "LUGAR", "CAMPANHA"),
    F5: ("TARGET", "LUGAR", "HORIZONTE"),
}
#: O nome do CRUZAMENTO que o motor dos cruzamentos ja escreve -> a familia.
FAMILIA_DO_CRUZAMENTO = {"ROTULO_X_SUBSTANCIA_CITADA_NO_BOLETIM": F1, "PORTFOLIO_MATCH": F2,
                         "COMPETITIVE_SET": F3}

# ── DELTA (INT-LAW-215) ──────────────────────────────────────────────────────
NOVO, FORTALECEU, MUDOU_ESTADO, ENFRAQUECEU, SEM_REVISAO = (
    "NOVO", "FORTALECEU", "MUDOU_ESTADO", "ENFRAQUECEU", "SEM_REVISAO")
MUDANCAS = (NOVO, FORTALECEU, MUDOU_ESTADO, ENFRAQUECEU, SEM_REVISAO)
SAIU = "SAIU"
PAPEIS = ("APOIA", "CONTRADIZ", "NAO_CONFERIVEL", "CONTEXTO")
#: As especies sobem numa direcao so (§5): uma referencia aponta sempre para baixo.
RANK = {"SINAL": 0, "RENDIMENTO_DE_FONTE": 0, "CROSSING": 1, "FINDING": 2,
        "OPORTUNIDADE": 3, "FATO_PRESENTE_SOBRE_O_FUTURO": 3}
TEMPORAL_CHANGE = "TEMPORAL_CHANGE_IN_RECOMMENDATION"
DIVERGENT = "DIVERGENT_RECOMMENDATIONS"
DIVERGENTE_ENTRE_LINKS = "DIVERGENTE_ENTRE_LINKS"


def _ign(v) -> bool:
    return v is None or (isinstance(v, str) and (not v.strip() or v.strip().upper() in ("NAO SEI", "NÃO SEI")))


def _sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def chave_substancia(s) -> str:
    """A MESMA chave do motor dos cruzamentos (TAU-FLUVALINATE = tau fluvalinate; METALAXYL != METALAXYL-M)."""
    import cruzamentos_max as XM   # noqa: E402  (motor/; importado na hora — ele importa este ficheiro)
    return XM.chave_substancia(s)


# ── A CHAVE ──────────────────────────────────────────────────────────────────
def crossing_key(familia: str, slots: dict, documento: str) -> str:
    """`FAMILIA/v1|SLOT=VALOR|...` em ordem fixa. Slot vazio/NAO SEI -> NAO_SEI@<documento> (INT-LAW-097)."""
    if familia not in FAMILIAS:
        raise ValueError("familia desconhecida: %r" % (familia,))
    partes = [familia + "/v1"]
    for s in FAMILIAS[familia]:
        v = slots.get(s)
        if _ign(v):
            v = "NAO_SEI@" + str(documento)
        partes.append("%s=%s" % (s, v))
    return "|".join(partes)


def crossing_id(key: str) -> str:
    return "XQ-" + _sha16(key)


def evidence_link_id(key: str, evidencia: str) -> str:
    return "XL-" + _sha16(key + "|" + evidencia)


def avaliacao_id(objeto_id: str, run_id: str) -> str:
    return "XA-" + _sha16(str(objeto_id) + "|" + str(run_id))


def campanha(fact_time):
    """A campanha agricola do FACTO. A publicacao nunca entra aqui (INT-LAW-100): sem FACT_TIME, None."""
    if _ign(fact_time):
        return None
    m = re.search(r"(20\d\d)", str(fact_time))
    return m.group(1) if m else None


def slot_ai(substancia):
    return None if _ign(substancia) else "AI:" + chave_substancia(substancia)


# ── A EVIDENCIA E O ORIGINADOR (INT-LAW-098 · INT-LAW-071/092) ────────────────
_DOC = ("DOCUMENT_ID", "SOURCE_DOCUMENT_ID", "raw_document_key")
_SHA = ("RAW_SHA256", "raw_sha256", "SHA256", "CONTENT_SHA256", "TEXTO_SHA256", "sha256")


def evidencia(prova: dict) -> str:
    """A identidade da EVIDENCIA = o documento; na falta, o SHA do conteudo que a Coleta entregou.
    Sem nenhum dos dois: o ITEM (dito ITEM:, para nao se passar por documento)."""
    for c in _DOC:
        if not _ign(prova.get(c)):
            return "DOC:" + str(prova[c])
    for c in _SHA:
        if not _ign(prova.get(c)):
            return "SHA:" + str(prova[c]).lower()[:16]
    return "ITEM:" + str(prova.get("ITEM_ID", NAO_SEI))


def originador(prova: dict) -> str:
    """ORIGINADOR quando a Coleta o entrega; senao o SOURCE_ID como PROXY DECLARADO (superconta: §3)."""
    for c in ("ORIGINADOR", "ORIGINATOR", "ORIGINATOR_ID"):
        if not _ign(prova.get(c)):
            return str(prova[c])
    return "PROXY_SOURCE_ID:" + str(prova.get("SOURCE_ID", NAO_SEI))


def contar_provas(provas) -> dict:
    """Contagens SEPARADAS, nunca somadas: links, documentos, originadores (INT-LAW-092)."""
    por_doc = {}
    for p in provas or []:
        por_doc.setdefault(evidencia(p), p)
    return {"N_LINKS": len(provas or []), "N_EVIDENCIAS_DOCUMENTO": len(por_doc),
            "N_ORIGINADORES": len({originador(p) for p in por_doc.values()})}


# ── O ESTADO ENTRE LEITURAS DA MESMA PERGUNTA (defeito 1 da POC, corrigido) ───
def relacao(a: dict, b: dict) -> str:
    """Duas leituras {estado, originador, periodo}. INT-LAW-079: a mesma origem em periodos diferentes =
    TEMPORAL_CHANGE; origens diferentes = DIVERGENT (contradicao UNRESOLVED). Nunca «CONFLITANTE»."""
    if a["estado"] == b["estado"]:
        return "CONCORDA"
    if a["originador"] == b["originador"] and a["periodo"] != b["periodo"]:
        return TEMPORAL_CHANGE
    return DIVERGENT


def estado_vigente(leituras: list) -> dict:
    """O estado vigente da pergunta a partir das leituras (F4: janela).

    Por originador, vale a leitura MAIS RECENTE por periodo (FACT_TIME) — a anterior vai ao HISTORICO com a
    RELACAO. Se os vigentes de originadores diferentes discordam: DIVERGENT, contradicao UNRESOLVED, e o
    estado fica NAO SEI com os dois a vista (nao se escolhe um).
    """
    if not leituras:
        return {"ESTADO": NAO_SEI, "RELACAO": NAO_SEI, "HISTORICO": [], "CONTRADICAO": NAO_SEI}
    por_orig, historico = {}, []
    for l in sorted(leituras, key=lambda x: (str(x["originador"]), str(x["periodo"]))):
        ant = por_orig.get(l["originador"])
        if ant is not None:
            historico.append({"DE": ant["estado"], "PARA": l["estado"], "ORIGINADOR": l["originador"],
                              "PERIODO_DE": ant["periodo"], "PERIODO_PARA": l["periodo"],
                              "RELACAO": relacao(ant, l)})
        por_orig[l["originador"]] = l
    vigentes = list(por_orig.values())
    estados = sorted({v["estado"] for v in vigentes})
    if len(estados) == 1:
        rel = next((h["RELACAO"] for h in reversed(historico) if h["RELACAO"] != "CONCORDA"), "CONCORDA")
        return {"ESTADO": estados[0], "RELACAO": rel, "HISTORICO": historico, "CONTRADICAO": "NENHUMA"}
    return {"ESTADO": NAO_SEI, "RELACAO": DIVERGENT, "HISTORICO": historico, "CONTRADICAO": "UNRESOLVED",
            "VIGENTES": [{"ORIGINADOR": v["originador"], "ESTADO": v["estado"], "PERIODO": v["periodo"]}
                         for v in vigentes]}


# ── SINAL e FUTURO sem run (ordem §11.3 passo 2) ─────────────────────────────
def sg2_id(documento, raw_observation_id, fact_time) -> str:
    return "SG2-" + _sha16("%s|%s|%s" % (documento, raw_observation_id, fact_time))


def fut2_id(issue, geo, horizonte, documento, raw_observation_id) -> str:
    if not _ign(issue):
        return "FUT2-" + _sha16("ISSUE|%s|%s|%s" % (issue, geo, horizonte))
    return "FUT2-" + _sha16("DOC|%s|%s|%s" % (documento, raw_observation_id, horizonte))


# ── MIGRACAO: um objeto do esquema anterior -> a identidade da pergunta, com ALIAS (INT-LAW-216) ──
_ESTAVEIS = ("XQ-", "SG2-", "FUT2-")


def _chaves(o):
    c = dict(o.get("FORA_DO_CONTRATO") or {})
    c.update({k: v for k, v in (o.get("CHAVES") or {}).items()})
    return c


def _doc_da_prova(o):
    p = (o.get("PROVA") or [{}])[0] or {}
    return p, evidencia(p)


def identificar(o: dict) -> dict:
    """{OBJETO_ID, CROSSING_KEY?, FAMILIA?, ALIAS} para um objeto de pote (v2) ou de entrada.

    NUNCA reescreve nem apaga o ID antigo: ele vai para ALIAS. Objeto que ja traz identidade estavel
    passa como veio. RENDIMENTO mantem o seu (e da corrida). FINDING/OPORTUNIDADE sem CROSSING_KEY:
    NAO SEI como os identificar pela pergunta — ficam com o ID que a Intelligence lhes deu.
    """
    antigo = o.get("OBJETO_ID") if not _ign(o.get("OBJETO_ID")) else o.get("SIGNAL_ID")
    alias = [a for a in (o.get("ALIAS") or []) if a]
    if not _ign(o.get("CROSSING_KEY")):
        novo = crossing_id(o["CROSSING_KEY"])
        if antigo and antigo != novo and antigo not in alias:
            alias.append(antigo)
        return {"OBJETO_ID": novo, "CROSSING_KEY": o["CROSSING_KEY"],
                "FAMILIA": o.get("FAMILIA") or o["CROSSING_KEY"].split("/")[0], "ALIAS": sorted(alias)}
    if str(antigo).startswith(_ESTAVEIS):
        return {"OBJETO_ID": antigo, "ALIAS": alias}
    especie = o.get("ESPECIE") or "SINAL"
    c = _chaves(o)
    p, doc = _doc_da_prova(o)
    novo, key, fam = None, None, None
    if especie == "SINAL":
        novo = sg2_id(doc, p.get("RAW_OBSERVATION_ID", NAO_SEI), p.get("FACT_TIME", c.get("FACT_TIME", NAO_SEI)))
    elif especie == "FATO_PRESENTE_SOBRE_O_FUTURO":
        geo = c.get("FACT_LOCATION") if not _ign(c.get("FACT_LOCATION")) else c.get("REGION_ID")
        novo = fut2_id(c.get("ISSUE_ID"), geo, c.get("FACT_TIME", p.get("FACT_TIME")), doc,
                       p.get("RAW_OBSERVATION_ID", NAO_SEI))
    elif especie == "CROSSING":
        fam = FAMILIA_DO_CRUZAMENTO.get(str(c.get("CRUZAMENTO")))
        if fam is None and not _ign(c.get("ACTIVE_INGREDIENT_ID")):
            fam = F1       # o crossing da R7 (rotulo x substancia citada), escrito antes do nome CRUZAMENTO
        if fam == F1:
            key = crossing_key(F1, {"JURISDICAO": "IT", "AI": slot_ai(c.get("ACTIVE_INGREDIENT_ID")),
                                    "CROP": VOCAB.cultura(c.get("CROP_ID"))}, doc)
        elif fam == F2:
            cult, pr = (str(c.get("PAR_DO_BOLETIM", "")).split(" x ", 1) + [None])[:2]
            key = crossing_key(F2, {"JURISDICAO": "IT", "CROP": VOCAB.cultura(cult), "TARGET": VOCAB.praga(pr)}, doc)
        elif fam == F3:
            subs = c.get("SUBSTANCIA_EM_COMUM") or []
            subs = subs if isinstance(subs, list) else [subs]
            reg = str(c.get("T4_REGISTRATION_EVIDENCE_ID") or c.get("PRODUCT_ID") or "").split(":")[-1]
            key = crossing_key(F3, {"JURISDICAO": "IT", "AI": "+".join(sorted(slot_ai(s) for s in subs if s)) or None,
                                    "REGISTRO": reg or None}, doc)
        if key:
            novo = crossing_id(key)
    if novo is None:
        return {"OBJETO_ID": antigo, "ALIAS": alias}
    if antigo and antigo != novo and antigo not in alias:
        alias.append(antigo)
    out = {"OBJETO_ID": novo, "ALIAS": sorted(alias)}
    if key:
        out.update(CROSSING_KEY=key, FAMILIA=fam)
    return out


def grupo(key: str, provas) -> str | None:
    """GRUPO de APRESENTACAO (nunca para contar): a chave sem o documento dos NAO SEI, e o originador.
    Ex.: os 2 tau-fluvalinato do ARIF n.37/n.38 continuam 2 cartoes, com o mesmo GRUPO."""
    if not key or "NAO_SEI@" not in key:
        return None
    base = re.sub(r"NAO_SEI@[^|]*", "NAO_SEI", key)
    origs = sorted({originador(p) for p in provas or []})
    return base + "|ORIGINADOR=" + "+".join(origs)


def _prova_chave(p):
    return (evidencia(p), str(p.get("ITEM_ID")), str(p.get("RAW_OBSERVATION_ID")), str(p.get("SOURCE_ID")))


def consolidar(objetos: list, estado_da_pergunta=None) -> list:
    """Varios objetos da MESMA pergunta (mesmo ID depois de `identificar`) -> UM cartao.

    PROVA = uniao sem repetir; LINKS = um por documento; ALIAS = uniao. O estado dos links fica em cada
    link. RESPOSTA: `estado_da_pergunta(cartao)` quando quem sabe a da (F1: o rotulo); senao o estado comum
    dos links, e se eles DIVERGEM, `DIVERGENTE_ENTRE_LINKS` com FUSAO_DIVERGENTE = true (para e sobe ao
    dono, INT-LAW-216) — nunca o «melhor».
    """
    por_id, ordem = {}, []
    for o in objetos:
        ident = identificar(o)
        oid = ident["OBJETO_ID"]
        estado_link = _estado_do_objeto(o)
        if oid not in por_id:
            base = dict(o)
            base.update(ident)
            base["PROVA"], base["_LINKS"], base["_CH"], base["_TXT"] = [], {}, {}, {}
            por_id[oid] = base
            ordem.append(oid)
        c = por_id[oid]
        c["ALIAS"] = sorted(set(c.get("ALIAS") or []) | set(ident.get("ALIAS") or []))
        for k, v in (o.get("CHAVES") or {}).items():
            vs = c["_CH"].setdefault(k, [])
            if not _ign(v) and v not in vs:
                vs.append(v)
        for k in ("PORQUE", "INCERTEZA", "CONTRADIZ"):
            vs = c["_TXT"].setdefault(k, [])
            if not _ign(o.get(k)) and o.get(k) not in vs:
                vs.append(o.get(k))
        vistos = {_prova_chave(p) for p in c["PROVA"]}
        for p in o.get("PROVA") or []:
            if _prova_chave(p) not in vistos:
                c["PROVA"].append(p)
                vistos.add(_prova_chave(p))
            ev = evidencia(p)
            lk = c["_LINKS"].setdefault(ev, {"EVIDENCIA": ev, "ORIGINADOR": originador(p), "ESTADOS": set(),
                                             "ALIAS": set()})
            lk["ESTADOS"].add(estado_link)
            if not _ign(o.get("OBJETO_ID") or o.get("SIGNAL_ID")):
                lk["ALIAS"].add(str(o.get("OBJETO_ID") or o.get("SIGNAL_ID")))
    out = []
    for oid in ordem:
        c = por_id[oid]
        links = c.pop("_LINKS")
        # CHAVES juntas: um valor = ele; varios (ex.: o PRODUCT_ID de cada link) = todos, a vista; nenhum = NAO SEI
        c["CHAVES"] = {k: (vs[0] if len(vs) == 1 else " | ".join(sorted(json.dumps(x, ensure_ascii=False)
                                                                         if not isinstance(x, str) else x for x in vs))
                           if vs else NAO_SEI) for k, vs in c.pop("_CH").items()}
        for k, vs in c.pop("_TXT").items():
            c[k] = " ‖ ".join(str(x) for x in vs) if vs else NAO_SEI
        key = c.get("CROSSING_KEY")
        c["LINKS"] = [{"EVIDENCE_LINK_ID": evidence_link_id(key or oid, ev), "EVIDENCIA": ev,
                       "ORIGINADOR": l["ORIGINADOR"], "ESTADO_DO_LINK": "|".join(sorted(l["ESTADOS"])),
                       "ALIAS_DO_LINK": sorted(l["ALIAS"])} for ev, l in sorted(links.items())]
        c["CONTAGENS"] = contar_provas(c["PROVA"])
        c["REGRA_DE_IDENTIDADE"] = REGRA
        c["VOCABULARIO"] = VOCAB.carimbo()
        c["ID_PROVISORIO"] = True           # D119: nenhum esquema definitivo ainda
        g = grupo(key, c["PROVA"])
        if g:
            c["GRUPO"] = g
        estados = sorted({s for l in links.values() for s in l["ESTADOS"]})
        resp = estado_da_pergunta(c) if estado_da_pergunta else None
        if resp is not None:
            c["RESPOSTA"] = resp
            c["RESPOSTA_DITA_POR"] = "ROTULO"
        elif len(estados) <= 1:
            c["RESPOSTA"] = estados[0] if estados else NAO_SEI
            c["RESPOSTA_DITA_POR"] = "LINKS_CONCORDAM"
        else:
            c["RESPOSTA"] = DIVERGENTE_ENTRE_LINKS
            c["RESPOSTA_DITA_POR"] = "LINKS_DIVERGEM"
            c["FUSAO_DIVERGENTE"] = True
            c["ESTADOS_DOS_LINKS"] = estados
        out.append(c)
    return out


def _estado_do_objeto(o) -> str:
    for v in (o.get("RESPOSTA"), (o.get("CHAVES") or {}).get("CROSSING_STATE"),
              (o.get("FORA_DO_CONTRATO") or {}).get("CROSSING_STATE"), o.get("RESULTADO")):
        if not _ign(v):
            return str(v)
    return NAO_SEI


# ── FECHO: a prova conta 1 vez (D125.4) ──────────────────────────────────────
def fecho(oid: str, cartoes: dict, _pilha=()) -> dict:
    """As evidencias e os originadores do cartao E dos que ele referencia (para baixo), cada um 1 vez."""
    if oid in _pilha:
        raise ValueError("CICLO nas referencias: " + " -> ".join(_pilha + (oid,)))
    c = cartoes[oid]
    evs = {evidencia(p): originador(p) for p in c.get("PROVA") or []}
    for r in c.get("REFERENCIAS") or []:
        alvo = r.get("CROSSING_ID")
        if alvo in cartoes:
            sub = fecho(alvo, cartoes, _pilha + (oid,))
            for e, o in zip(sub["EVIDENCIAS"], sub["_ORIG_POR_EV"]):
                evs.setdefault(e, o)
    evs_ord = sorted(evs)
    return {"EVIDENCIAS": evs_ord, "_ORIG_POR_EV": [evs[e] for e in evs_ord],
            "N_EVIDENCIAS_DOCUMENTO": len(evs), "N_ORIGINADORES": len(set(evs.values()))}


def conferir_referencias(cartoes: dict) -> list:
    """DAG: toda REFERENCIA aponta para um cartao existente, da MESMA corrida (AVALIACAO_ID), de especie
    mais baixa, com PAPEL valido. Lista de violacoes."""
    v = []
    for oid, c in cartoes.items():
        for r in c.get("REFERENCIAS") or []:
            alvo = cartoes.get(r.get("CROSSING_ID"))
            if alvo is None:
                v.append("%s: referencia %s SEM_PAI (cartao ausente)" % (oid, r.get("CROSSING_ID")))
                continue
            if r.get("PAPEL") not in PAPEIS:
                v.append("%s: referencia com PAPEL %r" % (oid, r.get("PAPEL")))
            if r.get("AVALIACAO_ID") != alvo.get("AVALIACAO_ID"):
                v.append("%s: referencia a %s com AVALIACAO_ID de outra corrida" % (oid, alvo.get("OBJETO_ID")))
            if RANK.get(alvo.get("ESPECIE"), 9) > RANK.get(c.get("ESPECIE"), -1):
                v.append("%s: referencia DESCE/CICLO (%s -> %s)" % (oid, c.get("ESPECIE"), alvo.get("ESPECIE")))
        try:
            fecho(oid, cartoes)
        except ValueError as e:
            v.append(str(e))
    return v


# ── DELTA pela opcao A: o pote ANTERIOR publicado (§6.1, INT-LAW-215) ─────────
def impressao_do_pote(texto_ou_bytes) -> str:
    b = texto_ou_bytes.encode("utf-8") if isinstance(texto_ou_bytes, str) else texto_ou_bytes
    return hashlib.sha256(b).hexdigest()


def ler_anterior(pote_anterior: dict, sha256: str) -> dict:
    """Indice do pote anterior (v2 ou v2.1): {id: {ESTADO, EVIDENCIAS}} e {alias: id}."""
    idx, alias = {}, {}
    if pote_anterior.get("CARTOES"):
        for oid, c in pote_anterior["CARTOES"].items():
            idx[oid] = {"ESTADO": _estado_do_objeto(c), "EVIDENCIAS": set((c.get("FECHO") or {}).get("EVIDENCIAS")
                                                                          or [evidencia(p) for p in c.get("PROVA") or []])}
            for a in c.get("ALIAS") or []:
                alias[a] = oid
    else:
        for comp in (pote_anterior.get("COMPARTIMENTOS") or {}).values():
            for o in comp.get("OBJETOS") or []:
                e = idx.setdefault(o["OBJETO_ID"], {"ESTADO": _estado_do_objeto(o), "EVIDENCIAS": set()})
                e["EVIDENCIAS"] |= {evidencia(p) for p in o.get("PROVA") or []}
    return {"IDX": idx, "ALIAS": alias,
            "REF": {"INTELLIGENCE_RUN_ID": pote_anterior.get("INTELLIGENCE_RUN_ID", NAO_SEI), "POTE_SHA256": sha256}}


def _no_anterior(c, ant):
    achados = []
    for i in [c["OBJETO_ID"]] + list(c.get("ALIAS") or []):
        i = ant["ALIAS"].get(i, i)
        if i in ant["IDX"] and i not in achados:
            achados.append(i)
    return achados


def delta(cartoes: dict, anterior=None, causas_de_saida=None, corrida_parcial=False) -> dict:
    """Escreve DELTA em cada cartao e devolve {ANTERIOR, DELTA_CONTAGEM, SAIRAM, NAO_REVISTOS}.

    `anterior` = `ler_anterior(...)` ou None (primeira corrida: tudo NOVO, ANTERIOR = "NENHUM").
    `causas_de_saida` = {id_anterior: causa} — SAIU so com causa; sem causa, ausencia = SEM_REVISAO.
    Os cartoes sao percorridos de baixo para cima (RANK): o pai decide antes do filho, e o filho que so
    mudou pelo pai diz CAUSA = PAI_MUDOU(<ids>) (D125.2).
    """
    causas_de_saida = causas_de_saida or {}
    usados = set()
    ordem = sorted(cartoes, key=lambda i: (RANK.get(cartoes[i].get("ESPECIE"), 9), i))
    for oid in ordem:
        c = cartoes[oid]
        f = fecho(oid, cartoes)
        c["FECHO"] = {k: v for k, v in f.items() if not k.startswith("_")}
        agora = set(f["EVIDENCIAS"])
        proprias = {evidencia(p) for p in c.get("PROVA") or []}
        estado = _estado_do_objeto(c)
        if anterior is None:
            c["DELTA"] = {"MUDANCA": NOVO, "ESTADO_DE": NAO_SEI, "ESTADO_PARA": estado,
                          "EVIDENCIAS_NOVAS": sorted(agora), "EVIDENCIAS_REVOGADAS": [],
                          "CAUSA": "SEM_POTE_ANTERIOR", "GATILHO": sorted(agora), "RELACAO": NAO_SEI}
            continue
        ants = _no_anterior(c, anterior)
        usados.update(ants)
        if not ants:
            c["DELTA"] = {"MUDANCA": NOVO, "ESTADO_DE": NAO_SEI, "ESTADO_PARA": estado,
                          "EVIDENCIAS_NOVAS": sorted(agora), "EVIDENCIAS_REVOGADAS": [],
                          "CAUSA": "PRIMEIRA_VEZ_NESTA_PERGUNTA", "GATILHO": sorted(agora), "RELACAO": NAO_SEI}
            continue
        antes = set().union(*(anterior["IDX"][a]["EVIDENCIAS"] for a in ants))
        estados_antes = sorted({anterior["IDX"][a]["ESTADO"] for a in ants})
        estado_de = estados_antes[0] if len(estados_antes) == 1 else DIVERGENTE_ENTRE_LINKS
        novas, revog = sorted(agora - antes), sorted(antes - agora)
        if estado_de != estado:
            mud = MUDOU_ESTADO
        elif novas:
            mud = FORTALECEU
        elif revog:
            mud = ENFRAQUECEU
        else:
            mud = SEM_REVISAO
        pais = sorted(r["CROSSING_ID"] for r in c.get("REFERENCIAS") or []
                      if cartoes.get(r.get("CROSSING_ID"), {}).get("DELTA", {}).get("MUDANCA") not in (None, SEM_REVISAO))
        gatilho = set(novas) | set(revog)
        if mud == SEM_REVISAO and pais:
            # D125.2 · o pai mudou e o filho nao tem nada proprio: ele muda JUNTO, com a mudanca do pai mais
            # forte, a mesma causa e o mesmo gatilho — nunca «sem revisao» ao lado de um pai que mudou.
            mp = [cartoes[x]["DELTA"]["MUDANCA"] for x in pais]
            mud = next(m for m in (MUDOU_ESTADO, ENFRAQUECEU, FORTALECEU, NOVO) if m in mp)
            mud = FORTALECEU if mud == NOVO else mud
            for x in pais:
                gatilho |= set(cartoes[x]["DELTA"]["GATILHO"])
        if mud == SEM_REVISAO:
            causa = "NADA_NOVO_SOBRE_ESTA_PERGUNTA"
        elif (set(novas) | set(revog)) and not ((set(novas) | set(revog)) & proprias) and pais:
            causa = "PAI_MUDOU(%s)" % ",".join(pais)
        elif novas or revog:
            causa = "NOVA_EVIDENCIA" if novas else "EVIDENCIA_REVOGADA"
        elif pais:
            causa = "PAI_MUDOU(%s)" % ",".join(pais)
        else:
            causa = "NOVA_AVALIACAO (edicao da referencia, regra ou vocabulario)"
        c["DELTA"] = {"MUDANCA": mud, "ESTADO_DE": estado_de, "ESTADO_PARA": estado,
                      "EVIDENCIAS_NOVAS": novas, "EVIDENCIAS_REVOGADAS": revog, "CAUSA": causa,
                      "GATILHO": sorted(gatilho),
                      "RELACAO": c.get("RELACAO", NAO_SEI) if mud == MUDOU_ESTADO else NAO_SEI,
                      "ANTERIOR_IDS": ants}
    sairam, nao_revistos = [], []
    if anterior is not None:
        for a in sorted(set(anterior["IDX"]) - usados):
            if a in causas_de_saida and not _ign(causas_de_saida[a]):
                sairam.append({"CROSSING_ID": a, "ESTADO_DE": anterior["IDX"][a]["ESTADO"], "CAUSA": causas_de_saida[a]})
            else:
                nao_revistos.append({"CROSSING_ID": a, "ESTADO_DE": anterior["IDX"][a]["ESTADO"], "MUDANCA": SEM_REVISAO,
                                     "PORQUE": ("corrida parcial: " if corrida_parcial else "")
                                     + "ausente nesta corrida SEM causa — ausencia nao e saida (INT-LAW-215)"})
    cont = {m: 0 for m in MUDANCAS}
    for c in cartoes.values():
        cont[c["DELTA"]["MUDANCA"]] += 1
    cont[SEM_REVISAO] += len(nao_revistos)
    cont[SAIU] = len(sairam)
    return {"ANTERIOR": anterior["REF"] if anterior else "NENHUM", "DELTA_CONTAGEM": cont,
            "SAIRAM": sairam, "NAO_REVISTOS": nao_revistos}
