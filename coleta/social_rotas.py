#!/usr/bin/env python3
"""
ROTAS SOCIAIS — o DESPACHO. Escolhe a porta, mede o portao, e executa.

Quem pede coleta diz PLATAFORMA e CAPACIDADE. Nunca diz FERRAMENTA.

    pedido = {'platform': 'MASTODON', 'capability': 'SEARCH_HASHTAG',
              'query': 'agricoltura', 'country_scope': 'IT', 'limit': 20}

A escolha da rota e desta casa, nao de quem chama. Se amanha o Mastodon fechar
a previa publica e a rota certa virar outra, o chamador nao muda uma linha.

ESTE FICHEIRO DEIXOU DE CONHECER O NOME DAS PLATAFORMAS
--------------------------------------------------------
Ate a convergencia C1, ele tinha um `dict` literal com nove pares
`(PLATAFORMA, CAPACIDADE) -> funcao`, e o corpo de todas as rotas por baixo.
Isso e o monolito: acrescentar o TikTok obrigava a editar o despachante.

Agora o mapa vive em `scrap_registo.py` e cada adaptador escreve-se nele. O
despachante le. Acrescentar uma plataforma nova NAO toca numa linha daqui.

    O TESTE DISTO NAO E ESTETICO. E: «ACRESCENTAR UMA PLATAFORMA OBRIGA A
    EDITAR ESTE FICHEIRO?» Se obrigar, o monolito voltou.

UM CONCEITO, UM DONO
---------------------
    scrap_capacidades.py   o que sabemos fazer, e onde       (a declaracao)
    scrap_registo.py       plataforma/capacidade -> adaptador (o mapa)
    scrap_http.py          o portao e a busca                 (o transporte)
    social_matriz.py       que porta e permitida              (a politica)
    social_rotas.py        escolher, medir e executar         (o despacho)

Cinco donos de cinco coisas. Nao cinco donos da mesma.

O QUE ESTE ARQUIVO NAO FAZ
----------------------------
Nao faz login, nao manda cookie, nao resolve CAPTCHA, nao troca de IP para
escapar de bloqueio, nao finge ser navegador de gente. Quando a plataforma diz
nao, a resposta e `ROUTE_NOT_ALLOWED` ou `BLOCKED` no artefato — nunca uma
tentativa mais esperta.

E nao julga conteudo. Ele traz o objeto e preserva o bruto. Se e relevante
para a ADAMA, se e ameaca, se e oportunidade — isso e decisao de outra camada,
que roda de graca sobre o artefato e pode ser refeita sem recoletar.
"""
import os
import sys
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import social_envelope as env      # noqa: E402
import social_matriz as mz         # noqa: E402
import falhas                      # noqa: E402  — a lingua unica do erro
import social_sessao as ss         # noqa: E402  — LOCAL_SESSION e rota, nao motor
import scrap_http as http          # noqa: E402  — o portao e a busca
import scrap_registo as reg        # noqa: E402  — o mapa, dono unico
import scrap_capacidades as cap    # noqa: E402  — a declaracao
import coletor                     # noqa: E402  — o dono do dinheiro
import autorizacao_de_gasto as _ag  # noqa: E402  — so o TIPO da recusa

# ── O QUE MUDOU DE SITIO, E CONTINUA A ATENDER PELO NOME ANTIGO ───────────
# Codigo vivo e testes ja chamam `social_rotas.permitido`. Mudar o ficheiro de
# sitio nao e razao para lhes partir a chamada.
AGENTE = http.AGENTE
TIMEOUT = http.TIMEOUT
PAUSA_ENTRE_CHAMADAS = http.PAUSA_ENTRE_CHAMADAS
RotaNaoPermitida = http.RotaNaoPermitida
RotaBloqueada = http.RotaBloqueada
PortaoIndisponivel = http.PortaoIndisponivel
SemOrcamentoDeRede = http.SemOrcamentoDeRede
#: A recusa do teto de DINHEIRO. Vem do dono do dinheiro, e nao daqui — este
#: ficheiro autoriza a rota paga, nunca decide ATE QUANTO.
#:
#:     PAID_ROUTE_AUTHORIZATION != FINANCIAL_BUDGET.
SemOrcamentoFinanceiro = coletor.SemOrcamentoFinanceiro
#: A recusa da GUARDA DE AUTORIZACAO — o terceiro eixo, e o unico que nao fala
#: de saldo. So o TIPO vem daqui: este ficheiro nao concede autorizacao nenhuma
#: e nao abre o livro de relevancia.
#:
#:     SALDO ESGOTADO != NINGUEM AUTORIZOU.
GastoRecusado = _ag.GastoRecusado
_EstadoDaApi = http.EstadoDaApi
permitido = http.permitido
_get = http.buscar

