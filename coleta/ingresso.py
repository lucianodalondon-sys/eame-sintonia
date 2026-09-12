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
# ⚠️ O DONO DO RASTRO, E NAO UMA SEGUNDA TELEMETRIA.
# `medidas/rastro_da_coleta.py` ja escreve as passagens de DERIVED, STRUCTURED
# e ADMISSION. A etapa RAW estava no vocabulario (`telemetria.ETAPAS_DA_COLETA`)
# e era muda. Esta porta passa a contar-lhe a passagem na MESMA lingua.
import rastro_da_coleta as rastro                           # noqa: E402
import diagnostico as dg                                    # noqa: E402

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


# ── A LINGUA DA PORTA — UM SO TRADUTOR, NA FRONTEIRA ───────────────────────
#
#     O COLETOR OBSERVA. A PORTA PRESERVA. A ADMISSAO JULGA.
#
# O contrato comum (`leis/artefato.py`) fala em MAIUSCULAS. A admissao le
# minusculas. Sao dez conceitos com dois nomes cada, e o defeito NAO era «a
# admissao le minusculas»: era que a traducao JA EXISTIA, escrita a mao, em
# dois sitios diferentes e com subconjuntos diferentes —
# `coleta/golden_path_pdf.py` e `coleta/rota_forward_documento.py` — enquanto a
# rota canonica (o orquestrador) nao traduzia de todo.
#
#     UMA TRADUCAO SEM DONO NAO E UMA TRADUCAO: SAO TRES.
#
# E o remendo obvio seria o pior de todos:
#
#     item.get("SOURCE_ID") or item.get("source_id") or item.get("fonte")
#
# espalhado por cada leitor. Isso nao da um dono a traducao — da-lhe um por
# ficheiro, e eles divergem no dia em que alguem acrescentar um alias a um so.
#
# Vive AQUI porque aqui e a fronteira: esta peca ja «transforma o que o coletor
# largou numa ficha do contrato comum». Traduzir para a lingua de quem julga e
# a mesma travessia, no mesmo sitio, uma vez.
PARA_A_PORTA = {
    "SOURCE_ID": "source_id",
    "SOURCE_URL": "url",
    "FACT_TIME": "fact_time",
    "PUBLISHED_AT": "published_at",
    "FACT_LOCATION": "fact_location",
    "SOURCE_LOCATION": "source_location",
    "ARTIFACT_TYPE": "artifact_type",
    "PARENT_ARTIFACT_ID": "parent_artifact_id",
    "PARENT_SHA256": "parent_sha256",
    "COLLECTED_AT": "captured_at",
}


class AliasEmConflito(ValueError):
    """Dois nomes do mesmo conceito, com valores diferentes.

    NAO SE ESCOLHE EM SILENCIO. Escolher o maiusculo seria arbitrario; escolher
    o minusculo tambem. Um item que se contradiz sobre a propria origem nao e um
    item com um campo a mais: e um item que nao se consegue ler.
    """


def para_a_porta(item: dict) -> dict:
    """O item na lingua de quem julga. Muda o NOME; nunca o VALOR.

    O que ja vem na lingua da porta fica. O que nao esta no mapa viaja intacto —
    `DOCUMENT_ID` nao tem par do outro lado, e cala-lo aqui seria esta peca a
    decidir o que a casa pode vir a saber.

    Ausencia continua ausencia: `NAO SEI` nao se fabrica nesta funcao, e um
    campo que o coletor nao deu nao aparece do lado de la como string vazia.
    """
    fora = dict(item)
    for de, para in PARA_A_PORTA.items():
        if de not in item:
            continue
        valor = item[de]
        if para in item and item[para] != valor:
            raise AliasEmConflito(
                "«%s» e «%s» sao o mesmo conceito e trazem valores diferentes: "
                "%r contra %r. Nao se escolhe um em silencio."
                % (de, para, valor, item[para]))
        fora[para] = valor
        # RENOMEIA, NAO DUPLICA. Deixar os dois nomes na saida seria entregar a
        # quem julga exactamente a doenca que esta funcao veio curar: um item a
        # falar duas linguas ao mesmo tempo, e o proximo leitor a escolher uma.
        fora.pop(de, None)
    return fora


