#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A RECEITA — como se atende um pedido, sem que quem pede precise de saber.

O conhecimento de «como se coleta ciencia italiana» estava espalhado por
cabecalho de script, README, prompt de aba e `if` solto dentro do coletor.
Espalhado assim, ele nao se consulta: redescobre-se. E redescobrir custa uma
coleta inteira de cada vez.

Aqui ele fica num sitio so, e — isto e o essencial — **derivado, nao escrito**:

    o assunto pedido (T7)
        -> as fontes que o atlas ja classificou nesse territorio
        -> a rota que a ficha de cada fonte declara
        -> o executor que sabe percorrer essa rota
        -> os contratos que ele e obrigado a cumprir
        -> o que se espera de volta

Se amanha alguem escrever a ficha de uma fonte nova, ela entra na receita
sozinha. Nao ha lista para atualizar a mao — listas a mao envelhecem caladas.

O NAO SEI E O PRODUTO MAIS IMPORTANTE DAQUI
-------------------------------------------
O censo mediu: **35 das 54 fontes italianas tem `access_method: NAO SEI`**. A
ficha diz que a fonte existe e o que ela tem, mas nao diz como se chega la.

Um planeador honesto nao pode esconder isso. Se o pedido tocar 12 fontes e a
casa souber percorrer 3, o plano diz «3 de 12», e nomeia as outras 9. A
alternativa — devolver so as 3 e calar as 9 — faz uma coleta parcial parecer
completa, que e o erro mais caro que este sistema pode cometer.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — poe as gavetas no caminho de importacao

from pedido import Pedido, ALVOS  # noqa: E402

FONTES_MEDIDAS = RAIZ / "system-map" / "data" / "sources.generated.json"

