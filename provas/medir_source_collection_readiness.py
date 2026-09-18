#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOURCE COLLECTION READINESS V1 — o censo, medido das autoridades reais.

    py provas/medir_source_collection_readiness.py            # escreve o JSON e o MD
    py provas/medir_source_collection_readiness.py --conferir # so compara com o JSON gravado

A pergunta e uma so, por fonte: DAS FONTES JA CONHECIDAS DO ATLAS (IT + EU),
QUANTAS A CASA CONSEGUE TRANSFORMAR EM SOURCE_COLLECTION_READY — e por que nao.

CINCO UNIVERSOS, NENHUM SE INFERE DO OUTRO (ADDENDUM-01):

    DECLARED_CONTRACT            a coluna «a maquina busca?» do indice gerado
                                 (le SO docs/operacao/CONTRATOS-DAS-FONTES-EAME.md)
    CAPABILITY / WIRING          o coletor sabe percorrer E a receita despacha
    FLOW_OBSERVED                uma corrida real deixou observacao HEALTHY com bytes
    TECHNICALLY_COLLECTION_READY o §16 da missao, medido
    BIG_COLLECTION_EXECUTABLE    READY x RELEVANCIA SIM x policy x custo

O indice NAO e owner do readiness — medido: das 6 fontes da primeira Big
Collection, o indice marca «sim» em 1. Este censo le codigo, runtime e
evidencia, e escreve o rotulo do indice AO LADO, nunca no lugar.

QUATRO CONTADORES, QUATRO OWNERS, NENHUM ACERTADO PARA BATER:

    ATLAS_FICHAS         210  fichas com SOURCE_ID    system-map/scripts/scan_sources.py (gerado)
    ATLAS_HEADER_STAMP   190  carimbo do cabecalho    docs/fontes/ATLAS-DE-FONTES-EAME.md (a mao)
    ESCADA_REGISTADA     173  degrau REGISTADA        scan_sources.py (fichas com exemplo real)
    CONTRATOS_DECLARADOS   5  «a maquina busca?»      CONTRATOS-DAS-FONTES-EAME.md via scan_sources.py

Nada aqui e adivinhado: cada valor traz o ficheiro de onde veio. O que nao
se mediu sai «NAO SEI», e um NAO SEI conta-se, nao se esconde.
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

from receitas import EXECUTORES  # noqa: E402

SAIDA_JSON = RAIZ / "data" / "derivados" / "SOURCE-COLLECTION-READINESS-V1.json"
SAIDA_MD = RAIZ / "docs" / "operacao" / "SOURCE-COLLECTION-READINESS-CENSO-V1.md"

FONTES_GERADAS = RAIZ / "system-map" / "data" / "sources.generated.json"
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
INDICE = RAIZ / "docs" / "fontes" / "INDICE-DE-FONTES.md"
MANIFESTOS = RAIZ / "data" / "samples" / "IT-SOURCE-SAMPLES"
RELEVANCIA = RAIZ / "data" / "samples" / "LIVRO-DE-RELEVANCIA-DE-FONTE.json"
OBSERVACOES = RAIZ / "data" / "collection-ledger" / "italy" / "observations.ndjson"
CORRIDAS = RAIZ / "data" / "collection-ledger" / "italy" / "runs.ndjson"
MANIFESTO_DE_CORRIDAS = RAIZ / "data" / "samples" / "RUN-MANIFEST.json"
COLETOR = RAIZ / "coleta" / "italy_pilot_collect.mjs"
TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"

MISSAO = "SOURCE-COLLECTION-READINESS-V1"
#: A primeira corrida desta missao. O que esta ANTES e o «antes»; o resto e «depois».
INICIO_DA_MISSAO = "2026-09-18T18:00:00Z"

#: O que a casa sabia percorrer ANTES desta missao — declarado, nao inferido.
#: Os sete do piloto (IT-T3-005 e candidata, fora do Atlas) e o ato UE por CELEX.
CAPACIDADE_ANTES = {"IT-T3-005", "IT-T2-002", "IT-T2-004", "IT-T3-002", "IT-T3-010",
                    "IT-T3-008", "IT-T4-001", "EU-T4-001"}

#: As seis da primeira Big Collection (commit d915f85a) — a contraprova do ADDENDUM-01.
AS_SEIS_DA_BIG_COLLECTION = ["IT-T2-002", "IT-T2-004", "IT-T3-002", "IT-T3-008", "IT-T3-010", "IT-T4-001"]

#: Vocabulario fechado dos blockers (§18 da missao). UNKNOWN permanece UNKNOWN.
BLOCKERS = ("RELEVANCE_PENDING", "SOURCE_ID_MISSING", "URL_DEAD", "ROUTE_UNKNOWN",
            "CAPABILITY_MISSING", "NOT_WIRED", "POLICY_BLOCKED", "AUTH_REQUIRED",
            "PAID_BLOCKED", "BROWSER_REQUIRED", "SOURCE_CHANGED", "RATE_LIMITED",
            "CANARY_FAILED", "SCRAP_CAPABILITY_GAP", "UNKNOWN")

#: Formas de aquisicao (§4). Baseadas no caminho REAL, nao no tema.
SHAPES = ("PDF_DISCOVERY_PAGE", "HTML_ARTICLE_DISCOVERY", "PDF_DIRECT", "HTML_STATIC",
          "CSV_DATASET", "JSON_API", "OFFICIAL_API", "BROWSER_PUBLIC", "SOCIAL_PUBLIC",
          "DATASET_ODS", "ROUTE_UNKNOWN")

