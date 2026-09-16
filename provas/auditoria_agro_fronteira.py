#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AUDITORIA DA FRONTEIRA AGRONOMICA — o que a Intelligence agricola recebe.

    ESTE FICHEIRO NAO MUDA NADA. Ele MEDE.

Missao `C-INT-AGRO-BENCH-01`. Instrumento nao-invasivo: corre o caminho real
(`admissao.decidir` -> `admissao.pronto_para_inteligencia`) com casos
DESCARTAVEIS e escreve o que sobrevive a fronteira.

    NAO escreve na Sala de Espera.  NAO toca no livro de decisoes.
    NAO importa nada da Collection runtime alem da propria porta.

Os quatro ataques sao os do enunciado:

    A  FACT STRUCTURE SURVIVAL   um FATO agronomico estruturado atravessa?
    B  PUBLICATION TIME          `published_at` abre o portao temporal?
    C  STRUCTURED AGRO CONTEXT   cultura/problema/metodo/valor/unidade chegam?
    D  IDENTITY                  que identidades sobrevivem?

    python3 provas/auditoria_agro_fronteira.py            # relatorio legivel
    python3 provas/auditoria_agro_fronteira.py --json     # o mesmo, em JSON
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
from admissao import (decidir, pronto_para_inteligencia, estagio,  # noqa: E402
                      _tem_quando, SIM, NAO_SEI, DOCUMENTO, FATO,
                      ESTAGIO_DESCONHECIDO)


# ── O CASO DESCARTAVEL ──────────────────────────────────────────────────────
# Um FATO agronomico com tudo o que os benchmarks externos exigem de uma
# observacao defensavel: MIAPPE/Crop Ontology (trait x method x scale), EFSA
# (denominador, populacao alvo, sensibilidade do metodo), EPPO (identidade),
# BBCH (fenologia), PP1/248 (uso de PPP). NENHUM destes campos e inventado por
# mim: cada um tem fonte externa citada no benchmark.
FATO_AGRO = {
    # identidade
    "id": "AUDIT-FATO-1",
    "claim_id": "AUDIT-CLAIM-1",
    "raw_asset_id": 9901,
    "parent_artifact_id": "AUDIT-DERIVED-1",
    # sujeito-predicado-objeto (COL-LAW-202)
    "subject": "Plasmopara viticola",
    "predicate": "incidencia_observada_em",
    "object": "Vitis vinifera",
    # ontologia agricola
    "crop": "Vite",
    "crop_eppo": "VITVI",
    "problem": "Peronospora della vite",
    "problem_eppo": "PLASVI",
    "active_substance": "metiram",
    "active_substance_cas": "9006-42-2",
    "product": "AUDIT-PRODUTO",
    "registration_id": "IT-00000",
    # observacao (MIAPPE / Crop Ontology / EFSA)
    "value": 12.5,
    "unit": "%",
    "scale": "percentagem_de_folhas_com_sintoma",
    "method": "inspecao_visual_de_100_folhas_por_parcela",
    "diagnostic_method": "sintomatologia_de_campo",
    "sample_size": 100,
    "denominator": 400,
    "target_population": "vinhedos_da_provincia",
    "design_prevalence": 0.02,
    "method_sensitivity": 0.8,
    "confidence_level": 0.95,
    # fenologia (BBCH)
    "bbch": 61,
    "phenological_stage": "floracao",
    # tempo e lugar (COL-LAW-031/032)
    "fact_time": "2026-05-02",
    "published_at": "2026-06-30",
    "observed_at": "2026-05-02",
    "captured_at": "2026-07-01",
    "fact_location": "IT-Veneto-Verona",
    "source_location": "IT-Roma",
    "nuts": "ITH31",
    # proveniencia
    "source_id": "IT-T3-005",
    "url": "https://exemplo.invalido/boletim",
    "doi": "10.0000/audit",
    "texto": "Sintomo di peronospora al 12,5% delle foglie, 100 foglie per parcella.",
}

# E · O MESMO FATO, na lingua em que a fonte o escreveria. Uma so palavra de
# diferenca — e ela decide se a porta reconhece o universo.
FATO_SEM_PALAVRA_DO_LEXICO = dict(FATO_AGRO)
FATO_SEM_PALAVRA_DO_LEXICO["id"] = "AUDIT-FATO-LEX"
FATO_SEM_PALAVRA_DO_LEXICO["texto"] = (
    "Peronospora osservata al 12,5% delle foglie in 100 foglie per parcella.")

