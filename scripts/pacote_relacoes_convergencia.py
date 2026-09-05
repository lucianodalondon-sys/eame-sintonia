#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIGAÇÕES A PARTIR DA CONVERGÊNCIA — o eixo que faltava para montar tela.

    (chamado por `pacote_montar.py`, depois que todas as camadas existem)

O pacote tinha 4.116 IDs e **6 ligações**, quase todas de listas vazias. Um Design
que abre `convergence.json` vê `VITE × SCAFOIDEO` e não tem como saber que existem
6 produtos, 12 vozes, 2 boletins e 135 obras falando do mesmo assunto — cada um
num arquivo diferente, sem ponte entre eles.

Esta camada constrói a ponte. Para cada convergência, procura em TODAS as outras
camadas o que fala da mesma cultura e do mesmo alvo.

⚠️ E É AQUI QUE SE INVENTA RELAÇÃO SEM QUERER
----------------------------------------------
Casar por nome de cultura é fácil e é onde nasce a mentira mais confortável:

    CROP_TERM_PRESENT ≠ ABOUT_THAT_CROP

Um anúncio da BASF que escreve «mais» no texto não é um anúncio SOBRE milho — pode
citar milho na lista de culturas de um produto de trigo. Um boletim que menciona
`vite` numa nota de rodapé não é um boletim de videira.

Por isso **toda ligação carrega COMO foi feita**, e o Design vê o método antes de
usar o dado:

    DECLARADO_NA_FONTE   a fonte declara aquela cultura num campo próprio
    TERMO_PRESENTE       o termo aparece no texto — e só isso
    ALVO_TAMBEM_BATE     além da cultura, o alvo também casa (a mais forte)

Uma ligação `TERMO_PRESENTE` sozinha **não sustenta** uma frase de tela sobre a
cultura. Ela sustenta «este item menciona esta cultura», que é outra coisa.

