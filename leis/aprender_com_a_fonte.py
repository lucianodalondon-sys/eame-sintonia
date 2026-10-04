#!/usr/bin/env python3
"""O CONTRATO DA APRENDIZAGEM SOBRE A FONTE — sem numero magico.

    UMA FONTE NAO TEM UMA NOTA.
    TEM VARIAS MEDIDAS, E ELAS DISCORDAM.

A tentacao e obvia: juntar tudo num `SOURCE_SCORE` de 0 a 100 e ordenar. E
exactamente por ser obvia que ela e perigosa. Um numero so esconde qual das
medidas o produziu, e a partir dai ninguem consegue discutir a decisao — so
obedecer-lhe ou ignora-la, e as duas coisas sao mas.

    NAO HA SOURCE_SCORE AQUI, E E DE PROPOSITO.

Uma fonte cara que traz o que mais ninguem tem pode valer mais do que tres
baratas que se repetem. Uma fonte lenta pode ser a unica com profundidade
historica. Ordenar por um numero perde exactamente isso.

O QUE ISTO E
------------
Um CONTRATO: o vocabulario do ciclo de vida de uma fonte, do papel que ela
cumpre, e das medidas que se guardam sobre ela. Nao ha modelo, nao ha
pontuacao, e nada corre sozinho.

⚠️ E AS MEDIDAS SAO DE DUAS ESPECIES QUE NAO SE SOMAM
-----------------------------------------------------
    SAUDE DA FONTE  ela responde? mudou de forma? ainda existe?
    SAUDE DA ROTA   o caminho ate ela funciona?

Uma fonte perfeita atras de uma rota partida da o mesmo resultado pratico que
uma fonte morta — e a causa e completamente diferente. Somar as duas apaga a
unica coisa que diz o que fazer a seguir.

    SOURCE ≠ ROUTE. Outra vez, aqui.
"""

CONTRATO = 'APRENDER_COM_A_FONTE/v1'

# ─────────────────────────────────────────────────────────────────────────
# O CICLO DE VIDA — e nenhum degrau se salta sem prova
# ─────────────────────────────────────────────────────────────────────────
CICLO_DE_VIDA = (
    'DISCOVERED',    # alguem viu que existe
    'SCREENED',      # alguem olhou e disse que pode servir
    'TRIAL',         # esta a ser experimentada, com prazo
    'PROBATION',     # ja serviu, e ainda nao e de confianca
    'ACTIVE',        # em uso, com saude medida
    'DEGRADED',      # em uso, e a piorar. NAO e o mesmo que partida
    'QUARANTINED',   # suspensa por decisao escrita, e pode voltar
    'RETIRED',       # fora, e a historia dela fica
)

# ⚠️ DEGRADED != QUARANTINED != RETIRED.
# A primeira e uma medida, a segunda e uma decisao, a terceira e um fim.
# Achata-las faz uma fonte com um mau dia parecer morta — e faz uma morta
# continuar a ser tentada para sempre.

# ⚠️ RETIRED NAO APAGA HISTORIA. O que ela trouxe continua a valer; o que
# muda e que nao se vai la buscar mais nada.
RETIRAR_NAO_APAGA = (
    'uma fonte retirada continua dona do que ja trouxe. Apagar o passado dela '
    'para «limpar» faria desaparecer prova que outras coisas citam.'
)

# ─────────────────────────────────────────────────────────────────────────
# O PAPEL — para que serve esta fonte
# ─────────────────────────────────────────────────────────────────────────
# ⚠️ O papel muda o que conta como BOM. Uma fonte de DISCOVERY que se repete
# muito esta a falhar; uma de CORROBORATION que se repete esta a fazer o
# trabalho dela. A mesma medida, lida ao contrario.
PAPEIS = {
    'EVIDENCE': 'traz o facto em si',
    'DISCOVERY': 'aponta para onde ha facto novo',
    'EARLY_WARNING': 'chega antes das outras, mesmo que incompleta',
    'CORROBORATION': 'confirma o que outra ja disse',
    'CONTEXT': 'explica o pano de fundo, sem ser facto pontual',
    'REFERENCE': 'nao muda quase nunca, e serve de regua',
}

# ─────────────────────────────────────────────────────────────────────────
# AS MEDIDAS — guardadas em separado, e cada uma diz o que responde
# ─────────────────────────────────────────────────────────────────────────
SAUDE_DA_FONTE = {
    'RESPONDE': 'a fonte devolve alguma coisa',
    'FORMA_ESTAVEL': 'o que devolve continua com a forma declarada',
    'CADENCIA_OBSERVADA': 'de quanto em quanto tempo ela muda, medido',
    'CADENCIA_DECLARADA': 'de quanto em quanto tempo ela DIZ que muda',
}
SAUDE_DA_ROTA = {
    'ROTA_COMPLETA': 'a cadeia chega ao fim',
    'ULTIMA_PASSAGEM': 'quando foi a ultima vez que passou inteira',
    'FALHAS_POR_CODIGO': 'em que codigo de diagnostico ela costuma parar',
}

