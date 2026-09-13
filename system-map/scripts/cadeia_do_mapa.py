#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · O LEITOR DA CADEIA

    O MANIFESTO E UM SO. O JEITO DE O LER TAMBEM.

`CADEIA-DO-MAPA.json` continua a ser o DONO da cadeia — este ficheiro nao
declara passo nenhum, nao guarda lista nenhuma e nao decide ordem nenhuma. Ele
so sabe INTERPRETAR o que o manifesto diz.

Existe porque o `G4` mudou a forma de cada passo:

    antes   "system-map/scripts/scan_repo.py"
    depois  {STEP_ID, EXECUTABLE, INPUTS[], OUTPUTS[]}

Quatro consumidores liam a lista antiga, cada um a seu modo — um `for ... of`,
um `list(...)`, um `.index(...)`, um `[p for p in ...]`. Se cada um aprendesse
sozinho a forma nova, a forma nova passava a ter quatro interpretacoes, e a
quinta mudanca partia tres deles em silencio.

    UM FORMATO COM QUATRO LEITORES NAO E UM FORMATO: SAO QUATRO ACORDOS
    QUE POR ENQUANTO CALHAM BATER.

O lado JavaScript tem o seu proprio leitor em `publicar_no_deploy.mjs`, porque
sao dois runtimes e nao ha como partilhar codigo — mas e UM por runtime, que e
o minimo possivel, e `test_system_map.py` prova que os dois leem o mesmo.

A ORDEM (G6)
------------
`passos()` ja NAO devolve a ordem escrita: devolve a ordem DERIVADA das
dependencias declaradas. A ordem escrita passou a ser so a semente do desempate.

    A DEPENDENCIA DETERMINA A ORDEM. A ORDEM NAO DETERMINA A DEPENDENCIA.

Ate ao G5 havia duas coisas que podiam discordar: a lista escrita e o que os
passos diziam ler. Discordaram — tres consumidores corriam antes do seu
produtor, e ninguem reclamava, porque cada um lia um ficheiro que EXISTIA (o da
rodada anterior). Um artefacto velho nao da erro: da uma resposta antiga.

    UM CONSUMIDOR ANTES DO PRODUTOR NAO FALHA: ELE RESPONDE DA RODADA PASSADA.

Por isso a ordem deixou de ser uma opiniao escrita a mao. Ela sai de Kahn sobre
as arestas NOMEADAS, com desempate estavel pela posicao escrita — deterministico
e sem preferencia nenhuma minha. Se as arestas nomeadas tiverem ciclo, isto
REBENTA em vez de escolher: um ciclo escondido para conseguir ordenar seria a
mentira que esta lei existe para impedir.
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MANIFESTO = AQUI / "CADEIA-DO-MAPA.json"
CADEIA = json.loads(MANIFESTO.read_text(encoding="utf-8"))

TRACKED_SOURCE_TREE = "TRACKED_SOURCE_TREE"
TRACKED_SOURCE_FILE = "TRACKED_SOURCE_FILE"
GENERATED_ARTIFACT = "GENERATED_ARTIFACT"
CANONICAL_MANIFEST = "CANONICAL_MANIFEST"
KINDS = (TRACKED_SOURCE_TREE, TRACKED_SOURCE_FILE,
         GENERATED_ARTIFACT, CANONICAL_MANIFEST)

FORA_DO_MANIFESTO = "FORA_DO_MANIFESTO"


# A ordem e uma funcao pura do manifesto, e o manifesto le-se uma vez no import.
# Sem isto, cada `passos()` refazia Kahn — e a cadeia chama `passos()` milhares
# de vezes por corrida.
_ORDEM: list = []


class CicloNomeado(Exception):
    """Ha um ciclo entre dependencias NOMEADAS — e isso nao se ordena."""


def ordem_escrita() -> list:
    """Os passos de regeneracao, na ordem LITERAL do ficheiro.

    Existe para UMA coisa: a guarda que compara o que esta escrito com o que a
    lei deriva. Quem quer correr a cadeia usa `passos()`.

        SE ISTO FOSSE USADO PARA CORRER, VOLTAVA A HAVER DUAS ORDENS.
    """
    return list(CADEIA["REGERAR"])


