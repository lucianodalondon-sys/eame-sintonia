#!/usr/bin/env python3
"""
objetos.py — DEPARTAMENTO DE INTELIGENCIA. Produz os intelligence objects.

Recebe o COLLECTION_PACKAGE (coleta) e o historico de instantaneos, e devolve
objetos reutilizaveis. O CASCO nunca abre PDF nem CSV: consome daqui.

Toda derivacao aponta a regra que a autoriza, por id, de v1/inteligencia/REGRAS.md.
O que nenhuma regra cobre sai UNKNOWN e aparece assim na tela.

    FACT -> DERIVED_REGULATORY_MEANING -> (portao) -> POTENTIAL_BUSINESS_IMPLICATION
                                       -> RECOMMENDED_REVIEW
    ACTION nao e emitida por esta ferramenta.
"""
import argparse, datetime, hashlib, json, os, sys
from collections import Counter

RULESET_VERSION = "v1/inteligencia/REGRAS.md@5"

# ---- C-*: roteamento declarado. Nada fora desta tabela e roteado.
ROTEAMENTO = {
    "EXPIRY_EVENT":            [("REGULATORY", "RELEVANT", "C-01"),
                                ("SUPPLY", "POTENTIALLY_RELEVANT", "C-07"),
                                ("INTELLIGENCE", "RELEVANT", "C-08"),
                                ("COUNTRY_PRODUCT_TEAM", "POTENTIALLY_RELEVANT", "C-09")],
    "DATE_CHANGE":             [("REGULATORY", "RELEVANT", "C-01"),
                                ("SUPPLY", "POTENTIALLY_RELEVANT", "C-11"),
                                ("INTELLIGENCE", "RELEVANT", "C-08"),
                                ("COUNTRY_PRODUCT_TEAM", "POTENTIALLY_RELEVANT", "C-09")],
    "STATUS_CHANGE":           [("REGULATORY", "RELEVANT", "C-01"),
                                ("SUPPLY", "POTENTIALLY_RELEVANT", "C-10"),
                                ("INTELLIGENCE", "RELEVANT", "C-08"),
                                ("COUNTRY_PRODUCT_TEAM", "POTENTIALLY_RELEVANT", "C-09")],
    "HOLDER_CHANGE":           [("REGULATORY", "RELEVANT", "C-01"),
                                ("INTELLIGENCE", "RELEVANT", "C-08")],
    "REVOCATION_ACT_CHANGE":   [("REGULATORY", "RELEVANT", "C-01"),
                                ("SUPPLY", "POTENTIALLY_RELEVANT", "C-12"),
                                ("INTELLIGENCE", "RELEVANT", "C-08"),
                                ("COUNTRY_PRODUCT_TEAM", "POTENTIALLY_RELEVANT", "C-09")],
    "ACTIVE_INGREDIENT_CHANGE": [("REGULATORY", "RELEVANT", "C-01"),
                                ("DEVELOPMENT_MARKET", "POTENTIALLY_RELEVANT", "C-04"),
                                ("INTELLIGENCE", "RELEVANT", "C-08")],
    "PRODUCT_ENTERED_REGISTRY": [("REGULATORY", "RELEVANT", "C-01"),
                                ("INTELLIGENCE", "RELEVANT", "C-08"),
                                ("COUNTRY_PRODUCT_TEAM", "POTENTIALLY_RELEVANT", "C-09")],
    "PRODUCT_LEFT_ACTIVE_SET": [("REGULATORY", "RELEVANT", "C-01"),
                                ("SUPPLY", "POTENTIALLY_RELEVANT", "C-13"),
                                ("INTELLIGENCE", "RELEVANT", "C-08")],
    "CROP_USE_ADDED":          [("REGULATORY", "RELEVANT", "C-01"),
                                ("DEVELOPMENT_MARKET", "POTENTIALLY_RELEVANT", "C-03"),
                                ("MARKETING_PRODUCT", "POTENTIALLY_RELEVANT", "C-06"),
                                ("INTELLIGENCE", "RELEVANT", "C-08")],
    "CROP_USE_REMOVED":        [("REGULATORY", "RELEVANT", "C-01"),
                                ("DEVELOPMENT_MARKET", "POTENTIALLY_RELEVANT", "C-04"),
                                ("MARKETING_PRODUCT", "POTENTIALLY_RELEVANT", "C-06"),
                                ("INTELLIGENCE", "RELEVANT", "C-08")],
    "TARGET_USE_ADDED":        [("REGULATORY", "RELEVANT", "C-01"),
                                ("DEVELOPMENT_MARKET", "POTENTIALLY_RELEVANT", "C-03"),
                                ("MARKETING_PRODUCT", "POTENTIALLY_RELEVANT", "C-06"),
                                ("INTELLIGENCE", "RELEVANT", "C-08")],
    "TARGET_USE_REMOVED":      [("REGULATORY", "RELEVANT", "C-01"),
                                ("DEVELOPMENT_MARKET", "POTENTIALLY_RELEVANT", "C-04"),
                                ("MARKETING_PRODUCT", "POTENTIALLY_RELEVANT", "C-06"),
                                ("INTELLIGENCE", "RELEVANT", "C-08")],
    "DOSE_CHANGE":             [("REGULATORY", "RELEVANT", "C-01"),
                                ("DEVELOPMENT_MARKET", "POTENTIALLY_RELEVANT", "C-04"),
                                ("MARKETING_PRODUCT", "POTENTIALLY_RELEVANT", "C-06"),
                                ("INTELLIGENCE", "RELEVANT", "C-08")],
    "RESTRICTION_CHANGE":      [("REGULATORY", "RELEVANT", "C-01"),
                                ("MARKETING_PRODUCT", "POTENTIALLY_RELEVANT", "C-06"),
                                ("INTELLIGENCE", "RELEVANT", "C-08")],
    "LABEL_DOCUMENT_CHANGED":  [("REGULATORY", "RELEVANT", "C-01"),
                                ("INTELLIGENCE", "RELEVANT", "C-08")],
    "NEEDS_HUMAN_REVIEW":      [("REGULATORY", "RELEVANT", "C-02")],
    "DATA_QUALITY_EVENT":      [("REGULATORY", "RELEVANT", "C-02")],
}
# O texto de cada regra, para a tela nao mostrar "regra C-07 — regra C-07".
PORQUE = {
    "C-01": "a mudanca e do registro oficial, que e o objeto de trabalho desta area",
    "C-02": "so esta area pode adjudicar leitura de rotulo",
    "C-03": "uso novo pode abrir avaliacao; a ferramenta nao afirma oportunidade",
    "C-04": "pode exigir reavaliacao de posicionamento",
    "C-05": ("o campo nao recebe fato regulatorio bruto; portao G-01 fechado nesta versao"),
    "C-06": ("material publicado pode citar o uso que mudou; gera CONTENT_REVIEW_CANDIDATE, "
             "nunca 'material errado'"),
    "C-07": ("e uma data no horizonte, e so isso. EXPIRY != WITHDRAWAL: a regra nao "
             "autoriza derivar dela nenhum efeito comercial — nem sobre procura, nem "
             "sobre inventario, nem sobre venda"),
    "C-08": "a area cruza portfolio, cultura, alvo e tempo",
    "C-09": "dono do portfolio local",
    "C-10": ("o estado administrativo do registro mudou. O fato e a mudanca de estado; "
             "a consequencia de abastecimento nao esta provada por ele"),
    "C-11": ("a data de validade declarada (data_scadenza_autorizzazione) mudou entre dois "
             "instantaneos oficiais. E prazo oficial com data na fonte, e nada mais: "
             "prorrogar validade nao e efeito comercial, e encurtar tampouco"),
    "C-12": ("mudou um dado do ato de revoga (motivo, decreto, decorrencia). Isto e "
             "sobre o ATO, nao sobre a existencia do produto no mercado"),
    "C-13": ("a registracao saiu do conjunto ativo do instantaneo. CATALOG_PRESENCE != "
             "MARKET_PRESENCE: sair do conjunto ativo prova uma coisa so, que a linha "
             "saiu daquele conjunto naquele instantaneo"),
}