# ── OS EXECUTORES QUE A CASA TEM, E O QUE CADA UM SABE PERCORRER ────────────
# Isto e a unica lista escrita a mao deste ficheiro, e e curta de proposito:
# sao 18 executores medidos pelo censo, e so estes declaram saber percorrer uma
# rota inteira ate ao fim. Cada linha diz o que o executor faz e como se chama
# — nunca o chamador precisa de saber isto.
#
# Um executor entra aqui quando prova que percorre a rota; sai quando deixa de
# a percorrer. Nao ha «talvez».
# ── O QUE CADA EXECUTOR DEVOLVE, E O QUE ISSO E ─────────────────────────────
# `larga_em` diz ONDE. A chave `retorno` diz O QUE — e e a COL-LAW-505 a entrar
# no runtime.
#
#     ENVELOPE   o ficheiro onde a CORRIDA declara o que produziu.
#                E a unica origem possivel de COLHEITA.
#
#     LEGADO     {caminho: ESPECIE} para o que ja esta em disco e cujo produtor
#                nao corre offline. SO PODE DECLARAR SUPORTE: manifesto,
#                catalogo, recibo de execucao ou plano.
#
# ⚠️ POR QUE O LEGADO NAO PODE DECLARAR COLHEITA. Uma declaracao escrita aqui e
# feita ANTES da corrida e envelhece sozinha — o proprio `larga_em` prova isso,
# com dois caminhos a apontar para pastas que nao existem sem ninguem notar. Se
# esta chave pudesse dizer «aqui ha colheita», uma linha desactualizada mandava
# suporte para o ingresso outra vez, e teriamos trocado uma heuristica por um
# literal. `leis/retorno_da_coleta.py::envelope_do_legado` recusa, e escreve o
# motivo no recibo.
#
#     DECLARAR SUPORTE E INOFENSIVO MESMO QUANDO ERRADO: SUPORTE NAO ATRAVESSA.
#     DECLARAR COLHEITA NAO E — E POR ISSO NAO SE PODE.
EXECUTORES = {
    # ⚠️ ESTE REGISTO MUDOU DE CHAVE, E A MUDANCA E UM CONSERTO DE VERDADE.
    # Estava em `"T7"` porque `pedido/pedido.py` declarava `T7 = «Ciencia e
    # ensaio»`. No Atlas — que e o dono — `T7` e TECHNICAL NETWORK, e as doze
    # fontes italianas classificadas la sao COOPERATIVAS E CONSORCIOS. Pedir
    # ciencia mandava este coletor cientifico correr sobre cooperativas.
    #
    # A chave certa nao e `T5` (SCIENCE) e sim `T6` (RESEARCHERS), e o criterio
    # nao e gosto: e a separacao que o proprio Atlas impoe e que o
    # `ITALY-SOURCE-MASTER-V1.json` repete —
    #
    #     TERRITORY = o que a rota MEDE.  ACCESS_METHOD = como se acessa.
    #
    # O que esta rota MEDE esta escrito no `retorno` dela, e foi contado: doze
    # fichas de PESSOA, zero unidades de obra. Ela mede pesquisadores. Que o
    # faca atraves de registos cientificos (OpenAlex, ORCID, que sao T5) e a
    # rota, e rota nao e territorio — confundir os dois foi exactamente o que
    # produziu esta colisao.
    #
    # ⚠️ E ISTO DEIXA `T5` SEM EXECUTOR, O QUE E A VERDADE E NAO UM BURACO NOVO.
    # As seis fontes de SCIENCE em ficha — `IT-T5-001..005` e `EU-T5-001` —
    # nunca tiveram executor nesta casa; tinham um coletor a correr sobre as
    # fontes ERRADAS e ninguem via. O plano passa a dizer «NAO SEI COMO», que e
    # o que sempre foi verdade.
    #
    #     UM BURACO QUE APARECE NAO E UM BURACO NOVO: E UM BURACO QUE ERA CEGO.
    "T6": [{
        "id": "corpus-pesquisador",
        # F3 · o retorno e o CATALOGO das pessoas de quem se PODE colher
        # obra — nao as obras. Medido: 12 fichas de pessoa, zero unidades.
        "retorno": {"LEGADO": {
            "data/samples/RESEARCHER-CORPUS-EAME-V1.json": "CATALOG"}},
        "roda": ["coleta/corpus_pesquisador.py", "coletar"],
        # ONDE ELE LARGA o que traz. Sem isto declarado, o orquestrador corre o
        # executor e fica sem saber o que procurar — e a colheita nunca chega a
        # porta de admissao. Foi o que se descobriu ao perguntar «o que o YouTube
        # colhe vai para onde?»: ia para uma pasta que ninguem lia.
        "larga_em": ["data/samples/RESEARCHER-CORPUS-EAME-V1.json"],
        "rotas": ["OpenAlex", "ORCID"],
        "o_que_traz": "obra publicada com data, tipo, veiculo e DOI, e a autoria "
                      "declarada obra a obra",
        "custo": "gratuito",
    }],
    "T4": [{
        # ⚠️ ESTE EXECUTOR ENTROU A FRENTE DO `rotulos-oficiais`, E NAO NO
        # LUGAR DELE. O orquestrador corre `plano.executores[0]`, e a ordem
        # desta lista e portanto uma DECISAO, nao arrumacao.
        #
        # O censo das classes mediu que T4 estava a UMA peca de atravessar a
        # Collection inteira — tinha regra de admissao e dono STRUCTURED, e
        # nao tinha aquisicao canonica. O `rotulos-oficiais` nao a podia dar:
        # declara `LEGADO/MANIFEST` (suporte, que nunca atravessa) e a fonte
        # dele nao verifica TLS deste ambiente.
        #
        #     UM EXECUTOR QUE NAO PODE DECLARAR COLHEITA
        #     NAO E UM EXECUTOR MAU: E OUTRO TRABALHO.
        #
        # O `rotulos-oficiais` FICA: ele indexa 163 rotulos e esse indice tem
        # valor. Sai da frente porque nao colhe — nao porque nao sirva.
        "id": "regulatorio-eu",
        # F1 · a corrida DECLARA o que produziu. Origem legitima de COLHEITA.
        "retorno": {"ENVELOPE": "data/colheita/eu-regulatorio/RETORNO.json"},
        "roda": ["coleta/eu_regulatorio_executor.py"],
        # O adapter NAO cunha corrida: recebe a que o orquestrador cunhou.
        "recebe_run_id": True,
        "larga_em": ["data/colheita/eu-regulatorio/"],
        # O pedido escolhe o ato; a receita traduz o filtro em argumento.
        "argumentos_de_filtros": ["celex"],
        # ⚠️ ESTE CELEX NAO FOI ESCOLHIDO POR CASAR COM A REGRA DA PORTA.
        # E o que a ficha de `EU-T4-001` ja nomeia no campo `real_example`,
        # escrito por outra missao. O criterio e mais velho do que a medicao.
        "filtros_por_omissao": {"celex": "32026R1696"},
        "rotas": ["EUR-Lex por CELEX (rota declarada no contrato de "
                  "EU-T4-001)"],
        "o_que_traz": "o ato regulatorio oficial da UE, em PDF, como o Jornal "
                      "Oficial o publica, com o CELEX que a fonte declara como "
                      "identidade",
        "custo": "gratuito",
    }, {
        "id": "rotulos-oficiais",
        # F3 · o retorno e o MANIFESTO de 163 descargas. Os 163 PDF que ele
        # indexa nao estao nesta arvore: `PAYLOAD = AUSENTE`, e ausencia
        # nao e erro nem e item.
        "retorno": {"LEGADO": {
            "data/raw/IT-ROTULOS/_MANIFESTO.json": "MANIFEST"}},
        "roda": ["coleta/rotulos_baixar.py"],
        "larga_em": ["data/raw/IT-ROTULOS"],
        "rotas": ["registro oficial (HTTP)"],
        "o_que_traz": "o rotulo oficial do produto, como PDF, com a data em que "
                      "foi baixado",
        "custo": "gratuito",
    }, {
        # ── A FONTE T4 ITALIANA GANHA O EXECUTOR QUE JA A COLHE — BG-05 ─────
        # `IT-T4-001` e T4, o coletor italiano SABE percorre-la (esta em
        # `PILOT_SOURCES` e ja a colheu com aquisicao real em 15/09), e ainda
        # assim um pedido `T4 + fonte=IT-T4-001` abria o `regulatorio-eu` —
        # que nao consome `fonte`, descartava o filtro EM SILENCIO e colhia
        # `EU-T4-001`. Outra fonte, outro pais, outro ato.
        #
        #     O PEDIDO NOMEIA UMA FONTE; O EXECUTOR NAO PODE TROCA-LA.
        #
        # Ele vem em TERCEIRO de proposito: o pedido T4 SEM filtros continua a
        # abrir exactamente o que abria antes (`regulatorio-eu`, primeiro da
        # lista). Quem o promove e a regra de consumo de filtros no
        # `resolver()`: declarado `fonte`, so ele a consome, e sobe.
        #
        # SEM `filtros_por_omissao`, e isso e uma escolha: um T4 que chegasse
        # aqui sem `fonte` nao pode ganhar uma fonte inventada pela receita —
        # e o coletor, sem fonte nomeada, recusa alto (FONTES_AUSENTES, BG-06).
        "id": "italia-recorrente",
        "retorno": {"ENVELOPE": "data/colheita/italia/RETORNO.json"},
        "roda": ["coleta/italy_executor.py"],
        "recebe_run_id": True,
        "larga_em": ["data/colheita/italia/"],
        "argumentos_de_filtros": ["fonte"],
        "rotas": ["HTTP direto"],
        "o_que_traz": "o registo oficial datado da fonte T4 italiana nomeada "
                      "no pedido, como CSV, com a versao do documento e o "
                      "sitio onde o byte ficou",
        "custo": "gratuito",
    }],
    "T3": [{
        # ── O COLETOR ITALIANO COBRE T3, E A RECEITA NAO O DIZIA ───────────
        # ⚠️ ESTE REGISTO NAO E NOVO CODIGO: E UMA DECLARACAO QUE FALTAVA.
        # `coleta/italy_pilot_collect.mjs` declara, no proprio ficheiro:
        #
        #     PILOT_SOURCES = ["IT-T3-005", "IT-T2-002", "IT-T2-004",
        #                      "IT-T3-002", "IT-T3-010", "IT-T3-008", "IT-T4-001"]
        #
        # QUATRO das sete sao T3 — boletins fitossanitarios e de praga, com
        # bytes preservados e SHA no livro italiano. A receita registava este
        # executor SO em T2, e por isso um pedido de T3 abria o `eppo`, que
        # nunca correu e cujo `larga_em` aponta para uma pasta inexistente.
        #
        #     UM EXECUTOR QUE COLHE T3 E SO SE DECLARA EM T2
        #     FAZ O PEDIDO DE T3 BATER NUMA PORTA QUE NAO ABRE.
        #
        # Ele vem PRIMEIRO porque o orquestrador abre `executores[0]` e este e
        # o unico dos dois que colhe. O `eppo` fica — o registo dele nao esta
        # errado, esta por cumprir — e passa para tras, que e onde estao os
        # executores que ainda nao atravessam.
        "id": "italia-recorrente",
        "retorno": {"ENVELOPE": "data/colheita/italia/RETORNO.json"},
        "roda": ["coleta/italy_executor.py"],
        "recebe_run_id": True,
        "larga_em": ["data/colheita/italia/"],
        "argumentos_de_filtros": ["fonte"],
        # `IT-T3-010` e o Bollettino Mosca dell'Olivo da APOL: boletim de praga
        # publicado, com bytes nesta arvore e SHA no livro. Nao foi escolhido
        # por casar com o vocabulario da porta — e o que o contrato de
        # `regras/italy_contracts.mjs` ja declara como P0 de T3.
        "filtros_por_omissao": {"fonte": "IT-T3-010"},
        "rotas": ["HTTP direto"],
        "o_que_traz": "o boletim fitossanitario ou de praga da zona, como PDF "
                      "ou HTML, com a versao do documento e o sitio onde o "
                      "byte ficou",
        "custo": "gratuito",
    }, {
        "id": "eppo",
        # F2 · nunca correu, e o sitio declarado nao existe. Nao ha nada a
        # declarar, e inventar uma especie para um ficheiro inexistente
        # seria a casa a fingir que sabe. Fica sem `retorno`, e o recibo
        # diz porque.
        "roda": ["coleta/eppo_gd.py"],
        "larga_em": ["data/samples/IT-PRAGAS"],
        "rotas": ["EPPO Global Database"],
        "o_que_traz": "a ficha da praga ou doenca, com o nome cientifico e a "
                      "distribuicao declarada",
        "custo": "gratuito",
    }],
    "T2": [{
        "id": "italia-recorrente",
        # F1 · a corrida DECLARA o que produziu. E a unica origem legitima
        # de COLHEITA nesta casa.
        "retorno": {"ENVELOPE": "data/colheita/italia/RETORNO.json"},
        # O COLETOR ITALIANO E NODE, e a rota canonica corre executores com
        # `sys.executable`. Quem entra aqui e o ADAPTER em Python — ele e que
        # sabe chamar o Node, ler o livro append-only e largar a colheita DESTA
        # corrida na lingua da porta. Sem ele, a Italia colhia ha meses e nunca
        # passava por `coleta/ingresso.py`: 144 observacoes preservadas num
        # armazem paralelo, zero linhas em `raw_asset`.
        "roda": ["coleta/italy_executor.py"],
        # ⚠️ O ADAPTER PRECISA DA CORRIDA QUE O T-04 CUNHOU, e nao de uma que
        # ele proprio invente. Este campo e OPT-IN: os outros executores nao o
        # declaram e continuam a ser chamados exactamente como antes.
        "recebe_run_id": True,
        "larga_em": ["data/colheita/italia/"],
        # precedente: o T9 ja traduz filtros do pedido em argumentos do executor.
        "argumentos_de_filtros": ["fonte"],
        # A A5.2 autorizou UMA fonte para o primeiro corte. O coletor sabe
        # percorrer sete; registar as sete de uma vez seria prometer o que nao
        # foi provado por aqui.
        "filtros_por_omissao": {"fonte": "IT-T2-002"},
        "rotas": ["HTTP direto"],
        "o_que_traz": "o boletim agrometeorologico da zona, como PDF, com a "
                      "versao do documento e o sitio onde o byte ficou",
        "custo": "gratuito",
    }],
    "T9": [{
        "id": "comunicacao-publica",
        # F3 · seis ficheiros, quatro especies, zero colheita. O
        # `CLASSIFICADO-V1.json` DECLARA um contentor `ITEMS` com
        # `ITEM_COUNT = 0`: e o recibo de uma coleta que nao trouxe nada,
        # e a heuristica antiga saltava-o por estar vazio para agarrar a
        # lista de contas ao lado.
        "retorno": {"LEGADO": {
            "data/samples/COMPETITOR-PUBLIC-COMM/ANCORAS-EVIDENCIA-V1.json": "CATALOG",
            "data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json": "CATALOG",
            "data/samples/COMPETITOR-PUBLIC-COMM/UNIVERSO-CONTAS-V1.json": "CATALOG",
            "data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json": "PLAN",
            "data/samples/COMPETITOR-PUBLIC-COMM/MEDICAO-PRIMEIRO-LOTE-V1.json": "RUN_RECEIPT",
            "data/samples/COMPETITOR-PUBLIC-COMM/CLASSIFICADO-V1.json": "RUN_RECEIPT"}},
        "serve_fases": ["contratos", "posts", "transcrever"],
        "roda": ["coleta/comunicacao_coleta.py"],
        # O executor precisa de saber a fase e a plataforma, e essas vem do
        # pedido — nao de quem o chama. Declarar aqui QUE filtros viram
        # argumentos e o que permite ao botao do GitHub parar de conhecer a
        # linha de comando do script: ele pede, e a receita traduz.
        # `fase` aceita hoje: `contratos` (gratis, le o schema do ator),
        # `posts` (a coleta paga) e `transcrever` — a FALA dos videos ja
        # coletados, que corre local e custa zero dolares.
        #
        # A fala entrou por AQUI, e nao como executor novo, de proposito: o
        # orquestrador chama apenas o PRIMEIRO executor de cada alvo, portanto
        # um segundo registo em T9 nunca seria aberto e ficaria a mentir nesta
        # lista. Uma capacidade, uma porta.
        "argumentos_de_filtros": ["fase", "plataforma"],
        "filtros_por_omissao": {"fase": "posts"},
        "larga_em": ["data/samples/COMPETITOR-PUBLIC-COMM",
                     "data/samples/REEL-TRANSCRICOES"],
        "rotas": ["YouTube", "Instagram", "LinkedIn", "Facebook"],
        "o_que_traz": "o que o concorrente publicou em canal aberto, com a data "
                      "e o endereco de onde veio — e, com `fase=transcrever`, a "
                      "FALA do video, num campo separado da legenda",
        "custo": "pago quando passa pela rota Apify; `transcrever` custa zero "
                 "dolares e paga-se em tempo de maquina",
    }, {
        # ── A FRENTE DE AQUISICAO CANONICA, E POR QUE ELA VEM PRIMEIRO ──────
        # O SCRAP e o executor canonico de aquisicao desta casa: tem portao
        # (`CHECK`), roteador, teto de rede, teto de gasto, guarda de
        # autorizacao e preservacao de RAW. Ate a SCRAP-FLOW-01 nenhum
        # `COLLECTION_REQUEST` conseguia chegar a ele — o disparador ia direto
        # a `coleta/social_scrap.py` e o que se colhia nunca via a porta.
        #
        #     MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.
        #
        # Ele fica em SEGUNDO de proposito: o pedido que nao nomeia fase
        # continua a abrir exactamente o executor que abria antes desta
        # missao. `serve_fases` e que o promove, e so para as fases dele.
        # Antes, a lista era lida so no primeiro item — e o comentario do
        # `comunicacao-publica` ja avisava que um segundo registo «nunca seria
        # aberto e ficaria a mentir nesta lista». Deixou de ficar.
        "id": "scrap-colheita",
        "roda": ["coleta/scrap_colheita.py"],
        "recebe_run_id": True,
        # A fonte DESCE COM O PEDIDO. O SCRAP observa PLATAFORMAS e a porta
        # fala em FONTES; sem o SOURCE_ID vindo daqui, o adapter declara zero
        # colheita e escreve porque. URL NAO E SOURCE_ID.
        # A ORDEM E A LINHA DE COMANDO. O orquestrador acrescenta os valores
        # por esta ordem, sem nomes — como ja faz para o `comunicacao-publica`.
        "argumentos_de_filtros": ["fase", "fonte"],
        # O TETO DE OBJETOS da janela. Ele existia no disparador desde sempre e
        # a SCRAP-FLOW-01 perdeu-o ao migrar: `social_scrap.py coletar FASE
        # $TETO` passava-o posicionalmente, e o pedido nao o levava.
        #
        #     MIGRAR UM CAMINHO E MUDAR POR ONDE ELE PASSA,
        #     NAO O QUE ELE LEVA.
        #
        # Ele desce como FILTRO nomeado, e nao como posicional: um terceiro
        # argumento sem nome seria indistinguivel da fonte no dia em que
        # alguem omitisse uma delas.
        # `handle` junta-se ao `teto` porque o canario da Release V1 precisa
        # de saber A QUE CONTA bate. Ele NAO e a fonte: `--fonte` continua a
        # descer o SOURCE_ID provado, e `coleta/scrap_colheita.py::NOMEADOS`
        # declara, por fase, qual dos dois ela aceita — um nome fora da lista
        # da fase recusa a corrida em vez de morrer no `**_` do adaptador.
        #
        #     HANDLE NAO E SOURCE_ID.
        # ⚠️ `site` ENTRA AQUI E NAO EM `argumentos_de_filtros`, E ISSO E UMA
        # ESCOLHA. A LINKEDIN-OP-01 passava-o como TERCEIRO POSICIONAL. Um
        # terceiro argumento sem nome e indistinguivel da fonte no dia em que
        # alguem omitir uma delas — e a `coleta/scrap_colheita.py::NOMEADOS`
        # ja declara, por fase, que filtros cada uma aceita, recusando os
        # outros em vez de os deixar morrer no `**_` do adaptador.
        #
        #     PORTA-SE O COMPORTAMENTO, NAO O MECANISMO.
        #     E O MECANISMO QUE FICA E O QUE RECUSA MAIS CEDO.
        "filtros_nomeados": ["teto", "handle", "site",
                             # ── OS ENDERECOS DAS TRES FASES NOVAS ─────────
                             # Cada um e o endereco de UMA rota de
                             # `adaptador_aberto`, e nenhum e SOURCE_ID.
                             # `scrap_colheita.py::NOMEADOS` declara, por fase,
                             # qual destes ela aceita — e recusa os outros em
                             # vez de os deixar morrer no `**_` do adaptador.
                             #
                             #     A LISTA AQUI ABRE; A LISTA DA FASE FECHA.
                             "canal", "instancia", "tag", "termo"],
        # `identidade-linkedin` chegou da LINKEDIN-OP-01. Ela e a UNICA rota que
        # a politica canonica permite no LinkedIn: le o site DA PROPRIA
        # organizacao e traz de la o endereco que a organizacao publicou. Nunca
        # toca `linkedin.com`, nunca usa buscador, e devolve CATALOGO — uma
        # entidade de onde se PODE colher — e nao COLHEITA.
        #
        #     IDENTITY != CONTENT. Pedir posts do LinkedIn continua a bater em
        #     `ROUTE_NOT_ALLOWED`, e nao ha receita que o contorne.
        "serve_fases": ["janela", "janela-perfis", "janela-objetos",
                        "canario-bluesky", "identidade-linkedin",
                        # As tres irmas da forma `adaptador_aberto/ROTA/ONLINE`.
                        # Sem esta linha a fase existe em `scrap_colheita` e o
                        # orquestrador continua a nao a saber pedir: a fase diz
                        # O QUE CORRE, e `serve_fases` diz QUEM A ABRE.
                        "canal-telegram", "tag-mastodon", "contas-bluesky"],
        "filtros_por_omissao": {},
        # O envelope do COL-LAW-505. Nao e `larga_em`: `larga_em` diz ONDE se
        # largou, e este diz O QUE SE LARGOU — que e a pergunta que faltava.
        # ── O VOCABULARIO DO RETORNO E UM SO ───────────────────────────
        # Esta receita dizia `envelope_em`. As outras cinco desta casa dizem
        # `retorno: {ESPECIE: caminho}`, que e a forma da COL-LAW-505 — a lei
        # que nomeia a ESPECIE do que volta, e nao so o sitio.
        #
        # E o orquestrador desta arvore le `retorno`. Com `envelope_em` ele
        # corria o executor, nao encontrava nada, e seguia em frente:
        # `COLHEITA_ENCONTRADA = 0`, admissao a nao correr, e nenhum erro.
        #
        #     DOIS NOMES PARA O MESMO CONCEITO NAO SAO SINONIMOS:
        #     SAO UM CAMINHO QUE NINGUEM PERCORRE.
        #
        # `ENVELOPE` e a especie certa: o SCRAP devolve UM envelope canonico,
        # e nao um legado por classificar.
        "retorno": {"ENVELOPE": "data/colheita/scrap/ENVELOPE.json"},
        "larga_em": ["data/colheita/scrap/"],
        "rotas": ["Instagram", "Bluesky",
                  "LinkedIn (so identidade, rota indireta)"],
        "o_que_traz": "a janela publica da conta — o perfil e os objetos que "
                      "ela publicou — pelo executor canonico do SCRAP, com "
                      "RAW preservado antes de qualquer normalizacao; e, na "
                      "fase `canario-bluesky`, a cronologia publica de uma "
                      "conta Bluesky pela AppView aberta, sem credencial; e, "
                      "com `fase=identidade-linkedin`, o ENDERECO LinkedIn que "
                      "a propria organizacao publica no site dela, como "
                      "CATALOGO e nunca como colheita",
        "custo": "gratuito",
    }],
}

