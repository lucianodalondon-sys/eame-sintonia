#!/usr/bin/env python3
"""
ITÁLIA — o painel que eu medi não é o país.

Este arquivo existe por causa de uma linha que eu publiquei e que estava certa em
aritmética e errada em sentido:

    TRIGO DURO · sinal cobre 0,0 % · 37,4 % medido · nenhuma região com sinal

O trigo duro é a **maior cultura da Itália** — 1.177,4 mil ha, mais que o milho e a
videira somados. Ler aquela linha leva a "a Itália não publica sinal de campo para a
sua maior cultura". Não é isso que o dado sustenta.

O QUE O 37,4 % REALMENTE ERA
----------------------------
As cinco regiões que entraram como *medidas* para trigo duro foram Vêneto (1,4 %),
Lombardia (1,4 %), Emilia-Romagna (5,9 %), Friuli-Venezia Giulia (**0,0 %**) e
Puglia (28,7 %). Ou seja:

  · **76,8 % da área "medida" é uma região só, a Puglia** — justamente aquela cujo
    notiziario agrometeorológico **deixou de redigir a seção de fitopatologia em
    11/04/2018**, por transferência de competência à ARIF. Não é silêncio agronômico;
    é uma decisão administrativa de oito anos atrás.
  · O **FVG entrou no painel com 0,0 mil ha de trigo duro**. Uma região que não planta
    a cultura não pode produzir evidência sobre a cultura. Não distorce a conta (área
    zero soma zero dos dois lados), mas é erro de categoria: ela aparece como se
    tivesse sido interrogada e tivesse respondido "não".
  · A **Sicília — 277,5 mil ha, 23,6 %, a segunda maior região de trigo duro do país —
    nunca foi medida para trigo duro.** Nem a Basilicata (9,8 %), nem as Marche (6,2 %).

O painel de oito regiões que montei foi escolhido para **milho e videira**, e nessas
duas ele é bom (89,6 % e 72,3 % da área). Para trigo duro e oliveira ele cobre ~63 %
da área, mas a parte *efetivamente interrogada* é muito menor.

A LEI QUE ESTE ARQUIVO ADICIONA
-------------------------------
    PAINEL MEDIDO ≠ PAÍS MEDIDO

E o corolário que dói mais:

    UM NÚMERO DE COBERTURA NÃO SIGNIFICA NADA SEM SABER DE QUANTAS REGIÕES ELE VEM.

Cobertura apoiada numa região só não é cobertura nacional — é uma amostra de tamanho
um com aparência de estatística. Por isso toda linha aqui publica
`SINGLE_REGION_DEPENDENCE_PCT`, e quando ela passa de 60 % o veredito da cultura vira
`UNMEASURED_NOT_ZERO`, independentemente de quanto o painel pareça cobrir.

O QUE ISTO **NÃO** DIZ
----------------------
Não diz que existe boletim de trigo duro na Sicília. Não sei. Diz que **eu não
perguntei**, e que "0,0 % de cobertura" foi lido como resposta quando era ausência de
pergunta. `NOT_ASKED ≠ NOT_FOUND ≠ DOES NOT EXIST` — três estados, não um.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ISTAT = os.path.join(ROOT, 'data', 'samples', 'IT-T1', 'IT-T1-001-istat-area-regional.json')
MATRIZ = os.path.join(ROOT, 'data', 'samples', 'IT-FONTES',
                      'ITALY-REGIONAL-COVERAGE-MATRIX.json')
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-FONTES', 'ITALY-PANEL-BIAS.json')

# Abaixo disto a região não consegue informar sobre a cultura: ou não a planta, ou a
# planta em escala que nenhum serviço regional acompanharia. Não é limiar de importância
# agronômica — é limiar de CAPACIDADE DE TESTEMUNHO.
LIMIAR_TESTEMUNHO_PCT = 2.0

# Acima disto a "cobertura" da cultura é, na prática, a opinião de uma região só.
LIMIAR_DEPENDENCIA_PCT = 60.0

NOMES = {'DURUM_WHEAT': 'Trigo duro', 'OLIVE': 'Oliveira',
         'MAIZE': 'Milho', 'VINE': 'Videira'}


def areas():
    """CROP -> (nacional, {REGIÃO: mil ha})."""
    d = json.load(open(ISTAT, encoding='utf-8'))
    return {c: (v['NATIONAL_THS_HA'],
                {r['REGION']: r['AREA_THS_HA'] for r in v['BY_REGION']})
            for c, v in d['BY_CROP'].items()}


def medidas_por_cultura():
    """CROP -> lista de regiões que ENTRARAM na conta de cobertura daquela cultura.

    Não é o painel inteiro: uma região pode estar na matriz e mesmo assim não ter sido
    interrogada para uma cultura específica.
    """
    m = json.load(open(MATRIZ, encoding='utf-8'))
    fora = {}
    for c, v in m['SIGNAL_COVERAGE_BY_CROP'].items():
        fora[c] = (list(v.get('REGIONS_WITH_SIGNAL', []))
                   + list(v.get('REGIONS_MEASURED_WITHOUT_SIGNAL', [])))
    # REGIÃO -> FIELD_STATE declarado. NOT_MEASURED é "não perguntei", e é diferente
    # de NOT_OBTAINED ("perguntei, a rota não respondeu").
    return fora, {r['REGION']: r.get('FIELD_STATE', 'NOT_MEASURED') for r in m['MATRIX']}


def avaliar(crop, nacional, area, medidas, painel):
    dentro = [(r, area.get(r, 0.0)) for r in medidas]
    total_medido = sum(a for _, a in dentro)
    pct_medido = 100.0 * total_medido / nacional if nacional else 0.0

    maior = max(dentro, key=lambda x: x[1]) if dentro else (None, 0.0)
    dependencia = 100.0 * maior[1] / total_medido if total_medido else 0.0

    mortas = [{'REGION': r, 'AREA_THS_HA': a,
               'PCT_NATIONAL': round(100.0 * a / nacional, 2)}
              for r, a in dentro if 100.0 * a / nacional < LIMIAR_TESTEMUNHO_PCT]

    # NOT_ASKED ≠ NOT_FOUND, e eu quase publiquei os dois com o mesmo rótulo. Uma região
    # que está no painel e não entrou na conta FOI interrogada — a rota é que falhou
    # (Piemonte, bacheca em JavaScript) ou o conteúdo não foi lido (Vêneto, milho da
    # AVISP). Chamá-la de "nunca perguntada" seria cometer, dentro do arquivo que
    # denuncia o colapso dos três estados, exatamente esse colapso.
    # E a régua NÃO é estar no painel: é o FIELD_STATE declarado. A Sicília e a Calábria
    # aparecem como linhas da matriz, mas com FIELD_STATE = NOT_MEASURED, "não medida
    # nesta rodada". Estar listado não é ter sido interrogado. Usar a lista como prova de
    # pergunta seria a mesma confusão entre presença e resposta, um nível acima.
    def maiores(cond):
        return sorted(
            ({'REGION': r, 'AREA_THS_HA': a,
              'PCT_NATIONAL': round(100.0 * a / nacional, 1),
              'FIELD_STATE': painel.get(r, 'FORA_DO_PAINEL')}
             for r, a in area.items()
             if r not in medidas and cond(painel.get(r, 'FORA_DO_PAINEL'))
             and 100.0 * a / nacional >= LIMIAR_TESTEMUNHO_PCT),
            key=lambda x: -x['AREA_THS_HA'])

    nunca = ('FORA_DO_PAINEL', 'NOT_MEASURED')
    nao_perguntadas = maiores(lambda st: st in nunca)
    perguntadas_sem_resposta = maiores(lambda st: st not in nunca)

    # A fatia que foi interrogada por uma região capaz de testemunhar.
    efetivo = sum(a for r, a in dentro if 100.0 * a / nacional >= LIMIAR_TESTEMUNHO_PCT)

    if dependencia >= LIMIAR_DEPENDENCIA_PCT:
        veredito = 'UNMEASURED_NOT_ZERO'
        porque = ('%.1f%% da área "medida" vem de uma região só (%s). Uma amostra de '
                  'tamanho um não é cobertura nacional.' % (dependencia, maior[0]))
    elif pct_medido < 50.0:
        veredito = 'PARTIALLY_MEASURED'
        porque = 'menos de metade da área nacional entrou na conta'
    else:
        veredito = 'MEASURED_ON_A_REPRESENTATIVE_PANEL'
        porque = 'mais de metade da área, distribuída em mais de uma região'

    # A distinção entre os dois estados não é escrúpulo: ela diz QUE TRABALHO fecha a
    # lacuna. Rota que falhou se conserta com engenharia (renderizar JS, achar o índice).
    # Região nunca perguntada se conserta abrindo o painel. São orçamentos diferentes, e
    # tratá-las como uma coisa só faz gastar o esforço errado na cultura errada.
    pct_nunca = sum(x['AREA_THS_HA'] for x in nao_perguntadas) * 100.0 / nacional
    pct_rota = sum(x['AREA_THS_HA'] for x in perguntadas_sem_resposta) * 100.0 / nacional
    if pct_nunca < 5.0 and pct_rota < 5.0:
        tipo, trabalho = 'NO_MATERIAL_GAP', 'nada a abrir nesta cultura'
    elif pct_rota > pct_nunca:
        tipo = 'ROUTE_ENGINEERING'
        trabalho = ('as regiões certas já foram interrogadas; o que falha é a rota '
                    '(JavaScript, índice ausente). Conserta-se com engenharia de coleta, '
                    'não abrindo região nova.')
    else:
        tipo = 'PANEL_EXPANSION'
        trabalho = ('a lacuna não é técnica: são regiões grandes que nunca foram '
                    'perguntadas. Nenhuma engenharia de rota resolve — é preciso abrir '
                    'o painel.')

    return {
        'CROP': NOMES.get(crop, crop),
        'NATIONAL_THS_HA': nacional,
        'REGIONS_COUNTED_AS_MEASURED': [r for r, _ in dentro],
        'PCT_NATIONAL_COUNTED_AS_MEASURED': round(pct_medido, 1),
        'LARGEST_MEASURED_REGION': maior[0],
        'SINGLE_REGION_DEPENDENCE_PCT': round(dependencia, 1),
        'PCT_NATIONAL_EFFECTIVELY_INTERROGATED': round(100.0 * efetivo / nacional, 1),
        'DEAD_WEIGHT_IN_PANEL': mortas,
        'LARGEST_REGIONS_NEVER_ASKED': nao_perguntadas[:5],
        'PCT_NATIONAL_NEVER_ASKED': round(
            sum(x['AREA_THS_HA'] for x in nao_perguntadas) * 100.0 / nacional, 1),
        # Estado intermediário, e é o que separa este arquivo de uma acusação preguiçosa.
        'REGIONS_ASKED_ROUTE_DID_NOT_ANSWER': perguntadas_sem_resposta,
        'PCT_NATIONAL_ASKED_ROUTE_DID_NOT_ANSWER': round(
            sum(x['AREA_THS_HA'] for x in perguntadas_sem_resposta) * 100.0 / nacional, 1),
        'VERDICT': veredito,
        'WHY': porque,
        'GAP_TYPE': tipo,
        'WHAT_WOULD_CLOSE_IT': trabalho,
    }


def main():
    a = areas()
    medidas, painel = medidas_por_cultura()
    linhas = {}
    for crop, regs in medidas.items():
        if crop not in a:
            continue
        nacional, area = a[crop]
        linhas[crop] = avaliar(crop, nacional, area, regs, painel)

    out = {
        'COUNTRY': 'IT',
        'SOURCE_ID': 'DERIVED/IT-PANEL-BIAS',
        'SOURCE': 'IT-T1-001 (área regional ISTAT) × ITALY-REGIONAL-COVERAGE-MATRIX',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'SOURCE_LOCATION': 'interno — auditoria de método sobre artefatos próprios',
        'FACT_LOCATION': 'ITALY',
        'ORIGINAL_LANGUAGE': 'pt',
        'QUESTION': ('quando eu digo que uma cultura tem X% de cobertura de sinal de '
                     'campo, de quantas regiões esse X vem?'),
        'ANSWER': ('no trigo duro, de uma só — e é a que parou de publicar fitopatologia '
                   'em 2018. O 0,0% não mede o país; mede um jornal descontinuado.'),
        'LAW_ADDED': 'PAINEL MEDIDO ≠ PAÍS MEDIDO',
        'LAW_COROLLARY': ('NOT_ASKED ≠ NOT_FOUND ≠ DOES NOT EXIST. São três estados. '
                          'Publicar "0,0% de cobertura" para uma cultura que só foi '
                          'perguntada a uma região colapsa os três em um.'),
        'THRESHOLDS': {
            'LIMIAR_TESTEMUNHO_PCT': LIMIAR_TESTEMUNHO_PCT,
            'PORQUE': ('abaixo disto a região não planta a cultura em escala que qualquer '
                       'serviço regional acompanharia; ela não pode testemunhar. Não é '
                       'limiar de importância agronômica, é de capacidade de testemunho.'),
            'LIMIAR_DEPENDENCIA_PCT': LIMIAR_DEPENDENCIA_PCT,
            'PORQUE_DEPENDENCIA': ('acima disto a cobertura da cultura é, na prática, a '
                                   'opinião de uma região só, e o veredito vira '
                                   'UNMEASURED_NOT_ZERO por mais que o painel pareça grande.'),
        },
        'PANEL': painel,
        'PANEL_NOTE': ('estar nesta lista não é ter sido interrogado. A Sicília e a '
                       'Calábria são linhas da matriz com FIELD_STATE = NOT_MEASURED.'),
        'BY_CROP': linhas,
        'WHAT_THIS_CHANGES': [
            ('a linha "trigo duro · 0,0% de cobertura" deixa de ser lida como ausência '
             'de sinal no país e passa a ser lida como AUSÊNCIA DE PERGUNTA'),
            ('a próxima sonda de campo mais informativa da Itália não é mais milho nem '
             'videira: é TRIGO DURO NA SICÍLIA (277,5 mil ha, 23,6%) e NA BASILICATA '
             '(115,2 mil ha, 9,8%), duas regiões nunca interrogadas para a cultura'),
        ],
        'WHAT_THIS_DOES_NOT_PROVE': [
            'que exista boletim de trigo duro na Sicília ou na Basilicata — não perguntei',
            'que a Puglia tenha deixado de ter pressão de doença em trigo duro; o que '
            'cessou foi a PUBLICAÇÃO da seção de fitopatologia, por ato administrativo',
            'que as culturas com veredito MEASURED_ON_A_REPRESENTATIVE_PANEL estejam '
            'corretamente medidas — só que a crítica de painel não as derruba',
        ],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    for c, v in sorted(linhas.items(), key=lambda x: -x[1]['SINGLE_REGION_DEPENDENCE_PCT']):
        print('%-12s medido %5.1f%% · dependencia de %-16s %5.1f%% · %s  [%s]'
              % (v['CROP'], v['PCT_NATIONAL_COUNTED_AS_MEASURED'],
                 v['LARGEST_MEASURED_REGION'], v['SINGLE_REGION_DEPENDENCE_PCT'],
                 v['VERDICT'], v['GAP_TYPE']))
        if v['DEAD_WEIGHT_IN_PANEL']:
            print('    peso morto no painel: '
                  + ', '.join('%s (%.1f%%)' % (x['REGION'], x['PCT_NATIONAL'])
                              for x in v['DEAD_WEIGHT_IN_PANEL']))
        if v['LARGEST_REGIONS_NEVER_ASKED']:
            print('    NUNCA perguntadas: '
                  + ', '.join('%s %.1f%%' % (x['REGION'], x['PCT_NATIONAL'])
                              for x in v['LARGEST_REGIONS_NEVER_ASKED'][:3])
                  + '  (total %.1f%%)' % v['PCT_NATIONAL_NEVER_ASKED'])
        if v['REGIONS_ASKED_ROUTE_DID_NOT_ANSWER']:
            print('    perguntadas, rota nao respondeu: '
                  + ', '.join('%s %.1f%%' % (x['REGION'], x['PCT_NATIONAL'])
                              for x in v['REGIONS_ASKED_ROUTE_DID_NOT_ANSWER'][:3])
                  + '  (total %.1f%%)' % v['PCT_NATIONAL_ASKED_ROUTE_DID_NOT_ANSWER'])
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
