#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GATILHO DO MODO CONTINUO — quando a fila baixa, o servico realimenta-se.

    "A FILA ACABOU" NAO E MOTIVO PARA PARAR.

O supervisor chama este gatilho quando o worker fica IDLE (sem trabalho
elegivel). Ele decide, de forma deterministica e SEM LLM, se realimenta a fila
— e como. Sao DOIS niveis, porque tem dois custos muito diferentes:

    FEEDER (barato, sem rede)   drena o acervo de candidatas para a fila.
                                A ponte ja existe e e idempotente.
    DISCOVERY (caro, com rede)  procura candidatas NOVAS. So corre quando o
                                proprio acervo esta a acabar, e com intervalo.

⚠️ ALIMENTACAO PROGRESSIVA. Uma fila saudavel nao e uma fila gigante. O gatilho
so age quando a fila esta ABAIXO do limiar; enquanto houver trabalho elegivel,
nao mexe. Isso, e nao um tamanho de lote inventado, e o que impede despejar
centenas de candidatas de uma vez.

────────────────────────────────────────────────────────────────────────────
OS LIMIARES, MEDIDOS E DECLARADOS (nao ha numero arbitrario)
────────────────────────────────────────────────────────────────────────────
QUEUE_LOW_WATERMARK = 10
  WHY: o worker faz uma etapa por tarefa (~1 s). A realimentacao pelo FEEDER e
  quase instantanea (sem rede) e refila a partir do acervo de candidatas. Basta,
  entao, um pequeno colchao para o worker nao ficar totalmente parado entre
  esvaziar a fila e o feeder a encher outra vez. 10 e esse colchao. Medido: a
  fila real desta missao tinha 72 tarefas QUALIFY — 10 e ~14% dela, um piso, nao
  uma meta.

CANDIDATE_LOW_WATERMARK = 20
  WHY: o acervo de candidatas e capital parado. DISCOVERY tem custo de rede
  (ate 250 pedidos) e so se justifica quando o acervo esta a acabar. Uma corrida
  de crawl rende, historicamente (ADDENDUM-01..04), dezenas de candidatas boas —
  logo 20 refila para um nivel saudavel sem despejar centenas. Acima de 20
  candidatas por qualificar, o FEEDER sozinho chega.

DISCOVERY_MIN_INTERVAL_S = 3600
  WHY: "discovery nada achou -> esperar intervalo e tentar outra vez". Sem teto
  de frequencia, um servico parado com acervo baixo faria crawls em rajada,
  gastando o orcamento de rede a cada volta. Uma vez por hora e suficiente para
  um acervo que muda em dias, e respeita "nao alargar orcamento sozinho".
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F                    # noqa: E402
import ponte_candidatas as PONTE    # noqa: E402

CANDIDATAS = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"

QUEUE_LOW_WATERMARK       = 10
CANDIDATE_LOW_WATERMARK   = 20
DISCOVERY_MIN_INTERVAL_S  = 3600


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def candidatas_por_qualificar() -> int:
    """Candidatas ainda por drenar para a fila (ESTADO == CANDIDATA).

    EM_ANALISE ja foi enfileirada pela ponte; RECUSADA/PROMOVIDA ja sairam. O
    que resta em CANDIDATA e o acervo que o FEEDER ainda pode aproveitar sem
    tocar a rede.
    """
    if not CANDIDATAS.exists():
        return 0
    doc = json.loads(CANDIDATAS.read_text(encoding="utf-8"))
    return sum(1 for c in doc.get("CANDIDATAS", [])
               if c.get("ESTADO") == "CANDIDATA")


