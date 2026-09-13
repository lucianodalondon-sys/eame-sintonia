#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O ADAPTER DO SCRAP PARA A PORTA CANÔNICA — traduz, e mais nada.

    python3 coleta/scrap_colheita.py --run-id=<RUN_ID> --fonte=<SOURCE_ID> <FASE>

POR QUE ESTE FICHEIRO EXISTE
-----------------------------
Medido nesta árvore, antes desta missão:

    orquestrador/orquestrador.py    é o dono único da orquestração
    coleta/scrap_executor.py        é o executor canônico do SCRAP
    ARESTA ENTRE OS DOIS            NÃO EXISTIA

O SCRAP tinha uma porta (`COLLECT`), tetos, guarda de gasto e preservação de
RAW — e ninguém a chamava a partir de um `COLLECTION_REQUEST`. O disparador ia
direto a `coleta/social_scrap.py`, que corria `COLLECT` e parava ali: o que a
corrida colheu nunca chegava a `coleta/ingresso.py`, e portanto nunca chegava à
admissão.

    MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.

Este ficheiro é a aresta. Ele **não** é um segundo orquestrador: não decide que
missão correr, que fonte colher, que rota usar nem que ator chamar. Recebe uma
fase já decidida, chama `COLLECT` uma vez, e declara o que voltou.

    AS QUATRO TRADUÇÕES

      1  corre `scrap_executor.COLLECT` com o RUN_ID que o orquestrador cunhou
      2  lê o que a corrida devolveu — objetos e trace
      3  separa COLHEITA de SUPORTE pela espécie DECLARADA (COL-LAW-505)
      4  escreve o envelope no balcão, na língua da porta

    E O QUE ELE NÃO PODE FAZER

      cunhar RUN_ID · inventar SOURCE_ID · fabricar DOCUMENT_ID ·
      derivar RAW_OBSERVATION_ID · escolher ator, rota ou provider ·
      julgar tema, relevância ou qualidade

O `--run-id` É OBRIGATÓRIO, E O `--fonte` TAMBÉM
-------------------------------------------------
O primeiro, porque `RUN != PROVIDER RUN`: se este adapter cunhasse corrida, a
corrida do orquestrador e a da coleta eram duas, e o `raw_asset` ficaria ligado
a uma que o manifesto não conhece. É a mesma lei que `coleta/italy_executor.py`
já obedece.

O segundo, porque **o SCRAP não conhece `SOURCE_ID`**. Medido: o envelope
canônico de `coleta/social_envelope.py` tem `PLATFORM`, `SOURCE_ACCOUNT`,
`NATIVE_ID` e `URL` — e nenhum deles é uma fonte provada. Derivar `SOURCE_ID` de
qualquer um seria fabricar identidade.

    URL NÃO É SOURCE_ID. HANDLE NÃO É SOURCE_ID. PLATAFORMA NÃO É FONTE.

A identidade desce COM O PEDIDO, e nunca sobe da observação. Quem pede nomeia a
fonte do atlas; este adapter carimba-a e diz que a carimbou. Sem `--fonte`, ele
NÃO inventa: declara zero colheita, escreve porquê, e tudo o que a corrida
produziu sai como SUPORTE — que nunca atravessa a porta.

    O QUE NÃO SE DECLAROU NÃO ENTRA.

