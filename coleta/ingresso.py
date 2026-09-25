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
import uuid

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import artefato as art                                    # noqa: E402
# ⚠️ `PASSAGEM` E `PASSAGENS` SAO DO DONO DO RAW, E NAO SE REDECLARAM AQUI.
# A alca da passagem e um contrato entre esta porta e `preservar()`. Escrever
# a string outra vez deste lado daria dois donos ao mesmo nome, e no dia em que
# um deles mudasse a ligacao partia-se em silencio — que e a pior maneira de
# uma linhagem se perder.
from guarda.preservar_coleta import (ArmazemLocal, PASSAGEM,  # noqa: E402
                                     PASSAGENS, preservar,
                                     ArmazemOperacionalSemRaiz, ArmazemProtegido,
                                     apagar_armazem_de_medicao, raiz_do_armazem_local)
# ⚠️ O DONO DO RASTRO, E NAO UMA SEGUNDA TELEMETRIA.
# `medidas/rastro_da_coleta.py` ja escreve as passagens de DERIVED, STRUCTURED
# e ADMISSION. A etapa RAW estava no vocabulario (`telemetria.ETAPAS_DA_COLETA`)
# e era muda. Esta porta passa a contar-lhe a passagem na MESMA lingua.
import rastro_da_coleta as rastro                           # noqa: E402
import diagnostico as dg                                    # noqa: E402
# ⚠️ O DONO DA ESPECIE DO TEXTO, E NAO UMA SEGUNDA COPIA DELA.
# `regras/proveniencia.py` ja governa a procedencia de um texto derivado
# (`ESPECIES_DO_TEXTO`, desde a C6). A porta NAO redeclara o vocabulario nem a
# regra de escolha: importa-os. Duas listas para o mesmo vocabulario divergem no
# dia em que alguem acrescentar uma especie a uma delas.
import proveniencia as pv                                   # noqa: E402

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
NAO_SEI_ID = "NAO SEI"

# ⚠️ `COLLECTED_AT` ENTROU AQUI, E A AUSENCIA DELE ERA UM DEFEITO CALADO.
# Esta tupla tinha treze campos e nenhum deles servia para o coletor dizer
# QUANDO ele trouxe os bytes. A ficha enchia esse campo com o `STARTED_AT` da
# CORRIDA, e enquanto a corrida que colhe e a corrida que preserva forem a
# mesma, os dois valores coincidem e ninguem repara.
#
# Deixam de coincidir no reprocessamento — que e exactamente o que esta missao
# faz. Medido: dez observacoes italianas capturadas a 2026-09-07, reprocessadas
# a 2026-09-14, chegaram a Sala de Espera com
#
#     captured_at = 2026-09-14  —  uma semana errado, e com ar de medido
#
# O livro italiano SEMPRE soube a resposta certa: cada observacao traz
# `CAPTURED_AT` com o instante real. O coletor sabia, e nao tinha por onde o
# dizer.
#
#     RUNTIME SABE != O SISTEMA GUARDA.
#     E UM CAMPO SEM SITIO NO CONTRATO E UM CAMPO QUE NAO EXISTE.
#
# A corrida continua a ser o valor por omissao — para quem nao declara, nada
# muda. O que muda e haver um sitio para a verdade quando ela e sabida.
DO_COLETOR = ("SOURCE_ID", "SOURCE_URL", "PUBLISHER", "COUNTRY_SCOPE",
              "SOURCE_LOCATION", "FACT_LOCATION", "ITEM_LANGUAGE",
              "FACT_TIME", "PUBLISHED_AT", "OBSERVED_AT", "COLLECTED_AT",
              "EXECUTOR_ID", "EXECUTOR_VERSION", "PIPELINE_VERSION",
              # ⚠️ `CONTENT_TYPE` ENTROU, E NAO E «MAIS UM CAMPO A VIAJAR».
              # A regra escrita a seguir continua a valer: um campo nao entra
              # aqui por precisar de boleia. Este entra porque e METADADO DA
              # FICHA — `Artefato` sempre teve a coluna — e porque a ficha
              # nascia com ela VAZIA enquanto o coletor a trazia preenchida.
              #
              # Medido a 2026-09-14 com um `.mp4` real de 9,2 MB: o item
              # declarava `video/mp4`, a ficha saia `NAO SEI`, e
              # `_quem_deriva_aceita` trata a ausencia como «tenta» — de
              # proposito, porque ausencia de evidencia nao e evidencia de
              # ausencia. Logo o video seguia para o extrator de PDF.
              #
              #     UMA TRAVA DE ESPECIE COM A ESPECIE APAGADA A MONTANTE
              #     NAO PROTEGE NADA: ELA SO NAO TEM O QUE LER.
              "CONTENT_TYPE")

# ⚠️ `TEXT_UNITS` NAO ESTA NA LISTA ACIMA, E A AUSENCIA E A DECISAO.
# Medido ao ligar: por-lo la levanta
# `Artefato.__init__() got an unexpected keyword argument 'TEXT_UNITS'` — e o
# erro tem razao. `DO_COLETOR` nao e «o que a porta transporta»: e o que entra
# na FICHA do contrato comum, e a ficha e metadado do artefato, nao conteudo
# dele. Este ficheiro ja o dizia, na linha a seguir:
#
#     «O item manda no conteudo — `texto` vive nele e nao na ficha.»
#
# A evidencia textual e conteudo. Ela atravessa porque `para_a_porta` deixa
# passar intacto tudo o que nao esta no mapa de nomes — a mesma regra que ja
# leva o `DOCUMENT_ID`, que tambem nao tem par do outro lado. E os bytes dela
# ficam preservados no RAW porque `_bytes_do_item` serializa o ITEM inteiro.
#
#     ACRESCENTAR UM CAMPO A UMA LISTA PORQUE ELE PRECISA DE VIAJAR
#     E CONFUNDIR «POR ONDE PASSA» COM «DE QUEM E».


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
# ═══════════════════════════════════════════════════════════════════════════
# A FRONTEIRA STRUCTURED → ADMISSION, DECLARADA
# ═══════════════════════════════════════════════════════════════════════════
# ⚠️ PORQUE ISTO NASCE AQUI, E NAO NUM FICHEIRO NOVO.
#
# A prova de fogo da Collection procurou, no repositorio inteiro, o contrato do
# registo STRUCTURED. Nao existe esquema nenhum, e a porta le chaves por
# tentativa e erro. O dano ficou medido no mesmo dia: o produtor escreveu
# `collected_time`, a porta leu `captured_at`, e SEIS unidades chegaram a Sala
# de Espera com `CAPTURED_AT = NAO SEI` — com o valor a existir e medido.
#
#     PRODUTOR E CONSUMIDOR SEM CONTRATO PARTILHADO
#     PERDEM DADO SEM DAR ERRO.
#
# O remendo obvio — aceitar tambem `collected_time` — seria o pior conserto
# possivel: cada nome novo que alguem inventasse passaria a ser suportado, e a
# fronteira deixaria de ter forma nenhuma.
#
#     ACEITAR MAIS NOMES NAO E TER UM CONTRATO. E DESISTIR DE TER UM.
#
# E nao se cria uma segunda arquitectura. Os DOIS donos ja existiam:
#
#     leis/artefato.py       o VOCABULARIO — cinco tempos, tres geografias,
#                            duas especies, e as proibicoes em codigo
#     coleta/ingresso.py     a TRAVESSIA — `PARA_A_PORTA`, o unico tradutor
#                            da fronteira, ja usado pelas tres rotas
#
# O que faltava nao era um dono: era a DECLARACAO de o que tem de atravessar.
# `PARA_A_PORTA` diz como um nome vira outro; nao dizia quais fazem falta, e
# por isso ninguem reparava quando um deles nao vinha.
#
#     UM MAPA DE NOMES NAO E UM CONTRATO: DIZ COMO TRADUZIR, NAO O QUE EXIGIR.
#
# ⚠️ E ISTO NAO PREENCHE NADA. `conferir_fronteira()` MEDE e escreve o que
# falta. Ausencia continua `NAO SEI`, e `NAO SEI` continua a nao ser `NAO`.

