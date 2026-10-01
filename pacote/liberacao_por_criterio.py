#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LIBERACAO POR CRITERIO — o C8 automatico (decisao do dono D-C8-AUTO, Diretoria 30/09/2026 09:05).

    «Objeto que cumpra integralmente C1–C7, as regras vigentes de inteligencia, os requisitos do LAB e o contrato
     de exibicao pode receber C8 automaticamente. Objeto que nao cumpra fica bloqueado. Nao e necessaria minha
     aprovacao objeto por objeto.» (Luciano, dono)

Dono: Intelligence (a liberacao e da Intelligence, objeto por objeto — CONTRATO-LIBERACAO-POR-OBJETO-v2.2).
Nenhuma regua nova: C1..C7 sao as do contrato v2.2 (as mesmas de PARA-O-CASCO-R9/montar_r9.py), agora calculadas
por REGRA a partir do que o motor ja escreve no objeto (EVIDENCE_SPAN, FACT_TIME_BASIS com posicao, trecho do lugar,
prova ate ao RAW). O que mudou e SO o C8: deixa de ser uma frase do dono por objeto e passa a ser
`REGRA_C8_AUTO`, que so passa quando C1..C7 = PASSOU. Qualquer falha -> NAO_PARA_CLIENTE com o motivo gravado.

    C1 PROVA_DO_ARQUIVO          DOCUMENT_ID sabido; RAW_SHA256/RAW_STORAGE_PATH iguais aos da Sala; o byte e RELIDO no
                                 armazem e o sha256 bate; o trecho da afirmacao esta literal no texto do item.
    C2 DATA_PROPRIA              trecho da data literal no texto, na MESMA seccao (entre quebras \\f) da afirmacao;
                                 origem da data nunca calculada da publicacao (RELATIVO_D63 falha).
    C3 LUGAR_PROPRIO             trecho do lugar literal, na mesma seccao; lugar da fonte nunca e lugar do fato.
    C4 LIGACAO_ADAMA             `porta_da_referencia.conferir_ligacao` sem falhas e estado D123 valido.
    C5 SEM_DUPLICADO             nenhum outro objeto liberado com o mesmo item + mesmo trecho.
    C6 ESPECIE_DO_COMPARTIMENTO  tabela do gerador do dono (pote_intelligence_casco.COMPARTIMENTOS).
    C7 SO_SAIDA_DA_INTELLIGENCE  ESPECIE_DITA_POR = INTELLIGENCE e prova = item da Sala.
    C8 REGRA_C8_AUTO             PASSOU sse C1..C7 PASSOU (+ G0 da afirmacao PASSOU, regra vigente do motor).

Objetos sem afirmacao propria (rendimento de fonte, facto sobre o futuro sem lugar, sinal de documento inteiro)
falham C2/C3 por regra e ficam BLOQUEADOS — nunca ha liberacao por omissao (conferencia ausente = nao liberado).

    python pacote/liberacao_por_criterio.py --copia <pasta da copia so-leitura> --afirmacoes <AFIRMACOES.json>
                                            --armazem <raiz do armazem> --entrega <pasta PARA-O-CASCO-AUTO>
                                            [--hoje AAAA-MM-DD]
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import pote_intelligence_casco as P      # noqa: E402 — gerador e fiscal do dono
import validar_pote_v2 as VP             # noqa: E402
import porta_da_referencia as PORTA      # noqa: E402

REGRA = "REGRA_C8_AUTO"
DECISAO = ("D-C8-AUTO · Luciano (dono), sala SINTONIA DIRETORIA 30/09/2026 09:05: C8 automatico por criterio — "
           "objeto que cumpre integralmente C1-C7 recebe C8 sem aprovacao por objeto; o resto bloqueia")
PASSOU = "PASSOU"
NS = "NAO SEI"
CONFERENCIAS = ("C1_PROVA_DO_ARQUIVO", "C2_DATA_PROPRIA", "C3_LUGAR_PROPRIO", "C4_LIGACAO_ADAMA", "C5_SEM_DUPLICADO",
                "C6_ESPECIE_DO_COMPARTIMENTO", "C7_SO_SAIDA_DA_INTELLIGENCE")
ORIGENS_DE_DATA_PROPRIA = ("LITERAL", "CABECALHO_D147", "RELATIVA_ANCORADA_D149")
#: LAB E5 (30/09): TRECHO_* = CITACAO literal do texto da Sala, cada uma com a sua posicao em SECAO (*_EM).
#: Nenhum outro campo pode usar o prefixo — interpretacao do sistema tem outro nome (DATA_LEGIVEL_INTERPRETADA).
TRECHOS_LITERAIS = {"TRECHO_DA_AFIRMACAO": "AFIRMACAO_EM", "TRECHO_DA_DATA": "DATA_EM", "TRECHO_DO_LUGAR": "LUGAR_EM"}


