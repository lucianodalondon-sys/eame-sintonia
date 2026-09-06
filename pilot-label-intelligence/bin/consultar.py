#!/usr/bin/env python3
"""
consultar.py — as perguntas que o cliente faz, respondidas com evidencia.

Toda resposta leva ao documento. Nenhuma resposta devolve so um numero.

Perguntas cobertas (as da missao, nesta ordem):
    cultura CULTURA          quais produtos ADAMA Italia tem esta cultura
    alvo ALVO                quais tem este alvo
    cultura X alvo Y         o cruzamento
    dose REGISTRO            a dose autorizada, com citacao
    rotulo REGISTRO          qual rotulo esta valendo
    mudou REGISTRO           esse rotulo mudou
    vencendo N               quais vencem nos proximos N dias
    sem-leitura              quais ainda nao tiveram tabela de uso lida
    mudancas                 o que mudou no registro oficial

A ultima e a mais importante para a honestidade do piloto: `sem-leitura` responde
com PARSE_STATE, nunca com "produto sem usos autorizados".
"""
import argparse, json, sys, unicodedata


def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").casefold())
    return "".join(c for c in s if not unicodedata.combining(c)).strip()


def carregar(p):
    return json.load(open(p, encoding="utf-8"))


def _casa(termo, *campos):
    t = norm(termo)
    return any(t in norm(c) for c in campos if c)


def por_cultura(d, termo):
    out = []
    for p in d["PRODUCTS"]:
        hits = [u for u in p["USE_ROWS"] if _casa(termo, u["CROP"], u.get("CROP_AS_WRITTEN"))]
        if hits:
            out.append((p, hits))
    return out


def por_alvo(d, termo):
    out = []
    for p in d["PRODUCTS"]:
        hits = [u for u in p["USE_ROWS"] if _casa(termo, u["TARGET"], u.get("TARGET_AS_WRITTEN"))]
        if hits:
            out.append((p, hits))
    return out


def cruzamento(d, cultura, alvo):
    out = []
    for p in d["PRODUCTS"]:
        hits = [u for u in p["USE_ROWS"]
                if _casa(cultura, u["CROP"], u.get("CROP_AS_WRITTEN"))
                and _casa(alvo, u["TARGET"], u.get("TARGET_AS_WRITTEN"))]
        if hits:
            out.append((p, hits))
    return out


def cab(p):
    return (f'{p["REGISTRATION_ID"]}  {p["PRODUCT"]}  [{p["REGULATORY_CATEGORY"]}]  '
            f'{p["HOLDER"]}  validade {p["EXPIRY"]}')