# ── As formas das fontes que NAO estao na tabela declarativa — declaradas com a prova ──
FORMA_DECLARADA = {
    # os sete do piloto: um `case` por fonte em coleta/italy_pilot_collect.mjs
    "IT-T2-002": ("PDF_DIRECT", "coleta/italy_pilot_collect.mjs::alvosDe — 29 PDFs de zona em URL fixa (contrato IT-T2-002)"),
    "IT-T2-004": ("HTML_STATIC", "coleta/italy_pilot_collect.mjs::alvosDe — pagina HTML fixa (contrato IT-T2-004)"),
    "IT-T3-002": ("PDF_DISCOVERY_PAGE", "coleta/italy_pilot_collect.mjs::alvosDe — indice do ano -> PDF (contrato IT-T3-002)"),
    "IT-T3-008": ("PDF_DISCOVERY_PAGE", "coleta/italy_pilot_collect.mjs::alvosDe — /bollettini -> PDF, com rota previsivel de reserva (contrato IT-T3-008)"),
    "IT-T3-010": ("PDF_DISCOVERY_PAGE", "coleta/italy_pilot_collect.mjs::alvosDe — home -> PDF (contrato IT-T3-010)"),
    "IT-T4-001": ("CSV_DATASET", "coleta/italy_pilot_collect.mjs::alvosDe — pagina do dataset -> CSV datado (contrato IT-T4-001)"),
    # contrato a mao, sem coletor
    "IT-T7-002": ("DATASET_ODS", "regras/italy_contracts.mjs IT-T7-002 — ODS (ZIP) descoberto; forma nao coberta pelo coletor generico"),
    "IT-T9-002": ("BROWSER_PUBLIC", "regras/italy_contracts.mjs / manifesto — servidor recusa cliente sem navegador (403)"),
    "IT-T9-008": ("BROWSER_PUBLIC", "regras/italy_contracts.mjs IT-T9-008 — BROWSER_DISCOVERED_ROUTE, WAF_OBSERVED"),
    # ficha sem endereco
    "IT-T3-001": ("ROUTE_UNKNOWN", "ficha do Atlas sem URL — cobertura parcial declarada (Emilia-Romagna)"),
    "IT-T11-001": ("ROUTE_UNKNOWN", "ficha do Atlas sem URL"),
    "IT-T9-001": ("ROUTE_UNKNOWN", "ficha agrupada FR/ES/IT-T9-001 sem URL propria"),
    # sondadas e sem documento descoberto pela regra generica
    "IT-T5-003": ("PDF_DISCOVERY_PAGE", "manifesto: PDF observado em aipp.it; a sonda de 2026-09-18 nao achou link PDF na entrada — rota por escrever"),
    "IT-T5-031": ("ROUTE_UNKNOWN", "manifesto: exemplo TEXTO numa pasta de ficheiros; sem documento identificavel"),
    # Europa
    "EU-T1-001": ("JSON_API", "ficha: API REST JSON-stat 2.0 sem chave (Eurostat)"),
    "EU-T1-002": ("JSON_API", "ficha: API REST JSON-stat sem chave (Eurostat)"),
    "EU-T10-001": ("JSON_API", "ficha: REST JSON sem chave; coleta/agrifood_ue.py ja chama o endpoint"),
    "EU-T12-001": ("OFFICIAL_API", "ficha: SPARQL + content negotiation — a mesma infraestrutura de EU-T4-001"),
    "EU-T2-001": ("JSON_API", "ficha: API REST JSON sem chave (NASA POWER)"),
    "EU-T2-002": ("JSON_API", "ficha: GeoJSON direto sem chave (NUTS)"),
    "EU-T2-003": ("JSON_API", "ficha: API REST sem chave, com cota diaria por IP (Open-Meteo)"),
    "EU-T3-001": ("OFFICIAL_API", "ficha: API REST devolve 403 sem token EPPO"),
    "EU-T4-001": ("OFFICIAL_API", "coleta/eu_regulatorio_executor.py — EUR-Lex por CELEX (SPARQL + content negotiation)"),
    "EU-T4-002": ("BROWSER_PUBLIC", "ficha: aplicacao Angular (SPA) + API interna — observado, nao obtido"),
    "EU-T5-001": ("JSON_API", "ficha: REST JSON sem chave (OpenAlex); coleta/corpus_pesquisador.py ja chama o endpoint"),
    "EU-T8-001": ("ROUTE_UNKNOWN", "ficha sem URL (T8 FARMERS & INFLUENCERS)"),
    "EU-T9-002": ("BROWSER_PUBLIC", "ficha: Meta Ads Library — rota nao executada; so abre com janela grafica"),
}

# ── Capacidade/executor existentes para o que NAO passa pelo coletor italiano ──
CAPACIDADE_EU = {
    "EU-T4-001": ("coleta/eu_regulatorio_executor.py (regulatorio-eu, T4)", "regulatorio-eu", "T4"),
    "EU-T12-001": ("coleta/cellar.sh + coleta/eu_regulatorio_executor.py (SOURCE_ID fixo = EU-T4-001)", "", ""),
    "EU-T10-001": ("coleta/agrifood_ue.py (nao registado em pedido/receitas.py)", "", ""),
    "EU-T5-001": ("coleta/corpus_pesquisador.py (corpus-pesquisador, T6; retorno LEGADO/CATALOG)", "corpus-pesquisador", "T6"),
    "EU-T3-001": ("coleta/eppo_gd.py (eppo, T3; nunca correu; API exige token)", "eppo", "T3"),
}


