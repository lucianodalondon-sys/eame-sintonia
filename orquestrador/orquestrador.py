#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O ORQUESTRADOR — quem responde «qual caminho executar para este pedido».

    py orquestrador/orquestrador.py "colete materiais de pesquisadores"
    py orquestrador/orquestrador.py "colete concorrentes" --so-a-porta   # so a peneira
    py orquestrador/orquestrador.py "colete materiais novos de pesquisadores da Espanha" --so-plano

ELE NAO COLETA. Nao abre pagina, nao chama API, nao raspa nada. Ele escolhe o
executor e coordena — e essa separacao e a razao de existir: quando o executor
for trocado por outro melhor, quem pediu continua a pedir a mesma coisa.

O QUE ELE ACRESCENTA E O RECIBO
--------------------------------
O censo encontrou o achado mais util desta missao: o `RUN-MANIFEST.json` ja tem
os campos certos — RUN_ID, ACTOR, ACTOR_VERSION, STARTED_AT, FINISHED_AT, INPUT,
COST_USD, ITEM_COUNT_RAW, STATUS, ERROR — e **cinco reguas ja o leem**. So que
nenhum executor o escreve. Por isso metade das corridas guardadas diz
`NOT_PRESERVED` no tempo e na versao: foram preenchidas a mao, depois, de
memoria.

Nao se inventa aqui um recibo novo. Faz-se o orquestrador ASSINAR o que ja
existe, em toda corrida, sem depender de ninguem se lembrar.

    O QUE NAO TEM RECIBO NAO ACONTECEU. Uma coleta sem recibo nao se consegue
    auditar, nao se consegue repetir, e nao se consegue cobrar — e daqui a tres
    meses ninguem sabe dizer se aquele numero veio de uma corrida boa ou de uma
    que falhou a meio.

ERRO NAO E REJEICAO
-------------------
Se o executor rebentar, o estado e ERRO e o recibo guarda a mensagem. Nao e
`REJEITADO`: rejeitado quer dizer «olhei e nao serve», e aqui ninguem chegou a
olhar. Confundir os dois faz uma falha de rede parecer um julgamento sobre a
fonte, e a fonte leva a culpa pela ferramenta.
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

from pedido import Pedido, de_uma_frase, PedidoInvalido, ERRO, COLHIDO  # noqa: E402
from receitas import (resolver, Plano,  # noqa: E402
                      FILTROS_DO_RESOLVEDOR, filtros_consumidos)
import admissao as adm  # noqa: E402
import proveniencia as pv  # noqa: E402
import ingresso as ing  # noqa: E402  — a porta de entrada da coleta
import derivacao_forward as deriv  # noqa: E402 — o RUNNER canonico do DERIVED
from guarda import preservar_documento as pdoc  # noqa: E402 — o dono do STRUCTURED documental
import retorno_da_coleta as rdc  # noqa: E402 — a lei do retorno (COL-LAW-505)
import persistencia  # noqa: E402 — quem liga a memoria ao banco descartavel

NAO_SEI_RUN = "NAO SEI"
import sala_de_espera as espera        # noqa: E402

# ⚠️ A MORADA DA ESPERA NAO VIVE AQUI, E JA NAO E ESTE FICHEIRO QUE ESCREVE.
# A constante ficava aqui e a escrita corria a baixo — e isso contradizia a
# COL-LAW-012: o orquestrador CONTROLA, nao transporta dado. Enquanto a unica
# escrita estivesse no control plane, a rota forward nao tinha como pousar a
# unidade sem escrever uma SEGUNDA.
#
#     ONE CONCEPT -> ONE OWNER.
#
# O dono e `admissao/sala_de_espera.py`, e este ficheiro passou a ser um
# chamador como qualquer outro.


