#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MICRO-PROVA — plano (SEM rede) das rondas de prova para as candidatas que esperam território.

    py curadoria/micro_prova_plano.py <BLOQUEADAS-268-V1.json>   ->  curadoria/MICRO-PROVA-PLANO-V1.json

Entra: as linhas PRECISA_DECISAO (80) e MESMO_SITE_CLASSES_MISTAS (9) da classificação BLOQUEADAS-268.
Regras (as da casa, nada novo):
  · prova de território = a do canal DECISOES-SEMANTICAS-V1 (curadoria/decisao_semantica.py): ≥1 página
    INSTITUCIONAL/LEI + ≥2 páginas de CONTEÚDO, URLs distintos, cada uma com sha256 — 3 pedidos de página;
  · teto D38: ≤5 pedidos por DOMÍNIO por ronda, robots.txt incluído → 1 robots + 3 páginas = 1 candidata por
    domínio por ronda (sobra 1 pedido, que NÃO se usa: margem para um redireccionamento);
  · robots.txt lido e cumprido; «Visit-time» (Rete Rurale 01–03 UTC) marcado como janela;
  · portão de egresso IT por consenso antes de cada ronda.
Não pede nada à rede. O plano diz, por candidata: domínio, ronda, pedidos previstos, e o que conta como prova
para cada gaveta (tabela GAVETAS).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "curadoria" / "MICRO-PROVA-PLANO-V1.json"
TETO_DOMINIO = 5
PAGINAS_POR_PROVA = 3            # 1 institucional + 2 conteúdos

# O que conta como prova, por gaveta (Atlas: atribuir_source_id.py + docs). A página INSTITUCIONAL diz o que a
# fonte É; as duas de CONTEÚDO mostram que ela PUBLICA disso — uma só não chega (medido: 1 item fabrica território).
GAVETAS = {
    "T1":  ("CROP & PRODUCTION", "produtor, OP, consórcio de produção ou de tutela (chi siamo / statuto)",
            "notícias de campanha, produção, colheita, qualidade do produto"),
    "T2":  ("CLIMATE / WATER / SOIL", "serviço meteorológico, agrometeo, ARPA, consórcio de bonifica",
            "boletins meteo/agrometeo, dados de água ou solo, datados"),
    "T3":  ("PEST / DISEASE / WEEDS", "serviço fitossanitário, consórcio de defesa",
            "boletins/avisos fitossanitários datados"),
    "T4":  ("REGULATORY", "órgão que emite ou compila norma (ministério, gazzetta, registo)",
            "decretos, circulares, registos de produtos"),
    "T5":  ("SCIENCE", "universidade, departamento, instituto de pesquisa (CNR, CREA…)",
            "publicações, projetos, resultados de pesquisa"),
    "T6":  ("RESEARCHERS", "página oficial da PESSOA na instituição (D21/D24)",
            "produção da pessoa (artigos, ensaios, apresentações)"),
    "T7":  ("TECHNICAL NETWORK", "associação, cooperativa, ordem profissional, federação (statuto / chi siamo)",
            "notícias técnicas, circulares aos membros, eventos técnicos"),
    "T8":  ("FARMERS & INFLUENCERS / MEDIA", "redação/testata (registo de imprensa, direção)",
            "artigos agrícolas publicados pela redação"),
    "T9":  ("COMPETITORS", "empresa (P.IVA, chi siamo, catálogo)", "comunicados e notícias da empresa"),
    "T10": ("MARKET / TRADE / INDUSTRY", "bolsa, câmara de comércio, observatório de preços",
            "cotações ou análises de mercado datadas"),
    "T11": ("FAIRS / EVENTS", "organizador da feira (edição, datas, local)", "programa, expositores, notícias da edição"),
    "T12": ("PUBLIC ADMINISTRATION", "ente público (região, província, agência regional)",
            "atos, avisos e notícias da secção agrícola"),
}


def dominio(u: str) -> str:
    return urlparse(u or "").netloc.lower().removeprefix("www.")


def planear(linhas: list[dict]) -> dict:
    alvo = [l for l in linhas if l["PROPOSTA"] in ("PRECISA_DECISAO", "MESMO_SITE_CLASSES_MISTAS")]
    por_dom = defaultdict(list)
    for l in alvo:
        por_dom[dominio(l["URL"])].append(l)
    plano = []
    for dom, ls in sorted(por_dom.items(), key=lambda x: (-len(x[1]), x[0])):
        for i, l in enumerate(sorted(ls, key=lambda x: x["ID"])):
            janela = "01:00-03:00 UTC (Visit-time do robots)" if l.get("DECISAO_SEMANTICA") == "JANELA_DO_ROBOTS" else None
            plano.append({"ID": l["ID"], "NOME": l.get("NOME"), "URL": l.get("URL"), "DOMINIO": dom,
                          "RONDA_NO_DOMINIO": i + 1, "PEDIDOS": 1 + PAGINAS_POR_PROVA,
                          "PAIS_DA_FICHA": l.get("PAIS"), "TIPO_DA_FICHA": l.get("TIPO"),
                          "REVISAO_ANTERIOR": l.get("DECISAO_SEMANTICA"), "GRUPO": l["PROPOSTA"],
                          "JANELA": janela})
    rondas = max((p["RONDA_NO_DOMINIO"] for p in plano), default=0)
    por_ronda = Counter(p["RONDA_NO_DOMINIO"] for p in plano)
    return {"DATASET": "MICRO-PROVA-PLANO-V1", "CANDIDATAS": len(plano), "DOMINIOS": len(por_dom),
            "PEDIDOS_PREVISTOS": sum(p["PEDIDOS"] for p in plano),
            "MAX_PEDIDOS_POR_DOMINIO_POR_RONDA": 1 + PAGINAS_POR_PROVA, "TETO_D38": TETO_DOMINIO,
            "RONDAS": rondas, "CANDIDATAS_POR_RONDA": dict(sorted(por_ronda.items())),
            "DOMINIOS_COM_MAIS_DE_UMA": {d: len(v) for d, v in sorted(por_dom.items(), key=lambda x: -len(x[1]))
                                         if len(v) > 1},
            "PAIS_DA_FICHA": dict(Counter(p["PAIS_DA_FICHA"] for p in plano)),
            "GAVETAS": {k: {"NOME": n, "INSTITUCIONAL": i, "CONTEUDO": c} for k, (n, i, c) in GAVETAS.items()},
            "PLANO": plano}


def main():
    linhas = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["LINHAS"]
    out = planear(linhas)
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for k in ("CANDIDATAS", "DOMINIOS", "PEDIDOS_PREVISTOS", "RONDAS", "CANDIDATAS_POR_RONDA",
              "DOMINIOS_COM_MAIS_DE_UMA", "PAIS_DA_FICHA"):
        print(k, out[k])


if __name__ == "__main__":
    main()