# B · um artefato com APENAS data de publicacao. Sem `fact_time`, sem `data`.
# O estagio e declarado FATO para que a pergunta do tempo SEJA feita — que e
# exactamente o que este ataque quer medir.
SO_PUBLICACAO = {
    "id": "AUDIT-PUB-1",
    "claim_id": "AUDIT-CLAIM-PUB",
    "subject": "Plasmopara viticola",
    "predicate": "relatada_em",
    "source_id": "IT-T3-005",
    "texto": "Bollettino: sintomo di malattia segnalato.",
    "published_at": "2026-06-30",
}

# D · um item que passa a porta sem `id` e sem `url`.
SEM_ID = {
    "source_id": "IT-T3-005",
    "texto": "Nota tecnica su sintomo di malattia, senza identificatore.",
    "fact_time": "2026-05-02",
    "claim_id": "AUDIT-CLAIM-SEM-ID",
}

# D · o mesmo fato, declarado como DOCUMENTO (o estagio que a rota real usa).
DOCUMENTO_AGRO = dict(FATO_AGRO)
for _k in ("claim_id", "subject", "predicate", "object"):
    DOCUMENTO_AGRO.pop(_k)
DOCUMENTO_AGRO["id"] = "AUDIT-DOC-1"
DOCUMENTO_AGRO["artifact_type"] = "DERIVED"

UNIVERSO = "T3"


def _atravessa(item, universo=UNIVERSO):
    """Corre o caminho real. Devolve (decisao, unidade_ready_ou_None)."""
    d = decidir(item, universo, corrida="AUDIT-AGRO")
    if d.resultado != SIM:
        return d, None
    return d, pronto_para_inteligencia(item, d)


def ataque_a():
    """FACT STRUCTURE SURVIVAL — o que sobrevive de um FATO estruturado."""
    d, ready = _atravessa(FATO_AGRO)
    entrou = set(FATO_AGRO)
    saiu_valores = set()
    if ready:
        for k, v in ready.items():
            for ke, ve in FATO_AGRO.items():
                if str(ve) == str(v):
                    saiu_valores.add(ke)
    perdidos = sorted(entrou - saiu_valores)
    return {
        "ATAQUE": "A · FACT STRUCTURE SURVIVAL",
        "ESTAGIO_RECONHECIDO": estagio(FATO_AGRO),
        "RESULTADO_DA_PORTA": d.resultado,
        "REGRA": d.regra,
        "CAMPOS_ENTRADA": len(entrou),
        "CAMPOS_READY": len(ready or {}),
        "CAMPOS_QUE_SOBREVIVEM_COM_VALOR": sorted(saiu_valores),
        "CAMPOS_PERDIDOS": perdidos,
        "N_PERDIDOS": len(perdidos),
        "READY": ready,
    }


def ataque_b():
    """PUBLICATION TIME — `published_at` abre o portao temporal?"""
    d, ready = _atravessa(SO_PUBLICACAO)
    ev = d.evidencia or {}
    # A pergunta do tempo, medida DIRECTAMENTE — o resultado agregado nao
    # mostra qual das perguntas respondeu o que.
    r_tempo, motivo_tempo, ev_tempo = _tem_quando(SO_PUBLICACAO)
    # E o campo generico `data`, que nao declara de que tempo e.
    com_data = dict(SO_PUBLICACAO)
    com_data.pop("published_at")
    com_data["data"] = SO_PUBLICACAO["published_at"]
    d_data, ready_data = _atravessa(com_data)
    return {
        "ATAQUE": "B · PUBLICATION TIME",
        "PERGUNTA_DO_TEMPO_DIRECTA": {
            "resultado": r_tempo, "motivo": motivo_tempo, "evidencia": ev_tempo},
        "EVIDENCIA_DO_TEMPO_CHEGA_AO_LIVRO": "quando" in json.dumps(ev),
        "CAMPO_GENERICO_DATA_VIRA_FACT_TIME": (ready_data or {}).get("FACT_TIME"),
        "ESTAGIO_RECONHECIDO": estagio(SO_PUBLICACAO),
        "RESULTADO_DA_PORTA": d.resultado,
        "REGRA": d.regra,
        "PASSOU_O_PORTAO_TEMPORAL": d.resultado == SIM,
        "EVIDENCIA_DA_PORTA": ev,
        "FACT_TIME_NO_READY": (ready or {}).get("FACT_TIME"),
        "PUBLISHED_AT_DA_ENTRADA": SO_PUBLICACAO["published_at"],
        "PUBLISHED_AT_CHEGA_AO_READY": bool(
            ready and SO_PUBLICACAO["published_at"] in json.dumps(ready)),
    }


