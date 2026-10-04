#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CARTAO DA FONTE — enriquecimento editorial das fontes ADMITIDAS ao Atlas.

    NAO INVENTAR. O RESUMO NUNCA SE BASEIA APENAS NO NOME.

Confirmado antes de escrever (requisito da missao):
    ATLAS_SOURCE_OF_TRUTH = docs/fontes/ATLAS-DE-FONTES-EAME.md  (o registry-mae)
    ATLAS_OWNER           = curadoria/escrever_no_atlas.py (acrescenta, nunca reescreve)
    ATLAS_WRITE_PATH      = docs/fontes/ATLAS-DE-FONTES-EAME.md
    ATLAS_SCHEMA          = SOURCE_ID/SOURCE_NAME/COUNTRY/TERRITORY/SOURCE_TYPE/URL/
                            CROPS/TOPICS/VERDICT/... (NAO tem SOURCE_SUMMARY,
                            EXPECTED_CONTENT, SINTONIA_RELEVANCE, KNOWN_LIMITATIONS,
                            SUMMARY_CONFIDENCE — medido)

Como o Atlas NAO tem os campos do cartao e o READY-SOURCES-V1.json e do
veredito_ready (nao se toca), este ficheiro e uma CAMADA de cartao sobre o Atlas,
referenciando o SOURCE_ID canonico — NAO e um segundo Atlas nem uma segunda
verdade de identidade (essa vive no ledger e no Atlas).

Cartao SO para fonte ADMITIDA (estado atual READY_FOR_COLLECTION no ledger).
NUNCA para CANDIDATE/PENDING/QUALIFY_IN_PROGRESS. RETRY/POLICY_BLOCK/
CAPABILITY_BLOCK/UNKNOWN nao aparecem como fonte aprovada.

Tudo DETERMINISTICO: o resumo compoe-se da evidencia JA observada na
caracterizacao (TOPICS/GEOGRAPHIES/CROPS/ACTIVITY/WHY_RELEVANT). Nao chama LLM;
nao volta a internet; nao inventa campos. Campo sem evidencia = UNKNOWN.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import lifecycle as LC          # noqa: E402
import telemetria_do_curador as T          # noqa: E402

ATLAS_MD   = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
ALLOC      = RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"
CARACT     = RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json"
CONTRATOS  = RAIZ / "curadoria" / "italy_contracts_curator.json"
CARDS      = RAIZ / "curadoria" / "SOURCE-CARDS-V1.json"

READY = LC.READY_FOR_COLLECTION
LLM_USED_FOR_SUMMARY = "NO"   # composto de evidencia estruturada; sem modelo


def _ler(p: Path, default):
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _alloc_por_sid() -> dict:
    d = _ler(ALLOC, {"NOVAS": []})
    return {n["SOURCE_ID"]: n for n in d.get("NOVAS", []) if n.get("SOURCE_ID")}


def _caract_por_candidate() -> dict:
    d = _ler(CARACT, {"FONTES": []})
    return {f["CANDIDATE_ID"]: f for f in d.get("FONTES", []) if f.get("CANDIDATE_ID")}


def _contrato_por_sid() -> dict:
    d = _ler(CONTRATOS, {"FONTES": []})
    return {c["SOURCE_ID"]: c for c in d.get("FONTES", []) if c.get("SOURCE_ID")}


def _admitidas() -> dict:
    """SOURCE_ID -> {READY_AT, EVIDENCE_REF} das fontes com estado ATUAL READY."""
    tr = T._ledger_transicoes()
    atual = {}
    ready_meta = {}
    for t in tr:
        atual[t["SOURCE_ID"]] = t["NEW_STATE"]
        if t["NEW_STATE"] == READY:
            ready_meta[t["SOURCE_ID"]] = {"READY_AT": t["OBSERVED_AT"],
                                          "EVIDENCE_REF": t.get("EVIDENCE_REF")}
    return {sid: ready_meta.get(sid, {}) for sid, st in atual.items() if st == READY}


def _confidence(car: dict | None) -> tuple[str, str]:
    """DETERMINISTICO, definido ANTES de usar (nao e confianca do modelo).

    HIGH   = identidade + tipo + conteudo observado + cobertura provada
    MEDIUM = identidade e conteudo provados, cobertura incompleta
    LOW    = identidade provada, pouca evidencia editorial
    """
    if not car:
        return "LOW", "sem ficha de caracterizacao: so identidade provada"
    tem_conteudo = bool([x for x in (car.get("CONTENT_TYPES") or []) if x and x != "UNKNOWN"]) \
        or bool([x for x in (car.get("TOPICS_OBSERVED") or []) if x and x != "UNKNOWN"])
    tem_cobertura = bool(car.get("GEOGRAPHIES_OBSERVED") or car.get("CROPS_OBSERVED"))
    estavel = str(car.get("SOURCE_PATTERN_STABLE", "")).upper().startswith(("SIM", "YES", "TRUE")) \
        or car.get("SOURCE_PATTERN_STABLE") is True
    if tem_conteudo and tem_cobertura and estavel:
        return "HIGH", "identidade + tipo + conteudo observado + cobertura provada"
    if tem_conteudo:
        return "MEDIUM", "identidade e conteudo provados, cobertura incompleta"
    return "LOW", "identidade provada, pouca evidencia editorial"


