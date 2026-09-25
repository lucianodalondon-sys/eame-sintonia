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


# ── REPARO ANTES DE DISCOVERY (REPARO-FONTES-V1, R1, 23/09/2026) ──────────────
# Pergunta do dono: «porque o bot esta procurando fontes novas e nao esta
# validando as que ja achou?». Medido no livro vivo as 15:10: 400 fontes em
# CONTRACTED_CANARY_FAILED e 102 em CANARY_PENDING, nenhuma com tarefa aberta.
# O alimentador nao tinha caminho de volta para elas: o REVALIDATE do
# `alimentar_fila.py` so corre a mao, e re-canariar o MESMO contrato da o MESMO
# EMPTY_LIST. O que faltava era reparar o contrato (worker REPAIR_CONTRACT).
#
#   CONTRACTED_CANARY_FAILED (HTML ou sem contrato), nunca reparada -> REPAIR_CONTRACT
#   CANARY_PENDING sem tarefa aberta e com contrato HTML             -> VALIDATE_ROUTE
#       (re-canariar com o detector de hoje; se falhar, cai na linha de cima)
#   CANARY_PENDING sem contrato                                      -> REPAIR_CONTRACT
#
# UM reparo por fonte: se o canario do contrato reparado tambem falha, a fonte
# fica CONTRACTED_CANARY_FAILED com as duas provas, e nao volta — um segundo
# reparo leria a mesma pagina e acharia o mesmo padrao. So um reparo que morreu
# por transporte (FAILED) volta, passado REPARO_RETOMA_S.
#
# E DISCOVERY SO QUANDO NAO HA REPARO ELEGIVEL: fonte ja achada vem antes de
# fonte nova (talvez_alimentar, Nivel 2).
#
# REPARAR_POR_VOLTA = 20
#   WHY: progressivo como o resto deste ficheiro (o gatilho so corre com a fila
#   elegivel <= QUEUE_LOW_WATERMARK). 20 reparos x <= 4 pedidos + o canario de
#   cada (<= 2) ~ 120 pedidos por volta, abaixo dos 250 de uma DISCOVERY.
# REPARO_RETOMA_S = 86400
#   WHY: o mesmo ritmo de «intermitente» da fila (6h/24h/72h), no degrau do meio.
# REVALIDAR_PENDENTE_S = 86400
#   WHY: uma CANARY_PENDING cujo canario correu ha menos de um dia e ficou la e
#   uma que o circuito ja viu hoje; re-medir antes disso e eco.
REPARAR_POR_VOLTA = 20
REPARO_RETOMA_S = 86400
REVALIDAR_PENDENTE_S = 86400
# ⚠️ AS QUALIFY DE YOUTUBE NAO SE DESBLOQUEIAM AQUI (reparo-fontes-v2). Na v1 o
# gatilho reabria as barradas pelo texto «YouTube exige channel_id e molde de
# video», porque o worker dessa linha (com a SOC2) ja dava rota ao canal. Esta
# linha retirou a SOC2: o worker de hoje escreve ESSE MESMO texto. Reabri-las
# seria um eco sem fim — reabre, o worker volta a barrar, a volta seguinte
# reabre. O YouTube volta quando a rota do Scrap voltar a linha, com o dono dela.
_ABERTAS = frozenset({F.PENDING, F.IN_PROGRESS, F.WAITING_RETRY})
CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"