def _como_se_le(linha: str) -> str:
    """Letras dobradas do negrito do PDF desfeitas pela regra do DONO (leis/tempo_da_afirmacao.como_se_le, ramo
    produtor-afirmacoes-v1). Sem o dono disponivel, fica o literal — nunca uma segunda copia da regra."""
    try:
        import tempo_da_afirmacao as TA  # noqa: PLC0415
    except ImportError:
        return linha
    return TA.como_se_le(linha)


def _sabido(v) -> bool:
    return v not in (None, "", NS, "NAO_SEI", "UNKNOWN", "?")


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def seccao(texto: str, i: int) -> tuple[int, int]:
    """Seccao do contrato v2.2 = entre quebras de pagina \\f."""
    ini = texto.rfind("\f", 0, i)
    fim = texto.find("\f", i)
    return (0 if ini < 0 else ini), (len(texto) if fim < 0 else fim)


def conferir_objeto(o: dict, comp: str, linhas: dict, armazem: Path | None, vistos: set, cache: dict) -> dict:
    """-> {C1..C7: PASSOU | FALHOU: motivo, C8: ...}. Puro sobre (objeto, texto da Sala, armazem)."""
    c = {}
    prova = o.get("PROVA") or []
    fora = o.get("FORA_DO_CONTRATO") or {}
    fonte = fora.get("DA_FONTE") or {}
    span = fonte.get("EVIDENCE_SPAN") if isinstance(fonte.get("EVIDENCE_SPAN"), dict) else None
    base = fonte.get("FACT_TIME_BASIS") if isinstance(fonte.get("FACT_TIME_BASIS"), dict) else None
    interp = fora.get("INTERPRETACAO_DO_SISTEMA") or {}
    p0 = prova[0] if prova else {}
    linha = linhas.get(str(p0.get("ITEM_ID")))
    texto = (linha or {}).get("texto") or ""

    # C1
    f = []
    if len(prova) != 1 or "CLAIM_ID" not in p0:
        f.append("objeto sem UMA afirmacao propria (prova de documento inteiro ou agregado)")
    if linha is None:
        f.append("item da prova fora do corte da Sala")
    else:
        if not _sabido(p0.get("DOCUMENT_ID")) or not linha.get("raw_document_key"):
            f.append("DOCUMENT_ID vazio")
        if p0.get("RAW_SHA256") != linha.get("raw_sha256") or p0.get("RAW_STORAGE_PATH") != linha.get("raw_storage_path"):
            f.append("RAW_SHA256/RAW_STORAGE_PATH da prova != Sala")
        lugar = armazem / str(linha.get("raw_storage_path")) if armazem and linha.get("raw_storage_path") else None
        if lugar is None or not lugar.is_file():
            f.append("RAW ausente no armazem")
        else:
            k = str(lugar)
            if k not in cache:
                cache[k] = _sha_bytes(lugar.read_bytes())
            if cache[k] != linha.get("raw_sha256"):
                f.append("sha do byte relido != raw_asset.sha256")
        if not span or texto[span.get("INICIO", -1):span.get("FIM", -1)] != span.get("TRECHO"):
            f.append("trecho da afirmacao nao esta literal no texto, na posicao declarada")
    c["C1_PROVA_DO_ARQUIVO"] = PASSOU if not f else "FALHOU: " + "; ".join(f)

    # C2
    if not span or not base or not isinstance(base.get("INICIO"), int):
        c["C2_DATA_PROPRIA"] = "FALHOU: data sem trecho proprio com posicao"
    elif texto[base["INICIO"]:base["FIM"]] != base.get("TRECHO"):
        c["C2_DATA_PROPRIA"] = "FALHOU: trecho da data nao esta literal no texto"
    elif interp.get("FACT_TIME_ORIGEM") not in ORIGENS_DE_DATA_PROPRIA:
        c["C2_DATA_PROPRIA"] = "FALHOU: origem da data %s (calculada ou nao propria)" % interp.get("FACT_TIME_ORIGEM")
    elif seccao(texto, span["INICIO"]) != seccao(texto, base["INICIO"]):
        c["C2_DATA_PROPRIA"] = "FALHOU: data fora da seccao da afirmacao"
    else:
        c["C2_DATA_PROPRIA"] = PASSOU

    # C3
    trecho_lugar = fonte.get("FACT_LOCATION_TRECHO")
    onde = fonte.get("FACT_LOCATION_ONDE") if isinstance(fonte.get("FACT_LOCATION_ONDE"), dict) else None
    if not span or not _sabido(trecho_lugar) or not _sabido((o.get("CHAVES") or {}).get("FACT_LOCATION")):
        c["C3_LUGAR_PROPRIO"] = "FALHOU: lugar do fato sem trecho proprio"
    elif not onde or not isinstance(onde.get("INICIO"), int) or not isinstance(onde.get("FIM"), int):
        # LAB E5 (30/09): lugar sem posicao nao se prova no texto («Puglia» 16x). O juiz nao afrouxa.
        c["C3_LUGAR_PROPRIO"] = "FALHOU: lugar sem posicao (ONDE) provada pelo produtor"
    elif texto[onde["INICIO"]:onde["FIM"]] != trecho_lugar or onde.get("TRECHO") != trecho_lugar:
        c["C3_LUGAR_PROPRIO"] = "FALHOU: trecho do lugar nao esta literal no texto, na posicao declarada"
    elif not (span["INICIO"] <= onde["INICIO"] and onde["FIM"] <= span["FIM"]):
        c["C3_LUGAR_PROPRIO"] = "FALHOU: trecho do lugar fora do trecho da afirmacao"
    elif o.get("LOCATION_SOURCE") in (None, "UNRESOLVED") and fora.get("LOCATION_SOURCE") in (None, "UNRESOLVED"):
        c["C3_LUGAR_PROPRIO"] = "FALHOU: LOCATION_SOURCE nao resolvido"
    else:
        c["C3_LUGAR_PROPRIO"] = PASSOU

    # C4
    lig = o.get("LIGACAO_ADAMA")
    fl = PORTA.conferir_ligacao(lig) if isinstance(lig, dict) else ["sem LIGACAO_ADAMA"]
    c["C4_LIGACAO_ADAMA"] = PASSOU if not fl else "FALHOU: " + "; ".join(map(str, fl))[:300]

    # C5
    k = (str(p0.get("ITEM_ID")), str((span or {}).get("TRECHO")))
    c["C5_SEM_DUPLICADO"] = PASSOU if k not in vistos else "FALHOU: afirmacao repetida"

    # C6
    c["C6_ESPECIE_DO_COMPARTIMENTO"] = (PASSOU if o.get("ESPECIE") in P.COMPARTIMENTOS.get(comp, {}).get("ESPECIES", ())
                                        else "FALHOU: especie fora do compartimento")
    # C7
    c["C7_SO_SAIDA_DA_INTELLIGENCE"] = (PASSOU if o.get("ESPECIE_DITA_POR") == "INTELLIGENCE" and prova
                                        and all(_sabido(p.get("ITEM_ID")) for p in prova)
                                        and all(p.get("G0") == PASSOU for p in prova)
                                        else "FALHOU: nao e objeto da Intelligence com G0 PASSOU")

    ok = all(c[x] == PASSOU for x in CONFERENCIAS)
    c["C8_DECISAO_DO_DONO"] = (PASSOU + " · " + REGRA + " · " + DECISAO) if ok else \
        "FALHOU: %s so libera com C1-C7 PASSOU (falhou: %s)" % (REGRA, ", ".join(x for x in CONFERENCIAS if c[x] != PASSOU))
    if ok:
        vistos.add(k)
    return c