# ── O QUE O CONTRATO APUROU, E QUE TEM DE CHEGAR A QUEM JULGA ──────────────
#
#     COL-LAW-502 · DOCUMENTO PRONTO NAO E FATO PRONTO.
#
# A porta ja sabe aplicar essa lei: `admissao.estagio()` le `artifact_type`, e a
# um RAW nao se pergunta o tempo do FATO. So que o estagio nunca lhe chegava.
# `orquestrador.pela_entrada` devolvia `len(r["ACEITES"])` e entregava a porta o
# item ORIGINAL — de seis campos, sem estagio nenhum.
#
#     CONTAR UMA COISA NAO E GUARDA-LA.
#
# O bloqueio da unidade italiana nunca foi `FACT_TIME`: era a perda do estagio.
# Medido — o mesmo item, com `ARTIFACT_TYPE = RAW` preservado, deixa de ouvir
# «o item nao diz quando o fato aconteceu».
#
# ⚠️ E HA UMA ARMADILHA AQUI, medida antes de escrever isto. A ficha preenche
# com `NAO SEI` o que o coletor nao disse. Junta-la ao item sem cuidado poria
# `fact_time = "NAO SEI"` — e `_tem_quando` le isso como VALOR:
#
#     fact_time=''          -> NAO_SEI  «o item nao diz quando»
#     fact_time='NAO SEI'   -> passa, como se fosse uma data
#
#     A CONFISSAO DE IGNORANCIA NAO E UM VALOR.
#     JUNTA-LA COMO SE FOSSE E MENTIR COM A PALAVRA CERTA.
#
# Por isso so atravessam AFIRMACOES. O que o contrato nao sabe fica ausente do
# lado de la, que e exactamente o que ele e.
NAO_E_AFIRMACAO = (art.NAO_SEI, "NAO_SE_APLICA", "", None)

# O que o CONTRATO sabe melhor do que o item: a especie e a linhagem. O resto
# do item e dele, e nao se toca — o conteudo vive no item, nao na ficha.
DA_FICHA_PARA_A_PORTA = ("ARTIFACT_TYPE", "PARENT_ARTIFACT_ID", "PARENT_SHA256")


def unidade_para_a_porta(item: dict, ficha) -> dict:
    """O conteudo original MAIS o que o contrato apurou, na lingua de quem julga.

    O item manda no conteudo — `texto` vive nele e nao na ficha. A ficha manda
    no estagio, porque foi ela que o apurou. Nada e reescrito: um campo que o
    item ja afirma nao e tocado.
    """
    fora = dict(item)
    for campo in DA_FICHA_PARA_A_PORTA:
        valor = getattr(ficha, campo, None)
        if valor in NAO_E_AFIRMACAO:
            continue
        fora.setdefault(campo, valor)
    return para_a_porta(fora)


def _bytes_do_item(item: dict) -> bytes:
    """A observacao, como bytes, sem normalizar nada.

    Um item que veio como JSON E o JSON: assina-se o que se recebeu. Ordenar as
    chaves nao e arrumacao — e o que torna a impressao digital reproduzivel
    quando o mesmo objecto e observado outra vez.

    As chaves com `_` a frente NAO entram, e nao e arrumacao tambem: sao
    anotacoes que esta casa poe no item DEPOIS de o receber — `_de` diz de que
    ficheiro ele foi lido. Deixa-las entrar faria a impressao digital da
    observacao mudar quando o ficheiro de colheita mudasse de nome, e a mesma
    observacao passaria a ser duas.

        A IDENTIDADE E DO QUE SE OBSERVOU, NAO DE ONDE SE LEU.
    """
    limpo = {k: v for k, v in item.items() if not str(k).startswith("_")}
    return json.dumps(limpo, ensure_ascii=False, sort_keys=True).encode("utf-8")


