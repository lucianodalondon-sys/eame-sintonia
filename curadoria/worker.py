#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O WORKER DO SOURCE CURATOR — pega trabalho, faz UMA etapa, persiste, segue.

    NUNCA DEPENDER DE UM HUMANO PARA CADA SOURCE_ID.

O ciclo e deliberadamente burro e por isso e que sobrevive:

    1. buscar proximo trabalho elegivel
    2. executar UMA etapa
    3. persistir o resultado
    4. actualizar o estado da fonte
    5. pegar o proximo

Uma etapa por volta, nunca duas. Se o processo morre entre a 2 e a 3, quem
reabrir o disco ve uma tarefa IN_PROGRESS e sabe que alguem comecou e nao
fechou — que e a verdade. Um worker que fizesse o ciclo inteiro por fonte
perderia tudo a meio e nao saberia dizer onde parou.

---------------------------------------------------------------------------
O QUE ESTE WORKER NAO FAZ

    NAO COLETA. NAO CUNHA RUN_ID. NAO ESCREVE RAW.
    NAO TOCA ADMISSION, SALA, INTELLIGENCE NEM BIG COLLECTION.

O canario abre UM documento para provar que a rota resolve. Isso e prova
sobre a FONTE, nao aquisicao de conteudo: nada e preservado como acervo.

    VALIDAR != COLETAR.

---------------------------------------------------------------------------
HUMAN REVIEW — quando o worker para e chama alguem

Custo, credencial, policy, conflito semantico, decisao irreversivel, e o
UNKNOWN que nao se resolve sozinho. Tudo o resto ele decide, porque tudo o
resto tem evidencia deterministica.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import atribuir_source_id as ASI   # noqa: E402
import canario as CANARIO          # noqa: E402
import decisao_semantica as DS     # noqa: E402
import fila as F                   # noqa: E402
import fonte_nova as FN            # noqa: E402
import gate_de_rota as GATE        # noqa: E402
import lifecycle as LC             # noqa: E402
import rota_do_scrap_youtube as RSY  # noqa: E402
import rota_do_scrap_social as RSS  # noqa: E402
import ready_split as RS           # noqa: E402
import revisao_ready as REV        # noqa: E402

CONTRATO = "SOURCE_CURATOR_WORKER/v1"
CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
EVIDENCIA = RAIZ / "curadoria" / "LIFECYCLE-EVIDENCE-V1.json"
ALLOCATION = RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"

# Classes de falha que NUNCA se tentam outra vez automaticamente.
# Tentar de novo o que esta barrado por politica nao e persistencia: e contorno.
NAO_INSISTIR = {"POLICY", "AUTH", "ROBOTS"}

# ⚠️ AS ETAPAS QUE, POR DESENHO, CORREM SEM CONTRATO.
# Uma candidata nova nao tem contrato — nao ter e a condicao de partida, nao um
# defeito. QUALIFY existe para caracterizar essa candidata e BUILD_CONTRACT
# existe para produzir o contrato. Exigir contrato a qualquer uma das duas seria
# pedir o resultado como pre-condicao de si proprio. Todas as outras etapas
# operam SOBRE um contrato e por isso continuam a exigi-lo.
SEM_CONTRATO_POR_DESENHO = frozenset({F.BUILD_CONTRACT, F.QUALIFY, F.REPAIR_CONTRACT})
# REPAIR_CONTRACT tambem: 25 das falhadas nunca tiveram contrato — o molde foi
# reprovado pelo validador («LINK_PATTERN casa com a propria INDEX_URL»). O
# reparo parte do mesmo molde e so o grava se o padrao novo passar a porta.

# Tipos sociais barrados por politica/capacidade conhecida (mesma lei da ponte).
#
# ⚠️ SOC-ONDA2 (24/09/2026): o LINKEDIN saiu daqui. A D23 (dono real) autorizou o
# VIDEO de pagina publica de ORGANIZACAO, e o Scrap declara a fase
# `video-linkedin` com a matriz ALLOWED — a candidata LinkedIn segue o mesmo
# caminho do YouTube (identidade + ligacao oficial + territorio -> numero ->
# contrato que NOMEIA a rota do Scrap). O INSTAGRAM tambem saiu da lista cega:
# o bloqueio dele agora e medido na matriz (`RSS.instagram_listar_permitido`),
# e diz o nome do buraco — a D22 abre o Reel por URL, nao a conta.
_SOCIAL_POLICY = frozenset()
_SOCIAL_CAPABILITY = frozenset({"FACEBOOK"})


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _contratos() -> dict:
    d = json.loads(CONTRATOS.read_text(encoding="utf-8"))
    return {c["SOURCE_ID"]: c for c in d["FONTES"]}


def _guardar_evidencia(source_id: str, etapa: str, dados: dict) -> str:
    """A prova fica num ficheiro proprio do Curator, e a transicao guarda a
    referencia. O livro de estado nao engorda com payloads."""
    if EVIDENCIA.exists():
        d = json.loads(EVIDENCIA.read_text(encoding="utf-8"))
    else:
        d = {"DATASET": "LIFECYCLE-EVIDENCE-V1", "CONTRATO": CONTRATO,
             "LEI": "prova por etapa. EVIDENCE_REF do livro aponta para aqui.",
             "PROVAS": []}
    ref = "EV-%s-%s-%04d" % (source_id, etapa, len(d["PROVAS"]) + 1)
    d["PROVAS"].append({"EVIDENCE_REF": ref, "SOURCE_ID": source_id,
                        "ETAPA": etapa, "OBSERVED_AT": agora(), "DADOS": dados})
    EVIDENCIA.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    return ref


# ---------------------------------------------------------------------------
# AS ETAPAS — cada uma devolve (RESULTADO, detalhe)
#
# RESULTADO ∈ {OK, RETRY, BLOCK, FAIL}
#   OK     avanca o estado
#   RETRY  transporte/429 — adia ESTA tarefa, nao a fila
#   BLOCK  policy/robots/auth — para, e diz de quem e o servico que falta
#   FAIL   a fonte respondeu e o que devolveu nao serve
# ---------------------------------------------------------------------------
def etapa_validate_route(source_id: str, contrato: dict) -> tuple[str, dict]:
    """O portao do anfitriao, lido AO VIVO.

        ROTA QUE RESPONDE != ROTA PERMITIDA.

    Um 200 nao torna uma rota legal. Esta etapa corre ANTES do canario de
    proposito: nao se bate a uma porta que ja se sabe estar proibida.
    """
    aq = contrato.get("ACQUISITION", {})
    # ⚠️ ROTA DO SCRAP: O PORTAO E A MATRIZ DELE, NAO O ROBOTS (SOC2).
    # A fase `canal-youtube` fala com a API oficial; nao ha pagina a que pedir
    # robots. Quem diz se a rota e permitida e a matriz do Scrap, lida por
    # `rota_do_scrap_youtube.conferir` — e se ela deixar de a declarar, isto
    # para aqui, antes de qualquer canario.
    if aq.get("STRATEGY") == RSY.STRATEGY:
        ok, porque = RSS.conferir(aq)
        if ok:
            return "OK", {"ROTA": aq.get("ROTA_DECLARADA_PELO_SCRAP"), "PERMITIDO": True,
                          "PORTAO": "matriz do Scrap", "PORQUE": porque}
        return "BLOCK", {"CLASSE": "CAPABILITY", "PORTAO": "matriz do Scrap",
                         "PORQUE": "a rota do Scrap nao confere: %s" % porque}
    # D42 (2): a rota fixa (STATIC_ENDPOINT) tem URL, nao INDEX_URL — sem isto, «a pagina e o
    # boletim» falhava aqui («sem endereco») antes de o canario a ver
    url = aq.get("FEED_URL") or aq.get("INDEX_URL") or aq.get("URL")
    if not url:
        return "FAIL", {"PORQUE": "contrato sem endereco de aquisicao"}
    host = url.split("/")[2]
    try:
        rp, origem = GATE.robots_de(host)
    except Exception as e:
        return "RETRY", {"PORQUE": "robots.txt ilegivel: %s" % type(e).__name__}

    if GATE.permitido(url, rp):
        return "OK", {"ROTA": url, "ROBOTS": origem[:120], "PERMITIDO": True}

    # ⚠️ NAO SEI != PROIBIDO — e aqui as duas coisas chegam pela MESMA porta.
    # `robots_de` devolve Disallow-total em dois casos muito diferentes: o host
    # proibiu mesmo, OU a rede nao deixou ler o ficheiro (e entao ele condena
    # «por prudencia», dizendo-o no texto que devolve). Prudencia e a decisao
    # certa para nao bater a porta; mas gravar CONTRACT_READY_ROUTE_BLOCKED por
    # um timeout e condenar uma fonte boa por defeito do nosso lado — o mesmo
    # erro que o proprio gate_de_rota documenta ter cometido com `nomisma.it`.
    #
    #     UM TIMEOUT NAO E UM DISALLOW.
    #
    # Logo: rede em baixo -> RETRY (volta depois, por conta propria).
    #       Disallow lido de verdade -> BLOCK (para, e chama o dono da politica).
    if "inacessivel" in origem:
        return "RETRY", {"ROTA": url, "ROBOTS": origem[:120],
                         "PORQUE": "robots nao pode ser lido — UNKNOWN, nao proibicao"}
    return "BLOCK", {"CLASSE": "ROBOTS", "ROTA": url, "ROBOTS": origem[:120],
                     "PORQUE": "o endereco do contrato casa com Disallow no robots vivo"}