def _json(p: Path):
    with io.open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _ndjson(p: Path) -> list:
    if not p.is_file():
        return []
    fora = []
    with io.open(p, encoding="utf-8") as fh:
        for linha in fh:
            linha = linha.strip()
            if not linha:
                continue
            try:
                fora.append(json.loads(linha))
            except json.JSONDecodeError:
                continue
    return fora


def contratos_e_capacidade() -> dict:
    """Pergunta ao node — o unico que le `.mjs` — sem copiar nada."""
    guiao = (
        "const c = await import(%s); const k = await import(%s);\n"
        "const fora = {};\n"
        "for (const [id, x] of Object.entries(c.CONTRACTS)) fora[id] = {ACQUISITION: x.ACQUISITION || null, "
        "CANONICAL_ENTRY_URL: String(x.CANONICAL_ENTRY_URL || ''), "
        "ROUTE_TYPE: x.ROUTE_TYPE, OUTPUT_TYPE: x.OUTPUT_TYPE, A_MAO: !x.ONBOARDED_BY || String(x.ONBOARDED_BY).includes('a mao'), "
        "ONBOARDED_BY: x.ONBOARDED_BY || null, DOCUMENT_ID_RULE: String(x.DOCUMENT_ID_RULE || ''), "
        "FAIL_CLOSED_RULE: String(x.FAIL_CLOSED_RULE || ''), NEGATIVE_CONTROL: !!x.NEGATIVE_CONTROL};\n"
        "process.stdout.write(JSON.stringify({CONTRACTS: fora, PILOT_SOURCES: k.PILOT_SOURCES, "
        "FONTES_GENERICAS: k.FONTES_GENERICAS, FONTES_PERCORRIVEIS: k.FONTES_PERCORRIVEIS}));\n"
        % (json.dumps((RAIZ / "regras" / "italy_contracts.mjs").resolve().as_uri()),
           json.dumps(COLETOR.resolve().as_uri()))
    )
    r = subprocess.run(["node", "--input-type=module", "-e", guiao], capture_output=True,
                       text=True, encoding="utf-8", errors="strict", cwd=str(RAIZ), timeout=120)
    if r.returncode != 0:
        raise RuntimeError("o node recusou os contratos: %s" % (r.stderr or "")[:500])
    return json.loads(r.stdout)


def fichas_do_atlas() -> dict:
    """Os SOURCE_IDs com ficha — pelo gerador canonico (scan_sources.py), nunca por regex."""
    S = _json(FONTES_GERADAS)
    return {f["source_id"]: f for f in S["SOURCES"]}


def indice_a_maquina_busca() -> dict:
    """A coluna «a maquina busca?» do indice gerado, tal e qual. NAO e readiness."""
    fora = {}
    if not INDICE.is_file():
        return fora
    with io.open(INDICE, encoding="utf-8") as fh:
        texto = fh.read()
    for m in re.finditer(r"^\| `([A-Z]{2}-T\d+-\d{3})` \| .*? \| (\S+) \|$", texto, re.M):
        fora[m.group(1)] = "sim" if m.group(2).strip() == "sim" else "nao"
    return fora


def os_quatro_contadores() -> dict:
    S = _json(FONTES_GERADAS)
    hc = S.get("HEADER_CLAIM") or {}
    escada = None
    if INDICE.is_file():
        with io.open(INDICE, encoding="utf-8") as fh:
            m = re.search(r"\| 2 \| \*\*REGISTADA\*\* \|.*?\| \*\*(\d+)\*\* \|", fh.read())
        escada = int(m.group(1)) if m else None
    return OrderedDict([
        ("ATLAS_FICHAS", {"VALOR": (S.get("COUNTS") or {}).get("sources"), "O_QUE_MEDE": "fichas do Atlas com campo SOURCE_ID valido (ficha multinacional conta por SOURCE_ID)",
                          "OWNER": "system-map/scripts/scan_sources.py -> system-map/data/sources.generated.json", "COMO": "gerado", "STALE": "NAO — regenerado pela cadeia do mapa"}),
        ("ATLAS_HEADER_STAMP", {"VALOR": hc.get("total"), "O_QUE_MEDE": "o numero que o cabecalho do Atlas declara (marcador SOURCE_ID_COUNT)",
                                "OWNER": "docs/fontes/ATLAS-DE-FONTES-EAME.md linha %s (a mao)" % hc.get("line"), "COMO": "carimbo escrito a mao", "STALE": "SIM — o proprio indice regista a divergencia (%s vs %s); decisao humana, nao correcao automatica" % (hc.get("total"), hc.get("fichas_completas"))}),
        ("ESCADA_REGISTADA", {"VALOR": escada, "O_QUE_MEDE": "fichas com exemplo real guardado (degrau 2 da escada)",
                              "OWNER": "system-map/scripts/scan_sources.py (escada) -> docs/fontes/INDICE-DE-FONTES.md", "COMO": "gerado", "STALE": "NAO SEI — o degrau le a ficha, nao a evidencia em disco; nao medido nesta missao"}),
        ("CONTRATOS_DECLARADOS", {"VALOR": (S.get("COUNTS") or {}).get("with_contract"), "O_QUE_MEDE": "fontes com bloco SOURCE_ID em docs/operacao/CONTRATOS-DAS-FONTES-EAME.md — e SO isso",
                                  "OWNER": "scan_sources.py::dos_contratos() le CONTRATOS-DAS-FONTES-EAME.md", "COMO": "gerado de um documento a mao", "STALE": "SIM como medida de readiness — nao le regras/italy_contracts.mjs nem o coletor; 1 das 6 fontes da Big Collection esta «sim»"}),
    ])


