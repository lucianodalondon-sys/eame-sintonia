#!/usr/bin/env python3
"""
selecionar_demo.py — escolhe os produtos da demo profunda, com criterio escrito.

A missao proibe escolher por conveniencia do parser. Entao o criterio e
declarado, o peso e visivel, e cada escolhido carrega o proprio WHY_SELECTED.
Um produto dificil que interessa ao cliente entra na frente de um produto facil
que nao interessa.
"""
import argparse, json, sys
from collections import defaultdict

# Linha comercial a partir da atividade declarada no registro oficial.
#
# O registro usa categorias compostas com hifen — "INSETTICIDA-DISERBANTE",
# "DISERBANTE-ANTIDOTO AGRONOMICO". A PRIMEIRA parte e a atividade principal.
# Ler a categoria inteira procurando palavra-chave classifica OLIONET, que e
# "INSETTICIDA-DISERBANTE", como herbicida. Por isso a decisao e pelo primeiro
# termo, e a categoria completa continua publicada ao lado.
def linha(cat):
    c = (cat or "").upper().split("-")[0].strip()
    if c.startswith("DISERBANTE"): return "HERBICIDA"
    if c.startswith("FUNGICIDA") or c.startswith("DIRADANTE"): return "FUNGICIDA"
    if c.startswith(("INSETTICIDA", "ACARICIDA", "AFICIDA", "MOLLUSCHICIDA")):
        return "INSETICIDA"
    return "OUTRA"


def pontuar(p):
    """Peso explicito. Nada aqui premia 'o parser foi bem'."""
    n = len(p["USE_ROWS"])
    s, por = 0.0, []
    # riqueza da tabela de uso: o cliente quer ver cultura x alvo de verdade
    if n:
        riq = min(n, 60) / 60 * 40
        s += riq; por.append(f"tabela de uso com {n} pares (+{riq:.0f})")
    # mudanca regulatoria observada na janela arquivada
    reg = [e for e in p["REGISTRY_CHANGES"] if not e.get("UNSTABLE_SOURCE")]
    if reg:
        s += 25; por.append(f"{len(reg)} mudanca(s) reais no registro oficial (+25)")
    # caso de validade interessante
    d = p["DAYS_TO_EXPIRY"]
    if isinstance(d, int):
        if d < 0:
            s += 30; por.append(f"validade VENCIDA ha {-d} dias e ainda listado como ativo (+30)")
        elif d <= 180:
            s += 20; por.append(f"vence em {d} dias (+20)")
    # rotulo com data efetiva declarada pela fonte: permite falar de versao
    if (p.get("LABEL", {}).get("EFFECTIVE_AT") or "NOT_KNOWN") != "NOT_KNOWN":
        s += 10; por.append("data efetiva do rotulo declarada pela fonte (+10)")
    # documento conferido nesta missao
    if p.get("LABEL", {}).get("STATE") == "CHECKED":
        s += 5; por.append("documento reconferido contra o hash arquivado (+5)")
    return s, por


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="pilot-label-intelligence/demo/IT-LABEL-INTELLIGENCE.json")
    ap.add_argument("--out", default="pilot-label-intelligence/demo/IT-DEMO-PRODUTOS.json")
    ap.add_argument("--por-linha", type=int, default=4)
    a = ap.parse_args()
    d = json.load(open(a.dados, encoding="utf-8"))

    grupos = defaultdict(list)
    for p in d["PRODUCTS"]:
        s, por = pontuar(p)
        grupos[linha(p["REGULATORY_CATEGORY"])].append((s, por, p))

    escolhidos, vistos_ai = [], set()
    for ln in ("HERBICIDA", "FUNGICIDA", "INSETICIDA"):
        cand = sorted(grupos[ln], key=lambda t: -t[0])
        n = 0
        for s, por, p in cand:
            # evita encher a demo de clones da mesma substancia ativa
            chave = (ln, tuple(sorted(p["ACTIVE_INGREDIENTS"])))
            if chave in vistos_ai and n >= 2:
                continue
            vistos_ai.add(chave)
            escolhidos.append({
                "REGISTRATION_ID": p["REGISTRATION_ID"],
                "PRODUCT": p["PRODUCT"],
                "LINE": ln,
                "REGULATORY_CATEGORY": p["REGULATORY_CATEGORY"],
                "HOLDER": p["HOLDER"],
                "ACTIVE_INGREDIENTS": p["ACTIVE_INGREDIENTS"],
                "EXPIRY": p["EXPIRY"],
                "DAYS_TO_EXPIRY": p["DAYS_TO_EXPIRY"],
                "USE_ROWS": len(p["USE_ROWS"]),
                "REGISTRY_CHANGES": len([e for e in p["REGISTRY_CHANGES"]
                                         if not e.get("UNSTABLE_SOURCE")]),
                "LABEL_EFFECTIVE_AT": p.get("LABEL", {}).get("EFFECTIVE_AT"),
                "LABEL_URL": p.get("LABEL", {}).get("URL"),
                "SCORE": round(s, 1),
                "WHY_SELECTED": por,
            })
            n += 1
            if n >= a.por_linha:
                break

    out = {
        "DATASET": "IT-DEMO-PRODUTOS",
        "BUILT_AT": d["BUILT_AT"],
        "CRITERIO": {
            "riqueza_da_tabela_de_uso": "ate +40, proporcional aos pares cultura x alvo lidos",
            "mudanca_regulatoria_real": "+25 se ha evento no historico oficial arquivado",
            "validade_vencida_e_ainda_ativo": "+30 — o caso que prova EXPIRY != WITHDRAWAL",
            "vence_em_ate_180_dias": "+20",
            "data_efetiva_do_rotulo_declarada": "+10",
            "documento_reconferido": "+5",
            "diversidade": "no maximo 2 produtos por substancia ativa dentro da mesma linha",
        },
        "O_QUE_O_CRITERIO_NAO_PREMIA": ("facilidade de parsing. Produto com tabela dificil entra "
                                        "se o caso interessa; a dificuldade aparece como estado "
                                        "de leitura, nao como exclusao silenciosa"),
        "DEMO_PRODUCTS": len(escolhidos),
        "PRODUCTS": escolhidos,
    }
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for e in escolhidos:
        print(f'  {e["LINE"]:<10} {e["REGISTRATION_ID"]} {e["PRODUCT"][:26]:<26} '
              f'score {e["SCORE"]:>5}  usos {e["USE_ROWS"]:>4}  venc {e["EXPIRY"]}', file=sys.stderr)
    print(f'\n  {len(escolhidos)} produtos -> {a.out}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
