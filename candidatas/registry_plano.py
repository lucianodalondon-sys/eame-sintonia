#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RECONCILIATION-PLAN.csv — o que fazer com cada uma das 255 identidades.

O §16 IMPEDE ESCREVER O ATLAS, E O PLANO E' O QUE SOBRA DE UTIL
--------------------------------------------------------------
Ha CINCO colisoes vivas: o mesmo numero afirmado sobre fontes diferentes, em
pontas ativas. A pior e' `IT-T4-001`, com 4.033 citacoes no repositorio,
apontada para o Ministero della Salute em 28 versoes do atlas e para a ARPAV
noutra branch. Reescrever o atlas com uma das duas escolhida por mim faria
4.033 referencias passarem a apontar para a fonte errada — em silencio.

Por isso esta missao entrega o PLANO, linha a linha, e nao o ficheiro.

A ORDEM DAS ACCOES, e ela importa
---------------------------------
    1 · resolver as 5 colisoes          decisao de gente, e desbloqueia o resto
    2 · declarar os 36 pares DERIVA_DE  o atlas ja tem o campo; e' escrita
    3 · trazer os 181 ausentes          mecanico, depois de 1 e 2
    4 · nao tocar nos 18 orfaos         identidade gasta e' identidade gasta
"""

import collections
import csv
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "build" / "source-registry-reconciliation"
CLAS = json.loads((SAIDA / "classificacao.json").read_text(encoding="utf-8"))
COL = json.loads((SAIDA / "colisoes.json").read_text(encoding="utf-8"))
CENSO = json.loads((SAIDA / "censo.json").read_text(encoding="utf-8"))

ACCOES = {
 "SAME_ID_DIFFERENT_SOURCE": (
  1, "BLOQUEADO — DECISAO DE GENTE",
  "duas fontes diferentes respondem por este numero, em pontas ativas. Ver "
  "COLLISIONS.csv: cada afirmacao tem data de primeira atribuicao, numero de "
  "versoes do atlas que a sustentam, e se tem cerca declarada e evidencia. "
  "Quem decidir escolhe UMA e da numero NOVO a outra — contra a populacao "
  "inteira de 255, nunca contra um ficheiro so. ⚠️ Nao renomear a que tem mais "
  "citacoes: e' ela que quebra mais referencias se mudar."),
 "SAME_SOURCE_MULTIPLE_IDS": (
  2, "DECLARAR DERIVA_DE — nenhum ID se apaga",
  "a mesma fonte levou dois numeros. O atlas JA TEM o mecanismo: o campo "
  "`DERIVA_DE`, que uma ficha usa assim — «DERIVA_DE: EU-T5-001 (mesma fonte, "
  "mesma rota, recorte proprio)». Escreve-se o par e os dois numeros "
  "continuam validos. O §8 mandava nao inventar alias, e nao foi preciso: "
  "existia."),
 "MISSING_FROM_CURRENT_ATLAS": (
  3, "TRAZER PARA O ATLAS DA LINHA DE INTEGRACAO",
  "emitido e ausente do atlas desta linha. Mecanico: copiar a ficha da versao "
  "que a tem, com a proveniencia. Depende de (1) e (2) estarem feitos, senao "
  "traz-se a colisao junto."),
 "SAME_ID_SAME_SOURCE": (
  4, "FUNDIR CAMPOS pela ordem de confianca",
  "mesmo numero, mesma fonte, em mais de um registo. Funde-se campo a campo: "
  "evidencia preservada > rota aberta > contrato > observado > documentado > "
  "descrito. Ausencia fica UNKNOWN. Ver a coluna DIVERGENCIAS."),
 "HISTORICAL_RED": (
  5, "PRESERVAR COMO GASTO",
  "ficha com veredito negativo. O numero continua GASTO: reciclar um ID de "
  "fonte morta e' o que faz dado antigo parecer dado novo."),
 "ONLY_IN_ONE_BRANCH": (
  6, "TRAZER, com a proveniencia escrita",
  "existe num sitio so'. Entra normalmente, dizendo de onde veio."),
}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    linhas = []
    for l in CLAS["LINHAS"]:
        ordem, accao, porque = ACCOES[l["ESTADO"]]
        linhas.append({
            "ORDEM": ordem, "ACCAO": accao,
            "SOURCE_ID": l["SOURCE_ID"], "ESTADO": l["ESTADO"],
            "SOURCE_NAME": l["SOURCE_NAME"], "SOURCE_OWNER": l["SOURCE_OWNER"],
            "COUNTRY": l["COUNTRY"], "TERRITORY": l["TERRITORY"],
            "URL": l["URL"],
            "NO_ATLAS_CORRENTE": l["NO_ATLAS_CORRENTE"],
            "IRMAOS_MESMA_FONTE": l["IRMAOS_MESMA_FONTE"],
            "N_CITACOES": l["N_CITACOES"],
            "FIRST_ASSIGNMENT_DATE": l["FIRST_ASSIGNMENT_DATE"],
            "FIRST_ASSIGNMENT_COMMIT": l["FIRST_ASSIGNMENT_COMMIT"],
            "FIRST_ASSIGNMENT_BRANCH": l["FIRST_ASSIGNMENT_BRANCH"],
            "N_VERSOES_QUE_O_SUSTENTAM": l["N_VERSOES"],
            "DIVERGENCIAS": l["DIVERGENCIAS"],
            "PORQUE": porque,
        })
    linhas.sort(key=lambda x: (x["ORDEM"], -x["N_CITACOES"], x["SOURCE_ID"]))

    # os orfaos entram no plano como accao 0: NAO TOCAR
    for i in CLAS["FANTASMAS"]:
        linhas.insert(0, {
            "ORDEM": 0, "ACCAO": "NAO TOCAR — IDENTIDADE GASTA SEM REGISTO",
            "SOURCE_ID": i, "ESTADO": "ORFAO_USADO_SEM_FICHA",
            "SOURCE_NAME": "", "SOURCE_OWNER": "", "COUNTRY": "",
            "TERRITORY": i.split("-")[1], "URL": "",
            "NO_ATLAS_CORRENTE": "NAO", "IRMAOS_MESMA_FONTE": "",
            "N_CITACOES": CENSO["CONSUMO"].get(i, 0),
            "FIRST_ASSIGNMENT_DATE": "NAO SEI", "FIRST_ASSIGNMENT_COMMIT": "",
            "FIRST_ASSIGNMENT_BRANCH": "", "N_VERSOES_QUE_O_SUSTENTAM": 0,
            "DIVERGENCIAS": "",
            "PORQUE": "este numero e' USADO pelo sistema e NUNCA foi declarado "
                      "em ficha nenhuma. Nao e' perda de reconciliacao — e' um "
                      "buraco anterior a ela. ⚠️ O numero esta GASTO: "
                      "reatribui-lo faria as referencias existentes apontarem "
                      "para a fonte nova. Registar a ficha que falta e' "
                      "trabalho de outra missao.",
        })

    cab = list(linhas[0])
    with open(SAIDA / "RECONCILIATION-PLAN.csv", "w", encoding="utf-8-sig",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cab, delimiter=";",
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)

    print("RECONCILIATION-PLAN — por ordem de execucao")
    print("=" * 104)
    c = collections.Counter((l["ORDEM"], l["ACCAO"]) for l in linhas)
    for (o, a), n in sorted(c.items()):
        print(f"  {o} · {a:46s} {n:4d} identidades")
    print("=" * 104)
    print(f"  TOTAL no plano: {len(linhas)}")
    print(f"  (255 emitidas + {len(CLAS['FANTASMAS'])} orfas usadas sem ficha)")
    print(f"\ngravado: {(SAIDA / 'RECONCILIATION-PLAN.csv').relative_to(RAIZ)}")
    print("\nficheiros de prova em build/source-registry-reconciliation/:")
    for p in sorted(SAIDA.glob("*.csv")):
        n = sum(1 for _ in open(p, encoding="utf-8-sig")) - 1
        print(f"  {p.name:34s} {n:5d} linhas")


if __name__ == "__main__":
    main()
