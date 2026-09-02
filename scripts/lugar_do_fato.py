#!/usr/bin/env python3
"""A LEI DO LUGAR DO FATO — do core, e independente de idioma.

A Itália escreveu `scripts/fato_local.py`: um LEITOR de texto italiano que
propõe candidatos a lugar do fato. O gazetteer dele é italiano, as âncoras
são italianas, os meses são italianos. Isso é do piloto e fica no piloto.

O que NÃO é do piloto são as leis que ele exerce. Elas valem em espanhol,
em francês e em qualquer idioma que venha depois, e por isso moram aqui:

    BASE != OPERATING != INFLUENCE != FACT
    PLACE_MENTION != FACT_LOCATION
    TERRITORIAL_LIST != FACT_LIST
    SOURCE_GEOGRAPHY != ADMIN_GEOGRAPHY
    OCCURRENCE != INCIDENCE
    PUBLISHED_AT != FACT_TIME
    ROW_PROVENANCE != VALUE_PROVENANCE
    NOT_IN_GAZETTEER != NOT_A_PLACE != REJECTED_BY_LAW
    SOURCE SAYS REGION != INVENT MUNICIPALITY

O risco que este arquivo existe para evitar é o de haver DUAS leis para a
mesma pergunta: uma no leitor italiano, outra no core, divergindo devagar
até que a mesma frase receba dois vereditos. Por isso o core não reimplementa
o leitor — ele declara o vocabulário, e `tests/test_lugar_do_fato.py`
compara este vocabulário com o da Itália E com o que o banco aceita. Três
lugares, uma lei; qualquer um que ande sozinho reprova.

    python3 scripts/lugar_do_fato.py     # imprime o contrato
"""
import json
import sys

# ── AS QUATRO ESPÉCIES DE LUGAR ───────────────────────────────────────
# Três são do SUJEITO (pessoa ou organização) e uma é do CONTEÚDO. É por
# isso que no banco são duas tabelas: `origem_lugar` e `conteudo_lugar`.
BASE, OPERATING, INFLUENCE, FACT = 'BASE', 'OPERATING', 'INFLUENCE', 'FACT'
ESPECIES = (BASE, OPERATING, INFLUENCE, FACT)
ESPECIES_DO_SUJEITO = (BASE, OPERATING, INFLUENCE)

# ── A ESCADA DE PRECISÃO ──────────────────────────────────────────────
# Ordenada. Mais específico só nasce de evidência mais específica: se a
# fonte prova região, não se inventa município; se prova município, não se
# reduz para país.
ESCADA_ADMINISTRATIVA = ('PAIS', 'REGIAO', 'PROVINCIA', 'MUNICIPIO',
                         'LOCALIDADE', 'COORDENADA')

# FORA da escada, de propósito. Uma zona que a fonte definiu não é "menos
# precisa que província": é outra coisa, e compará-las na mesma régua é
# exatamente o erro. Ordem 0 no banco, e sem sucessor aqui.
FORA_DA_ESCADA = ('ZONA_DEFINIDA_PELA_FONTE', 'ZONA_AGRONOMICA',
                  'OUTRA_GEOGRAFIA', 'NOT_KNOWN')
PRECISOES = ESCADA_ADMINISTRATIVA + FORA_DA_ESCADA

# Cada país nomeia os degraus como quiser — `provincia` na Itália e na
# Espanha, `département` na França. O DEGRAU é do contrato; o NOME é do país.
ESPECIE_DE_GEOGRAFIA = ('ADMIN', 'DEFINIDA_PELA_FONTE', 'ZONA_AGRONOMICA', 'OUTRA')

# ── AS ESPÉCIES DE EVIDÊNCIA ──────────────────────────────────────────
# Não se somam entre si. Cinco amostras de diagnóstico e um comunicado
# regional não fazem "seis ocorrências", e nenhum dos dois faz incidência.
TIPOS_DE_EVIDENCIA = ('FIELD_OBSERVATION', 'DIAGNOSTIC_SAMPLE',
                      'OFFICIAL_OCCURRENCE', 'CONFIRMED_FOCUS',
                      'REGIONAL_STATEMENT', 'INCIDENCE_MEASUREMENT', 'OTHER')

