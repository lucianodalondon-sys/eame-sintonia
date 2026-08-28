#!/usr/bin/env python3
"""
ASK SINTONIA — teste da camada de evidência.

A apresentação promete "a way to query the evidence layer". Antes de construir
qualquer interface, é preciso provar que a camada **é consultável**. Este script
responde perguntas reais usando SOMENTE o que já está preservado no repositório,
e separa, para cada uma: FACT · DERIVED · UNKNOWN.

Não há chatbot aqui. Há consulta determinística sobre evidência preservada.

    python3 scripts/ask_sintonia.py
"""
import csv, json, os, re, sys, xml.etree.ElementTree as ET
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FR = os.path.join(ROOT, 'data', 'raw', 'FR-T4-001')
IT = os.path.join(ROOT, 'data', 'raw', 'IT-T4-001', 'PROD_FTS_6_20260824.csv')
S = os.path.join(ROOT, 'data', 'samples')

ANSWERS = []


def record(q, answer, evidence, source, fact, derived, unknown, confidence):
    ANSWERS.append({'QUESTION': q, 'ANSWER': answer, 'EVIDENCE': evidence,
                    'SOURCE': source, 'WHAT_IS_FACT': fact,
                    'WHAT_IS_DERIVED': derived, 'WHAT_IS_UNKNOWN': unknown,
                    'CONFIDENCE': confidence})
    print(f'\n■ {q}')
    print(f'  RESPOSTA   {answer}')
    print(f'  FONTE      {source}')
    print(f'  EVIDÊNCIA  {evidence}')
    print(f'  FATO       {fact}')
    print(f'  DERIVADO   {derived}')
    print(f'  NÃO SEI    {unknown}')
    print(f'  CONFIANÇA  {confidence}')


def fr_products():
    with open(os.path.join(FR, 'produits_utf8.csv'), encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter=';'))


def fr_uses():
    with open(os.path.join(FR, 'usages_des_produits_autorises_utf8.csv'), encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter=';'))


def q1():
    """Which ADAMA cereal products in France depend on prothioconazole?"""
    au = [r for r in fr_products() if r['Etat d’autorisation'] == 'AUTORISE']
    hits = [r for r in au if 'ADAMA' in (r['titulaire'] or '').upper()
            and re.search('prothioconazole', r['Substances actives'], re.I)]
    names = [f"{r['nom produit']} (AMM {r['numero AMM']})" for r in hits]
    total = len([r for r in au if re.search('prothioconazole', r['Substances actives'], re.I)])
    record('Which ADAMA cereal products in France depend on prothioconazole?',
           f'{len(hits)}: ' + ' · '.join(names),
           'data/raw/FR-T4-001/produits_utf8.csv (versão 2026-08-25)',
           'FR-T4-001 — ANSES E-Phy, Licence Ouverte',
           'os três produtos constam como AUTORISE com prothioconazole na composição; '
           f'{total} produtos autorizados na França contêm a molécula',
           'a classificação "de cereal" vem do sinal público de lançamento, não do campo '
           'de cultura do registro — o E-Phy não classifica produto por cultura, só uso',
           'volume vendido, importância comercial relativa e plano interno da ADAMA',
           'HIGH para os fatos')


def q2():
    """Where has olive leaf spot (repilo) been observed recently in Spain?"""
    p = os.path.join(S, 'ES-T3-001-raif-olivar-repilo-2026.json')
    d = json.load(open(p, encoding='utf-8'))
    pv = d['provinces']
    top = sorted(pv.items(), key=lambda x: -x[1]['mean_pct_leaves_visible'])
    txt = ' · '.join(f"{k} {v['mean_pct_leaves_visible']}% (n={v['readings_visible']}, "
                     f"até {v['last_date']})" for k, v in top[:4])
    inc = [k for k, v in pv.items() if v['mean_pct_incubated']
           and v['mean_pct_incubated'] > v['mean_pct_leaves_visible']]
    record('Where has olive leaf spot (repilo) been observed recently in Spain?',
           f'Nas 7 províncias andaluzas monitoradas. Maiores médias: {txt}',
           'data/samples/ES-T3-001-raif-olivar-repilo-2026.json',
           'ES-T3-001 — RAIF Andalucía, CC BY 4.0',
           'percentual de folhas com sintoma visível medido em campo, por província, '
           f'safra 2026, última leitura em {max(v["last_date"] for v in pv.values())}',
           'a média por província é agregação nossa das leituras de parcela; '
           f'a marcação de infecção latente acima da visível ({", ".join(inc)}) também é derivada',
           'a Espanha fora da Andaluzia — nenhuma outra comunidade autônoma foi coletada; '
           'e as parcelas do RAIF não são amostra aleatória da província',
           'HIGH para a Andaluzia · NÃO SEI para o resto da Espanha')