# O campo RTV nunca recebe direto: C-05 mantem NOT_RELEVANT ate o portao G-01.
CAPACIDADES = ["REGULATORY", "DEVELOPMENT_MARKET", "COMMERCIAL_RTV", "MARKETING_PRODUCT",
               "SUPPLY", "INTELLIGENCE", "COUNTRY_PRODUCT_TEAM"]

SIGNIFICADO = {
    "EXPIRY_EVENT": ("a data de validade declarada da autorizacao ja passou e o registro "
                     "continua listando o produto como autorizado", "R-09"),
    "DATE_CHANGE": ("a validade declarada da autorizacao mudou entre dois instantaneos "
                    "oficiais", "R-01"),
    "STATUS_CHANGE": ("o estado administrativo declarado mudou", "R-02"),
    "PRODUCT_ENTERED_REGISTRY": ("o produto passou a constar no conjunto ativo do registro",
                                 "R-03"),
    "PRODUCT_LEFT_ACTIVE_SET": ("o produto deixou de constar no conjunto ativo", "R-04"),
    "HOLDER_CHANGE": ("o titular declarado mudou", "R-05"),
    "ACTIVE_INGREDIENT_CHANGE": ("a composicao declarada mudou", "R-06"),
    "LABEL_DOCUMENT_CHANGED": ("o documento do rotulo deixou de ser o mesmo arquivo", "R-08"),
    "REVOCATION_ACT_CHANGE": ("mudou uma data do ato de revoga (decreto ou decorrencia). "
                              "Isto NAO diz que o estado administrativo mudou", "R-07"),
}
# Que tipo de evento o differ do registro produz -> nome canonico do objeto
DE_REGISTRO = {
    "EXPIRY_CHANGED": "DATE_CHANGE",
    "STATUS_CHANGED": "STATUS_CHANGE",
    "PRODUCT_ADDED": "PRODUCT_ENTERED_REGISTRY",
    "PRODUCT_REMOVED": "PRODUCT_LEFT_ACTIVE_SET",
    "HOLDER_CHANGED": "HOLDER_CHANGE",
    "ACTIVE_INGREDIENT_CHANGED": "ACTIVE_INGREDIENT_CHANGE",
    # Revoga tem regra propria (R-07). Mapear para STATUS_CHANGE fazia a tela
    # citar R-02 ("stato_amministrativo mudou") para um evento em que o estado
    # administrativo NAO mudou — regra certa, condicao que nunca ocorreu.
    "REVOCATION_DECREE_CHANGED": "REVOCATION_ACT_CHANGE",
    "REVOCATION_EFFECT_CHANGED": "REVOCATION_ACT_CHANGE",
    "FORMULATION_CHANGED": "DATA_QUALITY_EVENT",
    "PRODUCT_NAME_CHANGED": "DATA_QUALITY_EVENT",
    "HAZARD_CHANGED": "DATA_QUALITY_EVENT",
}


