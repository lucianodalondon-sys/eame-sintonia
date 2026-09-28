#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O MOTOR DAS CAPACIDADES — uma corrida G0/v4, a CAP-WIN e a CAP-SCI, e a saida
que o gerador do pote v2 aceita.

    MISSAO   INT-R7-CAPS (juntar CAP-WIN + CAP-SCI no motor; regras D112 do teste
             da Puglia; saida para o pote v2; rodada 7 numa COPIA da Sala)
    ESTADO   EXPERIMENTAL / NAO_PARA_CLIENTE
    ENTRADA  o export read-only da vista `sala_de_espera_atual` + `raw_asset`
             (RUNBOOK-R7.md mostra o comando exato)
    SAIDA    MOTOR_DAS_CAPACIDADES/v1 — o livro de entrada que o gerador
             `pacote/pote_intelligence_casco.py @ ce775ff5`
             (POTE_INTELLIGENCE_CASCO/v2) le com `adaptar()`.

    python3 motor/motor_das_capacidades.py <export.json> --hoje AAAA-MM-DD \\
            [--source-head SHA] [--saida saida.json]
    python3 -m unittest tests.test_motor_das_capacidades -v

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    DADA UMA COPIA DA SALA, O QUE AS DUAS CAPACIDADES DIZEM SOBRE ELA — NUMA
    CORRIDA SO, COM A PROVA ATE AO RAW, E SEM QUE O SISTEMA FALE PELA FONTE?

O QUE ELE FAZ (e cada coisa tem um dono so)
-------------------------------------------
  1. UMA corrida G0/v4 (`corrida_da_inteligencia.correr`) sobre TODOS os READY
     do export: um INTELLIGENCE_RUN_ID, uma LINEAGE, um universo. As duas
     capacidades leem o MESMO livro — nenhuma conta de novo o que a corrida
     contou (sem contador duplicado).
  2. TRIAGEM pelo significado: estudo e o item cujo FATO declara identidade de
     estudo (DOI, TRIAL_ID ou especie cientifica, lidos pela CAP-SCI, dona
     desse vocabulario). Estudo vai a CAP-SCI; o resto a CAP-WIN. ESTUDO NUNCA
     VIRA INCIDENCIA DE CAMPO: nenhum estudo entra numa janela.
  3. D112 (teste da Puglia), verbatim da missao, em codigo:
       (a) local do fato so com sustentacao EXPLICITA da fonte;
       (b) toda entidade com a procedencia da evidencia (ENTITY_SOURCE);
       (c) evidencia insuficiente = NAO SEI;
       (d) o que veio da FONTE separado da INTERPRETACAO do sistema;
       (e) mesma redacao em N territorios = N aplicacoes / 1 instituicao;
       (f) limites diferentes = DIVERGENT com contradicao UNRESOLVED;
       (g) mudanca de recomendacao no tempo = TEMPORAL_CHANGE, e isso NAO prova
           mudanca no campo.
  4. A SAIDA no contrato de entrada do pote v2 (INTELLIGENCE_RUN_ID no topo,
     prova com URL e PUBLISHED_AT/PUBLICADO_EM), conferida por um portao
     proprio (`conferir_saida`) antes de sair.

O QUE ELE NUNCA FAZ
-------------------
    NAO abre a Sala: recebe o export ja lido (o dono da Sala e
        admissao/sala_de_espera.py; a leitura e do coordenador, read-only).
    NAO cunha DOCUMENT_ID, URL, SOURCE_ID nem RAW_OBSERVATION_ID: URL e
        DOCUMENT_ID vem do RAW (raw_asset.source_url / document_key) pelo
        RAW_OBSERVATION_ID do READY; ausentes = NAO SEI (e o pote recusa a
        prova sem DOCUMENT_ID — a vista, em RECUSADOS).
    NAO produz OPORTUNIDADE nem FINDING. NAO promove: tudo sai como
        EXPERIMENTAL_CANDIDATE, e o juizo das capacidades viaja com a especie
        SINAL (a unica do pote v2 que nao promete mais do que o juizo e).
    NAO escolhe entre limites divergentes, nem le mudanca de recomendacao como
        mudanca no campo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _g in ("motor", "leis"):
    if str(RAIZ / _g) not in sys.path:
        sys.path.insert(0, str(RAIZ / _g))

import corrida_da_inteligencia as CI            # noqa: E402
import cap_win as WIN                            # noqa: E402
import capacidade_cientifica as SCI              # noqa: E402
import porta_da_referencia as PORTA              # noqa: E402  (D116: uma edicao para as duas)
# A LEI DO LUGAR tem dono (leis/lugar_do_fato.py): quem pode virar lugar do
# fato e porque nao. D112(a) chama-a — nao a reescreve.
import lugar_do_fato as LUGAR                    # noqa: E402
# LOTE6-INTEGRA: a D112 passou a estar ESCRITA no repositorio (METODO-PUGLIA: COL-LAW-221..223 na Biblia
# da Coleta, INT-LAW-078/079 na da Intelligence). O vocabulario das RELACOES tem dono
# (leis/afirmacao_da_fonte.RELACOES / CONTRADICTION_STATUS): cada relacao deste motor diz tambem a
# palavra da lei, calculada pelas regras da lei — nao a reescreve.
import afirmacao_da_fonte as AFIRMACAO           # noqa: E402

NAO_SEI = CI.NAO_SEI
CONTRATO_DA_ENTRADA = "ENTRADA_DO_MOTOR_DAS_CAPACIDADES/v1"
EXPORT_DA_SALA = "SALA_ATUAL_READ_ONLY/v1"
CONTRATO = "MOTOR_DAS_CAPACIDADES/v1"
#: O gerador cujo contrato de entrada esta saida segue (outra equipa unifica o
#: pote; o contrato e o do commit, e nao o de um ramo que ainda se mexe).
POTE_ALVO = ("POTE_INTELLIGENCE_CASCO/v2 · pacote/pote_intelligence_casco.py @ "
             "ce775ff5ad2287d8f6fc19bee5feebd02843b8de "
             "(claude/intelligence-bridge-v2-7mngha)")
MARCA = "EXPERIMENTAL · NAO_PARA_CLIENTE"
ESTADO_TRANSPORTAVEL = "EXPERIMENTAL_CANDIDATE"
PERGUNTA = ("rodada das capacidades: que janela de cultura (CAP-WIN) e que ciencia "
            "(CAP-SCI) a Sala sustenta, com prova ate ao RAW?")

#: D112, verbatim da missao INT-R7-CAPS. Quando este ramo nasceu a decisao nao
#: estava escrita no repositorio; desde o LOTE6-INTEGRA esta (docs/iab/puglia/
#: DECISAO-D112.md, METODO-PUGLIA.md), e as relacoes falam a lingua dela (RELATION).
D112 = (
    "local do fato so com sustentacao explicita da fonte",
    "toda entidade com procedencia da evidencia (ENTITY_SOURCE)",
    "evidencia insuficiente = NAO SEI",
    "separar o que veio da fonte x interpretacao do sistema",
    "relacoes: mesma redacao em N territorios = N aplicacoes/1 instituicao",
    "limites diferentes = DIVERGENT com contradicao UNRESOLVED",
    "mudanca de recomendacao no tempo = TEMPORAL_CHANGE, nao prova mudanca no campo",
)

MESMA_REDACAO = "MESMA_REDACAO"
DIVERGENT = "DIVERGENT"
TEMPORAL_CHANGE = "TEMPORAL_CHANGE"
UNRESOLVED = "UNRESOLVED"
#: As palavras da lei (INT-LAW-078/079), lidas do dono. `TIPO` e o agrupamento deste motor;
#: `RELATION` e o veredito na lingua da lei. Palavra fora do dono = o modulo nem carrega.
REL_078, REL_TEMPORAL, REL_DIVERGENT, REL_NAO_SEI = (
    "SAME_CLAIM_TERRITORIAL_APPLICATION", "TEMPORAL_CHANGE_IN_RECOMMENDATION",
    "DIVERGENT_RECOMMENDATIONS", "NAO_SEI")
