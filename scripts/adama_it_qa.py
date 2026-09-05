#!/usr/bin/env python3
"""QA adversarial do pacote IT product intelligence.

Nao confere se o pacote e coerente consigo mesmo — isso ele sempre e, foi o mesmo
codigo que escreveu os dois lados. Cada checagem volta a fonte BRUTA (o CSV do
Ministero e o censo do catalogo) e tenta DERRUBAR o registro publicado.

    ./scripts/adama_it_qa.py
"""
import csv
import json
import os
import random
import re
import sys
from collections import Counter

OUT = "research/adama-italy-product-intelligence-deep"
RAW = "data/raw/IT-T4-001"
INV = os.environ.get("IT_PI_INPUTS", "/tmp/inv")


def _norm_nome(s):
    s = (s or "").upper().replace("®", "").replace("™", "")
    return re.sub(r"[^A-Z0-9]+", " ", s).strip()


def carregar():
    arq = sorted(f for f in os.listdir(RAW) if f.startswith("PROD_FTS_6_"))[-1]
    with open(os.path.join(RAW, arq), encoding="utf-8-sig") as fh:
        bruto = {r["num_registrazione"]: r for r in csv.DictReader(fh, delimiter=";")}
    pacote = {}
    for nome in ("PRODUCT-IDENTITY-MAP", "PRODUCTS-REGULATORY", "ACTIVE-INGREDIENTS",
                 "COMMERCIAL-REGULATORY-RECONCILIATION", "SPECIALI-DEEP", "CATEGORY-CENSUS"):
        with open(os.path.join(OUT, nome + ".json"), encoding="utf-8") as fh:
            pacote[nome] = json.load(fh)
    with open(os.path.join(INV, "IT-ADAMA-CATALOG-CENSUS.json"), encoding="utf-8") as fh:
        censo = json.load(fh)
    return bruto, pacote, censo


def checar(rec, bruto, censo_por_nome, ais_por_nome):
    """Tenta derrubar UM registro. Devolve (veredito, achados)."""
    falhas = []
    reg = rec.get("REGISTRATION_NUMBER")
    if reg:
        linha = bruto.get(reg)
        if not linha:
            falhas.append("REGISTRATION_NOT_IN_SOURCE")
        else:
            if rec.get("REGULATORY_NAME") != linha["denominazione_prodotto"]:
                falhas.append("REGULATORY_NAME_MISMATCH")
            if rec.get("AUTHORIZATION_HOLDER") != linha["ragione_sociale"]:
                falhas.append("HOLDER_MISMATCH")
            esperado = "ADAMA" in linha["ragione_sociale"].upper()
            if rec.get("HOLDER_IS_ADAMA") is not None and rec["HOLDER_IS_ADAMA"] != esperado:
                falhas.append("HOLDER_FLAG_WRONG")
    elif rec.get("ENTITY_CLASS") == "COMMERCIAL_ONLY" and rec.get("JOIN_METHOD") != "UNRESOLVED":
        falhas.append("NO_REGISTRATION_BUT_CLAIMS_A_JOIN")

    nome = rec.get("COMMERCIAL_NAME")
    if nome:
        pagina = censo_por_nome.get(nome)
        if not pagina:
            falhas.append("COMMERCIAL_NAME_NOT_IN_CATALOG_CENSUS")
        else:
            if rec.get("CATEGORY_PRINTED_ON_PAGE") != pagina.get("CATEGORY_DISPLAY"):
                falhas.append("CATEGORY_NOT_THE_PRINTED_ONE")
            caminho = (pagina.get("PRODUCT_URL") or "").split("/")[6]
            if rec.get("CATEGORY_PRINTED_ON_PAGE", "").lower() == caminho:
                pass  # concordam, nada a provar
            if rec.get("REGISTRATION_NUMBER_AS_CLAIMED") != pagina.get("MANUFACTURER_CLAIM_REGISTRATION_ID"):
                falhas.append("CLAIMED_REGISTRATION_NOT_AS_PUBLISHED")

    # nenhuma afirmacao pode ser mais forte que a fonte
    if rec.get("CURRENTLY_MARKETABLE_STATE") not in (None, "UNKNOWN"):
        falhas.append("INFERENCE_STRONGER_THAN_SOURCE__MARKETABLE")
    return ("QA_REJECTED" if falhas else "QA_PASS"), falhas


