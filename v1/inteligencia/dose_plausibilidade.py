#!/usr/bin/env python3
"""
dose_plausibilidade.py — descarta tabela que o extrator achou onde nao havia.

O extrator de dose acha a tabela por cabecalho. Em rotulo de prosa, um trecho
como "Dosi di POWERFILM" parece cabecalho, e ele monta uma tabela de fragmentos.
O red team achou o caso: PYXIDES WG saiu com 6 linhas em que a cultura e
"di foglia, su ▪ ▪" e o alvo e "Evitare di trattare con temperature" — texto de
recomendacao, nenhuma dose.

Pior que a linha errada e a linha errada com selo verde: FOLPAN GOLD saiu com
cultura "da vino" e alvo "della vite (Plasmopara", com dose 2 e conferencia
CONFIRMED_BY_RULE, porque o fio existia mesmo — ele so nao estava separando o
que a gente achou que estava.

As regras aqui sao conservadoras de proposito: preferem rebaixar linha boa a
publicar linha ruim.

    P-01  nenhuma linha do rotulo tem DOSE (nem por concentracao nem por hectare)
          -> a tabela inteira e espuria, e descartada.
          O teste e sobre DOSE, nao sobre "algum numero": no PYXIDES WG todas as
          seis linhas de prosa carregavam max=20, colhido de um numero solto do
          texto, e um teste frouxo deixaria a tabela passar inteira. A secao se
          chama CAMPI DI IMPIEGO E DOSI; tabela de uso sem uma dose sequer nao e
          tabela de uso.
    P-02  alvo comeca por marcador de lista ou simbolo (bullet, quadrado, traco)
          -> fragmento de prosa, vai para revisao
    P-03  linha sem dose, sem maximo e sem intervalo, num rotulo que tem outras
          com valor -> nao e linha de uso que a gente possa sustentar, vai para revisao
    P-04  cultura ou alvo com menos de 3 caracteres uteis -> vai para revisao
    P-05  cultura ou alvo comeca por palavra funcional italiana (da, della, di,
          in, su, con, per, e...) -> a celula foi cortada e o comeco ficou de
          fora. FOLPAN GOLD saiu com cultura "da vino" e alvo
          "della vite (Plasmopara", que sao os rabos de "Vite da vino" e
          "Peronospora della vite (Plasmopara viticola)". Com dose real e selo
          verde, que e a combinacao mais perigosa: parece conferido.

Nao ha regra que apague evidencia: o que sai daqui vira NEEDS_REVIEW com o motivo,
ou PARSE_STATE = SPURIOUS_TABLE_DISCARDED, nunca desaparece em silencio.
"""
import argparse, json, re, sys
from collections import Counter

MARCADOR = re.compile(r"^\s*[•▪●■‣·\-\*–—]")
# Palavra funcional italiana no INICIO da celula: sinal de celula cortada.
FUNCIONAL = re.compile(r"^\s*(da|della|dello|dei|delle|degli|del|di|in|su|con|per|e|ed|o|od|"
                       r"al|alla|allo|ai|alle|agli|nel|nella|sul|sulla|tra|fra)\b", re.I)
UTIL = re.compile(r"[A-Za-zÀ-ÿ]")


def tem_dose(r):
    """So dose conta. Maximo de aplicacoes sozinho nao faz linha de uso."""
    return any(str(r.get(k, "NOT_PRESENT")) != "NOT_PRESENT"
               for k in ("DOSE_CONCENTRATION", "DOSE_PER_HECTARE"))


def tem_valor(r):
    return tem_dose(r) or any(str(r.get(k, "NOT_PRESENT")) != "NOT_PRESENT"
                              for k in ("MAX_APPLICATIONS", "APPLICATION_INTERVAL"))


def uteis(s):
    return len(UTIL.findall(str(s or "")))


def filtra(lab):
    rows = lab.get("ROWS") or []
    if not rows:
        return lab, Counter()
    c = Counter()
    if not any(tem_dose(r) for r in rows):
        c["P-01_tabela_espuria"] += len(rows)
        lab["ROWS"] = []
        lab["PARSE_STATE"] = "SPURIOUS_TABLE_DISCARDED"
        lab["DISCARD_NOTE"] = ("nenhuma das linhas encontradas tinha DOSE; o que foi lido como "
                               "tabela era prosa. Regra P-01. "
                               "ISTO NAO SIGNIFICA PRODUTO SEM DOSE — significa que nao lemos")
        lab["DISCARDED_ROWS"] = rows
        return lab, c
    for r in rows:
        motivos = []
        if MARCADOR.match(str(r.get("TARGET", ""))):
            motivos.append("P-02 alvo comeca por marcador de lista: e fragmento de prosa")
        if not tem_valor(r):
            motivos.append("P-03 linha sem dose, maximo ou intervalo num rotulo que tem outras com valor")
        if uteis(r.get("CROP")) < 3 or uteis(r.get("TARGET")) < 3:
            motivos.append("P-04 cultura ou alvo curto demais para ser identidade")
        for campo in ("CROP", "TARGET"):
            if FUNCIONAL.match(str(r.get(campo, ""))):
                motivos.append(f"P-05 {campo.lower()} comeca por palavra funcional "
                               f"({str(r.get(campo))[:24]!r}): a celula foi cortada")
                break
        if motivos:
            for m in motivos:
                c[m.split()[0]] += 1
            r["NEEDS_REVIEW"] = True
            r["REVIEW_NOTE"] = ("; ".join(motivos) +
                                ". Rebaixada por implausibilidade, nao por contradicao de fio")
            r["PLAUSIBILITY_REJECTED"] = True
            r["DOSE_RULE_CHECK"] = "PLAUSIBILITY_REJECTED"
    return lab, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doses", default="pilot-label-intelligence/demo/IT-DOSES.json")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    d = json.load(open(a.doses, encoding="utf-8"))
    tot = Counter()
    descartados = 0
    for lab in d["LABELS"]:
        antes = len(lab.get("ROWS") or [])
        lab, c = filtra(lab)
        tot.update(c)
        if lab.get("PARSE_STATE") == "SPURIOUS_TABLE_DISCARDED":
            descartados += 1
            print(f'  {lab["REGISTRATION_ID"]} {str(lab.get("PRODUCT"))[:24]:<24} '
                  f'tabela espuria descartada ({antes} linhas)', file=sys.stderr)
    d["PLAUSIBILITY_FILTER"] = {
        "RULES": ["P-01 tabela sem nenhum valor -> descartada",
                  "P-02 alvo comeca por marcador de lista -> revisao",
                  "P-03 linha sem valor num rotulo com valores -> revisao",
                  "P-04 cultura ou alvo curto demais -> revisao"],
        "SPURIOUS_TABLES_DISCARDED": descartados,
        "ROWS_FLAGGED": dict(tot),
        "NOTE": ("filtro conservador: prefere rebaixar linha boa a publicar linha ruim. "
                 "Nada e apagado em silencio — o descartado fica em DISCARDED_ROWS"),
    }
    json.dump(d, open(a.out or a.doses, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    viva = sum(len(l.get("ROWS") or []) for l in d["LABELS"])
    rev = sum(1 for l in d["LABELS"] for r in (l.get("ROWS") or []) if r.get("NEEDS_REVIEW"))
    print(f'\n  tabelas espurias descartadas: {descartados}', file=sys.stderr)
    print(f'  linhas marcadas: {dict(tot)}', file=sys.stderr)
    print(f'  linhas restantes: {viva} | em revisao: {rev}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
