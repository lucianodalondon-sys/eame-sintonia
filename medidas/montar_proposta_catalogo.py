#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROPOSTA DE CORRECCAO DO CATALOGO T2/T12 — para o dono decidir (D5). NADA E APLICADO.

    NUNCA PROPOR SEM PROVA. DUVIDA = UNKNOWN.

Le SO provas ja guardadas (sem rede):
  curadoria/CATALOGO-PROVA-V1.json   paginas de entrada (egresso IT 51/51)
  curadoria/GABARITO-T2-T12-V2/V3    itens julgados a mao (D2)
  data/samples/IT-SOURCE-SAMPLES     acervo versionado (T2-001/002/004)
  curadoria/ROTAS-ELEGIVEIS-V1.json  canario da 3b (IT-T7-043)

REGRAS
  MANTER               a pagina prova o universo
  MUDAR_PARA_Tx        a pagina prova outro universo
  RETIRAR_DO_UNIVERSO  a pagina prova administracao/saude/impostos/contactos,
                       subpagina de um publicador ja catalogado, ou noticia
                       avulsa registada como se fosse fonte
  UNKNOWN              sem pagina guardada, pagina sem corpo, ou duvida. O que
                       o nome/endereco sugere vai em INDICIO_DO_CATALOGO e NAO
                       decide nada

As decisoes por fonte (tabela D) foram escritas a mao depois de ler cada
pagina; o PORQUE de cada uma vai na linha. Uma decisao sem prova e rebaixada a
UNKNOWN pelo proprio codigo.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
CUR = RAIZ / "curadoria"
SAIDA = CUR / "PROPOSTA-CATALOGO-V1.json"
PROVAS_EM = Path.home() / "sintonia-gabarito"
LIVRO = "origin/lote-76-v1"

R, M, U = "RETIRAR_DO_UNIVERSO", "MANTER", "UNKNOWN"
ADM = "pagina administrativa/institucional sem assunto agricola nem climatico"
SUB = "subpagina institucional de um publicador que ja esta no catalogo"
ITEM = "noticia avulsa registada como fonte; o publicador ja esta no catalogo"

