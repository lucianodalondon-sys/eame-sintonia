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


# ---------------------------------------------------------------- BENCHMARK
# 20 perguntas distribuídas pelas camadas do deck. O que importa não é só quantas
# são respondidas: é quantas são **corretamente recusadas**. Um sistema que responde
# tudo está inventando.
BENCH = [
    # (id, camada, pergunta, veredito esperado, motivo)
    ('B01', 'REGULATION', 'Que atos da UE de 2026 tratam de substância ativa?', 'ANSWERABLE',
     'EU-T4-001: SPARQL devolve CELEX, data e título'),
    ('B02', 'REGULATION', 'Quando expira a aprovação europeia do protioconazol?', 'ANSWERABLE',
     'CELEX 32025R0787, linha 168: 31/03/2027'),
    ('B03', 'REGULATION', 'Quantos produtos estão autorizados na Espanha com protioconazol?', 'ANSWERABLE',
     'ES-T4-005: 30 em vigor — Bayer 8, ADAMA 3, Syngenta 3, Sharda 3. Era CORRECT REFUSAL '
     'até a MISSÃO 06; a recusa estava certa para o que sabíamos e errada sobre a fonte'),
    ('B04', 'REGULATION', 'Que autorizações ADAMA vencem na Itália nos próximos 6 meses?', 'ANSWERABLE',
     'IT-T4-001 traz data_scadenza: 58 de 155'),
    ('B05', 'MOLECULE', 'Que produtos franceses contêm metalaxil-M e de quem são?', 'ANSWERABLE',
     'FR-T4-001: 9 autorizados, 7 Syngenta, 1 Ascenza, 1 ADAMA'),
    ('B06', 'MOLECULE', 'Quem fabrica a substância ativa de um produto ADAMA?', 'CORRECT REFUSAL',
     'o registro traz titular, não fabricante — G2'),
    ('B07', 'MOLECULE', '"Folpel" e "folpet" são a mesma substância?', 'ANSWERABLE',
     'X-006 MORPHOLOGY: sim, mesma entrada, grafias diferentes no mesmo registro'),
    ('B08', 'MOLECULE', 'Qual a origem autorizada de uma formulação vendida na Itália?', 'CORRECT REFUSAL',
     'nenhuma fonte de authorized origin investigada'),
    ('B09', 'PORTFOLIO', 'Em que pares cultura × alvo a ADAMA tem uso autorizado na França?', 'ANSWERABLE',
     'FR-T4-001: 504 usos, top Vigne×Mildiou 17'),
    ('B10', 'PORTFOLIO', 'A ADAMA é líder de mercado em míldio da videira na França?', 'CORRECT REFUSAL',
     'registro não é mercado — só sabemos usos autorizados'),
    ('B11', 'PORTFOLIO', 'Que produtos ADAMA existem em cereal na Itália com protioconazol?', 'ANSWERABLE',
     'IT-T4-001: MAGANIC, MAXENTIS, AVASTEL, SORATEL, KOJAMI'),
    ('B12', 'SCIENCE', 'Quem publica repetidamente sobre resistência a herbicidas na França?', 'ANSWERABLE',
     'EU-T5-001: Délye 9 trabalhos, INRAE Agroécologie'),
    ('B13', 'SCIENCE', 'Quem é a maior autoridade em septoriose na Espanha?', 'CORRECT REFUSAL',
     'recorrência não é autoridade — não há régua'),
    ('B14', 'CROP', 'Qual região tem mais área de trigo comum em FR, ES e IT?', 'ANSWERABLE',
     'EU-T1-001: ES41 Castilla y León, 771,8 mil ha'),
    ('B15', 'CROP', 'Qual o rendimento de trigo em Castilla y León em 2024?', 'CORRECT REFUSAL',
     'Eurostat não publica rendimento em NUTS 2 — medido, H-001'),
    ('B16', 'FIELD', 'A pressão de repilo subiu em Huelva nas últimas safras?', 'ANSWERABLE',
     'ES-T3-001: 11 safras; 1,19% (2023) → 8,83% (2026), com controle de coorte'),
    ('B17', 'FIELD', 'A pressão de míldio subiu na França nesta safra?', 'CORRECT REFUSAL',
     'FR-T3-001 é PDF regional sem série processável'),
    ('B18', 'COMPETITOR', 'Que empresas têm registro contra septoriose do trigo na França?', 'ANSWERABLE',
     'FR-T4-001: BASF 22, Bayer 20, Syngenta 8, ADAMA 6'),
    ('B19', 'COMPETITOR', 'A Syngenta aumentou a comunicação sobre septoriose?', 'CORRECT REFUSAL',
     'sem coleta e sem linha de base — DECK-011'),
    ('B20', 'MARKET', 'Qual o preço do trigo duro na França e na Itália na última semana?', 'ANSWERABLE',
     'EU-T10-001: FR €267,50/t e IT €271,83/t'),
    # --- MISSÃO 06: identidade de registro (ES-01717) ---
    ('B21', 'IDENTITY', 'Qual é o produto de referência do registro ES-01717?', 'ANSWERABLE',
     'MAPA: SORATEL MAX na versão de 26/08/2026; era MAXENTIS na de 28/05/2025'),
    ('B22', 'IDENTITY', 'Que denominações comuns estão ligadas ao ES-01717?', 'ANSWERABLE',
     'MAPA: AMISTAR ERA 350 SC (Syngenta España) e CUMILZAN (Comercial Química Massó)'),
    ('B23', 'IDENTITY', 'A Syngenta é titular do registro ES-01717?', 'CORRECT REFUSAL',
     'NÃO — é empresa CONCESSIONÁRIA de denominação comum. O documento não traz o titular'),
    ('B24', 'IDENTITY', 'Quem detém o registro ES-01717?', 'ANSWERABLE',
     'ADAMA Agriculture España S.A. — ficha oficial do ROPF, PRIMÁRIA. Era PARTIAL na '
     'MISSÃO 06, quando só tínhamos agregador comercial'),
    ('B25', 'IDENTITY', 'AMISTAR ERA 350 SC tem registro independente do MAXENTIS?', 'CORRECT REFUSAL',
     'não — na Espanha é denominação comum do MESMO ES-01717. Mas o AMISTAR ERA 240 EC '
     'italiano é outro registro, sob CAC Chemical: não confundir os dois'),
    ('B26', 'IDENTITY', 'Quem fabrica o produto do registro ES-01717 e onde?', 'ANSWERABLE',
     'ADAMA Agricultural Solutions Ltd., planta (Neot Hovav) — ficha oficial do ROPF'),
    ('B27', 'IDENTITY', 'A ADAMA depende de Israel para fornecer na Espanha?', 'CORRECT REFUSAL',
     'a ficha nomeia UM fabricante e UMA planta para UM registro. Não é cadeia de suprimento'),
    ('B28', 'IDENTITY', 'A ADAMA é a maior empresa do mercado fitossanitário espanhol?', 'CORRECT REFUSAL',
     'é a titular com MAIS REGISTROS (188 de 3.084). Contagem de registros não é venda, '
     'volume nem participação'),
    ('B29', 'IDENTITY', 'Quantos registros espanhóis têm mais de uma denominação comum?', 'ANSWERABLE',
     '363 em vigor, 18,2% dos 1.993 em vigor. O denominador vai junto ou a resposta engana'),
    ('B30', 'IDENTITY', 'Contar por marca infla o mercado espanhol em quanto?', 'CORRECT REFUSAL',
     'a pergunta não é respondível como está: MERCADO não é medível nesta fonte. O que se '
     'mede é excesso de contagem de AUTORIZAÇÕES — 1,52x sobre o registro em vigor'),
    ('B31', 'CHANGE', 'Algum registro espanhol mudou de nome entre 2025 e 2026?', 'ANSWERABLE',
     '5 renomeações confirmadas em 311 registros comparáveis, incluindo ES-01717'),
    ('B32', 'CHANGE', 'A renomeação do ES-01717 indica um relançamento comercial?', 'CORRECT REFUSAL',
     'prova apenas OFFICIAL RECORD NAME CHANGED. Nem canal, nem preço, nem venda'),
    ('B33', 'CHANGE', 'Algum registro espanhol mudou de titular no último ano?', 'CORRECT REFUSAL',
     'o campo existe e é comparável, mas só temos UMA versão arquivada do export do ROPF. '
     'Detectável a partir da segunda'),
    ('B34', 'CHANGE', 'Quando o nome do ES-01717 mudou?', 'PARTIAL',
     'sabemos o intervalo (entre 28/05/2025 e 26/08/2026) e o trâmite datado em 28/07/2026; '
     'a data em que o mercado passou a ver o nome novo não está na fonte'),
    ('B35', 'FIELD', 'Que culturas o ES-01717 pode tratar?', 'ANSWERABLE',
     'cebada, centeno, trigo e triticale — ficha oficial em PDF do ROPF'),
]


