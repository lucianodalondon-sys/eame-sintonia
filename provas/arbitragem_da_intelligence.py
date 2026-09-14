#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RE-ARBITRAGEM DA INTELLIGENCE — medida contra UMA árvore.

    MISSAO   C-INT-ATOMICITY-01
    ESPECIE  INSTRUMENTO DE MEDICAO. NAO DECIDE NADA SOZINHO.

    python3 provas/arbitragem_da_intelligence.py            # tabela legivel
    python3 provas/arbitragem_da_intelligence.py --json     # para maquina
    python3 provas/arbitragem_da_intelligence.py --escrever # grava o resultado

POR QUE ESTE FICHEIRO EXISTE
----------------------------
A arbitragem `C-INT-ARB-01` correu numa branch que **não continha**
`leis/gestao_da_coleta.py`. Mediu bem e concluiu mal: declarou `COLLECTION_GAP`
como «0 ficheiros na árvore» quando o conceito já tinha dono desde 2026-09-08.

    UM CENSO SEM A FOTOGRAFIA DECLARADA E UM NUMERO SEM DENOMINADOR.

Este instrumento corre contra a árvore integrada e **declara a fotografia** em
que correu. Se alguém o correr noutra árvore, o cabeçalho muda com ele.

O QUE ELE MEDE, E O QUE NAO MEDE
---------------------------------
    MEDE      ficheiros que tocam o conceito, por camada
              se o modulo dono declarado existe
              se as autoridades concordam sobre o dono
    NAO MEDE  se o codigo esta correcto
    NAO MEDE  arestas observadas em runtime — isso e o System Map

    FICHEIRO QUE TOCA A PALAVRA != FICHEIRO QUE E DONO DO CONCEITO.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: As camadas, e o que cada uma significa quando um conceito aparece nela.
CAMADAS = {
    "COLLECTION": ("coleta", "admissao", "guarda", "leis", "orquestrador",
                   "fontes"),
    "INTELLIGENCE": ("motor", "superficie"),
    "DELIVERY": ("italia-portale", "pacote", "build"),
    "PROVA": ("provas", "tests"),
    "LEI": ("docs/intelligence", "docs/operacao", "research/intelligence"),
}

#: Autoridades que esta árvore tem de conter para a medição valer.
AUTORIDADES = {
    "BIBLIA_INTELLIGENCE_V0.2": "BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md",
    "MOTOR_V2_REQUISITOS": "docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md",
    "BACKLOG_V2": "docs/intelligence/BACKLOG-OBRIGATORIO.md",
    "ARBITRAGEM_V1": "docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md",
    "CONCEPT_OWNERSHIP_V1": "docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V1.json",
    "CENSO_INTELLIGENCE": "docs/operacao/CENSO-ATUAL-DA-INTELLIGENCE.md",
    "AUTHORITY_REGISTRY": "controle/AUTORIDADES-CANONICAS.json",
    "SALA_DE_CONTROLE": "SALA-DE-CONTROLE-SINTONIA.md",
    "BENCHMARK_AGRO": "research/intelligence/AGRO-INTELLIGENCE-BENCHMARK-V1.md",
    "ESPINHA_CONTRATO": "research/intelligence/INTELLIGENCE-SPINE-CONTRACT-V1.md",
    "ESPINHA_PROVA": "provas/espinha_da_intelligence.py",
    "KNOW_HOW_CANONICO": "SINTONIA-EAME-KNOW-HOW.md",
    "BIBLIA_DA_COLETA": "BIBLIA-CANONICA-DA-COLETA.md",
    "GESTAO_DA_COLETA": "leis/gestao_da_coleta.py",
    "CONTRATO_READY": "admissao/admissao.py",
}