# Só esta sustenta uma afirmação de magnitude. As outras sustentam que
# HOUVE, e houve não é quanto.
SUSTENTAM_OCORRENCIA = ('FIELD_OBSERVATION', 'DIAGNOSTIC_SAMPLE',
                        'OFFICIAL_OCCURRENCE', 'CONFIRMED_FOCUS')
SUSTENTA_INCIDENCIA = ('INCIDENCE_MEASUREMENT',)

# ── COMO O LUGAR SE SOUBE — proveniência DO VALOR ─────────────────────
# DA_FONTE e DEDUZIDO existem para poderem ser DITOS, e são recusados como
# sustentação. LISTA_TERRITORIAL idem: a lista existe, e não é ocorrência.
ORIGENS_DO_LUGAR = ('ESCRITO', 'CITADO', 'DA_FONTE', 'DEDUZIDO',
                    'LISTA_TERRITORIAL', 'NAO_SEI')
ORIGENS_QUE_SUSTENTAM_FATO = ('ESCRITO', 'CITADO')

# ── OS PAPÉIS DE UM LUGAR DENTRO DE UM CONTEÚDO ───────────────────────
# Guardar os que NÃO são fato é o que permite PROVAR que não viraram
# ocorrência. Sem eles, a recusa não deixa rastro.
PAPEIS_NO_CONTEUDO = ('FACT', 'EVENT', 'OPERATING_MENCIONADO', 'AREA_COMERCIAL',
                      'LISTA_TERRITORIAL', 'MENCAO_APENAS', 'NAO_SEI')

# ── O QUE ACONTECEU COM O NOME QUE A FONTE ESCREVEU ───────────────────
# Três respostas diferentes que, no Brasil, saíam idênticas do outro lado.
ESTADOS_DO_LUGAR = ('RESOLVIDO', 'NAO_ESTA_NO_GAZETTEER', 'NAO_E_LUGAR',
                    'RECUSADO_POR_LEI')

# ── TEMPO DO FATO ─────────────────────────────────────────────────────
# `PUBLICACAO` não está aqui, e é a ausência mais importante do arquivo:
# não existe forma de declarar que o tempo do fato veio do carimbo da
# publicação, porque isso não é permitido.
ORIGENS_DO_TEMPO = ('ESCRITO_NO_TEXTO', 'AMARRADO_AO_ACONTECIMENTO',
                    'FONTE_OFICIAL', 'NAO_SEI')
# Reusa o vocabulário da 009. Criar um segundo seria um segundo dono.
RESOLUCAO_TEMPORAL = ('DATE_EXACT', 'WEEK', 'MONTH', 'PHENOLOGY_STAGE',
                      'SEASON', 'APPROXIMATE', 'NOT_KNOWN')

# Estados de recusa que o LEITOR devolve. Aqui para que o core e o leitor
# usem as mesmas palavras — e o teste compara.
PLACE_MENTION_ONLY = 'PLACE_MENTION_NOT_FACT'
TERRITORIAL_LIST = 'TERRITORIAL_LIST_NOT_FACT'
PUBLICATION_STAMP = 'PUBLICATION_STAMP_NOT_FACT_TIME'
SERIES_RANGE = 'SERIES_RANGE_NOT_FACT_TIME'


def sustenta_fato(origem_do_dado, papel):
    """A lei em uma linha: quem pode virar lugar do fato, e por quê não."""
    if papel != FACT:
        return False, 'papel %s não é o lugar do fato' % papel
    if origem_do_dado == 'LISTA_TERRITORIAL':
        return False, 'TERRITORIAL_LIST != FACT_LIST — lista nua não é ocorrência'
    if origem_do_dado in ('DA_FONTE',):
        return False, 'LOCAL_DA_FONTE != LOCAL_DO_FATO'
    if origem_do_dado in ('DEDUZIDO',):
        return False, 'geografia é lugar declarado, nunca inferido'
    if origem_do_dado not in ORIGENS_QUE_SUSTENTAM_FATO:
        return False, 'origem %s não sustenta lugar do fato' % origem_do_dado
    return True, 'sustentado por %s' % origem_do_dado


def mais_especifico_que(a, b):
    """`a` é mais específico que `b`?  None quando não são comparáveis.

    Devolver False para "l'Ovest vs PROVINCIA" seria dizer que a zona é
    menos específica, e ela não é: ela é incomparável. None é a resposta.
    """
    if a not in ESCADA_ADMINISTRATIVA or b not in ESCADA_ADMINISTRATIVA:
        return None
    return ESCADA_ADMINISTRATIVA.index(a) > ESCADA_ADMINISTRATIVA.index(b)


