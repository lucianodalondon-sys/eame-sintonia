#!/usr/bin/env python3
"""
ITÁLIA — os casos candidatos, com as pernas separadas e mensuráveis.

Um "hero case" só é caso quando cada perna existe por conta própria e é citável. Aqui a
estrutura força isso: nenhuma perna herda força da outra, e a perna que falta aparece
como falta — não some.

    SCALE          quanto e onde (área medida)
    FIELD          o campo está dizendo algo AGORA?
    WINDOW         a janela está aberta, e a janela DE QUÊ?
    SCIENCE        a ciência olha para isto?
    ADAMA          existe resposta REGISTRADA, com alvo declarado no rótulo?

`CONVERGENCE` conta quantas pernas têm evidência. É deliberadamente uma CONTAGEM e não um
escore ponderado: peso seria opinião disfarçada de número.

A distinção que este arquivo protege — e que trocou o caso vencedor desta rodada:

    WINDOW_FOR_SYMPTOM_RECOGNITION  ≠  WINDOW_FOR_VECTOR_CONTROL

O boletim da Lombardia dá a primeira; o produto da ADAMA age na segunda. São o mesmo caso
e não são a mesma janela, e tratá-las como uma só seria vender uma decisão que não foi
medida.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-hero-case-candidates.json')

PERNAS = ('SCALE', 'FIELD', 'WINDOW', 'SCIENCE', 'ADAMA_REGISTERED_RESPONSE')


def convergencia(caso):
    """Quantas pernas têm evidência. NÃO SEI e NOT_FOUND não contam — é o ponto."""
    n = 0
    for p in PERNAS:
        est = (caso.get(p) or {}).get('STATE', '')
        if est and not est.startswith(('NÃO SEI', 'NOT_FOUND', 'NOT_DERIVED', 'UNKNOWN')):
            n += 1
    return n


def casos():
    return [
        {
            'CASE_ID': 'IT-HERO-001', 'COUNTRY': 'IT',
            'CROP': 'Videira (Vitis vinifera)', 'CROP_CODE': 'W1000',
            'ISSUE': 'Flavescência dourada (fitoplasma) via vetor Scaphoideus titanus',
            'REGION': 'Lombardia (sinal); Vêneto NÃO VERIFICADO',
            'SCALE': {'STATE': 'MEASURED', 'AREA_THS_HA': 715.8, 'RANK_COMMODITY': 3,
                      'REGIONAL_BREAKDOWN': 'NÃO SEI — apro_cpshr não publica W1000 em NUTS 2',
                      'SOURCE': 'EU-T1-001'},
            'FIELD': {'STATE': 'CURRENT_SIGNAL',
                      'DOCUMENT': 'Bollettino Regionale LA VITE n.6 — 31/07/2026',
                      'SOURCE': 'IT-T3-003 (Regione Lombardia, Servizio Fitosanitario)',
                      'INSTITUTIONAL_LAYER': 'remete ao Documento tecnico ufficiale n. 29 '
                                             'dei Servizi Fitosanitari Nazionali'},
            'WINDOW': {'STATE': 'OPEN',
                       'WINDOW_FOR_SYMPTOM_RECOGNITION': 'início de agosto a fim de setembro',
                       'AS_OF': '2026-08-30',
                       'WINDOW_FOR_VECTOR_CONTROL': 'NÃO SEI — não medido. O produto da ADAMA '
                                                    'age no VETOR; a janela publicada é de '
                                                    'RECONHECIMENTO DE SINTOMA. Não são a mesma.'},
            'SCIENCE': {'STATE': 'MEASURED', 'GRAPEVINE_PHYTOPLASMA_WORKS': 135,
                        'SCAPHOIDEUS_TITANUS_WORKS': 66, 'SOURCE': 'IT-T5-001'},
            'ADAMA_REGISTERED_RESPONSE': {
                'STATE': 'FOUND_WITH_DECLARED_TARGET', 'PRODUCTS': 6,
                'ACTIVE_SUBSTANCE': 'TAU-FLUVALINATE',
                'PRODUCT_NAMES': ['KLARTAN 20 EW', 'KLARTAN SMART', 'TAU AL 240 EW',
                                  'MAVRIK EW', 'MAVRIK SMART', 'EVURE PRO'],
                'LABEL_QUOTE': ('Vite (da vino e da tavola) Contro cicaline (Empoasca vitis, '
                                'Scaphoideus titanus) e tripidi ... impiegare a 30-300 ml/hl '
                                'senza superare 0,3 l/ha'),
                'EVIDENCE_CLASS': 'REGULATORY_FACT', 'SOURCE': 'IT-T4-001-ETICHETTA'},
            'WHAT_IS_UNKNOWN': [
                'janela de controle do vetor', 'área de videira por região',
                'se o mesmo sinal vale no Vêneto', 'disponibilidade comercial',
                'pressão real de campo em 30/08', 'prioridade interna da ADAMA Italia'],
        },
        {
            'CASE_ID': 'IT-HERO-002', 'COUNTRY': 'IT',
            'CROP': 'Oliveira', 'CROP_CODE': 'O1000',
            'ISSUE': 'Mosca-da-azeitona (Bactrocera oleae)', 'REGION': 'Vêneto',
            'SCALE': {'STATE': 'MEASURED', 'AREA_THS_HA': 1083.0, 'RANK_COMMODITY': 2,
                      'REGIONAL_BREAKDOWN': 'NÃO SEI — sem NUTS 2 nesta fonte',
                      'SOURCE': 'EU-T1-001'},
            'FIELD': {'STATE': 'CURRENT_SIGNAL',
                      'DOCUMENT': 'Bollettino Olivo n.28 — 26/08/2026',
                      'OBSERVED_STAGE': 'ingrossamento/inolizione',
                      'SUB_REGIONAL_PRESSURE': '11 áreas nomeadas, 3–4% (Litorale veneziano 4–6%)',
                      'SOURCE': 'IT-T3-002 (Regione Veneto)'},
            'WINDOW': {'STATE': 'OPEN',
                       'DECLARED': 'queda térmica e aumento de umidade abrindo janela favorável '
                                   'à retomada da ovideposição', 'AS_OF': '2026-08-30'},
            'SCIENCE': {'STATE': 'MEASURED', 'BACTROCERA_WORKS': 70,
                        'NOTE': 'Xylella domina a ciência italiana da oliveira com 296',
                        'SOURCE': 'IT-T5-001'},
            'ADAMA_REGISTERED_RESPONSE': {
                'STATE': 'NOT_FOUND',
                'MEANING': 'Nenhum rótulo analisado declara Bactrocera oleae como alvo. '
                           'A presença da ADAMA em oliveira é herbicida de solo (glifosato, '
                           'fluroxipir) e óleo de parafina. NOT_FOUND é sobre os rótulos '
                           'analisados, não sobre o portfólio mundial.'},
            'WHAT_IS_UNKNOWN': ['área de oliveira por região', 'peso do Vêneto na oliveira italiana'],
        },
        {
            'CASE_ID': 'IT-HERO-003', 'COUNTRY': 'IT',
            'CROP': 'Milho grão', 'CROP_CODE': 'C1500',
            'ISSUE': 'DOIS candidatos medidos — ver ISSUE_CANDIDATES',
            'ISSUE_CANDIDATES': {
                'WEEDS': {
                    'ADAMA_PRODUCTS': 24, 'SCIENCE_WORKS': 79,
                    'MODE_OF_ACTION_GROUPS': ['HRAC 2 (B)', 'HRAC 3 (K1)', 'HRAC 4 (O)',
                                              'HRAC 5 (C1)', 'HRAC 27 (F2)', 'HRAC G'],
                    'STRENGTH': 'profundidade de portfólio e diversidade de modo de ação',
                    'WEAKNESS': 'nenhum alvo com época de aplicação declarada extraída'},
                'LEPIDOPTERA_OSTRINIA': {
                    'ADAMA_PRODUCTS': 1, 'PRODUCT': 'COSAYR 200 SC',
                    'REGISTRATION': '18561, de 04/02/2026',
                    'ACTIVE_SUBSTANCE': 'CHLORANTRANILIPROLE', 'MODE_OF_ACTION': 'IRAC 28',
                    'LABEL_QUOTE': ('Mais e Mais Dolce: utilizzare 100-150 mL/ha per il '
                                    'controllo di O. nubilalis e lepidotteri nottuidi quali '
                                    'H. armigera, S. exigua, S. littoralis, Sesamia spp. '
                                    'Intervenire in fase di ovideposizione'),
                    'SCIENCE_WORKS': 30,
                    'STRENGTH': ('registro NOVO (fev/2026), alvo declarado, dose E ÉPOCA '
                                 'de aplicação no rótulo — o único caso de milho com época'),
                    'WEAKNESS': 'um produto só; ciência modesta (30)'},
            },
            'MYCOTOXIN_BRIDGE_TESTED': {
                'HYPOTHESIS': ('o dano da broca é porta de entrada de Fusarium, o que ligaria '
                               'o produto novo ao cluster científico dominante (208 trabalhos)'),
                'MEASURED': 'milho × Ostrinia × micotoxina = 5 trabalhos italianos',
                'VERDICT': 'NÃO SUSTENTADO como convergência medida — 5 é pouco demais. '
                           'A ligação é agronomicamente plausível e NÃO foi provada aqui. '
                           'Fica como hipótese, com o teste que a mediria já escrito.'},
            'REGION': 'Planície do Pó — Vêneto, Lombardia, Piemonte',
            'SCALE': {'STATE': 'MEASURED', 'AREA_THS_HA': 495.4, 'RANK_COMMODITY': 5,
                      'RANK_ANNUAL': 3, 'TOP3_CONCENTRATION_PCT': 71.6,
                      'TOP_REGIONS': {'Veneto': 122.9, 'Lombardia': 115.8, 'Piemonte': 115.8},
                      'SOURCE': 'EU-T1-001'},
            'FIELD': {'STATE': 'NOT_FOUND',
                      'MEASURED': 'Vêneto 2026: ~90 boletins de permanentes/hortícolas contra 2 '
                                  'de herbáceas (o único aberto trata de beterraba/Cercospora). '
                                  'Lombardia: 0 de herbáceas. Fontes responderam HTTP 200: é '
                                  'ausência medida de COBERTURA, não falha de leitura.'},
            'WINDOW': {'STATE': 'PARTIAL',
                       'DECLARED_ON_LABEL': ('COSAYR 200 SC declara a época: "intervenire in '
                                             'fase di ovideposizione" — é época FENOLÓGICA DA '
                                             'PRAGA, não data de calendário'),
                       'WHY_NOT_A_DATE': ('sem calendário agronômico regional nem monitoramento '
                                          'de voo, "ovideposição" não vira data. BBCH aparece em '
                                          '2 de ~160 rótulos — não é rota na Itália')},
            'SCIENCE': {'STATE': 'MEASURED', 'MAIZE_WEED_WORKS': 79, 'MAIZE_BORER_WORKS': 30,
                        'HERBICIDE_RESISTANCE_IT_WORKS': 103, 'MAIZE_HERB_RESISTANCE_WORKS': 5,
                        'CONTRAST': 'milho × micotoxina/Fusarium = 208, 2,6× as daninhas',
                        'SOURCE': 'IT-T5-001'},
            'ADAMA_REGISTERED_RESPONSE': {
                'STATE': 'FOUND', 'HERBICIDES_CITING_MAIZE': 24, 'FUNGICIDES_CITING_MAIZE': 0,
                'INSECTICIDES_CITING_MAIZE': 9,
                'MODE_OF_ACTION_GROUPS_DECLARED': ['HRAC 2 (B)', 'HRAC 3 (K1)', 'HRAC 4 (O)',
                                                   'HRAC 5 (C1)', 'HRAC 27 (F2)', 'HRAC G'],
                'SOURCE': 'IT-T4-001-ETICHETTA'},
            'STRATEGIC_INPUT': {
                'STATEMENT': 'STRATEGIC_ADAMA_EAME_PRIORITY(MAIZE) = HIGH',
                'ORIGIN': 'fornecido pelo enunciado da missão — entrada, não medição',
                'WHAT_MEASUREMENT_SAYS': 'não contradiz: o milho italiano é grande e concentrado. '
                                         'Mas é, dos três casos, o de MENOR evidência demonstrável '
                                         'hoje — sem sinal de campo, sem janela derivável, e com a '
                                         'resposta registrada apontando para problema diferente do '
                                         'que a ciência mais estuda.'},
            'WHAT_IS_UNKNOWN': ['pressão real de daninhas', 'janela de aplicação',
                                'resistência observada em campo na Itália', 'venda', 'market share'],
        },
    ]


def main():
    cs = casos()
    for c in cs:
        c['CONVERGENCE_LEGS_WITH_EVIDENCE'] = convergencia(c)
        c['CONVERGENCE_OF'] = len(PERNAS)
    cs.sort(key=lambda c: -c['CONVERGENCE_LEGS_WITH_EVIDENCE'])
    out = {
        'COUNTRY': 'IT', 'AS_OF': '2026-08-30',
        # Proveniência do próprio artefato: ele é DERIVADO, e tem de dizer de que
        # fontes deriva. Há teste que reprova amostra sem origem e sem data.
        'SOURCE_ID': 'DERIVED/IT-HERO-CASES',
        'SOURCE': ('derivado de EU-T1-001 (escala), IT-T3-002 e IT-T3-003 (campo), '
                   'IT-T5-001 (ciência) e IT-T4-001-ETICHETTA (resposta registrada)'),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'METHOD': ('Cada perna é medida por conta própria e citada com fonte. CONVERGENCE é '
                   'CONTAGEM de pernas com evidência, nunca escore ponderado — peso seria '
                   'opinião disfarçada de número.'),
        'LEGS': list(PERNAS),
        'BEST_CURRENT_CASE': cs[0]['CASE_ID'],
        'BEST_MAIZE_CASE': 'IT-HERO-003',
        'CROSS_MARKET_RELATION': 'NOT_TESTED',
        'CASES': cs,
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    for c in cs:
        print('%-12s %d/%d pernas  %s × %s' % (c['CASE_ID'], c['CONVERGENCE_LEGS_WITH_EVIDENCE'],
                                               len(PERNAS), c['CROP'], c['ISSUE'][:44]))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