def ficha(item: dict, *, corrida: dict, raiz: str = RAIZ) -> art.Artefato:
    """A ficha do contrato comum para uma observacao que o coletor largou.

    Se o item aponta para um ficheiro que existe, a ficha e desse ficheiro — os
    bytes preservados sao os bytes originais. Se nao aponta, a observacao E o
    item, e e ele que se preserva.

    ⚠️ AQUI ESTAVA `or item.get("_de")`, E ELE CONTRADIZIA O PARAGRAFO ACIMA.
    `_de` e posto pelo orquestrador em `a_colheita`, e diz de que FICHEIRO DE
    COLHEITA o item foi extraido — um ficheiro que, por construcao, traz uma
    LISTA de itens. Usa-lo como origem dos bytes dava a todas as observacoes
    da mesma colheita o mesmo `sha256`, e portanto o mesmo caminho no armazem:

        cem observacoes  ->  um unico `raw_asset`, com os bytes do ficheiro
                             inteiro, e as outras noventa e nove caladas.

    Nao era um caso de bordo: era o caminho normal de qualquer executor que
    larga uma lista. A observacao que nao aponta para ficheiro E o item — como
    esta docstring sempre disse — e e assim que ela se preserva agora.

        O SITIO DE ONDE UM ITEM FOI LIDO NAO E O CORPO DO ITEM.
    """
    caminho = item.get("STORAGE_LOCATION") or ""
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


# ── COMO CADA CAMPO DIZ «NAO VEIO» ────────────────────────────────────────
# ⚠️ A CONFISSAO TEM DE CABER NA COLUNA QUE A RECEBE. `NOT_PRESERVED` e a
# palavra desta casa e continua a ser; mas `collection_run.source_country` nao
# e texto: e o enum `pais`, e o vocabulario dele e outro —
#
#     ES · FR · IT · PT · EU · BR · OTHER · NAO_SEI
#
# MEDIDO contra PostgreSQL 16 com as 27 migrations aplicadas:
#
#     corrida COMPLETA  ->  raw_asset = 1 · RUN_STATE = COMPLETE
#     corrida sem pais  ->  raw_asset = 0 · RUN_STATE = PARTIAL
#                           ERROR: invalid input value for enum pais:
#                           "NOT_PRESERVED"
#
# O bruto nao aterrava, e nao aterrava EM SILENCIO para quem nao lesse o
# recibo. E a mesma familia do defeito do `SOURCE_ID` (§60): um valor honesto
# de um lado que o outro lado nao aceita.
#
#     UMA CONFISSAO QUE A COLUNA RECUSA
#     NAO E UMA CONFISSAO: E UMA PERDA.
#
# ⚠️ E ISTO NAO COLAPSA OS DOIS CONCEITOS. `NOT_PRESERVED != NAO SEI` continua
# a valer, e continua a ser o que os outros campos recebem. O que esta tabela
# diz e outra coisa: QUAL DAS DUAS PALAVRAS o dono de CADA campo entende. Quem
# manda no vocabulario da ausencia e o dono da coluna, e nao a fronteira.
#
# `pais` ja declara `NAO_SEI` como o seu proprio default — o autor do esquema
# ja tinha decidido o que e um pais nao declarado. Aqui so se OBEDECE a essa
# decisao, em vez de lhe impor a palavra de outro contrato.
AUSENCIA_POR_CAMPO = {
    "SOURCE_COUNTRY": "NAO_SEI",     # enum `pais`, migration 001
}
AUSENCIA_PADRAO = "NOT_PRESERVED"


