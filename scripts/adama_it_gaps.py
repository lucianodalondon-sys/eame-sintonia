#!/usr/bin/env python3
"""Fecha os dois gaps que a fonte permitiu fechar: FRAC e estado EU.

O terceiro — conteudo das etichette — continua aberto e o motivo esta medido em
LABEL-MANIFEST.json. Aqui nada e inventado no lugar dele.

    ./scripts/adama_it_gaps.py

Entradas ja gravadas no pacote:
    MOA-SOURCE-FRAC.json      (./scripts/adama_it_frac.py)
    MOA-SOURCE-HRAC/IRAC.json (./scripts/adama_it_moa.py)
    EU-SOURCE-540-2011.json   (./scripts/adama_it_eu.py)
    ACTIVE-INGREDIENTS.json, PRODUCT-IDENTITY-MAP.json (./scripts/adama_it_intelligence.py)
"""
import json
import os
import re
from collections import Counter, defaultdict
from datetime import date

OUT = "research/adama-italy-product-intelligence-deep"

# Aliases EXPLICITOS. Nao ha casamento aproximado em lugar nenhum deste arquivo:
# cada linha e uma equivalencia que a propria fonte escreve — sinonimo entre
# parenteses no registro italiano, hifenizacao, ou o nome do sal.
ALIASES = {
    "ABAMECTIN (AKA AVERMECTIN)": "ABAMECTIN",
    "IMAZALIL (AKA ENILCONAZOLE)": "IMAZALIL",
    "FLONICAMID (IKI-220)": "FLONICAMID",
    "BENSULFURON METHYL": "BENSULFURON-METHYL",
    "FOSETYL-ALUMINIUM": "FOSETYL-AL",
    "POTASSIUM PHOSPHONATES (FORMERLY POTASSIUM PHOSPHITE)": "POTASSIUM PHOSPHONATES",
    # O proprio Anexo escreve "Mesosulfuron (parent) / Mesosulfuron-methyl (variant)"
    # na mesma linha, com o mesmo CAS. A equivalencia vem da fonte, nao de quimica minha.
    "MESOSULFURON-METHYL": "MESOSULFURON",
}

# Fitoprotetores (safeners) nao sao substancias ativas e nao entram no Anexo do
# 540/2011 — eles tem lista propria. Ausencia deles ali nao e desconhecimento: e a
# resposta certa, e fica dita com esse nome em vez de virar um UNKNOWN generico.
SAFENERS = {"ISOXADIFEN ETHYL", "MEFENPYR DIETHYL", "CLOQUINTOCET MEXYL", "BENOXACOR",
            "DICHLORMID", "FURILAZOLE", "MEFENPYR-DIETHYL", "ISOXADIFEN-ETHYL"}


def _ler(nome):
    with open(os.path.join(OUT, nome), encoding="utf-8") as fh:
        return json.load(fh)


def _grava(nome, obj):
    with open(os.path.join(OUT, nome), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)


def chaves(nome):
    """A chave da propria substancia e, quando existe, o alias declarado."""
    n = nome.upper().strip()
    return [n] + ([ALIASES[n]] if n in ALIASES else [])