def q3():
    """Which researchers repeatedly publish about septoria in cereals?"""
    d = json.load(open(os.path.join(S, 'EU-T5-001-openalex-people.json'), encoding='utf-8'))
    dr = d['spain_query_drift']
    record('Which researchers repeatedly publish about septoria in cereals?',
           'Espanha, consulta estrita "Zymoseptoria tritici" (2018–2026): '
           + ' · '.join(dr['strict_top_authors']),
           'data/samples/EU-T5-001-openalex-people.json',
           'EU-T5-001 — OpenAlex',
           f'{dr["strict_works"]} trabalhos com autor de afiliação espanhola; a contagem '
           'de trabalhos por autor é campo da fonte',
           'a leitura de "repetidamente" é nossa: contagem de trabalhos na janela',
           'se essas pessoas são as autoridades do tema — recorrência não é autoridade. '
           f'E a consulta larga devolveria {dr["loose_works"]} trabalhos e uma lista '
           f'diferente ({dr["ratio"]}× maior): a consulta é o experimento',
           'MEDIUM — depende de vocabulário controlado')


def q4():
    """Which competitor has registered products against the same issue?"""
    uses = [r for r in fr_uses() if (r.get('etat usage') or '').startswith('Autoris')]
    def firm(s):
        s = (s or '').upper()
        for k in ['ADAMA', 'BAYER', 'BASF', 'SYNGENTA', 'CORTEVA', 'DOW', 'FMC', 'UPL',
                  'NUFARM', 'GOWAN', 'SIPCAM', 'ASCENZA', 'CERTIS', 'DE SANGOSSE']:
            if k in s:
                return 'CORTEVA/DOW' if k in ('CORTEVA', 'DOW') else k
        return None
    sel = [r for r in uses
           if [x.strip() for x in (r['identifiant usage'] or '').split('*')][:1] == ['Blé']
           and 'Septorio' in (r['identifiant usage'] or '')]
    c = Counter(f for r in sel if (f := firm(r['titulaire'])))
    record('Which competitor has registered products against the same issue '
           '(wheat × septoria, France)?',
           f'{len(sel)} usos autorizados. Por empresa nomeada: '
           + ' · '.join(f'{k} {v}' for k, v in c.most_common()),
           'data/raw/FR-T4-001/usages_des_produits_autorises_utf8.csv (2026-08-25)',
           'FR-T4-001 — ANSES E-Phy',
           'cada uso autorizado é um ato administrativo com nº AMM, cultura, alvo e titular',
           'o agrupamento de razões sociais em grupo empresarial é nosso e **ainda não foi '
           'medido** — ver DECK-015; e a contagem é de usos, não de produtos',
           'participação de mercado, vendas, eficácia e preço. Contagem de registro '
           'não é posição de mercado',
           'HIGH para a contagem · LOW para qualquer leitura de mercado')


def q5():
    """Pergunta que a base NÃO consegue responder — o teste do 'we don't know yet'."""
    record('Is competitor communication about wheat septoria increasing in France?',
           '**NÃO SEI.**',
           'nenhuma — não existe coleta de comunicação de concorrente',
           'tentativas registradas: syngenta.fr 403 · agriculture.basf.fr 502 · corteva.it 404',
           'nenhum fato disponível',
           'nenhuma derivação possível',
           'tudo: o item de comunicação, a data, a linha de base histórica e a regra de '
           'medição. Sem linha de base não se pode dizer "increasing" — ver DECK-011 e G1',
           'NÃO SEI')


if __name__ == '__main__':
    print('ASK SINTONIA — consulta sobre a camada de evidência preservada\n' + '=' * 70)
    for fn in (q1, q2, q3, q4, q5):
        try:
            fn()
        except Exception as e:
            print(f'\n■ {fn.__doc__}\n  FALHOU: {type(e).__name__}: {e}')
    out = os.path.join(S, 'ASK-SINTONIA-teste.json')
    json.dump({'source': 'teste da camada de evidência — consulta determinística sobre '
                         'os dados já preservados no repositório',
               'sources': ['FR-T4-001', 'ES-T3-001', 'EU-T5-001'],
               'captured_at': '2026-08-28', 'SOURCE_LOCATION': 'FRANCE / SPAIN',
               'FACT_LOCATION': 'FRANCE / SPAIN', 'ORIGINAL_LANGUAGE': 'FR/ES',
               'answered': sum(1 for a in ANSWERS if a['ANSWER'] != '**NÃO SEI.**'),
               'unanswerable_by_design': sum(1 for a in ANSWERS if a['ANSWER'] == '**NÃO SEI.**'),
               'questions': ANSWERS}, open(out, 'w'), ensure_ascii=False, indent=2)
    print(f'\n\ngravado: {out}')
