#!/usr/bin/env python3
"""
cadencia.py — com que frequencia a etichetta italiana muda, de verdade.

Existe para transformar "nenhum rotulo mudou na nossa janela" de resultado pobre
em resultado ESPERADO — ou em alarme, se for o caso. Sem taxa de base, zero
mudancas nao significa nada.

A fonte da taxa nao e nossa: e a data de vigencia que o proprio Ministero declara
para cada etichetta ("Etichetta del DD/MM/AAAA"). Cada data dessas e um evento de
publicacao real. Nao inferimos nenhuma.

Limite honesto: a data diz quando a etichetta EM VIGOR entrou em vigor. Nao
enumera as anteriores. Entao isto mede a taxa de renovacao observavel hoje, nao
o historico completo de cada produto.
"""
import argparse, datetime, json, sys
from collections import Counter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="pilot-label-intelligence/demo/IT-LABEL-INTELLIGENCE.json")
    ap.add_argument("--hoje", required=True)
    ap.add_argument("--out", default="pilot-label-intelligence/labels/IT-CADENCIA-ROTULO.json")
    a = ap.parse_args()
    d = json.load(open(a.dados, encoding="utf-8"))
    hoje = datetime.date.fromisoformat(a.hoje)

    eff, sem = [], []
    for p in d["PRODUCTS"]:
        e = p["LABEL"].get("EFFECTIVE_AT")
        try:
            eff.append((datetime.date.fromisoformat(e), p["REGISTRATION_ID"], p["PRODUCT"]))
        except (TypeError, ValueError):
            sem.append(p["REGISTRATION_ID"])

    idades = sorted((hoje - e).days for e, _, _ in eff)
    med = idades[len(idades) // 2]
    janelas = {}
    for meses in (6, 12, 24, 36):
        lim = hoje - datetime.timedelta(days=meses * 30)
        janelas[f"ULTIMOS_{meses}_MESES"] = sum(1 for e, _, _ in eff if e >= lim)

    taxa_ano = janelas["ULTIMOS_12_MESES"] / len(eff)

    lvc = d.get("LABEL_VERSION_CHECK", {})
    try:
        b = datetime.date.fromisoformat(lvc["BASELINE_CAPTURED_AT"])
        o = datetime.date.fromisoformat(lvc["OBSERVED_AT"])
        dias = (o - b).days
    except Exception:
        dias = None
    esperado = round(len(eff) * taxa_ano * dias / 365, 2) if dias else "NOT_KNOWN"

    out = {
        "DATASET": "IT-CADENCIA-ROTULO",
        "BUILT_AT": a.hoje,
        "O_QUE_ISTO_E": ("taxa de renovacao das etichette ADAMA Italia, a partir da data de "
                         "vigencia declarada pelo proprio Ministero para cada rotulo"),
        "O_QUE_ISTO_NAO_E": ("nao e o historico de versoes de cada produto. A fonte declara a "
                             "data da etichetta EM VIGOR, nao as anteriores"),
        "LABELS_WITH_DECLARED_EFFECTIVE_DATE": len(eff),
        "LABELS_WITHOUT": len(sem),
        "LABELS_WITHOUT_LIST": sem,
        "OLDEST_LABEL_IN_FORCE": min(e for e, _, _ in eff).isoformat(),
        "NEWEST_LABEL_IN_FORCE": max(e for e, _, _ in eff).isoformat(),
        "MEDIAN_AGE_DAYS": med,
        "MEDIAN_AGE_YEARS": round(med / 365, 1),
        "RENEWED_WITHIN": janelas,
        "ANNUAL_RENEWAL_RATE": round(taxa_ano, 3),
        "BY_YEAR": dict(sorted(Counter(e.year for e, _, _ in eff).items())),
        "OBSERVATION_WINDOW_DAYS": dias,
        "EXPECTED_CHANGES_IN_WINDOW": esperado,
        "OBSERVED_CHANGES_IN_WINDOW": lvc.get("DOCUMENT_CHANGED"),
        "VEREDITO": (
            f"com {round(taxa_ano*100)}% de renovacao ao ano sobre {len(eff)} rotulos, uma janela "
            f"de {dias} dias faz esperar cerca de {esperado} mudancas. Observamos "
            f"{lvc.get('DOCUMENT_CHANGED')}. Zero e o resultado ESPERADO nesta janela, nao um "
            f"sinal de que os rotulos nao mudam — eles mudam, so nao nesta semana."
        ) if dias else "NOT_KNOWN",
        "IMPLICACAO_PARA_A_ESTEIRA": (
            "uma verificacao semanal cobre a taxa medida com folga; diaria seria desperdicio, "
            "porque o passo caro (baixar e parsear) so dispara quando o hash muda"),
        "RECENT_LABELS": [
            {"REGISTRATION_ID": r, "PRODUCT": n, "LABEL_EFFECTIVE_AT": e.isoformat()}
            for e, r, n in sorted(eff, reverse=True)[:15]
        ],
    }
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f'  {len(eff)} rotulos com data declarada | mediana {med} dias '
          f'({out["MEDIAN_AGE_YEARS"]} anos)', file=sys.stderr)
    print(f'  renovacao ao ano: {round(taxa_ano*100)}% | esperado na janela de '
          f'{dias}d: {esperado} | observado: {lvc.get("DOCUMENT_CHANGED")}', file=sys.stderr)
    print(f'  escrito {a.out}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