# ---------------------------------------------------------------------------------------------------------------
# ROTEAR PRIMEIRO, JULGAR DEPOIS (dono, Diretoria 01/10: «nao aplicar regua de fato de campo a tudo»).
# A auditoria cega do LAB (ROTULOS-CEGOS-V1 e518cfce, 313 materiais) mediu 107 uteis perdidos porque C1..C3 (afirmacao
# propria, data do FATO, lugar do FATO) eram exigidos a estudos publicados — que por natureza nao tem «onde aconteceu
# hoje». C1..C7 NAO afrouxam: continuam a regua de FATO/sinal/alerta. O que muda e a PORTA: o objeto que o motor ja
# declarou CONHECIMENTO/ESTUDO (§5-E do contrato de afirmacoes, F2 2882e899a: science, NO_DEFENSIBLE_ACTION_YET,
# USO_EXIGE_TEMPO=false) e julgado pela regua da SUA natureza. Nenhuma camada nova: mesma funcao, mesmo C8, mesmo pote.
# Conhecimento liberado nunca e alerta: leva RESULTADO=NO_DEFENSIBLE_ACTION_YET e nao abre janela/ACT_NOW (fiscal).
# ---------------------------------------------------------------------------------------------------------------
REGUA_FATO = "REGUA_FATO/C1-C7 (contrato v2.2)"
REGUA_CONHECIMENTO = "REGUA_CONHECIMENTO/v1 (estudo publicado; sem data/lugar do FATO por natureza)"
CONFERENCIAS_CONHECIMENTO = ("K1_PROVA_DO_DOCUMENTO", "K2_OBRA_CIENTIFICA_DECLARADA_PELA_FONTE",
                             "K3_SEM_USO_QUE_EXIGE_TEMPO", "C4_LIGACAO_ADAMA", "K5_SEM_OBRA_DUPLICADA",
                             "C6_ESPECIE_DO_COMPARTIMENTO", "K7_SO_SAIDA_DA_INTELLIGENCE")
#: tipo de obra DECLARADO pelo registo da fonte (campo `type` do registo bibliografico relido no armazem), nunca
#: inferido do texto. Fora da lista (editorial, erratum, letter, paratext, ...) nao e estudo -> fica bloqueado.
TIPOS_DE_OBRA_CIENTIFICA = ("article", "review", "preprint", "conference-paper", "conference-abstract", "dataset",
                            "data-paper", "dissertation", "book-chapter", "report")
