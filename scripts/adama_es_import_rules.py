#!/usr/bin/env python3
"""Regras de NORMALIZAÇÃO da fronteira de importação ADAMA España.

Elas não vivem no coletor da branch paralela nem no schema: vivem aqui, no
ponto onde o artefato vira linha canônica. É o único lugar onde as duas
decisões abaixo podem ser auditadas contra o texto literal da fonte.

RT-6 · BBCH
  O coletor lê `BBCH.search()` — a PRIMEIRA ocorrência — e, quando não há
  separador, faz `TO = FROM`. Num texto que diz "desde BBCH 00 (semilla
  seca) hasta BBCH 07" isso produz 00–00: uma janela de um estádio só onde a
  fonte declara sete. Medido: com cevada observada em BBCH 05, 00–07
  responde ACTIVE e 00–00 responde CLOSED.
  A regra abaixo nunca inventa o fim a partir do início.

RT-11 · origem do alvo
  ISSUE_RELATIONS nasce de varredura de texto sobre a PÁGINA INTEIRA. O
  coletor confere cultivo contra o bloco "Cultivos" declarado; para alvo não
  existe bloco equivalente na fonte, então nenhuma linha de alvo tem origem
  declarada. Resultado medido: os 56 produtos carregam pelo menos um termo
  de erva daninha — inclusive 25 que não são herbicida.
  A regra abaixo não apaga termo por lista: ela classifica ORIGEM e só
  admite como alvo autorizado o que veio de uma linha de tabela ancorada.

Uso:
    python3 scripts/adama_es_import_rules.py --autoteste
"""
import re
import sys

NAO_SEI = 'NÃO SEI'

# Uma menção isolada de estádio. O separador da FAIXA é tratado depois, de
# propósito: juntar as duas coisas na mesma regex foi o defeito de origem.
MENCAO_BBCH = re.compile(r'bbch\s*:?\s*(\d{1,2})', re.I)
# Faixa escrita com traço na mesma menção: "BBCH 12-29".
FAIXA_COM_TRACO = re.compile(r'bbch\s*:?\s*(\d{1,2})\s*[-–—]\s*(\d{1,2})', re.I)
# Linguagem que LIGA duas menções numa faixa.
LIGA_FAIXA = (
    (re.compile(r'\bdesde\b.*?\bhasta\b', re.I | re.S), 'desde…hasta'),
    (re.compile(r'\bentre\b.*?\by\b', re.I | re.S), 'entre…y'),
    (re.compile(r'\bdel\b.*?\bal\b', re.I | re.S), 'del…al'),
    (re.compile(r'\bde\b\s*bbch.*?\ba\b\s*bbch', re.I | re.S), 'de…a'),
)
# Linguagem que deixa uma ponta ABERTA — nunca vira faixa fechada.
ABERTA = re.compile(r'\b(a partir de|despu[ée]s de|antes de|hasta)\b', re.I)
# Linguagem que aponta UM estádio.
PONTUAL = re.compile(r'\b(en|durante|estadio|estad[ií]o|en el estadio)\s+bbch', re.I)


def normalizar_bbch(texto):
    """Texto literal da fonte -> faixa BBCH, com a regra que decidiu.

    Nunca deriva o fim a partir do início. Quando a fonte não sustenta uma
    faixa fechada, devolve APPROXIMATE com o texto inteiro — que é o que o
    schema aceita e o que o motor sabe ler como NOT_KNOWN.
    """
    t = texto or ''
    saida = {'TEXTO_LITERAL': t, 'BBCH_INICIO': None, 'BBCH_FIM': None}

    m = FAIXA_COM_TRACO.search(t)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a <= b:
            return dict(saida, RESOLUCAO='PHENOLOGY_STAGE', BBCH_INICIO=a, BBCH_FIM=b,
                        REGRA='FAIXA_COM_TRACO')
        # "BBCH 29-12" está fora de ordem: a fonte não sustenta faixa nenhuma.
        return dict(saida, RESOLUCAO='APPROXIMATE', REGRA='FAIXA_INVERTIDA_NAO_ACEITA')

    mencoes = [int(x.group(1)) for x in MENCAO_BBCH.finditer(t)]

    if len(mencoes) >= 2:
        for rx, nome in LIGA_FAIXA:
            if rx.search(t):
                a, b = mencoes[0], mencoes[-1]
                if a <= b:
                    return dict(saida, RESOLUCAO='PHENOLOGY_STAGE',
                                BBCH_INICIO=a, BBCH_FIM=b, REGRA='FAIXA_POR_LINGUAGEM:' + nome)
                return dict(saida, RESOLUCAO='APPROXIMATE',
                            REGRA='FAIXA_INVERTIDA_NAO_ACEITA')
        # Duas menções sem linguagem que as ligue: não dá para saber se são
        # uma faixa ou dois estádios soltos. Escolher seria inventar.
        return dict(saida, RESOLUCAO='APPROXIMATE', REGRA='MENCOES_SEM_LIGACAO')

    if len(mencoes) == 1:
        if ABERTA.search(t):
            # "a partir de BBCH 30" tem início e não tem fim. Fechar em 30
            # encolheria a janela para um estádio — o defeito do RT-6.
            return dict(saida, RESOLUCAO='APPROXIMATE', REGRA='PONTA_ABERTA')
        if PONTUAL.search(t):
            return dict(saida, RESOLUCAO='PHENOLOGY_STAGE',
                        BBCH_INICIO=mencoes[0], BBCH_FIM=mencoes[0],
                        REGRA='ESTADIO_UNICO')
        return dict(saida, RESOLUCAO='APPROXIMATE', REGRA='MENCAO_SEM_QUALIFICADOR')

    return dict(saida, RESOLUCAO='NOT_KNOWN', REGRA='SEM_MENCAO')