#: O que a unidade STRUCTURED tem de trazer para a admissao poder julgar. São
#: os nomes do CONTRATO COMUM (`leis/artefato.py`), porque é essa a língua em
#: que a unidade chega — `para_a_porta()` é que a traduz para a da porta.
FRONTEIRA_EXIGE = ("SOURCE_ID", "ARTIFACT_TYPE")

#: O que a fronteira TRANSPORTA quando existe, e que nunca se fabrica quando
#: não existe. Cada um é um facto diferente, e o mapa diz de que espécie é —
#: para que ninguém volte a encher um com o outro.
FRONTEIRA_TRANSPORTA = {
    "FACT_TIME": "quando o fato aconteceu",
    "PUBLISHED_AT": "quando a fonte publicou — NAO e quando o fato aconteceu",
    "OBSERVED_AT": "quando a fonte registou ter observado",
    "COLLECTED_AT": "quando ESTA maquina recebeu os bytes (raw_asset.captured_at)",
    "SOURCE_LOCATION": "onde esta quem publica",
    "FACT_LOCATION": "onde o fato aconteceu — PODE ser outro",
    "PARENT_SHA256": "a impressao do original de que este texto nasceu",
    # ⚠️ COMO SE SABE FAZ PARTE DO QUE SE SABE, e ate aqui nao atravessava.
    # `leis/artefato.py::conferir` JA reprova um `FACT_LOCATION` preenchido
    # «sem dizer de onde saiu» — a lei existia, e a fronteira nao declarava a
    # resposta como coisa que viaja. E do outro lado da moeda: o livro do
    # coletor italiano escreve, em 175 observacoes, PORQUE o tempo do fato e
    # desconhecido. Essa frase e uma MEDICAO, e morria aqui.
    #
    #     UM `NAO SEI` COM RAZAO E UMA MEDICAO.
    #     UM `NAO SEI` SEM RAZAO E INDISTINGUIVEL DE DESLEIXO.
    "FACT_TIME_BASIS": "como se sabe o FACT_TIME, ou porque NAO se sabe",
    "FACT_LOCATION_BASIS": "como se sabe o FACT_LOCATION, ou porque NAO se sabe",
    # TEMPO-E-LUGAR (25/09): os outros dois valores tambem tem de dizer de
    # onde vieram. A data de publicacao pode vir de um JSON-LD, de uma meta
    # tag ou da edicao impressa — sao bases diferentes, e so a base as separa.
    "PUBLISHED_AT_BASIS": "como se sabe o PUBLISHED_AT, ou porque NAO se sabe",
    "SOURCE_LOCATION_BASIS": "como se sabe o SOURCE_LOCATION, ou porque NAO se sabe",
    # A especie probatoria que o CONTRATO DE FONTE declara antes de correr.
    # DECLARADO PELA FONTE != MEDIDO NESTE DOCUMENTO, e o nome diz qual e qual.
    "SOURCE_DECLARED_EVIDENCE_CLASS":
        "a especie probatoria que o contrato de fonte declara — nao a medida aqui",
}

#: A linhagem. Não está em `FRONTEIRA_EXIGE` porque a rota documental a põe no
#: item já na língua da porta (`raw_asset_id`), e não como nome do contrato
#: comum. `admissao.pronto_para_inteligencia()` é quem a lê, e é lá que a
#: ausência vira `NAO SEI` — nunca um id fabricado.
FRONTEIRA_LINHAGEM = "raw_asset_id"

#: Os quatro tempos, escritos juntos uma vez, para que a proibição seja legível
#: no sítio onde ela pode ser quebrada.
TEMPOS_QUE_NAO_SE_MISTURAM = (
    "FACT_TIME != PUBLISHED_AT != OBSERVED_AT != COLLECTED_AT != DERIVED_AT")


