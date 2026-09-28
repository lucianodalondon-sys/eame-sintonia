#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PRECO DO ITEM — a linha de preco da Sala entra na corrida pelo MESMO item, e so por ele.

    MISSAO   PRECO-NO-MOTOR (decisao do dono, Diretoria 28/09: «o preco ainda NAO e consumido pelo motor
             da Intelligence»; PRICE/UNIT chegavam ao objeto por um script fora do Git)
    ESPECIE  MOTOR (Z-MOTOR). Chamado por `corrida_da_inteligencia.correr(..., precos=...)`.
             NAO abre a Sala. NAO abre rede. NAO chama coletor. NAO cunha identidade.
    VERSAO   PRECO_RULESET_VERSION (entra na identidade da corrida)

    python -m pytest tests/test_preco_no_motor.py -v

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    ESTA LINHA DE PRECO (vista `sala_de_espera_precos`, migration 038) E DO ITEM QUE A CORRIDA LEU,
    E O TEXTO DESSE ITEM SUSTENTA O VALOR, A UNIDADE, A CULTURA E O PERIODO QUE ELA DIZ?

Quem escreve a linha e a Collection (`admissao/preco_na_sala.py`). Aqui ela e LIDA — e so nasce objeto
quando os gates abaixo passam todos. Um preco que nao passa fica em PRECOS_RECUSADOS com o motivo: nunca
some, e nunca vira objeto por aproximacao.

OS GATES (ordem fixa; o primeiro que falha e o motivo)
------------------------------------------------------
    P0 LINHA_INCOMPLETA          falta campo da linha, ou o valor e «NAO SEI» (ausencia nao gera preco)
    P1 PRECO_SEM_ITEM_NA_CORRIDA a ligacao e (run_id, ordem) = (CORRIDA, ORDEM) de UM item desta corrida.
                                 Sem item -> recusa; mais de um -> PRECO_ITEM_AMBIGUO. Nunca por
                                 ITEM_ID, URL, texto parecido ou vizinhanca.
    P2 PRECO_DE_OUTRO_ITEM       item_id / source_id que a linha declara != os do item ligado
    P3 RAW_SHA256                a linha e o item tem de apontar os MESMOS bytes:
                                 RAW_SHA256_DO_ITEM_NAO_SEI · SHA_INVALIDO ·
                                 RAW_DE_OUTRO_ITEM (o sha e o de outro item da corrida) ·
                                 SHA_INCOMPATIVEL (o sha nao e o do item)
       RAW_BYTES_NAO_BATEM       (so com `armazem`) os bytes guardados nao dao o sha do item
    P4 ITEM_SEM_PROVENIENCIA     o item nao chega ao RAW (RAW_OBSERVATION_ID NAO SEI)
    P5 CITACAO_FORA_DO_TEXTO     a citacao da linha nao esta, literal, no texto do item
    P6 CITACAO_SO_FORA_DO_ARTIGO a citacao so aparece em menu, barra lateral, «potrebbe interessarti»,
                                 manchete vizinha ou rodape — conteudo de OUTRO artigo nao e preco deste
    P7 VALOR/UNIDADE/CULTURA_FORA_DA_CITACAO   o que a linha diz tem de estar DENTRO da citacao
    P8 PERIODO_INVALIDO / PERIODO_FUTURO       periodo ISO, fim >= inicio, nao comeca depois da captura
    P9 CLASSE_DESCONHECIDA       CURRENT | OUTLOOK | HISTORICAL
   P10 DUPLICADO                 a mesma chave natural (a unique da 038) ja deu objeto nesta corrida

O QUE O OBJETO DIZ, E O QUE FICA NAO SEI (INT-LAW-062, CAP-MKT da Biblia)
------------------------------------------------------------------------
    PRICE / UNIT        os literais da linha, conferidos dentro da citacao
    PERIOD              o periodo da linha (base: a linha da Sala; e se bate com o FACT_TIME do item)
    FACT_LOCATION       a praca da linha, so se estiver escrita no corpo do artigo; senao NAO SEI
    CULTURA_LITERAL     como a fonte escreve; CROP_ID = NAO SEI (nenhuma identidade canonica e cunhada)
    MARKET_PLACE_ID     NAO SEI (nenhuma identidade de praca e cunhada)
    MARKET_STAGE        NAO SEI — a Sala nao tem campo de estagio de mercado: NIVEL e escala geografica
                        (PIAZZA/NACIONAL/REGIAO), nao atacado/retalho. Nunca se infere do texto aqui.
    ESPECIE             SINAL · CAP-MKT como CONTEXTO: um ponto nao e MARKET_FINDING (os cinco gates
                        CHANGE + MATERIALITY + CONTEXT + DECISION_AFFECTED + ATTRIBUTION_LIMIT nao correm)

