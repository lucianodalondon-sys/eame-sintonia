#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS CASOS QUE O RED TEAM D160 NOMEOU — re-medidos, um a um.

    py provas/d158/casos_do_red_team.py [--saida CASOS-DO-RED-TEAM.json]

POR QUE EXISTE
--------------
O red team provisorio D160 reprovou o produtor e disse EXACTAMENTE onde: itens da Sala,
com o ITEM_ID e o defeito. Um «corrigi» sem re-medir esses itens nao vale nada. Isto corre
o produtor de hoje sobre a MESMA copia so-leitura da Sala e responde, caso a caso, o que
saiu — para o proximo red team poder repetir a medicao sem confiar na palavra de ninguem.

⚠️ Isto NAO e uma lista de respostas certas codificada. O que esta aqui sao os ITEM_ID que
o red team citou e a PERGUNTA que ele fez sobre cada um. A resposta sai do produtor.

MEDICAO, nunca caminho de integracao. So le; escreve um ficheiro.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _p in (RAIZ, RAIZ / "leis"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import afirmacao_do_documento as AD              # noqa: E402
import tempo_da_afirmacao as TA                  # noqa: E402

COPIA_DA_R9 = Path(r"C:/Users/London1/sintonia-sala-italia/intelligence-experimental"
                   r"/EXPD78-R9-20260928T155047Z/copia/SALA_ATUAL.json")

#: Os itens que o red team citou, e o que ele disse sobre cada um. A pergunta e dele; a
#: resposta e do produtor de hoje.
CASOS = [
    ("D160 §1.4-A · evento futuro com publicacao provada saia como ACONTECIMENTO",
     ["derived:921", "derived:1063", "derived:1163", "derived:56", "derived:130",
      "derived:61", "derived:1022"],
     "nenhum FACT_TIME com valor pode ter data posterior a publicacao provada ou a captura"),
    ("D160 §1.4-B · janela de uso permitido saia como ACONTECIMENTO",
     ["derived:busca-3ae87b2ee6c08d80"],
     "«impiego consentito … dal … fino al …» tem de sair VALIDADE, e VALIDADE nao e FACT_TIME"),
    ("D160 §1.4-D · as 10 afirmacoes que o LAB sorteou",
     ["derived:1058", "derived:928", "derived:1022", "derived:busca-d6f1236a1340b8bd",
      "derived:busca-3ae87b2ee6c08d80", "derived:21", "derived:911", "derived:11",
      "derived:busca-7451caf82c35fdc9"],
     "o papel da data tem de estar certo"),
    ("D160 §1.5 · o lugar-lixo que atravessou a linha de titulo",
     ["derived:busca-c788a591bf3ca8de"],
     "FACT_LOCATION nao pode misturar o titulo com a frase"),
]


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=str(Path(__file__).resolve().parent / "CASOS-DO-RED-TEAM.json"))
    a = ap.parse_args(argv)
    linhas = {l["item_id"]: l for l in json.loads(COPIA_DA_R9.read_text(encoding="utf-8"))}
    alvos = sorted({i for _, ids, _ in CASOS for i in ids})

    por_item, classes, futuras, validades = {}, {}, [], []
    for iid in alvos:
        linha = linhas.get(iid)
        if linha is None:
            por_item[iid] = {"ERRO": "este ITEM_ID nao esta na copia da Sala"}
            continue
        afs = AD.afirmacoes_do_item(linha)["AFIRMACOES"]
        pub = TA.FT.publicacao_provada(linha.get("published_at"), linha.get("published_at_basis"))
        cap = TA.dia_da_captura(linha.get("raw_captured_at"))
        com_tempo = [x for x in afs if x["FACT_TIME"]["VALOR"] not in (AD.NAO_SEI, TA.NAO_EXISTE)]
        depois = []
        for x in com_tempo:
            dia, _ = TA.primeiro_dia(x["FACT_TIME"]["VALOR"])
            if dia and ((pub and dia > pub) or (cap and dia > cap)):
                depois.append({"CLAIM_ID": x["CLAIM_ID"], "FACT_TIME": x["FACT_TIME"]["VALOR"],
                               "TRECHO": x["TRECHO_LITERAL"][:160]})
        futuras += depois
        for x in afs:
            k = x["CLAIM_KIND"]["VALOR"]
            classes[k] = classes.get(k, 0) + 1
        papeis = {}
        for x in afs:
            p = x["FACT_TIME_ROLE"]["PAPEL"]
            papeis[p] = papeis.get(p, 0) + 1
        vals = [{"CLAIM_ID": x["CLAIM_ID"], "VALIDITY": x["VALIDITY"]["VALOR"],
                 "TRECHO": x["TRECHO_LITERAL"][:160]}
                for x in afs if x["FACT_TIME_ROLE"]["PAPEL"] == TA.VALIDADE]
        validades += vals
        por_item[iid] = {
            "PUBLICACAO_PROVADA": pub.isoformat() if pub else None,
            "CAPTURA": cap.isoformat() if cap else None,
            "AFIRMACOES": len(afs), "COM_FACT_TIME": len(com_tempo),
            "PAPEIS": papeis, "FACT_TIME_DEPOIS_DA_PUBLICACAO_OU_DA_CAPTURA": depois,
            "COM_PAPEL_VALIDADE": vals,
            "ALERTA_EVENTO": sum(1 for x in afs if x["CLAIM_KIND"]["VALOR"] == "ALERTA_EVENTO"),
            "REPROVADAS": sum(1 for x in afs
                              if AD.conferir_afirmacao(x, linha.get("texto") or "",
                                                       raw_sha256=linha.get("raw_sha256"))),
        }

    r = {"SALA": {"FICHEIRO": str(COPIA_DA_R9), "SHA256": sha(COPIA_DA_R9)},
         "PERGUNTAS": [{"CASO": c, "ITENS": ids, "O_QUE_TEM_DE_SER_VERDADE": q}
                       for c, ids, q in CASOS],
         "POR_ITEM": por_item,
         "RESUMO": {
             "ITENS_MEDIDOS": len(alvos),
             "FACT_TIME_DEPOIS_DA_PUBLICACAO_OU_DA_CAPTURA": len(futuras),
             "AFIRMACOES_COM_PAPEL_VALIDADE": len(validades),
             "CLASSES": classes,
             "AFIRMACOES_REPROVADAS_NA_CONFERENCIA": sum(
                 v.get("REPROVADAS", 0) for v in por_item.values() if isinstance(v, dict))},
         "LEI": ("os ITEM_ID sao os que o red team D160 citou; a resposta e do produtor de "
                 "hoje, e nao ha gabarito escrito aqui")}
    Path(a.saida).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(r["RESUMO"], ensure_ascii=False))
    for x in futuras:
        print("  DEPOIS DA PUBLICACAO/CAPTURA:", x["FACT_TIME"], "|", x["TRECHO"][:90])
    print("saida:", a.saida, "sha256", sha(a.saida))
    return 0


if __name__ == "__main__":
    sys.exit(main())