def ataque_c():
    """STRUCTURED AGRONOMIC CONTEXT — chega identificavel, sem reparsear texto?"""
    campos = ("crop", "crop_eppo", "problem", "problem_eppo", "product",
              "registration_id", "active_substance", "bbch",
              "phenological_stage", "method", "diagnostic_method", "value",
              "unit", "scale", "sample_size", "denominator",
              "target_population", "design_prevalence", "method_sensitivity",
              "confidence_level", "nuts", "observed_at", "doi")
    linhas = []
    for estagio_nome, caso in (("FATO", FATO_AGRO), ("DOCUMENTO", DOCUMENTO_AGRO)):
        _, ready = _atravessa(caso)
        blob = json.dumps(ready, ensure_ascii=False) if ready else ""
        for c in campos:
            v = caso.get(c)
            chave_propria = ready is not None and c.upper() in ready
            valor_presente = ready is not None and str(v) in blob
            linhas.append({
                "ESTAGIO": estagio_nome, "CAMPO": c,
                "CHAVE_PROPRIA_NO_READY": chave_propria,
                "VALOR_APARECE_EM_ALGUM_CAMPO": valor_presente,
                "SO_NO_TEXTO": valor_presente and not chave_propria,
            })
    com_chave = [x for x in linhas if x["CHAVE_PROPRIA_NO_READY"]]
    return {
        "ATAQUE": "C · STRUCTURED AGRONOMIC CONTEXT",
        "CAMPOS_TESTADOS": len(campos),
        "COM_CHAVE_PROPRIA_NO_READY": len(com_chave),
        "DETALHE": linhas,
    }


def ataque_d():
    """IDENTITY — que identidades atravessam."""
    _, ready_fato = _atravessa(FATO_AGRO)
    d_sem, ready_sem = _atravessa(SEM_ID)
    ids = {
        "raw_asset_id -> RAW_OBSERVATION_ID": (
            ready_fato or {}).get("RAW_OBSERVATION_ID"),
        "id -> ITEM_ID": (ready_fato or {}).get("ITEM_ID"),
        "source_id -> SOURCE_ID": (ready_fato or {}).get("SOURCE_ID"),
        "claim_id": "PRESENTE" if (ready_fato and "CLAIM_ID" in ready_fato) else "PERDIDO",
        "parent_artifact_id": "PRESENTE" if (ready_fato and "PARENT_ARTIFACT_ID" in ready_fato) else "PERDIDO",
        "doi": "PRESENTE" if (ready_fato and "DOI" in ready_fato) else "PERDIDO",
        "registration_id": "PRESENTE" if (ready_fato and "REGISTRATION_ID" in ready_fato) else "PERDIDO",
        "crop_eppo": "PRESENTE" if (ready_fato and "CROP_EPPO" in ready_fato) else "PERDIDO",
        "problem_eppo": "PRESENTE" if (ready_fato and "PROBLEM_EPPO" in ready_fato) else "PERDIDO",
    }
    return {
        "ATAQUE": "D · IDENTITY",
        "IDENTIDADES": ids,
        "RAW_OBSERVATION_ID_PRESERVADO": (
            (ready_fato or {}).get("RAW_OBSERVATION_ID") == FATO_AGRO["raw_asset_id"]),
        "ITEM_SEM_ID_NEM_URL": {
            "RESULTADO_DA_PORTA": d_sem.resultado,
            "ITEM_ID_NO_READY": (ready_sem or {}).get("ITEM_ID"),
            "COL_LAW_034_PROIBE_ESTE_VALOR": (ready_sem or {}).get("ITEM_ID") in ("?", ""),
        },
    }