def _resumo(nome: str, car: dict | None, contrato: dict | None) -> str:
    """Resumo composto SO de evidencia observada. Sem nome-apenas, sem invencao."""
    if not car:
        return "Fonte admitida, mas descricao editorial ainda insuficiente."
    topicos = [x for x in (car.get("TOPICS_OBSERVED") or []) if x and x != "UNKNOWN"]
    ctypes = [x for x in (car.get("CONTENT_TYPES") or []) if x and x != "UNKNOWN"]
    geos = car.get("GEOGRAPHIES_OBSERVED") or []
    crops = car.get("CROPS_OBSERVED") or []
    why = (car.get("WHY_RELEVANT") or "").strip()
    if not (topicos or ctypes or why):
        return "Fonte admitida, mas descricao editorial ainda insuficiente."
    partes = []
    if ctypes:
        partes.append("Publica %s" % ", ".join(ctypes[:3]))
    if topicos:
        partes.append("sobre %s" % ", ".join(topicos[:3]))
    frase1 = (" ".join(partes) if partes else "Fonte agricola admitida").strip()
    frase1 = frase1[0].upper() + frase1[1:] + "."
    frase2 = ""
    if geos or crops:
        det = []
        if geos:
            det.append("regioes: %s" % ", ".join(geos[:3]))
        if crops:
            det.append("culturas: %s" % ", ".join(crops[:3]))
        frase2 = "Cobertura observada — %s." % "; ".join(det)
    frase3 = why if why else ""
    return " ".join(x for x in (frase1, frase2, frase3) if x).strip()