def candidatas_a_reparar(agora: datetime, *, estados: dict | None = None,
                         contratos: dict | None = None,
                         tarefas: list | None = None) -> list[dict]:
    """[{SOURCE_ID, TASK_TYPE, MOTIVO}] por ordem. Nao escreve nada."""
    import lifecycle as LC         # noqa: E402
    estados = estados if estados is not None else LC.snapshot()
    if contratos is None:
        contratos = ({c["SOURCE_ID"]: c for c in
                      json.loads(CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}
                     if CONTRATOS.exists() else {})
    tarefas = tarefas if tarefas is not None else F._ler()["TAREFAS"]
    abertas, reparos, ultima_rota = set(), {}, {}
    for t in tarefas:
        sid = t["SOURCE_ID"]
        if t["STATUS"] in _ABERTAS:
            abertas.add(sid)
        if t["TASK_TYPE"] == F.REPAIR_CONTRACT:
            reparos.setdefault(sid, []).append(t)
        if t["TASK_TYPE"] in (F.VALIDATE_ROUTE, F.CANARY):
            u = _quando(t.get("UPDATED_AT"))
            if u and (sid not in ultima_rota or u > ultima_rota[sid]):
                ultima_rota[sid] = u

    def _ja_reparada(sid: str) -> bool:
        for t in reparos.get(sid, []):
            if t["STATUS"] != F.FAILED:
                return True
            u = _quando(t.get("UPDATED_AT"))
            if u and (agora - u).total_seconds() < REPARO_RETOMA_S:
                return True
        return False

    import revisao_ready as REV   # noqa: E402
    revistas = {s: x for s, x in REV._ler().items() if x.get("REVISTO_EM")}

    def _leitura_nova(sid: str) -> bool:
        """So as leituras com data (REVISTO_EM) e mais novas que a ultima rota/canario."""
        x = revistas.get(sid)
        if not x:
            return False
        u = ultima_rota.get(sid)
        r = _quando(x["REVISTO_EM"])
        return r is not None and (u is None or u < r)

    def _html(c: dict | None) -> bool:
        return (c or {}).get("ACQUISITION", {}).get("STRATEGY") in (None, "HTML_LINK_DISCOVERY")

    out = []
    for sid in sorted(estados):
        e = estados[sid]
        if not sid.startswith("IT-") or sid in abertas:
            continue
        c = contratos.get(sid)
        if e == LC.CONTRACTED_CANARY_FAILED and _leitura_nova(sid):
            # REVISAO-15: a fonte ja reparada ganhou uma leitura DEPOIS do ultimo
            # canario — re-medir UMA vez, para a trava da revisao decidir com ela
            # (LIMPA -> READY pela regua; SUSPEITA -> o motivo fica no livro).
            out.append({"SOURCE_ID": sid, "TASK_TYPE": F.VALIDATE_ROUTE, "ORDEM": 0,
                        "MOTIVO": "revisao nova (%s) depois do ultimo canario: re-medir uma vez"
                                  % revistas[sid]["REVISTO_EM"][:19]})
        elif e == LC.CONTRACTED_CANARY_FAILED:
            if _html(c) and not _ja_reparada(sid):
                out.append({"SOURCE_ID": sid, "TASK_TYPE": F.REPAIR_CONTRACT, "ORDEM": 1,
                            "MOTIVO": "canario falhou e o contrato nunca foi reparado"})
        elif e == LC.CANARY_PENDING:
            if c is None:
                if not _ja_reparada(sid):
                    out.append({"SOURCE_ID": sid, "TASK_TYPE": F.REPAIR_CONTRACT, "ORDEM": 1,
                                "MOTIVO": "CANARY_PENDING sem contrato: escrever pelo reparo"})
            elif _html(c):
                u = ultima_rota.get(sid)
                if u is None or (agora - u).total_seconds() >= REVALIDAR_PENDENTE_S:
                    out.append({"SOURCE_ID": sid, "TASK_TYPE": F.VALIDATE_ROUTE, "ORDEM": 0,
                                "MOTIVO": "CANARY_PENDING sem tarefa: re-canariar com o detector de hoje"})
    out.sort(key=lambda x: (x["ORDEM"], x["SOURCE_ID"]))
    return out


ASSINATURA_SEM_TERRITORIO = "territorio indeterminado pelo nome"


def requalificar_se_a_prova_mudou(agora: datetime) -> list[str]:
    """QUALIFY barrada por «territorio indeterminado» volta a PENDING SO se a
    prova da casa, HOJE, decide: a regra do nome (`territorio_de`) ou uma
    decisao semantica com PAIS=IT (`decisao_semantica`). Sem prova nova, fica
    onde esta — e continua SEMANTIC_REVIEW, que e a verdade (NAO SEI).

    Medido na copia de 23/09 18:21Z: 179 barradas assim, 0 com prova nova. A
    funcao existe para a proxima regra ou decisao nao ficar outra vez sem
    caminho de volta, como ficaram as 21 do YouTube."""
    import atribuir_source_id as ASI   # noqa: E402
    import decisao_semantica as DS     # noqa: E402
    sys.path.insert(0, str(RAIZ / "candidatas"))
    import fonte_nova as FN            # noqa: E402
    fichas = {c.get("CANDIDATA_ID"): c for c in FN.carregar().get("CANDIDATAS", [])}
    alvo = []
    for t in F._ler()["TAREFAS"]:
        if (t["TASK_TYPE"] != F.QUALIFY or t["STATUS"] != F.BLOCKED
                or not (t.get("LAST_ERROR") or "").startswith(ASSINATURA_SEM_TERRITORIO)):
            continue
        f = fichas.get(t["SOURCE_ID"])
        if not f:
            continue
        terr, _ = ASI.territorio_de({"NOME": f.get("NOME", ""), "URL": f.get("URL", ""),
                                     "CONTENT_VALUE_TYPE": []})
        d, _ = DS.decisao_para(t["SOURCE_ID"], f) if terr == "NAO SEI" else (None, "")
        if terr != "NAO SEI" or (d and d.get("PAIS") == "IT"):
            alvo.append(t["TASK_ID"])
    if not alvo:
        return []
    d = F._ler()
    for t in d["TAREFAS"]:
        if t["TASK_ID"] in alvo and t["STATUS"] == F.BLOCKED:
            t["STATUS"] = F.PENDING
            t["LAST_ERROR"] = "reenfileirada: a prova da casa decide hoje o territorio (era: %s)" \
                              % (t.get("LAST_ERROR") or "")[:80]
            t["UPDATED_AT"] = agora.isoformat()
    F._gravar(d)
    return alvo


def reparar_encalhadas(agora: datetime, **kw) -> dict:
    """Enfileira ate REPARAR_POR_VOLTA. Devolve o que fez e quanto ficou."""
    desbloq = requalificar_se_a_prova_mudou(agora)
    cands = candidatas_a_reparar(agora, **kw)
    feitas = []
    for c in cands[:REPARAR_POR_VOLTA]:
        F.enfileirar(c["SOURCE_ID"], c["TASK_TYPE"],
                     priority=55 if c["TASK_TYPE"] == F.VALIDATE_ROUTE else 50,
                     motivo="reparo antes de discovery: %s" % c["MOTIVO"])
        feitas.append({k: c[k] for k in ("SOURCE_ID", "TASK_TYPE")})
    return {"CANDIDATAS": len(cands), "ENFILEIRADAS": feitas,
            "RESTAM": max(0, len(cands) - len(feitas)),
            "QUALIFY_REQUALIFICADAS": len(desbloq)}


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

    # Nivel 0c — REPARAR: fonte ja achada e encalhada volta a ser trabalho (R1).
    rp = reparar_encalhadas(agora)
    m["REPARAR"] = rp
    if rp["ENFILEIRADAS"] or rp["QUALIFY_REQUALIFICADAS"]:
        m["ACCOES"].append("REPARAR")

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

    # ⚠️ REPARO ANTES DE DISCOVERY (R1). Enquanto houver fonte ja achada por
    # reparar — na fila ou a espera da proxima volta — nao se procura fonte nova.
    reparo_aberto = sum(1 for t in F._ler()["TAREFAS"]
                        if t["TASK_TYPE"] == F.REPAIR_CONTRACT and t["STATUS"] in _ABERTAS)
    m["REPARO_PENDENTE"] = rp["RESTAM"] + reparo_aberto
    if m["REPARO_PENDENTE"] > 0:
        m["DECISAO"] = "REPARO_ANTES_DE_DISCOVERY"
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