def oid(*partes):
    return "IO-" + hashlib.sha256("|".join(str(p) for p in partes).encode()).hexdigest()[:16]


# Estados administrativos que a FONTE declara e que significam "a autorizacao
# nao esta em vigor agora". Medidos no instantaneo vigente sobre os 17.695
# produtos do registro inteiro, nao inventados: Revocato 13.216, Scaduto 765,
# Sospeso 3. Qualquer estado fora desta lista NAO e classificado por T-08.
ESTADOS_FORA_DE_VIGOR = ("revocato", "scaduto", "sospeso")


def janela(tipo, dias, novo, antes=None, depois=None):
    """T-*: janela temporal, sempre com a regra que a produziu."""
    if tipo in ("NEEDS_HUMAN_REVIEW", "DATA_QUALITY_EVENT"):
        return "UNKNOWN", "T-07"
    # T-08 · a unica revoga real do corpus recebia NO_ACTION_YET ("nada na fonte
    # pede tempo") enquanto uma prorrogacao de rotina recebia PLAN_NEXT_CYCLE.
    # Um ato administrativo datado sobre a validade do proprio registro e
    # exatamente o que uma janela serve para marcar. Isto continua sendo QUANDO
    # OLHAR e nada mais: EXPIRY != WITHDRAWAL, e nenhuma ACTION nasce daqui.
    if tipo == "REVOCATION_ACT_CHANGE":
        return "ACT_NOW", "T-08"
    # T-09, nao T-08: aqui mudou o ESTADO, e nem sempre ha ato datado por tras.
    # Em 014225/014227 (Revocato -> Scaduto) os tres campos de revoga sao "-" nos
    # 60 instantaneos: chamar isso de "ato administrativo datado" descrevia um
    # documento que a fonte nao traz.
    if tipo == "STATUS_CHANGE" and str(depois or "").strip().lower() in ESTADOS_FORA_DE_VIGOR:
        return "ACT_NOW", "T-09"
    if tipo == "EXPIRY_EVENT":
        return "ACT_NOW", "T-01"
    if isinstance(dias, int):
        if dias < 0:
            return "ACT_NOW", "T-01"
        if dias <= 90:
            return "PREPARE", "T-02"
        if dias <= 180:
            return "MONITOR", "T-03"
        if novo:
            return "PREPARE", "T-05"
        return "PLAN_NEXT_CYCLE", "T-04"
    if novo:
        return "PREPARE", "T-05"
    return "NO_ACTION_YET", "T-06"