if ({REL_078, REL_TEMPORAL, REL_DIVERGENT, REL_NAO_SEI} != set(AFIRMACAO.RELACOES)
        or {UNRESOLVED, "NO"} != set(AFIRMACAO.CONTRADICTION_STATUS)):
    raise ImportError("motor_das_capacidades fala relacoes fora da INT-LAW-078/079")

#: As especies do pote v2 que ESTE motor emite. SINAL para o juizo das
#: capacidades (o pote v2 nao tem especie ANALYTIC_JUDGMENT: a do motor viaja
#: em FORA_DO_CONTRATO.ESPECIE_DO_MOTOR, e a escolha de uma especie nova e do
#: dono do pote); FATO_PRESENTE_SOBRE_O_FUTURO e RENDIMENTO_DE_FONTE para o que
#: a corrida ja conta. Nunca OPORTUNIDADE, nunca FINDING.
SINAL = "SINAL"
FUTURO = "FATO_PRESENTE_SOBRE_O_FUTURO"
RENDIMENTO = "RENDIMENTO_DE_FONTE"
ESPECIES_EMITIDAS = (SINAL, FUTURO, RENDIMENTO)
G0_FUTURO_POR_DESENHO = "FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA"

#: As chaves de contrato por compartimento — as do gerador ce775ff5, copiadas
#: SO para o portao da saida conferir que nenhuma chave com valor fica sem
#: ENTITY_SOURCE. O dono delas e o gerador: se divergirem, o teste que corre o
#: gerador de verdade (tests.test_motor_das_capacidades, classe P) reprova.
CHAVES_DO_POTE = {
    "windows": ("CROP_ID", "REGION_ID", "ISSUE_ID", "DATE_OR_STAGE"),
    "science": ("DOI", "TRIAL_ID", "RESEARCHER_ORCID", "INSTITUTION_ID", "MOLECULE",
                "CROP_ID", "ISSUE_ID", "STUDY_LOCATION", "STUDY_PERIOD"),
    "future": ("CROP_ID", "ISSUE_ID", "REGION_ID", "FACT_LOCATION", "FACT_TIME",
               "FACT_TIME_BASIS"),
    "sources": ("SOURCE_ID", "ITENS_LIDOS", "ITENS_QUE_PASSARAM_G0", "OBJETOS_PRODUZIDOS"),
}

#: O export traz a vista `sala_de_espera_atual` (o que a Intelligence le,
#: migration 033) e tres colunas do `raw_asset` pelo RAW_OBSERVATION_ID.
COLUNAS_DO_RAW = {"raw_source_url": "URL", "raw_document_key": "DOCUMENT_ID",
                  "raw_document_key_basis": "DOCUMENT_ID_BASIS"}


class LeiViolada(Exception):
    """O motor recusou-se, e diz porque."""


def _ign(v) -> bool:
    return CI.e_ignorancia(v)


def _v(v):
    return NAO_SEI if _ign(v) else v