def _corrida_completa(corrida: dict) -> dict:
    """A corrida na lingua do dono do RAW, sem inventar o que nao veio.

    Campo que o chamador nao trouxe fica com a CONFISSAO QUE O DONO DAQUELE
    CAMPO ENTENDE — `NOT_PRESERVED` para quase todos, e a palavra propria da
    coluna quando ela tem uma. E NAO fica ausente: ausente rebentaria a
    colheita inteira por causa de um campo, e preenchido com um palpite seria
    pior, porque passaria a parecer medido.

        NOT_PRESERVED != AUSENTE != NAO SEI != ZERO.

    Os quatro continuam diferentes. O que mudou nao foi o significado: foi
    deixar de escrever uma palavra onde ela nao e lingua.
    """
    fora = dict(corrida)
    for c in CORRIDA_PARA_O_RAW:
        if not fora.get(c):
            fora[c] = AUSENCIA_POR_CAMPO.get(c, AUSENCIA_PADRAO)
    fora["RUN_ID"] = corrida.get("RUN_ID") or ""
    fora["STARTED_AT"] = corrida.get("STARTED_AT") or art.agora()
    return fora


# As confissoes que NAO identificam nada. Uma fonte que responde «NAO SEI» ao
# identificador nativo nao deu identificador nenhum, e tratar a confissao como
# discriminante poria a mesma palavra no endereco de tudo o que ela nao soube.
_SENTINELAS = frozenset(("NAO SEI", "NAO_SEI", "NÃO SEI", "NAO_SE_APLICA",
                         "UNKNOWN", "NOT_KNOWN"))


def _slug(v: str) -> str:
    """`IT-T2-002` -> `it-t2-002`. Endereco, nunca identidade."""
    return "".join(c if c.isalnum() else "-" for c in str(v).lower()).strip("-") or "sem-fonte"


def _sem_fragmento(url: str) -> str:
    """A URL sem o `#pedaco`, e sem mais nada tirado.

    O fragmento NUNCA chega ao servidor — ele e do browser. Duas URLs que so
    diferem nele pediram o MESMO recurso, e trata-las como duas guardaria o
    mesmo byte em dois enderecos.

    ⚠️ E A QUERYSTRING FICA. A tentacao e limpa-la tambem — «parametros sao
    ruido» — e ela esta errada nesta casa: `?id=731` e `?id=6321` sao dois
    DOCUMENTOS na mesma fonte, medido nos 195 objectos italianos. Uma limpeza
    que junta esses dois nao arruma nada: apaga um facto.
    """
    return str(url).split("#", 1)[0]


