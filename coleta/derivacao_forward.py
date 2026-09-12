#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FRONTEIRA FORWARD DA DERIVAÇÃO — quem leva o que o executor sabe até ao rastro.

    REAL CODE  !=  CANONICAL FORWARD FLOW.

O `O9` ligou a primeira torneira e provou que ela deita água. Mas ligou-a em
`executor_texto_de_pdf.correr()`, que é o modo LEGADO: varre os PDF históricos
da árvore do Git e escreve o `REGISTO-DE-ARTEFATOS.json`. Um replay legado prova
que a telemetria funciona; **não** prova que a estrada canónica forward está
instrumentada. São duas afirmações diferentes, e só a segunda serve para dizer
que a rota é observável.

    LEGACY_REPLAY_INSTRUMENTED  !=  FORWARD_INSTRUMENTED.

O caminho canónico forward é outro, e é este:

    collection_run  ->  raw_asset (o pai, no banco)
                    ->  executor_texto_de_pdf.derivar_um()
                    ->  guarda/preservar_derivado.py  (o dono da escrita)
                    ->  derived_artifact
                    ->  medidas/rastro_da_coleta.py   (o dono do rastro)

POR QUE ISTO NÃO VIVE DENTRO DO EXECUTOR
----------------------------------------
Porque o executor **não conhece banco**, e essa regra não é decorativa: é o que
impede um executor de declarar uma linhagem que não pode provar. `derivar_um()`
recebe o pai como contexto da unidade de trabalho, produz o texto, e entrega ao
dono. Ele não sabe — e não deve saber — o que é uma corrida, um `run_id`, um
`source_id` ou uma tabela de rastro.

    O EXECUTOR PRODUZ O QUE SÓ ELE SABE.
    A FRONTEIRA DE CIMA TRANSPORTA ISSO PARA O DONO CANÓNICO.

Este ficheiro é essa fronteira. Ele é um RUNNER, e não um executor: não abre
PDF nenhum, não extrai texto nenhum, não decide se um documento serve. Ele sabe
três coisas que o executor não sabe — de que corrida isto faz parte, de que
fonte, por que estrada — e é só isso que ele acrescenta.

O QUE ELE EMITE, E O QUE NÃO EMITE
----------------------------------
Emite UMA passagem: `DERIVED`, com `edge_from='RAW'`.

    NÃO emite `RAW`.       Quem escreve `raw_asset` é `guarda/preservar_coleta.py`,
                           e é dele a etapa. Esta fronteira LÊ brutos que já
                           existem; ler a linha de outro não é ter corrido a
                           etapa dele. Emitir `RAW PASS` aqui seria esta peça a
                           falar por um dono que está calado — que é exatamente
                           a confusão que o O8C pagou para desfazer.

    NÃO emite `STRUCTURED`, `ADMISSION` nem `READY`.

        STAGE EXISTS IN VOCABULARY  !=  STAGE RAN.

                           A unidade forward de hoje TERMINA em `DERIVED`. Não
                           há dono forward ligado a `derived_artifact` a jusante:
                           o modelo das estradas dá `STRUCTURED` e `ADMISSION` da
                           RC-1 como `STATE=CODE`, `PROOF_KIND=NENHUMA` — código
                           escrito, nunca corrido nesta cadeia. `NOT_RUN` também
                           seria mentira: `NOT_RUN` é «fazia parte do plano e não
                           chegou a vez». Estas etapas não fazem parte do plano
                           desta unidade; elas não têm ainda quem as corra.

O buraco fica declarado em `GAPS`, e não fechado com uma linha bonita.