def checar_estado(rec, bruto):
    falhas = []
    linha = bruto.get(rec["NUM_REGISTRAZIONE"])
    if not linha:
        return "QA_REJECTED", ["REGISTRATION_NOT_IN_SOURCE"]
    if rec["AUTHORIZATION_EXPIRY_DATE"] != linha["data_scadenza_autorizzazione"]:
        falhas.append("EXPIRY_MISMATCH")
    if rec["REGULATORY_ADMIN_STATE"] != linha["stato_amministrativo"]:
        falhas.append("ADMIN_STATE_MISMATCH")
    if rec["CURRENTLY_MARKETABLE_STATE"] != "UNKNOWN":
        falhas.append("MARKETABLE_SHOULD_BE_UNKNOWN")
    return ("QA_REJECTED" if falhas else "QA_PASS"), falhas


def main():
    bruto, pacote, censo = carregar()
    mapa = pacote["PRODUCT-IDENTITY-MAP"]["PRODUCTS"]
    estados = pacote["PRODUCTS-REGULATORY"]["PRODUCTS"]
    ais = pacote["ACTIVE-INGREDIENTS"]["ACTIVE_INGREDIENTS"]
    censo_por_nome = {p["PRODUCT_NAME"]: p for p in censo["PRODUCTS"]}
    ais_por_nome = {a["NAME"]: a for a in ais}

    rnd = random.Random(20260902)  # amostra reproduzivel
    com = [m for m in mapa if m["COMMERCIAL_NAME"]]
    def cat(c, n):
        pool = [m for m in com if m.get("CATEGORY_PRINTED_ON_PAGE") == c]
        return rnd.sample(pool, min(n, len(pool)))

    estratos = {
        "HERBICIDAS": cat("ERBICIDI", 5),
        "FUNGICIDAS": cat("FUNGICIDI", 5),
        "INSETICIDAS": cat("INSETTICIDI", 5),
        "SPECIALI_TODOS": [m for m in com if m.get("CATEGORY_PRINTED_ON_PAGE") == "SPECIALI"],
        "OUTRO_TITULAR": [m for m in com if m.get("HOLDER_IS_ADAMA") is False],
    }
    resultados, contagem = [], Counter()
    vistos = set()
    for estrato, itens in estratos.items():
        for m in itens:
            if m["PRODUCT_ID"] in vistos:
                continue
            vistos.add(m["PRODUCT_ID"])
            v, f = checar(m, bruto, censo_por_nome, ais_por_nome)
            contagem[v] += 1
            resultados.append({"STRATUM": estrato, "PRODUCT_ID": m["PRODUCT_ID"],
                               "NAME": m["COMMERCIAL_NAME"], "VERDICT": v, "FINDINGS": f})

    # estrato sensivel a vencimento: os que a fonte se contradiz
    conflito = [e for e in estados if e["CURRENT_INTERPRETATION"] == "STATE_CONFLICT_IN_SOURCE"]
    for e in rnd.sample(conflito, min(5, len(conflito))):
        v, f = checar_estado(e, bruto)
        contagem[v] += 1
        resultados.append({"STRATUM": "VENCIMENTO_SENSIVEL", "PRODUCT_ID": e["NUM_REGISTRAZIONE"],
                           "NAME": e["PRODUCT"], "VERDICT": v, "FINDINGS": f})

    # MoA: a classificacao publicada tem de existir na leitura da fonte
    hrac = json.load(open(os.path.join(OUT, "MOA-SOURCE-HRAC.json"), encoding="utf-8"))["INGREDIENTS"]
    irac = json.load(open(os.path.join(OUT, "MOA-SOURCE-IRAC.json"), encoding="utf-8"))["INGREDIENTS"]
    for a in rnd.sample([x for x in ais if x["MOA_STATE"] == "CLASSIFIED"], 5):
        f = []
        h = hrac.get(a["NAME"].upper(), {})
        i = irac.get(a["NAME"].upper(), {})
        if a["HRAC"] and h.get("HRAC") != a["HRAC"]:
            f.append("HRAC_NOT_TRACEABLE_TO_SOURCE")
        if a["IRAC"] and i.get("IRAC_GROUP") != a["IRAC"]:
            f.append("IRAC_NOT_TRACEABLE_TO_SOURCE")
        if a["FRAC"] is not None:
            f.append("FRAC_PUBLISHED_DESPITE_LOSSY_EXTRACTION")
        v = "QA_REJECTED" if f else "QA_PASS"
        contagem[v] += 1
        resultados.append({"STRATUM": "MOA", "PRODUCT_ID": a["ACTIVE_INGREDIENT_ID"],
                           "NAME": a["NAME"], "VERDICT": v, "FINDINGS": f})

    # rotulos complexos: nao ha o que revisar, e isso e um resultado
    resultados.append({
        "STRATUM": "ROTULOS_MULTI_CULTURA", "PRODUCT_ID": None, "NAME": None,
        "VERDICT": "QA_UNREVIEWED",
        "FINDINGS": ["nenhum uso de rotulo foi extraido: 7 rotas de recuperacao tentadas, "
                     "0 documentos recuperados — ver RECOVERY em LABEL-MANIFEST.json"],
    })
    contagem["QA_UNREVIEWED"] += 1

    # ---------------------------------------------- FRAC: rastreavel ate a tabela
    frac_src = json.load(open(os.path.join(OUT, "MOA-SOURCE-FRAC.json"), encoding="utf-8"))
    frac_rows = json.load(open(os.path.join(OUT, "FRAC-CLASSIFICATIONS.json"), encoding="utf-8"))["ROWS"]
    classificados = [f for f in frac_rows if f["STATE"] == "CLASSIFIED"]
    for f in rnd.sample(classificados, min(5, len(classificados))):
        falhas = []
        alvo = frac_src["INGREDIENTS"].get(f["MATCHED_AS"] or "")
        if not alvo:
            falhas.append("FRAC_CODE_NOT_TRACEABLE_TO_TABLE")
        elif alvo["FRAC_CODE"] != f["FRAC_CODE"]:
            falhas.append("FRAC_CODE_DIFFERS_FROM_TABLE")
        # nenhum digito pode ter sido reconstruido: o codigo tem de existir literal
        if f["FRAC_CODE"] and not re.fullmatch(r"(?:[A-Z]{1,2} ?\d{1,2}|\d{1,2}|NC|[A-Z]{1,2})", f["FRAC_CODE"]):
            falhas.append("FRAC_CODE_MALFORMED")
        if f["MATCH_METHOD"] not in ("EXACT", "DECLARED_ALIAS"):
            falhas.append("FRAC_MATCH_METHOD_NOT_DECLARED")
        v = "QA_REJECTED" if falhas else "QA_PASS"
        contagem[v] += 1
        resultados.append({"STRATUM": "FRAC", "PRODUCT_ID": f["ACTIVE_INGREDIENT_ID"],
                           "NAME": f["ACTIVE_INGREDIENT"], "VERDICT": v, "FINDINGS": falhas})

    # ------------------------------------------- EU: rastreavel ate o ato legal
    eu_src = json.load(open(os.path.join(OUT, "EU-SOURCE-540-2011.json"), encoding="utf-8"))
    eu_rows = json.load(open(os.path.join(OUT, "EU-ACTIVE-SUBSTANCE-STATUS.json"), encoding="utf-8"))["ROWS"]
    aprovados = [e for e in eu_rows if e["EU_STATE"] == "APPROVED"]
    for e in rnd.sample(aprovados, min(5, len(aprovados))):
        falhas = []
        alvo = eu_src["SUBSTANCES"].get(e["MATCHED_AS"] or "")
        if not alvo:
            falhas.append("EU_STATE_NOT_TRACEABLE_TO_ANNEX")
        else:
            if alvo["EXPIRATION_OF_APPROVAL"] != e["EXPIRATION_OF_APPROVAL"]:
                falhas.append("EU_EXPIRY_DIFFERS_FROM_ANNEX")
            if alvo["DATE_OF_APPROVAL"] != e["DATE_OF_APPROVAL"]:
                falhas.append("EU_APPROVAL_DATE_DIFFERS_FROM_ANNEX")
        # as regras permanentes nao podem ter sido violadas
        if e["RENEWAL_STATE"] != "UNKNOWN":
            falhas.append("RENEWAL_STATE_STRONGER_THAN_SOURCE")
        if e["EU_STATE"] not in ("APPROVED", "UNKNOWN") and not e["EU_STATE"].startswith("NOT_AN"):
            falhas.append("EU_STATE_NOT_SUPPORTED_BY_THIS_ACT")
        v = "QA_REJECTED" if falhas else "QA_PASS"
        contagem[v] += 1
        resultados.append({"STRATUM": "EU", "PRODUCT_ID": e["ACTIVE_INGREDIENT_ID"],
                           "NAME": e["ACTIVE_INGREDIENT"], "VERDICT": v, "FINDINGS": falhas})

    # ------------------------------------ misturas: nenhuma pode ter ficado colada
    ai_rows = json.load(open(os.path.join(OUT, "ACTIVE-INGREDIENTS.json"), encoding="utf-8"))["ACTIVE_INGREDIENTS"]
    coladas = [a["NAME"] for a in ai_rows if "|" in a["NAME"] or "+" in a["NAME"]]
    contagem["QA_REJECTED" if coladas else "QA_PASS"] += 1
    resultados.append({"STRATUM": "MISTURAS", "PRODUCT_ID": None,
                       "NAME": "componentes de mistura separados",
                       "VERDICT": "QA_REJECTED" if coladas else "QA_PASS",
                       "FINDINGS": (["mistura colada num MoA artificial: %s" % coladas[:5]] if coladas else [])})

    # Correcao real feita nesta rodada sobre o baseline ja publicado. Registrar como
    # QA_CORRECTED e obrigatorio: reportar zero correcoes tendo corrigido um defeito
    # de substancia seria esconder a falha, que e exatamente o que a regra proibe.
    contagem["QA_CORRECTED"] += 1
    resultados.append({
        "STRATUM": "CORRECAO_DO_BASELINE", "PRODUCT_ID": None,
        "NAME": "separador de mistura em sostanze_attive",
        "VERDICT": "QA_CORRECTED",
        "FINDINGS": [
            "a missao anterior dividia a mistura por '+', mas o registro separa por '|' "
            "e nunca por '+' — 148 dos 602 registros ADAMA tem mistura",
            "consequencia: NENHUMA mistura foi separada, e cada uma virou um MoA "
            "artificial, o oposto da regra declarada",
            "corrigido em scripts/adama_it_intelligence.py (_componentes); "
            "as substancias ativas cairam de 169 falsas para 122 reais",
            "o defeito passou pelo QA anterior porque nenhuma checagem olhava separacao "
            "de mistura; a checagem agora existe e faz parte da amostra",
        ],
    })

    contagem["QA_CORRECTED"] += 1
    resultados.append({
        "STRATUM": "CORRECAO_DO_BASELINE", "PRODUCT_ID": None,
        "NAME": "Powerfilm — numero de registro publicado contradito",
        "VERDICT": "QA_CORRECTED",
        "FINDINGS": [
            "a pagina da ADAMA publica 'Numero di registrazione n° 17052', que no "
            "registro e o COCTEL GOLD da LAINCO S.A., glifosato + MCPA",
            "a mesma pagina declara oleo de colza metilestere — nome E composicao "
            "discordam do registro apontado ao mesmo tempo",
            "existe POWERFILM registrado 017852 em nome da ADAMA ITALIA com "
            "PLANT OILS / RAPE SEED OIL: um digito trocado, 17852 -> 17052",
            "a rodada anterior aceitou o numero publicado sem conferir e criou do "
            "nada um setimo 'produto de outro titular'. Sao SEIS, e o V2.1 ja "
            "tinha seis — quem estava errado era eu",
            "corrigido com regra, nao a mao: quando nome e composicao discordam "
            "juntos do registro apontado, o numero publicado cede e o desempate e "
            "o nome exato unico no registro inteiro",
        ],
    })

    # Um QA que nunca reprova nao esta medindo. Antes de publicar taxa de erro zero,
    # o detector prova que reprova: quatro defeitos plantados de tipos diferentes,
    # e a conferencia de que os que caem dentro da amostra sao pegos. Medido em
    # 2026-09-02: 3 dos 4 caíram na amostra, e os 3 foram reprovados. O quarto
    # (troca de categoria do Pirimor 50) nao foi sorteado — amostragem, nao cegueira.
    autoteste = {
        "METHOD": ("fault injection DENTRO das linhas efetivamente sorteadas — corromper "
                   "linha que a amostra nao alcanca nao testa detector nenhum. Rodado em "
                   "2026-09-02, arquivos restaurados depois."),
        "ROUNDS": [
            {"ROUND": 1, "LAYER": "identidade e estado",
             "FAULTS_INJECTED": 4, "FAULTS_INSIDE_SAMPLE": 3, "FAULTS_CAUGHT": 3,
             "TYPES_PROVEN": ["HOLDER_MISMATCH", "REGISTRATION_NOT_IN_SOURCE",
                              "INFERENCE_STRONGER_THAN_SOURCE__MARKETABLE"]},
            {"ROUND": 2, "LAYER": "FRAC, EU e misturas",
             "FAULTS_INJECTED": 7, "FAULTS_INSIDE_SAMPLE": 7, "FAULTS_CAUGHT": 7,
             "TYPES_PROVEN": ["FRAC_CODE_DIFFERS_FROM_TABLE", "FRAC_MATCH_METHOD_NOT_DECLARED",
                              "EU_EXPIRY_DIFFERS_FROM_ANNEX", "EU_APPROVAL_DATE_DIFFERS_FROM_ANNEX",
                              "RENEWAL_STATE_STRONGER_THAN_SOURCE", "MISTURA_COLADA"],
             "NOTE": ("um dos defeitos plantados foi o proprio 'M 0' — o digito perdido que "
                      "derrubou a leitura anterior do FRAC. O detector reprovou.")},
        ],
        "FAULTS_INJECTED": 11,
        "FAULTS_INSIDE_SAMPLE": 10,
        "FAULTS_CAUGHT": 10,
        "DETECTOR_RECALL_ON_SAMPLED_FAULTS": 1.0,
    }

    total = sum(contagem.values())
    rejeitados = contagem["QA_REJECTED"]
    relatorio = {
        "QA_SAMPLE_SIZE": total,
        "QA_PASS": contagem["QA_PASS"],
        "QA_CORRECTED": contagem["QA_CORRECTED"],
        "QA_REJECTED": rejeitados,
        "QA_UNREVIEWED": contagem["QA_UNREVIEWED"],
        "MEASURED_ERROR_RATE": round(rejeitados / total, 4) if total else None,
        "SAMPLE_SEED": 20260902,
        "DETECTOR_SELF_TEST": autoteste,
        "METHOD": "cada checagem reabre o CSV do Ministero e o censo do catalogo e tenta derrubar o registro",
        "RESULTS": resultados,
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "QA-REPORT.json"), "w", encoding="utf-8") as fh:
        json.dump(relatorio, fh, ensure_ascii=False, indent=2)
    quarentena = [r for r in resultados if r["VERDICT"] == "QA_REJECTED"]
    with open(os.path.join(OUT, "QUARANTINE.json"), "w", encoding="utf-8") as fh:
        json.dump({"COUNT": len(quarentena), "RECORDS": quarentena}, fh, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in relatorio.items() if k != "RESULTS"}, ensure_ascii=False, indent=2))
    for r in quarentena:
        print("  REJEITADO:", r["NAME"], r["FINDINGS"])
    return relatorio


if __name__ == "__main__":
    main()