def _discriminante_do_endereco(f: art.Artefato, item: dict) -> str:
    """O que SEPARA duas publicacoes no endereco do armazem.

    ⚠️ ISTO ERA UM `or` COM QUATRO PERNAS E A ULTIMA ERA O PROPRIO CONTEUDO:

        nativo = SOURCE_NATIVE_ID or ID or id or f.SHA256[:16]

    E a ultima perna colapsava factos. Medido pelo codigo de producao, com dois
    ficheiros distintos, conteudo identico e o MESMO nome de base:

        XX/…/0b5c068c31e225fe-0b5c068c31e225fe-FDS.pdf
        XX/…/0b5c068c31e225fe-0b5c068c31e225fe-FDS.pdf     UM ENDERECO SO

    Duas publicacoes espremidas numa. E como o caminho e unico em
    `storage_object`, a segunda nunca chegava a existir.

    A ESCADA, DA PROVA MAIS FORTE PARA A MAIS FRACA:

        1. o identificador que a FONTE deu             `media/731`
        2. a URL que esta casa PEDIU, sem o fragmento  `u<sha16 da url>`
        3. o proprio conteudo                          `<sha16 dos bytes>`

    O degrau 2 e um ENDERECO, e nunca uma identidade de documento: ele nao vira
    `DOCUMENT_KEY`, nao entra em `identidade_da_observacao()` e nao promove
    ninguem a `FORWARD_IDENTIFIED`. Duas ideias diferentes, e e por isso que
    esta funcao vive aqui e nao la.

        ENDERECO FISICO  !=  IDENTIDADE DO DOCUMENTO

    A URL vai HASHADA e nao inteira: um caminho de armazem com uma querystring
    dentro fica ilegivel e comprido, e o que se precisa dela e que SEPARE — nao
    que se leia. O prefixo `u` diz de que degrau o discriminante veio, e isso
    e legivel no proprio caminho.

    E O DEGRAU 3 CONTINUA A COLAPSAR, DE PROPOSITO. Sem identificador e sem
    URL nao ha NENHUMA evidencia de que sejam duas coisas — e inventar uma
    seria fabricar a distincao em vez de a medir. Colapsar aqui e a resposta
    honesta; o que era defeito era colapsar quando a evidencia existia.
    """
    for chave in ("SOURCE_NATIVE_ID", "ID", "id"):
        v = item.get(chave)
        if v and str(v).strip() and str(v).strip().upper() not in _SENTINELAS:
            return str(v).strip()
    url = item.get("SOURCE_URL") or f.SOURCE_URL
    if url and str(url).strip() and str(url).strip().upper() not in _SENTINELAS:
        return "u" + art.hashlib.sha256(
            _sem_fragmento(url).encode("utf-8")).hexdigest()[:16]
    return f.SHA256[:16]


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
    nativo = _discriminante_do_endereco(f, item)
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
        # ── B5B · A IDENTIDADE VIAJA INTEIRA, E NAO DERRETIDA ────────────
        # `SOURCE_SLUG` acima e o ENDERECO — `it-t2-002`, e `it-t2-002` nao se
        # reconverte em `IT-T2-002` sem adivinhar. O codigo canonico da fonte
        # vai aqui, tal como o coletor o declarou.
        #
        #     A IDENTIDADE NAO ERA DESCONHECIDA. ELA NAO VIAJAVA.
        #
        # E quando o coletor nao a declarou, o que viaja e a confissao dele
        # (`NAO SEI`) — nao um campo vazio que o dono do RAW leria como
        # ausencia inocente. O dono do RAW recusa a confissao; recusar um
        # branco seria recusar sem saber o que se recusa.
        "SOURCE_ID": f.SOURCE_ID,
        # O DOCUMENT_ID sai do ITEM ORIGINAL, e so existe quando o contrato da
        # fonte o produziu. Nao se calcula aqui, nao se cai para o sha e nao se
        # troca por `DOCUMENT_VERSION_ID`, que e outra pergunta.
        "DOCUMENT_ID": item.get("DOCUMENT_ID"),
    }


# ═════════════════════════════════════════════════════════════════════════
# A FRONTEIRA FORWARD DO RAW — quem leva o que a porta sabe até ao rastro
# ═════════════════════════════════════════════════════════════════════════
# Esta peça é para o RAW o que `coleta/derivacao_forward.py` é para o DERIVED:
# ela não escreve SQL, não é dona da observação e não é dona do rastro. Ela
# traduz o recibo de `preservar()` para a língua de `rastro_da_coleta`.
#
#     COLETOR OBSERVA · PORTA PRESERVA · RASTRO CONTA
#
# ⚠️ E ELA FALA DEPOIS, NUNCA ANTES.
# O `RAW_OBSERVATION_ID` só existe porque o banco devolveu uma linha. Emitir a
# passagem antes do INSERT daria um sucesso sem sujeito — e um rastro de
# sucesso que aponta para nada é pior do que rastro nenhum, porque parece
# medido.

GRAO_ENTRADA_RAW = "artefato observado"
GRAO_SAIDA_RAW = "observacao bruta"