def conferir_fronteira(item: dict) -> dict:
    """O que atravessou esta fronteira, e o que NAO atravessou. Nao preenche.

    Devolve o recibo da travessia — nunca levanta, nunca escreve, nunca
    adivinha. Quem chama decide o que fazer com um `EXIGIDOS_EM_FALTA` não
    vazio; esta função só se recusa a deixar a perda ser silenciosa.

        UMA PERDA MEDIDA E UM DEFEITO. UMA PERDA CALADA E UMA ARQUITECTURA.

    Aceita o item em QUALQUER das duas línguas — a do contrato comum e a da
    porta — porque a fronteira é exactamente o sítio onde as duas se encontram,
    e um recibo que só soubesse ler uma delas mediria metade da travessia.
    """
    def _tem(nome):
        for chave in (nome, PARA_A_PORTA.get(nome, nome)):
            v = item.get(chave)
            if v not in NAO_E_AFIRMACAO:
                return True
        return False

    faltam = [c for c in FRONTEIRA_EXIGE if not _tem(c)]
    return {
        "FRONTEIRA": "STRUCTURED -> ADMISSION",
        "DONO": "coleta/ingresso.py",
        "VOCABULARIO": "leis/artefato.py",
        "EXIGIDOS": list(FRONTEIRA_EXIGE),
        "EXIGIDOS_EM_FALTA": faltam,
        "TRANSPORTADOS": sorted(c for c in FRONTEIRA_TRANSPORTA if _tem(c)),
        "AUSENTES": sorted(c for c in FRONTEIRA_TRANSPORTA if not _tem(c)),
        "LINHAGEM": ("PRESENTE" if item.get(FRONTEIRA_LINHAGEM) is not None
                     else "NAO SEI"),
        "A_LEI": TEMPOS_QUE_NAO_SE_MISTURAM,
        "O_QUE_ISTO_NAO_FAZ": ("nao preenche, nao adivinha e nao converte um "
                               "tempo no outro. Ausencia sai como ausencia."),
    }


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
    # ── OS QUATRO QUE `FRONTEIRA_TRANSPORTA` DECLARAVA E O MAPA NAO TRADUZIA ──
    # Um nome declarado como «coisa que atravessa» e sem par do outro lado
    # atravessa na lingua errada: chega a porta em MAIUSCULAS, a porta le
    # minusculas, e o valor fica no item a ser lido por ninguem.
    #
    #     DECLARAR QUE ATRAVESSA != TER POR ONDE ATRAVESSAR.
    "OBSERVED_AT": "observed_at",
    "FACT_TIME_BASIS": "fact_time_basis",
    "FACT_LOCATION_BASIS": "fact_location_basis",
    "SOURCE_DECLARED_EVIDENCE_CLASS": "source_declared_evidence_class",
    # ── D61/D63 (SOC-TEMPO): a base e a precisao da PUBLICACAO e do LUGAR DA FONTE ──
    # Sem elas, `leis/fato_do_texto.py` nao distingue uma publicacao provada de uma
    # data qualquer, e «ieri» nao se pode contar. Atravessam para quem julga; a Sala
    # ainda nao tem colunas para elas (ver o plano SOC-TEMPO: um dono so para a migracao).
    "PUBLISHED_AT_BASIS": "published_at_basis",
    "PUBLISHED_AT_PRECISION": "published_at_precision",
    "SOURCE_LOCATION_BASIS": "source_location_basis",
    "SOURCE_LOCATION_PRECISION": "source_location_precision",
    # DA-7: a evidencia da leitura do tempo e do lugar (033).
    "TEMPO_LUGAR_EVIDENCIA": "tempo_lugar_evidencia",
}

# ── TEMPO E LUGAR: O QUE A OBSERVACAO SABE, E TEM DE CHEGAR A PORTA ─────────
# ⚠️ TEMPO-E-LUGAR (25/09). Medido na Sala real: 78 de 78 com os cinco campos
# em `NAO SEI`. Nenhum sitio escrevia a constante — o valor MORRIA no caminho:
# a rota documental leva a observacao ate `raw_asset` e dai ao texto derivado,
# e nenhuma das tres paragens (`unidades_para_a_derivacao`,
# `derivacao_forward`, `orquestrador.pela_estruturacao`) o levava.
#
#     UM RECADO PASSADO DE MAO EM MAO QUE NINGUEM REPETE.
#
# Esta lista e o recado, na lingua do contrato comum. Viaja com a unidade
# desde a porta (onde o item original ainda esta em mao) ate
# `orquestrador.item_documental_para_a_porta`, e so `para_a_porta` o traduz.
# Cada valor vai com a sua base; o que nao se prova nao vai.
TEMPO_E_LUGAR = ("FACT_TIME", "FACT_TIME_BASIS",
                 "PUBLISHED_AT", "PUBLISHED_AT_BASIS",
                 "OBSERVED_AT",
                 "SOURCE_LOCATION", "SOURCE_LOCATION_BASIS",
                 "FACT_LOCATION", "FACT_LOCATION_BASIS") + (
    # D62 / DA-9: a precisao e a segunda fonte da publicacao. NAO sao nomes da
    # porta: `orquestrador.item_documental_para_a_porta` dobra-os para dentro
    # de `TEMPO_LUGAR_EVIDENCIA` (033).
    "PUBLISHED_AT_PRECISION", "SOURCE_LOCATION_PRECISION",
    "PUBLISHED_AT_OUTRA", "PUBLISHED_AT_OUTRA_BASIS", "PUBLISHED_AT_CONFLITO")
#: Os do recado que viajam para a evidencia, e nao como campo proprio.
TEMPO_E_LUGAR_PARA_A_EVIDENCIA = TEMPO_E_LUGAR[9:]


