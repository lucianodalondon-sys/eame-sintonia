#!/usr/bin/env python3
"""
ITÁLIA — o trigo duro existe, o sinal existe, e eles não se encontram.

Três medições que estavam separadas e que, juntas, mudam o que se pode dizer sobre a
maior cultura da Itália (1.177,4 mil ha, mais que milho e videira somados).

1 · O SINAL DE CAMPO DE TRIGO DURO EXISTE — eu não tinha perguntado
--------------------------------------------------------------------
Eu publiquei `TRIGO DURO · sinal cobre 0,0 %`. Não era ausência de sinal: era ausência
de pergunta (ver `italia_vies_de_painel.py`). Perguntando, ele aparece na primeira
região aberta: o **Consorzio LaMMA / Regione Toscana** publica boletim fitossanitário
**por província**, e o de Grosseto e o de Pisa trazem **frumento com grano duro
separado do grano tenero**, com doença nomeada, fase fenológica, nível de risco e
janela de tratamento.

O boletim de Grosseto lido em 2026-04-23 diz, sobre o grano duro:

    "Dove la fase fenologica sta entrando in fioritura, considerate le piogge e le
     previsioni di piogge per i prossimi giorni, che comportano quindi un alto rischio
     fusariosi, se non già protette con un trattamento specifico, è opportuno
     effettuare un trattamento fitosanitario"

Isto é sinal de campo de primeira qualidade: **doença × fase × risco × janela**.

2 · O QUE A ADAMA TEM COM O NOME "GRANO DURO" NO RÓTULO
--------------------------------------------------------
Catorze produtos. **Treze são herbicidas** (dez de clodinafop, um de
chlorotoluron+diflufenican, dois de mesosulfuron+pinoxaden) e **um é tratamento de
semente** (SEEDRON, fludioxonil+tebuconazole, contra cárie, carvão e fusariose
*transmitida pela semente*).

**Nenhum fungicida foliar nomeia grano duro.**

3 · O DESENCONTRO
------------------
O sinal público de trigo duro é **foliar e de espiga, na floração, sob chuva**. O
portfólio nomeado para trigo duro é **de plantas daninhas e de semente**. As duas
camadas existem, são boas, e **não se cruzam na mesma célula** CULTURA × PROBLEMA ×
MOMENTO.

O QUE EU **NÃO** SEI, E É A PERGUNTA QUE DECIDE TUDO
-----------------------------------------------------
Os fungicidas foliares que atendem exatamente o conjunto de doenças do boletim —
MAXENTIS e KOJAMI (azoxystrobin+prothioconazole, FRAC 11+3, com *Fusarium* spp.,
*Zymoseptoria tritici*, *Puccinia* spp., *Blumeria graminis*) — nomeiam
`COMMON_WHEAT` e `WHEAT_GENERIC`, não `DURUM_WHEAT`.

**Se "frumento" no rótulo italiano cobre juridicamente o grano duro, não há lacuna
nenhuma: é artefato de redação de rótulo.** Se não cobre, a lacuna é real e é grande.

Eu **não sei** qual das duas. Não é extraível do texto do rótulo, que é tudo o que
tenho. Resolver isso exige a leitura jurídica do decreto de autorização, não mais
extração. Enquanto não for resolvido, este arquivo **não afirma lacuna** — afirma um
desencontro observado e uma pergunta aberta, e a pergunta vale mais que um palpite.

    CROP_TERM ≠ AUTHORIZED_CROP

é a lei local, irmã de `REGISTRATION ≠ COMMERCIAL AVAILABILITY`. O contrato de
`IT-T4-001-portfolio-rotulo.json` já dizia isso; aqui ele passa a ter consequência.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PORT = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001', 'IT-T4-001-portfolio-rotulo.json')
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-T3-LOTTA', 'IT-trigo-duro-sinal-x-portfolio.json')

HOJE = datetime.date(2026, 8, 30)

# Conjunto de doenças que o boletim de campo da Toscana nomeia para frumento.
DOENCAS_DO_BOLETIM = ['Septoria', 'Ruggini', 'Oidio', 'Fusariosi']

# Fungicidas foliares de cereal: o que decide é a substância, não o nome comercial.
FOLIAR_CEREAL = ('AZOXYSTROBIN', 'PROTHIOCONAZOLE', 'TEBUCONAZOLE')
SEMENTE = ('FLUDIOXONIL',)
# Classificar por ALVO EXTRAÍDO falha quando a extração veio vazia: TOPIK 80 EC, VIP 80 EC
# e CELIO 80 EC sao clodinafop — herbicidas inequívocos — e caíam em OUTRO só porque o
# parser nao tirou alvo daqueles PDFs. AUSÊNCIA DE EXTRAÇÃO NÃO É AUSÊNCIA DE CLASSE.
# A substância decide primeiro; o alvo botânico fica como reforço.
HERBICIDA_SUB = ('CLODINAFOP', 'MESOSULFURON', 'PINOXADEN', 'CHLOROTOLURON',
                 'DIFLUFENICAN')


def _data(s):
    try:
        return datetime.datetime.strptime(s, '%d/%m/%Y').date()
    except (ValueError, TypeError):
        return None


def classificar(p):
    """HERBICIDA / TRATAMENTO_SEMENTE / FUNGICIDA_FOLIAR / OUTRO, pela substância."""
    subs = (p.get('ACTIVE_SUBSTANCE') or '').upper()
    alvos = ' '.join(i.get('SCIENTIFIC_NAME', '') for i in (p.get('ISSUES_FROM_SOURCE') or []))
    if any(s in subs for s in HERBICIDA_SUB):
        return 'HERBICIDA'
    if any(s in subs for s in SEMENTE):
        return 'TRATAMENTO_SEMENTE'
    if any(s in subs for s in FOLIAR_CEREAL):
        return 'FUNGICIDA_FOLIAR'
    # Herbicida se os alvos são plantas, e a marca disso é o gênero botânico daninho.
    if any(g in alvos for g in ('Avena', 'Lolium', 'Phalaris', 'Alopecurus', 'Galium',
                                'Stellaria', 'Matricaria', 'Ridolfia', 'Anagallis')):
        return 'HERBICIDA'
    return 'OUTRO'


def boletim_toscana():
    """A evidência de campo. Página rolante: traz a edição corrente, não um arquivo."""
    return {
        'SOURCE_ID': 'IT-T3-LAMMA',
        'PUBLISHER': 'Consorzio LaMMA — Regione Toscana / CNR',
        'ROUTE': 'lamma.toscana.it/previ/ita/agrometeo/html/<Provincia>_ftsnt.html',
        'READ_ON': '2026-08-30',
        'BULLETIN_DATE_SHOWN': '2026-04-23',
        'PAGE_KIND': 'ROLLING_CURRENT_ISSUE',
        'PAGE_KIND_NOTE': (
            'a página mostra a edição corrente e não expõe arquivo de edições passadas. '
            'Por isso NÃO se pode contar "N boletins em 2026" — a mesma limitação do '
            'Vêneto, por motivo diferente: lá faltava o conteúdo, aqui falta o índice. '
            'EDIÇÃO LIDA ≠ SÉRIE MEDIDA continua valendo.'),
        'PROVINCES_PROBED': [
            {'PROVINCE': 'Grosseto', 'CROPS': ['Frumento', 'Vite integrato', 'Vite biologico'],
             'DURUM_NAMED_SEPARATELY': True},
            {'PROVINCE': 'Pisa', 'CROPS': ['Frumento'],
             'DURUM_NAMED_SEPARATELY': True},
            {'PROVINCE': 'Siena', 'CROPS': ['Vite integrato', 'Vite biologico'],
             'DURUM_NAMED_SEPARATELY': False,
             'NOTE': 'sem boletim de frumento — a cultura coberta varia por província'},
        ],
        'DISEASES_NAMED': DOENCAS_DO_BOLETIM,
        'SIGNAL_GRANULARITY': 'doença × fase fenológica × nível de risco × janela',
        'VERBATIM_IT': (
            'Dove la fase fenologica sta entrando in fioritura, considerate le piogge e '
            'le previsioni di piogge per i prossimi giorni, che comportano quindi un alto '
            'rischio fusariosi, se non già protette con un trattamento specifico, è '
            'opportuno effettuare un trattamento fitosanitario'),
        'WHY_IT_MATTERS': (
            'derruba a leitura de que a Itália não publica sinal de campo para a sua maior '
            'cultura. Publica, e com fase e janela. Eu é que não tinha perguntado.'),
    }


def main():
    port = json.load(open(PORT, encoding='utf-8'))
    prods = port['PRODUCTS']

    duros = [p for p in prods if 'DURUM_WHEAT' in (p.get('CROP_TERMS_PRESENT') or [])]
    por_classe = {}
    for p in duros:
        por_classe.setdefault(classificar(p), []).append({
            'PRODUCT': p['PRODUCT'], 'ACTIVE_SUBSTANCE': p['ACTIVE_SUBSTANCE'],
            'EXPIRY': p['EXPIRY'], 'STATUS': p['STATUS'],
            'TARGETS': [i['SCIENTIFIC_NAME'] for i in (p.get('ISSUES_FROM_SOURCE') or [])],
        })

    # Os foliares que casam com o conjunto de doenças do boletim, sem nomear grano duro.
    def casa(p):
        alvos = ' '.join(i.get('SCIENTIFIC_NAME', '')
                         for i in (p.get('ISSUES_FROM_SOURCE') or []))
        return ('Fusarium' in alvos
                and ('Septoria' in alvos or 'Zymoseptoria' in alvos)
                and 'Puccinia' in alvos)

    foliares = [{
        'PRODUCT': p['PRODUCT'], 'ACTIVE_SUBSTANCE': p['ACTIVE_SUBSTANCE'],
        'EXPIRY': p['EXPIRY'], 'MODE_OF_ACTION': p.get('MODE_OF_ACTION_DECLARED'),
        'CROP_TERMS_PRESENT': p['CROP_TERMS_PRESENT'],
        'NAMES_DURUM': 'DURUM_WHEAT' in (p.get('CROP_TERMS_PRESENT') or []),
        'TARGETS': [i['SCIENTIFIC_NAME'] for i in (p.get('ISSUES_FROM_SOURCE') or [])],
    } for p in prods if casa(p) and classificar(p) == 'FUNGICIDA_FOLIAR']

    # Vencimento dos que nomeiam grano duro — fato regulatório, não previsão comercial.
    venc = sorted((( _data(x['EXPIRY']), x['PRODUCT'], cls, x['EXPIRY'])
                   for cls, ls in por_classe.items() for x in ls if _data(x['EXPIRY'])),
                  key=lambda t: t[0])
    proximos = [{'PRODUCT': n, 'CLASS': c, 'EXPIRY': s, 'DAYS_FROM_AS_OF': (d - HOJE).days}
                for d, n, c, s in venc if 0 <= (d - HOJE).days <= 400]

    out = {
        'COUNTRY': 'IT',
        'SOURCE_ID': 'DERIVED/IT-DURUM-SIGNAL-x-PORTFOLIO',
        'SOURCE': 'IT-T3-LAMMA (campo, Toscana) × IT-T4-001 (rótulos oficiais)',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'AS_OF': HOJE.isoformat(),
        'SOURCE_LOCATION': 'Toscana (campo) · Itália (rótulos)',
        'FACT_LOCATION': 'ITALY',
        'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'CROP': 'Trigo duro', 'CROP_NATIONAL_THS_HA': 1177.4,
        'CROP_RANK_IN_ITALY': 1,
        'QUESTION': ('existe sinal público de campo para o trigo duro italiano, e o '
                     'portfólio da ADAMA nomeado para a cultura responde a ele?'),
        'ANSWER': ('sim, existe — eu não tinha perguntado. E não, o que nomeia grano duro '
                   'não responde a ele: são 13 herbicidas e 1 tratamento de semente, '
                   'nenhum fungicida foliar.'),
        'FIELD_SIGNAL': boletim_toscana(),
        'PORTFOLIO_NAMING_DURUM': {
            'TOTAL': len(duros),
            'BY_CLASS': {k: len(v) for k, v in sorted(por_classe.items())},
            'FOLIAR_FUNGICIDES_NAMING_DURUM': len(por_classe.get('FUNGICIDA_FOLIAR', [])),
            'PRODUCTS': por_classe,
        },
        'FOLIAR_MATCHING_THE_BULLETIN_BUT_NOT_NAMING_DURUM': foliares,
        'THE_MISMATCH': (
            'o sinal público é foliar e de espiga, na floração, sob chuva. O portfólio '
            'nomeado para a cultura é de plantas daninhas e de semente. As duas camadas '
            'existem e não se cruzam na mesma célula CULTURA × PROBLEMA × MOMENTO.'),
        'THE_OPEN_QUESTION': {
            'STATE': 'NÃO SEI',
            'QUESTION': ('"frumento" no rótulo italiano cobre juridicamente o grano duro?'),
            'WHY_IT_DECIDES_EVERYTHING': (
                'se cobre, não há lacuna nenhuma e o desencontro é artefato de redação de '
                'rótulo. Se não cobre, a lacuna é real e é sobre a maior cultura do país.'),
            'WHY_I_CANNOT_ANSWER': (
                'não é extraível do texto do rótulo, que é tudo o que tenho. Exige leitura '
                'jurídica do decreto de autorização — trabalho de direito regulatório, '
                'não de extração.'),
            'LAW': 'CROP_TERM ≠ AUTHORIZED_CROP',
        },
        'REGULATORY_FACT_EXPIRY': {
            'NOTE': ('vencimento é fato do registro. EXPIRY ≠ WITHDRAWAL: não afirma '
                     'retirada, nem indisponibilidade comercial.'),
            'NEXT_400_DAYS': proximos,
        },
        'WHAT_THIS_DOES_NOT_PROVE': [
            'que a ADAMA não possa tratar fusariose de espiga em trigo duro na Itália — '
            'isso depende da pergunta em aberto sobre "frumento"',
            'que o boletim da Toscana represente o trigo duro italiano: a Toscana tem '
            '43,7 mil ha, 3,7% do país. Puglia, Sicília e Basilicata continuam sem sonda',
            'quantas edições a Toscana publica por ano — a página é rolante, sem arquivo',
            'qualquer coisa sobre venda, participação de mercado ou prioridade interna',
        ],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print('TRIGO DURO — %d produtos nomeiam grano duro' % len(duros))
    for k, v in sorted(por_classe.items()):
        print('   %-20s %d' % (k, len(v)))
    print('  fungicida foliar nomeando grano duro: %d'
          % len(por_classe.get('FUNGICIDA_FOLIAR', [])))
    print('  foliares que casam com o boletim mas NAO nomeiam grano duro: %d  (%s)'
          % (len(foliares), ', '.join(f['PRODUCT'] for f in foliares)))
    for x in proximos:
        print('  vence em %4d dias: %-14s %s' % (x['DAYS_FROM_AS_OF'], x['PRODUCT'], x['CLASS']))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