def _fonte_provada(para_o_raw):
    """A fonte da passagem, e só quando ela é UMA e está provada.

    ⚠️ ISTO NAO INFERE NADA. Não lê o caminho, não lê o nome da pasta, não lê
    o slug e não lê o sha. Lê o `SOURCE_ID` que o coletor declarou, e só o
    aceita se ele identificar de facto:

        None / "" / "   " / "NAO SEI" / "NAO_SE_APLICA"  →  ausência, e NULL

    ⚠️ `"   "` NAO ESTA EM `NAO_E_AFIRMACAO`, E PASSAVA POR FONTE.
    `preservar_coleta._identifica` já o recusava — «veio vazio, com espaço a
    fingir conteúdo». A fronteira tem de recusar o mesmo, ou a linha do rastro
    fica com uma fonte que o dono do RAW nunca aceitaria.

        DOIS SITIOS COM A MESMA REGRA ESCRITA DE MANEIRAS DIFERENTES
        SAO DUAS REGRAS A ESPERA DE DISCORDAR.

    E se a mesma passagem trouxer DUAS fontes diferentes, também fica NULL:
    escolher uma delas faria a passagem falar por uma fonte que só trouxe
    metade do trabalho.

        UNKNOWN HONESTO > ID INVENTADO.
    """
    fontes = set()
    for a in para_o_raw:
        v = a.get("SOURCE_ID")
        if isinstance(v, str):
            v = v.strip()
        if v in NAO_E_AFIRMACAO:
            continue
        fontes.add(v)
    return fontes.pop() if len(fontes) == 1 else None


def _baldes_do_raw(recibo, recusas_da_porta, entrada):
    """Onde cada item terminou. A conta tem de fechar, e é o banco que confere.

        NAO E OBRIGATORIO QUE 100% CHEGUE AO FIM.
        E OBRIGATORIO QUE 100% TENHA EXPLICACAO.

    ⚠️ A MESMA OBSERVACAO NAO CAI EM DOIS BALDES, E ELA ESTAVA A CAIR.
    `RAW_OBSERVATIONS` são as observações confirmadas DESTA corrida — e num
    reencontro a linha reaproveitada aparece nas duas listas. Somar as duas
    dava `accounted = 2` para uma entrada de 1, e o banco devolvia
    `unaccounted_input = -1`: um buraco NEGATIVO, inventado pela contagem.

        REAPROVEITADA E CONFIRMADA SAO A MESMA LINHA VISTA DE DOIS LADOS.

    `unknown` não é enchimento: é o resto medido — o que entrou, não foi
    recusado e não apareceu confirmado no banco. Chamar-lhe `passed` faria a
    perda diluir-se num número de sucesso.
    """
    confirmadas = len(recibo.get("RAW_OBSERVATIONS") or [])
    reaproveitadas = (recibo.get("JA_EXISTIA_NO_BANCO") or {}).get(
        "REUSED_METADATA") or 0
    reaproveitadas = min(reaproveitadas, confirmadas)
    recusadas = recusas_da_porta + len(recibo.get("RECUSADOS_SEM_IDENTIDADE") or [])
    novas = confirmadas - reaproveitadas
    resto = entrada - novas - reaproveitadas - recusadas
    return {"passed": novas, "reused": reaproveitadas,
            "rejected": recusadas, "unknown": max(resto, 0)}


def _a_observacao_desta_passagem(recibo):
    """O alvo da linha — e só quando ela produziu EXATAMENTE uma.

    Com N > 1 a passagem não tem uma observação: tem N. Escolher a primeira
    seria escolher ao acaso com cara de determinismo, e as contagens já dizem
    a verdade. Com zero, não há sujeito nenhum.

        UM ID EMPRESTADO NAO E UM ID ERRADO. E UMA OBSERVACAO A FAZER-SE
        PASSAR POR OUTRA.
    """
    obs = recibo.get("RAW_OBSERVATIONS") or []
    if len(obs) != 1:
        return None
    return obs[0]["RAW_OBSERVATION_ID"]