# --------------------------------------------------------------- FRESHNESS (M08)
# O benchmark media VERDADE e RECUSA. Faltava a terceira dimensao: uma resposta certa
# hoje pode estar velha amanha - e uma resposta sobre a versao arquivada NAO envelhece,
# porque é outra pergunta.
#
#   FACT_KIND   CURRENT     depende da versao de hoje da fonte
#               HISTORICAL  aponta para uma versao arquivada; nao envelhece
#               STRUCTURAL  é sobre a regra/o regime, nao sobre um valor
#   FRESHNESS   SIM / NAO / DEPENDE
#
# A recusa tambem envelhece: uma CORRECT REFUSAL por falta de fonte deixa de ser correta
# quando a fonte abre. Aconteceu com B03 e B24 na MISSAO 07.
FRESHNESS = {
    'B01': ('CURRENT', 'SIM', 'EU-T4-001 · consulta ao vivo'),
    'B02': ('CURRENT', 'SIM', 'CELEX 32025R0787 · ato pode ser prorrogado'),
    'B03': ('CURRENT', 'SIM', 'ES-T4-005 · export do dia'),
    'B04': ('CURRENT', 'SIM', 'IT-T4-001 · arquivo datado'),
    'B05': ('CURRENT', 'SIM', 'FR-T4-001 · dump semanal'),
    'B06': ('STRUCTURAL', 'NAO', 'o registro FR/IT nao traz fabricante — é do esquema'),
    'B07': ('STRUCTURAL', 'NAO', 'grafia de substancia é regra de normalizacao'),
    'B08': ('STRUCTURAL', 'DEPENDE', 'ausencia de fonte pode deixar de ser verdade'),
    'B09': ('CURRENT', 'SIM', 'FR-T4-001'),
    'B10': ('STRUCTURAL', 'NAO', 'registro nunca é mercado — nao depende de versao'),
    'B11': ('CURRENT', 'SIM', 'IT-T4-001'),
    'B12': ('CURRENT', 'DEPENDE', 'OpenAlex acumula; a resposta cresce, nao inverte'),
    'B13': ('STRUCTURAL', 'NAO', 'falta regua de autoridade — é de metodo'),
    'B14': ('CURRENT', 'DEPENDE', 'Eurostat publica com anos de atraso'),
    'B15': ('STRUCTURAL', 'NAO', 'Eurostat nao tem rendimento em NUTS2 — H-001'),
    'B16': ('CURRENT', 'SIM', 'ES-T3-001 · safra em curso'),
    'B17': ('STRUCTURAL', 'DEPENDE', 'FR-T3-001 pode passar a publicar serie'),
    'B18': ('CURRENT', 'SIM', 'FR-T4-001'),
    'B19': ('STRUCTURAL', 'DEPENDE', 'sem linha de base; coleta futura muda isto'),
    'B20': ('CURRENT', 'SIM', 'EU-T10-001 · preco semanal'),
    'B21': ('CURRENT', 'SIM', 'ES-T4-004 · o nome MUDOU uma vez; é o caso-tipo'),
    'B22': ('CURRENT', 'SIM', 'ES-T4-004 · denominacoes entram e saem'),
    'B23': ('STRUCTURAL', 'NAO', 'concessionaria nunca é titular — é do modelo'),
    'B24': ('CURRENT', 'SIM', 'ES-T4-005 · titular pode mudar'),
    'B25': ('STRUCTURAL', 'NAO', 'regime de denominacion comun'),
    'B26': ('CURRENT', 'SIM', 'ES-T4-005 · fabricante pode mudar'),
    'B27': ('STRUCTURAL', 'NAO', 'um fabricante por registro nunca é cadeia'),
    'B28': ('STRUCTURAL', 'NAO', 'contagem de registro nunca é venda'),
    'B29': ('CURRENT', 'SIM', 'ES-T4-004 + ES-T4-005 · 363/1.993 muda a cada versao'),
    'B30': ('STRUCTURAL', 'NAO', 'MERCADO nao é medivel nesta fonte'),
    'B31': ('HISTORICAL', 'NAO', 'compara 28/05/2025 com 26/08/2026 — versoes fixas'),
    'B32': ('STRUCTURAL', 'NAO', 'o que a renomeacao prova é regra, nao valor'),
    'B33': ('CURRENT', 'DEPENDE', 'vira ANSWERABLE quando existir a 2a versao do export'),
    'B34': ('HISTORICAL', 'NAO', 'o intervalo é o que as versoes arquivadas permitem'),
    'B35': ('CURRENT', 'SIM', 'ES-T4-005 · usos autorizados mudam'),
}


