#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PORTA DE ENTRADA DA COLETA — uma, e a mesma para toda a fonte.

    UMA UNIDADE DE INFORMACAO ENTRA UMA VEZ NA COLLECTION.

O PROBLEMA QUE ISTO FECHA
-------------------------
`leis/artefato.py` foi escrito com esta frase no cabecalho:

    «Hoje cada executor entrega o resultado a sua maneira: um deixa uma pasta,
     outro um JSON, outro um PDF. Ligar o orquestrador a isto obrigaria o
     cerebro da casa a ADIVINHAR o que cada um produziu.»

O contrato foi escrito. O orquestrador nunca o adoptou, e continuou a adivinhar
— literalmente. `orquestrador.a_colheita()` abre cada `*.json` da pasta que o
executor declarou e faz isto:

    lista = d if isinstance(d, list) else next(
        (v for v in d.values() if isinstance(v, list) and v
         and isinstance(v[0], dict)), [])

«o primeiro campo do ficheiro que seja uma lista de fichas». Qualquer dicionario
encontrado ali virava um item da coleta e ia direto a porta de admissao.

    ISSO NAO E UMA PORTA. E UM CHAO POR ONDE AS COISAS ENTRAM.

E o que se perdia nao era pouco: sem passar pelo contrato, o item chegava a
admissao sem impressao digital, sem hora de colheita, sem corrida, e sobretudo
SEM TER SIDO PRESERVADO. A etapa RAW existia, estava provada contra Postgres, e
`tests/test_preservar_coleta_no_banco.py` guardava a honestidade disso por
escrito:

    «Medido: nenhum ficheiro de producao chama `preservar()`.»

O QUE ESTA PORTA FAZ, E O QUE ELA RECUSA FAZER
-----------------------------------------------
Ela responde UMA pergunta:

    POSSO PRESERVAR ESTA OBSERVACAO COMO RAW?

e nao a outra, que e da admissao:

    ESTE OBJECTO PODE ENTRAR NO UNIVERSO UTILIZAVEL?

Por isso ela nao julga relevancia, nao classifica, nao pontua e nao decide
universo. Ela transforma o que o coletor largou numa ficha do contrato comum,
confere as leis que o contrato ja escreve, e entrega ao DONO DO RAW —
`guarda/preservar_coleta.preservar()`. Nada aqui sabe como a tabela `raw_asset`
e feita por dentro; isso e do dono, e continua a ser.

    O COLETOR OBSERVA. A PORTA PRESERVA. A ADMISSAO JULGA.

O QUE ELA NUNCA INVENTA
-----------------------
`FACT_TIME` e `FACT_LOCATION` ficam como o coletor os deu, e o coletor
normalmente nao os sabe — entao ficam `NAO SEI`. Enche-los com a hora da
colheita ou com o pais da fonte seria destruir exactamente a informacao que
`leis/artefato.py` existe para separar:

    FACT_TIME != PUBLICATION_TIME != OBSERVED_TIME != COLLECTED_TIME
    SOURCE_LOCATION != FACT_LOCATION

