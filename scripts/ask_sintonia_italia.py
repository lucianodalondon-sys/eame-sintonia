#!/usr/bin/env python3
"""
ASK SINTONIA ITALIA — a camada italiana é consultável, e recusa quando deve.

Não é chatbot e não é interface. É consulta determinística sobre a evidência preservada,
e cada resposta separa `FACT` · `DERIVED` · `UNKNOWN`.

O ativo mais forte do produto, segundo a rodada espanhola, é **recusar sinal falso com
evidência**. Por isso metade do valor deste arquivo está nas perguntas cuja resposta
correta é `REFUSE` — e nas REGRESSÕES, que reprovam a confiança falsa antes que ela chegue
a uma tela.

As cinco regressões vigiam as cinco confusões que já custaram medição nesta branch:

    SYMPTOM WINDOW ≠ APPLICATION WINDOW
    READ FAILURE   ≠ NO LABEL
    AFFILIATION    ≠ STUDY GEOGRAPHY
    REGISTRATION   ≠ COMMERCIAL CATALOG
    GENERIC TARGET ≠ SPECIFIC TARGET

    python3 scripts/ask_sintonia_italia.py
    python3 scripts/ask_sintonia_italia.py --json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
S = os.path.join(ROOT, 'data', 'samples')

ANSWERABLE, PARTIAL, REFUSE = 'ANSWERABLE', 'PARTIAL', 'REFUSE / NOT_KNOWN'
RESPOSTAS = []


def _ler(rel):
    p = os.path.join(S, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


def r(q, estado, resposta, fonte, fato, derivado, desconhecido):
    RESPOSTAS.append({'QUESTION': q, 'STATE': estado, 'ANSWER': resposta, 'SOURCE': fonte,
                      'WHAT_IS_FACT': fato, 'WHAT_IS_DERIVED': derivado,
                      'WHAT_IS_UNKNOWN': desconhecido})


def perguntas():
    casos = _ler('IT-CASOS/ITALY-HERO-CASES-V1.json') or {}
    venc = _ler('IT-T4-001/IT-T4-001-vencimentos-caso.json') or {}
    lotta = _ler('IT-T3-LOTTA/IT-lotta-obbligatoria-flavescenza-2026.json') or {}
    istat = _ler('IT-T1/IT-T1-001-istat-area-regional.json') or {}
    ciencia = _ler('IT-T5-001/IT-T5-001-ciencia-milho.json') or {}
    port = _ler('IT-T4-001/IT-T4-001-portfolio-rotulo.json') or {}
    idx = {c['CASE_ID']: c for c in casos.get('CASES', [])}

    r('Existe algo que precisa ser monitorado agora na Itália?', ANSWERABLE,
      'Sim, três coisas, e nenhuma delas é uma aplicação de produto. '
      '(1) Videira: sintoma foliar de flavescência, janela ago–set. '
      '(2) Milho no FVG: pico de ovideposição de piralide de 3ª geração. '
      '(3) A próxima versão do open data do Ministero, que resolve 7 vencimentos de 31/08.',
      'IT-T3-002 (bollettino vite n.19, 13/08) · IT-T3-006 (ERSA n.15 MAIS, 12/08) · IT-T4-001',
      'as três fontes publicaram nas últimas três semanas',
      'a agregação das três como "o que monitorar" é nossa',
      'a pressão real em campo hoje; nenhuma das fontes mede a Itália inteira')

    r('Temos alguma janela de APLICAÇÃO aberta agora?', PARTIAL,
      'Uma, e é estreita: piralide em milho no FVG, mas SÓ em semeadura tardia (junho) e '
      'milho de segundo raccolto — o boletim diz que nas demais lavouras as espigas estão '
      'em maturação avançada e a praga não causa dano. Limiar publicado: >3 ovaturas por '
      '100 plantas ou larvas em 30–40% de 50–100 espigas. '
      'Na videira a janela de aplicação FECHOU em junho.',
      'IT-T3-006 (ERSA FVG n.15) · IT-T3-LOTTA-OBBLIGATORIA',
      'o boletim declara o limiar e a exceção',
      'chamar isso de "janela aberta" sem a exceção seria exagero — por isso PARTIAL',
      'quantos hectares do FVG são de semeadura tardia ou segundo raccolto')

    r('A janela aberta na videira serve para tratar?', REFUSE,
      'Não. A janela ago–set é de RECONHECIMENTO DE SINTOMA foliar, não de aplicação. '
      'Os tratamentos obrigatórios ao vetor ocorreram em junho e o boletim de 31/07 já os '
      'dá por feitos. O que a norma exige agora é capitozzatura ou estirpação das plantas '
      'sintomáticas — que não é ação de produto.',
      'IT-T3-LOTTA-OBBLIGATORIA · bollettino vite Veneto n.19',
      'as duas janelas estão medidas e são diferentes',
      'nada — a recusa é a resposta',
      'nada relevante para esta pergunta')

    lote = lotta.get('REGIONS', [])
    r('Quando devemos preparar o próximo ciclo da flavescência?', PARTIAL,
      'PREPARE_BY 2027-05-31. A obrigação recorre por norma europeia, mas as DATAS são '
      'fixadas a cada ano pelo monitoramento: em 2026 caíram na primeira metade de junho '
      'nas duas regiões, e os atos saíram em maio (Lombardia 28/05, Vêneto 14/05). '
      'NEXT_2027_WINDOW = TO_BE_CONFIRMED.',
      'IT-T3-LOTTA-OBBLIGATORIA (%d regiões medidas)' % len(lote),
      'as datas de 2026 e as datas de publicação dos atos',
      'o PREPARE_BY é derivado do mês de publicação, não previsão da janela',
      'as datas de 2027; o próprio ato lombardo avisa que 2026 antecipou o ciclo')

    c1 = idx.get('IT-HERO-001', {}).get('ADAMA_REGISTERED_RESPONSE', {})
    r('Quais produtos registrados da ADAMA respondem ao vetor da flavescência?', ANSWERABLE,
      '%d nomeiam Scaphoideus titanus no rótulo (tau-fluvalinate: %s), com dose declarada. '
      'Mais 4 de lambda-cialotrina trazem o genérico «cicaline». A Lombardia admite '
      'exclusivamente produtos com um desses dois alvos no rótulo — os seis atendem aos dois.'
      % (c1.get('PRODUCTS_NAMING_VECTOR', 0), ', '.join(c1.get('PRODUCT_NAMES', [])[:3]) + '…'),
      'IT-T4-001-ETICHETTA (163/163 rótulos) · IT-T3-LOTTA-OBBLIGATORIA',
      'o alvo e a dose estão escritos na etichetta oficial',
      'a elegibilidade é leitura do critério do decreto contra o texto do rótulo',
      'se estão à venda hoje; disponibilidade comercial não é dedutível do registro')

    w = venc.get('WINDOW_CONVENTION', {})
    r('Que autorizações da ADAMA vencem nos próximos 6 meses?', ANSWERABLE,
      '%s em 6 meses de calendário — ou %s se a convenção for 180 dias. A diferença são '
      '13 autorizações que vencem TODAS em 2027-02-28. Sete vencem em 31/08/2026. '
      'Culturas mais afetadas: maçã 36, beterraba 35, videira 34.'
      % (w.get('EXPIRING_CALENDAR_6M_TO_2027_02_28'), w.get('EXPIRING_180_DAYS')),
      'IT-T4-001 (PROD_FTS_6_20260824) + etichette',
      'as datas e as contagens vêm do registro',
      'a atribuição de cultura vem do rótulo, não do CSV',
      'se cada autorização foi renovada — RENEWAL_STATUS = NÃO SEI para tudo após 24/08')

    r('A ADAMA vai perder esses produtos?', REFUSE,
      'Não sei, e a pergunta não é respondível por fora. EXPIRY ≠ WITHDRAWAL: re-registro é '
      'rotina e a maioria já consta como "Ri-registrato". Além disso o campo de estado '
      'atrasa — 8 autorizações vencidas em 15/08 seguiam ativas num arquivo de 24/08. '
      'O que se entrega é "estas datas pedem revisão".',
      'IT-T4-001',
      'o atraso de estado está medido (mínimo 9 dias)',
      'nada',
      'o estado de renovação de cada registro')

    r('Milho é realmente o melhor caso da Itália?', PARTIAL,
      'Não é o melhor, e não é o pior. Por convergência de pernas, milho e videira empatam '
      'em 5/5, mas a videira tem uma obrigação LEGAL anual por trás e o milho não — a lotta '
      'obbligatoria contra Diabrotica foi revogada em 2014. Por outro lado, o milho é o '
      'único com janela de aplicação aberta hoje, ainda que estreita.',
      'ITALY-HERO-CASES-V1',
      'as pernas de cada caso estão medidas uma a uma',
      'a comparação entre casos é nossa',
      'a pressão de campo nas três maiores regiões de milho, que não têm boletim medido')

    vol = ciencia.get('VOLUME_BY_SCOPE', {})
    r('O que a ciência italiana está vendo no milho?', ANSWERABLE,
      'Micotoxina/Fusarium domina com %s trabalhos — 2,6× as daninhas (%s) e muito acima de '
      'broca (%s) e Diabrotica (%s). Isso mede ATENÇÃO CIENTÍFICA, não pressão de campo.'
      % (vol.get('MAIZE_MYCOTOXIN'), vol.get('MAIZE_WEED'), vol.get('MAIZE_BORER'),
         vol.get('MAIZE_DIABROTICA')),
      'IT-T5-001 (OpenAlex, instituições italianas, 2019+)',
      'as contagens no recorte declarado',
      'nada — os números são diretos',
      'se a atenção científica reflete pressão de campo; são coisas diferentes')

    r('A broca do milho abre uma oportunidade em micotoxina?', REFUSE,
      'Não sustentado. A ponte é agronomicamente plausível — dano de broca é porta de '
      'entrada de Fusarium — e foi testada: milho × Ostrinia × micotoxina devolve 5 '
      'trabalhos no corpus italiano. Cinco é pouco demais. '
      'THIN_EVIDENCE / NOT_ENOUGH_FOR_CASE_BRIDGE.',
      'IT-T5-001',
      'a contagem de 5 é medida',
      'nada — a recusa é a resposta',
      'se a ligação existe em campo; não foi provada aqui')

    r('Existe field signal atual para milho na Itália?', ANSWERABLE,
      'Sim, no Friuli-Venezia Giulia: a ERSA publica série própria de boletim do MILHO, com '
      '10 números em 2026, o último de 12/08. Mas o FVG é a 5ª região (6,7% da área) — as '
      'três primeiras, que somam 71,6%, NÃO têm boletim de milho medido.',
      'IT-T3-006 (ERSA FVG) · IT-T1-001',
      'a série existe e está datada; a área regional está medida',
      'a leitura de que a cobertura é desalinhada com a área é nossa',
      'se Veneto, Lombardia e Piemonte publicam algo equivalente em outra rota')

    vine = (istat.get('BY_CROP', {}).get('VINE') or {})
    r('Onde está a videira italiana, e o caso está na região certa?', ANSWERABLE,
      'Sicilia 120,2 · Veneto 101,0 (17,2%) · Puglia 79,1 · Toscana 54,6 · Piemonte 39,9 · '
      'Lombardia 18,2 (3,1%). O caso estava rotulado como "Lombardia" porque de lá veio o '
      'decreto mais claro; a área diz Vêneto, que tem 5,5× mais videira e a mesma obrigação. '
      'Caso corrigido para Vêneto principal.',
      'IT-T1-001 (ISTAT, %s)' % (vine.get('CROP') or 'uva DOP+IGP+mesa'),
      'as áreas regionais',
      'a escolha da região do caso é derivada da área',
      'a área ISTAT (588,8) não é a mesma definição do Eurostat W1000 (715,8)')

    r('A ADAMA tem resposta à mosca-da-azeitona?', REFUSE,
      'Não nos rótulos analisados. Nenhum dos 163 nomeia Bactrocera oleae nem "mosca '
      'dell\'olivo". Doze citam olivo: dez são herbicidas de solo e dois são óleo de '
      'parafina cujo alvo declarado EM OLIVO é "Cocciniglie e Tignole". '
      'NO_REGISTERED_RESPONSE — não é ambíguo, é decisivo.',
      'IT-T4-001-ETICHETTA (%s rótulos)' % (port.get('LABEL_COVERAGE', {}).get('OBTAINED')),
      'a ausência é sobre o conjunto completo de rótulos vigentes',
      'nada',
      'o portfólio mundial da ADAMA; isto é sobre o registro italiano')

    r('Quantos produtos a ADAMA tem no catálogo comercial italiano?', REFUSE,
      'Não sei. adama.com devolve 403 de WAF a este ambiente, inclusive /robots.txt. O '
      'enunciado da missão menciona ~52 produtos, e isso permanece UNVERIFIED_INPUT — não '
      'entra como fato. O que se sabe é o REGISTRO: 163 autorizações vigentes do grupo. '
      'REGISTRATION ≠ COMMERCIAL CATALOG.',
      'IT-T9-001 (bloqueada) · IT-T4-001',
      'as 163 autorizações vigentes',
      'nada',
      'o catálogo comercial; a fonte está bloqueada e não foi contornada')


    # ------------------------------------------------- rodada de 30/08: painel e camada
    painel = _ler('IT-FONTES/ITALY-PANEL-BIAS.json') or {}
    duro = _ler('IT-T3-LOTTA/IT-trigo-duro-sinal-x-portfolio.json') or {}
    op = _ler('IT-FONTES/ITALY-OP-FIELD-LAYER.json') or {}
    pb = painel.get('BY_CROP', {})

    r('Qual a cobertura de sinal de campo do trigo duro na Itália?', PARTIAL,
      'O número que eu publiquei — 0,0% — não mede o país. Das cinco regiões contadas '
      'como medidas, 76,8% da área é uma só, a Puglia, cujo serviço parou de redigir '
      'fitopatologia em 2018; e o FVG entrou no painel com 0,0 mil ha da cultura. '
      '57,9% do trigo duro italiano NUNCA foi perguntado — Sicília (23,6%), Basilicata '
      '(9,8%), Marche (6,2%). O veredito é UNMEASURED_NOT_ZERO. '
      'Perguntando a uma região nova, o sinal apareceu de primeira: o LaMMA publica '
      'boletim de frumento por província na Toscana, com grano duro separado do tenero, '
      'fase fenológica e janela.',
      'ITALY-PANEL-BIAS.json + IT-T3-LAMMA',
      'as áreas regionais do ISTAT e as rotas efetivamente tentadas',
      'a distinção entre não perguntado, perguntado sem resposta e inexistente',
      'quantas edições a Toscana publica por ano — a página é rolante, sem arquivo; '
      'e o que Puglia, Sicília e Basilicata publicam, que é 62,1% da cultura')

    r('A ADAMA tem resposta para a fusariose de espiga em trigo duro na Itália?', REFUSE,
      'NÃO SEI, e a pergunta que decide isso é jurídica, não de dados. Fato: dos 14 '
      'produtos cujo rótulo nomeia grano duro, 13 são herbicidas e 1 é tratamento de '
      'semente (SEEDRON, cuja fusariose é a transmitida pela semente, não a da espiga) — '
      'zero fungicidas foliares. Fato: cinco foliares atendem exatamente o conjunto de '
      'doenças do boletim de campo (MAXENTIS e KOJAMI, azoxystrobin+prothioconazole, '
      'FRAC 11+3) e nomeiam frumento/COMMON_WHEAT, não DURUM_WHEAT. '
      'Se "frumento" no rótulo italiano cobre juridicamente o grano duro, NÃO HÁ LACUNA '
      'NENHUMA e o desencontro é artefato de redação. Se não cobre, a lacuna é real e é '
      'sobre a maior cultura do país. Responder qualquer das duas seria inventar.',
      'IT-trigo-duro-sinal-x-portfolio.json',
      'a classe e os alvos declarados de cada um dos 163 rótulos',
      'o desencontro observado entre a camada de campo e a de portfólio',
      'se "frumento" cobre grano duro — exige leitura do decreto de autorização, '
      'não é extraível do texto do rótulo. CROP_TERM ≠ AUTHORIZED_CROP')

    r('Não há sinal de campo de olivo na Puglia?', ANSWERABLE,
      'Há — eu é que estava medindo a instituição errada. O serviço regional não '
      'publica fitopatologia desde 2018, e a ARIF, que assumiu a competência, hoje É a '
      'editora do notiziario e ainda assim não restaurou a seção: ausência '
      'estabilizada, não transição. Mas a APOL, organização de produtores de Lecce, '
      'mantém série semanal numerada de mosca-da-azeitona com edições de 2026. '
      'O conteúdo dela não foi lido (503 daqui), então isso NÃO vira cobertura. '
      'SOURCE_LAYER ≠ SIGNAL_ABSENCE.',
      'ITALY-OP-FIELD-LAYER.json',
      'o texto da ARIF e os números/datas das edições da APOL indexadas',
      'que o sinal migrou do serviço regional para a organização de produtores',
      'o conteúdo dos boletins da APOL, e portanto a qualidade do sinal na Puglia')


def regressoes():
    """Cada uma reprova uma confiança falsa que já apareceu nesta branch."""
    casos = _ler('IT-CASOS/ITALY-HERO-CASES-V1.json') or {}
    idx = {c['CASE_ID']: c for c in casos.get('CASES', [])}
    port = _ler('IT-T4-001/IT-T4-001-portfolio-rotulo.json') or {}
    ciencia = _ler('IT-T5-001/IT-T5-001-ciencia-milho.json') or {}
    out = []

    c1 = idx.get('IT-HERO-001', {})
    out.append(('SYMPTOM_WINDOW != APPLICATION_WINDOW',
                (c1.get('MONITORING_WINDOW', {}).get('STATE') == 'OPEN'
                 and c1.get('APPLICATION_WINDOW', {}).get('STATE') == 'CLOSED_FOR_2026'),
                'a janela de monitoramento aberta não pode arrastar a de aplicação junto'))

    cob = port.get('LABEL_COVERAGE', {})
    out.append(('READ_FAILURE != NO_LABEL',
                cob.get('OBTAINED') == 163 and cob.get('PCT') == 100.0,
                '14 "ausentes" viraram 0 só com espera: ausência era falha de leitura'))

    out.append(('AFFILIATION != STUDY_GEOGRAPHY',
                'NÃO SEI' in str(ciencia.get('FACT_LOCATION', '')),
                'a afiliação do autor não é a região do fenômeno'))

    out.append(('REGISTRATION != COMMERCIAL_CATALOG',
                'NOT_COLLECTED' in str(c1.get('ADAMA_PUBLIC_COMMERCIAL_RESPONSE', '')),
                '163 autorizações não são um catálogo comercial, e o catálogo não foi obtido'))

    painel = _ler('IT-FONTES/ITALY-PANEL-BIAS.json') or {}
    duro = _ler('IT-T3-LOTTA/IT-trigo-duro-sinal-x-portfolio.json') or {}
    op = _ler('IT-FONTES/ITALY-OP-FIELD-LAYER.json') or {}

    out.append(('PANEL_MEASURED != COUNTRY_MEASURED',
                painel.get('BY_CROP', {}).get('DURUM_WHEAT', {}).get('VERDICT')
                == 'UNMEASURED_NOT_ZERO',
                'cobertura apoiada numa regiao so e amostra de tamanho um, nao pais'))

    out.append(('NOT_ASKED != NOT_FOUND != DOES_NOT_EXIST',
                painel.get('BY_CROP', {}).get('DURUM_WHEAT', {})
                .get('PCT_NATIONAL_NEVER_ASKED', 0) > 50.0,
                'mais de metade do trigo duro nunca foi perguntado, e isso nao e zero'))

    out.append(('CROP_TERM != AUTHORIZED_CROP',
                duro.get('THE_OPEN_QUESTION', {}).get('STATE') == 'NÃO SEI',
                'nomear frumento nao decide se cobre grano duro; afirmar lacuna seria inventar'))

    out.append(('SOURCE_LAYER != SIGNAL_ABSENCE',
                'não foi lido' in str(op.get('CORRECTION_TO_MY_OWN_FINDING', {})
                                      .get('WHAT_THIS_STILL_DOES_NOT_LICENSE', '')),
                'a camada estatal calada nao prova ausencia de sinal na regiao'))

    demo = casos.get('CAPABILITY_DEMONSTRATION_NOT_A_CASE', {})
    out.append(('GENERIC_TARGET != SPECIFIC_TARGET',
                'Cocciniglie' in str(demo.get('WHY_NOT_A_HERO_CASE', '')),
                'inseticida em olivo com alvo "Cocciniglie e Tignole" não responde a Bactrocera'))
    return out


def main():
    perguntas()
    regs = regressoes()
    if '--json' in sys.argv:
        print(json.dumps({'QUESTIONS': RESPOSTAS,
                          'REGRESSIONS': [{'NAME': n, 'PASS': p, 'WHY': w} for n, p, w in regs]},
                         ensure_ascii=False, indent=2))
        return
    for a in RESPOSTAS:
        print('\n■ %s' % a['QUESTION'])
        print('  [%s] %s' % (a['STATE'], a['ANSWER']))
        print('  FONTE     %s' % a['SOURCE'])
        print('  FATO      %s' % a['WHAT_IS_FACT'])
        print('  DERIVADO  %s' % a['WHAT_IS_DERIVED'])
        print('  NÃO SEI   %s' % a['WHAT_IS_UNKNOWN'])
    est = {}
    for a in RESPOSTAS:
        est[a['STATE']] = est.get(a['STATE'], 0) + 1
    print('\n%s\nPERGUNTAS %d · %s' % ('-' * 68, len(RESPOSTAS),
                                       ' · '.join('%s %d' % (k, v) for k, v in sorted(est.items()))))
    print('REGRESSÕES')
    for n, p, w in regs:
        print('  [%s] %-38s %s' % ('OK' if p else 'FALHOU', n, w))


if __name__ == '__main__':
    main()