def relevancia() -> dict:
    L = _json(RELEVANCIA)
    fora = {}
    for d in L.get("DECISOES") or []:
        fora.setdefault(d["SOURCE_ID"], {})[d["PROPOSITO"]] = d["RESULTADO"]
    return fora


def observacoes_por_fonte() -> dict:
    fora = {}
    for o in _ndjson(OBSERVACOES):
        sid = o.get("SOURCE_ID")
        if not sid:
            continue
        f = fora.setdefault(sid, {"OBSERVACOES": 0, "HEALTHY_COM_BYTES": 0, "ULTIMA": None, "PRIMEIRA_HEALTHY": None})
        f["OBSERVACOES"] += 1
        if o.get("HEALTH_STATE") == "HEALTHY" and o.get("RAW_SHA256"):
            f["HEALTHY_COM_BYTES"] += 1
            if f["PRIMEIRA_HEALTHY"] is None or str(o.get("CAPTURED_AT")) < str(f["PRIMEIRA_HEALTHY"]):
                f["PRIMEIRA_HEALTHY"] = o.get("CAPTURED_AT")
        f["ULTIMA"] = {"RUN_ID": o.get("RUN_ID"), "CAPTURED_AT": o.get("CAPTURED_AT"), "HEALTH_STATE": o.get("HEALTH_STATE"),
                       "OBSERVATION_RESULT": o.get("OBSERVATION_RESULT"), "SOURCE_URL": o.get("SOURCE_URL"),
                       "MIME_ASSINATURA": o.get("MIME_ASSINATURA"), "BYTES": o.get("BYTES"), "motivo": o.get("motivo")}
    return fora


def canarios_do_manifesto() -> dict:
    """A ultima corrida de cada fonte pela porta canonica (orquestrador -> italy_executor)."""
    M = _json(MANIFESTO_DE_CORRIDAS)
    fora = {}
    for r in M.get("RUNS") or []:
        cmd = str(r.get("COMANDO") or "")
        m = re.match(r"coleta/italy_executor\.py ([A-Z]{2}-T\d+-\d{3}) ", cmd)
        sid = m.group(1) if m else None
        if not sid and "eu_regulatorio_executor" in cmd:
            sid = "EU-T4-001"
        if not sid:
            continue
        ing = r.get("INGRESSO") or {}
        obs = (ing.get("PARA_A_PORTA") or [{}])
        o0 = obs[0] if obs else {}
        fora[sid] = {
            "RUN_ID": r.get("RUN_ID"), "STARTED_AT": r.get("STARTED_AT"), "STATUS": r.get("STATUS"),
            "ACTOR": r.get("ACTOR"), "COMANDO": cmd, "COST_USD": r.get("COST_USD"),
            "PRESERVADOS": ing.get("PRESERVADOS"), "FONTE_PROVADA": ing.get("FONTE_PROVADA"),
            "RUN_STATE": ing.get("RUN_STATE"), "RASTRO": (ing.get("RASTRO") or {}).get("ESTADO"),
            "DIAGNOSTIC_CODE": (ing.get("RASTRO") or {}).get("DIAGNOSTIC_CODE"),
            "DERIVACAO": (r.get("DERIVACAO") or {}).get("ESTADO_DA_ETAPA") or (r.get("DERIVACAO") or {}).get("PORQUE"),
            "ADMISSAO": (r.get("ADMISSAO") or {}).get("por_resultado"),
            "PRONTOS": (r.get("ADMISSAO") or {}).get("prontos"),
            "PERSISTENCIA": (r.get("PERSISTENCIA") or {}).get("ESTADO"),
            "RETORNO_ESTADO": (r.get("RETORNO") or {}).get("ESTADO"),
            "ERROS": (r.get("RETORNO") or {}).get("ERROS") or [],
            "OBSERVACAO": {"HEALTH_STATE": o0.get("HEALTH_STATE"), "OBSERVATION_RESULT": o0.get("OBSERVATION_RESULT"),
                           "SOURCE_URL": o0.get("SOURCE_URL") or o0.get("url"), "MIME_ASSINATURA": o0.get("MIME_ASSINATURA"),
                           "CONTENT_TYPE": o0.get("CONTENT_TYPE"), "BYTES": o0.get("BYTES"), "DOCUMENT_ID": o0.get("DOCUMENT_ID"),
                           "source_id": o0.get("source_id"), "raw_asset_id": o0.get("raw_asset_id"), "motivo": o0.get("motivo")},
        }
    return fora