def _hash_evidencia(car: dict | None, contrato: dict | None, alloc: dict | None) -> str:
    base = {
        "car": {k: car.get(k) for k in
                ("CONTENT_TYPES", "TOPICS_OBSERVED", "GEOGRAPHIES_OBSERVED",
                 "CROPS_OBSERVED", "LANGUAGES_OBSERVED", "ACTIVITY", "UPDATE_PATTERN",
                 "WHY_RELEVANT", "SOURCE_PATTERN_STABLE", "CANONICAL_EXAMPLE")} if car else None,
        "contrato": {k: (contrato or {}).get(k) for k in
                     ("NAME", "TERRITORY", "OWNER", "OUTPUT_TYPE")} if contrato else None,
        "alloc": {k: (alloc or {}).get(k) for k in ("NOME", "URL", "TERRITORY", "FAMILY")} if alloc else None,
    }
    return hashlib.sha256(json.dumps(base, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()[:16]


def _tipo_de(car, contrato, alloc) -> str:
    fam = (car or {}).get("FAMILY") or (alloc or {}).get("FAMILY")
    if fam == "YOUTUBE":
        return "YOUTUBE_CHANNEL"
    if (contrato or {}).get("OUTPUT_TYPE") == "HTML" or fam == "HTML_SITE":
        return "HTML_SITE"
    return "UNKNOWN"


def _expected_content(car: dict | None) -> list:
    if not car:
        return ["UNKNOWN"]
    ct = [x for x in (car.get("CONTENT_TYPES") or []) if x and x != "UNKNOWN"]
    return ct or ["UNKNOWN"]


def gerar(agora: datetime | None = None) -> dict:
    """(Re)gera os cartoes das fontes admitidas. Idempotente por hash de evidencia."""
    n = (agora or datetime.now(timezone.utc)).isoformat()
    admit = _admitidas()
    alloc = _alloc_por_sid()
    cbyc = _caract_por_candidate()
    cont = _contrato_por_sid()
    antigos = _ler(CARDS, {"CARDS": {}}).get("CARDS", {})

    cards = {}
    for sid, meta in admit.items():
        a = alloc.get(sid)
        cand_id = (a or {}).get("CANDIDATE_ID")
        car = cbyc.get(cand_id) if cand_id else None
        c = cont.get(sid)

        nome = (c or {}).get("NAME") or (a or {}).get("NOME") or (car or {}).get("NOME") or "UNKNOWN"
        url = (c or {}).get("CANONICAL_ENTRY_URL") or (a or {}).get("URL") or (car or {}).get("URL") or "UNKNOWN"
        terr = (c or {}).get("TERRITORY") or (a or {}).get("TERRITORY") or "UNKNOWN"
        h = _hash_evidencia(car, c, a)

        prev = antigos.get(sid)
        criado = prev["SUMMARY_CREATED_AT"] if prev and prev.get("SUMMARY_EVIDENCE_HASH") else n
        # ⚠️ SE O HASH NAO MUDOU, REUTILIZAR. Evita gasto e drift de texto.
        if prev and prev.get("SUMMARY_EVIDENCE_HASH") == h:
            cards[sid] = prev
            continue

        conf, conf_reason = _confidence(car)
        card = {
            "SOURCE_ID": sid,
            "ATLAS_STATUS": "READY_FOR_COLLECTION",
            "SOURCE_NAME": nome,
            "SOURCE_TYPE": _tipo_de(car, c, a),
            "COUNTRY": "ITALY",
            "REGION": (car or {}).get("GEOGRAPHIES_OBSERVED") or "UNKNOWN",
            "LANGUAGE": ((car or {}).get("LANGUAGES_OBSERVED") or ["UNKNOWN"])[0]
            if (car or {}).get("LANGUAGES_OBSERVED") else "UNKNOWN",
            "TERRITORY": terr,
            "OFFICIAL_URL": url,
            "SOURCE_SUMMARY": _resumo(nome, car, c),
            "EXPECTED_CONTENT": _expected_content(car),
            "SINTONIA_RELEVANCE": (car or {}).get("WHY_RELEVANT") or "UNKNOWN",
            "KNOWN_COVERAGE": {
                "GEOGRAPHY": (car or {}).get("GEOGRAPHIES_OBSERVED") or "UNKNOWN",
                "CROPS": (car or {}).get("CROPS_OBSERVED") or "UNKNOWN",
                "TOPICS": [x for x in ((car or {}).get("TOPICS_OBSERVED") or []) if x != "UNKNOWN"] or "UNKNOWN",
                "PUBLICATION_FREQUENCY": (car or {}).get("UPDATE_PATTERN")
                or (car or {}).get("INITIAL_COLLECTION_CADENCE") or "UNKNOWN",
            },
            "KNOWN_LIMITATIONS": (car or {}).get("SAMPLE_LIMIT_NOTE") or (
                "Sem caracterizacao de conteudo: cartao gerado so da identidade e "
                "de um canario que resolveu." if not car else "UNKNOWN"),
            "SUMMARY_EVIDENCE": (car or {}).get("CANONICAL_EXAMPLE") or meta.get("EVIDENCE_REF") or "UNKNOWN",
            "SUMMARY_CONFIDENCE": conf,
            "SUMMARY_CONFIDENCE_REASON": conf_reason,
            "READY_AT": meta.get("READY_AT"),
            "SUMMARY_EVIDENCE_HASH": h,
            "SUMMARY_CREATED_AT": criado,
            "SUMMARY_UPDATED_AT": n,
            "LLM_USED_FOR_SUMMARY": LLM_USED_FOR_SUMMARY,
        }
        cards[sid] = card

    saida = {
        "DATASET": "SOURCE-CARDS-V1",
        "O_QUE_ISTO_E": ("camada de cartao editorial sobre o Atlas. Enriquece o "
                         "SOURCE_ID canonico; NAO e um segundo Atlas nem verdade de "
                         "identidade (essa vive no ledger e em ATLAS-DE-FONTES-EAME.md)."),
        "ATLAS_SOURCE_OF_TRUTH": "docs/fontes/ATLAS-DE-FONTES-EAME.md",
        "ATLAS_OWNER": "curadoria/escrever_no_atlas.py",
        "LLM_USED_FOR_SUMMARY": LLM_USED_FOR_SUMMARY,
        "GERADO_EM": n,
        "TOTAL": len(cards),
        "CARDS": cards,
    }
    return saida


def escrever(saida: dict | None = None) -> dict:
    saida = saida or gerar()
    CARDS.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    return saida


def cartoes_navegaveis(sids: list[str]) -> list[dict]:
    """De uma lista de SOURCE_ID -> os cartoes reais, para navegar do numero a fonte."""
    cards = _ler(CARDS, {"CARDS": {}}).get("CARDS", {})
    out = []
    for sid in sids:
        c = cards.get(sid)
        if c:
            out.append({"SOURCE_ID": sid, "SOURCE_NAME": c["SOURCE_NAME"],
                        "SOURCE_TYPE": c["SOURCE_TYPE"],
                        "SUMMARY_CURTO": c["SOURCE_SUMMARY"][:120],
                        "READY_AT": c.get("READY_AT")})
        else:
            out.append({"SOURCE_ID": sid, "SOURCE_NAME": "UNKNOWN",
                        "SUMMARY_CURTO": "cartao ainda nao gerado", "READY_AT": None})
    return out


def main() -> int:
    s = escrever()
    print("cartoes gerados: %d (LLM_USED_FOR_SUMMARY=%s)"
          % (s["TOTAL"], s["LLM_USED_FOR_SUMMARY"]))
    from collections import Counter
    conf = Counter(c["SUMMARY_CONFIDENCE"] for c in s["CARDS"].values())
    print("por confianca:", dict(conf))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
