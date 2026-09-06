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
      'NO_REGISTERED_RESPONSE — não é ambíguo, é decisivo. A ausência foi conferida no '
      'TEXTO INTEGRAL dos 163, não na leitura parcial do parser: três rótulos citam o '
      'GÊNERO Bactrocera, e os três são Bactrocera DORSALIS, mosca-da-fruta em pomar. '
      'GENUS_MATCH != SPECIES_MATCH.',
      'IT-T4-001-ETICHETTA (%s rótulos com texto integral extraído)'
      % (_estagio_cobertura(port, 'TEXT_EXTRACTION_COVERAGE') or {}).get('OBTAINED'),
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

    r('A ADAMA tem resposta para a fusariose de espiga em trigo duro na Itália?',
      ANSWERABLE,
      'Sim, e a convergência fecha nos três eixos. CULTURA: a coluna Coltura da tabela '
      'de usos autorizados do MAXENTIS e do KOJAMI diz "Frumento tenero e duro '
      '(invernale e primaverile)". PROBLEMA: a mesma linha lista Fusarium (Fusarium '
      'spp., Microdochium spp.), Septoria, Oidio e Ruggini — o conjunto do boletim de '
      'campo, item por item. MOMENTO: o rótulo declara "Intervenire tra gli stadi di '
      'primo nodo visibile (inizio levata) e FINE FIORITURA per il controllo delle '
      'fusariosi del frumento", e o boletim de Grosseto pede tratamento justamente '
      '"dove la fase fenologica sta entrando in fioritura". São 25 produtos que nomeiam '
      'grano duro: 19 herbicidas, 5 fungicidas foliares, 1 tratamento de semente.',
      'IT-trigo-duro-sinal-x-portfolio.json × IT-T3-LAMMA',
      'a coluna Coltura e a janela de aplicação, ambas no texto do rótulo oficial; '
      'e a janela do boletim regional',
      'que as duas janelas são a mesma — comparação entre dois textos primários',
      'nada sobre venda, disponibilidade em ponto de venda ou prioridade interna: '
      'REGISTRATION ≠ COMMERCIAL AVAILABILITY. E o sinal de campo continua raso — '
      'a Toscana é 3,7% da área e 57,9% da cultura nunca foi sondada')

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


    # ------------------------------------------- rodada de 30/08: o caso e o painel
    caso = _ler('IT-CASOS/IT-CASE-DURUM-FUSARIUM-001.json') or {}
    pnl = _ler('IT-T3-LOTTA/IT-durum-field-panel.json') or {}

    r('Existe uma convergência real entre sinal de campo e portfólio na Itália?',
      ANSWERABLE,
      'Sim, uma, e é REGIONAL: IT-CASE-DURUM-FUSARIUM-001, na Toscana, província de '
      'Grosseto. Grano duro × fusariosi × fioritura, com os três eixos lidos de fonte '
      'primária e a coincidência de janela sendo TEXTUAL — os dois documentos escrevem '
      '"fioritura". Veredito REAL_REGIONAL_CONVERGENCE_PROVED: as duas pernas estão '
      'preservadas com hash reconferível, e a auditoria temporal passa (o alerta fecha '
      'só com evidência de 23/04/2026 ou anterior). Isso prova que o Sintonia TERIA '
      'enxergado a convergência enquanto ela existia — NÃO que ainda exista oportunidade '
      'hoje: a janela agronômica de 2026 fechou, a comercial é NOT_KNOWN, e o caso é de '
      'uma província com 3,7% da cultura.',
      'IT-CASE-DURUM-FUSARIUM-001.json + manifesto IT-T3-LAMMA',
      'o boletim datado e preservado (sha256) e a tabela de usos autorizados do rótulo',
      'que as duas janelas coincidem — comparação literal entre dois textos',
      'se o tratamento foi feito, se houve venda, a janela comercial, e se a '
      'convergência se repete nas regiões que concentram a cultura')

    r('Isso é uma oportunidade para a ADAMA na Itália?', REFUSE,
      'Não posso dizer isso, e a pergunta embute dois saltos. PRIMEIRO salto: de '
      'Toscana para Itália — a região é 3,7% da cultura e 57,9% do trigo duro nacional '
      'nunca recebeu sonda de campo. SEGUNDO salto: de autorização para oportunidade — '
      'o rótulo prova que o produto PODE ser usado, não que foi vendido, que há estoque, '
      'que estava disponível no ponto de venda ou que alguém deveria comprá-lo. O rótulo '
      'máximo que a evidência sustenta é REGIONAL CONVERGENCE WORTH INVESTIGATING.',
      'IT-CASE-DURUM-FUSARIUM-001.json',
      'a área regional (ISTAT) e o que o rótulo autoriza',
      'nada — a recusa é o resultado',
      'a janela comercial, que é NOT_KNOWN e depende de input da ADAMA')

    r('Sondar Sicília e Basilicata aumentou a cobertura de campo do trigo duro?',
      ANSWERABLE,
      'Não. Sondei três regiões (Sicília 23,6%, Basilicata 9,8%, Campânia 4,5% — 37,9% '
      'da cultura) e a cobertura medida continua em 3,7%, só a Toscana. Abrir a rota não '
      'é ler o sinal: na Sicília não achei índice de boletim nas rotas medidas (e o SIAS '
      'deu 503 em duas tentativas); na Basilicata o serviço foi retomado em janeiro de '
      '2026 mas as edições estão atrás de cadastro gratuito, que eu não abri; na Campânia '
      'há série provincial de 26/08/2026 cuja lista de culturas não é legível daqui.',
      'IT-durum-field-panel.json',
      'o órgão, a rota tentada e o HTTP de cada região',
      'que nenhuma das três pode entrar como coberta',
      'se qualquer uma delas publica boletim de cereal — nenhuma foi negada, só não lida')


    voz = _ler('IT-CASOS/IT-HUMAN-SENSOR-PILOT.json') or {}
    r('Pessoas funcionaram como sensores antecipados no caso do trigo duro?', PARTIAL,
      'Na amostra medida, não. Nenhuma das quatro classes humanas — pesquisador, '
      'técnico, produtor, creator — produziu sinal datado ANTES de 23/04/2026 sobre '
      'fusariose em grano duro. O único item anterior é de uma EMPRESA (Corteva, '
      '29/03/2026, 25 dias antes) com observação de campo real, mas sobre SEPTORIA, sem '
      'região nomeada. A camada de pesquisa convoca depois: o Durum Days 2026 foi em '
      '19/05. A voz do produtor falou de PREÇO em 03/07. Creator: zero, pelo terceiro '
      'crop×issue seguido. MAS duas das três plataformas estavam fechadas por login, '
      'então o veredito é NOT_PROVED_IN_SAMPLE, não NOT_EXISTS.',
      'IT-HUMAN-SENSOR-PILOT.json',
      'as datas de publicação de cada conteúdo lido e o estado HTTP de cada plataforma',
      'a classificação por classe de voz e a posição de cada uma no tempo',
      'o que LinkedIn e Instagram teriam mostrado — ACCESS_FAILURE ≠ NO_SIGNAL')


    portas = _ler('IT-CASOS/IT-HUMAN-SENSOR-OPEN-DOORS.json') or {}
    r('Pesquisadores funcionam como sensores públicos na Itália?', ANSWERABLE,
      'Sim, e isto mudou de uma rodada para a outra. Sabrina Locatelli, ricercatrice do '
      'CREA de Bérgamo, tem sinal público DATADO de 13/02/2026 — 69 dias antes do caso —, '
      'com 190 amostras, 29 centros de estocagem e 5 macroáreas, e com interpretação '
      'estrutural ("le fumonisine sono ormai un rischio cronico e strutturale"). É '
      'exatamente o recorte geográfico que o boletim regional não dá. DUAS ressalvas que '
      'não podem cair: é MILHO, não grano duro, então não fecha o caso; e é '
      'RETROSPECTIVO (relata 2025), então é contexto estrutural, não aviso antecipado.',
      'IT-HUMAN-SENSOR-OPEN-DOORS.json',
      'a data da publicação, a do evento, e os números que ela apresentou',
      'que a classe pesquisador deixou de ser NOT_OBSERVED',
      'se ela ou outro pesquisador falou de grano duro × fusariose na janela')