#: P1/1B CAP-SCI (dono 01/10 «rotear primeiro»): obra que a fonte DECLARA nao-primaria. Nao e estudo -> nunca vai ao
#: cliente como evidencia; mas e obra cientifica com identidade -> PRESERVA-SE em science (Biblia CAP-SCI: forca
#: NAO_APLICAVEL, «nao e evidencia primaria»). So entra aqui tipo que apareceu nos 313 (editorial, 5 casos).
TIPOS_DE_OBRA_SECUNDARIA = ("editorial",)
#: P1/1B: CAP-SCI so sustenta leitura para decisao quando o TEMA esta provado (cultura E problema, motor
#: capacidade_cientifica.julgar_estudo). TEMA_NAO_PROVADO = conhecimento guardado, nao material de cliente.
APLICABILIDADE_PARA_CLIENTE = ("PARCIAL", "COMPLETA")
DESTINO_CLIENTE, DESTINO_PRESERVADO, DESTINO_BLOQUEADO = "LIBERADO_PARA_CLIENTE", "PRESERVADO_EM_SCIENCE", "BLOQUEADO"
_DOI = re.compile(r"^10\.\d{4,9}/\S+$")
_OBRA_OPENALEX = re.compile(r"^https?://openalex\.org/W\d+$")


def natureza_do_objeto(o: dict, comp: str) -> str:
    """-> CONHECIMENTO | FATO. So o que o MOTOR ja declarou conhecimento sem tempo vai a regua de conhecimento;
    tudo o resto (incluindo o que nao se sabe) fica na regua de FATO — a mais exigente."""
    fora = o.get("FORA_DO_CONTRATO") or {}
    uso = ((fora.get("INTERPRETACAO_DO_SISTEMA") or {}).get("USO") or {})
    if (comp == "science" and str(fora.get("ESPECIE_DO_MOTOR", "")).startswith("CONHECIMENTO/ESTUDO")
            and o.get("USO_EXIGE_TEMPO") is False and o.get("RESULTADO") == "NO_DEFENSIBLE_ACTION_YET"
            and uso.get("G0_FALTA") == ["FACT_TIME"]):
        return "CONHECIMENTO"
    return "FATO"


def _registo_da_obra(lugar: Path) -> dict | None:
    try:
        d = json.loads(lugar.read_bytes().decode("utf-8"))
    except (ValueError, UnicodeDecodeError, OSError):
        return None
    return d if isinstance(d, dict) else None


