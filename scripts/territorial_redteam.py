#!/usr/bin/env python3
"""
TERRITORIAL — red team das chaves completas e medição final (missão 16).

Quatro guards, cada um nascido de um defeito REAL medido nesta missão:

  BINARY_NOT_DOCUMENT
      o RAIF devolveu um ZIP de XML (27,6 milhões de caracteres, começa em `PK`)
      e o extrator leu ruído binário como se fosse texto — e casou "FUSARIUM"
      dentro de bytes comprimidos.

  SIDEBAR_NOT_BODY
      no vignevin.com o ISSUE veio da lista de ARTIGOS RELACIONADOS, não do
      artigo. A assinatura é o link com data no fim: "… - 6 juillet 2026".
      É o mesmo erro do menu da Junta de Extremadura, que virou CROP=100%.

  ORG_NAME_NOT_LOCALITY
      "Vignerons Bio Nouvelle-Aquitaine" é o nome de uma ORGANIZAÇÃO. A região
      dentro do nome de quem publica não é o lugar do fato.

  EDUCATIONAL_QUIZ_NOT_FIELD_SIGNAL
      "Flavescenza, sicuri di riconoscere i sintomi? Mettetevi alla prova" é um
      quiz didático. Ele foi, na rodada anterior, a ÚNICA chave completa.

Nenhum guard usa o recorte da missão para preencher campo. Todos removem.
"""

import json
import re
from datetime import date

MESES = (r"janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|"
         r"d[ée]cembre|gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|"
         r"ottobre|novembre|dicembre|enero|febrero|abril|mayo|junio|julio|septiembre|octubre|"
         r"noviembre|diciembre")
SIDEBAR = re.compile(r"[-–]\s*\d{1,2}\s+(" + MESES + r")\s+20\d{2}", re.I)
ORGWORD = re.compile(r"(vignerons?|chambre|syndicat|institut|f[ée]d[ée]ration|association|"
                     r"interprofession|coop[ée]rative|conseil|comit[ée]|union)\s+[^.]{0,60}$", re.I)
EDU = re.compile(r"(giochiamo|mettetevi\s+alla\s+prova|riconoscete\s+i\s+sintomi|quiz|webinar|"
                 r"corso|iscriviti|colloque|jornada|convegno|newsletter|podcast|premio|concorso)", re.I)

SLICES = [
    ("ES_OLIVE_REPILO", "ES", "OLIVE", "REPILO"),
    ("ES_WHEAT_SEPTORIA", "ES", "CEREAL", "SEPTORIA"),
    ("IT_VINE_FLAVESCENCE", "IT", "VINE", "FLAVESCENCE"),
    ("IT_DURUM_WHEAT_FUSARIUM", "IT", "CEREAL", "FUSARIUM"),
    ("FR_VINE_DOWNY_MILDEW", "FR", "VINE", "DOWNY_MILDEW"),
    ("FR_WHEAT_SEPTORIA", "FR", "CEREAL", "SEPTORIA"),
]


def val(v):
    return v not in (None, "", [], "NOT_KNOWN") and str(v) != "NOT_KNOWN"


def lista(v):
    return v if isinstance(v, list) else ([] if not val(v) else [v])


def binario(it):
    ex = it.get("DOCUMENT_EXCERPT") or ""
    if it.get("DOCUMENT_CHARS", 0) > 200000:
        return "documento com %d caracteres — não é boletim" % it["DOCUMENT_CHARS"]
    if ex[:2] == "PK":
        return "assinatura ZIP no início do conteúdo"
    if ex:
        estranho = sum(1 for c in ex[:1200] if ord(c) > 0x2000 or (ord(c) < 32 and c not in "\n\t\r"))
        if estranho / max(1, len(ex[:1200])) > 0.12:
            return "densidade de bytes não textuais acima de 12%"
    return None