class TextoEmConflito(ValueError):
    """O item traz unidades de texto E um `texto` a mao que as contradiz.

    NAO SE ESCOLHE EM SILENCIO, pela mesma razao de `AliasEmConflito`. E aqui a
    escolha calada seria pior do que um alias trocado: um `texto` escrito a mao
    ao lado de `TEXT_UNITS` e exactamente a forma que o contrato novo tem de ser
    ignorado sem que nada reclame — o campo antigo continua a responder, a
    especie fica no campo novo a ser lida por ninguem, e as duas coisas divergem
    a partir do dia em que uma delas mudar.

        UM CONTRATO QUE O CAMINHO ANTIGO CONSEGUE CONTORNAR NAO E UM CONTRATO.
    """


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

    # ── O TEXTO ATRAVESSA AQUI, PELA MESMA RAZAO QUE OS OUTROS DEZ ─────────
    # ⚠️ NAO EM `unidade_para_a_porta`, e a diferenca nao e de arrumacao.
    # A rota documental (`orquestrador.item_documental_para_a_porta`) chama ESTA
    # funcao e nunca passa por aquela. Se a escolha vivesse la, o documento
    # estruturado ficava sem especie e a rota social ficava com ela — duas rotas
    # a entregar a mesma porta coisas diferentes, que e o defeito que
    # `PARA_A_PORTA` veio curar para os dez nomes do contrato comum.
    #
    #     UMA TRAVESSIA, UM TRADUTOR, NA FRONTEIRA. O TEXTO NAO E EXCEPCAO.
    unidades = fora.get(pv.CAMPO_DAS_UNIDADES)
    if unidades:
        escolha = pv.texto_para_quem_julga(unidades)
        # ⚠️ ABSENCIA CONTINUA ABSENCIA. `texto_para_quem_julga` devolve `{}`
        # quando nao ha texto legivel, e nao `{"texto": ""}`. Uma observacao com
        # unidades vazias chega a porta SEM `texto`, para ela responder «nao
        # consegui ver» — e nao «vi, e estava vazio».
        antigo = fora.get("texto")
        if (antigo is not None and str(antigo).strip()
                and str(antigo) != str(escolha.get("texto"))):
            raise TextoEmConflito(
                "o item traz %s e tambem um «texto» escrito a mao que nao e o "
                "que a regra canonica escolheu. Um deles esta errado, e escolher "
                "em silencio faria a especie de um viajar colada ao valor do "
                "outro. Declarado: %r. Escolhido: %r (%s)."
                % (pv.CAMPO_DAS_UNIDADES, str(antigo)[:120],
                   str(escolha.get("texto"))[:120],
                   escolha.get("texto_escolha_porque")))
        fora.update(escolha)

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
# ── O QUE A PORTA PROVOU VIAJA COM O ITEM ───────────────────────────────
# Os tres primeiros ja ca estavam. Os quatro seguintes vieram do SCRAP, que
# tinha razao na intencao e criava um segundo balde para a cumprir: ele
# devolvia uma lista `ENTRADOS` com o item mais um carimbo `INGRESSO`, e o
# orquestrador julgava ESSA lista.
#
#     UMA SEGUNDA LISTA PARA A ADMISSAO E UMA SEGUNDA PORTA DA COLLECTION.
#
# Duas listas a chegar a quem julga significam duas travessias, e so uma
# delas passa pelo tradutor do texto — a observacao do SCRAP seria julgada
# sem o contrato E7 aplicado. A intencao fica; o segundo balde sai.
#
#     UM ESTAGIO QUE NAO ATRAVESSA A FRONTEIRA NAO ACONTECEU
#     PARA QUEM ESTA DO OUTRO LADO.  (a frase e do SCRAP, e esta certa)
#
# ⚠️ `RAW_OBSERVATION_ID` NAO ENTRA AQUI, e a ausencia continua deliberada.
# Ele e `raw_asset.id`, cunhado pelo banco DEPOIS desta linha: a ficha nao o
# sabe, e o que a ficha nao sabe nao se escreve na ficha.
#
#     RAW_OBSERVATION_ID = raw_asset.id, E MAIS NADA.
#
# ⚠️ O QUE MUDOU EM `C-SCRAP-READY-RAW-LINEAGE-V1` E O DEPOIS, E NAO O AQUI.
# A unidade que sai desta funcao passa a ser a MESMA que, mais abaixo, recebe
# `raw_asset_id` de `_a_observacao_volta_ao_item()` — quando `preservar()`
# responder, e so com o id que ele devolveu. Ate la ela nao o tem, e nao o
# finge ter.
DA_FICHA_PARA_A_PORTA = ("ARTIFACT_TYPE", "PARENT_ARTIFACT_ID", "PARENT_SHA256",
                         "ARTIFACT_ID", "SHA256", "STORAGE_LOCATION", "BYTES")


def unidade_para_a_porta(item: dict, ficha) -> dict:
    """O conteudo original MAIS o que o contrato apurou, na lingua de quem julga.

    O item manda no conteudo — `texto` vive nele e nao na ficha. A ficha manda
    no estagio, porque foi ela que o apurou. Nada e reescrito: um campo que o
    item ja afirma nao e tocado.

    ⚠️ E E AQUI, E SO AQUI, QUE A EVIDENCIA TEXTUAL VIRA O TEXTO QUE SE JULGA.
    A observacao traz N unidades com especie; quem julga le uma. A regra da
    escolha e de `regras/proveniencia.py` — a porta APLICA-A, nao a redefine, e
    nao a aplica duas vezes: se ela vivesse tambem no orquestrador, as duas
    copias divergiam no dia em que alguem mudasse uma.

        UMA TRAVESSIA, UM TRADUTOR, NA FRONTEIRA. Ja era a lei deste ficheiro
        para os dez nomes do contrato comum; passa a valer para o texto.
    """
    fora = dict(item)
    for campo in DA_FICHA_PARA_A_PORTA:
        valor = getattr(ficha, campo, None)
        if valor in NAO_E_AFIRMACAO:
            continue
        fora.setdefault(campo, valor)

    return para_a_porta(fora)


# ── A OBSERVACAO PRESERVADA, NA LINGUA DE QUEM A VAI DERIVAR ───────────────
# ⚠️ ESTA TRADUCAO E A PONTE QUE FALTAVA, E A SUA AUSENCIA ERA O BURACO.
#
# Medido em `provas/o_pedido_atravessa.py`: um pedido real atravessava
# REQUEST -> ORCHESTRATOR -> EXECUTOR -> RUN -> RAW -> STORAGE e parava. Nao
# por falta de CAPACIDADE — `derivacao_forward.correr()` existe, corre, e
# derivava com PASS quando alguem o chamava a mao — mas por falta de LIGACAO:
# ninguem lhe entregava as observacoes daquela corrida.
#
#     CAPABILITY EXISTS != EDGE EXISTS.
#
# E ha uma maneira errada de a construir, que a prova diagnostica usou de
# proposito e que NAO pode atravessar para a producao: procurar um PDF no
# disco por `glob` e emparelha-lo com o primeiro `raw_asset`. Isso prova que a
# ferramenta funciona; nao prova que AQUELA observacao derivou.
#
#     PATH != IDENTITY.
#     O PRIMEIRO FICHEIRO DA PASTA NAO E O FILHO DA PRIMEIRA LINHA.
#
# Por isso o par (observacao, bytes) sai inteiro da LINHAGEM canonica, que ja
# existia e que ninguem percorria:
#
#     raw_asset.id              a identidade da observacao  (RAW_OBSERVATION_ID)
#     raw_asset.storage_object_id -> storage_object.storage_path
#                               o endereco fisico daquele byte
#
# Nenhum dos dois e inventado aqui, e nenhum e derivado do outro.
#: Os executores de derivação cujas capacidades esta porta consulta. Hoje é um;
#: a lista existe para o segundo entrar sem ninguém tocar na regra de cima.
#:
#: O import é LOCAL e protegido: esta porta corre em contextos onde o executor
#: pode não estar importável (uma prova que copia meia árvore, por exemplo), e
#: um `ImportError` aqui faria a coleta parar por causa de uma PERGUNTA sobre
#: capacidade. Sem a declaração, `_quem_deriva_aceita` responde True — que é o
#: comportamento de sempre, e o seguro.
#: Os executores de derivação, por ordem de consulta. A ordem NÃO é prioridade:
#: as espécies não se sobrepõem — `application/pdf` não é `video/*` — e no dia
#: em que se sobrepuserem isso é uma decisão a escrever, não a herdar de quem
#: foi importado primeiro.
#:
#:     UMA ORDEM QUE DECIDE SEM QUE NINGUÉM A TENHA DECIDIDO
#:     É UMA REGRA ESCONDIDA NUM `import`.
#:
#: ⚠️ `executor_texto_de_html` ENTROU AQUI PORQUE DECLARAR NÃO É LIGAR.
#: A ficha `CAPACIDADE` dele podia existir um ano sem que nada mudasse — foi
#: exactamente o que aconteceu ao `SUPPORTS` do executor de PDF, e o próprio
#: ficheiro escreveu o preço. É esta linha que faz a capacidade ser LIDA:
#: `executor_para("text/html")` devolvia `None` antes dela, e devolve o módulo
#: depois. Nada mais mudou nesta porta.
#:
#:     MISSING_ROUTE FECHA-SE NA LISTA DE DONOS, E NÃO NA FICHA DE QUEM SABE.
_DONOS_DA_DERIVACAO = ("executor_texto_de_pdf", "executor_transcricao_midia",
                       "executor_texto_de_html")


