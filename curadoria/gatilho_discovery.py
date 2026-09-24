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
    # A regra da ponte e a caracterizacao que ela le tambem sao condicao: sem
    # isto, instalar uma regra nova deixava o FEEDER em NO-OP para sempre.
    h.update(PONTE.REGRA_VERSAO.encode("utf-8"))
    h.update(PONTE.CARACT.read_bytes() if PONTE.CARACT.exists() else b"-")
    h.update(CANDIDATAS.read_bytes() if CANDIDATAS.exists() else b"-")
    h.update(assinatura_da_fila().encode("utf-8"))
    return h.hexdigest()


def assinatura_da_fila() -> str:
    """O essencial de cada tarefa (id, estado, tentativas), sem carimbos de hora."""
    h = hashlib.sha256()
    try:
        tarefas = F._ler()["TAREFAS"]
    except Exception:
        tarefas = []
    for t in sorted(tarefas, key=lambda x: x.get("TASK_ID", "")):
        h.update(("%s|%s|%s;" % (t.get("TASK_ID"), t.get("STATUS"),
                                  t.get("ATTEMPTS"))).encode("utf-8"))
    return h.hexdigest()


# ────────────────────────────────────────────────────────────────────────────
# REVALIDAR AS ELEGIVEIS (B3, 2026-09-23)
# ────────────────────────────────────────────────────────────────────────────
# O bot so re-media o que FALHOU (alimentar_fila: REVALIDATE de
# CONTRACTED_CANARY_FAILED). Uma fonte ELIGIBLE nunca mais era olhada: IT-T5-041
# mudou de casa (crpv.it -> rinova.eu) a 22/09 e continuava no portao, porque
# nada a voltava a medir. Sem re-medicao nao ha DEMOTION sem humano.
#
#     O QUE O PORTAO DEIXA COLHER TEM DE SER RE-MEDIDO — SENAO A PROVA E UMA MEMORIA.
#
# REVALIDAR_ELEGIVEIS_DIAS = 7
#   WHY: nem a Biblia nem o know-how fixam uma idade maxima de prova (procurado a
#   23/09: «revalid», «prova velha», «idade da prova» — nada). Proposto e
#   declarado: 7 dias limita a uma semana o tempo que uma fonte que mudou de casa
#   fica no portao (a CRPV mudou em <1 dia); e custa pouco — ~30 elegiveis x <=4
#   pedidos por semana, contra ate 250 pedidos por DISCOVERY por hora. A cadencia
#   inicial das fontes (MONTHLY_PROBE) e de COLHEITA, nao de prova da rota.
# REVALIDAR_POR_VOLTA = 5
#   WHY: alimentacao progressiva, como o resto deste ficheiro: 5 x <=4 pedidos por
#   volta ociosa, nunca a lista inteira de uma vez.
# Guarda anti-eco: uma fonte cuja VALIDATE_ROUTE mexeu ha menos de N dias nao volta
#   a ser pedida, SEJA QUAL FOR o desfecho. Medido na prova viva T02077: «BLOCK sem
#   contrato» nao escreve linha no livro; sem esta guarda a fonte continuava velha e
#   ELIGIBLE e era pedida em cada volta ociosa — o eco que o FEEDER ja teve.
# Contrato novo (CONTRATO_UNICO da D10) e razao propria: re-medir logo, uma vez,
#   com o contrato novo (D10, condicao 2), mesmo que a prova seja recente.
#
# A re-medicao passa pela cadeia normal do worker: VALIDATE_ROUTE -> CANARY_PENDING
# -> CANARY -> READY so com os quatro passos, ou CONTRACTED_CANARY_FAILED. Durante
# a re-medicao a fonte sai do portao, e volta se passar — um contrato e hipotese
# ate o canario o provar.
REVALIDAR_ELEGIVEIS_DIAS = 7
REVALIDAR_POR_VOLTA = 5


def _quando(s: str | None) -> datetime | None:
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")) if s else None
    except ValueError:
        return None


