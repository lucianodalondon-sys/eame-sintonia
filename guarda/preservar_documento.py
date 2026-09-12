#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O DONO DO DOCUMENTO ESTRUTURADO — e o único.

    RAW != DERIVED != STRUCTURED.

`guarda/preservar_coleta.py` escreve `raw_asset`. `guarda/preservar_derivado.py`
escreve `derived_artifact`. Este escreve `documento_estruturado`, e mais nada.

POR QUE ELE EXISTE, E NÃO É `social_persistencia`
--------------------------------------------------
`coleta/social_persistencia.py` é o dono de `public.conteudo`, e está certo
para o que ele é: a casa do que uma PLATAFORMA publica. As próprias colunas o
dizem — `canal.channel_id` é «o id da plataforma, NUNCA o nome», e
`conteudo.content_id` é «id da plataforma (video_id, post_id)».

Um boletim agrometeorológico em PDF, publicado no sítio de uma agência
regional, não tem nenhum dos dois. Não porque falte medir: porque **não há
plataforma**.

    SOURCE != ENDPOINT != ARTIFACT.
    PROVAR A FONTE E PROVAR O ENDPOINT NÃO CRIA UM CANAL.

Fazer este writer escrever em `conteudo` obrigaria a inventar um `canal_id` a
partir da URL, do domínio ou do nome da agência — e isso é identidade
fabricada, que é o defeito que esta casa paga para não cometer.

    ONE CONCEPT → ONE OWNER
    NÃO QUER DIZER UMA TABELA PARA TODO O TIPO DE CONTEÚDO.

O QUE ELE NÃO INVENTA
---------------------
`document_id` fica `None` quando a fonte não o prova. Não se deriva de
`sha256`, URL, filename, timestamp, slug nem `storage_path`.

    DOCUMENT_ID SÓ EXISTE QUANDO A FONTE CONSEGUE PROVÁ-LO.
    SEM PROVA: NÃO SEI.