def _estagio_cobertura(port, nome):
    """Lê um estágio de cobertura do gêmeo regulatório.

    `LABEL_COVERAGE` plano está DEPRECATED: media DOWNLOAD e era lido como LEITURA.
    Quem quiser um número aqui tem de dizer QUAL dos seis estágios quer.
    """
    return (port.get('COBERTURA_POR_ESTAGIO') or {}).get(nome)


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

    # A régua mudou de nome de propósito. `LABEL_COVERAGE` media DOWNLOAD e era lida como
    # LEITURA; ancorar aqui de novo faria a lição virar o erro. O que esta regressão prova é
    # o DOWNLOAD: 14 rótulos "ausentes" viraram 0 só por esperar. A leitura tem régua própria,
    # e ela NÃO é 100%.
    baixa = _estagio_cobertura(port, 'LABEL_DOWNLOAD_COVERAGE') or {}
    leitura = _estagio_cobertura(port, 'LABEL_READ_COVERAGE') or {}
    # A camada que RESPONDE tem de saber que existem 40 rotulos mudos, senao a
    # pergunta "a ADAMA tem produto para X?" pode ser respondida com ausencia sobre um
    # rotulo que este artefacto nao leu. `PARSER_SILENCE != NO_PRODUCT`.
    divida = port.get('READ_STRUCTURING_DEBT') or {}
    out.append(('PARSER_SILENCE != NO_PRODUCT',
                (divida.get('CLASSE') == 'READ/STRUCTURING_DEBT'
                 and divida.get('NAO_E') == 'REGULATORY_ABSENCE'
                 and len(divida.get('REGISTRATION_IDS') or []) > 0
                 and divida.get('CONFIRMED_PARSER_DEBT', {}).get('COUNT', 0) > 0),
                'os rotulos que este artefacto nao leu ficam nomeados; ausencia sobre eles '
                'seria silencio do parser publicado como ausencia de registo'))

    out.append(('READ_FAILURE != NO_LABEL',
                (baixa.get('OBTAINED') == 163 and baixa.get('PCT') == 100.0
                 and 'PCT' not in port.get('LABEL_COVERAGE', {})
                 and 0 < (leitura.get('OBTAINED') or 0) < 163),
                '14 "ausentes" viraram 0 só com espera: ausência era falha de leitura — e a '
                'régua plana de 100% morreu, porque media outra coisa'))

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

    # A LEI CONTINUA VERDADEIRA; a minha APLICACAO dela e que estava errada. Presenca de
    # termo em prosa solta segue nao sendo autorizacao — o contrato do portfolio diz isso.
    # O que mudou e que no MAXENTIS/KOJAMI o termo aparece DENTRO da coluna Coltura da
    # tabela de usos autorizados, que e classe de evidencia mais forte. Apagar a lei
    # porque um caso a superou seria a forma errada de fazer a suite passar.
    out.append(('CROP_TERM != AUTHORIZED_CROP',
                'NÃO É AUTHORIZED_ON_CROP' in str(port.get('CROP_TERM_CONTRACT', '')),
                'presenca de termo em prosa nao e autorizacao; a tabela de usos, sim'))

    out.append(('STRONG_PATTERN != PERMISSION_TO_CLOSE',
                'CONTRÁRIO' in str(duro.get('THE_QUESTION_THAT_WAS_OPEN', {})
                                   .get('WHAT_THIS_TEACHES', '')),
                'o padrao de manha dizia lacuna; o NAO SEI segurou e a resposta veio ao contrario'))

    out.append(('SOURCE_LAYER != SIGNAL_ABSENCE',
                'não foi lido' in str(op.get('CORRECTION_TO_MY_OWN_FINDING', {})
                                      .get('WHAT_THIS_STILL_DOES_NOT_LICENSE', '')),
                'a camada estatal calada nao prova ausencia de sinal na regiao'))

    caso = _ler('IT-CASOS/IT-CASE-DURUM-FUSARIUM-001.json') or {}
    pnl = _ler('IT-T3-LOTTA/IT-durum-field-panel.json') or {}

    out.append(('AUTHORIZATION != OPPORTUNITY',
                caso.get('CASE_LABEL') == 'REGIONAL CONVERGENCE WORTH INVESTIGATING',
                'o rotulo prova que o produto PODE ser usado, nao que ha venda ou demanda'))

    out.append(('ONE_REGION != COUNTRY',
                caso.get('REGION_PCT_OF_NATIONAL_CROP', 100) < 5.0
                and 'REGIONAL' in str(caso.get('VERDICT_DECOMPOSED', {}).get('SCOPE', '')),
                'a Toscana e 3,7% do trigo duro; elevar o caso a Italia seria inventar'))

    out.append(('ROUTE_OPENED != SIGNAL_READ',
                pnl.get('COVERAGE_MOVED') is False
                and pnl.get('PCT_NATIONAL_NOW_COVERED') == 3.7,
                'sondar 37,9% da cultura sem ler boletim nao move cobertura nenhuma'))

    portas = _ler('IT-CASOS/IT-HUMAN-SENSOR-OPEN-DOORS.json') or {}
    _nm = {c['ID']: c for c in portas.get('THE_FOUR_NEAR_MISSES', [])}

    out.append(('RIGHT_CLASS + WRONG_CROP != CASE_SIGNAL',
                _nm.get('LOCATELLI-2026-02-13', {}).get('CLOSES_THE_CASE') is False,
                'pesquisadora datada 69 dias antes do caso — e de milho, nao de trigo duro'))

    out.append(('MANUFACTURER_CONTENT != HUMAN_SENSOR',
                _nm.get('FEZAN400-2026-02-13', {}).get('CLOSES_THE_CASE') is False,
                'o Fezan 400 acerta cultura, issue e janela e continua sendo anuncio'))

    out.append(('RETROSPECTIVE_FINDING != EARLY_WARNING',
                'RETROSPECTIVE_FINDING' in str(_nm.get('LOCATELLI-2026-02-13', {}).get('ALSO', '')),
                'a relacao e sobre a safra 2025; diz o que houve, nao o que vem'))

    voz = _ler('IT-CASOS/IT-HUMAN-SENSOR-PILOT.json') or {}
    out.append(('ACCESS_FAILURE != NO_SIGNAL',
                'ACCESS_FAILURE' in str(voz.get('PLATFORM_STATE', {})
                                        .get('LINKEDIN', {}).get('STATE', '')),
                'LinkedIn e Instagram devolvem 200 com muro de login; 200 nao e fonte viva'))

    out.append(('APPROXIMATE_DATE != DATED_EVIDENCE',
                all(p.get('RELATIVE_TO_CASE') != 'BEFORE_CASE'
                    for p in voz.get('PROFILES', [])
                    if p.get('DATE_STATE') == 'NOT_DATED_PRECISELY'),
                '"6 mesi fa" nao coloca o webinar antes do caso'))

    ant = _ler('IT-CASOS/IT-CASE-DURUM-FUSARIUM-001-antecipacao.json') or {}
    out.append(('FUTURE_EVIDENCE_CANNOT_CLOSE_PAST_CASE',
                ant.get('AUDIT_PASSES') is True and ant.get('VIOLATIONS') == [],
                'o alerta de 23/04 fecha so com evidencia daquele dia ou anterior'))

    out.append(('OBSERVED_SYMPTOM != MODELLED_RISK',
                'SINTOMA OBSERVADO ≠ RISCO MODELADO' in json.dumps(
                    _ler('IT-CASOS/IT-CASE-DURUM-FUSARIUM-001.json') or {},
                    ensure_ascii=False),
                'o boletim declara os dois separados, e generalizar o risco foi erro meu'))

    out.append(('PAST_WINDOW != OPEN_WINDOW',
                caso.get('CLOCKS', {}).get('B_AGRONOMIC_CLOCK', {})
                .get('WINDOW_STATE_AT_AS_OF') == 'CLOSED_FOR_2026',
                'a floracao de 2026 passou; o caso e para o ciclo seguinte'))

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