D = {
    "IT-T2-001": (M, None, "boletim agrometeorologico regional (acervo)"),
    "IT-T2-002": (M, None, "boletim meteo do Veneto (V3) e boletins agrometeo (acervo)"),
    "IT-T2-004": (M, None, "dados de precipitacao diaria SIAS (acervo)"),
    "IT-T2-006": (M, None, "agencia ambiental regional; paginas lidas institucionais — rendimento T2 baixo"),
    "IT-T2-007": (M, None, "agencia ambiental; noticias de ar e mar — rendimento T2 baixo"),
    "IT-T2-008": (M, None, "agencia ambiental; a entrada so deu paginas institucionais"),
    "IT-T2-009": (M, None, "instituto nacional do ambiente; noticias de eventos (agua) — rendimento T2 baixo"),
    "IT-T2-010": (M, None, "agencia ambiental; ozono, dados — rendimento T2 baixo"),
    "IT-T2-011": (M, None, "agencia ambiental; a entrada so deu paginas institucionais"),
    "IT-T2-013": (M, None, "rede micrometeorologica, solos (V2)"),
    "IT-T2-014": (M, None, "agencia ambiental; emissoes, odores — rendimento T2 baixo"),
    "IT-T2-015": (M, None, "associacao de agrometeorologia (brochura: agrometeo, balancos hidricos)"),
    "IT-T2-016": (M, None, "agencia ambiental; a entrada so deu paginas institucionais"),
    "IT-T2-017": ("MUDAR_PARA_T5", None, "instituto de investigacao: linhas de pesquisa em plantas e ecossistemas"),
    "IT-T2-018": (U, None, "so navegacao e webcam lidas"),
    "IT-T2-020": (M, None, "agencia ambiental; carta da natureza — rendimento T2 baixo"),
    "IT-T2-021": (M, None, "verao 2026 de calor recorde (V2)"),
    "IT-T2-022": (M, None, "agencia ambiental; so paginas institucionais lidas"),
    "IT-T2-024": (M, None, "consorcios de bonifica e irrigacao (agua)"),
    "IT-T2-029": (M, None, "agencia ambiental; ar, wind day — rendimento T2 baixo"),
    "IT-T2-030": ("MUDAR_PARA_T10", None, "consultoria e observatorios de mercado; noticias de credito e mobilidade"),
    "IT-T2-031": (M, "IT-T2-013 (mesmo sitio)", "homepage da agencia ambiental"),
    "IT-T2-032": (M, "IT-T2-021 (mesmo sitio)", "homepage da agencia ambiental"),
    "IT-T2-033": (M, "IT-T2-011 (mesmo sitio)", "homepage da agencia ambiental"),
    "IT-T2-034": (M, "IT-T2-016 (mesmo sitio)", "noticias ambientais (polens, algas)"),
    "IT-T2-037": (M, "IT-T2-008 (mesmo sitio)", "homepage da agencia ambiental"),
    "IT-T2-038": (M, None, "boletins meteorologicos oficiais (3 positivos)"),
    "IT-T2-039": (R, None, ITEM + " (IT-T2-051)"),
    "IT-T2-043": (M, None, "seccao 'Acqua' da agencia ambiental"),
    "IT-T2-049": (M, "IT-T2-007 (mesmo sitio)", "homepage da agencia ambiental"),
    "IT-T2-050": (M, "IT-T2-006 (mesmo sitio)", "homepage da agencia ambiental"),
    "IT-T2-051": (M, None, "agencia ambiental; itens lidos institucionais/balneares — rendimento T2 baixo"),
    "IT-T2-052": (R, None, SUB), "IT-T2-055": (R, None, SUB), "IT-T2-057": (R, None, SUB),
    "IT-T2-054": (U, None, "seletor de idioma: pagina sem corpo"),
    "IT-T2-060": (R, None, SUB + "; serve como INDEX_URL de IT-T2-037"),
    "IT-T2-062": (R, None, SUB), "IT-T2-065": (R, None, SUB),
    "IT-T2-070": (R, None, "perfil do mesmo publicador noutra plataforma (Issuu)"),
    "IT-T12-003": (M, None, "CIA: politica de uso do solo agricola (V3)"),
    "IT-T12-006": (M, None, "CIA Toscana: comunicados de politica agricola (3 positivos)"),
    "IT-T12-009": (U, None, "pagina de cortesia: a ASSAM passou a chamar-se AMAP — rever o endereco"),
    "IT-T12-018": ("MUDAR_PARA_T7", None, "agencia de desenvolvimento agricola: assistencia tecnica as empresas (V2)"),
    "IT-T12-019": ("MUDAR_PARA_T7", None, "servicos a agricultura: jornadas de demonstracao em campo (V2)"),
    "IT-T12-020": (M, None, "ministerio da agricultura: nucleo de T12; a entrada so deu paginas de concurso"),
    "IT-T12-021": (U, None, "pagina sem corpo (conteudo por JavaScript)"),
    "IT-T12-022": (U, None, "a entrada e o portal geral da Regiao, nao a seccao agricola"),
    "IT-T12-023": (U, None, "a entrada agricola so deu o menu geral do portal"),
    "IT-T12-024": (M, None, "portal agricola: Natura 2000 e areas protegidas (politica agro-ambiental)"),
    "IT-T12-025": (U, None, "a entrada e o portal geral da Regiao"),
    "IT-T12-026": (M, None, "Pianeta PSR: PAC e desenvolvimento rural (3 positivos)"),
    "IT-T12-027": (R, None, "agencia regional de mobilidade: concurso publico"),
    "IT-T12-028": (M, None, "CSR Campania 2023-2027 (PAC)"),
    "IT-T12-029": ("MUDAR_PARA_T2", None, "alertas e boletins meteo da protecao civil"),
    "IT-T12-030": (R, None, ADM), "IT-T12-033": (R, None, ADM), "IT-T12-034": (R, None, ADM),
    "IT-T12-035": (R, None, ADM),
    "IT-T12-031": (U, None, "pagina sem corpo"), "IT-T12-032": (U, None, "pagina sem corpo"),
    "IT-T12-036": (U, None, "pagina sem corpo (intranet)"),
    "IT-T12-037": (R, None, ADM + " (assembleia legislativa)"),
    "IT-T12-038": (U, None, "boletim oficial geral; nao lido item a item"),
    "IT-T12-039": (R, None, "concursos, portais e emprego (V2)"),
    "IT-T12-040": (R, None, ADM + " (concursos gerais)"),
    "IT-T12-041": (R, None, "boletim oficial geral: 0 de 3 com ato agricola; 'PAC' = Piano Attuativo Comunale"),
    "IT-T12-042": (U, None, "so a pagina de pesquisa foi lida"),
    "IT-T12-043": (R, None, ADM + " (imposto automovel)"),
    "IT-T12-044": (R, None, ITEM), "IT-T12-064": (R, None, ITEM), "IT-T12-080": (R, None, ITEM),
    "IT-T12-045": (U, None, "pagina sem corpo"),
    "IT-T12-047": (R, None, ADM), "IT-T12-048": (R, None, ADM),
    "IT-T12-049": (R, None, "cultura e museus (V2)"),
    "IT-T12-050": (U, None, "pagina sem corpo"), "IT-T12-051": (U, None, "pagina sem corpo"),
    "IT-T12-052": (R, None, "saude (vacinas)"), "IT-T12-053": (R, None, ADM + " (eleicoes)"),
    "IT-T12-054": (R, None, "politica de coesao, regeneracao urbana, aeroporto (V2)"),
    "IT-T12-056": (R, None, "saude (ficha sanitaria)"),
    "IT-T12-057": (R, None, "juventude (V2/V3)"),
    "IT-T12-067": (U, None, "HTTP 422"),
    "IT-T12-069": (R, None, "turismo e cultura (V2)"),
    "IT-T12-070": (R, None, "monitorizacao geral do PNRR"),
    "IT-T12-071": (U, None, "pagina sem corpo"),
    "IT-T12-073": (R, None, "jogos olimpicos (V2)"),
    "IT-T12-074": (R, None, "inovacao e startups (V2/V3)"),
    "IT-T12-075": (R, None, "educacao"),
    "IT-T12-076": (R, None, "PNRR geral; 1 item sobre barragem/irrigacao foi para T2 por REROUTE"),
    "IT-T12-077": (U, None, "pagina sem corpo"),
    "IT-T12-081": (U, None, "programacao europeia: menciona o PSR, mas as paginas lidas eram coesao urbana"),
    "IT-T12-086": (R, None, "saude"), "IT-T12-087": (R, None, "saude"),
    "IT-T12-092": (R, None, ADM + " (catalogo de servicos digitais)"),
    "IT-T12-094": (U, None, "so rodape"),
    "IT-T12-095": (R, None, "hub de sitios regionais"),
    "IT-T12-098": (R, None, ADM + " (imposto automovel)"),
    "IT-T12-103": (U, None, "pagina sem corpo"),
    "IT-T12-104": (U, None, "geoportal: pagina sem corpo (podia servir T2)"),
    "IT-T12-105": (R, None, "portal geral da Regiao; itens institucionais (V2)"),
    "IT-T12-107": (U, None, "pagina sem corpo"),
    "IT-T12-108": (R, None, SUB + " (IT-T12-018)"), "IT-T12-109": (R, None, SUB + " (IT-T12-018)"),
    "IT-T12-122": (R, None, SUB + " (IT-T12-018)"),
    "IT-T12-112": (R, None, SUB + " (IT-T12-009)"), "IT-T12-114": (R, None, SUB + " (IT-T12-009)"),
    "IT-T12-124": (R, None, SUB + " (IT-T12-009)"),
    "IT-T12-125": ("MUDAR_PARA_T2", None, "cartas de solos e zonas vulneraveis a nitratos (V2)"),
    "IT-T7-043": ("MUDAR_PARA_T9", None, "associacao das empresas de defensivos (os pares da ADAMA)"),
}