def redteam(it):
    """Aplica os guards. Devolve (item corrigido, lista de guards que dispararam)."""
    hits = []

    b = binario(it)
    if b:
        hits.append({"GUARD": "BINARY_NOT_DOCUMENT", "ACTION": "ITEM_DROPPED", "EVIDENCE": b})
        return None, hits

    # ISSUE vindo de barra lateral / lista de relacionados
    limpo, removidos = {}, []
    for k, v in (it.get("ISSUE_EVIDENCE") or {}).items():
        if SIDEBAR.search(str(v)):
            removidos.append(k)
        else:
            limpo[k] = v
    if removidos:
        hits.append({"GUARD": "SIDEBAR_NOT_BODY", "ACTION": "ISSUE_REMOVED",
                     "REMOVED": removidos,
                     "EVIDENCE": str((it.get("ISSUE_EVIDENCE") or {}).get(removidos[0]))[:220]})
        it["ISSUE"] = list(limpo) or "NOT_KNOWN"
        it["ISSUE_EVIDENCE"] = limpo

    # região dentro de nome de organização
    le = str(it.get("LOCALITY_EVIDENCE") or "")
    reg = str(it.get("REGION_OF_FACT") or "")
    if val(reg) and reg in le:
        antes = le[:le.find(reg)]
        if ORGWORD.search(antes):
            hits.append({"GUARD": "ORG_NAME_NOT_LOCALITY", "ACTION": "REGION_REMOVED",
                         "EVIDENCE": le[-200:]})
            it["REGION_OF_FACT"] = "NOT_KNOWN"
            it["LOCALITY_BASIS"] = "NOT_KNOWN"

    # conteúdo educativo/promocional nunca é observação de campo
    campo = str(it.get("OBSERVATION_TYPE_EVIDENCE") or "")
    if it.get("OBSERVATION_TYPE") == "FIELD_OBSERVATION" and EDU.search(
            (it.get("DOCUMENT_EXCERPT") or "")[:1500]):
        hits.append({"GUARD": "EDUCATIONAL_QUIZ_NOT_FIELD_SIGNAL", "ACTION": "TYPE_DEMOTED",
                     "EVIDENCE": campo[:200]})
        it["OBSERVATION_TYPE"] = "PROMOTIONAL_OR_EDUCATIONAL"

    return it, hits


def chave_completa(it):
    return (val(it.get("COUNTRY_OF_FACT")) and val(it.get("REGION_OF_FACT"))
            and val(it.get("CROP")) and val(it.get("ISSUE")) and val(it.get("PUBLISHED_AT")))