def _discovery_real() -> dict:
    """Uma corrida de crawl com o orcamento DURO da missao. Rede real.

    Isolada aqui para poder ser injectada/mockada nos testes — provar o GATILHO
    nao pode exigir 250 pedidos de rede a cada corrida do teste.
    """
    import descobrir as D

    # A MESMA CONSTRUCAO DO `descobrir.py --crawl`, e nao outra. crawl_sementes
    # exige quatro posicionais (orcamento, conhecidos, visitados, log) e devolve
    # o par (registados, stats). Chamar so com `max_sementes` levantava
    # TypeError, que o except do supervisor engolia como DISCOVERY_HOOK_ERRO:
    # o servico ficava IDLE para sempre e parecia saudavel.
    orcamento  = D.Orcamento(total=D.MAX_PEDIDOS_TOTAIS)
    conhecidos = D._construir_set_conhecido()
    visitados  = D._ler_visitados()   # `_marcar_visitado` persiste por dentro
    log: list[dict] = []

    registados, stats = D.crawl_sementes(
        orcamento=orcamento,
        conhecidos=conhecidos,
        visitados=visitados,
        log=log,
        max_sementes=D.MAX_SEMENTES_ESTA_CORRIDA,
    )
    # ⚠️ PORQUE E QUE DEU ZERO, E NAO SO QUE DEU ZERO. Sem estes tres campos o
    # log escrevia «CANDIDATAS_NOVAS: 0» e ficava-se sem saber se o crawl nao
    # achou nada, se nao teve sementes, ou se as que tinha foram recusadas pela
    # regra de semente. Sao contadores que `crawl_sementes` ja produz.
    return {"CRAWL": stats.get("SEMENTES_USADAS"),
            "CANDIDATAS_NOVAS": len(registados),
            "PAGINAS_BUSCADAS": stats.get("PAGINAS_BUSCADAS"),
            "REQUESTS_REAIS_A_REDE": orcamento.pedidos_feitos,
            "ROBOTS_BLOCKS": stats.get("ROBOTS_BLOCKS"),
            "SEMENTES_DISPONIVEIS": stats.get("SEMENTES_DISPONIVEIS"),
            "SEMENTES_A_USAR": stats.get("SEMENTES_A_USAR"),
            "SEMENTES_RECUSADAS_POR_REGRA": stats.get("SEMENTES_GENERICAS_RECUSADAS")}


def assinatura_da_condicao() -> str:
    """O que o FEEDER le, reduzido a uma impressao digital.

    A ponte decide so a partir de duas coisas: o acervo de candidatas e a fila
    (o BRIDGE-LEDGER so muda quando a propria ponte corre). Se nenhuma mudou,
    a resposta do FEEDER tambem nao muda. Da fila entra o essencial de cada
    tarefa (id, estado, tentativas) — e nao os carimbos de hora, que mexem sem
    mudar nada.
    """
    h = hashlib.sha256()
    h.update(CANDIDATAS.read_bytes() if CANDIDATAS.exists() else b"-")
    try:
        tarefas = F._ler()["TAREFAS"]
    except Exception:
        tarefas = []
    for t in sorted(tarefas, key=lambda x: x.get("TASK_ID", "")):
        h.update(("%s|%s|%s;" % (t.get("TASK_ID"), t.get("STATUS"),
                                  t.get("ATTEMPTS"))).encode("utf-8"))
    return h.hexdigest()