SINAL = re.compile(r"agric|rural|psr|\bpac\b|agro|masaf|arsac|assam|ersa|confagri|\bcia\b|aiab|"
                   r"meteo|clima|acqu|suol|irrig", re.I)

FALTAM = [
    {"FONTE": "AGEA — Agenzia per le Erogazioni in Agricoltura (paga a PAC)",
     "NO_CATALOGO": "NAO", "NAS_CANDIDATAS": "so via SIAN (sian.it), sem SOURCE_ID"},
    {"FONTE": "CREA-PB — Centro Politiche e Bioeconomia",
     "NO_CATALOGO": "NAO (o CREA tem 14 centros no livro, todos T5; o PB nao esta)", "NAS_CANDIDATAS": "NAO"},
    {"FONTE": "Rete Rurale Nazionale (reterurale.it)",
     "NO_CATALOGO": "so o canal YouTube IT-T12-011 e a revista Pianeta PSR IT-T12-026",
     "NAS_CANDIDATAS": "sim (12 mencoes a reterurale/pianetapsr)"},
    {"FONTE": "ISMEA", "NO_CATALOGO": "NAO no livro; no Atlas como IT-T10-007 (mercado)",
     "NAS_CANDIDATAS": "NAO", "NOTA": "publica tambem analise da PAC; decidir se ganha ficha T12"},
    {"FONTE": "Agriregionieuropa (revista de economia e politica agraria)",
     "NO_CATALOGO": "NAO", "NAS_CANDIDATAS": "NAO"},
    {"FONTE": "MASAF — seccao de comunicados", "NO_CATALOGO": "a fonte existe (IT-T12-020), mas a "
     "entrada so deu paginas de concurso; falta o INDEX_URL das noticias", "NAS_CANDIDATAS": "—"},
    {"FONTE": "Coldiretti, CIA nacional, Confagricoltura, Copagri",
     "NO_CATALOGO": "SIM, mas em T7 (11 fontes)", "NAS_CANDIDATAS": "sim",
     "NOTA": "publicam sobretudo posicoes de politica agricola; pela lei D2 os itens podem ir "
             "para T12 por REROUTE sem mudar a gaveta da fonte"},
]


