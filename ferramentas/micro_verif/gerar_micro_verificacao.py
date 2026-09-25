#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MICRO-VERIFICACAO · junta a escolha (pela regra do .md), as medidas e a previsao num JSON com sha256.

    py ferramentas/micro_verif/gerar_micro_verificacao.py

Sem rede. Le so os ficheiros desta pasta.
"""
import hashlib
import json
from pathlib import Path

AQUI = Path(__file__).parent
COORTE_SHA = "06f87b97761d73281bc341d87d7a644ec0c5014a291265db2b8372732bf4977f"
ESCOLHA = ["IT-T10-018", "IT-T2-034", "IT-T5-160", "IT-T7-017", "IT-T2-051"]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    d40 = {f["SOURCE_ID"]: f for f in json.loads((AQUI / "MEDICAO-D40-MICRO-VERIF.json").read_text(encoding="utf-8"))["FONTES"]}
    data = {f["SOURCE_ID"]: f for f in json.loads((AQUI / "DATA-NA-PAGINA-COORTE-V1.json").read_text(encoding="utf-8"))["FONTES"]}
    prev = {f["SOURCE_ID"]: f for f in json.loads((AQUI / "PREVISAO-COM-O-INSTALADO-V1.json").read_text(encoding="utf-8"))["FONTES"]}
    plano = json.loads((AQUI / "ONDA-WEB-SO-PLANO.json").read_text(encoding="utf-8"))

    def novos(s):
        f = d40.get(s)
        if not f or f.get("MEDIDO") != "OK":
            return {"ALVOS_NOVOS_NO_INDICE": "NAO MEDIDO (sem indice guardado)", "DOCUMENTOS_NOVOS_NA_CORRIDA": "NAO SEI"}
        return {"ALVOS_NOVOS_NO_INDICE": f.get("NOVOS"), "DOCUMENTOS_NOVOS_NA_CORRIDA": f.get("DOCUMENTOS_NOVOS_NA_CORRIDA")}

    def frac(s, k_sim, k_nao):
        c = prev[s]["CONTAGENS"]
        n = c.get(k_sim, 0) + c.get(k_nao, 0)
        return "%d de %d" % (c.get(k_sim, 0), n) if n else "NAO SEI"

    cat = {"IT-T10-018": "A · myfruit", "IT-T2-034": "B · agencia T2 (melhor D40 entre as T2 medidas)",
           "IT-T5-160": "C · pesquisa (nenhuma C tem indice guardado: desempate por SOURCE_ID)",
           "IT-T7-017": "D · data na pagina (37/37 marcadas; o maior D40 entre as D com fracao 1.0)",
           "IT-T2-051": "5.a · outra T2 com >= 1 alvo novo e dominio novo"}
    fontes = []
    for s in ESCOLHA:
        c = prev[s]["CONTAGENS"]
        pub = c.get("PUBLICACAO_SIM", 0)
        fontes.append({
            "SOURCE_ID": s, "CATEGORIA": cat[s], "INDEX_URL": data[s]["INDEX_URL"],
            **novos(s),
            "DATA_NA_PAGINA_GUARDADA": "%s de %s" % (data[s]["COM_ALGUMA_MARCA"], data[s]["HTML"]),
            "PREVISAO": {
                "PUBLICACAO": ("SIM (precisao INSTANTE), pelo leitor de pagina" if pub and pub == c.get("HTML")
                               else "NAO (NAO SEI com o porque)" if not pub else "EM PARTE"),
                "LUGAR_DA_FONTE": "NAO — o contrato nao declara SOURCE_LOCATION_RULE (base NAO SEI com o porque)",
                "DATA_DO_FATO_NAS_GUARDADAS": frac(s, "DATA_FATO_SIM", "DATA_FATO_NAO"),
                "LUGAR_DO_FATO_NAS_GUARDADAS": frac(s, "LUGAR_FATO_SIM", "LUGAR_FATO_NAO"),
                "TIPOS_DE_DATA": {k.split(":")[1]: v for k, v in c.items() if k.startswith("DATA_FATO_KIND:")},
                "TIPOS_DE_LUGAR": {k.split(":")[1]: v for k, v in c.items() if k.startswith("LUGAR_FATO_KIND:")},
            }})
    out = {
        "DATASET": "MICRO-VERIFICACAO-V1", "LEI": "D74 (proxima acao operacional; NAO e onda)",
        "VIVO": "e5cd691f (origin/servico-20260923-0923)", "REDE_NESTA_MISSAO": 0,
        "COORTE": {"FICHEIRO": "ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json", "ESTADO": "CONGELADA",
                   "FONTES": 28, "SHA256_DO_COMMIT": COORTE_SHA},
        "REGRA": "MICRO-VERIFICACAO.md §1 (commit 1d58b49c, antes de medir)",
        "ESCOLHA": fontes,
        "SO_PLANO": {k: plano[k] for k in ("PODE_CORRER", "CORREM", "PEDIDOS_POR_DOMINIO", "MAXIMO_POR_DOMINIO",
                                            "PEDIDOS_TOTAL_PREVISTO", "SALTAM_POR_TETO_DOMINIO")},
        "COMANDO": ("py ferramentas/big_collection/onda_web.py --correr "
                    "--fontes=%s --sha256=%s --saida=C:\\bc\\micro-verif-<AAAAMMDD-HHMM>" % (",".join(ESCOLHA), COORTE_SHA)),
        "SELECTS": "MICRO-VERIFICACAO-SELECTS.sql (READ ONLY + ROLLBACK; Q0 antes e depois; Q5 prova que foi o codigo novo)",
        "EVIDENCIA_SHA256": {p.name: sha(p) for p in sorted(AQUI.glob("*")) if p.is_file()
                             and p.name not in ("MICRO-VERIFICACAO.json",)},
    }
    (AQUI / "MICRO-VERIFICACAO.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out["ESCOLHA"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