# ⚠️ CADENCIA DECLARADA != CADENCIA OBSERVADA.
# Um portal que promete boletim semanal e publica de mes a mes nao esta
# avariado — esta a mentir na promessa. Sao duas medidas, e a diferenca entre
# elas e informacao.

RENDIMENTOS = {
    'UNIQUE_YIELD': ('quanto do que ela traz mais ninguem trouxe. E o unico '
                     'numero que justifica manter uma fonte cara.'),
    'READY_YIELD': ('quanto do que ela traz chega a ser admitido. Trazer '
                    'muito e admitir pouco e trabalho a mais, nao valor.'),
    'CHANGE_RATE': 'quanto do que ela publica e novo',
    'DUPLICATE_RATE': 'quanto se repete — e o que isto quer dizer DEPENDE DO PAPEL',
    'COST': 'o que custa, na unidade da rota',
    'LATENCY': 'quanto tempo entre o facto acontecer e ela publicar',
}

# ⚠️ COLETADO != ADMITIDO.
# `UNIQUE_YIELD` alto com `READY_YIELD` baixo e uma fonte que da trabalho e
# nao entrega. Um numero so nao distingue os dois casos.

CAMPOS_DA_MEDIDA = (
    'SOURCE_ID', 'MEDIDA', 'VALOR', 'UNIDADE', 'JANELA',
    'MEDIDO_EM', 'COMO_FOI_MEDIDO', 'AMOSTRA',
)

# Sem amostra, uma taxa e uma impressao. 2 de 2 nao e 100%.
PORQUE_AMOSTRA = (
    'uma taxa sem denominador engana: 2 em 2 nao e o mesmo que 200 em 200, e '
    'as duas dao «100%». Toda medida guarda a amostra de onde saiu.'
)

# ─────────────────────────────────────────────────────────────────────────
# O QUE ESTE CONTRATO RECUSA
# ─────────────────────────────────────────────────────────────────────────
NAO_CRIAR = ('SOURCE_SCORE', 'RANKING_UNICO', 'NOTA_DE_0_A_100')
PORQUE_NAO_CRIAR = (
    'um numero so esconde qual das medidas o produziu, e a partir dai ninguem '
    'consegue discutir a decisao — so obedecer-lhe ou ignora-la. Uma fonte '
    'cara que traz o que mais ninguem tem pode valer mais do que tres baratas '
    'que se repetem, e ordenar por um numero perde exactamente isso.'
)

LEIS = (
    'UMA FONTE NAO TEM UMA NOTA — TEM VARIAS MEDIDAS, E ELAS DISCORDAM',
    'SAUDE DA FONTE != SAUDE DA ROTA',
    'DEGRADED != QUARANTINED != RETIRED',
    'CADENCIA DECLARADA != CADENCIA OBSERVADA',
    'COLETADO != ADMITIDO',
    'O QUE CONTA COMO BOM DEPENDE DO PAPEL',
    'RETIRAR NAO APAGA HISTORIA',
    'TAXA SEM AMOSTRA E IMPRESSAO',
)


def leitura_da_repeticao(papel, taxa):
    """A MESMA MEDIDA, LIDA AO CONTRARIO CONFORME O PAPEL.

    Uma fonte de DISCOVERY que se repete muito esta a falhar. Uma de
    CORROBORATION que se repete esta a fazer o trabalho dela.
    """
    if papel not in PAPEIS:
        return 'UNKNOWN', 'papel desconhecido: nao se le a taxa sem saber para que serve'
    if papel in ('CORROBORATION', 'REFERENCE'):
        return ('ESPERADO' if taxa >= 0.5 else 'ATENCAO',
                'repetir e o trabalho desta fonte')
    if papel in ('DISCOVERY', 'EARLY_WARNING'):
        return ('ATENCAO' if taxa >= 0.5 else 'ESPERADO',
                'esta fonte existe para trazer o que ainda nao ha')
    return 'NEUTRO', 'a repeticao nao diz nada sobre este papel sozinha'


def main():
    print('CONTRATO %s' % CONTRATO)
    print('ciclo de vida %d · papeis %d · rendimentos %d'
          % (len(CICLO_DE_VIDA), len(PAPEIS), len(RENDIMENTOS)))
    print('NAO CRIAR: %s' % ', '.join(NAO_CRIAR))
    for l in LEIS:
        print('  · %s' % l)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