def _json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def fontes() -> dict:
    r = subprocess.run(["git", "show", "%s:curadoria/italy_contracts_curator.json" % LIVRO],
                       capture_output=True, cwd=RAIZ)
    F = {x["SOURCE_ID"]: x for x in json.loads(r.stdout)["FONTES"]
         if x["SOURCE_ID"].startswith(("IT-T2-", "IT-T12-"))}
    atlas = (RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md").read_text(encoding="utf-8")
    for m in re.finditer(r"^#### (IT-T(?:2|12)-\d+) · ([^\n]*)\n(.*?)(?=^#### |\Z)", atlas, re.S | re.M):
        if m.group(1) not in F:
            u = re.search(r"^URL:\s+(\S+)", m.group(3), re.M)
            F[m.group(1)] = {"SOURCE_ID": m.group(1), "NAME": m.group(2),
                             "CANONICAL_ENTRY_URL": u.group(1) if u else "", "_ATLAS": True}
    F["IT-T7-043"] = {"SOURCE_ID": "IT-T7-043", "NAME": "Agrofarma — Federchimica",
                      "CANONICAL_ENTRY_URL": "https://agrofarma.federchimica.it/"}
    return F


def provas(F: dict) -> dict:
    prov = {}

    def add(s, orig, url, sha, rot="", ficheiro=None):
        prov.setdefault(s, []).append({"ORIGEM": orig, "URL": url, "SHA256": sha, "ROTULO": rot,
                                       "FICHEIRO": ficheiro})

    for p in _json(CUR / "CATALOGO-PROVA-V1.json")["PAGINAS"]:
        if p.get("SHA256"):
            add(p["SOURCE_ID"], "CATALOGO-PROVA-V1", p["URL"], p["SHA256"], "",
                p.get("FICHEIRO_FORA_DO_GIT"))
    por_url = {x["CANONICAL_ENTRY_URL"].rstrip("/"): s for s, x in F.items()}
    for v in ("V2", "V3"):
        for i in _json(CUR / ("GABARITO-T2-T12-%s.json" % v))["ITENS"]:
            rot = ("%s/%s/%s" % (i.get("UNIVERSO_DO_CONTEUDO"), i.get("UNIVERSE_MATCH"),
                                 i.get("SINTONIA_RELEVANT")) if i.get("UTILIZAVEL") else "INUTILIZAVEL")
            add(i["SOURCE_ID"], "GABARITO-" + v, i["URL"], i["SHA256"], rot,
                i.get("FICHEIRO_FORA_DO_GIT"))
            s2 = por_url.get(i["URL"].rstrip("/"))
            if s2 and s2 != i["SOURCE_ID"]:
                add(s2, "GABARITO-%s (o item e a entrada desta fonte)" % v, i["URL"], i["SHA256"], rot,
                    i.get("FICHEIRO_FORA_DO_GIT"))
    for s, f in [("IT-T2-001", "data/samples/IT-SOURCE-SAMPLES/IT-T2-001/35_boll_agro_20260831.pdf"),
                 ("IT-T2-002", "data/samples/IT-SOURCE-SAMPLES/IT-T2-002/agro_01.pdf"),
                 ("IT-T2-004", "data/samples/IT-SOURCE-SAMPLES/IT-T2-004/NHEOWL0530_00.html")]:
        h = hashlib.sha256((RAIZ / f).read_bytes()).hexdigest()
        # copia com o nome pelo sha em ~/sintonia-gabarito/ACERVO-GIT, para a
        # prova se conferir no MESMO sitio que as outras
        add(s, "ACERVO_GIT", f, h, "T2/YES/YES",
            str(PROVAS_EM / "ACERVO-GIT" / (h[:16] + Path(f).suffix)))
    for l in _json(CUR / "ROTAS-ELEGIVEIS-V1.json")["LINHAS"]:
        if l["SOURCE_ID"] == "IT-T7-043":
            # ⚠️ o canario da 3b guardou o sha do TEXTO, nao os bytes: nao ha
            # ficheiro. Fica registado, e a conferencia abaixo rebaixa a accao.
            add("IT-T7-043", "CANARIO_3B", l["CANARIO"]["URL"],
                "TEXT_SHA256:" + l["CANARIO"]["TEXT_SHA256"], "biocontrolo", None)
    return prov


def prova_confere(p: dict) -> bool:
    """A prova existe em disco com o sha256 que declara? Sem ficheiro = nao."""
    f = p.get("FICHEIRO")
    if not f or not Path(f).is_file():
        return False
    return hashlib.sha256(Path(f).read_bytes()).hexdigest() == p.get("SHA256")


def main() -> int:
    F = fontes()
    prov = provas(F)
    linhas = []
    chave = lambda s: (s.split("-")[1], int(s.split("-")[2]))
    for s in sorted(F, key=chave):
        x, pv = F[s], prov.get(s, [])
        conferidas = [p for p in pv if prova_confere(p)]
        if s in D and pv and len(conferidas) < len(pv):
            # PROVA DECLARADA SEM FICHEIRO QUE A CONFIRA: a accao nao sobrevive.
            a, dup = U, None
            why = ("rebaixada a UNKNOWN: %d de %d provas sem ficheiro com o sha256 declarado "
                   "(%s). Decisao lida: %s — %s" % (len(pv) - len(conferidas), len(pv),
                   ", ".join(p["ORIGEM"] for p in pv if p not in conferidas), D[s][0], D[s][2]))
        elif s in D and pv:
            a, dup, why = D[s]
        else:
            a, dup = U, None
            why = "sem pagina guardada" + (" (YouTube nao aberto: 429)"
                                           if "youtube" in x.get("CANONICAL_ENTRY_URL", "") else "")
        ind = None
        if a == U:
            # so o NOME e o CAMINHO: o anfitriao (arsacweb, assam) marcaria como
            # agricola a pagina de privacy do mesmo sitio
            n = x.get("NAME", "") + " " + urlparse(x.get("CANONICAL_ENTRY_URL", "")).path
            ind = ("o nome/endereco sugere assunto agricola ou climatico" if SINAL.search(n)
                   else "o nome/endereco sugere pagina administrativa ou geral")
        linhas.append({"SOURCE_ID": s, "UNIVERSO_ACTUAL": s.split("-")[1],
                       "NOME": " ".join(x.get("NAME", "").split())[:120],
                       "ENTRADA": x.get("CANONICAL_ENTRY_URL"),
                       "ORIGEM_NO_CATALOGO": "ATLAS" if x.get("_ATLAS") else LIVRO,
                       "ACCAO": a, "PORQUE": why, "DUPLICADA_DE": dup,
                       "INDICIO_DO_CATALOGO": ind, "PROVA": pv})
    t12 = [l["SOURCE_ID"] for l in linhas if l["UNIVERSO_ACTUAL"] == "T12" and l["ACCAO"] == M]
    t12_talvez = [l["SOURCE_ID"] for l in linhas if l["UNIVERSO_ACTUAL"] == "T12" and l["ACCAO"] == U
                  and l["INDICIO_DO_CATALOGO"].startswith("o nome/endereco sugere assunto")]
    t2 = [l["SOURCE_ID"] for l in linhas if l["UNIVERSO_ACTUAL"] == "T2" and l["ACCAO"] == M
          and not l["DUPLICADA_DE"]]
    d = {"DATASET": "PROPOSTA-CATALOGO-V1",
         "ESTADO": "PROPOSTA — NADA APLICADO; decide o dono (D5)",
         "INSTRUMENTO": "medidas/montar_proposta_catalogo.py (sem rede)",
         "BYTES_FORA_DO_GIT": "~/sintonia-gabarito/{GABARITO-T2-T12-V2,GABARITO-T2-T12-V3,CATALOGO-PROVA-V1}",
         "CONTAGEM": {"FONTES": len(linhas), "POR_ACCAO": dict(Counter(l["ACCAO"] for l in linhas)),
                      "POR_UNIVERSO": {u: dict(Counter(l["ACCAO"] for l in linhas
                                                       if l["UNIVERSO_ACTUAL"] == u))
                                       for u in ("T2", "T12", "T7")}},
         "TRES_NUMEROS": {
             "1_T12_AGRICOLAS_DE_VERDADE_PROVADAS": {"N": len(t12), "IDS": t12,
                                                     "POSSIVEIS_SEM_PROVA": t12_talvez},
             "2_POSITIVOS_ATINGIVEIS_SO_COM_ESSAS": {
                 "T12_OBTIDOS_EM_3_IDAS": 9, "T12_TETO_POR_IDA": 3 * len(t12),
                 "T2_OBTIDOS_EM_3_IDAS": 13, "T2_FONTES_MANTER_SEM_DUPLICADO": len(t2),
                 "T2_TETO_POR_IDA": 3 * len(t2),
                 "NOTA": "teto = 3 materias por sitio por ida (o limite autorizado). O observado "
                         "ficou muito abaixo do teto: as paginas de entrada levam primeiro a administracao"},
             "3_T12_CHEGA_A_20_SEM_FONTES_NOVAS": {
                 "RESPOSTA": ("NAO numa ida: o teto e %d e o observado em 3 idas foi 9. So se "
                              "chegaria acumulando idas ao longo do tempo, e isso nao esta garantido"
                              % (3 * len(t12))),
                 "FONTES_REAIS_EM_FALTA": FALTAM}},
         "LINHAS": linhas}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(d["CONTAGEM"], ensure_ascii=False))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "FONTES_REAIS_EM_FALTA"}
                      for k, v in d["TRES_NUMEROS"].items()}, ensure_ascii=False))
    print("accao sem prova:", [l["SOURCE_ID"] for l in linhas if l["ACCAO"] != U and not l["PROVA"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