def roteia(tipo):
    regras = ROTEAMENTO.get(tipo)
    out = []
    if not regras:
        for c in CAPACIDADES:
            out.append({"CAPABILITY_ID": c, "ROUTING_STATE": "UNKNOWN", "RULE_ID": "C-99",
                        "JUSTIFICATION": f"nenhuma regra de roteamento cobre o tipo {tipo}"})
        return out
    mapa = {c: None for c in CAPACIDADES}
    for cap, estado, rid in regras:
        mapa[cap] = (estado, rid)
    for c in CAPACIDADES:
        if c == "COMMERCIAL_RTV":
            # Unico NOT_RELEVANT com regra propria: e uma decisao declarada, nao
            # uma lacuna de conhecimento.
            out.append({"CAPABILITY_ID": c, "ROUTING_STATE": "NOT_RELEVANT", "RULE_ID": "C-05",
                        "JUSTIFICATION": ("decisao declarada: o campo nao recebe fato regulatorio "
                                          "bruto. Passa pelo portao G-01, que exige prova e revisao "
                                          "humana registrada e nao e aberto nesta versao")})
        elif mapa[c]:
            estado, rid = mapa[c]
            out.append({"CAPABILITY_ID": c, "ROUTING_STATE": estado, "RULE_ID": rid,
                        "JUSTIFICATION": PORQUE.get(rid, f"ver regra {rid} em v1/inteligencia/REGRAS.md")})
        else:
            # C-99 diz UNKNOWN, e UNKNOWN e o que tem de sair. Carimbar
            # NOT_RELEVANT aqui seria transformar "nenhuma regra cobre isto" em
            # uma afirmacao positiva de que a area NAO precisa olhar — que e
            # exatamente inventar conhecimento que nao temos.
            out.append({"CAPABILITY_ID": c, "ROUTING_STATE": "UNKNOWN", "RULE_ID": "C-99",
                        "JUSTIFICATION": (f"nenhuma regra de roteamento cobre {tipo} para esta "
                                          f"capacidade. Isto NAO afirma que a area nao precisa "
                                          f"olhar: afirma que nao sabemos")})
    return out