def o_envelope(e: dict, run_id: str = "") -> tuple[dict, str]:
    """O QUE A CORRIDA DEVOLVEU, LIDO DA DECLARACAO — e nunca adivinhado.

        SO COLHEITA ENTRA NO INGRESSO.  (COL-LAW-505)

    ⚠️ AQUI VIVIA A HEURISTICA, E ELA CUSTOU 253 FALSOS POSITIVOS:

        lista = d if isinstance(d, list) else next(
            (v for v in d.values() if isinstance(v, list) and v
             and isinstance(v[0], dict)), [])

    «uma lista, ou o primeiro campo do ficheiro que seja lista de fichas». Com
    isso, 163 linhas de um manifesto de descarga, 74 fichas de conta, 12 fichas
    de pessoa e 4 passos de um plano entraram na cadeia como material observado.
    E o contraexemplo que fecha o assunto: o `CLASSIFICADO-V1.json` DECLARA um
    contentor `ITEMS` com `ITEM_COUNT = 0`, e a heuristica SALTAVA-O por estar
    vazio para agarrar a lista de catalogo ao lado.

        UMA HEURISTICA QUE PREFERE UMA LISTA CHEIA A UMA LISTA CERTA
        NAO ESTA A LER O RETORNO: ESTA A ADIVINHAR.

    Esta funcao deixou de classificar. O que sobra dela e legitimo e continua a
    ser dela: ENCONTRAR a declaracao, e dizer alto quando o sitio declarado nao
    existe. Quem classifica e `leis/retorno_da_coleta.py`, e a lei nao esta
    copiada aqui — esta importada.
    """
    ident = e.get("id") or "NAO SEI"
    versao = versao_do_executor((e.get("roda") or [""])[0])
    retorno = e.get("retorno") or {}
    notas = []

    # ── 1 · A CORRIDA DECLAROU? Essa e a unica origem de COLHEITA ──────────
    # ⚠️ O ENDERECO E DESTA CORRIDA, E A REGRA NAO VIVE AQUI.
    # Isto lia `retorno.ENVELOPE` como um caminho literal — um por EXECUTOR.
    # Duas corridas do mesmo executor escreviam no mesmo ficheiro, e esta
    # funcao devolvia a ultima que tivesse escrito, a qualquer um que
    # perguntasse. Medido em `G-ENV-01`.
    #
    #     «PEGUEI O QUE ESTAVA LA» NAO E UMA RESPOSTA SOBRE ESTA CORRIDA.
    #
    # Quem sabe onde vive o envelope de uma corrida e `leis/retorno_da_coleta`,
    # e e de la que a regra vem. Aqui so se pergunta.
    padrao = retorno.get("ENVELOPE")
    # ⚠️ PERGUNTAR PELA COLHEITA SEM DIZER DE QUE CORRIDA E UMA PERGUNTA MAL
    # POSTA, e era exactamente assim que uma corrida consumia o envelope de
    # outra. Com o endereco por corrida, a pergunta sem corrida cairia no
    # caminho sem sufixo — que ninguem escreve — e devolveria «nao ha nada»
    # em silencio. Silencio nao: recusa com motivo.
    #
    #     «DA-ME A COLHEITA DESTE EXECUTOR» NAO TEM RESPOSTA.
    #     A COLHEITA E DE UMA CORRIDA, OU NAO E DE NINGUEM.
    if padrao and not str(run_id or "").strip():
        notas.append("pediu-se a colheita de «%s» sem dizer de que corrida. "
                     "O envelope e de uma corrida, e sem ela nao ha o que "
                     "devolver." % ident)
        return rdc.envelope_de_quem_nao_declarou(
            run_id or NAO_SEI_RUN, ident, versao,
            "a colheita foi pedida sem corrida"), " · ".join(notas)
    caminho = rdc.endereco_do_envelope(padrao, run_id) if padrao else padrao
    if caminho:
        alvo = RAIZ / caminho
        if alvo.is_file():
            try:
                envelope = json.loads(alvo.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as ex:
                notas.append(f"«{caminho}» nao deu para ler: {type(ex).__name__}")
            else:
                # ── E O ENVELOPE TEM DE SER DESTA CORRIDA ─────────────────
                # O endereco ja separa; isto e a segunda tranca, e existe
                # porque a primeira pode ser contornada por um ficheiro
                # deixado a mao, por um restauro de backup ou por um padrao
                # sem sufixo. Uma tranca de endereco protege do acidente; uma
                # tranca de CONTEUDO protege tambem do engano.
                #
                #     O CAMINHO E MORADA. A IDENTIDADE ESTA DENTRO.
                dele = str(envelope.get("RUN_ID") or "").strip()
                if run_id and dele and dele != run_id:
                    notas.append(
                        f"«{caminho}» declara a corrida «{dele}» e quem "
                        f"perguntou foi «{run_id}». Saida de outra corrida "
                        f"nao se atribui a esta.")
                    return rdc.envelope_de_quem_nao_declarou(
                        run_id, ident, versao,
                        f"o envelope encontrado pertence a «{dele}»"), \
                        " · ".join(notas)
                if run_id and not dele:
                    envelope["RUN_ID"] = run_id
                return envelope, " · ".join(notas)
        notas.append(f"«{caminho}» e o envelope declarado e nao existe: ou a "
                     f"corrida nao correu aqui, ou ela nao declarou o que fez.")

    # ── 2 · O LEGADO, QUE SO PODE DECLARAR SUPORTE ─────────────────────────
    legado = retorno.get("LEGADO")
    if legado:
        for onde in legado:
            if not (RAIZ / onde).exists():
                notas.append(f"«{onde}» esta declarado e nao existe nesta arvore.")
        return rdc.envelope_do_legado(run_id or "NAO SEI", ident, versao,
                                      legado, str(RAIZ)), " · ".join(notas)

    # ── 3 · NINGUEM DECLAROU NADA ──────────────────────────────────────────
    #     UM RETORNO SEM DECLARACAO NAO E UM RETORNO VAZIO:
    #     E UM RETORNO QUE NAO SE DECLAROU.
    for onde in e.get("larga_em") or []:
        if not (RAIZ / onde).exists():
            notas.append(f"«{onde}» nao existe nesta arvore: o executor declara "
                         f"que larga ai, e nao ha nada.")
    return rdc.envelope_de_quem_nao_declarou(
        run_id or "NAO SEI", ident, versao,
        "este executor nao declara o que devolve (sem ENVELOPE nem LEGADO em "
        "`retorno`). Antes, era aqui que a heuristica adivinhava."), \
        " · ".join(notas)


def a_colheita(e: dict, run_id: str = "") -> tuple[list, str]:
    """So o que a lei deixa atravessar. Mesma assinatura de sempre, outra fonte.

    Quem chama isto continua a receber `(itens, notas)`. O que mudou e de onde
    vem a lista: era um palpite sobre a forma do JSON, e agora e o resultado de
    `conferir()` + `so_o_que_entra()` sobre um envelope declarado.
    """
    envelope, notas = o_envelope(e, run_id)
    mal = rdc.conferir(envelope, str(RAIZ))
    if mal:
        # UM ENVELOPE QUE QUEBRA O CONTRATO NAO ENTREGA NADA. Recusar item a
        # item deixaria passar metade de um retorno que ja se sabe mal formado.
        return [], " · ".join(filter(None, [notas] + ["ENVELOPE_INVALIDO: " + m
                                                     for m in mal]))
    return rdc.so_o_que_entra(envelope), notas


def pela_entrada(itens: list, recibo: dict, memoria=None,
                 banco_do_rastro=None, armazem=None) -> dict:
    """Leva a colheita a PORTA DE ENTRADA da coleta, que a preserva como RAW.

    Ela nao julga nada: quem julga e a admissao, logo a seguir. Aqui responde-se
    so «posso preservar esta observacao?», e o que nao passa sai com nome —
    `INGRESS_SEM_CONTEUDO`, `INGRESS_CONTRATO_QUEBRADO` — que NAO e o mesmo que
    ser rejeitado na admissao, nem que ter dado erro, nem que nao ter corrido.

        RECUSA NA PORTA != REJEITADO NA ADMISSAO != ERRO != NAO CORREU.

    O armazem e LOCAL de proposito. Preservar nao pode depender de haver rede
    nem credencial: um coletor que corre offline continua a ter de deixar
    rasto.

    ⚠️ A `memoria` E O BANCO, E ELA NAO CHEGAVA AQUI. A frase acima dizia
    «quando houver banco, ele entra por `memoria=` sem esta funcao mudar» — e
    era falsa por uma unica razao: esta funcao nao tinha por onde o receber.
    `ing.receber` sempre aceitou `memoria=`; quem o chamava e que nao o
    passava, e por isso `collection_run` e `raw_asset` nunca viam uma corrida
    da rota canonica.

        UM PARAMETRO OPCIONAL QUE NINGUEM CONSEGUE PASSAR
        NAO E OPCIONAL: E INEXISTENTE.

    Continua a ser opcional de verdade: sem banco ligado, `memoria=None`, e a
    preservacao em disco acontece na mesma.
    """
    # ⚠️ O ARMAZEM PASSOU A PODER VIR DE FORA, E A RAZAO E A DERIVACAO.
    # Quem preserva o bruto e quem escreve o derivado tem de ser o MESMO
    # armazem: sao dois bytes da mesma corrida, e dois armazens dariam ao
    # derivado uma morada que o bruto nao conhece. Sem ninguem o passar,
    # continua a nascer aqui exactamente como nascia.
    armazem = armazem if armazem is not None else ing.ArmazemLocal(RAIZ)
    r = ing.receber(itens, corrida=recibo, armazem=armazem, memoria=memoria,
                    raiz=str(RAIZ), banco_do_rastro=banco_do_rastro)
    bruto = r.get("RAW") or {}
    return {
        # ⚠️ ISTO DEVOLVIA SO A CONTAGEM, e a unidade canonica morria aqui.
        # `len(r["ACEITES"])` contava o que o contrato tinha acabado de apurar
        # — `ARTIFACT_TYPE = RAW` incluido — e a linha seguinte entregava a
        # porta o item ORIGINAL, sem estagio nenhum. A porta, sem saber que
        # julgava um documento, cobrava-lhe o tempo de um FATO (COL-LAW-502).
        #
        #     CONTAR UMA COISA NAO E GUARDA-LA.
        #
        # A unidade vai junto agora. Quem a monta continua a ser o dono da
        # fronteira: `coleta/ingresso.py::unidade_para_a_porta`.
        "PARA_A_PORTA": r.get("PARA_A_PORTA") or [],
        # ⚠️ E A MESMA COISA OUTRA VEZ, PARA A OUTRA ETAPA. `PARA_A_PORTA`
        # nasceu porque contar os aceites nao era guarda-los; isto nasce pela
        # razao gemea, um degrau a frente: o `recibo` do RAW trazia o
        # `RAW_OBSERVATION_ID` e o endereco de cada byte, e esta funcao
        # deitava-o fora ao devolver so `PRESERVADOS`. Sem eles, quem quisesse
        # derivar tinha de ir procurar os ficheiros ao disco — e procurar por
        # caminho e o que faz um derivado nascer com o pai errado.
        #
        #     CONTAR UMA COISA NAO E GUARDA-LA.
        "PARA_A_DERIVACAO": r.get("PARA_A_DERIVACAO") or [],
        "SEM_BYTES_PARA_DERIVAR": r.get("SEM_BYTES_PARA_DERIVAR") or [],
        # A fonte que o COLETOR declarou, apurada uma vez pela porta. Ela vem
        # por aqui para a derivacao nao a inferir do caminho — que e de onde
        # ela nunca pode vir.
        "FONTE_PROVADA": r.get("FONTE_PROVADA"),
        "PRESERVADOS": len(r["ACEITES"]),
        "RECUSADOS": len(r["RECUSAS"]),
        "PORQUE_RECUSADOS": [x["PORQUE"] for x in r["RECUSAS"]],
        "RUN_STATE": bruto.get("RUN_STATE", "NAO_CORREU"),
        # ⚠️ A CORRIDA CANONICA CORRIA E NAO DEIXAVA RASTO NENHUM.
        # MEDIDO em C-PROVE-CANONICAL-E2E-FROM-REQUEST-V1: um pedido real
        # atravessou ate a ADMISSION, escreveu 4 linhas em `raw_asset` — e
        # `etapa_da_corrida` ficou com ZERO. A etapa RAW ja sabia falar desde
        # `C-MAKE-RAW-OBSERVABLE-V1`; quem a chamava e que nao lhe dava onde.
        #
        #     UM PARAMETRO OPCIONAL QUE NINGUEM CONSEGUE PASSAR
        #     NAO E OPCIONAL: E INEXISTENTE.
        #
        # E a mesma familia do defeito da `memoria`, oito linhas acima, no
        # mesmo ficheiro e na mesma funcao. Duas vezes o mesmo, e a segunda
        # depois de a primeira estar escrita a vista.
        "RASTRO": r.get("RASTRO", "NAO_EMITIDO"),
        # O banco NAO foi medido nesta corrida, e dizer 0 seria dizer que se
        # olhou e nao havia. Nao se olhou.
        "BANCO": (bruto.get("MEMORIA") or {}).get("COMO_FOI_MEDIDO",
                                                  "NAO MEDIDO — sem banco ligado"),
    }


def pela_derivacao(unidades: list, *, run_id: str, armazem, memoria,
                   banco_do_rastro=None, source_id=None,
                   route_class_id=None, nao_derivaveis=None) -> dict:
    """Leva as observacoes preservadas ao RUNNER CANONICO do DERIVED.

    ⚠️ ESTA FUNCAO NAO DERIVA NADA, E ISSO NAO E MODESTIA: E A LEI.

        CONTROL PLANE != DATA PLANE.  (COL-LAW-012)

    Ela nao abre um PDF, nao extrai texto, nao escreve `derived_artifact`, nao
    escreve `etapa_da_corrida` e nao calcula linhagem. Tudo isso ja tem dono:

        coleta/executor_texto_de_pdf.py   produz o texto (e nao conhece banco)
        coleta/derivacao_forward.py       o RUNNER: transporta a identidade
        guarda/preservar_derivado.py      escreve `derived_artifact`
        medidas/rastro_da_coleta.py       escreve a passagem DERIVED

    O que faltava nao era nenhum deles: era a CHAMADA. Medido em
    `provas/o_pedido_atravessa.py`, um pedido real chegava a STORAGE e parava
    ali — com a derivacao a funcionar, a um `import` de distancia, sem ninguem
    a invocar.

        CAPABILITY EXISTS != EDGE EXISTS.
        UMA CAPACIDADE QUE NINGUEM CHAMA NAO E UMA ETAPA DA ESTRADA.

    ⚠️ E ELA NAO ESCOLHE O QUE DERIVA. As `unidades` vem da porta, ja
    filtradas por quem tem esse direito: sao as observacoes que o BANCO
    confirmou nesta corrida. Deixar o orquestrador escolher — por nome, por
    pasta, pelo primeiro ficheiro que aparecesse — seria o control plane a
    decidir linhagem, que e a maneira mais silenciosa de um derivado nascer
    filho de outro bruto.

    `route_class_id` vai como vier, e hoje vem `None`: nenhuma peca entre o
    Pedido e a corrida declara classe de rota. Escrever `RC-1` aqui porque o
    canario de hoje e RC-1 seria fabricar identidade a partir do caso da vez.

        UNKNOWN HONESTO > ID INVENTADO.
    """
    if not unidades:
        # ── DUAS AUSENCIAS DIFERENTES, E SO UMA E SILENCIO ─────────────────
        # NAO CORREU != CORREU E NAO DEU NADA. Sem observacao preservada nao
        # ha sujeito, e inventar uma chamada vazia poria uma passagem DERIVED
        # no rastro a dizer que a etapa correu.
        #
        # ⚠️ MAS «NAO HA UNIDADES» DEIXOU DE QUERER DIZER UMA COISA SO.
        # A porta passou a separar duas razoes para uma observacao nao ir
        # derivar, e elas nao sao a mesma ausencia:
        #
        #     nao houve observacao nenhuma        -> nao ha sujeito. Silencio.
        #     houve, e a especie nao se deriva    -> HA sujeito, e ha resposta.
        #
        # A segunda tem de aparecer no rastro. Uma corrida que preservou
        # observacoes e nao deixou linha `DERIVED` nenhuma le-se, tres meses
        # depois, como «ninguem sabe se aquela etapa correu» — e sabe-se.
        #
        #     UMA ETAPA QUE NAO SE APLICA NAO E UMA ETAPA SEM RESPOSTA.
        #
        # Quem escreve a passagem continua a ser o RUNNER, e nao esta funcao:
        # CONTROL PLANE != DATA PLANE (COL-LAW-012) nao muda por a resposta
        # ser um nao.
        if nao_derivaveis:
            r = deriv.nao_se_aplica(
                nao_derivaveis, banco_do_rastro=banco_do_rastro,
                run_id=run_id, source_id=source_id,
                route_class_id=route_class_id)
            return {"CHAMADO": False,
                    "APLICABILIDADE": "NOT_APPLICABLE",
                    "PORQUE": r.get("PORQUE"),
                    "UNIDADES": 0,
                    "NAO_DERIVAVEIS": len(nao_derivaveis),
                    "ESTADO_DA_ETAPA": r.get("ESTADO_DA_ETAPA"),
                    "RASTRO": ("EMITIDO" if r.get("RASTRO") not in
                               (None, "NAO_EMITIDO") else "NAO_EMITIDO")}
        return {"CHAMADO": False, "PORQUE": "nenhuma observacao preservada "
                                            "nesta corrida para derivar",
                "UNIDADES": 0}
    recibo = deriv.correr(unidades, banco_do_rastro=banco_do_rastro,
                          run_id=run_id, armazem=armazem, memoria=memoria,
                          source_id=source_id, route_class_id=route_class_id)
    return {
        "CHAMADO": True,
        "UNIDADES": len(unidades),
        "RUNNER": recibo.get("FRONTEIRA"),
        "RUN_ID": recibo.get("RUN_ID"),
        "SOURCE_ID": recibo.get("SOURCE_ID"),
        "ROUTE_CLASS_ID": recibo.get("ROUTE_CLASS_ID"),
        "ESTADO_DA_ETAPA": recibo.get("ESTADO_DA_ETAPA"),
        "BALDES": recibo.get("BALDES"),
        "SAIRAM": recibo.get("SAIRAM"),
        "RASTRO": ("EMITIDO" if recibo.get("RASTRO") not in (None, "NAO_EMITIDO")
                   else "NAO_EMITIDO"),
        # Os derivados desta passagem, com o pai REAL de cada um. Nao e
        # decoracao do recibo: e o que permite a quem audita perguntar ao
        # banco se aquela linha tem mesmo aquele pai.
        "DERIVADOS": [{"RAW_ASSET_ID": r.get("RAW_ASSET_ID"),
                       "PORTA": r.get("PORTA"),
                       "STORAGE_PATH": r.get("STORAGE_PATH")}
                      for r in (recibo.get("RESULTADOS") or [])],
        # ⚠️ E OS RESULTADOS INTEIROS SEGUEM, porque a etapa seguinte precisa
        # da LINHA do derivado — o `id` e o `storage_path` — e reconstrui-la
        # do outro lado daria duas versoes do mesmo facto.
        "RESULTADOS": recibo.get("RESULTADOS") or [],
    }


def pela_estruturacao(derivacao: dict, *, run_id: str, armazem, memoria,
                      source_id=None) -> dict:
    """Leva o TEXTO derivado ao dono do documento estruturado.

    ⚠️ ESTA ETAPA NAO ESCREVE NADA, E ISSO E A LEI E NAO MODESTIA.

        CONTROL PLANE != DATA PLANE.  (COL-LAW-012)

    Quem escreve `documento_estruturado` e `guarda/preservar_documento.py`.
    Aqui le-se o corpo pelo endereco canonico do derivado e entrega-se.

    ⚠️ E O CORPO VEM DO ARMAZEM, PELO `storage_path` DA LINHA DO DERIVADO.
    Nao se reaproveita o texto que o executor tinha em memoria: o que seguir
    para a frente tem de ser o que FICOU GUARDADO, ou a estrada estaria a
    estruturar uma coisa e a ter guardada outra.

        EDGE LABEL != DATA DEPENDENCY.

    ⚠️ E NAO HA CANAL, NEM SE INVENTA UM. Esta rota e documental: a fonte e
    uma agencia que publica PDF no sitio dela, e nao uma plataforma que emita
    identificadores. Por isso o dono e `documento_estruturado` e nao
    `conteudo` — ver a migration 030.

        SOURCE != ENDPOINT != ARTIFACT.
    """
    bons = [r for r in (derivacao.get("RESULTADOS") or [])
            if r.get("PORTA") in ("PASSED", "REUSED") and (r.get("LINHA") or {})]
    if not bons:
        # NAO CORREU != CORREU E NAO DEU NADA. Sem derivado nao ha corpo, e
        # inventar uma passagem vazia poria STRUCTURED no rastro a dizer que a
        # etapa correu.
        return {"CHAMADO": False, "UNIDADES": 0,
                "PORQUE": "nenhum derivado desta corrida para estruturar"}

    feitos, recusados = [], []
    for r in bons:
        linha = r["LINHA"]
        try:
            corpo = armazem.ler(linha["storage_path"]).decode("utf-8",
                                                              errors="replace")
        except Exception as erro:                          # noqa: BLE001
            recusados.append({"DERIVED_ARTIFACT_ID": linha.get("id"),
                              "PORQUE": "o corpo nao se leu: %s" % erro})
            continue
        # ── A FONTE DESTE DOCUMENTO, E SO DEPOIS A DA CORRIDA ──────────
        # ⚠️ ISTO PASSAVA `source_id` — o da CORRIDA — a cada documento.
        # Medido contra os dez documentos italianos reais desta arvore: a
        # corrida trouxe SETE fontes diferentes, `_fonte_provada()` devolveu
        # `None` (com razao: uma corrida com sete fontes nao tem uma), e o dono
        # do STRUCTURED recusou os sete com «o documento nao diz de que fonte
        # veio». A estrada parava aqui, com a resposta certa a pergunta errada.
        #
        #     A FONTE DE UM DOCUMENTO E DO DOCUMENTO.
        #     PERGUNTA-LA A CORRIDA E LER O REGISTO DO COLECTIVO
        #     PARA SABER O NOME DE UM INDIVIDUO.
        #
        # A da corrida fica como ultimo recurso — e nao se inventa: quando
        # nenhuma das duas identifica, o dono do STRUCTURED recusa, e recusar
        # continua a ser o comportamento certo.
        fonte_do_documento = r.get("SOURCE_ID") or source_id
        recibo = pdoc.preservar_documento(
            {"derived_artifact_id": linha["id"], "run_id": run_id,
             "source_id": fonte_do_documento, "texto": corpo,
             # ⚠️ `document_id` NAO VAI — E A RAZAO MUDOU, E ISSO FICA DITO.
             # Esta linha dizia «a fonte documental nao o prova». Era verdade
             # da unica fonte que por aqui passava (um boletim ARPAV, sem
             # numero que a fonte declare). Deixou de ser verdade em
             # `C-T4-CANONICAL-ACQUISITION-TO-WAITING-ROOM-V1`: a fonte
             # `EU-T4-001` declara, no contrato dela, `identity_keys: CELEX`,
             # e a observacao chega com esse CELEX provado.
             #
             #     UMA FRASE VERDADEIRA SOBRE A UNICA FONTE QUE JA PASSOU
             #     NAO E UMA FRASE VERDADEIRA SOBRE A ESTRADA.
             #
             # A identidade NAO SE PERDE: ela vive onde e a casa dela —
             # `raw_asset.document_key`, com `document_key_basis =
             # SOURCE_DOCUMENT_ID` e `identity_state = FORWARD_IDENTIFIED`.
             # Medido: a corrida T4 aterra com o CELEX escrito la.
             #
             # O que falta e TRANSPORTA-LA daqui ate `documento_estruturado`,
             # e isso atravessa quatro donos (o dono do RAW emite quatro
             # campos, a ponte da derivacao passa dois, o runner outro tanto).
             # Alargar essa cadeia era mexer no que esta missao nao veio
             # medir, e por isso fica DECLARADO em vez de improvisado:
             # `documento_estruturado.document_id` continua NULL, e NULL aqui
             # significa «esta casa ainda nao o transporta», e nao «a fonte
             # nao o provou». Os dois nao sao a mesma ausencia.
             "source_url": r.get("SOURCE_URL")},
            memoria)
        if recibo["ESTADO"] in (pdoc.INSERTED, pdoc.REUSED):
            feitos.append({"RAW_ASSET_ID": r.get("RAW_ASSET_ID"),
                           "SOURCE_ID": fonte_do_documento,
                           "DERIVED_ARTIFACT_ID": linha["id"],
                           "PARENT_SHA256": linha.get("parent_sha256"),
                           # ⚠️ ELA ATRAVESSA, E NAO SE MEDE AQUI.
                           # `raw_asset.captured_at` e o instante em que esta
                           # maquina recebeu o ORIGINAL. Esta etapa e de
                           # escritorio e acontece depois; escrever a hora
                           # dela aqui poria a hora do trabalho no campo do
                           # tempo da colheita.
                           "CAPTURED_AT": r.get("CAPTURED_AT"),
                           "ESTADO": recibo["ESTADO"],
                           "TEXTO": corpo})
        else:
            recusados.append({"DERIVED_ARTIFACT_ID": linha.get("id"),
                              "PORQUE": recibo.get("PORQUE"),
                              "ESTADO": recibo["ESTADO"]})
    return {"CHAMADO": True, "UNIDADES": len(bons),
            "ESTRUTURADOS": feitos, "RECUSADOS": recusados,
            "DONO": "guarda/preservar_documento.py"}


def item_documental_para_a_porta(estruturado, *, source_id):
    """A unidade STRUCTURED na lingua que a porta le.

    ⚠️ O ESTAGIO VIAJA, E E ELE QUE MUDA A PERGUNTA.
    `admissao.estagio()` le `artifact_type`: a um DERIVED pergunta-se o que se
    pergunta a um DOCUMENTO, e nao o tempo do FATO (COL-LAW-502). Sem isto,
    todo documento chegava como estagio desconhecido e respondia NAO SEI a uma
    pergunta que nao era a dele.

    ⚠️ E O `id` DO ITEM E O DO NOSSO REGISTO, e nao um DOCUMENT_ID.
    `documento_estruturado` e chaveada pelo `derived_artifact_id`, e e esse o
    nome da linha. O nome que o MUNDO deu ao documento continua ausente, e
    ausente e o que ele e.

        A IDENTIDADE DO NOSSO REGISTO NAO E A IDENTIDADE DO DOCUMENTO.
        CONFUNDI-LAS E QUE SERIA FABRICAR.
    """
    # ── E O TEXTO LEVA A ESPECIE DELE, QUE NAO E A DE UM POST ─────────────
    # ⚠️ ESTE `texto` NAO E O TEXTO DE NINGUEM: E EXTRACCAO DE MAQUINA.
    # Ele sai de `armazem.ler(storage_path)` sobre um DERIVED que
    # `executor_texto_de_pdf` produziu a partir de um PDF. Chegava a porta
    # indistinguivel de uma legenda escrita por uma pessoa — e a primeira
    # pergunta que a inteligencia faz sobre qualquer classificacao e
    # exactamente essa: o que sustentou isto, o que alguem escreveu ou o que a
    # maquina leu?
    #
    #     DOCUMENT_TEXT != AUTHOR_TEXT. O PDF NAO FALOU: NOS LEMOS.
    #
    # E aqui a linhagem NAO e `UNKNOWN`: esta rota conhece a observacao de onde
    # o documento nasceu (`RAW_ASSET_ID`) e o pai dos bytes (`PARENT_SHA256`).
    # Escreve-los e a diferenca entre um texto que se confere contra o original
    # e um texto que ninguem consegue ligar ao PDF de onde saiu.
    unidade = pv.unidade_de_texto(
        texto=estruturado["TEXTO"],
        kind=pv.DOCUMENT_TEXT, kind_basis=pv.DECLARED_BY_ROUTE,
        relation=pv.ORIGINAL, unit_id="TU-1",
        raw_observation_id=estruturado.get("RAW_ASSET_ID"),
        source_artifact=estruturado.get("PARENT_SHA256"),
        derivation_method=pv.EXTRAIDO_DO_DOCUMENTO,
        tool="coleta/executor_texto_de_pdf.py")
    # ── E A HORA DA COLHEITA ATRAVESSA COM ELA ────────────────────────────
    # ⚠️ NO NOME DO CONTRATO COMUM, e nao no da porta. `COLLECTED_AT` e o nome
    # que `leis/artefato.py` deu a este facto, e `ing.para_a_porta()` e o unico
    # sitio onde ele vira `captured_at`. Escrever ja `captured_at` aqui saltaria
    # o tradutor — e um segundo sitio que traduz e um sitio onde a traducao pode
    # divergir.
    #
    #     UMA TRAVESSIA, UM TRADUTOR, NA FRONTEIRA.
    #
    # E AUSENCIA NAO SE FABRICA: sem `CAPTURED_AT` na unidade, o campo nao e
    # escrito, a porta nao o ve, e `pronto_para_inteligencia()` escreve
    # `NAO SEI` — que e a verdade, e nao um remendo.
    bruto = {"SOURCE_ID": estruturado.get("SOURCE_ID") or source_id,
             "ARTIFACT_TYPE": "DERIVED",
             "PARENT_SHA256": estruturado.get("PARENT_SHA256"),
             pv.CAMPO_DAS_UNIDADES: [unidade]}
    if estruturado.get("CAPTURED_AT") not in (None, "", "NAO SEI", "NAO_SE_APLICA"):
        bruto["COLLECTED_AT"] = estruturado["CAPTURED_AT"]
    item = ing.para_a_porta(bruto)
    item.update({"id": "derived:%s" % estruturado["DERIVED_ARTIFACT_ID"],
                 "raw_asset_id": estruturado.get("RAW_ASSET_ID")})
    return item


def universo_do_pedido(p) -> str:
    """O universo que a porta vai perguntar. → a string, ou levanta.

    ⚠️ ELE VEM DO PEDIDO, E SÓ DO PEDIDO. Não se deriva do `alvo`, do
    território da fonte, da plataforma nem do conteúdo — e é por isso que esta
    função não recebe nenhum deles como alternativa.

        ALVO = PARA QUE SERVE a coleta.
        UNIVERSO = QUE PERGUNTA a porta faz ao conteúdo.
        ALVO != UNIVERSO.

    A régua de quem julga é `admissao.PERGUNTAS_DO_UNIVERSO`, e ela conhece
    cinco: `T3 T4 T5 T7 T9`. Os alvos são treze. Emprestar um ao outro produz
    perguntas que não existem — silenciosamente, porque a porta responde
    `NAO_SE_APLICA` com toda a educação a um universo sem régua.

    FAIL-CLOSED PELO DONO QUE JÁ EXISTE: a validação é de
    `coleta/rota_forward_documento.universo_declarado`, que já levanta
    `UniversoNaoDeclarado` para `None`, `''`, `'  '` e `'NAO SEI'` (§148).
    Escrever aqui uma segunda verificação faria duas leis para a mesma
    pergunta, e a partir daí nenhuma das duas valeria.

    ⚠️ E NÃO HÁ FALLBACK. Nem para `p.alvo`, nem para um universo por omissão:
    era exactamente disso que o §148 livrou esta casa, e um `or p.alvo` no fim
    desta linha repunha o defeito com outra roupa.
    """
    import rota_forward_documento as _rf                    # noqa: PLC0415
    return _rf.universo_declarado((p.filtros or {}).get("universo"))


def pela_porta(itens: list, universo: str, run_id: str) -> dict:
    """Leva cada item a porta de admissao e guarda TODAS as decisoes.

    TODAS, e nao so as que passaram: o «nao» sem testemunha e trabalho perdido
    duas vezes — perde-se o item e perde-se a informacao de que aquela fonte
    entrega lixo.
    """
    # ── A TRAVESSIA DE LINGUA, UMA VEZ, PELO DONO DELA ─────────────────────
    # A unidade chega na lingua do contrato comum (`SOURCE_ID`) e a admissao le
    # a dela (`source_id`). Esta rota NAO traduzia — e por isso a primeira
    # unidade italiana a chegar aqui ouviu «nao da para dizer de onde veio»
    # com a origem declarada no proprio item.
    #
    # A traducao nao se escreve aqui: `coleta/ingresso.py::para_a_porta` e o
    # unico dono, e este e um dos tres sitios que passaram a usa-lo.
    prontos, decisoes = [], []
    for x in itens:
        try:
            prontos.append(ing.para_a_porta(x))
        except ing.AliasEmConflito as ex:
            # DOIS NOMES, DOIS VALORES. Nao se escolhe em silencio e nao se
            # rebenta a corrida: o item vai a porta declarado como ilegivel, e
            # ela responde ERRO — que NAO e rejeicao. `erro_de_leitura` e o
            # campo que a propria admissao ja usa para isto.
            prontos.append(dict(x, erro_de_leitura=str(ex)))
    decisoes = [adm.decidir(x, universo, corrida=run_id) for x in prontos]
    itens = prontos
    if decisoes:
        adm.escrever(decisoes)

    aceites = []
    for x, d in zip(itens, decisoes):
        if d.resultado == adm.SIM:
            aceites.append(adm.pronto_para_inteligencia(x, d))
    # A ESCRITA E DO DONO DA ESPERA. Aqui so se diz o que foi admitido.
    recibo = espera.pousar(run_id, aceites)

    conta: dict = {}
    for d in decisoes:
        conta[d.resultado] = conta.get(d.resultado, 0) + 1
    # ── QUANTOS DOS JULGADOS TRAZIAM O CARIMBO DA PORTA ────────────────────
    # Sem este numero, mandar a lista ORIGINAL a admissao em vez da que saiu do
    # ingresso e uma troca invisivel: as duas tem o mesmo tamanho, os mesmos
    # campos e o mesmo aspecto no recibo. A diferenca e exactamente o que a
    # porta provou — e e isso que se conta aqui.
    #
    #     UMA TROCA QUE NAO MUDA NENHUM NUMERO NAO SE CONSEGUE VIGIAR.
    carimbados = sum(1 for x in itens
                     if isinstance(x, dict) and x.get("INGRESSO"))
    # ── O RECIBO DA FRONTEIRA, E ELE CORRE ─────────────────────────────────
    # ⚠️ A REGRA QUE O CAMINHO NAO CONSULTA NAO E UMA REGRA. Escrever o
    # contrato da fronteira em `coleta/ingresso.py` e nunca o perguntar aqui
    # repetiria exactamente o defeito que ele veio fechar — um campo perdido em
    # silencio, com o valor a existir.
    #
    #     REGRA ESCRITA NO ARTEFATO != REGRA EXECUTADA NO CAMINHO.
    #
    # E ele NAO decide nada: nao recusa item, nao muda veredito, nao preenche
    # campo. Conta o que atravessou e o que nao atravessou, e e no recibo que
    # a perda deixa de ser invisivel.
    #
    #     COLETAR != ADMITIR != JULGAR — E MEDIR NAO E NENHUM DOS TRES.
    fronteira = [ing.conferir_fronteira(x) for x in itens
                 if isinstance(x, dict)]
    em_falta = {}
    for f in fronteira:
        for c in f["EXIGIDOS_EM_FALTA"]:
            em_falta[c] = em_falta.get(c, 0) + 1
    ausentes = {}
    for f in fronteira:
        for c in f["AUSENTES"]:
            ausentes[c] = ausentes.get(c, 0) + 1
    return {"itens": len(itens), "por_resultado": conta, "prontos": len(aceites),
            "ficheiro": recibo["FICHEIRO"] or "",
            "espera": recibo["ESTADO"],
            "FRONTEIRA": {
                "CONTRATO": "STRUCTURED -> ADMISSION",
                "DONO": "coleta/ingresso.py::conferir_fronteira",
                "MEDIDOS": len(fronteira),
                "EXIGIDOS_EM_FALTA": em_falta,
                "TRANSPORTAVEIS_AUSENTES": ausentes,
                "COM_LINHAGEM": sum(1 for f in fronteira
                                    if f["LINHAGEM"] == "PRESENTE"),
                "A_LEI": ing.TEMPOS_QUE_NAO_SE_MISTURAM,
            }}

# O caminho do RUN-MANIFEST NAO vive aqui. Deixar a constante para tras seria
# deixar a porta destrancada: a proxima pessoa escreve `MANIFESTO.write_text` e
# o contrato volta a ser contornado sem ninguem reparar. O dono e
# `regras/proveniencia.py`, e o caminho e dele.


def agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versao_do_executor(caminho: str) -> str:
    """A versao e o commit que tocou o ficheiro pela ultima vez.

    NOT_PRESERVED era o que estava escrito nas corridas antigas — quer dizer
    «ninguem apontou». Com o commit ao lado, da para voltar exatamente ao codigo
    que produziu aquele numero.
    """
    r = subprocess.run(["git", "-C", str(RAIZ), "log", "-1", "--format=%h",
                        "--", caminho], capture_output=True, text=True)
    return (r.stdout.strip() or "NOT_PRESERVED") if r.returncode == 0 else "NOT_PRESERVED"


# ⚠️ A CORRIDA TINHA O SEGUNDO COMO GRANULARIDADE, E ISSO NAO E IDENTIDADE.
# Medido em `C-COLLECTION-OPERATIONAL-READINESS-OVERNIGHT-V1`, com cinco
# corridas concorrentes do mesmo alvo e do mesmo pais:
#
#     CORRIDAS_DISTINTAS = 1  ·  SUCCESS = 1  ·  ERROR = 4
#     duplicate key value violates unique constraint
#         "etapa_da_corrida_run_id_etapa_tentativa_..."
#
# As cinco nasceram no mesmo segundo e receberam O MESMO NOME. Quatro
# rebentaram na chave unica — e rebentar foi o BOM desfecho: o banco recusou.
# O mau desfecho e silencioso, e e o que acontece nas tabelas sem essa chave:
# as observacoes de uma corrida ficam atribuidas a outra, e ninguem ve.
#
#     DUAS COLETAS NO MESMO SEGUNDO NAO SAO A MESMA COLETA.
#     UM NOME QUE SE REPETE NAO E UM NOME.
#
# O QUE SE ACRESCENTOU, E POR QUE NAO E ENFEITE. O prefixo legivel fica —
# `pais`, `alvo` e o instante continuam a dizer o que dizem, e ha gente que le
# estes nomes. O que entra e um SUFIXO DE DESEMPATE, e ele nao carrega
# significado nenhum: nao se le de volta, nao se compara, nao se ordena por
# ele. Existe para que duas corridas do mesmo segundo sejam duas.
#
# NAO SE USOU O SEGUNDO COM MAIS CASAS SOZINHO: microsegundos reduzem a
# probabilidade e nao a fecham, e a coleta grande e exactamente onde o
# improvavel acontece. NAO SE USOU O PID: o mesmo processo corre varias
# corridas em fios. NAO SE PEDIU AO BANCO uma sequencia: a corrida nasce ANTES
# de qualquer escrita, porque a proveniencia e prospectiva — e uma identidade
# que so existe depois do primeiro INSERT nao serve para nomear o que vem
# antes dele.
#
# ⚠️ E O TAMANHO DO SUFIXO FOI MEDIDO, E NAO ESCOLHIDO A OLHO.
# A primeira versao usava tres bytes. Com 400 nomes gerados no mesmo instante
# houve UMA colisao — 400 contra 399 distintos. Tres bytes dao 16,7 milhoes de
# valores, e o paradoxo dos aniversarios come isso a uma velocidade que a
# coleta grande alcanca.
#
#     «IMPROVAVEL» NAO E «IMPOSSIVEL», E A COLETA GRANDE
#     E EXACTAMENTE ONDE O IMPROVAVEL ACONTECE.
#
# Oito bytes dao 1,8e19. Com vinte mil corridas no mesmo segundo a
# probabilidade de duas colidirem fica na ordem de 1e-11 — e isso ja nao e
# «pouco provavel»: e outra ordem de grandeza de risco. Criticar os
# microsegundos por reduzirem sem fechar e depois aceitar tres bytes seria
# aplicar duas reguas.
def novo_run_id(p: Pedido) -> str:
    pais = (p.filtros.get("pais") or "XX").upper()
    quando = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    return f"{pais}-{p.alvo}-{quando}-{secrets.token_hex(8)}"


def guardar_recibo(recibo: dict) -> None:
    """Entrega a corrida a quem e dono da procedencia. Nao escreve o ficheiro.

    ⚠️ ESTA FUNCAO ESCREVIA O MANIFESTO DIRECTAMENTE, e por isso o contrato nunca
    passava por aqui. O resultado esta medido no proprio ficheiro: das 20
    corridas, DEZ nao trazem `DATASET_ID`, `SOURCE_VERSION`, `RAW_EVIDENCE_PATH`
    nem `RAW_EVIDENCE_STATE`. Todas as dez sairam deste `write_text`.

        EXECUTAR A CORRIDA NAO E SER A AUTORIDADE SOBRE A PROCEDENCIA DELA.

    O orquestrador sabe o que correu, e continua a dize-lo. Quem escreve e
    `regras/proveniencia.py`, que e a peca que conhece a lei do manifesto — e
    que agora recusa palavra fora do contrato e confessa em `NOT_PRESERVED` o
    campo que nao veio, em vez de o deixar simplesmente ausente.
    """
    faltaram = pv.acrescentar(recibo)
    if faltaram:
        print("  · manifesto: %d campo(s) do contrato ficaram NOT_PRESERVED: %s"
              % (len(faltaram), ", ".join(faltaram)))


def correr(p: Pedido, so_plano: bool = False, seco: bool = False,
           so_a_porta: bool = False, memoria=None, banco_do_rastro=None,
           colheita_da_corrida: str = "", raiz_do_armazem=None) -> dict:
    """Do pedido ao recibo. Devolve o recibo, sempre — mesmo quando falha."""
    plano = resolver(p)

    if so_plano or not plano.da_para_correr:
        return {
            "RUN_ID": novo_run_id(p),
            "STATUS": "PLANO" if so_plano else "SEM_CAMINHO",
            "PEDIDO": p.para_json(),
            "MISSION": p.assunto,
            "COUNTRY": p.filtros.get("pais", "NAO SEI"),
            "FONTES_DO_ASSUNTO": len(plano.fontes_do_assunto),
            "FONTES_SEM_CAMINHO": len(plano.sem_caminho),
            "ERROR": "" if so_plano else plano.porque_nao(),
            "_plano": plano,
        }

    e = plano.executores[0]
    caminho = e["roda"][0]

    # ── NENHUM FILTRO DESAPARECE EM SILENCIO — BG-05 ────────────────────────
    # O pedido declarou um filtro; o executor escolhido nao o consome; ate
    # aqui, o valor simplesmente nao entrava no comando e ninguem sabia.
    # Medido: `T4 + fonte=IT-T4-001` abria o `regulatorio-eu` (que consome
    # `celex`), o `fonte` evaporava, e a corrida colhia `EU-T4-001` — outra
    # fonte, outro pais — com cara de sucesso.
    #
    #     PEDIDO ESPECIFICA FILTRO + EXECUTOR NAO SABE CONSUMIR
    #     = ERRO EXPLICITO, ANTES DA REDE. NUNCA SILENCIO.
    #
    # Quem declara o que consome e a receita do executor; quem consome
    # `pais`/`tema`/`fase` e o resolvedor. O que sobrar e recusa, com nome.
    sobras = sorted({k for k, v in p.filtros.items() if v not in (None, "")}
                    - set(FILTROS_DO_RESOLVEDOR) - filtros_consumidos(e))
    if sobras:
        return {
            "RUN_ID": novo_run_id(p),
            "STATUS": "FILTRO_NAO_CONSUMIDO",
            "PEDIDO": p.para_json(),
            "MISSION": p.assunto,
            "COUNTRY": p.filtros.get("pais", "NAO SEI"),
            "EXECUTOR_ESCOLHIDO": e.get("id", "NAO SEI"),
            "FILTROS_NAO_CONSUMIDOS": sobras,
            "ERROR": ("FILTRO_NAO_CONSUMIDO: o pedido declara %s e o executor "
                      "«%s» so consome %s. Nenhum executor de %s consome tudo "
                      "o que o pedido declarou; correr assim descartaria o "
                      "filtro em silencio, e foi exactamente assim que um "
                      "pedido de IT-T4-001 colheu EU-T4-001."
                      % (", ".join(sobras), e.get("id", "?"),
                         sorted(filtros_consumidos(e)) or "(nada)", p.alvo)),
            "_plano": plano,
        }

    # ── A CORRIDA NASCE AQUI, ANTES DE QUALQUER COISA CORRER ────────────────
    # ⚠️ O `RUN_ID` NASCIA OITO LINHAS DEPOIS DE O EXECUTOR JA TER CORRIDO.
    # O executor ia a fonte, trazia bytes, e so entao esta casa decidia como se
    # chamava a corrida que os trouxe. Enquanto o executor era mudo isso
    # passava despercebido; no dia em que um executor precisa de DIZER em nome
    # de que corrida colheu, deixa de passar.
    #
    #     PROVENIENCIA E PROSPECTIVA. Quem so a decide depois do facto
    #     nao a regista: reconstroi-a — e reconstrucao nao e testemunho.
    #
    # O nome nao mudou, nem o formato: mudou QUANDO se pergunta.
    run_id = novo_run_id(p)

    # o comando nasce do PEDIDO, nao de quem chama o orquestrador
    comando = list(e["roda"])
    valores = {**(e.get("filtros_por_omissao") or {}), **p.filtros}
    for nome in e.get("argumentos_de_filtros") or []:
        v = valores.get(nome)
        if v:
            comando.append(str(v))
    # OPT-IN, e declarado no registo. O executor que nao pede a corrida
    # continua a ser chamado com exactamente os mesmos argumentos de antes —
    # acrescentar isto a todos mudaria a linha de comando de quatro executores
    # que nunca a pediram.
    # ── OS FILTROS NOMEADOS ───────────────────────────────────────────────
    # `argumentos_de_filtros` manda valores POSICIONAIS, pela ordem. Um filtro
    # opcional nao cabe la: omiti-lo faz o seguinte ocupar o lugar dele.
    #
    #     UM ARGUMENTO OPCIONAL SEM NOME NAO E OPCIONAL: E UMA ARMADILHA.
    for nome in e.get("filtros_nomeados") or []:
        v = valores.get(nome)
        if v not in (None, ""):
            comando.append("--%s=%s" % (nome, v))
    if e.get("recebe_run_id"):
        comando.append("--run-id=%s" % run_id)
    inicio = agora()
    saida, erro, codigo = "", "", 0

    if seco or so_a_porta:
        # ensaio: prova o caminho inteiro sem gastar rede nem dinheiro.
        # `--so-a-porta` vai mais longe: nao colhe, mas leva a colheita QUE JA
        # EXISTE a peneira. E o que permite reprocessar quando a regra muda —
        # sem isto, mudar a regra obrigaria a coletar tudo outra vez, e ninguem
        # o faria; a regra nova valeria so para o que viesse depois.
        saida, codigo = ("(nao se colheu: so se levou a colheita a porta)"
                         if so_a_porta else
                         "(ensaio seco: o executor nao foi chamado)"), 0
    else:
        try:
            r = subprocess.run([sys.executable, *comando], cwd=str(RAIZ),
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=1800)
            saida, erro, codigo = r.stdout[-4000:], r.stderr[-2000:], r.returncode
        except Exception as ex:                                # noqa: BLE001
            erro, codigo = f"{type(ex).__name__}: {ex}", 1

    recibo = {
        "RUN_ID": run_id,
        # O CONTRATO FALA `SUCCESS`/`FAILED`. Isto dizia `OK`, e as tres
        # corridas com `STATUS: OK` no manifesto sao dai. Duas palavras
        # para o mesmo estado sao o mesmo defeito da autoria, um andar
        # abaixo. `ESTADO_DOS_ITENS` continua a falar COLHIDO/ERRO —
        # esse e outro campo e outra pergunta.
        "STATUS": "SUCCESS" if codigo == 0 else "FAILED",
        "PEDIDO": p.para_json(),
        "MISSION": p.assunto,
        "COUNTRY": p.filtros.get("pais", "NAO SEI"),
        "PLATFORM": ", ".join(e["rotas"]),
        "ACTOR": caminho,
        "ACTOR_VERSION": versao_do_executor(caminho),
        "CAPTURE_METHOD": e["custo"],
        "INPUT": p.filtros or {},
        "QUERY": p.em_uma_frase(),
        "COMANDO": " ".join(comando),
        "STARTED_AT": inicio,
        "FINISHED_AT": agora(),
        # Custo ZERO quando o executor nao foi chamado: uma passagem so pela
        # peneira nao abre ligacao nenhuma. Escrever «NAO SEI» aqui seria pior
        # que impreciso — o portao do padrao conta os «NAO SEI» como divida, e
        # eu estaria a inventar divida sobre uma corrida que nao gastou nada.
        "COST_USD": (0 if (seco or so_a_porta or e["custo"] == "gratuito")
                     else "NAO SEI"),
        "ITEM_COUNT_RAW": "NAO SEI",
        "ITEM_COUNT_NORMALIZED": "NAO SEI",
        "ERROR": erro.strip(),
        "ESTADO_DOS_ITENS": COLHIDO if codigo == 0 else ERRO,
        "FONTES_DO_ASSUNTO": len(plano.fontes_do_assunto),
        "FONTES_SEM_CAMINHO": len(plano.sem_caminho),
        "SAIDA": saida.strip()[-1500:],
        "_plano": plano,
    }

    # ── E A COLHEITA VAI A PORTA ────────────────────────────────────────────
    # O caminho so esta fechado aqui. Antes desta parte, o executor corria,
    # largava o que trouxe numa pasta, e ninguem ia buscar: a peneira existia e
    # nada passava por ela.
    envelope, notas = o_envelope(e, run_id)
    # ⚠️ REPROCESSAR NAO E COLHER, E A COLHEITA NAO E «A QUE ESTIVER LA».
    # `--so-a-porta` leva a peneira uma colheita que JA existe — e essa
    # colheita e de OUTRA corrida, a que a produziu. Enquanto o envelope viveu
    # num caminho fixo, isto funcionava por acidente: lia-se o ultimo que
    # tivesse sido escrito, fosse de quem fosse.
    #
    #     REPROCESSAR TEM DE DIZER O QUE REPROCESSA.
    #     «O ULTIMO QUE ESTAVA LA» NAO E UMA RESPOSTA.
    #
    # Entao o reprocessamento NOMEIA a corrida cuja colheita quer levar a
    # porta, e a corrida nova continua a ser nova: ela julga de novo, e as
    # decisoes sao dela. O que se reaproveita e o MATERIAL, e nao a corrida.
    de_quem = str(colheita_da_corrida or "").strip() or run_id
    itens, notas = a_colheita(e, de_quem)
    if colheita_da_corrida:
        notas = " · ".join(filter(None, [
            notas, "colheita reprocessada da corrida «%s» pela corrida «%s»"
                   % (colheita_da_corrida, run_id)]))
    recibo["COLHEITA_ENCONTRADA"] = len(itens)
    recibo["COLHEITA_NAO_ENCONTRADA"] = notas
    # O RETORNO FICA ESCRITO NO RECIBO, e nao so a contagem: quem audita
    # precisa de saber que ESPECIE veio, e nao apenas quantas linhas.
    recibo["RETORNO"] = {
        "ESTADO": envelope.get("ESTADO"),
        "COLHEITA": len(envelope.get("COLHEITA") or []),
        "SUPORTE": [x.get("ESPECIE") for x in (envelope.get("SUPORTE") or [])],
        "ERROS": envelope.get("ERROS") or [],
        "PORQUE_ZERO_COLHEITA": envelope.get("PORQUE_ZERO_COLHEITA"),
    }

    # ── E A COLHEITA ENTRA PELA PORTA, ANTES DE ALGUEM A JULGAR ─────────────
    # ⚠️ ATE AQUI, O QUE O EXECUTOR LARGAVA IA DIRECTO A ADMISSAO. A etapa RAW
    # existia, estava provada contra Postgres, e nunca corria: o item era
    # julgado sem nunca ter sido PRESERVADO, e sem passar pelo contrato comum
    # que `leis/artefato.py` escreveu exactamente para isto.
    #
    #     OBSERVAR NAO E PRESERVAR. PRESERVAR NAO E JULGAR.
    #
    # A porta responde «posso preservar esta observacao como RAW?». A admissao,
    # logo a seguir, responde outra pergunta: «isto pode entrar no universo?».
    # Sao duas perguntas, e agora sao duas etapas.
    # ⚠️ O ARMAZEM NASCE AQUI, E UM SO SERVE AS DUAS ETAPAS. O bruto e o
    # derivado sao dois bytes da mesma corrida; dois armazens dariam ao
    # derivado uma morada que o bruto nao conhece.
    # ⚠️ E A RAIZ DOS BYTES VEM DA PERSISTENCIA, NAO DA ARVORE. Medido em
    # 20/09/2026: com a memoria OPERACIONAL, os 107 objectos da Big
    # Collection 2 cairam em `<repo>/XX/` — residuo de medicao — e a suite
    # apagou-os. Sem raiz declarada (modo DESCARTAVEL/AUSENTE, provas), a
    # arvore continua a ser a raiz, exactamente como era.
    armazem = ing.ArmazemLocal(raiz_do_armazem or RAIZ)
    if itens and (so_a_porta or not seco):
        recibo["INGRESSO"] = pela_entrada(itens, recibo, memoria=memoria,
                                          banco_do_rastro=banco_do_rastro,
                                          armazem=armazem)

    # ── E O QUE FOI PRESERVADO ATRAVESSA PARA O DERIVED ────────────────────
    # ⚠️ ATE AQUI A ESTRADA PARTIA-SE NESTE PONTO EXACTO. Medido em
    # `provas/o_pedido_atravessa.py`: RAW aterrava, STORAGE ligava, e a
    # corrida seguia direita para a ADMISSAO — que recebia um documento sem
    # texto e respondia `NAO SEI`, com razao, porque ninguem o tinha derivado.
    #
    #     UMA ETAPA QUE CORRE DEPOIS DO BURACO NAO FECHA O BURACO.
    #
    # A ordem e a que a estrada canonica declara, e nao a que era comoda:
    # RAW -> STORAGE -> DERIVED, e so entao o resto.
    if itens and (so_a_porta or not seco):
        entrada = recibo["INGRESSO"]
        recibo["DERIVACAO"] = pela_derivacao(
            entrada.get("PARA_A_DERIVACAO") or [],
            run_id=recibo["RUN_ID"], armazem=armazem, memoria=memoria,
            banco_do_rastro=banco_do_rastro,
            source_id=entrada.get("FONTE_PROVADA"),
            nao_derivaveis=entrada.get("SEM_BYTES_PARA_DERIVAR") or [])

    # ── E O QUE FOI DERIVADO ATRAVESSA PARA O STRUCTURED ──────────────────
    # ⚠️ ATE AQUI A ESTRADA PARTIA-SE AQUI. O texto era extraido, guardado, e
    # a corrida seguia para a ADMISSAO com o item da ENTRADA — o documento sem
    # texto. A porta respondia NAO SEI, com razao.
    #
    # O dono deste degrau NAO e `conteudo`: essa e a casa do que uma
    # PLATAFORMA publica, e exige um canal que uma agencia com um sitio nao
    # tem. Ver `supabase/migrations/030_o_documento_ganha_registo.sql`.
    if itens and (so_a_porta or not seco):
        recibo["ESTRUTURACAO"] = pela_estruturacao(
            recibo.get("DERIVACAO") or {},
            run_id=recibo["RUN_ID"], armazem=armazem, memoria=memoria,
            source_id=(recibo.get("INGRESSO") or {}).get("FONTE_PROVADA"))

    if itens and (so_a_porta or not seco):
        # ⚠️ A PORTA JULGA O QUE ATRAVESSOU A FRONTEIRA MAIS RECENTE.
        # Quando houve STRUCTURED, e ele que vai — com o texto que o dono
        # guardou. Sem STRUCTURED, vai o que a porta de entrada aceitou, que
        # e o que havia antes desta missao.
        #
        #     A ADMISSAO JULGA O ITEM DA FRONTEIRA ANTERIOR,
        #     E NAO UM ITEM DE TRES ETAPAS ATRAS.
        estruturados = (recibo.get("ESTRUTURACAO") or {}).get("ESTRUTURADOS")
        if estruturados:
            fonte = (recibo.get("INGRESSO") or {}).get("FONTE_PROVADA")
            julgar = [item_documental_para_a_porta(e, source_id=fonte)
                      for e in estruturados]
        else:
            julgar = recibo["INGRESSO"].get("PARA_A_PORTA") or []
        # ── O UNIVERSO VEM DO PEDIDO, E NÃO DO ALVO ────────────────────────
        # ⚠️ AQUI ESTAVA `pela_porta(julgar, p.alvo, ...)`, e isso era um
        # campo EMPRESTADO. Medido no canário do YouTube: um pedido com
        # `alvo=T8` e `universo=T5` declarado pelo humano chegava à porta a
        # perguntar `T8` — que não tem régua escrita (só T3, T4, T5, T7 e T9
        # têm). A Admissão responderia `NAO_SE_APLICA` a um texto que nunca
        # seria julgado contra `T5`, e o relatório diria «testámos T5».
        #
        #     ALVO = PARA QUE SERVE a coleta · audiência, missão, finalidade.
        #     UNIVERSO = QUE PERGUNTA a porta faz ao conteúdo.
        #     ALVO != UNIVERSO.
        #
        # Funcionou durante meses por COINCIDÊNCIA: as corridas usavam alvos
        # (`T3`, `T4`, `T9`) cujos nomes por acaso existem como universos.
        #
        #     COINCIDIR POR HÁBITO NÃO É ESTAR LIGADO.
        #
        # É o irmão do §148: lá o universo nascia de um default silencioso;
        # aqui nascia de um campo vizinho. Nos dois casos a decisão de negócio
        # ficava sem autor — e a correção é a mesma, que é ter autor.
        #
        # SEM FALLBACK PARA `p.alvo`. Quem não declarar recebe a recusa do
        # dono canónico (`rota_forward_documento.universo_declarado`), que já
        # existe e já levanta `UniversoNaoDeclarado`. Uma segunda exceção com
        # a mesma função seria uma segunda lei.
        universo = universo_do_pedido(p)
        r = pela_porta(julgar, universo, recibo["RUN_ID"])
        recibo["ADMISSAO"] = r
        # ── UM FOSSIL DO SCRAP, RETIRADO — E A DIVIDA DELE, DECLARADA ───────
        # Aqui estava `pop("ENTRADOS")`. `ENTRADOS` era o segundo balde de
        # itens do SCRAP, e ele saiu na integracao: uma segunda lista a chegar
        # a quem julga e uma segunda porta da Collection, e so uma delas passa
        # pelo tradutor do texto.
        #
        # A INTENCAO dele era boa e NAO foi adoptada: «um recibo que carrega
        # todas as observacoes deixa de ser um recibo». Continua verdade para
        # `PARA_A_PORTA`. Mas esvazia-la aqui e mudanca de comportamento que
        # esta missao nao tem autorizacao para fazer, e ha consumidores.
        #
        #     DIVIDA DECLARADA E DIVIDA. DIVIDA CALADA E DEFEITO.
        recibo["ITEM_COUNT_RAW"] = r["itens"]
        recibo["ITEM_COUNT_NORMALIZED"] = r["prontos"]
        recibo["ESTADO_DOS_ITENS"] = ("PRONTO_PARA_INTELIGENCIA" if r["prontos"]
                                      else "NA_PORTA")
    return recibo


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    so_plano = "--so-plano" in sys.argv
    so_a_porta = "--so-a-porta" in sys.argv
    colheita_de = ""
    for _a in sys.argv[1:]:
        if _a.startswith("--colheita-da-corrida="):
            colheita_de = _a.split("=", 1)[1]
    seco = "--seco" in sys.argv and not so_a_porta
    # --filtro fase=posts --filtro plataforma=youtube
    extras = {}
    for i, a in enumerate(sys.argv):
        if a == "--filtro" and i + 1 < len(sys.argv) and "=" in sys.argv[i + 1]:
            k, v = sys.argv[i + 1].split("=", 1)
            extras[k.strip()] = v.strip()
    frase = " ".join(args) or "colete materiais de pesquisadores"

    try:
        p = de_uma_frase(frase)
        p.filtros.update(extras)
    except PedidoInvalido as ex:
        print(f"PEDIDO RECUSADO: {ex}")
        return 2

    # ── AS DEPENDÊNCIAS DE PERSISTÊNCIA NASCEM AQUI, ANTES DA CORRIDA ─────
    # ⚠️ ISTO CHAMAVA `correr()` SEM `memoria` E SEM `banco_do_rastro`, e o
    # replay canário pelo workflow real (run 35215565657, know-how §132)
    # mediu o preço: o workflow criava e migrava um Postgres descartável, o
    # portão da Sala aprovava-o, e a corrida nunca lhe escrevia uma linha —
    # `RAW_OBSERVATIONS` vazio, DERIVED e STRUCTURED por chamar, a Admissão a
    # responder NAO_SEI a um documento sem texto. A primeira coleta (§130)
    # passara por OUTRA porta: o corredor de prova ligava o banco em processo.
    #
    #     DEPENDÊNCIA DECLARADA != DEPENDÊNCIA LIGADA.
    #     A PORTA QUE A PROVA USOU NÃO É A PORTA QUE O WORKFLOW USA.
    #
    # Quem compõe é `orquestrador/persistencia.py`, a partir do ambiente e de
    # UMA variável (`BANCO_DESCARTAVEL_URL`), com a trava canónica de
    # `guarda/banco_descartavel.py`. Fail closed: variável presente e não
    # descartável recusa ANTES de a corrida nascer; variável ausente corre
    # sem memória e o recibo di-lo. Nunca se cai para produção.
    try:
        runtime = persistencia.dependencias_do_runtime()
    except (persistencia.BancoRecusado,
            persistencia.BancoOperacionalRecusado,
            persistencia.ModosEmConflito,
            ing.ArmazemOperacionalSemRaiz) as ex:
        print(str(ex))
        return 2

    recibo = correr(p, so_plano=so_plano, seco=seco, so_a_porta=so_a_porta,
                    colheita_da_corrida=colheita_de,
                    memoria=runtime.memoria,
                    banco_do_rastro=runtime.banco_do_rastro,
                    raiz_do_armazem=runtime.raiz_do_armazem)
    recibo["PERSISTENCIA"] = runtime.para_json()
    plano = recibo.pop("_plano")
    print(plano.em_palavras())
    print()

    if recibo["STATUS"] == "PLANO":
        print("(so o plano foi pedido; nada correu)")
        return 0
    if recibo["STATUS"] == "SEM_CAMINHO":
        print(f"NAO CORREU · {recibo['ERROR']}")
        return 1

    if not seco:
        guardar_recibo({k: v for k, v in recibo.items() if k != "SAIDA"})
    print(f"CORRIDA {recibo['STATUS']} · {recibo['RUN_ID']}")
    # A morada nunca traz utilizador nem senha: `morada_sem_segredo` só
    # devolve host:porto/banco. Ausência também se imprime — é informação.
    print(f"  persistencia: {runtime.ESTADO}"
          + (f" ({runtime.MORADA})" if runtime.MORADA else ""))
    print(f"  executor {recibo['ACTOR']} @ {recibo['ACTOR_VERSION']}")
    print(f"  de {recibo['STARTED_AT']} a {recibo['FINISHED_AT']}")
    if recibo["ERROR"]:
        print(f"  ERRO (nao e rejeicao): {recibo['ERROR'][:300]}")
    print(f"  colheita encontrada: {recibo.get('COLHEITA_ENCONTRADA', 0)} item(ns)")
    if recibo.get("COLHEITA_NAO_ENCONTRADA"):
        print(f"  NAO ENCONTREI O QUE ELE LARGOU: {recibo['COLHEITA_NAO_ENCONTRADA']}")
    a = recibo.get("ADMISSAO")
    if a and a["itens"]:
        print("  pela porta de admissao: "
              + " · ".join(f"{k} {v}" for k, v in sorted(a["por_resultado"].items())))
        if a["ficheiro"]:
            print(f"  prontos para a inteligencia: {a['prontos']} -> {a['ficheiro']}")
    if seco:
        print("  (ensaio seco: nada foi coletado e nada foi escrito no manifesto)")
    return 0 if recibo["STATUS"] == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