def conferir_conhecimento(o: dict, comp: str, linhas: dict, armazem: Path | None, vistos: set, cache: dict) -> dict:
    """Regua de CONHECIMENTO: prova do DOCUMENTO (nao de uma afirmacao de campo), identidade de obra declarada pela
    fonte, e nenhum uso que exija tempo. Puro sobre (objeto, texto da Sala, armazem)."""
    c = {"REGUA": REGUA_CONHECIMENTO}
    prova = o.get("PROVA") or []
    p0 = prova[0] if prova else {}
    linha = linhas.get(str(p0.get("ITEM_ID")))
    texto = (linha or {}).get("texto") or ""
    registo, titulo_em = None, -1

    # K1 — o documento existe, e o mesmo byte da Sala, e o titulo da obra esta literal no texto
    f = []
    if len(prova) != 1:
        f.append("objeto com %d provas (conhecimento e UMA obra)" % len(prova))
    if linha is None:
        f.append("item da prova fora do corte da Sala")
    else:
        doc = p0.get("DOCUMENT_ID")
        if not _sabido(doc) or doc != linha.get("raw_document_key"):
            f.append("DOCUMENT_ID vazio ou diferente do raw_document_key da Sala")
        if p0.get("RAW_SHA256") != linha.get("raw_sha256") or p0.get("RAW_STORAGE_PATH") != linha.get("raw_storage_path"):
            f.append("RAW_SHA256/RAW_STORAGE_PATH da prova != Sala")
        lugar = armazem / str(linha.get("raw_storage_path")) if armazem and linha.get("raw_storage_path") else None
        if lugar is None or not lugar.is_file():
            f.append("RAW ausente no armazem")
        else:
            k = str(lugar)
            if k not in cache:
                cache[k] = _sha_bytes(lugar.read_bytes())
            if cache[k] != linha.get("raw_sha256"):
                f.append("sha do byte relido != raw_asset.sha256")
            else:
                registo = _registo_da_obra(lugar)
        titulo = (registo or {}).get("title") or (registo or {}).get("display_name")
        if not isinstance(titulo, str) or not titulo.strip():
            f.append("registo da obra sem titulo legivel no RAW")
        else:
            titulo_em = texto.find(titulo)
            if titulo_em < 0:
                f.append("titulo da obra nao esta literal no texto da Sala")
    c["K1_PROVA_DO_DOCUMENTO"] = PASSOU if not f else "FALHOU: " + "; ".join(f)

    # K2 — e uma OBRA CIENTIFICA porque a fonte o declara (identidade de obra + tipo no registo), nao porque o texto
    #      «parece» ciencia. Pagina institucional, noticia, editorial, obituario-sem-tipo: nao passam.
    doc = str(p0.get("DOCUMENT_ID"))
    tipo = (registo or {}).get("type")
    secundaria = False
    if not (_DOI.match(doc) or _OBRA_OPENALEX.match(doc)):
        c["K2_OBRA_CIENTIFICA_DECLARADA_PELA_FONTE"] = "FALHOU: DOCUMENT_ID nao e identidade de obra (DOI/OpenAlex)"
    elif tipo in TIPOS_DE_OBRA_SECUNDARIA:
        secundaria = True
        c["K2_OBRA_CIENTIFICA_DECLARADA_PELA_FONTE"] = (
            "FALHOU: tipo da obra no registo da fonte = %r (obra secundaria: nao e evidencia primaria)" % (tipo,))
    elif tipo not in TIPOS_DE_OBRA_CIENTIFICA:
        c["K2_OBRA_CIENTIFICA_DECLARADA_PELA_FONTE"] = "FALHOU: tipo da obra no registo da fonte = %r" % (tipo,)
    else:
        c["K2_OBRA_CIENTIFICA_DECLARADA_PELA_FONTE"] = PASSOU

    # K3 — nada aqui pode virar alerta: sem FACT_TIME inventado, uso sem tempo, resultado honesto
    ft = [p.get("FACT_TIME") for p in prova]
    if o.get("USO_EXIGE_TEMPO") is not False or o.get("RESULTADO") != "NO_DEFENSIBLE_ACTION_YET":
        c["K3_SEM_USO_QUE_EXIGE_TEMPO"] = "FALHOU: objeto exige tempo ou promete acao"
    elif any(_sabido(x) for x in ft):
        c["K3_SEM_USO_QUE_EXIGE_TEMPO"] = "FALHOU: conhecimento com FACT_TIME preenchido (vai a regua de FATO)"
    elif any(p.get("ADMITIDA_POR") != "USO_SEM_TEMPO" for p in prova):
        c["K3_SEM_USO_QUE_EXIGE_TEMPO"] = "FALHOU: prova nao admitida por USO_SEM_TEMPO"
    else:
        c["K3_SEM_USO_QUE_EXIGE_TEMPO"] = PASSOU

    lig = o.get("LIGACAO_ADAMA")
    fl = PORTA.conferir_ligacao(lig) if isinstance(lig, dict) else ["sem LIGACAO_ADAMA"]
    c["C4_LIGACAO_ADAMA"] = PASSOU if not fl else "FALHOU: " + "; ".join(map(str, fl))[:300]

    k = ("OBRA", doc)
    c["K5_SEM_OBRA_DUPLICADA"] = PASSOU if k not in vistos else "FALHOU: a mesma obra ja foi liberada (INT-LAW-072)"
    c["C6_ESPECIE_DO_COMPARTIMENTO"] = (PASSOU if o.get("ESPECIE") in P.COMPARTIMENTOS.get(comp, {}).get("ESPECIES", ())
                                        else "FALHOU: especie fora do compartimento")
    c["K7_SO_SAIDA_DA_INTELLIGENCE"] = (PASSOU if o.get("ESPECIE_DITA_POR") == "INTELLIGENCE" and prova
                                        and all(_sabido(p.get("ITEM_ID")) for p in prova)
                                        else "FALHOU: nao e objeto da Intelligence com item da Sala")
    # K8 — CAP-SCI (Biblia §34, motor capacidade_cientifica.julgar_estudo): sem CULTURA e PROBLEMA provados o estudo
    #      nao tem leitura («SEM_LEITURA_TEMA_NAO_PROVADO»). Guarda-se em science; nao e material de cliente.
    aplic = (((o.get("FORA_DO_CONTRATO") or {}).get("INTERPRETACAO_DO_SISTEMA") or {}).get("APLICABILIDADE")
             or {}).get("ESTADO", NS)
    c["K8_TEMA_PROVADO_CAP_SCI"] = (PASSOU if aplic in APLICABILIDADE_PARA_CLIENTE else
                                    "FALHOU: APLICABILIDADE=%s (CAP-SCI: sem cultura e problema provados nao ha "
                                    "leitura para decisao)" % (aplic,))
    ok = all(c[x] == PASSOU for x in CONFERENCIAS_CONHECIMENTO) and c["K8_TEMA_PROVADO_CAP_SCI"] == PASSOU
    # PRESERVAR: a obra e provada (byte, identidade DOI/OpenAlex, titulo literal, sem tempo, unica, da Intelligence)
    # mas a CAP-SCI nao a deixa ir ao cliente (obra secundaria declarada pela fonte ou tema nao provado). Nao e
    # bloqueio nem liberacao: e conhecimento guardado em science, NAO_PARA_CLIENTE, NO_DEFENSIBLE_ACTION_YET.
    prova_da_obra = (all(c[x] == PASSOU for x in ("K1_PROVA_DO_DOCUMENTO", "K3_SEM_USO_QUE_EXIGE_TEMPO",
                                                   "K5_SEM_OBRA_DUPLICADA", "C6_ESPECIE_DO_COMPARTIMENTO",
                                                   "K7_SO_SAIDA_DA_INTELLIGENCE"))
                     and (c["K2_OBRA_CIENTIFICA_DECLARADA_PELA_FONTE"] == PASSOU or secundaria))
    c["DESTINO"] = DESTINO_CLIENTE if ok else (DESTINO_PRESERVADO if prova_da_obra else DESTINO_BLOQUEADO)
    falhas = [x for x in CONFERENCIAS_CONHECIMENTO + ("K8_TEMA_PROVADO_CAP_SCI",) if c[x] != PASSOU]
    c["C8_DECISAO_DO_DONO"] = (PASSOU + " · " + REGRA + " · " + REGUA_CONHECIMENTO + " · " + DECISAO) if ok else \
        "FALHOU: %s (%s) so libera com todas PASSOU (falhou: %s)%s" % (
            REGRA, REGUA_CONHECIMENTO, ", ".join(falhas),
            " -> PRESERVADO_EM_SCIENCE (obra provada, nao vai ao cliente)" if prova_da_obra else "")
    if ok or prova_da_obra:
        vistos.add(k)
        c["_TITULO_EM"] = titulo_em
        c["_TITULO"] = (registo or {}).get("title") or (registo or {}).get("display_name")
    return c


