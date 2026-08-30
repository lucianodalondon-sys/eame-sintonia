#!/usr/bin/env python3
"""
ITÁLIA — o trigo duro está coberto, e quem tinha a lacuna era o meu extrator.

Este arquivo mudou de conclusão no mesmo dia em que nasceu. A versão da manhã dizia:

    "O sinal público é foliar e de espiga, na floração. O portfólio nomeado para trigo
     duro é de plantas daninhas e de semente. As duas camadas não se cruzam."

**Isso estava errado, e o erro era meu.**

O QUE ACONTECEU
---------------
A tabela de usos autorizados escreve a coluna `Coltura` como um cabeçalho para DUAS
culturas de uma vez:

    DOSI ED EPOCHE DI IMPIEGO
    Coltura: **Frumento tenero e duro (invernale e primaverile)**

O padrão `frumento\\s+duro` não casa nisso — o substantivo não encosta no adjetivo. Onze
dos vinte e cinco rótulos que autorizam trigo duro estavam sendo perdidos por um espaço
em branco: **79 % de subcontagem**. E entre os perdidos estavam **todos os fungicidas
foliares de cereal**. A cultura mais plantada da Itália parecia descoberta por causa de
uma conjunção.

A CONVERGÊNCIA REAL, NOS TRÊS EIXOS
------------------------------------
Corrigido o extrator, o cruzamento fecha exatamente:

    CULTURA   o rótulo do MAXENTIS/KOJAMI diz, na própria tabela de usos autorizados,
              "Frumento tenero e duro (invernale e primaverile)"

    PROBLEMA  a mesma linha lista "Fusarium (Fusarium spp., Microdochium spp.)",
              "Septoria (Zymoseptoria tritici, Septoria nodorum)", "Oidio
              (Blumeria graminis)" e "Ruggini (Puccinia striiformis, P. recondita)" —
              o conjunto que o boletim de campo da Toscana nomeia, item por item

    MOMENTO   o rótulo declara a janela: "Intervenire tra gli stadi di primo nodo
              visibile (inizio levata) e **fine fioritura** per il controllo delle
              fusariosi del frumento"
              e o boletim de Grosseto diz: "Dove la fase fenologica sta entrando in
              **fioritura** ... alto rischio fusariosi ... è opportuno effettuare un
              trattamento fitosanitario"

Mesma cultura, mesmo patógeno, mesma janela — e a janela sai do **rótulo oficial** de um
lado e do **boletim regional** do outro, sem ninguém precisar inferir nada.

A LIÇÃO, QUE VALE MAIS QUE O ACHADO
------------------------------------
De manhã o padrão dos dados era convincente: 13 herbicidas, 1 tratamento de semente,
**zero** fungicidas foliares. Era tentador publicar "a ADAMA tem uma lacuna na maior
cultura da Itália". Eu não publiquei — declarei `NÃO SEI`, porque cinco foliares casavam
com o conjunto de doenças e a pergunta de cobertura jurídica estava em aberto.

**A resposta veio ao contrário do que o padrão sugeria.** Se eu tivesse resolvido a
dúvida por plausibilidade, teria publicado uma acusação falsa sobre o portfólio, e ela
teria passado — era coerente com tudo que estava medido.

    UM PADRÃO FORTE NOS DADOS NÃO É PERMISSÃO PARA FECHAR UMA PERGUNTA ABERTA.

E a lei local se inverte junto. Não era `CROP_TERM ≠ AUTHORIZED_CROP` no sentido em que
eu usei: aqui o termo aparece **dentro da coluna `Coltura` da tabela de usos
autorizados**, que é a evidência mais forte que um rótulo oferece. O que faltava não era
autoridade jurídica sobre o termo — era **ler o termo direito**.

O QUE CONTINUA VERDADE
-----------------------
A crítica de painel (`italia_vies_de_painel.py`) não muda: 57,9 % do trigo duro italiano
segue sem sonda de campo, e a Toscana são 3,7 % da área. **A camada de campo continua
rasa; a camada de portfólio é que não estava.**
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
        'ANSWER': ('sim para as duas. O sinal existe (LaMMA/Toscana) e o portfólio '
                   'responde: 5 fungicidas foliares autorizados em "Frumento tenero e '
                   'duro" contra Fusarium, com a janela declarada no próprio rótulo — '
                   'inizio levata a FINE FIORITURA —, que é a mesma janela do boletim.'),
        'FIELD_SIGNAL': boletim_toscana(),
        'PORTFOLIO_NAMING_DURUM': {
            'TOTAL': len(duros),
            'BY_CLASS': {k: len(v) for k, v in sorted(por_classe.items())},
            'FOLIAR_FUNGICIDES_NAMING_DURUM': len(por_classe.get('FUNGICIDA_FOLIAR', [])),
            'PRODUCTS': por_classe,
        },
        'FOLIAR_MATCHING_THE_BULLETIN': foliares,
        'FOLIAR_MATCHING_AND_NAMING_DURUM': [f['PRODUCT'] for f in foliares
                                             if f['NAMES_DURUM']],
        'NOTE_ON_THIS_FIELD': (
            'na versão da manhã este campo se chamava '
            'FOLIAR_MATCHING_THE_BULLETIN_BUT_NOT_NAMING_DURUM e a lista era a mesma. '
            'Não mudou o conjunto de produtos: mudou o que eu conseguia ler no rótulo '
            'deles. Os cinco sempre nomearam grano duro, na forma coordenada.'),
        'THE_CONVERGENCE': {
            'CROP': ('a coluna Coltura da tabela de usos autorizados do MAXENTIS/KOJAMI '
                     'diz "Frumento tenero e duro (invernale e primaverile)"'),
            'ISSUE': ('a mesma linha lista Fusarium (Fusarium spp., Microdochium spp.), '
                      'Septoria (Zymoseptoria tritici, Septoria nodorum), Oidio '
                      '(Blumeria graminis) e Ruggini (Puccinia striiformis, '
                      'P. recondita) — o conjunto do boletim, item por item'),
            'TIMING_FROM_LABEL_IT': ('Intervenire tra gli stadi di primo nodo visibile '
                                     '(inizio levata) e fine fioritura per il controllo '
                                     'delle fusariosi del frumento'),
            'TIMING_FROM_FIELD_IT': ('Dove la fase fenologica sta entrando in fioritura, '
                                     'considerate le piogge e le previsioni di piogge '
                                     'per i prossimi giorni, che comportano quindi un '
                                     'alto rischio fusariosi ... è opportuno effettuare '
                                     'un trattamento fitosanitario'),
            'AXES_THAT_MATCH': ['CROP', 'ISSUE', 'TIMING'],
            'EVIDENCE_CLASS': 'CROP_IN_AUTHORIZED_USE_TABLE',
            'WHY_THAT_CLASS_IS_STRONGER': (
                'o termo não aparece em prosa solta: aparece na coluna Coltura da seção '
                'DOSI ED EPOCHE DI IMPIEGO, que é a tabela de usos autorizados. É a '
                'evidência mais forte que um rótulo oferece sobre cultura.'),
        },
        'MY_OWN_DEFECT_THAT_THIS_CORRECTS': {
            'WHAT_I_PUBLISHED_THIS_MORNING': (
                'que o portfólio nomeado para trigo duro era só de plantas daninhas e '
                'de semente, com ZERO fungicidas foliares'),
            'WHY_IT_WAS_WRONG': (
                'o padrão `frumento\\s+duro` não casa em "Frumento tenero e duro" — o '
                'substantivo não encosta no adjetivo. A forma coordenada é como a tabela '
                'de usos autorizados escreve um cabeçalho para duas culturas.'),
            'MEASURED_IMPACT': ('11 dos 25 rótulos que autorizam trigo duro estavam sendo '
                                'perdidos: 79% de subcontagem, e entre os perdidos '
                                'estavam TODOS os fungicidas foliares de cereal'),
            'FIXED_IN': 'scripts/italia_rotulo_parse.py — CROP_TERMS, forma coordenada',
            'GUARDED_BY': 'tests/test_italia.py::TestFormaCoordenadaDaCultura',
        },
        'THE_QUESTION_THAT_WAS_OPEN': {
            'STATE': 'RESOLVIDA — e ao contrário do que o padrão dos dados sugeria',
            'QUESTION': ('"frumento" no rótulo italiano cobre juridicamente o grano duro?'),
            'ANSWER': (
                'a pergunta estava mal posta, e a culpa é minha. O rótulo NÃO diz '
                '"frumento" genérico e deixa a cobertura para o intérprete: ele diz, '
                'literalmente e na tabela de usos autorizados, "Frumento tenero e duro". '
                'Não faltava autoridade jurídica sobre o termo — faltava ler o termo '
                'direito.'),
            'WHAT_THIS_TEACHES': (
                'de manhã o padrão era convincente: 13 herbicidas, 1 tratamento de '
                'semente, ZERO foliares. Era tentador publicar "a ADAMA tem uma lacuna '
                'na maior cultura da Itália". Eu declarei NÃO SEI, e a resposta veio ao '
                'CONTRÁRIO do padrão. Resolver a dúvida por plausibilidade teria '
                'publicado uma acusação falsa sobre o portfólio — e ela teria passado, '
                'porque era coerente com tudo que estava medido.'),
            'LAW': ('UM PADRÃO FORTE NOS DADOS NÃO É PERMISSÃO PARA FECHAR UMA PERGUNTA '
                    'ABERTA'),
        },
        'REGULATORY_FACT_EXPIRY': {
            'NOTE': ('vencimento é fato do registro. EXPIRY ≠ WITHDRAWAL: não afirma '
                     'retirada, nem indisponibilidade comercial.'),
            'NEXT_400_DAYS': proximos,
        },
        'WHAT_THIS_DOES_NOT_PROVE': [
            'que exista qualquer coisa sobre venda, participação de mercado, '
            'disponibilidade em ponto de venda ou prioridade interna — o rótulo prova '
            'autorização, e REGISTRATION ≠ COMMERCIAL AVAILABILITY continua valendo',
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
    nd = [f['PRODUCT'] for f in foliares if f['NAMES_DURUM']]
    print('  foliares que casam com o boletim: %d  (%s)'
          % (len(foliares), ', '.join(f['PRODUCT'] for f in foliares)))
    print('  destes, nomeiam grano duro na tabela de usos autorizados: %d  (%s)'
          % (len(nd), ', '.join(nd)))
    for x in proximos:
        print('  vence em %4d dias: %-14s %s' % (x['DAYS_FROM_AS_OF'], x['PRODUCT'], x['CLASS']))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