⚠️ ESTA PEÇA NÃO É UM EXECUTOR.
O censo tipado (`system-map/scripts/censo_da_observabilidade.py`) classifica-a
como `RUNNER`. `FILE IN coleta/  !=  EXECUTOR`.
"""
from __future__ import annotations

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import artefato as art               # noqa: E402
import diagnostico as dg             # noqa: E402
import falhas                        # noqa: E402
import rastro_da_coleta as rastro    # noqa: E402

import executor_texto_de_pdf as ex   # noqa: E402
from guarda import preservar_derivado as pd   # noqa: E402

# ── A IDENTIDADE DA UNIDADE, E DE ONDE ELA VEM ──────────────────────────────
# ⚠️ NADA AQUI É INVENTADO, E ESSA É A CORREÇÃO.
#
#     MADE-UP TRACEABILITY ID IS WORSE THAN UNKNOWN.
#
# O `O9` escreveu `source_id="IT-PDF-ITALIANOS"`. Medido: essa cadeia de
# caracteres não existe em mais lado nenhum do repositório — nem no catálogo de
# fontes, nem no modelo das estradas, nem no banco. Era um identificador
# fabricado, e um identificador fabricado é pior do que `NULL`: `NULL` diz «não
# sei», e o fabricado diz «sei» sobre uma coisa que não existe.
#
# Os dois valores canónicos desta unidade, com dono e prova:
#
#     SOURCE_ID        IT-T2-002    candidatas/ITALY-SOURCE-MASTER-V1.json
#                                   (ARPAV — bollettini agrometeo, Veneto)
#     ROUTE_CLASS_ID   RC-1         system-map/data/estradas-it.model.json
#                                   ROUTE_CLASSES[0], OFFICIAL_HTTP_DOCUMENT,
#                                   cujo STEPS.DERIVED.OWNER é literalmente
#                                   `coleta/executor_texto_de_pdf.py`
#
# E o mesmo ficheiro do modelo declara o canário desta estrada:
#     CANARIO = {SOURCE_ID: IT-T2-002, ROUTE_CLASS_ID: RC-1}
#
# Por isso os dois NÃO são constantes deste ficheiro: eles são PARÂMETROS da
# unidade de trabalho, tal como o `raw_asset_id`. Quem manda derivar sabe de que
# fonte e por que estrada — e se não souber, passa `None`, que é a resposta
# honesta.
FRONTEIRA = "derivacao-forward"
FRONTEIRA_VERSION = "1"

# O grão de cada lado. Uma unidade forward é UM bruto -> UM derivado.
GRAO_ENTRADA = "raw_asset canonico"
GRAO_SAIDA = "derived_artifact"

# ── O MAPA DE DESTINOS: o que o dono da escrita devolveu -> por que porta o
#    item saiu. Uma tabela, e não um `if` disperso: quem acrescentar um estado
#    novo ao writer tem de vir aqui dizer por que porta ele sai, e o `UNKNOWN`
#    apanha-o enquanto não vier.
#
#     ERROR != REJECTED · o sistema falhou / o item não servia.
DESTINO_DO_ESTADO = {
    pd.INSERTED:                "PASSED",
    pd.REUSED:                  "REUSED",
    pd.REUSED_AFTER_RACE:       "REUSED",
    # Os cinco a seguir são factos sobre NÓS, e não sobre o item.
    pd.DERIVATION_DRIFT:        "ERROR",
    pd.STORAGE_CONFLICT:        "ERROR",
    pd.STORAGE_MISSING:         "ERROR",
    pd.METADATA_NOT_RECONCILED: "ERROR",
    pd.RAW_PARENT_NOT_FOUND:    "ERROR",
    pd.ERROR:                   "ERROR",
}

# `SEM_DERIVADO` não é um estado do writer — é do executor, e quer dizer que o
# original não deu texto. Ele desdobra-se em dois destinos DIFERENTES, e a
# diferença é toda:
#
#     TEXT_LAYER_ABSENT   REJECTED  o PDF é fotografia de papel. Propriedade
#                                   DELE. A ferramenta não falhou.
#     EXTRACTION_ERROR    ERROR     a ferramenta falhou, ou não está cá.
DESTINO_DO_MOTIVO = {
    art.TEXT_LAYER_ABSENT:  "REJECTED",
    art.EXTRACTION_ERROR:   "ERROR",
}

# O que este caminho AINDA não faz, dito com nome. Um buraco declarado é uma
# dívida; um buraco calado é uma mentira que ninguém vai procurar.
GAPS = (
    # ⚠️ AQUI VIVIA `RAW_FORWARD_NAO_EMITE`, E ELE FECHOU EM
    # C-MAKE-RAW-OBSERVABLE-V1. O texto dizia que `guarda/preservar_coleta.py`
    # escrevia `raw_asset` e nao emitia rastro — e era verdade.
    #
    # Quem passou a falar pela etapa RAW NAO foi esta fronteira: foi
    # `coleta/ingresso.falar_do_raw()`, na porta que preserva. Esta continua a
    # nao falar pelo RAW, e continua a ter razao — ler a linha de outro nao e
    # ter corrido a etapa dele.
    #
    #     UM BURACO QUE FECHA SAI DA LISTA DOS BURACOS.
    #     DEIXA-LO CA DEPOIS DE FECHADO E DIVIDA INVENTADA.
    #
    # A prova vive em `provas/o_raw_fala.py`, e `provas/a_rota_m2_atravessa.py`
    # exige que a aresta `RAW -> DERIVED` continue com os DOIS topos.
    ("STRUCTURED_SEM_DONO_LIGADO",
     "RC-1 STEPS.STRUCTURED: STATE=CODE, PROOF_KIND=NENHUMA. Ha codigo em "
     "guarda/importar_italia.py e ele nunca correu nesta cadeia."),
    ("ADMISSION_SEM_DONO_LIGADO",
     "RC-1 STEPS.ADMISSION: STATE=CODE, PROOF_KIND=NENHUMA. admissao/admissao.py "
     "julga o registo legado, e nao `derived_artifact`."),
    # ⚠️ O NOME DESTE GAP DIZ MAIS DO QUE SE MEDIU, e fica com o texto
    # corrigido em vez de ser apagado — porque a FALTA e real, so que nao e
    # a que o nome anuncia. Medido em `provas/a_fronteira_da_coleta.py`:
    #
    #     READY TEM contrato   COL-LAW-043, 11 campos, fixos
    #     READY TEM dono       admissao.pronto_para_inteligencia()
    #     READY TEM 0 produtores em runtime (so um CLI e uma prova)
    #     READY TEM 0 consumidores, e o destino nem sequer existe
    #
    # `leis/artefato.py:43` ja dizia «ja e o READY desta casa», e este tuplo
    # dizia «nao tem dono». Os dois nao podiam estar certos.
    #
    # O ID nao muda: ele e citado noutras linhas desta casa, e trocar um
    # identificador para melhorar uma frase espalha o custo por toda a gente.
    ("READY_NAO_TEM_DONO",
     "o NOME esta errado e o buraco e real: READY TEM dono "
     "(admissao.pronto_para_inteligencia) e TEM contrato (COL-LAW-043, 11 "
     "campos). O que nao tem e caminho: a rota forward termina em ADMISSION e "
     "nao chega la — o dono recebe `item` e a rota produz `derived_artifact` — "
     "e nao tem NENHUM consumidor. UMA PORTA POR ONDE NINGUEM PASSA NAO E UMA "
     "PORTA. Medido em provas/a_fronteira_da_coleta.py."),
    # ⚠️ ESTE ESTAVA DECLARADO SO NUM `print`.
    # `provas/o_forward_conta_se.py` media-o e escrevia-o no ecra — e mais
    # nada. Nao estava neste tuplo, nao estava em JSON nenhum, e nenhum
    # teste o guardava: era o unico dos oito buracos desta casa que podia
    # desaparecer sem dar erro em sitio nenhum.
    #
    #     UM BURACO DECLARADO E UMA DIVIDA.
    #     UM BURACO SO NUM `print` E UMA DIVIDA QUE NINGUEM HERDA.
    #
    # O sitio e este porque a excecao sobe por `correr()`, que e daqui. E
    # continua sem POLITICA de proposito: escrever aqui o que fazer quando
    # o sensor se parte seria inventar constituicao para passar num exame.
    # Declara-se a falta; nao se preenche.
    ("TELEMETRY_FAILURE_SEM_POLITICA",
     "a excecao do rastro SOBE por `correr()`. O artefato fica guardado — a "
     "coleta NAO falhou — mas quem chama perde o recibo e pode ler a excecao "
     "como corrida falhada. Nao ha politica escrita para «o sensor partiu-se». "
     "OBSERVABILITY FAILURE != COLLECTION FAILURE."),
)


def _porta(resultado: dict) -> str:
    """Por que porta este item saiu. `UNKNOWN` quando ninguém sabe — nunca zero."""
    estado = resultado.get("ESTADO")
    if estado == "SEM_DERIVADO":
        return DESTINO_DO_MOTIVO.get(resultado.get("MOTIVO_DO_EXECUTOR"), "UNKNOWN")
    return DESTINO_DO_ESTADO.get(estado, "UNKNOWN")


def correr(unidades, *, banco_do_rastro, run_id, armazem, memoria,
           source_id=None, route_class_id=None, relogio=None, derivar=None,
           tentativa=None) -> dict:
    """Deriva N unidades forward e conta-se ao rastro. Devolve o recibo.

    `unidades`   [{"RAW_ASSET_ID": <id real no banco>, "PDF": <caminho>}, ...]
    `banco_do_rastro`  onde a passagem é escrita, ou `None` para não emitir.
                       ⚠️ `None` NÃO muda o que é derivado — ver a prova de
                       invariância em `provas/o_forward_conta_se.py`.
    `run_id`     tem de existir em `collection_run`. A `024` tem chave
                 estrangeira e o banco recusa se não existir; não se contorna.
    `source_id` / `route_class_id`
                 a identidade da unidade. `None` é resposta legítima e é a
                 resposta CERTA quando não se pode provar qual é.

    `tentativa`  `None` quer dizer «pergunta ao dono». Ela estava FIXA EM
                 ZERO, e uma segunda derivação da mesma corrida colidia na
                 chave `(run_id, etapa, tentativa)` — a passagem da segunda
                 perdia-se, e o erro do banco subia com o tipo do erro do
                 fluxo. Quem sabe responder é `rastro.proxima_tentativa`, que
                 é dono da tabela; aqui não se conta nada.

                     A PERGUNTA SOBRE UMA TABELA É DE QUEM É DONO DELA.

    ⚠️ A DERIVAÇÃO ACONTECE PRIMEIRO, E O RASTRO DEPOIS. Se fosse ao contrário,
    uma falha a escrever telemetria podia impedir uma derivação de acontecer — e
    OBSERVABILITY FAILURE != COLLECTION FAILURE.
    """
    derivar = derivar or ex.derivar_um
    baldes = {d: 0 for d in ("PASSED", "REJECTED", "ERROR", "NOT_RUN",
                             "UNKNOWN", "REUSED")}
    resultados, ultimo_bom, primeiro_erro = [], None, None

    for u in unidades:
        r = derivar(u["RAW_ASSET_ID"], u["PDF"], armazem, memoria,
                    relogio=relogio)
        porta = _porta(r)
        baldes[porta] += 1
        # ⚠️ A LINHA DO DERIVADO SAI NO RECIBO, e nao so o veredito.
        # Ate a M2R esta funcao calculava a linha, tirava dela o
        # `storage_path` para o `last_good_artifact`, e DEITAVA-A FORA. Quem
        # chamasse ficava a saber que a derivacao passou — e nao a saber O QUE
        # ela produziu. Sem isso, a etapa seguinte tinha de arranjar o texto
        # noutro sitio, e a aresta DERIVED -> STRUCTURED virava um rotulo.
        #
        #     EDGE LABEL != DATA DEPENDENCY.
        #
        # Nada aqui muda o que e derivado: expoe-se o que ja estava calculado.
        linha = (r.get("LINHA_ESCRITA") or r.get("LINHA_EXISTENTE") or {}) \
            if porta in ("PASSED", "REUSED") else {}
        resultados.append({"RAW_ASSET_ID": u["RAW_ASSET_ID"], "PDF": u["PDF"],
                           "ESTADO": r.get("ESTADO"), "PORTA": porta,
                           "PORQUE": r.get("PORQUE"),
                           "LINHA": linha or None,
                           "STORAGE_PATH": (linha.get("storage_path")
                                            or r.get("STORAGE_PATH")),
                           "MOTIVO_DO_EXECUTOR": r.get("MOTIVO_DO_EXECUTOR")})
        if porta in ("PASSED", "REUSED"):
            ultimo_bom = linha.get("storage_path") or ultimo_bom
        elif porta == "ERROR" and primeiro_erro is None:
            primeiro_erro = r

    entrada = len(unidades)
    sairam = baldes["PASSED"] + baldes["REUSED"]
    houve_avaria = baldes["ERROR"] > 0 or baldes["UNKNOWN"] > 0

    # ⚠️ A ETAPA FALHA, O ITEM ERRA. Duas palavras porque são duas coisas.
    # Um item recusado NÃO faz a etapa falhar: a etapa correu, e o item não
    # servia. Foi essa confusão que já fez um defeito parecer cinco nesta casa.
    estado = rastro.FAIL if houve_avaria else rastro.PASS

    canonico = None
    if houve_avaria:
        # De `leis/falhas.py`, e não inventado aqui. `EXECUTOR_UNAVAILABLE`
        # quando a própria ferramenta não está na máquina — isso é uma avaria de
        # EXECUTOR, e diz «instale/mude de executor», não «tente outra vez».
        erro = (primeiro_erro or {})
        falta_ferramenta = "FERRAMENTA_AUSENTE" in str(
            (erro.get("ERRO") or "") + (erro.get("PORQUE") or ""))
        # ⚠️ E QUEM CONFERE ESTES NOMES NAO E ESTA PECA.
        # `medidas/rastro_da_coleta.registrar` recusa qualquer `canonical_state`
        # que `leis/falhas.py` nao declare — essa trava chegou na mesma missao,
        # pela outra sessao, depois de um emissor ter escrito `ERROR`, que e um
        # DESTINO DE ITEM e nao um estado de falha. Repetir aqui a mesma
        # verificacao seria DOIS DONOS DA MESMA PERGUNTA, que e o pecado do O8C.
        canonico = ("EXECUTOR_UNAVAILABLE" if falta_ferramenta
                    else "ITEM_ERROR")

    recibo = {
        "FRONTEIRA": FRONTEIRA,
        "RUN_ID": run_id,
        "SOURCE_ID": source_id,
        "ROUTE_CLASS_ID": route_class_id,
        "ETAPAS_EMITIDAS": ["DERIVED"] if banco_do_rastro is not None else [],
        "ENTRADA": entrada,
        "SAIRAM": sairam,
        "BALDES": dict(baldes),
        "ESTADO_DA_ETAPA": estado,
        "LAST_GOOD_ARTIFACT": ultimo_bom,
        "RESULTADOS": resultados,
        "GAPS": [g[0] for g in GAPS],
        "TERMINA_EM": "DERIVED",
        "PORQUE_TERMINA_AI": (
            "nao ha dono forward ligado a jusante de `derived_artifact`. "
            "STAGE EXISTS IN VOCABULARY != STAGE RAN."),
    }

    if banco_do_rastro is None:
        recibo["RASTRO"] = "NAO_EMITIDO"
        return recibo

    # ── A PASSAGEM, PELO DONO CANÓNICO ──────────────────────────────────────
    # Nada de SQL aqui. `medidas/rastro_da_coleta.py` é quem escreve; esta peça
    # só lhe diz o que aconteceu, na língua que ele fala — e é também a ele que
    # se pergunta em que tentativa vai esta corrida.
    if tentativa is None:
        tentativa = rastro.proxima_tentativa(banco_do_rastro, run_id, "DERIVED")

    linha = rastro.registrar(
        banco_do_rastro,
        run_id=run_id, etapa="DERIVED", edge_from="RAW", tentativa=tentativa,
        source_id=source_id, route_class_id=route_class_id,
        input_grain=GRAO_ENTRADA, input_count=entrada,
        output_grain=GRAO_SAIDA, output_count=sairam,
        cardinalidade="1:1",
        passed=baldes["PASSED"], rejected=baldes["REJECTED"],
        error=baldes["ERROR"], not_run=baldes["NOT_RUN"],
        unknown=baldes["UNKNOWN"], reused=baldes["REUSED"],
        estado=estado,
        actor=ex.EXECUTOR_ID, actor_version=ex.EXECUTOR_VERSION,
        policy_version=ex.PIPELINE_VERSION,
        canonical_state=canonico,
        error_class=((primeiro_erro or {}).get("ESTADO") if houve_avaria else None),
        error_message=((primeiro_erro or {}).get("PORQUE") if houve_avaria else None),
        last_good_artifact=ultimo_bom)

    recibo["RASTRO"] = linha
    return recibo


def main():
    print(__doc__)
    print("GAPS DECLARADOS")
    for nome, porque in GAPS:
        print("  %-28s %s" % (nome, porque))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