def conferir_por_natureza(o: dict, comp: str, linhas: dict, armazem: Path | None, vistos: set, cache: dict) -> dict:
    if natureza_do_objeto(o, comp) == "CONHECIMENTO":
        return conferir_conhecimento(o, comp, linhas, armazem, vistos, cache)
    return dict(conferir_objeto(o, comp, linhas, armazem, vistos, cache), REGUA=REGUA_FATO)


def liberar(pote: dict, linhas: dict, armazem: Path | None, run_id: str) -> tuple[dict, dict]:
    """Carimba LIBERACAO por objeto no pote (copia). -> (pote carimbado, {OBJETO_ID: conferencia})."""
    pote = json.loads(json.dumps(pote, ensure_ascii=False))
    vistos, cache, conf = set(), {}, {}
    for comp, e in pote["COMPARTIMENTOS"].items():
        for o in e["OBJETOS"]:
            c = conferir_por_natureza(o, comp, linhas, armazem, vistos, cache)
            ok = c["C8_DECISAO_DO_DONO"].startswith(PASSOU)
            c.setdefault("DESTINO", DESTINO_CLIENTE if ok else DESTINO_BLOQUEADO)
            preservado = c["DESTINO"] == DESTINO_PRESERVADO
            titulo, titulo_em = c.pop("_TITULO", None), c.pop("_TITULO_EM", None)
            o["LIBERACAO"] = "LIBERADO_PARA_CLIENTE" if ok else "NAO_PARA_CLIENTE"
            o["CONFERENCIA_DE_LIBERACAO"] = c
            o["LIBERADO_POR"] = REGRA if ok else NS
            o["LIBERADO_NA_CORRIDA"] = run_id
            if preservado:
                # CAP-SCI: valor guardado em science, nunca cliente; a prova cita a obra (titulo literal)
                o["DESTINO_DO_OBJETO"] = DESTINO_PRESERVADO
                o["NATUREZA_DO_OBJETO"] = "CONHECIMENTO"
                for p in o["PROVA"]:
                    p.update({"TRECHO_DA_AFIRMACAO": titulo, "SECAO": {"AFIRMACAO_EM": titulo_em}})
            elif ok and c["REGUA"] == REGUA_CONHECIMENTO:
                # conhecimento: a prova cita a OBRA (titulo literal, com posicao) — nunca data/lugar de fato
                for p in o["PROVA"]:
                    p.update({"TRECHO_DA_AFIRMACAO": titulo, "SECAO": {"AFIRMACAO_EM": titulo_em}})
                o["NATUREZA_DO_OBJETO"] = "CONHECIMENTO"
            elif ok:
                fonte = o["FORA_DO_CONTRATO"]["DA_FONTE"]
                for p in o["PROVA"]:
                    p.update({"TRECHO_DA_AFIRMACAO": fonte["EVIDENCE_SPAN"]["TRECHO"],
                              "TRECHO_DA_DATA": fonte["FACT_TIME_BASIS"]["TRECHO"],
                              "TRECHO_DO_LUGAR": fonte["FACT_LOCATION_TRECHO"],
                              "SECAO": {"AFIRMACAO_EM": fonte["EVIDENCE_SPAN"]["INICIO"],
                                        "DATA_EM": fonte["FACT_TIME_BASIS"]["INICIO"],
                                        "LUGAR_EM": fonte["FACT_LOCATION_ONDE"]["INICIO"]}})
                    legivel = _como_se_le(p["TRECHO_DA_DATA"])
                    if legivel != p["TRECHO_DA_DATA"]:
                        # LAB E5 (30/09): isto NAO e citacao — e o cabecalho desdobrado pela regra do dono. Todo campo
                        # TRECHO_* e literal no texto da Sala na sua posicao; a leitura do sistema tem outro nome (D112 r4).
                        p["DATA_LEGIVEL_INTERPRETADA"] = legivel
                    naoliteral = [k for k in p if k.startswith("TRECHO_") and k not in TRECHOS_LITERAIS]
                    if naoliteral:
                        raise ValueError("campo TRECHO_ que nao e citacao literal: %s" % naoliteral)
            conf[o["OBJETO_ID"]] = dict(c, COMPARTIMENTO=comp, ESPECIE=o.get("ESPECIE"), LIBERACAO=o["LIBERACAO"])
    return pote, conf