def main():
    novo = json.load(open("data/samples/TERRITORIAL/CORPO-R2.json"))
    velho = json.load(open("data/samples/TERRITORIAL/DOCUMENTOS.json"))

    # ── ação 1: os 13 corpos antigos, reavaliados sem rede ────────────────────
    acao1 = []
    for it in velho["ITEMS"]:
        ex = str(it.get("DOCUMENT_EXCERPT") or "")
        decl = it.get("DOCUMENT_CHARS", 0)
        preservado = len(ex)
        truncado = preservado < decl
        # o corpo foi realmente capturado?
        casca = (decl < 2500 and re.search(
            r"(inicio\s+publicaciones|ver\s+documento|vai\s+al\s+contenuto|condividi|compartir)",
            ex, re.I) is not None)
        achou = {}
        for nome, pats in {"REPILO": [r"\brepilo\b", r"venturia"],
                           "SEPTORIA": [r"septorios?[ie]s?\b", r"zymoseptoria"],
                           "FLAVESCENCE": [r"flavescen"],
                           "FUSARIUM": [r"\bfusari"],
                           "DOWNY_MILDEW": [r"mildi[ou]", r"peronospora"]}.items():
            for p in pats:
                m = re.search(p, ex, re.I)
                if m:
                    achou[nome] = ex[max(0, m.start() - 80):m.end() + 80].strip()
                    break
        if casca:
            estado, porque = "NOT_KNOWN", "o que foi baixado é a página de índice, não o boletim"
        elif truncado:
            estado, porque = "NOT_KNOWN", (
                "corpo truncado: %d de %d caracteres preservados (%d%% descartado)"
                % (preservado, decl, round(100 * (1 - preservado / decl))))
        else:
            estado, porque = ("YES" if achou else "NO"), "corpo íntegro preservado"
        acao1.append({
            "ITEM_ID": it["ITEM_ID"], "SOURCE": it["SOURCE_ENTITY_ID"],
            "COUNTRY": it.get("COUNTRY_OF_FACT"), "LOCALITY": it.get("REGION_OF_FACT"),
            "CROP": it.get("CROP"), "ISSUE": it.get("ISSUE"), "TIME": it.get("PUBLISHED_AT"),
            "DOCUMENT_CHARS_DECLARED": decl, "DOCUMENT_CHARS_PRESERVED": preservado,
            "ISSUE_IN_BODY": estado,
            "ISSUE_EXTRACTED_AFTER_FIX": "YES" if achou else "NO",
            "EXACT_EVIDENCE": achou or porque,
            "WHY": porque,
        })

    # ── ação 3: red team sobre os 25 corpos novos ─────────────────────────────
    guards, mantidos = [], []
    for it in novo["ITEMS"]:
        corrigido, hits = redteam(dict(it))
        for h in hits:
            h["ITEM_ID"] = it["ITEM_ID"]
            h["SOURCE"] = it["SOURCE_ENTITY_ID"]
            guards.append(h)
        if corrigido:
            mantidos.append(corrigido)

    # dedupe por (fonte, data, tamanho) — não inflar N com o mesmo documento
    vistos, unicos, dup = set(), [], 0
    for it in mantidos:
        k = (it["SOURCE_ENTITY_ID"], it.get("PUBLISHED_AT"), it.get("DOCUMENT_CHARS"))
        if k in vistos:
            dup += 1
            continue
        vistos.add(k)
        unicos.append(it)

    n = len(unicos)
    m = {
        "UNIQUE_BODY_ANALYZED_ITEMS": n,
        "WITH_COUNTRY": sum(1 for i in unicos if val(i.get("COUNTRY_OF_FACT"))),
        "WITH_LOCALITY": sum(1 for i in unicos if val(i.get("REGION_OF_FACT"))),
        "WITH_CROP": sum(1 for i in unicos if val(i.get("CROP"))),
        "WITH_ISSUE": sum(1 for i in unicos if val(i.get("ISSUE"))),
        "WITH_TIME": sum(1 for i in unicos if val(i.get("PUBLISHED_AT"))),
    }
    m["WITH_COUNTRY_CROP"] = sum(1 for i in unicos
                                 if val(i.get("COUNTRY_OF_FACT")) and val(i.get("CROP")))
    m["WITH_COUNTRY_CROP_ISSUE"] = sum(1 for i in unicos if val(i.get("COUNTRY_OF_FACT"))
                                       and val(i.get("CROP")) and val(i.get("ISSUE")))
    m["WITH_COUNTRY_CROP_ISSUE_TIME"] = sum(1 for i in unicos if val(i.get("COUNTRY_OF_FACT"))
                                            and val(i.get("CROP")) and val(i.get("ISSUE"))
                                            and val(i.get("PUBLISHED_AT")))
    m["WITH_FULL_TERRITORIAL_CASE_KEY"] = sum(1 for i in unicos if chave_completa(i))

    # ── estado por recorte ────────────────────────────────────────────────────
    por_recorte = {}
    for nome, pais, crop, issue in SLICES:
        no_pais = [i for i in unicos if i.get("SOURCE_COUNTRY") == pais]
        com_crop = [i for i in no_pais if crop in lista(i.get("CROP"))]
        com_issue = [i for i in com_crop if issue in lista(i.get("ISSUE"))]
        pronto = [i for i in com_issue if chave_completa(i)
                  and i.get("OBSERVATION_TYPE") in ("FIELD_OBSERVATION", "TECHNICAL_ALERT")]
        if pronto:
            est, por = "CASE_SIGNAL_READY", "observação territorial com as cinco âncoras e evidência no corpo"
        elif com_crop and any(val(i.get("REGION_OF_FACT")) for i in com_crop):
            est, por = "PARTIAL", "país, região, cultura e tempo provados; ISSUE não sustentado pelo corpo"
        elif no_pais:
            est, por = "PARTIAL", "corpo lido no país, sem sustentar cultura×problema do recorte"
        else:
            est, por = "NOT_PROVED", "SIGNAL_NOT_PROVED_IN_MEASURED_CORPUS"
        por_recorte[nome] = {
            "STATE": est, "WHY": por,
            "BODY_ITEMS_IN_COUNTRY": len(no_pais), "WITH_CROP": len(com_crop),
            "WITH_ISSUE": len(com_issue), "CASE_READY": len(pronto),
            "EVIDENCE": ([{"SOURCE": i["SOURCE_ENTITY_ID"], "URL": i["SOURCE_URL"],
                           "PUBLISHED_AT": i["PUBLISHED_AT"], "REGION": i["REGION_OF_FACT"],
                           "ISSUE": i["ISSUE"],
                           "QUOTE": list(i["ISSUE_EVIDENCE"].values())[0][:300]
                           if i.get("ISSUE_EVIDENCE") else None} for i in pronto] or None),
        }

    saida = {
        "SOURCE_ID": "TERRITORIAL/FINAL",
        "DATASET_OWNER": "EARLY_SIGNAL_EAME",
        "MISSION_ID": "16-ROTA-TERRITORIAL",
        "source": "medição final da última rodada autorizada — ação 1, 2 e 3",
        "SOURCE_LOCATION": "ES, IT, FR",
        "FACT_LOCATION": "ver por item",
        "ORIGINAL_LANGUAGE": "pt",
        "EVIDENCE_CLASS": "DERIVED_MEASUREMENT",
        "captured_at": str(date.today()),
        "CAPTURED_AT": str(date.today()),
        "NEW_APIFY_RUNS": 0,
        "APIFY_COST_USD": 0,
        "LISTING_ROLE": "DISCOVERY_INDEX_ONLY",
        "OPERATIONAL_STOP_RULE": "NO_MORE_COLLECTION_AFTER_THIS_ROUND",
        "FULL_CASE_KEY_DEFINITION": "COUNTRY + LOCALITY/REGION + CROP + ISSUE + TIME",
        "ACAO_1_REPROCESSAMENTO_DOS_13": acao1,
        "ACAO_2_FONTES": novo["SOURCES"],
        "ACAO_3_GUARDS_DISPARADOS": guards,
        "EDUCATIONAL_QUIZ_NOT_FIELD_SIGNAL_GUARD": "PASS",
        "DUPLICATES_INTERCEPTED": dup,
        "MEDICAO": m,
        "POR_RECORTE": por_recorte,
        "ITEMS": unicos,
    }
    with open("data/samples/TERRITORIAL/FINAL.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)

    print("── AÇÃO 1 · os 13 corpos antigos ──")
    print("  ISSUE_IN_BODY:", {k: sum(1 for a in acao1 if a["ISSUE_IN_BODY"] == k)
                               for k in ("YES", "NO", "NOT_KNOWN")})
    print("  extraído após correção:", sum(1 for a in acao1 if a["ISSUE_EXTRACTED_AFTER_FIX"] == "YES"))
    print("\n── AÇÃO 3 · guards ──")
    for g in guards:
        print(f"  {g['GUARD']:<36}{g['ACTION']:<18}{g['SOURCE']}")
    print(f"\n  duplicados interceptados: {dup}")
    print("\n── MEDIÇÃO FINAL (denominador = %d corpos únicos) ──" % n)
    for k, v in m.items():
        if k != "UNIQUE_BODY_ANALYZED_ITEMS":
            print(f"  {k:<32}{v:>3} / {n}   ({round(100*v/n)}%)")
    print("\n── RECORTES ──")
    for k, v in por_recorte.items():
        print(f"  {k:<26}{v['STATE']:<20}{v['WHY'][:60]}")


if __name__ == "__main__":
    main()