# Contratos que NENHUMA coleta pode dispensar. Nao sao conselhos: sem eles o
# item nao consegue provar de onde veio nem quando aconteceu, e a inteligencia
# recebe um numero sem passado.
CONTRATOS_OBRIGATORIOS = (
    ("procedencia", "regras/proveniencia.py",
     "carimba de onde veio, no momento em que entra"),
    ("tempo do fato", "leis/data_clock.py",
     "separa quando o fato aconteceu de quando nos o capturamos"),
    ("lugar do fato", "leis/fato_local.py",
     "separa o lugar de onde veio o documento do lugar onde o fato aconteceu"),
    ("recibo da corrida", "data/samples/RUN-MANIFEST.json",
     "quem correu, quando, com que entrada, quanto trouxe e quanto custou"),
)


#: Os filtros que o PROPRIO resolvedor consome — recortam fontes e ordenam
#: executores, e por isso nao descem ao executor nem podem ser acusados de
#: nao-consumidos. Um filtro fora desta lista OU e consumido pelo executor
#: escolhido, OU a corrida e recusada antes da rede (BG-05).
FILTROS_DO_RESOLVEDOR = ("pais", "tema", "fase")


def filtros_consumidos(e: dict) -> set:
    """O que ESTE executor declara saber consumir — e nada alem disso.

    A declaracao ja existia (`argumentos_de_filtros` + `filtros_nomeados`);
    o que faltava era alguem le-la ANTES de correr, em vez de deixar o
    filtro nao-declarado cair no chao.
    """
    return (set(e.get("argumentos_de_filtros") or ())
            | set(e.get("filtros_nomeados") or ()))


