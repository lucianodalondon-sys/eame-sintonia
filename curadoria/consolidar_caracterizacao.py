#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Consolida a caracterizacao, decide ONBOARDING_READY e recalcula o batch.

    CONNECTIVITY_PROVEN != SOURCE_CHARACTERIZED != ONBOARDING_READY

Tres estados distintos, medidos em separado. Uma fonte pode ter os tres, ou so
o primeiro — e dizer isso e o trabalho, nao um defeito.
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import caracterizador as CH  # noqa: E402

LOTES = ["_c_yt.json", "_c_fb.json", "_c_html.json"]


def decidir(c: dict) -> tuple[str, str]:
    """A DECISAO FINAL DESTA MISSAO, e cada «nao» tem de dizer de quem e o servico.

    ⚠️ ORDEM IMPORTA. Policy antes de capability, capability antes de semantica,
    e semantica antes de «falta amostra» — porque uma fonte bloqueada por
    politica nao ganha nada com mais amostragem.
    """
    if c.get("POLICY_STATUS") == "POLICY_BLOCK":
        return "POLICY_BLOCK", "politica da casa — nao se tentou, de proposito"

    # ⚠️ A CAPACIDADE LE-SE NOS DOIS CAMPOS, E ELES PODEM DISCORDAR.
    # Medido: as 14 do Facebook tinham `BROWSER_REQUIRED = NAO SEI` (a captura
    # anonima devolveu bytes) e `SMALL_ADAPTATION_REQUIRED = «SIM — exige
    # navegador»` (a rota de COLETA precisa de um). Ler so o primeiro deu
    # `ONBOARDING_READY` a 14 fontes cuja rota ninguem construiu.
    #
    #     CAPTURAR UMA AMOSTRA != TER ROTA DE COLETA.
    #     Uma sonda anonima pode passar onde a coleta recorrente nao passa.
    adapt = str(c.get("SMALL_ADAPTATION_REQUIRED") or "")
    if (c.get("LOGIN_REQUIRED") == "SIM" or c.get("BROWSER_REQUIRED") == "SIM"
            or "navegador" in adapt.lower()):
        return "CAPABILITY_BLOCK", ("exige navegador/sessao para a rota de coleta "
                                    "(%s): a fonte le-se, a CAPACIDADE e que falta. "
                                    "Servico do SCRAP ENGINEER" % (adapt or "medido na ficha"))

    # ⚠️ IDENTIDADE ERRADA E O UNICO CASO QUE SOBE A HUMANO POR MERITO PROPRIO.
    # A fonte funciona, o conteudo e real, e a ficha fala de outra entidade.
    # Nenhuma amostragem adicional resolve isto: e uma decisao de nomeacao.
    if c.get("DECLARED_IDENTITY_MATCHES_CONTENT") == "NAO":
        return "SEMANTIC_REVIEW_REQUIRED", c.get("IDENTITY_REASON", "")

    if c.get("SAMPLE_ERROR"):
        return "NEEDS_MORE_SAMPLING", "a amostragem falhou: %s" % c["SAMPLE_ERROR"]

    n = c.get("REPRESENTATIVE_SAMPLE_COUNT") or 0
    estavel = c.get("SOURCE_PATTERN_STABLE")

    if estavel == "SIM":
        # ⚠️ DORMANT NAO BLOQUEIA. A fonte e conhecida e a cadencia ja reflecte
        # o silencio (QUARTERLY_WATCH). LOW_YIELD != LOW_VALUE.
        return "ONBOARDING_READY", ("padrao estavel sobre %d itens · %s · cadencia %s"
                                    % (n, c["ACTIVITY"], c["INITIAL_COLLECTION_CADENCE"]))

    # ⚠️ «UNIVERSO INTEIRO» SO VALE SE HOUVER PADRAO PARA OBSERVAR.
    # Medido: 19 fontes tinham `n = 1` e `SAMPLE_IS_FULL_AVAILABLE_UNIVERSE`, e
    # passavam a READY. Mas um item nao e um padrao — e precisamente a premissa
    # desta missao:
    #
    #     UM REAL_EXAMPLE PROVA QUE A FONTE FUNCIONA.
    #     NAO PROVA O QUE ELA NORMALMENTE PUBLICA.
    #
    # Aceitar n=1 como «conhecida» seria refazer, uma camada acima, o erro que
    # esta missao existe para corrigir.
    if c.get("SAMPLE_IS_FULL_AVAILABLE_UNIVERSE") and n >= 2 and estavel != "NAO":
        return "ONBOARDING_READY", ("universo disponivel inteiro (%d itens) — nao ha "
                                    "mais o que amostrar, e isso nao e uma amostra "
                                    "pobre" % n)

    if n == 0:
        return "UNKNOWN", "nenhum item amostrado e nenhuma causa identificada"

    if n == 1:
        return "NEEDS_MORE_SAMPLING", ("um unico item: prova que a fonte funciona, "
                                       "nao o que ela normalmente publica. %s"
                                       % c.get("STABILITY_REASON", ""))

    return "NEEDS_MORE_SAMPLING", ("%d itens e o padrao ainda nao estabilizou: %s"
                                   % (n, c.get("STABILITY_REASON", "")))