# ── A COSTURA DE TESTE, QUE EM PRODUCAO FICA VAZIA ────────────────────────
# Um teste precisa de injetar um adaptador que rebenta de proposito, para
# provar que o despachante classifica a falha. O registo recusa capacidade nao
# declarada — e bem, porque registar o que ninguem mediu e prometer o que nao
# existe. Entao a injecao tem um sitio proprio, com nome que diz o que e.
#
#     EM PRODUCAO ISTO ESTA VAZIO, E HA UM TESTE QUE O EXIGE VAZIO.
#
# E a diferenca entre uma costura e um segundo dono: o segundo dono enche-se
# sozinho com o tempo, e ninguem repara.
ADAPTADORES = {}


def _rota_executavel(plat, cap_grossa):
    """→ a funcao que executa, pelo dono unico do mapa.

    A capacidade grossa da matriz — `INCREMENTAL`, `SEARCH_KEYWORD` — e
    traduzida para o nome declarado antes da busca. Os dois vocabularios
    coexistem sem que um se imponha ao outro.
    """
    if (plat, cap_grossa) in ADAPTADORES:
        return ADAPTADORES[(plat, cap_grossa)]
    reg.carregar_adaptadores()
    nome = cap.pela_matriz(plat, cap_grossa)
    return reg.rota_de(plat, nome) if nome else None