O BALCÃO NÃO É ARQUIVO
----------------------
`data/colheita/scrap/` é reescrito a cada corrida, e não acumulado — a mesma
escolha (e a mesma razão) de `coleta/italy_executor.py`: um balcão que guarda o
que já entregou entrega a colheita da corrida anterior outra vez.
"""
from __future__ import annotations

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', 'regras', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import retorno_da_coleta as rc                                    # noqa: E402
import scrap_executor as sx                                       # noqa: E402

EXECUTOR_ID = 'scrap-colheita'
EXECUTOR_VERSION = 'adapter-v1'

BALCAO = os.path.join('data', 'colheita', 'scrap')
ENVELOPE = os.path.join(BALCAO, 'ENVELOPE.json')

#: As fases que este adapter sabe pedir ao `COLLECT`. O nome vem do disparador;
#: a plataforma, a capacidade e os argumentos vivem AQUI, em Python versionado.
#:
#:     UM DISPARADOR QUE ESCOLHE A CAPACIDADE ESCOLHE O QUE SE COLHE.
#:
#: E CADA FASE DIZ QUE ESPECIE DE RETORNO PRODUZ — quarta posicao, OBRIGATORIA,
#: sem valor por omissao. Chegou da LINKEDIN-OP-01, e e o campo que a
#: `leis/retorno_da_coleta.py` nasceu a dizer que faltava.
#:
#:     UMA ESPECIE POR OMISSAO E UMA DECISAO QUE NINGUEM TOMOU.
FASES = {
    'janela':         ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'tudo'}, rc.COLHEITA),
    'janela-perfis':  ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'perfis'}, rc.COLHEITA),
    'janela-objetos': ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'objetos'}, rc.COLHEITA),

    # ── A IDENTIDADE DO LINKEDIN, E POR QUE ELA E CATALOGO ─────────────────
    # Esta fase le o site DA PROPRIA ORGANIZACAO e traz de la o endereco que a
    # organizacao publicou. O que ela devolve nao e uma observacao da fonte: e
    # uma ENTIDADE DE ONDE SE PODE COLHER — a definicao literal de `CATALOG`.
    #
    #     IDENTITY != CONTENT. UM ENDERECO NAO E UMA PUBLICACAO.
    #     E `ENTRAM_NO_INGRESSO = (COLHEITA,)`: CATALOGO NAO ATRAVESSA A PORTA.
    #
    # O terminal canonico desta fase e o ENVELOPE, na lista de SUPORTE — e nao
    # a Sala de Espera. Empurra-la para a Admissao completava uma seta no
    # desenho e metia gasolina na mangueira da agua.
    'identidade-linkedin': ('LINKEDIN', 'linkedin.identity.discovery', {}, rc.CATALOG),
    # ── O CANARIO DA RELEASE V1 ────────────────────────────────────────────
    # As tres fases acima correm `instagram.profile.discovery`, que a
    # `scrap_capacidades.py` declara `PARTIAL` e `LOCAL/DATACENTER_BLOCKED`:
    # ela precisa de maquina residencial e nao corre de um datacenter. Medido,
    # nao presumido — e por isso a unica fase que o caminho canonico sabia
    # pedir era uma que este ambiente nao consegue executar.
    #
    #     UMA ARVORE QUE SO SABE PEDIR O QUE NAO CONSEGUE CORRER
    #     NAO SE CONSEGUE PROVAR A CORRER.
    #
    # `bluesky.author.incremental` e o oposto em todos os eixos que a escolha
    # do canario pesa: `PROVEN` com trial ao vivo citado, `ONLINE`, gratuita,
    # sem credencial, sem navegador autenticado e sem fornecedor pago. O
    # adaptador, o registo da rota e a linha da matriz ja existiam todos antes
    # desta missao — o que faltava era a fase que os pede.
    #
    #     ISTO NAO ABRE PLATAFORMA NENHUMA. A PLATAFORMA JA ESTAVA ABERTA;
    #     O QUE NAO EXISTIA ERA A ARESTA DO PEDIDO ATE ELA.
    'canario-bluesky': ('BLUESKY', 'bluesky.author.incremental', {'limit': 1},
                        rc.COLHEITA),
}

#: Que filtros NOMEADOS cada fase aceita, e so ela. O orquestrador traduz
#: `filtros_nomeados` da receita em `--nome=valor`, e sem uma lista por fase um
#: nome que a rota nao conhece chega la dentro e morre no `**_` do adaptador,
#: em silencio, com a corrida a dar verde.
#:
#:     UM ARGUMENTO QUE A ROTA ENGOLE SEM USAR NAO E OPCIONAL: E UMA ARMADILHA.
#:
#: Entao um nome fora da lista da fase RECUSA a corrida, e diz qual era a lista.
#: Fail closed: o silencio nao autoriza.
#: A forma e `{fase: {nome publico: nome que a rota recebe}}`. Os dois lados sao
#: quase sempre iguais — e quando nao sao, a traducao mora AQUI, a vista, e nao
#: escondida num `if fase ==` la dentro.
#:
#:     UMA TRADUCAO QUE NAO SE VE E UMA TRADUCAO QUE NINGUEM CONFERE.
NOMEADOS = {
    'janela':          {'teto': 'teto'},
    'janela-perfis':   {'teto': 'teto'},
    'janela-objetos':  {'teto': 'teto'},
    # `handle` e o ENDERECO da observacao, e nunca a identidade da fonte. Ele
    # diz A QUE CONTA se vai bater; `--fonte` diz DE QUE FONTE PROVADA o
    # pedido fala. Sao dois campos porque sao duas coisas.
    #
    #     HANDLE NAO E SOURCE_ID. Derivar um do outro seria fabricar identidade.
    'canario-bluesky': {'handle': 'handle'},
    # `site` e o endereco do site DA ORGANIZACAO, de onde se le o handle que
    # ela propria publicou. Nao e o SOURCE_ID, e nao e o handle: e onde se vai
    # perguntar. A rota chama-lhe `site_url`, e a traducao e esta linha.
    'identidade-linkedin': {'site': 'site_url'},
}

#: O que o envelope canônico do SCRAP responde, com o nome que a porta usa.
#: `coleta/ingresso.py::DO_COLETOR` tem treze campos; o SCRAP responde a estes,
#: e os outros chegam em falta — e a porta escreve «NAO SEI», que é honesto.
#:
#:     TRADUZIR NOME E FORMA É TRABALHO DE ADAPTER.
#:     PREENCHER UM CAMPO QUE A OBSERVAÇÃO NÃO TROUXE NÃO É.
DO_SCRAP_PARA_A_PORTA = {
    'URL': 'SOURCE_URL',
    'COUNTRY_SCOPE': 'COUNTRY_SCOPE',
    'SOURCE_LOCATION': 'SOURCE_LOCATION',
    'LANGUAGE': 'ITEM_LANGUAGE',
    'PUBLISHED_AT': 'PUBLISHED_AT',
    'COLLECTED_AT': 'OBSERVED_AT',
}

DESCONHECIDO = 'UNKNOWN'

#: O valor de nascenca de `COST_STATE` em `coleta/social_rotas.py`: a rota nao
#: correu. So quem corre o sobrescreve.
NAO_CORREU = 'NOT_RUN'


def _limpo(v):
    """→ o valor, ou None quando ele é uma confissão de ausência."""
    s = str(v or '').strip()
    return None if not s or s in (DESCONHECIDO, rc.NAO_SEI) else v


def unidade(objeto, *, run_id, fonte):
    """Um objeto do SCRAP na língua da porta. → a unidade de COLHEITA.

    `DOCUMENT_ID` sai `NAO SEI` de propósito e por lei: o SCRAP não tem
    identidade documental para dar, e um identificador tirado do `sha` ou do
    caminho seria uma mentira com forma de dado.

        UNKNOWN PERMANECE UNKNOWN.
    """
    fora = {'ESPECIE': rc.COLHEITA, 'RUN_ID': run_id, 'SOURCE_ID': fonte,
            'DOCUMENT_ID': rc.NAO_SEI}
    for de, para in DO_SCRAP_PARA_A_PORTA.items():
        v = _limpo(objeto.get(de))
        if v is not None:
            fora[para] = v
    # O corpo da observação viaja inteiro: a porta assina o que recebeu, e
    # normalizar aqui faria a impressão digital ser de outra coisa.
    #
    #     RAW BEFORE NORMALIZATION.
    fora['OBSERVACAO'] = objeto
    # Sem ficheiro separado: a observação É o item, e isso diz-se.
    fora['PAYLOAD'] = {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA}
    return fora


def suporte_do_trace(trace):
    """O que a corrida produziu e que NÃO é colheita. → lista de suporte.

    O trace é a prova da execução — é `RUN_RECEIPT`, e nunca observação.
    Declará-lo aqui é o que impede que ele entre pela porta por distração.

        O RECIBO DE UMA COLHEITA NÃO É A COLHEITA.
    """
    return [{'ESPECIE': rc.RUN_RECEIPT, 'ONDE': '',
             'O_QUE_E': 'o trace da corrida do SCRAP: rota escolhida, estado, '
                        'tetos e custo. Prova da execução, não material observado.',
             'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA},
             'RESUMO': resumo_do_trace(trace)}]


#: Os eixos que o recibo leva, e por que sao estes.
#:
#: ⚠️ MEDIDO NA SCRAP-MORNING-01, no portao §2B. A NIGHT-SHIFT-01 consertou o
#: TRACE — sem Chrome, `instagram.profile.discovery` passou a dizer
#: `EXECUTOR_UNAVAILABLE` em vez de `UNKNOWN_ERROR`. Mas o recibo que atravessa
#: para quem le carregava CINCO chaves, e nenhuma delas era a recuperacao nem a
#: frase. Quem lesse o envelope via um estado sem saber de quem era a culpa nem
#: o que fazer a seguir:
#:
#:     RESULT EXECUTOR_UNAVAILABLE  ·  e mais nada
#:
#: Um estado que sabe, num recibo que nao o leva, volta a ser «nao sei» para
#: quem le.
#:
#:     CONSERTAR O TRACE E CONSERTAR O TRACE.
#:     O QUE ATRAVESSA E O RECIBO.
#:
#: Os quatro eixos novos nao sao inventados aqui: `leis/falhas.py` ja os deriva
#: todos a partir do estado canonico, e `social_rotas.selar()` ja os escreve.
#: Este ficheiro so deixa de os deitar fora.
EIXOS_DO_RECIBO = (
    'RESULT',                 # o estado canonico
    'EXECUTOR_ID',
    'EXECUTION_MODE',
    'NETWORK_REQUESTS_USED',
    'COST_STATE',             # NOT_RUN != COST 0
    'FAILURE_LAYER',          # de quem e a culpa — ROTA CAIDA NAO E FONTE CAIDA
    'RECOVERY_ACTION',        # o que fazer a seguir
    'NATIVE_REASON',          # o nome nativo, de maquina
)


def resumo_do_trace(trace):
    """O que o recibo leva de uma corrida. → o resumo, sem nada inventado.

    A frase de gente viaja ao lado dos nomes, e nunca dentro deles:

        STATE          o estado canonico       EXECUTOR_UNAVAILABLE
        NATIVE_REASON  o nome, de maquina      BROWSER_NOT_REACHED
        PORQUE         a frase, de gente       «sem Chrome nesta maquina: ...»

    UM NOME E UMA FRASE NAO CABEM NO MESMO CAMPO.

    A frase vem de `ROUTER_RECORD.ERRO`, que `social_rotas` ja REDIGIU — um
    traceback de `urllib` carrega a URL, e a URL pode carregar o token. Copia-la
    de outro sitio seria copia-la por redigir.
    """
    resumo = {k: trace.get(k) for k in EIXOS_DO_RECIBO if k in trace}
    porque = ((trace.get('ROUTER_RECORD') or {}).get('ERRO'))
    if porque:
        resumo['PORQUE'] = porque
    return resumo


def colher(fase, *, run_id, fonte, banco=None, **extra):
    """Uma fase, uma corrida do `COLLECT`. → o envelope do COL-LAW-505.

    NÃO levanta por rota recusada: recusa é resultado de medição, e desce como
    estado. O envelope diz o que a corrida devolveu — inclusive «nada, e porquê».
    """
    plataforma, capacidade, fixos, especie = FASES[fase]
    objetos, trace = sx.COLLECT(platform=plataforma, capability=capacidade,
                                run_id=run_id, banco=banco,
                                **dict(fixos, **extra))
    objetos = objetos or []
    estado = rc.SUCCESS if trace.get('RESULT') in (None, 'OK', 'SUCCESS') else rc.PARTIAL
    erros = []
    porque_zero = ''

    # ── UMA ROTA QUE NAO CORREU NAO OBSERVOU NADA ──────────────────────────
    # ⚠️ MEDIDO NA NIGHT-SHIFT-01, e reproduzido antes de corrigido:
    #
    #     instagram.reel.capture · RESULT = ROUTE_NOT_ALLOWED
    #     PROVIDER_USED = None  ·  COST_STATE = NOT_RUN
    #     -> e mesmo assim UM objeto voltava, e virava UMA unidade de COLHEITA
    #        carimbada com um SOURCE_ID verdadeiro.
    #
    # O objeto era um esqueleto: todos os campos em `NOT_KNOWN`. Ele nasce de
    # proposito — a cadeia de Reel distingue REUSAR de ADQUIRIR e devolve o que
    # sabe mesmo quando a aquisicao e recusada, o que esta certo LA. O que
    # estava errado era aqui: quem decide o que e COLHEITA e este ficheiro, e
    # ele contava o esqueleto como observacao.
    #
    #     UMA ROTA QUE NAO CORREU NAO OBSERVOU NADA.
    #     UM ESQUELETO COM SOURCE_ID E UMA OBSERVACAO FABRICADA.
    #
    # O sinal nao e o estado de falha — uma rota que colheu dez e depois levou
    # `RATE_LIMITED` colheu dez de verdade. O sinal e o do dono do custo, que
    # nasce `NOT_RUN` e so quem corre sobrescreve:
    #
    #     NOT_RUN != COST 0. UNKNOWN COST != COST 0.  (`coleta/social_rotas.py`)
    if objetos and trace.get('COST_STATE') == NAO_CORREU:
        suporte = suporte_do_trace(trace) + [
            {'ESPECIE': rc.ESPECIE_DESCONHECIDA, 'ONDE': '',
             'O_QUE_E': 'o que a rota devolveu sem ter corrido: %s'
                        % (trace.get('RESULT') or 'sem estado'),
             'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA},
             'QUANTOS': len(objetos)}]
        return {
            'RUN_ID': run_id, 'EXECUTOR_ID': EXECUTOR_ID,
            'EXECUTOR_VERSION': EXECUTOR_VERSION, 'ESTADO': rc.PARTIAL,
            'COLHEITA': [], 'SUPORTE': suporte, 'ERROS': erros,
            'FASE': fase, 'PLATFORM': plataforma, 'CAPABILITY': capacidade,
            'ESPECIE_DA_FASE': especie,
            'SOURCE_ID_DO_PEDIDO': fonte or rc.NAO_SEI,
            'PORQUE_ZERO_COLHEITA': (
                'a rota nao correu (COST_STATE=%s, RESULT=%s) e, mesmo assim, '
                'devolveu %d objeto(s). Eles NAO sao observacoes: saem por '
                'SUPORTE. Uma rota que nao correu nao observou nada, e um '
                'esqueleto carimbado com SOURCE_ID seria observacao fabricada.'
                % (NAO_CORREU, trace.get('RESULT'), len(objetos))),
        }

    if especie != rc.COLHEITA:
        # ── A FASE DECLAROU QUE NAO PRODUZ COLHEITA, E ISSO E UM FACTO ──────
        # `ENTRAM_NO_INGRESSO = (COLHEITA,)`. Esta fase devolve uma entidade DE
        # ONDE SE PODE COLHER, nao material observado — entao ela sai por
        # SUPORTE, com a especie escrita, e a COLHEITA fica vazia porque e
        # vazia. Zero aqui nao e falha nem e ausencia de dados: e a especie.
        #
        #     UM ZERO QUE VEM DA ESPECIE NAO SE LE COMO UM ZERO QUE VEM DA FONTE.
        #
        # E nao se escolhe por `if plataforma == ...`: escolhe-se pelo que a
        # fase DECLAROU em `FASES`, que e o unico sitio onde isso se decide.
        suporte = suporte_do_trace(trace) + [
            {'ESPECIE': especie, 'ONDE': '',
             'O_QUE_E': 'o que esta fase produz, pela especie que ela declara: '
                        '%s de %s/%s' % (especie, plataforma, capacidade),
             'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA},
             'QUANTOS': len(objetos),
             'ITENS': objetos}]
        return {
            'RUN_ID': run_id, 'EXECUTOR_ID': EXECUTOR_ID,
            'EXECUTOR_VERSION': EXECUTOR_VERSION, 'ESTADO': estado,
            'COLHEITA': [], 'SUPORTE': suporte, 'ERROS': erros,
            'FASE': fase, 'PLATFORM': plataforma, 'CAPABILITY': capacidade,
            'ESPECIE_DA_FASE': especie,
            'SOURCE_ID_DO_PEDIDO': fonte or rc.NAO_SEI,
            'PORQUE_ZERO_COLHEITA': (
                'esta fase produz %s, e nao COLHEITA. So %s atravessa o '
                'ingresso, entao %d resultado(s) sairam por SUPORTE com a '
                'especie declarada. IDENTITY != CONTENT: um endereco de conta '
                'nao e uma observacao dela, e empurra-lo para a Admissao seria '
                'falsa colheita.'
                % (especie, ', '.join(rc.ENTRAM_NO_INGRESSO), len(objetos))),
        }

    if not fonte:
        # ── SEM FONTE PROVADA NÃO HÁ COLHEITA, E ISSO NÃO É UM ERRO ────────
        # É a resposta certa. O SCRAP não sabe de que fonte do atlas veio o que
        # colheu, e inventá-la seria fabricar identidade.
        porque_zero = (
            'o pedido não nomeou fonte. O SCRAP observa PLATAFORMAS e a porta '
            'fala em FONTES; sem o SOURCE_ID vindo do pedido, estas %d '
            'observações são CANDIDATAS e não observações de uma fonte provada. '
            'URL não é SOURCE_ID.' % len(objetos))
        colheita = []
        suporte = suporte_do_trace(trace) + [
            {'ESPECIE': rc.ESPECIE_DESCONHECIDA, 'ONDE': '',
             'O_QUE_E': 'o que a corrida observou, sem fonte provada que o ancore',
             'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA},
             'QUANTOS': len(objetos)}]
    else:
        colheita = [unidade(o, run_id=run_id, fonte=fonte) for o in objetos]
        suporte = suporte_do_trace(trace)
        if not colheita:
            porque_zero = ('a corrida correu e não observou nada. ZERO LEGÍTIMO '
                           'NÃO É FALHA: %s' % (trace.get('RESULT') or 'sem estado'))

    envelope = {
        'RUN_ID': run_id, 'EXECUTOR_ID': EXECUTOR_ID,
        'EXECUTOR_VERSION': EXECUTOR_VERSION, 'ESTADO': estado,
        'COLHEITA': colheita, 'SUPORTE': suporte, 'ERROS': erros,
        'FASE': fase, 'PLATFORM': plataforma, 'CAPABILITY': capacidade,
        'ESPECIE_DA_FASE': especie,
        'SOURCE_ID_DO_PEDIDO': fonte or rc.NAO_SEI,
    }
    if porque_zero:
        envelope['PORQUE_ZERO_COLHEITA'] = porque_zero
    return envelope


def escrever(envelope, raiz=RAIZ):
    alvo = os.path.join(raiz, BALCAO)
    os.makedirs(alvo, exist_ok=True)
    caminho = os.path.join(raiz, ENVELOPE)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(json.dumps(envelope, ensure_ascii=False, indent=1,
                           sort_keys=True) + '\n')
    return caminho


def main(argv=None):
    args = list(argv if argv is not None else sys.argv[1:])
    run_id = fonte = None
    nomeados = {}
    resto = []
    for a in args:
        if a.startswith('--run-id='):
            run_id = a.split('=', 1)[1].strip()
        elif a.startswith('--fonte='):
            fonte = a.split('=', 1)[1].strip() or None
        elif a.startswith('--') and '=' in a:
            # Um filtro nomeado qualquer. Nao se julga aqui se ele serve: a
            # fase ainda nao esta escolhida, e julgar antes de saber a fase
            # seria julgar contra a lista errada. Vazio = nao foi dado, e isso
            # e um valor (o teto vazio quer dizer «sem teto»).
            k, v = a[2:].split('=', 1)
            v = v.strip()
            if v:
                nomeados[k.strip().replace('-', '_')] = v
        else:
            resto.append(a)
    # Os filtros chegam POSICIONAIS, sem nome: e assim que o orquestrador
    # traduz `argumentos_de_filtros` para linha de comando, e e assim que o
    # `comunicacao-publica` ja os recebe. A ordem esta na receita.
    if resto and resto[0] in FASES:
        fase = resto[0]
        if fonte is None and len(resto) > 1:
            fonte = resto[1].strip() or None
    else:
        fase = resto[0] if resto else 'janela'
    if fase not in FASES:
        print('FASE_DESCONHECIDA=%s · as que existem: %s'
              % (fase, ', '.join(sorted(FASES))))
        return 2
    # ── AGORA SIM: A FASE ESTA ESCOLHIDA, E A LISTA DELA E QUE JULGA ───────
    aceites = NOMEADOS.get(fase, ())
    sobra = sorted(k for k in nomeados if k not in aceites)
    if sobra:
        print('FILTRO_NAO_ACEITE_NESTA_FASE=%s · a fase «%s» aceita: %s'
              % (', '.join(sobra), fase, ', '.join(aceites) or 'nenhum'))
        return 2
    falta = sorted(k for k in aceites if k not in nomeados and k != 'teto')
    if falta:
        # Um alvo em falta NAO se inventa a partir da fonte nem do nome da
        # fase. Sem ele nao ha a que bater, e isso diz-se antes de a corrida
        # comecar — e nao depois, com zero objetos e uma razao adivinhada.
        print('FILTRO_EM_FALTA=%s · a fase «%s» precisa dele para saber a que '
              'conta bater, e o adapter nao o deriva de --fonte' % (', '.join(falta), fase))
        return 2
    if not run_id:
        # Cunhar um aqui daria DUAS corridas canônicas para o mesmo acto.
        print('SEM_RUN_ID=o orquestrador é quem cunha a corrida; este adapter '
              'não a inventa')
        return 2

    # Os nomes publicos viram os nomes que a rota recebe, pela tabela da fase.
    envelope = colher(fase, run_id=run_id, fonte=fonte,
                      **{aceites[k]: v for k, v in nomeados.items()})
    caminho = escrever(envelope)
    mal = rc.conferir(envelope, RAIZ)

    print('SCRAP_COLHEITA')
    print('  fase          %s' % fase)
    print('  run_id        %s' % run_id)
    print('  source_id     %s' % (fonte or rc.NAO_SEI))
    print('  especie       %s' % envelope.get('ESPECIE_DA_FASE', rc.COLHEITA))
    for k in sorted(aceites):
        print('  %-13s %s' % (k, nomeados.get(k) or ('sem teto' if k == 'teto'
                                                     else rc.NAO_SEI)))
    print('  colheita      %d' % len(envelope['COLHEITA']))
    print('  suporte       %d' % len(envelope['SUPORTE']))
    print('  envelope      %s' % os.path.relpath(caminho, RAIZ))
    if envelope.get('PORQUE_ZERO_COLHEITA'):
        print('  porque zero   %s' % envelope['PORQUE_ZERO_COLHEITA'])
    for m in mal:
        print('  CONTRATO      %s' % m)
    return 0 if not mal else 1


if __name__ == '__main__':
    sys.exit(main())