# ══════════════════════════════════════════════════════════════════════════
# 1 · A ENTRADA — o export da Sala, separado em READY | JANELA | RAW
# ══════════════════════════════════════════════════════════════════════════
def _json(v):
    """Coluna json da vista: pode chegar como objeto (json_agg) ou como texto."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def entrada_do_export(export: dict) -> dict:
    """O export read-only da Sala -> a entrada do motor. Nada e completado.

    ⚠️ TRES PORTAS, E NENHUMA E IDENTIDADE INVENTADA:
      READY  = os campos de `CAMPOS_DO_READY` (dono: admissao/sala_de_espera.py);
               ESTADO = PRONTO_PARA_INTELIGENCIA, como o proprio leitor da Sala
               o reconstroi (a Sala so guarda READY).
      JANELA = `janela_declarada` da vista (migration 033, dono: a Collection) —
               NAO esta em CAMPOS_DO_READY, e por isso viaja AO LADO do READY e
               so a CAP-WIN a le.
      RAW    = o endereco da prova (URL, DOCUMENT_ID) do `raw_asset` apontado
               pelo RAW_OBSERVATION_ID. E prova, nao facto: nunca entra no READY.
    """
    if not isinstance(export, dict) or export.get("EXPORT") != EXPORT_DA_SALA:
        raise LeiViolada("isto nao e um export %s" % EXPORT_DA_SALA)
    linhas = export.get("LINHAS")
    if not isinstance(linhas, list):
        raise LeiViolada("export sem LINHAS")
    itens, raw = [], {}
    for l in linhas:
        if not isinstance(l, dict):
            raise LeiViolada("linha do export que nao e objeto")
        obs = l.get("raw_observation_id")
        ready = {
            "ESTADO": SCI.PRONTO,
            "ITEM_ID": l.get("item_id"),
            "RAW_OBSERVATION_ID": NAO_SEI if obs in (None, "") else obs,
            "UNIVERSO": l.get("universo"),
            "ESTAGIO": l.get("estagio"),
            "TEXTO": l.get("texto"),
            "SOURCE_ID": l.get("source_id"),
            "SOURCE_LOCATION": l.get("source_location"),
            "FACT_LOCATION": l.get("fact_location"),
            "FACT_TIME": l.get("fact_time"),
            "FACT_TIME_BASIS": l.get("fact_time_basis"),
            "FACT_LOCATION_BASIS": l.get("fact_location_basis"),
            "PUBLISHED_AT": l.get("published_at"),
            "OBSERVED_AT": l.get("observed_at"),
            "PUBLISHED_AT_BASIS": l.get("published_at_basis"),
            "SOURCE_LOCATION_BASIS": l.get("source_location_basis"),
            "COMPLETUDE_TEMPO_LUGAR": _json(l.get("completude_tempo_lugar")),
            "TEMPO_LUGAR_EVIDENCIA": _json(l.get("tempo_lugar_evidencia")),
            "SOURCE_DECLARED_EVIDENCE_CLASS": l.get("source_declared_evidence_class"),
            "FATO": _json(l.get("fato")),
            # LOTE6-INTEGRA: o dono do READY (admissao/sala_de_espera.CAMPOS_DO_READY, D58
            # QUATRO-CHAVES-NA-SALA) leva a janela DENTRO do READY. Este ramo nasceu antes (60faa7cb)
            # e levava-a ao lado; o consumidor segue o dono — uma copia so.
            "JANELA_DECLARADA": _json(l.get("janela_declarada")),
            "CAPTURED_AT": l.get("captured_at"),
            "CORRIDA": l.get("run_id"),
            "ADMITIDO_POR": l.get("admitido_por"),
        }
        ready = {c: (NAO_SEI if ready[c] is None else ready[c]) for c in CI.CAMPOS_DO_READY}
        itens.append({"READY": ready})
        if obs not in (None, "") and str(obs) not in raw:
            raw[str(obs)] = {n: _v(l.get(c)) for c, n in COLUNAS_DO_RAW.items()}
    return {"SCHEMA": CONTRATO_DA_ENTRADA, "SINTETICA": export.get("SINTETICO") is True,
            "CORTE": _v(export.get("CORTE")), "ORIGEM": _v(export.get("ORIGEM")),
            "ITENS": itens, "RAW": raw}


def _conferir_entrada(entrada: dict) -> None:
    if not isinstance(entrada, dict) or entrada.get("SCHEMA") != CONTRATO_DA_ENTRADA:
        raise LeiViolada("entrada fora do contrato %s" % CONTRATO_DA_ENTRADA)
    for r in entrada.get("ITENS") or []:
        sobra = sorted(set(r) - {"READY"})
        if sobra:
            raise LeiViolada("IDENTIDADE_DE_FORA_DO_READY: registo com %s" % ", ".join(sobra))
        SCI.conferir_ready(r.get("READY"))


# ══════════════════════════════════════════════════════════════════════════
# 2 · D112(a) — O LUGAR DO FATO SO COM SUSTENTACAO EXPLICITA DA FONTE
# ══════════════════════════════════════════════════════════════════════════
def lugar_sustentado(valor, base, veio_de) -> dict:
    """-> {SUSTENTADO, VALOR, PORQUE}. Tres condicoes, e a terceira e a D112:

        o valor nao e ignorancia;  a base nao e ignorancia (INT-LAW-062);
        a ORIGEM do valor sustenta fato (`lugar_do_fato.sustenta_fato`:
        ESCRITO ou CITADO). DA_FONTE, DEDUZIDO, LISTA_TERRITORIAL e NAO SEI
        nao sustentam — o lugar da fonte nao e o lugar do fato.
    """
    if _ign(valor):
        return {"SUSTENTADO": False, "VALOR": NAO_SEI, "PORQUE": "valor NAO SEI"}
    if CI.base_ignorante(base):
        return {"SUSTENTADO": False, "VALOR": NAO_SEI, "VALOR_RECUSADO": valor,
                "PORQUE": "valor sem base"}
    origem = NAO_SEI if _ign(veio_de) else str(veio_de).strip().upper()
    ok, porque = LUGAR.sustenta_fato(origem, LUGAR.FACT)
    if not ok:
        return {"SUSTENTADO": False, "VALOR": NAO_SEI, "VALOR_RECUSADO": valor,
                "VEIO_DE": origem,
                "PORQUE": "D112: sem sustentacao explicita da fonte — " + porque}
    return {"SUSTENTADO": True, "VALOR": valor, "VEIO_DE": origem, "BASE": base,
            "PORQUE": porque}


#: Os blocos de JANELA_DECLARADA que sao LUGAR (e so esses passam pela D112a).
LUGARES_DA_JANELA = ("REGIAO_DO_FATO", WIN.CHAVE_DA_SUBAREA)


def aplicar_d112_lugar(registo: dict) -> tuple:
    """-> (ready_para_as_capacidades, janela_para_a_cap_win, relatorio).

    O READY e a janela ORIGINAIS nao mudam (a corrida le-os como vieram). As
    capacidades recebem uma COPIA onde o lugar sem sustentacao explicita virou
    NAO SEI — com o valor recusado e o porque no relatorio, nunca apagado.
    """
    ready = dict(registo["READY"])
    evid = ready.get("TEMPO_LUGAR_EVIDENCIA")
    evid = evid if isinstance(evid, dict) else {}
    rel = {"FACT_LOCATION": lugar_sustentado(ready.get("FACT_LOCATION"),
                                             ready.get("FACT_LOCATION_BASIS"),
                                             evid.get("FACT_LOCATION_VEIO_DE"))}
    if not rel["FACT_LOCATION"]["SUSTENTADO"] and not _ign(ready.get("FACT_LOCATION")):
        # a CAP-SCI le o local pela BASE: sem base, NAO SEI com o valor a vista.
        ready["FACT_LOCATION_BASIS"] = NAO_SEI + " — " + rel["FACT_LOCATION"]["PORQUE"]
    jd = ready.get("JANELA_DECLARADA")
    jd = json.loads(json.dumps(jd)) if isinstance(jd, dict) else {}
    for campo in LUGARES_DA_JANELA:
        bloco = jd.get(campo)
        if not isinstance(bloco, dict):
            continue
        r = lugar_sustentado(bloco.get("VALOR"), bloco.get("BASE"), bloco.get("VEIO_DE"))
        rel["JANELA_DECLARADA." + campo] = r
        if not r["SUSTENTADO"]:
            jd[campo] = dict(bloco, VALOR=NAO_SEI, D112=r["PORQUE"])
    if jd:
        ready["JANELA_DECLARADA"] = jd     # a copia das capacidades leva a janela JA passada pela D112a
    return ready, jd, rel


# ══════════════════════════════════════════════════════════════════════════
# 3 · A TRIAGEM — estudo ou observacao, pelo FATO e nunca pelo texto
# ══════════════════════════════════════════════════════════════════════════
def e_estudo(ready: dict) -> tuple:
    """-> (e_estudo, porque). Estudo = o FATO declara DOI, TRIAL_ID ou uma
    especie cientifica do vocabulario da CAP-SCI. `SOURCE_DECLARED_EVIDENCE_CLASS`
    NAO decide: e a expectativa de quem publica, nao a especie deste item."""
    fato = ready.get("FATO") if isinstance(ready.get("FATO"), dict) else {}
    achado = []
    for chave in ("DOI", "TRIAL_ID"):
        v, de = SCI.ler_chave(fato, chave)
        if v != NAO_SEI:
            achado.append(de)
    esp, de = SCI._especie(fato)
    if esp in SCI.ESPECIES:
        achado.append(de)
    if achado:
        return True, "o FATO declara identidade de estudo: " + ", ".join(achado)
    return False, "o FATO nao declara DOI, TRIAL_ID nem especie cientifica"


# ══════════════════════════════════════════════════════════════════════════
# 4 · D112(e,f,g) — AS RELACOES, sobre as evidencias da CAP-WIN
# ══════════════════════════════════════════════════════════════════════════
_LIMITE = re.compile(r"(\d+(?:,\d+)?)\s*(?:(?:-|–|a|e)\s*(\d+(?:,\d+)?)\s*)?%")


def limites(oracao: str) -> tuple:
    """Os limites numericos que a FONTE escreveu numa condicao («4-5%», «10%»).
    O valor e o da fonte; ler o numero e a unica interpretacao, e e declarada."""
    return tuple(sorted({(a + ("-" + b if b else "") + "%") for a, b in _LIMITE.findall(str(oracao))}))


def _territorios(sub) -> tuple:
    """A subarea declarada (ja passada pela D112a) em territorios; NAO SEI = ()."""
    if _ign(sub) or sub == NAO_SEI:
        return ()
    return tuple(sorted({t.strip() for t in str(sub).split(",") if t.strip()}))


def _por_item(evs: list) -> dict:
    out = {}
    for e in evs:
        d = out.setdefault(e["ITEM_ID"], {
            "ITEM_ID": e["ITEM_ID"], "INSTITUICAO": e["SOURCE_ID"],
            "TERRITORIOS": _territorios(e["SUBAREA"]), "TIME_WINDOW": e["TIME_WINDOW"],
            "MANDA_NAO_TRATAR": bool(e["DOCUMENTO_MANDA_NAO_TRATAR"]),
            "DECLARADO": set(), "LIMITES": set(), "CONDICOES_COM_LIMITE": []})
        if e["WINDOW_TYPE"] in WIN.AGRONOMICOS:
            d["DECLARADO"].add(e["DECLARADO_PELA_FONTE"])
        if e["WINDOW_TYPE"] == WIN.THRESHOLD_WINDOW:
            lim = limites(e["WINDOW_CONDITION"])
            if lim:
                d["LIMITES"].update(lim)
                d["CONDICOES_COM_LIMITE"].append(e["WINDOW_CONDITION"])
    return out


def relacoes(janela: dict) -> list:
    """As tres relacoes da D112 dentro de UM par (cultura x problema x regiao)."""
    evs = janela.get("EVIDENCE") or []
    itens = _por_item(evs)
    par = [janela["CROP_ID"], janela["ISSUE_ID"], janela["REGION_ID"]]
    out = []

    # (e) MESMA REDACAO em N territorios = N aplicacoes / 1 instituicao
    redacoes = {}
    for e in evs:
        chave = WIN._n(e["WINDOW_CONDITION"])
        g = redacoes.setdefault(chave, {"TEXTO": e["WINDOW_CONDITION"], "POR": {}})
        inst = g["POR"].setdefault(e["SOURCE_ID"], {"ITENS": set(), "TERRITORIOS": set(),
                                                    "SEM_TERRITORIO": set()})
        inst["ITENS"].add(e["ITEM_ID"])
        ts = _territorios(e["SUBAREA"])
        inst["TERRITORIOS"].update(ts)
        if not ts:
            inst["SEM_TERRITORIO"].add(e["ITEM_ID"])
    for chave, g in sorted(redacoes.items()):
        n_itens = sum(len(i["ITENS"]) for i in g["POR"].values())
        n_terr = sum(len(i["TERRITORIOS"]) for i in g["POR"].values())
        if n_itens < 2 and n_terr < 2:
            continue
        por = []
        for inst, i in sorted(g["POR"].items()):
            por.append({
                "INSTITUICAO": inst, "ITENS": sorted(i["ITENS"]),
                "TERRITORIOS": sorted(i["TERRITORIOS"]),
                "APLICACOES": (len(i["TERRITORIOS"]) if not i["SEM_TERRITORIO"] else NAO_SEI),
                "INSTITUICOES": 1,
                "PORQUE_NAO_SEI": (sorted(i["SEM_TERRITORIO"]) and
                                   "item sem territorio sustentado: " + ", ".join(sorted(i["SEM_TERRITORIO"])))
                                  or None})
        out.append({
            "TIPO": MESMA_REDACAO, "PAR": par,
            # INT-LAW-078 so para a MESMA instituicao; a mesma redacao em casas diferentes a lei nao
            # qualifica (afirmacao_da_fonte.relacao: mesmo valor, outra casa = NAO_SEI, UNRESOLVED)
            "RELATION": REL_078 if len(por) == 1 else REL_NAO_SEI,
            "CONTRADICTION_STATUS": "NO" if len(por) == 1 else UNRESOLVED,
            "LEI": "INT-LAW-078",
            "DA_FONTE": {"REDACAO": g["TEXTO"]},
            "POR_INSTITUICAO": por,
            "INSTITUICOES": len(por),
            "INTERPRETACAO_DO_SISTEMA": (
                "a mesma redacao aplicada em N territorios pela mesma instituicao sao N "
                "aplicacoes de 1 instituicao: conta como 1 apoio, nunca como N fontes"
                + ("" if len(por) == 1 else
                   "; a mesma redacao em instituicoes diferentes NAO prova independencia "
                   "(texto comum provavel): INDEPENDENCIA_ENTRE_INSTITUICOES = NAO SEI")),
            "INDEPENDENCIA_ENTRE_INSTITUICOES": (None if len(por) == 1 else NAO_SEI),
        })

    # (f) LIMITES DIFERENTES = DIVERGENT, contradicao UNRESOLVED
    por_limite = {}
    for i in itens.values():
        if i["LIMITES"]:
            k = tuple(sorted(i["LIMITES"]))
            g = por_limite.setdefault(k, {"ITENS": [], "INSTITUICOES": set(), "CONDICOES": set()})
            g["ITENS"].append(i["ITEM_ID"])
            g["INSTITUICOES"].add(i["INSTITUICAO"])
            g["CONDICOES"].update(i["CONDICOES_COM_LIMITE"])
    if len(por_limite) > 1:
        casas = {c for g in por_limite.values() for c in g["INSTITUICOES"]}
        out.append({
            "TIPO": DIVERGENT, "PAR": par, "CONTRADICAO": UNRESOLVED,
            # INT-LAW-079: DIVERGENT_RECOMMENDATIONS e entre FONTES diferentes; a mesma casa com limites
            # diferentes e sem validade que os ordene a lei nao qualifica (NAO_SEI). UNRESOLVED nos dois.
            "RELATION": REL_DIVERGENT if len(casas) > 1 else REL_NAO_SEI,
            "CONTRADICTION_STATUS": UNRESOLVED, "LEI": "INT-LAW-079",
            "DA_FONTE": [{"LIMITE": list(k), "ITENS": sorted(g["ITENS"]),
                          "INSTITUICOES": sorted(g["INSTITUICOES"]),
                          "CONDICOES": sorted(g["CONDICOES"])}
                         for k, g in sorted(por_limite.items())],
            "INTERPRETACAO_DO_SISTEMA": (
                "as fontes escrevem limites diferentes para o mesmo par: o sistema NAO "
                "escolhe um, nao faz media e nao da razao a maioria; a contradicao fica "
                "aberta ate uma fonte ou o dono a resolver"),
        })

    # (g) MUDANCA DE RECOMENDACAO NO TEMPO = TEMPORAL_CHANGE (nao prova o campo)
    grupos = {}
    for i in itens.values():
        grupos.setdefault((i["INSTITUICAO"], i["TERRITORIOS"]), []).append(i)
    for (inst, terr), its in sorted(grupos.items()):
        com_tempo = sorted((i for i in its if i["TIME_WINDOW"]),
                           key=lambda i: (i["TIME_WINDOW"]["INICIO"], i["ITEM_ID"]))
        sem_tempo = [i["ITEM_ID"] for i in its if not i["TIME_WINDOW"]]
        for a, b in zip(com_tempo, com_tempo[1:]):
            if a["TIME_WINDOW"]["FIM"] >= b["TIME_WINDOW"]["INICIO"]:
                continue   # tempos que se tocam nao sao «antes e depois»
            sa = {"MANDA_NAO_TRATAR": a["MANDA_NAO_TRATAR"], "DECLARADO": sorted(a["DECLARADO"])}
            sb = {"MANDA_NAO_TRATAR": b["MANDA_NAO_TRATAR"], "DECLARADO": sorted(b["DECLARADO"])}
            if sa == sb:
                continue
            out.append({
                "TIPO": TEMPORAL_CHANGE, "PAR": par, "INSTITUICAO": inst,
                "RELATION": REL_TEMPORAL, "CONTRADICTION_STATUS": "NO",
                "CONCLUIR_MUDANCA_DO_CAMPO": False, "LEI": "INT-LAW-079",
                "TERRITORIOS": list(terr) or NAO_SEI,
                "DE": a["ITEM_ID"], "PARA": b["ITEM_ID"],
                "DA_FONTE": {"ANTES": dict(sa, TIME_WINDOW=a["TIME_WINDOW"]),
                             "DEPOIS": dict(sb, TIME_WINDOW=b["TIME_WINDOW"])},
                "INTERPRETACAO_DO_SISTEMA": (
                    "a recomendacao da mesma instituicao, no mesmo territorio, mudou entre "
                    "dois periodos"),
                "NAO_PROVA": "MUDANCA_NO_CAMPO — a recomendacao mudou no tempo; se o campo "
                             "mudou, esta relacao nao o diz",
                "SEM_TEMPO_NAO_ORDENADOS": sem_tempo or None,
            })
    return out


# ══════════════════════════════════════════════════════════════════════════
# 5 · D112(b,d) — ENTITY_SOURCE e FONTE x INTERPRETACAO, objeto a objeto
# ══════════════════════════════════════════════════════════════════════════
_CAMPO_DA_JANELA = {"CROP_ID": "CULTURA", "ISSUE_ID": "PROBLEMA",
                    "REGION_ID": "REGIAO_DO_FATO", "DATE_OR_STAGE": "FASE"}


def _entidade(valor, fonte: str, por_item: list, extra: dict | None = None) -> dict:
    if valor == NAO_SEI or _ign(valor):
        return {"VALOR": NAO_SEI, "ENTITY_SOURCE": NAO_SEI,
                "PORQUE": "evidencia insuficiente: nenhuma fonte o declara com base (D112c)"}
    return dict({"VALOR": valor, "ENTITY_SOURCE": fonte, "POR_ITEM": por_item}, **(extra or {}))


def _prova(ready: dict, linha: dict, raw: dict) -> dict:
    """Um elemento de PROVA como o pote v2 o le. PUBLICADO_EM (nome do pote) e
    PUBLISHED_AT (nome da Sala) sao o MESMO campo do READY, e nunca o tempo do
    facto: FACT_TIME e o que a corrida ancorou, ou NAO SEI."""
    r = raw.get(str(ready.get("RAW_OBSERVATION_ID"))) or {}
    pub = _v(ready.get("PUBLISHED_AT"))
    return {
        "ITEM_ID": ready["ITEM_ID"],
        "CORRIDA_UPSTREAM": _v(linha.get("CORRIDA_UPSTREAM")),
        "RAW_OBSERVATION_ID": ready.get("RAW_OBSERVATION_ID"),
        "SOURCE_ID": ready.get("SOURCE_ID"),
        "DOCUMENT_ID": _v(r.get("DOCUMENT_ID")),
        "URL": _v(r.get("URL")),
        "PUBLICADO_EM": pub,
        "PUBLISHED_AT": pub,
        "COLHIDO_EM": _v(ready.get("CAPTURED_AT")),
        "FACT_TIME": _v(linha.get("FACT_TIME")),
    }


def _admite(linha: dict, especie: str) -> bool:
    """A regra de prova do pote v2 (herdada da ponte v1): so G0 = PASSOU prova;
    o facto sobre o futuro prova-se pelo item que G0 bloqueou SO por ser futuro."""
    if especie == FUTURO:
        return linha.get("G0") == "BLOQUEADO_EM_G0" and linha.get("G0_FALTA") == [G0_FUTURO_POR_DESENHO]
    return linha.get("G0") == "PASSOU"


def _objeto_da_janela(j: dict, ctx: dict, rels: list) -> tuple:
    """Uma CROP_WINDOW -> (objeto do pote | None, motivo se nao vai)."""
    ids = sorted({e["ITEM_ID"] for e in j["EVIDENCE"]})
    provas, sem_g0 = [], []
    for iid in ids:
        linha = ctx["LINHA"][iid]
        if _admite(linha, SINAL):
            provas.append(_prova(ctx["READY"][iid], linha, ctx["RAW"]))
        else:
            sem_g0.append(iid)
    if not provas:
        return None, ("nenhuma evidencia da janela passou G0: o pote v2 so admite prova "
                      "com G0 = PASSOU (itens: %s)" % ", ".join(ids or [NAO_SEI]))
    ent = {}
    for chave, campo in _CAMPO_DA_JANELA.items():
        por_item = []
        for iid in ids:
            bloco = (ctx["JANELA"][iid] or {}).get(campo)
            if isinstance(bloco, dict) and not _ign(bloco.get("VALOR")):
                por_item.append({"ITEM_ID": iid, "VALOR": bloco.get("VALOR"),
                                 "VEIO_DE": _v(bloco.get("VEIO_DE")), "BASE": _v(bloco.get("BASE"))})
        valor = {"CROP_ID": j["CROP_ID"], "ISSUE_ID": j["ISSUE_ID"], "REGION_ID": j["REGION_ID"]}.get(chave)
        if chave == "DATE_OR_STAGE":
            fases = [f for f in j["PHENOLOGY_STAGE"] if f != NAO_SEI]
            valor = ",".join(fases) if fases else NAO_SEI
        ent[chave] = _entidade(valor, "JANELA_DECLARADA." + campo, por_item,
                               {"D112_LUGAR": "SUSTENTADO"} if chave == "REGION_ID" else None)
    ent["SUBAREA"] = _entidade(",".join(s for s in j["SUBAREAS"] if s != NAO_SEI) or NAO_SEI,
                               "JANELA_DECLARADA." + WIN.CHAVE_DA_SUBAREA,
                               [{"ITEM_ID": e["ITEM_ID"], "VALOR": e["SUBAREA"]} for e in j["EVIDENCE"]
                                if e["SUBAREA"] != NAO_SEI])
    divergentes = [r for r in rels if r["TIPO"] == DIVERGENT]
    resultado, porque = j["RESULT"], list(j["WHY"])
    if divergentes and resultado == WIN.ACT_NOW:
        # D112(f) so pode BAIXAR: limites em aberto nao sustentam «agir agora».
        resultado = WIN.NO_DEFENSIBLE_ACTION_YET
        porque.append("D112: limites divergentes entre fontes, contradicao UNRESOLVED")
    da_fonte = {
        "CONDICOES": j["WINDOW_CONDITIONS"],
        "RESTRICOES_ADMINISTRATIVAS": j["ADMINISTRATIVE_CONSTRAINTS"],
        "A_FONTE_MANDA_NAO_TRATAR": j["SOURCE_SAYS_DO_NOT_TREAT"],
        "DECLARADO_POR_ITEM": sorted({(e["ITEM_ID"], e["WINDOW_TYPE"], e["DECLARADO_PELA_FONTE"],
                                       e["METODO_DECLARADO"]) for e in j["EVIDENCE"]}),
    }
    interp = {
        "WINDOW_DEFINED": j["WINDOW_DEFINED"], "WINDOW_TYPES": j["WINDOW_TYPES"],
        "WINDOW_OPEN_NOW": j["WINDOW_OPEN_NOW"], "METHOD": j["METHOD"],
        "TEMPORAL_STATE": j["TEMPORAL_STATE"], "SUPPORTS": j["SUPPORTS"],
        "RESULT": resultado, "RESULT_DA_CAP_WIN": j["RESULT"], "WHY": porque,
        "READING": j["READING"], "LIMITATIONS": j["LIMITATIONS"],
        "CONTRADICTIONS": j["CONTRADICTIONS"], "RELACOES_D112": rels,
    }
    fora = {"ESPECIE_DO_MOTOR": "ANALYTIC_JUDGMENT/CROP_WINDOW", "CAPACIDADE": WIN.CAPACIDADE,
            "CROP_WINDOW_ID": j["CROP_WINDOW_ID"], "ENTITY_SOURCE": ent,
            "DA_FONTE": da_fonte, "INTERPRETACAO_DO_SISTEMA": interp,
            "EVIDENCIA_SEM_G0_FORA_DA_PROVA": sem_g0}
    chaves = {k: ent[k]["VALOR"] for k in CHAVES_DO_POTE["windows"]}
    chaves.update({k: v for k, v in fora.items()})
    contradiz = "; ".join(
        ["DIVERGENT/UNRESOLVED: " + " x ".join("%s (%s)" % (",".join(g["LIMITE"]), ",".join(g["INSTITUICOES"]))
                                              for g in r["DA_FONTE"]) for r in divergentes]
        + ["CONTRADICTS %s->%s" % (c["DE"], c["PARA"]) for c in j["CONTRADICTIONS"]]) or None
    incerteza = "; ".join(j["LIMITATIONS"]
                          + ["TEMPORAL_CHANGE %s->%s (nao prova mudanca no campo)" % (r["DE"], r["PARA"])
                             for r in rels if r["TIPO"] == TEMPORAL_CHANGE]) or None
    obj = {"OBJETO_ID": "R7-" + j["CROP_WINDOW_ID"], "ESPECIE": SINAL,
           "ESTADO": ESTADO_TRANSPORTAVEL, "CHAVES": chaves, "PROVA": provas,
           "PORQUE": " · ".join(porque + ([j["READING"]] if j["READING"] else [])),
           "CONTRADIZ": contradiz, "INCERTEZA": incerteza,
           # D123: a ligacao que a CAP-WIN recebeu da porta — transportada, nunca recalculada
           "LIGACAO_ADAMA": j["LIGACAO_ADAMA"]}
    return obj, None


def _objeto_do_estudo(e: dict, sci: dict, ctx: dict) -> tuple:
    iid = e["ITEM_ID"]
    ready, linha = ctx["READY"][iid], ctx["LINHA"][iid]
    if not _admite(linha, SINAL):
        return None, "estudo %s nao passou G0 (%s): o pote v2 so admite prova com G0 = PASSOU" % (
            iid, ", ".join(linha.get("G0_FALTA") or []))
    fato = ready.get("FATO") if isinstance(ready.get("FATO"), dict) else {}

    def de(chave):
        return SCI.ler_chave(fato, chave)[1]
    autores = e["CHAVES_DE_INDEPENDENCIA"]["AUTOR"]
    insts = e["CHAVES_DE_INDEPENDENCIA"]["INSTITUICAO"]
    local, periodo = e["LOCAL_DO_ESTUDO"], e["PERIODO_DO_ESTUDO"]
    mol = e["MOLECULA"] if e["MOLECULA"] != NAO_SEI else NAO_SEI
    item = [{"ITEM_ID": iid}]
    ent = {
        "DOI": _entidade(e["DOI"], de("DOI"), item),
        "TRIAL_ID": _entidade(e["TRIAL_ID"], de("TRIAL_ID"), item),
        "RESEARCHER_ORCID": _entidade(",".join(autores) or NAO_SEI, de("AUTORES"), item),
        "INSTITUTION_ID": _entidade(",".join(insts) or NAO_SEI, de("INSTITUICOES"), item,
                                    {"NAO_E_LUGAR": "afiliacao nunca e local do estudo (INT-LAW-102)"}),
        "MOLECULE": _entidade(",".join(mol) if mol != NAO_SEI else NAO_SEI, de("MOLECULA"), item),
        "CROP_ID": _entidade(e["CULTURA"], de("CULTURA"), item),
        "ISSUE_ID": _entidade(e["PROBLEMA"], de("PROBLEMA"), item),
        "STUDY_LOCATION": _entidade(local["VALOR"] if local["ESTADO"] == "PROVADO" else NAO_SEI,
                                    "READY.FACT_LOCATION", item, {"D112_LUGAR": "SUSTENTADO"}),
        "STUDY_PERIOD": _entidade(periodo["VALOR"] if periodo["ESTADO"] == "PROVADO" else NAO_SEI,
                                  "READY.FACT_TIME", item),
    }
    if local["ESTADO"] != "PROVADO":
        ent["STUDY_LOCATION"]["PORQUE"] = local.get("PORQUE", NAO_SEI)
    ligacao = next((x for x in sci["LIGACOES"] if x["ITEM_ID"] == iid), None)
    replic = [r for r in sci["REPLICACAO"] if iid in r["ESTUDOS"]]
    da_fonte = {"FATO": {k: v for k, v in fato.items()}, "PUBLISHED_AT": _v(ready.get("PUBLISHED_AT")),
                "PUBLICACAO_NAO_E_PERIODO_DO_ESTUDO": True}
    interp = {"ESPECIE_DO_ESTUDO": e["ESPECIE"], "FORCA": e["FORCA"],
              "APLICABILIDADE": e["APLICABILIDADE"], "LEITURA": e["LEITURA"],
              "REPLICACAO": replic, "LIGACAO_TEMATICA": ligacao or NAO_SEI,
              "NAO_E": e["NAO_E"]}
    fora = {"ESPECIE_DO_MOTOR": "ANALYTIC_JUDGMENT/ESTUDO", "CAPACIDADE": SCI.CAPACIDADE,
            "ENTITY_SOURCE": ent, "DA_FONTE": da_fonte, "INTERPRETACAO_DO_SISTEMA": interp}
    chaves = {k: ent[k]["VALOR"] for k in CHAVES_DO_POTE["science"]}
    chaves.update(fora)
    contra = [r for r in replic if r["CONTRADICAO_COM"]]
    obj = {"OBJETO_ID": "R7-SCI-" + hashlib.sha256(
               (ctx["RUN_ID"] + "|" + str(iid)).encode()).hexdigest()[:16],
           "ESPECIE": SINAL, "ESTADO": ESTADO_TRANSPORTAVEL, "CHAVES": chaves,
           "PROVA": [_prova(ready, linha, ctx["RAW"])],
           "PORQUE": "estudo: forca %s, aplicabilidade %s, especie %s, leitura %s — nunca incidencia "
                     "de campo" % (e["FORCA"]["NIVEL"], e["APLICABILIDADE"]["ESTADO"], e["ESPECIE"],
                                   e["LEITURA"]),
           "CONTRADIZ": ("; ".join("%s %s contradiz %s" % (r["MOLECULA"], r["DIRECAO"], ",".join(r["CONTRADICAO_COM"]))
                                   for r in contra) or None),
           "INCERTEZA": ("falta: " + ", ".join(e["APLICABILIDADE"]["FALTA"])
                         if e["APLICABILIDADE"]["FALTA"] else None),
           # D123: a ligacao que a CAP-SCI recebeu da porta — transportada, nunca recalculada
           "LIGACAO_ADAMA": e["LIGACAO_ADAMA"]}
    return obj, None


def _objeto_do_futuro(f: dict, ctx: dict) -> tuple:
    iid = f["ITEM_ID"]
    ready, linha = ctx["READY"][iid], ctx["LINHA"][iid]
    if not _admite(linha, FUTURO):
        return None, ("%s: G0 bloqueou por mais do que o futuro (%s): nao prova um facto "
                      "presente sobre o futuro" % (iid, ", ".join(linha.get("G0_FALTA") or [])))
    jd = ctx["JANELA"].get(iid) or {}
    item = [{"ITEM_ID": iid}]
    ent = {}
    for chave, campo in (("CROP_ID", "CULTURA"), ("ISSUE_ID", "PROBLEMA"), ("REGION_ID", "REGIAO_DO_FATO")):
        b = jd.get(campo) if isinstance(jd.get(campo), dict) else {}
        if campo == "PROBLEMA":
            # CHAVE-PROBLEMA: o PROBLEMA le-se SO pelo contrato PROBLEMA/v1 (o mesmo leitor da CAP-WIN)
            valor, _porque = AFIRMACAO.problema_da_chave(b or None, texto=str(ready.get("TEXTO") or ""))
            ok = valor is not None
        else:
            valor = b.get("VALOR")
            ok = not _ign(valor) and not CI.base_ignorante(b.get("BASE"))
        ent[chave] = _entidade(valor if ok else NAO_SEI, "JANELA_DECLARADA." + campo,
                               [dict(item[0], VEIO_DE=_v(b.get("VEIO_DE")))])
    lugar = ctx["D112"][iid]["FACT_LOCATION"]
    ent["FACT_LOCATION"] = _entidade(lugar["VALOR"], "READY.FACT_LOCATION", item)
    ent["FACT_TIME"] = _entidade(_v(ready.get("FACT_TIME")), "READY.FACT_TIME", item)
    ent["FACT_TIME_BASIS"] = _entidade(_v(ready.get("FACT_TIME_BASIS")), "READY.FACT_TIME_BASIS", item)
    fora = {"ESPECIE_DO_MOTOR": "FACTO_PRESENTE_SOBRE_O_FUTURO (corrida G0/v4, D14)",
            "ENTITY_SOURCE": ent,
            "DA_FONTE": {"FACT_TIME": _v(ready.get("FACT_TIME")), "CAPTURED_AT": _v(ready.get("CAPTURED_AT"))},
            "INTERPRETACAO_DO_SISTEMA": {"NAO_E": f.get("NAO_E"),
                                         "LEITURA": "a data do facto e depois da captura: e um facto "
                                                    "PRESENTE sobre o futuro, nao uma oportunidade"}}
    chaves = {k: ent[k]["VALOR"] for k in CHAVES_DO_POTE["future"]}
    chaves.update(fora)
    return {"OBJETO_ID": "R7-FUT-" + hashlib.sha256((ctx["RUN_ID"] + "|" + str(iid)).encode()).hexdigest()[:16],
            "ESPECIE": FUTURO, "ESTADO": ESTADO_TRANSPORTAVEL, "CHAVES": chaves,
            "PROVA": [_prova(ready, linha, ctx["RAW"])],
            "PORQUE": "facto presente sobre o futuro (G0 bloqueou so por FACT_TIME depois da captura)",
            "CONTRADIZ": None, "INCERTEZA": None,
            # D123: pela porta, com a cultura/problema da JANELA_DECLARADA (so com procedencia)
            "LIGACAO_ADAMA": PORTA.ligacao_adama(ctx["REF"], {
                "CULTURA": ent["CROP_ID"]["VALOR"], "PROBLEMA": ent["ISSUE_ID"]["VALOR"],
                "VEM_DE": {"CULTURA": "JANELA_DECLARADA.CULTURA", "PROBLEMA": "JANELA_DECLARADA.PROBLEMA"}})}, None


def _rendimentos(livro: dict, ctx: dict, objetos: dict) -> tuple:
    """RENDIMENTO_DE_FONTE contado da LINEAGE da corrida (nao se reconta nada)."""
    por_fonte, nao_vao = {}, []
    for l in livro["LINEAGE"]:
        por_fonte.setdefault(str(l.get("SOURCE_ID")), []).append(l)
    produzidos = {}
    for objs in objetos.values():
        for o in objs:
            for s in {str(p["SOURCE_ID"]) for p in o["PROVA"]}:
                produzidos[s] = produzidos.get(s, 0) + 1
    out = []
    for fonte, ls in sorted(por_fonte.items()):
        passaram = [l for l in ls if l.get("G0") == "PASSOU"]
        oid = "R7-SRC-" + hashlib.sha256((ctx["RUN_ID"] + "|" + fonte).encode()).hexdigest()[:16]
        if _ign(fonte) or not passaram:
            nao_vao.append({"OBJETO_ID": oid, "COMPARTIMENTO": "sources",
                            "MOTIVO": "RENDIMENTO_SEM_PROVA",
                            "DETALHE": "fonte %s: nenhum item passou G0 — o rendimento prova-se so "
                                       "pela propria fonte" % fonte})
            continue
        # a prova do rendimento cita os itens da fonte que passaram G0 e cujo RAW
        # tem DOCUMENT_ID; os outros contam no numero, e ficam ditos a parte (o
        # pote recusa o objeto inteiro por um elemento de prova sem DOCUMENT_ID).
        com_doc = [l for l in passaram if not _ign((ctx["RAW"].get(
            str(l.get("RAW_OBSERVATION_ID"))) or {}).get("DOCUMENT_ID"))]
        if not com_doc:
            nao_vao.append({"OBJETO_ID": oid, "COMPARTIMENTO": "sources",
                            "MOTIVO": "RENDIMENTO_SEM_PROVA",
                            "DETALHE": "fonte %s: nenhum item que passou G0 tem DOCUMENT_ID no RAW"
                                       % fonte})
            continue
        item = [{"ITEM_ID": l["ITEM_ID"]} for l in ls]
        ent = {"SOURCE_ID": _entidade(fonte, "LINEAGE.SOURCE_ID", item),
               "ITENS_LIDOS": _entidade(len(ls), "LINEAGE (contagem da corrida)", item),
               "ITENS_QUE_PASSARAM_G0": _entidade(len(passaram), "LINEAGE.G0 (contagem da corrida)", item),
               "OBJETOS_PRODUZIDOS": _entidade(produzidos.get(fonte, 0), "ITENS_POR_FERRAMENTA desta saida", item)}
        fora = {"ESPECIE_DO_MOTOR": "RENDIMENTO_DE_FONTE", "ENTITY_SOURCE": ent,
                "PASSARAM_G0_SEM_DOCUMENT_ID_FORA_DA_PROVA": sorted(
                    str(l["ITEM_ID"]) for l in passaram if l not in com_doc),
                "DA_FONTE": {}, "INTERPRETACAO_DO_SISTEMA": {"LEITURA": "contagem desta corrida; zero nao "
                                                                     "prova ausencia no mundo"}}
        chaves = {k: ent[k]["VALOR"] for k in CHAVES_DO_POTE["sources"]}
        chaves.update(fora)
        out.append({"OBJETO_ID": oid, "ESPECIE": RENDIMENTO, "ESTADO": ESTADO_TRANSPORTAVEL,
                    "CHAVES": chaves,
                    "PROVA": [_prova(ctx["READY"][str(l["ITEM_ID"])], l, ctx["RAW"]) for l in com_doc],
                    "PORQUE": "rendimento da fonte nesta corrida", "CONTRADIZ": None, "INCERTEZA": None,
                    # D123: rendimento de fonte nao tem cultura nem substancia: NAO_SEI dito pela porta
                    "LIGACAO_ADAMA": PORTA.ligacao_adama(ctx["REF"], {"VEM_DE": {}})})
    return out, nao_vao


# ══════════════════════════════════════════════════════════════════════════
# 6 · A RODADA
# ══════════════════════════════════════════════════════════════════════════
def rodar(entrada: dict, hoje: date, source_head=None, referencia: dict | None = None) -> dict:
    """UMA corrida, as duas capacidades, a saida para o pote v2 — conferida."""
    if not isinstance(hoje, date):
        raise LeiViolada("sem HOJE declarado nao ha «agora»")
    _conferir_entrada(entrada)
    registos = entrada["ITENS"]
    prontos = [r["READY"] for r in registos]
    ids = [str(p.get("ITEM_ID")) for p in prontos]
    if len(set(ids)) != len(ids):
        raise LeiViolada("ITEM_ID repetido no corte: nao serve de endereco da prova")
    livro = CI.correr(PERGUNTA, prontos,
                      universo={"ITENS_NO_CORTE": len(prontos), "CORTE": entrada.get("CORTE", NAO_SEI)})
    if livro["RESULT_STATE"] not in ("DONE", "REUSED"):
        raise LeiViolada("a corrida terminou em %s: %s" % (livro["RESULT_STATE"], livro["ERRORS"]))
    run_id = livro["INTELLIGENCE_RUN_ID"]

    d112, ready_cap, janelas, triagem, para_win, para_sci = {}, [], {}, {}, {}, {}
    for r in registos:
        iid = str(r["READY"]["ITEM_ID"])
        rc, jd, rel = aplicar_d112_lugar(r)
        d112[iid], janelas[iid] = rel, jd
        ready_cap.append(rc)
        estudo, porque = e_estudo(r["READY"])
        triagem[iid] = {"CAPACIDADE": SCI.CAPACIDADE if estudo else WIN.CAPACIDADE, "PORQUE": porque}
        (para_win if estudo else para_sci)[r["READY"]["ITEM_ID"]] = (
            "TRIAGEM: estudo — vai a CAP-SCI; estudo nunca vira observacao de janela nem "
            "incidencia de campo (%s)" % porque if estudo else
            "TRIAGEM: nao e estudo — %s" % porque)

    itens_win = [dict(rc, JANELA_DECLARADA=janelas[str(rc["ITEM_ID"])],
                      URL=(entrada["RAW"].get(str(rc.get("RAW_OBSERVATION_ID"))) or {}).get("URL", NAO_SEI))
                 for rc in ready_cap]
    # UMA abertura da porta, e a MESMA referencia para as duas capacidades: a janela e a
    # ciencia nunca respondem sobre produto com edicoes diferentes (D116).
    ref = referencia if referencia is not None else PORTA.abrir(hoje=hoje)
    win = WIN.julgar(livro, itens_win, hoje, fora=para_win, referencia=ref)
    sci = SCI.julgar(livro, ready_cap, ref, triados_fora=para_sci)

    ctx = {"RUN_ID": run_id, "RAW": entrada["RAW"], "D112": d112, "JANELA": janelas, "REF": ref,
           "READY": {str(p["ITEM_ID"]): p for p in prontos},
           "LINHA": {str(l["ITEM_ID"]): l for l in livro["LINEAGE"]}}
    objetos = {"windows": [], "science": [], "future": []}
    nao_vao, todas_rel = [], []
    for j in win["CROP_WINDOWS"]:
        rels = relacoes(j)
        todas_rel += rels
        o, motivo = _objeto_da_janela(j, ctx, rels)
        (objetos["windows"].append(o) if o else
         nao_vao.append({"OBJETO_ID": "R7-" + j["CROP_WINDOW_ID"], "COMPARTIMENTO": "windows",
                         "MOTIVO": "SEM_PROVA_ADMITIDA_PELO_POTE", "DETALHE": motivo}))
    for e in sci["ESTUDOS"]:
        o, motivo = _objeto_do_estudo(e, sci, ctx)
        (objetos["science"].append(o) if o else
         nao_vao.append({"OBJETO_ID": str(e["ITEM_ID"]), "COMPARTIMENTO": "science",
                         "MOTIVO": "SEM_PROVA_ADMITIDA_PELO_POTE", "DETALHE": motivo}))
    for f in livro["FUTURE_DATED_FACTS"]:
        o, motivo = _objeto_do_futuro(f, ctx)
        (objetos["future"].append(o) if o else
         nao_vao.append({"OBJETO_ID": str(f["ITEM_ID"]), "COMPARTIMENTO": "future",
                         "MOTIVO": "FUTURO_COM_OUTRA_FALTA", "DETALHE": motivo}))
    fontes, sem_rend = _rendimentos(livro, ctx, objetos)
    objetos["sources"] = fontes
    nao_vao += sem_rend

    requisitos = ([dict(q, FERRAMENTA="windows", CAPACIDADE=WIN.CAPACIDADE) for q in win["REQUIREMENTS"]]
                  + [dict(q, CAPACIDADE="CORRIDA_G0") for q in livro["REQUIREMENTS"]])
    saida = {
        # ⚠️ INTELLIGENCE_RUN_ID NO TOPO: a primeira chave. Um pote e de UMA corrida.
        "INTELLIGENCE_RUN_ID": run_id,
        "SCHEMA": CONTRATO,
        "CONTRATO_DE_SAIDA_PARA": POTE_ALVO,
        "MARCA": MARCA, "NAO_PARA_CLIENTE": True,
        "SOURCE_HEAD": _v(source_head),
        "CORTE": entrada.get("CORTE", NAO_SEI),
        "RESULT_STATE": livro["RESULT_STATE"],
        "SINTETICA": entrada.get("SINTETICA") is True,
        "HOJE": hoje.isoformat(),
        "REFERENCIA_ADAMA": PORTA.carimbo(ref) if PORTA.lida(ref) else ref.get("CARIMBO", PORTA.carimbo(ref)),
        "LINEAGE": livro["LINEAGE"],
        # Os SINAIS da corrida ficam no livro (CORRIDA.SIGNALS): o pote recusaria
        # sinal sem ferramenta, e o motor nao escolhe ferramenta por eles.
        "SIGNALS": [],
        "GAPS": [],
        "REQUIREMENTS": requisitos,
        "ITENS_POR_FERRAMENTA": objetos,
        "NAO_ENVIADOS_AO_POTE": nao_vao,
        "CAPACIDADES_EXECUTADAS": {WIN.CAPACIDADE: {"VERSION": WIN.VERSAO, "RUN": run_id},
                                   SCI.CAPACIDADE: {"VERSION": SCI.CONTRATO, "RUN": run_id}},
        "TRIAGEM": triagem,
        "D112": {"REGRAS": list(D112), "LUGAR": d112, "RELACOES": todas_rel},
        "CAP_WIN": win,
        "CAP_SCI": sci,
        "CORRIDA": livro,
    }
    saida = json.loads(json.dumps(saida, ensure_ascii=False, default=list))
    violacoes = conferir_saida(saida)
    if violacoes:
        raise LeiViolada("saida reprovada no portao do motor: " + "; ".join(violacoes))
    return saida


# ══════════════════════════════════════════════════════════════════════════
# 7 · O PORTAO DA SAIDA — independente de `rodar`
# ══════════════════════════════════════════════════════════════════════════
def conferir_saida(saida: dict) -> list:
    """Lista de violacoes; vazia = passa. Le a saida como o pote a leria."""
    v = []
    if not isinstance(saida, dict) or not saida:
        return ["saida nao e objeto"]
    if next(iter(saida)) != "INTELLIGENCE_RUN_ID" or _ign(saida.get("INTELLIGENCE_RUN_ID")):
        v.append("INTELLIGENCE_RUN_ID tem de ser a primeira chave, com valor")
    for k in ("SOURCE_HEAD", "CORTE"):
        if k not in saida or (_ign(saida[k]) and saida[k] != NAO_SEI):
            v.append("cabecalho esconde %s" % k)
    linhas = {(str(l.get("CORRIDA_UPSTREAM")), str(l.get("ITEM_ID"))): l
              for l in saida.get("LINEAGE") or []}
    estudos = {i for i, t in (saida.get("TRIAGEM") or {}).items() if t.get("CAPACIDADE") == SCI.CAPACIDADE}
    texto = json.dumps(saida.get("ITENS_POR_FERRAMENTA"), ensure_ascii=False).upper()
    for p in SCI.LEITURAS_PROIBIDAS:
        if p in texto:
            v.append("leitura proibida na saida: " + p)
    for comp, objs in (saida.get("ITENS_POR_FERRAMENTA") or {}).items():
        if comp not in CHAVES_DO_POTE:
            v.append("%s: compartimento que este motor nao alimenta" % comp)
            continue
        for o in objs:
            oid = o.get("OBJETO_ID", "?")
            if o.get("ESPECIE") not in ESPECIES_EMITIDAS:
                v.append("%s/%s: especie %s nao e emitida por este motor" % (comp, oid, o.get("ESPECIE")))
            if o.get("ESTADO") != ESTADO_TRANSPORTAVEL:
                v.append("%s/%s: estado %s" % (comp, oid, o.get("ESTADO")))
            ch = o.get("CHAVES") or {}
            for k in ("ENTITY_SOURCE", "DA_FONTE", "INTERPRETACAO_DO_SISTEMA", "ESPECIE_DO_MOTOR"):
                if k not in ch:
                    v.append("%s/%s: falta %s (D112)" % (comp, oid, k))
            ent = ch.get("ENTITY_SOURCE") or {}
            for k in CHAVES_DO_POTE[comp]:
                val = ch.get(k)
                if _ign(val) and val != NAO_SEI:
                    v.append("%s/%s: %s esconde a ignorancia" % (comp, oid, k))
                e = ent.get(k)
                if not isinstance(e, dict) or e.get("VALOR") != val:
                    v.append("%s/%s: %s sem ENTITY_SOURCE que bata com o valor" % (comp, oid, k))
                elif val != NAO_SEI and _ign(e.get("ENTITY_SOURCE")):
                    v.append("%s/%s: %s com valor e sem procedencia (D112b)" % (comp, oid, k))
            if not o.get("PROVA"):
                v.append("%s/%s: objeto sem prova" % (comp, oid))
            # D123: todo objeto leva a ligacao ADAMA, e ela tem de ter saido da porta
            for x in PORTA.conferir_ligacao(o.get("LIGACAO_ADAMA")):
                v.append("%s/%s: %s" % (comp, oid, x))
            for p in o.get("PROVA") or []:
                for k in ("ITEM_ID", "CORRIDA_UPSTREAM", "RAW_OBSERVATION_ID", "SOURCE_ID",
                          "DOCUMENT_ID", "URL", "PUBLICADO_EM", "PUBLISHED_AT", "COLHIDO_EM", "FACT_TIME"):
                    if k not in p or (_ign(p[k]) and p[k] != NAO_SEI):
                        v.append("%s/%s: prova esconde %s" % (comp, oid, k))
                if p.get("PUBLISHED_AT") != p.get("PUBLICADO_EM"):
                    v.append("%s/%s: PUBLISHED_AT e PUBLICADO_EM divergem" % (comp, oid))
                l = linhas.get((str(p.get("CORRIDA_UPSTREAM")), str(p.get("ITEM_ID"))))
                if l is None:
                    v.append("%s/%s: prova %s fora da LINEAGE" % (comp, oid, p.get("ITEM_ID")))
                    continue
                if not _admite(l, o.get("ESPECIE")):
                    v.append("%s/%s: prova %s nao admitida em G0" % (comp, oid, p.get("ITEM_ID")))
                if str(p.get("FACT_TIME")) != str(_v(l.get("FACT_TIME"))):
                    v.append("%s/%s: FACT_TIME da prova nao e o da corrida (publicacao nao e facto)"
                             % (comp, oid))
                if comp == "windows" and str(p.get("ITEM_ID")) in estudos:
                    v.append("%s/%s: ESTUDO %s numa janela — estudo nunca vira incidencia de campo"
                             % (comp, oid, p.get("ITEM_ID")))
    return v


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="motor das capacidades (CAP-WIN + CAP-SCI) sobre um export da Sala")
    ap.add_argument("export")
    ap.add_argument("--hoje", required=True, help="AAAA-MM-DD: o «agora» declarado")
    ap.add_argument("--source-head", default=None, help="o commit da arvore que corre o motor")
    ap.add_argument("--saida", default=None)
    a = ap.parse_args(argv)
    dado = json.loads(Path(a.export).read_text(encoding="utf-8"))
    entrada = dado if dado.get("SCHEMA") == CONTRATO_DA_ENTRADA else entrada_do_export(dado)
    saida = rodar(entrada, date.fromisoformat(a.hoje), a.source_head)
    texto = json.dumps(saida, ensure_ascii=False, indent=1) + "\n"
    if a.saida:
        Path(a.saida).write_text(texto, encoding="utf-8")
    else:
        sys.stdout.write(texto)
    n = {k: len(v) for k, v in saida["ITENS_POR_FERRAMENTA"].items()}
    print("%s · %s · corrida %s · objetos %s · nao enviados %d · requisitos %d"
          % (MARCA, CONTRATO, saida["INTELLIGENCE_RUN_ID"], n, len(saida["NAO_ENVIADOS_AO_POTE"]),
             len(saida["REQUIREMENTS"])), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