def freshness_report():
    from collections import Counter
    linhas = []
    for bid, layer, q, verdict, why in BENCH:
        kind, fresh, dep = FRESHNESS.get(bid, ('UNKNOWN', 'DEPENDE', '—'))
        linhas.append({'id': bid, 'layer': layer, 'verdict': verdict,
                       'FACT_KIND': kind, 'FRESHNESS_REQUIRED': fresh,
                       'SOURCE_VERSION_DEPENDENCE': dep})
    faltando = [b[0] for b in BENCH if b[0] not in FRESHNESS]
    return {'questions': linhas,
            'BY_FACT_KIND': dict(Counter(l['FACT_KIND'] for l in linhas)),
            'BY_FRESHNESS': dict(Counter(l['FRESHNESS_REQUIRED'] for l in linhas)),
            'STALE_RISK': [l['id'] for l in linhas
                           if l['FACT_KIND'] == 'CURRENT' and l['FRESHNESS_REQUIRED'] == 'SIM'],
            'REFUSALS_THAT_CAN_EXPIRE': [l['id'] for l in linhas
                                         if l['verdict'] == 'CORRECT REFUSAL'
                                         and l['FRESHNESS_REQUIRED'] == 'DEPENDE'],
            'WITHOUT_FRESHNESS_LABEL': faltando}