def _fontes() -> list:
    """As fontes que a casa ja tem em ficha — atlas europeu e master italiano."""
    if not FONTES_MEDIDAS.is_file():
        return []
    S = json.loads(FONTES_MEDIDAS.read_text(encoding="utf-8"))
    return list(S.get("SOURCES") or []) + list(S.get("MASTER_ITALIANO") or [])


def _sabe_o_caminho(f: dict) -> bool:
    """A ficha diz COMO se chega la? «NAO SEI» nao conta como caminho."""
    m = str(f.get("access_method") or "").strip()
    return bool(m) and "NAO SEI" not in m.upper() and "NÃO SEI" not in m.upper()


@dataclass
class Plano:
    """O caminho que se vai percorrer — e o que ficou por saber."""

    pedido: Pedido
    fontes_do_assunto: list = field(default_factory=list)
    com_caminho: list = field(default_factory=list)
    sem_caminho: list = field(default_factory=list)
    executores: list = field(default_factory=list)
    contratos: tuple = CONTRATOS_OBRIGATORIOS
    saida_esperada: str = ""

    @property
    def da_para_correr(self) -> bool:
        return bool(self.executores)

    def porque_nao(self) -> str:
        if self.executores:
            return ""
        if not self.fontes_do_assunto:
            return (f"NAO SEI: nenhuma fonte em ficha esta classificada como "
                    f"«{self.pedido.assunto}» ({self.pedido.alvo}). Antes de "
                    f"coletar isto, alguem tem de levantar pelo menos uma fonte.")
        return (f"NAO SEI COMO: ha {len(self.fontes_do_assunto)} fonte(s) de "
                f"«{self.pedido.assunto}», mas nenhum executor desta casa declara "
                f"saber percorrer a rota delas. A ficha diz que existem; ninguem "
                f"escreveu ainda como se chega la.")

    def em_palavras(self) -> str:
        L = [f"PLANO PARA: {self.pedido.em_uma_frase()}", ""]
        L.append(f"  fontes deste assunto em ficha : {len(self.fontes_do_assunto)}")
        L.append(f"  destas, com caminho escrito   : {len(self.com_caminho)}")
        L.append(f"  destas, NAO SEI como se chega : {len(self.sem_caminho)}")
        if self.sem_caminho:
            nomes = ", ".join(x.get("source_id") or x.get("name", "?")
                              for x in self.sem_caminho[:6])
            L.append(f"      ({nomes}{' ...' if len(self.sem_caminho) > 6 else ''})")
        L.append("")
        if self.executores:
            L.append("  quem vai correr:")
            for e in self.executores:
                L.append(f"      {e['id']}  ->  {' '.join(e['roda'])}")
                L.append(f"          traz: {e['o_que_traz']}")
                L.append(f"          rota: {', '.join(e['rotas'])} · {e['custo']}")
        else:
            L.append(f"  NAO DA PARA CORRER: {self.porque_nao()}")
        L.append("")
        L.append("  contratos que a corrida tem de cumprir:")
        for nome, onde, porque in self.contratos:
            L.append(f"      {nome:18s} {porque}")
        if self.saida_esperada:
            L.append("")
            L.append(f"  saida esperada: {self.saida_esperada}")
        return "\n".join(L)