A ORDEM DE FORÇA, E POR QUE ELA NÃO É DECORATIVA
-------------------------------------------------
Um par cultura × alvo que bate nos DOIS eixos é raro e vale muito; um que bate só
na cultura é abundante e vale pouco. Misturar os dois numa contagem só produziria
um número grande e vazio — o mesmo erro que a plateia do canal já tinha ensinado.
"""
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DR = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF',
                  '01-DESIGN-READY')


def _n(t):
    return ''.join(c for c in unicodedata.normalize('NFD', str(t or ''))
                   if unicodedata.category(c) != 'Mn').lower()


# ── O DICIONÁRIO QUE LIGA AS CHAVES ÀS PALAVRAS DAS OUTRAS CAMADAS ─────────────
# As camadas foram escritas em momentos diferentes e cada uma usa o vocabulário da
# sua fonte. Este mapa é NOSSO, e por isso vai declarado no resultado.
CULTURA_PALAVRAS = {
    # ⚠️ as camadas falam TRES linguas: a ciencia usa chave em ingles (VINE,
    # DURUM_WHEAT), a oportunidade usa portugues (Videira), o rotulo usa italiano.
    # Faltando o ingles, 45 registros cientificos de videira ficavam invisiveis.
    'VITE': ['vite', 'viti', 'vigneto', 'uva', 'grape', 'vine', 'videira', 'vid'],
    'MELO': ['melo', 'meli', 'mela', 'apple', 'pomacee', 'macieira'],
    'MAIS_DOLCE': ['mais dolce', 'sweet corn'],
    'PERO': ['pero', 'peri', 'pera', 'pear'],
    'PESCO': ['pesco', 'pesca', 'peach', 'nettarin'],
    'OLIVO': ['olivo', 'olive', 'oliveto', 'oliva', 'oliveira'],
    'POMODORO': ['pomodoro', 'tomato', 'tomate'],
    'FRUMENTO': ['frumento', 'grano tenero', 'grano duro', 'wheat', 'durum',
                 'trigo', 'cereal', 'cereali'],
    'GRANO_GEN': ['grano', 'wheat', 'durum', 'cereal', 'cereali'],
    'MAIS': ['mais', 'granoturco', 'maize', 'corn', 'milho'],
    'ORZO': ['orzo', 'barley', 'cevada'],
    'RISO': ['riso', 'risaia', 'rice', 'arroz'],
    'SOIA': ['soia', 'soybean', 'soja'],
    'BARBABIETOLA': ['barbabietola', 'bietola', 'sugar beet', 'beet'],
    'PATATA': ['patata', 'potato', 'batata'],
    'GIRASOLE': ['girasole', 'sunflower'],
    'COLZA': ['colza', 'rapeseed'],
    'OLEAGINOSE': ['oleaginose', 'oilseed'],
    'ORTAGGI': ['ortagg', 'orticol', 'vegetable'],
    'ORTICOLE': ['ortagg', 'orticol', 'vegetable'],
    'AGRUMI': ['agrumi', 'citrus', 'arancio', 'limone'],
    'ACTINIDIA': ['actinidia', 'kiwi'],
    'FRAGOLA': ['fragola', 'strawberry'],
}
ALVO_PALAVRAS = {
    'SCAFOIDEO': ['scaphoideus', 'scafoideo', 'flavescenza', 'flavescencia'],
    'FLAVESCENZA': ['flavescenza', 'flavescencia', 'scaphoideus', 'giallumi'],
    'PERONOSPORA': ['peronospora', 'plasmopara', 'mildiu', 'downy mildew'],
    'OIDIO': ['oidio', 'erysiphe', 'powdery mildew', 'mal bianco'],
    'BOTRITE': ['botrite', 'botrytis', 'muffa grigia'],
    'TICCHIOLATURA': ['ticchiolatura', 'venturia', 'scab'],
    'SEPTORIOSI': ['septorio', 'zymoseptoria', 'septoria'],
    'FUSARIOSI': ['fusario', 'fusarium', 'don', 'micotossin', 'mycotoxin'],
    'RUGGINE': ['ruggine', 'puccinia', 'rust'],
    'CARPOCAPSA': ['carpocapsa', 'cydia pomonella', 'codling'],
    'AFIDI': ['afid', 'aphis', 'myzus', 'aphid', 'pulgon'],
    'MOSCA_OLIVO': ['bactrocera', 'mosca dell', 'olive fly'],
    'PIRALIDE': ['piralide', 'ostrinia'],
    'DIABROTICA': ['diabrotica'],
    'CIMICE': ['cimice', 'halyomorpha'],
    'CICALINA_GEN': ['cicalin', 'empoasca', 'scaphoideus'],
    'CICALINE': ['cicalin', 'empoasca', 'scaphoideus'],
    'GIAVONE': ['echinochloa', 'giavone'],
    'LOIETTO': ['lolium', 'loietto', 'loglio'],
    'BRUSONE': ['brusone', 'pyricularia', 'magnaporthe'],
    'NOTTUA': ['nottu', 'agrotis', 'spodoptera'],
    'RAGNETTO': ['ragnetto', 'tetranychus'],
    'ACARO_GEN': ['acar', 'tetranychus', 'eriophy'],
    'CERCOSPORA': ['cercospor'],
}

# (arquivo, chave do array, campos de cultura, campos de alvo, rótulo da relação)
ONDE_PROCURAR = [
    ('VOCI-DAL-CAMPO/field-voices.json', 'VOICES',
     ['CROP'], ['TARGET', 'PROBLEM', 'TEXT'], 'RELATED_FIELD_VOICES'),
    ('CROP-WINDOWS/current-phenology.json', 'PHENOLOGY',
     ['CROPS'], ['PESTS_AND_DISEASES_CITED'], 'RELATED_PHENOLOGY'),
    ('CROP-WINDOWS/crop-windows.json', 'WINDOWS',
     ['CROP'], ['TARGET', 'PEST'], 'RELATED_CROP_WINDOWS'),
    ('SCIENCE/scientific-records.json', 'RECORDS',
     ['CROP'], ['TITLE', 'TARGET', 'THEME', 'VENUE'], 'RELATED_SCIENCE'),
    ('SCIENCE/research-themes.json', 'THEMES',
     ['CROP', 'THEME', 'TITLE'], ['THEME', 'TITLE', 'TARGET'], 'RELATED_RESEARCH_THEMES'),
    ('SCIENCE/herbicide-resistance.json', 'RESISTANCES',
     ['CROP_DECLARED'], ['SPECIES', 'SPECIES_IT'], 'RELATED_RESISTANCE'),
    ('COMPETITOR-WATCH/competitor-activities.json', 'ACTIVITIES',
     ['CROP_TERMS'], ['TEXT', 'AD_TEXT', 'TITLE'], 'RELATED_COMPETITOR_ACTIVITY'),
    ('NEWS/news.json', 'NEWS', ['CROP'], ['TITLE'], 'RELATED_NEWS'),
    ('MARKET-PULSE/market-pulse.json', 'PRICES', ['CROP', 'PRODUCT_CROP'], [],
     'RELATED_MARKET_PRICES'),
    ('EVENTS/events.json', 'EVENTS', ['CROP_RELEVANCE'], [], 'RELATED_EVENTS'),
    ('OPPORTUNITIES/opportunities.json', 'OPPORTUNITIES', ['CROP', 'TITLE'],
     ['TARGET', 'ISSUE', 'ISSUE_TYPE', 'TITLE'], 'RELATED_OPPORTUNITIES'),
    ('FUTURE-RADAR/future-signals.json', 'SIGNALS', ['CROP', 'TITLE'],
     ['TARGET', 'TITLE', 'SIGNAL', 'SUBSTANCE'], 'RELATED_FUTURE_SIGNALS'),
    ('PEOPLE/people.json', 'PEOPLE', ['CROP', 'FIELD', 'ROLE', 'TOPIC'],
     ['FIELD', 'TOPIC', 'ROLE'], 'RELATED_PEOPLE'),
    ('SCIENCE/researchers.json', 'RESEARCHERS', ['CROP', 'SCOPE', 'TOPIC'],
     ['SCOPE', 'TOPIC'], 'RELATED_RESEARCHERS'),
]
# Quanto item de uma mesma relação entra. Uma lista de 400 IDs não ajuda ninguém.
TETO = 25


def _texto_dos_campos(item, campos):
    partes = []
    for c in campos:
        v = item.get(c)
        if isinstance(v, list):
            partes.extend(str(x) for x in v)
        elif v:
            partes.append(str(v))
    return _n(' | '.join(partes))


def _bate(texto, palavras):
    return any(re.search(r'\b%s' % re.escape(p), texto) for p in palavras)


def _carrega(rel):
    p = os.path.join(DR, rel.replace('/', os.sep))
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding='utf-8'))


def construir():
    conv = _carrega('CONVERGENCE/convergence.json')
    lbl = _carrega('LABEL-USE/label-use-pairs.json')
    prod = _carrega('ADAMA/adama-italy-products.json')
    if not conv:
        return None

    # registro -> ID do produto no pacote
    reg2id = {}
    if prod:
        for p in prod['PRODUCTS']:
            if p.get('REGISTRATION_ID'):
                reg2id[p['REGISTRATION_ID']] = p['ID']

    fontes = []
    for rel, chave, cc, ca, rotulo in ONDE_PROCURAR:
        d = _carrega(rel)
        if d and isinstance(d.get(chave), list):
            fontes.append((rel, d[chave], cc, ca, rotulo))

    ligacoes, resumo = [], {'ALVO_TAMBEM_BATE': 0, 'DECLARADO_NA_FONTE': 0,
                            'TERMO_PRESENTE': 0}

    for c in conv['CONVERGENCE']:
        pc = CULTURA_PALAVRAS.get(c['CROP'], [_n(c['CROP'])])
        pa = ALVO_PALAVRAS.get(c['TARGET'], [_n(c['TARGET'])])
        no = {'FROM': c['ID'], 'FROM_PAIR': c['PAIR'],
              'CROP': c['CROP'], 'TARGET': c['TARGET'],
              'AUDIENCE_VERDICT': c.get('AUDIENCE_VERDICT')}

        # produtos e pares de rótulo — ligação exata, sem casamento por texto
        regs = set()
        pares_lbl = []
        if lbl:
            for p in lbl['PAIRS']:
                if p['CROP'] == c['CROP'] and p['TARGET'] == c['TARGET']:
                    regs.add(p['REGISTRATION_ID'])
                    if len(pares_lbl) < TETO:
                        pares_lbl.append(p['ID'])
        no['RELATED_PRODUCTS'] = sorted(
            {reg2id[r] for r in regs if r in reg2id})
        no['RELATED_LABEL_PAIRS'] = pares_lbl
        no['RELATED_PRODUCTS_HOW'] = ('CHAVE_EXATA: mesmo par cultura x alvo no '
                                      'rotulo. Nao ha casamento por texto aqui.')

        for rel, itens, cc, ca, rotulo in fontes:
            fortes, fracos = [], []
            for it in itens:
                if not it.get('ID'):
                    continue
                tc = _texto_dos_campos(it, cc)
                if not tc or not _bate(tc, pc):
                    continue
                ta = _texto_dos_campos(it, ca)
                if ta and _bate(ta, pa):
                    fortes.append(it['ID'])
                else:
                    fracos.append(it['ID'])
            if fortes or fracos:
                no[rotulo] = (fortes + fracos)[:TETO]
                no[rotulo + '_HOW'] = {
                    'ALVO_TAMBEM_BATE': len(fortes),
                    'SO_A_CULTURA_BATE': len(fracos),
                    'AVISO': ('os que batem so na cultura sustentam «este item menciona '
                              'esta cultura», nunca «este item e sobre esta cultura». '
                              'CROP_TERM_PRESENT nao e ABOUT_THAT_CROP.'),
                }
                resumo['ALVO_TAMBEM_BATE'] += len(fortes)
                resumo['TERMO_PRESENTE'] += len(fracos)

        ligacoes.append(no)

    return {
        'LAYER': 'CONVERGENCE_LINKS',
        'BUILT_AT': '2026-09-02',
        'O_QUE_E': 'para cada convergencia, o que existe nas outras camadas sobre a '
                   'mesma cultura e o mesmo alvo',
        'LAW': 'CROP_TERM_PRESENT nao e ABOUT_THAT_CROP. Toda ligacao carrega COMO foi '
               'feita, e uma ligacao que bate so na cultura NAO sustenta frase de tela '
               'sobre a cultura.',
        'ORDEM_DE_FORCA': [
            'CHAVE_EXATA (produto e par de rotulo): mesmo par cultura x alvo',
            'ALVO_TAMBEM_BATE: cultura e alvo casam no mesmo item',
            'SO_A_CULTURA_BATE: apenas o termo da cultura aparece',
        ],
        'DICIONARIO_E_NOSSO': {
            'O_QUE_E': 'as camadas nasceram em momentos diferentes e cada uma usa o '
                       'vocabulario da sua fonte. Este mapa liga as chaves, e e ato '
                       'nosso -- pode estar errado, e por isso vai escrito.',
            'CULTURA': CULTURA_PALAVRAS,
            'ALVO': ALVO_PALAVRAS,
        },
        'TETO_POR_RELACAO': TETO,
        'TETO_POR_QUE': 'uma lista de 400 IDs numa tela nao e informacao, e ruido. O '
                        'numero cheio esta em cada *_HOW.',
        'COUNT': len(ligacoes),
        'TOTAL_POR_FORCA': resumo,
        'LINKS': ligacoes,
    }


def main():
    d = construir()
    if not d:
        print('  (sem camada de convergencia — ligacoes nao geradas)')
        return
    destino = os.path.join(DR, 'RELATIONSHIPS', 'convergence-links.json')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    json.dump(d, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('  RELATIONSHIPS/convergence-links.json          %d convergencias ligadas'
          % d['COUNT'])
    print('  ligacoes por forca:', d['TOTAL_POR_FORCA'])


if __name__ == '__main__':
    main()