def ocorrencia_nao_e_incidencia(tipos):
    """Conta POR espécie. Nunca devolve um total, e nunca devolve score."""
    por_tipo = {}
    for t in tipos:
        t = t if t in TIPOS_DE_EVIDENCIA else 'OTHER'
        por_tipo[t] = por_tipo.get(t, 0) + 1
    return {
        'BY_TYPE_OF_EVIDENCE': por_tipo,
        'OBSERVED_OCCURRENCES': sum(por_tipo.get(t, 0) for t in SUSTENTAM_OCORRENCIA),
        'INCIDENCE': ('NOT_KNOWN' if not por_tipo.get('INCIDENCE_MEASUREMENT')
                      else 'MEDIDA_DECLARADA'),
        'PREVALENCE': 'NOT_KNOWN',
        'REGIONAL_PRESSURE': 'NOT_KNOWN',
        'WHY': ('POSITIVE_SAMPLE != REGIONAL_INCIDENCE. As espécies não se somam '
                'entre si, e "houve" não autoriza dizer "quanto".'),
    }


def contrato():
    return {
        'SOURCE_ID': 'LUGAR-DO-FATO-CONTRATO',
        'VERSION': 'V1',
        'O_QUE_ISTO_E': 'a lei do lugar do fato, independente de idioma.',
        'O_QUE_ISTO_NAO_E':
            'não é um leitor de texto. Ler texto é do piloto — o italiano está '
            'em scripts/fato_local.py, portado da branch da Itália.',
        'SOURCE_LOCATION': 'interno',
        'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'pt',
        'ESPECIES': list(ESPECIES),
        'ESPECIES_DO_SUJEITO': list(ESPECIES_DO_SUJEITO),
        'ESCADA_ADMINISTRATIVA': list(ESCADA_ADMINISTRATIVA),
        'FORA_DA_ESCADA': list(FORA_DA_ESCADA),
        'ESPECIE_DE_GEOGRAFIA': list(ESPECIE_DE_GEOGRAFIA),
        'TIPOS_DE_EVIDENCIA': list(TIPOS_DE_EVIDENCIA),
        'ORIGENS_DO_LUGAR': list(ORIGENS_DO_LUGAR),
        'ORIGENS_QUE_SUSTENTAM_FATO': list(ORIGENS_QUE_SUSTENTAM_FATO),
        'PAPEIS_NO_CONTEUDO': list(PAPEIS_NO_CONTEUDO),
        'ESTADOS_DO_LUGAR': list(ESTADOS_DO_LUGAR),
        'ORIGENS_DO_TEMPO': list(ORIGENS_DO_TEMPO),
        'PUBLICACAO_NAO_E_ORIGEM_DO_TEMPO_DO_FATO':
            'não há valor no vocabulário de origem do tempo que signifique "veio da '
            'data de publicação". A ausência é a trava.',
        'LEIS': [
            'BASE != OPERATING != INFLUENCE != FACT',
            'PLACE_MENTION != FACT_LOCATION',
            'TERRITORIAL_LIST != FACT_LIST',
            'SOURCE_GEOGRAPHY != ADMIN_GEOGRAPHY',
            'OCCURRENCE != INCIDENCE',
            'PUBLISHED_AT != FACT_TIME',
            'ROW_PROVENANCE != VALUE_PROVENANCE',
            'NOT_IN_GAZETTEER != NOT_A_PLACE != REJECTED_BY_LAW',
            'SOURCE SAYS REGION != INVENT MUNICIPALITY',
        ],
        'DONO_NO_BANCO': {
            'especies_do_sujeito': 'public.origem_lugar',
            'lugar_do_fato': 'public.conteudo_lugar',
            'escada': 'public.precisao_da_geografia / public.escada_de_precisao',
            'tempo_do_fato': 'public.conteudo.fact_tempo_*',
            'ocorrencia_por_especie': 'public.f_ocorrencia_nao_e_incidencia',
        },
        'LEITORES_POR_IDIOMA': {'it': 'scripts/fato_local.py (portado da Itália)'},
    }


if __name__ == '__main__':
    json.dump(contrato(), sys.stdout, ensure_ascii=False, indent=1)
    print()
