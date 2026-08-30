#!/usr/bin/env python3
"""
ITÁLIA — escala agrícola medida, não lembrada.

A pergunta que este arquivo responde é "quais culturas realmente importam na Itália, e
onde" — e ela tem de ser respondida por medição. Conhecimento geral sobre agricultura
italiana não elege cultura aqui. A ordem sai do dado.

Fonte: `EU-T1-001` (Eurostat `apro_cpshr`), rota já provada para FR/ES/IT.

DUAS LIMITAÇÕES QUE VÊM DE MEDIÇÃO ANTERIOR E CONTINUAM VALENDO

1. **`AR_THS_HA` desce a NUTS 2; `YLD_HUMD_EU_T_HA` não.** O dataset se chama "by NUTS 2
   region", mas rendimento regional não existe para nenhum país. Só ÁREA é regional.
   Quem ler "produtividade por região do Eurostat" está lendo o que não está lá.

2. **NUTS 2 ≠ região administrativa italiana em dois casos.** `ITH1` (Bolzano/Bozen) e
   `ITH2` (Trento) são duas NUTS 2 para UMA região administrativa (Trentino-Alto Adige).
   Somar as duas para falar da região é correto; tratá-las como duas regiões italianas
   não é. O serviço fitossanitário, porém, é provincial nesse caso — então para efeito
   de FIELD as duas continuam separadas. Declarado, nunca silenciado.

A hierarquia de rubricas do Eurostat SOMA-SE A SI MESMA: `C0000` (cereais) contém
`C1500` (milho grão), e `C1500` contém `C1500A`. **Somar rubricas de níveis diferentes
produz número inflado.** Por isso este módulo separa AGREGADOS de FOLHAS e nunca os
mistura num mesmo ranking.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SOURCE_ID = 'EU-T1-001'
DATASET = 'apro_cpshr'
API = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/' + DATASET
AREA = 'AR_THS_HA'
PROD = 'HPRD_HUMD_EU_THS_T'

# NUTS 2 italianas. Duas delas (ITH1/ITH2) formam UMA região administrativa.
NUTS2_IT = {
    'ITC1': 'Piemonte', 'ITC2': "Valle d'Aosta", 'ITC3': 'Liguria', 'ITC4': 'Lombardia',
    'ITF1': 'Abruzzo', 'ITF2': 'Molise', 'ITF3': 'Campania', 'ITF4': 'Puglia',
    'ITF5': 'Basilicata', 'ITF6': 'Calabria', 'ITG1': 'Sicilia', 'ITG2': 'Sardegna',
    'ITH1': 'Provincia Autonoma di Bolzano/Bozen', 'ITH2': 'Provincia Autonoma di Trento',
    'ITH3': 'Veneto', 'ITH4': 'Friuli-Venezia Giulia', 'ITH5': 'Emilia-Romagna',
    'ITI1': 'Toscana', 'ITI2': 'Umbria', 'ITI3': 'Marche', 'ITI4': 'Lazio',
}
REGIAO_ADMIN = {'ITH1': 'Trentino-Alto Adige', 'ITH2': 'Trentino-Alto Adige'}

# Rubricas AGREGADAS conhecidas do apro_cpshr. Nunca entram no mesmo ranking das folhas.
AGREGADOS = {
    'C0000', 'C1000', 'C2000', 'C3000', 'G0000', 'I0000', 'P0000', 'R0000', 'V0000',
    'N0000', 'C0000X1000', 'G1000', 'G2000', 'G3000', 'I1000', 'P1000', 'R1000',
    'R2000', 'V0000_S0000', 'S0000', 'T0000', 'E0000', 'F0000', 'W1000', 'J0000',
}


# NÍVEL COMMODITY — seleção que NÃO se sobrepõe, e a não-sobreposição é PROVADA
# aritmeticamente por `provar_hierarquia()`, não assumida. Cada código aqui é folha
# ou é pai cujos filhos ficaram DE FORA desta lista, nunca as duas coisas.
#
# A prova, medida em 2024 (mil ha), com diferença ≤ 0,01:
#     C1100 (1697,8) = C1110 (520,3) + C1120 (1177,4)
#     C0000 (2837,5) = C1000 + C2000
#     C2000  (226,1) = C2100 + C2200
# Por isso `C1100` NÃO entra: entram os dois filhos. E `C2000` entra como um só,
# porque arroz Indica e Japonica são a mesma decisão agronômica de portfólio.
COMMODITY = [
    'C1110', 'C1120', 'C1300', 'C1400', 'C1500', 'C1600', 'C1700', 'C2000',
    'I1110', 'I1120', 'I1130', 'P1200', 'R1000', 'R2000',
    'O1000', 'W1000',
]

HIERARQUIA_PROVAS = [
    ('C1100', ['C1110', 'C1120']),
    ('C1110', ['C1111', 'C1112']),
    ('C1300', ['C1310', 'C1320']),
    ('C1400', ['C1410', 'C1420']),
    ('I1110-1130', ['I1110', 'I1120', 'I1130']),
    ('C0000', ['C1000', 'C2000']),
    ('C2000', ['C2100', 'C2200']),
]


def provar_hierarquia(valores, tolerancia=0.05):
    """Prova que pai = soma dos filhos. Sem esta prova, qualquer ranking pode estar
    somando o mesmo hectare duas vezes. A prova é aritmética e roda contra o dado."""
    saida = []
    for pai, filhos in HIERARQUIA_PROVAS:
        if pai not in valores:
            saida.append({'PARENT': pai, 'STATE': 'PARENT_ABSENT'})
            continue
        presentes = [c for c in filhos if c in valores]
        soma = sum(valores[c] for c in presentes)
        dif = valores[pai] - soma
        saida.append({
            'PARENT': pai, 'PARENT_VALUE': valores[pai], 'CHILDREN': presentes,
            'CHILDREN_SUM': round(soma, 2), 'DIFF': round(dif, 2),
            'STATE': 'PROVED' if abs(dif) <= tolerancia else 'NOT_ADDITIVE',
        })
    return saida


def consultar(geo, time, strucpro=AREA):
    q = [('format', 'JSON'), ('lang', 'EN'), ('time', str(time)), ('strucpro', strucpro)]
    for g in (geo if isinstance(geo, (list, tuple)) else [geo]):
        q.append(('geo', g))
    url = API + '?' + urllib.parse.urlencode(q)
    with urllib.request.urlopen(url, timeout=180) as r:
        return json.load(r)


def desdobrar(d):
    """JSON-stat → [(geo, crop_code, crop_label, valor)]. Índice achatado desdobrado."""
    dims = d['id']
    sizes = d['size']
    cats = {name: d['dimension'][name]['category'] for name in dims}
    ordem = {}
    for name in dims:
        idx = cats[name]['index']
        ordem[name] = {v: k for k, v in idx.items()} if isinstance(idx, dict) else \
            {i: k for i, k in enumerate(idx)}
    out = []
    for flat, val in d['value'].items():
        n = int(flat)
        coords = {}
        for i in range(len(dims) - 1, -1, -1):
            coords[dims[i]] = ordem[dims[i]][n % sizes[i]]
            n //= sizes[i]
        cc = coords['crops']
        out.append((coords['geo'], cc, cats['crops']['label'].get(cc, cc), val))
    return out


def nacional(time=2024):
    d = consultar('IT', time)
    linhas = desdobrar(d)
    folhas = [x for x in linhas if x[1] not in AGREGADOS]
    agreg = [x for x in linhas if x[1] in AGREGADOS]
    return {
        'UPDATED': d.get('updated'),
        'TIME': str(time),
        'LEAF_CROPS': sorted(folhas, key=lambda x: -x[3]),
        'AGGREGATES': sorted(agreg, key=lambda x: -x[3]),
    }


def regional(crop_codes, time=2024):
    """Área por NUTS 2 para as rubricas pedidas. Região ausente é NÃO SEI, nunca zero."""
    d = consultar(sorted(NUTS2_IT), time)
    linhas = [x for x in desdobrar(d) if x[1] in set(crop_codes)]
    por_crop = {}
    for geo, cc, lab, val in linhas:
        por_crop.setdefault(cc, {'LABEL': lab, 'REGIONS': []})
        por_crop[cc]['REGIONS'].append({
            'NUTS2': geo, 'REGION': NUTS2_IT.get(geo, geo),
            'ADMIN_REGION': REGIAO_ADMIN.get(geo, NUTS2_IT.get(geo, geo)),
            'AREA_THS_HA': val,
        })
    for cc in por_crop:
        rs = sorted(por_crop[cc]['REGIONS'], key=lambda r: -r['AREA_THS_HA'])
        por_crop[cc]['REGIONS'] = rs
        tot = sum(r['AREA_THS_HA'] for r in rs)
        por_crop[cc]['NUTS2_SUM_THS_HA'] = round(tot, 2)
        por_crop[cc]['REGIONS_REPORTING'] = len(rs)
        por_crop[cc]['REGIONS_MISSING'] = sorted(set(NUTS2_IT) - {r['NUTS2'] for r in rs})
    return por_crop


def main():
    ano = 2024
    for a in sys.argv[1:]:
        if a.startswith('--ano='):
            ano = int(a.split('=')[1])
    nac = nacional(ano)
    print('EUROSTAT %s · IT · %s · atualizado %s' % (DATASET, ano, nac['UPDATED']))
    print('\nTOP 20 CULTURAS (rubricas FOLHA, área mil ha) — a ordem é medida')
    for geo, cc, lab, val in nac['LEAF_CROPS'][:20]:
        print('  %8.1f  %-10s %s' % (val, cc, lab[:58]))
    print('\nAGREGADOS (não somar com as folhas)')
    for geo, cc, lab, val in nac['AGGREGATES'][:8]:
        print('  %8.1f  %-10s %s' % (val, cc, lab[:58]))


if __name__ == '__main__':
    main()