def _proxima_tentativa(banco, run_id):
    """A tentativa seguinte desta etapa nesta corrida.

    ⚠️ FIXAR `tentativa=0` FARIA A SEGUNDA PASSAGEM COLIDIR na chave
    `(run_id, etapa, tentativa)` — e o erro do banco subiria com o mesmo tipo
    do erro do fluxo. `rota_forward_documento` já resolveu isto no STRUCTURED,
    e a etapa RAW não tem razão nenhuma para o resolver de outra maneira.

    E a linha anterior FICA. Apagar a tentativa que falhou apagaria a evidência
    daquilo que se está a tentar consertar.
    """
    try:
        r = banco.executa(
            "select coalesce(max(tentativa), -1) from public.etapa_da_corrida"
            " where run_id = %s and etapa = 'RAW'" % rastro._lit(run_id))
        return int(r[0][0]) + 1
    except Exception:                                        # noqa: BLE001
        return 0


def falar_do_raw(banco, *, recibo, corrida, entrada, recusas_da_porta,
                 source_id=None, route_class_id=None, tentativa=None):
    """A passagem pela etapa RAW, escrita pelo dono canónico do rastro.

    `recibo` é o que `preservar()` devolveu — ou `None`, quando a porta não
    chegou a preservar nada. Os dois casos são diferentes e nenhum é silêncio:

        recibo None   a etapa NAO CORREU  → NOT_RUN
        recibo com    a etapa correu      → PASS / PARTIAL / FAIL

    ⚠️ NOT_RUN != FAIL. Uma etapa que não correu não falhou, e uma etapa que
    falhou correu. Colapsar as duas manda o operador ao sítio errado.
    """
    if tentativa is None:
        tentativa = _proxima_tentativa(banco, corrida["RUN_ID"])

    if recibo is None:
        # Nada a preservar: nenhum artefato sobreviveu ao contrato da porta.
        # A etapa não correu, e dizê-lo é a única coisa honesta a dizer.
        return rastro.registrar(
            banco, run_id=corrida["RUN_ID"], etapa="RAW", estado="NOT_RUN",
            tentativa=tentativa, source_id=source_id,
            route_class_id=route_class_id,
            input_grain=GRAO_ENTRADA_RAW, input_count=entrada,
            output_grain=GRAO_SAIDA_RAW, output_count=0,
            cardinalidade="1:1",
            rejected=recusas_da_porta,
            not_run=max(entrada - recusas_da_porta, 0))

    baldes = _baldes_do_raw(recibo, recusas_da_porta, entrada)
    confirmadas = baldes["passed"]
    pendencia = recibo.get("PENDENCIA")
    erro = (recibo.get("MEMORIA") or {}).get("ERRO")
    # ⚠️ RECUSAR NAO E FALHAR, E A ETAPA NAO ASSINA O DEFEITO DO ITEM.
    # `rota_forward_documento` já decidiu isto no STRUCTURED: um item que não
    # cumpre a pré-condição da cadeia sai `rejected` com a etapa em PASS —
    # «NAO e erro nosso: e o item». Uma colheita inteira sem fonte provada é
    # uma colheita recusada, e não uma etapa avariada. Marcá-la FAIL mandava
    # o operador consertar o coletor de bruto em vez do coletor da fonte.
    tentadas = entrada - baldes["rejected"]
    if erro or (tentadas > 0 and confirmadas + baldes["reused"] == 0):
        estado, canonico = "FAIL", "UNKNOWN_ERROR"
    elif tentadas == 0:
        estado, canonico = "PASS", None
    elif pendencia == "PRESERVED_AND_REGISTERED" and not baldes["unknown"]:
        estado, canonico = "PASS", None
    else:
        estado, canonico = "PARTIAL", "ITEM_ERROR"

    return rastro.registrar(
        banco, run_id=corrida["RUN_ID"], etapa="RAW", estado=estado,
        tentativa=tentativa, source_id=source_id,
        route_class_id=route_class_id,
        input_grain=GRAO_ENTRADA_RAW, input_count=entrada,
        output_grain=GRAO_SAIDA_RAW,
        # As observações que esta passagem deixou de pé: as novas mais as
        # reaproveitadas. NÃO se soma `confirmadas` outra vez — ela já é a
        # soma das duas.
        output_count=baldes["passed"] + baldes["reused"],
        cardinalidade="1:1",
        passed=baldes["passed"], rejected=baldes["rejected"],
        unknown=baldes["unknown"], reused=baldes["reused"],
        canonical_state=canonico,
        diagnostic_code=(dg.RAW_PERSISTENCE_FAILED if estado == "FAIL" else None),
        error_message=erro if estado == "FAIL" else None,
        # A OBSERVACAO, quando esta passagem produziu exatamente uma.
        raw_asset_id=_a_observacao_desta_passagem(recibo))