def _executar(*, platform, capability, run_id, country_scope='IT',
            permitir_pago=False, motivo_pago=None, ownership=None, **kwargs):
    """Escolhe a rota declarada e executa. Devolve (objetos, registro).

    O registro é gravado MESMO quando a rota falha — recusa e bloqueio são
    resultado de medição, não ausência de resultado.
    """
    plat, cap = platform.upper(), capability.upper()
    # O padrão é TERCEIRO. Ler dado de outra empresa é o caso perigoso, então é
    # ele que precisa ser o padrão — quem for ler conta PRÓPRIA declara.
    ownership = ownership or ss.THIRD_PARTY
    rotas = (mz.MATRIZ.get(plat) or {}).get(cap)
    registro = {
        'PLATFORM': plat, 'CAPABILITY': cap, 'RUN_ID': run_id,
        'COUNTRY_SCOPE': country_scope, 'QUANDO': env.agora(),
        'ROTA_ESCOLHIDA': None, 'CLASSE_DA_ROTA': None,
        'AUTH_MODE': None, 'ESTADO': None, 'OBJETOS': 0,
        'COST_USD': 0.0, 'ERRO': None, 'MOTIVO_PAGO': None,
        # ── O QUE SE SABE DO CUSTO, QUE NAO E O CUSTO ────────────────────────
        # `COST_USD` e um numero e comeca em zero. Um numero sozinho nao
        # distingue «a rota nao correu» de «a rota correu e foi de graca» de
        # «a rota correu, era paga, e ninguem conseguiu ler quanto custou».
        #
        #     NOT_RUN != 0. UNKNOWN != 0.
        #
        # Entao o EIXO do conhecimento e um campo proprio, e comeca no unico
        # valor que e sempre verdade antes de a rota correr.
        'COST_STATE': 'NOT_RUN', 'ACTUAL_COST_USD': None,
        # ── O BALDE DA MEDIDA ────────────────────────────────────────────────
        # `COST_USD` ja era o eixo do gasto em dolar. Falta o eixo da QUOTA: uma
        # API oficial e gratuita e NAO e infinita, e quem gasta unidades e a
        # rota — o roteador nao tem como saber quantas.
        #
        #     UM EIXO SEM CAMPO E MEDIDO POR PALPITE DE QUEM LE.
        #
        # Este dicionario vai PARA a rota, e e o MESMO objeto que volta dentro
        # do registo. Por isso a medida sobrevive a recusa e ao erro: uma rota
        # que gastou quota e so depois levou 403 gastou na mesma, e apagar isso
        # faria o relatorio dizer que a execucao foi de graca.
        #
        # Generico de proposito. Nao ha nome de plataforma aqui, e nao vai
        # haver: quem sabe o preco da chamada e o dono da chamada.
        'MEDIDA': {},
    }
    if not rotas:
        registro['ESTADO'] = 'NOT_APPLICABLE'
        registro['ERRO'] = 'capacidade não declarada na matriz para esta plataforma'
        return [], registro

    escolhida = mz._rota_padrao(rotas)
    if escolhida is None:
        registro['ESTADO'] = 'ROUTE_NOT_ALLOWED'
        registro['ERRO'] = 'nenhuma rota permitida para %s/%s' % (plat, cap)
        return [], registro
    registro['ROTA_ESCOLHIDA'] = escolhida['ROTA']
    # A CLASSE sobe junto com a rota. Sem ela, quem le o registo teria de
    # adivinhar pelo NOME da rota se aquilo foi API oficial, Apify ou HTTP —
    # e adivinhar pelo nome e como se escreve a primeira mentira do trace.
    registro['CLASSE_DA_ROTA'] = escolhida['CLASSE']

    registro['AUTH_MODE'] = mz.auth_mode(escolhida)

    # ── A TRAVA DA SESSÃO ────────────────────────────────────────────────────
    # Estar logado não autoriza automatizar. A pergunta é sobre o CONTRATO com
    # a plataforma e sobre DE QUEM É a conta alvo — nunca sobre o que a máquina
    # consegue fazer. Por isso ela roda ANTES de qualquer navegação, e nem
    # sequer consulta o preflight: recusa por termo não depende de ter Chrome.
    if escolhida['CLASSE'] == 'LOCAL_SESSION':
        ok_auto, porque = ss.automacao_permitida(plat, ownership)
        registro['OWNERSHIP'] = ownership
        if not ok_auto:
            registro['ESTADO'] = ss.AUTOMATION_NOT_ALLOWED
            registro['ERRO'] = ss.redigir(porque)
            return [], registro
        pre = ss.preflight()
        # O preflight vai para o registro REDIGIDO e sem caminho de perfil.
        registro['SESSION_STATE'] = pre['ESTADO']
        if pre['ESTADO'] != ss.SESSION_AVAILABLE:
            registro['ESTADO'] = pre['ESTADO']
            registro['ERRO'] = ss.redigir(pre['PORQUE'])
            return [], registro

    # A trava do gasto. Rota paga só passa com motivo do vocabulário fechado —
    # e "a Apify já estava configurada" não está no vocabulário.
    if escolhida['CLASSE'] in ('APIFY', 'OFFICIAL_API_PAID'):
        if not permitir_pago:
            registro['ESTADO'] = 'PAID_ROUTE_REFUSED'
            registro['ERRO'] = ('a rota padrão é PAGA (%s) e esta execução não autorizou '
                                'gasto' % escolhida['CLASSE'])
            return [], registro
        if motivo_pago not in mz.MOTIVOS_PAGOS:
            registro['ESTADO'] = 'PAID_ROUTE_REFUSED'
            registro['ERRO'] = ('motivo de gasto fora do vocabulário canônico: %r. '
                                'Aceitos: %s' % (motivo_pago, ', '.join(mz.MOTIVOS_PAGOS)))
            return [], registro
        registro['MOTIVO_PAGO'] = motivo_pago

    fn = _rota_executavel(plat, cap)
    if fn is None:
        registro['ESTADO'] = ('CREDENTIAL_MISSING'
                              if escolhida['ESTADO'] == 'CREDENTIAL_MISSING'
                              else 'POSSIBLE_NOT_PROVED')
        registro['ERRO'] = ('rota declarada e permitida, mas sem adaptador nesta missão: %s'
                            % escolhida['ROTA'])
        return [], registro

    try:
        objetos = fn(run_id=run_id, country_scope=country_scope,
                     medida=registro['MEDIDA'], **kwargs)
    except (SemOrcamentoDeRede, SemOrcamentoFinanceiro, GastoRecusado):
        # As recusas dos TRES PORTOES sobem inteiras ate ao executor, que e quem
        # sabe qual era cada um. Traduzi-las aqui para um estado de rota faria a
        # casa dizer que a fonte recusou quando fomos nos.
        #
        #     ESGOTAR O ORCAMENTO NAO E A FONTE ESTAR VAZIA,
        #     E TAMBEM NAO E A PLATAFORMA IMPEDIR.
        #
        # E sao TRES excecoes e nao uma porque sao tres eixos: a primeira diz
        # «nao cabe mais uma ida», a segunda «nao cabe mais exposicao», a
        # terceira «ninguem respondeu por esta compra». Colapsa-las faria o
        # rasto mentir sobre qual dos tres parou a execucao — e a terceira e a
        # unica cuja resposta nao esta em nenhum saldo.
        #
        # ⚠️ A TERCEIRA ENTROU NA CV-01, e nao por elegancia: ate ai
        # `GastoRecusado` herdava de `PermissionError`, caia no balde generico
        # deste ficheiro e subia como `UNKNOWN_ERROR` — ou, pior, apanhada como
        # `OSError` mais acima, como `TRANSIENT_NETWORK_ERROR`, que pede WAIT.
        # Quem le WAIT chama outra vez, e a chamada seguinte e uma compra.
        raise
    except RotaNaoPermitida as e:
        registro['ESTADO'] = 'ROUTE_NOT_ALLOWED'
        registro['ERRO'] = ss.redigir(str(e))
        return [], registro
    except _EstadoDaApi as e:
        # A API disse o que houve. Não reinterpretamos: gravamos o que ela disse.
        registro['ESTADO'] = e.rel.get('STATE')
        registro['NATIVE_REASON'] = e.rel.get('NATIVE_REASON')
        registro['RECOVERY_ACTION'] = e.rel.get('RECOVERY_ACTION')
        registro['ERRO'] = ss.redigir(str(e))
        return [], registro
    except RotaBloqueada as e:
        registro['ESTADO'] = 'BLOCKED'
        registro['ERRO'] = ss.redigir(str(e))
        return [], registro
    except urllib.error.HTTPError as e:
        # O código da resposta é a melhor prova que existe. 401/403 não é vazio,
        # 429 não é fonte caída, 5xx é a FONTE e 4xx é PEDIDO NOSSO.
        registro['ESTADO'] = falhas.classificar(http=e.code)
        registro['ERRO'] = ss.redigir('HTTP %s: %s' % (e.code, e))
        return [], registro
    except (PortaoIndisponivel, urllib.error.URLError, TimeoutError,
            ConnectionError, OSError) as e:
        # Transporte caiu. NÃO é rota morta e NÃO é fonte vazia.
        #
        # `PortaoIndisponivel` entra AQUI, e não no balde genérico, porque ela
        # é exatamente isto: o portão não conseguiu LER o robots.txt. A C10.8A
        # mediu ao vivo o que custava a diferença — um túnel que caiu fazia o
        # trilho dizer `ROUTE_NOT_ALLOWED` sobre uma rota cujo host responde
        # `Allow: /`.
        #
        #     UM TRANSPORTE QUE CAIU NÃO É UMA POLÍTICA QUE RECUSOU.
        registro['ESTADO'] = 'TRANSIENT_NETWORK_ERROR'
        registro['ERRO'] = ss.redigir('%s: %s' % (type(e).__name__, e))
        return [], registro
    except (KeyError, IndexError, AttributeError, TypeError, ValueError) as e:
        # A fonte respondeu e o NOSSO extrator não achou o campo. Este é o estado
        # que o balde `FAILED` escondia — e o único aqui que pede gente.
        #
        #     PARSER QUEBRADO NÃO É FONTE VAZIA.
        registro['ESTADO'] = 'PARSER_DRIFT'
        registro['ERRO'] = ss.redigir('%s: %s' % (type(e).__name__, e))
        return [], registro
    except Exception as e:
        # A exceção é REDIGIDA antes de virar registro. Um traceback de urllib
        # carrega a URL, e a URL pode carregar o token — foi assim que segredo
        # vazou em casa alheia sem ninguém ter escrito `print(cookie)`.
        registro['ESTADO'] = 'UNKNOWN_ERROR'
        registro['ERRO'] = ss.redigir('%s: %s' % (type(e).__name__, e))
        return [], registro

    registro['ESTADO'] = 'OK' if objetos else 'ZERO_RESULTS'
    registro['OBJETOS'] = len(objetos)
    # ── A ROTA CORREU. O QUE SE SABE DO CUSTO DELA? ──────────────────────────
    # Quem sabe o preco da chamada e o dono da chamada, e ele declara-o na
    # MEDIDA. Este ficheiro nao inventa numero nenhum: ele so sabe a CLASSE, e
    # a classe responde uma coisa so — se a politica declara a rota gratuita,
    # entao zero e um facto e nao um palpite.
    #
    # Uma rota PAGA que correu e nao declarou custo e o caso perigoso: o numero
    # existe do lado do provider e nao chegou ca. Isso e `UNKNOWN`, nunca zero.
    medida = registro.get('MEDIDA') or {}
    if 'COST_STATE' in medida:
        registro['COST_STATE'] = medida['COST_STATE']
        registro['ACTUAL_COST_USD'] = medida.get('ACTUAL_COST_USD')
    elif escolhida['CLASSE'] in ('APIFY', 'OFFICIAL_API_PAID'):
        registro['COST_STATE'] = 'UNKNOWN'
    else:
        registro['COST_STATE'] = 'FREE_ROUTE_BY_POLICY'
        registro['ACTUAL_COST_USD'] = 0.0
    if registro.get('ACTUAL_COST_USD') is not None:
        registro['COST_USD'] = registro['ACTUAL_COST_USD']
    return objetos, registro