#: ⚠️ O conjunto de conceitos NAO foi herdado. Foi construido da uniao das duas
#: arbitragens existentes, com os apelidos declarados — porque «dois nomes para
#: o mesmo objeto» foi exactamente o defeito que a missao anterior encontrou.
#:
#:     CONCEITO -> (tokens a procurar, dono declarado, modulo dono ou None)
CONCEITOS = {
    "SOURCE_FACT / READY_ITEM": {
        "ALIAS": ["SOURCE_CLAIM", "EVIDENCE", "READY_ITEM"],
        "TOKENS": ["PRONTO_PARA_INTELIGENCIA", "pronto_para_inteligencia"],
        "OWNER": "COLLECTION",
        "MODULO": "admissao/admissao.py",
    },
    "CLAIM_DOMAIN_JUDGMENT": {
        "ALIAS": [], "TOKENS": ["dominio_da_alegacao", "DOMINIO_DA_ALEGACAO"],
        "OWNER": "INTELLIGENCE", "MODULO": "motor/v21_dominio_da_alegacao.py",
    },
    "INTELLIGENCE_REQUEST": {
        "ALIAS": ["KIT", "KIQ"], "TOKENS": ["INTELLIGENCE_REQUEST", "REQUEST_ID"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "INTELLIGENCE_RUN": {
        "ALIAS": [], "TOKENS": ["INTELLIGENCE_RUN", "INTELLIGENCE_RUN_ID"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "SIGNAL": {
        "ALIAS": ["ANALYTIC_SIGNAL"], "TOKENS": ["ANALYTIC_SIGNAL", "SIGNAL_ID"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "SCREENING": {
        "ALIAS": [], "TOKENS": ["SCREENED_BY", "SCREENING"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "SUPPORT": {
        "ALIAS": [], "TOKENS": ["SUPPORT_EDGE", "SUPPORTS"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "CONTRADICTION": {
        "ALIAS": [], "TOKENS": ["CONTRADICTION_EDGE", "CONTRADICTS"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "DEPENDENCY / INDEPENDENCE": {
        "ALIAS": ["SAME_ORIGIN"], "TOKENS": ["SAME_ORIGIN", "INDEPENDENT_SOURCE"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "CROSSING": {
        "ALIAS": [], "TOKENS": ["CROSSING", "CRUZAMENTO"],
        "OWNER": "INTELLIGENCE", "MODULO": "motor/v21_crossings.py",
    },
    "CONVERGENCE": {
        "ALIAS": [], "TOKENS": ["CONVERGENCIA", "CONVERGENCE"],
        "OWNER": "INTELLIGENCE", "MODULO": "motor/pacote_convergencia.py",
    },
    "ANALYTIC_ASSUMPTION": {
        "ALIAS": [], "TOKENS": ["ANALYTIC_ASSUMPTION", "ASSUMPTION_ID"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "ANALYTIC_HYPOTHESIS": {
        "ALIAS": ["CANDIDATE_FINDING"],
        "TOKENS": ["ANALYTIC_HYPOTHESIS", "HYPOTHESIS_ID", "CANDIDATE_FINDING"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "VALIDATION_STATE": {
        "ALIAS": ["VALIDATION_QUEUE"],
        "TOKENS": ["VALIDATION_QUEUE", "VALIDATION_STATE"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "FINDING / ANALYTIC_JUDGMENT": {
        "ALIAS": ["JUDGMENT"], "TOKENS": ["FINDING_ID", "ANALYTIC_JUDGMENT"],
        "OWNER": "INTELLIGENCE", "MODULO": "motor/v21_fechar.py",
    },
    "REVERSAL / DEMOTED_BY": {
        "ALIAS": [], "TOKENS": ["DEMOTED_BY", "REVERSAL"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "FUTURE_SIGNAL": {
        "ALIAS": [], "TOKENS": ["FUTURE_SIGNAL", "RADAR_FUTURO"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "OPPORTUNITY": {
        "ALIAS": [], "TOKENS": ["OPPORTUNITY_ID", "OPORTUNIDADE"],
        "OWNER": "INTELLIGENCE", "MODULO": "motor/v21_oportunidades.py",
    },
    "ANALYTIC_RECOMMENDATION": {
        "ALIAS": [], "TOKENS": ["RECOMMENDATION_ID", "ANALYTIC_RECOMMENDATION"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "INTELLIGENCE_PACKAGE": {
        "ALIAS": [], "TOKENS": ["BUILD_ID", "CANONICAL-PACKAGE-CONTRACT"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "CONFIDENCE": {
        "ALIAS": [], "TOKENS": ["CONFIDENCE", "CONFIANCA"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    # ── o conceito que se partiu, e continua partido em dois ───────────────
    "INTELLIGENCE_REQUIREMENT": {
        "ALIAS": ["COLLECTION_GAP (metade da Intelligence)"],
        "TOKENS": ["INTELLIGENCE_REQUIREMENT", "COLLECTION_GAP"],
        "OWNER": "INTELLIGENCE", "MODULO": None,
    },
    "GAP / SATISFACTION / DECISION / ROTA": {
        "ALIAS": ["COLLECTION_GAP (metade da Collection)"],
        "TOKENS": ["GAP_ID", "SATISFACTION_STATE", "COLLECT_NOW"],
        "OWNER": "COLLECTION", "MODULO": "leis/gestao_da_coleta.py",
    },
    # ── os nove que estavam escondidos atras de dois nomes ─────────────────
    # ⚠️ ATE 2026-09-14 AQUI ESTAVAM `RELEVANCE` e `PRIORITY`, cada um com
    # OWNER = HUMAN_DECISION_REQUIRED. A decisao humana (C-INT-NIGHT-01, opcao
    # A/A) APOSENTOU OS DOIS NOMES NUS — nao lhes deu dono.
    #
    #     UM NOME QUE COBRE CINCO PERGUNTAS NAO GANHA UM DONO.
    #     PERDE O DIREITO DE SER USADO SOZINHO.
    #
    # O que entra no lugar sao os conceitos que eles escondiam, cada um com o
    # dono que JA TINHA. Ver NOMES_APOSENTADOS, ao fundo.
    "SOURCE_RELEVANCE": {
        "ALIAS": [], "TOKENS": ["SOURCE_RELEVANCE", "RELEVANCIA_DA_FONTE"],
        "OWNER": "COLLECTION", "MODULO": "leis/relevancia_da_fonte.py",
    },
    "ITEM_RELEVANCE": {
        "ALIAS": [], "TOKENS": ["ITEM_RELEVANCE", "LIVRO-DE-DECISOES"],
        "OWNER": "COLLECTION", "MODULO": "admissao/admissao.py",
    },
    "CASE_RELEVANCE": {
        "ALIAS": ["ADAMA_RELEVANCE"],
        "TOKENS": ["CASE_RELEVANCE", "RELEVANCE_A_PROVEN", "adama_relevance"],
        "OWNER": "INTELLIGENCE", "MODULO": "leis/adama_relevance.py",
    },
    "CROP_RELEVANCE": {
        "ALIAS": [], "TOKENS": ["CROP_RELEVANCE", "cropRelevance"],
        "OWNER": "COLLECTION", "MODULO": None,   # rotulo vindo da fonte
    },
    "USER_DECISION_RELEVANCE": {
        "ALIAS": [], "TOKENS": ["USER_DECISION_RELEVANCE"],
        "OWNER": "SEM_DONO_DECLARADO", "MODULO": None,   # metrica INT-LAW-251
    },
    "REQUIREMENT_PRIORITY": {
        "ALIAS": [], "TOKENS": ["REQUIREMENT_PRIORITY", "P1_BLOQUEIA_OUTRAS"],
        "OWNER": "COLLECTION", "MODULO": "leis/gestao_da_coleta.py",
    },
    "PRIORITY_TIER": {
        "ALIAS": [], "TOKENS": ["PRIORITY_TIER"],
        "OWNER": "COLLECTION", "MODULO": "leis/politica_da_coleta.py",
    },
    "COMMERCIAL_PRIORITY": {
        "ALIAS": [], "TOKENS": ["COMMERCIAL_PRIORITY", "SALES_READY"],
        "OWNER": "INTELLIGENCE", "MODULO": "motor/v21_comercial.py",
    },
    "WATCHLIST_PRIORITY": {
        "ALIAS": [], "TOKENS": ["WATCHLIST_PRIORITY"],
        "OWNER": "INTELLIGENCE", "MODULO": None,   # so em documento
    },
}

#: ⚠️ OS NOMES QUE DEIXARAM DE DESIGNAR ALGUMA COISA.
#: Nao sao conceitos sem dono: sao palavras que cobriam varios conceitos, cada
#: um com o seu dono. Usa-las sozinhas passou a ser um defeito de vocabulario.
#:
#: A decisao e humana, esta datada, e nao se apaga: `POR` diz quem a tomou.
NOMES_APOSENTADOS = {
    "RELEVANCE": {
        "DECISAO": "RETIRED_AS_OVERLOADED_NAME",
        "POR": "decisao humana · C-INT-NIGHT-01 · opcao A",
        "EM": "2026-09-14",
        "COBRIA": ["SOURCE_RELEVANCE", "ITEM_RELEVANCE", "CASE_RELEVANCE",
                   "CROP_RELEVANCE", "USER_DECISION_RELEVANCE"],
        "NAO_TEM_DONO_PORQUE": "nao designa uma pergunta. Cada uma das cinco "
                               "tem a sua, e quatro ja tinham dono em lei.",
    },
    "PRIORITY": {
        "DECISAO": "RETIRED_AS_OVERLOADED_NAME",
        "POR": "decisao humana · C-INT-NIGHT-01 · opcao A",
        "EM": "2026-09-14",
        "COBRIA": ["REQUIREMENT_PRIORITY", "PRIORITY_TIER",
                   "COMMERCIAL_PRIORITY", "WATCHLIST_PRIORITY"],
        "NAO_TEM_DONO_PORQUE": "idem: quatro perguntas, tres com dono em lei.",
    },
}


def _cabeca():
    """A fotografia. Sem ela, nenhum número abaixo significa alguma coisa."""
    def g(*a):
        try:
            return subprocess.check_output(["git"] + list(a), cwd=RAIZ,
                                           text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return "NAO SEI"
    return {
        "COMMIT": g("rev-parse", "HEAD"),
        "BRANCH": g("rev-parse", "--abbrev-ref", "HEAD"),
        "ARVORE_LIMPA": g("status", "--porcelain") == "",
        "SHALLOW": g("rev-parse", "--is-shallow-repository"),
    }


#: ⚠️ SAIDA DE GERADOR NAO E EVIDENCIA DE NADA.
#: O espelho do System Map passou a conter a prosa das pecas que esta missao
#: declarou — e essa prosa nomeia INTELLIGENCE_RUN e INTELLIGENCE_REQUIREMENT.
#: Contada como ficheiro da camada DELIVERY, ela movia os dois conceitos de
#: DEFINED_ONLY para DISPERSO: um documento a descrever um conceito passava a
#: contar como implementacao dele.
#:
#:     UM MAPA QUE DESCREVE O SISTEMA NAO FAZ PARTE DA CONTAGEM DO SISTEMA.
GERADOS = (".generated.json",)


def _ficheiros_que_tocam(tokens):
    """Quem menciona o conceito, por camada. É um indício, não uma prova."""
    achados = set()
    for t in tokens:
        try:
            out = subprocess.check_output(
                ["git", "grep", "-l", "-I", "--", t], cwd=RAIZ, text=True,
                stderr=subprocess.DEVNULL)
            achados |= {l for l in out.splitlines() if l}
        except subprocess.CalledProcessError:
            pass
    achados = {f for f in achados if not f.endswith(GERADOS)}
    por_camada = {c: 0 for c in CAMADAS}
    por_camada["OUTRA"] = 0
    for f in achados:
        for camada, prefixos in CAMADAS.items():
            if any(f.startswith(p + "/") or f.startswith(p) for p in prefixos):
                por_camada[camada] += 1
                break
        else:
            por_camada["OUTRA"] += 1
    return len(achados), por_camada


def medir():
    faltam = {k: v for k, v in AUTORIDADES.items()
              if not os.path.exists(os.path.join(RAIZ, v))}
    resultado = {
        "DATASET": "SINTONIA-INTELLIGENCE-REARBITRATION",
        "MISSAO": "C-INT-ATOMICITY-01",
        "FOTOGRAFIA": _cabeca(),
        "AUTORIDADES_EXIGIDAS": len(AUTORIDADES),
        "AUTORIDADES_AUSENTES": faltam,
        "CONTROL_PLANE_ATOMICITY": "FAIL" if faltam else "PASS",
        "NOMES_APOSENTADOS": NOMES_APOSENTADOS,
        "CONCEITOS": {},
    }
    for nome, d in CONCEITOS.items():
        total, camadas = _ficheiros_que_tocam(d["TOKENS"])
        modulo = d["MODULO"]
        tem_modulo = bool(modulo) and os.path.exists(os.path.join(RAIZ, modulo))

        # ⚠️ A distincao que o §17 do enunciado exige, e que um `grep` cru
        # apaga: um conceito citado SO em lei e em prova esta DEFINIDO, nao
        # implementado. Contar as duas coisas juntas foi como a Intelligence
        # chegou a ter documentos a dizer IMPLEMENTED sobre contratos.
        #
        #     CITADO NA LEI != EXISTE EM RUNTIME.
        em_codigo = (camadas["COLLECTION"] + camadas["INTELLIGENCE"]
                     + camadas["DELIVERY"])
        if modulo and not tem_modulo:
            atual, veredito = "MODULO_DECLARADO_AUSENTE", "CONFLICT"
        elif tem_modulo:
            atual, veredito = "IMPLEMENTED", "OWNER_PROVEN"
        elif total == 0:
            atual, veredito = "ABSENT", "OWNER_DECLARED_ONLY"
        elif em_codigo == 0:
            atual, veredito = "DEFINED_ONLY", "OWNER_DECLARED_ONLY"
        else:
            atual, veredito = "DISPERSO", "OWNER_DECLARED_ONLY"

        if d["OWNER"] == "HUMAN_DECISION_REQUIRED":
            veredito = "OWNER_NEEDS_HUMAN_DECISION"

        # ⚠️ O sinal de alarme que a missao anterior nao pode dar: um conceito
        # cujo dono e a INTELLIGENCE mas cujos ficheiros vivem na COLLECTION.
        vazamento = (d["OWNER"] == "INTELLIGENCE"
                     and camadas["COLLECTION"] > camadas["INTELLIGENCE"]
                     and camadas["COLLECTION"] > 0)

        resultado["CONCEITOS"][nome] = {
            "OWNER": d["OWNER"],
            "ALIAS": d["ALIAS"],
            "MODULO_DONO": modulo,
            "MODULO_EXISTE": tem_modulo,
            "FICHEIROS_QUE_TOCAM": total,
            "POR_CAMADA": camadas,
            "CURRENT_IMPLEMENTATION": atual,
            "VERDICT": veredito,
            "ALERTA_DE_CAMADA": vazamento,
        }
    return resultado


def _tabela(r):
    print("FOTOGRAFIA  %s @ %s  · arvore limpa: %s · shallow: %s"
          % (r["FOTOGRAFIA"]["BRANCH"], r["FOTOGRAFIA"]["COMMIT"][:8],
             r["FOTOGRAFIA"]["ARVORE_LIMPA"], r["FOTOGRAFIA"]["SHALLOW"]))
    print("AUTORIDADES %d exigidas · %d ausentes · CONTROL_PLANE_ATOMICITY = %s"
          % (r["AUTORIDADES_EXIGIDAS"], len(r["AUTORIDADES_AUSENTES"]),
             r["CONTROL_PLANE_ATOMICITY"]))
    for k, v in r["AUTORIDADES_AUSENTES"].items():
        print("   AUSENTE  %s -> %s" % (k, v))
    print()
    print("%-38s %-22s %-24s %s" % ("CONCEITO", "OWNER", "CURRENT", "VERDICT"))
    print("-" * 116)
    for nome, c in r["CONCEITOS"].items():
        marca = " ⚠" if c["ALERTA_DE_CAMADA"] else ""
        print("%-38s %-22s %-24s %s%s"
              % (nome[:38], c["OWNER"][:22], c["CURRENT_IMPLEMENTATION"],
                 c["VERDICT"], marca))
    print()
    n = len(r["CONCEITOS"])
    defi = sum(1 for c in r["CONCEITOS"].values()
               if c["CURRENT_IMPLEMENTATION"] == "DEFINED_ONLY")
    prov = sum(1 for c in r["CONCEITOS"].values() if c["VERDICT"] == "OWNER_PROVEN")
    hum = sum(1 for c in r["CONCEITOS"].values()
              if c["VERDICT"] == "OWNER_NEEDS_HUMAN_DECISION")
    conf = sum(1 for c in r["CONCEITOS"].values() if c["VERDICT"] == "CONFLICT")
    print("conceitos %d · owner provado %d · so definido %d · sem dono humano %d "
          "· conflito %d" % (n, prov, defi, hum, conf))


def main():
    r = medir()
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        _tabela(r)
    if "--escrever" in sys.argv:
        destino = os.path.join(
            RAIZ, "docs", "intelligence",
            "INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json")
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("\nescrito: %s" % os.path.relpath(destino, RAIZ))
    return 0 if r["CONTROL_PLANE_ATOMICITY"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