def etapa_canary(source_id: str, contrato: dict) -> tuple[str, dict]:
    """A corrida real: o contrato resolve e sai um ITEM com identidade?

    Distinguir 429 de falha da fonte e o coracao da FASE 4: um 429 e a
    plataforma a pedir tempo, nao a fonte a dizer que nao presta.
    """
    estrategia = contrato.get("ACQUISITION", {}).get("STRATEGY")
    # ⚠️ O CANARIO DE UMA ROTA DO SCRAP E UMA COLHEITA DO SCRAP. O Curator nao
    # a corre (a chave vive no runner, e o Scrap e de outro dono), e a regua de
    # promocao dos quatro passos e de HTML. Promover aqui seria READY sem prova.
    # O caminho normal nem chega a esta etapa (VALIDATE_ROUTE para em
    # CANARY_PENDING); isto e a guarda para quem a enfileirar por outra porta.
    if estrategia == RSY.STRATEGY:
        return "BLOCK", {"CLASSE": "CAPABILITY", "CANARIO": "DO_SCRAP",
                         "PORQUE": ("o canario desta rota e uma colheita do Scrap "
                                    "(fase %s, --fonte %s, %s) pedida pelo orquestrador; "
                                    "o Curator nao corre o Scrap nem promove rota social "
                                    "pela regua de HTML"
                                    % (contrato.get("ACQUISITION", {}).get("FASE"), source_id,
                                       contrato.get("ACQUISITION", {}).get("FILTROS")))}
    try:
        if estrategia == "YOUTUBE_CHANNEL_FEED":
            r = CANARIO.canario_youtube(contrato)
        elif contrato.get("FORMA") == CANARIO.FORMA_PAGINA_E_BOLETIM:
            # D42 (2): a pagina e o boletim — a forma e explicita no contrato, nunca adivinhada
            r = CANARIO.canario_pagina_boletim(contrato)
        else:
            r = CANARIO.canario_html(contrato)
    except Exception as e:
        return "RETRY", {"PORQUE": "%s: %s" % (type(e).__name__, str(e)[:120])}

    if r.get("PASS"):
        return "OK", r
    if r.get("HTTP") in (429, 503):
        return "RETRY", r
    if r.get("HTTP") in (401, 403):
        return "BLOCK", dict(r, CLASSE="AUTH")
    if r.get("CLASSE") == "UNKNOWN":
        return "RETRY", r
    return "FAIL", r