def ordem_derivada() -> list:
    """OS STEP_ID PELA ORDEM QUE AS DEPENDENCIAS EXIGEM.

    Kahn, com fila de prioridade pela posicao escrita. A posicao escrita nao
    decide nada sozinha: ela so desempata entre passos que ja estao ambos
    prontos. E por isso que o resultado e o mesmo em qualquer maquina e que
    reescrever o ficheiro por outra ordem nao muda a ordem de execucao — muda so
    o desempate, e a guarda apanha a discrepancia.
    """
    if _ORDEM:
        return list(_ORDEM[0])
    import heapq
    escrita = [p["STEP_ID"] for p in CADEIA["REGERAR"]]
    pos = {s: i for i, s in enumerate(escrita)}
    adj = {s: set() for s in escrita}
    grau = {s: 0 for s in escrita}
    for a in arestas():
        if a["CLASSE"] != NOMEADA:
            continue                       # varredura nao ordena — ver LEI
        p, c = a["PRODUTOR"], a["CONSUMIDOR"]
        if p in pos and c in pos and p != c and c not in adj[p]:
            adj[p].add(c)
            grau[c] += 1
    fila = [pos[s] for s in escrita if grau[s] == 0]
    heapq.heapify(fila)
    saida = []
    while fila:
        s = escrita[heapq.heappop(fila)]
        saida.append(s)
        for w in sorted(adj[s], key=lambda x: pos[x]):
            grau[w] -= 1
            if grau[w] == 0:
                heapq.heappush(fila, pos[w])
    if len(saida) != len(escrita):
        presos = sorted(set(escrita) - set(saida), key=lambda s: pos[s])
        raise CicloNomeado(
            "ciclo entre dependencias NOMEADAS, entre: %s. Uma dependencia "
            "nomeada e um pedido de artefacto FRESCO; em ciclo, nenhum dos "
            "lados pode ser fresco. Ou uma delas e varredura (e declara-se "
            "como tal), ou uma delas nao existe." % presos)
    _ORDEM.append(list(saida))
    return saida


def passos() -> list:
    """Os passos de regeneracao, NA ORDEM QUE AS DEPENDENCIAS DERIVAM."""
    por_id = {p["STEP_ID"]: p for p in CADEIA["REGERAR"]}
    return [por_id[s] for s in ordem_derivada()]


def passos_de_validar() -> list:
    return list(CADEIA["VALIDAR"])


def passos_a_mao() -> list:
    """Os regeneradores que nenhuma automacao corre.

    Escrevem artefatos commitados de que o mapa depende, e nenhum workflow os
    executa. Estao aqui para deixarem de ser invisiveis — nao para fingir que
    correm.

        UM ARTEFATO COMMITADO QUE NENHUMA AUTOMACAO REGENERA
        NAO ESTA ERRADO: ESTA A ENVELHECER SEM TESTEMUNHA.
    """
    return list(CADEIA.get("REGERAR_A_MAO", []))


def portoes_pos_commit() -> list:
    """OS PORTOES QUE SO TEM RESPOSTA DEPOIS DO COMMIT.

    `--conferir-carimbo` compara o carimbo do mapa COMMITADO com a arvore
    COMMITADA. Nao regenera, e nao valida conteudo: pergunta «este mapa e o
    mapa desta arvore?» — e essa pergunta e impossivel antes do commit.

        POR UM PORTAO EM REGERAR PARA ZERAR UMA LISTA E MENTIR SOBRE O
        CONTRATO DELE. PO-LO EM VALIDAR E MENTIR SOBRE QUANDO ELE CORRE.
    """
    return list(CADEIA.get("PORTOES_POS_COMMIT", []))


def outras_execucoes(papel: str = None) -> list:
    """As provas, o publicador do build e o portao de deploy.

    Elas NAO compoem o mapa — nao ha INPUTS/OUTPUTS de geracao a declarar —
    mas o workflow executa-as, e uma execucao que o workflow faz e o manifesto
    nao conhece e uma segunda cadeia a comecar.
    """
    return [x for x in CADEIA.get("OUTRAS_EXECUCOES", [])
            if papel is None or x.get("PAPEL") == papel]


def produtores_externos() -> list:
    """O que o mapa CONSOME e nao produz. Fica fora, e fica dito."""
    return list(CADEIA.get("PRODUTORES_EXTERNOS", []))


def todas_as_execucoes() -> list:
    """TUDO o que pertence ao System Map e e executado. O universo, num sitio so."""
    return (passos() + passos_a_mao() + passos_de_validar()
            + portoes_pos_commit() + outras_execucoes())


def todos_os_passos() -> list:
    """So os que COMPOEM o mapa — os que o contrato de IO do G4 governa."""
    return passos() + passos_a_mao() + passos_de_validar()


def executaveis() -> list:
    """So os caminhos, na ordem — o que o publicador e o CI correm."""
    return [p["EXECUTABLE"] for p in passos()]


def executaveis_de_validar() -> list:
    return [p["EXECUTABLE"] for p in passos_de_validar()]