def candidatas_a_revalidar(agora: datetime, *, ctx: dict | None = None,
                           tarefas: list | None = None) -> list[dict]:
    """[{SOURCE_ID, MOTIVO, PROMOVIDA_EM}] por ordem de urgencia. Nao escreve nada."""
    import collection_gate as CG   # noqa: E402  (lido so aqui: o gatilho corre sem ele)
    import ready_split as RS       # noqa: E402
    import lifecycle as LC         # noqa: E402
    ctx = ctx if ctx is not None else CG._contexto()
    tarefas = tarefas if tarefas is not None else F._ler()["TAREFAS"]
    limite = REVALIDAR_ELEGIVEIS_DIAS * 86400
    ultima_vr = {}
    for t in tarefas:
        if t.get("TASK_TYPE") == F.VALIDATE_ROUTE:
            u = _quando(t.get("UPDATED_AT"))
            if u and (t["SOURCE_ID"] not in ultima_vr or u > ultima_vr[t["SOURCE_ID"]]):
                ultima_vr[t["SOURCE_ID"]] = u
    est = {}
    for t in ctx["livro"]["TRANSICOES"]:
        est[t["SOURCE_ID"]] = t["NEW_STATE"]
    elegiveis = set(CG.elegiveis(ctx=ctx))
    out = []
    for sid in sorted(s for s, e in est.items() if e == LC.READY_FOR_COLLECTION):
        promo = RS.ultima_promocao(sid, ctx["livro"]) or {}
        quando = _quando(promo.get("OBSERVED_AT"))
        cu = (ctx["contratos"].get(sid) or {}).get("CONTRATO_UNICO") or {}
        novo = _quando(cu.get("APLICADO_EM"))
        vr = ultima_vr.get(sid)
        if novo and (quando is None or novo > quando):
            if vr is None or vr < novo:
                out.append({"SOURCE_ID": sid, "MOTIVO": "CONTRATO_NOVO",
                            "PROMOVIDA_EM": promo.get("OBSERVED_AT"), "ORDEM": 0})
            continue
        if sid not in elegiveis or quando is None:
            continue
        if (agora - quando).total_seconds() <= limite:
            continue
        if vr is not None and (agora - vr).total_seconds() <= limite:
            continue
        out.append({"SOURCE_ID": sid, "MOTIVO": "PROVA_VELHA",
                    "PROMOVIDA_EM": promo.get("OBSERVED_AT"), "ORDEM": 1})
    out.sort(key=lambda x: (x["ORDEM"], x["PROMOVIDA_EM"] or ""))
    return out


def revalidar_elegiveis(agora: datetime, *, ctx: dict | None = None,
                        tarefas: list | None = None) -> dict:
    cands = candidatas_a_revalidar(agora, ctx=ctx, tarefas=tarefas)
    feitas = []
    for c in cands[:REVALIDAR_POR_VOLTA]:
        F.enfileirar(c["SOURCE_ID"], F.VALIDATE_ROUTE, priority=55,
                     motivo=("re-medir: contrato novo (D10)" if c["MOTIVO"] == "CONTRATO_NOVO"
                             else "re-medir: prova com mais de %d dias (promovida em %s)"
                             % (REVALIDAR_ELEGIVEIS_DIAS, (c["PROMOVIDA_EM"] or "?")[:19])))
        feitas.append({k: c[k] for k in ("SOURCE_ID", "MOTIVO")})
    return {"CANDIDATAS": len(cands), "ENFILEIRADAS": feitas}


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

    # Nivel 0b — REVALIDAR: o que o portao tem por ELIGIBLE tem de ser re-medido
    # (B3). Sem rede propria: so enfileira VALIDATE_ROUTE; a rede e a do worker.
    rv = revalidar_elegiveis(agora)
    if rv["ENFILEIRADAS"]:
        m["REVALIDAR"] = rv
        m["ACCOES"].append("REVALIDAR")

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

    # Nivel 2 — DISCOVERY: so quando o proprio acervo esta baixo.
    pend = candidatas_por_qualificar()
    m["CANDIDATAS_POR_QUALIFICAR"] = pend

    # Re-medir elegíveis DEPOIS do feeder: se ele acabou de criar tarefas, a
    # fila já não está vazia e o discovery não precisa de disparar agora.
    eligible_agora = len(F.elegiveis())
    m["QUEUE_ELIGIBLE_APOS_FEEDER"] = eligible_agora

    if eligible_agora > QUEUE_LOW_WATERMARK or pend > CANDIDATE_LOW_WATERMARK:
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

    # ⚠️ IMPASSE B4 (23/09): fila e acervo a zero, e o gatilho esperava 54 min.
    # O intervalo existe contra a RAJADA (discovery que nada acha, repetido a
    # cada 15 s). Chegar a zero DEPOIS de trabalho feito nao e rajada: a fila
    # mudou desde o ultimo discovery, logo dispara ja. Fila igual a do ultimo
    # discovery = nada aconteceu desde entao -> o intervalo manda.
    #
    #     CHEGOU A ZERO AGORA != CONTINUA A ZERO DESDE O ULTIMO CRAWL.
    #
    # Sem assinatura gravada (estado de antes desta regra) o intervalo manda.
    fila_no_ultimo = estado.get("DISCOVERY_ASSINATURA_FILA")
    chegou_a_zero = (eligible_agora == 0 and pend == 0 and fila_no_ultimo is not None
                     and fila_no_ultimo != assinatura_da_fila())
    if faltam > 0 and chegou_a_zero:
        m["DISCOVERY_ANTECIPADO"] = "fila mudou desde o ultimo discovery e chegou a zero"
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
    estado["DISCOVERY_ASSINATURA_FILA"] = assinatura_da_fila()
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