def _executores_de_derivacao():
    """Os módulos de derivação importáveis AGORA. → tupla de módulos.

    O import continua LOCAL e protegido, um a um: uma prova que copia meia
    árvore pode ter o de PDF e não ter o de mídia, e faltar um NÃO pode fazer
    a coleta parar por causa de uma PERGUNTA sobre capacidade.

        FERRAMENTA QUE FALTA NÃO É DOCUMENTO QUEBRADO — `COL-LAW-503`.
    """
    import importlib                                           # noqa: PLC0415
    fora = []
    for nome in _DONOS_DA_DERIVACAO:
        try:
            mod = importlib.import_module(nome)
        except Exception:                                      # noqa: BLE001
            continue
        if isinstance(getattr(mod, "CAPACIDADE", None), dict):
            fora.append(mod)
    return tuple(fora)


def _capacidades_de_derivacao():
    return tuple(m.CAPACIDADE for m in _executores_de_derivacao())


def _cabe_na_capacidade(cap, tipo) -> bool:
    """`tipo` (já em minúsculas, sem parâmetros) cabe nesta ficha? → bool.

    Dois eixos, e os dois são DECLARADOS pelo dono da capacidade:

        ACEITA_MEDIA_TYPES   o tipo exacto      `application/pdf`
        ACEITA_FAMILIAS      a família do tipo  `audio` · `video`

    ⚠️ A FAMÍLIA ENTROU PORQUE A LISTA EXACTA NÃO FECHAVA.
    Um tipo só — PDF — cabe numa tupla. Mídia não: `video/mp4`,
    `video/quicktime`, `video/webm`, `audio/mpeg`, `audio/mp4`, `audio/wav`,
    `audio/ogg`, `audio/x-m4a`… e a lista nunca acaba. Escrevê-la aqui
    garantia que, no dia em que chegasse um `audio/flac`, esta casa
    responderia `NÃO SUPORTADO` a uma coisa que o `ffmpeg` abre há anos.

        UMA LISTA QUE PRECISA DE SER COMPLETA PARA ESTAR CERTA
        ESTÁ ERRADA NO DIA SEGUINTE.

    E a família não afrouxa a trava: ela só decide A QUEM PERGUNTAR. Quem
    responde de verdade é o executor, que abre o contentor e mede.
    """
    exactos = tuple(str(a).strip().lower()
                    for a in (cap.get("ACEITA_MEDIA_TYPES") or ()))
    if tipo in exactos:
        return True
    familias = tuple(str(f).strip().lower()
                     for f in (cap.get("ACEITA_FAMILIAS") or ()))
    return bool(familias) and tipo.split("/")[0] in familias


def executor_para(media_type):
    """Quem abre esta espécie? → o módulo do executor, ou `None`.

    ⚠️ ESTA É A PERGUNTA QUE FALTAVA, E A SUA AUSÊNCIA ERA O DEFEITO.
    `_quem_deriva_aceita` respondia «ALGUÉM abre isto?» — um booleano — e com
    ele a porta sabia deixar passar. Mas quem derivava a seguir chamava sempre
    o MESMO executor, escrito à mão em `derivacao_forward`. Enquanto houve um
    executor só, as duas coisas coincidiam por acidente.

        «ALGUÉM ABRE» != «QUEM ABRE».
        UM ÚNICO EXECUTOR FAZ AS DUAS PERGUNTAS PARECEREM A MESMA.

    `None` é resposta legítima e quer dizer «nenhum executor declara esta
    espécie» — nunca «falhou». Quem recebe `None` escreve `NOT_APPLICABLE`.
    """
    if media_type is None or not str(media_type).strip():
        return None
    tipo = str(media_type).split(";")[0].strip().lower()
    if tipo in _SENTINELAS or tipo.upper() in _SENTINELAS:
        return None
    for mod in _executores_de_derivacao():
        if _cabe_na_capacidade(mod.CAPACIDADE, tipo):
            return mod
    return None


DERIVACAO_SEM_BYTES_LOCAIS = "DERIVACAO_SEM_BYTES_LOCAIS"
#: A espécie dos bytes foi DECLARADA, e nenhum executor de derivação a sabe
#: abrir. NÃO é erro, NÃO é recusa e NÃO é ausência: é uma etapa que não se
#: aplica a esta observação.
#:
#:     NOT_APPLICABLE != FAIL. NOT_APPLICABLE != PASS.
DERIVACAO_ESPECIE_NAO_SUPORTADA = "DERIVACAO_ESPECIE_NAO_SUPORTADA"


def _quem_deriva_aceita(media_type) -> bool:
    """A espécie declarada cabe em algum executor de derivação? → True/False.

    A pergunta é feita AO DONO DA CAPACIDADE, e não a uma lista escrita aqui.
    `coleta/executor_texto_de_pdf.py::CAPACIDADE` declara o que sabe abrir; esta
    porta lê essa declaração. Repetir aqui «application/pdf» seria um SEGUNDO
    dono da mesma pergunta, e no dia em que entrasse um executor de áudio os
    dois divergiam em silêncio.

        ONE CONCEPT -> ONE OWNER. QUEM SABE ABRIR É QUEM DIZ O QUE ABRE.

    ⚠️ AUSÊNCIA NÃO É RECUSA, e a diferença decide o comportamento:

        espécie DECLARADA e suportada      -> deriva
        espécie DECLARADA e não suportada  -> não deriva, e diz-se porquê
        espécie NÃO DECLARADA              -> deriva, como sempre derivou

    O terceiro caso é o que impede esta função de encolher a coleta por
    silêncio. Sem `media_type` na linha, esta casa não sabe o que são aqueles
    bytes — e «não sei» nunca autoriza a concluir «não serve». Tenta-se, e o
    executor responde honestamente o que encontrou.

        AUSÊNCIA DE EVIDÊNCIA NÃO É EVIDÊNCIA DE AUSÊNCIA.
    """
    if media_type is None or not str(media_type).strip():
        return True
    tipo = str(media_type).split(";")[0].strip().lower()
    if tipo in _SENTINELAS or tipo.upper() in _SENTINELAS:
        return True
    for cap in _capacidades_de_derivacao():
        if _cabe_na_capacidade(cap, tipo):
            return True
    return False