def main() -> int:
    fichas = []
    for nome in LOTES:
        p = RAIZ / "curadoria" / nome
        if p.exists():
            fichas += json.loads(p.read_text(encoding="utf-8"))

    D = {d["CANDIDATE_ID"]: d for d in json.loads(
        (RAIZ / "curadoria" / "SOURCE-CURATOR-DECISIONS-V1.json")
        .read_text(encoding="utf-8"))["DECISOES"]}

    conta, por_fam, por_act = Counter(), defaultdict(Counter), Counter()
    por_cad, por_rel, por_tipo = Counter(), Counter(), Counter()
    tamanhos = []

    for c in fichas:
        # ⚠️ A ROTA VEM DA MISSAO 02 E TEM DE ESTAR NA FICHA *ANTES* DE DECIDIR.
        # Na primeira corrida, `decidir()` corria antes destas tres linhas e lia
        # `SMALL_ADAPTATION_REQUIRED = None`: as 14 do Facebook escapavam ao
        # CAPABILITY_BLOCK e caiam em NEEDS_MORE_SAMPLING — o rotulo certo pelo
        # motivo errado, que e pior do que um rotulo errado, porque parece bem.
        c["ONBOARDING_FAMILY"] = D[c["CANDIDATE_ID"]].get("ONBOARDING_FAMILY")
        c["LIKELY_ROUTE_STRATEGY"] = D[c["CANDIDATE_ID"]].get("LIKELY_ROUTE_STRATEGY")
        c["SMALL_ADAPTATION_REQUIRED"] = D[c["CANDIDATE_ID"]].get("SMALL_ADAPTATION_REQUIRED")

        estado, porque = decidir(c)
        c["FINAL_STATE"] = estado
        c["FINAL_REASON"] = porque
        c["SOURCE_CHARACTERIZED"] = "YES" if c["SOURCE_PATTERN_STABLE"] in ("SIM",) \
            or c.get("SAMPLE_IS_FULL_AVAILABLE_UNIVERSE") else "NO"
        c["ONBOARDING_READY"] = "YES" if estado == "ONBOARDING_READY" else "NO"

        conta[estado] += 1
        por_fam[c["FAMILY"]][estado] += 1
        por_act[c["ACTIVITY"]] += 1
        por_cad[c["INITIAL_COLLECTION_CADENCE"]] += 1
        por_rel[c["RELEVANT_TO_SINTONIA"]] += 1
        for t in c["CONTENT_VALUE_TYPE"]:
            por_tipo[t] += 1
        tamanhos.append(c["REPRESENTATIVE_SAMPLE_COUNT"])
        conta["CHARACTERIZED" if c["SOURCE_CHARACTERIZED"] == "YES" else "NOT_CHARACTERIZED"] += 1
        if c["SOURCE_PATTERN_STABLE"] == "SIM":
            conta["PATTERN_STABLE"] += 1
        elif c["SOURCE_PATTERN_STABLE"] == "NAO":
            conta["PATTERN_NOT_STABLE"] += 1
        if c.get("SAMPLE_BUDGET_REACHED"):
            conta["SAMPLE_BUDGET_REACHED"] += 1
        if c["EXPECTED_ITEMS_PER_WEEK"] != "NAO SEI":
            conta["EXPECTED_YIELD_MEASURED"] += 1
        else:
            conta["EXPECTED_YIELD_UNKNOWN"] += 1

    # ⚠️ UM ESTADO COM ZERO TEM DE APARECER COMO ZERO.
    # `Counter` omite as chaves que nunca ocorreram, e uma categoria ausente
    # da tabela le-se como «nao se aplica» em vez de «mediu-se e deu zero».
    # `POLICY_BLOCK = 0` e um resultado: diz que nenhuma das 124 promovidas
    # esbarrou em politica — e isso so se sabe se o zero for publicado.
    ESTADOS = ("ONBOARDING_READY", "NEEDS_MORE_SAMPLING", "CAPABILITY_BLOCK",
               "POLICY_BLOCK", "SEMANTIC_REVIEW_REQUIRED", "UNKNOWN")
    for e in ESTADOS:
        conta.setdefault(e, 0)

    # batch novo: pronto E sem adaptacao pendente
    prontos = [c for c in fichas if c["ONBOARDING_READY"] == "YES"]
    batch = [c for c in prontos
             if str(c.get("SMALL_ADAPTATION_REQUIRED", "")).startswith("NAO")]

    agora = datetime.now(timezone.utc).isoformat()
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, cwd=str(RAIZ)).stdout.strip()

    saida = {
        "DATASET": "SOURCE-CHARACTERIZATION-V1",
        "CONTRATO": CH.CONTRATO,
        "O_QUE_ISTO_E": ("caracterizacao das fontes promoviveis: quem sao, o que "
                         "publicam, com que frequencia, que temas e geografias cobrem, "
                         "quanto tendem a produzir e se estao activas."),
        "NAO_E": ("nao e Source Registry. Nao substitui o Atlas nem a fila. Referencia "
                  "CANDIDATE_ID e, quando aplicavel, MATCHED_SOURCE_ID."),
        "LEI": ("CONNECTIVITY_PROVEN != SOURCE_CHARACTERIZED != ONBOARDING_READY. "
                "LOW_YIELD != LOW_VALUE. DORMANT != IRRELEVANT. "
                "«nao consegui ler» != «nao serve»."),
        "GERADO_EM": agora,
        "SOURCE_CURATOR_HEAD": head,
        "EGRESSO": "205.147.30.6 · Milano, IT · AS208172 Proton AG",
        "AMOSTRAGEM": {
            "INICIAL": CH.AMOSTRA_INICIAL, "TECTO": CH.AMOSTRA_TECTO,
            "REGRA": "para quando o padrao estabiliza; o tecto e limite, nao meta",
            "TOTAL_SAMPLE_ITEMS": sum(tamanhos),
            "AVG_SAMPLE_ITEMS_PER_SOURCE": round(statistics.mean(tamanhos), 2) if tamanhos else 0,
            "MEDIAN_SAMPLE_ITEMS_PER_SOURCE": statistics.median(tamanhos) if tamanhos else 0,
        },
        "TOTAIS": dict(conta),
        "POR_FAMILIA": {k: dict(v) for k, v in por_fam.items()},
        "POR_ACTIVIDADE": dict(por_act),
        "POR_CADENCIA_INICIAL": dict(por_cad),
        "POR_RELEVANCIA": dict(por_rel),
        "BY_CONTENT_VALUE_TYPE": dict(por_tipo),
        "NEW_NEXT_BATCH_SIZE": len(batch),
        "NEW_NEXT_BATCH": [c["CANDIDATE_ID"] for c in batch],
        "FONTES": fichas,
    }
    p = RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json"
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("TARGET                    %d" % len(fichas))
    for k in ("CHARACTERIZED", "NOT_CHARACTERIZED", "PATTERN_STABLE",
              "PATTERN_NOT_STABLE", "SAMPLE_BUDGET_REACHED",
              "EXPECTED_YIELD_MEASURED", "EXPECTED_YIELD_UNKNOWN"):
        print("%-26s%d" % (k, conta[k]))
    print("-" * 46)
    for k in ("ONBOARDING_READY", "NEEDS_MORE_SAMPLING", "CAPABILITY_BLOCK",
              "POLICY_BLOCK", "SEMANTIC_REVIEW_REQUIRED", "UNKNOWN"):
        print("%-26s%d" % (k, conta[k]))
    print("-" * 46)
    print("actividade : %s" % dict(por_act))
    print("cadencia   : %s" % dict(por_cad))
    print("relevancia : %s" % dict(por_rel))
    print("cobertura  : %s" % dict(por_tipo))
    print("-" * 46)
    print("TOTAL_SAMPLE_ITEMS %d · media %.2f · mediana %s"
          % (sum(tamanhos), statistics.mean(tamanhos) if tamanhos else 0,
             statistics.median(tamanhos) if tamanhos else 0))
    print("NEW_NEXT_BATCH_SIZE %d" % len(batch))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