def talvez_alimentar(estado: dict | None = None, *,
                     feeder_fn=None, descobrir_fn=None,
                     agora: datetime | None = None) -> dict:
    """Decide e executa a realimentacao. Devolve o que fez, sempre.

    `estado` guarda LAST_DISCOVERY_AT para o intervalo (o supervisor persiste-o).
    `feeder_fn`/`descobrir_fn` sao injectaveis para teste.
    """
    estado = estado if estado is not None else {}
    agora = agora or _agora()
    feeder = feeder_fn or PONTE.processar
    descobrir = descobrir_fn or _discovery_real

    m: dict = {"ACCOES": [], "QUEUE_ELIGIBLE": len(F.elegiveis())}

    # ⚠️ NADA A FAZER ENQUANTO HOUVER TRABALHO. Este e o «progressivo».
    if m["QUEUE_ELIGIBLE"] > QUEUE_LOW_WATERMARK:
        m["DECISAO"] = "QUEUE_OK"
        return m

    # Nivel 0 — REVIVER: FAILED por transporte volta, devagar (ver fila.py).
    # Sem rede e sem trabalho inventado: so mexe quando o relogio de uma tarefa
    # chega; nas outras voltas devolve [] e nao deixa rasto.
    revividas = F.reviver_intermitentes(agora)
    if revividas:
        m["REVIVER"] = {
            "REVIVIDAS": sum(1 for t in revividas
                             if t.get("INTERMITENCIA_VEREDICTO") != F.MORTA),
            "DECLARADAS_MORTAS": sum(1 for t in revividas
                                     if t.get("INTERMITENCIA_VEREDICTO") == F.MORTA),
            "TASK_IDS": [t["TASK_ID"] for t in revividas][:50],
        }
        m["ACCOES"].append("REVIVER")

    # Nivel 1 — FEEDER: drenar o acervo para a fila (barato).
    #
    # ⚠️ SEM CONDICAO NOVA, NAO HA FEEDER. Medido em 22/09: com a fila elegivel
    # a 0, o supervisor chamava o FEEDER a cada volta (15 s) — lia 476
    # candidatas, enfileirava 0 e anotava um REALIMENTACAO identico: 240 por
    # hora, ~5.700 por dia, o mesmo defeito do DISCOVERY_HOOK_ERRO noutra
    # roupa. A ponte e idempotente, logo com as MESMAS candidatas e a MESMA
    # fila o resultado e o mesmo: chama-la outra vez nao e trabalho, e eco.
    #
    #     REPETIR O QUE NADA MUDOU NAO E PERSISTENCIA, E RUIDO.
    #
    # Nada e engolido: cada volta saltada soma em FEEDER_NOOP_TOTAL, que o
    # estado do supervisor persiste e o painel mostra.
    assin = assinatura_da_condicao()
    if assin == estado.get("FEEDER_ASSINATURA"):
        estado["FEEDER_NOOP_TOTAL"] = int(estado.get("FEEDER_NOOP_TOTAL", 0)) + 1
        estado["FEEDER_NOOP_ULTIMO_AT"] = agora.isoformat()
        m["FEEDER_NOOP"] = True
    else:
        m["FEEDER"] = feeder()
        m["ACCOES"].append("FEEDER")
        # a assinatura grava-se DEPOIS do feeder: o que ele proprio escreveu
        # nao conta como condicao nova na volta seguinte.
        estado["FEEDER_ASSINATURA"] = assinatura_da_condicao()
        estado["FEEDER_ULTIMA_CHAMADA_AT"] = agora.isoformat()
        estado["FEEDER_CHAMADAS_TOTAL"] = int(estado.get("FEEDER_CHAMADAS_TOTAL", 0)) + 1

    # Nivel 2 — DISCOVERY: so quando o proprio acervo esta baixo, e com intervalo.
    pend = candidatas_por_qualificar()
    m["CANDIDATAS_POR_QUALIFICAR"] = pend
    if pend > CANDIDATE_LOW_WATERMARK:
        m["DECISAO"] = "FEEDER_SO — acervo ainda chega"
        return m

    last = estado.get("LAST_DISCOVERY_AT")
    if last:
        try:
            faltam = DISCOVERY_MIN_INTERVAL_S - (agora - datetime.fromisoformat(last)).total_seconds()
        except Exception:
            faltam = -1
    else:
        faltam = -1
    if faltam > 0:
        m["DECISAO"] = "DISCOVERY_EM_INTERVALO"
        m["DISCOVERY_PROXIMA_EM_S"] = round(faltam, 0)
        return m

    m["DISCOVERY"] = descobrir()
    estado["LAST_DISCOVERY_AT"] = agora.isoformat()
    m["ACCOES"].append("DISCOVERY")
    # Depois de descobrir, drenar as novas para a fila.
    m["FEEDER_2"] = feeder()
    m["ACCOES"].append("FEEDER_2")
    m["DECISAO"] = "DISCOVERY_ACCIONADA"
    return m


if __name__ == "__main__":
    print(json.dumps({
        "QUEUE_LOW_WATERMARK": QUEUE_LOW_WATERMARK,
        "CANDIDATE_LOW_WATERMARK": CANDIDATE_LOW_WATERMARK,
        "DISCOVERY_MIN_INTERVAL_S": DISCOVERY_MIN_INTERVAL_S,
        "QUEUE_ELIGIBLE_NOW": len(F.elegiveis()),
        "CANDIDATAS_POR_QUALIFICAR": candidatas_por_qualificar(),
    }, ensure_ascii=False, indent=1))
