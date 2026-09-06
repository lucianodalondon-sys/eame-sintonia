#!/usr/bin/env python3
"""
ITÁLIA — área regional pelo ISTAT, e a armadilha de código que quase apagou o vale do Pó.

Por que este arquivo existe: o Eurostat **não publica oliveira nem videira em NUTS 2**
(medido). As duas maiores culturas permanentes da Itália ficavam sem geografia, e sem
geografia não há caso regional. O ISTAT publica — e publica com um detalhe que engana.

A ARMADILHA, e ela é silenciosa:

    O ISTAT ainda codifica as regiões em **NUTS 2006**. O Eurostat usa **NUTS 2021**.

        ISTAT   ITD3 = Veneto        Eurostat  ITH3 = Veneto
        ISTAT   ITD5 = Emilia-Romagna          ITH5
        ISTAT   ITE1 = Toscana                 ITI1

    Quem cruzar as duas fontes pela chave literal não recebe erro: recebe um resultado
    **menor e plausível**. As regiões que somem são exatamente `ITD*` e `ITE*` — ou seja,
    todo o Nord-Est e todo o Centro. Veneto e Emilia-Romagna, as duas que mais importam
    para milho e para videira, evaporam em silêncio.

    Foi o que aconteceu na primeira tentativa: a soma NUTS 2 do milho deu 261,3 mil ha
    contra 495,4 nacionais, e "faltar metade" era o único sintoma.

A VALIDAÇÃO QUE PROVA A ROTA: o total nacional do ISTAT bate **exatamente** com o do
Eurostat para milho (495,4) e trigo duro (1177,4). Não é aproximação: é o mesmo número,
porque é o mesmo dado — o Eurostat republica o que o ISTAT apura. Por isso a divergência
regional era erro de chave, e não discordância entre fontes.

`ART` é área total em hectares. Este módulo publica em mil ha para casar com `EU-T1-001`.
"""
import collections
import csv
import io
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SOURCE_ID = 'IT-T1-001'
DATAFLOW = 'IT1,101_1015_DF_DCSP_COLTIVAZIONI_1,1.0'
BASE = 'https://esploradati.istat.it/SDMXWS/rest/data/'

# NUTS 2006 (como o ISTAT publica) → NUTS 2021 (como o Eurostat publica).
# As linhas que mudam são as que mais importam.
NUTS2006_PARA_2021 = {
    'ITD1': 'ITH1', 'ITD2': 'ITH2', 'ITD3': 'ITH3', 'ITD4': 'ITH4', 'ITD5': 'ITH5',
    'ITE1': 'ITI1', 'ITE2': 'ITI2', 'ITE3': 'ITI3', 'ITE4': 'ITI4',
}

REGIOES = {
    'ITC1': 'Piemonte', 'ITC2': "Valle d'Aosta", 'ITC3': 'Liguria', 'ITC4': 'Lombardia',
    'ITH1': 'Provincia Autonoma di Bolzano/Bozen', 'ITH2': 'Provincia Autonoma di Trento',
    'ITH3': 'Veneto', 'ITH4': 'Friuli-Venezia Giulia', 'ITH5': 'Emilia-Romagna',
    'ITI1': 'Toscana', 'ITI2': 'Umbria', 'ITI3': 'Marche', 'ITI4': 'Lazio',
    'ITF1': 'Abruzzo', 'ITF2': 'Molise', 'ITF3': 'Campania', 'ITF4': 'Puglia',
    'ITF5': 'Basilicata', 'ITF6': 'Calabria', 'ITG1': 'Sicilia', 'ITG2': 'Sardegna',
}

