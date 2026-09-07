#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · SCANNER DA COLETA

    A COLETA JA ESTAVA ORGANIZADA. SO NAO ESTAVA LEGIVEL.

Este repositorio ja descreve, com cuidado, de onde o dado vem e como e buscado.
So que essa descricao vive em 1.600 linhas de prosa, em dois documentos, e por
isso ninguem consegue responder de cabeca "quantas fontes temos, de que paises,
quais delas sabemos coletar sozinhos". Este ficheiro le essa prosa e devolve uma
tabela.

Nao inventa nada. Nao resume. Nao interpreta. Le e transcreve, guardando o
ficheiro e a linha de onde cada campo saiu.

O QUE ELE LE
------------
  docs/fontes/ATLAS-DE-FONTES-EAME.md        O QUE cada fonte tem
                                             (blocos ``` com CHAVE: valor)
  docs/operacao/CONTRATOS-DAS-FONTES-EAME.md COMO se busca, o que se espera de
                                             volta, e o que fazer quando quebra
  scripts/*.py                               as PALAVRAS realmente usadas na
                                             busca (`TERMOS = ...`), lidas com
                                             `ast`, sem executar codigo nenhum

A SEPARACAO QUE IMPORTA
-----------------------
Uma fonte REGISTRADA e uma fonte que alguem abriu e olhou.
Uma fonte com CONTRATO e uma fonte que a maquina sabe buscar sozinha.
Sao coisas diferentes, e o mapa mostra as duas separadas — porque a distancia
entre elas e exatamente o trabalho que falta fazer.

SAIDA: system-map/data/sources.generated.json
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "system-map" / "data" / "sources.generated.json"

ATLAS = "docs/fontes/ATLAS-DE-FONTES-EAME.md"
CONTRATOS = "docs/operacao/CONTRATOS-DAS-FONTES-EAME.md"

PAIS = {"EU": "EUROPA", "FR": "FRANCA", "ES": "ESPANHA", "IT": "ITALIA"}
TERRITORIO = {
    "T1": "Cultura e producao", "T2": "Clima e tempo", "T3": "Praga e doenca",
    "T4": "Regulatorio", "T5": "Preco e mercado", "T6": "Comercio e distribuicao",
    "T7": "Ciencia e ensaio", "T8": "Voz do campo", "T9": "Concorrente",
    "T10": "Politica e subsidio", "T11": "Solo e agua", "T12": "Substancia ativa",
}


def ler(rel: str) -> list[str]:
    p = RAIZ / rel
    if not p.exists():
        return []
    return p.read_text(encoding="utf-8", errors="replace").splitlines()


# ─────────────────────────────────────────────────────────────────────────────
# 1 · O ATLAS — o que cada fonte tem
# ─────────────────────────────────────────────────────────────────────────────
RE_CAMPO = re.compile(r"^([A-Z_]{3,32}):\s*(.*)$")


def contagem_declarada() -> dict:
    """O cabecalho do atlas carrega um contador escrito a mao.

    Comparar esse numero com o numero de fichas que realmente existem e a coisa
    mais barata que este scanner faz — e a que mais vezes vai apanhar alguem. Um
    contador de cabecalho envelhece em silencio: ninguem o atualiza ao acrescentar
    uma fonte, e a partir dai o documento afirma um total que ele proprio nao tem.
    """
    for n, linha in enumerate(ler(ATLAS), 1):
        m = re.search(r"<!--M:SOURCE_ID_COUNT-->(\d+)<!--/M-->", linha)
        if m:
            v = re.search(r"\((\d+) GREEN, (\d+) YELLOW, (\d+) NÃO SEI\)", linha)
            return {"total": int(m.group(1)), "line": n,
                    "green": int(v.group(1)) if v else None,
                    "yellow": int(v.group(2)) if v else None,
                    "nao_sei": int(v.group(3)) if v else None}
    return {}


def citadas_sem_ficha() -> list:
    """Fontes que o atlas NOMEIA em tabela, mas para as quais nao escreveu ficha.

    `ES-T8-001`, `ES-T8-002` e `ES-T8-003` aparecem numa tabela de resumo com o
    numero de origens e o veredito — mas sem SOURCE_NAME, sem ACCESS_METHOD, sem
    EVIDENCE. Sao tres linhas de tabela, e nao tres fichas.

    E sao exatamente as que MAIS foram coletadas: oito das dez corridas
    registadas foram buscar a estas tres.

        A COLETA MAIS FEITA E A MENOS DOCUMENTADA.

    Isto nao e detalhe de arrumacao. Sem ficha, ninguem sabe como se volta la:
    por que porta se entra, o que se espera de volta, o que fazer quando quebrar.
    A proxima pessoa refaz a descoberta do zero — e paga por ela outra vez.
    """
    linhas, achadas = ler(ATLAS), []
    RE_LINHA = re.compile(r"^\|\s*`((?:EU|FR|ES|IT)-T\d{1,2}-\d{3})`\s*\|(.+)\|\s*$")
    for n, l in enumerate(linhas, 1):
        m = RE_LINHA.match(l.strip())
        if m:
            celulas = [c.strip().strip("*") for c in m.group(2).split("|")]
            achadas.append({"source_id": m.group(1), "line": n,
                            "o_que_a_tabela_diz": " · ".join(c for c in celulas if c)})
    return achadas


def veredito(bruto: str) -> str:
    v = (bruto or "").strip().upper()
    for conhecido in ("GREEN", "YELLOW", "RED", "PARCIAL"):
        if v.startswith(conhecido):
            return conhecido
    return "NAO SEI"


def do_atlas() -> list[dict]:
    """Cada fonte e um bloco ``` com linhas `CHAVE: valor`.

    Valor que continua na linha seguinte (recuado, sem CHAVE:) e continuacao —
    juntar com espaco em vez de descartar, senao metade dos URLs e dos exemplos
    reais some sem ninguem reparar.
    """
    linhas, fontes = ler(ATLAS), []
    dentro, atual, chave, inicio = False, {}, None, 0

    for n, cru in enumerate(linhas, 1):
        if cru.strip().startswith("```"):
            if dentro and atual.get("SOURCE_ID"):
                atual["_line"] = inicio
                fontes.append(atual)
            dentro, atual, chave, inicio = not dentro and True or False, {}, None, n
            continue
        if not dentro:
            continue
        m = RE_CAMPO.match(cru)
        if m:
            chave, valor = m.group(1), m.group(2).strip()
            atual[chave] = valor
        elif chave and cru.strip():
            atual[chave] = (atual[chave] + " " + cru.strip()).strip()

    # O atlas comeca com um MODELO de ficha em branco (`SOURCE_ID: # ex.: ...`),
    # para quem for registrar uma fonte nova copiar. Ele nao e uma fonte. Sem este
    # filtro, o mapa passaria a contar 30 fontes e uma delas seria um formulario
    # vazio — e um numero inflado e pior do que um numero pequeno.
    RE_ID = re.compile(r"^(EU|FR|ES|IT)-T\d{1,2}-\d{3}$")
    saida = []
    for f in fontes:
        sid = f["SOURCE_ID"].strip()
        if not RE_ID.match(sid):
            continue
        pais, terr = (sid.split("-") + ["", ""])[:2]
        saida.append({
            "source_id": sid,
            "name": f.get("SOURCE_NAME", sid),
            "owner": f.get("SOURCE_OWNER", ""),
            "country": PAIS.get(pais, f.get("COUNTRY", "?")),
            "territory": terr,
            "territory_name": TERRITORIO.get(terr, ""),
            "type": f.get("SOURCE_TYPE", ""),
            "url": f.get("URL", ""),
            "access_method": f.get("ACCESS_METHOD", ""),
            "language": f.get("LANGUAGE", ""),
            "update_frequency": f.get("UPDATE_FREQUENCY", ""),
            "historical_depth": f.get("HISTORICAL_DEPTH", ""),
            "automation": f.get("AUTOMATION_FEASIBILITY", ""),
            "collection": f.get("COLLECTION_FEASIBILITY", ""),
            "risk": f.get("LEGAL_OR_ACCESS_RISK", ""),
            "use_case": f.get("ADAMA_USE_CASE", ""),
            "real_example": f.get("REAL_EXAMPLE", ""),
            "evidence_path": f.get("EVIDENCE", ""),
            # "NÃO SEI" sao duas palavras: cortar no primeiro espaco transformava
            # o unico estado honesto do repositorio num "NÃO" que nao significa nada.
            "verdict": veredito(f.get("VERDICT", "")),
            "evidence": {"file": ATLAS, "line": f["_line"],
                         "snippet": f"bloco {sid} no atlas de fontes"},
        })
    return sorted(saida, key=lambda s: s["source_id"])


# ─────────────────────────────────────────────────────────────────────────────
# 1b · O SEGUNDO CATALOGO — e a reconciliacao com o primeiro
# ─────────────────────────────────────────────────────────────────────────────
MASTER_IT = "candidatas/ITALY-SOURCE-MASTER-V1.json"


def do_master() -> list:
    """As 54 fontes italianas, do catalogo que a coleta de Italia levantou.

    Ele tem campos que o atlas nao tem, e sao bons: `OWNER_ID` (dono normalizado,
    44 deles), `SOURCE_ROLE`, `WHAT_IT_PROVES` e — o melhor de todos —
    `WHAT_IT_DOES_NOT_PROVE`, que e a pergunta que quase nenhum catalogo faz.

    Mas ele nasceu AO LADO do atlas, e nao dentro dele. Duas listas a responder
    «que fontes o SINTONIA tem» sao duas verdades, e a segunda envelhece calada.

        NAO SE APAGA UM REGISTO PARA ARRUMAR. RECONCILIA-SE.

    O atlas continua a ser o registo canonico das FICHAS. Este e lido como o que
    e — um levantamento — e o mapa mostra, fonte a fonte, em qual dos dois ela
    esta. A diferenca entre as duas listas deixa de ser silencio e passa a ser
    uma coluna.
    """
    p = RAIZ / MASTER_IT
    if not p.exists():
        return []
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    donos = {o["OWNER_ID"]: o for o in d.get("owners", [])}
    fora = []
    for s in d.get("sources", []):
        dono = donos.get(s.get("OWNER_ID"), {})
        sid = s.get("SOURCE_ID", "")
        pais, terr = (sid.split("-") + ["", ""])[:2]
        fora.append({
            "source_id": sid,
            "name": s.get("SOURCE_NAME", sid),
            "owner": dono.get("OWNER_CANONICAL_NAME", ""),
            "owner_kind": dono.get("OWNER_KIND", ""),
            "country": PAIS.get(pais, "?"),
            "territory": terr, "territory_name": TERRITORIO.get(terr, ""),
            "type": s.get("SOURCE_TYPE", ""), "role": s.get("SOURCE_ROLE", ""),
            "url": s.get("URL", ""), "access_method": s.get("ACCESS_METHOD", ""),
            "crops": s.get("CROPS", ""), "topics": s.get("TOPICS", ""),
            "region": s.get("REGION", ""),
            "update_frequency": s.get("UPDATE_FREQUENCY", ""),
            "historical_depth": s.get("HISTORICAL_DEPTH", ""),
            "status": s.get("STATUS", ""),
            "verdict": veredito(s.get("ATLAS_VERDICT", "")),
            "prova": s.get("WHAT_IT_PROVES", ""),
            "nao_prova": s.get("WHAT_IT_DOES_NOT_PROVE", ""),
            "onde": MASTER_IT,
        })
    return sorted(fora, key=lambda x: x["source_id"])


def reconciliar(atlas: list, master: list, citadas: list) -> dict:
    """Onde cada fonte esta registada — e onde nao esta."""
    a = {f["source_id"] for f in atlas}
    m = {f["source_id"] for f in master}
    c = {x["source_id"] for x in citadas}
    return {
        "so_no_atlas": sorted(a - m),
        "so_no_master_italiano": sorted(m - a - c),
        "nos_dois": sorted(a & m),
        "so_citadas_em_tabela": sorted(c - a - m),
        "total_distintas": len(a | m | c),
        "leitura": (
            f"{len(a)} tem ficha no atlas, {len(m)} estao no levantamento italiano, "
            f"{len(a & m)} estao nos dois. {len(m - a - c)} foram levantadas em Italia "
            f"e nunca ganharam ficha no atlas — e o atlas e o registo canonico."),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2 · OS CONTRATOS — como se busca, e o que fazer quando quebra
# ─────────────────────────────────────────────────────────────────────────────
RE_CONTRATO = re.compile(r"^([A-Z_/]{4,32})\s{2,}(.*)$")


def dos_contratos() -> dict:
    linhas, fora, atual, inicio = ler(CONTRATOS), {}, None, 0
    chave = None
    for n, cru in enumerate(linhas, 1):
        m = RE_CONTRATO.match(cru)
        if m and m.group(1) == "SOURCE_ID":
            if atual:
                fora[atual["SOURCE_ID"]] = {**atual, "_line": inicio}
            atual, inicio, chave = {"SOURCE_ID": m.group(2).strip()}, n, None
            continue
        if atual is None:
            continue
        if m:
            chave = m.group(1)
            atual[chave] = m.group(2).strip()
        elif chave and cru.startswith(" " * 10) and cru.strip():
            atual[chave] = (atual[chave] + " " + cru.strip()).strip()
        elif cru.startswith("#"):
            if atual:
                fora[atual["SOURCE_ID"]] = {**atual, "_line": inicio}
            atual, chave = None, None
    if atual:
        fora[atual["SOURCE_ID"]] = {**atual, "_line": inicio}

    return {sid: {
        "retrieval_method": c.get("RETRIEVAL_METHOD", ""),
        "http_method": c.get("HTTP_METHOD", ""),
        "parameters": c.get("PARAMETERS", ""),
        "auth_required": c.get("AUTH_REQUIRED", ""),
        "output_type": c.get("OUTPUT_TYPE", ""),
        "expected_fields": c.get("EXPECTED_FIELDS", ""),
        "identity_keys": c.get("IDENTITY_KEYS", ""),
        "date_field": c.get("DATE_FIELD", ""),
        "update_behavior": c.get("UPDATE_BEHAVIOR", ""),
        "expected_failures": c.get("EXPECTED_FAILURES", ""),
        "fail_closed_rule": c.get("FAIL_CLOSED_RULE", ""),
        "fallback": c.get("FALLBACK", ""),
        "archive_requirement": c.get("ARCHIVE_REQUIREMENT", ""),
        "criticality": c.get("PRIMARY/SECONDARY", ""),
        "evidence": {"file": CONTRATOS, "line": c["_line"],
                     "snippet": f"contrato de {sid}"},
    } for sid, c in fora.items()}


# ─────────────────────────────────────────────────────────────────────────────
# 3 · AS CONTAS — a outra metade das fontes, que nao esta no atlas
# ─────────────────────────────────────────────────────────────────────────────
CONTAS = "data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json"


def as_contas() -> dict:
    """As paginas publicas do concorrente, uma por plataforma.

    O atlas nao as cobre, e isso nao e esquecimento: uma base regulatoria e uma
    pagina de Instagram sao fontes de naturezas diferentes e por isso vivem em
    registos diferentes. Mas para quem olha o mapa sao a mesma pergunta — "de onde
    vem o que sabemos?" — e por isso aparecem lado a lado.

    ESTAR NA LISTA NAO E AUTORIZACAO. `COLLECTION_AUTHORIZED` so e `YES` quando a
    identidade da conta esta PROVED **e** a conta e local do pais. As outras ficam
    a vista, com o motivo da recusa escrito — porque saber o que foi deixado de
    fora e parte de saber o que foi visto.
    """
    p = RAIZ / CONTAS
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    por_plataforma: dict[str, dict] = {}
    for a in d.get("ACCOUNTS", []):
        plat = a.get("PLATFORM", "?")
        g = por_plataforma.setdefault(plat, {"plataforma": plat, "total": 0,
                                             "autorizadas": 0, "contas": []})
        g["total"] += 1
        ok = a.get("COLLECTION_AUTHORIZED") == "YES"
        g["autorizadas"] += 1 if ok else 0
        g["contas"].append({
            "empresa": a.get("COMPANY", ""), "pais": a.get("COUNTRY", ""),
            "handle": a.get("ACCOUNT_HANDLE", ""), "url": a.get("ACCOUNT_URL", ""),
            "autorizada": ok,
            "identidade": a.get("ACCOUNT_IDENTITY_STATE", ""),
            "porque": (a.get("COLLECTION_AUTHORIZED_WHY")
                       or a.get("EXCLUSION_REASONS") or "")[:200],
        })
    for g in por_plataforma.values():
        g["contas"].sort(key=lambda c: (not c["autorizada"], c["empresa"], c["pais"]))
    return {"file": CONTAS, "por_plataforma": dict(sorted(por_plataforma.items())),
            "total": sum(g["total"] for g in por_plataforma.values()),
            "autorizadas": sum(g["autorizadas"] for g in por_plataforma.values())}


# ─────────────────────────────────────────────────────────────────────────────
# 4 · A PORTA DE ENTRADA — e a escada que uma fonte tem de subir
# ─────────────────────────────────────────────────────────────────────────────
FILA = "candidatas/FONTES-CANDIDATAS.json"


def a_porta(fontes: list, contratos: dict) -> dict:
    """Mede em que degrau esta cada fonte, e o que ha na fila de entrada.

    O acervo de fontes e capital parado: consulta-se antes de coletar. Mas capital
    parado sem porta apodrece — fonte nova aparece no meio de uma coleta e morre no
    historico do terminal de quem a viu. A porta e `candidatas/fonte_nova.py`, e o que
    entra por ela e CANDIDATA, nunca fonte.

    A distancia entre os degraus e o trabalho que falta. Um numero por degrau diz,
    numa linha, se a casa esta a acumular pistas que ninguem verifica ou fichas que
    ninguem sabe buscar.
    """
    fila = {"CANDIDATAS": []}
    p = RAIZ / FILA
    if p.exists():
        try:
            fila = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    cand = fila.get("CANDIDATAS", [])
    por_tipo: dict[str, int] = {}
    for c in cand:
        por_tipo[c.get("TIPO", "?")] = por_tipo.get(c.get("TIPO", "?"), 0) + 1

    registadas = [f for f in fontes if f["verdict"] in ("GREEN", "YELLOW")]
    return {
        "porta": "candidatas/fonte_nova.py",
        "fila_file": FILA,
        "tipos_aceites": sorted(por_tipo) or [],
        "escada": [
            {"degrau": 1, "nome": "CANDIDATA",
             "o_que_e": "alguem viu que existe. Ninguem abriu ainda.",
             "quantas": len([c for c in cand if c.get("ESTADO") == "CANDIDATA"]),
             "onde": FILA,
             "sobe_como": "abrir, olhar o que entrega e guardar um exemplo real"},
            {"degrau": 2, "nome": "REGISTADA",
             "o_que_e": "tem ficha no atlas, com exemplo real guardado.",
             "quantas": len(registadas), "onde": ATLAS,
             "sobe_como": "escrever COMO se busca e o que fazer quando quebrar"},
            {"degrau": 3, "nome": "CONTRATADA",
             "o_que_e": "tem contrato de busca escrito.",
             "quantas": len(contratos), "onde": CONTRATOS,
             "sobe_como": "por a busca a correr sozinha, num workflow"},
            {"degrau": 4, "nome": "AUTOMATICA",
             "o_que_e": "a maquina vai la sozinha, sem ninguem por perto.",
             "quantas": None, "onde": ".github/workflows/",
             "sobe_como": "—"},
        ],
        "por_tipo": dict(sorted(por_tipo.items())),
        "candidatas": cand,
        "nao_verificadas": len([f for f in fontes if f["verdict"] == "NAO SEI"]),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7 · AS COLETAS QUE JA FORAM FEITAS
# ─────────────────────────────────────────────────────────────────────────────
MANIFESTO = "data/samples/RUN-MANIFEST.json"


def coletas_feitas(fontes: list) -> dict:
    """Cruza cada corrida registada com a fonte que ela foi buscar.

    O `RUN_ID` comeca pelo `SOURCE_ID` — `ES-T8-001-2026-08-29-a` foi buscar a
    fonte `ES-T8-001`. E isso fecha o circulo que faltava:

        a fonte  ->  como foi buscada  ->  o que trouxe  ->  o que sobrou
                                                          ->  quanto custou

    `ITEM_COUNT_RAW` e `ITEM_COUNT_NORMALIZED` sao os dois numeros que respondem
    «o que e descartado»: o que veio, e o que atravessou a regua. A diferenca
    entre os dois nao e desperdicio — e o filtro a trabalhar. Mas so se sabe se
    esta a trabalhar bem quando os dois numeros ficam guardados lado a lado.

        UMA COLETA SEM RENDIMENTO MEDIDO E UMA COLETA QUE NAO ENSINA A SEGUINTE.

    Nada e inferido: os campos vazios aparecem como `NOT_PRESERVED`, que e o que
    o proprio manifesto escreve quando nao guardou.
    """
    p = RAIZ / MANIFESTO
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    ids = {f["source_id"] for f in fontes} | {
        c["source_id"] for c in citadas_sem_ficha()}
    vazio = ("NOT_PRESERVED", None, "", "NAO SEI")

    def num(v):
        return v if isinstance(v, int) else None

    corridas = []
    for r in d.get("RUNS", []):
        rid = r.get("RUN_ID", "")
        # a fonte e o prefixo mais longo do RUN_ID que exista no atlas
        fonte = next((i for i in sorted(ids, key=len, reverse=True)
                      if rid.startswith(i)), None)
        cru, limpo = num(r.get("ITEM_COUNT_RAW")), num(r.get("ITEM_COUNT_NORMALIZED"))
        corridas.append({
            "run_id": rid,
            "fonte": fonte,
            "plataforma": r.get("PLATFORM", ""),
            "quem_foi_buscar": r.get("ACTOR", ""),
            "com_que_parametros": r.get("INPUT") if r.get("INPUT") not in vazio else None,
            "que_pergunta": r.get("QUERY") if r.get("QUERY") not in vazio else None,
            "pais": r.get("COUNTRY", ""),
            "missao": r.get("MISSION", ""),
            "trouxe": cru,
            "sobrou": limpo,
            "rendimento": (round(100 * limpo / cru) if cru and limpo is not None
                           and cru > 0 else None),
            "custou_usd": r.get("COST_USD") if r.get("COST_USD") not in vazio else None,
            "estado": r.get("STATUS", ""),
            "erro": r.get("ERROR") if r.get("ERROR") not in vazio else None,
            "prova": r.get("EVIDENCE_PATH") if r.get("EVIDENCE_PATH") not in vazio else None,
            "bruto": r.get("RAW_EVIDENCE_PATH") if r.get("RAW_EVIDENCE_PATH") not in vazio else None,
        })

    por_pais: dict[str, int] = {}
    por_plataforma: dict[str, int] = {}
    for c in corridas:
        por_pais[c["pais"]] = por_pais.get(c["pais"], 0) + 1
        por_plataforma[c["plataforma"]] = por_plataforma.get(c["plataforma"], 0) + 1

    com_rend = [c for c in corridas if c["rendimento"] is not None]
    com_custo = [c for c in corridas if isinstance(c["custou_usd"], (int, float))]
    fontes_com_corrida = {c["fonte"] for c in corridas if c["fonte"]}

    return {
        "ficheiro": MANIFESTO,
        "corridas": corridas,
        "total": len(corridas),
        "por_pais": dict(sorted(por_pais.items())),
        "por_plataforma": dict(sorted(por_plataforma.items())),
        "fontes_ja_coletadas": sorted(fontes_com_corrida),
        "fontes_nunca_coletadas": sorted(ids - fontes_com_corrida),
        "com_rendimento_medido": len(com_rend),
        "com_custo_medido": len(com_custo),
        "custo_total_usd": round(sum(c["custou_usd"] for c in com_custo), 2) if com_custo else None,
        "trouxe_total": sum(c["trouxe"] for c in corridas if c["trouxe"]),
        "sobrou_total": sum(c["sobrou"] for c in corridas if c["sobrou"]),
    }


LEDGER_IT = "data/collection-ledger/italy/observations.ndjson"
RUNS_IT = "data/collection-ledger/italy/runs.ndjson"


def coletas_italianas() -> dict:
    """O registo da coleta italiana — outro formato, a mesma pergunta.

    Sao dois registos de coleta nesta casa, e nenhum sabia do outro:

        RUN-MANIFEST.json          10 corridas, campos em MAIUSCULAS, uma linha
        observations.ndjson       144 observacoes, uma por linha, outro esquema

    Nao se apaga um registo para arrumar. O que se faz e ler os dois e apresentar
    UMA memoria — com a diferenca de formato a vista, porque ela e um facto sobre
    a casa e nao um detalhe a esconder.

    E o registo italiano e mais rico: guarda o SHA256 de cada documento, a
    assinatura MIME, o `FACT_TIME` separado do `CAPTURED_AT`, o estado de saude,
    a cadencia esperada e o IP por onde a requisicao saiu. Tres coisas dessas o
    manifesto espanhol nao tem.
    """
    obs, runs = [], []
    p = RAIZ / LEDGER_IT
    if p.exists():
        for l in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if l.strip():
                try:
                    obs.append(json.loads(l))
                except json.JSONDecodeError:
                    pass
    q = RAIZ / RUNS_IT
    if q.exists():
        for l in q.read_text(encoding="utf-8", errors="replace").splitlines():
            if l.strip():
                try:
                    runs.append(json.loads(l))
                except json.JSONDecodeError:
                    pass
    if not obs and not runs:
        return {}

    por_fonte: dict[str, int] = {}
    novos = repetidos = 0
    for o in obs:
        sid = o.get("SOURCE_ID", "?")
        por_fonte[sid] = por_fonte.get(sid, 0) + 1
        r = (o.get("OBSERVATION_RESULT") or "").upper()
        if "NEW" in r or "NOVO" in r:
            novos += 1
        elif "SEEN" in r or "AGAIN" in r or "REPETID" in r:
            repetidos += 1

    return {
        "ficheiro_observacoes": LEDGER_IT,
        "ficheiro_corridas": RUNS_IT,
        "observacoes": len(obs),
        "corridas": len(runs),
        "por_fonte": dict(sorted(por_fonte.items(), key=lambda x: -x[1])),
        "documentos_novos": novos,
        "ja_vistos": repetidos,
        "com_sha256": sum(1 for o in obs if o.get("RAW_SHA256")),
        "com_fact_time": sum(1 for o in obs if o.get("FACT_TIME")),
        "com_cadencia": sum(1 for o in obs if o.get("CADENCE_STATE")),
        "corridas_com_egress": sum(1 for r in runs if r.get("EGRESS_IP")),
        "campos": sorted(obs[0]) if obs else [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6 · A MEMORIA DA COLETA — o que cada coletor faz, medido nele proprio
# ─────────────────────────────────────────────────────────────────────────────
CARIMBO_DATA = ("CAPTURED_AT", "PUBLICATION_DATE", "FACT_DATE", "CAPTURE_DATE")
CARIMBO_LUGAR = ("SOURCE_LOCATION", "FACT_LOCATION", "COUNTRY")
MARCA_DESCARTE = ("EXCLUSION_REASON", "DESCARTAD", "RECUSAD", "NOT_ELIGIBLE",
                  "EXCLUID", "MOTIVO_DA_RECUSA", "REJEIT")


def memoria_da_coleta(arquivos: list) -> list:
    """Cinco perguntas, por coletor, respondidas pelo proprio ficheiro.

        1 · como se busca          2 · o que traz
        3 · como e filtrada        4 · o que e descartado, e porque
        5 · onde fica antes de ir para a inteligencia

    Uma coleta so aprende com a coleta feita se a coleta feita tiver deixado
    resposta escrita. Hoje, cinco das vinte e tres fontes tem contrato de busca;
    as outras dezoito so existem na memoria de quem as descobriu.

        O QUE NAO FOI ESCRITO NAO SE APRENDE — REPETE-SE.

    Nada aqui e declarado. Cada resposta sai do proprio ficheiro do coletor: os
    campos que ele carimba, as leis que ele importa, se ele regista o que deixou
    de fora. O que ele nao fizer aparece como buraco, e nao como silencio.
    """
    saida = []
    for rel in sorted(f for f in arquivos
                      if f.startswith(("coleta/", "regras/")) and f.endswith(".py")):
        p = RAIZ / rel
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not re.search(r"open\(|json\.dump|write_text", t):
            continue  # nao grava registo: nao e coletor

        data = sorted({c for c in CARIMBO_DATA if c in t})
        lugar = sorted({c for c in CARIMBO_LUGAR if c in t})
        leis = sorted({m for m in re.findall(
            r"^\s*import\s+(proveniencia|voz|cicatrizes_brasil|lugar_do_fato|"
            r"fato_local|source_health|sensor_medir|comunicacao_identidade)",
            t, re.M)})
        saida.append({
            "ficheiro": rel,
            "como_se_chama": re.search(r"^\s+(?:python3?|py)\s+([\w/.\- ]+)",
                                       t, re.M).group(1).strip()
                             if re.search(r"^\s+(?:python3?|py)\s+[\w/.\- ]+", t, re.M)
                             else "",
            "carimba_data": data,
            "carimba_lugar": lugar,
            "separa_fonte_do_fato": "SOURCE_LOCATION" in t and "FACT_LOCATION" in t,
            "leis_que_obedece": leis,
            "regista_descarte": [m for m in MARCA_DESCARTE if m in t.upper()][:3],
        })
    return saida


# ─────────────────────────────────────────────────────────────────────────────
# 5 · AS PALAVRAS — o que e realmente digitado na busca
# ─────────────────────────────────────────────────────────────────────────────
def as_palavras(arquivos: list[str]) -> list[dict]:
    """Le `TERMOS = ...` com `ast`, sem executar nada.

    Importar o modulo para ler a variavel seria dar ao scanner do mapa o poder de
    correr codigo de coleta — e um scanner que executa o que le deixa de ser
    seguro para correr no CI de um repositorio publico.
    """
    saida = []
    for rel in arquivos:
        p = RAIZ / rel
        if p.suffix != ".py" or not p.exists():
            continue
        try:
            arvore = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for no in arvore.body:
            if not isinstance(no, ast.Assign):
                continue
            nomes = [t.id for t in no.targets if isinstance(t, ast.Name)]
            if not any(x in ("TERMOS", "QUERIES", "KEYWORDS", "BUSCAS") for x in nomes):
                continue
            try:
                valor = ast.literal_eval(no.value)
            except (ValueError, SyntaxError):
                continue
            grupos = []
            if isinstance(valor, dict):
                for k, v in valor.items():
                    grupos.append({"grupo": str(k),
                                   "palavras": [str(x) for x in v] if isinstance(v, (list, tuple)) else [str(v)]})
            elif isinstance(valor, (list, tuple)):
                for item in valor:
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        pal = item[1] if isinstance(item[1], (list, tuple)) else [item[1]]
                        grupos.append({"grupo": str(item[0]),
                                       "palavras": [str(x) for x in pal],
                                       "porque": str(item[2]) if len(item) > 2 else ""})
            if grupos:
                saida.append({
                    "file": rel, "line": no.lineno, "variavel": nomes[0],
                    "grupos": grupos,
                    "total_palavras": sum(len(g["palavras"]) for g in grupos),
                })
    return sorted(saida, key=lambda x: x["file"])


# ─────────────────────────────────────────────────────────────────────────────
# 4 · POR ONDE SE ENTRA — os enderecos que o codigo realmente chama
# ─────────────────────────────────────────────────────────────────────────────
RE_URL = re.compile(r"https://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]{8,90}")


def as_portas(arquivos: list[str]) -> list[dict]:
    achados: dict[str, dict] = {}
    for rel in arquivos:
        if Path(rel).suffix not in (".py", ".sh"):
            continue
        p = RAIZ / rel
        if not p.exists():
            continue
        for n, linha in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            nu = linha.split("#")[0]
            for u in RE_URL.findall(nu):
                # so o host + primeiro segmento: o resto e parametro, e parametro
                # muda a cada corrida. O que identifica a porta e por onde se bate.
                partes = u.split("/")
                porta = "/".join(partes[:4]) if len(partes) > 3 else u
                a = achados.setdefault(porta, {"endpoint": porta, "usado_por": []})
                if not any(x["file"] == rel for x in a["usado_por"]):
                    a["usado_por"].append({"file": rel, "line": n})
    return sorted(achados.values(), key=lambda x: -len(x["usado_por"]))[:40]


# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    gerado = RAIZ / "system-map" / "data" / "architecture.generated.json"
    if not gerado.exists():
        print("FALTA=architecture.generated.json · corra scan_repo.py primeiro", file=sys.stderr)
        return 2
    G = json.loads(gerado.read_text(encoding="utf-8"))
    arquivos = [f["path"] for f in G["FILES"]]

    fontes = do_atlas()
    master = do_master()
    com_ficha = {f["source_id"] for f in fontes}
    so_em_tabela = [c for c in citadas_sem_ficha() if c["source_id"] not in com_ficha]
    contratos = dos_contratos()
    for f in fontes:
        f["contract"] = contratos.get(f["source_id"])
        f["sabe_coletar"] = bool(f["contract"])

    head = subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    por_pais: dict[str, int] = {}
    por_verdict: dict[str, int] = {}
    for f in fontes:
        por_pais[f["country"]] = por_pais.get(f["country"], 0) + 1
        por_verdict[f["verdict"]] = por_verdict.get(f["verdict"], 0) + 1

    dados = {
        "SCHEMA": "sintonia.system-map.sources/1",
        "PROVENANCE": {"HEAD": head, "ATLAS": ATLAS, "CONTRATOS": CONTRATOS},
        "SOURCES": fontes,
        "CITADAS_SEM_FICHA": so_em_tabela,
        "MASTER_ITALIANO": master,
        "RECONCILIACAO": reconciliar(fontes, master, so_em_tabela),
        "ACCOUNTS": as_contas(),
        "INTAKE": a_porta(fontes, contratos),
        "SEARCH_TERMS": as_palavras(arquivos),
        "MEMORIA_DA_COLETA": memoria_da_coleta(arquivos),
        "COLETAS_FEITAS": coletas_feitas(fontes),
        "COLETAS_ITALIANAS": coletas_italianas(),
        "ENDPOINTS": as_portas(arquivos),
        "COUNTS": {
            "sources": len(fontes),
            "with_contract": sum(1 for f in fontes if f["sabe_coletar"]),
            "by_country": dict(sorted(por_pais.items())),
            "by_verdict": dict(sorted(por_verdict.items())),
        },
    }
    dados["COUNTS"]["search_term_groups"] = sum(
        len(t["grupos"]) for t in dados["SEARCH_TERMS"])
    dados["COUNTS"]["search_terms"] = sum(
        t["total_palavras"] for t in dados["SEARCH_TERMS"])
    dados["COUNTS"]["endpoints"] = len(dados["ENDPOINTS"])
    dados["COUNTS"]["candidates"] = len(dados["INTAKE"]["candidatas"])
    M = dados["MEMORIA_DA_COLETA"]
    dados["COUNTS"]["coletores"] = len(M)
    dados["COUNTS"]["coletores_com_data"] = sum(1 for m in M if m["carimba_data"])
    dados["COUNTS"]["coletores_com_lugar"] = sum(1 for m in M if m["carimba_lugar"])
    dados["COUNTS"]["coletores_que_separam_fonte_do_fato"] = sum(
        1 for m in M if m["separa_fonte_do_fato"])
    dados["COUNTS"]["coletores_que_registam_descarte"] = sum(
        1 for m in M if m["regista_descarte"])
    F = dados["COLETAS_FEITAS"]
    I = dados["COLETAS_ITALIANAS"]
    dados["COUNTS"]["corridas_registadas"] = F.get("total", 0) + I.get("corridas", 0)
    dados["COUNTS"]["observacoes_registadas"] = I.get("observacoes", 0)
    dados["COUNTS"]["fontes_ja_coletadas"] = len(F.get("fontes_ja_coletadas", []))
    dados["COUNTS"]["fontes_nunca_coletadas"] = len(F.get("fontes_nunca_coletadas", []))
    dados["COUNTS"]["citadas_sem_ficha"] = len(so_em_tabela)
    R = dados["RECONCILIACAO"]
    dados["COUNTS"]["fontes_no_master_italiano"] = len(master)
    dados["COUNTS"]["fontes_distintas"] = R["total_distintas"]
    dados["COUNTS"]["levantadas_sem_ficha"] = len(R["so_no_master_italiano"])

    # O cruzamento que dói: das fontes que foram MESMO coletadas, quantas nao
    # tem ficha? Cada uma destas e uma descoberta que vai ser refeita do zero.
    coletadas = set(F.get("fontes_ja_coletadas", []))
    sem_ficha_e_coletadas = sorted(coletadas & {c["source_id"] for c in so_em_tabela})
    dados["COLETADAS_SEM_FICHA"] = sem_ficha_e_coletadas
    dados["COUNTS"]["coletadas_sem_ficha"] = len(sem_ficha_e_coletadas)
    dados["COUNTS"]["accounts"] = dados["ACCOUNTS"].get("total", 0)
    dados["COUNTS"]["accounts_authorized"] = dados["ACCOUNTS"].get("autorizadas", 0)

    # A DIVERGENCIA, dita na cara. Nao corrijo o documento nem escondo o numero:
    # registo os dois e deixo a diferenca visivel, porque quem tem de decidir o
    # que fazer com ela e gente, nao este script.
    decl = contagem_declarada()
    if decl:
        dados["HEADER_CLAIM"] = {
            **decl,
            "fichas_completas": len(fontes),
            "divergencia": decl["total"] - len(fontes),
            "leitura": (
                f"O cabecalho do atlas diz {decl['total']} fontes registradas; "
                f"fichas completas, com SOURCE_ID valido, ha {len(fontes)}. "
                f"Faltam {decl['total'] - len(fontes)} fichas — as fontes podem "
                f"existir, mas sem ficha ninguem consegue saber o que elas tem."
            ) if decl["total"] != len(fontes) else "O cabecalho bate com as fichas.",
        }
        if decl["total"] != len(fontes):
            print(f"  ATENCAO: cabecalho diz {decl['total']} fontes, fichas completas sao "
                  f"{len(fontes)} (faltam {decl['total'] - len(fontes)})")

    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    c = dados["COUNTS"]
    print(f"  contas de rede social: {c['accounts']} "
          f"({c['accounts_authorized']} autorizadas) em "
          f"{len(dados['ACCOUNTS'].get('por_plataforma', {}))} plataformas")
    print(f"  memoria da coleta: {c['coletores']} coletores · "
          f"{c['coletores_com_data']} carimbam data · "
          f"{c['coletores_com_lugar']} carimbam lugar · "
          f"{c['coletores_que_separam_fonte_do_fato']} separam fonte do fato · "
          f"{c['coletores_que_registam_descarte']} registam o descarte")
    if master:
        print(f"  levantamento italiano: {len(master)} fontes · "
              f"{len(dados['RECONCILIACAO']['nos_dois'])} tambem no atlas · "
              f"{len(dados['RECONCILIACAO']['so_no_master_italiano'])} so no levantamento")
    if so_em_tabela:
        print(f"  ATENCAO: {len(so_em_tabela)} fonte(s) citadas em tabela, sem ficha: "
              + ", ".join(c["source_id"] for c in so_em_tabela[:8]))
    if dados["COUNTS"].get("coletadas_sem_ficha"):
        print(f"  ATENCAO: {dados['COUNTS']['coletadas_sem_ficha']} destas JA FORAM "
              f"COLETADAS: {', '.join(dados['COLETADAS_SEM_FICHA'])}")
    if I.get("observacoes"):
        print(f"  registo italiano: {I['observacoes']} observacoes em {I['corridas']} "
              f"corridas · {I['com_sha256']} com SHA256 · {I['com_fact_time']} com "
              f"FACT_TIME · {I['com_cadencia']} com cadencia")
    if F.get("total"):
        print(f"  coletas ja feitas: {F['total']} corridas · "
              f"{c['fontes_ja_coletadas']} fontes ja coletadas, "
              f"{c['fontes_nunca_coletadas']} nunca · "
              f"trouxe {F['trouxe_total']} e sobrou {F['sobrou_total']}")
        print(f"     por pais: " + " · ".join(f"{k}={v}" for k, v in F["por_pais"].items()))
    print(f"COLETA=OK · fontes={c['sources']} (com contrato de busca: {c['with_contract']}) "
          f"· palavras={c['search_terms']} em {c['search_term_groups']} grupos "
          f"· portas={c['endpoints']}")
    print("  por pais:    " + " · ".join(f"{k}={v}" for k, v in c["by_country"].items()))
    print("  por veredito:" + " · ".join(f" {k}={v}" for k, v in c["by_verdict"].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