def so_liberados(pote: dict) -> dict:
    """O pote PARA_CLIENTE: so objetos LIBERADO_PARA_CLIENTE (contrato v2.2 §3: dois potes por corrida)."""
    p = json.loads(json.dumps(pote, ensure_ascii=False))
    for e in p["COMPARTIMENTOS"].values():
        antes = len(e["OBJETOS"])
        e["OBJETOS"] = [o for o in e["OBJETOS"] if o.get("LIBERACAO") == "LIBERADO_PARA_CLIENTE"]
        if antes and not e["OBJETOS"]:
            e["ESTADO"] = "VAZIO"
            e["PORQUE_VAZIO"] = "NENHUM_OBJETO_LIBERADO"
            e["PORQUE_TEXTO"] = ("%d objeto(s) desta corrida neste compartimento ficaram BLOQUEADOS pela %s "
                                 "(C1-C7 nao passaram); estao no POTE-EXPERIMENTAL.json e em BLOQUEADOS.json" % (antes, REGRA))
    n = sum(len(e["OBJETOS"]) for e in p["COMPARTIMENTOS"].values())
    p["OBJETOS_LIBERADOS"] = n
    p["POTE_DA_CORRIDA"] = "PARA_CLIENTE"
    p["LIBERACAO_POR_CRITERIO"] = {"REGRA": REGRA, "DECISAO": DECISAO, "CONTRATO": "v2.2 C1-C7 + C8 por regra"}
    return p


def _sha(p: Path) -> str:
    return _sha_bytes(p.read_bytes())


def entregar(pote_cliente: dict, pote_todo: dict, conf: dict, entrega: Path, extra: dict) -> dict:
    """POTE.json (so liberados) + BLOQUEADOS.json + MANIFESTO.json + SHA256SUMS.txt (ULTIMO). Troca-se inteira."""
    nova = entrega.with_name(entrega.name + ".nova")
    shutil.rmtree(nova, ignore_errors=True)
    nova.mkdir(parents=True)
    w = lambda n, d: (nova / n).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",  # noqa: E731
                                           encoding="utf-8", newline="\n")
    w("POTE.json", pote_cliente)
    w("POTE-EXPERIMENTAL.json", pote_todo)
    bloq = {oid: c for oid, c in conf.items() if c["LIBERACAO"] != "LIBERADO_PARA_CLIENTE"
            and c.get("DESTINO") != DESTINO_PRESERVADO}
    pres = [oid for oid, c in conf.items() if c.get("DESTINO") == DESTINO_PRESERVADO]
    w("BLOQUEADOS.json", {"REGRA": REGRA, "N": len(bloq), "OBJETOS": bloq})
    man = dict(extra, INTELLIGENCE_RUN_ID=pote_cliente.get("INTELLIGENCE_RUN_ID"),
               RESULT_STATE=pote_cliente.get("RESULT_STATE"), CORRIDA_SINTETICA=pote_cliente.get("CORRIDA_SINTETICA"),
               SOURCE_HEAD=pote_cliente.get("SOURCE_HEAD"), GERADO_EM=datetime.now(timezone.utc).isoformat(),
               GERADO_POR="pacote/liberacao_por_criterio.py (" + REGRA + ")",
               POTE={"ARQUIVO": "POTE.json", "SHA256_ARQUIVO": _sha(nova / "POTE.json"),
                     # o sha do JSON canonico (chaves ordenadas, compacto, UTF-8): o POTE_SHA256 que o envelope leva
                     # no ar e que a prova reversa compara (portoes/PUBLICACAO-AUTOMATICA.json -> NO_MANIFESTO)
                     "SHA256_CANONICO": _sha_bytes(json.dumps(pote_cliente, sort_keys=True, ensure_ascii=False,
                                                              separators=(",", ":")).encode("utf-8")),
                     "CONTRATO": pote_cliente.get("SCHEMA"), "OBJETOS_LIBERADOS": pote_cliente["OBJETOS_LIBERADOS"]},
               POTE_EXPERIMENTAL={"ARQUIVO": "POTE-EXPERIMENTAL.json", "SHA256_ARQUIVO": _sha(nova / "POTE-EXPERIMENTAL.json")},
               BLOQUEADOS=len(bloq), VALIDAR_POTE_V2="PASSA",
               # CAP-SCI (P1/1B): obras provadas guardadas em science, NAO_PARA_CLIENTE, fora de BLOQUEADOS
               PRESERVADOS_EM_SCIENCE=pres,
               # K2 · EIXO 2 no manifesto: onde este pote pode aparecer (nunca producao por esta via, D141)
               AMBIENTE=pote_cliente.get("AMBIENTE", NS), PRODUCAO=pote_cliente.get("PRODUCAO", NS),
               EIXOS=pote_cliente.get("EIXOS", NS),
               LIBERADOS=[oid for oid, c in conf.items() if c["LIBERACAO"] == "LIBERADO_PARA_CLIENTE"])
    w("MANIFESTO.json", man)
    (nova / "SHA256SUMS.txt").write_text("".join("%s *%s\n" % (_sha(nova / n), n) for n in
                                                 ("POTE.json", "POTE-EXPERIMENTAL.json", "BLOQUEADOS.json",
                                                  "MANIFESTO.json")), encoding="utf-8", newline="\n")
    velha = entrega.with_name(entrega.name + ".velha")
    shutil.rmtree(velha, ignore_errors=True)
    if entrega.exists():
        os.replace(entrega, velha)
    os.replace(nova, entrega)
    shutil.rmtree(velha, ignore_errors=True)
    return man