def executaveis_de(categoria: str) -> list:
    """Os executaveis de UMA categoria, na ordem escrita. Sem ordenar nada."""
    tabela = {"REGERAR": passos, "REGERAR_A_MAO": passos_a_mao,
              "VALIDAR": passos_de_validar,
              "PORTOES_POS_COMMIT": portoes_pos_commit,
              "OUTRAS_EXECUCOES": outras_execucoes}
    if categoria not in tabela:
        raise KeyError("categoria desconhecida: %s (ha %s)"
                       % (categoria, sorted(tabela)))
    return [p["EXECUTABLE"] for p in tabela[categoria]()]


CATEGORIAS = ("REGERAR", "REGERAR_A_MAO", "VALIDAR",
              "PORTOES_POS_COMMIT", "OUTRAS_EXECUCOES")


def por_id(step_id: str) -> dict:
    for p in todos_os_passos():
        if p["STEP_ID"] == step_id:
            return p
    raise KeyError(step_id)


def entradas(passo: dict, kind: str = None) -> list:
    return [e for e in passo.get("INPUTS", [])
            if kind is None or e.get("KIND") == kind]


def saidas(passo: dict) -> list:
    return list(passo.get("OUTPUTS", []))


def executavel_que_produz(caminho: str):
    """O EXECUTAVEL que materializa este caminho, ou None.

    `quem_produz` devolve o STEP_ID; quem corre o passo precisa do caminho do
    programa. Sem isto, cada consumidor reconstruia o par artefato -> produtor
    a partir do nome do ficheiro — e um par reconstruido e uma segunda verdade
    a nascer devagar.
    """
    for p in todas_as_execucoes():
        for s in saidas(p):
            if s.get("PATH") == caminho:
                return p["EXECUTABLE"]
    return None


def quem_produz(caminho: str):
    """QUE PASSO DESTE MANIFESTO materializa este caminho? None se nenhum.

    `None` nao quer dizer «ninguem produz»: ha artefatos que o mapa CONSOME e
    nao produz — `golden-path-pdf.generated.json` nasce na COLETA — e esses
    estao em PRODUTORES_EXTERNOS, com dono declarado. Quem chamar isto tem de
    saber a diferenca, e por isso a resposta e None e nunca uma invencao.
    """
    for p in todas_as_execucoes():
        for s in saidas(p):
            if s.get("PATH") == caminho:
                return p["STEP_ID"]
    return None


# ── O GRAFO (G6) ──────────────────────────────────────────────────────────
#
#     PRODUTOR -> ARTEFATO -> CONSUMIDOR
#
# Duas classes de aresta, e a diferenca entre elas e a lei inteira do G6:
#
#   NOMEADA     o consumidor PEDE aquele artefacto pelo nome. Quem pede pelo
#               nome quer a versao desta rodada. Logo: o produtor corre antes.
#
#   VARREDURA   o consumidor varre um SELETOR sobre a arvore rastreada, e
#               calha que ficheiros gerados caem la dentro. Ele nao pediu
#               aquele artefacto: pediu «a arvore que existir quando eu correr».
#               Logo: nao ordena, e o que for escrito depois dele so e visto na
#               rodada seguinte.
#
# QUERES FRESCO? NOMEIA. Esta e a regra de conversao entre as duas, e e o que
# impede alguem de fugir a ordem escondendo uma dependencia num seletor.
NOMEADA = "NOMEADA"
VARREDURA = "VARREDURA"
EXTERNA = "EXTERNA"
PRODUTOR_EXTERNO = "EXTERNAL_PRODUCER"


def _dono_dos_artefatos() -> dict:
    dono = {}
    for p in passos_a_mao() + list(CADEIA["REGERAR"]):
        for s in saidas(p):
            dono.setdefault(s["PATH"], []).append(p["STEP_ID"])
    return dono