def tempo_e_lugar_por_observacao(recibo, item_por_passagem) -> dict:
    """`{RAW_OBSERVATION_ID: {campo de TEMPO_E_LUGAR: valor}}`.

    O item original so esta em mao aqui, na porta. Liga-se a observacao pela
    mesma alca que `_a_observacao_volta_ao_item` usa — sem procurar por sha,
    caminho ou posicao.

    ⚠️ N passagens da MESMA observacao que discordam num campo nao escolhem:
    o campo sai ausente (a porta escreve `NAO SEI`). Escolher a primeira seria
    escolher ao acaso com cara de determinismo.
    """
    fora = {}
    for o in (recibo or {}).get("RAW_OBSERVATIONS") or []:
        ident = o.get("RAW_OBSERVATION_ID")
        if ident is None:
            continue
        vistos = []
        for alca in (o.get(PASSAGENS) or []):
            item = item_por_passagem.get(alca)
            if item is not None:
                vistos.append({k: item[k] for k in TEMPO_E_LUGAR
                               if item.get(k) not in NAO_E_AFIRMACAO})
        if not vistos:
            continue
        juntos = {}
        for k in TEMPO_E_LUGAR:
            valores = {json.dumps(v.get(k), sort_keys=True) for v in vistos}
            if len(valores) == 1 and vistos[0].get(k) is not None:
                juntos[k] = vistos[0][k]
        fora[ident] = juntos
    return fora


def unidades_para_a_derivacao(recibo, armazem, tempo_e_lugar=None) -> tuple:
    """As observacoes DESTA passagem, com o endereco dos bytes delas.

    Devolve `(unidades, sem_bytes)`. Uma unidade e o que
    `derivacao_forward.correr()` pede, e nada mais:

        {"RAW_ASSET_ID": <int, o id real no banco>, "PDF": <caminho absoluto>}

    ⚠️ SO ENTRA QUEM O BANCO CONFIRMOU. `RAW_OBSERVATIONS` sao as linhas que
    `preservar()` leu DE VOLTA depois de escrever, e so as desta corrida — a
    lista ja nasce filtrada pelo dono dela. Quem foi recusado na porta nunca
    chegou a `raw_asset` e por isso nao pode aparecer aqui:

        RECUSA NA PORTA -> NAO HA OBSERVACAO -> NAO HA O QUE DERIVAR.

    ⚠️ E QUEM NAO TEM BYTES ALCANCAVEIS NAO VIRA UNIDADE, e tambem nao
    desaparece: sai em `sem_bytes`, com o endereco que nao respondeu. Fabricar
    um caminho para a lista ficar completa seria entregar ao executor um
    ficheiro que nao existe e chamar ERROR ao que foi invencao nossa.

        AUSENCIA DE BYTES E AUSENCIA. ELA DIZ-SE, NAO SE PREENCHE.
    """
    unidades, sem_bytes = [], []
    for o in (recibo or {}).get("RAW_OBSERVATIONS") or []:
        caminho = o.get("STORAGE_PATH")
        local = armazem.caminho_local(caminho) if caminho else None
        if not local:
            sem_bytes.append({"RAW_ASSET_ID": o.get("RAW_OBSERVATION_ID"),
                              "STORAGE_PATH": caminho,
                              "PORQUE": DERIVACAO_SEM_BYTES_LOCAIS})
            continue
        # ── E A SEGUNDA PERGUNTA, QUE FALTAVA ───────────────────────────
        # Ter os bytes não é saber o que eles são. Uma observação social — um
        # JSON cujo texto já vem declarado no envelope — tem bytes perfeitamente
        # alcançáveis e NADA que um extrator de PDF possa fazer com eles.
        #
        # Medido antes desta linha existir: a etapa DERIVED saía `FAIL` com
        # `EXTRACTION_ERROR` em TODA corrida do SCRAP, porque a ferramenta certa
        # era chamada para o trabalho errado.
        #
        #     UMA FERRAMENTA QUE RECEBE O QUE NÃO SABE ABRIR NÃO FALHOU:
        #     FOI CHAMADA PARA O TRABALHO ERRADO.
        #
        # E a saída dela NÃO é `FAIL`: é uma etapa que não se aplica a esta
        # observação. `NOT_APPLICABLE` já existe no vocabulário canónico
        # (`leis/telemetria.py::ESTADOS_DE_ETAPA`), e `ETAPA_ACONTECEU` já o
        # exclui — não se inventa estado nenhum aqui.
        if not _quem_deriva_aceita(o.get("MEDIA_TYPE")):
            sem_bytes.append({"RAW_ASSET_ID": o.get("RAW_OBSERVATION_ID"),
                              "STORAGE_PATH": caminho,
                              "MEDIA_TYPE": o.get("MEDIA_TYPE"),
                              "PORQUE": DERIVACAO_ESPECIE_NAO_SUPORTADA})
            continue
        # ⚠️ `CAPTURED_AT` VIAJA COM A UNIDADE, E NAO SE MEDE OUTRA VEZ.
        # Ele e `raw_asset.captured_at` — o instante em que ESTA maquina
        # recebeu os bytes, escrito pelo dono do RAW. Medi-lo de novo aqui
        # daria a hora em que a DERIVACAO comecou, que e outro facto:
        #
        #     COLLECTED_AT != DERIVED_AT.
        #
        # Sem ele, a rota documental chegava a admissao sem saber quando o
        # documento foi colhido, e a Sala recebia `CAPTURED_AT = NAO SEI` com
        # o valor guardado tres degraus atras. Ausente continua ausente: uma
        # linha sem `captured_at` poe `None` aqui, e ninguem o enche.
        # ⚠️ `MEDIA_TYPE` VIAJA COM A UNIDADE, E SEM ELE A ESCOLHA NÃO ACONTECE.
        # A porta acima já leu a espécie para decidir se ALGUÉM a abre. Se ela
        # não a puser na unidade, quem deriva a seguir tem de a adivinhar — e a
        # única coisa que lá chega é um caminho de ficheiro, que é a extensão
        # outra vez.
        #
        #     DEIXAR A ESPÉCIE PARA TRÁS NA PORTA OBRIGA A DEDUZI-LA DEPOIS,
        #     E A DEDUÇÃO DEPOIS É A EXTENSÃO A VOLTAR PELA JANELA.
        unidades.append({"RAW_ASSET_ID": o["RAW_OBSERVATION_ID"],
                         "CAPTURED_AT": o.get("CAPTURED_AT"),
                         "MEDIA_TYPE": o.get("MEDIA_TYPE"),
                         # A fonte DESTA observacao. Nao e a da corrida: uma
                         # corrida pode ter colhido sete fontes, e entao ela
                         # nao tem nenhuma.
                         "SOURCE_ID": o.get("SOURCE_ID"),
                         # V1A: o endereco da observacao, ate a porta (V1).
                         "SOURCE_URL": o.get("SOURCE_URL"),
                         # TEMPO-E-LUGAR: o recado da observacao, com as bases.
                         "TEMPO_E_LUGAR": dict((tempo_e_lugar or {}).get(
                             o["RAW_OBSERVATION_ID"]) or {}),
                         "PDF": local})
    return unidades, sem_bytes


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
    # ⚠️ O QUE O COLETOR DECLAROU VENCE O VALOR POR OMISSAO DA CORRIDA.
    # `COLLECTED_AT` vem primeiro com a hora da corrida e so depois e
    # sobreposto pelo que o coletor disse — nunca ao contrario. A corrida sabe
    # quando ELA comecou; so o coletor sabe quando os BYTES chegaram, e num
    # reprocessamento essas duas datas estao a uma semana de distancia.
    comum = dict(RUN_ID=corrida.get("RUN_ID", art.NAO_SEI),
                 COLLECTED_AT=corrida.get("STARTED_AT") or art.agora())
    comum.update(declarados)
    # ⚠️ AS BASES VAO PARA AS NOTAS DA FICHA, que e onde `art.conferir` as le.
    # Sem isto, um `FACT_LOCATION` provado chegava a ficha sem a base e a
    # porta recusava o item inteiro por «preenchido sem dizer de onde saiu».
    notas = {k: item[k] for k in ("FACT_TIME_BASIS", "FACT_LOCATION_BASIS")
             if item.get(k)}
    if notas:
        comum["NOTES"] = notas

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


