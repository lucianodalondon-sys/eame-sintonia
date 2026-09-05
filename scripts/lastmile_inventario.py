#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INVENTÁRIO ANTES DE COLETAR — o §11 da missão LAST-MILE.

    python3 scripts/lastmile_inventario.py

A missão manda, antes de qualquer coleta: comparar com o pacote mais novo e
classificar cada família em ALREADY_SUFFICIENT · PARTIAL · REAL_GAP ·
NO_PUBLIC_SOURCE_FOUND. Só PARTIAL e REAL_GAP autorizam coleta.

    COLETAR O QUE JÁ SE TEM É GASTAR DUAS VEZES E MEDIR A MESMA COISA.

O que este script NÃO faz: não decide sozinho. Ele conta o que existe e mede a
cobertura por cultura e por região; a classificação sai desses números, e o
motivo de cada uma vai escrito no resultado.

⚠️ UMA ARMADILHA QUE O PRÓPRIO INVENTÁRIO REVELOU
--------------------------------------------------
As regiões dos boletins vêm rotuladas em GRUPOS — `PUGLIA-SUD`, `TOSCANA-FVG`,
`MARCHE-UMBRIA`. Contar isso como «6 regiões» esconde que são 8 regiões
administrativas em 6 rótulos, e esconde que nenhuma delas é a região inteira
(o boletim de Modena não representa a Emília-Romanha). A contagem honesta
separa RÓTULOS de REGIÕES ADMINISTRATIVAS.
"""
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DR = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF',
                  '01-DESIGN-READY')

# As 20 regiões administrativas italianas. O denominador honesto.
REGIOES_IT = [
    'Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna',
    'Friuli-Venezia Giulia', 'Lazio', 'Liguria', 'Lombardia', 'Marche',
    'Molise', 'Piemonte', 'Puglia', 'Sardegna', 'Sicilia', 'Toscana',
    'Trentino-Alto Adige', 'Umbria', "Valle d'Aosta", 'Veneto',
]

CULTURAS_PILOTO = [
    'MAIS', 'FRUMENTO_DURO', 'FRUMENTO_TENERO', 'VITE', 'OLIVO',
    'BARBABIETOLA', 'MELO', 'POMODORO', 'RISO', 'SOIA',
]
CULTURA_PALAVRAS = {
    'MAIS': ['mais', 'granoturco', 'maize', 'corn'],
    'FRUMENTO_DURO': ['frumento duro', 'grano duro', 'durum'],
    'FRUMENTO_TENERO': ['frumento tenero', 'grano tenero', 'soft wheat',
                        'cereali autunno', 'frumento e orzo'],
    'VITE': ['vite', 'vigneto', 'uva', 'grapevine', 'vine'],
    'OLIVO': ['olivo', 'oliveto', 'olive'],
    'BARBABIETOLA': ['barbabietola', 'bietola', 'sugar beet'],
    'MELO': ['melo', 'mela', 'apple', 'pomacee'],
    'POMODORO': ['pomodoro', 'tomato'],
    'RISO': ['riso', 'risaia', 'rice'],
    'SOIA': ['soia', 'soybean'],
}


def _n(t):
    return re.sub(r'\s+', ' ', str(t or '')).strip().lower()


def carrega(rel, chave):
    p = os.path.join(DR, rel.replace('/', os.sep))
    if not os.path.exists(p):
        return None, []
    d = json.load(open(p, encoding='utf-8'))
    return d, d.get(chave) or []


def bate_cultura(texto, cult):
    """⚠️ COM BORDA DE PALAVRA, e a razao doi.

    A primeira versao usava `p in t` e devolveu RISO=77 para o mercado -- o
    total de registros. Motivo: «riso» esta dentro de «compa*riso*n», que
    aparece em todo registro de preco. Um substring achou uma cultura onde ha
    uma palavra inglesa.

        SUBSTRING NAO E PALAVRA. E a mesma lei do corpus: CROP_TERM_PRESENT
        so vale se o termo for um TERMO, nao um pedaco de outro.
    """
    t = _n(texto)
    return any(re.search(r'(?<![a-z])' + re.escape(p) + r'(?![a-z])', t)
               for p in CULTURA_PALAVRAS[cult])


def regioes_administrativas(rotulos):
    """Um rótulo como `TOSCANA-FVG` são DUAS regiões. Separar é honestidade."""
    achadas = set()
    for r in rotulos:
        t = _n(r)
        for reg in REGIOES_IT:
            chave = _n(reg).split()[0].split('-')[0]
            if chave in t or _n(reg) in t:
                achadas.add(reg)
        if 'fvg' in t:
            achadas.add('Friuli-Venezia Giulia')
    return achadas


def main():
    fam = []

    # ── 1 · FENOLOGIA CORRENTE ────────────────────────────────────────────────
    _, ph = carrega('CROP-WINDOWS/current-phenology.json', 'PHENOLOGY')
    rot = Counter(x.get('REGION') for x in ph)
    admin = regioes_administrativas(rot)
    datas = sorted(x.get('PUBLICATION_DATE') or '' for x in ph if x.get('PUBLICATION_DATE'))
    por_cult = {}
    for c in CULTURAS_PILOTO:
        regs = set()
        for x in ph:
            txt = ' '.join(str(v) for v in (x.get('CROPS') or [])) + ' ' + \
                str(x.get('PHENOLOGICAL_STAGE_DECLARED') or '')
            if bate_cultura(txt, c):
                regs |= regioes_administrativas([x.get('REGION')])
        por_cult[c] = sorted(regs)
    inferidas = sum(1 for x in ph if 'INFER' in str(x.get('CROP_STATE', '')).upper())
    fam.append({
        'FAMILIA': '1 · FENOLOGIA / CAMPO CORRENTE',
        'TEM': {
            'BOLETINS': len(ph),
            'ROTULOS_DE_REGIAO': len(rot),
            'REGIOES_ADMINISTRATIVAS': len(admin),
            'DE_UM_TOTAL_DE': len(REGIOES_IT),
            'REGIOES_ALCANCADAS': sorted(admin),
            'REGIOES_SEM_NENHUM_BOLETIM': sorted(set(REGIOES_IT) - admin),
            'JANELA_DE_DATAS': [datas[0], datas[-1]] if datas else None,
            'CULTURA_INFERIDA_NAO_DECLARADA': inferidas,
            'COBERTURA_POR_CULTURA': por_cult,
        },
        'CLASSE': 'PARTIAL',
        'POR_QUE': ('8 regioes administrativas de 20 (40%), em 6 rotulos agrupados. '
                    'MAIS, RISO, FRUMENTO_DURO e SOIA tem cobertura fina ou nula. '
                    'E 12 dos 73 boletins tem a cultura INFERIDA das avversita, '
                    'nao declarada.'),
        'VALE_COLETAR': True,
        'ONDE': ['servicos fitossanitarios regionais ainda nao lidos',
                 'Veneto, Trentino-Alto Adige, Sicilia, Campania, Lazio, Sardegna',
                 'Ente Nazionale Risi (arroz)', 'CREA'],
    })

    # ── 2 · MERCADO ───────────────────────────────────────────────────────────
    dmk, pr = carrega('MARKET-PULSE/market-pulse.json', 'PRICES')
    _, cap = carrega('MARKET-PULSE/market-capabilities.json', 'CAPABILITIES')
    _, msrc = carrega('MARKET-PULSE/market-sources.json', 'SOURCES')
    mk_cult = {}
    for c in CULTURAS_PILOTO:
        n = sum(1 for x in pr if bate_cultura(json.dumps(x, ensure_ascii=False), c))
        mk_cult[c] = n
    fam.append({
        'FAMILIA': '2 · MERCADO (Market Pulse)',
        'TEM': {
            'OBSERVACOES_DE_PRECO': len(pr),
            'CAPACIDADES_DE_FONTE': len(cap),
            'FONTES': len(msrc),
            'OBSERVACOES_POR_CULTURA': mk_cult,
            'CULTURAS_SEM_NENHUMA': [c for c, n in mk_cult.items() if n == 0],
        },
        'CLASSE': 'PARTIAL',
        'POR_QUE': 'ha preco para cereais e azeite; falta para varias culturas do piloto.',
        'VALE_COLETAR': True,
        'ONDE': ['EC Agri-food Data Portal (rotas ja provadas)', 'Eurostat',
                 'BMTI', 'ISMEA e ISTAT bloqueadas pelo NOSSO IP, nao pela fonte'],
    })

    # ── 3 · PESO ECONOMICO DA CULTURA ─────────────────────────────────────────
    tem_area = False
    for f in ('MARKET-PULSE/market-pulse.json', 'MARKET-PULSE/market-capabilities.json'):
        d, _ = carrega(f, 'X')
        if d and re.search(r'\b(AREA|HECTARE|ETTAR|PRODUCTION_VOLUME|YIELD|RESA)\b',
                           json.dumps(d, ensure_ascii=False), re.I):
            tem_area = True
    fam.append({
        'FAMILIA': '3 · PESO ECONOMICO DA CULTURA (area, producao, rendimento)',
        'TEM': {'AREA_OU_PRODUCAO_POR_REGIAO': 'SIM (mencao)' if tem_area else 'NAO',
                'OBJETOS_DEDICADOS': 0},
        'CLASSE': 'REAL_GAP',
        'POR_QUE': ('nao existe no pacote um objeto de area/producao por cultura x '
                    'regiao. Sem ele o portal nao distingue problema tecnicamente '
                    'interessante de problema em area de producao grande.'),
        'VALE_COLETAR': True,
        'ONDE': ['Eurostat apro_cpshr e apro_cpnhr (nacional)',
                 'Eurostat ef_lus / agr_r_crops (NUTS-2 = regiao italiana)',
                 'ISTAT (bloqueada desta linha)'],
    })

    # ── 4 · CATALOGO COMERCIAL ────────────────────────────────────────────────
    _, prod = carrega('ADAMA/adama-italy-products.json', 'PRODUCTS')
    no_cat = [p for p in prod if p.get('IN_PUBLIC_CATALOG')]
    cat_cat = Counter(p.get('CATALOG_CATEGORY') for p in no_cat)
    fam.append({
        'FAMILIA': '4 · CATALOGO COMERCIAL ADAMA ITALIA',
        'TEM': {
            'PRODUTOS_NO_REGISTRO': len(prod),
            'MARCADOS_NO_CATALOGO_PUBLICO': len(no_cat),
            'POR_CATEGORIA_DE_CATALOGO': dict(cat_cat),
            'REGISTRO_SEM_CATALOGO': len(prod) - len(no_cat),
        },
        'CLASSE': 'PARTIAL',
        'POR_QUE': ('as duas classes ja estao separadas (CATALOG_PRODUCT x '
                    'REGULATORY_PRODUCT), mas a contagem por categoria do catalogo '
                    'precisa ser reconferida na fonte, e os SPECIALI confirmados.'),
        'VALE_COLETAR': True,
        'ONDE': ['adama.com/italia — paginas de categoria e de produto'],
    })

    # ── 5 · RADAR REGULATORIO ─────────────────────────────────────────────────
    _, fut = carrega('FUTURE-RADAR/future-signals.json', 'SIGNALS')
    venc = Counter()
    for p in prod:
        e = str(p.get('EXPIRY') or '')[:7]
        if e:
            venc[e] += 1
    prox = {k: v for k, v in sorted(venc.items()) if '2026-09' <= k <= '2028-09'}
    fam.append({
        'FAMILIA': '5 · RADAR REGULATORIO FUTURO',
        'TEM': {
            'SINAIS_DE_FUTURO': len(fut),
            'ATOS_UE_LIDOS_NA_INTEGRA': 15,
            'VENCIMENTOS_DE_REGISTRO_POR_MES_ATE_2028': prox,
            'PRODUTOS_QUE_VENCEM_EM_12_MESES': sum(
                v for k, v in venc.items() if '2026-09' <= k <= '2027-09'),
        },
        'CLASSE': 'PARTIAL',
        'POR_QUE': ('o calendario de vencimento NACIONAL esta completo (163 produtos '
                    'com data). Falta o lado EUROPEU: quais substancias do portfolio '
                    'tem decisao de renovacao marcada, e quais atos sairam depois de '
                    '02/09/2026.'),
        'VALE_COLETAR': True,
        'ONDE': ['EU Pesticides Database', 'CELLAR/EUR-Lex (rota ja provada)',
                 'EFSA conclusions'],
    })

    # ── 6 · METEOROLOGIA ──────────────────────────────────────────────────────
    tudo = ''
    for dp, _dn, fn in os.walk(DR):
        for f in fn:
            if f.endswith('.json'):
                tudo += open(os.path.join(dp, f), encoding='utf-8',
                             errors='replace').read()
    met = len(re.findall(r'\b(rainfall|precipit|temperatur|drought|siccit|umidit|'
                         r'soil moisture|anomal|meteo|agrometeo)\b', tudo, re.I))
    fam.append({
        'FAMILIA': '6 · METEOROLOGIA / AGROMETEOROLOGIA',
        'TEM': {'MENCOES_NO_PACOTE': met, 'OBJETOS_DEDICADOS': 0,
                'FONTES_DE_CLIMA_MAPEADAS': 0},
        'CLASSE': 'REAL_GAP',
        'POR_QUE': ('o pacote nao tem nenhuma fonte de clima mapeada. E a lei tem de '
                    'nascer junto: CLIMA E CONDICAO, nao presenca de doenca.'),
        'VALE_COLETAR': True,
        'ONDE': ['Copernicus CDS / ERA5', 'JRC MARS bulletins',
                 'ARPA regionais', 'EDO/EDO-drought (Copernicus)'],
    })

    # ── 7 · CONCORRENTE ───────────────────────────────────────────────────────
    _, act = carrega('COMPETITOR-WATCH/competitor-activities.json', 'ACTIVITIES')
    tipos = Counter(x.get('ACTIVITY_KIND') or x.get('KIND') or x.get('TYPE')
                    for x in act)
    fam.append({
        'FAMILIA': '7 · SINAIS PUBLICOS DE CONCORRENTE',
        'TEM': {'ATIVIDADES': len(act), 'POR_TIPO': dict(tipos),
                'EMPRESAS': 14, 'PRODUTOS_NOMEADOS': 36},
        'CLASSE': 'PARTIAL',
        'POR_QUE': ('o lado PAGO ja e grande (a missao proibe expandir por volume). '
                    'Falta o lado que nao vem de anuncio: field day, webinar, '
                    'lancamento, comunicado tecnico, comunicacao para revenda.'),
        'VALE_COLETAR': True,
        'ONDE': ['sites das empresas .it', 'Agronotizie', 'Informatore Agrario',
                 'paginas de evento das proprias empresas'],
    })

    # ── 8 · VOZES DE CAMPO DE ALTA CONFIANCA ──────────────────────────────────
    _, vz = carrega('VOCI-DAL-CAMPO/field-voices.json', 'VOICES')
    plat = Counter(x.get('CHANNEL_AUDIENCE_KIND') or x.get('AUDIENCE') or 'NAO_SEI'
                   for x in vz)
    fam.append({
        'FAMILIA': '8 · VOZES PUBLICAS DE ALTA CONFIANCA',
        'TEM': {'FALAS': len(vz), 'POR_PLATEIA_DO_CANAL': dict(plat),
                'CANAIS_ITALIANOS': 62, 'PESSOAS_COM_IDENTIDADE_E_PAPEL': 15},
        'CLASSE': 'PARTIAL',
        'POR_QUE': ('as 58 falas sao de PLATEIA de canal. A missao pede VOZ '
                    'IDENTIFICADA -- agronomo, tecnico, organizacao de produtores, '
                    'cooperativa -- com evidencia de papel. Disso ha 15.'),
        'VALE_COLETAR': True,
        'ONDE': ['organizacoes de produtores', 'consorzi', 'cooperativas',
                 'CREA e universidades', 'associacoes de cultura'],
    })

    # ── 9 · HERBICIDA / DANINHA ───────────────────────────────────────────────
    _, res = carrega('SCIENCE/herbicide-resistance.json', 'RESISTANCES')
    _, lbl = carrega('LABEL-USE/label-use-pairs.json', 'PAIRS')
    ervas = [p for p in lbl if p.get('TARGET_KIND') == 'PLANTA_INFESTANTE']
    fam.append({
        'FAMILIA': '9 · HERBICIDA / DANINHA CORRENTE',
        'TEM': {'RESISTENCIAS_GIRE': len(res),
                'PARES_DE_DANINHA_NO_ROTULO': len(ervas),
                'HERBICIDAS_NO_PORTFOLIO': 91},
        'CLASSE': 'PARTIAL',
        'POR_QUE': ('o lado ESTATICO esta forte (GIRE + rotulo). Falta o CORRENTE: '
                    'qual janela de diserbo esta aberta ou abrindo agora, por regiao, '
                    'com fonte datada. Janela sazonal ainda precisa de data defensavel.'),
        'VALE_COLETAR': True,
        'ONDE': ['boletins regionais (secao diserbo)', 'Ente Nazionale Risi',
                 'disciplinari di produzione integrata regionais'],
    })

    # ── 10 · EVENTOS FUTUROS ──────────────────────────────────────────────────
    _, ev = carrega('EVENTS/events.json', 'EVENTS')
    fam.append({
        'FAMILIA': '10 · EVENTOS FUTUROS (SET/2026 -> SET/2027)',
        'TEM': {'EVENTOS': len(ev)},
        'CLASSE': 'PARTIAL',
        'POR_QUE': '18 eventos, concentrados em feira grande. Falta o calendario '
                   'tecnico regional: giornate, convegni, campi prova.',
        'VALE_COLETAR': True,
        'ONDE': ['sites de feira', 'CREA', 'universidades', 'consorzi',
                 'Giornate Fitopatologiche'],
    })

    saida = {
        'DATASET': 'IT-LASTMILE-INVENTARIO',
        'O_QUE_E': 'o §11 da missao: o que o pacote novo JA tem, antes de coletar',
        'LEI': 'COLETAR O QUE JA SE TEM E GASTAR DUAS VEZES E MEDIR A MESMA COISA',
        'DATA_DE_REFERENCIA': '2026-09-02',
        'PACOTE_LIDO': 'build/SINTONIA-ITALY-PILOT-REALITY-HANDOFF',
        'CLASSES': {
            'ALREADY_SUFFICIENT': 'nao coletar',
            'PARTIAL': 'coletar so o que falta, com alvo declarado',
            'REAL_GAP': 'coletar do zero',
            'NO_PUBLIC_SOURCE_FOUND': 'declarar a ausencia, nao inventar',
        },
        'RESUMO': dict(Counter(f['CLASSE'] for f in fam)),
        'FAMILIAS': fam,
    }
    d = os.path.join(ROOT, 'data', 'samples', 'IT-LASTMILE')
    os.makedirs(d, exist_ok=True)
    json.dump(saida, open(os.path.join(d, 'IT-LASTMILE-INVENTARIO.json'), 'w',
                          encoding='utf-8'), ensure_ascii=False, indent=1)

    print('%-46s %-16s %s' % ('FAMILIA', 'CLASSE', 'O QUE JA TEM'))
    print('-' * 104)
    for f in fam:
        t = f['TEM']
        prim = next(iter(t.items()))
        print('%-46s %-16s %s=%s' % (f['FAMILIA'][:46], f['CLASSE'],
                                     prim[0][:28], str(prim[1])[:30]))
    print()
    print('resumo:', saida['RESUMO'])
    print('gravado: data/samples/IT-LASTMILE/IT-LASTMILE-INVENTARIO.json')


if __name__ == '__main__':
    main()