def fonte(p):
    lab = p.get("LABEL", {})
    return (f'      rotulo   : {lab.get("URL","NOT_KNOWN")}\n'
            f'      versao   : sha256 {str(lab.get("SHA256","NOT_KNOWN"))[:16]}  '
            f'em vigor desde {lab.get("EFFECTIVE_AT","NOT_KNOWN")}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="pilot-label-intelligence/demo/IT-LABEL-INTELLIGENCE.json")
    ap.add_argument("pergunta", nargs="+")
    a = ap.parse_args()
    d = carregar(a.dados)
    q = a.pergunta
    verbo = q[0].lower()

    if verbo == "cultura" and "x" not in q and "alvo" not in q:
        res = por_cultura(d, " ".join(q[1:]))
        print(f'CULTURA "{" ".join(q[1:])}" — {len(res)} produtos ADAMA Italia\n')
        for p, hits in res:
            print("  " + cab(p))
            for u in hits[:4]:
                print(f'      uso    : {u["CROP"]} x {u["TARGET"]}  (pag. {u["SOURCE_PAGE"]})')
            if len(hits) > 4:
                print(f'      ... e mais {len(hits)-4} usos')
            print(fonte(p)); print()

    elif verbo == "alvo":
        res = por_alvo(d, " ".join(q[1:]))
        print(f'ALVO "{" ".join(q[1:])}" — {len(res)} produtos\n')
        for p, hits in res:
            print("  " + cab(p))
            for u in hits[:4]:
                print(f'      uso    : {u["CROP"]} x {u["TARGET"]}  (pag. {u["SOURCE_PAGE"]})')
            print(fonte(p)); print()

    elif verbo == "cruzar":
        cultura, alvo = q[1], " ".join(q[2:])
        res = cruzamento(d, cultura, alvo)
        print(f'{cultura} x {alvo} — {len(res)} produtos\n')
        for p, hits in res:
            print("  " + cab(p))
            for u in hits:
                print(f'      uso    : {u["CROP"]} x {u["TARGET"]}  (pag. {u["SOURCE_PAGE"]})')
            for r in p.get("DOSE_ROWS", []):
                if _casa(cultura, r["CROP"]) and _casa(alvo, r["TARGET"]):
                    print(f'      dose   : {r["DOSE_PER_HECTARE"]} {r["DOSE_PER_HECTARE_UNIT"]}'
                          f'  max {r["MAX_APPLICATIONS"]}  int {r["APPLICATION_INTERVAL"]}')
                    print(f'      citacao: "{r["SOURCE_QUOTE"][:120]}"')
            print(fonte(p)); print()

    elif verbo == "dose":
        reg = q[1]
        p = next((x for x in d["PRODUCTS"] if x["REGISTRATION_ID"] == reg), None)
        if not p:
            print(f"registro {reg} nao esta entre os {d['TOTAL_ADAMA_PRODUCTS']} ativos"); return 1
        print(cab(p)); print()
        if not p.get("DOSE_ROWS"):
            print(f'  DOSE_PARSE_STATE = {p.get("DOSE_PARSE_STATE","NOT_ATTEMPTED")}')
            print("  Isto e estado de LEITURA, nao ausencia regulatoria.")
        for r in p["DOSE_ROWS"]:
            print(f'  {r["CROP"][:28]:<28} | {r["TARGET"][:30]:<30} | '
                  f'{r["DOSE_PER_HECTARE"]:>10} {r["DOSE_PER_HECTARE_UNIT"]:<7} | '
                  f'max {r["MAX_APPLICATIONS"]:<4} | pag {r["SOURCE_PAGE"]}')
        print(); print(fonte(p))

    elif verbo == "rotulo":
        reg = q[1]
        p = next((x for x in d["PRODUCTS"] if x["REGISTRATION_ID"] == reg), None)
        if not p:
            print(f"registro {reg} nao encontrado"); return 1
        lab = p["LABEL"]
        print(cab(p)); print()
        print(f'  em vigor desde : {lab.get("EFFECTIVE_AT")}   (data declarada pela fonte oficial)')
        print(f'  documento      : sha256 {lab.get("SHA256")}')
        print(f'  bytes          : {lab.get("BYTES")}')
        print(f'  fonte          : {lab.get("URL")}')
        print(f'  conferido em   : {lab.get("OBSERVED_AT")} contra captura de {lab.get("BASELINE_CAPTURED_AT")}')
        print(f'  mudou?         : {lab.get("DOCUMENT_CHANGED")}')

    elif verbo == "mudou":
        reg = q[1]
        p = next((x for x in d["PRODUCTS"] if x["REGISTRATION_ID"] == reg), None)
        if not p:
            print(f"registro {reg} nao encontrado"); return 1
        lab = p["LABEL"]
        print(cab(p)); print()
        print(f'  DOCUMENTO DO ROTULO: mudou = {lab.get("DOCUMENT_CHANGED")}')
        print(f'    {lab.get("BASELINE_CAPTURED_AT")} sha {str(lab.get("BASELINE_SHA256"))[:16]}')
        print(f'    {lab.get("OBSERVED_AT")} sha {str(lab.get("SHA256"))[:16]}')
        ev = p.get("REGISTRY_CHANGES", [])
        print(f'\n  REGISTRO OFICIAL: {len(ev)} mudancas na janela arquivada')
        for e in ev:
            flag = " (texto, nao regulatorio)" if e.get("UNSTABLE_SOURCE") else ""
            print(f'    {e["OBSERVATION_WINDOW"]}  {e["CHANGE_TYPE"]}{flag}')
            print(f'      {e["BEFORE"]}  ->  {e["AFTER"]}')

    elif verbo == "vencendo":
        n = int(q[1])
        res = sorted([p for p in d["PRODUCTS"] if isinstance(p["DAYS_TO_EXPIRY"], int)
                      and 0 <= p["DAYS_TO_EXPIRY"] <= n],
                     key=lambda p: p["DAYS_TO_EXPIRY"])
        print(f'VENCENDO EM ATE {n} DIAS — {len(res)} de {d["TOTAL_ADAMA_PRODUCTS"]} produtos ativos\n')
        for p in res:
            print(f'  {p["EXPIRY"]}  (+{p["DAYS_TO_EXPIRY"]:>3}d)  {p["REGISTRATION_ID"]}  '
                  f'{p["PRODUCT"][:28]:<28} {p["REGULATORY_CATEGORY"][:14]:<14} '
                  f'usos lidos: {len(p["USE_ROWS"])}')

    elif verbo == "sem-leitura":
        res = [p for p in d["PRODUCTS"] if not p["USE_ROWS"]]
        print(f'SEM TABELA DE USO LIDA — {len(res)} de {d["TOTAL_ADAMA_PRODUCTS"]}\n')
        print("  Isto e DIVIDA DE LEITURA, nao ausencia de uso autorizado.")
        print("  PARSER_FAILURE != REGULATORY_ABSENCE\n")
        for p in res:
            print(f'  {p["REGISTRATION_ID"]}  {p["PRODUCT"][:30]:<30} '
                  f'{p["REGULATORY_CATEGORY"][:14]:<14} rotulo: {p["LABEL"].get("STATE")}')

    elif verbo == "mudancas":
        h = d.get("REGISTRY_HISTORY", {})
        print(f'REGISTRO OFICIAL — janela {h.get("WINDOW")}')
        print(f'  instantaneos baixados : {h.get("SNAPSHOTS_DOWNLOADED")}')
        print(f'  documentos distintos  : {h.get("DISTINCT_DOCUMENTS")}')
        print(f'  mudancas regulatorias : {h.get("CHANGE_EVENTS_REGULATORY")}')
        print(f'  so texto (descartadas): {h.get("CHANGE_EVENTS_TEXT_ONLY")}\n')
        for p in d["PRODUCTS"]:
            for e in p.get("REGISTRY_CHANGES", []):
                if e.get("UNSTABLE_SOURCE"):
                    continue
                print(f'  {e["OBSERVATION_WINDOW"]}  {e["REGISTRATION_ID"]} '
                      f'{e["PRODUCT"][:24]:<24} {e["CHANGE_TYPE"]}')
                print(f'      {e["BEFORE"]}  ->  {e["AFTER"]}')
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