# Culturas, com o código Eurostat quando o próprio ISTAT o declara em
# `NOTE_TYPE_OF_CROP_EUCODE`. A videira NÃO traz código Eurostat: por isso é somada
# a partir das três rubricas que a compõem, e a soma é declarada.
CULTURAS = {
    'MAIZE': {'ISTAT': ['MAIZE'], 'EU': 'C1500', 'NOME': 'Milho grão'},
    'DURUM_WHEAT': {'ISTAT': ['WHEATD'], 'EU': 'C1120', 'NOME': 'Trigo duro'},
    'COMMON_WHEAT': {'ISTAT': ['COMMEAT'], 'EU': 'C1110', 'NOME': 'Trigo mole'},
    'OLIVE': {'ISTAT': ['OLIVTAB_OIL'], 'EU': 'O1000', 'NOME': 'Oliveira'},
    'VINE': {'ISTAT': ['GRAPEDOPWINE', 'GRAPEIGPWINE', 'TABLEGRAPES'], 'EU': None,
             'NOME': 'Videira (uva DOP + IGP + de mesa)',
             'NOTA': ('o ISTAT não declara código Eurostat para videira. A soma das três '
                      'rubricas dá 588,8 mil ha contra 715,8 do Eurostat W1000 (2024): as '
                      'definições NÃO coincidem e os dois números NÃO devem ser trocados '
                      'um pelo outro. Para ordenar REGIÕES, o recorte ISTAT é coerente '
                      'consigo mesmo, e é para isso que ele é usado aqui.')},
}


def baixar(ano=2024):
    url = ('%s%s/A..ART..ALL?startPeriod=%d&endPeriod=%d&format=csv'
           % (BASE, DATAFLOW, ano, ano))
    with urllib.request.urlopen(url, timeout=300) as r:
        return r.read().decode('utf-8', 'replace')


def carregar(texto, ano=2024):
    return [r for r in csv.DictReader(io.StringIO(texto))
            if r['TIME_PERIOD'] == str(ano) and r['DATA_TYPE'] == 'ART']


def canonico(ref):
    """NUTS 2006 do ISTAT → NUTS 2021. Código já corrente passa direto."""
    return NUTS2006_PARA_2021.get(ref, ref)


def areas(rows, codes):
    """Devolve (por_regiao_mil_ha, nacional_mil_ha). Região ausente é NÃO SEI."""
    por, nac = collections.defaultdict(float), 0.0
    alvo = set(codes)
    for r in rows:
        if r['TYPE_OF_CROP'] not in alvo:
            continue
        try:
            v = float(r['OBS_VALUE'])
        except (TypeError, ValueError):
            continue
        ref = r['REF_AREA']
        if ref == 'IT':
            nac += v
        else:
            c = canonico(ref)
            if c in REGIOES:
                por[c] += v
    return ({k: round(v / 1000.0, 1) for k, v in por.items()}, round(nac / 1000.0, 1))


def montar(ano=2024, texto=None):
    rows = carregar(texto or baixar(ano), ano)
    out = {}
    for chave, cfg in CULTURAS.items():
        por, nac = areas(rows, cfg['ISTAT'])
        soma = round(sum(por.values()), 1)
        ordenado = sorted(por.items(), key=lambda kv: -kv[1])
        top3 = round(100.0 * sum(v for _, v in ordenado[:3]) / soma, 1) if soma else None
        out[chave] = {
            'CROP': cfg['NOME'], 'ISTAT_CODES': cfg['ISTAT'], 'EUROSTAT_CODE': cfg['EU'],
            'NATIONAL_THS_HA': nac,
            'REGIONS_REPORTING': len(por),
            'NUTS2_SUM_THS_HA': soma,
            # A cobertura é publicada porque a soma regional NÃO fecha com o nacional em
            # nenhuma cultura: parte da área fica em linhas que não são de região.
            'REGIONAL_COVERAGE_PCT': round(100.0 * soma / nac, 1) if nac else None,
            'BY_REGION': [{'NUTS2': k, 'REGION': REGIOES[k], 'AREA_THS_HA': v}
                          for k, v in ordenado],
            'TOP3_CONCENTRATION_PCT': top3,
        }
        if cfg.get('NOTA'):
            out[chave]['DEFINITION_NOTE'] = cfg['NOTA']
    return out


if __name__ == '__main__':
    import sys
    ano = 2024
    for a in sys.argv[1:]:
        if a.startswith('--ano='):
            ano = int(a.split('=')[1])
    d = montar(ano)
    for k, v in d.items():
        print('%-14s nac=%8.1f  regioes=%2d  soma=%8.1f (%s%%)  top3=%s%%'
              % (k, v['NATIONAL_THS_HA'], v['REGIONS_REPORTING'], v['NUTS2_SUM_THS_HA'],
                 v['REGIONAL_COVERAGE_PCT'], v['TOP3_CONCENTRATION_PCT']))
        for r in v['BY_REGION'][:5]:
            print('      %7.1f  %s' % (r['AREA_THS_HA'], r['REGION']))
