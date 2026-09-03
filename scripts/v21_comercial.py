#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O LADO COMERCIAL · o catálogo dos 51 e a prioridade que ele sustenta.

    import v21_comercial as C

DOIS CATÁLOGOS QUE NÃO SÃO O MESMO CATÁLOGO
--------------------------------------------
`PRODUCTS-REGULATORY.json` traz **163**: tudo o que tem autorização ministerial
viva em Itália sob titularidade rastreável. `PRODUCTS-COMMERCIAL.json` traz
**51**: o que a ADAMA publica no próprio catálogo comercial.

O V1 carregava o segundo e nunca o consultava. Resultado medido: dos 77 produtos
citados nas 37 oportunidades, **77 saíam dos 163** e nenhum era conferido contra
os 51. Uma oportunidade podia nomear um produto que a empresa não oferece.

    AUTORIZAÇÃO NÃO É CATÁLOGO, E CATÁLOGO NÃO É RÓTULO.
    O REGISTRO DIZ QUE PODE. O CATÁLOGO DIZ QUE HÁ. O RÓTULO DIZ PARA QUÊ.

As duas camadas ficam, lado a lado. A regulatória não é apagada: ela é o que
prova o direito de uso. A comercial responde outra pergunta — «isto existe para
vender hoje?» — e é ela que a prioridade comercial exige.

A CHAVE DA JUNÇÃO
-----------------
`MATCHED_REGULATORY_ID` do catálogo comercial contra `REGISTRATION_NUMBER` do
rótulo, ambos reduzidos a dígitos e preenchidos com zeros à esquerda. Nunca por
nome: `Lamdex® Extra`, `LAMDEX EXTRA` e `Lamdex Extra` são três grafias do mesmo
registro, e casar por texto reintroduz o erro que a normalização já resolveu.

    NOME COMERCIAL É GRAFIA. NÚMERO DE REGISTRO É IDENTIDADE.