E a identidade do REGISTO não é a do documento: o registo é o
`derived_artifact_id`, tal como a observação é o `raw_asset.id`. Uma coisa é o
nome que nós damos à linha; outra é o nome que o mundo deu ao documento.
"""
from __future__ import annotations

import hashlib
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

# Os estados, e são os mesmos do dono do derivado — de propósito. Quem lê dois
# writers desta casa não devia ter de aprender dois vocabulários.
INSERTED = "INSERTED"
REUSED = "REUSED"
TEXTO_DIVERGENTE = "TEXTO_DIVERGENTE"
SEM_FONTE = "SEM_FONTE"
SEM_TEXTO = "SEM_TEXTO"

# O que se compara num reencontro. É o CORPO, e não os campos opcionais: um
# título que apareceu depois não faz do registo outro registo.
RESULTADO = ("hash_texto", "source_id")

# ⚠️ OS ATALHOS QUE NÃO VIRAM `document_id`, E ELES ESTÃO AQUI POR NOME.
# A trava do banco recusa o hash. Os outros são deste ficheiro, porque é ele
# que vê o pedido inteiro e sabe de onde cada valor veio.
NAO_SAO_IDENTIDADE_DE_DOCUMENTO = ("hash_texto", "source_url", "storage_path",
                                   "sha256", "nome_do_ficheiro")


def _sql(v):
    if v is None:
        return "null"
    return "'%s'" % str(v).replace("'", "''")


def sha256(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


class MemoriaDoDocumento:
    """A porta do banco: escreve, e sobretudo deixa LER DE VOLTA."""

    def aplicar(self, sql: str) -> None:
        raise NotImplementedError

    def documento_do_derivado(self, derived_artifact_id) -> dict:
        """A linha que já estrutura este derivado, ou `None`."""
        raise NotImplementedError


def _identidade_provada(pedido: dict, hash_texto: str):
    """O `document_id`, e só quando ele foi PROVADO pela fonte.

    ⚠️ ESTA FUNÇÃO EXISTE PARA DIZER NÃO. Ela não constrói identidade: ela
    recusa os valores que se parecem com identidade e não são.

        O HASH IDENTIFICA BYTES.
        A URL É UM ENDEREÇO.
        O NOME DO FICHEIRO É UMA ESCOLHA DE QUEM O GRAVOU.

    Nenhum dos três diz que documento isto é no mundo. Quem sabe é a fonte —
    um número de boletim, um registo, um DOI — e quando ela não diz, a resposta
    é ausência.
    """
    declarado = pedido.get("document_id")
    if declarado is None or not str(declarado).strip():
        return None
    declarado = str(declarado).strip()
    if declarado.upper() in ("NAO SEI", "NAO_SEI", "UNKNOWN", "NULL", "NONE"):
        return None
    # Um `document_id` que é igual a um valor que NÃO é identidade foi
    # fabricado a partir dele, ainda que quem o passou não soubesse.
    for campo in NAO_SAO_IDENTIDADE_DE_DOCUMENTO:
        valor = hash_texto if campo == "hash_texto" else pedido.get(campo)
        if valor and declarado == str(valor):
            raise ValueError(
                "document_id fabricado a partir de `%s`: %r. DOCUMENT_ID SO "
                "EXISTE QUANDO A FONTE CONSEGUE PROVA-LO." % (campo, declarado))
    return declarado


def preservar_documento(pedido: dict, memoria: MemoriaDoDocumento) -> dict:
    """Escreve UM documento estruturado, e lê de volta o que escreveu.

        MEDIR O CORPO → LER A IDENTIDADE → COMPARAR → ESCREVER → RELER

    O que o chamador entrega: `derived_artifact_id`, `run_id`, `source_id`,
    `texto`, e — só quando provados — `document_id`, `source_url`, `titulo`.
    O `hash_texto` é deste ficheiro.

    ⚠️ REENCONTRO NÃO É SUCESSO PRESUMIDO. Quando a linha já existe, ela é
    LIDA e comparada campo a campo com o que esta passagem produziu. Corpo
    diferente para o mesmo derivado é `TEXTO_DIVERGENTE` — não se sobrescreve,
    e não se chama a isso REUSED.
    """
    texto = pedido.get("texto")
    if texto is None or not str(texto).strip():
        return {"ESTADO": SEM_TEXTO,
                "PORQUE": ("nao ha corpo para estruturar. Um registo de "
                           "documento sem texto seria uma ficha vazia com "
                           "cara de conteudo.")}
    fonte = pedido.get("source_id")
    if not fonte or not str(fonte).strip():
        return {"ESTADO": SEM_FONTE,
                "PORQUE": ("o documento nao diz de que fonte veio, e a fonte "
                           "nao se reconstroi do caminho nem da URL.")}

    hash_texto = sha256(texto.encode("utf-8"))
    documento = _identidade_provada(pedido, hash_texto)

    esperado = {
        "derived_artifact_id": int(pedido["derived_artifact_id"]),
        "run_id": str(pedido["run_id"]),
        "source_id": str(fonte).strip(),
        "hash_texto": hash_texto,
        "document_id": documento,
        "source_url": pedido.get("source_url"),
        "titulo": pedido.get("titulo"),
    }

    ja = memoria.documento_do_derivado(esperado["derived_artifact_id"])
    if ja:
        divergem = [c for c in RESULTADO
                    if str(ja.get(c)) != str(esperado.get(c))]
        if divergem:
            return {"ESTADO": TEXTO_DIVERGENTE, "DIVERGENCIAS": divergem,
                    "LINHA_EXISTENTE": ja,
                    "PORQUE": ("o mesmo derivado ja tem registo, e o corpo ou "
                               "a fonte nao batem. Nao se apaga e nao se "
                               "escreve por cima: as duas versoes sao factos, "
                               "e uma delas e um defeito por descobrir.")}
        return {"ESTADO": REUSED, "LINHA_EXISTENTE": ja,
                "DOCUMENTO_ESTRUTURADO_ID": ja["derived_artifact_id"],
                "PORQUE": ("reencontro: o mesmo derivado ja estava "
                           "estruturado, e o corpo foi LIDO e comparado.")}

    memoria.aplicar(
        "insert into public.documento_estruturado "
        "(derived_artifact_id, run_id, source_id, texto, hash_texto,"
        " document_id, source_url, titulo) values (%d, %s, %s, %s, %s, %s, %s,"
        " %s) on conflict (derived_artifact_id) do nothing;"
        % (esperado["derived_artifact_id"], _sql(esperado["run_id"]),
           _sql(esperado["source_id"]), _sql(texto), _sql(hash_texto),
           _sql(documento), _sql(esperado["source_url"]),
           _sql(esperado["titulo"])))

    # ⚠️ E QUEM DECIDE E A RELEITURA, e nao o retorno do insert. Com
    # `on conflict do nothing`, um insert que nao escreveu nada tambem nao
    # levanta — e a diferenca entre «escrevi» e «alguem chegou primeiro» so se
    # ve lendo.
    escrita = memoria.documento_do_derivado(esperado["derived_artifact_id"])
    if not escrita:
        return {"ESTADO": SEM_TEXTO,
                "PORQUE": ("o insert correu e a linha nao esta la. Nao se "
                           "presume: leu-se, e nao havia.")}
    divergem = [c for c in RESULTADO
                if str(escrita.get(c)) != str(esperado.get(c))]
    if divergem:
        return {"ESTADO": TEXTO_DIVERGENTE, "DIVERGENCIAS": divergem,
                "LINHA_EXISTENTE": escrita,
                "PORQUE": ("outro escritor ganhou a corrida e escreveu outro "
                           "corpo para o mesmo derivado.")}
    return {"ESTADO": INSERTED, "LINHA_ESCRITA": escrita,
            "DOCUMENTO_ESTRUTURADO_ID": escrita["derived_artifact_id"],
            "DOCUMENT_ID": documento,
            "PORQUE": "escrita, lida de volta e conferida campo a campo."}