def main():
    ais = _ler("ACTIVE-INGREDIENTS.json")["ACTIVE_INGREDIENTS"]
    mapa = _ler("PRODUCT-IDENTITY-MAP.json")["PRODUCTS"]
    frac = _ler("MOA-SOURCE-FRAC.json")
    hrac = _ler("MOA-SOURCE-HRAC.json")["INGREDIENTS"]
    irac = _ler("MOA-SOURCE-IRAC.json")["INGREDIENTS"]
    eu = _ler("EU-SOURCE-540-2011.json")
    hoje = date.today().isoformat()

    por_reg = defaultdict(list)
    for m in mapa:
        if m["REGISTRATION_NUMBER"]:
            por_reg[m["REGISTRATION_NUMBER"]].append(m)

    # ------------------------------------------------------------- FRAC
    frac_linhas = []
    for a in ais:
        achado = next((frac["INGREDIENTS"][k] for k in chaves(a["NAME"])
                       if k in frac["INGREDIENTS"]), None)
        usado = next((k for k in chaves(a["NAME"]) if k in frac["INGREDIENTS"]), None)
        frac_linhas.append({
            "ACTIVE_INGREDIENT": a["NAME"],
            "ACTIVE_INGREDIENT_ID": a["ACTIVE_INGREDIENT_ID"],
            "FRAC_CODE": achado["FRAC_CODE"] if achado else None,
            "FRAC_GROUP": achado["FRAC_CODE"] if achado else None,
            "SOURCE_URL": frac["SOURCE_URL"] if achado else None,
            "SOURCE_VERSION": frac["SOURCE_VERSION"] if achado else None,
            "SOURCE_CITATION": (frac["SOURCE_CITATION"] + ", pagina %s" % achado["PAGE"]) if achado else None,
            "DOCUMENT_SHA256": frac["DOCUMENT_SHA256"] if achado else None,
            "MATCHED_AS": usado,
            "MATCH_METHOD": ("EXACT" if usado == a["NAME"].upper()
                             else "DECLARED_ALIAS" if usado else None),
            "CONFIDENCE": "HIGH" if achado else "NONE",
            "STATE": "CLASSIFIED" if achado else "UNKNOWN",
            "REGISTRATION_NUMBERS": a["REGISTRATION_NUMBERS"],
        })
    _grava("FRAC-CLASSIFICATIONS.json", {
        "BUILT_AT": hoje, **{k: frac[k] for k in ("SOURCE", "SOURCE_URL", "SOURCE_VERSION",
                                                  "DOCUMENT_SHA256", "METHOD", "NO_DIGIT_RECONSTRUCTED")},
        "NOTE": ("codigo lido por geometria da tabela; nenhum digito reconstruido. "
                 "Substancia sem linha na tabela sai UNKNOWN, nao sai com palpite."),
        "CLASSIFIED": sum(1 for f in frac_linhas if f["STATE"] == "CLASSIFIED"),
        "UNKNOWN": sum(1 for f in frac_linhas if f["STATE"] == "UNKNOWN"),
        "ROWS": frac_linhas,
    })

    # --------------------------------------------------------------- EU
    subs = eu["SUBSTANCES"]
    eu_linhas = []
    for a in ais:
        a_nome = a["NAME"].upper().strip()
        usado = next((k for k in chaves(a["NAME"]) if k in subs), None)
        s = subs.get(usado) if usado else None
        eu_linhas.append({
            "ACTIVE_INGREDIENT": a["NAME"],
            "ACTIVE_INGREDIENT_ID": a["ACTIVE_INGREDIENT_ID"],
            "EU_STATE": ("APPROVED" if s else
                         "NOT_AN_ACTIVE_SUBSTANCE__SAFENER" if a_nome in SAFENERS else "UNKNOWN"),
            "EU_STATE_WHY": (
                "consta do Anexo do Reg. 540/2011 na consolidacao %s" % eu["CONSOLIDATION_DATE"]
                if s else
                "e fitoprotetor (safener), nao substancia ativa: nao se espera no Anexo do 540/2011"
                if a_nome in SAFENERS else
                "nao consta do Anexo. Ausencia NAO prova NON_RENEWED: pode nunca ter sido "
                "aprovada, ou ter saido por ato que esta coleta nao leu"),
            "DATE_OF_APPROVAL": s["DATE_OF_APPROVAL"] if s else None,
            "EXPIRATION_OF_APPROVAL": s["EXPIRATION_OF_APPROVAL"] if s else None,
            "CAS": s["CAS"] if s else None,
            "CIPAC": s["CIPAC"] if s else None,
            "LATEST_RELEVANT_COMMISSION_ACT": eu["CELEX"] if s else None,
            "SCOPAFF_EVIDENCE": "UNKNOWN",
            "EFSA_EVIDENCE": "UNKNOWN",
            "RENEWAL_STATE": "UNKNOWN",
            "RENEWAL_STATE_WHY": ("o ato legal prova aprovacao e expiracao; nao prova renovacao "
                                  "em curso, projeto de nao-renovacao nem revisao do art. 21. "
                                  "A EU Pesticides Database, que traria isso, devolve 307 -> "
                                  "sorry.ec.europa.eu deste ambiente"),
            "SOURCE_URL": eu["SOURCE_URL"] if s else None,
            "DOCUMENT_DATE": eu["CONSOLIDATION_DATE"] if s else None,
            "MATCHED_AS": usado,
            "MATCH_METHOD": ("EXACT" if usado == a["NAME"].upper()
                             else "DECLARED_ALIAS" if usado else None),
        })
    _grava("EU-ACTIVE-SUBSTANCE-STATUS.json", {
        "BUILT_AT": hoje, "SOURCE": eu["SOURCE"], "SOURCE_URL": eu["SOURCE_URL"],
        "CELEX": eu["CELEX"], "CONSOLIDATION_DATE": eu["CONSOLIDATION_DATE"],
        "RULES": eu["RULES"],
        "CHECKED": len(eu_linhas),
        "RESOLVED": sum(1 for e in eu_linhas if e["EU_STATE"] == "APPROVED"),
        "NOT_ACTIVE_SUBSTANCE_SAFENER": sum(1 for e in eu_linhas if e["EU_STATE"].startswith("NOT_AN")),
        "UNKNOWN": sum(1 for e in eu_linhas if e["EU_STATE"] == "UNKNOWN"),
        "STATES_NOT_OBTAINABLE_FROM_THIS_SOURCE": [
            "APPROVAL_EXTENDED", "RENEWAL_UNDER_REVIEW", "DRAFT_NON_RENEWAL",
            "ARTICLE_21_REVIEW", "NON_RENEWED"],
        "ROWS": eu_linhas,
    })

    # ------------------------------------- EU -> produtos italianos -> catalogo
    por_ai = {a["NAME"]: a for a in ais}
    rel = []
    for e in eu_linhas:
        if e["EU_STATE"] != "APPROVED":
            continue
        a = por_ai[e["ACTIVE_INGREDIENT"]]
        regs = a["REGISTRATION_NUMBERS"]
        comercial = sorted({m["COMMERCIAL_NAME"] for r in regs for m in por_reg.get(r, [])
                            if m["COMMERCIAL_NAME"]})
        rel.append({
            "ACTIVE_INGREDIENT": e["ACTIVE_INGREDIENT"],
            "EU_STATE": e["EU_STATE"],
            "EU_EXPIRATION_OF_APPROVAL": e["EXPIRATION_OF_APPROVAL"],
            "ITALIAN_REGISTRATIONS": regs,
            "ITALIAN_REGISTRATION_COUNT": len(regs),
            "COMMERCIAL_CATALOG_PRODUCTS": comercial,
            "COMMERCIAL_CATALOG_COUNT": len(comercial),
            "VERIFIED_LABEL_CROPS": [],
            "VERIFIED_LABEL_CROPS_WHY": "nenhuma etichetta foi lida; ver LABEL-MANIFEST.json",
            "NOT_A_CLAIM": ("relacao candidata factual. Estado EU nao e comercializacao na "
                            "Italia, e expiracao de aprovacao nao e risco, retirada nem perda"),
        })
    rel.sort(key=lambda r: (r["EU_EXPIRATION_OF_APPROVAL"] or "9999", -r["COMMERCIAL_CATALOG_COUNT"]))
    _grava("REGULATORY-FUTURE-DEEP.json", {
        "BUILT_AT": hoje, "STATE": "PARTIAL",
        "SOURCE": eu["SOURCE"], "SOURCE_URL": eu["SOURCE_URL"], "CELEX": eu["CELEX"],
        "WHAT_IS_CLOSED": "APPROVED e data de expiracao da aprovacao, por substancia, ligados aos produtos italianos e ao catalogo",
        "WHAT_IS_STILL_OPEN": ["RENEWAL_UNDER_REVIEW", "DRAFT_NON_RENEWAL", "ARTICLE_21_REVIEW",
                               "APPROVAL_EXTENDED", "SCoPAFF", "EFSA"],
        "WHY_STILL_OPEN": "EU Pesticides Database: 307 -> sorry.ec.europa.eu em toda rota de dados, com e sem cabecalho de navegador",
        "RULES": eu["RULES"],
        "COUNT": len(rel),
        "RELATIONSHIPS": rel,
    })

    resumo = {
        "FRAC_CLASSIFIED": sum(1 for f in frac_linhas if f["STATE"] == "CLASSIFIED"),
        "FRAC_UNKNOWN": sum(1 for f in frac_linhas if f["STATE"] == "UNKNOWN"),
        "EU_CHECKED": len(eu_linhas),
        "EU_RESOLVED": sum(1 for e in eu_linhas if e["EU_STATE"] == "APPROVED"),
        "EU_SAFENERS": sum(1 for e in eu_linhas if e["EU_STATE"].startswith("NOT_AN")),
        "EU_UNKNOWN": sum(1 for e in eu_linhas if e["EU_STATE"] == "UNKNOWN"),
        "PRODUCT_EU_RELATIONSHIPS": len(rel),
        "EU_LINKED_TO_COMMERCIAL": sum(1 for r in rel if r["COMMERCIAL_CATALOG_COUNT"]),
        "ALIASES_USED": sum(1 for f in frac_linhas if f["MATCH_METHOD"] == "DECLARED_ALIAS"),
    }
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    return resumo


if __name__ == "__main__":
    main()