def receber(itens: list, *, corrida: dict, armazem, memoria=None,
            raiz: str = RAIZ, banco_do_rastro=None) -> dict:
    """A porta. Devolve o que entrou, o que foi recusado, e o recibo do RAW.

    NAO levanta por item mau: um item que quebra o contrato e uma RECUSA com
    nome, e a corrida continua. Rebentar aqui faria uma observacao estragada
    apagar todas as outras da mesma colheita.

    `banco_do_rastro` e onde a passagem pela etapa RAW e escrita, ou `None`
    para nao emitir — a mesma forma que `derivacao_forward.correr()` usa.
    Sem banco nao ha rastro, e nao se fabrica um ficheiro ao lado para o
    substituir: AUSENCIA DE RASTRO E AUSENCIA, e ela diz-se com `NAO_EMITIDO`.
    """
    if not corrida.get("RUN_ID"):
        # Sem corrida nao ha procedencia, e sem procedencia nao ha RAW
        # canonico. O dono do RAW recusa isto de qualquer maneira; recusar aqui
        # da o nome antes de gastar o resto.
        return {"ACEITES": [], "RECUSAS": [{"PORQUE": SEM_CORRIDA,
                                            "DETALHE": "corrida sem RUN_ID"}],
                "RAW": None}

    aceites, recusas, bytes_por_caminho, para_o_raw = [], [], {}, []
    para_a_porta_ = []
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
        para_a_porta_.append(unidade_para_a_porta(item, f))
        para_o_raw.append(para_o_dono_do_raw(f, item))

    recibo = None
    if para_o_raw:
        recibo = preservar(_corrida_completa(corrida), para_o_raw, armazem,
                           lambda o: bytes_por_caminho[o["SHA256"]],
                           memoria=memoria)
    # ── A PASSAGEM, DEPOIS DE A OBSERVACAO EXISTIR ──────────────────────
    # ⚠️ A ORDEM E A PROVA. `preservar()` ja correu, ja leu de volta e ja
    # devolveu os ids REAIS. So agora a etapa tem o que contar. Trocar estas
    # duas linhas de sitio escreveria um sucesso antes de haver sujeito.
    #
    # A excecao do rastro SOBE, e nao e apanhada aqui. Ha divida declarada
    # sobre isso (`G-TEL-01`), e esta missao nao lhe inventa politica nova:
    # inventar uma politica calada faria uma falha de telemetria passar por
    # falha de RAW — e elas nao sao a mesma coisa.
    trilho = "NAO_EMITIDO"
    if banco_do_rastro is not None:
        trilho = falar_do_raw(
            banco_do_rastro, recibo=recibo, corrida=corrida,
            entrada=len(itens), recusas_da_porta=len(recusas),
            source_id=_fonte_provada(para_o_raw))

    # `PARA_A_PORTA` sao os MESMOS aceites, com o conteudo intacto e o estagio
    # preservado. Nao e um terceiro objecto: e a unidade aceite, na lingua de
    # quem a vai julgar. Quem foi recusado nao aparece aqui.
    return {"ACEITES": aceites, "RECUSAS": recusas, "RAW": recibo,
            "RASTRO": trilho, "PARA_A_PORTA": para_a_porta_}