# ── RT-11 · de onde veio o alvo ───────────────────────────────────────
ORIGENS = ('PAIR_TABLE_ROW', 'PAGE_BODY_TEXT', 'NOT_KNOWN')


def classificar_origem_do_issue(relacao):
    """PAIR_TABLE_ROW quando a linha da tabela nomeia cultivo E agente juntos.

    Só essa origem pode virar alvo autorizado. Varredura de texto da página
    fica registrada como PAGE_BODY_TEXT e nunca vira `crop_issue`.
    """
    ancora = relacao.get('ANCHOR') or {}
    if ancora.get('ROW_TEXT') and ancora.get('ROW_INDEX') is not None \
            and relacao.get('CROP') and relacao.get('ISSUE'):
        return 'PAIR_TABLE_ROW'
    if relacao.get('ISSUE'):
        return 'PAGE_BODY_TEXT'
    return 'NOT_KNOWN'


def pode_virar_alvo_autorizado(origem):
    """A regra em uma linha: menu de site não vira alvo por conter a palavra."""
    return origem == 'PAIR_TABLE_ROW'


def termos_ubiquos(relacoes, total_de_produtos):
    """Termos presentes em TODOS os produtos da captura.

    Não é filtro: é medida. Um termo que aparece para todo produto não
    discrimina produto nenhum, e saber disso é o que separa evidência de
    ruído. A decisão de admissão continua sendo por ORIGEM, não por
    frequência — limiar de frequência seria um número que ninguém acordou.
    """
    por_termo = {}
    for r in relacoes:
        por_termo.setdefault(r['ISSUE'], set()).add(r['PRODUCT_ID'])
    return {t: len(p) for t, p in por_termo.items() if len(p) == total_de_produtos}


# ── autoteste, com os textos LITERAIS da fonte ────────────────────────
DA_FONTE = [
    ('En cebada de invierno se podrá realizar una aplicación en post-emergencia '
     'temprada del cultivo, o bien, realizar dicha aplicación en pre-emergencia del '
     'cultivo, desde BBCH 00 (semilla seca) hasta BBCH 07 (coleòptilo, emergido de '
     'la semilla).', 'PHENOLOGY_STAGE', 0, 7),
    ('Aplicar únicamente en variedades Full Page. Pueden realizarse 2 aplicaciones a '
     '0,4375 l/ha, espaciadas 20 días. Aplicar sin agua e inundar 3-4 días más tarde. '
     'Aplicar durante BBCH 12-29.', 'PHENOLOGY_STAGE', 12, 29),
    ('Centeno | Malas Hierbas | 2 l/ha |', 'NOT_KNOWN', None, None),
]
# Sem exemplo na fonte capturada. A regra existe porque uma janela de um
# estádio só é legítima (BBCH 65-65), e precisa continuar possível.
SEM_EXEMPLO_NA_FONTE = [
    ('Aplicar en BBCH 65', 'PHENOLOGY_STAGE', 65, 65),
    ('Aplicar a partir de BBCH 30', 'APPROXIMATE', None, None),
    ('Aplicar hasta BBCH 39', 'APPROXIMATE', None, None),
    ('BBCH 29-12', 'APPROXIMATE', None, None),
    ('Tratar em BBCH 13 e novamente BBCH 39', 'APPROXIMATE', None, None),
]


def autoteste():
    falhas = []
    for texto, res, ini, fim in DA_FONTE + SEM_EXEMPLO_NA_FONTE:
        r = normalizar_bbch(texto)
        if (r['RESOLUCAO'], r['BBCH_INICIO'], r['BBCH_FIM']) != (res, ini, fim):
            falhas.append((texto[:50], res, ini, fim, r))
    for t, r, i, f in DA_FONTE:
        print('  %-14s %-4s %-4s  %s' % (normalizar_bbch(t)['RESOLUCAO'],
                                         normalizar_bbch(t)['BBCH_INICIO'],
                                         normalizar_bbch(t)['BBCH_FIM'], t[:56]))
    if falhas:
        for f in falhas:
            print('FALHA:', f)
        return 1
    print('BBCH_RULES=PASS (%d casos)' % len(DA_FONTE + SEM_EXEMPLO_NA_FONTE))
    return 0


if __name__ == '__main__':
    sys.exit(autoteste() if '--autoteste' in sys.argv else 0)