"""
import re

# ── OS CINCO ESTADOS DA PRIORIDADE COMERCIAL ─────────────────────────────────
SALES_READY = 'SALES_READY'
SALES_PREPARE = 'SALES_PREPARE'
COMMERCIAL_WATCH = 'COMMERCIAL_WATCH'
STRATEGIC_OPPORTUNITY = 'STRATEGIC_OPPORTUNITY'
TO_VALIDATE = 'TO_VALIDATE'

PRIORIDADES = (SALES_READY, SALES_PREPARE, COMMERCIAL_WATCH,
               STRATEGIC_OPPORTUNITY, TO_VALIDATE)

# O que cada estado significa, em uma frase que vai à tela.
SIGNIFICADO = {
 SALES_READY: 'necessidade externa corrente e positiva, produto do catálogo '
              'comercial com rótulo no par cultura × alvo, geografia que se '
              'sustenta e tempo para agir.',
 SALES_PREPARE: 'a relação comercial fecha, mas o momento é de preparação: a '
                'janela é futura ou o tempo ainda não tem precisão para agir.',
 COMMERCIAL_WATCH: 'há abertura comercial relevante — mercado, concorrente ou '
                   'voz — e portfólio comercial na cultura, mas não há '
                   'necessidade agronômica corrente que a sustente.',
 STRATEGIC_OPPORTUNITY: 'importa à ADAMA e não deve ser apresentado como venda '
                        'agora: prazo regulatório longo, ciência sem presença '
                        'corrente, ou mudança estrutural de mercado.',
 TO_VALIDATE: 'falta um elemento indispensável, ou a evidência se contradiz.',
}

# ── AS RAZÕES, FIXAS POR CÓDIGO ──────────────────────────────────────────────
# ⚠️ FRASE COM VARIÁVEL DENTRO NUNCA FICA TRADUZIDA. A memória de tradução
# chaveia pelo próprio texto em português; uma frase que muda a cada caso é
# frase nova a cada build, e nasce sem irmã em italiano. Este projeto já cometeu
# isso duas vezes, e a primeira versão desta camada quase o cometeu de novo:
# «a fonte que sustenta o caso não manda agir: ACTION_SUSPENDED» eram quatro
# frases diferentes para a mesma razão.
#
#     O CÓDIGO É DADO. A FRASE É TEXTO. O VALOR VARIÁVEL VIVE NO CAMPO AO LADO.
#
# O valor que faltava na frase já está estruturado em `NEED_DIRECTION`,
# `COMMERCIAL_WINDOW` e `COMMERCIAL_PRODUCT_COUNT` — a tela lê de lá.
RAZAO = {
 'NEED_CLOSED': 'a fonte que sustenta o caso não manda agir — ver NEED_DIRECTION '
                'e a frase original em NEED_EXCERPT.',
 'REGULATORY_BY_NATURE': 'data regulatória europeia é preparação de portfólio e '
                         'de supply, não necessidade de campo.',
 'REGULATORY_WITHOUT_CATALOG': 'e nenhum dos produtos ADAMA que contêm a '
                               'substância está no catálogo comercial público: '
                               'a preparação é regulatória, não comercial.',
 'LABEL_WITHOUT_CATALOG': 'há rótulo ministerial verificado, mas nenhum dos '
                          'produtos autorizados está no catálogo comercial '
                          'público: autorização não é catálogo.',
 'NO_COMMERCIAL_PRODUCT': 'nenhum produto do catálogo comercial ADAMA cobre '
                          'esta cultura.',
 'TARGET_WITHOUT_LABEL': 'há alvo agronômico, mas nenhum rótulo verificado no '
                         'par cultura × alvo.',
 'NEED_NOT_POSITIVE': 'há par e produto, mas a fonte não declara necessidade '
                      'positiva corrente — ver NEED_DIRECTION.',
 'GEOGRAPHY_DOES_NOT_HOLD': 'a necessidade é positiva, mas a geografia da '
                            'afirmação não se sustenta no apoio que a carrega.',
 'ALL_GATES_CLOSE': 'necessidade positiva corrente, produto do catálogo com '
                    'rótulo no par, geografia que se sustenta e tempo para agir.',
 'TIME_FROM_APPLICATION_WINDOW': 'e o tempo vem de uma janela de aplicação com '
                                 'datas — ver COMMERCIAL_WINDOW.',
 'TIME_FROM_SOURCE_RECOMMENDATION': 'e o tempo vem da recomendação corrente da '
                                    'própria fonte, que não traz datas de '
                                    'calendário — ver NEED_EXCERPT e '
                                    'SIGNAL_CURRENCY. Isto NÃO é janela de '
                                    'aplicação, e por isso não autoriza ACT_NOW.',
 'TIME_NOT_PRECISE': 'necessidade, produto e geografia fecham; falta precisão '
                     'de tempo para agir — ver COMMERCIAL_WINDOW.',
 'OPENING_WITHOUT_NEED': 'há portfólio comercial na cultura e movimento externo, '
                         'mas o caso não nomeia problema agronômico.',
 'NEITHER_NEED_NOR_OPENING': 'o caso não nomeia problema agronômico e não é '
                             'abertura de mercado nem preparação regulatória.',
}

# ⚠️ CÓDIGOS QUE NÃO ENTRAM NA FRASE. Medido ao criar os dois códigos de
# relógio: `WHY_COMMERCIAL` é composto por junção das frases dos códigos, e uma
# junção nova é uma FRASE NOVA — nasce sem irmã na memória de tradução e a
# aceitação a acusa como «ainda só em português». Estes códigos são DADO: a
# resposta estruturada deles vive em `COMMERCIAL_TIMING_BASIS`.
#
#     ACRESCENTAR UMA ORAÇÃO A UMA FRASE TRADUZIDA CRIA UMA FRASE NOVA.
#     O CÓDIGO NOVO VAI NA LISTA DE CÓDIGOS, NÃO DENTRO DA FRASE.
SO_CODIGO = ('TIME_FROM_APPLICATION_WINDOW', 'TIME_FROM_SOURCE_RECOMMENDATION')


def frase(codigos):
    """→ a frase de WHY_COMMERCIAL, sem os códigos que são só dado."""
    return ' '.join(RAZAO[c] for c in codigos if c not in SO_CODIGO)


# O que NENHUM estado prova. Vale para os cinco, e vai junto com o cartão.
NAO_PROVA = ('NÃO prova demanda de revenda, sell-in, sell-out, pedido, estoque, '
             'margem, pipeline nem intenção de compra. Nada aqui vem de dado '
             'interno da ADAMA. Pressão agronômica é oportunidade comercial '
             'externa a examinar — não é demanda.')

# Direções de necessidade que ABREM a porta comercial (ver v21_necessidade).
NECESSIDADE_POSITIVA = ('POSITIVE_PRESSURE',)
# As que a FECHAM: o documento manda parar, suspender, concluir ou proíbe.
NECESSIDADE_FECHADA = ('NO_ACTION_RECOMMENDED', 'ACTION_SUSPENDED',
                       'WINDOW_CONCLUDED', 'TREATMENT_PROHIBITED')
# As que nem abrem nem fecham: há assunto, não há ordem de agir.
NECESSIDADE_MORNA = ('MONITOR', 'NEUTRAL_MENTION', 'UNKNOWN')

# Arquétipos cuja natureza é preparação, não venda.
ARQ_ESTRATEGICO = ('O5_REGULATORY_PREPARATION',)
# Arquétipos que são abertura comercial sem necessidade agronômica própria.
ARQ_ABERTURA = ('O2_MARKET_MOMENT', 'O4_COMPETITIVE_OPENING')


# ── O QUE PODE SAIR DA ADAMA ─────────────────────────────────────────────────
# SALES_READY responde «isto vende?». Ele NÃO responde «isto pode ser enviado a
# um revendedor ou a um RTV hoje?». São perguntas diferentes, e confundi-las é o
# jeito mais rápido de pôr uma inferência nossa na mão de terceiro como se fosse
# recomendação técnica.
#
#     VENDER É UMA DECISÃO INTERNA. ENVIAR É UMA AFIRMAÇÃO PÚBLICA.
#     A SEGUNDA PRECISA SOBREVIVER A QUEM A LER SEM NOS CONHECER.
EXTERNAL_YES = 'YES'
EXTERNAL_VALIDATION_REQUIRED = 'VALIDATION_REQUIRED'
EXTERNAL_NO = 'NO'

# Por que um caso não pode sair. Frases FIXAS — o valor variável vive ao lado.
BLOQUEIO_EXTERNO = {
 'NOT_SALES_READY': 'o caso não é comercialmente pronto nem internamente — '
                    'ver COMMERCIAL_PRIORITY e WHY_COMMERCIAL.',
 'EVIDENCE_GATE_OPEN': 'há portão de evidência aberto sobre a mesma afirmação '
                       'que o material levaria — ver BLOCKING_GATES.',
 'RED_TEAM_FINDING': 'o red team registrou uma extrapolação neste caso — ver '
                     'RED_TEAM_FINDINGS.',
 'CATALOG_DOES_NOT_DECLARE_CROP': 'o rótulo ministerial cobre o par, mas a '
                                  'página de catálogo do produto não declara '
                                  'esta cultura. Enviar assim faria o material '
                                  'afirmar mais do que o catálogo público diz.',
 'WINDOW_IS_ADMINISTRATIVE': 'a janela exibida no caso é data de ato, não '
                             'janela de aplicação — ver WINDOW_KIND.',
 'NO_SOURCE_SENTENCE': 'não há frase da fonte guardada para sustentar a '
                       'necessidade — ver NEED_EXCERPT.',
}

# A lei, em uma linha, para viajar com o campo.
EXTERNAL_LAW = ('SALES_READY sozinho NAO autoriza saida externa. Material que '
                'vai da ADAMA para revendedor ou RTV exige vinculo produto x '
                'cultura x alvo sustentado, geografia sem contradicao, tempo '
                'aplicavel, nenhum portao de evidencia sobre a mesma afirmacao '
                'e nenhuma inferencia nossa apresentada como recomendacao. '
                'VALIDATION_REQUIRED nao rebaixa a leitura interna: ele diz o '
                'que falta antes de a frase sair de casa.')


def num(x):
    """Número de registro reduzido à identidade: só dígitos, seis casas."""
    return re.sub(r'\D', '', str(x or '')).lstrip('0').zfill(6)


def indice_comercial(produtos_comerciais):
    """→ {número de registro: [registro do catálogo]}.

    Dos 51 do catálogo, 38 trazem `MATCHED_REGULATORY_ID`. Os outros 13 não são
    descartados nem casados por nome: ficam fora do índice, e a contagem os
    declara. Um produto que o catálogo publica sem número de registro é um
    produto cuja autorização não sabemos ligar — e isso é um `NÃO SEI`, não um
    palpite.
    """
    ix = {}
    for p in produtos_comerciais:
        n = num(p.get('MATCHED_REGULATORY_ID') or p.get('REGISTRATION_NUMBER_ON_PAGE'))
        if n != '000000':
            ix.setdefault(n, []).append(p)
    return ix


def casar(rotulos, ix_comercial):
    """→ COMMERCIAL_PRODUCT_MATCH sobre uma lista de pares de rótulo.

    O par de rótulo é a ponte: ele traz o número de registro e diz para que
    cultura e que alvo aquele registro está autorizado. Casar o número contra o
    catálogo responde a pergunta comercial sem inventar nada.
    """
    ids, nomes = [], []
    for r in rotulos:
        for p in ix_comercial.get(num(r.get('REGISTRATION_NUMBER')), []):
            if p['ID'] not in ids:
                ids.append(p['ID'])
                nomes.append(p.get('NAME'))
    ordem = sorted(range(len(ids)), key=lambda i: (nomes[i] or '').upper())
    return {
        'MATCHED_COMMERCIAL_PRODUCT_IDS': [ids[i] for i in ordem],
        'MATCHED_COMMERCIAL_PRODUCT_NAMES': [nomes[i] for i in ordem],
        'COMMERCIAL_PRODUCT_COUNT': len(ids),
        'COMMERCIAL_MATCH_LAW': 'casado por NUMERO DE REGISTRO entre o catalogo '
                                'comercial e o par de rotulo. Nunca por nome. '
                                'Produto regulatorio nao vira produto comercial '
                                'automaticamente.',
    }


# ── A PRIORIDADE, POR PORTÕES SEMÂNTICOS ─────────────────────────────────────
def prioridade(o):
    """→ (COMMERCIAL_PRIORITY, [códigos de RAZAO]). Portões, não soma de pontos.

    Devolve CÓDIGOS, não frases: a frase correspondente está em `RAZAO`, fixa, e
    o valor variável que ela não carrega dentro vive em `NEED_DIRECTION`,
    `COMMERCIAL_WINDOW` e `COMMERCIAL_PRODUCT_COUNT`.


    O score continua ordenando dentro de uma mesma categoria; ele não promove
    ninguém de categoria.

        UM 12 COM A NECESSIDADE FECHADA CONTINUA SENDO UM 12 COM A NECESSIDADE
        FECHADA.

    E NÃO há exigência de número mínimo de famílias externas. Uma fonte oficial
    forte que feche necessidade, portfólio, geografia e tempo basta; uma segunda
    família amplifica e ordena, não autoriza.

        CORROBORAÇÃO É AMPLIFICADOR, NÃO CONTADOR CEGO.
    """
    r = []
    arq = o.get('ARCHETYPE')
    need = o.get('NEED_DIRECTION') or 'UNKNOWN'
    comercial = (o.get('COMMERCIAL_PRODUCT_COUNT') or 0) > 0
    rotulo_par = o.get('PRODUCT_LINK_STATE') == 'VERIFIED_LABEL_MATCH' and bool(o.get('TARGET'))
    geo_ok = o.get('CLAIM_GEOGRAPHY_HOLDS') is True
    quando = o.get('COMMERCIAL_WINDOW') or 'UNKNOWN'

    # ── 1 · contradição declarada: a fonte manda parar ────────────────────────
    if need in NECESSIDADE_FECHADA:
        return TO_VALIDATE, r + ['NEED_CLOSED']

    # ── 2 · o caso é de preparação por natureza ───────────────────────────────
    # O arquétipo O5 nasce de uma data europeia sobre substância que produtos
    # ADAMA registrados contêm. Isso é trabalho de REGULATORY, PORTFOLIO e
    # SUPPLY, e vale exista ou não entrada no catálogo comercial: a ausência de
    # catálogo torna o caso menos vendável, não menos estratégico.
    #
    #     DATA REGULATÓRIA NÃO É RISCO COMERCIAL, E TAMBÉM NÃO É VENDA.
    if arq in ARQ_ESTRATEGICO:
        r.append('REGULATORY_BY_NATURE')
        if not comercial:
            r.append('REGULATORY_WITHOUT_CATALOG')
        return STRATEGIC_OPPORTUNITY, r

    # ── 3 · sem produto comercial não há o que vender ─────────────────────────
    if not comercial:
        # A distinção que o V1 não fazia: o registro autoriza, o catálogo não
        # oferece. As duas coisas são verdade ao mesmo tempo.
        r.append('LABEL_WITHOUT_CATALOG' if
                 o.get('PRODUCT_LINK_STATE') == 'VERIFIED_LABEL_MATCH'
                 else 'NO_COMMERCIAL_PRODUCT')
        return TO_VALIDATE, r

    # ── 4 · problema agronômico declarado: o caminho da venda ─────────────────
    if o.get('TARGET'):
        if not rotulo_par:
            return TO_VALIDATE, r + ['TARGET_WITHOUT_LABEL']
        if need not in NECESSIDADE_POSITIVA:
            # MONITOR não fecha a porta: o serviço manda observar, e observar é
            # a antessala de tratar. O que não se pode é chamar isso de venda.
            return (SALES_PREPARE if need == 'MONITOR' else TO_VALIDATE,
                    r + ['NEED_NOT_POSITIVE'])
        if not geo_ok:
            return SALES_PREPARE, r + ['GEOGRAPHY_DOES_NOT_HOLD']
        # ── o tempo, e QUAL RELÓGIO o declarou ───────────────────────────────
        # Medido: o motor vinha chamando de `ACT_NOW` a IDADE DO SINAL quando não
        # havia janela — e o cartão saía com «ACT NOW» ao lado de «no canonical
        # window linked». O conserto NÃO foi tirar o tempo dos casos: foi parar
        # de chamar os dois relógios pelo mesmo nome.
        #
        #     O BOLETIM DE ONTEM QUE MANDA INTERVIR DECLARA UM MOMENTO.
        #     ELE NÃO DECLARA UMA JANELA. AS DUAS COISAS SÃO VERDADE.
        #
        # A janela de aplicação é o relógio forte e é a ÚNICA que autoriza
        # `ACT_NOW` — essa regra vive no motor, em `elos_de_agora`. Aqui, para
        # dizer se há oportunidade comercial, a recomendação corrente da fonte
        # também conta — desde que o cartão diga que foi ela, e não uma janela.
        if quando in ('ACT_NOW', 'PREPARE_NOW'):
            return SALES_READY, r + ['ALL_GATES_CLOSE',
                                     'TIME_FROM_APPLICATION_WINDOW']
        if o.get('COMMERCIAL_TIMING_BASIS') == 'CURRENT_SOURCE_RECOMMENDATION':
            return SALES_READY, r + ['ALL_GATES_CLOSE',
                                     'TIME_FROM_SOURCE_RECOMMENDATION']
        return SALES_PREPARE, r + ['TIME_NOT_PRECISE']

    # ── 5 · sem alvo: abertura comercial, não necessidade ─────────────────────
    if arq in ARQ_ABERTURA:
        return COMMERCIAL_WATCH, r + ['OPENING_WITHOUT_NEED']

    return STRATEGIC_OPPORTUNITY, r + ['NEITHER_NEED_NOR_OPENING']


def catalogo_declara_cultura(crop, produtos_casados):
    """A página pública do produto nomeia esta cultura?

    ⚠️ Medido nesta revisão: `Lamdex® Extra` tem rótulo ministerial em
    `MELO × CARPOCAPSA`, e a página de catálogo dele declara
    `['MAIS', 'POMODORO', 'VITE']` — macieira não está lá. O rótulo autoriza; o
    catálogo público não anuncia. Para uso interno as duas coisas convivem; para
    material que sai de casa, a segunda é a que o leitor vai conferir.

        O RÓTULO DIZ O QUE É PERMITIDO. O CATÁLOGO DIZ O QUE A EMPRESA OFERECE.
        MATERIAL EXTERNO NÃO PODE PROMETER MAIS DO QUE O CATÁLOGO ANUNCIA.
    """
    import v21_normalizar as N
    for p in produtos_casados:
        for termo in (p.get('CROPS_DECLARED_ON_SITE') or []):
            if crop in N.crops_no_texto(termo):
                return True, p.get('NAME')
    return False, None


def externo(o, produtos_casados=()):
    """→ (EXTERNAL_MATERIAL_READY, [códigos de BLOQUEIO_EXTERNO]).

    Nunca deriva de `COMMERCIAL_PRIORITY` sozinho, e nunca esconde a
    independência das duas colunas: um caso pode continuar SALES_READY
    internamente e sair daqui como VALIDATION_REQUIRED.
    """
    if o.get('COMMERCIAL_PRIORITY') != SALES_READY:
        return EXTERNAL_NO, ['NOT_SALES_READY']

    b = []
    if o.get('BLOCKING_GATES'):
        b.append('EVIDENCE_GATE_OPEN')
    if o.get('RED_TEAM_FINDINGS'):
        b.append('RED_TEAM_FINDING')
    if not o.get('NEED_EXCERPT'):
        b.append('NO_SOURCE_SENTENCE')
    if o.get('WINDOW_KIND') == 'PREPARATION':
        b.append('WINDOW_IS_ADMINISTRATIVE')
    declara, _quem = catalogo_declara_cultura(o.get('CROP'), produtos_casados)
    if not declara:
        b.append('CATALOG_DOES_NOT_DECLARE_CROP')
    return (EXTERNAL_VALIDATION_REQUIRED if b else EXTERNAL_YES), b