def arestas() -> list:
    """TODAS as dependencias entre passos, classificadas e com a evidencia.

    A evidencia e sempre uma declaracao do manifesto — nunca um palpite sobre o
    nome do ficheiro. Uma aresta sem declaracao nao aparece aqui: aparece em
    `nao_resolvidas()`, que e onde tem de doer.
    """
    dono = _dono_dos_artefatos()
    universo = list(CADEIA["REGERAR"]) + passos_a_mao()
    # ⚠️ AQUI NAO SE CHAMA `por_id()`. Ele passa por `passos()`, que pede a ordem
    # derivada, que pede estas arestas — e a volta nunca mais acaba. Quem
    # constroi o grafo tem de ler a lista CRUA: o grafo e anterior a ordem.
    cru = {p["STEP_ID"]: p for p in universo}
    fora = {x["PATH"] for x in produtores_externos()}
    saida = []
    for p in universo:
        c = p["STEP_ID"]
        for e in entradas(p, GENERATED_ARTIFACT):
            caminho = e["PATH"]
            decl = e.get("PRODUCER")
            if decl == PRODUTOR_EXTERNO and caminho in fora:
                saida.append({"PRODUTOR": PRODUTOR_EXTERNO, "CONSUMIDOR": c,
                              "ARTEFATO": caminho, "CLASSE": EXTERNA,
                              "EVIDENCIA": "INPUTS[].PRODUCER + PRODUTORES_EXTERNOS"})
                continue
            for real in dono.get(caminho, []):
                saida.append({"PRODUTOR": real, "CONSUMIDOR": c,
                              "ARTEFATO": caminho, "CLASSE": NOMEADA,
                              "EVIDENCIA": "INPUTS[].PRODUCER"})
        for e in entradas(p, TRACKED_SOURCE_TREE):
            for real in e.get("INCLUI_GERADOS") or []:
                for s in saidas(cru.get(real) or {}):
                    saida.append({"PRODUTOR": real, "CONSUMIDOR": c,
                                  "ARTEFATO": s["PATH"], "CLASSE": VARREDURA,
                                  "EVIDENCIA": "INPUTS[].INCLUI_GERADOS",
                                  "SELETOR": e.get("FILTRO_DONO")})
    return saida


def nao_resolvidas() -> list:
    """Entradas geradas que nao sabem dizer quem as escreve.

    Nao ha aqui nenhuma inferencia de misericordia: se o manifesto nao nomeia o
    produtor e ninguem declara aquele caminho como saida, a dependencia fica
    por resolver e diz-se. Adivinhar pelo nome do ficheiro seria fabricar DAG
    para obter verde.
    """
    dono = _dono_dos_artefatos()
    fora = {x["PATH"] for x in produtores_externos()}
    soltas = []
    for p in list(CADEIA["REGERAR"]) + passos_a_mao():
        for e in entradas(p, GENERATED_ARTIFACT):
            caminho = e["PATH"]
            if caminho in dono or caminho in fora:
                continue
            soltas.append({"CONSUMIDOR": p["STEP_ID"], "ARTEFATO": caminho,
                           "PRODUCER_DECLARADO": e.get("PRODUCER")})
    return soltas


def _componentes(nos: list, adj: dict) -> list:
    """Tarjan, iterativo — as componentes fortemente conexas."""
    indice, baixo, napilha, pilha, saida = {}, {}, set(), [], []
    contador = [0]
    for raiz in nos:
        if raiz in indice:
            continue
        trabalho = [(raiz, iter(sorted(adj.get(raiz, ()))))]
        indice[raiz] = baixo[raiz] = contador[0]
        contador[0] += 1
        pilha.append(raiz)
        napilha.add(raiz)
        while trabalho:
            v, filhos = trabalho[-1]
            avancou = False
            for w in filhos:
                if w not in indice:
                    indice[w] = baixo[w] = contador[0]
                    contador[0] += 1
                    pilha.append(w)
                    napilha.add(w)
                    trabalho.append((w, iter(sorted(adj.get(w, ())))))
                    avancou = True
                    break
                if w in napilha:
                    baixo[v] = min(baixo[v], indice[w])
            if avancou:
                continue
            trabalho.pop()
            if trabalho:
                baixo[trabalho[-1][0]] = min(baixo[trabalho[-1][0]], baixo[v])
            if baixo[v] == indice[v]:
                comp = []
                while True:
                    w = pilha.pop()
                    napilha.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                saida.append(sorted(comp))
    return saida