O CORPO DO ARTIGO TEM UM DONO, E NAO E ESTE FICHEIRO
---------------------------------------------------
P6 usa `leis/fato_do_texto.vizinhos` e `RODAPE` (dono: extrator lugar/tempo da Collection). Um so ajuste,
declarado e testado: o rotulo do bloco vizinho escrito com a palavra final «anche» («Potrebbe interessarti
anche») nao casa no rotulo do dono (medido no derived:911); aqui a palavra e trocada por espacos do MESMO
comprimento ANTES de chamar o dono, para as posicoes continuarem certas. Defeito registado para o dono;
quando ele o corrigir, o ajuste deixa de mudar alguma coisa.
"""
from __future__ import annotations

import hashlib
import re
from datetime import date
from pathlib import Path

import fato_do_texto as FT                        # leis/ — o dono do corpo do artigo

NAO_SEI = "NAO SEI"
PRECO_RULESET_VERSION = "PRECO/v1"
LEI = "D-PRECO-NO-MOTOR (Diretoria 28/09) · CAP-MKT · INT-LAW-062/067/101"

CAMPOS_DA_LINHA = ("run_id", "ordem", "indicador", "cultura_literal", "valor_texto", "unidade",
                   "periodo_inicio", "periodo_fim", "classe", "citacao_literal", "o_que_nao_prova",
                   "raw_sha256")
CLASSES = ("CURRENT", "OUTLOOK", "HISTORICAL")
RE_SHA256 = re.compile(r"^[0-9a-f]{64}$")
#: A chave natural da tabela 038 (`preco_do_item_uma_vez`). Mesmo preco -> mesmo objeto.
CHAVE_NATURAL = ("run_id", "ordem", "indicador", "cultura_literal", "praca", "periodo_inicio",
                 "periodo_fim")

_PALAVRAS_DE_IGNORANCIA = ("NAO SEI", "NAO_SEI", "UNKNOWN", "NOT_KNOWN")


def _ign(v) -> bool:
    if v is None:
        return True
    s = str(v).strip()
    return not s or s.upper().startswith(_PALAVRAS_DE_IGNORANCIA) or s.upper() in ("NONE", "NULL")


def _txt(d: dict, k) -> str:
    v = d.get(k)
    return "" if v is None else str(v).strip()


# ── P6 · o corpo do artigo (pelo dono), com o ajuste declarado ───────────────
_RE_ROTULO_COM_ANCHE = re.compile(
    r"^(\s*(?:%s))(\s+anche)(\s*:?\s*)$" % "|".join(FT._ROTULOS_VIZINHOS), re.I)


def _rotulos_normalizados(texto: str) -> str:
    """«Potrebbe interessarti anche» -> «Potrebbe interessarti      » (mesmo comprimento)."""
    out = []
    for linha in str(texto or "").splitlines(keepends=True):
        corpo = linha.rstrip("\r\n")
        fim = linha[len(corpo):]
        m = _RE_ROTULO_COM_ANCHE.match(corpo)
        if m:
            corpo = m.group(1) + " " * len(m.group(2)) + m.group(3)
        out.append(corpo + fim)
    return "".join(out)


def fora_do_artigo(texto: str) -> list:
    """[(inicio, fim, motivo)] do que NAO e o artigo: vizinhos (dono) + linhas de rodape (dono)."""
    t = _rotulos_normalizados(texto)
    fora = list(FT.vizinhos(t))
    pos = 0
    # a linha de rodape e a MESMA regra do dono (`corpo()` descarta-a inteira)
    for linha in str(texto or "").splitlines(keepends=True):
        corpo = linha.rstrip("\r\n")
        if corpo.strip() and FT.RODAPE.search(corpo):
            fora.append((pos, pos + len(corpo), "linha de rodape"))
        pos += len(linha)
    return fora


def ocorrencias_no_artigo(texto: str, trecho: str) -> list:
    """Posicoes de `trecho` no texto que NAO caem em menu/barra lateral/vizinho/rodape."""
    fora = fora_do_artigo(texto)
    out, i = [], str(texto or "").find(trecho)
    while trecho and i >= 0:
        if not any(a <= i < b for a, b, _ in fora):
            out.append(i)
        i = texto.find(trecho, i + 1)
    return out


# ── os gates ─────────────────────────────────────────────────────────────────
def _dia(s):
    try:
        return date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def chave_natural(linha: dict) -> tuple:
    return tuple(_txt(linha, k) for k in CHAVE_NATURAL)


def objeto_id(linha: dict) -> str:
    return "PR-" + hashlib.sha256("|".join(chave_natural(linha)).encode("utf-8")).hexdigest()[:16]


def _sha_dos_bytes(armazem, caminho):
    p = Path(armazem) / str(caminho)
    if not p.is_file():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def conferir(linha: dict, itens: list, armazem=None) -> tuple:
    """`(item, None, detalhe)` se a linha e do item e o texto a sustenta; `(item|None, motivo, detalhe)`."""
    if not isinstance(linha, dict):
        return None, "LINHA_INCOMPLETA", "a linha nao e um objeto"
    falta = [k for k in CAMPOS_DA_LINHA if _ign(linha.get(k))]
    if falta:
        return None, "LINHA_INCOMPLETA", "falta " + ", ".join(falta)
    # P1 · a ligacao: (run_id, ordem) e so isso
    ligados = [i for i in itens if isinstance(i, dict) and _txt(i, "CORRIDA") == _txt(linha, "run_id")
               and _txt(i, "ORDEM") == _txt(linha, "ordem") and not _ign(i.get("ORDEM"))]
    if not ligados:
        return None, "PRECO_SEM_ITEM_NA_CORRIDA", "(%s, %s) nao e (CORRIDA, ORDEM) de nenhum item desta corrida" % (
            linha["run_id"], linha["ordem"])
    if len(ligados) > 1:
        return None, "PRECO_ITEM_AMBIGUO", "(%s, %s) liga %d itens" % (linha["run_id"], linha["ordem"], len(ligados))
    item = ligados[0]
    # P2 · a linha nao pode dizer que e de outro item
    for k_l, k_i in (("item_id", "ITEM_ID"), ("source_id", "SOURCE_ID")):
        if not _ign(linha.get(k_l)) and _txt(linha, k_l) != _txt(item, k_i):
            return item, "PRECO_DE_OUTRO_ITEM", "%s da linha = %s; do item = %s" % (k_l, linha[k_l], item.get(k_i))
    # P3 · os mesmos bytes
    sha_l, sha_i = _txt(linha, "raw_sha256").lower(), _txt(item, "RAW_SHA256").lower()
    if _ign(item.get("RAW_SHA256")):
        return item, "RAW_SHA256_DO_ITEM_NAO_SEI", "o item nao traz o sha dos bytes (raw_asset) — sem ele nao ha prova"
    if not RE_SHA256.match(sha_l):
        return item, "SHA_INVALIDO", "raw_sha256 da linha nao e sha256: %r" % sha_l[:70]
    if sha_l != sha_i:
        outros = sorted({_txt(i, "ITEM_ID") for i in itens if isinstance(i, dict) and i is not item
                         and _txt(i, "RAW_SHA256").lower() == sha_l})
        if outros:
            return item, "RAW_DE_OUTRO_ITEM", "o sha da linha e o RAW de %s, nao de %s" % (", ".join(outros),
                                                                                              item.get("ITEM_ID"))
        return item, "SHA_INCOMPATIVEL", "sha da linha %s... != sha do item %s..." % (sha_l[:12], sha_i[:12])
    if armazem is not None:
        if _ign(item.get("RAW_STORAGE_PATH")):
            return item, "RAW_BYTES_NAO_BATEM", "o item nao diz onde os bytes estao guardados"
        lido = _sha_dos_bytes(armazem, item["RAW_STORAGE_PATH"])
        if lido != sha_i:
            return item, "RAW_BYTES_NAO_BATEM", ("bytes ausentes no armazem" if lido is None
                                                 else "bytes relidos %s... != %s..." % (lido[:12], sha_i[:12]))
    # P4 · proveniencia
    if _ign(item.get("RAW_OBSERVATION_ID")):
        return item, "ITEM_SEM_PROVENIENCIA", "RAW_OBSERVATION_ID NAO SEI"
    # P5 / P6 · a citacao, literal, no ARTIGO deste item
    texto, cit = str(item.get("TEXTO") or ""), _txt(linha, "citacao_literal")
    if cit not in texto:
        return item, "CITACAO_FORA_DO_TEXTO", "a citacao nao esta literal no texto do item"
    no_artigo = ocorrencias_no_artigo(texto, cit)
    if not no_artigo:
        return item, "CITACAO_SO_FORA_DO_ARTIGO", ("a citacao so aparece em menu, barra lateral, bloco "
                                                   "vizinho ou rodape: e conteudo de outro artigo")
    # P7 · o que a linha diz esta dentro da citacao
    for k, motivo in (("valor_texto", "VALOR_FORA_DA_CITACAO"), ("unidade", "UNIDADE_FORA_DA_CITACAO")):
        if _txt(linha, k) not in cit:
            return item, motivo, "%s %r nao esta na citacao" % (k, linha[k])
    if _txt(linha, "cultura_literal").casefold() not in cit.casefold():
        return item, "CULTURA_FORA_DA_CITACAO", "cultura %r nao esta na citacao" % linha["cultura_literal"]
    # P8 · periodo
    ini, fim = _dia(linha["periodo_inicio"]), _dia(linha["periodo_fim"])
    if ini is None or fim is None or fim < ini:
        return item, "PERIODO_INVALIDO", "%s..%s" % (linha["periodo_inicio"], linha["periodo_fim"])
    cap = _dia(item.get("CAPTURED_AT") or "")
    if cap is not None and ini > cap:
        return item, "PERIODO_FUTURO", "o periodo comeca %s, depois da captura %s" % (ini, cap)
    # P9
    if _txt(linha, "classe") not in CLASSES:
        return item, "CLASSE_DESCONHECIDA", _txt(linha, "classe")
    return item, None, {"CITACAO_EM": no_artigo[0], "CAPTURA": str(cap) if cap else NAO_SEI}


def _periodo(linha) -> str:
    return "%s/%s" % (linha["periodo_inicio"], linha["periodo_fim"])


def objeto(linha: dict, item: dict, detalhe: dict, run_id: str, g0: str, fact_time_item) -> dict:
    """O objeto de mercado, tal como a corrida o produz (o pote so o transporta)."""
    texto = str(item.get("TEXTO") or "")
    praca = _txt(linha, "praca")
    praca_no_artigo = bool(praca) and bool(ocorrencias_no_artigo(texto, praca))
    periodo = _periodo(linha)
    ft_item = fact_time_item or {}
    bate = (ft_item.get("ESTADO") == "INTERVALO" and ft_item.get("INICIO") == linha["periodo_inicio"]
            and ft_item.get("FIM") == linha["periodo_fim"])
    doc = item.get("RAW_DOCUMENT_KEY")
    doc = doc if not _ign(doc) else (linha.get("document_id") if not _ign(linha.get("document_id")) else NAO_SEI)
    return {
        "OBJETO_ID": objeto_id(linha),
        "ESPECIE": "SINAL", "ESPECIE_DITA_POR": "INTELLIGENCE", "ESTADO": "EXPERIMENTAL_CANDIDATE",
        "CAPACIDADE": "CAP-MKT",
        "LEITURA": ("CONTEXTO_DE_MERCADO: um ponto de preco observado; nao e MARKET_FINDING (os cinco gates "
                    "CAP-MKT nao correm) nem mudanca de mercado (sem serie)"),
        "CHAVES": {
            "CROP_ID": NAO_SEI, "CULTURA_LITERAL": linha["cultura_literal"],
            "MARKET_PLACE_ID": NAO_SEI, "PRACA_DA_LINHA": praca or NAO_SEI,
            "NIVEL_DA_LINHA": _txt(linha, "nivel") or NAO_SEI,
            "PERIOD": periodo, "PRICE": linha["valor_texto"], "UNIT": linha["unidade"],
            "VALOR_NUMERICO": linha.get("valor_numerico") if linha.get("valor_numerico") is not None else NAO_SEI,
            "MARKET_STAGE": NAO_SEI,
            "INDICADOR": linha["indicador"], "CLASSE": linha["classe"],
            "FACT_TIME": periodo,
            "FACT_TIME_BASIS": ("LINHA_DE_PRECO_DA_SALA (periodo_inicio/periodo_fim) · %s o FACT_TIME do item"
                                % ("BATE com" if bate else "NAO bate com")),
            "FACT_LOCATION": praca if praca_no_artigo else NAO_SEI,
            "FACT_LOCATION_BASIS": ("praca da linha, escrita no corpo do artigo" if praca_no_artigo
                                    else "NAO SEI — a praca da linha nao esta escrita no corpo do artigo"),
            "O_QUE_NAO_PROVA": linha["o_que_nao_prova"],
        },
        "MARKET_STAGE_PORQUE": ("a Sala nao tem campo de estagio de mercado; NIVEL (%s) e escala geografica, "
                                "nao atacado/retalho" % (_txt(linha, "nivel") or NAO_SEI)),
        "LOCATION_SOURCE": "PRACA_DA_LINHA_DE_PRECO" if praca_no_artigo else NAO_SEI,
        "ENTITY_SOURCE": "CITACAO_DA_LINHA_DE_PRECO",
        "PROVA": [{
            "ITEM_ID": item.get("ITEM_ID"), "CORRIDA_UPSTREAM": item.get("CORRIDA"), "ORDEM": item.get("ORDEM"),
            "RAW_OBSERVATION_ID": item.get("RAW_OBSERVATION_ID"), "SOURCE_ID": item.get("SOURCE_ID"),
            "DOCUMENT_ID": doc, "URL": item.get("RAW_SOURCE_URL") or NAO_SEI,
            "PUBLICADO_EM": item.get("PUBLISHED_AT") or NAO_SEI, "COLHIDO_EM": item.get("CAPTURED_AT") or NAO_SEI,
            "FACT_TIME": periodo, "RAW_SHA256": item.get("RAW_SHA256"),
            "RAW_STORAGE_PATH": item.get("RAW_STORAGE_PATH") or NAO_SEI,
            "CITACAO": linha["citacao_literal"], "CITACAO_EM": detalhe["CITACAO_EM"],
            "ONDE": linha.get("prova_onde") or NAO_SEI,
        }],
        "G0_DO_ITEM": g0,
        "GATES_DO_PRECO": "P0..P10 PASSOU (%s)" % PRECO_RULESET_VERSION,
        "PORQUE": "linha de preco da Sala ligada por (run_id, ordem) ao item %s, citacao no corpo do artigo" % (
            item.get("ITEM_ID")),
        "CONTRADIZ": NAO_SEI,
        "INCERTEZA": ("UM ponto de preco (sinal solto, nao mudanca de mercado). %s MARKET_STAGE NAO SEI."
                      % linha["o_que_nao_prova"]),
        "INTELLIGENCE_RUN_ID": run_id, "REGRA": PRECO_RULESET_VERSION,
    }


def precos_da_corrida(precos: list, itens: list, run_id: str, lineage: list, tempo_do_item,
                      armazem=None) -> dict:
    """{OBJETOS, RECUSADOS, DUPLICADOS} — o que a corrida faz com as linhas de preco que recebeu."""
    g0_de = {(str(l.get("CORRIDA_UPSTREAM")), str(l.get("ITEM_ID")), str(l.get("RAW_OBSERVATION_ID"))): l.get("G0")
             for l in lineage}
    out = {"OBJETOS": [], "RECUSADOS": [], "DUPLICADOS": []}
    vistos = {}
    for n, linha in enumerate(precos or []):
        item, motivo, detalhe = conferir(linha, itens, armazem)
        ref = {"LINHA": n, "RUN_ID": (linha or {}).get("run_id") if isinstance(linha, dict) else NAO_SEI,
               "ORDEM": (linha or {}).get("ordem") if isinstance(linha, dict) else NAO_SEI,
               "ITEM_ID": item.get("ITEM_ID") if item else NAO_SEI}
        if motivo:
            out["RECUSADOS"].append(dict(ref, MOTIVO=motivo, DETALHE=detalhe))
            continue
        k = chave_natural(linha)
        if k in vistos:
            out["DUPLICADOS"].append(dict(ref, MOTIVO="DUPLICADO", DE=vistos[k]))
            continue
        g0 = g0_de.get((str(item.get("CORRIDA")), str(item.get("ITEM_ID")), str(item.get("RAW_OBSERVATION_ID"))),
                       NAO_SEI)
        o = objeto(linha, item, detalhe, run_id, g0, tempo_do_item(item.get("FACT_TIME")))
        vistos[k] = o["OBJETO_ID"]
        out["OBJETOS"].append(o)
    return out


def referencia_da_linha(linha) -> dict:
    """O que da linha entra na IDENTIDADE da corrida: a chave natural e os bytes (nunca o relogio)."""
    if not isinstance(linha, dict):
        return {"LINHA_INVALIDA": True}
    return dict(zip(CHAVE_NATURAL, chave_natural(linha)), raw_sha256=_txt(linha, "raw_sha256"),
                valor_texto=_txt(linha, "valor_texto"), unidade=_txt(linha, "unidade"),
                citacao_literal=_txt(linha, "citacao_literal"))