def resolver(p: Pedido) -> Plano:
    """Do pedido ao caminho. Tudo medido do atlas; nada adivinhado."""
    pais = (p.filtros.get("pais") or "").upper()
    tema = (p.filtros.get("tema") or "").lower()

    do_assunto = []
    for f in _fontes():
        if str(f.get("territory") or "").upper() != p.alvo:
            continue
        if pais:
            c = str(f.get("country") or "").upper()
            mapa = {"ES": ("ES", "ESPANHA"), "IT": ("IT", "ITALIA"),
                    "FR": ("FR", "FRANCA"), "EU": ("EU", "EUROPA")}
            # EUROPA serve qualquer pais europeu: nao se descarta uma base
            # continental so porque o pedido nomeou um pais dela.
            if c not in mapa.get(pais, (pais,)) and c not in ("EU", "EUROPA"):
                continue
        if tema:
            texto = " ".join(str(f.get(k) or "") for k in
                             ("crops", "topics", "name", "use_case")).lower()
            if tema not in texto:
                continue
        do_assunto.append(f)

    com = [f for f in do_assunto if _sabe_o_caminho(f)]
    sem = [f for f in do_assunto if not _sabe_o_caminho(f)]

    # ── QUEM CONSOME OS FILTROS DECLARADOS VEM PRIMEIRO — BG-05 ────────────
    # O orquestrador abre apenas `executores[0]`. Enquanto a ordem fosse fixa,
    # um segundo executor no mesmo alvo nunca era aberto — e o proprio registo
    # do `comunicacao-publica` dizia isso, por escrito, como defeito conhecido.
    #
    #     UMA LISTA CUJO SEGUNDO ITEM NUNCA E LIDO NAO E UMA LISTA:
    #     E UM ITEM E UMA MENTIRA.
    #
    # A promocao tem DUAS chaves, por esta ordem:
    #
    #   1 · consome TODOS os filtros que o pedido declarou (fora os do
    #       resolvedor). Foi a falta disto que mandou `T4 + fonte=IT-T4-001`
    #       para o `regulatorio-eu`, que nao consome `fonte` — o filtro
    #       morria calado e vinha `EU-T4-001` no lugar.
    #   2 · serve a fase pedida (a regra que ja existia).
    #
    # Nao ha adivinhacao: quem nao declara `serve_fases` serve tudo, como
    # sempre serviu; um pedido SEM filtros de executor nao mexe em nada, e a
    # ordem declarada continua a mandar entre iguais (sort estavel).
    execs = list(EXECUTORES.get(p.alvo, []))
    fase = str(p.filtros.get("fase") or "").strip()
    declarados = ({k for k, v in p.filtros.items() if v not in (None, "")}
                  - set(FILTROS_DO_RESOLVEDOR))
    if fase or declarados:
        execs.sort(key=lambda e: (
            0 if declarados <= filtros_consumidos(e) else 1,
            0 if fase in (e.get("serve_fases") or [fase]) else 1))

    return Plano(
        pedido=p,
        fontes_do_assunto=do_assunto,
        com_caminho=com,
        sem_caminho=sem,
        executores=execs,
        saida_esperada=(f"itens de «{p.assunto}» com procedencia, tempo do fato e "
                        f"lugar do fato carimbados, prontos para a porta de admissao"),
    )


if __name__ == "__main__":
    from pedido import de_uma_frase
    frase = " ".join(sys.argv[1:]) or "colete materiais de pesquisadores"
    print(resolver(de_uma_frase(frase)).em_palavras())
