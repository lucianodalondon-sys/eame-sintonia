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
FILA = "data/samples/FONTES-CANDIDATAS.json"


def a_porta(fontes: list, contratos: dict) -> dict:
    """Mede em que degrau esta cada fonte, e o que ha na fila de entrada.

    O acervo de fontes e capital parado: consulta-se antes de coletar. Mas capital
    parado sem porta apodrece — fonte nova aparece no meio de uma coleta e morre no
    historico do terminal de quem a viu. A porta e `scripts/fonte_nova.py`, e o que
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
        "porta": "scripts/fonte_nova.py",
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
        "ACCOUNTS": as_contas(),
        "INTAKE": a_porta(fontes, contratos),
        "SEARCH_TERMS": as_palavras(arquivos),
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
    print(f"COLETA=OK · fontes={c['sources']} (com contrato de busca: {c['with_contract']}) "
          f"· palavras={c['search_terms']} em {c['search_term_groups']} grupos "
          f"· portas={c['endpoints']}")
    print("  por pais:    " + " · ".join(f"{k}={v}" for k, v in c["by_country"].items()))
    print("  por veredito:" + " · ".join(f" {k}={v}" for k, v in c["by_verdict"].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
