#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUEM CHEGA A PERGUNTA TEMATICA, E O QUE PARA OS OUTROS ANTES.

    python3 provas/alcance_da_pergunta_tematica.py

O benchmark mediu quem responde MELHOR. Esta prova mede uma coisa anterior e
mais barata de ignorar: quantos documentos chegam sequer a ser perguntados.

    UM CLASSIFICADOR PERFEITO NUMA PERGUNTA QUE NINGUEM FAZ
    MELHORA EXACTAMENTE ZERO DOCUMENTOS.

A porta corre uma cadeia de prontidao ANTES do tema (COL-LAW-042: a ordem das
perguntas e parte da lei). Quem para na prontidao nunca e julgado pelo
conteudo — e trocar o mecanismo tematico nao muda nada para esse.

O QUE ESTA PROVA NAO FAZ
------------------------
    MEASURE != FIX

Ela nao inventa `SOURCE_ID`, nao inventa `DOCUMENT_ID`, nao usa hash como
identidade, nao remove constraint e nao toca em migration. Fabricar
identidade para os fazer chegar seria apagar a medicao com a mao que a
escreve: o numero ficava bonito e o acervo ficava na mesma.
"""
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
from coleta import ingresso as ing  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "_gate_alc", os.path.join(RAIZ, "provas", "gate_de_aceitacao_tematica.py"))
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

GABARITO = "data/samples/T3-GROUND-TRUTH-EVAL-V1.json"
REGISTO = "data/derivados/REGISTO-DE-ARTEFATOS.json"
SAIDA = "data/derivados/ALCANCE-PERGUNTA-TEMATICA-T3-V1.json"
UNIVERSO = "T3"

# A regra que decide o TEMA. Todas as outras sao prontidao, e parar numa delas
# e nunca ter sido perguntado.
REGRA_TEMATICA = "pertence ao universo"

DA_FICHA = (ing.DO_COLETOR + ing.DA_FICHA_PARA_A_PORTA
            + ("FACT_TIME", "PUBLISHED_AT", "COLLECTED_AT"))

# ── OS DOIS PLANOS ────────────────────────────────────────────────────────
# CONTRATO e o que a producao ve HOJE: so o que o registo de artefatos diz.
# LINHAGEM acrescenta o `SOURCE_ID` que o gabarito JA declara — resolvido e
# commitado numa missao anterior. E uma LEITURA de algo escrito, nao uma
# inferencia, e muito menos uma invencao.
CONTRATO, LINHAGEM = "CONTRATO", "LINHAGEM"


def _json(c):
    with open(os.path.join(RAIZ, c), encoding="utf-8") as f:
        return json.load(f)


def _corpo(c):
    with open(os.path.join(RAIZ, c), "rb") as f:
        return f.read().decode("utf-8", "replace")


def item_do(ficha_gt, registo, plano):
    bruto = {k: v for k, v in registo.items()
             if k in DA_FICHA and v not in ing.NAO_E_AFIRMACAO}
    if plano == LINHAGEM:
        sid = ficha_gt.get("SOURCE_ID")
        if sid not in ing.NAO_E_AFIRMACAO:
            bruto.setdefault("SOURCE_ID", sid)
    item = ing.para_a_porta(bruto)
    item["id"] = registo.get("ARTIFACT_ID") or ficha_gt["ITEM_ID"]
    item["texto"] = _corpo(ficha_gt["BODY_PATH"])
    return item


def medir(plano):
    doc = _json(GABARITO)
    reg = {a["STORAGE_LOCATION"]: a for a in _json(REGISTO)["ARTEFATOS"]}
    linhas = []
    for x in sorted(doc["GROUND_TRUTH"], key=lambda y: y["ITEM_ID"]):
        ficha = reg.get(x["BODY_PATH"], {})
        try:
            d = adm.decidir(item_do(x, ficha, plano), UNIVERSO)
            regra, motivo, ev = d.regra, d.motivo, d.evidencia
            saida = d.resultado
        except Exception as e:                              # noqa: BLE001
            regra, saida = "excecao ao correr a porta", adm.ERRO
            motivo, ev = "%s: %s" % (type(e).__name__, e), {}
        linhas.append({
            "ITEM_ID": x["ITEM_ID"], "DOC_SHA256": x["DOC_SHA256"],
            "PUBLISHER": x.get("PUBLISHER"),
            "SOURCE_ID_NO_GABARITO": x.get("SOURCE_ID"),
            "SOURCE_ID_NO_REGISTO": ficha.get("SOURCE_ID"),
            "ARTIFACT_TYPE": ficha.get("ARTIFACT_TYPE"),
            "ESTAGIO": ev.get("estagio"),
            "REGRA_QUE_DECIDIU": regra,
            "SAIDA": saida,
            "MOTIVO": motivo[:180],
            "CHEGOU_AO_TEMA": regra == REGRA_TEMATICA,
        })
    return linhas


# ── AS CLASSES DE FALHA NASCEM DA MEDICAO ─────────────────────────────────
# ⚠️ Nao ha lista de classes escrita a mao neste ficheiro. As classes SAO as
# regras que efectivamente pararam documentos, contadas.
#
#     UMA TAXONOMIA ESCRITA ANTES DE MEDIR
#     DESCREVE O AUTOR, NAO O ACERVO.
def classes_de_paragem(linhas):
    fora = defaultdict(list)
    for l in linhas:
        if not l["CHEGOU_AO_TEMA"]:
            fora[l["REGRA_QUE_DECIDIU"]].append(l["ITEM_ID"])
    return {k: sorted(v) for k, v in sorted(fora.items())}


def porque_a_prontidao_falha(linhas):
    """A causa CONCRETA, lida do item e nao presumida da regra.

    «origem» pode falhar por o registo dizer «NAO SEI» ou por o campo nem
    existir. Sao buracos diferentes e consertam-se em sitios diferentes.
    """
    fora = Counter()
    for l in linhas:
        if l["CHEGOU_AO_TEMA"]:
            continue
        if l["REGRA_QUE_DECIDIU"] != "origem":
            fora["%s · %s" % (l["REGRA_QUE_DECIDIU"], l["ESTAGIO"])] += 1
            continue
        no_reg = l["SOURCE_ID_NO_REGISTO"]
        no_gab = l["SOURCE_ID_NO_GABARITO"]
        if no_reg in ing.NAO_E_AFIRMACAO and no_gab not in ing.NAO_E_AFIRMACAO:
            fora["origem · o registo confessa «NAO SEI» e a linhagem SABE"] += 1
        elif no_reg in ing.NAO_E_AFIRMACAO:
            fora["origem · ninguem sabe, nem o registo nem a linhagem"] += 1
        else:
            fora["origem · o registo diz algo que a porta nao aceita"] += 1
    return dict(fora.most_common())


def main():
    planos = {p: medir(p) for p in (CONTRATO, LINHAGEM)}
    art = {
        "SCHEMA": "sintonia.thematic-reachability/1",
        "O_QUE_ISTO_E": (
            "Quantos dos 36 documentos do gabarito chegam a ser perguntados "
            "sobre o tema, e que regra de PRONTIDAO para os outros antes."),
        "MEASURE_NOT_FIX": (
            "Esta prova nao conserta nada e nao fabrica identidade nenhuma. "
            "SOURCE_ID inventado, DOCUMENT_ID inventado, hash como "
            "identidade, constraint removida: nenhum deles acontece aqui."),
        "UNIVERSE": UNIVERSO,
        "REGRA_TEMATICA": REGRA_TEMATICA,
        "A_ORDEM_E_LEI": (
            "COL-LAW-042: as perguntas de prontidao vem antes do tema. Parar "
            "numa delas nao e ser recusado pelo conteudo — e nunca ter sido "
            "lido."),
        "PLANOS": {},
        "GENERATED_BY": "provas/alcance_da_pergunta_tematica.py",
    }
    for p, linhas in planos.items():
        chegaram = [l for l in linhas if l["CHEGOU_AO_TEMA"]]
        art["PLANOS"][p] = {
            "O_QUE_E": ("o que a producao ve hoje: so o registo de artefatos"
                        if p == CONTRATO else
                        "o registo MAIS o SOURCE_ID que o gabarito ja declara "
                        "— uma leitura de algo escrito, nao uma inferencia"),
            "TOTAL": len(linhas),
            "ALCANCARAM_O_TEMA": len(chegaram),
            "REACHABILITY": gate.avaliar_reachability(len(chegaram),
                                                      len(linhas)),
            "PARARAM_ANTES": len(linhas) - len(chegaram),
            "CLASSES_DE_PARAGEM": classes_de_paragem(linhas),
            "PORQUE": porque_a_prontidao_falha(linhas),
            "SAIDAS": dict(Counter(l["SAIDA"] for l in linhas)),
            "LINHAS": linhas,
        }
    c, ln = art["PLANOS"][CONTRATO], art["PLANOS"][LINHAGEM]
    art["O_QUE_MUDA_ENTRE_OS_PLANOS"] = (
        "%d de %d chegam ao tema com o que a producao ve hoje; %d de %d "
        "chegam quando o SOURCE_ID ja escrito no gabarito e lido. A "
        "diferenca nao e do classificador: e de identidade."
        % (c["ALCANCARAM_O_TEMA"], c["TOTAL"],
           ln["ALCANCARAM_O_TEMA"], ln["TOTAL"]))
    art["INTEGRACAO"] = gate.avaliar_integracao(
        ln["REACHABILITY"], {"THEMATIC_GATE_PASS": False})
    art["PORQUE_INTEGRACAO_FALHA"] = (
        "O benchmark cego deu WINNER = NONE, e o alcance nao esta em 1. "
        "CLASSIFIER_BAD + LINEAGE_BROKEN: nenhum dos dois lados esta pronto, "
        "e consertar so um deles nao entrega documento nenhum.")
    caminho = os.path.join(RAIZ, SAIDA)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("\n  ALCANCE DA PERGUNTA TEMATICA — T3")
    print("  " + "─" * 66)
    for p in (CONTRATO, LINHAGEM):
        d = art["PLANOS"][p]
        print("\n  PLANO %s — %s" % (p, d["O_QUE_E"]))
        print("    alcance: %s de %s   (%s)"
              % (d["ALCANCARAM_O_TEMA"], d["TOTAL"],
                 d["REACHABILITY"]["REACHABILITY"]))
        for regra, ids in d["CLASSES_DE_PARAGEM"].items():
            print("    parou em «%s»: %d" % (regra, len(ids)))
        for causa, n in d["PORQUE"].items():
            print("      %-62s %d" % (causa, n))
    print("\n  " + "─" * 66)
    print("  %s" % art["O_QUE_MUDA_ENTRE_OS_PLANOS"])
    print("  INTEGRACAO = %s" % art["INTEGRACAO"]["VEREDICTO"])
    print("  escrito: %s\n" % SAIDA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