def ataque_e():
    """LEXICO DO UNIVERSO — o mesmo fato, duas redaccoes, duas decisoes."""
    com, _ = _atravessa(FATO_AGRO)
    sem, _ = _atravessa(FATO_SEM_PALAVRA_DO_LEXICO)
    return {
        "ATAQUE": "E · LEXICO DO UNIVERSO (conceito -> termo local)",
        "COM_PALAVRA_DO_LEXICO": {
            "texto": FATO_AGRO["texto"],
            "resultado": com.resultado, "motivo": com.motivo[:120],
            "evidencia": com.evidencia},
        "SEM_PALAVRA_DO_LEXICO": {
            "texto": FATO_SEM_PALAVRA_DO_LEXICO["texto"],
            "resultado": sem.resultado, "motivo": sem.motivo[:120],
            "evidencia": sem.evidencia},
        "MESMO_EPPO_NOS_DOIS": (FATO_AGRO["problem_eppo"]
                                == FATO_SEM_PALAVRA_DO_LEXICO["problem_eppo"]),
        "DECISAO_MUDA_SEM_O_FATO_MUDAR": com.resultado != sem.resultado,
    }


def ataque_f():
    """O VOCABULARIO DA FRONTEIRA — que nomes a travessia conhece.

    `coleta/ingresso.py::PARA_A_PORTA` e o tradutor unico do contrato comum.
    O que ele nao conhece viaja intacto ate `decidir`, e morre em
    `pronto_para_inteligencia`. Esta medicao mostra os dois numeros.
    """
    import ingresso
    mapa = dict(ingresso.PARA_A_PORTA)
    # O que a rota forward real poe no item (rota_forward_documento.item_para_a_porta)
    rota_forward = ["SOURCE_ID", "ARTIFACT_TYPE", "PARENT_SHA256",
                    "PARENT_ARTIFACT_ID", "id", "texto", "url", "captured_at",
                    "raw_asset_id"]
    agro = ["CROP", "CROP_EPPO", "PROBLEM", "PROBLEM_EPPO", "PRODUCT",
            "REGISTRATION_ID", "ACTIVE_SUBSTANCE", "BBCH", "METHOD", "VALUE",
            "UNIT", "SCALE", "DENOMINATOR", "SAMPLE_SIZE", "EVIDENCE_CLASS",
            "CLAIM_ID", "SUBJECT", "PREDICATE", "OBJECT", "DOI"]
    return {
        "ATAQUE": "F · VOCABULARIO DA FRONTEIRA",
        "CONTRATO_COMUM_PARA_A_PORTA": sorted(mapa),
        "N_CONTRATO_COMUM": len(mapa),
        "ROTA_FORWARD_POE_NO_ITEM": rota_forward,
        "N_ROTA_FORWARD": len(rota_forward),
        "CAMPOS_AGRO_NO_CONTRATO_COMUM": [c for c in agro if c in mapa],
        "CAMPOS_AGRO_NA_ROTA_FORWARD": [c for c in agro if c in rota_forward],
        "FACT_TIME_NA_ROTA_FORWARD": "FACT_TIME" in rota_forward,
        "FACT_LOCATION_NA_ROTA_FORWARD": "FACT_LOCATION" in rota_forward,
        "SOURCE_LOCATION_NA_ROTA_FORWARD": "SOURCE_LOCATION" in rota_forward,
    }


def medir():
    return {
        "MISSAO": "C-INT-AGRO-BENCH-01",
        "INSTRUMENTO": "provas/auditoria_agro_fronteira.py",
        "CONTRATO_MEDIDO": "admissao.pronto_para_inteligencia (COL-LAW-043)",
        "ATAQUES": [ataque_a(), ataque_b(), ataque_c(), ataque_d(),
                    ataque_e(), ataque_f()],
    }