def etapa_build_contract(source_id: str, contrato: dict | None) -> tuple[str, dict]:
    """Escreve o contrato de uma fonte que tem identidade mas nao tem rota.

    Reutiliza o MOLDE que as 77 fontes ja atravessaram
    (`escrever_contratos.contrato_html`) — uma regua nova faria as fontes
    novas entrarem por criterio diferente das que ja ca estao.

        O MOLDE E O QUE TORNA A FONTE NOVA COMPARAVEL AS ANTIGAS.

    O contrato escrito aqui NAO e uma prontidao: e uma hipotese de rota que
    o canario a seguir tem de confirmar. Por isso a etapa termina em
    CANARY_PENDING e enfileira o canario, nunca em READY.
    """
    import escrever_contratos as EC
    import validar_contratos as VC

    # O MESMO registo que o QUALIFY escreve (ALLOCATION), e nao um caminho
    # fixo ao lado: um teste que o redireciona tem de ver aqui o que la gravou.
    alloc = _ler_alloc()
    n = next((x for x in alloc["NOVAS"] if x["SOURCE_ID"] == source_id), None)
    if not n:
        return "FAIL", {"PORQUE": "sem identidade alocada para esta fonte"}
    if not n.get("URL"):
        return "FAIL", {"PORQUE": "identidade sem endereco canonico"}

    # ⚠️ NAO CONTRATAR O QUE O DONO EXCLUIU DE PROPOSITO.
    #
    # A missao 04 so escreveu contrato para quem tinha
    # `SMALL_ADAPTATION_REQUIRED` a comecar por «NAO». As restantes ficaram
    # de fora por DECISAO — precisam de capacidade que ainda nao existe
    # («ramo de indice»: a entrada nao lista os itens, e o molde generico
    # nunca os encontraria).
    #
    # Medido: as 7 que sobraram estao TODAS marcadas «SIM — ramo de indice».
    # Contrata-las com o molde generico produziria contratos que passam na
    # validacao e falham sempre no canario — um EMPTY_LIST garantido, com ar
    # de trabalho feito.
    #
    #     UMA FILA UNIFORME PODE SER UMA DECISAO UNIFORME, NAO UM ESQUECIMENTO.
    #     O GARGALO DELAS E CAPACIDADE, E CAPACIDADE TEM OUTRO DONO.
    # ── YOUTUBE: O MOLDE QUE NOMEIA A ROTA DO SCRAP (SOC2) ──────────────────
    # A caracterizacao das HTML nao se aplica: o canal tem identidade propria
    # (o channel_id que o QUALIFY guardou) e a rota e a do Scrap.
    if n.get("FAMILY") == "YOUTUBE":
        canal = n.get("SOURCE_NATIVE_ID")
        if not canal:
            return "FAIL", {"PORQUE": "canal YouTube sem channel_id na alocacao"}
        outras = [x for x in _donos_do_canal(canal) if x != source_id]
        if outras:
            return "BLOCK", {"CLASSE": "SEMANTIC",
                             "PORQUE": "o canal %s ja e de %s: nao se escreve um segundo "
                                       "contrato para o mesmo canal" % (canal, ", ".join(outras))}
        novo = EC.contrato_youtube_scrap(n, canal)
    elif n.get("FAMILY") == "LINKEDIN":
        slug = n.get("SOURCE_NATIVE_ID")
        if not slug:
            return "FAIL", {"PORQUE": "pagina LinkedIn sem slug na alocacao"}
        outras = [x for x in _donos_da_pagina(slug) if x != source_id]
        if outras:
            return "BLOCK", {"CLASSE": "SEMANTIC",
                             "PORQUE": "a pagina %s ja e de %s: nao se escreve um segundo "
                                       "contrato para a mesma pagina" % (slug, ", ".join(outras))}
        novo = EC.contrato_linkedin_scrap(n, slug)
    else:
        novo = None
    car = json.loads((RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json")
                     .read_text(encoding="utf-8"))
    f = next((x for x in car["FONTES"]
              if x.get("CANDIDATE_ID") == n.get("CANDIDATE_ID")), {})
    adaptacao = str(f.get("SMALL_ADAPTATION_REQUIRED", ""))
    if novo is None and adaptacao and not adaptacao.startswith("NAO"):
        return "BLOCK", {"CLASSE": "CAPABILITY",
                         "PORQUE": ("exige capacidade nova (%s) — o molde "
                                    "generico daria EMPTY_LIST garantido; "
                                    "dono: SCRAP ENGINEER" % adaptacao[:60])}
    if novo is None and f.get("FAMILY") not in ("HTML_SITE", None, ""):
        return "BLOCK", {"CLASSE": "CAPABILITY",
                         "PORQUE": "familia %s sem molde provado nesta arvore"
                                   % f.get("FAMILY")}

    if novo is None:
        novo = EC.contrato_html(n, f)

    # O carimbo de procedencia faz parte do contrato, nao do script que o
    # escreveu: sem ele o proprio validador da casa recusa a linha.
    # ── D61 (SOC-TEMPO): O LUGAR DE QUEM PUBLICA, NO CONTRATO DA CONTA SOCIAL ──
    # A conta so tem numero porque o site oficial da organizacao aponta para ela;
    # e esse site que diz onde esta quem publica (`leis/lugar_da_organizacao.py`:
    # sede no cadastro-mestre, senao pais da ficha do site no Atlas, senao NAO SEI
    # com o porque). O contrato e o dono; o Scrap le-o daqui.
    if n.get("FAMILY") in ("LINKEDIN", "YOUTUBE"):
        if str(RAIZ / "leis") not in sys.path:
            sys.path.append(str(RAIZ / "leis"))
        import lugar_da_organizacao as LO
        ficha = _ficha_candidata(n.get("CANDIDATE_ID") or "") or {}
        site, _como = RSY.ligacao_oficial(ficha)
        novo.update(LO.lugar_da_organizacao(site))
    novo["SOURCE_CONTRACT_VERSION"] = EC.VERSAO
    novo["SOURCE_CONTRACT_HASH"] = EC.hash_do_contrato(novo)
    novo["ONBOARDED_BY"] = ("SOURCE-CURATOR-WORKER · contrato escrito pelo "
                            "ciclo continuo a partir do molde da missao 04")

    # Um contrato so entra na tabela depois de passar as MESMAS portas que
    # validaram os 77 — validar depois de escrever seria escrever primeiro e
    # perguntar depois.
    ok, falhas = VC.validar([novo])
    if falhas:
        return "FAIL", {"PORQUE": "contrato reprovado: %s"
                        % str(falhas[0])[:140], "CONTRATO": novo["SOURCE_ID"]}

    d = json.loads(CONTRATOS.read_text(encoding="utf-8"))
    if any(c["SOURCE_ID"] == source_id for c in d["FONTES"]):
        return "OK", {"CONTRATO": source_id, "NOTA": "ja existia; nada reescrito"}
    d["FONTES"].append(novo)
    CONTRATOS.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    return "OK", {"CONTRATO": source_id,
                  "STRATEGY": novo["ACQUISITION"]["STRATEGY"],
                  "INDEX_URL": (novo["ACQUISITION"].get("INDEX_URL")
                                or "%s/%s" % (novo["ACQUISITION"].get("EXECUTOR"),
                                              novo["ACQUISITION"].get("FASE")))[:110]}


# ---------------------------------------------------------------------------
# QUALIFY — o primeiro degrau de uma candidata sem SOURCE_ID nem contrato.
#
#     ENFILEIRADA != PROCESSAVEL.
#
# A ponte enche a fila com QUALIFY cuja chave e o CANDIDATA_ID (CAND-xxxx), nao
# um SOURCE_ID — porque o SOURCE_ID e precisamente o que ainda nao existe. Sem
# esta etapa, a fila enchia de trabalho que o worker nao sabia fazer, e cada
# QUALIFY morria em BLOCK «etapa sem executor».
#
# Tudo aqui e deterministico e SEM LLM: le a ficha, mede o territorio pela regra
# do Atlas (nome/URL), pede o SOURCE_ID canonico (ou UNKNOWN, sem fabricar) e
# reenfileira o degrau seguinte. OPUS entraria so na ambiguidade semantica
# (territorio NAO SEI), e mesmo ai o resultado volta ao lifecycle deterministico.
# ---------------------------------------------------------------------------
def _ficha_candidata(cand_id: str) -> dict | None:
    """A ficha da candidata, lida pela PORTA (candidatas/fonte_nova), nao por um
    ficheiro qualquer. A porta e a fonte de verdade da candidata."""
    doc = FN.carregar()
    for c in doc.get("CANDIDATAS", []):
        if c.get("CANDIDATA_ID") == cand_id:
            return c
    return None


def _ler_alloc() -> dict:
    if ALLOCATION.exists():
        return json.loads(ALLOCATION.read_text(encoding="utf-8"))
    return {"DATASET": "SOURCE-ID-ALLOCATION-V1",
            "MAIOR_POR_TERRITORIO_ANTES": {}, "ATRIBUIDOS": 0, "NOVAS": []}


def _donos_do_canal(canal: str) -> list[str]:
    """Os SOURCE_ID que ja ligam este canal: tabela do coletor, contratos escritos
    a mao, ESTE livro de contratos e ESTE registo de alocacao."""
    livro = json.loads(CONTRATOS.read_text(encoding="utf-8")) if CONTRATOS.exists() else {}
    return RSY.canal_conhecido(canal, livro=livro, alloc=_ler_alloc())


def _donos_da_pagina(slug: str) -> list[str]:
    """Os SOURCE_ID que ja ligam esta pagina LinkedIn (tabela, livro, alocacao)."""
    livro = json.loads(CONTRATOS.read_text(encoding="utf-8")) if CONTRATOS.exists() else {}
    return RSS.pagina_conhecida(slug, livro=livro, alloc=_ler_alloc())


def _gravar_alloc(d: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(ALLOCATION.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, ALLOCATION)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _max_por_territorio(alloc: dict) -> dict:
    """O maior numero usado por territorio, para continuar dali. NUNCA recicla.

    ⚠️ CAVEAT DE FRAGMENTACAO (medido e documentado noutras missoes): o registo
    de SOURCE_ID vive espalhado por varias branches. Este calculo garante que
    nao ha colisao DENTRO deste registo — a sequencia parte de
    MAIOR_POR_TERRITORIO_ANTES (que ja absorveu o Atlas + onboarded no momento
    da alocacao em lote) e do maior ja atribuido aqui. Reconciliar colisoes
    entre branches e outra lane, e esta missao NAO lhe toca.
    """
    maior: dict[str, int] = {k: int(v) for k, v in
                             alloc.get("MAIOR_POR_TERRITORIO_ANTES", {}).items()}
    for n in alloc.get("NOVAS", []):
        m = re.match(r"^IT-(T\d+)-(\d+)$", str(n.get("SOURCE_ID", "")))
        if m:
            maior[m.group(1)] = max(maior.get(m.group(1), 0), int(m.group(2)))
    return maior


def _alocar_source_id(cand_id: str, territorio: str, familia: str,
                      ficha: dict, porque: str, native: str | None = None,
                      mesma_organizacao: dict | None = None,
                      native_kind: str = "YOUTUBE_CHANNEL_ID") -> tuple[str, bool]:
    """Pede o SOURCE_ID canonico ao registo de alocacao. Idempotente: se esta
    candidata ja tem numero, devolve o mesmo (nunca cunha um segundo).

    Devolve (SOURCE_ID, novo?).
    """
    alloc = _ler_alloc()
    for n in alloc.get("NOVAS", []):
        if n.get("CANDIDATE_ID") == cand_id:
            return n["SOURCE_ID"], False
    maior = _max_por_territorio(alloc)
    seq = maior.get(territorio, 0) + 1
    sid = "IT-%s-%03d" % (territorio, seq)
    nova = {
        "CANDIDATE_ID": cand_id,
        "SOURCE_ID": sid,
        "TERRITORY": territorio,
        "TERRITORY_REASON": porque,
        "NOME": ficha.get("NOME", ""),
        "URL": ficha.get("URL", ""),
        "FAMILY": familia,
        "MESMA_ORGANIZACAO": mesma_organizacao,
        **({"SOURCE_NATIVE_ID": native, "SOURCE_NATIVE_ID_KIND": native_kind}
           if native else {}),
        "ALLOCATED_BY": ("SOURCE-CURATOR-WORKER/QUALIFY — regra do Atlas "
                         "(IT-T<territorio>-<seq>, max+1, nunca recicla)"),
        "ALLOCATED_AT": agora(),
    }
    alloc.setdefault("NOVAS", []).append(nova)
    alloc["ATRIBUIDOS"] = len(alloc["NOVAS"])
    _gravar_alloc(alloc)
    return sid, True


# D80(ii): onde a casa ja escreveu numeros de fora de IT. None = o Atlas + os
# livros JSON de curadoria/ e regras/ (os testes trocam por ficheiros seus).
FONTES_DE_NUMEROS: list | None = None


def _fontes_de_numeros() -> list:
    if FONTES_DE_NUMEROS is not None:
        return list(FONTES_DE_NUMEROS)
    return ([RSY.ATLAS] + sorted((RAIZ / "curadoria").glob("*.json"))
            + sorted((RAIZ / "regras").glob("*.json")))


def _max_fora_de_it(prefixo: str, territorio: str, alloc: dict) -> int:
    """O maior <prefixo>-<territorio>-<nnn> ja escrito em qualquer livro da casa
    ou ja cunhado aqui. NUNCA recicla: um numero visto em qualquer sitio conta."""
    rx = re.compile(r"(?<![A-Z])%s-%s-(\d{3})\b" % (re.escape(prefixo), re.escape(territorio)))
    maior = 0
    for p in _fontes_de_numeros():
        p = Path(p)
        if p.exists():
            for m in rx.finditer(p.read_text(encoding="utf-8", errors="replace")):
                maior = max(maior, int(m.group(1)))
    for n in alloc.get("NOVAS_FORA_DE_IT", []):
        m = rx.fullmatch(str(n.get("SOURCE_ID", "")))
        if m:
            maior = max(maior, int(m.group(1)))
    return maior


def _qualificar_fora_de_it(cand_id: str, ficha: dict, familia: str,
                           decisao: dict) -> tuple[str, dict]:
    """D80(ii). Cunha o numero no prefixo da prova e PARA (CAPABILITY_BLOCK).

    Os numeros vivem em NOVAS_FORA_DE_IT, nao em NOVAS: quem le NOVAS (ponte,
    contratos, coletor) le numeros italianos, e um EU- ali entrava na estrada
    italiana pela porta das traseiras."""
    pais, territorio = decisao["PAIS"], decisao["TERRITORIO"]
    if familia != "HTML_SITE":
        return "BLOCK", {"CLASSE": "SEMANTIC", "SEMANTIC_PENDING": True,
                         "PORQUE": ("territorio decidido fora de IT: %s, PAIS=%s — D80(ii) "
                                    "cobre sites; %s de fora de IT fica NAO SEI"
                                    % (territorio, pais, familia))}
    import linkedin_pelo_site as LPS
    host = LPS.host(ficha.get("URL", ""))
    livro = json.loads(CONTRATOS.read_text(encoding="utf-8")) if CONTRATOS.exists() else {}
    tabela = json.loads(RSY.TABELA.read_text(encoding="utf-8")) if RSY.TABELA.exists() else {}
    atlas = RSY.ATLAS.read_text(encoding="utf-8") if RSY.ATLAS.exists() else ""
    ja = sorted(RSY._territorios_do_host(host, tabela, livro, atlas))
    alloc = _ler_alloc()
    minhas = [n for n in alloc.get("NOVAS_FORA_DE_IT", []) if n.get("CANDIDATE_ID") == cand_id]
    outras = [n["SOURCE_ID"] for n in alloc.get("NOVAS_FORA_DE_IT", [])
              if n.get("CANDIDATE_ID") != cand_id and LPS.host(n.get("URL", "")) == host]
    if not minhas and (ja or outras):
        return "BLOCK", {"CLASSE": "SEMANTIC", "SEMANTIC_PENDING": True,
                         "PORQUE": ("territorio decidido fora de IT (%s, PAIS=%s), mas o site %s "
                                    "ja tem numero na casa (%s): um site, um numero — "
                                    "decisao humana" % (territorio, pais, host,
                                                        ", ".join(ja + outras)))}
    if minhas:
        sid, novo = minhas[0]["SOURCE_ID"], False
    else:
        sid = "%s-%s-%03d" % (pais, territorio, _max_fora_de_it(pais, territorio, alloc) + 1)
        novo = True
        alloc.setdefault("NOVAS_FORA_DE_IT", []).append({
            "CANDIDATE_ID": cand_id, "SOURCE_ID": sid, "TERRITORY": territorio,
            "PAIS": pais, "NOME": ficha.get("NOME", ""), "URL": ficha.get("URL", ""),
            "FAMILY": familia,
            "TERRITORY_REASON": "decisao semantica de %s: %s" % (
                decisao.get("DECIDIDO_POR"), (decisao.get("PORQUE") or "")[:200]),
            "PROVAS": ["%s %s sha256=%s" % (p.get("PAPEL"), p.get("URL"), p.get("SHA256"))
                       for p in decisao.get("PROVAS", [])],
            "ALLOCATED_BY": ("SOURCE-CURATOR-WORKER/QUALIFY — D80(ii): prefixo canonico "
                             "<PAIS>-T<territorio>-<seq>, max+1 sobre o Atlas e os livros, "
                             "nunca recicla"),
            "ALLOCATED_AT": agora()})
        _gravar_alloc(alloc)
    return "BLOCK", {"CLASSE": "CAPABILITY", "SOURCE_ID_REAL": sid, "SOURCE_ID_NOVO": novo,
                     "TERRITORY": territorio, "PAIS": pais,
                     "PORQUE": ("D80(ii): %s -> %s (%s, PAIS=%s pela prova); PARA aqui — a "
                                "estrada de coleta so aceita IT-, sem contrato nem READY "
                                "automatico" % (cand_id, sid, territorio, pais))}


def etapa_qualify(source_id: str, contrato: dict | None) -> tuple[str, dict]:
    """O primeiro degrau. `source_id` e o CANDIDATA_ID (a fila nao tem outro).

    NUNCA promove READY. Devolve, como as outras etapas, (RESULTADO, detalhe):
      OK    -> identidade canonica alocada; BUILD_CONTRACT enfileirado
      BLOCK -> social/policy, sem capacidade (YouTube), ou identidade ambigua
      FAIL  -> a candidata nem existe na porta
    """
    cand_id = source_id
    ficha = _ficha_candidata(cand_id)
    if not ficha:
        return "FAIL", {"PORQUE": "candidata %s desconhecida na porta de entrada"
                        % cand_id}

    tipo = (ficha.get("TIPO") or "").upper()
    pais = ficha.get("PAIS") or "NAO SEI"

    # D80(i): uma candidata RECUSADA pela porta nao se qualifica. A recusa e
    # reversivel pela porta (`fonte_nova.reverter_recusa`), nunca por aqui.
    if ficha.get("ESTADO") == "RECUSADA":
        return "BLOCK", {"CLASSE": "POLICY", "RECUSADA": True,
                         "PORQUE": ("RECUSADA pela porta de entrada: %s%s"
                                    % ((ficha.get("MOTIVO_DA_RECUSA") or "")[:100],
                                       " · duplicada de %s" % ficha["DUPLICADA_DE"]
                                       if ficha.get("DUPLICADA_DE") else ""))}

    # ⚠️ A PORTA DAS TRASEIRAS NAO EXISTE. Social barrado por politica/capacidade
    # nao entra por QUALIFY — insistir no que a policy barra e contorno.
    if tipo in _SOCIAL_POLICY:
        return "BLOCK", {"CLASSE": "POLICY",
                         "PORQUE": "%s: coleta automatizada proibida pelos TOS" % tipo}
    if tipo in _SOCIAL_CAPABILITY:
        return "BLOCK", {"CLASSE": "CAPABILITY",
                         "PORQUE": "%s: sem capacidade de coleta nesta instalacao" % tipo}

    # ── INSTAGRAM (D22): O REEL ABRE-SE POR URL; A CONTA NAO SE LISTA ───────
    # A identidade de uma conta declarada no site oficial esta provada — o que
    # falta e ROTA. `instagram.profile.discovery` (a fase `janela`) e a unica
    # maneira de o Scrap listar os Reels de uma conta, e a matriz dele diz
    # ROUTE_NOT_ALLOWED. Cunhar um numero para uma fonte que nenhuma rota colhe
    # seria uma fonte com ar de pronta. O bloqueio e lido na matriz, nao escrito
    # a mao: no dia em que ela mudar, esta linha deixa de bloquear sozinha.
    if tipo == "INSTAGRAM":
        pode, porque_ig = RSS.instagram_listar_permitido()
        if not pode:
            return "BLOCK", {"CLASSE": "POLICY", "SEM_ROTA_PARA_LISTAR": True,
                             "PORQUE": ("INSTAGRAM: a D22 abre so o Reel por URL directa; "
                                        "listar os Reels da conta e %s — sem rota que "
                                        "colha a conta, sem numero" % porque_ig)}
        return "BLOCK", {"CLASSE": "CAPABILITY",
                         "PORQUE": ("INSTAGRAM: a matriz ja deixa listar (%s), mas o "
                                    "Curator nao tem molde de contrato para a conta"
                                    % porque_ig)}

    familia = {"YOUTUBE": "YOUTUBE", "LINKEDIN": "LINKEDIN"}.get(tipo, "HTML_SITE")

    # ── O YOUTUBE SEGUE PARA O SCRAP (SOC2, D17.4) ─────────────────────────
    # Aqui havia um BLOCK/CAPABILITY para toda candidata YouTube: «exige
    # channel_id e molde de video — capacidade com outro dono». Era verdade
    # quando se escreveu; deixou de ser quando o Scrap declarou a fase
    # `canal-youtube` (API oficial, matriz ALLOWED). A capacidade continua a ser
    # do outro dono — e por isso o Curator nao a imita: so NOMEIA a rota dele no
    # contrato. O que ficou do bloqueio antigo e a condicao verdadeira dele:
    # sem channel_id nao ha identidade, e sem identidade nao ha numero.
    #
    #     UM «NAO SEI FAZER» ESCRITO A MAO NAO SE DESACTUALIZA SOZINHO.
    canal = None
    if familia == "YOUTUBE":
        canal = (RSY.channel_id_da_url(ficha.get("URL", ""))
                 # SOC4: o @handle que a API oficial ja resolveu (registo com a corrida)
                 or RSY.canal_resolvido(cand_id, ficha.get("URL", "")))
        if not canal:
            return "BLOCK", {"CLASSE": "CAPABILITY", "IDENTIDADE": "NAO SEI",
                             "PORQUE": ("NAO SEI: canal YouTube sem channel_id no endereco (%s): "
                                        "@handle, /user/, /c/ e playlist so se resolvem "
                                        "pela API (youtube.channel.resolve, chave e "
                                        "rede) — sem fabricar"
                                        % (ficha.get("URL", "")[:80]))}
        # ⚠️ UM CANAL, UM SOURCE_ID. Um canal que a casa ja liga a uma fonte
        # nao recebe um segundo numero: seriam duas fontes a colher o mesmo
        # canal, e a Sala com tudo em dobro.
        ja = _donos_do_canal(canal)
        if len(ja) > 1:
            return "BLOCK", {"CLASSE": "SEMANTIC", "CHANNEL_ID": canal,
                             "PORQUE": ("o canal %s ja esta ligado a %d fontes (%s): "
                                        "colisao de identidade, decisao humana"
                                        % (canal, len(ja), ", ".join(ja)))}
        if ja:
            return "OK", {"SOURCE_ID_REAL": ja[0], "SOURCE_ID_NOVO": False,
                          "FAMILY": familia, "CHANNEL_ID": canal, "TIPO": tipo,
                          "JA_TINHA_IDENTIDADE": True,
                          "PORQUE": ("o canal %s ja e %s: nenhum numero novo; o "
                                     "contrato dessa fonte e que nomeia a rota"
                                     % (canal, ja[0]))}

    # ── LINKEDIN (D23): A PAGINA PUBLICA DE ORGANIZACAO ─────────────────────
    # A identidade e o slug de `/company/<slug>/` — o mesmo alvo que o
    # adaptador do Scrap aceita. Perfil de pessoa fica fora (D23), e
    # `/showcase/` nao e alvo do adaptador: contratar isso seria um contrato
    # que valida e reprova sempre no Scrap.
    if familia == "LINKEDIN":
        canal, porque_li = RSS.slug_linkedin(ficha.get("URL", ""))
        if not canal:
            return "BLOCK", {"CLASSE": "POLICY" if porque_li == "PERFIL_DE_PESSOA" else "CAPABILITY",
                             "IDENTIDADE": "NAO SEI",
                             "PORQUE": ("LINKEDIN %s: a rota do Scrap (video-linkedin, D23) "
                                        "le so /company/<slug>/ (%s)"
                                        % (porque_li, ficha.get("URL", "")[:80]))}
        ja = _donos_da_pagina(canal)
        if len(ja) > 1:
            return "BLOCK", {"CLASSE": "SEMANTIC", "LINKEDIN_SLUG": canal,
                             "PORQUE": ("a pagina %s ja esta ligada a %d fontes (%s): "
                                        "colisao de identidade, decisao humana"
                                        % (canal, len(ja), ", ".join(ja)))}
        if ja:
            return "OK", {"SOURCE_ID_REAL": ja[0], "SOURCE_ID_NOVO": False,
                          "FAMILY": familia, "LINKEDIN_SLUG": canal, "TIPO": tipo,
                          "JA_TINHA_IDENTIDADE": True,
                          "PORQUE": "a pagina %s ja e %s: nenhum numero novo" % (canal, ja[0])}

    # ── IDENTIDADE PROVADA = LIGACAO OFICIAL (D21 cond. 2, D24) ────────────
    # Um channel_id ou um slug dizem QUAL conta; nao dizem DE QUEM ela e. Um
    # canal «ismeaofficial» pode nao ser do ISMEA. So a pagina da propria
    # organizacao a apontar para a conta prova o dono — nome parecido nao conta.
    # Sem essa prova nao ha numero: a conta fica NAO SEI, com o buraco escrito.
    if familia in ("YOUTUBE", "LINKEDIN"):
        pagina_of, _como_of = RSY.ligacao_oficial(ficha)
        if not pagina_of:
            return "BLOCK", {"CLASSE": "SEMANTIC", "IDENTIDADE": "SEM_LIGACAO_OFICIAL",
                             "PORQUE": ("%s sem ligacao oficial escrita na ficha (o site da "
                                        "organizacao que aponta para a conta): de quem e "
                                        "a conta fica NAO SEI, sem fabricar" % tipo)}

    territorio, porque = ASI.territorio_de({
        "NOME": ficha.get("NOME", ""), "URL": ficha.get("URL", ""),
        "CONTENT_VALUE_TYPE": [],
    })

    # ── D21 · O CANAL HERDA A GAVETA DO SITE DA MESMA ORGANIZACAO ──────────
    # So para YouTube, so quando o nome nao decidiu, e so com LIGACAO OFICIAL
    # escrita na ficha (o site linka o canal) + SOURCE_ID e territorio do site
    # na casa. Conflito ou falta de prova continuam NAO SEI. Nome ou logotipo
    # nao contam: nada aqui compara nomes (`rota_do_scrap_youtube.heranca_do_site`).
    heranca = None
    if territorio == "NAO SEI" and familia in ("YOUTUBE", "LINKEDIN"):
        herdado, prova_d21 = RSY.heranca_do_site(ficha)
        if herdado:
            territorio, heranca = herdado, prova_d21
            porque = ("D21: o canal herda %s do site %s (%s; fontes do site: %s)"
                      % (herdado, prova_d21["HOST"], prova_d21["LIGACAO"],
                         ", ".join(prova_d21["SOURCE_IDS_DO_SITE"][:5])))

    # O nome nao decidiu: ha decisao semantica (Opus/humano) COM PROVA no canal?
    # So entra aqui — nunca por cima de um territorio que a regra ja decidiu.
    decisao, porque_ds = (None, "")
    if territorio == "NAO SEI":
        decisao, porque_ds = DS.decisao_para(cand_id, ficha)
        # ⚠️ UMA FONTE DE FORA DE IT NAO RECEBE NUMERO ITALIANO. D80(ii) (26/09,
        # dono via bot Luciano): territorio e identidade provados no canal ->
        # prefixo canonico do Atlas (EU-, INT-, FR-...), max+1 por prefixo e
        # territorio, nunca recicla. E PARA AI: a estrada de coleta e italiana —
        # `validar_contratos` so aceita IT-T<n>-<nnn> e o coletor
        # (`regras/italy_contracts.mjs`) rebenta com outro prefixo na tabela.
        # Sem contrato, sem canario, nunca READY automatico: CAPABILITY_BLOCK.
        if decisao and decisao.get("PAIS") != "IT":
            return _qualificar_fora_de_it(cand_id, ficha, familia, decisao)
        if decisao:
            territorio = decisao["TERRITORIO"]
            porque = "decisao semantica de %s: %s · provas: %s" % (
                decisao["DECIDIDO_POR"], (decisao.get("PORQUE") or "")[:200],
                "; ".join("%s %s sha256=%s" % (p.get("PAPEL"), p.get("URL"),
                                               (p.get("SHA256") or "")[:16])
                          for p in decisao.get("PROVAS", [])))

    # D80(iii): a PAGINA herda a classe do MESMO site canonico — so com classe
    # unica, host exacto, e nunca a raiz do site (`RSY.heranca_da_pagina`). A
    # decisao com prova, quando existe, ja decidiu acima e vale primeiro.
    duvida = DS.duvida_de_identidade(cand_id) if territorio == "NAO SEI" else None
    if duvida:
        porque_ds = "%s · D80(iii): nao herda — NAO SEI registado por duvida de identidade (%s)" % (
            porque_ds, duvida)
    elif territorio == "NAO SEI" and familia == "HTML_SITE":
        herdado, prova_d80 = RSY.heranca_da_pagina(ficha)
        if herdado:
            territorio, heranca = herdado, prova_d80
            porque = ("D80(iii): a pagina herda %s do site %s (%s; fontes do site: %s)"
                      % (herdado, prova_d80["HOST"], prova_d80["LIGACAO"],
                         ", ".join(prova_d80["SOURCE_IDS_DO_SITE"][:5])))
        else:
            porque_ds = ("%s · %s" % (porque_ds, prova_d80.get("PORQUE", ""))).strip(" ·")

    # ⚠️ SEM SINAL, SEM NUMERO — E SEM FABRICAR. Territorio indeterminado pelo
    # nome/URL e identidade que so raciocinio semantico (Opus/humano) resolve.
    # Um numero inventado poe a fonte na gaveta errada e da ar de trabalho feito.
    if territorio == "NAO SEI":
        return "BLOCK", {"CLASSE": "SEMANTIC",
                         "PORQUE": ("territorio indeterminado pelo nome (%s) — SOURCE_ID "
                                    "fica UNKNOWN, sem fabricar; precisa de decisao "
                                    "semantica (Opus/humano) ou caracterizacao · %s"
                                    % (ficha.get("NOME", "")[:50], porque_ds))}

    # HTML: pedir/alocar o SOURCE_ID canonico e passar ao degrau do contrato.
    sid_real, novo = _alocar_source_id(cand_id, territorio, familia, ficha, porque,
                                       native=canal, mesma_organizacao=heranca,
                                       native_kind=(RSS.LI_KIND if familia == "LINKEDIN"
                                                    else "YOUTUBE_CHANNEL_ID"))

    if LC.estado_de(sid_real) != LC.CONTRACT_PENDING:
        LC.registar(sid_real, LC.CONTRACT_PENDING,
                    "QUALIFY: %s -> %s (%s); identidade canonica alocada, falta contrato"
                    % (cand_id, sid_real, territorio),
                    evidence_ref=None)
    F.enfileirar(sid_real, F.BUILD_CONTRACT, priority=45,
                 motivo="QUALIFY alocou %s a partir de %s; construir contrato"
                        % (sid_real, cand_id))

    return "OK", {"SOURCE_ID_REAL": sid_real, "TERRITORY": territorio,
                  "FAMILY": familia, "PAIS": pais, "TIPO": tipo,
                  "CHANNEL_ID": canal, "HERANCA_D21": heranca,
                  "SOURCE_ID_NOVO": novo,
                  "TERRITORY_REASON": porque,
                  "DECISAO_SEMANTICA": decisao,
                  "PORQUE": "qualificada: %s -> %s (%s)"
                            % (cand_id, sid_real, territorio)}


def _contrato_do_molde(source_id: str) -> dict | None:
    """O contrato do molde da missao 04 para uma fonte com identidade e sem
    contrato na tabela — o ponto de partida do reparo, nunca gravado assim."""
    import escrever_contratos as EC
    n = next((x for x in _ler_alloc().get("NOVAS", []) if x.get("SOURCE_ID") == source_id), None)
    if not n or not n.get("URL") or n.get("FAMILY") == "YOUTUBE":
        return None
    car = RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json"
    f = {}
    if car.exists():
        f = next((x for x in json.loads(car.read_text(encoding="utf-8"))["FONTES"]
                  if x.get("CANDIDATE_ID") == n.get("CANDIDATE_ID")), {})
    c = EC.contrato_html(n, f)
    c["SOURCE_CONTRACT_VERSION"] = EC.VERSAO
    c["ONBOARDED_BY"] = ("SOURCE-CURATOR-WORKER · contrato escrito pelo reparo (REPAIR_CONTRACT) "
                         "a partir do molde da missao 04")
    return c


def etapa_repair_contract(source_id: str, contrato: dict | None) -> tuple[str, dict]:
    """REPARO-FONTES-V1: le a entrada, infere o padrao pelo metodo da casa e
    escreve o contrato novo pela porta do reparo (`reparar_contrato.aplicar`).

    OK   -> contrato reescrito; o worker poe CANARY_PENDING e VALIDATE_ROUTE
    FAIL -> REPARO_RECUSADO com o motivo (institucional, noticia, duplicada...)
    RETRY/BLOCK -> como no resto do worker. NUNCA promove READY.
    """
    import reparar_contrato as RC
    base = contrato or _contrato_do_molde(source_id)
    if not base:
        return "FAIL", {"PORQUE": "REPARO_RECUSADO: SEM_IDENTIDADE — sem contrato e sem "
                                  "alocacao HTML com endereco para partir"}
    if LC.estado_de(source_id) != LC.REPAIRING:
        LC.registar(source_id, LC.REPAIRING,
                    "reparo do contrato: ler a entrada e inferir o padrao dos itens (%s)" % RC.METODO,
                    evidence_ref=None)
    livro = json.loads(CONTRATOS.read_text(encoding="utf-8"))
    estados = LC.snapshot()
    # os documentos que ja tem dono: fontes READY e as ja reparadas
    outros = {c["SOURCE_ID"]: c for c in livro["FONTES"]
              if c["SOURCE_ID"] != source_id
              and (estados.get(c["SOURCE_ID"]) == LC.READY_FOR_COLLECTION
                   or c.get("REPARO_DE_CONTRATO"))}
    p = RC.inferir(base, outros=outros)
    resumo = {k: p.get(k) for k in ("DESFECHO", "MOTIVO", "CLASSE", "INDEX_URL", "LINK_PATTERN",
                                   "COMO", "ALVOS_NA_LISTAGEM", "ITEM_LIDO", "ENTRADA",
                                   "ENTRADA_RETRATO", "SECCAO_TENTADA", "FAMILIAS_VISTAS",
                                   "TENTADOS", "PEDIDOS", "PAGINAS_LIDAS", "METODO")
              if p.get(k) is not None}
    if p["DESFECHO"] == "RETRY":
        return "RETRY", dict(resumo, PORQUE=p["PORQUE"])
    if p["DESFECHO"] == "BLOCK":
        return "BLOCK", dict(resumo, CLASSE=p.get("CLASSE", "UNKNOWN"), PORQUE=p["PORQUE"])
    if p["DESFECHO"] != "PADRAO_NOVO":
        return "FAIL", dict(resumo, PORQUE="REPARO_RECUSADO: %s — %s"
                            % (p.get("MOTIVO"), p.get("PORQUE", "")))
    try:
        novo = RC.aplicar(base, p)
    except RC.ReparoInvalido as e:
        return "FAIL", dict(resumo, PORQUE="REPARO_RECUSADO: PORTA — %s" % e)
    livro = json.loads(CONTRATOS.read_text(encoding="utf-8"))
    for i, c in enumerate(livro["FONTES"]):
        if c["SOURCE_ID"] == source_id:
            livro["FONTES"][i] = novo
            break
    else:
        livro["FONTES"].append(novo)
    CONTRATOS.write_text(json.dumps(livro, ensure_ascii=False, indent=1), encoding="utf-8")
    return "OK", dict(resumo, CONTRATO=source_id, PORQUE="contrato reparado: %s" % p["PORQUE"])


ETAPAS = {
    F.REPAIR_CONTRACT: etapa_repair_contract,
    F.QUALIFY: etapa_qualify,
    F.VALIDATE_ROUTE: etapa_validate_route,
    F.CANARY: etapa_canary,
    F.REVALIDATE: etapa_canary,
    F.REPAIR: etapa_canary,
    F.BUILD_CONTRACT: etapa_build_contract,
}


def executar_uma(tarefa: dict, contratos: dict) -> dict:
    """UMA etapa. Devolve o desfecho, ja persistido na fila e no livro."""
    sid, tipo, tid = tarefa["SOURCE_ID"], tarefa["TASK_TYPE"], tarefa["TASK_ID"]
    contrato = contratos.get(sid)

    # ⚠️ O GUARD DE «SEM CONTRATO» SO SE APLICA A QUEM OPERA SOBRE UM CONTRATO.
    # QUALIFY e BUILD_CONTRACT correm SEM contrato por desenho — QUALIFY porque
    # a candidata ainda nem tem SOURCE_ID, BUILD_CONTRACT porque e o que ela
    # existe para produzir. Barra-las aqui era o defeito que punha as 72 QUALIFY
    # em BLOCK. Nao se fabrica contrato vazio: corrige-se a condicao.
    if not contrato and tipo not in SEM_CONTRATO_POR_DESENHO:
        F.bloquear(tid, "sem contrato nesta arvore")
        return {"TASK_ID": tid, "SOURCE_ID": sid, "TASK_TYPE": tipo,
                "RESULTADO": "BLOCK", "EVIDENCE_REF": "",
                "PORQUE": "sem contrato"}

    fn = ETAPAS.get(tipo)
    if not fn:
        F.bloquear(tid, "etapa nao implementada neste worker: %s" % tipo)
        return {"TASK_ID": tid, "SOURCE_ID": sid, "RESULTADO": "BLOCK",
                "PORQUE": "etapa %s sem executor" % tipo}

    # ⚠️ UMA FONTE QUE REBENTA NAO MATA A VOLTA.
    #
    # Medido (PROVAS-P1, DEFEITO 3): sem este try, uma excecao numa etapa
    # subia ate ao ciclo e matava a volta inteira — a tarefa venenosa ficava
    # IN_PROGRESS, as seguintes ficavam PENDING sem ninguem lhes tocar, o
    # RUN-LOG (escrito so no fim da volta) nao recebia batimento, e o
    # supervisor lia a morte como «sem progresso»: tres fontes venenosas em
    # 120 s mandavam o SERVICO a BLOCKED por culpa das FONTES. E a recuperacao
    # de orfas repunha a venenosa em PENDING de 30 em 30 min sem tocar em
    # ATTEMPTS — um loop lento que nunca chegava a FAILED.
    #
    # Aqui a excecao vira o RETRY da casa: F.adiar incrementa ATTEMPTS, marca
    # o relogio, e ao teto (MAX_ATTEMPTS) fecha em FAILED. A volta segue para
    # a tarefa seguinte, escreve o batimento no fim, e o supervisor ve
    # progresso — porque houve.
    #
    #     FONTE FALHOU != SERVICO MORREU.
    #
    # BLOCK (POLICY/AUTH/ROBOTS) nao passa por aqui: e um RESULTADO devolvido
    # pela etapa, nao uma excecao, e continua a nao ganhar tentativas novas.
    fonte_rebentou = False
    try:
        resultado, detalhe = fn(sid, contrato)
    except Exception as e:  # noqa: BLE001 — qualquer excecao de UMA fonte
        fonte_rebentou = True
        resultado = "RETRY"
        detalhe = {"PORQUE": "excecao na etapa %s: %s: %s"
                             % (tipo, type(e).__name__, str(e)[:120]),
                   "EXCECAO": type(e).__name__,
                   "FONTE_FALHOU": True}
    ref = _guardar_evidencia(sid, tipo, detalhe)

    if resultado == "OK":
        F.concluir(tid, "%s OK" % tipo)
        if tipo == F.BUILD_CONTRACT:
            # O contrato e uma HIPOTESE de rota. Quem a confirma e o canario,
            # e por isso esta etapa nunca chega perto de READY.
            if LC.estado_de(sid) != LC.CANARY_PENDING:
                LC.registar(sid, LC.CANARY_PENDING,
                            "contrato escrito e validado; falta provar a rota",
                            evidence_ref=ref)
            F.enfileirar(sid, F.VALIDATE_ROUTE, priority=55,
                         motivo="contrato novo — validar rota e canariar")
        elif tipo == F.REPAIR_CONTRACT:
            # Contrato novo = hipotese nova. Quem a julga e o circuito normal:
            # VALIDATE_ROUTE -> CANARY -> regua dos quatro passos.
            LC.registar(sid, LC.CANARY_PENDING,
                        ("contrato reparado (%s); falta provar a rota"
                         % detalhe.get("COMO", "?"))[:200], evidence_ref=ref)
            F.enfileirar(sid, F.VALIDATE_ROUTE, priority=55,
                         motivo="contrato reparado — validar rota e canariar")
        elif tipo == F.VALIDATE_ROUTE:
            do_scrap = (contrato or {}).get("ACQUISITION", {}).get("STRATEGY") == RSY.STRATEGY
            if LC.estado_de(sid) != LC.CANARY_PENDING:
                LC.registar(sid, LC.CANARY_PENDING,
                            ("rota do Scrap permitida pela matriz dele; o canario e "
                             "uma colheita do Scrap" if do_scrap else
                             "rota permitida pelo portao do anfitriao"),
                            evidence_ref=ref)
            # A rota do Scrap para aqui: o canario dela nao e do Curator.
            if not do_scrap:
                F.enfileirar(sid, F.CANARY, priority=60,
                             motivo="rota validada, falta o canario")
        elif tipo == F.QUALIFY:
            # ⚠️ QUALIFY NAO PROMOVE. A alocacao de identidade, o lifecycle
            # (CONTRACT_PENDING) e o enfileiramento do BUILD_CONTRACT ja
            # aconteceram DENTRO da etapa, sob o SOURCE_ID real — nunca sob o
            # CANDIDATA_ID. Aqui so se fecha a tarefa de qualificacao. Deixar
            # QUALIFY cair no ramo de baixo promoveria READY sem canario.
            pass
        else:
            # PROMOCAO. So daqui, e so com a prova do canario em mao.
            #
            # ⚠️ A RAZAO DIZ POR QUE REGUA A FONTE PASSOU. Desde a integracao
            # do gate de detalhe (AQUISICAO-DETALHE-V1), o canario HTML abre
            # um item e retrata-o; `DETAIL_GATE_PASSED` so existe nesse caso.
            # As 18 promovidas antes disto nao tem a chave na evidencia — e
            # essa ausencia e o que as distingue como READY_LEGACY. Nao se
            # reescreve o passado: a regua fica escrita na linha do livro.
            if detalhe.get("DETAIL_GATE_PASSED") is True:
                razao = ("canario resolveu, abriu um item real e passou o gate "
                         "de detalhe (%s)" % detalhe.get("DETAIL_GATE", "?"))
            else:
                razao = "canario resolveu e trouxe um item com identidade"
            # ⚠️ READY SO SE PROMOVE A PARTIR DE CANARY_PENDING OU REPAIRING —
            # e o livro recusa o resto com ValueError. Um REVALIDATE que
            # passa vem de CONTRACTED_CANARY_FAILED; um remedir vem de READY.
            # Medido: 0 das 18 REVALIDATE tinham passado, e por isso este
            # caminho nunca rebentou. Rebentaria no primeiro sucesso — e o
            # supervisor leria «worker morto sem progresso». A fonte passa
            # por CANARY_PENDING primeiro, com a razao escrita, e o livro fica
            # legal e legivel.
            #
            # ⚠️ UM SO CANARIO PROMOVE (UNIFICACAO-V1, 23/09/2026). Havia dois:
            # o do worker («o canario resolveu») promovia READY_FOR_COLLECTION,
            # e a regua dos quatro passos (ready_split.passos_da_promocao:
            # INDEX_URL -> DETAIL_LINKS -> ITEM ABERTO -> BODY UTIL + contrato
            # atual) decidia depois, na ponte e no portao, se esse READY valia.
            # Medido no livro unificado: 111 READY, das quais 88 a regua chama
            # LEGACY — READY que o portao nunca deixa colher. Agora a regua e o
            # juiz na hora da promocao; o canario do worker so traz a prova.
            # O que resolve mas nao passa nos quatro passos e PASS_PARCIAL:
            # CONTRACTED_CANARY_FAILED com o passo em falta escrito, e o
            # REVALIDATE do alimentador volta a mede-la. O passado nao se
            # reescreve (append-only): as READY antigas continuam no livro,
            # classificadas LEGACY pela mesma regua.
            regua = RS.passos_da_promocao(
                {"OBSERVED_AT": LC.agora(), "EVIDENCE_REF": ref},
                {"DADOS": detalhe}, contrato)
            if regua["REGUA"] not in RS.REGUAS_QUE_ADMITEM:   # a lista unica (DETAIL/v1 · PAGINA_BOLETIM/v1;
                # SOCIAL/v1 nunca nasce aqui: o canario do Scrap nao e do worker, e a regua so a da com o
                # veredito READY de curadoria/regua_social.py para a fase do contrato)
                if LC.estado_de(sid) != LC.CONTRACTED_CANARY_FAILED:
                    LC.registar(sid, LC.CONTRACTED_CANARY_FAILED,
                                ("canario resolveu, mas a regua dos quatro passos nao "
                                 "promove: %s" % regua["PORQUE"])[:200],
                                evidence_ref=ref)
                return {"TASK_ID": tid, "SOURCE_ID": sid, "TASK_TYPE": tipo,
                        "RESULTADO": "PASS_PARCIAL", "EVIDENCE_REF": ref,
                        "FONTE_FALHOU": False, "PORQUE": regua["PORQUE"][:160]}
            # ⚠️ A REGUA NAO LE. A revisao da R1 (curadoria/revisao_ready.py) retem
            # o que a leitura achou pagina fixa, texto de terceiros ou listagem, e
            # o que o reparo trouxe e ninguem leu. O motivo vai para o livro.
            rev = REV.decisao(sid, contrato)
            if rev and rev["ACAO"] == "RETER":
                if LC.estado_de(sid) != rev["ESTADO"]:
                    LC.registar(sid, rev["ESTADO"], rev["RAZAO"], evidence_ref=ref)
                return {"TASK_ID": tid, "SOURCE_ID": sid, "TASK_TYPE": tipo,
                        "RESULTADO": "PASS_RETIDO_PELA_REVISAO", "EVIDENCE_REF": ref,
                        "FONTE_FALHOU": False, "PORQUE": rev["RAZAO"][:160]}
            if rev and rev["ACAO"] == "PROMOVER_COM_NOTA":
                razao = ("%s · %s" % (razao, rev["NOTA"]))[:200]
            de = LC.estado_de(sid)
            if de not in LC.PODEM_PROMOVER:
                LC.registar(sid, LC.CANARY_PENDING,
                            "canario resolveu vindo de %s; passa por CANARY_PENDING "
                            "para a promocao ser legal no livro" % de,
                            evidence_ref=ref)
            LC.registar(sid, LC.READY_FOR_COLLECTION, razao, evidence_ref=ref)

    elif resultado == "RETRY":
        espera = detalhe.get("RETRY_AFTER_S")
        F.adiar(tid, retry_after_s=espera, erro=detalhe.get("PORQUE", "")[:160])
        if LC.estado_de(sid) not in (LC.RETRY_AFTER, LC.READY_FOR_COLLECTION):
            LC.registar(sid, LC.RETRY_AFTER,
                        "adiada: %s" % detalhe.get("PORQUE", "")[:120],
                        evidence_ref=ref)

    elif resultado == "BLOCK":
        classe = detalhe.get("CLASSE", "UNKNOWN")
        F.bloquear(tid, detalhe.get("PORQUE", classe)[:160])
        novo = {"ROBOTS": LC.CONTRACT_READY_ROUTE_BLOCKED,
                "AUTH": LC.AUTH_BLOCK,
                "POLICY": LC.POLICY_BLOCK,
                "SEMANTIC": LC.SEMANTIC_REVIEW}.get(classe, LC.CAPABILITY_BLOCK)
        if LC.estado_de(sid) != novo:
            LC.registar(sid, novo, detalhe.get("PORQUE", "")[:200], evidence_ref=ref)

    else:  # FAIL
        F.concluir(tid, "canario reprovou")
        if LC.estado_de(sid) != LC.CONTRACTED_CANARY_FAILED:
            LC.registar(sid, LC.CONTRACTED_CANARY_FAILED,
                        detalhe.get("PORQUE", "")[:200], evidence_ref=ref)

    return {"TASK_ID": tid, "SOURCE_ID": sid, "TASK_TYPE": tipo,
            "RESULTADO": resultado, "EVIDENCE_REF": ref,
            "FONTE_FALHOU": fonte_rebentou,
            "PORQUE": detalhe.get("PORQUE", "")[:160]}


PULSO = RAIZ / "curadoria" / "WORKER-HEARTBEAT.json"


def _pulso(r: dict) -> None:
    """Sinal de vida do worker, por tarefa. Nunca levanta."""
    try:
        PULSO.write_text(json.dumps({
            "AT": datetime.now(timezone.utc).isoformat(), "PID": os.getpid(),
            "TASK_ID": r.get("TASK_ID"), "RESULTADO": r.get("RESULTADO")}),
            encoding="utf-8")
    except Exception:
        pass


# ⚠️ PULSO DURANTE A TAREFA, COM TETO. O pulso por tarefa nao cobre UMA
# tarefa longa (rede lenta, canario grande): passados HEARTBEAT_TIMEOUT_S sem
# pulso o supervisor da-o como morto — e agora termina-o, a meio. Um fio de
# fundo pulsa enquanto ha tarefa em curso. Mas um fio que pulsa SEMPRE
# esconderia um worker realmente encravado; por isso so pulsa ate
# TAREFA_MAX_S. Encravado passa a ser detectado em TAREFA_MAX_S + 300 s.
PULSO_INTERVALO_S = 30
TAREFA_MAX_S = 900
_EM_CURSO: dict = {}


def _pulsar_em_fundo() -> None:
    while True:
        time.sleep(PULSO_INTERVALO_S)
        t = dict(_EM_CURSO)
        if t and time.time() - t["DESDE"] < TAREFA_MAX_S:
            _pulso({"TASK_ID": t["TASK_ID"], "RESULTADO": "EM_CURSO"})


_FIO_ARRANCADO: list = []


def _arrancar_fio_de_pulso() -> None:
    """Um fio por processo, arrancado na primeira tarefa."""
    import threading
    threading.Thread(target=_pulsar_em_fundo, daemon=True,
                     name="pulso-do-worker").start()
    _FIO_ARRANCADO.append(1)


def correr(max_tarefas: int = 0, pausa: float = 0.8, verboso: bool = True) -> list[dict]:
    """O LOOP. Para quando a fila nao tem nada ELEGIVEL — o que nao e o mesmo
    que a fila estar vazia: pode haver tarefas a espera do relogio delas, e
    esperar por elas aqui seria exatamente o bloqueio que a FASE 4 proibe.
    """
    contratos = _contratos()
    feitos = []
    F.recuperar_orfas()
    while True:
        if max_tarefas and len(feitos) >= max_tarefas:
            break
        t = F.proxima()
        if t is None:
            break
        if not _FIO_ARRANCADO:
            _arrancar_fio_de_pulso()
        _EM_CURSO.update({"TASK_ID": t["TASK_ID"], "DESDE": time.time()})
        try:
            r = executar_uma(t, contratos)
        finally:
            _EM_CURSO.clear()
        # ⚠️ BUILD_CONTRACT acrescenta linhas a tabela. Um dicionario lido uma
        # vez no arranque nao ve o contrato que acabou de nascer, e o canario
        # seguinte diria «sem contrato» sobre a fonte que o Bot acabou de
        # contratar — um falso BLOCK produzido por cache, nao pela fonte.
        if r.get("TASK_TYPE") in (F.BUILD_CONTRACT, F.REPAIR_CONTRACT) and r["RESULTADO"] == "OK":
            contratos = _contratos()
        feitos.append(r)
        # ⚠️ PULSO POR TAREFA. O diario so recebe a VOLTA no fim de todas as
        # tarefas; uma volta com mais de HEARTBEAT_TIMEOUT_S de rede lia-se
        # como worker morto (medido: 37 das 50 «mortes» de RC vazio eram
        # workers ainda a escrever no livro). O pulso vai para um ficheiro
        # proprio, nao para o diario: uma linha por tarefa seria ruido.
        _pulso(r)
        if verboso:
            print("  %-12s %-10s %s  %s" % (r["SOURCE_ID"], r["RESULTADO"],
                                            r["TASK_TYPE"], r["PORQUE"][:70]),
                  flush=True)
        time.sleep(pausa)
    return feitos


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=0, help="0 = ate esgotar elegiveis")
    ap.add_argument("--pausa", type=float, default=0.8)
    a = ap.parse_args()

    print("WORKER DO SOURCE CURATOR — %s" % CONTRATO)
    print("fila antes: %s" % json.dumps(F.metricas(), ensure_ascii=False))
    feitos = correr(a.max, a.pausa)
    print("\nfila depois: %s" % json.dumps(F.metricas(), ensure_ascii=False))
    print("fontes:      %s" % json.dumps(
        {k: v for k, v in LC.metricas().items() if v}, ensure_ascii=False))
    print("executadas:  %d" % len(feitos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