def main(argv=None) -> int:
    import argparse
    a = argparse.ArgumentParser()
    a.add_argument("--copia", required=True)
    a.add_argument("--afirmacoes", required=True)
    a.add_argument("--armazem", required=True)
    a.add_argument("--entrega", required=True)
    a.add_argument("--hoje", default=date.today().isoformat())
    a.add_argument("--produtor", help="raiz do ramo produtor-afirmacoes (dono de leis/tempo_da_afirmacao.como_se_le)")
    x = a.parse_args(argv)
    if x.produtor:
        sys.path.append(str(Path(x.produtor) / "leis"))
    sys.path.insert(0, str(RAIZ / "admissao"))
    import motor_das_capacidades as M                   # noqa: PLC0415
    import gatilho_da_inteligencia as GI                # noqa: PLC0415
    copia = Path(x.copia)
    sala = copia / "SALA_ATUAL.json"
    ro = (copia / "PROVA_RO.txt").read_text(encoding="utf-8").split()
    if ro[0] != "on":
        raise SystemExit("copia sem prova de transacao so-leitura")
    linhas = json.loads(sala.read_text(encoding="utf-8"))
    export = {"EXPORT": M.EXPORT_DA_SALA, "SINTETICO": False, "CORTE": ro[1] + "T" + ro[2],
              "ORIGEM": "copia so-leitura · sha256 %s" % _sha(sala), "READ_ONLY": ro[0], "LINHAS": linhas,
              "POUSOS_DA_COPIA": [{"run_id": l["run_id"], "ordem": l["ordem"], "item_id": l["item_id"],
                                   "pousado_em": l.get("pousado_em")} for l in linhas]}
    limpo, corte = GI.cortar_vigente(export)
    art = json.loads(Path(x.afirmacoes).read_text(encoding="utf-8"))
    s = M.rodar(M.entrada_do_export(limpo), date.fromisoformat(x.hoje), GI._cabeca(), afirmacoes=art)
    del art
    pote, _ = GI.montar_o_pote(s)
    run = pote.get("INTELLIGENCE_RUN_ID", NS)
    por_item = {str(l["item_id"]): l for l in limpo["LINHAS"]}
    todo, conf = liberar(pote, por_item, Path(x.armazem), run)
    # K2 (01/10): os DOIS eixos — o objeto diz uma coisa sobre o cliente (LIBERACAO), a raiz diz o ambiente
    todo = P.aplicar_eixos(todo)
    cliente = so_liberados(todo)
    for nome, p in (("EXPERIMENTAL", todo), ("PARA_CLIENTE", cliente)):
        v = P.conferir_pote(p) + VP.validar(p)
        if v:
            raise SystemExit("pote %s reprovado pelo fiscal: %s" % (nome, v[:5]))
    if cliente["OBJETOS_LIBERADOS"] == 0:
        print(json.dumps({"LIBERADOS": 0, "BLOQUEADOS": len(conf), "ENTREGA": "NAO GERADA (nada liberado)"}))
        return 0
    man = entregar(cliente, todo, conf, Path(x.entrega), {
        "COPIA_DA_SALA": {"SHA256": _sha(sala), "EM": ro[1] + "T" + ro[2], "READ_ONLY": ro[0]},
        "AFIRMACOES": {"FICHEIRO": Path(x.afirmacoes).name, "SHA256": _sha(Path(x.afirmacoes))},
        "CORTE_VIGENTE": {k: corte.get(k, NS) for k in ("LINHAS_NO_EXPORT", "LINHAS_NO_CORTE")}})
    print(json.dumps({k: man[k] for k in ("INTELLIGENCE_RUN_ID", "POTE", "BLOQUEADOS", "LIBERADOS")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