def base(tipo, item, **kw):
    """Molde comum de todo intelligence object."""
    dias = item.get("DAYS_TO_EXPIRY")
    jan, jrule = janela(tipo, dias, kw.pop("novo", False),
                        kw.get("BEFORE_VALUE"), kw.get("AFTER_VALUE"))
    sig, srule = SIGNIFICADO.get(tipo, ("NOT_PROVED", None))
    o = {
        "INTELLIGENCE_OBJECT_ID": oid(tipo, item["REGISTRATION_ID"],
                                      kw.get("BEFORE_VALUE"), kw.get("AFTER_VALUE"),
                                      kw.get("VALID_FROM")),
        "OBJECT_TYPE": tipo,
        "PRODUCT_ID": item["REGISTRATION_ID"],
        "REGISTRATION_ID": item["REGISTRATION_ID"],
        "PRODUCT_NAME": item.get("PRODUCT_NAME_RAW"),
        "HOLDER": item.get("HOLDER_RAW"),
        "COUNTRY": "IT",
        "SOURCE_ID": item.get("SOURCE_ID", "IT-MINSAL-FITOSANITARI"),
        "SOURCE_AUTHORITY": item.get("SOURCE_AUTHORITY"),
        "VALID_FROM": kw.pop("VALID_FROM", "NOT_KNOWN"),
        "VALID_UNTIL": kw.pop("VALID_UNTIL", "NOT_KNOWN"),
        "CAPTURED_AT": kw.pop("CAPTURED_AT", item.get("CAPTURED_AT", "NOT_KNOWN")),
        "DETECTED_AT": kw.pop("DETECTED_AT", "NOT_KNOWN"),
        "BEFORE_VALUE": kw.pop("BEFORE_VALUE", "NOT_APPLICABLE"),
        "AFTER_VALUE": kw.pop("AFTER_VALUE", "NOT_APPLICABLE"),
        "RAW_BEFORE": kw.pop("RAW_BEFORE", "NOT_PRESERVED"),
        "RAW_AFTER": kw.pop("RAW_AFTER", "NOT_PRESERVED"),
        "CHANGE_TYPE": tipo,
        "PROOF_STATE": kw.pop("PROOF_STATE", "PROVED"),
        "CONFIDENCE_STATE": kw.pop("CONFIDENCE_STATE", "OFFICIAL_FIELD_DIFF"),
        "SOURCE_DOCUMENT_BEFORE": kw.pop("SOURCE_DOCUMENT_BEFORE", "NOT_APPLICABLE"),
        "SOURCE_DOCUMENT_AFTER": kw.pop("SOURCE_DOCUMENT_AFTER", "NOT_APPLICABLE"),
        "EVIDENCE_LOCATION": kw.pop("EVIDENCE_LOCATION", "NOT_PRESERVED"),
        "PARSER_VERSION": kw.pop("PARSER_VERSION", "NOT_APPLICABLE"),
        "RULESET_VERSION": RULESET_VERSION,
        # as cinco camadas, separadas
        "FACT": kw.pop("FACT"),
        "DERIVED_REGULATORY_MEANING": sig,
        "DERIVED_BY_RULE": srule or "NOT_PROVED",
        "POTENTIAL_BUSINESS_IMPLICATION": "NOT_PROVED",
        "BUSINESS_IMPLICATION_NOTE": ("portao G-03 fechado: nao existe regra B-* nesta versao. "
                                      "Implicacao de negocio nao e derivada automaticamente"),
        "RECOMMENDED_REVIEW": kw.pop("RECOMMENDED_REVIEW", "NOT_PROVED"),
        "ACTION": "NOT_EMITTED_BY_THIS_TOOL",
        "TIME_WINDOW": jan,
        "TIME_WINDOW_RULE": jrule,
        "CAPABILITY_ROUTING": roteia(tipo),
        "AFFECTED_CROP": kw.pop("AFFECTED_CROP", "NOT_KNOWN"),
        "AFFECTED_TARGET": kw.pop("AFFECTED_TARGET", "NOT_KNOWN"),
        "AFFECTED_USE": kw.pop("AFFECTED_USE", "NOT_KNOWN"),
    }
    o.update(kw)
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pacote", default="v1/dados/COLLECTION-PACKAGE.json")
    ap.add_argument("--versoes", default="pilot-label-intelligence/registry/IT-REGISTRO-VERSOES.json")
    ap.add_argument("--reverificacao",
                    default="pilot-label-intelligence/labels/IT-ROTULOS-REVERIFICACAO.json")
    ap.add_argument("--doses", default="pilot-label-intelligence/demo/IT-DOSES.json")
    ap.add_argument("--hoje", required=True)
    ap.add_argument("--out", default="v1/dados/INTELLIGENCE-OBJECTS.json")
    a = ap.parse_args()

    pkg = json.load(open(a.pacote, encoding="utf-8"))
    hoje = datetime.date.fromisoformat(a.hoje)
    itens = {i["REGISTRATION_ID"]: i for i in pkg["ITEMS"]}
    for i in itens.values():
        try:
            i["DAYS_TO_EXPIRY"] = (datetime.date.fromisoformat(i["EXPIRY_RAW"]) - hoje).days
        except Exception:
            i["DAYS_TO_EXPIRY"] = "NOT_KNOWN"

    objs = []

    # ---- 1. eventos do registro oficial (differ ja filtrado por N-*)
    vs = json.load(open(a.versoes, encoding="utf-8"))
    ultima = vs["VERSIONS"][-1]["SNAPSHOT_DATE"]
    def limpa(v):
        """O CSV oficial imprime "-" para celula vazia. Isso e ausencia, e tem de
        chegar na tela como ausencia declarada, nao como um traco."""
        v = str(v).strip()
        return "NOT_PRESENT" if v in ("-", "", "--") else v

    def diz(v, ausente="NOT_KNOWN"):
        """Nenhum None de Python pode vazar para texto que uma pessoa le.

        Medido: 6 objetos exibiam a frase "separa a linha do valor None" —
        None ali nao era um valor lido, era a ausencia de um valor lido
        aparecendo com o nome que a linguagem lhe da. Token de ignorancia tem
        de ser dito pelo nome do contrato, nao pelo nome da linguagem.
        """
        if v is None:
            return ausente
        v = str(v).strip()
        return v if v and v not in ("-", "--", "None") else ausente

    for e in vs["CHANGE_EVENTS"]:
        if e.get("UNSTABLE_SOURCE"):
            continue                       # N-03: oscilacao nao vira objeto
        it = itens.get(e["REGISTRATION_ID"])
        if it is None:
            it = {"REGISTRATION_ID": e["REGISTRATION_ID"],
                  "PRODUCT_NAME_RAW": e.get("PRODUCT"), "HOLDER_RAW": e.get("HOLDER"),
                  "SOURCE_ID": "IT-MINSAL-FITOSANITARI",
                  "SOURCE_AUTHORITY": "Ministero della Salute (Italia)",
                  "CAPTURED_AT": e["NEW_SNAPSHOT"], "DAYS_TO_EXPIRY": "NOT_KNOWN"}
        tipo = DE_REGISTRO.get(e["CHANGE_TYPE"], "DATA_QUALITY_EVENT")
        novo = e["NEW_SNAPSHOT"] == ultima
        objs.append(base(
            tipo, it,
            FACT=(f'no registro oficial, o campo {e["FIELD"]} passou de '
                  f'"{limpa(e["BEFORE"])}" para "{limpa(e["AFTER"])}"'
                  if e["FIELD"] != "*" else
                  f'o registro passou a constar no conjunto ativo com estado "{limpa(e["AFTER"])}"'),
            BEFORE_VALUE=limpa(e["BEFORE"]), AFTER_VALUE=limpa(e["AFTER"]),
            RAW_BEFORE=e["BEFORE"], RAW_AFTER=e["AFTER"],
            VALID_FROM=e["NEW_SNAPSHOT"], VALID_UNTIL="NOT_KNOWN",
            CAPTURED_AT=e["NEW_SNAPSHOT"], DETECTED_AT=e["NEW_SNAPSHOT"],
            SOURCE_DOCUMENT_BEFORE=f'PROD_FTS_6_{e["OLD_SNAPSHOT"]}.csv sha256={e["OLD_VERSION"]}',
            SOURCE_DOCUMENT_AFTER=f'PROD_FTS_6_{e["NEW_SNAPSHOT"]}.csv sha256={e["NEW_VERSION"]}',
            EVIDENCE_LOCATION=(f'campo {e["FIELD"]}, registro {e["REGISTRATION_ID"]}'
                               if e["FIELD"] != "*" else
                               f'o registro {e["REGISTRATION_ID"]} inteiro, nao um campo isolado'),
            OBSERVATION_WINDOW=e["OBSERVATION_WINDOW"],
            SOURCE_URL=e["SOURCE"], novo=novo,
            CONFIDENCE_STATE="OFFICIAL_FIELD_DIFF",
            RECOMMENDED_REVIEW=("conferir na ficha oficial do registro" if tipo != "DATA_QUALITY_EVENT"
                                else "conferir se a diferenca tem significado regulatorio"),
        ))

    # ---- 2. validade vencida e ainda listado ativo (R-09)
    for it in itens.values():
        d = it["DAYS_TO_EXPIRY"]
        if isinstance(d, int) and d < 0:
            objs.append(base(
                "EXPIRY_EVENT", it,
                FACT=(f'a validade declarada e {it["EXPIRY_RAW"]} (ha {-d} dias) e o estado '
                      f'administrativo no registro vigente e "{it["STATUS_RAW"]}"'),
                BEFORE_VALUE=f'validade {it["EXPIRY_RAW"]}', AFTER_VALUE=f'hoje {a.hoje}',
                RAW_BEFORE=it["EXPIRY_RAW"], RAW_AFTER=it["STATUS_RAW"],
                VALID_FROM=it["EXPIRY_RAW"], VALID_UNTIL="NOT_KNOWN",
                CAPTURED_AT=a.hoje, DETECTED_AT=a.hoje,
                SOURCE_DOCUMENT_AFTER=f'{pkg["REGISTRY_SNAPSHOT_ID"]}.csv sha256={pkg["REGISTRY_SNAPSHOT_SHA256"][:16]}',
                EVIDENCE_LOCATION="campos data_scadenza_autorizzazione e stato_amministrativo",
                SOURCE_URL=it["SOURCE_URL"], CONFIDENCE_STATE="OFFICIAL_FIELD_VALUE",
                RECOMMENDED_REVIEW=("confirmar na fonte se houve prorroga, renovacao ou revoga "
                                    "nao refletida no dataset. VENCER NAO E SER REVOGADO"),
            ))

    # ---- 3. documento do rotulo mudou (R-08)
    if os.path.exists(a.reverificacao):
        rv = json.load(open(a.reverificacao, encoding="utf-8"))
        for i in rv["ITEMS"]:
            if i.get("DOCUMENT_CHANGED") is not True:
                continue                   # N-04: hash igual nao e versao nova
            it = itens.get(i["REGISTRATION_ID"])
            if not it:
                continue
            objs.append(base(
                "LABEL_DOCUMENT_CHANGED", it,
                FACT="o PDF da etichetta oficial deixou de ter o mesmo sha256",
                BEFORE_VALUE=i["BASELINE_SHA256"], AFTER_VALUE=i.get("CURRENT_SHA256"),
                CAPTURED_AT=i["OBSERVED_AT"], DETECTED_AT=i["OBSERVED_AT"],
                SOURCE_DOCUMENT_BEFORE=f'sha256={i["BASELINE_SHA256"]}',
                SOURCE_DOCUMENT_AFTER=f'sha256={diz(i.get("CURRENT_SHA256"), "NOT_PRESERVED")}',
                EVIDENCE_LOCATION=i["LABEL_URL"], SOURCE_URL=i["LABEL_URL"],
                CONFIDENCE_STATE="DOCUMENT_HASH_DIFF",
                RECOMMENDED_REVIEW=("comparar o conteudo das duas versoes; hash diferente prova "
                                    "documento diferente, nao diz ainda O QUE mudou dentro"),
            ))

    # ---- 4. o que a maquina recusou adivinhar
    if os.path.exists(a.doses):
        dz = json.load(open(a.doses, encoding="utf-8"))
        for lab in dz["LABELS"]:
            it = itens.get(lab["REGISTRATION_ID"])
            if not it:
                continue
            for r in (lab.get("ROWS") or []):
                if not r.get("NEEDS_REVIEW"):
                    continue
                cul = diz(r.get("CROP"), "NOT_KNOWN")
                alv = diz(r.get("TARGET"), "NOT_KNOWN")
                rej = diz(r.get("DOSE_PER_HECTARE_REJECTED"), "NOT_PRESERVED")
                objs.append(base(
                    "NEEDS_HUMAN_REVIEW", it,
                    FACT=((f'a dose lida para {cul} x {alv} foi rebaixada: um fio desenhado '
                           f'da tabela separa a linha do valor. '
                           if r.get("DOSE_RULE_CHECK") != "PLAUSIBILITY_REJECTED" else
                           f'a dose lida para {cul} x {alv} foi rebaixada por FILTRO DE '
                           f'PLAUSIBILIDADE ({r.get("REVIEW_NOTE") or "regra P-*"}) — '
                           f'uma heuristica nossa, nao uma medida do documento. ')
                          + (f'O valor recusado foi {rej}.' if rej != "NOT_PRESERVED"
                             else 'Este leitor NAO preservou qual valor recusou '
                                  '(NOT_PRESERVED): sabe-se que houve recusa, nao o que '
                                  'foi recusado.')),
                    BEFORE_VALUE=rej,
                    AFTER_VALUE="NOT_PRESENT",
                    PROOF_STATE="NOT_PROVED",
                    # Duas maquinas diferentes rebaixam dose, e a tela chamava as
                    # duas de "contradicao de fio". Fio desenhado e medida
                    # geometrica; plausibilidade e heuristica escrita por nos.
                    # Sao graus de evidencia diferentes e tem de aparecer assim.
                    CONFIDENCE_STATE=("RULE_CONTRADICTION"
                                      if r.get("DOSE_RULE_CHECK") != "PLAUSIBILITY_REJECTED"
                                      else "PLAUSIBILITY_HEURISTIC"),
                    DEMOTION_MECHANISM=("DRAWN_TABLE_RULE"
                                        if r.get("DOSE_RULE_CHECK") != "PLAUSIBILITY_REJECTED"
                                        else "PLAUSIBILITY_FILTER"),
                    DEMOTION_RULE=diz(r.get("REVIEW_NOTE") or r.get("DOSE_RULE_CHECK"),
                                      "NOT_KNOWN"),
                    # O que o fio desenhado dizia ANTES da heuristica passar por
                    # cima. Em 2 das 6 linhas ele dizia CONFIRMED_BY_RULE: o
                    # documento confirmava o valor e a heuristica derrubou assim
                    # mesmo. A tela nao pode chamar isso de "nenhum fio
                    # contradisse nada".
                    RULE_CHECK_BEFORE_DEMOTION=diz(
                        r.get("DOSE_RULE_CHECK_BEFORE_PLAUSIBILITY"), "NOT_CHECKED"),
                    AFFECTED_CROP=cul, AFFECTED_TARGET=alv,
                    AFFECTED_USE=f'{cul} x {alv}',
                    EVIDENCE_LOCATION=f'pagina {diz(r.get("SOURCE_PAGE"), "NOT_PRESERVED")}, {it["PDF_URL"]}',
                    SOURCE_DOCUMENT_AFTER=f'sha256={it["PDF_SHA256"]}',
                    SOURCE_URL=it["PDF_URL"],
                    PARSER_VERSION="v1/dose_extrair + dose_validar",
                    RECOMMENDED_REVIEW="ler a celula na etichetta e adjudicar a dose",
                ))
            if lab.get("PARSE_STATE") in ("NO_USE_TABLE_FOUND", "TABLE_FOUND_NO_ROWS"):
                # A afirmacao aqui e sobre a NOSSA LEITURA de um documento
                # especifico. O documento lido e a prova dela: sem apontar qual
                # PDF, com que hash, a afirmacao nao volta para lugar nenhum.
                objs.append(base(
                    "DATA_QUALITY_EVENT", it,
                    FACT=(f'o leitor de tabela devolveu {lab["PARSE_STATE"]} ao ler este documento'),
                    PROOF_STATE="NOT_PROVED", CONFIDENCE_STATE="READING_STATE",
                    BEFORE_VALUE="NOT_APPLICABLE", AFTER_VALUE=lab["PARSE_STATE"],
                    SOURCE_DOCUMENT_AFTER=(f'etichetta {it["PDF_URL"]} '
                                           f'sha256={it["PDF_SHA256"]} '
                                           f'({it["PDF_BYTES"]} bytes, capturada {it["CAPTURED_AT"]})'),
                    EVIDENCE_LOCATION=(f'documento inteiro; {it["TEXT_CHARS"]} caracteres de texto '
                                       f'recuperados, nenhuma tabela de uso localizada'),
                    SOURCE_URL=it["PDF_URL"],
                    PARSER_VERSION="v1/dose_extrair",
                    RECOMMENDED_REVIEW=("verificar se a etichetta declara dose em prosa em vez de "
                                        "tabela. ISTO NAO SIGNIFICA PRODUTO SEM DOSE"),
                ))

    out = {
        "DATASET": "IT-INTELLIGENCE-OBJECTS",
        "BUILT_AT": a.hoje,
        "RULESET_VERSION": RULESET_VERSION,
        "O_QUE_ISTO_E": "objetos de inteligencia reutilizaveis, cada um apontando a regra que o autoriza",
        "O_QUE_ISTO_NAO_E": ("nao emite ACTION, nao emite implicacao de negocio (portao G-03 "
                             "fechado), nao emite PHI_CHANGE (portao G-02 fechado), nao envia "
                             "nada ao campo (portao G-01 fechado)"),
        "OBJECTS": len(objs),
        "BY_TYPE": dict(Counter(o["OBJECT_TYPE"] for o in objs)),
        "BY_PROOF_STATE": dict(Counter(o["PROOF_STATE"] for o in objs)),
        "BY_TIME_WINDOW": dict(Counter(o["TIME_WINDOW"] for o in objs)),
        "OBJECTS_LIST": objs,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f'  objetos {len(objs)}', file=sys.stderr)
    for k, v in out["BY_TYPE"].items():
        print(f'    {k:<28} {v}', file=sys.stderr)
    print(f'  por prova: {out["BY_PROOF_STATE"]}', file=sys.stderr)
    print(f'  por janela: {out["BY_TIME_WINDOW"]}', file=sys.stderr)
    print(f'  escrito {a.out}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