def medir() -> dict:
    fichas = fichas_do_atlas()
    universo = OrderedDict((sid, f) for sid, f in sorted(fichas.items()) if f.get("country") in ("ITALIA", "EUROPA"))
    K = contratos_e_capacidade()
    contratos, pilot = K["CONTRACTS"], set(K["PILOT_SOURCES"])
    percorriveis = set(K["FONTES_PERCORRIVEIS"])
    tabela = {r["SOURCE_ID"]: r for r in _json(TABELA)["FONTES"]}
    indice = indice_a_maquina_busca()
    rel = relevancia()
    obs = observacoes_por_fonte()
    canarios = canarios_do_manifesto()
    exec_por_alvo = {alvo: [e["id"] for e in lista] for alvo, lista in EXECUTORES.items()}

    linhas = []
    for sid, f in universo.items():
        c = contratos.get(sid) or {}
        aq = c.get("ACQUISITION")
        # O endereco vem da ficha; quando a ficha diz «NAO SEI» e o contrato a mao
        # sabe (IT-T3-010: http://www.apol.it), vale o do contrato — e diz-se.
        url = str(f.get("url") or "").strip()
        if not url.startswith("http") and str(c.get("CANONICAL_ENTRY_URL") or "").startswith("http"):
            url = c["CANONICAL_ENTRY_URL"] + "  (do contrato; a ficha diz NAO SEI)"
        tem_url = url.startswith("http")
        # ── forma de aquisicao ─────────────────────────────────────────────
        if sid in tabela:
            shape, prova_shape = tabela[sid]["SHAPE"], "regras/italy_contracts_onboarded.json (sondagem %s)" % (tabela[sid].get("SONDAGEM") or {}).get("SONDADO_EM")
        elif sid in FORMA_DECLARADA:
            shape, prova_shape = FORMA_DECLARADA[sid]
        elif sid.startswith("IT-T6-"):
            shape, prova_shape = "JSON_API", "manifesto: ORCID public API /works (JSON)"
        elif not tem_url:
            shape, prova_shape = "ROUTE_UNKNOWN", "ficha sem URL"
        else:
            shape, prova_shape = "ROUTE_UNKNOWN", "NAO SEI — nao classificada nesta missao"
        # ── capacidade / executor / receita / wiring ───────────────────────
        alvo = str(f.get("territory") or "")
        if sid in percorriveis:
            capacidade = "coleta/italy_pilot_collect.mjs (%s)" % ("case proprio" if sid in pilot else "forma generica ACQUISITION")
            executor, receita = "italia-recorrente (coleta/italy_executor.py)", alvo if "italia-recorrente" in exec_por_alvo.get(alvo, []) else ""
            wired = bool(receita)
        elif sid.startswith("IT-T6-"):
            capacidade, executor, receita = "coleta/corpus_pesquisador.py (ORCID/OpenAlex)", "corpus-pesquisador", "T6"
            wired = False  # retorno LEGADO/CATALOG: nao atravessa o ingresso
        elif sid in CAPACIDADE_EU:
            capacidade, executor, receita = CAPACIDADE_EU[sid]
            wired = sid == "EU-T4-001"
        else:
            capacidade, executor, receita, wired = "", "", "", False
        # ── policy / custo ─────────────────────────────────────────────────
        policy = "BROWSER_REQUIRED" if shape == "BROWSER_PUBLIC" else ("AUTH_REQUIRED" if sid == "EU-T3-001" else "ALLOWED")
        custo = "gratuito"
        # ── relevancia ────────────────────────────────────────────────────
        decisoes = rel.get(sid) or {}
        relev = decisoes.get(alvo) or (next(iter(decisoes.values())) if decisoes else "NAO_AVALIADA")
        # ── fluxo observado (ledger) e canario (manifesto de corridas) ─────
        o = obs.get(sid) or {}
        fluxo = "YES" if o.get("HEALTHY_COM_BYTES") else ("YES" if sid == "EU-T4-001" and canarios.get(sid, {}).get("STATUS") == "SUCCESS" else "NO")
        can = canarios.get(sid)
        if can:
            ok = (can["STATUS"] == "SUCCESS" and (can.get("PRESERVADOS") or 0) >= 1
                  and can.get("FONTE_PROVADA") == sid and can["OBSERVACAO"].get("HEALTH_STATE") == "HEALTHY")
            canary = "PASS" if ok else "FAIL"
        else:
            canary = "NOT_RUN"
        # ── a definicao do §16, criterio a criterio ────────────────────────
        criterios = OrderedDict([
            ("SOURCE_ID_CANONICO", True),
            ("ENDERECO_VALIDADO", tem_url and (canary == "PASS" or fluxo == "YES")),
            ("ROTA_EXISTE", shape not in ("ROUTE_UNKNOWN",)),
            ("CAPABILITY_EXISTE", bool(capacidade)),
            ("EXECUTOR_EXISTE", bool(executor)),
            ("WIRING_EXISTE", wired),
            ("PARAMETROS_CONTRATADOS", bool(aq) or sid in pilot or sid == "EU-T4-001"),
            ("RETORNO_TIPADO", bool(aq) or sid in pilot or sid == "EU-T4-001"),
            ("POLICY_NAO_BLOQUEIA", policy == "ALLOWED"),
            ("CANARIO_PROVOU", canary == "PASS" or (fluxo == "YES" and sid in CAPACIDADE_ANTES)),
            ("LINEAGE_NAO_FABRICA", (can or {}).get("FONTE_PROVADA") in (sid, None) and ((can or {}).get("OBSERVACAO") or {}).get("source_id") in (sid, None)),
        ])
        ready = all(criterios.values())
        # ── blocker, com nome, ou nenhum ──────────────────────────────────
        if ready:
            blocker, detalhe = "", ""
        elif not tem_url and shape == "ROUTE_UNKNOWN":
            blocker, detalhe = "ROUTE_UNKNOWN", "ficha sem URL"
        elif shape == "ROUTE_UNKNOWN":
            blocker, detalhe = "ROUTE_UNKNOWN", prova_shape
        elif policy == "BROWSER_REQUIRED":
            blocker, detalhe = "BROWSER_REQUIRED", prova_shape
        elif policy == "AUTH_REQUIRED":
            blocker, detalhe = "AUTH_REQUIRED", prova_shape
        elif not capacidade:
            blocker, detalhe = "CAPABILITY_MISSING", "nenhum coletor desta casa percorre a forma %s para esta fonte" % shape
        elif not wired:
            blocker, detalhe = "NOT_WIRED", ("o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao esta decidida"
                                             if sid.startswith("IT-T6-") else "capacidade existe, mas nenhuma receita despacha esta fonte")
        elif canary == "FAIL":
            erros = (can or {}).get("ERROS") or []
            motivo = str((erros[0].get("MOTIVO") if erros else "")
                         or (can or {}).get("OBSERVACAO", {}).get("motivo")
                         or (can or {}).get("DIAGNOSTIC_CODE") or "")
            blocker, detalhe = "CANARY_FAILED", motivo[:160] or "corrida sem observacao saudavel"
        elif canary == "NOT_RUN":
            blocker, detalhe = "UNKNOWN", "configurada e wired, canario nao correu"
        else:
            blocker, detalhe = "UNKNOWN", "; ".join(k for k, v in criterios.items() if not v)
        executavel = ready and relev == "SIM" and policy == "ALLOWED" and custo == "gratuito"
        linhas.append(OrderedDict([
            ("SOURCE_ID", sid), ("PROPOSITO", alvo), ("SOURCE_NAME", f.get("name")),
            ("SOURCE_TYPE", f.get("type") or "NAO SEI"), ("PRIMARY_URL", url or "NAO SEI"),
            ("ACCESS_SHAPE", shape), ("ACCESS_SHAPE_PROVA", prova_shape),
            ("RELEVANCE_STATE", relev),
            ("EXISTING_CAPABILITY", capacidade or "NENHUMA"), ("EXISTING_EXECUTOR", executor or "NENHUM"),
            ("EXISTING_RECIPE", receita or "NENHUMA"), ("COLLECTION_WIRED", "YES" if wired else "NO"),
            ("POLICY_STATE", policy), ("COST_CLASS", custo),
            ("CANARY_STATE", canary), ("CANARY", can),
            ("FLOW_OBSERVED", fluxo), ("FLOW_EVIDENCE", o or None),
            ("DECLARED_CONTRACT", "YES" if indice.get(sid) == "sim" else "NO"),
            ("INDEX_A_MAQUINA_BUSCA", indice.get(sid, "NAO SEI")),
            ("CRITERIOS_16", criterios),
            ("TECHNICALLY_COLLECTION_READY", "YES" if ready else "NO"),
            ("BIG_COLLECTION_EXECUTABLE", "YES" if executavel else "NO"),
            ("BLOCKER", blocker), ("BLOCKER_DETALHE", detalhe),
            ("ONBOARDED_NESTA_MISSAO", sid in tabela),
            ("CONTRATO", "a mao" if (c and c.get("A_MAO")) else ("tabela declarativa" if c else "nenhum")),
            # O documento que o canario ABRIU. READY diz que a estrada existe e foi
            # percorrida; NAO diz que este e o boletim certo — essa e a pergunta da
            # regra de descoberta por fonte (LINK_PATTERN), e fica a vista para quem decide.
            ("DOCUMENTO_OBSERVADO", ((can or {}).get("OBSERVACAO") or {}).get("SOURCE_URL") or "NAO SEI"),
            ("REGRA_DE_DESCOBERTA", (tabela.get(sid, {}).get("SONDAGEM") or {}).get("REGRA", "") if sid in tabela else ""),
        ]))

    # ── o antes e o depois — pela capacidade e pelo fluxo, nunca pelo indice ──
    antes = sorted(l["SOURCE_ID"] for l in linhas
                   if l["SOURCE_ID"] in CAPACIDADE_ANTES and l["FLOW_OBSERVED"] == "YES"
                   and (obs.get(l["SOURCE_ID"]) or {}).get("PRIMEIRA_HEALTHY", "9") < INICIO_DA_MISSAO)
    depois = sorted(l["SOURCE_ID"] for l in linhas if l["TECHNICALLY_COLLECTION_READY"] == "YES")
    novas = sorted(set(depois) - set(antes))
    por_shape = OrderedDict()
    for s in SHAPES:
        ls = [l for l in linhas if l["ACCESS_SHAPE"] == s]
        if not ls:
            continue
        por_shape[s] = OrderedDict([
            ("FONTES", len(ls)), ("READY", sum(1 for l in ls if l["TECHNICALLY_COLLECTION_READY"] == "YES")),
            ("BLOCKED", sum(1 for l in ls if l["BLOCKER"])),
            ("TOOL", sorted({l["EXISTING_CAPABILITY"] for l in ls if l["EXISTING_CAPABILITY"] != "NENHUMA"})),
            ("NEW_CODE", "coletor generico (forma lida do contrato) — SOURCE-COLLECTION-READINESS-V1" if s in ("PDF_DISCOVERY_PAGE", "HTML_ARTICLE_DISCOVERY", "PDF_DIRECT") and any(l["ONBOARDED_NESTA_MISSAO"] for l in ls) else "nenhum"),
            ("BLOCKERS", dict(Counter(l["BLOCKER"] for l in ls if l["BLOCKER"]))),
        ])
    contraprova = OrderedDict((sid, {"INDICE_A_MAQUINA_BUSCA": indice.get(sid), "FLOW_OBSERVED": (obs.get(sid) or {}).get("HEALTHY_COM_BYTES", 0) > 0,
                                     "OBSERVACOES_HEALTHY_COM_BYTES": (obs.get(sid) or {}).get("HEALTHY_COM_BYTES", 0)})
                              for sid in AS_SEIS_DA_BIG_COLLECTION)
    it = [l for l in linhas if l["SOURCE_ID"].startswith("IT-")]
    eu = [l for l in linhas if l["SOURCE_ID"].startswith("EU-")]
    resumo = OrderedDict([
        ("TOTAL_SOURCES", len(linhas)), ("IT_SOURCES", len(it)), ("EU_APPLICABLE", len(eu)),
        ("RELEVANCE_SIM", sum(1 for l in linhas if l["RELEVANCE_STATE"] == "SIM")),
        ("RELEVANCE_PENDING", sum(1 for l in linhas if l["RELEVANCE_STATE"] != "SIM")),
        ("DECLARED_CONTRACT", sum(1 for l in linhas if l["DECLARED_CONTRACT"] == "YES")),
        ("COLLECTION_WIRED", sum(1 for l in linhas if l["COLLECTION_WIRED"] == "YES")),
        ("FLOW_OBSERVED", sum(1 for l in linhas if l["FLOW_OBSERVED"] == "YES")),
        ("SOURCE_COLLECTION_READY_BEFORE", len(antes)), ("SOURCE_COLLECTION_READY_BEFORE_IDS", antes),
        ("SOURCE_COLLECTION_READY_AFTER", len(depois)),
        ("NEW_SOURCE_COLLECTION_READY", len(novas)), ("NEW_SOURCE_COLLECTION_READY_IDS", novas),
        ("STILL_NOT_READY", len(linhas) - len(depois)),
        ("BIG_COLLECTION_EXECUTABLE_BEFORE", sum(1 for l in linhas if l["SOURCE_ID"] in antes and l["RELEVANCE_STATE"] == "SIM")),
        ("BIG_COLLECTION_EXECUTABLE_AFTER", sum(1 for l in linhas if l["BIG_COLLECTION_EXECUTABLE"] == "YES")),
        ("SOURCES_CONFIGURED", sum(1 for l in linhas if l["ONBOARDED_NESTA_MISSAO"])),
        ("SOURCES_CANARY_PASS", sum(1 for l in linhas if l["ONBOARDED_NESTA_MISSAO"] and l["CANARY_STATE"] == "PASS")),
        ("SOURCES_CANARY_FAIL", sum(1 for l in linhas if l["ONBOARDED_NESTA_MISSAO"] and l["CANARY_STATE"] == "FAIL")),
        ("SOURCES_CANARY_NOT_RUN", sum(1 for l in linhas if l["ONBOARDED_NESTA_MISSAO"] and l["CANARY_STATE"] == "NOT_RUN")),
        ("BLOCKERS", OrderedDict(sorted(Counter(l["BLOCKER"] for l in linhas if l["BLOCKER"]).items(), key=lambda kv: -kv[1]))),
        ("INDEX_COLLECTION_READINESS_STALE", "YES" if sum(1 for v in contraprova.values() if v["INDICE_A_MAQUINA_BUSCA"] == "sim") < sum(1 for v in contraprova.values() if v["FLOW_OBSERVED"]) else "NO"),
    ])
    return OrderedDict([
        ("DATASET", "SINTONIA-SOURCE-COLLECTION-READINESS-V1"), ("MISSAO", MISSAO),
        ("LEI", "DECLARED_CONTRACT != CAPABILITY != WIRING != FLOW_OBSERVED != SOURCE_COLLECTION_READY != BIG_COLLECTION_EXECUTABLE. Nenhum se infere do outro; o indice gerado nao e owner do readiness."),
        ("INICIO_DA_MISSAO", INICIO_DA_MISSAO),
        ("FONTES_DA_MEDICAO", [str(p.relative_to(RAIZ)).replace(os.sep, "/") for p in
                               (FONTES_GERADAS, INDICE, TABELA, RAIZ / "regras" / "italy_contracts.mjs", COLETOR,
                                RAIZ / "pedido" / "receitas.py", RELEVANCIA, OBSERVACOES, CORRIDAS, MANIFESTO_DE_CORRIDAS)]),
        ("OS_QUATRO_CONTADORES", os_quatro_contadores()),
        ("CONTRAPROVA_AS_SEIS", contraprova),
        ("RESUMO", resumo), ("POR_SHAPE", por_shape), ("FONTES", linhas),
    ])