def main():
    r = medir()
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    a, b, c, d, e, f = r["ATAQUES"]
    print("AUDITORIA DA FRONTEIRA AGRONOMICA · %s" % r["MISSAO"])
    print("contrato medido: %s\n" % r["CONTRATO_MEDIDO"])

    print("── %s" % a["ATAQUE"])
    print("   estagio reconhecido ........ %s" % a["ESTAGIO_RECONHECIDO"])
    print("   porta ...................... %s (%s)" % (a["RESULTADO_DA_PORTA"], a["REGRA"]))
    print("   campos na entrada .......... %d" % a["CAMPOS_ENTRADA"])
    print("   campos no READY ............ %d" % a["CAMPOS_READY"])
    print("   sobrevivem com valor ....... %d  %s" % (
        len(a["CAMPOS_QUE_SOBREVIVEM_COM_VALOR"]), a["CAMPOS_QUE_SOBREVIVEM_COM_VALOR"]))
    print("   PERDIDOS ................... %d" % a["N_PERDIDOS"])
    print("   %s\n" % ", ".join(a["CAMPOS_PERDIDOS"]))

    print("── %s" % b["ATAQUE"])
    print("   estagio .................... %s" % b["ESTAGIO_RECONHECIDO"])
    print("   porta ...................... %s (%s)" % (b["RESULTADO_DA_PORTA"], b["REGRA"]))
    print("   passou o portao temporal ... %s" % b["PASSOU_O_PORTAO_TEMPORAL"])
    print("   pergunta do tempo, directa   %s · %s · %s" % (
        b["PERGUNTA_DO_TEMPO_DIRECTA"]["resultado"],
        b["PERGUNTA_DO_TEMPO_DIRECTA"]["motivo"],
        json.dumps(b["PERGUNTA_DO_TEMPO_DIRECTA"]["evidencia"], ensure_ascii=False)))
    print("   evidencia da porta ......... %s" % json.dumps(b["EVIDENCIA_DA_PORTA"], ensure_ascii=False))
    print("   essa evidencia chega ao livro  %s" % b["EVIDENCIA_DO_TEMPO_CHEGA_AO_LIVRO"])
    print("   campo generico `data` vira FACT_TIME: %r" % b["CAMPO_GENERICO_DATA_VIRA_FACT_TIME"])
    print("   FACT_TIME no READY ......... %r" % b["FACT_TIME_NO_READY"])
    print("   published_at chega ao READY  %s\n" % b["PUBLISHED_AT_CHEGA_AO_READY"])

    print("── %s" % c["ATAQUE"])
    print("   campos agronomicos testados  %d" % c["CAMPOS_TESTADOS"])
    print("   com chave propria no READY . %d" % c["COM_CHAVE_PROPRIA_NO_READY"])
    so_texto = [x for x in c["DETALHE"] if x["SO_NO_TEXTO"]]
    print("   so no TEXTO ................ %d\n" % len(so_texto))

    print("── %s" % d["ATAQUE"])
    for k, v in d["IDENTIDADES"].items():
        print("   %-38s %s" % (k, v))
    print("   RAW_OBSERVATION_ID preservado  %s" % d["RAW_OBSERVATION_ID_PRESERVADO"])
    s = d["ITEM_SEM_ID_NEM_URL"]
    print("   item sem id nem url -> ITEM_ID %r  (COL-LAW-034 proibe: %s)\n"
          % (s["ITEM_ID_NO_READY"], s["COL_LAW_034_PROIBE_ESTE_VALOR"]))

    print("── %s" % e["ATAQUE"])
    print("   com palavra do lexico ...... %s" % e["COM_PALAVRA_DO_LEXICO"]["resultado"])
    print("   sem palavra do lexico ...... %s" % e["SEM_PALAVRA_DO_LEXICO"]["resultado"])
    print("   mesmo codigo EPPO nos dois . %s" % e["MESMO_EPPO_NOS_DOIS"])
    print("   a decisao muda sem o fato mudar: %s\n" % e["DECISAO_MUDA_SEM_O_FATO_MUDAR"])

    print("── %s" % f["ATAQUE"])
    print("   contrato comum (PARA_A_PORTA)  %d nomes" % f["N_CONTRATO_COMUM"])
    print("   %s" % ", ".join(f["CONTRATO_COMUM_PARA_A_PORTA"]))
    print("   rota forward poe no item ..... %d nomes" % f["N_ROTA_FORWARD"])
    print("   %s" % ", ".join(f["ROTA_FORWARD_POE_NO_ITEM"]))
    print("   campos agro no contrato comum  %s" % (f["CAMPOS_AGRO_NO_CONTRATO_COMUM"] or "NENHUM"))
    print("   campos agro na rota forward .. %s" % (f["CAMPOS_AGRO_NA_ROTA_FORWARD"] or "NENHUM"))
    print("   FACT_TIME na rota forward .... %s" % f["FACT_TIME_NA_ROTA_FORWARD"])
    print("   FACT_LOCATION na rota forward  %s" % f["FACT_LOCATION_NA_ROTA_FORWARD"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