def executar(**kwargs):
    """Porta única. Sela TODA saída com a taxonomia canônica — nenhum caminho escapa.

    O selo é aplicado aqui, e não em cada `return`, porque um `return` novo daqui a
    três meses esqueceria de selar. Envolver é a única forma que não depende de
    alguém lembrar.
    """
    objetos, registro = _executar(**kwargs)
    return objetos, selar(registro)


def selar(registro):
    """Traduz o estado para o vocabulário canônico e anexa o que ele significa."""
    bruto = registro.get('ESTADO')
    if bruto is None:
        return registro
    canon = falhas.traduzir(bruto)
    registro['ESTADO'] = canon
    if bruto != canon:
        registro['ESTADO_ORIGINAL'] = bruto
    camada, saude = falhas.saude(canon)
    registro['FAILURE_LAYER'] = camada
    registro['EXPECTED'] = falhas.esperado(canon)
    registro['DEGRADES_SOURCE'] = falhas.degrada_fonte(canon)
    registro.setdefault('RECOVERY_ACTION',
                        falhas.recuperacao(canon, registro.get('NATIVE_REASON')))
    registro['SOURCE_HEALTH'] = saude if camada == falhas.SOURCE else falhas.HEALTHY
    registro['ROUTE_HEALTH'] = saude if camada == falhas.ROUTE else falhas.HEALTHY
    registro['EXECUTOR_HEALTH'] = saude if camada == falhas.EXECUTOR else falhas.HEALTHY
    return registro