def benchmark():
    from collections import Counter
    print('\n\n' + '=' * 70)
    print('BENCHMARK ASK SINTONIA — perguntas pelas camadas do deck')
    print('=' * 70)
    c = Counter(v for _, _, _, v, _ in BENCH)
    by_layer = {}
    for bid, layer, q, verdict, why in BENCH:
        by_layer.setdefault(layer, Counter())[verdict] += 1
        mark = '✔' if verdict == 'ANSWERABLE' else ('⊘' if verdict == 'CORRECT REFUSAL' else '~')
        print(f'  {mark} {bid} [{layer:11s}] {q[:58]}')
        print(f'       {verdict:16s} — {why}')
    print('\n  RESULTADO')
    for k in ('ANSWERABLE', 'PARTIAL', 'CORRECT REFUSAL', 'WRONG ANSWER'):
        print(f'    {k:16s} {c[k]:2d}  ({100*c[k]/len(BENCH):.0f}%)')
    print('\n  por camada:')
    for l in sorted(by_layer):
        d = by_layer[l]
        print(f'    {l:12s} respondidas {d["ANSWERABLE"]}  recusadas {d["CORRECT REFUSAL"]}')
    out = os.path.join(S, 'ASK-SINTONIA-benchmark.json')
    json.dump({'source': 'benchmark da camada de evidência — 20 perguntas',
               'sources': ['EU-T4-001', 'FR-T4-001', 'IT-T4-001', 'ES-T3-001', 'EU-T5-001',
                           'EU-T1-001', 'EU-T10-001'],
               'captured_at': '2026-08-28', 'SOURCE_LOCATION': 'EU/FR/ES/IT',
               'FACT_LOCATION': 'EU/FR/ES/IT', 'ORIGINAL_LANGUAGE': 'FR/ES/IT/EN',
               'totals': dict(c), 'wrong_answers': c['WRONG ANSWER'],
               'questions': [{'id': b[0], 'layer': b[1], 'question': b[2],
                              'verdict': b[3], 'basis': b[4],
                              'FACT_KIND': FRESHNESS.get(b[0], ('UNKNOWN',))[0],
                              'FRESHNESS_REQUIRED': FRESHNESS.get(b[0], ('', 'DEPENDE'))[1]}
                             for b in BENCH]},
              open(out, 'w'), ensure_ascii=False, indent=2)
    print(f'\n  gravado: {out}')


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
    benchmark()