O que ela preenche e so o que ela MEDIU: os bytes, o sha, o tamanho, a hora em
que ESTA maquina os recebeu, e quem correu.
"""
from __future__ import annotations

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import artefato as art                                    # noqa: E402
from guarda.preservar_coleta import ArmazemLocal, preservar  # noqa: E402

# O que a porta recusa, com nome. Cada um destes e uma RECUSA da porta — nunca
# um ERRO da coleta, e nunca uma REJEICAO da admissao, que e outra pergunta.
#
#     RECUSA_NA_PORTA != REJEITADO_NA_ADMISSAO != ERRO != NAO_CORREU.
SEM_CORRIDA = "INGRESS_SEM_CORRIDA"
SEM_CONTEUDO = "INGRESS_SEM_CONTEUDO"
CONTRATO_QUEBRADO = "INGRESS_CONTRATO_QUEBRADO"
RECUSAS = (SEM_CORRIDA, SEM_CONTEUDO, CONTRATO_QUEBRADO)

# Os campos que o coletor PODE declarar e que a porta transporta sem tocar.
# Nao ha valor por omissao nenhum aqui: o que o coletor nao disser fica NAO SEI.
DO_COLETOR = ("SOURCE_ID", "SOURCE_URL", "PUBLISHER", "COUNTRY_SCOPE",
              "SOURCE_LOCATION", "FACT_LOCATION", "ITEM_LANGUAGE",
              "FACT_TIME", "PUBLISHED_AT", "OBSERVED_AT",
              "EXECUTOR_ID", "EXECUTOR_VERSION", "PIPELINE_VERSION")


def _bytes_do_item(item: dict) -> bytes:
    """A observacao, como bytes, sem normalizar nada.

    Um item que veio como JSON E o JSON: assina-se o que se recebeu. Ordenar as
    chaves nao e arrumacao — e o que torna a impressao digital reproduzivel
    quando o mesmo objecto e observado outra vez.
    """
    return json.dumps(item, ensure_ascii=False, sort_keys=True).encode("utf-8")


def ficha(item: dict, *, corrida: dict, raiz: str = RAIZ) -> art.Artefato:
    """A ficha do contrato comum para uma observacao que o coletor largou.

    Se o item aponta para um ficheiro que existe, a ficha e desse ficheiro — os
    bytes preservados sao os bytes originais. Se nao aponta, a observacao E o
    item, e e ele que se preserva.
    """
    caminho = item.get("STORAGE_LOCATION") or item.get("_de") or ""
    abs_ = os.path.join(raiz, caminho) if caminho else ""
    declarados = {k: item[k] for k in DO_COLETOR if item.get(k)}
    comum = dict(
        RUN_ID=corrida.get("RUN_ID", art.NAO_SEI),
        COLLECTED_AT=corrida.get("STARTED_AT") or art.agora(),
        **declarados)

    if abs_ and os.path.isfile(abs_):
        return art.raw_do_disco(abs_, raiz, **comum)

    dados = _bytes_do_item(item)
    sha = art.hashlib.sha256(dados).hexdigest()
    return art.Artefato(
        ARTIFACT_ID=art.artifact_id(sha, art.RAW),
        ARTIFACT_TYPE=art.RAW,
        # A OBSERVACAO NAO TEM FICHEIRO DE ORIGEM, e por isso o sitio dela e
        # derivado do sha e nao de um nome que alguem escolheu. Nome escolhido
        # colide; sha nao.
        STORAGE_LOCATION="data/raw/observacoes/%s.json" % sha,
        SHA256=sha,
        CONTENT_TYPE="application/json",
        BYTES=len(dados),
        **comum)


# O que o DONO DO RAW le da corrida. Nao e a mesma lista do RUN-MANIFEST — e a
# lista dele, e e ele que manda no que ele le.
CORRIDA_PARA_O_RAW = ("RUN_ID", "PLATFORM", "ACTOR", "ACTOR_VERSION",
                      "RULE_VERSION", "SOURCE_COUNTRY", "STARTED_AT")


def _corrida_completa(corrida: dict) -> dict:
    """A corrida na lingua do dono do RAW, sem inventar o que nao veio.

    Campo que o chamador nao trouxe fica `NOT_PRESERVED` — a confissao que o
    manifesto desta casa ja define — e NAO fica ausente. Ausente rebentaria a
    colheita inteira por causa de um campo; e preenchido com um palpite seria
    pior, porque passaria a parecer medido.

        NOT_PRESERVED != AUSENTE != NAO SEI != ZERO.
    """
    fora = dict(corrida)
    for c in CORRIDA_PARA_O_RAW:
        if not fora.get(c):
            fora[c] = "NOT_PRESERVED"
    fora["RUN_ID"] = corrida.get("RUN_ID") or ""
    fora["STARTED_AT"] = corrida.get("STARTED_AT") or art.agora()
    return fora


def _slug(v: str) -> str:
    """`IT-T2-002` -> `it-t2-002`. Endereco, nunca identidade."""
    return "".join(c if c.isalnum() else "-" for c in str(v).lower()).strip("-") or "sem-fonte"


def para_o_dono_do_raw(f: art.Artefato, item: dict) -> dict:
    """A ficha do contrato comum, na lingua do DONO DO RAW.

    ⚠️ ESTA TRADUCAO E A PECA QUE FALTAVA, E A SUA AUSENCIA EXPLICA TUDO.
    A casa tem DUAS linguas de artefato, e as duas estao certas:

        leis/artefato.Artefato          como o EXECUTOR entrega
        guarda/preservar_coleta         como o ARMAZEM enderecа

    `preservar()` nunca aceitou um `Artefato`: ele pede `COUNTRY`,
    `SOURCE_SLUG`, `ARTIFACT_KIND`, `SOURCE_NATIVE_ID`, `NAME` — o endereco do
    byte. Nada no repositorio ligava as duas, e por isso nenhum ficheiro de
    producao conseguia chamar o dono do RAW sem falar a lingua dele a mao.

        DOIS CONTRATOS CERTOS E NENHUMA PONTE
        SAO DOIS CONTRATOS QUE NAO SE USAM.

    A traducao NAO inventa: o que a ficha nao souber vai como `NAO SEI`, e o
    identificador nativo, quando a fonte nao o deu, e o proprio sha — que e
    verdade sobre os bytes, e nao um nome escolhido por nos.
    """
    nativo = (item.get("SOURCE_NATIVE_ID") or item.get("ID")
              or item.get("id") or f.SHA256[:16])
    nome = os.path.basename(f.STORAGE_LOCATION)
    return {
        "COUNTRY": f.COUNTRY_SCOPE if f.COUNTRY_SCOPE != art.NAO_SEI else "XX",
        "SOURCE_SLUG": _slug(f.SOURCE_ID),
        # RAW e DERIVED sao ESPECIES do contrato; no armazem a especie do byte
        # e outra pergunta, e a resposta honesta para uma observacao e OBSERVATION.
        "ARTIFACT_KIND": "DOCUMENT" if f.CONTENT_TYPE == "application/pdf"
                         else "OBSERVATION",
        "NAME": nome,
        "SOURCE_NATIVE_ID": _slug(nativo),
        "SHA256": f.SHA256,
        "BYTES": f.BYTES,
        "MEDIA_TYPE": f.CONTENT_TYPE,
        # CAPTURED_AT e a hora em que ESTA maquina recebeu. Nao e FACT_TIME,
        # nao e PUBLISHED_AT, e nao se enche com nenhuma das duas.
        "CAPTURED_AT": f.COLLECTED_AT,
        "SOURCE_URL": f.SOURCE_URL,
        "USED_BY": item.get("USED_BY"),
        "ARTIFACT_ID": f.ARTIFACT_ID,
    }


def receber(itens: list, *, corrida: dict, armazem, memoria=None,
            raiz: str = RAIZ) -> dict:
    """A porta. Devolve o que entrou, o que foi recusado, e o recibo do RAW.

    NAO levanta por item mau: um item que quebra o contrato e uma RECUSA com
    nome, e a corrida continua. Rebentar aqui faria uma observacao estragada
    apagar todas as outras da mesma colheita.
    """
    if not corrida.get("RUN_ID"):
        # Sem corrida nao ha procedencia, e sem procedencia nao ha RAW
        # canonico. O dono do RAW recusa isto de qualquer maneira; recusar aqui
        # da o nome antes de gastar o resto.
        return {"ACEITES": [], "RECUSAS": [{"PORQUE": SEM_CORRIDA,
                                            "DETALHE": "corrida sem RUN_ID"}],
                "RAW": None}

    aceites, recusas, bytes_por_caminho, para_o_raw = [], [], {}, []
    for i, item in enumerate(itens):
        if not isinstance(item, dict) or not item:
            recusas.append({"INDICE": i, "PORQUE": SEM_CONTEUDO,
                            "DETALHE": "a observacao nao e um objecto com campos"})
            continue
        f = ficha(item, corrida=corrida, raiz=raiz)
        quebras = art.conferir(f)
        if quebras:
            recusas.append({"INDICE": i, "PORQUE": CONTRATO_QUEBRADO,
                            "ARTIFACT_ID": f.ARTIFACT_ID, "DETALHE": quebras})
            continue
        caminho = os.path.join(raiz, f.STORAGE_LOCATION)
        bytes_por_caminho[f.SHA256] = (
            open(caminho, "rb").read() if os.path.isfile(caminho)
            else _bytes_do_item(item))
        aceites.append(f)
        para_o_raw.append(para_o_dono_do_raw(f, item))

    recibo = None
    if para_o_raw:
        recibo = preservar(_corrida_completa(corrida), para_o_raw, armazem,
                           lambda o: bytes_por_caminho[o["SHA256"]],
                           memoria=memoria)
    return {"ACEITES": aceites, "RECUSAS": recusas, "RAW": recibo}