def escrever_md(d: dict) -> str:
    R, L = d["RESUMO"], []
    P = L.append
    P("# SOURCE COLLECTION READINESS V1 — CENSO (gerado)")
    P("")
    P("> **Gerado** por `provas/medir_source_collection_readiness.py`. Nao editar a mao: o JSON irmao")
    P("> (`data/derivados/SOURCE-COLLECTION-READINESS-V1.json`) e a fonte, e um teste reprova se divergirem.")
    P("")
    P("```")
    for k in ("TOTAL_SOURCES", "IT_SOURCES", "EU_APPLICABLE", "DECLARED_CONTRACT", "COLLECTION_WIRED", "FLOW_OBSERVED",
              "SOURCE_COLLECTION_READY_BEFORE", "SOURCE_COLLECTION_READY_AFTER", "NEW_SOURCE_COLLECTION_READY", "STILL_NOT_READY",
              "RELEVANCE_SIM", "RELEVANCE_PENDING", "BIG_COLLECTION_EXECUTABLE_BEFORE", "BIG_COLLECTION_EXECUTABLE_AFTER",
              "SOURCES_CONFIGURED", "SOURCES_CANARY_PASS", "SOURCES_CANARY_FAIL", "SOURCES_CANARY_NOT_RUN", "INDEX_COLLECTION_READINESS_STALE"):
        P("%-36s %s" % (k, R[k]))
    P("```")
    P("")
    P("## Os quatro contadores — quatro owners, nenhum acertado para bater")
    P("")
    P("| contador | valor | o que mede | owner | como | stale? |")
    P("|---|---|---|---|---|---|")
    for k, v in d["OS_QUATRO_CONTADORES"].items():
        P("| `%s` | **%s** | %s | `%s` | %s | %s |" % (k, v["VALOR"], v["O_QUE_MEDE"], v["OWNER"], v["COMO"], v["STALE"]))
    P("")
    P("## A contraprova — as seis da primeira Big Collection")
    P("")
    P("| SOURCE_ID | indice «a maquina busca?» | FLOW_OBSERVED | observacoes HEALTHY com bytes |")
    P("|---|---|---|---|")
    for sid, v in d["CONTRAPROVA_AS_SEIS"].items():
        P("| `%s` | %s | %s | %s |" % (sid, v["INDICE_A_MAQUINA_BUSCA"], "YES" if v["FLOW_OBSERVED"] else "NO", v["OBSERVACOES_HEALTHY_COM_BYTES"]))
    P("")
    P("## Por forma de aquisicao")
    P("")
    P("| SHAPE | FONTES | READY | BLOCKED | TOOL | NEW CODE? | blockers |")
    P("|---|---|---|---|---|---|---|")
    for s, v in d["POR_SHAPE"].items():
        P("| `%s` | %s | %s | %s | %s | %s | %s |" % (s, v["FONTES"], v["READY"], v["BLOCKED"], "; ".join(v["TOOL"]) or "—", v["NEW_CODE"],
                                                     ", ".join("%s %s" % (k, n) for k, n in v["BLOCKERS"].items()) or "—"))
    P("")
    P("## Por blocker")
    P("")
    P("| BLOCKER | FONTES |")
    P("|---|---|")
    for k, n in R["BLOCKERS"].items():
        P("| `%s` | %s |" % (k, n))
    P("")
    P("## Fonte a fonte")
    P("")
    P("| SOURCE_ID | T | SHAPE | wired | canario | fluxo | indice | relev. | READY | EXEC | blocker | documento observado |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for l in d["FONTES"]:
        doc = ((l.get("CANARY") or {}).get("OBSERVACAO") or {}).get("SOURCE_URL") or ((l.get("FLOW_EVIDENCE") or {}).get("ULTIMA") or {}).get("SOURCE_URL") or ""
        P("| `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            l["SOURCE_ID"], l["PROPOSITO"], l["ACCESS_SHAPE"], l["COLLECTION_WIRED"], l["CANARY_STATE"], l["FLOW_OBSERVED"],
            l["INDEX_A_MAQUINA_BUSCA"], l["RELEVANCE_STATE"], l["TECHNICALLY_COLLECTION_READY"], l["BIG_COLLECTION_EXECUTABLE"],
            ("`%s` %s" % (l["BLOCKER"], l["BLOCKER_DETALHE"][:70].replace("|", "/"))) if l["BLOCKER"] else "—",
            str(doc)[:90].replace("|", "/")))
    P("")
    return "\n".join(L) + "\n"


