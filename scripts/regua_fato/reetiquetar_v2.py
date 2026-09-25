#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REGUA-FATO · ADENDA 1 (D71-D73): reetiqueta o gabarito e a cega na taxonomia v2 (agro_fact_kind).

    py scripts/regua_fato/reetiquetar_v2.py

Le os rotulos v1 e escreve, em cada item, AGRO_FACT_KIND (v2), MUDOU_POR (a decisao que mudou) e,
para MARKETING_CONCORRENCIA, EMPRESA / PRODUTO / QUEM_FALOU. O rotulo v1 fica em FACT_KIND_V1.
Cada troca foi decidida a ler o texto (nao o classificador). VALIDADO_POR_HUMANO = NAO.
"""
import json
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).parent
MK = "MARKETING_CONCORRENCIA"

# ID -> (tipo v2, decisao, anotacoes)
TROCAS = {
    # D72: empresa a promover os proprios produtos / presenca de empresa num evento para mostrar produtos
    "93c836dd2abab8ed": (MK, "D72", {"EMPRESA": "Hm.Clause", "PRODUTO": "novas variedades hortícolas", "QUEM_FALOU": "Hm.Clause"}),
    "925a2a0f7c570077": (MK, "D72", {"EMPRESA": "Vog", "PRODUTO": "mele biologiche", "QUEM_FALOU": "Vog"}),
    "aae3bdef0c33d972": (MK, "D72", {"EMPRESA": "Alkelux", "PRODUTO": "additivi per packaging (shelf-life berries)", "QUEM_FALOU": "Alkelux"}),
    "727dc78fd96a3daa": (MK, "D72", {"EMPRESA": "Cantine Maschio (Riunite & CIV)", "PRODUTO": "Mini Prosecco", "QUEM_FALOU": "Riunite & CIV"}),
    "1278eae73661b268": (MK, "D72", {"EMPRESA": "Dei Cavalieri (Riunite & CIV)", "PRODUTO": "Prosecco", "QUEM_FALOU": "Riunite & CIV"}),
    "a9914f76fc7dad1e": (MK, "D72", {"EMPRESA": "Riunite", "PRODUTO": "Lambrusco", "QUEM_FALOU": "Riunite & CIV"}),
    "788ee868bbf76535": (MK, "D72", {"EMPRESA": "NAO SEI", "PRODUTO": "Thor (pomodoro da industria)", "QUEM_FALOU": "NAO SEI"}),
    "f5a7b27659028207": (MK, "D72", {"EMPRESA": "Pro Food", "PRODUTO": "imballaggi ortofrutta", "QUEM_FALOU": "Roberto Zanichelli"}),
    "2f94e8c17f04eccd": (MK, "D72", {"EMPRESA": "Consorzio Vino Chianti Classico", "PRODUTO": "Chianti Classico", "QUEM_FALOU": "Consorzio"}),
    "7bc42bc7452a73c4": (MK, "D72", {"EMPRESA": "Consorzi Vino e Olio Chianti Classico", "PRODUTO": "Chianti Classico (certificado Expert)", "QUEM_FALOU": "Consorzi"}),
    "04b1d0c3ed1d81a9": (MK, "D72", {"EMPRESA": "Cantine Maschio", "PRODUTO": "NAO SEI", "QUEM_FALOU": "Riunite & CIV"}),
    "e581115a4308d1a9": (MK, "D72", {"EMPRESA": "Consorzio Conegliano Valdobbiadene Prosecco DOCG", "PRODUTO": "Prosecco DOCG", "QUEM_FALOU": "NAO SEI"}),
    # D71: empresa a explicar tecnica = o tipo tecnico, com a empresa como quem publicou
    "f5d85a483dd13b10": ("CAMPO_FITOSSANITARIO", "D71", {"PUBLICADOR": "Koppert"}),
    # D73: varejo com facto de produto (loja, insignia, e-commerce, prateleira no CORPO ou «online» no titulo)
    "d8c4b58710b88070": ("MERCADO_VAREJO", "D73", {"PROVA": "«Uva da tavola online, prezzi 2026»"}),
    "d3aec5e747c0da9f": ("MERCADO_VAREJO", "D73", {"PROVA": "«ha visitato 14 punti vendita di 14 insegne»; referenze in promozione"}),
    "49d810984f550905": ("MERCADO_VAREJO", "D73", {"PROVA": "«panel Uva e-commerce Italia … 19 insegne dell'e-commerce»"}),
    "64e55e42c7745492": ("MERCADO_VAREJO", "D73", {"PROVA": "prezzo con cui la Grande distribuzione acquista le banane"}),
    "2d7d4d39ff5a9596": ("MERCADO_VAREJO", "D73", {"PROVA": "consumi e freschi nella distribuzione tedesca"}),
}
# D73 + ponto 5: conteudo do mundo agro sem facto, e abertura/operacao de loja -> INSTITUCIONAL.
# O resto do antigo INSTITUCIONAL_NAO_FATO (nao agro) -> NAO_FATO.
INSTITUCIONAL = {
    "e79afc0f677b3f1d": "delegados de departamento agroalimentar (DI4A)",
    "5aa59558089218f1": "abertura de supermercados (D73: loja = INSTITUCIONAL)",
    "31189f686550e721": "Welcome Day do Dip. de Agricoltura",
    "23972ee6be4f4449": "avisos de exames de cursos agrarios",
    "7006fd1a32262af6": "operacao logistica da GDO (D73)",
    "2c9f9efd062d9e40": "ampliacao de superstore (D73: operacao de loja)",
    "80841439830e6926": "CONAF, ordem dos agronomos",
    "5f23e208c8b4141e": "lista de exames agrarios",
    "5971381966ec9908": "curso de mestrado Sustainable Food Systems",
    "fca5cbf5f4c83b9d": "menu da ARSAC (agencia agricola)",
    "4bec0b706957aaaf": "licenciatura em Viticoltura ed Enologia",
    "1136deeef50023c3": "historia do CNR-ISPA (agroalimentar)",
    "f4c2204a1f7fc152": "curso de Scienze Gastronomiche (Agraria)",
    "b5d0129a2c71c124": "avisos de aulas de cursos agrarios (controlo biologico, entomologia)",
    "eca8ad431f745e14": "infraestruturas de investigacao do CREA",
    "7a7e50c7cce00eea": "Georgofili institucional",
    "c9c96814715f7a17": "livro de ex-alunos de Agraria",
    "fbff276d46ab534c": "Fondazione Minoprio ITS (escola agraria)",
    "fa13b59c108dceae": "Organismo Pagatore para agricultores",
    "8e81e821eac0ebbf": "historia das associacoes agricolas",
}


def reetiquetar(nome):
    f = AQUI / "rotulos" / nome
    rot = json.loads(f.read_text(encoding="utf-8"))
    usados = set()
    for r in rot:
        v1 = r.get("FACT_KIND_V1", r["FACT_KIND"])
        r["FACT_KIND_V1"] = v1
        if r["ID"] in TROCAS:
            k, dec, anot = TROCAS[r["ID"]]
            r["AGRO_FACT_KIND"], r["MUDOU_POR"] = k, dec
            r.update(anot)
            usados.add(r["ID"])
        elif v1 == "INSTITUCIONAL_NAO_FATO":
            if r["ID"] in INSTITUCIONAL:
                r["AGRO_FACT_KIND"], r["MUDOU_POR"] = "INSTITUCIONAL", "D73/ponto 5: " + INSTITUCIONAL[r["ID"]]
                usados.add(r["ID"])
            else:
                r["AGRO_FACT_KIND"], r["MUDOU_POR"] = "NAO_FATO", "ponto 5: nao e agro nem comunicacao de concorrente"
        else:
            r["AGRO_FACT_KIND"], r["MUDOU_POR"] = v1, None
        r.pop("FACT_KIND", None)
    f.write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return rot, usados


def main():
    tudo, usados = [], set()
    for nome in ("rotulos-gabarito.json", "rotulos-cega.json"):
        rot, u = reetiquetar(nome)
        usados |= u
        print(nome, dict(Counter(r["AGRO_FACT_KIND"] for r in rot).most_common()),
              "mudaram:", sum(1 for r in rot if r["AGRO_FACT_KIND"] != r["FACT_KIND_V1"]))
        tudo += rot
    falta = (set(TROCAS) | set(INSTITUCIONAL)) - usados
    assert not falta, "IDs sem item: %s" % falta


if __name__ == "__main__":
    main()