def ciclos() -> list:
    """OS CICLOS DO GRAFO INTEIRO, CADA UM COM A SUA CLASSE.

    Classificar nao e opcional e nao tem gaveta «resto»:

        DELAYED_CYCLE   o ciclo tem pelo menos uma aresta de VARREDURA. Essa
                        aresta e o CORTE NO TEMPO: a varredura le a arvore que
                        existe quando corre, e o que for escrito depois dela fica
                        para a rodada seguinte. O ciclo fecha-se entre rodadas,
                        e nao dentro de uma.
        BUG             o ciclo sobrevive so com arestas NOMEADAS. Nao ha corte:
                        os dois lados querem-se frescos ao mesmo tempo, e isso
                        nenhuma ordem resolve. Tem de ser corrigido, nao
                        classificado.
    """
    universo = [p["STEP_ID"] for p in list(CADEIA["REGERAR"]) + passos_a_mao()]
    todas = [a for a in arestas() if a["CLASSE"] in (NOMEADA, VARREDURA)]
    adj = {s: set() for s in universo}
    for a in todas:
        if a["PRODUTOR"] in adj and a["CONSUMIDOR"] in adj:
            adj[a["PRODUTOR"]].add(a["CONSUMIDOR"])
    saida = []
    for comp in _componentes(universo, adj):
        dentro = [a for a in todas
                  if a["PRODUTOR"] in comp and a["CONSUMIDOR"] in comp]
        if len(comp) == 1 and not any(a["PRODUTOR"] == a["CONSUMIDOR"]
                                      for a in dentro):
            continue
        cortes = [a for a in dentro if a["CLASSE"] == VARREDURA]
        saida.append({
            "MEMBROS": comp,
            "CLASSE": "DELAYED_CYCLE" if cortes else "BUG",
            "CORTES_NO_TEMPO": sorted({(a["PRODUTOR"], a["CONSUMIDOR"],
                                        a["ARTEFATO"]) for a in cortes}),
            "ARESTAS_NOMEADAS_DENTRO": sorted({(a["PRODUTOR"], a["CONSUMIDOR"],
                                                a["ARTEFATO"]) for a in dentro
                                               if a["CLASSE"] == NOMEADA}),
        })
    return saida


def atrasos() -> list:
    """AS ARESTAS QUE SO SE FECHAM NA RODADA SEGUINTE.

    Uma aresta esta atrasada quando o produtor corre DEPOIS do consumidor — ou
    quando o produtor nem sequer corre na automacao (`REGERAR_A_MAO`). Depois do
    G6 nenhuma aresta NOMEADA pode estar aqui: se estiver, e defeito, e a guarda
    do G6 morde.
    """
    pos = {s: i for i, s in enumerate(ordem_derivada())}
    mao = {p["STEP_ID"] for p in passos_a_mao()}
    fora = []
    for a in arestas():
        if a["CLASSE"] == EXTERNA:
            continue
        p, c = a["PRODUTOR"], a["CONSUMIDOR"]
        if c in mao:
            continue                     # a mao corre fora da rodada; ver PORQUE
        if p in mao:
            fora.append(dict(a, PORQUE="o produtor nao corre na automacao"))
        elif p in pos and c in pos and pos[p] >= pos[c]:
            fora.append(dict(a, PORQUE=("o produtor corre depois"
                                        if pos[p] > pos[c] else "e ele proprio")))
    return fora


def produtor_corre_antes(consumidor: str, produtor: str):
    """O produtor corre antes do consumidor NESTA rodada? None se nao se sabe.

    `None` nao e um talvez educado: e o caso em que um dos dois nao pertence a
    rodada automatica (corre a mao, ou nasce fora da cadeia), e ai a pergunta
    nao tem resposta nesta escala de tempo.
    """
    pos = {s: i for i, s in enumerate(ordem_derivada())}
    if produtor not in pos or consumidor not in pos:
        return None
    return pos[produtor] < pos[consumidor]


def passo_do_executavel(caminho: str):
    """De `system-map/scripts/x.py` para o passo. None se nao e passo nenhum."""
    for p in todas_as_execucoes():
        if p.get("EXECUTABLE") == caminho:
            return p
    return None


AUTOMATED = "AUTOMATED"
MANUAL_BY_CONTRACT = "MANUAL_BY_CONTRACT"
UNREACHABLE = "UNREACHABLE"
DESCONHECIDO = "UNKNOWN"
CLASSES_DE_EXECUCAO = (AUTOMATED, MANUAL_BY_CONTRACT, UNREACHABLE, DESCONHECIDO)


def classe_de_execucao(passo: dict) -> str:
    """QUEM CORRE ISTO — AUTOMACAO, MAO, NINGUEM, OU NAO SE SABE.

    Tudo o que nao esta em REGERAR_A_MAO e corrido por automacao declarada: e
    por isso que a classe nao se repete em vinte passos. Quem esta em
    REGERAR_A_MAO tem de a DIZER, e sem a dizer a resposta e UNKNOWN — nunca
    MANUAL por omissao.

        «NAO ESTA AUTOMATIZADO» E UM FACTO.
        «E MANUAL POR CONTRATO» E UMA DECISAO, E DECISOES ESCREVEM-SE.
    """
    a_mao = {p["STEP_ID"] for p in passos_a_mao()}
    if passo["STEP_ID"] not in a_mao:
        return AUTOMATED
    declarada = passo.get("CLASSE_DE_EXECUCAO")
    return declarada if declarada in CLASSES_DE_EXECUCAO else DESCONHECIDO