def main() -> int:
    d = medir()
    if "--conferir" in sys.argv:
        if not SAIDA_JSON.is_file():
            print("SEM_JSON_GRAVADO")
            return 1
        gravado = _json(SAIDA_JSON)
        iguais = gravado["RESUMO"] == d["RESUMO"] and [l["SOURCE_ID"] + l["TECHNICALLY_COLLECTION_READY"] + l["BLOCKER"] for l in gravado["FONTES"]] == \
            [l["SOURCE_ID"] + l["TECHNICALLY_COLLECTION_READY"] + l["BLOCKER"] for l in d["FONTES"]]
        print("CENSO_CONFERE=%s" % ("SIM" if iguais else "NAO"))
        return 0 if iguais else 1
    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    with io.open(SAIDA_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with io.open(SAIDA_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(escrever_md(d))
    R = d["RESUMO"]
    print("CENSO=OK · fontes=%s · READY antes=%s depois=%s novas=%s · wired=%s · fluxo=%s · executaveis=%s · blockers=%s"
          % (R["TOTAL_SOURCES"], R["SOURCE_COLLECTION_READY_BEFORE"], R["SOURCE_COLLECTION_READY_AFTER"],
             R["NEW_SOURCE_COLLECTION_READY"], R["COLLECTION_WIRED"], R["FLOW_OBSERVED"], R["BIG_COLLECTION_EXECUTABLE_AFTER"],
             json.dumps(R["BLOCKERS"], ensure_ascii=False)))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