class LigacaoAmbigua(Exception):
    """Uma alça reclamada por DUAS observações confirmadas.

        UM ITEM TEM UMA OBSERVAÇÃO. DUAS NÃO É «QUASE UMA»: É NENHUMA.

    Isto não pode acontecer — `planear()` visita cada artefato uma vez, e a
    alça é única por passagem — e é exactamente por isso que se levanta em vez
    de se escolher. Escolher aqui daria ao item o `raw_asset.id` de outra
    observação com cara de linhagem provada, e um id errado que ninguém
    procura é pior do que um `NAO SEI` honesto.
    """


def _a_observacao_volta_ao_item(recibo, por_passagem):
    """O id que o banco cunhou volta ao item que o originou. Sem procurar nada.

    ⚠️ ESTE É O METRO QUE FALTAVA, e ele é de transporte — não de descoberta.
    O par (alça, `raw_asset.id`) vem PRONTO de `preservar()`, que o atou lá
    dentro, no único sítio onde a observação planeada e a linha escrita estão
    as duas em mão. Aqui não se consulta o banco, não se compara `sha256`, não
    se lê `storage_path` e não se conta posição.

        A PONTE NÃO PROCURA A OBSERVAÇÃO: ELA RECEBE-A.

    ⚠️ E A CARDINALIDADE É DECLARADA, e não presumida:

        1 observação → N alças   legítimo. As N entradas colapsaram em
                                 `planear()` por terem a MESMA identidade de
                                 observação: são a mesma observação, e têm
                                 direito ao mesmo id.
        1 alça → 2 observações   impossível, e levanta. Ver `LigacaoAmbigua`.
        alça sem observação      ausência, e fica ausência: o item segue sem
                                 `raw_asset_id` e o READY dirá `NAO SEI`.
                                 Uma observação que o banco não confirmou não
                                 empresta id a ninguém.
    """
    visto = {}
    for o in (recibo or {}).get("RAW_OBSERVATIONS") or []:
        ident = o.get("RAW_OBSERVATION_ID")
        if ident is None:
            continue
        for alca in (o.get(PASSAGENS) or []):
            if alca in visto and visto[alca] != ident:
                raise LigacaoAmbigua(
                    "a mesma passagem foi reclamada por duas observacoes "
                    "(%s e %s). NAO foi escrita linhagem nenhuma."
                    % (visto[alca], ident))
            visto[alca] = ident
            unidade = por_passagem.get(alca)
            if unidade is not None:
                # ⚠️ O NOME É `raw_asset_id`, e é o que `admissao.
                # pronto_para_inteligencia()` lê para escrever
                # `RAW_OBSERVATION_ID`. Um segundo nome aqui seria um segundo
                # contrato com o mesmo significado.
                unidade["raw_asset_id"] = ident
    return visto


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
        # ⚠️ A PERGUNTA E SOBRE `etapa_da_corrida`, E ELA E DO DONO DELA.
        # Aqui vivia uma copia da consulta, e uma porta com SQL la dentro e um
        # segundo dono a nascer.
        tentativa = rastro.proxima_tentativa(banco, corrida["RUN_ID"], "RAW")

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
    # A alca de cada aceite -> a unidade DELE que vai a porta. O valor do mapa
    # e o PROPRIO dicionario que segue para quem julga, e nao um indice para
    # ele: um indice sobrevive a uma recusa no meio da lista e passa a apontar
    # para o vizinho, e e assim que uma linhagem troca de dono sem ninguem ver.
    #
    #     POSICAO NAO E LIGACAO.
    por_passagem = {}
    # TEMPO-E-LUGAR: o ITEM original de cada alca, para o recado de tempo e
    # lugar viajar ate a derivacao (a unidade da porta ja fala outra lingua).
    item_por_passagem = {}
    for i, item in enumerate(itens):
        if not isinstance(item, dict) or not item:
            recusas.append({"INDICE": i, "PORQUE": SEM_CONTEUDO,
                            "DETALHE": "a observacao nao e um objecto com campos"})
            continue
        f = ficha(item, corrida=corrida, raiz=raiz)
        # ⚠️ O CONTRATO DO TEXTO CONFERE-SE AQUI, COM O DO ARTEFATO E NA MESMA
        # RECUSA. Deixar passar uma unidade de texto malformada e deixar entrar
        # uma especie que ninguem vai conseguir ler depois — e a porta e o
        # ultimo sitio onde ainda ha um item a quem devolver o motivo.
        #
        #     UMA ESPECIE QUE ENTRA ERRADA NAO SE CONSERTA DEPOIS:
        #     ELA VIRA O QUE O PROXIMO LEITOR ACHAR QUE ELA E.
        quebras = art.conferir(f) + pv.conferir_unidades_de_texto(
            item.get(pv.CAMPO_DAS_UNIDADES))
        if quebras:
            recusas.append({"INDICE": i, "PORQUE": CONTRATO_QUEBRADO,
                            "ARTIFACT_ID": f.ARTIFACT_ID, "DETALHE": quebras})
            continue
        caminho = os.path.join(raiz, f.STORAGE_LOCATION)
        bytes_por_caminho[f.SHA256] = (
            open(caminho, "rb").read() if os.path.isfile(caminho)
            else _bytes_do_item(item))
        aceites.append(f)
        # ── A ALCA DESTA PASSAGEM, ATADA AQUI E CORTADA JA A SEGUIR ────────
        # ⚠️ ELA NAO PODE SER O `ARTIFACT_ID`, E ISSO FOI MEDIDO.
        # `artefato.artifact_id()` nasce do `sha256`: dois itens com os mesmos
        # bytes tem o MESMO `ARTIFACT_ID`, e uma ligacao feita nele juntaria
        # duas observacoes numa. Tambem nao pode ser o sha, nem o caminho, nem
        # a posicao na lista — sao todos ou identidade de outra especie ou
        # ligacao nenhuma.
        #
        #     UMA ALCA E PARA AMARRAR, NAO PARA IDENTIFICAR.
        #
        # Por isso ela e nova em cada passagem, unica dentro dela, e nao diz
        # NADA sobre o conteudo: e so um fio entre o item que entrou e a
        # observacao que o banco confirmar. Morre no fim desta funcao.
        alca = uuid.uuid4().hex
        unidade = unidade_para_a_porta(item, f)
        para_a_porta_.append(unidade)
        por_passagem[alca] = unidade
        item_por_passagem[alca] = item
        para_o_raw.append(dict(para_o_dono_do_raw(f, item), **{PASSAGEM: alca}))

    recibo = None
    if para_o_raw:
        recibo = preservar(_corrida_completa(corrida), para_o_raw, armazem,
                           lambda o: bytes_por_caminho[o["SHA256"]],
                           memoria=memoria)
        _a_observacao_volta_ao_item(recibo, por_passagem)
    # ── A PASSAGEM, DEPOIS DE A OBSERVACAO EXISTIR ──────────────────────
    # ⚠️ A ORDEM E A PROVA. `preservar()` ja correu, ja leu de volta e ja
    # devolveu os ids REAIS. So agora a etapa tem o que contar. Trocar estas
    # duas linhas de sitio escreveria um sucesso antes de haver sujeito.
    #
    # A excecao do rastro SOBE, e nao e apanhada aqui. Ha divida declarada
    # sobre isso (`G-TEL-01`), e esta missao nao lhe inventa politica nova:
    # inventar uma politica calada faria uma falha de telemetria passar por
    # falha de RAW — e elas nao sao a mesma coisa.
    # ⚠️ A FONTE APURA-SE UMA VEZ, E AS DUAS ETAPAS USAM A MESMA.
    # Ela ja era calculada aqui para a passagem RAW. A derivacao precisa da
    # mesma resposta, e recalcula-la la fora seria uma segunda leitura da
    # mesma pergunta — que e como duas etapas da MESMA corrida acabam a
    # declarar fontes diferentes.
    fonte = _fonte_provada(para_o_raw)

    trilho = "NAO_EMITIDO"
    if banco_do_rastro is not None:
        trilho = falar_do_raw(
            banco_do_rastro, recibo=recibo, corrida=corrida,
            entrada=len(itens), recusas_da_porta=len(recusas),
            source_id=fonte)

    # ── E AS MESMAS OBSERVACOES, NA LINGUA DE QUEM AS VAI DERIVAR ───────
    # ⚠️ ISTO SAI DO `recibo`, E NAO DA LISTA DE ACEITES. Um aceite e uma
    # ficha que passou o contrato; uma observacao e uma LINHA QUE O BANCO
    # CONFIRMOU. Entre as duas ha uma escrita que pode falhar, e derivar a
    # partir da primeira seria derivar o que talvez nao exista.
    #
    #     ACEITE NA PORTA != OBSERVACAO NO BANCO.
    #
    # Sem banco, `preservar()` nao devolve `RAW_OBSERVATIONS` e a lista sai
    # vazia — que e a verdade: nao ha observacao canonica para derivar.
    para_derivar, sem_bytes = unidades_para_a_derivacao(
        recibo, armazem,
        tempo_e_lugar_por_observacao(recibo, item_por_passagem))

    # `PARA_A_PORTA` sao os MESMOS aceites, com o conteudo intacto e o estagio
    # preservado. Nao e um terceiro objecto: e a unidade aceite, na lingua de
    # quem a vai julgar. Quem foi recusado nao aparece aqui.
    #
    # ⚠️ E DESDE `C-SCRAP-READY-RAW-LINEAGE-V1` CADA UMA LEVA A SUA OBSERVACAO.
    # `raw_asset_id` ja la esta — posto por `_a_observacao_volta_ao_item()`, a
    # partir do que `preservar()` devolveu, e so para quem o banco confirmou.
    # Era isto que faltava para a rota social cumprir o contrato READY: a rota
    # documental ja o levava por `PARA_A_DERIVACAO -> STRUCTURED`, e esta nao
    # tinha por onde.
    #
    #     COLETAR != ADMITIR != JULGAR. A PORTA NAO JULGA, MAS TRANSPORTA.
    return {"ACEITES": aceites, "RECUSAS": recusas, "RAW": recibo,
            "RASTRO": trilho, "PARA_A_PORTA": para_a_porta_,
            "PARA_A_DERIVACAO": para_derivar,
            "SEM_BYTES_PARA_DERIVAR": sem_bytes,
            "FONTE_PROVADA": fonte}
